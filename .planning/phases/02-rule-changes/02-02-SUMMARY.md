---
phase: 02-rule-changes
plan: 02
subsystem: rules
tags: [ros, own-spend, budget-ledger, golden-snapshot, rule-06, wr-06]
requires: [02-01]
provides:
  - "rules.security_spend(init, opex_by_wave, window_costs=()) -> int (registered in FORMULA_FUNCTIONS)"
  - "BudgetLedger.security_spend (fifth field); rules.ros(base_losses, total_damage, own_spend); rules.budget_ledger(tier_budget, own_spend, event_opex, event_budget)"
  - "evaluate_plan output key costs.security_spend"
  - "rules.final_index returns weight_kz * kz_final when RoS is None (WR-06)"
  - "tests/test_ros_ledger.py"
  - "golden_diff.py EXPECTED['02-02'] and 02-02-GOLDEN-DIFF.md"
affects: [02-03, 02-04, 02-05, 02-06, 02-07, 02-08]
tech-stack:
  added: []
  patterns: ["one own_spend input for RoS in store/report/dump/analyze", "total_cost keeps budget meaning, digest-stable"]
key-files:
  created:
    - tests/test_ros_ledger.py
    - .planning/phases/02-rule-changes/02-02-GOLDEN-DIFF.md
  modified:
    - planspiel/rules.py
    - planspiel/enumerate.py
    - planspiel/report.py
    - planspiel/analyze.py
    - tests/support/harness.py
    - tests/test_kernel_conformance.py
    - tests/test_enumeration.py
    - tests/test_rules_semantics.py
    - tests/test_single_definition.py
    - tests/golden/characterization_low.json
    - tests/golden/characterization_medium.json
    - tests/golden/characterization_high.json
    - README.md
    - CLAUDE.md
    - .planning/PROJECT.md
    - .planning/phases/02-rule-changes/tools/golden_diff.py
key-decisions:
  - "RULE-06 / D-21 / D-12: RoS divides by the team's own security spend only (Init, regular OPEX, window costs incl. the Kurswechsel difference); event OPEX penalties/discounts and event budget changes no longer move it"
  - "total_cost keeps its budget meaning, so over-budget and the Budget Review input are unchanged and the digest goldens stay byte-identical"
  - "D-20: the RoS snapshot change was committed as one reviewed commit after the blocking review; characterization goldens changed only through --update-golden"
requirements-completed: [RULE-06]
duration: n/a (multi-session with review checkpoint)
completed: 2026-10-03
status: complete
---

# Phase 2 Plan 02: Own-spend RoS Summary

RoS now divides by the team's own security spend only (new `rules.security_spend`), so event OPEX penalties/discounts and event budget changes no longer move it, while `total_cost` and all budget semantics stay unchanged and digest-stable.

## Tasks

| Task | Name | Commit |
|------|------|--------|
| 1a | Golden diff expectations (EXPECTED["02-02"]) | 0197ac7 |
| 1b RED | Failing tests for the own-spend RoS ledger | 7cd32eb |
| 1c GREEN + 2 | Own-spend RoS in rules/enumerate/report/analyze, regenerated characterization goldens | d3b8ef4 |
| 2 docs | README, CLAUDE.md, PROJECT.md, golden diff report | eb06905 |
| 3 | Review checkpoint (user replied "approved") | d3b8ef4, eb06905 |

Commits:

- `0197ac7` chore(02-02): add RoS ledger expectations to the golden diff tool
- `7cd32eb` test(02-02): add failing tests for the own-spend RoS ledger
- `d3b8ef4` feat(02-02): compute RoS from the team's own security spend only
- `eb06905` docs(02-02): document the own-spend RoS ledger

## Runs

- Checkpoint (before commits): `uv run pytest -q` 285 passed; `uv run planspiel validate` 0 errors, 1 known warning.
- Slow suite at the checkpoint (not re-run after the commits, by instruction): `uv run pytest -m slow -q tests/test_digest.py tests/test_kernel_conformance.py` 6 passed in 660 s.
- After the commits: `uv run pytest -q` 285 passed, 11 deselected (14.73 s).
- `uv run planspiel validate`: 0 errors, 1 warning (`hand_calc.kz_slope attacks.exfil`, known).
- `git status --porcelain -- planspiel tests README.md CLAUDE.md` is empty.

## Snapshot change reviewed (3 x 782,336 combinations)

Report: `.planning/phases/02-rule-changes/02-02-GOLDEN-DIFF.md`. In every tier KZ, damage, own cost, budget total, remaining budget and in-budget count are unchanged and over-budget flips are 0; only RoS moves.

- RoS changed for 779,900 plans per tier (the rest have full damage, RoS -1 either way).
- Max |dRoS| 0.1206 (plan `0101012211`).
- Best-RoS plan `0002012210` (1.581) -> `0002022200` (1.494); top-100 RoS overlap 93 / 100.
- Digest goldens untouched; characterization goldens gained `costs.security_spend` and new RoS values.

## Deliberately updated tests

Ledger tuples (BudgetLedger fifth field), store RoS, brute-force RoS summary, WR-06 fallback (`final_index` with RoS None).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan arithmetic error in the ledger test**
- **Found during:** Task 1 (GREEN)
- **Issue:** The plan's test expectation of own spend 360 is wrong; Init 250 + OPEX 100 + window 20 = 370.
- **Fix:** `tests/test_ros_ledger.py` expects 370.
- **Files modified:** tests/test_ros_ledger.py
- **Commit:** d3b8ef4

The plan's three-step split (RED test commit, GREEN commit, goldens/docs) was folded as the plan prescribes: code, tests and goldens in `d3b8ef4`, docs and report in `eb06905`.

## Auth gates

None.

## Known Stubs

None.

## Threat Flags

None. Dumps stayed in the gitignored `golden-diff/` directory (T-02-04 pattern from 02-01); nothing from it was committed.

## Self-Check

## Self-Check: PASSED

- FOUND: tests/test_ros_ledger.py, 02-02-GOLDEN-DIFF.md
- FOUND commits: 0197ac7, 7cd32eb, d3b8ef4, eb06905
- `git status --porcelain -- planspiel tests README.md CLAUDE.md` is empty
