"""The Welle 0 practice view: a throw-away Config in which the practice attack is the only wave (FLOW-01, D-12).

Nothing outside this module reads `cfg.practice`. The view reuses `rules` unchanged, so every printed practice number
comes from the same primitives as the real waves; the real `cfg.waves`, `cfg.attacks` and `cfg.events` never see the
block, which keeps the enumeration, the gate and the digests of waves 1-3 identical.

`check_example` proves that the fixed example selection teaches what Welle 0 is for (D-13, D-15): Fall 3, one bonus met
and one missed, recovery, a wave KZ change that is an exact half before rounding, and a clamp that acts.
"""
import dataclasses
from fractions import Fraction

from planspiel.config import BudgetTier, Config
from planspiel.printmodel import MIN_HALF_DISTANCE, PrintModelError, min_half_distance
from planspiel.rules import (
    KZ_MAX,
    KZ_MIN,
    Path,
    PathError,
    PathTrace,
    WorksheetInvariantError,
    path_trace,
    worksheet_constants,
)

PRACTICE_JOB = "uebung-welle-0"
PRACTICE_TIER = "practice"
PRACTICE_ATTACK = "practice"
PREFIX = "Übung"


def practice_config(cfg: Config) -> Config:
    """The config in which the practice wave (id 0) is the only wave and `practice` the only budget tier."""
    block = cfg.practice
    if block is None:
        raise PrintModelError(f"{PREFIX}: Die Konfiguration enthält keinen Block 'practice'.")
    tier = BudgetTier(PRACTICE_TIER, block.budget, block.kz_start, Fraction(1))
    return dataclasses.replace(
        cfg,
        default_budget_tier=PRACTICE_TIER,
        attacks={**cfg.attacks, PRACTICE_ATTACK: block.attack},
        waves=[block.wave],
        events={block.wave.wave_id: [block.event]},
        final_events=[],
        budget_tiers={PRACTICE_TIER: tier},
        practice=None,
    )


def check_example(cfg: Config) -> PathTrace:
    """Trace of the example selection on the practice view; PrintModelError unless it teaches the Welle 0 mechanics."""
    view = practice_config(cfg)
    wave_config = view.waves[0]
    try:
        constants = worksheet_constants(view, wave_config)
    except WorksheetInvariantError as error:
        raise PrintModelError(f"{PREFIX}: {error}") from error
    distance = min_half_distance(view, constants)
    if distance is not None and distance < MIN_HALF_DISTANCE:
        raise PrintModelError(
            f"{PREFIX}: Zwei Nachkommastellen genügen für die KZ-Berechnung nicht, ein Wert liegt nur {distance} "
            f"neben einem halben Punkt (Grenze {MIN_HALF_DISTANCE}); die Rundung könnte kippen (D-09)."
        )

    try:
        trace = path_trace(view, PRACTICE_TIER, Path(start=dict(cfg.practice.selection)))
    except PathError as error:
        raise PrintModelError(f"{PREFIX}: Die Beispielauswahl ist nicht zulässig ({error}).") from error

    wave = trace.waves[0]
    if trace.review.own_spend_k > cfg.practice.budget:
        raise PrintModelError(
            f"{PREFIX}: Init und OPEX der Beispielauswahl ({trace.review.own_spend_k}) übersteigen das Budget "
            f"({cfg.practice.budget})."
        )
    if wave.case != 3:
        raise PrintModelError(f"{PREFIX}: Die Beispielauswahl muss in Fall 3 landen, sie landet in Fall {wave.case}.")
    if len(wave.bonus_met) != 1 or not wave.bonus_missed:
        raise PrintModelError(
            f"{PREFIX}: Es muss genau eine Bonus-Maßnahme erfüllt und mindestens eine verfehlt sein "
            f"(erfüllt: {len(wave.bonus_met)}, verfehlt: {len(wave.bonus_missed)})."
        )
    if wave.recovery_factor <= 0:
        raise PrintModelError(f"{PREFIX}: Die Beispielauswahl muss Recovery auslösen (Faktor größer als 0).")
    if wave.kz_change_exact.denominator == 1:
        raise PrintModelError(
            f"{PREFIX}: Die KZ-Änderung vor dem Runden ({wave.kz_change_exact}) ist ganzzahlig, es gäbe nichts zu runden."
        )
    if wave.kz_change_exact.denominator != 2:
        raise PrintModelError(
            f"{PREFIX}: Die KZ-Änderung vor dem Runden ({wave.kz_change_exact}) muss genau auf einem halben Punkt liegen, "
            "damit das Runden ab ,5 sichtbar wird."
        )
    if KZ_MIN <= wave.kz_unclamped <= KZ_MAX:
        raise PrintModelError(
            f"{PREFIX}: Die Begrenzung auf {KZ_MIN} bis {KZ_MAX} muss wirken, die KZ landet bei {wave.kz_unclamped}."
        )
    return trace
