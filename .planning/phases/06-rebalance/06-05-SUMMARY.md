---
phase: 06-rebalance
plan: 05
subsystem: testing
tags: [balance-metrics, rewarding, comeback, median-margin]

requires:
  - phase: 06-rebalance
    provides: candidate-config test infrastructure (cached enumerations, balance marker), swap-layer start aggregates (06-01)
provides:
  - planspiel/rewarding.py with the BAL-08 metrics (median_margins, comeback, rewarding_tier, check_rewarding, format_rewarding) and the proposal constants
  - two slow balance checks on the configured config in tests/test_rewarding.py
affects: [06-08, 06-09, 06-10]

tech-stack:
  added: []
  patterns:
    - "wave-1 KZ of a start only through TierTables.path_outcome (kz_after[0]); no wave formula re-encoded"
    - "pure metric over swap-layer start aggregates, equal to a brute force built from rules.evaluate_plan / evaluate_path"

key-files:
  created:
    - planspiel/rewarding.py
    - tests/test_rewarding.py
  modified: []

key-decisions:
  - "Hit starts are all dependency-valid starts (not only those with a continuation); starts without an in-budget continuation are reported separately and a tier with hit starts but no continuation at all fails the check"
  - "A tier without hit starts, or a layer without in-budget plans, is handled explicitly: no hit starts passes vacuously, no in-budget plans fails with a German line"
  - "Thresholds stay module constants (MEDIAN_MARGIN 5, COMEBACK_DROP 5, COMEBACK_GAIN 10, COMEBACK_SHARE 9/10) for re-approval at D-04"

patterns-established:
  - "Stub tables for threshold tests expose path_outcome as a staticmethod attribute, because test_single_definition forbids a second function named path_outcome"

requirements-completed: [BAL-08]

coverage:
  - id: D1
    description: "median_margins and comeback are exact: comeback equals a brute force over rules.evaluate_plan (wave-1 KZ) and rules.evaluate_path (best in-budget swap continuation) on every mini tier for five (drop, gain) pairs; synthetic cases cover the inclusive thresholds and the empty cases"
    requirement: BAL-08
    verification:
      - kind: unit
        ref: "tests/test_rewarding.py::test_mini_comeback_equals_brute_force, ::test_comeback_*, ::test_median_margins_*"
        status: pass
    human_judgment: false
  - id: D2
    description: "check_rewarding and format_rewarding return German failure lines for margins below 5, a missing layer median, comeback share below 9/10 and hit starts without any continuation"
    requirement: BAL-08
    verification:
      - kind: unit
        ref: "tests/test_rewarding.py::test_check_rewarding_*, ::test_format_rewarding_reports_every_tier_in_german"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both BAL-08 checks pass on today's configured config (static and legal margins, comeback shares)"
    requirement: BAL-08
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_rewarding.py -m slow -q (real config, 2 passed in 8m06s)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Thresholds (median margin 5, comeback drop 5, gain 10, share 90 %) are acceptable as the BAL-08 definition"
    requirement: BAL-08
    verification: []
    human_judgment: true
    rationale: "Thresholds are Claude's-discretion proposals (research Q7); the user re-approves them at checkpoint D-04 in 06-09"

duration: 35min
completed: 2026-10-28
status: complete
---

# Phase 6 Plan 05: BAL-08 rewarding metrics Summary

**`planspiel/rewarding.py` guards "the game is rewarding overall": the in-budget median must end at least 5 KZ above the start KZ on the static and the legal swap layer, and at least 90 % of the starts that lose 5 or more KZ in wave 1 (and still have an in-budget swap continuation) must have one ending at start KZ + 10 or better.**

## Performance

- **Duration:** about 35 min (dominated by the 8 min slow run)
- **Tasks:** 2 (both TDD; Task 2 is test-only, so it has a single test commit)
- **Files modified:** 2 (both new)

## Accomplishments

- `median_margins(static_summary, swap_summary)` reads the in-budget p50 of both summaries minus the start KZ (None for a layer without in-budget plans).
- `comeback(tables, starts, drop=5, gain=10)` returns `ComebackResult(hit, with_continuation, without_continuation, share_gain, share_above_start, median_best, p90_best)`. The KZ after wave 1 comes from `tables.path_outcome((s,) * wave_count, 0).kz_after[0]`; continuation and best final come from the `enumerate_swap_layer(...)["starts"]` aggregates; median and p90 use `report.nearest_rank`.
- `rewarding_tier`, `check_rewarding` and `format_rewarding` (German failure lines and report) are ready for the consolidated report of plan 06-08 (which replaces `balance.POSITIVE_KZ_THRESHOLD` by this check).
- Brute force: on all three mini tiers and for five (drop, gain) pairs the result equals an independent computation from `rules.evaluate_plan` (`waves[0]["kz_after"]`) and `rules.evaluate_path` over every legal swap path of each hit start.
- Slow checks `test_median_ends_above_start_on_both_layers` and `test_comeback_after_wave_one_is_possible` (`slow` + `balance`) pass on today's config, so they carry no `TUNING_TARGET`.

