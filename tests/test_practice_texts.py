"""Text coverage and lints of the Welle 0 practice story (FLOW-01, D-12, D-16, T-05-50).

The practice texts live under `practice.*` in content/texte.toml. They are required exactly when the config carries a
practice block, they are scanned with the story giveaway profile, and the digit lint stays strict on them.
"""
import copy

import pytest

from planspiel.config import load_config
from planspiel.texts import (
    Texts,
    check_coverage,
    check_digits,
    check_giveaway,
    check_texts,
    giveaway_hits,
    load_content,
    load_texts,
    required_keys,
)
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
ATTACK_IDS = ("ransomware", "ot", "exfil")
PRACTICE_KEYS = (
    "practice.title",
    "practice.intro",
    "practice.narrative",
    "practice.cia_rationale",
    "practice.case_1",
    "practice.case_2",
    "practice.case_3",
    "practice.selection_title",
    "practice.event_result",
    "practice.tracking_title",
)


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def content():
    return load_content(CONTENT_DIR)


def _with(content, dotted, value):
    data = copy.deepcopy(content.texts.data)
    *parents, last = dotted.split(".")
    node = data
    for part in parents:
        node = node.setdefault(part, {})
    node[last] = value
    return Texts(data)


def test_required_keys_list_every_practice_key(cfg):
    keys = required_keys(cfg)
    assert set(PRACTICE_KEYS) <= keys
    for bonus in cfg.practice.wave.bonus_measures:
        assert f"practice.bonus_reasons.{bonus.measure}" in keys
    assert "practice.event.narrative" in keys
    for tier in cfg.practice.event.params["tiers"]:
        assert f"practice.event.tier_labels.{tier}" in keys


def test_the_mini_config_has_no_practice_keys():
    mini = load_config(MINI)
    assert mini.practice is None
    assert not [key for key in required_keys(mini) if key.startswith("practice")]


def test_the_real_texts_cover_the_practice_keys(cfg, content):
    issues = [issue for issue in check_coverage(cfg, content.texts) if issue.path.startswith("practice")]
    assert issues == []


def test_every_text_check_passes_on_the_real_content(cfg, content):
    assert [issue for issue in check_texts(cfg, content) if issue.level == "error"] == []


@pytest.mark.parametrize("word", ["Phishing", "Datendiebstahl", "Ransomware", "Lösegeld", "Darknet", "Verschlüsselung"])
def test_the_story_giveaway_scan_covers_the_practice_texts(cfg, content, word):
    texts = _with(content, "practice.narrative", f"Ein Vorfall mit {word} im Büro.")
    issues = check_giveaway(cfg, texts, content.terms)
    assert [(issue.code, issue.path) for issue in issues] == [("texts.giveaway", "practice.narrative")]


def test_the_giveaway_scan_reaches_nested_practice_texts(cfg, content):
    texts = _with(content, "practice.event.tier_labels.0", "Phishing bleibt unbemerkt")
    issues = check_giveaway(cfg, texts, content.terms)
    assert [issue.path for issue in issues] == ["practice.event.tier_labels.0"]


@pytest.mark.parametrize("key", ["practice.narrative", "practice.bonus_reasons.M9", "practice.event.narrative"])
def test_the_digit_lint_is_strict_on_the_practice_texts(content, key):
    texts = _with(content, key, "Nach 3 Stunden war alles wieder da.")
    issues = check_digits(texts, content.allowlist)
    assert [(issue.code, issue.path) for issue in issues] == [("texts.digit", key)]


def test_the_practice_texts_also_pass_the_stricter_veiled_profile(cfg, content):
    """No domain word of a real attack (not even OT or Erpress*), so the practice hints at none (T-05-50)."""
    for key, text in content.texts.strings("practice"):
        assert giveaway_hits(text, content.terms, ATTACK_IDS, profile="veiled") == [], key


def test_the_mini_content_stays_free_of_practice_texts():
    assert not load_texts(MINI_CONTENT_DIR / "texte.toml").has("practice")
