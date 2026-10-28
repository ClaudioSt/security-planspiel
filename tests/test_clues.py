"""Hinweis-Matrix für die Spielleitung: Daten, Prüfung, Tabelle und `planspiel clues` (VEIL-03, D-17, D-18)."""
import copy
import dataclasses
import unicodedata

import pytest

from planspiel.cli import main
from planspiel.config import load_config
from planspiel.texts import (
    Clue,
    FacilitatorView,
    Texts,
    check_clues,
    format_clue_matrix,
    load_clues,
    load_texts,
)
from tests.support import MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
CLUES_PATH = MINI_CONTENT_DIR / "clues.toml"
HEADER = "| Angriff | Nr. | Dokument | Abschnitt | Zitat | Warum | Maßnahmen (Gewicht) |"

CFG = load_config(MINI)
TEXTS = load_texts(MINI_CONTENT_DIR / "texte.toml")
CLUES = load_clues(CLUES_PATH)


def _codes(issues):
    return [(issue.code, issue.path) for issue in issues]


def _of(attack):
    return [clue for clue in CLUES if clue.attack == attack]


def _without(removed):
    return tuple(clue for clue in CLUES if clue is not removed)


def test_load_clues_returns_the_entries_in_file_order():
    assert len(CLUES) == 6
    assert all(isinstance(clue, Clue) for clue in CLUES)
    assert [clue.attack for clue in CLUES] == ["ransomware", "ransomware", "ot", "ot", "exfil", "exfil"]
    assert CLUES[0].source == "story.steckbrief.betrieb.bullets"
    assert CLUES[0].quote == "Sicherung der Daten nur einmal im Monat"
    assert CLUES[0].why.startswith("Kaum Datensicherung")


def test_the_mini_clues_pass_the_check():
    assert check_clues(CFG, TEXTS, CLUES) == []


def test_every_mini_quote_is_at_least_fifteen_characters():
    assert all(len(clue.quote) >= 15 for clue in CLUES)


def test_a_single_clue_for_an_attack_is_too_few():
    issues = check_clues(CFG, TEXTS, _without(_of("ot")[0]))
    assert _codes(issues) == [("clues.too_few", "clues.ot")]


def test_an_attack_without_any_clue_is_too_few():
    kept = tuple(clue for clue in CLUES if clue.attack != "exfil")
    assert _codes(check_clues(CFG, TEXTS, kept)) == [("clues.too_few", "clues.exfil")]


def test_two_clues_from_the_same_document_are_a_single_source():
    clues = list(CLUES)
    ot_second = _of("ot")[1]
    clues[clues.index(ot_second)] = dataclasses.replace(
        ot_second,
        source="story.steckbrief.betrieb.bullets",
        quote="Sicherung der Daten nur einmal im Monat",
    )
    assert _codes(check_clues(CFG, TEXTS, tuple(clues))) == [("clues.single_source", "clues.ot")]


def test_one_changed_character_in_a_quote_is_not_found():
    clues = list(CLUES)
    clues[1] = dataclasses.replace(clues[1], quote="Wir hatten kein funktionierendes Backup-Konzepz")
    assert _codes(check_clues(CFG, TEXTS, tuple(clues))) == [("clues.quote_not_found", "clues[2]")]


def test_a_quote_matching_only_case_insensitively_is_not_found():
    clues = list(CLUES)
    clues[1] = dataclasses.replace(clues[1], quote=clues[1].quote.lower())
    assert _codes(check_clues(CFG, TEXTS, tuple(clues))) == [("clues.quote_not_found", "clues[2]")]


def test_a_quote_found_in_one_element_of_a_list_value_passes():
    assert TEXTS.get("story.steckbrief.betrieb.bullets")[1] == CLUES[0].quote
    assert check_clues(CFG, TEXTS, CLUES) == []


def test_a_decomposed_quote_matches_after_nfc():
    clues = list(CLUES)
    clues[2] = dataclasses.replace(clues[2], quote=unicodedata.normalize("NFD", clues[2].quote))
    assert check_clues(CFG, TEXTS, tuple(clues)) == []


def test_a_quote_may_be_a_part_of_a_sentence():
    quote = "Drei Fertigungslinien standen still"
    assert quote in TEXTS.get("story.zeitungsartikel.bericht.paragraphs")[0]
    assert quote != TEXTS.get("story.zeitungsartikel.bericht.paragraphs")[0]
    assert check_clues(CFG, TEXTS, CLUES) == []


