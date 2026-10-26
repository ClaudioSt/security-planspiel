"""Print model of the team booklet in calculation order (PRINT-07, D-05, D-08): planning first, RoS and Budget Review last.

Every number comes from config through `rules`, `review_text`, `eventtext` and `fmt`; every word comes from
`content/texte.toml` through `PreAttackView`. No value is written twice: start levels exist only in the planning
table, the sums are carried by the player from page to page, and a formula line names its operands instead of
asking for them again. The own costs follow `rules.security_spend` (Init, Init differences of the change windows,
OPEX; never an event effect, RULE-06); the remaining budget follows `rules.budget_ledger`. The Final-Index is a
facilitator comparator and has no place here (D-23).

The module is a pre-wave builder: it reads the veiled attack titles and the wave count, never a wave's weights,
thresholds or bonus data, and nothing under the revealed text namespace (VEIL-02).
"""
from dataclasses import dataclass

from planspiel import fmt, rules
from planspiel.cards import printed_strings
from planspiel.config import Config
from planspiel.eventtext import effect_rows
from planspiel.printmodel import PrintModelError
from planspiel.review_text import _tier_value_text, format_eur, penalty_rows, tier_rows
from planspiel.texts import PreAttackView, Texts

BOOKLET_JOB = "spieler-teamheft"
# Rows of today's overspend table (X = 9 KZ per started step): rows until the penalty alone reaches the KZ cap of 100,
# ceil(100 / 9) = 12. The Budget Review page is proven (pdf test, fill report) for at most this many rows. Phase 6
# calibrates X; a smaller X adds rows, so the constant is reviewed together with a new layout proof of that page.
MAX_PENALTY_ROWS = 12
EN_DASH = "–"


@dataclass(frozen=True)
class Metric:
    """One `Kennzahl | Wert` row: the label, and a grey formula line under it that names the operands ('' for none)."""

    label: str
    note: str


@dataclass(frozen=True)
class PlanningPage:
    title: str
    intro: str
    step_costs: str
    cost_header: tuple[str, str, str]
    cost_rows: tuple[tuple[str, str, str], ...]
    step_tiers: str
    tier_intro: str
    tier_header: tuple[str, str, str]
    tier_rows: tuple[tuple[str, str, str], ...]
    step_planning: str
    planning_intro: str
    planning_instruction: str
    planning_header: tuple[str, str, str, str]
    planning_rows: tuple[str, ...]
    sum_label: str
    wave_count_text: str
    anticipated_line: str

    def printed_fragments(self) -> tuple[str, ...]:
        return _fragments(self)


@dataclass(frozen=True)
class RosPage:
    title: str
    purpose: str
    instruction: str
    carry_hint: str
    metric_header: tuple[str, str]
    own_cost_rows: tuple[Metric, ...]
    damage_rows: tuple[Metric, ...]
    damage_sum: Metric
    avoided_line: Metric
    ros_line: Metric
    review_title: str
    review_intro: str
    sign_hint: str
    budget_rows: tuple[Metric, ...]
    remaining_line: Metric
    tier_header: tuple[str, str]
    tier_rows: tuple[tuple[str, str], ...]
    overspend_rule: str
    penalty_title: str
    penalty_intro: str
    penalty_header: tuple[str, str]
    penalty_rows: tuple[tuple[str, str], ...]

    def printed_fragments(self) -> tuple[str, ...]:
        return _fragments(self)


@dataclass(frozen=True)
class TeamBooklet:
    job: str
    planning: PlanningPage
    ros: RosPage

    def printed_fragments(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys((*self.planning.printed_fragments(), *self.ros.printed_fragments())))


def _fragments(page: object) -> tuple[str, ...]:
    """Every string of a page that ends up on the paper, without duplicates and without empty strings."""
    return tuple(dict.fromkeys(text for text in printed_strings(page) if text))


def _review_event(cfg: Config):
    for event in cfg.final_events:
        if event.type == "final_budget_tier":
            return event
    raise PrintModelError("Die Config hat kein Budget-Review-Event (final_budget_tier)")


def _planning_page(cfg: Config, texts: Texts) -> PlanningPage:
    view = PreAttackView(cfg, texts)
    budget, labels, words = view.sheet("budget"), view.sheet("labels"), view.sheet("teamheft")
    waves = len(cfg.waves)
    wave_count_text = f"{fmt.TIMES} {waves}"
    anticipated_line = (
        f"{labels['anticipated_sum']} = {labels['sum']} {labels['init_costs']} + {labels['sum']} "
        f"{words['opex_per_wave']} {wave_count_text} ="
    )
    return PlanningPage(
        title=words["planning_title"],
        intro=budget["intro"],
        step_costs=words["step_costs"],
        cost_header=(labels["cost_type"], labels["what"], labels["when"]),
        cost_rows=(
            (labels["init_costs"], budget["init_what"], budget["init_when"]),
            (labels["opex"], budget["opex_what"], budget["opex_when"]),
        ),
        step_tiers=words["step_tiers"],
        tier_intro=budget["tier_intro"],
        tier_header=(labels["tier"], labels["available_budget"], words["kz_start"]),
        tier_rows=tuple(
            (name.capitalize(), fmt.format_money(tier.budget * 1000), str(tier.kz_start))
            for name, tier in cfg.budget_tiers.items()
        ),
        step_planning=words["step_planning"],
        planning_intro=budget["anticipated_sum_intro"],
        planning_instruction=words["planning_instruction"],
        planning_header=(labels["measure"], labels["level"], labels["init_costs"], words["opex_per_wave"]),
        planning_rows=tuple(f"{measure_id} {EN_DASH} {measure.name}" for measure_id, measure in cfg.measures.items()),
        sum_label=labels["sum"],
        wave_count_text=wave_count_text,
        anticipated_line=anticipated_line,
    )


