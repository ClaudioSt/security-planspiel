"""Exact arithmetic with one rounding point per wave (FOUND-05; D-01, D-02, D-03, D-06, D-23)."""
import ast
import copy
import json
from fractions import Fraction

import pytest

from planspiel.config import load_config
from planspiel.rules import attack_kz_delta, clamp_kz, damage_euros, kz_slope, wave_kz_change
from tests.support import CONFIG_PATH, REPO_ROOT, harness

TIERS = ("low", "medium", "high")


def golden_cases(tier):
    path = REPO_ROOT / "tests" / "golden" / f"characterization_{tier}.json"
    return json.loads(path.read_text(encoding="utf-8"))["cases"]


def code_with_tag(tier, predicate):
    for case in golden_cases(tier):
        if any(predicate(tag) for tag in case["tags"]):
            return case["code"]
    raise AssertionError("no golden case with the requested tag")


def tie_code_with_zero_event():
    return code_with_tag("medium", lambda tag: tag.startswith("census:tie_w3:") and tag.endswith("/0"))


def evaluate(cfg, tier, code):
    return harness.evaluate(cfg, tier, harness.selection_of(cfg, code))


def wave_events_kz(wave):
    return sum(event["kz_delta"] for event in wave["events"])


def test_config_numbers_are_exact():
    cfg = load_config(CONFIG_PATH)
    weight = cfg.waves[0].weights["c"]
    assert isinstance(weight, Fraction)
    assert weight == Fraction(2, 5)
    assert cfg.ws == 10
    assert cfg.rs == 10
    assert cfg.measures["M4"].levels[1].recovery == Fraction(1, 10)


@pytest.mark.parametrize(
    ("e_target_delta", "attack_delta", "event_kz", "expected"),
    [
        (10, Fraction(3, 2), 0, 12),
        (-7, Fraction(3, 2), 0, -6),
        (-7, Fraction(-32, 7), 0, -12),
        (5, Fraction(-6), 1, 0),
    ],
)
def test_wave_kz_change_rounds_once_half_away(e_target_delta, attack_delta, event_kz, expected):
    assert wave_kz_change(e_target_delta, attack_delta, event_kz) == expected


def test_clamp_kz():
    assert clamp_kz(-3) == 0
    assert clamp_kz(42) == 42
    assert clamp_kz(140) == 100


def test_attack_kz_delta_exfil_slope():
    slope = kz_slope(-7, 10, 7)
    assert attack_kz_delta(-7, slope, 10, 10) == Fraction(-32, 7)


def test_damage_euros_whole_euros_with_recovery():
    assert damage_euros(75, 20, 3, 10, 10) == 105_000


def test_damage_euros_rejects_fractional_euros():
    with pytest.raises(ValueError):
        damage_euros(1, 1, 0, 3, 1)


def test_positive_tie_rounds_up():
    cfg = harness.load_config()
    record = evaluate(cfg, "medium", tie_code_with_zero_event())
    waves = record["waves"]
    wave3 = waves[2]
    assert wave3["capped_reduction"] == Fraction(7, 2)
    assert wave3["kz_delta_attack"] == Fraction(3, 2)
    assert wave3["e_reached"] is True
    assert wave3["kz_delta_e_target"] == 10
    expected = clamp_kz(waves[1]["kz_after"] + wave_kz_change(10, Fraction(3, 2), wave_events_kz(wave3)))
    assert wave3["kz_after"] == expected
    assert wave3["kz_after"] == clamp_kz(waves[1]["kz_after"] + 12 + wave_events_kz(wave3))


def test_negative_tie_rounds_down_with_raised_wave3_target(tmp_path):
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    override = copy.deepcopy(raw)
    for tier in override["budget_tiers"].values():
        tier["e_targets"]["3"] = 40
    path = tmp_path / "simulation_config.json"
    path.write_text(json.dumps(override, ensure_ascii=False), encoding="utf-8")

    cfg = harness.load_config(path)
    record = evaluate(cfg, "medium", tie_code_with_zero_event())
    waves = record["waves"]
    wave3 = waves[2]
    assert wave3["e_reached"] is False
    assert wave3["kz_delta_e_target"] == -7
    assert wave3["kz_delta_attack"] == Fraction(3, 2)
    assert wave3["kz_after"] == clamp_kz(waves[1]["kz_after"] - 6 + wave_events_kz(wave3))


def test_clamp_happens_after_rounding():
    cfg = harness.load_config()
    code = code_with_tag("medium", lambda tag: tag == "census:wave_clamp_high")
    record = evaluate(cfg, "medium", code)
    kz_previous = cfg.budget_tiers["medium"].kz_start
    found = False
    for wave in record["waves"]:
        change = wave_kz_change(wave["kz_delta_e_target"], wave["kz_delta_attack"], wave_events_kz(wave))
        if wave["kz_after"] == 100 and kz_previous + change > 100:
            found = True
        kz_previous = wave["kz_after"]
    assert found


@pytest.mark.parametrize("tier", TIERS)
def test_damage_is_whole_euros(tier):
    cfg = harness.load_config()
    checked = 0
    for case in golden_cases(tier):
        if not case["valid"]:
            continue
        record = evaluate(cfg, tier, case["code"])
        assert (record["total_damage"] * 1000).denominator == 1, case["code"]
        for wave in record["waves"]:
            assert (wave["damage"] * 1000).denominator == 1, case["code"]
        checked += 1
    assert checked > 0


def test_e_value_compared_exactly_with_target():
    cfg = harness.load_config()
    code = code_with_tag("medium", lambda tag: tag == "census:e_eq_target_w2")
    wave2 = evaluate(cfg, "medium", code)["waves"][1]
    assert wave2["e_value"] == wave2["e_target"]
    assert wave2["e_reached"] is True


def test_empty_selection_medium():
    cfg = harness.load_config()
    record = evaluate(cfg, "medium", "0" * len(cfg.measures))
    assert record["kz_final"] == 15
    assert record["total_damage"] == 620


@pytest.mark.parametrize("module", ["planspiel/rules.py", "planspiel/rounding.py"])
def test_builtin_round_is_never_called(module):
    tree = ast.parse((REPO_ROOT / module).read_text(encoding="utf-8"))
    calls = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "round"
    ]
    assert calls == []
