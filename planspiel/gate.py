"""Überziehungs-Gate (RULE-04, D-17, BAL-01): Überziehen lohnt sich nie.

Debriefing-Satz: "Wer am Ende über Budget liegt, hätte mit dem besten Paket, das nur durch Senken oder
Kündigen von Leveln entsteht und im Budget bleibt, immer eine höhere End-KZ erreicht."

Das statische Gate arbeitet auf dem Referenzplan ohne Change-Fenster-Züge (D-24, D-25). Je Plan über Budget wird die
gekürzte Version gesucht: der beste Plan im Budget, dessen Level alle <= denen des Plans sind (inkl. positiver
Budget-Review-Stufe). Das nötige X je Plan ist die kleinste ganze Zahl, bei der der Plan strikt verliert.
Das Gate liest nur Spalten des Ergebnisspeichers und `rules.penalty_params`, nie Formel-Operanden.

Pfad-Gate (D-13, BAL-01; Phase-2-D-25 zurückgestellt): dieselbe Frage für legale Spielpfade, in den Familien
- `tausch`: Tausch-Schicht (Pflicht-Maßnahmentausch mit kanonischer Reparatur, legales Minimum);
- `tausch_fenster2`: der Pflicht-Tausch und danach ein freiwilliger Zug (ein Level einer Maßnahme geändert) im Fenster
  nach Welle 2; das ist die Form der Referenzpfade und Lösungsschlüssel (`refpaths`);
- `fenster1`, `fenster2`: ein Zug im Fenster nach Welle 1 oder 2 ohne Tausch, nur aus Startplänen, in denen kein Tausch
  möglich ist. Ist ein Tausch möglich, ist er Pflicht (D-22, `rules.evaluate_path`); ein Zug ohne Tausch wäre dort ein
  Pfad, den kein Team spielen kann, und darf weder geprüft werden noch als gekürzte Version dienen (06-REVIEW WR-03).
Gekürzte Version eines Pfads über Budget = Startplan mit nur gesenkten oder gekündigten Leveln, danach jede legale
Fortsetzung des Pools der Familie (Tausch-Schicht: legaler Pool; Zug-Familien: Vereinigung aller vier Familien, also
aller hier geprüften legalen Pfade). Debriefing: "Hätte das Team zu Spielbeginn weniger oder niedrigere Maßnahmen
gewählt, wäre es im Budget geblieben und besser gelandet." Die enge Kürzung (gleiches Tauschpaar) ist nur eine
Diagnose (`tausch_eng`) und geht nie in das Urteil oder die Kalibrierung ein.

Nicht geprüft sind mehrere Züge in einem Fenster, Züge in beiden Fenstern und ein zusätzlicher freiwilliger Zug im
Tausch-Fenster (die Regeln erlauben "beliebig viele" Züge); die Kalibrierung nennt diese Lücke.

`tausch_fenster2` hat etwa 30 Züge je Tausch-Pfad (rund eine Milliarde Pfade je Tier) und wird deshalb verdichtet: ein
Zug wirkt nur über seine KZ-Änderung in Welle 3 und seinen Budgetbedarf (OPEX und Event-Kosten der Welle 3, Init-
Differenz, abzüglich Event-Budget der Welle 3). Je Fensterzustand zählen nur die Züge der Pareto-Front (kein anderer Zug
hat höchstens den Bedarf und mindestens die KZ-Änderung). Ein beherrschter Zug erhöht X nie: liegt sein Beherrscher über
Budget, verlangt dieser bei höchstens so vielen Schritten mindestens dieselbe KZ vor Review; liegt der Beherrscher im
Budget, endet die gekürzte Version mindestens auf dessen End-KZ (Budget-Review-Stufen nicht negativ und steigend), der
beherrschte Zug braucht X = 1. Nötiges X (roh, schwach, gekappt), Urteil, Pfadzahlen sowie nicht verlierbare und nicht
kürzbare Pfade sind damit exakt; Verteilung und "nicht strikt verlieren" zählen Gruppen der Pareto-Front, der
bestimmende Pfad ist exakt, sobald das nötige X über 1 liegt.

Kalibrierung (D-13): X = größtes nötiges X über alle Tiers und Familien + 1. Roh und gekappt werden beide gemeldet
(Annahme A1 der Phase-6-Recherche, am Checkpoint D-04 zu bestätigen): roh = Strafe ohne Untergrenze
(KZ vor Review - X * Schritte), gekappt = nach der Strafe auf 0..100 begrenzt (`rules.clamp_kz`, wie das Budget
Review). Endet die gekürzte Version bei KZ 0, gibt es kein endliches gekapptes X; solche Pfade zählen als
"nicht verlierbar".
"""
from array import array
from bisect import bisect_right
from pathlib import Path
from typing import Dict, NamedTuple, Optional

