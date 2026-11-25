"""Debrief question set of the facilitator booklet (FLOW-03, D-08..D-11, D-27).

Numbers (stage minutes, team rows) come from `session_schedule`, words from `sheets.debrief`; the page names no attack
and types no digit. The shared phase-7 number-word lint (`tests/test_texts_number_words.py`) covers the prose.
"""
import dataclasses

import pytest

from planspiel import audience, debrief, fmt, veil
from planspiel.config import load_config
from planspiel.printmodel import PrintModelError
from planspiel.texts import PREWAVE_SHEETS, load_content, load_texts, required_keys
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
STAGE_ORDER = ("reaction", "description", "analysis", "application")


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def texts():
    return load_texts(CONTENT_DIR / "texte.toml")


@pytest.fixture(scope="module")
def page(cfg, texts):
    return debrief.build_debrief_page(cfg, texts)


def _entries(section):
    return len(section.questions) + len(section.prompts)


def test_no_page_without_a_schedule():
    mini = load_config(MINI)
    mini_texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    assert mini.session_schedule is None
    assert debrief.build_debrief_page(mini, mini_texts) is None


def test_the_real_config_builds_a_page(page):
    assert isinstance(page, debrief.DebriefPage)
    assert all(isinstance(section, debrief.DebriefSection) for section in page.stages)


def test_stages_follow_the_config_order_and_take_their_titles_from_the_texts(cfg, texts, page):
    ids = [stage.id for stage in cfg.session_schedule.debrief_stages]
    assert tuple(ids) == STAGE_ORDER
    assert [section.title for section in page.stages] == [
        texts.get(f"sheets.debrief.stages.{stage_id}.title") for stage_id in ids
    ]


def test_every_stage_has_two_to_six_entries_and_twelve_to_sixteen_in_total(page):
    assert all(2 <= _entries(section) <= 6 for section in page.stages)
    assert 12 <= sum(_entries(section) for section in page.stages) <= 16


def _stage(page, stage_id):
    return page.stages[STAGE_ORDER.index(stage_id)]


def test_the_description_recalls_the_register_and_the_chosen_measures(texts, page):
    title = texts.get("sheets.register.title")
    assert any(title in question for question in _stage(page, "description").questions)


def test_the_analysis_follows_the_chain(texts, page):
    questions = _stage(page, "analysis").questions
    review = texts.get("sheets.register.head_review")
    assert any(review in question for question in questions)
    assert "Welches akzeptierte Risiko hat euch getroffen?" in " ".join(questions)
    assert any(
        all(word in question for word in ("Gewichtung", "Vertraulichkeit", "Integrität", "Verfügbarkeit"))
        for question in questions
    )
    # PROT-04 (D-10): the C/I/A question starts from the protection-need table and asks for the main goal.
    need_title = texts.get("sheets.register.need_title")
    head_goal = texts.get("sheets.register.head_goal")
    assert any(
        all(
            word in question
            for word in ("Gewichtung", "Vertraulichkeit", "Integrität", "Verfügbarkeit", need_title, head_goal)
        )
        for question in questions
    )
    assert any(all(word in question for word in ("RoS", "Kosten", "Euro")) for question in questions)


def test_the_application_transfers_to_a_real_risk_register(texts, page):
    title = texts.get("sheets.register.title")
    assert any(title in question for question in _stage(page, "application").questions)


def test_the_debrief_intro_asks_for_the_filled_register(texts, page):
    assert texts.get("sheets.register.title") in page.intro
    assert texts.get("sheets.register.head_review") in page.intro


def test_the_pitch_is_optional_and_has_no_guide_minutes(cfg, texts, page):
    words = texts.subtree("sheets.debrief")
    assert page.pitch_title == words["pitch_title"]
    assert page.pitch_text == words["pitch_text"]
    assert page.pitch_limit_label == words["pitch_limit_label"]
    assert page.pitch_text.startswith("Optional:") and "Warum war unser Budget gut investiert?" not in page.pitch_text
    seconds = cfg.session_schedule.pitch_seconds
    assert page.pitch_limit == f"{fmt.format_number(seconds)} {words['seconds_unit']}"
    assert tuple(stage.id for stage in cfg.session_schedule.debrief_stages) == STAGE_ORDER
    block = next(block for block in cfg.session_schedule.blocks if block.id == "debrief")
    assert page.total_value == f"{block.minutes} {words['minutes_unit']}"


def test_a_config_without_a_pitch_time_has_empty_pitch_fields_and_needs_no_pitch_keys(cfg, texts):
    plain = dataclasses.replace(cfg, session_schedule=dataclasses.replace(cfg.session_schedule, pitch_seconds=None))
    built = debrief.build_debrief_page(plain, texts)
    assert (built.pitch_title, built.pitch_text, built.pitch_limit_label, built.pitch_limit) == ("", "", "", "")
    assert "sheets.debrief.pitch_title" not in required_keys(plain)
    assert "sheets.debrief.pitch_title" in required_keys(cfg)


def test_the_debrief_direction_mentions_the_pitch(texts):
    assert texts.get("sheets.debrief.pitch_title") in texts.get("sheets.ablauf.blocks.debrief.direction")


