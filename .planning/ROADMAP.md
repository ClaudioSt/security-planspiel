# Roadmap: CIA-Planspiel Automotive — Post-Workshop Refinement

## Overview

This milestone turns the MHP workshop feedback into a game that facilitators and players can run by hand without ambiguity. First the simulation gets a safe base: a reproducible environment, characterization tests, one shared rules module, exact arithmetic, and a memory-safe enumeration that includes over-budget plans. Next the rules participants stumbled over are settled test-first. In parallel, all German prose moves into one veiled/revealed content source. After that a LaTeX pipeline generates the attack worksheets, which carry the most print-sync risk, and proves them equal to the simulation. The remaining cards and sheets follow, including the tracking sheet and the "Welle 0" worked example. Only once every document is generated does the config get rebalanced against the design principles, so each tuning step costs one command. The milestone ends with a revised session flow, legacy files retired, and a timed dry run by someone who did not write the rules. Order principle: *rule definitions* before templates, *numeric values* after the generator exists.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Simulation Foundation** - Reproducible env, characterization tests, shared `planspiel/` rules module, exact arithmetic, streaming enumeration incl. over-budget plans, config validator
- [ ] **Phase 2: Rule Changes** - Settle Levelwechsel/Maßnahmenwechsel, downgrade, linear overspend penalty + gate, Sparprogramm window, RoS ledger, Budget Review boundaries, E-target mechanic (TDD)
- [ ] **Phase 3: Content Source & Veiling** - All German prose in one content source keyed by config id, veiled vs revealed attack texts, clue matrix
- [ ] **Phase 4: Print Pipeline & Attack Worksheets** - Non-interactive, reproducible LaTeX → PDF build; generated Angriff 1–3 worksheets proven equal to the simulation
- [ ] **Phase 5: Player & Facilitator Print Material** - Measure/event/Budget Review cards, budget + RoS sheets, tracking sheet, "So funktioniert eine Welle", Welle 0, facilitator master sheet, veiling scan
- [ ] **Phase 6: Rebalance** - Calibrate X and all values by full enumeration against design principles 1–4, then regenerate all print material
- [ ] **Phase 7: Session Flow & Handoff** - Revised schedule with debrief, "Was ist neu", legacy files archived, docs updated, timed dry run

## Phase Details

### Phase 1: Simulation Foundation

**Goal**: The maintainer can change simulation code safely. One reproducible environment, current outputs pinned by tests, every formula in one shared module, exact arithmetic, and a memory-safe enumeration that includes over-budget plans.
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04, FOUND-05, FOUND-06, FOUND-07
**Success Criteria** (what must be TRUE):

  1. On a fresh clone, one command sets up the environment and `uv run pytest` passes; every documented script command runs via `uv run`, whichever `python` is on PATH.
  2. Characterization tests pin KZ, damage, costs and RoS per selection and tier, and they pass against the refactored code. In that code every formula exists once in `planspiel/` and the root scripts are thin wrappers. Any deviation caused by exact arithmetic shows up as an explicit, reviewed snapshot change.
  3. Loading the config yields correct German text (real umlauts/ß, no mojibake). The shared rounding/step helper returns the paper result at boundary inputs (exactly 10.000 €, 10.001 €, zero, negative amounts).
  4. A full enumeration per tier, including over-budget combinations, finishes without exhausting memory and reports top-K, percentiles, best in-budget vs best over-budget, and the Pareto count. A complete dump is written only on explicit request.
  5. The config validator rejects a config with a broken reference (e.g. an unknown measure id). It warns on hand-calculability violations, flagging today's wave-3 KZ slope (17/7) and any broken printed invariant such as `base_severity != mitigation_cap`.

**Plans**: 4/7 plans executed

Plans:

- [x] 01-01-PLAN.md — FOUND-01: uv environment, lockfile, `planspiel` package skeleton (Wave 1)
- [x] 01-02-PLAN.md — FOUND-04: UTF-8 everywhere, real umlauts in config (Wave 2)
- [x] 01-03-PLAN.md — FOUND-02: golden characterization tests + full per-tier digests (Wave 3)
- [x] 01-04-PLAN.md — FOUND-03: every formula once in `planspiel/`, root scripts as thin wrappers (Wave 4)
- [ ] 01-05-PLAN.md — FOUND-07: config validator (errors + hand-calculability warnings) (Wave 5)
- [ ] 01-06-PLAN.md — FOUND-05: exact arithmetic + paper rounding/step helper (Wave 6)
- [ ] 01-07-PLAN.md — FOUND-06: bounded full enumeration incl. over-budget, compact report (Wave 7)

### Phase 2: Rule Changes

