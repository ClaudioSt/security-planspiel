"""The risk_matrix block (RISK-01, D-01, D-04, D-20, D-22, D-24): loader, invisibility to the rules and the band product rules.

The block is read only by the validator, the print models and tests, never by rules or enumeration. The product rules
(five register rows, limits 0 / 50 / 150 thousand euros) live here and not in the validator, so a future band change is
a deliberate test edit.
"""
import copy
import dataclasses
import json

import pytest

from planspiel import rules
from planspiel.config import RiskBand, RiskMatrix, load_config
from planspiel.risk import band_of
from planspiel.validate import validate
from tests.support import CONFIG_PATH


def _raw():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _errors(raw):
    return [issue for issue in validate(raw) if issue.level == "error"]


def _codes(raw):
    return [issue.code for issue in _errors(raw)]


def _load(raw, tmp_path, name="config.json"):
    target = tmp_path / name
    target.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    return load_config(target)


def _mutated(mutate):
    raw = _raw()
    mutate(raw["risk_matrix"])
    return raw


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


# --- loader ----------------------------------------------------------------------------------------------------


def test_the_real_config_carries_the_matrix(cfg):
    matrix = cfg.risk_matrix
    assert isinstance(matrix, RiskMatrix)
    assert matrix.register_rows == 5
    assert all(isinstance(band, RiskBand) for band in matrix.bands)
    assert [(band.id, band.minimum) for band in matrix.bands] == [("low", 0), ("medium", 50), ("high", 150)]


def test_a_config_without_the_block_has_no_matrix(tmp_path):
    raw = _raw()
    del raw["risk_matrix"]
    assert _load(raw, tmp_path).risk_matrix is None


# --- invisible to the rules ---------------------------------------------------------------------------------


def test_the_block_never_reaches_the_real_machinery(cfg, tmp_path):
    raw = _raw()
    del raw["risk_matrix"]
    plain = _load(raw, tmp_path)
    assert dataclasses.replace(cfg, risk_matrix=None) == plain
    selection = {"M1": 2, "M2": 2, "M3": 1, "M4": 1, "M5": 0, "M6": 1, "M7": 0, "M8": 0, "M9": 0, "M10": 0}
    assert rules.evaluate_plan(cfg, "medium", selection) == rules.evaluate_plan(plain, "medium", selection)


# --- unprotected damage and product rules -------------------------------------------------------------------


def test_the_unprotected_damages_are_the_known_game_values(cfg):
    assert rules.unprotected_damage(cfg.attacks["ransomware"]) == 160
    assert rules.unprotected_damage(cfg.attacks["ot"]) == 320
    assert rules.unprotected_damage(cfg.attacks["exfil"]) == 140


def test_base_losses_is_the_sum_of_the_unprotected_damages(cfg):
    total = sum(rules.unprotected_damage(cfg.attacks[wave.attack_id]) for wave in cfg.waves)
    assert rules.base_losses(cfg.waves, cfg.attacks) == total == 620


def test_each_attack_lands_in_its_d24_band(cfg):
    bands = cfg.risk_matrix.bands
    landed = {attack_id: band_of(bands, rules.unprotected_damage(cfg.attacks[attack_id])).id
              for attack_id in ("exfil", "ransomware", "ot")}
    assert landed == {"exfil": "medium", "ransomware": "high", "ot": "high"}


def test_the_case_1_damage_of_every_worksheet_is_the_unprotected_damage(cfg):
    for wave in cfg.waves:
        constants = rules.worksheet_constants(cfg, wave)
        assert constants.case_1_damage_eur == 1000 * rules.unprotected_damage(cfg.attacks[wave.attack_id])


# --- validator -------------------------------------------------------------------------------------------------


def test_the_real_config_validates():
    assert _errors(_raw()) == []


def test_the_first_band_must_start_at_zero():
    raw = _mutated(lambda block: block["bands"][0].update(min=10))
    assert "risk.bands_order" in _codes(raw)


def test_equal_limits_are_rejected():
    raw = _mutated(lambda block: block["bands"][2].update(min=50))
    assert "risk.bands_order" in _codes(raw)


def test_bands_out_of_order_are_rejected():
    raw = _mutated(lambda block: block["bands"].reverse())
    assert "risk.bands_order" in _codes(raw)


def test_two_bands_are_rejected():
    raw = _mutated(lambda block: block["bands"].pop())
    assert "risk.bands_count" in _codes(raw)


def test_four_bands_are_rejected():
    raw = _mutated(lambda block: block["bands"].append({"id": "extreme", "min": 400}))
    assert "risk.bands_count" in _codes(raw)


