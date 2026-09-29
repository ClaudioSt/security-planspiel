# Phase 1: Simulation Foundation - Context

**Gathered:** 2026-09-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the simulation safe to change. Phase 1 delivers:

- one reproducible uv environment;
- characterization tests that pin today's outputs;
- every game formula exactly once in a shared `planspiel/` package, with the root scripts kept as thin wrappers;
- UTF-8 config with real umlauts in display strings;
- exact arithmetic plus one tested rounding helper that matches paper;
- a memory-safe full enumeration per tier that includes over-budget plans;
- a config validator.

Requirements: FOUND-01 … FOUND-07. Rule changes (overspend penalty, RoS ledger, downgrade, E-target bonus) are **not** part of this phase. Phase 1 pins current behaviour, and Phase 2 changes it.

</domain>

<decisions>
## Implementation Decisions

### Paper rounding rule (FOUND-05)
- **D-01:** Rounding happens at exactly one point: each wave's **KZ-Delta is rounded to a whole number**, and the waves are then summed. The E-value, Gesamtreduktion, reduction above threshold and severity stay exact. The E-value always has ≤1 decimal because CIA values are integers and weights have 1 decimal.
- **D-02:** Rounding mode is **kaufmännisch, symmetric (half away from zero)**: +2,5 → +3, −2,5 → −3. Never use Python's `round()`, which rounds half to even. Use `Fraction`/`Decimal` with ROUND_HALF_UP semantics on the absolute value.
- **D-03:** **Damage stays exact in whole euros**, with no rounding. Budget units are thousands, so s_unit × severity (0,1 steps) × (1 − recovery 0,1/0,3/0,5) always ends in whole euros. RoS stays exact.
- **D-04:** The rounding helper is also the single place for the "per started 10.000 €" step logic that Phase 2 will need. Test it at the boundaries (exactly 10.000 €, 10.001 €, 0, negative).
- **D-05:** Sequencing: (1) pin the raw float outputs; (2) refactor into `planspiel/` with **zero snapshot diff**; (3) switch to exact arithmetic plus KZ rounding in a **separate commit** with an explicit, reviewed snapshot diff, in Phase 1 itself.
- **D-06:** Clamp KZ to 0…100 after applying the rounded wave delta, keeping the current order. The planner verifies that the order matches the current code.

### Characterization baseline (FOUND-02)
- **D-07:** A **readable golden JSON per tier** with about 30–50 selections: the named strategies from `balance_analysis.py` `define_strategies`, boundary and dependency edge cases, and a fixed-seed random sample. All output fields are pinned (KZ, per-wave values, damage, costs, event effects, RoS).
- **D-08:** A **full digest** per tier: one hash over the canonical outputs of *all* combinations, which catches regressions the sample misses. It is opt-in via `@pytest.mark.slow` (`uv run pytest -m slow`), and the default `uv run pytest` stays fast.
- **D-09:** Over-budget selections are pinned at the `simulate_selection` level, including today's final-event behaviour (Budget Review −15 for negative remaining budget, event OPEX added to cost). That is the behaviour Phase 2 changes, so it needs a baseline.
- **D-10:** Intentional snapshot changes go through an explicit `uv run pytest --update-golden` flag. It rewrites the golden files and prints a diff summary: selection → field → old → new. The commit message states the reason. Tests never update silently.

### Enumeration report (FOUND-06)
- **D-11:** "Over budget" keeps the **current definition**: `init + opex × waves + event opex > budget + event budget delta`. It lives in one function so that Phase 2 can swap the ledger (RULE-05/06).
- **D-12:** The report shows top-K three ways: **by final KZ, by RoS, by Final-Index**. Final-Index uses the current weights and is labelled provisional until the Phase 6 rescale. Percentiles cover KZ and RoS, split in-budget vs over-budget.
- **D-13:** "Best in-budget vs best over-budget" is compared on **final KZ**, the metric the RULE-04 overspend gate uses.
- **D-14:** The Pareto front is **final KZ vs total own cost**. Report its point count and the front points.
- **D-15:** Output is a small **per-tier JSON summary** (gitignored) plus a short console table. A full per-combination dump (JSONL) is written only on explicit request.
- **D-16:** The **old CLI keeps working**. `simulate_outcomes.py --budget-tier X --budget-utilization 0.85 --output file.json` still writes the full result, since `--output` counts as an explicit request. Without `--output`, the default is the new summary. `--budget-utilization` stays until Phase 6 drops it (BAL-03).
- **D-17:** Aggregation uses **compact in-memory per-combination tuples** (selection code, KZ, own cost, RoS, damage, in/over-budget flag), not true one-pass streaming. The user is getting a RAM upgrade, and tens of MB is fine. Phase 6 reuses the same tuples for its trim-back calibration sweep instead of re-enumerating.

