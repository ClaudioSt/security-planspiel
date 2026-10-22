"""`planspiel print` end to end: the whole print set rebuilds byte-identically (PRINT-01, ROADMAP SC1).

Run with `uv run pytest -m pdf tests/test_print_cli_pdf.py -v`.
"""
import re

import pytest
from pypdf import PdfReader

pytestmark = pytest.mark.pdf


def _squashed(page) -> str:
    return re.sub(r"\s+", "", page.extract_text())


def test_both_runs_produce_the_same_files(printed_set):
    names_a = sorted(path.name for path in printed_set.out_a.glob("*.pdf"))
    names_b = sorted(path.name for path in printed_set.out_b.glob("*.pdf"))
    assert names_a == names_b
    assert "smoke.pdf" in names_a
    assert sorted(printed_set.jobs) == [name[:-4] for name in names_a]


def test_pdfs_are_byte_identical(printed_set):
    for job in printed_set.jobs:
        first = (printed_set.out_a / f"{job}.pdf").read_bytes()
        second = (printed_set.out_b / f"{job}.pdf").read_bytes()
        assert first == second, f"{job}.pdf unterscheidet sich zwischen zwei Läufen"


def test_smoke_pdf_has_page_numbers_and_escaped_specials(printed_set):
    reader = PdfReader(printed_set.out_a / "smoke.pdf")
    assert len(reader.pages) == 2
    first, second = (_squashed(page) for page in reader.pages)
    assert "Seite1von2" in first
    assert "Seite2von2" in second
    assert "Backup&DisasterRecovery" in first
    assert "_#$" in first


def test_smoke_pdf_prints_quotes_and_ligature_characters_verbatim(printed_set):
    # babel-ngerman's `"` shorthand and fontspec's TeX ligatures must not alter the source text.
    reader = PdfReader(printed_set.out_a / "smoke.pdf")
    first = _squashed(reader.pages[0])
    assert '"aktiv""Auch"a--b<<c>>,,d\'\'0,5' in first
