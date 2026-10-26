"""Welle 0 worked example: every printed number equals the rules module (FLOW-01, ROADMAP SC3, T-05-40).

The filled values come from `rules.path_trace` (through `practice.check_example`), are replayed independently from the
exact fields of the worksheet by tests/support/worksheet_replay.py, and are pinned in tests/golden/welle0.json.
"""
import dataclasses
import json
from fractions import Fraction

import pytest

from planspiel import eventtext, fmt, practice, rules
from planspiel.booklet import TRACKING_ROW_ORDER, build_tracking_page
from planspiel.config import load_config
from planspiel.printmodel import Box, PrintModelError, build_attack_sheet, fill_line
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR
from tests.support.golden import check_golden
from tests.support.worksheet_replay import replay_steps, replay_wave
from tests.test_welle0_render import GOLDEN_DIR

TRACKING_KEYS = ("kz_before", "kz_change", "kz_after", "damage", "own_init", "own_opex", "remaining")


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def texts():
    return load_texts(CONTENT_DIR / "texte.toml")


@pytest.fixture(scope="module")
def doc(cfg, texts):
    return practice.build_practice_document(cfg, texts)


@pytest.fixture(scope="module")
def trace(cfg):
    return practice.check_example(cfg)


def _values(line):
    return [part.value for part in line if isinstance(part, Box)]


def _modified(tmp_path, change):
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    change(raw)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return load_config(path)


# ---- printmodel.fill_line ------------------------------------------------------------------------------------


def test_fill_line_replaces_the_boxes_in_order():
    line = ("A ", Box("short"), " B ", Box("long"), " C")
    filled = fill_line(line, ("1", "2"))
    assert filled == ("A ", Box("short", "1"), " B ", Box("long", "2"), " C")
    assert line == ("A ", Box("short"), " B ", Box("long"), " C")


@pytest.mark.parametrize("values", [(), ("1",), ("1", "2", "3")])
def test_fill_line_rejects_a_wrong_number_of_values(values):
    with pytest.raises(PrintModelError):
        fill_line(("A ", Box("short"), " B ", Box("long")), values)


def test_a_real_sheet_stays_unfilled(cfg, texts):
    for wave in cfg.waves:
        sheet = build_attack_sheet(cfg, texts, wave)
        assert (sheet.cia_filled, sheet.cia_sum, sheet.bonus_fulfilled) == ((), (), ())
        for line in (sheet.e_value_line, sheet.total_bonus_line, sheet.reduction_line, sheet.wave_kz_line):
            assert all(value is None for value in _values(line))


# ---- the document ----------------------------------------------------------------------------------------------


def test_job_and_title(doc, cfg):
    assert doc.job == practice.PRACTICE_JOB == "uebung-welle-0"
    assert doc.title == "Welle 0 – Übung"
    assert doc.sheet.title == doc.title
    assert doc.sheet.job == doc.job
    assert doc.sheet.wave_id == cfg.practice.wave.wave_id == 0


def test_no_practice_block_gives_no_document(cfg, texts, tmp_path):
    def drop(raw):
        del raw["practice"]

    assert practice.build_practice_document(_modified(tmp_path, drop), texts) is None


def test_the_sheet_is_the_worksheet_model_of_the_practice_view(doc, cfg, texts):
    view = practice.practice_config(cfg)
    plain = build_attack_sheet(
        view, texts, view.waves[0], view=practice.PracticeView(cfg, texts), job=practice.PRACTICE_JOB
    )
    assert dataclasses.replace(doc.sheet, **{
        name: getattr(plain, name)
        for name in (
            "e_value_line", "total_bonus_line", "reduction_line", "cases", "recovery_line", "wave_kz_line",
            "result_line", "cia_filled", "cia_sum", "bonus_fulfilled",
        )
    }) == plain


def test_every_box_of_the_sheet_is_filled(doc):
    sheet = doc.sheet
    lines = [sheet.e_value_line, sheet.total_bonus_line, sheet.reduction_line, sheet.wave_kz_line, sheet.result_line]
    lines += [sheet.recovery_line, *sheet.cases[2].lines]
    assert all(line is not None for line in lines)
    for line in lines:
        boxes = [part for part in line if isinstance(part, Box)]
        assert boxes and all(box.value for box in boxes)


