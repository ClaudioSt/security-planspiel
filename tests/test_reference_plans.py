"""The `reference_plans` config block: shape, validator references and ranges, loader (PRINT-10 part 2, D-22).

Legality of the real pinned paths is tested in the real-config section below (they are pinned at the checkpoint).
"""
import copy
import dataclasses
import json

import pytest

from planspiel import refpaths, rules
from planspiel.config import Config, load_config
from planspiel.validate import validate
from tests.support import CONFIG_PATH, REPO_ROOT

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


def test_reference_plans_is_a_plain_defaulted_config_field_before_practice():
    fields = {field.name: field for field in dataclasses.fields(Config)}
    assert fields["reference_plans"].default_factory() == {}
    names = list(fields)
    assert names.index("reference_plans") < names.index("practice") == len(names) - 1


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


# --- real config: the three reference paths re-chosen in 06-09 and approved at D-04 --------------------------------

TIERS = ("low", "medium", "high")
REAL_IDS = tuple(f"M{number}" for number in range(1, 11))


def _levels(**levels):
    return {measure_id: levels.get(measure_id, 0) for measure_id in REAL_IDS}


# Approved structure only (D-22): start, the Kurswechsel swap with its window selection, one voluntary move.
APPROVED = {
    "low": {
        "start": _levels(M4=1, M6=2, M7=1, M8=1, M9=3, M10=2),
        "swap": ("M8", "M5"),
        "swapped": _levels(M4=1, M5=1, M6=2, M7=1, M9=3, M10=2),
        "moved": _levels(M4=1, M5=1, M7=1, M9=3, M10=2),
    },
    "medium": {
        "start": _levels(M4=1, M6=3, M7=1, M8=1, M9=2, M10=3),
        "swap": ("M4", "M5"),
        "swapped": _levels(M5=1, M6=3, M7=1, M8=1, M9=2, M10=3),
        "moved": _levels(M6=3, M7=1, M8=1, M9=2, M10=3),
    },
    "high": {
        "start": _levels(M4=1, M5=2, M7=1, M8=1, M9=2, M10=3),
        "swap": ("M4", "M6"),
        "swapped": _levels(M5=2, M6=1, M7=1, M8=1, M9=2, M10=3),
        "moved": _levels(M3=1, M5=2, M6=1, M7=1, M8=1, M9=2, M10=3),
    },
}


@pytest.fixture(scope="module")
def real():
    return load_config(CONFIG_PATH)


def test_real_config_pins_exactly_the_budget_tiers(real):
    assert set(real.reference_plans) == set(real.budget_tiers) == set(TIERS)


@pytest.mark.parametrize("tier", TIERS)
def test_pinned_path_has_the_approved_structure(real, tier):
    approved = APPROVED[tier]
    path = refpaths.reference_path(real, tier)
    assert path.start == approved["start"]
    assert len(path.windows) == 2
    assert path.windows[0].selection == approved["swapped"]
    assert path.windows[0].swap == approved["swap"]
    assert path.windows[1].selection == approved["moved"]
    assert path.windows[1].swap is None


@pytest.mark.parametrize("tier", TIERS)
def test_pinned_path_is_legal_in_budget_with_swap_and_voluntary_move(real, tier):
    path = refpaths.reference_path(real, tier)
    record = rules.evaluate_path(real, tier, path)  # raises PathError when illegal; Kurswechsel enforced
    assert record["over_budget"] is False
    swap_window = [wave.wave_id for wave in real.waves].index(rules.kurswechsel_wave(real.events))
    assert path.windows[swap_window].swap is not None
    assert refpaths.voluntary_moves(real, path)


@pytest.mark.parametrize("tier", TIERS)
def test_pinned_path_touches_the_mechanics(real, tier):
    trace = rules.path_trace(real, tier, refpaths.reference_path(real, tier))
    waves = trace.waves
    assert any(wave.case == 3 for wave in waves)
    assert any(wave.recovery_factor > 0 for wave in waves)
    assert any(wave.bonus_met for wave in waves) and any(wave.bonus_missed for wave in waves)
    assert any(wave.bonus_met and wave.bonus_missed for wave in waves)
    assert any(wave.kz_event != 0 for wave in waves)
    assert refpaths.mechanics_score(trace, refpaths.review_deltas(real)) == refpaths.MECHANICS_MAX


def test_real_config_still_validates_without_a_new_error():
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    assert "reference_plans" in raw
    assert _errors(raw) == []
