# Phase 6: Rebalance - Context

**Gathered:** 2026-10-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Tune `simulation_config.json` (and, where needed, clue/story wording in `content/`) so the five design principles hold under full enumeration:
- overspending never pays (gate, static + move paths);
- every choice matters and no measure is overpowered;
- good play wins and clue-driven, risk-based measure choice pays off;
- mediocre play ends positive;
- tiers stay comparable.

Then regenerate all print material from the final numbers and finish the Phase-5 carry-over list (reference paths, answer keys, Welle 0, `MAX_PENALTY_ROWS`/`MAX_WINDOWS`, removing `≈`, dropping "vorläufig" on the final index).

Requirements: BAL-01 … BAL-09. Out of scope: new measures, attacks, waves or event types; session-flow changes (Phase 7).

**Baseline measured 2026-10-28** (static reference plan, 782,336 plans per tier, current config):

| Tier | Start KZ | In budget | Median final KZ (in budget) | Best in budget | Best over budget |
|---|---|---|---|---|---|
| low | 50 | 69,454 | 63 | 98 | 91 |
| medium | 42 | 124,321 | 65 | 100 | 91 |
| high | 34 | 197,753 | 66 | 100 | 89 |

- In-budget RoS spans about −1 … +1.5, so RoS·100 out-ranges KZ.
- Validator: one warning, `hand_calc.kz_slope attacks.exfil` (17/7, wave 3).
- Gate (Phase 2): strict min X 9 / 5 / 3, config X = 9, zero margin in low.

</domain>

<decisions>
## Implementation Decisions

### Carried forward (decided earlier, not re-asked)
- **Phase 2 D-18:** If trim-back needs X > ~5, soften the step rewards: Exzellenz +5/L3, the OEM-Audit tiers and the M7 "Kritische Schwachstelle" tiers. No overspend cap, no voiding of bonuses, no steep X.
- **Phase 2 D-25:** X = 9 is provisional. The slow gate over move paths (swap layer + window families) was deferred to this phase.
- **Phase 2 trim-back definition:** an over-budget plan must end strictly below its best in-budget version that is reachable by lowering or cancelling levels only.
- **Hand-calculability:** formulas stay fixed and linear; only operands change. Order of change is config → README → print material.
- **Phase 5 D-18/D-22/D-23 carry-over:**
  - re-choose the reference paths (`uv run planspiel referenzpfade`) and re-pin `tests/golden/answer_keys.json`;
  - rescale `final_index` and drop "vorläufig";
  - re-run `practice.check_example` and re-pin `welle0.json` and `worksheet_tex.json`;
  - review `booklet.MAX_PENALTY_ROWS` (⌈100 ÷ X⌉; a smaller X needs more rows plus a new RoS-page layout proof) and `MAX_WINDOWS`;
  - remove the `≈` approximations once no slope is non-terminating.
- The committed print set is written only by the last plan of the phase (Phase 5 D-19 order).

### Tuning levers (Stellschrauben)
- **D-01: Scope of change = all numeric values plus the shape of tier events.**
  - Allowed: OEM-Audit or M7 tiers may become linear instead of stepped.
  - Unchanged: the set of measures, attacks, waves and event types; nothing new is added.
  - Changing bonus measures of a wave counts as a value change and is allowed, but must stay consistent with the clues (D-17..D-20).
- **D-02: Nothing is taboo.** Budgets (350/400/450), start KZ (50/42/34), wave weights, costs, CIA values, thresholds, caps, bonuses and event values may all change if the enumeration justifies it.
  - Wave weights must stay thematically plausible for their attack.
  - Every printed number is regenerated from config, so no hand edit is needed.
- **D-03: Hand-friendly (BAL-02) = at most one decimal place.** This applies to every worksheet slope and constant.
  - `hand_calc` validator warnings become errors.
  - No 17/7-type slope may remain.
- **D-04: One review checkpoint for the config change.** Claude iterates autonomously until all checks pass, then stops at one human-verify checkpoint showing:
  - the old → new diff per value, with the rationale;
  - all BAL metrics before/after per tier;
  - the gate results;
  - the proposed reference strategies (D-06) and overpowered thresholds (D-16);
  - any story/clue edits (D-20).
  Goldens are regenerated (`--update-golden`) and print material rebuilt only after approval, as a reviewed snapshot change in the style of Phase 1 01-06 / Phase 2 D-20.

