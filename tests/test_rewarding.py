"""BAL-08 checks ("das Spiel ist insgesamt belohnend"): mediocre ends positive, comeback after wave 1 is possible.

The metrics are pure functions over report summaries, the swap-layer start aggregates and TierTables. `comeback` is
compared with an independent brute force on the mini config (wave-1 KZ from `rules.evaluate_plan`, continuations from
`rules.evaluate_path`); the slow checks run on the config chosen with --planspiel-config.
"""
import itertools
from array import array
from fractions import Fraction
from types import SimpleNamespace

import pytest

from planspiel import enumerate as enum
from planspiel import report, rewarding, rules
from tests.support import REPO_ROOT, candidate, harness

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


# ---------------------------------------------------------------------------------------------------------------
# constants and median margins
# ---------------------------------------------------------------------------------------------------------------


def test_thresholds_are_the_documented_proposals():
    assert rewarding.MEDIAN_MARGIN == 5
    assert rewarding.COMEBACK_DROP == 5
    assert rewarding.COMEBACK_GAIN == 10
    assert rewarding.COMEBACK_SHARE == Fraction(9, 10)


def _summary(p50, kz_start=50):
    kz_final = {"p50": p50} if p50 is not None else {"p50": None}
    return {"kz_start": kz_start, "percentiles": {"in_budget": {"count": 0 if p50 is None else 7, "kz_final": kz_final}}}


def test_median_margins_are_the_in_budget_p50_minus_the_start_kz():
    assert rewarding.median_margins(_summary(63), _summary(60)) == (13, 10)


def test_median_margins_can_be_negative():
    assert rewarding.median_margins(_summary(45), _summary(50)) == (-5, 0)


def test_median_margins_without_in_budget_plans_are_none_for_that_layer():
    assert rewarding.median_margins(_summary(None), _summary(60)) == (None, 10)
    assert rewarding.median_margins(_summary(63), _summary(None)) == (13, None)


# ---------------------------------------------------------------------------------------------------------------
# comeback on a synthetic layer
# ---------------------------------------------------------------------------------------------------------------


_KZ_AFTER_ONE = {1: 49, 2: 45, 3: 44, 4: 30}


def _fake_outcome(codes, window_cost_total):
    assert window_cost_total == 0
    assert len(codes) == 3 and len(set(codes)) == 1
    return SimpleNamespace(kz_after=(_KZ_AFTER_ONE[codes[0]], 0, 0))


class _FakeTables:
    """Five states: state 0 is invalid; wave-1 KZ after the start 50: states 1..4 end at 49, 45, 44, 30."""

    wave_count = 3
    tier = SimpleNamespace(kz_start=50)
    valid = bytearray([0, 1, 1, 1, 1])
    # a game formula is defined once in rules.py (test_single_definition), so the stub gets it as an attribute
    path_outcome = staticmethod(_fake_outcome)


def _starts(best, paths):
    return {
        "best_in_budget": array("b", best),
        "worst_in_budget": array("b", best),
        "in_budget_paths": array("I", paths),
    }


def test_comeback_on_a_synthetic_layer():
    # hit starts (drop 5): 2 (45), 3 (44), 4 (30); state 3 has no in-budget continuation
    starts = _starts([-1, 80, 60, -1, 55], [0, 3, 2, 0, 1])
    got = rewarding.comeback(_FakeTables(), starts)
    assert got.hit == 3
    assert got.with_continuation == 2
    assert got.without_continuation == 1
    assert got.share_gain == Fraction(1, 2)  # best 60 >= 60 yes, best 55 >= 60 no
    assert got.share_above_start == Fraction(1)  # 60 > 50, 55 > 50
    assert got.median_best == 55
    assert got.p90_best == 60


def test_comeback_threshold_is_inclusive_and_above_start_is_strict():
    starts = _starts([-1, 80, 60, -1, 50], [0, 3, 2, 0, 1])
    got = rewarding.comeback(_FakeTables(), starts)
    assert got.share_gain == Fraction(1, 2)
    assert got.share_above_start == Fraction(1, 2)  # 50 is not above the start KZ 50


def test_comeback_drop_is_inclusive():
    starts = _starts([-1, 80, 60, 70, 55], [0, 3, 2, 1, 1])
    assert rewarding.comeback(_FakeTables(), starts, drop=5).hit == 3  # 45 <= 45 is a hit, 49 is not
    assert rewarding.comeback(_FakeTables(), starts, drop=6).hit == 2  # only 44 and 30
    assert rewarding.comeback(_FakeTables(), starts, drop=1).hit == 4


