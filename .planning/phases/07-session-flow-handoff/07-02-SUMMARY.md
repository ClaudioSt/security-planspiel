---
phase: 07-session-flow-handoff
plan: 02
subsystem: facilitator-booklet
tags: [schedule, config, print-list, booklet, texts, lint]
requires: []
provides:
  - "simulation_config.json session_schedule block (11 blocks, 190 min, teams 3, persons_per_team 5, print list quantities)"
  - "planspiel/schedule.py (schedule_rows, print_list_rows, build_schedule_page), shared with the dry-run protocol"
  - "sheets.ablauf texts in content/texte.toml"
  - "schedule page and print-list page in spielleitung-uebersicht"
  - "tests/test_texts_number_words.py (PHASE7_PREFIXES, ALLOWED, NUMBER_WORDS)"
affects: [07-04, 07-05, 07-06, 07-07, 07-08, 07-09]
tech-stack:
  added: []
  patterns: ["optional config block read by one print module (invisible to rules)", "keys generated from config ids only when the block exists"]
key-files:
  created:
    - planspiel/schedule.py
    - tests/test_session_schedule_config.py
    - tests/test_schedule_model.py
    - tests/test_texts_number_words.py
  modified:
    - simulation_config.json
    - planspiel/config.py
    - planspiel/validate.py
    - planspiel/texts.py
    - planspiel/master.py
    - content/texte.toml
    - print/templates/master.tex.j2
    - tests/test_master_pdf.py
key-decisions:
  - "Product rules (190 min, D-02 order, 20-minute waves, 3 teams of 5) live in the test, not the validator; the validator only guards structure and the sum rule"
  - "The print list sits on its own page right after the schedule page (the combined page overflowed by about 16 pt), D-23 accepts both"
  - "MasterSheet.printed_fragments takes the schedule fragments from SchedulePage.printed_fragments so block ids (keys) are not counted as printed text"
requirements-completed: [FLOW-02]
duration: ~50 min
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 02: Session schedule and print list Summary

The facilitator booklet now opens with a run sheet: 11 config-held blocks (190 minutes, wave 1 in 20 minutes, a 20-minute debrief, no whiteboard step), cumulative minutes, an empty clock column and one direction line per block, followed by a print list with quantities from config.

## Tasks and commits

| Task | Commit | Result |
|------|--------|--------|
| 1 | d204400 | `session_schedule` block, `ScheduleBlock`/`PrintRow`/`SessionSchedule`, `check_session_schedule` (codes `schedule.sum`, `schedule.id`, `schedule.wave_block`, `schedule.print_job`, `schedule.print_veil`); `_comment_events` retargeted to `mhp_print_material_2026-07/Events_Security-Game.pptx` (LEG-01 follow-through, no `archive/` token) |
| 2 | b0f5afc | `planspiel/schedule.py`, `sheets.ablauf` texts (19 keys, 11 block tables, 10 print labels), gated `required_keys` branch, phase-7 number-word lint |
| 3 | fb358f0 | `MasterSheet.schedule`, schedule page and print-list page in `master.tex.j2`, two new PDF tests |
| fix | 9238086 | `session_schedule` field order, `job` in the lint ID keys (see deviation 3) |

TDD: RED tests were written first in each task (import errors / missing attribute), GREEN verified before each commit.

## Verification

- Task 3 gate: `uv run pytest -m pdf tests/test_master_pdf.py -q` gave 14 passed; own fast tests (config, schedule model, number words, practice config, validate, texts coverage and digits, master model and render) gave 238 passed.
- `uv run planspiel validate` and `uv run planspiel texts`: 0 Fehler, 0 Warnung(en).
- Full fast suite `uv run pytest -q`: 2717 passed, 187 deselected in 215 s (second run, after the field-order fix; the first run had 4 failures, see deviation 3).
- Fill report (pt used of 731.2 pt text height): page 1 (overview) 498.8, schedule page 437.8, print-list page 309.1.
- `content/digit_allowlist.toml` and `tests/fixtures/` unchanged; no file under `final_documents/generated` touched.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Layout] Schedule and print list on two pages**
- **Found during:** Task 3 (fill report)
- **Issue:** On one page the content overflowed (758.5 pt used of 731.2 pt), which broke the one-fill-report-per-page test; the first column also had an overfull box for "Story-Gruppenarbeit".
- **Fix:** Print list moved to its own page with its own `\pagereport` (explicitly allowed by the plan and D-23 test), label column widened from 27 to 32 mm.
- **Files modified:** print/templates/master.tex.j2
- **Commit:** fb358f0

**2. [Rule 1 - Bug] Block ids counted as printed text**
- **Found during:** Task 3 design
- **Issue:** `cards.printed_strings` walks nested dataclasses and would list `ScheduleRow.block_id` (a key) as a fragment that must appear in the PDF.
- **Fix:** `SchedulePage.printed_fragments` builds the list explicitly, and `MasterSheet.printed_fragments` delegates the `schedule` field to it.
- **Files modified:** planspiel/schedule.py, planspiel/master.py
- **Commit:** b0f5afc, fb358f0

**3. [Rule 1 - Bug] Field order and transliteration lint broke four existing tests**
- **Found during:** full fast suite after Task 3
- **Issue:** The plan placed `Config.session_schedule` after `practice`, but three tests pin `practice` as the last field (`test_reference_plans`, `test_reference_strategies`, `test_final_index_config`); the transliteration lint in `test_config_text.py` flagged the ASCII print-list job names (`spieler-massnahmenkarten`, `spielleitung-uebersicht`).
- **Fix:** `session_schedule` now sits before `reference_plans` (all fields are keyword arguments); `job` joined `ID_KEYS` of the lint, as the job names are file ids, not display strings.
- **Files modified:** planspiel/config.py, tests/test_config_text.py
- **Commit:** 9238086

### Notes

- `planspiel/config.py` and `planspiel/validate.py` use CRLF line endings in the working tree; edits were made accordingly so the diff stays minimal.

## Known Stubs

None.

## Threat Flags

None (the new page is facilitator-only; T-07-05..T-07-09 mitigations are covered by `test_no_schedule_string_names_an_attack`, `schedule.print_veil`, the validator tests and the invisibility test).

## Self-Check: PASSED

Files found: planspiel/schedule.py, the three new test files, this summary. Commits found: d204400, b0f5afc, fb358f0, 9238086.
