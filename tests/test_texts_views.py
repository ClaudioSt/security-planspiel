"""Verhüllte und enthüllte Angriffstexte, generierte Titel und zielgruppenbezogene Sichten (VEIL-01, D-13, D-23, D-26)."""
import dataclasses
import re
import unicodedata

import pytest

from planspiel.cli import main
from planspiel.config import load_config
from planspiel.texts import (
    PreAttackView,
    RevealView,
    Texts,
    attack_title,
    check_coverage,
    load_texts,
    required_keys,
)
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    return load_config(config_path), load_texts(content_dir / "texte.toml")


def _nfc_lower(text: str) -> str:
    return unicodedata.normalize("NFC", text).lower()


def _reversed_waves(cfg):
    waves = [dataclasses.replace(wave, wave_id=number) for number, wave in enumerate(reversed(cfg.waves), start=1)]
    return dataclasses.replace(cfg, waves=waves)


def test_required_keys_contain_a_veiled_title_for_every_attack(loaded):
    cfg, _ = loaded
    keys = required_keys(cfg)
    for attack_id in cfg.attacks:
        assert f"attacks.{attack_id}.veiled.title" in keys


def test_real_veiled_titles_are_the_bare_word_without_a_digit():
    texts = load_texts(CONTENT_DIR / "texte.toml")
    cfg = load_config(CONFIG_PATH)
    for attack_id in cfg.attacks:
        assert texts.get(f"attacks.{attack_id}.veiled.title") == "Angriff"


def test_real_and_mini_content_are_fully_covered(loaded):
    cfg, texts = loaded
    assert check_coverage(cfg, texts) == []


def test_attack_titles_are_generated_from_the_position():
    texts = load_texts(CONTENT_DIR / "texte.toml")
    assert attack_title(texts, "ransomware", 1) == "Angriff 1"
    assert attack_title(texts, "ransomware", 1, revealed=True) == "Angriff 1: Ransomware"
    assert attack_title(texts, "ot", 3, revealed=True) == "Angriff 3: OT-Störung"
    assert attack_title(texts, "exfil", 2, revealed=True) == "Angriff 2: Datenexfiltration"


def test_a_reordered_wave_list_changes_the_titles_without_a_text_edit(loaded):
    cfg, texts = loaded
    reordered = _reversed_waves(cfg)
    assert [wave.attack_id for wave in reordered.waves][0] == "exfil"
    pre, reveal = PreAttackView(reordered, texts), RevealView(reordered, texts)
    first = reordered.waves[0]
    assert pre.attack_title(first) == "Angriff 1"
    assert reveal.attack_title(first) == "Angriff 1: Datenexfiltration"
    last = reordered.waves[-1]
    assert reveal.attack_title(last) == f"Angriff {len(reordered.waves)}: Ransomware"


def test_pre_attack_view_serves_veiled_titles_by_wave_position(loaded):
    cfg, texts = loaded
    view = PreAttackView(cfg, texts)
    assert [view.attack_title(wave) for wave in cfg.waves] == [f"Angriff {wave.wave_id}" for wave in cfg.waves]


def test_reveal_view_serves_revealed_titles_and_attack_texts(loaded):
    cfg, texts = loaded
    view = RevealView(cfg, texts)
    names = {"ransomware": "Ransomware", "ot": "OT-Störung", "exfil": "Datenexfiltration"}
    for wave in cfg.waves:
        assert view.attack_title(wave) == f"Angriff {wave.wave_id}: {names[wave.attack_id]}"
    ransomware = view.attack("ransomware")
    assert ransomware["name"] == "Ransomware"
    assert ransomware["narrative"] == texts.get("attacks.ransomware.revealed.narrative")
    assert ransomware["cia_rationale"] == texts.get("attacks.ransomware.revealed.cia_rationale")
    assert ransomware["cases"] == [
        texts.get("attacks.ransomware.revealed.case_1"),
        texts.get("attacks.ransomware.revealed.case_2"),
        texts.get("attacks.ransomware.revealed.case_3"),
    ]
    assert ransomware["bonus_reasons"]["M4"] == "Backup ermöglicht schnelle Wiederherstellung"
    assert set(view.attack("ot")) == {"name", "narrative", "cia_rationale", "cases", "bonus_reasons"}


def test_pre_attack_view_serves_measures_events_and_prewave_sheets(loaded):
    cfg, texts = loaded
    view = PreAttackView(cfg, texts)
    measure = view.measure("M1")
    assert measure["focus"] == texts.get("measures.M1.focus")
    assert measure["description"] == texts.get("measures.M1.description")
    assert measure["levels_desc"][1] == texts.get("measures.M1.levels_desc.1")
    assert measure["levels_simple"][3] == texts.get("measures.M1.levels_simple.3")
    assert view.event("kurswechsel")["narrative"] == texts.get("events.kurswechsel.narrative")
    assert view.event("budget_review")["rule"] == texts.get("final_events.budget_review.rule")
    for name in ("budget", "ros", "backup_recovery", "labels"):
        assert view.sheet(name)
    assert view.sheet("labels")["measure"] == "Maßnahme"


