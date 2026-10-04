"""Überziehungs-Gate (RULE-04, D-17): Überziehen lohnt sich nie.

Debriefing-Satz: "Wer am Ende über Budget liegt, hätte mit dem besten Paket, das nur durch Senken oder
Kündigen von Leveln entsteht und im Budget bleibt, immer eine höhere End-KZ erreicht."

Das Gate arbeitet auf dem Referenzplan ohne Change-Fenster-Züge (D-24, D-25). Je Plan über Budget wird die
gekürzte Version gesucht: der beste Plan im Budget, dessen Level alle <= denen des Plans sind (inkl. positiver
Budget-Review-Stufe). Das nötige X je Plan ist die kleinste ganze Zahl, bei der der Plan strikt verliert.
Das Gate liest nur Spalten des Ergebnisspeichers und `rules.penalty_params`, nie Formel-Operanden.
"""
from array import array
from typing import Dict, NamedTuple, Optional

from planspiel import rules
from planspiel.enumerate import code_from_index, enumerate_tier
from planspiel.report import REFERENCE_LABEL, REFERENCE_LAYER
from planspiel.rounding import started_steps

LEVELS = 4


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
