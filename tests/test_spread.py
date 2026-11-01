"""BAL-09 checks ("outcomes stay controlled"): tier corridor, best result below 100, spread per tier in a range.

The metrics are pure functions over report summaries. They are verified on handmade spreads, and `tier_spread` is
compared with a direct nearest-rank computation over the in-budget final KZ of the mini config; the slow checks run on
the config chosen with --planspiel-config, one check per criterion.
"""
import pytest

from planspiel import enumerate as enum
from planspiel import report, spread
from tests.support import REPO_ROOT, candidate, harness

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


# ---------------------------------------------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------------------------------------------


def test_thresholds_are_the_documented_proposals():
    assert spread.CORRIDOR_WIDTH == 6
    assert (spread.BEST_MIN, spread.BEST_MAX) == (90, 98)
    assert (spread.IQR_MIN, spread.IQR_MAX) == (13, 21)
    assert spread.IQR_TIER_DIFF == 4
    assert spread.P5_P95_MAX == 50
    assert spread.MEDIAN_START_MAX == 28


# ---------------------------------------------------------------------------------------------------------------
# tier_spread on handmade summaries
# ---------------------------------------------------------------------------------------------------------------


def _summary(tier="low", start=50, best=95, p5=40, p25=52, p50=63, p75=69, p95=80):
    return {
        "tier": tier,
        "kz_start": start,
        "best": {"in_budget": None if best is None else {"kz_final": best}},
        "percentiles": {
            "in_budget": {
                "count": 5,
                "kz_final": {"p0": 20, "p5": p5, "p25": p25, "p50": p50, "p75": p75, "p95": p95, "p100": 99},
            }
        },
    }


def test_tier_spread_reads_best_median_iqr_and_width_from_both_summaries():
    got = spread.tier_spread(_summary(best=98, p50=63), _summary(best=100, p50=60, p25=50, p75=66, p5=41, p95=77))
    assert got.tier == "low"
    assert got.kz_start == 50
    assert (got.best_static, got.best_legal) == (98, 100)
    assert (got.median_static, got.median_legal) == (63, 60)
    assert (got.iqr_static, got.iqr_legal) == (69 - 52, 66 - 50)
    assert (got.p5_p95_static, got.p5_p95_legal) == (80 - 40, 77 - 41)


def test_tier_spread_without_swap_summary_leaves_the_legal_fields_none():
    got = spread.tier_spread(_summary())
    assert got.best_legal is None and got.median_legal is None
    assert got.iqr_legal is None and got.p5_p95_legal is None


def test_tier_spread_without_in_budget_plans_gives_none():
    empty = _summary(best=None, p5=None, p25=None, p50=None, p75=None, p95=None)
    got = spread.tier_spread(empty, empty)
    assert got.best_static is None and got.median_static is None
    assert got.iqr_static is None and got.p5_p95_static is None
    assert got.best_legal is None and got.iqr_legal is None


# ---------------------------------------------------------------------------------------------------------------
# criteria on handmade spreads
# ---------------------------------------------------------------------------------------------------------------


def _spread(tier="low", start=50, best=(95, 95), median=(63, 62), iqr=(17, 16), width=(40, 38)):
    return spread.TierSpread(tier, start, best[0], best[1], median[0], median[1], iqr[0], iqr[1], width[0], width[1])


def _good():
    return {
        "low": _spread("low", 50, (95, 95), (63, 60), (17, 16), (38, 36)),
        "medium": _spread("medium", 42, (96, 96), (65, 62), (17, 17), (43, 40)),
        "high": _spread("high", 34, (97, 97), (60, 58), (17, 17), (46, 45)),
    }


def test_check_spread_passes_on_values_inside_every_range():
    assert spread.check_spread(_good()) == []


def test_check_spread_passes_at_the_inclusive_limits():
    spreads = {
        "low": _spread("low", 50, (90, 90), (60, 60), (13, 13), (50, 50)),
        "medium": _spread("medium", 42, (93, 93), (62, 62), (17, 17), (50, 50)),
        "high": _spread("high", 34, (96, 96), (62, 62), (17, 17), (50, 50)),
    }  # best corridor 6, median corridor 2, IQR 13..17 (difference 4), high median is exactly start + 28
    assert spread.check_spread(spreads) == []


