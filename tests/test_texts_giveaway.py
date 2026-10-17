"""Giveaway-Lint für verhüllte Angriffsschlüssel und Event-Texte (VEIL-01, D-13b, D-13c, D-20, D-06)."""
import copy
import dataclasses

import pytest

from planspiel.cli import main
from planspiel.config import load_config
from planspiel.texts import (
    GiveawayTerms,
    Texts,
    check_giveaway,
    check_texts,
    giveaway_hits,
    load_content,
    load_giveaway_terms,
    load_texts,
    normalize_for_matching,
)
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
ATTACK_IDS = ("ransomware", "ot", "exfil")
NON_BREAKING_HYPHEN = "‑"

BOTH_HIT = [
    "Ransomware legt Zulieferer lahm",
    "Ransomware-Angriff",
    "Anti-Ransomware",
    "RANSOMWARE",
    "Datenverschlüsselung",
    "Die Daten wurden verschlüsselt",
    "VERSCHLÜSSELUNG",
    "Verschluesselung",
    "Lösegeldforderung",
    "Loesegeld",
    "Phishing-Mail",
    "Sinumerik-Schwachstelle",
    "12 CNC-Steuerungen (Sinumerik/Heidenhain)",
    "Datenexfiltration",
    "im Darknet angeboten",
    "OT-Störung",
    f"OT{NON_BREAKING_HYPHEN}Störung",
    "OT Störungen im Werk",
    "SPS-Steuerung",
    "APT-Gruppe",
]
VEILED_ONLY = [
    "Erpresser legen Zulieferer lahm",
    "OT/IT-Netz, kein separates OT-Netz",
    "OT / Produktion",
]
BOTH_PASS = [
    "Eine Störung in der Produktion",
    "Schaden durch Ausfall der Fertigung",
    "Spaß und Spiele",
    "Apotheke, Kapt'n, Optik",
    "Hotel, Pilot, Robot",
]


@pytest.fixture(scope="module")
def terms():
    return load_giveaway_terms(CONTENT_DIR / "giveaway_terms.toml")


@pytest.mark.parametrize("profile", ["veiled", "story"])
@pytest.mark.parametrize("text", BOTH_HIT)
def test_banned_in_both_profiles(terms, text, profile):
    assert giveaway_hits(text, terms, ATTACK_IDS, profile=profile)


@pytest.mark.parametrize("text", VEILED_ONLY)
def test_story_exceptions_apply_only_to_the_story_profile(terms, text):
    assert giveaway_hits(text, terms, ATTACK_IDS, profile="veiled")
    assert giveaway_hits(text, terms, ATTACK_IDS, profile="story") == []


@pytest.mark.parametrize("profile", ["veiled", "story"])
@pytest.mark.parametrize("text", BOTH_PASS)
def test_benign_text_passes_in_both_profiles(terms, text, profile):
    assert giveaway_hits(text, terms, ATTACK_IDS, profile=profile) == []


def test_ot_after_the_word_stoerung_is_not_the_compound(terms):
    assert giveaway_hits("Störung in der OT", terms, (), profile="veiled") == []
    assert giveaway_hits("Störung in der OT", terms, (), profile="story") == []
    # With the attack id 'ot' the bare token hits in the veiled profile (no exceptions there), not in the story profile.
    assert giveaway_hits("Störung in der OT", terms, ATTACK_IDS, profile="veiled") == ["ot"]
    assert giveaway_hits("Störung in der OT", terms, ATTACK_IDS, profile="story") == []


def test_ot_stoerung_stays_banned_in_the_story_profile(terms):
    assert giveaway_hits("OT-Störung im Werk", terms, ATTACK_IDS, profile="story")


def test_an_unknown_profile_raises(terms):
    with pytest.raises(ValueError):
        giveaway_hits("x", terms, ATTACK_IDS, profile="other")