def test_filled_values_equal_the_path_trace(doc, trace):
    wave = trace.waves[0]
    sheet = doc.sheet
    number, signed = fmt.format_number, fmt.format_signed
    cia = [number(wave.cia[key]) for key in "cia"]
    assert _values(sheet.e_value_line) == [*cia, number(wave.e_value)]
    assert _values(sheet.total_bonus_line) == [number(wave.bonus_reduction)]
    assert _values(sheet.reduction_line) == [
        number(wave.e_value), number(wave.bonus_reduction), number(wave.gesamtreduktion)
    ]
    assert wave.case == 3
    damage_line, kz_line = sheet.cases[2].lines
    assert _values(damage_line) == [number(wave.gesamtreduktion), fmt.format_money(wave.damage_before_eur)]
    assert _values(kz_line) == [number(wave.gesamtreduktion), signed(wave.kz_attack)]
    assert _values(sheet.recovery_line) == [
        fmt.format_money(wave.damage_before_eur), fmt.format_percent(wave.recovery_factor),
        fmt.format_money(wave.damage_eur),
    ]
    assert _values(sheet.wave_kz_line) == [
        signed(wave.kz_attack), signed(wave.kz_event), signed(wave.kz_change_exact), signed(wave.kz_change)
    ]
    assert _values(sheet.result_line) == [fmt.format_money(wave.damage_eur), signed(wave.kz_change)]


def test_the_pinned_example_numbers(doc):
    sheet = doc.sheet
    assert _values(sheet.e_value_line) == ["16", "22", "19", "19"]
    assert _values(sheet.reduction_line) == ["19", "4", "23"]
    assert _values(sheet.wave_kz_line) == ["+6,5", "−4", "+2,5", "+3"]
    assert _values(sheet.result_line) == ["18.000 €", "+3"]


def test_cia_rows_and_bonus_marks(doc, cfg, trace):
    wave = trace.waves[0]
    sheet = doc.sheet
    selected = [(measure_id, level) for measure_id, level in cfg.practice.selection.items() if level > 0]
    assert len(sheet.cia_filled) == len(selected)
    for row, (measure_id, level) in zip(sheet.cia_filled, selected):
        facts = rules.card_facts(cfg.measures, measure_id, level)
        assert row == (
            f"{measure_id} – {cfg.measures[measure_id].name}", str(level),
            *(fmt.format_number(facts.cia[key]) for key in "cia"),
        )
    assert sheet.cia_sum == tuple(fmt.format_number(wave.cia[key]) for key in "cia")
    met = {row.measure: row.measure in wave.bonus_met for row in sheet.bonus_rows}
    assert list(met.values()).count(True) == 1 and list(met.values()).count(False) == 1
    assert sheet.bonus_fulfilled == tuple(fmt.TIMES if met[row.measure] else "–" for row in sheet.bonus_rows)


def test_the_independent_replay_equals_the_trace(doc, trace):
    wave = trace.waves[0]
    sheet = doc.sheet
    levels = {row[0].split(" ")[0]: int(row[1]) for row in sheet.cia_filled}
    cia = [sheet.base_cia[index] + sum(int(row[2 + index]) for row in sheet.cia_filled) for index in range(3)]
    result = replay_wave(sheet, cia, levels, wave.kz_event)
    assert result.case == wave.case == 3
    assert result.e_value == wave.e_value
    assert result.gr == wave.gesamtreduktion
    assert result.damage_before_eur == wave.damage_before_eur
    assert result.damage_eur == wave.damage_eur
    assert result.kz_attack == wave.kz_attack
    assert result.change == wave.kz_change
    assert replay_steps(sheet, wave.e_value, levels, wave.kz_event) == result


def test_selection_rows_equal_the_card_facts(doc, cfg):
    selected = [(measure_id, level) for measure_id, level in cfg.practice.selection.items() if level > 0]
    assert len(doc.selection_rows) == len(selected)
    init_sum = opex_sum = 0
    for row, (measure_id, level) in zip(doc.selection_rows, selected):
        facts = rules.card_facts(cfg.measures, measure_id, level)
        assert row.measure == f"{measure_id} – {cfg.measures[measure_id].name}"
        assert row.level == str(level)
        assert (row.c, row.i, row.a) == tuple(fmt.format_number(facts.cia[key]) for key in "cia")
        assert row.init == fmt.format_money(facts.init_k * 1000)
        assert row.opex == fmt.format_money(facts.opex_k * 1000)
        init_sum += facts.init_k
        opex_sum += facts.opex_k
    assert doc.selection_total.init == fmt.format_money(init_sum * 1000) == "104.000 €"
    assert doc.selection_total.opex == fmt.format_money(opex_sum * 1000) == "23.000 €"