def test_best_corridor_names_the_layer_when_the_width_exceeds_the_limit():
    spreads = _good()
    spreads["low"] = spreads["low"]._replace(best_static=91)
    spreads["high"] = spreads["high"]._replace(best_static=98)
    lines = spread.check_corridor(spreads)
    assert len(lines) == 1
    assert "statisch" in lines[0] and "Bestes" in lines[0]


def test_best_corridor_passes_at_exactly_the_width():
    spreads = _good()
    spreads["low"] = spreads["low"]._replace(best_legal=92)
    spreads["high"] = spreads["high"]._replace(best_legal=98)
    assert spread.check_corridor(spreads) == []


def test_median_corridor_is_checked_per_layer():
    spreads = _good()
    spreads["low"] = spreads["low"]._replace(median_legal=50)
    spreads["high"] = spreads["high"]._replace(median_legal=57)
    lines = spread.check_corridor(spreads)
    assert len(lines) == 1
    assert "Median" in lines[0] and "legal" in lines[0]


def test_both_corridors_fail_independently():
    spreads = _good()
    spreads["low"] = spreads["low"]._replace(best_static=90, median_static=50)
    spreads["high"] = spreads["high"]._replace(best_static=98, median_static=60)
    assert len(spread.check_corridor(spreads)) == 2


def test_best_band_names_tier_and_layer_for_a_best_above_the_maximum():
    spreads = _good()
    spreads["medium"] = spreads["medium"]._replace(best_static=99, best_legal=100)
    lines = spread.check_best_band(spreads)
    assert len(lines) == 2
    assert all("medium" in line for line in lines)
    assert any("statisch" in line for line in lines) and any("legal" in line for line in lines)


def test_best_band_names_a_best_below_the_minimum():
    spreads = _good()
    spreads["low"] = spreads["low"]._replace(best_legal=89)
    lines = spread.check_best_band(spreads)
    assert len(lines) == 1 and "low" in lines[0] and "89" in lines[0]


def test_iqr_outside_the_range_names_tier_and_layer():
    spreads = _good()
    spreads["low"] = spreads["low"]._replace(iqr_static=12, iqr_legal=22)
    spreads["medium"] = spreads["medium"]._replace(iqr_static=14, iqr_legal=20)
    spreads["high"] = spreads["high"]._replace(iqr_static=14, iqr_legal=20)  # tier differences stay within 4
    lines = spread.check_iqr(spreads)
    assert len(lines) == 2
    assert any("12" in line and "statisch" in line for line in lines)
    assert any("22" in line and "legal" in line for line in lines)


def test_iqr_tier_difference_above_the_limit_fails_per_layer():
    spreads = _good()
    spreads["low"] = spreads["low"]._replace(iqr_static=14)
    spreads["high"] = spreads["high"]._replace(iqr_static=19)
    lines = spread.check_iqr(spreads)
    assert len(lines) == 1
    assert "Unterschied" in lines[0] and "statisch" in lines[0]


def test_iqr_tier_difference_passes_at_exactly_the_limit():
    spreads = _good()
    spreads["low"] = spreads["low"]._replace(iqr_static=14)
    spreads["high"] = spreads["high"]._replace(iqr_static=18)
    assert spread.check_iqr(spreads) == []


def test_width_above_the_limit_names_tier_and_layer():
    spreads = _good()
    spreads["high"] = spreads["high"]._replace(p5_p95_static=51)
    lines = spread.check_width(spreads)
    assert len(lines) == 1 and "high" in lines[0] and "51" in lines[0] and "statisch" in lines[0]


def test_median_bound_names_the_tier_with_the_median_too_far_above_start():
    spreads = _good()
    spreads["high"] = spreads["high"]._replace(median_static=34 + 29)
    lines = spread.check_median_bound(spreads)
    assert len(lines) == 1 and "high" in lines[0] and "29" in lines[0]


def test_median_bound_passes_at_exactly_the_limit():
    spreads = _good()
    spreads["high"] = spreads["high"]._replace(median_static=34 + 28, median_legal=34 + 28)
    assert spread.check_median_bound(spreads) == []


def test_none_legal_fields_are_skipped_by_every_criterion():
    spreads = {
        tier: s._replace(best_legal=None, median_legal=None, iqr_legal=None, p5_p95_legal=None)
        for tier, s in _good().items()
    }
    assert spread.check_spread(spreads) == []


