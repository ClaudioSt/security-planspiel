"""The Welle 0 practice view: a throw-away Config in which the practice attack is the only wave (FLOW-01, D-12).

Nothing outside this module reads the content of `cfg.practice` (the text coverage only asks whether the block
exists). The view reuses `rules` unchanged, so every printed practice number comes from the same primitives as the
real waves; the real `cfg.waves`, `cfg.attacks` and `cfg.events` never see the block, which keeps the enumeration, the
gate and the digests of waves 1-3 identical.

`check_example` proves that the fixed example selection teaches what Welle 0 is for (D-13, D-15): Fall 3, one bonus met
and one missed, recovery, a wave KZ change that is an exact half before rounding, and a clamp that acts.

`build_practice_document` turns the trace of that example into the printed document: the worksheet of the practice
wave with every box filled, the example selection, the practice event and a filled tracking excerpt (D-14).
"""
import copy
import dataclasses
from fractions import Fraction
from typing import Optional

from planspiel import eventtext, fmt, rules
from planspiel.booklet import TRACKING_ROW_ORDER, build_tracking_page
from planspiel.cards import printed_strings
from planspiel.config import BudgetTier, Config, Wave
from planspiel.printmodel import (
    MIN_HALF_DISTANCE,
    AttackSheet,
    PrintModelError,
    build_attack_sheet,
    fill_line,
    min_half_distance,
)
from planspiel.rules import (
    KZ_MAX,
    KZ_MIN,
    Path,
    PathError,
    PathTrace,
    WorksheetInvariantError,
    path_trace,
    worksheet_constants,
)
from planspiel.texts import CASE_KEYS, Texts

PRACTICE_JOB = "uebung-welle-0"
PRACTICE_TIER = "practice"
PRACTICE_ATTACK = "practice"
PREFIX = "Übung"


def practice_config(cfg: Config) -> Config:
    """The config in which the practice wave (id 0) is the only wave and `practice` the only budget tier."""
    block = cfg.practice
    if block is None:
        raise PrintModelError(f"{PREFIX}: Die Konfiguration enthält keinen Block 'practice'.")
    tier = BudgetTier(PRACTICE_TIER, block.budget, block.kz_start, Fraction(1))
    return dataclasses.replace(
        cfg,
        default_budget_tier=PRACTICE_TIER,
        attacks={**cfg.attacks, PRACTICE_ATTACK: block.attack},
        waves=[block.wave],
        events={block.wave.wave_id: [block.event]},
        final_events=[],
        budget_tiers={PRACTICE_TIER: tier},
        practice=None,
        # Welle 0 is a worked example without the team's register (RISK-04, A8): no reality-check line.
        risk_matrix=None,
    )


def check_example(cfg: Config) -> PathTrace:
    """Trace of the example selection on the practice view; PrintModelError unless it teaches the Welle 0 mechanics."""
    view = practice_config(cfg)
    wave_config = view.waves[0]
    try:
        constants = worksheet_constants(view, wave_config)
    except WorksheetInvariantError as error:
        raise PrintModelError(f"{PREFIX}: {error}") from error
    distance = min_half_distance(view, constants)
    if distance is not None and distance < MIN_HALF_DISTANCE:
        raise PrintModelError(
            f"{PREFIX}: Zwei Nachkommastellen genügen für die KZ-Berechnung nicht, ein Wert liegt nur {distance} "
            f"neben einem halben Punkt (Grenze {MIN_HALF_DISTANCE}); die Rundung könnte kippen (D-09)."
        )

    try:
        trace = path_trace(view, PRACTICE_TIER, Path(start=dict(cfg.practice.selection)))
    except PathError as error:
        raise PrintModelError(f"{PREFIX}: Die Beispielauswahl ist nicht zulässig ({error}).") from error

    wave = trace.waves[0]
    if trace.review.own_spend_k > cfg.practice.budget:
        raise PrintModelError(
            f"{PREFIX}: Init und OPEX der Beispielauswahl ({trace.review.own_spend_k}) übersteigen das Budget "
            f"({cfg.practice.budget})."
        )
    if wave.case != 3:
        raise PrintModelError(f"{PREFIX}: Die Beispielauswahl muss in Fall 3 landen, sie landet in Fall {wave.case}.")
    if len(wave.bonus_met) != 1 or not wave.bonus_missed:
        raise PrintModelError(
            f"{PREFIX}: Es muss genau eine Bonus-Maßnahme erfüllt und mindestens eine verfehlt sein "
            f"(erfüllt: {len(wave.bonus_met)}, verfehlt: {len(wave.bonus_missed)})."
        )
    if wave.recovery_factor <= 0:
        raise PrintModelError(f"{PREFIX}: Die Beispielauswahl muss Recovery auslösen (Faktor größer als 0).")
    if wave.kz_change_exact.denominator == 1:
        raise PrintModelError(
            f"{PREFIX}: Die KZ-Änderung vor dem Runden ({wave.kz_change_exact}) ist ganzzahlig, es gäbe nichts zu runden."
        )
    if wave.kz_change_exact.denominator != 2:
        raise PrintModelError(
            f"{PREFIX}: Die KZ-Änderung vor dem Runden ({wave.kz_change_exact}) muss genau auf einem halben Punkt liegen, "
            "damit das Runden ab ,5 sichtbar wird."
        )
    if KZ_MIN <= wave.kz_unclamped <= KZ_MAX:
        raise PrintModelError(
            f"{PREFIX}: Die Begrenzung auf {KZ_MIN} bis {KZ_MAX} muss wirken, die KZ landet bei {wave.kz_unclamped}."
        )
    return trace


