"""The printed worksheet steps equal the simulation over the dense synthetic grid (PRINT-04, D-09 to D-12, D-21).

The simulation side lives only here: every comparison drives rules.apply_attack and rules.wave_kz_change and
compares with tests/support/worksheet_replay.py, which reads nothing but the exact AttackSheet fields.
"""
import itertools
import math
from fractions import Fraction

import pytest

from planspiel import rules
from planspiel.config import load_config
from planspiel.printmodel import build_attack_sheets
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT
from tests.support.worksheet_replay import (
    event_kz_bounds,
    paper_round,
    replay_bonus,
    replay_e_value,
    replay_recovery_factor,
    replay_steps,
)

MINI_CONFIG = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
MAX_MISMATCHES = 50
MIN_REAL_POINTS = 10_000
MARGIN = 3
LEVELS = (0, 1, 2, 3)


class Setup:
    def __init__(self, name, config_path, content_dir):
        self.name = name
        self.cfg = load_config(config_path)
        self.texts = load_texts(content_dir / "texte.toml")
        self.sheets = build_attack_sheets(self.cfg, self.texts)


@pytest.fixture(scope="module", params=["real", "mini"])
def setup(request):
    """Sheets are built here, before any test patches the rules module."""
    if request.param == "real":
        return Setup("real", CONFIG_PATH, CONTENT_DIR)
    return Setup("mini", MINI_CONFIG, MINI_CONTENT_DIR)


@pytest.fixture(scope="module")
def real():
    return Setup("real", CONFIG_PATH, CONTENT_DIR)


def _lattice(sheet, ws):
    """Every Gesamtreduktion on the 1/ws lattice from MARGIN below Fall 1 to MARGIN above Fall 2, bounds included."""
    return [Fraction(step, ws) for step in range((sheet.lower - MARGIN) * ws, (sheet.upper + MARGIN) * ws + 1)]


def _varied_measures(cfg, sheet):
    ids = [row.measure for row in sheet.bonus_rows]
    if sheet.recovery_measure is not None and sheet.recovery_measure not in ids:
        ids.append(sheet.recovery_measure)
    return ids


def _grid_mismatches(cfg, sheets, *, waves=None):
    """Compare replay and simulation at every grid point; return (mismatch lines capped at 50, points checked)."""
    found = []
    points = 0

    def note(text):
        if len(found) < MAX_MISMATCHES:
            found.append(text)

    for wave, sheet in zip(cfg.waves, sheets):
        if waves is not None and wave.wave_id not in waves:
            continue
        attack = cfg.attacks[wave.attack_id]
        # The E-value is placed on the first non-zero weight so that Gesamtreduktion can be set exactly.
        carrier = next(key for key in ("c", "i", "a") if wave.weights[key] != 0)
        axes = [sorted(cfg.measures[measure].levels) for measure in _varied_measures(cfg, sheet)]
        names = _varied_measures(cfg, sheet)
        pairs = {}
        for combination in itertools.product(*axes):
            levels = dict(zip(names, combination))
            bonus = replay_bonus(sheet, levels)
            for gr in _lattice(sheet, cfg.ws):
                e_value = gr - bonus
                cia = {"c": Fraction(0), "i": Fraction(0), "a": Fraction(0)}
                cia[carrier] = e_value / wave.weights[carrier]
                sim = rules.apply_attack(levels, cfg.measures, attack, wave, cia, cfg.ws, cfg.rs)
                replay = replay_steps(sheet, e_value, levels, 0)
                points += 1
                checks = {
                    "e_value": (replay.e_value, sim["e_value"]),
                    "bonus_reduction": (replay.total_bonus, sim["bonus_reduction"]),
                    "gesamtreduktion": (replay.gr, sim["gesamtreduktion"]),
                    "damage": (replay.damage_eur, sim["damage"] * 1000),
                    "recovery_factor": (replay_recovery_factor(sheet, levels), sim["recovery_factor"]),
                    "kz_delta": (replay.kz_attack, sim["kz_delta"]),
                }
                for field, (replayed, simulated) in checks.items():
                    if replayed != simulated:
                        note(
                            f"wave {wave.wave_id} GR {gr} levels {levels} {field}: "
                            f"replay {replayed} != simulation {simulated}"
                        )
                pairs.setdefault((sim["kz_delta"], replay.kz_attack), (e_value, levels))
        # The wave KZ change depends only on (KZ attack, KZ events): sweep the whole event range once per distinct KZ.
        for (sim_kz, _), (e_value, levels) in pairs.items():
            for event_kz in event_kz_bounds(cfg, wave.wave_id):
                points += 1
                replayed = replay_steps(sheet, e_value, levels, event_kz).change
                simulated = rules.wave_kz_change(sim_kz, event_kz)
                if replayed != simulated:
                    note(
                        f"wave {wave.wave_id} GR {replay_steps(sheet, e_value, levels, 0).gr} levels {levels} "
                        f"event KZ {event_kz} change: replay {replayed} != simulation {simulated}"
                    )
    return found, points


