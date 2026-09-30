"""Adapter between the golden tests and the simulation code (D-05).

Step 1 (this file): composes the legacy `run_simulation` loop body from `simulate_outcomes`.
Later plans swap the body to `planspiel` and change `STAGE`; the golden tests only call this module.
"""
import itertools
from pathlib import Path
from typing import NamedTuple

from simulate_outcomes import (
    compute_costs,
    dependencies_satisfied,
    evaluate_event,
    simulate_selection,
)
from simulate_outcomes import load_config as _legacy_load_config

from tests.support import CONFIG_PATH

STAGE = "legacy-float"

LEGACY_RECORD_KEYS = (
    "selection",
    "kz_final",
    "total_damage",
    "total_event_opex",
    "total_event_budget",
    "cia_mali",
    "waves",
    "final_events",
    "costs",
)

LEVELS = 4


class Config(NamedTuple):
    default_budget_tier: str
    budget_tiers: dict
    attacks: dict
    waves: list
    measures: dict
    events: dict
    base_cia: dict
    final_events: list


def load_config(path: Path = CONFIG_PATH) -> Config:
    return Config(*_legacy_load_config(path))


def measure_ids(cfg: Config) -> list:
    return list(cfg.measures.keys())


def code_of(cfg: Config, selection: dict) -> str:
    return "".join(str(selection[m]) for m in measure_ids(cfg))


def selection_of(cfg: Config, code: str) -> dict:
    return {m: int(digit) for m, digit in zip(measure_ids(cfg), code)}


def iter_codes(cfg: Config):
    for levels in itertools.product(range(LEVELS), repeat=len(cfg.measures)):
        yield "".join(map(str, levels))


def _base_losses(cfg: Config) -> float:
    base_losses = 0.0
    for wave in cfg.waves:
        attack = cfg.attacks[wave.attack_id]
        base_losses += attack.base_severity * attack.s_unit
    return base_losses


def evaluate(cfg: Config, tier_name: str, selection: dict) -> dict:
    if not dependencies_satisfied(selection, cfg.measures):
        return {"valid": False}

    tier = cfg.budget_tiers[tier_name]
    init, opex_per_wave, total_cost = compute_costs(selection, cfg.measures, len(cfg.waves))
    outcome = simulate_selection(
        selection, tier, cfg.waves, cfg.attacks, cfg.measures, cfg.events, cfg.base_cia, tier.kz_start
    )
    total_cost += outcome["total_event_opex"]
    adjusted_budget = tier.budget + outcome["total_event_budget"]
    over_budget = total_cost > adjusted_budget
    remaining_budget = adjusted_budget - total_cost

    final_event_results = []
    for event in cfg.final_events:
        ev_kz, _, _, description = evaluate_event(event, selection, remaining_budget=remaining_budget)
        outcome["kz_final"] = max(0, min(100, outcome["kz_final"] + ev_kz))
        final_event_results.append({
            "id": event.id,
            "name": event.name,
            "effect_description": description,
            "kz_delta": ev_kz,
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

    outcome["valid"] = True
    outcome["over_budget"] = over_budget
    if total_cost == 0:
        outcome["ros"] = None
    else:
        avoided_losses = _base_losses(cfg) - outcome["total_damage"]
        outcome["ros"] = (avoided_losses - total_cost) / total_cost
    return outcome
