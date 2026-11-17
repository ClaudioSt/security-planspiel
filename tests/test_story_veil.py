"""Verhüllte Story-Dokumente und die echte Hinweis-Matrix (VEIL-03, D-13, D-16, D-18, D-20, D-21)."""
import copy

import pytest

from planspiel.cli import main
from planspiel.config import load_config
from planspiel.texts import (
    STORY_DOCS,
    FacilitatorView,
    PreAttackView,
    Texts,
    check_clues,
    check_giveaway,
    check_texts,
    giveaway_hits,
    load_clues,
    load_content,
    load_giveaway_terms,
    load_texts,
)
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"

REAL_CFG = load_config(CONFIG_PATH)
REAL_CONTENT = load_content(CONTENT_DIR)
REAL_TEXTS = REAL_CONTENT.texts

MINI_CFG = load_config(MINI)
MINI_TERMS = load_giveaway_terms(MINI_CONTENT_DIR / "giveaway_terms.toml")
MINI_TEXTS = load_texts(MINI_CONTENT_DIR / "texte.toml")


@pytest.fixture
def real_clues():
    return load_clues(CONTENT_DIR / "clues.toml")


def _with_story_text(key_path, value):
    data = copy.deepcopy(MINI_TEXTS.data)
    node = data
    for part in key_path[:-1]:
        node = node[part]
    node[key_path[-1]] = value
    return Texts(data)


def _story_giveaways(cfg, texts, terms):
    return [issue for issue in check_giveaway(cfg, texts, terms) if issue.path.startswith("story.")]


def test_the_real_story_documents_contain_no_giveaway_term():
    hits = {}
    for doc in STORY_DOCS:
        for key, text in REAL_TEXTS.strings(f"story.{doc}"):
            found = giveaway_hits(text, REAL_CONTENT.terms, tuple(REAL_CFG.attacks), profile="story")
            if found:
                hits.setdefault(doc, []).append((key, found))
    report = "\n".join(f"{doc}: {entries}" for doc, entries in hits.items())
    assert hits == {}, f"Giveaway-Treffer in den Story-Dokumenten:\n{report}"


def test_check_giveaway_reports_nothing_on_the_real_story():
    assert _story_giveaways(REAL_CFG, REAL_TEXTS, REAL_CONTENT.terms) == []


def test_the_giveaway_check_scans_every_story_document():
    hits_by_doc = {}
    for doc in STORY_DOCS:
        data = copy.deepcopy(MINI_TEXTS.data)
        data["story"][doc]["doc_title"] = "Eine Ransomware-Meldung"
        issues = _story_giveaways(MINI_CFG, Texts(data), MINI_TERMS)
        hits_by_doc[doc] = [issue.path for issue in issues]
    assert hits_by_doc == {doc: [f"story.{doc}.doc_title"] for doc in STORY_DOCS}


@pytest.mark.parametrize(
    "sentence",
    [
        "Office-IT und OT/Produktion nutzen dasselbe LAN (kein separates OT-Netz)",
        "Die Erpresser-Software sperrte die Büro-Daten.",
        "Erpresser legen Zulieferer tagelang lahm",
    ],
)
def test_the_story_profile_honours_the_domain_exceptions(sentence):
    texts = _with_story_text(("story", "zeitungsartikel", "aufmacher", "text"), sentence)
    assert _story_giveaways(MINI_CFG, texts, MINI_TERMS) == []


@pytest.mark.parametrize(
    "sentence",
    [
        "Eine OT-Störung legt die Halle lahm.",
        "Die Daten wurden verschlüsselt.",
        "Die Angreifer forderten Lösegeld.",
        "Eine Phishing-Mail wurde geöffnet.",
        "12 CNC-Steuerungen (Sinumerik/Heidenhain)",
    ],
)
def test_the_story_profile_still_rejects_real_giveaways(sentence):
    texts = _with_story_text(("story", "zeitungsartikel", "aufmacher", "text"), sentence)
    issues = _story_giveaways(MINI_CFG, texts, MINI_TERMS)
    assert [(issue.code, issue.path) for issue in issues] == [
        ("texts.giveaway", "story.zeitungsartikel.aufmacher.text")
    ]


