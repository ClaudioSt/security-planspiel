---
phase: 07-session-flow-handoff
plan: 05
subsystem: intro-deck-checklist
tags: [deck, checklist, approval, sc4, leg-02]
requires: [07-02]
provides:
  - "07-DECK-CHECKLIST.md: slide-by-slide edit list for the intro deck, approved by the user on 2026-11-03 (D-18)"
  - "SC4 evidence: MHP company profile deck, VWI deck and the generated story documents contain no outdated rule"
affects: [07-07]
tech-stack:
  added: []
  patterns: ["checklist first, user approval, then binary edit in a later plan"]
key-files:
  created:
    - .planning/phases/07-session-flow-handoff/07-DECK-CHECKLIST.md
  modified: []
key-decisions:
  - "(a) Slide-1 date is removed (no fixed date for the next workshop)"
  - "(b) Slide 28 is unhidden and rewritten as the six-phase flow overview, slide 36 is deleted (D-19)"
  - "(c) Team size on slide 30 is composed from session_schedule.persons_per_team (Beratungsteam aus 5 Personen), pinned by the 07-07 deck test"
  - "(d) Phishing, Malware and Supply Chain Attack on slides 19 and 21 stay as generic teaching examples"
  - "(e1) Slide-23 copy error is fixed; (e2) no Change-Fenster sentence on slide 34"
requirements-completed: []
duration: ~25 min
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 05: Intro deck checklist Summary

Sourced, unpadded checklist for the intro deck "Planspiel_Einführung + Grundlagen.pptx", approved as written ("Freigeben", 2026-11-03), plus the SC4 check of the other hand-maintained documents. The deck was only read, not modified: `git status --porcelain final_documents` is empty.

LEG-02 is part 1 of 4 here (checklist and approval). It is not marked complete: the deck edit (07-07), the German README (07-10) and the English CLAUDE.md with the codebase maps (07-11) are still open.

## Accomplishments

- Extracted all 37 slides (hidden flags, shapes, speaker notes) of the intro deck and wrote the slide table with current text, problem, proposed change and config source per row. Every minute figure cites its `session_schedule.blocks.*` key, the team size cites `session_schedule.persons_per_team`, clock times are dropped (D-04), slide 36 loses attack names and the budget figure (D-19).
- Searched all three decks for Whiteboard, Pinnwand and Tafel (D-02); the only hit is the slide-36 title.
- Listed what is not in the deck (E-target bonus/malus, Maßnahmenwechsel, flat -15, Budget Review 25.001 boundaries, RoS with event effects).
- SC4: MHP company profile (29 slides) and VWI deck (33 slides) have 0 hits for the game terms; `uv run planspiel texts` printed 0 errors, 0 warnings for the Audit-Mail, Steckbrief, Anfrage-Mail and Zeitungsartikel. `## Other deck findings` says "None found".
- Recorded the approval with the verbatim verdict, date and the outcome of decisions (a) to (e2) in `## Approval`.

## Task Commits

1. Task 1, extract and write checklist: cb8fa52
2. Task 2, record approval (checkpoint:decision): 9fda8cf

## Deviations from Plan

None - plan executed exactly as written. No slide row changed at approval.

## Known Stubs

None.

## Threat Flags

None. T-07-18 (veil), T-07-19 (deck untouched) and T-07-20 (figures cite config keys) are mitigated as planned.

## Self-Check: PASSED

- 07-DECK-CHECKLIST.md exists and contains `## Approval` with "Freigeben"
- Commits cb8fa52 and 9fda8cf exist
- `git status --porcelain final_documents` empty
