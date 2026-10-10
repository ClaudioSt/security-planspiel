"""Loader der Inhaltsquelle content/texte.toml (PRINT-02)."""
import pytest

from planspiel.texts import AllowEntry, Content, Texts, load_allowlist, load_content, load_texts
from tests.support import MINI_CONTENT_DIR

MINI_TEXTE = MINI_CONTENT_DIR / "texte.toml"


def _write(path, text, newline="\n"):
    with open(path, "w", encoding="utf-8", newline=newline) as handle:
        handle.write(text)


def test_load_texts_returns_texts_and_get_reads_leaves():
    texts = load_texts(MINI_TEXTE)
    assert isinstance(texts, Texts)
    assert texts.get("measures.M1.focus") == "Zugriffe regeln"
    assert texts.get("measures.M1.levels_desc.1").startswith("Zentrale Benutzerverwaltung")


def test_umlauts_and_typographic_quotes_round_trip(tmp_path):
    path = tmp_path / "texte.toml"
    value = "Prüfung: Größe, Maßnahmen, Äpfel, Öl, Übung „enterprise-ready“"
    _write(path, f'[a]\nb = "{value}"\n')
    assert load_texts(path).get("a.b") == value


def test_crlf_file_yields_the_same_multiline_value(tmp_path):
    body = '[a]\nb = """Erste Zeile\nZweite Zeile"""\n'
    lf_path = tmp_path / "lf.toml"
    crlf_path = tmp_path / "crlf.toml"
    _write(lf_path, body)
    _write(crlf_path, body, newline="\r\n")
    assert load_texts(crlf_path).get("a.b") == load_texts(lf_path).get("a.b")


def test_get_on_missing_key_raises_key_error():
    texts = load_texts(MINI_TEXTE)
    with pytest.raises(KeyError):
        texts.get("measures.M99.focus")


def test_has_distinguishes_present_and_absent_keys():
    texts = load_texts(MINI_TEXTE)
    assert texts.has("measures.M1.focus")
    assert texts.has("measures.M1")
    assert not texts.has("measures.M99")


def test_list_of_strings_is_one_leaf_and_strings_yields_its_elements():
    texts = load_texts(MINI_TEXTE)
    key = "story.steckbrief.produkte.bullets"
    assert texts.get(key) == ["Präzisions-Getriebeteile", "Prototyping und Kleinserien"]
    leaf_keys = [name for name, _ in texts.leaves()]
    assert leaf_keys.count(key) == 1
    assert [text for name, text in texts.strings() if name == key] == [
        "Präzisions-Getriebeteile",
        "Prototyping und Kleinserien",
    ]


def test_leaves_come_back_in_file_order_with_digit_keys_as_strings(tmp_path):
    path = tmp_path / "texte.toml"
    _write(path, '[z]\nb = "1"\na = "2"\n[z.levels]\n1 = "x"\n2 = "y"\n[a]\nc = "3"\n')
    keys = [name for name, _ in load_texts(path).leaves()]
    assert keys == ["z.b", "z.a", "z.levels.1", "z.levels.2", "a.c"]


def test_strings_filters_by_prefix():
    texts = load_texts(MINI_TEXTE)
    keys = [name for name, _ in texts.strings("story")]
    assert keys
    assert all(name.startswith("story.") for name in keys)
    assert not any(name.startswith("story.") for name, _ in texts.strings("measures"))


def test_subtree_returns_the_table():
    texts = load_texts(MINI_TEXTE)
    assert texts.subtree("events.exzellenz_bonus") == {"narrative": texts.get("events.exzellenz_bonus.narrative")}


def test_load_allowlist_reads_allow_entries():
    entries = load_allowlist(MINI_CONTENT_DIR / "digit_allowlist.toml")
    assert entries == (
        AllowEntry(
            key="measures.M2.levels_desc.1",
            token="30 Tage",
            why="Aufbewahrungsdauer der Protokolle, kein Spielparameter",
        ),
    )


def test_load_content_reads_both_files():
    content = load_content(MINI_CONTENT_DIR)
    assert isinstance(content, Content)
    assert content.texts.has("measures.M1.focus")
    assert len(content.allowlist) == 1
