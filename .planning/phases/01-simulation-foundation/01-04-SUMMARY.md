---
phase: 01-simulation-foundation
plan: 04
subsystem: simulation-core
tags: [refactor, planspiel-package, single-definition, thin-wrappers, ros, final-index]
requires: ["01-03"]
provides:
  - "planspiel/config.py: dataclasses, Config, load_config (UTF-8)"
  - "planspiel/rules.py: every game formula once, plus evaluate_plan, over_budget, base_losses, ros, final_index"
  - "planspiel/enumerate.py, simulate.py, analyze.py, balance.py: the logic behind the three root scripts"
  - "tests/test_single_definition.py: AST guard (formulas once in rules.py, retired scorers gone, no imports of root scripts)"
  - "tests/fixtures/mini_config.json: 4-measure config (M1, M2, M4, M6; 256 codes)"
affects: [01-05, 01-06, 01-07]
tech-stack:
  added: []
  patterns: ["verbatim move under golden/digest guard", "thin wrapper: planspiel import + main guard only", "AST test as single-definition guard"]
key-files:
  created:
    - planspiel/config.py
    - planspiel/rules.py
    - planspiel/enumerate.py
    - planspiel/simulate.py
    - planspiel/analyze.py
    - planspiel/balance.py
    - tests/test_rules_semantics.py
    - tests/test_wrappers.py
    - tests/test_single_definition.py
    - tests/fixtures/mini_config.json
  modified:
    - simulate_outcomes.py
    - analyze_simulation_results.py
    - balance_analysis.py
    - tests/support/harness.py
    - tests/support/golden_cases.py
    - tests/test_config_text.py
    - tests/test_harness_vs_run_simulation.py
key-decisions:
  - "Dead selection_to_key was dropped (repo-wide grep: no caller; only mentioned in .claude/CLAUDE.md prose)"
  - "In-budget filter in run_simulation now evaluates every dependency-valid plan through evaluate_plan (final events computed for over-budget plans too) and drops the over_budget/ros keys before writing; output is byte-identical to the old script"
  - "balance report flags over-budget strategies in best/worst and TIER-VERGLEICH lines with [ÜBER BUDGET] instead of hiding them; the 'KEINE STRATEGIE PASST INS BUDGET' message became 'KEINE STRATEGIE AUSWERTBAR' because over-budget strategies are no longer skipped"
requirements-completed: [FOUND-03]
duration: ~50min
completed: 2026-09-30
status: complete
---

# Phase 1 Plan 04: Shared rules package and thin wrappers Summary

All game formulas now live once in `planspiel/rules.py` (moved verbatim from `simulate_outcomes.py`), the shared plan-level functions `evaluate_plan`, `over_budget`, `base_losses`, `ros` and `final_index` were added test-first, the three root scripts are 5-line wrappers, and the 01-03 golden samples and full digests pass with zero diff.

## Tasks

| Task | Name | Commits |
|------|------|---------|
| 1 | Config and formulas into planspiel, shared plan-level functions, golden adapter swap | RED 1972788, GREEN ce37d0f |
| 2 | Simulate path as thin wrapper, mini fixture config | 45f9e67 |
| 3 | Analyze and balance on shared rules, thin wrappers, single-definition guard | 05cabab |

## What changed