def test_comeback_without_hit_starts_has_no_shares():
    starts = _starts([-1, 80, 60, 70, 55], [0, 3, 2, 1, 1])
    got = rewarding.comeback(_FakeTables(), starts, drop=40)
    assert got == (0, 0, 0, None, None, None, None)


def test_comeback_with_hit_starts_but_no_continuation_has_no_shares():
    starts = _starts([-1, 80, -1, -1, -1], [0, 3, 0, 0, 0])
    got = rewarding.comeback(_FakeTables(), starts)
    assert (got.hit, got.with_continuation, got.without_continuation) == (3, 0, 3)
    assert got.share_gain is None and got.share_above_start is None
    assert got.median_best is None and got.p90_best is None


# ---------------------------------------------------------------------------------------------------------------
# comeback equals a brute force on the mini config
# ---------------------------------------------------------------------------------------------------------------


def _selection(cfg, index):
    return harness.selection_of(cfg, enum.code_from_index(index, len(cfg.measures)))


def _valid_starts(cfg):
    for index in range(4 ** len(cfg.measure_ids)):
        selection = _selection(cfg, index)
        if rules.dependencies_satisfied(selection, cfg.measures):
            yield index, selection


def _continuations(cfg, selection):
    """End selections and swap windows of every legal Kurswechsel path of a start (empty if no swap is legal)."""
    if not rules.swap_possible(selection):
        yield ()
        return
    ids = cfg.measure_ids
    for dropped, incoming, level in itertools.product(ids, ids, (1, 2, 3)):
        if selection[dropped] == 0 or selection[incoming] != 0:
            continue
        end = rules.swap_repair(selection, dropped, cfg.measures)
        end[incoming] = level
        if rules.dependencies_satisfied(end, cfg.measures):
            yield (rules.Window(end, (dropped, incoming)),)


def _brute_comeback(cfg, tier, drop, gain):
    kz_start = cfg.budget_tiers[tier].kz_start
    hit = 0
    bests = []
    for _index, selection in _valid_starts(cfg):
        after_one = rules.evaluate_plan(cfg, tier, selection)["waves"][0]["kz_after"]
        if after_one > kz_start - drop:
            continue
        hit += 1
        finals = []
        for windows in _continuations(cfg, selection):
            record = rules.evaluate_path(cfg, tier, rules.Path(selection, windows))
            if not record["over_budget"]:
                finals.append(record["kz_final"])
        if finals:
            bests.append(max(finals))
    return kz_start, hit, sorted(bests)


@pytest.mark.parametrize("tier", TIERS)
@pytest.mark.parametrize("drop,gain", [(1, 1), (2, 5), (3, 3), (5, 10), (8, 2)])
def test_mini_comeback_equals_brute_force(mini, tier, drop, gain):
    tables = rules.TierTables(mini, tier)
    layer = enum.enumerate_swap_layer(mini, tier)
    got = rewarding.comeback(tables, layer["starts"], drop=drop, gain=gain)
    kz_start, hit, bests = _brute_comeback(mini, tier, drop, gain)
    assert got.hit == hit
    assert got.with_continuation == len(bests)
    assert got.without_continuation == hit - len(bests)
    if bests:
        assert got.share_gain == Fraction(sum(best >= kz_start + gain for best in bests), len(bests))
        assert got.share_above_start == Fraction(sum(best > kz_start for best in bests), len(bests))
        assert got.median_best == report.nearest_rank(bests, 50)
        assert got.p90_best == report.nearest_rank(bests, 90)
    else:
        assert got.share_gain is None and got.median_best is None


def test_mini_config_has_hit_starts_with_and_without_continuation_somewhere(mini):
    totals = []
    for tier in TIERS:
        tables = rules.TierTables(mini, tier)
        layer = enum.enumerate_swap_layer(mini, tier)
        totals.append(rewarding.comeback(tables, layer["starts"], drop=1, gain=1))
    assert any(got.hit > 0 for got in totals)
    assert any(got.with_continuation > 0 for got in totals)


def test_mini_rewarding_tier_collects_the_margins_and_the_comeback(mini):
    tier = "medium"
    store = enum.enumerate_tier(mini, tier)
    static = report.summarize_tier(mini, tier, store, 3)
    layer = enum.enumerate_swap_layer(mini, tier)
    swap = report.summarize_swap_layer(mini, tier, layer)
    tables = rules.TierTables(mini, tier)
    block = rewarding.rewarding_tier(mini, tier, static, swap, tables, layer)
    assert block["tier"] == tier
    assert block["kz_start"] == mini.budget_tiers[tier].kz_start
    assert (block["static_margin"], block["legal_margin"]) == rewarding.median_margins(static, swap)
    assert block["comeback"] == rewarding.comeback(tables, layer["starts"])


