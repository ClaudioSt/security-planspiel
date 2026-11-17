"""Prosa verlässt simulation_config.json (D-02, D-03, D-24): nur Zahlen, IDs und kurze Labels bleiben."""
import copy
import dataclasses
import json
from fractions import Fraction

import pytest

from planspiel import rules
from planspiel.config import BonusMeasure, Event, Wave, load_config
from planspiel.validate import ConfigError, validate
from tests.support import CONFIG_PATH, REPO_ROOT, harness

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
PATHS = pytest.param(CONFIG_PATH, id="real"), pytest.param(MINI, id="mini")


def _raw(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _events(raw):
    for wave_events in raw["events"].values():
        yield from wave_events
    yield from raw["final_events"]


@pytest.mark.parametrize("path", PATHS)
def test_raw_config_has_no_prose_keys(path):
    raw = _raw(path)
    assert [a for a, info in raw["attacks"].items() if "description" in info] == []
    assert [w["id"] for w in raw["waves"] if "name" in w] == []
    assert [
        bm["measure"] for w in raw["waves"] for bm in w["bonus_measures"] if "description" in bm
    ] == []
    assert [e["id"] for e in _events(raw) if "description" in e] == []


@pytest.mark.parametrize("path", PATHS)
def test_events_and_measures_keep_their_short_labels(path):
    raw = _raw(path)
    assert all(isinstance(e["name"], str) and e["name"] for e in _events(raw))
    assert all(isinstance(m["name"], str) and m["name"] for m in raw["measures"].values())


def test_dataclasses_lost_the_prose_fields():
    assert "description" not in {f.name for f in dataclasses.fields(BonusMeasure)}
    assert "name" not in {f.name for f in dataclasses.fields(Wave)}
    event_fields = {f.name for f in dataclasses.fields(Event)}
    assert "description" not in event_fields
    assert "name" in event_fields


def _set_key(path_parts, key, value="Prosa"):
    def mutate(raw):
        target = raw
        for part in path_parts:
            target = target[part]
        target[key] = value

    return mutate


PROSE_MUTATIONS = [
    pytest.param(_set_key(["attacks", "ransomware"], "description"), "attacks.ransomware.description", id="attack"),
    pytest.param(_set_key(["waves", 0], "name"), "waves[0].name", id="wave-name"),
    pytest.param(
        _set_key(["waves", 0, "bonus_measures", 0], "description"),
        "waves[0].bonus_measures[0].description",
        id="bonus-description",
    ),
    pytest.param(_set_key(["events", "wave_1", 0], "description"), "events.wave_1[0].description", id="event"),
    pytest.param(_set_key(["final_events", 0], "description"), "final_events[0].description", id="final-event"),
]


@pytest.mark.parametrize(("mutate", "path"), PROSE_MUTATIONS)
def test_prose_in_config_is_a_validator_error_at_its_path(mutate, path):
    raw = copy.deepcopy(_raw(CONFIG_PATH))
    mutate(raw)
    hits = [i for i in validate(raw) if i.code == "schema.prose_in_config"]
    assert [(i.level, i.path) for i in hits] == [("error", path)]


@pytest.mark.parametrize(("mutate", "path"), PROSE_MUTATIONS)
def test_load_config_rejects_prose(tmp_path, mutate, path):
    raw = copy.deepcopy(_raw(CONFIG_PATH))
    mutate(raw)
    target = tmp_path / "config.json"
    target.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ConfigError) as error:
        load_config(target)
    assert "schema.prose_in_config" in str(error.value)


def test_real_config_is_clean():
    assert validate(_raw(CONFIG_PATH)) == []


def test_compute_bonus_reduction_returns_an_int():
    cfg = load_config(CONFIG_PATH)
    selection = {m: 2 for m in cfg.measures}
    bonus = rules.compute_bonus_reduction(cfg.waves[0], selection)
    assert isinstance(bonus, int)
    assert bonus == 15


def test_sparprogramm_label_is_generated_from_the_params():
    cfg = load_config(CONFIG_PATH)
    event = next(e for e in cfg.events[2] if e.id == "sparprogramm")
    assert rules.evaluate_event(event, {m: 1 for m in cfg.measures})[3] == "Gesamtbudget -20k€"


def test_simulation_records_carry_no_wave_name_or_bonus_descriptions():
    cfg = load_config(CONFIG_PATH)
    record = harness.evaluate(cfg, "medium", harness.selection_of(cfg, "2" * len(cfg.measures)))
    assert record["valid"]
    for wave in record["waves"]:
        assert "wave_name" not in wave
        assert "bonus_descriptions" not in wave


def _params(cfg, event_id):
    events = [e for wave_events in cfg.events.values() for e in wave_events] + cfg.final_events
    return next(e for e in events if e.id == event_id).params


def test_removed_numbers_map_to_config_params():
    cfg = load_config(CONFIG_PATH)
    ledger = [
        ("operative_unterstuetzung", "opex_per_measure", -2),
        ("sparprogramm", "budget_delta", -20),
        ("oem_audit", "measures", ["M1", "M2", "M4", "M5", "M7"]),
        ("oem_audit", "min_level", 1),
        ("kritische_schwachstelle", "measure", "M7"),
        ("exzellenz_bonus", "level", 2),
        ("exzellenz_bonus", "kz_per_measure", 3),
        ("nervige_authentifizierung", "kz_delta", -6),
    ]
    for event_id, key, expected in ledger:
        assert _params(cfg, event_id)[key] == expected, (event_id, key)
    clauses = _params(cfg, "nervige_authentifizierung")["clauses"]
    assert clauses[0] == {"measure": "M1", "min_level": 2}
    assert clauses[1] == {"measure": "M6", "level_eq": 0}
    levels = cfg.measures["M4"].levels
    assert [1 - levels[n].recovery for n in (1, 2, 3)] == [Fraction(9, 10), Fraction(7, 10), Fraction(1, 2)]
