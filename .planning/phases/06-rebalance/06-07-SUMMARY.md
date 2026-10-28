---
phase: 06-rebalance
plan: 07
subsystem: testing
tags: [reference-strategies, clue-mapping, quartile-placement, bal-07]

requires:
  - phase: 06-rebalance
    provides: candidate-config test infrastructure and cached enumerations (06-01), Final-Index with two-decimal RoS (06-03)
provides:
  - rules.bonus_importance (bonus times KZ slope per bonus measure)
  - clue to measure mapping in planspiel/texts.py (Clue.measures/weight, clue_scores, clue_mapping_issues, check_clues(require_mapping), console matrix column)
  - config key reference_strategies with validator (ref.bad_kind), Config.reference_strategies and refpaths.path_from_block
  - planspiel/strategies.py with quartile placement, the clue-derived good start and the non-clue guard
affects: [06-08, 06-09, 06-10]

tech-stack:
  added: []
  patterns:
    - "Per-path reference checks shared by reference_plans and reference_strategies (_check_reference_path)"
    - "Slow BAL-07 checks are TUNING_TARGET xfails that fail fast (no enumeration) while the block or the mapping is absent"

key-files:
  created:
    - planspiel/strategies.py
    - tests/test_clues_mapping.py
    - tests/test_reference_strategies.py
    - tests/test_strategies.py
  modified:
    - planspiel/rules.py
    - planspiel/texts.py
    - planspiel/cli.py
    - planspiel/config.py
    - planspiel/validate.py
    - planspiel/refpaths.py
    - tests/test_clues.py
    - tests/test_single_definition.py
    - tests/test_texts_coverage.py
    - tests/fixtures/mini_config.json
    - tests/fixtures/mini_content/clues.toml

key-decisions:
  - "Clue score = sum of the weights of all clues naming the measure; importance = sum over waves of bonus times slope (exact Fractions); rule I(a) > I(b) implies S(a) >= S(b), S >= 2 for every bonus measure, S(most important) >= 4 (research A4, proposals for D-04)"
  - "require_mapping stays False by default; 06-10 flips it with the adopted content. The real content/clues.toml carries no mapping and the booklet column is not built here (D-04 freeze)"
  - "Placement counts strictly below / strictly above shares, quartile bounds inclusive (3/4 and 1/4); good needs both populations (static Final-Index and swap-layer KZ), research A9 resolved as 'both'"
  - "check_strategies takes the kind coverage from the placements and the 'good' start check from the config entries, so each defect yields exactly one German line"

patterns-established:
  - "Brute-force oracle for placement built only from rules.evaluate_plan / evaluate_path and the swap-layer brute force of test_swap_layer"

requirements-completed: [BAL-07]

coverage:
  - id: D1
    description: "Clue to measure mapping with importance, support/graduation/top-floor checks and the facilitator console column"
    requirement: BAL-07
    verification:
      - kind: unit
        ref: "tests/test_clues_mapping.py, tests/test_clues.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "reference_strategies block: validator codes, loader, field order, shared path builder, legal in-budget mini entries"
    requirement: BAL-07
    verification:
      - kind: unit
        ref: "tests/test_reference_strategies.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "Placement equals a brute force over both populations; clue_good_start follows the written-out procedure; non_clue_share and check_strategies"
    requirement: BAL-07
    verification:
      - kind: unit
        ref: "tests/test_strategies.py (mini config)"
        status: pass
      - kind: integration
        ref: "uv run pytest tests/test_strategies.py -m slow -q -rx (5 xfailed on today's config)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Weight scale 1..3, score floors 2 and 4, graduation by bonus times slope, both-population placement rule"
    requirement: BAL-07
    verification: []
    human_judgment: true
    rationale: "Definition choices for the tuning; re-presented to the user at D-04 together with the real mapping (06-09)"

duration: 55min
completed: 2026-10-28
status: complete
---

# Phase 6 Plan 07: BAL-07 reference strategies and clue mapping Summary

**Clue to measure mapping with importance-graduated checks, a validated `reference_strategies` config key, and `planspiel/strategies.py`, which places good/mediocre/bad strategies in the quartiles of both populations and ties the good strategy to the clue scores.**

## Performance

- **Duration:** about 55 min (including one 8 min measurement run on the real config)
- **Completed:** 2026-10-28
- **Tasks:** 3 (all TDD: RED commit, then GREEN commit)
- **Files modified:** 15 (4 new)

## Accomplishments

