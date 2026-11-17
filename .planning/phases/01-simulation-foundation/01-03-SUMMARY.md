---
phase: 01-simulation-foundation
plan: 03
subsystem: testing
tags: [characterization, golden-files, sha256-digest, pytest, update-golden]
requires: ["01-02"]
provides:
  - "tests/support/harness.py: evaluate(cfg, tier, selection) adapter over the legacy run_simulation loop body (STAGE legacy-float)"
  - "tests/support/golden.py: check_golden with --update-golden rewrite and 'tier code | field | old -> new' summary"
  - "tests/support/golden_cases.py: deterministic case finder (seed 20260930) with tag contract"
  - "tests/support/digest.py: streaming sha256 digest over all 782,336 valid combinations per tier"
  - "six committed golden files: characterization_{low,medium,high}.json, digest_{low,medium,high}.json"
affects: [01-04, 01-05, 01-06, 01-07]
tech-stack:
  added: []
  patterns: ["golden files change only via --update-golden", "sample membership stored in the golden file, not re-derived", "slow marker for full enumeration"]
key-files:
  created:
    - tests/conftest.py
    - tests/support/harness.py
    - tests/support/golden.py
    - tests/support/golden_cases.py
    - tests/support/digest.py
    - tests/test_golden_support.py
    - tests/test_characterization.py
    - tests/test_digest.py
    - tests/test_harness_vs_run_simulation.py
    - tests/golden/characterization_low.json
    - tests/golden/characterization_medium.json
    - tests/golden/characterization_high.json
    - tests/golden/digest_low.json
    - tests/golden/digest_medium.json
    - tests/golden/digest_high.json
  modified: [.gitattributes]
key-decisions:
  - "Wave-3 tie cases are deduplicated per (wave, bonus, E-value) instead of per (bonus, E-value, event KZ): 4 tie cases per tier instead of 15, so the sample stays within the 45-70 target"
  - "check_golden compares parsed JSON with a strict recursive equality (type-aware), so 3.0 -> 3 or 22.5 -> \"22.5\" are detected and reported as representation-only changes"
requirements-completed: [FOUND-02]
duration: 55min
completed: 2026-09-30
status: complete
---

# Phase 1 Plan 03: Golden characterization and full digests Summary

Today's legacy-float outputs are pinned before any refactoring: a readable golden sample per tier (61-63 unique selections), a sha256 digest with counts and KZ histogram over all 782,336 dependency-valid combinations per tier (slow marker only), a `--update-golden` path with a domain-readable diff, and a slow cross-check that ties the harness to the real `run_simulation`.

## Tasks

| Task | Name | Commits |
|------|------|---------|
| 1 | Golden infrastructure: harness adapter, `--update-golden`, readable diff | RED 8f32b37, GREEN b46a078 |
| 2 | Case finder and per-tier characterization capture with mutation tests | 6b9e255 |
| 3 | Full per-tier digest and slow cross-check against `run_simulation` | d4b2fa6 |

