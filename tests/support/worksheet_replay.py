"""Independent replay of the printed attack worksheet steps (PRINT-04, D-10, D-11).

This module is the one deliberate second encoding of the hand calculation: it reads only the exact fields of an
AttackSheet (the numbers printed on the sheet) and never imports or calls planspiel.rules or planspiel.rounding.
The equivalence tests compare it with the simulation. If a comparison fails, the model or the rules are wrong,
never the replay.

Printed step order: E-value, bonus, total reduction = E + bonus, cap line (threshold + cap = upper limit),
case 1 / case 2 / case 3, recovery, wave KZ change = attack KZ + event KZ rounded half away from zero.
"""
import math
from fractions import Fraction
from typing import Mapping, NamedTuple, Sequence

from planspiel.config import Config
from planspiel.printmodel import AttackSheet

# Keys returned by the simulation's attack step, grouped by how the sheet carries them (D-21).
REPLAYED_KEYS = {"e_value", "bonus_reduction", "gesamtreduktion", "damage", "kz_delta", "recovery_factor"}
# Intermediates implied by the printed case formulas; they are checked through damage and KZ.
DERIVED_NOT_PRINTED_KEYS = {"capped_reduction", "severity", "effective_base_severity"}
# Computed by the simulation but feeding no score and not printed.
UNPRINTED_UNSCORED_KEYS = {"cia_delta"}


class SheetResult(NamedTuple):
    e_value: Fraction
    total_bonus: int
    gr: Fraction
    case: int
    damage_before_eur: Fraction
    damage_eur: Fraction
    kz_attack: Fraction
    change: int


def paper_round(value) -> int:
    """Round half away from zero (a half is rounded up in absolute value), as taught on the sheet."""
    exact = Fraction(value)
    magnitude = math.floor(abs(exact) + Fraction(1, 2))
    return -magnitude if exact < 0 else magnitude


def replay_e_value(sheet: AttackSheet, cia: Sequence) -> Fraction:
    """Step 1: E-value = C x w_C + I x w_I + A x w_A from the team's CIA totals."""
    c, i, a = cia
    return Fraction(c) * sheet.w_c + Fraction(i) * sheet.w_i + Fraction(a) * sheet.w_a


def replay_bonus(sheet: AttackSheet, levels: Mapping[str, int]) -> int:
    """Step 2: sum of the printed bonus points of every row whose measure reaches the printed level."""
    return sum(row.points for row in sheet.bonus_rows if levels.get(row.measure, 0) >= row.min_level)


def replay_steps(sheet: AttackSheet, e_value: Fraction, levels: Mapping[str, int], event_kz) -> SheetResult:
    """Steps 3 to 7 in printed order for a given E-value, measure levels and event KZ."""
    assert sheet.lower + sheet.reduction_cap == sheet.upper, (
        f"wave {sheet.wave_id}: printed cap line is wrong: {sheet.lower} + {sheet.reduction_cap} != {sheet.upper}"
    )
    total_bonus = replay_bonus(sheet, levels)
    gr = Fraction(e_value) + total_bonus

    if gr <= sheet.lower:
        case = 1
        damage_before = Fraction(sheet.case_1_damage_eur)
        kz_attack = Fraction(sheet.kz_case_1)
    elif gr >= sheet.upper:
        case = 2
        damage_before = Fraction(sheet.case_2_damage_eur)
        kz_attack = Fraction(sheet.kz_case_2)
    else:
        case = 3
        damage_before = (sheet.upper - gr) * sheet.unit_eur
        kz_attack = Fraction(sheet.kz_case_1) + (gr - sheet.lower) * sheet.slope

    factor = Fraction(0)
    if sheet.with_recovery:
        table = {row.level: row.factor for row in sheet.recovery_rows}
        factor = Fraction(table[levels.get(sheet.recovery_measure, 0)])
    damage = damage_before * (1 - factor)

    change = paper_round(kz_attack + Fraction(event_kz))
    return SheetResult(Fraction(e_value), total_bonus, gr, case, damage_before, damage, kz_attack, change)


def replay_wave(sheet: AttackSheet, cia: Sequence, levels: Mapping[str, int], event_kz) -> SheetResult:
    """The whole sheet: E-value step from the CIA totals, then steps 3 to 7."""
    return replay_steps(sheet, replay_e_value(sheet, cia), levels, event_kz)


def event_kz_bounds(cfg: Config, wave_id: int) -> range:
    """Integer range that contains every KZ sum the wave's events can produce (sum of per-event extrema)."""
    low = 0
    high = 0
    for event in cfg.events.get(wave_id, []):
        params = event.params
        if event.type in ("kurswechsel", "flat_budget", "opex_discount_per_active_measure"):
            values = [0]
        elif event.type == "checklist_tier":
            values = [kz for _, kz in params["tiers"]]
        elif event.type == "measure_level_tier":
            values = list(params["tiers"].values())
        elif event.type == "level_bonus_per_measure":
            values = [0, len(cfg.measures) * params["kz_per_measure"]]
        elif event.type == "and_condition":
            values = [0, params["kz_delta"]]
        else:
            raise ValueError(f"unknown event type '{event.type}' in wave {wave_id}: the replay cannot bound its KZ")
        low += min(values)
        high += max(values)
    return range(int(low), int(high) + 1)
