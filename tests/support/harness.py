"""Adapter between the golden tests and the simulation code (D-05).

Step 2: delegates to `planspiel.rules.evaluate_plan`; `STAGE` marks the arithmetic generation.
Later plans change `STAGE`; the golden tests only call this module.
"""
import itertools
from pathlib import Path

from planspiel import rules
from planspiel.config import Config
from planspiel.config import load_config as _load_config

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


def load_config(path: Path = CONFIG_PATH) -> Config:
    return _load_config(path)


def measure_ids(cfg: Config) -> list:
    return list(cfg.measures.keys())


def code_of(cfg: Config, selection: dict) -> str:
    return "".join(str(selection[m]) for m in measure_ids(cfg))


def selection_of(cfg: Config, code: str) -> dict:
    return {m: int(digit) for m, digit in zip(measure_ids(cfg), code)}


def iter_codes(cfg: Config):
    for levels in itertools.product(range(LEVELS), repeat=len(cfg.measures)):
        yield "".join(map(str, levels))


def evaluate(cfg: Config, tier_name: str, selection: dict) -> dict:
    if not rules.dependencies_satisfied(selection, cfg.measures):
        return {"valid": False}
    return {"valid": True, **rules.evaluate_plan(cfg, tier_name, selection)}
