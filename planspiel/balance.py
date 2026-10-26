"""
Balance-Analyse für das Security-Planspiel.
Simuliert verschiedene Strategien für alle Budget-Tiers und analysiert die Outcomes.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from planspiel import rules
from planspiel.cli import configure_utf8_stdio
from planspiel.config import DEFAULT_CONFIG_PATH, load_config
from planspiel.report import REFERENCE_LABEL

# Präsentationsschwelle für den Balance-Bericht, keine Spielregel; wird in Phase 6 (BAL-08) überprüft.
POSITIVE_KZ_THRESHOLD = 50


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
        "low": [
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
                description="M9+M10 L2 - Falsche Prioritäten",
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
        "medium": [
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
        "high": [
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
                description="M9+M10 L3 - falsche Priorität",
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


def _over_budget_flag(result: Dict) -> str:
    return " [ÜBER BUDGET]" if result["over_budget"] else ""


def _ros_text(ros) -> str:
    return "n/a" if ros is None else f"{ros:.2f}"


def run_analysis(config_path: Path = DEFAULT_CONFIG_PATH):
    cfg = load_config(config_path)
    wave_count = len(cfg.waves)

    print(f"Basis: {REFERENCE_LABEL}")
    print("=" * 100)
    print(f"KOSTEN-REFERENZ (Init + {wave_count}*OPEX)")
    print("=" * 100)
    for level in [1, 2]:
        costs = []
        for mid in cfg.measure_ids:
            total = rules.compute_costs({mid: level}, cfg.measures, wave_count)[2]
            costs.append(f"{mid}={total}")
        print(f"L{level}: {', '.join(costs)}")

    strategies = define_strategies()

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

    for tier_name, tier in cfg.budget_tiers.items():
        print(f"\n{'='*100}")
        print(f"BUDGET-TIER: {tier_name.upper()} (Budget: {tier.budget}k, KZ-Start: {tier.kz_start}, Sev-Mult: {tier.severity_multiplier:.1f})")
        print("=" * 100)

        tier_results = []

        for strategy in all_strategies:
            if not rules.dependencies_satisfied(strategy.selection, cfg.measures):
                print(f"\n[SKIP] {strategy.name}: Abhängigkeiten nicht erfüllt")
                continue

            rec = rules.evaluate_plan(cfg, tier_name, strategy.selection)
            cia = rules.compute_cia(strategy.selection, cfg.measures, cfg.base_cia)
            final_index = rules.final_index(
                rec["kz_final"], rec["ros"], cfg.final_index.weight_kz, cfg.final_index.weight_ros
            )

            result = {
                "strategy": strategy.name,
                "selection": strategy.selection,
                "costs": rec["costs"],
                "cia": cia,
                "kz_final": rec["kz_final"],
                "total_damage": rec["total_damage"],
                "over_budget": rec["over_budget"],
                "ros": rec["ros"],
                "final_index": final_index,
                "waves": rec["waves"],
            }
            tier_results.append(result)

            print(f"\n{strategy.name}")
            print(f"  Kosten: {rec['costs']['total']}k | CIA: C={cia['c']}, I={cia['i']}, A={cia['a']}")

            for w in rec["waves"]:
                bonus = f"+{w['bonus_reduction']}B" if w["bonus_reduction"] > 0 else ""
                events_kz = sum(e.get("kz_delta", 0) for e in w["events"])
                print(f"  W{w['wave_id']}: E={w['e_value']:.1f}, "
                      f"Sev={w['severity']:.1f}{bonus}, Dmg={w['damage']:.0f}k, Evt={events_kz:+d}, KZ={w['kz_after']}")

            kz_status = "OK" if rec["kz_final"] >= POSITIVE_KZ_THRESHOLD else "KRIT"
            print(f"  >> KZ={rec['kz_final']} [{kz_status}]{_over_budget_flag(result)}, Dmg={rec['total_damage']:.0f}k, "
                  f"RoS={_ros_text(rec['ros'])}, Final-Index (vorläufig)={final_index:.1f}")

        results[tier_name] = tier_results

        if tier_results:
            print(f"\n--- {tier_name.upper()} SUMMARY ---")
            best = max(tier_results, key=lambda x: x["final_index"])
            worst = min(tier_results, key=lambda x: x["final_index"])
            print(f"  Best: {best['strategy']} (KZ={best['kz_final']}, Final-Index (vorläufig)={best['final_index']:.1f}){_over_budget_flag(best)}")
            print(f"  Worst: {worst['strategy']} (KZ={worst['kz_final']}, Final-Index (vorläufig)={worst['final_index']:.1f}){_over_budget_flag(worst)}")

    # Summary
    print(f"\n{'='*100}")
    print("TIER-VERGLEICH")
    print("=" * 100)
    print(f"{'Tier':<8} {'Best Strategy':<20} {'KZ':>4} {'Dmg':>8} {'RoS':>7} {'Final-Index (vorläufig)':>24}")
    print("-" * 78)

    for tier_name in ["low", "medium", "high"]:
        if results.get(tier_name):
            best = max(results[tier_name], key=lambda x: x["final_index"])
            print(f"{tier_name:<8} {best['strategy']:<20} {best['kz_final']:>4} {best['total_damage']:>8.0f}k {_ros_text(best['ros']):>7} {best['final_index']:>24.1f}{_over_budget_flag(best)}")
        else:
            print(f"{tier_name:<8} KEINE STRATEGIE AUSWERTBAR!")

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
        positive_kz = [kz for kz in all_kz if kz >= POSITIVE_KZ_THRESHOLD]

        print(f"\n1. KZ-VERTEILUNG:")
        print(f"   - Alle KZ-Werte: {min(all_kz)} bis {max(all_kz)}")
        print(f"   - Positive Outcomes (KZ>={POSITIVE_KZ_THRESHOLD}): {len(positive_kz)}/{len(all_kz)}")

        if len(positive_kz) < len(all_kz) * 0.5:
            print(f"   [PROBLEM] Weniger als 50% positive Outcomes!")

    # Check budget coverage
    print(f"\n2. BUDGET-ABDECKUNG:")
    for tier_name in ["low", "medium", "high"]:
        tier = cfg.budget_tiers[tier_name]
        valid_count = sum(1 for r in results.get(tier_name, []) if not r["over_budget"])
        total_count = len(all_strategies)
        print(f"   {tier_name}: {valid_count}/{total_count} Strategien passen ins Budget ({tier.budget}k)")

    return results


def main(argv=None) -> int:
    configure_utf8_stdio()
    run_analysis()
    return 0