**Goal**: Every rule participants stumbled over at MHP is defined unambiguously, implemented test-first in the shared rules module and documented in README. Templates can then be written against a settled rule set. Numeric values (X, slopes, weights) stay provisional until Phase 6.
**Depends on**: Phase 1
**Requirements**: RULE-01, RULE-02, RULE-03, RULE-04, RULE-05, RULE-06, RULE-07, RULE-08
**Success Criteria** (what must be TRUE):

  1. README and config distinguish "Levelwechsel" (same measure, other level) from "Maßnahmenwechsel" (swap one measure for another), and the Kurswechsel event names exactly which move it allows. The simulation models change-window moves, including a downgrade that keeps initial costs sunk and lowers OPEX from the next wave.
  2. A plan over budget loses X KZ per started 10.000 € (X read from config, penalty lookup table derivable for print). A team pushed over budget by an event such as Sparprogramm is penalized only if it is still over budget after the change window.
  3. The overspend gate runs per tier in the test suite and compares every over-budget plan with its own trimmed in-budget version. It reports the minimum X required under current values and fails, naming the offending plan, when X in config is set too low.
  4. RoS for any selection is identical with and without event cost effects (penalties and discounts); only initial costs, regular OPEX and the Kurswechsel init difference count. Budget Review tiers give the same result in sim and print at the 25k/50k/75k boundaries, with boundary text derived from the tier list.
  5. The per-wave E-target KZ bonus/malus is resolved against the printed MHP material and the decision is logged in PROJECT.md. It is either removed from the simulation or registered as a mechanic the worksheets must print.

**Plans**: TBD
**Research flag**: yes. Topics: trim-back criterion mechanics ("trimmed version" definition, interaction with step rewards: OEM-Audit tiers, M7 tiers, Exzellenz +5/L3, E-target bonus) and a bounded change-model enumeration for downgrade/swap moves in the change window.

### Phase 3: Content Source & Veiling

**Goal**: All German prose exists once, in a content source keyed by config id, with separate veiled and revealed attack texts. Templates then contain only layout, and players can infer the coming attack but never read its name.
**Depends on**: Phase 1 (independent of Phase 2; the two can be worked in parallel)
**Requirements**: PRINT-02, VEIL-01, VEIL-03
**Success Criteria** (what must be TRUE):

  1. Every prose text used on print material lives in one UTF-8 content source keyed by config id: measure descriptions formerly in `MEASURE_META`, event narratives, attack texts and sheet instructions. A coverage check fails on missing or orphaned keys.
  2. A lint fails if narrative prose contains digits, so every printed number has to come from config.
  3. Each attack has a veiled pre-attack text and a revealed at-wave text. The veiled texts contain no attack names and none of the listed technical giveaway terms.
  4. A facilitator clue matrix shows, per attack, at least two clues and where each appears in the pre-wave material. A check fails if any attack has fewer than two.
  5. An inventory of the current hand-maintained docx/pptx (wording, colours, branding) shows every item either carried into the content source or deliberately dropped.

**Plans**: TBD

### Phase 4: Print Pipeline & Attack Worksheets

**Goal**: The Angriff 1–3 worksheets carry the highest print-sync risk because facilitators calculate from them by hand. They are generated from config through a proven, non-interactive LaTeX pipeline and provably compute the same results as the simulation.
**Depends on**: Phase 2, Phase 3
**Requirements**: PRINT-01, PRINT-03, PRINT-04, PRINT-11
**Success Criteria** (what must be TRUE):

  1. One command rebuilds the attack worksheets as PDFs from `simulation_config.json` without any interactive MiKTeX prompt (a missing package fails fast instead of hanging). Two builds from identical inputs produce byte-identical PDFs.
  2. The generated Angriff 1–3 worksheets show thresholds, caps, bonus tables and the case 1/2/3 calculation steps, all derived from config. Changing a threshold in config and rebuilding changes the printed number with no template edit.
  3. An equivalence test replays the printed hand-calculation steps over a dense input grid and matches the simulation for every input. The test fails if the simulation applies a mechanic the worksheet does not print.
  4. Every generated page carries a version stamp (config hash and date) in its footer.

**Plans**: TBD
**Research flag**: yes. Topics: non-interactive MiKTeX build (update 23.10 → current, `--disable-installer`, subprocess timeout) as the first-plan smoke gate, then worksheet/card layout (tcolorbox raster, print scaling, cut lines). Spike-compile only, no full card sheet.

### Phase 5: Player & Facilitator Print Material

