# Phase 6: Rebalance - Research

**Researched:** 2026-10-28
**Domain:** Deterministic game-balance calibration over a full enumeration (Python 3.12, uv, pytest); config tuning, check tooling, clue content, print regeneration
**Confidence:** HIGH for measured baseline numbers and code facts (all re-derived this session against the real tooling); MEDIUM for proposed thresholds and the feasibility of the D-11/D-12 combination (measured search, not proven); LOW for items tagged `[ASSUMED]`

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Carried forward (decided earlier, not re-asked)**
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

**Tuning levers (Stellschrauben)**
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

**Measurement basis and thresholds (Messbasis & Schwellen)**
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

**Overspend X (BAL-01)**
- **D-12: One global X** for all tiers: one rule and one penalty table in the team booklet. Softening the step rewards (Phase 2 D-18) should bring the required X to ≤ ~5 in every tier.
- **D-13: X = the maximum of the per-tier strict minima + 1** (safety margin of 1 KZ in X).
  - The gate must pass on the static reference **and** on move paths: swap layer plus window-1/window-2 families.
  - The move-path gate runs as a `slow` test before the D-04 checkpoint and at phase end.
- **D-13a: Fallback if X stays > ~5 after softening without hurting other principles.** The D-04 checkpoint presents both options with measured numbers and the user decides:
  - (a) accept the higher X;
  - (b) soften the step rewards further, up to linear or flat.
  Capping overspend and voiding bonuses stay excluded (Phase 2 D-18).

**Final index (BAL-03)**
- **D-14: Purpose: determining the winner in the debrief.** The facilitator compares teams with one number, also across tiers, so it must be computable by hand in the debrief minute. It stays facilitator-side and is not added to the team booklet.
- **D-15: KZ leads, RoS corrects.**
  - Weights are set from the measured in-budget distributions so that KZ carries about 2/3 and RoS about 1/3 of the in-budget spread; research picks the spread measure, e.g. IQR.
  - Form: `KZ + k · RoS`, with `weight_kz = 1` and an integer `k` (a round number like 20 or 25), RoS taken with two decimals.
  - The weights stay in the config `final_index` block, and the 0.85 utilization filter is dropped (BAL-03).

**Overpowered and dominance (BAL-06)**
- **D-16: Claude proposes the thresholds from the measured distributions**, for example:
  - near-mandatory: in > 90 % of the top-100 plans;
  - overpowered: removing it drops the tier's best by > 10 KZ;
  - strictly dominated: no plan where this level beats the alternatives.
  The user approves them at the D-04 checkpoint with the numbers. No measure may be overpowered.

**Clues lead to measures: risk-based protection (added by the user)**
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

**Plan-phase requirements review (2026-10-28)**
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

### Deferred Ideas (OUT OF SCOPE)
- **Plenum analysis step (Phase 7, FLOW-02/03):** after the teams analyse the company on their own, a plenum discussion of CIA weighting and particular risks. Variants raised by the user:
  - discuss and steer, so all groups share the same knowledge;
  - collect without comment and leave it standing;
  - skip the discussion entirely to demand more independence.
  This is a session-flow decision with time-budget impact, to be decided in Phase 7 (debrief/schedule).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BAL-01 | X calibrated per tier on the trim-back criterion (raw and capped KZ); impractical X after softening is a user decision (D-22) | Q1 (min X is independent of config X; sweepable from cached columns; X = max + 1), Q2 (move-path gate definition decides 14/7/5 vs 9/5/2), Q3 (step-reward inventory and measured lever table), D-13a numbers |
| BAL-02 | All worksheet slopes/constants hand-friendly; validator warnings become errors | Q4 (what `hand_calc.*` checks; load_config would reject the real config if promoted too early; fix options for exfil 17/7: range 14 at cap 7 gives slope 2.0 and is balance-neutral) |
| BAL-03 | 0.85 filter dropped; Final-Index weights rescaled from data | Q5 (filter lives only in the legacy `--output` mode of `planspiel/simulate.py` + 3 docs), Q6 (pooled IQR gives k = 20.5, so k = 20; formula decision `KZ + k·RoS`) |
| BAL-04 | Balance reports show top-K, Pareto, unfiltered optima per tier | Q5 (what `report.py` already writes, what is missing: in-budget-only lists, `--config` for `balance.py`, one consolidated per-tier report the D-04 checkpoint can print) |
| BAL-05 | All print material regenerated from the rebalanced config | Q10 (goldens to re-pin, `print --check`, 13 PDFs + manifest, `MAX_PENALTY_ROWS` arithmetic, Welle-0 guards), D-24 scope |
| BAL-06 | No measure/level dominated or near-mandatory; every decision point shifts outcomes | Q7 (today: M7 and M2 near-mandatory, M7 overpowered; band-based near-mandatory metric; decision-point effects measured) |
| BAL-07 | Good strategies top quartile, bad bottom quartile (overspender via gate) | Q8 (`reference_strategies` shape; measured placement of candidate archetypes; the all-in-C archetype lands in the TOP quartile today), Q9 (clue→measure mapping) |
| BAL-08 | Mediocre ends above start KZ; comeback after wave 1 possible | Q7 (median 63/65/66 static, 60/62/62 legal; comeback quantified) |
| BAL-09 | Best and median comparable across tiers; spread within a defined range | Q7 (corridor, IQR, p5–p95 per tier measured) |
</phase_requirements>

## Summary

Phase 6 is a calibration problem over a fully enumerable, deterministic game. All tooling needed to measure it already exists (`ResultStore` columns, `gate.py`, `enumerate_swap_layer`, `report.py`); what is missing are the checks, the per-tier consolidated report, a move-path gate and the tuned values. This session re-derived the baseline with the real code and with an independent vectorised re-implementation (numpy, scratch only) that reproduces `TierKernel` exactly (0 mismatches over 782,336 plans × 7 columns × 3 tiers, 1.2 s per tier instead of 37–52 s) and reproduces the pinned gate histograms and the Phase 2 path-family numbers exactly. All numbers below are measured, not estimated, unless tagged.

The baseline fails five of the principles at once. (1) Overspend: strict min X is 9 / 5 / 3 (low / medium / high), so D-13 would give X = 10 and D-12's "≤ ~5" is not met. (2) Every choice matters: M7 appears in 100 % of all in-budget plans within 10 KZ of the tier best (≥ L2 in 88–89 %), M2 in 100 % in medium/high; removing M7 drops the tier best by 14 / 16 / 18 KZ (threshold 10). (3) D-11: best in-budget is 98 / 100 / 100 on the static layer and 100 in every tier on the legal swap layer. (4) Final-Index: with weights 1/1 the RoS term is `100·RoS`, which makes the KZ share of the in-budget IQR only 0.19 / 0.26 / 0.34 (low / medium / high); a pooled IQR calculation gives `k = 20.5`, i.e. `k = 20` (KZ share 0.67 pooled; 0.54 / 0.64 / 0.72 per tier). (5) Hand-calculability: one warning, `attacks.exfil` slope 17/7. Mediocre-ends-positive (median 63/65/66 vs 50/42/34) and tier comparability of best/median (corridor 2 and 3 KZ) already hold.

The central tuning finding is that the three softenings D-18 names are the wrong first lever for the low tier. Low-tier X is set by a thin tail (89 one-step overspenders need X ≥ 6) and it responds mostly to two things the Phase 2 research did not vary: (a) the **positive Budget Review tiers** (the trimmed in-budget version collects them; no tier bonus at all gives X 14 / 13 / 12, today's 5/10/15 per 25 k€ gives 9 / 5 / 3, 8/16/24 gives 6 / 2 / 1, 9/18/27 gives 4 / 2 / 1; this lever is sweepable from the cached columns without re-enumerating), and (b) the top of the distribution saturating at 100 (low budget 350 → X 9, 380 → 6, 400 → 5). Single-lever softening of Exzellenz, OEM and M7 barely moves the low tier (Exzellenz 0..5: always 9; Phase 2's combination reaches 6 / 4 / 2 but lowers the best to 95 / 91 / 88). A raised review tier lifts the median by 4–6 and keeps the best at 100, which D-11 forbids; start KZ shifts restore it without touching X. A hand-built candidate shows D-11 and D-12 can hold together on the static layer: review 9/18/27 per 25 k€, exfil range −5…9, start KZ 38 / 28 / 18 gives static X 3 / 1 / 1, best 94 / 97 / 98, median 57 / 57 / 56, IQR 14 / 16 / 17 (move-path result in Q11). What it does not solve is the structural dominance (M7 and M2 near-mandatory, M7 overpowered), which is the harder half of the tuning plan. A bounded random search (Q11) adds evidence.

**Primary recommendation:** Build each BAL check test-first as a pure function over the existing `ResultStore` columns (plus the swap-layer tables), every command taking `--config`; fix the move-path trim definition as "lower the START plan, then any legal continuation" (X-neutral, 9/5/2 on the swap family) instead of "same swap pair" (14/7/5); in the tuning plan lower X first through the positive Budget Review tiers (a column-level lever), then restore D-11 and the corridor with start KZ and attack ranges, and treat M7/M2 dominance and the BAL-07 archetype placement as the hard half; tune on a candidate config file outside `simulation_config.json` with the fast vectorised engine for iteration and the real tooling for the verdict; flip `hand_calc` to errors and adopt the config only in the BAL-05 plan.

## Architectural Responsibility Map

This repository is an offline Python tool chain, not a multi-tier application. "Tier" below means the module layer that owns a capability.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Game numbers (X, step rewards, k, budgets) | `simulation_config.json` | — | Single source of truth (CLAUDE.md: config → README → print) |
| Formulas (final index, review penalty, window cost, swap credit) | `planspiel/rules.py` | `tests/test_single_definition.py` (AST guard) | Every formula exists once; new check code must call rules, not re-implement |
| Enumeration and compact store | `planspiel/enumerate.py` (`ResultStore`, `enumerate_tier`, `enumerate_swap_layer`) | `rules.TierKernel`, `rules.TierTables` | Columns are the cache that makes sweeps cheap |
| Trim-back gate (static) | `planspiel/gate.py` | `planspiel/cli.py` (`gate`) | Already column-based; extend, do not duplicate |
| Move-path gate | new functions next to `gate.py` over `rules.TierTables` | `enumerate.py` swap iterator | Needs per-state tables; shares `lowering_closure` |
| Balance metrics BAL-06..09 | new pure functions over columns/tables (module `planspiel/balance.py` family or a new `metrics` module) | `report.py` formatting | Metrics are data; formatting stays in `report.py` |
| Hand-calc validation | `planspiel/validate.py` | `planspiel/config.py` (`check_config` turns warnings into `HandCalcWarning`) | Severity switch must not break `load_config` early |
| Clue → measure mapping and checks | `planspiel/texts.py` (`Clue`, `load_clues`, `check_clues`, `FacilitatorView`) | `content/clues.toml`, `planspiel/master.py`, `print/templates/master.tex.j2`, `planspiel/cli.py` (`clues`) | Facilitator-only; never reaches `PreAttackView` |
| Reference strategies | config key `reference_strategies` + validator | `planspiel/refpaths.py` (path shape reuse), `rules.evaluate_path` | Same `{start, windows}` shape as `reference_plans` |
| Print regeneration | `planspiel print` (`render`, `texbuild`, `stamp`) | `planspiel/booklet.py` layout guards | Last plan only (Phase 5 D-19) |

## Research Findings by Planning Question

### Q1. Calibration method for X (BAL-01)

**How `gate.py` works today** [VERIFIED: planspiel/gate.py]
- `gate_tier(cfg, tier, store=None)` enumerates (or takes) a `ResultStore` and calls `gate_from_columns(n_measures, code_index, kz_final, kz_pre_review, remaining, over_budget, config_x, step, tier_name)`.
- `trim_keys` writes, for every in-budget plan, the key `kz_final·4ⁿ + (4ⁿ−1−code)` into a 4ⁿ grid and `lowering_closure(best, n)` (prefix maximum along each of the n axes, 2.3–2.6 s per tier in pure Python) turns each cell into the best in-budget plan whose levels are all ≤ the cell's. The tie-break picks the lowest code.
- Per over-budget plan: `trimmed_final = key // 4ⁿ`; `required_penalty_x(kz_pre_review, trimmed_final, steps, strict)` is `max(1, gap // steps + 1)` (strict) or `max(1, ceil(gap/steps))` (weak) with `steps = started_steps(−remaining, step)`. `unlosable` counts trimmed finals of 0, `untrimmable` counts plans without any in-budget lowering. `passed = config_x ≥ min_strict and unlosable == 0 and untrimmable == 0 and violations == 0`.
- Result and witness shape: `GateResult` (tier, layer, config_x, step, over_budget, min_x_strict, min_x_weak, x_histogram, witness, unlosable, untrimmable, violations_at_config_x, passed); goldens `tests/golden/gate_{low,medium,high}.json`.

