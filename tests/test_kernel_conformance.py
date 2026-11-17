"""The compact tier kernel computes exactly what `rules.evaluate_plan` computes (FOUND-06; T-01-19)."""
import copy
import json
import random
from fractions import Fraction

import pytest

from planspiel import rules
from tests.support import CONFIG_PATH, REPO_ROOT, harness
from tests.support.digest import compute_digest
from tests.support.ties import NEGATIVE_TIE_EVENT, tie_codes, write_tie_config

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"


def _golden_cases(tier):
    path = REPO_ROOT / "tests" / "golden" / f"characterization_{tier}.json"
    return json.loads(path.read_text(encoding="utf-8"))["cases"]


def _expected(cfg, tier, selection):
    record = harness.evaluate(cfg, tier, selection)
    if not record["valid"]:
        return None
    return harness.compact_from_plan(cfg, record)


def _digest_view(outcome):
    if outcome is None:
        return {"valid": False}
    return {
        "valid": True,
        "kz_final": outcome.kz_final,
        "total_damage": Fraction(outcome.damage_eur, 1000),
        "costs": {"total": outcome.total_cost},
        "total_event_opex": outcome.event_opex,
        "total_event_budget": outcome.event_budget,
        "waves": [{"kz_after": kz} for kz in outcome.kz_after],
        "over_budget": outcome.over_budget,
    }


def test_budget_ledger_in_budget():
    ledger = rules.budget_ledger(400, 250, -12, -20)
    assert ledger == rules.BudgetLedger(
        total_cost=238, budget_available=380, over_budget=False, remaining_budget=142, security_spend=250
    )


def test_budget_ledger_over_budget():
    ledger = rules.budget_ledger(400, 400, -2, -20)
    assert ledger == rules.BudgetLedger(398, 380, True, -18, 400)


def test_budget_ledger_equality_stays_in_budget():
    assert rules.budget_ledger(380, 380, 0, 0).over_budget is False


def test_apply_final_events_boundary_is_inclusive():
    cfg = harness.load_config()
    kz, records = rules.apply_final_events(cfg.final_events, {}, 25, 50)
    assert kz == 50 + dict((remaining, delta) for remaining, delta in cfg.final_events[0].params["tiers"])[25]
    assert len(records) == 1
    assert list(records[0]) == ["id", "name", "effect_description", "kz_delta"]


def test_apply_final_events_negative_remaining_budget():
    cfg = harness.load_config()
    x, _ = rules.penalty_params(cfg.final_events)
    assert rules.apply_final_events(cfg.final_events, {}, -1, 50)[0] == 50 - x


def test_apply_final_events_clamps():
    cfg = harness.load_config()
    top = cfg.final_events[0].params["tiers"][-1][1]
    assert rules.apply_final_events(cfg.final_events, {}, 75, 100 - top + 1)[0] == 100


@pytest.mark.parametrize("tier", TIERS)
def test_kernel_equals_evaluate_plan_on_golden_cases(tier):
    cfg = harness.load_config()
    kernel = rules.TierKernel(cfg, tier)
    for case in _golden_cases(tier):
        selection = harness.selection_of(cfg, case["code"])
        outcome = kernel.evaluate(selection)
        assert (outcome is None) == (not case["valid"]), case["code"]
        assert outcome == _expected(cfg, tier, selection), case["code"]


@pytest.mark.parametrize("tier", TIERS)
def test_kernel_equals_evaluate_plan_on_mini_config(tier):
    cfg = harness.load_config(MINI)
    kernel = rules.TierKernel(cfg, tier)
    invalid = 0
    for code in harness.iter_codes(cfg):
        selection = harness.selection_of(cfg, code)
        outcome = kernel.evaluate(selection)
        if outcome is None:
            invalid += 1
            assert not rules.dependencies_satisfied(selection, cfg.measures)
        assert outcome == _expected(cfg, tier, selection), code
    failing = sum(
        1
        for code in harness.iter_codes(cfg)
        if not rules.dependencies_satisfied(harness.selection_of(cfg, code), cfg.measures)
    )
    assert invalid == failing > 0


@pytest.mark.parametrize("tier", TIERS)
def test_kernel_equals_evaluate_plan_on_random_real_codes(tier):
    cfg = harness.load_config()
    kernel = rules.TierKernel(cfg, tier)
    rng = random.Random(20260930)
    picked = 0
    while picked < 500:
        code = "".join(str(rng.randrange(4)) for _ in cfg.measures)
        selection = harness.selection_of(cfg, code)
        if not rules.dependencies_satisfied(selection, cfg.measures):
            continue
        picked += 1
        assert kernel.evaluate(selection) == _expected(cfg, tier, selection), code


@pytest.mark.parametrize("tier", TIERS)
def test_kernel_equals_evaluate_plan_on_negative_tie_override(tier, tmp_path):
    cfg = harness.load_config(write_tie_config(tmp_path, [NEGATIVE_TIE_EVENT]))
    kernel = rules.TierKernel(cfg, tier)
    codes = tie_codes(cfg, tier, count=3, positive=False) + tie_codes(cfg, tier, count=3, positive=True)
    for code in codes:
        selection = harness.selection_of(cfg, code)
        assert kernel.evaluate(selection) == _expected(cfg, tier, selection), code


def test_kernel_memoization_never_changes_a_result():
    cfg = harness.load_config()
    kernel = rules.TierKernel(cfg, "medium")
    for case in _golden_cases("medium")[:60]:
        if not case["valid"]:
            continue
        selection = harness.selection_of(cfg, case["code"])
        first = kernel.evaluate(selection)
        assert first is not None
        assert kernel.evaluate(selection) == first


@pytest.mark.slow
@pytest.mark.parametrize("tier", TIERS)
def test_kernel_digest_matches_golden(tier):
    cfg = harness.load_config()
    kernel = rules.TierKernel(cfg, tier)
    got = compute_digest(cfg, tier, evaluate=lambda _c, _t, sel: _digest_view(kernel.evaluate(sel)))
    want = json.loads((REPO_ROOT / "tests" / "golden" / f"digest_{tier}.json").read_text(encoding="utf-8"))
    if got != want:
        bins = [i for i, (a, b) in enumerate(zip(got["kz_histogram"], want["kz_histogram"])) if a != b][:10]
        print(f"count={got['count']} in_budget={got['in_budget']} differing histogram bins: {bins}")
    assert got == want
