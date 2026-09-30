import ast
import json
import subprocess
import sys

import pytest

from tests.support import REPO_ROOT
from tests.support.harness import LEGACY_RECORD_KEYS

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
WRAPPERS = ("simulate_outcomes.py",)


def _run(args, cwd=REPO_ROOT):
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _is_docstring(node):
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )


def _is_main_guard(node):
    if not isinstance(node, ast.If):
        return False
    test = node.test
    return (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and test.left.id == "__name__"
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value == "__main__"
    )


def _is_single_call_statement(body):
    if len(body) != 1:
        return False
    stmt = body[0]
    if isinstance(stmt, ast.Expr):
        return isinstance(stmt.value, ast.Call)
    if isinstance(stmt, ast.Raise):
        exc = stmt.exc
        return (
            isinstance(exc, ast.Call)
            and isinstance(exc.func, ast.Name)
            and exc.func.id == "SystemExit"
            and len(exc.args) == 1
            and isinstance(exc.args[0], ast.Call)
        )
    return False


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_wrapper_is_thin(wrapper):
    source = (REPO_ROOT / wrapper).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=wrapper)
    offenders = []
    guards = 0
    for index, node in enumerate(tree.body):
        if index == 0 and _is_docstring(node):
            continue
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("planspiel"):
            continue
        if _is_main_guard(node) and _is_single_call_statement(node.body):
            guards += 1
            continue
        offenders.append(f"{wrapper}:{node.lineno} {type(node).__name__}")
    assert offenders == []
    assert guards == 1


def test_legacy_output_on_mini_config(tmp_path):
    out = tmp_path / "out.json"
    result = _run(
        ["simulate_outcomes.py", "--config", str(MINI), "--budget-tier", "low", "--output", str(out)]
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")

    data = json.loads(out.read_text(encoding="utf-8"))
    assert list(data["summary"]) == [
        "total_outcomes",
        "budget_tier",
        "budget",
        "kz_start",
        "budget_filter",
        "measures",
    ]
    results = data["results"]
    assert data["summary"]["total_outcomes"] == len(results) > 0
    for record in results:
        assert list(record) == list(LEGACY_RECORD_KEYS)
        assert record["costs"]["total"] <= record["costs"]["budget_available"]
    keys = [(-r["kz_final"], r["total_damage"]) for r in results]
    assert keys == sorted(keys)
