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
    kz_at_full_damage: float
    kz_at_full_mitigation: float
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
    type: str
    params: Dict


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
            kz_at_full_damage=info["kz_at_full_damage"],
            kz_at_full_mitigation=info["kz_at_full_mitigation"],
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
                    type=ev["type"],
                    params={k: v for k, v in ev.items() if k not in ("id", "name", "description", "type")},
                )
                for ev in wave_events
            ]

    final_events = [
        Event(
            id=ev["id"],
            name=ev["name"],
            description=ev["description"],
            type=ev["type"],
            params={k: v for k, v in ev.items() if k not in ("id", "name", "description", "type")},
        )
        for ev in raw.get("final_events", [])
    ]

    expectation_malus = {
        k: v for k, v in raw.get("budget_tier_expectation_malus", {}).items()
        if k != "description"
    }

    return raw["default_budget_tier"], budget_tiers, attacks, waves, measures, events, base_cia, final_events, expectation_malus


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


def compute_bonus_reduction(
    wave: Wave,
    selection: Dict[str, int],
) -> Tuple[int, List[str]]:
    """Bonus reduction from specific measures (per Angriffs-Arbeitsblatt: 'Gesamtbonus')."""
    bonus_reduction = 0
    bonus_descriptions = []
    for bm in wave.bonus_measures:
        if selection.get(bm.measure, 0) >= bm.min_level:
            bonus_reduction += bm.bonus
            bonus_descriptions.append(bm.description)

    return bonus_reduction, bonus_descriptions


