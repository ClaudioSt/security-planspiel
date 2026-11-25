"""FLOW-04 data side of the "Was ist neu" sheet: the frozen MHP baseline and the old -> new value changes (D-14, D-26).

This is the only module that reads `content/mhp_baseline.json`. The file freezes the values the MHP facilitators printed
and played, in today's key names, numbers and ids only. Nothing in the rules, the enumeration or any other print builder
sees it: `Config` has no baseline field, and only `render.py` and `cli.py` may import this module.

The loader never chooses a path from content and never opens the printed MHP files (only the provenance test does).
Facilitator-only: the sheet is for people who ran the MHP version, never for players.

The second half of the module builds the one-page sheet (FLOW-04, D-12..D-15): rule, flow and material rows are texte
prose plus numbers generated from the config; the value rows are the grouped `value_changes`, formatted here (the diff
itself stays raw). `render.py` is the only caller that hands the baseline to a builder.
"""
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from planspiel import fmt, review_text, rules
from planspiel.config import Config
from planspiel.printmodel import PrintModelError
from planspiel.schedule import wave_label
from planspiel.texts import WAS_NEU_FLOW_IDS, WAS_NEU_MATERIAL_IDS, WAS_NEU_RULE_IDS, RevealView, Texts

BASELINE_FILE = "mhp_baseline.json"
BASELINE_GROUPS = ("budget_tiers", "base_cia", "waves", "attacks", "measures", "events", "budget_review")

SCHEMA = 1
BOUNDARIES = ("above", "inclusive")
OVERRIDE_KEYS = ("key", "value", "file", "part", "location", "printed")
SOURCE_KEYS = ("config_commit", "print_commit", "printed_overrides")

_NUM = "num"
_BOOL = "bool"
_ID = "id"
_CIA = ("obj", {"c": _NUM, "i": _NUM, "a": _NUM})
_LEVEL = ("obj", {"cia": _CIA, "init": _NUM, "opex": _NUM, "recovery": _NUM})
_PAIR_LIST = ("list", ("list", _NUM))
_SPECS: Dict[str, Any] = {
    "budget_tiers": ("map", ("obj", {"budget": _NUM, "kz_start": _NUM, "severity_multiplier": _NUM})),
    "base_cia": _CIA,
    "waves": (
        "map",
        (
            "obj",
            {
                "weights": _CIA,
                "e_threshold": _NUM,
                "bonus_measures": ("list", ("obj", {"measure": _ID, "min_level": _NUM, "bonus": _NUM})),
            },
        ),
    ),
    "attacks": (
        "map",
        (
            "obj",
            {
                "base_severity": _NUM,
                "s_unit": _NUM,
                "kz_at_full_damage": _NUM,
                "kz_at_full_mitigation": _NUM,
                "cia_impact": _CIA,
                "mitigation_cap": _NUM,
                "allow_recovery": _BOOL,
            },
        ),
    ),
    "measures": ("map", ("obj", {"levels": ("map", _LEVEL)})),
    "events": (
        "map",
        (
            "obj",
            {
                "opex_per_measure": _NUM,
                "budget_delta": _NUM,
                "measures": ("list", _ID),
                "measure": _ID,
                "min_level": _NUM,
                "level": _NUM,
                "kz_per_measure": _NUM,
                "kz_delta": _NUM,
                "tiers": ("any", _PAIR_LIST, ("map", _NUM)),
                "clauses": ("list", ("obj", {"measure": _ID, "min_level": _NUM, "level_eq": _NUM})),
            },
        ),
    ),
    "budget_review": (
        "obj",
        {
            "boundary": ("enum", BOUNDARIES),
            "tiers": _PAIR_LIST,
            "overspend": ("obj", {"flat_kz": _NUM, "kz_per_step": _NUM, "step": _NUM}),
        },
    ),
}


@dataclass(frozen=True)
class PrintedOverride:
    """One place where the printed MHP material overrules the config at the MHP commit (D-26)."""

    key: str
    value: Any
    file: str
    part: str
    location: str
    printed: Tuple[str, ...]


@dataclass(frozen=True)
class BaselineSource:
    config_commit: str
    print_commit: str
    printed_overrides: Tuple[PrintedOverride, ...]


