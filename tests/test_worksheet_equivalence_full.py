"""Every enumerated plan, replayed wave by wave through the printed worksheet steps (PRINT-04, D-12).

Run with `uv run pytest -m slow tests/test_worksheet_equivalence_full.py -v -s` (a few minutes per tier). For every
dependency-valid plan of a tier the replay takes the team's CIA table, the measure levels and the facilitator's
event KZ input, follows the sheet steps, chains the KZ from the tier start with the clamp to 0..100 (which lives on
the tracking sheet, so the test applies it) and must reproduce the simulation's per-wave KZ and total damage.
"""
import itertools
import time
from functools import lru_cache

import pytest

from planspiel import rules
from planspiel.config import load_config
from planspiel.enumerate import LEVEL_OPTIONS, code_from_index, enumerate_tier
from planspiel.printmodel import build_attack_sheets
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR
from tests.support.worksheet_replay import event_kz_bounds, replay_wave

pytestmark = pytest.mark.slow

MAX_MISMATCHES = 20
KZ_MIN = 0
KZ_MAX = 100


@lru_cache(maxsize=1)
def _setup():
    cfg = load_config(CONFIG_PATH)
    return cfg, build_attack_sheets(cfg, load_texts(CONTENT_DIR / "texte.toml"))


@lru_cache(maxsize=1)
def _valid_plan_count():
    """Independent count of dependency-valid plans: the product of all level options, filtered by the dependencies."""
    cfg, _ = _setup()
    ids = cfg.measure_ids
    return sum(
        1
        for levels in itertools.product(LEVEL_OPTIONS, repeat=len(ids))
        if rules.dependencies_satisfied(dict(zip(ids, levels)), cfg.measures)
    )


def _card_cia(cfg, selection):
    """Step 1 of the sheet: base protection plus the CIA values printed on the measure cards."""
    totals = [cfg.base_cia["c"], cfg.base_cia["i"], cfg.base_cia["a"]]
    for measure_id, level in selection.items():
        card = cfg.measures[measure_id].levels[level].cia
        totals[0] += card["c"]
        totals[1] += card["i"]
        totals[2] += card["a"]
    return tuple(totals)


@pytest.mark.parametrize("tier_name", list(_setup()[0].budget_tiers))
def test_every_plan_replays_to_the_simulation_result(tier_name, record_property):
    cfg, sheets = _setup()
    tier = cfg.budget_tiers[tier_name]
    measure_ids = cfg.measure_ids
    varied = []
    for sheet in sheets:
        names = [row.measure for row in sheet.bonus_rows]
        if sheet.recovery_measure is not None and sheet.recovery_measure not in names:
            names.append(sheet.recovery_measure)
        varied.append(tuple(names))

    memo = {}
    event_sets = {wave.wave_id: set() for wave in cfg.waves}
    mismatches = []
    stats = {"plans": 0, "wrong": 0}

    def replayed(index, cia, selection, event_kz):
        names = varied[index]
        key = (index, cia, tuple(selection.get(name, 0) for name in names), event_kz)
        result = memo.get(key)
        if result is None:
            outcome = replay_wave(sheets[index], cia, selection, event_kz)
            result = memo[key] = (outcome.change, outcome.damage_eur)
        return result

    def check(code_index, outcome):
        stats["plans"] += 1
        code = code_from_index(code_index, len(measure_ids))
        selection = {measure_id: int(digit) for measure_id, digit in zip(measure_ids, code)}
        cia = _card_cia(cfg, selection)
        kz = tier.kz_start
        kz_after = []
        damage = 0
        for index, wave in enumerate(cfg.waves):
            event_kz = rules.apply_events(wave.wave_id, selection, cfg.events)[0]
            event_sets[wave.wave_id].add(event_kz)
            change, wave_damage = replayed(index, cia, selection, event_kz)
            kz = max(KZ_MIN, min(KZ_MAX, kz + change))
            kz_after.append(kz)
            damage += wave_damage
        if tuple(kz_after) != outcome.kz_after or damage != outcome.damage_eur:
            stats["wrong"] += 1
            if len(mismatches) < MAX_MISMATCHES:
                mismatches.append(
                    f"{tier_name} {code}: replay KZ {tuple(kz_after)} damage {damage} != "
                    f"simulation KZ {outcome.kz_after} damage {outcome.damage_eur}"
                )

    started = time.perf_counter()
    enumerate_tier(cfg, tier_name, on_outcome=check)
    seconds = time.perf_counter() - started

    print(f"\n[{tier_name}] plans checked: {stats['plans']}, mismatches: {stats['wrong']}, seconds: {seconds:.0f}")
    for wave in cfg.waves:
        bounds = event_kz_bounds(cfg, wave.wave_id)
        values = sorted(event_sets[wave.wave_id])
        record_property(f"{tier_name}_event_kz_wave_{wave.wave_id}", str(values))
        print(f"[{tier_name}] wave {wave.wave_id} event KZ set ({len(values)}): {values}; bounds {bounds}")
        assert set(values) <= set(bounds), (wave.wave_id, values, bounds)
    record_property(f"{tier_name}_plans", stats["plans"])
    record_property(f"{tier_name}_seconds", round(seconds))

    assert mismatches == []
    assert stats["plans"] == _valid_plan_count()
