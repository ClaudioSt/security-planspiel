---
phase: 05-player-facilitator-print-material
verified: 2026-10-26T16:30:00Z
status: human_needed
score: 6/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
gaps: []
deferred:
  - truth: "Reference paths and answer keys re-chosen after rebalance; final-index weights rescaled; Welle 0 and worksheet goldens re-pinned; 17/7 slope and approximations removed"
    addressed_in: "Phase 6"
    evidence: "ROADMAP Phase 6 'Carried over from Phase 5' bullets and SC2/SC3/SC5 (BAL-02, BAL-03, BAL-05)"
human_verification:
  - test: "Print spieler-eventkarten.pdf (both sheets, single-sided, colour, 100 %). Read Kurswechsel, OEM-Audit and Budget Review aloud as a facilitator. (05-05 human-check + orchestrator item a)"
    expected: "Every card fits its A6 cell; OEM-Audit rows read 0 erfuellt -> KZ -15 ... 5 erfuellt -> KZ +15 with the measure list; Budget Review shows tiers and overspend rule in euros; nothing names an attack. Kurswechsel card (98 % fill, caption band dropped on event cards) is legible; effect boxes have less inner padding than the approved measure-card factboxes - decide if acceptable."
    why_human: "Legibility, padding and wording on paper cannot be judged from PDF text"
  - test: "Print spieler-teamheft.pdf, plan a medium-tier selection of five measures on page 1 with the printed measure cards, fill the RoS page with invented damages. (05-06 human-check + orchestrator item b)"
    expected: "Every value written once; tier table and anticipated-sum line make the budget check obvious; RoS page computes without a calculator beyond one division; overspend table readable. RoS page is about 43 % empty: decide if acceptable. Carried sums and the OPEX-event sign hint are understandable."
    why_human: "Usability of a paper form in calculation order needs a human run-through"
  - test: "Play wave 1 for one medium-tier team using booklet, both decks, angriff-1 worksheet and the tracking page; do the Kurswechsel swap plus one upgrade in change window 1. (05-07 human-check + orchestrator item c)"
    expected: "Exactly one place to write per step; own costs and external effects clearly separate; swap credit and net Init difference computable without help; remaining budget after wave 1 obvious; no whiteboard. Tracking page is 99 % full with 6 mm rows and about 1.3-1.5 mm clearance (below the ~1.5-2 mm preference); window headers and where the net Init difference goes must be clear."
    why_human: "ROADMAP SC2 is a usability claim about the paper form; row clearance is a physical handwriting judgement"
  - test: "Give spieler-so-funktioniert-eine-welle.pdf to someone who has not read the rules, with a blank attack worksheet and the tracking page; ask them to explain the order of one wave. (05-08 human-check + orchestrator item d)"
    expected: "They name events -> attack steps -> recovery -> round once -> clamp -> change window, say what events change versus attacks, and find no hint which attack comes. Page is at 98 % fill with 9 pt step text (user prefers generous type); right-to-left second diagram row and recovery factor shown as % must read naturally."
    why_human: "Comprehensibility and type-size preference need a reader"
  - test: "Open the four story PDFs next to the legacy files in final_documents/ and print the newspaper. (05-10 human-check + orchestrator item f)"
    expected: "Newspaper reads like a newspaper page (masthead, two columns, both images legible in print); Steckbrief and mails look like a company profile and e-mails; texts are the veiled Phase 3 texts; no document names an attack."
    why_human: "Visual design and story atmosphere need human judgement"
  - test: "Print uebung-welle-0.pdf and walk through it as the facilitator would before wave 1. (05-12 human-check + orchestrator item e)"
    expected: "Every box filled and readable; example lands in Fall 3, shows one bonus met (cross) and one missed (dash), applies recovery, shows the half rounded away from zero, tracking excerpt shows clamp to 100; story is the approved one. Damage-before-recovery is printed without the euro sign: decide if acceptable."
    why_human: "Teaching quality of the worked example needs a facilitator's judgement"
  - test: "Print spielleitung-uebersicht.pdf; check one filled team worksheet (Welle 0 or an invented GR for wave 2) against the quick-check table; follow the medium reference path through all waves with the answer keys. (05-15 human-check + orchestrator item g)"
    expected: "A team's sheet can be checked in seconds from the check rows; answer keys read in calculation order; facilitator-only notice unmistakable; approximation signs explained; clue matrix usable during discovery."
    why_human: "Facilitator usability under time pressure needs a human run-through"
  - test: "Physical print of the measure card sheets (05-03 checkpoint, already approved per SUMMARY) - only re-check if the factbox padding decision in item (a) is revisited."
    expected: "Cards cut cleanly to size; legend readable."
    why_human: "Physical print fidelity"
---

# Phase 5: Player & Facilitator Print Material Verification Report

**Phase Goal:** Every remaining card and sheet that players and facilitators use is generated from config and explains the mechanics. Nothing a player sees before a wave gives away the attack.
**Verified:** 2026-10-26
**Status:** human_needed
**Re-verification:** No - initial verification

