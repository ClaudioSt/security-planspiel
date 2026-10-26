"""Wave explainer "So funktioniert eine Welle": model, vocabulary shared with worksheet and tracking sheet, veil (PRINT-09).

The page explains the order of a wave with symbols only (D-11, D-26): no wave weight, threshold, cap or attack name.
The recovery table comes from `rules.recovery_table`, independent of any attack. No TeX is involved in the model
tests; the template and the built PDF are covered below and in tests/test_wave_page_pdf.py.
"""
import dataclasses
import re
from fractions import Fraction

import pytest

from planspiel import audience, fmt, rules, veil
from planspiel.cards import printed_strings
from planspiel.config import load_config
from planspiel.eventtext import EFFECT_KINDS
from planspiel.rules import RecoveryRow, WorksheetInvariantError, recovery_table, worksheet_constants
from planspiel.texts import PREWAVE_SHEETS, PreAttackView, load_content
from planspiel.wave_page import WAVE_PAGE_JOB, FlowStep, WavePage, build_wave_page
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
TEMPLATES = REPO_ROOT / "print" / "templates"
TEMPLATE = TEMPLATES / "welle.tex.j2"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]
STEP_KEYS = ("events", "cia", "e_value", "bonus", "reduction", "cases", "recovery", "wave_kz", "clamp", "window")
WORKSHEET_STEPS = ("cia", "e_value", "bonus", "reduction", "cases", "recovery", "wave_kz")
PLAIN_VARIABLE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\[\]'\"]*$")
VARIABLE = re.compile(r"\\VAR\{([^}]*)\}")


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    cfg = load_config(config_path)
    content = load_content(content_dir)
    return cfg, content, build_wave_page(cfg, content.texts)


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    content = load_content(CONTENT_DIR)
    return cfg, content, build_wave_page(cfg, content.texts)


def _text(value) -> str:
    return "\n".join(printed_strings(value))


# ---- rules.recovery_table -----------------------------------------------------------------------------------------


def _with_recovery_on(cfg, measure_id):
    measure = cfg.measures[measure_id]
    levels = dict(measure.levels)
    levels[1] = dataclasses.replace(levels[1], recovery=Fraction(1, 10))
    return dataclasses.replace(cfg, measures={**cfg.measures, measure_id: dataclasses.replace(measure, levels=levels)})


@pytest.mark.parametrize("config_path", [MINI, CONFIG_PATH], ids=["mini", "real"])
def test_recovery_table_returns_the_one_carrier_with_a_row_per_level(config_path):
    cfg = load_config(config_path)
    measure_id, rows = recovery_table(cfg)
    assert measure_id == "M4"
    levels = cfg.measures["M4"].levels
    assert [row.level for row in rows] == sorted(levels)
    assert rows == tuple(RecoveryRow(level, Fraction(levels[level].recovery)) for level in sorted(levels))
    assert rows[0].factor == 0


def test_recovery_table_does_not_depend_on_any_attack_or_wave():
    cfg = load_config(CONFIG_PATH)
    broken = dataclasses.replace(cfg, waves=[], attacks={})
    assert recovery_table(broken) == recovery_table(cfg)


def test_recovery_table_refuses_a_second_carrier():
    cfg = _with_recovery_on(load_config(CONFIG_PATH), "M1")
    with pytest.raises(WorksheetInvariantError, match="Recovery"):
        recovery_table(cfg)


def test_recovery_table_without_a_carrier_is_empty():
    cfg = load_config(CONFIG_PATH)
    measures = {}
    for measure_id, measure in cfg.measures.items():
        levels = {
            level: dataclasses.replace(data, recovery=Fraction(0)) for level, data in measure.levels.items()
        }
        measures[measure_id] = dataclasses.replace(measure, levels=levels)
    assert recovery_table(dataclasses.replace(cfg, measures=measures)) == (None, ())


def test_recovery_carriers_are_shared_by_the_worksheet_derivation():
    cfg = load_config(CONFIG_PATH)
    assert rules.recovery_carriers(cfg.measures) == ("M4",)
    broken = _with_recovery_on(cfg, "M1")
    assert rules.recovery_carriers(broken.measures) == ("M1", "M4")
    # the worksheet keeps raising only for an attack that allows recovery
    with pytest.raises(WorksheetInvariantError):
        worksheet_constants(broken, broken.waves[0])
    assert worksheet_constants(broken, broken.waves[2]).recovery_rows == ()


# ---- the page model -----------------------------------------------------------------------------------------------


def test_the_job_is_a_prewave_job_with_the_story_profile():
    assert WAVE_PAGE_JOB == "spieler-so-funktioniert-eine-welle"
    assert audience.audience_of(WAVE_PAGE_JOB) == audience.PREWAVE
    assert audience.scan_profile(WAVE_PAGE_JOB) == audience.PROFILE_STORY


