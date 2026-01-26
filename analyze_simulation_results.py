#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional


def load_results(path: Path) -> Dict:
    return json.loads(path.read_text())


def load_base_losses(config_path: Optional[Path]) -> Optional[float]:
    if config_path is None:
        return None
    raw = json.loads(config_path.read_text())
    attacks = raw.get("attacks", {})
    waves = raw.get("waves", [])
    base_losses = 0.0
    for wave in waves:
        attack_id = wave["attack_id"]
        attack = attacks[attack_id]
        base_losses += attack["base_severity"] * attack["s_unit"]
    return base_losses


def format_currency(value: float) -> str:
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


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


def compute_final_index(kz_final: int, ros: Optional[float], weight_kz: float, weight_ros: float) -> float:
    if ros is None:
        return kz_final
    return (weight_kz * kz_final) + (weight_ros * (ros * 100))


def compute_summary(data: Dict, top_n: int, base_losses: Optional[float], weight_kz: float, weight_ros: float):
    results = data.get("results", [])
    if not results:
        print("Keine Ergebnisse gefunden.")
        return

    kz_values = [item["kz_final"] for item in results]
    damage_values = [item["total_damage"] for item in results]
    cost_values = [item["costs"]["total"] for item in results]
    ros_values = []
    ros_positive = 0
    ros_negative = 0
    if base_losses is not None:
        for item in results:
            avoided_losses = base_losses - item["total_damage"]
            ros = (avoided_losses - item["costs"]["total"]) / item["costs"]["total"]
            ros_values.append(ros)
            if ros >= 0:
                ros_positive += 1
            else:
                ros_negative += 1
    final_index_values = []
    for item in results:
        ros = None
        if base_losses is not None:
            avoided_losses = base_losses - item["total_damage"]
            ros = (avoided_losses - item["costs"]["total"]) / item["costs"]["total"]
        final_index_values.append(compute_final_index(item["kz_final"], ros, weight_kz, weight_ros))

    print_section("Gesamtübersicht")
    print(f"Outcomes: {len(results)}")
    print(f"KZ: min {min(kz_values)}, max {max(kz_values)}")
    print(f"Schaden: min {format_currency(min(damage_values))}, max {format_currency(max(damage_values))}")
    print(f"Kosten: min {format_currency(min(cost_values))}, max {format_currency(max(cost_values))}")
    if ros_values:
        print(f"RoS: min {format_percent(min(ros_values) * 100)}, max {format_percent(max(ros_values) * 100)}")
        print(f"RoS >= 0: {ros_positive} | RoS < 0: {ros_negative}")
    print(f"Final-Index: min {format_currency(min(final_index_values))}, max {format_currency(max(final_index_values))}")

    print_section("Top KZ")
    for item in summarize_top(results, "kz_final", top_n):
        print(f"KZ {item['kz_final']} | Schaden {format_currency(item['total_damage'])} | Kosten {format_currency(item['costs']['total'])}")
        print(f"  Auswahl: {selection_to_string(item['selection'])}")
        if base_losses is not None:
            avoided_losses = base_losses - item["total_damage"]
            ros = (avoided_losses - item["costs"]["total"]) / item["costs"]["total"]
            print(f"  RoS: {format_percent(ros * 100)}")
            final_index = compute_final_index(item["kz_final"], ros, weight_kz, weight_ros)
            print(f"  Final-Index: {format_currency(final_index)}")

    print_section("Geringster Schaden")
    for item in summarize_bottom(results, "total_damage", top_n):
        print(f"Schaden {format_currency(item['total_damage'])} | KZ {item['kz_final']} | Kosten {format_currency(item['costs']['total'])}")
        print(f"  Auswahl: {selection_to_string(item['selection'])}")
        if base_losses is not None:
            avoided_losses = base_losses - item["total_damage"]
            ros = (avoided_losses - item["costs"]["total"]) / item["costs"]["total"]
            print(f"  RoS: {format_percent(ros * 100)}")
            final_index = compute_final_index(item["kz_final"], ros, weight_kz, weight_ros)
            print(f"  Final-Index: {format_currency(final_index)}")

    print_section("Niedrigste Kosten")
    for item in summarize_bottom(results, "costs.total", top_n):
        print(f"Kosten {format_currency(item['costs']['total'])} | KZ {item['kz_final']} | Schaden {format_currency(item['total_damage'])}")
        print(f"  Auswahl: {selection_to_string(item['selection'])}")
        if base_losses is not None:
            avoided_losses = base_losses - item["total_damage"]
            ros = (avoided_losses - item["costs"]["total"]) / item["costs"]["total"]
            print(f"  RoS: {format_percent(ros * 100)}")
            final_index = compute_final_index(item["kz_final"], ros, weight_kz, weight_ros)
            print(f"  Final-Index: {format_currency(final_index)}")

    print_section("Beste Ergebnisse (KZ, Schaden, Kosten)")
    best_ranked = sorted(
        results,
        key=lambda item: -compute_final_index(
            item["kz_final"],
            (base_losses - item["total_damage"]) / item["costs"]["total"] - 1 if base_losses is not None else None,
            weight_kz,
            weight_ros,
        ),
    )[:top_n]
    for item in best_ranked:
        print(f"KZ {item['kz_final']} | Schaden {format_currency(item['total_damage'])} | Kosten {format_currency(item['costs']['total'])}")
        print(f"  Auswahl: {selection_to_string(item['selection'])}")
        if base_losses is not None:
            avoided_losses = base_losses - item["total_damage"]
            ros = (avoided_losses - item["costs"]["total"]) / item["costs"]["total"]
            print(f"  RoS: {format_percent(ros * 100)}")
            final_index = compute_final_index(item["kz_final"], ros, weight_kz, weight_ros)
            print(f"  Final-Index: {format_currency(final_index)}")

    print_section("Schlechteste Ergebnisse (KZ, Schaden, Kosten)")
    worst_ranked = sorted(
        results,
        key=lambda item: compute_final_index(
            item["kz_final"],
            (base_losses - item["total_damage"]) / item["costs"]["total"] - 1 if base_losses is not None else None,
            weight_kz,
            weight_ros,
        ),
    )[:top_n]
    for item in worst_ranked:
        print(f"KZ {item['kz_final']} | Schaden {format_currency(item['total_damage'])} | Kosten {format_currency(item['costs']['total'])}")
        print(f"  Auswahl: {selection_to_string(item['selection'])}")
        if base_losses is not None:
            avoided_losses = base_losses - item["total_damage"]
            ros = (avoided_losses - item["costs"]["total"]) / item["costs"]["total"]
            print(f"  RoS: {format_percent(ros * 100)}")
            final_index = compute_final_index(item["kz_final"], ros, weight_kz, weight_ros)
            print(f"  Final-Index: {format_currency(final_index)}")


def parse_args():
    parser = argparse.ArgumentParser(description="Auswertung für simulation_results.json.")
    parser.add_argument("--input", default="simulation_results.json", help="Pfad zur Ergebnisdatei.")
    parser.add_argument("--config", default=None, help="Optionaler Pfad zur simulation_config.json (für RoS).")
    parser.add_argument("--top", type=int, default=5, help="Anzahl Top/Bottom-Einträge.")
    parser.add_argument("--weight-kz", type=float, default=1.0, help="Gewichtung für KZ im Final-Index.")
    parser.add_argument("--weight-ros", type=float, default=1.0, help="Gewichtung für RoS im Final-Index.")
    return parser.parse_args()


def main():
    args = parse_args()
    data = load_results(Path(args.input))
    base_losses = load_base_losses(Path(args.config)) if args.config else None
    compute_summary(data, args.top, base_losses, args.weight_kz, args.weight_ros)


if __name__ == "__main__":
    main()
