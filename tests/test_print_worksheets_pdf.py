"""Built attack worksheets: two A4 pages, steps on their page, every model fragment on the page (D-05, D-11, D-16).

Run with `uv run pytest -m pdf tests/test_print_worksheets_pdf.py -v`.
"""
import re

import pytest
from pypdf import PdfReader

from planspiel.config import load_config
from planspiel.printmodel import build_attack_sheets
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR

pytestmark = pytest.mark.pdf

FILL = re.compile(r"PLANSPIEL-FILL page=(\d+) used=([0-9.]+)pt text=([0-9.]+)pt")
PT_PER_MM = 72.27 / 25.4


@pytest.fixture(scope="module")
def sheets():
    return build_attack_sheets(load_config(CONFIG_PATH), load_texts(CONTENT_DIR / "texte.toml"))


def _squash(text: str) -> str:
    return re.sub(r"\s+", "", text.replace(" ", " "))


def _pages(pdf_path):
    return [_squash(page.extract_text()) for page in PdfReader(pdf_path).pages]


def _string_parts(line):
    return [part for part in line or () if isinstance(part, str)]


def test_worksheet_jobs_equal_the_model_jobs(printed_set, sheets):
    worksheet_jobs = [job for job in printed_set.jobs if job.startswith("angriff-")]
    assert worksheet_jobs == sorted(sheet.job for sheet in sheets)


def test_each_worksheet_has_exactly_two_pages(printed_set, sheets):
    for sheet in sheets:
        assert len(_pages(printed_set.out_a / f"{sheet.job}.pdf")) == 2, sheet.job


def test_steps_stay_whole_on_their_page(printed_set, sheets):
    for sheet in sheets:
        first, second = _pages(printed_set.out_a / f"{sheet.job}.pdf")
        for key in ("cia", "e_value", "bonus", "reduction"):
            assert _squash(sheet.step_headings[key]) in first, f"{sheet.job}: {key} nicht auf Seite 1"
            assert _squash(sheet.step_headings[key]) not in second, f"{sheet.job}: {key} auch auf Seite 2"
        assert _squash(_string_parts(sheet.reduction_line)[0]) in first, sheet.job
        wanted = ["cases", "wave_kz", *(["recovery"] if sheet.with_recovery else [])]
        for key in wanted:
            assert _squash(sheet.step_headings[key]) in second, f"{sheet.job}: {key} nicht auf Seite 2"
            assert _squash(sheet.step_headings[key]) not in first, f"{sheet.job}: {key} auch auf Seite 1"
        assert _squash(sheet.cap_line[0]) in second, sheet.job
        for line in sheet.cases[2].lines:
            for part in _string_parts(line):
                assert _squash(part) in second, f"{sheet.job}: {part!r} nicht auf Seite 2"


def test_every_model_fragment_is_in_the_pdf_text(printed_set, sheets):
    for sheet in sheets:
        text = "".join(_pages(printed_set.out_a / f"{sheet.job}.pdf"))
        for fragment in sheet.printed_fragments():
            assert _squash(fragment) in text, f"{sheet.job}: {fragment!r} fehlt im PDF"


def test_build_logs_show_no_missing_glyph_and_no_overfull_line(printed_set, sheets):
    for sheet in sheets:
        log = (printed_set.build_a / f"{sheet.job}.log").read_text(encoding="utf-8", errors="replace")
        assert "Missing character" not in log, sheet.job
        assert "Overfull \\hbox" not in log, sheet.job


def test_both_pages_fit_the_text_height_as_measured_in_the_log(printed_set, sheets):
    for sheet in sheets:
        log = (printed_set.build_a / f"{sheet.job}.log").read_text(encoding="utf-8", errors="replace")
        reports = FILL.findall(log)
        assert [number for number, _, _ in reports] == ["1", "2"], f"{sheet.job}: {reports}"
        for number, used, text in reports:
            assert float(used) <= float(text), (
                f"{sheet.job} Seite {number}: {float(used) / PT_PER_MM:.1f} mm belegt, "
                f"{float(text) / PT_PER_MM:.1f} mm Satzspiegel"
            )
