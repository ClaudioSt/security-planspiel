"""Pre-wave print model of the measure deck (PRINT-05, D-01..D-07): one card per measure level plus a legend card.

Strings only: every number comes from `rules.card_facts` / `rules.level_requirements`, every word from
`content/texte.toml` through `PreAttackView`; the template only inserts these strings. The card has no field for
wave weights, bonus links, waves or attacks (VEIL-04), so a measure card cannot leak them.
"""
import dataclasses
from dataclasses import dataclass
from typing import Optional

from planspiel import audience, fmt, rules
from planspiel.config import Config
from planspiel.printmodel import PrintModelError
from planspiel.texts import PreAttackView, Texts

CARDS_PER_SHEET = 4
LEVELS = (1, 2, 3)  # the level badge colours exist for exactly these levels
LEGEND_ID = "LEGEND"


@dataclass(frozen=True)
class MeasureCard:
    kind: str
    card_id: str
    measure_id: str
    level: str
    title: str
    focus: str
    description: str
    simple: str
    technical: str
    cia_values: tuple[str, str, str]
    init_text: str
    opex_text: str
    dependency: Optional[str]


@dataclass(frozen=True)
class LegendCard:
    kind: str
    card_id: str
    sample: MeasureCard
    title: str
    intro: str
    callouts: tuple[tuple[str, str], ...]
    formula: str


@dataclass(frozen=True)
class CardLabels:
    """Row labels shared by every card of the deck."""

    level: str
    init: str
    opex: str
    requires: str


@dataclass(frozen=True)
class CardDeck:
    job: str
    labels: CardLabels
    cards: tuple[MeasureCard | LegendCard, ...]
    sheets: tuple[tuple[MeasureCard | LegendCard, ...], ...]

    def printed_fragments(self) -> tuple[str, ...]:
        """Every digit-bearing string a card prints, de-duplicated (the pdf test finds each in the PDF text)."""
        found: dict[str, None] = {}
        for card in self.cards:
            for text in printed_strings(card):
                if any(char.isdigit() for char in text):
                    found[text] = None
        return tuple(found)


# Fields that identify a card in the model and the build log but are never printed on it.
_NOT_PRINTED = frozenset({"kind", "card_id", "measure_id"})


def printed_strings(value: object) -> list[str]:
    """Every string of a card (or part of one) that ends up on the paper."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, tuple):
        return [text for part in value for text in printed_strings(part)]
    if dataclasses.is_dataclass(value):
        return [
            text
            for field in dataclasses.fields(value)
            if field.name not in _NOT_PRINTED
            for text in printed_strings(getattr(value, field.name))
        ]
    return []


def _dependency(measure, level: int) -> Optional[str]:
    requirements = rules.level_requirements(measure, level)
    if not requirements:
        return None
    return ", ".join(f"{required} ≥ L{min_level}" for required, min_level in requirements)


def _measure_cards(cfg: Config, texts: Texts) -> list[MeasureCard]:
    view = PreAttackView(cfg, texts)
    per_wave = str(texts.get("sheets.karten.per_wave"))
    cards: list[MeasureCard] = []
    for measure_id, measure in cfg.measures.items():
        measure_texts = view.measure(measure_id)
        for level in sorted(level for level in measure.levels if level > 0):
            if level not in LEVELS:
                raise PrintModelError(f"{measure_id}: Level {level} hat keine Abzeichenfarbe (erlaubt: 1 bis 3)")
            facts = rules.card_facts(cfg.measures, measure_id, level)
            cards.append(
                MeasureCard(
                    kind="measure",
                    card_id=f"{measure_id}-L{level}",
                    measure_id=measure_id,
                    level=str(level),
                    title=f"{measure_id} – {measure.name}",
                    focus=measure_texts["focus"],
                    description=measure_texts["description"],
                    simple=measure_texts["levels_simple"][level],
                    technical=measure_texts["levels_desc"][level],
                    cia_values=tuple(fmt.format_number(facts.cia[key]) for key in ("c", "i", "a")),
                    init_text=fmt.format_money(facts.init_k * 1000),
                    opex_text=f"{fmt.format_money(facts.opex_k * 1000)} {per_wave}",
                    dependency=_dependency(measure, level),
                )
            )
    return cards


def _legend_card(texts: Texts, measure_cards: list[MeasureCard]) -> LegendCard:
    sample = next((card for card in measure_cards if card.dependency), measure_cards[0])
    callouts = tuple(
        (str(number), str(texts.get(f"sheets.karten.{key}")))
        for number, key in enumerate(("legend_cia", "legend_costs", "legend_dependency", "legend_levels"), start=1)
    )
    return LegendCard(
        kind="legend",
        card_id=LEGEND_ID,
        sample=sample,
        title=str(texts.get("sheets.karten.legend_title")),
        intro=str(texts.get("sheets.karten.legend_intro")),
        callouts=callouts,
        formula=str(texts.get("sheets.karten.legend_formula")),
    )


def build_measure_deck(cfg: Config, texts: Texts) -> CardDeck:
    measure_cards = _measure_cards(cfg, texts)
    labels = PreAttackView(cfg, texts).sheet("labels")
    cards = (_legend_card(texts, measure_cards), *measure_cards)
    return CardDeck(
        job=audience.MEASURE_DECK_JOB,
        labels=CardLabels(
            level=labels["level"],
            init=labels["init_costs"],
            opex=labels["opex"],
            requires=str(texts.get("sheets.karten.requires")),
        ),
        cards=cards,
        sheets=tuple(cards[start:start + CARDS_PER_SHEET] for start in range(0, len(cards), CARDS_PER_SHEET)),
    )
