"""rules.path_trace: every printed hand-calculation value of a game path, equal to the simulation (FLOW-01, F2).

The trace is read-only. It is checked against `evaluate_path` (the single definition of legality, window costs and
ledger), against the independent worksheet replay per wave, and against the characterization records, which
stay untouched.
"""
import dataclasses
import json
from fractions import Fraction

import pytest

from planspiel import rules
from planspiel.printmodel import build_attack_sheets
from planspiel.rules import Path, PathError, Window
from planspiel.texts import load_texts
from tests.support import CONTENT_DIR, REPO_ROOT, harness
from tests.support.worksheet_replay import replay_wave

TIERS = ("low", "medium", "high")
REAL_IDS = tuple(f"M{number}" for number in range(1, 11))
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"


def _selection(level=0, **levels):
    return {measure_id: levels.get(measure_id, level) for measure_id in REAL_IDS}


def _swap_paths():
    start = _selection(M1=2, M2=1, M3=1, M4=1, M5=1)
    swapped = _selection(M1=2, M2=1, M3=1, M4=1, M8=3)
    downgraded = _selection(M1=1, M2=1, M3=1, M4=2, M8=3)
    swap = ("M5", "M8")
    return {
        "kurswechsel-swap": Path(start, (Window(swapped, swap),)),
        "swap-and-downgrade-in-window-2": Path(start, (Window(swapped, swap), Window(downgraded))),
    }


def _static_paths(tier):
    document = json.loads((GOLDEN_DIR / f"characterization_{tier}.json").read_text(encoding="utf-8"))
    valid = [case for case in document["cases"] if case["valid"]]
    return {f"static-{case['code']}": Path(case["expected"]["selection"]) for case in valid[::5]}


def _all_paths(tier):
    paths = dict(_static_paths(tier))
    paths.update(_swap_paths())
    return paths


def _cases():
    return [
        pytest.param(tier, name, id=f"{tier}-{name}")
        for tier in TIERS
        for name in _all_paths(tier)
    ]


@pytest.fixture(scope="module")
def real():
    return harness.load_config()


@pytest.fixture(scope="module")
def sheets(real):
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return {sheet.wave_id: sheet for sheet in build_attack_sheets(real, texts)}


def _evaluate(cfg, tier, path):
    return rules.evaluate_path(cfg, tier, path, enforce_kurswechsel=False)


def _trace(cfg, tier, path):
    return rules.path_trace(cfg, tier, path, enforce_kurswechsel=False)


def test_the_three_path_kinds_are_covered_for_every_tier():
    for tier in TIERS:
        names = set(_all_paths(tier))
        assert {"kurswechsel-swap", "swap-and-downgrade-in-window-2"} <= names
        assert sum(name.startswith("static-") for name in names) >= 5


@pytest.mark.parametrize(("tier", "name"), _cases())
def test_trace_equals_evaluate_path_per_wave(real, tier, name):
    path = _all_paths(tier)[name]
    record = _evaluate(real, tier, path)
    trace = _trace(real, tier, path)

    assert [wave.wave_id for wave in trace.waves] == [wave["wave_id"] for wave in record["waves"]]
    for wave_trace, wave in zip(trace.waves, record["waves"]):
        assert wave_trace.cia == wave["cia"]
        assert wave_trace.e_value == wave["e_value"]
        assert wave_trace.bonus_reduction == wave["bonus_reduction"]
        assert wave_trace.gesamtreduktion == wave["gesamtreduktion"]
        assert Fraction(wave_trace.damage_eur, 1000) == wave["damage"]
        assert wave_trace.kz_attack == wave["kz_delta_attack"]
        assert wave_trace.kz_event == sum(event["kz_delta"] for event in wave["events"])
        assert wave_trace.kz_after == wave["kz_after"]
        assert wave_trace.events == tuple(wave["events"])


@pytest.mark.parametrize(("tier", "name"), _cases())
def test_review_values_equal_evaluate_path(real, tier, name):
    path = _all_paths(tier)[name]
    record = _evaluate(real, tier, path)
    review = _trace(real, tier, path).review

    assert review.kz_pre_review == record["kz_pre_review"]
    assert review.kz_final == record["kz_final"]
    assert review.own_spend_k == record["costs"]["security_spend"]
    assert review.remaining_k == record["costs"]["remaining"]
    assert review.ros == record["ros"]
    assert review.kz_review_change == sum(event["kz_delta"] for event in record["final_events"])
    assert Fraction(review.total_damage_eur, 1000) == record["total_damage"]
    assert review.over_budget == record["over_budget"]


