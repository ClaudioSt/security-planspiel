# CIA-Planspiel Automotive — Post-Workshop Refinement

## What This Is

An offline, paper/whiteboard IT-security business game ("CIA-Planspiel Automotive") for student teams (3 teams × 5 people, one afternoon, ~3h). Teams act as consultants for the fictional automotive supplier MechTech: they negotiate a budget, pick security measures at levels L1–L3, and face deterministic events and three attack waves, optimizing customer satisfaction (KZ), CIA goal fulfilment and Return on Security (RoS). This repo holds the game design, the central parameter config and the Python tooling for simulation, balance checks and print-material generation — not a runtime for playing the game.

This project refines the game after its live run at the MHP workshop (2026-09): fix the rule issues participants hit, make the mechanics understandable, generate all print material from `simulation_config.json`, and rebalance.

## Core Value

Facilitators and players can run the game by hand without ambiguity: every rule is unambiguous, every printed number matches `simulation_config.json`, and no strategy exploits a rule loophole.

## Design Principles

Every balance decision is checked against these (measurable via full enumeration, see BAL-06…09):

1. **Every choice matters** — no dominated or mandatory measure/level; every decision point shifts the outcome.
2. **Good strategy → good outcome, bad strategy → bad outcome** — reference strategies rank where they should.
3. **Rewarding overall** — mediocre play still ends positive; comebacks stay possible after wave 1.
4. **Controlled** — outcomes bounded, tiers comparable, fully deterministic *within* a session.
5. **Variable between sessions (v4)** — randomness only in the scenario draw (same for all teams), never in outcomes, so strategies must adapt and veiling survives repeat play.

## Requirements

### Validated

- ✓ Deterministic resolution: E-value = Team_C·wC + Team_I·wI + Team_A·wA, Gesamtreduktion = E-value + bonus, 3-case resolution with linear KZ interpolation — existing (`simulate_outcomes.py`)
- ✓ All numeric values parametrized in `simulation_config.json` (budget tiers, waves, attacks, measures, events, final events) — existing
- ✓ Full enumeration of valid measure combinations per budget tier (`simulate_outcomes.py --budget-tier …`) — existing
- ✓ Top-N ranking by Final-Index (`analyze_simulation_results.py`) and named-strategy dominance check (`balance_analysis.py`) — existing
- ✓ Per-tier KZ start values (50/42/34) balanced — existing (commit 1cfb2fa)
- ✓ Game is interactive and engaging — validated by MHP workshop feedback ("interaktiv ++"); keep the format
- ✓ Wave calculation is learnable: waves 2 and 3 fit the planned 20 min once teams knew the procedure — MHP workshop
- ✓ Safe-to-change simulation foundation: uv env (`uv sync`), golden characterization tests + full digests, every formula once in `planspiel/` with thin root wrappers, UTF-8 config with real umlauts, exact arithmetic with paper rounding, config validator, bounded full enumeration incl. over-budget plans (FOUND-01..07) — Validated in Phase 1: Simulation Foundation
- ✓ Settled rule set (RULE-01..08): "Levelwechsel" vs "Maßnahmentausch" defined, Kurswechsel forces exactly one swap; change-window moves modelled exactly (downgrade keeps Init sunk, OPEX drops next wave); linear overspend penalty −X per started 10k (X = 9 provisional) with a trim-back overspend gate (min X 9/5/3); event-induced overrun penalized only if still over budget at the end; RoS from own security spend only; Budget Review boundaries generated from the tier list; E-target bonus/malus removed — Validated in Phase 2: Rule Changes
- ✓ Single content source (PRINT-02, VEIL-01, VEIL-03): all German print prose in `content/texte.toml` keyed by config id, prose in config is a validator error; `planspiel texts` checks coverage, digits (reviewed allowlist), story mechanics and giveaway terms; attacks have a veiled title ("Angriff N") and a separate revealed set, read only through `PreAttackView`/`RevealView` (leak-tested); story documents veiled and a 14-clue facilitator matrix (`planspiel clues`, ≥2 clues from ≥2 documents per attack); SC5 inventory of the hand-maintained documents — Validated in Phase 3: Content Source & Veiling (printing the veiled material is Phase 5)
- ✓ Print pipeline and attack worksheets (PRINT-01, PRINT-03, PRINT-04, PRINT-11): `planspiel print` builds the print set from `simulation_config.json` + `content/texte.toml` via Jinja → LuaLaTeX non-interactively (installer disabled, bounded, byte-reproducible; MiKTeX 26.5); Angriff 1–3 worksheets generated into `final_documents/generated/` (two A4 pages each, test print approved); worksheet replay proven equal to the simulation (dense grid 36,467 cases + all 782,336 plans per tier, 0 mismatches); every page carries a content-hash version stamp ("+lokal" for uncommitted or non-default inputs) and `planspiel print --check` detects stale PDFs via manifest.json — Validated in Phase 4: Print Pipeline & Attack Worksheets (remaining print material is Phase 5; legacy Angriff-*.docx retire in Phase 7)

