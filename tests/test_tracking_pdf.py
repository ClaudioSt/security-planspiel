"""Built tracking sheet: exactly one A4 page between planning and RoS, every label printed, fill marker within the page.

Run with `uv run pytest -m pdf tests/test_tracking_pdf.py -v`.
"""
import re

import pytest

from planspiel.booklet import BOOKLET_JOB, build_team_booklet
from planspiel.config import load_config
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR
from tests.support.pdf_text import FILL, squash, squashed_pages, unwrapped_log

pytestmark = pytest.mark.pdf

STAMP = re.compile(r"Stand\d{4}-\d{2}-\d{2}·[0-9a-f]{7}(?:\+lokal)?")


@pytest.fixture(scope="module")
def booklet():
    return build_team_booklet(load_config(CONFIG_PATH), load_texts(CONTENT_DIR / "texte.toml"))


@pytest.fixture(scope="module")
def pages(printed_set):
    return squashed_pages(printed_set.out_a / f"{BOOKLET_JOB}.pdf")


@pytest.fixture(scope="module")
def tracking_index(pages, booklet):
    found = [number for number, page in enumerate(pages) if squash(booklet.tracking.title) in page]
    assert len(found) == 1, "the tracking title is printed on exactly one page"
    return found[0]


def _log(printed_set):
    return unwrapped_log(printed_set.build_a / f"{BOOKLET_JOB}.log")


def test_the_tracking_sheet_is_one_page_between_planning_and_ros(pages, booklet, tracking_index):
    planning = next(n for n, page in enumerate(pages) if squash(booklet.planning.title) in page)
    ros = next(n for n, page in enumerate(pages) if squash(booklet.ros.title) in page)
    assert planning == 0 and tracking_index == 1 and ros == 2
    page = pages[tracking_index]
    assert squash(booklet.ros.title) not in page and squash(booklet.planning.title) not in page


def test_the_page_holds_every_column_head_row_label_and_both_block_titles(pages, booklet, tracking_index):
    page = pages[tracking_index]
    tracking = booklet.tracking
    for text in (*tracking.columns, tracking.title, tracking.step_waves, tracking.block_own, tracking.block_external):
        assert squash(text) in page, text
    for row in tracking.rows:
        assert squash(row.label) in page, row.label


def test_the_page_holds_the_window_blocks_with_all_measure_labels_and_the_summary(pages, booklet, tracking_index):
    page = pages[tracking_index]
    tracking = booklet.tracking
    assert squash(tracking.step_windows) in page and squash(tracking.measure_header) in page
    for block in tracking.windows:
        assert squash(block.after_wave) in page, block.after_wave
        for label in block.measure_rows:
            assert squash(label) in page, label
    for label in tracking.window_columns:
        assert squash(label) in page, label
    for row in tracking.summary_rows:
        assert squash(row.label) in page, row.label
    for text in (*tracking.hints, *tracking.window_hints, tracking.window_intro, tracking.intro):
        assert squash(text) in page, text


def test_the_clamp_sentence_names_zero_and_one_hundred(pages, booklet, tracking_index):
    assert squash(booklet.tracking.clamp_text) in pages[tracking_index]
    assert booklet.tracking.clamp_text.endswith("0 bis 100")


def test_the_tracking_page_fits_the_text_height_as_measured_in_the_log(printed_set, pages, tracking_index):
    reports = FILL.findall(_log(printed_set))
    assert len(reports) == len(pages)
    number, used, limit = reports[tracking_index]
    assert int(number) == tracking_index + 1
    assert float(used) <= float(limit), f"Tracking-Seite: {used}pt > {limit}pt"


def test_stamp_and_page_counter_are_on_the_tracking_page(pages, tracking_index):
    page = pages[tracking_index]
    assert len(STAMP.findall(page)) == 1
    assert page.count(f"Seite{tracking_index + 1}von{len(pages)}") == 1


def test_the_build_log_has_no_missing_glyph_and_no_overfull_line(printed_set):
    log = _log(printed_set)
    assert "Missing character" not in log
    assert "Overfull \\hbox" not in log
    assert "Overfull \\vbox" not in log
