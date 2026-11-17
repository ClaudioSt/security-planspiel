"""Built dry-run protocol: exactly one A4 page with room to write in every block row (FLOW-05, D-07, D-25).

Run with `uv run pytest -m pdf tests/test_probelauf_pdf.py -v`.
"""
import re

import pytest
from pypdf import PdfReader

from planspiel import audience, render, veil
from planspiel.config import load_config
from planspiel.probelauf import PROBELAUF_JOB, build_probelauf_sheet
from planspiel.texts import load_content
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT
from tests.support.pdf_text import FILL, pdf_text, squash, squashed_pages, unwrapped_log

pytestmark = pytest.mark.pdf

STAMP = re.compile(r"Stand\d{4}-\d{2}-\d{2}·[0-9a-f]{7}(?:\+lokal)?")
TEMPLATES = REPO_ROOT / "print" / "templates"
JOB = PROBELAUF_JOB
MIN_ROW_MM = 12


@pytest.fixture(scope="module")
def setup():
    cfg = load_config(CONFIG_PATH)
    content = load_content(CONTENT_DIR)
    return cfg, content, build_probelauf_sheet(cfg, content.texts)


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


def test_the_protocol_is_exactly_one_a4_page(pdf_path):
    reader = PdfReader(pdf_path)
    assert len(reader.pages) == 1
    box = reader.pages[0].mediabox
    assert (round(float(box.width) / 72 * 25.4), round(float(box.height) / 72 * 25.4)) == (210, 297)


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


def test_every_block_row_keeps_at_least_twelve_millimetres_of_writing_height(setup):
    _, content, sheet = setup
    source = render.make_env(TEMPLATES).get_template("probelauf.tex.j2").render(sheet=sheet)
    strut = re.search(r"\\newcommand\{\\protocolrow\}\{\\rule\[-([\d.]+)mm\]\{0pt\}\{([\d.]+)mm\}\}", source)
    assert strut is not None
    assert float(strut.group(1)) + float(strut.group(2)) >= MIN_ROW_MM
    assert source.count("\\protocolrow{}") == len(sheet.rows)


def test_the_protocol_names_no_attack_on_the_page(printed_set, setup):
    cfg, content, _ = setup
    ctx = veil.context(cfg, content.texts, content.terms)
    assert audience.scan_profile(JOB) is None  # facilitator documents are unscanned: this test is the control
    text = pdf_text(printed_set.out_a / f"{JOB}.pdf")
    assert veil.name_hits(text, ctx, audience.PROFILE_NAMES, squashed=True) == []
    assert veil.name_hits(squash(text), ctx, audience.PROFILE_NAMES, squashed=True) == []


def test_the_real_config_renders_the_protocol_and_the_mini_config_does_not(setup):
    cfg, content, _ = setup
    documents = render.render_all(cfg, content.texts, TEMPLATES)
    assert JOB in documents
    mini = load_config(REPO_ROOT / "tests" / "fixtures" / "mini_config.json")
    mini_content = load_content(MINI_CONTENT_DIR)
    assert JOB not in render.render_all(mini, mini_content.texts, TEMPLATES)
