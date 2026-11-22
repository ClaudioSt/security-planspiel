# Requirements: CIA-Planspiel Automotive — Post-Workshop Refinement

**Defined:** 2026-09-29
**Core Value:** Facilitators and players can run the game by hand without ambiguity: every rule is unambiguous, every printed number matches `simulation_config.json`, and no strategy exploits a rule loophole.

## v1 Requirements

### Foundation (FOUND)

- [x] **FOUND-01**: Maintainer can set up the environment with one command (uv-managed venv, `pyproject.toml` + `uv.lock`); all scripts run via `uv run`, independent of the Inkscape `python` on PATH
- [x] **FOUND-02**: Characterization tests pin current simulation outputs (KZ, damage, costs, RoS per selection and tier) before any refactoring
- [x] **FOUND-03**: Every game formula exists exactly once in a shared `planspiel/` package used by simulation, balance analysis and print generation; root scripts remain as thin wrappers so documented commands keep working
- [x] **FOUND-04**: Config is read as UTF-8 everywhere, and all German display strings in config use real umlauts/ß instead of transliterations
- [x] **FOUND-05**: Calculations use exact (integer/fraction) arithmetic and one tested rounding/step helper that matches how facilitators round on paper
- [x] **FOUND-06**: Full enumeration including over-budget combinations runs per tier within measured memory and runtime bounds, using compact per-combination aggregates (top-K, percentiles, best in- vs over-budget, Pareto count); full dump only on request
- [x] **FOUND-07**: A config validator rejects broken references and flags hand-calculability violations (non-linear or awkward slopes, printed invariants such as `base_severity == mitigation_cap`)

### Rules (RULE)

- [x] **RULE-01**: "Levelwechsel" (same measure, different level) and "Maßnahmentausch" (swap one measure for another; replaces the MHP term "Maßnahmenwechsel") are defined unambiguously, and the Kurswechsel event names exactly which move it allows
- [x] **RULE-02**: Teams may downgrade a measure's level in the change window; initial costs are not refunded, OPEX drops from the next wave; the simulation models this move
- [x] **RULE-03**: Going over budget costs −X KZ per started 10.000 € over budget (linear, printable as lookup table); X is a config parameter
- [x] **RULE-04**: An automated gate proves overspending is never profitable under the trim-back criterion: every over-budget plan loses to its own trimmed-into-budget version, per tier
- [x] **RULE-05**: If an event (e.g. Sparprogramm) pushes a team over budget, the team gets the change window to return within budget; the penalty applies only if it is still over afterwards
- [x] **RULE-06**: RoS counts only the team's own security spend (initial costs, regular OPEX, Kurswechsel init difference); event cost effects are excluded in both directions (penalties and discounts)
- [x] **RULE-07**: Budget Review tier boundaries are identical in print and simulation (no off-by-one at 25k/50k/75k)
- [x] **RULE-08**: The per-wave E-target KZ bonus/malus is checked against what the printed MHP material actually used, then either printed on the worksheets or removed from the simulation — sim and paper agree afterwards

### Veiling (VEIL)

- [x] **VEIL-01**: Config/content hold separate veiled (pre-attack) and revealed (at-wave) texts per attack
- [x] **VEIL-02**: Material players see before a wave (company profile, newspaper article, measure cards, planning sheets, file names, PDF metadata) contains no attack names and no wave CIA weights — verified by an automated scan
- [x] **VEIL-03**: A facilitator clue matrix shows every attack is inferable from at least two clues in the pre-wave material
- [x] **VEIL-04**: Measure cards show CIA values, costs and dependencies only; the measure→attack bonus link and wave weights appear on the attack worksheet when the wave is revealed

### Print Material (PRINT)

- [x] **PRINT-01**: One command rebuilds all print material from `simulation_config.json` via LaTeX → PDF, non-interactively (no MiKTeX install prompts) and reproducibly (identical inputs → identical PDFs)
- [x] **PRINT-02**: All German prose lives in one content source keyed by config id; printed numbers are never typed into prose
- [x] **PRINT-03**: Attack worksheets (Angriff 1–3) are generated, including thresholds, caps, bonus tables and case 1/2/3 calculation steps
- [x] **PRINT-04**: An equivalence test proves the printed hand-calculation steps give the same results as the simulation over a dense input grid
- [x] **PRINT-05**: Measure cards (10 measures × 3 levels) are generated with a legend explaining how to read a card and how a measure affects CIA and the E-value
- [x] **PRINT-06**: Event cards and the Budget Review card are generated, with effect lines derived from event type and parameters
- [x] **PRINT-07**: Budget sheet and RoS sheet are generated
- [x] **PRINT-08**: A printed team tracking sheet in calculation order (incl. separate rows for own costs vs external effects) replaces the whiteboard write-up
- [x] **PRINT-09**: A one-page "So funktioniert eine Welle" explains the wave calculation and what attacks and events affect
- [x] **PRINT-10**: A facilitator master sheet lists per-wave thresholds, caps, bonus tables, event effects, check rows and answer keys for reference selections
- [x] **PRINT-11**: Every generated page carries a version stamp (config hash/date)
- [x] **PRINT-12**: The pre-wave story documents (Unternehmenssteckbrief, Zeitungsartikel, Anfrage-Mail, Audit-Mail) are generated from the content source via LaTeX; their veiled prose and clues live in `content/texte.toml` (added 2026-10-06, Phase 3 D-14)

