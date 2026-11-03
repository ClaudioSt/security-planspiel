"""Inhaltsquelle content/texte.toml: Laden, Abdeckung gegen die Config, Ziffern-Lint, Story-Lint.

Alle deutschen Texte für Druckmaterial stehen einmal in content/texte.toml, geordnet nach Config-ID.
Zahlen stehen nie in der Prosa: Sie kommen aus der Config und werden im Code erzeugt (D-03).
"""
import copy
import re
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from planspiel import audience, rules
from planspiel.config import Config, Wave
from planspiel.review_text import format_eur
from planspiel.validate import Issue

CONTENT_DIR = Path(__file__).resolve().parents[1] / "content"
TEXTE_FILE = "texte.toml"
ALLOWLIST_FILE = "digit_allowlist.toml"
GIVEAWAY_FILE = "giveaway_terms.toml"
CLUES_FILE = "clues.toml"
PREWAVE_PREFIXES = ("story.", "measures.")
MIN_QUOTE_LENGTH = 15
CLUE_WEIGHTS = (1, 2, 3)
CLUE_SCORE_MIN = 2
CLUE_SCORE_TOP = 4

STORY_DOCS = ("steckbrief", "zeitungsartikel", "anfrage_mail", "audit_mail")
PREWAVE_SHEETS = (
    "budget", "ros", "backup_recovery", "labels", "karten", "eventkarten", "teamheft", "tracking", "angriff", "welle"
)
CASE_KEYS = ("case_1", "case_2", "case_3")

_SHEET_LABELS = (
    "measure", "level", "base_protection", "sum", "from_level", "bonus", "fulfilled", "total_bonus",
    "total_reduction", "e_value", "damage", "satisfaction", "case", "cost_type", "what", "when", "tier",
    "available_budget", "period", "init_costs", "opex", "anticipated_sum",
    "budget_remaining", "damage_wave", "start", "after_wave", "events",
    "metric", "value", "total_init", "total_opex", "total_costs", "avoided_damage", "event_after_wave",
    "condition_met", "effect", "no_implementation", "final_damage", "min_level",
    "mail_from", "mail_to", "mail_subject",
)

_KARTEN_KEYS = (
    "legend_title", "legend_intro", "legend_cia", "legend_formula", "legend_reveal", "legend_costs",
    "legend_dependency", "legend_levels", "per_wave", "requires",
)

_EVENTKARTEN_KEYS = (
    "review_header", "kz", "fulfilled", "each_at_least", "level_of_measure", "per_measure_at_level",
    "condition_if", "condition_and", "level_equals", "otherwise", "total_budget", "opex_costs",
    "per_active_measure", "kurswechsel_window", "tier_heading", "tier_from", "overspend_label", "per_started",
)

_TEAMHEFT_KEYS = (
    "planning_title", "planning_instruction", "step_costs", "step_tiers", "step_planning", "kz_start",
    "opex_per_wave", "ros_title", "ros_carry_hint", "window_differences", "init_differences", "own_costs",
    "damage_sum", "ros_short", "review_title", "review_intro", "tier_budget", "budget_event", "event_opex",
    "review_costs", "remaining_budget", "sign_hint", "kz_change", "penalty_title", "penalty_intro",
    "overspend_header",
)

_TRACKING_KEYS = (
    "title", "intro", "wave", "row_kz_before", "row_kz_change", "row_kz_after",
    "row_damage", "block_own", "row_own_opex", "row_own_window", "block_external", "row_external_budget",
    "row_external_opex", "row_remaining", "row_kz_review", "row_kz_final", "kz_after_last", "remaining_previous",
    "rounding_hint", "clamp_lead", "clamp_to", "external_hint", "window_title", "window_intro",
    "window_level", "window_delta", "window_sum", "window_credit", "window_credit_short", "window_net", "never_refund", "credit_hint",
    "next_wave_hint",
)

_WELLE_KEYS = (
    "title", "intro", "text_events", "text_cia", "text_e_value_lead", "text_e_value_reveal", "text_bonus",
    "text_reduction", "text_cases_lead", "case_1", "case_2", "case_3", "text_recovery", "rounding_lead",
    "clamp_next", "window_rules", "step_window", "effects_attacks_head", "effects_events_head", "effect_damage",
    "effect_kz", "effect_budget", "effect_opex", "ros_note",
)