def test_a_malformed_band_id_is_rejected():
    raw = _mutated(lambda block: block["bands"][1].update(id="Medium"))
    assert "risk.band_id" in _codes(raw)


def test_a_duplicate_band_id_is_rejected():
    raw = _mutated(lambda block: block["bands"][2].update(id="low"))
    assert "risk.band_id" in _codes(raw)


def test_unknown_keys_are_rejected():
    assert "schema.keys" in _codes(_mutated(lambda block: block.update(extra=1)))
    assert "schema.keys" in _codes(_mutated(lambda block: block["bands"][0].update(extra=1)))


def test_zero_register_rows_are_rejected():
    raw = _mutated(lambda block: block.update(register_rows=0))
    assert "schema.range" in _codes(raw)


def test_the_block_must_be_an_object():
    raw = _raw()
    raw["risk_matrix"] = []
    assert "schema.type" in _codes(raw)


def test_an_unprotected_damage_on_a_band_limit_is_rejected():
    raw = _mutated(lambda block: block["bands"][2].update(min=160))
    assert "risk.attack_band" in _codes(raw)


def test_an_unprotected_damage_in_the_lowest_band_is_rejected():
    raw = _mutated(lambda block: block["bands"][1].update(min=145))
    assert "risk.attack_band" in _codes(raw)


def test_a_highest_band_nobody_reaches_is_rejected():
    raw = _mutated(lambda block: block["bands"][2].update(min=330))
    assert "risk.attack_band" in _codes(raw)


def test_the_validator_does_not_mutate_its_input():
    raw = _raw()
    before = copy.deepcopy(raw)
    validate(raw)
    assert raw == before


# --- cheat-sheet cases (RISK-05, D-06, D-22 as clarified on 2026-11-13) ---------------------------------------------


def _case(block, case_id):
    return next(item for item in block["cases"] if item["id"] == case_id)


def test_the_real_config_carries_six_to_eight_cases(cfg):
    cases = cfg.risk_matrix.cases
    assert 6 <= len(cases) <= 8
    assert len({case.id for case in cases}) == len(cases)
    assert {case.band for case in cases} == {band.id for band in cfg.risk_matrix.bands}


def test_every_wave_attack_is_the_anchor_of_a_case(cfg):
    anchors = {case.like_attack for case in cfg.risk_matrix.cases if case.like_attack}
    assert {wave.attack_id for wave in cfg.waves} <= anchors


def test_an_anchored_case_has_the_band_of_the_attack_damage(cfg):
    bands = cfg.risk_matrix.bands
    for case in cfg.risk_matrix.cases:
        if case.like_attack:
            damage = rules.unprotected_damage(cfg.attacks[case.like_attack])
            assert case.band == band_of(bands, damage).id, case.id


def test_only_anchored_cases_are_tied_to_the_attack_damage(cfg):
    anchored = {case.id for case in cfg.risk_matrix.cases if case.like_attack}
    assert anchored == {"production_days", "production_week", "design_data"}
    for case_id in ("audit_findings", "oem_hold"):
        for band_id in ("low", "medium", "high"):
            raw = _mutated(lambda block: _case(block, case_id).update(band=band_id))
            assert "risk.case_consistency" not in _codes(raw)
    raw = _mutated(lambda block: _case(block, "design_data").update(band="high"))
    assert "risk.case_consistency" in _codes(raw)


def test_a_block_without_cases_loads_with_no_cases(tmp_path):
    raw = _raw()
    del raw["risk_matrix"]["cases"]
    assert _load(raw, tmp_path).risk_matrix.cases == ()
    assert _errors(raw) == []


def test_cases_must_be_a_list():
    assert "schema.type" in _codes(_mutated(lambda block: block.update(cases={})))


def test_an_unknown_case_key_is_rejected():
    assert "schema.keys" in _codes(_mutated(lambda block: block["cases"][0].update(extra=1)))


def test_a_malformed_or_duplicate_case_id_is_rejected():
    assert "risk.case_id" in _codes(_mutated(lambda block: block["cases"][0].update(id="Bad Id")))
    assert "risk.case_id" in _codes(_mutated(lambda block: block["cases"][1].update(id=block["cases"][0]["id"])))


def test_a_case_band_must_be_a_band_id():
    assert "risk.case_band" in _codes(_mutated(lambda block: block["cases"][0].update(band="extreme")))


def test_a_like_attack_must_be_an_attack_used_in_the_waves():
    assert "risk.case_attack" in _codes(_mutated(lambda block: _case(block, "design_data").update(like_attack="nope")))


def test_the_exfil_case_set_to_high_is_inconsistent():
    raw = _mutated(lambda block: _case(block, "design_data").update(band="high"))
    assert "risk.case_consistency" in _codes(raw)
