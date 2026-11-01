"""Story document models built from `[story.*]`: nothing dropped, headings keep their case, every clue quote present (PRINT-12).

No TeX is involved here; the templates and the built PDFs are covered in tests/test_story_render.py and
tests/test_story_pdf.py.
"""
import ast
import copy
import dataclasses
import unicodedata
from collections import Counter

import pytest

from planspiel import audience, texbuild
from planspiel.config import load_config
from planspiel.printmodel import PrintModelError
from planspiel.story import (
    STORY_JOBS,
    Mail,
    Section,
    Steckbrief,
    Zeitungsartikel,
    build_story_documents,
)
from planspiel.texts import STORY_DOCS, PreAttackView, Texts, _clue_document, load_clues, load_content
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]
EXPECTED_JOBS = {
    "steckbrief": "spieler-unternehmenssteckbrief",
    "zeitungsartikel": "spieler-zeitungsartikel",
    "anfrage_mail": "spieler-anfrage-mail",
    "audit_mail": "spieler-audit-mail",
}


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    cfg = load_config(config_path)
    content = load_content(content_dir)
    return cfg, content.texts, build_story_documents(cfg, content.texts)


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    content = load_content(CONTENT_DIR)
    return cfg, content.texts, build_story_documents(cfg, content.texts)


def _by_doc(documents):
    return dict(zip(STORY_DOCS, documents))


def _leaf_strings(node) -> list[str]:
    if isinstance(node, str):
        return [node]
    if isinstance(node, list):
        return [item for item in node if isinstance(item, str)]
    return [text for value in node.values() for text in _leaf_strings(value)]


def _headings(sections) -> list[str]:
    found = []
    for section in sections:
        found.append(section.heading)
        found.extend(_headings(section.subsections))
    return found


def _modified(texts, path, value):
    data = copy.deepcopy(texts.data)
    node = data
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = value
    return Texts(data)


# ---- jobs and types -----------------------------------------------------------------------------------------------


def test_the_story_jobs_are_the_four_prewave_jobs_in_story_doc_order():
    assert STORY_JOBS == EXPECTED_JOBS
    assert tuple(STORY_JOBS) == STORY_DOCS
    for job in STORY_JOBS.values():
        assert audience.audience_of(job) == audience.PREWAVE
        assert audience.scan_profile(job) == audience.PROFILE_STORY


def test_the_models_are_frozen_and_carry_the_story_jobs(loaded):
    _, _, documents = loaded
    assert len(documents) == 4
    steckbrief, zeitung, anfrage, audit = documents
    assert isinstance(steckbrief, Steckbrief) and isinstance(zeitung, Zeitungsartikel)
    assert isinstance(anfrage, Mail) and isinstance(audit, Mail)
    assert [model.job for model in documents] == list(STORY_JOBS.values())
    with pytest.raises(dataclasses.FrozenInstanceError):
        steckbrief.job = "x"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        Section(heading="a").heading = "b"  # type: ignore[misc]


# ---- Steckbrief ---------------------------------------------------------------------------------------------------


def test_the_steckbrief_loses_no_string_of_its_toml_subtree(loaded):
    cfg, texts, documents = loaded
    steckbrief = documents[0]
    stored = Counter(_leaf_strings(PreAttackView(cfg, texts).story("steckbrief")))
    printed = Counter(steckbrief.printed_strings())
    title = texts.get("story.steckbrief.doc_title")
    assert steckbrief.title == title
    assert printed - Counter([title]) == stored - Counter([title])
    assert printed[title] >= 1


def test_the_real_steckbrief_keeps_the_toml_order_and_nests_the_it_ot_landscape(real):
    _, _, documents = real
    steckbrief = documents[0]
    assert [section.heading for section in steckbrief.sections] == [
        "Kurzprofil",
        "Produkte & Leistungen",
        "Standort & Organisation",
        "Wirtschaftliche Eckdaten",
        "Produktion & Betrieb",
        "IT-/OT-Landschaft",
        "Betriebs- & Service-Setup",
        "Abhängigkeiten",
    ]
    landscape = steckbrief.sections[5]
    assert landscape.paragraphs == () and landscape.bullets == ()
    assert [sub.heading for sub in landscape.subsections] == [
        "Office / Engineering",
        "OT / Produktion",
        "SaaS / Cloud / Externe Anwendungen",
    ]
    assert steckbrief.sections[0].paragraphs and not steckbrief.sections[0].bullets
    assert steckbrief.sections[1].bullets and not steckbrief.sections[1].paragraphs