_SPIELLEITUNG_KEYS = (
    "title", "notice", "intro", "gr_legend", "contents_title", "how_to_title", "how_to", "paths_title", "paths_intro",
    "path_start", "path_window", "path_swap", "params_title", "param_weights", "param_unit", "param_slope",
    "param_kz_full_damage", "param_kz_full_defence", "param_recovery", "recovery_allowed", "recovery_not_allowed",
    "bonus_title", "bonus_reason_head", "check_title", "check_case_head", "check_kz_head",
    "check_table_intro", "events_title", "events_none", "event_head_name", "event_head_kind", "event_head_effect",
    "kind_window", "kind_external_opex", "kind_external_budget", "kind_kz", "kind_review", "keys_title", "keys_intro",
    "key_head", "key_selection", "key_cia", "key_e_value", "key_bonus", "key_gr", "key_case", "key_damage_before",
    "key_recovery", "key_damage_after", "key_kz_attack", "key_kz_event", "key_kz_exact", "key_kz_change",
    "key_kz_before", "key_kz_unclamped", "key_kz_after", "key_own_opex", "key_window_cost", "key_external_budget",
    "key_external_opex", "key_remaining", "review_intro", "review_x", "review_step", "final_title", "final_intro",
    "final_head", "final_remaining", "final_review_delta", "final_kz", "final_own_spend", "final_total_damage",
    "final_ros", "final_index", "final_index_weight", "final_index_note", "welle0_title", "welle0_intro",
    "clues_title", "clues_intro", "clue_head_nr", "clue_head_document", "clue_head_section", "clue_head_quote",
    "clue_head_why", "clue_head_measures", "clue_section_anfrage_mail_lage", "clue_section_audit_mail_einleitung",
    "clue_section_zeitungsartikel",
)

SHEET_KEYS = (
    "sheets.angriff.start_values_intro",
    "sheets.angriff.cia_table_instruction",
    "sheets.angriff.e_value_intro",
    "sheets.angriff.bonus_intro",
    "sheets.angriff.case_3_hint",
    "sheets.angriff.step_cia",
    "sheets.angriff.step_e_value",
    "sheets.angriff.step_bonus",
    "sheets.angriff.step_reduction",
    "sheets.angriff.step_cases",
    "sheets.angriff.step_recovery",
    "sheets.angriff.step_wave_kz",
    "sheets.angriff.label_step",
    "sheets.angriff.label_gr",
    "sheets.angriff.label_kz",
    "sheets.angriff.label_kz_attack",
    "sheets.angriff.label_kz_events",
    "sheets.angriff.label_result",
    "sheets.angriff.label_damage_before_recovery",
    "sheets.angriff.label_damage_after_recovery",
    "sheets.angriff.label_recovery_factor",
    "sheets.angriff.label_threshold",
    "sheets.angriff.label_cap",
    "sheets.angriff.label_upper",
    "sheets.angriff.cap_intro",
    "sheets.angriff.recovery_intro",
    "sheets.angriff.kz_decimals_hint",
    "sheets.angriff.kz_fraction_hint",
    "sheets.angriff.events_hint",
    "sheets.angriff.wave_kz_rounding",
    "sheets.budget.title",
    "sheets.budget.intro",
    "sheets.budget.init_what",
    "sheets.budget.init_when",
    "sheets.budget.opex_what",
    "sheets.budget.opex_when",
    "sheets.budget.tier_intro",
    "sheets.budget.anticipated_sum_intro",
    "sheets.ros.title",
    "sheets.ros.instruction",
    "sheets.ros.purpose",
    "sheets.backup_recovery.title",
    "sheets.backup_recovery.subtitle",
    "sheets.backup_recovery.narrative",
    *(f"sheets.backup_recovery.level_labels.{level}" for level in range(4)),
    *(f"sheets.karten.{name}" for name in _KARTEN_KEYS),
    *(f"sheets.eventkarten.{name}" for name in _EVENTKARTEN_KEYS),
    *(f"sheets.teamheft.{name}" for name in _TEAMHEFT_KEYS),
    *(f"sheets.tracking.{name}" for name in _TRACKING_KEYS),
    *(f"sheets.welle.{name}" for name in _WELLE_KEYS),
    *(f"sheets.spielleitung.{name}" for name in _SPIELLEITUNG_KEYS),
    *(f"sheets.labels.{name}" for name in _SHEET_LABELS),
)

_ABLAUF_KEYS = (
    "title", "intro", "head_block", "head_minutes", "head_span", "head_clock", "head_direction", "wave_label",
    "practice_label", "total_label", "print_title", "print_intro", "print_head_label", "print_head_file",
    "print_head_team", "print_head_facilitator", "print_head_total", "print_attack_sheet", "teams_label",
)
# Required only when the config carries a session_schedule, so the mini fixture needs no schedule texts.
ABLAUF_KEYS = tuple(f"sheets.ablauf.{name}" for name in _ABLAUF_KEYS)

_DEBRIEF_KEYS = (
    "title", "intro", "guide_label", "questions_label", "prompts_label", "minutes_unit", "compare_title",
    "compare_intro", "compare_head_team", "compare_head_kz", "compare_head_ros", "compare_head_final_index",
    "team_label", "clue_pointer", "total_label",
)
# Required only when the config carries debrief_stages; stage and prompt keys follow the config ids (FLOW-03).
DEBRIEF_KEYS = tuple(f"sheets.debrief.{name}" for name in _DEBRIEF_KEYS)
DEBRIEF_PROMPT_KEYS = tuple(f"sheets.debrief.prompts.{name}" for name in ("compare", "clues", "window"))

