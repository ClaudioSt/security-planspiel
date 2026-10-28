"""The Kurswechsel swap layer as the legal minimum: tables against the exact evaluator (RULE-02, D-24).

Every valid wave-1 plan x every legal Kurswechsel swap with the canonical minimal repair (D-28); plans without
a possible swap (D-22) count as their static path. Table results must equal `evaluate_path` exactly (T-02-23).
"""
import functools
import json
import random
import time
from itertools import product

import pytest

from planspiel import enumerate as enum
from planspiel import report, rules
from planspiel.cli import main
from planspiel.rules import Path, Window
from tests.support import REPO_ROOT, harness

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SWAP_LABEL = "Pflicht-Maßnahmentausch (Kurswechsel), legales Minimum"


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


def _index(code):
    return int(code, 4)


def _code(cfg, index):
    return enum.code_from_index(index, len(cfg.measures))


def _selection(cfg, index):
    return harness.selection_of(cfg, _code(cfg, index))


def _end_selection(cfg, start_selection, dropped, incoming, level):
    end = rules.swap_repair(start_selection, dropped, cfg.measures)
    end[incoming] = level
    return end


def _brute_swaps(cfg):
    """Independent enumeration: (start, end, dropped, incoming, level) for every legal canonical swap."""
    ids = cfg.measure_ids
    swaps = set()
    exempt = []
    for code in harness.iter_codes(cfg):
        selection = harness.selection_of(cfg, code)
        if not rules.dependencies_satisfied(selection, cfg.measures):
            continue
        if not rules.swap_possible(selection):
            exempt.append(_index(code))
            continue
        for dropped, incoming, level in product(ids, ids, (1, 2, 3)):
            if selection[dropped] == 0 or selection[incoming] != 0:
                continue
            end = _end_selection(cfg, selection, dropped, incoming, level)
            if rules.dependencies_satisfied(end, cfg.measures):
                swaps.add((_index(code), _index(harness.code_of(cfg, end)), dropped, incoming, level))
    return swaps, exempt


@functools.lru_cache(maxsize=None)
def _brute_games(tier):
    """Every legal game of the mini config via evaluate_path: sort key and outcome."""
    cfg = harness.load_config(MINI)
    ids = cfg.measure_ids
    swaps, exempt = _brute_swaps(cfg)
    games = []
    for start in exempt:
        rec = rules.evaluate_path(cfg, tier, Path(_selection(cfg, start)))
        games.append((start, start, -1, -1, 0, 0, harness.compact_from_path(cfg, rec)))
    for start, end, dropped, incoming, level in sorted(swaps):
        selection = _selection(cfg, start)
        window = Window(_selection(cfg, end), (dropped, incoming))
        rec = rules.evaluate_path(cfg, tier, Path(selection, (window,)))
        cost = rec["costs"]["window_costs"][0]
        games.append((start, end, ids.index(dropped), ids.index(incoming), level, cost, harness.compact_from_path(cfg, rec)))
    return games


def _best(games, over):
    pool = [game for game in games if game[6].over_budget is over]
    if not pool:
        return None
    return min(pool, key=lambda g: (-g[6].kz_final, g[6].own_cost, g[0], g[1], g[2], g[3]))


@pytest.mark.parametrize("tier", TIERS)
def test_static_path_outcome_equals_the_kernel(mini, tier):
    tables = rules.TierTables(mini, tier)
    kernel = rules.TierKernel(mini, tier)
    waves = len(mini.waves)
    checked = 0
    for code in harness.iter_codes(mini):
        index = _index(code)
        expected = kernel.evaluate(harness.selection_of(mini, code))
        assert bool(tables.valid[index]) == (expected is not None), code
        if expected is None:
            continue
        assert tables.path_outcome((index,) * waves, 0) == expected, code
        checked += 1
    assert checked > 0


@pytest.mark.parametrize("tier", TIERS)
def test_swap_paths_equal_the_exact_evaluator_on_every_mini_path(mini, tier):
    tables = rules.TierTables(mini, tier)
    ids = mini.measure_ids
    checked = 0
    for start, end, dropped, incoming, level, cost in tables.swap_paths():
        selection = _selection(mini, start)
        if dropped is None:
            assert (end, incoming, level, cost) == (start, None, 0, 0)
            rec = rules.evaluate_path(mini, tier, Path(selection))
            codes, window_total = (start,) * len(mini.waves), 0
        else:
            window = Window(_selection(mini, end), (ids[dropped], ids[incoming]))
            rec = rules.evaluate_path(mini, tier, Path(selection, (window,)), enforce_kurswechsel=True)
            assert rec["costs"]["window_costs"] == [cost]
            assert _selection(mini, end)[ids[incoming]] == level
            codes, window_total = (start,) + (end,) * (len(mini.waves) - 1), cost
        assert tables.path_outcome(codes, window_total) == harness.compact_from_path(mini, rec), (start, end)
        checked += 1
    assert checked > 0


