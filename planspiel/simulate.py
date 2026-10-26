import argparse
import json
import time
from fractions import Fraction
from pathlib import Path
from typing import Dict, Optional

from planspiel import rules
from planspiel.cli import configure_utf8_stdio
from planspiel.config import load_config
from planspiel.enumerate import LEVEL_OPTIONS, enumerate_tier, iter_selections
from planspiel.report import (
    DEFAULT_TOP_K,
    SUMMARY_FILENAME,
    dump_record,
    format_console,
    summarize_tier,
    write_summary,
)


def to_legacy_json(obj):
    if isinstance(obj, Fraction):
        return int(obj) if obj.denominator == 1 else float(obj)
    if isinstance(obj, dict):
        return {key: to_legacy_json(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [to_legacy_json(value) for value in obj]
    return obj


def run_simulation(
    config_path: Path,
    budget_tier_name: str,
    output_path: Path,
    budget_min: Optional[int],
    budget_max: Optional[int],
    budget_utilization: float,
) -> Dict:
    cfg = load_config(config_path)
    budget_tier = cfg.budget_tiers[budget_tier_name or cfg.default_budget_tier]
    kz_start = budget_tier.kz_start
    measure_ids = cfg.measure_ids
    results = []

    # Use fixed budget value
    tier_budget = budget_tier.budget
    min_cost = budget_min if budget_min is not None else 0
    max_cost = budget_max if budget_max is not None else tier_budget
    utilization_threshold = max_cost * budget_utilization if budget_utilization else None

    for selection in iter_selections(measure_ids, LEVEL_OPTIONS):
        if not rules.dependencies_satisfied(selection, cfg.measures):
            continue
        outcome = rules.evaluate_plan(cfg, budget_tier.name, selection)
        total_cost = outcome["costs"]["total"]

        if total_cost < min_cost or outcome["over_budget"]:
            continue
        if utilization_threshold is not None and total_cost < utilization_threshold:
            continue

        del outcome["over_budget"]
        del outcome["ros"]
        results.append(outcome)

    results.sort(key=lambda item: (-item["kz_final"], item["total_damage"]))

    summary = {
        "total_outcomes": len(results),
        "budget_tier": budget_tier.name,
        "budget": tier_budget,
        "kz_start": kz_start,
        "budget_filter": {
            "min": min_cost,
            "max": max_cost,
            "utilization_min": utilization_threshold,
        },
        "measures": measure_ids,
    }

    output = {
        "summary": summary,
        "results": results,
    }
    output_path.write_text(json.dumps(to_legacy_json(output), indent=2), encoding="utf-8")
    return summary


def build_parser():
    parser = argparse.ArgumentParser(description="Enumerate all deterministic outcomes for the planspiel.")
    parser.add_argument("--config", default="simulation_config.json", help="Path to simulation config JSON.")
    parser.add_argument("--budget-tier", default=None, help="Budget tier name (low|medium|high).")
    parser.add_argument(
        "--output",
        default=None,
        help="Legacy-Vollausgabe als JSON (nur Kombinationen im Budget, Eingabe für analyze_simulation_results.py). "
        "Ohne --output wird die Zusammenfassung über alle Kombinationen geschrieben.",
    )
    parser.add_argument("--budget-min", type=int, default=None, help="Minimum total cost filter (points).")
    parser.add_argument("--budget-max", type=int, default=None, help="Maximum total cost filter (points).")
    parser.add_argument(
        "--budget-utilization",
        type=float,
        default=None,
        help="Minimum utilization of budget max (e.g. 0.9 for 90%%).",
    )
    parser.add_argument(
        "--summary",
        default=None,
        help="Pfad der Zusammenfassung (Standard: simulation_summary_<tier>.json im Arbeitsverzeichnis).",
    )
    parser.add_argument(
        "--dump-jsonl",
        default=None,
        help="Vollständiger Dump aller gültigen Kombinationen als JSONL (nur auf Anfrage, sehr groß).",
    )
    parser.add_argument(
        "--top", type=int, default=None, help=f"Anzahl der Einträge je Top-Liste (Standard: {DEFAULT_TOP_K})."
    )
    return parser


def parse_args(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.output is None:
        legacy = [
            flag
            for flag, value in (
                ("--budget-min", args.budget_min),
                ("--budget-max", args.budget_max),
                ("--budget-utilization", args.budget_utilization),
            )
            if value is not None
        ]
        if legacy:
            parser.error(f"{', '.join(legacy)} wirken nur zusammen mit --output (Legacy-Vollausgabe).")
    else:
        summary_flags = [
            flag
            for flag, given in (
                ("--summary", args.summary is not None),
                ("--dump-jsonl", args.dump_jsonl is not None),
                ("--top", args.top is not None),
            )
            if given
        ]
        if summary_flags:
            parser.error(f"{', '.join(summary_flags)} sind mit --output (Legacy-Vollausgabe) nicht kombinierbar.")
    if args.top is not None and args.top < 1:
        parser.error("--top muss mindestens 1 sein.")
    return args


def _enumerate(cfg, tier_name, dump_path):
    if dump_path is None:
        return enumerate_tier(cfg, tier_name)
    base_losses = rules.base_losses(cfg.waves, cfg.attacks)
    measure_ids = cfg.measure_ids
    with open(dump_path, "w", encoding="utf-8", newline="\n") as handle:

        def write(code_index, outcome):
            record = dump_record(measure_ids, code_index, outcome, base_losses, cfg.final_index)
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

        return enumerate_tier(cfg, tier_name, on_outcome=write)


def main(argv=None) -> int:
    configure_utf8_stdio()
    args = parse_args(argv)
    if args.output is not None:
        summary = run_simulation(
            Path(args.config),
            args.budget_tier,
            Path(args.output),
            args.budget_min,
            args.budget_max,
            args.budget_utilization or 0.0,
        )
        print(json.dumps(summary, indent=2))
        return 0

    cfg = load_config(Path(args.config))
    tier_name = args.budget_tier or cfg.default_budget_tier
    if tier_name not in cfg.budget_tiers:
        build_parser().error(
            f"Unbekanntes Budget-Tier '{tier_name}'. Verfügbar: {', '.join(cfg.budget_tiers)}."
        )
    summary_path = Path(args.summary or SUMMARY_FILENAME.format(tier=tier_name))

    started = time.perf_counter()
    store = _enumerate(cfg, tier_name, args.dump_jsonl)
    summary = summarize_tier(cfg, tier_name, store, args.top or DEFAULT_TOP_K)
    write_summary(summary_path, summary)
    seconds = time.perf_counter() - started

    print(format_console(summary))
    print()
    print(f"Laufzeit: {seconds:.1f} s")
    print(f"Speicher je Kombination: {store.bytes_per_record} Byte")
    print(f"Zusammenfassung: {summary_path}")
    if args.dump_jsonl is not None:
        print(f"Dump: {args.dump_jsonl}")
    return 0
