"""Ziffern-Lint (strikt, mit geprüfter Allowlist) und Story-Mechanik-Lint (D-10..D-12, D-15)."""
import copy

import pytest

from planspiel.config import load_config
from planspiel.texts import (
    AllowEntry,
    Texts,
    check_digits,
    check_story_mechanics,
    check_texts,
    load_allowlist,
    load_content,
    load_texts,
)
from tests.support import MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
ALLOW_KEY = "measures.M2.levels_desc.1"


def _data():
    return copy.deepcopy(load_texts(MINI_CONTENT_DIR / "texte.toml").data)


def _allowlist():
    return load_allowlist(MINI_CONTENT_DIR / "digit_allowlist.toml")


def _put(data, dotted, value):
    *parents, last = dotted.split(".")
    node = data
    for part in parents:
        node = node.setdefault(part, {})
    node[last] = value


def _codes(issues):
    return sorted((issue.code, issue.path) for issue in issues)


def test_mini_fixture_with_its_allowlist_is_clean():
    assert check_digits(load_texts(MINI_CONTENT_DIR / "texte.toml"), _allowlist()) == []


def test_digit_outside_story_fails():
    data = _data()
    _put(data, "measures.M1.focus", "Level 3 Schutz")
    assert _codes(check_digits(Texts(data), _allowlist())) == [("texts.digit", "measures.M1.focus")]


def test_the_same_token_at_another_key_still_fails():
    data = _data()
    _put(data, "measures.M2.levels_simple.1", "30 Tage Aufbewahrung")
    assert _codes(check_digits(Texts(data), _allowlist())) == [("texts.digit", "measures.M2.levels_simple.1")]


def test_digit_in_a_list_element_fails():
    data = _data()
    _put(data, "measures.M1.focus", ["gut", "b1"])
    assert _codes(check_digits(Texts(data), _allowlist())) == [("texts.digit", "measures.M1.focus")]


def test_story_is_exempt_from_the_digit_lint():
    data = _data()
    _put(data, "story.steckbrief.kurzprofil.text", "ca. 80 Mitarbeitende und 15 Mio. EUR Umsatz")
    assert check_digits(Texts(data), _allowlist()) == []


def test_german_number_words_pass():
    data = _data()
    _put(data, "measures.M1.focus", "drei Fertigungslinien und zwei Admins")
    assert check_digits(Texts(data), _allowlist()) == []


def test_vulgar_fraction_counts_as_a_digit():
    data = _data()
    _put(data, "measures.M1.focus", "½ Stunde")
    assert _codes(check_digits(Texts(data), _allowlist())) == [("texts.digit", "measures.M1.focus")]


def test_stale_entry_with_absent_token_fails():
    data = _data()
    _put(data, ALLOW_KEY, "Zentrale Protokolle")
    assert _codes(check_digits(Texts(data), _allowlist())) == [("texts.allowlist_stale", ALLOW_KEY)]


def test_stale_entry_with_missing_key_fails():
    allowlist = (AllowEntry(key="measures.M99.focus", token="30 Tage", why="Grund"),)
    issues = check_digits(load_texts(MINI_CONTENT_DIR / "texte.toml"), allowlist)
    assert ("texts.allowlist_stale", "measures.M99.focus") in _codes(issues)


def test_entry_without_reason_fails():
    allowlist = (AllowEntry(key=ALLOW_KEY, token="30 Tage", why="  "),)
    issues = check_digits(load_texts(MINI_CONTENT_DIR / "texte.toml"), allowlist)
    assert _codes(issues) == [("texts.allowlist_reason", ALLOW_KEY)]


STORY_KEY = "story.zeitungsartikel.aufmacher.text"


@pytest.mark.parametrize(
    "term", ["KZ", "Kundenzufriedenheit", "OPEX", "Init-Kosten", "Budget-Tier", "RoS", "E-Wert", "Level 2"]
)
def test_story_mechanics_vocabulary_fails(term):
    data = _data()
    _put(data, STORY_KEY, f"Es geht um {term} im Gespräch.")
    issues = check_story_mechanics(load_config(MINI), Texts(data))
    assert _codes(issues) == [("texts.story_mechanics", STORY_KEY)]


def test_plain_budget_word_is_allowed_in_story():
    data = _data()
    _put(data, STORY_KEY, "Wir hätten Budget für ein Beratungsprojekt")
    assert check_story_mechanics(load_config(MINI), Texts(data)) == []


@pytest.mark.parametrize("amount", ["350.000", "400.000", "450.000"])
def test_budget_tier_amount_fails_in_story(amount):
    data = _data()
    _put(data, STORY_KEY, f"Das Budget liegt bei {amount} Euro.")
    issues = check_story_mechanics(load_config(MINI), Texts(data))
    assert _codes(issues) == [("texts.story_mechanics", STORY_KEY)]


def test_mechanics_words_outside_story_are_not_checked():
    data = _data()
    _put(data, "measures.M1.focus", "KZ und OPEX und RoS")
    assert check_story_mechanics(load_config(MINI), Texts(data)) == []


def test_check_texts_on_the_mini_content_is_clean():
    assert check_texts(load_config(MINI), load_content(MINI_CONTENT_DIR)) == []