@dataclass(frozen=True)
class Baseline:
    """The MHP state in current key names; group dicts hold int/Fraction/bool numbers and id strings only."""

    schema: int
    source: BaselineSource
    budget_tiers: Dict[str, Dict[str, Any]]
    base_cia: Dict[str, Any]
    waves: Dict[str, Dict[str, Any]]
    attacks: Dict[str, Dict[str, Any]]
    measures: Dict[str, Dict[str, Any]]
    events: Dict[str, Dict[str, Any]]
    budget_review: Dict[str, Any]


class _Invalid(Exception):
    """Internal: carries the message up to `load_baseline`, which prefixes the file path."""


def _where(path: Tuple[str, ...]) -> str:
    return ".".join(path) if path else "(Datei)"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, Fraction)) and not isinstance(value, bool)


def _normalise(value: Any) -> Any:
    if isinstance(value, Fraction) and value.denominator == 1:
        return int(value)
    if isinstance(value, dict):
        return {key: _normalise(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_normalise(child) for child in value]
    return value


def _check(value: Any, spec: Any, path: Tuple[str, ...]) -> None:
    kind = spec if isinstance(spec, str) else spec[0]
    if kind == _NUM:
        if not _is_number(value):
            raise _Invalid(f"{_where(path)}: Zahl erwartet, gefunden {value!r}")
    elif kind == _BOOL:
        if not isinstance(value, bool):
            raise _Invalid(f"{_where(path)}: Wahrheitswert erwartet, gefunden {value!r}")
    elif kind == _ID:
        if not isinstance(value, str):
            raise _Invalid(f"{_where(path)}: Kennung (Text) erwartet, gefunden {value!r}")
    elif kind == "enum":
        if value not in spec[1]:
            raise _Invalid(f"{_where(path)}: erlaubt sind {', '.join(spec[1])}, gefunden {value!r}")
    elif kind == "list":
        if not isinstance(value, list):
            raise _Invalid(f"{_where(path)}: Liste erwartet")
        for index, child in enumerate(value):
            _check(child, spec[1], path + (str(index),))
    elif kind == "map":
        if not isinstance(value, dict):
            raise _Invalid(f"{_where(path)}: Objekt erwartet")
        for key, child in value.items():
            _check(child, spec[1], path + (key,))
    elif kind == "obj":
        if not isinstance(value, dict):
            raise _Invalid(f"{_where(path)}: Objekt erwartet")
        for key, child in value.items():
            if key not in spec[1]:
                raise _Invalid(f"{_where(path)}: unbekannter Schlüssel '{key}'")
            _check(child, spec[1][key], path + (key,))
    elif kind == "any":
        errors = []
        for alternative in spec[1:]:
            try:
                _check(value, alternative, path)
                return
            except _Invalid as exc:
                errors.append(str(exc))
        raise _Invalid(errors[0])
    else:  # pragma: no cover - the spec table above is fixed
        raise AssertionError(kind)


def _source(raw: Any) -> BaselineSource:
    path = ("source",)
    if not isinstance(raw, dict):
        raise _Invalid("source: Objekt erwartet")
    for key in raw:
        if key not in SOURCE_KEYS:
            raise _Invalid(f"source: unbekannter Schlüssel '{key}'")
    for key in SOURCE_KEYS:
        if key not in raw:
            raise _Invalid(f"source: Schlüssel '{key}' fehlt")
    for key in ("config_commit", "print_commit"):
        if not isinstance(raw[key], str) or not raw[key]:
            raise _Invalid(f"source.{key}: Commit-Kennung (Text) erwartet")
    records = raw["printed_overrides"]
    if not isinstance(records, list):
        raise _Invalid("source.printed_overrides: Liste erwartet")
    overrides = []
    for index, record in enumerate(records):
        where = f"source.printed_overrides.{index}"
        if not isinstance(record, dict):
            raise _Invalid(f"{where}: Objekt erwartet")
        for key in record:
            if key not in OVERRIDE_KEYS:
                raise _Invalid(f"{where}: unbekannter Schlüssel '{key}'")
        for key in OVERRIDE_KEYS:
            if key not in record:
                raise _Invalid(f"{where}: Schlüssel '{key}' fehlt")
        for key in ("key", "file", "part", "location"):
            if not isinstance(record[key], str) or not record[key]:
                raise _Invalid(f"{where}.{key}: Text erwartet")
        if "/" in record["file"] or "\\" in record["file"]:
            raise _Invalid(f"{where}.file: nur ein Dateiname ohne Verzeichnis erlaubt, gefunden {record['file']!r}")
        printed = record["printed"]
        if (
            not isinstance(printed, list)
            or not printed
            or not all(isinstance(item, str) and item for item in printed)
        ):
            raise _Invalid(f"{where}.printed: nicht leere Liste von Texten erwartet")
        overrides.append(
            PrintedOverride(
                key=record["key"],
                value=record["value"],
                file=record["file"],
                part=record["part"],
                location=record["location"],
                printed=tuple(printed),
            )
        )
    return BaselineSource(raw["config_commit"], raw["print_commit"], tuple(overrides))


def _parse(raw: Any) -> Baseline:
    if not isinstance(raw, dict):
        raise _Invalid("Objekt erwartet")
    known = {"schema", "source", *BASELINE_GROUPS}
    for key in raw:
        if key not in known:
            raise _Invalid(f"unbekannter Schlüssel '{key}'")
    if raw.get("schema") != SCHEMA or isinstance(raw.get("schema"), bool):
        raise _Invalid(f"schema: {SCHEMA} erwartet, gefunden {raw.get('schema')!r}")
    if "source" not in raw:
        raise _Invalid("Schlüssel 'source' fehlt")
    source = _source(raw["source"])
    groups = {}
    for group in BASELINE_GROUPS:
        if group not in raw:
            raise _Invalid(f"Schlüssel '{group}' fehlt")
        _check(raw[group], _SPECS[group], (group,))
        groups[group] = _normalise(raw[group])
    return Baseline(schema=SCHEMA, source=source, **groups)


def load_baseline(path: Path) -> Optional[Baseline]:
    """The frozen MHP baseline, or None when the file does not exist; a malformed file raises ValueError."""
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"), parse_float=Fraction)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path.name}: kein gültiges JSON ({exc})") from exc
    try:
        return _parse(raw)
    except _Invalid as exc:
        raise ValueError(f"{path.name}: {exc}") from exc


