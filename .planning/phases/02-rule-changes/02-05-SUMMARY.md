---
phase: 02-rule-changes
plan: 05
subsystem: rules
tags: [kurswechsel, massnahmentausch, levelwechsel, reference-plan, golden-text-only, rule-01, d-09, d-10, d-11, d-13, d-22, d-23, d-24, d-28]
requires: [02-04]
provides:
  - "rules.swap_possible(selection) -> bool, swap_legal(wave1, window_end, dropped, incoming) -> bool, swap_credit(measures, wave1, dropped, incoming, window_end) -> int, swap_repair(selection, dropped, measures) -> Dict[str, int], kurswechsel_wave(events) -> Optional[int]"
  - "event type `kurswechsel` (replaces `noop`) in rules.evaluate_event, validator registries and both configs; `noop` is now an unknown type"
  - "validator: schema.kurswechsel_count and a placement rule (no Kurswechsel in the last wave) under schema.event_placement"
  - "report.REFERENCE_LAYER = 'referenz', report.REFERENCE_LABEL = 'Referenzplan ohne Change-Fenster-Züge'; summary keys layer, layer_label"
  - "README vocabulary: Levelwechsel vs. Maßnahmentausch, section 'Kurswechsel (Maßnahmentausch)'"
affects: [02-06, 02-07, 02-08]
tech-stack:
  added: []
  patterns: ["swap rules defined once in rules.py for the later path model", "static results carry an explicit reference-plan label"]
key-files:
  created:
    - tests/test_kurswechsel.py
    - .planning/phases/02-rule-changes/02-05-GOLDEN-DIFF.md
  modified:
    - simulation_config.json
    - tests/fixtures/mini_config.json
    - planspiel/rules.py
    - planspiel/validate.py
    - planspiel/report.py
    - planspiel/balance.py
    - planspiel/analyze.py
    - tests/test_enumeration.py
    - tests/test_wrappers.py
    - tests/test_single_definition.py
    - tests/golden/characterization_low.json
    - tests/golden/characterization_medium.json
    - tests/golden/characterization_high.json
    - .planning/phases/02-rule-changes/tools/golden_diff.py
    - README.md
    - CLAUDE.md
    - .planning/PROJECT.md
key-decisions:
  - "RULE-01 / D-09..D-11, D-13: the Kurswechsel is exactly one forced Maßnahmentausch in the change window after the Kurswechsel wave; the customer carries the incoming Init up to the dropped measure's Init at its Kurswechsel-wave level, the team pays max(0, Init new - Init dropped), never a refund"
  - "D-22/D-23/D-28: a swap needs one measure active and one inactive in the Kurswechsel wave; no legal swap means exemption; dependents of the dropped measure are lowered by a canonical minimal repair"
  - "D-24/D-26: static enumeration is the reference plan without change-window moves; every static report carries layer/layer_label so it is not read as a reachable legal result"
requirements-completed: [RULE-01]
duration: multi-session (checkpoint at Task 3)
completed: 2026-10-04
status: complete
---

# Phase 2 Plan 05: Kurswechsel as a Forced Maßnahmentausch Summary

The Kurswechsel is now the event type `kurswechsel`: exactly one forced Maßnahmentausch in the change window after its wave, with swap legality, credit, exemption and minimal repair defined once in `planspiel/rules.py` and covered by unit tests. README and config now separate "Levelwechsel" (same measure, other level) from "Maßnahmentausch" (one out, one in, only via the Kurswechsel). Static reports are labelled "Referenzplan ohne Change-Fenster-Züge". No number changed: only the Kurswechsel record's `effect_description` text moved in the characterization goldens.

## Tasks

| Task | Name | Commit |
|------|------|--------|
| 0 | Kurswechsel expectations in the golden diff tool | 7df5d97 |
| 1 RED | Failing tests for the Kurswechsel swap rules | 90bdff3 |
| 2 GREEN | Config, rules, validator, report labels, goldens (text-only) | 4209d22 |
| 3 | README, CLAUDE.md, PROJECT.md, golden diff report (after review) | fe7a28e |

Task 3 was the blocking human-verify checkpoint. The reviewer replied "approved", including the reworded description "fällt ganz weg" instead of "(Level 0)".

## Verification

