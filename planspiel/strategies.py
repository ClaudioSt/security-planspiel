"""Referenzstrategien (BAL-07): gute Strategien führen zu guten Ergebnissen.

Jede Strategie der Config (`reference_strategies`, Art good/mediocre/bad) wird mit `rules.evaluate_path` bewertet und
gegen zwei Gesamtheiten der Spielenden eingeordnet: gegen den Final-Index aller statischen Pläne im Budget und gegen
die End-KZ aller legalen Spiele der Tausch-Schicht im Budget (D-05, D-09). `good` muss im oberen, `bad` im unteren
Viertel liegen, `mediocre` dazwischen. Die gute Strategie ist an die Hinweis-Zuordnung gebunden: sie folgt den
Hinweis-Punkten der Maßnahmen (D-19), und ein Hinweis-Edit, der sie ändert, bricht die Prüfung sichtbar.

Die Überziehungs-Archetypen sind keine Einträge dieses Blocks; das Überziehungs-Gate beurteilt sie (D-23). Die
Strategien sind Referenzen für Prüfungen, kein Spielinhalt.
"""
import heapq
import math
from bisect import bisect_left, bisect_right
from collections import Counter
from fractions import Fraction
from typing import Dict, List, NamedTuple, Optional, Sequence

from planspiel import refpaths, rules
from planspiel.enumerate import ResultStore, code_from_index
from planspiel.rules import Path, PathError
from planspiel.texts import Clue, clue_scores
from planspiel.validate import REFERENCE_STRATEGY_KINDS

__all__ = [
    "QUARTILE",
    "LOWER_QUARTILE",
    "TOP_SHARE",
    "NON_CLUE_SHARE_MIN",
    "Placement",
    "check_strategies",
    "clue_good_start",
    "clue_scores",
    "format_strategies",
    "non_clue_share",
    "place_strategies",
    "placed_by_kind",
    "strategies_tier",
    "strategy_path",
]

QUARTILE = Fraction(3, 4)
LOWER_QUARTILE = Fraction(1, 4)
TOP_SHARE = Fraction(1, 100)
NON_CLUE_SHARE_MIN = Fraction(1, 5)


class Placement(NamedTuple):
    """Wo eine Referenzstrategie in den beiden Gesamtheiten liegt; Anteile exakt, `None` bei unzulässigem Pfad."""

    tier: str
    name: str
    kind: str
    legal: bool
    in_budget: bool
    kz_final: Optional[int]
    ros: Optional[Fraction]
    final_index: Optional[Fraction]
    fi_below: Optional[Fraction]
    fi_above: Optional[Fraction]
    kz_below: Optional[Fraction]
    kz_above: Optional[Fraction]
    placed: bool


def strategy_path(block: dict) -> Path:
    return refpaths.path_from_block(block)


def placed_by_kind(
    kind: str, fi_below: Fraction, fi_above: Fraction, kz_below: Fraction, kz_above: Fraction
) -> bool:
    """good: oberes Viertel in beiden Gesamtheiten; bad: unteres Viertel in beiden; mediocre: in allen vier Anteilen
    mindestens ein Viertel Abstand zu beiden Enden. Die Grenzen sind inklusiv."""
    if kind == "good":
        return fi_below >= QUARTILE and kz_below >= QUARTILE
    if kind == "bad":
        return fi_above >= QUARTILE and kz_above >= QUARTILE
    if kind == "mediocre":
        return min(fi_below, fi_above, kz_below, kz_above) >= LOWER_QUARTILE
    return False


def _weights(cfg):
    return cfg.final_index.weight_kz, cfg.final_index.weight_ros


def _final_index_population(cfg, store: ResultStore):
    """(sortierte Final-Index-Werte, kumulierte Anzahl vor jedem Wert, Gesamtzahl) der Pläne im Budget."""
    weight_kz, weight_ros = _weights(cfg)
    kz_col = store.column("kz_final")
    damage_col = store.column("damage_eur")
    own_col = store.column("own_cost")
    over_col = store.column("over_budget")
    keys = Counter()
    for i in range(len(store)):
        if not over_col[i]:
            keys[(kz_col[i], damage_col[i], own_col[i])] += 1
    counts = Counter()
    for (kz, damage, own), count in keys.items():
        ros = rules.ros(store.base_losses, Fraction(damage, 1000), own)
        counts[rules.final_index(kz, ros, weight_kz, weight_ros)] += count
    values = sorted(counts)
    before = [0]
    for value in values:
        before.append(before[-1] + counts[value])
    return values, before, before[-1]


