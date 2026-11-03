---
phase: 07-session-flow-handoff
plan: 06
subsystem: facilitator-sheet
tags: [was-ist-neu, baseline, print-pipeline, texts, fill-proof]
requires: [07-02, 07-03, 07-04]
provides:
  - "planspiel/was_neu.py: WAS_NEU_JOB, RULE_IDS, FLOW_IDS, MATERIAL_IDS, VALUE_GROUP_ORDER, MAX_VALUE_ROWS, RuleRow, ValueRow, WasNeuSheet, build_was_neu_sheet"
  - "print/templates/was_neu.tex.j2 and the PDF job spielleitung-was-ist-neu (one A4 page, fill report)"
  - "render.was_neu_sheet and render_all(..., baseline=); _print_command loads content/mhp_baseline.json by its fixed name"
  - "sheets.was_neu texts (rules, flow, material, parts, fields) with gated required keys; print-list row spielleitung-was-ist-neu"
affects: [07-08, 07-09]
tech-stack:
  added: []
  patterns: ["dedicated render path for the one builder that may see the MHP baseline", "value rows grouped from raw ValueChange, formatted in the sheet module", "priority cap with a worst-case page proof"]
key-files:
  created:
    - print/templates/was_neu.tex.j2
    - tests/test_was_neu_model.py
    - tests/test_was_neu_pdf.py
  modified:
    - planspiel/was_neu.py
    - planspiel/texts.py
    - planspiel/render.py
    - planspiel/cli.py
    - content/texte.toml
    - simulation_config.json
    - tests/test_texts_number_words.py
    - tests/test_master_render.py
    - tests/test_schedule_model.py
    - tests/test_print_cli.py
key-decisions:
  - "Value rows are grouped per printed row (tier budgets, KZ start, one threshold per wave, bonuses of one wave, KZ at full damage and full defence of one wave, one measure field across levels, one event, Budget Review tiers, boundary and overspend); unchanged members of a group are read from the config so the row shows all members"
  - "MAX_VALUE_ROWS is 19: the real baseline yields 19 rows (all shown, no pointer line); the capped worst case (19 rows of the longest real strings plus the flag note and the pointer line) fills 720.9 of 731.2 pt"
  - "render.was_neu_sheet returns {} for baseline None before touching cfg, so render_all(None, None, ...) and the existing clue-spy test stay valid"
  - "The retired term Maßnahmenwechsel is not printed (test_kurswechsel guards all display strings); the levelwechsel row says the new term replaces the old MHP term"
requirements-completed: [FLOW-04]
duration: ~3 h
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 06: Was-ist-neu sheet Summary

The facilitator PDF `spielleitung-was-ist-neu.pdf` exists: one A4 page with the twelve rule changes (RULE-01..08 plus the four D-29 items), four flow changes, six new-material points and the grouped old -> new value table, all numbers generated from the config or the frozen MHP baseline, and the baseline reaches that one builder only.

## Tasks and commits

| Task | Commit | Result |
|------|--------|--------|
| 1 | 256712a | `build_was_neu_sheet`, `RuleRow`/`ValueRow`/`WasNeuSheet`, grouped and capped value rows, `sheets.was_neu` texts and gated required keys, `sheets.was_neu` in `PHASE7_PREFIXES` |
| 2 | 5780662 | `render.was_neu_sheet` + `render_all(baseline=)`, CLI baseline loading, print-list row and label, first template version, routing/spy/CLI tests |
| 3 | 7db3e75 | Compact one-page template, `MAX_VALUE_ROWS` calibration, PDF tests incl. worst case |
| fix | 57e21f2 | Retired term kept out of the prose (guard in test_kurswechsel) |

TDD: model tests were written first (collection error on the missing names), routing and CLI tests failed before the render change, the PDF tests drove the layout.

## What the sheet holds

