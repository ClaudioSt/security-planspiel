"""Proposes typical legal game paths per tier for the facilitator answer keys (PRINT-10, D-18, D-22).

A candidate is a start selection, the mandatory Kurswechsel swap in the window after the Kurswechsel wave and one
voluntary change-window move later, evaluated with `rules.path_trace`. Candidates stay near the in-budget median of
the swap layer and are ranked by how many mechanics they touch. The approved paths are pinned in the config block
`reference_plans`; re-run this after the Phase 6 rebalance (D-18).
"""
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

from planspiel import rules
from planspiel.enumerate import code_from_index, enumerate_swap_layer, enumerate_tier
from planspiel.fmt import format_approx, format_money, format_number, format_signed
from planspiel.report import summarize_swap_layer
from planspiel.rules import Path, PathError, Window

MECHANICS_MAX = 7
START_TOLERANCE = 3  # static final KZ of a start around the median
MEDIAN_TOLERANCE = 2  # final KZ of a whole path around the median
LEVELS = (0, 1, 2, 3)


class Candidate(NamedTuple):
    tier: str
    path: Path
    trace: rules.PathTrace
    score: int


def reference_path(cfg, tier_name: str) -> Path:
    """The pinned reference path of a tier (KeyError without a `reference_plans` entry)."""
    return path_from_block(cfg.reference_plans[tier_name])


def path_from_block(block) -> Path:
    """The `rules.Path` of a config block with `start` and `windows` (reference plans and reference strategies)."""
    windows = tuple(
        Window(dict(window["selection"]), tuple(window["swap"]) if window.get("swap") is not None else None)
        for window in block["windows"]
    )
    return Path(dict(block["start"]), windows)


def review_deltas(cfg) -> Tuple:
    """Sorted distinct KZ changes of the Budget Review tiers (empty without such an event)."""
    for event in cfg.final_events:
        if event.type == "final_budget_tier":
            return tuple(sorted({delta for _, delta in event.params["tiers"]}))
    return ()


def mechanics_score(trace: rules.PathTrace, review_deltas: Optional[Sequence] = None) -> int:
    """Selection heuristic, not a game rule: one point per mechanic a path touches (at most MECHANICS_MAX).

    Fall 3 in a wave, more than one distinct Fall, a wave with recovery, a wave with a bonus met and one missed, a
    non-zero event KZ, a change window without a swap that moves measures, a Budget Review tier that is neither the
    lowest nor the highest (only with the tier KZ changes given).
    """
    waves = trace.waves
    cases = {wave.case for wave in waves}
    score = 0
    score += 3 in cases
    score += len(cases) > 1
    score += any(wave.recovery_factor > 0 for wave in waves)
    score += any(wave.bonus_met and wave.bonus_missed for wave in waves)
    score += any(wave.kz_event != 0 for wave in waves)
    score += any(
        window.swap is None and window.selection != waves[index].selection
        for index, window in enumerate(trace.windows)
    )
    if review_deltas:
        change = trace.review.kz_review_change
        score += change in review_deltas and change not in (min(review_deltas), max(review_deltas))
    return int(score)


def voluntary_moves(cfg, path: Path) -> List[Tuple[int, str, int, int]]:
    """(window number from 1, measure, level before, level after) for every change beyond the declared swap.

    In the swap window the swap itself and its canonical dependency repair are not voluntary."""
    moves = []
    before = path.start
    for number, window in enumerate(path.windows, start=1):
        expected = before
        if window.swap is not None:
            dropped, incoming = window.swap
            expected = rules.swap_repair(before, dropped, cfg.measures)
            expected[incoming] = window.selection[incoming]
        for measure_id in cfg.measure_ids:
            if window.selection[measure_id] != expected[measure_id]:
                moves.append((number, measure_id, expected[measure_id], window.selection[measure_id]))
        before = window.selection
    return moves


def swap_layer_median(cfg, tier_name: str) -> Optional[int]:
    """In-budget p50 of the final KZ over the swap layer (about 4 minutes per real tier)."""
    summary = summarize_swap_layer(cfg, tier_name, enumerate_swap_layer(cfg, tier_name))
    return summary["percentiles"]["in_budget"]["kz_final"]["p50"]


def _selection(measure_ids: Sequence[str], code: str) -> Dict[str, int]:
    return {measure_id: int(digit) for measure_id, digit in zip(measure_ids, code)}


def _levels(measure_ids: Sequence[str], selection: Dict[str, int]) -> Tuple[int, ...]:
    return tuple(selection[measure_id] for measure_id in measure_ids)


