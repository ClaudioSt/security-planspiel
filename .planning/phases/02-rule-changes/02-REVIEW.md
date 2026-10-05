---
phase: 02-rule-changes
reviewed: 2026-10-05T00:00:00Z
depth: standard
files_reviewed: 37
files_reviewed_list:
  - .gitignore
  - CLAUDE.md
  - README.md
  - planspiel/analyze.py
  - planspiel/balance.py
  - planspiel/cli.py
  - planspiel/config.py
  - planspiel/enumerate.py
  - planspiel/gate.py
  - planspiel/report.py
  - planspiel/review_text.py
  - planspiel/rounding.py
  - planspiel/rules.py
  - planspiel/validate.py
  - simulation_config.json
  - tests/fixtures/mini_config.json
  - tests/support/digest.py
  - tests/support/golden_cases.py
  - tests/support/harness.py
  - tests/test_budget_review.py
  - tests/test_budget_review_text.py
  - tests/test_characterization.py
  - tests/test_digest.py
  - tests/test_e_target_removed.py
  - tests/test_enumeration.py
  - tests/test_kernel_conformance.py
  - tests/test_kurswechsel.py
  - tests/test_overspend_gate.py
  - tests/test_paths.py
  - tests/test_ros_ledger.py
  - tests/test_rules_exact.py
  - tests/test_rules_semantics.py
  - tests/test_single_definition.py
  - tests/test_sparprogramm.py
  - tests/test_swap_layer.py
  - tests/test_validate.py
  - tests/test_wrappers.py
findings:
  critical: 0
  warning: 6
  info: 6
  total: 12
status: issues_found
---

# Phase 2: Code Review Report

**Reviewed:** 2026-10-05
**Depth:** standard
**Files Reviewed:** 37
**Status:** issues_found

## Narrative Findings (AI reviewer)

## Summary

I reviewed the Phase 2 diff (`cae404b..HEAD`): E-target removal, own-spend RoS ledger, linear overspend penalty, generated Budget Review text, Kurswechsel swap rules, `evaluate_path` and `TierTables`, the event-overrun validator warning and the overspend gate. The fast suite passes (551 passed).

I ran these checks beyond the existing tests:
- **Exact arithmetic holds.** There is no `round()` and no float in any rule path. `started_steps`, `round_half_away` and `required_penalty_x` stay in integers.
- **Gate maths is correct.** `lowering_closure` builds a correct componentwise prefix maximum. The strict and weak X formulas are correct, including the clamp at 0.
- **Printed text matches the simulation.** `boundary_text` and `penalty_rows` agree with `budget_review_delta`.
- **Tables match the exact evaluator.** I moved the Kurswechsel to wave 2 in a copy of the mini config, which no shipped test covers. `TierTables.swap_paths` + `path_outcome` still matched `evaluate_path` on all 1,477 paths in every tier.

No blocker shows up on the shipped configs. The problems are latent rule gaps that a config change can trigger (confirmed with mutated configs), validator gaps that the gate's arithmetic depends on, and the per-wave evaluation now being written out three times.

## Warnings

### WR-01: A plan can need the Kurswechsel swap but have no legal swap; it then has no legal game and silently drops out of the swap layer

**File:** `planspiel/rules.py:224-228`, `planspiel/rules.py:648-650`, `planspiel/rules.py:935-955`, `planspiel/enumerate.py:130-132`

**Issue:** `swap_possible` only checks "at least one active and one inactive measure". A swap can still be impossible: every possible incoming measure may, at every level, depend on the measure being dropped.
- `evaluate_path` then raises `kurswechsel_missing` for every path from that start, so the team has no legal game.
- `TierTables.swap_paths` yields nothing for that start, so `enumerate_swap_layer` does not count it in `start_plans` or `legal_games`.
- Neither the README rule ("Kein Tausch möglich: ... keine oder jede Maßnahme aktiv") nor the config description covers this case.
- The validator accepts the config that triggers it.

I reproduced it: in a mini-config copy, `M1`, `M4` and `M6` each get an L1 dependency on `M2 >= 1`. From start `{M2: 1}`, `evaluate_path` raises `kurswechsel_missing`, and only 190 of 193 valid starts are counted. The shipped configs are safe only because no L1 or L2 level has a dependency. `test_every_non_exempt_mini_plan_has_a_legal_swap` pins this property for the mini config only.

**Fix:** Define the exemption by whether a legal swap exists, and share it between the evaluator and the tables:
```python
def swap_possible(selection, measures) -> bool:
    for dropped, level in selection.items():
        if level == 0:
            continue
        repaired = swap_repair(selection, dropped, measures)
        for incoming, in_level in selection.items():
            if in_level == 0 and any(
                dependencies_satisfied({**repaired, incoming: lvl}, measures) for lvl in (1, 2, 3)
            ):
                return True
    return False
```
Alternatively, add a validator error when any measure has a dependency at level 1. Either way, update the "Kein Tausch möglich" wording in the README and in the config description.

