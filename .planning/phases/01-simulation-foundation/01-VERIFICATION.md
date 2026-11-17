---
phase: 01-simulation-foundation
verified: 2026-10-01T12:00:00Z
status: passed
score: 5/5 roadmap success criteria verified (plus all plan-level truths spot-checked)
behavior_unverified: 0
overrides_applied: 0
deferred:
  - truth: "Budget Review awards +5/+10/+15 at exactly 25.000/50.000/75.000 EUR while the printed rule text says 25.001/50.001/75.001 (review finding CR-01)"
    addressed_in: "Phase 2"
    evidence: "Phase 2 success criterion 4: 'Budget Review tiers give the same result in sim and print at the 25k/50k/75k boundaries, with boundary text derived from the tier list' (RULE-07). Pre-existing rule question; Phase 1 only pins the current behavior in goldens, to be regenerated via the explicit --update-golden path."
  - truth: "generate_attack_calculator.py re-encodes the wave formulas as Excel formulas outside planspiel/"
    addressed_in: "Phase 4 / Phase 7"
    evidence: "Documented exception D-29 (tests/test_single_definition.py docstring); Phase 4 generates worksheets from config, Phase 7 LEG-01 moves the Excel calculator and legacy generators to archive/. Not a root simulation script."
---

# Phase 1: Simulation Foundation Verification Report

**Phase Goal:** The maintainer can change simulation code safely. One reproducible environment, current outputs pinned by tests, every formula in one shared module, exact arithmetic, and a memory-safe enumeration that includes over-budget plans.
**Verified:** 2026-10-01
**Status:** passed
**Re-verification:** No, initial verification