def apply_attack(
    selection: Dict[str, int],
    measures: Dict[str, Measure],
    attack: Attack,
    wave: Wave,
    cia: Dict[str, int],
    severity_multiplier: float = 1.0,
) -> Dict:
    """
    Apply an attack exactly as specified on the printed Angriffs-Arbeitsblatt
    (z.B. Angriff-1_Ransomware.docx):

        Gesamtreduktion = E-Wert + Gesamtbonus
        Fall 1: Gesamtreduktion <= e_threshold              -> volle Basisschadenswirkung
        Fall 2: Gesamtreduktion >= e_threshold + mitigation_cap -> kein Schaden
        Fall 3: dazwischen                                  -> lineare Interpolation

    No flooring/division is applied to E-Wert or Gesamtreduktion - the formula
    matches the paper worksheet number-for-number.
    """
    e_value = compute_e_value(cia, wave.weights)
    bonus_reduction, bonus_descriptions = compute_bonus_reduction(wave, selection)

    gesamtreduktion = e_value + bonus_reduction
    reduktion_ueber_schwelle = min(
        attack.mitigation_cap, max(0, gesamtreduktion - wave.e_threshold)
    )

    # Apply severity multiplier (larger companies are bigger targets)
    effective_base_severity = attack.base_severity * severity_multiplier
    severity = max(0.0, effective_base_severity - reduktion_ueber_schwelle)

    damage = severity * attack.s_unit

    # KZ-Delta linear zwischen den auf dem Arbeitsblatt festgelegten Endpunkten
    # interpoliert (Fall 1: redu=0 -> kz_at_full_damage, Fall 2: redu=cap ->
    # kz_at_full_mitigation), statt der im Word-Dokument widersprüchlichen
    # Fall-3-Subformel (deren Steigung bei Welle 2/3 nicht zu den eigenen
    # Fall-1/Fall-2-Werten passt).
    mitigation_fraction = (
        reduktion_ueber_schwelle / attack.mitigation_cap if attack.mitigation_cap else 0.0
    )
    kz_delta = attack.kz_at_full_damage + mitigation_fraction * (
        attack.kz_at_full_mitigation - attack.kz_at_full_damage
    )
    cia_delta = {key: severity * impact for key, impact in attack.cia_impact.items()}

    recovery_factor = 0.0
    if attack.allow_recovery:
        recovery_factor = compute_recovery(selection, measures)
        damage = damage * (1 - recovery_factor)

    return {
        "e_value": e_value,
        "bonus_reduction": bonus_reduction,
        "bonus_descriptions": bonus_descriptions,
        "gesamtreduktion": gesamtreduktion,
        "capped_reduction": reduktion_ueber_schwelle,
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


def _tier_lookup(value: float, tiers: List[List[float]]) -> float:
    """
    tiers: list of [min_inclusive, value], sorted ascending by min_inclusive.
    Returns the value of the highest tier whose min_inclusive <= value.
    """
    result = tiers[0][1]
    for min_inclusive, tier_value in tiers:
        if value >= min_inclusive:
            result = tier_value
    return result


def evaluate_event(
    event: Event,
    selection: Dict[str, int],
    remaining_budget: Optional[float] = None,
    total_budget: Optional[float] = None,
) -> Tuple[int, int, int, str]:
    """
    Evaluate a single event exactly as specified on Events_Security-Game.pptx.

    Returns: (kz_delta, opex_delta, budget_delta, effect_description)
    """
    p = event.params

    if event.type == "noop":
        # "Kurswechsel": freier Maßnahmenwechsel mit Kostendifferenz - eine
        # Strategieentscheidung der Teams, die sich nicht in der statischen
        # Maßnahmen-Enumeration abbilden laesst. Wird hier kostenneutral (0)
        # angenommen.
        return 0, 0, 0, "Kurswechsel: kostenneutral angenommen (Spielerentscheidung, nicht simuliert)"

    if event.type == "flat_budget":
        return 0, 0, p["budget_delta"], event.description

    if event.type == "opex_discount_per_active_measure":
        active = count_measures_at_level(selection, 1)
        opex_delta = p["opex_per_measure"] * active
        return 0, opex_delta, 0, f"{active} aktive Maßnahmen x {p['opex_per_measure']}k€"

    if event.type == "checklist_tier":
        count = sum(
            1 for m in p["measures"]
            if selection.get(m, 0) >= p["min_level"]
        )
        kz_delta = _tier_lookup(count, p["tiers"])
        return kz_delta, 0, 0, f"{count}/{len(p['measures'])} Maßnahmen erfüllt"

    if event.type == "measure_level_tier":
        level = selection.get(p["measure"], 0)
        kz_delta = p["tiers"][str(level)]
        return kz_delta, 0, 0, f"{p['measure']} auf Level {level}"

    if event.type == "level_bonus_per_measure":
        count = count_measures_at_level(selection, p["level"])
        kz_delta = count * p["kz_per_measure"]
        return kz_delta, 0, 0, f"{count} Maßnahmen auf Level {p['level']}"

    if event.type == "and_condition":
        all_met = all(
            (selection.get(c["measure"], 0) >= c["min_level"])
            if "min_level" in c
            else (selection.get(c["measure"], 0) == c["level_eq"])
            for c in p["clauses"]
        )
        kz_delta = p["kz_delta"] if all_met else 0
        return kz_delta, 0, 0, "Bedingung erfüllt" if all_met else "Bedingung nicht erfüllt"

    if event.type == "final_budget_tier":
        if p.get("relative") and total_budget:
            value = 100 * remaining_budget / total_budget
            kz_delta = _tier_lookup(value, p["tiers"])
            return kz_delta, 0, 0, f"Restbudget {value:.0f}% von {total_budget:.0f}k€"
        kz_delta = _tier_lookup(remaining_budget, p["tiers"])
        return kz_delta, 0, 0, f"Restbudget {remaining_budget:.0f}k€"

    raise ValueError(f"Unknown event type: {event.type}")


def apply_events(
    wave_id: int,
    selection: Dict[str, int],
    events: Dict[int, List[Event]],
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
        ev_kz, ev_opex, ev_budget, description = evaluate_event(event, selection)

        kz_delta += ev_kz
        budget_delta += ev_budget
        opex_delta += ev_opex

        event_results.append({
            "id": event.id,
            "name": event.name,
            "effect_description": description,
            "kz_delta": ev_kz,
            "budget_delta": ev_budget,
            "opex_delta": ev_opex,
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
            wave.wave_id, selection, events
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
            "bonus_reduction": attack_result["bonus_reduction"],
            "bonus_descriptions": attack_result["bonus_descriptions"],
            "gesamtreduktion": round(attack_result["gesamtreduktion"], 1),
            "capped_reduction": round(attack_result["capped_reduction"], 1),
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
    default_budget_tier, budget_tiers, attacks, waves, measures, events, base_cia, final_events, expectation_malus = load_config(config_path)
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

        remaining_budget = adjusted_budget - total_cost
        final_event_results = []
        for event in final_events:
            ev_kz, _, _, description = evaluate_event(
                event, selection, remaining_budget=remaining_budget, total_budget=adjusted_budget
            )
            outcome["kz_final"] = max(0, min(100, outcome["kz_final"] + ev_kz))
            final_event_results.append({
                "id": event.id, "name": event.name,
                "effect_description": description, "kz_delta": ev_kz,
            })

        malus = expectation_malus.get(budget_tier.name, 0)
        if malus:
            outcome["kz_final"] = max(0, min(100, outcome["kz_final"] + malus))
            final_event_results.append({
                "id": "budget_tier_expectation_malus", "name": "Erwartungshaltung",
                "effect_description": f"Hoeheres Budget-Tier ({budget_tier.name}) -> hoehere Erwartung",
                "kz_delta": malus,
            })
        outcome["final_events"] = final_event_results

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
