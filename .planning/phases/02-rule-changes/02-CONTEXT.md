# Phase 2: Rule Changes - Context

**Gathered:** 2026-10-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Every rule participants stumbled over at MHP is defined unambiguously, implemented test-first in `planspiel/rules.py` and documented in README (German rule text). Covers RULE-01..08: change-window moves (Levelwechsel up/down, cancel, add) and the Kurswechsel event (incl. its edge cases D-22/D-23), downgrade without refund, a linear overspend penalty with an automated trim-back gate, Sparprogramm handling, an RoS ledger with only the team's own spend, Budget Review boundaries identical in sim and print, and removal of the unprinted E-target bonus/malus.

Numeric values (X, step-reward sizes, slopes) stay provisional until Phase 6. Print templates come in Phases 4/5; this phase only fixes rule definitions, config shape, sim behaviour and README text.

</domain>

<decisions>
## Implementation Decisions

### Carried forward (decided 2026-09-29, PROJECT.md Key Decisions; not re-asked)
- Downgrade allowed: no Init refund, OPEX drops from the next wave.
- Overspend penalty is linear: −X KZ per started 10.000 € over budget; X is a config parameter, provisional until Phase 6.
- Overspend X is checked against the trim-back criterion: every over-budget plan must lose to its own trimmed in-budget version, per tier.
- RoS counts only the team's own spend; event cost effects are excluded in both directions (penalties and discounts).
- An event-induced overrun (Sparprogramm) gets the change window before any penalty.
- Phase 1 rounding rule applies to every new KZ effect: one rounding per wave, half away from zero, then clamp 0..100. `planspiel.rounding.started_steps` is the existing helper for "per started 10.000 €".

### Change-window moves (RULE-01, RULE-02)
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

