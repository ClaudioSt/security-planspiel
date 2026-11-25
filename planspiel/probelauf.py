"""FLOW-05 dry-run protocol: a one-page sheet the observer fills in while the facilitator runs the whole session (D-07, D-25).

Facilitator-side only. The rows are the `schedule_rows` of the booklet (same blocks, planned minutes and spans, D-07);
the pass rule is digit-free prose from `sheets.probelauf`; the practice sheet is a handout and has no row. The protocol and the dry-run verdict judge the same blocks.
"""
from dataclasses import dataclass, fields
from typing import Optional

from planspiel import fmt
from planspiel.cards import printed_strings
from planspiel.config import Config
from planspiel.schedule import schedule_rows
from planspiel.texts import RevealView, Texts

PROBELAUF_JOB = "spielleitung-probelauf"
SHEET = "probelauf"
EN_DASH = "–"


@dataclass(frozen=True)
class ProtocolRow:
    label: str
    planned: str
    span: str


@dataclass(frozen=True)
class ProtocolSheet:
    job: str
    title: str
    notice: str
    intro: str
    header: tuple[str, ...]
    rows: tuple[ProtocolRow, ...]
    total_label: str
    total_value: str
    pass_title: str
    pass_rules: tuple[str, ...]
    help_title: str
    observer_label: str
    date_label: str

    def printed_fragments(self) -> tuple[str, ...]:
        """Every string of the sheet that ends up on the paper, without duplicates and without empty strings."""
        found = [
            text for field in fields(self) if field.name not in ("job", "rows") for text in printed_strings(getattr(self, field.name))
        ]
        for row in self.rows:
            found += [row.label, row.planned, row.span]
        return tuple(dict.fromkeys(text for text in found if text))


def build_probelauf_sheet(cfg: Config, texts: Texts) -> Optional[ProtocolSheet]:
    """The protocol; None when the config has no `session_schedule` (e.g. the mini test config)."""
    schedule = cfg.session_schedule
    if schedule is None:
        return None
    words = RevealView(cfg, texts).sheet(SHEET)
    source = schedule_rows(cfg, texts)
    wave_rule = f"{words['pass_wave_lead']} {words['pass_wave_tail']}"
    return ProtocolSheet(
        job=PROBELAUF_JOB,
        title=words["title"],
        notice=words["notice"],
        intro=words["intro"],
        header=(
            words["head_block"], words["head_planned"], words["head_span"], words["head_start"], words["head_actual"],
            words["head_questions"], words["head_errors"],
        ),
        rows=tuple(ProtocolRow(label=row.label, planned=row.minutes, span=f"{row.start} {EN_DASH} {row.end}") for row in source),
        total_label=words["total_label"],
        total_value=fmt.format_number(schedule.total_minutes),
        pass_title=words["pass_title"],
        pass_rules=(wave_rule, *words["pass_rules"]),
        help_title=words["help_title"],
        observer_label=words["observer_label"],
        date_label=words["date_label"],
    )
