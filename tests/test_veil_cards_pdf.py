"""Information boundary of VEIL-04 in the built PDFs: nothing on the measure deck, everything on the worksheets.

The deck carries no wave weight, bonus reason, attack name or wave reference. Each revealed attack worksheet
carries its own wave's weights and every row of its bonus table (ROADMAP SC5, T-05-13, T-05-14).

Run with `uv run pytest -m pdf tests/test_veil_cards_pdf.py -v`.
"""
import pytest

from planspiel import audience, veil
from planspiel.cards import build_measure_deck
from planspiel.config import load_config
from planspiel.printmodel import build_attack_sheets
from planspiel.texts import PreAttackView, load_content
from tests.support import CONFIG_PATH, CONTENT_DIR
from tests.support.pdf_text import pdf_text, squash, squashed_pages

pytestmark = pytest.mark.pdf

DECK_JOB = audience.MEASURE_DECK_JOB
WAVE_IDS = [wave.wave_id for wave in load_config(CONFIG_PATH).waves]


def _plain(text: str) -> str:
    """Squashed and without hyphens: a word may be hyphenated at a line end in the PDF."""
    return squash(text).replace("-", "")


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def content():
    return load_content(CONTENT_DIR)


@pytest.fixture(scope="module")
def ctx(cfg, content):
    return veil.context(cfg, content.texts, content.terms)


@pytest.fixture(scope="module")
def sheets(cfg, content):
    return {sheet.wave_id: sheet for sheet in build_attack_sheets(cfg, content.texts)}


def _string_parts(line):
    return [part for part in line if isinstance(part, str)]


def test_the_deck_pdf_carries_no_weight_triple_and_passes_the_veil_scan(printed_set, ctx):
    text = pdf_text(printed_set.out_a / f"{DECK_JOB}.pdf")
    assert veil.weight_hits(text, ctx.signatures) == []
    assert veil.weight_symbol_hits(text) == []
    assert veil.scan_text(text, DECK_JOB, ctx, layer="pdf") == []


def test_the_deck_pdf_carries_no_bonus_reason_or_attack_name(printed_set, cfg, content, ctx):
    squashed = "".join(squashed_pages(printed_set.out_a / f"{DECK_JOB}.pdf"))
    plain = squashed.replace("-", "")
    reasons = [
        text for attack_id in cfg.attacks for _, text in content.texts.strings(f"attacks.{attack_id}.revealed.bonus_reasons")
    ]
    assert reasons
    for reason in reasons:
        assert _plain(reason) not in plain, reason
    for key, strings in ctx.revealed.items():
        for name, text in strings:
            assert _plain(text) not in plain, f"{key}.{name}"
    assert veil.name_hits(squashed, ctx, audience.PROFILE_NAMES, squashed=True) == []


def test_no_deck_page_prints_a_veiled_attack_title(printed_set, cfg, content):
    view = PreAttackView(cfg, content.texts)
    titles = [_plain(view.attack_title(wave)) for wave in cfg.waves]
    for number, page in enumerate(squashed_pages(printed_set.out_a / f"{DECK_JOB}.pdf"), start=1):
        for title in titles:
            assert title not in page.replace("-", ""), f"Seite {number}: {title}"


def test_the_deck_pdf_tells_players_where_weights_and_bonus_are_revealed(printed_set, cfg, content):
    note = build_measure_deck(cfg, content.texts).cards[0].reveal_note
    squashed = "".join(squashed_pages(printed_set.out_a / f"{DECK_JOB}.pdf")).replace("-", "")
    assert _plain(note) in squashed


@pytest.mark.parametrize("wave_id", WAVE_IDS, ids=lambda wave_id: f"wave{wave_id}")
def test_a_revealed_worksheet_prints_its_own_weights_and_no_other_wave_s(printed_set, sheets, ctx, wave_id):
    sheet = sheets[wave_id]
    text = pdf_text(printed_set.out_a / f"{sheet.job}.pdf")
    assert veil.weight_hits(text, ctx.signatures) == [wave_id]


@pytest.mark.parametrize("wave_id", WAVE_IDS, ids=lambda wave_id: f"wave{wave_id}")
def test_a_revealed_worksheet_prints_every_row_of_its_bonus_table_on_page_1(printed_set, sheets, wave_id):
    sheet = sheets[wave_id]
    first = squashed_pages(printed_set.out_a / f"{sheet.job}.pdf")[0].replace("-", "")
    assert sheet.bonus_table
    for label, _min_level, points, reason in sheet.bonus_table:
        assert _plain(label) in first, f"{sheet.job}: Maßnahme {label!r}"
        assert _plain(points) in first, f"{sheet.job}: Punkte {points!r}"
        assert _plain(reason) in first, f"{sheet.job}: Grund {reason!r}"
    assert len(sheet.bonus_table) == len(sheet.bonus_rows)


@pytest.mark.parametrize("wave_id", WAVE_IDS, ids=lambda wave_id: f"wave{wave_id}")
def test_a_revealed_worksheet_prints_the_e_value_line_with_its_weights_on_page_1(printed_set, sheets, wave_id):
    sheet = sheets[wave_id]
    first = squashed_pages(printed_set.out_a / f"{sheet.job}.pdf")[0].replace("-", "")
    parts = _string_parts(sheet.e_value_line)
    weighted = [part for part in parts if "×" in part]
    assert len(weighted) == 3
    for part in parts:
        assert _plain(part) in first, f"{sheet.job}: {part!r}"
