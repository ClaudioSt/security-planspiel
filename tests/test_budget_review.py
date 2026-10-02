"""Budget Review: linear overspend penalty instead of the flat -15 (RULE-03, D-14, D-15, D-25)."""
import copy
import json

import pytest

from planspiel import rules
from planspiel.review_text import format_eur, penalty_rows
from planspiel.rounding import started_steps
from planspiel.validate import validate
from tests.support import CONFIG_PATH, REPO_ROOT, harness

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
TIERS = ("low", "medium", "high")
MINUS = "−"

TIERS_WITH_SENTINEL = [[-100000, -15], [0, 0], [25, 5], [50, 10], [75, 15]]
TIERS_WITHOUT_SENTINEL = [[0, 0], [25, 5], [50, 10], [75, 15]]

DELTA_CASES = (
    (0, 0),
    (24, 0),
    (25, 5),
    (50, 10),
    (75, 15),
    (-1, -9),
    (-10, -9),
    (-11, -18),
    (-20, -18),
    (-21, -27),
)


def _raw(path=CONFIG_PATH):
    return json.loads(path.read_text(encoding="utf-8"))


def _errors(issues):
    return [issue for issue in issues if issue.level == "error"]


def _warnings(issues):
    return [issue for issue in issues if issue.level == "warning"]


def _penalty(raw):
    return raw["final_events"][0]["overspend_penalty"]


@pytest.mark.parametrize("tiers", [TIERS_WITH_SENTINEL, TIERS_WITHOUT_SENTINEL], ids=["sentinel", "no-sentinel"])
@pytest.mark.parametrize(("remaining", "expected"), DELTA_CASES)
def test_budget_review_delta_boundaries(tiers, remaining, expected):
    assert rules.budget_review_delta(remaining, tiers, 9, 10) == expected


def test_flat_tier_no_longer_decides_over_budget():
    assert rules.budget_review_delta(-1, TIERS_WITH_SENTINEL, 9, 10) != -15
    assert rules.budget_review_delta(-500, TIERS_WITH_SENTINEL, 9, 10) == -9 * 50


def test_penalty_scales_with_kz_per_step_and_step():
    assert rules.budget_review_delta(-25, TIERS_WITHOUT_SENTINEL, 5, 10) == -15
    assert rules.budget_review_delta(-25, TIERS_WITHOUT_SENTINEL, 9, 5) == -45


def test_unit_trap_kilo_euro_ledger_versus_euro_default():
    assert started_steps(10, 10) == 1
    assert started_steps(11, 10) == 2
    assert started_steps(10_000) == 1
    assert started_steps(10_001) == 2


def test_penalty_params_from_config():
    cfg = harness.load_config()
    assert rules.penalty_params(cfg.final_events) == (9, 10)


def test_penalty_params_requires_a_budget_review_event():
    cfg = harness.load_config()
    with pytest.raises(ValueError):
        rules.penalty_params([])
    with pytest.raises(ValueError):
        rules.penalty_params(cfg.events[1])


def test_apply_final_events_over_budget_applies_the_penalty_once():
    cfg = harness.load_config()
    x, _ = rules.penalty_params(cfg.final_events)
    assert rules.apply_final_events(cfg.final_events, {}, -1, 50)[0] == 50 - x
    assert rules.apply_final_events(cfg.final_events, {}, -10, 50)[0] == 50 - x
    assert rules.apply_final_events(cfg.final_events, {}, -11, 50)[0] == 50 - 2 * x


def test_apply_final_events_clamps_after_the_penalty():
    cfg = harness.load_config()
    assert rules.apply_final_events(cfg.final_events, {}, -1, 5)[0] == 0
    assert rules.apply_final_events(cfg.final_events, {}, -890, 100)[0] == 0
    assert rules.apply_final_events(cfg.final_events, {}, 25, 50)[0] == 55
    assert rules.apply_final_events(cfg.final_events, {}, 75, 98)[0] == 100


