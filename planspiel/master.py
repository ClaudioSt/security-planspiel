"""Print model of the facilitator master sheet: parameters, check rows, event schedule, answer keys, clue matrix
(PRINT-10, D-17..D-23, ROADMAP SC4).

Facilitator-only: the sheet reads revealed texts (attack names, bonus reasons, the clue matrix) through `RevealView` and
`FacilitatorView` and must never be handed to players; the `spielleitung-` job prefix keeps it out of the pre-wave
veil scan (VEIL-02). Every number comes from `rules` (`worksheet_constants`, `path_trace`, `final_index`), `eventtext`,
`review_text` and `practice`; this module only formats and orders. Values with no finite decimal form (the 17/7 slope,
RoS, final index) are printed with `fmt.format_approx` and appear on this sheet only (D-26 Q6).

The answer keys follow the reference paths pinned in the config (`reference_plans`, 05-14): the build stops with a
`PrintModelError` when a tier has no path, a path is illegal or over budget, or it lacks a voluntary move.
"""
import dataclasses
from dataclasses import dataclass
from typing import Optional

from planspiel import eventtext, fmt, practice, refpaths, rules
from planspiel.cards import printed_strings
from planspiel.config import Config, Wave
from planspiel.printmodel import PrintModelError
from planspiel.texts import Clue, FacilitatorView, RevealView, Texts

MASTER_JOB = "spielleitung-uebersicht"
DASH = "–"
ARROW = "→"
MINUS = fmt.MINUS
APPROX = "≈"

# The answer-key rows of one wave, in calculation order (the order of the worksheet steps).
KEY_ROW_IDS = (
    "selection", "cia", "e_value", "bonus", "gr", "case", "damage_before", "recovery", "damage_after",
    "kz_attack", "kz_event", "kz_exact", "kz_change", "kz_before", "kz_unclamped", "kz_after",
    "own_opex", "window_cost", "external_budget", "external_opex", "remaining",
)
FINAL_ROW_IDS = ("remaining", "review_delta", "kz_final", "own_spend", "total_damage", "ros", "final_index")
EFFECT_KIND_KEYS = {
    "window": "kind_window",
    "external_opex": "kind_external_opex",
    "external_budget": "kind_external_budget",
    "kz": "kind_kz",
    "review": "kind_review",
}


@dataclass(frozen=True)
class ParameterBlock:
    rows: tuple[tuple[str, str], ...]
    bonus_header: tuple[str, str, str, str]
    bonus_rows: tuple[tuple[str, str, str, str], ...]


@dataclass(frozen=True)
class CheckRows:
    case_header: tuple[str, str, str]
    case_rows: tuple[tuple[str, str, str], ...]
    table_header: tuple[str, str, str]
    table_rows: tuple[tuple[str, str, str], ...]


@dataclass(frozen=True)
class EventScheduleRow:
    name: str
    kind: str
    heading: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class AnswerKeyRow:
    key: str
    label: str
    values: tuple[str, ...]


@dataclass(frozen=True)
class WaveSection:
    wave_id: int
    title: str
    parameters: ParameterBlock
    checks: CheckRows
    events: tuple[EventScheduleRow, ...]
    no_events: str
    key_header: tuple[str, ...]
    key_rows: tuple[AnswerKeyRow, ...]


@dataclass(frozen=True)
class PathLine:
    tier: str
    start: str
    windows: tuple[str, ...]


@dataclass(frozen=True)
class ReviewSection:
    title: str
    intro: str
    tier_heading: str
    tier_lines: tuple[str, ...]
    x_label: str
    x_value: str
    step_label: str
    step_value: str


@dataclass(frozen=True)
class TierResult:
    tier: str
    remaining: str
    review_delta: str
    kz_final: str
    own_spend: str
    total_damage: str
    ros: str
    final_index: str


@dataclass(frozen=True)
class WelleZeroKey:
    title: str
    intro: str
    header: tuple[str, ...]
    rows: tuple[AnswerKeyRow, ...]


@dataclass(frozen=True)
class ClueEntry:
    number: str
    document: str
    section: str
    quote: str
    why: str
    measures: str


@dataclass(frozen=True)
class ClueGroup:
    title: str
    rows: tuple[ClueEntry, ...]


