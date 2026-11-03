"""Built facilitator booklet: notice, wave sections, final table, Welle 0 key, clue matrix, approximations (PRINT-10, D-21).

Run with `uv run pytest -m pdf tests/test_master_pdf.py -v`.
"""
import re

import pytest

from planspiel import master
from planspiel.config import load_config
from planspiel.texts import load_clues, load_content
from tests.support import CONFIG_PATH, CONTENT_DIR
from tests.support.pdf_text import FILL, pdf_text, squash, squashed_pages, unwrapped_log

pytestmark = pytest.mark.pdf

JOB = master.MASTER_JOB
PT_PER_MM = 72.27 / 25.4
STAMP = re.compile(r"Stand\d{4}-\d{2}-\d{2}·[0-9a-f]{7}(?:\+lokal)?")


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def content():
    return load_content(CONTENT_DIR)


@pytest.fixture(scope="module")
def sheet(cfg, content):
    return master.build_master_sheet(cfg, content.texts, load_clues(CONTENT_DIR / "clues.toml"))


def _pages(printed_set):
    return squashed_pages(printed_set.out_a / f"{JOB}.pdf")


def _first_page_with(pages, text, start=0):
    needle = squash(text)
    for number in range(start, len(pages)):
        if needle in pages[number]:
            return number
    raise AssertionError(f"{text!r} steht auf keiner Seite ab {start + 1}")


def _section_pages(pages, sheet):
    """Page range of every wave section: from its title page (after the overview) to the page before the next one."""
    starts = []
    for section in sheet.waves:
        starts.append(_first_page_with(pages, section.title, start=(starts[-1] + 1) if starts else 1))
    review = _first_page_with(pages, sheet.review.intro, start=starts[-1] + 1)
    ends = [*starts[1:], review]
    return [(start, end) for start, end in zip(starts, ends)], review


def test_the_master_pdf_is_built(printed_set):
    assert JOB in printed_set.jobs


def test_page_one_states_the_facilitator_only_notice(printed_set, sheet):
    first = _pages(printed_set)[0]
    assert squash(sheet.notice) in first
    assert squash(sheet.intro) in first
    assert squash(sheet.gr_legend) in first
    for text in sheet.how_to:
        assert squash(text) in first


def test_page_one_lists_the_reference_paths(printed_set, sheet):
    first = _pages(printed_set)[0]
    for line in sheet.paths:
        assert squash(line.tier) in first
        assert squash(line.start) in first
        for window in line.windows:
            assert squash(window) in first


def test_the_schedule_and_print_list_precede_the_waves(printed_set, sheet):
    pages = _pages(printed_set)
    schedule_page = _first_page_with(pages, sheet.schedule.title, start=1)
    assert schedule_page == 1
    ranges, _ = _section_pages(pages, sheet)
    first_wave = ranges[0][0]
    assert first_wave > schedule_page
    text = "".join(pages[schedule_page:first_wave])
    for text_part in (sheet.schedule.title, sheet.schedule.intro, sheet.schedule.total_label,
                      sheet.schedule.total_value, sheet.schedule.print_title, sheet.schedule.print_intro,
                      sheet.schedule.teams_label, sheet.schedule.teams_value,
                      *sheet.schedule.header, *sheet.schedule.print_header):
        assert squash(text_part) in text, text_part
    for row in sheet.schedule.rows:
        for part in (row.label, row.minutes, row.start, row.end, row.direction):
            assert squash(part) in text, (row.block_id, part)
    for row in sheet.schedule.print_rows:
        for part in (row.label, row.file, row.per_team, row.facilitator, row.total):
            assert squash(part) in text, (row.file, part)


def test_the_contents_list_names_the_schedule(printed_set, sheet):
    first = _pages(printed_set)[0]
    assert squash(sheet.schedule.title) in first
    assert squash(sheet.schedule.print_title) in first


def test_every_wave_section_starts_on_its_own_page_with_its_parts(printed_set, sheet):
    pages = _pages(printed_set)
    ranges, _ = _section_pages(pages, sheet)
    assert [start for start, _ in ranges] == sorted({start for start, _ in ranges})
    for section, (start, end) in zip(sheet.waves, ranges):
        text = "".join(pages[start:end])
        assert pages[start].startswith(squash(section.title)) or squash(section.title) in pages[start][:200]
        assert squash(sheet.params_title) in text and squash(sheet.check_title) in text
        assert squash(sheet.events_title) in text and squash(sheet.keys_title) in text
        for label, value in section.parameters.rows:
            assert squash(label) in text and squash(value) in text, (section.wave_id, label)
        for row in (section.parameters.bonus_header, *section.parameters.bonus_rows):
            for cell in row:
                assert squash(cell) in text, (section.wave_id, cell)
        for row in (section.checks.case_header, *section.checks.case_rows, section.checks.table_header, *section.checks.table_rows):
            for cell in row:
                assert squash(cell) in text, (section.wave_id, cell)
        for event in section.events:
            for part in (event.name, event.kind, event.heading, *event.lines):
                assert squash(part) in text, (section.wave_id, part)
        for row in (section.key_header, *((row.label, *row.values) for row in section.key_rows)):
            for cell in row:
                assert squash(cell) in text, (section.wave_id, cell)