def test_final_event_description_keeps_its_format():
    cfg = harness.load_config()
    _, records = rules.apply_final_events(cfg.final_events, {}, -12, 50)
    assert records[0]["effect_description"] == "Restbudget -12k€"


def test_evaluate_plan_all_l3_low_is_over_budget_and_floored():
    cfg = harness.load_config()
    x, step = rules.penalty_params(cfg.final_events)
    rec = rules.evaluate_plan(cfg, "low", {m: 3 for m in cfg.measure_ids})
    remaining = rec["costs"]["budget_available"] - rec["costs"]["total"]
    assert remaining == -890
    assert rec["over_budget"] is True
    assert rec["final_events"][0]["kz_delta"] == -x * 89
    assert rec["kz_final"] == 0


def test_penalty_rows_shape():
    rows = penalty_rows(9, 10)
    assert len(rows) == 12
    assert rows[0] == (1, 10_000, -9)
    assert rows[1] == (10_001, 20_000, -18)
    assert rows[11] == (110_001, 120_000, -108)
    assert len(penalty_rows(5, 10)) == 20


@pytest.mark.parametrize(("x", "step"), [(9, 10), (5, 10), (7, 10), (3, 5)])
def test_penalty_rows_agree_with_the_simulation_row_by_row(x, step):
    rows = penalty_rows(x, step)
    for index, (first_eur, last_eur, kz) in enumerate(rows, start=1):
        assert first_eur == (index - 1) * step * 1000 + 1
        assert last_eur == index * step * 1000
        for deficit_k in range((index - 1) * step + 1, index * step + 1):
            assert rules.budget_review_delta(-deficit_k, TIERS_WITHOUT_SENTINEL, x, step) == kz


def test_penalty_rows_end_when_the_penalty_alone_reaches_the_scale():
    rows = penalty_rows(9, 10)
    assert rows[-1][2] <= -100
    assert rows[-2][2] > -100


@pytest.mark.parametrize(
    ("amount", "text"),
    [(0, "0"), (999, "999"), (24_999, "24.999"), (120_000, "120.000"), (1_000_000, "1.000.000")],
)
def test_format_eur_uses_dot_thousands(amount, text):
    assert format_eur(amount) == text


def test_format_eur_negative_uses_the_true_minus_sign():
    assert format_eur(-1_500) == f"{MINUS}1.500"


def _compact_view(cfg, tier, selection):
    rec = rules.evaluate_plan(cfg, tier, selection)
    return rec["waves"][-1]["kz_after"], rec["costs"]["budget_available"] - rec["costs"]["total"]


@pytest.mark.parametrize("tier", TIERS)
def test_kernel_carries_kz_pre_review_and_remaining_on_mini_config(tier):
    cfg = harness.load_config(MINI)
    kernel = rules.TierKernel(cfg, tier)
    checked = 0
    for code in harness.iter_codes(cfg):
        selection = harness.selection_of(cfg, code)
        outcome = kernel.evaluate(selection)
        if outcome is None:
            continue
        kz_pre_review, remaining = _compact_view(cfg, tier, selection)
        assert outcome.kz_pre_review == outcome.kz_after[-1] == kz_pre_review, code
        assert outcome.remaining == remaining, code
        checked += 1
    assert checked > 0


@pytest.mark.parametrize("tier", TIERS)
def test_kernel_carries_kz_pre_review_and_remaining_on_golden_cases(tier):
    cfg = harness.load_config()
    kernel = rules.TierKernel(cfg, tier)
    x, step = rules.penalty_params(cfg.final_events)
    path = REPO_ROOT / "tests" / "golden" / f"characterization_{tier}.json"
    checked = 0
    for case in json.loads(path.read_text(encoding="utf-8"))["cases"]:
        if not case["valid"]:
            continue
        selection = harness.selection_of(cfg, case["code"])
        outcome = kernel.evaluate(selection)
        kz_pre_review, remaining = _compact_view(cfg, tier, selection)
        assert (outcome.kz_pre_review, outcome.remaining) == (kz_pre_review, remaining), case["code"]
        assert outcome.kz_final == rules.clamp_kz(
            kz_pre_review + rules.budget_review_delta(remaining, cfg.final_events[0].params["tiers"], x, step)
        )
        checked += 1
    assert checked > 0


