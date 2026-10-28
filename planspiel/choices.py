"""BAL-06 (D-16): "Jede Entscheidung zählt" - dominierte Level, fast zwingende und überstarke Maßnahmen sowie die
messbare Wirkung der Entscheidungspunkte (Budget-Tier, Maßnahmen-/Levelwahl, Change-Fenster, Kurswechsel).

Alle Kennzahlen sind reine Funktionen über Spalten des Ergebnisspeichers, die Start-Aggregate der Tausch-Schicht und
`rules.TierTables` und lesen nie Formel-Operanden (D-05: Dominanz, Band und Wegfall-Abfall auf der statischen Schicht,
Change-Fenster und Kurswechsel auf der Tausch-Schicht und den Zugpfaden). Das 4^n-Gitter `kz_grid` hält die End-KZ
jedes gültigen Plans im Budget (-1 sonst); der Zustandsindex ist der Basis-4-Code mit Maßnahme 0 an höchster Stelle
(Schrittweite von Maßnahme j: 4 ** (n - 1 - j)).

Die Schwellen sind Vorschläge aus der Recherche (Q7) und werden am Checkpoint D-04 zur Abnahme vorgelegt.
"""
import heapq
from array import array
from fractions import Fraction
from itertools import combinations
from typing import Callable, Dict, Iterable, List, NamedTuple, Optional, Tuple

from planspiel.enumerate import code_from_index
from planspiel.fmt import format_approx
from planspiel.gate import LEVELS
from planspiel.report import nearest_rank

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


class KurswechselSpread(NamedTuple):
    share: Optional[Fraction]
    median: Optional[int]
    p90: Optional[int]
    starts: int


class WindowMoveEffect(NamedTuple):
    share: Optional[Fraction]
    mean: Optional[Fraction]
    maximum: Optional[int]
    sample: int


def kurswechsel_spread(starts: Dict, shift: int = DECISION_SHIFT_KZ) -> KurswechselSpread:
    """Je Start mit mindestens zwei Tauschpfaden im Budget: bestes minus schlechtestes End-KZ der Pfade. Ergebnis:
    Anteil der Starts mit Spanne >= shift, Median, 90. Perzentil (Nearest-Rank) und Zahl der Starts."""
    spreads = sorted(
        best - worst
        for best, worst, paths in zip(starts["best_in_budget"], starts["worst_in_budget"], starts["in_budget_paths"])
        if paths >= 2
    )
    if not spreads:
        return KurswechselSpread(None, None, None, 0)
    return KurswechselSpread(
        Fraction(sum(spread >= shift for spread in spreads), len(spreads)),
        nearest_rank(spreads, 50),
        nearest_rank(spreads, 90),
        len(spreads),
    )


def window_move_effect(
    tables, sample_stride: int = WINDOW_SAMPLE_STRIDE, shift: int = DECISION_SHIFT_KZ
) -> WindowMoveEffect:
    """Wirkung des Change-Fensters nach Welle 2: für jeden Tauschpfad im Budget (Stichprobe: Starts mit Index durch
    `sample_stride` teilbar) der beste einzelne Zug dort, der im Budget bleibt (Welle 1 Start, Welle 2 Ende des Tauschs,
    Welle 3 Ziel; Kosten = Tauschkosten + Zugkosten). Verbesserung = bester End-KZ-Gewinn, mindestens 0 (kein Zug).
    Ergebnis: Anteil mit Verbesserung >= shift, mittlere und größte Verbesserung, Stichprobengröße."""
    if tables.wave_count != 3 or tables.prefix_waves != 1:
        raise ValueError("window_move_effect modelliert drei Wellen mit dem Kurswechsel nach Welle 1")
    sample = hits = total = maximum = 0
    for start, end, _dropped, _incoming, _level, cost in tables.swap_paths(start_stride=sample_stride):
        base = tables.path_outcome((start, end, end), cost)
        if base.over_budget:
            continue
        best = base.kz_final
        for target, move_cost in tables.single_moves(end):
            moved = tables.path_outcome((start, end, target), cost + move_cost)
            if not moved.over_budget and moved.kz_final > best:
                best = moved.kz_final
        gain = best - base.kz_final
        sample += 1
        total += gain
        if gain >= shift:
            hits += 1
        if gain > maximum:
            maximum = gain
    if not sample:
        return WindowMoveEffect(None, None, None, 0)
    return WindowMoveEffect(Fraction(hits, sample), Fraction(total, sample), maximum, sample)


