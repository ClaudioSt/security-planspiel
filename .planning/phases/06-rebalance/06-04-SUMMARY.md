---
phase: 06-rebalance
plan: 04
subsystem: testing
tags: [balance-metrics, dominance, near-mandatory, overpowered, decision-points]

requires:
  - phase: 06-rebalance
    provides: candidate-config test infrastructure (TUNING_TARGET, cached enumerations), swap-layer start aggregates, TierTables.single_moves (06-01)
provides:
  - planspiel/choices.py with the BAL-06 metrics (strictly dominated levels, near-mandatory band shares, removal drops, level swing, tier band Jaccard, Kurswechsel spread, window-2 move effect) and a German report
  - one slow balance check per BAL-06 criterion in tests/test_choices.py (near-mandatory and overpowered are TUNING_TARGET)
  - TierTables.swap_paths(start_stride) for deterministic start samples
affects: [06-05, 06-06, 06-07, 06-08, 06-09, 06-10]

tech-stack:
  added: []
  patterns:
    - "per-criterion check functions (choices.CRITERIA) so each slow test and each TUNING_TARGET marker is precise"
    - "pure metrics over ResultStore columns and swap-layer start aggregates, equal to a brute force built only from rules.evaluate_path / harness"

key-files:
  created:
    - planspiel/choices.py
    - tests/test_choices.py
  modified:
    - planspiel/rules.py

key-decisions:
  - "Near-mandatory band is the 5-KZ band widened to the 200 best in-budget plans; on today's config the band is 200 in every tier (research: 5-KZ band is 104/134/120), so the widening decides the result"
  - "Window-move improvement is floored at 0 (no move is always possible) and a moved path must stay in budget; mean is over all sampled in-budget swap paths"
  - "Best plan of a tier is band[0] (max KZ, then lowest own cost, then lowest code), used for the identical-optimum check"
  - "Thresholds stay module constants (BAND_KZ 5, BAND_MIN_SIZE 200, NEAR_MANDATORY_SHARE 9/10, OVERPOWERED_DROP 10, DECISION_SHIFT_KZ 3, DECISION_SHARE 1/2, TIER_JACCARD_MAX 1/2, WINDOW_SAMPLE_STRIDE 97) for re-approval at D-04"

patterns-established:
  - "Slow balance check per criterion: _assert_criterion(name, path) over choices.CRITERIA, cached blocks per config path"

requirements-completed: [BAL-06]

coverage:
  - id: D1
    description: "Static-layer choice metrics (kz_grid, improvement shares, strictly dominated, swing, near-optimal band, band shares, near-mandatory, removal drops, tier Jaccard) equal an independent brute force on the mini config"
    requirement: BAL-06
    verification:
      - kind: unit
        ref: "tests/test_choices.py::test_mini_*, ::test_synthetic_*"
        status: pass
    human_judgment: false
  - id: D2
    description: "Kurswechsel spread and window-2 move effect equal a brute force over rules.evaluate_path (swap paths and two-window paths) on the mini config; start-strided swap_paths equals the filtered full list"
    requirement: BAL-06
    verification:
      - kind: unit
        ref: "tests/test_choices.py::test_mini_kurswechsel_spread_equals_brute_force_over_the_swap_paths, ::test_mini_window_move_effect_equals_brute_force_over_two_windows, ::test_swap_paths_start_stride_keeps_exactly_the_strided_starts"
        status: pass
    human_judgment: false
  - id: D3
    description: "Slow BAL-06 checks on the configured config: dominance, swing, tier optima, Kurswechsel and window pass today; near-mandatory and overpowered xfail"
    requirement: BAL-06
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_choices.py -m slow -q -rx (real config, 7m25s: 5 passed, 2 xfailed)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Thresholds (band 5 KZ widened to 200, near-mandatory 90 %, overpowered drop 10, decision shift 3 KZ in 50 %, tier Jaccard under 0.5) are acceptable as the BAL-06 definition"
    requirement: BAL-06
    verification: []
    human_judgment: true
    rationale: "Thresholds are Claude's-discretion proposals (D-16); the user re-approves them at checkpoint D-04 in 06-09"

