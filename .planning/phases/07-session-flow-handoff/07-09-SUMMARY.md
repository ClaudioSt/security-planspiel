---
phase: 07-session-flow-handoff
plan: 09
subsystem: print-release
tags: [print-set, release, solo-timing, schedule, intro-deck, D-27, D-32, D-34, FLOW-05]
requires: [07-08, 07-01, 07-10, 07-11]
provides:
  - "Committed Phase 7 print set, release candidate 2 (commit 8cf1972, stamp Stand 2026-11-04 · 737ba65, 15 PDFs + manifest.json), released by the user on 2026-11-06 for the dry run on 2026-11-25"
  - "07-SOLO-TIMING.md: D-32/D-34 solo timing record with block verdict lines, the overall verdict line and the release note"
  - "session_schedule re-budget: wave_1 25 min, total_minutes 195 (D-34 deviation, user-approved)"
  - "Intro deck slide 34 composed per wave from session_schedule (tests/test_intro_deck.py)"
affects: [07-12]
tech-stack:
  added: []
  patterns: ["deck slide minute figure composed per wave in the regression test instead of one shared figure", "surgical zip patch of one pptx part so the binary changes in exactly one entry"]
key-files:
  created:
    - .planning/phases/07-session-flow-handoff/07-SOLO-TIMING.md
  modified:
    - simulation_config.json
    - tests/test_session_schedule_config.py
    - tests/test_was_neu_model.py
    - tests/test_intro_deck.py
    - "final_documents/Planspiel_Einführung + Grundlagen.pptx"
    - final_documents/generated/ (15 PDFs + manifest.json, twice: RC1 and RC2)
key-decisions:
  - "wave_1 re-budgeted from 20 to 25 minutes instead of closing a material gap: the solo run took 30 min, the time went to calculating and filling in, not to ambiguity; a team of five splits the work (user decision 2026-11-04)"
  - "Overall solo verdict stays OVERRUN in the record, 'resolved by user decision'; the release proceeded on the user's explicit approval, not on a WITHIN verdict"
  - "Slide 34 shows '25 min Welle 1, je 20 min Welle 2 und 3' (option A of three); the text box moved up one line so the wrapped text stays above the footer"
  - "FLOW-05 is not marked complete: this plan is part 2 of 3, the timed dry run (07-12) is what confirms it"
requirements-completed: []
duration: 3 sessions (2026-11-03 to 2026-11-06, waiting on the user)
completed: 2026-11-06
status: complete
---

# Phase 7 Plan 09: Print release and solo timing Summary

The Phase 7 print set is regenerated from committed inputs and released by the user as release candidate 2 (commit 8cf1972, `Stand 2026-11-04 · 737ba65`). A solo walk-through found "Maßnahmen + Budget" within its 30 minutes and wave 1 over (30 against 20), and the user resolved the overrun by re-budgeting wave 1 to 25 minutes (session total 190 to 195) instead of changing material; the dry run on 2026-11-25 re-measures it.

## Tasks and commits

| Task | Commit | Result |
|------|--------|--------|
| 1 (decision) | none (quoted in 6482639) | Print-list quantities confirmed, config unchanged |
| 2 | 6482639 | Print set, release candidate 1 (stamp Stand 2026-11-03 · 13d4090) |
| 3 prep | 9554f18 | `07-SOLO-TIMING.md` prepared with generated minutes and direction lines |
| 3 result | 8e70384 | Timing and decision recorded |
| 3 follow-up, RED | 8868ee0 | `tests/test_session_schedule_config.py` pins wave_1 = 25 and total = 195 |
| 3 follow-up, GREEN | 43d7be5 | `simulation_config.json` wave_1 25, total 195; Was-ist-neu test expects wave figures 20 and 25 |
| 3 follow-up, RED | 53c183f | `tests/test_intro_deck.py` composes slide 34 per wave |
| 3 follow-up, GREEN | d4b0cb8 | Deck slide 34 edited (the only commit of the deck binary) |
| 2 (round 2) | 8cf1972 | Print set, release candidate 2 (the released one) |
| 4 | this plan's closing docs commit | Release decision recorded |

## Print-list quantities (Task 1, D-27)

The user's answers on 2026-11-04, verbatim from the RC1 commit: Story-Dokumente "1 je Team (wie Config)"; Eventkarten "1 je Team (wie Config)"; "So funktioniert eine Welle" "1 je Team (wie Config)"; Übrige Mengen "Bestaetigt". `session_schedule.print_list` stayed unchanged: every player document and the practice sheet 1 per team and 1 for the facilitator; the three attack worksheets 1 per team and 1 for the facilitator; `spielleitung-uebersicht`, `spielleitung-was-ist-neu` and `spielleitung-probelauf` 0 per team and 1 for the facilitator.

## Solo timing (Task 3, D-32, D-34)

Round 1, 2026-11-04, one person alone with the RC1 material:

| Block | Planned | Actual | Result |
|-------|---------|--------|--------|
| measures_budget | 30 | 30 | WITHIN |
| wave_1 | 20 | 30 | OVERRUN |

No unclear points, no hesitations, no ST gap items. The chosen plan and the wave-1 values were not reported, so no recomputation against the rules was possible; this is recorded as "not reported". Against MHP: measures plus budget took 35 minutes there, attack 1 plus event 1 took 34.

## Verification