from planspiel import rules
from planspiel.enumerate import code_from_index, enumerate_tier
from planspiel.report import REFERENCE_LABEL, REFERENCE_LAYER
from planspiel.rounding import started_steps

LEVELS = 4

SWAP_MOVE_FAMILY = "tausch_fenster2"
PATH_FAMILIES = ("tausch", "fenster1", "fenster2", SWAP_MOVE_FAMILY)
NARROW_FAMILY = "tausch_eng"
STATIC_FAMILY = "statisch"
X_TARGET = 5
PATH_LABELS = {
    "tausch": "Tausch-Schicht (Pflicht-Maßnahmentausch, legales Minimum)",
    "fenster1": "ein Zug im Fenster nach Welle 1 (Startpläne ohne möglichen Tausch)",
    "fenster2": "ein Zug im Fenster nach Welle 2 (Startpläne ohne möglichen Tausch)",
    SWAP_MOVE_FAMILY: "Pflicht-Maßnahmentausch, danach ein Zug im Fenster nach Welle 2",
    NARROW_FAMILY: "Tausch-Schicht, enge Kürzung (gleiches Tauschpaar)",
}
POOL_OF = {
    "tausch": "legal", "fenster1": "union", "fenster2": "union", SWAP_MOVE_FAMILY: "union", NARROW_FAMILY: "same_pair",
}
UNCOVERED_SHAPES = (
    "nicht geprüft: mehrere Züge in einem Fenster, Züge in beiden Fenstern, ein zusätzlicher Zug im Tausch-Fenster"
)


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
        self.add_group(start, steps, pre)

    def add_group(self, start: int, steps: int, pre: int) -> None:
        """Nur die Verdichtung, ohne den Pfad zu zählen (die Zug-Familie mit Tausch zählt ihre Pfade selbst)."""
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


