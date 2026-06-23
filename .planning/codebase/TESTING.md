# Testing Patterns

**Analysis Date:** 2026-06-23

## Honest Summary

**There is no automated test suite in this repository.** A repo-wide search found:

- No `test_*.py`, `*_test.py`, or `tests/` directory.
- No `pytest.ini`, `pyproject.toml` `[tool.pytest.ini_options]` block, `conftest.py`, `tox.ini`, or `unittest.TestCase` usage anywhere.
- No CI workflow (`.github/workflows/` does not exist) that would run tests on push/PR.
- No `assert`-based smoke tests embedded in the six Python scripts beyond ordinary control-flow `if`/`return` checks (no `assert` statements used for verification purposes).

Do not invent or assume unit test coverage when planning changes to this codebase — none exists. If a future phase requires automated tests, they would need to be created from scratch (e.g., `pytest` against the pure functions in `simulate_outcomes.py`, which are good candidates since they are deterministic and side-effect-free).

## What Actually Assures Quality Here

Quality assurance in this project happens at two levels: a **deterministic simulation/balance check** (script-driven) and a **human playtest evaluation loop** (document-driven). Both are described below as they actually function today.

### 1. Deterministic Simulation as De Facto Regression Test

**Script:** `/home/user/security-planspiel/simulate_outcomes.py`

- Enumerates every legal combination of measure levels (0-3) per measure (`iter_selections`, `simulate_outcomes.py:442-445`) for a given budget tier, subject to dependency constraints (`dependencies_satisfied`, `simulate_outcomes.py:166-174`) and budget filters.
- For each combination, computes CIA totals, E-values, mitigation, attack severity/damage, KZ trajectory, and cost (`simulate_selection`, `simulate_outcomes.py:355-435`) — entirely deterministic, no randomness, given the current `simulation_config.json`.
- Writes a full results JSON (default `simulation_results.json`) containing every outcome plus a `summary` block.

**Run command:**
```bash
python3 simulate_outcomes.py --config simulation_config.json --budget-tier medium --output simulation_results.json
```
Pre-generated large outputs already exist for low/medium tiers: `/home/user/security-planspiel/sim_low.json`, `/home/user/security-planspiel/sim_med.json` (>10MB — per `CLAUDE.md`, do not read these fully; query with `jq`/Python instead).

**Effective purpose as a "test":** Because the simulation is exhaustive and deterministic, re-running it after any change to `simulation_config.json` (or to the formulas in `simulate_outcomes.py` itself) acts as a full-coverage regression check over the entire decision space — if a change produces nonsensical KZ/damage/cost combinations, they will appear directly in the output.

### 2. Balance/Dominance Analysis as De Facto Integration Test

**Script:** `/home/user/security-planspiel/balance_analysis.py`

- Imports functions directly from `simulate_outcomes.py` (`load_config`, `compute_cia`, `compute_costs`, `simulate_selection`, `dependencies_satisfied`) — `balance_analysis.py:15-18`.
- Defines ~27 hand-curated "strategies" per budget tier (`define_strategies`, `balance_analysis.py:28-261`) representing plausible and intentionally suboptimal team choices, each with a manually pre-computed cost annotated in a comment (e.g. `# 26+36+34+46+16+32=190`).
- Runs each strategy against each budget tier, computes RoS (`calculate_ros`) and a weighted combined score (`calculate_combined_score`: 60% KZ, 30% RoS, 10% inverse damage), and prints per-wave detail plus tier summaries.
- At the end, prints explicit **balance-problem detectors**:
  - KZ distribution check: flags if fewer than 50% of valid outcomes reach KZ ≥ 50 (`balance_analysis.py:416-417`).
  - Budget coverage check: how many of the 27 strategies actually fit each tier's budget (`balance_analysis.py:420-425`).

**Run command:**
```bash
python3 balance_analysis.py
```

**Effective purpose as a "test":** This is the project's stand-in for an integration/acceptance test — it answers "does any single measure or strategy dominate or break the game?" The hardcoded cost comments inside the strategy definitions are themselves a manual cross-check against `simulation_config.json` measure costs; if a measure's `init`/`opex` value changes, these comments will go stale and should be recalculated (there is no automated check that they stay correct — this is a known manual maintenance burden, not a gap to silently ignore).

### 3. Result Summarization

**Script:** `/home/user/security-planspiel/analyze_simulation_results.py`

