"""Change-window paths: exact per-wave evaluation, window pricing, Kurswechsel enforcement (RULE-02).

D-01..D-07, D-09, D-12, D-21, D-22, D-23, D-27, D-28. `evaluate_path` with no windows and the Kurswechsel
not enforced must equal the golden-protected `evaluate_plan`.
"""
import dataclasses
import json

import pytest

from planspiel import rules
from tests.support import REPO_ROOT, harness

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"

ALL_L1 = "1111111111"
KURS_START = "0000032323"


@pytest.fixture(scope="module")
def real():
    return harness.load_config()


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


def sel(cfg, code):
    return harness.selection_of(cfg, code)


def win(cfg, code, swap=None):
    return rules.Window(sel(cfg, code), swap)


def path(cfg, start, *windows):
    return rules.Path(sel(cfg, start), tuple(win(cfg, *w) if isinstance(w, tuple) else win(cfg, w) for w in windows))


def run(cfg, start, *windows, tier="medium", enforce=True):
    return rules.evaluate_path(cfg, tier, path(cfg, start, *windows), enforce_kurswechsel=enforce)


def reason_of(cfg, start, *windows, tier="medium", enforce=True):
    with pytest.raises(rules.PathError) as caught:
        run(cfg, start, *windows, tier=tier, enforce=enforce)
    return caught.value.reason


def _golden_cases(tier):
    file = REPO_ROOT / "tests" / "golden" / f"characterization_{tier}.json"
    return json.loads(file.read_text(encoding="utf-8"))["cases"]


def _assert_equals_reference(cfg, tier, code):
    selection = sel(cfg, code)
    reference = harness.evaluate(cfg, tier, selection)
    assert reference["valid"]
    got = rules.evaluate_path(cfg, tier, rules.Path(selection), enforce_kurswechsel=False)
    assert harness.compact_from_path(cfg, got) == harness.compact_from_plan(cfg, reference), code
    assert got["ros"] == reference["ros"], code
    assert got["final_events"] == reference["final_events"], code
    assert got["kz_final"] == reference["kz_final"], code


@pytest.mark.parametrize("tier", TIERS)
def test_no_window_path_equals_evaluate_plan_on_every_valid_mini_plan(mini, tier):
    checked = 0
    for code in harness.iter_codes(mini):
        if not rules.dependencies_satisfied(sel(mini, code), mini.measures):
            continue
        _assert_equals_reference(mini, tier, code)
        checked += 1
    assert checked > 0


@pytest.mark.parametrize("tier", TIERS)
def test_no_window_path_equals_evaluate_plan_on_golden_cases(real, tier):
    checked = 0
    for case in _golden_cases(tier):
        if not case["valid"]:
            continue
        _assert_equals_reference(real, tier, case["code"])
        checked += 1
    assert checked > 0


@pytest.mark.parametrize("tier", TIERS)
def test_unchanged_windows_equal_no_windows(real, tier):
    for code in (ALL_L1, "2310120201", "0000000000"):
        plain = rules.evaluate_path(real, tier, rules.Path(sel(real, code)), enforce_kurswechsel=False)
        held = run(real, code, code, code, tier=tier, enforce=False)
        assert harness.compact_from_path(real, held) == harness.compact_from_path(real, plain)


def test_simulate_selection_equals_simulate_waves_with_one_selection(real):
    selection = sel(real, "2310120201")
    tier = real.budget_tiers["medium"]
    args = (tier, real.waves, real.attacks, real.measures, real.events, real.base_cia, tier.kz_start, real.ws, real.rs)
    single = rules.simulate_selection(selection, *args)
    waves = rules.simulate_waves([selection] * len(real.waves), *args)
    assert single == {"selection": selection, **waves}
    assert list(single) == list(
        ["selection", "kz_final", "total_damage", "total_event_opex", "total_event_budget", "cia_mali", "waves"]
    )


def test_simulate_waves_rejects_a_wrong_selection_count(real):
    tier = real.budget_tiers["medium"]
    with pytest.raises(ValueError):
        rules.simulate_waves(
            [sel(real, ALL_L1)], tier, real.waves, real.attacks, real.measures, real.events,
            real.base_cia, tier.kz_start, real.ws, real.rs,
        )


def test_exempt_starts_need_no_swap(real):
    for code in (ALL_L1, "0000000000"):
        got = run(real, code, enforce=True)
        assert got["windows"] == []
        _assert_equals_reference(real, "medium", code)


def test_non_exempt_start_without_windows_misses_the_kurswechsel(real):
    assert reason_of(real, KURS_START) == "kurswechsel_missing"


def test_non_exempt_start_with_an_unchanged_window_misses_the_kurswechsel(real):
    assert reason_of(real, KURS_START, KURS_START) == "kurswechsel_missing"