def _swap_mandatory(tables, start: int) -> bool:
    """D-22 auf dem Zustandsindex: mit Kurswechsel ist der Tausch Pflicht, sobald eine Maßnahme aktiv und eine inaktiv ist."""
    if tables.kurswechsel_wave is None:
        return False
    levels = [(start // stride) % LEVELS for stride in tables.strides]
    return any(levels) and not all(levels)


def _window_stream(tables, window: int):
    """Ein Zug ohne Tausch, nur aus Startplänen, in denen kein Tausch möglich ist (sonst wäre der Pfad illegal)."""
    for start in range(len(tables.valid)):
        if not tables.valid[start] or _swap_mandatory(tables, start):
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


def _review_monotone(final_events) -> bool:
    """Die Verdichtung der Zug-Familie mit Tausch setzt nicht negative, mit dem Restbudget steigende Review-Stufen voraus."""
    for event in final_events:
        if event.type != "final_budget_tier":
            return False
        values = [value for _minimum, value in event.params["tiers"]]
        if values[0] < 0 or any(later < earlier for earlier, later in zip(values, values[1:])):
            return False
    return True


def _move_front(tables, end: int):
    """(alle Bedarfe aufsteigend, Pareto-Front als (Bedarf, KZ-Änderung) aufsteigend) der Züge im Fenster nach Welle 2."""
    opex = tables.opex_cost
    change = tables.change[2]
    event_opex = tables.event_opex[2]
    event_budget = tables.event_budget[2]
    options = [
        (opex[target] + cost + event_opex[target] - event_budget[target], change[target])
        for target, cost in tables.single_moves(end)
    ]
    needs = tuple(sorted(need for need, _ in options))
    options.sort(key=lambda option: (option[0], -option[1]))
    front = []
    for need, kz_change in options:
        if not front or kz_change > front[-1][1]:
            front.append((need, kz_change))
    return needs, tuple(front)


def _run_swap_moves(tables, pool: array, scan: PathScan, step: int) -> int:
    """Familie `tausch_fenster2` in einer Runde über die Tausch-Pfade: KZ nach Welle 2 und Restbudget ohne Welle 3 je
    Tausch-Pfad, dann die Züge der Pareto-Front (Modul-Docstring). Die Pfade über Budget je Start zählt sie exakt."""
    size = len(tables.valid)
    tier = tables.tier
    budget = tier.budget
    kz_start = tier.kz_start
    change0, change1 = tables.change[0], tables.change[1]
    event_opex0, event_opex1 = tables.event_opex[0], tables.event_opex[1]
    event_budget0, event_budget1 = tables.event_budget[0], tables.event_budget[1]
    init = tables.init_cost
    opex = tables.opex_cost
    final_events = tables.cfg.final_events
    clamp = rules.clamp_kz
    over_count = scan.over_budget
    fronts: Dict[int, tuple] = {}
    finals: Dict[tuple, int] = {}
    steps_of: Dict[int, int] = {}
    paths = 0
    for start, end, dropped, _incoming, _level, cost in tables.swap_paths():
        if dropped is None:
            continue
        entry = fronts.get(end)
        if entry is None:
            entry = fronts[end] = _move_front(tables, end)
        needs, front = entry
        paths += len(needs)
        kz = clamp(clamp(kz_start + change0[start]) + change1[end])
        before = (
            budget + event_budget0[start] + event_budget1[end]
            - init[start] - opex[start] - opex[end] - cost - event_opex0[start] - event_opex1[end]
        )
        over = len(needs) - bisect_right(needs, before)
        if over:
            over_count[start] += over
        best = pool[start]
        for need, kz_change in front:
            remaining = before - need
            kz_pre = clamp(kz + kz_change)
            if remaining < 0:
                steps = steps_of.get(remaining)
                if steps is None:
                    steps = steps_of[remaining] = started_steps(-remaining, step)
                scan.add_group(start, steps, kz_pre)
            else:
                kz_final = finals.get((remaining, kz_pre))
                if kz_final is None:
                    kz_final = finals[(remaining, kz_pre)] = rules.apply_final_events(
                        final_events, {}, remaining, kz_pre
                    )[0]
                key = kz_final * size + size - 1 - start
                if key > best:
                    best = key
        pool[start] = best
    return paths


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
    """Pfad-Gate eines Tiers (Familien `tausch`, `fenster1`, `fenster2`, `tausch_fenster2`; mit `narrow` zusätzlich
    `tausch_eng`).
    Je Familie höchstens eine Runde über ihre Pfade; die Verdichtung je (Start, angefangene Schritte) macht das
    nötige X, die Zähler für nicht verlierbare und nicht kürzbare Pfade und den bestimmenden Pfad exakt."""
    if tables is None:
        tables = rules.TierTables(cfg, tier_name)
    if tables.wave_count != 3:
        raise ValueError("Das Pfad-Gate kennt zwei Change-Fenster (MAX_WINDOWS = 2, drei Wellen)")
    if tables.kurswechsel_wave is not None and tables.prefix_waves != 1:
        raise ValueError("Das Pfad-Gate erwartet den Kurswechsel in der ersten Welle (Tausch im Fenster nach Welle 1)")
    if not _review_monotone(cfg.final_events):
        raise ValueError("Das Pfad-Gate setzt nicht negative, mit dem Restbudget steigende Budget-Review-Stufen voraus")
    n = len(tables.measure_ids)
    config_x, step = rules.penalty_params(cfg.final_events)
    legal_pool = new_pool(n)
    union_pool = new_pool(n)
    scans = {family: PathScan(n) for family in PATH_FAMILIES}

    # The swap layer carries the static paths of the starts without a possible swap; static paths of every other start
    # are illegal (the swap is mandatory there), so the union gets no separate static pass.
    scans["tausch"].paths = _run_stream(tables, _swap_stream(tables), (legal_pool, union_pool), scans["tausch"], step)
    scans["fenster1"].paths = _run_stream(tables, _window_stream(tables, 1), (union_pool,), scans["fenster1"], step)
    scans["fenster2"].paths = _run_stream(tables, _window_stream(tables, 2), (union_pool,), scans["fenster2"], step)
    scans[SWAP_MOVE_FAMILY].paths = _run_swap_moves(tables, union_pool, scans[SWAP_MOVE_FAMILY], step)
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


def paths_worker(config_path: str, tier_name: str, narrow: bool = False, hand_calc_level: str = "error"):
    """Prozess-Worker für `parallel.map_tiers`: statisches Gate und Pfad-Familien eines Tiers."""
    from planspiel.config import load_config

    cfg = load_config(Path(config_path), hand_calc_level)
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
    "union": "gekürzter Startplan, danach jede legale Fortsetzung (Tausch-Schicht, Tausch mit Zug in Fenster 2, "
    "Züge in Fenster 1 und 2 ohne möglichen Tausch)",
    "same_pair": "gekürzter Startplan und gesenktes Level der neuen Maßnahme, gleiches Tauschpaar (Diagnose)",
}
HISTOGRAM_TAIL = 5


def format_path_gate_report(result: PathGateResult) -> str:
    unit = "Pfade" if result.family == NARROW_FAMILY else "Gruppen aus Start und angefangenen Schritten"
    if result.family == SWAP_MOVE_FAMILY:
        unit += " (Pareto-Front der Züge je Fensterzustand)"
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
    lines = ["Kalibrierung von X (Maximum über Tiers und Familien, enge Kürzung ausgenommen)", f"  {UNCOVERED_SHAPES}"]
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
