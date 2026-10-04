"""Overspend trim-back gate (RULE-04, D-17, D-24): closure, required X and gate result against brute force."""
import random
from array import array

import pytest

from planspiel import gate, rules
from planspiel.cli import main
from planspiel.enumerate import code_from_index, enumerate_tier
from planspiel.report import REFERENCE_LABEL
from planspiel.rounding import started_steps
from tests.support import REPO_ROOT, harness

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


def _digits(index, n):
    return [(index // 4 ** (n - 1 - j)) % 4 for j in range(n)]


def _below(lower, upper, n):
    return all(a <= b for a, b in zip(_digits(lower, n), _digits(upper, n)))


@pytest.mark.parametrize("n", [3, 4])
@pytest.mark.parametrize("seed", range(5))
def test_lowering_closure_equals_brute_force(n, seed):
    rng = random.Random(seed)
    size = 4 ** n
    initial = [rng.choice([-1, -1, rng.randrange(0, 2 ** 20)]) for _ in range(size)]
    best = array("i", initial)
    gate.lowering_closure(best, n)
    for i in range(size):
        expected = max(initial[j] for j in range(size) if _below(j, i, n))
        assert best[i] == expected, (i, expected, best[i])


@pytest.mark.parametrize(
    "pre, trimmed, steps, strict, expected",
    [
        (91, 83, 1, True, 9),
        (91, 83, 1, False, 8),
        (89, 85, 2, True, 3),
        (89, 85, 2, False, 2),
        (85, 81, 1, True, 5),
        (85, 81, 1, False, 4),
        (80, 85, 1, True, 1),
        (80, 85, 1, False, 1),
    ],
)
def test_required_penalty_x(pre, trimmed, steps, strict, expected):
    assert gate.required_penalty_x(pre, trimmed, steps, strict=strict) == expected


def _synthetic(rows, config_x=9, step=10):
    """rows: (code_index, kz_final, kz_pre_review, remaining, over_budget) on the n = 2 lattice."""
    columns = list(zip(*rows))
    return gate.gate_from_columns(
        2,
        array("I", columns[0]),
        array("B", columns[1]),
        array("B", columns[2]),
        array("h", columns[3]),
        array("B", columns[4]),
        config_x,
        step,
        tier_name="synthetic",
    )


def test_synthetic_gate_names_the_offending_plan_when_x_is_too_low():
    result = _synthetic([(4, 80, 80, 20, 0), (5, 81, 90, -5, 1)])
    assert result.min_x_strict == 11
    assert result.min_x_weak == 10
    assert result.over_budget == 1
    assert result.unlosable == 0 and result.untrimmable == 0
    assert result.violations_at_config_x == 1
    assert result.passed is False
    assert result.config_x == 9 and result.step == 10
    assert result.x_histogram == {11: 1}
    witness = result.witness
    assert witness["code"] == "11"
    assert witness["trimmed_code"] == "10"
    assert witness["remaining"] == -5
    assert witness["steps"] == 1
    assert witness["kz_pre_review"] == 90
    assert witness["kz_final"] == 81
    assert witness["required_x"] == 11
    assert witness["trimmed_kz_final"] == 80
    assert witness["trimmed_remaining"] == 20
    report = gate.format_gate_report(result)
    assert "11" in report and "10" in report
    assert REFERENCE_LABEL in report
    assert "NICHT bestanden" in report


def test_synthetic_gate_passes_when_x_is_large_enough():
    result = _synthetic([(4, 80, 80, 20, 0), (5, 79, 90, -5, 1)], config_x=11)
    assert result.min_x_strict == 11
    assert result.violations_at_config_x == 0
    assert result.passed is True
    assert "bestanden" in gate.format_gate_report(result)
    assert "NICHT bestanden" not in gate.format_gate_report(result)


def test_synthetic_untrimmable_plan_fails_the_gate():
    result = _synthetic([(5, 0, 90, -5, 1)])
    assert result.untrimmable == 1
    assert result.passed is False
    assert result.witness is None
    assert result.min_x_strict == 1 and result.min_x_weak == 1


def test_synthetic_unlosable_plan_fails_the_gate():
    result = _synthetic([(4, 0, 0, 20, 0), (5, 0, 90, -5, 1)])
    assert result.unlosable == 1
    assert result.untrimmable == 0
    assert result.passed is False


def test_synthetic_trimmed_tie_names_the_lowest_code():
    result = _synthetic([(1, 70, 70, 20, 0), (4, 70, 70, 20, 0), (5, 85, 90, -5, 1)])
    assert result.witness["trimmed_code"] == "01"


def test_synthetic_without_over_budget_plans():
    result = _synthetic([(4, 80, 80, 20, 0)])
    assert result.over_budget == 0
    assert result.min_x_strict == 1 and result.min_x_weak == 1
    assert result.witness is None
    assert result.passed is True


def _mini_brute(cfg, tier):
    config_x, step = rules.penalty_params(cfg.final_events)
    n = len(cfg.measures)
    valid = {}
    for code in harness.iter_codes(cfg):
        rec = harness.evaluate(cfg, tier, harness.selection_of(cfg, code))
        if rec["valid"]:
            valid[int(code, 4)] = harness.compact_from_plan(cfg, rec)
    in_budget = {index: out for index, out in valid.items() if not out.over_budget}
    trimmed_of = {}
    histogram = {}
    untrimmable = unlosable = violations = over = 0
    required = []
    for index in sorted(valid):
        outcome = valid[index]
        if not outcome.over_budget:
            continue
        over += 1
        candidates = [t for t in in_budget if _below(t, index, n)]
        if not candidates:
            untrimmable += 1
            continue
        best = min(candidates, key=lambda t: (-in_budget[t].kz_final, t))
        trimmed = in_budget[best].kz_final
        trimmed_of[index] = (trimmed, best)
        steps = started_steps(-outcome.remaining, step)
        if outcome.kz_final >= trimmed:
            violations += 1
        if trimmed == 0:
            unlosable += 1
            continue
        gap = outcome.kz_pre_review - trimmed
        strict = max(1, gap // steps + 1)
        weak = max(1, -(-gap // steps))
        histogram[strict] = histogram.get(strict, 0) + 1
        required.append((strict, weak, index))
    min_strict = max((r[0] for r in required), default=1)
    min_weak = max((r[1] for r in required), default=1)
    witness_index = min((r[2] for r in required if r[0] == min_strict), default=None)
    return {
        "valid": valid,
        "trimmed_of": trimmed_of,
        "over_budget": over,
        "untrimmable": untrimmable,
        "unlosable": unlosable,
        "violations": violations,
        "histogram": dict(sorted(histogram.items())),
        "min_strict": min_strict,
        "min_weak": min_weak,
        "witness_index": witness_index,
        "config_x": config_x,
        "step": step,
    }


@pytest.mark.parametrize("tier", TIERS)
def test_mini_gate_equals_brute_force(mini, tier):
    expected = _mini_brute(mini, tier)
    store = enumerate_tier(mini, tier)
    result = gate.gate_tier(mini, tier, store=store)
    assert expected["over_budget"] > 0
    assert result.tier == tier
    assert result.config_x == expected["config_x"] and result.step == expected["step"]
    assert result.over_budget == expected["over_budget"]
    assert result.untrimmable == expected["untrimmable"]
    assert result.unlosable == expected["unlosable"]
    assert result.violations_at_config_x == expected["violations"]
    assert result.x_histogram == expected["histogram"]
    assert result.min_x_strict == expected["min_strict"]
    assert result.min_x_weak == expected["min_weak"]
    if expected["witness_index"] is None:
        assert result.witness is None
    else:
        n = len(mini.measures)
        trimmed_final, trimmed_index = expected["trimmed_of"][expected["witness_index"]]
        assert result.witness["code"] == code_from_index(expected["witness_index"], n)
        assert result.witness["trimmed_code"] == code_from_index(trimmed_index, n)
        assert result.witness["trimmed_kz_final"] == trimmed_final
        assert result.witness["required_x"] == expected["min_strict"]
    expected_passed = (
        result.config_x >= expected["min_strict"]
        and expected["unlosable"] == 0
        and expected["untrimmable"] == 0
        and expected["violations"] == 0
    )
    assert result.passed is expected_passed


@pytest.mark.parametrize("tier", TIERS)
def test_mini_trimmed_final_equals_brute_force_for_every_over_budget_plan(mini, tier):
    expected = _mini_brute(mini, tier)
    store = enumerate_tier(mini, tier)
    n = len(mini.measures)
    keys = gate.trim_keys(
        n, store.column("code_index"), store.column("kz_final"), store.column("over_budget")
    )
    size = 4 ** n
    checked = 0
    for index, outcome in expected["valid"].items():
        if not outcome.over_budget or index not in expected["trimmed_of"]:
            continue
        trimmed_final, trimmed_index = expected["trimmed_of"][index]
        assert keys[index] // size == trimmed_final
        assert size - 1 - keys[index] % size == trimmed_index
        checked += 1
    assert checked + expected["untrimmable"] == expected["over_budget"]


@pytest.mark.parametrize("tier", TIERS)
def test_gate_result_json_is_stable(mini, tier):
    result = gate.gate_tier(mini, tier)
    data = gate.gate_result_json(result)
    assert list(data) == [
        "tier",
        "layer",
        "config_x",
        "step",
        "over_budget",
        "min_x_strict",
        "min_x_weak",
        "x_histogram",
        "witness",
        "unlosable",
        "untrimmable",
        "violations_at_config_x",
        "passed",
    ]
    assert list(data["x_histogram"]) == [str(x) for x in sorted(result.x_histogram)]
    assert gate.gate_result_json(result) == data
    assert "Referenzplan" in gate.format_gate_report(result)


def test_gate_command_matches_gate_tier_on_the_mini_config(mini, capsys):
    expected_passed = gate.gate_tier(mini, "low").passed
    code = main(["gate", "--config", str(MINI), "--tier", "low"])
    out = capsys.readouterr().out
    assert code == (0 if expected_passed else 1)
    assert REFERENCE_LABEL in out
    assert ("Überziehungs-Gate: bestanden" if expected_passed else "Überziehungs-Gate: NICHT bestanden") in out


def test_gate_command_rejects_an_unknown_tier():
    with pytest.raises(SystemExit) as raised:
        main(["gate", "--config", str(MINI), "--tier", "nope"])
    assert raised.value.code == 2
