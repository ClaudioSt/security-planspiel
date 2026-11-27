"""`planspiel export-web` (WEB-01): config and golden cases for the TypeScript engine of the web app.

The web app ports `planspiel/rules.py` to TypeScript and must hit every golden case exactly. These tests pin what the
export promises: the config round-trips exactly, the golden traces come from `rules.path_trace` (single definition),
they cover every branch the engine has to get right, and the export is deterministic.
"""
import json
from fractions import Fraction

import pytest

from planspiel import rules
from planspiel.config import load_config, read_raw_config
from planspiel.export_web import build_export, golden_path, write_export
from tests.support import REPO_ROOT

CONFIG_PATH = REPO_ROOT / "simulation_config.json"


@pytest.fixture(scope="module")
def export():
    return build_export(CONFIG_PATH)


def _exact(value):
    """Reads back what exact_to_json wrote: int, "2.24" or "p/q"."""
    return Fraction(value) if isinstance(value, str) else Fraction(value)


def _same_numbers(raw, exported):
    if isinstance(raw, dict):
        assert set(raw) == set(exported)
        for key in raw:
            _same_numbers(raw[key], exported[key])
    elif isinstance(raw, list):
        assert len(raw) == len(exported)
        for a, b in zip(raw, exported):
            _same_numbers(a, b)
    elif isinstance(raw, bool) or raw is None:
        assert raw == exported
    elif isinstance(raw, (int, Fraction)):
        assert not isinstance(exported, float), "no binary floats in the export"
        assert _exact(exported) == raw
    else:
        assert raw == exported


def test_config_round_trips_exactly(export):
    _same_numbers(read_raw_config(CONFIG_PATH), export["config.json"])


def test_manifest_names_source_and_counts(export):
    manifest = export["manifest.json"]
    assert manifest["schema"] == 1
    assert len(manifest["config_sha256"]) == 64
    assert manifest["golden_cases"] == len(export["golden.json"]["cases"])


def test_golden_traces_come_from_path_trace(export):
    cfg = load_config(CONFIG_PATH)
    case = next(c for c in export["golden.json"]["cases"] if c["id"] == "reference_strategy.medium.good")
    path = golden_path(case["path"])
    trace = rules.path_trace(cfg, case["tier"], path, enforce_kurswechsel=case["enforce_kurswechsel"])
    assert case["expect"]["trace"]["review"]["kz_final"] == trace.review.kz_final
    assert case["expect"]["trace"]["waves"][0]["case"] == trace.waves[0].case
    assert _exact(case["expect"]["final_index"]) == rules.final_index(
        trace.review.kz_final, trace.review.ros, cfg.final_index.weight_kz, cfg.final_index.weight_ros
    )


def test_every_reference_plan_and_strategy_is_a_case(export):
    cfg = load_config(CONFIG_PATH)
    ids = {case["id"] for case in export["golden.json"]["cases"]}
    for tier in cfg.reference_plans:
        assert f"reference_plan.{tier}" in ids
    for tier, strategies in cfg.reference_strategies.items():
        for name in strategies:
            assert f"reference_strategy.{tier}.{name}" in ids
    for tier in cfg.budget_tiers:
        assert f"clue_measures_min_level.{tier}" in ids


def test_error_cases_cover_every_path_error(export):
    reasons = {case["expect"]["error"] for case in export["golden.json"]["cases"] if "error" in case["expect"]}
    assert reasons == {
        "unknown_measure",
        "level_range",
        "dependencies",
        "too_many_windows",
        "kurswechsel_missing",
        "kurswechsel_illegal",
        "swap_without_kurswechsel",
    }


def test_golden_cases_cover_the_branches(export):
    cfg = load_config(CONFIG_PATH)
    traces = [case["expect"]["trace"] for case in export["golden.json"]["cases"] if "trace" in case["expect"]]
    waves = [wave for trace in traces for wave in trace["waves"]]
    for index in range(len(cfg.waves)):
        assert {w["case"] for w in waves if w["wave_id"] == cfg.waves[index].wave_id} == {1, 2, 3}
    fractional = [_exact(w["kz_change_exact"]) for w in waves if _exact(w["kz_change_exact"]).denominator != 1]
    assert any(x > 0 for x in fractional) and any(x < 0 for x in fractional), "wave KZ rounding on both signs"
    event_types = {event.type for events in cfg.events.values() for event in events}
    seen_ids = {event["id"] for w in waves for event in w["events"]}
    assert {event.id for events in cfg.events.values() for event in events} <= seen_ids
    assert "kurswechsel" in event_types
    remaining = {trace["review"]["remaining_k"] for trace in traces}
    assert any(r < 0 for r in remaining) and any(r >= 0 for r in remaining)
    assert any(trace["windows"] and trace["windows"][0]["swap"] for trace in traces)
    review_changes = {trace["review"]["kz_review_change"] for trace in traces}
    assert len(review_changes) >= 4, "several budget review bands and overspend steps"


def test_rounding_table_covers_exact_halves(export):
    """With the current config no wave lands on an exact half, so the rounding rule gets its own table from
    `round_half_away` (the single definition), including +x,5 and -x,5."""
    from planspiel.rounding import round_half_away

    table = export["golden.json"]["rounding"]
    assert {(row["n"], row["d"]) for row in table} >= {(5, 2), (-5, 2), (1, 2), (-1, 2), (7, 4), (-7, 4)}
    for row in table:
        assert row["result"] == round_half_away(row["n"], row["d"])


def test_export_is_deterministic(tmp_path):
    first = tmp_path / "a"
    second = tmp_path / "b"
    write_export(CONFIG_PATH, first)
    write_export(CONFIG_PATH, second)
    for name in ("config.json", "content.json", "golden.json", "manifest.json"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
        json.loads((first / name).read_text(encoding="utf-8"))


def test_cli_writes_the_export(tmp_path):
    from planspiel.cli import main

    assert main(["export-web", "--out", str(tmp_path)]) == 0
    assert (tmp_path / "golden.json").exists()


def test_practice_wave_is_exported(export):
    """Welle 0 of the web app is checked against practice.check_example (the printed practice sheet)."""
    from planspiel import practice

    cfg = load_config(CONFIG_PATH)
    wave = practice.check_example(cfg).waves[0]
    exported = export["golden.json"]["practice"]
    assert exported["case"] == wave.case
    assert _exact(exported["kz_change_exact"]) == wave.kz_change_exact
    assert exported["kz_after"] == wave.kz_after
