"""Built wave explainer: exactly one A4 page, every step and table printed, fill marker within the page, veil clean.

Run with `uv run pytest -m pdf tests/test_wave_page_pdf.py -v`.
"""
import re

import pytest
from pypdf import PdfReader

from planspiel import audience, veil
from planspiel.config import load_config
from planspiel.texts import load_content
from planspiel.wave_page import WAVE_PAGE_JOB, build_wave_page
from tests.support import CONFIG_PATH, CONTENT_DIR
from tests.support.pdf_text import FILL, pdf_text, squash, squashed_pages, unwrapped_log

pytestmark = pytest.mark.pdf

STAMP = re.compile(r"Stand\d{4}-\d{2}-\d{2}·[0-9a-f]{7}(?:\+lokal)?")


@pytest.fixture(scope="module")
def setup():
    cfg = load_config(CONFIG_PATH)
    content = load_content(CONTENT_DIR)
    return cfg, content, build_wave_page(cfg, content.texts)


@pytest.fixture(scope="module")
def pdf_path(printed_set):
    return printed_set.out_a / f"{WAVE_PAGE_JOB}.pdf"


@pytest.fixture(scope="module")
def page_text(pdf_path):
    pages = squashed_pages(pdf_path)
    assert len(pages) == 1
    return pages[0]


def _log(printed_set):
    return unwrapped_log(printed_set.build_a / f"{WAVE_PAGE_JOB}.log")


def test_the_explainer_is_exactly_one_a4_page(pdf_path):
    reader = PdfReader(pdf_path)
    assert len(reader.pages) == 1
    box = reader.pages[0].mediabox
    assert (round(float(box.width) / 72 * 25.4), round(float(box.height) / 72 * 25.4)) == (210, 297)


def test_the_page_holds_every_step_heading_and_text(page_text, setup):
    _, _, page = setup
    assert squash(page.title) in page_text and squash(page.intro) in page_text
    for step in page.steps:
        assert squash(step.heading) in page_text, step.heading
        assert squash(step.text) in page_text, step.key


def test_the_page_holds_the_effects_table(page_text, setup):
    _, _, page = setup
    for text in (*page.effects_header, *page.attack_effects, *page.event_effects, page.ros_note):
        assert squash(text) in page_text, text


def test_the_page_holds_the_rounding_and_clamp_texts(page_text, setup):
    _, _, page = setup
    assert squash(page.rounding_text) in page_text
    assert squash(page.clamp_text) in page_text
    assert page.clamp_text.endswith("0 bis 100")


def test_the_page_holds_the_recovery_section_with_all_four_rows(page_text, setup):
    _, _, page = setup
    for text in (page.recovery_title, page.recovery_subtitle, page.recovery_narrative, *page.recovery_header):
        assert squash(text) in page_text, text
    assert len(page.recovery_rows) == 4
    for level, label, factor in page.recovery_rows:
        assert squash(label) in page_text and squash(factor) in page_text


def test_every_printed_fragment_is_on_the_page(page_text, setup):
    _, _, page = setup
    for fragment in page.printed_fragments():
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
    assert "Overfull \hbox" not in log
    assert "Overfull \vbox" not in log
    assert "Undefined control sequence" not in log


def test_the_explainer_passes_the_layer_two_veil_scan(printed_set, setup):
    cfg, content, _ = setup
    ctx = veil.context(cfg, content.texts, content.terms)
    assert audience.scan_profile(WAVE_PAGE_JOB) == audience.PROFILE_STORY
    text = pdf_text(printed_set.out_a / f"{WAVE_PAGE_JOB}.pdf")
    assert veil.scan_text(text, WAVE_PAGE_JOB, ctx, layer="pdf") == []
