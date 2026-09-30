import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Dict, Optional

from planspiel import rules
from planspiel.cli import configure_utf8_stdio
from planspiel.config import load_config
from planspiel.enumerate import LEVEL_OPTIONS, iter_selections


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


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Enumerate all deterministic outcomes for the planspiel.")
    parser.add_argument("--config", default="simulation_config.json", help="Path to simulation config JSON.")
    parser.add_argument("--budget-tier", default=None, help="Budget tier name (low|medium|high).")
    parser.add_argument("--output", default="simulation_results.json", help="Output JSON file path.")
    parser.add_argument("--budget-min", type=int, default=None, help="Minimum total cost filter (points).")
    parser.add_argument("--budget-max", type=int, default=None, help="Maximum total cost filter (points).")
    parser.add_argument(
        "--budget-utilization",
        type=float,
        default=0.0,
        help="Minimum utilization of budget max (e.g. 0.9 for 90%%).",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    configure_utf8_stdio()
    args = parse_args(argv)
    summary = run_simulation(
        Path(args.config),
        args.budget_tier,
        Path(args.output),
        args.budget_min,
        args.budget_max,
        args.budget_utilization,
    )
    print(json.dumps(summary, indent=2))
    return 0
