---
phase: 02-rule-changes
plan: 03
subsystem: rules
tags: [budget-review, overspend-penalty, golden-snapshot, rule-03, d-15, d-14, d-25]
requires: [02-02]
provides:
  - "rules.budget_review_delta(remaining, tiers, kz_per_step, step) -> int; rules.penalty_params(final_events) -> (kz_per_step, step)"
  - "config key final_events[budget_review].overspend_penalty = {kz_per_step: 9, step: 10}"
  - "CompactOutcome / CompactRecord fields kz_pre_review and remaining; store layout 19 bytes; dump_record keys kz_pre_review and remaining"
  - "planspiel/review_text.py: format_eur, penalty_rows (print-ready penalty lookup rows)"
  - "validator: overspend_penalty required, hand_calc.penalty_step warning"
  - "tests/test_budget_review.py; golden_diff.py EXPECTED['02-03'] and 02-03-GOLDEN-DIFF.md"
affects: [02-04, 02-05, 02-06, 02-07, 02-08]
tech-stack:
  added: []
  patterns: ["penalty parameters read from config via penalty_params, tests derive expected values from them", "ledger and config step both in kEUR, step passed explicitly to started_steps"]
key-files:
  created:
    - planspiel/review_text.py
    - tests/test_budget_review.py
    - .planning/phases/02-rule-changes/02-03-GOLDEN-DIFF.md
  modified:
    - simulation_config.json
    - tests/fixtures/mini_config.json
    - planspiel/rules.py
    - planspiel/validate.py
    - planspiel/enumerate.py
    - planspiel/report.py
    - tests/support/harness.py
    - tests/test_kernel_conformance.py
    - tests/test_rules_semantics.py
    - tests/test_characterization.py
    - tests/test_enumeration.py
    - tests/test_validate.py
    - tests/test_single_definition.py
    - tests/test_ros_ledger.py
    - tests/golden/characterization_low.json
    - tests/golden/characterization_medium.json
    - tests/golden/characterization_high.json
    - tests/golden/digest_low.json
    - tests/golden/digest_medium.json
    - tests/golden/digest_high.json
    - README.md
    - CLAUDE.md
    - .planning/PROJECT.md
    - .planning/phases/02-rule-changes/tools/golden_diff.py
key-decisions:
  - "RULE-03 / D-15 / D-14 / D-25: a plan that ends over budget loses X KZ per started 10.000 EUR of overspend, measured once on the final remaining budget, then clamped to 0..100; provisional X = 9, step 10 kEUR"
  - "No hand_calc warning for large X: the X > ~5 question stays a STATE.md Phase-6 input owned by the gate plan 02-08, so the 'one known warning' invariant holds"
  - "D-20: the over-budget KZ snapshot change was committed as one reviewed commit after the blocking review (user: approved)"
requirements-completed: [RULE-03]
duration: n/a (multi-session with review checkpoint)
completed: 2026-10-04
status: complete
---

# Phase 2 Plan 03: Linear Overspend Penalty Summary

An over-budget plan now loses X = 9 KZ per started 10.000 EUR of overspend (config `overspend_penalty`, `rules.budget_review_delta`) instead of the flat -15, measured once at the end; in-budget results are untouched, and the kernel, store and dump now carry `kz_pre_review` and `remaining` for the RULE-04 gate.

## Tasks

| Task | Name | Commit |
|------|------|--------|
| 1a | Golden diff expectations (EXPECTED["02-03"]) | 72137d8 |
| 1b RED | Failing tests for the linear overspend penalty | f7bf43b |
| 1c GREEN + 2 | Penalty, store columns, lookup rows, regenerated goldens | ba31f42 |
| 2 docs | README, CLAUDE.md, PROJECT.md, golden diff report, golden_diff tool | bfc2b80 |
| 3 | Review checkpoint (user replied "approved") | ba31f42, bfc2b80 |

Commits:

- `72137d8` chore(02-03): add overspend penalty expectations to the golden diff tool
- `f7bf43b` test(02-03): add failing tests for the linear overspend penalty
- `ba31f42` feat(02-03): replace the flat budget-review penalty with a linear overspend penalty
- `bfc2b80` docs(02-03): document the linear overspend penalty

## Runs

- RED run (before the implementation): `12 failed, 257 passed, 11 deselected, 3 errors`.
- Checkpoint (before the commits): fast suite passed; slow suite `uv run pytest -m slow -q` 11 passed in 1126.57 s on content identical to what was committed (not re-run after the commits, by instruction).
- After the commits: `uv run pytest -q` 357 passed, 11 deselected (15.43 s).
- `uv run planspiel validate`: 0 Fehler, 1 Warnung(en) (`hand_calc.kz_slope attacks.exfil`, known).
- `uv run python -c "from planspiel.review_text import penalty_rows; print(penalty_rows(9, 10)[:3])"` prints `[(1, 10000, -9), (10001, 20000, -18), (20001, 30000, -27)]`.
- `git status --porcelain -- planspiel tests simulation_config.json README.md CLAUDE.md` is empty.