- RED run (90bdff3): 43 failed, 378 passed, 14 deselected.
- `uv run pytest -q` after the commits: `428 passed, 11 deselected, 88 warnings in 20.07s`.
- Slow suite (run at the checkpoint, not re-run): `uv run pytest -m slow -q tests/test_digest.py tests/test_kernel_conformance.py` gave 6 passed in 588.8 s.
- `uv run planspiel validate`: `0 Fehler, 1 Warnung(en)` (`hand_calc.kz_slope attacks.exfil`, the known one).
- Golden diff (`02-05-GOLDEN-DIFF.md`): across 3 tiers x 782,336 combinations every numeric metric (KZ, RoS, damage, own cost, budget, remaining budget, per-wave KZ, over-budget flips, best plans, top-100 RoS overlap) changed in 0 cases.
- Golden update summary: only `waves[0].events[0].effect_description` changed, in 59 (low), 58 (medium) and 60 (high) cases; cross-checked leaf by leaf.
- D-22: 48,115 selections have a legal swap available (swap_possible).
- `git log -3 --format="%h %s"` before this summary:
  - `fe7a28e docs(02-05): define Levelwechsel, Massnahmentausch and the Kurswechsel`
  - `4209d22 feat(02-05): make the Kurswechsel a forced Massnahmentausch with tested swap rules`
  - `90bdff3 test(02-05): add failing tests for the Kurswechsel swap rules`
- Working tree clean after the two commits.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Wording] Config description reworded after review**
- **Found during:** Task 3 review
- **Issue:** The first description said the dropped measure goes to "(Level 0)", which reads like a Levelwechsel; the reviewer asked for unambiguous wording.
- **Fix:** Description now says the measure "fällt ganz weg"; README uses the same words.
- **Files modified:** simulation_config.json, README.md
- **Commit:** 4209d22

**2. [Rule 3 - Blocking] `_requirements_met` split out of `dependencies_satisfied`**
- **Found during:** Task 2 GREEN
- **Issue:** `swap_repair` must test the dependencies of a single measure at a single level; the existing function only checked a whole selection, so the check would have been duplicated.
- **Fix:** Extracted `_requirements_met(measure, level, selection)`; `dependencies_satisfied` now delegates to it with identical behaviour (all numeric diffs 0).
- **Files modified:** planspiel/rules.py
- **Commit:** 4209d22

### Notes

- The RED commit also touched `tests/test_single_definition.py` (registering the swap rules as single definitions), and the golden tool expectations (`EXPECTED["02-05"]`) were added up front in 7df5d97, so the golden diff report is checked against stated expectations.
- `tests/test_validate.py` was listed in the plan but was not modified in the commits; the new validator rules (`schema.kurswechsel_count`, last-wave placement, `noop` unknown) are exercised in `tests/test_kurswechsel.py` (parametrized error mutations) instead.
- Stale README change-window bullets (the old description of the Kurswechsel-adjacent change-window moves) are intentionally left for plan 02-06, which rewrites the change window as the path model.
- The golden diff dumps under `.planning/phases/02-rule-changes/golden-diff/` are not committed.
- A Kurswechsel in `final_events` was already rejected by the existing placement rule (`schema.event_placement`); only the last-wave and count rules are new, so that validator case already passed at RED.
- The PROJECT.md Key Decisions row is dated 2026-10-04 (the implementation date) instead of the plan's 2026-10-01.
- Line endings preserved: touched CRLF files kept CRLF, goldens stay LF per `.gitattributes`, the new `tests/test_kurswechsel.py` is CRLF like the other tests.
- `.planning/PROJECT.md` still uses the retired term "Maßnahmenwechsel" in the historical open-requirement and context lines (lines 38 and 76); left as history.

## Notes for later plans

- 02-06 builds the path model on `swap_possible`, `swap_legal`, `swap_credit`, `swap_repair`, `kurswechsel_wave`; the swap credit is read at the Kurswechsel-wave level and capped at the incoming Init.
- The enumeration remains the reference plan; only plans where no swap is possible are legal games without a change-window move.

## Auth gates

None.

## Known Stubs

None.

## Threat Flags

None. T-02-18 (golden text change reviewed via `--update-golden` after the blocking review, numeric diff 0), T-02-19 (validator errors for misplaced or duplicated Kurswechsel and unknown `noop`), T-02-20 (layer/layer_label in summary JSON and console) and T-02-21 (credit capped at incoming Init, read at the Kurswechsel-wave level) are covered by tests.

## Self-Check

- FOUND: tests/test_kurswechsel.py, planspiel/rules.py (`def swap_credit`, `def kurswechsel_wave`), .planning/phases/02-rule-changes/02-05-GOLDEN-DIFF.md
- FOUND commits: 7df5d97, 90bdff3, 4209d22, fe7a28e
- `uv run pytest -q`: 428 passed; `uv run planspiel validate`: 0 Fehler

## Self-Check: PASSED