def test_swap_paths_equal_a_brute_force_over_the_mini_config(mini):
    tables = rules.TierTables(mini, "low")
    ids = mini.measure_ids
    swaps, exempt = _brute_swaps(mini)
    got_swaps = set()
    got_exempt = []
    for start, end, dropped, incoming, level, _cost in tables.swap_paths():
        if dropped is None:
            got_exempt.append(start)
        else:
            assert (start, end, ids[dropped], ids[incoming], level) not in got_swaps
            got_swaps.add((start, end, ids[dropped], ids[incoming], level))
    assert got_swaps == swaps
    assert sorted(got_exempt) == sorted(exempt)
    assert len(exempt) == sum(
        1
        for code in harness.iter_codes(mini)
        if rules.dependencies_satisfied(harness.selection_of(mini, code), mini.measures)
        and not rules.swap_possible(harness.selection_of(mini, code))
    )
    non_exempt_starts = {
        _index(code)
        for code in harness.iter_codes(mini)
        if rules.dependencies_satisfied(harness.selection_of(mini, code), mini.measures)
        and rules.swap_possible(harness.selection_of(mini, code))
    }
    assert {swap[0] for swap in got_swaps} == non_exempt_starts


def test_swap_paths_are_ordered_by_start_index(mini):
    tables = rules.TierTables(mini, "low")
    starts = [path[0] for path in tables.swap_paths()]
    assert starts == sorted(starts)


def test_tables_expose_the_per_state_arrays(mini):
    tables = rules.TierTables(mini, "low")
    assert tables.kurswechsel_wave == 1
    assert len(tables.valid) == 4 ** len(mini.measures)
    assert tables.strides == [64, 16, 4, 1]
    assert len(tables.change) == len(mini.waves)
    assert tables.level_init[0][:2] == [0, 30]
    all_l1 = _index("1111")
    assert tables.init_cost[all_l1] == 30 + 20 + 16 + 10
    assert tables.opex_cost[all_l1] == 4 + 2 + 6 + 2


@pytest.mark.parametrize("tier", TIERS)
def test_summary_equals_a_brute_force_over_all_mini_paths(mini, tier):
    layer = enum.enumerate_swap_layer(mini, tier)
    games = _brute_games(tier)
    swaps = [game for game in games if game[2] >= 0]
    counts = layer["counts"]
    assert counts["legal_games"] == len(games) == counts["exempt_static"] + counts["swap_paths"]
    assert counts["in_budget"] + counts["over_budget"] == counts["legal_games"]
    assert counts["swap_paths"] == len(swaps)
    assert counts["swap_in_budget"] == sum(1 for game in swaps if not game[6].over_budget)
    assert counts["swap_over_budget"] == sum(1 for game in swaps if game[6].over_budget)
    assert counts["in_budget"] == sum(1 for game in games if not game[6].over_budget)
    assert counts["start_plans"] == len({game[0] for game in games})

    summary = report.summarize_swap_layer(mini, tier, layer)
    for name, over in (("in_budget", False), ("over_budget", True)):
        best = _best(games, over)
        got = summary["best"][name]
        if best is None:
            assert got is None
            continue
        start, end, dropped, incoming, level, cost, outcome = best
        assert got["start"] == _code(mini, start)
        assert got["end"] == _code(mini, end)
        ids = mini.measure_ids
        assert got["dropped"] == (None if dropped < 0 else ids[dropped])
        assert got["incoming"] == (None if incoming < 0 else ids[incoming])
        assert (got["level"], got["window_cost"], got["kz_final"], got["own_cost"]) == (
            level, cost, outcome.kz_final, outcome.own_cost,
        )
        assert (got["total_cost"], got["remaining"], got["over_budget"]) == (
            outcome.total_cost, outcome.remaining, over,
        )

        values = sorted(game[6].kz_final for game in games if game[6].over_budget is over)
        group = summary["percentiles"][name]
        assert group["count"] == len(values)
        for p in report.PERCENTILES:
            assert group["kz_final"][f"p{p}"] == report.nearest_rank(values, p), (name, p)
    assert summary["percentiles"]["method"] == "nearest-rank"
    assert summary["percentiles"]["p"] == list(report.PERCENTILES)


@pytest.mark.parametrize("tier", TIERS)
def test_start_aggregates_equal_a_brute_force_over_the_mini_paths(mini, tier):
    layer = enum.enumerate_swap_layer(mini, tier)
    starts = layer["starts"]
    size = 4 ** len(mini.measures)
    for name in ("best_in_budget", "worst_in_budget", "in_budget_paths"):
        assert len(starts[name]) == size
    expected = {}
    for game in _brute_games(tier):
        if not game[6].over_budget:
            expected.setdefault(game[0], []).append(game[6].kz_final)
    assert expected
    for start in range(size):
        finals = expected.get(start)
        if finals is None:
            assert (starts["best_in_budget"][start], starts["worst_in_budget"][start], starts["in_budget_paths"][start]) == (-1, -1, 0), start
        else:
            assert starts["best_in_budget"][start] == max(finals), start
            assert starts["worst_in_budget"][start] == min(finals), start
            assert starts["in_budget_paths"][start] == len(finals), start
    assert sum(starts["in_budget_paths"]) == layer["counts"]["in_budget"]