## Measured results on the real config (today's simulation_config.json)

| Metric | low | medium | high |
|--------|-----|--------|------|
| start KZ | 50 | 42 | 34 |
| static in-budget median / margin | 63 / +13 | 65 / +23 | 66 / +32 |
| legal-layer in-budget median / margin | 60 / +10 | 62 / +20 | 62 / +28 |
| hit starts (KZ after wave 1 <= start - 5) | 19,532 | 19,532 | 19,532 |
| hit starts with in-budget continuation | 19,369 | 19,531 | 19,532 |
| hit starts without any in-budget continuation | 163 | 1 | 0 |
| share_gain (best continuation >= start + 10) | 17,715 / 19,369 = 0.915 | 18,748 / 19,531 = 0.960 | 18,781 / 19,532 = 0.962 |
| share_above_start (best continuation > start) | 19,128 / 19,369 = 0.988 | 19,485 / 19,531 = 0.998 | 9,745 / 9,766 = 0.998 |
| best continuation median / p90 | 71 / 81 | 70 / 79 | 65 / 76 |

Runtime: the two slow checks together took 8 min 06 s (cold caches, `--jobs 3` inside, while a second identical measurement run competed for the same cores). The mini brute-force suite takes about 4 s; the fast suite (`uv run pytest -q`) takes 2 min 36 s.

Findings for the tuning plan:

- The low tier is the binding one for the comeback (0.915 against the 0.90 threshold): only 1.5 pp of headroom, and 163 low-tier hit starts have no in-budget continuation at all (they are excluded from the share by definition, but they are the "effectively eliminated" cases in spirit). A tuning step that tightens the low budget or lowers the low start KZ must be re-checked against this first.
- The count of continued hit starts differs from the research note (19,368 / 19,530 / 19,531) by exactly one per tier; the median, p90 and shares match the research values (91 / 96 / 96 %). The plan's definition (all valid starts, `in_budget_paths > 0`) is implemented as written; the one-start difference is most likely the empty plan, which has no swap and counts as an exempt static path here.

## Task Commits

1. **Task 1 RED:** `5aa48f1` test(06-05): add failing tests for the median margin and comeback metrics
2. **Task 1 GREEN:** `501fe81` feat(06-05): median margin and comeback metrics for BAL-08
3. **Task 2:** `64e7c92` test(06-05): slow BAL-08 checks on the configured config

## Decisions Made

See `key-decisions` in the frontmatter. Open for D-04: confirm the thresholds, in particular the 90 % comeback share (low tier headroom is 1.5 pp) and that starts without any continuation are reported but not part of the share.

## Deviations from Plan

None - plan executed as written. One test-construction note: the stub tables of the synthetic comeback tests expose `path_outcome` as a `staticmethod` attribute instead of a method, because `tests/test_single_definition.py` requires exactly one function named `path_outcome` (in `planspiel/rules.py`) across `planspiel/` and `tests/`. Fixed in the GREEN commit.

## Known Stubs

None.

## Issues Encountered

- Pre-existing, out of scope: `HandCalcWarning` for the exfil slope 17/7 on every load of the real config (Phase-6 Pitfall 3, handled by a later plan).

## Threat Flags

None. The module is pure computation over summaries, in-memory arrays and `TierTables`; T-06-14 is mitigated: the wave-1 KZ is read only from `TierTables.path_outcome`, the brute force uses `rules.evaluate_plan` / `evaluate_path`, and the single-definition guard passes.

## Next Phase Readiness

Plan 06-08 can call `rewarding.rewarding_tier(cfg, tier, static_summary, swap_summary, tables, swap_layer)` per tier, `check_rewarding` for the verdict and `format_rewarding` for the report. Plans 06-09 and 06-10 can run `uv run pytest tests/test_rewarding.py -m slow --planspiel-config <candidate> --planspiel-content-dir <dir>` for the BAL-08 verdict on a candidate. `simulation_config.json`, `content/`, goldens and `final_documents/` are untouched (D-04 freeze).

## Self-Check: PASSED

- Files exist: planspiel/rewarding.py, tests/test_rewarding.py
- Commits exist: 5aa48f1, 501fe81, 64e7c92
- `uv run pytest -q`: 2479 passed, 1 xfailed (fast suite); `uv run pytest tests/test_rewarding.py -m slow -q`: 2 passed
