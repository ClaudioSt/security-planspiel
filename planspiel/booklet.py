"""Print model of the team booklet in calculation order (PRINT-07, D-05, D-08): planning first, RoS and Budget Review last.

Every number comes from config through `rules`, `review_text`, `eventtext` and `fmt`; every word comes from
`content/texte.toml` through `PreAttackView`. No value is written twice: start levels exist only in the planning
table, the sums are carried by the player from page to page, and a formula line names its operands instead of
asking for them again. The own costs follow `rules.security_spend` (Init, Init differences of the change windows,
OPEX; never an event effect, RULE-06); the remaining budget follows `rules.budget_ledger`. The Final-Index is a
facilitator comparator and has no place here (D-23).

The module is a pre-wave builder: it reads the veiled attack titles and the wave count, never a wave's weights,
thresholds or bonus data, and nothing under the revealed text namespace (VEIL-02).

The register page opens the booklet with the protection-need table (PROT-02, D-05) and the risk register below it;
its rows and € bands come from `cfg.risk_matrix` through `planspiel.risk`.
"""
from dataclasses import dataclass
from typing import Optional

from planspiel import fmt, risk, rules
from planspiel.cards import printed_strings
from planspiel.config import Config
from planspiel.eventtext import EFFECT_KINDS
from planspiel.printmodel import PrintModelError
from planspiel.texts import PreAttackView, Texts

BOOKLET_JOB = "spieler-teamheft"
EN_DASH = "–"
# Register rows the one-page register is proven for by the PDF fill report; a larger `register_rows` needs a new
# layout proof of that page.
MAX_REGISTER_ROWS = 5
# Asset rows the one-page protection-need table is proven for by the PDF fill report; a larger `asset_rows` needs a
# new layout proof of that page.
MAX_ASSET_ROWS = 4
# Ranks start at one; the last rank is `register_rows`.
RANK_FIRST = 1

# The tracking sheet (PRINT-08): rows in calculation order. `remaining` closes the wave columns; the Budget Review
# column adds the two rows `kz_review` and `kz_final` below it. A cell is written (WRITE) or crossed out (SHADED).
TRACKING_ROW_ORDER = (
    "kz_before", "kz_change", "kz_after", "damage", "own_init", "own_opex", "own_window", "external_budget",
    "external_opex", "remaining",
)
REVIEW_ROWS = ("kz_review", "kz_final")
WRITE = "write"
SHADED = "shaded"
# Change windows the one-page measure grid is proven for (two columns per window). Today: after waves 1 and 2.
MAX_WINDOWS = 2


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
    planning_hint: str
    planning_header: tuple[str, ...]
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
    result_line: Metric  # write-in line for the KZ change; the value comes from the event card, never from this page

    def printed_fragments(self) -> tuple[str, ...]:
        return _fragments(self)


@dataclass(frozen=True)
class TrackingRow:
    """One row of the tracking table: its label and one cell state per column (`WRITE` or `SHADED`)."""

    key: str
    label: str
    group: str  # "kz", "damage", "own", "external", "budget", "review" or "window"
    cells: tuple[str, ...]


@dataclass(frozen=True)
class WindowBlock:
    """One change window: every measure once, and the summary labels that apply to this window."""

    after_wave: str
    measure_rows: tuple[str, ...]
    with_credit: bool
    summary_rows: tuple[str, ...]


@dataclass(frozen=True)
class TrackingPage:
    title: str
    intro: str
    columns: tuple[str, ...]
    rows: tuple[TrackingRow, ...]
    block_own: str
    block_external: str
    clamp_text: str
    hints: tuple[str, ...]
    window_intro: str
    measure_header: str
    window_columns: tuple[str, str]
    windows: tuple[WindowBlock, ...]
    summary_rows: tuple[TrackingRow, ...]  # one cell per window
    window_hints: tuple[str, ...]

    def printed_fragments(self) -> tuple[str, ...]:
        return _fragments(self)