def place_strategies(cfg, tier: str, store: ResultStore, swap_layer: Dict) -> List[Placement]:
    entries = cfg.reference_strategies.get(tier, {})
    if not entries:
        return []
    values, before, total = _final_index_population(cfg, store)
    histogram = swap_layer["histogram"]["in_budget"]
    legal_total = sum(histogram)
    weight_kz, weight_ros = _weights(cfg)
    placements = []
    for name, entry in entries.items():
        kind = entry["kind"]
        try:
            record = rules.evaluate_path(cfg, tier, strategy_path(entry))
        except PathError:
            placements.append(Placement(tier, name, kind, False, False, None, None, None, None, None, None, None, False))
            continue
        kz = record["kz_final"]
        index = rules.final_index(kz, record["ros"], weight_kz, weight_ros)
        in_budget = not record["over_budget"]
        if total and legal_total:
            fi_below = Fraction(before[bisect_left(values, index)], total)
            fi_above = Fraction(total - before[bisect_right(values, index)], total)
            kz_below = Fraction(sum(histogram[:kz]), legal_total)
            kz_above = Fraction(sum(histogram[kz + 1 :]), legal_total)
        else:
            fi_below = fi_above = kz_below = kz_above = Fraction(0)
        placed = in_budget and placed_by_kind(kind, fi_below, fi_above, kz_below, kz_above)
        placements.append(
            Placement(tier, name, kind, True, in_budget, kz, record["ros"], index, fi_below, fi_above, kz_below, kz_above, placed)
        )
    return placements


def _fits(cfg, tier: str, selection: Dict[str, int]) -> bool:
    return rules.dependencies_satisfied(selection, cfg.measures) and not rules.evaluate_plan(cfg, tier, selection)["over_budget"]


def clue_good_start(cfg, tier: str, clues: Sequence[Clue]) -> Dict[str, int]:
    """Die Start-Auswahl, die den Hinweisen folgt (D-19).

    1. Maßnahmen mit Hinweis-Punkten > 0 nach (-Punkte, -Wichtigkeit, Config-Reihenfolge); jede bekommt Level 2,
       sonst Level 1, solange der Plan abhängigkeitsgültig und im Budget bleibt.
    2. Danach hebt sie wiederholt die eine Maßnahme um ein Level, die das schwächste CIA-Maß am stärksten hebt
       (Gleichstand: größere Summe C+I+A, geringere eigene Ausgaben, Config-Reihenfolge) und im Budget bleibt, aber nur
       solange das schwächste CIA-Maß dadurch strikt wächst.
    """
    scores = clue_scores(tuple(clues))
    importance = rules.bonus_importance(cfg)
    ids = list(cfg.measures)
    ordered = sorted(
        (measure_id for measure_id in ids if scores.get(measure_id, 0) > 0),
        key=lambda measure_id: (-scores[measure_id], -importance.get(measure_id, Fraction(0)), ids.index(measure_id)),
    )
    selection = {measure_id: 0 for measure_id in ids}
    for measure_id in ordered:
        for level in (2, 1):
            trial = {**selection, measure_id: level}
            if _fits(cfg, tier, trial):
                selection = trial
                break
    while True:
        current = min(rules.compute_cia(selection, cfg.measures, cfg.base_cia).values())
        best = None
        for position, measure_id in enumerate(ids):
            if selection[measure_id] >= max(cfg.measures[measure_id].levels):
                continue
            trial = {**selection, measure_id: selection[measure_id] + 1}
            if not _fits(cfg, tier, trial):
                continue
            cia = rules.compute_cia(trial, cfg.measures, cfg.base_cia)
            spend = rules.evaluate_plan(cfg, tier, trial)["costs"]["security_spend"]
            key = (-min(cia.values()), -sum(cia.values()), spend, position)
            if best is None or key < best[0]:
                best = (key, trial, min(cia.values()))
        if best is None or best[2] <= current:
            return selection
        selection = best[1]


def non_clue_share(cfg, store: ResultStore, clues: Sequence[Clue], top: Fraction = TOP_SHARE) -> Fraction:
    """Anteil der besten Pläne im Budget (obere `top` nach Final-Index, dann KZ, eigene Kosten, Code), die eine
    Maßnahme auf Level >= 1 enthalten, für die kein Hinweis-Punkt vergeben ist (D-19: nur die belegten Maßnahmen zu
    kaufen ist nicht automatisch am besten)."""
    weight_kz, weight_ros = _weights(cfg)
    kz_col = store.column("kz_final")
    damage_col = store.column("damage_eur")
    own_col = store.column("own_cost")
    code_col = store.column("code_index")
    over_col = store.column("over_budget")
    indices = [i for i in range(len(store)) if not over_col[i]]
    if not indices:
        return Fraction(0)
    cache: Dict[tuple, Fraction] = {}

    def final_index_of(i: int) -> Fraction:
        key = (kz_col[i], damage_col[i], own_col[i])
        if key not in cache:
            ros = rules.ros(store.base_losses, Fraction(damage_col[i], 1000), own_col[i])
            cache[key] = rules.final_index(kz_col[i], ros, weight_kz, weight_ros)
        return cache[key]

    count = math.ceil(len(indices) * top)
    best = heapq.nsmallest(count, indices, key=lambda i: (-final_index_of(i), -kz_col[i], own_col[i], code_col[i]))
    scores = clue_scores(tuple(clues))
    unsupported = [position for position, measure_id in enumerate(cfg.measures) if scores.get(measure_id, 0) == 0]
    width = len(cfg.measures)
    hits = 0
    for i in best:
        code = code_from_index(code_col[i], width)
        if any(code[position] != "0" for position in unsupported):
            hits += 1
    return Fraction(hits, len(best))


