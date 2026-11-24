"""The old -> new value changes of the "Was ist neu" sheet (FLOW-04, D-13 values part, D-14).

`value_changes(cfg, baseline)` lists exactly the rebalance-able parameters whose MHP value differs from today's config.
Formatting and prose belong to the sheet builder (plan 07-06); these tests pin the raw values.
"""
import copy
import dataclasses
import json
from fractions import Fraction

import pytest

from planspiel.config import load_config
from planspiel.printmodel import PrintModelError
from planspiel.was_neu import BASELINE_FILE, BASELINE_GROUPS, ValueChange, load_baseline, value_changes
from tests.support import CONFIG_PATH, CONTENT_DIR


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def baseline():
    return load_baseline(CONTENT_DIR / BASELINE_FILE)


@pytest.fixture(scope="module")
def changes(cfg, baseline):
    return value_changes(cfg, baseline)


def _find(changes, group, subject, field):
    found = [c for c in changes if (c.group, c.subject, c.field) == (group, subject, field)]
    assert len(found) <= 1, (group, subject, field)
    return found[0] if found else None


def _assert_change(changes, group, subject, field, old, new, meaning=False):
    change = _find(changes, group, subject, field)
    assert change is not None, f"missing change {group} {subject} {field}"
    assert (change.old, change.new, change.meaning_changed) == (old, new, meaning), change


def _assert_unchanged(changes, group, subject, field):
    assert _find(changes, group, subject, field) is None, f"unexpected change {group} {subject} {field}"


# --- the baseline of the current config (nothing changed) -------------------------------------------------------


def _baseline_of_current(raw, tmp_path):
    """A baseline file holding today's values, with today's Budget Review reading."""
    out = {
        "schema": 1,
        "source": {"config_commit": "x", "print_commit": "y", "printed_overrides": []},
        "base_cia": raw["base_cia"],
        "budget_tiers": {
            name: {key: tier[key] for key in ("budget", "kz_start", "severity_multiplier")}
            for name, tier in raw["budget_tiers"].items()
        },
        "waves": {
            str(wave["id"]): {
                "weights": wave["weights"],
                "e_threshold": wave["e_threshold"],
                "bonus_measures": wave["bonus_measures"],
            }
            for wave in raw["waves"]
        },
        "attacks": {
            attack_id: {key: value for key, value in attack.items()}
            for attack_id, attack in raw["attacks"].items()
        },
        "measures": {
            measure_id: {
                "levels": {
                    level: {
                        "cia": info["cia"], "init": info["init"], "opex": info["opex"],
                        "recovery": info.get("recovery", 0),
                    }
                    for level, info in measure["levels"].items()
                    if level != "0"
                }
            }
            for measure_id, measure in raw["measures"].items()
        },
        "events": {},
    }
    for events in raw["events"].values():
        for event in events:
            params = {k: v for k, v in event.items() if k not in ("id", "name", "type")}
            if params:
                out["events"][event["id"]] = params
    review = raw["final_events"][0]
    out["budget_review"] = {
        "boundary": "inclusive",
        "tiers": review["tiers"],
        "overspend": {key: review["overspend_penalty"][key] for key in ("kz_per_step", "step")},
    }
    return out


def _load_raw_baseline(raw, tmp_path):
    target = tmp_path / BASELINE_FILE
    target.write_text(json.dumps(raw, default=float), encoding="utf-8")
    return load_baseline(target)


def _current_raw():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"), parse_float=Fraction)


@pytest.fixture
def same(tmp_path):
    return _load_raw_baseline(_baseline_of_current(_current_raw(), tmp_path), tmp_path)


def test_a_baseline_equal_to_the_config_gives_nothing(cfg, same):
    assert value_changes(cfg, same) == ()


# --- the real result -----------------------------------------------------------------------------------------


def test_the_result_is_a_tuple_of_value_changes(changes):
    assert isinstance(changes, tuple) and changes
    assert all(isinstance(change, ValueChange) for change in changes)
    assert all(isinstance(change.subject, tuple) for change in changes)


def test_budget_and_kz_start(changes):
    for tier, old, new in (("low", 350, 370), ("medium", 400, 390), ("high", 450, 405)):
        _assert_change(changes, "budget_tiers", (tier,), "budget", old, new)
    for tier, old, new in (("low", 50, 39), ("medium", 42, 36), ("high", 34, 33)):
        _assert_change(changes, "budget_tiers", (tier,), "kz_start", old, new)