All automated evidence supports the goal. No gaps. The remaining items are paper-usability and layout-taste judgements that only a print run can settle.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC1 | One command generates measure cards (legend + 10x3), event cards, Budget Review card, budget and RoS sheets, with effect lines derived from type/parameters | VERIFIED | `planspiel print` builds 13 PDFs (manifest.json, `dirty:false`). `spieler-massnahmenkarten.pdf` 8 pages with "So liest du eine Massnahmenkarte" legend and cards showing only CIA, Init/OPEX, dependency lock. `spieler-eventkarten.pdf` carries Kurswechsel, Operative Unterstuetzung, Sparprogramm, OEM-Audit and Budget Review cards. `spieler-teamheft.pdf` (4 pp) has Budget und Planung and RoS/Budget Review pages. `eventtext.py`, `review_text.py`, `cards.py`, `booklet.py` exist; `test_event_text.py`, `test_budget_review_text.py` pass. |
| SC2 | Team can run a wave on the printed tracking sheet in calculation order, separate rows for own costs vs external effects, guided by "So funktioniert eine Welle", no whiteboard | VERIFIED (automated); usability routed to human | Teamheft text: "Tracking-Bogen", "Eigene Kosten (zaehlen fuer den RoS)", "Externe Effekte (zaehlen nicht fuer den RoS)", change-window grid, "Kurswechsel: Gutschrift Kunde"; one-page `spieler-so-funktioniert-eine-welle.pdf` (1 page) with the wave order. `test_tracking_model.py` replays against `evaluate_path`. |
| SC3 | Welle 0 generated from rules module; golden test fails if printed numbers diverge | VERIFIED | `uebung-welle-0.pdf` (3 pp); `practice.build_practice_document`, `rules.path_trace`; `tests/golden/welle0.json`, `tests/test_welle0_golden.py` (replays from worksheet fields, includes mutation tests). Independent check of printed E-value: 16*0.3+22*0.3+19*0.4 = 19, GR 19+4 = 23, consistent. Practice weights (0.3/0.3/0.4) differ from all three real waves (0.4/0.4/0.2, 0.2/0.2/0.6, 0.5/0.3/0.2); practice block proven invisible to waves 1-3 (`test_practice_config.py`, `test_path_trace.py`). |
| SC4 | Facilitator master sheet lists thresholds, caps, bonus tables, event effects, check rows, answer keys, matching the simulation | VERIFIED | `spielleitung-uebersicht.pdf` (12 pp): per-wave "Kennwerte der Welle", "Bonus-Tabelle mit Begruendung", "Pruefzeilen", "Loesungsschluessel", Budget Review, Endergebnis je Tier, Welle-0 key, clue matrix, reference paths per tier. `master.py`, `refpaths.py`; `tests/golden/answer_keys.json`; `test_master_model.py`, `test_reference_plans.py`, `test_master_pdf.py` pass. |
| SC5 | Automated scan of all pre-wave material (text, file names, PDF metadata) finds no attack names and no wave CIA weights; bonus links and weights only on revealed worksheets | VERIFIED | `veil.py` + `audience.py` (two-layer scan, `print.veil` build gate), `test_veil_*` and `test_story_veil.py` pass. Independent re-scan of the committed `spieler-*.pdf` text with the giveaway list (ransomware, verschluessel, loesegeld, phishing, emotet, exfil, datendiebstahl, darknet, sinumerik, SPS, APT, OT-Stoerung): hits only for "Phishing" on the M6 measure card (a defence term, documented D-24 names-only profile for the deck). "Angriff 1/2/3" ordinals in the teamheft are numbers, not names. Weights appear only as symbols (wC, wI, wA) in pre-wave documents, never as values. `pdfinfo` metadata (Title/Subject/Keywords) empty on all `spieler-*` PDFs. Names and weights appear in `angriff-*.pdf` and the facilitator sheet only. |
| SC6 | Four story documents generated from `[story.*]`, every clue quote appears in the rendered PDF | VERIFIED | Four story PDFs committed. Independent check: all 14 quotes of `content/clues.toml` found in the committed story PDFs after whitespace normalisation (0 missing). `test_story_pdf.py::test_every_clue_quote_is_in_the_pdf_of_its_source_document` passes. `uv run planspiel clues`: 0 errors. |

