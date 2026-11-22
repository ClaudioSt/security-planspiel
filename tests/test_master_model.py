"""Facilitator master sheet model: parameters, check rows, event schedule, answer keys, clue matrix (PRINT-10, ROADMAP SC4).

Every answer-key value equals `rules.path_trace` on the reference paths pinned in 05-14, is replayed independently from
the worksheet fields by tests/support/worksheet_replay.py, and is pinned in tests/golden/answer_keys.json. The numbers
are formatted here with `fmt` again (not through the model), so a drift between model and rules shows up.
The business-impact cheat sheet (RISK-05, D-05, D-06, D-22) is a page of the same booklet and is tested here too.
"""
import dataclasses
import json
from fractions import Fraction

import pytest

from planspiel import audience, cheatsheet, eventtext, fmt, master, practice, refpaths, risk, rules, veil
from planspiel.config import load_config
from planspiel.printmodel import PrintModelError, build_attack_sheet
from planspiel.rounding import round_half_away_frac
from planspiel.texts import (
    PREWAVE_SHEETS,
    SHEET_KEYS,
    FacilitatorView,
    RevealView,
    check_coverage,
    load_clues,
    load_content,
    load_texts,
    required_keys,
)
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT
from tests.support.golden import check_golden
from tests.support.worksheet_replay import replay_steps
from tests.test_texts_number_words import PHASE7_PREFIXES

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"
MINUS, TIMES, DASH = fmt.MINUS, fmt.TIMES, "–"


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
def sheet(cfg, texts, clues):
    return master.build_master_sheet(cfg, texts, clues)


@pytest.fixture(scope="module")
def traces(cfg):
    return {name: rules.path_trace(cfg, name, refpaths.reference_path(cfg, name)) for name in cfg.budget_tiers}


def _modified(tmp_path, change):
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    change(raw)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return load_config(path)


def master_text(name):
    return load_texts(CONTENT_DIR / "texte.toml").get(f"sheets.spielleitung.{name}")


def _signed_approx(value) -> str:
    text = fmt.format_approx(value)
    if not text.startswith("≈"):
        return fmt.format_signed(value)
    number = text[2:]
    return f"≈ {number}" if number.startswith(MINUS) else f"≈ +{number}"


def _selection_text(selection) -> str:
    return ", ".join(f"{measure_id} L{level}" for measure_id, level in selection.items() if level > 0)


def _row(rows, key):
    return next(row for row in rows if row.key == key)


# ---- the job, the guard for configs without reference plans ----------------------------------------------------


def test_the_job_is_a_facilitator_document():
    assert master.MASTER_JOB == "spielleitung-uebersicht"
    assert audience.audience_of(master.MASTER_JOB) == audience.FACILITATOR
    assert audience.scan_profile(master.MASTER_JOB) is None


def test_a_config_without_reference_plans_gives_no_sheet():
    mini = load_config(MINI)
    mini_texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    assert mini.reference_plans == {}
    assert master.build_master_sheet(mini, mini_texts, load_clues(MINI_CONTENT_DIR / "clues.toml")) is None


def test_the_sheet_has_one_section_per_wave_and_one_result_per_tier(sheet, cfg):
    assert [section.wave_id for section in sheet.waves] == [wave.wave_id for wave in cfg.waves]
    assert [result.tier for result in sheet.tiers] == [name.capitalize() for name in cfg.budget_tiers]
    assert sheet.waves[0].title == RevealView(cfg, load_texts(CONTENT_DIR / "texte.toml")).attack_title(cfg.waves[0])


# ---- texts ------------------------------------------------------------------------------------------------------


def test_the_spielleitung_texts_are_required_keys_and_digit_free(cfg, texts):
    keys = [key for key in SHEET_KEYS if key.startswith("sheets.spielleitung.")]
    assert "sheets.spielleitung.final_index_weight" in keys
    assert "sheets.spielleitung.clue_head_measures" in keys
    assert "sheets.spielleitung.final_index_provisional" not in keys
    assert set(keys) <= required_keys(cfg)
    assert [issue for issue in check_coverage(cfg, texts) if issue.path.startswith("sheets.spielleitung")] == []
    for key, text in texts.strings("sheets.spielleitung"):
        assert not any(char.isnumeric() for char in text), key


