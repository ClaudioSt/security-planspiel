"""The `reference_strategies` config block: shape, validator, loader, shared path builder (BAL-07, D-25).

The block is separate from `reference_plans` (answer keys). The overspender archetype is not an entry, it is judged
by the overspend gate (D-23). Placement and legality against the quartiles live in tests/test_strategies.py.
"""
import copy
import dataclasses
import json

import pytest

from planspiel import refpaths, rules
from planspiel.config import Config, load_config
from planspiel.validate import REFERENCE_STRATEGY_KINDS, validate
from tests.support import CONFIG_PATH, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
TIERS = ("low", "medium", "high")
NAMES = ("good", "mediocre", "bad_ignore", "bad_all_in", "bad_hoard")

REFERENCE_PLAN_BLOCK = {
    "medium": {
        "start": {"M1": 2, "M2": 2, "M4": 1, "M6": 0},
        "windows": [
            {"selection": {"M1": 2, "M2": 2, "M4": 0, "M6": 1}, "swap": ["M4", "M6"]},
            {"selection": {"M1": 2, "M2": 2, "M4": 0, "M6": 0}},
        ],
    }
}


def _raw():
    return json.loads(MINI.read_text(encoding="utf-8"))


def _errors(raw):
    return [issue for issue in validate(raw) if issue.level == "error"]


def _codes(raw):
    return {issue.code for issue in _errors(raw)}


def _entry(raw, tier="medium", name="good"):
    return raw["reference_strategies"][tier][name]


def test_the_kinds_are_good_mediocre_bad():
    assert REFERENCE_STRATEGY_KINDS == ("good", "mediocre", "bad")


def test_the_mini_config_carries_five_entries_per_tier():
    block = _raw()["reference_strategies"]
    assert set(block) == set(TIERS)
    for tier in TIERS:
        assert tuple(block[tier]) == NAMES
        assert [block[tier][name]["kind"] for name in NAMES] == ["good", "mediocre", "bad", "bad", "bad"]


def test_the_mini_block_has_no_validator_errors():
    assert _errors(_raw()) == []


def test_an_absent_block_is_allowed():
    raw = _raw()
    del raw["reference_strategies"]
    assert _errors(raw) == []


def test_the_loader_exposes_the_block_and_defaults_to_empty(tmp_path):
    cfg = load_config(MINI)
    assert cfg.reference_strategies == _raw()["reference_strategies"]
    raw = _raw()
    del raw["reference_strategies"]
    path = tmp_path / "config.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    assert load_config(path).reference_strategies == {}


def test_the_real_config_carries_the_block():
    block = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))["reference_strategies"]
    assert block
    assert load_config(CONFIG_PATH).reference_strategies == block


def test_reference_strategies_sits_after_reference_plans_and_practice_stays_last():
    fields = {field.name: field for field in dataclasses.fields(Config)}
    assert fields["reference_strategies"].default_factory() == {}
    names = list(fields)
    assert names.index("reference_plans") + 1 == names.index("reference_strategies")
    assert names[-1] == "practice"


def test_the_block_must_be_an_object():
    raw = _raw()
    raw["reference_strategies"] = []
    assert "schema.type" in _codes(raw)


def test_an_unknown_tier_is_an_error():
    raw = _raw()
    raw["reference_strategies"]["extreme"] = raw["reference_strategies"].pop("medium")
    assert "ref.unknown_tier" in _codes(raw)


def test_a_tier_must_be_an_object():
    raw = _raw()
    raw["reference_strategies"]["medium"] = []
    assert "schema.type" in _codes(raw)


@pytest.mark.parametrize("kind", ["excellent", "", 3, None])
def test_an_unknown_kind_is_an_error(kind):
    raw = _raw()
    _entry(raw)["kind"] = kind
    assert "ref.bad_kind" in _codes(raw)


def test_a_missing_kind_is_an_error():
    raw = _raw()
    del _entry(raw)["kind"]
    assert "ref.bad_kind" in _codes(raw)


def test_an_unknown_key_in_an_entry_is_an_error():
    raw = _raw()
    _entry(raw)["note"] = "x"
    assert "schema.keys" in _codes(raw)


def test_a_non_object_entry_is_an_error():
    raw = _raw()
    raw["reference_strategies"]["medium"]["good"] = "M1"
    assert "schema.type" in _codes(raw)


def test_the_start_must_name_exactly_the_config_measures():
    raw = _raw()
    del _entry(raw)["start"]["M6"]
    assert "ref.measure_set" in _codes(raw)


def test_a_missing_start_is_reported():
    raw = _raw()
    del _entry(raw)["start"]
    assert "schema.keys" in _codes(raw)


def test_a_level_outside_the_measure_levels_is_an_error():
    raw = _raw()
    _entry(raw)["start"]["M1"] = 4
    assert "schema.range" in _codes(raw)


def test_too_many_windows_is_an_error():
    raw = _raw()
    windows = _entry(raw)["windows"]
    windows.extend(copy.deepcopy(windows[-1]) for _ in range(3))
    assert "ref.window_count" in _codes(raw)


def test_a_swap_naming_the_same_measure_twice_is_an_error():
    raw = _raw()
    _entry(raw)["windows"][0]["swap"] = ["M4", "M4"]
    assert "ref.swap_same_measure" in _codes(raw)


def test_an_unknown_key_in_a_window_is_an_error():
    raw = _raw()
    _entry(raw)["windows"][0]["extra"] = 1
    assert "schema.keys" in _codes(raw)


def test_reference_plans_still_reject_a_kind_key():
    raw = _raw()
    raw["reference_plans"] = {"medium": dict(copy.deepcopy(REFERENCE_PLAN_BLOCK["medium"]), kind="good")}
    assert "schema.keys" in _codes(raw)


def test_reference_plans_and_strategies_validate_side_by_side():
    raw = _raw()
    raw["reference_plans"] = copy.deepcopy(REFERENCE_PLAN_BLOCK)
    assert _errors(raw) == []


def test_path_from_block_builds_the_same_path_as_reference_path():
    cfg = dataclasses.replace(load_config(MINI), reference_plans=copy.deepcopy(REFERENCE_PLAN_BLOCK))
    built = refpaths.path_from_block(REFERENCE_PLAN_BLOCK["medium"])
    assert built == refpaths.reference_path(cfg, "medium")
    assert isinstance(built, rules.Path)
    assert built.windows[0].swap == ("M4", "M6") and built.windows[1].swap is None


def test_path_from_block_copies_the_selections():
    block = copy.deepcopy(REFERENCE_PLAN_BLOCK["medium"])
    built = refpaths.path_from_block(block)
    block["start"]["M1"] = 0
    assert built.start["M1"] == 2


@pytest.mark.parametrize("tier", TIERS)
@pytest.mark.parametrize("name", NAMES)
def test_every_mini_entry_is_a_legal_in_budget_path(tier, name):
    cfg = load_config(MINI)
    path = refpaths.path_from_block(cfg.reference_strategies[tier][name])
    record = rules.evaluate_path(cfg, tier, path)  # raises PathError when illegal, Kurswechsel enforced
    assert record["over_budget"] is False