def _ranked_starts(cfg, tier_name: str, median: int, starts: int, deltas: Tuple) -> List[Dict[str, int]]:
    """In-budget starts whose static final KZ is near the median and that allow a swap, best static score first."""
    measure_ids = cfg.measure_ids
    store = enumerate_tier(cfg, tier_name)
    codes = store.column("code_index")
    kz_final = store.column("kz_final")
    over_budget = store.column("over_budget")
    ranked = []
    for index in range(len(store)):
        if over_budget[index] or abs(kz_final[index] - median) > START_TOLERANCE:
            continue
        selection = _selection(measure_ids, code_from_index(codes[index], len(measure_ids)))
        if not rules.swap_possible(selection):
            continue
        trace = rules.path_trace(cfg, tier_name, Path(selection), enforce_kurswechsel=False)
        ranked.append((-mechanics_score(trace, deltas), abs(kz_final[index] - median), codes[index], selection))
    ranked.sort(key=lambda item: item[:3])
    return [item[3] for item in ranked[:starts]]


def _swap_windows(cfg, start: Dict[str, int]):
    """Every legal Kurswechsel swap window of a start with the canonical minimal repair (D-28)."""
    measure_ids = cfg.measure_ids
    for dropped in measure_ids:
        if start[dropped] == 0:
            continue
        repaired = rules.swap_repair(start, dropped, cfg.measures)
        for incoming in measure_ids:
            if start[incoming] != 0:
                continue
            for level in LEVELS[1:]:
                end = dict(repaired)
                end[incoming] = level
                if not rules.dependencies_satisfied(end, cfg.measures):
                    continue
                if rules.swap_legal(start, end, dropped, incoming):
                    yield Window(end, (dropped, incoming))


def _voluntary_windows(cfg, window: Window):
    """Every single voluntary move after the swap window: one measure to another level or cancelled."""
    for measure_id in cfg.measure_ids:
        for level in LEVELS:
            if level == window.selection[measure_id]:
                continue
            moved = dict(window.selection)
            moved[measure_id] = level
            if rules.dependencies_satisfied(moved, cfg.measures):
                yield Window(moved)


def candidate_paths(
    cfg, tier_name: str, *, median: Optional[int] = None, starts: int = 40, keep: int = 3
) -> List[Candidate]:
    """At most `keep` legal, in-budget reference path candidates near the swap-layer median, best first.

    Ranking: mechanics score, then distance of the final KZ to the median, then a stable code order. Candidates are
    taken from different starts first so that the proposals are not near-copies of each other."""
    if median is None:
        median = swap_layer_median(cfg, tier_name)
    if median is None:
        return []
    deltas = review_deltas(cfg)
    measure_ids = cfg.measure_ids
    found = []
    for start in _ranked_starts(cfg, tier_name, median, starts, deltas):
        for swap_window in _swap_windows(cfg, start):
            for move in _voluntary_windows(cfg, swap_window):
                path = Path(start, (swap_window, move))
                try:
                    record = rules.evaluate_path(cfg, tier_name, path)
                except PathError:
                    continue
                if record["over_budget"] or abs(record["kz_final"] - median) > MEDIAN_TOLERANCE:
                    continue
                found.append((
                    abs(record["kz_final"] - median),
                    (_levels(measure_ids, start), _levels(measure_ids, swap_window.selection),
                     _levels(measure_ids, move.selection)),
                    path,
                ))
    scored = []
    for distance, code, path in found:
        trace = rules.path_trace(cfg, tier_name, path)
        scored.append(((-mechanics_score(trace, deltas), distance, code), Candidate(tier_name, path, trace, 0)))
    scored.sort(key=lambda item: item[0])

    chosen, seen_starts, taken = [], set(), set()
    for position, (key, _) in enumerate(scored):
        if len(chosen) == keep:
            break
        if key[2][0] not in seen_starts:
            seen_starts.add(key[2][0])
            chosen.append(position)
            taken.add(position)
    for position in range(len(scored)):
        if len(chosen) == keep:
            break
        if position not in taken:
            chosen.append(position)
    chosen.sort()
    return [
        Candidate(tier_name, scored[position][1].path, scored[position][1].trace, -scored[position][0][0])
        for position in chosen
    ]


def _eur_k(value: int) -> str:
    return f"{format_number(value)} k€"


def _signed_k(value: int) -> str:
    return f"{format_signed(value)} k€"


def _selection_text(measure_ids: Sequence[str], selection: Dict[str, int]) -> str:
    active = [f"{measure_id} L{selection[measure_id]}" for measure_id in measure_ids if selection[measure_id] > 0]
    inactive = [measure_id for measure_id in measure_ids if selection[measure_id] == 0]
    text = ", ".join(active) if active else "keine aktive Maßnahme"
    return f"{text} (inaktiv: {', '.join(inactive)})" if inactive else text


def _event_text(events) -> str:
    parts = []
    for event in events:
        effects = []
        if event["kz_delta"]:
            effects.append(f"KZ {format_signed(event['kz_delta'])}")
        if event["budget_delta"]:
            effects.append(f"Budget {_signed_k(event['budget_delta'])}")
        if event["opex_delta"]:
            effects.append(f"OPEX {_signed_k(event['opex_delta'])}")
        if effects:
            parts.append(f"{event['name']} ({', '.join(effects)})")
    return "; ".join(parts) if parts else "keine Wirkung"


