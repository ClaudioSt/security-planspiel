import copy
import json
from fractions import Fraction

import pytest

from planspiel.rules import kz_slope
from planspiel.validate import scale_factors, validate
from tests.support import CONFIG_PATH, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"


def _raw(path=CONFIG_PATH):
    return json.loads(path.read_text(encoding="utf-8"))


def _errors(issues):
    return [issue for issue in issues if issue.level == "error"]


def _warnings(issues):
    return [issue for issue in issues if issue.level == "warning"]


def test_real_config_has_no_errors_and_one_slope_warning():
    issues = validate(_raw())
    assert _errors(issues) == []
    warnings = _warnings(issues)
    assert len(warnings) == 1
    warning = warnings[0]
    assert warning.code == "hand_calc.kz_slope"
    assert warning.path == "attacks.exfil"
    assert "Welle 3" in warning.message
    assert "17/7" in warning.message


def test_mini_config_has_no_errors():
    assert _errors(validate(_raw(MINI))) == []


def test_scale_factors_real_config():
    assert scale_factors(_raw()) == (10, 10)


def test_kz_slope_is_exact():
    assert kz_slope(-7, 10, 7) == Fraction(17, 7)
    assert kz_slope(-6, 10, 8) == 2
    assert kz_slope(-5, 7, 10) == Fraction(6, 5)


def _set(path_parts, value):
    def mutate(raw):
        target = raw
        for part in path_parts[:-1]:
            target = target[part]
        target[path_parts[-1]] = value

    return mutate


def _delete(path_parts):
    def mutate(raw):
        target = raw
        for part in path_parts[:-1]:
            target = target[part]
        del target[path_parts[-1]]

    return mutate


def _final_event_into_wave_1(raw):
    raw["events"]["wave_1"].append(copy.deepcopy(raw["final_events"][0]))


def _reverse_budget_tiers(raw):
    raw["final_events"][0]["tiers"].reverse()


def _dependency_cycle(raw):
    raw["measures"]["M2"]["dependencies"] = [
        {"level": 1, "requires": [{"measure": "M1", "min_level": 1}]}
    ]


def _rename_wave_key(raw):
    raw["events"]["wave_9"] = raw["events"].pop("wave_3")


ERROR_MUTATIONS = [
    pytest.param(
        _set(["waves", 0, "bonus_measures", 0, "measure"], "M99"),
        "ref.unknown_measure",
        "waves[0].bonus_measures[0].measure",
        id="unknown-bonus-measure",
    ),
    pytest.param(_set(["waves", 0, "attack_id"], "phishing"), "ref.unknown_attack", "waves[0].attack_id", id="unknown-attack"),
    pytest.param(
        _set(["measures", "M1", "dependencies", 0, "requires", 0, "measure"], "M42"),
        "ref.unknown_measure",
        "measures.M1.dependencies[0].requires[0].measure",
        id="dependency-on-unknown-measure",
    ),
    pytest.param(_dependency_cycle, "ref.dependency_cycle", "measures.", id="dependency-cycle"),
    pytest.param(_delete(["budget_tiers", "low", "e_targets", "3"]), "schema.e_targets", "budget_tiers.low.e_targets", id="missing-e-target"),
    pytest.param(
        _set(["events", "wave_2", 1, "measures", 0], "M77"),
        "ref.unknown_measure",
        "events.wave_2[1].measures[0]",
        id="event-unknown-measure",
    ),
    pytest.param(_set(["events", "wave_1", 0, "type"], "mystery"), "schema.unknown_event_type", "events.wave_1[0].type", id="unknown-event-type"),
    pytest.param(_final_event_into_wave_1, "schema.event_placement", "events.wave_1[2]", id="final-event-in-wave"),
    pytest.param(_set(["default_budget_tier"], "huge"), "ref.unknown_tier", "default_budget_tier", id="unknown-default-tier"),
    pytest.param(_delete(["measures", "M3", "levels", "3"]), "schema.levels", "measures.M3.levels", id="missing-level"),
    pytest.param(_set(["attacks", "ot", "mitigation_cap"], True), "schema.type", "attacks.ot.mitigation_cap", id="bool-is-not-a-number"),
    pytest.param(_reverse_budget_tiers, "schema.tiers_order", "final_events[0].tiers", id="tiers-out-of-order"),
    pytest.param(_set(["attacks", "ot", "mitigation_cap"], 0), "schema.range", "attacks.ot.mitigation_cap", id="mitigation-cap-zero"),
    pytest.param(_set(["waves", 2, "id"], 4), "schema.wave_ids", "waves", id="wave-ids-not-consecutive"),
    pytest.param(_rename_wave_key, "ref.unknown_wave", "events.wave_9", id="events-unknown-wave"),
    pytest.param(
        _set(["budget_tiers", "low", "severity_multiplier"], 1.25),
        "exact.severity_scaling",
        "budget_tiers.low",
        id="severity-scaling-not-integral",
    ),
    pytest.param(
        _set(["measures", "M4", "levels", "1", "recovery"], 0.1234),
        "exact.damage_whole_euros",
        "attacks.",
        id="damage-not-whole-euros",
    ),
]


@pytest.mark.parametrize(("mutate", "code", "path_fragment"), ERROR_MUTATIONS)
def test_broken_config_is_reported(mutate, code, path_fragment):
    raw = copy.deepcopy(_raw())
    mutate(raw)
    errors = _errors(validate(raw))
    matching = [issue for issue in errors if issue.code == code]
    assert matching, [(issue.code, issue.path) for issue in errors]
    assert any(path_fragment in issue.path for issue in matching), [issue.path for issue in matching]


WARNING_MUTATIONS = [
    pytest.param(_set(["attacks", "ransomware", "base_severity"], 9), "hand_calc.severity_cap", id="base-severity-not-cap"),
    pytest.param(_set(["budget_tiers", "low", "severity_multiplier"], 1.1), "hand_calc.severity_multiplier", id="severity-multiplier"),
    pytest.param(
        lambda raw: raw["waves"][0].update(weights={"c": 0.45, "i": 0.35, "a": 0.2}),
        "hand_calc.weights",
        id="weights-two-decimals",
    ),
    pytest.param(_set(["waves", 1, "weights", "a"], 0.5), "hand_calc.weights", id="weights-sum-not-one"),
    pytest.param(_set(["measures", "M4", "levels", "1", "recovery"], 0.15), "hand_calc.recovery", id="recovery-two-decimals"),
    pytest.param(_delete(["waves", 0, "e_threshold"]), "schema.default_used", id="hidden-default-e-threshold"),
]


@pytest.mark.parametrize(("mutate", "code"), WARNING_MUTATIONS)
def test_hand_calc_issue_is_a_warning_not_an_error(mutate, code):
    raw = copy.deepcopy(_raw())
    mutate(raw)
    issues = validate(raw)
    assert _errors(issues) == [], [(issue.code, issue.path) for issue in _errors(issues)]
    assert code in {issue.code for issue in _warnings(issues)}


def test_all_errors_are_collected():
    raw = copy.deepcopy(_raw())
    raw["waves"][0]["bonus_measures"][0]["measure"] = "M99"
    raw["waves"][1]["attack_id"] = "phishing"
    codes = sorted(issue.code for issue in _errors(validate(raw)))
    assert codes == ["ref.unknown_attack", "ref.unknown_measure"]
