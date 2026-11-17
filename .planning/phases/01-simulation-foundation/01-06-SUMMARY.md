---
phase: 01-simulation-foundation
plan: 06
subsystem: simulation-core
tags: [exact-arithmetic, rounding, paper-rounding, golden-regeneration, characterization, tdd]
requires: ["01-05"]
provides:
  - "planspiel/rounding.py: round_half_away(n, d), round_half_away_frac, started_steps(amount, step=10_000), exact_to_json"
  - "planspiel/rules.py: exact integer-scaled primitives (e_value_scaled, reduction_above_threshold_scaled, severity_scaled, damage_euros, clamp_kz, attack_kz_delta, wave_kz_change) and a single per-wave rounding point"
  - "planspiel/config.py: Config.ws / Config.rs scale factors, exact Fraction parsing of the config"
  - "Regenerated goldens tests/golden/characterization_*.json and digest_*.json with stage 'exact-rounded'"
  - ".planning/phases/01-simulation-foundation/01-EXACT-SWITCH-DIFF.md: human-approved all-combination diff"
affects: [01-07]
tech-stack:
  added: []
  patterns:
    - "integer-scaled arithmetic (E-value and severity scaled by ws, recovery by rs), Fractions only for slopes and KZ deltas"
    - "one rounding point per wave: round_half_away of (attack KZ-Delta + E-target bonus/malus + event KZ), then clamp 0..100"
    - "exact values serialised as int, finite decimal string (\"2.24\") or \"p/q\" via exact_to_json; Fraction(str) reads all of them back"
key-files:
  created:
    - planspiel/rounding.py
    - tests/test_rounding.py
    - tests/test_rules_exact.py
    - .planning/phases/01-simulation-foundation/tools/exact_switch_diff.py
    - .planning/phases/01-simulation-foundation/01-EXACT-SWITCH-DIFF.md
  modified:
    - planspiel/rules.py
    - planspiel/config.py
    - planspiel/simulate.py
    - planspiel/analyze.py
    - planspiel/balance.py
    - tests/support/harness.py
    - tests/support/golden.py
    - tests/support/digest.py
    - tests/test_harness_vs_run_simulation.py
    - tests/test_rules_semantics.py
    - tests/test_single_definition.py
    - tests/golden/characterization_low.json
    - tests/golden/characterization_medium.json
    - tests/golden/characterization_high.json
    - tests/golden/digest_low.json
    - tests/golden/digest_medium.json
    - tests/golden/digest_high.json
    - README.md
    - CLAUDE.md
    - .gitignore
key-decisions:
  - "Rounding rule approved by the user: kaufmaennisch (half away from zero), applied once per wave to the summed exact KZ change, then clamped to 0..100; final Budget Review stays an integer applied after the waves (D-01, D-02, D-06)"
  - "The float-to-exact snapshot change was committed as one explicit, human-reviewed commit (D-05 step 3 / D-10) after the user reviewed 01-EXACT-SWITCH-DIFF.md"
  - "Stage marker in the harness is now 'exact-rounded'; golden digests pin the new arithmetic generation"
requirements-completed: [FOUND-05]
duration: ~9h wall clock (includes an executor interruption by a provider quota limit and the user review gate)
completed: 2026-10-01
status: complete
---

# Phase 1 Plan 06: Exact arithmetic and paper rounding Summary

The simulation now runs on exact integer/Fraction arithmetic with a single tested paper-rounding helper (`round_half_away`, half away from zero) and a single `started_steps` helper; the float-to-exact change of all three tiers was reviewed and approved by the user and committed as one explicit snapshot change (`0d342f6`).

## Tasks

| Task | Name | Commits |
|------|------|---------|
| 1 | Paper rounding and started-step helpers, plus the exact-switch diff tool (test-first) | RED `9a82d6b`, GREEN `785ed97`, tool `683cfd9` |
| 2 | Exact integer-scaled wave arithmetic with one rounding point (test-first) | RED `53f678b`, GREEN in `0d342f6` |
| 3 | Exact values at the boundaries, all-combination diff report, golden regeneration | in `0d342f6` (uncommitted until approval, per plan) |
| 4 | Checkpoint human-verify: review of the diff report | approved by the user; switch commit `0d342f6` |

Commit hashes: `9a82d6b`, `785ed97`, `683cfd9`, `53f678b`, `0d342f6`.

## What was built

- `planspiel/rounding.py`: `round_half_away(n, d)` (+2.5 -> +3, -2.5 -> -3, -5.5 -> -6, +11.5 -> +12), `round_half_away_frac`, `started_steps` (1 for exactly 10.000 EUR, 2 for 10.001 EUR, 0 for zero and negative), `exact_to_json`.
- `planspiel/rules.py`: E-value, reduction above threshold and severity are integers scaled by `ws`; damage is whole euros via a single `divmod` with `rs`; RoS is an exact Fraction. Each wave's KZ change (attack KZ-Delta + E-target bonus/malus + that wave's event KZ) is summed exactly, rounded once by `wave_kz_change`, and clamped by `clamp_kz`.
- `planspiel/config.py`: config numbers parsed exactly; `Config.ws` / `Config.rs` carry the scale factors from `validate.scale_factors`.
- `simulate.py`, `analyze.py`, `balance.py` and the test harness consume exact values at their boundaries; `README.md` and `CLAUDE.md` document the rounding rule.
- `tools/exact_switch_diff.py`: captures the legacy float dumps and compares them with the exact run over all 782,336 combinations per tier.