@pytest.mark.parametrize(("tier", "name"), _cases())
def test_window_costs_equal_evaluate_path(real, tier, name):
    path = _all_paths(tier)[name]
    record = _evaluate(real, tier, path)
    trace = _trace(real, tier, path)

    assert [window.cost_k for window in trace.windows] == [window["cost"] for window in record["windows"]]
    assert [window.swap for window in trace.windows] == [window["swap"] for window in record["windows"]]
    assert [window.after_wave for window in trace.windows] == [
        wave["wave_id"] for wave in record["waves"][: len(trace.windows)]
    ]
    for window in trace.windows:
        assert window.increase_k - window.credit_k == window.cost_k
        assert (window.credit_k > 0) == (window.swap is not None)
    assert trace.init_k == record["costs"]["init"]


@pytest.mark.parametrize(("tier", "name"), _cases())
def test_every_wave_equals_the_independent_worksheet_replay(real, sheets, tier, name):
    trace = _trace(real, tier, _all_paths(tier)[name])
    for wave in trace.waves:
        cia = (wave.cia["c"], wave.cia["i"], wave.cia["a"])
        replayed = replay_wave(sheets[wave.wave_id], cia, wave.selection, wave.kz_event)
        assert wave.case == replayed.case
        assert wave.damage_before_eur == replayed.damage_before_eur
        assert wave.damage_eur == replayed.damage_eur
        assert wave.kz_attack == replayed.kz_attack
        assert wave.kz_change == replayed.change


@pytest.mark.parametrize(("tier", "name"), _cases())
def test_case_and_damage_follow_the_printed_bounds(real, tier, name):
    trace = _trace(real, tier, _all_paths(tier)[name])
    for wave in trace.waves:
        constants = rules.worksheet_constants(real, next(w for w in real.waves if w.wave_id == wave.wave_id))
        if wave.gesamtreduktion <= constants.lower:
            assert wave.case == 1
        elif wave.gesamtreduktion >= constants.upper:
            assert wave.case == 2
        else:
            assert wave.case == 3
        assert wave.damage_eur == wave.damage_before_eur * (1 - wave.recovery_factor)
        assert wave.kz_change == rules.wave_kz_change(wave.kz_attack, wave.kz_event)
        assert wave.kz_change_exact == wave.kz_attack + wave.kz_event
        assert wave.kz_unclamped == wave.kz_before + wave.kz_change
        assert wave.kz_after == rules.clamp_kz(wave.kz_unclamped)


@pytest.mark.parametrize(("tier", "name"), _cases())
def test_kz_chain_runs_from_the_tier_start(real, tier, name):
    trace = _trace(real, tier, _all_paths(tier)[name])
    assert trace.waves[0].kz_before == real.budget_tiers[tier].kz_start
    for earlier, later in zip(trace.waves, trace.waves[1:]):
        assert later.kz_before == earlier.kz_after
    assert trace.review.kz_pre_review == trace.waves[-1].kz_after


@pytest.mark.parametrize(("tier", "name"), _cases())
def test_running_budget_ends_at_the_ledger_remaining(real, tier, name):
    path = _all_paths(tier)[name]
    record = _evaluate(real, tier, path)
    trace = _trace(real, tier, path)
    tier_budget = real.budget_tiers[tier].budget

    assert trace.start_remaining_k == tier_budget - record["costs"]["init"]
    remaining = trace.start_remaining_k
    for index, wave in enumerate(trace.waves):
        window_cost = record["costs"]["window_costs"][index] if index < len(record["costs"]["window_costs"]) else 0
        assert wave.window_cost_k == window_cost
        assert wave.own_opex_k == record["costs"]["opex_by_wave"][index]
        remaining = remaining - wave.own_opex_k + wave.event_budget_k - wave.event_opex_k - window_cost
        assert wave.remaining_k == remaining
    assert trace.waves[-1].remaining_k == record["costs"]["remaining"]
    assert trace.review.remaining_k == record["costs"]["remaining"]