# --- old -> new value changes ---------------------------------------------------------------------------------------

INCLUSIVE = "inclusive"  # RULE-07: a Budget Review tier starts at its printed amount (the MHP print read "above")
_EVENT_MEANING_CHANGES = {("exzellenz_bonus", "level")}  # the rule counts measures at or above the level now


@dataclass(frozen=True)
class ValueChange:
    """One parameter whose MHP value differs from today's config; old/new are raw comparable values (no formatting).

    `old` is None when the baseline does not hold the value, `new` is None when the config no longer has it.
    `meaning_changed` marks changes of what the rule means, so the sheet must say so instead of only showing numbers.
    """

    group: str
    subject: Tuple[Any, ...]
    field: str
    old: Any
    new: Any
    meaning_changed: bool = False


def _plain(value: Any) -> Any:
    """A comparable plain value: Fractions with denominator 1 become ints, dicts and lists become sorted tuples."""
    if isinstance(value, Fraction):
        return int(value) if value.denominator == 1 else value
    if isinstance(value, dict):
        if value and all(isinstance(key, str) and key.lstrip("-").isdigit() for key in value):
            items = sorted(((int(key), child) for key, child in value.items()), key=lambda item: item[0])
        else:
            items = sorted(value.items(), key=lambda item: str(item[0]))
        return tuple((key, _plain(child)) for key, child in items)
    if isinstance(value, (list, tuple)):
        return tuple(_plain(child) for child in value)
    return value


def _cia(values: Optional[Dict[str, Any]]) -> Optional[Tuple[Any, ...]]:
    return None if values is None else tuple(_plain(values[key]) for key in "cia")


def _emit(
    out: List[ValueChange], group: str, subject: Tuple[Any, ...], field: str, old: Any, new: Any, meaning: bool = False
) -> None:
    old, new = _plain(old), _plain(new)
    if old != new:
        out.append(ValueChange(group, subject, field, old, new, meaning))


def _known(baseline_ids: Iterable[str], config_ids: Iterable[str], kind: str) -> None:
    known = set(config_ids)
    unknown = [item for item in baseline_ids if item not in known]
    if unknown:
        raise PrintModelError(f"Die MHP-Basisdatei nennt {kind} '{unknown[0]}', die die Konfiguration nicht kennt")


