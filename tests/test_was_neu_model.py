"""The "Was ist neu" sheet model (FLOW-04, D-12..D-15, D-29, D-33).

Rule, flow and material rows are texte prose plus generated numbers; the value rows come from `value_changes` over the
frozen MHP baseline. No TeX is involved; the built PDF is covered by tests/test_was_neu_pdf.py.
"""
import copy
import dataclasses
import re
from fractions import Fraction

import pytest

from planspiel import audience, fmt, review_text, rules, veil
from planspiel.config import load_config
from planspiel.texts import PREWAVE_SHEETS, check_texts, load_content, load_texts, required_keys
from planspiel.was_neu import (
    BASELINE_FILE,
    FLOW_IDS,
    MATERIAL_IDS,
    MAX_VALUE_ROWS,
    RULE_IDS,
    WAS_NEU_JOB,
    RuleRow,
    ValueRow,
    WasNeuSheet,
    build_was_neu_sheet,
    load_baseline,
)
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
YEAR = re.compile(r"(?<![\d.])(?:19|20)\d{2}(?![\d.])")
EXPECTED_RULES = (
    "levelwechsel", "kurswechsel", "downgrade", "init_window", "overspend", "sparprogramm", "ros", "review_boundary",
    "e_target", "rounding", "final_index", "event_order",
)


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
def baseline():
    return load_baseline(CONTENT_DIR / BASELINE_FILE)


@pytest.fixture(scope="module")
def sheet(cfg, texts, baseline):
    return build_was_neu_sheet(cfg, texts, baseline)


def _rule(sheet, rule_id):
    return sheet.rules[RULE_IDS.index(rule_id)]


def _penalty(cfg):
    return cfg.final_events[0].params["overspend_penalty"]


# --- when there is a sheet ---------------------------------------------------------------------------------------


def test_no_sheet_without_a_schedule_or_a_baseline(cfg, texts, baseline):
    assert build_was_neu_sheet(dataclasses.replace(cfg, session_schedule=None), texts, baseline) is None
    assert build_was_neu_sheet(cfg, texts, None) is None
    mini = load_config(MINI)
    mini_texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    assert build_was_neu_sheet(mini, mini_texts, baseline) is None


def test_the_real_inputs_build_the_facilitator_sheet(sheet):
    assert isinstance(sheet, WasNeuSheet)
    assert sheet.job == WAS_NEU_JOB == "spielleitung-was-ist-neu"
    assert audience.audience_of(sheet.job) == audience.FACILITATOR
    assert audience.scan_profile(sheet.job) is None
    assert all(isinstance(row, RuleRow) for row in sheet.rules)
    assert all(isinstance(row, ValueRow) for row in sheet.values)


def test_was_neu_is_not_a_pre_wave_sheet():
    assert "was_neu" not in PREWAVE_SHEETS


# --- rule rows ---------------------------------------------------------------------------------------------------


def test_the_rule_rows_follow_the_rule_ids(texts, sheet):
    assert RULE_IDS == EXPECTED_RULES
    assert len(sheet.rules) == 12
    for rule_id, row in zip(RULE_IDS, sheet.rules):
        assert row.heading == texts.get(f"sheets.was_neu.rules.{rule_id}.heading")
        assert row.text.startswith(texts.get(f"sheets.was_neu.rules.{rule_id}.text"))


def test_the_overspend_row_carries_x_and_the_step_from_the_config(cfg, texts, baseline):
    penalty = _penalty(cfg)
    row = _rule(build_was_neu_sheet(cfg, texts, baseline), "overspend")
    assert f" {penalty['kz_per_step']} KZ je angefangene " in row.text and "−" not in row.text
    assert fmt.format_money(penalty["step"] * 1000) in row.text
    changed = copy.deepcopy(cfg)
    _penalty(changed).update(kz_per_step=7, step=20)
    row = _rule(build_was_neu_sheet(changed, texts, baseline), "overspend")
    assert " 7 KZ je angefangene " in row.text and fmt.format_money(20000) in row.text
    assert f" {penalty['kz_per_step']} KZ je angefangene " not in row.text