@pytest.mark.parametrize(("tier", "name"), _cases())
def test_bonus_met_and_missed_partition_the_wave_rows(real, tier, name):
    trace = _trace(real, tier, _all_paths(tier)[name])
    for wave in trace.waves:
        rows = next(w for w in real.waves if w.wave_id == wave.wave_id).bonus_measures
        assert set(wave.bonus_met) | set(wave.bonus_missed) == {row.measure for row in rows}
        assert not set(wave.bonus_met) & set(wave.bonus_missed)
        for row in rows:
            reached = wave.selection[row.measure] >= row.min_level
            assert (row.measure in wave.bonus_met) == reached
        assert wave.bonus_reduction == sum(row.bonus for row in rows if row.measure in wave.bonus_met)


def test_a_low_kz_start_makes_the_clamp_act_and_the_trace_still_equals_the_simulation(real):
    tier = real.budget_tiers["medium"]
    boosted = dataclasses.replace(real, budget_tiers={"medium": dataclasses.replace(tier, kz_start=1)})
    path = _swap_paths()["kurswechsel-swap"]
    record = rules.evaluate_path(boosted, "medium", path)
    trace = rules.path_trace(boosted, "medium", path)

    assert any(wave.kz_unclamped < rules.KZ_MIN for wave in trace.waves), "the fixture must show the clamp"
    assert [wave.kz_after for wave in trace.waves] == [wave["kz_after"] for wave in record["waves"]]
    assert trace.review.kz_final == record["kz_final"]


def test_recovery_factor_is_zero_for_an_attack_without_recovery(real):
    trace = _trace(real, "medium", _swap_paths()["kurswechsel-swap"])
    exfil = next(wave for wave in trace.waves if wave.attack_id == "exfil")
    assert exfil.recovery_factor == 0
    assert exfil.damage_eur == exfil.damage_before_eur
    ransomware = next(wave for wave in trace.waves if wave.attack_id == "ransomware")
    assert ransomware.recovery_factor > 0


@pytest.mark.parametrize(
    ("path", "enforce"),
    [
        pytest.param(Path(_selection(M1=1), (Window(_selection(M1=1)),)), True, id="kurswechsel-missing"),
        pytest.param(Path(_selection(M1=3)), True, id="dependencies"),
        pytest.param(Path({"M1": 1}), False, id="unknown-measure"),
        pytest.param(Path(_selection(M1=1), (Window(_selection(M1=1)),) * 3), False, id="too-many-windows"),
        pytest.param(Path(_selection(M1=1), (Window(_selection(M1=1), ("M1", "M2")),)), False, id="swap-illegal"),
    ],
)
def test_path_trace_raises_where_evaluate_path_raises(real, path, enforce):
    with pytest.raises(PathError) as expected:
        rules.evaluate_path(real, "medium", path, enforce_kurswechsel=enforce)
    with pytest.raises(PathError) as raised:
        rules.path_trace(real, "medium", path, enforce_kurswechsel=enforce)
    assert raised.value.reason == expected.value.reason


def test_enforcement_default_matches_evaluate_path(real):
    path = Path(_selection(M1=1))
    with pytest.raises(PathError) as raised:
        rules.path_trace(real, "medium", path)
    assert raised.value.reason == "kurswechsel_missing"


def test_the_trace_of_a_path_without_windows_equals_evaluate_plan(real):
    selection = _selection(M1=2, M2=2, M4=1, M6=1)
    plan = rules.evaluate_plan(real, "medium", selection)
    trace = rules.path_trace(real, "medium", Path(selection), enforce_kurswechsel=False)
    assert trace.review.kz_final == plan["kz_final"]
    assert trace.review.ros == plan["ros"]
    assert [wave.kz_after for wave in trace.waves] == [wave["kz_after"] for wave in plan["waves"]]


def test_path_trace_leaves_the_simulation_records_alone(real):
    selection = _selection(M1=2, M2=2, M4=1, M6=1)
    keys = set(rules.evaluate_plan(real, "medium", selection)["waves"][0])
    rules.path_trace(real, "medium", Path(selection), enforce_kurswechsel=False)
    assert set(rules.evaluate_plan(real, "medium", selection)["waves"][0]) == keys
    assert keys == {
        "wave_id", "attack", "cia", "e_value", "bonus_reduction", "gesamtreduktion", "capped_reduction",
        "severity", "damage", "kz_delta_attack", "events", "kz_after",
    }


