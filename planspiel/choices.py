"""BAL-06 (D-16): "Jede Entscheidung zählt" - dominierte Level, fast zwingende und überstarke Maßnahmen.

Alle Kennzahlen sind reine Funktionen über Spalten des Ergebnisspeichers (statische Schicht, D-05) und lesen nie
Formel-Operanden. Das 4^n-Gitter `kz_grid` hält die End-KZ jedes gültigen Plans im Budget (-1 sonst); der Zustandsindex
ist der Basis-4-Code mit Maßnahme 0 an höchster Stelle (Schrittweite von Maßnahme j: 4 ** (n - 1 - j)).

Die Schwellen sind Vorschläge aus der Recherche (Q7) und werden am Checkpoint D-04 zur Abnahme vorgelegt.
"""
import heapq
from array import array
from fractions import Fraction
from itertools import combinations
from typing import Dict, Iterable, List, Optional, Tuple

from planspiel.gate import LEVELS

BAND_KZ = 5
BAND_MIN_SIZE = 200
NEAR_MANDATORY_SHARE = Fraction(9, 10)
OVERPOWERED_DROP = 10
DECISION_SHIFT_KZ = 3
DECISION_SHARE = Fraction(1, 2)
TIER_JACCARD_MAX = Fraction(1, 2)
WINDOW_SAMPLE_STRIDE = 97


def kz_grid(n_measures: int, code_index, kz_final, over_budget) -> array:
    """Gitter der Länge 4^n: End-KZ jedes gültigen Plans im Budget, -1 für ungültige und überzogene Pläne."""
    grid = array("h", [-1]) * LEVELS**n_measures
    for code, kz, over in zip(code_index, kz_final, over_budget):
        if not over:
            grid[code] = kz
    return grid


def _level_slices(grid: array, n_measures: int, measure: int):
    """Erzeugt die vier Level-Scheiben der Maßnahme: je Kontext (übrige Stellen fest) die Werte der Level 0 bis 3."""
    stride = LEVELS ** (n_measures - 1 - measure)
    for block in range(0, len(grid), LEVELS * stride):
        yield zip(*(grid[block + level * stride : block + (level + 1) * stride] for level in range(LEVELS)))


def level_improvement_shares(grid: array, n_measures: int) -> Dict[Tuple[int, int], Optional[Fraction]]:
    """Je (Maßnahme, Level >= 1): Anteil der Kontexte im Budget, in denen das Level strikt besser endet als das
    beste tiefere Level derselben Maßnahme. Ohne Kontext None (wird berichtet, ist kein Fehler)."""
    shares: Dict[Tuple[int, int], Optional[Fraction]] = {}
    for measure in range(n_measures):
        contexts = [0] * LEVELS
        improved = [0] * LEVELS
        for slices in _level_slices(grid, n_measures, measure):
            for values in slices:
                lower_best = values[0]
                for level in range(1, LEVELS):
                    value = values[level]
                    if value >= 0 and lower_best >= 0:
                        contexts[level] += 1
                        if value > lower_best:
                            improved[level] += 1
                    if value > lower_best:
                        lower_best = value
        for level in range(1, LEVELS):
            shares[(measure, level)] = Fraction(improved[level], contexts[level]) if contexts[level] else None
    return shares


def strictly_dominated(shares: Dict[Tuple[int, int], Optional[Fraction]]) -> List[Tuple[int, int]]:
    return sorted(key for key, share in shares.items() if share is not None and share == 0)


def level_swing_shares(grid: array, n_measures: int, shift: int = DECISION_SHIFT_KZ) -> Dict[int, Optional[Fraction]]:
    """Je Maßnahme: Anteil der Kontexte mit mindestens zwei Leveln im Budget, in denen sich die End-KZ der Level um
    mindestens `shift` unterscheidet (größter minus kleinster Wert)."""
    swings: Dict[int, Optional[Fraction]] = {}
    for measure in range(n_measures):
        contexts = hits = 0
        for slices in _level_slices(grid, n_measures, measure):
            for values in slices:
                valid = [value for value in values if value >= 0]
                if len(valid) >= 2:
                    contexts += 1
                    if max(valid) - min(valid) >= shift:
                        hits += 1
        swings[measure] = Fraction(hits, contexts) if contexts else None
    return swings


def near_optimal_band(
    code_index, kz_final, own_cost, over_budget, band: int = BAND_KZ, min_size: int = BAND_MIN_SIZE
) -> List[int]:
    """Alle Pläne im Budget mit End-KZ >= Bestwert - band; sind es weniger als `min_size`, die `min_size` besten.
    Sortierung (-KZ, eigene Kosten, Code); ohne Plan im Budget leer."""
    best = -1
    for kz, over in zip(kz_final, over_budget):
        if not over and kz > best:
            best = kz
    if best < 0:
        return []
    rows = (
        (-kz, own, code)
        for code, kz, own, over in zip(code_index, kz_final, own_cost, over_budget)
        if not over
    )
    within = sorted(row for row in rows if -row[0] >= best - band)
    if len(within) < min_size:
        rows = (
            (-kz, own, code)
            for code, kz, own, over in zip(code_index, kz_final, own_cost, over_budget)
            if not over
        )
        within = heapq.nsmallest(min_size, rows)
    return [row[2] for row in within]


def band_shares(codes: Iterable[int], n_measures: int) -> Dict[int, Tuple[Fraction, Fraction]]:
    """Je Maßnahme: (Anteil Level >= 1, Anteil Level >= 2) über die Pläne des Bands."""
    codes = list(codes)
    if not codes:
        raise ValueError("Das Band enthält keinen Plan")
    shares = {}
    for measure in range(n_measures):
        stride = LEVELS ** (n_measures - 1 - measure)
        levels = [(code // stride) % LEVELS for code in codes]
        shares[measure] = (
            Fraction(sum(level >= 1 for level in levels), len(codes)),
            Fraction(sum(level >= 2 for level in levels), len(codes)),
        )
    return shares


def near_mandatory(shares: Dict[int, Tuple[Fraction, Fraction]], threshold: Fraction = NEAR_MANDATORY_SHARE) -> List[int]:
    return [measure for measure, (present, _high) in sorted(shares.items()) if present > threshold]


def removal_drops(grid: array, n_measures: int) -> Dict[int, int]:
    """Je Maßnahme: bestes End-KZ des Tiers im Budget minus bestes End-KZ im Budget, wenn die Maßnahme auf Level 0
    gezwungen wird (-1 zählt als Wert, falls ohne die Maßnahme kein Plan im Budget bleibt)."""
    best = max(grid)
    drops = {}
    for measure in range(n_measures):
        stride = LEVELS ** (n_measures - 1 - measure)
        without = max(max(grid[block : block + stride]) for block in range(0, len(grid), LEVELS * stride))
        drops[measure] = best - without
    return drops


def tier_band_jaccard(bands_by_tier: Dict[str, Iterable[int]]) -> Dict[Tuple[str, str], Fraction]:
    sets = {tier: set(codes) for tier, codes in bands_by_tier.items()}
    result = {}
    for first, second in combinations(sets, 2):
        union = sets[first] | sets[second]
        result[(first, second)] = Fraction(len(sets[first] & sets[second]), len(union)) if union else Fraction(0)
    return result
