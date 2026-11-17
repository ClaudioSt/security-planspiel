# Phase 2: Rule Changes - Research

**Researched:** 2026-10-01
**Domain:** Deterministic rules engine for a paper business game (Python 3.12 stdlib, exact arithmetic, full-enumeration verification); rule definitions, change-window path model, overspend gate
**Confidence:** HIGH for the static gate, ledgers, removals and config/validator work (measured and cross-checked against the real kernel); MEDIUM for the bounded path layer (design prototyped and checked against a rules-primitive reference evaluator, runtime extrapolated); the escalation items below are decisions, not facts

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Carried forward (decided 2026-09-29, PROJECT.md Key Decisions; not re-asked)**
- Downgrade allowed: no Init refund, OPEX drops from the next wave.
- Overspend penalty is linear: −X KZ per started 10.000 € over budget; X is a config parameter, provisional until Phase 6.
- Overspend X is checked against the trim-back criterion: every over-budget plan must lose to its own trimmed in-budget version, per tier.
- RoS counts only the team's own spend; event cost effects are excluded in both directions (penalties and discounts).
- An event-induced overrun (Sparprogramm) gets the change window before any penalty.
- Phase 1 rounding rule applies to every new KZ effect: one rounding per wave, half away from zero, then clamp 0..100. `planspiel.rounding.started_steps` is the existing helper for "per started 10.000 €".

**Change-window moves (RULE-01, RULE-02)**
- **D-01:** Allowed moves in the regular change window between waves: **Levelwechsel up**, **Levelwechsel down**, **cancel a measure** (level → 0), and **add a new measure**. There is no free Maßnahmentausch; cancel + add in the same window is allowed and is priced as two separate moves.
- **D-02:** An upgrade or add costs the **Init difference**: Init(new level) − Init(current level), and the full Init of the chosen level for a new measure (current level 0 has Init 0).
- **D-03:** Downgrade and cancel **never refund Init**. OPEX is charged at the new (lower or zero) level from the next wave.
- **D-04:** **No change fee.** Remove the "konfigurierbare Change-Gebühr" sentence from the README change-window section. The README "Kommunikationseffekt" and "Zwangs-Change" bullets are not part of the decided rule set; remove them or mark them as not in use.
- **D-05:** **Unlimited moves per window.** Budget is the only limit.
- **D-06:** **Timing:** a move's CIA, bonus and level effects apply from the next wave. Init differences are booked immediately in the window. OPEX at the new level applies from the next wave.
- **D-07:** **Dependencies must stay valid** after every window. A move that leaves a dependency broken is illegal; the team must fix the dependent measure in the same window. The same `dependencies_satisfied` check as at game start applies.
- **D-08:** Vocabulary, used verbatim in config descriptions and README:
  - **Levelwechsel:** same measure, different level, up or down; cancel is a Levelwechsel to 0.
  - **Maßnahmentausch** (or Maßnahmenwechsel; pick one term and use it everywhere): one measure out, another in. It happens only through the Kurswechsel event.