## Snapshot change reviewed (3 x 782,336 combinations)

Report: `.planning/phases/02-rule-changes/02-03-GOLDEN-DIFF.md`. Only over-budget plans change KZ; in-budget plans, over-budget flags and RoS are unchanged.

| Quantity | low | medium | high |
|----------|-----|--------|------|
| KZ changed (all over-budget plans) | 712,882 | 658,015 | 584,583 |
| In-budget plans, KZ and count unchanged | 69,454 | 124,321 | 197,753 |
| Over-budget flips | 0 | 0 | 0 |
| RoS changed | 0 | 0 | 0 |
| Best in-budget KZ (unchanged) | 98 | 100 | 100 |
| Best over-budget KZ, old -> new | 85 -> 91 | 85 -> 91 | 85 -> 89 |
| KZ = 0 among over-budget after | 606,209 | 525,877 | 442,578 |

Digest goldens keep `count` 782336 and their `in_budget` values; only histogram and hash changed.

Approval: the user replied "approved" at the Task 3 checkpoint before any commit (T-02-10).

## Deliberately updated tests (old -> new)

- Negative-remaining final event (`apply_final_events(..., -1, 50)`): 35 -> 41 (`50 - X`).
- All-L3 in low: final event -15 -> -801 (`-X * 89`), `kz_final` 0.
- Store record size: 16 -> 19 bytes, with `kz_pre_review` and `remaining` fields; `dump_record` key list extended.
- Characterization category check: the over-budget case must have `kz_delta == -X * started_steps(-remaining, step)`, with `(X, step)` read from `rules.penalty_params`, so a Phase-6 change of X only changes goldens.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] tests/test_ros_ledger.py needed the new outcome fields**
- **Found during:** Task 1 (RED)
- **Issue:** The shared outcome helper in this module builds `CompactOutcome` positionally and broke (3 errors) once the new `kz_pre_review` and `remaining` fields existed; it is not in the plan's file list.
- **Fix:** Adapted the helper in the RED commit.
- **Files modified:** tests/test_ros_ledger.py
- **Commit:** f7bf43b

### Additions beyond the plan text

**2. [Rule 2 - Missing critical] golden_diff overspend-distribution section**
- The golden diff report gained an overspend-distribution section (best over-budget KZ before/after, KZ = 0 saturation counts) so checkpoint items 2 and 3 are readable directly from the report.
- **Files modified:** .planning/phases/02-rule-changes/tools/golden_diff.py
- **Commit:** bfc2b80

**3. Validator tests live in `tests/test_budget_review.py`**
- The behaviour list allowed either location; they were put in the new module, so `tests/test_validate.py` is unchanged and still pins the single known warning.

**4. CRLF line endings preserved**
- Config, README and the touched sources keep CRLF; git prints the usual LF/CRLF notices, no content changes from it.

**Attribution trailer:** commits of this continuation carry `Co-Authored-By: Claude Sonnet 5.5` (the harness attribution for this session) instead of the `Claude Opus 5.5` line used in earlier commits of the phase; the `Claude-Session` line is identical.

## Notes for later plans and phases

- Boundary text in Phase 4/5 must say "ab 25.000 EUR" (tier minimum 25 kEUR) and the penalty rows come from `review_text.penalty_rows`; the footer "jede weitere angefangene Schrittweite -X, KZ nie unter 0" is template work.
- X-observations for the RULE-04 gate (02-08):
  - X = 9 sits well above the global minimum: the smallest X that still makes going over budget non-optimal is 2 / 0 / 0 per tier (3 / 1 / 1 if ties must lose).
  - Saturation at KZ 0 starts from 5 steps (50.000 EUR) over budget at X = 9, which is why 443k-606k over-budget plans bottom out at 0.
  - `kz_pre_review` and `remaining` are stored per plan, so the gate can sweep X without re-enumerating.
- The global data does not indicate that X > 5 is needed; the final answer stays pending the 02-08 trim-back gate (STATE.md concern updated).

## Auth gates

None.

## Known Stubs

None.

## Threat Flags

None. Dumps stayed in the gitignored `golden-diff/` directory; nothing from it was committed (T-02-10 mitigated by the blocking review; T-02-11 to T-02-14 covered by the tests in `tests/test_budget_review.py` and `tests/test_enumeration.py`).

## Self-Check

## Self-Check: PASSED

- FOUND: planspiel/review_text.py, tests/test_budget_review.py, 02-03-GOLDEN-DIFF.md
- FOUND commits: 72137d8, f7bf43b, ba31f42, bfc2b80
- `git status --porcelain -- planspiel tests simulation_config.json README.md CLAUDE.md` is empty