def test_the_mini_texte_carries_the_same_keys():
    mini_texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    for key in SHEET_KEYS:
        assert mini_texts.has(key), key


def test_the_master_sheet_is_not_a_pre_wave_sheet():
    from planspiel.texts import PREWAVE_SHEETS

    assert "spielleitung" not in PREWAVE_SHEETS


# ---- parameters ---------------------------------------------------------------------------------------------------


def test_parameters_equal_the_worksheet_constants(sheet, cfg, texts):
    angriff = RevealView(cfg, texts).sheet("angriff")
    for section, wave in zip(sheet.waves, cfg.waves):
        constants = rules.worksheet_constants(cfg, wave)
        values = dict(section.parameters.rows)
        weights = " / ".join(fmt.format_number(weight) for weight in (constants.w_c, constants.w_i, constants.w_a))
        assert values[texts.get("sheets.spielleitung.param_weights")] == weights
        assert values[angriff["label_threshold"]] == fmt.format_number(constants.lower)
        assert values[angriff["label_cap"]] == fmt.format_number(constants.reduction_cap)
        assert values[angriff["label_upper"]] == fmt.format_number(constants.upper)
        assert values[texts.get("sheets.spielleitung.param_unit")] == fmt.format_money(constants.unit_eur)
        slope = values[texts.get("sheets.spielleitung.param_slope")]
        assert slope.startswith(fmt.format_factor(constants.slope))
        assert ("≈" in slope) == (not fmt.terminates(constants.slope))
        if not fmt.terminates(constants.slope):
            assert fmt.format_approx(constants.slope) in slope
        assert values[texts.get("sheets.spielleitung.param_kz_full_damage")] == fmt.format_signed(constants.kz_case_1)
        assert values[texts.get("sheets.spielleitung.param_kz_full_defence")] == fmt.format_signed(constants.kz_case_2)
        recovery = values[texts.get("sheets.spielleitung.param_recovery")]
        if constants.with_recovery:
            assert recovery.startswith(texts.get("sheets.spielleitung.recovery_allowed"))
            assert constants.recovery_measure in recovery
        else:
            assert recovery == texts.get("sheets.spielleitung.recovery_not_allowed")


def test_every_slope_of_the_tuned_config_is_a_one_decimal_factor_without_approximation(sheet):
    for section in sheet.waves:
        slope = dict(section.parameters.rows)[master_text("param_slope")]
        assert "≈" not in slope and "÷" not in slope, slope


def test_the_bonus_table_has_the_reasons_of_the_revealed_view(sheet, cfg, texts):
    view = RevealView(cfg, texts)
    for section, wave in zip(sheet.waves, cfg.waves):
        reasons = view.attack(wave.attack_id)["bonus_reasons"]
        expected = tuple(
            (f"{bm.measure} {DASH} {cfg.measures[bm.measure].name}", str(bm.min_level), fmt.format_signed(bm.bonus), reasons[bm.measure])
            for bm in wave.bonus_measures
        )
        assert section.parameters.bonus_rows == expected


# ---- check rows ---------------------------------------------------------------------------------------------------


def test_the_check_cases_name_the_bounds_damage_and_kz(sheet, cfg):
    for section, wave in zip(sheet.waves, cfg.waves):
        constants = rules.worksheet_constants(cfg, wave)
        one, two, three = section.checks.case_rows
        assert fmt.format_number(constants.lower) in one[0] and "≤" in one[0]
        assert fmt.format_number(constants.upper) in two[0] and "≥" in two[0]
        assert fmt.format_number(constants.lower) in three[0] and fmt.format_number(constants.upper) in three[0]
        assert one[1] == fmt.format_money(constants.case_1_damage_eur)
        assert one[2] == fmt.format_signed(constants.kz_case_1)
        assert two[1] == fmt.format_money(constants.case_2_damage_eur)
        assert two[2] == fmt.format_signed(constants.kz_case_2)
        assert fmt.format_money(constants.unit_eur) in three[1]
        assert fmt.format_number(constants.upper) in three[1]


