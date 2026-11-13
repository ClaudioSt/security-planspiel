import math
import re
from dataclasses import dataclass
from fractions import Fraction
from math import lcm
from typing import Any, Dict, List, Optional, Tuple

from planspiel.config import RiskBand
from planspiel.risk import band_of
from planspiel.rules import kz_slope

KNOWN_EVENT_TYPES = (
    "kurswechsel",
    "flat_budget",
    "opex_discount_per_active_measure",
    "checklist_tier",
    "measure_level_tier",
    "level_bonus_per_measure",
    "and_condition",
    "final_budget_tier",
)

REQUIRED_EVENT_PARAMS = {
    "kurswechsel": (),
    "flat_budget": ("budget_delta",),
    "opex_discount_per_active_measure": ("opex_per_measure",),
    "checklist_tier": ("measures", "min_level", "tiers"),
    "measure_level_tier": ("measure", "tiers"),
    "level_bonus_per_measure": ("level", "kz_per_measure"),
    "and_condition": ("clauses", "kz_delta"),
    "final_budget_tier": ("tiers", "overspend_penalty"),
}

SCHEDULE_KEYS = ("total_minutes", "teams", "persons_per_team", "blocks", "print_list", "debrief_stages")
DEBRIEF_STAGE_KEYS = ("id", "minutes")
SCHEDULE_BLOCK_KEYS = ("id", "minutes", "wave")
PRINT_ROW_KEYS = ("job", "per_team", "facilitator")
RISK_MATRIX_KEYS = ("register_rows", "bands", "cases")
RISK_CASE_KEYS = ("id", "band", "like_attack")
RISK_BAND_KEYS = ("id", "min")
RISK_BAND_COUNT = 3  # the matrix is 3 x 3 (D-03)
SNAKE_ID = re.compile(r"[a-z][a-z0-9_]*")
PRINT_JOB = re.compile(r"[a-z0-9][a-z0-9_-]*")

PRACTICE_KEYS = ("kz_start", "budget", "attack", "wave", "event", "selection")
PRACTICE_EVENT_TYPES = ("checklist_tier", "measure_level_tier", "level_bonus_per_measure", "and_condition")

CIA_KEYS = {"c", "i", "a"}
LEVEL_KEYS = {"0", "1", "2", "3"}
WAVE_KEY = re.compile(r"wave_(\d+)")


@dataclass(frozen=True)
class Issue:
    level: str
    code: str
    path: str
    message: str


class HandCalcWarning(UserWarning):
    """A `hand_calc.*` finding loaded at level "warning" (reports that judge hand-calculability themselves)."""


class ConfigWarning(UserWarning):
    """Every other warning-level finding (schema defaults, removed keys, rule hints); never suppressed by reports."""


class ConfigError(ValueError):
    def __init__(self, issues: List[Issue], source: str = ""):
        self.issues = list(issues)
        self.source = source
        super().__init__(str(self))

    def __str__(self) -> str:
        header = f"Ungültige Konfiguration {self.source}".rstrip()
        lines = [f"ERROR {issue.code} {issue.path}: {issue.message}" for issue in self.issues]
        return "\n".join([header, *lines])


def _fraction(value: Any) -> Optional[Fraction]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(repr(value)) if math.isfinite(value) else None
    if isinstance(value, Fraction):
        return value
    return None


def _one_decimal(value: Fraction) -> bool:
    return (value * 10).denominator == 1


def _dicts(value: Any) -> List[dict]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def scale_factors(raw: dict) -> Tuple[int, int]:
    """(WS, RS): lcm of the denominators of all wave weights and of all measure-level recoveries."""
    weight_scale = 1
    for wave in _dicts(raw.get("waves")):
        weights = wave.get("weights")
        for value in weights.values() if isinstance(weights, dict) else []:
            fraction = _fraction(value)
            if fraction is not None:
                weight_scale = lcm(weight_scale, fraction.denominator)
    recovery_scale = 1
    measures = raw.get("measures")
    for measure in measures.values() if isinstance(measures, dict) else []:
        levels = measure.get("levels") if isinstance(measure, dict) else None
        for level in levels.values() if isinstance(levels, dict) else []:
            fraction = _fraction(level.get("recovery", 0)) if isinstance(level, dict) else None
            if fraction is not None:
                recovery_scale = lcm(recovery_scale, fraction.denominator)
    return weight_scale, recovery_scale


HAND_CALC_LEVELS = ("warning", "error")
REFERENCE_STRATEGY_KINDS = ("good", "mediocre", "bad")


