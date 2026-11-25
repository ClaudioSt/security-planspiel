"""Schedule and print-list model of the facilitator booklet (FLOW-02, D-01, D-04, D-23).

Numbers come from `session_schedule`, words from `sheets.ablauf`; no label or direction names an attack or types a digit.
"""
import dataclasses

import pytest

from planspiel import audience, printmodel, render, schedule, veil
from planspiel.config import load_config
from planspiel.printmodel import PrintModelError
from planspiel.texts import PREWAVE_SHEETS, load_clues, load_content, load_texts, required_keys
from planspiel.was_neu import BASELINE_FILE, load_baseline
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"


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
def page(cfg, texts):
    return schedule.build_schedule_page(cfg, texts)


# --- schedule rows ---------------------------------------------------------------------------------------------


def test_one_row_per_block_with_running_minutes(cfg, texts):
    rows = schedule.schedule_rows(cfg, texts)
    blocks = cfg.session_schedule.blocks
    assert [row.block_id for row in rows] == [block.id for block in blocks]
    assert [row.minutes for row in rows] == [str(block.minutes) for block in blocks]
    assert (rows[0].start, rows[0].end) == ("0", "10")
    assert rows[-1].end == str(cfg.session_schedule.total_minutes)
    for earlier, later in zip(rows, rows[1:]):
        assert earlier.end == later.start


def test_wave_labels_are_composed_from_the_texte_word_and_the_config_wave(cfg, texts):
    rows = {row.block_id: row for row in schedule.schedule_rows(cfg, texts)}
    words = texts.subtree("sheets.ablauf")
    for wave in cfg.waves:
        assert rows[f"wave_{wave.wave_id}"].label == f"{words['wave_label']} {wave.wave_id}"
    assert "wave_0" not in rows, "the practice sheet is a handout, not a block (quick 261125-fsu)"
    assert rows["intro"].label == words["blocks"]["intro"]["label"]
    assert rows["debrief"].direction == words["blocks"]["debrief"]["direction"]


def test_no_digit_is_typed_in_the_ablauf_texts(texts):
    for key, text in texts.strings("sheets.ablauf"):
        assert not any(character.isnumeric() for character in text), key


# --- print list -------------------------------------------------------------------------------------------------


def test_print_rows_follow_config_with_totals(cfg, texts):
    rows = schedule.print_list_rows(cfg, texts)
    config_rows = cfg.session_schedule.print_list
    teams = cfg.session_schedule.teams
    assert [row.file for row in rows] == [f"{row.job}.pdf" for row in config_rows]
    for row, config_row in zip(rows, config_rows):
        assert row.per_team == str(config_row.per_team)
        assert row.facilitator == str(config_row.facilitator)
        assert row.total == str(config_row.per_team * teams + config_row.facilitator)


def test_attack_sheets_are_labelled_with_the_wave_id(cfg, texts):
    rows = {row.file: row for row in schedule.print_list_rows(cfg, texts)}
    prefix = texts.get("sheets.ablauf.print_attack_sheet")
    for wave in cfg.waves:
        assert rows[f"{printmodel.worksheet_job(wave)}.pdf"].label == f"{prefix} {wave.wave_id}"


def test_the_print_list_is_exactly_the_set_of_rendered_jobs(cfg, texts, clues):
    baseline = load_baseline(CONTENT_DIR / BASELINE_FILE)
    rendered = render.render_all(cfg, texts, TEMPLATES, clues=clues, baseline=baseline)
    assert {row.job for row in cfg.session_schedule.print_list} == set(rendered)
    assert {row.file for row in schedule.print_list_rows(cfg, texts)} == {f"{job}.pdf" for job in rendered}


def test_facilitator_documents_print_zero_per_team(cfg, texts):
    for row in schedule.print_list_rows(cfg, texts):
        if row.file.startswith("spielleitung-"):
            assert row.per_team == "0"


def test_a_print_row_without_a_label_stops_the_build(cfg, texts):
    extra = dataclasses.replace(cfg.session_schedule.print_list[0], job="spieler-neu")
    rows = cfg.session_schedule.print_list + (extra,)
    broken = dataclasses.replace(cfg, session_schedule=dataclasses.replace(cfg.session_schedule, print_list=rows))
    with pytest.raises(PrintModelError, match="spieler-neu"):
        schedule.print_list_rows(broken, texts)