### Measurement basis and thresholds (Messbasis & Schwellen)
- **D-05: Both layers.**
  - Dominance, near-mandatory checks and distributions (percentiles, Pareto, top-K) use the static enumeration (782k plans per tier, fast).
  - Reference-strategy placement (BAL-07), comeback after wave 1 (BAL-08) and the decision-point effect of change window / Kurswechsel (BAL-06) use the swap layer and move paths (`planspiel tausch`, `rules.evaluate_path`; about 4 min per tier).
- **D-06: Reference strategies are proposed by Claude and approved by the user at the D-04 checkpoint.**
  - Archetypes from BAL-07, made concrete per tier:
    - good: reads the clues, risk-based, balanced CIA;
    - bad: ignores the clues, all-in on one CIA dimension, overspends, or hoards budget;
    - mediocre: in between.
  - They live in config like `reference_plans`.
- **D-07: Tier comparability (BAL-09) is measured on final KZ.** Best in-budget final KZ and median in-budget final KZ must lie within a corridor across tiers; research proposes the width, e.g. ±5 KZ.
  - The tier choice stays a trade-off (more budget vs lower start KZ); no tier may be clearly better.
- **D-08: Priority when principles conflict:** 1 every choice matters > 2 good → good > 3 rewarding > 4 controlled. The overspend gate is a hard constraint above all of them.
- **D-09: Quartiles and "mediocre" are measured against in-budget plans only.** Over-budget plans are judged by the gate, not by quartiles.
- **D-10: "Mediocre ends positive" (BAL-08)** = the median in-budget plan of each tier ends above that tier's start KZ. This holds today (63/65/66 vs 50/42/34) and must keep holding.
- **D-11: The best in-budget result lands slightly below 100** (about 90–98 per tier), so the 0..100 clamp barely binds and the top stays distinguishable. A perfect 100 should be very hard or impossible to reach.

### Overspend X (BAL-01)
- **D-12: One global X** for all tiers: one rule and one penalty table in the team booklet. Softening the step rewards (Phase 2 D-18) should bring the required X to ≤ ~5 in every tier.
- **D-13: X = the maximum of the per-tier strict minima + 1** (safety margin of 1 KZ in X).
  - The gate must pass on the static reference **and** on move paths: swap layer plus window-1/window-2 families.
  - The move-path gate runs as a `slow` test before the D-04 checkpoint and at phase end.
- **D-13a: Fallback if X stays > ~5 after softening without hurting other principles.** The D-04 checkpoint presents both options with measured numbers and the user decides:
  - (a) accept the higher X;
  - (b) soften the step rewards further, up to linear or flat.
  Capping overspend and voiding bonuses stay excluded (Phase 2 D-18).

### Final index (BAL-03)
- **D-14: Purpose: determining the winner in the debrief.** The facilitator compares teams with one number, also across tiers, so it must be computable by hand in the debrief minute. It stays facilitator-side and is not added to the team booklet.
- **D-15: KZ leads, RoS corrects.**
  - Weights are set from the measured in-budget distributions so that KZ carries about 2/3 and RoS about 1/3 of the in-budget spread; research picks the spread measure, e.g. IQR.
  - Form: `KZ + k · RoS`, with `weight_kz = 1` and an integer `k` (a round number like 20 or 25), RoS taken with two decimals.
  - The weights stay in the config `final_index` block, and the 0.85 utilization filter is dropped (BAL-03).

### Overpowered and dominance (BAL-06)
- **D-16: Claude proposes the thresholds from the measured distributions**, for example:
  - near-mandatory: in > 90 % of the top-100 plans;
  - overpowered: removing it drops the tier's best by > 10 KZ;
  - strictly dominated: no plan where this level beats the alternatives.
  The user approves them at the D-04 checkpoint with the numbers. No measure may be overpowered.

### Clues lead to measures: risk-based protection (added by the user)
- **D-17: The learning goal is risk-based protection.** Teams analyse the company (story documents) and choose measures based on that analysis.
  - Hints stay indirect and not too unambiguous; story texts never name measures.
  - From the description texts plus the measure cards (Phase 5 D-06: a card says what the measure defends against), a team can work out which measures fit MechTech.
- **D-18: The clue matrix gains a facilitator-only measure mapping.**
  - Each clue in `content/clues.toml` records the measure(s) it points to and a weight (e.g. strong/weak).
  - Players never see it; the matrix on the facilitator booklet shows it.
  - `planspiel clues` checks:
    - every bonus measure of every wave is supported by at least one clue;
    - clue count and weight are graduated by measure importance (bonus size / effect): more important measures get more or stronger clues.
- **D-19: The clue-following strategy must pay off.** The "good" reference strategy (D-06) is derived from the clue→measure mapping and must rank in the top quartile (BAL-07).
  - "Just buy the bonus measures" must not automatically be the best plan: budget and CIA balance still matter.
  - This ties in with "no measure overpowered" (D-16).
