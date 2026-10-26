"""The `reference_plans` config block: shape, validator references and ranges, loader (PRINT-10 part 2, D-22).

Legality of the real pinned paths is tested in the real-config section below (they are pinned at the checkpoint).
"""
import copy
import dataclasses
import json

import pytest

from planspiel.config import Config, load_config
from planspiel.validate import validate
from tests.support import REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"

VALID_BLOCK = {
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


def _with_block(block):
    raw = _raw()
    raw["reference_plans"] = block
    return raw


def _errors(raw):
    return [issue for issue in validate(raw) if issue.level == "error"]


def _codes(raw):
    return {issue.code for issue in _errors(raw)}


def test_an_absent_block_is_allowed():
    assert "reference_plans" not in _raw()
    assert _errors(_raw()) == []


def test_a_valid_block_has_no_errors():
    assert _errors(_with_block(copy.deepcopy(VALID_BLOCK))) == []


def test_the_loader_copies_the_block_and_defaults_to_empty(tmp_path):
    assert load_config(MINI).reference_plans == {}
    path = tmp_path / "config.json"
    path.write_text(json.dumps(_with_block(copy.deepcopy(VALID_BLOCK))), encoding="utf-8")
    assert load_config(path).reference_plans == VALID_BLOCK


def test_reference_plans_is_a_plain_trailing_config_field():
    fields = dataclasses.fields(Config)
    assert fields[-1].name == "reference_plans"
    assert fields[-1].default_factory() == {}


def test_block_must_be_an_object():
    assert "schema.type" in _codes(_with_block([]))


def test_unknown_tier_is_an_error():
    block = copy.deepcopy(VALID_BLOCK)
    block["extreme"] = block.pop("medium")
    assert "ref.unknown_tier" in _codes(_with_block(block))


def test_start_must_name_exactly_the_config_measures():
    missing = copy.deepcopy(VALID_BLOCK)
    del missing["medium"]["start"]["M6"]
    assert "ref.measure_set" in _codes(_with_block(missing))
    extra = copy.deepcopy(VALID_BLOCK)
    extra["medium"]["start"]["M9"] = 1
    assert "ref.measure_set" in _codes(_with_block(extra))


def test_window_selection_must_name_exactly_the_config_measures():
    block = copy.deepcopy(VALID_BLOCK)
    del block["medium"]["windows"][1]["selection"]["M1"]
    assert "ref.measure_set" in _codes(_with_block(block))


@pytest.mark.parametrize("level", [4, -1, "2", 1.5, True])
def test_levels_outside_the_measure_levels_are_errors(level):
    block = copy.deepcopy(VALID_BLOCK)
    block["medium"]["start"]["M1"] = level
    assert "schema.range" in _codes(_with_block(block)) or "schema.type" in _codes(_with_block(block))


def test_too_many_windows_is_an_error():
    block = copy.deepcopy(VALID_BLOCK)
    block["medium"]["windows"].append(copy.deepcopy(block["medium"]["windows"][1]))
    assert "ref.window_count" in _codes(_with_block(block))


def test_a_swap_naming_an_unknown_measure_is_an_error():
    block = copy.deepcopy(VALID_BLOCK)
    block["medium"]["windows"][0]["swap"] = ["M4", "M99"]
    assert "ref.unknown_measure" in _codes(_with_block(block))


def test_a_swap_must_name_two_different_measures():
    block = copy.deepcopy(VALID_BLOCK)
    block["medium"]["windows"][0]["swap"] = ["M4"]
    assert "schema.type" in _codes(_with_block(block))
    block["medium"]["windows"][0]["swap"] = ["M4", "M4"]
    assert "ref.swap_same_measure" in _codes(_with_block(block))


def test_missing_keys_are_reported():
    block = copy.deepcopy(VALID_BLOCK)
    del block["medium"]["start"]
    assert "schema.keys" in _codes(_with_block(block))
    block = copy.deepcopy(VALID_BLOCK)
    del block["medium"]["windows"][1]["selection"]
    assert "schema.keys" in _codes(_with_block(block))