def test_real_and_mini_config_declare_the_penalty():
    for path in (CONFIG_PATH, MINI):
        assert _penalty(_raw(path)) == {"kz_per_step": 9, "step": 10}


def test_missing_overspend_penalty_is_an_error():
    raw = _raw()
    del raw["final_events"][0]["overspend_penalty"]
    errors = _errors(validate(raw))
    assert [issue.code for issue in errors] == ["schema.event_params"]
    assert "overspend_penalty" in errors[0].message


@pytest.mark.parametrize("value", [0, -3])
def test_non_positive_kz_per_step_is_a_range_error(value):
    raw = _raw()
    _penalty(raw)["kz_per_step"] = value
    errors = _errors(validate(raw))
    assert [issue.code for issue in errors] == ["schema.range"]
    assert errors[0].path == "final_events[0].overspend_penalty.kz_per_step"


@pytest.mark.parametrize("value", ["10", 2.5, True, None])
def test_non_integer_step_is_a_type_error(value):
    raw = _raw()
    _penalty(raw)["step"] = value
    errors = _errors(validate(raw))
    assert [issue.code for issue in errors] == ["schema.type"]
    assert errors[0].path == "final_events[0].overspend_penalty.step"


def test_non_positive_step_is_a_range_error():
    raw = _raw()
    _penalty(raw)["step"] = 0
    errors = _errors(validate(raw))
    assert [issue.code for issue in errors] == ["schema.range"]
    assert errors[0].path == "final_events[0].overspend_penalty.step"


@pytest.mark.parametrize("value", [5, "9", [9, 10], None])
def test_overspend_penalty_must_be_an_object(value):
    raw = _raw()
    raw["final_events"][0]["overspend_penalty"] = value
    errors = _errors(validate(raw))
    assert [issue.code for issue in errors] == ["schema.type"]
    assert errors[0].path == "final_events[0].overspend_penalty"


@pytest.mark.parametrize("key", ["kz_per_step", "step"])
def test_overspend_penalty_keys_are_required(key):
    raw = _raw()
    del _penalty(raw)[key]
    errors = _errors(validate(raw))
    assert [issue.code for issue in errors] == ["schema.keys"]
    assert errors[0].path == f"final_events[0].overspend_penalty.{key}"


def test_step_other_than_ten_thousand_euro_is_only_a_warning():
    raw = _raw()
    _penalty(raw)["step"] = 5
    issues = validate(raw)
    assert _errors(issues) == []
    codes = {issue.code for issue in _warnings(issues)}
    assert "hand_calc.penalty_step" in codes
    message = next(i.message for i in _warnings(issues) if i.code == "hand_calc.penalty_step")
    assert "10.000" in message


@pytest.mark.parametrize("path", [CONFIG_PATH, MINI], ids=["real", "mini"])
def test_shipped_configs_have_no_errors_and_no_penalty_warning(path):
    issues = validate(_raw(path))
    assert _errors(issues) == []
    assert "hand_calc.penalty_step" not in {issue.code for issue in issues}


def test_real_config_still_has_exactly_one_warning():
    warnings = _warnings(validate(_raw()))
    assert [warning.code for warning in warnings] == ["hand_calc.kz_slope"]


def test_large_penalty_is_not_a_validator_warning():
    raw = _raw()
    _penalty(raw)["kz_per_step"] = 40
    issues = validate(raw)
    assert _errors(issues) == []
    assert {issue.code for issue in _warnings(issues)} == {"hand_calc.kz_slope"}