PRACTICE_KEYS = tuple(
    f"practice.{name}"
    for name in (
        "title", "intro", "narrative", "cia_rationale", *CASE_KEYS, "selection_title", "event_result", "tracking_title",
    )
)

EVENT_KEYS_BY_TYPE = {
    "kurswechsel": ("narrative", "rule"),
    "opex_discount_per_active_measure": ("narrative", "rule"),
    "flat_budget": ("narrative", "rule"),
    "checklist_tier": ("narrative", "checklist_heading"),
    "measure_level_tier": ("narrative",),
    "level_bonus_per_measure": ("narrative",),
    "and_condition": ("narrative",),
    "final_budget_tier": ("narrative", "rule"),
}

STORY_MECHANICS_PATTERNS = (
    re.compile(r"\bKZ\b"),
    re.compile(r"Kundenzufriedenheit", re.IGNORECASE),
    re.compile(r"\bOPEX\b", re.IGNORECASE),
    re.compile(r"Init-Kosten", re.IGNORECASE),
    re.compile(r"Budget-Tier", re.IGNORECASE),
    re.compile(r"\bRoS\b"),
    re.compile(r"E-Wert"),
    re.compile(r"Level\s?\d"),
)


@dataclass(frozen=True)
class Texts:
    """Geladener Inhalt als verschachteltes Wörterbuch, adressiert über Punkt-Schlüssel."""

    data: dict

    def get(self, key: str) -> str | list[str]:
        node: object = self.data
        for part in key.split("."):
            if not isinstance(node, dict) or part not in node:
                raise KeyError(f"Schlüssel '{key}' fehlt in der Inhaltsquelle")
            node = node[part]
        return node  # type: ignore[return-value]

    def has(self, key: str) -> bool:
        try:
            self.get(key)
        except KeyError:
            return False
        return True

    def leaves(self) -> list[tuple[str, object]]:
        found: list[tuple[str, object]] = []

        def walk(prefix: str, node: dict) -> None:
            for name, value in node.items():
                key = f"{prefix}.{name}" if prefix else str(name)
                if isinstance(value, dict):
                    walk(key, value)
                else:
                    found.append((key, value))

        walk("", self.data)
        return found

    def strings(self, prefix: str = "") -> list[tuple[str, str]]:
        wanted = prefix.rstrip(".")
        found: list[tuple[str, str]] = []
        for key, value in self.leaves():
            if wanted and key != wanted and not key.startswith(wanted + "."):
                continue
            if isinstance(value, str):
                found.append((key, value))
            elif isinstance(value, list):
                found.extend((key, item) for item in value if isinstance(item, str))
        return found

    def subtree(self, prefix: str) -> dict:
        node = self.get(prefix)
        if not isinstance(node, dict):
            raise KeyError(f"Schlüssel '{prefix}' ist kein Abschnitt")
        return node


@dataclass(frozen=True)
class AllowEntry:
    key: str
    token: str
    why: str


@dataclass(frozen=True)
class GiveawayTerms:
    """Verbotene Begriffe (D-13b) und die Ausnahmen für Story- und Event-Texte (D-20)."""

    substrings: tuple[str, ...]
    tokens: tuple[str, ...]
    compounds: tuple[tuple[str, str], ...]
    story_exception_tokens: tuple[str, ...]
    story_exception_substrings: tuple[str, ...]


@dataclass(frozen=True)
class Content:
    texts: Texts
    allowlist: tuple[AllowEntry, ...]
    terms: GiveawayTerms


def load_texts(path: Path) -> Texts:
    with open(path, "rb") as handle:
        return Texts(tomllib.load(handle))


def load_allowlist(path: Path) -> tuple[AllowEntry, ...]:
    with open(path, "rb") as handle:
        data = tomllib.load(handle)
    return tuple(
        AllowEntry(key=entry["key"], token=entry["token"], why=entry.get("why", ""))
        for entry in data.get("allow", [])
    )


def load_giveaway_terms(path: Path) -> GiveawayTerms:
    with open(path, "rb") as handle:
        data = tomllib.load(handle)
    exceptions = data.get("story_exceptions", {})
    return GiveawayTerms(
        substrings=tuple(data.get("substrings", [])),
        tokens=tuple(data.get("tokens", [])),
        compounds=tuple((first, second) for first, second in data.get("compounds", [])),
        story_exception_tokens=tuple(exceptions.get("tokens", [])),
        story_exception_substrings=tuple(exceptions.get("substrings", [])),
    )


def load_content(content_dir: Path = CONTENT_DIR) -> Content:
    return Content(
        texts=load_texts(content_dir / TEXTE_FILE),
        allowlist=load_allowlist(content_dir / ALLOWLIST_FILE),
        terms=load_giveaway_terms(content_dir / GIVEAWAY_FILE),
    )


def _event_keys(prefix: str, event) -> set[str]:
    keys = {f"{prefix}.{name}" for name in EVENT_KEYS_BY_TYPE.get(event.type, ("narrative",))}
    if event.type == "measure_level_tier":
        keys.update(f"{prefix}.tier_labels.{tier}" for tier in event.params["tiers"])
    return keys