def _tier_texts(cfg: Config, texts: Texts) -> tuple[tuple[str, str], ...]:
    """Restbudget tiers as (span, KZ change), with the same inclusive boundaries as the Budget Review card."""
    start = PreAttackView(cfg, texts).sheet("eventkarten")["tier_from"]
    rows = []
    for index, (from_eur, to_eur, kz) in enumerate(tier_rows(_review_event(cfg).params["tiers"])):
        if index == 0 and to_eur is not None:
            span = f"{format_eur(from_eur)} {EN_DASH} {format_eur(to_eur)} €"
        else:
            span = f"{start} {format_eur(from_eur)} €"
        rows.append((span, _tier_value_text(kz)))
    return tuple(rows)


def _penalty_texts(cfg: Config) -> tuple[tuple[str, str], ...]:
    rows = penalty_rows(*rules.penalty_params(cfg.final_events))
    if len(rows) > MAX_PENALTY_ROWS:
        raise PrintModelError(
            f"Die Überziehungstabelle hat {len(rows)} Zeilen, die Budget-Review-Seite ist für höchstens "
            f"{MAX_PENALTY_ROWS} belegt (MAX_PENALTY_ROWS in planspiel/booklet.py); die Konstante nur zusammen "
            "mit einem neuen Layout-Nachweis dieser Seite anheben, wenn Phase 6 die Strafe je Schritt senkt."
        )
    return tuple(
        (f"{format_eur(low)} {EN_DASH} {format_eur(high)} €", _tier_value_text(kz)) for low, high, kz in rows
    )


def _ros_page(cfg: Config, texts: Texts) -> RosPage:
    view = PreAttackView(cfg, texts)
    labels, words, eventkarten = view.sheet("labels"), view.sheet("teamheft"), view.sheet("eventkarten")
    final = _review_event(cfg)
    base_losses = fmt.format_money(rules.base_losses(cfg.waves, cfg.attacks) * 1000)

    total_init, total_opex = labels["total_init"], labels["total_opex"]
    own, damage_sum = words["own_costs"], words["damage_sum"]
    own_cost_rows = (
        Metric(total_init, ""),
        Metric(words["window_differences"], ""),
        Metric(total_opex, ""),
        Metric(own, f"= {total_init} + {words['init_differences']} + {total_opex}"),
    )
    avoided = Metric(labels["avoided_damage"], f"= {base_losses} {fmt.MINUS} {damage_sum}")
    ros_line = Metric(words["ros_short"], f"= ({avoided.label} {fmt.MINUS} {own}) {fmt.DIVIDED} {own}")

    tier_budget, budget_event = words["tier_budget"], words["budget_event"]
    available, event_opex, costs = labels["available_budget"], words["event_opex"], words["review_costs"]
    budget_rows = (
        Metric(tier_budget, ""),
        Metric(budget_event, ""),
        Metric(available, f"= {tier_budget} + {budget_event}"),
        Metric(own, ""),
        Metric(event_opex, ""),
        Metric(costs, f"= {own} + {event_opex}"),
    )
    remaining = Metric(words["remaining_budget"], f"= {available} {fmt.MINUS} {costs}")

    return RosPage(
        title=words["ros_title"],
        purpose=view.sheet("ros")["purpose"],
        instruction=view.sheet("ros")["instruction"],
        carry_hint=words["ros_carry_hint"],
        metric_header=(labels["metric"], labels["value"]),
        own_cost_rows=own_cost_rows,
        damage_rows=tuple(Metric(f"{labels['damage']} {view.attack_title(wave)}", "") for wave in cfg.waves),
        damage_sum=Metric(damage_sum, ""),
        avoided_line=avoided,
        ros_line=ros_line,
        review_title=words["review_title"],
        review_intro=words["review_intro"],
        sign_hint=words["sign_hint"],
        budget_rows=budget_rows,
        remaining_line=remaining,
        tier_header=(eventkarten["tier_heading"], words["kz_change"]),
        tier_rows=_tier_texts(cfg, texts),
        overspend_rule=effect_rows(final, cfg, texts).rows[-1].text,
        penalty_title=words["penalty_title"],
        penalty_intro=words["penalty_intro"],
        penalty_header=(words["overspend_header"], words["kz_change"]),
        penalty_rows=_penalty_texts(cfg),
    )


def build_team_booklet(cfg: Config, texts: Texts) -> TeamBooklet:
    return TeamBooklet(job=BOOKLET_JOB, planning=_planning_page(cfg, texts), ros=_ros_page(cfg, texts))
