"""Print model of the attack worksheets: exact values next to the strings the template prints (PRINT-03).

An AttackSheet holds, per wave, the exact numbers a facilitator calculates with (taken from
rules.worksheet_constants) and the German display strings built from them with planspiel.fmt and the wording in
content/texte.toml. The Jinja template only inserts these strings; the equivalence replay reads only the exact
fields, so sheet and proof share one source (D-11). No formula is derived here: every number comes from
rules.worksheet_constants, and the two build guards (D-06, D-09) turn a broken hand-calculation shape into a
build failure instead of a wrong printed formula.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional

from planspiel import fmt
from planspiel.config import Config, Wave
from planspiel.rules import (
    BonusRow,
    RecoveryRow,
    WorksheetConstants,
    WorksheetInvariantError,
    attack_kz_delta,
    worksheet_constants,
)
from planspiel.texts import RevealView, Texts

MIN_HALF_DISTANCE = Fraction(1, 100)
INTRO_KEYS = (
    "start_values_intro", "cia_table_instruction", "e_value_intro", "bonus_intro", "case_3_hint",
    "cap_intro", "recovery_intro", "events_hint",
)
LABEL_PREFIX = "label_"
DASH = "–"
MINUS = fmt.MINUS


class PrintModelError(ValueError):
    """The config cannot be printed as a hand-calculable worksheet; the build stops (D-06, D-09)."""


@dataclass(frozen=True)
class Box:
    """A fill-in box; size is 'short' (an entry) or 'long' (a result). The template maps it to a width."""

    size: str


Line = tuple[str | Box, ...]


@dataclass(frozen=True)
class CaseBlock:
    """Fall 1 and 2 carry an outcome string; Fall 3 carries the damage and KZ formula lines."""

    heading: str
    text: str
    outcome: str
    lines: tuple[Line, ...]


@dataclass(frozen=True)
class AttackSheet:
    wave_id: int
    attack_id: str
    job: str
    title: str
    narrative: str
    cia_rationale: str
    intro: dict[str, str]
    labels: dict[str, str]
    # Exact values (names equal the WorksheetConstants fields).
    w_c: Fraction
    w_i: Fraction
    w_a: Fraction
    lower: int
    reduction_cap: int
    upper: int
    unit_eur: int
    case_1_damage_eur: int
    case_2_damage_eur: int
    kz_case_1: Fraction
    kz_case_2: Fraction
    slope: Fraction
    bonus_rows: tuple[BonusRow, ...]
    with_recovery: bool
    recovery_measure: Optional[str]
    recovery_rows: tuple[RecoveryRow, ...]
    base_cia: tuple[int, int, int]
    cia_rows: int
    # Display strings.
    step_headings: dict[str, str]
    cia_header: tuple[str, ...]
    cia_base_row: tuple[str, ...]
    level_hint: str
    e_value_line: Line
    bonus_header: tuple[str, ...]
    bonus_table: tuple[tuple[str, str, str, str], ...]
    total_bonus_line: Line
    reduction_line: Line
    cap_line: Line
    cases: tuple[CaseBlock, CaseBlock, CaseBlock]
    kz_hint: str
    result_line: Line
    recovery_header: tuple[str, ...]
    recovery_table: tuple[tuple[str, str, str], ...]
    recovery_line: Optional[Line]
    wave_kz_line: Line

    def printed_fragments(self) -> tuple[str, ...]:
        """Title, step headings and every number-bearing display string, without duplicates (D-11).

        Strings are the parts of a line between fill-in boxes, or one table cell; a line without a box (the cap
        line) is one fragment. The PDF check matches these, whitespace-insensitively, against the extracted text.
        """
        found: list[str] = [self.title, *self.step_headings.values()]

        def take(text: str) -> None:
            if any(char.isdigit() for char in text):
                found.append(text)

        def take_line(line: Optional[Line]) -> None:
            for part in line or ():
                if isinstance(part, str):
                    take(part)

        for cell in self.cia_base_row:
            take(cell)
        take(self.level_hint)
        for line in (self.e_value_line, self.total_bonus_line, self.reduction_line, self.cap_line):
            take_line(line)
        for row in self.bonus_table:
            for cell in row:
                take(cell)
        for block in self.cases:
            take(block.heading)
            take(block.outcome)
            for line in block.lines:
                take_line(line)
        take_line(self.result_line)
        for row in self.recovery_table:
            for cell in row:
                take(cell)
        take_line(self.recovery_line)
        take_line(self.wave_kz_line)
        return tuple(dict.fromkeys(found))


def min_half_distance(cfg: Config, constants: WorksheetConstants) -> Optional[Fraction]:
    """Smallest nonzero distance of a Fall-3 attack KZ to a half-integer, on the whole 1/ws reduction lattice.

    None when every lattice value is exactly a half-integer or an integer distance never occurs.
    """
    half = Fraction(1, 2)
    smallest: Optional[Fraction] = None
    for step in range(1, (constants.upper - constants.lower) * cfg.ws):
        value = attack_kz_delta(constants.kz_case_1, constants.slope, step, cfg.ws)
        fraction_part = value - (value.numerator // value.denominator)
        distance = abs(fraction_part - half)
        if distance == 0:
            continue
        smallest = distance if smallest is None else min(smallest, distance)
    return smallest


def _short() -> Box:
    return Box("short")


def _long() -> Box:
    return Box("long")


def _measure_name(cfg: Config, measure_id: str) -> str:
    return f"{measure_id} {DASH} {cfg.measures[measure_id].name}"


def _level_hint(cfg: Config) -> str:
    levels = sorted({level for measure in cfg.measures.values() for level in measure.levels if level > 0})
    return "(" + " / ".join(str(level) for level in levels) + ")"


def build_attack_sheet(cfg: Config, texts: Texts, wave: Wave) -> AttackSheet:
    view = RevealView(cfg, texts)
    try:
        constants = worksheet_constants(cfg, wave)
    except WorksheetInvariantError as error:
        raise PrintModelError(f"Welle {wave.wave_id}: {error}") from error

    distance = min_half_distance(cfg, constants)
    if distance is not None and distance < MIN_HALF_DISTANCE:
        raise PrintModelError(
            f"Welle {wave.wave_id}: Zwei Nachkommastellen genügen für die KZ-Berechnung nicht, ein Wert liegt nur "
            f"{distance} neben einem halben Punkt (Grenze {MIN_HALF_DISTANCE}); "
            "die Rundung der Welle könnte kippen (D-09)."
        )

    attack = view.attack(wave.attack_id)
    angriff = view.sheet("angriff")
    labels = view.sheet("labels")
    level_labels = view.sheet("backup_recovery")["level_labels"]
    for key, text in angriff.items():
        if key.startswith(LABEL_PREFIX):
            labels[key[len(LABEL_PREFIX):]] = text
    intro = {key: angriff[key] for key in INTRO_KEYS}

    number = fmt.format_number
    with_recovery = constants.with_recovery
    damage_label = labels["damage_before_recovery"] if with_recovery else labels["damage"]

    keys = ["cia", "e_value", "bonus", "reduction", "cases"]
    if with_recovery:
        keys.append("recovery")
    keys.append("wave_kz")
    step_headings = {
        key: f"{labels['step']} {position}: {angriff[f'step_{key}']}" for position, key in enumerate(keys, start=1)
    }

    e_value_line: Line = (
        f"{labels['e_value']} = C ", _short(),
        f" {fmt.TIMES} {number(constants.w_c)} + I ", _short(),
        f" {fmt.TIMES} {number(constants.w_i)} + A ", _short(),
        f" {fmt.TIMES} {number(constants.w_a)} = ", _long(),
    )
    reasons = attack["bonus_reasons"]
    bonus_table = tuple(
        (
            _measure_name(cfg, row.measure),
            str(row.min_level),
            fmt.format_signed(row.points),
            reasons[row.measure],
        )
        for row in constants.bonus_rows
    )
    total_bonus_line: Line = (f"{labels['total_bonus']} = ", _long())
    reduction_line: Line = (
        f"{labels['total_reduction']} = {labels['e_value']} ", _short(),
        f" + {labels['total_bonus']} ", _short(), " = ", _long(),
    )
    cap_line: Line = (
        f"{labels['threshold']}: {number(constants.lower)} · {labels['cap']}: {number(constants.reduction_cap)}"
        f" · {labels['upper']}: {number(constants.lower)} + {number(constants.reduction_cap)}"
        f" = {number(constants.upper)}",
    )

    case_word, reduction_word, gr = labels["case"], labels["total_reduction"], labels["gr"]
    case_texts = attack["cases"]
    outcome_1 = (
        f"{damage_label}: {fmt.format_money(constants.case_1_damage_eur)}"
        f" · {labels['kz']}: {fmt.format_signed(constants.kz_case_1)}"
    )
    outcome_2 = (
        f"{damage_label}: {fmt.format_money(constants.case_2_damage_eur)}"
        f" · {labels['kz']}: {fmt.format_signed(constants.kz_case_2)}"
    )
    damage_line: Line = (
        f"{damage_label} = ({number(constants.upper)} {MINUS} {gr} ", _short(),
        f") {fmt.TIMES} {fmt.format_money(constants.unit_eur)} = ", _long(),
    )
    kz_line: Line = (
        f"{labels['kz']} = {number(constants.kz_case_1)} + ({gr} ", _short(),
        f" {MINUS} {number(constants.lower)}) {fmt.format_factor(constants.slope)} = ", _long(),
    )
    cases = (
        CaseBlock(f"{case_word} 1: {reduction_word} ≤ {number(constants.lower)}", case_texts[0], outcome_1, ()),
        CaseBlock(f"{case_word} 2: {reduction_word} ≥ {number(constants.upper)}", case_texts[1], outcome_2, ()),
        CaseBlock(
            f"{case_word} 3: {number(constants.lower)} < {reduction_word} < {number(constants.upper)}",
            case_texts[2], "", (damage_line, kz_line),
        ),
    )

    recovery_header: tuple[str, ...] = ()
    recovery_table: tuple[tuple[str, str, str], ...] = ()
    recovery_line: Optional[Line] = None
    if with_recovery:
        recovery_header = (labels["level"], "", labels["recovery_factor"])
        recovery_table = tuple(
            (str(row.level), level_labels[str(row.level)], fmt.format_percent(row.factor))
            for row in constants.recovery_rows
        )
        recovery_line = (
            f"{labels['damage_after_recovery']} = {damage_label} ", _short(),
            f" {fmt.TIMES} (1 {MINUS} r ", _short(), ") = ", _long(),
        )

    wave_kz_line: Line = (
        f"{angriff['step_wave_kz']} = {labels['kz_attack']} ", _short(),
        f" + {labels['kz_events']} ", _short(), " = ", _long(),
        f", {angriff['wave_kz_rounding']}: ", _long(),
    )
    final_damage_label = labels["damage_after_recovery"] if with_recovery else labels["damage"]
    result_line: Line = (
        f"{labels['result']}: {final_damage_label} ", _long(), f" · {angriff['step_wave_kz']} ", _short(),
    )

    hint_key = "kz_decimals_hint" if fmt.terminates(constants.slope) else "kz_fraction_hint"
    base_cia = (cfg.base_cia["c"], cfg.base_cia["i"], cfg.base_cia["a"])
    return AttackSheet(
        wave_id=wave.wave_id,
        attack_id=wave.attack_id,
        job=f"angriff-{wave.wave_id}_{wave.attack_id}",
        title=view.attack_title(wave),
        narrative=attack["narrative"],
        cia_rationale=attack["cia_rationale"],
        intro=intro,
        labels=labels,
        w_c=constants.w_c,
        w_i=constants.w_i,
        w_a=constants.w_a,
        lower=constants.lower,
        reduction_cap=constants.reduction_cap,
        upper=constants.upper,
        unit_eur=constants.unit_eur,
        case_1_damage_eur=constants.case_1_damage_eur,
        case_2_damage_eur=constants.case_2_damage_eur,
        kz_case_1=constants.kz_case_1,
        kz_case_2=constants.kz_case_2,
        slope=constants.slope,
        bonus_rows=constants.bonus_rows,
        with_recovery=with_recovery,
        recovery_measure=constants.recovery_measure,
        recovery_rows=constants.recovery_rows,
        base_cia=base_cia,
        cia_rows=len(cfg.measures),
        step_headings=step_headings,
        cia_header=(labels["measure"], labels["level"], "C", "I", "A"),
        cia_base_row=(labels["base_protection"], "", *(str(value) for value in base_cia)),
        level_hint=_level_hint(cfg),
        e_value_line=e_value_line,
        bonus_header=(labels["measure"], labels["from_level"], labels["bonus"]),
        bonus_table=bonus_table,
        total_bonus_line=total_bonus_line,
        reduction_line=reduction_line,
        cap_line=cap_line,
        cases=cases,
        kz_hint=angriff[hint_key],
        result_line=result_line,
        recovery_header=recovery_header,
        recovery_table=recovery_table,
        recovery_line=recovery_line,
        wave_kz_line=wave_kz_line,
    )


def build_attack_sheets(cfg: Config, texts: Texts) -> tuple[AttackSheet, ...]:
    return tuple(build_attack_sheet(cfg, texts, wave) for wave in cfg.waves)