# ---- the printed document --------------------------------------------------------------------------------------

DASH = "–"
ARROW = "→"
BONUS_MET = fmt.TIMES
BONUS_MISSED = DASH
# The tracking rows a Welle 0 excerpt fills: the ones that apply to a first wave without a change window or event
# budget effect, in the order of the tracking sheet.
EXCERPT_KEYS = ("kz_before", "kz_change", "kz_after", "damage", "own_init", "own_opex", "remaining")


class PracticeView:
    """Text source of the practice worksheet: the methods `build_attack_sheet` reads from the revealed view.

    The practice story lives under `practice.*` in content/texte.toml; the vocabulary of the sheet (step headings,
    labels, recovery levels) is the one of the real worksheets, so players meet the same words twice.
    """

    def __init__(self, cfg: Config, texts: Texts) -> None:
        self._cfg = cfg
        self._texts = texts

    def attack_title(self, wave: Wave) -> str:
        """`Welle 0 – Übung`: the word from the tracking sheet, the number from the wave id, the name from the story."""
        return f"{self._texts.get('sheets.tracking.wave')} {wave.wave_id} {DASH} {self._texts.get('practice.title')}"

    def attack(self, attack_id: str) -> dict:
        if attack_id != PRACTICE_ATTACK:
            raise KeyError(f"Angriff '{attack_id}' ist nicht der Übungsangriff")
        get = self._texts.get
        return {
            "name": get("practice.title"),
            "narrative": get("practice.narrative"),
            "cia_rationale": get("practice.cia_rationale"),
            "cases": [get(f"practice.{case}") for case in CASE_KEYS],
            "bonus_reasons": dict(self._texts.subtree("practice.bonus_reasons")),
        }

    def sheet(self, name: str) -> dict:
        words = copy.deepcopy(self._texts.subtree(f"sheets.{name}"))
        if name == "angriff":
            # The practice has no event card: its hint says where the event of the example is printed.
            words["events_hint"] = self._texts.get("practice.events_hint")
        return words


@dataclasses.dataclass(frozen=True)
class SelectionRow:
    measure: str
    level: str
    c: str
    i: str
    a: str
    init: str
    opex: str


@dataclasses.dataclass(frozen=True)
class SelectionTotal:
    label: str
    init: str
    opex: str


@dataclasses.dataclass(frozen=True)
class EventBlock:
    title: str
    narrative: str
    heading: str
    rows: tuple[str, ...]
    selected: int
    result: str


@dataclasses.dataclass(frozen=True)
class TrackingExcerpt:
    title: str
    start_line: str
    columns: tuple[str, str]
    rows: tuple[tuple[str, str, str], ...]
    clamp_hint: str
    rounding_hint: str


