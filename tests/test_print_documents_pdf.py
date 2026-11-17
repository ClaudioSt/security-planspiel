"""Log hygiene of every job of the print set (IN-09): no lost glyph, no overfull line.

`printed_set.jobs` lists whatever the build produced, so every document a later plan registers is covered
without touching this file. Run with `uv run pytest -m pdf tests/test_print_documents_pdf.py -v`.
"""
import pytest

pytestmark = pytest.mark.pdf


def _log(printed_set, job):
    return (printed_set.build_a / f"{job}.log").read_text(encoding="utf-8", errors="replace")


def test_the_print_set_is_not_empty(printed_set):
    assert printed_set.jobs


def test_no_job_logs_a_missing_glyph(printed_set):
    for job in printed_set.jobs:
        assert "Missing character" not in _log(printed_set, job), job


def test_no_job_logs_an_overfull_line(printed_set):
    for job in printed_set.jobs:
        assert "Overfull \\hbox" not in _log(printed_set, job), job
