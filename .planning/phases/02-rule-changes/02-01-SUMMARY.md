---
phase: 02-rule-changes
plan: 01
subsystem: rules
tags: [e-target, rule-removal, golden-snapshot, enumeration-kernel, validator, rule-08]
requires: []
provides:
  - "E-target bonus/malus removed from config, loader, validator, rules and kernel (RULE-08, D-19)"
  - "planspiel/rules.py: wave_kz_change(attack_kz_delta, event_kz) (two arguments)"
  - "validator warning schema.removed_key for stale e_targets/kz_bonus/kz_malus keys"
  - ".planning/phases/02-rule-changes/tools/golden_diff.py (dump/report, EXPECTED entry 02-01)"
  - "tests/test_e_target_removed.py"
  - "E-target-free goldens as the baseline for every later Phase-2 golden diff"
affects: [02-02, 02-03, 02-04, 02-05, 02-06, 02-07, 02-08]
tech-stack:
  added: []
  patterns: ["all-combination before/after dump diff with hard expectations before regenerating goldens", "blocking human review of the golden update summary (D-20)"]
key-files:
  created:
    - .planning/phases/02-rule-changes/tools/golden_diff.py
    - .planning/phases/02-rule-changes/02-01-GOLDEN-DIFF.md
    - tests/test_e_target_removed.py
  modified:
    - simulation_config.json
    - tests/fixtures/mini_config.json
    - planspiel/config.py
    - planspiel/validate.py
    - planspiel/rules.py
    - planspiel/rounding.py
    - planspiel/report.py
    - planspiel/balance.py
    - tests/support/digest.py
    - tests/support/harness.py
    - tests/support/golden_cases.py
    - tests/test_kernel_conformance.py
    - tests/test_rules_exact.py
    - tests/test_rules_semantics.py
    - tests/test_digest.py
    - tests/test_enumeration.py
    - tests/test_validate.py
    - tests/test_single_definition.py
    - tests/golden/characterization_low.json
    - tests/golden/characterization_medium.json
    - tests/golden/characterization_high.json
    - tests/golden/digest_low.json
    - tests/golden/digest_medium.json
    - tests/golden/digest_high.json
    - README.md
    - CLAUDE.md
    - .planning/PROJECT.md
    - .gitignore
key-decisions:
  - "RULE-08 / D-19: the per-wave E-target bonus/malus is removed, because no printed MHP material mentions it; the simulation now matches the paper game"
  - "D-20: the resulting snapshot change is committed as one reviewed commit with per-tier numbers in the message; goldens changed only through --update-golden after the blocking review"
  - "Stale e_targets/kz_bonus/kz_malus keys in an old config are ignored by the loader and reported as schema.removed_key (cannot change results)"
  - "generate_attack_calculator.py is retired (D-29); it raises KeyError if run and is archived in Phase 7 (LEG-01)"
requirements-completed: [RULE-08]
duration: n/a (multi-session with review checkpoint)
completed: 2026-10-02
status: complete
---

# Phase 2 Plan 01: Remove the E-target bonus/malus Summary

The unprinted per-wave E-target bonus/malus is gone from config, loader, validator, rules and the enumeration kernel; the per-wave KZ change is now attack + events, rounded once and clamped to 0-100, and the resulting snapshot change was reviewed on all 3 x 782,336 combinations before the goldens were regenerated.

## Tasks

| Task | Name | Commit |
|------|------|--------|
| 1 | Golden diff tool and pre-change dumps | 18298c2 |
| 2 RED | Failing tests for the removal | e36a39b |
| 2 GREEN | Remove the mechanic (code, config, fixtures) | 7d3f239 (shared with the reviewed goldens, by plan) |
| 3 | Docs, diff report, golden regeneration | 7d3f239 (goldens), deea583 (docs, report) |
| 4 | Review checkpoint (user replied "approved") | 7d3f239, deea583 |

Commits:

- `18298c2` chore(02-01): add golden diff tool for phase-2 snapshot reviews
- `e36a39b` test(02-01): add failing tests for removing the E-target bonus/malus
- `7d3f239` feat(02-01): remove the unprinted E-target bonus/malus from the simulation
- `deea583` docs(02-01): document the E-target removal

## Runs

- RED (`e36a39b`): 60 failed / 201 passed, as intended.
- Checkpoint (before commit): `uv run pytest -q` 265 passed; `uv run pytest -m slow -q` 11 passed in 1010.89 s (not re-run after the commits, by instruction).
- After the commits: `uv run pytest -q` 265 passed, 11 deselected (14.64 s).
- `uv run planspiel validate`: 0 errors, 1 warning (`hand_calc.kz_slope attacks.exfil`, as expected).

## Snapshot change reviewed (3 x 782,336 combinations)

Report: `.planning/phases/02-rule-changes/02-01-GOLDEN-DIFF.md`. In every tier the in-budget count is unchanged, over-budget flips are 0, and damage, RoS, own cost and budget are unchanged for all combinations; only KZ moves.

| Tier | In-budget count | KZ changed | Mean KZ shift | Best in-budget KZ | Best over-budget KZ |
|------|-----------------|------------|---------------|-------------------|---------------------|
| low | 69,454 -> 69,454 | 512,006 | -8.84 | 100 -> 98 | 85 -> 85 |
| medium | 124,321 -> 124,321 | 648,246 | -12.84 | 100 -> 100 | 85 -> 85 |
| high | 197,753 -> 197,753 | 739,828 | -16.56 | 100 -> 100 | 85 -> 85 |

These match the research expectations. Spot check approved by the user: empty plan in medium, `kz_final` 15 -> 19, `kz_after` [33, 3, 0] -> [36, 11, 4] (the malus -3/-5/-7 no longer applies).

Digest goldens keep `"count": 782336` and the unchanged `in_budget` values.

## Deliberately rewritten tests

E-target tie and clamp tests (`test_negative_tie_rounds_down_with_test_only_wave3_event`, `test_clamp_happens_after_rounding`), the empty-plan KZ (`test_empty_selection_medium_without_e_target`), the digest mutation (`test_digest.py`), the validator parameter (`test_validate.py`), `test_wave_kz_change_rounds_once_half_away` (two-argument form), `test_gesamtreduktion_compared_exactly_with_threshold`. Removed: `test_e_target_check_reached_at_equality`, `test_e_target_check_missed`.

## Deviations from Plan

None - plan executed as written. Note: the plan's Task 2 files `tests/test_*.py` were committed as RED in `e36a39b`; `tests/test_e_target_removed.py` received a further README/CLAUDE.md check in Task 3 and is part of `7d3f239`.

## Auth gates

None.

## Known Stubs

None.

## Threat Flags

None. `generate_attack_calculator.py` (T-02-05, accepted) now raises KeyError when run; it is retired (D-29) and archived in Phase 7 (LEG-01). Dumps stayed in the gitignored `golden-diff/` directory (T-02-04); nothing from it was committed.

## Self-Check

## Self-Check: PASSED

- FOUND: tools/golden_diff.py, 02-01-GOLDEN-DIFF.md, tests/test_e_target_removed.py
- FOUND commits: 18298c2, e36a39b, 7d3f239, deea583
- `git status --porcelain -- planspiel tests simulation_config.json README.md CLAUDE.md` is empty; `golden-diff/` is gitignored and untracked
