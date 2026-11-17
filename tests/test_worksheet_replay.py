"""Worksheet replay helpers and the apply_attack key guard (PRINT-04, D-11, D-21)."""
import ast
import dataclasses
from fractions import Fraction

import pytest

from planspiel import rules
from planspiel.config import load_config
from planspiel.printmodel import build_attack_sheets
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT
from tests.support.worksheet_replay import (
    DERIVED_NOT_PRINTED_KEYS,
    REPLAYED_KEYS,
    UNPRINTED_UNSCORED_KEYS,
    event_kz_bounds,
    paper_round,
    replay_bonus,
    replay_e_value,
    replay_steps,
    replay_wave,
)

REPLAY_FILE = REPO_ROOT / "tests" / "support" / "worksheet_replay.py"


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, build_attack_sheets(cfg, texts)


@pytest.mark.parametrize(
    "value, expected",
    [
        (Fraction(5, 2), 3),
        (Fraction(-5, 2), -3),
        (Fraction(249, 100), 2),
        (Fraction(-249, 100), -2),
        (Fraction(0), 0),
        (Fraction(7, 2), 4),
        (Fraction(-7, 2), -4),
        (Fraction(1, 2), 1),
        (Fraction(-1, 2), -1),
        (Fraction(49, 100), 0),
    ],
)
def test_paper_round_is_half_away_from_zero(value, expected):
    assert paper_round(value) == expected


def test_paper_round_accepts_integers():
    assert paper_round(3) == 3
    assert paper_round(-4) == -4


def test_wave_one_case_three_without_recovery(real):
    _, sheets = real
    result = replay_steps(sheets[0], Fraction(20), {"M3": 2, "M4": 0, "M6": 0}, 0)
    assert result.total_bonus == 6
    assert result.gr == 26
    assert result.case == 3
    assert result.damage_before_eur == 80_000
    assert result.damage_eur == 80_000
    assert result.kz_attack == 0
    assert result.change == 0


def test_wave_one_case_two_with_strong_recovery_level(real):
    _, sheets = real
    result = replay_steps(sheets[0], Fraction(20), {"M3": 2, "M4": 3, "M6": 0}, 0)
    assert result.total_bonus == 11
    assert result.gr == 31
    assert result.case == 2
    assert result.damage_eur == 0
    assert result.kz_attack == 8
    assert result.change == 8


def test_wave_one_case_one_with_recovery_discount(real):
    _, sheets = real
    result = replay_steps(sheets[0], Fraction(15), {"M3": 0, "M4": 1, "M6": 0}, 0)
    assert result.gr == 15
    assert result.case == 1
    assert result.damage_before_eur == 160_000
    assert result.damage_eur == 144_000
    assert result.kz_attack == -8
    assert result.change == -8


def test_bounds_of_case_three_belong_to_case_one_and_two(real):
    _, sheets = real
    sheet = sheets[0]
    at_lower = replay_steps(sheet, Fraction(sheet.lower), {}, 0)
    at_upper = replay_steps(sheet, Fraction(sheet.upper), {}, 0)
    assert at_lower.case == 1
    assert at_upper.case == 2


def test_case_three_event_kz_is_added_before_rounding(real):
    _, sheets = real
    # GR 26 gives KZ attack 0; with events +3 the change is 3, with GR 23.25 (KZ -5.5) and +0 it rounds to -6.
    assert replay_steps(sheets[0], Fraction(26), {}, 3).change == 3
    assert replay_steps(sheets[0], Fraction(2325, 100), {}, 0).change == -6


def test_cap_line_arithmetic_is_checked_first(real):
    _, sheets = real
    broken = dataclasses.replace(sheets[0], reduction_cap=sheets[0].reduction_cap + 1)
    with pytest.raises(AssertionError, match="1"):
        replay_steps(broken, Fraction(20), {}, 0)


def test_replay_e_value_is_weighted_sum(real):
    _, sheets = real
    sheet = sheets[0]
    assert replay_e_value(sheet, (10, 5, 5)) == Fraction(10) * sheet.w_c + 5 * sheet.w_i + 5 * sheet.w_a
    assert isinstance(replay_e_value(sheet, (1, 1, 1)), Fraction)


def test_replay_bonus_counts_rows_reached_by_the_level(real):
    _, sheets = real
    sheet = sheets[0]
    assert replay_bonus(sheet, {}) == 0
    assert replay_bonus(sheet, {"M3": 1}) == 0
    assert replay_bonus(sheet, {"M3": 2}) == 6
    assert replay_bonus(sheet, {"M3": 3, "M4": 2, "M6": 3}) == 15


def test_replay_wave_is_e_step_plus_steps(real):
    _, sheets = real
    sheet = sheets[0]
    cia = (30, 20, 10)
    levels = {"M3": 2, "M4": 1, "M6": 2}
    expected = replay_steps(sheet, replay_e_value(sheet, cia), levels, 4)
    assert replay_wave(sheet, cia, levels, 4) == expected


def test_event_kz_bounds_on_the_real_config(real):
    cfg, _ = real
    assert event_kz_bounds(cfg, 1) == range(0, 1)
    assert event_kz_bounds(cfg, 2) == range(-5, 8)
    assert event_kz_bounds(cfg, 3) == range(-6, 31)


def test_event_kz_bounds_rejects_unknown_event_types(real):
    cfg, _ = real
    event = dataclasses.replace(cfg.events[2][0], type="mystery_event", params={})
    patched = dataclasses.replace(cfg, events={**cfg.events, 2: [event]})
    with pytest.raises(ValueError, match="mystery_event"):
        event_kz_bounds(patched, 2)


def test_apply_attack_returns_exactly_the_known_keys(real):
    cfg, _ = real
    wave = cfg.waves[0]
    attack = cfg.attacks[wave.attack_id]
    selection = {"M3": 2, "M4": 1}
    cia = rules.compute_cia(selection, cfg.measures, cfg.base_cia)
    result = rules.apply_attack(selection, cfg.measures, attack, wave, cia, cfg.ws, cfg.rs)
    assert set(result) == REPLAYED_KEYS | DERIVED_NOT_PRINTED_KEYS | UNPRINTED_UNSCORED_KEYS


def test_key_sets_are_disjoint_and_cia_delta_is_named_unscored():
    assert UNPRINTED_UNSCORED_KEYS == {"cia_delta"}
    assert not REPLAYED_KEYS & DERIVED_NOT_PRINTED_KEYS
    assert not REPLAYED_KEYS & UNPRINTED_UNSCORED_KEYS
    assert not DERIVED_NOT_PRINTED_KEYS & UNPRINTED_UNSCORED_KEYS


def test_replay_imports_neither_rules_nor_rounding():
    tree = ast.parse(REPLAY_FILE.read_text(encoding="utf-8"), filename=str(REPLAY_FILE))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported.append(module)
            imported.extend(f"{module}.{alias.name}" for alias in node.names)
    forbidden = [name for name in imported if name in {"planspiel.rules", "planspiel.rounding"}]
    assert forbidden == []
    assert not any(name.startswith(("planspiel.rules.", "planspiel.rounding.")) for name in imported)