Legacy code (`simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`) is untouched (`git diff` over the plan's commits is empty). `simulation_config.json` is unchanged (`git diff --quiet` exits 0).

## TDD

Task 1 RED (`uv run pytest tests/test_golden_support.py -q`): collection error `ModuleNotFoundError: No module named 'tests.support.golden'`. GREEN: `20 passed in 0.94s`. Task 2 and 3 are characterization captures (pass by construction), covered by permanent mutation tests plus the manual mutation run below.

## Golden sample size

Unique codes per tier after dedupe: low 62, medium 61, high 63 (`grep -c '"code"'`). Each has 4 `census:tie_w3:` cases (medium: `0/28.5/0`, `6/22.5/0`, `8/20.5/-10`, `9/19.5/0`), a `census:wave_clamp_high` and `census:wave_clamp_low` case, and `census:remaining_{-1,0,24,25,49,50,74,75}`. All 27 strategy names are present (26 unique codes: "Maximum Coverage" and "Realistic Max" share one).

## Digest results (legacy-float)

| Tier | count | in_budget | over_budget | digest |
|------|-------|-----------|-------------|--------|
| low | 782336 | 69454 | 712882 | f7aa5bef...faea0 |
| medium | 782336 | 124321 | 658015 | ebf16bbb...ea93 |
| high | 782336 | 197753 | 584583 | bddfa3de...9cf3c9 |

The in-budget counts equal the research-measured legacy counts. `sum_damage` is `34846331.68000199` in all three tiers (damage does not depend on the tier).

## Verification output

Golden bootstrap, characterization (3 census scans): `9 passed in 159.06s`. Without the flag: `9 passed in 0.17s`.

Digest bootstrap: `uv run pytest -m slow tests/test_digest.py --update-golden -q` -> `3 passed, 1 deselected in 152.07s (0:02:32)`.

Slow suite without the flag (4 slow tests: 3 digests + harness cross-check; `test_digest_is_deterministic_and_sensitive` is a fast test and is deselected by `-m slow`, so the run reports 4 passed, 1 deselected):
```
uv run pytest -m slow tests/test_digest.py tests/test_harness_vs_run_simulation.py -q
....                                                                     [100%]
4 passed, 1 deselected in 232.26s (0:03:52)
```

Fast suite (slow tests deselected):
```
uv run pytest -q
..............................................                           [100%]
46 passed, 4 deselected in 1.73s
```

`git status --porcelain` after the final task commit: empty (golden files committed).

### Manual mutation run (sensitivity proof)

`simulation_config.json` wave-1 `"e_threshold": 23` changed to 24, then `uv run pytest tests/test_characterization.py -q -k medium`:
```
F.                                                                       [100%]
golden file characterization_medium.json differs: 276 differences
medium 0121011000 | kz_final | 70.2 -> 68.2
medium 0121011000 | total_damage | 489.2 -> 507.2
medium 0121011000 | cia_mali.c | -37.8 -> -39.8
medium 0121011000 | waves[0].capped_reduction | 4.6 -> 3.6
medium 0121011000 | waves[0].damage | 61.199999999999974 -> 79.19999999999997
medium 0121011000 | ros | -0.28913043478260864 -> -0.38695652173913037
... 246 more
1 failed, 1 passed, 7 deselected in 0.08s
```
Restore with `git checkout -- simulation_config.json` (then `git diff --quiet -- simulation_config.json` succeeds), re-run:
```
..                                                                       [100%]
2 passed, 7 deselected in 0.06s
```

The permanent mutation tests (`wave1_e_threshold`, `budget_review_boundary_25`) also pass: both mutations change at least one golden case, the boundary mutation changes the `census:remaining_25` case, and the digest of the first 3,000 codes changes with `kz_malus - 1`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Wave-3 tie cases deduplicated per (wave, bonus, E-value)**
- **Found during:** Task 2, first capture
- **Issue:** The plan defines a tie signature as `(bonus_reduction, e_value, event_kz)` and expects research's five signatures. The full census finds 15 distinct signatures for wave 3 (event KZ takes 5-value steps between -10 and +20), which pushed the medium golden to 72 unique codes and broke the acceptance range of 45-70. The rounding behaviour depends only on the wave total's `.5` fraction, and all 15 have positive totals and are unclamped in most codes, so the extra event-KZ variants add no rounding information.
- **Fix:** One tie case per `(wave, bonus, e_value)` (first code in enumeration order, tag keeps the `census:tie_w<n>:<bonus>/<e_value>/<event_kz>` format with that code's event KZ). Four tie cases per tier remain, all in wave 3, so the tag contract for plan 01-06 (`census:tie_w3:`) is unchanged.
- **Files modified:** `tests/support/golden_cases.py`, golden files regenerated before commit
- **Commit:** 6b9e255

**2. Task-order note:** the plan's Task 3 verify command runs `uv run pytest -m slow ...` which selects only slow tests; the fast `test_digest_is_deterministic_and_sensitive` is verified by the plain `uv run pytest` run. No behaviour deviation.

## Auth gates

None.

## Known Stubs

None.

## Threat Flags

None. `sim_low.json`, `sim_med.json` and `sim_high.json` were never opened; digests stream sha256 per line (T-01-09). Golden files change only through `--update-golden` (T-01-07). The manual mutation run restored the config via `git checkout` and asserted it clean (T-01-08).

## Self-Check: PASSED

All created files exist (nine test/support modules, six golden files); commits 8f32b37, b46a078, 6b9e255, d4b2fa6 present in `git log`.
