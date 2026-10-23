"""Measure deck print model: 30 level cards plus a legend card, numbers from rules, words from texte.toml (PRINT-05, D-01..D-06)."""
import dataclasses
import json
import re

import pytest

from planspiel import audience, fmt, rules
from planspiel.cards import (
    CARDS_PER_SHEET,
    CardDeck,
    LegendCard,
    MeasureCard,
    build_measure_deck,
)
from planspiel.config import load_config
from planspiel.printmodel import PrintModelError
from planspiel.texts import PreAttackView, load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]
MEASURE_CARD_FIELDS = {
    "kind", "card_id", "measure_id", "level", "title", "focus", "description", "simple", "technical",
    "cia_values", "init_text", "opex_text", "dependency",
}
EXPECTED_DEPENDENCIES = {"M1-L3": "M2 ≥ L2", "M3-L3": "M2 ≥ L2", "M7-L3": "M2 ≥ L1"}


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    cfg = load_config(config_path)
    texts = load_texts(content_dir / "texte.toml")
    return cfg, texts, build_measure_deck(cfg, texts)


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, texts, build_measure_deck(cfg, texts)


def _old_requirements_met(measure, level, selection):
    """The loop `_requirements_met` had before `level_requirements` existed (truth-table reference)."""
    for dependency in measure.dependencies:
        if level >= dependency["level"]:
            for req in dependency["requires"]:
                if selection.get(req["measure"], 0) < req["min_level"]:
                    return False
    return True


def test_card_facts_equal_the_config_level(real):
    cfg, _, _ = real
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    for measure_id, measure in cfg.measures.items():
        for level in (1, 2, 3):
            expected = raw["measures"][measure_id]["levels"][str(level)]
            facts = rules.card_facts(cfg.measures, measure_id, level)
            assert facts.cia == expected["cia"]
            assert facts.init_k == expected["init"]
            assert facts.opex_k == expected["opex"]
    facts = rules.card_facts(cfg.measures, "M4", 2)
    assert (facts.init_k, facts.opex_k) == (40, 12)


def test_level_requirements_on_the_real_config(real):
    measures = real[0].measures
    assert rules.level_requirements(measures["M1"], 3) == (("M2", 2),)
    assert rules.level_requirements(measures["M1"], 2) == ()
    assert rules.level_requirements(measures["M7"], 3) == (("M2", 1),)
    assert rules.level_requirements(measures["M3"], 3) == (("M2", 2),)
    with_requirements = {
        (measure_id, level)
        for measure_id, measure in measures.items()
        for level in (1, 2, 3)
        if rules.level_requirements(measure, level)
    }
    assert with_requirements == {("M1", 3), ("M3", 3), ("M7", 3)}


