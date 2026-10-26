"""Built Welle 0 document: worksheet pages in the real two-page shape plus the selection page (FLOW-01, D-14).

Run with `uv run pytest -m pdf tests/test_welle0_pdf.py -v`.
"""
import re

import pytest

from planspiel import practice, veil
from planspiel.config import load_config
from planspiel.texts import load_content
from tests.support import CONFIG_PATH, CONTENT_DIR
from tests.support.pdf_text import FILL, pdf_text, squash, squashed_pages

pytestmark = pytest.mark.pdf

JOB = practice.PRACTICE_JOB
PT_PER_MM = 72.27 / 25.4
STAMP = re.compile(r"Stand\d{4}-\d{2}-\d{2}·[0-9a-f]{7}(?:\+lokal)?")


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def content():
    return load_content(CONTENT_DIR)


@pytest.fixture(scope="module")
def doc(cfg, content):
    return practice.build_practice_document(cfg, content.texts)


def _pages(printed_set):
    return squashed_pages(printed_set.out_a / f"{JOB}.pdf")


def test_the_practice_pdf_is_built(printed_set):
    assert JOB in printed_set.jobs


def test_three_pages_worksheet_then_selection(printed_set, doc):
    first, second, third = _pages(printed_set)
    for key in ("cia", "e_value", "bonus", "reduction"):
        assert squash(doc.sheet.step_headings[key]) in first, key
        assert squash(doc.sheet.step_headings[key]) not in second, key
    for key in ("cases", "recovery", "wave_kz"):
        assert squash(doc.sheet.step_headings[key]) in second, key
        assert squash(doc.sheet.step_headings[key]) not in first, key
    assert squash(doc.title) in first
    for text in (doc.selection_title, doc.event.heading, doc.event.result, doc.tracking.title):
        assert squash(text) in third, text
        assert squash(text) not in second, text


def test_exactly_three_pages(printed_set):
    assert len(_pages(printed_set)) == 3


def test_every_model_fragment_is_in_the_pdf_text(printed_set, doc):
    text = "".join(_pages(printed_set))
    for fragment in doc.printed_fragments():
        assert squash(fragment) in text, f"{fragment!r} fehlt im PDF"


def test_every_filled_value_is_on_its_page(printed_set, doc):
    first, second, third = _pages(printed_set)
    sheet = doc.sheet
    for row in sheet.cia_filled:
        for cell in row:
            assert squash(cell) in first, row
    for value in sheet.cia_sum:
        assert squash(value) in first
    for part in (*sheet.wave_kz_line, *sheet.result_line, *sheet.recovery_line):
        if not isinstance(part, str):
            assert squash(part.value) in second, part
    for row in doc.tracking.rows:
        for cell in row:
            assert squash(cell) in third, row


def test_build_log_shows_no_missing_glyph_and_no_overfull_line(printed_set):
    log = (printed_set.build_a / f"{JOB}.log").read_text(encoding="utf-8", errors="replace")
    assert "Missing character" not in log
    assert "Overfull \\hbox" not in log
    assert "Overfull \\vbox" not in log


def test_every_page_fits_the_text_height_as_measured_in_the_log(printed_set):
    log = (printed_set.build_a / f"{JOB}.log").read_text(encoding="utf-8", errors="replace")
    reports = FILL.findall(log)
    assert [number for number, _, _ in reports] == ["1", "2", "3"], reports
    for number, used, text in reports:
        assert float(used) <= float(text), (
            f"Seite {number}: {float(used) / PT_PER_MM:.1f} mm belegt, {float(text) / PT_PER_MM:.1f} mm Satzspiel"
        )


def test_the_stamp_is_on_every_page(printed_set):
    for number, page in enumerate(_pages(printed_set), start=1):
        assert STAMP.search(page), f"Seite {number} ohne Stempel"


def test_the_practice_pdf_passes_the_layer_two_veil_scan(printed_set, cfg, content):
    ctx = veil.context(cfg, content.texts, content.terms)
    text = pdf_text(printed_set.out_a / f"{JOB}.pdf")
    assert veil.scan_text(text, JOB, ctx, layer="pdf") == []