def _percent(share: Optional[Fraction]) -> str:
    return "-" if share is None else f"{float(share) * 100:.0f} %"


def check_strategies(
    cfg, tier: str, placements: Sequence[Placement], clues: Sequence[Clue], non_clue: Fraction
) -> List[str]:
    """Deutsche Fehlerzeilen für einen Tier; leer heißt, BAL-07 gilt für diese Config und diese Hinweise."""
    entries = cfg.reference_strategies.get(tier)
    if not entries:
        return [f"Tier {tier}: keine Referenzstrategien in der Config (reference_strategies)"]
    lines = []
    present = {placement.kind for placement in placements}
    for kind in REFERENCE_STRATEGY_KINDS:
        if kind not in present:
            lines.append(f"Tier {tier}: keine Referenzstrategie der Art '{kind}'")
    for placement in placements:
        if not placement.legal:
            lines.append(f"Tier {tier}: Strategie '{placement.name}' ist kein legaler Pfad (Kurswechsel, Abhängigkeiten)")
        elif not placement.in_budget:
            lines.append(
                f"Tier {tier}: Strategie '{placement.name}' liegt über dem Budget; "
                "Überziehen beurteilt das Überziehungs-Gate (D-23), nicht dieser Block"
            )
        elif not placement.placed:
            lines.append(
                f"Tier {tier}: Strategie '{placement.name}' ({placement.kind}) liegt nicht im erwarteten Viertel: "
                f"Final-Index unter {_percent(placement.fi_below)} / über {_percent(placement.fi_above)}, "
                f"KZ unter {_percent(placement.kz_below)} / über {_percent(placement.kz_above)}"
            )
    if "good" not in entries:
        lines.append(f"Tier {tier}: keine Strategie mit dem Namen 'good'")
    else:
        derived = clue_good_start(cfg, tier, clues)
        if dict(entries["good"]["start"]) != derived:
            lines.append(
                f"Tier {tier}: der Start von 'good' weicht von der Strategie aus den Hinweisen ab "
                f"(Hinweise: {_code(cfg, derived)}, Config: {_code(cfg, entries['good']['start'])})"
            )
    if non_clue < NON_CLUE_SHARE_MIN:
        lines.append(
            f"Tier {tier}: nur {_percent(non_clue)} der besten Pläne enthalten eine Maßnahme ohne Hinweis, "
            f"nötig sind mindestens {_percent(NON_CLUE_SHARE_MIN)}"
        )
    return lines


def _code(cfg, selection: Dict[str, int]) -> str:
    return "".join(str(selection[measure_id]) for measure_id in cfg.measures)


def strategies_tier(cfg, tier: str, store: ResultStore, swap_layer: Dict, clues: Sequence[Clue]) -> Dict:
    placements = place_strategies(cfg, tier, store, swap_layer)
    share = non_clue_share(cfg, store, clues)
    return {
        "tier": tier,
        "placements": placements,
        "non_clue_share": share,
        "good_start": clue_good_start(cfg, tier, clues),
        "failures": check_strategies(cfg, tier, placements, clues, share),
    }


def format_strategies(blocks_by_tier: Dict[str, Dict]) -> str:
    lines = ["Referenzstrategien (BAL-07)"]
    if not blocks_by_tier:
        lines.append("Keine Referenzstrategien konfiguriert.")
        return "\n".join(lines)
    for tier, block in blocks_by_tier.items():
        lines.append("")
        lines.append(f"Tier {tier}")
        lines.append("| Name | Art | KZ | RoS | Final-Index | Final-Index unter/über | KZ unter/über | platziert |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for placement in block["placements"]:
            if not placement.legal:
                cells = (placement.name, placement.kind, "-", "-", "-", "-", "-", "unzulässig")
            else:
                ros = "-" if placement.ros is None else f"{float(placement.ros):.2f}"
                cells = (
                    placement.name,
                    placement.kind,
                    str(placement.kz_final),
                    ros,
                    f"{float(placement.final_index):.2f}",
                    f"{_percent(placement.fi_below)} / {_percent(placement.fi_above)}",
                    f"{_percent(placement.kz_below)} / {_percent(placement.kz_above)}",
                    "ja" if placement.placed else ("über Budget" if not placement.in_budget else "nein"),
                )
            lines.append("| " + " | ".join(cells) + " |")
        lines.append(f"Beste Pläne mit Maßnahme ohne Hinweis: {_percent(block['non_clue_share'])}")
        for failure in block["failures"]:
            lines.append(f"FEHLER {failure}")
    return "\n".join(lines)