### WR-02: The validator accepts zero or several `final_budget_tier` events, but the gate, `penalty_params` and `TierTables` assume exactly one

**File:** `planspiel/validate.py:414-416`, `planspiel/validate.py:497-511`, `planspiel/rules.py:215-221`, `planspiel/rules.py:900-905`, `planspiel/gate.py:51-55`

**Issue:**
- **Several reviews:** `penalty_params` reads only the first event. `apply_final_events` applies all of them, so the penalty and the tier bonus are counted twice. `required_penalty_x` assumes `kz_final = clamp(kz_pre_review - X*steps)`, which is then false. With a duplicated Budget Review, the validator reports 0 errors and `gate_tier` still returns `passed=True` with `min_x_strict=1`, a verdict computed against the wrong model.
- **No review:** `final_events` may be empty. `gate_tier` then crashes with an uncaught `ValueError("Kein final_budget_tier-Event ...")`, so `planspiel gate` prints a traceback instead of a diagnostic.
- **Hidden coupling:** `TierTables.path_outcome` passes an empty selection `{}` to `apply_final_events`. This is only correct while the final events are Budget Reviews alone.

**Fix:** In `check_events`, require exactly one `final_budget_tier`:
```python
if isinstance(final_events, list):
    reviews = [e for e in final_events if isinstance(e, dict) and e.get("type") == "final_budget_tier"]
    if len(reviews) != 1:
        self.error("schema.event_placement", "final_events",
                   f"genau ein final_budget_tier-Event erforderlich, gefunden {len(reviews)}")
```

### WR-03: The gate checks "Überziehen lohnt sich nie" only on plans that are mostly not legal games, with zero margin; the README heading claims it in general

**File:** `planspiel/gate.py:1-9`, `README.md:174`, `CLAUDE.md` (gate instruction)

**Issue:** The gate runs on the static reference layer, where the Kurswechsel is not applied. Under the new rules the static plan is a legal game for only 48,115 of 782,336 start plans; every other team must swap. The configured X equals the minimum the gate allows in the low tier (`min_x_strict = 9`, `config_x = 9`), so there is no safety margin. Any path effect (the forced swap, a later trim in window 2) can flip the property in the real game, and nothing checks that.

The README bullet "Überziehen lohnt sich nie (automatisch geprüft)" and the CLAUDE.md instruction treat a passing gate as a balance guarantee. Deferring the path-level check to Phase 6 is documented and approved, but the wording oversells what is verified.

**Fix:**
- Reword the README heading, e.g. "auf dem Referenzplan automatisch geprüft; über Spielpfade erst ab Phase 6".
- Make `format_gate_report` print that the result applies only to the reference layer and print the margin `config_x - min_x_strict`.
- Consider a swap-layer variant of the gate: compare each over-budget swap path with the best in-budget swap path whose start and end are componentwise lower.

### WR-04: The per-wave evaluation and the ledger composition now exist in three to four copies; the single-definition guard cannot see this

**File:** `planspiel/rules.py:380-452` (`simulate_waves`), `planspiel/rules.py:735-783` (`TierKernel.evaluate`), `planspiel/rules.py:848-879` and `881-917` (`TierTables._fill` / `path_outcome`), `planspiel/rules.py:538-564` vs `611-688` (`evaluate_plan` vs `evaluate_path`)

**Issue:**
- **Wave loop:** the E-value / bonus / reduction / damage / KZ-change / event loop is copied almost line for line in `TierKernel.evaluate` and `TierTables._fill`, each with its own memo dictionaries. `simulate_waves` holds the reference version.
- **Ledger:** the composition `security_spend -> budget_ledger -> apply_final_events -> ros` is spelled out separately in `evaluate_plan`, `evaluate_path`, `TierKernel.evaluate` and `TierTables.path_outcome`.
- **Equivalence:** `evaluate_plan` is just `evaluate_path(..., Path(selection), enforce_kurswechsel=False)` plus key renames.
- **Guard blind spot:** `tests/test_single_definition.py` only checks function names, so these copies pass the "rules defined once" guard.
- **Drift risk:** a future per-wave mechanic has to be added in three places. Drift is caught only where the conformance tests sample (exhaustive on the 4-measure mini config, 2,000 random real paths under `-m slow`).