@dataclass(frozen=True)
class MasterSheet:
    job: str
    title: str
    notice: str
    intro: str
    gr_legend: str
    contents_title: str
    how_to_title: str
    how_to: tuple[str, ...]
    approx_hint: str
    paths_title: str
    paths_intro: str
    path_start: str
    paths: tuple[PathLine, ...]
    params_title: str
    check_title: str
    check_table_intro: str
    events_title: str
    event_header: tuple[str, str, str]
    keys_title: str
    keys_intro: str
    waves: tuple[WaveSection, ...]
    review: ReviewSection
    tiers: tuple[TierResult, ...]
    final_title: str
    final_intro: str
    final_note: str
    final_header: tuple[str, ...]
    final_rows: tuple[AnswerKeyRow, ...]
    final_weight_label: str
    final_weight_value: str
    welle0: Optional[WelleZeroKey]
    bonus_title: str
    clues_title: str
    clues_intro: str
    clue_header: tuple[str, str, str, str, str, str]
    clue_groups: tuple[ClueGroup, ...]

    def printed_fragments(self) -> tuple[str, ...]:
        """Every string of the sheet that ends up on the paper, without duplicates and without empty strings."""
        found = [
            text
            for field in dataclasses.fields(self)
            if field.name != "job"
            for text in printed_strings(getattr(self, field.name))
        ]
        return tuple(dict.fromkeys(text for text in found if text))


def approx_signed(value) -> str:
    """Signed value on the facilitator sheet: exact text with a sign, or `≈` plus the two-decimal value with a sign."""
    text = fmt.format_approx(value)
    if not text.startswith(APPROX):
        return fmt.format_signed(value)
    number = text[len(APPROX) + 1:]
    return f"{APPROX} {number}" if number.startswith(MINUS) else f"{APPROX} +{number}"


def selection_text(selection) -> str:
    """The active measures of a selection as `M4 L1, M6 L3`."""
    return ", ".join(f"{measure_id} L{level}" for measure_id, level in selection.items() if level > 0)


def _measure_label(cfg: Config, measure_id: str) -> str:
    return f"{measure_id} {DASH} {cfg.measures[measure_id].name}"


def _parameters(cfg: Config, wave: Wave, constants, view: RevealView, words: dict, attack: dict) -> ParameterBlock:
    angriff = view.sheet("angriff")
    slope = fmt.format_factor(constants.slope)
    if not fmt.terminates(constants.slope):
        slope = f"{slope} ({fmt.format_approx(constants.slope)})"
    if constants.with_recovery:
        factors = ", ".join(f"L{row.level} {fmt.format_percent(row.factor)}" for row in constants.recovery_rows)
        recovery = f"{words['recovery_allowed']} {_measure_label(cfg, constants.recovery_measure)}: {factors}"
    else:
        recovery = words["recovery_not_allowed"]
    weights = " / ".join(fmt.format_number(weight) for weight in (constants.w_c, constants.w_i, constants.w_a))
    rows = (
        (words["param_weights"], weights),
        (angriff["label_threshold"], fmt.format_number(constants.lower)),
        (angriff["label_cap"], fmt.format_number(constants.reduction_cap)),
        (angriff["label_upper"], fmt.format_number(constants.upper)),
        (words["param_unit"], fmt.format_money(constants.unit_eur)),
        (words["param_slope"], slope),
        (words["param_kz_full_damage"], fmt.format_signed(constants.kz_case_1)),
        (words["param_kz_full_defence"], fmt.format_signed(constants.kz_case_2)),
        (words["param_recovery"], recovery),
    )
    labels = view.sheet("labels")
    reasons = attack["bonus_reasons"]
    bonus_rows = tuple(
        (_measure_label(cfg, row.measure), str(row.min_level), fmt.format_signed(row.points), reasons[row.measure])
        for row in constants.bonus_rows
    )
    return ParameterBlock(
        rows=rows,
        bonus_header=(labels["measure"], labels["from_level"], labels["bonus"], words["bonus_reason_head"]),
        bonus_rows=bonus_rows,
    )


