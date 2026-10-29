"""BAL-04: in-budget top-K and Pareto in the tier summary, the consolidated balance report and its CLI.

The in-budget sections are compared with an independent brute force over `rules.evaluate_plan` (through the
enumeration test helpers); the consolidated report is exercised on the mini config and mini content.
"""
import json
from fractions import Fraction

import pytest

from planspiel import balance
from planspiel.config import FinalIndexWeights
from planspiel.enumerate import ResultStore, enumerate_tier
from planspiel.report import format_console, pareto_front, summarize_tier
from planspiel.rounding import exact_to_json
from planspiel.validate import ConfigError
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


# ---------------------------------------------------------------------------------------------------------------
# Task 2: consolidated report
# ---------------------------------------------------------------------------------------------------------------

NOT_COMPUTED = "nicht berechnet (nur mit --layers all)"
TIER_BLOCKS = ["distribution", "gate", "choices", "strategies", "rewarding", "spread_input"]
CROSS_BLOCKS = ["spread", "choices", "final_index", "hand_calc", "clue_mapping"]


@pytest.fixture(scope="module")
def static_report():
    return balance.build_balance_report(MINI, MINI_CONTENT, layers="static")


@pytest.fixture(scope="module")
def full_report():
    return balance.build_balance_report(MINI, MINI_CONTENT, layers="all", paths=True)


def _all_blocks(report):
    for tier, blocks in report["tiers"].items():
        for name, block in blocks.items():
            yield f"{name} {tier}", block
    for name, block in report["cross_tier"].items():
        yield name, block


def test_static_report_structure(static_report):
    report = static_report
    assert {"config", "content_dir", "layers", "tiers", "cross_tier", "verdict"} <= set(report)
    assert report["layers"] == "static"
    assert list(report["tiers"]) == list(TIERS)
    for blocks in report["tiers"].values():
        assert list(blocks) == TIER_BLOCKS
    assert list(report["cross_tier"]) == CROSS_BLOCKS
    for _name, block in _all_blocks(report):
        assert set(block) >= {"passed", "failures", "data"}
        assert block["passed"] in (True, False, None)
        assert isinstance(block["failures"], list)


def test_static_report_marks_swap_dependent_parts_as_not_computed(static_report):
    for tier, blocks in static_report["tiers"].items():
        for name in ("choices", "strategies", "rewarding"):
            block = blocks[name]
            assert block["passed"] is None and block["data"] is None and block["failures"] == []
            assert block["note"] == NOT_COMPUTED
        assert blocks["distribution"]["data"]["legal"] is None
    choices = static_report["cross_tier"]["choices"]
    assert choices["passed"] is None and choices["note"] == NOT_COMPUTED
    assert "calibration" not in static_report["cross_tier"]
    assert static_report["tiers"]["low"]["gate"]["data"]["paths"] is None


def test_verdict_is_the_conjunction_of_the_computed_blocks(static_report, full_report):
    for report in (static_report, full_report):
        failed = [name for name, block in _all_blocks(report) if block["passed"] is False]
        verdict = report["verdict"]
        assert verdict["passed"] is (not failed)
        assert verdict["failed_checks"] == len(failed)
        expected = [
            line for _name, block in _all_blocks(report) if block["passed"] is False for line in block["failures"]
        ]
        assert len(verdict["failures"]) == len(expected)
        for line in expected:
            assert any(entry.endswith(line) for entry in verdict["failures"])


def test_full_report_computes_every_block(full_report):
    assert full_report["layers"] == "all"
    for tier, blocks in full_report["tiers"].items():
        for name in ("choices", "strategies", "rewarding"):
            assert blocks[name]["passed"] in (True, False), (tier, name)
            assert blocks[name]["data"] is not None
        assert blocks["distribution"]["data"]["legal"] is not None
        assert blocks["gate"]["data"]["paths"] is not None
        assert set(blocks["gate"]["data"]["paths"]) >= {"tausch", "fenster1", "fenster2"}
        assert blocks["spread_input"]["data"].best_static is not None
    assert list(full_report["cross_tier"]) == CROSS_BLOCKS + ["calibration"]
    assert full_report["cross_tier"]["choices"]["passed"] in (True, False)
    static_gate = full_report["tiers"]["low"]["gate"]["data"]["static"]
    assert full_report["cross_tier"]["calibration"]["data"].config_x == static_gate.config_x


