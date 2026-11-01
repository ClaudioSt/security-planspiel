import heapq
import json
from collections import Counter
from fractions import Fraction
from typing import Dict, List, Optional

from planspiel import rules
from planspiel.enumerate import LEVEL_OPTIONS, ResultStore, code_from_index
from planspiel.rounding import exact_to_json

PERCENTILES = (0, 5, 25, 50, 75, 95, 100)
DEFAULT_TOP_K = 10
CONSOLE_TOP_LINES = 3
SUMMARY_FILENAME = "simulation_summary_{tier}.json"
FINAL_INDEX_STATUS = "Final-Index = KZ + k · RoS, RoS auf zwei Nachkommastellen gerundet, Gewichte aus final_index"
REFERENCE_LAYER = "referenz"
REFERENCE_LABEL = "Referenzplan ohne Change-Fenster-Züge"
SWAP_LAYER = "tausch"
SWAP_LABEL = "Pflicht-Maßnahmentausch (Kurswechsel), legales Minimum"


def nearest_rank(sorted_values: List, p: int):
    if not sorted_values:
        return None
    return sorted_values[max(0, (p * len(sorted_values) + 99) // 100 - 1)]


def pareto_front(store: ResultStore, in_budget_only: bool = False) -> List[Dict]:
    pairs = {}
    for code_index, kz, own, over in zip(
        store.column("code_index"), store.column("kz_final"), store.column("own_cost"), store.column("over_budget")
    ):
        if in_budget_only and over:
            continue
        key = (own, kz)
        seen = pairs.get(key)
        if seen is None:
            pairs[key] = [1, code_index]
        else:
            seen[0] += 1
            if code_index < seen[1]:
                seen[1] = code_index

    best_by_cost = {}
    for own, kz in pairs:
        if best_by_cost.get(own, -1) < kz:
            best_by_cost[own] = kz

    front = []
    best_so_far = -1
    for own in sorted(best_by_cost):
        kz = best_by_cost[own]
        if kz > best_so_far:
            count, example_index = pairs[(own, kz)]
            front.append(
                {"own_cost": own, "kz_final": kz, "combinations": count, "example_index": example_index}
            )
            best_so_far = kz
    return front


def _group_percentiles(kz_values: List[int], ros_values: List[Fraction]) -> Dict:
    kz_sorted = sorted(kz_values)
    return {
        "count": len(kz_values),
        "kz_final": {f"p{p}": nearest_rank(kz_sorted, p) for p in PERCENTILES},
        "ros_count": len(ros_values),
        "ros": {
            f"p{p}": None if not ros_values else exact_to_json(nearest_rank(ros_values, p))
            for p in PERCENTILES
        },
    }


def summarize_tier(cfg, tier_name: str, store: ResultStore, top_k: int = DEFAULT_TOP_K) -> Dict:
    tier = cfg.budget_tiers[tier_name]
    measure_ids = cfg.measure_ids
    base = store.base_losses
    code_col = store.column("code_index")
    kz_col = store.column("kz_final")
    own_col = store.column("own_cost")
    total_col = store.column("total_cost")
    damage_col = store.column("damage_eur")
    over_col = store.column("over_budget")
    n = len(store)

    ros_cache = {}

    def ros_of(i):
        key = (damage_col[i], own_col[i])
        try:
            return ros_cache[key]
        except KeyError:
            value = ros_cache[key] = rules.ros(base, Fraction(key[0], 1000), key[1])
            return value

    ros_values = [ros_of(i) for i in range(n)]

    fi_cache = {}

    def final_index_of(i):
        key = (kz_col[i], damage_col[i], own_col[i])
        try:
            return fi_cache[key]
        except KeyError:
            value = fi_cache[key] = rules.final_index(
                kz_col[i], ros_values[i], cfg.final_index.weight_kz, cfg.final_index.weight_ros
            )
            return value

    def kz_key(i):
        return (-kz_col[i], own_col[i], damage_col[i], code_col[i])

    def ros_key(i):
        return (-ros_values[i], -kz_col[i], own_col[i], code_col[i])

    def final_index_key(i):
        return (-final_index_of(i), -kz_col[i], own_col[i], code_col[i])

    def entry(i):
        code = code_from_index(code_col[i], len(measure_ids))
        ros = ros_values[i]
        return {
            "code": code,
            "selection": {measure: int(digit) for measure, digit in zip(measure_ids, code)},
            "kz_final": kz_col[i],
            "own_cost": own_col[i],
            "total_cost": total_col[i],
            "total_damage": exact_to_json(Fraction(damage_col[i], 1000)),
            "ros": None if ros is None else exact_to_json(ros),
            "final_index": exact_to_json(final_index_of(i)),
            "over_budget": bool(over_col[i]),
        }

    def ranked(indices, key):
        return [
            {"rank": rank, **entry(i)}
            for rank, i in enumerate(heapq.nsmallest(top_k, indices, key=key), start=1)
        ]

    def best_of(flag):
        found = heapq.nsmallest(1, (i for i in range(n) if over_col[i] == flag), key=kz_key)
        return entry(found[0]) if found else None

    percentiles = {}
    for name, flag in (("in_budget", 0), ("over_budget", 1)):
        kz_values = [kz for kz, over in zip(kz_col, over_col) if over == flag]
        counts = Counter(
            (damage, own)
            for damage, own, over in zip(damage_col, own_col, over_col)
            if over == flag and own != 0
        )
        ordered_keys = sorted(counts, key=ros_cache.__getitem__)
        ros_sorted = [ros_cache[key] for key in ordered_keys for _ in range(counts[key])]
        percentiles[name] = _group_percentiles(kz_values, ros_sorted)

    best_in = best_of(0)
    best_over = best_of(1)
    kz_gap = None if best_in is None or best_over is None else best_over["kz_final"] - best_in["kz_final"]

    def pareto_block(in_budget_only):
        points = []
        for point in pareto_front(store, in_budget_only):
            i = code_col.index(point["example_index"])
            points.append(
                {
                    "own_cost": point["own_cost"],
                    "kz_final": point["kz_final"],
                    "combinations": point["combinations"],
                    "example": entry(i),
                }
            )
        return {
            "objectives": {"kz_final": "max", "own_cost": "min"},
            "count": len(points),
            "points": points,
        }

    in_budget_indices = [i for i in range(n) if not over_col[i]]
    in_budget_count = len(in_budget_indices)
    return {
        "format": 1,
        "tier": tier_name,
        "layer": REFERENCE_LAYER,
        "layer_label": REFERENCE_LABEL
        + " (Kurswechsel nicht angewendet; legales Spiel nur ohne möglichen Maßnahmentausch)",
        "budget": tier.budget,
        "kz_start": tier.kz_start,
        "measures": measure_ids,
        "combinations": {
            "total": len(LEVEL_OPTIONS) ** len(measure_ids),
            "valid": n,
            "in_budget": in_budget_count,
            "over_budget": n - in_budget_count,
        },
        "top_k": top_k,
        "final_index_status": FINAL_INDEX_STATUS,
        "top": {
            "kz_final": ranked(range(n), kz_key),
            "ros": ranked((i for i in range(n) if ros_values[i] is not None), ros_key),
            "final_index": ranked(range(n), final_index_key),
        },
        "top_in_budget": {
            "kz_final": ranked(in_budget_indices, kz_key),
            "ros": ranked((i for i in in_budget_indices if ros_values[i] is not None), ros_key),
            "final_index": ranked(in_budget_indices, final_index_key),
        },
        "percentiles": {
            "method": "nearest-rank",
            "p": list(PERCENTILES),
            "in_budget": percentiles["in_budget"],
            "over_budget": percentiles["over_budget"],
        },
        "best": {
            "metric": "kz_final",
            "in_budget": best_in,
            "over_budget": best_over,
            "kz_gap": kz_gap,
        },
        "pareto": pareto_block(False),
        "pareto_in_budget": pareto_block(True),
    }


def _number(value, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return str(value)
    return f"{float(Fraction(value)):.{digits}f}"


def _entry_line(entry: Dict) -> str:
    budget = "über Budget" if entry["over_budget"] else "im Budget"
    return (
        f"{entry['code']}  End-KZ {entry['kz_final']}  RoS {_number(entry['ros'])}  "
        f"Final-Index {_number(entry['final_index'], 2)}  eigene Kosten {entry['own_cost']}  ({budget})"
    )


def format_console(summary: Dict) -> str:
    combos = summary["combinations"]
    best = summary["best"]
    lines = [
        summary["layer_label"],
        f"Tier {summary['tier']}: Budget {summary['budget']}, Start-KZ {summary['kz_start']}",
        f"Kombinationen: {combos['valid']} gültig, davon {combos['in_budget']} im Budget "
        f"und {combos['over_budget']} über Budget",
    ]
    if best["kz_gap"] is None:
        lines.append("Bestes Ergebnis (End-KZ): nur eine Gruppe vorhanden")
    else:
        lines.append(
            f"Bestes Ergebnis (End-KZ): im Budget {best['in_budget']['kz_final']}, "
            f"über Budget {best['over_budget']['kz_final']}, Differenz {best['kz_gap']:+d}"
        )

    percentiles = summary["percentiles"]
    lines.append("")
    lines.append("Perzentile (Nearest-Rank)")
    lines.append(f"{'':<22}" + "".join(f"{'p' + str(p):>9}" for p in percentiles["p"]))
    for metric, label in (("kz_final", "End-KZ"), ("ros", "RoS")):
        for group, group_label in (("in_budget", "im Budget"), ("over_budget", "über Budget")):
            values = percentiles[group][metric]
            lines.append(
                f"{label + ' ' + group_label:<22}"
                + "".join(f"{_number(values[f'p{p}']):>9}" for p in percentiles["p"])
            )

    for key, label in (
        ("kz_final", "Top nach End-KZ"),
        ("ros", "Top nach RoS"),
        ("final_index", "Top nach Final-Index"),
    ):
        lines.append("")
        lines.append(f"{label} (K={summary['top_k']}, erste {CONSOLE_TOP_LINES}):")
        for item in summary["top"][key][:CONSOLE_TOP_LINES]:
            lines.append(f"  {item['rank']}. {_entry_line(item)}")

    for key, label in (
        ("kz_final", "Top im Budget nach End-KZ"),
        ("ros", "Top im Budget nach RoS"),
        ("final_index", "Top im Budget nach Final-Index"),
    ):
        lines.append("")
        lines.append(f"{label} (K={summary['top_k']}, erste {CONSOLE_TOP_LINES}):")
        for item in summary["top_in_budget"][key][:CONSOLE_TOP_LINES]:
            lines.append(f"  {item['rank']}. {_entry_line(item)}")

    for key, label in (
        ("pareto", "Pareto-Front (End-KZ vs. eigene Kosten, alle Kombinationen)"),
        ("pareto_in_budget", "Pareto-Front im Budget (End-KZ vs. eigene Kosten)"),
    ):
        pareto = summary[key]
        lines.append("")
        lines.append(f"{label}: {pareto['count']} Punkte")
        if pareto["points"]:
            cheapest = pareto["points"][0]
            highest = pareto["points"][-1]
            lines.append(f"  günstigster Punkt: eigene Kosten {cheapest['own_cost']}, End-KZ {cheapest['kz_final']}")
            lines.append(f"  höchster Punkt: eigene Kosten {highest['own_cost']}, End-KZ {highest['kz_final']}")
    return "\n".join(lines)


def _histogram_rank(histogram: List[int], p: int) -> Optional[int]:
    total = sum(histogram)
    if total == 0:
        return None
    rank = max(1, (p * total + 99) // 100)
    seen = 0
    for value, count in enumerate(histogram):
        seen += count
        if seen >= rank:
            return value


def _swap_entry(cfg, layer_best: Optional[Dict], base: int) -> Optional[Dict]:
    if layer_best is None:
        return None
    measure_ids = cfg.measure_ids
    outcome = layer_best["outcome"]
    dropped = layer_best["dropped"]
    incoming = layer_best["incoming"]
    ros = rules.ros(base, Fraction(outcome.damage_eur, 1000), outcome.own_cost)
    return {
        "start": code_from_index(layer_best["start"], len(measure_ids)),
        "end": code_from_index(layer_best["end"], len(measure_ids)),
        "dropped": None if dropped is None else measure_ids[dropped],
        "incoming": None if incoming is None else measure_ids[incoming],
        "level": layer_best["level"],
        "window_cost": layer_best["window_cost"],
        "kz_final": outcome.kz_final,
        "own_cost": outcome.own_cost,
        "total_cost": outcome.total_cost,
        "remaining": outcome.remaining,
        "ros": None if ros is None else exact_to_json(ros),
        "over_budget": outcome.over_budget,
    }


def summarize_swap_layer(cfg, tier_name: str, layer: Dict) -> Dict:
    tier = cfg.budget_tiers[tier_name]
    base = rules.base_losses(cfg.waves, cfg.attacks)
    percentiles = {"method": "nearest-rank", "p": list(PERCENTILES)}
    for name in ("in_budget", "over_budget"):
        histogram = layer["histogram"][name]
        percentiles[name] = {
            "count": sum(histogram),
            "kz_final": {f"p{p}": _histogram_rank(histogram, p) for p in PERCENTILES},
        }
    return {
        "format": 1,
        "tier": tier_name,
        "layer": SWAP_LAYER,
        "layer_label": SWAP_LABEL,
        "kurswechsel_wave": layer["kurswechsel_wave"],
        "budget": tier.budget,
        "kz_start": tier.kz_start,
        "measures": cfg.measure_ids,
        "counts": dict(layer["counts"]),
        "best": {
            "metric": "kz_final",
            "in_budget": _swap_entry(cfg, layer["best"]["in_budget"], base),
            "over_budget": _swap_entry(cfg, layer["best"]["over_budget"], base),
        },
        "percentiles": percentiles,
    }


def _swap_entry_line(entry: Dict) -> str:
    if entry["dropped"] is None:
        move = "kein Tausch möglich (statischer Pfad)"
    else:
        move = f"Tausch {entry['dropped']} gegen {entry['incoming']} auf Level {entry['level']}"
    return (
        f"Start {entry['start']}, Ende {entry['end']}, {move}, Fensterkosten {entry['window_cost']}, "
        f"End-KZ {entry['kz_final']}, eigene Kosten {entry['own_cost']}, RoS {_number(entry['ros'])}"
    )


def format_swap_console(summary: Dict) -> str:
    counts = summary["counts"]
    lines = [
        summary["layer_label"],
        f"Tier {summary['tier']}: Budget {summary['budget']}, Start-KZ {summary['kz_start']}",
        f"Pläne der ersten Welle: {counts['start_plans']} gültig, davon {counts['exempt_static']} ohne möglichen "
        f"Tausch (statischer Pfad) und {counts['swap_paths']} Tausch-Pfade",
        f"Legale Spiele: {counts['legal_games']}, davon {counts['in_budget']} im Budget und "
        f"{counts['over_budget']} über Budget",
        f"Tausch-Pfade: {counts['swap_in_budget']} im Budget, {counts['swap_over_budget']} über Budget",
    ]
    for name, label in (("in_budget", "im Budget"), ("over_budget", "über Budget")):
        entry = summary["best"][name]
        lines.append(f"Bestes Ergebnis (End-KZ) {label}: " + ("keines" if entry is None else _swap_entry_line(entry)))

    percentiles = summary["percentiles"]
    lines.append("")
    lines.append("Perzentile End-KZ (Nearest-Rank)")
    lines.append(f"{'':<22}" + "".join(f"{'p' + str(p):>9}" for p in percentiles["p"]))
    for name, label in (("in_budget", "im Budget"), ("over_budget", "über Budget")):
        values = percentiles[name]["kz_final"]
        lines.append(f"{'End-KZ ' + label:<22}" + "".join(f"{_number(values[f'p{p}']):>9}" for p in percentiles["p"]))
    return "\n".join(lines)


def write_summary(path, summary: Dict) -> None:
    text = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def dump_record(measure_ids, code_index: int, outcome, base_losses, weights) -> Dict:
    ros = rules.ros(base_losses, Fraction(outcome.damage_eur, 1000), outcome.own_cost)
    return {
        "code": code_from_index(code_index, len(measure_ids)),
        "kz_final": outcome.kz_final,
        "kz_pre_review": outcome.kz_pre_review,
        "kz_after": list(outcome.kz_after),
        "own_cost": outcome.own_cost,
        "total_cost": outcome.total_cost,
        "remaining": outcome.remaining,
        "total_damage": exact_to_json(Fraction(outcome.damage_eur, 1000)),
        "ros": None if ros is None else exact_to_json(ros),
        "final_index": exact_to_json(
            rules.final_index(outcome.kz_final, ros, weights.weight_kz, weights.weight_ros)
        ),
        "over_budget": outcome.over_budget,
    }
