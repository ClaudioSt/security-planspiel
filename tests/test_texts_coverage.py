"""Abdeckung der Inhaltsquelle gegen Config-IDs und deklarierte Listen (PRINT-02, D-09)."""
import copy
import json

import pytest

from planspiel.cli import main
from planspiel.config import load_config
from planspiel.texts import SHEET_KEYS, Texts, check_coverage, load_texts, required_keys
from tests.support import MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"


def _data():
    return copy.deepcopy(load_texts(MINI_CONTENT_DIR / "texte.toml").data)


def _delete(data, dotted):
    *parents, last = dotted.split(".")
    node = data
    for part in parents:
        node = node[part]
    del node[last]


def _put(data, dotted, value):
    *parents, last = dotted.split(".")
    node = data
    for part in parents:
        node = node.setdefault(part, {})
    node[last] = value


def _codes(issues):
    return sorted((issue.code, issue.path) for issue in issues)


def test_mini_fixture_is_fully_covered():
    texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    assert check_coverage(load_config(MINI), texts) == []


def test_required_keys_follow_the_config_ids():
    keys = required_keys(load_config(MINI))
    assert "measures.M1.levels_simple.3" in keys
    assert "measures.M1.levels_desc.0" not in keys
    assert "attacks.ransomware.revealed.bonus_reasons.M4" in keys
    assert {f"attacks.{attack_id}.veiled.title" for attack_id in ("ransomware", "ot", "exfil")} <= keys
    assert "attacks.ot.revealed.bonus_reasons.M4" not in keys
    assert "events.kritische_schwachstelle.tier_labels.2" in keys
    assert "events.oem_audit.checklist_heading" in keys
    assert "final_events.budget_review.rule" in keys
    assert set(SHEET_KEYS) <= keys
    assert "story.steckbrief.doc_title" in keys


MUTATIONS = [
    ("missing measure key", lambda d: _delete(d, "measures.M1.focus"), [("texts.missing_key", "measures.M1.focus")]),
    ("orphan measure", lambda d: _put(d, "measures.M99.focus", "x"), [("texts.orphan_key", "measures.M99.focus")]),
    (
        "orphan attack",
        lambda d: _put(d, "attacks.foo.revealed.name", "x"),
        [("texts.orphan_key", "attacks.foo.revealed.name")],
    ),
    ("missing veiled title", lambda d: _delete(d, "attacks.ot.veiled.title"), [("texts.missing_key", "attacks.ot.veiled.title")]),
    ("veiled teaser", lambda d: _put(d, "attacks.ot.veiled.teaser", "x"), [("texts.orphan_key", "attacks.ot.veiled.teaser")]),
    (
        "attack name outside revealed",
        lambda d: _put(d, "attacks.ransomware.name", "x"),
        [("texts.orphan_key", "attacks.ransomware.name")],
    ),
    (
        "bonus reasons on a measure",
        lambda d: _put(d, "measures.M3.bonus_reasons.x", "x"),
        [("texts.orphan_key", "measures.M3.bonus_reasons.x")],
    ),
    ("missing event rule", lambda d: _delete(d, "events.sparprogramm.rule"), [("texts.missing_key", "events.sparprogramm.rule")]),
    (
        "missing tier label",
        lambda d: _delete(d, "events.kritische_schwachstelle.tier_labels.2"),
        [("texts.missing_key", "events.kritische_schwachstelle.tier_labels.2")],
    ),
    ("orphan top-level", lambda d: _put(d, "foo.bar", "x"), [("texts.orphan_key", "foo.bar")]),
    ("missing sheet label", lambda d: _delete(d, "sheets.labels.sum"), [("texts.missing_key", "sheets.labels.sum")]),
    ("orphan sheet key", lambda d: _put(d, "sheets.angriff.extra", "x"), [("texts.orphan_key", "sheets.angriff.extra")]),
    (
        "orphan story doc",
        lambda d: _put(d, "story.unknown_doc.doc_title", "x"),
        [("texts.orphan_key", "story.unknown_doc.doc_title")],
    ),
    (
        "missing story title",
        lambda d: _delete(d, "story.steckbrief.doc_title"),
        [("texts.missing_key", "story.steckbrief.doc_title")],
    ),
    ("free-form story block", lambda d: _put(d, "story.steckbrief.new_block.text", "frei"), []),
    ("empty string", lambda d: _put(d, "measures.M1.focus", ""), [("texts.empty", "measures.M1.focus")]),
    ("blank string", lambda d: _put(d, "measures.M1.focus", "  \n"), [("texts.empty", "measures.M1.focus")]),
    ("integer leaf", lambda d: _put(d, "measures.M1.focus", 5), [("texts.type", "measures.M1.focus")]),
    (
        "list with non-string",
        lambda d: _put(d, "story.steckbrief.produkte.bullets", ["a", 3]),
        [("texts.type", "story.steckbrief.produkte.bullets")],
    ),
    (
        "required key is a table",
        lambda d: _put(d, "measures.M1.focus", {"unter": "x"}),
        [("texts.missing_key", "measures.M1.focus"), ("texts.orphan_key", "measures.M1.focus.unter")],
    ),
]


