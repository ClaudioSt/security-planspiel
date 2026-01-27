#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Balance-Analyse fuer das Security-Planspiel.
Simuliert verschiedene Strategien fuer alle Budget-Tiers und analysiert die Outcomes.
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent))
from simulate_outcomes import (
    load_config, compute_cia, compute_costs, simulate_selection,
    dependencies_satisfied
)


@dataclass
class Strategy:
    name: str
    description: str
    selection: Dict[str, int]


def define_strategies() -> Dict[str, List[Strategy]]:
    """Define test strategies for each budget tier with CORRECT cost calculations."""
    # Verified costs (Init + 3*OPEX):
    # L1: M1=42, M2=26, M3=36, M4=34, M5=46, M6=16, M7=32, M8=28, M9=27, M10=18
    # L2: M1=90, M2=74, M3=86, M4=76, M5=88, M6=42, M7=68, M8=60, M9=61, M10=43

    strategies = {
        "low": [  # Budget: 300k
            Strategy(
                name="Smart Basis",
                description="M2+M3+M4+M5+M6+M7 auf L1",
                selection={
                    "M1": 0, "M2": 1, "M3": 1, "M4": 1, "M5": 1,
                    "M6": 1, "M7": 1, "M8": 0, "M9": 0, "M10": 0
                }
            ),  # 26+36+34+46+16+32=190
            Strategy(
                name="Ransomware Fokus L1",
                description="M3+M4 L2 + Basis",
                selection={
                    "M1": 0, "M2": 1, "M3": 2, "M4": 1, "M5": 0,
                    "M6": 1, "M7": 1, "M8": 0, "M9": 0, "M10": 0
                }
            ),  # 26+86+34+16+32=194
            Strategy(
                name="Minimum Viable",
                description="Basis-Schutz auf L1",
                selection={
                    "M1": 0, "M2": 1, "M3": 1, "M4": 1, "M5": 0,
                    "M6": 1, "M7": 1, "M8": 0, "M9": 0, "M10": 0
                }
            ),  # 26+36+34+16+32=144
            Strategy(
                name="Balanced L1",
                description="M1-M7 alle L1",
                selection={
                    "M1": 1, "M2": 1, "M3": 1, "M4": 1, "M5": 1,
                    "M6": 1, "M7": 1, "M8": 0, "M9": 0, "M10": 0
                }
            ),  # 42+26+36+34+46+16+32=232
            Strategy(
                name="Suboptimal Cloud",
                description="M9+M10 L2 - Falsche Prioritaeten",
                selection={
                    "M1": 0, "M2": 0, "M3": 1, "M4": 1, "M5": 0,
                    "M6": 1, "M7": 0, "M8": 0, "M9": 2, "M10": 2
                }
            ),  # 36+34+16+61+43=190
            # Neue schlechte Strategien
            Strategy(
                name="Nur Backup",
                description="Nur M4 auf L2 - zu einseitig",
                selection={
                    "M1": 0, "M2": 0, "M3": 0, "M4": 2, "M5": 0,
                    "M6": 0, "M7": 0, "M8": 0, "M9": 0, "M10": 0
                }
            ),  # 76
            Strategy(
                name="Keine Detection",
                description="M1+M5+M7 ohne SIEM/EDR",
                selection={
                    "M1": 1, "M2": 0, "M3": 0, "M4": 1, "M5": 1,
                    "M6": 1, "M7": 1, "M8": 0, "M9": 0, "M10": 0
                }
            ),  # 42+34+46+16+32=170
            Strategy(
                name="Alles L1 breit",
                description="M1-M8 alle L1",
                selection={
                    "M1": 1, "M2": 1, "M3": 1, "M4": 1, "M5": 1,
                    "M6": 1, "M7": 1, "M8": 1, "M9": 0, "M10": 0
                }
            ),  # 42+26+36+34+46+16+32+28=260
            Strategy(
                name="OT Fokus Low",
                description="M5+M7 L2",
                selection={
                    "M1": 0, "M2": 1, "M3": 1, "M4": 1, "M5": 2,
                    "M6": 1, "M7": 1, "M8": 0, "M9": 0, "M10": 0
                }
            ),  # 26+36+34+88+16+32=232
        ],
        "medium": [  # Budget: 400k
            Strategy(
                name="Optimal Balanced",
                description="M2+M3+M4+M5+M6 L2",
                selection={
                    "M1": 1, "M2": 2, "M3": 2, "M4": 2, "M5": 0,
                    "M6": 2, "M7": 1, "M8": 1, "M9": 0, "M10": 0
                }
            ),  # 42+74+86+76+42+32+28=380
            Strategy(
                name="Defense Depth",
                description="M2+M3+M4+M6 L2, Rest L1",
                selection={
                    "M1": 1, "M2": 2, "M3": 2, "M4": 2, "M5": 0,
                    "M6": 2, "M7": 1, "M8": 0, "M9": 0, "M10": 0
                }
            ),  # 42+74+86+76+42+32=352
            Strategy(
                name="Ransomware Focus",
                description="M3+M4+M6 L2",
                selection={
                    "M1": 0, "M2": 2, "M3": 2, "M4": 2, "M5": 0,
                    "M6": 2, "M7": 1, "M8": 1, "M9": 0, "M10": 0
                }
            ),  # 74+86+76+42+32+28=338
            Strategy(
                name="OT Protection",
                description="M5+M7 L2 + Basis",
                selection={
                    "M1": 0, "M2": 2, "M3": 1, "M4": 1, "M5": 2,
                    "M6": 1, "M7": 2, "M8": 1, "M9": 0, "M10": 0
                }
            ),  # 74+36+34+88+16+68+28=344
            Strategy(
                name="Suboptimal Mix",
                description="M9+M10 dabei",
                selection={
                    "M1": 1, "M2": 1, "M3": 1, "M4": 1, "M5": 1,
                    "M6": 1, "M7": 1, "M8": 0, "M9": 2, "M10": 2
                }
            ),  # 42+26+36+34+46+16+32+61+43=336
            # Neue Medium Strategien
            Strategy(
                name="Exfil Defense",
                description="M1+M2+M8 L2 fokus",
                selection={
                    "M1": 2, "M2": 2, "M3": 1, "M4": 1, "M5": 0,
                    "M6": 1, "M7": 1, "M8": 2, "M9": 0, "M10": 0
                }
            ),  # 90+74+36+34+16+32+60=342
            Strategy(
                name="Nur L2 Core",
                description="M2+M3+M4 L2 nur",
                selection={
                    "M1": 0, "M2": 2, "M3": 2, "M4": 2, "M5": 0,
                    "M6": 0, "M7": 0, "M8": 0, "M9": 0, "M10": 0
                }
            ),  # 74+86+76=236
            Strategy(
                name="Awareness Heavy",
                description="M6 L2 + breite L1",
                selection={
                    "M1": 1, "M2": 1, "M3": 1, "M4": 1, "M5": 1,
                    "M6": 2, "M7": 1, "M8": 1, "M9": 0, "M10": 0
                }
            ),  # 42+26+36+34+46+42+32+28=286
        ],
        "high": [  # Budget: 500k
            Strategy(
                name="Maximum Coverage",
                description="M1-M8 auf L2",
                selection={
                    "M1": 2, "M2": 2, "M3": 2, "M4": 2, "M5": 1,
                    "M6": 2, "M7": 2, "M8": 1, "M9": 0, "M10": 0
                }
            ),  # 90+74+86+76+46+42+68+28=510 - knapp drueber
            Strategy(
                name="Strong Defense",
                description="M2+M3+M4+M5+M6+M7 L2",
                selection={
                    "M1": 1, "M2": 2, "M3": 2, "M4": 2, "M5": 2,
                    "M6": 2, "M7": 2, "M8": 1, "M9": 0, "M10": 0
                }
            ),  # 42+74+86+76+88+42+68+28=504 - knapp drueber
            Strategy(
                name="OT Festung",
                description="M5+M7 L2 hoch",
                selection={
                    "M1": 1, "M2": 2, "M3": 2, "M4": 2, "M5": 2,
                    "M6": 2, "M7": 2, "M8": 0, "M9": 0, "M10": 0
                }
            ),  # 42+74+86+76+88+42+68=476
            Strategy(
                name="Realistic Max",
                description="Beste Kombi im Budget",
                selection={
                    "M1": 2, "M2": 2, "M3": 2, "M4": 2, "M5": 1,
                    "M6": 2, "M7": 2, "M8": 1, "M9": 0, "M10": 0
                }
            ),  # 90+74+86+76+46+42+68+28=510 - knapp drueber
            Strategy(
                name="Balanced High",
                description="Gute L2-Mischung",
                selection={
                    "M1": 2, "M2": 2, "M3": 2, "M4": 2, "M5": 1,
                    "M6": 2, "M7": 1, "M8": 1, "M9": 0, "M10": 0
                }
            ),  # 90+74+86+76+46+42+32+28=474
            Strategy(
                name="Suboptimal Overkill",
                description="Mit M9+M10",
                selection={
                    "M1": 1, "M2": 2, "M3": 2, "M4": 2, "M5": 1,
                    "M6": 1, "M7": 1, "M8": 0, "M9": 2, "M10": 2
                }
            ),  # 42+74+86+76+46+16+32+61+43=476
            # Neue High Tier Strategien
            Strategy(
                name="Alles L1 High",
                description="Budget verschwendet - nur L1",
                selection={
                    "M1": 1, "M2": 1, "M3": 1, "M4": 1, "M5": 1,
                    "M6": 1, "M7": 1, "M8": 1, "M9": 1, "M10": 1
                }
            ),  # 42+26+36+34+46+16+32+28+27+18=305
            Strategy(
                name="Cloud Fokus High",
                description="M9+M10 L3 - falsche Prioritaet",
                selection={
                    "M1": 1, "M2": 1, "M3": 2, "M4": 2, "M5": 0,
                    "M6": 1, "M7": 1, "M8": 0, "M9": 3, "M10": 3
                }
            ),  # 42+26+86+76+16+32+112+80=470
            Strategy(
                name="Supply Chain Heavy",
                description="M8 L3 fokus",
                selection={
                    "M1": 2, "M2": 2, "M3": 1, "M4": 1, "M5": 1,
                    "M6": 1, "M7": 1, "M8": 3, "M9": 0, "M10": 0
                }
            ),  # 90+74+36+34+46+16+32+118=446
            Strategy(
                name="Nur Detection High",
                description="M2+M3 L3, Rest schwach",
                selection={
                    "M1": 1, "M2": 3, "M3": 3, "M4": 1, "M5": 0,
                    "M6": 1, "M7": 1, "M8": 0, "M9": 0, "M10": 0
                }
            ),  # 42+152+144+34+16+32=420
        ],
    }
    return strategies


