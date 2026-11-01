"""The per-wave E-target KZ bonus/malus is gone (RULE-08, D-19)."""
import copy
import inspect
import json
from fractions import Fraction

import pytest

from planspiel import rules
from planspiel.config import BudgetTier, Wave, load_config
from planspiel.rules import clamp_kz, wave_kz_change
from planspiel.validate import validate
from tests.support import CONFIG_PATH, REPO_ROOT, harness
from tests.support.ties import NEGATIVE_TIE_EVENT, tie_codes, tie_total, write_tie_config

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
REMOVED_RECORD_KEYS = {"e_target", "e_reached", "kz_delta_e_target"}


def _raw(path=CONFIG_PATH):
    return json.loads(path.read_text(encoding="utf-8"))


def _warnings(issues):
    return [issue for issue in issues if issue.level == "warning"]


def _errors(issues):
    return [issue for issue in issues if issue.level == "error"]


def _write(tmp_path, raw):
    path = tmp_path / "simulation_config.json"
    path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    return path


def _golden_cases(tier):
    path = REPO_ROOT / "tests" / "golden" / f"characterization_{tier}.json"
    return json.loads(path.read_text(encoding="utf-8"))["cases"]


def _evaluate(cfg, tier, code):
    return harness.evaluate(cfg, tier, harness.selection_of(cfg, code))


def _event_kz(wave):
    return sum(event["kz_delta"] for event in wave["events"])


@pytest.mark.parametrize("path", [CONFIG_PATH, MINI], ids=["real", "mini"])
def test_raw_configs_carry_no_e_target_keys(path):
    raw = _raw(path)
    assert all("e_targets" not in tier for tier in raw["budget_tiers"].values())
    assert all("kz_bonus" not in wave and "kz_malus" not in wave for wave in raw["waves"])


def test_loader_dataclasses_have_no_e_target_fields():
    assert not hasattr(Wave, "kz_bonus") and "kz_bonus" not in Wave.__dataclass_fields__
    assert "kz_malus" not in Wave.__dataclass_fields__
    assert "e_targets" not in BudgetTier.__dataclass_fields__
    cfg = load_config(CONFIG_PATH)
    assert not hasattr(cfg.waves[0], "kz_bonus")
    assert not hasattr(cfg.budget_tiers["low"], "e_targets")


@pytest.mark.parametrize(
    ("mutate", "path"),
    [
        (lambda raw: raw["budget_tiers"]["low"].update(e_targets={"1": 15, "2": 17, "3": 19}), "budget_tiers.low.e_targets"),
        (lambda raw: raw["waves"][0].update(kz_bonus=5), "waves[0].kz_bonus"),
        (lambda raw: raw["waves"][2].update(kz_malus=-7), "waves[2].kz_malus"),
    ],
    ids=["e_targets", "kz_bonus", "kz_malus"],
)
def test_leftover_key_is_a_removed_key_warning(mutate, path):
    raw = copy.deepcopy(_raw())
    mutate(raw)
    issues = validate(raw)
    assert _errors(issues) == []
    removed = [issue for issue in _warnings(issues) if issue.code == "schema.removed_key"]
    assert [issue.path for issue in removed] == [path]


def test_leftover_key_never_changes_a_result(tmp_path):
    raw = copy.deepcopy(_raw())
    raw["budget_tiers"]["medium"]["e_targets"] = {"1": 99, "2": 99, "3": 99}
    raw["waves"][0]["kz_bonus"] = 40
    raw["waves"][0]["kz_malus"] = -40
    cfg = harness.load_config(_write(tmp_path, raw))
    reference = harness.load_config()
    code = "3" * len(cfg.measures)
    assert _evaluate(cfg, "medium", code)["kz_final"] == _evaluate(reference, "medium", code)["kz_final"]


def test_e_target_check_is_gone_and_wave_kz_change_has_two_parameters():
    assert not hasattr(rules, "e_target_check")
    assert list(inspect.signature(wave_kz_change).parameters) == ["attack_kz_delta", "event_kz"]