- ✓ Player & facilitator print material (PRINT-05..10, PRINT-12, VEIL-02, VEIL-04): `planspiel print` now builds the complete set of 13 PDFs into `final_documents/generated/` from config + content. It covers measure cards with a legend (A6 landscape, names-only veil profile), event and Budget Review cards with effect lines proven equal to `rules.evaluate_event`, and the team booklet (budget, RoS, Budget Review, tracking page in calculation order). It also includes the one-page "So funktioniert eine Welle", the four story documents with images, the Welle 0 worked example (Fall 3, bonus met/missed, recovery, exact half, clamp) and the facilitator overview with answer keys on user-approved reference paths. A two-layer veil scan (rendered `.tex` + PDF, metadata) gates every pre-wave document. UAT 8/8 passed on physical prints and SECURITY verified with 55 threats closed. Validated in Phase 5: Player & Facilitator Print Material. Answer keys, Welle 0 and the overspend table are pinned to the current values and must be re-chosen after Phase 6.

### Active

- [ ] Rebalanced config verified by full enumeration after the rule changes
- [ ] Flow fits the afternoon: wave 1 no longer overruns. The worked example (Welle 0) and the printed tracking sheet exist since Phase 5. Timing is still unproven until the next live run.

### Out of Scope

- Digital/online version in this milestone — stays paper-based for now; a web app is planned as v3 (WEB-01), built on the same rules module
- Randomness/dice — determinism is a core design principle
- Non-linear formulas on worksheets — facilitators must be able to calculate by hand (hard design criterion)
- Updating the 26 historical docs in `archive/historical_docs/` — superseded, kept for reference only
- Regenerating the MHP-branded intro slide deck (`Planspiel_Einführung + Grundlagen.pptx`) — stays manually maintained; only content updates
- Purging old simulation JSONs from git history — needs force-push to main, not worth it

## Context

**MHP workshop (2026-09) timing** (planned 20 min per wave):

| Time | Phase | Duration |
|---|---|---|
| 14:55 | Intro | 10 min |
| 15:05 | Break | 5 min |
| 15:10 | Introduction + groups | 30 min |
| 15:40 | Measures + budget | 35 min |
| 16:15 | Whiteboard write-up | 15 min |
| 16:30 | Break | 20 min |
| 17:00 | Attack 1 + Event 1 | 34 min |
| 17:34 | Attack 2 + Event 2 | 18 min |
| 17:52 | Attack 3 | — |

**Participant/facilitator feedback (handwritten notes):**
1. "interaktiv ++" — keep interactivity.
2. "Wie funktionieren Maßnahmen → auf Zettel und Folie vermerken → was haben Angriffe und Events für Effekte" — mechanics unclear; explain on cards and slides.
3. "Maßnahmenwechsel ≠ Levelwechsel" — the Kurswechsel event ("genau ein Maßnahmenwechsel") is ambiguous.
4. "Level runterstufen sinnvoll?" — open whether downgrading should be allowed.
5. "Budgetüberschreitung darf nicht eskalieren" — Budget Review gives flat KZ −15 for any negative budget, so heavy overspending buys far more KZ than it costs.
6. "Eventstrafen bei RoS rausnehmen" — event OPEX is currently added to total cost (`simulate_outcomes.py:536`) and distorts RoS.

