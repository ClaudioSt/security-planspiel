"""Information boundary of the measure deck on the model and the .tex (VEIL-04, T-05-13, T-05-15, D-04, D-24).

A measure card shows CIA values, costs and dependencies only. Wave weights and measure->attack bonus links are
printed on the revealed attack worksheet of that wave (see `tests/test_veil_cards_pdf.py`) and nowhere earlier.
"""
import ast
import dataclasses
import re

import pytest

from planspiel import audience, render, veil
from planspiel.cards import LegendCard, MeasureCard, build_measure_deck, printed_strings
from planspiel.config import load_config
from planspiel.texts import PreAttackView, load_content
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
TEMPLATES = REPO_ROOT / "print" / "templates"
CARDS_MODULE = REPO_ROOT / "planspiel" / "cards.py"
DECK_JOB = "spieler-massnahmenkarten"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]
MEASURE_CARD_FIELDS = {
    "kind", "card_id", "measure_id", "level", "title", "focus", "description", "simple", "technical",
    "cia_values", "init_text", "opex_text", "dependency",
}
# Attribute names that would let cards.py reach wave, attack or bonus data (D-04, Phase 3 D-13).
FORBIDDEN_ATTRIBUTES = frozenset({"waves", "attacks", "bonus_measures", "bonus_rows", "bonus_reasons", "weights"})
FORBIDDEN_NAMES = frozenset({"RevealView", "FacilitatorView", "worksheet_constants", "build_attack_sheets"})
WAVE_REFERENCE = re.compile(r"Welle\s*\d")
MEASURE_ID = re.compile(r"\bM\d+\b")


