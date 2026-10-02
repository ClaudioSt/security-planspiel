"""RoS counts the team's own security spend only; event cost effects never enter it (RULE-06, D-21)."""
import json
from fractions import Fraction

import pytest

from planspiel import analyze, rules
from planspiel.config import load_config
from planspiel.enumerate import ResultStore
from planspiel.report import dump_record
from planspiel.rounding import exact_to_json
from tests.support import REPO_ROOT, harness

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"

OPEX_VALUES = (-2, 0, 3)
BUDGET_VALUES = (-20, 0, 15)


def test_security_spend_sums_init_opex_and_window_costs():
    assert rules.security_spend(250, (40, 40, 40)) == 370
    assert rules.security_spend(250, (40, 30, 30), (20,)) == 360
    assert rules.security_spend(0, ()) == 0


def test_budget_ledger_in_budget_carries_both_totals():
    ledger = rules.budget_ledger(400, 250, -12, -20)
    assert ledger == rules.BudgetLedger(
        total_cost=238, budget_available=380, over_budget=False, remaining_budget=142, security_spend=250
    )


def test_budget_ledger_over_budget_carries_both_totals():
    assert rules.budget_ledger(400, 400, -2, -20) == rules.BudgetLedger(398, 380, True, -18, 400)


def test_budget_ledger_equality_stays_in_budget():
    assert rules.budget_ledger(380, 380, 0, 0).over_budget is False


def test_ros_denominator_is_own_spend():
    assert rules.ros(620, Fraction(96), 250) == Fraction(137, 125)
    assert rules.ros(620, 0, 0) is None


@pytest.mark.parametrize("tier", TIERS)
def test_real_config_costs_split_into_own_spend_and_event_opex(tier):
    cfg = harness.load_config()
    base = rules.base_losses(cfg.waves, cfg.attacks)
    cases = json.loads((GOLDEN_DIR / f"characterization_{tier}.json").read_text(encoding="utf-8"))["cases"]
    checked = 0
    for case in cases:
        if not case["valid"]:
            continue
        rec = harness.evaluate(cfg, tier, harness.selection_of(cfg, case["code"]))
        costs = rec["costs"]
        assert costs["security_spend"] == costs["init"] + costs["opex_per_wave"] * len(cfg.waves)
        assert costs["total"] == costs["security_spend"] + costs["event_opex"]
        assert rec["ros"] == rules.ros(base, rec["total_damage"], costs["security_spend"])
        checked += 1
    assert checked > 0


def test_evaluate_plan_costs_key_order():
    cfg = harness.load_config()
    rec = harness.evaluate(cfg, "medium", harness.selection_of(cfg, "0" * len(cfg.measure_ids)))
    assert list(rec["costs"]) == [
        "init",
        "opex_per_wave",
        "security_spend",
        "total",
        "event_opex",
        "event_budget",
        "budget_available",
    ]


def _variant_config(tmp_path, opex, budget):
    data = json.loads(MINI.read_text(encoding="utf-8"))
    for events in data["events"].values():
        for event in events:
            if event["id"] == "operative_unterstuetzung":
                event["opex_per_measure"] = opex
            if event["id"] == "sparprogramm":
                event["budget_delta"] = budget
    path = tmp_path / f"mini_{opex}_{budget}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return load_config(path)


def _ros_by_code(cfg, tier):
    result = {}
    for code in harness.iter_codes(cfg):
        rec = harness.evaluate(cfg, tier, harness.selection_of(cfg, code))
        if not rec["valid"]:
            continue
        spend = rec["costs"]["security_spend"]
        assert (rec["ros"] is None) == (spend == 0)
        result[code] = rec["ros"]
    return result


@pytest.mark.parametrize("tier", TIERS)
def test_ros_is_invariant_under_event_cost_effects(tmp_path, tier):
    reference = _ros_by_code(_variant_config(tmp_path, 0, 0), tier)
    assert reference
    for opex in OPEX_VALUES:
        for budget in BUDGET_VALUES:
            assert _ros_by_code(_variant_config(tmp_path, opex, budget), tier) == reference


def test_event_variants_do_change_the_budget_total(tmp_path):
    cfg = _variant_config(tmp_path, 3, 15)
    base = _variant_config(tmp_path, 0, 0)
    selection = harness.selection_of(cfg, "1111")
    changed = harness.evaluate(cfg, "medium", selection)
    plain = harness.evaluate(base, "medium", selection)
    assert changed["costs"]["security_spend"] == plain["costs"]["security_spend"]
    assert changed["costs"]["total"] != plain["costs"]["total"]
    assert changed["costs"]["budget_available"] != plain["costs"]["budget_available"]


def test_store_ros_uses_own_cost_not_total():
    store = ResultStore(620)
    store.append(
        0,
        rules.CompactOutcome(
            kz_final=80, own_cost=100, total_cost=110, damage_eur=12345, event_opex=10,
            event_budget=0, over_budget=False, kz_after=(80, 80, 80),
        ),
    )
    assert store.record(0).ros == rules.ros(620, Fraction(12345, 1000), 100)


def test_dump_record_ros_uses_own_cost():
    mini = harness.load_config(MINI)
    base = rules.base_losses(mini.waves, mini.attacks)
    outcome = rules.CompactOutcome(
        kz_final=70, own_cost=100, total_cost=104, damage_eur=5000, event_opex=4,
        event_budget=0, over_budget=False, kz_after=(70, 70, 70),
    )
    record = dump_record(mini.measure_ids, 5, outcome, base)
    assert record["ros"] == exact_to_json(rules.ros(base, Fraction(5), 100))


def test_analyze_item_ros_uses_security_spend():
    item = {"total_damage": 96, "costs": {"security_spend": 250, "total": 238, "event_opex": -12}}
    assert analyze.item_ros(item, 620) == rules.ros(620, 96, 250)


def test_analyze_item_ros_falls_back_for_legacy_records():
    item = {"total_damage": 96, "costs": {"total": 238, "event_opex": -12}}
    assert analyze.item_ros(item, 620) == rules.ros(620, 96, 250)