**Score:** 6/6 truths verified (0 present, behavior-unverified)

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|--------------|----------|
| 1 | Re-pin reference paths/answer keys, rescale final-index weights, re-pin Welle 0 goldens, remove 17/7 slope and approximation signs, review `MAX_PENALTY_ROWS` / `MAX_WINDOWS` layout guards | Phase 6 | ROADMAP Phase 6 "Carried over from Phase 5" and SC2/SC3/SC5 |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `final_documents/generated/*.pdf` (13) + `manifest.json` | Committed print set, fresh | VERIFIED | All 13 present with expected page counts; `planspiel print --check`: "Druckmaterial aktuell: Stand 2026-10-26 3878dab"; manifest `dirty:false`; working tree clean for the set |
| `planspiel/{cards,eventtext,review_text,booklet,wave_page,story,practice,master,refpaths,veil,audience}.py` | Models for each document | VERIFIED | Present, imported by print driver, covered by tests |
| `content/{texte,clues}.toml`, `content/assets/images` | Story/clue input | VERIFIED | Present; hashed image asset path (PRINT-12) covered by `test_print_assets.py` |
| `tests/golden/{welle0,answer_keys,worksheet_tex}.json` | Pins | VERIFIED | Present, used by golden tests |
| `simulation_config.json` `practice`, `reference_plans`, `final_index` | Config-driven data | VERIFIED | Top-level keys present |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `planspiel print` | all 13 jobs | texbuild/render + stamp | WIRED | One command produced the full set; `test_print_cli*.py`, `test_print_driver.py` pass |
| Print jobs | veil gate | `print.veil` on rendered .tex and built PDFs | WIRED | `test_veil_scan.py`, `test_story_pdf.py` metadata and layer-two assertions |
| Welle 0 / tracking / master | `rules.path_trace` / `evaluate_path` | replay tests | WIRED | `tests/support/worksheet_replay.py` replays printed fields independently |
| Clues | story PDFs | quote match | WIRED | Verified independently (14/14) |

### Data-Flow Trace (Level 4)

Printed numbers are produced by the rules module and config (no hardcoded values), proven by the print-equals-simulation replay tests and config-mutation tests (e.g. changing a level's Init in a config copy changes the card text). Status: FLOWING.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Fast suite | `uv run pytest -q` | 2272 passed, 153 deselected | PASS |
| PDF suite | `uv run pytest -m pdf -q` | 131 passed | PASS |
| Print set fresh | `uv run planspiel print --check` | aktuell, 13 Dokumente | PASS |
| Config validator | `uv run planspiel validate` | 0 Fehler, 1 Warnung (17/7, Phase 6) | PASS |
| Texts / clues | `uv run planspiel texts` / `clues` | 0 Fehler, 0 Warnungen each | PASS |
| Independent veil re-scan, clue-quote re-check | pdftotext / pypdf scripts | clean / 14 of 14 | PASS |

The slow digest test (`-m slow`) was not re-run here; 05-16 SUMMARY records 3 passed.

### Probe Execution

Step 7c: SKIPPED (no `probe-*.sh` declared or present).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| VEIL-02 | 05-01 | Pre-wave material has no attack names / wave weights, automated scan | SATISFIED | SC5 |
| PRINT-05 | 05-02, 05-03 | Measure cards 10x3 + legend | SATISFIED | SC1 |
| VEIL-04 | 05-04 | Cards show CIA/costs/dependencies only; bonus links and weights on attack worksheet | SATISFIED | Card text inspected; weights/bonus tables only in `angriff-*` and facilitator sheet |
| PRINT-06 | 05-05 | Event cards + Budget Review card, derived effect lines | SATISFIED | SC1 |
| PRINT-07 | 05-06 | Budget sheet and RoS sheet | SATISFIED | Teamheft pages |
| PRINT-08 | 05-07 | Tracking sheet in calculation order | SATISFIED (usability human) | SC2 |
| PRINT-09 | 05-08 | "So funktioniert eine Welle" | SATISFIED (comprehension human) | SC2 |
| PRINT-12 | 05-09, 05-10 | Story documents via LaTeX | SATISFIED | SC6 |
| FLOW-01 | 05-11, 05-12 | Welle 0 worked example, golden-tested | SATISFIED | SC3 |
| PRINT-10 | 05-13, 05-14, 05-15, 05-16 | Facilitator master sheet | SATISFIED | SC4 |

All 10 requirement IDs from the phase assignment appear in plan frontmatter and are marked Complete in REQUIREMENTS.md. No orphaned Phase 5 requirements.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `planspiel/`, `print/`, `content/`, `tests/` | - | TBD/FIXME/XXX scan | none | Only a binary PNG false positive; no debt markers |
| `simulation_config.json` | - | HandCalcWarning 17/7 slope (exfil) | Info | Known, scheduled for Phase 6 (BAL-02) |
| `planspiel/audience.py` | 21 | "Phishing" tolerated on the M6 card via names-only profile (D-24) | Info | Documented decision; defence term, not an attack name |

### Human Verification Required

See the `human_verification` list in the frontmatter (7 items: the 7 harvested `<human-check>` blocks from plans 05-05, 05-06, 05-07, 05-08, 05-10, 05-12, 05-15, merged with orchestrator print-test items a to g, plus one conditional physical-print re-check). Plan 05-16 contains no new check of its own. Main open judgement calls for the user:

- Event deck: Kurswechsel card at 98 % fill, reduced effect-box padding versus approved measure cards.
- Tracking page: 99 % full, 1.3-1.5 mm row clearance (below the 1.5-2 mm preference).
- Wave explainer: 9 pt step text at 98 % fill (below the preferred generous type).
- Teamheft RoS page about 43 % empty (spare room could be used for larger type).
- Welle 0: damage-before-recovery printed without the euro sign.

### Gaps Summary

No gaps. Every ROADMAP success criterion is backed by committed artifacts, passing tests and independent re-checks. Status is human_needed only because paper-usability and layout-taste checks are outstanding.

---

_Verified: 2026-10-26_
_Verifier: Claude (gsd-verifier)_