def choices_tier(cfg, tier: str, store, tables, swap_layer: Dict, sample_stride: int = WINDOW_SAMPLE_STRIDE) -> Dict:
    """Alle BAL-06-Kennzahlen eines Tiers: Dominanz, Swing, Band, Wegfall-Abfall (statische Schicht) sowie Kurswechsel-
    Spanne und Fensterzug-Wirkung (Tausch-Schicht und Zugpfade)."""
    n = len(cfg.measure_ids)
    code_index = store.column("code_index")
    kz_final = store.column("kz_final")
    own_cost = store.column("own_cost")
    over_budget = store.column("over_budget")
    grid = kz_grid(n, code_index, kz_final, over_budget)
    improvement = level_improvement_shares(grid, n)
    band = near_optimal_band(code_index, kz_final, own_cost, over_budget)
    shares = band_shares(band, n)
    return {
        "tier": tier,
        "measure_ids": list(cfg.measure_ids),
        "improvement": improvement,
        "dominated": strictly_dominated(improvement),
        "swing": level_swing_shares(grid, n),
        "band": band,
        "band_shares": shares,
        "near_mandatory": near_mandatory(shares),
        "drops": removal_drops(grid, n),
        "best_kz": max(grid),
        "best_code": band[0],
        "kurswechsel": kurswechsel_spread(swap_layer["starts"]),
        "window": window_move_effect(tables, sample_stride=sample_stride),
    }


def cross_tier_choices(blocks_by_tier: Dict[str, Dict], bands_by_tier: Dict[str, Iterable[int]]) -> Dict:
    """Entscheidungspunkt Budget-Tier: Jaccard-Ähnlichkeit der Bänder je Tier-Paar und Paare mit demselben besten Plan."""
    tiers = list(blocks_by_tier)
    return {
        "jaccard": tier_band_jaccard({tier: bands_by_tier[tier] for tier in tiers}),
        "same_best": [
            (first, second)
            for first, second in combinations(tiers, 2)
            if blocks_by_tier[first]["best_code"] == blocks_by_tier[second]["best_code"]
        ],
    }


def _name(block: Dict, measure: int) -> str:
    return block["measure_ids"][measure]


def _best_plan(block: Dict) -> str:
    return code_from_index(block["best_code"], len(block["measure_ids"]))


def _dominated(blocks_by_tier: Dict[str, Dict]) -> List[str]:
    return [
        f"Tier {tier}: {_name(block, measure)} L{level} ist strikt dominiert "
        "(es gibt keinen Kontext, in dem das Level besser endet als ein tieferes)"
        for tier, block in blocks_by_tier.items()
        for measure, level in block["dominated"]
    ]


def _swing(blocks_by_tier: Dict[str, Dict]) -> List[str]:
    return [
        f"Tier {tier}: {_name(block, measure)} verschiebt die End-KZ nur in {format_approx(share)} der Kontexte um "
        f"mindestens {DECISION_SHIFT_KZ} (Soll: mindestens {format_approx(DECISION_SHARE)})"
        for tier, block in blocks_by_tier.items()
        for measure, share in sorted(block["swing"].items())
        if share is not None and share < DECISION_SHARE
    ]


def _near_mandatory(blocks_by_tier: Dict[str, Dict]) -> List[str]:
    return [
        f"Tier {tier}: {_name(block, measure)} ist fast zwingend (Level >= 1 in {format_approx(block['band_shares'][measure][0])} "
        f"des Bands, Grenze {format_approx(NEAR_MANDATORY_SHARE)})"
        for tier, block in blocks_by_tier.items()
        for measure in block["near_mandatory"]
    ]


def _overpowered(blocks_by_tier: Dict[str, Dict]) -> List[str]:
    return [
        f"Tier {tier}: {_name(block, measure)} ist überstark (ohne die Maßnahme sinkt die beste End-KZ um {drop}, "
        f"Grenze {OVERPOWERED_DROP})"
        for tier, block in blocks_by_tier.items()
        for measure, drop in sorted(block["drops"].items())
        if drop > OVERPOWERED_DROP
    ]


def _tiers(blocks_by_tier: Dict[str, Dict]) -> List[str]:
    cross = cross_tier_choices(blocks_by_tier, {tier: block["band"] for tier, block in blocks_by_tier.items()})
    lines = [
        f"Tiers {first} und {second}: Jaccard-Ähnlichkeit der Bänder {format_approx(value)} "
        f"(Grenze: unter {format_approx(TIER_JACCARD_MAX)})"
        for (first, second), value in cross["jaccard"].items()
        if value >= TIER_JACCARD_MAX
    ]
    lines += [
        f"Tiers {first} und {second}: gleicher bester Plan {_best_plan(blocks_by_tier[first])}"
        for first, second in cross["same_best"]
    ]
    return lines


def _kurswechsel(blocks_by_tier: Dict[str, Dict]) -> List[str]:
    lines = []
    for tier, block in blocks_by_tier.items():
        share = block["kurswechsel"].share
        if share is None:
            lines.append(f"Tier {tier}: Kurswechsel ohne Start mit zwei Tauschpfaden im Budget")
        elif share < DECISION_SHARE:
            lines.append(
                f"Tier {tier}: Kurswechsel verschiebt die End-KZ nur bei {format_approx(share)} der Starts um "
                f"mindestens {DECISION_SHIFT_KZ} (Soll: mindestens {format_approx(DECISION_SHARE)})"
            )
    return lines