Method: SUMMARY claims were not used as evidence. I made a fresh `git clone` into the scratchpad and ran the suite there, executed the documented commands, ran the full per-tier enumeration, ran the slow kernel-digest and perf tests, mutated a config to test the validator, and read the code.

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Fresh clone: one command sets up the environment, `uv run pytest` passes, every documented script runs via `uv run` whichever `python` is on PATH | VERIFIED | `git clone` into scratchpad; `which python` = `/c/Program Files/Inkscape/bin/python` (Inkscape's, first on PATH); `uv sync --locked` ok; `uv run --locked pytest -q` gave `240 passed, 11 deselected in 17.68s`. `uv run python simulate_outcomes.py --help`, `analyze_simulation_results.py --help` exit 0. `balance_analysis.py` ran to completion (exit 0, 624 lines). `uv run planspiel --help` and `planspiel validate` exit 0. `pyproject.toml` has `python-preference = only-managed`, `.python-version` = 3.12, `uv.lock` committed. README/CLAUDE.md contain no `python ...` command without `uv run`; the only grep hits were prose. |
| 2 | Characterization tests pin KZ, damage, costs, RoS per selection and tier and pass against refactored code; every formula exists once in `planspiel/`; root scripts are thin wrappers; exact-arithmetic deviations are an explicit reviewed snapshot change | VERIFIED | `tests/golden/characterization_{low,medium,high}.json` hold 62 cases each (keys: `selection, kz_final, total_damage, costs, over_budget, ros`, per-wave values), stage `exact-rounded`; `digest_*.json` pin sha256 plus counts and KZ histogram over all 782,336 combinations per tier. Fast characterization tests pass in the fresh clone. I ran the slow `test_kernel_conformance.py` digest tests: 3 passed (kernel equals the pinned digest over every combination, all tiers). `simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py` are 6-line wrappers (read in full). `tests/test_single_definition.py` AST-enforces 30 formula functions defined once in `rules.py`/`rounding.py`, retired scorers gone, no operand attributes outside rules/config; it passes. No `round(` and no float arithmetic in `rules.py`/`rounding.py` (grep). Float-to-exact change: one dedicated commit `0d342f6` with `01-EXACT-SWITCH-DIFF.md` (all 3 x 782,336 combinations compared: 0 E-target flips, 0 over-budget flips, 0 damage changes > 0.5 EUR, max KZ shift 1.22), user-approved 2026-10-01. Pre-refactor float goldens were committed first (`6b9e255`, `d4b2fa6`) and plan 04's refactor produced zero diff. |
| 3 | Config loads as correct German text; rounding/step helper right at 10.000, 10.001, zero, negative | VERIFIED | `simulation_config.json` contains "früh", "OT-Störung"; 0 occurrences of mojibake "Ã". `tests/test_config_text.py` and `tests/test_encoding_lint.py` (AST lint: every text-mode open/read_text/write_text declares `encoding=`) pass on this cp1252 machine. `planspiel/rounding.py`: `started_steps(10_000)=1`, `10_001 -> 2`, `0 -> 0`, `-5_000 -> 0` (parametrized in `tests/test_rounding.py`); `round_half_away` verified for +-2.5, +-5.5, 11.5 and for ties. |
| 4 | Full enumeration per tier incl. over-budget finishes without exhausting memory; reports top-K, percentiles, best in vs over budget, Pareto count; dump only on explicit request | VERIFIED | `uv run python simulate_outcomes.py --budget-tier low`: 782,336 valid, 69,454 in budget, 712,882 over budget (equals pinned digest), 43.8 s, 16 B per combination. Output shows top-K x3, nearest-rank percentiles (in/over budget), best in vs over budget (100 vs 85, -15), Pareto front (22 points). Summary JSON keys: `top, percentiles, best, pareto, combinations`. No `simulation_full*.jsonl` written without `--dump-jsonl`. Slow perf tests `-m slow tests/test_enumeration_perf.py -k summary_run`: all three tiers pass, peak RSS 121 / 129 / 125 MB (bound 500 MB), 43-44 s (bound 120 s). |
| 5 | Validator rejects broken reference; warns on hand-calculability, flagging wave-3 KZ slope 17/7 and `base_severity != mitigation_cap` | VERIFIED | Mutated config (`M99` as bonus measure): `planspiel validate` prints `ERROR ref.unknown_measure waves[0].bonus_measures[0].measure: Unbekannte Maßnahme 'M99'`, exit 1; `simulate_outcomes.py` with that config raises `ConfigError` and does not run (rejected on every load). Real config: `WARN hand_calc.kz_slope attacks.exfil: KZ-Steigung 17/7 ... (verwendet in Welle 3)`, exit 0. `check_hand_calc` in `planspiel/validate.py:543` emits `hand_calc.severity_cap` when base_severity differs from mitigation_cap; covered by `test_validate.py` mutation (`base-severity-not-cap`). 17 error mutations and 6 warning mutations are tested. |

**Score:** 5/5 roadmap truths verified; 0 present-but-behavior-unverified.

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|--------------|----------|
| 1 | Budget Review tier boundaries differ from printed text at 25k/50k/75k (review CR-01) | Phase 2 (RULE-07, SC 4) | Phase 2 SC 4 names exactly these boundaries. Phase 1 pins current behavior only; the golden update path makes the later change an explicit snapshot diff. |
| 2 | `generate_attack_calculator.py` duplicates formulas as Excel formulas | Phase 4 / Phase 7 (LEG-01) | Documented exception D-29, excluded from the single-definition scan by design. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml`, `uv.lock`, `.python-version` | uv project, pins, console script, slow marker | VERIFIED | Present, `planspiel = "planspiel.cli:main"`, `addopts = "-m 'not slow'"`, fresh-clone sync passes with `--locked`. |
| `planspiel/rules.py` (564 lines) | All formulas once, exact arithmetic, kernel | VERIFIED | Substantive and wired (used by simulate, analyze, balance, enumerate, report, tests). |
| `planspiel/rounding.py` | `round_half_away`, `started_steps`, `exact_to_json` | VERIFIED | Integer-only arithmetic, tested. `started_steps` has no production caller yet (review IN-10; Phase 2 groundwork, not a gap). |
| `planspiel/config.py`, `validate.py`, `cli.py` | UTF-8 load, validate on every load, `planspiel validate` | VERIFIED | Behavior confirmed by execution above. |
| `planspiel/enumerate.py`, `report.py`, `simulate.py` | Compact store, summary report, default summary mode | VERIFIED | Output and bounds confirmed by execution. |
| `planspiel/analyze.py`, `balance.py` | Logic behind wrappers | VERIFIED | `analyze_simulation_results.py --input sim_low.json` ran in 5 s, exit 0; `balance_analysis.py` exit 0. |
| `tests/golden/*.json` (6 files) | Characterization + digests | VERIFIED | Present, stage `exact-rounded`. |
| `tests/test_*.py` (16 files) | Test suite | VERIFIED | 240 fast tests pass in fresh clone. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `pyproject.toml` | `planspiel/cli.py` | `[project.scripts]` | WIRED | `uv run planspiel --help` works from repo root. |
| root wrappers | `planspiel.{simulate,analyze,balance}.main` | import + main guard | WIRED | Read in full; `tests/test_wrappers.py` passes. |
| `load_config` | `validate.check_config` | called on every load | WIRED | Broken config rejected by all entry points (checked simulate). |
| `evaluate_plan` / `TierKernel` | `budget_ledger`, `e_target_check`, `apply_final_events` | shared helpers in `rules.py` | WIRED | Kernel digest equals golden digest (slow test run). |
| `simulate.main` | `enumerate_tier` -> `report` | summary default mode | WIRED | CLI run produced report and JSON. |

### Data-Flow Trace (Level 4)

Not applicable: no UI or rendering artifacts. The data path (config -> rules -> enumeration -> report) was exercised end to end; counts equal the golden digest.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Fresh-clone suite | `uv run --locked pytest -q` (clone, Inkscape python first on PATH) | 240 passed | PASS |
| Full enumeration, low | `uv run python simulate_outcomes.py --budget-tier low --summary ...` | 782,336 / 69,454 / 712,882, 43.8 s | PASS |
| Kernel = pinned digest | `uv run pytest -m slow tests/test_kernel_conformance.py` | 3 passed (170 s) | PASS |
| Memory/time bounds | `uv run pytest -m slow tests/test_enumeration_perf.py -k summary_run` | 3 tiers pass, peak 121-129 MB | PASS |
| Validator rejects broken ref | `planspiel validate --config broken.json` | exit 1, `ref.unknown_measure` | PASS |
| Validator warns 17/7 | `planspiel validate` | `hand_calc.kz_slope ... 17/7`, exit 0 | PASS |
| Legacy analyze on 131 MB file | `analyze_simulation_results.py --input sim_low.json` | exit 0 in 5 s (review IN-08 not a practical problem for this file) | PASS |

I did not re-run the full slow suite (about 20 min); the three slow groups above give independent evidence for kernel exactness and bounds, and the SUMMARYs quote full runs.

### Probe Execution

SKIPPED: the phase declares no probe scripts (`scripts/*/tests/probe-*.sh` absent, none in PLAN/SUMMARY).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FOUND-01 | 01-01 | One-command uv environment | SATISFIED | SC 1 evidence. |
| FOUND-02 | 01-03 | Characterization tests pin KZ, damage, costs, RoS | SATISFIED | SC 2: golden + digests, pre-refactor commits `6b9e255`/`d4b2fa6`. |
| FOUND-03 | 01-04 | Every formula once in `planspiel/`, thin root wrappers | SATISFIED | AST test passes; wrappers 6 lines. Excel calculator generator exempt by documented D-29. |
| FOUND-04 | 01-02 | UTF-8 everywhere, real umlauts/ß | SATISFIED | SC 3 evidence. |
| FOUND-05 | 01-06 | Exact arithmetic, one rounding/step helper | SATISFIED | SC 2/3 evidence; `rules.py` has no float arithmetic or `round(`. |
| FOUND-06 | 01-07 | Bounded full enumeration incl. over-budget, compact aggregates, dump on request | SATISFIED | SC 4 evidence. |
| FOUND-07 | 01-05 | Validator: broken references and hand-calculability | SATISFIED | SC 5 evidence. |

All seven IDs are claimed by exactly one plan each (01-01..01-07) and match REQUIREMENTS.md and its traceability table (all marked Phase 1 / Complete). No orphaned requirements.

### Anti-Patterns Found

Grep of `planspiel/`, `tests/`, wrappers, `pyproject.toml`, README, CLAUDE.md for `TBD|FIXME|XXX|TODO|HACK`: no debt markers (one hit is the filename `TODO.md` in prose). No stub implementations.

### Code Review Findings vs. Success Criteria

`01-REVIEW.md` (1 critical, 10 warnings, 10 info) was read against each criterion. None falsifies a success criterion:

- **CR-01** (Budget Review inclusive boundary vs. printed text): pre-existing rule question, belongs to Phase 2 SC 4 / RULE-07; Phase 1's goal is to pin current behavior. Deferred, see above. Needs a user rule decision in Phase 2.
- **WR-01 (cp1252/BOM config tracebacks), WR-02, WR-03, WR-05:** error-handling polish. Rejection still happens; I observed a `ConfigError` traceback rather than a clean message from `simulate_outcomes.py` on a broken config. SC 5 requires rejection, which holds.
- **WR-06 (`final_index` ignores `weight_kz` when RoS is undefined)** and **IN-01 (`base_losses` ignores `severity_multiplier`, latent since all tiers use 1.0):** inherited legacy formula defects, now pinned. They do not affect the criteria; fix in Phase 2/6 when weights are rescaled (BAL-03).
- **WR-04, WR-07, WR-08, WR-09, WR-10, IN-02..IN-10:** robustness, docs and test-hygiene items. WR-10 is real but environmental: the slow perf test fails if the README's dump command has been run in the repo root.

### Human Verification Required

None. All success criteria were verified by execution or code evidence.

### Gaps Summary

No gaps. All five roadmap success criteria and all seven FOUND requirements are achieved in the codebase. Recommended follow-ups (non-blocking, none gate Phase 2): decide CR-01 at the start of Phase 2; clean up WR-01..WR-10 in a small hardening plan or alongside Phase 2; fix WR-10 before anyone runs the README dump command and then the slow suite.

---

_Verified: 2026-10-01_
_Verifier: Claude (gsd-verifier)_
