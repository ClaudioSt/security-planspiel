"""Event-induced overruns (RULE-05, D-14): the budget is checked once, after the last wave.

A team pushed over budget by an event such as the Sparprogramm gets the following change window to come back
within budget and is penalised only if it is still over budget at the end. Trimming in the window saves only the
OPEX of later waves, Init is never refunded (D-03). The static reference `evaluate_plan` has no change window,
so it penalises every event-induced overrun and cannot decide RULE-05; the path evaluator decides it.
"""
import copy
import dataclasses
import itertools
import json

import pytest

from planspiel import rules
from planspiel.config import Event
from planspiel.validate import validate
from tests.support import CONFIG_PATH, REPO_ROOT, harness

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"

EXEMPT = "1111111123"
EXEMPT_TRIM_M10 = "1111111121"
EXEMPT_TRIM_M9 = "1111111113"
EXEMPT_LOW = "1111111113"
EXEMPT_LOW_TRIM_M10 = "1111111111"
KURS_START = "0000032323"
KURS_SWAPPED = "0002032320"
KURS_SWAPPED_TRIM_M8 = "0002032120"


@pytest.fixture(scope="module")
def real():
    return harness.load_config()


def sel(cfg, code):
    return harness.selection_of(cfg, code)


def run(cfg, tier, start, *windows):
    built = tuple(
        rules.Window(sel(cfg, w[0]), w[1]) if isinstance(w, tuple) else rules.Window(sel(cfg, w)) for w in windows
    )
    return rules.evaluate_path(cfg, tier, rules.Path(sel(cfg, start), built))


def review_delta(record):
    return [e for e in record["final_events"] if e["id"] == "budget_review"][0]["kz_delta"]


def test_exempt_plan_trimmed_in_window_two_returns_within_budget(real):
    got = run(real, "medium", EXEMPT, EXEMPT, EXEMPT_TRIM_M10)
    assert got["costs"]["remaining"] == 7
    assert got["over_budget"] is False
    assert review_delta(got) == 0
    assert got["costs"]["init"] == 266
    assert got["costs"]["window_costs"] == [0, 0]
    assert got["costs"]["opex_by_wave"] == [45, 45, 37]


def test_exempt_plan_alternative_trim_of_m9_is_enough(real):
    got = run(real, "medium", EXEMPT, EXEMPT, EXEMPT_TRIM_M9)
    assert got["costs"]["remaining"] == 3
    assert got["over_budget"] is False
    assert review_delta(got) == 0


def test_exempt_plan_untrimmed_is_over_budget_by_the_event(real):
    got = rules.evaluate_path(real, "medium", rules.Path(sel(real, EXEMPT)))
    assert got["costs"]["remaining"] == -1
    assert got["over_budget"] is True
    assert review_delta(got) == -9


def test_static_reference_penalises_the_overrun_and_cannot_decide_rule_05(real):
    reference = harness.evaluate(real, "medium", sel(real, EXEMPT))
    assert reference["final_events"][0]["id"] == "budget_review"
    assert reference["final_events"][0]["kz_delta"] == -9
    assert review_delta(run(real, "medium", EXEMPT, EXEMPT, EXEMPT_TRIM_M10)) == 0


def test_partial_trim_that_stays_over_budget_is_still_penalised(real):
    got = run(real, "low", EXEMPT_LOW, EXEMPT_LOW, EXEMPT_LOW_TRIM_M10)
    assert got["costs"]["remaining"] == -9
    assert got["over_budget"] is True
    assert review_delta(got) == -9


def test_forced_swap_alone_leaves_the_team_over_budget(real):
    got = run(real, "medium", KURS_START, (KURS_SWAPPED, ("M10", "M4")))
    assert got["costs"]["window_costs"] == [0]
    assert got["costs"]["remaining"] == -11
    assert review_delta(got) == -18