## Approved diff (float vs exact-rounded), per tier

| Metric | low | medium | high |
|---|---|---|---|
| Combinations compared | 782,336 | 782,336 | 782,336 |
| Final KZ changed (abs delta > 1e-9) | 121,306 | 168,625 | 194,360 |
| Final KZ float-noise-only difference (<= 1e-9) | 80 | 168 | 258 |
| KZ shift >= 0.5 down / up | 8,074 / 8,178 | 8,730 / 9,321 | 9,071 / 9,760 |
| Max absolute KZ shift | 1.22 | 1.22 | 1.22 |
| E-target flips | 0 | 0 | 0 |
| Over-budget flips | 0 | 0 | 0 |
| Damage changes > 0.5 EUR | 0 | 0 | 0 |
| Wave-3 ties (legacy capped reduction == 3.5) | 1,050 | 1,050 | 1,050 |

All counts match the research expectations (121,306 / 168,625 / 194,360 changed KZ, 0 flips). Full report with top movers and example codes: `01-EXACT-SWITCH-DIFF.md`.

New golden digests (stage `exact-rounded`):

- low `1048fe8563e76a5b1704dbfc916d7a0c69bb5eef2a0a21c2811015bc41708923`
- medium `bcfa568c3993a95b7e3f901782598f63ad2cae3a6defacd38e9c17559f5b3c37`
- high `87b12ff9feb013ccc2d448e0771914d31556fffb45597769a18e8ccdeffd9c17`

## Verification output (run after the switch commit `0d342f6`)

```
uv run pytest -q
183 passed, 4 deselected, 24 warnings in 11.62s

uv run pytest -m slow -q
4 passed, 183 deselected, 5 warnings in 1035.86s (0:17:15)
```

`git status --porcelain -- planspiel tests README.md CLAUDE.md` is empty after both runs; the working tree is clean. (Before the commit the same suites were run once with the regenerated goldens: fast 183 passed, slow 4 passed in 14m05s.)

The TDD RED gates are visible in the log (`9a82d6b` and `53f678b` are `test(...)` commits that preceded the GREEN code). The GREEN code for Task 2 was deliberately not committed separately: the plan requires the float-to-exact change to land as one reviewed snapshot commit.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Diff tool counted float-noise-only differences as real KZ changes**
- **Found during:** Task 3 (all-combination diff), before the user review
- **Issue:** `exact_switch_diff.py` counted every nonzero difference between the legacy float KZ and the exact KZ as "changed", so values such as `80.78000000000001` vs `80.78` inflated the changed count above the research figures.
- **Fix:** Introduced `NOISE_EPS = 1e-9`; "changed" now means abs delta > NOISE_EPS, and differences with 0 < abs delta <= NOISE_EPS are reported in a separate row (80 / 168 / 258 in low / medium / high). The corrected counts equal the research expectations exactly.
- **Files modified:** `.planning/phases/01-simulation-foundation/tools/exact_switch_diff.py`
- **Commit:** `0d342f6` (tool first added in `683cfd9`)

### Process notes (not code deviations)

- The executor run was interrupted by a provider quota limit in the middle of the plan and resumed as a continuation agent. No work was lost: Tasks 2 and 3 were in the working tree and were verified against the checkpoint state (fast 183 passed, slow 4 passed) before the approval commit.
- The user's approval at the Task 4 checkpoint additionally asked to include the corrected diff tool and the diff report in the same single commit; both are in `0d342f6`.

## Known Stubs

None.

## Threat Flags

None. No new network, auth or file-access surface; the diff tool writes only into the gitignored `exact-switch/` directory.

## Notes for plan 01-07

- Use the exact primitives in `planspiel/rules.py` (`e_value_scaled`, `reduction_above_threshold_scaled`, `severity_scaled`, `damage_euros`, `attack_kz_delta`, `wave_kz_change`, `clamp_kz`, `ros`) from the compact kernel; do not re-derive the arithmetic. Conformance target: the kernel digest over all combinations must equal the regenerated golden digests above.
- Scale factors are `cfg.ws` and `cfg.rs` (currently 10 and 10); pass them into every scaled primitive.
- RoS is an exact Fraction (or None at cost 0); serialise exact values with `planspiel.rounding.exact_to_json` (int, `"2.24"`, or `"p/q"`); `Fraction(str)` reads them back.
- The golden `digest_*.json` and `characterization_*.json` files carry stage `exact-rounded` (`tests/support/harness.STAGE`). Do not regenerate them in 01-07; any kernel difference is a bug in the kernel, not in the goldens.
- Damage is whole euros (integer); the legacy `run_simulation` output format still exists for `analyze_simulation_results.py`.
- The hand-calc warning `kz_slope 17/7 has more than one decimal place` (attacks.exfil) appears in test output by design (plan 01-05 validator); it is a warning, not a failure.

## Self-Check: PASSED

- Commits `9a82d6b`, `785ed97`, `683cfd9`, `53f678b`, `0d342f6` exist in `git log`.
- `planspiel/rounding.py`, `tests/test_rounding.py`, `tests/test_rules_exact.py`, `01-EXACT-SWITCH-DIFF.md`, `tools/exact_switch_diff.py` exist.
- Fast and slow suites passed after the switch commit; working tree clean for code paths.
