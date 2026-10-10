"""Inhaltsquelle content/texte.toml: Laden, Abdeckung gegen die Config, Ziffern-Lint, Story-Lint.

Alle deutschen Texte für Druckmaterial stehen einmal in content/texte.toml, geordnet nach Config-ID.
Zahlen stehen nie in der Prosa: Sie kommen aus der Config und werden im Code erzeugt (D-03).
"""
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from planspiel.config import Config
from planspiel.review_text import format_eur
from planspiel.validate import Issue

CONTENT_DIR = Path(__file__).resolve().parents[1] / "content"
TEXTE_FILE = "texte.toml"
ALLOWLIST_FILE = "digit_allowlist.toml"

STORY_DOCS = ("steckbrief", "zeitungsartikel", "anfrage_mail", "audit_mail")
CASE_KEYS = ("case_1", "case_2", "case_3")

_SHEET_LABELS = (
    "measure", "level", "base_protection", "sum", "from_level", "bonus", "fulfilled", "total_bonus",
    "total_reduction", "e_value", "damage", "satisfaction", "case", "cost_type", "what", "when", "tier",
    "available_budget", "period", "init_costs", "opex", "anticipated_sum", "status_tracker",
    "point_in_time", "budget_remaining", "kz_cumulative", "damage_wave", "start", "after_wave", "events",
    "metric", "value", "total_init", "total_opex", "total_costs", "avoided_damage", "event_after_wave",
    "condition_met", "effect", "no_implementation", "final_damage", "min_level",
)

SHEET_KEYS = (
    "sheets.angriff.start_values_intro",
    "sheets.angriff.cia_table_instruction",
    "sheets.angriff.e_value_intro",
    "sheets.angriff.bonus_intro",
    "sheets.angriff.case_3_hint",
    "sheets.budget.title",
    "sheets.budget.intro",
    "sheets.budget.init_what",
    "sheets.budget.init_when",
    "sheets.budget.opex_what",
    "sheets.budget.opex_when",
    "sheets.budget.tier_intro",
    "sheets.budget.anticipated_sum_intro",
    "sheets.budget.status_tracker_intro",
    "sheets.ros.title",
    "sheets.ros.instruction",
    "sheets.ros.purpose",
    "sheets.backup_recovery.title",
    "sheets.backup_recovery.subtitle",
    "sheets.backup_recovery.narrative",
    *(f"sheets.backup_recovery.level_labels.{level}" for level in range(4)),
    *(f"sheets.labels.{name}" for name in _SHEET_LABELS),
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
class Content:
    texts: Texts
    allowlist: tuple[AllowEntry, ...]


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


def load_content(content_dir: Path = CONTENT_DIR) -> Content:
    return Content(
        texts=load_texts(content_dir / TEXTE_FILE),
        allowlist=load_allowlist(content_dir / ALLOWLIST_FILE),
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


def check_texts(cfg: Config, content: Content) -> list[Issue]:
    return [
        *check_coverage(cfg, content.texts),
        *check_digits(content.texts, content.allowlist),
        *check_story_mechanics(cfg, content.texts),
    ]
