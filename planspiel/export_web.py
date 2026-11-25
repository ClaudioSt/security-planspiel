"""WEB-01: export of config and golden cases for the TypeScript engine of the web app (`planspiel export-web`).

The web app (repo security-planspiel-web) ports `planspiel/rules.py` to TypeScript. This module writes
- `config.json`: `simulation_config.json` with every non-integral number as an exact string (`exact_to_json`),
- `golden.json`: game paths with the full `rules.path_trace` (or the expected `PathError` reason), the Final-Index and
  the worksheet constants per wave; the TS engine must reproduce every value exactly,
- `manifest.json`: schema, config hash and source commit.

Nothing here computes a game formula: every value comes from `planspiel.rules` (FOUND-03). The case selection is
deterministic: reference plans and strategies, the clue measures at their minimum level, an index-stride sample of
static plans and of Kurswechsel paths, and every candidate that adds a branch not yet covered (case per wave,
clamping, event outcomes, budget review bands and overspend steps).
"""
import hashlib
import itertools
import json
import subprocess
from fractions import Fraction
from pathlib import Path as FsPath
from typing import Dict, Iterable, List, Optional, Tuple

from planspiel import rules
from planspiel.config import Config, load_config, read_raw_config
from planspiel.rounding import exact_to_json

SCHEMA = 1
LEVELS = (0, 1, 2, 3)
STATIC_STRIDE = 1009
SWAP_STRIDE = 4999
BULK_PER_TIER = 40


def _jsonable(value):
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, (int, Fraction)):
        return exact_to_json(value)
    if hasattr(value, "_asdict"):
        return {key: _jsonable(item) for key, item in value._asdict().items()}
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    raise TypeError(f"not exportable: {value!r}")


def golden_path(data: Dict) -> rules.Path:
    """Path object from the JSON form of a golden case."""
    return rules.Path(
        start=dict(data["start"]),
        windows=tuple(
            rules.Window(dict(window["selection"]), tuple(window["swap"]) if window.get("swap") else None)
            for window in data.get("windows", [])
        ),
    )


def _path_json(path: rules.Path) -> Dict:
    return {
        "start": dict(path.start),
        "windows": [
            {"selection": dict(window.selection), "swap": list(window.swap) if window.swap else None}
            for window in path.windows
        ],
    }


def _path_from_config(entry: Dict) -> rules.Path:
    return golden_path({"start": entry["start"], "windows": entry.get("windows", [])})


def _case(cfg: Config, case_id: str, tier: str, path: rules.Path, enforce: bool) -> Dict:
    case = {"id": case_id, "tier": tier, "enforce_kurswechsel": enforce, "path": _path_json(path)}
    try:
        trace = rules.path_trace(cfg, tier, path, enforce_kurswechsel=enforce)
    except rules.PathError as error:
        case["expect"] = {"error": error.reason}
        return case
    ros = trace.review.ros
    case["expect"] = {
        "trace": _jsonable(trace),
        "ros2": None if ros is None else exact_to_json(rules.ros_two_decimals(ros)),
        "final_index": exact_to_json(
            rules.final_index(trace.review.kz_final, ros, cfg.final_index.weight_kz, cfg.final_index.weight_ros)
        ),
    }
    return case


def _features(case: Dict) -> set:
    trace = case["expect"].get("trace")
    if trace is None:
        return {("error", case["expect"]["error"])}
    found = set()
    for wave in trace["waves"]:
        wid = wave["wave_id"]
        found.add(("case", wid, wave["case"]))
        exact = Fraction(str(wave["kz_change_exact"]))
        if exact.denominator == 2:
            found.add(("half", exact > 0))
        if wave["kz_unclamped"] != wave["kz_after"]:
            found.add(("clamp", wave["kz_after"]))
        if Fraction(str(wave["recovery_factor"])):
            found.add(("recovery", wid, str(wave["recovery_factor"])))
        for event in wave["events"]:
            found.add(("event", event["id"], event["kz_delta"], event["opex_delta"], event["budget_delta"]))
    review = trace["review"]
    found.add(("review", review["kz_review_change"]))
    found.add(("over_budget", review["over_budget"]))
    found.add(("ros_none", review["ros"] is None))
    for window in trace["windows"]:
        found.add(("swap", window["swap"] is not None, window["credit_k"] > 0))
    return found


def _selection(ids: List[str], levels: Iterable[int]) -> Dict[str, int]:
    return dict(zip(ids, levels))


def _static_candidates(cfg: Config) -> List[Dict[str, int]]:
    ids = cfg.measure_ids
    found = []
    for index, levels in enumerate(itertools.product(LEVELS, repeat=len(ids))):
        if index % STATIC_STRIDE:
            continue
        selection = _selection(ids, levels)
        if rules.dependencies_satisfied(selection, cfg.measures):
            found.append(selection)
    return found


def _swap_candidates(cfg: Config) -> List[rules.Path]:
    """Kurswechsel paths: per sampled start up to three legal swaps (canonical repair, D-28), the third with a
    single-measure move in the second window."""
    ids = cfg.measure_ids
    paths = []
    for index, levels in enumerate(itertools.product(LEVELS, repeat=len(ids))):
        if index % SWAP_STRIDE:
            continue
        start = _selection(ids, levels)
        if not rules.dependencies_satisfied(start, cfg.measures) or not rules.swap_possible(start):
            continue
        made = 0
        for dropped in ids:
            if start[dropped] == 0 or made >= 3:
                continue
            repaired = rules.swap_repair(start, dropped, cfg.measures)
            for incoming in ids:
                if start[incoming] != 0 or made >= 3:
                    continue
                level = 1 + (index + made) % 3
                window = dict(repaired, **{incoming: level})
                if not rules.dependencies_satisfied(window, cfg.measures):
                    continue
                windows = [rules.Window(window, (dropped, incoming))]
                if made == 2:
                    moved = _single_move(cfg, window)
                    if moved is not None:
                        windows.append(rules.Window(moved))
                paths.append(rules.Path(start, tuple(windows)))
                made += 1
                break
    return paths


