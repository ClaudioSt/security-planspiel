---
status: complete
phase: 05-player-facilitator-print-material
source: [05-VERIFICATION.md]
started: 2026-10-26T15:10:23Z
updated: 2026-10-27T00:53:06Z
---

## Current Test

[testing complete]

## Tests

### 1. Print spieler-eventkarten.pdf (both sheets, single-sided, colour, 100 %). Read Kurswechsel, OEM-Audit and Budget Review aloud as a facilitator. (05-05 human-check + orchestrator item a)
expected: Every card fits its A6 cell; OEM-Audit rows read 0 erfuellt -> KZ -15 ... 5 erfuellt -> KZ +15 with the measure list; Budget Review shows tiers and overspend rule in euros; nothing names an attack. Kurswechsel card (98 % fill, caption band dropped on event cards) is legible; effect boxes have less inner padding than the approved measure-card factboxes - decide if acceptable.
result: pass

### 2. Print spieler-teamheft.pdf, plan a medium-tier selection of five measures on page 1 with the printed measure cards, fill the RoS page with invented damages. (05-06 human-check + orchestrator item b)
expected: Every value written once; tier table and anticipated-sum line make the budget check obvious; RoS page computes without a calculator beyond one division; overspend table readable. RoS page is about 43 % empty: decide if acceptable. Carried sums and the OPEX-event sign hint are understandable.
result: pass

### 3. Play wave 1 for one medium-tier team using booklet, both decks, angriff-1 worksheet and the tracking page; do the Kurswechsel swap plus one upgrade in change window 1. (05-07 human-check + orchestrator item c)
expected: Exactly one place to write per step; own costs and external effects clearly separate; swap credit and net Init difference computable without help; remaining budget after wave 1 obvious; no whiteboard. Tracking page is 99 % full with 6 mm rows and about 1.3-1.5 mm clearance (below the ~1.5-2 mm preference); window headers and where the net Init difference goes must be clear.
result: pass

### 4. Give spieler-so-funktioniert-eine-welle.pdf to someone who has not read the rules, with a blank attack worksheet and the tracking page; ask them to explain the order of one wave. (05-08 human-check + orchestrator item d)
expected: They name events -> attack steps -> recovery -> round once -> clamp -> change window, say what events change versus attacks, and find no hint which attack comes. Page is at 98 % fill with 9 pt step text (user prefers generous type); right-to-left second diagram row and recovery factor shown as % must read naturally.
result: pass

### 5. Open the four story PDFs next to the legacy files in final_documents/ and print the newspaper. (05-10 human-check + orchestrator item f)
expected: Newspaper reads like a newspaper page (masthead, two columns, both images legible in print); Steckbrief and mails look like a company profile and e-mails; texts are the veiled Phase 3 texts; no document names an attack.
result: pass

### 6. Print uebung-welle-0.pdf and walk through it as the facilitator would before wave 1. (05-12 human-check + orchestrator item e)
expected: Every box filled and readable; example lands in Fall 3, shows one bonus met (cross) and one missed (dash), applies recovery, shows the half rounded away from zero, tracking excerpt shows clamp to 100; story is the approved one. Damage-before-recovery is printed without the euro sign: decide if acceptable.
result: pass

### 7. Print spielleitung-uebersicht.pdf; check one filled team worksheet (Welle 0 or an invented GR for wave 2) against the quick-check table; follow the medium reference path through all waves with the answer keys. (05-15 human-check + orchestrator item g)
expected: A team's sheet can be checked in seconds from the check rows; answer keys read in calculation order; facilitator-only notice unmistakable; approximation signs explained; clue matrix usable during discovery.
result: pass

### 8. Physical print of the measure card sheets (05-03 checkpoint, already approved per SUMMARY) - only re-check if the factbox padding decision in item (a) is revisited.
expected: Cards cut cleanly to size; legend readable.
result: pass

## Summary

total: 8
passed: 8
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none]