@pytest.mark.parametrize(
    "text",
    [
        "Ransomware",
        "Verschlüsselung",
        "verschlüsselt",
        "Lösegeld",
        "Erpressung",
        "Phishing",
        "Emotet",
        "OT-Störung",
        "SPS",
        "Sinumerik",
        "Sinumerik-Schwachstelle",
        "Exfiltration",
        "Datendiebstahl",
        "Darknet",
        "APT",
        "ransomware",
        "ot",
        "exfil",
    ],
)
def test_every_d13b_term_hits_in_the_veiled_profile(terms, text):
    assert giveaway_hits(text, terms, ATTACK_IDS, profile="veiled")


def test_the_terms_file_is_pinned_to_the_decisions(terms):
    assert terms.substrings == (
        "ransomware", "verschlüssel", "verschluessel", "lösegeld", "loesegeld", "erpress",
        "phishing", "emotet", "exfil", "datendiebstahl", "darknet", "sinumerik",
    )
    assert terms.tokens == ("sps", "apt")
    assert terms.compounds == (("ot", "stör"), ("ot", "stoer"))
    assert terms.story_exception_tokens == ("ot",)
    assert terms.story_exception_substrings == ("erpress",)


def test_the_mini_terms_equal_the_real_terms(terms):
    assert load_giveaway_terms(MINI_CONTENT_DIR / "giveaway_terms.toml") == terms


def test_hidden_characters_do_not_hide_a_term(terms):
    assert giveaway_hits("Ran­somware", terms, ATTACK_IDS, profile="veiled")
    assert giveaway_hits("Ran​som‍ware", terms, ATTACK_IDS, profile="veiled")
    assert giveaway_hits("Phi﻿shing", terms, ATTACK_IDS, profile="veiled")


def test_decomposed_umlauts_are_matched(terms):
    assert giveaway_hits("Verschlüsselung", terms, ATTACK_IDS, profile="veiled")


def test_normalization_keeps_the_sharp_s_and_translates_dashes():
    assert normalize_for_matching("STRASSE Straße") == "strasse straße"
    assert normalize_for_matching("a‐b‑c‒d–e—f―g−h") == "a-b-c-d-e-f-g-h"


def test_hits_are_sorted_matched_terms(terms):
    assert giveaway_hits("Phishing und Ransomware", terms, ATTACK_IDS, profile="veiled") == ["phishing", "ransomware"]


def _content(path):
    return load_texts(path / "texte.toml"), load_giveaway_terms(path / "giveaway_terms.toml")


@pytest.mark.parametrize(
    "config_path, content_dir",
    [pytest.param(MINI, MINI_CONTENT_DIR, id="mini"), pytest.param(CONFIG_PATH, CONTENT_DIR, id="real")],
)
def test_check_giveaway_is_clean_on_the_content(config_path, content_dir):
    cfg = load_config(config_path)
    texts, terms = _content(content_dir)
    assert check_giveaway(cfg, texts, terms) == []


def _mutated(mutate):
    texts, terms = _content(MINI_CONTENT_DIR)
    data = copy.deepcopy(texts.data)
    mutate(data)
    return load_config(MINI), Texts(data), terms


def _codes(issues):
    return sorted((issue.code, issue.path) for issue in issues)


def test_a_veiled_title_naming_an_attack_fails():
    cfg, texts, terms = _mutated(lambda d: d["attacks"]["ransomware"]["veiled"].update(title="Angriff Ransomware"))
    assert _codes(check_giveaway(cfg, texts, terms)) == [("texts.giveaway", "attacks.ransomware.veiled.title")]


def test_a_veiled_title_with_ot_fails_without_exceptions():
    cfg, texts, terms = _mutated(lambda d: d["attacks"]["ot"]["veiled"].update(title="Angriff OT"))
    assert _codes(check_giveaway(cfg, texts, terms)) == [("texts.giveaway", "attacks.ot.veiled.title")]


def test_the_message_names_the_hits():
    cfg, texts, terms = _mutated(lambda d: d["attacks"]["ot"]["veiled"].update(title="Angriff Phishing"))
    (issue,) = check_giveaway(cfg, texts, terms)
    assert issue.level == "error" and "phishing" in issue.message