def test_pre_attack_view_refuses_the_attack_worksheet(loaded):
    cfg, texts = loaded
    with pytest.raises(KeyError):
        PreAttackView(cfg, texts).sheet("angriff")


def test_reveal_view_serves_every_sheet(loaded):
    cfg, texts = loaded
    view = RevealView(cfg, texts)
    assert view.sheet("angriff")["case_3_hint"] == texts.get("sheets.angriff.case_3_hint")
    assert view.sheet("budget")["title"] == "Budget"


def test_pre_attack_view_has_no_reveal_member(loaded):
    cfg, texts = loaded
    view = PreAttackView(cfg, texts)
    assert [name for name in dir(view) if "reveal" in name.lower()] == []


def test_the_mini_and_real_titles_follow_the_config_wave_order():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    assert [wave.attack_id for wave in cfg.waves] == ["ransomware", "ot", "exfil"]
    assert PreAttackView(cfg, texts).attack_title(cfg.waves[2]) == "Angriff 3"


def _leaks(cfg, texts):
    reachable = [_nfc_lower(text) for text in PreAttackView(cfg, texts).strings()]
    assert reachable
    revealed_names = [str(texts.get(f"attacks.{attack_id}.revealed.name")) for attack_id in cfg.attacks]
    reasons = [text for key, text in texts.strings() if ".revealed.bonus_reasons." in key]
    assert reasons
    banned = [_nfc_lower(name) for name in revealed_names]
    banned += [attack_id for attack_id in cfg.attacks if len(re.findall(r"[^\W\d_]", attack_id)) >= 5]
    banned += [_nfc_lower(reason) for reason in reasons]
    return [(term, text) for text in reachable for term in banned if term in text]


# Scope of this leak test: it guards the MEASURE texts, which the giveaway lint deliberately skips
# (D-06: a measure text may name what it defends against, but it must not name an attack). It checks that
# nothing the pre-attack view can reach contains a revealed attack name, an attack id of five or more
# letters or a bonus reason, so a later measure edit that names an attack fails here by design. The id
# "exfil" is substring-matched on purpose (the same rule giveaway_hits applies to ids of five or more
# letters), which is stricter than a whole-token match.
def test_pre_attack_view_cannot_reach_a_revealed_name_or_bonus_reason(loaded):
    cfg, texts = loaded
    assert _leaks(cfg, texts) == []


@pytest.mark.parametrize(
    "focus, term",
    [
        ("Schutz vor Datenexfiltration", "datenexfiltration"),
        ("Schutz vor Exfil-Versuchen", "exfil"),
        ("Gegen OT-STÖRUNG gerüstet", "ot-störung"),
        ("Gegen Ransomware gerüstet", "ransomware"),
        ("Backup ermöglicht schnelle Wiederherstellung", "backup ermöglicht schnelle wiederherstellung"),
    ],
)
def test_leak_test_catches_a_revealed_term_in_a_measure_text(loaded, focus, term):
    cfg, texts = loaded
    measures = {key: dict(value) for key, value in texts.data["measures"].items()}
    measures["M1"]["focus"] = focus
    mutated = Texts({**texts.data, "measures": measures})
    assert (term, _nfc_lower(focus)) in _leaks(cfg, mutated)


def test_pre_attack_strings_cover_every_text_family(loaded):
    cfg, texts = loaded
    strings = PreAttackView(cfg, texts).strings()
    assert str(texts.get("measures.M1.focus")) in strings
    assert str(texts.get("events.kurswechsel.narrative")) in strings
    assert str(texts.get("final_events.budget_review.rule")) in strings
    assert str(texts.get("sheets.budget.title")) in strings
    assert str(texts.get("sheets.labels.measure")) in strings
    for wave in cfg.waves:
        assert f"Angriff {wave.wave_id}" in strings
    assert str(texts.get("sheets.angriff.case_3_hint")) not in strings


def test_leak_test_catches_a_name_in_a_measure_text(loaded):
    cfg, texts = loaded
    data = {key: value for key, value in texts.data.items()}
    measures = {key: dict(value) for key, value in data["measures"].items()}
    measures["M1"]["focus"] = "Schutz vor Datenexfiltration"
    data["measures"] = measures
    strings = [_nfc_lower(text) for text in PreAttackView(cfg, Texts(data)).strings()]
    assert any("datenexfiltration" in text for text in strings)


def test_the_texts_cli_still_passes_on_the_mini_content(capsys):
    code = main(["texts", "--config", str(MINI), "--content-dir", str(MINI_CONTENT_DIR)])
    assert code == 0
    assert "0 Fehler, 0 Warnung(en)" in capsys.readouterr().out