# ---- Zeitungsartikel ----------------------------------------------------------------------------------------------


def test_the_newspaper_carries_masthead_header_ticker_and_footer(loaded):
    cfg, texts, documents = loaded
    zeitung = documents[1]
    story = PreAttackView(cfg, texts).story("zeitungsartikel")
    assert zeitung.masthead == story["doc_title"]
    assert zeitung.header_items == tuple(story.get("kopfzeile", ()))
    assert zeitung.ticker == tuple(story.get("ticker", ()))
    assert zeitung.footer_items == tuple(story.get("fusszeile", ()))


def test_the_newspaper_loses_no_string_of_its_toml_subtree(loaded):
    cfg, texts, documents = loaded
    zeitung = documents[1]
    stored = Counter(_leaf_strings(PreAttackView(cfg, texts).story("zeitungsartikel")))
    assert Counter(zeitung.printed_strings()) == stored


def test_the_real_newspaper_sections_and_images(real):
    _, _, documents = real
    zeitung = documents[1]
    assert [section.heading for section in zeitung.sections] == [
        "OEM VERSCHÄRFT SECURITY-ANFORDERUNGEN",
        "Erpresser legen Zulieferer tagelang lahm",
    ]
    meldung, bericht = zeitung.sections
    assert len(meldung.paragraphs) == 3 and meldung.caption.startswith("Symbolbild")
    assert bericht.dateline == "Kassel, 10.01.2026"
    assert bericht.lead.startswith("Ein mittelständischer Automotive Zulieferer")
    assert bericht.caption.startswith("Symbolbild")
    assert [sub.heading for sub in bericht.subsections] == ["DER ANGRIFF", "FOLGEN"]
    assert [len(sub.paragraphs) for sub in bericht.subsections] == [2, 2]


def test_the_newspaper_refers_to_its_images_only_through_the_asset_constants(loaded):
    _, _, documents = loaded
    zeitung = documents[1]
    assert zeitung.images == texbuild.ASSET_FILES
    placed = [section.image for section in zeitung.sections if section.image]
    assert placed == list(texbuild.ASSET_FILES)
    assert all(section.caption for section in zeitung.sections if section.image)
    assert all(not section.image for section in zeitung.sections if not section.caption)