def _budget_changes(cfg: Config, baseline: Baseline) -> List[ValueChange]:
    _known(baseline.budget_tiers, cfg.budget_tiers, "die Budgetstufe")
    out: List[ValueChange] = []
    for name, tier in cfg.budget_tiers.items():
        old = baseline.budget_tiers.get(name, {})
        for field in ("budget", "kz_start", "severity_multiplier"):
            _emit(out, "budget_tiers", (name,), field, old.get(field), getattr(tier, field))
    return out


def _base_cia_changes(cfg: Config, baseline: Baseline) -> List[ValueChange]:
    out: List[ValueChange] = []
    _emit(out, "base_cia", (), "cia", _cia(baseline.base_cia), _cia(cfg.base_cia))
    return out


def _wave_changes(cfg: Config, baseline: Baseline) -> List[ValueChange]:
    _known(baseline.waves, [str(wave.wave_id) for wave in cfg.waves], "die Welle")
    out: List[ValueChange] = []
    for wave in cfg.waves:
        old = baseline.waves.get(str(wave.wave_id), {})
        wave_id = wave.wave_id
        _emit(out, "waves", (wave_id,), "e_threshold", old.get("e_threshold"), wave.e_threshold)
        _emit(out, "waves", (wave_id,), "weights", _cia(old.get("weights")), _cia(wave.weights))
        old_bonus = {entry["measure"]: entry for entry in old.get("bonus_measures", [])}
        new_bonus = {entry.measure: entry for entry in wave.bonus_measures}
        for measure in [*new_bonus, *(m for m in old_bonus if m not in new_bonus)]:
            before, after = old_bonus.get(measure), new_bonus.get(measure)
            for field in ("bonus", "min_level"):
                _emit(
                    out, "waves", (wave_id, measure), field,
                    None if before is None else before[field],
                    None if after is None else getattr(after, field),
                )
    return out


def _attack_changes(cfg: Config, baseline: Baseline) -> List[ValueChange]:
    _known(baseline.attacks, cfg.attacks, "den Angriff")
    out: List[ValueChange] = []
    for attack_id, attack in cfg.attacks.items():
        old = baseline.attacks.get(attack_id, {})
        for field in (
            "base_severity", "s_unit", "kz_at_full_damage", "kz_at_full_mitigation", "mitigation_cap", "allow_recovery",
        ):
            _emit(out, "attacks", (attack_id,), field, old.get(field), getattr(attack, field))
        _emit(out, "attacks", (attack_id,), "cia_impact", _cia(old.get("cia_impact")), _cia(attack.cia_impact))
    return out


def _measure_changes(cfg: Config, baseline: Baseline) -> List[ValueChange]:
    _known(baseline.measures, cfg.measures, "die Maßnahme")
    out: List[ValueChange] = []
    for measure_id, measure in cfg.measures.items():
        old_levels = baseline.measures.get(measure_id, {}).get("levels", {})
        _known(old_levels, [str(level) for level in measure.levels], f"das Level von {measure_id}")
        for level, info in measure.levels.items():
            if level == 0:
                continue
            old = old_levels.get(str(level), {})
            subject = (measure_id, level)
            _emit(out, "measures", subject, "cia", _cia(old.get("cia")), _cia(info.cia))
            _emit(out, "measures", subject, "init", old.get("init"), info.init)
            _emit(out, "measures", subject, "opex", old.get("opex"), info.opex)
            _emit(out, "measures", subject, "recovery", old.get("recovery"), info.recovery)
    return out


def _event_changes(cfg: Config, baseline: Baseline) -> List[ValueChange]:
    events = [event for wave_events in cfg.events.values() for event in wave_events]
    _known(baseline.events, [event.id for event in events], "das Ereignis")
    out: List[ValueChange] = []
    for event in events:
        old = baseline.events.get(event.id, {})
        for field in [*event.params, *(key for key in old if key not in event.params)]:
            _emit(
                out, "events", (event.id,), field, old.get(field), event.params.get(field),
                meaning=(event.id, field) in _EVENT_MEANING_CHANGES,
            )
    return out


def _overspend(spec: Dict[str, Any]) -> Optional[Tuple[Any, ...]]:
    if "flat_kz" in spec:
        return ("flat", spec["flat_kz"])
    if "kz_per_step" in spec and "step" in spec:
        return ("per_step", spec["kz_per_step"], spec["step"])
    return None


