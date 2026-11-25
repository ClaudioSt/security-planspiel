"""Proofreading pass 2 (quick 261125-ail, print RC7): the behaviour changes that need code, pinned test-first.

Pure wording changes are pinned by the existing text tests; this module covers what the code now prints differently:
the Teamheft value cells and tier field, the register example without a W label, the Übung start line and event note,
the exfiltration no-Recovery step, the rounding hint on its own line, the review overspend order, and the facilitator
booklet (contents with page numbers, Übung key before Angriff 1, signed slope and RoS).
"""
import re

import pytest

from planspiel import fmt, master, practice, render, was_neu
from planspiel.booklet import build_team_booklet
from planspiel.config import load_config
from planspiel.printmodel import build_attack_sheets
from planspiel.texts import load_clues, load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"


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


def _joined(line):
    return "".join(part if isinstance(part, str) else "▢" for part in line)


def test_the_computed_teamheft_rows_have_a_white_value_cell(rendered):
    ros_page = rendered["spieler-teamheft"].split("Return on Security", 1)[1]
    assert ros_page.count("\\cellcolor{white}") >= 9


def test_the_planning_page_has_a_tier_field_and_relates_costs_to_the_tier_budget(cfg, texts, rendered):
    booklet = build_team_booklet(cfg, texts)
    assert booklet.planning.tier_line == texts.get("sheets.teamheft.tier_field")
    assert booklet.planning.tier_line in rendered["spieler-teamheft"]
    assert "Tier-Budget" in texts.get("sheets.teamheft.planning_instruction")


def test_the_register_examples_carry_no_wave_style_label(cfg, texts):
    register = build_team_booklet(cfg, texts).register
    asset = texts.get("sheets.register.need_example.asset")
    assert register.need_example[0] == asset
    assert register.example[0] == asset


def test_the_ros_page_explains_the_full_damage_amount(cfg, texts):
    ros = build_team_booklet(cfg, texts).ros
    assert ros.avoided_line.note.startswith("= ")
    assert texts.get("sheets.ros.avoided_note") in ros.avoided_line.note


def test_the_practice_sheet_states_budget_and_kz_start_from_the_config(cfg, texts):
    doc = practice.build_practice_document(cfg, texts)
    block = cfg.practice
    assert fmt.format_money(block.budget * 1000) in doc.tracking.start_line
    assert str(block.kz_start) in doc.tracking.start_line
    assert texts.get("practice.start_remaining") in doc.tracking.start_line


def test_the_practice_sheet_says_where_its_event_is(cfg, texts):
    doc = practice.build_practice_document(cfg, texts)
    assert doc.sheet.intro["events_hint"] == texts.get("practice.events_hint")


def test_the_practice_recovery_box_is_followed_by_the_euro_sign(cfg, texts):
    sheet = practice.build_practice_document(cfg, texts).sheet
    assert _joined(sheet.recovery_line).startswith("Schaden nach Recovery = Schaden vor Recovery ▢ € × (1 − r ▢)")


def test_an_attack_without_recovery_says_so_and_names_the_damage_step(cfg, texts):
    sheets = build_attack_sheets(cfg, texts)
    for sheet in sheets:
        if sheet.with_recovery:
            assert sheet.no_recovery_note == ""
        else:
            cases_step = sheet.step_headings["cases"].split(":")[0]
            assert sheet.no_recovery_note
            assert cases_step.split()[-1] in sheet.no_recovery_note
    assert any(not sheet.with_recovery for sheet in sheets)


def test_the_rounding_hint_stands_on_its_own_line_not_inside_the_formula(cfg, texts, rendered):
    sheet = build_attack_sheets(cfg, texts)[0]
    assert _joined(sheet.wave_kz_line).endswith(", gerundet: ▢")
    assert sheet.rounding_note == texts.get("sheets.angriff.rounding_note")
    assert sheet.rounding_note in rendered[sheet.job]


def test_the_review_overspend_rule_reads_kz_before_the_signed_value(cfg, texts):
    from planspiel.eventtext import effect_rows

    rows = effect_rows(cfg.final_events[0], cfg, texts).rows
    assert re.fullmatch(r"Überzogen: KZ −\d+ je angefangene [\d.]+ €", rows[-1].text)


def test_was_neu_overspend_reads_without_a_double_negative(cfg, texts):
    parts = dict(texts.subtree("sheets.was_neu.parts"))
    suffix = was_neu._rule_suffix("overspend", cfg, parts)
    assert suffix.startswith(" 3 KZ je angefangene"), suffix
    assert "−" not in suffix


def test_the_master_contents_carry_page_numbers_and_the_uebung_key_comes_first(cfg, texts, clues, rendered):
    sheet = master.build_master_sheet(cfg, texts, clues)
    source = rendered[master.MASTER_JOB]
    labels = [entry.label for entry in sheet.contents]
    assert len(labels) == len(set(labels)) >= 10
    for label in labels:
        assert f"\\label{{{label}}}" in source
        assert f"\\pageref{{{label}}}" in source
    titles = [entry.title for entry in sheet.contents]
    assert titles.index(sheet.welle0.title) < titles.index(sheet.waves[0].title)
    assert source.index(sheet.welle0.title, source.index("\\step{" + sheet.how_to_title)) < source.index(
        sheet.waves[0].title, source.index("\\step{" + sheet.how_to_title)
    )


def test_the_master_slope_and_the_tier_ros_are_signed(cfg, texts, clues):
    sheet = master.build_master_sheet(cfg, texts, clues)
    slope_label = texts.get("sheets.spielleitung.param_slope")
    for section in sheet.waves:
        slope = dict(section.parameters.rows)[slope_label]
        assert re.fullmatch(r"\+\d+(,\d+)?", slope), slope
    ros_row = next(row for row in sheet.final_rows if row.key == "ros")
    assert all(value[0] in "+−±" for value in ros_row.values)


def test_the_event_plan_heading_has_no_double_colon(cfg, texts, clues, rendered):
    assert "Eventplan der Welle:" not in rendered[master.MASTER_JOB]
