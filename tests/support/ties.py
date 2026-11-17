"""Test-only config with real .5 ties in wave 3 (D-23).

The tuned config has one-decimal slopes and one-decimal E values, so no real plan ends a wave on a .5 attack delta
any more. The rounding rule (once per wave, half away from zero) still has to hold, so the tie tests run on a test
copy of the real config in which the third attack has the slope 3/2 (damage -6, full mitigation +6, cap and base
severity 8). Everything else is the real config.
"""
import copy
import json
import random
from fractions import Fraction
from pathlib import Path

from planspiel import rules
from tests.support import CONFIG_PATH, harness

TIE_SEED = 20260930
MAX_DRAWS = 20000
NEGATIVE_TIE_EVENT = {
    "id": "test_negative_tie",
    "name": "Test negative tie",
    "type": "and_condition",
    "clauses": [{"measure": "M6", "min_level": 0}],
    "kz_delta": -7,
}


def tie_raw(extra_wave_3_events=()):
    raw = copy.deepcopy(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    exfil = raw["attacks"]["exfil"]
    exfil.update(base_severity=8, mitigation_cap=8, kz_at_full_damage=-6, kz_at_full_mitigation=6)
    raw["risk_matrix"].pop("cases", None)  # the cheat-sheet band of the exfil case no longer fits the test damage
    raw["events"]["wave_3"].extend(copy.deepcopy(event) for event in extra_wave_3_events)
    return raw


def write_tie_config(tmp_path: Path, extra_wave_3_events=()) -> Path:
    path = tmp_path / "simulation_config.json"
    path.write_text(json.dumps(tie_raw(extra_wave_3_events), ensure_ascii=False), encoding="utf-8")
    return path


def wave_events_kz(wave) -> int:
    return sum(event["kz_delta"] for event in wave["events"])


def tie_total(wave):
    return wave["kz_delta_attack"] + wave_events_kz(wave)


def tie_codes(cfg, tier, count=1, positive=None, seed=TIE_SEED):
    """Deterministic valid codes whose wave 3 ends on a .5 total (attack plus events).

    `positive` True keeps ties with a positive total, False with a negative one, None either.
    """
    rng = random.Random(seed)
    found = []
    for _ in range(MAX_DRAWS):
        code = "".join(str(rng.randrange(4)) for _ in cfg.measures)
        selection = harness.selection_of(cfg, code)
        if not rules.dependencies_satisfied(selection, cfg.measures):
            continue
        record = harness.evaluate(cfg, tier, selection)
        wave = record["waves"][2]
        total = tie_total(wave)
        if total % 1 != Fraction(1, 2):
            continue
        if positive is not None and (total > 0) != positive:
            continue
        found.append(code)
        if len(found) == count:
            return found
    raise AssertionError(f"no wave-3 tie found in {MAX_DRAWS} draws")