def test_summary_header_fields(mini):
    layer = enum.enumerate_swap_layer(mini, "medium")
    summary = report.summarize_swap_layer(mini, "medium", layer)
    assert report.SWAP_LAYER == "tausch"
    assert report.SWAP_LABEL == SWAP_LABEL
    assert summary["format"] == 1
    assert summary["tier"] == "medium"
    assert summary["layer"] == "tausch"
    assert summary["layer_label"] == SWAP_LABEL
    assert summary["kurswechsel_wave"] == 1
    assert summary["budget"] == 400
    assert summary["kz_start"] == 42
    assert summary["measures"] == mini.measure_ids
    assert summary["best"]["metric"] == "kz_final"
    assert summary["counts"] == layer["counts"]


def test_console_text_starts_with_the_label(mini):
    layer = enum.enumerate_swap_layer(mini, "low")
    text = report.format_swap_console(report.summarize_swap_layer(mini, "low", layer))
    assert text.splitlines()[0] == SWAP_LABEL
    assert "Tausch" in text


def test_cli_tausch_writes_the_summary_and_prints_the_label(tmp_path, capsys):
    assert main(["tausch", "--config", str(MINI), "--tier", "low", "--summary-dir", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert SWAP_LABEL in out
    target = tmp_path / "simulation_summary_tausch_low.json"
    assert [path.name for path in tmp_path.iterdir()] == [target.name]
    raw = target.read_bytes()
    assert b"\r" not in raw
    summary = json.loads(raw.decode("utf-8"))
    assert summary["layer_label"] == SWAP_LABEL
    assert summary["tier"] == "low"


def test_cli_tausch_defaults_to_all_tiers(tmp_path, capsys):
    assert main(["tausch", "--config", str(MINI), "--summary-dir", str(tmp_path)]) == 0
    capsys.readouterr()
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        f"simulation_summary_tausch_{tier}.json" for tier in sorted(TIERS)
    ]


def test_cli_tausch_rejects_an_unknown_tier(tmp_path, capsys):
    with pytest.raises(SystemExit) as caught:
        main(["tausch", "--config", str(MINI), "--tier", "huge", "--summary-dir", str(tmp_path)])
    assert caught.value.code == 2
    assert "low" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


def test_cli_validate_still_works(capsys):
    assert main(["validate", "--config", str(MINI)]) == 0
    assert "0 Fehler" in capsys.readouterr().out


REAL_LOW_COUNTS = {
    "start_plans": 782_336,
    "exempt_static": 48_115,
    "swap_paths": 37_300_736,
    "swap_in_budget": 3_587_803,
    "swap_over_budget": 33_712_933,
}


@pytest.mark.slow
def test_real_low_tier_counts_and_runtime():
    cfg = harness.load_config()
    started = time.perf_counter()
    layer = enum.enumerate_swap_layer(cfg, "low")
    seconds = time.perf_counter() - started
    print(f"\nswap layer low tier: {seconds:.1f} s, counts {layer['counts']}")
    counts = layer["counts"]
    for key, expected in REAL_LOW_COUNTS.items():
        assert counts[key] == expected, key
    assert counts["legal_games"] == counts["exempt_static"] + counts["swap_paths"]
    assert counts["in_budget"] + counts["over_budget"] == counts["legal_games"]
    assert sum(layer["histogram"]["in_budget"]) == counts["in_budget"]
    assert sum(layer["histogram"]["over_budget"]) == counts["over_budget"]
    assert seconds <= 900


@pytest.mark.slow
def test_real_low_tier_random_swap_paths_equal_the_exact_evaluator():
    cfg = harness.load_config()
    tables = rules.TierTables(cfg, "low")
    ids = cfg.measure_ids
    rng = random.Random(20261001)
    waves = len(cfg.waves)
    picked = 0
    while picked < 2000:
        levels = [rng.randrange(4) for _ in ids]
        selection = dict(zip(ids, levels))
        if not rules.dependencies_satisfied(selection, cfg.measures) or not rules.swap_possible(selection):
            continue
        dropped = rng.choice([m for m in ids if selection[m] > 0])
        incoming = rng.choice([m for m in ids if selection[m] == 0])
        level = rng.randrange(1, 4)
        end = _end_selection(cfg, selection, dropped, incoming, level)
        if not rules.dependencies_satisfied(end, cfg.measures):
            continue
        picked += 1
        start_index = int("".join(map(str, levels)), 4)
        end_index = int(harness.code_of(cfg, end), 4)
        rec = rules.evaluate_path(cfg, "low", Path(selection, (Window(end, (dropped, incoming)),)))
        cost = rec["costs"]["window_costs"][0]
        codes = (start_index,) + (end_index,) * (waves - 1)
        assert tables.path_outcome(codes, cost) == harness.compact_from_path(cfg, rec), (selection, end)
