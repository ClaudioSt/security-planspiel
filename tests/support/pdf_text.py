"""Shared PDF text helpers for the Phase 5 pdf tests."""
import re

FILL = re.compile(r"PLANSPIEL-FILL page=(\d+) used=([0-9.]+)pt text=([0-9.]+)pt")


def squash(text):
    raise NotImplementedError


def page_texts(pdf_path):
    raise NotImplementedError


def squashed_pages(pdf_path):
    raise NotImplementedError


def pdf_text(pdf_path):
    raise NotImplementedError
