import json
import warnings
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Dict, List


@dataclass
class Attack:
    attack_id: str
    base_severity: int
    s_unit: int
    kz_at_full_damage: float
    kz_at_full_mitigation: float
    cia_impact: Dict[str, int]
    mitigation_cap: int
    allow_recovery: bool


@dataclass
class BonusMeasure:
    measure: str
    min_level: int
    bonus: int
    description: str


@dataclass
class Wave:
    wave_id: int
    name: str
    attack_id: str
    weights: Dict[str, Fraction]
    e_threshold: int
    bonus_measures: List[BonusMeasure]


@dataclass
class MeasureLevel:
    cia: Dict[str, int]
    init: int
    opex: int
    recovery: Fraction = Fraction(0)


@dataclass
class Measure:
    measure_id: str
    name: str
    levels: Dict[int, MeasureLevel]
    dependencies: List[Dict] = field(default_factory=list)


@dataclass
class BudgetTier:
    name: str
    budget: int
    kz_start: int
    severity_multiplier: Fraction


@dataclass
class Event:
    id: str
    name: str
    description: str
    type: str
    params: Dict


@dataclass
class Config:
    default_budget_tier: str
    budget_tiers: Dict[str, BudgetTier]
    attacks: Dict[str, Attack]
    waves: List[Wave]
    measures: Dict[str, Measure]
    events: Dict[int, List[Event]]
    base_cia: Dict[str, int]
    final_events: List[Event]
    ws: int
    rs: int

    @property
    def measure_ids(self) -> List[str]:
        return list(self.measures)


def _build_event(ev: Dict) -> Event:
    return Event(
        id=ev["id"],
        name=ev["name"],
        description=ev["description"],
        type=ev["type"],
        params={k: v for k, v in ev.items() if k not in ("id", "name", "description", "type")},
    )


def read_raw_config(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"), parse_float=Fraction)


def check_config(raw: Dict, source: str) -> None:
    from planspiel.validate import ConfigError, HandCalcWarning, validate

    issues = validate(raw)
    errors = [issue for issue in issues if issue.level == "error"]
    if errors:
        raise ConfigError(errors, source)
    for issue in issues:
        if issue.level == "warning":
            warnings.warn(f"{issue.code} {issue.path}: {issue.message}", HandCalcWarning, stacklevel=3)


def load_config(path: Path) -> Config:
    raw = read_raw_config(path)
    check_config(raw, str(path))
    from planspiel.validate import scale_factors

    ws, rs = scale_factors(raw)
    base_cia = raw.get("base_cia", {"c": 0, "i": 0, "a": 0})

    budget_tiers = {}
    for name, info in raw["budget_tiers"].items():
        budget_tiers[name] = BudgetTier(
            name=name,
            budget=info["budget"],
            kz_start=info.get("kz_start", 60),
            severity_multiplier=info.get("severity_multiplier", Fraction(1)),
        )

    attacks = {
        attack_id: Attack(
            attack_id=attack_id,
            base_severity=info["base_severity"],
            s_unit=info["s_unit"],
            kz_at_full_damage=info["kz_at_full_damage"],
            kz_at_full_mitigation=info["kz_at_full_mitigation"],
            cia_impact=info["cia_impact"],
            mitigation_cap=info["mitigation_cap"],
            allow_recovery=info["allow_recovery"],
        )
        for attack_id, info in raw["attacks"].items()
    }

    waves = []
    for wave in raw["waves"]:
        bonus_measures = [
            BonusMeasure(
                measure=bm["measure"],
                min_level=bm["min_level"],
                bonus=bm["bonus"],
                description=bm["description"],
            )
            for bm in wave.get("bonus_measures", [])
        ]
        waves.append(Wave(
            wave_id=wave["id"],
            name=wave["name"],
            attack_id=wave["attack_id"],
            weights=wave["weights"],
            e_threshold=wave.get("e_threshold", 18),
            bonus_measures=bonus_measures,
        ))

    measures = {}
    for measure_id, info in raw["measures"].items():
        levels = {
            int(level_id): MeasureLevel(
                cia=level_info["cia"],
                init=level_info["init"],
                opex=level_info["opex"],
                recovery=level_info.get("recovery", 0),
            )
            for level_id, level_info in info["levels"].items()
        }
        measures[measure_id] = Measure(
            measure_id=measure_id,
            name=info["name"],
            levels=levels,
            dependencies=info.get("dependencies", []),
        )

    # Load events per wave
    events = {}
    raw_events = raw.get("events", {})
    for wave_key, wave_events in raw_events.items():
        if wave_key.startswith("wave_"):
            wave_id = int(wave_key.split("_")[1])
            events[wave_id] = [_build_event(ev) for ev in wave_events]

    final_events = [_build_event(ev) for ev in raw.get("final_events", [])]

    return Config(
        default_budget_tier=raw["default_budget_tier"],
        budget_tiers=budget_tiers,
        attacks=attacks,
        waves=waves,
        measures=measures,
        events=events,
        base_cia=base_cia,
        final_events=final_events,
        ws=ws,
        rs=rs,
    )
