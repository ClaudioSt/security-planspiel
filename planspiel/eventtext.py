"""Print wording of the event effects (PRINT-06, Phase 3 D-24): effect lines generated from event type and params.

Every number of a line comes from the event params or from `rules` (`penalty_params`, `kurswechsel_wave`, the tier
lookup) and is formatted with `planspiel.fmt`; every word comes from `[sheets.eventkarten]` and the event's own
text subtree through `PreAttackView`. `tests/test_event_text.py` proves each row equal to `rules.evaluate_event`
and `rules.budget_review_delta` for every input it covers, so a printed effect cannot drift from the simulation.
The module is a pre-wave builder: it never reads revealed text (VEIL-02).
"""
from typing import NamedTuple, Optional

from planspiel import fmt, rules
from planspiel.config import Config, Event
from planspiel.printmodel import PrintModelError
from planspiel.review_text import _tier_value_text, format_eur, tier_rows
from planspiel.texts import PreAttackView, Texts

# Event type -> effect kind. External kinds change the budget but not the RoS (rules.security_spend, RULE-06);
# `window` is applied by the path model; `review` is the end check (plans 05-07 and 05-15 consume the kinds).
EFFECT_KINDS: dict[str, str] = {
    "kurswechsel": "window",
    "opex_discount_per_active_measure": "external_opex",
    "flat_budget": "external_budget",
    "checklist_tier": "kz",
    "measure_level_tier": "kz",
    "level_bonus_per_measure": "kz",
    "and_condition": "kz",
    "final_budget_tier": "review",
}
EN_DASH = "–"
ARROW = "→"


class EffectRow(NamedTuple):
    """One printed effect line: its text, its exact value (KZ points; k EUR for budget and OPEX) and the counts or
    levels the row covers (`()` when the row does not stand for a count or level)."""

    text: str
    value: int
    covers: tuple[int, ...]


class EventEffect(NamedTuple):
    event_id: str
    kind: str
    heading: Optional[str]
    rows: tuple[EffectRow, ...]


def event_wave(cfg: Config, event_id: str) -> Optional[int]:
    """The config wave key of a wave event; None for the final events (Budget Review)."""
    for wave_id, events in cfg.events.items():
        if any(event.id == event_id for event in events):
            return wave_id
    return None


def _kz(words: dict, value: int) -> str:
    return f"{words['kz']} {_tier_value_text(value)}"


def _measure_label(cfg: Config, measure_id: str) -> str:
    if measure_id not in cfg.measures:
        raise PrintModelError(f"Maßnahme '{measure_id}' gibt es in der Config nicht")
    return f"{measure_id} {EN_DASH} {cfg.measures[measure_id].name}"


def _checklist(event: Event, cfg: Config, view: PreAttackView, words: dict, event_texts: dict) -> EventEffect:
    params = event.params
    count_max = len(params["measures"])
    values = [rules._tier_lookup(count, params["tiers"]) for count in range(count_max + 1)]
    groups: list[list[int]] = []
    for count, value in enumerate(values):
        if groups and values[groups[-1][0]] == value:
            groups[-1].append(count)
        else:
            groups.append([count])
    rows = []
    for group in groups:
        counts = str(group[0]) if len(group) == 1 else f"{group[0]}{EN_DASH}{group[-1]}"
        value = values[group[0]]
        rows.append(EffectRow(f"{counts} {words['fulfilled']} {ARROW} {_kz(words, value)}", value, tuple(group)))
    measures = ", ".join(_measure_label(cfg, measure_id) for measure_id in params["measures"])
    labels = f"{event_texts['checklist_heading']}: {measures}, {words['each_at_least']} {params['min_level']}"
    return EventEffect(event.id, EFFECT_KINDS[event.type], labels, tuple(rows))


def _level_tier(event: Event, cfg: Config, view: PreAttackView, words: dict, event_texts: dict) -> EventEffect:
    params = event.params
    labels = event_texts.get("tier_labels", {})
    if set(labels) != set(params["tiers"]):
        raise PrintModelError(
            f"{event.id}: tier_labels {sorted(labels)} passen nicht zu den Stufen {sorted(params['tiers'])}"
        )
    levels = sorted(int(level) for level in params["tiers"])
    rows = tuple(
        EffectRow(
            f"{view.sheet('labels')['level']} {level}: {labels[str(level)]} {ARROW} {_kz(words, params['tiers'][str(level)])}",
            params["tiers"][str(level)],
            (level,),
        )
        for level in levels
    )
    heading = f"{words['level_of_measure']} {_measure_label(cfg, params['measure'])}:"
    return EventEffect(event.id, EFFECT_KINDS[event.type], heading, rows)