duration: 70min
completed: 2026-10-28
status: complete
---

# Phase 6 Plan 04: BAL-06 choice metrics Summary

**`planspiel/choices.py` measures "every choice matters" by full enumeration: strictly dominated levels, near-mandatory measures on a near-optimal band, overpowered measures by removal drop, and the effect of the four decision points; M7 (all tiers) and M2 (medium, high) show up as near-mandatory and overpowered, plus M1/M4/M5 near-mandatory in high.**

## Performance

- **Duration:** about 70 min (including two long real-config runs)
- **Started:** 2026-10-28T20:55Z
- **Completed:** 2026-10-28T22:10Z
- **Tasks:** 2 (both TDD: RED commit, then GREEN commit)
- **Files modified:** 3 (2 new)

## Accomplishments

- Static layer (Task 1): `kz_grid` (4^n grid, -1 for invalid or over budget), `level_improvement_shares`, `strictly_dominated`, `level_swing_shares`, `near_optimal_band`, `band_shares`, `near_mandatory`, `removal_drops`, `tier_band_jaccard`. Slice-based stride arithmetic like `gate.lowering_closure`; no operand access, no builtin round; percentiles through `report.nearest_rank`.
- Move layer (Task 2): `kurswechsel_spread` (from the swap-layer start aggregates), `window_move_effect` (deterministic start sample, best in-budget single window-2 move on every in-budget swap path), `choices_tier`, `cross_tier_choices`, per-criterion checks collected in `CRITERIA`, `check_choices`, `format_choices` (German).
- Every function equals an independent brute force on the mini config for all three tiers (brute force built from `harness.evaluate` and `rules.evaluate_path`, never from the functions under test), plus synthetic n = 2 cases for the thresholds and failure lines.
- Slow checks, one test per criterion on `balance_config_path`: dominance, swing, tier optima, Kurswechsel and window pass on today's config; near-mandatory and overpowered are `TUNING_TARGET` and xfail.

## Measured results on the real config (today's simulation_config.json)

Band: the 5-KZ band is smaller than 200 in every tier, so the 200 best in-budget plans form the band (200 / 200 / 200). Tier best in budget and best plan: low 98 (`0102003200`), medium 100 (`1101122200`), high 100 (`1201123000`); all three differ.

| Metric | low | medium | high |
|--------|-----|--------|------|
| band share level >= 1: M7 | 1.000 | 1.000 | 1.000 |
| M2 | 0.860 | 0.990 | 1.000 |
| M4 | 0.780 | 0.875 | 0.965 |
| M1 | 0.425 | 0.705 | 0.960 |
| M5 | 0.455 | 0.685 | 0.930 |
| near-mandatory (> 0.9) | M7 | M2, M7 | M1, M2, M4, M5, M7 |
| removal drop M7 / M2 | 14 / 3 | 16 / 7 | 18 / 11 |
| other removal drops | M4 1, M8 1 | M1 1, M4 1, M5 1, M6 1 | M1 2, M4 2, M5 2 |
| overpowered (drop > 10) | M7 | M7 | M2, M7 |
| smallest improvement share | M1 L3 0.046 (9 of 197 contexts; next M9 L2 0.242) | M1 L3 0.242 | M1 L3 0.343 |
| smallest swing share (>= 3 KZ) | M9 0.659 | M8 0.754 | M8 0.818 |
| largest swing share | M7 0.971 | M7 0.969 | M7 0.959 |
| Kurswechsel: share of starts with spread >= 3 | 0.986 | 0.988 | 0.988 |
| Kurswechsel spread median / p90 | 29 / 40 | 30 / 42 | 30 / 43 |
| Kurswechsel starts (>= 2 swaps in budget) | 92,537 | 160,318 | 246,604 |
| window-2 move: share with gain >= 3 KZ | 0.604 | 0.606 | 0.622 |
| window-2 mean / max gain | 6.11 / 25 | 6.45 / 25 | 6.58 / 25 |
| window-2 sample (in-budget swap paths, stride 97) | 37,021 | 68,182 | 110,412 |