@dataclasses.dataclass(frozen=True)
class PracticeDocument:
    job: str
    title: str
    sheet: AttackSheet
    selection_title: str
    selection_header: tuple[str, ...]
    selection_rows: tuple[SelectionRow, ...]
    selection_total: SelectionTotal
    event: EventBlock
    tracking: TrackingExcerpt

    def printed_fragments(self) -> tuple[str, ...]:
        """Every string of the document that ends up on the paper, without duplicates and without empty strings."""
        own = [
            text
            for field in dataclasses.fields(self)
            if field.name not in ("job", "sheet")
            for text in printed_strings(getattr(self, field.name))
        ]
        return tuple(dict.fromkeys([*self.sheet.printed_fragments(), *(text for text in own if text)]))


def _measure_label(cfg: Config, measure_id: str) -> str:
    return f"{measure_id} {DASH} {cfg.measures[measure_id].name}"


def _selected(cfg: Config) -> list[tuple[str, int]]:
    return [(measure_id, level) for measure_id, level in cfg.practice.selection.items() if level > 0]


def _fill_sheet(cfg: Config, sheet: AttackSheet, trace: PathTrace) -> AttackSheet:
    """The worksheet with every box and table filled from the trace (exact values only, formatted with `fmt`)."""
    wave = trace.waves[0]
    number, signed = fmt.format_number, fmt.format_signed
    if sheet.recovery_line is None:
        raise PrintModelError(f"{PREFIX}: Das Übungsblatt braucht den Recovery-Schritt, der Angriff lässt keine Recovery zu.")
    damage_line, kz_line = sheet.cases[2].lines
    gr = number(wave.gesamtreduktion)
    case_three = dataclasses.replace(
        sheet.cases[2],
        lines=(
            fill_line(damage_line, (gr, fmt.format_money(wave.damage_before_eur))),
            fill_line(kz_line, (gr, signed(wave.kz_attack))),
        ),
    )
    rows = []
    for measure_id, level in _selected(cfg):
        facts = rules.card_facts(cfg.measures, measure_id, level)
        rows.append((_measure_label(cfg, measure_id), str(level), *(number(facts.cia[key]) for key in "cia")))
    return dataclasses.replace(
        sheet,
        e_value_line=fill_line(sheet.e_value_line, (*(number(wave.cia[key]) for key in "cia"), number(wave.e_value))),
        total_bonus_line=fill_line(sheet.total_bonus_line, (number(wave.bonus_reduction),)),
        reduction_line=fill_line(sheet.reduction_line, (number(wave.e_value), number(wave.bonus_reduction), gr)),
        cases=(sheet.cases[0], sheet.cases[1], case_three),
        recovery_line=fill_line(
            sheet.recovery_line,
            (
                fmt.format_number(wave.damage_before_eur),  # the euro sign follows the short box in the line text
                fmt.format_percent(wave.recovery_factor),
                fmt.format_money(wave.damage_eur),
            ),
        ),
        wave_kz_line=fill_line(
            sheet.wave_kz_line,
            (signed(wave.kz_attack), signed(wave.kz_event), signed(wave.kz_change_exact), signed(wave.kz_change)),
        ),
        result_line=fill_line(sheet.result_line, (fmt.format_money(wave.damage_eur), signed(wave.kz_change))),
        cia_filled=tuple(rows),
        cia_sum=tuple(number(wave.cia[key]) for key in "cia"),
        bonus_fulfilled=tuple(BONUS_MET if row.measure in wave.bonus_met else BONUS_MISSED for row in sheet.bonus_rows),
    )


def _selection(
    cfg: Config, texts: Texts, trace: PathTrace
) -> tuple[tuple[str, ...], tuple[SelectionRow, ...], SelectionTotal]:
    labels = texts.subtree("sheets.labels")
    header = (
        labels["measure"], labels["level"], "C", "I", "A", labels["init_costs"],
        f"{labels['opex']} {texts.get('sheets.karten.per_wave')}",
    )
    rows = []
    init_sum = opex_sum = 0
    for measure_id, level in _selected(cfg):
        facts = rules.card_facts(cfg.measures, measure_id, level)
        init_sum += facts.init_k
        opex_sum += facts.opex_k
        rows.append(
            SelectionRow(
                measure=_measure_label(cfg, measure_id),
                level=str(level),
                c=fmt.format_number(facts.cia["c"]),
                i=fmt.format_number(facts.cia["i"]),
                a=fmt.format_number(facts.cia["a"]),
                init=fmt.format_money(facts.init_k * 1000),
                opex=fmt.format_money(facts.opex_k * 1000),
            )
        )
    if init_sum != trace.init_k or opex_sum != trace.waves[0].own_opex_k:
        raise PrintModelError(f"{PREFIX}: Init und OPEX der Auswahlzeilen weichen von der Berechnung der Regeln ab.")
    total = SelectionTotal(labels["sum"], fmt.format_money(init_sum * 1000), fmt.format_money(opex_sum * 1000))
    return header, tuple(rows), total