def required_keys(cfg: Config) -> set[str]:
    """Alle Schlüssel, die die Config verlangt; neue Config-IDs erzeugen sofort neue Pflichtschlüssel."""
    keys: set[str] = set()
    for measure_id, measure in cfg.measures.items():
        base = f"measures.{measure_id}"
        keys.update({f"{base}.focus", f"{base}.description"})
        for level_id in measure.levels:
            if level_id > 0:
                keys.add(f"{base}.levels_desc.{level_id}")
                keys.add(f"{base}.levels_simple.{level_id}")
    for attack_id in cfg.attacks:
        keys.add(f"attacks.{attack_id}.veiled.title")
        base = f"attacks.{attack_id}.revealed"
        keys.update(f"{base}.{name}" for name in ("name", "narrative", "cia_rationale", *CASE_KEYS))
    for wave in cfg.waves:
        for bonus_measure in wave.bonus_measures:
            keys.add(f"attacks.{wave.attack_id}.revealed.bonus_reasons.{bonus_measure.measure}")
    for wave_events in cfg.events.values():
        for event in wave_events:
            keys.update(_event_keys(f"events.{event.id}", event))
    for event in cfg.final_events:
        keys.update(_event_keys(f"final_events.{event.id}", event))
    keys.update(SHEET_KEYS)
    keys.update(f"story.{doc}.doc_title" for doc in STORY_DOCS)
    if cfg.practice is not None:
        keys.update(PRACTICE_KEYS)
        keys.update(f"practice.bonus_reasons.{bonus.measure}" for bonus in cfg.practice.wave.bonus_measures)
        keys.update(_event_keys("practice.event", cfg.practice.event))
    if cfg.session_schedule is not None:
        keys.update(ABLAUF_KEYS)
        for block in cfg.session_schedule.blocks:
            keys.add(f"sheets.ablauf.blocks.{block.id}.direction")
            if block.wave is None:
                keys.add(f"sheets.ablauf.blocks.{block.id}.label")
        for row in cfg.session_schedule.print_list:
            if audience.audience_of(row.job) != audience.REVEALED:
                keys.add(f"sheets.ablauf.print.{row.job}")
        if cfg.session_schedule.debrief_stages:
            keys.update(DEBRIEF_KEYS)
            keys.update(DEBRIEF_PROMPT_KEYS)
            for stage in cfg.session_schedule.debrief_stages:
                keys.update({f"sheets.debrief.stages.{stage.id}.title", f"sheets.debrief.stages.{stage.id}.questions"})
    return keys


def _under_story_doc(key: str) -> bool:
    return any(key.startswith(f"story.{doc}.") for doc in STORY_DOCS)


def check_coverage(cfg: Config, texts: Texts) -> list[Issue]:
    required = required_keys(cfg)
    leaves = texts.leaves()
    present = {key for key, _ in leaves}
    issues = [
        Issue("error", "texts.missing_key", key, f"Pflichtschlüssel '{key}' fehlt in content/texte.toml")
        for key in sorted(required - present)
    ]
    for key, value in leaves:
        if key not in required and not _under_story_doc(key):
            issues.append(
                Issue("error", "texts.orphan_key", key, f"Schlüssel '{key}' gehört zu keiner Config-ID oder deklarierten Liste")
            )
        items = value if isinstance(value, list) else [value]
        if not items or not all(isinstance(item, str) for item in items):
            issues.append(Issue("error", "texts.type", key, "Text oder Liste von Texten erwartet"))
        elif any(not item.strip() for item in items):
            issues.append(Issue("error", "texts.empty", key, "Text darf nicht leer sein"))
    return issues


def check_digits(texts: Texts, allowlist: tuple[AllowEntry, ...]) -> list[Issue]:
    """Strikt: jede Ziffer außerhalb von story.* fällt durch, außer der exakte Token steht auf der Allowlist."""
    issues: list[Issue] = []
    by_key: dict[str, list[AllowEntry]] = {}
    for entry in allowlist:
        by_key.setdefault(entry.key, []).append(entry)
        if not entry.why.strip():
            issues.append(
                Issue("error", "texts.allowlist_reason", entry.key, f"Allowlist-Eintrag '{entry.token}' braucht eine Begründung")
            )
        strings = [text for key, text in texts.strings() if key == entry.key]
        if not strings or not any(entry.token in text for text in strings):
            issues.append(
                Issue(
                    "error",
                    "texts.allowlist_stale",
                    entry.key,
                    f"Allowlist-Eintrag '{entry.token}' passt auf keinen Text mehr und muss entfernt werden",
                )
            )
    for key, text in texts.strings():
        if key == "story" or key.startswith("story."):
            continue
        remaining = text
        for entry in by_key.get(key, []):
            remaining = remaining.replace(entry.token, "")
        if any(char.isnumeric() for char in remaining):
            issues.append(
                Issue("error", "texts.digit", key, "Ziffer in der Prosa; Zahlen kommen aus der Config oder stehen auf der Allowlist")
            )
    return issues


