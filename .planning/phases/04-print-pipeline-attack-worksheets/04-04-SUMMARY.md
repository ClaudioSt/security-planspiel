---
phase: 04-print-pipeline-attack-worksheets
plan: 04
subsystem: worksheet-equivalence-proof
tags: [equivalence, replay, negative-controls, rounding, tdd, print-pipeline]

requires:
  - phase: 04-print-pipeline-attack-worksheets
    provides: AttackSheet exact fields (printmodel.py, plan 04-02)
provides:
  - tests/support/worksheet_replay.py, an independent replay of the printed worksheet steps
  - fast dense-grid equivalence tests with negative controls and the D-09 two-decimal brute force
  - slow replay of every dependency-valid plan of every tier
affects: [04-06 attack worksheet template and PDF commit]

tech-stack:
  added: []
  patterns:
    - "The replay reads only AttackSheet exact fields; an AST test bars it from importing planspiel.rules or planspiel.rounding"
    - "apply_attack key set is pinned as REPLAYED | DERIVED_NOT_PRINTED | UNPRINTED_UNSCORED, so a new simulation mechanic fails the suite until the sheet carries it"
    - "Negative controls monkeypatch planspiel.rules at call time and require the grid helper to report mismatches"

key-files:
  created:
    - tests/support/worksheet_replay.py
    - tests/test_worksheet_replay.py
    - tests/test_worksheet_equivalence.py
    - tests/test_worksheet_equivalence_full.py
  modified: []

key-decisions:
  - "replay_recovery_factor is a separate public helper (used by replay_steps) so the grid can compare recovery_factor with the simulation without widening SheetResult"
  - "The grid places E = GR - bonus on the first non-zero weight even when E is negative; e_value_scaled needs no integrality guard beyond the 1/ws lattice, and the clamp at 0 makes low GR points valid Fall-1 inputs"
  - "Negative control on wave_kz_change was added to the three required ones, so the rounding step itself is proven to be compared"

requirements-completed: [PRINT-04]

duration: 40min
completed: 2026-10-22
status: complete
---

# Phase 4 Plan 04: Worksheet Equivalence Proof Summary

**An independent replay of the printed hand-calculation steps reproduces `rules.apply_attack` and `rules.wave_kz_change` at 36,467 grid comparisons and for all 782,336 dependency-valid plans of each tier (0 mismatches), and the suite fails when recovery, attack KZ, bonus or rounding is altered in the simulation.**

## Accomplishments

- `tests/support/worksheet_replay.py` encodes the sheet a second time: `paper_round`, `replay_e_value`, `replay_bonus`, `replay_recovery_factor`, `replay_steps` (cap line check first, then Fall 1/2/3, recovery, wave KZ change), `replay_wave`, `event_kz_bounds`, plus the three key sets `REPLAYED_KEYS`, `DERIVED_NOT_PRINTED_KEYS`, `UNPRINTED_UNSCORED_KEYS = {"cia_delta"}` (D-21). It calls no `planspiel.rules` function and imports neither `planspiel.rules` nor `planspiel.rounding` (AST test).
- The fast grid covers, per wave, every Gesamtreduktion on the 1/ws lattice from three below Fall 1 to three above Fall 2 (both bounds exactly), every level 0..3 assignment of the bonus measures and the recovery measure, and every integer of `event_kz_bounds`. It compares e_value, bonus_reduction, gesamtreduktion, damage in euros, recovery_factor, kz_delta and the rounded wave KZ change.
- The E-step equals `rules.e_value_scaled` for every reachable CIA triple (DP superset, dependencies ignored); the printed bonus rule and the bonus rows equal `compute_bonus_reduction` and `wave.bonus_measures` for every level assignment.
- The D-09 brute force confirms that carrying two decimals (cut off or rounded) never changes the rounded wave KZ change, and that the fraction-slope sheet carries `kz_fraction_hint` (terminating slopes carry `kz_decimals_hint`).
- The slow replay walks every enumerated plan of low, medium and high through the sheet steps, chains the KZ with a test-side clamp to 0..100 and matches `kz_after` and `damage_eur`.

## Task Commits

1. Task 1 RED: `d76df35` test(04-04): add failing worksheet replay tests
2. Task 1 GREEN: `12f1607` test(04-04): add the worksheet replay and the apply_attack key guard
3. Task 2: `e237415` test(04-04): prove worksheet steps equal the simulation over the dense grid
4. Task 3: `afade46` test(04-04): replay every enumerated plan through the worksheet steps

RED run (Task 1): `tests/test_worksheet_replay.py` failed at collection with `ModuleNotFoundError: No module named 'tests.support.worksheet_replay'`.

## Verification

