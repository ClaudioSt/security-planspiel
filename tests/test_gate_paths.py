"""Move-path overspend gate (BAL-01, D-13): families, start-lowered trim, narrow diagnostic and calibration.

Families (WR-03): the swap layer (`tausch`), the mandatory swap followed by one voluntary window-2 move
(`tausch_fenster2`, the shape of the reference paths) and one move in window 1 or 2 (`fenster1`, `fenster2`) from the
starts where no swap is possible (D-22: everywhere else the swap is mandatory, so a move without it is illegal). Every
path of every family is evaluated with `enforce_kurswechsel=True`, so an illegal path would raise.

Trim definition of the path gate (research Q2): the trimmed versions of an over-budget path are all in-budget legal
paths whose START plan has only lowered or cancelled levels, followed by ANY legal continuation of the family's pool
(swap layer: legal pool; the move families: union pool of all four families).
The narrow definition (same swap pair, start and incoming level lowered) is a diagnostic and never enters the verdict.

Debrief sentence: "Hätte das Team zu Spielbeginn weniger oder niedrigere Maßnahmen gewählt, wäre es im Budget
geblieben und besser gelandet."

The brute force below builds every path of a family as a `rules.Path`, evaluates it with `rules.evaluate_path` and
never touches `TierTables`.
"""
import copy
import json
from array import array
from itertools import product

import pytest

from planspiel import gate, parallel, rules
from planspiel.cli import main
from planspiel.rounding import started_steps
from tests.support import REPO_ROOT, candidate, harness
from tests.support.golden import check_golden

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