def test_none_static_fields_fail_with_a_german_line():
    spreads = _good()
    spreads["low"] = spreads["low"]._replace(best_static=None, median_static=None, iqr_static=None, p5_p95_static=None)
    lines = spread.check_spread(spreads)
    assert len(lines) == 1
    assert "low" in lines[0] and "keine Pläne im Budget" in lines[0]


def test_check_spread_collects_every_criterion():
    spreads = _good()
    spreads["low"] = spreads["low"]._replace(best_static=100, iqr_static=30, p5_p95_static=60, median_static=90)
    lines = spread.check_spread(spreads)
    assert len(lines) >= 5  # corridor best, corridor median, band, iqr range, width, median bound ...


def test_format_spread_lists_every_tier_and_marks_missing_legal_values():
    spreads = _good()
    spreads["high"] = spreads["high"]._replace(best_legal=None, median_legal=None, iqr_legal=None, p5_p95_legal=None)
    text = spread.format_spread(spreads)
    for tier in TIERS:
        assert tier in text
    assert "nicht berechnet" in text


# ---------------------------------------------------------------------------------------------------------------
# mini config: tier_spread equals a direct nearest-rank computation
# ---------------------------------------------------------------------------------------------------------------


def _in_budget_finals(store):
    return sorted(kz for kz, over in zip(store.column("kz_final"), store.column("over_budget")) if not over)


def _expand(histogram):
    return [value for value, count in enumerate(histogram) for _ in range(count)]


@pytest.mark.parametrize("tier", TIERS)
def test_mini_tier_spread_equals_a_direct_nearest_rank_computation(mini, tier):
    store = enum.enumerate_tier(mini, tier)
    static = report.summarize_tier(mini, tier, store, 3)
    layer = enum.enumerate_swap_layer(mini, tier)
    swap = report.summarize_swap_layer(mini, tier, layer)
    got = spread.tier_spread(static, swap)

    finals = _in_budget_finals(store)
    legal = _expand(layer["histogram"]["in_budget"])
    assert got.tier == tier
    assert got.kz_start == mini.budget_tiers[tier].kz_start
    for values, best, median, iqr, width in (
        (finals, got.best_static, got.median_static, got.iqr_static, got.p5_p95_static),
        (legal, got.best_legal, got.median_legal, got.iqr_legal, got.p5_p95_legal),
    ):
        assert best == values[-1]
        assert median == report.nearest_rank(values, 50)
        assert iqr == report.nearest_rank(values, 75) - report.nearest_rank(values, 25)
        assert width == report.nearest_rank(values, 95) - report.nearest_rank(values, 5)


# ---------------------------------------------------------------------------------------------------------------
# slow checks on the configured (real or candidate) config
# ---------------------------------------------------------------------------------------------------------------

_SPREADS = {}


def _balance_spreads(path):
    key = str(path)
    if key not in _SPREADS:
        cfg = candidate.load_balance_config(path)
        statics = candidate.static_summaries(path)
        layers = candidate.swap_layers(path)
        _SPREADS[key] = {
            tier: spread.tier_spread(statics[tier], report.summarize_swap_layer(cfg, tier, layers[tier]))
            for tier in statics
        }
    return _SPREADS[key]


def _assert_criterion(path, criterion):
    spreads = _balance_spreads(path)
    lines = spread.check_missing(spreads) + criterion(spreads)
    assert not lines, "\n".join(lines) + "\n\n" + spread.format_spread(spreads)


@pytest.mark.slow
@pytest.mark.balance
def test_best_and_median_inside_tier_corridor(balance_config_path):
    _assert_criterion(balance_config_path, spread.check_corridor)


@pytest.mark.slow
@pytest.mark.balance
def test_best_in_budget_inside_d11_band(balance_config_path):
    _assert_criterion(balance_config_path, spread.check_best_band)


@pytest.mark.slow
@pytest.mark.balance
def test_iqr_inside_range(balance_config_path):
    _assert_criterion(balance_config_path, spread.check_iqr)


@pytest.mark.slow
@pytest.mark.balance
def test_p5_p95_width_bounded(balance_config_path):
    _assert_criterion(balance_config_path, spread.check_width)


@pytest.mark.slow
@pytest.mark.balance
def test_median_not_too_far_above_start(balance_config_path):
    _assert_criterion(balance_config_path, spread.check_median_bound)
