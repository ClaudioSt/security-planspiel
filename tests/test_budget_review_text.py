"""Budget Review boundaries: '>=' with round numbers, text generated from the tier list (RULE-07, D-16, CR-01, WR-07)."""
import json
import re
from fractions import Fraction

import pytest

from planspiel import rules
from planspiel.review_text import boundary_text
from planspiel.validate import validate
from tests.support import CONFIG_PATH, REPO_ROOT, harness

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
REAL_TIERS = [[0, 0], [25, 5], [50, 10], [75, 15]]
MUTATED_TIERS = [[0, 0], [30, 4], [60, 8]]
EURO_CASES = (0, 24_999, 25_000, 49_999, 50_000, 74_999, 75_000, 200_000)

FIRST_PART = re.compile(r"^0 – ([\d.]+) € → (±0|[+−]\d+)$")
LATER_PART = re.compile(r"^ab ([\d.]+) € → (±0|[+−]\d+)$")


def _raw(path=CONFIG_PATH):
    return json.loads(path.read_text(encoding="utf-8"))


def _errors(issues):
    return [issue for issue in issues if issue.level == "error"]


def _warnings(issues):
    return [issue for issue in issues if issue.level == "warning"]


def _value(text):
    if text == "±0":
        return 0
    sign = 1 if text[0] == "+" else -1
    return sign * int(text[1:])


def _euros(text):
    return int(text.replace(".", ""))


def parse_text(text):
    """Parse generated boundary text back into [(from_eur, value)] using only numbers found in the text."""
    parts = text.split(", ")
    rows = []
    first = FIRST_PART.match(parts[0])
    if first:
        rows.append((0, _value(first.group(2))))
        parts = parts[1:]
    for part in parts:
        match = LATER_PART.match(part)
        assert match, f"unparseable part: {part!r}"
        rows.append((_euros(match.group(1)), _value(match.group(2))))
    return rows


def parsed_value(rows, eur):
    result = None
    for minimum, value in rows:
        if eur >= minimum:
            result = value
    return result


@pytest.mark.parametrize(
    ("tiers", "expected"),
    [
        (REAL_TIERS, "0 – 24.999 € → ±0, ab 25.000 € → +5, ab 50.000 € → +10, ab 75.000 € → +15"),
        ([[0, 0], [30, 4], [60, 8]], "0 – 29.999 € → ±0, ab 30.000 € → +4, ab 60.000 € → +8"),
        ([[0, -3], [10, 0]], "0 – 9.999 € → −3, ab 10.000 € → ±0"),
        ([[0, 3]], "ab 0 € → +3"),
    ],
)
def test_boundary_text_is_generated_from_the_tier_list(tiers, expected):
    assert boundary_text(tiers) == expected


@pytest.mark.parametrize("tiers", [REAL_TIERS, MUTATED_TIERS], ids=["real", "mutated"])
def test_parsed_text_matches_simulation_at_euro_boundaries(tiers):
    rows = parse_text(boundary_text(tiers))
    for eur in EURO_CASES:
        assert parsed_value(rows, eur) == rules._tier_lookup(Fraction(eur, 1000), tiers), eur


@pytest.mark.parametrize("tiers", [REAL_TIERS, MUTATED_TIERS], ids=["real", "mutated"])
def test_parsed_text_matches_simulation_on_the_whole_keur_grid(tiers):
    rows = parse_text(boundary_text(tiers))
    for k in range(0, 201):
        assert parsed_value(rows, k * 1000) == rules.budget_review_delta(k, tiers, 9, 10), k


def test_tier_lookup_fails_below_its_domain():
    tiers = [[0, 0], [25, 5]]
    with pytest.raises(ValueError):
        rules._tier_lookup(-1, tiers)
    assert rules._tier_lookup(0, tiers) == 0
    assert rules._tier_lookup(25, tiers) == 5


def test_negative_remaining_takes_the_penalty_branch_first():
    assert rules.budget_review_delta(-1, [[0, 0], [25, 5]], 9, 10) == -9


@pytest.mark.parametrize(("remaining", "kz"), [(24, 50), (25, 55), (50, 60), (75, 65)])
def test_simulation_at_the_boundaries(remaining, kz):
    cfg = harness.load_config()
    assert rules.apply_final_events(cfg.final_events, {}, remaining, 50)[0] == kz


def test_real_and_mini_config_tiers_start_at_zero():
    for path in (CONFIG_PATH, MINI):
        event = _raw(path)["final_events"][0]
        assert event["tiers"] == REAL_TIERS


def test_real_config_text_is_the_printed_card_text():
    tiers = _raw()["final_events"][0]["tiers"]
    assert boundary_text(tiers) == "0 – 24.999 € → ±0, ab 25.000 € → +5, ab 50.000 € → +10, ab 75.000 € → +15"


@pytest.mark.parametrize("path", [CONFIG_PATH, MINI], ids=["real", "mini"])
def test_shipped_configs_validate_cleanly(path):
    issues = validate(_raw(path))
    assert _errors(issues) == []
    assert len(_warnings(issues)) == 1



def test_readme_states_inclusive_boundaries():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "einschließlich" in readme
    assert "boundary_text" in readme