def test_the_boundary_row_carries_the_generated_tier_text(cfg, texts, baseline):
    tiers = cfg.final_events[0].params["tiers"]
    row = _rule(build_was_neu_sheet(cfg, texts, baseline), "review_boundary")
    assert review_text.boundary_text(tiers) in row.text
    changed = copy.deepcopy(cfg)
    changed.final_events[0].params["tiers"] = [[0, 0], [30, 9], [60, 18], [90, 27]]
    row = _rule(build_was_neu_sheet(changed, texts, baseline), "review_boundary")
    assert review_text.boundary_text([[0, 0], [30, 9], [60, 18], [90, 27]]) in row.text
    assert review_text.boundary_text(tiers) not in row.text


def test_the_final_index_row_carries_the_weights_from_the_config(cfg, texts, baseline):
    row = _rule(build_was_neu_sheet(cfg, texts, baseline), "final_index")
    assert fmt.format_number(cfg.final_index.weight_ros) in row.text
    changed = dataclasses.replace(cfg, final_index=dataclasses.replace(cfg.final_index, weight_ros=Fraction(12)))
    row = _rule(build_was_neu_sheet(changed, texts, baseline), "final_index")
    assert fmt.format_number(12) in row.text
    assert fmt.format_number(cfg.final_index.weight_ros) not in row.text


def test_the_penalty_parameters_are_those_of_the_rules_module(cfg):
    assert rules.penalty_params(cfg.final_events) == (_penalty(cfg)["kz_per_step"], _penalty(cfg)["step"])


# --- flow and material rows --------------------------------------------------------------------------------------


def test_one_flow_row_per_flow_id_naming_the_debrief_and_the_schedule(cfg, texts, sheet):
    assert FLOW_IDS == ("whiteboard", "welle0", "debrief", "schedule")
    assert len(sheet.flow) == len(FLOW_IDS)
    debrief_row, schedule_row = sheet.flow[2], sheet.flow[3]
    assert texts.get("sheets.debrief.title") in debrief_row
    assert texts.get("sheets.ablauf.title") in schedule_row
    assert fmt.format_number(cfg.session_schedule.total_minutes) in schedule_row


def test_the_schedule_row_generates_the_wave_block_minutes(cfg, texts, baseline):
    minutes = sorted({block.minutes for block in cfg.session_schedule.blocks if block.wave})
    assert minutes == [20, 25]  # D-34: wave 1 is re-budgeted to 25 minutes, waves 2 and 3 keep 20
    row = build_was_neu_sheet(cfg, texts, baseline).flow[3]
    assert all(fmt.format_number(figure) in row for figure in minutes)
    blocks = tuple(
        dataclasses.replace(block, minutes=block.minutes + 5) if block.id == "wave_1" else block
        for block in cfg.session_schedule.blocks
    )
    changed = dataclasses.replace(cfg, session_schedule=dataclasses.replace(cfg.session_schedule, blocks=blocks))
    row = build_was_neu_sheet(changed, texts, baseline).flow[3]
    assert fmt.format_number(minutes[0] + 10) in row and fmt.format_number(minutes[0]) in row


def test_one_material_row_per_material_id_naming_the_clue_matrix(texts, sheet):
    assert MATERIAL_IDS == ("generated", "veil", "clues", "teamheft", "wave_page", "practice")
    assert len(sheet.material) == len(MATERIAL_IDS)
    assert texts.get("sheets.spielleitung.clues_title") in sheet.material[2]


def test_every_material_row_ends_with_a_full_stop_also_after_an_inserted_title(sheet):
    assert all(row.endswith(".") for row in sheet.material), sheet.material


def test_the_teamheft_line_names_the_protection_need(texts):
    # PROT-04 (D-13): the Teamheft line of the sheet names the protection-need table.
    assert texts.get("sheets.register.need_title") in texts.get("sheets.was_neu.material.teamheft")


# --- value rows --------------------------------------------------------------------------------------------------


def _labels(sheet):
    return [row.label for row in sheet.values]


def _find(sheet, *needles):
    found = [row for row in sheet.values if all(needle in row.label for needle in needles)]
    assert len(found) == 1, (needles, _labels(sheet))
    return found[0]