def test_a_story_list_element_with_a_giveaway_is_found():
    texts = _with_story_text(("story", "steckbrief", "produkte", "bullets"), ["Präzisions-Getriebeteile", "Lösegeld"])
    issues = _story_giveaways(MINI_CFG, texts, MINI_TERMS)
    assert [issue.path for issue in issues] == ["story.steckbrief.produkte.bullets"]


@pytest.mark.parametrize("doc", STORY_DOCS)
def test_the_pre_attack_view_returns_every_story_document(doc):
    view = PreAttackView(REAL_CFG, REAL_TEXTS)
    story = view.story(doc)
    assert story == REAL_TEXTS.subtree(f"story.{doc}")
    assert story["doc_title"] == REAL_TEXTS.get(f"story.{doc}.doc_title")


def test_the_pre_attack_view_story_is_a_copy():
    view = PreAttackView(REAL_CFG, REAL_TEXTS)
    view.story("steckbrief")["doc_title"] = "verändert"
    assert REAL_TEXTS.get("story.steckbrief.doc_title") != "verändert"


def test_an_unknown_story_document_raises_key_error():
    with pytest.raises(KeyError):
        PreAttackView(REAL_CFG, REAL_TEXTS).story("attacks")
    with pytest.raises(KeyError):
        PreAttackView(REAL_CFG, REAL_TEXTS).story("gibt_es_nicht")


def test_the_pre_attack_view_strings_include_every_story_string():
    strings = set(PreAttackView(REAL_CFG, REAL_TEXTS).strings())
    story = {text for _, text in REAL_TEXTS.strings("story")}
    assert story
    assert story <= strings


def test_no_revealed_name_or_bonus_reason_is_reachable_from_the_real_pre_wave_texts():
    strings = [text.lower() for text in PreAttackView(REAL_CFG, REAL_TEXTS).strings()]
    forbidden = [
        REAL_TEXTS.get(f"attacks.{attack_id}.revealed.name").lower() for attack_id in REAL_CFG.attacks
    ] + [text.lower() for key, text in REAL_TEXTS.strings("attacks") if ".bonus_reasons." in key]
    assert forbidden
    leaks = [(term, text) for term in forbidden for text in strings if term in text]
    assert leaks == []


def test_every_real_attack_has_two_clues_from_two_story_documents(real_clues):
    for wave in REAL_CFG.waves:
        clues = [clue for clue in real_clues if clue.attack == wave.attack_id]
        documents = {clue.source.split(".")[1] for clue in clues if clue.source.startswith("story.")}
        assert len(clues) >= 2, wave.attack_id
        assert len(documents) >= 2, wave.attack_id
        assert documents <= set(STORY_DOCS)


def test_the_real_clue_matrix_passes_the_check(real_clues):
    issues = check_clues(REAL_CFG, REAL_TEXTS, real_clues)
    assert [(issue.code, issue.path) for issue in issues] == []


def test_the_real_clue_matrix_covers_every_wave_in_order(real_clues):
    rows = FacilitatorView(REAL_CFG, REAL_TEXTS, real_clues).clue_matrix()
    titles = list(dict.fromkeys(row.title for row in rows))
    assert titles == [
        "Angriff 1: Ransomware",
        "Angriff 2: OT-Störung",
        "Angriff 3: Datenexfiltration",
    ]
    assert all(len(row.quote) >= 15 and row.why.strip() for row in rows)


def test_the_clues_cli_passes_on_the_real_content(capsys):
    code = main(["clues", "--config", str(CONFIG_PATH), "--content-dir", str(CONTENT_DIR)])
    out = capsys.readouterr().out
    assert code == 0
    for title in ("Angriff 1: Ransomware", "Angriff 2: OT-Störung", "Angriff 3: Datenexfiltration"):
        assert title in out
    assert "0 Fehler, 0 Warnung(en)" in out


def test_the_real_content_still_passes_the_full_texts_check():
    assert [(issue.code, issue.path) for issue in check_texts(REAL_CFG, REAL_CONTENT)] == []


def test_the_clues_stay_out_of_the_pre_wave_view_and_the_content_bundle():
    assert not hasattr(PreAttackView(REAL_CFG, REAL_TEXTS), "clues")
    assert not hasattr(REAL_CONTENT, "clues")
