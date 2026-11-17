"""Attack worksheet print model: exact values next to display strings, with the D-06/D-08/D-09 guards (PRINT-03)."""
import dataclasses
import re
from fractions import Fraction

import pytest

from planspiel import fmt
from planspiel.config import load_config
from planspiel.printmodel import (
    MIN_HALF_DISTANCE,
    AttackSheet,
    Box,
    PrintModelError,
    build_attack_sheet,
    build_attack_sheets,
    min_half_distance,
)
from planspiel.rules import worksheet_constants
from planspiel.texts import RevealView, load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]
BOX = "▢"


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    return load_config(config_path), load_texts(content_dir / "texte.toml")


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, texts, build_attack_sheets(cfg, texts)


def _norm(line):
    text = "".join(BOX if isinstance(part, Box) else part for part in line)
    return re.sub(r"\s+", " ", text).strip()


def test_one_sheet_per_wave_in_wave_order(real):
    cfg, _, sheets = real
    assert [sheet.job for sheet in sheets] == ["angriff-1_ransomware", "angriff-2_ot", "angriff-3_exfil"]
    assert [sheet.title for sheet in sheets] == [
        "Angriff 1: Ransomware", "Angriff 2: OT-Störung", "Angriff 3: Datenexfiltration"
    ]
    assert [sheet.wave_id for sheet in sheets] == [wave.wave_id for wave in cfg.waves]


def test_exact_fields_equal_the_worksheet_constants(loaded):
    cfg, texts = loaded
    for wave, sheet in zip(cfg.waves, build_attack_sheets(cfg, texts)):
        constants = worksheet_constants(cfg, wave)
        for name in constants._fields:
            assert getattr(sheet, name) == getattr(constants, name), name
        assert sheet.base_cia == (10, 10, 10)
        assert sheet.cia_rows == len(cfg.measures)


def test_real_cia_table_has_one_blank_row_per_measure(real):
    cfg, _, sheets = real
    assert all(sheet.cia_rows == len(cfg.measures) == 10 for sheet in sheets)


def test_step_headings_are_numbered_in_the_mhp_order(real):
    _, _, sheets = real
    assert list(sheets[0].step_headings) == ["cia", "e_value", "bonus", "reduction", "cases", "recovery", "wave_kz"]
    assert sheets[0].step_headings["cia"] == "Schritt 1: CIA-Werte eintragen"
    assert sheets[0].step_headings["cases"] == "Schritt 5: Fall bestimmen, Schaden und KZ berechnen"
    assert sheets[0].step_headings["recovery"] == "Schritt 6: Recovery anrechnen"
    assert sheets[0].step_headings["wave_kz"] == "Schritt 7: KZ-Änderung dieser Welle"
    assert list(sheets[2].step_headings) == ["cia", "e_value", "bonus", "reduction", "cases", "wave_kz"]
    assert sheets[2].step_headings["wave_kz"] == "Schritt 6: KZ-Änderung dieser Welle"


def test_e_value_line_carries_the_weights_with_boxes(real):
    _, _, sheets = real
    assert _norm(sheets[0].e_value_line) == f"E-Wert = C {BOX} × 0,4 + I {BOX} × 0,4 + A {BOX} × 0,2 = {BOX}"
    assert _norm(sheets[1].e_value_line) == f"E-Wert = C {BOX} × 0,2 + I {BOX} × 0,2 + A {BOX} × 0,6 = {BOX}"
    assert _norm(sheets[2].e_value_line) == f"E-Wert = C {BOX} × 0,5 + I {BOX} × 0,3 + A {BOX} × 0,2 = {BOX}"


def test_the_cap_is_printed_as_its_own_number(real):
    _, _, sheets = real
    assert [_norm(sheet.cap_line) for sheet in sheets] == [
        "Schwelle: 22 · Kappung: 8 · Obergrenze: 22 + 8 = 30",
        "Schwelle: 20 · Kappung: 10 · Obergrenze: 20 + 10 = 30",
        "Schwelle: 24 · Kappung: 7 · Obergrenze: 24 + 7 = 31",
    ]
    assert all(len(sheet.cap_line) == 1 and isinstance(sheet.cap_line[0], str) for sheet in sheets)