def test_an_event_narrative_naming_a_technique_fails():
    cfg, texts, terms = _mutated(lambda d: d["events"]["sparprogramm"].update(narrative="Eine Phishing-Welle trifft euch."))
    assert _codes(check_giveaway(cfg, texts, terms)) == [("texts.giveaway", "events.sparprogramm.narrative")]


def test_an_event_narrative_with_erpresser_passes_under_the_story_profile():
    cfg, texts, terms = _mutated(lambda d: d["events"]["sparprogramm"].update(narrative="Erpresser legen Zulieferer lahm."))
    assert check_giveaway(cfg, texts, terms) == []


def test_a_final_event_rule_naming_an_attack_fails():
    cfg, texts, terms = _mutated(lambda d: d["final_events"]["budget_review"].update(rule="Nach der Ransomware prüft ihr das Restbudget."))
    assert _codes(check_giveaway(cfg, texts, terms)) == [("texts.giveaway", "final_events.budget_review.rule")]


def test_a_config_event_name_naming_an_attack_fails():
    cfg, texts, terms = _mutated(lambda d: None)
    events = {wave: list(items) for wave, items in cfg.events.items()}
    events[2][0] = dataclasses.replace(events[2][0], name="Ransomware-Sparprogramm")
    cfg = dataclasses.replace(cfg, events=events)
    assert _codes(check_giveaway(cfg, texts, terms)) == [("texts.giveaway", "events.sparprogramm.name (config)")]


def test_a_final_event_config_name_naming_an_attack_fails():
    cfg, texts, terms = _mutated(lambda d: None)
    finals = [dataclasses.replace(cfg.final_events[0], name="Phishing Review")]
    cfg = dataclasses.replace(cfg, final_events=finals)
    assert _codes(check_giveaway(cfg, texts, terms)) == [("texts.giveaway", "final_events.budget_review.name (config)")]


def test_measure_texts_are_not_giveaway_linted():
    cfg, texts, terms = _mutated(lambda d: d["measures"]["M6"].update(focus="Phishing abwehren"))
    assert check_giveaway(cfg, texts, terms) == []


def test_revealed_texts_may_name_the_attack():
    def mutate(data):
        data["attacks"]["ransomware"]["revealed"]["narrative"] = "Ransomware verschlüsselt eure Daten."

    cfg, texts, terms = _mutated(mutate)
    assert check_giveaway(cfg, texts, terms) == []


def test_check_texts_includes_the_giveaway_issues():
    content = load_content(MINI_CONTENT_DIR)
    data = copy.deepcopy(content.texts.data)
    data["attacks"]["ot"]["veiled"]["title"] = "Angriff Darknet"
    broken = dataclasses.replace(content, texts=Texts(data))
    issues = check_texts(load_config(MINI), broken)
    assert ("texts.giveaway", "attacks.ot.veiled.title") in _codes(issues)


def test_the_loaded_content_carries_the_terms():
    assert isinstance(load_content(CONTENT_DIR).terms, GiveawayTerms)


def test_the_real_content_passes_the_cli(capsys):
    assert main(["texts", "--config", str(CONFIG_PATH), "--content-dir", str(CONTENT_DIR)]) == 0
    assert "0 Fehler, 0 Warnung(en)" in capsys.readouterr().out


def test_the_cli_fails_on_a_giveaway_in_a_veiled_title(tmp_path, capsys):
    source = (MINI_CONTENT_DIR / "texte.toml").read_text(encoding="utf-8")
    broken = source.replace('[attacks.ransomware.veiled]\ntitle = "Angriff"', '[attacks.ransomware.veiled]\ntitle = "Ransomware"', 1)
    assert broken != source
    (tmp_path / "texte.toml").write_text(broken, encoding="utf-8", newline="\n")
    for name in ("digit_allowlist.toml", "giveaway_terms.toml"):
        (tmp_path / name).write_text((MINI_CONTENT_DIR / name).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    code = main(["texts", "--config", str(MINI), "--content-dir", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 1
    assert "ERROR texts.giveaway attacks.ransomware.veiled.title" in out
