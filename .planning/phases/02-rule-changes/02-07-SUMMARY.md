---
phase: 02-rule-changes
plan: 07
subsystem: rules
tags: [event-overrun, sparprogramm, budget-review, validator, rule-05, d-14, d-15, d-03, d-22, d-24]
requires: [02-06, 02-03]
provides:
  - "validator warning rules.event_without_window (negative flat_budget event in the last wave)"
  - "tests/test_sparprogramm.py: 15 tests pinning event-induced overruns on evaluate_path (trim, alternative trim, no trim, partial trim, forced swap, mid-game negative) plus validator, config text and README checks"
  - "Sparprogramm description (real and mini config) stating that the remaining budget is only checked at the end and the following change window can still be used"
  - "README bullet 'Event-induzierte Überziehung' in 'Budget Review und Überziehung'; PROJECT.md decision row marked implemented"
affects: [02-08]
tech-stack:
  added: []
  patterns: ["scenario tests on the legal path evaluator instead of the static reference", "text-only golden regeneration verified by a field-level diff against HEAD"]
key-files:
  created:
    - tests/test_sparprogramm.py
  modified:
    - planspiel/validate.py
    - simulation_config.json
    - tests/fixtures/mini_config.json
    - tests/golden/characterization_low.json
    - tests/golden/characterization_medium.json
    - tests/golden/characterization_high.json
    - tests/test_validate.py
    - README.md
    - .planning/PROJECT.md
key-decisions:
  - "RULE-05 / D-14: no rules change was needed; the single end check already means an event-induced overrun is penalised only if the team is still over budget after the following change window. The static reference cannot decide RULE-05 (it has no window) and is documented as such (D-24)"
  - "Budget cuts in the last wave are flagged with the validator warning rules.event_without_window, not an error, because no change window follows"
  - "User decision (option 1): the Sparprogramm description carries the end-check sentence, and the characterization goldens are regenerated for that text-only change"
duration: ~1h (including the decision checkpoint)
completed: 2026-10-04
status: complete
requirements-completed: [RULE-05]
---

# Phase 2 Plan 07: Event-Induced Overruns (Sparprogramm) Summary

An event-induced overrun is penalised only when the team is still over budget after the next change window. The existing end-only Budget Review already does this, so the plan pins it with exact scenarios on `evaluate_path`, warns on budget cuts that no window follows, and states the rule in the event text, README and decision log. `planspiel/rules.py` was not changed.

## Tasks

| Task | Name | Commit |
|------|------|--------|
| 1 RED | Failing tests for event-induced overruns | 07e6651 |
| 1 GREEN | Validator warning, Sparprogramm text, regenerated characterization goldens | 0a7fb0d |
| 2 | README rule sentence, PROJECT.md row, `test_readme_states_event_overrun_rule` | ace4ef0 |

## Verification

- Task 1 RED (07e6651): `3 failed, 55 passed` in the targeted run (the validator warning, the description text and the warning-mutation case; all scenario values passed on the existing rules).
- All 11 scenario values from the plan matched on the first run without a `rules.py` change: exempt plan trimmed M10 (remaining +7, `opex_by_wave [45, 45, 37]`, Init 266, no penalty), alternative trim M9 (+3), untrimmed (−1, `kz_delta` −9, static reference also −9), partial trim low tier (−9, `kz_delta` −9), forced swap alone (−11, `kz_delta` −18), forced swap plus M8 trim (+1, no penalty), mid-game negative with the extra wave-3 `test_nachtragsbudget` event (found by the deterministic search, `kz_delta >= 0`).
- Task 1 GREEN: `uv run pytest -q` gave `513 passed, 13 deselected` after the golden regeneration (`uv run pytest --update-golden`).
- Task 2: RED `1 failed, 14 passed` for `test_readme_states_event_overrun_rule`, then final `uv run pytest -q` gave `514 passed, 13 deselected, 98 warnings`.
- `uv run pytest tests/test_sparprogramm.py -q`: `15 passed`.
- `uv run planspiel validate`: `WARN hand_calc.kz_slope attacks.exfil: KZ-Steigung 17/7 hat mehr als eine Nachkommastelle (verwendet in Welle 3)` then `0 Fehler, 1 Warnung(en)`.
- `git log -3 --format="%h %s"`: `ace4ef0 docs(02-07): ...`, `0a7fb0d feat(02-07): ...`, `07e6651 test(02-07): ...`.

## Deviations from Plan

### Decision checkpoint (user approved, option 1)

**1. [Rule 4 - Decision] Plan claimed "No golden changes", but the characterization goldens contain the event description**
- **Found during:** Task 1 GREEN
- **Issue:** `effect_description` of events is copied into the characterization goldens, so changing the Sparprogramm description changes them.
- **Decision:** the user chose option 1: apply the new description and regenerate the goldens.
- **Verification before commit:** a script diffed `tests/golden/*.json` against HEAD field by field. The only changed path is `cases[n].expected.waves[n].events[n].effect_description` (at `waves[1].events[0]`, the Sparprogramm), each time old text plus the appended sentence. Changed fields: low 59, medium 58, high 60. Digest goldens (low, medium, high): 0 changed fields. Unexpected differences: 0.
- **Files modified:** `tests/golden/characterization_{low,medium,high}.json`
- **Commit:** 0a7fb0d

### Auto-fixed Issues

None. The plan's scenario values were all correct on the first run.

### Notes

- Config and README edits preserved the existing line endings (README, PROJECT.md, test files and configs are CRLF; the replaced text stays inside existing lines).
- The README bullet uses the non-breaking hyphen (U+2011) in "Change‑Fenster" like the rest of the README.
- The README bullet was added after the "Begrenzung" bullet of "Budget Review und Überziehung".

## Auth gates

None.

## Known Stubs

None.

## Threat Flags

None. T-02-26 (budget cut moved to the last wave) is mitigated by `rules.event_without_window` with a test on a mutated config; T-02-27 (static reference misread) is covered by the test docstring, the static-reference scenario test and the README bullet.

## Self-Check

- FOUND: tests/test_sparprogramm.py, `rules.event_without_window` in planspiel/validate.py, `Geprüft wird das Restbudget erst am Ende` in simulation_config.json, `am Ende noch überzogen` in README.md, `RULE-05, D-14` in .planning/PROJECT.md
- FOUND commits: 07e6651, 0a7fb0d, ace4ef0
- `uv run pytest -q`: 514 passed; `uv run planspiel validate`: 0 Fehler, 1 Warnung(en)
- `git log -3` shows test, feat, docs in order

## Self-Check: PASSED
