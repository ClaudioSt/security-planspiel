"""Pre-wave print model of the card decks: the measure deck (PRINT-05, D-01..D-07) and the event deck (PRINT-06).

The measure deck is one card per measure level plus a legend card; the event deck is one card per wave event plus
the Budget Review card.

Strings only: every number comes from `rules.card_facts` / `rules.level_requirements`, every word from
`content/texte.toml` through `PreAttackView`; the template only inserts these strings. The card has no field for
wave weights, bonus links, waves or attacks (VEIL-04), so a measure card cannot leak them.
"""
import dataclasses
from dataclasses import dataclass
from typing import Optional

from planspiel import audience, fmt, rules
from planspiel.eventtext import effect_rows
from planspiel.config import Config
from planspiel.printmodel import PrintModelError
from planspiel.texts import PreAttackView, Texts

CARDS_PER_SHEET = 4
LEVELS = (1, 2, 3)  # the level badge colours exist for exactly these levels
LEGEND_ID = "LEGEND"
EVENT_DECK_JOB = "spieler-eventkarten"


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
    reveal_note: str


@dataclass(frozen=True)
class EventCard:
    """A wave event: header, name, narrative, rule text where one exists, and the generated effect lines."""

    kind: str
    card_id: str
    header: str
    title: str
    narrative: str
    rule: Optional[str]
    effect_heading: Optional[str]
    effect_lines: tuple[str, ...]


@dataclass(frozen=True)
class ReviewCard:
    """The Budget Review card: narrative, rule, the tier rows and the overspend rule (the full penalty table is not here)."""

    kind: str
    card_id: str
    header: str
    title: str
    narrative: str
    rule: str
    tier_heading: str
    tier_lines: tuple[str, ...]
    overspend_line: str


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
    cards: tuple[MeasureCard | LegendCard | EventCard | ReviewCard, ...]
    sheets: tuple[tuple[MeasureCard | LegendCard | EventCard | ReviewCard, ...], ...]

    def printed_fragments(self) -> tuple[str, ...]:
        """Every digit-bearing string a card prints, de-duplicated (the pdf test finds each in the PDF text)."""
        found: dict[str, None] = {}
        for card in self.cards:
            for text in printed_strings(card):
                if any(char.isdigit() for char in text):
                    found[text] = None
        return tuple(found)


# Fields that identify a card in the model and the build log but are never printed on it. `key`, `group` and `cells`
# belong to the tracking sheet rows: a row key and group name the row, the cells hold write/shaded states.
_NOT_PRINTED = frozenset({"kind", "card_id", "measure_id", "key", "group", "cells"})


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
        reveal_note=str(texts.get("sheets.karten.legend_reveal")),
    )


def _labels(cfg: Config, texts: Texts) -> CardLabels:
    labels = PreAttackView(cfg, texts).sheet("labels")
    return CardLabels(
        level=labels["level"],
        init=labels["init_costs"],
        opex=labels["opex"],
        requires=str(texts.get("sheets.karten.requires")),
    )


def _sheets(cards: tuple) -> tuple[tuple, ...]:
    return tuple(cards[start:start + CARDS_PER_SHEET] for start in range(0, len(cards), CARDS_PER_SHEET))


def build_measure_deck(cfg: Config, texts: Texts) -> CardDeck:
    measure_cards = _measure_cards(cfg, texts)
    cards = (_legend_card(texts, measure_cards), *measure_cards)
    return CardDeck(job=audience.MEASURE_DECK_JOB, labels=_labels(cfg, texts), cards=cards, sheets=_sheets(cards))


def _card_id(event_id: str) -> str:
    """Ids with a hyphen: the id is written into the build log, where a TeX-escaped underscore would not round-trip."""
    return event_id.replace("_", "-")


def _event_cards(cfg: Config, texts: Texts) -> list[EventCard]:
    """One card per wave event: waves in ascending key order, config order inside a wave (the order they are played)."""
    view = PreAttackView(cfg, texts)
    labels = view.sheet("labels")
    cards: list[EventCard] = []
    for wave_id in sorted(cfg.events):
        for event in cfg.events[wave_id]:
            event_texts = view.event(event.id)
            effect = effect_rows(event, cfg, texts)
            cards.append(
                EventCard(
                    kind="event",
                    card_id=_card_id(event.id),
                    header=f"{labels['event_after_wave']} {wave_id}",
                    title=event.name,
                    narrative=event_texts["narrative"],
                    rule=event_texts.get("rule"),
                    effect_heading=effect.heading,
                    effect_lines=tuple(row.text for row in effect.rows),
                )
            )
    return cards


def _review_cards(cfg: Config, texts: Texts) -> list[ReviewCard]:
    view = PreAttackView(cfg, texts)
    header = view.sheet("eventkarten")["review_header"]
    cards: list[ReviewCard] = []
    for event in cfg.final_events:
        if event.type != "final_budget_tier":
            raise PrintModelError(f"Abschluss-Event '{event.id}': Typ '{event.type}' hat keine Karte")
        event_texts = view.event(event.id)
        effect = effect_rows(event, cfg, texts)
        cards.append(
            ReviewCard(
                kind="review",
                card_id=_card_id(event.id),
                header=header,
                title=event.name,
                narrative=event_texts["narrative"],
                rule=event_texts["rule"],
                tier_heading=str(effect.heading),
                tier_lines=tuple(row.text for row in effect.rows[:-1]),
                overspend_line=effect.rows[-1].text,
            )
        )
    return cards


def build_event_deck(cfg: Config, texts: Texts) -> CardDeck:
    """Seven wave event cards in play order, then the Budget Review card. `sheets.backup_recovery` is not a card (D-26)."""
    cards = (*_event_cards(cfg, texts), *_review_cards(cfg, texts))
    return CardDeck(job=EVENT_DECK_JOB, labels=_labels(cfg, texts), cards=cards, sheets=_sheets(cards))
