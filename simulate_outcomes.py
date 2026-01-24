#!/usr/bin/env python3
import argparse
import itertools
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


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
class Wave:
    wave_id: int
    name: str
    attack_id: str
    weights: Dict[str, float]
    kz_bonus: int
    kz_malus: int


@dataclass
class MeasureLevel:
    cia: Dict[str, int]
    init: int
    opex: int
    mitigation: Dict[str, int]
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
    kz_start: int
    e_targets: Dict[int, int]
    budget_range: Tuple[int, int]


def load_config(path: Path):
    raw = json.loads(path.read_text())
    budget_tiers = {}
    for name, info in raw["budget_tiers"].items():
        budget_tiers[name] = BudgetTier(
            name=name,
            kz_start=info["kz_start"],
            e_targets={int(k): v for k, v in info["e_targets"].items()},
            budget_range=tuple(info["range"]),
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
    waves = [
        Wave(
            wave_id=wave["id"],
            name=wave["name"],
            attack_id=wave["attack_id"],
            weights=wave["weights"],
            kz_bonus=wave["kz_bonus"],
            kz_malus=wave["kz_malus"],
        )
        for wave in raw["waves"]
    ]
    measures = {}
    for measure_id, info in raw["measures"].items():
        levels = {
            int(level_id): MeasureLevel(
                cia=level_info["cia"],
                init=level_info["init"],
                opex=level_info["opex"],
                mitigation=level_info["mitigation"],
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
    events = raw["events"]
    return raw["default_budget_tier"], budget_tiers, attacks, waves, measures, events


def dependencies_satisfied(selection: Dict[str, int], measures: Dict[str, Measure]) -> bool:
    for measure_id, level in selection.items():
        measure = measures[measure_id]
        for dependency in measure.dependencies:
            if level >= dependency["level"]:
                for req in dependency["requires"]:
                    if selection.get(req["measure"], 0) < req["min_level"]:
                        return False
    return True


def compute_cia(selection: Dict[str, int], measures: Dict[str, Measure]) -> Dict[str, int]:
    totals = {"c": 0, "i": 0, "a": 0}
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


def compute_mitigation(selection: Dict[str, int], measures: Dict[str, Measure], attack_id: str) -> int:
    mitigation_sum = 0
    for measure_id, level in selection.items():
        level_data = measures[measure_id].levels[level]
        mitigation_sum += level_data.mitigation.get(attack_id, 0)
    return mitigation_sum


def apply_attack(selection: Dict[str, int], measures: Dict[str, Measure], attack: Attack) -> Dict[str, float]:
    mitigation_sum = compute_mitigation(selection, measures, attack.attack_id)
    reduction = max(0, -mitigation_sum)
    capped = min(attack.mitigation_cap, reduction)
    severity = max(0, attack.base_severity - capped)
    damage = severity * attack.s_unit
    kz_delta = -severity * attack.kz_unit
    cia_delta = {key: severity * impact for key, impact in attack.cia_impact.items()}
    recovery_factor = 0.0
    if attack.allow_recovery:
        recovery_factor = compute_recovery(selection, measures)
        damage = damage * (1 - recovery_factor)
    return {
        "severity": severity,
        "damage": damage,
        "kz_delta": kz_delta,
        "cia_delta": cia_delta,
        "recovery_factor": recovery_factor,
    }


def apply_events(
    wave_id: int,
    kz: int,
    selection: Dict[str, int],
    events: Dict,
    e_reached_prev: bool,
    budget: int,
) -> Tuple[int, int, int]:
    kz_delta = 0
    budget_delta = 0
    opex_delta = 0
    if wave_id == events["oem_audit"]["trigger_wave"]:
        kz_delta += events["oem_audit"]["kz_bonus"] if e_reached_prev else events["oem_audit"]["kz_malus"]
    if wave_id == events["staff_turnover"]["trigger_wave"]:
        if selection.get("M6", 0) < 2:
            kz_delta += events["staff_turnover"]["kz_delta"]
            opex_delta += events["staff_turnover"]["opex_delta"]
    if wave_id == events["gdpr_bonus"]["trigger_wave"]:
        if selection.get("M1", 0) >= 2 and selection.get("M2", 0) >= 2:
            kz_delta += events["gdpr_bonus"]["kz_delta"]
            budget_delta += events["gdpr_bonus"]["budget_delta"]
    return kz + kz_delta, budget + budget_delta, opex_delta


def simulate_selection(selection: Dict[str, int], budget_tier: BudgetTier, waves: List[Wave], attacks: Dict[str, Attack], measures: Dict[str, Measure], events: Dict) -> Dict:
    kz = budget_tier.kz_start
    budget = 0
    total_damage = 0.0
    event_opex_penalty = 0
    event_budget_delta = 0
    cia_mali = {"c": 0, "i": 0, "a": 0}
    per_wave = []
    e_reached_prev = False

    for wave in waves:
        if wave.wave_id > 1:
            kz, budget, opex_delta = apply_events(wave.wave_id, kz, selection, events, e_reached_prev, budget)
            event_opex_penalty += opex_delta
            event_budget_delta = budget
        cia = compute_cia(selection, measures)
        e_value = cia["c"] * wave.weights["c"] + cia["i"] * wave.weights["i"] + cia["a"] * wave.weights["a"]
        e_target = budget_tier.e_targets[wave.wave_id]
        e_reached = e_value >= e_target
        kz += wave.kz_bonus if e_reached else wave.kz_malus
        attack = attacks[wave.attack_id]
        attack_result = apply_attack(selection, measures, attack)
        kz += attack_result["kz_delta"]
        kz = max(0, min(100, kz))
        total_damage += attack_result["damage"]
        for key in cia_mali:
            cia_mali[key] += attack_result["cia_delta"][key]
        per_wave.append(
            {
                "wave_id": wave.wave_id,
                "attack": wave.attack_id,
                "e_value": e_value,
                "e_target": e_target,
                "e_reached": e_reached,
                "kz_after": kz,
                "severity": attack_result["severity"],
                "damage": attack_result["damage"],
                "kz_delta": attack_result["kz_delta"],
            }
        )
        e_reached_prev = e_reached
    return {
        "selection": selection,
        "kz_final": kz,
        "total_damage": total_damage,
        "event_opex_penalty": event_opex_penalty,
        "event_budget_delta": event_budget_delta,
        "cia_mali": cia_mali,
        "waves": per_wave,
    }


def selection_to_key(selection: Dict[str, int]) -> str:
    return ",".join(f"{measure}:{level}" for measure, level in sorted(selection.items()))


def iter_selections(measure_ids: Iterable[str], level_options: Iterable[int]) -> Iterable[Dict[str, int]]:
    for levels in itertools.product(level_options, repeat=len(list(measure_ids))):
        yield {measure: level for measure, level in zip(measure_ids, levels)}


def run_simulation(config_path: Path, budget_tier_name: str, output_path: Path) -> Dict:
    default_budget_tier, budget_tiers, attacks, waves, measures, events = load_config(config_path)
    budget_tier = budget_tiers[budget_tier_name or default_budget_tier]
    measure_ids = list(measures.keys())
    level_options = [0, 1, 2, 3]
    results = []
    for selection in iter_selections(measure_ids, level_options):
        if not dependencies_satisfied(selection, measures):
            continue
        init, opex_per_wave, total_cost = compute_costs(selection, measures, len(waves))
        outcome = simulate_selection(selection, budget_tier, waves, attacks, measures, events)
        total_cost += outcome["event_opex_penalty"]
        outcome["costs"] = {
            "init": init,
            "opex_per_wave": opex_per_wave,
            "total": total_cost,
            "event_opex_penalty": outcome["event_opex_penalty"],
            "event_budget_delta": outcome["event_budget_delta"],
        }
        results.append(outcome)
    results.sort(key=lambda item: (-item["kz_final"], item["total_damage"]))
    summary = {
        "total_outcomes": len(results),
        "budget_tier": budget_tier.name,
        "budget_range": budget_tier.budget_range,
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
    return parser.parse_args()


def main():
    args = parse_args()
    summary = run_simulation(Path(args.config), args.budget_tier, Path(args.output))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