def test_the_guide_minutes_come_from_config_and_fill_the_debrief_block(cfg, texts, page):
    unit = texts.get("sheets.debrief.minutes_unit")
    stages = cfg.session_schedule.debrief_stages
    assert [section.guide for section in page.stages] == [f"{stage.minutes} {unit}" for stage in stages]
    parsed = [int(section.guide.split()[0]) for section in page.stages]
    block = next(block for block in cfg.session_schedule.blocks if block.id == "debrief")
    assert sum(parsed) == block.minutes
    assert page.total_value == f"{block.minutes} {unit}"


def test_the_data_prompts_sit_on_their_stages(page):
    by_id = dict(zip(STAGE_ORDER, page.stages))
    assert dict(debrief.PROMPT_STAGES) == {"compare": "description", "clues": "analysis", "window": "analysis"}
    assert len(by_id["description"].prompts) == 1
    assert len(by_id["analysis"].prompts) == 2
    assert by_id["reaction"].prompts == () and by_id["application"].prompts == ()


def test_the_compare_prompt_names_the_three_figures(texts):
    prompt = texts.get("sheets.debrief.prompts.compare")
    for figure in ("KZ", "RoS", "Final-Index"):
        assert figure in prompt


def test_the_clue_prompt_points_to_the_clue_matrix_by_its_title(texts, page):
    title = texts.get("sheets.spielleitung.clues_title")
    analysis = page.stages[STAGE_ORDER.index("analysis")]
    tail = f"{texts.get('sheets.debrief.clue_pointer')} {title} {texts.get('sheets.debrief.clue_pointer_end')}"
    pointers = [prompt for prompt in analysis.prompts if prompt.endswith(tail)]
    assert len(pointers) == 1
    assert texts.get("sheets.debrief.prompts.clues") in pointers[0]
    assert pointers[0].endswith("Siehe die Hinweis-Matrix für die Story-Gruppenarbeit am Ende dieses Hefts.")


def test_the_window_prompt_asks_about_the_change_window(texts):
    assert "Change-Fenster" in texts.get("sheets.debrief.prompts.window")


def test_the_compare_table_has_one_row_per_team_and_empty_cells(cfg, texts, page):
    words = texts.subtree("sheets.debrief")
    assert page.compare_header == (
        words["compare_head_team"], words["compare_head_kz"], words["compare_head_ros"],
        words["compare_head_final_index"],
    )
    assert page.compare_rows == tuple(
        f"{words['team_label']} {number}" for number in range(1, cfg.session_schedule.teams + 1)
    )


def test_the_team_rows_follow_the_config_team_count(cfg, texts):
    more = dataclasses.replace(cfg, session_schedule=dataclasses.replace(cfg.session_schedule, teams=4))
    assert len(debrief.build_debrief_page(more, texts).compare_rows) == 4


def test_the_application_stage_asks_transfer_questions_and_carries_no_data_prompt(page):
    application = page.stages[STAGE_ORDER.index("application")]
    assert len(application.questions) >= 2
    assert application.prompts == ()


def test_a_prompt_stage_the_config_lacks_stops_the_build(cfg, texts):
    stages = tuple(stage for stage in cfg.session_schedule.debrief_stages if stage.id != "analysis")
    broken = dataclasses.replace(cfg, session_schedule=dataclasses.replace(cfg.session_schedule, debrief_stages=stages))
    with pytest.raises(PrintModelError, match="analysis"):
        debrief.build_debrief_page(broken, texts)


def test_no_debrief_string_names_an_attack(cfg, texts, page):
    ctx = veil.context(cfg, texts, load_content(CONTENT_DIR).terms)
    assert page.printed_fragments()
    for text in page.printed_fragments():
        assert veil.name_hits(text, ctx, audience.PROFILE_NAMES) == [], text


def test_the_fragments_hold_every_printed_string_once(page):
    fragments = page.printed_fragments()
    assert len(fragments) == len(set(fragments)) and "" not in fragments
    for section in page.stages:
        for text in (section.title, section.guide, *section.questions, *section.prompts):
            assert text in fragments
    for text in (page.title, page.intro, page.compare_title, page.compare_intro, *page.compare_header,
                 *page.compare_rows, page.pitch_title, page.pitch_text, page.pitch_limit_label, page.pitch_limit):
        assert text in fragments


def test_debrief_is_not_a_pre_wave_sheet():
    assert "debrief" not in PREWAVE_SHEETS


def test_required_keys_follow_the_config_stages(cfg):
    keys = required_keys(cfg)
    for stage in cfg.session_schedule.debrief_stages:
        assert f"sheets.debrief.stages.{stage.id}.title" in keys
        assert f"sheets.debrief.stages.{stage.id}.questions" in keys
    for name in debrief.PROMPT_STAGES:
        assert f"sheets.debrief.prompts.{name}" in keys
    assert "sheets.debrief.title" in keys


def test_the_mini_config_requires_no_debrief_key():
    assert not [key for key in required_keys(load_config(MINI)) if key.startswith("sheets.debrief")]