def test_event_block_equals_the_generated_effect_rows(doc, cfg, texts, trace):
    view = practice.practice_config(cfg)
    effect = eventtext.effect_rows(cfg.practice.event, view, texts, event_texts=texts.subtree("practice.event"))
    assert doc.event.rows == tuple(row.text for row in effect.rows)
    assert doc.event.heading == effect.heading
    level = cfg.practice.selection[cfg.practice.event.params["measure"]]
    chosen = effect.rows[doc.event.selected]
    assert level in chosen.covers
    assert chosen.value == trace.waves[0].kz_event
    assert doc.event.result.endswith(chosen.text)
    assert doc.event.narrative == texts.get("practice.event.narrative")


def test_effect_rows_still_need_the_event_in_the_config_without_the_override(cfg, texts):
    view = practice.practice_config(cfg)
    with pytest.raises(KeyError):
        eventtext.effect_rows(cfg.practice.event, view, texts)


def test_tracking_excerpt_follows_the_tracking_sheet(doc, cfg, texts, trace):
    wave = trace.waves[0]
    page = build_tracking_page(cfg, texts)
    expected_rows = [row for key in TRACKING_ROW_ORDER if key in TRACKING_KEYS for row in page.rows if row.key == key]
    assert doc.tracking.columns == (page.columns[0], "Welle 0")
    assert [row[0] for row in doc.tracking.rows] == [row.label for row in expected_rows]
    cells = {
        row.key: (row.label, *cell)
        for row, cell in zip(
            expected_rows,
            [
                (str(wave.kz_before), str(wave.kz_before)),
                ("", fmt.format_signed(wave.kz_change)),
                ("", str(wave.kz_after)),
                ("", fmt.format_money(wave.damage_eur)),
                (fmt.format_money(trace.init_k * 1000), ""),
                ("", fmt.format_money(wave.own_opex_k * 1000)),
                (fmt.format_money(trace.start_remaining_k * 1000), fmt.format_money(wave.remaining_k * 1000)),
            ],
        )
    }
    assert list(doc.tracking.rows) == list(cells.values())
    assert wave.kz_unclamped > rules.KZ_MAX and wave.kz_after == rules.KZ_MAX
    assert str(wave.kz_unclamped) in doc.tracking.clamp_hint and str(rules.KZ_MAX) in doc.tracking.clamp_hint


def test_the_build_stops_when_the_example_no_longer_teaches_the_mechanics(texts, tmp_path):
    def flatten(raw):
        raw["practice"]["selection"] = {key: 0 for key in raw["practice"]["selection"]}

    with pytest.raises(PrintModelError):
        practice.build_practice_document(_modified(tmp_path, flatten), texts)


# ---- golden --------------------------------------------------------------------------------------------------


def printed_payload(doc) -> dict:
    sheet = doc.sheet
    return {
        "title": doc.title,
        "intro": doc.intro,
        "sheet_lines": {
            "e_value": _values(sheet.e_value_line),
            "total_bonus": _values(sheet.total_bonus_line),
            "reduction": _values(sheet.reduction_line),
            "damage": _values(sheet.cases[2].lines[0]),
            "kz": _values(sheet.cases[2].lines[1]),
            "recovery": _values(sheet.recovery_line),
            "wave_kz": _values(sheet.wave_kz_line),
            "result": _values(sheet.result_line),
        },
        "cia_rows": [list(row) for row in sheet.cia_filled],
        "cia_sum": list(sheet.cia_sum),
        "bonus_fulfilled": list(sheet.bonus_fulfilled),
        "selection": [dataclasses.astuple(row) for row in doc.selection_rows],
        "selection_total": dataclasses.astuple(doc.selection_total),
        "event": {"rows": list(doc.event.rows), "selected": doc.event.selected, "result": doc.event.result},
        "tracking": {
            "columns": list(doc.tracking.columns),
            "rows": [list(row) for row in doc.tracking.rows],
            "clamp_hint": doc.tracking.clamp_hint,
        },
        "fragments": list(doc.printed_fragments()),
    }


def test_every_printed_string_is_pinned(doc, update_golden, golden_report):
    check_golden(GOLDEN_DIR / "welle0.json", printed_payload(doc), update_golden, golden_report)


def test_changing_a_practice_weight_changes_the_printed_e_value_line(texts, doc, tmp_path):
    def reweigh(raw):
        raw["practice"]["wave"]["weights"] = {"c": 0.35, "i": 0.35, "a": 0.3}

    other = practice.build_practice_document(_modified(tmp_path, reweigh), texts)
    assert other.sheet.e_value_line != doc.sheet.e_value_line
    assert "0,35" in "".join(part for part in other.sheet.e_value_line if isinstance(part, str))
    assert printed_payload(other) != printed_payload(doc)
    expected = Fraction(16) * Fraction(35, 100) + Fraction(22) * Fraction(35, 100) + Fraction(19) * Fraction(3, 10)
    assert _values(other.sheet.e_value_line)[3] == fmt.format_number(expected)