def _check_rows(cfg: Config, constants, view: RevealView, words: dict) -> CheckRows:
    angriff = view.sheet("angriff")
    labels = view.sheet("labels")
    gr = angriff["label_gr"]
    case_word = labels["case"]
    lower, upper = fmt.format_number(constants.lower), fmt.format_number(constants.upper)
    damage_label = angriff["label_damage_before_recovery"] if constants.with_recovery else labels["damage"]
    kz_head = words["check_kz_head"]
    case_rows = (
        (
            f"{case_word} 1: {gr} ≤ {lower}",
            fmt.format_money(constants.case_1_damage_eur),
            fmt.format_signed(constants.kz_case_1),
        ),
        (
            f"{case_word} 2: {gr} ≥ {upper}",
            fmt.format_money(constants.case_2_damage_eur),
            fmt.format_signed(constants.kz_case_2),
        ),
        (
            f"{case_word} 3: {lower} < {gr} < {upper}",
            f"({upper} {MINUS} {gr}) {fmt.TIMES} {fmt.format_money(constants.unit_eur)}",
            f"{fmt.format_number(constants.kz_case_1)} + ({gr} {MINUS} {lower}) {fmt.format_factor(constants.slope)}",
        ),
    )
    table_rows = tuple(
        (
            fmt.format_number(step),
            fmt.format_money((constants.upper - step) * constants.unit_eur),
            approx_signed(rules.attack_kz_delta(constants.kz_case_1, constants.slope, (step - constants.lower) * cfg.ws, cfg.ws)),
        )
        for step in range(constants.lower + 1, constants.upper)
    )
    return CheckRows(
        case_header=(words["check_case_head"], damage_label, kz_head),
        case_rows=case_rows,
        table_header=(gr, damage_label, kz_head),
        table_rows=table_rows,
    )


def _event_schedule(cfg: Config, texts: Texts, wave: Wave, words: dict) -> tuple[EventScheduleRow, ...]:
    rows = []
    for event in cfg.events.get(wave.wave_id, []):
        effect = eventtext.effect_rows(event, cfg, texts)
        rows.append(
            EventScheduleRow(
                name=event.name,
                kind=words[EFFECT_KIND_KEYS[effect.kind]],
                heading=effect.heading or "",
                lines=tuple(row.text for row in effect.rows),
            )
        )
    return tuple(rows)


def _key_values(constants, trace_wave: rules.WaveTrace) -> dict[str, str]:
    """The printed strings of one wave's answer key; every value is a formatted `WaveTrace` field."""
    marks = ", ".join(
        f"{row.measure} {fmt.TIMES if row.measure in trace_wave.bonus_met else DASH}" for row in constants.bonus_rows
    )
    return {
        "selection": selection_text(trace_wave.selection),
        "cia": " / ".join(fmt.format_number(trace_wave.cia[key]) for key in "cia"),
        "e_value": fmt.format_approx(trace_wave.e_value),
        "bonus": f"{fmt.format_number(trace_wave.bonus_reduction)} ({marks})",
        "gr": fmt.format_approx(trace_wave.gesamtreduktion),
        "case": str(trace_wave.case),
        "damage_before": fmt.format_money(trace_wave.damage_before_eur),
        "recovery": fmt.format_percent(trace_wave.recovery_factor) if constants.with_recovery else DASH,
        "damage_after": fmt.format_money(trace_wave.damage_eur),
        "kz_attack": approx_signed(trace_wave.kz_attack),
        "kz_event": fmt.format_signed(trace_wave.kz_event),
        "kz_exact": approx_signed(trace_wave.kz_change_exact),
        "kz_change": fmt.format_signed(trace_wave.kz_change),
        "kz_before": str(trace_wave.kz_before),
        "kz_unclamped": str(trace_wave.kz_unclamped),
        "kz_after": str(trace_wave.kz_after),
        "own_opex": fmt.format_money(trace_wave.own_opex_k * 1000),
        "window_cost": fmt.format_money(trace_wave.window_cost_k * 1000),
        "external_budget": f"{fmt.format_signed(trace_wave.event_budget_k * 1000)} €",
        "external_opex": f"{fmt.format_signed(trace_wave.event_opex_k * 1000)} €",
        "remaining": fmt.format_money(trace_wave.remaining_k * 1000),
    }


def _key_rows(words: dict, columns: list[dict[str, str]]) -> tuple[AnswerKeyRow, ...]:
    return tuple(
        AnswerKeyRow(key, words[f"key_{key}"], tuple(column[key] for column in columns)) for key in KEY_ROW_IDS
    )