def test_the_story_module_names_no_image_file_itself():
    source = (REPO_ROOT / "planspiel" / "story.py").read_text(encoding="utf-8")
    literals = [
        node.value for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    assert not [text for text in literals if text.lower().endswith((".png", ".jpg", ".jpeg", ".pdf"))]
    assert "ASSET_FILES" in source


def test_the_image_names_are_not_part_of_the_printed_strings(loaded):
    _, _, documents = loaded
    for name in texbuild.ASSET_FILES:
        assert name not in documents[1].printed_strings()


# ---- Mails --------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("doc", ["anfrage_mail", "audit_mail"])
def test_a_mail_takes_header_subject_salutation_and_lines_from_its_subtree(loaded, doc):
    cfg, texts, documents = loaded
    mail = _by_doc(documents)[doc]
    story = PreAttackView(cfg, texts).story(doc)
    labels = PreAttackView(cfg, texts).sheet("labels")
    assert mail.sender == story["kopf"]["von"]
    assert mail.recipient == story["kopf"]["an"]
    assert mail.subject == story["doc_title"]
    assert mail.salutation == story.get("anrede", {}).get("text", "")
    assert mail.closing_lines == tuple(story.get("gruss", {}).get("lines", ()))
    assert mail.footer_lines == tuple(story.get("fusszeile", {}).get("lines", ()))
    assert (mail.labels.sender, mail.labels.recipient, mail.labels.subject) == (
        labels["mail_from"],
        labels["mail_to"],
        labels["mail_subject"],
    )


def test_the_mail_header_labels_are_von_an_betreff(real):
    cfg, texts, documents = real
    labels = documents[2].labels
    assert (labels.sender, labels.recipient, labels.subject) == ("Von", "An", "Betreff")


@pytest.mark.parametrize("doc", ["anfrage_mail", "audit_mail"])
def test_a_mail_loses_no_string_of_its_toml_subtree(loaded, doc):
    cfg, texts, documents = loaded
    mail = _by_doc(documents)[doc]
    stored = Counter(_leaf_strings(PreAttackView(cfg, texts).story(doc)))
    labels = PreAttackView(cfg, texts).sheet("labels")
    label_strings = Counter([labels["mail_from"], labels["mail_to"], labels["mail_subject"]])
    assert Counter(mail.printed_strings()) - label_strings == stored


def test_the_real_mails_keep_their_sections_in_toml_order(real):
    _, _, documents = real
    anfrage, audit = documents[2], documents[3]
    assert [section.heading for section in anfrage.sections] == ["", "", "IHRE AUFGABE:", ""]
    assert anfrage.sections[2].bullets and anfrage.sections[2].paragraphs
    assert [section.heading for section in audit.sections] == [
        "",
        "ERWARTETE NACHWEISE:",
        "KONSEQUENZEN:",
        "UNTERSTÜTZUNG:",
    ]
    assert anfrage.sender == '"Dr. Thomas Weber" <t.weber@mechtech-gmbh.de>'
    assert audit.subject == "Information Security Assessment - Supplier Audit Q2/2026"


# ---- headings, clues and content errors ---------------------------------------------------------------------------


def test_headings_keep_their_stored_case(real):
    _, texts, documents = real
    stored = {text for key, text in texts.strings("story") if key.endswith(".heading") or key.endswith(".headline")}
    shown = {heading for model in documents for heading in _headings(getattr(model, "sections", ())) if heading}
    assert shown == stored
    assert "Kurzprofil" in shown and "DER ANGRIFF" in shown and "Erpresser legen Zulieferer tagelang lahm" in shown


def test_every_clue_quote_is_in_the_model_of_its_source_document(real):
    _, _, documents = real
    clues = load_clues(CONTENT_DIR / "clues.toml")
    assert len(clues) == (CONTENT_DIR / "clues.toml").read_text(encoding="utf-8").count("[[clue]]")
    by_doc = _by_doc(documents)
    for clue in clues:
        document = _clue_document(clue.source)
        assert document is not None and document.startswith("story."), clue.source
        printed = [unicodedata.normalize("NFC", text) for text in by_doc[document.removeprefix("story.")].printed_strings()]
        quote = unicodedata.normalize("NFC", clue.quote)
        assert any(quote in text for text in printed), (clue.source, clue.quote)


@pytest.mark.parametrize(
    "path, value",
    [
        (("story", "steckbrief", "kurzprofil", "bullets"), 5),
        (("story", "steckbrief", "kurzprofil", "unbekannt"), "Text"),
        (("story", "zeitungsartikel", "ticker"), "kein Liste"),
        (("story", "anfrage_mail", "kopf", "von"), ["liste"]),
        (("story", "audit_mail", "gruss", "lines"), [1, 2]),
    ],
)
def test_an_unexpected_story_value_stops_the_build(path, value):
    cfg = load_config(CONFIG_PATH)
    texts = _modified(load_content(CONTENT_DIR).texts, path, value)
    with pytest.raises(PrintModelError):
        build_story_documents(cfg, texts)


def test_a_second_level_of_subsections_stops_the_build():
    cfg = load_config(CONFIG_PATH)
    texts = _modified(
        load_content(CONTENT_DIR).texts,
        ("story", "steckbrief", "it_ot_landschaft", "ot_produktion", "unten"),
        {"heading": "zu tief", "text": "Text"},
    )
    with pytest.raises(PrintModelError, match="Ebene"):
        build_story_documents(cfg, texts)


def test_a_mail_without_a_header_stops_the_build():
    cfg = load_config(CONFIG_PATH)
    data = copy.deepcopy(load_content(CONTENT_DIR).texts.data)
    del data["story"]["anfrage_mail"]["kopf"]
    with pytest.raises(PrintModelError, match="kopf"):
        build_story_documents(cfg, Texts(data))


def test_a_newspaper_with_a_wrong_number_of_captions_stops_the_build():
    cfg = load_config(CONFIG_PATH)
    data = copy.deepcopy(load_content(CONTENT_DIR).texts.data)
    del data["story"]["zeitungsartikel"]["meldung_audit"]["caption"]
    with pytest.raises(PrintModelError, match="Bild"):
        build_story_documents(cfg, Texts(data))


def test_story_py_is_registered_as_a_prewave_model_module():
    from tests.test_veil_models import PREWAVE_MODULES

    assert "story.py" in PREWAVE_MODULES
