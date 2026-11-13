"""Facilitator-only debrief model (FLOW-03, D-08..D-11): four stages, fixed questions, three data prompts.

Guide minutes come from `session_schedule.debrief_stages`, the team rows from `session_schedule.teams`, all prose from
`sheets.debrief`. The page lies after the final results of the facilitator booklet; it names no attack and types no digit.
The optional management pitch (RISK-07, D-17) is no stage: it has no guide minutes and its speaking time comes from
`session_schedule.pitch_seconds`.
"""
from dataclasses import dataclass
from typing import Optional

from planspiel import fmt
from planspiel.cards import printed_strings
from planspiel.config import Config
from planspiel.printmodel import PrintModelError
from planspiel.texts import RevealView, Texts

SHEET = "debrief"
# Data prompts and the stage that carries them (D-09); every other stage holds questions only.
PROMPT_STAGES = {"compare": "description", "clues": "analysis", "window": "analysis"}


@dataclass(frozen=True)
class DebriefSection:
    title: str
    guide: str
    questions: tuple[str, ...]
    prompts: tuple[str, ...]


@dataclass(frozen=True)
class DebriefPage:
    title: str
    intro: str
    guide_label: str
    questions_label: str
    prompts_label: str
    stages: tuple[DebriefSection, ...]
    pitch_title: str
    pitch_text: str
    pitch_limit_label: str
    pitch_limit: str
    compare_title: str
    compare_intro: str
    compare_header: tuple[str, str, str, str]
    compare_rows: tuple[str, ...]
    total_label: str
    total_value: str

    def printed_fragments(self) -> tuple[str, ...]:
        """Every string of the page that ends up on the paper, without duplicates and without empty strings."""
        return tuple(dict.fromkeys(text for text in printed_strings(self) if text))


def build_debrief_page(cfg: Config, texts: Texts) -> Optional[DebriefPage]:
    """The debrief page; None when the config has no `session_schedule` or no `debrief_stages` (e.g. the mini config)."""
    schedule = cfg.session_schedule
    if schedule is None or not schedule.debrief_stages:
        return None
    stage_ids = [stage.id for stage in schedule.debrief_stages]
    for name, stage_id in PROMPT_STAGES.items():
        if stage_id not in stage_ids:
            raise PrintModelError(f"Der Datenimpuls '{name}' gehört zur Debriefing-Stufe '{stage_id}', die in debrief_stages fehlt")
    words = RevealView(cfg, texts).sheet(SHEET)
    clues_title = RevealView(cfg, texts).sheet("spielleitung")["clues_title"]
    unit = words["minutes_unit"]

    def prompt(name: str) -> str:
        text = words["prompts"][name]
        return f"{text} {words['clue_pointer']} {clues_title}" if name == "clues" else text

    stages = tuple(
        DebriefSection(
            title=words["stages"][stage.id]["title"],
            guide=f"{fmt.format_number(stage.minutes)} {unit}",
            questions=tuple(words["stages"][stage.id]["questions"]),
            prompts=tuple(prompt(name) for name, stage_id in PROMPT_STAGES.items() if stage_id == stage.id),
        )
        for stage in schedule.debrief_stages
    )
    total = sum(stage.minutes for stage in schedule.debrief_stages)
    pitch = schedule.pitch_seconds is not None
    return DebriefPage(
        title=words["title"],
        intro=words["intro"],
        guide_label=words["guide_label"],
        questions_label=words["questions_label"],
        prompts_label=words["prompts_label"],
        stages=stages,
        pitch_title=words["pitch_title"] if pitch else "",
        pitch_text=words["pitch_text"] if pitch else "",
        pitch_limit_label=words["pitch_limit_label"] if pitch else "",
        pitch_limit=f"{fmt.format_number(schedule.pitch_seconds)} {words['seconds_unit']}" if pitch else "",
        compare_title=words["compare_title"],
        compare_intro=words["compare_intro"],
        compare_header=(
            words["compare_head_team"], words["compare_head_kz"], words["compare_head_ros"],
            words["compare_head_final_index"],
        ),
        compare_rows=tuple(f"{words['team_label']} {fmt.format_number(number)}" for number in range(1, schedule.teams + 1)),
        total_label=words["total_label"],
        total_value=f"{fmt.format_number(total)} {unit}",
    )
