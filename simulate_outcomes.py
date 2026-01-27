#!/usr/bin/env python3
import argparse
import itertools
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Optional


@dataclass
class Attack:
    attack_id: str
    base_severity: int
    s_unit: int
    kz_unit: int
    cia_impact: Dict[str, int]
    mitigation_cap: int
    allow_recovery: bool


@dataclass
class BonusMeasure:
    measure: str
    min_level: int
    bonus: int
    description: str


@dataclass
class Wave:
    wave_id: int
    name: str
    attack_id: str
    weights: Dict[str, float]
    e_threshold: int
    e_divisor: int
    kz_bonus: int
    kz_malus: int
    bonus_measures: List[BonusMeasure]


@dataclass
class MeasureLevel:
    cia: Dict[str, int]
    init: int
    opex: int
    recovery: float = 0.0


@dataclass
class Measure:
    measure_id: str
    name: str
    levels: Dict[int, MeasureLevel]
    dependencies: List[Dict] = field(default_factory=list)


@dataclass
class BudgetTier:
    name: str
    budget: int
    kz_start: int
    severity_multiplier: float
    e_targets: Dict[int, int]


@dataclass
class Event:
    id: str
    name: str
    description: str
    condition: Dict
    effect_if_met: Dict
    effect_if_not_met: Dict


def load_config(path: Path):
    raw = json.loads(path.read_text())
    base_cia = raw.get("base_cia", {"c": 0, "i": 0, "a": 0})

    budget_tiers = {}
    for name, info in raw["budget_tiers"].items():
        budget_tiers[name] = BudgetTier(
            name=name,
            budget=info["budget"],
            kz_start=info.get("kz_start", 60),
            severity_multiplier=info.get("severity_multiplier", 1.0),
            e_targets={int(k): v for k, v in info["e_targets"].items()},
        )

    attacks = {
        attack_id: Attack(
            attack_id=attack_id,
            base_severity=info["base_severity"],
            s_unit=info["s_unit"],
            kz_unit=info["kz_unit"],
            cia_impact=info["cia_impact"],
            mitigation_cap=info["mitigation_cap"],
            allow_recovery=info["allow_recovery"],
        )
        for attack_id, info in raw["attacks"].items()
    }

    waves = []
    for wave in raw["waves"]:
        bonus_measures = [
            BonusMeasure(
                measure=bm["measure"],
                min_level=bm["min_level"],
                bonus=bm["bonus"],
                description=bm["description"],
            )
            for bm in wave.get("bonus_measures", [])
        ]
        waves.append(Wave(
            wave_id=wave["id"],
            name=wave["name"],
            attack_id=wave["attack_id"],
            weights=wave["weights"],
            e_threshold=wave.get("e_threshold", 18),
            e_divisor=wave.get("e_divisor", 2),
            kz_bonus=wave["kz_bonus"],
            kz_malus=wave["kz_malus"],
            bonus_measures=bonus_measures,
        ))

    measures = {}
    for measure_id, info in raw["measures"].items():
        levels = {
            int(level_id): MeasureLevel(
                cia=level_info["cia"],
                init=level_info["init"],
                opex=level_info["opex"],
                recovery=level_info.get("recovery", 0.0),
            )
            for level_id, level_info in info["levels"].items()
        }
        measures[measure_id] = Measure(
            measure_id=measure_id,
            name=info["name"],
            levels=levels,
            dependencies=info.get("dependencies", []),
        )

    # Load events per wave
    events = {}
    raw_events = raw.get("events", {})
    for wave_key, wave_events in raw_events.items():
        if wave_key.startswith("wave_"):
            wave_id = int(wave_key.split("_")[1])
            events[wave_id] = [
                Event(
                    id=ev["id"],
                    name=ev["name"],
                    description=ev["description"],
                    condition=ev["condition"],
                    effect_if_met=ev["effect_if_met"],
                    effect_if_not_met=ev["effect_if_not_met"],
                )
                for ev in wave_events
            ]

    return raw["default_budget_tier"], budget_tiers, attacks, waves, measures, events, base_cia


def dependencies_satisfied(selection: Dict[str, int], measures: Dict[str, Measure]) -> bool:
    for measure_id, level in selection.items():
        measure = measures[measure_id]
        for dependency in measure.dependencies:
            if level >= dependency["level"]:
                for req in dependency["requires"]:
                    if selection.get(req["measure"], 0) < req["min_level"]:
                        return False
    return True


def compute_cia(selection: Dict[str, int], measures: Dict[str, Measure], base_cia: Dict[str, int]) -> Dict[str, int]:
    totals = {"c": base_cia.get("c", 0), "i": base_cia.get("i", 0), "a": base_cia.get("a", 0)}
    for measure_id, level in selection.items():
        level_data = measures[measure_id].levels[level]
        for key in totals:
            totals[key] += level_data.cia[key]
    return totals


def compute_costs(selection: Dict[str, int], measures: Dict[str, Measure], wave_count: int) -> Tuple[int, int, int]:
    init = 0
    opex_per_wave = 0
    for measure_id, level in selection.items():
        level_data = measures[measure_id].levels[level]
        init += level_data.init
        opex_per_wave += level_data.opex
    total = init + opex_per_wave * wave_count
    return init, opex_per_wave, total


