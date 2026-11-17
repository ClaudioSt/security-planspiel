"""D-17: the build reads nothing from archive/ and the git tree matches the archive layout (LEG-01)."""
import subprocess
import unicodedata

import pytest

from tests.support import REPO_ROOT

SCANNED_DIRS = ("planspiel", "print")
SCANNED_FILES = (
    "pyproject.toml",
    ".gitattributes",
    "simulate_outcomes.py",
    "analyze_simulation_results.py",
    "balance_analysis.py",
)
SCANNED_GLOBS = ("content/*.toml", "content/*.json")
RETIRED_TOKENS = (
    "archive/",
    "pptx_output",
    "generate_pptx_cards",
    "generate_from_template",
    "generate_attack_calculator",
    "angriff_berechnung",
    "final_documents/Angriff",
    "final_documents/Zeitungsartikel",
)
BINARY_SUFFIXES = {".png", ".jpg", ".pdf", ".ttf", ".otf"}

KEPT_FILES = {unicodedata.normalize("NFC", name) for name in (
    "final_documents/13052026_VWI meets MHP_Offenes Treffen.pptx",
    "final_documents/DanielGhebreselassie 1.jpg",
    "final_documents/MHP Company Profile DE - Jubilee Logo.pptx",
    "final_documents/Planspiel_Einführung + Grundlagen.pptx",
    "final_documents/Stanullo Claudio_2022_04.jpg",
)}


def _scanned_paths():
    paths = []
    for directory in SCANNED_DIRS:
        paths += [p for p in (REPO_ROOT / directory).rglob("*")
                  if p.is_file() and "__pycache__" not in p.parts]
    paths += [REPO_ROOT / name for name in SCANNED_FILES]
    for pattern in SCANNED_GLOBS:
        paths += sorted(REPO_ROOT.glob(pattern))
    return [p for p in paths if p.suffix.lower() not in BINARY_SUFFIXES]


def _tracked():
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "-c", "core.quotepath=off", "ls-files"],
        capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL, timeout=30, check=True,
    ).stdout
    return [unicodedata.normalize("NFC", line) for line in out.splitlines()]


def test_no_build_input_references_archive_or_a_retired_generator():
    hits = []
    for path in _scanned_paths():
        text = path.read_text(encoding="utf-8", errors="replace")
        hits += [f"{path.relative_to(REPO_ROOT).as_posix()}: {token}"
                 for token in RETIRED_TOKENS if token in text]
    assert hits == []


def test_retired_generators_and_outputs_are_not_tracked_at_the_old_places():
    tracked = _tracked()
    assert [f for f in tracked if f.startswith("pptx_output/")] == []
    assert [f for f in tracked if "/" not in f and f.endswith(".xlsx")] == []
    assert [f for f in tracked if "/" not in f and f.startswith("generate_") and f.endswith(".py")] == []
    assert [f for f in tracked if f.startswith("docs/")] == []


def test_retired_generators_and_outputs_are_tracked_in_the_archive():
    tracked = set(_tracked())
    base = "archive/legacy_generators/"
    for name in ("generate_attack_calculator.py", "generate_from_template.py",
                 "generate_pptx_cards.py", "angriff_berechnung.xlsx"):
        assert base + name in tracked, name
    assert len([f for f in tracked if f.startswith(base + "pptx_output/")]) == 6
    assert "archive/historical_docs/folienkonzept_spielphasen_mechtech.md" in tracked


def test_final_documents_hold_only_the_kept_files_and_generated():
    manual = {f for f in _tracked()
              if f.startswith("final_documents/") and not f.startswith("final_documents/generated/")}
    assert manual == KEPT_FILES