def test_the_check_table_covers_every_whole_gr_step_and_equals_the_replay(sheet, cfg, texts):
    for section, wave in zip(sheet.waves, cfg.waves):
        constants = rules.worksheet_constants(cfg, wave)
        printed = build_attack_sheet(cfg, texts, wave)
        steps = range(constants.lower + 1, constants.upper)
        assert [row[0] for row in section.checks.table_rows] == [fmt.format_number(step) for step in steps]
        for row, step in zip(section.checks.table_rows, steps):
            result = replay_steps(printed, Fraction(step), {}, 0)
            assert result.case == 3
            assert row[1] == fmt.format_money(result.damage_before_eur)
            assert row[2] == _signed_approx(result.kz_attack), (wave.wave_id, step)
            assert row[1] == fmt.format_money((constants.upper - step) * constants.unit_eur)


def test_no_printed_string_of_the_master_sheet_contains_an_approximation_sign(sheet):
    assert [fragment for fragment in sheet.printed_fragments() if "≈" in fragment] == []
    assert not hasattr(sheet, "approx_hint")


def test_no_wave_shows_approximations_in_its_check_table(sheet):
    flags = [any("≈" in cell for row in section.checks.table_rows for cell in row) for section in sheet.waves]
    assert flags == [False, False, False]


# ---- event schedule -----------------------------------------------------------------------------------------------


def test_the_event_schedule_follows_the_config_and_the_effect_rows(sheet, cfg, texts):
    kinds = {
        "window": "kind_window", "external_opex": "kind_external_opex", "external_budget": "kind_external_budget",
        "kz": "kind_kz", "review": "kind_review",
    }
    for section, wave in zip(sheet.waves, cfg.waves):
        events = cfg.events.get(wave.wave_id, [])
        assert [row.name for row in section.events] == [event.name for event in events]
        for row, event in zip(section.events, events):
            effect = eventtext.effect_rows(event, cfg, texts)
            assert row.kind == texts.get(f"sheets.spielleitung.{kinds[effect.kind]}")
            assert row.heading == (effect.heading or "")
            assert row.lines == tuple(line.text for line in effect.rows)
    assert sum(len(section.events) for section in sheet.waves) == sum(len(events) for events in cfg.events.values())


# ---- answer keys --------------------------------------------------------------------------------------------------


def _expected_keys(cfg, wave, trace_wave) -> dict:
    constants = rules.worksheet_constants(cfg, wave)
    marks = ", ".join(
        f"{row.measure} {TIMES if row.measure in trace_wave.bonus_met else DASH}" for row in constants.bonus_rows
    )
    return {
        "selection": _selection_text(trace_wave.selection),
        "cia": " / ".join(fmt.format_number(trace_wave.cia[key]) for key in "cia"),
        "e_value": fmt.format_approx(trace_wave.e_value),
        "bonus": f"{fmt.format_number(trace_wave.bonus_reduction)} ({marks})",
        "gr": fmt.format_approx(trace_wave.gesamtreduktion),
        "case": str(trace_wave.case),
        "damage_before": fmt.format_money(trace_wave.damage_before_eur),
        "recovery": fmt.format_percent(trace_wave.recovery_factor) if constants.with_recovery else DASH,
        "damage_after": fmt.format_money(trace_wave.damage_eur),
        "kz_attack": _signed_approx(trace_wave.kz_attack),
        "kz_event": fmt.format_signed(trace_wave.kz_event),
        "kz_exact": _signed_approx(trace_wave.kz_change_exact),
        "kz_change": fmt.format_signed(trace_wave.kz_change),
        "kz_before": str(trace_wave.kz_before),
        "kz_unclamped": str(trace_wave.kz_unclamped),
        "kz_after": str(trace_wave.kz_after),
        "own_opex": fmt.format_money(trace_wave.own_opex_k * 1000),
        "window_cost": fmt.format_money(trace_wave.window_cost_k * 1000),
        "external_budget": f"{fmt.format_signed(trace_wave.event_budget_k * 1000)} €",
        "external_opex": f"{fmt.format_signed(trace_wave.event_opex_k * 1000)} €",
        "remaining": fmt.format_money(trace_wave.remaining_k * 1000),
    }