@pytest.mark.parametrize(
    ("attack_delta", "event_kz", "expected"),
    [
        (Fraction(3, 2), 0, 2),
        (Fraction(3, 2), -7, -6),
        (Fraction(-32, 7), -7, -12),
        (Fraction(-6), 1, -5),
        (Fraction(5, 2), 0, 3),
        (Fraction(-5, 2), 0, -3),
    ],
)
def test_wave_kz_change_is_attack_plus_events_rounded_once(attack_delta, event_kz, expected):
    assert wave_kz_change(attack_delta, event_kz) == expected


@pytest.mark.parametrize("tier", ("low", "medium", "high"))
def test_records_carry_no_e_target_data(tier):
    cfg = harness.load_config()
    record = _evaluate(cfg, tier, "0" * len(cfg.measures))
    for wave in record["waves"]:
        assert not REMOVED_RECORD_KEYS & set(wave)
    assert "e_reached" not in rules.CompactOutcome._fields


def test_empty_selection_medium_without_e_target():
    cfg = harness.load_config()
    record = _evaluate(cfg, "medium", "0" * len(cfg.measures))
    assert [wave["kz_after"] for wave in record["waves"]] == [28, 17, 11]
    assert record["kz_final"] == 38
    assert record["total_damage"] == 620
    assert record["final_events"][0]["kz_delta"] == 27


def test_positive_tie_rounds_up(tmp_path):
    cfg = harness.load_config(write_tie_config(tmp_path))
    waves = _evaluate(cfg, "medium", tie_codes(cfg, "medium", positive=True)[0])["waves"]
    wave3 = waves[2]
    total = tie_total(wave3)
    assert total > 0 and total % 1 == Fraction(1, 2)
    assert wave3["kz_after"] == clamp_kz(waves[1]["kz_after"] + total + Fraction(1, 2))


def test_negative_tie_rounds_down_with_test_only_event(tmp_path):
    cfg = harness.load_config(write_tie_config(tmp_path, [NEGATIVE_TIE_EVENT]))
    waves = _evaluate(cfg, "medium", tie_codes(cfg, "medium", positive=False)[0])["waves"]
    wave3 = waves[2]
    total = tie_total(wave3)
    assert total < 0 and total % 1 == Fraction(1, 2)
    assert any(event["id"] == "test_negative_tie" for event in wave3["events"])
    assert wave3["kz_after"] == clamp_kz(waves[1]["kz_after"] + total - Fraction(1, 2))


def test_clamp_happens_after_rounding(tmp_path):
    raw = copy.deepcopy(_raw())
    raw["budget_tiers"]["medium"]["kz_start"] = 100
    cfg = harness.load_config(_write(tmp_path, raw))
    wave1 = _evaluate(cfg, "medium", "3" * len(cfg.measures))["waves"][0]
    change = wave_kz_change(wave1["kz_delta_attack"], _event_kz(wave1))
    assert wave1["kz_after"] == 100
    assert 100 + change > 100


def test_gesamtreduktion_is_compared_exactly_with_threshold():
    cfg = harness.load_config()
    code = next(
        case["code"] for case in _golden_cases("medium") if "census:g_eq_threshold_w2" in case["tags"]
    )
    wave2 = _evaluate(cfg, "medium", code)["waves"][1]
    assert wave2["gesamtreduktion"] == cfg.waves[1].e_threshold
    assert wave2["capped_reduction"] == 0


def test_readme_and_claude_md_describe_no_e_target_check():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8").replace("\u2011", "-")
    claude_md = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8").replace("\u2011", "-")
    assert "E-Ziel prüfen" not in readme
    assert "E-Ziel erreicht" not in readme
    assert "E-Ziel-Check" not in claude_md
    assert "Angriff + E-Ziel" not in claude_md
    assert "Angriff + E-Ziel" not in readme
