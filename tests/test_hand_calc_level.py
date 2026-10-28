"""BAL-02: the hand-calculability findings of the validator can be raised to errors (`hand_calc_level`)."""
import copy
import json

import pytest

from planspiel.config import read_raw_config
from planspiel.validate import validate
from tests.support import CONFIG_PATH, REPO_ROOT, candidate

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"


def _raw(path=CONFIG_PATH):
    return json.loads(path.read_text(encoding="utf-8"))


def _mutated(mutate):
    raw = copy.deepcopy(_raw())
    mutate(raw)
    return raw


def _set(path_parts, value):
    def mutate(raw):
        target = raw
        for part in path_parts[:-1]:
            target = target[part]
        target[path_parts[-1]] = value

    return mutate


def _level_of(issues, code):
    return sorted({issue.level for issue in issues if issue.code == code})


HAND_CALC_MUTATIONS = [
    pytest.param(_set(["attacks", "ot", "kz_at_full_damage"], -6), "hand_calc.kz_slope", id="kz-slope"),
    pytest.param(_set(["attacks", "ransomware", "base_severity"], 9), "hand_calc.severity_cap", id="severity-cap"),
    pytest.param(_set(["budget_tiers", "low", "severity_multiplier"], 1.1), "hand_calc.severity_multiplier", id="severity-multiplier"),
    pytest.param(
        lambda raw: raw["waves"][0].update(weights={"c": 0.45, "i": 0.35, "a": 0.2}),
        "hand_calc.weights",
        id="weights",
    ),
    pytest.param(_set(["measures", "M4", "levels", "1", "recovery"], 0.15), "hand_calc.recovery", id="recovery"),
    pytest.param(_set(["final_events", 0, "overspend_penalty", "step"], 5), "hand_calc.penalty_step", id="penalty-step"),
    pytest.param(_set(["final_index", "weight_ros"], 20.5), "hand_calc.final_index_weights", id="final-index-weights"),
]


@pytest.mark.parametrize(("mutate", "code"), HAND_CALC_MUTATIONS)
def test_hand_calc_code_follows_the_level(mutate, code):
    raw = _mutated(mutate)
    assert _level_of(validate(raw), code) == ["warning"]
    assert _level_of(validate(raw, hand_calc_level="warning"), code) == ["warning"]
    assert _level_of(validate(raw, hand_calc_level="error"), code) == ["error"]


NON_HAND_CALC_MUTATIONS = [
    pytest.param(
        lambda raw: raw["waves"][0].pop("e_threshold"),
        "schema.default_used",
        id="hidden-default",
    ),
    pytest.param(_set(["waves", 0, "kz_bonus"], 5), "schema.removed_key", id="removed-key"),
    pytest.param(
        lambda raw: raw["events"]["wave_3"].append(raw["events"]["wave_2"].pop(0)),
        "rules.event_without_window",
        id="event-without-window",
    ),
]


@pytest.mark.parametrize(("mutate", "code"), NON_HAND_CALC_MUTATIONS)
def test_other_warnings_stay_warnings_in_error_mode(mutate, code):
    issues = validate(_mutated(mutate), hand_calc_level="error")
    assert _level_of(issues, code) == ["warning"]


def test_unknown_level_is_rejected():
    with pytest.raises(ValueError):
        validate(_raw(), hand_calc_level="loud")


def test_final_index_weights_of_the_form_kz_plus_k_ros_are_fine():
    raw = _mutated(_set(["final_index", "weight_ros"], 20))
    assert [i for i in validate(raw, hand_calc_level="error") if i.code == "hand_calc.final_index_weights"] == []


@pytest.mark.parametrize(
    "weights",
    [{"weight_kz": 1, "weight_ros": 20.5}, {"weight_kz": 2, "weight_ros": 20}],
    ids=["fractional-ros-weight", "kz-weight-not-one"],
)
def test_bad_final_index_weights_yield_exactly_one_finding(weights):
    raw = _mutated(_set(["final_index"], weights))
    findings = [i for i in validate(raw) if i.code == "hand_calc.final_index_weights"]
    assert [(f.level, f.path) for f in findings] == [("warning", "final_index")]


@pytest.mark.parametrize("path", [CONFIG_PATH, MINI], ids=["real", "mini"])
def test_todays_final_index_weights_are_fine(path):
    assert [i for i in validate(_raw(path)) if i.code == "hand_calc.final_index_weights"] == []


def test_default_call_on_the_real_config_is_unchanged():
    issues = validate(_raw())
    assert [(i.level, i.code, i.path) for i in issues] == [("warning", "hand_calc.kz_slope", "attacks.exfil")]


def _errors(issues):
    return [issue for issue in issues if issue.level == "error"]


def _exfil_one_decimal(raw):
    raw["attacks"]["exfil"]["kz_at_full_damage"] = -5
    raw["attacks"]["exfil"]["kz_at_full_mitigation"] = 9


def test_real_config_in_error_mode_has_only_the_exfil_slope():
    errors = _errors(validate(_raw(), hand_calc_level="error"))
    assert [(issue.code, issue.path) for issue in errors] == [("hand_calc.kz_slope", "attacks.exfil")]
    assert "17/7" in errors[0].message
    assert "Welle 3" in errors[0].message


def test_exfil_with_one_decimal_slope_has_no_issue_in_error_mode():
    raw = _mutated(_exfil_one_decimal)
    assert raw["attacks"]["exfil"]["mitigation_cap"] == 7
    assert validate(raw, hand_calc_level="error") == []


def test_cli_strict_gate_accepts_the_one_decimal_variant_only(tmp_path):
    from planspiel.cli import main

    config_file = tmp_path / "candidate_config.json"
    config_file.write_text(json.dumps(_mutated(_exfil_one_decimal)), encoding="utf-8")
    assert main(["validate", "--config", str(config_file), "--strict"]) == 0
    assert main(["validate", "--config", str(CONFIG_PATH), "--strict"]) == 1


@pytest.mark.slow
@pytest.mark.balance
@candidate.TUNING_TARGET
def test_configured_config_is_hand_friendly(balance_config_path):
    issues = validate(read_raw_config(balance_config_path), hand_calc_level="error")
    assert _errors(issues) == [], [(issue.code, issue.path) for issue in _errors(issues)]