# --- page ------------------------------------------------------------------------------------------------------


def test_no_page_without_a_schedule():
    mini = load_config(MINI)
    mini_texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    assert mini.session_schedule is None
    assert schedule.build_schedule_page(mini, mini_texts) is None


def test_the_page_carries_titles_totals_and_every_string(cfg, page):
    assert page.total_value == str(cfg.session_schedule.total_minutes)
    assert page.teams_value == str(cfg.session_schedule.teams)
    assert len(page.rows) == len(cfg.session_schedule.blocks)
    fragments = page.printed_fragments()
    for row in page.rows:
        assert row.label in fragments and row.direction in fragments
    for row in page.print_rows:
        assert row.label in fragments and row.file in fragments
    assert page.title in fragments and page.print_title in fragments
    assert len(fragments) == len(set(fragments))
    assert "" not in fragments


def test_no_schedule_string_names_an_attack(cfg, texts, page):
    ctx = veil.context(cfg, texts, load_content(CONTENT_DIR).terms)
    strings = [
        page.title, page.intro, *page.header, page.total_label, page.print_title, page.print_intro,
        *page.print_header, page.teams_label,
    ]
    strings += [text for row in page.rows for text in (row.label, row.direction)]
    # The file names of the angriff-* rows carry attack ids and are exempt: the page lies in the facilitator-only
    # booklet whose later pages name every attack (T-07-07).
    strings += [row.label for row in page.print_rows]
    for text in strings:
        assert veil.name_hits(text, ctx, audience.PROFILE_NAMES) == [], text


def test_directions_hold_back_the_attack_worksheets(texts):
    for wave_block in ("wave_1", "wave_2", "wave_3"):
        direction = texts.get(f"sheets.ablauf.blocks.{wave_block}.direction")
        assert "Arbeitsblatt" in direction


def test_the_teamheft_is_handed_out_in_the_story_block(cfg, texts):
    label = texts.get("sheets.ablauf.print.spieler-teamheft")
    directions = [
        (block.id, texts.get(f"sheets.ablauf.blocks.{block.id}.direction")) for block in cfg.session_schedule.blocks
    ]
    first = next(block_id for block_id, direction in directions if label in direction)
    assert first == "story_groups"
    story = dict(directions)["story_groups"]
    assert texts.get("sheets.register.title") in story
    # PROT-04 (D-13): the protection-need table comes first, the register second.
    need_title = texts.get("sheets.register.need_title")
    assert need_title in story
    assert story.index(need_title) < story.index(texts.get("sheets.register.title"))
    assert "Schutzziel" in story


def test_the_measures_block_hands_out_the_measure_cards(texts):
    direction = texts.get("sheets.ablauf.blocks.measures_budget.direction")
    assert texts.get("sheets.ablauf.print.spieler-massnahmenkarten") in direction


def test_the_measures_direction_points_to_the_optional_column(texts):
    direction = texts.get("sheets.ablauf.blocks.measures_budget.direction")
    assert texts.get("sheets.register.planning_column") in direction


def test_the_closing_block_directs_the_rueckblick(texts):
    direction = texts.get("sheets.ablauf.blocks.closing.direction")
    assert texts.get("sheets.register.head_review") in direction


# --- key coverage ----------------------------------------------------------------------------------------------


def test_ablauf_is_not_a_pre_wave_sheet():
    assert "ablauf" not in PREWAVE_SHEETS


def test_required_keys_follow_the_config_ids(cfg):
    keys = required_keys(cfg)
    for block in cfg.session_schedule.blocks:
        assert f"sheets.ablauf.blocks.{block.id}.direction" in keys
        assert (f"sheets.ablauf.blocks.{block.id}.label" in keys) == (block.wave is None)
    assert "sheets.ablauf.practice_label" in keys and "sheets.ablauf.print_attack_sheet" in keys
    for row in cfg.session_schedule.print_list:
        assert (f"sheets.ablauf.print.{row.job}" in keys) == (not row.job.startswith("angriff-"))


def test_the_mini_config_requires_no_ablauf_key():
    mini = load_config(MINI)
    assert not [key for key in required_keys(mini) if key.startswith("sheets.ablauf")]