def _window(blocks_by_tier: Dict[str, Dict]) -> List[str]:
    lines = []
    for tier, block in blocks_by_tier.items():
        share = block["window"].share
        if share is None:
            lines.append(f"Tier {tier}: kein Tauschpfad im Budget für den Fenster-Zug")
        elif share < DECISION_SHARE:
            lines.append(
                f"Tier {tier}: der beste Zug im Fenster nach Welle 2 gewinnt nur bei {format_approx(share)} der Pfade "
                f"mindestens {DECISION_SHIFT_KZ} KZ (Soll: mindestens {format_approx(DECISION_SHARE)})"
            )
    return lines


CRITERIA: Tuple[Tuple[str, Callable[[Dict[str, Dict]], List[str]]], ...] = (
    ("dominated", _dominated),
    ("swing", _swing),
    ("near_mandatory", _near_mandatory),
    ("overpowered", _overpowered),
    ("tiers", _tiers),
    ("kurswechsel", _kurswechsel),
    ("window", _window),
)


def check_choices(blocks_by_tier: Dict[str, Dict]) -> List[str]:
    """Deutsche Fehlerzeilen über alle Kriterien (leer = bestanden)."""
    return [line for _name_of_criterion, check in CRITERIA for line in check(blocks_by_tier)]


def format_choices(blocks_by_tier: Dict[str, Dict]) -> str:
    """Deutscher Bericht: je Tier Band, größte Anteile, Wegfall-Abfälle, kleinste Verbesserung, Swing, Entscheidungspunkte."""
    lines = []
    for tier, block in blocks_by_tier.items():
        ids = block["measure_ids"]
        lines.append(f"Tier {tier}: bestes End-KZ im Budget {block['best_kz']} (Plan {_best_plan(block)})")
        lines.append(
            f"  Band: {len(block['band'])} Pläne (höchstens {BAND_KZ} KZ unter dem Bestwert, mindestens {BAND_MIN_SIZE} Pläne)"
        )
        top = sorted(block["band_shares"].items(), key=lambda item: (-item[1][0], item[0]))[:5]
        lines.append(
            "  Anteil im Band (Level >= 1 / >= 2): "
            + ", ".join(f"{ids[m]} {format_approx(s1)} / {format_approx(s2)}" for m, (s1, s2) in top)
        )
        drops = sorted(block["drops"].items(), key=lambda item: (-item[1], item[0]))[:5]
        lines.append("  Wegfall-Abfall der besten End-KZ: " + ", ".join(f"{ids[m]} {drop}" for m, drop in drops))
        known = [(share, key) for key, share in block["improvement"].items() if share is not None]
        if known:
            share, (measure, level) = min(known)
            lines.append(f"  Kleinster Verbesserungsanteil eines Levels: {ids[measure]} L{level} {format_approx(share)}")
        swings = [(share, measure) for measure, share in block["swing"].items() if share is not None]
        if swings:
            share, measure = min(swings)
            lines.append(f"  Kleinster Swing-Anteil (>= {DECISION_SHIFT_KZ} KZ): {ids[measure]} {format_approx(share)}")
        kurswechsel = block["kurswechsel"]
        if kurswechsel.share is not None:
            lines.append(
                f"  Kurswechsel: Anteil der Starts mit Spanne >= {DECISION_SHIFT_KZ} {format_approx(kurswechsel.share)}, "
                f"Median {kurswechsel.median}, p90 {kurswechsel.p90}, {kurswechsel.starts} Starts"
            )
        window = block["window"]
        if window.share is not None:
            lines.append(
                f"  Fenster-Zug nach Welle 2: Anteil mit Gewinn >= {DECISION_SHIFT_KZ} {format_approx(window.share)}, "
                f"Mittel {format_approx(window.mean)}, Maximum {window.maximum}, {window.sample} Pfade"
            )
    cross = cross_tier_choices(blocks_by_tier, {tier: block["band"] for tier, block in blocks_by_tier.items()})
    for (first, second), value in cross["jaccard"].items():
        lines.append(f"Tiers {first} und {second}: Jaccard-Ähnlichkeit der Bänder {format_approx(value)}")
    for first, second in cross["same_best"]:
        lines.append(f"Tiers {first} und {second}: gleicher bester Plan")
    failures = check_choices(blocks_by_tier)
    lines.append("BAL-06: bestanden" if not failures else "BAL-06: NICHT bestanden")
    lines.extend(f"  {failure}" for failure in failures)
    return "\n".join(lines)