# ---------------------------------------------------------------------------------------------------------------
# check_rewarding and format_rewarding
# ---------------------------------------------------------------------------------------------------------------


def _comeback(share_gain=Fraction(19, 20), hit=100, with_continuation=100):
    return rewarding.ComebackResult(
        hit, with_continuation, hit - with_continuation, share_gain, Fraction(1), 70, 80
    )


def _block(static=13, legal=10, comeback=None):
    return {
        "tier": "low",
        "kz_start": 50,
        "static_margin": static,
        "legal_margin": legal,
        "comeback": _comeback() if comeback is None else comeback,
    }


def test_check_rewarding_passes_on_values_at_the_thresholds():
    blocks = {"low": _block(static=5, legal=5, comeback=_comeback(share_gain=Fraction(9, 10)))}
    assert rewarding.check_rewarding(blocks) == []


def test_check_rewarding_names_a_static_margin_below_the_threshold():
    lines = rewarding.check_rewarding({"low": _block(static=4)})
    assert len(lines) == 1
    assert "low" in lines[0] and "statisch" in lines[0] and "4" in lines[0]


def test_check_rewarding_names_a_legal_margin_below_the_threshold():
    lines = rewarding.check_rewarding({"medium": _block(legal=-2)})
    assert len(lines) == 1
    assert "medium" in lines[0] and "Tausch" in lines[0] and "-2" in lines[0]


def test_check_rewarding_names_a_comeback_share_below_the_threshold():
    lines = rewarding.check_rewarding({"high": _block(comeback=_comeback(share_gain=Fraction(89, 100)))})
    assert len(lines) == 1
    assert "high" in lines[0] and "Comeback" in lines[0]


def test_check_rewarding_fails_when_a_layer_has_no_in_budget_plan():
    lines = rewarding.check_rewarding({"low": _block(static=None, legal=None)})
    assert len(lines) == 2
    assert all("Budget" in line for line in lines)


def test_check_rewarding_fails_when_hit_starts_have_no_continuation_at_all():
    blocks = {"low": _block(comeback=_comeback(share_gain=None, hit=4, with_continuation=0))}
    assert len(rewarding.check_rewarding(blocks)) == 1


def test_check_rewarding_accepts_a_tier_without_hit_starts():
    blocks = {"low": _block(comeback=rewarding.ComebackResult(0, 0, 0, None, None, None, None))}
    assert rewarding.check_rewarding(blocks) == []


def test_check_rewarding_collects_every_failure_across_tiers():
    blocks = {"low": _block(static=0), "medium": _block(legal=0), "high": _block(comeback=_comeback(Fraction(1, 2)))}
    assert len(rewarding.check_rewarding(blocks)) == 3


def test_format_rewarding_reports_every_tier_in_german():
    blocks = {"low": _block(), "medium": _block(static=None)}
    text = rewarding.format_rewarding(blocks)
    assert "low" in text and "medium" in text
    assert "Comeback" in text and "Median" in text
    assert "keine Pläne im Budget" in text


# ---------------------------------------------------------------------------------------------------------------
# slow checks on the configured (real or candidate) config
# ---------------------------------------------------------------------------------------------------------------

_BLOCKS = {}


def _balance_blocks(path):
    key = str(path)
    if key not in _BLOCKS:
        cfg = candidate.load_balance_config(path)
        statics = candidate.static_summaries(path)
        layers = candidate.swap_layers(path)
        _BLOCKS[key] = {
            tier: rewarding.rewarding_tier(
                cfg,
                tier,
                statics[tier],
                report.summarize_swap_layer(cfg, tier, layers[tier]),
                candidate.tier_tables(path, tier),
                layers[tier],
            )
            for tier in statics
        }
    return _BLOCKS[key]


def _failures(path, prefix):
    blocks = _balance_blocks(path)
    return [line for line in rewarding.check_rewarding(blocks) if prefix(line)], rewarding.format_rewarding(blocks)


@pytest.mark.slow
@pytest.mark.balance
def test_median_ends_above_start_on_both_layers(balance_config_path):
    failures, text = _failures(balance_config_path, lambda line: "Median" in line)
    assert not failures, "\n".join(failures) + "\n\n" + text


@pytest.mark.slow
@pytest.mark.balance
def test_comeback_after_wave_one_is_possible(balance_config_path):
    failures, text = _failures(balance_config_path, lambda line: "Comeback" in line)
    assert not failures, "\n".join(failures) + "\n\n" + text
