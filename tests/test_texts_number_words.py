"""Phase 7 prose lint: counts that config holds (waves, teams, persons, stages, blocks, documents) are never typed as number words; digits are already caught by `check_digits`.

Later plans append their prefixes to PHASE7_PREFIXES instead of writing their own check (07-04 sheets.debrief, 07-06 sheets.was_neu, 07-08 sheets.probelauf).
"""
import re

import pytest

from planspiel.texts import load_texts
from tests.support import CONTENT_DIR

NUMBER_WORDS = ("eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf")
# (key, phrase) -> reason; a phrase is the matched number word as it stands in the text.
ALLOWED: dict[tuple[str, str], str] = {}
PHASE7_PREFIXES = (
    "sheets.ablauf", "sheets.debrief", "sheets.was_neu", "sheets.probelauf",
    "sheets.eventkarten.level_or_higher", "sheets.labels.event_after_wave", "sheets.register",
    "sheets.cheatsheet",
)

_PATTERN = re.compile(r"(?<![^\W\d_])(" + "|".join(NUMBER_WORDS) + r")(?![^\W\d_])", re.IGNORECASE)


@pytest.fixture(scope="module")
def texts():
    return load_texts(CONTENT_DIR / "texte.toml")


def _under(key: str, prefix: str) -> bool:
    return key == prefix or key.startswith(prefix + ".")


def _strings(texts, prefix):
    """Every (key, string) under the prefix; lists are walked by `Texts.strings`."""
    return [(key, text) for key, text in texts.strings() if _under(key, prefix)]


@pytest.mark.parametrize("prefix", PHASE7_PREFIXES)
def test_the_prefix_is_not_stale(texts, prefix):
    assert _strings(texts, prefix), prefix


@pytest.mark.parametrize("prefix", PHASE7_PREFIXES)
def test_no_count_is_spelled_out(texts, prefix):
    hits = []
    for key, text in _strings(texts, prefix):
        for match in _PATTERN.finditer(text):
            if (key, match.group(0)) not in ALLOWED:
                hits.append((key, match.group(0)))
    assert hits == []


def test_every_allowed_entry_still_occurs(texts):
    for (key, phrase), reason in ALLOWED.items():
        assert reason.strip(), (key, phrase)
        strings = [text for found, text in texts.strings() if found == key]
        assert any(phrase in text for text in strings), (key, phrase)


def test_the_lint_catches_a_number_word():
    assert _PATTERN.search("Gebt drei Blätter aus")
    assert not _PATTERN.search("Eine Einheit, dreißig Minuten, achtet darauf")