@pytest.mark.parametrize("name, mutate, expected", MUTATIONS, ids=[case[0] for case in MUTATIONS])
def test_coverage_mutations(name, mutate, expected):
    data = _data()
    mutate(data)
    assert _codes(check_coverage(load_config(MINI), Texts(data))) == sorted(expected)


def test_a_new_config_measure_without_text_fails_coverage(tmp_path):
    raw = json.loads(MINI.read_text(encoding="utf-8"))
    raw["measures"]["M99"] = copy.deepcopy(raw["measures"]["M1"])
    raw["measures"]["M99"]["name"] = "Neu"
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    issues = check_coverage(load_config(config_path), texts)
    assert ("texts.missing_key", "measures.M99.focus") in _codes(issues)
    assert ("texts.missing_key", "measures.M99.levels_simple.3") in _codes(issues)


def test_cli_texts_passes_on_the_mini_content(capsys):
    code = main(["texts", "--config", str(MINI), "--content-dir", str(MINI_CONTENT_DIR)])
    assert code == 0
    assert "0 Fehler, 0 Warnung(en)" in capsys.readouterr().out


def test_cli_texts_reports_a_missing_key(tmp_path, capsys):
    source = (MINI_CONTENT_DIR / "texte.toml").read_text(encoding="utf-8")
    broken = source.replace('focus = "Zugriffe regeln"\n', "", 1)
    assert broken != source
    (tmp_path / "texte.toml").write_text(broken, encoding="utf-8", newline="\n")
    for name in ("digit_allowlist.toml", "giveaway_terms.toml"):
        (tmp_path / name).write_text((MINI_CONTENT_DIR / name).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    code = main(["texts", "--config", str(MINI), "--content-dir", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 1
    assert any(line.startswith("ERROR texts.missing_key measures.M1.focus") for line in out.splitlines())
    assert "1 Fehler, 0 Warnung(en)" in out


def test_cli_texts_reports_invalid_toml(tmp_path, capsys):
    (tmp_path / "texte.toml").write_text("das = = ist kein toml\n", encoding="utf-8", newline="\n")
    (tmp_path / "digit_allowlist.toml").write_text("", encoding="utf-8", newline="\n")
    (tmp_path / "giveaway_terms.toml").write_text("", encoding="utf-8", newline="\n")
    code = main(["texts", "--config", str(MINI), "--content-dir", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 1
    assert "ERROR texts.toml" in out


def test_cli_texts_reports_a_missing_file(tmp_path, capsys):
    code = main(["texts", "--config", str(MINI), "--content-dir", str(tmp_path)])
    assert code == 1
    assert "ERROR texts.toml" in capsys.readouterr().out