def format_candidate(candidate: Candidate, cfg) -> str:
    """German block for the checkpoint: path structure, per-wave worksheet numbers and the final values."""
    trace = candidate.trace
    path = candidate.path
    measure_ids = cfg.measure_ids
    lines = [f"Tier {candidate.tier}: Mechanik-Punkte {candidate.score} von {MECHANICS_MAX}"]
    lines.append(f"Start: {_selection_text(measure_ids, path.start)}")
    for number, (window, window_trace) in enumerate(zip(path.windows, trace.windows), start=1):
        if window.swap is not None:
            dropped, incoming = window.swap
            lines.append(
                f"Fenster nach Welle {number}: Kurswechsel {dropped} gegen {incoming} auf Level "
                f"{window.selection[incoming]} (Init-Zuwachs {_eur_k(window_trace.increase_k)}, Gutschrift "
                f"{_eur_k(window_trace.credit_k)}, Kosten {_eur_k(window_trace.cost_k)})"
            )
        moves = [move for move in voluntary_moves(cfg, path) if move[0] == number]
        for _, measure_id, before, after in moves:
            lines.append(
                f"Fenster nach Welle {number}: freiwillig {measure_id} von Level {before} auf Level {after} "
                f"(Fensterkosten {_eur_k(window_trace.cost_k)})"
            )
        lines.append(f"  Auswahl danach: {_selection_text(measure_ids, window.selection)}")
    lines.append("")
    for wave in trace.waves:
        recovery = ""
        if wave.recovery_factor > 0:
            recovery = f", vor Recovery {format_money(wave.damage_before_eur)} (Recovery {format_approx(wave.recovery_factor)})"
        clamp = "" if wave.kz_unclamped == wave.kz_after else f" (Begrenzung von {format_number(wave.kz_unclamped)})"
        bonus = f"Bonus +{format_number(wave.bonus_reduction)}"
        if wave.bonus_met or wave.bonus_missed:
            bonus += f" (erfüllt: {', '.join(wave.bonus_met) or '-'}; verfehlt: {', '.join(wave.bonus_missed) or '-'})"
        lines.append(f"Welle {wave.wave_id} ({wave.attack_id}): Auswahl {_selection_text(measure_ids, wave.selection)}")
        lines.append(
            f"  E-Wert {format_approx(wave.e_value)}, {bonus}, GR {format_approx(wave.gesamtreduktion)}, "
            f"Fall {wave.case}, Schaden {format_money(wave.damage_eur)}{recovery}"
        )
        lines.append(
            f"  KZ-Änderung {format_signed(wave.kz_change)} (exakt {format_approx(wave.kz_change_exact)}; Angriff "
            f"{format_approx(wave.kz_attack)}, Ereignisse {format_signed(wave.kz_event)}), "
            f"KZ {format_number(wave.kz_before)} → {format_number(wave.kz_after)}{clamp}"
        )
        lines.append(
            f"  eigene OPEX {_eur_k(wave.own_opex_k)}, Fensterkosten {_eur_k(wave.window_cost_k)}, externe Effekte: "
            f"Budget {_signed_k(wave.event_budget_k)}, OPEX {_signed_k(wave.event_opex_k)} "
            f"[{_event_text(wave.events)}], Restbudget {_eur_k(wave.remaining_k)}"
        )
    review = trace.review
    weights = cfg.final_index
    final_index = rules.final_index(review.kz_final, review.ros, weights.weight_kz, weights.weight_ros)
    lines.append("")
    lines.append(
        f"Budget Review: {format_signed(review.kz_review_change)} KZ bei Restbudget {_eur_k(review.remaining_k)}; "
        f"KZ vor Review {format_number(review.kz_pre_review)}, KZ final {format_number(review.kz_final)}"
    )
    lines.append(
        f"Gesamtschaden {format_money(review.total_damage_eur)}, eigene Kosten {_eur_k(review.own_spend_k)}, "
        f"Restbudget {_eur_k(review.remaining_k)}, im Budget: {'nein' if review.over_budget else 'ja'}"
    )
    ros_text = "nicht definiert" if review.ros is None else format_approx(review.ros)
    lines.append(
        f"RoS {ros_text}; Final-Index {format_approx(final_index)} (vorläufig, Gewichte KZ "
        f"{format_number(weights.weight_kz)} und RoS {format_number(weights.weight_ros)})"
    )
    return "\n".join(lines)


def format_tier_report(cfg, tier_name: str, median: Optional[int], candidates: Sequence[Candidate]) -> str:
    """Whole console/file text of one tier: header, then one block per candidate."""
    header = (
        f"Referenzpfade Tier {tier_name}: Median {median} (End-KZ im Budget, Tausch-Schicht), "
        f"Toleranz ±{MEDIAN_TOLERANCE}, {len(candidates)} Kandidat(en)"
    )
    if not candidates:
        return f"{header}\nKeine Kandidaten im Bereich um den Median."
    blocks = [header]
    for number, candidate in enumerate(candidates, start=1):
        blocks.append("")
        blocks.append(f"Kandidat {number}")
        blocks.append(format_candidate(candidate, cfg))
    return "\n".join(blocks)