def test_the_page_is_a_frozen_wave_page_with_flow_steps(loaded):
    _, _, page = loaded
    assert isinstance(page, WavePage) and page.job == WAVE_PAGE_JOB
    assert all(isinstance(step, FlowStep) for step in page.steps)
    with pytest.raises(dataclasses.FrozenInstanceError):
        page.title = "x"  # type: ignore[misc]


def test_the_steps_follow_the_wave_order(loaded):
    _, _, page = loaded
    assert tuple(step.key for step in page.steps) == STEP_KEYS
    for step in page.steps:
        assert step.heading and step.text


def test_the_attack_step_headings_are_the_worksheet_headings_in_the_worksheet_words(loaded):
    cfg, content, page = loaded
    angriff = PreAttackView(cfg, content.texts).sheet("angriff")
    by_key = {step.key: step for step in page.steps}
    for key in WORKSHEET_STEPS:
        assert by_key[key].heading == angriff[f"step_{key}"], key


def test_the_clamp_and_window_steps_use_the_tracking_sheet_labels(loaded):
    cfg, content, page = loaded
    tracking = PreAttackView(cfg, content.texts).sheet("tracking")
    by_key = {step.key: step for step in page.steps}
    assert by_key["clamp"].heading == tracking["row_kz_after"]
    assert tracking["window_title"].startswith(by_key["window"].heading)
    assert tracking["never_refund"] in page.window_text
    assert page.window_text == by_key["window"].text


def test_the_events_heading_is_the_label_events(loaded):
    cfg, content, page = loaded
    assert page.steps[0].heading == PreAttackView(cfg, content.texts).sheet("labels")["events"]


def test_the_reduction_step_introduces_gr_as_gesamtreduktion(loaded):
    cfg, content, page = loaded
    view = PreAttackView(cfg, content.texts)
    words, labels = view.sheet("angriff"), view.sheet("labels")
    reduction = next(step for step in page.steps if step.key == "reduction")
    assert f"{labels['total_reduction']} ({words['label_gr']})" in reduction.text
    assert labels["e_value"] in reduction.text and labels["total_bonus"] in reduction.text


def test_the_e_value_step_names_only_symbols(loaded):
    cfg, content, page = loaded
    formula = PreAttackView(cfg, content.texts).sheet("karten")["legend_formula"]
    e_value = next(step for step in page.steps if step.key == "e_value")
    assert formula in e_value.text


def test_the_cases_step_states_the_three_cases_in_words(loaded):
    cfg, content, page = loaded
    view = PreAttackView(cfg, content.texts)
    words, labels = view.sheet("angriff"), view.sheet("labels")
    cases = next(step for step in page.steps if step.key == "cases")
    for number in (1, 2, 3):
        assert f"{labels['case']} {number}" in cases.text
    for word in (words["label_threshold"], words["label_cap"], words["label_upper"]):
        assert word in cases.text


def test_the_rounding_text_holds_the_allowlisted_wording_and_the_clamp_text_the_bounds(loaded):
    cfg, content, page = loaded
    view = PreAttackView(cfg, content.texts)
    assert view.sheet("angriff")["wave_kz_rounding"] in page.rounding_text
    assert str(rules.KZ_MIN) in page.clamp_text and str(rules.KZ_MAX) in page.clamp_text
    tracking = view.sheet("tracking")
    assert page.clamp_text == f"{tracking['clamp_lead']} {rules.KZ_MIN} {tracking['clamp_to']} {rules.KZ_MAX}"
    by_key = {step.key: step for step in page.steps}
    assert page.rounding_text in by_key["wave_kz"].text
    assert page.clamp_text in by_key["clamp"].text


def test_the_diagram_has_one_label_per_step_in_step_order(loaded):
    _, _, page = loaded
    assert page.diagram_labels == tuple(step.heading for step in page.steps)
    assert len(page.diagram_labels) == 10


def test_the_effects_table_names_what_attacks_and_events_affect(loaded):
    cfg, content, page = loaded
    assert len(page.effects_header) == 2
    assert page.attack_effects and page.event_effects
    kinds = {kind for kind in EFFECT_KINDS.values() if kind not in ("window", "review")}
    assert len(page.event_effects) == len(kinds)
    words = PreAttackView(cfg, content.texts).sheet("welle")
    assert page.attack_effects == (words["effect_damage"], words["effect_kz"])
    assert set(page.event_effects) == {words["effect_kz"], words["effect_budget"], words["effect_opex"]}
    rows = page.effect_rows()
    assert len(rows) == max(len(page.attack_effects), len(page.event_effects))
    assert [left for left, _ in rows if left] == list(page.attack_effects)
    assert [right for _, right in rows if right] == list(page.event_effects)


