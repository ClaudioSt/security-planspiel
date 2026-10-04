"""Every game formula is defined exactly once, in planspiel/rules.py (FOUND-03).

D-29 exception: `generate_attack_calculator.py` re-encodes the wave formulas as Excel formulas and
stays untouched until Phase 7 / LEG-01, so the three `generate_*.py` scripts are excluded from every scan.
"""
import ast
from collections import defaultdict

import pytest

from tests.support import REPO_ROOT

RULES = "planspiel/rules.py"
CONFIG = "planspiel/config.py"
ROUNDING = "planspiel/rounding.py"
REVIEW_TEXT = "planspiel/review_text.py"

FORMULA_FUNCTIONS = {
    name: RULES
    for name in (
        "dependencies_satisfied",
        "compute_cia",
        "compute_costs",
        "compute_recovery",
        "e_value_scaled",
        "reduction_above_threshold_scaled",
        "severity_scaled",
        "damage_euros",
        "attack_kz_delta",
        "wave_kz_change",
        "clamp_kz",
        "compute_bonus_reduction",
        "apply_attack",
        "kz_slope",
        "count_measures_at_level",
        "_tier_lookup",
        "evaluate_event",
        "apply_events",
        "simulate_selection",
        "evaluate_plan",
        "over_budget",
        "base_losses",
        "ros",
        "final_index",
        "budget_ledger",
        "security_spend",
        "apply_final_events",
        "budget_review_delta",
        "penalty_params",
        "swap_possible",
        "swap_legal",
        "swap_credit",
        "swap_repair",
        "kurswechsel_wave",
        "simulate_waves",
        "window_cost",
        "evaluate_path",
    )
}
FORMULA_FUNCTIONS.update(
    {name: ROUNDING for name in ("round_half_away", "round_half_away_frac", "started_steps")}
)
FORMULA_FUNCTIONS.update({name: REVIEW_TEXT for name in ("format_eur", "penalty_rows", "boundary_text")})

RETIRED_FUNCTIONS = {
    "e_target_check",
    "calculate_ros",
    "calculate_combined_score",
    "compute_final_index",
    "load_base_losses",
}

WRAPPERS = (
    "simulate_outcomes.py",
    "analyze_simulation_results.py",
    "balance_analysis.py",
)

OPERAND_ATTRIBUTES = {
    "s_unit",
    "base_severity",
    "mitigation_cap",
    "kz_at_full_damage",
    "kz_at_full_mitigation",
    "e_threshold",
    "recovery",
    "init",
    "opex",
    "weights",
    "bonus",
    "kz_per_step",
}

ROOT_SCRIPT_MODULES = {"simulate_outcomes", "analyze_simulation_results", "balance_analysis"}


def _rel(path):
    return path.relative_to(REPO_ROOT).as_posix()


def _scanned_files():
    files = sorted((REPO_ROOT / "planspiel").rglob("*.py"))
    files += sorted((REPO_ROOT / "tests").rglob("*.py"))
    files += [REPO_ROOT / wrapper for wrapper in WRAPPERS]
    return files


def _parse(path):
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _definitions():
    found = defaultdict(list)
    for path in _scanned_files():
        for node in ast.walk(_parse(path)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found[node.name].append(f"{_rel(path)}:{node.lineno}")
    return found


@pytest.mark.parametrize("name", sorted(FORMULA_FUNCTIONS))
def test_formula_defined_once_in_rules(name):
    sites = _definitions().get(name, [])
    assert len(sites) == 1, f"{name} defined at {sites}"
    assert sites[0].startswith(f"{FORMULA_FUNCTIONS[name]}:"), sites


@pytest.mark.parametrize("name", sorted(RETIRED_FUNCTIONS))
def test_retired_function_is_gone(name):
    assert _definitions().get(name, []) == []


def test_no_formula_operands_outside_rules_and_config():
    checked = sorted((REPO_ROOT / "planspiel").rglob("*.py")) + [REPO_ROOT / w for w in WRAPPERS]
    offenders = []
    for path in checked:
        if _rel(path) in (RULES, CONFIG):
            continue
        for node in ast.walk(_parse(path)):
            if isinstance(node, ast.Attribute) and node.attr in OPERAND_ATTRIBUTES:
                offenders.append(f"{_rel(path)}:{node.lineno} .{node.attr}")
    assert offenders == []


def test_nothing_imports_the_root_scripts():
    offenders = []
    for path in sorted((REPO_ROOT / "planspiel").rglob("*.py")) + sorted((REPO_ROOT / "tests").rglob("*.py")):
        for node in ast.walk(_parse(path)):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            else:
                continue
            for module in modules:
                if module.split(".")[0] in ROOT_SCRIPT_MODULES:
                    offenders.append(f"{_rel(path)}:{node.lineno} {module}")
    assert offenders == []