**Raw vs capped KZ** [ASSUMED interpretation; flag to the user]: the simulation clamps the KZ to 0..100 after every wave and again after the review. The gate already uses the pre-review KZ (clamped per wave) and subtracts `X·steps` without a floor ("raw" at the 0 end), and separately fails on `unlosable` (trimmed final 0). I read BAL-01's "raw and capped" as exactly this pair: strict minimum on the raw penalty, plus the capped outcome check. Keep both, report both.

**What can be cached and swept without re-enumerating** [VERIFIED: planspiel/enumerate.py STORE_LAYOUT, rules.py]
- Store: 19 bytes per dependency-valid plan (`code_index`, `kz_final`, `own_cost`, `total_cost`, `damage_eur`, `over_budget`, `kz_pre_review`, `remaining`), 782,336 plans per tier.
- Important structural fact: **the minimum X does not depend on the config X.** In-budget plans carry no penalty, and an over-budget plan's pre-review KZ and `steps` are X-independent. X only enters `violations_at_config_x` and the final KZ of over-budget plans. So the tuning loop never needs X until the end: calibrate everything else, then `X = max(strict minima over tiers and families) + 1` (D-13).
- Sweepable from the cached columns (no re-enumeration): X and step (`kz_final' = clamp(kz_pre_review + review_delta(remaining))`), the review tier list (values and minima; this is the strongest X lever measured, Q3), the tier budget (`remaining' = remaining + Δbudget`, `over' = remaining' < 0`; `total_cost` and event budget unchanged), the final-index weights (`damage_eur`, `own_cost`, `kz_final`). [VERIFIED by reasoning from the column definitions; the review-tier effect itself was measured with the full engine, which recomputes everything]
- Needs a re-enumeration: attack and wave parameters, measure costs/CIA/recovery, all events including the step rewards, `base_cia`, `kz_start` (clamp interplay), `severity_multiplier`. `kz_after` per wave is not stored (needed for the comeback metric, Q7).

**Runtimes (measured this session, 6-core Windows machine)**

| Operation | Time |
|-----------|------|
| `enumerate_tier` + store write, 3 tiers in parallel | 52 s per tier (37 s sequential per Phase 2 research) |
| `planspiel gate` all tiers (Phase 2 report, sequential) | 120 s |
| `lowering_closure` | 2.4 s per tier |
| `rules.TierTables` build | 36 s per tier |
| `planspiel tausch` (swap layer, 37.3 M paths), 3 tiers in parallel | 279–284 s per tier |
| pure-Python `path_outcome` over swap paths | 5.9 s per 1 M paths, i.e. about 221 s per 37.3 M |
| vectorised numpy evaluation (scratch engine), all 782,336 plans | 1.2 s per tier; static gate +0.2 s; full metric set per config (3 tiers) 3.4 s |
| numpy swap-family gate (37.3 M paths, narrow closure per swap pair) | 22 s per tier; start-lowered variant two passes 61 s per tier (3 tiers in parallel) |

The numpy engine reproduced the repo exactly: `kz_final`, `kz_pre_review`, `remaining`, `own_cost`, `total_cost`, `damage_eur`, `over_budget`: 0 mismatches in all three tiers; gate histograms identical to `tests/golden/gate_*.json` (low {1: 679,007 … 9: 3}, medium {… 5: 11}, high {… 3: 24}); swap-layer counts identical to `planspiel tausch` (37,300,736 swap paths; in budget 3,587,803 / 6,630,851 / 10,699,761). [VERIFIED: scratch scripts run against the real config]

**Recommendation.** Calibration plan (BAL-01) = (1) extend `gate.py` with the move-path gate (Q2) and a `calibrate` report (per tier and family: strict/weak minima, tail of the histogram, witness, unlosable/untrimmable; recommended `X = max + 1`), (2) keep the closure/threshold logic as pure functions over columns so synthetic-column tests and mini-config brute-force tests run in milliseconds (same pattern as `tests/test_overspend_gate.py`), (3) a `slow` test per tier for the real config. For the tuning loop, either run the real tools three tiers in parallel (about 55 s per candidate for the static layer; about 5 min per tier for swap-layer figures) or take the vector engine (see Standard Stack, decision needed).

### Q2. Move-path gate (D-13, deferred Phase 2 D-25)

**Path space** [VERIFIED: rules.py `TierTables.swap_paths`, `evaluate_path`, `swap_legal`, `swap_credit`, `swap_repair`]
- Windows follow waves 1 and 2 (`MAX_WINDOWS = 2`). The Kurswechsel (wave-1 event) forces exactly one Maßnahmentausch in the window after wave 1 unless the plan is D-22-exempt (all measures active or none active: 48,115 plans per tier).
- Swap layer: for every valid start `s0` with a possible swap, every `(dropped d, incoming i, level l)` with `s0[d] ≥ 1`, `s0[i] = 0`, end selection = canonical repair of `s0` without `d` plus `i` at level `l` (only `M2` has dependents, so repair caps M1/M3/M7 at level 2), valid; cost = `Init(i,l) − min(Init(d,s0[d]), Init(i,l))`. 37,300,736 swap paths + 48,115 exempt static = 37,348,851 legal games per tier; in budget 3.59 M / 6.63 M / 10.70 M.
- The families Phase 2 added for isolated late moves, counted over valid single-measure moves: window-1 move 22,274,048 and window-2 move 22,274,048 per tier (Phase 2 quotes 31,293,440 = 782,336 × 40, i.e. all 10 × 4 targets per start, probably including invalid and no-op targets [ASSUMED]). Swap + one window-2 move would be 1.43 bn paths (Phase 2 measured 6 / 3 / 2 "own"; not binding, not recommended for the gate).

**Precise definition of the "trimmed version" (recommended).**

> For a legal path P with start plan s0 that ends over budget, the trimmed versions are all in-budget legal paths whose START plan s0' is ≤ s0 componentwise (levels only lowered or cancelled), followed by ANY legal continuation (any swap, any window moves of the family). The best final KZ among them (including the positive Budget Review tier) is the comparison value; the path loses at X if `pre_review(P) − X·steps(P)` is strictly below it. Required X per path = `max(1, (pre − T) // steps + 1)`.

Debrief sentence: "Hätte das Team zu Spielbeginn weniger oder niedrigere Maßnahmen gewählt, wäre es im Budget geblieben und besser gelandet." It is deterministic, it reuses `lowering_closure` on a per-start array (`pool[s0]` = best in-budget final over all legal continuations from s0, then close under lowering), and it needs one pool pass and one scan.

**Why not "same swap pair, only levels lowered" (narrow).** It is more conservative and measured 14 / 7 / 5 on the swap family (witness low: swap M3→M1 L1 from start `0210133000`, pre-review 97 vs trimmed 84), which would force `X = 15` and make D-12 unreachable. The start-lowered definition measured 9 / 5 / 2 on the same 37.3 M paths. The choice moves X by 5 in the low tier, so I recommend stating it at the D-04 checkpoint even though it is formally discretion.

**Measured at today's config (X-requirement per family, pool from all families = Phase 2 "union"):**

| Family (paths per tier) | low | medium | high |
|-------------------------|-----|--------|------|
| static reference (782,336) | 4 | 1 | 1 |
| swap layer, start-lowered, pool = swap paths only (legal-only pool) | 9 | 5 | 2 |
| swap layer, narrow same pair | 14 | 7 | 5 |
| window-1 move family, union pool (22.3 M) | 9 | 5 | 3 |
| window-2 move family, union pool (22.3 M) | 5 | 2 | 1 |
| static, own alternatives only (the pinned Phase-2 gate) | 9 | 5 | 3 |
| **maximum** | **9** | **5** | **3** |