def _reference_traces(cfg: Config) -> dict[str, rules.PathTrace]:
    """The trace of every tier's pinned reference path; PrintModelError for a missing, illegal, over-budget or
    swap-only path (the build guard of the answer keys, T-05-44)."""
    traces: dict[str, rules.PathTrace] = {}
    for name in cfg.budget_tiers:
        if name not in cfg.reference_plans:
            raise PrintModelError(f"Spielleitung: Für das Tier '{name}' fehlt ein Referenzpfad in reference_plans.")
        path = refpaths.reference_path(cfg, name)
        try:
            trace = rules.path_trace(cfg, name, path)
        except rules.PathError as error:
            raise PrintModelError(f"Spielleitung: Der Referenzpfad des Tiers '{name}' ist nicht zulässig ({error}).") from error
        if trace.review.over_budget:
            raise PrintModelError(
                f"Spielleitung: Der Referenzpfad des Tiers '{name}' überzieht das Budget "
                f"(Restbudget {trace.review.remaining_k} k€)."
            )
        if not refpaths.voluntary_moves(cfg, path):
            raise PrintModelError(
                f"Spielleitung: Der Referenzpfad des Tiers '{name}' enthält neben dem Pflichttausch keinen freiwilligen Zug."
            )
        traces[name] = trace
    return traces


def _path_lines(cfg: Config, words: dict) -> tuple[PathLine, ...]:
    lines = []
    for name in cfg.budget_tiers:
        path = refpaths.reference_path(cfg, name)
        windows = []
        for index, window in enumerate(path.windows):
            swap = ""
            if window.swap is not None:
                swap = f"{words['path_swap']} {window.swap[0]} {ARROW} {window.swap[1]} · "
            windows.append(f"{words['path_window']} {cfg.waves[index].wave_id}: {swap}{selection_text(window.selection)}")
        lines.append(PathLine(name.capitalize(), selection_text(path.start), tuple(windows)))
    return tuple(lines)


def _review_section(cfg: Config, texts: Texts, view: RevealView, words: dict) -> ReviewSection:
    event = next(event for event in cfg.final_events if event.type == "final_budget_tier")
    effect = eventtext.effect_rows(event, cfg, texts)
    kz_per_step, step_k = rules.penalty_params(cfg.final_events)
    return ReviewSection(
        title=view.sheet("teamheft")["review_title"],
        intro=words["review_intro"],
        tier_heading=effect.heading or "",
        tier_lines=tuple(row.text for row in effect.rows),
        x_label=words["review_x"],
        x_value=str(kz_per_step),
        step_label=words["review_step"],
        step_value=fmt.format_money(step_k * 1000),
    )


def _tier_results(cfg: Config, traces: dict[str, rules.PathTrace], words: dict) -> tuple[TierResult, ...]:
    weights = cfg.final_index
    results = []
    for name, trace in traces.items():
        review = trace.review
        index = rules.final_index(review.kz_final, review.ros, weights.weight_kz, weights.weight_ros)
        results.append(
            TierResult(
                tier=name.capitalize(),
                remaining=fmt.format_money(review.remaining_k * 1000),
                review_delta=fmt.format_signed(review.kz_review_change),
                kz_final=str(review.kz_final),
                own_spend=fmt.format_money(review.own_spend_k * 1000),
                total_damage=fmt.format_money(review.total_damage_eur),
                ros=DASH if review.ros is None else fmt.format_number(rules.ros_two_decimals(review.ros)),
                final_index=fmt.format_number(index),
            )
        )
    return tuple(results)


def _final_rows(words: dict, results: tuple[TierResult, ...]) -> tuple[AnswerKeyRow, ...]:
    labels = {
        "remaining": words["final_remaining"],
        "review_delta": words["final_review_delta"],
        "kz_final": words["final_kz"],
        "own_spend": words["final_own_spend"],
        "total_damage": words["final_total_damage"],
        "ros": words["final_ros"],
        "final_index": words["final_index"],
    }
    return tuple(
        AnswerKeyRow(key, labels[key], tuple(getattr(result, key) for result in results)) for key in FINAL_ROW_IDS
    )