Tier band Jaccard: low-medium 0.413, low-high 0.036, medium-high 0.320 (all under 0.5). No strictly dominated level in any tier (every improvement share is above 0).

Runtime of the slow checks (6-core Windows, cold caches, `--jobs 3` inside): 7 min 25 s for the whole slow file (static stores about 49 s, swap layers about 250 s, `choices_tier` 45 to 56 s per tier including the window sample). The mini brute-force suite takes under 20 s.

Findings for the tuning plan:

- The near-mandatory result in the high tier is wider than the research headline: with the 200-plan widening M1 (0.96), M4 (0.965) and M5 (0.93) are near-mandatory next to M2 and M7. Fixing only M7 and M2 will not make `test_no_measure_is_near_mandatory` pass in high.
- The Kurswechsel and window decisions are strong today (0.99 and 0.60 to 0.62), so a tuning step that flattens the wave-3 bonuses must be re-checked against the 0.5 window-move threshold.
- No check other than near-mandatory and overpowered fails today, so those two are the only additional TUNING_TARGET markers (as expected by the plan).

## Task Commits

1. **Task 1 RED:** `8edf7d6` test(06-04): add failing tests for the static-layer choice metrics
2. **Task 1 GREEN:** `cffe994` feat(06-04): static-layer choice metrics for dominance, swing, band and removal drops
3. **Task 2 RED:** `017a53f` test(06-04): add failing tests for the move-layer decision points and the choice report
4. **Task 2 GREEN:** `53cd63e` feat(06-04): move-layer decision points, tier report and slow BAL-06 checks

## Decisions Made

See `key-decisions` in the frontmatter. Open for D-04: confirm the thresholds, in particular the 200-plan band widening (it decides near-mandatory in high) and the definition of the window-move improvement (floored at 0, moved path must stay in budget).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `TierTables.swap_paths` gained an optional `start_stride` parameter**
- **Found during:** Task 2 (window_move_effect)
- **Issue:** The plan samples starts with `state code % stride == 0`, but `swap_paths()` always generates the paths of every start (about 37 million per tier, about 4 min); filtering the generator output would have cost the full enumeration again per tier.
- **Fix:** `swap_paths(self, start_stride: int = 1)` skips starts whose index is not divisible by `start_stride`; the default keeps all existing callers unchanged. A test proves the strided output equals the filtered full list on the mini config.
- **Files modified:** planspiel/rules.py (not listed in the plan's files_modified), tests/test_choices.py
- **Commit:** 53cd63e

Otherwise the plan was executed as written.

## Known Stubs

None.

## Issues Encountered

- A bash heredoc that appended the second test block failed; the block was written through the Write tool into the scratchpad and appended from there (no repo impact).
- Pre-existing, out of scope: `HandCalcWarning` for the exfil slope 17/7 on every config load (Phase-6 Pitfall 3, handled by a later plan).

## Threat Flags

None. The module is pure computation over in-memory arrays; configs reach it only through `load_config` (T-06-12 mitigated by the brute-force equality tests and one slow test per criterion; T-06-13 mitigated by the deterministic stride sample and the cached swap layers and tables of `tests/support/candidate.py`).

## Next Phase Readiness

Plans 06-05 to 06-10 can run `uv run pytest tests/test_choices.py -m slow --runxfail --planspiel-config <candidate> --planspiel-content-dir <dir>` for the BAL-06 verdict on a candidate, or `choices.format_choices(...)` for the German report; the goldens, `simulation_config.json`, `content/` and `final_documents/` are untouched (D-04 freeze).

## Self-Check: PASSED

- Files exist: planspiel/choices.py, tests/test_choices.py, planspiel/rules.py (swap_paths start_stride)
- Commits exist: 8edf7d6, cffe994, 017a53f, 53cd63e
- `uv run pytest -q`: 2444 passed, 1 xfailed (fast suite); `uv run pytest tests/test_choices.py -m slow -q -rx`: 5 passed, 2 xfailed