### Session Flow (FLOW)

- [x] **FLOW-01**: A worked example "Welle 0" (fictional practice incident, generated from the rules module and golden-tested) is run before wave 1
- [x] **FLOW-02**: The session schedule is revised: whiteboard step removed, wave 1 fits 20 min, a 15–20 min debrief slot is included, total still one afternoon
- [x] **FLOW-03**: A debrief question set (reaction → description → analysis → application) is part of the facilitator material
- [x] **FLOW-04**: A "Was ist neu" sheet summarizes rule changes for facilitators who ran the MHP version
- [ ] **FLOW-05**: A timed dry run by someone who did not write the rules confirms the material is self-explanatory and waves fit the schedule

### Balance (BAL)

- [x] **BAL-01**: X is calibrated per tier on the trim-back criterion (raw and capped KZ); if the required X is still impractical after softening the step rewards, accepting the higher X or softening further is presented to the user as a decision with measured numbers (capping overspend is excluded: Phase 2 D-18, Phase 6 D-22)
- [x] **BAL-02**: All worksheet slopes and constants are hand-friendly (e.g. no 17/7 in wave 3); validator warnings become errors
- [x] **BAL-03**: The 0.85 utilization filter is dropped from the balance workflow and Final-Index weights are rescaled using measured data
- [x] **BAL-04**: Balance reports show top-K, Pareto and unfiltered optima per tier, not only averages
- [x] **BAL-05**: All print material is regenerated from the rebalanced config
- [x] **BAL-06**: Every choice matters — no measure or level is strictly dominated or near-mandatory (appears in almost all top strategies), and each decision point (budget tier, measure/level selection, change window, Kurswechsel) measurably shifts outcomes; verified by full enumeration per tier
- [x] **BAL-07**: Good strategies lead to good outcomes — defined reference strategies (good: reacts to discovery clues, balanced CIA; bad: ignores clues, all-in on one dimension, overspends, hoards budget) rank in the top resp. bottom quartile of their tier; an over-budget strategy is judged by the overspend gate instead (Phase 6 D-23)
- [x] **BAL-08**: The game is rewarding overall — a sensible but mediocre strategy still ends positive (e.g. final KZ above start KZ), and no team is effectively eliminated after wave 1 (comeback possible via change window)
- [x] **BAL-09**: Outcomes stay controlled — the best achievable result is comparable across budget tiers and the outcome spread per tier stays within a defined range

### Legacy (LEG)

- [x] **LEG-01**: Legacy hand-maintained docx/pptx worksheets/cards, old pptx generators, `pptx_output/` and the Excel attack calculator are moved to `archive/`
- [x] **LEG-02**: README.md and CLAUDE.md describe the new pipeline and rules (print-sync section rewritten); manually maintained documents (intro deck, Audit-Mail, company profile) are checked for outdated rules

### Risk-Based Learning Chain (RISK)

Added 2026-11-12 for the inserted Phase 07.1 (pedagogical review): make the chain company profile → risk (CIA, likelihood, business impact) → measure → budget explicit for teams. Texts, templates and schedule only; no game formula or balance value changes.

