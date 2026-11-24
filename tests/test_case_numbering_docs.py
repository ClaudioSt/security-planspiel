"""The rulebook and the repo guide number the three resolution cases like the worksheet and `rules.path_trace`.

Worksheet (`sheets.welle.case_1..3` in `content/texte.toml`) and code agree: Fall 1 at or below the threshold,
Fall 2 cap reached (no damage), Fall 3 in between (linear). README and CLAUDE.md must say the same, otherwise readers
(and tooling built on the docs, such as the web app) mix up Fall 2 and Fall 3.
"""
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_worksheet_numbering_is_the_reference():
    texts = tomllib.loads((ROOT / "content" / "texte.toml").read_text(encoding="utf-8"))
    welle = texts["sheets"]["welle"]
    assert "Obergrenze" in welle["case_2"] and "kein Schaden" in welle["case_2"]
    assert "dazwischen" in welle["case_3"]


def test_readme_numbers_cases_like_the_worksheet():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert re.search(r"Fall 2 \(Deckel erreicht", readme), "README: Fall 2 muss 'Deckel erreicht' sein"
    assert re.search(r"Fall 3 \(zwischen Schwelle und Deckel", readme), "README: Fall 3 muss 'zwischen' sein"


def test_claude_md_numbers_cases_like_the_worksheet():
    guide = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "case 2 cap reached" in guide
    assert "case 3 between threshold and cap" in guide
