# Roadmap: CIA-Planspiel Automotive — Post-Workshop Refinement

## Overview

This milestone turns the MHP workshop feedback into a game that facilitators and players can run by hand without ambiguity. First the simulation gets a safe base: a reproducible environment, characterization tests, one shared rules module, exact arithmetic, and a memory-safe enumeration that includes over-budget plans. Next the rules participants stumbled over are settled test-first. In parallel, all German prose moves into one veiled/revealed content source. After that a LaTeX pipeline generates the attack worksheets, which carry the most print-sync risk, and proves them equal to the simulation. The remaining cards and sheets follow, including the tracking sheet and the "Welle 0" worked example. Only once every document is generated does the config get rebalanced against the design principles, so each tuning step costs one command. The milestone ends with a revised session flow, legacy files retired, and a timed dry run by someone who did not write the rules. Order principle: *rule definitions* before templates, *numeric values* after the generator exists.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Simulation Foundation** - Reproducible env, characterization tests, shared `planspiel/` rules module, exact arithmetic, streaming enumeration incl. over-budget plans, config validator (completed 2026-10-01)
- [x] **Phase 2: Rule Changes** - Settle Levelwechsel/Maßnahmentausch, downgrade, linear overspend penalty + gate, Sparprogramm window, RoS ledger, Budget Review boundaries, E-target mechanic (TDD) (completed 2026-10-05)
- [x] **Phase 3: Content Source & Veiling** - All German prose in one content source keyed by config id, veiled vs revealed attack texts, clue matrix (completed 2026-10-19)
- [x] **Phase 4: Print Pipeline & Attack Worksheets** - Non-interactive, reproducible LaTeX → PDF build; generated Angriff 1–3 worksheets proven equal to the simulation (completed 2026-10-22)
- [x] **Phase 5: Player & Facilitator Print Material** - Measure/event/Budget Review cards, budget + RoS sheets, tracking sheet, "So funktioniert eine Welle", Welle 0, facilitator master sheet, veiling scan (completed 2026-10-26)
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

**Plans**: 7/7 plans complete

Plans:

- [x] 01-01-PLAN.md — FOUND-01: uv environment, lockfile, `planspiel` package skeleton (Wave 1)
- [x] 01-02-PLAN.md — FOUND-04: UTF-8 everywhere, real umlauts in config (Wave 2)
- [x] 01-03-PLAN.md — FOUND-02: golden characterization tests + full per-tier digests (Wave 3)
- [x] 01-04-PLAN.md — FOUND-03: every formula once in `planspiel/`, root scripts as thin wrappers (Wave 4)
- [x] 01-05-PLAN.md — FOUND-07: config validator (errors + hand-calculability warnings) (Wave 5)
- [x] 01-06-PLAN.md — FOUND-05: exact arithmetic + paper rounding/step helper (Wave 6)
- [x] 01-07-PLAN.md — FOUND-06: bounded full enumeration incl. over-budget, compact report (Wave 7)

### Phase 2: Rule Changes

**Goal**: Every rule participants stumbled over at MHP is defined unambiguously, implemented test-first in the shared rules module and documented in README. Templates can then be written against a settled rule set. Numeric values (X, slopes, weights) stay provisional until Phase 6.
**Depends on**: Phase 1
**Requirements**: RULE-01, RULE-02, RULE-03, RULE-04, RULE-05, RULE-06, RULE-07, RULE-08
**Success Criteria** (what must be TRUE):

  1. README and config distinguish "Levelwechsel" (same measure, other level) from "Maßnahmentausch" (swap one measure for another; replaces the MHP term "Maßnahmenwechsel"), and the Kurswechsel event names exactly which move it allows. The simulation models change-window moves, including a downgrade that keeps initial costs sunk and lowers OPEX from the next wave.
  2. A plan over budget loses X KZ per started 10.000 € (X read from config, penalty lookup table derivable for print). A team pushed over budget by an event such as Sparprogramm is penalized only if it is still over budget after the change window.
  3. The overspend gate runs per tier in the test suite and compares every over-budget plan with its own trimmed in-budget version. It reports the minimum X required under current values and fails, naming the offending plan, when X in config is set too low.
  4. RoS for any selection is identical with and without event cost effects (penalties and discounts); only initial costs, regular OPEX and the Kurswechsel init difference count. Budget Review tiers give the same result in sim and print at the 25k/50k/75k boundaries, with boundary text derived from the tier list.
  5. The per-wave E-target KZ bonus/malus is resolved against the printed MHP material and the decision is logged in PROJECT.md. It is either removed from the simulation or registered as a mechanic the worksheets must print.

