"""Built team booklet: register page first, then planning, RoS and Budget Review last, every page fits as measured in the log (PRINT-07, RISK-02).

Run with `uv run pytest -m pdf tests/test_booklet_pdf.py -v`.
"""
import re

import pytest
from pypdf import PdfReader

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


def _log(printed_set):
    return unwrapped_log(printed_set.build_a / f"{BOOKLET_JOB}.log")


def _page_of(pages, text):
    found = [number for number, page in enumerate(pages) if squash(text) in page]
    assert found, f"{text!r} fehlt im PDF"
    return found


def test_the_booklet_is_a4_portrait_with_the_register_page_first(printed_set, pages, booklet):
    assert len(pages) == 5, "register, planning, tracking, RoS and Budget Review"
    mm_per_pt = 25.4 / 72
    for number, page in enumerate(PdfReader(printed_set.out_a / f"{BOOKLET_JOB}.pdf").pages, start=1):
        width, height = float(page.mediabox.width) * mm_per_pt, float(page.mediabox.height) * mm_per_pt
        assert (round(width), round(height)) == (210, 297), f"Seite {number}: {width:.1f} x {height:.1f} mm"
    assert _page_of(pages, booklet.register.title)[0] == 0
    assert _page_of(pages, booklet.planning.title)[0] == 1


def test_the_register_page_holds_every_register_string(pages, booklet):
    first = pages[0]
    fragments = booklet.register.printed_fragments()
    assert fragments
    for text in fragments:
        assert squash(text) in first, text
    for text in (*booklet.register.rows, *booklet.register.band_ranges):
        assert squash(text) in first, text


def test_the_planning_page_holds_the_cost_table_the_tier_rows_and_the_anticipated_sum(pages, booklet):
    first = pages[1]
    planning = booklet.planning
    for text in (*planning.cost_header, planning.step_costs, planning.step_tiers, planning.step_planning):
        assert squash(text) in first, text
    for row in planning.cost_rows:
        for cell in row:
            assert squash(cell) in first, cell
    for row in (planning.tier_header, *planning.tier_rows):
        for cell in row:
            assert squash(cell) in first, cell
    for text in (
        *planning.planning_header, *planning.planning_rows, planning.planning_hint, planning.sum_label,
        planning.anticipated_line,
    ):
        assert squash(text) in first, text


def test_the_ros_part_starts_on_a_new_page_and_holds_the_ros_formula(pages, booklet):
    ros = booklet.ros
    ros_page = _page_of(pages, ros.title)[0]
    assert ros_page == _page_of(pages, booklet.tracking.title)[0] + 1, "the RoS page follows the tracking page"
    page = pages[ros_page]
    for metric in (*ros.own_cost_rows, *ros.damage_rows, ros.damage_sum, ros.avoided_line, ros.ros_line):
        assert squash(metric.label) in page, metric.label
        if metric.note:
            assert squash(metric.note) in page, metric.note
    assert squash(ros.ros_line.note) not in pages[1]


def test_the_budget_review_page_holds_all_tier_rows_and_all_penalty_rows(pages, booklet):
    ros = booklet.ros
    review_page = _page_of(pages, ros.review_title)[-1]
    assert review_page == len(pages) - 1, "the Budget Review is the last page of the booklet"
    page = pages[review_page]
    for row in (ros.tier_header, *ros.tier_rows, ros.penalty_header, *ros.penalty_rows):
        for cell in row:
            assert squash(cell) in page, cell
    for metric in (*ros.budget_rows, ros.remaining_line):
        assert squash(metric.label) in page, metric.label
        if metric.note:
            assert squash(metric.note) in page, metric.note
    assert squash(ros.overspend_rule) in page
    assert squash(ros.sign_hint) in page


def test_every_digit_bearing_fragment_is_somewhere_in_the_pdf(pages, booklet):
    text = "".join(pages)
    for fragment in booklet.printed_fragments():
        if any(char.isdigit() for char in fragment):
            assert squash(fragment) in text, f"{fragment!r} fehlt im PDF"


def test_every_page_fits_the_text_height_as_measured_in_the_log(printed_set, pages):
    reports = FILL.findall(_log(printed_set))
    assert len(reports) == len(pages), "every page ends with a fill report, so no page broke by itself"
    assert [int(number) for number, _, _ in reports] == list(range(1, len(pages) + 1))
    for number, used, limit in reports:
        assert float(used) <= float(limit), f"Seite {number}: {used}pt > {limit}pt"


def test_the_review_page_is_proven_for_the_current_row_count(printed_set, booklet):
    from planspiel.booklet import MAX_PENALTY_ROWS

    assert len(booklet.ros.penalty_rows) == MAX_PENALTY_ROWS
    used, limit = (float(value) for value in FILL.findall(_log(printed_set))[-1][1:])
    assert used <= limit


def test_stamp_and_page_counter_are_on_every_page(pages):
    total = len(pages)
    for number, text in enumerate(pages, start=1):
        assert len(STAMP.findall(text)) == 1, f"Seite {number}: Stempel nicht genau einmal"
        assert text.count(f"Seite{number}von{total}") == 1, f"Seite {number}: Seitenzähler fehlt oder doppelt"


def test_the_build_log_has_no_missing_glyph_and_no_overfull_line(printed_set):
    log = _log(printed_set)
    assert "Missing character" not in log
    assert "Overfull \\hbox" not in log


def test_the_ros_page_carries_the_purpose_sentence(pages, booklet):
    ros_page = _page_of(pages, booklet.ros.title)[0]
    assert squash(booklet.ros.purpose) in pages[ros_page]
    assert squash(booklet.ros.purpose) not in pages[1], "not on the planning page"
