"""Compact result store and enumeration report, checked against an independent brute force (FOUND-06)."""
import json
import subprocess
import sys
from fractions import Fraction

import pytest

from planspiel import rules
from planspiel.enumerate import (
    LEVEL_OPTIONS,
    STORE_LAYOUT,
    CompactRecord,
    ResultStore,
    code_from_index,
    enumerate_tier,
    iter_selections,
)
from planspiel.report import (
    DEFAULT_TOP_K,
    PERCENTILES,
    dump_record,
    format_console,
    nearest_rank,
    pareto_front,
    summarize_tier,
    write_summary,
)
from planspiel.rounding import exact_to_json
from planspiel.simulate import run_simulation
from tests.support import REPO_ROOT, harness

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
ENTRY_KEYS = [
    "code",
    "selection",
    "kz_final",
    "own_cost",
    "total_cost",
    "total_damage",
    "ros",
    "final_index",
    "over_budget",
]


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


def _outcome(kz, own, total=None, damage=0, over=False, kz_pre_review=None, remaining=0):
    return rules.CompactOutcome(
        kz_final=kz,
        own_cost=own,
        total_cost=own if total is None else total,
        damage_eur=damage,
        event_opex=0,
        event_budget=0,
        over_budget=over,
        kz_after=(kz, kz, kz),
        kz_pre_review=kz if kz_pre_review is None else kz_pre_review,
        remaining=remaining,
    )


def _brute_records(cfg, tier):
    base = rules.base_losses(cfg.waves, cfg.attacks)
    records = []
    for code in harness.iter_codes(cfg):
        rec = harness.evaluate(cfg, tier, harness.selection_of(cfg, code))
        if not rec["valid"]:
            continue
        outcome = harness.compact_from_plan(cfg, rec)
        ros = rules.ros(base, rec["total_damage"], outcome.own_cost)
        records.append(
            {
                "code": code,
                "index": int(code, 4),
                "selection": rec["selection"],
                "kz": outcome.kz_final,
                "own": outcome.own_cost,
                "total": outcome.total_cost,
                "damage": rec["total_damage"],
                "ros": ros,
                "fi": rules.final_index(outcome.kz_final, ros),
                "over": outcome.over_budget,
            }
        )
    return records


def _entry(r):
    return {
        "code": r["code"],
        "selection": r["selection"],
        "kz_final": r["kz"],
        "own_cost": r["own"],
        "total_cost": r["total"],
        "total_damage": exact_to_json(r["damage"]),
        "ros": None if r["ros"] is None else exact_to_json(r["ros"]),
        "final_index": exact_to_json(r["fi"]),
        "over_budget": r["over"],
    }


def _without_rank(entry):
    return {key: value for key, value in entry.items() if key != "rank"}