def test_distribution_carries_the_in_budget_sections(static_report):
    summary = static_report["tiers"]["low"]["distribution"]["data"]["static"]
    assert summary["tier"] == "low"
    assert summary["top_in_budget"]["kz_final"]
    assert all(not entry["over_budget"] for entry in summary["top_in_budget"]["final_index"])
    assert summary["pareto_in_budget"]["count"] >= 1


def _without_final_index(value):
    if isinstance(value, dict):
        return {key: _without_final_index(item) for key, item in value.items() if key != "final_index"}
    if isinstance(value, list):
        return [_without_final_index(item) for item in value]
    return value


def test_index_weights_override_changes_only_final_index_based_values(static_report):
    heavy = FinalIndexWeights(Fraction(1), Fraction(20))
    other = balance.build_balance_report(MINI, MINI_CONTENT, layers="static", index_weights=heavy)
    assert static_report["index_weights_source"] == "Konfiguration"
    assert other["index_weights_source"] == "Kandidat"
    for tier in TIERS:
        before = static_report["tiers"][tier]["distribution"]["data"]["static"]
        after = other["tiers"][tier]["distribution"]["data"]["static"]
        assert before["top_in_budget"]["final_index"] != after["top_in_budget"]["final_index"]
        for key in ("percentiles", "best", "pareto", "pareto_in_budget", "combinations"):
            assert _without_final_index(before[key]) == _without_final_index(after[key])
        for group in ("top", "top_in_budget"):
            for name in ("kz_final", "ros"):
                assert _without_final_index(before[group][name]) == _without_final_index(after[group][name])
        assert static_report["tiers"][tier]["gate"]["data"]["static"] == other["tiers"][tier]["gate"]["data"]["static"]
    old_block = static_report["cross_tier"]["final_index"]["data"]
    new_block = other["cross_tier"]["final_index"]["data"]
    assert old_block["k"] == new_block["k"]
    assert new_block["weight_ros"] == 20
    assert new_block["configured_weights"] == old_block["configured_weights"]


def test_unknown_tier_is_rejected():
    with pytest.raises(ValueError, match="nope"):
        balance.build_balance_report(MINI, MINI_CONTENT, tiers=["nope"])


def test_malformed_config_raises_instead_of_a_partial_verdict(tmp_path):
    raw = json.loads(MINI.read_text(encoding="utf-8"))
    del raw["budget_tiers"]
    broken = tmp_path / "broken.json"
    broken.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises((ConfigError, KeyError)):
        balance.build_balance_report(broken, MINI_CONTENT)


def test_missing_clue_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        balance.build_balance_report(MINI, tmp_path)


def test_report_json_is_serializable_and_exact(full_report):
    data = balance.report_json(full_report)
    text = json.dumps(data, ensure_ascii=False)
    back = json.loads(text)
    assert back["layers"] == "all"
    assert back["verdict"]["passed"] is full_report["verdict"]["passed"]
    block = back["cross_tier"]["final_index"]["data"]
    assert block["k_raw"] == exact_to_json(full_report["cross_tier"]["final_index"]["data"]["k_raw"])
    assert back["tiers"]["low"]["gate"]["data"]["static"]["tier"] == "low"


def test_config_diff_example_and_sorting():
    old = {"a": {"b": 1, "c": [1, 2]}}
    new = {"a": {"b": 2, "c": [1, 3]}, "d": 4}
    assert balance.config_diff(old, new) == [("a.b", 1, 2), ("a.c[1]", 2, 3), ("d", balance.MISSING, 4)]