def test_the_key_rows_come_in_calculation_order(sheet):
    assert tuple(row.key for row in sheet.waves[0].key_rows) == master.KEY_ROW_IDS
    assert master.KEY_ROW_IDS.index("gr") < master.KEY_ROW_IDS.index("case") < master.KEY_ROW_IDS.index("damage_before")
    assert master.KEY_ROW_IDS.index("kz_attack") < master.KEY_ROW_IDS.index("kz_change") < master.KEY_ROW_IDS.index("kz_after")


def test_every_answer_key_value_equals_the_path_trace(sheet, cfg, traces):
    tiers = list(cfg.budget_tiers)
    for index, (section, wave) in enumerate(zip(sheet.waves, cfg.waves)):
        assert section.key_header[1:] == tuple(name.capitalize() for name in tiers)
        for position, name in enumerate(tiers):
            expected = _expected_keys(cfg, wave, traces[name].waves[index])
            for key, value in expected.items():
                assert _row(section.key_rows, key).values[position] == value, (wave.wave_id, name, key)


def test_the_keys_follow_the_pinned_legal_paths_not_the_static_plan(sheet, cfg, traces):
    for name, trace in traces.items():
        path = refpaths.reference_path(cfg, name)
        assert path.windows and path.windows[0].swap is not None
        assert refpaths.voluntary_moves(cfg, path)
    medium = list(cfg.budget_tiers).index("medium")
    selections = [_row(section.key_rows, "selection").values[medium] for section in sheet.waves]
    assert selections[0] != selections[1]  # the Kurswechsel swap changes the selection after wave one


def test_each_wave_key_equals_the_independent_worksheet_replay(sheet, cfg, texts, traces):
    for index, (section, wave) in enumerate(zip(sheet.waves, cfg.waves)):
        printed = build_attack_sheet(cfg, texts, wave)
        for position, name in enumerate(cfg.budget_tiers):
            trace_wave = traces[name].waves[index]
            result = replay_steps(printed, trace_wave.e_value, trace_wave.selection, trace_wave.kz_event)
            assert _row(section.key_rows, "gr").values[position] == fmt.format_approx(result.gr)
            assert _row(section.key_rows, "case").values[position] == str(result.case)
            assert _row(section.key_rows, "damage_before").values[position] == fmt.format_money(result.damage_before_eur)
            assert _row(section.key_rows, "damage_after").values[position] == fmt.format_money(result.damage_eur)
            assert _row(section.key_rows, "kz_attack").values[position] == _signed_approx(result.kz_attack)
            assert _row(section.key_rows, "kz_change").values[position] == fmt.format_signed(result.change)


def test_the_pinned_paths_touch_the_mechanics_the_keys_teach(sheet):
    cases = {value for section in sheet.waves for value in _row(section.key_rows, "case").values}
    assert cases == {"1", "2", "3"}
    recoveries = {value for section in sheet.waves for value in _row(section.key_rows, "recovery").values}
    assert DASH in recoveries and len(recoveries) > 1


# ---- the reference paths on the overview ---------------------------------------------------------------------------


def test_the_overview_lists_the_start_and_the_windows_of_every_pinned_path(sheet, cfg):
    assert [line.tier for line in sheet.paths] == [name.capitalize() for name in cfg.budget_tiers]
    for line, name in zip(sheet.paths, cfg.budget_tiers):
        path = refpaths.reference_path(cfg, name)
        assert line.start == _selection_text(path.start)
        assert len(line.windows) == len(path.windows)
        for text, window in zip(line.windows, path.windows):
            assert _selection_text(window.selection) in text
            if window.swap is not None:
                assert window.swap[0] in text and window.swap[1] in text


# ---- Budget Review and the final table ----------------------------------------------------------------------------


def test_the_budget_review_section_equals_the_event_rows(sheet, cfg, texts):
    event = cfg.final_events[0]
    effect = eventtext.effect_rows(event, cfg, texts)
    assert sheet.review.tier_heading == effect.heading
    assert sheet.review.tier_lines == tuple(row.text for row in effect.rows)
    kz_per_step, step_k = rules.penalty_params(cfg.final_events)
    assert sheet.review.x_value == str(kz_per_step)
    assert sheet.review.step_value == fmt.format_money(step_k * 1000)