def _review_event(cfg: Config):
    event = next((e for e in cfg.final_events if e.type == "final_budget_tier"), None)
    if event is None:
        raise PrintModelError("Die Konfiguration hat kein Budget-Review-Ereignis")
    return event


def _review_changes(cfg: Config, baseline: Baseline) -> List[ValueChange]:
    event = _review_event(cfg)
    old = baseline.budget_review
    out: List[ValueChange] = []
    _emit(out, "budget_review", (), "tiers", old.get("tiers"), event.params["tiers"])
    boundary = old.get("boundary")
    _emit(out, "budget_review", (), "boundary", boundary, INCLUSIVE, meaning=boundary != INCLUSIVE)
    before = _overspend(old.get("overspend", {}))
    after = ("per_step", *rules.penalty_params(cfg.final_events))
    _emit(
        out, "budget_review", (), "overspend", before, after,
        meaning=before is None or before[0] != after[0],
    )
    return out


def value_changes(cfg: Config, baseline: Baseline) -> Tuple[ValueChange, ...]:
    """Every rebalance-able parameter whose MHP value differs from the config, in group order (D-13 values part)."""
    extractors = {
        "budget_tiers": _budget_changes,
        "base_cia": _base_cia_changes,
        "waves": _wave_changes,
        "attacks": _attack_changes,
        "measures": _measure_changes,
        "events": _event_changes,
        "budget_review": _review_changes,
    }
    changes: List[ValueChange] = []
    for group in BASELINE_GROUPS:
        changes.extend(extractors[group](cfg, baseline))
    return tuple(changes)


# --- the one-page sheet ---------------------------------------------------------------------------------------------

WAS_NEU_JOB = "spielleitung-was-ist-neu"
SHEET = "was_neu"
RULE_IDS = WAS_NEU_RULE_IDS
FLOW_IDS = WAS_NEU_FLOW_IDS
MATERIAL_IDS = WAS_NEU_MATERIAL_IDS
VALUE_GROUP_ORDER = BASELINE_GROUPS  # display order of the value rows
# D-15: the value table shrinks first. Calibrated against the worst-case page proof in tests/test_was_neu_pdf.py.
MAX_VALUE_ROWS = 19
# Rows kept longest when the table is capped: budgets, KZ start and thresholds (meaning-changed rows always rank first).
_FIRST_TIER_FIELDS = ("budget", "kz_start")
_KZ_END_FIELDS = ("kz_at_full_damage", "kz_at_full_mitigation")
_CIA_FIELDS = ("cia", "weights", "cia_impact", "base_cia")
_SIGNED_FIELDS = (*_KZ_END_FIELDS, "kz_delta", "kz_per_measure")
_MONEY_FIELDS = ("budget", "init", "opex")
_SIGNED_MONEY_FIELDS = ("budget_delta", "opex_per_measure")
SEPARATOR = " / "
CIA_SEPARATOR = " · "


@dataclass(frozen=True)
class RuleRow:
    heading: str
    text: str


@dataclass(frozen=True)
class ValueRow:
    """One printed row of the value table; `flag` is the mark of a changed meaning ("" when only the number changed)."""

    label: str
    old: str
    new: str
    flag: str


@dataclass(frozen=True)
class WasNeuSheet:
    job: str
    title: str
    notice: str
    intro: str
    rules_title: str
    rules: Tuple[RuleRow, ...]
    flow_title: str
    flow: Tuple[str, ...]
    material_title: str
    material: Tuple[str, ...]
    values_title: str
    values_header: Tuple[str, str, str]
    values: Tuple[ValueRow, ...]
    values_more: str
    flag_note: str

    def printed_fragments(self) -> Tuple[str, ...]:
        """Every string of the sheet that ends up on the paper, without duplicates and without empty strings."""
        found: List[str] = [self.title, self.notice, self.intro, self.rules_title, self.flow_title, self.material_title]
        for rule in self.rules:
            found += [rule.heading, rule.text]
        found += [*self.flow, *self.material, self.values_title, *self.values_header]
        for row in self.values:
            found += [row.label, row.old, row.new, row.flag]
        found += [self.values_more, self.flag_note]
        return tuple(dict.fromkeys(text for text in found if text))


def _number(value: Any) -> str:
    return fmt.format_number(value)


def _triple(values: Any) -> str:
    return "/".join(_number(value) for value in values)


