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
- ✓ Full enumeration of valid measure combinations per budget tier (`simulate_outcomes.py --budget-tier … --budget-utilization …`) — existing
- ✓ Top-N ranking by Final-Index (`analyze_simulation_results.py`) and named-strategy dominance check (`balance_analysis.py`) — existing
- ✓ Per-tier KZ start values (50/42/34) balanced — existing (commit 1cfb2fa)
- ✓ Game is interactive and engaging — validated by MHP workshop feedback ("interaktiv ++"); keep the format
- ✓ Wave calculation is learnable: waves 2 and 3 fit the planned 20 min once teams knew the procedure — MHP workshop
- ✓ Safe-to-change simulation foundation: uv env (`uv sync`), golden characterization tests + full digests, every formula once in `planspiel/` with thin root wrappers, UTF-8 config with real umlauts, exact arithmetic with paper rounding, config validator, bounded full enumeration incl. over-budget plans (FOUND-01..07) — Validated in Phase 1: Simulation Foundation

### Active

- [ ] Rule clarity: "Maßnahmenwechsel" vs "Levelwechsel" are defined unambiguously (Kurswechsel event + rules)
- [ ] Level downgrade rule decided and documented
- [ ] Budget overrun penalty is linear (−X KZ per started 10k over budget) and never makes overspending profitable
- [ ] Event cost effects are excluded from RoS
- [ ] Players understand how measures work and what attacks/events affect (card legend + explainer)
- [ ] Attack names veiled in pre-attack material, revealed by name when the wave hits
- [ ] All print material generated from `simulation_config.json` via LaTeX → PDF (attack worksheets, measure cards, budget/event cards, tracking + how-it-works sheet)
- [ ] Rebalanced config verified by full enumeration after the rule changes
- [ ] Flow fits the afternoon: wave 1 no longer overruns (worked example), whiteboard write-up replaced by printed tracking sheet

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
- Phase 1 complete (2026-10-01): `uv run pytest` (240 fast + 11 slow tests), rules in `planspiel/rules.py`, `planspiel validate`, default `simulate_outcomes.py --budget-tier <t>` enumerates all 782,336 combinations incl. over-budget (~50 s, ~125 MB per tier). Best over-budget final KZ is 85 vs 100 in budget in every tier; Budget Review boundary at exactly 25k/50k/75k contradicts the printed text (review CR-01 → Phase 2 RULE-07).
- (pre-Phase 1) `simulate_outcomes.py:539` dropped over-budget combinations — now enumerated.
- Manual print-sync trap: `e_threshold`, `mitigation_cap`, bonus values are printed verbatim on `Angriff-{1,2,3}_*.docx` with no generator; measure cards pptx also hand-maintained.
- Existing generators: `generate_pptx_cards.py`, `generate_from_template.py` (pptx), `generate_attack_calculator.py` (xlsx).
- **Interpreter trap:** `python` on PATH is Inkscape's bundled 3.12 without packages → always `uv run` (resolved in Phase 1). MiKTeX 23.10 (pdflatex/lualatex/latexmk) available.
- Sim ↔ print divergence already exists: per-wave KZ bonus/malus for meeting the E-target (`simulate_outcomes.py:448-449`) is not printed anywhere.
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
| Overspend X calibrated on trim-back criterion | Every over-budget plan must lose to its own trimmed version; step rewards make marginal criterion infeasible | ✓ Decided 2026-09-29 |
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
*Last updated: 2026-10-01 after Phase 1 (Simulation Foundation)*