def test_forced_swap_plus_window_two_trim_returns_within_budget(real):
    got = run(real, "medium", KURS_START, (KURS_SWAPPED, ("M10", "M4")), KURS_SWAPPED_TRIM_M8)
    assert got["costs"]["remaining"] == 1
    assert got["over_budget"] is False
    assert review_delta(got) == 0


def _balance_after_wave_two(record, budget):
    waves = record["waves"][:2]
    event_budget = sum(e["budget_delta"] for wave in waves for e in wave["events"])
    event_opex = sum(e["opex_delta"] for wave in waves for e in wave["events"])
    costs = record["costs"]
    return budget + event_budget - costs["init"] - sum(costs["opex_by_wave"][:2]) - event_opex


def test_negative_balance_in_the_middle_of_the_game_is_not_penalised(real):
    extra = Event(
        id="test_nachtragsbudget",
        name="Nachtragsbudget",
        description="Test",
        type="flat_budget",
        params={"budget_delta": 60},
    )
    events = {wave_id: list(wave_events) for wave_id, wave_events in real.events.items()}
    events[3].append(extra)
    cfg = dataclasses.replace(real, events=events)
    budget = cfg.budget_tiers["medium"].budget
    found = None
    for levels in itertools.product(range(1, 4), repeat=len(cfg.measures)):
        selection = dict(zip(cfg.measures, levels))
        if not rules.dependencies_satisfied(selection, cfg.measures):
            continue
        record = rules.evaluate_path(cfg, "medium", rules.Path(selection))
        if _balance_after_wave_two(record, budget) < 0 and record["costs"]["remaining"] >= 0:
            found = record
            break
    assert found is not None
    assert found["over_budget"] is False
    assert review_delta(found) >= 0


def _raw(path=CONFIG_PATH):
    return json.loads(path.read_text(encoding="utf-8"))


def _warnings(issues):
    return [issue for issue in issues if issue.level == "warning"]


def _errors(issues):
    return [issue for issue in issues if issue.level == "error"]


def _move_sparprogramm_to_last_wave(raw):
    raw["events"]["wave_3"].append(raw["events"]["wave_2"].pop(0))


def test_budget_cut_in_the_last_wave_warns_without_error():
    raw = _raw()
    assert raw["events"]["wave_2"][0]["id"] == "sparprogramm"
    _move_sparprogramm_to_last_wave(raw)
    issues = validate(raw)
    assert _errors(issues) == []
    hits = [issue for issue in issues if issue.code == "rules.event_without_window"]
    assert len(hits) == 1
    assert hits[0].level == "warning"
    assert hits[0].path == f"events.wave_3[{len(raw['events']['wave_3']) - 1}]"


def test_positive_budget_event_in_the_last_wave_does_not_warn():
    raw = _raw()
    _move_sparprogramm_to_last_wave(raw)
    raw["events"]["wave_3"][-1]["budget_delta"] = 20
    assert "rules.event_without_window" not in {issue.code for issue in validate(raw)}


def test_budget_cut_before_the_last_wave_does_not_warn():
    assert "rules.event_without_window" not in {issue.code for issue in validate(_raw())}


@pytest.mark.parametrize("path", [CONFIG_PATH, MINI], ids=["real", "mini"])
def test_shipped_configs_have_exactly_the_known_slope_warning(path):
    issues = validate(_raw(path))
    assert _errors(issues) == []
    assert [issue.code for issue in _warnings(issues)] == ["hand_calc.kz_slope"]


def test_sparprogramm_description_states_the_end_check_and_the_window():
    for path in (CONFIG_PATH, MINI):
        events = _raw(path)["events"]["wave_2"]
        text = [e for e in events if e["id"] == "sparprogramm"][0]["description"]
        assert "Geprüft wird das Restbudget erst am Ende" in text
        assert "Change-Fenster" in text


def test_readme_states_event_overrun_rule():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Sparprogramm" in text
    assert "am Ende noch überzogen" in text