def _welle_zero(cfg: Config, view: RevealView, words: dict) -> Optional[WelleZeroKey]:
    if cfg.practice is None:
        return None
    trace = practice.check_example(cfg)
    wave_view = practice.practice_config(cfg)
    wave = wave_view.waves[0]
    constants = rules.worksheet_constants(wave_view, wave)
    column = _key_values(constants, trace.waves[0])
    tracking_wave = view.sheet("tracking")["wave"]
    return WelleZeroKey(
        title=words["welle0_title"],
        intro=words["welle0_intro"],
        header=(words["key_head"], f"{tracking_wave} {wave.wave_id}"),
        rows=_key_rows(words, [column]),
    )


def _clue_groups(cfg: Config, texts: Texts, clues: tuple[Clue, ...]) -> tuple[ClueGroup, ...]:
    groups: dict[str, list[ClueEntry]] = {}
    for row in FacilitatorView(cfg, texts, clues).clue_matrix():
        groups.setdefault(row.title, []).append(
            ClueEntry(str(row.number), row.document, row.section, row.quote, row.why, row.measures)
        )
    return tuple(ClueGroup(title, tuple(entries)) for title, entries in groups.items())


def build_master_sheet(cfg: Config, texts: Texts, clues: tuple[Clue, ...]) -> Optional[MasterSheet]:
    """The facilitator booklet model; None when the config pins no reference plans (e.g. the mini test config).

    Raises PrintModelError (the build stops) when a tier lacks a legal, in-budget reference path with a voluntary
    move, when a wave has no hand-calculable worksheet shape, or when the Welle 0 example no longer teaches the mechanics.
    """
    if not cfg.reference_plans:
        return None
    traces = _reference_traces(cfg)
    view = RevealView(cfg, texts)
    words = view.sheet("spielleitung")
    tier_names = tuple(name.capitalize() for name in cfg.budget_tiers)

    sections = []
    for index, wave in enumerate(cfg.waves):
        try:
            constants = rules.worksheet_constants(cfg, wave)
        except rules.WorksheetInvariantError as error:
            raise PrintModelError(f"Welle {wave.wave_id}: {error}") from error
        columns = [_key_values(constants, trace.waves[index]) for trace in traces.values()]
        events = _event_schedule(cfg, texts, wave, words)
        sections.append(
            WaveSection(
                wave_id=wave.wave_id,
                title=view.attack_title(wave),
                parameters=_parameters(cfg, wave, constants, view, words, view.attack(wave.attack_id)),
                checks=_check_rows(cfg, constants, view, words),
                events=events,
                no_events="" if events else words["events_none"],
                key_header=(words["key_head"], *tier_names),
                key_rows=_key_rows(words, columns),
            )
        )
    results = _tier_results(cfg, traces, words)
    return MasterSheet(
        job=MASTER_JOB,
        title=words["title"],
        notice=words["notice"],
        intro=words["intro"],
        gr_legend=words["gr_legend"],
        contents_title=words["contents_title"],
        how_to_title=words["how_to_title"],
        how_to=tuple(words["how_to"]),
        approx_hint=words["approx_hint"],
        paths_title=words["paths_title"],
        paths_intro=words["paths_intro"],
        path_start=words["path_start"],
        paths=_path_lines(cfg, words),
        params_title=words["params_title"],
        check_title=words["check_title"],
        check_table_intro=words["check_table_intro"],
        events_title=words["events_title"],
        event_header=(words["event_head_name"], words["event_head_kind"], words["event_head_effect"]),
        keys_title=words["keys_title"],
        keys_intro=words["keys_intro"],
        waves=tuple(sections),
        review=_review_section(cfg, texts, view, words),
        tiers=results,
        final_title=words["final_title"],
        final_intro=words["final_intro"],
        final_note=words["final_index_note"],
        final_header=(words["final_head"], *tier_names),
        final_rows=_final_rows(words, results),
        final_weight_label=words["final_index_weight"],
        final_weight_value=fmt.format_number(cfg.final_index.weight_ros),
        welle0=_welle_zero(cfg, view, words),
        bonus_title=words["bonus_title"],
        clues_title=words["clues_title"],
        clues_intro=words["clues_intro"],
        clue_header=(
            words["clue_head_nr"], words["clue_head_document"], words["clue_head_section"],
            words["clue_head_quote"], words["clue_head_why"], words["clue_head_measures"],
        ),
        clue_groups=_clue_groups(cfg, texts, clues),
    )