def test_wave_thresholds_and_bonuses(changes):
    _assert_change(changes, "waves", (1,), "e_threshold", 23, 22)
    _assert_change(changes, "waves", (3,), "e_threshold", 25, 24)
    _assert_change(changes, "waves", (1, "M4"), "bonus", 6, 5)
    _assert_change(changes, "waves", (1, "M6"), "bonus", 3, 4)
    _assert_change(changes, "waves", (2, "M7"), "bonus", 6, 3)
    _assert_change(changes, "waves", (3, "M1"), "bonus", 8, 4)
    _assert_change(changes, "waves", (3, "M8"), "bonus", 9, 3)


def test_attack_kz_endpoints(changes):
    for attack, damage_old, damage_new, mitigation_old, mitigation_new in (
        ("ransomware", -6, -8, 10, 8),
        ("ot", -5, -6, 7, 8),
        ("exfil", -7, -6, 10, 8),
    ):
        _assert_change(changes, "attacks", (attack,), "kz_at_full_damage", damage_old, damage_new)
        _assert_change(changes, "attacks", (attack,), "kz_at_full_mitigation", mitigation_old, mitigation_new)


def test_measure_changes_are_exactly_m6_init_and_m7_cia(changes):
    measure_changes = {(c.subject, c.field) for c in changes if c.group == "measures"}
    assert measure_changes == {
        *(((("M6"), level), "init") for level in (1, 2, 3)),
        *((("M7", level), "cia") for level in (1, 2, 3)),
    }
    for level, old, new in ((1, 10, 16), (2, 24, 30), (3, 40, 46)):
        _assert_change(changes, "measures", ("M6", level), "init", old, new)
    for level, old, new in (
        (1, (2, 3, 2), (0, 1, 0)),
        (2, (4, 5, 3), (2, 3, 1)),
        (3, (6, 7, 4), (4, 5, 2)),
    ):
        _assert_change(changes, "measures", ("M7", level), "cia", old, new)


def test_event_changes(changes):
    _assert_change(
        changes, "events", ("oem_audit",), "tiers",
        ((0, -15), (1, -5), (2, 0), (3, 0), (4, 5), (5, 15)),
        ((0, -2), (1, -1), (2, 0), (3, 1), (4, 2), (5, 3)),
    )
    _assert_change(
        changes, "events", ("kritische_schwachstelle",), "tiers",
        ((0, -5), (1, 0), (2, 3), (3, 7)),
        ((0, -3), (1, 0), (2, 0), (3, 4)),
    )
    _assert_change(changes, "events", ("nervige_authentifizierung",), "kz_delta", -10, -6)
    _assert_change(changes, "events", ("exzellenz_bonus",), "level", 3, 2, meaning=True)
    _assert_change(changes, "events", ("exzellenz_bonus",), "kz_per_measure", 5, 3)


def test_budget_review_changes(changes):
    _assert_change(
        changes, "budget_review", (), "tiers",
        ((0, 0), (25, 5), (50, 10), (75, 15)),
        ((0, 0), (25, 9), (50, 18), (75, 27)),
    )
    _assert_change(changes, "budget_review", (), "boundary", "above", "inclusive", meaning=True)
    _assert_change(changes, "budget_review", (), "overspend", ("flat", -15), ("per_step", 3, 10), meaning=True)


def test_exactly_three_changes_are_flagged_as_meaning_changes(changes):
    flagged = {(c.group, c.subject, c.field) for c in changes if c.meaning_changed}
    assert flagged == {
        ("events", ("exzellenz_bonus",), "level"),
        ("budget_review", (), "boundary"),
        ("budget_review", (), "overspend"),
    }


def test_unchanged_parameters_are_not_listed(changes):
    _assert_unchanged(changes, "waves", (2,), "e_threshold")
    _assert_unchanged(changes, "waves", (2, "M5"), "bonus")
    _assert_unchanged(changes, "waves", (3, "M2"), "bonus")
    _assert_unchanged(changes, "waves", (1, "M3"), "bonus")
    _assert_unchanged(changes, "events", ("sparprogramm",), "budget_delta")
    _assert_unchanged(changes, "events", ("operative_unterstuetzung",), "opex_per_measure")
    _assert_unchanged(changes, "base_cia", (), "cia")
    for attack in ("ransomware", "ot", "exfil"):
        for field in ("s_unit", "base_severity", "mitigation_cap", "cia_impact", "allow_recovery"):
            _assert_unchanged(changes, "attacks", (attack,), field)
    for tier in ("low", "medium", "high"):
        _assert_unchanged(changes, "budget_tiers", (tier,), "severity_multiplier")


def test_no_change_has_equal_old_and_new(changes):
    assert all(change.old != change.new for change in changes)


