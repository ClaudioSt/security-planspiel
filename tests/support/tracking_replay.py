"""Second encoding of the printed tracking procedure (PRINT-08, T-05-25): fills the rows in printed order.

A team fills the sheet from what it holds in its hands: the card costs, the once-rounded KZ change and the damage of
each attack worksheet, the effect values printed on the event cards and the clamp bounds printed on the sheet. This
module does exactly that, column by column, top to bottom, with plain integer arithmetic. It never imports or calls
the path evaluator, the wave simulator or the budget ledger of `planspiel.rules`, so a match with `evaluate_path`
proves the printed procedure and not a shared implementation.
"""
from dataclasses import dataclass
from typing import Optional

from planspiel import review_text
from planspiel.eventtext import EFFECT_KINDS, effect_rows
from planspiel.rules import KZ_MAX, KZ_MIN, card_facts


@dataclass(frozen=True)
class TrackingResult:
    levels: tuple  # the level of every measure in each wave, as the measure grid leaves them
    kz_before: tuple
    kz_change: tuple
    kz_after: tuple
    damages: tuple
    own_init: int
    own_opex: tuple
    increases: tuple  # per window: Summe Init-Erhöhungen
    credits: tuple  # per window: Kurswechsel: Gutschrift Kunde (0 without a swap)
    window_nets: tuple  # per window: Init-Differenz netto
    external_budget: tuple
    external_opex: tuple
    remaining: tuple  # Start column, then one per wave
    remaining_final: int
    own_spend: int
    kz_review: int
    kz_final: int


def _clamp(value: int) -> int:
    """The sentence under the table: limited to the printed bounds."""
    return max(KZ_MIN, min(KZ_MAX, value))


def _review_change(cfg, remaining_k: int) -> int:
    """Read the KZ change of the Budget Review off the printed tier table or the printed overspend table."""
    event = next(event for event in cfg.final_events if EFFECT_KINDS[event.type] == "review")
    remaining_eur = remaining_k * 1000
    if remaining_eur >= 0:
        for low, high, kz in review_text.tier_rows(event.params["tiers"]):
            if remaining_eur >= low and (high is None or remaining_eur <= high):
                return kz
        raise AssertionError("no tier row covers the remaining budget")
    penalty = event.params["overspend_penalty"]
    overspend = -remaining_eur
    for low, high, kz in review_text.penalty_rows(penalty["kz_per_step"], penalty["step"]):
        if low <= overspend <= high:
            return kz
    return -KZ_MAX  # beyond the printed table the penalty alone exceeds the whole scale


def _event_effect(cfg, texts, wave_id: int, kind: str) -> Optional[int]:
    """The value printed on the event card of that kind in that wave, None when the wave has none."""
    for event in cfg.events.get(wave_id, []):
        if EFFECT_KINDS[event.type] == kind:
            return effect_rows(event, cfg, texts).rows[0].value
    return None


def replay_tracking(cfg, tier_name, path, worksheet_changes, damages, texts, ignore_credit=False) -> TrackingResult:
    """Fill the printed rows for a legal path. `ignore_credit` leaves the credit row empty (negative control)."""
    tier = cfg.budget_tiers[tier_name]
    measure_ids = list(cfg.measures)

    # The measure grid: only changed measures are written, blank means unchanged.
    grids = []
    levels = dict(path.start)
    for window in path.windows:
        grid = {m: window.selection[m] for m in measure_ids if window.selection[m] != levels[m]}
        grids.append((levels, grid, window.swap))
        levels = {**levels, **grid}

    current = dict(path.start)
    per_wave_levels = []
    for index in range(len(cfg.waves)):
        per_wave_levels.append(dict(current))
        if index < len(grids):
            current = {**current, **grids[index][1]}

    def init_of(measure_id, level):
        return card_facts(cfg.measures, measure_id, level).init_k

    # Start column: Init-Kosten, KZ vor der Welle = Start-KZ of the tier, Restbudget = Tier-Budget - Init.
    own_init = sum(init_of(m, level) for m, level in path.start.items())
    remaining = [tier.budget - own_init]
    kz = tier.kz_start

    kz_before, kz_after, own_opex, increases, credits, window_nets = [], [], [], [], [], []
    external_budget, external_opex = [], []
    for index, wave in enumerate(cfg.waves):
        selection = per_wave_levels[index]
        kz_before.append(kz)
        kz = _clamp(kz + worksheet_changes[index])
        kz_after.append(kz)

        opex = sum(card_facts(cfg.measures, m, level).opex_k for m, level in selection.items())
        own_opex.append(opex)
        active = sum(1 for level in selection.values() if level >= 1)
        budget_value = _event_effect(cfg, texts, wave.wave_id, "external_budget") or 0
        opex_value = (_event_effect(cfg, texts, wave.wave_id, "external_opex") or 0) * active
        external_budget.append(budget_value)
        external_opex.append(opex_value)

        window_net = 0
        if index < len(grids):
            before, grid, swap = grids[index]
            rise = sum(max(0, init_of(m, level) - init_of(m, before[m])) for m, level in grid.items())
            credit = 0
            if swap is not None and not ignore_credit:
                dropped, incoming = swap
                credit = min(init_of(dropped, before[dropped]), init_of(incoming, grid[incoming]))
            increases.append(rise)
            credits.append(credit)
            window_net = rise - credit
            window_nets.append(window_net)

        remaining.append(remaining[-1] + budget_value - opex - window_net - opex_value)

    own_spend = own_init + sum(own_opex) + sum(window_nets)
    review = _review_change(cfg, remaining[-1])
    return TrackingResult(
        levels=tuple(per_wave_levels),
        kz_before=tuple(kz_before),
        kz_change=tuple(worksheet_changes),
        kz_after=tuple(kz_after),
        damages=tuple(damages),
        own_init=own_init,
        own_opex=tuple(own_opex),
        increases=tuple(increases),
        credits=tuple(credits),
        window_nets=tuple(window_nets),
        external_budget=tuple(external_budget),
        external_opex=tuple(external_opex),
        remaining=tuple(remaining),
        remaining_final=remaining[-1],
        own_spend=own_spend,
        kz_review=review,
        kz_final=_clamp(kz_after[-1] + review),
    )
