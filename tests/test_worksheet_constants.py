"""Derived worksheet constants come from rules.worksheet_constants, one derivation per number (PRINT-03, D-06, D-11)."""
import dataclasses
from fractions import Fraction

import pytest

from planspiel import rules
from planspiel.config import load_config
from planspiel.rules import BonusRow, RecoveryRow, WorksheetInvariantError, worksheet_constants
from tests.support import CONFIG_PATH, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SETUPS = [pytest.param(MINI, id="mini"), pytest.param(CONFIG_PATH, id="real")]


@pytest.fixture(params=SETUPS)
def cfg(request):
    return load_config(request.param)


@pytest.fixture
def real():
    return load_config(CONFIG_PATH)


def _far_below(cfg, wave):
    attack = cfg.attacks[wave.attack_id]
    cia = {"c": 0, "i": 0, "a": 0}
    return rules.apply_attack({}, cfg.measures, attack, wave, cia, cfg.ws, cfg.rs)


def _far_above(cfg, wave):
    attack = cfg.attacks[wave.attack_id]
    cia = {"c": 1000, "i": 1000, "a": 1000}
    return rules.apply_attack({}, cfg.measures, attack, wave, cia, cfg.ws, cfg.rs)


def test_values_equal_the_simulation_at_the_two_outer_cases(cfg):
    for wave in cfg.waves:
        attack = cfg.attacks[wave.attack_id]
        constants = worksheet_constants(cfg, wave)
        below, above = _far_below(cfg, wave), _far_above(cfg, wave)
        assert constants.lower == wave.e_threshold
        assert constants.reduction_cap == attack.mitigation_cap
        assert isinstance(constants.reduction_cap, int)
        assert constants.upper == constants.lower + constants.reduction_cap
        assert constants.case_1_damage_eur == below["damage"] * 1000
        assert constants.case_2_damage_eur == above["damage"] * 1000
        assert constants.kz_case_1 == below["kz_delta"]
        assert constants.kz_case_2 == above["kz_delta"]
        assert constants.unit_eur * attack.base_severity == constants.case_1_damage_eur
        assert (constants.w_c, constants.w_i, constants.w_a) == (
            wave.weights["c"], wave.weights["i"], wave.weights["a"]
        )
        assert constants.slope == (constants.kz_case_2 - constants.kz_case_1) / constants.reduction_cap


def test_real_wave_1_ransomware(real):
    constants = worksheet_constants(real, real.waves[0])
    assert (constants.w_c, constants.w_i, constants.w_a) == (Fraction(2, 5), Fraction(2, 5), Fraction(1, 5))
    assert constants.lower == 22
    assert constants.reduction_cap == 8
    assert constants.upper == 30
    assert constants.unit_eur == 20000
    assert constants.case_1_damage_eur == 160000
    assert constants.case_2_damage_eur == 0
    assert constants.kz_case_1 == -8
    assert constants.kz_case_2 == 8
    assert constants.slope == 2
    assert constants.bonus_rows == (BonusRow("M3", 2, 6), BonusRow("M4", 2, 5), BonusRow("M6", 2, 4))
    assert constants.with_recovery is True
    assert constants.recovery_measure == "M4"
    assert constants.recovery_rows == (
        RecoveryRow(0, 0), RecoveryRow(1, Fraction(1, 10)), RecoveryRow(2, Fraction(3, 10)), RecoveryRow(3, Fraction(1, 2))
    )


def test_real_wave_2_ot(real):
    constants = worksheet_constants(real, real.waves[1])
    assert constants.reduction_cap == 10
    assert constants.upper == 30
    assert constants.unit_eur == 32000
    assert constants.case_1_damage_eur == 320000
    assert constants.slope == Fraction(7, 5)
    assert constants.with_recovery is True


def test_real_wave_3_exfil_has_no_recovery(real):
    constants = worksheet_constants(real, real.waves[2])
    assert constants.reduction_cap == 7
    assert constants.upper == 31
    assert constants.slope == 2
    assert constants.with_recovery is False
    assert constants.recovery_measure is None
    assert constants.recovery_rows == ()
    assert constants.bonus_rows == (BonusRow("M1", 2, 4), BonusRow("M2", 2, 6), BonusRow("M8", 2, 3))


def test_a_wave_without_bonus_measures_has_no_bonus_rows():
    mini = load_config(MINI)
    assert worksheet_constants(mini, mini.waves[1]).bonus_rows == ()


def test_unequal_base_severity_and_cap_is_refused_naming_the_attack(real):
    attack = dataclasses.replace(real.attacks["ransomware"], base_severity=9)
    broken = dataclasses.replace(real, attacks={**real.attacks, "ransomware": attack})
    with pytest.raises(WorksheetInvariantError, match="ransomware"):
        worksheet_constants(broken, broken.waves[0])


def test_a_severity_multiplier_other_than_one_is_refused_naming_the_tier(real):
    tier = dataclasses.replace(real.budget_tiers["low"], severity_multiplier=Fraction(11, 10))
    broken = dataclasses.replace(real, budget_tiers={**real.budget_tiers, "low": tier})
    with pytest.raises(WorksheetInvariantError, match="low"):
        worksheet_constants(broken, broken.waves[0])


def test_the_error_is_a_value_error():
    assert issubclass(WorksheetInvariantError, ValueError)


def _with_recovery_on(cfg, measure_id):
    measure = cfg.measures[measure_id]
    levels = dict(measure.levels)
    levels[1] = dataclasses.replace(levels[1], recovery=Fraction(1, 10))
    return dataclasses.replace(cfg, measures={**cfg.measures, measure_id: dataclasses.replace(measure, levels=levels)})


def test_two_recovery_measures_on_a_recovery_attack_are_refused(real):
    broken = _with_recovery_on(real, "M1")
    with pytest.raises(WorksheetInvariantError, match="Recovery"):
        worksheet_constants(broken, broken.waves[0])


def test_two_recovery_measures_do_not_matter_for_an_attack_without_recovery(real):
    broken = _with_recovery_on(real, "M1")
    constants = worksheet_constants(broken, broken.waves[2])
    assert constants.with_recovery is False
    assert constants.recovery_rows == ()