def compute_recovery(selection: Dict[str, int], measures: Dict[str, Measure]) -> float:
    recovery = 0.0
    for measure_id, level in selection.items():
        recovery = max(recovery, measures[measure_id].levels[level].recovery)
    return recovery


def compute_e_value(cia: Dict[str, int], weights: Dict[str, float]) -> float:
    """Compute the E-Value from CIA values and weights."""
    return cia["c"] * weights["c"] + cia["i"] * weights["i"] + cia["a"] * weights["a"]


def compute_mitigation_from_e_value(
    e_value: float,
    wave: Wave,
    selection: Dict[str, int],
) -> Tuple[int, int, List[str]]:
    """
    Compute mitigation based on E-Value and bonus measures.

    Returns:
        base_reduction: Reduction from E-Value exceeding threshold
        bonus_reduction: Additional reduction from bonus measures
        bonus_descriptions: List of active bonus descriptions
    """
    # Base reduction from E-Value
    e_excess = max(0, e_value - wave.e_threshold)
    base_reduction = int(e_excess / wave.e_divisor)

    # Bonus reduction from specific measures
    bonus_reduction = 0
    bonus_descriptions = []
    for bm in wave.bonus_measures:
        if selection.get(bm.measure, 0) >= bm.min_level:
            bonus_reduction += bm.bonus
            bonus_descriptions.append(bm.description)

    return base_reduction, bonus_reduction, bonus_descriptions


def apply_attack(
    selection: Dict[str, int],
    measures: Dict[str, Measure],
    attack: Attack,
    wave: Wave,
    cia: Dict[str, int],
    severity_multiplier: float = 1.0,
) -> Dict:
    """Apply an attack using the new E-Value based mitigation system."""
    e_value = compute_e_value(cia, wave.weights)
    base_reduction, bonus_reduction, bonus_descriptions = compute_mitigation_from_e_value(
        e_value, wave, selection
    )

    total_reduction = base_reduction + bonus_reduction
    capped_reduction = min(attack.mitigation_cap, total_reduction)

    # Apply severity multiplier (larger companies are bigger targets)
    effective_base_severity = int(attack.base_severity * severity_multiplier)
    severity = max(0, effective_base_severity - capped_reduction)

    damage = severity * attack.s_unit
    kz_delta = -severity * attack.kz_unit
    cia_delta = {key: severity * impact for key, impact in attack.cia_impact.items()}

    recovery_factor = 0.0
    if attack.allow_recovery:
        recovery_factor = compute_recovery(selection, measures)
        damage = damage * (1 - recovery_factor)

    return {
        "e_value": e_value,
        "base_reduction": base_reduction,
        "bonus_reduction": bonus_reduction,
        "bonus_descriptions": bonus_descriptions,
        "total_reduction": total_reduction,
        "capped_reduction": capped_reduction,
        "effective_base_severity": effective_base_severity,
        "severity": severity,
        "damage": damage,
        "kz_delta": kz_delta,
        "cia_delta": cia_delta,
        "recovery_factor": recovery_factor,
    }


def count_measures_at_level(selection: Dict[str, int], min_level: int) -> int:
    """Count how many measures are at or above the specified level."""
    return sum(1 for level in selection.values() if level >= min_level)


def check_event_condition(
    event: Event,
    selection: Dict[str, int],
    e_value: float,
) -> bool:
    """Check if an event condition is met."""
    condition = event.condition

    if "measure" in condition:
        measure_level = selection.get(condition["measure"], 0)
        if measure_level < condition["min_level"]:
            return False

    if "e_value_min" in condition:
        if e_value < condition["e_value_min"]:
            return False

    if "measures_at_level_2" in condition:
        count = count_measures_at_level(selection, 2)
        if count < condition["measures_at_level_2"]:
            return False

    return True


def apply_events(
    wave_id: int,
    selection: Dict[str, int],
    events: Dict[int, List[Event]],
    e_value: float,
) -> Tuple[int, int, int, List[Dict]]:
    """
    Apply events for a wave.

    Returns:
        kz_delta: Total KZ change from events
        budget_delta: Total budget change from events
        opex_delta: Total OPEX change from events
        event_results: List of event outcomes
    """
    kz_delta = 0
    budget_delta = 0
    opex_delta = 0
    event_results = []

    wave_events = events.get(wave_id, [])
    for event in wave_events:
        condition_met = check_event_condition(event, selection, e_value)
        effect = event.effect_if_met if condition_met else event.effect_if_not_met

        kz_delta += effect.get("kz_delta", 0)
        budget_delta += effect.get("budget_delta", 0)
        opex_delta += effect.get("opex_delta", 0)

        event_results.append({
            "id": event.id,
            "name": event.name,
            "condition_met": condition_met,
            "effect_description": effect.get("description", ""),
            "kz_delta": effect.get("kz_delta", 0),
            "budget_delta": effect.get("budget_delta", 0),
            "opex_delta": effect.get("opex_delta", 0),
        })

    return kz_delta, budget_delta, opex_delta, event_results