- [x] **RISK-01**: The € impact bands (low, medium, high) of the risk matrix live in a new `simulation_config.json` block; the validator rejects bands that are not ascending or that overlap, and the limits agree with the game's unprotected attack damage
- [x] **RISK-02**: The Teamheft opens with a risk register page: five risks R1–R5 with asset, threat or weakness plus source document, protection goal C/I/A, business-impact category plus one sentence, rank 1–5, treat/accept plus one line of reasoning and a Rückblick column; a 3×3 likelihood × impact matrix with colour zones and the config € bands on the impact axis; a short instruction and one filled-in example from another industry; the page passes the veil, digit and fill checks
- [x] **RISK-03**: The planning table on the Teamheft planning page has a "gegen R#" column for one or more register risks per measure, marked as a recommendation (no penalty, no rule change, no facilitator check)
- [x] **RISK-04**: Every attack worksheet ends with one reality-check line asking which register risk the attack hit (R# or "nicht im Register"); the worksheet keeps its page count and passes the veil checks
- [x] **RISK-05**: The facilitator booklet has a business-impact cheat sheet of 6–8 business cases phrased as consequences, never as attacks, each with an answer and a band from config; the facilitator answers team questions in the role of MechTech's management with a € order of magnitude that agrees with the game's damage values
- [x] **RISK-06**: The Teamheft RoS page explains RoS in one sentence as net damage avoided per invested euro (avoided damage minus own cost, per euro of own cost); the formula and the printed calculation stay unchanged
- [x] **RISK-07**: The debriefing is rebuilt around the chain: questions per stage on register vs. reality, accepted risks that hit, the team's C/I/A assessment vs. the wave weightings, which risks the money paid off against (RoS, net framing) and transfer to real risk management, plus an optional 60-second management pitch per team without planned minutes
- [x] **RISK-08**: The session schedule gives the story block 35 and the debriefing 30 minutes (stages 3/5/14/8), 215 minutes in total; the Teamheft is handed out in the story block, the closing block directs the Rückblick, and the print list, the dry-run protocol and the dry-run record follow
- [x] **RISK-09**: The intro deck has a new "Risiko-Matrix" slide (likelihood × impact, zones, how the register is used; no MechTech or attack content) and its minute figures follow the new schedule; the deck is edited once from a user-approved checklist and pinned by the deck test
- [x] **RISK-10**: The print set is rebuilt and released as release candidate 3: clean stamp, `print --check` exit 0, fast and pdf test suites pass, printed and approved by the user before the dry run on 2026-11-25

### Protection-Need Analysis (PROT)

Added 2026-11-22 for the inserted Phase 07.2: a per-asset protection-need analysis (C/I/A in the existing € bands, maximum principle) replaces the likelihood × impact matrix of RISK-02. Print material, texts, config structure and deck only; no game formula or balance value changes.

- [x] **PROT-01**: The `risk_matrix` config block carries the number of asset rows and a protection goal (c/i/a) per cheat-sheet case; the validator rejects a missing or unknown goal and, for a case anchored to an attack, a goal that is not one of that attack's strongest `cia_impact` goals; matrix-only code (zones, likelihood) is removed
- [x] **PROT-02**: The Teamheft register page opens with a protection-need table (empty asset rows W1–W4, per row C/I/A each gering/mittel/hoch with the config € ranges, a "gesamt" column by the maximum principle, an example row from another industry) instead of the 3×3 matrix; register risks reference an asset W# and a main goal, the Rückblick reads the risk's band from the table; the page stays one page and passes the veil, digit and fill checks
- [x] **PROT-03**: The facilitator cheat sheet prints each case's protection goal; C, I and A each have at least one case, 6–8 cases in total, bands consistent with the game values
- [x] **PROT-04**: README, "Was ist neu", the debriefing questions and the booklet direction texts describe the protection-need table; no player or facilitator text names the risk matrix, a likelihood or the colour zones
- [ ] **PROT-05**: Intro deck slide 32 explains the protection-need analysis (assets × C/I/A, gering/mittel/hoch, maximum principle, register reads its band from the table; no MechTech or attack content); edited once from a user-approved checklist and pinned by the deck test
- [ ] **PROT-06**: The print set is rebuilt and released as release candidate 4: clean stamp, `print --check` exit 0, fast and pdf suites pass, only `risk_matrix` differs in the config, the dry-run material record names RC4, printed and approved by the user before the dry run on 2026-11-25

## v2 Requirements

Deferred to a future release. Tracked but not in the current roadmap.

- **DEBR-01**: "Perfekte Strategie" debrief sheet generated from the full enumeration, showing each team's percentile
- **DEBR-02**: 2–3 min impulse debrief after each wave
- **DEBR-03**: "Controller:in" scribe role per team
- **DEBR-04**: One-page participant feedback form

## v3 Requirements

Later milestone. Scope to be refined when v3 starts; v1 architecture (single `planspiel/` rules module, content source, config) should not block it.

- **WEB-01**: Digital web app version of the game, built on the same `planspiel/` rules module and `simulation_config.json` (exact scope — facilitator companion vs. fully digital play — decided at v3 start)

## v4 Requirements

### Scenario Variants (SCEN) — replayability

Randomness in the *scenario*, never in the *outcome*: deterministic within a session, variable between sessions.

- **SCEN-01**: Multiple scenarios (varying attack types/order, events, wave weights) exist in config; one is drawn per session and applies to all teams equally
- **SCEN-02**: Each scenario is individually balanced by full enumeration and meets BAL-06…BAL-09
- **SCEN-03**: No single fixed strategy is top-ranked in all scenarios — reading the clues and adapting is rewarded
- **SCEN-04**: Print material is generated per scenario; players cannot tell the scenario in advance, so veiling works on repeat play

## Out of Scope

| Feature | Reason |
|---------|--------|
| Typst renderer | LaTeX chosen 2026-09-29 (known tool, mature) |
| Refunds on downgrade | Reference-game norm; keeps sunk-cost lesson |
| Digital/online game in v1/v2 | v1/v2 stay paper-based; web app planned as v3 (WEB-01) |
| Dice / randomness in outcomes | Breaks team comparability and "good strategy → good outcome"; variability comes from scenario draw instead (SCEN, v4) |
| Non-linear worksheet formulas | Facilitators must calculate by hand |
| Loan/interest mechanics, flat penalty bands | Replaced by linear overspend penalty |
| Live leaderboard after every wave | Distracts from learning goals |
| Regenerating the MHP-branded intro deck | Stays manually maintained; only content checked (LEG-02) |
| Updating `archive/historical_docs/` | Superseded, reference only |
| Purging old sim JSONs from git history | Needs force-push to main |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1 | Complete |
| FOUND-02 | Phase 1 | Complete |
| FOUND-03 | Phase 1 | Complete |
| FOUND-04 | Phase 1 | Complete |
| FOUND-05 | Phase 1 | Complete |
| FOUND-06 | Phase 1 | Complete |
| FOUND-07 | Phase 1 | Complete |
| RULE-01 | Phase 2 | Complete |
| RULE-02 | Phase 2 | Complete |
| RULE-03 | Phase 2 | Complete |
| RULE-04 | Phase 2 | Complete |
| RULE-05 | Phase 2 | Complete |
| RULE-06 | Phase 2 | Complete |
| RULE-07 | Phase 2 | Complete |
| RULE-08 | Phase 2 | Complete |
| VEIL-01 | Phase 3 | Complete |
| VEIL-02 | Phase 5 | Complete |
| VEIL-03 | Phase 3 | Complete |
| VEIL-04 | Phase 5 | Complete |
| PRINT-01 | Phase 4 | Complete |
| PRINT-02 | Phase 3 | Complete |
| PRINT-03 | Phase 4 | Complete |
| PRINT-04 | Phase 4 | Complete |
| PRINT-05 | Phase 5 | Complete |
| PRINT-06 | Phase 5 | Complete |
| PRINT-07 | Phase 5 | Complete |
| PRINT-08 | Phase 5 | Complete |
| PRINT-09 | Phase 5 | Complete |
| PRINT-10 | Phase 5 | Complete |
| PRINT-11 | Phase 4 | Complete |
| PRINT-12 | Phase 5 | Complete |
| FLOW-01 | Phase 5 | Complete |
| FLOW-02 | Phase 7 | Complete |
| FLOW-03 | Phase 7 | Complete |
| FLOW-04 | Phase 7 | Complete |
| FLOW-05 | Phase 7 | Pending |
| BAL-01 | Phase 6 | Complete |
| BAL-02 | Phase 6 | Complete |
| BAL-03 | Phase 6 | Complete |
| BAL-04 | Phase 6 | Complete |
| BAL-05 | Phase 6 | Complete |
| BAL-06 | Phase 6 | Complete |
| BAL-07 | Phase 6 | Complete |
| BAL-08 | Phase 6 | Complete |
| BAL-09 | Phase 6 | Complete |
| LEG-01 | Phase 7 | Complete |
| LEG-02 | Phase 7 | Complete |
| RISK-01 | Phase 07.1 | Complete |
| RISK-02 | Phase 07.1 | Complete |
| RISK-03 | Phase 07.1 | Complete |
| RISK-04 | Phase 07.1 | Complete |
| RISK-05 | Phase 07.1 | Complete |
| RISK-06 | Phase 07.1 | Complete |
| RISK-07 | Phase 07.1 | Complete |
| RISK-08 | Phase 07.1 | Complete |
| RISK-09 | Phase 07.1 | Complete |
| RISK-10 | Phase 07.1 | Complete (paper approval moved to PROT-06) |
| PROT-01 | Phase 07.2 | Complete |
| PROT-02 | Phase 07.2 | Complete |
| PROT-03 | Phase 07.2 | Complete |
| PROT-04 | Phase 07.2 | Complete |
| PROT-05 | Phase 07.2 | Pending |
| PROT-06 | Phase 07.2 | Pending |

**Coverage:**

- v1 requirements: 63 total
- Mapped to phases: 63
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-29*
*Last updated: 2026-11-22 — PROT-01..PROT-06 added for Phase 07.2 (protection-need analysis)*