- `planspiel/config.py`: seven dataclasses verbatim, new `Config` dataclass (`measure_ids` property), `load_config` returns `Config`; the twice-written Event construction is one private `_build_event`.
- `planspiel/rules.py`: `dependencies_satisfied` ... `simulate_selection` verbatim (float order, comments, German strings), plus `base_losses`, `ros` (None at cost 0), `final_index`, `over_budget`, `evaluate_plan` (the former harness composition; returns legacy keys plus `over_budget` and `ros`).
- `tests/support/harness.py`: adapter now delegates to `rules.evaluate_plan` (`STAGE` stays `"legacy-float"`); the harness-local base-loss/RoS code is gone.
- `planspiel/simulate.py`: legacy `run_simulation` rebuilt on `evaluate_plan` + `over_budget` (keeps the `--budget-max` quirk: only feeds the utilization threshold), `parse_args(argv)`, `main(argv) -> int`.
- `planspiel/analyze.py`: uses `rules.base_losses` (via `load_config`, so 01-05's validator covers it), `rules.ros`, `rules.final_index`; the five inline RoS blocks and two sort-key variants are one helper each; a None RoS prints `RoS: n/a` and Final-Index falls back to KZ (D-27).
- `planspiel/balance.py`: canonical semantics (D-24). Evaluates via `evaluate_plan`, flags `[ÜBER BUDGET]`, ranks by `Final-Index (vorläufig)`; combined score, local RoS helper, simulated baseline and local budget skip removed; cost reference via `compute_costs`; `POSITIVE_KZ_THRESHOLD = 50` labelled presentation constant; stale 300k/400k/500k tier comments deleted; umlauts in console strings and strategy descriptions.
- `tests/fixtures/mini_config.json`: real config reduced to M1, M2, M4, M6 (256 codes) with the event adjustments from the plan.

## Verification output

Fast suite (after Task 3):
```
uv run pytest -q
84 passed, 4 deselected in 3.32s
```

Slow suite after the refactor, no `--update-golden`:
```
uv run pytest -m slow -q
....                                                                     [100%]
4 passed, 84 deselected in 244.72s (0:04:04)
```
(3 x 782,336-combination digests plus the `run_simulation` vs harness cross-check.) The digest run after Task 1 alone: `3 passed, 1 deselected in 151.13s`; cross-check after Task 2: `1 passed in 97.93s`. `git status --porcelain tests/golden` is empty.

Extra proof for D-26 (legacy `--output` unchanged): the pre-refactor `simulate_outcomes.py` (from `git show HEAD~`) and the new wrapper were run on the real config for all three tiers with `--budget-utilization 0.85`; `cmp` reports byte-identical result files (131,409,858 / 237,677,493 / 361,912,864 bytes) and identical stdout summaries.

`uv run python balance_analysis.py | head -40` (excerpt, first strategy blocks; medium/high tiers contain 27 `ÜBER BUDGET` markers overall):
```
KOSTEN-REFERENZ (Init + 3*OPEX)
L1: M1=42, M2=26, M3=36, M4=34, M5=46, M6=16, M7=32, M8=28, M9=27, M10=18
L2: M1=90, M2=74, M3=86, M4=76, M5=88, M6=42, M7=68, M8=60, M9=61, M10=43
BUDGET-TIER: LOW (Budget: 350k, KZ-Start: 50, Sev-Mult: 1.0)
Smart Basis
  Kosten: 178k | CIA: C=20, I=24, A=21
  >> KZ=75.68 [OK], Dmg=532k, RoS=-0.50, Final-Index (vorläufig)=25.3
...
TIER-VERGLEICH
Tier     Best Strategy          KZ      Dmg     RoS Final-Index (vorläufig)
low      OT Protection         100      58k    0.70                    170.4
```

## TDD

Task 1 RED (`uv run pytest tests/test_rules_semantics.py -q`): `ModuleNotFoundError: No module named 'planspiel.config'`; GREEN: all pass. Task 3 guard sensitivity: a temporary duplicate `def ros` reading `.s_unit` in `planspiel/analyze.py` made `test_formula_defined_once_in_rules[ros]` and `test_no_formula_operands_outside_rules_and_config` fail; reverted, 23 passed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] balance_analysis.py import stopgap between Task 2 and Task 3**
- **Found during:** Task 2 (`test_documented_wrappers_run[balance_analysis]` failed once `simulate_outcomes.py` became a wrapper)
- **Issue:** the legacy `balance_analysis.py` still imported `load_config` etc. from `simulate_outcomes`, so committing Task 2 alone left a broken script and a red suite.
- **Fix:** minimal import/`load_config` unpacking edit in `balance_analysis.py` in the Task 2 commit; superseded by the rebuild in Task 3.
- **Files modified:** `balance_analysis.py`
- **Commit:** 45f9e67

**2. [Note] "KEINE STRATEGIE PASST INS BUDGET!" reworded**
- Over-budget strategies are now evaluated and flagged (D-24), so a tier with no result means no dependency-valid strategy; the message says `KEINE STRATEGIE AUSWERTBAR!`.

No other deviations.

## Removed dead code

`selection_to_key` (was `simulate_outcomes.py` L500-501): repo-wide grep over `*.py`/`*.md` found no caller (only a prose mention in `.claude/CLAUDE.md` naming conventions). Deleted with the move.

## Auth gates

None.

## Known Stubs

None.

## Threat Flags

None. T-01-10 mitigated (golden sample + full digests + cross-check unchanged, byte-identical legacy output); T-01-11 mitigated (`ros` returns None at cost 0, `test_analyze_handles_zero_cost_plan`); T-01-12 accepted, behaviour unchanged.

## Self-Check: PASSED

Created files exist (`planspiel/{config,rules,enumerate,simulate,analyze,balance}.py`, `tests/test_rules_semantics.py`, `tests/test_wrappers.py`, `tests/test_single_definition.py`, `tests/fixtures/mini_config.json`); commits 1972788, ce37d0f, 45f9e67, 05cabab present in `git log`; wrappers have 5 non-empty lines each.
