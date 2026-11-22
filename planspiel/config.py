import json
import warnings
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "simulation_config.json"


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


@dataclass
class Wave:
    wave_id: int
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
    type: str
    params: Dict


@dataclass
class Practice:
    """Welle 0 practice incident (D-12): read only by planspiel/practice.py, never by the real machinery."""

    kz_start: int
    budget: int
    attack: Attack
    wave: Wave
    event: Event
    selection: Dict[str, int]


@dataclass
class ScheduleBlock:
    id: str
    minutes: int
    wave: Optional[int] = None


@dataclass
class PrintRow:
    job: str
    per_team: int
    facilitator: int


@dataclass
class DebriefStage:
    id: str
    minutes: int


@dataclass
class SessionSchedule:
    """Session schedule and print list: read only by the facilitator print models (schedule, booklet, protocol) and
    the intro-deck test (persons_per_team), never by rules or enumeration."""

    total_minutes: int
    teams: int
    persons_per_team: int
    blocks: tuple[ScheduleBlock, ...]
    print_list: tuple[PrintRow, ...]
    debrief_stages: tuple[DebriefStage, ...] = ()
    pitch_seconds: Optional[int] = None


@dataclass
class RiskBand:
    """One € impact band of the risk matrix; `minimum` is the inclusive lower limit in thousand euros."""

    id: str
    minimum: int


@dataclass
class RiskCase:
    """One business case of the facilitator cheat sheet with its band id and its protection goal (c, i or a, printed
    next to the case; PROT-01, D-11); `like_attack` is a consistency anchor for the validator and tests and is never
    printed."""

    id: str
    band: str
    goal: str
    like_attack: Optional[str] = None


@dataclass
class RiskMatrix:
    """Rows of the register and of the protection-need table, € bands and cheat-sheet cases of the `risk_matrix` block
    (name kept per D-15): read only by the validator, print models and tests, never by rules or enumeration."""

    register_rows: int
    asset_rows: int
    bands: tuple[RiskBand, ...]
    cases: tuple[RiskCase, ...] = ()


@dataclass
class FinalIndexWeights:
    """Weights of the facilitator-side final index (D-23); the single source for reports and printed answer keys."""

    weight_kz: Fraction
    weight_ros: Fraction


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
    final_index: FinalIndexWeights
    session_schedule: Optional[SessionSchedule] = None
    risk_matrix: Optional[RiskMatrix] = None
    reference_plans: Dict[str, Dict] = field(default_factory=dict)
    reference_strategies: Dict[str, Dict] = field(default_factory=dict)
    practice: Optional[Practice] = None

    @property
    def measure_ids(self) -> List[str]:
        return list(self.measures)


def _build_attack(attack_id: str, info: Dict) -> Attack:
    return Attack(
        attack_id=attack_id,
        base_severity=info["base_severity"],
        s_unit=info["s_unit"],
        kz_at_full_damage=info["kz_at_full_damage"],
        kz_at_full_mitigation=info["kz_at_full_mitigation"],
        cia_impact=info["cia_impact"],
        mitigation_cap=info["mitigation_cap"],
        allow_recovery=info["allow_recovery"],
    )


def _build_wave(wave_id: int, attack_id: str, info: Dict) -> Wave:
    return Wave(
        wave_id=wave_id,
        attack_id=attack_id,
        weights=info["weights"],
        e_threshold=info.get("e_threshold", 18),
        bonus_measures=[
            BonusMeasure(measure=bm["measure"], min_level=bm["min_level"], bonus=bm["bonus"])
            for bm in info.get("bonus_measures", [])
        ],
    )


def _build_event(ev: Dict) -> Event:
    return Event(
        id=ev["id"],
        name=ev["name"],
        type=ev["type"],
        params={k: v for k, v in ev.items() if k not in ("id", "name", "type")},
    )


def read_raw_config(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"), parse_float=Fraction)


def check_config(raw: Dict, source: str, hand_calc_level: str = "error") -> None:
    from planspiel.validate import ConfigError, ConfigWarning, HandCalcWarning, validate

    issues = validate(raw, hand_calc_level=hand_calc_level)
    errors = [issue for issue in issues if issue.level == "error"]
    if errors:
        raise ConfigError(errors, source)
    for issue in issues:
        if issue.level == "warning":
            category = HandCalcWarning if issue.code.startswith("hand_calc.") else ConfigWarning
            warnings.warn(f"{issue.code} {issue.path}: {issue.message}", category, stacklevel=3)


def load_config(path: Path, hand_calc_level: str = "error") -> Config:
    """`hand_calc_level="warning"` loads a config whose only defects are hand-calc findings (for reports that judge them)."""
    raw = read_raw_config(path)
    check_config(raw, str(path), hand_calc_level)
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

    attacks = {attack_id: _build_attack(attack_id, info) for attack_id, info in raw["attacks"].items()}

    waves = [_build_wave(wave["id"], wave["attack_id"], wave) for wave in raw["waves"]]

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

    practice = None
    if "practice" in raw:
        block = raw["practice"]
        practice = Practice(
            kz_start=block["kz_start"],
            budget=block["budget"],
            attack=_build_attack("practice", block["attack"]),
            wave=_build_wave(0, "practice", block["wave"]),
            event=_build_event(block["event"]),
            selection=dict(block["selection"]),
        )

    session_schedule = None
    if "session_schedule" in raw:
        block = raw["session_schedule"]
        session_schedule = SessionSchedule(
            total_minutes=block["total_minutes"],
            teams=block["teams"],
            persons_per_team=block["persons_per_team"],
            blocks=tuple(
                ScheduleBlock(id=item["id"], minutes=item["minutes"], wave=item.get("wave"))
                for item in block["blocks"]
            ),
            print_list=tuple(
                PrintRow(job=item["job"], per_team=item["per_team"], facilitator=item["facilitator"])
                for item in block["print_list"]
            ),
            debrief_stages=tuple(
                DebriefStage(id=item["id"], minutes=item["minutes"]) for item in block.get("debrief_stages", [])
            ),
            pitch_seconds=block.get("pitch_seconds"),
        )

    risk_matrix = None
    if "risk_matrix" in raw:
        block = raw["risk_matrix"]
        risk_matrix = RiskMatrix(
            register_rows=block["register_rows"],
            asset_rows=block["asset_rows"],
            bands=tuple(RiskBand(id=item["id"], minimum=item["min"]) for item in block["bands"]),
            cases=tuple(
                RiskCase(id=item["id"], band=item["band"], goal=item["goal"], like_attack=item.get("like_attack"))
                for item in block.get("cases", [])
            ),
        )

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
        final_index=FinalIndexWeights(
            weight_kz=Fraction(raw["final_index"]["weight_kz"]),
            weight_ros=Fraction(raw["final_index"]["weight_ros"]),
        ),
        practice=practice,
        session_schedule=session_schedule,
        risk_matrix=risk_matrix,
        reference_plans=dict(raw.get("reference_plans", {})),
        reference_strategies=dict(raw.get("reference_strategies", {})),
    )