def check_story_mechanics(cfg: Config, texts: Texts) -> list[Issue]:
    """Story-Texte dürfen weder Spielmechanik-Vokabular noch Budget-Tier-Beträge nennen (D-15)."""
    amounts = [format_eur(tier.budget * 1000) for tier in cfg.budget_tiers.values()]
    issues: list[Issue] = []
    for key, text in texts.strings("story"):
        hit = next((pattern.search(text) for pattern in STORY_MECHANICS_PATTERNS if pattern.search(text)), None)
        amount = next((value for value in amounts if value in text), None)
        if hit is not None:
            issues.append(
                Issue("error", "texts.story_mechanics", key, f"Story-Text nennt Spielmechanik ('{hit.group(0)}')")
            )
        elif amount is not None:
            issues.append(
                Issue("error", "texts.story_mechanics", key, f"Story-Text nennt einen Budget-Tier-Betrag ('{amount}')")
            )
    return issues


_DASHES = {code: "-" for code in (*range(0x2010, 0x2016), 0x2212)}
_INVISIBLE = {code: None for code in (0x00AD, 0x200B, 0x200C, 0x200D, 0xFEFF)}
_WORD = r"[^\W\d_]"
PROFILES = ("veiled", "story")


def normalize_for_matching(text: str) -> str:
    """NFC, Strichvarianten zu '-', unsichtbare Zeichen entfernt, klein geschrieben (lower, nicht casefold: ß bleibt)."""
    normalised = unicodedata.normalize("NFC", text).translate(_DASHES).translate(_INVISIBLE)
    return normalised.lower()


def giveaway_hits(text: str, terms: GiveawayTerms, attack_ids, *, profile: str) -> list[str]:
    """Verbotene Begriffe im Text. Profil 'veiled' hat keine Ausnahmen, 'story' zieht die D-20-Ausnahmen ab."""
    if profile not in PROFILES:
        raise ValueError(f"Unbekanntes Profil '{profile}', erlaubt sind {PROFILES}")
    normalised = normalize_for_matching(text)
    ids = [attack_id.lower() for attack_id in attack_ids]
    substrings = {term.lower() for term in terms.substrings} | {name for name in ids if len(name) >= 5}
    tokens = {term.lower() for term in terms.tokens} | {name for name in ids if len(name) < 5}
    if profile == "story":
        substrings -= {term.lower() for term in terms.story_exception_substrings}
        tokens -= {term.lower() for term in terms.story_exception_tokens}
    hits = {term for term in substrings if term in normalised}
    hits |= tokens & set(re.findall(rf"{_WORD}+", normalised))
    for first, second in terms.compounds:
        pattern = rf"(?<!{_WORD}){re.escape(first.lower())}[\s-]*{re.escape(second.lower())}"
        if re.search(pattern, normalised):
            hits.add(f"{first.lower()}-{second.lower()}")
    return sorted(hits)


def _giveaway_issue(path: str, hits: list[str], profile: str) -> Issue:
    scope = "verhülltem Angriffstext" if profile == "veiled" else "Story- oder Event-Text"
    return Issue("error", "texts.giveaway", path, f"Verbotener Begriff in {scope}: {', '.join(hits)}")


def check_giveaway(cfg: Config, texts: Texts, terms: GiveawayTerms) -> list[Issue]:
    """Verhüllte Angriffsschlüssel ohne Ausnahmen; Story-Dokumente, Event-Texte und Event-Namen mit Story-Profil (D-13b, D-13c, D-16, D-20)."""
    attack_ids = tuple(cfg.attacks)
    issues: list[Issue] = []
    scoped = [(f"attacks.{attack_id}.veiled", "veiled") for attack_id in cfg.attacks]
    scoped += [("events", "story"), ("final_events", "story"), ("story", "story"), ("practice", "story")]
    for prefix, profile in scoped:
        for key, text in texts.strings(prefix):
            hits = giveaway_hits(text, terms, attack_ids, profile=profile)
            if hits:
                issues.append(_giveaway_issue(key, hits, profile))
    named = [(f"events.{event.id}", event) for events in cfg.events.values() for event in events]
    named += [(f"final_events.{event.id}", event) for event in cfg.final_events]
    for prefix, event in named:
        hits = giveaway_hits(event.name, terms, attack_ids, profile="story")
        if hits:
            issues.append(_giveaway_issue(f"{prefix}.name (config)", hits, "story"))
    return issues


def check_texts(cfg: Config, content: Content) -> list[Issue]:
    return [
        *check_coverage(cfg, content.texts),
        *check_digits(content.texts, content.allowlist),
        *check_story_mechanics(cfg, content.texts),
        *check_giveaway(cfg, content.texts, content.terms),
    ]


def attack_title(texts: Texts, attack_id: str, position: int, *, revealed: bool = False) -> str:
    """Titel eines Angriffs; die Nummer ist die Wellenposition aus dem Code, nie ein Wert aus dem TOML (D-23)."""
    title = f"{texts.get(f'attacks.{attack_id}.veiled.title')} {position}"
    if revealed:
        return f"{title}: {texts.get(f'attacks.{attack_id}.revealed.name')}"
    return title


