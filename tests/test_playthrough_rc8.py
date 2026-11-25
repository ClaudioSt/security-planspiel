"""Play-through review of print RC7 (quick 261125-djw, print RC8): behaviour changes pinned test-first.

Wording-only changes are pinned next to their texts; this module covers what the code prints differently.
"""
import pytest

from planspiel import render
from planspiel.config import load_config
from planspiel.texts import load_clues, load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"
BS = chr(92)
ROWSTRUT = BS + "rowstrutgrid{}"
SHADED = BS + "shadedcell{}"


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def texts():
    return load_texts(CONTENT_DIR / "texte.toml")


@pytest.fixture(scope="module")
def clues():
    return load_clues(CONTENT_DIR / "clues.toml")


@pytest.fixture(scope="module")
def rendered(cfg, texts, clues):
    return render.render_all(cfg, texts, TEMPLATES, clues)


def _tracking_row(source: str, label: str) -> str:
    return next(line for line in source.splitlines() if line.startswith(ROWSTRUT) and label in line)


def test_v1_the_event_rows_of_the_tracking_sheet_print_no_grey_cell_in_a_wave_column(texts, rendered):
    """Only the Start and the Budget Review column stay crossed out: no wave column tells where an event comes."""
    source = rendered["spieler-teamheft"]
    for key in ("row_external_budget", "row_external_opex"):
        line = _tracking_row(source, texts.get(f"sheets.tracking.{key}"))
        cells = line.split("&")
        assert line.count(SHADED) == 2, (key, line)
        assert SHADED in cells[1] and SHADED in cells[-1], key


def test_d2_the_print_list_says_to_print_everything_single_sided(texts):
    assert texts.get("sheets.ablauf.print_intro").startswith("Druckt alles einseitig.")


def test_d2_the_start_column_of_the_tracking_sheet_is_instructed_twice(texts):
    for key in ("sheets.tracking.intro", "sheets.ablauf.blocks.measures_budget.direction"):
        text = texts.get(key)
        assert "Spalte Start" in text, key
        assert all(word in text for word in ("KZ-Start", "Init-Kosten", "Restbudget")), key
    assert "Tier-Budget minus Init-Kosten" in texts.get("sheets.ablauf.blocks.measures_budget.direction")


def test_d2_the_attack_sheets_say_to_enter_zero_without_a_kz_event_card(texts):
    assert texts.get("sheets.angriff.events_hint").endswith("Nennt keine Eventkarte eine KZ-Wirkung, tragt ±0 ein.")


def test_d2_teamheft_page_five_sends_the_teams_back_to_the_tracking_sheet(texts):
    text = texts.get("sheets.teamheft.review_intro")
    assert text.endswith("in der Spalte Budget Review ein und berechnet dort die KZ final.")
    assert texts.get("sheets.tracking.title") in text


def test_d2_the_closing_direction_keeps_the_teamheft_with_the_teams_and_notes_the_comparison(texts):
    text = texts.get("sheets.ablauf.blocks.closing.direction")
    assert "Sammelt" not in text and "einsammeln" not in text
    assert "berechnen zuletzt im Tracking-Bogen die KZ final" in text
    assert "Notiert je Team KZ final und RoS in der Vergleichstabelle" in text
    assert "die Teamhefte bleiben bei den Teams" in text
    assert texts.get("sheets.debrief.compare_title") in text


def test_d3_the_tracking_hint_says_what_to_enter_when_a_wave_has_no_event_of_that_kind(texts):
    text = texts.get("sheets.tracking.external_hint")
    assert "kein Event dieser Art" in text and "leer" in text and "null" in text