def _overspend_text(spec: Optional[Tuple[Any, ...]], parts: Dict[str, str]) -> str:
    if spec is None:
        return parts["removed"]
    if spec[0] == "flat":
        return f"{fmt.format_signed(spec[1])} {parts['kz']} {parts['flat']}"
    return f"{fmt.format_signed(-spec[1])} {parts['kz']} {parts['per_started']} {fmt.format_money(spec[2] * 1000)}"


def _generic(value: Any, parts: Dict[str, str]) -> str:
    if isinstance(value, bool):
        return parts["yes"] if value else parts["no"]
    if isinstance(value, (int, Fraction, float)):
        return _number(value)
    if isinstance(value, tuple):
        return SEPARATOR.join(_generic(item, parts) for item in value)
    return str(value)


def _value_text(field: str, value: Any, parts: Dict[str, str]) -> str:
    """One old or new value as the sheet prints it (a missing value is handled by the caller)."""
    if field in _MONEY_FIELDS:
        return fmt.format_money(value * 1000)
    if field in _SIGNED_MONEY_FIELDS:
        return f"{fmt.format_signed(value * 1000)} €"
    if field in _SIGNED_FIELDS:
        return fmt.format_signed(value)
    if field == "recovery":
        return fmt.format_percent(value)
    if field in _CIA_FIELDS:
        return _triple(value)
    if field == "allow_recovery":
        return parts["yes"] if value else parts["no"]
    if field == "level":
        return f"{parts['from_level']} {_number(value)}"
    if field == "tiers":
        return SEPARATOR.join(fmt.format_signed(delta) for _, delta in value)
    if field == "boundary":
        return parts["boundary_inclusive"] if value == INCLUSIVE else parts["boundary_above"]
    if field == "overspend":
        return _overspend_text(value, parts)
    return _generic(value, parts)


def _tiers_text(old: Any, new: Any, parts: Dict[str, str]) -> Tuple[str, str]:
    """Budget Review tiers as KZ values; with moved lower bounds each value carries its bound."""
    if [minimum for minimum, _ in old] == [minimum for minimum, _ in new]:
        return tuple(SEPARATOR.join(fmt.format_signed(kz) for _, kz in tiers) for tiers in (old, new))
    return tuple(
        SEPARATOR.join(
            f"{parts['tier_from']} {fmt.format_money(minimum * 1000)}: {fmt.format_signed(kz)}" for minimum, kz in tiers
        )
        for tiers in (old, new)
    )