def _levels(node: dict) -> dict[int, str]:
    return {int(level): text for level, text in node.items()}


class PreAttackView:
    """Sicht für alles, was vor einer Welle gedruckt wird: nur verhüllte Titel, Maßnahmen, Events, Vorab-Blätter, Story.

    Die Sicht liest keinen Schlüssel unterhalb von attacks.<id>.revealed und bietet keinen Zugriff darauf (D-13).
    """

    def __init__(self, cfg: Config, texts: Texts) -> None:
        self._cfg = cfg
        self._texts = texts

    def attack_title(self, wave: Wave) -> str:
        return attack_title(self._texts, wave.attack_id, wave.wave_id)

    def measure(self, measure_id: str) -> dict:
        if measure_id not in self._cfg.measures:
            raise KeyError(f"Maßnahme '{measure_id}' gibt es in der Config nicht")
        base = f"measures.{measure_id}"
        return {
            "focus": self._texts.get(f"{base}.focus"),
            "description": self._texts.get(f"{base}.description"),
            "levels_desc": _levels(self._texts.subtree(f"{base}.levels_desc")),
            "levels_simple": _levels(self._texts.subtree(f"{base}.levels_simple")),
        }

    def _event_prefix(self, event_id: str) -> str:
        if any(event.id == event_id for events in self._cfg.events.values() for event in events):
            return f"events.{event_id}"
        if any(event.id == event_id for event in self._cfg.final_events):
            return f"final_events.{event_id}"
        raise KeyError(f"Event '{event_id}' gibt es in der Config nicht")

    def event(self, event_id: str) -> dict:
        return copy.deepcopy(self._texts.subtree(self._event_prefix(event_id)))

    def story(self, doc: str) -> dict:
        if doc not in STORY_DOCS:
            raise KeyError(f"Story-Dokument '{doc}' gibt es nicht")
        return copy.deepcopy(self._texts.subtree(f"story.{doc}"))

    def sheet(self, name: str) -> dict:
        if name not in PREWAVE_SHEETS:
            raise KeyError(f"Blatt '{name}' ist vor der Welle nicht zugänglich")
        return copy.deepcopy(self._texts.subtree(f"sheets.{name}"))

    def strings(self) -> list[str]:
        """Jeder Text, den diese Sicht liefern kann (Grundlage des Leak-Tests)."""
        found = [self.attack_title(wave) for wave in self._cfg.waves]
        for measure_id in self._cfg.measures:
            found.extend(text for _, text in self._texts.strings(f"measures.{measure_id}"))
        for events in self._cfg.events.values():
            for event in events:
                found.extend(text for _, text in self._texts.strings(self._event_prefix(event.id)))
        for event in self._cfg.final_events:
            found.extend(text for _, text in self._texts.strings(self._event_prefix(event.id)))
        for name in PREWAVE_SHEETS:
            found.extend(text for _, text in self._texts.strings(f"sheets.{name}"))
        found.extend(text for _, text in self._texts.strings("story"))
        return found


@dataclass(frozen=True)
class Clue:
    """Ein Hinweis auf einen Angriff in einem Vorab-Dokument: Quelle, wörtliches Zitat, Begründung (D-17)."""

    attack: str
    source: str
    quote: str
    why: str
    measures: tuple[str, ...] = ()
    weight: int = 0


@dataclass(frozen=True)
class ClueRow:
    title: str
    number: int
    document: str
    section: str
    quote: str
    why: str
    measures: str = ""


def _clue_mapping(number: int, entry: dict) -> tuple[tuple[str, ...], int]:
    measures = entry.get("measures", [])
    if not isinstance(measures, list) or not all(isinstance(item, str) for item in measures):
        raise ValueError(f"Hinweis {number}: 'measures' muss eine Liste von Maßnahmen-Kennungen (Text) sein")
    weight = entry.get("weight", 0)
    if isinstance(weight, bool) or not isinstance(weight, int):
        raise ValueError(f"Hinweis {number}: 'weight' muss eine ganze Zahl sein")
    return tuple(measures), weight


def load_clues(path: Path) -> tuple[Clue, ...]:
    with open(path, "rb") as handle:
        data = tomllib.load(handle)
    clues = []
    for number, entry in enumerate(data.get("clue", []), start=1):
        measures, weight = _clue_mapping(number, entry)
        clues.append(
            Clue(
                attack=str(entry.get("attack", "")),
                source=str(entry.get("source", "")),
                quote=str(entry.get("quote", "")),
                why=str(entry.get("why", "")),
                measures=measures,
                weight=weight,
            )
        )
    return tuple(clues)


def clue_scores(clues: tuple[Clue, ...]) -> dict[str, int]:
    """Hinweis-Punkte je Maßnahme: Summe der Gewichte aller Hinweise, die sie nennen (D-17)."""
    scores: dict[str, int] = {}
    for clue in clues:
        for measure_id in clue.measures:
            scores[measure_id] = scores.get(measure_id, 0) + clue.weight
    return scores