- Phase gate before RC1: quoted in 6482639 and the earlier report.
- Phase gate after the re-budget, before RC2: `uv run planspiel validate`, `texts` and `clues` each `0 Fehler, 0 Warnung(en)`; `uv run pytest -q` gave `2921 passed, 205 deselected, 219 warnings in 221.02s (0:03:41)`; `uv run pytest -m pdf -q` gave `157 passed, 2969 deselected in 213.95s (0:03:33)`.
- Build RC2: `uv run planspiel print` printed `Stand: Stand 2026-11-04 · 737ba65`, no "+lokal", 15 documents, manifest `"dirty": false`.
- Reproducibility: `uv run planspiel print --check` printed `Druckmaterial aktuell: Stand 2026-11-04 · 737ba65 (15 Dokument(e) in final_documents/generated)` and exited 0, both after the commit and after a second build; the second build left `git status --porcelain final_documents/generated` empty (byte-identical).
- Deck: `tests/test_intro_deck.py` 22 passed; a zip comparison of the old and new pptx shows exactly one differing part, `ppt/slides/slide34.xml`.
- Not run, as the plan requires: `-m slow`, `-m balance`, `planspiel gate --paths` (no rule or balance change).

## Deviations from Plan

### User-approved deviation

**1. [D-34 deviation] Overrun resolved by re-budgeting wave 1 instead of gap closure**
- **Found during:** Task 3
- **Issue:** The plan says an overrun of either block blocks the release and goes to a gap item. The solo run had wave_1 at 30 min against 20 planned.
- **Decision:** User, 2026-11-04: change the schedule so wave_1 is 25 minutes; every other block stays, so the total goes 190 to 195. The user accepts that the solo run still exceeds 25: a team of five splits the work, and the dry run measures the real time.
- **Fix:** config change with TDD (8868ee0, 43d7be5), the Was-ist-neu test now expects two distinct wave figures, intro deck slide 34 adapted, print set rebuilt as RC2.
- **Consequence:** `07-SOLO-TIMING.md` keeps `**Block wave_1:** OVERRUN` and an overall line `**Verdict:** OVERRUN resolved by user decision...`; the plan's must-have "released only after an overall WITHIN verdict" was replaced by the user's explicit release.

### Auto-fixed Issues

**2. [Rule 3 - Blocking] Deck test and Was-ist-neu test pinned a single wave figure**
- **Found during:** the schedule change
- **Issue:** `tests/test_was_neu_model.py` asserted that all wave blocks share one minute figure; `tests/test_intro_deck.py` composed slide 34 from all three wave blocks with one figure.
- **Fix:** the Was-ist-neu test now expects `[20, 25]` (the model already joined distinct figures); the deck test composes slide 34 per wave ("{first} min Welle 1, je {rest} min Welle 2 und 3").
- **Commits:** 43d7be5, 53c183f

**3. [Layout, within the approved one-shape deck edit] Slide 34 text box moved up one line**
- **Found during:** the deck edit
- **Issue:** the new text is about 39 characters; in the 3.2M-EMU-wide, right-aligned, auto-fit box at 18 pt it wraps to two lines and would grow into the footer.
- **Fix:** only shape id 3 on slide 34: run text changed (formatting kept), y 6090680 to 5783680 and height 399405 to 706405. A LibreOffice render showed the two right-aligned lines level with the "Material:" line, nothing overlapping. The user confirmed the slide after printing.
- **Commit:** d4b0cb8

## Release (Task 4)

User answer, 2026-11-06, to the release checkpoint: "freigeben". Release candidate 2 is approved after the physical print, including slide 34 of the intro deck. The released print-set commit is 8cf1972, and `uv run planspiel print --check` exits 0 on it.

Changed in content between RC1 and RC2 (TeX hash differs): `spielleitung-uebersicht.pdf` (Welle 1 25 min, offsets 100-125, Welle 2 125-145, Welle 3 145-165, Abschluss 165-175, Debriefing 175-195, total 195), `spielleitung-was-ist-neu.pdf` (schedule row 195 min in total, 20 / 25 per wave) and `spielleitung-probelauf.pdf` (new planned minutes and offsets). The other 12 PDFs only carry a new stamp.

## Follow-up for 07-12

- Re-measure wave 1 in the dry run on 2026-11-25: the solo run was 30 min against the new 25; the budget is accepted on the assumption that five people split the work, and the dry run decides whether 25 holds.
- Measures plus budget (30 min, within) and waves 0, 2, 3 are first timed with a real group there.
- The dry-run protocol (`spielleitung-probelauf.pdf`) already carries the new minutes.

## Known Stubs

None. This plan adds no code symbols and no placeholder content.

## Threat Flags

None. No new endpoint, auth path or trust-boundary surface; T-07-32 (stale PDFs), T-07-33 (facilitator PDFs for teams, 0 per team enforced by `schedule.print_veil`) and T-07-34 (hand edits) are mitigated as planned: clean-input build, `"dirty": false`, `--check` exit 0, byte-identical rebuild.

## Self-Check: PASSED

- Files: 07-SOLO-TIMING.md, 07-09-SUMMARY.md, `final_documents/generated/manifest.json` and the intro deck exist.
- Commits found in `git log`: 6482639, 9554f18, 8e70384, 8868ee0, 43d7be5, 53c183f, d4b0cb8, 8cf1972.
- `07-SOLO-TIMING.md` verify command (both block lines, one overall `**Verdict:**` line) passes.