@dataclass(frozen=True)
class RegisterPage:
    page_title: str
    need_title: str
    need_instruction: str
    need_header: tuple[str, str, str, str, str]
    asset_rows: tuple[str, ...]
    need_example: tuple[str, str, str, str, str]
    legend_title: str
    band_legend: tuple[str, ...]
    title: str
    instruction: str
    rank_hint: str
    example_label: str
    header: tuple[str, str, str, str, str, str, str]
    example: tuple[str, str, str, str, str, str, str]
    rows: tuple[str, ...]
    goal_ticks: tuple[str, ...]
    category_ticks: tuple[str, ...]
    decision_ticks: tuple[str, ...]
    review_ticks: tuple[str, ...]
    source_label: str
    reason_label: str
    review_hint: str
    band_labels: tuple[str, ...]

    def printed_fragments(self) -> tuple[str, ...]:
        return _fragments(self)


@dataclass(frozen=True)
class TeamBooklet:
    job: str
    register: Optional[RegisterPage]
    planning: PlanningPage
    tracking: TrackingPage
    ros: RosPage

    def printed_fragments(self) -> tuple[str, ...]:
        register = self.register.printed_fragments() if self.register is not None else ()
        return tuple(
            dict.fromkeys(
                (
                    *register,
                    *self.planning.printed_fragments(),
                    *self.tracking.printed_fragments(),
                    *self.ros.printed_fragments(),
                )
            )
        )


def _fragments(page: object) -> tuple[str, ...]:
    """Every string of a page that ends up on the paper, without duplicates and without empty strings."""
    return tuple(dict.fromkeys(text for text in printed_strings(page) if text))


def _register_page(cfg: Config, texts: Texts) -> Optional[RegisterPage]:
    matrix = cfg.risk_matrix
    if matrix is None:
        return None
    if matrix.register_rows > MAX_REGISTER_ROWS:
        raise PrintModelError(
            f"Das Risikoregister hat {matrix.register_rows} Zeilen, die Seite ist für höchstens {MAX_REGISTER_ROWS} "
            "belegt (MAX_REGISTER_ROWS in planspiel/booklet.py); die Konstante nur zusammen mit einem neuen "
            "Layout-Nachweis dieser Seite anheben."
        )
    if matrix.asset_rows > MAX_ASSET_ROWS:
        raise PrintModelError(
            f"Die Schutzbedarfstabelle hat {matrix.asset_rows} Zeilen, die Seite ist für höchstens {MAX_ASSET_ROWS} "
            "belegt (MAX_ASSET_ROWS in planspiel/booklet.py); die Konstante nur zusammen mit einem neuen "
            "Layout-Nachweis dieser Seite anheben."
        )
    words = PreAttackView(cfg, texts).sheet("register")
    asset_rows = tuple(
        f"{words['asset_prefix']}{fmt.format_number(number)}" for number in range(1, matrix.asset_rows + 1)
    )
    band_labels = tuple(words["bands"][band.id] for band in matrix.bands)
    need = words["need_example"]
    rated = tuple(need[goal] for goal in ("c", "i", "a"))
    for goal, word in zip(("c", "i", "a"), rated):
        if word not in band_labels:
            raise PrintModelError(
                f"sheets.register.need_example.{goal} ist '{word}', kein Bandwort ({', '.join(band_labels)})"
            )
    highest = max(rated, key=band_labels.index)
    rows = tuple(f"{words['risk_prefix']}{fmt.format_number(number)}" for number in range(1, matrix.register_rows + 1))
    last_rank = fmt.format_number(matrix.register_rows)
    example = words["example"]
    goals = words["goals"]
    return RegisterPage(
        page_title=words["page_title"],
        need_title=words["need_title"],
        need_instruction=words["need_instruction"],
        need_header=(words["need_head_asset"], goals["c"], goals["i"], goals["a"], words["head_total"]),
        asset_rows=asset_rows,
        need_example=(f"{asset_rows[0]} {need['asset']}", *rated, highest),
        legend_title=words["legend_title"],
        band_legend=tuple(
            f"{label}: {span}" for label, span in zip(band_labels, risk.band_ranges(matrix.bands, words))
        ),
        title=words["title"],
        instruction=words["instruction"],
        rank_hint=f"{words['rank_hint']} {fmt.format_number(RANK_FIRST)} {EN_DASH} {last_rank}",
        example_label=words["example_label"],
        header=tuple(
            words[name]
            for name in (
                "head_asset", "head_threat", "head_goal", "head_impact", "head_rank", "head_decision", "head_review"
            )
        ),
        example=(
            asset_rows[0], example["threat"], example["goal"], example["impact"], fmt.format_number(RANK_FIRST),
            example["decision"], words["review"]["correct"],
        ),
        rows=rows,
        goal_ticks=tuple(words["goals"][name] for name in ("c", "i", "a")),
        category_ticks=tuple(words["categories"][name] for name in ("production", "customer", "knowhow", "costs")),
        decision_ticks=tuple(words["decision"][name] for name in ("treat", "accept")),
        review_ticks=tuple(words["review"][name] for name in ("correct", "under", "over")),
        source_label=words["source_label"],
        reason_label=words["reason_label"],
        review_hint=words["review_hint"],
        band_labels=band_labels,
    )


