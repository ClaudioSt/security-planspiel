import importlib.metadata
import subprocess
import sys
from pathlib import Path

import pytest

import planspiel
from tests.support import REPO_ROOT


def _run(args):
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_interpreter_is_project_venv():
    assert sys.version_info[:2] == (3, 12)
    assert Path(sys.prefix).resolve() == (REPO_ROOT / ".venv").resolve()
    assert "inkscape" not in sys.base_prefix.lower()


def test_pinned_packages():
    assert importlib.metadata.version("pytest") == "9.1.1"
    assert importlib.metadata.version("openpyxl") == "3.1.5"
    assert importlib.metadata.version("python-pptx") == "1.0.2"


def test_planspiel_is_the_repo_package():
    assert Path(planspiel.__file__).resolve().parent == (REPO_ROOT / "planspiel").resolve()


def test_console_script_installed():
    if sys.platform == "win32":
        script = Path(sys.prefix) / "Scripts" / "planspiel.exe"
    else:
        script = Path(sys.prefix) / "bin" / "planspiel"
    assert script.exists()
    result = _run([str(script), "--help"])
    assert result.returncode == 0, result.stderr


def test_module_entry_point():
    result = _run([sys.executable, "-m", "planspiel", "--help"])
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "args",
    [
        ["simulate_outcomes.py", "--help"],
        ["analyze_simulation_results.py", "--help"],
        ["balance_analysis.py"],
    ],
    ids=["simulate_outcomes", "analyze_simulation_results", "balance_analysis"],
)
def test_documented_wrappers_run(args):
    result = _run([sys.executable, *args])
    assert result.returncode == 0, result.stderr