def _event_block(cfg: Config, texts: Texts, trace: PathTrace) -> EventBlock:
    block = cfg.practice
    event_texts = texts.subtree("practice.event")
    effect = eventtext.effect_rows(block.event, practice_config(cfg), texts, event_texts=event_texts)
    measure_id = block.event.params["measure"]
    level = block.selection.get(measure_id, 0)
    index = next((position for position, row in enumerate(effect.rows) if level in row.covers), None)
    if index is None or effect.heading is None:
        raise PrintModelError(f"{PREFIX}: Das Übungsereignis hat keine Zeile für Level {level} von {measure_id}.")
    chosen = effect.rows[index]
    if chosen.value != trace.waves[0].kz_event:
        raise PrintModelError(f"{PREFIX}: Die gedruckte Eventzeile ({chosen.value}) weicht von der Berechnung der Regeln ab.")
    return EventBlock(
        title=texts.get("sheets.labels.events"),
        narrative=event_texts["narrative"],
        heading=effect.heading,
        rows=tuple(row.text for row in effect.rows),
        selected=index,
        result=f"{texts.get('practice.event_result')}: {chosen.text}",
    )


def _tracking_excerpt(cfg: Config, texts: Texts, trace: PathTrace) -> TrackingExcerpt:
    page = build_tracking_page(cfg, texts)
    wave = trace.waves[0]
    cells = {
        "kz_before": (str(wave.kz_before), str(wave.kz_before)),
        "kz_change": ("", fmt.format_signed(wave.kz_change)),
        "kz_after": ("", str(wave.kz_after)),
        "damage": ("", fmt.format_money(wave.damage_eur)),
        "own_init": (fmt.format_money(trace.init_k * 1000), ""),
        "own_opex": ("", fmt.format_money(wave.own_opex_k * 1000)),
        "remaining": (fmt.format_money(trace.start_remaining_k * 1000), fmt.format_money(wave.remaining_k * 1000)),
    }
    if tuple(cells) != tuple(key for key in TRACKING_ROW_ORDER if key in EXCERPT_KEYS):
        raise PrintModelError(f"{PREFIX}: Die Zeilen des Tracking-Auszugs folgen nicht der Reihenfolge des Tracking-Bogens.")
    labels = {row.key: row.label for row in page.rows}
    return TrackingExcerpt(
        title=texts.get("practice.tracking_title"),
        start_line=(
            f"{texts.get('practice.start_budget')} {fmt.format_money(cfg.practice.budget * 1000)} "
            f"{texts.get('practice.start_kz')} {cfg.practice.kz_start}. {texts.get('practice.start_remaining')}"
        ),
        columns=(page.columns[0], f"{texts.get('sheets.tracking.wave')} {wave.wave_id}"),
        rows=tuple((labels[key], *pair) for key, pair in cells.items()),
        clamp_hint=f"{page.clamp_text}: {wave.kz_unclamped} {ARROW} {wave.kz_after}",
        rounding_hint=page.hints[0],
    )


def build_practice_document(cfg: Config, texts: Texts) -> Optional[PracticeDocument]:
    """The Welle 0 document; None when the config has no practice block.

    Raises PrintModelError (the build stops) when the example no longer teaches the mechanics (`check_example`) or
    a printed value leaves the trace.
    """
    if cfg.practice is None:
        return None
    trace = check_example(cfg)
    view = practice_config(cfg)
    sheet = build_attack_sheet(view, texts, view.waves[0], view=PracticeView(cfg, texts), job=PRACTICE_JOB)
    sheet = _fill_sheet(cfg, sheet, trace)
    header, rows, total = _selection(cfg, texts, trace)
    return PracticeDocument(
        job=PRACTICE_JOB,
        title=sheet.title,
        sheet=sheet,
        selection_title=texts.get("practice.selection_title"),
        selection_header=header,
        selection_rows=rows,
        selection_total=total,
        event=_event_block(cfg, texts, trace),
        tracking=_tracking_excerpt(cfg, texts, trace),
    )