def test_the_ros_note_separates_own_costs_from_event_effects(loaded):
    cfg, content, page = loaded
    assert page.ros_note == PreAttackView(cfg, content.texts).sheet("welle")["ros_note"]
    assert "RoS" in page.ros_note


def test_the_recovery_section_comes_from_backup_recovery_and_the_generated_table(loaded):
    cfg, content, page = loaded
    view = PreAttackView(cfg, content.texts)
    backup = view.sheet("backup_recovery")
    assert page.recovery_title == backup["title"]
    assert page.recovery_subtitle == backup["subtitle"]
    assert page.recovery_narrative == backup["narrative"]
    measure_id, rows = recovery_table(cfg)
    assert page.recovery_measure_label == f"{measure_id} – {cfg.measures[measure_id].name}"
    assert page.recovery_rows == tuple(
        (str(row.level), backup["level_labels"][str(row.level)], fmt.format_percent(row.factor)) for row in rows
    )
    assert [row[0] for row in page.recovery_rows] == ["0", "1", "2", "3"]


def test_the_real_recovery_measure_label_has_the_card_title_form(real):
    assert real[2].recovery_measure_label == "M4 – Backup & Disaster Recovery"


def test_the_recovery_section_names_no_wave(loaded):
    cfg, content, page = loaded
    section = "\n".join(
        (page.recovery_title, page.recovery_subtitle, page.recovery_narrative, page.recovery_measure_label,
         *("\n".join(row) for row in page.recovery_rows))
    )
    assert not re.search(r"Welle\s*\d", section)
    recovery_step = next(step for step in page.steps if step.key == "recovery")
    assert not re.search(r"Welle\s*\d", recovery_step.text)


# ---- the veil -----------------------------------------------------------------------------------------------------


def test_no_wave_weight_triple_or_symbol_value_is_on_the_page(loaded):
    cfg, content, page = loaded
    ctx = veil.context(cfg, content.texts, content.terms)
    text = _text(page)
    assert veil.weight_hits(text, ctx.signatures) == []
    assert veil.weight_symbol_hits(text) == []
    assert veil.weight_hits(text.replace("\n", " "), ctx.signatures) == []


def test_no_attack_name_or_giveaway_term_is_on_the_page(loaded):
    cfg, content, page = loaded
    ctx = veil.context(cfg, content.texts, content.terms)
    assert veil.name_hits(_text(page), ctx, audience.PROFILE_STORY) == []
    assert veil.name_hits(_text(page), ctx, audience.PROFILE_STORY, squashed=True) == []


def test_the_only_digits_are_case_numbers_the_measure_id_the_clamp_bounds_levels_factors_and_the_rounding_rule(loaded):
    cfg, content, page = loaded
    words = PreAttackView(cfg, content.texts).sheet("labels")
    allowed = [
        page.clamp_text,
        page.recovery_measure_label,
        *("\n".join(row) for row in page.recovery_rows),
        *(f"{words['case']} {number}" for number in (1, 2, 3)),
        PreAttackView(cfg, content.texts).sheet("angriff")["wave_kz_rounding"],  # the allowlisted ",5"
    ]
    remaining = _text(page)
    # the allowed strings may be a whole printed string or part of one, so remove them as substrings
    for text in sorted(allowed, key=len, reverse=True):
        for part in text.split("\n"):
            remaining = remaining.replace(part, "")
    assert not re.search(r"\d", remaining), remaining


def test_the_page_prints_no_threshold_or_cap_value_next_to_the_words(real):
    cfg, content, page = real
    text = _text(page)
    for wave in cfg.waves:
        constants = worksheet_constants(cfg, wave)
        for value in (constants.lower, constants.reduction_cap, constants.upper):
            pattern = rf"(Schwelle|Kappung|Obergrenze)[^\n]{{0,12}}\b{value}\b"
            assert not re.search(pattern, text), (wave.wave_id, value)


def test_wave_page_is_registered_as_a_prewave_model_module():
    from tests.test_veil_models import PREWAVE_MODULES

    assert "wave_page.py" in PREWAVE_MODULES


def test_the_page_fragments_hold_every_printed_string_but_the_job_name(loaded):
    _, _, page = loaded
    fragments = page.printed_fragments()
    assert page.clamp_text in fragments
    assert page.job not in fragments
    assert len(fragments) == len(set(fragments))
    assert set(fragments) == {text for text in printed_strings(page) if text and text != page.job}


def test_prewave_sheets_now_hold_angriff_and_welle():
    assert "angriff" in PREWAVE_SHEETS and "welle" in PREWAVE_SHEETS
