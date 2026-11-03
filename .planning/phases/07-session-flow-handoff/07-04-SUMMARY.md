---
phase: 07-session-flow-handoff
plan: 04
subsystem: facilitator-booklet
tags: [debrief, config, booklet, texts, lint]
requires: [07-02]
provides:
  - "simulation_config.json session_schedule.debrief_stages (reaction 3, description 4, analysis 8, application 5 minutes = the 20-minute debrief block)"
  - "DebriefStage / SessionSchedule.debrief_stages and the validator codes schedule.debrief_sum and schedule.debrief_block"
  - "planspiel/debrief.py (PROMPT_STAGES, DebriefSection, DebriefPage, build_debrief_page)"
  - "sheets.debrief texts in content/texte.toml (ten entries over four stages, three data prompts, compare table labels)"
  - "debrief page in spielleitung-uebersicht after the Budget Review / Endergebnis page, before Welle 0 key and clue matrix"
affects: [07-05, 07-08, 07-09]
tech-stack:
  added: []
  patterns: ["optional config sub-list read by one print module", "keys generated from config stage ids only when debrief_stages exists"]
key-files:
  created:
    - planspiel/debrief.py
    - tests/test_debrief_model.py
  modified:
    - simulation_config.json
    - planspiel/config.py
    - planspiel/validate.py
    - planspiel/texts.py
    - planspiel/master.py
    - content/texte.toml
    - print/templates/master.tex.j2
    - tests/test_session_schedule_config.py
    - tests/test_texts_number_words.py
    - tests/test_master_pdf.py
key-decisions:
  - "Guide minutes reaction 3, description 4, analysis 8, application 5 (sum 20); analysis gets the most because it carries two data prompts"
  - "Stage ids, minutes and team count come from config; the prose never types a count (shared phase-7 lint covers sheets.debrief)"
  - "build_debrief_page returns None when the schedule or debrief_stages is missing; a PROMPT_STAGES entry naming a stage the config lacks raises PrintModelError"
  - "Page title is Debriefing-Fragen (not Debriefing) so a page search for it cannot match the Endergebnis note or the schedule block label"
requirements-completed: [FLOW-03]
duration: ~45 min
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 04: Debrief question set Summary

The facilitator booklet now carries a one-page debrief (reaction, description, analysis, application) with ten fixed questions and data prompts, guide minutes from config that the validator proves add up to the 20-minute debrief block, and an empty KZ / RoS / Final-Index comparison table with one row per team.

## Tasks and commits

| Task | Commit | Result |
|------|--------|--------|
| 1 | 71b3eac | `session_schedule.debrief_stages`, `DebriefStage`, `check_debrief_stages` (codes `schedule.debrief_sum`, `schedule.debrief_block`, plus `schedule.id`, `schema.range`, `schema.keys` for stages) |
| 2 | 894d09d | `planspiel/debrief.py`, `sheets.debrief` texts, gated `required_keys` branch (stage ids and prompt names), `sheets.debrief` in `PHASE7_PREFIXES` |
| 3 | 9cb526f | `MasterSheet.debrief`, debrief page and contents entry in `master.tex.j2`, two PDF tests |

TDD: RED tests written first in each task (ImportError / AttributeError), confirmed failing, then GREEN.

## Content shape (D-09, D-10, D-11)

- Reaction: 2 questions. Description: 2 questions plus the compare prompt (KZ, RoS, Final-Index; table below). Analysis: 1 question plus the clue prompt (pointer ends with the clue-matrix title from `sheets.spielleitung.clues_title`) and the change-window prompt. Application: 2 transfer questions (first measure in the own company, real CIA trade-offs), no data prompt. Ten entries in total.
- No debrief string names an attack, types a digit or spells out a count; the name-hit test and the shared number-word lint pass without any `ALLOWED` entry.

## Verification

- Wave-1 integration gate (run before the first RED test): `uv run pytest -q -x` gave `2770 passed, 187 deselected, 219 warnings in 184.64s`.
- Task 1: `uv run pytest tests/test_session_schedule_config.py tests/test_practice_config.py -q` 73 passed; Task 2: 75 passed in the four touched test files.
- `uv run pytest -m pdf tests/test_master_pdf.py -q`: 16 passed (including the two new tests and the tail test).
- End gate full fast suite `uv run pytest -q`: `2796 passed, 189 deselected, 219 warnings in 182.20s` (the 189 deselected include the two new pdf tests).
- `uv run planspiel validate` and `uv run planspiel texts`: 0 Fehler, 0 Warnung(en).
- Fill report (pt used of 731.2 pt text height): overview page 511.5 (was 498.8, one more contents line), Budget Review / Endergebnis page 689.8, debrief page 502.1.
- `content/digit_allowlist.toml`, `tests/fixtures/` and `final_documents/generated` unchanged; no PDF committed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Debrief title matched the Endergebnis page**
- **Found during:** Task 3 test design
- **Issue:** The planned title "Debriefing" occurs in `final_index_note` on the Endergebnis page, so a first-page-with search starting at the review page would resolve to that page and not to the debrief page.
- **Fix:** Title set to "Debriefing-Fragen"; the intro and labels carry the remaining wording.
- **Files modified:** content/texte.toml
- **Commit:** 9cb526f

**2. [Rule 3 - Blocking] Template snippet written with unescaped backslashes**
- **Found during:** Task 3 (first PDF run: "Text line contains an invalid character")
- **Issue:** A Python-string insertion turned `\a`, `\v`, `\n`, `\t` sequences into control characters.
- **Fix:** Reverted the template and inserted the snippet from a file without escape processing.
- **Files modified:** print/templates/master.tex.j2
- **Commit:** 9cb526f

### Notes

- `planspiel/config.py` and `planspiel/validate.py` keep their CRLF endings; edits were made preserving them.
- `DEBRIEF_PROMPT_KEYS` in `texts.py` repeats the three prompt names of `debrief.PROMPT_STAGES` (texts cannot import debrief); `test_required_keys_follow_the_config_stages` pins that both agree.

## Known Stubs

None. The comparison table is empty by design (writing surface for the facilitator).

## Threat Flags

None (T-07-15 covered by the name-hit test, T-07-16 by `schedule.debrief_sum` / `schedule.debrief_block` and the stage validator tests, T-07-17 by `fmt` plus `check_digits`).

## Self-Check: PASSED

Files found: planspiel/debrief.py, tests/test_debrief_model.py, this summary. Commits found: 71b3eac, 894d09d, 9cb526f.