**Goal**: Every remaining card and sheet that players and facilitators use is generated from config and explains the mechanics. Nothing a player sees before a wave gives away the attack.
**Depends on**: Phase 4
**Requirements**: PRINT-05, PRINT-06, PRINT-07, PRINT-08, PRINT-09, PRINT-10, VEIL-02, VEIL-04, FLOW-01
**Success Criteria** (what must be TRUE):

  1. The same one command generates measure cards (10 measures × 3 levels, CIA values, costs and dependencies only, with a "how to read this card" legend), event cards and the Budget Review card with effect lines derived from event type and parameters, plus the budget and RoS sheets.
  2. A team can run a wave on the printed tracking sheet in calculation order, with separate rows for own costs and external effects, guided by the one-page "So funktioniert eine Welle" and without a whiteboard write-up.
  3. The worked example "Welle 0" (fictional practice incident, deliberately mediocre selection) is generated from the rules module. A golden test fails if its printed numbers diverge from the simulation.
  4. The facilitator master sheet lists per-wave thresholds, caps, bonus tables, event effects, check rows and answer keys for reference selections, all matching the simulation.
  5. An automated scan of all pre-wave material (text, file names, PDF metadata) finds no attack names and no wave CIA weights. Measure→attack bonus links and wave weights appear only on the revealed attack worksheets.

**Plans**: TBD

### Phase 6: Rebalance

**Goal**: The config is tuned so the design principles hold under full enumeration: overspending never pays, every choice matters, good play wins, mediocre play still ends positive, and tiers stay comparable. All print material reflects the final numbers.
**Depends on**: Phase 5
**Requirements**: BAL-01, BAL-02, BAL-03, BAL-04, BAL-05, BAL-06, BAL-07, BAL-08, BAL-09
**Success Criteria** (what must be TRUE):

  1. X is calibrated per tier on the trim-back criterion (raw and capped KZ) and the overspend gate passes with it. If the required X was impractical, the user chose between capping overspend and softening step rewards from presented numbers, and the gate passes under that choice.
  2. The validator runs with hand-calculability checks as errors and passes: every worksheet slope and constant is hand-friendly, and no 17/7-type slope remains.
  3. The per-tier balance report runs without the 0.85 utilization filter and shows top-K, Pareto points and unfiltered optima. Final-Index weights are rescaled from measured data so RoS·100 no longer dominates KZ.
  4. Design-principle checks pass per tier under full enumeration. No measure/level is strictly dominated or near-mandatory, and every decision point shifts outcomes. Good reference strategies rank in the top quartile and bad ones in the bottom quartile. A mediocre strategy ends above start KZ, a comeback after wave 1 is possible, and best results and spread stay comparable across tiers.
  5. All print material is regenerated from the rebalanced config with one command, and the print≡sim equivalence and Welle-0 golden tests pass on the new values.

**Plans**: TBD
**Research flag**: yes. Topics: calibration method (trim-back sweep over cached per-combo tuples instead of re-enumerating), concrete metrics and thresholds for BAL-06…09 (dominance, "near-mandatory", quartile placement, spread range), Final-Index rescaling.

### Phase 7: Session Flow & Handoff

**Goal**: A facilitator who did not write the rules can run the new version in one afternoon from the generated material alone. Legacy hand-maintained files are retired and the docs describe the new pipeline.
**Depends on**: Phase 6
**Requirements**: FLOW-02, FLOW-03, FLOW-04, FLOW-05, LEG-01, LEG-02
**Success Criteria** (what must be TRUE):

  1. The revised session schedule drops the whiteboard step, gives wave 1 20 minutes and includes a 15–20 min debrief. The debrief has a question set (reaction → description → analysis → application), and the whole session still fits one afternoon.
  2. A facilitator who ran the MHP version learns every rule change from a one-page "Was ist neu" sheet.
  3. The legacy hand-maintained docx/pptx worksheets and cards, the old pptx generators, `pptx_output/` and the Excel attack calculator are in `archive/`, and the build no longer uses any of them.
  4. README.md and CLAUDE.md describe the new pipeline and rules, with the print-sync section rewritten. The manually maintained intro deck, Audit-Mail and company profile contain no outdated rules.
  5. Someone who did not write the rules completes a timed dry run using only the material, and each wave fits the schedule.

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 (Phase 3 depends only on Phase 1 and may be worked alongside Phase 2)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Simulation Foundation | 4/7 | In Progress|  |
| 2. Rule Changes | 0/TBD | Not started | - |
| 3. Content Source & Veiling | 0/TBD | Not started | - |
| 4. Print Pipeline & Attack Worksheets | 0/TBD | Not started | - |
| 5. Player & Facilitator Print Material | 0/TBD | Not started | - |
| 6. Rebalance | 0/TBD | Not started | - |
| 7. Session Flow & Handoff | 0/TBD | Not started | - |