- `uv run pytest -q`: 1057 passed, 30 deselected (baseline 1016; +25 replay tests, +16 equivalence tests); the slow file is not run.
- `uv run pytest -m pdf -q`: 8 passed.
- `uv run pytest tests/test_worksheet_replay.py tests/test_worksheet_equivalence.py -q`: 41 passed in 12 s; slowest test 2.6 s (a negative-control grid run). `tests/test_single_definition.py` stays green.
- `uv run pytest -m slow tests/test_worksheet_equivalence_full.py -v -s --durations=0`: 3 passed in 248 s.

### Grid point counts (real config)

| Wave | Comparisons (grid points plus event sweeps) |
|------|---------------------------------------------|
| 1 | 9,105 |
| 2 | 14,647 |
| 3 | 12,715 |
| total | 36,467 (asserted above 10,000) |

### Negative controls (RED proof that the comparison can fail; first mismatch line of each)

- `compute_recovery` + 1/10: `wave 1 GR 20 levels {'M3': 0, 'M4': 0, 'M6': 0} damage: replay 160000 != simulation 144000`
- `attack_kz_delta` + 1: `wave 1 GR 20 levels {'M3': 0, 'M4': 0, 'M6': 0} kz_delta: replay -6 != simulation -5`
- `compute_bonus_reduction` + 1: `wave 1 GR 20 levels {'M3': 0, 'M4': 0, 'M6': 0} bonus_reduction: replay 0 != simulation 1`
- `wave_kz_change` + 1 (extra control): reports `change` mismatches.

### Slow replay (one test per tier)

| Tier | Plans checked | Mismatches | Runtime |
|------|---------------|------------|---------|
| low | 782,336 | 0 | 85 s |
| medium | 782,336 | 0 | 81 s |
| high | 782,336 | 0 | 82 s |

The plan count equals an independent count (all 4^10 level combinations filtered by `rules.dependencies_satisfied`).

### Event-KZ sets per wave

| Wave | `event_kz_bounds` range (fast grid) | Exact set from the dependency-valid plans (all three tiers, identical) | Research reference |
|------|--------------------------------------|-----------------------------------------------------------------------|--------------------|
| 1 | 0 ... 0 (`range(0, 1)`) | {0} | {0} |
| 2 | -20 ... 22 (`range(-20, 23)`, 43 values) | {-20, -10, -5, -2, 0, 3, 5, 7, 8, 12, 15, 18, 22} (13 values) | {-20, -10, -5, -2, 0, 2, 3, 5, 7, 8, 12, 15, 18, 22} (14 values) |
| 3 | -10 ... 50 (`range(-10, 51)`, 61 values) | {-10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50} (13 values) | same 13 values |

One difference: the value `2` of wave 2 is in the research reference (taken over all 4^10 selections) but not in the dependency-valid plans, which is the omission the research already noted. Every exact set lies inside the range, so the fast grid's event axis is a strict superset.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] `replay_recovery_factor` helper**
- **Found during:** Task 2
- **Issue:** the plan compares `recovery_factor` with the simulation, but `SheetResult` carries no factor and the plan fixes its field list.
- **Fix:** the table lookup moved into the public helper `replay_recovery_factor`, which `replay_steps` also uses; `SheetResult` unchanged.
- **Files modified:** tests/support/worksheet_replay.py
- **Commit:** e237415

**2. [Rule 2 - Missing critical functionality] Fourth negative control**
- **Found during:** Task 2
- **Issue:** the plan lists three controls (recovery, attack KZ, bonus), and none of them exercises `wave_kz_change`, so a vacuous rounding comparison would go unnoticed (T-04-14).
- **Fix:** added a control on `wave_kz_change` so the rounding comparison is shown to fail too.
- **Commit:** e237415

Otherwise the plan was executed as written. No model or rules bug was found, so `planspiel/printmodel.py` and `planspiel/rules.py` are unchanged.

## Decisions Made

See key-decisions in the frontmatter. The replay was never bent toward the simulation.

## Known Stubs

None.

## Threat Flags

None beyond the plan's threat model. T-04-13 is covered by the key-set guard plus grid and slow replay, T-04-14 by the negative controls, the grid point assertion, the plan-count assertion and the AST import check, T-04-15 by the two-decimal brute force and the hint assertion.

## Issues Encountered

`HandCalcWarning hand_calc.kz_slope attacks.exfil` (slope 17/7) shows on every `load_config`; it is the known warning that stays until Phase 6 (BAL-02), not an error.

## Next Phase Readiness

Plan 04-06 can commit the PDFs knowing the printed steps and the simulation agree for every plan; any later change to the config or to `apply_attack` that breaks this fails the fast suite, and the slow file re-proves it over all plans. PRINT-03 stays pending until 04-06.

## Self-Check: PASSED

- Files exist: tests/support/worksheet_replay.py, tests/test_worksheet_replay.py, tests/test_worksheet_equivalence.py, tests/test_worksheet_equivalence_full.py.
- Commits d76df35, 12f1607, e237415, afade46 present in `git log`.