def test_grid_lattice_includes_both_bounds_exactly(setup):
    cfg = setup.cfg
    for sheet in setup.sheets:
        lattice = _lattice(sheet, cfg.ws)
        assert Fraction(sheet.lower) in lattice and Fraction(sheet.upper) in lattice
        assert lattice[0] == sheet.lower - MARGIN and lattice[-1] == sheet.upper + MARGIN
        assert {b - a for a, b in zip(lattice, lattice[1:])} == {Fraction(1, cfg.ws)}


def test_dense_grid_equals_the_simulation(setup):
    mismatches, points = _grid_mismatches(setup.cfg, setup.sheets)
    assert mismatches == []
    if setup.name == "real":
        assert points > MIN_REAL_POINTS


def test_e_step_equals_e_value_scaled_for_every_reachable_cia_triple(setup):
    cfg = setup.cfg
    reachable = {(cfg.base_cia["c"], cfg.base_cia["i"], cfg.base_cia["a"])}
    for measure in cfg.measures.values():
        reachable = {
            (c + level.cia["c"], i + level.cia["i"], a + level.cia["a"])
            for (c, i, a) in reachable
            for level in measure.levels.values()
        }
    assert len(reachable) > 100
    for wave, sheet in zip(cfg.waves, setup.sheets):
        for c, i, a in reachable:
            scaled = rules.e_value_scaled({"c": c, "i": i, "a": a}, wave.weights, cfg.ws)
            assert replay_e_value(sheet, (c, i, a)) == Fraction(scaled, cfg.ws)


def test_printed_bonus_rule_equals_compute_bonus_reduction(setup):
    cfg = setup.cfg
    for wave, sheet in zip(cfg.waves, setup.sheets):
        assert [(row.measure, row.min_level, row.points) for row in sheet.bonus_rows] == [
            (bm.measure, bm.min_level, bm.bonus) for bm in wave.bonus_measures
        ]
        measures = [bm.measure for bm in wave.bonus_measures]
        for combination in itertools.product(LEVELS, repeat=len(measures)):
            levels = dict(zip(measures, combination))
            assert replay_bonus(sheet, levels) == rules.compute_bonus_reduction(wave, levels)


def test_negative_control_recovery_mutation_is_detected(real, monkeypatch):
    original = rules.compute_recovery
    monkeypatch.setattr(
        rules, "compute_recovery", lambda selection, measures: original(selection, measures) + Fraction(1, 10)
    )
    mismatches, _ = _grid_mismatches(real.cfg, real.sheets)
    assert mismatches
    assert any("recovery_factor" in line or "damage" in line for line in mismatches)


def test_negative_control_attack_kz_mutation_is_detected(real, monkeypatch):
    original = rules.attack_kz_delta
    monkeypatch.setattr(rules, "attack_kz_delta", lambda *args, **kwargs: original(*args, **kwargs) + 1)
    mismatches, _ = _grid_mismatches(real.cfg, real.sheets)
    assert mismatches
    assert any("kz_delta" in line for line in mismatches)


def test_negative_control_bonus_mutation_is_detected(real, monkeypatch):
    original = rules.compute_bonus_reduction
    monkeypatch.setattr(rules, "compute_bonus_reduction", lambda wave, selection: original(wave, selection) + 1)
    mismatches, _ = _grid_mismatches(real.cfg, real.sheets)
    assert mismatches
    assert any("bonus_reduction" in line or "gesamtreduktion" in line for line in mismatches)


def test_negative_control_rounding_mutation_is_detected(real, monkeypatch):
    original = rules.wave_kz_change
    monkeypatch.setattr(rules, "wave_kz_change", lambda kz, event: original(kz, event) + 1)
    mismatches, _ = _grid_mismatches(real.cfg, real.sheets)
    assert any("change" in line for line in mismatches)


def _trunc_two(value):
    magnitude = Fraction(math.floor(abs(value) * 100), 100)
    return -magnitude if value < 0 else magnitude


def _round_two(value):
    magnitude = Fraction(math.floor(abs(value) * 100 + Fraction(1, 2)), 100)
    return -magnitude if value < 0 else magnitude


def test_two_decimals_never_change_the_rounded_wave_change(setup):
    cfg = setup.cfg
    for wave, sheet in zip(cfg.waves, setup.sheets):
        events = event_kz_bounds(cfg, wave.wave_id)
        for step in range(1, (sheet.upper - sheet.lower) * cfg.ws):
            kz = Fraction(sheet.kz_case_1) + Fraction(step, cfg.ws) * sheet.slope
            for event_kz in events:
                exact = paper_round(kz + event_kz)
                assert paper_round(_trunc_two(kz) + event_kz) == exact, (wave.wave_id, step, event_kz, "cut off")
                assert paper_round(_round_two(kz) + event_kz) == exact, (wave.wave_id, step, event_kz, "rounded")


def _terminates(slope):
    denominator = Fraction(slope).denominator
    for prime in (2, 5):
        while denominator % prime == 0:
            denominator //= prime
    return denominator == 1


def test_sheet_with_a_fraction_slope_carries_the_fraction_hint(setup):
    fraction_hint = setup.texts.get("sheets.angriff.kz_fraction_hint")
    decimals_hint = setup.texts.get("sheets.angriff.kz_decimals_hint")
    for sheet in setup.sheets:
        assert sheet.kz_hint == (decimals_hint if _terminates(sheet.slope) else fraction_hint)