def test_a_missing_source_key_is_unknown():
    extra = dataclasses.replace(CLUES[0], source="story.steckbrief.gibt_es_nicht.bullets")
    assert _codes(check_clues(CFG, TEXTS, (*CLUES, extra))) == [("clues.unknown_source", "clues[7]")]


def test_a_section_instead_of_a_text_is_an_unknown_source():
    extra = dataclasses.replace(CLUES[0], source="story.steckbrief.betrieb")
    assert _codes(check_clues(CFG, TEXTS, (*CLUES, extra))) == [("clues.unknown_source", "clues[7]")]


@pytest.mark.parametrize(
    "source", ["attacks.ransomware.revealed.narrative", "sheets.angriff.bonus_intro", "events.kurswechsel.narrative"]
)
def test_a_source_that_is_not_pre_wave_material_is_rejected(source):
    extra = dataclasses.replace(CLUES[0], source=source)
    assert _codes(check_clues(CFG, TEXTS, (*CLUES, extra))) == [("clues.not_prewave", "clues[7]")]


def test_a_measure_text_is_a_valid_pre_wave_source_in_its_own_document():
    measure = dataclasses.replace(
        _of("ransomware")[1],
        source="measures.M4.description",
        quote="Daten werden gesichert, damit der Betrieb nach einem Vorfall weiterläuft",
    )
    clues = tuple(measure if clue is _of("ransomware")[1] else clue for clue in CLUES)
    assert check_clues(CFG, TEXTS, clues) == []


def test_two_measure_clues_count_as_one_document():
    first = dataclasses.replace(
        _of("ransomware")[0],
        source="measures.M4.description",
        quote="Daten werden gesichert, damit der Betrieb nach einem Vorfall weiterläuft",
    )
    second = dataclasses.replace(
        _of("ransomware")[1],
        source="measures.M6.description",
        quote="Mitarbeitende lernen, Gefahren zu erkennen",
    )
    clues = tuple(
        first if clue is _of("ransomware")[0] else second if clue is _of("ransomware")[1] else clue for clue in CLUES
    )
    assert _codes(check_clues(CFG, TEXTS, clues)) == [("clues.single_source", "clues.ransomware")]


def test_a_measure_clue_and_a_story_clue_are_two_documents():
    measure = dataclasses.replace(
        _of("ransomware")[0],
        source="measures.M4.description",
        quote="Daten werden gesichert, damit der Betrieb nach einem Vorfall weiterläuft",
    )
    clues = tuple(measure if clue is _of("ransomware")[0] else clue for clue in CLUES)
    assert check_clues(CFG, TEXTS, clues) == []


def test_a_clue_for_an_attack_outside_the_waves_is_unknown():
    extra = dataclasses.replace(CLUES[0], attack="foo")
    assert _codes(check_clues(CFG, TEXTS, (*CLUES, extra))) == [("clues.unknown_attack", "clues[7]")]


def test_the_attack_ids_come_from_the_waves_not_from_a_fixed_list():
    shortened = dataclasses.replace(CFG, waves=CFG.waves[:2])
    issues = check_clues(shortened, TEXTS, CLUES)
    assert _codes(issues) == [("clues.unknown_attack", "clues[5]"), ("clues.unknown_attack", "clues[6]")]


def test_an_additional_wave_demands_its_own_clues():
    wave = dataclasses.replace(CFG.waves[0], wave_id=4, attack_id="ransomware")
    longer = dataclasses.replace(CFG, waves=[*CFG.waves, wave])
    assert check_clues(longer, TEXTS, CLUES) == []


@pytest.mark.parametrize("why", ["", "   "])
def test_a_blank_reason_is_rejected(why):
    clues = list(CLUES)
    clues[0] = dataclasses.replace(clues[0], why=why)
    assert _codes(check_clues(CFG, TEXTS, tuple(clues))) == [("clues.empty_why", "clues[1]")]


def test_a_short_quote_is_rejected():
    clues = list(CLUES)
    clues[3] = dataclasses.replace(clues[3], quote="standen still")
    assert _codes(check_clues(CFG, TEXTS, tuple(clues))) == [("clues.quote_too_short", "clues[4]")]


