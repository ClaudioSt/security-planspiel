import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional

from planspiel import rules
from planspiel.cli import configure_utf8_stdio
from planspiel.config import load_config
from planspiel.report import REFERENCE_LABEL


def load_results(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"), parse_float=Fraction)


def format_currency(value: float) -> str:
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_kz(value) -> str:
    return str(int(value)) if value.denominator == 1 else f"{value:.1f}"


def format_percent(value: float) -> str:
    return f"{value:.2f}%".replace(".", ",")


def get_value(item: Dict, key: str):
    if "." not in key:
        return item[key]
    current = item
    for part in key.split("."):
        current = current[part]
    return current


def summarize_top(results: List[Dict], key: str, top_n: int) -> List[Dict]:
    return sorted(results, key=lambda item: get_value(item, key), reverse=True)[:top_n]


def summarize_bottom(results: List[Dict], key: str, top_n: int) -> List[Dict]:
    return sorted(results, key=lambda item: get_value(item, key))[:top_n]


def selection_to_string(selection: Dict[str, int]) -> str:
    return ", ".join(f"{measure}:{level}" for measure, level in sorted(selection.items()))


def print_section(title: str):
    print(f"\n{title}")
    print("-" * len(title))


def item_ros(item: Dict, base_losses: Optional[float]) -> Optional[float]:
    if base_losses is None:
        return None
    costs = item["costs"]
    own_spend = costs["security_spend"] if "security_spend" in costs else costs["total"] - costs["event_opex"]
    return rules.ros(base_losses, item["total_damage"], own_spend)


def print_ros_and_final_index(item: Dict, base_losses: Optional[float], weight_kz: Fraction, weight_ros: Fraction):
    if base_losses is None:
        return
    ros = item_ros(item, base_losses)
    if ros is None:
        print("  RoS: n/a")
    else:
        print(f"  RoS: {format_percent(ros * 100)}")
    final_index = rules.final_index(item["kz_final"], ros, weight_kz, weight_ros)
    print(f"  Final-Index: {format_currency(final_index)}")


def compute_summary(data: Dict, top_n: int, base_losses: Optional[float], weight_kz: Fraction, weight_ros: Fraction):
    results = data.get("results", [])
    if not results:
        print("Keine Ergebnisse gefunden.")
        return

    kz_values = [item["kz_final"] for item in results]
    damage_values = [item["total_damage"] for item in results]
    cost_values = [item["costs"]["total"] for item in results]
    ros_values = [
        ros for ros in (item_ros(item, base_losses) for item in results) if ros is not None
    ]
    ros_positive = sum(1 for ros in ros_values if ros >= 0)
    ros_negative = sum(1 for ros in ros_values if ros < 0)
    final_index_values = [
        rules.final_index(item["kz_final"], item_ros(item, base_losses), weight_kz, weight_ros)
        for item in results
    ]

    print(f"Basis: {REFERENCE_LABEL}")
    print_section("Gesamtübersicht")
    print(f"Outcomes: {len(results)}")
    print(f"KZ: min {format_kz(min(kz_values))}, max {format_kz(max(kz_values))}")
    print(f"Schaden: min {format_currency(min(damage_values))}, max {format_currency(max(damage_values))}")
    print(f"Kosten: min {format_currency(min(cost_values))}, max {format_currency(max(cost_values))}")
    if ros_values:
        print(f"RoS: min {format_percent(min(ros_values) * 100)}, max {format_percent(max(ros_values) * 100)}")
        print(f"RoS >= 0: {ros_positive} | RoS < 0: {ros_negative}")
    print(f"Final-Index: min {format_currency(min(final_index_values))}, max {format_currency(max(final_index_values))}")

    print_section("Top KZ")
    for item in summarize_top(results, "kz_final", top_n):
        print(f"KZ {format_kz(item['kz_final'])} | Schaden {format_currency(item['total_damage'])} | Kosten {format_currency(item['costs']['total'])}")
        print(f"  Auswahl: {selection_to_string(item['selection'])}")
        print_ros_and_final_index(item, base_losses, weight_kz, weight_ros)

    print_section("Geringster Schaden")
    for item in summarize_bottom(results, "total_damage", top_n):
        print(f"Schaden {format_currency(item['total_damage'])} | KZ {format_kz(item['kz_final'])} | Kosten {format_currency(item['costs']['total'])}")
        print(f"  Auswahl: {selection_to_string(item['selection'])}")
        print_ros_and_final_index(item, base_losses, weight_kz, weight_ros)

    print_section("Niedrigste Kosten")
    for item in summarize_bottom(results, "costs.total", top_n):
        print(f"Kosten {format_currency(item['costs']['total'])} | KZ {format_kz(item['kz_final'])} | Schaden {format_currency(item['total_damage'])}")
        print(f"  Auswahl: {selection_to_string(item['selection'])}")
        print_ros_and_final_index(item, base_losses, weight_kz, weight_ros)

    print_section("Beste Ergebnisse (KZ, Schaden, Kosten)")
    best_ranked = sorted(
        results,
        key=lambda item: -rules.final_index(
            item["kz_final"], item_ros(item, base_losses), weight_kz, weight_ros
        ),
    )[:top_n]
    for item in best_ranked:
        print(f"KZ {format_kz(item['kz_final'])} | Schaden {format_currency(item['total_damage'])} | Kosten {format_currency(item['costs']['total'])}")
        print(f"  Auswahl: {selection_to_string(item['selection'])}")
        print_ros_and_final_index(item, base_losses, weight_kz, weight_ros)

    print_section("Schlechteste Ergebnisse (KZ, Schaden, Kosten)")
    worst_ranked = sorted(
        results,
        key=lambda item: rules.final_index(
            item["kz_final"], item_ros(item, base_losses), weight_kz, weight_ros
        ),
    )[:top_n]
    for item in worst_ranked:
        print(f"KZ {format_kz(item['kz_final'])} | Schaden {format_currency(item['total_damage'])} | Kosten {format_currency(item['costs']['total'])}")
        print(f"  Auswahl: {selection_to_string(item['selection'])}")
        print_ros_and_final_index(item, base_losses, weight_kz, weight_ros)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Auswertung für simulation_results.json.")
    parser.add_argument("--input", default="simulation_results.json", help="Pfad zur Ergebnisdatei.")
    parser.add_argument("--config", default=None, help="Optionaler Pfad zur simulation_config.json (für RoS).")
    parser.add_argument("--top", type=int, default=5, help="Anzahl Top/Bottom-Einträge.")
    parser.add_argument("--weight-kz", type=Fraction, default=Fraction(1), help="Gewichtung für KZ im Final-Index.")
    parser.add_argument("--weight-ros", type=Fraction, default=Fraction(1), help="Gewichtung für RoS im Final-Index.")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    configure_utf8_stdio()
    args = parse_args(argv)
    data = load_results(Path(args.input))
    base_losses = None
    if args.config:
        cfg = load_config(Path(args.config))
        base_losses = rules.base_losses(cfg.waves, cfg.attacks)
    compute_summary(data, args.top, base_losses, args.weight_kz, args.weight_ros)
    return 0