def simulate_selection(
    selection: Dict[str, int],
    budget_tier: BudgetTier,
    waves: List[Wave],
    attacks: Dict[str, Attack],
    measures: Dict[str, Measure],
    events: Dict[int, List[Event]],
    base_cia: Dict[str, int],
    kz_start: int,
) -> Dict:
    kz = kz_start
    total_damage = 0.0
    total_event_opex = 0
    total_event_budget = 0
    cia_mali = {"c": 0, "i": 0, "a": 0}
    per_wave = []

    for wave in waves:
        cia = compute_cia(selection, measures, base_cia)
        attack = attacks[wave.attack_id]

        # Apply attack with new E-Value based mitigation
        attack_result = apply_attack(
            selection, measures, attack, wave, cia,
            severity_multiplier=budget_tier.severity_multiplier
        )
        e_value = attack_result["e_value"]

        # Check E-Target
        e_target = budget_tier.e_targets[wave.wave_id]
        e_reached = e_value >= e_target
        kz += wave.kz_bonus if e_reached else wave.kz_malus

        # Apply attack damage to KZ
        kz += attack_result["kz_delta"]

        # Apply events
        event_kz, event_budget, event_opex, event_results = apply_events(
            wave.wave_id, selection, events, e_value
        )
        kz += event_kz
        total_event_budget += event_budget
        total_event_opex += event_opex

        # Clamp KZ
        kz = max(0, min(100, kz))

        total_damage += attack_result["damage"]
        for key in cia_mali:
            cia_mali[key] += attack_result["cia_delta"][key]

        per_wave.append({
            "wave_id": wave.wave_id,
            "wave_name": wave.name,
            "attack": wave.attack_id,
            "cia": cia,
            "e_value": round(e_value, 1),
            "e_target": e_target,
            "e_reached": e_reached,
            "base_reduction": attack_result["base_reduction"],
            "bonus_reduction": attack_result["bonus_reduction"],
            "bonus_descriptions": attack_result["bonus_descriptions"],
            "total_reduction": attack_result["total_reduction"],
            "capped_reduction": attack_result["capped_reduction"],
            "severity": attack_result["severity"],
            "damage": attack_result["damage"],
            "kz_delta_attack": attack_result["kz_delta"],
            "kz_delta_e_target": wave.kz_bonus if e_reached else wave.kz_malus,
            "events": event_results,
            "kz_after": kz,
        })

    return {
        "selection": selection,
        "kz_final": kz,
        "total_damage": total_damage,
        "total_event_opex": total_event_opex,
        "total_event_budget": total_event_budget,
        "cia_mali": cia_mali,
        "waves": per_wave,
    }


def selection_to_key(selection: Dict[str, int]) -> str:
    return ",".join(f"{measure}:{level}" for measure, level in sorted(selection.items()))


def iter_selections(measure_ids: Iterable[str], level_options: Iterable[int]) -> Iterable[Dict[str, int]]:
    measure_list = list(measure_ids)
    for levels in itertools.product(level_options, repeat=len(measure_list)):
        yield {measure: level for measure, level in zip(measure_list, levels)}


def run_simulation(
    config_path: Path,
    budget_tier_name: str,
    output_path: Path,
    budget_min: Optional[int],
    budget_max: Optional[int],
    budget_utilization: float,
) -> Dict:
    default_budget_tier, budget_tiers, attacks, waves, measures, events, base_cia = load_config(config_path)
    budget_tier = budget_tiers[budget_tier_name or default_budget_tier]
    kz_start = budget_tier.kz_start
    measure_ids = list(measures.keys())
    level_options = [0, 1, 2, 3]
    results = []

    # Use fixed budget value
    tier_budget = budget_tier.budget
    min_cost = budget_min if budget_min is not None else 0
    max_cost = budget_max if budget_max is not None else tier_budget
    utilization_threshold = max_cost * budget_utilization if budget_utilization else None

    for selection in iter_selections(measure_ids, level_options):
        if not dependencies_satisfied(selection, measures):
            continue
        init, opex_per_wave, total_cost = compute_costs(selection, measures, len(waves))
        outcome = simulate_selection(selection, budget_tier, waves, attacks, measures, events, base_cia, kz_start)
        total_cost += outcome["total_event_opex"]
        adjusted_budget = tier_budget + outcome["total_event_budget"]

        if total_cost < min_cost or total_cost > adjusted_budget:
            continue
        if utilization_threshold is not None and total_cost < utilization_threshold:
            continue

        outcome["costs"] = {
            "init": init,
            "opex_per_wave": opex_per_wave,
            "total": total_cost,
            "event_opex": outcome["total_event_opex"],
            "event_budget": outcome["total_event_budget"],
            "budget_available": adjusted_budget,
        }
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
    output_path.write_text(json.dumps(output, indent=2))
    return summary


def parse_args():
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
    return parser.parse_args()


def main():
    args = parse_args()
    summary = run_simulation(
        Path(args.config),
        args.budget_tier,
        Path(args.output),
        args.budget_min,
        args.budget_max,
        args.budget_utilization,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