class _Builder:
    """Turns grouped `ValueChange`s into printed rows; unchanged members of a grouped row are read from the config."""

    def __init__(self, cfg: Config, words: Dict[str, Any]) -> None:
        self.cfg = cfg
        self.parts = words["parts"]
        self.fields = words["fields"]
        self.wave_word = words["wave_label"]
        self.attack_wave = {wave.attack_id: wave.wave_id for wave in cfg.waves}

    def key(self, change: ValueChange) -> Tuple[Any, ...]:
        group, subject, field = change.group, change.subject, change.field
        if group == "budget_tiers":
            return (group, field)
        if group == "base_cia":
            return (group,)
        if group == "waves":
            return (group, subject[0], field)
        if group == "attacks":
            return (group, self.attack_wave[subject[0]], "kz_ends" if field in _KZ_END_FIELDS else field)
        if group == "measures":
            return (group, subject[0], field)
        if group == "events":
            return (group, subject[0])
        return (group, field)

    def priority(self, key: Tuple[Any, ...]) -> bool:
        return (key[0] == "budget_tiers" and key[1] in _FIRST_TIER_FIELDS) or (
            key[0] == "waves" and key[2] == "e_threshold"
        )

    def _pair(self, field: str, old: Any, new: Any) -> Tuple[str, str]:
        return (
            self.parts["added"] if old is None else _value_text(field, old, self.parts),
            self.parts["removed"] if new is None else _value_text(field, new, self.parts),
        )

    def _joined(self, field: str, pairs: List[Tuple[Any, Any]], separator: str = SEPARATOR) -> Tuple[str, str]:
        texts = [self._pair(field, old, new) for old, new in pairs]
        return separator.join(old for old, _ in texts), separator.join(new for _, new in texts)

    def _wave_label(self, wave: int) -> str:
        return f"{self.wave_word} {_number(wave)}"

    def row(self, key: Tuple[Any, ...], members: List[ValueChange]) -> Tuple[str, str, str]:
        return getattr(self, f"_{key[0]}")(key, members)

    def _budget_tiers(self, key, members):
        field = key[1]
        by_tier = {change.subject[0]: change for change in members}
        pairs = []
        for name, tier in self.cfg.budget_tiers.items():
            change = by_tier.get(name)
            pairs.append((change.old, change.new) if change else (getattr(tier, field),) * 2)
        names = SEPARATOR.join(name.capitalize() for name in self.cfg.budget_tiers)
        return (f"{self.fields[field]} ({names})", *self._joined(field, pairs))

    def _base_cia(self, key, members):
        return (self.fields["base_cia"], *self._pair("base_cia", members[0].old, members[0].new))

    def _waves(self, key, members):
        _, wave_id, field = key
        label = f"{self.fields[field]}, {self._wave_label(wave_id)}"
        if len(members[0].subject) == 1:
            return (label, *self._pair(field, members[0].old, members[0].new))
        wave = next(wave for wave in self.cfg.waves if wave.wave_id == wave_id)
        current = {bonus.measure: getattr(bonus, field) for bonus in wave.bonus_measures}
        by_measure = {change.subject[1]: change for change in members}
        measures = [*current, *(measure for measure in by_measure if measure not in current)]
        pairs = [
            (by_measure[m].old, by_measure[m].new) if m in by_measure else (current[m], current[m]) for m in measures
        ]
        return (f"{label} ({SEPARATOR.join(measures)})", *self._joined(field, pairs))

    def _attacks(self, key, members):
        _, wave_id, field = key
        label = f"{self.fields[field]}, {self._wave_label(wave_id)}"
        if field != "kz_ends":
            return (label, *self._pair(field, members[0].old, members[0].new))
        attack = self.cfg.attacks[members[0].subject[0]]
        by_field = {change.field: change for change in members}
        pairs = [
            (by_field[name].old, by_field[name].new) if name in by_field else (getattr(attack, name),) * 2
            for name in _KZ_END_FIELDS
        ]
        return (label, *self._joined("kz_delta", pairs))

    def _measures(self, key, members):
        _, measure_id, field = key
        measure = self.cfg.measures[measure_id]
        by_level = {change.subject[1]: change for change in members}
        levels = sorted(level for level in measure.levels if level > 0)
        pairs = []
        for level in levels:
            if level in by_level:
                pairs.append((by_level[level].old, by_level[level].new))
            else:
                info = measure.levels[level]
                value = _plain(_cia(info.cia) if field == "cia" else getattr(info, field))
                pairs.append((value, value))
        shown = SEPARATOR.join(_number(level) for level in levels)
        label = f"{measure_id} {measure.name}, {self.fields[field]} ({self.parts['level']} {shown})"
        return (label, *self._joined(field, pairs, CIA_SEPARATOR if field == "cia" else SEPARATOR))

    def _events(self, key, members):
        event = next(e for events in self.cfg.events.values() for e in events if e.id == key[1])
        label = f"{event.name}, {SEPARATOR.join(self.fields[change.field] for change in members)}"
        pairs = [self._pair(change.field, change.old, change.new) for change in members]
        return label, SEPARATOR.join(old for old, _ in pairs), SEPARATOR.join(new for _, new in pairs)

    def _budget_review(self, key, members):
        field, change = key[1], members[0]
        label = f"{_review_event(self.cfg).name}, {self.fields['review_tiers' if field == 'tiers' else field]}"
        if field == "tiers":
            return (label, *_tiers_text(change.old, change.new, self.parts))
        return (label, *self._pair(field, change.old, change.new))


def _value_rows(
    cfg: Config, changes: Tuple[ValueChange, ...], words: Dict[str, Any]
) -> Tuple[Tuple[ValueRow, ...], bool]:
    """The grouped value rows in display order, capped at `MAX_VALUE_ROWS` by priority (D-15); True if rows were cut."""
    builder = _Builder(cfg, words)
    groups: Dict[Tuple[Any, ...], List[ValueChange]] = {}
    for change in changes:
        groups.setdefault(builder.key(change), []).append(change)
    ranked = []
    for index, (key, members) in enumerate(groups.items()):
        meaning = any(change.meaning_changed for change in members)
        label, old, new = builder.row(key, members)
        row = ValueRow(label, old, new, words["flag_mark"] if meaning else "")
        order = (VALUE_GROUP_ORDER.index(members[0].group), index)
        ranked.append((0 if meaning or builder.priority(key) else 1, order, row))
    by_priority = sorted(ranked, key=lambda item: (item[0], item[1]))[:MAX_VALUE_ROWS]
    kept = sorted(by_priority, key=lambda item: item[1])
    return tuple(row for _, _, row in kept), len(ranked) > MAX_VALUE_ROWS