### Refactor scope & cleanup (FOUND-03/04/07)
- **D-18:** The old generators (`generate_pptx_cards.py`, `generate_from_template.py`, `generate_attack_calculator.py`) are **left untouched**. They contain no game formulas and are archived in Phase 7. At most, add a smoke/import check that they still load the umlaut-fixed config.
- **D-19:** FOUND-03's thin wrappers cover `simulate_outcomes.py`, `analyze_simulation_results.py` and `balance_analysis.py`. Their documented commands keep working via `uv run`.
- **D-20:** Umlauts: fix **display strings only** (name/description/text fields, e.g. "OT-Störung", "Geschäftsführung", "Unterstützung"). **Ids and keys stay ASCII** (`operative_unterstuetzung`, `ot`, `M1` …). A test fails if a display field contains a transliteration from an allow-list of known words.
- **D-21:** Validator: **broken references are hard errors on every config load**, so no script runs on a broken config. **Hand-calculability issues are warnings** in Phase 1: non-1-decimal KZ slope (flag wave 3 17/7), `base_severity != mitigation_cap`, `severity_multiplier != 1.0`, weights not summing to 1.0 or having >1 decimal, recovery >1 decimal. Warnings appear in pytest and via a standalone CLI (e.g. `uv run planspiel validate`), and Phase 6 promotes them to errors.
- **D-22:** Repo hygiene is already done: `sim_*.json` and `__pycache__` are untracked and gitignored, so `.planning/codebase/CONCERNS.md` is stale there. No git cleanup in this phase. `angriff_berechnung.xlsx` stays tracked until Phase 7.

### Claude's Discretion
- Python version pin, dependency set and pins in `pyproject.toml`, and `planspiel/` module layout.
- The exact golden-set selection list and random seed, the digest canonicalization format, and the K for top-K.
- Whether arithmetic uses `Fraction` throughout or integer scaling (e.g. weights ×10), as long as results are exact and D-01…D-03 hold.
- Validator CLI naming and the warning output format.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope & requirements
- `.planning/ROADMAP.md` §Phase 1 — goal and 5 success criteria
- `.planning/REQUIREMENTS.md` §Foundation (FOUND-01…07)
- `.planning/PROJECT.md` — constraints (hand-calculability, determinism, single source of truth), Key Decisions table
- `.planning/STATE.md` §Blockers — interpreter trap (`python` on PATH = Inkscape 3.12; use uv)

### Rules & formulas
- `README.md` — current source of truth for rules and formulas
- `CLAUDE.md` (repo root) — mechanics summary, "balance = full enumeration", large-JSON handling rules
- `simulation_config.json` — central config (budget_tiers, waves, attacks, measures, events, final_events)

### Research
- `.planning/research/PITFALLS.md` §Pitfall 6 — float/rounding sim-vs-paper divergence, clean-slope guidance
- `.planning/research/ARCHITECTURE.md` (≈ lines 220–230) — validator invariants and hand-calc checks
- `.planning/research/STACK.md`, `.planning/research/SUMMARY.md` — tooling choices (uv, pytest)

### Codebase maps
- `.planning/codebase/ARCHITECTURE.md`, `CONVENTIONS.md`, `TESTING.md`, `STACK.md`
- `.planning/codebase/CONCERNS.md` — partly stale (repo hygiene already done, see D-22)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `simulate_outcomes.py`: `load_config`, dataclasses (`Attack`, `Wave`, `Measure`, `MeasureLevel`, `BudgetTier`, `Event`), `compute_cia`, `compute_costs`, `compute_recovery`, `compute_e_value`, `compute_bonus_reduction`, `apply_attack`, `evaluate_event`/`apply_events`, `simulate_selection`, `iter_selections`, `run_simulation`. This is the formula core that moves into `planspiel/`.
- `balance_analysis.py` `define_strategies` — named strategies for the golden set. Its inline cost comments are load-bearing sanity checks.
- `analyze_simulation_results.py` — Final-Index = `weight_kz·KZ + weight_ros·RoS·100`, imports from `simulate_outcomes`.

### Established Patterns
- Config-driven dataclasses and snake_case, with domain abbreviations kz/cia/e_value/opex/ros. English identifiers, German user-facing output.
- Budget/cost units in config are thousands of euros (budget 350/400/450).
- `run_simulation` currently: filters out over-budget and below-utilization combos *before* final events, adds event OPEX to total cost, rounds `e_value` only for display (comparison uses the raw value — see Pitfall 6).
- `apply_attack` uses linear KZ interpolation on purpose (see its comment); keep that.

### Integration Points
- Root scripts become thin wrappers over `planspiel/`. `balance_analysis.py` and `analyze_simulation_results.py` import from it.
- The per-combination tuple store (D-17) is the hand-off to Phase 2 (overspend gate, RULE-04) and Phase 6 (calibration).
- The rounding/step helper (D-04) is reused by Phase 2's overspend penalty and Phase 4's print≡sim equivalence test.

</code_context>

<specifics>
## Specific Ideas

- "Rounds like paper" means the exact rule is printable: "KZ-Delta je Welle auf ganze Zahl runden, ab ,5 vom Betrag aufrunden". Phase 4 prints this rule, so the helper name and doc should mirror it.
- The golden diff summary should be domain-readable (selection key, field, old → new), not a raw JSON diff.

</specifics>

<deferred>
## Deferred Ideas

- Dropping `--budget-utilization` / the 0.85 filter and rescaling Final-Index weights → Phase 6 (BAL-03).
- Promoting validator warnings to errors → Phase 6 (BAL-02).
- Redefining the budget/RoS ledger and Budget Review boundaries → Phase 2 (RULE-05/06/07).

### Reviewed Todos (not folded)
- `2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md` (veil attacks/events). It matched on keywords only and is already assigned to Phase 3 (VEIL-01/03) and Phase 5 (VEIL-02/04).

</deferred>

---

*Phase: 01-simulation-foundation*
*Context gathered: 2026-09-29*
