"""Built "Was ist neu" sheet: exactly one A4 page for the real values and for the capped worst case (FLOW-04, D-15).

Run with `uv run pytest -m pdf tests/test_was_neu_pdf.py -v`.
"""
import dataclasses
import re

import pytest
from pypdf import PdfReader

from planspiel import audience, render, texbuild, veil
from planspiel.config import load_config
from planspiel.texts import load_content
from planspiel.was_neu import BASELINE_FILE, MAX_VALUE_ROWS, WAS_NEU_JOB, ValueRow, build_was_neu_sheet, load_baseline
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT
from tests.support.pdf_text import FILL, pdf_text, squash, squashed_pages, unwrapped_log
from tests.support.tex import PRINT_DIR, tex_skip_reason

pytestmark = pytest.mark.pdf

STAMP = re.compile(r"Stand\d{4}-\d{2}-\d{2}·[0-9a-f]{7}(?:\+lokal)?")
TEMPLATES = REPO_ROOT / "print" / "templates"
JOB = WAS_NEU_JOB


@pytest.fixture(scope="module")
def setup():
    cfg = load_config(CONFIG_PATH)
    content = load_content(CONTENT_DIR)
    baseline = load_baseline(CONTENT_DIR / BASELINE_FILE)
    return cfg, content, build_was_neu_sheet(cfg, content.texts, baseline)


@pytest.fixture(scope="module")
def pdf_path(printed_set):
    return printed_set.out_a / f"{JOB}.pdf"


@pytest.fixture(scope="module")
def page_text(pdf_path):
    pages = squashed_pages(pdf_path)
    assert len(pages) == 1
    return pages[0]


def _log(printed_set):
    return unwrapped_log(printed_set.build_a / f"{JOB}.log")


def test_the_sheet_is_exactly_one_a4_page(pdf_path):
    reader = PdfReader(pdf_path)
    assert len(reader.pages) == 1
    box = reader.pages[0].mediabox
    assert (round(float(box.width) / 72 * 25.4), round(float(box.height) / 72 * 25.4)) == (210, 297)


def test_the_real_sheet_has_every_value_row_and_every_rule_row(setup):
    _, _, sheet = setup
    assert len(sheet.rules) == 12
    assert 0 < len(sheet.values) <= MAX_VALUE_ROWS
    assert sheet.values_more == ""


def test_every_printed_fragment_is_on_the_page(page_text, setup):
    _, _, sheet = setup
    for fragment in sheet.printed_fragments():
        assert squash(fragment) in page_text, fragment


def test_the_page_fits_the_text_height_as_measured_in_the_log(printed_set):
    reports = FILL.findall(_log(printed_set))
    assert len(reports) == 1
    number, used, limit = reports[0]
    assert int(number) == 1
    assert float(used) <= float(limit), f"Seite: {used}pt > {limit}pt"


def test_stamp_and_page_counter_are_on_the_page(page_text):
    assert len(STAMP.findall(page_text)) == 1
    assert page_text.count("Seite1von1") == 1


def test_the_build_log_has_no_missing_glyph_overfull_line_or_undefined_control_sequence(printed_set):
    log = _log(printed_set)
    assert "Missing character" not in log
    assert "Overfull \\hbox" not in log
    assert "Overfull \\vbox" not in log
    assert "Undefined control sequence" not in log


def test_the_sheet_names_no_attack_on_the_page(printed_set, setup):
    cfg, content, _ = setup
    ctx = veil.context(cfg, content.texts, content.terms)
    assert audience.scan_profile(JOB) is None  # facilitator documents are unscanned: this test is the control
    text = pdf_text(printed_set.out_a / f"{JOB}.pdf")
    assert veil.name_hits(text, ctx, audience.PROFILE_NAMES, squashed=True) == []
    assert veil.name_hits(squash(text), ctx, audience.PROFILE_NAMES, squashed=True) == []


def test_the_capped_worst_case_still_fits_one_page(setup, tmp_path):
    """MAX_VALUE_ROWS rows of the longest real strings, the pointer line and the flag note: one page (D-15, T-07-25)."""
    reason = tex_skip_reason()
    if reason is not None:
        pytest.skip(reason)
    _, _, sheet = setup
    longest = lambda texts: max(texts, key=len)  # noqa: E731
    row = ValueRow(
        label=longest([r.label for r in sheet.values]),
        old=longest([r.old for r in sheet.values]),
        new=longest([r.new for r in sheet.values]),
        flag=next(r.flag for r in sheet.values if r.flag),
    )
    worst = dataclasses.replace(
        sheet, values=(row,) * MAX_VALUE_ROWS, values_more=sheet.values_more or "Weitere Änderungen siehe Karten."
    )
    assert len(worst.values) == MAX_VALUE_ROWS
    source = render.make_env(TEMPLATES).get_template("was_neu.tex.j2").render(sheet=worst)
    stamp_tex = "\\def\\footerstamp{Stand 2026-11-03 · 0123abc}\n"
    pdfs = texbuild.build_documents({JOB: source}, PRINT_DIR, tmp_path, stamp_tex=stamp_tex)
    assert len(PdfReader(pdfs[JOB]).pages) == 1
    reports = FILL.findall(unwrapped_log(tmp_path / f"{JOB}.log"))
    assert len(reports) == 1
    used, limit = float(reports[0][1]), float(reports[0][2])
    assert used <= limit, f"Worst case: {used}pt > {limit}pt"
