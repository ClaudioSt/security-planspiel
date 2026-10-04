---
phase: 02-rule-changes
plan: 04
subsystem: rules
tags: [budget-review, tier-boundaries, generated-text, rule-07, d-16, cr-01, wr-07]
requires: [02-03]
provides:
  - "review_text.boundary_text(tiers) -> str, card text generated from the config tier list"
  - "rules._tier_lookup raises ValueError below the first tier minimum (WR-07)"
  - "validator: check_tiers(..., first_minimum=None); first minimum must be 0 for final_budget_tier and checklist_tier (schema.tiers_order)"
  - "Budget Review tiers [[0, 0], [25, 5], [50, 10], [75, 15]] in real and mini config (sentinel removed)"
  - "tests/test_budget_review_text.py: boundary cases and parse-back equivalence with the simulation"
affects: [02-05, 02-06, 02-07, 02-08]
tech-stack:
  added: []
  patterns: ["printed text generated from the config list, tests parse it back and compare with the simulation"]
key-files:
  created:
    - tests/test_budget_review_text.py
  modified:
    - simulation_config.json
    - tests/fixtures/mini_config.json
    - planspiel/rules.py
    - planspiel/validate.py
    - planspiel/review_text.py
    - tests/test_characterization.py
    - tests/test_validate.py
    - tests/test_single_definition.py
    - README.md
    - .planning/PROJECT.md
key-decisions:
  - "RULE-07 / D-16: Budget Review tiers are inclusive ('ab' = >=) with round numbers; the card text is generated from the tier list, so print and simulation cannot drift (closes Phase-1 review item CR-01)"
  - "WR-07: the tier list starts at 0; the unreachable [-100000, -15] sentinel is gone and _tier_lookup fails loudly below its domain; negative remaining never reaches it because the penalty branch comes first"
requirements-completed: [RULE-07]
duration: single session
completed: 2026-10-04
status: complete
---

# Phase 2 Plan 04: Budget Review Boundaries Summary

Budget Review tiers are now inclusive with round numbers and the printed card text is generated from the config tier list (`review_text.boundary_text`); a parse-back test proves the generated text and the simulation agree at every whole k-EUR remaining 0..200 and at the euro boundaries 24.999/25.000/49.999/50.000/74.999/75.000, also for a mutated tier list. No simulation result changed.

## Tasks

| Task | Name | Commit |
|------|------|--------|
| 1 RED | Failing tests for boundaries, generated text, lookup domain, validator rule | d77cc2b |
| 1 GREEN | Tier list from 0, domain check, validator rule, `boundary_text` | 436acaf |
| 2 | README boundary rule, decision log, README test | ca7721a |

## Verification

- `uv run pytest -q`: 379 passed, 11 deselected (15.18 s), no `--update-golden`; `git diff --stat HEAD~1 -- tests/golden` after the GREEN commit prints nothing, so no golden was touched.
- RED run: 4 failed (characterization boundary mutation, single-definition registration, two validator mutations) plus a collection error for the new module (missing `boundary_text`).
- `uv run planspiel validate`: `0 Fehler, 1 Warnung(en)` (`hand_calc.kz_slope attacks.exfil`, the known one).
- `boundary_text` of the real config prints: `0 – 24.999 € → ±0, ab 25.000 € → +5, ab 50.000 € → +10, ab 75.000 € → +15`.
- `git log -3 --format="%h %s"`:
  - `ca7721a docs(02-04): document inclusive budget review boundaries`
  - `436acaf feat(02-04): generate budget review boundaries from the tier list`
  - `d77cc2b test(02-04): add failing tests for budget review boundaries and generated text`
- Slow suite not run (plan does not require it; no simulation result can change because the removed sentinel tier was unreachable and the penalty branch precedes the lookup).

CR-01 (Phase-1 review: printed "25.001-50.000" vs simulation ">= 25.000") is closed by D-16: the text now says "ab 25.000 €" and is derived from the same list the simulation reads.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Test quality] Validator mutations rewritten to pin the new rule**
- **Found during:** Task 1 RED
- **Issue:** The first draft of the two validator mutations (insert a duplicate sentinel; first OEM-Audit minimum 1) already tripped the existing "strictly ascending" check, so they would not have failed before the implementation and would not have pinned the first-minimum rule.
- **Fix:** Mutations now keep the list ascending but start below 0 (Budget Review first minimum -5, OEM-Audit first minimum -1), so only the new rule can flag them.
- **Files modified:** tests/test_validate.py
- **Commit:** d77cc2b

### Notes

- The plan's behaviour list put the validator mutations into `tests/test_validate.py` `ERROR_MUTATIONS` only; they live there and are not duplicated in the new module.
- The README test was added in Task 2 as the plan specifies (not in the RED commit), so Task 1 GREEN stays fully green.
- The plan's expected strings and boundary values contained no arithmetic errors.

## Notes for later plans

- Phase 4/5 print work can call `review_text.boundary_text(tiers)` directly; the tier values are in k-EUR with the first minimum 0.
- `_tier_lookup` now raises for values below the first minimum; any new caller must keep negative remaining out of it (as `budget_review_delta` does).

## Auth gates

None.

## Known Stubs

None.

## Threat Flags

None. T-02-15 (print/sim drift), T-02-16 (lookup below domain) and T-02-17 (regex on generated strings) are covered by `tests/test_budget_review_text.py` and `tests/test_validate.py`.

## Self-Check

- FOUND: tests/test_budget_review_text.py, planspiel/review_text.py (`def boundary_text`), simulation_config.json (`[[0, 0], [25, 5], [50, 10], [75, 15]]`)
- FOUND commits: d77cc2b, 436acaf, ca7721a
- `git diff --stat` for `tests/golden` across the plan is empty

## Self-Check: PASSED