def test_the_budgets_form_one_row_with_old_and_new_per_tier(cfg, texts, sheet):
    row = _find(sheet, texts.get("sheets.was_neu.fields.budget"))
    assert row.old == " / ".join(fmt.format_money(k * 1000) for k in (350, 400, 450))
    assert row.new == " / ".join(fmt.format_money(tier.budget * 1000) for tier in cfg.budget_tiers.values())


def test_the_kz_starts_form_one_row(cfg, texts, sheet):
    row = _find(sheet, texts.get("sheets.was_neu.fields.kz_start"))
    assert row.old == "50 / 42 / 34"
    assert row.new == "39 / 36 / 33"


def test_attack_related_rows_are_labelled_with_the_wave_and_never_with_an_attack_name(cfg, texts, sheet):
    wave_word = texts.get("sheets.was_neu.wave_label")
    ends = [row for row in sheet.values if texts.get("sheets.was_neu.fields.kz_ends") in row.label]
    assert [row.label for row in ends] == [
        f"{texts.get('sheets.was_neu.fields.kz_ends')}, {wave_word} {wave.wave_id}" for wave in cfg.waves
    ]
    first = ends[0]
    assert first.old == f"{fmt.format_signed(-6)} / {fmt.format_signed(10)}"
    assert first.new == f"{fmt.format_signed(-8)} / {fmt.format_signed(8)}"


def test_a_bonus_row_prints_all_bonuses_of_the_wave_once_any_of_them_changed(cfg, texts, sheet):
    wave_word = texts.get("sheets.was_neu.wave_label")
    word = texts.get("sheets.was_neu.fields.bonus")
    wave_two = _find(sheet, word, f"{wave_word} 2")
    members = [bonus.measure for bonus in cfg.waves[1].bonus_measures]
    assert len(members) > 1
    for measure in members:
        assert measure in wave_two.label
    assert len(wave_two.old.split(" / ")) == len(members) == len(wave_two.new.split(" / "))


def test_a_measure_field_forms_one_row_across_the_levels(texts, sheet):
    init = _find(sheet, "M6", texts.get("sheets.was_neu.fields.init"))
    assert init.old == " / ".join(fmt.format_money(k * 1000) for k in (10, 24, 40))
    assert init.new == " / ".join(fmt.format_money(k * 1000) for k in (16, 30, 46))
    cia = _find(sheet, "M7", texts.get("sheets.was_neu.fields.cia"))
    assert "2/3/2" in cia.old and "0/1/0" in cia.new


def test_every_event_with_a_change_forms_one_row(cfg, sheet):
    names = [event.name for events in cfg.events.values() for event in events]
    for name in ("OEM-Audit", "Kritische Schwachstelle im System", "Exzellenz-Bonus", "Nervige Authentifizierung"):
        assert name in names
        assert len([row for row in sheet.values if row.label.startswith(name)]) == 1
    for name in ("Sparprogramm", "Operative Unterstützung", "Kurswechsel"):
        assert not [row for row in sheet.values if row.label.startswith(name)]


def test_the_budget_review_rows_show_tiers_boundary_and_overspend(cfg, texts, sheet):
    penalty = _penalty(cfg)
    overspend = _find(sheet, texts.get("sheets.was_neu.fields.overspend"))
    assert fmt.format_signed(-15) in overspend.old
    assert fmt.format_signed(-penalty["kz_per_step"]) in overspend.new
    assert fmt.format_money(penalty["step"] * 1000) in overspend.new
    boundary = _find(sheet, texts.get("sheets.was_neu.fields.boundary"))
    assert boundary.old != boundary.new
    tiers = _find(sheet, texts.get("sheets.was_neu.fields.review_tiers"))
    assert tiers.old != tiers.new


def test_meaning_changed_rows_are_flagged_and_the_sheet_explains_the_flag(texts, sheet):
    flagged = [row for row in sheet.values if row.flag]
    assert len(flagged) == 3
    mark = texts.get("sheets.was_neu.flag_mark")
    assert all(row.flag == mark for row in flagged)
    assert sheet.flag_note == texts.get("sheets.was_neu.flag_note")
    for field in ("boundary", "overspend"):
        word = texts.get(f"sheets.was_neu.fields.{field}")
        assert any(word in row.label for row in flagged), field
    assert any(row.label.startswith("Exzellenz-Bonus") for row in flagged)