- Rule rows in `RULE_IDS` order: levelwechsel, kurswechsel, downgrade, init_window, overspend, sparprogramm, ros, review_boundary, e_target, rounding, final_index, event_order. Generated numbers: overspend `−3 KZ je angefangene 10.000 €` (from `rules.penalty_params`), the Budget Review tier text (`review_text.boundary_text`), the Final-Index formula `1 × KZ + 10 × RoS` (weights from `cfg.final_index`).
- Flow rows: no whiteboard, Welle 0, debrief (title and 20 minutes from the debrief block), schedule (title, 190 minutes, wave-block minutes from config).
- Material rows: generated PDFs, veiled attacks, clue matrix (title from `sheets.spielleitung`), team booklet, wave explainer (title from `sheets.welle`), practice sheet.
- Value rows (19): tier budgets, KZ start, thresholds of wave 1 and 3, bonuses of waves 1-3, KZ endpoints of waves 1-3, M6 Init, M7 CIA, four event rows, three Budget Review rows. Three rows carry the `*` mark (Exzellenz-Bonus level, boundary, overspend) with the flag note. Attack-related rows are labelled "Welle N".

## Verification

- Own fast tests: `uv run pytest tests/test_was_neu_model.py tests/test_was_neu_values.py tests/test_baseline_isolation.py tests/test_texts_number_words.py tests/test_master_render.py tests/test_schedule_model.py tests/test_print_cli.py tests/test_print_check.py tests/test_texts_coverage.py tests/test_texts_digits.py -q`: 223 passed.
- PDF tests: `uv run pytest -m pdf tests/test_was_neu_pdf.py tests/test_master_pdf.py -q`: 24 passed (Task 3 state); after the final text fix `uv run pytest -m pdf tests/test_was_neu_pdf.py -q`: 8 passed.
- Full fast suite `uv run pytest -q`: 2832 passed, 197 deselected (the first full run after Task 3 found one failure, test_kurswechsel retired-term guard, fixed in 57e21f2; the re-run is green).
- `uv run planspiel validate` and `uv run planspiel texts`: 0 Fehler, 0 Warnung(en).
- Fill report (pt used of 731.2 pt text height): real sheet 710.6; capped worst case (19 rows of the longest real strings, flag note and pointer line) 720.9; 20 worst-case rows overflowed (732.5), hence the cap of 19.
- `final_documents/generated`, `content/digit_allowlist.toml` and `tests/fixtures` unchanged; no PDF committed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] First template version moved into Task 2**
- **Found during:** Task 2 (routing tests render the sheet through `render_all`)
- **Issue:** The routing tests need `was_neu.tex.j2`, which the plan assigned to Task 3.
- **Fix:** A first template version was committed with Task 2; Task 3 reworked layout and calibrated the cap.
- **Commit:** 5780662, 7db3e75

**2. [Rule 1 - Bug] Template spacing macros and the retired term**
- **Found during:** Task 3 and the full-suite run
- **Issue:** `{\small\VAR{..}}` swallowed the first word (undefined control sequence); the levelwechsel row printed the retired term, which `test_kurswechsel` forbids in every display string.
- **Fix:** `{\small{} ...}` pattern; the row names the replaced term only as "alten Begriff der MHP-Runde".
- **Commit:** 7db3e75, 57e21f2

**3. [Interpretation] `render.was_neu_sheet` returns early without a baseline**
The existing `render_all(None, None, ...)` spy test would otherwise crash on `cfg.session_schedule`; the early return keeps that test unchanged.

**4. [Interpretation] Event labels carry the config event name**
Event rows are labelled with `event.name` (OEM-Audit, Exzellenz-Bonus, ...), measure rows with id and config name; both pass the `veil.name_hits` test, so no id-only fallback was needed.

## Known Stubs

None.

## Threat Flags

None. T-07-21 (veil) is covered by the model-level and layer-two PDF `name_hits` tests plus the "Welle N" labels, T-07-22 by the spy test, the unchanged 4-argument builder signature test and the 07-03 isolation tests, T-07-23 by `tex_escape` on every string, T-07-24 by the mutation tests (X, step, tiers, k, wave minutes), T-07-25 by the cap and the worst-case page proof.

## Self-Check: PASSED

Created files exist (`print/templates/was_neu.tex.j2`, `tests/test_was_neu_model.py`, `tests/test_was_neu_pdf.py`, this summary); commits 256712a, 5780662, 7db3e75, 57e21f2 exist.
