"""Überziehungs-Gate (RULE-04, D-17, BAL-01): Überziehen lohnt sich nie.

Debriefing-Satz: "Wer am Ende über Budget liegt, hätte mit dem besten Paket, das nur durch Senken oder
Kündigen von Leveln entsteht und im Budget bleibt, immer eine höhere End-KZ erreicht."

Das statische Gate arbeitet auf dem Referenzplan ohne Change-Fenster-Züge (D-24, D-25). Je Plan über Budget wird die
gekürzte Version gesucht: der beste Plan im Budget, dessen Level alle <= denen des Plans sind (inkl. positiver
Budget-Review-Stufe). Das nötige X je Plan ist die kleinste ganze Zahl, bei der der Plan strikt verliert.
Das Gate liest nur Spalten des Ergebnisspeichers und `rules.penalty_params`, nie Formel-Operanden.

Pfad-Gate (D-13, BAL-01; Phase-2-D-25 zurückgestellt): dieselbe Frage für legale Spielpfade, in den Familien
`tausch` (Tausch-Schicht, legales Minimum), `fenster1` und `fenster2` (je ein Zug im Fenster nach Welle 1 oder 2, ohne
Tausch). Gekürzte Version eines Pfads über Budget = Startplan mit nur gesenkten oder gekündigten Leveln, danach jede
legale Fortsetzung des Pools der Familie (Tausch-Schicht: legaler Pool; Fenster: Vereinigung aus statischem Pfad,
Tausch-Schicht und beiden Zug-Familien). Debriefing: "Hätte das Team zu Spielbeginn weniger oder niedrigere Maßnahmen
gewählt, wäre es im Budget geblieben und besser gelandet." Die enge Kürzung (gleiches Tauschpaar) ist nur eine
Diagnose (`tausch_eng`) und geht nie in das Urteil oder die Kalibrierung ein.

Kalibrierung (D-13): X = größtes nötiges X über alle Tiers und Familien + 1. Roh und gekappt werden beide gemeldet
(Annahme A1 der Phase-6-Recherche, am Checkpoint D-04 zu bestätigen): roh = Strafe ohne Untergrenze
(KZ vor Review - X * Schritte), gekappt = nach der Strafe auf 0..100 begrenzt (`rules.clamp_kz`, wie das Budget
Review). Endet die gekürzte Version bei KZ 0, gibt es kein endliches gekapptes X; solche Pfade zählen als
"nicht verlierbar".
"""
from array import array
from pathlib import Path
from typing import Dict, NamedTuple, Optional

from planspiel import rules
from planspiel.enumerate import code_from_index, enumerate_tier
from planspiel.report import REFERENCE_LABEL, REFERENCE_LAYER
from planspiel.rounding import started_steps

LEVELS = 4

PATH_FAMILIES = ("tausch", "fenster1", "fenster2")
NARROW_FAMILY = "tausch_eng"
STATIC_FAMILY = "statisch"
X_TARGET = 5
PATH_LABELS = {
    "tausch": "Tausch-Schicht (Pflicht-Maßnahmentausch, legales Minimum)",
    "fenster1": "ein Zug im Fenster nach Welle 1 (ohne Tausch)",
    "fenster2": "ein Zug im Fenster nach Welle 2 (ohne Tausch)",
    NARROW_FAMILY: "Tausch-Schicht, enge Kürzung (gleiches Tauschpaar)",
}
POOL_OF = {"tausch": "legal", "fenster1": "union", "fenster2": "union", NARROW_FAMILY: "same_pair"}


class GateResult(NamedTuple):
    tier: str
    layer: str
    config_x: int
    step: int
    over_budget: int
    min_x_strict: int
    min_x_weak: int
    x_histogram: Dict[int, int]
    witness: Optional[Dict]
    unlosable: int
    untrimmable: int
    violations_at_config_x: int
    passed: bool
    min_x_capped: Optional[int] = None