def test_kurswechsel_may_be_switched_off_for_plain_evaluation(real):
    got = run(real, KURS_START, enforce=False)
    assert got["costs"]["window_costs"] == []


def test_downgrade_keeps_init_sunk_and_lowers_opex_from_the_next_wave(real):
    got = run(real, "1111311111", "1111111111")
    costs = got["costs"]
    assert costs["init"] == 276
    assert costs["window_costs"] == [0]
    assert costs["opex_by_wave"] == [43, 33, 33]
    assert costs["security_spend"] == 385
    static = rules.evaluate_plan(real, "medium", sel(real, "1111311111"))
    assert static["costs"]["security_spend"] == 405
    assert got["waves"][0]["cia"] == static["waves"][0]["cia"]
    assert got["waves"][1]["cia"] == rules.compute_cia(sel(real, "1111111111"), real.measures, real.base_cia)
    assert got["selections"][0] == sel(real, "1111311111")
    assert got["selections"][1] == got["selections"][2] == sel(real, "1111111111")


def test_add_costs_the_init_of_the_chosen_level(real):
    got = run(real, "0000000000", "0000020000")
    costs = got["costs"]
    assert costs["window_costs"] == [24]
    assert costs["opex_by_wave"] == [0, 6, 6]
    assert costs["security_spend"] == 36


def test_upgrade_costs_the_init_difference(real):
    got = run(real, ALL_L1, ALL_L1, "1311111111")
    costs = got["costs"]
    assert costs["window_costs"] == [0, 60]
    assert costs["opex_by_wave"] == [33, 33, 55]
    assert costs["security_spend"] == 387


def test_cancel_refunds_nothing_and_stops_opex(real):
    got = run(real, ALL_L1, ALL_L1, "1111111110")
    costs = got["costs"]
    assert costs["window_costs"] == [0, 0]
    assert costs["opex_by_wave"] == [33, 33, 31]
    assert costs["init"] == 206


def test_unlimited_moves_and_events_follow_the_selection_in_force(real):
    got = run(real, "0000000000", "1101101000")
    assert got["costs"]["window_costs"] == [126]
    oem = next(event for event in got["waves"][1]["events"] if event["id"] == "oem_audit")
    assert oem["kz_delta"] == 15
    assert got["waves"][0]["events"][1]["opex_delta"] == 0
    assert got["waves"][0]["events"][1]["id"] == "operative_unterstuetzung"


def test_bonus_and_level_effects_start_with_the_next_wave(real):
    got = run(real, ALL_L1, "1111211111")
    assert got["waves"][0]["bonus_reduction"] == 0
    assert got["waves"][1]["bonus_reduction"] == 9


def test_window_effects_hold_until_the_next_window(real):
    got = run(real, ALL_L1, "1111211111", "1111211111")
    assert [wave["bonus_reduction"] for wave in got["waves"]][:2] == [0, 9]
    assert got["selections"][2] == sel(real, "1111211111")


def test_dependency_broken_by_a_window_is_illegal(real):
    start = "3211111111"
    assert reason_of(real, start, start, "3111111111") == "dependencies"


def test_lowering_the_dependent_in_the_same_window_is_legal(real):
    start = "3211111111"
    got = run(real, start, start, "2111111111")
    assert got["selections"][2] == sel(real, "2111111111")


def test_broken_start_selection_is_illegal(real):
    assert reason_of(real, "3111111111") == "dependencies"


def test_window_cost_prices_only_the_net_change(real):
    empty = sel(real, "0000000000")
    before = dict(empty, M3=1, M5=3)
    after = dict(empty, M3=2, M5=1)
    assert rules.window_cost(real.measures, before, after) == 32


def test_window_cost_is_zero_for_equal_levels_and_never_negative(real):
    same = sel(real, "2211122332")
    assert rules.window_cost(real.measures, same, same) == 0
    assert rules.window_cost(real.measures, sel(real, "3333333333"), sel(real, "0000000000")) == 0
    assert rules.window_cost(real.measures, sel(real, "0000000000"), sel(real, "1100000000")) == 50


def test_swap_carries_the_credit_of_the_dropped_measure(real):
    got = run(real, KURS_START, ("1000032320", ("M10", "M1")))
    assert got["costs"]["window_costs"] == [0]
    assert got["costs"]["security_spend"] == 385
    assert got["windows"] == [{"swap": ("M10", "M1"), "cost": 0}]


def test_swap_pays_only_the_surplus_and_counts_as_own_spend(real):
    got = run(real, KURS_START, ("2000002323", ("M6", "M1")))
    assert got["costs"]["window_costs"] == [20]
    assert got["costs"]["security_spend"] == 417
    expected = rules.ros(rules.base_losses(real.waves, real.attacks), got["total_damage"], 417)
    assert got["ros"] == expected