class _Validator:
    def __init__(self, raw: dict, hand_calc_level: str = "error"):
        if hand_calc_level not in HAND_CALC_LEVELS:
            raise ValueError(f"hand_calc_level muss warning oder error sein, nicht {hand_calc_level!r}")
        self.raw = raw
        self.hand_calc_level = hand_calc_level
        self.issues: List[Issue] = []
        self.wave_ids: List[int] = []
        self.event_ids: Dict[str, str] = {}

    def error(self, code: str, path: str, message: str) -> None:
        self.issues.append(Issue("error", code, path, message))

    def warning(self, code: str, path: str, message: str) -> None:
        self.issues.append(Issue("warning", code, path, message))

    def _hand_calc(self, code: str, path: str, message: str) -> None:
        self.issues.append(Issue(self.hand_calc_level, code, path, message))

    def removed_key(self, key: str, path: str) -> None:
        self.warning(
            "schema.removed_key",
            path,
            f"Schlüssel '{key}' wird nicht mehr verwendet (E-Ziel-Bonus/Malus entfernt) und ignoriert",
        )

    def prose_key(self, key: str, path: str) -> None:
        self.error(
            "schema.prose_in_config",
            path,
            f"Prosa gehört nach content/texte.toml; Schlüssel '{key}' entfernen",
        )

    def int_value(self, value: Any, path: str, lo: Optional[int] = None, hi: Optional[int] = None) -> Optional[int]:
        if isinstance(value, bool) or not isinstance(value, int):
            self.error("schema.type", path, f"Ganzzahl erwartet, gefunden {value!r}")
            return None
        if (lo is not None and value < lo) or (hi is not None and value > hi):
            bounds = f"{lo if lo is not None else '-inf'}..{hi if hi is not None else 'inf'}"
            self.error("schema.range", path, f"Wert {value} außerhalb des erlaubten Bereichs {bounds}")
            return None
        return value

    def number_value(self, value: Any, path: str, lo: Optional[int] = None, hi: Optional[int] = None) -> Optional[Fraction]:
        fraction = _fraction(value)
        if fraction is None:
            self.error("schema.type", path, f"endliche Zahl erwartet, gefunden {value!r}")
            return None
        if (lo is not None and fraction < lo) or (hi is not None and fraction > hi):
            self.error("schema.range", path, f"Wert {value} außerhalb des erlaubten Bereichs {lo}..{hi}")
            return None
        return fraction

    def text_value(self, value: Any, path: str) -> Optional[str]:
        if not isinstance(value, str):
            self.error("schema.type", path, f"Text erwartet, gefunden {value!r}")
            return None
        return value

    def field(self, obj: dict, key: str, path: str) -> Any:
        if key not in obj:
            self.error("schema.keys", f"{path}.{key}", f"Pflichtfeld '{key}' fehlt")
            return None
        return obj[key]

    def int_field(self, obj: dict, key: str, path: str, lo: Optional[int] = None, hi: Optional[int] = None) -> Optional[int]:
        if key not in obj:
            self.error("schema.keys", f"{path}.{key}", f"Pflichtfeld '{key}' fehlt")
            return None
        return self.int_value(obj[key], f"{path}.{key}", lo, hi)

    def container(self, value: Any, kind: type, path: str, code: str = "schema.type") -> bool:
        if not isinstance(value, kind):
            wanted = "Objekt" if kind is dict else "Liste"
            self.error(code, path, f"{wanted} erwartet")
            return False
        return True

    def cia_dict(self, value: Any, path: str) -> None:
        if not self.container(value, dict, path):
            return
        if set(value) != CIA_KEYS:
            self.error("schema.keys", path, f"Schlüssel müssen genau c, i, a sein, gefunden {sorted(value)}")
        for key, item in value.items():
            self.int_value(item, f"{path}.{key}")

    def run(self) -> List[Issue]:
        raw = self.raw
        if not self.container(raw, dict, "", "schema.top_level"):
            return self.issues
        for key, kind in (("budget_tiers", dict), ("waves", list), ("attacks", dict), ("measures", dict)):
            if key not in raw:
                self.error("schema.top_level", key, f"Pflichtfeld '{key}' fehlt")
            else:
                self.container(raw[key], kind, key, "schema.top_level")
        if "default_budget_tier" not in raw:
            self.error("schema.top_level", "default_budget_tier", "Pflichtfeld 'default_budget_tier' fehlt")
        self.check_final_index(raw.get("final_index"), "final_index" in raw)
        if "events" in raw:
            self.container(raw["events"], dict, "events", "schema.top_level")
        if "final_events" in raw:
            self.container(raw["final_events"], list, "final_events", "schema.top_level")
        if "base_cia" in raw:
            self.cia_dict(raw["base_cia"], "base_cia")
        else:
            self.warning("schema.default_used", "base_cia", "base_cia fehlt, der Lader setzt c=0, i=0, a=0")

        measures = raw["measures"] if isinstance(raw.get("measures"), dict) else {}
        attacks = raw["attacks"] if isinstance(raw.get("attacks"), dict) else {}
        self.check_measures(measures)
        self.check_attacks(attacks)
        self.check_waves(raw.get("waves"), attacks, measures)
        self.check_budget_tiers(raw.get("budget_tiers"), raw.get("default_budget_tier"))
        self.check_events(raw.get("events"), raw.get("final_events"), measures)
        self.check_exactness()
        self.check_hand_calc()
        if "practice" in raw:
            self.check_practice(raw["practice"], attacks, measures)
        if "session_schedule" in raw:
            self.check_session_schedule(raw["session_schedule"], raw.get("waves"))
        if "risk_matrix" in raw:
            self.check_risk_matrix(raw["risk_matrix"], raw.get("attacks"), raw.get("waves"))
        if "reference_plans" in raw:
            self.check_reference_plans(raw["reference_plans"], measures)
        if "reference_strategies" in raw:
            self.check_reference_strategies(raw["reference_strategies"], measures)
        return self.issues

    def check_measures(self, measures: dict) -> None:
        for measure_id, info in measures.items():
            path = f"measures.{measure_id}"
            if not self.container(info, dict, path):
                continue
            self.text_value(self.field(info, "name", path), f"{path}.name")
            levels = self.field(info, "levels", path)
            if isinstance(levels, dict):
                if set(levels) != LEVEL_KEYS:
                    self.error("schema.levels", f"{path}.levels", f"Level müssen genau 0, 1, 2, 3 sein, gefunden {sorted(levels)}")
                for level_id, level in levels.items():
                    self.check_level(level, f"{path}.levels.{level_id}", level_id == "0")
            elif levels is not None:
                self.error("schema.type", f"{path}.levels", "Objekt erwartet")
            self.check_dependencies(info.get("dependencies", []), measure_id, measures)
        self.check_dependency_cycles(measures)

    def check_level(self, level: Any, path: str, is_zero: bool) -> None:
        if not self.container(level, dict, path):
            return
        cia = self.field(level, "cia", path)
        if cia is not None:
            self.cia_dict(cia, f"{path}.cia")
        init = self.int_field(level, "init", path, lo=0)
        opex = self.int_field(level, "opex", path, lo=0)
        recovery = None
        if "recovery" in level:
            recovery = self.number_value(level["recovery"], f"{path}.recovery", lo=0, hi=1)
        if is_zero:
            cia_zero = isinstance(cia, dict) and all(value == 0 for value in cia.values())
            if not cia_zero or init not in (0, None) or opex not in (0, None) or recovery not in (0, None):
                self.error("schema.range", path, "Level 0 muss überall 0 sein")

    def check_dependencies(self, dependencies: Any, measure_id: str, measures: dict) -> None:
        path = f"measures.{measure_id}.dependencies"
        if not self.container(dependencies, list, path):
            return
        for index, dependency in enumerate(dependencies):
            dep_path = f"{path}[{index}]"
            if not self.container(dependency, dict, dep_path):
                continue
            self.int_field(dependency, "level", dep_path, lo=1, hi=3)
            requires = self.field(dependency, "requires", dep_path)
            if requires is None or not self.container(requires, list, f"{dep_path}.requires"):
                continue
            for req_index, req in enumerate(requires):
                req_path = f"{dep_path}.requires[{req_index}]"
                if not self.container(req, dict, req_path):
                    continue
                self.int_field(req, "min_level", req_path, lo=0, hi=3)
                self.check_measure_ref(req.get("measure"), f"{req_path}.measure", measures)

    def check_measure_ref(self, value: Any, path: str, measures: dict) -> bool:
        if not isinstance(value, str) or value not in measures:
            self.error("ref.unknown_measure", path, f"Unbekannte Maßnahme {value!r}")
            return False
        return True

    def check_dependency_cycles(self, measures: dict) -> None:
        edges: Dict[str, List[str]] = {}
        for measure_id, info in measures.items():
            targets = []
            for dependency in _dicts(info.get("dependencies") if isinstance(info, dict) else None):
                for req in _dicts(dependency.get("requires")):
                    target = req.get("measure")
                    if isinstance(target, str) and target in measures:
                        targets.append(target)
            edges[measure_id] = targets
        state: Dict[str, int] = {}

        def visit(node: str, trail: List[str]) -> None:
            state[node] = 1
            trail.append(node)
            for target in edges[node]:
                if state.get(target) == 1:
                    cycle = trail[trail.index(target):] + [target]
                    self.error(
                        "ref.dependency_cycle",
                        f"measures.{node}.dependencies",
                        f"Zyklische Abhängigkeit: {' -> '.join(cycle)}",
                    )
                elif target not in state:
                    visit(target, trail)
            trail.pop()
            state[node] = 2

        for node in edges:
            if node not in state:
                visit(node, [])

    def check_attacks(self, attacks: dict) -> None:
        for attack_id, info in attacks.items():
            self.check_attack(info, f"attacks.{attack_id}")

    def check_attack(self, info: Any, path: str) -> None:
        if not self.container(info, dict, path):
            return
        if "description" in info:
            self.prose_key("description", f"{path}.description")
        self.int_field(info, "base_severity", path, lo=0)
        self.int_field(info, "s_unit", path, lo=0)
        self.int_field(info, "kz_at_full_damage", path)
        self.int_field(info, "kz_at_full_mitigation", path)
        self.int_field(info, "mitigation_cap", path, lo=1)
        cia_impact = self.field(info, "cia_impact", path)
        if cia_impact is not None:
            self.cia_dict(cia_impact, f"{path}.cia_impact")
        recovery_flag = self.field(info, "allow_recovery", path)
        if recovery_flag is not None and not isinstance(recovery_flag, bool):
            self.error("schema.type", f"{path}.allow_recovery", "Wahrheitswert erwartet")

    def check_waves(self, waves: Any, attacks: dict, measures: dict) -> None:
        if not isinstance(waves, list):
            return
        ids = []
        for index, wave in enumerate(waves):
            path = f"waves[{index}]"
            if not self.container(wave, dict, path):
                continue
            wave_id = self.int_field(wave, "id", path)
            if wave_id is not None:
                ids.append(wave_id)
            if "name" in wave:
                self.prose_key("name", f"{path}.name")
            attack_id = self.field(wave, "attack_id", path)
            if attack_id is not None and (not isinstance(attack_id, str) or attack_id not in attacks):
                self.error("ref.unknown_attack", f"{path}.attack_id", f"Unbekannter Angriff {attack_id!r}")
            self.check_wave_scoring(wave, path, measures)
        if ids != list(range(1, len(waves) + 1)):
            self.error("schema.wave_ids", "waves", f"Wellen-IDs müssen 1..{len(waves)} fortlaufend und eindeutig sein, gefunden {ids}")
        else:
            self.wave_ids = ids

    def check_wave_scoring(self, wave: dict, path: str, measures: dict) -> None:
        weights = self.field(wave, "weights", path)
        if weights is not None and self.container(weights, dict, f"{path}.weights"):
            if set(weights) != CIA_KEYS:
                self.error("schema.keys", f"{path}.weights", f"Schlüssel müssen genau c, i, a sein, gefunden {sorted(weights)}")
            for key, value in weights.items():
                self.number_value(value, f"{path}.weights.{key}", lo=0)
        if "e_threshold" in wave:
            self.int_value(wave["e_threshold"], f"{path}.e_threshold", lo=0)
        else:
            self.warning("schema.default_used", f"{path}.e_threshold", "e_threshold fehlt, der Lader setzt 18")
        for removed in ("kz_bonus", "kz_malus"):
            if removed in wave:
                self.removed_key(removed, f"{path}.{removed}")
        bonus_measures = wave.get("bonus_measures", [])
        if self.container(bonus_measures, list, f"{path}.bonus_measures"):
            for bm_index, bm in enumerate(bonus_measures):
                bm_path = f"{path}.bonus_measures[{bm_index}]"
                if not self.container(bm, dict, bm_path):
                    continue
                self.check_measure_ref(bm.get("measure"), f"{bm_path}.measure", measures)
                self.int_field(bm, "min_level", bm_path, lo=1, hi=3)
                self.int_field(bm, "bonus", bm_path, lo=0)
                if "description" in bm:
                    self.prose_key("description", f"{bm_path}.description")

    def check_final_index(self, block: Any, present: bool) -> None:
        if not present:
            self.error("schema.top_level", "final_index", "Pflichtfeld 'final_index' fehlt")
            return
        if not self.container(block, dict, "final_index"):
            return
        weights = [self.field(block, key, "final_index") for key in ("weight_kz", "weight_ros")]
        values = [
            self.number_value(weight, f"final_index.{key}", lo=0)
            for key, weight in zip(("weight_kz", "weight_ros"), weights)
            if weight is not None
        ]
        if len(values) == 2 and all(value is not None for value in values) and not any(values):
            self.error("schema.range", "final_index", "weight_kz und weight_ros dürfen nicht beide 0 sein")

    def check_budget_tiers(self, tiers: Any, default_tier: Any) -> None:
        if not isinstance(tiers, dict):
            return
        if default_tier is not None and default_tier not in tiers:
            self.error("ref.unknown_tier", "default_budget_tier", f"Unbekannter Budget-Tier {default_tier!r}")
        for name, info in tiers.items():
            path = f"budget_tiers.{name}"
            if not self.container(info, dict, path):
                continue
            self.int_field(info, "budget", path, lo=0)
            if "kz_start" in info:
                self.int_value(info["kz_start"], f"{path}.kz_start")
            else:
                self.warning("schema.default_used", f"{path}.kz_start", "kz_start fehlt, der Lader setzt 60")
            if "severity_multiplier" in info:
                self.number_value(info["severity_multiplier"], f"{path}.severity_multiplier", lo=0)
            else:
                self.warning("schema.default_used", f"{path}.severity_multiplier", "severity_multiplier fehlt, der Lader setzt 1.0")
            if "e_targets" in info:
                self.removed_key("e_targets", f"{path}.e_targets")

    def check_events(self, events: Any, final_events: Any, measures: dict) -> None:
        kurswechsel_seen = 0
        if isinstance(events, dict):
            for key, wave_events in events.items():
                path = f"events.{key}"
                match = WAVE_KEY.fullmatch(key)
                if match is None or (self.wave_ids and int(match.group(1)) not in self.wave_ids):
                    self.error("ref.unknown_wave", path, f"Schlüssel {key!r} verweist auf keine Welle")
                if not self.container(wave_events, list, path):
                    continue
                for index, event in enumerate(wave_events):
                    self.check_event(event, f"{path}[{index}]", measures, final=False)
                    if isinstance(event, dict) and event.get("type") == "kurswechsel":
                        kurswechsel_seen += 1
                        if kurswechsel_seen > 1:
                            self.error("schema.kurswechsel_count", f"{path}[{index}]", "höchstens ein Kurswechsel erlaubt")
                        if match is not None and self.wave_ids and int(match.group(1)) == max(self.wave_ids):
                            self.error(
                                "schema.event_placement",
                                f"{path}[{index}]",
                                "Kurswechsel braucht ein Change-Fenster danach; in der letzten Welle nicht erlaubt",
                            )
                    if (
                        isinstance(event, dict)
                        and event.get("type") == "flat_budget"
                        and isinstance(event.get("budget_delta"), int)
                        and not isinstance(event.get("budget_delta"), bool)
                        and event["budget_delta"] < 0
                        and match is not None
                        and self.wave_ids
                        and int(match.group(1)) == max(self.wave_ids)
                    ):
                        self.warning(
                            "rules.event_without_window",
                            f"{path}[{index}]",
                            "Budgetkürzung in der letzten Welle: danach gibt es kein Change-Fenster mehr, "
                            "die Überziehung wird ohne Reaktionsmöglichkeit am Ende geprüft",
                        )
        if isinstance(final_events, list):
            for index, event in enumerate(final_events):
                self.check_event(event, f"final_events[{index}]", measures, final=True)

    def check_event(self, event: Any, path: str, measures: dict, final: bool) -> None:
        if not self.container(event, dict, path):
            return
        event_id = self.field(event, "id", path)
        if event_id is not None:
            if not isinstance(event_id, str) or not event_id or not event_id.isascii():
                self.error("schema.duplicate_id", f"{path}.id", f"Event-ID muss ein nicht leerer ASCII-Text sein, gefunden {event_id!r}")
            elif event_id in self.event_ids:
                self.error("schema.duplicate_id", f"{path}.id", f"Event-ID {event_id!r} bereits vergeben bei {self.event_ids[event_id]}")
            else:
                self.event_ids[event_id] = path
        self.text_value(self.field(event, "name", path), f"{path}.name")
        if "description" in event:
            self.prose_key("description", f"{path}.description")
        event_type = self.field(event, "type", path)
        if event_type is None:
            return
        if event_type not in KNOWN_EVENT_TYPES:
            self.error("schema.unknown_event_type", f"{path}.type", f"Unbekannter Event-Typ {event_type!r}")
            return
        if (event_type == "final_budget_tier") != final:
            where = "nur in final_events" if event_type == "final_budget_tier" else "nicht in final_events"
            self.error("schema.event_placement", path, f"Event-Typ {event_type} ist {where} erlaubt")
        missing = [key for key in REQUIRED_EVENT_PARAMS[event_type] if key not in event]
        if missing:
            self.error("schema.event_params", path, f"Pflichtparameter fehlen für {event_type}: {', '.join(missing)}")
            return
        getattr(self, f"event_{event_type}")(event, path, measures)

    def event_kurswechsel(self, event: dict, path: str, measures: dict) -> None:
        pass

    def event_flat_budget(self, event: dict, path: str, measures: dict) -> None:
        self.int_value(event["budget_delta"], f"{path}.budget_delta")

    def event_opex_discount_per_active_measure(self, event: dict, path: str, measures: dict) -> None:
        self.int_value(event["opex_per_measure"], f"{path}.opex_per_measure")

    def event_checklist_tier(self, event: dict, path: str, measures: dict) -> None:
        listed = event["measures"]
        count = None
        if self.container(listed, list, f"{path}.measures"):
            count = len(listed)
            for index, measure_id in enumerate(listed):
                self.check_measure_ref(measure_id, f"{path}.measures[{index}]", measures)
        self.int_value(event["min_level"], f"{path}.min_level", lo=1, hi=3)
        self.check_tiers(event["tiers"], f"{path}.tiers", max_minimum=count, first_minimum=0)

    def event_measure_level_tier(self, event: dict, path: str, measures: dict) -> None:
        self.check_measure_ref(event["measure"], f"{path}.measure", measures)
        tiers = event["tiers"]
        if not self.container(tiers, dict, f"{path}.tiers"):
            return
        if set(tiers) != LEVEL_KEYS:
            self.error("schema.tiers_order", f"{path}.tiers", f"Schlüssel müssen genau 0..3 sein, gefunden {sorted(tiers)}")
        for key, value in tiers.items():
            self.int_value(value, f"{path}.tiers.{key}")

    def event_level_bonus_per_measure(self, event: dict, path: str, measures: dict) -> None:
        self.int_value(event["level"], f"{path}.level", lo=1, hi=3)
        self.int_value(event["kz_per_measure"], f"{path}.kz_per_measure")

    def event_and_condition(self, event: dict, path: str, measures: dict) -> None:
        self.int_value(event["kz_delta"], f"{path}.kz_delta")
        clauses = event["clauses"]
        if not self.container(clauses, list, f"{path}.clauses"):
            return
        if not clauses:
            self.error("schema.event_params", f"{path}.clauses", "mindestens eine Bedingung erforderlich")
        for index, clause in enumerate(clauses):
            clause_path = f"{path}.clauses[{index}]"
            if not self.container(clause, dict, clause_path):
                continue
            self.check_measure_ref(clause.get("measure"), f"{clause_path}.measure", measures)
            present = [key for key in ("min_level", "level_eq") if key in clause]
            if len(present) != 1:
                self.error("schema.event_params", clause_path, "genau eines von min_level und level_eq erforderlich")
                continue
            self.int_value(clause[present[0]], f"{clause_path}.{present[0]}", lo=0, hi=3)

    def event_final_budget_tier(self, event: dict, path: str, measures: dict) -> None:
        self.check_tiers(event["tiers"], f"{path}.tiers", first_minimum=0)
        penalty_path = f"{path}.overspend_penalty"
        penalty = event["overspend_penalty"]
        if not self.container(penalty, dict, penalty_path):
            return
        self.int_field(penalty, "kz_per_step", penalty_path, lo=1)
        step = self.int_field(penalty, "step", penalty_path, lo=1)
        if step is not None and step != 10:
            self._hand_calc(
                "hand_calc.penalty_step",
                f"{penalty_path}.step",
                f"Schrittweite {step} k€ weicht von 10 k€ ab, die gedruckte Regel lautet \"je angefangene 10.000 €\"",
            )

    def check_tiers(
        self, tiers: Any, path: str, max_minimum: Optional[int] = None, first_minimum: Optional[int] = None
    ) -> None:
        if not self.container(tiers, list, path):
            return
        if not tiers:
            self.error("schema.tiers_order", path, "mindestens eine Stufe erforderlich")
            return
        minima = []
        for index, tier in enumerate(tiers):
            tier_path = f"{path}[{index}]"
            if not isinstance(tier, list) or len(tier) != 2:
                self.error("schema.type", tier_path, "Paar [Minimum, Wert] erwartet")
                continue
            minimum = self.int_value(tier[0], f"{tier_path}[0]")
            self.int_value(tier[1], f"{tier_path}[1]")
            if minimum is not None:
                minima.append(minimum)
                if max_minimum is not None and minimum > max_minimum:
                    self.error("schema.tiers_order", tier_path, f"Stufenminimum {minimum} größer als die Anzahl der Maßnahmen ({max_minimum})")
        if any(later <= earlier for earlier, later in zip(minima, minima[1:])):
            self.error("schema.tiers_order", path, f"Stufenminima müssen streng aufsteigend sein, gefunden {minima}")
        if first_minimum is not None and minima and minima[0] != first_minimum:
            self.error("schema.tiers_order", path, f"erstes Stufenminimum muss {first_minimum} sein, gefunden {minima[0]}")

    def check_session_schedule(self, block: Any, waves: Any) -> None:
        """Ablaufplan und Druckliste (D-01, D-22, D-27): nur Zahlen und IDs, Prosa steht in content/texte.toml."""
        path = "session_schedule"
        if not self.container(block, dict, path):
            return
        for key in block:
            if key not in SCHEDULE_KEYS:
                self.error("schema.keys", f"{path}.{key}", f"Unbekannter Schlüssel '{key}' im Ablaufplan")
        total = self.int_field(block, "total_minutes", path, lo=1)
        self.int_field(block, "teams", path, lo=1)
        self.int_field(block, "persons_per_team", path, lo=1)

        wave_ids = {
            wave["id"] for wave in waves
            if isinstance(wave, dict) and isinstance(wave.get("id"), int) and not isinstance(wave.get("id"), bool)
        } if isinstance(waves, list) else set()
        blocks = self.field(block, "blocks", path)
        if blocks is not None and self.container(blocks, list, f"{path}.blocks"):
            self.check_schedule_blocks(blocks, total, wave_ids)
        print_list = self.field(block, "print_list", path)
        if print_list is not None and self.container(print_list, list, f"{path}.print_list"):
            self.check_print_list(print_list)
        stages = block.get("debrief_stages")
        if stages is not None and self.container(stages, list, f"{path}.debrief_stages"):
            debrief_minutes = None
            if isinstance(blocks, list):
                debrief_minutes = next(
                    (
                        item.get("minutes") for item in blocks
                        if isinstance(item, dict) and item.get("id") == "debrief"
                    ),
                    None,
                )
            self.check_debrief_stages(stages, debrief_minutes)

    def check_risk_matrix(self, block: Any, attacks: Any, waves: Any) -> None:
        """Risikomatrix (RISK-01, D-04, D-22, D-24): Zeilen des Registers und € Bänder; nur Zahlen und IDs, Prosa steht in content/texte.toml."""
        path = "risk_matrix"
        if not self.container(block, dict, path):
            return
        for key in block:
            if key not in RISK_MATRIX_KEYS:
                self.error("schema.keys", f"{path}.{key}", f"Unbekannter Schlüssel '{key}' in der Risikomatrix")
        self.int_field(block, "register_rows", path, lo=1)
        bands = self.field(block, "bands", path)
        if bands is None or not self.container(bands, list, f"{path}.bands"):
            return
        if len(bands) != RISK_BAND_COUNT:
            self.error(
                "risk.bands_count", f"{path}.bands",
                f"Die Risikomatrix hat genau {RISK_BAND_COUNT} Bänder, gefunden {len(bands)}",
            )
        seen: set = set()
        minima: List[Optional[int]] = []
        ids_ok = True
        for index, band in enumerate(bands):
            band_path = f"{path}.bands[{index}]"
            if not self.container(band, dict, band_path):
                minima.append(None)
                ids_ok = False
                continue
            for key in band:
                if key not in RISK_BAND_KEYS:
                    self.error("schema.keys", f"{band_path}.{key}", f"Unbekannter Schlüssel '{key}' im Band")
            band_id = self.field(band, "id", band_path)
            if band_id is None:
                ids_ok = False
            elif not isinstance(band_id, str) or not SNAKE_ID.fullmatch(band_id):
                self.error("risk.band_id", f"{band_path}.id", f"Ungültige Band-ID {band_id!r}")
                ids_ok = False
            elif band_id in seen:
                self.error("risk.band_id", f"{band_path}.id", f"Doppelte Band-ID {band_id!r}")
                ids_ok = False
            else:
                seen.add(band_id)
            minima.append(self.int_field(band, "min", band_path, lo=0))
        if any(value is None for value in minima):
            self.check_risk_cases(block, seen, None, attacks, waves)
            return
        ordered = minima[0] == 0 and all(left < right for left, right in zip(minima, minima[1:]))
        if not ordered:
            self.error(
                "risk.bands_order", f"{path}.bands",
                f"Die Untergrenzen der Bänder müssen bei 0 beginnen und streng aufsteigen, gefunden {minima}",
            )
        rebuilt = None
        if ordered and ids_ok and len(bands) == RISK_BAND_COUNT:
            rebuilt = tuple(RiskBand(id=item["id"], minimum=item["min"]) for item in bands)
        self.check_risk_cases(block, seen, rebuilt, attacks, waves)
        if rebuilt is None:
            return
        damages = self.used_unprotected_damages(attacks, waves)
        if not damages:
            return
        for attack_id, damage in damages.items():
            if damage in minima[1:]:
                self.error(
                    "risk.attack_band", f"{path}.bands",
                    f"Der ungeschützte Schaden von '{attack_id}' ({damage}) liegt genau auf einer Bandgrenze",
                )
        if band_of(rebuilt, min(damages.values())).id == rebuilt[0].id:
            self.error("risk.attack_band", f"{path}.bands", "Ein ungeschützter Angriff läge im niedrigsten Band")
        if band_of(rebuilt, max(damages.values())).id != rebuilt[-1].id:
            self.error("risk.attack_band", f"{path}.bands", "Kein ungeschützter Angriff erreicht das höchste Band")

    def check_risk_cases(
        self, block: dict, band_ids: set, bands: Optional[tuple], attacks: Any, waves: Any,
    ) -> None:
        """Geschäftsfälle der Spielleitung (RISK-05, D-06, D-22): ID, Band und optionaler Angriffs-Anker; nur ein
        verankerter Fall muss das Band des ungeschützten Schadens seines Angriffs tragen, die anderen sind
        Plausibilitätsurteile ohne Spielwert."""
        path = "risk_matrix.cases"
        if "cases" not in block:
            return
        cases = block["cases"]
        if not self.container(cases, list, path):
            return
        damages = self.used_unprotected_damages(attacks, waves)
        seen: set = set()
        for index, case in enumerate(cases):
            case_path = f"{path}[{index}]"
            if not self.container(case, dict, case_path):
                continue
            for key in case:
                if key not in RISK_CASE_KEYS:
                    self.error("schema.keys", f"{case_path}.{key}", f"Unbekannter Schlüssel '{key}' im Geschäftsfall")
            case_id = self.field(case, "id", case_path)
            if case_id is not None:
                if not isinstance(case_id, str) or not SNAKE_ID.fullmatch(case_id):
                    self.error("risk.case_id", f"{case_path}.id", f"Ungültige Fall-ID {case_id!r}")
                elif case_id in seen:
                    self.error("risk.case_id", f"{case_path}.id", f"Doppelte Fall-ID {case_id!r}")
                else:
                    seen.add(case_id)
            band = self.field(case, "band", case_path)
            band_known = isinstance(band, str) and band in band_ids
            if band is not None and not band_known:
                self.error("risk.case_band", f"{case_path}.band", f"Fall '{case_id}': '{band}' ist keine Band-ID")
            if "like_attack" not in case:
                continue
            anchor = case["like_attack"]
            if not isinstance(anchor, str) or anchor not in damages:
                self.error(
                    "risk.case_attack", f"{case_path}.like_attack",
                    f"Fall '{case_id}': '{anchor}' ist kein in Wellen genutzter Angriff",
                )
            elif band_known and bands is not None and band_of(bands, damages[anchor]).id != band:
                self.error(
                    "risk.case_consistency", f"{case_path}.band",
                    f"Fall '{case_id}': Band passt nicht zum ungeschützten Schaden des Angriffs",
                )

    @staticmethod
    def used_unprotected_damages(attacks: Any, waves: Any) -> Dict[str, int]:
        """Basis-Schweregrad mal Euro je Punkt der in Wellen genutzten Angriffe (nur gültige Werte, in Tausend Euro)."""
        if not isinstance(attacks, dict) or not isinstance(waves, list):
            return {}
        damages: Dict[str, int] = {}
        for wave in waves:
            attack_id = wave.get("attack_id") if isinstance(wave, dict) else None
            attack = attacks.get(attack_id) if isinstance(attack_id, str) else None
            if not isinstance(attack, dict):
                continue
            severity, unit = attack.get("base_severity"), attack.get("s_unit")
            if all(isinstance(value, int) and not isinstance(value, bool) for value in (severity, unit)):
                damages[attack_id] = severity * unit
        return damages

    def check_debrief_stages(self, stages: list, debrief_minutes: Any) -> None:
        """Richtzeit je Debriefing-Stufe (D-11): Summe der Stufen = Dauer des Blocks 'debrief'."""
        path = "session_schedule.debrief_stages"
        seen: set = set()
        stage_sum = 0
        sum_known = True
        for index, item in enumerate(stages):
            item_path = f"{path}[{index}]"
            if not self.container(item, dict, item_path):
                sum_known = False
                continue
            for key in item:
                if key not in DEBRIEF_STAGE_KEYS:
                    self.error("schema.keys", f"{item_path}.{key}", f"Unbekannter Schlüssel '{key}' in der Debriefing-Stufe")
            stage_id = self.field(item, "id", item_path)
            if stage_id is not None:
                if not isinstance(stage_id, str) or not SNAKE_ID.fullmatch(stage_id):
                    self.error("schedule.id", f"{item_path}.id", f"Stufen-ID {stage_id!r} muss snake_case sein")
                elif stage_id in seen:
                    self.error("schedule.id", f"{item_path}.id", f"Stufen-ID '{stage_id}' kommt doppelt vor")
                else:
                    seen.add(stage_id)
            minutes = self.int_field(item, "minutes", item_path, lo=1)
            if minutes is None:
                sum_known = False
            else:
                stage_sum += minutes
        if not stages:
            return
        if not isinstance(debrief_minutes, int) or isinstance(debrief_minutes, bool):
            self.error("schedule.debrief_block", path, "Debriefing-Stufen brauchen einen Ablaufblock mit der ID 'debrief'")
        elif sum_known and stage_sum != debrief_minutes:
            self.error(
                "schedule.debrief_sum", path,
                f"Die Stufen ergeben {stage_sum} Minuten, der Block 'debrief' dauert {debrief_minutes}",
            )

    def check_schedule_blocks(self, blocks: list, total: Optional[int], wave_ids: set) -> None:
        path = "session_schedule.blocks"
        seen_ids: set = set()
        seen_waves: set = set()
        minutes_sum = 0
        sum_known = True
        for index, item in enumerate(blocks):
            item_path = f"{path}[{index}]"
            if not self.container(item, dict, item_path):
                sum_known = False
                continue
            for key in item:
                if key not in SCHEDULE_BLOCK_KEYS:
                    self.error("schema.keys", f"{item_path}.{key}", f"Unbekannter Schlüssel '{key}' im Ablaufblock")
            block_id = self.field(item, "id", item_path)
            if block_id is not None:
                if not isinstance(block_id, str) or not SNAKE_ID.fullmatch(block_id):
                    self.error("schedule.id", f"{item_path}.id", f"Block-ID {block_id!r} muss snake_case sein")
                elif block_id in seen_ids:
                    self.error("schedule.id", f"{item_path}.id", f"Block-ID '{block_id}' kommt doppelt vor")
                else:
                    seen_ids.add(block_id)
            minutes = self.int_field(item, "minutes", item_path, lo=1)
            if minutes is None:
                sum_known = False
            else:
                minutes_sum += minutes
            if "wave" in item:
                wave = self.int_value(item["wave"], f"{item_path}.wave")
                if wave is not None:
                    if wave != 0 and wave not in wave_ids:
                        self.error("schedule.wave_block", f"{item_path}.wave", f"Welle {wave} gibt es in der Konfiguration nicht")
                    elif wave in seen_waves:
                        self.error("schedule.wave_block", f"{item_path}.wave", f"Welle {wave} hat mehr als einen Block")
                    else:
                        seen_waves.add(wave)
        for wave_id in sorted(wave_ids - seen_waves):
            self.error("schedule.wave_block", path, f"Welle {wave_id} hat keinen Block im Ablaufplan")
        if sum_known and total is not None and minutes_sum != total:
            self.error("schedule.sum", path, f"Die Blöcke ergeben {minutes_sum} Minuten, total_minutes ist {total}")

    def check_print_list(self, rows: list) -> None:
        path = "session_schedule.print_list"
        seen: set = set()
        for index, item in enumerate(rows):
            item_path = f"{path}[{index}]"
            if not self.container(item, dict, item_path):
                continue
            for key in item:
                if key not in PRINT_ROW_KEYS:
                    self.error("schema.keys", f"{item_path}.{key}", f"Unbekannter Schlüssel '{key}' in der Druckliste")
            job = self.field(item, "job", item_path)
            if job is not None:
                if not isinstance(job, str) or not PRINT_JOB.fullmatch(job):
                    self.error("schedule.print_job", f"{item_path}.job", f"Dokumentname {job!r} darf nur a-z, 0-9, _ und - enthalten")
                    job = None
                elif job in seen:
                    self.error("schedule.print_job", f"{item_path}.job", f"Dokument '{job}' steht doppelt in der Druckliste")
                else:
                    seen.add(job)
            per_team = self.int_field(item, "per_team", item_path, lo=0)
            self.int_field(item, "facilitator", item_path, lo=0)
            if job is not None and job.startswith("spielleitung-") and per_team:
                self.error(
                    "schedule.print_veil", f"{item_path}.per_team",
                    f"Das Spielleitungs-Dokument '{job}' darf nicht an die Teams gehen",
                )

    def check_practice(self, block: Any, attacks: dict, measures: dict) -> None:
        """Welle 0 (D-12): own attack, wave, event and example selection that must stay invisible to waves 1-3."""
        path = "practice"
        if "practice" in attacks:
            self.error("practice.attack_id_taken", "attacks.practice", "Die ID 'practice' ist dem Übungsangriff vorbehalten")
        if not self.container(block, dict, path):
            return
        for key in block:
            if key not in PRACTICE_KEYS:
                self.error("schema.keys", f"{path}.{key}", f"Unbekannter Schlüssel '{key}' im Übungsblock")
        self.int_field(block, "kz_start", path)
        self.int_field(block, "budget", path, lo=0)

        attack = self.field(block, "attack", path)
        self.check_attack(attack, f"{path}.attack")
        if (
            isinstance(attack, dict)
            and isinstance(attack.get("base_severity"), int)
            and isinstance(attack.get("mitigation_cap"), int)
            and attack["base_severity"] != attack["mitigation_cap"]
        ):
            self.error(
                "practice.severity_cap",
                f"{path}.attack",
                f"base_severity {attack['base_severity']} muss mitigation_cap {attack['mitigation_cap']} gleich sein, "
                "sonst stimmt die gedruckte Schadensformel nicht",
            )

        wave = self.field(block, "wave", path)
        if isinstance(wave, dict):
            self.check_wave_scoring(wave, f"{path}.wave", measures)
            if "e_threshold" not in wave:
                self.error("schema.keys", f"{path}.wave.e_threshold", "Pflichtfeld 'e_threshold' fehlt")
            self.check_practice_distinct(wave, f"{path}.wave")
        elif wave is not None:
            self.error("schema.type", f"{path}.wave", "Objekt erwartet")

        event = self.field(block, "event", path)
        if isinstance(event, dict):
            self.check_event(event, f"{path}.event", measures, final=False)
            if event.get("type") in KNOWN_EVENT_TYPES and event["type"] not in PRACTICE_EVENT_TYPES:
                self.error(
                    "practice.event_type",
                    f"{path}.event.type",
                    f"Das Übungs-Ereignis braucht eine KZ-Wirkung, Typ {event['type']} hat keine",
                )
        elif event is not None:
            self.error("schema.type", f"{path}.event", "Objekt erwartet")

        selection = self.field(block, "selection", path)
        if selection is not None and self.container(selection, dict, f"{path}.selection"):
            if set(selection) != set(measures):
                self.error(
                    "practice.selection_measures",
                    f"{path}.selection",
                    f"Die Auswahl muss genau alle Maßnahmen enthalten, gefunden {sorted(selection)}",
                )
            for measure_id, level in selection.items():
                known = measures.get(measure_id)
                levels = known.get("levels") if isinstance(known, dict) else None
                valid = (
                    isinstance(level, int)
                    and not isinstance(level, bool)
                    and isinstance(levels, dict)
                    and str(level) in levels
                )
                if measure_id in measures and not valid:
                    self.error(
                        "practice.selection_level",
                        f"{path}.selection.{measure_id}",
                        f"Level {level!r} von {measure_id} gibt es nicht in der Konfiguration",
                    )

    def check_practice_distinct(self, wave: dict, path: str) -> None:
        """Weights and bonus measures of the practice wave must not hint at a real wave (D-12, T-05-39)."""
        raw = self.raw
        weights = wave.get("weights")
        if isinstance(weights, dict) and set(weights) == CIA_KEYS:
            values = [_fraction(weights[key]) for key in ("c", "i", "a")]
            if all(value is not None for value in values):
                weight_scale = scale_factors(raw)[0]
                for key, value in zip(("c", "i", "a"), values):
                    if weight_scale % value.denominator != 0:
                        self.error(
                            "practice.weight_scale",
                            f"{path}.weights",
                            f"Gewicht {key} = {float(value)} teilt die Gewichtsskala {weight_scale} der echten Wellen nicht",
                        )
                        break
                for index, real in enumerate(_dicts(raw.get("waves"))):
                    real_weights = real.get("weights")
                    if not isinstance(real_weights, dict) or set(real_weights) != CIA_KEYS:
                        continue
                    real_values = [_fraction(real_weights[key]) for key in ("c", "i", "a")]
                    if any(value is None for value in real_values):
                        continue
                    if values == real_values:
                        self.error(
                            "practice.weights_equal_wave",
                            f"{path}.weights",
                            f"Die Übungsgewichte sind gleich den Gewichten von waves[{index}]",
                        )
                    elif sorted(values) == sorted(real_values):
                        self.error(
                            "practice.weights_permutation",
                            f"{path}.weights",
                            f"Die Übungsgewichte sind eine Umordnung der Gewichte von waves[{index}]",
                        )
        real_bonus = {
            bm.get("measure")
            for real in _dicts(raw.get("waves"))
            for bm in _dicts(real.get("bonus_measures"))
        }
        for index, bm in enumerate(_dicts(wave.get("bonus_measures"))):
            if bm.get("measure") in real_bonus:
                self.error(
                    "practice.bonus_measure_shared",
                    f"{path}.bonus_measures[{index}].measure",
                    f"Maßnahme {bm.get('measure')} ist Bonus-Maßnahme einer echten Welle",
                )

    def check_reference_plans(self, block: Any, measures: dict) -> None:
        """Reference paths for the answer keys (D-22): references and ranges only; legality is a rules matter."""
        path = "reference_plans"
        if not self.container(block, dict, path):
            return
        tiers = self.raw.get("budget_tiers")
        for tier, plan in block.items():
            plan_path = f"{path}.{tier}"
            if not isinstance(tiers, dict) or tier not in tiers:
                self.error("ref.unknown_tier", plan_path, f"Unbekannter Budget-Tier {tier!r}")
            self._check_reference_path(plan, plan_path, measures, ("start", "windows"))

    def check_reference_strategies(self, block: Any, measures: dict) -> None:
        """Reference strategies of the quartile checks (BAL-07, D-25): tier, name, then kind plus the plan shape.

        Kept apart from `reference_plans`; legality (Kurswechsel, budget) is judged by `rules.evaluate_path`.
        """
        path = "reference_strategies"
        if not self.container(block, dict, path):
            return
        tiers = self.raw.get("budget_tiers")
        for tier, entries in block.items():
            tier_path = f"{path}.{tier}"
            if not isinstance(tiers, dict) or tier not in tiers:
                self.error("ref.unknown_tier", tier_path, f"Unbekannter Budget-Tier {tier!r}")
            if not self.container(entries, dict, tier_path):
                continue
            for name, entry in entries.items():
                entry_path = f"{tier_path}.{name}"
                if isinstance(entry, dict):
                    kind = entry.get("kind")
                    if not isinstance(kind, str) or kind not in REFERENCE_STRATEGY_KINDS:
                        self.error(
                            "ref.bad_kind",
                            f"{entry_path}.kind",
                            f"Art muss eine von {', '.join(REFERENCE_STRATEGY_KINDS)} sein, gefunden {kind!r}",
                        )
                self._check_reference_path(entry, entry_path, measures, ("kind", "start", "windows"))

    def _check_reference_path(self, plan: Any, plan_path: str, measures: dict, allowed_keys: tuple) -> None:
        """Start selection and change windows of one reference path: references and ranges only."""
        waves = self.raw.get("waves")
        max_windows = len(waves) - 1 if isinstance(waves, list) else None
        if not self.container(plan, dict, plan_path):
            return
        for key in plan:
            if key not in allowed_keys:
                self.error("schema.keys", f"{plan_path}.{key}", f"Unbekannter Schlüssel '{key}' im Referenzpfad")
        start = self.field(plan, "start", plan_path)
        if start is not None:
            self.check_reference_selection(start, f"{plan_path}.start", measures)
        windows = self.field(plan, "windows", plan_path)
        if windows is None or not self.container(windows, list, f"{plan_path}.windows"):
            return
        if max_windows is not None and len(windows) > max_windows:
            self.error(
                "ref.window_count",
                f"{plan_path}.windows",
                f"{len(windows)} Fenster bei {len(waves)} Wellen, höchstens {max_windows}",
            )
        for number, window in enumerate(windows, start=1):
            window_path = f"{plan_path}.windows[{number}]"
            if not self.container(window, dict, window_path):
                continue
            for key in window:
                if key not in ("selection", "swap"):
                    self.error("schema.keys", f"{window_path}.{key}", f"Unbekannter Schlüssel '{key}' im Fenster")
            selection = self.field(window, "selection", window_path)
            if selection is not None:
                self.check_reference_selection(selection, f"{window_path}.selection", measures)
            if "swap" in window:
                self.check_reference_swap(window["swap"], f"{window_path}.swap", measures)

    def check_reference_selection(self, selection: Any, path: str, measures: dict) -> None:
        if not self.container(selection, dict, path):
            return
        if set(selection) != set(measures):
            self.error(
                "ref.measure_set",
                path,
                f"Die Auswahl muss genau alle Maßnahmen enthalten, gefunden {sorted(selection)}",
            )
        for measure_id, level in selection.items():
            known = measures.get(measure_id)
            levels = known.get("levels") if isinstance(known, dict) else None
            if not isinstance(levels, dict):
                continue
            value = self.int_value(level, f"{path}.{measure_id}")
            if value is not None and str(value) not in levels:
                self.error("schema.range", f"{path}.{measure_id}", f"Level {value} von {measure_id} gibt es nicht")

    def check_reference_swap(self, swap: Any, path: str, measures: dict) -> None:
        if not isinstance(swap, list) or len(swap) != 2:
            self.error("schema.type", path, "Liste aus genau zwei Maßnahmen erwartet (wegfallend, neu)")
            return
        known = [self.check_measure_ref(measure_id, f"{path}[{index}]", measures) for index, measure_id in enumerate(swap)]
        if all(known) and swap[0] == swap[1]:
            self.error("ref.swap_same_measure", path, "Ein Tausch nennt zwei verschiedene Maßnahmen")

    def check_exactness(self) -> None:
        raw = self.raw
        weight_scale, recovery_scale = scale_factors(raw)
        attacks = raw["attacks"] if isinstance(raw.get("attacks"), dict) else {}
        tiers = raw["budget_tiers"] if isinstance(raw.get("budget_tiers"), dict) else {}
        for tier_name, tier in tiers.items():
            if not isinstance(tier, dict):
                continue
            multiplier = _fraction(tier.get("severity_multiplier", 1.0))
            if multiplier is None:
                continue
            offenders = []
            for attack_id, attack in attacks.items():
                severity = attack.get("base_severity") if isinstance(attack, dict) else None
                if isinstance(severity, int) and not isinstance(severity, bool):
                    if (severity * multiplier * weight_scale).denominator != 1:
                        offenders.append(attack_id)
            if offenders:
                self.error(
                    "exact.severity_scaling",
                    f"budget_tiers.{tier_name}",
                    f"base_severity x severity_multiplier x {weight_scale} ist für {', '.join(offenders)} nicht ganzzahlig",
                )
        recoveries = {Fraction(0)}
        for measure in raw["measures"].values() if isinstance(raw.get("measures"), dict) else []:
            levels = measure.get("levels") if isinstance(measure, dict) else None
            for level in levels.values() if isinstance(levels, dict) else []:
                fraction = _fraction(level.get("recovery", 0)) if isinstance(level, dict) else None
                if fraction is not None:
                    recoveries.add(fraction)
        for attack_id, attack in attacks.items():
            if not isinstance(attack, dict):
                continue
            s_unit = attack.get("s_unit")
            if not isinstance(s_unit, int) or isinstance(s_unit, bool):
                continue
            applicable = recoveries if attack.get("allow_recovery") is True else {Fraction(0)}
            for recovery in sorted(applicable):
                damage = Fraction(s_unit * 1000) * (1 - recovery) / weight_scale
                if damage.denominator != 1:
                    self.error(
                        "exact.damage_whole_euros",
                        f"attacks.{attack_id}",
                        f"Schaden pro Schweregrad-Schritt ist bei Recovery {float(recovery)} kein ganzer Euro-Betrag ({damage} EUR)",
                    )
                    break

    def check_final_index_weights(self, block: Any) -> None:
        if not isinstance(block, dict):
            return
        weight_kz, weight_ros = _fraction(block.get("weight_kz")), _fraction(block.get("weight_ros"))
        if weight_kz is None or weight_ros is None:
            return
        if weight_kz != 1 or weight_ros.denominator != 1:
            self._hand_calc(
                "hand_calc.final_index_weights",
                "final_index",
                "Final-Index-Gewichte müssen ganze Zahlen sein und weight_kz = 1 (Form KZ + k × RoS)",
            )

    def check_hand_calc(self) -> None:
        raw = self.raw
        waves = _dicts(raw.get("waves"))
        attacks = raw["attacks"] if isinstance(raw.get("attacks"), dict) else {}
        for attack_id, attack in attacks.items():
            if not isinstance(attack, dict):
                continue
            path = f"attacks.{attack_id}"
            ints = [attack.get(key) for key in ("kz_at_full_damage", "kz_at_full_mitigation", "mitigation_cap", "base_severity")]
            if any(isinstance(value, bool) or not isinstance(value, int) for value in ints) or ints[2] <= 0:
                continue
            slope = kz_slope(ints[0], ints[1], ints[2])
            if not _one_decimal(slope):
                used = [f"Welle {wave.get('id')}" for wave in waves if wave.get("attack_id") == attack_id]
                suffix = f" (verwendet in {', '.join(used)})" if used else ""
                self._hand_calc(
                    "hand_calc.kz_slope",
                    path,
                    f"KZ-Steigung {slope.numerator}/{slope.denominator} hat mehr als eine Nachkommastelle{suffix}",
                )
            if ints[3] != ints[2]:
                self._hand_calc("hand_calc.severity_cap", path, f"base_severity {ints[3]} weicht von mitigation_cap {ints[2]} ab")
        self.check_final_index_weights(raw.get("final_index"))
        tiers = raw["budget_tiers"] if isinstance(raw.get("budget_tiers"), dict) else {}
        for tier_name, tier in tiers.items():
            multiplier = _fraction(tier.get("severity_multiplier", 1.0)) if isinstance(tier, dict) else None
            if multiplier is not None and multiplier != 1:
                self._hand_calc(
                    "hand_calc.severity_multiplier",
                    f"budget_tiers.{tier_name}.severity_multiplier",
                    f"severity_multiplier {float(multiplier)} weicht von 1.0 ab",
                )
        for index, wave in enumerate(_dicts(raw.get("waves"))):
            weights = wave.get("weights")
            values = [_fraction(v) for v in weights.values()] if isinstance(weights, dict) else []
            if not values or any(v is None for v in values):
                continue
            if sum(values) != 1 or not all(_one_decimal(v) for v in values):
                self._hand_calc(
                    "hand_calc.weights",
                    f"waves[{index}].weights",
                    f"Gewichte müssen sich zu 1.0 summieren und höchstens eine Nachkommastelle haben, Summe {float(sum(values))}",
                )
        measures = raw["measures"] if isinstance(raw.get("measures"), dict) else {}
        for measure_id, measure in measures.items():
            levels = measure.get("levels") if isinstance(measure, dict) else None
            for level_id, level in levels.items() if isinstance(levels, dict) else []:
                recovery = _fraction(level.get("recovery", 0)) if isinstance(level, dict) else None
                if recovery is not None and not _one_decimal(recovery):
                    self._hand_calc(
                        "hand_calc.recovery",
                        f"measures.{measure_id}.levels.{level_id}.recovery",
                        f"Recovery {float(recovery)} hat mehr als eine Nachkommastelle",
                    )


def validate(raw: dict, hand_calc_level: str = "error") -> List[Issue]:
    return _Validator(raw, hand_calc_level).run()
