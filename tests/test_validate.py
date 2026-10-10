import copy
import json
import subprocess
import sys
from fractions import Fraction

import pytest

from planspiel.cli import main
from planspiel.config import load_config
from planspiel.rules import kz_slope
from planspiel.simulate import run_simulation
from planspiel.validate import ConfigError, HandCalcWarning, scale_factors, validate
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


def _budget_review_first_minimum_negative(raw):
    raw["final_events"][0]["tiers"][0][0] = -5


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
    pytest.param(_budget_review_first_minimum_negative, "schema.tiers_order", "final_events[0].tiers", id="budget-review-first-minimum-not-zero"),
    pytest.param(
        _set(["events", "wave_2", 1, "tiers", 0, 0], -1),
        "schema.tiers_order",
        "events.wave_2[1].tiers",
        id="oem-audit-first-minimum-not-zero",
    ),
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
    pytest.param(
        _set(["attacks", "ransomware", "description"], "Prosa"),
        "schema.prose_in_config",
        "attacks.ransomware.description",
        id="prose-attack-description",
    ),
    pytest.param(_set(["waves", 0, "name"], "Prosa"), "schema.prose_in_config", "waves[0].name", id="prose-wave-name"),
    pytest.param(
        _set(["waves", 0, "bonus_measures", 0, "description"], "Prosa"),
        "schema.prose_in_config",
        "waves[0].bonus_measures[0].description",
        id="prose-bonus-description",
    ),
    pytest.param(
        _set(["events", "wave_1", 0, "description"], "Prosa"),
        "schema.prose_in_config",
        "events.wave_1[0].description",
        id="prose-event-description",
    ),
    pytest.param(
        _set(["final_events", 0, "description"], "Prosa"),
        "schema.prose_in_config",
        "final_events[0].description",
        id="prose-final-event-description",
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
    pytest.param(
        _set(["budget_tiers", "low", "e_targets"], {"1": 15, "2": 17, "3": 19}),
        "schema.removed_key",
        id="removed-e-targets",
    ),
    pytest.param(_set(["waves", 0, "kz_bonus"], 5), "schema.removed_key", id="removed-kz-bonus"),
    pytest.param(_set(["waves", 2, "kz_malus"], -7), "schema.removed_key", id="removed-kz-malus"),
    pytest.param(
        lambda raw: raw["events"]["wave_3"].append(raw["events"]["wave_2"].pop(0)),
        "rules.event_without_window",
        id="budget-cut-in-last-wave",
    ),
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


def _write_config(tmp_path, mutate, name="broken.json"):
    raw = copy.deepcopy(_raw())
    mutate(raw)
    path = tmp_path / name
    path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    return path


def _two_broken_references(raw):
    raw["waves"][0]["bonus_measures"][0]["measure"] = "M99"
    raw["waves"][1]["attack_id"] = "phishing"


def test_load_config_rejects_broken_reference_with_code_and_path(tmp_path):
    broken = _write_config(tmp_path, _set(["waves", 0, "bonus_measures", 0, "measure"], "M99"))
    with pytest.raises(ConfigError) as excinfo:
        load_config(broken)
    assert "ref.unknown_measure" in str(excinfo.value)
    assert "waves[0].bonus_measures[0].measure" in str(excinfo.value)


def test_load_config_lists_every_error(tmp_path):
    broken = _write_config(tmp_path, _two_broken_references)
    with pytest.raises(ConfigError) as excinfo:
        load_config(broken)
    assert {issue.code for issue in excinfo.value.issues} == {"ref.unknown_measure", "ref.unknown_attack"}
    assert "ref.unknown_measure" in str(excinfo.value)
    assert "ref.unknown_attack" in str(excinfo.value)


def test_load_config_warns_about_hand_calculability():
    with pytest.warns(HandCalcWarning, match="hand_calc.kz_slope"):
        load_config(CONFIG_PATH)


def test_cli_validate_real_config_exits_zero_with_one_warning(capsys):
    assert main(["validate", "--config", str(CONFIG_PATH)]) == 0
    out = capsys.readouterr().out
    assert "WARN hand_calc.kz_slope attacks.exfil" in out
    assert "0 Fehler, 1 Warnung(en)" in out


def test_cli_validate_strict_fails_on_warnings():
    assert main(["validate", "--config", str(CONFIG_PATH), "--strict"]) == 1


def test_cli_validate_broken_config_exits_one(tmp_path, capsys):
    broken = _write_config(tmp_path, _set(["waves", 0, "bonus_measures", 0, "measure"], "M99"))
    assert main(["validate", "--config", str(broken)]) == 1
    assert "ERROR ref.unknown_measure" in capsys.readouterr().out


def test_cli_validate_reports_invalid_json(tmp_path, capsys):
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    assert main(["validate", "--config", str(broken)]) == 1
    assert "ERROR schema.json" in capsys.readouterr().out


def _run(args):
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_module_entry_point_validates_default_config():
    result = _run(["-m", "planspiel", "validate"])
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert "17/7" in result.stdout.decode("utf-8")


def test_simulate_script_refuses_broken_config(tmp_path):
    broken = _write_config(tmp_path, _set(["waves", 0, "bonus_measures", 0, "measure"], "M99"))
    out = tmp_path / "out.json"
    result = _run(["simulate_outcomes.py", "--config", str(broken), "--output", str(out)])
    assert result.returncode != 0
    assert "ref.unknown_measure" in result.stderr.decode("utf-8", errors="replace")
    assert not out.exists()


def test_analyze_script_refuses_broken_config(tmp_path):
    broken = _write_config(tmp_path, _set(["waves", 0, "bonus_measures", 0, "measure"], "M99"))
    legacy = tmp_path / "legacy.json"
    run_simulation(MINI, "low", legacy, None, None, 0.0)
    result = _run(["analyze_simulation_results.py", "--input", str(legacy), "--config", str(broken)])
    assert result.returncode != 0
    assert "ref.unknown_measure" in result.stderr.decode("utf-8", errors="replace")