def _planning_page(cfg: Config, texts: Texts) -> PlanningPage:
    view = PreAttackView(cfg, texts)
    budget, labels, words = view.sheet("budget"), view.sheet("labels"), view.sheet("teamheft")
    waves = len(cfg.waves)
    wave_count_text = f"{fmt.TIMES} {waves}"
    anticipated_line = (
        f"{labels['anticipated_sum']} = {labels['sum']} {labels['init_costs']} + {labels['sum']} "
        f"{words['opex_per_wave']} {wave_count_text} ="
    )
    planning_header = (labels["measure"], labels["level"], labels["init_costs"], words["opex_per_wave"])
    planning_hint = ""
    if cfg.risk_matrix is not None:
        register = view.sheet("register")
        planning_header += (register["planning_column"],)
        planning_hint = register["planning_hint"]
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
        planning_hint=planning_hint,
        planning_header=planning_header,
        planning_rows=tuple(f"{measure_id} {EN_DASH} {measure.name}" for measure_id, measure in cfg.measures.items()),
        sum_label=labels["sum"],
        wave_count_text=wave_count_text,
        anticipated_line=anticipated_line,
    )


def _ros_page(cfg: Config, texts: Texts) -> RosPage:
    view = PreAttackView(cfg, texts)
    labels, words = view.sheet("labels"), view.sheet("teamheft")
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
        result_line=Metric(words["review_result"], words["review_result_note"]),
    )


def _event_kinds(cfg: Config, wave_id: int) -> set[str]:
    return {EFFECT_KINDS[event.type] for event in cfg.events.get(wave_id, [])}


def _tracking_rows(cfg: Config, view: PreAttackView) -> tuple[TrackingRow, ...]:
    words, labels = view.sheet("tracking"), view.sheet("labels")
    wave_ids = [wave.wave_id for wave in cfg.waves]

    def cells(*, start: bool = False, wave=None, review: bool = False) -> tuple[str, ...]:
        """Cell states of one row: the Start column, one column per wave (`wave(index, wave_id)`), the review."""
        flags = [wave(index, wave_id) if wave else False for index, wave_id in enumerate(wave_ids)]
        return tuple(WRITE if flag else SHADED for flag in (start, *flags, review))

    def every_wave(index: int, wave_id: int) -> bool:
        return True

    def before_window(index: int, wave_id: int) -> bool:
        return index < len(wave_ids) - 1

    def with_event(kind: str):
        return lambda index, wave_id: kind in _event_kinds(cfg, wave_id)

    final = f"{words['row_kz_final']} = {words['kz_after_last']} + {words['row_kz_review']}"
    spec = (
        ("kz_before", words["row_kz_before"], "kz", cells(start=True, wave=every_wave)),
        ("kz_change", words["row_kz_change"], "kz", cells(wave=every_wave)),
        ("kz_after", words["row_kz_after"], "kz", cells(wave=every_wave)),
        ("damage", words["row_damage"], "damage", cells(wave=every_wave)),
        ("own_init", labels["init_costs"], "own", cells(start=True)),
        ("own_opex", words["row_own_opex"], "own", cells(wave=every_wave)),
        ("own_window", words["row_own_window"], "own", cells(wave=before_window)),
        ("external_budget", words["row_external_budget"], "external", cells(wave=with_event("external_budget"))),
        ("external_opex", words["row_external_opex"], "external", cells(wave=with_event("external_opex"))),
        ("remaining", words["row_remaining"], "budget", cells(start=True, wave=every_wave, review=True)),
        ("kz_review", words["row_kz_review"], "review", cells(review=True)),
        ("kz_final", final, "review", cells(review=True)),
    )
    assert tuple(key for key, *_ in spec) == (*TRACKING_ROW_ORDER, *REVIEW_ROWS)
    return tuple(TrackingRow(*item) for item in spec)