**Technical state:**
- Phase 2 complete (2026-10-05): `uv run pytest` (551 fast + 19 slow tests); rules settled in `planspiel/rules.py` (`evaluate_path`, swap rules), `planspiel gate` (trim-back overspend gate, passes with X = 9; zero headroom in the low tier → soften step rewards in Phase 6, D-18), `planspiel tausch` (swap layer = legal minimum), generated review/penalty text in `planspiel/review_text.py`. Code review: 6 non-blocking warnings in `02-REVIEW.md`.
- Phase 1 complete (2026-10-01): `uv run pytest` (240 fast + 11 slow tests), rules in `planspiel/rules.py`, `planspiel validate`, default `simulate_outcomes.py --budget-tier <t>` enumerates all 782,336 combinations incl. over-budget (~50 s, ~125 MB per tier). Best over-budget final KZ is 85 vs 100 in budget in every tier; Budget Review boundary at exactly 25k/50k/75k contradicts the printed text (review CR-01 → Phase 2 RULE-07).
- (pre-Phase 1) `simulate_outcomes.py:539` dropped over-budget combinations — now enumerated.
- Manual print-sync trap: `e_threshold`, `mitigation_cap`, bonus values are printed verbatim on `Angriff-{1,2,3}_*.docx` with no generator; measure cards pptx also hand-maintained.
- Existing generators: `generate_pptx_cards.py`, `generate_from_template.py` (pptx), `generate_attack_calculator.py` (xlsx).
- **Interpreter trap:** `python` on PATH is Inkscape's bundled 3.12 without packages → always `uv run` (resolved in Phase 1). MiKTeX 23.10 (pdflatex/lualatex/latexmk) available.
- (pre-Phase 2) Sim ↔ print divergence on the per-wave E-target bonus/malus — resolved in Phase 2 by removing it from the simulation.
- Pending todo: `.planning/todos/pending/2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md`.
- Codebase map: `.planning/codebase/`.

## Constraints