def test_the_budget_review_the_final_table_and_welle_zero_follow_the_waves(printed_set, sheet):
    pages = _pages(printed_set)
    ranges, review = _section_pages(pages, sheet)
    assert review > ranges[-1][0]
    tail = "".join(pages[review:])
    for text in (sheet.review.title, sheet.review.tier_heading, *sheet.review.tier_lines, sheet.review.x_label,
                 sheet.review.x_value, sheet.review.step_label, sheet.review.step_value):
        assert squash(text) in tail, text
    for text in (sheet.final_title, sheet.final_intro, sheet.final_note, *sheet.final_header):
        assert squash(text) in tail, text
    for row in sheet.final_rows:
        for cell in (row.label, *row.values):
            assert squash(cell) in tail, cell
    for text in (sheet.welle0.title, sheet.welle0.intro, *sheet.welle0.header):
        assert squash(text) in tail, text
    for row in sheet.welle0.rows:
        for cell in (row.label, *row.values):
            assert squash(cell) in tail, cell


def test_the_debrief_page_follows_the_final_table_and_precedes_welle_zero(printed_set, sheet):
    pages = _pages(printed_set)
    _, review = _section_pages(pages, sheet)
    debrief_page = _first_page_with(pages, sheet.debrief.title, start=review)
    assert debrief_page > review
    assert sum(squash(sheet.debrief.intro) in page for page in pages) == 1
    assert _first_page_with(pages, sheet.welle0.title, start=review) > debrief_page
    assert debrief_page < _first_page_with(pages, sheet.clues_intro, start=debrief_page)
    text = pages[debrief_page]
    parts = [sheet.debrief.title, sheet.debrief.intro, sheet.debrief.guide_label, sheet.debrief.questions_label,
             sheet.debrief.prompts_label, sheet.debrief.compare_title, sheet.debrief.compare_intro,
             sheet.debrief.total_label, sheet.debrief.total_value, *sheet.debrief.compare_header,
             *sheet.debrief.compare_rows]
    for section in sheet.debrief.stages:
        parts += [section.title, section.guide, *section.questions, *section.prompts]
    for part in parts:
        assert squash(part) in text, part


def test_the_contents_list_names_the_debrief(printed_set, sheet):
    assert squash(sheet.debrief.title) in _pages(printed_set)[0]


def test_every_final_index_is_printed_exactly_with_the_weight_row(printed_set, sheet, content):
    pages = _pages(printed_set)
    page = pages[_first_page_with(pages, sheet.final_title, start=1)]
    assert "vorläufig" not in page
    for result in sheet.tiers:
        assert squash(result.ros) in page
        assert squash(result.final_index) in page
    assert squash(sheet.final_weight_label) in page
    assert squash(sheet.final_weight_value) in page


def test_the_clue_matrix_lists_every_clue(printed_set, sheet):
    text = "".join(_pages(printed_set))
    entries = [entry for group in sheet.clue_groups for entry in group.rows]
    assert len(entries) == len(load_clues(CONTENT_DIR / "clues.toml"))
    for group in sheet.clue_groups:
        assert squash(group.title) in text
    for entry in entries:
        for part in (entry.document, entry.section, entry.quote, entry.why, entry.measures):
            assert squash(part) in text, part


def test_every_model_fragment_is_in_the_pdf_text(printed_set, sheet):
    text = "".join(_pages(printed_set))
    for fragment in sheet.printed_fragments():
        assert squash(fragment) in text, f"{fragment!r} fehlt im PDF"


def test_the_approximation_sign_is_in_no_pdf(printed_set):
    for pdf in sorted(printed_set.out_a.glob("*.pdf")):
        assert "≈" not in pdf_text(pdf), pdf.name


def test_build_log_shows_no_missing_glyph_and_no_overfull_line(printed_set):
    log = (printed_set.build_a / f"{JOB}.log").read_text(encoding="utf-8", errors="replace")
    assert "Missing character" not in log
    assert "Overfull \\hbox" not in log
    assert "Overfull \\vbox" not in log


def test_every_page_fits_the_text_height_as_measured_in_the_log(printed_set):
    reports = FILL.findall(unwrapped_log(printed_set.build_a / f"{JOB}.log"))
    assert len(reports) == len(_pages(printed_set)), reports
    for number, used, text in reports:
        assert float(used) <= float(text), (
            f"Bericht {number}: {float(used) / PT_PER_MM:.1f} mm belegt, {float(text) / PT_PER_MM:.1f} mm Satzspiel"
        )


def test_the_stamp_is_on_every_page(printed_set):
    for number, page in enumerate(_pages(printed_set), start=1):
        assert STAMP.search(page), f"Seite {number} ohne Stempel"
