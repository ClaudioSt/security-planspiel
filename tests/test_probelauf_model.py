"""The dry-run protocol model (FLOW-05, D-07, D-25).

The protocol reads the same schedule rows as the facilitator booklet; its pass rule is digit-free prose, the only number
is the config wave number inside the practice-wave label. The built PDF is covered by tests/test_probelauf_pdf.py.
"""
import dataclasses

import pytest

from planspiel import audience, veil
from planspiel.config import ScheduleBlock, load_config
from planspiel.probelauf import PROBELAUF_JOB, ProtocolRow, ProtocolSheet, build_probelauf_sheet
from planspiel.schedule import schedule_rows
from planspiel.texts import PREWAVE_SHEETS, check_texts, load_content, load_texts, required_keys
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
PRACTICE_LABEL = "Übungswelle (Welle 0)"


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def content():
    return load_content(CONTENT_DIR)


@pytest.fixture(scope="module")
def texts(content):
    return content.texts


@pytest.fixture(scope="module")
def sheet(cfg, texts):
    return build_probelauf_sheet(cfg, texts)


def test_no_protocol_without_a_schedule():
    mini = load_config(MINI)
    mini_texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    assert build_probelauf_sheet(mini, mini_texts) is None


def test_the_real_config_builds_the_facilitator_protocol(sheet):
    assert isinstance(sheet, ProtocolSheet)
    assert sheet.job == PROBELAUF_JOB == "spielleitung-probelauf"
    assert audience.audience_of(sheet.job) == audience.FACILITATOR
    assert all(isinstance(row, ProtocolRow) for row in sheet.rows)


def test_the_probelauf_is_not_a_pre_wave_sheet():
    assert "probelauf" not in PREWAVE_SHEETS


def test_the_rows_are_the_schedule_rows_of_the_booklet(cfg, texts, sheet):
    expected = schedule_rows(cfg, texts)
    assert len(sheet.rows) == len(expected) == len(cfg.session_schedule.blocks)
    for row, source in zip(sheet.rows, expected):
        assert row.label == source.label
        assert row.planned == source.minutes
        assert row.span == f"{source.start} – {source.end}"


def test_a_changed_block_duration_reaches_the_protocol(cfg, texts):
    blocks = tuple(
        dataclasses.replace(block, minutes=block.minutes + 5) if block.id == "wave_1" else block
        for block in cfg.session_schedule.blocks
    )
    changed = dataclasses.replace(
        cfg, session_schedule=dataclasses.replace(cfg.session_schedule, blocks=blocks)
    )
    rows = build_probelauf_sheet(changed, texts).rows
    assert [row.planned for row in rows] == [row.minutes for row in schedule_rows(changed, texts)]
    assert [row.planned for row in rows] != [row.planned for row in build_probelauf_sheet(cfg, texts).rows]


def test_the_header_names_the_seven_columns(texts, sheet):
    keys = ("head_block", "head_planned", "head_span", "head_start", "head_actual", "head_questions", "head_errors")
    assert sheet.header == tuple(texts.get(f"sheets.probelauf.{key}") for key in keys)
    assert len(sheet.header) == 7


def test_the_total_line_is_the_label_and_the_generated_total(cfg, texts, sheet):
    assert sheet.total_label == texts.get("sheets.probelauf.total_label")
    assert sheet.total_value == str(cfg.session_schedule.total_minutes)


def test_four_pass_rules_without_a_practice_row_since_the_practice_sheet_is_a_handout(cfg, texts, sheet):
    # quick 261125-fsu: the shipped schedule has no practice block, so the wave rule names no practice wave
    assert len(sheet.pass_rules) == 4
    assert not [row for row in sheet.rows if row.label == PRACTICE_LABEL]
    assert sheet.pass_rules[0] == (
        f"{texts.get('sheets.probelauf.pass_wave_lead')} {texts.get('sheets.probelauf.pass_wave_tail')}"
    )
    assert sheet.pass_rules[1:] == tuple(texts.get("sheets.probelauf.pass_rules"))
    assert len(texts.get("sheets.probelauf.pass_rules")) == 3


def test_the_wave_rule_names_the_practice_wave_when_a_config_still_has_a_practice_block(cfg, texts):
    blocks = (ScheduleBlock(id="wave_0", minutes=15, wave=0), *cfg.session_schedule.blocks)
    changed = dataclasses.replace(
        cfg,
        session_schedule=dataclasses.replace(
            cfg.session_schedule, blocks=blocks, total_minutes=sum(block.minutes for block in blocks)
        ),
    )
    sheet = build_probelauf_sheet(changed, texts)
    assert PRACTICE_LABEL in sheet.pass_rules[0]
    assert sheet.pass_rules[0] == (
        f"{texts.get('sheets.probelauf.pass_wave_lead')}, {texts.get('sheets.probelauf.pass_wave_practice')} "
        f"{PRACTICE_LABEL}, {texts.get('sheets.probelauf.pass_wave_tail')}"
    )


def test_the_prose_texts_are_digit_free(texts):
    strings = [text for key, text in texts.strings() if key == "sheets.probelauf" or key.startswith("sheets.probelauf.")]
    assert strings
    for text in strings:
        assert not any(char.isdigit() for char in text), text


def test_the_help_log_and_the_signature_lines_come_from_the_texts(texts, sheet):
    assert sheet.help_title == texts.get("sheets.probelauf.help_title")
    assert sheet.observer_label == texts.get("sheets.probelauf.observer_label")
    assert sheet.date_label == texts.get("sheets.probelauf.date_label")


def test_no_printed_string_names_an_attack(cfg, texts, content, sheet):
    ctx = veil.context(cfg, texts, content.terms)
    fragments = sheet.printed_fragments()
    assert fragments
    for text in fragments:
        assert veil.name_hits(text, ctx, audience.PROFILE_NAMES) == [], text


def test_the_fragments_hold_every_printed_string_once(sheet):
    fragments = sheet.printed_fragments()
    assert len(fragments) == len(set(fragments)) and "" not in fragments
    assert PROBELAUF_JOB not in fragments
    for text in (sheet.title, sheet.notice, sheet.intro, *sheet.header, sheet.total_label, sheet.total_value):
        assert text in fragments
    for rule in sheet.pass_rules:
        assert rule in fragments
    for row in sheet.rows:
        assert row.label in fragments and row.span in fragments


def test_the_texts_check_passes_with_the_new_keys(cfg, content):
    keys = required_keys(cfg)
    assert "sheets.probelauf.pass_rules" in keys
    errors = [issue for issue in check_texts(cfg, content) if issue.level == "error"]
    assert errors == []
