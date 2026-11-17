"""Measure deck template: thin Jinja rendering of the card model, registered in the print set (PRINT-05, D-02, D-06)."""
import json
import re

import pytest

from planspiel import fmt, render, texbuild
from planspiel.cards import build_measure_deck
from planspiel.config import load_config
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"
STYLE = REPO_ROOT / "print" / "planspiel.sty"
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
DECK_JOB = "spieler-massnahmenkarten"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]
CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b-\x1f]")


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    cfg = load_config(config_path)
    texts = load_texts(content_dir / "texte.toml")
    deck = build_measure_deck(cfg, texts)
    return cfg, texts, deck, render.render_all(cfg, texts, TEMPLATES)[DECK_JOB]


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, texts, build_measure_deck(cfg, texts), render.render_all(cfg, texts, TEMPLATES)


def _card_blocks(source, deck):
    """The .tex text of each card: from the end of the previous card (or the sheet start) to its own \\cardreport."""
    blocks = {}
    start = 0
    for card in deck.cards:
        marker = f"\\cardreport{{{card.card_id}}}"
        end = source.index(marker, start)
        blocks[card.card_id] = source[start:end]
        start = end + len(marker)
    return blocks


def test_the_real_print_set_holds_the_deck_next_to_the_worksheets(real):
    jobs = list(real[3])
    assert jobs == sorted(jobs)
    assert DECK_JOB in jobs
    assert [job for job in jobs if job.startswith("angriff-")] == [
        "angriff-1_ransomware", "angriff-2_ot", "angriff-3_exfil"
    ]


def test_the_mini_config_renders_13_cards():
    cfg = load_config(MINI)
    texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    source = render.render_all(cfg, texts, TEMPLATES)[DECK_JOB]
    assert source.count("\\cardreport{") == 13


def test_the_deck_skeleton(loaded):
    source = loaded[3]
    assert source.startswith("\\documentclass")
    assert "\\usepackage{planspiel}" in source
    assert "\\usepackage{tikz}" in source
    assert source.endswith("\\end{document}\n")
    assert "\r" not in source
    assert CONTROL_CHARACTERS.search(source) is None


def test_every_printed_fragment_is_in_the_tex(loaded):
    _, _, deck, source = loaded
    for fragment in deck.printed_fragments():
        assert render.tex_escape(fragment) in source, fragment


def test_measure_names_are_escaped(real):
    source = real[3][DECK_JOB]
    assert "Logging \\& SIEM/MDR" in source
    assert "Logging & SIEM/MDR" not in source


def test_one_card_report_per_card_and_one_sheet_per_a4_page(loaded):
    _, _, deck, source = loaded
    for card in deck.cards:
        assert source.count(f"\\cardreport{{{card.card_id}}}") == 1, card.card_id
    assert source.count("\\cardreport{") == len(deck.cards)
    assert source.count("\\begin{cardsheet}") == len(deck.sheets)
    assert source.count("\\end{cardsheet}") == len(deck.sheets)


def test_the_real_deck_is_31_cards_on_8_sheets(real):
    source = real[3][DECK_JOB]
    assert source.count("\\cardreport{") == 31
    assert source.count("\\begin{cardsheet}") == 8


def test_the_lock_icon_sits_exactly_on_the_cards_with_a_dependency(loaded):
    _, _, deck, source = loaded
    blocks = _card_blocks(source, deck)
    for card in deck.cards[1:]:
        block = blocks[card.card_id]
        if card.dependency:
            assert block.count("\\lockicon") == 1, card.card_id
            assert re.search(r"\\lockicon.*?" + re.escape(render.tex_escape(card.dependency)), block, re.DOTALL)
        else:
            assert "\\lockicon" not in block, card.card_id
    assert blocks[deck.cards[0].card_id].count("\\lockicon") >= 1


def test_the_real_deck_shows_the_lock_on_three_cards(real):
    _, _, deck, documents = real
    blocks = _card_blocks(documents[DECK_JOB], deck)
    assert [card_id for card_id, block in blocks.items() if card_id != "LEGEND" and "\\lockicon" in block] == [
        "M1-L3", "M3-L3", "M7-L3"
    ]


def test_a_cost_change_reaches_the_card_without_a_template_change(tmp_path):
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    original = load_config(CONFIG_PATH)
    old_init = original.measures["M1"].levels[1].init
    raw["measures"]["M1"]["levels"]["1"]["init"] = old_init + 1
    path = tmp_path / "config.json"
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    cfg = load_config(path)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    deck = build_measure_deck(cfg, texts)
    source = render.render_all(cfg, texts, TEMPLATES)[DECK_JOB]
    block = _card_blocks(source, deck)["M1-L1"]
    assert fmt.format_money((old_init + 1) * 1000) in block
    assert fmt.format_money(old_init * 1000) not in block


def test_the_card_template_exists_and_keeps_to_plain_variables():
    template = TEMPLATES / "karten.tex.j2"
    assert template.is_file()
    text = template.read_text(encoding="utf-8")
    assert "card.kind" in text
    assert "\\usepackage{tikz}" in text
    for expression in re.findall(r"\\VAR\{([^}]*)\}", text):
        assert re.match(r"^[A-Za-z_][A-Za-z0-9_.\[\]'\"]*$", expression), expression


def test_tikz_is_a_probed_package_and_in_the_install_list():
    assert texbuild.TEX_PROBES["tikz.sty"] == "pgf"
    lines = (REPO_ROOT / "print" / "miktex-packages.txt").read_text(encoding="utf-8").split()
    assert "pgf" in lines
    assert lines == sorted(lines)


def test_the_level_badge_has_an_error_branch():
    style = STYLE.read_text(encoding="utf-8")
    assert "\\else\\PackageError{planspiel}{Unbekanntes Level" in style


def test_the_style_carries_the_card_macros():
    style = STYLE.read_text(encoding="utf-8")
    for needle in ("\\lockicon", "\\cardreport", "PLANSPIEL-CARD", "cardsheet", "cardcell"):
        assert needle in style, needle
