---
phase: 06-rebalance
plan: 06
subsystem: testing
tags: [balance-metrics, tier-comparability, spread]

requires:
  - phase: 06-rebalance
    provides: candidate-config test infrastructure (cached enumerations, balance marker, TUNING_TARGET) (06-01)
provides:
  - planspiel/spread.py with the BAL-09 metrics (TierSpread, tier_spread, one check helper per criterion, check_spread, format_spread) and the proposal constants
  - five slow balance checks on the configured config in tests/test_spread.py
affects: [06-08, 06-09, 06-10]

tech-stack:
  added: []
  patterns:
    - "one check helper and one slow test per criterion, so a failing criterion cannot be masked by a combined check (T-06-15)"
    - "pure metric over report summaries; tier_spread equals a direct nearest-rank computation on the mini config"

key-files:
  created:
    - planspiel/spread.py
    - tests/test_spread.py
  modified: []

key-decisions:
  - "Corridor, IQR tier difference and median bound are measured per layer (static and legal swap layer); D-11 band, IQR range and p5-p95 width per tier and layer"
  - "A tier without in-budget plans on the static layer fails with a German line (check_missing); legal fields that are None are skipped by the criteria and shown as 'nicht berechnet' in the table"
  - "Thresholds stay module constants (CORRIDOR_WIDTH 6, BEST 90..98, IQR 13..21, IQR_TIER_DIFF 4, P5_P95_MAX 50, MEDIAN_START_MAX 28) for re-approval at D-04"

patterns-established:
  - "Slow spread checks share one cached spreads dict per config path and prepend check_missing, so a missing layer fails every check instead of passing vacuously"

requirements-completed: [BAL-09]

coverage:
  - id: D1
    description: "tier_spread reads best, median, IQR and p5-p95 width from the summaries and equals a direct nearest-rank computation over the in-budget final KZ (static store and legal histogram) on all three mini tiers"
    requirement: BAL-09
    verification:
      - kind: unit
        ref: "tests/test_spread.py::test_mini_tier_spread_equals_a_direct_nearest_rank_computation, ::test_tier_spread_*"
        status: pass
    human_judgment: false
  - id: D2
    description: "check_corridor, check_best_band, check_iqr, check_width, check_median_bound and check_spread return German failure lines per violated criterion, are inclusive at the limits and skip None legal fields"
    requirement: BAL-09
    verification:
      - kind: unit
        ref: "tests/test_spread.py::test_best_corridor_*, ::test_median_corridor_*, ::test_best_band_*, ::test_iqr_*, ::test_width_*, ::test_median_bound_*, ::test_check_spread_*, ::test_format_spread_*"
        status: pass
    human_judgment: false
  - id: D3
    description: "Corridor, IQR and width checks pass on today's configured config; the D-11 band and the median bound fail today and carry TUNING_TARGET (xfail)"
    requirement: BAL-09
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_spread.py -m slow -q -rx (real config, 3 passed, 2 xfailed in 5m14s)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Thresholds (corridor 6, best 90..98, IQR 13..21, IQR difference 4, p5-p95 50, median - start 28) are acceptable as the BAL-09 definition"
    requirement: BAL-09
    verification: []
    human_judgment: true
    rationale: "Thresholds are Claude's-discretion proposals (research Q7); the user re-approves them at checkpoint D-04 in 06-09"

duration: 30min
completed: 2026-10-28
status: complete
---

# Phase 6 Plan 06: BAL-09 spread and corridor metrics Summary

**`planspiel/spread.py` guards "outcomes stay controlled": best and median in-budget final KZ lie within a 6-KZ corridor across tiers, the best result sits in 90..98 so the 100 clamp barely binds (D-11), and the per-tier spread (IQR 13..21, IQR difference at most 4, p5-p95 at most 50, median at most 28 above start) stays in range, on the static and on the legal swap layer.**

## Performance

- **Duration:** about 30 min (dominated by two 5 min slow runs)
- **Tasks:** 2 (both TDD; Task 2 is test-only, so it has a single test commit)
- **Files modified:** 2 (both new)

## Accomplishments

- `tier_spread(static_summary, swap_summary=None)` returns `TierSpread(tier, kz_start, best_static, best_legal, median_static, median_legal, iqr_static, iqr_legal, p5_p95_static, p5_p95_legal)` from `report.summarize_tier` / `report.summarize_swap_layer` (IQR = p75 - p25, width = p95 - p5, nearest rank). Brute-force equality on all three mini tiers: static against the in-budget `kz_final` column of the store, legal against the expanded in-budget histogram of the swap layer.
- One helper per criterion: `check_corridor` (best and median, D-07), `check_best_band` (D-11), `check_iqr` (range and tier difference), `check_width`, `check_median_bound`, plus `check_missing` (static layer without in-budget plans). `check_spread` collects them; `format_spread` prints the German table.
- Five slow checks (`slow` + `balance`), one per criterion, built from `candidate.static_summaries` and `report.summarize_swap_layer` over `candidate.swap_layers`. Each prepends `check_missing`, so a missing layer cannot pass vacuously. The two failing ones carry `candidate.TUNING_TARGET`.

