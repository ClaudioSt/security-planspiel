import copy
import json

import pytest

from planspiel.rounding import started_steps
from planspiel.rules import penalty_params
from tests.support import CONFIG_PATH, REPO_ROOT, harness
from tests.support.golden import check_golden, normalize
from tests.support.golden_cases import SEED, build_case_list

TIERS = ("low", "medium", "high")
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"


def golden_path(tier):
    return GOLDEN_DIR / f"characterization_{tier}.json"


def read_golden(tier):
    path = golden_path(tier)
    if not path.exists():
        pytest.fail(f"{path.name} is missing; create it with `uv run pytest --update-golden`", pytrace=False)
    return json.loads(path.read_text(encoding="utf-8"))


def expected_of(record):
    return normalize({k: v for k, v in record.items() if k != "valid"})


def test_tiers_match_config():
    assert set(TIERS) == set(harness.load_config().budget_tiers)


@pytest.mark.parametrize("tier", TIERS)
def test_golden_sample_matches(tier, update_golden, golden_report):
    cfg = harness.load_config()
    path = golden_path(tier)
    if path.exists():
        cases = [{"code": c["code"], "tags": c["tags"]} for c in json.loads(path.read_text(encoding="utf-8"))["cases"]]
    elif update_golden:
        cases = build_case_list(cfg, tier)
    else:
        cases = []

    documented = []
    for case in cases:
        record = harness.evaluate(cfg, tier, harness.selection_of(cfg, case["code"]))
        entry = {"code": case["code"], "tags": case["tags"], "valid": record["valid"]}
        if record["valid"]:
            entry["expected"] = expected_of(record)
        documented.append(entry)

    document = {
        "format": 1,
        "tier": tier,
        "stage": harness.STAGE,
        "meta": {"seed": SEED, "case_generator": "tests/support/golden_cases.py"},
        "cases": documented,
    }
    check_golden(path, document, update_golden, golden_report)


@pytest.mark.parametrize("tier", TIERS)
def test_golden_covers_required_categories(tier):
    cases = read_golden(tier)["cases"]
    tags = {tag for case in cases for tag in case["tags"]}

    x, step = penalty_params(harness.load_config().final_events)

    def overspend_penalty(case):
        costs = case["expected"]["costs"]
        return -x * started_steps(costs["total"] - costs["budget_available"], step)

    over_budget_strategies = [
        c for c in cases
        if any(t.startswith("strategy:") for t in c["tags"])
        and c["expected"]["over_budget"]
        and c["expected"]["final_events"][0]["kz_delta"] == overspend_penalty(c) < 0
    ]
    assert over_budget_strategies, "no over-budget strategy pinned with the linear overspend penalty (D-09, D-15)"

    empty = next(c for c in cases if "edge:empty" in c["tags"])
    assert empty["expected"]["ros"] is None

    assert any(t.startswith("census:tie_w3:") for t in tags), "wave-3 .5 tie missing (D-23)"
    for remaining in (-1, 0, 25, 50, 75):
        assert f"census:remaining_{remaining}" in tags

    invalid_dependency = [c for c in cases if any(t.startswith("dep:") and t.endswith(":invalid") for t in c["tags"])]
    assert invalid_dependency
    assert all(c["valid"] is False for c in invalid_dependency)

    assert len({t for t in tags if t.startswith("strategy:")}) == 27


def mutate_wave1_threshold(raw):
    raw["waves"][0]["e_threshold"] += 1


def mutate_budget_review_boundary(raw):
    assert raw["final_events"][0]["tiers"][1][0] == 25
    raw["final_events"][0]["tiers"][1][0] += 1


@pytest.mark.parametrize(
    "mutation, required_tag",
    [
        (mutate_wave1_threshold, None),
        (mutate_budget_review_boundary, "census:remaining_25"),
    ],
    ids=["wave1_e_threshold", "budget_review_boundary_25"],
)
def test_golden_detects_config_mutation(tmp_path, mutation, required_tag):
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(raw)
    mutation(mutated)
    mutated_path = tmp_path / "simulation_config.json"
    mutated_path.write_text(json.dumps(mutated, ensure_ascii=False), encoding="utf-8")
    cfg = harness.load_config(mutated_path)

    differing = {}
    for case in read_golden("medium")["cases"]:
        if not case["valid"]:
            continue
        record = harness.evaluate(cfg, "medium", harness.selection_of(cfg, case["code"]))
        if expected_of(record) != case["expected"]:
            differing[case["code"]] = case["tags"]

    assert differing, "mutation was not detected by any golden case"
    if required_tag is not None:
        assert any(required_tag in tags for tags in differing.values())