- **D-20: Config and story both adapt until they fit.** When clue weight and measure importance disagree, either may change.
  - Editing the story is probably easier: adding, strengthening or weakening a clue in `content/texte.toml` and `content/clues.toml`.
  - Story edits must pass the veil scan, giveaway, digit and SC6 quote checks.
  - Any story change is shown at the D-04 checkpoint.

### Plan-phase requirements review (2026-10-28)
- **D-21: Plan cut: one check plan per requirement, then one tuning plan, then BAL-05.** *(Decided 2026-10-28 in the plan-phase requirements review.)*
  - BAL-01, BAL-02, BAL-03, BAL-04, BAL-06, BAL-07, BAL-08 and BAL-09 each get their own plan. It builds that requirement's check, metric or tooling test-first. A check may fail against today's config; that is its target.
  - Exactly one tuning plan follows. It changes the values (X and the final-index `k` included) until every check passes and ends at the D-04 checkpoint. It is the only plan that carries several requirement IDs: the tuning is one search under the D-08 priorities, and splitting it per requirement would re-tune the same values, X above all, in every plan.
  - The BAL-05 plan comes last. It adopts the approved config, re-pins the goldens, re-chooses the reference paths and regenerates the print material (Phase 5 D-19 order).
- **D-22: BAL-01's "capping overspend" option is superseded.** Phase 2 D-18 and D-13a exclude capping and voiding bonuses. If X stays above ~5 after softening, the user chooses between accepting the higher X and softening further. *(Clarified 2026-10-28 in the plan-phase requirements review.)*
- **D-23: The "overspends" bad archetype of BAL-07 is judged by the overspend gate (D-09), not by quartile placement.** Putting a typical overspender into the bottom quartile would need a steep X, which D-12 and Phase 2 D-18 exclude. The other bad archetypes (ignores clues, all-in on one CIA dimension, hoards budget) are defined as in-budget plans and placed by quartile. *(Clarified 2026-10-28 in the plan-phase requirements review.)*
- **D-24: BAL-05 covers the generated print set**, i.e. `planspiel print` and the PDFs in `final_documents/generated/`. The legacy hand-maintained docx/pptx in `final_documents/` are retired in Phase 7 (LEG-01) and are not updated in this phase. *(Clarified 2026-10-28 in the plan-phase requirements review.)*
- **D-25: The BAL-07 reference strategies get their own config key**, e.g. `reference_strategies`. `reference_plans` keeps the Phase-5 answer-key paths that `planspiel referenzpfade` chooses. *(Clarified 2026-10-28 in the plan-phase requirements review.)*

### Claude's Discretion
- The calibration method, e.g. a trim-back sweep over cached per-combination tuples instead of re-enumerating, and the search strategy over config values.
- The exact metrics and numeric thresholds for BAL-06…09 (corridor width D-07, spread measure D-15, overpowered thresholds D-16), proposed with data at D-04.
- How the "decision point shifts outcomes" check is quantified for budget tier, measure/level choice, change window and Kurswechsel.
- The clue weight scale and the exact graduation rule (D-18), e.g. the sum of clue weights per measure is monotone in bonus size.
- How the balance report presents top-K, Pareto and unfiltered optima (BAL-04); the existing `simulation_summary_<tier>.json` already holds most of it.
- Whether `MAX_PENALTY_ROWS` rises and the RoS page is re-proven, which depends on the final X.
- What the trimmed in-budget version of an over-budget move path is (swap layer, window-1/window-2 families) for the move-path gate (D-13).
- Which population the path-based reference strategies are placed against: static in-budget plans or legal in-budget paths (D-05, D-09).
- How "the budget tier shifts outcomes" (BAL-06) is shown while best and median stay inside the D-07 corridor, e.g. each tier has a different optimal plan.
- How the suite stays green while goldens and print wait for D-04 approval. One option: wave-1 checks are tested on fixtures, and the tuning plan works on a candidate config file that replaces `simulation_config.json` only after approval.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and requirements
- `.planning/PROJECT.md` — design principles 1–5, Key Decisions (overspend, RoS, Final-Index, reference paths)
- `.planning/REQUIREMENTS.md` — BAL-01 … BAL-09 wording
- `.planning/ROADMAP.md` §Phase 6 — success criteria, Phase-5 carry-over list, research flag topics
- `.planning/STATE.md` §Blockers/Concerns — Phase 2 D-18 / gate numbers
- `README.md` — rules and formulas (prose source of truth; update if a rule shape changes, e.g. linear OEM-Audit)
- `CLAUDE.md` — print-sync, full-enumeration and `planspiel gate` workflow rules