def clue_mapping_issues(cfg: Config, clues: tuple[Clue, ...]) -> list[Issue]:
    """Jede Bonus-Maßnahme ist gestützt, die Punkte folgen der Wichtigkeit, die wichtigste hat mindestens CLUE_SCORE_TOP (D-18)."""
    scores = clue_scores(clues)
    importance = rules.bonus_importance(cfg)
    ranked = sorted(importance, key=lambda measure_id: (-importance[measure_id], measure_id))
    issues: list[Issue] = []
    for measure_id in ranked:
        if scores.get(measure_id, 0) < CLUE_SCORE_MIN:
            issues.append(
                Issue(
                    "error",
                    "clues.unsupported_bonus",
                    f"clues.measures.{measure_id}",
                    f"Bonus-Maßnahme '{measure_id}' hat {scores.get(measure_id, 0)} Hinweis-Punkt(e), nötig sind mindestens {CLUE_SCORE_MIN}",
                )
            )
    for measure_id in ranked:
        outranking = [
            other
            for other in ranked
            if importance[other] < importance[measure_id] and scores.get(other, 0) > scores.get(measure_id, 0)
        ]
        if outranking:
            issues.append(
                Issue(
                    "error",
                    "clues.not_graduated",
                    f"clues.measures.{measure_id}",
                    f"Bonus-Maßnahme '{measure_id}' ist wichtiger als '{outranking[0]}', hat aber weniger Hinweis-Punkte",
                )
            )
    if ranked and scores.get(ranked[0], 0) < CLUE_SCORE_TOP:
        issues.append(
            Issue(
                "error",
                "clues.top_too_weak",
                f"clues.measures.{ranked[0]}",
                f"Die wichtigste Bonus-Maßnahme '{ranked[0]}' braucht mindestens {CLUE_SCORE_TOP} Hinweis-Punkte",
            )
        )
    return issues


def _clue_document(source: str) -> str | None:
    """Dokument-Kennung einer Quelle: 'story.<doc>' für Story-Texte, 'measures' für Maßnahmentexte (D-18)."""
    parts = source.split(".")
    if parts[0] == "story" and len(parts) > 1:
        return f"story.{parts[1]}"
    if parts[0] == "measures":
        return "measures"
    return None


def _source_strings(texts: Texts, source: str) -> list[str] | None:
    if not texts.has(source):
        return None
    value = texts.get(source)
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    return None


def check_clues(cfg: Config, texts: Texts, clues: tuple[Clue, ...], require_mapping: bool = True) -> list[Issue]:
    """Mindestens zwei wörtliche Hinweise aus zwei Vorab-Dokumenten je Angriff der Wellen (VEIL-03, D-17, D-18).

    Mit `require_mapping` muss außerdem die Maßnahmen-Zuordnung vollständig und nach Wichtigkeit gestaffelt sein.
    """
    attack_ids = list(dict.fromkeys(wave.attack_id for wave in cfg.waves))
    issues: list[Issue] = []
    documents: dict[str, set[str]] = {attack_id: set() for attack_id in attack_ids}
    counts = {attack_id: 0 for attack_id in attack_ids}
    for number, clue in enumerate(clues, start=1):
        path = f"clues[{number}]"
        if clue.attack not in counts:
            issues.append(
                Issue("error", "clues.unknown_attack", path, f"Angriff '{clue.attack}' kommt in den Wellen der Config nicht vor")
            )
            continue
        counts[clue.attack] += 1
        for measure_id in clue.measures:
            if measure_id not in cfg.measures:
                issues.append(
                    Issue("error", "clues.unknown_measure", path, f"Maßnahme '{measure_id}' kommt in der Config nicht vor")
                )
        if (clue.weight not in CLUE_WEIGHTS) if clue.measures else (clue.weight != 0):
            issues.append(
                Issue(
                    "error",
                    "clues.bad_weight",
                    path,
                    f"Gewicht {clue.weight} ist ungültig (mit Maßnahmen {CLUE_WEIGHTS[0]} bis {CLUE_WEIGHTS[-1]}, ohne Maßnahmen 0)",
                )
            )
        document = _clue_document(clue.source)
        if document is not None:
            documents[clue.attack].add(document)
        if not clue.source.startswith(PREWAVE_PREFIXES):
            issues.append(
                Issue("error", "clues.not_prewave", path, f"Quelle '{clue.source}' ist kein Vorab-Material (erlaubt: story.*, measures.*)")
            )
            continue
        if not clue.why.strip():
            issues.append(Issue("error", "clues.empty_why", path, "Die Begründung des Hinweises darf nicht leer sein"))
        strings = _source_strings(texts, clue.source)
        quote = unicodedata.normalize("NFC", clue.quote)
        if strings is None:
            issues.append(
                Issue("error", "clues.unknown_source", path, f"Quelle '{clue.source}' ist kein Text in content/texte.toml")
            )
        elif len(quote) < MIN_QUOTE_LENGTH:
            issues.append(
                Issue("error", "clues.quote_too_short", path, f"Das Zitat braucht mindestens {MIN_QUOTE_LENGTH} Zeichen")
            )
        elif not any(quote in unicodedata.normalize("NFC", text) for text in strings):
            issues.append(
                Issue("error", "clues.quote_not_found", path, f"Das Zitat steht nicht wörtlich in '{clue.source}'")
            )
    for attack_id in attack_ids:
        if counts[attack_id] < 2:
            issues.append(
                Issue("error", "clues.too_few", f"clues.{attack_id}", f"Angriff '{attack_id}' hat {counts[attack_id]} Hinweis(e), nötig sind mindestens zwei")
            )
        elif len(documents[attack_id]) < 2:
            issues.append(
                Issue("error", "clues.single_source", f"clues.{attack_id}", f"Die Hinweise zu '{attack_id}' stammen aus weniger als zwei verschiedenen Dokumenten")
            )
    if require_mapping:
        issues.extend(clue_mapping_issues(cfg, clues))
    return issues