- Loads a `simulate_outcomes.py` output JSON and a `simulation_config.json` (for baseline loss calculation), and prints top-N/bottom-N outcomes by configurable metric (KZ, RoS, damage, "final index" — a weighted KZ/RoS blend), via `summarize_top`/`summarize_bottom` (`analyze_simulation_results.py:43-48`).
- Not itself a check/assertion tool — it is a reporting aid used by a human to manually eyeball whether top results look sane before finalizing balance.

**Run command (example):**
```bash
python3 analyze_simulation_results.py simulation_results.json --config simulation_config.json
```
(Run with `--help` to see all available sort keys and weighting flags; exact flag names should be confirmed against `parse_args()`/`argparse` setup in the script before use.)

### 4. Mandated Verification Workflow (from `CLAUDE.md`)

Per project instructions, after any content change to measures/attacks/events:

```bash
python3 simulate_outcomes.py --config simulation_config.json --budget-tier <tier> --output simulation_results.json
python3 balance_analysis.py
```

This must be done **before** regenerating print material (`generate_attack_calculator.py`, `generate_from_template.py`, `generate_pptx_cards.py`), so that any introduced dominance/inconsistency is caught before it propagates into player-facing documents.

### 5. Human Playtest Loop (the real-world QA, not code)

This project's actual acceptance testing happens with live human playtests, captured in:

**`/home/user/security-planspiel/BEOBACHTUNGSBOGEN_PLAYTEST.md`** (167 lines) — a facilitator observation form filled out live during a playtest session:
- Timing tracker per phase (Discovery, Budget, Measure selection, each Wave + calculation, each Change window, Debrief) against planned durations (e.g. total planned 150 min).
- Comprehensibility ratings (1-5 scale) for: game goal, budget trade-off, measure selection, dependencies, formulas, E-value concept, events, RoS calculation.
- Engagement tracker (Hoch/Mittel/Niedrig) per phase.
- Free-text fields for most frequently asked questions and observed problems.

**`/home/user/security-planspiel/EVALUIERUNGSPLAN.md`** (562 lines) — the evaluation framework defining what "success" means for a playtest run:
- Target audience, game mode, learning objectives (CIA triad understanding, trade-off thinking, risk-based decision making).
- Success criteria with explicit weights: KZ 60%, RoS 30%, total damage 10% — these weights are the human-facing equivalent of `calculate_combined_score` in `balance_analysis.py`, and the two must be kept in sync if either changes.
- Full worked formulas (CIA totals, E-value, mitigation, damage) restated in prose for facilitators to verify by hand against the code/config.

**`/home/user/security-planspiel/BALANCE_ANALYSE.md`** (264 lines) — the human-readable writeup of `balance_analysis.py`'s output for the finalized parameter set:
- States the design invariant that all budget tiers represent the *same* company facing identical threats (same E-targets 15/17/19, same KZ-start 60, same severity multiplier 1.0) — only budget differs.
- Documents the actual best-strategy result per tier (e.g. Low tier: "Awareness Heavy", KZ=73, Score=71.4) from a run of 27 strategies — this is essentially a checked-in "expected output" snapshot of `balance_analysis.py`, and should be regenerated/updated whenever `simulation_config.json` changes the underlying numbers.

**Loop in practice:** content/balance change → run `simulate_outcomes.py` + `balance_analysis.py` (automated, deterministic) → if results look sane, update `BALANCE_ANALYSE.md` with new findings → conduct/observe a live playtest using `BEOBACHTUNGSBOGEN_PLAYTEST.md` → compare observed timing/comprehension/engagement against `EVALUIERUNGSPLAN.md` targets → feed findings back into `simulation_config.json` and the Markdown rule documents.

## What This Means for Future Work

- If asked to "add tests" for this codebase, clarify scope: there is no existing pytest/unittest convention to extend. A from-scratch test suite would most naturally target the pure functions in `simulate_outcomes.py` (`compute_cia`, `compute_e_value`, `compute_mitigation_from_e_value`, `apply_attack`, `dependencies_satisfied`, `check_event_condition`) since they are deterministic and free of I/O.
- Any change to formulas or default values in `simulate_outcomes.py`/`simulation_config.json` should be validated by re-running `simulate_outcomes.py` + `balance_analysis.py` and diffing against the snapshot in `BALANCE_ANALYSE.md`, not by writing/relying on unit tests that do not exist.
- Do not claim or imply test coverage percentages, CI status, or pytest results in any generated documentation for this repo — none of that infrastructure exists.

---

*Testing analysis: 2026-06-23*