**Plans**: 8/8 plans complete

Plans:
**Wave 1**

- [x] 02-01-PLAN.md — RULE-08: remove the unprinted E-target bonus/malus; golden diff tool; reviewed snapshot change (Wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 02-02-PLAN.md — RULE-06: RoS from own security spend only; two-total budget ledger (Wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 02-03-PLAN.md — RULE-03: linear overspend penalty −X per started 10.000 € (X = 9 provisional), store columns, lookup rows (Wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 02-04-PLAN.md — RULE-07: Budget Review boundaries "ab" with text generated from the tier list (Wave 4)

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 02-05-PLAN.md — RULE-01: Levelwechsel/Maßnahmentausch vocabulary, Kurswechsel as forced swap with tested swap rules, reference-plan labels (Wave 5)

**Wave 6** *(blocked on Wave 5 completion)*

- [x] 02-06-PLAN.md — RULE-02: change-window moves, exact path evaluator, swap layer as legal minimum (Wave 6)

**Wave 7** *(blocked on Wave 6 completion)*

- [x] 02-07-PLAN.md — RULE-05: event-induced overrun penalised only if still over after the window (Wave 7)

**Wave 8** *(blocked on Wave 7 completion)*

- [x] 02-08-PLAN.md — RULE-04: per-tier trim-back overspend gate, `planspiel gate`, Phase-6 X input (Wave 8)

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

**Plans**: 3/3 plans complete

Plans:
**Wave 1**

- [x] 03-01-PLAN.md — PRINT-02: `content/texte.toml` + `planspiel texts` (coverage, digit lint), prose stripped from config with reviewed text-only golden change, assets folder and inventory (SC1, SC2, SC5) (Wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 03-02-PLAN.md — VEIL-01: veiled title "Angriff N" vs revealed texts, audience views with leak test, giveaway lint on veiled keys and events, revealed-text review (SC3) (Wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 03-03-PLAN.md — VEIL-03: veiled story documents, `content/clues.toml` + `planspiel clues` (≥ 2 clues from ≥ 2 documents per attack), rewrite and matrix review (SC4) (Wave 3)

### Phase 4: Print Pipeline & Attack Worksheets

**Goal**: The Angriff 1–3 worksheets carry the highest print-sync risk because facilitators calculate from them by hand. They are generated from config through a proven, non-interactive LaTeX pipeline and provably compute the same results as the simulation.
**Depends on**: Phase 2, Phase 3
**Requirements**: PRINT-01, PRINT-03, PRINT-04, PRINT-11
**Success Criteria** (what must be TRUE):

  1. One command rebuilds the attack worksheets as PDFs from `simulation_config.json` without any interactive MiKTeX prompt (a missing package fails fast instead of hanging). Two builds from identical inputs produce byte-identical PDFs.
  2. The generated Angriff 1–3 worksheets show thresholds, caps, bonus tables and the case 1/2/3 calculation steps, all derived from config. Changing a threshold in config and rebuilding changes the printed number with no template edit.
  3. An equivalence test replays the printed hand-calculation steps over a dense input grid and matches the simulation for every input. The test fails if the simulation applies a mechanic the worksheet does not print.
  4. Every generated page carries a version stamp (config hash and date) in its footer.

**Plans**: 6/6 plans complete
**Research flag**: yes. Topics: non-interactive MiKTeX build (update 23.10 → current, `--disable-installer`, subprocess timeout) as the first-plan smoke gate, then worksheet/card layout (tcolorbox raster, print scaling, cut lines). Spike-compile only, no full card sheet.

Plans:
**Wave 1**

- [x] 04-01-PLAN.md — PRINT-01: non-interactive TeX smoke gate: bounded driver, `kpsewhich --miktex-disable-installer` preflight, aux-stable pass loop, shared `planspiel.sty` (byte-identical PDFs), `pdf` marker; user checkpoint for the MiKTeX update and colortbl/tikzfill (SC1 mechanism) (Wave 1)
- [x] 04-02-PLAN.md — PRINT-03: worksheet print model: `rules.worksheet_constants`, German print formatting, `[sheets.angriff]` wording, `AttackSheet` with the D-06/D-08/D-09 guards (Wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 04-03-PLAN.md — PRINT-01: Jinja render stage and `uv run planspiel print` (preflight → render → build → publish); supply-chain checkpoint for jinja2/pypdf; whole-set byte-identity test (SC1) (Wave 2)
- [x] 04-04-PLAN.md — PRINT-04: independent replay of the printed steps vs the simulation over the D-12 grid, `apply_attack` key guard, negative controls, two-decimal brute force, slow replay of every plan (SC3) (Wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 04-05-PLAN.md — PRINT-11: content-hash version stamp on every page, UTC input commit date, scoped "+lokal", manifest and `planspiel print --check` (SC4) (Wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 04-06-PLAN.md — PRINT-03: worksheet template and layout macros, two-page A4 sheets, fragment and layout PDF tests, first stamped build committed in the D-19 order (SC2) (Wave 4)

### Phase 5: Player & Facilitator Print Material

**Goal**: Every remaining card and sheet that players and facilitators use is generated from config and explains the mechanics. Nothing a player sees before a wave gives away the attack.
**Depends on**: Phase 4
**Requirements**: PRINT-05, PRINT-06, PRINT-07, PRINT-08, PRINT-09, PRINT-10, PRINT-12, VEIL-02, VEIL-04, FLOW-01
**Success Criteria** (what must be TRUE):

  1. The same one command generates measure cards (10 measures × 3 levels, CIA values, costs and dependencies only, with a "how to read this card" legend), event cards and the Budget Review card with effect lines derived from event type and parameters, plus the budget and RoS sheets.
  2. A team can run a wave on the printed tracking sheet in calculation order, with separate rows for own costs and external effects, guided by the one-page "So funktioniert eine Welle" and without a whiteboard write-up.
  3. The worked example "Welle 0" (fictional practice incident, deliberately mediocre selection) is generated from the rules module. A golden test fails if its printed numbers diverge from the simulation.
  4. The facilitator master sheet lists per-wave thresholds, caps, bonus tables, event effects, check rows and answer keys for reference selections, all matching the simulation.
  5. An automated scan of all pre-wave material (text, file names, PDF metadata) finds no attack names and no wave CIA weights. Measure→attack bonus links and wave weights appear only on the revealed attack worksheets.
  6. The story documents (Unternehmenssteckbrief, Zeitungsartikel, Anfrage-Mail, Audit-Mail) are generated by the same command from the `[story.*]` content, and every clue quote in `content/clues.toml` appears in the rendered PDF.

**Plans**: 16/16 plans complete

Plans:
**Wave 1**

- [x] 05-01-PLAN.md — VEIL-02: audience registry by job prefix, two-layer veil scan (rendered .tex as `print.veil` build gate, built PDFs incl. metadata and file names), pre-wave AST guard (Wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 05-02-PLAN.md — PRINT-05 (1/2): measure deck model (legend + 30 level cards), `rules.card_facts`/`level_requirements`, card template and macros, registration in the print set (Wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 05-03-PLAN.md — PRINT-05 (2/2): deck laid out on A4 card sheets (fit, stamp per sheet), log hygiene for every job; physical print checkpoint (Wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 05-04-PLAN.md — VEIL-04: pinned measure-card shape, legend reveal note, proof that weights and bonus links appear only on the revealed worksheets (Wave 4)

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 05-05-PLAN.md — PRINT-06: event cards and Budget Review card, effect lines from type and parameters proven equal to the simulation (`eventtext.py`, `review_text.tier_rows`) (Wave 5)

**Wave 6** *(blocked on Wave 5 completion)*

- [x] 05-06-PLAN.md — PRINT-07: team booklet with budget/planning and RoS/Budget Review pages; printed formulas replay `evaluate_path`; overspend table size guard pinned for Phase 6 review (Wave 6)

**Wave 7** *(blocked on Wave 6 completion)*

- [x] 05-07-PLAN.md — PRINT-08: one-page tracking sheet in calculation order (own costs vs external effects, change-window grid, Kurswechsel credit), `KZ_MIN`/`KZ_MAX`, replay against `evaluate_path` (Wave 7)

**Wave 8** *(blocked on Wave 7 completion)*

- [x] 05-08-PLAN.md — PRINT-09: one-page "So funktioniert eine Welle" with TikZ flow, attacks vs events, Backup & Recovery table (Wave 8)

**Wave 9** *(blocked on Wave 8 completion)*

- [x] 05-09-PLAN.md — PRINT-12 (1/2): hashed, fixed-name image asset path through build, stamp and CLI (Wave 9)

**Wave 10** *(blocked on Wave 9 completion)*

- [x] 05-10-PLAN.md — PRINT-12 (2/2): four story documents from `[story.*]`, every clue quote in the PDF (Wave 10)

**Wave 11** *(blocked on Wave 10 completion)*

- [x] 05-11-PLAN.md — FLOW-01 (1/2): `rules.path_trace`, practice block in config with validator and guards, proven invisible to waves 1-3 (Wave 11)

**Wave 12** *(blocked on Wave 11 completion)*

- [x] 05-12-PLAN.md — FLOW-01 (2/2): practice story review checkpoint, Welle 0 worked example in the worksheet layout, golden test (Wave 12)

**Wave 13** *(blocked on Wave 12 completion)*

- [x] 05-13-PLAN.md — PRINT-10 (1/4): final-index weights into config (D-23), every caller reads them, outputs unchanged (Wave 13)

**Wave 14** *(blocked on Wave 13 completion)*

- [x] 05-14-PLAN.md — PRINT-10 (2/4): reference paths (`planspiel referenzpfade`, `fmt.format_approx`), approval checkpoint, approved paths pinned in config (Wave 14)

**Wave 15** *(blocked on Wave 14 completion)*

- [x] 05-15-PLAN.md — PRINT-10 (3/4): facilitator master sheet with parameters, check rows, event schedule, answer keys and clue matrix; clues as a stamped print input (Wave 15)

**Wave 16** *(blocked on Wave 15 completion)*

- [x] 05-16-PLAN.md — PRINT-10 (4/4): final regeneration of the print set in the D-19 order, Phase 6 follow-ups, veiling todo closed (Wave 16)

### Phase 6: Rebalance

**Goal**: The config is tuned so the design principles hold under full enumeration: overspending never pays, every choice matters, good play wins, mediocre play still ends positive, and tiers stay comparable. All print material reflects the final numbers.
**Depends on**: Phase 5
**Requirements**: BAL-01, BAL-02, BAL-03, BAL-04, BAL-05, BAL-06, BAL-07, BAL-08, BAL-09
**Success Criteria** (what must be TRUE):

  1. X is calibrated per tier on the trim-back criterion (raw and capped KZ) and the overspend gate passes with it. If the required X was still impractical after softening, the user chose between accepting the higher X and softening further from presented numbers (capping is excluded, D-22), and the gate passes under that choice.
  2. The validator runs with hand-calculability checks as errors and passes: every worksheet slope and constant is hand-friendly, and no 17/7-type slope remains.
  3. The per-tier balance report runs without the 0.85 utilization filter and shows top-K, Pareto points and unfiltered optima. Final-Index weights are rescaled from measured data so RoS·100 no longer dominates KZ.
  4. Design-principle checks pass per tier under full enumeration. No measure/level is strictly dominated or near-mandatory, and every decision point shifts outcomes. Good reference strategies rank in the top quartile and bad in-budget ones in the bottom quartile; an overspending one is judged by the gate (D-23). A mediocre strategy ends above start KZ, a comeback after wave 1 is possible, and best results and spread stay comparable across tiers.
  5. All print material is regenerated from the rebalanced config with one command, and the print≡sim equivalence and Welle-0 golden tests pass on the new values.

**Carried over from Phase 5:**

- Re-choose the reference paths with `uv run planspiel referenzpfade` after the rebalance and re-pin `tests/golden/answer_keys.json` (D-18, D-22).
- Rescale the `final_index` weights in `simulation_config.json` and drop the `vorläufig` label on the master sheet (D-23, BAL-03).
- Re-run `practice.check_example` and re-pin `tests/golden/welle0.json` and `tests/golden/worksheet_tex.json` (BAL-05).
- Review `booklet.MAX_PENALTY_ROWS` (12 today: X = 9 KZ je angefangene 10.000 €, ⌈100 ÷ 9⌉ rows) against the calibrated X and raise it together with a new RoS-page layout proof if X falls below 9 (a smaller X adds rows and stops the build with `ERROR print.model`). Review `booklet.MAX_WINDOWS` (2 today, about 2 mm to spare on the tracking page) the same way: a third change window or a fourth wave needs a new layout proof.
- Remove the `≈` approximations on the master sheet once no slope is non-terminating (BAL-02).

**Plans**: 5/10 plans executed

Plans:
**Wave 1**

- [x] 06-01-PLAN.md — BAL-01: move-path overspend gate (swap / window-1 / window-2, start-lowered trim, narrow diagnostic), raw and capped minimum X, calibration X = max + 1, shared candidate-config test infrastructure (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 06-02-PLAN.md — BAL-02: hand-calc severity parameter (errors on request), final-index weight rule, candidate hand-calc check (wave 2)
- [x] 06-03-PLAN.md — BAL-03: Final-Index as KZ + k · RoS (two-decimal RoS), k measurement from pooled IQR, 0.85 filter removed; code and tests only, the moved answer-key row is a tuning target until 06-10 (wave 2)
- [x] 06-04-PLAN.md — BAL-06: dominance, near-mandatory band, overpowered drop, decision-point effects (wave 2)
- [x] 06-05-PLAN.md — BAL-08: median above start on both layers, comeback after wave 1 (wave 2)
- [ ] 06-06-PLAN.md — BAL-09: tier corridor, D-11 band, spread range (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 06-07-PLAN.md — BAL-07: clue → measure mapping and checks (console matrix), reference_strategies key, quartile placement, clue-derived good strategy (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 06-08-PLAN.md — BAL-04: in-budget top-K / Pareto / unfiltered optima and the consolidated balance report with baseline comparison (wave 4)

**Wave 5** *(blocked on Wave 4 completion)*

- [ ] 06-09-PLAN.md — Tuning (BAL-01/02/03/06/07/08/09 targets, X and k) on a candidate config/content, ending at the D-04 checkpoint (wave 5, checkpoint)

**Wave 6** *(blocked on Wave 5 completion)*

- [ ] 06-10-PLAN.md — BAL-05: pre-flight D-04 gate, adopt the approved candidate, flip defaults, final-index wording/weight row and booklet clue column, single re-pin of goldens, regenerate the print set (wave 6)

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
| 1. Simulation Foundation | 7/7 | Complete    | 2026-10-01 |
| 2. Rule Changes | 8/8 | Complete    | 2026-10-05 |
| 3. Content Source & Veiling | 3/3 | Complete    | 2026-10-19 |
| 4. Print Pipeline & Attack Worksheets | 6/6 | Complete    | 2026-10-22 |
| 5. Player & Facilitator Print Material | 16/16 | Complete    | 2026-10-26 |
| 6. Rebalance | 5/10 | In Progress|  |
| 7. Session Flow & Handoff | 0/TBD | Not started | - |