def test_case_blocks_of_the_recovery_wave(real):
    _, texts, sheets = real
    sheet = sheets[0]
    reveal = RevealView(real[0], texts).attack("ransomware")
    assert [block.heading for block in sheet.cases] == [
        "Fall 1: Gesamtreduktion ≤ 22", "Fall 2: Gesamtreduktion ≥ 30", "Fall 3: 22 < Gesamtreduktion < 30"
    ]
    assert [block.text for block in sheet.cases] == reveal["cases"]
    assert sheet.cases[0].outcome == "Schaden vor Recovery: 160.000 € · KZ: −8"
    assert sheet.cases[1].outcome == "Schaden vor Recovery: 0 € · KZ: +8"
    damage_line, kz_line = sheet.cases[2].lines
    assert _norm(damage_line) == f"Schaden vor Recovery = (30 − GR {BOX}) × 20.000 € = {BOX}"
    assert _norm(kz_line) == f"KZ = −8 + (GR {BOX} − 22) × 2 = {BOX}"


def test_recovery_step(real):
    _, _, sheets = real
    sheet = sheets[0]
    assert _norm(sheet.recovery_line) == (
        f"Schaden nach Recovery = Schaden vor Recovery {BOX} × (1 − r {BOX}) = {BOX}"
    )
    assert sheet.recovery_table[0] == ("0", "kein Recovery", "0 %")
    assert sheet.recovery_table[1] == ("1", "Basis-Recovery", "10 %")
    assert sheet.recovery_table[2] == ("2", "teilw. Recovery", "30 %")
    assert sheet.recovery_table[3] == ("3", "starke Recovery", "50 %")


def test_wave_kz_line(real):
    _, _, sheets = real
    expected = (
        f"KZ-Änderung dieser Welle = KZ Angriff {BOX} + KZ Events {BOX} = {BOX}, "
        f"gerundet (ab ,5 vom Betrag aufrunden): {BOX}"
    )
    assert all(_norm(sheet.wave_kz_line) == expected for sheet in sheets)


def test_wave_without_recovery_uses_plain_damage_and_the_one_decimal_slope(real):
    _, texts, sheets = real
    sheet = sheets[2]
    assert sheet.with_recovery is False
    assert sheet.recovery_line is None
    assert sheet.recovery_table == ()
    assert sheet.cases[0].outcome == "Schaden: 140.000 € · KZ: −6"
    assert sheet.cases[1].outcome == "Schaden: 0 € · KZ: +8"
    damage_line, kz_line = sheet.cases[2].lines
    assert _norm(damage_line) == f"Schaden = (31 − GR {BOX}) × 20.000 € = {BOX}"
    assert _norm(kz_line).endswith(f"× 2 = {BOX}")
    assert "÷" not in _norm(kz_line)
    assert sheet.kz_hint == texts.get("sheets.angriff.kz_decimals_hint")


def test_terminating_slopes_use_the_decimals_hint(real):
    _, texts, sheets = real
    assert sheets[0].kz_hint == sheets[1].kz_hint == texts.get("sheets.angriff.kz_decimals_hint")
    assert "× 1,4" in _norm(sheets[1].cases[2].lines[1])


def test_bonus_rows_carry_the_reason_texts(real):
    cfg, texts, sheets = real
    reasons = RevealView(cfg, texts).attack("ransomware")["bonus_reasons"]
    assert sheets[0].bonus_table == (
        ("M3 – EDR/XDR", "2", "+6", reasons["M3"]),
        ("M4 – Backup & Disaster Recovery", "2", "+5", reasons["M4"]),
        ("M6 – Security Awareness & Training", "2", "+4", reasons["M6"]),
    )
    assert _norm(sheets[0].total_bonus_line) == f"Gesamtbonus = {BOX}"
    assert _norm(sheets[0].reduction_line) == f"Gesamtreduktion = E-Wert {BOX} + Gesamtbonus {BOX} = {BOX}"


def test_a_wave_without_bonus_measures_prints_an_empty_table_and_still_the_total():
    cfg, texts = load_config(MINI), load_texts(MINI_CONTENT_DIR / "texte.toml")
    sheet = build_attack_sheet(cfg, texts, cfg.waves[1])
    assert sheet.bonus_table == ()
    assert _norm(sheet.total_bonus_line) == f"Gesamtbonus = {BOX}"


def test_cia_table_rows(real):
    _, _, sheets = real
    assert sheets[0].cia_base_row[-3:] == ("10", "10", "10")
    assert sheets[0].level_hint == "(1 / 2 / 3)"


