---
phase: 07-session-flow-handoff
plan: 07
subsystem: legacy-material
tags: [intro-deck, pptx, deck-test, flow-overview, team-size, LEG-02]
requires: [07-05, 07-01, 07-02]
provides:
  - "final_documents/Planspiel_Einführung + Grundlagen.pptx edited to the new session flow (36 slides, flow overview on slide 28, Pinnwand slide gone)"
  - "tests/test_intro_deck.py: DECK, MINUTE_SLIDES, TEAM_SIZE_SLIDE, TEAM_SIZE_TEXT, _slide_text, PLANSPIEL_DECK override; minute and team-size figures composed from session_schedule"
  - "07-DECK-CHECKLIST.md Result review record (verbatim approval of the edited deck)"
affects: [07-08, 07-10, 07-11]
tech-stack:
  added: []
  patterns: ["run-level python-pptx edits on a copy in build/deck/, then one binary commit after user review", "hand-maintained deck pinned by a config-composed regression test"]
key-files:
  created:
    - tests/test_intro_deck.py
  modified:
    - "final_documents/Planspiel_Einführung + Grundlagen.pptx"
    - content/INVENTORY.md
    - .planning/phases/07-session-flow-handoff/07-DECK-CHECKLIST.md
key-decisions:
  - "Deck edited exactly per the approved checklist (all recommendations, no override): slide-1 date removed, hidden slide 28 unhidden and rewritten as the six-phase flow overview, slide 36 (Pinnwand template with budget figure and attack names) deleted, 'Beratungsteam aus 5 Personen' from session_schedule.persons_per_team, break and block minutes without clock times, material lines renamed, slide-23 copy error fixed"
  - "Phishing, Malware, Supply Chain Attack on slides 19 and 21 stay as generic teaching examples (decision d); pinned in the test"
  - "MHP company profile and VWI decks untouched (checklist: 'None found', 0 hits)"
  - "The 82 MB deck was committed once (0b3642a, 82533307 -> 81228044 bytes), after the user's review"
requirements-completed: []
duration: ~5 h incl. user review
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 07: Intro deck update Summary

The hand-maintained intro deck now matches the new session flow: a six-phase overview (Einführung, Story-Gruppenarbeit, Übungswelle, Maßnahmen und Budget, Angriffswellen, Abschluss und Debriefing) without attack names, budget figure or minute figures replaces the Pinnwand template, the team-size line reads "Beratungsteam aus 5 Personen" from config, and a regression test composes every remaining minute figure and the team size from `session_schedule`. The user reviewed the edited deck in PowerPoint and answered "Freigeben" on 2026-11-03.

## What changed in the deck (all map to approved checklist rows)

| Slide | Old | New | Checklist row |
|-------|-----|-----|---------------|
| 1 | subtitle date "06.07.2026" | removed | decision (a) |
| 23 | the three category boxes carried threat texts | Physische / Technische / Organisatorische describe measures | decision (e1) |
| 26 | "5 Minuten Pause bis 15:00" | "5 Minuten Pause" | break_1 |
| 28 | hidden, five MHP phases, "Reflexion im Plenum" | visible, six-phase flow overview (shape group copied for phase 6) | decision (b), D-19 |
| 30 | "Beratungsteam aus 3–4 Personen" | "Beratungsteam aus 5 Personen" (persons_per_team) | decision (c), D-19 |
| 31 | "20 min", Beauftragungsmail material | "25 min", Anfrage-Mail and Audit-Mail material | story_groups, print_list |
| 32 | "Budget von 350.000 €", Budgetübersicht | budget without figure, Teamheft | budget_tiers, print_list |
| 33 | "20 Minuten Pause bis16:50" | "15 Minuten Pause" | break_2 |
| 34 | Angriffsblatt, Events material | Arbeitsblatt der Welle, Eventkarten, So funktioniert eine Welle | print_list |
| 35 | "Endergebnis und Reflexion", Endergebnisblatt | "Abschluss und Debriefing", Teamheft ("30 min" kept = closing 10 + debrief 20) | closing, debrief |
| 36 | Pinnwand template with "Bewilligtes Budget: 150.000 €" and wrong attack names | slide deleted | decision (b), D-19 |

Slide count 37 -> 36. Auto date fields were not touched. Rows not changed: slides 25, 29 (checked against the Steckbrief), 22, 6, 7, 19, 21 and slide 34's Change-Fenster sentence (decision e2: no).

## Other decks (SC4)

The MHP company profile deck and the VWI deck were searched (29 and 33 slides, slides and notes) and have 0 hits for every game term. No `07-07` row, no `gap` row; both decks untouched.

## Task commits

1. Task 1 RED, deck test: `afa2c17` (`test(07-07): pin the approved intro deck changes`), `55a016b` (read the flow phases by column position)
2. Task 2 GREEN, inventory row: `d5a0921` (deck edited on a copy and verified, deck not committed yet)
3. Task 3 user review "Freigeben", deck and checklist committed once: `0b3642a`

## Verification

`uv run pytest tests/test_intro_deck.py tests/test_inventory.py -q`: 33 passed on the committed deck. The full suite was 2854 passed at the checkpoint. Per the plan, the integration run of the full suite belongs to 07-08.

## Deviations from Plan

None. The plan executed as written; the user answered "Freigeben" with no corrections.

## Known Stubs

None.

## Threat Flags

None. T-07-26 (veil: no name hit on the flow slide, decision d pinned), T-07-27 (copy edit, run-level, text diff, user review, single commit) and T-07-28 (figures composed from `session_schedule`) are mitigated as planned.

## LEG-02 status

Part 2 of 4 done (07-05 checklist, 07-07 deck). LEG-02 stays open until 07-10 and 07-11 are finished, so it is not marked complete here.

## Self-Check: PASSED

- `tests/test_intro_deck.py`, `07-DECK-CHECKLIST.md` Result review, the edited deck: found
- Commits `afa2c17`, `55a016b`, `d5a0921`, `0b3642a`: found in `git log`
- `git status` shows only the untouched `.claude/settings.local.json` as modified