def _rule_suffix(rule_id: str, cfg: Config, parts: Dict[str, str]) -> str:
    """The numbers of a rule row, generated from the config (D-13)."""
    if rule_id == "overspend":
        kz_per_step, step_k = rules.penalty_params(cfg.final_events)
        # The rule text says "kostet", so the amount stands without a sign (no double negative).
        return (
            f" {_number(kz_per_step)} {parts['kz']} {parts['per_started']} {fmt.format_money(step_k * 1000)} "
            f"{parts['over_budget']}."
        )
    if rule_id == "review_boundary":
        return f" {review_text.boundary_text(_review_event(cfg).params['tiers'])}"
    if rule_id == "final_index":
        weights = cfg.final_index
        kz, ros = _number(weights.weight_kz), _number(weights.weight_ros)
        return f" {kz} {fmt.TIMES} {parts['kz']} + {ros} {fmt.TIMES} {parts['ros']}."
    return ""


def build_was_neu_sheet(cfg: Config, texts: Texts, baseline: Optional[Baseline]) -> Optional[WasNeuSheet]:
    """The "Was ist neu" sheet; None without a `session_schedule` (mini config) or without a baseline file (D-14)."""
    schedule = cfg.session_schedule
    if schedule is None or baseline is None:
        return None
    view = RevealView(cfg, texts)
    words, ablauf, debrief = view.sheet(SHEET), view.sheet("ablauf"), view.sheet("debrief")
    parts = words["parts"]
    unit = debrief["minutes_unit"]

    rule_rows = tuple(
        RuleRow(
            heading=words["rules"][rule_id]["heading"],
            text=words["rules"][rule_id]["text"] + _rule_suffix(rule_id, cfg, parts),
        )
        for rule_id in RULE_IDS
    )

    practice = next((block for block in schedule.blocks if block.wave == 0), None)
    debrief_block = next((block for block in schedule.blocks if block.id == "debrief"), None)
    if practice is None or debrief_block is None:
        raise PrintModelError("Der Ablaufplan braucht einen Block für die Übungswelle (Welle 0) und einen Block 'debrief'")
    # The minutes stand per wave in wave order, built from the schedule; a sorted set would put the shorter waves first.
    wave_minutes = ", ".join(
        f"{wave_label(ablauf, block.wave)}: {_number(block.minutes)}" for block in schedule.blocks if block.wave
    )
    flow = words["flow"]
    flow_rows = (
        flow["whiteboard"],
        f"{wave_label(ablauf, practice.wave)}: {flow['welle0']}",
        f"{flow['debrief']} {debrief['title']} ({_number(debrief_block.minutes)} {unit}).",
        f"{flow['schedule']} {ablauf['title']} "
        f"({_number(schedule.total_minutes)} {unit} {parts['total']}; {wave_minutes} {unit}).",
    )

    material = words["material"]
    material_rows = (
        material["generated"],
        material["veil"],
        f"{material['clues']} {view.sheet('spielleitung')['clues_title']}.",
        material["teamheft"],
        f"{material['wave_page']} {view.sheet('welle')['title']}.",
        material["practice"],
    )

    values, left_out = _value_rows(cfg, value_changes(cfg, baseline), words)
    return WasNeuSheet(
        job=WAS_NEU_JOB,
        title=words["title"],
        notice=words["notice"],
        intro=words["intro"],
        rules_title=words["rules_title"],
        rules=rule_rows,
        flow_title=words["flow_title"],
        flow=flow_rows,
        material_title=words["material_title"],
        material=material_rows,
        values_title=words["values_title"],
        values_header=(words["values_head_item"], words["values_head_old"], words["values_head_new"]),
        values=values,
        values_more=words["values_more"] if left_out else "",
        flag_note=words["flag_note"] if any(row.flag for row in values) else "",
    )