def lowering_closure(best: array, n: int) -> None:
    """Präfix-Maximum über das 4^n-Gitter: danach ist best[i] das Maximum von best[j] über alle j <= i
    (komponentenweise; Maßnahme 0 ist die höchstwertige Stelle)."""
    size = LEVELS**n
    for j in range(n):
        stride = LEVELS ** (n - 1 - j)
        for i in range(stride, size):
            if (i // stride) % LEVELS:
                lower = best[i - stride]
                if lower > best[i]:
                    best[i] = lower


def required_penalty_x(kz_pre_review: int, trimmed_final: int, steps: int, strict: bool = True) -> int:
    gap = kz_pre_review - trimmed_final
    if strict:
        return max(1, gap // steps + 1)
    return max(1, -(-gap // steps))


def capped_required_x(kz_pre_review: int, trimmed_final: int, steps: int) -> Optional[int]:
    """Kleinstes X >= 1, bei dem die nach der Strafe auf 0..100 begrenzte KZ strikt unter der gekürzten Version endet;
    None, wenn diese bei KZ 0 endet (dann gibt es kein endliches X)."""
    if trimmed_final <= 0:
        return None
    x = required_penalty_x(kz_pre_review, trimmed_final, steps)
    while rules.clamp_kz(kz_pre_review - x * steps) >= trimmed_final:
        x += 1
    while x > 1 and rules.clamp_kz(kz_pre_review - (x - 1) * steps) < trimmed_final:
        x -= 1
    return x


def trim_keys(n_measures: int, code_index, kz_final, over_budget) -> array:
    """Schlüssel kz_final * 4^n + (4^n - 1 - Code) der besten gekürzten Version je Gitterpunkt, -1 ohne eine."""
    size = LEVELS**n_measures
    best = array("i", [-1]) * size
    for row in range(len(code_index)):
        if not over_budget[row]:
            code = code_index[row]
            best[code] = kz_final[row] * size + (size - 1 - code)
    lowering_closure(best, n_measures)
    return best


def gate_from_columns(
    n_measures: int,
    code_index,
    kz_final,
    kz_pre_review,
    remaining,
    over_budget,
    config_x: int,
    step: int,
    tier_name: str = "",
) -> GateResult:
    size = LEVELS**n_measures
    best = trim_keys(n_measures, code_index, kz_final, over_budget)
    row_of_code = array("i", [-1]) * size
    for row in range(len(code_index)):
        if not over_budget[row]:
            row_of_code[code_index[row]] = row

    over_count = 0
    unlosable = 0
    untrimmable = 0
    violations = 0
    min_strict = 1
    min_weak = 1
    min_capped = 1
    histogram: Dict[int, int] = {}
    witness_row = None
    witness_key = None
    for row in range(len(code_index)):
        if not over_budget[row]:
            continue
        over_count += 1
        code = code_index[row]
        key = best[code]
        if key < 0:
            untrimmable += 1
            continue
        trimmed_final = key // size
        if kz_final[row] >= trimmed_final:
            violations += 1
        if trimmed_final == 0:
            unlosable += 1
            continue
        steps = started_steps(-remaining[row], step)
        strict_x = required_penalty_x(kz_pre_review[row], trimmed_final, steps)
        weak_x = required_penalty_x(kz_pre_review[row], trimmed_final, steps, strict=False)
        min_capped = max(min_capped, capped_required_x(kz_pre_review[row], trimmed_final, steps))
        histogram[strict_x] = histogram.get(strict_x, 0) + 1
        min_weak = max(min_weak, weak_x)
        if witness_key is None or (strict_x, -code) > witness_key:
            witness_key = (strict_x, -code)
            witness_row = row
        min_strict = max(min_strict, strict_x)

    witness = None
    if witness_row is not None:
        code = code_index[witness_row]
        trimmed_code = size - 1 - best[code] % size
        trimmed_row = row_of_code[trimmed_code]
        witness = {
            "code": code_from_index(code, n_measures),
            "remaining": remaining[witness_row],
            "steps": started_steps(-remaining[witness_row], step),
            "kz_pre_review": kz_pre_review[witness_row],
            "kz_final": kz_final[witness_row],
            "required_x": witness_key[0],
            "trimmed_code": code_from_index(trimmed_code, n_measures),
            "trimmed_kz_final": kz_final[trimmed_row],
            "trimmed_remaining": remaining[trimmed_row],
        }
    passed = config_x >= min_strict and unlosable == 0 and untrimmable == 0 and violations == 0
    return GateResult(
        tier=tier_name,
        layer=REFERENCE_LAYER,
        config_x=config_x,
        step=step,
        over_budget=over_count,
        min_x_strict=min_strict,
        min_x_weak=min_weak,
        x_histogram=dict(sorted(histogram.items())),
        witness=witness,
        unlosable=unlosable,
        untrimmable=untrimmable,
        violations_at_config_x=violations,
        passed=passed,
        min_x_capped=min_capped,
    )


def gate_tier(cfg, tier_name: str, store=None) -> GateResult:
    if store is None:
        store = enumerate_tier(cfg, tier_name)
    config_x, step = rules.penalty_params(cfg.final_events)
    return gate_from_columns(
        len(cfg.measure_ids),
        store.column("code_index"),
        store.column("kz_final"),
        store.column("kz_pre_review"),
        store.column("remaining"),
        store.column("over_budget"),
        config_x,
        step,
        tier_name=tier_name,
    )


def gate_result_json(result: GateResult) -> Dict:
    return {
        "tier": result.tier,
        "layer": result.layer,
        "config_x": result.config_x,
        "step": result.step,
        "over_budget": result.over_budget,
        "min_x_strict": result.min_x_strict,
        "min_x_weak": result.min_x_weak,
        "x_histogram": {str(x): count for x, count in sorted(result.x_histogram.items())},
        "witness": result.witness,
        "unlosable": result.unlosable,
        "untrimmable": result.untrimmable,
        "violations_at_config_x": result.violations_at_config_x,
        "passed": result.passed,
    }


def format_gate_report(result: GateResult) -> str:
    lines = [
        f"Überziehungs-Gate, Tier {result.tier}: {REFERENCE_LABEL}",
        f"  nötiges X (strikt) {result.min_x_strict}, (schwach) {result.min_x_weak}; "
        f"Konfiguration X = {result.config_x} je angefangene {result.step} k€",
        f"  Pläne über Budget: {result.over_budget}",
        f"  nicht verlierbar (gekürzte Version endet bei KZ 0): {result.unlosable}; "
        f"nicht kürzbar (kein Plan im Budget darunter): {result.untrimmable}",
        f"  Pläne, die mit X = {result.config_x} nicht strikt verlieren: {result.violations_at_config_x}",
    ]
    witness = result.witness
    if witness is not None:
        lines.append(
            f"  bestimmender Plan {witness['code']}: Restbudget {witness['remaining']} k€, "
            f"angefangene Schritte {witness['steps']}, KZ vor Review {witness['kz_pre_review']}, "
            f"End-KZ {witness['kz_final']}, nötiges X {witness['required_x']}"
        )
        lines.append(
            f"  gekürzte Version {witness['trimmed_code']}: Restbudget {witness['trimmed_remaining']} k€, "
            f"End-KZ {witness['trimmed_kz_final']}"
        )
    lines.append("  bestanden" if result.passed else "  NICHT bestanden")
    return "\n".join(lines)


class PathGateResult(NamedTuple):
    tier: str
    family: str
    pool: str
    config_x: int
    step: int
    paths: int
    over_budget: int
    min_x_strict: int
    min_x_capped: int
    min_x_weak: int
    x_histogram: Dict[int, int]
    witness: Optional[Dict]
    unlosable: int
    untrimmable: int
    violations_at_config_x: int
    passed: bool


class PathScan:
    """Pfade über Budget einer Familie, verdichtet je Startplan: Anzahl der Pfade und je angefangene Schritte das
    Maximum der KZ vor Review (das nötige X wächst mit ihr, die Verdichtung ist für X exakt)."""

    def __init__(self, n_measures: int):
        self.n_measures = n_measures
        self.size = LEVELS**n_measures
        self.paths = 0
        self.over_budget = array("I", [0]) * self.size
        self.max_pre: Dict[int, array] = {}

    def add_over(self, start: int, steps: int, pre: int) -> None:
        self.over_budget[start] += 1
        column = self.max_pre.get(steps)
        if column is None:
            column = self.max_pre[steps] = array("b", [-1]) * self.size
        if pre > column[start]:
            column[start] = pre


def new_pool(n_measures: int) -> array:
    return array("i", [-1]) * (LEVELS**n_measures)


def path_gate_from_scan(
    scan: PathScan, pool: array, config_x: int, step: int, tier_name: str, family: str, pool_label: str
) -> PathGateResult:
    """Wertet die Pfade über Budget gegen den bereits abgeschlossenen Pool aus (Schlüssel wie `trim_keys`)."""
    n = scan.n_measures
    size = scan.size
    over = scan.over_budget
    untrimmable = 0
    unlosable = 0
    for start in range(size):
        count = over[start]
        if count:
            key = pool[start]
            if key < 0:
                untrimmable += count
            elif key < size:
                unlosable += count

    min_strict = 1
    min_weak = 1
    min_capped = 1
    violations = 0
    histogram: Dict[int, int] = {}
    witness_key = None
    witness_group = None
    memo: Dict = {}
    for steps in sorted(scan.max_pre):
        column = scan.max_pre[steps]
        for start in range(size):
            pre = column[start]
            if pre < 0:
                continue
            key = pool[start]
            if key < size:
                continue
            trimmed_final = key // size
            triple = memo.get((pre, trimmed_final, steps))
            if triple is None:
                triple = memo[(pre, trimmed_final, steps)] = (
                    required_penalty_x(pre, trimmed_final, steps),
                    required_penalty_x(pre, trimmed_final, steps, strict=False),
                    capped_required_x(pre, trimmed_final, steps),
                )
            strict_x, weak_x, capped_x = triple
            histogram[strict_x] = histogram.get(strict_x, 0) + 1
            if strict_x > config_x:
                violations += 1
            min_strict = max(min_strict, strict_x)
            min_weak = max(min_weak, weak_x)
            min_capped = max(min_capped, capped_x)
            candidate = (strict_x, -start, -steps)
            if witness_key is None or candidate > witness_key:
                witness_key = candidate
                witness_group = (start, steps, pre, key)

    witness = None
    if witness_group is not None:
        start, steps, pre, key = witness_group
        witness = {
            "code": code_from_index(start, n),
            "steps": steps,
            "kz_pre_review": pre,
            "required_x": witness_key[0],
            "trimmed_code": code_from_index(size - 1 - key % size, n),
            "trimmed_kz_final": key // size,
        }
    return PathGateResult(
        tier=tier_name,
        family=family,
        pool=pool_label,
        config_x=config_x,
        step=step,
        paths=scan.paths,
        over_budget=sum(over),
        min_x_strict=min_strict,
        min_x_capped=min_capped,
        min_x_weak=min_weak,
        x_histogram=dict(sorted(histogram.items())),
        witness=witness,
        unlosable=unlosable,
        untrimmable=untrimmable,
        violations_at_config_x=violations,
        passed=config_x >= min_strict and unlosable == 0 and untrimmable == 0,
    )


def _swap_stream(tables):
    prefix = tables.prefix_waves
    suffix = tables.wave_count - prefix
    for start, end, _dropped, _incoming, _level, cost in tables.swap_paths():
        yield start, (start,) * prefix + (end,) * suffix, cost


def _static_stream(tables):
    codes = tables.wave_count
    for start in range(len(tables.valid)):
        if tables.valid[start]:
            yield start, (start,) * codes, 0


def _window_stream(tables, window: int):
    for start in range(len(tables.valid)):
        if not tables.valid[start]:
            continue
        for target, cost in tables.single_moves(start):
            if window == 1:
                yield start, (start, target, target), cost
            else:
                yield start, (start, start, target), cost


def _run_stream(tables, stream, pools, scan, step: int) -> int:
    """Eine Runde über die Pfade einer Familie: Pfade im Budget füllen die Pools, Pfade über Budget die Verdichtung."""
    size = len(tables.valid)
    path_outcome = tables.path_outcome
    steps_of: Dict[int, int] = {}
    count = 0
    for start, codes, cost in stream:
        count += 1
        outcome = path_outcome(codes, cost)
        if outcome.over_budget:
            if scan is not None:
                remaining = outcome.remaining
                steps = steps_of.get(remaining)
                if steps is None:
                    steps = steps_of[remaining] = started_steps(-remaining, step)
                scan.add_over(start, steps, outcome.kz_pre_review)
        else:
            key = outcome.kz_final * size + size - 1 - start
            for pool in pools:
                if key > pool[start]:
                    pool[start] = key
    return count


def _narrow_family(tables, config_x: int, step: int, tier_name: str) -> PathGateResult:
    """Enge Kürzung (Diagnose): gleiches Tauschpaar, Startlevel und Level der neuen Maßnahme nur gesenkt. Je Paar ein
    Pool über das 4^n-Gitter am Index Start + Level * Stelle der neuen Maßnahme (eindeutig, weil sie im Start 0 ist)."""
    n = len(tables.measure_ids)
    size = LEVELS**n
    prefix = tables.prefix_waves
    suffix = tables.wave_count - prefix
    strides = tables.strides
    path_outcome = tables.path_outcome
    pools: Dict = {}
    for start, end, dropped, incoming, level, cost in tables.swap_paths():
        if dropped is None:
            continue
        outcome = path_outcome((start,) * prefix + (end,) * suffix, cost)
        if outcome.over_budget:
            continue
        pool = pools.get((dropped, incoming))
        if pool is None:
            pool = pools[(dropped, incoming)] = array("b", [-1]) * size
        cell = start + level * strides[incoming]
        if outcome.kz_final > pool[cell]:
            pool[cell] = outcome.kz_final
    for pool in pools.values():
        lowering_closure(pool, n)

    paths = 0
    over_budget = 0
    untrimmable = 0
    unlosable = 0
    violations = 0
    min_strict = 1
    min_weak = 1
    min_capped = 1
    histogram: Dict[int, int] = {}
    witness_key = None
    witness = None
    memo: Dict = {}
    steps_of: Dict[int, int] = {}
    for start, end, dropped, incoming, level, cost in tables.swap_paths():
        if dropped is None:
            continue
        paths += 1
        outcome = path_outcome((start,) * prefix + (end,) * suffix, cost)
        if not outcome.over_budget:
            continue
        over_budget += 1
        pool = pools.get((dropped, incoming))
        trimmed_final = -1 if pool is None else pool[start + level * strides[incoming]]
        if trimmed_final < 0:
            untrimmable += 1
            continue
        if trimmed_final == 0:
            unlosable += 1
            continue
        remaining = outcome.remaining
        steps = steps_of.get(remaining)
        if steps is None:
            steps = steps_of[remaining] = started_steps(-remaining, step)
        pre = outcome.kz_pre_review
        triple = memo.get((pre, trimmed_final, steps))
        if triple is None:
            triple = memo[(pre, trimmed_final, steps)] = (
                required_penalty_x(pre, trimmed_final, steps),
                required_penalty_x(pre, trimmed_final, steps, strict=False),
                capped_required_x(pre, trimmed_final, steps),
            )
        strict_x, weak_x, capped_x = triple
        histogram[strict_x] = histogram.get(strict_x, 0) + 1
        if strict_x > config_x:
            violations += 1
        min_strict = max(min_strict, strict_x)
        min_weak = max(min_weak, weak_x)
        min_capped = max(min_capped, capped_x)
        if witness_key is None or strict_x > witness_key:
            witness_key = strict_x
            witness = {
                "code": code_from_index(start, n),
                "swap": [tables.measure_ids[dropped], tables.measure_ids[incoming], level],
                "steps": steps,
                "kz_pre_review": pre,
                "required_x": strict_x,
                "trimmed_code": None,
                "trimmed_kz_final": trimmed_final,
            }
    return PathGateResult(
        tier=tier_name,
        family=NARROW_FAMILY,
        pool=POOL_OF[NARROW_FAMILY],
        config_x=config_x,
        step=step,
        paths=paths,
        over_budget=over_budget,
        min_x_strict=min_strict,
        min_x_capped=min_capped,
        min_x_weak=min_weak,
        x_histogram=dict(sorted(histogram.items())),
        witness=witness,
        unlosable=unlosable,
        untrimmable=untrimmable,
        violations_at_config_x=violations,
        passed=config_x >= min_strict and unlosable == 0 and untrimmable == 0,
    )


def gate_paths_tier(cfg, tier_name: str, tables=None, narrow: bool = False) -> Dict[str, PathGateResult]:
    """Pfad-Gate eines Tiers (Familien `tausch`, `fenster1`, `fenster2`; mit `narrow` zusätzlich `tausch_eng`).
    Je Familie höchstens eine Runde über ihre Pfade; die Verdichtung je (Start, angefangene Schritte) macht das
    nötige X, die Zähler für nicht verlierbare und nicht kürzbare Pfade und den bestimmenden Pfad exakt."""
    if tables is None:
        tables = rules.TierTables(cfg, tier_name)
    if tables.wave_count != 3:
        raise ValueError("Das Pfad-Gate kennt zwei Change-Fenster (MAX_WINDOWS = 2, drei Wellen)")
    n = len(tables.measure_ids)
    config_x, step = rules.penalty_params(cfg.final_events)
    legal_pool = new_pool(n)
    union_pool = new_pool(n)
    scans = {family: PathScan(n) for family in PATH_FAMILIES}

    scans["tausch"].paths = _run_stream(tables, _swap_stream(tables), (legal_pool, union_pool), scans["tausch"], step)
    _run_stream(tables, _static_stream(tables), (union_pool,), None, step)
    scans["fenster1"].paths = _run_stream(tables, _window_stream(tables, 1), (union_pool,), scans["fenster1"], step)
    scans["fenster2"].paths = _run_stream(tables, _window_stream(tables, 2), (union_pool,), scans["fenster2"], step)
    lowering_closure(legal_pool, n)
    lowering_closure(union_pool, n)

    results = {
        family: path_gate_from_scan(
            scans[family], legal_pool if POOL_OF[family] == "legal" else union_pool,
            config_x, step, tier_name, family, POOL_OF[family],
        )
        for family in PATH_FAMILIES
    }
    if narrow:
        results[NARROW_FAMILY] = _narrow_family(tables, config_x, step, tier_name)
    return results


def paths_worker(config_path: str, tier_name: str, narrow: bool = False):
    """Prozess-Worker für `parallel.map_tiers`: statisches Gate und Pfad-Familien eines Tiers."""
    from planspiel.config import load_config

    cfg = load_config(Path(config_path))
    return gate_tier(cfg, tier_name), gate_paths_tier(cfg, tier_name, narrow=narrow)


class Calibration(NamedTuple):
    config_x: int
    max_min_x_raw: int
    max_min_x_capped: int
    recommended_x: int
    binding_tier: str
    binding_family: str
    binding_kind: str
    calibrated: bool
    within_target: bool
    passed_all: bool
    unlosable_total: int
    x_target: int = X_TARGET
    static_min_x_capped: Optional[Dict[str, int]] = None


def calibrate(
    static_by_tier: Dict[str, GateResult],
    paths_by_tier: Dict[str, Dict[str, PathGateResult]],
    x_target: int = X_TARGET,
) -> Calibration:
    """X = größtes nötiges X (roh und gekappt) über statisches Gate und die Pfad-Familien aller Tiers + 1 (D-13).
    Die enge Kürzung bleibt außen vor."""
    cells = []
    passed_all = True
    unlosable_total = 0
    config_x = None
    for tier, static in static_by_tier.items():
        config_x = static.config_x if config_x is None else config_x
        results = [(STATIC_FAMILY, static)]
        families = paths_by_tier.get(tier, {})
        results += [(family, families[family]) for family in PATH_FAMILIES if family in families]
        for family, result in results:
            cells.append((result.min_x_strict, tier, family, "roh"))
            if result.min_x_capped is not None:
                cells.append((result.min_x_capped, tier, family, "gekappt"))
            passed_all = passed_all and result.passed
            unlosable_total += result.unlosable
    maximum = max(cell[0] for cell in cells)
    binding = next(cell for cell in cells if cell[0] == maximum)
    raw = max(cell[0] for cell in cells if cell[3] == "roh")
    capped = max((cell[0] for cell in cells if cell[3] == "gekappt"), default=raw)
    recommended = maximum + 1
    return Calibration(
        config_x=config_x,
        max_min_x_raw=raw,
        max_min_x_capped=capped,
        recommended_x=recommended,
        binding_tier=binding[1],
        binding_family=binding[2],
        binding_kind=binding[3],
        calibrated=config_x == recommended,
        within_target=recommended <= x_target,
        passed_all=passed_all,
        unlosable_total=unlosable_total,
        x_target=x_target,
        static_min_x_capped={
            tier: static.min_x_capped for tier, static in static_by_tier.items() if static.min_x_capped is not None
        },
    )


def gate_paths_result_json(result: PathGateResult) -> Dict:
    return {
        "tier": result.tier,
        "family": result.family,
        "pool": result.pool,
        "config_x": result.config_x,
        "step": result.step,
        "paths": result.paths,
        "over_budget": result.over_budget,
        "min_x_strict": result.min_x_strict,
        "min_x_capped": result.min_x_capped,
        "min_x_weak": result.min_x_weak,
        "x_histogram": {str(x): count for x, count in sorted(result.x_histogram.items())},
        "witness": result.witness,
        "unlosable": result.unlosable,
        "untrimmable": result.untrimmable,
        "violations_at_config_x": result.violations_at_config_x,
        "passed": result.passed,
    }


def calibration_json(cal: Calibration) -> Dict:
    return {
        "config_x": cal.config_x,
        "x_target": cal.x_target,
        "max_min_x_raw": cal.max_min_x_raw,
        "max_min_x_capped": cal.max_min_x_capped,
        "recommended_x": cal.recommended_x,
        "binding_tier": cal.binding_tier,
        "binding_family": cal.binding_family,
        "binding_kind": cal.binding_kind,
        "calibrated": cal.calibrated,
        "within_target": cal.within_target,
        "passed_all": cal.passed_all,
        "unlosable_total": cal.unlosable_total,
        "static_min_x_capped": dict(cal.static_min_x_capped or {}),
    }


POOL_TEXT = {
    "legal": "gekürzter Startplan, danach jede legale Fortsetzung der Tausch-Schicht",
    "union": "gekürzter Startplan, danach jede legale Fortsetzung (statisch, Tausch-Schicht, Züge in Fenster 1 und 2)",
    "same_pair": "gekürzter Startplan und gesenktes Level der neuen Maßnahme, gleiches Tauschpaar (Diagnose)",
}
HISTOGRAM_TAIL = 5


def format_path_gate_report(result: PathGateResult) -> str:
    unit = "Pfade" if result.family == NARROW_FAMILY else "Gruppen aus Start und angefangenen Schritten"
    lines = [
        f"Überziehungs-Gate, Tier {result.tier}, Pfade: {PATH_LABELS[result.family]}",
        f"  Vergleich: {POOL_TEXT[result.pool]}",
        f"  nötiges X roh {result.min_x_strict}, gekappt {result.min_x_capped} "
        f"(Begrenzung 0..100 nach der Strafe), schwach {result.min_x_weak}; "
        f"Konfiguration X = {result.config_x} je angefangene {result.step} k€",
        f"  Pfade: {result.paths}, davon über Budget: {result.over_budget}",
        f"  nicht verlierbar (gekürzte Version endet bei KZ 0): {result.unlosable}; "
        f"nicht kürzbar (kein Pfad im Budget darunter): {result.untrimmable}",
        f"  {unit}, die mit X = {result.config_x} nicht strikt verlieren: {result.violations_at_config_x}",
    ]
    if result.x_histogram:
        tail = sorted(result.x_histogram.items(), reverse=True)[:HISTOGRAM_TAIL]
        lines.append(f"  Ende der Verteilung ({unit}), nötiges X: " + ", ".join(f"{x}: {count}" for x, count in tail))
    witness = result.witness
    if witness is not None:
        swap = ""
        if "swap" in witness:
            swap = f", Tausch {witness['swap'][0]} -> {witness['swap'][1]} Level {witness['swap'][2]}"
        lines.append(
            f"  bestimmender Pfad: Start {witness['code']}{swap}, angefangene Schritte {witness['steps']}, "
            f"KZ vor Review {witness['kz_pre_review']}, nötiges X {witness['required_x']}"
        )
        trimmed = "" if witness["trimmed_code"] is None else f" {witness['trimmed_code']}"
        lines.append(f"  gekürzte Version{trimmed}: End-KZ {witness['trimmed_kz_final']}")
    lines.append("  bestanden" if result.passed else "  NICHT bestanden")
    return "\n".join(lines)


def format_calibration(cal: Calibration) -> str:
    lines = ["Kalibrierung von X (Maximum über Tiers und Familien, enge Kürzung ausgenommen)"]
    if cal.static_min_x_capped:
        capped = ", ".join(f"{tier} {x}" for tier, x in cal.static_min_x_capped.items())
        lines.append(f"  statisches Gate, nötiges X gekappt je Tier: {capped}")
    lines += [
        f"  größtes nötiges X roh {cal.max_min_x_raw}, gekappt {cal.max_min_x_capped}; "
        f"nicht verlierbar {cal.unlosable_total}",
        f"  Empfohlenes X = Maximum + 1 = {cal.recommended_x} "
        f"(bestimmend: Tier {cal.binding_tier}, Familie {cal.binding_family}, {cal.binding_kind})",
        f"  Konfiguration X = {cal.config_x}: " + ("kalibriert" if cal.calibrated else "nicht kalibriert"),
        f"  Ziel X ≤ {cal.x_target}: " + ("erreicht" if cal.within_target else "verfehlt"),
    ]
    return "\n".join(lines)
