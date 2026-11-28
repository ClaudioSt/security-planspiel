"""Treue der Migration nach content/texte.toml (D-04, D-05, D-13a, D-14, D-27, D-28).

The generator-fidelity tests were retired in Phase 7 (LEG-01) after the migration was complete.
"""
import pytest

from planspiel.cli import main
from planspiel.config import load_config
from planspiel.texts import check_texts, load_content
from tests.support import CONFIG_PATH, CONTENT_DIR

BONUS_REASONS = {
    ("ransomware", "M3"): "EDR/XDR erkennt Ransomware früh",
    ("ransomware", "M4"): "Backup ermöglicht schnelle Wiederherstellung",
    ("ransomware", "M6"): "Geschulte Mitarbeitende erkennen Phishing",
    ("ot", "M5"): "OT/IT-Segmentierung isoliert die Produktion",
    ("ot", "M7"): "Patch Management schließt OT-Schwachstellen",
    ("exfil", "M1"): "IAM/PAM verhindert unbefugten Zugriff",
    ("exfil", "M2"): "SIEM erkennt Datenabfluss",
    ("exfil", "M8"): "Supplier Security schützt die Schnittstellen zu Lieferanten",
}

ALLOWLIST_PINNED = {
    ("measures.M2.levels_desc.1", "30 Tage"),
    ("measures.M2.levels_simple.1", "30 Tage"),
    ("measures.M2.levels_desc.3", "24/7"),
    ("measures.M4.levels_desc.1", "14 Tage"),
    ("measures.M4.levels_desc.2", "3-2-1"),
    ("measures.M4.levels_desc.3", "<4h"),
    ("measures.M6.levels_desc.1", "30 Min"),
    ("sheets.angriff.wave_kz_rounding", ",5"),
    ("sheets.angriff.rounding_note", ",5"),
    ("sheets.tracking.window_intro", "Level 0"),
    ("sheets.angriff.events_hint", "±0"),
}


CONTENT = load_content(CONTENT_DIR)
TEXTS = CONTENT.texts


def test_revealed_attack_names_are_the_worksheet_names():
    names = {attack: TEXTS.get(f"attacks.{attack}.revealed.name") for attack in ("ransomware", "ot", "exfil")}
    assert names == {"ransomware": "Ransomware", "ot": "OT-Störung", "exfil": "Datenexfiltration"}


def test_attack_tables_hold_only_the_veiled_and_the_revealed_part():
    for attack in ("ransomware", "ot", "exfil"):
        assert set(TEXTS.subtree(f"attacks.{attack}")) == {"veiled", "revealed"}


def test_bonus_reasons_are_carried_as_revealed_only_keys():
    found = {}
    for attack in ("ransomware", "ot", "exfil"):
        for measure, text in TEXTS.subtree(f"attacks.{attack}.revealed.bonus_reasons").items():
            found[(attack, measure)] = text
    assert found == BONUS_REASONS


def test_kurswechsel_and_sparprogramm_rule_texts():
    rule = TEXTS.get("events.kurswechsel.rule")
    assert rule.startswith("Im Change-Fenster nach dieser Welle führt ihr genau einen Maßnahmentausch durch")
    assert rule.endswith("Weitere Änderungen im selben Fenster bleiben erlaubt.")
    narrative = TEXTS.get("events.kurswechsel.narrative")
    assert narrative.startswith("Nach den neuesten Erkenntnissen richtet die Geschäftsführung")
    assert narrative.endswith("der Kunde beteiligt sich an den Kosten.")
    assert TEXTS.get("events.sparprogramm.rule") == (
        "Geprüft wird das Restbudget erst am Ende; im Change-Fenster nach dieser Welle könnt ihr noch "
        "gegensteuern (Senken oder Kündigen spart OPEX in der nächsten Welle, Init wird nicht erstattet)."
    )


STORY_SPOT_CHECKS = [
    ("steckbrief", "Office-IT und OT/Produktion nutzen dasselbe LAN (kein separates OT-Netz)"),
    ("steckbrief", "Remote-Zugänge für fünf Lieferanten (u. a. MES, CAD, IT)"),
    ("zeitungsartikel", "Drei Fertigungslinien standen still"),
    ("anfrage_mail", "Wir haben einen Virenscanner und Backups, aber keine strukturierte Security-Strategie."),
    ("audit_mail", "Bei kritischen Lücken behalten wir uns vor:"),
]


@pytest.mark.parametrize("doc, sentence", STORY_SPOT_CHECKS)
def test_story_sentences_are_carried_verbatim(doc, sentence):
    assert any(sentence in text for _, text in TEXTS.strings(f"story.{doc}")), sentence


def test_digit_allowlist_is_exactly_the_reviewed_set():
    assert {(entry.key, entry.token) for entry in CONTENT.allowlist} == ALLOWLIST_PINNED
    assert len(CONTENT.allowlist) == len(ALLOWLIST_PINNED)
    assert all(entry.why.strip() for entry in CONTENT.allowlist)


def test_real_content_passes_every_lint():
    assert check_texts(load_config(CONFIG_PATH), CONTENT) == []


def test_cli_texts_passes_on_the_real_content(capsys):
    code = main(["texts", "--config", str(CONFIG_PATH), "--content-dir", str(CONTENT_DIR)])
    assert code == 0
    assert "0 Fehler, 0 Warnung(en)" in capsys.readouterr().out