def test_swap_with_an_extra_downgrade_is_legal(real):
    got = run(real, KURS_START, ("1000032220", ("M10", "M1")))
    assert got["costs"]["window_costs"] == [0]


def test_swap_with_an_extra_upgrade_pays_the_upgrade(real):
    got = run(real, KURS_START, ("1000032330", ("M10", "M1")))
    assert got["costs"]["window_costs"] == [30]


def test_swap_on_an_exempt_start_is_illegal(real):
    assert reason_of(real, ALL_L1, (ALL_L1, ("M1", "M2"))) == "kurswechsel_illegal"


def test_swap_in_window_two_is_not_the_kurswechsel_window(real):
    swapped = "1000032320"
    assert reason_of(real, KURS_START, (swapped, ("M10", "M1")), (swapped, ("M10", "M1"))) == "swap_without_kurswechsel"


def test_swap_without_any_kurswechsel_in_the_config_is_illegal(real):
    events = {wave_id: [e for e in wave_events if e.type != "kurswechsel"] for wave_id, wave_events in real.events.items()}
    cfg = dataclasses.replace(real, events=events)
    assert rules.kurswechsel_wave(cfg.events) is None
    assert reason_of(cfg, KURS_START, ("1000032320", ("M10", "M1")), enforce=False) == "swap_without_kurswechsel"
    assert run(cfg, KURS_START)["windows"] == []


def test_incoming_measure_active_in_wave_one_is_illegal(real):
    assert reason_of(real, KURS_START, ("0000032320", ("M10", "M7"))) == "kurswechsel_illegal"


def test_dropped_measure_must_end_at_zero(real):
    assert reason_of(real, KURS_START, ("1000032321", ("M10", "M1"))) == "kurswechsel_illegal"


def test_dropped_measure_must_have_been_active(real):
    assert reason_of(real, KURS_START, ("1000032323", ("M4", "M1"))) == "kurswechsel_illegal"


def test_dropping_a_measure_leaves_the_dependents_to_the_team(real):
    start = "3200000000"
    assert reason_of(real, start, ("3010000000", ("M2", "M3"))) == "dependencies"
    got = run(real, start, ("2010000000", ("M2", "M3")))
    assert got["costs"]["window_costs"] == [0]


def test_event_effects_stay_out_of_ros(real):
    got = run(real, "1111311111", "1111111111", tier="low")
    costs = got["costs"]
    assert costs["total"] == costs["security_spend"] + costs["event_opex"]
    assert costs["event_opex"] != 0
    base = rules.base_losses(real.waves, real.attacks)
    assert got["ros"] == rules.ros(base, got["total_damage"], costs["security_spend"])
    assert costs["remaining"] == costs["budget_available"] - costs["total"]
    assert got["over_budget"] == (costs["total"] > costs["budget_available"])


def test_result_keys(real):
    got = run(real, ALL_L1, ALL_L1)
    assert list(got) == [
        "selections", "windows", "kz_pre_review", "kz_final", "total_damage", "total_event_opex",
        "total_event_budget", "cia_mali", "waves", "final_events", "costs", "over_budget", "ros",
    ]
    assert list(got["costs"]) == [
        "init", "window_costs", "opex_by_wave", "security_spend", "event_opex", "event_budget", "total",
        "budget_available", "remaining",
    ]


def test_three_windows_for_three_waves_are_too_many(real):
    assert reason_of(real, ALL_L1, ALL_L1, ALL_L1, ALL_L1) == "too_many_windows"


def test_level_outside_the_range_is_rejected(real):
    selection = dict(sel(real, ALL_L1), M3=4)
    with pytest.raises(rules.PathError) as caught:
        rules.evaluate_path(real, "medium", rules.Path(selection))
    assert caught.value.reason == "level_range"
    assert str(caught.value)


@pytest.mark.parametrize("break_selection", ["unknown", "missing"])
def test_unknown_or_missing_measure_ids_are_rejected(real, break_selection):
    selection = dict(sel(real, ALL_L1))
    if break_selection == "unknown":
        selection["M11"] = 1
    else:
        del selection["M10"]
    with pytest.raises(rules.PathError) as caught:
        rules.evaluate_path(real, "medium", rules.Path(selection))
    assert caught.value.reason == "unknown_measure"


def test_window_selection_with_a_wrong_measure_set_is_rejected(real):
    broken = dict(sel(real, ALL_L1))
    del broken["M2"]
    with pytest.raises(rules.PathError) as caught:
        rules.evaluate_path(real, "medium", rules.Path(sel(real, ALL_L1), (rules.Window(broken),)))
    assert caught.value.reason == "unknown_measure"


def test_path_error_is_a_value_error(real):
    assert issubclass(rules.PathError, ValueError)
