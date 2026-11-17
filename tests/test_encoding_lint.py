"""Every text-mode file read/write must declare encoding= (machine code page is cp1252)."""
import ast

from tests.support import REPO_ROOT

LINT_TARGETS = (
    sorted((REPO_ROOT / "planspiel").rglob("*.py"))
    + [
        REPO_ROOT / "simulate_outcomes.py",
        REPO_ROOT / "analyze_simulation_results.py",
        REPO_ROOT / "balance_analysis.py",
    ]
    + sorted((REPO_ROOT / "tests").rglob("*.py"))
)


def _is_binary_open(call: ast.Call) -> bool:
    mode = None
    if len(call.args) > 1:
        mode = call.args[1]
    for keyword in call.keywords:
        if keyword.arg == "mode":
            mode = keyword.value
    return (
        isinstance(mode, ast.Constant)
        and isinstance(mode.value, str)
        and "b" in mode.value
    )


def _needs_encoding(call: ast.Call) -> bool:
    func = call.func
    if isinstance(func, ast.Name) and func.id == "open":
        return not _is_binary_open(call)
    return isinstance(func, ast.Attribute) and func.attr in {"read_text", "write_text"}


def test_text_io_declares_encoding():
    violations = []
    for path in LINT_TARGETS:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not _needs_encoding(node):
                continue
            if not any(keyword.arg == "encoding" for keyword in node.keywords):
                violations.append(f"{path.relative_to(REPO_ROOT).as_posix()}:{node.lineno}")
    assert violations == []
