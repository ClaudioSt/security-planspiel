"""BAL-06 checks ("every choice matters"): dominated levels, near-mandatory and overpowered measures, decision points.

The metrics are pure functions over ResultStore columns, swap-layer start aggregates and TierTables. Every function
is compared with an independent brute force on the mini config; the slow checks run on the config chosen with
--planspiel-config (default simulation_config.json), one test per criterion.
"""
import itertools
from array import array
from fractions import Fraction

import pytest

from planspiel import choices, enumerate as enum, report, rules
from tests.support import REPO_ROOT, harness

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


def _digit(code, j, n):
    return (code // 4 ** (n - 1 - j)) % 4


def _replace(code, j, level, n):
    stride = 4 ** (n - 1 - j)
    return code + (level - _digit(code, j, n)) * stride


def _mini_plans(cfg, tier):
    """code -> (kz_final, own_cost, over_budget) for every dependency-valid plan, via the exact evaluator."""
    plans = {}
    for code in harness.iter_codes(cfg):
        record = harness.evaluate(cfg, tier, harness.selection_of(cfg, code))
        if record["valid"]:
            outcome = harness.compact_from_plan(cfg, record)
            plans[int(code, 4)] = (outcome.kz_final, outcome.own_cost, outcome.over_budget)
    return plans


def _in_budget(plans):
    return {code: kz for code, (kz, _own, over) in plans.items() if not over}


def _columns(store):
    return store.column("code_index"), store.column("kz_final"), store.column("own_cost"), store.column("over_budget")


# ---------------------------------------------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------------------------------------------


def test_thresholds_are_the_documented_proposals():
    assert choices.BAND_KZ == 5
    assert choices.BAND_MIN_SIZE == 200
    assert choices.NEAR_MANDATORY_SHARE == Fraction(9, 10)
    assert choices.OVERPOWERED_DROP == 10
    assert choices.DECISION_SHIFT_KZ == 3
    assert choices.DECISION_SHARE == Fraction(1, 2)
    assert choices.TIER_JACCARD_MAX == Fraction(1, 2)
    assert choices.WINDOW_SAMPLE_STRIDE == 97


# ---------------------------------------------------------------------------------------------------------------
# synthetic n = 2 grid
# ---------------------------------------------------------------------------------------------------------------


def _synthetic_grid():
    """Measure 0 level 2 never beats levels 0 and 1; measure 1 only has levels 0 and 1."""
    rows = []
    for d1 in (0, 1):
        for d0, base in ((0, 50), (1, 60), (2, 55), (3, 70)):
            rows.append((d0 * 4 + d1, base + 10 * d1))
    code_index = array("I", [row[0] for row in rows])
    kz_final = array("B", [row[1] for row in rows])
    over_budget = array("B", [0] * len(rows))
    return choices.kz_grid(2, code_index, kz_final, over_budget)


def test_kz_grid_holds_final_kz_of_in_budget_plans_and_minus_one_elsewhere():
    code_index = array("I", [0, 1, 5, 6])
    kz_final = array("B", [10, 20, 30, 40])
    over_budget = array("B", [0, 1, 0, 1])
    grid = choices.kz_grid(2, code_index, kz_final, over_budget)
    assert len(grid) == 16
    assert grid[0] == 10 and grid[5] == 30
    assert grid[1] == -1 and grid[6] == -1
    assert [grid[i] for i in range(16) if i not in (0, 5)] == [-1] * 14


def test_synthetic_dominated_level_has_share_zero():
    shares = choices.level_improvement_shares(_synthetic_grid(), 2)
    assert shares[(0, 1)] == 1
    assert shares[(0, 2)] == 0
    assert shares[(0, 3)] == 1
    assert shares[(1, 1)] == 1
    assert shares[(1, 2)] is None and shares[(1, 3)] is None
    assert choices.strictly_dominated(shares) == [(0, 2)]


def test_synthetic_swing_share_counts_contexts_with_two_levels():
    grid = _synthetic_grid()
    swing = choices.level_swing_shares(grid, 2, shift=3)
    assert swing[0] == 1
    assert swing[1] == 1
    assert choices.level_swing_shares(grid, 2, shift=21)[0] == 0
    assert choices.level_swing_shares(grid, 2, shift=20)[0] == 1


def test_synthetic_removal_drop_is_best_minus_best_without_the_measure():
    grid = _synthetic_grid()
    assert choices.removal_drops(grid, 2) == {0: 80 - 60, 1: 80 - 70}


def test_band_takes_everything_within_the_width_of_the_best():
    code_index = array("I", [0, 1, 2, 3, 4])
    kz_final = array("B", [90, 88, 85, 84, 60])
    own_cost = array("H", [100, 90, 80, 70, 10])
    over_budget = array("B", [0, 0, 0, 0, 0])
    assert choices.near_optimal_band(code_index, kz_final, own_cost, over_budget, band=5, min_size=1) == [0, 1, 2]


def test_band_is_widened_to_the_min_size_best_rows_ordered_by_kz_cost_code():
    code_index = array("I", [7, 3, 5, 4, 2])
    kz_final = array("B", [90, 90, 90, 80, 70])
    own_cost = array("H", [100, 100, 50, 10, 10])
    over_budget = array("B", [0, 0, 0, 0, 0])
    assert choices.near_optimal_band(code_index, kz_final, own_cost, over_budget, band=1, min_size=4) == [5, 3, 7, 4]


def test_band_ignores_over_budget_rows_and_an_empty_pool():
    code_index = array("I", [0, 1])
    kz_final = array("B", [99, 50])
    own_cost = array("H", [1, 1])
    over_budget = array("B", [1, 0])
    assert choices.near_optimal_band(code_index, kz_final, own_cost, over_budget, band=5, min_size=1) == [1]
    assert choices.near_optimal_band(code_index, kz_final, own_cost, array("B", [1, 1]), band=5, min_size=1) == []


def test_band_shares_and_near_mandatory_use_strictly_more_than_the_threshold():
    codes = [int("12", 4), int("13", 4), int("22", 4), int("10", 4), int("03", 4)]
    shares = choices.band_shares(codes, 2)
    assert shares[0] == (Fraction(4, 5), Fraction(1, 5))
    assert shares[1] == (Fraction(4, 5), Fraction(4, 5))
    assert choices.near_mandatory(shares, Fraction(4, 5)) == []
    assert choices.near_mandatory(shares, Fraction(79, 100)) == [0, 1]
    assert choices.near_mandatory(shares) == []


def test_band_shares_reject_an_empty_band():
    with pytest.raises(ValueError):
        choices.band_shares([], 2)


def test_tier_band_jaccard_is_intersection_over_union_of_the_code_sets():
    result = choices.tier_band_jaccard({"low": [1, 2, 3], "medium": [2, 3, 4, 5], "high": [9]})
    assert result == {("low", "medium"): Fraction(2, 5), ("low", "high"): Fraction(0), ("medium", "high"): Fraction(0)}


# ---------------------------------------------------------------------------------------------------------------
# mini config against brute force
# ---------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("tier", TIERS)
def test_mini_kz_grid_equals_the_exact_evaluator(mini, tier):
    n = len(mini.measures)
    plans = _mini_plans(mini, tier)
    store = enum.enumerate_tier(mini, tier)
    code_index, kz_final, _own, over_budget = _columns(store)
    grid = choices.kz_grid(n, code_index, kz_final, over_budget)
    expected = _in_budget(plans)
    assert expected
    assert len(grid) == 4 ** n
    for code in range(4 ** n):
        assert grid[code] == expected.get(code, -1), code


@pytest.mark.parametrize("tier", TIERS)
def test_mini_improvement_shares_and_swings_equal_brute_force(mini, tier):
    n = len(mini.measures)
    in_budget = _in_budget(_mini_plans(mini, tier))
    store = enum.enumerate_tier(mini, tier)
    code_index, kz_final, _own, over_budget = _columns(store)
    grid = choices.kz_grid(n, code_index, kz_final, over_budget)
    shares = choices.level_improvement_shares(grid, n)
    shift = 3
    swings = choices.level_swing_shares(grid, n, shift=shift)
    assert set(shares) == {(j, level) for j in range(n) for level in (1, 2, 3)}
    for j in range(n):
        for level in (1, 2, 3):
            contexts = improved = 0
            for code, kz in in_budget.items():
                if _digit(code, j, n) != level:
                    continue
                lowers = [in_budget[_replace(code, j, low, n)] for low in range(level) if _replace(code, j, low, n) in in_budget]
                if not lowers:
                    continue
                contexts += 1
                improved += kz > max(lowers)
            expected = Fraction(improved, contexts) if contexts else None
            assert shares[(j, level)] == expected, (j, level)
        groups = {}
        for code, kz in in_budget.items():
            groups.setdefault(_replace(code, j, 0, n), []).append(kz)
        multi = [values for values in groups.values() if len(values) >= 2]
        expected_swing = Fraction(sum(max(v) - min(v) >= shift for v in multi), len(multi)) if multi else None
        assert swings[j] == expected_swing, j
    assert choices.strictly_dominated(shares) == sorted(key for key, share in shares.items() if share == 0)


@pytest.mark.parametrize("tier", TIERS)
@pytest.mark.parametrize("band, min_size", [(5, 200), (5, 3), (2, 10), (0, 1), (100, 1)])
def test_mini_band_equals_brute_force(mini, tier, band, min_size):
    plans = _mini_plans(mini, tier)
    store = enum.enumerate_tier(mini, tier)
    code_index, kz_final, own_cost, over_budget = _columns(store)
    got = choices.near_optimal_band(code_index, kz_final, own_cost, over_budget, band=band, min_size=min_size)
    rows = sorted((-kz, own, code) for code, (kz, own, over) in plans.items() if not over)
    best = -rows[0][0]
    within = [row for row in rows if -row[0] >= best - band]
    chosen = within if len(within) >= min_size else rows[:min_size]
    assert got == [row[2] for row in chosen]


@pytest.mark.parametrize("tier", TIERS)
def test_mini_band_shares_and_near_mandatory_equal_brute_force(mini, tier):
    n = len(mini.measures)
    plans = _mini_plans(mini, tier)
    store = enum.enumerate_tier(mini, tier)
    code_index, kz_final, own_cost, over_budget = _columns(store)
    codes = choices.near_optimal_band(code_index, kz_final, own_cost, over_budget, band=5, min_size=3)
    shares = choices.band_shares(codes, n)
    for j in range(n):
        at_least_1 = sum(_digit(code, j, n) >= 1 for code in codes)
        at_least_2 = sum(_digit(code, j, n) >= 2 for code in codes)
        assert shares[j] == (Fraction(at_least_1, len(codes)), Fraction(at_least_2, len(codes)))
    for threshold in (Fraction(0), Fraction(1, 2), Fraction(9, 10)):
        assert choices.near_mandatory(shares, threshold) == [j for j in range(n) if shares[j][0] > threshold]


@pytest.mark.parametrize("tier", TIERS)
def test_mini_removal_drops_equal_a_recomputed_tier_best(mini, tier):
    n = len(mini.measures)
    in_budget = _in_budget(_mini_plans(mini, tier))
    store = enum.enumerate_tier(mini, tier)
    code_index, kz_final, _own, over_budget = _columns(store)
    grid = choices.kz_grid(n, code_index, kz_final, over_budget)
    drops = choices.removal_drops(grid, n)
    best = max(in_budget.values())
    for j in range(n):
        without = max((kz for code, kz in in_budget.items() if _digit(code, j, n) == 0), default=-1)
        assert drops[j] == best - without, j


def test_mini_tier_band_jaccard_equals_set_arithmetic(mini):
    bands = {}
    for tier in TIERS:
        store = enum.enumerate_tier(mini, tier)
        code_index, kz_final, own_cost, over_budget = _columns(store)
        bands[tier] = choices.near_optimal_band(code_index, kz_final, own_cost, over_budget, band=5, min_size=3)
    result = choices.tier_band_jaccard(bands)
    assert set(result) == set(itertools.combinations(TIERS, 2))
    for (a, b), value in result.items():
        assert value == Fraction(len(set(bands[a]) & set(bands[b])), len(set(bands[a]) | set(bands[b])))


# ---------------------------------------------------------------------------------------------------------------
# move layer: Kurswechsel spread and window-2 move effect
# ---------------------------------------------------------------------------------------------------------------


def _selection(cfg, index):
    return harness.selection_of(cfg, enum.code_from_index(index, len(cfg.measures)))


def _legal_games(cfg):
    """(start index, start selection, swap window or None, end selection): the swap layer built without TierTables."""
    ids = cfg.measure_ids
    for index in range(4 ** len(ids)):
        selection = _selection(cfg, index)
        if not rules.dependencies_satisfied(selection, cfg.measures):
            continue
        if not rules.swap_possible(selection):
            yield index, selection, None, selection
            continue
        for dropped, incoming, level in itertools.product(ids, ids, (1, 2, 3)):
            if selection[dropped] == 0 or selection[incoming] != 0:
                continue
            end = rules.swap_repair(selection, dropped, cfg.measures)
            end[incoming] = level
            if rules.dependencies_satisfied(end, cfg.measures):
                yield index, selection, rules.Window(end, (dropped, incoming)), end


def _windows(swap_window):
    return () if swap_window is None else (swap_window,)


@pytest.mark.parametrize("tier", TIERS)
@pytest.mark.parametrize("shift", [1, 3, 8])
def test_mini_kurswechsel_spread_equals_brute_force_over_the_swap_paths(mini, tier, shift):
    finals = {}
    for index, selection, swap_window, _end in _legal_games(mini):
        record = rules.evaluate_path(mini, tier, rules.Path(selection, _windows(swap_window)))
        if not record["over_budget"]:
            finals.setdefault(index, []).append(record["kz_final"])
    spreads = sorted(max(values) - min(values) for values in finals.values() if len(values) >= 2)
    assert spreads
    layer = enum.enumerate_swap_layer(mini, tier)
    got = choices.kurswechsel_spread(layer["starts"], shift=shift)
    assert got.starts == len(spreads)
    assert got.share == Fraction(sum(spread >= shift for spread in spreads), len(spreads))
    assert got.median == report.nearest_rank(spreads, 50)
    assert got.p90 == report.nearest_rank(spreads, 90)
    assert tuple(got) == (got.share, got.median, got.p90, got.starts)


def test_kurswechsel_spread_without_a_start_with_two_swaps_is_empty():
    starts = {
        "best_in_budget": array("b", [-1, 70]),
        "worst_in_budget": array("b", [-1, 70]),
        "in_budget_paths": array("I", [0, 1]),
    }
    got = choices.kurswechsel_spread(starts)
    assert got.starts == 0 and got.share is None and got.median is None and got.p90 is None


def test_kurswechsel_spread_on_a_synthetic_layer():
    starts = {
        "best_in_budget": array("b", [-1, 70, 80, 60]),
        "worst_in_budget": array("b", [-1, 70, 78, 40]),
        "in_budget_paths": array("I", [0, 1, 4, 2]),
    }
    got = choices.kurswechsel_spread(starts, shift=3)
    assert got == (Fraction(1, 2), 2, 20, 2)


def _window_brute(cfg, tier, stride):
    sample = 0
    improvements = []
    for index, selection, swap_window, end in _legal_games(cfg):
        if index % stride:
            continue
        base = rules.evaluate_path(cfg, tier, rules.Path(selection, _windows(swap_window)))
        if base["over_budget"]:
            continue
        first = swap_window if swap_window is not None else rules.Window(selection)
        best = base["kz_final"]
        for measure, level in itertools.product(cfg.measure_ids, range(4)):
            if level == end[measure]:
                continue
            target = dict(end)
            target[measure] = level
            if not rules.dependencies_satisfied(target, cfg.measures):
                continue
            moved = rules.evaluate_path(cfg, tier, rules.Path(selection, (first, rules.Window(target))))
            if not moved["over_budget"] and moved["kz_final"] > best:
                best = moved["kz_final"]
        sample += 1
        improvements.append(best - base["kz_final"])
    return sample, improvements


_WINDOW_CASES = [("low", 1), ("medium", 1), ("high", 1), ("low", 5), ("medium", 7), ("high", 3)]


@pytest.mark.parametrize("tier, stride", _WINDOW_CASES)
def test_mini_window_move_effect_equals_brute_force_over_two_windows(mini, tier, stride):
    sample, improvements = _window_brute(mini, tier, stride)
    assert sample > 0
    tables = rules.TierTables(mini, tier)
    got = choices.window_move_effect(tables, sample_stride=stride, shift=3)
    assert got.sample == sample
    assert got.share == Fraction(sum(value >= 3 for value in improvements), sample)
    assert got.mean == Fraction(sum(improvements), sample)
    assert got.maximum == max(improvements)
    assert tuple(got) == (got.share, got.mean, got.maximum, got.sample)


def test_window_move_effect_needs_three_waves_and_a_wave_one_kurswechsel(mini):
    tables = rules.TierTables(mini, "low")
    tables.wave_count = 4
    with pytest.raises(ValueError):
        choices.window_move_effect(tables, sample_stride=1)


@pytest.mark.parametrize("stride", [1, 3, 10])
def test_swap_paths_start_stride_keeps_exactly_the_strided_starts(mini, stride):
    tables = rules.TierTables(mini, "low")
    full = list(tables.swap_paths())
    assert list(tables.swap_paths(start_stride=stride)) == [path for path in full if path[0] % stride == 0]


# ---------------------------------------------------------------------------------------------------------------
# tier block, cross-tier comparison, criteria and report
# ---------------------------------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def mini_blocks(mini):
    blocks = {}
    for tier in TIERS:
        store = enum.enumerate_tier(mini, tier)
        blocks[tier] = choices.choices_tier(
            mini, tier, store, rules.TierTables(mini, tier), enum.enumerate_swap_layer(mini, tier), sample_stride=3
        )
    return blocks


@pytest.mark.parametrize("tier", TIERS)
def test_mini_choices_tier_aggregates_the_individual_metrics(mini, mini_blocks, tier):
    n = len(mini.measures)
    block = mini_blocks[tier]
    store = enum.enumerate_tier(mini, tier)
    code_index, kz_final, own_cost, over_budget = _columns(store)
    grid = choices.kz_grid(n, code_index, kz_final, over_budget)
    band = choices.near_optimal_band(code_index, kz_final, own_cost, over_budget)
    assert block["tier"] == tier
    assert block["measure_ids"] == list(mini.measure_ids)
    assert block["improvement"] == choices.level_improvement_shares(grid, n)
    assert block["dominated"] == choices.strictly_dominated(block["improvement"])
    assert block["swing"] == choices.level_swing_shares(grid, n)
    assert block["band"] == band
    assert block["band_shares"] == choices.band_shares(band, n)
    assert block["near_mandatory"] == choices.near_mandatory(block["band_shares"])
    assert block["drops"] == choices.removal_drops(grid, n)
    assert block["best_kz"] == max(grid)
    assert block["best_code"] == band[0]
    layer = enum.enumerate_swap_layer(mini, tier)
    assert block["kurswechsel"] == choices.kurswechsel_spread(layer["starts"])
    assert block["window"] == choices.window_move_effect(rules.TierTables(mini, tier), sample_stride=3)


def test_cross_tier_choices_reports_jaccard_and_identical_best_plans(mini_blocks):
    bands = {tier: block["band"] for tier, block in mini_blocks.items()}
    cross = choices.cross_tier_choices(mini_blocks, bands)
    assert cross["jaccard"] == choices.tier_band_jaccard(bands)
    expected = [
        (a, b) for a, b in itertools.combinations(TIERS, 2) if mini_blocks[a]["best_code"] == mini_blocks[b]["best_code"]
    ]
    assert cross["same_best"] == expected


def _ok_block(tier, best_code):
    return {
        "tier": tier,
        "measure_ids": ["M1", "M2"],
        "improvement": {(0, 1): Fraction(1, 2), (0, 2): Fraction(1, 3), (1, 1): Fraction(1, 4), (1, 2): None},
        "dominated": [],
        "swing": {0: Fraction(3, 4), 1: Fraction(1, 2)},
        "band": [best_code],
        "band_shares": {0: (Fraction(1, 2), Fraction(1, 4)), 1: (Fraction(9, 10), Fraction(0))},
        "near_mandatory": [],
        "drops": {0: 10, 1: 2},
        "best_kz": 95,
        "best_code": best_code,
        "kurswechsel": choices.KurswechselSpread(Fraction(99, 100), 29, 40, 1000),
        "window": choices.WindowMoveEffect(Fraction(3, 5), Fraction(6), 25, 40000),
    }


def _ok_blocks():
    return {"low": _ok_block("low", 5), "medium": _ok_block("medium", 6), "high": _ok_block("high", 7)}


def _disjoint_bands(blocks):
    for offset, block in enumerate(blocks.values()):
        block["band"] = [offset * 10 + 1, offset * 10 + 2]
        block["best_code"] = block["band"][0]


def test_check_choices_is_silent_on_a_healthy_set_of_blocks():
    blocks = _ok_blocks()
    _disjoint_bands(blocks)
    assert choices.check_choices(blocks) == []


def _failures(mutate):
    blocks = _ok_blocks()
    _disjoint_bands(blocks)
    mutate(blocks)
    return choices.check_choices(blocks)


def test_check_choices_names_a_strictly_dominated_level_in_german():
    lines = _failures(lambda b: b["medium"].update(dominated=[(1, 2)]))
    assert len(lines) == 1
    assert "dominiert" in lines[0] and "medium" in lines[0] and "M2" in lines[0] and "L2" in lines[0]


def test_check_choices_names_a_measure_with_too_small_a_swing_share():
    lines = _failures(lambda b: b["low"]["swing"].update({1: Fraction(2, 5)}))
    assert len(lines) == 1 and "low" in lines[0] and "M2" in lines[0]


def test_check_choices_names_a_near_mandatory_measure_with_its_share():
    def mutate(blocks):
        blocks["high"]["near_mandatory"] = [0]
        blocks["high"]["band_shares"][0] = (Fraction(19, 20), Fraction(1, 2))

    lines = _failures(mutate)
    assert len(lines) == 1 and "high" in lines[0] and "M1" in lines[0] and "zwingend" in lines[0]


def test_check_choices_flags_a_removal_drop_above_the_limit_only():
    assert _failures(lambda b: b["low"]["drops"].update({0: choices.OVERPOWERED_DROP})) == []
    lines = _failures(lambda b: b["low"]["drops"].update({0: choices.OVERPOWERED_DROP + 1}))
    assert len(lines) == 1 and "überstark" in lines[0] and "M1" in lines[0]


def test_check_choices_flags_overlapping_bands_and_identical_best_plans():
    def overlap(blocks):
        blocks["low"]["band"] = [1, 2]
        blocks["medium"]["band"] = [1, 2]

    lines = _failures(overlap)
    assert any("Jaccard" in line and "low" in line and "medium" in line for line in lines)

    def same_best(blocks):
        blocks["low"]["best_code"] = blocks["high"]["best_code"] = 77

    lines = _failures(same_best)
    assert any("bester Plan" in line and "low" in line and "high" in line for line in lines)


def test_check_choices_flags_weak_decision_points():
    lines = _failures(lambda b: b["medium"].update(kurswechsel=choices.KurswechselSpread(Fraction(2, 5), 1, 2, 10)))
    assert len(lines) == 1 and "Kurswechsel" in lines[0] and "medium" in lines[0]
    lines = _failures(lambda b: b["high"].update(window=choices.WindowMoveEffect(Fraction(1, 5), Fraction(1), 4, 10)))
    assert len(lines) == 1 and "Fenster" in lines[0] and "high" in lines[0]


def test_check_choices_criteria_are_individually_addressable():
    assert [name for name, _function in choices.CRITERIA] == [
        "dominated",
        "swing",
        "near_mandatory",
        "overpowered",
        "tiers",
        "kurswechsel",
        "window",
    ]
    blocks = _ok_blocks()
    _disjoint_bands(blocks)
    blocks["low"]["dominated"] = [(0, 2)]
    by_name = dict(choices.CRITERIA)
    assert len(by_name["dominated"](blocks)) == 1
    assert by_name["swing"](blocks) == []


def test_format_choices_is_german_and_names_the_worst_offenders(mini_blocks):
    text = choices.format_choices(mini_blocks)
    for tier in TIERS:
        assert tier in text
    assert "M1" in text
    assert "Band" in text and "Kurswechsel" in text and "Fenster" in text
