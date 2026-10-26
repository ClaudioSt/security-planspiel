"""Model-level veil guard: pre-wave builder modules never touch revealed data (VEIL-02, T-05-04).

A cheap AST check in the default suite. `practice.py` and `master.py` are exempt by design (practice shows its
own attack, the master sheet is for facilitators); the scan layers cover their output instead.
"""
import ast
from pathlib import Path

import pytest

from tests.support import REPO_ROOT

# Later plans append their pre-wave builder modules (file names under planspiel/): cards.py (05-02),
# eventtext.py (05-05), booklet.py (05-06), wave_page.py (05-08) and story.py (05-10).
PREWAVE_MODULES: tuple[str, ...] = ("cards.py", "eventtext.py", "booklet.py")

FORBIDDEN_NAMES = frozenset(
    {
        "RevealView",
        "FacilitatorView",
        "worksheet_constants",
        "bonus_measures",
        "bonus_rows",
        "bonus_reasons",
        "build_attack_sheet",
        "build_attack_sheets",
        "worksheet_job",
    }
)
REVEALED_NAMESPACE = ".revealed"


def forbidden_references(source: str) -> list[str]:
    """Findings (`line: what`) of forbidden names, import aliases and revealed-namespace strings in a module."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            found.append(f"{node.lineno}: name {node.id}")
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_NAMES:
            found.append(f"{node.lineno}: attribute {node.attr}")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                for name in (alias.name.split(".")[-1], alias.asname):
                    if name in FORBIDDEN_NAMES:
                        found.append(f"{node.lineno}: import {name}")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if REVEALED_NAMESPACE in node.value:
                found.append(f"{node.lineno}: string names the revealed namespace")
            elif node.value in FORBIDDEN_NAMES:
                found.append(f"{node.lineno}: string {node.value}")
    return found


@pytest.mark.parametrize("module", PREWAVE_MODULES)
def test_prewave_modules_do_not_reference_revealed_data(module):
    path: Path = REPO_ROOT / "planspiel" / module
    assert path.is_file(), f"planspiel/{module} fehlt"
    assert forbidden_references(path.read_text(encoding="utf-8")) == []


def test_the_guard_reports_the_reveal_view_and_bonus_reasons():
    source = (
        "from planspiel.texts import RevealView as View\n"
        "def build(texts):\n"
        "    reasons = texts.get('attacks.ot.revealed.bonus_reasons.M5')\n"
        "    return RevealView, reasons\n"
    )
    findings = forbidden_references(source)
    assert any("import RevealView" in finding for finding in findings)
    assert any("name RevealView" in finding for finding in findings)
    assert any("revealed namespace" in finding for finding in findings)


@pytest.mark.parametrize(
    "source",
    [
        "x = rules.worksheet_constants(cfg, wave)",
        "rows = constants.bonus_rows",
        "import planspiel.printmodel as pm\nfrom planspiel.printmodel import build_attack_sheets",
        "view = getattr(texts, 'FacilitatorView')",
    ],
)
def test_the_guard_reports_each_forbidden_form(source):
    assert forbidden_references(source)


def test_the_guard_passes_a_clean_module():
    source = "from planspiel.texts import PreAttackView\nview = PreAttackView(cfg, texts)\nview.sheet('budget')\n"
    assert forbidden_references(source) == []
