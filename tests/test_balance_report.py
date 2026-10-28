"""BAL-04: in-budget top-K and Pareto in the tier summary, the consolidated balance report and its CLI.

The in-budget sections are compared with an independent brute force over `rules.evaluate_plan` (through the
enumeration test helpers); the consolidated report is exercised on the mini config and mini content.
"""
import pytest

from planspiel.enumerate import ResultStore, enumerate_tier
from planspiel.report import format_console, pareto_front, summarize_tier
from tests.support import REPO_ROOT, harness
from tests.test_enumeration import _brute_pareto, _brute_records, _entry, _outcome, _without_rank

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
MINI_CONTENT = REPO_ROOT / "tests" / "fixtures" / "mini_content"


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


# ---------------------------------------------------------------------------------------------------------------
# Task 1: in-budget top-K and Pareto
# ---------------------------------------------------------------------------------------------------------------


def test_pareto_front_in_budget_only_skips_over_budget_rows():
    store = ResultStore(620)
    rows = [
        # code_index, own cost, kz, over budget
        (0, 10, 50, False),
        (1, 8, 90, True),
        (2, 12, 60, False),
        (3, 12, 60, False),
        (4, 9, 40, False),
        (5, 20, 55, False),
    ]
    for code_index, own, kz, over in rows:
        store.append(code_index, _outcome(kz, own, over=over))
    full = pareto_front(store)
    assert [(p["own_cost"], p["kz_final"]) for p in full] == [(8, 90)]
    points = pareto_front(store, in_budget_only=True)
    assert [(p["own_cost"], p["kz_final"], p["combinations"], p["example_index"]) for p in points] == [
        (9, 40, 1, 4),
        (10, 50, 1, 0),
        (12, 60, 2, 2),
    ]


@pytest.mark.parametrize("tier", TIERS)
def test_pareto_in_budget_matches_brute_force(mini, tier):
    store = enumerate_tier(mini, tier)
    records = [r for r in _brute_records(mini, tier) if not r["over"]]
    expected = _brute_pareto(records)
    points = pareto_front(store, in_budget_only=True)
    assert [(p["own_cost"], p["kz_final"], p["combinations"], p["example_index"]) for p in points] == expected


@pytest.mark.parametrize("tier", TIERS)
def test_top_in_budget_is_the_in_budget_prefix_of_the_sort_orders(mini, tier):
    top_k = 5
    summary = summarize_tier(mini, tier, enumerate_tier(mini, tier), top_k=top_k)
    in_budget = [r for r in _brute_records(mini, tier) if not r["over"]]
    orderings = {
        "kz_final": sorted(in_budget, key=lambda r: (-r["kz"], r["own"], r["damage"], r["index"])),
        "ros": sorted(
            (r for r in in_budget if r["ros"] is not None),
            key=lambda r: (-r["ros"], -r["kz"], r["own"], r["index"]),
        ),
        "final_index": sorted(in_budget, key=lambda r: (-r["fi"], -r["kz"], r["own"], r["index"])),
    }
    assert list(summary["top_in_budget"]) == ["kz_final", "ros", "final_index"]
    for name, ordering in orderings.items():
        got = summary["top_in_budget"][name]
        assert all(entry["over_budget"] is False for entry in got)
        assert [e["rank"] for e in got] == list(range(1, len(got) + 1))
        assert [_without_rank(e) for e in got] == [_entry(r) for r in ordering[:top_k]]


@pytest.mark.parametrize("tier", TIERS)
def test_pareto_in_budget_summary_block(mini, tier):
    summary = summarize_tier(mini, tier, enumerate_tier(mini, tier), top_k=3)
    block = summary["pareto_in_budget"]
    records = [r for r in _brute_records(mini, tier) if not r["over"]]
    expected = _brute_pareto(records)
    assert block["objectives"] == {"kz_final": "max", "own_cost": "min"}
    assert block["count"] == len(expected) == len(block["points"])
    got = [
        (p["own_cost"], p["kz_final"], p["combinations"], int(p["example"]["code"], 4)) for p in block["points"]
    ]
    assert got == expected
    assert all(p["example"]["over_budget"] is False for p in block["points"])


def test_unfiltered_sections_and_format_stay_as_before(mini):
    summary = summarize_tier(mini, "low", enumerate_tier(mini, "low"), top_k=4)
    assert summary["format"] == 1
    assert len(summary["top"]["kz_final"]) == 4
    assert summary["pareto"]["count"] == len(summary["pareto"]["points"])
    assert summary["best"]["in_budget"] is not None
    assert summary["best"]["over_budget"] is not None


def test_format_console_prints_the_in_budget_sections(mini):
    text = format_console(summarize_tier(mini, "low", enumerate_tier(mini, "low")))
    assert "Top im Budget nach End-KZ" in text
    assert "Top im Budget nach RoS" in text
    assert "Top im Budget nach Final-Index" in text
    assert "Pareto-Front im Budget" in text
    assert "Bestes Ergebnis (End-KZ): im Budget" in text
