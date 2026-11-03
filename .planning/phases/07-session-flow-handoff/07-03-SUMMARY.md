---
phase: 07-session-flow-handoff
plan: 03
subsystem: print-data
tags: [baseline, mhp, diff, provenance, stamp, isolation]
requires: []
provides:
  - "content/mhp_baseline.json: frozen MHP values in current key names (config at 1cfb2fa, printed Budget Review boundary 'above')"
  - "planspiel/was_neu.py: BASELINE_FILE, BASELINE_GROUPS, PrintedOverride, BaselineSource, Baseline, load_baseline, ValueChange, value_changes"
  - "content/mhp_baseline.json in stamp.DATA_INPUTS and stamp.BUILD_INPUTS; content/*.json LF-normalised"
  - "tests/test_baseline_isolation.py, tests/test_was_neu_values.py"
affects: [07-06]
tech-stack:
  added: []
  patterns: ["single-reader content file (fixed file name constant, strict loader)", "machine-readable printed-vs-config override records checked against the printed Office file"]
key-files:
  created:
    - content/mhp_baseline.json
    - planspiel/was_neu.py
    - tests/test_baseline_isolation.py
    - tests/test_was_neu_values.py
  modified:
    - planspiel/stamp.py
    - .gitattributes
    - tests/test_print_stamp.py
    - tests/test_print_gitattributes.py
    - tests/test_single_definition.py
key-decisions:
  - "ValueChange uses tuple-valued fields (cia, weights, tiers, overspend as ('flat', x) or ('per_step', k, step)) so plan 07-06 formats one row per field without re-deriving structure"
  - "A bonus that exists only in the baseline is listed with new=None (removed), other unknown ids in the baseline raise PrintModelError"
  - "Exactly three changes carry meaning_changed: exzellenz_bonus.level, budget_review.boundary (above -> inclusive), budget_review.overspend (flat -> per_step)"
  - "tests/test_single_definition.py gets a one-file allowlist (OPERAND_READERS) for was_neu.py because the diff reads raw operand attributes to compare and list them, never to compute"
requirements-completed: [FLOW-04]
duration: ~45 min
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 03: MHP baseline and value diff Summary

The data side of the "Was ist neu" sheet exists: the MHP state is frozen in `content/mhp_baseline.json`, proven against git commit 1cfb2fa and against slide 9 of the printed `Events_Security-Game.pptx`, and `value_changes(cfg, baseline)` lists exactly the parameters whose old and new values differ. No prose and no rendering yet; plan 07-06 builds the PDF on top of this.

## Tasks and commits

| Task | Commit | Result |
|------|--------|--------|
| 1 | d1e5a80 | Baseline file (numbers and ids only outside `source`), strict `load_baseline`, `PrintedOverride` records, provenance tests (config at 1cfb2fa mapped through the schema table; printed strings found after the location text in the Office part) |
| 2 | 0348bf0 | `ValueChange` and `value_changes` with one extractor per group; unchanged values drop out; mutation, unknown-id and missing-id tests |
| 3 | 01f1599 | Isolation tests (file name only in was_neu.py and stamp.py, importers only render.py and cli.py, no Config field, load_config never reads the file); stamp data and build input; `content/*.json text eol=lf` |
| fix | 5de235d | Single-definition guard: `OPERAND_READERS` allowlist for `planspiel/was_neu.py` |

TDD: the loader and diff tests were written first (collection error on the missing module) and driven to green.

## What the baseline holds

`schema` 1; `source` (config commit 1cfb2fa, print commit 72f54b2, one printed override); `base_cia`; budget tiers with kz_start and severity multiplier; per wave weights, threshold and bonus measures; three attacks; ten measures at levels 1-3 (cia, init, opex, recovery); the six numeric events; `budget_review` with boundary `above`, tiers and the flat -15 overspend. The one override record is `budget_review.boundary = above`, file `Events_Security-Game.pptx`, part `ppt/slides/slide9.xml`, location `Budget Review`, printed `25.001`, `50.001`, `75.001`. The printed-file test finds the file in `final_documents/` or `archive/mhp_print_material_2026-07/` (it is in the archive now).

## Value changes found (real config)

Budget 350/400/450 -> 370/390/405, KZ start 50/42/34 -> 39/36/33, thresholds wave 1 and 3, bonuses M4/M6 (wave 1), M7 (wave 2), M1/M8 (wave 3), KZ endpoints of all three attacks, M6 init, M7 CIA, OEM audit tiers, critical vulnerability tiers, annoying authentication, Exzellenz level and amount, Budget Review tiers, boundary and overspend rule. Wave weights, s_unit, caps, severities, recovery and the other measures are unchanged and do not appear.

## Deviations from Plan

**1. [Rule 3 - Blocking] Single-definition guard rejected the diff module**
- **Found during:** full fast suite after Task 3
- **Issue:** `tests/test_single_definition.py::test_no_formula_operands_outside_rules_and_config` forbids `.e_threshold`, `.recovery`, `.init`, `.opex`, `.bonus` outside rules and config; `was_neu.py` reads them to compare old and new values.
- **Fix:** named allowlist `OPERAND_READERS = {"planspiel/was_neu.py"}` with a justification comment; the module does no arithmetic on operands.
- **Files modified:** tests/test_single_definition.py
- **Commit:** 5de235d

**2. [Interpretation] `min_level` is listed together with `bonus` for a removed bonus**
A bonus present only in the baseline yields two changes (bonus and min_level, new None). The plan did not specify this case; the test pins it.

## Verification

- Own files: `uv run pytest tests/test_baseline_isolation.py tests/test_was_neu_values.py tests/test_print_stamp.py tests/test_print_gitattributes.py -q` gave 109 passed, no skips (both provenance tests run in this clone).
- Full fast suite `uv run pytest -q`: 2769 passed, 1 failed (the single-definition guard, fixed in 5de235d and re-run: 72 passed in that file). No other failures.
- `uv run planspiel validate`: 0 Fehler, 0 Warnung(en). `git check-attr` reports `text: set`, `eol: lf` for the baseline.

## Known Stubs

None. The baseline holds only values; texts and rendering belong to plan 07-06.

## Threat Flags

None. Mitigations T-07-10 to T-07-14 are covered by the isolation tests, the two provenance tests, the strict loader tests, the stamp input tests and the no-`archive/` assertion on the baseline.

## Self-Check: PASSED

Created files exist (`content/mhp_baseline.json`, `planspiel/was_neu.py`, `tests/test_baseline_isolation.py`, `tests/test_was_neu_values.py`); commits d1e5a80, 0348bf0, 01f1599, 5de235d exist.