**Kurswechsel event (RULE-01, RULE-06)**
- **D-09:** Kurswechsel (wave-1 event) forces **exactly one Maßnahmentausch** in the change window after wave 1. It comes on top of any normal moves in that window.
- **D-10:** The incoming measure may be introduced at **any level**.
- **D-11:** Cost to the team is **max(0, Init(new measure at chosen level) − Init(dropped measure at its level))**. The customer covers the Init up to the dropped measure's value. A cheaper incoming measure refunds nothing. This is the **only** case where a dropped measure's Init is credited; Init is never refunded anywhere else.
- **D-12:** The Init delta the team pays counts as **own spend in RoS**. The dropped measure's OPEX stops and the new measure's OPEX is paid by the team from the next wave (D-06).
- **D-13:** The printed MHP Kurswechsel text ("Differenz … muss gezahlt werden oder wird ‚erstattet'") is superseded. The config `description` and the README must state D-09..D-11 explicitly. The event type changes from `noop` to a real mechanic the simulation models.
- **D-22:** If a team cannot perform the Maßnahmentausch — no measure was at level 0 in wave 1 (all measures active) or no measure was active in wave 1 — the Kurswechsel has **no effect** for that team. Regular moves in the window stay allowed. The check uses the wave-1 selection. *(Clarified 2026-10-01 in the plan-phase requirements review.)*
- **D-23:** The incoming measure must be **new**: a measure that was at level 0 in wave 1. A measure cancelled earlier in the same window does not qualify (no cancel-and-re-add). The D-11 credit is the Init of the dropped measure at its **wave-1 level**; moves on that measure earlier in the same window do not change the credit. *(Clarified 2026-10-01: not a money exploit either way — the credit only offsets the dropped measure's sunk Init — chosen to keep Maßnahmentausch and Levelwechsel strictly separate and the swap enumeration small.)*

**Overspend penalty and Budget Review (RULE-03, RULE-05, RULE-07)**
- **D-14:** "Over budget" is measured **once, at the end**: final remaining budget after all waves and change windows. Teams may go below zero mid-game. RULE-05 (Sparprogramm) is satisfied because the change window after wave 2 lets teams trim before the only check.
- **D-15:** The Budget Review card keeps its **positive tiers** (leftover budget → ±0 / +5 / +10 / +15). The flat "< 0 → −15" tier is **replaced** by the linear penalty −X × started_steps(overspend, 10.000 €). The card prints a lookup table for it.
- **D-16:** **Boundaries use "≥" with round numbers:** at exactly 25.000 / 50.000 / 75.000 € remaining the higher tier applies. The card text is **generated from the tier list**: "0 – 24.999 € → ±0, ab 25.000 € → +5, ab 50.000 € → +10, ab 75.000 € → +15". The MHP wording "25.001–50.000" is superseded. Simulation results for these cases do not change; only the text and tests change. Code review CR-01 is resolved this way, and `test_apply_final_events_boundary_is_inclusive` stays correct.
- **D-17:** X stays a provisional config value in this phase. The trim-back gate (RULE-04) runs per tier in the test suite, reports the minimum X required, and fails, naming the offending plan, if config X is too low.
- **D-18:** **If trim-back requires X > ~5, soften the step rewards** (Exzellenz +5/L3, OEM-Audit tiers, M7 tiers). Do not void bonuses when over budget, do not add a hard overspend cap, and do not accept a steep X. Softening is a value change carried out in Phase 6. In Phase 2 the gate reports the required X, and a value > ~5 is logged as a Phase-6 input in STATE.md, not fixed here.

**E-target bonus/malus (RULE-08)**
- **D-19:** **Remove the per-wave E-target KZ bonus/malus from the simulation.** Checked on 2026-10-01: none of the printed MHP material mentions it, so the sim matches what was played. Remove `budget_tiers.*.e_targets`, `waves[].kz_bonus` and `waves[].kz_malus` from the config, the loader, the validator and `rules` (`e_target_check`, the `e_target_delta` term in `wave_kz_change`, and the `TierKernel` memo). Remove `e_target` / `e_reached` / `kz_delta_e_target` from the per-wave records. Log the decision in the PROJECT.md Key Decisions table, as success criterion 5 requires.
- **D-20:** Removing it changes the pinned goldens. Handle this as a **reviewed snapshot change, like Phase 1 (01-06)**: the executor stops at a human-verify checkpoint with an all-combination diff report per tier showing KZ changed counts, best in-budget vs best over-budget before and after, and the in-budget count, which must be unchanged. The goldens are regenerated only through `--update-golden` and committed only after approval.

**RoS ledger (RULE-06)**
- **D-21:** Own spend counts in RoS: Init, Init differences from upgrades and adds, regular OPEX (level-dependent per wave once moves exist), and the Kurswechsel delta (D-12). Kept out of RoS but still part of the budget ledger: event OPEX penalties, event OPEX discounts (Operative Unterstützung), event budget deltas (Sparprogramm). Today `evaluate_plan` passes `ledger.total_cost`, which includes event OPEX, into `ros()`. That must split into a security-spend total for RoS and a budget-balance total for the Budget Review and penalty.

### Claude's Discretion
- **Definition of the "trimmed in-budget version"** for the trim-back gate. Research defines it precisely and justifies it. The starting point to evaluate is: among all in-budget plans reachable from the over-budget plan by only lowering or cancelling levels, take the best. It must be deterministic, computable per tier within the Phase-1 enumeration bounds, and explainable in one sentence for the debrief.
- **How change-window moves enter the enumeration** (bounded change-path model) and how the gate and reports treat plans with moves. Research flagged this as a key topic. Keep the static-plan enumeration from Phase 1 as the baseline and add move paths only as far as RULE-02/04 need them.
- Config schema for moves, the Kurswechsel mechanic, the penalty X and the generated boundary text. Validator rules for it are new errors and warnings in `planspiel/validate.py`.
- Whether "Maßnahmentausch" or "Maßnahmenwechsel" is the single term (D-08).

### Deferred Ideas (OUT OF SCOPE)
- Softening step rewards (Exzellenz/OEM-Audit/M7) if the trim-back X is too high: value change in Phase 6 (D-18).
- Final value of X: Phase 6 calibration.
- Printing the move rules, the Kurswechsel card, the Budget Review card and the penalty lookup table: Phases 4/5 templates.
- Code review warnings from Phase 1 not touched by this phase's rule work (WR-01..05, WR-08..10): optional `/gsd-code-review 1 --fix`; not part of RULE-01..08.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RULE-01 | Levelwechsel vs Maßnahmen(tausch/wechsel) defined unambiguously; Kurswechsel names exactly which move it allows | Vocabulary recommendation (Maßnahmentausch, section "Vocabulary"); `kurswechsel` event type replaces `noop`; leaf functions `swap_possible` / `swap_legal` / `swap_credit` implement D-09..D-11, D-22, D-23; 48,115 of 782,336 valid plans (6.15%) fall under D-22 |
| RULE-02 | Downgrade/cancel/add/upgrade moves modelled; Init sunk, OPEX from next wave | Path model (`Path`/`Window`, per-wave selections, `window_cost`, `evaluate_path`); prototype cross-checked on 2,927 random paths with 0 mismatches; test vectors with config numbers |
| RULE-03 | Linear overspend penalty −X per started 10.000 €, X from config, lookup table printable | `budget_review_delta`, config keys, `started_steps` unit trap (k€ vs €), table generator verified, `ResultStore` gets `kz_pre_review` + `remaining`; measured golden impact for X = 5/9/11 |
| RULE-04 | Automated gate: every over-budget plan loses to its trimmed in-budget version, per tier | Definition, downward-closure DP (stdlib, 2.4-2.6 s per tier), min-X formula, measured X per tier (with and without E-target), driver plans, path-layer families (union alternatives give the same 9 / 5 / 3), gate golden |
| RULE-05 | Event-induced overrun gets the window; penalty only if still over afterwards | D-14 makes the single end check the whole mechanism; measured event-induced overrun counts and window-2 trim feasibility; tests via `evaluate_path`; validator warning for budget-cutting events in the last wave |
| RULE-06 | RoS counts only own security spend; event cost effects excluded both ways | Ledger split (`security_spend` vs budget total), every consumer of `total_cost`/`ros` listed, measured RoS impact (779,900 of 782,335 plans change, max abs 0.1206), invariance property test |
| RULE-07 | Budget Review boundaries identical in print and sim (25k/50k/75k) | Tier-list schema (first minimum 0), generated boundary text + parse-back equivalence test, `_tier_lookup` domain hardening (WR-07), boundary counts at exactly 25/50/75 k |
| RULE-08 | Per-wave E-target KZ bonus/malus resolved against printed MHP material | Removal inventory (every config/loader/validator/rules/kernel/report/test/README location), predicted golden diff numbers for the D-20 checkpoint, legacy Excel generator caveat |
</phase_requirements>

## Summary

Phase 2 is mostly a precise-definition and plumbing phase on top of a solid Phase-1 base, with one genuinely hard modelling problem: the Kurswechsel makes a Maßnahmentausch **mandatory** (D-09), so a static plan is no longer a legal game for 93.85% of valid wave-1 plans (all except the 48,115 plans where D-22 applies). The Phase-1 static enumeration stays exact and cheap and is the right object for the overspend gate required by SC3, but it must be described honestly as the "reference plan without window moves", not as legal play. A bounded path layer (explicit path evaluator plus table-based families: swap-complete pairs, single late moves) represents the minimal legal play and the late-move overspend vectors the gate can also verify (it confirms the static minima, see M7); it is feasible (about 37.3 million swap pairs per tier, roughly 1 µs per path with precomputed per-state tables) but not inside the Phase-1 50 s bound, so it belongs in slow tests.

The trim-back gate has a clean, deterministic definition: for an over-budget plan p, the trimmed version is the best in-budget, dependency-valid plan t with t ≤ p componentwise (levels only lowered or cancelled), where "best" means highest final KZ including its Budget Review bonus; p "loses" iff its final KZ after the penalty (clamped at 0) is strictly lower. It is computed for all plans at once by a prefix-max (downward closure) over the 4^10 level lattice: 10 passes, 2.4-2.6 s per tier in pure Python on top of the existing 37 s kernel enumeration. The minimum integer X is `max(1, floor((kz_pre_review(p) − final(trim(p))) / started_steps(p)) + 1)` over all over-budget p. Measured on the real kernel and cross-checked on a numpy model: **with the E-target bonus/malus still present X = 21 / 5 / 3 (low/medium/high); with it removed (D-19) X = 9 / 5 / 3.** Only a handful of plans set the tier maximum (5 plans of 712,882 need X ≥ 8 in low). Widening the scope to move paths does **not** raise the per-tier minimum: when the alternatives of a path are drawn from the union of the modelled families (static, the Kurswechsel swap pairs, a single move in window 1, a single move in window 2), the required X is again 9 / 5 / 3. Comparing a path family only with its own family gives higher numbers (up to 11 for window-1 single moves in low, 14 for a narrow swap definition), but those are upper bounds, not requirements: richer alternatives (for example a free trim move in window 2) only make an over-budget path lose more easily (swap plus one window-2 move: 6 / 3 / 2). A value of 9 in the low tier exceeds D-18's "~5", so it is logged as a Phase-6 input; the sensitivity run shows that softening Exzellenz/OEM-Audit/M7 alone only gets low to 6, and only flattening all step rewards reaches 4/2/1.

The eight requirements split into eight plans with one shared-infrastructure owner each (see "Requirement-to-Plan Map"). Recommended execution order: RULE-08, RULE-06, RULE-07, RULE-03, RULE-01, RULE-02, RULE-05, RULE-04. That order keeps each human-reviewed golden diff isolated: G1 (RULE-08) changes `kz_final` for 512k-740k plans per tier, G2 (RULE-06) changes only `ros`, G3 (RULE-03) changes only over-budget `kz_final`, and RULE-07/02/05 change no pinned simulation number.

**Primary recommendation:** Keep the Phase-1 static enumeration as the exact baseline and gate (strict definition above, `kz_pre_review` and `remaining` added to `ResultStore`), implement the Kurswechsel and all window moves in one exact `evaluate_path` owned by RULE-02, optionally verify the swap and single late-move families with a table-based slow gate owned by RULE-04 (it should reproduce X = 9 / 5 / 3), set the provisional config X to 9, and resolve the escalation items in "Decisions Needed Before Planning" (especially the static-baseline wording) before plans are written.

## Decisions Needed Before Planning

| # | Decision | Recommendation | Why it matters |
|---|----------|----------------|----------------|
| U1 | What the static baseline represents now that the Kurswechsel swap is mandatory | Keep it as "reference plan without window moves and without the swap", legal only for the 6.15% D-22 plans; add the swap-complete pair family (37.3M paths/tier) as the legal minimum and measure the late-move vectors on top. See "Mandatory Kurswechsel vs the Static Baseline" | Phase 6 balance (BAL-06/08/09) must not treat static best results as achievable legal results: the best swap response beats the static in-budget value by +15 KZ on average |
| U2 | Provisional X in config and gate scope | Config X = **9** (the maximum of the per-tier minima 9 / 5 / 3, a single global X). The static gate (exact, mandatory for SC3) and the optional slow path-layer verification give the same minima, so RULE-03 can land with X = 9 and RULE-04 only verifies. Decide whether the path layer is in Phase 2 or deferred to Phase 6 (it does not change X) | A later X change re-writes the over-budget `kz_final` of 585k-713k plans per tier (G3 again); the path layer costs an estimated 10-15 min of slow-suite time |
| U3 | Vocabulary term | **Maßnahmentausch**; "Maßnahmenwechsel" becomes the retired term. Requires editing RULE-01 and ROADMAP SC1 wording | The MHP confusion came from the suffix collision (Levelwechsel / Maßnahmenwechsel / Kurswechsel) |
| U4 | Window pricing wording | "Within a window only each measure's net level change counts; the declared Kurswechsel pair carries the credit" | D-01 says cancel + add is "two separate moves"; net-change pricing is identical for different measures and strictly cheaper than literal pricing for cancel + re-add of the same measure, which a team would never choose |
| U5 | Legacy `generate_attack_calculator.py` | Accept that running it raises `KeyError` on `kz_bonus`/`kz_malus` after RULE-08 (it is retired, D-29); record it in the RULE-08 plan | Smoke test only imports the module (config load), so tests stay green |
| U6 | Swap sub-rules to state in README | (a) dropped measure ends at level 0; (b) incoming level is its level at window end; (c) a dependent of the dropped measure is lowered or cancelled by the team in the same window (D-07), the simulation uses the minimal downward repair as canonical | Needed so the sim and the paper rule agree on repair |

## Mandatory Kurswechsel vs the Static Baseline

**Facts (all measured, see "Measured Results"):**
- D-09 makes one Maßnahmentausch mandatory in the window after wave 1. D-22 exempts a team only if all ten measures were active or none was. Of 782,336 dependency-valid wave-1 plans, 48,115 (6.15%) are exempt; for the other 734,221 a static plan (no swap) is not a legal play.
- Legal swaps per non-exempt plan: at least 1, mean 50.8 (47.7 over all valid plans), max 75 (A active, B inactive, 3 levels, B's own dependencies must hold, dependents of A lowered minimally). Total 37,300,736 swap pairs per tier. Every non-exempt plan has at least one legal swap.
- The swap is worth a lot on average: for in-budget static plans, the best in-budget swap response beats the static final KZ by +15.35 / +15.35 / +15.11 KZ on average (low/medium/high), better for 97.8% / 97.2% / 96.5% of plans, worse for 0.5% / 0.4% / 0.4% (range −23..+51). The static best in-budget KZ is 98 / 100 / 100; best over all swap paths is 100 in all tiers.
- A bounded model cannot represent all legal play: unrestricted windows can reach any valid state from any state (downgrades are free), so the path space is bounded only by budget, up to roughly (782k)^3 ≈ 5·10^17 paths.

**What the static baseline then represents:** the outcome of a wave-1 plan held unchanged through all waves and the Kurswechsel not applied. It is exact, cheap (≈ 40 s per tier), pinned by the Phase-1 digests, and it is the right object for the SC3 gate. It is a legal game only for D-22 plans. Reports and README must call it "Referenzplan ohne Change-Fenster-Züge" (reference plan without window moves), never "achievable result".

**What it would cost to do more (measured/extrapolated).** The existing dict-based `TierKernel` costs about 47-60 µs per plan (Phase 1: 47 s per 782,336 plans), so even the swap pairs alone would take roughly 30-40 minutes per tier through it (estimate, 37.3M x 47-60 µs); the path layer therefore needs per-state tables and index arithmetic instead of per-path dict evaluation.


| Model layer | Size per tier | Cost | Represents |
|-------------|---------------|------|-----------|
| B1 static reference | 782,336 plans | 37-38 s kernel + 2.5 s closure (measured, pure Python) | Plan without moves; legal for D-22 plans |
| B2 swap-complete pairs (s2 = s1) | 37,300,736 paths | numpy 77-130 s (measured); pure Python ≈ 1 µs/path in a table benchmark, so 40-110 s plus ≈ 60 s table build (estimate) | Minimal legal play for every non-exempt plan |
| B3 B2 + one window-2 move | 1,432,875,008 paths | numpy 35 min per tier with three tiers in parallel (measured); pure Python ≈ 1 h (estimate), not suite-sized | Late-move vectors on top of the swap; own-family alternatives require X = 6 / 3 / 2 (measured) |
| B4 two moves per window | ≈ 28·10^9 and up | infeasible | n/a |
| Exact optimum (DP over state × KZ × budget) | 782k × 101 × ~500 | infeasible | n/a |

**Escalation (U1):** no bounded model represents all legal play, but B1 + B2 + the late-move families (W1/W2/B3) bound it well enough for a rule gate and for Phase 6 comparisons, provided reports label the layers. The measured gate result is robust against the choice of layer: the union of static, swap, W1 and W2 alternatives gives the same per-tier minima as the static gate (9 / 5 / 3). If the user prefers that the Kurswechsel be optional or exactly cost-neutral, that contradicts D-09 and would have to be a new decision; research does not recommend it.

## Architectural Responsibility Map

The project has no web tiers; the relevant tiers are the code and document layers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Rule formulas (penalty, ledgers, window cost, swap) | `planspiel/rules.py` | `planspiel/rounding.py` | Single-definition AST guard: every formula exists once here |
| Config schema and validation (X, step, kurswechsel, tier list) | `planspiel/config.py` + `planspiel/validate.py` | `simulation_config.json` | Config first; validator rejects stale/invalid keys with codes and JSON paths |
| Per-state tables, memoized static kernel, path families | `planspiel/rules.py` (kernel/tables) | `planspiel/enumerate.py` (loops) | The operand-attribute guard forbids `.init/.opex/...` outside rules/config |
| Trim-back gate (closure DP, min X, witnesses) | new `planspiel/gate.py` | `planspiel/cli.py` (`planspiel gate`) | Analysis over the `ResultStore`; not a game formula; reuses the Phase-1 enumeration |
| Generated German boundary text and penalty lookup rows | new small module (e.g. `planspiel/review_text.py`) | Phase 4 `fmt.py` later | Print/README text derived from config, tested against the sim |
| Rule prose (vocabulary, change window, Kurswechsel, Budget Review) | `README.md` | `simulation_config.json` descriptions, root `CLAUDE.md` | README stays symbolic (no fixed numbers); descriptions carry the verbatim vocabulary |
| Snapshot protection | `tests/golden/*`, `tests/support/*` | `--update-golden` + human checkpoint | D-20 precedent from Phase 1 plan 01-06 |

## Project Constraints (from CLAUDE.md)

Extracted from `./CLAUDE.md` and `./.claude/CLAUDE.md` (treated as locked, same authority as CONTEXT decisions):
- Use `uv sync` once; run everything via `uv run python ...` and `uv run pytest` (fast) / `uv run pytest -m slow` (full enumeration). Never use the `python` on PATH (Inkscape's, no packages).
- Order of change: `simulation_config.json` first, then `README.md`, then affected `final_documents/`/print. Do not introduce fixed numbers into prose without reflecting them in the config. README stays symbolic.
- Hand-calculability is a hard criterion: lines on worksheets must be linear and computable by hand (penalty −X × steps qualifies; X must be an integer).
- Balance is verified by full enumeration, not only `balance_analysis.py`.
- Never use Python's built-in `round()` in `planspiel/rules.py` / `planspiel/rounding.py`; exact `Fraction`/int arithmetic; KZ change per wave rounded once (half away from zero), then clamped 0..100.
- Config display strings are German with real umlauts (`tests/test_config_text.py` rejects transliterations such as "massnahm", "ueber", "pruef"); ids and keys stay ASCII.
- `Angriff-*.docx`, `Budget.docx`, `Events_Security-Game.pptx` are print-sync traps; Phase 2 does not edit `final_documents/` (printing is Phases 4/5), but the superseded MHP wording is documented.
- Never read `sim_*.json` / `simulation_*.json` whole; `generate_*.py` are excluded from the single-definition guard (D-29).
- GSD workflow enforcement: file changes go through a GSD command; TDD (RED test commit then GREEN); `workflow.human_verify_mode` is `end-of-phase` in `.planning/config.json`, but D-20 still requires an explicit human-verify checkpoint at each golden regeneration.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python (uv-managed CPython) | 3.12.14 [VERIFIED: `uv run python -c "import sys"`] | Rules, kernel, gate | Project runtime (`.python-version`, `pyproject.toml`) |
| stdlib `fractions`, `array`, `itertools`, `dataclasses`, `typing` | 3.12 | Exact arithmetic, compact arrays, path types | Already the Phase-1 pattern; no new dependency |
| pytest | 9.1.1 [VERIFIED: `uv run python -c "import pytest"`] | Test runner (`-m slow` marker) | Pinned in `pyproject.toml` dev group |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `planspiel.rounding` | in repo | `round_half_away_frac`, `started_steps` | Every new KZ effect and the penalty step count |
| `planspiel.validate._Validator` | in repo | New codes with JSON paths | All new config keys |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Stdlib lattice closure (2.4-2.6 s) | numpy (`np.maximum.accumulate`) | numpy was used only for throwaway research via `uv run --with numpy` (2.5.3); it is not a project dependency, would duplicate formulas outside `rules.py` (violates FOUND-03) and is not needed: the pure-Python gate was cross-checked and is fast enough. Not recommended. |
| Table-based path families in pure Python | numpy vectorisation | numpy is ~10x faster for the swap family but needs a second implementation of the wave formulas; keep one definition. |

**Installation:** none. This phase adds no external packages.

**Version verification:** `uv --version` → 0.12.5; project pins from `pyproject.toml` / `uv.lock` unchanged.

## Package Legitimacy Audit

No external packages are installed or recommended by this phase, so the audit table is not applicable. (numpy was used ephemerally for measurement via `uv run --with numpy` and is not added to `pyproject.toml`/`uv.lock`; if the user ever wants it as a dependency, treat it as `[ASSUMED]` and add a `checkpoint:human-verify` install task.)

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
simulation_config.json ── load_config/validate ──► Config (tiers, waves, events, measures,
                                                    final_budget_tier{tiers, overspend_penalty})
                                                       │
         ┌─────────────────────────────────────────────┴──────────────────────────────┐
         │ planspiel/rules.py (single definition of every formula)                      │
         │                                                                              │
         │  static plan s ──► TierKernel.evaluate ──► CompactOutcome                    │
         │   (782k per tier)    wave k uses s          kz_pre_review, remaining,         │
         │                                             own_cost, total_cost, damage ... │
         │  Path(s0, windows) ─► evaluate_path ─► per-wave selections s_0..s_{W-1}      │
         │   explicit, exact      window_cost (Init diffs, swap credit)                 │
         │                        ledgers: security_spend | budget (adds event OPEX)   │
         │                        kz chain ─► budget_review_delta(remaining) ─► clamp   │
         └───────┬───────────────────────────────────────────┬─────────────────────────┘
                 │                                           │
   enumerate_tier ──► ResultStore (+kz_pre_review, remaining)   TierTables (per-state arrays,
                 │                                           │    built from kernel primitives)
                 ▼                                           ▼
   gate.py: lowering_closure (4^10 prefix-max)      path families: swap pairs, W1, W2 (index
   required X per over-budget plan, witnesses        arithmetic on tables, ~1 µs/path)
                 │                                           │
                 └──────────────► `planspiel gate` report + tests (static: SC3; paths: slow)
   review_text.py: boundary text + penalty rows (from tier list/X) ◄── tests parse text back
```

### Recommended Project Structure

```
planspiel/
├── rules.py        # + kurswechsel leaf functions, window_cost, evaluate_path, budget_review_delta,
│                   #   security_spend; - e_target_check; TierKernel without E-target; TierTables
├── config.py       # - e_targets/kz_bonus/kz_malus; + overspend penalty fields on the final event params
├── validate.py     # + codes below; - e_targets/kz_bonus/kz_malus checks
├── enumerate.py    # ResultStore + kz_pre_review, remaining; path-family loops (use tables only)
├── gate.py         # NEW: lowering_closure, required_penalty_x, GateResult, witnesses (+ path layer)
├── review_text.py  # NEW: boundary_text, penalty_rows (derived from config)
└── cli.py          # + `planspiel gate [--tier T] [--paths]`
tests/
├── test_<per requirement>.py   # see Validation Architecture
├── golden/gate_<tier>.json     # NEW pinned gate result (min X, witness) via --update-golden
└── fixtures/mini_config.json   # updated to the new schema (4 measures: M1, M2, M4, M6)
```

### Pattern 1: Per-wave selections and two ledgers (RULE-02, RULE-06)

**What:** A path is a wave-1 selection plus one `Window` per change window. Wave k (1-based) is resolved with the selection `s_{k-1}`: CIA, bonus, recovery, wave events (including event KZ and Operative Unterstützung) and OPEX all use the selection in force during that wave. The final events evaluate on the last wave's selection. There is no window after the last wave.

```
s_0 = start;  s_k = windows[k-1].selection  (state after window k; missing window = unchanged)
window_cost(a -> b, swap) = sum_m max(0, Init(b_m) - Init(a_m)) - (min(Init(dropped @ a), Init(incoming @ b)) if swap else 0)
init_paid       = Init(s_0) + sum_k window_cost_k
opex_paid       = sum_k Opex(s_{k-1})
security_spend  = init_paid + opex_paid                        # RoS denominator (D-21)
budget_spend    = security_spend + sum_k event_opex(wave k, s_{k-1})
remaining       = tier.budget + sum_k event_budget(wave k) - budget_spend   # Budget Review input (D-14)
kz_k            = clamp(kz_{k-1} + round_half_away(attack_kz_delta(s_{k-1}) + event_kz(k, s_{k-1})))
kz_final        = clamp(kz_W + budget_review_delta(remaining))
```

Dependencies (D-07): `dependencies_satisfied` must hold for every `s_k`; an illegal path is rejected with a reason, not silently repaired. Event KZ and event OPEX must be evaluated per wave with `s_{k-1}`; the Phase-1 `apply_events(wave_id, selection, events)` takes one selection and must be called per wave with the right one (do not reuse the wave-1 selection).

`evaluate_plan(selection)` stays the golden-protected static reference and equals `evaluate_path(Path(selection, ()))` for every plan (conformance test over the mini config and the golden cases).

### Pattern 2: Kurswechsel leaf functions (RULE-01)

Window 1 carries an optional declared pair `swap = (dropped, incoming)`. The swap is required iff the config has a `kurswechsel` event in that wave and `swap_possible(s_0)`:

```python
def swap_possible(selection) -> bool:              # D-22, uses the wave-1 selection
    levels = selection.values()
    return any(level > 0 for level in levels) and any(level == 0 for level in levels)

def swap_legal(wave1, window_end, dropped, incoming) -> bool:   # D-09, D-23
    return (wave1[dropped] > 0 and window_end[dropped] == 0
            and wave1[incoming] == 0 and window_end[incoming] > 0)

def swap_credit(measures, wave1, dropped, incoming, window_end) -> int:
    # D-11 + D-23: credit is Init(dropped at its WAVE-1 level); team pays max(0, Init(incoming) - credit)
    return min(measures[dropped].levels[wave1[dropped]].init,
               measures[incoming].levels[window_end[incoming]].init)
```
`window_cost` already subtracts this credit, so a cheaper incoming measure refunds nothing (the credit is capped at the incoming Init). Test vector from the config: drop M6 L1 (Init 10), incoming M2 L2 (Init 50) → delta 40; drop M5 L3 (Init 110), incoming M8 L2 (Init 36) → delta 0, no refund.

### Pattern 3: Budget Review with the linear penalty (RULE-03, RULE-07)

```python
def budget_review_delta(remaining: int, tiers, penalty_per_step: int, penalty_step: int) -> int:
    if remaining < 0:
        return -penalty_per_step * started_steps(-remaining, penalty_step)   # step in the SAME unit as remaining (k EUR)
    return _tier_lookup(remaining, tiers)        # tiers[0][0] == 0 (validator), raises below the first minimum
```
Applied once after the wave-3 clamp, then clamped again once (this is today's `apply_final_events` order). `remaining == 0` is in budget (tier 0, no penalty). Unit trap: `started_steps(amount_eur, step_eur=10_000)` defaults to euros while the ledger is in k€; with the default step every k€ deficit would count as one step (silent bug). Keep the step in config in k€ (10) and pass it explicitly, or convert both to euros.

### Pattern 4: Trim-back gate (RULE-04)

**Definition (one sentence for the debrief):** "Whoever ends over budget would always have scored higher with the best package reachable by only lowering or cancelling levels that stays within budget."

- Trimmed version `trim(p)` = the in-budget (`remaining >= 0`), dependency-valid plan `t` with `t <= p` (every measure level of t ≤ that of p; t may equal p only if p is in budget, so for over-budget p it is strictly lower somewhere) that maximises `final_kz(t)`; `final_kz(t) = clamp(kz_pre_review(t) + tier_bonus(remaining(t)))` (the positive Budget Review tier of the trimmed plan counts). Ties: lowest own cost, then lowest code index (only affects which witness is named).
- p loses iff `clamp(kz_pre_review(p) - X * started_steps(p)) < final_kz(trim(p))`, strict. If `final_kz(trim(p)) == 0` p cannot lose strictly because of the 0 clamp; the gate must report such plans explicitly (measured count today: 0 in every tier).
- Metric is final KZ (after per-wave clamps and the final clamp), not Final-Index: the penalty is a KZ rule, and Final-Index (weights 1/1 provisional, RoS·100 dominant) gives a meaningless sup of 20.4 / 19.9 / 14.3 (measured), to be revisited with BAL-03. BAL-01's "raw" (unclamped) variant cannot be derived from the stored clamped chain; it needs an unclamped kernel variant in Phase 6.
- Minimum integer X per tier: `X_tier = max over over-budget p of max(1, (kz_pre(p) - final(trim(p))) // steps(p) + 1)`. Config `X` must satisfy `X >= X_tier` for each tier; the failure message names the plan (code, remaining, steps, kz_pre) and its trimmed version with the largest required X (ties: lowest code index). Weak variant (ties allowed) is `ceil(gap/steps)`; report both: 8/4/3 weak vs 9/5/3 strict (E-target removed).
- Algorithm: fill an `array("i")` of size `4**n` with `final_kz(t) * 4**n + code_index` for in-budget valid plans and `-1` otherwise (key < 2^31), run the closure over the full lattice (not just valid plans; order-theoretic, so intermediate invalid plans are irrelevant), then scan over-budget plans. Measured equal to a valid-only single-step search on the current config (0 differing plans), but the full lattice is simpler and config-independent.
- Needs per plan: `kz_pre_review`, `remaining` (and `own_cost` for tie-breaks) → add columns to `ResultStore` (`"B"` and `"h"`, +3 B per record, +2.3 MB per tier). With these, X can be swept without re-enumerating (kz_final of an over-budget plan is `max(0, kz_pre - X*steps)`).

### Pattern 5: Bounded path layer (RULE-04 scope, RULE-02 oracle)

Path families, all with the same definition generalised: for a set of path shapes F, `V_F(t)` = best in-budget final KZ over all F-paths starting at t; the trimmed alternative of an over-budget path from s0 is `max_{t <= s0} V_F(t)` ("lower the start plan, then play the best in-budget continuation"; one closure over `V_F`). The static family is the special case with no moves. Use the **union** of the modelled families for F (it is the faithful reading: a team may lower its plan and then use any modelled move); comparing a family only with itself, or the stricter "narrow" variant (same moves kept, only levels lowered), gives larger numbers that are upper bounds, because the required X is not monotone in the family: a richer alternative set lowers it. Per family keep two small tables per start plan `s0`: `H[s0]` (best in-budget final KZ) and `M[s0][steps]` (maximum `kz_pre_review` of over-budget paths with that step count; steps 1..16 suffice for X >= 3), then X = max over s0, steps of `max(1, (M - prefix_max(H_union)[s0]) // steps + 1)`.

Per-state tables built once per tier from kernel primitives: `valid`, wave KZ change `c1,c2,c3` (array `"b"`), `init`, `opex` (`"h"`), wave-1 event OPEX. A swap path (s0, A, B, l) is index arithmetic: `s1 = s0 - level_A*stride_A + l*stride_B` (then minimal downward repair of dependents of A, validity lookup), cost `init[s0] + (Init(B,l) - credit) + opex[s0] + 2*opex[s1] + event_opex_w1[s0]`, KZ chain from `c1[s0], c2[s1], c3[s1]`. These loops live in `enumerate.py`/`gate.py` but only read the arrays (the operand-attribute guard forbids `.init` etc. outside rules/config).

### Anti-Patterns to Avoid
- **Reusing one selection for all waves in path evaluation:** events (OEM-Audit, M7, Exzellenz, Nervige Authentifizierung) and OPEX depend on the selection of that wave.
- **Storing only `kz_final` with the penalty applied:** the gate then needs a re-enumeration per X. Store `kz_pre_review` and `remaining`.
- **Hand-writing the Budget Review text or lookup table in config/README:** generate from the tier list and X; test by parsing the text back.
- **Pricing moves by literal sequence instead of net change:** see U4.
- **Splitting shared infrastructure across plans:** see ownership table.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| "per started 10.000 €" | `ceil` on floats, `int(x/10)` | `rounding.started_steps` with an explicit step in the ledger's unit | Exact integer ceil; tested at 0, 1, 10, 11 |
| KZ rounding | `round()` | `rounding.round_half_away_frac` | Built-in round() is banker's rounding, forbidden |
| Dependency legality of windows (D-07) | a second dependency checker | `rules.dependencies_satisfied` | Same check as game start |
| Over-budget definition | `total > budget` in new code | `rules.budget_ledger` | Single definition shared by evaluate_plan and kernel |
| Trim-back search | pairwise comparison over 782k × 782k plans | 4^n prefix-max closure | Pairwise is ~10^11; closure is 10 passes |
| Config validation | ad-hoc asserts in loader | `validate._Validator` codes with JSON paths | Phase-1 contract; clean errors |
| Snapshot updates | editing golden JSON | `--update-golden` + human checkpoint | D-20 |
| Boundary text / penalty table | typed strings | generator from config + parse-back test | SC4 |

**Key insight:** the whole game is linear/integer; everything the gate needs (closure, required X, ledgers) is a few lines of exact integer code, and the risk is in definitions and units, not in algorithms.

## Measured Results

All numbers below were produced by throwaway scripts outside the repo (scratchpad `.../scratchpad/research/`, run with `uv run --with numpy python -W ignore <script>` from the project root, except where marked "pure Python"). The numpy model reproduced the real `TierKernel` exactly: 0 mismatches in 20,000 random valid plans per tier on `kz_final`, `total_cost`, damage and `over_budget`, and in-budget counts 69,454 / 124,321 / 197,753 with best in-budget 100 and best over-budget 85 in every tier [VERIFIED: `validate_static.py`]. The path model matched a pure-Python reference evaluator built on `rules.apply_attack/apply_events/compute_cia` on 2,927 random swap / window-1 / window-2 paths with 0 mismatches [VERIFIED: `ref_path.py`].

### M1. Static trim-back X (cells: strict integer X (real supremum; weak integer X))

| Variant | low | medium | high | Command |
|---------|-----|--------|------|---------|
| E-target present (current code) | 21 (20; 20) | 5 (4; 4) | 3 (9/4; 3) | `gate_static.py`; cross-checked in pure Python through the real kernel: `real_gate_check.py <tier>` → 21 / 5 / 3 |
| **E-target removed (D-19)** | **9** (8; 8) | **5** (4; 4) | **3** (9/4; 3) | `gate_static.py` |
| Reference from research: global (not trim-back) minimum | 2.21 | 0.83 | 0.39 | `.planning/research/SUMMARY.md` |

Pure-Python gate cost on the real kernel per tier: enumeration 36.6-37.6 s, closure 2.4-2.6 s, scan 0.2-0.3 s [VERIFIED: `real_gate_check.py`]. Stdlib closure alone: 2.3 s on random data [VERIFIED: `dp_timing.py`].

Driver plans (E-target removed; code digits in config measure order M1..M10):
- low: `1121103000` (spend 340, remaining −10 k€, 1 step) vs trim `1121102000` (remaining +40): kz_pre 91 vs 78 + review +5 = 83, gap 8. Cause: M7 L3 (wave-2 M7 event +7 vs +3, Exzellenz +5 in wave 3, CIA/bonus). Also `1221102000`, `2100133000` (gap 8).
- medium: `1101103113` (remaining −5) vs `1101103111`: M10 L3 adds Exzellenz +5 and CIA, gap 4; also `1110103113`, `1110311013`, `1111013113`, `1200301013`.
- high: `0011311033` (remaining −12, 2 steps) vs `0011311031`; `0111311033` (4 steps, gap 8).
- With E-target present, medium is set by `1110311013` (remaining −9) vs `1110311012` (final 86), also `1200301013`, `1200301103`, `1211330000`, `1301110103` (gap 4); high by the same plans as without the E-target (`0011311033`, `0100330133`, `0101301133`, `0110301133`, `0111300133`, gap 4 over 2 steps).
- With E-target present, low is set by `3300000100` (remaining −4) vs `3200000000` (remaining +100): gap 20: the lowered plan misses the wave-2 and wave-3 E-targets (malus −5 / −7 instead of bonus +7 / +10) while p reaches them, plus Exzellenz +10 vs +5 (wave changes −3 vs −15 in wave 2 and +20 vs −3 in wave 3). That one plan is the reason for X = 21; removing the E-target (D-19) takes most of that gap away and the low-tier minimum falls to 9.

Tail shape (E-target removed): low per-plan strict X histogram `{1: 679,007; 2: 31,617; 3: 1,724; 4: 299; 5: 146; 6: 64; 7: 20; 8: 2; 9: 3}` (5 plans need ≥ 8, 89 need ≥ 6); medium `{1: 651,931; 2: 5,778; 3: 258; 4: 37; 5: 11}`; high `{1: 584,030; 2: 529; 3: 24}`. X is set by a fat tail of a few plans.

### M2. Sensitivity of static X to softened step rewards (Phase-6 input; E-target removed) [VERIFIED: `sensitivity.py`]

| Variant | low | medium | high |
|---------|-----|--------|------|
| current values | 9 | 5 | 3 |
| Exzellenz +3/L3 (or +2, +1, 0) | 9 | 4 | 2 (1 for +1/+0) |
| OEM-Audit 4/5 +3, 5/5 +6 | 8 | 5 | 3 |
| M7 L3 = +4 | 9 | 5 | 3 |
| Exzellenz +2, OEM +3/+6, M7 L3 +4 | 6 | 4 | 2 |
| no Exzellenz, OEM flat above 2, M7 L3 = L2 | 4 | 2 | 1 |

So D-18's softening reaches X ≤ 5 in the low tier only if the step rewards are largely flattened; part of X comes from the attack-mitigation curve and the `bonus_measures` thresholds.

### M3. Golden-impact predictions (E-target removed, current flat −15 review) [VERIFIED: `static_extras.py`]

| | low | medium | high |
|---|-----|--------|------|
| final KZ changed (of 782,336) | 512,006 | 648,246 | 739,828 |
| in-budget count (must be unchanged) | 69,454 | 124,321 | 197,753 |
| best in-budget KZ before → after | 100 → 98 | 100 → 100 | 100 → 100 |
| best over-budget KZ before → after | 85 → 85 | 85 → 85 | 85 → 85 |
| mean KZ shift (after − before) | −8.84 | −12.84 | −16.56 |

Predictions are valid only if RULE-08 is the first golden-changing plan.

### M4. Linear penalty replaces flat −15 (E-target already removed) [VERIFIED: `g3_predict.py`]

| X | low: changed over-budget plans / best over-budget / KZ-0 plans | medium | high |
|---|-------|--------|------|
| 5 | 701,953 / 95 / 451,770 | 643,360 / 95 / 370,118 | 567,069 / 93 / 293,128 |
| 9 | 712,882 / 91 / 606,209 | 658,015 / 91 / 525,877 | 584,583 / 89 / 442,578 |
| 11 | 712,882 / 89 / 634,173 | 658,015 / 89 / 558,185 | 584,583 / 87 / 474,303 |

Best in-budget is 98 / 100 / 100. At X = 9, 85% of over-budget plans floor at KZ 0 (the linear penalty saturates; marginal overspend deterrence ends at the floor).

Max overspend over all plans: 890 / 840 / 790 k€ (89 / 84 / 79 started steps). The lookup table needs only `ceil(100 / X)` rows (12 rows at X = 9) plus a "each further started step −X, KZ never below 0" line. Plans over by ≤ 10 k€ (1 step): 9,417 / 13,264 / 16,794.

### M5. RoS ledger split (D-21) [VERIFIED: `static_extras.py`]

RoS is tier-independent (damage multiplier 1.0). 779,900 of 782,335 plans with own spend > 0 change; the other 2,435 have RoS = −1 (full damage) regardless. Max |ΔRoS| 0.1206, mean (new − old) −0.0326 (the event OPEX discount −2 k€ per active measure currently lowers the cost term). The argmax-RoS plan moves from `0002012210` (1.581) to `0002022200` (1.494); top-100 overlap 93. `ResultStore` already carries `own_cost` and `total_cost`; digests do not contain RoS, so only the characterization goldens change.

### M6. Budget Review boundaries [VERIFIED: `static_extras.py`]

Plans with remaining exactly 25 / 50 / 75 k€: low 735 / 540 / 418, medium 1,148 / 889 / 735 (reproduces CR-01), high 1,549 / 1,285 / 1,148. D-16 keeps the simulation result; only text and tests change.

### M7. Path families (E-target removed; strict integer X low / medium / high)

Definitions: "own" = lower the start plan, then best in-budget continuation drawn only from the same family; "union" = same, but the alternatives come from the union of static, swap, W1 and W2; "narrow" = same moves kept, only levels lowered. Required X is not monotone in the family: a richer alternative set lowers it.

| Family | Paths per tier | own | union (alternatives from static ∪ swap ∪ W1 ∪ W2) | narrow |
|--------|---------------|-----|-----|--------|
| static (no moves) | 782,336 | 9 / 5 / 3 | 4 / 1 / 1 | 9 / 5 / 3 |
| swap-complete pairs (s2 = s1) | 37,300,736 | 9 / 5 / 2 | 9 / 5 / 2 | 14 / 7 / 5 |
| W1: one single-measure move in window 1 (no swap) | 31,293,440 | 11 / 6 / 3 | 9 / 5 / 3 | 12 / 7 / 5 |
| W2: one single-measure move in window 2 (no swap) | 31,293,440 | 9 / 4 / 3 | 5 / 2 / 1 | 11 / 9 / 5 |
| swap + one window-2 move | 1,432,875,008 | 6 / 3 / 2 | not computed | n/a |
| **maximum over the families (union alternatives)** | | | **9 / 5 / 3** | |

W1 and W2 without the swap are not legal for the 93.85% of plans the Kurswechsel applies to; they are modelled as isolated late-move vectors. The union row is the recommended gate definition for the path layer; it equals the static minima.

Commands: `swap_gate.py <tier> 9 0` (swap, own and narrow), `moves_gate.py <tier> W1|W2 9 0` (W1/W2 own and narrow), `swap_w2_gate.py <tier>`, `union_gate.py <tier>` (union; 222 s per tier with three tiers in parallel). Union witnesses: low swap from `1202100002` (kz_pre 96 vs best alternative 88, 1 step), low W1 from `1202101000` (97 vs 89), medium swap from `1100130123` (85 vs 81), high W1 from `1111101123` (89 vs 85, 2 steps). Late-move vectors that make a family-only comparison look worse: low W1 `1220102000` + adding M4 at L1 in window 1 reaches the OEM-Audit 5/5 tier (+15 vs +5 at 4/5) for Init 16 plus two waves of OPEX; low W2 `1101123000` with M2 L1 → L2 in window 2 reaches the wave-3 `bonus_measures` threshold of M2 (min_level 2) for the Init difference plus one wave of OPEX. Two-move combinations were not measured; richer alternatives only lower the requirement, richer over-budget paths (swap + window-1 move) are the open risk (swap + window-2 move measured 6 / 3 / 2).

Pure-Python table benchmark for the swap family: 0.98 µs per path on random tables (no repair/dependency logic), 37.3M paths ≈ 36 s [VERIFIED: `bench_pure.py`; real runtime estimated 2-3x higher, `[ASSUMED]`].

### M8. Sparprogramm (RULE-05) [VERIFIED: `static_extras.py`]

Event-induced overruns (spend ≤ tier budget but > budget − 20): 19,583 / 27,341 / 33,933 static plans, deficits uniform over 1..20 k€. Window-2 can only save wave-3 OPEX (Init never refunded). Cancelling everything in window 2 saves at least the deficit for 100% of them; a single-measure downgrade/cancel returns 67.1% / 73.7% / 80.4% into budget; for those, the cheapest such trim changes final KZ vs staying over at X = 9 by min −23, median −7 / −9 / −9, max +13 / +13 / +9 (negative = trimming gains KZ). Static baseline plans in this set are penalised although a team could still fix them; this is exactly why the static baseline cannot decide RULE-05, the path evaluator must.

### M9. Legal path space and swap lift [VERIFIED: `swap_gate.py`, `swap_enum.py`]

See "Mandatory Kurswechsel vs the Static Baseline". D-22-exempt plans 48,115 (all active or none, valid). Swap pairs 37,300,736 per tier; in-budget / over-budget swap pairs: low 3,587,803 / 33,712,933, medium 6,630,851 / 30,669,885, high 10,699,761 / 26,600,975.

## Requirement-to-Plan Map (one plan per requirement)

Recommended order, owners of shared infrastructure, and dependencies. All plans follow TDD (RED test commit, then GREEN); golden changes only via `--update-golden` + human-verify checkpoint.

| Order | Req | Owns (shared infrastructure) | Depends on | Golden impact |
|-------|-----|------------------------------|-----------|---------------|
| 1 | RULE-08 | E-target removal across config/loader/validator/rules/kernel/report/tests/README; kernel simplification (`change_key` without `e_target_delta`) | none | **G1**: `kz_final` of 512k / 648k / 740k plans per tier (M3); in-budget counts unchanged; digests + characterization |
| 2 | RULE-06 | `security_spend` and the two-ledger `BudgetLedger`; `ros` consumers; WR-06 (`final_index` with `weight_kz`) | 08 only for golden isolation | **G2**: characterization `ros` (+ new `costs` key); digests unchanged because `costs.total` stays the budget total |
| 3 | RULE-07 | Budget Review tier-list schema (first minimum 0), `_tier_lookup` domain error (WR-07), `review_text.boundary_text`, parse-back equivalence test | 08/06 for ordering | none (sim unchanged; config text changes) |
| 4 | RULE-03 | `overspend_penalty` config + validator, `budget_review_delta`, `ResultStore` columns `kz_pre_review`/`remaining`, `review_text.penalty_rows`, provisional X | 07 (tier schema), 08 | **G3**: over-budget `kz_final` (M4); in-budget unchanged |
| 5 | RULE-01 | `kurswechsel` event type (replaces `noop`), vocabulary text, leaf functions `swap_possible`/`swap_legal`/`swap_credit`, validator rules, D-22/D-23 tests | none technical; after 03 to serialise config edits | small: characterization `events[].effect_description` of the Kurswechsel record; digests unchanged |
| 6 | RULE-02 | `Path`/`Window`, `window_cost`, `evaluate_path`, per-wave selections, README change-window rewrite, `evaluate_path == evaluate_plan` conformance | 01 (swap functions), 06 (ledger), 03 (review) | none |
| 7 | RULE-05 | Sparprogramm tests/README sentence, validator warning for budget-cutting events in the last wave | 02, 03 | none |
| 8 | RULE-04 | `gate.py`, `planspiel gate`, `TierTables`, path families (swap/W1/W2), gate golden `tests/golden/gate_<tier>.json`, set/verify X | 03, 08, 02, 01 | none unless the final X differs from RULE-03's (then G3 again, reviewed) |

Cross-requirement notes:
- RULE-06 defines `security_spend(init, opex_by_wave, window_costs=())` so the Kurswechsel delta (D-12) is a window cost; RULE-02's tests assert the delta counts in RoS and event effects do not.
- RULE-03 sets X = 9 from this research (U2) so RULE-04 verifies instead of changing it; RULE-04 must reproduce the M1 numbers (and, if the path layer is in scope, the M7 union numbers) from the real implementation before trusting them.
- The static-gate part of RULE-04 does not need the path evaluator; only its path layer does. The plan can still be sequenced last.
- Sequential execution is advised: all plans edit `simulation_config.json`, `rules.py`, `validate.py` and the same tests.

### Per-plan task outline

**RULE-08 (E-target removal)**
- Config: delete `budget_tiers.*.e_targets`, `waves[].kz_bonus`, `waves[].kz_malus` in `simulation_config.json` and `tests/fixtures/mini_config.json`.
- `config.py`: `Wave.kz_bonus/kz_malus` (lines 36-37), `BudgetTier.e_targets` (63), loader (134, 168-169).
- `validate.py`: remove `kz_bonus`/`kz_malus` `int_field` (330-331) and the `e_targets` block (366-376, code `schema.e_targets`); add warning `schema.removed_key` if a config still carries them.
- `rules.py`: remove `e_target_check` (292-294); `wave_kz_change(attack_kz_delta, event_kz)` (107-109); `simulate_selection` (e_target lookups, 327-329, 351-352, 360); `TierKernel` (`wave_context` fourth element, `_e_target`, `target_key`, `change_key` → `(index, reduction, event_kz)`); `CompactOutcome.e_reached`.
- `enumerate.py`: `STORE_LAYOUT` has no `e_reached` (store format unchanged). `report.dump_record` drops `e_reached` (line 282). `balance.py` lines 334-337 (print of E target).
- Tests/support: `test_kernel_conformance.py` (e_target tests, `_digest_view`), `test_digest.py` (mutates `kz_malus`; choose another field), `test_enumeration.py` (`_outcome(e_reached=...)`, key lists), `tests/support/digest.py` (`e_reached` in `canonical_line`), `harness.py` (`compact_from_plan`), `golden_cases.py` (`census:e_eq_target_w*`, `kz_delta_e_target`), `test_single_definition.py` (`e_target_check` from `FORMULA_FUNCTIONS` → `RETIRED_FUNCTIONS`; `kz_bonus`/`kz_malus` from `OPERAND_ATTRIBUTES`).
- Docs: README (Spielablauf 4c, Kernelemente "E-Ziel", Wellen-Ziel bullet, Tabelle 2 column "E-Ziel erreicht?", Parametrisierung bullets), root `CLAUDE.md` Spielmechanik list, `PROJECT.md` Key Decisions row (SC5), `STATE.md` note.
- Legacy: `generate_attack_calculator.py` reads `wave_data['kz_bonus']/['kz_malus']` (lines 70, 379-380) and would raise `KeyError` when run; it is retired and D-29-excluded; record in the plan (U5). `docs/folienkonzept_spielphasen_mechtech.md` still mentions "E-Ziel-Check" (lines 120-134, 194): out of scope, note for Phase 7 / LEG-02.
- Checkpoint: all-combination diff report per tier (M3 numbers as expected values), then `--update-golden`.

**RULE-06 (RoS ledger)**
- `rules.py`: `BudgetLedger` gains `security_spend`; `budget_ledger(tier_budget, own_cost, event_opex, event_budget)` keeps `total_cost` as budget total (digest-stable); `ros(base_losses, damage, own_spend)`; `evaluate_plan` passes `security_spend` and `outcome["costs"]` gains `security_spend`; kernel `CompactOutcome.own_cost` already is the security spend.
- Consumers: `enumerate.ResultStore.record` (RoS from `own_cost`), `report.summarize_tier` (`ros_cache` keyed by `(damage, own)`, percentile counter filter `own != 0`, `entry()`), `report.dump_record`, `analyze.item_ros` and cost stats (legacy JSON: own = `costs.total - costs.event_opex`, works for old and new files), `balance.py` (prints `rec["ros"]`), `simulate.py` legacy filter keeps using `costs.total` (budget semantics), tests `test_enumeration.py`, `test_rules_semantics.py`, `test_characterization.py`, `test_kernel_conformance.py`.
- Property test: for any mini-config selection, flipping/zeroing all event OPEX/budget effects leaves RoS unchanged; RoS undefined (None) iff own spend 0.
- README: RoS formula block (Gesamtkosten = Init + OPEX je Welle + Kurswechsel-Differenz; keine Event-Effekte), "Simulation" definitions, root `CLAUDE.md` RoS line.
- WR-06 incidental fix with a test using `weight_kz != 1`.

**RULE-07 (Budget Review boundaries)**
- Config `final_events[0]`: tiers `[[0,0],[25,5],[50,10],[75,15]]` (drop the `-100000` sentinel); description keeps only the German intro, the boundary part is generated.
- `_tier_lookup` raises `ValueError` when value < first minimum (WR-07) and the validator requires first minimum 0 for `final_budget_tier` and `checklist_tier` (`schema.tiers_order`).
- `review_text.boundary_text(tiers)` → "0 – 24.999 € → ±0, ab 25.000 € → +5, ab 50.000 € → +10, ab 75.000 € → +15" (verified against the current tier list).
- Equivalence test: parse the generated text (simple regexes) into intervals and compare with `_tier_lookup` for remaining in euros at 0, 24,999, 25,000, 49,999, 50,000, 74,999, 75,000 and the k€ grid −50..200; also for a mutated tier list.
- `test_apply_final_events_boundary_is_inclusive` stays; CR-01 closed.

**RULE-03 (penalty)**
- Config: `overspend_penalty: {"kz_per_step": X, "step": 10}` on the `budget_review` event (k€ units; `step` 10 = 10.000 €). Validator: required for `final_budget_tier` (`schema.event_params`), both positive ints (`schema.range`), warning `hand_calc.penalty_step` if step ≠ 10 (printed wording), optional warning `hand_calc.penalty_x` if X > 5 (D-18 marker).
- `rules.budget_review_delta` + `evaluate_event` branch; `apply_final_events` unchanged order; `ResultStore` columns `kz_pre_review` (`"B"`) and `remaining` (`"h"`), `CompactOutcome.kz_pre_review`, `CompactOutcome.remaining`.
- `review_text.penalty_rows(x, step_eur, ...)` → rows `(from_eur, to_eur, -x*i)` for `i = 1..ceil(100/x)`; boundary tests at deficit 0, 1, 10, 11, 20, 21 k€ and euros 10,000 / 10,001.
- Unit trap and clamp order tests (kz_pre 100 − X·steps, KZ floor 0).
- Golden G3 with checkpoint (M4 numbers at X = 9: all over-budget plans change, best over-budget 85 → 91 / 91 / 89, best in-budget 98 / 100 / 100 unchanged, KZ-0 plans 606,209 / 525,877 / 442,578).

**RULE-01 (Kurswechsel)**
- Config: event type `kurswechsel` (no numeric params), German description stating D-09..D-11 and the chosen term; validator: placement only in `events.wave_k` with k < last wave (`schema.event_placement`), at most one per config (new `schema.kurswechsel_count`).
- `evaluate_event`: `kurswechsel` returns zeros with a fixed description for the static reference ("im Referenzplan nicht angewendet").
- Leaf functions of Pattern 2 + unit tests (D-11 table incl. cheaper/equal/more expensive incoming, D-22 both exempt cases, D-23 re-add forbidden, credit at wave-1 level).
- Vocabulary lint test (config descriptions and README contain "Levelwechsel" and the chosen term and not the retired term; README no longer mentions "Change-Gebühr" etc., that part belongs to RULE-02's README rewrite but the lint test can live here).
- Update ROADMAP SC1 / REQUIREMENTS RULE-01 wording if "Maßnahmentausch" is chosen (U3).

**RULE-02 (moves and path evaluator)**
- `Path`, `Window`, `window_cost`, `evaluate_path`, `PathError` reasons (dependencies, swap legality, level range); README change-window section rewritten (D-01..D-07, remove Change-Gebühr, Kommunikationseffekt, Zwangs-Change; symbolic, no numbers).
- Test vectors: M5 L3 → L1 in window 1: Init 110 stays in spend, OPEX 12 + 2 + 2 = 16 vs static 36, CIA reduced from wave 2; upgrade L1 → L3 pays Init difference; add pays full Init; cancel saves OPEX only; unlimited moves; per-wave event use of `s_{k-1}` (OEM-Audit with the window-1 selection); `evaluate_path(Path(s, ())) == evaluate_plan(s)` for all 256 mini-config plans × tiers and for all golden cases.

**RULE-05 (Sparprogramm)**
- Tests via `evaluate_path`: a plan over budget only because of the −20 k€ event (remaining slightly negative after wave 2 events) has no penalty if window 2 trims it back into budget (saving only wave-3 OPEX, Init never refunded) and the penalty if it does not; remaining negative mid-game but ≥ 0 at the end → no penalty; plan in budget before the event.
- Validator warning (e.g. `rules.event_without_window`) for a negative `flat_budget` event in the last wave (no window follows, D-14 check applies immediately).
- Config description of Sparprogramm may mention the window; README sentence in the Change-Fenster/Budget section.

**RULE-04 (gate)**
- `gate.lowering_closure`, `required_penalty_x`, `GateResult(min_x_strict, min_x_weak, witness, unlosable)`; `planspiel gate --tier T` prints German report (min X, driver plan, trimmed version); fast tests: brute-force pairwise comparison on the mini config (256 plans, all tiers) equals closure result; slow tests: real tiers assert `config X >= min_x` and pin `tests/golden/gate_<tier>.json` (expected 9 / 5 / 3 static).
- Path layer (slow, optional per U2): `TierTables`, families static/swap/W1/W2 with the union-alternatives definition of Pattern 5, pinned expectation 9 / 5 / 3 (M7 union row), conformance of the tables against `evaluate_path` on random paths. swap + window-2 move (1.43 billion paths) stays out of the suite.
- STATE.md: log X > 5 (low tier) as a Phase-6 input (D-18) with M1/M2/M7 numbers.

## Config Schema and Validator

**Config changes**
```json
"final_events": [{
  "id": "budget_review", "name": "Budget Review",
  "description": "Nach Abschluss wird das Restbudget geprüft.",
  "type": "final_budget_tier",
  "tiers": [[0, 0], [25, 5], [50, 10], [75, 15]],
  "overspend_penalty": {"kz_per_step": 9, "step": 10}
}]
"events": {"wave_1": [{"id": "kurswechsel", "name": "Kurswechsel", "type": "kurswechsel",
  "description": "<German text stating D-09..D-11: genau ein Maßnahmentausch ... Kunde übernimmt die Init-Kosten bis zur Höhe der getauschten Maßnahme; keine Erstattung>"}, ...]}
```
(X = 9 per recommendation U2; units k€; `step` 10 = 10.000 €.) No config keys for moves: D-04/D-05 remove fee and limit, so there is nothing numeric to configure.

**New validator codes** (follow the existing `schema.*` / `ref.*` / `hand_calc.*` families in `planspiel/validate.py`):
| Code | Level | Condition |
|------|-------|-----------|
| `schema.event_params` (existing) | error | `final_budget_tier` without `overspend_penalty` |
| `schema.range` (existing) | error | `kz_per_step` or `step` not a positive integer |
| `schema.tiers_order` (existing) | error | first minimum of `final_budget_tier`/`checklist_tier` ≠ 0 (WR-07) |
| `schema.event_placement` (existing) | error | `kurswechsel` in `final_events` or in the last wave |
| `schema.kurswechsel_count` (new) | error | more than one `kurswechsel` event |
| `schema.removed_key` (new) | warning | `e_targets`, `kz_bonus` or `kz_malus` still present |
| `hand_calc.penalty_step` (new) | warning | `step` ≠ 10 (printed wording is per 10.000 €) |
| `hand_calc.penalty_x` (new, optional) | warning | `kz_per_step` > 5 (D-18 marker) |
| `rules.event_without_window` (new) | warning | negative `flat_budget` event in the last wave |

`KNOWN_EVENT_TYPES`: replace `noop` with `kurswechsel` (update `REQUIRED_EVENT_PARAMS`, add `event_kurswechsel` no-op handler, migrate the mini config).

**Single-definition AST guard (`tests/test_single_definition.py`):** register in `FORMULA_FUNCTIONS` (file mapping already supports other modules): `budget_review_delta`, `security_spend`, `window_cost`, `swap_possible`, `swap_legal`, `swap_credit`, `evaluate_path` in `planspiel/rules.py`; `lowering_closure`, `required_penalty_x` in `planspiel/gate.py`; `boundary_text`, `penalty_rows` in `planspiel/review_text.py`. Remove `e_target_check` (add to `RETIRED_FUNCTIONS`). Add operand attributes introduced by the phase to `OPERAND_ATTRIBUTES` (`kz_per_step`, `overspend_penalty`) so only rules/config read them; drop `kz_bonus`/`kz_malus`. Path-family loops must read table arrays, never `.init/.opex/.weights/.bonus`.

## Vocabulary (D-08, Claude's discretion)

Recommendation: **Maßnahmentausch**. Reasoning: the MHP confusion ("Maßnahmenwechsel ≠ Levelwechsel") is a suffix collision: Levelwechsel, Maßnahmenwechsel and the event name Kurswechsel all end in "-wechsel" and differ only in the first part; "Tausch" names the one-out/one-in operation (D-08's own definition) and cannot be mistaken for changing a level. Cost: SC1 and RULE-01 currently use "Maßnahmenwechsel"; update those two texts in the RULE-01 plan (a doc edit) and keep "Maßnahmenwechsel" only as the retired term in the facilitator "Was ist neu" sheet (FLOW-04). The vocabulary lint test enforces single use.

## README and Doc Change Map

README (symbolic, no fixed numbers; German):
- Kernelemente "Wellen": drop "E-Ziel" (RULE-08). "Budget (B)": mention Budget Review and Überziehung symbolically.
- Spielablauf step 4: remove "c) E-Ziel prüfen (KZ-Bonus/Malus)" and renumber; step 5 "Change-Fenster": replace the swap/communication wording with the decided rules (RULE-02/01).
- "Wellen-Ziel (E-Wert) & Scoring": remove "E-Schwelle ... KZ-Bonus/Malus" bullet; fix the Rundung sentence ("Angriff + E-Ziel + Events" → "Angriff + Events"); RoS block (Gesamtkosten = Σ Init + Σ OPEX je Welle + Kurswechsel-Differenz, keine Event-Strafen/-Rabatte).
- "Change-Fenster (Planbarkeit + Agency)": rewrite (D-01..D-07; delete Change-Gebühr, Kommunikationseffekt, Zwangs-Change).
- New short sections "Kurswechsel (Maßnahmentausch)" (D-09..D-13, D-22, D-23) and "Budget Review und Überziehung" (tier rule, penalty −X je angefangene Schrittweite, X/Schrittweite in der Config, einmalige Prüfung am Ende, Sparprogramm-Hinweis).
- Tabellen: Tabelle 1 row "Change-Fenster" (remove "Kommunikation (KZ-Effekt)"), Tabelle 2 column "E-Ziel erreicht?" (remove); Parametrisierung bullets ("E-Ziel/Change-Kommunikation").
- "Simulation (alle Outcomes)": update the definitions of "über Budget", "eigene Kosten" and RoS.
- Root `CLAUDE.md` "Spielmechanik in Kürze" (state machine without E-Ziel-Check, RoS definition). `.planning/PROJECT.md` Key Decisions (E-target decision; update "Pending" rows resolved by the phase). `final_documents/` is untouched (Phases 4/5).

## Runtime State Inventory

Phase 2 removes a mechanic (E-target) and redefines ledgers; it is not a rename, but stale state is possible:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `tests/golden/characterization_*.json` and `digest_*.json` (pin E-target-based KZ and flat −15); ignored `sim_low.json`, `sim_med.json`, `sim_high.json`, `simulation_summary_*.json` (E-target-based outcomes, old RoS) | Regenerate goldens only via `--update-golden` with human checkpoint (G1, G2, G3, minor G1b); treat the ignored dumps as stale, regenerate on demand, never read whole |
| Live service config | None — verified: offline tool, no services | none |
| OS-registered state | None — verified: no scheduled tasks or services reference these names | none |
| Secrets/env vars | None | none |
| Build artifacts | `angriff_berechnung.xlsx` and `generate_attack_calculator.py` encode a KZ bonus/malus from config `kz_bonus`/`kz_malus` (the sheet uses `e_threshold`, not `e_targets`); `final_documents/*` print the superseded MHP Kurswechsel and Budget Review wording | Leave generator untouched (retired, D-29; will `KeyError` if run); `final_documents/` is regenerated in Phases 4/5 |

## Common Pitfalls

### Pitfall 1: Unit mismatch in `started_steps`
**What goes wrong:** `started_steps(deficit_k)` with the default `step_eur=10_000` returns 1 for any deficit up to 10,000 k€; the penalty silently becomes flat −X.
**How to avoid:** config `step` in k€ (10) passed explicitly, or convert to euros; boundary tests at deficits 10 and 11 k€ (1 vs 2 steps) and 10,000 / 10,001 €.
**Warning signs:** every over-budget plan shows the same penalty.

### Pitfall 2: `_tier_lookup` returns the first tier below its domain
**What goes wrong:** after removing the `-100000` sentinel from the Budget Review tiers, `_tier_lookup(-5)` returns `tiers[0][1]` (= 0) instead of a penalty if the negative branch is skipped (WR-07).
**How to avoid:** branch on `remaining < 0` first, make `_tier_lookup` raise below the first minimum, validator requires first minimum 0.

### Pitfall 3: Gate without the clamp awareness
**What goes wrong:** `final(p) = max(0, kz_pre − X·steps)`; if the trimmed final is 0, strict loss is impossible; at X = 9 85% of over-budget plans floor at 0, so a naive "max over-budget KZ < max in-budget KZ" check passes trivially (the original PITFALLS finding).
**How to avoid:** compare against the best trimmed version of each plan (not the tier maximum); count and report `unlosable` plans (0 today); report the strict and weak X.

### Pitfall 4: Golden churn from provisional X
**What goes wrong:** RULE-03 lands with X = a, RULE-04 later sets X = b; the over-budget `kz_final` of 585k-713k plans per tier is re-reviewed.
**How to avoid:** decide U2 first; RULE-03 uses the research value; RULE-04 only verifies (or accepts a documented second G3).

### Pitfall 5: Applying one selection to all waves in path evaluation
**What goes wrong:** window moves have no effect on events/OPEX of later waves; Operative Unterstützung and OEM-Audit read the wrong selection.
**How to avoid:** per-wave selection list, tests with a window-1 upgrade that changes the wave-2 OEM-Audit tier.

### Pitfall 6: Kurswechsel credit and legality edge cases
**What goes wrong:** credit taken at the post-move level (D-23 says wave-1 level); cancelled-then-re-added measure accepted as incoming; swap possible when all measures are active; refund when the incoming measure is cheaper.
**How to avoid:** `swap_legal` checks `wave1[incoming] == 0`; credit = `min(Init(dropped @ wave-1), Init(incoming))`; D-22 tests.

### Pitfall 7: Dependency repair hidden in the sim
**What goes wrong:** dropping M2 invalidates M1/M3/M7 at L3 (dependents of M2: M1 L3 needs M2 ≥ 2, M3 L3 needs M2 ≥ 2, M7 L3 needs M2 ≥ 1); the sim must not silently keep or auto-raise.
**How to avoid:** `evaluate_path` rejects dependency-invalid windows (D-07); the enumeration helpers use the documented minimal downward repair and the incoming measure's own dependencies must hold (U6).

### Pitfall 8: Operand attributes outside rules
**What goes wrong:** table/family code in `enumerate.py` or `gate.py` reads `.init`/`.opex` and fails `test_no_formula_operands_outside_rules_and_config`.
**How to avoid:** build tables inside `rules.py`; loops read arrays.

### Pitfall 9: README with fixed numbers
**What goes wrong:** writing "25.000 €" or the value of X in README violates the "no fixed numbers in prose" rule.
**How to avoid:** README symbolic; numbers only in generated print text.

### Pitfall 10: Removing the E-target breaks golden-case generation
**What goes wrong:** `tests/support/golden_cases.py` tags (`census:e_eq_target_w*`) and `kz_delta_e_target` reads would crash when bootstrapping; digest `canonical_line` includes `e_reached`.
**How to avoid:** update support code in RULE-08; case membership stays stored in the golden files.

### Pitfall 11: Penalty saturation at KZ 0
**What goes wrong:** with large X most over-budget plans land on 0; marginal overspend stops costing anything beyond the floor and percentile reports pile up at 0.
**How to avoid:** document; cap the printed table at `ceil(100/X)` rows; flag for Phase 6 (BAL-09).

## Code Examples

Verified prototypes (stdlib; the closure and `required_x` were checked against a brute-force pairwise search on 200 random 4-measure lattices; the text generator against the current tier list; `[VERIFIED: snippets_check.py]`).

### Lowering closure and required X (RULE-04)
```python
from array import array

def lowering_closure(best, n):
    """best[i] holds value*4**n + index for in-budget plans, -1 otherwise; afterwards best[i] is the
    key of the best in-budget plan t <= i componentwise (axis stride 4**(n-1-j), measure 0 = most significant)."""
    size = 4 ** n
    for j in range(n):
        stride = 4 ** (n - 1 - j)
        for i in range(stride, size):
            if (i // stride) & 3:                      # level of measure j > 0
                lower = best[i - stride]
                if lower > best[i]:
                    best[i] = lower

def required_x(kz_pre, trimmed_final, steps):
    return max(1, (kz_pre - trimmed_final) // steps + 1)   # strict; Python // floors, so negative gaps give 1
```
Usage: `best = array("i", [-1]) * size`; for each in-budget plan `best[code_index] = final_kz * size + code_index`; run the closure; for each over-budget plan `trimmed = best[code_index] // size`, `x = required_x(kz_pre, trimmed, steps)`; the tier minimum is the max, the witness is the argmax (ties → lowest code index). The store's `code_index` already is the lattice index (M1 most significant). Measured 2.4-2.6 s per tier.

### Path evaluator skeleton (RULE-02; prototype matched the numpy model and a primitives-based reference)
```python
def evaluate_path_ref(cfg, tier_name, start, windows, penalty_x):
    tier = cfg.budget_tiers[tier_name]
    sels, spend = [start], init_of(start)
    for sel, swap in windows:                                   # sel = selection after the window
        assert dependencies_satisfied(sel, cfg.measures)        # D-07
        spend += window_cost(cfg, sels[-1], sel, swap)
        sels.append(sel)
    while len(sels) < len(cfg.waves):
        sels.append(sels[-1])
    kz, event_opex, event_budget = tier.kz_start, 0, 0
    for k, wave in enumerate(cfg.waves):
        sel = sels[k]                                           # selection in force during wave k
        attack = apply_attack(sel, cfg.measures, cfg.attacks[wave.attack_id], wave,
                              compute_cia(sel, cfg.measures, cfg.base_cia), cfg.ws, cfg.rs, tier.severity_multiplier)
        ev_kz, ev_budget, ev_opex, _ = apply_events(wave.wave_id, sel, cfg.events)
        kz = clamp_kz(kz + wave_kz_change(attack["kz_delta"], ev_kz))
        spend += opex_of(sel)
        event_opex += ev_opex; event_budget += ev_budget
    security_spend = spend                                      # RoS denominator
    remaining = tier.budget + event_budget - (security_spend + event_opex)
    return clamp_kz(kz + budget_review_delta(remaining, ...)), security_spend, remaining
```

### Boundary text and penalty rows (RULE-07, RULE-03)
```python
def eur(amount):                         # whole euros -> "24.999"
    return f"{amount:,}".replace(",", ".")

def boundary_text(tiers):                # tiers in k EUR, first minimum 0
    parts = []
    for i, (minimum, value) in enumerate(tiers):
        sign = "±0" if value == 0 else f"{value:+d}"
        if i == 0:
            parts.append(f"{eur(minimum * 1000)} – {eur(tiers[1][0] * 1000 - 1)} € → {sign}")
        else:
            parts.append(f"ab {eur(minimum * 1000)} € → {sign}")
    return ", ".join(parts)

def penalty_rows(x, step_eur=10_000, floor_from=100):
    return [((i - 1) * step_eur + 1, i * step_eur, -x * i) for i in range(1, -(-floor_from // x) + 1)]
```
Verified output for the current tier list: `0 – 24.999 € → ±0, ab 25.000 € → +5, ab 50.000 € → +10, ab 75.000 € → +15` (exactly the D-16 text); `penalty_rows(9)` gives `(1, 10000, -9), (10001, 20000, -18), ...`, 12 rows. Implement the number formatting once in a helper that Phase 4's `fmt.py` can absorb; the parse-back test must read the numbers out of the generated string, not out of the tier list.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Flat −15 for any negative budget | Linear −X per started 10.000 € (D-15) | Phase 2 | No exploit of heavy overspend; X fat-tail issue |
| E-target KZ bonus/malus per wave (unprinted) | Removed (D-19) | Phase 2 | Sim equals MHP print; low-tier X 21 → 9 |
| Event OPEX inside RoS cost | RoS on own security spend only (D-21) | Phase 2 | RoS changes for 99.7% of plans |
| `noop` Kurswechsel | Mandatory Maßnahmentausch (D-09) | Phase 2 | Static plan no longer legal play |
| Float arithmetic | Exact ints/Fractions, paper rounding | Phase 1 | unchanged |

**Deprecated/outdated:** README "Change-Gebühr", "Kommunikationseffekt", "Zwangs-Change"; the printed MHP Kurswechsel ("wird erstattet") and Budget Review ("25.001–50.000") wording.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Real pure-Python runtime of the swap/W1/W2 table families is 2-3x the 0.98 µs/path benchmark (≈ 3-5 min per tier including table build) | Mandatory Kurswechsel, M7 | Path layer might need to be sampled or moved to an on-demand script |
| A2 | Swap + one window-2 move needs 15-45 min per tier in pure Python | Mandatory Kurswechsel | If infeasible, B3 stays numpy-only research or sampled |
| A3 | Paths with more moves than measured (two moves per window, swap + window-1 move) do not need X above 9 / 5 / 3, because richer alternatives lower the requirement (swap + window-2 move measured 6 / 3 / 2) | M7 | Gate on a richer family could demand a higher X |
| A4 | Net-change-per-window pricing is what the user means by "priced as two separate moves" (U4) | Decisions | README wording and tests would change |
| A5 | "Dropped measure ends at level 0, incoming level fixed at window end, minimal downward repair" (U6) is the intended swap reading | Decisions | Different legal-swap set and different X for the swap family |
| A6 | One global X (not per tier) is wanted | Pattern 4 | Per-tier X would change the print card |
| A7 | KZ-only metric for the gate is acceptable (Final-Index revisited in Phase 6) | Pattern 4 | Gate would need weights |
| A8 | Maßnahmentausch is preferred to Maßnahmenwechsel | Vocabulary | Doc edits revert |
| A9 | Leaving `generate_attack_calculator.py` broken until Phase 7 is acceptable | U5 | Retired tool would need a `.get()` patch |

## Open Questions

1. **Does the user want path coverage in the Phase-2 gate or only the static gate (U2)?**
   - Known: the per-tier minima are 9 / 5 / 3 for the static gate and for the union of static, swap and single-move alternatives alike.
   - Unclear: whether the user wants the 10-15 min slow path layer in Phase 2 or only in Phase 6.
   - Recommendation: include it as slow verification (pinned expectation 9 / 5 / 3); static gate only is acceptable and loses no X information.
2. **Should reports expose the swap layer (e.g. `best_swap_kz` per plan) in Phase 2?**
   - Known: computable in 40-110 s per tier (estimate).
   - Recommendation: no CLI change in Phase 2; Phase 6 consumes the families.
3. **Is any scenario with a Kurswechsel in a later wave expected (v4 SCEN)?**
   - Recommendation: model the swap in the window after the wave that carries the event (config-driven) even though D-09 says wave 1; validator ensures one event and a following window.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| uv | all commands | yes | 0.12.5 | none needed |
| Python (managed) | rules, tests | yes | 3.12.14 | none needed |
| pytest | tests | yes | 9.1.1 | none needed |
| numpy | research only | yes via `uv run --with numpy` (2.5.3) | not a project dependency | not needed |
| git | commits | yes | repo root `security-planspiel` | none needed |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 [VERIFIED] |
| Config file | `pyproject.toml` (`testpaths = ["tests"]`, `addopts = "-m 'not slow' --strict-markers"`, marker `slow`) |
| Quick run command | `uv run pytest -q` (240 passed, 11 deselected, 14.8 s measured today) |
| Full suite command | `uv run pytest -m slow -q -s` (11 slow tests, 21 min today; Phase 2 adds about 2-3 min static gate and an estimated 10-15 min path layer) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RULE-01 | swap legality/cost (D-09..D-11, D-22, D-23), vocabulary lint, validator placement/count | unit + lint | `uv run pytest tests/test_kurswechsel.py -q` | ❌ Wave 0 |
| RULE-02 | window moves, timing, deps, `evaluate_path == evaluate_plan` (mini all plans, golden cases), vectors | unit + conformance | `uv run pytest tests/test_paths.py -q` | ❌ Wave 0 |
| RULE-03 | penalty at 0/1/10/11/20/21 k€, clamp order, X validator, store columns, lookup rows | unit | `uv run pytest tests/test_budget_review.py -q` | ❌ Wave 0 |
| RULE-04 | closure == brute force (mini); real tiers `config X >= min X`, gate golden; path layer expectations | unit (fast), integration (slow) | `uv run pytest tests/test_overspend_gate.py -q`; `uv run pytest -m slow tests/test_overspend_gate.py -q` | ❌ Wave 0 |
| RULE-05 | event-induced overrun: trim in window 2 → no penalty; untrimmed → penalty; Init never refunded | unit (mini) + slow sample (real) | `uv run pytest tests/test_sparprogramm.py -q` | ❌ Wave 0 |
| RULE-06 | RoS excludes event effects both ways (property), None at own spend 0, store/report/analyze consumers | unit + property | `uv run pytest tests/test_ros_ledger.py -q` | ❌ Wave 0 |
| RULE-07 | boundaries at 24.999/25.000 etc., generated text parsed back equals sim, `_tier_lookup` domain, validator | unit | `uv run pytest tests/test_budget_review_text.py -q` | ❌ Wave 0 |
| RULE-08 | config/records free of E-target keys, validator warning, regenerated digests | unit + slow digests | `uv run pytest tests/test_e_target_removed.py -q`; `uv run pytest -m slow tests/test_digest.py -q` | ❌ Wave 0 (digests exist, regenerated) |

(File names are suggestions; the planner may merge into existing test modules.)

### Sampling Rate
- **Per task commit:** `uv run pytest -q` (≈ 15 s, grows slightly)
- **Per wave merge:** `uv run pytest -q` plus the relevant slow check for the changed layer (`-m slow` on the affected file/tier)
- **Phase gate:** `uv run pytest -m slow` full suite green, `uv run planspiel validate` 0 errors (the known 17/7 warning remains until Phase 6), golden diffs approved, before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] The eight new test modules above (RED first)
- [ ] `tests/fixtures/mini_config.json` migrated to the new schema (no `e_targets`/`kz_*`, `kurswechsel` type, tier list from 0, `overspend_penalty`)
- [ ] Support updates for removed fields (`tests/support/digest.py`, `harness.py`, `golden_cases.py`)
- [ ] Gate golden bootstrap path (`tests/golden/gate_<tier>.json` via `--update-golden`)
- [ ] Framework install: none

## Security Domain

`security_enforcement` is enabled (ASVS level 1). This phase is an offline simulation/tooling change with no network, auth or user data.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | n/a (offline CLI) |
| V3 Session Management | no | n/a |
| V4 Access Control | no | n/a |
| V5 Input Validation | yes | `validate._Validator` (typed fields, ranges, JSON paths); CLI argparse validation; `ConfigError` instead of tracebacks for new keys |
| V6 Cryptography | no | none (digests are SHA-256 for change detection only, not security) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed/hostile config (wrong types, huge values) | Tampering / DoS | Validator rejects non-integers/negatives for X and step; enumeration bound (WR-09 is deferred, keep measure count at 10) |
| Path/file overwrite via `--summary`, `--dump-jsonl` | Tampering | Existing explicit user-chosen paths; no change in this phase (accepted in Phase 1) |
| Regex DoS in the text parse-back tests | DoS | Use simple anchored regexes on short generated strings |

## Sources

### Primary (HIGH confidence)
- Repository code read in full: `planspiel/rules.py`, `enumerate.py`, `report.py`, `config.py`, `rounding.py`, `validate.py`, `simulate.py`, `analyze.py`/`balance.py` (consumers), `tests/test_single_definition.py`, `tests/support/*`, `tests/conftest.py`, `tests/fixtures/mini_config.json`, `simulation_config.json`, `README.md`, root and `.claude/CLAUDE.md`, `pyproject.toml`
- `.planning/phases/02-rule-changes/02-CONTEXT.md` and `02-DISCUSSION-LOG.md`; `.planning/REQUIREMENTS.md`, `STATE.md`, `PROJECT.md`, `research/SUMMARY.md`, `research/PITFALLS.md`; Phase 1 `01-07-SUMMARY.md`, `01-EXACT-SWITCH-DIFF.md`, `01-REVIEW.md`
- Local measurements (scratchpad scripts, commands in "Measured Results"); real-kernel cross-check `real_gate_check.py`; fast suite run `uv run pytest -q` (240 passed)

### Secondary (MEDIUM confidence)
- Extrapolated runtimes for the pure-Python path families (benchmark-based)

### Tertiary (LOW confidence)
- None; no web sources were needed (domain-specific rules over stdlib code; no external library documentation applies)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new packages; stdlib verified
- Architecture: HIGH for static gate/ledger/config; MEDIUM for path layer (validated prototype, extrapolated runtime)
- Pitfalls: HIGH — each tied to code locations or measurements

**Research date:** 2026-10-01
**Valid until:** 2026-10-31 (stable; invalid as soon as `simulation_config.json` values, events or the Phase-1 kernel change)