def forbidden_accesses(source: str) -> list[str]:
    """Findings (`line: what`) of wave, attack and bonus access in a module."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRIBUTES:
            found.append(f"{node.lineno}: attribute {node.attr}")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            found.append(f"{node.lineno}: name {node.id}")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                for name in (alias.name.split(".")[-1], alias.asname):
                    if name in FORBIDDEN_NAMES:
                        found.append(f"{node.lineno}: import {name}")
    return found


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    cfg = load_config(config_path)
    content = load_content(content_dir)
    return cfg, content, build_measure_deck(cfg, content.texts)


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    content = load_content(CONTENT_DIR)
    deck = build_measure_deck(cfg, content.texts)
    source = render.render_all(cfg, content.texts, TEMPLATES)[DECK_JOB]
    return cfg, content, deck, source, veil.context(cfg, content.texts, content.terms)


def test_the_measure_card_can_only_carry_descriptive_text_cia_costs_and_dependencies():
    assert {field.name for field in dataclasses.fields(MeasureCard)} == MEASURE_CARD_FIELDS


def test_cards_module_never_reads_wave_or_attack_data():
    assert forbidden_accesses(CARDS_MODULE.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize(
    "source",
    [
        "weights = cfg.waves[0]",
        "rows = cfg.attacks['ot']",
        "x = measure.bonus_measures",
        "from planspiel.texts import RevealView",
        "from planspiel.rules import worksheet_constants as constants",
        "sheets = build_attack_sheets(cfg, texts)",
    ],
)
def test_the_cards_scan_reports_each_forbidden_access(source):
    assert forbidden_accesses(source)


def test_the_cards_scan_passes_the_pre_wave_view():
    assert forbidden_accesses("view = PreAttackView(cfg, texts)\nfacts = rules.card_facts(cfg.measures, 'M1', 1)\n") == []


def _wave_and_bonus_hits(strings, cfg, content):
    """Everything on a measure card that would reveal a weight, a bonus link, an attack or a wave."""
    ctx = veil.context(cfg, content.texts, content.terms)
    view = PreAttackView(cfg, content.texts)
    forbidden: list[str] = []
    for attack_id in cfg.attacks:
        prefix = f"attacks.{attack_id}.revealed"
        forbidden += [text for _, text in content.texts.strings(f"{prefix}.bonus_reasons")]
        if content.texts.has(f"{prefix}.name"):
            forbidden.append(str(content.texts.get(f"{prefix}.name")))
    forbidden += [view.attack_title(wave) for wave in cfg.waves]
    forbidden.append(str(content.texts.get("sheets.labels.bonus")))
    joined = "\n".join(strings)
    hits = [text for text in forbidden if text in joined]
    hits += [match.group(0) for match in WAVE_REFERENCE.finditer(joined)]
    hits += [f"weights of wave {wave}" for wave in veil.weight_hits(joined, ctx.signatures)]
    return hits


def test_no_measure_card_text_carries_a_weight_bonus_link_attack_name_or_wave_reference(loaded):
    cfg, content, deck = loaded
    for card in deck.cards:
        if isinstance(card, MeasureCard):
            assert _wave_and_bonus_hits(printed_strings(card), cfg, content) == [], card.card_id


def test_the_hit_finder_catches_each_kind_of_leak(loaded):
    cfg, content, _ = loaded
    wave = cfg.waves[0]
    reason = next(text for _, text in content.texts.strings(f"attacks.{wave.attack_id}.revealed.bonus_reasons"))
    title = PreAttackView(cfg, content.texts).attack_title(wave)
    signature = next(triple for triple, wave_id in veil.weight_signatures(cfg).items() if wave_id == wave.wave_id)
    for leak in (reason, title, "in Welle 2 wichtig", "Bonus", " ".join(signature)):
        assert _wave_and_bonus_hits(["Text", leak], cfg, content), leak


def test_the_legend_reveal_note_is_the_text_and_has_no_digit_measure_or_attack(loaded):
    cfg, content, deck = loaded
    legend = deck.cards[0]
    assert isinstance(legend, LegendCard)
    assert legend.reveal_note == content.texts.get("sheets.karten.legend_reveal")
    assert legend.reveal_note
    assert not any(char.isdigit() for char in legend.reveal_note)
    assert MEASURE_ID.search(legend.reveal_note) is None
    ctx = veil.context(cfg, content.texts, content.terms)
    assert veil.name_hits(legend.reveal_note, ctx, audience.PROFILE_NAMES) == []
    assert veil.revealed_hits(legend.reveal_note, ctx) == []


def test_the_legend_note_says_where_weights_and_bonus_are_revealed(real):
    note = real[2].cards[0].reveal_note
    for word in ("wC", "wI", "wA", "Bonus", "Angriffsblatt"):
        assert word in note, word


def test_the_deck_tex_passes_the_names_only_profile_and_carries_no_weight(real):
    _, _, _, source, ctx = real
    text = veil.detex(source)
    assert veil.name_hits(text, ctx, audience.PROFILE_NAMES) == []
    assert veil.name_hits(text, ctx, audience.PROFILE_NAMES, squashed=True) == []
    assert veil.revealed_hits(text, ctx) == []
    assert veil.revealed_hits(text, ctx, squashed=True) == []
    assert veil.weight_hits(text, ctx.signatures) == []
    assert veil.weight_symbol_hits(text) == []


def test_the_story_profile_would_reject_the_phishing_defence_term_of_m6(real):
    """Documents D-24: the deck needs the names-only profile because M6 legitimately says Phishing."""
    _, _, _, source, ctx = real
    assert veil.name_hits(veil.detex(source), ctx, audience.PROFILE_STORY) == ["phishing"]
    assert audience.scan_profile(DECK_JOB) == audience.PROFILE_NAMES


def test_the_rendered_legend_carries_the_reveal_note(real):
    _, _, deck, source, _ = real
    marker = "\\cardreport{LEGEND}"
    block = source[: source.index(marker)]
    assert render.tex_escape(deck.cards[0].reveal_note) in block


def test_the_deck_scan_over_the_whole_document_is_clean(real):
    _, _, _, source, ctx = real
    assert veil.scan_text(veil.detex(source), DECK_JOB, ctx, layer="tex") == []