### Prior phase decisions
- `.planning/phases/02-rule-changes/02-CONTEXT.md` — D-14 … D-28 (overspend penalty, trim-back definition, D-18 softening, D-25 deferred move-path gate, swap rules)
- `.planning/phases/02-rule-changes/02-08-GATE-REPORT.md` — measured X minima, witness plans, the step-reward explanation
- `.planning/phases/02-rule-changes/02-RESEARCH.md` — M2: softening options, partial softening reaches low 6, flattening all reaches 4/2/1
- `.planning/phases/05-player-facilitator-print-material/05-CONTEXT.md` — D-17 … D-23 (answer keys, reference paths, final-index weights in config), D-26 Q6 (`≈` until Phase 6)
- `.planning/phases/03-content-source-veiling/03-CONTEXT.md` — clue matrix rules, veiling, giveaway list, digit allowlist (constraints on story edits)

### Config and content
- `simulation_config.json` — every tuned value; `final_index`, `reference_plans`, `practice`, `final_events.budget_review.overspend_penalty`
- `content/clues.toml` — clue matrix to be extended with the measure mapping (D-18)
- `content/texte.toml` — story and measure prose (D-17, D-20)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `planspiel/enumerate.py` / `TierKernel` + `simulate_outcomes.py --budget-tier <t>`: full static enumeration with compact per-combination store; writes `simulation_summary_<tier>.json` (top-K, percentiles in/over budget, best, Pareto).
- `planspiel/gate.py` (`gate_tier`, `gate_from_columns`, `lowering_closure`, `required_penalty_x`): static trim-back gate, extensible to move paths.
- `planspiel tausch` / `rules.evaluate_path` / `rules.swap_credit`: swap layer and change-window paths (37.3 M paths per tier).
- `planspiel referenzpfade` / `planspiel/refpaths.py`: proposes reference paths near the median.
- `planspiel/validate.py` (`_one_decimal`, `hand_calc.*` checks): switch warnings to errors (D-03).
- `planspiel/balance.py`, `planspiel/report.py`, `planspiel/analyze.py`: balance reporting and final-index ranking (`rules.final_index`, weights from config).
- `planspiel clues` (`planspiel/story.py` / clue checks): extend for the D-18 measure mapping.
- `planspiel/practice.py` (`check_example`): Welle-0 guards to re-run.

### Established Patterns
- Reviewed snapshot change: goldens are regenerated only through `--update-golden` after a human-verify diff checkpoint (01-06, Phase 2 D-20).
- Exact arithmetic (`Fraction`), paper rounding via `planspiel.rounding.round_half_away`; builtin `round()` forbidden.
- TDD for simulation changes; `uv run pytest` (fast) / `uv run pytest -m slow` (full enumeration).
- Prose has no digits (allowlist); printed numbers come from config only.

### Integration Points
- Goldens to re-pin after approval: `tests/golden/characterization_*.json`, `digest_*.json`, `gate_*.json`, `answer_keys.json`, `welle0.json`, `worksheet_tex.json`.
- `planspiel print` rebuilds the 13 PDFs into `final_documents/generated/`; `planspiel print --check` must pass; the print≡sim equivalence test (Phase 4) must pass on the new values.
- `booklet.MAX_PENALTY_ROWS`, `booklet.MAX_WINDOWS` layout guards.

</code_context>

<specifics>
## Specific Ideas

- The user's framing of the learning goal: "Analyse des Unternehmens → darauf basierend Wahl der Maßnahmen". Hints should let teams work it out themselves, never hand it to them.
- "Die Anzahl der Hinweise und die Wichtigkeit der Hinweise sollte nach der Wichtigkeit der Maßnahmen gestaffelt sein."
- "Letztendlich soll alles ineinander passend sein": story, clues, bonus measures and values form one coherent whole.
- The witness plan from Phase 2 shows the step-reward problem: low `1121103000` gains 13 KZ before review from M7 L3 (+7 vs +3) and Exzellenz (+5).

</specifics>

<deferred>
## Deferred Ideas

- **Plenum analysis step (Phase 7, FLOW-02/03):** after the teams analyse the company on their own, a plenum discussion of CIA weighting and particular risks. Variants raised by the user:
  - discuss and steer, so all groups share the same knowledge;
  - collect without comment and leave it standing;
  - skip the discussion entirely to demand more independence.
  This is a session-flow decision with time-budget impact, to be decided in Phase 7 (debrief/schedule).

</deferred>

---

*Phase: 06-rebalance*
*Context gathered: 2026-10-28*
