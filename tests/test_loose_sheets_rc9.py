"""No joint practice wave, Teamheft as loose sheets (quick 261125-fsu, print RC9).

The practice sheet is a reference handout of the Maßnahmen-und-Budget block (no `wave_0` block, no box that asks the
teams to calculate it together) and the Teamheft is handed out per block, so the facilitator directions name its
chapters with the printed page titles and the print list says not to staple it.
"""
import dataclasses
import pytest

from planspiel import practice
from planspiel.config import load_config
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def texts():
    return load_texts(CONTENT_DIR / "texte.toml")


def _direction(texts, block):
    return texts.get(f"sheets.ablauf.blocks.{block}.direction")


# --- the practice sheet -----------------------------------------------------------------------------------------


def test_the_practice_sheet_has_no_intro_box_any_more(cfg, texts):
    doc = practice.build_practice_document(cfg, texts)
    assert "intro" not in {field.name for field in dataclasses.fields(doc)}
    assert not texts.has("practice.intro")
    assert "doc.intro" not in (TEMPLATES / "uebung.tex.j2").read_text(encoding="utf-8")
    assert "intro is defined" not in (TEMPLATES / "angriff_blatt.tex.j2").read_text(encoding="utf-8")


def test_the_practice_title_says_it_is_an_example_that_does_not_count(cfg, texts):
    doc = practice.build_practice_document(cfg, texts)
    assert doc.title == "Welle 0 – Übung (Beispiel, zählt nicht für die Wertung)"
    assert doc.sheet.title == doc.title


# --- the schedule has no practice block ---------------------------------------------------------------------------


def test_the_schedule_has_no_practice_block_and_still_prints_the_practice_sheet(cfg):
    schedule = cfg.session_schedule
    assert not [block for block in schedule.blocks if block.wave == 0 or block.id == "wave_0"]
    assert schedule.total_minutes == sum(block.minutes for block in schedule.blocks) == 200
    assert "uebung-welle-0" in {row.job for row in schedule.print_list}


# --- facilitator directions: the Teamheft by chapter --------------------------------------------------------------


def test_story_groups_hands_out_only_the_protection_need_chapter(texts):
    direction = _direction(texts, "story_groups")
    assert f"Teamheft ({texts.get('sheets.register.page_title')})" in direction


def test_measures_budget_hands_out_cards_practice_sheet_wave_page_and_two_chapters_together(texts):
    direction = _direction(texts, "measures_budget")
    labels = {key: texts.get(f"sheets.ablauf.print.{key}") for key in (
        "spieler-massnahmenkarten", "uebung-welle-0", "spieler-so-funktioniert-eine-welle")}
    for label in labels.values():
        assert label in direction, label
    chapters = f"{texts.get('sheets.teamheft.planning_title')}, {texts.get('sheets.tracking.title')}"
    assert f"Teamheft ({chapters})" in direction
    assert "nicht gemeinsam" in direction, "the practice sheet is an aid that is not calculated together"
    assert "Spalte Start" in direction


def test_the_practice_wave_has_no_direction_block_text(texts):
    assert not texts.has("sheets.ablauf.blocks.wave_0")


def test_closing_hands_out_the_last_two_chapters_with_the_event_card(texts):
    direction = _direction(texts, "closing")
    chapters = f"{texts.get('sheets.teamheft.ros_title')}, {texts.get('sheets.teamheft.review_title')}"
    assert f"Teamheft ({chapters})" in direction
    assert "Eventkarte" in direction and texts.get("sheets.teamheft.review_title") in direction
    assert "die Blätter bleiben bei den Teams" in direction
    assert "Teamhefte" not in direction


def test_the_print_list_says_the_teamheft_is_printed_per_team_and_not_stapled(texts):
    intro = texts.get("sheets.ablauf.print_intro")
    assert "Teamheft" in intro and "nicht" in intro and "heftet" in intro
    assert intro.startswith("Druckt alles einseitig.")


def test_the_debrief_asks_for_the_sheets_not_for_the_booklet(texts):
    intro = texts.get("sheets.debrief.intro")
    assert "legen dafür ihre Blätter" in intro
    assert "ihr Teamheft" not in intro

