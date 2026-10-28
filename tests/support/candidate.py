"""Shared infrastructure of the Phase-6 balance checks: evaluate any config, cache the expensive enumerations.

The slow design-principle checks read the config chosen with `--planspiel-config` (default simulation_config.json)
and the content directory chosen with `--planspiel-content-dir` (default content/), through the session fixtures
`balance_config_path` and `balance_content_dir` of tests/conftest.py.

Checks that fail on today's config but are targets of the Phase-6 tuning carry `TUNING_TARGET` (a non-strict xfail),
so they stay visible in every `-m slow` run. The hard verdict on a candidate config is

    uv run pytest -m balance --runxfail --planspiel-config <candidate> --planspiel-content-dir <dir>

(xfail plus --runxfail was chosen over a separate default-deselected marker because the targets stay visible in
every run; it is the single approach for all Phase-6 checks).

The enumerations (static stores, summaries, swap layers, tier tables) are cached per resolved config path; stores
and swap layers are computed with one worker process per tier.
"""
import functools
import warnings
from pathlib import Path
from typing import Dict

import pytest

from planspiel import enumerate as enum
from planspiel import parallel, report, rules
from planspiel.config import load_config
from planspiel.validate import HandCalcWarning
from tests.support import CONFIG_PATH, CONTENT_DIR

TUNING_TARGET = pytest.mark.xfail(
    strict=False,
    reason="Ziel des Phase-6-Tunings: gilt erst mit der abgenommenen Konfiguration (06-10)",
)

TIER_JOBS = 3

_STORES: Dict[str, Dict] = {}
_SUMMARIES: Dict[str, Dict] = {}
_SWAP_LAYERS: Dict[str, Dict] = {}
_TABLES: Dict[tuple, rules.TierTables] = {}


def resolve_config_path(value) -> Path:
    return CONFIG_PATH if value is None else Path(value)


def resolve_content_dir(value) -> Path:
    return CONTENT_DIR if value is None else Path(value)


def _key(path) -> str:
    return str(Path(path).resolve())


@functools.lru_cache(maxsize=None)
def _load(key: str):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", HandCalcWarning)
        return load_config(Path(key))


def load_balance_config(path):
    return _load(_key(path))


def _tiers(path):
    return list(load_balance_config(path).budget_tiers)


def static_stores(path) -> Dict[str, enum.ResultStore]:
    key = _key(path)
    if key not in _STORES:
        _STORES[key] = parallel.map_tiers(enum.store_worker, key, _tiers(path), jobs=TIER_JOBS)
    return _STORES[key]


def static_summaries(path) -> Dict[str, dict]:
    key = _key(path)
    if key not in _SUMMARIES:
        cfg = load_balance_config(path)
        stores = static_stores(path)
        _SUMMARIES[key] = {tier: report.summarize_tier(cfg, tier, stores[tier]) for tier in stores}
    return _SUMMARIES[key]


def swap_layers(path) -> Dict[str, dict]:
    key = _key(path)
    if key not in _SWAP_LAYERS:
        _SWAP_LAYERS[key] = parallel.map_tiers(enum.swap_layer_worker, key, _tiers(path), jobs=TIER_JOBS)
    return _SWAP_LAYERS[key]


def tier_tables(path, tier: str) -> rules.TierTables:
    key = (_key(path), tier)
    if key not in _TABLES:
        _TABLES[key] = rules.TierTables(load_balance_config(path), tier)
    return _TABLES[key]