**Fix:**
- Move the per-state wave step into one helper and call it from `TierKernel.evaluate` and `TierTables._fill`, e.g. `_wave_step(wave, attack, slope, selection, cia, recovery_scaled, tier, ws, rs, memos) -> (change, damage, event_opex, event_budget)`.
- Move the ledger tail into `_close_ledger(tier, own, event_opex, event_budget, kz, final_selection)`.
- Implement `evaluate_plan` through `evaluate_path`.

### WR-05: The event-overrun warning covers only negative `flat_budget`, not OPEX-raising events in the last wave

**File:** `planspiel/validate.py:398-413`

**Issue:** `rules.event_without_window` fires only for a negative `flat_budget` in the last wave. An `opex_discount_per_active_measure` event with a positive `opex_per_measure` in the last wave raises `total_cost` through `event_opex` in `budget_ledger` (`rules.py:510-519`). That is the same budget squeeze with no change window to react in, and the validator says nothing.

The README's rule ("Events wie das Sparprogramm können ein Team ... über das Budget bringen ... der Validator warnt") is broader than what is checked.

**Fix:** Also warn when `event.get("type") == "opex_discount_per_active_measure"` and `opex_per_measure > 0` in the last wave. Alternatively, narrow the README sentence to `flat_budget` cuts.

### WR-06: `started_steps` is named and defaulted in euros, but every caller passes k€

**File:** `planspiel/rounding.py:20-28`

**Issue:** The signature is `started_steps(amount_eur, step_eur=10_000)` and the docstring talks about "10.000 €". Both production callers (`rules.budget_review_delta`, `gate.gate_from_columns`) pass the deficit in k€ with `step` in k€ (10). Any new caller that leaves out `step` and passes a ledger value (k€) gets steps of 10,000 k€, so practically no penalty. Nothing would flag it, because the result is still a plausible integer. `budget_review_delta`'s docstring even warns that the step "wird explizit an started_steps gegeben", which shows how easy this is to get wrong.

**Fix:** Remove the default and use unit-neutral names:
```python
def started_steps(amount: int, step: int) -> int:
    """Anzahl angefangener Schritte; amount und step in derselben Einheit (Ledger: k€)."""
```

## Info

### IN-01: The `rules.Path` NamedTuple shadows the usual `pathlib.Path` name

**File:** `planspiel/rules.py:572-574`

**Issue:** `from planspiel.rules import Path` (as in `tests/test_swap_layer.py:17`, `tests/test_paths.py`) shadows `pathlib.Path` in modules that also handle file paths (`REPO_ROOT / ...`). This is an easy source of confusing type errors.

**Fix:** Rename it to `GamePath` or `PlanPath`.

### IN-02: `penalty_rows` stops at the first row whose penalty reaches the KZ scale, so there is no row for larger overspends

**File:** `planspiel/review_text.py:11-20`

**Issue:** With X = 9 the table ends at "110.001 – 120.000 € → −108". A team that overspends by more than 120.000 € finds no row on a generated card.

**Fix:** Have the print layer (Phase 5) add a final "darüber → KZ 0" row, or return an open-ended last row.

### IN-03: `evaluate_plan` does not expose `kz_pre_review` / `remaining`, while `evaluate_path` does

**File:** `planspiel/rules.py:538-564`, `tests/support/harness.py:79-96`

**Issue:** `compact_from_plan` has to rebuild both values (`rec["waves"][-1]["kz_after"]`, `budget_available - total`). The two reference evaluators return different result shapes for the same concept.

**Fix:** Covered by WR-04: implement `evaluate_plan` through `evaluate_path`.

### IN-04: `HandCalcWarning` is used for warnings that are not about hand calculation

**File:** `planspiel/config.py:111-113`

**Issue:** `schema.removed_key` and `rules.event_without_window` are issued as `HandCalcWarning`. Filters on that category, such as `--strict` semantics in Phase 6, will also catch schema and rule warnings.

**Fix:** Add a `ConfigWarning` base class with `HandCalcWarning` as a subclass, or pick the category from the issue code prefix.

### IN-05: A slow test asserts wall-clock time

**File:** `tests/test_swap_layer.py:305`

**Issue:** `assert seconds <= 900` makes `-m slow` flaky on a slower or busy machine. Earlier runs took about 220-240 s per tier.

**Fix:** Print the runtime instead of asserting it, or move the check into the dedicated perf test.

### IN-06: The exact-arithmetic functions are annotated with `float`

**File:** `planspiel/rules.py:188`, `planspiel/rules.py:203`

**Issue:** `_tier_lookup(value: float, tiers: List[List[float]])` and `budget_review_delta(remaining: float, ...)` take ints or Fractions only. The `float` hints contradict the module's no-float rule and invite float inputs.

**Fix:** Annotate as `int` (ledger k€) or `Union[int, Fraction]`.

---

_Reviewed: 2026-10-05_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