def test_requirements_met_keeps_its_truth_table(real):
    measures = real[0].measures
    checked = 0
    for measure in measures.values():
        required = sorted({req["measure"] for dep in measure.dependencies for req in dep["requires"]})
        for level in (0, 1, 2, 3):
            for combination in range(4 ** len(required)):
                selection = {
                    measure_id: (combination // 4 ** position) % 4 for position, measure_id in enumerate(required)
                }
                assert rules._requirements_met(measure, level, selection) == _old_requirements_met(
                    measure, level, selection
                ), (measure.measure_id, level, selection)
                checked += 1
    assert checked == 76  # 10 measures x 4 levels, times the 4 levels of the one required measure for M1, M3, M7


def test_the_real_deck_has_31_cards_on_8_sheets(real):
    _, _, deck = real
    assert isinstance(deck, CardDeck)
    assert deck.job == audience.MEASURE_DECK_JOB
    assert CARDS_PER_SHEET == 4
    assert len(deck.cards) == 31
    assert isinstance(deck.cards[0], LegendCard)
    assert [card.card_id for card in deck.cards[1:]] == [f"M{n}-L{level}" for n in range(1, 11) for level in (1, 2, 3)]
    assert [len(sheet) for sheet in deck.sheets] == [4, 4, 4, 4, 4, 4, 4, 3]
    assert [card for sheet in deck.sheets for card in sheet] == list(deck.cards)


def test_the_mini_deck_has_13_cards_on_4_sheets():
    cfg = load_config(MINI)
    deck = build_measure_deck(cfg, load_texts(MINI_CONTENT_DIR / "texte.toml"))
    assert len(deck.cards) == 13
    assert [len(sheet) for sheet in deck.sheets] == [4, 4, 4, 1]


def test_every_measure_card_carries_rules_numbers_and_text_wording(loaded):
    cfg, texts, deck = loaded
    view = PreAttackView(cfg, texts)
    per_wave = texts.get("sheets.karten.per_wave")
    for card in deck.cards[1:]:
        assert isinstance(card, MeasureCard)
        level = int(card.level)
        facts = rules.card_facts(cfg.measures, card.measure_id, level)
        measure_texts = view.measure(card.measure_id)
        assert card.kind == "measure"
        assert card.card_id == f"{card.measure_id}-L{card.level}"
        assert card.title == f"{card.measure_id} – {cfg.measures[card.measure_id].name}"
        assert card.focus == measure_texts["focus"]
        assert card.description == measure_texts["description"]
        assert card.simple == measure_texts["levels_simple"][level]
        assert card.technical == measure_texts["levels_desc"][level]
        assert card.cia_values == tuple(fmt.format_number(facts.cia[key]) for key in ("c", "i", "a"))
        assert card.init_text == fmt.format_money(facts.init_k * 1000)
        assert card.opex_text.startswith(fmt.format_money(facts.opex_k * 1000))
        assert card.opex_text.endswith(per_wave)


def test_dependency_only_where_a_requirement_applies(real):
    _, _, deck = real
    found = {card.card_id: card.dependency for card in deck.cards[1:] if card.dependency is not None}
    assert found == EXPECTED_DEPENDENCIES
    assert sum(card.dependency is None for card in deck.cards[1:]) == 27


def test_the_measure_card_field_set_is_pinned():
    assert {field.name for field in dataclasses.fields(MeasureCard)} == MEASURE_CARD_FIELDS


def test_the_legend_samples_the_dependency_card_and_explains_four_things(real):
    _, texts, deck = real
    legend = deck.cards[0]
    assert legend.kind == "legend"
    assert legend.sample.card_id == "M1-L3"
    assert legend.sample.dependency == "M2 ≥ L2"
    assert [number for number, _ in legend.callouts] == ["1", "2", "3", "4"]
    assert [text for _, text in legend.callouts] == [
        texts.get("sheets.karten.legend_cia"),
        texts.get("sheets.karten.legend_costs"),
        texts.get("sheets.karten.legend_dependency"),
        texts.get("sheets.karten.legend_levels"),
    ]
    assert legend.formula == "E-Wert = C · wC + I · wI + A · wA" == texts.get("sheets.karten.legend_formula")
    assert legend.title == texts.get("sheets.karten.legend_title")
    assert legend.intro == texts.get("sheets.karten.legend_intro")


def test_no_measure_card_carries_legend_text(real):
    _, texts, deck = real
    legend_texts = {text for key, text in texts.strings("sheets.karten") if key.startswith("sheets.karten.legend_")}
    for card in deck.cards[1:]:
        for field in dataclasses.fields(card):
            value = getattr(card, field.name)
            for part in value if isinstance(value, tuple) else (value,):
                assert part not in legend_texts, (card.card_id, field.name)


def test_printed_fragments_hold_every_digit_bearing_string(real):
    _, _, deck = real
    fragments = deck.printed_fragments()
    assert len(fragments) == len(set(fragments))
    assert all(re.search(r"\d", fragment) for fragment in fragments)
    for card in deck.cards[1:]:
        for value in (*card.cia_values, card.init_text, card.opex_text, card.title, card.level):
            assert value in fragments, (card.card_id, value)
        if card.dependency:
            assert card.dependency in fragments
    for number, _ in deck.cards[0].callouts:
        assert number in fragments


def test_a_level_outside_one_to_three_is_a_model_error():
    cfg = load_config(MINI)
    measure = cfg.measures["M1"]
    measure.levels[4] = dataclasses.replace(measure.levels[3])
    with pytest.raises(PrintModelError, match="Level"):
        build_measure_deck(cfg, load_texts(MINI_CONTENT_DIR / "texte.toml"))


def test_the_karten_sheet_is_readable_through_the_prewave_view(real):
    cfg, texts, _ = real
    sheet = PreAttackView(cfg, texts).sheet("karten")
    assert {"legend_title", "legend_intro", "legend_cia", "legend_formula", "legend_costs"} <= set(sheet)
    assert {"legend_dependency", "legend_levels", "per_wave", "requires"} <= set(sheet)