(The pinned static gate and the move families agree: the move paths add no demand beyond the static reference at today's config, X = max + 1 = 10. This must be re-run after tuning because it can start to bind.) Unlosable and untrimmable counts are 0 everywhere. [VERIFIED: scratch runs reproduce the Phase 2 M7 table exactly: static-own 9/5/3, swap-own 9/5/2, swap-narrow 14/7/5, W1-union 9/5/3, W2-union 5/2/1]

**Implementation and runtime of the slow gate**
- Pure Python on `TierTables`: build 36 s + 221 s per pass over the swap iterator. Two-pass (pool, then scan) ≈ 8 min per tier; single pass is possible by storing per start the maximum `pre_review` per `steps` value of its over-budget paths (a small dict per start) and evaluating X after the closure: ≈ 4.5 min per tier for the swap family, plus ≈ 2 × 2.5 min per tier for window-1/window-2. Three tiers in parallel processes fit a `slow` test in roughly 10–15 minutes (consistent with Phase 2 D-25's estimate).
- Vectorised numpy: about 1 min per tier for all four families.
- Test pattern without mocks: a brute-force cross-check on `tests/fixtures/mini_config.json` (M1, M2, M4, M6; 256 plans) enumerating every legal path through `rules.evaluate_path`, plus the real-config slow test pinning a `gate_paths_<tier>.json` golden (new golden; shape: per family min X strict/weak, histogram tail, witness, counts).

### Q3. Step-reward softening (Phase 2 D-18, D-01, D-13a)

**What forms the step rewards** [VERIFIED: simulation_config.json, `rules.evaluate_event`]

| Element | Config today | KZ swing |
|---------|--------------|----------|
| Wave bonuses (`bonus_measures`, `min_level` 2) | W1: M3 6, M4 6, M6 3; W2: M5 9, M7 6; W3: M1 8, M2 6, M8 9 | bonus × slope of the wave's attack (slopes 2.0 / 1.2 / 17/7): M8 21.9, M1 19.4, M2 14.6, M3 12, M4 12, M5 10.8, M7 7.2, M6 6 KZ |
| OEM-Audit (`checklist_tier`, wave 2) | measures M1 M2 M4 M5 M7 at level ≥ 1; tiers [[0,−15],[1,−5],[2,0],[3,0],[4,5],[5,15]] | −15 … +15 (largest single steps 0→1 +10, 4→5 +10) |
| Kritische Schwachstelle (`measure_level_tier`, wave 2) | M7 level tiers {0:−5, 1:0, 2:3, 3:7} | 12 swing |
| Exzellenz-Bonus (`level_bonus_per_measure`, wave 3) | +5 per measure at level 3 | +5 per L3 measure |
| Nervige Authentifizierung (`and_condition`, wave 3) | −10 if M1 ≥ 2 and M6 = 0 | −10 |
| Budget Review (`final_budget_tier`) | remaining 0/25/50/75 k€ → 0/5/10/15 | +5 per 25 k€ |

A single level upgrade can move the pre-review KZ by up to 29 KZ in the low tier (M7 L0→L1 max 29, p99 23; M1/M2/M3/M4/M8 L1→L2 maxima 22–23) [VERIFIED: pairwise slice analysis over valid plan pairs]. The wave bonuses (a threshold at level 2 worth 6–9 reduction points, i.e. 6–22 KZ per measure) are the largest single steps; no single step of the OEM, M7 or Exzellenz rewards exceeds +10, +5, +5.

**Phase 2 M2 measured (partial softening → low 6; flattening all → 4/2/1)** and reproduced this session exactly (static strict X low/medium/high; median, best in-budget as added columns):

| Variant | X | median | best in budget |
|---------|---|--------|----------------|
| current | 9 / 5 / 3 | 63 / 65 / 66 | 98 / 100 / 100 |
| Exzellenz +3, +2, +1, +0 | 9 / 4 / 2 (… 9 / 4 / 1) | 61 / 63 / 63 … 59 / 61 / 60 | 98 / 100 / 100 |
| OEM 4/5 → +3, 5/5 → +6 | 8 / 5 / 3 | 62 / 64 / 65 | 98 / 99 / 98 |
| M7 level 3 = +4 | 9 / 5 / 3 | 62 / 65 / 65 | 98 / 100 / 100 |
| Exz +2, OEM 3/6, M7 L3 +4 (Phase 2 "partial") | 6 / 4 / 2 | 60 / 62 / 61 | 95 / 91 / 88 |
| no Exz, OEM flat above 2, M7 L3 = L2 ("flatten") | 4 / 2 / 1 | 58 / 59 / 58 | 95 / 87 / 79 |

**New measurements (one lever at a time, static layer, X / median / best):**

| Lever | X low/med/high | median | best |
|-------|----------------|--------|------|
| OEM linear `s·(count−2)`, s = 2, 3, 4, 5 | 8/6/3, 8/6/3, 8/6/3, 9/6/3 | 63–65 / 66–68 / 66–69 | 100 / 100 / 98–100 |
| M7 linear `s·(level−1)`, s = 2, 3, 4 | 9/5/3 each | 63–64 / 65–66 / 66 | 97–99 / 99–100 / 100 |
| Exzellenz at level ≥ 2 instead of 3, +1/+2/+3 | 9/6/2, 9/7/3, 9/8/4 | 62–67 / 64–70 / 63–70 | 100 |
| exfil range −7…7 (slope 2.0) | 9/4/2 | 61/63/63 | 95/98/100 |
| exfil range −5…9 (slope 2.0) | 9/4/2 | 63/65/65 | 97/100/100 |
| exfil range −4…10 (slope 2.0) | 9/4/2 | 64/66/66 | 98/100/100 |
| exfil range −7…0 (slope 1.0) | 7/3/2 | 58/59/58 | 92/94/94 |
| wave-3 bonuses −1 / −2 / −3 | 10/7/3, 13/9/5, 13/7/5 | 62/64/65 … 60/63/64 | 98/100/100 |
| all bonuses −1 / −2 | 11/7/4, 13/9/5 | 61/63/65, 58/62/63 | 97/100/100, 97/99/100 |

Reading: (a) No single softening moves the low tier below 7; two of them make X worse (smaller bonuses lower the trimmed plans' final KZ more than they lower the over-budget plan's). (b) The exfil fix for BAL-02 (range 14 at cap 7, offset chosen so the best stays ≥ 97) is balance-neutral and lowers medium and high X by 1: a free first move. (c) The binding plans (89 low-tier plans need X ≥ 6) are one-step overspenders (87 of 89) whose lowering costs wave 1 (+3.0 KZ), wave 2 (+3.0) and wave 3 (+6.6) change, with the trimmed version gaining the review tier (mean review delta −9.2 for the over-budget plan vs +7.1 for the trimmed one); the lowered measure is most often M10 (36), M1 (28), M3 (12).

**Positive Budget Review tiers (the strongest X lever found; sweepable from cached columns)** [VERIFIED: 1.4 s evaluations per tier]. Review tiers are `[[0,0],[spacing,a],[2·spacing,2a],[3·spacing,3a]]`; X (static strict) low / medium / high, with median and best in budget:

| Review tiers (remaining ≥ …) | X | median | best |
|------------------------------|---|--------|------|
| none (all 0) | 14 / 13 / 12 | 55 / 57 / 57 | 97 / 100 / 96 |
| 0/3/6/9 at 25/50/75 | 11 / 9 / 9 | 60 / 62 / 62 | 97 / 100 / 99 |
| **today 0/5/10/15 at 25/50/75** | **9 / 5 / 3** | **63 / 65 / 66** | **98 / 100 / 100** |
| 0/7/14/21 at 25/50/75 | 7 / 3 / 2 | 65 / 68 / 69 | 100 |
| 0/8/16/24 at 25/50/75 | 6 / 2 / 1 | 67 / 69 / 70 | 100 |
| 0/9/18/27 at 25/50/75 | 4 / 2 / 1 | 68 / 71 / 72 | 100 |
| 0/10/20/30 at 25/50/75 | 2 / 1 / 1 | 70 / 72 / 74 | 100 |
| 0/5/10/15 at 20/40/60 | 8 / 4 / 2 | 64 / 66 / 66 | 100 |
| 0/7/14/21 at 20/40/60 | 4 / 2 / 1 | 67 / 69 / 70 | 100 |
| 0/5/10/15 at 30/60/90 | 11 / 7 / 7 | 61 / 64 / 64 | 97 / 100 / 99 |

Mechanism: the over-budget plan forfeits the review bonus and pays X per started step, while its trimmed version collects the tier (mean +7.1 for the binding low-tier plans). Side effects the D-04 report must show: a bigger tier raises the median by about +2 per +1 step, rewards hoarding (a plan that keeps 75 k€ gets +27 at 9/18/27 instead of +15, so the "hoard" archetype of Q8, today KZ 27 / 19 / 15, gains 12 KZ and must be re-placed), and raises the Budget Review's weight against the wave bonuses.

**Budget sweep (the structural link between X and saturation at the top)** [VERIFIED: 1.4 s evaluations]

| Tier | budget → X (median / best) |
|------|-----------------------------|
| low | 340 → 12 (60/96), 350 → 9 (63/98), 360 → 9 (65/100), 370 → 7 (67/100), 380 → 6 (69/100), 400 → 5 (73/100) |
| medium | 380 → 6 (61/97), 400 → 5 (65/100), 420 → 5 (69/100), 440 → 4 (72/100) |
| high | 400 → 5 (57/93), 440 → 4 (64/100), 450 → 3 (66/100), 470 → 3 (68/100) |

X falls as the budget rises because more top plans saturate at 100 and a clamped trimmed version ties or wins. D-11 forbids exactly that saturation, so changing the budget trades D-12 against D-11; the review tiers and the start KZ do not (start KZ shifts of −8 left X unchanged in a measured candidate while lowering best and median).

**What "linear instead of stepped" looks like** [VERIFIED: `eventtext.py` prints any tier list; `rules._tier_lookup`]
- Config only, no new event type: OEM `tiers: [[0,−6],[1,−3],[2,0],[3,3],[4,6],[5,9]]` (equal increments); M7 `tiers: {"0":−3,"1":0,"2":3,"3":6}`; Exzellenz as `level: 2`, `kz_per_measure: 2` or as a smaller constant. Integer KZ values keep it hand-calculable; no rule code changes. `eventtext.effect_rows` groups equal consecutive checklist values and prints one row per level for the level tier, so a linear list prints as a regular table. `measure_level_tier` requires `texts` `tier_labels` per level, which exist (labels do not contain numbers).
- README: CLAUDE.md says README has no fixed numbers; the event tier shape is not described there, so README needs no change unless the review/penalty text or the gate definition (Q2) changes. [VERIFIED: README grep]

### Q4. Hand-friendliness (BAL-02, D-03)

**What the validator checks today** [VERIFIED: planspiel/validate.py `check_hand_calc`, `check_exactness`, `event_final_budget_tier`]
`hand_calc.kz_slope` (slope `(kz_at_full_mitigation − kz_at_full_damage)/mitigation_cap` must have ≤ 1 decimal, `_one_decimal`: `(value·10).denominator == 1`), `hand_calc.severity_cap` (`base_severity == mitigation_cap`), `hand_calc.severity_multiplier` (= 1), `hand_calc.weights` (sum 1, ≤ 1 decimal), `hand_calc.recovery` (≤ 1 decimal), `hand_calc.penalty_step` (step = 10). `kz_at_full_*`, `e_threshold`, bonuses, `s_unit` are validated as integers, so only slope, weights, recovery and step can be non-friendly. Exactness errors (`exact.severity_scaling`, `exact.damage_whole_euros`) already exist.
Today's single warning: `hand_calc.kz_slope attacks.exfil` (17/7, wave 3). Ransomware slope is 16/8 = 2.0, OT 12/10 = 1.2. Fix options for exfil keeping `base_severity == mitigation_cap`: range 14 at cap 7 (slope 2.0) or 21 (3.0) or 7 (1.0); or cap = base severity = 10 with range 17 (slope 1.7) and `s_unit` adjusted (14 k€ keeps base loss 140); or cap 8 with range 16.

**Where a slope/constant is printed** [VERIFIED: grep]: `planspiel/printmodel.py` (attack worksheet: `format_factor(slope)`, `kz_decimals_hint` vs `kz_fraction_hint`), `planspiel/master.py` (parameter table with `format_factor` + `≈` for non-terminating slopes; Fall-3 rows via `approx_signed`; wave check rows `e_value`, `gr`, `kz_attack`, `kz_exact`), `planspiel/fmt.py` (`format_factor` falls back to "× 17 ÷ 7", `format_approx`), `planspiel/refpaths.py` (console), `content/texte.toml` (`approx_hint`). After the slope is one-decimal: E-values and GR have ≤ 1 decimal (weights one decimal × integer CIA), `kz_attack` ≤ 2 decimals, so the `≈` disappears from every slope-derived cell. The RoS (division by own spend) and the final index (if built from the unrounded RoS) stay non-terminating: see Q6 for the rule that makes them exact. The `format_factor` fraction fallback and the `kz_fraction_hint` branch become dead code once the validator rejects non-terminating slopes (delete or keep as defence; recommend delete in BAL-05 with the `≈` removal).

**Switching to errors without breaking the build** [VERIFIED: config.py `check_config`, tests]
`load_config` calls `validate` and raises `ConfigError` for any `error`, but turns `warning`s into `HandCalcWarning`. If `hand_calc.*` were errors immediately, `load_config(simulation_config.json)` would raise and the whole suite (and `planspiel print`) would fail until the exfil slope is changed. Six tests assert the exfil warning as the only warning on the real config: `tests/test_budget_review.py` (lines 276, 284), `tests/test_config_prose_removed.py:99`, `tests/test_kurswechsel.py:205`, `tests/test_practice_config.py` (356, 360). Recommended sequencing:
1. BAL-02 plan: add a `hand_calc_level` parameter (default "warning") to `validate`/`_Validator`; `planspiel validate` passes "error"; new tests on fixtures and a test asserting that `planspiel validate --config <candidate>` exits 1 on the 17/7 config and 0 on a fixed one. `planspiel validate --strict` exists already (warnings → exit 1) and is the zero-code interim gate.
2. Tuning plan: candidate config must pass `planspiel validate --config <candidate>` in error mode.
3. BAL-05 plan: flip the default to "error" together with adopting the config; update the six tests to expect no issues (they will otherwise fail on the adopted config only if the exfil slope still warns, which it will not).

### Q5. Balance report (BAL-04) and the 0.85 filter (BAL-03)

**What exists** [VERIFIED: planspiel/report.py, simulate.py, analyze.py, balance.py]
- `simulate_outcomes.py --budget-tier <t>` (wrapper → `planspiel.simulate.main`) enumerates all valid plans, in and over budget, and writes `simulation_summary_<tier>.json` (format 1): combinations (total, valid, in/over budget), `top.kz_final/ros/final_index` (K = 10 default, `--top`), `percentiles` (nearest-rank p0, 5, 25, 50, 75, 95, 100 of KZ and RoS, in vs over budget), `best` (in budget, over budget, `kz_gap`), `pareto` (KZ max vs own cost min; points with example plan and count), `final_index_status` string "vorläufig …". Console `format_console` prints the same.
- `planspiel tausch` → `simulation_summary_tausch_<tier>.json` (counts, KZ percentiles of legal games from a histogram, best in/over budget).
- Gaps against BAL-04: the top lists and the Pareto front are over all plans (in budget and over budget mixed) while D-09 judges in-budget plans only; there is no per-tier report that combines distribution, dominance, near-mandatory, overpowered, corridor and reference-strategy placement; `balance.py` (`balance_analysis.py`) has a hard-coded strategy list (with stale cost comments) and no `--config` (its `main()` ignores arguments, calls `run_analysis()` with `DEFAULT_CONFIG_PATH`) and still prints "Final-Index (vorläufig)"; `POSITIVE_KZ_THRESHOLD = 50` is a presentation constant flagged for BAL-08 ("Präsentationsschwelle … wird in Phase 6 überprüft").
- **Where the 0.85 filter lives** [VERIFIED: grep `utilization|0.85`]: only in the legacy `--output` mode: `planspiel/simulate.py` (`run_simulation`, `--budget-utilization`, `--budget-max`, `--budget-min`, `budget_filter` in the output summary), documented in `README.md` lines 280–289, `CLAUDE.md` (Balance bullet and the large-files bullet), `.planning/PROJECT.md` (Key Decisions); tested by `tests/test_enumeration.py` (lines 431–475). The default run is already unfiltered. The consumer of the legacy output is `analyze_simulation_results.py` (→ `planspiel/analyze.py`), which ranks that JSON by Final-Index.
- Root wrappers (`simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`) must keep working (Phase 1 D-26): they are 6-line shims; flags they expose are documented commands. Recommendation: remove `--budget-utilization` and `--budget-max` (only meaningful with it) and their tests, keep `--output`/`--budget-min` for `analyze`, and rewrite the three docs; alternatively keep the flags and only drop them from the documented workflow. Either satisfies "dropped from the balance workflow"; the first is YAGNI-cleaner.

**Recommendation for the BAL-04 plan (tooling only):** one `planspiel balance` (or extended `report`) entry point per tier, `--config` aware, that prints (a) in-budget top-K by KZ, RoS and Final-Index, (b) in-budget Pareto (KZ vs own cost) and the unfiltered optima (best in budget, best over budget, gap, as today), (c) percentile table, and has a stable section where BAL-06..09 add their metric blocks. Keep `simulation_summary_<tier>.json` format 1 additive (new keys, format number bump only if a key changes meaning). `balance.py` then reads `reference_strategies` from config (Q8) instead of the hard-coded list.

### Q6. Final-Index (BAL-03, D-14, D-15)

**Measured in-budget spreads, current config, static layer, own cost > 0** [VERIFIED: numpy engine on the exact columns]

| Tier | n | KZ p5/25/50/75/95 | KZ IQR | RoS p5/25/50/75/95 | RoS IQR | k for 2:1 (IQR) | k (p5–p95) | k (std) |
|------|---|-------------------|--------|--------------------|---------|-----------------|-----------|---------|
| low | 69,453 | 43/54/63/71/81 | 17 | −0.87/−0.22/0.19/0.49/0.80 | 0.705 | 12.1 | 11.4 | 11.7 |
| medium | 124,320 | 40/56/65/73/83 | 17 | −0.70/0.03/0.32/0.51/0.74 | 0.488 | 17.4 | 15.0 | 15.1 |
| high | 197,752 | 37/56/66/73/83 | 17 | −0.53/0.14/0.35/0.47/0.68 | 0.330 | 25.7 | 19.0 | 19.2 |
| pooled | 391,525 | | 18 | | 0.44 | **20.5** | | |

Spread measure: **IQR** (robust against the −1.00 RoS tail of plans that buy nothing and the clamped KZ top). With `k = 20`: KZ share of the in-budget IQR is 0.67 pooled (0.54 low, 0.64 medium, 0.72 high); `k = 15`: 0.73 pooled; `k = 25`: 0.62 pooled. KZ and RoS correlate at 0.79 (0.76 high), rank correlation final-index vs KZ 0.95 at k = 20. Current weights (1, with `RoS·100`) are an effective `k = 100`: KZ share about 0.2 (low). **Recommend `k = 20`** as the starting value; one global k is consistent across tiers within ±0.1 of the target share, no per-tier k is possible (D-14 compares across tiers). Re-measure after tuning because RoS (damage and own cost) changes with every value; the tuning plan sets the final integer, but 15, 20, 25 are the candidates.
Cross-tier note: with k = 20 the best Final-Index per tier is 124.8 / 118.6 / 114.8 and the median 66.0 / 71.0 / 72.4 (low highest best, lowest median). D-07 corridors are on final KZ; a Final-Index corridor is an optional addition.

**Where the weights are consumed** [VERIFIED: grep `final_index|weight_ros`]: `rules.final_index(kz_final, ros, weight_kz, weight_ros)` (`weight_kz·kz + weight_ros·(ros·100)`; None RoS → `weight_kz·kz`); callers `report.py` (summary ranking, `dump_record`), `analyze.py` (`--weight-kz/--weight-ros` default from config), `balance.py`, `master.py` (answer-key rows, `final_index` shown as `format_approx(index)` + "vorläufig"), `refpaths.py` (console text "vorläufig, Gewichte …"); config `final_index` block, validator `check_final_index`, loader `FinalIndexWeights`; tests `tests/test_final_index_config.py`, `test_rules_semantics`, `test_ros_ledger`, `test_enumeration*`, `test_master_model`, `test_booklet_model`; golden `tests/golden/answer_keys.json`. "vorläufig" strings: `report.FINAL_INDEX_STATUS`, `report.format_console` label, `balance.py` (several), `refpaths.py:302`, `content/texte.toml` keys `final_index_provisional` and `final_index_note` (and the key list in `texts.py:88`).

**Formula decision (needs a plan-level call):** D-15 says `KZ + k·RoS`, integer `k`, RoS with two decimals. The current code computes `weight_ros·(RoS·100)`, so `k = 20` would be `weight_ros = 1/5` on RoS-in-percent, which is neither an integer nor hand-friendly. Recommended: change `rules.final_index` to `weight_kz·kz + weight_ros·ros2`, where `ros2 = round_half_away(ros, 2 decimals)` (exact `Fraction`, builtin `round()` forbidden), config `{"weight_kz": 1, "weight_ros": 20}` (integers). Then the Final-Index is exact with at most 1 decimal (20 × 0.88 = 17.6), the master sheet shows RoS as a rounded value by rule (no `≈`), and `format_approx` is no longer needed for RoS or the index. Consumers listed above all pass through `rules.final_index`, so the change is one function plus its tests plus the "vorläufig" removals and one `answer_keys.json` re-pin. Prose that states the old weights or the provisional status and must be updated (config → README → print order): `README.md` (Simulation section: "Final-Index (vorläufig bis zur Neuskalierung)", "Standard 1.0/1.0", the `--weight-ros 0.5` example, the filter paragraphs, the gate sentence if the path definition is added), `CLAUDE.md` (Spielmechanik bullets "RoS … Final-Index … Default-Gewichte 1.0/1.0", "Budget Review … X … vorläufig bis Phase 6", the Balance and large-files bullets that mention `--budget-utilization 0.85`), `.planning/PROJECT.md` Key Decisions. [VERIFIED: grep]

### Q7. Metrics and thresholds for BAL-06 … BAL-09

All numbers: current config, in-budget plans, measured this session (static layer unless noted).

**Strictly dominated.** Define per (measure, level l ≥ 1): the share of in-budget contexts (the other 9 measures fixed, plan in budget and dependency-valid) in which level l ends with a strictly higher `kz_final` than the best lower level of the same measure. "Strictly dominated" = share 0 over all contexts. Today the smallest shares are M9 L2 0.24 / M10 L2 0.25 (low), so **nothing is strictly dominated at the context level** (every share is > 0). This metric is cheap (slice comparison on the 4ⁿ grid) and the right guard against a future dead level; keep it, threshold "share > 0".
A practical second signal is "dead in the top set": levels that never occur in near-optimal plans (M1 L3, M2 L3, M3 L3, M5 L3, M9 L3 occur in 0 % of the 1,000 best in-budget plans in low; M9/M10 ≥ L2 in ≤ 2 %). Report it, do not make it a hard check (budget limits which L3 can be bought at all).

**Near-mandatory.** The D-16 example (">90 % of the top-100 plans") is degenerate: top-100 by KZ with the cost tie-break is a thin slice (10 plans reach 98 in low; top-100 spans KZ 93–98). Recommend instead the **near-optimal band**: all in-budget plans within B = 5 KZ of the tier best (low 104 plans, medium 134, high 120; B = 10: 728 / 1,057 / 1,195). Near-mandatory = the measure is present (level ≥ 1) in > 90 % of band plans. The band gets thin when the distribution is tightened (a tuned candidate had bands of 31–53 plans in two tiers), so widen it to at least the 200 best plans when it is smaller [ASSUMED size]. Measured at today's config, B = 5, share (level ≥ 1) of the worst offenders: **M7 1.00 in all tiers (≥ L2: 0.94 / 0.96 / 0.93)**, **M2 1.00 in medium and high (0.88 in low)**, M4 0.85 / 0.90 / 0.97, M1 0.95 and M5 0.91 in high; at B = 10 M7 is still 1.00 (≥ L2 0.88 / 0.89 / 0.86) and M2 1.00 in high; top-100 view: M7 1.00 (≥ L2 0.94–0.97), M2 0.87–1.00. In the hand-built and searched candidates of Q11, M7 stayed above 0.9 in medium and high in every case, so near-mandatory is the hardest check to satisfy. Expect M7 to need structural work (see Q11), not just value nudges: M7 L1/L2 are among the best CIA-per-cost buys (M7 L1: CIA 7 for 32 k€; only M6 L1 is better), M7 sits in the OEM checklist, carries the Kritische-Schwachstelle swing and a wave-2 bonus.

**Overpowered.** Removing a measure (forcing level 0) drops the tier's best in-budget KZ by Δ. Today: M7 14 / 16 / 18, M2 3 / 7 / 11, all other measures 0–2. D-16's threshold "> 10 KZ" fails for M7 in every tier and for M2 in high. Capping at ≤ L1 or ≤ L2 gives M7 4 / 3 / 1 and 0, so only the presence of M7 matters, not its level. Measured effect of M7-specific changes on the drop (static): flat Kritische-Schwachstelle tiers 6 / 8 / 12; tiers {−2,0,2,4} 10 / 12 / 15; M7 bonus 3: 13 / 16 / 18; CIA −1 each: 12 / 16 / 18; init +20: 11 / 13 / 17; the M7 event swing is the dominant part of Δ, yet the near-mandatory band share stays 1.0 in all of them.

**Decision-point effects (BAL-06, second half).** Measured:
- Budget tier: top-1 in-budget plan differs per tier (`0102003200` KZ 98 cost 280 / `1101122200` KZ 100 cost 318 / `1201123000` KZ 100 cost 356); top-100 overlap low–medium 49, medium–high 55, low–high 4; the low-optimal plan lands at rank percentile 99.9 % in medium and 98.1 % in high. Quantify as "tier-specific optimum": Jaccard of the top-100 (or band) sets between tiers < 0.5 while best and median stay inside the corridor.
- Measure/level choice: in-budget IQR 17 on every tier; the context-level improvement shares above.
- Change window: for a sample of 40,388 in-budget swap paths, the best single window-2 move improves the final KZ by ≥ 3 in 59–61 % of paths (≥ 1 in 65 %), mean +6.0 / +6.3 / +6.5, max +25. A "just-in-time buy before wave 3" effect: adding the wave-3 bonus measure in window 2 saves two waves of OPEX and only pays Init once (a feature for clue readers, but note it when sizing wave-3 bonuses).
- Kurswechsel: per start with ≥ 2 in-budget swaps (92,537 / 160,318 / 246,604 starts) the best-minus-worst swap final KZ has median 29 / 30 / 30, p90 40 / 42 / 43; share with range ≥ 3 is 0.99.
Threshold proposal: each decision point must shift the final KZ by ≥ 3 in ≥ 50 % of the tested situations (all four hold by a wide margin today).

**Comeback after wave 1 (BAL-08).** The loss in wave 1 is bounded by the ransomware range (−6 at full damage, no wave-1 KZ events): KZ after wave 1 ranges 44–60 (low, start 50), 36–52 (medium, start 42), 28–44 (high, start 34). So nobody is eliminated by construction. Quantify the comeback as: among starts with KZ after wave 1 ≤ start − 5 (19,368 / 19,530 / 19,531 starts with an in-budget swap continuation), the best legal continuation ends median 71 / 70 / 65 (p90 81 / 79 / 76, max 93 / 95 / 88) and 99–100 % of them end above the start KZ. Static in-budget plans in that group: 57.5 % / 66.5 % / 68.1 % end above start (median final 53 / 47 / 40). Proposed check: ≥ 90 % of such starts have a legal continuation that ends at start KZ + 10 or better (today 91 % / 96 % / 96 %, above start 99 % / 100 % / 100 %); the stricter variant "reaches the tier's legal in-budget median (60 / 62 / 62)" holds for 91 % / 81 % / 66 %, so it would constrain the high tier first. `kz_after` is not in the store: compute from `TierTables.change` (or add a `kz_after_1` column, +1 byte/record).

**Mediocre ends positive (D-10).** Static in-budget median 63 / 65 / 66 vs start 50 / 42 / 34 (margins +13 / +23 / +32); legal swap-layer median 60 / 62 / 62 (margins +10 / +20 / +28); swap-layer p5 42 / 39 / 36 (so ≥ 95 % of legal in-budget games end ≥ start − 8 in low, ≥ start − 3 in medium, above start in high). Check: median − start ≥ 5 on both layers.

**Tier comparability and controlled spread (BAL-09).**

| Metric | low | medium | high | Today's corridor |
|--------|-----|--------|------|------------------|
| best in budget (static) | 98 | 100 | 100 | 2 |
| best in budget (legal swap layer) | 100 | 100 | 100 | 0 |
| median in budget (static) | 63 | 65 | 66 | 3 |
| median in budget (swap layer) | 60 | 62 | 62 | 2 |
| IQR (static / swap layer) | 17 / 16 | 17 / 17 | 17 / 17 | |
| p5–p95 (static) | 43–81 | 40–83 | 37–83 | width 38 / 43 / 46 |
| over-budget best (static) | 91 | 91 | 89 | |

Proposed (D-07): corridor ±3 KZ (width ≤ 6) for best and for median in-budget final KZ, on both layers; D-11: best in [90, 98] on both layers (today the swap-layer best is 100 in every tier, so D-11 fails on the legal layer, not only the static one); spread (BAL-09): IQR within [13, 21] per tier and IQR differences across tiers ≤ 4; p5–p95 width ≤ 50. The "controlled" side also needs an upper bound on the median (median − start ≤ 28) because without it a search drifts into an "easy mode" (observed in the search runs, Q11).

### Q8. Reference strategies (BAL-07; D-06, D-19, D-23, D-25)

**Config shape.** New top-level key `reference_strategies`, separate from `reference_plans`, reusing the `{start, windows}` path shape and the existing helpers `validate.check_reference_selection` / `check_reference_swap` / `refpaths.reference_path`:

```json
"reference_strategies": {
  "low": {
    "good":       {"kind": "good",       "start": {"M1": 0, "...": 0}, "windows": []},
    "mediocre":   {"kind": "mediocre",   "start": {"...": 0}, "windows": []},
    "bad_ignore": {"kind": "bad",        "start": {"...": 0}, "windows": []},
    "bad_all_in": {"kind": "bad",        "start": {"...": 0}, "windows": []},
    "bad_hoard":  {"kind": "bad",        "start": {"...": 0}, "windows": []}
  }
}
```
(`kind` ∈ good / mediocre / bad; names free; the overspender archetype is NOT a strategy entry but is judged by the gate, D-23.) Validator: references only (like `reference_plans`); legality via `rules.evaluate_path` in the check, because a path with a possible Kurswechsel needs a swap window.

**Population and metric.** Recommended: place on the static in-budget population by Final-Index rank (exact, cheap, uses `summarize_tier`-style columns) AND check the KZ rank against the legal swap-layer population from the histogram percentiles (`planspiel tausch` already writes p25/p50/p75: low 52/60/68, medium 53/62/70, high 53/62/70). Path-based strategies include a mandatory swap; the swap-layer is the population they actually play in, static is the only layer with RoS columns. Rank by KZ alone is a weaker proxy of D-14's winner metric; if only one is wanted, use Final-Index on static.

**Measured placement of candidate archetypes (static, in-budget, k = 20; illustrative, not proposals):**

Cells: final KZ, KZ percentile / Final-Index percentile among the tier's in-budget plans (higher is better; top quartile = 75+, bottom quartile = below 25).

| Archetype (algorithmic definition) | low | medium | high |
|------------------------------------|-----|--------|------|
| good: bonus measures in descending bonus order (M5, M8, M1, M3, M4, M7, M2, M6), level 2 then 1 while the budget lasts (`2020210200` low, `2021201200` medium, `2022201200` high) | 71, 74 / 86 | 64, 46 / 60 | 56, 24 / 34 |
| bad: ignore clues, M9 + M10 at max level (`0000000022`) | 27, 0 / 0 | 19, 0 / 0 | 15, 0 / 0 |
| bad: hoard (M6 L1 only) | 27, 0 / 0 | 19, 0 / 0 | 15, 0 / 0 |
| bad: all-in A (M4, M5 high) | 52, 18 / 60 | 44, 7 / 35 | 36, 4 / 20 |
| bad: all-in I (M2, M4 high) | 42, 3 / 15 | 34, 1 / 7 | 26, 1 / 4 |
| bad: all-in C (M1, M3, M7, M6 high, `2020022000`) | **84, 97 / 96** | **81, 91 / 94** | **73, 73 / 85** |

(All-in A scores in the bottom quartile by KZ but only the 20th–60th percentile by Final-Index, because its RoS is high: another reason to fix which metric BAL-07 ranks by.)

Two design findings the tuning plan must act on: (1) the naive "buy the bonus measures in bonus order" strategy is NOT top quartile in medium and high (greedy spends the budget on the first measures at L2 and drops M7), and (2) the all-in-C archetype is top quartile everywhere because the C weights (W1 0.4, W3 0.5) dominate two of three waves and M1/M3/M7/M6 are themselves bonus measures; "all-in on one CIA dimension" must be defined so that it ignores the bonus measures of the other waves, or the wave weights (D-02, plausibility) must change. Also today the best plan in every tier (by KZ and by Final-Index) uses only bonus measures (M9 = M10 = 0), while 35–45 % of the top-1 % plans by Final-Index include M9 or M10, so "just buy the bonus measures" is not automatically best but the optimum is a bonus-only plan; D-19 needs a measurable form: "the best plan restricted to clue-supported measures is not the global best in at least one tier" or "≥ 20 % of the top-1 % plans contain a non-clue measure" (holds today at 35–45 %).

**Deriving "good" from the clue mapping (D-19).** Define it as an algorithm over config + `clues.toml`: take the clue-supported measures, sorted by clue weight sum (Q9) descending, buy L2 (L1 if L2 does not fit) in that order while `own_cost + event_opex ≤ budget`; then use remaining budget for the balanced-CIA fill. The tuning plan proposes the resulting concrete plan per tier at D-04; the config stores the concrete selection, the check asserts quartile placement and that the stored selection equals what the algorithm yields from the current clues (so a clue edit that changes the "good" plan breaks the check visibly).

### Q9. Clue → measure mapping (D-17 … D-20)

**Schema today** [VERIFIED: content/clues.toml, planspiel/texts.py]: 14 `[[clue]]` entries with `attack`, `source` (key in `content/texte.toml`, prefix `story.` or `measures.`), `quote` (verbatim, ≥ 15 chars after NFC, no typographic quotes), `why`. `Clue` is a frozen dataclass (`attack, source, quote, why`); `load_clues` reads exactly these four keys (unknown keys are silently ignored today); `check_clues` enforces ≥ 2 clues from ≥ 2 documents per attack, verbatim quote, pre-wave source, non-empty `why`. `planspiel clues` prints `format_clue_matrix` (6 columns) and the issues; the facilitator booklet renders the same rows through `master._clue_groups` → `ClueEntry(nr, document, section, quote, why)` → `master.tex.j2` (5 columns, headers `clue_head_*` in `[sheets.spielleitung]`).

**Proposed extension (all `[ASSUMED]` design, needs the planner's confirmation):**
- TOML: `measures = ["M4"]` (list of measure ids; empty list allowed for atmospheric clues) and `weight = 3` (1 = weak/atmospheric, 2 = clear, 3 = strong). Integer scale, three steps, matches D-18's "strong/weak".
- `Clue` gains `measures: tuple[str, ...]`, `weight: int`; `ClueRow`/`ClueEntry` gain a "Maßnahmen (Gewicht)" cell; `format_clue_matrix` a 7th column; header word `clue_head_measures` in texte.toml; the mini fixtures `tests/fixtures/mini_content/clues.toml` (6 clues, M1/M2/M4/M6) get the new keys.
- Checks in `check_clues` (new codes, errors): `clues.unknown_measure` (id not in config), `clues.bad_weight` (not 1–3), `clues.unsupported_bonus` (a bonus measure of any wave has clue score 0), `clues.not_graduated` (see below).
- Importance and graduation: importance `I(m) = Σ over waves where m is a bonus measure of bonus × slope(attack of that wave)` (KZ points at stake, exact Fractions) rather than the raw bonus, because slopes differ by wave: today M8 21.9, M1 19.4, M2 14.6, M3 12.0, M4 12.0, M5 10.8, M7 7.2, M6 6.0, so M5 has the largest raw bonus (9) but the 6th-largest effect. Clue score `S(m) = Σ weights of clues listing m`. Rule: `I(a) > I(b) ⇒ S(a) ≥ S(b)` for all bonus measures (weakly monotone), plus `S(m) ≥ 2` for every bonus measure and `S(max I) ≥ 4` (suggested floor, tune with the story). Warn, not error, for clues on non-bonus measures (red herrings are allowed; D-17 only requires bonus measures to be supported).
- Gap in today's matrix by my reading of the `why` texts (to be confirmed by the user): M4 (backup, clues 1, 3), M5 (clues 1, 3, 5), M7 (clue 2), M8 (clues 1, 2, 4, 5), M1 (clue 3), M3 weakly (clue 2) are supported; **M6 (wave 1) and M2 (wave 3) have no clue**, M3 and M1 only one; M9 and M10 (not bonus measures) have none either. A story edit of two or three clues is therefore needed, in line with D-20.
- Story-edit guards that a new or changed clue must pass: `uv run planspiel texts` (digit allowlist `content/digit_allowlist.toml`: prose has no digits except pinned exceptions; giveaway terms `content/giveaway_terms.toml`: ransomware, Verschlüssel*, Lösegeld, Erpress*, Phishing, Emotet, Exfil, Datendiebstahl, Darknet, Sinumerik, tokens "sps", "apt", compound "OT"+"Stör*"; the veiled/pre-wave profile; `OT` and `Erpress*` allowed only in story texts), `uv run planspiel clues` (quote verbatim ≥ 15 characters in the source key), the veil scan of `planspiel print` (`veil.scan_documents`), and the tests `tests/test_texts_digits.py`, `test_texts_giveaway.py`, `test_story_veil.py`, `test_veil_*`, `test_clues.py`. Story text must not name measures (D-17). A story edit changes the print stamp: candidate story edits live in a candidate content directory (`--content-dir`) during tuning and enter `content/` only in BAL-05.

### Q10. Keeping the suite green during tuning (D-04, Phase 2 D-20)

**Commands that take `--config`** [VERIFIED: planspiel/cli.py, simulate.py, analyze.py]: `planspiel validate | tausch | referenzpfade | gate | texts | clues | print` (the last three also `--content-dir`), `simulate_outcomes.py --config`, `analyze_simulation_results.py --config`. `balance_analysis.py` has no `--config` (gap, fix in BAL-04/BAL-07). Tests read `tests.support.CONFIG_PATH` = repo `simulation_config.json` (no override), so the whole suite always runs against the committed config; the tuning plan therefore must not edit `simulation_config.json` (nor `content/`) before approval. Work on `.planning/phases/06-rebalance/candidate_config.json` (and a candidate content dir) and run the real tools with `--config`. `planspiel print` with a non-default config marks the stamp `+lokal`, which is correct for candidates and keeps the committed manifest untouched (`stamp.nondefault_inputs`).

**Goldens and how they re-pin** [VERIFIED: grep `update_golden` in tests]

| Golden | Test | Fast/slow | Re-pin |
|--------|------|-----------|--------|
| `characterization_{tier}.json` | `test_characterization.py` | fast | `--update-golden` |
| `digest_{tier}.json` | `test_digest.py` | slow | `--update-golden -m slow` |
| `gate_{tier}.json` (+ new `gate_paths_{tier}.json`) | `test_overspend_gate.py` | slow | `--update-golden -m slow` |
| `answer_keys.json` | `test_master_model.py` | fast | after `referenzpfade` + config pin; also holds the final-index text |
| `welle0.json`, `worksheet_tex.json` | `test_welle0_golden.py`, `test_welle0_render.py` | fast | after `practice.check_example` passes on the new values |

The Welle-0 practice example reuses the real measures' costs, CIA and recovery (`practice_config(cfg)` view) while it has its own attack/wave/event block. Any change to M2, M4, M8, M9, M10 values can break `check_example` guards (case 3, exactly one bonus met and one missed, recovery > 0, a fractional KZ change with denominator 2, a minimum distance to a half point); re-choose the practice selection or values (`practice` is config, so it is in scope) and re-run `uv run pytest tests/test_practice_config.py tests/test_welle0_golden.py tests/test_welle0_render.py`.

**Print and equivalence.** `uv run planspiel print --check` (no TeX needed; exits 0 current, 1 stale, 2 environment error) reports `Druckmaterial aktuell: Stand 2026-10-26 · 3878dab (13 Dokument(e) …)` today and goes stale on any config or content commit; the test suite does not assert freshness, so a stale committed print set during tuning is harmless until BAL-05. The print≡sim equivalence test (`test_worksheet_equivalence.py` fast, `_full` slow, `test_worksheet_replay.py`) runs on whatever config it loads and asserts the printed steps equal the simulation on a dense grid; it needs no edit unless the worksheet shape changes (the removal of the fraction branch for a non-terminating slope is such a change). The build needs LuaLaTeX (MiKTeX 26.5 present, preflight returns no problems); 13 PDFs plus `manifest.json` land in `final_documents/generated/`. `build_master_sheet` raises `PrintModelError` when a tier lacks a legal in-budget reference path with a voluntary move, so the reference paths must be re-chosen (`uv run planspiel referenzpfade`, `--median N` skips about 4 min per tier) before `print`.

**`MAX_PENALTY_ROWS` and `MAX_WINDOWS`.** `penalty_rows(kz_per_step, step_k)` produces `⌈100 / X⌉` rows (one per started step until the penalty alone reaches 100): X = 10 → 10 rows, 9 → 12 (today's cap), 8 → 13, 7 → 15, 6 → 17, 5 → 20, 4 → 25. With the recommended `X = max + 1` and today's minima X = 10, rows decrease and the cap 12 holds with no layout work; any X ≤ 8 needs `MAX_PENALTY_ROWS` raised together with a new RoS-page layout proof (`tests/test_booklet_pdf.py` fill report, template `teamheft_ros.tex.j2`, which already splits the table in two columns at `penalty_split`). `MAX_WINDOWS = 2 = waves − 1` stays correct because D-01 adds no wave.

### Q11. Tuning search strategy (wave 2) and lever → metric sensitivity map

**Order of moves implied by D-08** (gate is a hard constraint, then 1 every choice matters > 2 good → good > 3 rewarding > 4 controlled):
1. Fix BAL-02 first (exfil slope; free, X-neutral: e.g. range 14 at cap 7, range −5…9).
2. Dominance structure (M7 and M2 near-mandatory/overpowered): measure efficiency and swing (M7: event swing, OEM membership, CIA/cost, bonus). Structural; every later distribution depends on it, so do it before X and quartiles.
3. X (gate): set the positive Budget Review tiers first (sweepable from columns, strongest lever), then residual softening and budgets; re-compute min X per tier and family after each structural change; X itself is set last as max + 1 (D-13).
4. Good-beats-bad placement (reference strategies; clue/story edits in parallel, since clue weights follow bonus importance, Q9).
5. Rewarding (median − start, comeback) and controlled (D-11 best 90–98, corridor, IQR) as constraints, tuned with `kz_start`, attack KZ ranges and `e_threshold` (X-neutral or nearly).
6. Final-index `k` last: it depends on the final RoS distribution (current config k = 20.5; a searched candidate gave 25.0).

**Lever → metric sensitivity map** (measured on the exact engine; X = static strict minimum, low / medium / high):

| Lever | X | Median | Best | Dominance / mandatory | Notes |
|-------|---|--------|------|-----------------------|-------|
| Positive review tiers (0/5/10/15 → 0/9/18/27 at 25/50/75) | **9/5/3 → 4/2/1** (none: 14/13/12) | +5 / +6 / +6 | 100 | none | sweepable from columns; rewards hoarding; strongest lever |
| tier budget +10 | −0.5 … −1 (low 350 → 380: 9 → 6) | +2 | → 100 (saturation) | thins Pareto | conflicts with D-11 |
| `kz_start` −8 (all tiers) | unchanged (3/1/1 in the candidate) | −8 | 100 → 98 in low, medium/high stay 100 until about −14 | none | cheapest corridor/D-11 knob; changes the tier narrative |
| exfil range 14 at cap 7 (−5…9) | medium/high −1 | ±0–1 | −1 … −3 | none | also BAL-02 |
| bonuses (all −1 / −2) | +2 / +4 (smaller bonus → larger X) | −2 / −5 | ≤ −1 | removes "buy bonus" pull | per-measure bonus also fixes the clue graduation (Q9) |
| Exzellenz kz 5 → 3 / 0 | medium/high −1; low unchanged | −2 / −4 | 0 | none | |
| OEM tiers linear s·(count−2) | medium +1 | +1 / +2 | 0 | changes the OEM-membership pull on M1/M2/M4/M5/M7 | |
| M7 event swing flat | −1 (low), 0 | ±1 | −3 | M7 removal drop 14/16/18 → 6/8/12 | band share of M7 stays 1.0 |
| M7 CIA −1 (−2) / Init +20 | +0 … +2 (+2 … +4) / +1 … +2 | −2 (−4) / −3 | −2 | drop barely moves | |
| `e_threshold` ±2 per wave, attack KZ ranges | searched (mixed) | large | large | | main median and best knobs |
| measure costs | not swept individually | | | likely main lever for near-mandatory `[ASSUMED]` | |

### Search results (evidence for the tuning plan, not a proposal)

Method: simulated-annealing / random local search over 28 discrete levers (Exzellenz value and level, OEM and M7 tier slopes, three attacks' KZ endpoints within hand-friendly ranges, per-measure bonus deltas, per-wave `e_threshold` deltas, M7 CIA and Init, three budgets, three start KZ), exact numpy engine, 3.4 s per full evaluation, five seeds of 140 steps (about 20 minutes in parallel). Objective (all per tier): static strict X ≤ 5; best in budget 90–98; median − start in [8, 28]; IQR 13–21; ≤ 1 % of plans ≥ 95; near-optimal band share of every measure ≤ 0.9 (B = 5); removal drop ≤ 10; corridor of best and of median ≤ 6. Not in the objective: review tiers, BAL-07 placement, move-path gate, clue consistency, hand-friendliness (the ranges were chosen friendly).

| Seed | X | best | median (start) | IQR | band share max | removal drop max |
|------|---|------|----------------|-----|----------------|------------------|
| 22 | 5 / 5 / 2 | 91 / 90 / 89 | 64 / 65 / 66 (52 / 46 / 40) | 14 / 16 / 14 | 0.96 / 0.90 / 0.87 | 2 / 2 / 3 |
| 25 | 5 / 3 / 2 | 98 / 92 / 94 | 65 / 59 / 62 (54 / 42 / 36) | 14 / 17 / 18 | 0.95 / 0.90 / 0.96 | 4 / 2 / 4 |
| 24 | 4 / 4 / 1 | 91 / 93 / 89 | 64 / 67 / 62 (44 / 48 / 36) | 13 / 12 / 13 | 0.93 / 0.91 / 0.99 | 3 / 2 / 4 |
| 23 | 5 / 5 / 2 | 95 / 95 / 90 | 64 / 64 / 59 | 13 / 13 / 14 | 0.96 / 0.96 / 0.92 | 4 / 4 / 4 |
| 21 | 5 / 5 / 3 | 91 / 93 / 90 | 64 / 66 / 63 | 13 / 13 / 12 | 0.91 / 0.92 / 0.98 | 3 / 4 / 5 |

Reading: D-11 (best 90–98), D-12 (X ≤ 5), D-07 (corridor), D-10 (median above start with margin) and "no measure overpowered" (drop ≤ 5) can hold at the same time on the static layer; the near-optimal-band share of the most-used measure sits at 0.87–0.99, i.e. around the 0.9 threshold, never clearly below it in all tiers. The searches moved M7 (event swing 0 … ±2 per level, CIA −1 … −2, Init +10 … +30), the bonuses (typically M4/M8/M1 down, M3/M5/M2/M7 up, i.e. the bonus-weight order changed a lot, so clue graduation has to follow), thresholds and ranges. Seed 25 (`exz_kz` 4 at level 2, OEM flat, M7 swing 2 per level with CIA −2 and Init +20, ransomware KZ −10…10, OT −6…6, exfil −6…1, OEM-Audit values all 0 (a zero-valued event, the planner must judge that), M3 +2, M5 +2, M7 +2, M2 +2, M4 −3, M8 −3, M1 −2, M6 +1, e_threshold +2 / −4 / −2, budgets 360 / 400 / 460, start KZ 54 / 42 / 36) was checked with the real tooling: `planspiel validate --config` 0 errors 0 warnings (slopes 2.5 / 1.2 / 1.0), `planspiel gate --config` strict X 5 / 3 / 2, identical to the engine, and the move-path families (start-lowered union pool) need X 4 / 2 / 2 (narrow same-pair: 8 / 5 / 4). The legal layer of that candidate (real `planspiel tausch --config`, 248–250 s per tier in parallel) shows why the swap layer belongs in D-11 and D-07: best in budget 100 / 96 / 94 (static 98 / 92 / 94), median 63 / 57 / 60 (static 65 / 59 / 62), p25 56 / 50 / 51, p75 70 / 65 / 68, p5 48 / 40 / 39, p95 80 / 75 / 77; so the low tier breaks the 98 ceiling on the legal layer and the best-corridor is 6. The best-by-KZ archetypes of Q8 on that candidate: the importance-order "good" greedy is in the top quartile (KZ pct 94 / 98 / 87), but "all-in C" is still KZ pct 99 / 100 / 99, so BAL-07's bad-archetype placement was not met without being searched for.

**Hand-built candidate with the review lever** (no search): review 9/18/27 per 25 k€, exfil −5…9, start KZ 38 / 28 / 18 gives static X 3 / 1 / 1, best 94 / 97 / 98, median 57 / 57 / 56, IQR 14 / 16 / 17; move paths (union pool) X 2 / 1 / 1 (narrow 6 / 2 / 1); near-mandatory and the M7 removal drop (11 / 16 / 21) not addressed.

Tuning-plan advice: take one of these as a seed rather than the current config; add the missing objective terms (BAL-07 placement for the algorithmic archetypes, band share, move-path gate, final-index k, clue consistency) and iterate in small structured steps from the sensitivity map with the same metric report each time; keep a change log (old → new, metric before/after) because D-04 prints exactly that; verify the final candidate with the real tools (`planspiel gate --paths`, `tausch`, `validate`, `texts`, `clues`), not only the engine. [ASSUMED: scratch search code is not kept in the repo; if the vector engine is accepted it belongs in `tests/support/`.]

### Plan inputs by requirement (serves the D-21 cut; does not re-open it)

| Plan | Build (test-first) | Real-config result today (expected to fail = the target) | Main risk |
|------|--------------------|-----------------------------------------------------------|-----------|
| BAL-01 | `gate.py` path gate (start-lowered, families swap / window-1 / window-2), `calibrate` report (`X = max + 1`), `planspiel gate --paths`, `gate_paths_{tier}.json` golden | static X 9/5/3; paths 9/5/3 (union), 14/7/5 (narrow); X would be 10 > ~5 | definition choice (Q2); runtime of the slow test |
| BAL-02 | `hand_calc_level` parameter in `validate`, CLI passes `error`, tests for each `hand_calc.*` code | one error: `attacks.exfil` 17/7 | breaking `load_config` early (Q4) |
| BAL-03 | `rules.final_index` with integer `k` and two-decimal RoS, remove "vorläufig", remove the 0.85 flags and docs | weights 1/1 (KZ share 0.19–0.34) | one `answer_keys.json` re-pin and doc sync |
| BAL-04 | per-tier balance report (in-budget top-K, Pareto, optima, metric blocks), `balance` takes `--config` and reads `reference_strategies` | hard-coded strategy list, mixed in/over-budget top lists | keep wrapper commands working |
| BAL-06 | dominance shares, band near-mandatory, removal drop, decision-point effects | M7 and M2 near-mandatory, M7 drop 14/16/18 | band definition and thresholds (A5) |
| BAL-07 | `reference_strategies` key + validator + legality, quartile placement, clue-derived "good" | all-in-C in the top quartile, greedy "good" not in medium/high | archetype definitions; which metric/population |
| BAL-08 | median-above-start on both layers, comeback metric | passes (63/65/66 vs 50/42/34; comeback 99–100 %) | `kz_after` not stored |
| BAL-09 | corridor, D-11 band, IQR range, p5–p95 width | D-11 fails (98/100/100 static, 100 legal); corridor and IQR pass | tuning drift to "easy mode" (needs the upper median bound) |
| Tuning | candidate config, review-tier lever first, then structural M7/M2, then ranges/starts, `k` last; story/clue edits in a candidate content dir | all of the above | the D-13a decision; M7 near-mandatory |
| BAL-05 | adopt config/content, flip `hand_calc` default, `--update-golden` (fast and `-m slow`), `referenzpfade`, practice guards, `MAX_PENALTY_ROWS`, remove `≈`/fraction branch, `planspiel print`, `print --check` | — | `PrintModelError` when a tier lacks a legal reference path; stale stamp |

## Standard Stack

### Core (all already in the repo; no new runtime dependency)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12 (uv-managed, `.python-version`) | all tooling | project constraint [VERIFIED: pyproject.toml] |
| uv | 0.12.5 | env + runner (`uv run`) | project rule: never the PATH `python` (Inkscape's) [VERIFIED: `uv --version`] |
| pytest | 9.1.1 | tests; markers `slow`, `pdf` | in `uv.lock` dev group [VERIFIED: pyproject.toml] |
| jinja2 | 3.1.6 | print templates | existing |
| pypdf | 6.19.0 | PDF layout tests | existing dev dep |
| `fractions.Fraction`, `array`, `itertools` (stdlib) | — | exact arithmetic, compact columns | all rules code is exact; `planspiel.rounding.round_half_away` |

### Supporting (optional, decision required)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| numpy | 2.5.4 (via `uv run --with numpy`, scratch only this session) | vectorised second encoding of the kernel for tuning iterations (1.2 s per tier) and a ~1 min/tier move-path gate | only if the tuning plan wants automated search or a fast slow-test; otherwise stay stdlib |

Vector-engine caveat: it is a second implementation of the formulas (like `tests/support/worksheet_replay.py`, Phase 4 "independent second encoding"). If adopted it belongs in `tests/support/` as a tuning/verification aid with a conformance test against `TierKernel` (random 20,000 plans per tier, 0 mismatches, as done here) and must not enter `planspiel/` (`tests/test_single_definition.py` AST guard forbids a second formula definition there).

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| numpy vector engine | real `TierKernel` + 3 parallel processes | no new dependency; about 55 s per candidate for the static layer, about 5 min per tier for swap-layer figures; fine for ~30–40 hand-guided iterations, too slow for random search |
| Pure-Python move-path gate | numpy | 4.5–8 min per tier vs ~1 min; pure Python keeps one implementation |

**Installation:** none for the recommended path. If the vector engine is accepted: `uv add --dev numpy` (see audit).

**Version verification:** numpy 2.5.4 resolved by `uv run --with numpy` on 2026-10-28 (`numpy.__version__`). `uv pip index versions` is not available in uv 0.12.5.

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| numpy | PyPI | long-established (latest release 2026-10-10) | seam returned unknown | seam returned none | SUS (`too-new`, `unknown-downloads`, `no-repository`) | Flagged: false-positive pattern (the newest release is 18 days old; numpy is a foundational scientific library), but the protocol requires a `checkpoint:human-verify` before `uv add --dev numpy`; optional and dev-only. Used in this session only through `uv run --with` in a scratch dir [`gsd-tools query package-legitimacy check --ecosystem pypi numpy`] |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** numpy (optional; planner inserts `checkpoint:human-verify` before any install). No other package is introduced; jinja2, openpyxl, python-pptx, pypdf, pytest are existing locked dependencies.

## Architecture Patterns

### System Architecture Diagram

```
                simulation_config.json            candidate_config.json (tuning only)
                        |                                   |
                        +---------------+-------------------+
                                        v
                    planspiel.config.load_config  --(validate; hand_calc level)-->  ConfigError / HandCalcWarning
                                        |
        +-------------------------------+--------------------------------+
        v                               v                                v
  rules.TierKernel               rules.TierTables                  rules.evaluate_path
  (static plans)                 (per-state tables)                (single legal game, traces)
        |                               |                                |
        v                               v                                v
  enumerate_tier ->              enumerate_swap_layer /            reference_plans (Phase 5)
  ResultStore columns            swap_paths() iterator             reference_strategies (new)
  (19 B/plan, 782,336)           (37.3 M legal paths)                       |
        |                               |                                    |
        +---------- pure checks over columns / tables ----------------------+
        |   gate (static) | gate (paths) | dominance | mandatory | overpowered
        |   quartiles | comeback | corridor | spread | final-index spread
        v
  per-tier balance report (top-K, Pareto, unfiltered optima, metric blocks)
        |
        v   wave 2: tuning loop edits ONLY the candidate config / candidate content
  D-04 human-verify checkpoint (old → new diff, metrics before/after, gate, strategies, story edits)
        |  approved
        v   wave 3 (BAL-05): adopt config + content, flip hand_calc default to error,
            re-pin goldens (--update-golden), referenzpfade → reference_plans, practice guards,
            MAX_PENALTY_ROWS review, remove ≈ / "vorläufig", planspiel print, print --check
```

### Recommended Project Structure (additions only)

```
planspiel/
├── gate.py            # + move-path gate (families swap / window-1 / window-2, start-lowered trim), calibrate report
├── balance.py         # reads reference_strategies from config; --config; consolidated per-tier report hook
├── metrics.py (new)   # pure functions: dominance shares, near-optimal band, overpowered drop, quartile placement,
│                      #   comeback, corridor/spread, final-index spread (columns in, numbers out)
├── report.py          # in-budget top-K/Pareto, drop FINAL_INDEX_STATUS
├── texts.py           # Clue(measures, weight), check_clues graduation, matrix cell
tests/
├── test_gate_paths.py, test_balance_metrics.py, test_reference_strategies.py, test_clues_mapping.py (new)
├── golden/gate_paths_{tier}.json (new, slow)
.planning/phases/06-rebalance/candidate_config.json   # tuning working copy (not simulation_config.json)
```

### Pattern 1: Column-based check over the existing store
**What:** every BAL check is a pure function of the `ResultStore` columns (and, for paths, `TierTables`), tested three ways: synthetic columns (milliseconds), brute force on `tests/fixtures/mini_config.json` (256 plans, no mocks), and a `slow` real-config test with a pinned golden.
**When:** BAL-01, -06, -07, -08, -09.
**Example (X what-if from cached columns):**
```python
# Source: planspiel/gate.py, rules.py (verified this session)
store = enumerate_tier(cfg, "low")
x, step = rules.penalty_params(cfg.final_events)
res = gate.gate_from_columns(len(cfg.measure_ids), store.column("code_index"), store.column("kz_final"),
                             store.column("kz_pre_review"), store.column("remaining"),
                             store.column("over_budget"), x, step, tier_name="low")
required = res.min_x_strict       # independent of config X; calibrated X = max over tiers/families + 1
```

### Pattern 2: Start-lowered path gate (pool + closure + scan)
**What:** pass 1: `pool[s0] = max in-budget final over all legal continuations from s0`; `lowering_closure(pool, n)`; pass 2: for every over-budget path with start `s0`, `T = pool[s0]`, `X = max(1, (pre − T)//steps + 1)`; single-pass variant stores `max pre` per `(start, steps)` and evaluates after the closure.
```python
# Source: scratch prototype (numpy), logic identical to gate.trim_keys / lowering_closure
pool = array("i", [-1]) * 4**n
for s0, pre, steps, final, in_budget in legal_paths(tables):      # swap iterator + window families
    if in_budget and final > pool[s0]: pool[s0] = final
gate.lowering_closure(pool, n)                                    # prefix maximum over the 4^n grid
x = max(max(1, (pre - pool[s0]) // steps + 1) for s0, pre, steps in over_budget_paths if pool[s0] > 0)
```

### Pattern 3: Near-optimal band instead of top-N
```python
best = max(kz[i] for i in in_budget)
band = [i for i in in_budget if kz[i] >= best - 5]                 # B = 5 KZ
share_l1 = {m: sum(level(i, m) >= 1 for i in band) / len(band) for m in measures}
near_mandatory = [m for m, s in share_l1.items() if s > 0.9]
```

### Pattern 4: Candidate-config tuning with the real tools
`uv run planspiel validate --config <cand>`; `uv run planspiel gate --config <cand> [--paths]`; `uv run python simulate_outcomes.py --config <cand> --budget-tier t --summary <tmp>`; `uv run planspiel tausch --config <cand> --summary-dir <tmp>`; summaries are gitignored and large outputs go to a temp dir.

### Anti-Patterns to Avoid
- **Top-100 by KZ with cost tie-break as the near-mandatory population:** 10 plans reach the maximum in low; use the band.
- **Promoting `hand_calc.*` to errors in `load_config` before the exfil slope is fixed:** the whole suite and `planspiel print` stop.
- **Editing `simulation_config.json`, `content/` or goldens before D-04 approval:** stales print and breaks fast tests (`test_characterization`, `test_master_model`, `test_welle0_*`).
- **A second formula definition in `planspiel/`:** vector engines live in `tests/support/` with a conformance test.
- **Using the narrow ("same swap pair") trim definition by default:** X +5 in the low tier for no debrief benefit.
- **Judging the Final-Index by RoS·100:** the KZ share is about 20 %.
- **Reading `sim_*.json`, `simulation_results*.json`, `*.jsonl` whole:** large and gitignored; parse targeted.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Best in-budget version with all levels ≤ plan | pairwise comparison of 782k × 782k plans | `gate.lowering_closure` (4ⁿ prefix maximum, 2.4 s) | pairwise is ~10¹¹; closure is n passes |
| "Per started 10.000 €" | `ceil` on floats | `rounding.started_steps` | exact, tested |
| KZ rounding | builtin `round()` (banker's) | `rounding.round_half_away_frac` | builtin `round()` is forbidden in rules/rounding |
| Over-budget definition | `total > budget` in new code | `rules.budget_ledger` | single definition |
| Legality of a window or swap | a second checker | `rules.evaluate_path`, `swap_legal`, `swap_repair`, `dependencies_satisfied` | same checks as the game |
| Percentiles | sorted-array interpolation | `report.nearest_rank` / `_histogram_rank` | same method as the summaries |
| Review/penalty text and rows | typed strings | `review_text.penalty_rows`, `tier_rows`, `eventtext` | generated from config with parse-back tests |
| Snapshot updates | editing golden JSON by hand | `--update-golden` + human checkpoint | D-04, Phase 2 D-20 |
| Config validation | ad-hoc asserts | `validate._Validator` codes with JSON paths | Phase 1 contract |

**Key insight:** the whole game is linear and integer; the risk is in definitions (which population, which trim, which spread), not in algorithms. Every check should be a few lines of exact arithmetic over data that already exists.

## Common Pitfalls

### Pitfall 1: Lowering X through saturation breaks D-11
**What goes wrong:** the budget lever that lowers low-tier X (350 → 400: 9 → 5) pushes the best to 100; softening the three D-18 rewards alone does not reach X ≤ 5 in low (best case 6 / 4 / 2 at the price of best 95 / 91 / 88). A larger positive review tier lowers X without saturation but raises the median by 4–6 and rewards hoarding.
**How to avoid:** lower X with the review tiers, then restore D-11 and the corridor with `kz_start`, attack KZ ranges and `e_threshold` (static X stayed at 3 / 1 / 1 while the start KZ moved by −8 … −16 in the measured candidate); still prepare the D-13a numbers in case the plan cannot hold every principle.
**Warning signs:** best ≥ 99 after an X improvement; median above start + 28; hoard archetype leaving the bottom quartile.

### Pitfall 2: The move-path trim definition silently decides X
**What goes wrong:** "same swap pair" = 14 / 7 / 5, "start-lowered" = 9 / 5 / 2.
**How to avoid:** state the definition in the gate docstring, README sentence and the D-04 report; keep both numbers visible (narrow as a diagnostic).

### Pitfall 3: Hand-calc errors break `load_config`
**What goes wrong:** every test and print run fails once `hand_calc.*` is an error while the real config still has 17/7.
**How to avoid:** parameterised severity (Q4), flipped only in BAL-05.

### Pitfall 4: Stale goldens and print during tuning
**How to avoid:** never edit committed config/content before approval; candidate files only; `print --check` is the freshness signal, not a test.

### Pitfall 5: Welle-0 and reference paths depend on measure values
**What goes wrong:** retuning measure costs/CIA/recovery invalidates `practice.check_example` guards and the pinned `reference_plans` (a tier then has no legal in-budget path with a voluntary move → `PrintModelError`).
**How to avoid:** re-run `check_example` and `referenzpfade` as part of the tuning loop's final verification, and budget time for re-choosing the practice selection.

### Pitfall 6: Static vs legal populations
**What goes wrong:** static in-budget median 63 vs legal swap-layer 60; best 98 vs 100; ranking a path-based strategy against the static population is slightly optimistic.
**How to avoid:** report both; decide which one gates (recommendation: Final-Index on static, KZ on the swap layer, both required).

### Pitfall 7: Archetype definitions decide BAL-07
**What goes wrong:** "all-in C" is top quartile today; "buy the bonus measures" is not top quartile in medium/high.
**How to avoid:** define archetypes by algorithm and show placement at D-04; adjust wave weights or archetype definition, not the check.

### Pitfall 8: Near-mandatory by KZ-rank top-N
Covered in Anti-Patterns; use the band.

### Pitfall 9: `MAX_PENALTY_ROWS`
X ≤ 8 needs more than 12 rows (13 at 8, 20 at 5); raise only with a RoS-page layout proof.

### Pitfall 10: Print and story digit rules
Prose cannot contain numbers (allowlist), clue quotes must be verbatim ≥ 15 characters, story text never names measures or the giveaway terms.

## Code Examples

### Hand-friendly exfil slope (candidate value, config only)
```json
"exfil": {"base_severity": 7, "s_unit": 20, "kz_at_full_damage": -5, "kz_at_full_mitigation": 9,
          "cia_impact": {"c": -3, "i": -1, "a": 0}, "mitigation_cap": 7, "allow_recovery": false}
```
Slope (9 − (−5)) / 7 = 2.0. Measured static: X 9 / 4 / 2, median 63 / 65 / 65, best 97 / 100 / 100.

### Final index with integer weights and RoS to two decimals (proposal)
```python
# planspiel/rules.py (single definition; builtin round() forbidden)
def final_index(kz_final, ros, weight_kz, weight_ros):
    if ros is None:
        return weight_kz * kz_final
    return weight_kz * kz_final + weight_ros * round_half_away_frac(ros * 100) / 100
```
Config: `"final_index": {"weight_kz": 1, "weight_ros": 20}`.

### Clue with mapping (proposal)
```toml
[[clue]]
attack = "ot"
source = "story.steckbrief.it_ot_landschaft.ot_produktion.bullets"
quote = "Office-IT und OT/Produktion nutzen dasselbe LAN (kein separates OT-Netz)"
why = "Kein getrenntes Produktionsnetz: ein Vorfall im Büro erreicht die Fertigung."
measures = ["M5"]
weight = 3
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `--budget-utilization 0.85` filtered legacy output | unfiltered summary with top-K, percentiles, Pareto, best in/over budget | Phase 1 | 0.85 hid the true optimum (72 % utilisation) [CITED: .planning/research/PITFALLS.md] |
| Final-Index `KZ + RoS·100` (weights 1/1) | `KZ + k·RoS`, integer k from pooled IQR | Phase 6 | KZ share 0.2 → 0.67 |
| Static-only gate | static + move-path gate, start-lowered trim | Phase 6 | closes the deferred Phase 2 D-25 item |

**Deprecated/outdated:** `balance.py` hard-coded strategy list and the `POSITIVE_KZ_THRESHOLD = 50` constant (replace by `reference_strategies` and the D-10 median-above-start check); `format_factor` fraction fallback once slopes are one-decimal.

## Runtime State Inventory

Not a rename/migration phase; no stored data, live-service config, OS-registered state or secrets are involved. Build artifacts: `final_documents/generated/` (13 PDFs + `manifest.json`, stamp `2026-10-26 · 3878dab`) and `build/print/` go stale on any config or content change and are rewritten only by the BAL-05 plan.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | "raw and capped KZ" in BAL-01 means penalty without floor vs the 0-clamped outcome (`unlosable`) | Q1 | Gate criterion differs from the user's intent; low impact (both are reported) |
| A2 | The start-lowered trim definition is acceptable instead of "same swap pair" | Q2 | X would have to be 15 (low) under the narrow definition; user must see it at D-04 |
| A3 | Final-index formula change to `KZ + k·RoS` with RoS rounded to two decimals and integer `k` | Q6 | Touches `rules.final_index` and one golden; D-15 wording supports it |
| A4 | Clue weight scale 1–3, importance = bonus × slope, graduation rule and floors | Q9 | Check might be too strict/loose; only the planner/user can confirm |
| A5 | Near-mandatory via band (B = 5) with 90 % threshold, corridor ±3, IQR [13, 21], p5–p95 ≤ 50, decision-point ≥ 3 KZ in ≥ 50 % | Q7 | Thresholds are proposals for D-04 approval |
| A6 | Mapping of existing 14 clues to measures and the gap (M6, M2 without clue) | Q9 | Reading of the `why` texts; user confirms |
| A7 | numpy accepted as optional dev dependency for tuning speed | Standard Stack | If refused, tuning is slower (55 s / candidate) but still feasible |
| A8 | Swap + window-2-move family (1.43 bn paths) is not needed for the gate; numpy time about 5 min per tier | Q2 | Phase 2 measured it non-binding (6/3/2) at the old config; may bind after tuning |
| A9 | Which population gates BAL-07 (static FI vs swap-layer KZ) | Q8 | Different pass/fail near the quartile boundary |
| A10 | Measure costs as a lever for near-mandatory (unmeasured) | Q11 | Search may need more levers |

## Open Questions

1. **Trim definition for the move-path gate (A2).** What we know: narrow 14/7/5 vs start-lowered 9/5/2. Unclear: whether the user wants the stricter one. Recommendation: use start-lowered, show narrow as a diagnostic, state it at D-04.
2. **D-11 vs D-12.** What we know: X falls as the top saturates. Unclear: which the user prefers if both cannot hold. Recommendation: the tuning plan prepares both (higher X vs flatter) with measured tables for D-13a.
3. **Near-mandatory for M2 and M7 may need structural levers, not only values.** What we know: both are 100 % in the band today. Unclear: how far costs/CIA/events can move before D-02 plausibility or hand-calculability suffers. Recommendation: first moves on M7 (event swing, CIA per cost), then M2 (OEM membership, wave-3 bonus).
4. **Reference-strategy population (A9).** Recommendation above; planner decides.
5. **Does the user want a Final-Index corridor across tiers?** With k = 20 the best is 124.8 / 118.6 / 114.8 and the median 66 / 71 / 72.
6. **Story edits for M6 and M2 clues.** Needs the user's review at D-04 (wording, veil, no measure names).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| uv | all commands | ✓ | 0.12.5 | — |
| Python 3.12 (managed) | everything | ✓ | via `.python-version` | — |
| LuaLaTeX (MiKTeX) | BAL-05 `planspiel print`, `-m pdf` tests | ✓ | LuaHBTeX 1.25.7, MiKTeX 26.5; `texbuild.preflight()` returns no problems | `print --check` needs no TeX |
| numpy | optional vector engine | ✓ via `uv run --with` | 2.5.4 | stdlib path |
| CPU cores | parallel tier runs | ✓ | 6 | sequential, ≈3× slower |
| jq | (CLAUDE.md suggestion) | ✗ | — | targeted Python (used throughout) |

**Missing dependencies with no fallback:** none. **Missing with fallback:** jq.

## Validation Architecture

Nyquist validation is enabled (`workflow.nyquist_validation: true`).

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (markers `slow`, `pdf`; `addopts = -m 'not slow and not pdf' --strict-markers`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `uv run pytest -q` (measured today: 2,272 tests pass in 125 s; 22 `slow` and 131 `pdf` tests deselected; the 838 warnings are the repeated `HandCalcWarning` for exfil 17/7 and disappear with the slope fix) |
| Full suite command | `uv run pytest -q && uv run pytest -m slow -q` (and `-m pdf` for BAL-05) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test type | Automated command | File exists? |
|--------|----------|-----------|-------------------|--------------|
| BAL-01 | closure/required-X on synthetic columns; path gate equals brute force on mini config; calibrated X = max + 1; real-config path gate per tier | unit + brute force; slow | `uv run pytest tests/test_overspend_gate.py tests/test_gate_paths.py -q`; `-m slow` real | gate: ✅; paths: ❌ Wave 1 |
| BAL-02 | `hand_calc.*` severity parameter; exit codes of `planspiel validate`; candidate with 17/7 fails, fixed passes; real config passes after adoption | unit | `uv run pytest tests/test_validate.py -q` | ✅ extend |
| BAL-03 | `rules.final_index` new form, k from config, no "vorläufig" in report/master; filter flags removed or documented out; analyze/summary consume weights | unit | `uv run pytest tests/test_final_index_config.py tests/test_enumeration.py -q` | ✅ extend |
| BAL-04 | per-tier report: in-budget top-K, Pareto, unfiltered optima, percentile blocks on the mini config; `balance` accepts `--config` | unit + CLI | `uv run pytest tests/test_balance_report.py -q` | ❌ Wave 1 |
| BAL-05 | goldens re-pinned; `print --check` exit 0; print≡sim equivalence; Welle-0 guards; booklet row cap | fast + pdf | `uv run pytest -q`; `uv run pytest -m pdf -q`; `uv run planspiel print --check` | ✅ existing |
| BAL-06 | dominance shares, band near-mandatory, overpowered drop, decision-point effects: synthetic columns + mini brute force; real config via slow test over 782k plans | unit; slow | `uv run pytest tests/test_balance_metrics.py -q`; `-m slow` | ❌ Wave 1 |
| BAL-07 | `reference_strategies` validator + legality; quartile placement function; clue-derived "good" equals algorithm output | unit; slow | `uv run pytest tests/test_reference_strategies.py tests/test_clues_mapping.py -q` | ❌ Wave 1 |
| BAL-08 | median − start ≥ 5 on both layers; comeback metric on mini tables | unit; slow | same as BAL-06 | ❌ Wave 1 |
| BAL-09 | corridor, IQR range, p5–p95 width, D-11 band from summaries | unit; slow | same | ❌ Wave 1 |

Wave-1 checks are expected to FAIL on today's `simulation_config.json` in their slow real-config variants (that is their target); the fast variants run on `tests/fixtures/mini_config.json` and must be green. Mark the failing real-config checks `slow` and either `xfail(strict=False)` with reason "target of Phase 6 tuning" until BAL-05 removes the marker, or keep them out of the default `-m slow` selection until the candidate is adopted; the tuning plan runs them against the candidate through a `--config` option or an environment variable read by a shared fixture.

### Sampling Rate
- **Per task commit:** `uv run pytest -q` (fast suite) plus the touched file.
- **Per wave merge:** fast suite; for tuning iterations the candidate-config report (static layer, ~1 min).
- **Tuning checkpoint (before D-04):** `-m slow` over the candidate: static gate, move-path gate, all BAL metric checks; `uv run planspiel validate --config <cand>`; `uv run planspiel tausch --config <cand>` for legal-layer percentiles.
- **Phase gate:** full suite green, `-m slow` green, `-m pdf` green, `planspiel print --check` exit 0 before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_gate_paths.py` (+ `tests/golden/gate_paths_*.json`), `tests/test_balance_metrics.py`, `tests/test_balance_report.py`, `tests/test_reference_strategies.py`, `tests/test_clues_mapping.py` plus mini-fixture additions (`mini_config.json` reference strategies, `mini_content/clues.toml` mapping keys).
- [ ] A shared way for the slow real-config checks to point at the candidate config (CLI `--config` and a test option), because `tests.support.CONFIG_PATH` is fixed.
- [ ] Decision on numpy (A7) before Wave 2.

## Security Domain

`security_enforcement` is enabled (ASVS level 1). This phase has no network, authentication, session, secret or user-data surface: it is an offline tool chain plus generated documents.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes (config JSON, TOML content, CLI paths) | `planspiel/validate.py` codes with JSON paths, `check_texts`/`check_clues`, `tomllib`/`json` parsers, strict Jinja environment (`render.py`) |
| V6 Cryptography | no (print stamp uses a content hash only) | stdlib `hashlib` in `stamp.py` |
| V12 Files and resources | yes (candidate files, generated PDFs, TeX subprocess) | write only under `--out-dir`/`--build-dir`; `texbuild` runs LuaLaTeX non-interactively; large generated outputs stay gitignored |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed config/clue file crashes tooling or produces wrong print | Tampering | validator errors, `ConfigError`, print preflight; new keys (`reference_strategies`, clue `measures`/`weight`) get validator rules |
| TeX injection through text content | Tampering | `render.tex_escape`, strict templates (existing) |
| Giveaway leakage of attack names to players (veil) | Information disclosure | veil scan in `planspiel print`, giveaway/digit lists (existing) |
| Committing multi-GB enumeration outputs | Denial of service (repo) | `.gitignore`, never read `sim_*.json` whole |

## Sources

### Primary (HIGH confidence)
- This repository at commit state of 2026-10-28 (read and executed): `planspiel/{gate,enumerate,rules,report,balance,analyze,simulate,validate,config,cli,texts,master,fmt,eventtext,booklet,review_text,refpaths,practice}.py`, `simulation_config.json`, `content/{clues,giveaway_terms,digit_allowlist}.toml`, `tests/` layout and fixtures, `README.md`, `CLAUDE.md`, `pyproject.toml`.
- `.planning/phases/06-rebalance/06-CONTEXT.md`, `.planning/REQUIREMENTS.md`, `.planning/phases/02-rule-changes/{02-CONTEXT,02-RESEARCH,02-08-GATE-REPORT}.md`, `.planning/phases/05-player-facilitator-print-material/05-CONTEXT.md`, `.planning/research/PITFALLS.md`.
- Scratch measurement scripts (session scratchpad, not in the repo): vector engine `fast.py` (exact against `TierKernel`), `gatenp.py`, `swapgate.py`, `unionall.py`, `metrics.py`, `search.py`; outputs quoted above.
- `uv run planspiel tausch` (real tooling, all three tiers), `uv run planspiel validate`, `uv run planspiel print --check`.

### Secondary (MEDIUM confidence)
- Phase 2 research M1/M2/M7 tables (re-derived and matched exactly this session).

### Tertiary (LOW confidence)
- Items tagged `[ASSUMED]` (numpy estimate for the 1.43 bn family, threshold proposals, clue weight scale).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH (no new dependency required; numpy optional and flagged)
- Architecture: HIGH for what exists (verified by running it), MEDIUM for the proposed new modules
- Pitfalls: HIGH (each reproduced by measurement)
- Feasibility of D-11 + D-12 together: MEDIUM-LOW (see search evidence)

**Research date:** 2026-10-28
**Valid until:** until `simulation_config.json`, `content/` or `planspiel/rules.py` changes (all numbers are config-specific); re-measure the baseline table first thing in the tuning plan.