def test_the_order_is_deterministic_by_group(cfg, baseline, changes):
    assert value_changes(cfg, baseline) == changes
    positions = [BASELINE_GROUPS.index(change.group) for change in changes]
    assert positions == sorted(positions)


# --- mutations ---------------------------------------------------------------------------------------------


def test_a_changed_budget_adds_exactly_that_change(cfg, same):
    tiers = dict(cfg.budget_tiers)
    tiers["low"] = dataclasses.replace(tiers["low"], budget=tiers["low"].budget + 5)
    result = value_changes(dataclasses.replace(cfg, budget_tiers=tiers), same)
    assert [(c.group, c.subject, c.field, c.old, c.new) for c in result] == [
        ("budget_tiers", ("low",), "budget", cfg.budget_tiers["low"].budget, cfg.budget_tiers["low"].budget + 5)
    ]


def test_a_changed_measure_level_adds_exactly_that_change(cfg, same):
    measures = dict(cfg.measures)
    levels = dict(measures["M3"].levels)
    levels[2] = dataclasses.replace(levels[2], opex=levels[2].opex + 1)
    measures["M3"] = dataclasses.replace(measures["M3"], levels=levels)
    result = value_changes(dataclasses.replace(cfg, measures=measures), same)
    assert [(c.group, c.subject, c.field) for c in result] == [("measures", ("M3", 2), "opex")]


def test_a_changed_event_param_adds_exactly_that_change(cfg, same):
    events = {wave: list(items) for wave, items in cfg.events.items()}
    index = next(i for i, e in enumerate(events[2]) if e.id == "sparprogramm")
    event = events[2][index]
    events[2][index] = dataclasses.replace(event, params={**event.params, "budget_delta": -25})
    result = value_changes(dataclasses.replace(cfg, events=events), same)
    assert [(c.group, c.subject, c.field, c.old, c.new) for c in result] == [
        ("events", ("sparprogramm",), "budget_delta", -20, -25)
    ]


def test_a_changed_bonus_adds_exactly_that_change(cfg, same):
    waves = list(cfg.waves)
    bonus = list(waves[0].bonus_measures)
    bonus[0] = dataclasses.replace(bonus[0], bonus=bonus[0].bonus + 1)
    waves[0] = dataclasses.replace(waves[0], bonus_measures=bonus)
    result = value_changes(dataclasses.replace(cfg, waves=waves), same)
    assert [(c.group, c.subject, c.field) for c in result] == [("waves", (1, bonus[0].measure), "bonus")]


def test_a_removed_bonus_is_listed_with_new_none(cfg, same):
    waves = list(cfg.waves)
    waves[0] = dataclasses.replace(waves[0], bonus_measures=waves[0].bonus_measures[1:])
    removed = cfg.waves[0].bonus_measures[0]
    result = value_changes(dataclasses.replace(cfg, waves=waves), same)
    assert [(c.group, c.subject, c.field, c.old, c.new) for c in result] == [
        ("waves", (1, removed.measure), "bonus", removed.bonus, None),
        ("waves", (1, removed.measure), "min_level", removed.min_level, None),
    ]


# --- unknown and missing ids ---------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "mutate,needle",
    [
        (lambda raw: raw["measures"].__setitem__("M99", copy.deepcopy(raw["measures"]["M1"])), "M99"),
        (lambda raw: raw["attacks"].__setitem__("zz_attack", copy.deepcopy(raw["attacks"]["ot"])), "zz_attack"),
        (lambda raw: raw["events"].__setitem__("zz_event", {"kz_delta": -1}), "zz_event"),
        (lambda raw: raw["waves"].__setitem__("9", copy.deepcopy(raw["waves"]["1"])), "9"),
        (lambda raw: raw["budget_tiers"].__setitem__("zz_tier", copy.deepcopy(raw["budget_tiers"]["low"])), "zz_tier"),
    ],
)
def test_a_baseline_naming_something_unknown_to_the_config_is_an_error(cfg, tmp_path, mutate, needle):
    raw = _baseline_of_current(_current_raw(), tmp_path)
    mutate(raw)
    with pytest.raises(PrintModelError, match=needle):
        value_changes(cfg, _load_raw_baseline(raw, tmp_path))


def test_a_measure_missing_from_the_baseline_gives_old_none(cfg, tmp_path):
    raw = _baseline_of_current(_current_raw(), tmp_path)
    del raw["measures"]["M6"]
    result = value_changes(cfg, _load_raw_baseline(raw, tmp_path))
    assert {(c.group, c.subject, c.field) for c in result} == {
        ("measures", ("M6", level), field) for level in (1, 2, 3) for field in ("cia", "init", "opex", "recovery")
    }
    assert all(change.old is None and change.new is not None for change in result)