## Measured results on the real config (today's simulation_config.json)

TierSpread table (static / legal swap layer, in-budget plans only):

| Tier | start KZ | best | median | median - start | IQR | p5-p95 width |
|------|----------|------|--------|----------------|-----|--------------|
| low | 50 | 98 / 100 | 63 / 60 | +13 / +10 | 17 / 16 | 38 / 37 |
| medium | 42 | 100 / 100 | 65 / 62 | +23 / +20 | 17 / 17 | 43 / 42 |
| high | 34 | 100 / 100 | 66 / 62 | +32 / +28 | 17 / 17 | 46 / 44 |

Verdict per check:

| Check | Result today | Marker |
|-------|--------------|--------|
| `test_best_and_median_inside_tier_corridor` | pass (best corridor 2, median corridor 3 static / 2 legal) | none |
| `test_best_in_budget_inside_d11_band` | fails: best 100 in medium and high static and in all three tiers on the legal layer (only low static, 98, is inside) | TUNING_TARGET |
| `test_iqr_inside_range` | pass (16..17, difference at most 1) | none |
| `test_p5_p95_width_bounded` | pass (maximum 46) | none |
| `test_median_not_too_far_above_start` | fails: high static median 66 is 32 above the start KZ 34 (limit 28); the legal layer is exactly at 28 | TUNING_TARGET |

The values reproduce the research Q7 table (best 98/100/100 static and 100 legal, median 63/65/66 and 60/62/62, IQR 17/17/17 static). The legal p5-p95 widths (37/42/44) are 1 to 2 below the static ones; research gave only the static widths.

Runtime: each slow run (all five checks, cold caches, `--jobs 3` inside) took about 5 min 15 s; the fast suite takes 2 min 37 s.

Findings for the tuning plan:

- D-11 is the main gap: lowering the best result needs 2 KZ off the top in medium and high static and in every legal tier. The median bound binds in the high tier static, where the 28-KZ headroom is already exhausted on the legal layer (62 - 34 = 28), so any tuning step that raises the high-tier median must be checked against it first.
- Lowering the high-tier static median by 4 (66 to 62) also narrows the static median corridor (63/65/66 to 62..65), so the median bound and the corridor move together; the D-11 cut on the best result and the median bound should be tuned jointly and re-checked with the full table.

## Task Commits

1. **Task 1 RED:** `261ad71` test(06-06): add failing tests for the BAL-09 spread and corridor metrics
2. **Task 1 GREEN:** `c2cb296` feat(06-06): spread and corridor metrics for BAL-09
3. **Task 2:** `914351a` test(06-06): slow BAL-09 checks on the configured config

## Decisions Made

See `key-decisions` in the frontmatter. Open for D-04: confirm the thresholds, in particular the median-above-start bound of 28 (it fails today only in the high tier) and the corridor width of 6.

## Deviations from Plan

None - plan executed as written. Two small implementation notes: `check_missing` was added as a sixth helper (not in the plan's list) so that a static layer without in-budget plans fails instead of being silently skipped; the failure lines use the dative layer labels ("auf der statischen Schicht") for correct German.

## Known Stubs

None.

## Issues Encountered

- Pre-existing, out of scope: `HandCalcWarning` for the exfil slope 17/7 on every load of the real config (Phase-6 Pitfall 3, handled by a later plan).

## Threat Flags

None. The module is pure computation over summaries. T-06-15 is mitigated: one helper and one slow test per criterion, and the TUNING_TARGET markers were set per measured result (only D-11 and the median bound).

## Next Phase Readiness

Plan 06-08 can call `spread.tier_spread(static_summary, swap_summary)` per tier, `check_spread` for the verdict and `format_spread` for the report. Plans 06-09 and 06-10 can run `uv run pytest tests/test_spread.py -m slow --runxfail --planspiel-config <candidate> --planspiel-content-dir <dir>` for the BAL-09 verdict on a candidate. `simulation_config.json`, `content/`, goldens and `final_documents/` are untouched (D-04 freeze).

## Self-Check: PASSED

- Files exist: planspiel/spread.py, tests/test_spread.py
- Commits exist: 261ad71, c2cb296, 914351a
- `uv run pytest -q`: 2504 passed, 1 xfailed (fast suite); `uv run pytest tests/test_spread.py -m slow -q -rx`: 3 passed, 2 xfailed