def calculate_ros(total_damage: float, total_cost: int, baseline_damage: float) -> float:
    avoided_loss = baseline_damage - total_damage
    if total_cost <= 0:
        return 0.0
    return (avoided_loss - total_cost) / total_cost


def calculate_combined_score(kz_final: int, ros: float, damage: float) -> float:
    kz_component = kz_final * 0.6
    ros_normalized = max(0, min(100, (ros + 1) * 33.33))
    ros_component = ros_normalized * 0.3
    damage_normalized = max(0, min(100, 100 - (damage / 5000)))
    damage_component = damage_normalized * 0.1
    return kz_component + ros_component + damage_component


def run_analysis():
    config_path = Path(__file__).parent / "simulation_config.json"
    default_tier, budget_tiers, attacks, waves, measures, events, base_cia = load_config(config_path)

    # First: Calculate cost reference
    print("=" * 100)
    print("KOSTEN-REFERENZ (Init + 3*OPEX)")
    print("=" * 100)
    for level in [1, 2]:
        costs = []
        for mid in [f"M{i}" for i in range(1, 11)]:
            m = measures[mid]
            l = m.levels[level]
            total = l.init + l.opex * 3
            costs.append(f"{mid}={total}")
        print(f"L{level}: {', '.join(costs)}")

    strategies = define_strategies()
    no_measures = {f"M{i}": 0 for i in range(1, 11)}

    results = {}

    print("\n" + "=" * 100)
    print("BALANCE-ANALYSE: Security-Planspiel")
    print("=" * 100)

    # Combine all strategies into one list
    all_strategies = []
    for tier_strats in strategies.values():
        for s in tier_strats:
            if s.name not in [x.name for x in all_strategies]:
                all_strategies.append(s)

    for tier_name, tier in budget_tiers.items():
        print(f"\n{'='*100}")
        print(f"BUDGET-TIER: {tier_name.upper()} (Budget: {tier.budget}k, KZ-Start: {tier.kz_start}, Sev-Mult: {tier.severity_multiplier})")
        print("=" * 100)

        baseline_outcome = simulate_selection(
            no_measures, tier, waves, attacks, measures, events, base_cia, tier.kz_start
        )
        baseline_damage = baseline_outcome["total_damage"]
        baseline_kz = baseline_outcome["kz_final"]

        print(f"\nBaseline (keine Massnahmen): KZ={baseline_kz}, Schaden={baseline_damage:.0f}k")
        print("-" * 100)

        tier_results = []

        for strategy in all_strategies:
            if not dependencies_satisfied(strategy.selection, measures):
                print(f"\n[SKIP] {strategy.name}: Dependencies nicht erfuellt")
                continue

            init, opex, total_cost = compute_costs(strategy.selection, measures, len(waves))

            if total_cost > tier.budget:
                print(f"\n[SKIP] {strategy.name}: Kosten ({total_cost}k) > Budget ({tier.budget}k)")
                continue

            outcome = simulate_selection(
                strategy.selection, tier, waves, attacks, measures, events, base_cia, tier.kz_start
            )
            total_cost += outcome["total_event_opex"]

            ros = calculate_ros(outcome["total_damage"], total_cost, baseline_damage)
            combined = calculate_combined_score(outcome["kz_final"], ros, outcome["total_damage"])
            cia = compute_cia(strategy.selection, measures, base_cia)

            result = {
                "strategy": strategy.name,
                "selection": strategy.selection,
                "costs": {"init": init, "opex": opex, "total": total_cost},
                "cia": cia,
                "kz_final": outcome["kz_final"],
                "total_damage": outcome["total_damage"],
                "ros": ros,
                "combined_score": combined,
                "waves": outcome["waves"],
            }
            tier_results.append(result)

            print(f"\n{strategy.name}")
            print(f"  Kosten: {total_cost}k | CIA: C={cia['c']}, I={cia['i']}, A={cia['a']}")

            for w in outcome["waves"]:
                e_status = "[OK]" if w["e_reached"] else "[X]"
                bonus = f"+{w['bonus_reduction']}B" if w["bonus_reduction"] > 0 else ""
                events_kz = sum(e.get("kz_delta", 0) for e in w["events"])
                print(f"  W{w['wave_id']}: E={w['e_value']:.1f}/{w['e_target']} {e_status}, "
                      f"Sev={w['severity']}{bonus}, Dmg={w['damage']:.0f}k, Evt={events_kz:+d}, KZ={w['kz_after']}")

            kz_status = "OK" if outcome["kz_final"] >= 50 else "KRIT"
            print(f"  >> KZ={outcome['kz_final']} [{kz_status}], Dmg={outcome['total_damage']:.0f}k, ROS={ros:.2f}, Score={combined:.1f}")

        results[tier_name] = tier_results

        if tier_results:
            print(f"\n--- {tier_name.upper()} SUMMARY ---")
            best = max(tier_results, key=lambda x: x["combined_score"])
            worst = min(tier_results, key=lambda x: x["combined_score"])
            print(f"  Best: {best['strategy']} (KZ={best['kz_final']}, Score={best['combined_score']:.1f})")
            print(f"  Worst: {worst['strategy']} (KZ={worst['kz_final']}, Score={worst['combined_score']:.1f})")

    # Summary
    print(f"\n{'='*100}")
    print("TIER-VERGLEICH")
    print("=" * 100)
    print(f"{'Tier':<8} {'Best Strategy':<20} {'KZ':>4} {'Dmg':>8} {'ROS':>7} {'Score':>6}")
    print("-" * 60)

    for tier_name in ["low", "medium", "high"]:
        if results.get(tier_name):
            best = max(results[tier_name], key=lambda x: x["combined_score"])
            print(f"{tier_name:<8} {best['strategy']:<20} {best['kz_final']:>4} {best['total_damage']:>8.0f}k {best['ros']:>7.2f} {best['combined_score']:>6.1f}")
        else:
            print(f"{tier_name:<8} KEINE STRATEGIE PASST INS BUDGET!")

    # Balance Analysis
    print(f"\n{'='*100}")
    print("BALANCE PROBLEME")
    print("=" * 100)

    all_valid = []
    for tier_name in ["low", "medium", "high"]:
        if results.get(tier_name):
            all_valid.extend([(tier_name, r) for r in results[tier_name]])

    if all_valid:
        all_kz = [r["kz_final"] for _, r in all_valid]
        positive_kz = [kz for kz in all_kz if kz >= 50]

        print(f"\n1. KZ-VERTEILUNG:")
        print(f"   - Alle KZ-Werte: {min(all_kz)} bis {max(all_kz)}")
        print(f"   - Positive Outcomes (KZ>=50): {len(positive_kz)}/{len(all_kz)}")

        if len(positive_kz) < len(all_kz) * 0.5:
            print(f"   [PROBLEM] Weniger als 50% positive Outcomes!")

    # Check budget coverage
    print(f"\n2. BUDGET-ABDECKUNG:")
    for tier_name in ["low", "medium", "high"]:
        tier = budget_tiers[tier_name]
        valid_count = len(results.get(tier_name, []))
        total_count = len(all_strategies)
        print(f"   {tier_name}: {valid_count}/{total_count} Strategien passen ins Budget ({tier.budget}k)")

    return results


if __name__ == "__main__":
    results = run_analysis()
