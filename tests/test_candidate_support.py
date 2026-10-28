"""Candidate-config infrastructure of the Phase-6 balance checks: option resolution, per-tier fan-out, single moves."""
from pathlib import Path

import pytest

from planspiel import enumerate as enum
from planspiel import parallel, rules
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT, candidate, harness

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


def test_resolve_config_path_defaults_to_the_repository_config():
    assert candidate.resolve_config_path(None) == CONFIG_PATH
    assert candidate.resolve_config_path("x/y.json") == Path("x/y.json")


def test_resolve_content_dir_defaults_to_the_repository_content():
    assert candidate.resolve_content_dir(None) == CONTENT_DIR
    assert candidate.resolve_content_dir("x/content") == Path("x/content")


def test_balance_fixtures_follow_the_pytest_options(request, balance_config_path, balance_content_dir):
    assert balance_config_path == candidate.resolve_config_path(request.config.getoption("--planspiel-config"))
    assert balance_content_dir == candidate.resolve_content_dir(request.config.getoption("--planspiel-content-dir"))


def test_tuning_target_is_a_non_strict_xfail():
    mark = candidate.TUNING_TARGET.mark
    assert mark.name == "xfail"
    assert mark.kwargs["strict"] is False
    assert "Phase-6" in mark.kwargs["reason"]


def test_load_balance_config_is_cached_and_silent(mini, recwarn):
    first = candidate.load_balance_config(MINI)
    assert candidate.load_balance_config(MINI) is first
    assert first.measure_ids == mini.measure_ids


def test_cached_enumerations_cover_every_tier(mini):
    stores = candidate.static_stores(MINI)
    assert list(stores) == list(mini.budget_tiers)
    assert candidate.static_stores(MINI) is stores
    for tier in TIERS:
        assert len(stores[tier]) == len(enum.enumerate_tier(mini, tier))
    summaries = candidate.static_summaries(MINI)
    assert list(summaries) == list(mini.budget_tiers)
    layers = candidate.swap_layers(MINI)
    assert list(layers) == list(mini.budget_tiers)
    assert candidate.tier_tables(MINI, "low") is candidate.tier_tables(MINI, "low")


def test_map_tiers_gives_equal_results_for_one_and_two_jobs():
    serial = parallel.map_tiers(enum.swap_layer_worker, MINI, TIERS, jobs=1)
    pooled = parallel.map_tiers(enum.swap_layer_worker, MINI, TIERS, jobs=2)
    assert list(serial) == list(pooled) == list(TIERS)
    for tier in TIERS:
        assert serial[tier]["counts"] == pooled[tier]["counts"]
        assert serial[tier]["histogram"] == pooled[tier]["histogram"]
        assert list(serial[tier]["starts"]["best_in_budget"]) == list(pooled[tier]["starts"]["best_in_budget"])


def test_store_worker_matches_enumerate_tier(mini):
    store = enum.store_worker(str(MINI), "low")
    expected = enum.enumerate_tier(mini, "low")
    assert list(store.column("code_index")) == list(expected.column("code_index"))
    assert list(store.column("kz_final")) == list(expected.column("kz_final"))


@pytest.mark.parametrize("tier", TIERS)
def test_single_moves_are_every_valid_one_measure_change_once(mini, tier):
    tables = rules.TierTables(mini, tier)
    count = len(mini.measure_ids)
    checked = 0
    for code in harness.iter_codes(mini):
        index = int(code, 4)
        selection = harness.selection_of(mini, code)
        expected = {}
        for measure in mini.measure_ids:
            for level in range(4):
                if level == selection[measure]:
                    continue
                target = dict(selection)
                target[measure] = level
                if not rules.dependencies_satisfied(target, mini.measures):
                    continue
                expected[int(harness.code_of(mini, target), 4)] = rules.window_cost(
                    mini.measures, selection, target
                )
        got = list(tables.single_moves(index))
        assert len(got) == len({target for target, _ in got}), code
        assert dict(got) == expected, code
        checked += len(got)
    assert checked > 0
    assert count == 4