- **Hand-calculability**: all worksheet formulas stay linear and computable by hand — facilitators calculate live on paper
- **Determinism**: same inputs → same outputs within a session; no randomness in outcomes. Scenario draw between sessions is allowed (v4, SCEN) — v1 code must not hard-code "exactly one scenario"
- **Single source of truth**: every number comes from `simulation_config.json`; order of change is config → README → print material
- **Format**: 3 teams × 5, one afternoon (~3h), paper/whiteboard — unchanged
- **Language**: game content/UI German; code, commits bodies, docs English (commit subject per user convention)
- **Timeline**: no fixed next workshop date — refine at own pace
- **Workflow**: TDD for simulation changes; balance verified by full enumeration, not only `balance_analysis.py`

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Overspending allowed, penalized linearly: −X KZ per started 10k over budget | Keeps overspending as a risky option while removing the flat −15 exploit; X calibrated via full enumeration so over-budget never beats best in-budget | ✓ Implemented 2026-10-01 (RULE-03, D-15): provisional X = 9 (D-25), calibrated in Phase 6 |
| Event cost effects removed from RoS | RoS should measure efficiency of the team's own security spend, not external shocks | ✓ Implemented 2026-10-01 (RULE-06, D-21): excluded in both directions (penalties and discounts) |
| Attack names veiled only before the wave, revealed by name when it hits; mechanics always transparent | Players should infer threats from clues, but understand the mechanics fully | ✓ Decided 2026-09-29 |
| Print material generated via LaTeX → PDF from `simulation_config.json` | Eliminates manual print-sync; precise print layout | ✓ Decided 2026-09-29 |
| Generate docs before rebalancing | Every rebalance otherwise requires manual docx edits | ✓ Decided 2026-09-29 |
| Overspend X calibrated on trim-back criterion | Every over-budget plan must lose to its own trimmed version; step rewards make marginal criterion infeasible | ✓ Decided 2026-09-29; gate implemented 2026-10-04 (RULE-04): strict minimum X 9 / 5 / 3 on the static reference, config X = 9 passes; final X in Phase 6 |
| Downgrade allowed: no init refund, OPEX drops next wave | Gives teams an adaptation lever; requires change model in sim | ✓ Decided 2026-09-29; implemented 2026-10-04 (RULE-02: `evaluate_path`, net pricing D-27, swap layer D-24) |
| RoS = own spend only; event effects out in both directions | Symmetric, matches Decisions & Disruptions ledgers | ✓ Decided 2026-09-29 |
| Sparprogramm overrun → re-plan window before penalty | Teams shouldn't be punished for an external shock they can still react to | ✓ Decided 2026-09-29; implemented 2026-10-01 (RULE-05, D-14: single end check, pinned on legal paths) |
| Measure cards CIA only; wave weights hidden until reveal | Weights and attack links would reveal attacks | ✓ Decided 2026-09-29 |
| E-target bonus/malus: check printed MHP material first | Sim applies it, print doesn't show it | ✓ Decided 2026-10-01: removed from the simulation (RULE-08, D-19); no printed MHP material uses it, so sim and paper agree |
| Budget Review boundaries '≥' (ab) with text generated from the tier list | MHP card said 25.001–50.000 while the sim used ≥ 25.000 (CR-01) | ✓ Implemented 2026-10-01 (RULE-07, D-16) |
| Single term 'Maßnahmentausch'; Kurswechsel forces exactly one swap, customer covers Init up to the dropped measure | MHP terms collided and the card promised refunds | ✓ Implemented 2026-10-04 (RULE-01; D-09..D-13, D-22, D-23, D-26, D-28) |
| Keep LaTeX (not Typst) | Known, mature tool | ✓ Decided 2026-09-29 |
| Drop 0.85 utilization filter, rescale Final-Index in rebalance | Filter hides the real optimum; RoS·100 dominates | ✓ Decided 2026-09-29 |
| Excel attack calculator retired | Generated worksheets + facilitator sheet replace it | ✓ Decided 2026-09-29 |
| Design principles 1–5 as measurable balance criteria | "Every choice matters, good→good, rewarding, controlled" must be verifiable | ✓ Decided 2026-09-29 |
| Replayability via scenario draw (v4), not outcome dice; web app v3 | Keeps fairness between teams and hand-calculability | ✓ Decided 2026-09-29 |
| Historical root docs archived in `archive/historical_docs/` | Declutter; they are out of sync with config | ✓ Done (63ffac0) |
| Paper rounding: KZ change per wave rounded once, half away from zero, then clamped 0–100; all else exact | Sim must match what facilitators compute by hand | ✓ Approved 2026-10-01 (commit 0d342f6, 01-EXACT-SWITCH-DIFF.md) |
| Prose lives in content/texte.toml; config holds numbers, ids and short labels; prose in config is a validator error | One edit point for wording; printed numbers come from config, never from typed prose | ✓ Phase 3, D-01/D-02/A3 (03-01, commit e36f24d) |
| Print stamp marks non-default inputs as +lokal instead of rejecting them (WR-07) | Keeps experimental/playtest prints possible while making them recognisable on paper | ✓ User 2026-10-22 (Phase 4 UAT, commit 8514b6a) |
| Job-name prefix (`spieler-`, `uebung-`, `angriff-`, `spielleitung-`) is the single audience classification; unclassified jobs fail the build | One place decides who may see a document; the veil scan profile follows from it | ✓ Phase 5 (05-01) |
| Cards in A6 landscape, 2×2 on A4, 12 pt body; event cards reuse the layout without a caption band | Approved after five physical print rounds; Kurswechsel card fits only without the band | ✓ User 2026-10-23..26 (05-03, 05-05; UAT 2026-10-27) |
| Final-index weights and reference paths live in `simulation_config.json` (Low 2, Medium 1H, High 3) | One source for reports and answer keys; legal paths near the swap-layer median | ✓ User-approved in 05-13/05-14; re-choose after Phase 6 |
| Approximations (`≈`) only on the facilitator booklet | Players never see a rounded non-terminating value; a PDF test enforces it | ✓ Phase 5 (05-15) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-10-27 after Phase 5 (Player & Facilitator Print Material)*
