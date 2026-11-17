"""RISK-04 (D-12, D-20): the reality-check line of the attack worksheets.

Every real attack worksheet ends with one line asking which risk of the team's register the attack hit. The Welle 0
practice sheet and the mini fixture carry no register, so they carry no line.
"""
import pytest

from planspiel import audience, practice, veil
from planspiel.config import load_config
from planspiel.printmodel import Box, build_attack_sheets
from planspiel.texts import REALITY_KEYS, load_content, load_texts, required_keys
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
QUESTION = "sheets.angriff.reality_question"
HINT = "sheets.angriff.reality_hint"


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, texts, build_attack_sheets(cfg, texts)


def _strings(line):
    return [part for part in line if isinstance(part, str)]


def _boxes(line):
    return [part for part in line if isinstance(part, Box)]


def _text(texts, key):
    return texts.get(key)


def test_every_real_sheet_has_a_reality_line_with_one_box(real):
    _, texts, sheets = real
    assert sheets
    for sheet in sheets:
        assert sheet.reality_line is not None, sheet.job
        assert len(_boxes(sheet.reality_line)) == 1, sheet.job
        joined = "".join(_strings(sheet.reality_line))
        assert _text(texts, QUESTION) in joined, sheet.job
        assert _text(texts, HINT) in joined, sheet.job


def test_the_question_names_the_register_and_the_hint_names_the_answers(real):
    _, texts, _ = real
    assert _text(texts, "sheets.register.title") in _text(texts, QUESTION)
    assert _text(texts, "sheets.register.risk_prefix") in _text(texts, HINT)
    assert "nicht im Register" in _text(texts, HINT)


def test_the_reality_label_is_the_one_the_register_review_hint_names(real):
    _, texts, _ = real
    label = _text(texts, QUESTION).split(":", 1)[0]
    assert label == "Realitätscheck"
    assert label in _text(texts, "sheets.register.review_hint")


def test_the_reality_line_is_attack_neutral(real):
    cfg, texts, sheets = real
    ctx = veil.context(cfg, texts, load_content(CONTENT_DIR).terms)
    for sheet in sheets:
        for text in _strings(sheet.reality_line):
            assert veil.name_hits(text, ctx, audience.PROFILE_STORY) == [], (sheet.job, text)


def test_the_reality_text_has_no_digit(real):
    _, texts, _ = real
    for key in REALITY_KEYS:
        assert not any(char.isdigit() for char in _text(texts, key)), key


def test_the_practice_config_has_no_register_and_its_sheet_no_reality_line(real):
    cfg, texts, _ = real
    assert practice.practice_config(cfg).risk_matrix is None
    document = practice.build_practice_document(cfg, texts)
    assert document.sheet.reality_line is None


def test_the_mini_config_has_no_reality_line_and_needs_no_reality_texts():
    cfg = load_config(MINI)
    texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    assert all(sheet.reality_line is None for sheet in build_attack_sheets(cfg, texts))
    assert QUESTION not in required_keys(cfg)
    assert HINT not in required_keys(cfg)


def test_the_real_config_requires_both_reality_texts(real):
    cfg, _, _ = real
    assert {QUESTION, HINT} <= required_keys(cfg)
    assert set(REALITY_KEYS) == {QUESTION, HINT}
