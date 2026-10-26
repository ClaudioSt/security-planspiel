"""Built event deck: two A4 sheets, every card fits its cell, stamp per sheet, card strings on their page (PRINT-06).

Run with `uv run pytest -m pdf tests/test_event_cards_pdf.py -v`.
"""
import re

import pytest
from pypdf import PdfReader

from planspiel.cards import CARDS_PER_SHEET, EVENT_DECK_JOB, build_event_deck, printed_strings
from planspiel.config import load_config
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR
from tests.support.pdf_text import CARD, CARDTITLE, squash, squashed_pages, unwrapped_log

pytestmark = pytest.mark.pdf

STAMP = re.compile(r"Stand\d{4}-\d{2}-\d{2}·[0-9a-f]{7}(?:\+lokal)?")


@pytest.fixture(scope="module")
def deck():
    return build_event_deck(load_config(CONFIG_PATH), load_texts(CONTENT_DIR / "texte.toml"))


@pytest.fixture(scope="module")
def pages(printed_set):
    return squashed_pages(printed_set.out_a / f"{EVENT_DECK_JOB}.pdf")


def _log(printed_set):
    return unwrapped_log(printed_set.build_a / f"{EVENT_DECK_JOB}.log")


def test_the_deck_is_two_a4_landscape_sheets(deck, pages, printed_set):
    assert len(deck.cards) == 8
    assert len(pages) == 2
    mm_per_pt = 25.4 / 72
    for number, page in enumerate(PdfReader(printed_set.out_a / f"{EVENT_DECK_JOB}.pdf").pages, start=1):
        width, height = float(page.mediabox.width) * mm_per_pt, float(page.mediabox.height) * mm_per_pt
        assert (round(width), round(height)) == (297, 210), f"Blatt {number}: {width:.1f} x {height:.1f} mm"


def test_each_sheet_carries_the_stamp_and_the_page_counter_once(pages):
    for number, text in enumerate(pages, start=1):
        assert len(STAMP.findall(text)) == 1, f"Blatt {number}: Stempel nicht genau einmal"
        assert text.count(f"Seite{number}von2") == 1, f"Blatt {number}: Seitenzähler fehlt oder doppelt"


def test_every_card_string_is_on_the_page_that_holds_the_card(deck, pages):
    for index, card in enumerate(deck.cards):
        page = pages[index // CARDS_PER_SHEET]
        for text in printed_strings(card):
            assert squash(text) in page, f"{card.card_id}: {text!r} fehlt auf Blatt {index // CARDS_PER_SHEET + 1}"


def test_every_deck_fragment_is_somewhere_in_the_pdf(deck, pages):
    text = "".join(pages)
    for fragment in deck.printed_fragments():
        assert squash(fragment) in text, f"{fragment!r} fehlt im PDF"


def test_every_card_fits_its_cell_as_logged(printed_set, deck):
    reports = CARD.findall(_log(printed_set))
    assert [card_id for card_id, _, _ in reports] == [card.card_id for card in deck.cards]
    assert len(reports) == 8
    for card_id, used, limit in reports:
        assert float(used) <= float(limit), f"{card_id}: {used}pt > {limit}pt"


def test_every_card_title_is_set_on_one_line_with_room_to_spare(printed_set, deck):
    reports = CARDTITLE.findall(_log(printed_set))
    assert [card_id for card_id, _, _ in reports] == [card.card_id for card in deck.cards]
    for card_id, width, avail in reports:
        assert float(width) <= float(avail), f"{card_id}: title {width}pt wider than the {avail}pt available"
