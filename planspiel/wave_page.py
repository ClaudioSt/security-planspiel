"""Print model of the one-page explainer "So funktioniert eine Welle" (PRINT-09, D-11, D-26).

The page is pre-wave material: it explains the order of a wave with symbols only, never a wave weight, threshold, cap
or attack name (VEIL-02). It speaks the vocabulary of the attack worksheet (`sheets.angriff` step headings and labels)
and of the tracking sheet (`sheets.tracking` clamp and window wording), so a player meets one set of words on all
three pages. The only numbers are the KZ bounds (`rules.KZ_MIN`, `rules.KZ_MAX`), the case numbers and the generated
recovery table (`rules.recovery_table`, independent of any attack: the page never says which waves allow recovery).

The module is a pre-wave builder: it never reads revealed text or wave data (VEIL-02).
"""
from dataclasses import dataclass

from planspiel import fmt, rules
from planspiel.cards import printed_strings
from planspiel.config import Config
from planspiel.eventtext import EFFECT_KINDS
from planspiel.printmodel import PrintModelError
from planspiel.texts import PreAttackView, Texts

WAVE_PAGE_JOB = "spieler-so-funktioniert-eine-welle"
EN_DASH = "–"
# The flow diagram of the template is laid out for exactly these steps (two rows of five, the second row read
# right to left). A change of the step list needs a new layout of the diagram.
STEP_KEYS = ("events", "cia", "e_value", "bonus", "reduction", "cases", "recovery", "wave_kz", "clamp", "window")
WORKSHEET_STEP_KEYS = ("cia", "e_value", "bonus", "reduction", "cases", "recovery", "wave_kz")
CASE_NUMBERS = (1, 2, 3)
# Event effect kinds that change something a team enters on the sheets; `window` and `review` are handled elsewhere.
EVENT_EFFECT_WORDS = {"kz": "effect_kz", "external_budget": "effect_budget", "external_opex": "effect_opex"}


@dataclass(frozen=True)
class FlowStep:
    """One step of the wave: its key, the heading (worksheet or tracking sheet wording) and a short explanation."""

    key: str
    heading: str
    text: str


@dataclass(frozen=True)
class WavePage:
    job: str
    title: str
    intro: str
    steps: tuple[FlowStep, ...]
    diagram_labels: tuple[str, ...]
    effects_header: tuple[str, str]
    attack_effects: tuple[str, ...]
    event_effects: tuple[str, ...]
    rounding_text: str
    clamp_text: str
    window_text: str
    ros_note: str
    recovery_title: str
    recovery_subtitle: str
    recovery_narrative: str
    recovery_measure_label: str
    recovery_header: tuple[str, str, str]
    recovery_rows: tuple[tuple[str, str, str], ...]

    def effect_rows(self) -> tuple[tuple[str, str], ...]:
        """The two effect lists side by side, the shorter one padded with empty cells."""
        count = max(len(self.attack_effects), len(self.event_effects))
        padded_attacks = (*self.attack_effects, *("",) * (count - len(self.attack_effects)))
        padded_events = (*self.event_effects, *("",) * (count - len(self.event_effects)))
        return tuple(zip(padded_attacks, padded_events))

    def printed_fragments(self) -> tuple[str, ...]:
        """Every string of the page that ends up on the paper, without duplicates and without empty strings."""
        return tuple(dict.fromkeys(text for text in printed_strings(self) if text and text != self.job))


def build_wave_page(cfg: Config, texts: Texts) -> WavePage:
    view = PreAttackView(cfg, texts)
    words, welle, labels = view.sheet("angriff"), view.sheet("welle"), view.sheet("labels")
    tracking, backup, karten = view.sheet("tracking"), view.sheet("backup_recovery"), view.sheet("karten")

    if not tracking["window_title"].startswith(welle["step_window"]):
        raise PrintModelError("Der Schritt 'Change-Fenster' muss mit dem Fenstertitel des Tracking-Bogens beginnen")
    rounding_text = words["wave_kz_rounding"]
    clamp_text = f"{tracking['clamp_lead']} {rules.KZ_MIN} {tracking['clamp_to']} {rules.KZ_MAX}"
    gr = f"{labels['total_reduction']} ({words['label_gr']})"
    cases = " ".join(f"{labels['case']} {number}: {welle[f'case_{number}']}" for number in CASE_NUMBERS)
    headings = {key: words[f"step_{key}"] for key in WORKSHEET_STEP_KEYS}
    headings.update(events=labels["events"], clamp=tracking["row_kz_after"], window=welle["step_window"])
    step_texts = {
        "events": welle["text_events"],
        "cia": welle["text_cia"],
        "e_value": f"{welle['text_e_value_lead']} {karten['legend_formula']}. {welle['text_e_value_reveal']}",
        "bonus": welle["text_bonus"],
        "reduction": f"{gr} = {labels['e_value']} + {labels['total_bonus']}. {welle['text_reduction']}",
        "cases": f"{welle['text_cases_lead']} {cases}",
        "recovery": welle["text_recovery"],
        "wave_kz": f"{welle['rounding_lead']} {rounding_text}.",
        "clamp": f"{clamp_text}. {welle['clamp_next']}",
        "window": welle["window_rules"],
    }
    steps = tuple(FlowStep(key, headings[key], step_texts[key]) for key in STEP_KEYS)

    kinds = dict.fromkeys(EFFECT_KINDS.values())
    event_effects = tuple(welle[word] for kind, word in EVENT_EFFECT_WORDS.items() if kind in kinds)

    measure_id, rows = rules.recovery_table(cfg)
    if measure_id is None:
        raise PrintModelError("Keine Maßnahme trägt Recovery: der Abschnitt Backup & Recovery hätte keine Tabelle (D-26)")
    measure_label = f"{measure_id} {EN_DASH} {cfg.measures[measure_id].name}"
    level_labels = backup["level_labels"]
    recovery_rows = tuple(
        (str(row.level), level_labels[str(row.level)], fmt.format_percent(row.factor)) for row in rows
    )

    return WavePage(
        job=WAVE_PAGE_JOB,
        title=welle["title"],
        intro=welle["intro"],
        steps=steps,
        diagram_labels=tuple(step.heading for step in steps),
        effects_header=(welle["effects_attacks_head"], welle["effects_events_head"]),
        attack_effects=(welle["effect_damage"], welle["effect_kz"]),
        event_effects=event_effects,
        rounding_text=step_texts["wave_kz"],
        clamp_text=clamp_text,
        window_text=welle["window_rules"],
        ros_note=welle["ros_note"],
        recovery_title=backup["title"],
        recovery_subtitle=backup["subtitle"],
        recovery_narrative=backup["narrative"],
        recovery_measure_label=measure_label,
        recovery_header=(labels["level"], measure_label, words["label_recovery_factor"]),
        recovery_rows=recovery_rows,
    )