def test_the_final_table_equals_the_trace_and_the_config_weights(sheet, cfg, traces):
    weights = cfg.final_index
    for result, (name, trace) in zip(sheet.tiers, traces.items()):
        review = trace.review
        index = rules.final_index(review.kz_final, review.ros, weights.weight_kz, weights.weight_ros)
        assert result.tier == name.capitalize()
        assert result.review_delta == fmt.format_signed(review.kz_review_change)
        assert result.kz_final == str(review.kz_final)
        assert result.own_spend == fmt.format_money(review.own_spend_k * 1000)
        assert result.total_damage == fmt.format_money(review.total_damage_eur)
        assert result.remaining == fmt.format_money(review.remaining_k * 1000)
        assert result.ros == fmt.format_number(rules.ros_two_decimals(review.ros))
        assert result.final_index == fmt.format_number(index)
    assert tuple(row.key for row in sheet.final_rows) == master.FINAL_ROW_IDS
    assert len(sheet.final_rows) == 7
    for row in sheet.final_rows:
        assert len(row.values) == len(cfg.budget_tiers)
    assert sheet.final_weight_label == master_text("final_index_weight")
    assert sheet.final_weight_value == fmt.format_number(weights.weight_ros)


def test_the_final_index_uses_the_weights_of_the_config(cfg, texts, clues, tmp_path):
    def reweigh(raw):
        raw["final_index"] = {"weight_kz": 1, "weight_ros": 2}

    other = master.build_master_sheet(_modified(tmp_path, reweigh), texts, clues)
    base = master.build_master_sheet(cfg, texts, clues)
    assert _row(other.final_rows, "final_index").values != _row(base.final_rows, "final_index").values


# ---- Welle 0 --------------------------------------------------------------------------------------------------------


def test_the_welle_zero_key_equals_the_printed_example(sheet, cfg, texts):
    trace = practice.check_example(cfg)
    doc = practice.build_practice_document(cfg, texts)
    assert sheet.welle0.header[1] == f"{texts.get('sheets.tracking.wave')} 0"
    expected = _expected_keys(practice.practice_config(cfg), practice.practice_config(cfg).waves[0], trace.waves[0])
    for key, value in expected.items():
        assert _row(sheet.welle0.rows, key).values == (value,), key
    printed = {
        "e_value": doc.sheet.e_value_line[-1].value,
        "gr": doc.sheet.reduction_line[-1].value,
        "kz_change": doc.sheet.wave_kz_line[-1].value,
        "kz_attack": doc.sheet.wave_kz_line[1].value,
        "damage_after": doc.sheet.result_line[1].value,
    }
    for key, value in printed.items():
        assert _row(sheet.welle0.rows, key).values == (value,), key


# ---- clue matrix ------------------------------------------------------------------------------------------------------


def test_the_clue_matrix_equals_the_facilitator_view(sheet, cfg, texts, clues):
    rows = FacilitatorView(cfg, texts, clues).clue_matrix()
    flat = [
        (group.title, entry.number, entry.document, entry.section, entry.quote, entry.why, entry.measures)
        for group in sheet.clue_groups
        for entry in group.rows
    ]
    assert flat == [
        (row.title, str(row.number), row.document, row.section, row.quote, row.why, row.measures) for row in rows
    ]
    assert len(flat) == len(clues)
    assert sheet.clue_header[5] == master_text("clue_head_measures")
    assert any(entry.measures for group in sheet.clue_groups for entry in group.rows)
    assert [group.title for group in sheet.clue_groups] == list(dict.fromkeys(row.title for row in rows))


# ---- build guard ----------------------------------------------------------------------------------------------------


def test_a_missing_tier_stops_the_build(texts, clues, tmp_path):
    def drop(raw):
        del raw["reference_plans"]["high"]

    with pytest.raises(PrintModelError, match="high"):
        master.build_master_sheet(_modified(tmp_path, drop), texts, clues)


def test_an_illegal_path_stops_the_build(texts, clues, tmp_path):
    def break_swap(raw):
        del raw["reference_plans"]["medium"]["windows"][0]["swap"]

    with pytest.raises(PrintModelError, match="medium"):
        master.build_master_sheet(_modified(tmp_path, break_swap), texts, clues)