def test_a_quote_of_exactly_fifteen_characters_is_accepted():
    data = copy.deepcopy(TEXTS.data)
    data["story"]["steckbrief"]["betrieb"]["bullets"][0] = "x" * 15
    clues = list(CLUES)
    clues[2] = dataclasses.replace(clues[2], quote="x" * 15)
    assert check_clues(CFG, Texts(data), tuple(clues)) == []


def test_issue_messages_are_german_errors():
    issues = check_clues(CFG, TEXTS, _without(_of("ot")[0]))
    assert [issue.level for issue in issues] == ["error"]
    assert "Hinweis" in issues[0].message


def test_the_matrix_lists_rows_in_wave_order_then_file_order():
    rows = FacilitatorView(CFG, TEXTS, CLUES).clue_matrix()
    assert [(row.title, row.number) for row in rows] == [
        ("Angriff 1: Ransomware", 1),
        ("Angriff 1: Ransomware", 2),
        ("Angriff 2: OT-Störung", 1),
        ("Angriff 2: OT-Störung", 2),
        ("Angriff 3: Datenexfiltration", 1),
        ("Angriff 3: Datenexfiltration", 2),
    ]


def test_the_matrix_follows_a_reordered_wave_list():
    reversed_waves = [
        dataclasses.replace(wave, wave_id=number) for number, wave in enumerate(reversed(CFG.waves), start=1)
    ]
    rows = FacilitatorView(dataclasses.replace(CFG, waves=reversed_waves), TEXTS, CLUES).clue_matrix()
    assert rows[0].title == "Angriff 1: Datenexfiltration"
    assert rows[-1].title == "Angriff 3: Ransomware"


def test_the_matrix_rows_carry_document_section_quote_and_reason():
    rows = FacilitatorView(CFG, TEXTS, CLUES).clue_matrix()
    first, second = rows[0], rows[1]
    assert first.document == "MECHTECH GmbH: Unternehmenssteckbrief"
    assert first.section == "Betrieb & IT"
    assert first.quote == "Sicherung der Daten nur einmal im Monat"
    assert first.why == CLUES[0].why
    assert second.document == "AUTO TIMES"
    assert second.section == "Vorfall bei einem Zulieferer"
    assert (first.measures, second.measures) == ("M4 (2)", "M6 (2)")


def test_a_measure_source_uses_the_measure_name_and_the_source_key_as_section():
    measure = dataclasses.replace(
        CLUES[1],
        source="measures.M4.description",
        quote="Daten werden gesichert, damit der Betrieb nach einem Vorfall weiterläuft",
    )
    rows = FacilitatorView(CFG, TEXTS, (CLUES[0], measure, *CLUES[2:])).clue_matrix()
    assert rows[1].document == CFG.measures["M4"].name
    assert rows[1].section == "measures.M4.description"


def test_the_section_falls_back_to_the_source_key_without_a_heading():
    data = copy.deepcopy(TEXTS.data)
    del data["story"]["steckbrief"]["betrieb"]["heading"]
    rows = FacilitatorView(CFG, Texts(data), CLUES).clue_matrix()
    assert rows[0].section == "story.steckbrief.betrieb.bullets"


def test_a_headline_serves_as_the_section_when_there_is_no_heading():
    data = copy.deepcopy(TEXTS.data)
    del data["story"]["steckbrief"]["betrieb"]["heading"]
    data["story"]["steckbrief"]["betrieb"]["headline"] = "SCHLAGZEILE"
    rows = FacilitatorView(CFG, Texts(data), CLUES).clue_matrix()
    assert rows[0].section == "SCHLAGZEILE"


def test_the_table_has_the_header_and_one_line_per_clue():
    rows = FacilitatorView(CFG, TEXTS, CLUES).clue_matrix()
    table = format_clue_matrix(rows).splitlines()
    assert table[0] == HEADER
    assert table[1].startswith("|") and set(table[1]) <= set("|- :")
    assert len(table) == 2 + len(CLUES)
    assert table[2].startswith("| Angriff 1: Ransomware | 1 | MECHTECH GmbH: Unternehmenssteckbrief | Betrieb & IT |")


def test_a_pipe_inside_a_cell_is_escaped():
    clue = dataclasses.replace(CLUES[0], why="Erst A | dann B")
    rows = FacilitatorView(CFG, TEXTS, (clue, *CLUES[1:])).clue_matrix()
    line = format_clue_matrix(rows).splitlines()[2]
    assert "Erst A \\| dann B" in line
    assert line.count(" | ") + line.count("\\|") >= 6