def _windows(cfg: Config, view: PreAttackView) -> tuple[tuple[WindowBlock, ...], tuple[TrackingRow, ...]]:
    words = view.sheet("tracking")
    gaps = cfg.waves[:-1]
    if len(gaps) > MAX_WINDOWS:
        raise PrintModelError(
            f"Die Config hat {len(gaps)} Change-Fenster, das Raster des Tracking-Bogens ist für höchstens "
            f"{MAX_WINDOWS} belegt (MAX_WINDOWS in planspiel/booklet.py); die Konstante nur zusammen mit einem "
            "neuen Layout-Nachweis dieser Seite anheben."
        )
    kurswechsel = rules.kurswechsel_wave(cfg.events)
    credits = [wave.wave_id == kurswechsel for wave in gaps]
    net_formula = f"{words['window_net']} = {words['window_sum']}"
    if any(credits):
        net_formula += f" {fmt.MINUS} {words['window_credit_short']}"
    net = f"{net_formula}, {words['never_refund']}"
    measures = tuple(f"{measure_id} {EN_DASH} {measure.name}" for measure_id, measure in cfg.measures.items())
    blocks = tuple(
        WindowBlock(
            after_wave=f"{words['window_title']} {wave.wave_id}",
            measure_rows=measures,
            with_credit=with_credit,
            summary_rows=(words["window_sum"], *((words["window_credit"],) if with_credit else ()), net),
        )
        for wave, with_credit in zip(gaps, credits)
    )
    summary = [TrackingRow("window_sum", words["window_sum"], "window", (WRITE,) * len(gaps))]
    if any(credits):
        summary.append(
            TrackingRow(
                "window_credit", words["window_credit"], "window", tuple(WRITE if has else SHADED for has in credits)
            )
        )
    summary.append(TrackingRow("window_net", net, "window", (WRITE,) * len(gaps)))
    return blocks, tuple(summary)


def build_tracking_page(cfg: Config, texts: Texts) -> TrackingPage:
    view = PreAttackView(cfg, texts)
    words, labels, teamheft = view.sheet("tracking"), view.sheet("labels"), view.sheet("teamheft")
    columns = (
        labels["start"],
        *(f"{words['wave']} {wave.wave_id}" for wave in cfg.waves),
        teamheft["review_title"],
    )
    remaining = (
        f"{teamheft['remaining_budget']} = {words['remaining_previous']} + {words['row_external_budget']} "
        f"{fmt.MINUS} {words['row_own_opex']} {fmt.MINUS} {words['row_own_window']} "
        f"{fmt.MINUS} {words['row_external_opex']}. {labels['start']}: {teamheft['tier_budget']} "
        f"{fmt.MINUS} {labels['init_costs']}."
    )
    blocks, summary = _windows(cfg, view)
    return TrackingPage(
        title=words["title"],
        intro=words["intro"],
        columns=columns,
        rows=_tracking_rows(cfg, view),
        block_own=words["block_own"],
        block_external=words["block_external"],
        clamp_text=f"{words['clamp_lead']} {rules.KZ_MIN} {words['clamp_to']} {rules.KZ_MAX}",
        hints=(words["rounding_hint"], words["external_hint"], remaining),
        window_intro=words["window_intro"],
        measure_header=labels["measure"],
        window_columns=(words["window_level"], words["window_delta"]),
        windows=blocks,
        summary_rows=summary,
        window_hints=(words["credit_hint"], words["next_wave_hint"]),
    )


def build_team_booklet(cfg: Config, texts: Texts) -> TeamBooklet:
    return TeamBooklet(
        job=BOOKLET_JOB,
        register=_register_page(cfg, texts),
        planning=_planning_page(cfg, texts),
        tracking=build_tracking_page(cfg, texts),
        ros=_ros_page(cfg, texts),
    )