def test_an_out_of_budget_path_stops_the_build(texts, clues, tmp_path):
    def shrink(raw):
        raw["budget_tiers"]["low"]["budget"] = 120

    with pytest.raises(PrintModelError, match="low"):
        master.build_master_sheet(_modified(tmp_path, shrink), texts, clues)


def test_a_swap_only_path_stops_the_build(texts, clues, tmp_path):
    def drop_voluntary_move(raw):
        windows = raw["reference_plans"]["high"]["windows"]
        windows[1]["selection"] = dict(windows[0]["selection"])

    with pytest.raises(PrintModelError, match="high"):
        master.build_master_sheet(_modified(tmp_path, drop_voluntary_move), texts, clues)


# ---- golden ---------------------------------------------------------------------------------------------------------


def printed_payload(sheet) -> dict:
    return {
        "waves": {
            str(section.wave_id): {
                "title": section.title,
                "check_cases": [list(row) for row in section.checks.case_rows],
                "check_table": [list(row) for row in section.checks.table_rows],
                "keys": {row.key: list(row.values) for row in section.key_rows},
            }
            for section in sheet.waves
        },
        "paths": {line.tier: {"start": line.start, "windows": list(line.windows)} for line in sheet.paths},
        "final": {row.key: list(row.values) for row in sheet.final_rows},
        "welle0": {row.key: list(row.values) for row in sheet.welle0.rows},
    }


def test_every_printed_answer_key_is_pinned(sheet, update_golden, golden_report):
    check_golden(GOLDEN_DIR / "answer_keys.json", printed_payload(sheet), update_golden, golden_report)


def test_committed_index_is_kz_plus_k_times_two_decimal_ros(cfg, traces):
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    k = raw["final_index"]["weight_ros"]
    assert raw["final_index"]["weight_kz"] == 1
    assert isinstance(k, int) and not isinstance(k, bool) and k >= 1
    for name, trace in traces.items():
        review = trace.review
        expected = review.kz_final + k * Fraction(round_half_away_frac(review.ros * 100), 100)
        index = rules.final_index(
            review.kz_final, review.ros, cfg.final_index.weight_kz, cfg.final_index.weight_ros
        )
        assert index == expected, name


def test_changing_a_reference_path_changes_the_pinned_payload(sheet, texts, clues, tmp_path):
    def cheaper(raw):
        raw["reference_plans"]["medium"]["windows"][1]["selection"]["M7"] = 0

    other = master.build_master_sheet(_modified(tmp_path, cheaper), texts, clues)
    assert printed_payload(other) != printed_payload(sheet)


# --- business-impact cheat sheet (RISK-05, D-05, D-06, D-22) -------------------------------------------------------


@pytest.fixture(scope="module")
def cheat_page(cfg, texts):
    return cheatsheet.build_cheat_sheet_page(cfg, texts)


def test_cheat_sheet_page_is_absent_without_cases(cfg, texts, tmp_path):
    assert cheatsheet.build_cheat_sheet_page(load_config(MINI), texts) is None

    def no_cases(raw):
        del raw["risk_matrix"]["cases"]

    assert cheatsheet.build_cheat_sheet_page(_modified(tmp_path, no_cases), texts) is None


def test_cheat_sheet_bands_follow_the_config_bands_with_their_ranges(cfg, texts, cheat_page):
    words = texts.subtree("sheets.register")
    ranges = risk.band_ranges(cfg.risk_matrix.bands, words)
    assert [(band.word, band.range) for band in cheat_page.bands] == [
        (words["bands"][band.id], ranges[index]) for index, band in enumerate(cfg.risk_matrix.bands)
    ]


def test_cheat_sheet_cases_follow_the_config_order_with_texts_and_band_strings(cfg, texts, cheat_page):
    bands = {band.id: f"{item.word} ({item.range})" for band, item in zip(cfg.risk_matrix.bands, cheat_page.bands)}
    assert [case.case for case in cheat_page.cases] == [
        texts.get(f"sheets.cheatsheet.cases.{case.id}.case") for case in cfg.risk_matrix.cases
    ]
    for case, printed in zip(cfg.risk_matrix.cases, cheat_page.cases):
        assert printed.answer == texts.get(f"sheets.cheatsheet.cases.{case.id}.answer")
        assert printed.band == bands[case.band]


