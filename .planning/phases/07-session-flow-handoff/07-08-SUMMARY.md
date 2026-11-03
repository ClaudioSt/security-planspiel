---
phase: 07-session-flow-handoff
plan: 08
subsystem: dry-run-preparation
tags: [probelauf, protocol, print-list, texts, wording, D-28, FLOW-05]
requires: [07-02, 07-06, 07-07]
provides:
  - "planspiel/probelauf.py: PROBELAUF_JOB, ProtocolRow, ProtocolSheet, build_probelauf_sheet (same schedule_rows as the booklet)"
  - "print/templates/probelauf.tex.j2 and the PDF job spielleitung-probelauf (one A4 page, fill report)"
  - "render.probelauf_sheet in DOCUMENT_BUILDERS; print-list row spielleitung-probelauf (0 per team, 1 facilitator)"
  - "sheets.probelauf texts with gated required keys (PROBELAUF_KEYS); sheets.probelauf, sheets.eventkarten.level_or_higher and sheets.labels.event_after_wave in PHASE7_PREFIXES"
  - "D-28 wording: Exzellenz effect line 'Je Maßnahme auf Level 2 oder höher: KZ +3'; event card header 'Event in Welle N'"
affects: [07-09, 07-12]
tech-stack:
  added: []
  patterns: ["protocol sheet reuses the booklet's schedule_rows so both documents judge the same blocks", "practice-wave rule composed from texte fragments plus the schedule row label, so row and rule name the block identically"]
key-files:
  created:
    - planspiel/probelauf.py
    - print/templates/probelauf.tex.j2
    - tests/test_probelauf_model.py
    - tests/test_probelauf_pdf.py
  modified:
    - planspiel/texts.py
    - planspiel/render.py
    - planspiel/eventtext.py
    - content/texte.toml
    - simulation_config.json
    - print/planspiel.sty
    - tests/fixtures/mini_content/texte.toml
    - tests/test_texts_number_words.py
    - tests/test_event_cards.py
    - tests/test_event_text.py
    - tests/test_texts_coverage.py
key-decisions:
  - "Protocol spans are printed as 'start – end' strings built in the model from the schedule row (ProtocolRow.span), the booklet keeps start and end separate; both come from schedule_rows"
  - "Block rows use a strut of 14 mm total (rule depth 9.5 mm, height 4.5 mm) so the first line sits at the top of the cell; the test accepts any strut of at least 12 mm"
  - "event_after_wave keeps its key name; only the value changes to 'Event in Welle' (mini fixture value untouched, its header test compares against the label)"
requirements-completed: [FLOW-05]
duration: ~2.5 h
completed: 2026-11-04
status: complete
---

# Phase 7 Plan 08: Dry-run protocol and D-28 wording Summary

The facilitator PDF `spielleitung-probelauf.pdf` exists: one A4 page that lists every `session_schedule` block with its planned minutes and span (the same rows as the booklet), has empty columns for actual start, actual minutes, questions or unclear points and calculation errors, states the D-25 pass rule (the practice wave named exactly as its row, "Übungswelle (Welle 0)"), and carries a help log plus observer and date lines. The Exzellenz-Bonus card now says "Je Maßnahme auf Level 2 oder höher: KZ +3" and the event cards say "Event in Welle N".

## Tasks and commits

| Task | Commit | Result |
|------|--------|--------|
| 1 | e4da243 | `build_probelauf_sheet`, `ProtocolRow`/`ProtocolSheet`, `sheets.probelauf` texts (digit-free), gated required keys, `sheets.probelauf` in `PHASE7_PREFIXES` |
| 2 | 4863599 | `probelauf.tex.j2`, `render.probelauf_sheet`, print-list row and label, PDF tests |
| 3 | b960343 | `sheets.eventkarten.level_or_higher` (required key, `_level_bonus`), `event_after_wave` value, tests, mini fixture key, `.sty` comment |

TDD: Task 1 and 3 tests were written first and seen failing (collection error on the missing module; 8 failures for Task 3). Task 2's PDF tests failed first (6 failed, 2 errors) before the template and registration existed.

## Verification

- Wave-3 integration gate (before the first RED step): `uv run pytest -q -x` gave `2854 passed, 197 deselected, 219 warnings in 262.68s`.
- Own fast tests: probelauf model, number words, coverage, digits, schedule model, master render, print CLI/check: green; Task 3 set (`test_event_cards`, `test_event_text`, `test_master_model`, `test_wave_page`, `test_texts_coverage`, `test_texts_number_words`): 209 passed.
- PDF tests: `uv run pytest -m pdf tests/test_event_cards_pdf.py tests/test_master_pdf.py tests/test_probelauf_pdf.py tests/test_was_neu_pdf.py -q`: 38 passed (the protocol file alone: 8 passed).
- `uv run planspiel validate` and `uv run planspiel texts`: 0 Fehler, 0 Warnung(en).
- Exzellenz effect line from the config (quoted): `Je Maßnahme auf Level 2 oder höher: KZ +3`.
- Fill report of the protocol (pt used of 731.2 pt text height): 664.7 with 11 block rows of 14 mm.
- Task 3 commit changes neither `simulation_config.json` nor `planspiel/rules.py` (D-28 is text only).
- End gate (full fast suite): see the line below.

- End gate: `uv run pytest -q -x` gave `2879 passed, 205 deselected, 219 warnings in 188.20s` (2854 before plus the new model, PDF and wording tests).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Template syntax fixes found by the first builds**
- **Found during:** Task 2
- **Issue:** The first template used `\leaders` inside `\parbox` ("Leaders not followed by proper glue") and a lost row terminator produced "Misplaced \noalign".
- **Fix:** Observer and date lines use plain rules; row terminators restored.
- **Commit:** 4863599

**2. [Rule 1 - Bug] Layout: row strut and block column**
- **Found during:** Task 2 (rendered page check)
- **Issue:** A plain 12 mm strut put the text at the bottom of the cell and the practice-wave label wrapped.
- **Fix:** Strut `\rule[-9.5mm]{0pt}{4.5mm}` (14 mm total, text at the top), block column widened to 34 mm; the test asserts height plus depth is at least 12 mm instead of pinning one literal.
- **Commit:** 4863599

### Notes

- `tests/test_texts_coverage.py` got one mutation row for the new required key `sheets.eventkarten.level_or_higher` (the plan named test_event_text for the required-key test; both exist now).
- The mini fixture keeps `event_after_wave = "Event: Nach Welle"`; the only fixture edit is the required `level_or_higher` line, as planned.
- The existing line `assert source.count("\clearpage")` in `tests/test_event_cards.py` and the `\hbox` assertions in other PDF tests emit SyntaxWarnings (pre-existing, not touched).
- No generated PDF is committed; 07-09 owns the print set.

## Known Stubs

None.

## Threat Flags

None. T-07-29 (veil): rows come from `schedule_rows`, model and PDF tests run `veil.name_hits`; T-07-30: D-28 wording pinned by tests, config and rules untouched; T-07-31: the 07-02 validator and the print-list bijection test cover the new row.

## Self-Check: PASSED

Files found: planspiel/probelauf.py, print/templates/probelauf.tex.j2, tests/test_probelauf_model.py, tests/test_probelauf_pdf.py, this summary. Commits found: e4da243, 4863599, b960343.