def _brute_nearest(values, p):
    if not values:
        return None
    return values[max(0, -(-(p * len(values)) // 100) - 1)]


def _brute_group(records):
    kz = sorted(r["kz"] for r in records)
    ros = sorted(r["ros"] for r in records if r["ros"] is not None)
    return {
        "count": len(records),
        "kz_final": {f"p{p}": _brute_nearest(kz, p) for p in PERCENTILES},
        "ros_count": len(ros),
        "ros": {
            f"p{p}": None if not ros else exact_to_json(_brute_nearest(ros, p)) for p in PERCENTILES
        },
    }


def _brute_pareto(records):
    pairs = {}
    for r in records:
        pairs.setdefault((r["own"], r["kz"]), []).append(r["index"])
    front = []
    for (cost, kz), indices in pairs.items():
        dominated = any(
            (c2 <= cost and k2 >= kz) and (c2, k2) != (cost, kz) for (c2, k2) in pairs
        )
        if not dominated:
            front.append((cost, kz, len(indices), min(indices)))
    return sorted(front)


def test_code_from_index():
    assert code_from_index(int("0000012313", 4), 10) == "0000012313"
    assert code_from_index(0, 4) == "0000"
    assert code_from_index(255, 4) == "3333"


def test_code_from_index_follows_iter_selections_order(mini):
    for index, selection in enumerate(iter_selections(mini.measure_ids, LEVEL_OPTIONS)):
        assert harness.code_of(mini, selection) == code_from_index(index, 4)


def test_store_layout_and_record_roundtrip():
    store = ResultStore(620)
    assert tuple((name, store.column(name).typecode) for name, _ in STORE_LAYOUT) == STORE_LAYOUT
    assert store.bytes_per_record == 19
    store.append(7, _outcome(80, 100, total=110, damage=12345, over=True, kz_pre_review=95, remaining=-890))
    record = store.record(0)
    assert isinstance(record, CompactRecord)
    assert record.code_index == 7
    assert record.kz_final == 80
    assert record.own_cost == 100
    assert record.total_cost == 110
    assert record.damage_eur == 12345
    assert record.over_budget is True
    assert record.kz_pre_review == 95
    assert record.remaining == -890
    assert record.ros == rules.ros(620, Fraction(12345, 1000), 100)
    assert len(store) == 1


def test_store_ros_is_none_at_cost_zero():
    store = ResultStore(620)
    store.append(0, _outcome(50, 0))
    assert store.record(0).ros is None


def test_store_refuses_to_wrap_out_of_range_values():
    store = ResultStore(620)
    with pytest.raises(OverflowError):
        store.append(0, _outcome(50, 70000))
    with pytest.raises(OverflowError):
        store.append(0, _outcome(50, 10, remaining=40000))
    with pytest.raises(OverflowError):
        store.append(0, _outcome(50, 10, remaining=-40000))


@pytest.mark.parametrize("tier", TIERS)
def test_enumerate_tier_matches_evaluate_plan(mini, tier):
    seen = []
    store = enumerate_tier(mini, tier, on_outcome=lambda index, outcome: seen.append((index, outcome)))
    expected = _brute_records(mini, tier)
    assert len(store) == len(expected) == len(seen)
    for position, r in enumerate(expected):
        record = store.record(position)
        assert record.code_index == r["index"]
        assert record.kz_final == r["kz"]
        assert record.own_cost == r["own"]
        assert record.total_cost == r["total"]
        assert record.damage_eur == r["damage"] * 1000
        assert bool(record.over_budget) == r["over"]
        assert record.ros == r["ros"]
        index, outcome = seen[position]
        assert index == r["index"]
        assert outcome == harness.compact_from_plan(
            mini, harness.evaluate(mini, tier, harness.selection_of(mini, r["code"]))
        )


def test_nearest_rank():
    values = list(range(1, 21))
    got = [nearest_rank(values, p) for p in (0, 5, 25, 50, 75, 95, 100)]
    assert got == [1, 1, 5, 10, 15, 19, 20]
    assert [nearest_rank([7], p) for p in PERCENTILES] == [7] * len(PERCENTILES)
    assert nearest_rank([], 50) is None


def test_pareto_front_synthetic():
    store = ResultStore(620)
    rows = [
        (4, 10, 50),
        (2, 10, 50),
        (6, 12, 50),
        (3, 15, 60),
        (7, 9, 40),
        (1, 20, 60),
        (5, 8, 30),
        (0, 9, 35),
    ]
    for code_index, own, kz in rows:
        store.append(code_index, _outcome(kz, own))
    points = pareto_front(store)
    assert [(p["own_cost"], p["kz_final"], p["combinations"], p["example_index"]) for p in points] == [
        (8, 30, 1, 5),
        (9, 40, 1, 7),
        (10, 50, 2, 2),
        (15, 60, 1, 3),
    ]


@pytest.mark.parametrize("tier", TIERS)
def test_summary_matches_brute_force(mini, tier):
    top_k = 5
    summary = summarize_tier(mini, tier, enumerate_tier(mini, tier), top_k=top_k)
    records = _brute_records(mini, tier)
    in_budget = [r for r in records if not r["over"]]
    over = [r for r in records if r["over"]]

    assert summary["tier"] == tier
    assert summary["measures"] == mini.measure_ids
    assert summary["top_k"] == top_k
    assert summary["combinations"] == {
        "total": 4 ** len(mini.measure_ids),
        "valid": len(records),
        "in_budget": len(in_budget),
        "over_budget": len(over),
    }

    by_kz = sorted(records, key=lambda r: (-r["kz"], r["own"], r["damage"], r["index"]))
    by_ros = sorted(
        (r for r in records if r["ros"] is not None), key=lambda r: (-r["ros"], -r["kz"], r["own"], r["index"])
    )
    by_fi = sorted(records, key=lambda r: (-r["fi"], -r["kz"], r["own"], r["index"]))
    for name, ordering in (("kz_final", by_kz), ("ros", by_ros), ("final_index", by_fi)):
        got = summary["top"][name]
        assert [e["rank"] for e in got] == list(range(1, top_k + 1))
        assert [_without_rank(e) for e in got] == [_entry(r) for r in ordering[:top_k]]
    assert list(summary["top"]["kz_final"][0]) == ["rank", *ENTRY_KEYS]

    assert summary["percentiles"]["method"] == "nearest-rank"
    assert summary["percentiles"]["p"] == list(PERCENTILES)
    assert summary["percentiles"]["in_budget"] == _brute_group(in_budget)
    assert summary["percentiles"]["over_budget"] == _brute_group(over)

    best_in = sorted(in_budget, key=lambda r: (-r["kz"], r["own"], r["damage"], r["index"]))[0]
    best_over = sorted(over, key=lambda r: (-r["kz"], r["own"], r["damage"], r["index"]))[0]
    assert summary["best"]["metric"] == "kz_final"
    assert summary["best"]["in_budget"] == _entry(best_in)
    assert summary["best"]["over_budget"] == _entry(best_over)
    assert summary["best"]["kz_gap"] == best_over["kz"] - best_in["kz"]

    expected_front = _brute_pareto(records)
    assert summary["pareto"]["objectives"] == {"kz_final": "max", "own_cost": "min"}
    assert summary["pareto"]["count"] == len(expected_front) == len(summary["pareto"]["points"])
    got_front = [
        (p["own_cost"], p["kz_final"], p["combinations"], int(p["example"]["code"], 4))
        for p in summary["pareto"]["points"]
    ]
    assert got_front == expected_front


def test_zero_cost_plan_has_no_ros_and_final_index_equals_kz(mini):
    summary = summarize_tier(mini, "low", enumerate_tier(mini, "low"), top_k=1000)
    records = _brute_records(mini, "low")
    zero = [r for r in records if r["own"] == 0]
    assert len(zero) == 1
    code = zero[0]["code"]
    assert code not in [e["code"] for e in summary["top"]["ros"]]
    kz_entry = next(e for e in summary["top"]["kz_final"] if e["code"] == code)
    assert kz_entry["ros"] is None
    assert kz_entry["final_index"] == kz_entry["kz_final"]
    ros_counted = sum(summary["percentiles"][group]["ros_count"] for group in ("in_budget", "over_budget"))
    assert ros_counted == len(records) - len(zero)


def test_summary_is_deterministic_and_has_no_timing(mini):
    first = summarize_tier(mini, "medium", enumerate_tier(mini, "medium"))
    second = summarize_tier(mini, "medium", enumerate_tier(mini, "medium"))
    assert json.dumps(first, ensure_ascii=False) == json.dumps(second, ensure_ascii=False)
    assert first["top_k"] == DEFAULT_TOP_K
    assert list(first) == [
        "format",
        "tier",
        "budget",
        "kz_start",
        "measures",
        "combinations",
        "top_k",
        "final_index_status",
        "top",
        "percentiles",
        "best",
        "pareto",
    ]


def test_write_summary_is_utf8_lf_and_roundtrips(mini, tmp_path):
    summary = summarize_tier(mini, "high", enumerate_tier(mini, "high"))
    path = tmp_path / "summary.json"
    write_summary(path, summary)
    raw = path.read_bytes()
    assert b"\r" not in raw
    assert raw.endswith(b"\n")
    assert json.loads(raw.decode("utf-8")) == summary


def test_format_console_labels(mini):
    text = format_console(summarize_tier(mini, "low", enumerate_tier(mini, "low")))
    for label in ("Pareto-Front", "im Budget", "über Budget", "Final-Index (vorläufig)", "Perzentile"):
        assert label in text


def test_dump_record_keys(mini):
    base = rules.base_losses(mini.waves, mini.attacks)
    record = dump_record(mini.measure_ids, 5, _outcome(70, 100, total=104, damage=5000), base)
    assert list(record) == [
        "code",
        "kz_final",
        "kz_pre_review",
        "kz_after",
        "own_cost",
        "total_cost",
        "remaining",
        "total_damage",
        "ros",
        "final_index",
        "over_budget",
    ]
    assert record["code"] == "0011"
    assert record["kz_after"] == [70, 70, 70]
    assert record["kz_pre_review"] == 70
    assert record["remaining"] == 0
    json.dumps(record)


def _run_cli(args, cwd):
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "simulate_outcomes.py"), *args],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _valid_count(cfg):
    return sum(
        1
        for code in harness.iter_codes(cfg)
        if rules.dependencies_satisfied(harness.selection_of(cfg, code), cfg.measures)
    )


def test_cli_default_mode_writes_only_the_summary(mini, tmp_path):
    result = _run_cli(["--config", str(MINI), "--budget-tier", "low"], tmp_path)
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert sorted(path.name for path in tmp_path.iterdir()) == ["simulation_summary_low.json"]
    summary = json.loads((tmp_path / "simulation_summary_low.json").read_text(encoding="utf-8"))
    assert summary["combinations"]["valid"] == _valid_count(mini)
    assert "Pareto-Front" in result.stdout.decode("utf-8")


def test_cli_dump_jsonl_is_complete_and_ascending(mini, tmp_path):
    result = _run_cli(
        ["--config", str(MINI), "--budget-tier", "low", "--dump-jsonl", "dump.jsonl"], tmp_path
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert (tmp_path / "simulation_summary_low.json").is_file()
    lines = (tmp_path / "dump.jsonl").read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines]
    assert len(records) == _valid_count(mini)
    codes = [int(record["code"], 4) for record in records]
    assert codes == sorted(set(codes))
    assert {record["over_budget"] for record in records} == {True, False}


def test_cli_output_keeps_the_legacy_mode(tmp_path):
    result = _run_cli(["--config", str(MINI), "--budget-tier", "low", "--output", "legacy.json"], tmp_path)
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert sorted(path.name for path in tmp_path.iterdir()) == ["legacy.json"]
    data = json.loads((tmp_path / "legacy.json").read_text(encoding="utf-8"))
    assert sorted(data) == ["results", "summary"]


@pytest.mark.parametrize(
    "args",
    [
        ["--budget-utilization", "0.85"],
        ["--budget-min", "10"],
        ["--budget-max", "100"],
        ["--output", "a.json", "--dump-jsonl", "b.jsonl"],
        ["--output", "a.json", "--summary", "s.json"],
        ["--output", "a.json", "--top", "3"],
        ["--top", "0"],
    ],
)
def test_cli_rejects_inconsistent_flags(args, tmp_path):
    result = _run_cli(["--config", str(MINI), "--budget-tier", "low", *args], tmp_path)
    assert result.returncode == 2
    assert list(tmp_path.iterdir()) == []


def test_cli_rejection_message_names_output_flag(tmp_path):
    result = _run_cli(["--config", str(MINI), "--budget-utilization", "0.85"], tmp_path)
    assert "--output" in result.stderr.decode("utf-8", errors="replace")


def test_cli_unknown_tier_lists_tier_names(tmp_path):
    result = _run_cli(["--config", str(MINI), "--budget-tier", "huge"], tmp_path)
    assert result.returncode == 2
    stderr = result.stderr.decode("utf-8", errors="replace")
    for name in ("low", "medium", "high"):
        assert name in stderr


def test_cli_top_flag_controls_list_length(tmp_path):
    result = _run_cli(["--config", str(MINI), "--budget-tier", "medium", "--top", "3"], tmp_path)
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    summary = json.loads((tmp_path / "simulation_summary_medium.json").read_text(encoding="utf-8"))
    assert summary["top_k"] == 3
    assert [len(summary["top"][key]) for key in ("kz_final", "ros", "final_index")] == [3, 3, 3]


def test_budget_max_only_scales_the_utilization_threshold(tmp_path):
    out = tmp_path / "out.json"
    summary = run_simulation(MINI, "low", out, None, 100, 0.0)
    assert summary["budget_filter"] == {"min": 0, "max": 100, "utilization_min": None}
    results = json.loads(out.read_text(encoding="utf-8"))["results"]
    assert any(record["costs"]["total"] > 100 for record in results)

    summary = run_simulation(MINI, "low", out, None, 100, 0.5)
    assert summary["budget_filter"]["utilization_min"] == 50
    results = json.loads(out.read_text(encoding="utf-8"))["results"]
    assert results
    assert all(record["costs"]["total"] >= 50 for record in results)