def test_cheat_sheet_case_has_no_anchor_field_and_names_no_attack(cfg, texts, cheat_page):
    assert not hasattr(cheat_page.cases[0], "like_attack")
    ctx = veil.context(cfg, texts, load_content(CONTENT_DIR).terms)
    fragments = cheat_page.printed_fragments()
    assert fragments
    for text in fragments:
        assert not any(attack_id in text.lower() for attack_id in cfg.attacks), text
        for profile in (audience.PROFILE_STORY, audience.PROFILE_NAMES):
            assert veil.name_hits(text, ctx, profile) == [], (profile, text)


def test_cheat_sheet_intro_names_the_management_role_and_case_texts_hold_no_amount(cheat_page):
    assert "Geschäftsführung" in cheat_page.intro
    for case in cheat_page.cases:
        for text in (case.case, case.answer):
            assert not any(char.isdigit() for char in text) and "€" not in text, text


def test_cheat_sheet_cases_carry_their_goal_letter(cfg, texts, cheat_page):
    assert [case.goal for case in cheat_page.cases] == [
        texts.get(f"sheets.register.goals.{case.goal}") for case in cfg.risk_matrix.cases
    ]


def test_cheat_sheet_goal_header_comes_from_the_texts(texts, cheat_page):
    assert cheat_page.goal_header == texts.get("sheets.cheatsheet.head_goal")
    assert cheat_page.header == (
        texts.get("sheets.cheatsheet.head_case"),
        texts.get("sheets.cheatsheet.head_answer"),
        texts.get("sheets.cheatsheet.head_band"),
    )


def test_cheat_sheet_intro_asks_per_asset_and_goal(cheat_page):
    assert "Geschäftsführung" in cheat_page.intro
    assert "Schutzziel" in cheat_page.intro
    assert "Matrix" not in cheat_page.intro
    assert "Matrix" not in cheat_page.bands_title


def test_cheat_sheet_more_cases_than_the_maximum_stop_the_build(cfg, texts):
    extra = tuple(
        dataclasses.replace(cfg.risk_matrix.cases[0], id=f"extra_{index}")
        for index in range(cheatsheet.MAX_CHEAT_CASES + 1)
    )
    broken = dataclasses.replace(cfg, risk_matrix=dataclasses.replace(cfg.risk_matrix, cases=extra))
    with pytest.raises(PrintModelError, match="MAX_CHEAT_CASES"):
        cheatsheet.build_cheat_sheet_page(broken, texts)


def test_cheat_sheet_texts_are_required_only_with_cases(cfg):
    assert "cheatsheet" not in PREWAVE_SHEETS
    assert "sheets.cheatsheet" in PHASE7_PREFIXES
    assert not [key for key in required_keys(load_config(MINI)) if key.startswith("sheets.cheatsheet")]
    keys = required_keys(cfg)
    assert "sheets.cheatsheet.title" in keys
    for case in cfg.risk_matrix.cases:
        assert f"sheets.cheatsheet.cases.{case.id}.case" in keys
        assert f"sheets.cheatsheet.cases.{case.id}.answer" in keys


def test_the_story_direction_points_to_the_cheat_sheet(texts):
    direction = texts.get("sheets.ablauf.blocks.story_groups.direction")
    assert texts.get("sheets.cheatsheet.title") in direction


def test_the_was_neu_clue_line_names_the_cheat_sheet(texts):
    line = texts.get("sheets.was_neu.material.clues")
    assert "Geschäftsfolgen" in line and "Geschäftsfolgen" in texts.get("sheets.cheatsheet.title")
    assert len(line) <= 64


def test_the_master_sheet_carries_the_cheat_sheet(cfg, texts, clues, sheet, cheat_page):
    assert isinstance(sheet.cheat, cheatsheet.CheatSheetPage)
    assert sheet.cheat == cheat_page
    printed = sheet.printed_fragments()
    for fragment in cheat_page.printed_fragments():
        assert fragment in printed, fragment