- `rules.bonus_importance(cfg)`: KZ points at stake per bonus measure. Registered in the single-definition guard.
- Clue mapping: `Clue.measures` / `Clue.weight` (defaults `()` and 0), type validation in `load_clues` (ValueError naming the clue, reported by `planspiel clues` as `ERROR clues.toml`), `clue_scores`, `clue_mapping_issues`, `check_clues(..., require_mapping=False)`. New codes `clues.unknown_measure`, `clues.bad_weight` (always), `clues.unsupported_bonus`, `clues.not_graduated`, `clues.top_too_weak` (only with `require_mapping`). Console matrix has the 7th column `Maßnahmen (Gewicht)` (`ClueRow.measures`, e.g. `M1 (3), M2 (3)`).
- `reference_strategies` key: `check_reference_strategies`, `REFERENCE_STRATEGY_KINDS`, code `ref.bad_kind`, per-path checks extracted into `_check_reference_path` and shared with `reference_plans`; `Config.reference_strategies` directly after `reference_plans` (`practice` stays last); `refpaths.path_from_block` and `reference_path` delegating to it.
- `planspiel/strategies.py`: `Placement`, `placed_by_kind`, `place_strategies` (exact Fraction shares against the static in-budget Final-Index population and the swap-layer in-budget KZ histogram), `clue_good_start`, `non_clue_share`, `check_strategies` (German lines, one per defect), `strategies_tier`, `format_strategies`.
- Mini fixtures: graduated clue mapping (scores M1 5, M2 3, M4 2, M6 2) and five legal in-budget strategies per tier (`good`, `mediocre`, `bad_ignore`, `bad_all_in`, `bad_hoard`).
- Five slow checks on the configured config and content directory (present/legal, placed by kind, good derived from clues, non-clue guard, mapping complete). All xfail on today's config and fail before any enumeration while the block or the mapping is missing.

## Measurements on today's config (for the tuning plan 06-09)

Provisional mapping from the research reading of the 14 clues (A6), applied only in a scratch script and not written to `content/`: M4 gets clues 1 (weight 2) and 3 (3); M3 clue 2 (1); M5 clues 5 (2), 7 (3), 9 (3); M7 clue 6 (2); M8 clues 10, 11, 13, 14 (2 each); M1 clue 12 (2); clues 4 and 8 are atmospheric. Scores: M4 5, M3 1, M5 8, M7 2, M8 8, M1 2, M2 0, M6 0. `check_clues(require_mapping=True)` on it reports unsupported bonus measures M2, M3, M6 and graduation breaks at M1, M2, M3, M4. A story edit that supports M2 and M6 and re-weights is therefore needed, as the research predicted.

Clue-derived good start (procedure of D-19, codes in config measure order M1..M10) and placement of the research archetypes as static plans. Cells: final KZ, share of in-budget static plans strictly below by KZ / by Final-Index, and share of legal in-budget swap-layer games strictly below by KZ. Good needs at least 75 in both Final-Index and swap-layer KZ; bad is judged by the share above.

| Tier | Plan | Code | KZ | KZ below (static) / FI below / KZ below (swap layer) |
|------|------|------|----|-----------------------------------------------------|
| low | clue-derived good | 2002210200 | 71 | 74 / 77 / 81 |
| low | good, bonus order (research) | 2020210200 | 71 | 74 / 77 / 81 |
| low | all-in C (M1, M3, M6, M7 at L2) | 2020022000 | 84 | 97 / 97 / 98 |
| low | all-in A (M4, M5 L3) | 0003300000 | 59 | 37 / 40 / 46 |
| low | all-in I (M2, M4 L3) | 0303000000 | 47 | 8 / 11 / 12 |
| low | bad: ignore (M9 + M10) / hoard (M6 L1) | 0000000022 / 0000010000 | 27 | 0 / 0 / 0 |
| medium | clue-derived good | 2002202200 | 67 | 55 / 58 / 64 |
| medium | good, bonus order | 2021201200 | 64 | 46 / 49 / 55 |
| medium | all-in C | 2020022000 | 81 | 91 / 92 / 94 |
| medium | all-in A | 0003300000 | 61 | 37 / 40 / 46 |
| medium | all-in I | 0303000000 | 49 | 12 / 13 / 16 |
| medium | bad: ignore / hoard | see low | 19 | 0 / 0 / 0 |
| high | clue-derived good | 2012212200 | 69 | 60 / 62 / 69 |
| high | good, bonus order | 2022201200 | 56 | 24 / 26 / 31 |
| high | all-in C | 2020022000 | 73 | 73 / 75 / 81 |
| high | all-in A | 0003300000 | 53 | 19 / 21 / 25 |
| high | all-in I | 0303000000 | 41 | 7 / 7 / 8 |
| high | bad: ignore / hoard | see low | 15 | 0 / 0 / 0 |