def _single_move(cfg: Config, selection: Dict[str, int]) -> Optional[Dict[str, int]]:
    for measure_id in cfg.measure_ids:
        for level in (selection[measure_id] + 1, selection[measure_id] - 1):
            if level in cfg.measures[measure_id].levels:
                moved = dict(selection, **{measure_id: level})
                if rules.dependencies_satisfied(moved, cfg.measures):
                    return moved
    return None


def _clue_measures_min_level(cfg: Config) -> Dict[str, int]:
    """Every wave's bonus measure at its minimum level, everything else off (the plan a clue-following team makes)."""
    selection = {measure_id: 0 for measure_id in cfg.measure_ids}
    for wave in cfg.waves:
        for bonus in wave.bonus_measures:
            selection[bonus.measure] = max(selection[bonus.measure], bonus.min_level)
    return selection


def _error_cases(cfg: Config, tier: str) -> List[Tuple[str, rules.Path, bool]]:
    ids = cfg.measure_ids
    off = {measure_id: 0 for measure_id in ids}
    some = dict(off, **{ids[0]: 1})
    dependent = next(
        (measure_id, dependency["level"])
        for measure_id, measure in cfg.measures.items()
        for dependency in measure.dependencies
    )
    missing = dict(off)
    del missing[ids[-1]]
    inactive_drop = dict(off, **{ids[1]: 1})
    return [
        ("unknown_measure", rules.Path(missing), False),
        ("level_range", rules.Path(dict(off, **{ids[0]: max(LEVELS) + 1})), False),
        ("dependencies", rules.Path(dict(off, **{dependent[0]: dependent[1]})), False),
        ("too_many_windows", rules.Path(off, tuple(rules.Window(off) for _ in cfg.waves)), False),
        ("kurswechsel_missing", rules.Path(some), True),
        ("kurswechsel_illegal", rules.Path(some, (rules.Window(inactive_drop, (ids[2], ids[1])),)), True),
        (
            "swap_without_kurswechsel",
            rules.Path(off, (rules.Window(off), rules.Window(off, (ids[0], ids[1])))),
            False,
        ),
    ]


def build_golden(cfg: Config) -> Dict:
    cases: List[Dict] = []
    seen: set = set()

    def add(case: Dict, force: bool) -> None:
        features = _features(case)
        if force or not features <= seen:
            seen.update(features)
            cases.append(case)

    for tier, entry in cfg.reference_plans.items():
        add(_case(cfg, f"reference_plan.{tier}", tier, _path_from_config(entry), True), True)
    for tier, strategies in cfg.reference_strategies.items():
        for name, entry in strategies.items():
            add(_case(cfg, f"reference_strategy.{tier}.{name}", tier, _path_from_config(entry), True), True)
    for tier in cfg.budget_tiers:
        clue_path = rules.Path(_clue_measures_min_level(cfg))
        add(_case(cfg, f"clue_measures_min_level.{tier}", tier, clue_path, False), True)
    for reason, path, enforce in _error_cases(cfg, cfg.default_budget_tier):
        add(_case(cfg, f"error.{reason}", cfg.default_budget_tier, path, enforce), True)

    statics = _static_candidates(cfg)
    swaps = _swap_candidates(cfg)
    for tier in cfg.budget_tiers:
        for number, selection in enumerate(statics):
            case = _case(cfg, f"static.{tier}.{number}", tier, rules.Path(selection), False)
            add(case, number % max(1, len(statics) // BULK_PER_TIER) == 0)
        for number, path in enumerate(swaps):
            case = _case(cfg, f"kurswechsel.{tier}.{number}", tier, path, True)
            add(case, number % max(1, len(swaps) // BULK_PER_TIER) == 0)

    worksheets = {str(wave.wave_id): _jsonable(rules.worksheet_constants(cfg, wave)) for wave in cfg.waves}
    return {"schema": SCHEMA, "worksheet_constants": worksheets, "rounding": _rounding_table(), "cases": cases}


def _rounding_table() -> List[Dict]:
    """round_half_away on exact halves and neighbours of both signs: the current config never lands a wave on an
    exact half, so the engine's rounding is pinned by this table."""
    from planspiel.rounding import round_half_away

    pairs = [(n, d) for d in (1, 2, 4, 5, 10) for n in range(-31, 32)]
    return [{"n": n, "d": d, "result": round_half_away(n, d)} for n, d in pairs]


def _source_commit(repo: FsPath) -> Optional[str]:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"], cwd=repo, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return sha or None


def build_export(config_path: FsPath) -> Dict[str, Dict]:
    config_path = FsPath(config_path)
    cfg = load_config(config_path)
    golden = build_golden(cfg)
    manifest = {
        "schema": SCHEMA,
        "generated_by": "planspiel export-web",
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "source_commit": _source_commit(config_path.parent),
        "golden_cases": len(golden["cases"]),
    }
    return {"config.json": _jsonable(read_raw_config(config_path)), "golden.json": golden, "manifest.json": manifest}


def write_export(config_path: FsPath, out_dir: FsPath) -> Dict[str, Dict]:
    out_dir = FsPath(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    export = build_export(config_path)
    for name, data in export.items():
        text = json.dumps(data, ensure_ascii=False, indent=None if name == "golden.json" else 2, sort_keys=False)
        (out_dir / name).write_text(text + "\n", encoding="utf-8", newline="\n")
    return export