def _digits(index, n):
    return [(index // 4 ** (n - 1 - j)) % 4 for j in range(n)]


def _below(lower, upper, n):
    return all(a <= b for a, b in zip(_digits(lower, n), _digits(upper, n)))


def _index(cfg, selection):
    return int(harness.code_of(cfg, selection), 4)


def _selection(cfg, index):
    return harness.selection_of(cfg, "".join(map(str, _digits(index, len(cfg.measures)))))


# ---------------------------------------------------------------------------------------------------------------
# synthetic pools on the n = 2 lattice
# ---------------------------------------------------------------------------------------------------------------


def _pool(entries, n=2):
    size = 4 ** n
    pool = array("i", [-1]) * size
    for start, final in entries:
        key = final * size + size - 1 - start
        if key > pool[start]:
            pool[start] = key
    gate.lowering_closure(pool, n)
    return pool


def _scan(over, n=2):
    scan = gate.PathScan(n)
    for start, steps, pre in over:
        scan.add_over(start, steps, pre)
    return scan


def _synthetic(entries, over, config_x=9, step=10, family="tausch"):
    return gate.path_gate_from_scan(
        _scan(over), _pool(entries), config_x, step, "synthetic", family, "legal"
    )


def test_synthetic_pool_names_the_start_lowered_path_when_x_is_too_low():
    result = _synthetic([(4, 80)], [(5, 1, 90)])
    assert result.min_x_strict == 11 and result.min_x_weak == 10 and result.min_x_capped == 11
    assert result.over_budget == 1 and result.unlosable == 0 and result.untrimmable == 0
    assert result.violations_at_config_x == 1 and result.passed is False
    assert result.x_histogram == {11: 1}
    assert result.witness["code"] == "11" and result.witness["trimmed_code"] == "10"
    assert result.witness["steps"] == 1 and result.witness["kz_pre_review"] == 90
    assert result.witness["required_x"] == 11 and result.witness["trimmed_kz_final"] == 80
    assert (result.tier, result.family, result.pool) == ("synthetic", "tausch", "legal")


def test_synthetic_pool_passes_when_x_is_large_enough():
    result = _synthetic([(4, 80)], [(5, 1, 90)], config_x=11)
    assert result.violations_at_config_x == 0 and result.passed is True


def test_synthetic_start_without_an_in_budget_path_below_it_is_untrimmable():
    result = _synthetic([(5, 80)], [(4, 1, 90), (5, 1, 70)])
    assert result.untrimmable == 1 and result.passed is False
    assert result.over_budget == 2
    assert result.x_histogram == {1: 1}


def test_synthetic_closed_pool_value_zero_is_unlosable():
    result = _synthetic([(4, 0)], [(5, 1, 90), (5, 2, 90)])
    assert result.unlosable == 2 and result.untrimmable == 0
    assert result.passed is False
    assert result.x_histogram == {} and result.witness is None
    assert result.min_x_strict == 1 and result.min_x_capped == 1


def test_synthetic_groups_keep_the_maximum_pre_review_per_start_and_steps():
    result = _synthetic([(0, 70)], [(5, 2, 80), (5, 2, 90), (5, 2, 85)])
    assert result.over_budget == 3
    assert result.x_histogram == {11: 1}
    assert result.min_x_strict == 11


def test_synthetic_trimmed_tie_names_the_lowest_start():
    result = _synthetic([(1, 70), (4, 70)], [(5, 1, 90)])
    assert result.witness["trimmed_code"] == "01"


def test_synthetic_without_over_budget_paths():
    result = _synthetic([(4, 80)], [])
    assert result.over_budget == 0 and result.passed is True
    assert result.min_x_strict == 1 and result.min_x_weak == 1 and result.min_x_capped == 1
    assert result.witness is None


@pytest.mark.parametrize(
    "pre, trimmed, steps, expected",
    [(91, 83, 1, 9), (89, 85, 2, 3), (85, 81, 1, 5), (80, 85, 1, 1), (100, 100, 1, 1), (100, 1, 3, 34)],
)
def test_capped_required_x_equals_the_strict_x_above_zero(pre, trimmed, steps, expected):
    assert gate.capped_required_x(pre, trimmed, steps) == expected
    assert gate.capped_required_x(pre, trimmed, steps) == gate.required_penalty_x(pre, trimmed, steps)


def test_capped_required_x_is_none_when_the_trimmed_version_ends_at_zero():
    assert gate.capped_required_x(90, 0, 1) is None


def test_capped_required_x_is_the_smallest_x_whose_clamped_outcome_loses():
    for pre, trimmed, steps in product(range(0, 101, 7), range(1, 101, 9), (1, 2, 5)):
        x = gate.capped_required_x(pre, trimmed, steps)
        assert x >= 1 and rules.clamp_kz(pre - x * steps) < trimmed
        assert x == 1 or rules.clamp_kz(pre - (x - 1) * steps) >= trimmed


def test_static_gate_carries_the_capped_minimum_last_and_does_not_serialize_it(mini):
    result = gate.gate_tier(mini, "low")
    assert gate.GateResult._fields[-1] == "min_x_capped"
    assert result.min_x_capped == result.min_x_strict
    assert "min_x_capped" not in gate.gate_result_json(result)


# ---------------------------------------------------------------------------------------------------------------
# brute force on the mini config
# ---------------------------------------------------------------------------------------------------------------


def _valid_starts(cfg):
    return [
        index
        for index in range(4 ** len(cfg.measures))
        if rules.dependencies_satisfied(_selection(cfg, index), cfg.measures)
    ]


def _legal_paths(cfg):
    """(start, rules.Path, enforce) of the swap layer: canonical swaps, exempt starts as static paths."""
    ids = cfg.measure_ids
    for start in _valid_starts(cfg):
        selection = _selection(cfg, start)
        if not rules.swap_possible(selection):
            yield start, None, rules.Path(selection), True
            continue
        for dropped, incoming, level in product(ids, ids, (1, 2, 3)):
            if selection[dropped] == 0 or selection[incoming] != 0:
                continue
            end = rules.swap_repair(selection, dropped, cfg.measures)
            end[incoming] = level
            if rules.dependencies_satisfied(end, cfg.measures):
                path = rules.Path(selection, (rules.Window(end, (dropped, incoming)),))
                yield start, (dropped, incoming, level), path, True


def _moves(cfg, selection):
    for measure, level in product(cfg.measure_ids, range(4)):
        if level == selection[measure]:
            continue
        target = dict(selection)
        target[measure] = level
        if rules.dependencies_satisfied(target, cfg.measures):
            yield target


def _swap_move_paths(cfg):
    """Every swap path of the swap layer followed by one voluntary move in window 2."""
    for start, swap, path, _enforce in _legal_paths(cfg):
        if swap is None:
            continue
        end = path.windows[0]
        for target in _moves(cfg, end.selection):
            yield start, swap, rules.Path(path.start, (end, rules.Window(target))), True


def _move_paths(cfg, window):
    ids = cfg.measure_ids
    for start in _valid_starts(cfg):
        selection = _selection(cfg, start)
        if rules.swap_possible(selection):
            continue
        for measure, level in product(ids, range(4)):
            if level == selection[measure]:
                continue
            target = dict(selection)
            target[measure] = level
            if not rules.dependencies_satisfied(target, cfg.measures):
                continue
            windows = (rules.Window(target),) if window == 1 else (rules.Window(selection), rules.Window(target))
            yield start, None, rules.Path(selection, windows), True


def _evaluate(cfg, tier, stream):
    out = []
    for start, swap, path, enforce in stream:
        rec = rules.evaluate_path(cfg, tier, path, enforce_kurswechsel=enforce)
        out.append(
            {
                "start": start,
                "swap": swap,
                "final": rec["kz_final"],
                "pre": rec["kz_pre_review"],
                "remaining": rec["costs"]["remaining"],
                "over": rec["over_budget"],
            }
        )
    return out


def _closed_pool(cfg, paths_lists):
    n = len(cfg.measures)
    best = {}
    for paths in paths_lists:
        for path in paths:
            if not path["over"]:
                best[path["start"]] = max(best.get(path["start"], -1), path["final"])
    return {
        start: max((final for lower, final in best.items() if _below(lower, start, n)), default=-1)
        for start in range(4 ** n)
    }


def _expected(cfg, over_paths, pool, config_x, step):
    untrimmable = unlosable = over = 0
    groups = {}
    for path in over_paths:
        if not path["over"]:
            continue
        over += 1
        trimmed = pool[path["start"]]
        if trimmed < 0:
            untrimmable += 1
        elif trimmed == 0:
            unlosable += 1
        else:
            key = (path["start"], started_steps(-path["remaining"], step))
            groups[key] = max(groups.get(key, -1), path["pre"])
    required = []
    histogram = {}
    for (start, steps), pre in groups.items():
        trimmed = pool[start]
        strict = gate.required_penalty_x(pre, trimmed, steps)
        weak = gate.required_penalty_x(pre, trimmed, steps, strict=False)
        histogram[strict] = histogram.get(strict, 0) + 1
        required.append((strict, weak, start, steps))
    min_strict = max((r[0] for r in required), default=1)
    witness = min((r for r in required if r[0] == min_strict), key=lambda r: (r[2], r[3]), default=None)
    return {
        "over_budget": over,
        "untrimmable": untrimmable,
        "unlosable": unlosable,
        "min_x_strict": min_strict,
        "min_x_weak": max((r[1] for r in required), default=1),
        "histogram": dict(sorted(histogram.items())),
        "violations": sum(1 for r in required if r[0] > config_x),
        "witness_start": None if witness is None else witness[2],
        "passed": config_x >= min_strict and unlosable == 0 and untrimmable == 0,
    }


def _mini_expected(cfg, tier):
    config_x, step = rules.penalty_params(cfg.final_events)
    legal = _evaluate(cfg, tier, _legal_paths(cfg))
    window1 = _evaluate(cfg, tier, _move_paths(cfg, 1))
    window2 = _evaluate(cfg, tier, _move_paths(cfg, 2))
    swap_move = _evaluate(cfg, tier, _swap_move_paths(cfg))
    legal_pool = _closed_pool(cfg, [legal])
    union_pool = _closed_pool(cfg, [legal, window1, window2, swap_move])
    return {
        "tausch": (legal, _expected(cfg, legal, legal_pool, config_x, step), len(legal)),
        "fenster1": (window1, _expected(cfg, window1, union_pool, config_x, step), len(window1)),
        "fenster2": (window2, _expected(cfg, window2, union_pool, config_x, step), len(window2)),
        "tausch_fenster2": (swap_move, _expected(cfg, swap_move, union_pool, config_x, step), len(swap_move)),
    }


_EXPECTED = {}


def _cached_expected(cfg, tier):
    if tier not in _EXPECTED:
        _EXPECTED[tier] = _mini_expected(cfg, tier)
    return _EXPECTED[tier]


_RESULT = {}


def _cached_result(cfg, tier, narrow=False):
    key = (tier, narrow)
    if key not in _RESULT:
        _RESULT[key] = gate.gate_paths_tier(cfg, tier, narrow=narrow)
    return _RESULT[key]


@pytest.mark.parametrize("family", gate.PATH_FAMILIES)
@pytest.mark.parametrize("tier", TIERS)
def test_mini_path_gate_equals_brute_force(mini, tier, family):
    paths, expected, count = _cached_expected(mini, tier)[family]
    result = _cached_result(mini, tier)[family]
    config_x, step = rules.penalty_params(mini.final_events)
    assert (result.tier, result.family) == (tier, family)
    assert result.pool == ("legal" if family == "tausch" else "union")
    assert (result.config_x, result.step) == (config_x, step)
    assert result.paths == count
    assert result.over_budget == expected["over_budget"]
    if family in ("tausch", gate.SWAP_MOVE_FAMILY):
        assert expected["over_budget"] > 0
    assert result.min_x_strict == expected["min_x_strict"]
    assert result.min_x_weak == expected["min_x_weak"]
    assert result.min_x_capped == expected["min_x_strict"]
    assert result.unlosable == expected["unlosable"]
    assert result.untrimmable == expected["untrimmable"]
    assert result.passed is expected["passed"]
    if family == gate.SWAP_MOVE_FAMILY:
        # Groups are counted on the Pareto front of the window-2 moves per window state: dominated moves never raise X
        # (gate docstring), so the histogram can hold fewer groups but has the same maximum.
        assert max(result.x_histogram, default=1) == max(expected["histogram"], default=1)
        assert sum(result.x_histogram.values()) <= sum(expected["histogram"].values())
        assert (result.violations_at_config_x > 0) is (expected["violations"] > 0)
        if expected["min_x_strict"] == 1:
            assert result.witness is None or result.witness["required_x"] == 1
            return
    else:
        assert result.x_histogram == expected["histogram"]
        assert result.violations_at_config_x == expected["violations"]
    if expected["witness_start"] is None:
        assert result.witness is None
    else:
        n = len(mini.measures)
        assert result.witness["code"] == "".join(map(str, _digits(expected["witness_start"], n)))
        assert result.witness["required_x"] == expected["min_x_strict"]


def test_window_families_skip_every_start_where_the_swap_is_mandatory(mini):
    tables = rules.TierTables(mini, "low")
    for start in range(len(tables.valid)):
        if tables.valid[start]:
            assert gate._swap_mandatory(tables, start) is rules.swap_possible(_selection(mini, start))


def test_path_gate_requires_a_rising_non_negative_budget_review(mini):
    falling = copy.deepcopy(mini)
    tiers = falling.final_events[0].params["tiers"]
    tiers[:] = [[minimum, -value] for minimum, value in tiers]
    with pytest.raises(ValueError, match="Budget-Review"):
        gate.gate_paths_tier(falling, "low")


def test_path_gate_requires_the_kurswechsel_in_the_first_wave(mini):
    late = copy.deepcopy(mini)
    first, second = sorted(late.events)[:2]
    kurswechsel = [event for event in late.events[first] if event.type == "kurswechsel"]
    assert kurswechsel
    late.events[first] = [event for event in late.events[first] if event.type != "kurswechsel"]
    late.events[second] = late.events[second] + kurswechsel
    with pytest.raises(ValueError, match="Kurswechsel"):
        gate.gate_paths_tier(late, "low")


def test_mini_path_gate_covers_every_family(mini):
    results = _cached_result(mini, "low")
    assert tuple(results) == gate.PATH_FAMILIES
    assert gate.NARROW_FAMILY not in results


def _brute_narrow(cfg, tier):
    config_x, step = rules.penalty_params(cfg.final_events)
    n = len(cfg.measures)
    legal = [p for p in _evaluate(cfg, tier, _legal_paths(cfg)) if p["swap"] is not None]
    ids = cfg.measure_ids
    over = 0
    histogram = {}
    untrimmable = unlosable = 0
    required = []
    for path in legal:
        if not path["over"]:
            continue
        over += 1
        dropped, incoming, level = path["swap"]
        candidates = [
            other["final"]
            for other in legal
            if not other["over"]
            and other["swap"][0] == dropped
            and other["swap"][1] == incoming
            and other["swap"][2] <= level
            and _below(other["start"], path["start"], n)
        ]
        if not candidates:
            untrimmable += 1
            continue
        trimmed = max(candidates)
        if trimmed == 0:
            unlosable += 1
            continue
        steps = started_steps(-path["remaining"], step)
        strict = gate.required_penalty_x(path["pre"], trimmed, steps)
        weak = gate.required_penalty_x(path["pre"], trimmed, steps, strict=False)
        histogram[strict] = histogram.get(strict, 0) + 1
        required.append((strict, weak))
    return {
        "paths": len(legal),
        "over_budget": over,
        "untrimmable": untrimmable,
        "unlosable": unlosable,
        "min_x_strict": max((r[0] for r in required), default=1),
        "min_x_weak": max((r[1] for r in required), default=1),
        "histogram": dict(sorted(histogram.items())),
        "violations": sum(1 for r in required if r[0] > config_x),
        "config_x": config_x,
        "ids": ids,
    }


@pytest.mark.parametrize("tier", TIERS)
def test_mini_narrow_diagnostic_equals_brute_force(mini, tier):
    expected = _brute_narrow(mini, tier)
    results = _cached_result(mini, tier, narrow=True)
    assert tuple(results) == gate.PATH_FAMILIES + (gate.NARROW_FAMILY,)
    narrow = results[gate.NARROW_FAMILY]
    assert narrow.pool == "same_pair"
    assert narrow.paths == expected["paths"]
    assert narrow.over_budget == expected["over_budget"]
    assert narrow.untrimmable == expected["untrimmable"]
    assert narrow.unlosable == expected["unlosable"]
    assert narrow.min_x_strict == expected["min_x_strict"]
    assert narrow.min_x_weak == expected["min_x_weak"]
    assert narrow.x_histogram == expected["histogram"]
    assert narrow.violations_at_config_x == expected["violations"]
    assert narrow.passed is (
        expected["config_x"] >= expected["min_x_strict"]
        and expected["unlosable"] == 0
        and expected["untrimmable"] == 0
    )
    for family in gate.PATH_FAMILIES:
        assert results[family] == _cached_result(mini, tier)[family]


# ---------------------------------------------------------------------------------------------------------------
# calibration
# ---------------------------------------------------------------------------------------------------------------


def _static(tier, strict, capped=None, config_x=9, passed=True, unlosable=0):
    return gate.GateResult(
        tier=tier, layer="referenz", config_x=config_x, step=10, over_budget=5, min_x_strict=strict,
        min_x_weak=strict, x_histogram={strict: 1}, witness=None, unlosable=unlosable, untrimmable=0,
        violations_at_config_x=0, passed=passed, min_x_capped=strict if capped is None else capped,
    )


def _family(tier, family, strict, capped=None, config_x=9, passed=True, unlosable=0):
    return gate.PathGateResult(
        tier=tier, family=family, pool="legal", config_x=config_x, step=10, paths=10, over_budget=4,
        min_x_strict=strict, min_x_capped=strict if capped is None else capped, min_x_weak=strict,
        x_histogram={strict: 1}, witness=None, unlosable=unlosable, untrimmable=0,
        violations_at_config_x=0, passed=passed,
    )


def _families(tier, tausch, fenster1, fenster2):
    return {
        "tausch": _family(tier, "tausch", tausch),
        "fenster1": _family(tier, "fenster1", fenster1),
        "fenster2": _family(tier, "fenster2", fenster2),
    }


def test_calibrate_recommends_the_maximum_plus_one_and_names_the_binding_cell():
    static = {"low": _static("low", 9), "medium": _static("medium", 5), "high": _static("high", 3)}
    paths = {
        "low": _families("low", 9, 9, 5),
        "medium": _families("medium", 5, 5, 2),
        "high": _families("high", 2, 3, 1),
    }
    cal = gate.calibrate(static, paths)
    assert cal.recommended_x == 10
    assert (cal.max_min_x_raw, cal.max_min_x_capped) == (9, 9)
    assert (cal.binding_tier, cal.binding_family, cal.binding_kind) == ("low", "statisch", "roh")
    assert cal.config_x == 9 and cal.calibrated is False
    assert cal.within_target is False and cal.passed_all is True and cal.unlosable_total == 0


def test_calibrate_names_a_path_family_when_it_binds():
    static = {"low": _static("low", 4)}
    paths = {"low": _families("low", 4, 7, 5)}
    cal = gate.calibrate(static, paths)
    assert cal.recommended_x == 8
    assert (cal.binding_tier, cal.binding_family) == ("low", "fenster1")


def test_calibrate_uses_the_capped_minimum_when_it_is_larger():
    static = {"low": _static("low", 4, capped=6)}
    paths = {"low": _families("low", 4, 4, 4)}
    cal = gate.calibrate(static, paths)
    assert (cal.max_min_x_raw, cal.max_min_x_capped, cal.recommended_x) == (4, 6, 7)
    assert (cal.binding_family, cal.binding_kind) == ("statisch", "gekappt")


def test_calibrate_is_calibrated_when_the_config_x_equals_the_recommendation():
    static = {"low": _static("low", 4, config_x=5)}
    paths = {"low": _families("low", 4, 3, 2)}
    cal = gate.calibrate(static, paths)
    assert cal.recommended_x == 5 and cal.calibrated is True
    assert cal.within_target is True
    assert gate.calibrate(static, paths, x_target=4).within_target is False


def test_calibrate_ignores_the_narrow_family_and_counts_unlosable_paths():
    static = {"low": _static("low", 4)}
    families = _families("low", 4, 3, 2)
    families[gate.NARROW_FAMILY] = _family("low", gate.NARROW_FAMILY, 14, passed=False)
    cal = gate.calibrate(static, {"low": families})
    assert cal.recommended_x == 5 and cal.passed_all is True
    families["fenster2"] = _family("low", "fenster2", 2, unlosable=3, passed=False)
    cal = gate.calibrate(static, {"low": families})
    assert cal.unlosable_total == 3 and cal.passed_all is False


def test_x_target_is_the_design_goal():
    assert gate.X_TARGET == 5
    assert gate.PATH_FAMILIES == ("tausch", "fenster1", "fenster2", "tausch_fenster2")
    assert gate.SWAP_MOVE_FAMILY == "tausch_fenster2"
    assert gate.NARROW_FAMILY == "tausch_eng"
    assert set(gate.PATH_LABELS) == set(gate.PATH_FAMILIES) | {gate.NARROW_FAMILY}


def test_json_key_order_is_fixed(mini):
    results = _cached_result(mini, "low")
    data = gate.gate_paths_result_json(results["tausch"])
    assert list(data) == [
        "tier", "family", "pool", "config_x", "step", "paths", "over_budget", "min_x_strict", "min_x_capped",
        "min_x_weak", "x_histogram", "witness", "unlosable", "untrimmable", "violations_at_config_x", "passed",
    ]
    assert list(data["x_histogram"]) == [str(x) for x in sorted(results["tausch"].x_histogram)]
    assert gate.gate_paths_result_json(results["tausch"]) == data
    json.dumps(data)

    static = {t: gate.gate_tier(mini, t) for t in ("low",)}
    cal = gate.calibrate(static, {"low": results})
    out = gate.calibration_json(cal)
    assert list(out) == [
        "config_x", "x_target", "max_min_x_raw", "max_min_x_capped", "recommended_x", "binding_tier",
        "binding_family", "binding_kind", "calibrated", "within_target", "passed_all", "unlosable_total",
        "static_min_x_capped",
    ]
    assert out["static_min_x_capped"] == {"low": static["low"].min_x_capped}
    json.dumps(out)


def test_reports_are_german_and_name_raw_and_capped(mini):
    results = _cached_result(mini, "low")
    text = gate.format_path_gate_report(results["tausch"])
    assert "Tier low" in text and gate.PATH_LABELS["tausch"] in text
    assert "roh" in text and "gekappt" in text
    assert text.rstrip().endswith("bestanden") or text.rstrip().endswith("NICHT bestanden")
    static = {"low": gate.gate_tier(mini, "low")}
    cal = gate.calibrate(static, {"low": results})
    report = gate.format_calibration(cal)
    assert "Empfohlenes X = Maximum + 1" in report
    assert "bestimmend: Tier" in report
    assert gate.UNCOVERED_SHAPES in report
    assert "Startplan" in gate.__doc__ and "A1" in gate.__doc__


def test_paths_worker_returns_the_static_gate_and_the_path_families(mini):
    static, families = gate.paths_worker(str(MINI), "low")
    assert static == gate.gate_tier(mini, "low")
    assert tuple(families) == gate.PATH_FAMILIES
    static, families = gate.paths_worker(str(MINI), "low", narrow=True)
    assert gate.NARROW_FAMILY in families


# ---------------------------------------------------------------------------------------------------------------
# planspiel gate --paths
# ---------------------------------------------------------------------------------------------------------------


def _run(capsys, *args):
    code = main(["gate", "--config", str(MINI), *args])
    return code, capsys.readouterr().out


def test_gate_paths_prints_static_families_and_calibration(capsys):
    code, out = _run(capsys, "--paths")
    assert code == 0
    for tier in TIERS:
        assert f"Überziehungs-Gate, Tier {tier}: " in out
        for family in gate.PATH_FAMILIES:
            assert f"Überziehungs-Gate, Tier {tier}, Pfade: {gate.PATH_LABELS[family]}" in out
    assert gate.PATH_LABELS[gate.NARROW_FAMILY] not in out
    assert "Empfohlenes X = Maximum + 1" in out
    assert out.rstrip().endswith("Überziehungs-Gate: bestanden")


def test_gate_paths_on_a_subset_of_tiers_does_not_calibrate(capsys):
    code, out = _run(capsys, "--paths", "--tier", "low")
    assert code == 0
    assert "Empfohlenes X" not in out
    assert "Kalibrierung von X: nicht berechnet (nur über alle Tiers)" in out
    assert out.rstrip().endswith("Überziehungs-Gate: bestanden")


def test_gate_paths_exit_code_follows_the_static_and_family_verdicts(capsys, tmp_path):
    text = MINI.read_text(encoding="utf-8").replace('"kz_per_step": 9', '"kz_per_step": 1')
    assert text != MINI.read_text(encoding="utf-8")
    low_x_config = tmp_path / "x1.json"
    low_x_config.write_text(text, encoding="utf-8")
    code = main(["gate", "--config", str(low_x_config), "--paths"])
    out = capsys.readouterr().out
    assert code == 1
    assert out.rstrip().endswith("Überziehungs-Gate: NICHT bestanden")
    assert "nicht kalibriert" in out


def test_gate_paths_narrow_adds_the_diagnostic_without_changing_the_exit_code(capsys):
    code, plain = _run(capsys, "--paths")
    code_narrow, narrow = _run(capsys, "--paths", "--narrow")
    assert code_narrow == code
    assert gate.PATH_LABELS[gate.NARROW_FAMILY] in narrow
    assert narrow.count("Pfade: " + gate.PATH_LABELS[gate.NARROW_FAMILY]) == len(TIERS)


def test_gate_narrow_without_paths_is_a_parser_error(capsys):
    with pytest.raises(SystemExit) as raised:
        main(["gate", "--config", str(MINI), "--narrow"])
    assert raised.value.code == 2
    assert "--paths" in capsys.readouterr().err


def test_gate_paths_jobs_do_not_change_the_output(capsys):
    _, serial = _run(capsys, "--paths", "--jobs", "1")
    _, pooled = _run(capsys, "--paths", "--jobs", "2")
    assert serial == pooled


def test_gate_without_paths_output_is_the_static_report_only(capsys, mini):
    code, out = _run(capsys)
    expected = ""
    for tier in TIERS:
        expected += gate.format_gate_report(gate.gate_tier(mini, tier)) + "\n\n"
    expected += "Überziehungs-Gate: bestanden\n"
    assert code == 0
    assert out == expected


# ---------------------------------------------------------------------------------------------------------------
# slow checks on the configured (real or candidate) config
# ---------------------------------------------------------------------------------------------------------------

_BALANCE = {}


def _balance_results(path):
    key = str(path)
    if key not in _BALANCE:
        names = list(candidate.load_balance_config(path).budget_tiers)
        _BALANCE[key] = parallel.map_tiers(gate.paths_worker, path, names, jobs=3)
    return _BALANCE[key]


@pytest.mark.slow
@pytest.mark.balance
def test_every_path_family_passes_at_config_x(balance_config_path):
    for tier, (static, families) in _balance_results(balance_config_path).items():
        assert static.passed, gate.format_gate_report(static)
        for family, result in families.items():
            assert result.passed, gate.format_path_gate_report(result)


@pytest.mark.slow
@pytest.mark.balance
def test_config_x_is_calibrated(balance_config_path):
    results = _balance_results(balance_config_path)
    cal = gate.calibrate({t: r[0] for t, r in results.items()}, {t: r[1] for t, r in results.items()})
    assert cal.calibrated, gate.format_calibration(cal)


@pytest.mark.slow
@pytest.mark.balance
@pytest.mark.parametrize("tier", TIERS)
def test_path_gate_matches_golden(tier, update_golden, golden_report):
    static, families = _balance_results(candidate.resolve_config_path(None))[tier]
    payload = {
        "static": gate.gate_result_json(static),
        "families": {family: gate.gate_paths_result_json(result) for family, result in families.items()},
    }
    check_golden(REPO_ROOT / "tests" / "golden" / f"gate_paths_{tier}.json", payload, update_golden, golden_report)