def _expected_strings(sheet):
    yield fmt.format_number(sheet.w_c)
    yield fmt.format_number(sheet.w_i)
    yield fmt.format_number(sheet.w_a)
    yield fmt.format_number(sheet.lower)
    yield fmt.format_number(sheet.upper)
    yield fmt.format_number(sheet.unit_eur)
    yield fmt.format_money(sheet.case_1_damage_eur)
    yield fmt.format_money(sheet.case_2_damage_eur)
    yield fmt.format_signed(sheet.kz_case_1)
    yield fmt.format_signed(sheet.kz_case_2)
    yield fmt.format_factor(sheet.slope)
    for row in sheet.bonus_rows:
        yield str(row.min_level)
        yield fmt.format_signed(row.points)
    for row in sheet.recovery_rows:
        yield fmt.format_percent(row.factor)
    for value in sheet.base_cia:
        yield str(value)


def test_every_exact_value_appears_in_a_printed_fragment(loaded):
    cfg, texts = loaded
    for sheet in build_attack_sheets(cfg, texts):
        fragments = sheet.printed_fragments()
        assert len(fragments) == len(set(fragments))
        for expected in _expected_strings(sheet):
            assert any(expected in fragment for fragment in fragments), (sheet.job, expected)


def test_the_cap_is_checked_through_the_cap_line_fragment(loaded):
    cfg, texts = loaded
    for sheet in build_attack_sheets(cfg, texts):
        compact = [re.sub(r"\s+", "", fragment) for fragment in sheet.printed_fragments()]
        assert any(f"Kappung:{fmt.format_number(sheet.reduction_cap)}" in fragment for fragment in compact)
        assert any(_norm(sheet.cap_line) == fragment for fragment in sheet.printed_fragments())


def test_fragments_start_with_title_and_headings(real):
    _, _, sheets = real
    fragments = sheets[0].printed_fragments()
    assert fragments[0] == "Angriff 1: Ransomware"
    assert all(heading in fragments for heading in sheets[0].step_headings.values())


def test_fragments_are_exactly_the_digit_bearing_strings(real):
    _, _, sheets = real
    for fragment in sheets[0].printed_fragments()[1 + len(sheets[0].step_headings):]:
        assert re.search(r"\d", fragment), fragment


def test_real_minimal_distances_to_a_half_integer(real):
    cfg, _, _ = real
    distances = [min_half_distance(cfg, worksheet_constants(cfg, wave)) for wave in cfg.waves]
    assert distances == [Fraction(1, 10), Fraction(1, 50), Fraction(1, 10)]
    assert all(distance >= MIN_HALF_DISTANCE for distance in distances)


def test_guard_refuses_a_base_severity_that_differs_from_the_cap(real):
    cfg, texts, _ = real
    attack = dataclasses.replace(cfg.attacks["ransomware"], base_severity=9)
    broken = dataclasses.replace(cfg, attacks={**cfg.attacks, "ransomware": attack})
    with pytest.raises(PrintModelError, match="Welle 1"):
        build_attack_sheet(broken, texts, broken.waves[0])


def test_guard_refuses_a_severity_multiplier(real):
    cfg, texts, _ = real
    tier = dataclasses.replace(cfg.budget_tiers["medium"], severity_multiplier=Fraction(11, 10))
    broken = dataclasses.replace(cfg, budget_tiers={**cfg.budget_tiers, "medium": tier})
    with pytest.raises(PrintModelError, match="Welle 2"):
        build_attack_sheet(broken, texts, broken.waves[1])


def test_guard_refuses_two_decimals_that_could_flip_the_rounding(real):
    cfg, texts, _ = real
    attack = dataclasses.replace(cfg.attacks["exfil"], base_severity=11, mitigation_cap=11)
    broken = dataclasses.replace(cfg, attacks={**cfg.attacks, "exfil": attack})
    assert min_half_distance(broken, worksheet_constants(broken, broken.waves[2])) == Fraction(1, 110)
    with pytest.raises(PrintModelError, match="Welle 3") as error:
        build_attack_sheet(broken, texts, broken.waves[2])
    assert "1/110" in str(error.value)


def test_model_carries_no_cia_mali():
    names = {field.name for field in dataclasses.fields(AttackSheet)}
    assert not [name for name in names if "cia_delta" in name or "cia_impact" in name or "mali" in name]


def test_recovery_table_names_the_measure_whose_level_sets_r(real):
    cfg, _, sheets = real
    sheet = sheets[0]
    measure = sheet.recovery_measure
    assert measure == "M4"
    assert sheet.recovery_header == ("Level", f"{measure} – {cfg.measures[measure].name}", "Recovery-Faktor r")
    assert sheet.recovery_header[1] in sheet.printed_fragments()