def test_config_diff_covers_removed_keys_longer_lists_and_type_changes():
    old = {"x": 1, "y": [1], "z": {"k": 1}}
    new = {"y": [1, 2], "z": 5}
    assert balance.config_diff(old, new) == [
        ("x", 1, balance.MISSING),
        ("y[1]", balance.MISSING, 2),
        ("z", {"k": 1}, 5),
    ]
    assert balance.config_diff(old, old) == []


def test_config_diff_treats_equal_numbers_of_different_types_as_equal():
    assert balance.config_diff({"a": Fraction(1)}, {"a": 1}) == []


def test_format_config_diff_lists_paths_old_and_new():
    text = balance.format_config_diff([("a.b", 1, 2), ("d", balance.MISSING, Fraction(1, 2))])
    assert "a.b" in text and "d" in text
    assert "fehlt" in text
    assert "→" in text
    assert balance.format_config_diff([]) == "keine"


def test_compare_reports_of_identical_reports_has_equal_columns(static_report):
    rows = balance.compare_reports(static_report, static_report)
    assert rows
    assert all(old == new for _metric, _tier, old, new in rows)
    metrics = {metric for metric, _tier, _old, _new in rows}
    assert any("Nötiges X" in metric for metric in metrics)
    assert any("Bestes End-KZ im Budget" in metric for metric in metrics)
    assert any("Median" in metric for metric in metrics)
    assert any("Interquartilsabstand" in metric for metric in metrics)
    assert any("KZ-Anteil" in metric for metric in metrics)
    assert any("Information" in metric for metric in metrics)


def test_compare_reports_includes_swap_dependent_metrics_and_calibration(full_report):
    rows = balance.compare_reports(full_report, full_report)
    metrics = {metric for metric, _tier, _old, _new in rows}
    assert any("Band-Anteil" in metric for metric in metrics)
    assert any("Wegfall" in metric for metric in metrics)
    assert any("Strategie" in metric for metric in metrics)
    assert any("Empfohlenes X" in metric for metric in metrics)
    assert any("legale" in metric for metric in metrics)


def test_compare_reports_shows_a_changed_value(tmp_path, static_report):
    raw = json.loads(MINI.read_text(encoding="utf-8"))
    raw["budget_tiers"]["low"]["kz_start"] = raw["budget_tiers"]["low"]["kz_start"] - 3
    edited = tmp_path / "edited.json"
    edited.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    other = balance.build_balance_report(edited, MINI_CONTENT, layers="static")
    rows = balance.compare_reports(static_report, other)
    assert any(old != new for _metric, tier, old, new in rows if tier == "low")


def test_format_comparison_prints_a_table(static_report):
    text = balance.format_comparison(balance.compare_reports(static_report, static_report))
    assert "vorher" in text and "nachher" in text
    assert "low" in text


def test_format_balance_report_is_german_and_ends_with_the_verdict(static_report, full_report):
    for report in (static_report, full_report):
        text = balance.format_balance_report(report)
        assert "Referenzplan ohne Change-Fenster-Züge" in text
        assert "Tier low" in text and "Tier high" in text
        verdict = report["verdict"]
        tail = text[text.index("Gesamturteil:"):]
        if verdict["passed"]:
            assert tail.startswith("Gesamturteil: alle berechneten Prüfungen bestanden")
        else:
            assert tail.startswith(f"Gesamturteil: {verdict['failed_checks']} Prüfung(en) nicht bestanden")
            for line in verdict["failures"]:
                assert line in tail
    assert NOT_COMPUTED in balance.format_balance_report(static_report)


def test_removed_hard_coded_strategy_list():
    assert not hasattr(balance, "POSITIVE_KZ_THRESHOLD")
    assert not hasattr(balance, "define_strategies")
    assert not hasattr(balance, "run_analysis")