Findings for 06-09:

- The research expectations hold. The all-in-C archetype is top quartile in every tier (it would also pass as a "good" strategy, so a bad archetype must not be built from C-heavy bonus measures, or the wave weights must change); the naive bonus-order good is not top quartile in medium and high.
- The clue-derived good is top quartile only in low (FI 77 / swap-layer KZ 81). In medium (58 / 64) and high (62 / 69) it misses the 75 mark on both populations, so BAL-07 needs tuning there.
- All-in I is bottom quartile in every tier (Final-Index below 11 / 13 / 7 and swap-layer KZ below 12 / 16 / 8). All-in A is bottom quartile only in high (21 / 25) and sits at 40 / 46 in low and medium, so it is a poor "bad" candidate there. "Ignore" and "hoard" (0 in every cell) are the safe bad entries.
- Non-clue guard: with the provisional mapping 98 to 100 % of the top 1 % in-budget plans contain a measure without clue points (M2, M3, M6 are unclued and appear in the best plans), so the 20 % floor of D-19 holds with a wide margin today.

## Task Commits

1. **Task 1 RED:** `6c008d9` test(06-07): add failing tests for the clue to measure mapping
2. **Task 1 GREEN:** `f4f9902` feat(06-07): clue to measure mapping with importance checks and matrix column
3. **Task 2 RED:** `0b48eab` test(06-07): add failing tests for the reference_strategies block
4. **Task 2 GREEN:** `ef86b21` feat(06-07): reference_strategies config key with validator and shared path builder
5. **Task 3 RED:** `6042fb8` test(06-07): add failing tests for quartile placement and the clue-derived good strategy
6. **Task 3 GREEN:** `ec1b6e0` feat(06-07): quartile placement, clue-derived good strategy and the non-clue guard

## Decisions Made

See `key-decisions`. Open for D-04: scale and floors of the clue score (research A4), the reading of the 14 clues (A6) and the both-population placement rule (A9); the 06-09 plan proposes the real mapping and concrete strategies.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Coverage test broke on the mini `reference_strategies` block**
- **Found during:** Task 2 (full fast suite)
- **Issue:** `tests/test_texts_coverage.py::test_a_new_config_measure_without_text_fails_coverage` adds a fifth measure M99 to the mini raw config; the new block's selections name exactly four measures, so the config failed to load with `ref.measure_set`.
- **Fix:** the test deletes `reference_strategies` from its raw copy before adding the measure.
- **Files modified:** tests/test_texts_coverage.py
- **Commit:** ef86b21

Otherwise the plan was executed as written. `ClueRow.measures` defaults to `""` so existing constructions still work; `bonus_importance` is typed against `Config`.

## Known Stubs

None. `content/clues.toml` deliberately has no mapping and `simulation_config.json` no `reference_strategies` block yet (D-04 freeze, 06-09 proposes both); this is the planned state, not a stub.

## Threat Flags

None. New surface is local file parsing only (`clues.toml`, config JSON) with type validation and validator codes (T-06-16); the mapping reaches no player document (T-06-17); `git diff --exit-code -- content print tests/golden simulation_config.json` is clean (T-06-18); the good start must equal the algorithm output and placement uses two populations (T-06-19).

## Issues Encountered

- The `HandCalcWarning` for the exfil slope 17/7 is pre-existing and appears on every load (Phase-6 Pitfall 3).

## Next Phase Readiness

06-08/06-09 can write the real mapping and `reference_strategies` into candidate files and verify them with `uv run pytest tests/test_strategies.py -m slow --runxfail --planspiel-config <cand> --planspiel-content-dir <dir>`; 06-10 adopts them, builds the booklet column and its `sheets.spielleitung` label from `ClueRow.measures`, and switches `require_mapping` on.

## Self-Check: PASSED

- Files exist: planspiel/strategies.py, tests/test_clues_mapping.py, tests/test_reference_strategies.py, tests/test_strategies.py
- Commits exist: 6c008d9, f4f9902, 0b48eab, ef86b21, 6042fb8, ec1b6e0
- `uv run pytest -q`: 2638 passed, 1 xfailed; `uv run pytest tests/test_strategies.py -m slow -q -rx`: 5 xfailed; `uv run planspiel clues` and `texts` 0 errors on the real content; content/, print/, tests/golden and simulation_config.json unchanged