def _clue_section(texts: Texts, source: str) -> str:
    """Nächste Überschrift (`heading`, sonst `headline`) entlang des Quellpfads, sonst das Abschnitts-Label der Spielleitung, sonst der Quellschlüssel."""
    parts = source.split(".")[:-1]
    label_key = "sheets.spielleitung.clue_section_" + "_".join(parts[1:])
    while parts:
        for name in ("heading", "headline"):
            key = ".".join([*parts, name])
            if texts.has(key) and isinstance(texts.get(key), str):
                return str(texts.get(key))
        parts.pop()
    if texts.has(label_key) and isinstance(texts.get(label_key), str):
        return str(texts.get(label_key))
    return source


class FacilitatorView:
    """Sicht für die Spielleitung: die Hinweis-Matrix mit enthüllten Angriffsnamen. Nie Teil von PreAttackView."""

    def __init__(self, cfg: Config, texts: Texts, clues: tuple[Clue, ...]) -> None:
        self._cfg = cfg
        self._texts = texts
        self._clues = clues

    def _document_title(self, source: str) -> str:
        document = _clue_document(source)
        if document is None:
            return source
        if document == "measures":
            measure_id = source.split(".")[1] if source.count(".") >= 1 else ""
            measure = self._cfg.measures.get(measure_id)
            return measure.name if measure is not None else document
        title_key = f"{document}.doc_title"
        return str(self._texts.get(title_key)) if self._texts.has(title_key) else document

    def clue_matrix(self) -> list[ClueRow]:
        rows: list[ClueRow] = []
        for wave in self._cfg.waves:
            title = attack_title(self._texts, wave.attack_id, wave.wave_id, revealed=True)
            wanted = [clue for clue in self._clues if clue.attack == wave.attack_id]
            for number, clue in enumerate(wanted, start=1):
                rows.append(
                    ClueRow(
                        title=title,
                        number=number,
                        document=self._document_title(clue.source),
                        section=_clue_section(self._texts, clue.source),
                        quote=clue.quote,
                        why=clue.why,
                        measures=", ".join(f"{measure_id} ({clue.weight})" for measure_id in clue.measures),
                    )
                )
        return rows


def _cell(text: str) -> str:
    return " ".join(text.split()).replace("|", "\\|")


def format_clue_matrix(rows: list[ClueRow]) -> str:
    lines = [
        "| Angriff | Nr. | Dokument | Abschnitt | Zitat | Warum | Maßnahmen (Gewicht) |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        cells = (row.title, str(row.number), row.document, row.section, row.quote, row.why, row.measures)
        lines.append("| " + " | ".join(_cell(cell) for cell in cells) + " |")
    return "\n".join(lines)


class RevealView:
    """Sicht für den Moment der Welle: enthüllte Titel, Angriffstexte und alle Blätter."""

    def __init__(self, cfg: Config, texts: Texts) -> None:
        self._cfg = cfg
        self._texts = texts

    def attack_title(self, wave: Wave) -> str:
        return attack_title(self._texts, wave.attack_id, wave.wave_id, revealed=True)

    def attack(self, attack_id: str) -> dict:
        if attack_id not in self._cfg.attacks:
            raise KeyError(f"Angriff '{attack_id}' gibt es in der Config nicht")
        base = f"attacks.{attack_id}.revealed"
        reasons = f"{base}.bonus_reasons"
        return {
            "name": self._texts.get(f"{base}.name"),
            "narrative": self._texts.get(f"{base}.narrative"),
            "cia_rationale": self._texts.get(f"{base}.cia_rationale"),
            "cases": [self._texts.get(f"{base}.{case}") for case in CASE_KEYS],
            "bonus_reasons": dict(self._texts.subtree(reasons)) if self._texts.has(reasons) else {},
        }

    def sheet(self, name: str) -> dict:
        return copy.deepcopy(self._texts.subtree(f"sheets.{name}"))