def test_unchanged_groups_have_no_value_row(texts, sheet):
    for field in ("base_severity", "s_unit", "mitigation_cap", "allow_recovery", "recovery", "cia_impact", "weights"):
        word = texts.get(f"sheets.was_neu.fields.{field}")
        assert not [row for row in sheet.values if word in row.label], field
    for name in ("Sparprogramm", "Operative Unterstützung"):
        assert not [row for row in sheet.values if name in row.label]


def test_the_real_baseline_fits_under_the_row_cap(sheet):
    assert 0 < len(sheet.values) <= MAX_VALUE_ROWS
    assert sheet.values_more == ""


# --- D-15: the value table shrinks first -------------------------------------------------------------------------


def _every_measure_level_differs(baseline):
    changed = copy.deepcopy(baseline)
    for measure in changed.measures.values():
        for level in measure["levels"].values():
            level["init"] += 1
            level["opex"] += 1
            level["recovery"] += 1
            level["cia"] = {key: value + 1 for key, value in level["cia"].items()}
    return changed


def test_a_flood_of_changes_caps_the_value_rows_and_keeps_every_rule_row(cfg, texts, baseline):
    sheet = build_was_neu_sheet(cfg, texts, _every_measure_level_differs(baseline))
    assert len(sheet.values) == MAX_VALUE_ROWS
    assert sheet.values_more == texts.get("sheets.was_neu.values_more")
    assert len(sheet.rules) == len(RULE_IDS) and len(sheet.flow) == len(FLOW_IDS)
    assert len(sheet.material) == len(MATERIAL_IDS)
    labels = _labels(sheet)
    budget = texts.get("sheets.was_neu.fields.budget")
    assert any(budget in label for label in labels)
    assert any(texts.get("sheets.was_neu.fields.overspend") in label for label in labels)
    assert any(label.startswith("Exzellenz-Bonus") for label in labels)
    assert len([row for row in sheet.values if row.flag]) == 3


def test_the_cap_keeps_the_display_order_of_the_groups(cfg, texts, baseline):
    full = build_was_neu_sheet(cfg, texts, baseline)
    capped = build_was_neu_sheet(cfg, texts, _every_measure_level_differs(baseline))
    kept = [row.label for row in capped.values if row.label in _labels(full)]
    assert kept == [label for label in _labels(full) if label in kept]


# --- printed strings ----------------------------------------------------------------------------------------------


def test_no_printed_string_names_an_attack_or_a_year(cfg, texts, content, sheet):
    ctx = veil.context(cfg, texts, content.terms)
    fragments = sheet.printed_fragments()
    assert fragments
    for text in fragments:
        assert veil.name_hits(text, ctx, audience.PROFILE_NAMES) == [], text
        assert not YEAR.search(text), text


def test_the_fragments_hold_every_printed_string_once(sheet):
    fragments = sheet.printed_fragments()
    assert len(fragments) == len(set(fragments)) and "" not in fragments
    assert WAS_NEU_JOB not in fragments
    for row in sheet.rules:
        assert row.heading in fragments and row.text in fragments
    for text in (*sheet.flow, *sheet.material, sheet.title, sheet.notice, sheet.intro, *sheet.values_header):
        assert text in fragments
    for row in sheet.values:
        assert row.label in fragments and row.old in fragments and row.new in fragments


# --- texts ----------------------------------------------------------------------------------------------------


def test_the_texts_cover_the_required_keys_and_pass_the_text_checks(cfg, content):
    required = required_keys(cfg)
    for rule_id in RULE_IDS:
        assert f"sheets.was_neu.rules.{rule_id}.heading" in required
        assert f"sheets.was_neu.rules.{rule_id}.text" in required
    for flow_id in FLOW_IDS:
        assert f"sheets.was_neu.flow.{flow_id}" in required
    for material_id in MATERIAL_IDS:
        assert f"sheets.was_neu.material.{material_id}" in required
    assert [issue for issue in check_texts(cfg, content) if issue.level == "error"] == []


def test_the_mini_config_needs_no_was_neu_texts():
    mini = load_config(MINI)
    assert not [key for key in required_keys(mini) if key.startswith("sheets.was_neu")]
