"""Facilitator-only schedule model: block durations, minutes from the start and the print list (D-01, D-04, D-23).

Numbers come from the `session_schedule` config block, prose from `sheets.ablauf`; no start time exists anywhere, the
clock column stays empty on paper. The model is shared by the facilitator booklet and the dry-run protocol (D-07).
It names no attack: wave labels are composed from the texte word and the wave number of the config.
"""
from dataclasses import dataclass, fields
from typing import Optional

from planspiel import fmt
from planspiel.cards import printed_strings
from planspiel.config import Config
from planspiel.printmodel import PrintModelError, worksheet_job
from planspiel.texts import RevealView, Texts

SHEET = "ablauf"


@dataclass(frozen=True)
class ScheduleRow:
    block_id: str
    label: str
    minutes: str
    start: str
    end: str
    direction: str


@dataclass(frozen=True)
class PrintListRow:
    label: str
    file: str
    per_team: str
    facilitator: str
    total: str


@dataclass(frozen=True)
class SchedulePage:
    title: str
    intro: str
    header: tuple[str, ...]
    rows: tuple[ScheduleRow, ...]
    total_label: str
    total_value: str
    print_title: str
    print_intro: str
    print_header: tuple[str, ...]
    print_rows: tuple[PrintListRow, ...]
    teams_label: str
    teams_value: str

    def printed_fragments(self) -> tuple[str, ...]:
        """Every string of the page that ends up on the paper, without duplicates and without empty strings."""
        found = [text for field in fields(self) if field.name != "rows" for text in printed_strings(getattr(self, field.name))]
        for row in self.rows:  # the block id is a key, not printed text
            found += [row.label, row.minutes, row.start, row.end, row.direction]
        return tuple(dict.fromkeys(text for text in found if text))


def wave_label(words: dict, wave: int) -> str:
    return f"{words['wave_label']} {fmt.format_number(wave)}"


def _block_label(words: dict, block) -> str:
    if block.wave is None:
        return words["blocks"][block.id]["label"]
    if block.wave == 0:
        return f"{words['practice_label']} ({wave_label(words, block.wave)})"
    return wave_label(words, block.wave)


def schedule_rows(cfg: Config, texts: Texts) -> tuple[ScheduleRow, ...]:
    words = RevealView(cfg, texts).sheet(SHEET)
    rows = []
    elapsed = 0
    for block in cfg.session_schedule.blocks:
        rows.append(
            ScheduleRow(
                block_id=block.id,
                label=_block_label(words, block),
                minutes=fmt.format_number(block.minutes),
                start=fmt.format_number(elapsed),
                end=fmt.format_number(elapsed + block.minutes),
                direction=words["blocks"][block.id]["direction"],
            )
        )
        elapsed += block.minutes
    return tuple(rows)


def print_list_rows(cfg: Config, texts: Texts) -> tuple[PrintListRow, ...]:
    words = RevealView(cfg, texts).sheet(SHEET)
    schedule = cfg.session_schedule
    sheet_of_job = {worksheet_job(wave): wave for wave in cfg.waves}
    rows = []
    for item in schedule.print_list:
        if item.job in sheet_of_job:
            label = f"{words['print_attack_sheet']} {fmt.format_number(sheet_of_job[item.job].wave_id)}"
        elif item.job in words.get("print", {}):
            label = words["print"][item.job]
        else:
            raise PrintModelError(f"Die Druckliste nennt '{item.job}', aber sheets.ablauf.print.{item.job} fehlt")
        rows.append(
            PrintListRow(
                label=label,
                file=f"{item.job}.pdf",
                per_team=fmt.format_number(item.per_team),
                facilitator=fmt.format_number(item.facilitator),
                total=fmt.format_number(item.per_team * schedule.teams + item.facilitator),
            )
        )
    return tuple(rows)


def build_schedule_page(cfg: Config, texts: Texts) -> Optional[SchedulePage]:
    """The schedule and print-list page; None when the config has no `session_schedule` (e.g. the mini test config)."""
    schedule = cfg.session_schedule
    if schedule is None:
        return None
    words = RevealView(cfg, texts).sheet(SHEET)
    return SchedulePage(
        title=words["title"],
        intro=words["intro"],
        header=(
            words["head_block"], words["head_minutes"], words["head_span"], words["head_clock"],
            words["head_direction"],
        ),
        rows=schedule_rows(cfg, texts),
        total_label=words["total_label"],
        total_value=fmt.format_number(schedule.total_minutes),
        print_title=words["print_title"],
        print_intro=words["print_intro"],
        print_header=(
            words["print_head_label"], words["print_head_file"], words["print_head_team"],
            words["print_head_facilitator"], words["print_head_total"],
        ),
        print_rows=print_list_rows(cfg, texts),
        teams_label=words["teams_label"],
        teams_value=fmt.format_number(schedule.teams),
    )
