"""FLOW-04 data side of the "Was ist neu" sheet: the frozen MHP baseline and the old -> new value changes (D-14, D-26).

This is the only module that reads `content/mhp_baseline.json`. The file freezes the values the MHP facilitators printed
and played, in today's key names, numbers and ids only. Nothing in the rules, the enumeration or any other print builder
sees it: `Config` has no baseline field, and only `render.py` and `cli.py` may import this module.

The loader never chooses a path from content and never opens the printed MHP files (only the provenance test does).
Facilitator-only: the sheet is for people who ran the MHP version, never for players.
"""
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from planspiel import rules
from planspiel.config import Config
from planspiel.printmodel import PrintModelError

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


def _review_changes(cfg: Config, baseline: Baseline) -> List[ValueChange]:
    event = next((e for e in cfg.final_events if e.type == "final_budget_tier"), None)
    if event is None:
        raise PrintModelError("Die Konfiguration hat kein Budget-Review-Ereignis")
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