### Kurswechsel event (RULE-01, RULE-06)
- **D-09:** Kurswechsel (wave-1 event) forces **exactly one Maßnahmentausch** in the change window after wave 1. It comes on top of any normal moves in that window.
- **D-10:** The incoming measure may be introduced at **any level**.
- **D-11:** Cost to the team is **max(0, Init(new measure at chosen level) − Init(dropped measure at its level))**. The customer covers the Init up to the dropped measure's value. A cheaper incoming measure refunds nothing. This is the **only** case where a dropped measure's Init is credited; Init is never refunded anywhere else.
- **D-12:** The Init delta the team pays counts as **own spend in RoS**. The dropped measure's OPEX stops and the new measure's OPEX is paid by the team from the next wave (D-06).
- **D-13:** The printed MHP Kurswechsel text ("Differenz … muss gezahlt werden oder wird ‚erstattet'") is superseded. The config `description` and the README must state D-09..D-11 explicitly. The event type changes from `noop` to a real mechanic the simulation models.
- **D-22:** If a team cannot perform the Maßnahmentausch — no measure was at level 0 in wave 1 (all measures active) or no measure was active in wave 1 — the Kurswechsel has **no effect** for that team. Regular moves in the window stay allowed. The check uses the wave-1 selection. *(Clarified 2026-10-01 in the plan-phase requirements review.)*
- **D-23:** The incoming measure must be **new**: a measure that was at level 0 in wave 1. A measure cancelled earlier in the same window does not qualify (no cancel-and-re-add). The D-11 credit is the Init of the dropped measure at its **wave-1 level**; moves on that measure earlier in the same window do not change the credit. *(Clarified 2026-10-01: not a money exploit either way — the credit only offsets the dropped measure's sunk Init — chosen to keep Maßnahmentausch and Levelwechsel strictly separate and the swap enumeration small.)*

### Overspend penalty and Budget Review (RULE-03, RULE-05, RULE-07)
- **D-14:** "Over budget" is measured **once, at the end**: final remaining budget after all waves and change windows. Teams may go below zero mid-game. RULE-05 (Sparprogramm) is satisfied because the change window after wave 2 lets teams trim before the only check.
- **D-15:** The Budget Review card keeps its **positive tiers** (leftover budget → ±0 / +5 / +10 / +15). The flat "< 0 → −15" tier is **replaced** by the linear penalty −X × started_steps(overspend, 10.000 €). The card prints a lookup table for it.
- **D-16:** **Boundaries use "≥" with round numbers:** at exactly 25.000 / 50.000 / 75.000 € remaining the higher tier applies. The card text is **generated from the tier list**: "0 – 24.999 € → ±0, ab 25.000 € → +5, ab 50.000 € → +10, ab 75.000 € → +15". The MHP wording "25.001–50.000" is superseded. Simulation results for these cases do not change; only the text and tests change. Code review CR-01 is resolved this way, and `test_apply_final_events_boundary_is_inclusive` stays correct.
- **D-17:** X stays a provisional config value in this phase. The trim-back gate (RULE-04) runs per tier in the test suite, reports the minimum X required, and fails, naming the offending plan, if config X is too low.
- **D-18:** **If trim-back requires X > ~5, soften the step rewards** (Exzellenz +5/L3, OEM-Audit tiers, M7 tiers). Do not void bonuses when over budget, do not add a hard overspend cap, and do not accept a steep X. Softening is a value change carried out in Phase 6. In Phase 2 the gate reports the required X, and a value > ~5 is logged as a Phase-6 input in STATE.md, not fixed here.

### E-target bonus/malus (RULE-08)
- **D-19:** **Remove the per-wave E-target KZ bonus/malus from the simulation.** Checked on 2026-10-01: none of the printed MHP material mentions it, so the sim matches what was played. Remove `budget_tiers.*.e_targets`, `waves[].kz_bonus` and `waves[].kz_malus` from the config, the loader, the validator and `rules` (`e_target_check`, the `e_target_delta` term in `wave_kz_change`, and the `TierKernel` memo). Remove `e_target` / `e_reached` / `kz_delta_e_target` from the per-wave records. Log the decision in the PROJECT.md Key Decisions table, as success criterion 5 requires.
- **D-20:** Removing it changes the pinned goldens. Handle this as a **reviewed snapshot change, like Phase 1 (01-06)**: the executor stops at a human-verify checkpoint with an all-combination diff report per tier showing KZ changed counts, best in-budget vs best over-budget before and after, and the in-budget count, which must be unchanged. The goldens are regenerated only through `--update-golden` and committed only after approval.

### RoS ledger (RULE-06)
- **D-21:** Own spend counts in RoS: Init, Init differences from upgrades and adds, regular OPEX (level-dependent per wave once moves exist), and the Kurswechsel delta (D-12). Kept out of RoS but still part of the budget ledger: event OPEX penalties, event OPEX discounts (Operative Unterstützung), event budget deltas (Sparprogramm). Today `evaluate_plan` passes `ledger.total_cost`, which includes event OPEX, into `ros()`. That must split into a security-spend total for RoS and a budget-balance total for the Budget Review and penalty.

### Plan-phase clarifications (2026-10-01, after research; see 02-RESEARCH.md U1–U6)
- **D-24:** **Simulation layers.** The Phase-1 static enumeration stays as the exact, labelled **"reference plan without window moves"** (a legal game only for D-22-exempt plans) and is the basis of the RULE-04 gate. A **swap layer** (every wave-1 plan × each legal Kurswechsel swap) is added as the legal minimum. Reports and summaries label which layer a number comes from; static best results must not be presented as achievable legal results.
- **D-25:** **Provisional X = 9**, one global value (maximum of the measured per-tier minima 9 / 5 / 3, E-target removed). Set in config when the penalty lands (RULE-03); the RULE-04 gate verifies it on static plans. Low tier > ~5 → logged as a Phase-6 input in STATE.md (D-18). The slow gate over move paths (swap/window families, ~10–15 min) is **deferred to Phase 6**.
- **D-26:** **Single term: "Maßnahmentausch"** (one measure out, another in). "Maßnahmenwechsel" is the retired MHP term; README notes the replacement. RULE-01 and ROADMAP SC1 wording updated accordingly.
- **D-27:** **Net pricing within a window:** only each measure's net level change in a window is priced (Init(level at window end) − Init(level at window start) if positive, never a refund); the declared Kurswechsel pair carries the D-11 credit.
- **D-28:** **Swap sub-rules:** the dropped measure ends the window at level 0; the incoming measure's level is its level at window end; a dependent broken by the drop must be lowered or cancelled by the team in the same window (D-07) — the simulation uses the minimal downward repair as canonical.

### Claude's Discretion
- **Definition of the "trimmed in-budget version"** for the trim-back gate. Research defines it precisely and justifies it. The starting point to evaluate is: among all in-budget plans reachable from the over-budget plan by only lowering or cancelling levels, take the best. It must be deterministic, computable per tier within the Phase-1 enumeration bounds, and explainable in one sentence for the debrief.
- **How change-window moves enter the enumeration** (bounded change-path model) and how the gate and reports treat plans with moves. Research flagged this as a key topic. Keep the static-plan enumeration from Phase 1 as the baseline and add move paths only as far as RULE-02/04 need them.
- Config schema for moves, the Kurswechsel mechanic, the penalty X and the generated boundary text. Validator rules for it are new errors and warnings in `planspiel/validate.py`.
- ~~Whether "Maßnahmentausch" or "Maßnahmenwechsel" is the single term (D-08).~~ Decided: D-26.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope and prior decisions
- `.planning/ROADMAP.md` §"Phase 2: Rule Changes": goal, success criteria 1–5, research flag
- `.planning/REQUIREMENTS.md`: RULE-01..RULE-08
- `.planning/PROJECT.md`: Key Decisions (2026-09-29 rule decisions, paper rounding 2026-10-01) and Context (MHP feedback 1–6)
- `.planning/STATE.md`: Blockers/Concerns (step rewards vs X)
- `.planning/research/SUMMARY.md`: open questions 1–6 (X criterion, Sparprogramm, RoS symmetry, downgrade, E-target) and the Phase 2 delivery list
- `.planning/research/FEATURES.md`: T6/T7/T8/T9 and anti-features A4/A6 (refund and flat-band risks)
- `.planning/research/PITFALLS.md`: X calibration being ill-posed, boundary off-by-one, unprinted E-target

### Phase 1 foundation (code this phase builds on)
- `.planning/phases/01-simulation-foundation/01-CONTEXT.md`: D-01..D-30 (exact arithmetic, golden/digest process, over-budget definition, enumeration bounds)
- `.planning/phases/01-simulation-foundation/01-07-SUMMARY.md`: `TierKernel`, `ResultStore`, `budget_ledger`, report and perf bounds
- `.planning/phases/01-simulation-foundation/01-06-SUMMARY.md` and `01-EXACT-SWITCH-DIFF.md`: the reviewed-snapshot procedure to repeat for D-20
- `.planning/phases/01-simulation-foundation/01-REVIEW.md`: CR-01 (resolved by D-16), WR-06/WR-07 (`final_index`, `_tier_lookup` below the lowest tier), relevant when touching those functions

### Rules, config and printed MHP material
- `README.md` §"Change‑Fenster (Planbarkeit + Agency)" and §"Spielablauf", the rule text to rewrite (German)
- `simulation_config.json`: `events.wave_1.kurswechsel` (type `noop` today), `events.wave_2.sparprogramm`, `final_events.budget_review`, `budget_tiers.*.e_targets`, `waves[].kz_bonus/kz_malus`
- `final_documents/Events_Security-Game.pptx`: slide 2 Kurswechsel and slide 9 Budget Review, the MHP wording that D-13/D-16 supersede
- `final_documents/Angriff-1_Ransomware.docx`, `Angriff-2_OT-Störung.docx`, `Angriff-3_Datenexfiltration.docx`: evidence for D-19 (no E-target on the worksheets)
- `final_documents/Budget.docx`: Init only on introduction or upgrade; the budget and status tracker layout
- `final_documents/Return on Security und Final Wert.docx`: the MHP RoS formula that included "Summe Event-Strafen", superseded by D-21

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `planspiel/rules.py`:
  - `budget_ledger` / `BudgetLedger`: the single over-budget definition; extend it to split security spend from budget balance (D-21).
  - `apply_final_events` and `_tier_lookup` / `evaluate_event`: the Budget Review evaluation; add the linear penalty here (D-15).
  - `e_target_check`, `wave_kz_change` and `TierKernel`: what D-19 removes or simplifies.
  - `dependencies_satisfied`: reuse for D-07.
  - `compute_costs`: static `init + opex × waves` today; needs a per-wave, move-aware variant.
- `planspiel/rounding.py`: `started_steps(amount, 10_000)` for the penalty steps; `round_half_away_frac` for any new KZ term.
- `planspiel/validate.py`: the `_Validator` framework (error and warning codes with JSON paths) for the new config keys (X, moves, Kurswechsel).
- `planspiel/enumerate.py`, `planspiel/report.py`, `ResultStore`: Phase-1 bounded enumeration (about 50 s and 125 MB per tier); the trim-back gate should reuse these, not add a second enumerator.
- `tests/support/golden.py`, `harness.py`, `digest.py`, `--update-golden`, `tests/golden/*`: the reviewed-snapshot procedure for D-20.

### Established Patterns
- Every formula exists once in `planspiel/rules.py`, enforced by the AST guard in `tests/test_single_definition.py`. New functions such as the penalty, the security-spend ledger and move costs must be registered there.
- TDD: a RED test commit, then GREEN. Exact `Fraction`/int arithmetic and no built-in `round()`.
- Config first, then README, then print. Config display text is German with real umlauts; ids and keys stay ASCII.
- Snapshot changes are only made through `--update-golden` and need a human review checkpoint (D-20).

### Integration Points
- `evaluate_plan` (`rules.py:437`) and `TierKernel` must stay equivalent; the kernel-conformance digests guard this.
- `ros()` currently receives `ledger.total_cost`, which includes event OPEX; RULE-06 changes this input.
- Root wrappers `simulate_outcomes.py`, `balance_analysis.py` and `analyze_simulation_results.py` keep working (D-26 from Phase 1).

</code_context>

<specifics>
## Specific Ideas

- The user's view of Kurswechsel: "it's an event — the customer pays, so one measure must be changed but at no extra cost; it can be good or bad. It is about the players' strategic thinking." The forced swap is a strategic twist, not a cost trap.
- The Budget Review lookup table and the boundary text must be derivable from config, because the generators in Phases 4/5 print them.
- Research-measured global minimum X (2.21 / 0.83 / 0.39 for low/med/high) is a lower reference. Trim-back will need more; research estimated up to about 34 KZ gained per started 10k near the budget edge because of step rewards.

</specifics>

<deferred>
## Deferred Ideas

- Softening step rewards (Exzellenz/OEM-Audit/M7) if the trim-back X is too high: value change in Phase 6 (D-18).
- Final value of X: Phase 6 calibration.
- Slow trim-back gate over move paths (swap + window-1/window-2 families): Phase 6 (D-25).
- Printing the move rules, the Kurswechsel card, the Budget Review card and the penalty lookup table: Phases 4/5 templates.
- Code review warnings from Phase 1 not touched by this phase's rule work (WR-01..05, WR-08..10): optional `/gsd-code-review 1 --fix`; not part of RULE-01..08.

### Reviewed Todos (not folded)
- `2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md` (veil attacks and events): matched on keywords only. It belongs to Phase 3 (VEIL-01/03) and Phase 5 (VEIL-02/04); the user confirmed it stays there.

</deferred>

---

*Phase: 02-rule-changes*
*Context gathered: 2026-10-01*
