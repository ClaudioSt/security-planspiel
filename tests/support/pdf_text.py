"""Shared PDF text helpers for the Phase 5 pdf tests.

pypdf drops most word spaces from the extracted text (research F10), so the veil scan and the layout tests work on
whitespace-squashed text; `pdf_text` keeps the raw text for the weight-triple windows.
"""
import re

from pypdf import PdfReader

FILL = re.compile(r"PLANSPIEL-FILL page=(\d+) used=([0-9.]+)pt text=([0-9.]+)pt")
CARD = re.compile(r"PLANSPIEL-CARD id=(\S+) used=([0-9.]+)pt limit=([0-9.]+)pt")
CARDTITLE = re.compile(r"PLANSPIEL-CARDTITLE id=(\S+) width=([0-9.]+)pt avail=([0-9.]+)pt")


def squash(text: str) -> str:
    return re.sub(r"\s+", "", text.replace(" ", " "))


def page_texts(pdf_path) -> list[str]:
    return [page.extract_text() for page in PdfReader(pdf_path).pages]


def squashed_pages(pdf_path) -> list[str]:
    return [squash(text) for text in page_texts(pdf_path)]


def pdf_text(pdf_path) -> str:
    return "\n".join(page_texts(pdf_path))


TEX_LOG_WIDTH = 79


def unwrapped_log(path) -> str:
    """The TeX log with its hard line breaks removed: TeX wraps every log line at 79 characters, which would split a
    long card id or a measured value in the PLANSPIEL-CARD and PLANSPIEL-CARDTITLE lines."""
    text = path.read_text(encoding="utf-8", errors="replace")
    return re.sub(rf"(?m)^(.{{{TEX_LOG_WIDTH}}})\n", r"\1", text)