def _level_bonus(event: Event, words: dict) -> EventEffect:
    params = event.params
    text = (
        f"{words['per_measure_at_level']} {params['level']} {words['level_or_higher']}: "
        f"{_kz(words, params['kz_per_measure'])}"
    )
    return EventEffect(event.id, EFFECT_KINDS[event.type], None, (EffectRow(text, params["kz_per_measure"], ()),))


def _clause_text(clause: dict, cfg: Config, labels: dict, words: dict) -> str:
    name = _measure_label(cfg, clause["measure"])
    if "min_level" in clause:
        return f"{name} {labels['min_level']} {clause['min_level']}"
    if "level_eq" in clause:
        if clause["level_eq"] == 0:
            return f"{name} {words['not_active']} ({labels['level']} {clause['level_eq']})"
        return f"{name} {words['level_equals']} {clause['level_eq']}"
    raise PrintModelError(f"Bedingung ohne min_level oder level_eq: {clause}")


def _and_condition(event: Event, cfg: Config, view: PreAttackView, words: dict) -> EventEffect:
    params = event.params
    labels = view.sheet("labels")
    clauses = f" {words['condition_and']} ".join(_clause_text(clause, cfg, labels, words) for clause in params["clauses"])
    rows = (
        EffectRow(f"{words['condition_if']} {clauses}: {_kz(words, params['kz_delta'])}", params["kz_delta"], ()),
        EffectRow(f"{words['otherwise']}: {_kz(words, 0)}", 0, ()),
    )
    return EventEffect(event.id, EFFECT_KINDS[event.type], None, rows)


def _flat_budget(event: Event, words: dict) -> EventEffect:
    delta_k = event.params["budget_delta"]
    text = f"{words['total_budget']} {fmt.format_signed(delta_k * 1000)} €"
    return EventEffect(event.id, EFFECT_KINDS[event.type], None, (EffectRow(text, delta_k, ()),))


def _opex_discount(event: Event, words: dict) -> EventEffect:
    delta_k = event.params["opex_per_measure"]
    text = f"{words['opex_costs']} {fmt.format_signed(delta_k * 1000)} € {words['per_active_measure']}"
    return EventEffect(event.id, EFFECT_KINDS[event.type], None, (EffectRow(text, delta_k, ()),))


def _kurswechsel(event: Event, cfg: Config, words: dict) -> EventEffect:
    wave = rules.kurswechsel_wave(cfg.events)
    if wave is None:
        raise PrintModelError(f"{event.id}: keine Welle der Config enthält den Kurswechsel")
    text = f"{words['kurswechsel_window']} {wave}"
    return EventEffect(event.id, EFFECT_KINDS[event.type], None, (EffectRow(text, 0, ()),))


def _budget_review(event: Event, cfg: Config, words: dict) -> EventEffect:
    kz_per_step, step_k = rules.penalty_params(cfg.final_events)
    rows: list[EffectRow] = []
    for index, (from_eur, to_eur, kz) in enumerate(tier_rows(event.params["tiers"])):
        if index == 0 and to_eur is not None:
            span = f"{format_eur(from_eur)} {EN_DASH} {format_eur(to_eur)} €"
        else:
            span = f"{words['tier_from']} {format_eur(from_eur)} €"
        rows.append(EffectRow(f"{span} {ARROW} {_kz(words, kz)}", kz, ()))
    penalty = -kz_per_step
    overspend = f"{words['overspend_label']} {fmt.MINUS}{kz_per_step} {words['kz']} {words['per_started']} {fmt.format_money(step_k * 1000)}"
    rows.append(EffectRow(overspend, penalty, ()))
    return EventEffect(event.id, EFFECT_KINDS[event.type], words["tier_heading"], tuple(rows))


def effect_rows(event: Event, cfg: Config, texts: Texts, event_texts: Optional[dict] = None) -> EventEffect:
    """The printed effect of one event; the rows are generated from the event type and its params.

    `event_texts` replaces the event's text subtree (the Welle 0 practice event keeps its texts under `practice.event`).
    """
    if event.type not in EFFECT_KINDS:
        raise PrintModelError(f"Event '{event.id}': Typ '{event.type}' hat keine Druckdarstellung")
    view = PreAttackView(cfg, texts)
    words = view.sheet("eventkarten")
    if event.type == "kurswechsel":
        return _kurswechsel(event, cfg, words)
    if event.type == "opex_discount_per_active_measure":
        return _opex_discount(event, words)
    if event.type == "flat_budget":
        return _flat_budget(event, words)
    if event.type == "checklist_tier":
        return _checklist(event, cfg, view, words, event_texts if event_texts is not None else view.event(event.id))
    if event.type == "measure_level_tier":
        return _level_tier(event, cfg, view, words, event_texts if event_texts is not None else view.event(event.id))
    if event.type == "level_bonus_per_measure":
        return _level_bonus(event, words)
    if event.type == "and_condition":
        return _and_condition(event, cfg, view, words)
    return _budget_review(event, cfg, words)