def test_the_cli_prints_the_matrix_and_passes(capsys):
    assert main(["clues", "--config", str(MINI), "--content-dir", str(MINI_CONTENT_DIR)]) == 0
    out = capsys.readouterr().out
    assert HEADER in out
    assert "Angriff 1: Ransomware" in out
    assert out.rstrip().endswith("0 Fehler, 0 Warnung(en)")


def _copy_content(tmp_path, *, drop_clues=False):
    for name in ("texte.toml", "digit_allowlist.toml", "giveaway_terms.toml", "clues.toml"):
        if drop_clues and name == "clues.toml":
            continue
        (tmp_path / name).write_text((MINI_CONTENT_DIR / name).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")


def test_the_cli_fails_when_an_attack_keeps_one_clue(tmp_path, capsys):
    _copy_content(tmp_path)
    text = (tmp_path / "clues.toml").read_text(encoding="utf-8")
    first_ot = text.index('attack = "ot"')
    start = text.rindex("[[clue]]", 0, first_ot)
    end = text.index("[[clue]]", first_ot)
    (tmp_path / "clues.toml").write_text(text[:start] + text[end:], encoding="utf-8", newline="\n")
    assert main(["clues", "--config", str(MINI), "--content-dir", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "ERROR clues.too_few clues.ot" in out
    assert "1 Fehler, 0 Warnung(en)" in out


def test_the_cli_fails_on_a_missing_clues_file(tmp_path, capsys):
    _copy_content(tmp_path, drop_clues=True)
    assert main(["clues", "--config", str(MINI), "--content-dir", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "ERROR clues.toml" in out
    assert "1 Fehler, 0 Warnung(en)" in out


def test_the_cli_fails_on_malformed_toml(tmp_path, capsys):
    _copy_content(tmp_path)
    (tmp_path / "clues.toml").write_text("[[clue]\nattack = ", encoding="utf-8", newline="\n")
    assert main(["clues", "--config", str(MINI), "--content-dir", str(tmp_path)]) == 1
    assert "ERROR clues.toml" in capsys.readouterr().out


def test_planspiel_texts_does_not_read_the_clues_file(tmp_path, capsys):
    _copy_content(tmp_path, drop_clues=True)
    assert main(["texts", "--config", str(MINI), "--content-dir", str(tmp_path)]) == 0
    assert "0 Fehler, 0 Warnung(en)" in capsys.readouterr().out


def _matrix_cells(rows):
    return [cell for row in rows for cell in (row.title, row.document, row.section)]


def test_no_clue_matrix_cell_of_the_real_content_is_a_source_key():
    cfg = load_config(REPO_ROOT / "simulation_config.json")
    texts = load_texts(REPO_ROOT / "content" / "texte.toml")
    clues = load_clues(REPO_ROOT / "content" / "clues.toml")
    rows = FacilitatorView(cfg, texts, clues).clue_matrix()
    assert rows
    for cell in _matrix_cells(rows):
        assert not cell.startswith(("story.", "measures.")), cell
        assert ".paragraphs" not in cell and ".bullets" not in cell, cell


def test_no_clue_matrix_cell_of_the_mini_content_is_a_source_key():
    rows = FacilitatorView(CFG, TEXTS, CLUES).clue_matrix()
    assert rows
    for cell in _matrix_cells(rows):
        assert not cell.startswith(("story.", "measures.")), cell
        assert ".paragraphs" not in cell and ".bullets" not in cell, cell


def test_a_mail_section_without_a_heading_prints_the_german_label():
    cfg = load_config(REPO_ROOT / "simulation_config.json")
    texts = load_texts(REPO_ROOT / "content" / "texte.toml")
    clues = load_clues(REPO_ROOT / "content" / "clues.toml")
    sections = {
        clue.source: row.section
        for clue, row in zip(
            sorted(clues, key=lambda clue: [wave.attack_id for wave in cfg.waves].index(clue.attack)),
            FacilitatorView(cfg, texts, clues).clue_matrix(),
        )
    }
    assert sections["story.anfrage_mail.lage.paragraphs"] == "Lage"
    assert sections["story.audit_mail.einleitung.paragraphs"] == "Einleitung"
