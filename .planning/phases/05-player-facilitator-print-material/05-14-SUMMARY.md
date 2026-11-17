---
phase: 05-player-facilitator-print-material
plan: 14
subsystem: rules
tags: [reference-paths, answer-keys, format-approx, config, validator, d-18, d-22, print-10]

requires:
  - phase: 05-player-facilitator-print-material
    provides: rules.path_trace (05-11), cfg.final_index weights (05-13), enumerate_swap_layer and summarize_swap_layer (Phase 2)
provides:
  - planspiel.refpaths with reference_path, mechanics_score, voluntary_moves, review_deltas, swap_layer_median, Candidate, candidate_paths, format_candidate, format_tier_report
  - CLI subcommand planspiel referenzpfade [--config] [--tier] [--median] [--out] [--starts] [--keep]
  - fmt.format_approx(value, places=2)
  - Config.reference_plans (plain dict, defaulted) and validate.check_reference_plans
  - reference_plans block in simulation_config.json with the three user-approved paths
affects: [05-15, 05-16]

tech-stack:
  added: []
  patterns:
    - "Candidate finder on legal paths only: every candidate goes through rules.evaluate_path / path_trace, never the static reference plan (Pitfall 10)"
    - "Selection heuristic kept out of rules.py and out of FORMULA_FUNCTIONS: mechanics_score is not a game rule"
    - "Checkpoint answer pinned verbatim; tests state the approved structure, never computed numbers"

key-files:
  created:
    - planspiel/refpaths.py
    - tests/test_refpaths.py
    - tests/test_reference_plans.py
  modified:
    - planspiel/cli.py
    - planspiel/config.py
    - planspiel/fmt.py
    - planspiel/validate.py
    - simulation_config.json
    - tests/test_print_fmt.py
    - tests/test_single_definition.py

key-decisions:
  - "Config.reference_plans sits before the trailing practice field (both defaulted), because the 05-13 guard and the orchestrator note require practice to stay last"
  - "Candidates are taken from different starts first, then filled in rank order, so the three proposals are not near-copies"
  - "mechanics_score counts only change windows without a swap as voluntary moves; the exact check including the swap repair is voluntary_moves(cfg, path)"
  - "The Budget Review criterion of mechanics_score needs the tier KZ changes (review_deltas(cfg)); without them that point is skipped"
  - "Voluntary moves are searched for every swap path, not only in-budget ones, because a downgrade in window 2 can bring a path into budget"

patterns-established:
  - "format_approx prints exactly the given decimals after the approximation sign and trims nothing, so approximate values read uniformly (2,40, not 2,4)"

requirements-completed: []

duration: ~55 min plus about 5 min background candidate runs and 12 min slow/pdf suites
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 14: Reference paths per tier Summary

**`uv run planspiel referenzpfade` proposes legal, in-budget game paths near the swap-layer median (start, mandatory Kurswechsel swap, one voluntary move) ranked by the mechanics they touch; the user approved Low 2, Medium 1H and High 3, and they are pinned in `simulation_config.json` `reference_plans` with real-config legality and mechanics tests.**

PRINT-10 spans 05-13 to 05-16, so the requirement is intentionally not marked complete here. 05-15 keys the facilitator master sheet on these paths and reuses `format_approx`.

## Accomplishments

- `planspiel/refpaths.py` (Task 1): `candidate_paths` takes the in-budget starts whose static final KZ is within 3 of the swap-layer median and that allow a swap, ranks them by the static mechanics score, expands the best 40 by every legal canonical Kurswechsel swap and every single voluntary move in window 2, keeps in-budget paths within 2 of the median, and ranks by mechanics score, distance to the median, code order. `format_candidate` prints per wave E-Wert, Bonus, GR, Fall, Schaden (before and after recovery), KZ change (exact and rounded), KZ, own OPEX, window cost, external effects and Restbudget, then Budget Review, KZ final, RoS and Final-Index (vorläufig).
- `fmt.format_approx` (T-05-53): exact text when the value terminates within the decimals, else `≈` plus the value rounded half away from zero through `rounding.round_half_away_frac`; registered in `FORMULA_FUNCTIONS`.
- Config and validator: `Config.reference_plans` and `check_reference_plans` (`ref.unknown_tier`, `ref.measure_set`, `schema.range`/`schema.type` for levels, `ref.window_count`, `ref.unknown_measure`, `ref.swap_same_measure`, `schema.keys`); an absent block is allowed.
- Pinned block (Task 3, T-05-52): one path per tier, proven by tests to be legal, in budget, with the swap in the Kurswechsel window, a voluntary move, and a Fall-3 wave, a recovery wave, a wave with a bonus met and one missed, a non-zero event KZ (7 of 7 mechanics points).

## RED runs

- Task 1: `uv run pytest tests/test_refpaths.py ... -x -q` failed at collection with `ImportError: cannot import name 'refpaths' from 'planspiel'`; `uv run pytest tests/test_reference_plans.py tests/test_print_fmt.py tests/test_single_definition.py -q` failed at collection with `ImportError: cannot import name 'format_approx' from 'planspiel.fmt'`. Commit `58a0b7b`.
- Task 3: `uv run pytest tests/test_reference_plans.py -q` gave 11 failed, 17 passed (first failure `assert set() == {'high', 'low', 'medium'}`: the block is absent). Commit `4602d88`.

## Candidates presented at the checkpoint

Swap-layer in-budget p50 of the final KZ used as the median: low 60, medium 62, high 62 (one run of `uv run planspiel referenzpfade --tier <t> --out build/referenzpfade`, 312 to 320 s per tier; output in `build/referenzpfade/referenzpfade_{low,medium,high}.txt`, not committed). Headers as printed:

- `Referenzpfade Tier low: Median 60 (End-KZ im Budget, Tausch-Schicht), Toleranz ±2, 3 Kandidat(en)`
- `Referenzpfade Tier medium: Median 62 (End-KZ im Budget, Tausch-Schicht), Toleranz ±2, 3 Kandidat(en)`
- `Referenzpfade Tier high: Median 62 (End-KZ im Budget, Tausch-Schicht), Toleranz ±2, 3 Kandidat(en)`

Every candidate had `Mechanik-Punkte 7 von 7`. Notation: measure and level, Fälle for waves 1/2/3, KZ path from the start KZ through the waves, then the Budget Review change and the final KZ.

| Tier | # | Start | Kurswechsel | Voluntary move (window 2) | Fälle | KZ path | Restbudget | RoS | Final-Index |
|------|---|-------|-------------|---------------------------|-------|---------|------------|-----|-------------|
| low | 1 | M4 1, M7 2, M9 3, M10 3 | M4 gegen M8 L2 (20 k€) | cancel M9 | 1/3/3 | 50, 44, 48, 55, +5, 60 | 34 | ≈ 0,26 | ≈ 85,66 |
| low | 2 | M4 1, M6 3, M7 1, M9 3, M10 1 | M4 gegen M5 L2 (54 k€) | cancel M6 | 3/2/1 | 50, 50, 57, 55, +5, 60 | 30 | ≈ 0,26 | ≈ 85,81 |
| low | 3 | M4 1, M5 1, M7 2, M8 1, M9 2, M10 2 | M4 gegen M6 L2 (8 k€) | cancel M5 | 3/2/1 | 50, 47, 57, 50, +10, 60 | 56 | ≈ 0,28 | ≈ 87,55 |
| medium | 1 | M4 1, M7 2, M8 1, M9 3, M10 3 | M4 gegen M5 L1 (24 k€) | cancel M5 | 3/2/1 | 42, 39, 49, 52, +10, 62 | 54 | ≈ 0,09 | ≈ 70,57 |
| medium | 1H | as 1 | as 1 | downgrade M7 L2 to L1 | 3/2/1 | 42, 39, 49, 52, +10, 62 | 56 | ≈ 0,09 | ≈ 71,22 |
| medium | 2 | M4 1, M6 2, M8 3, M9 3, M10 2 | M4 gegen M7 L1 (4 k€) | downgrade M8 L3 to L2 | 3/3/2 | 42, 46, 42, 57, +5, 62 | 49 | ≈ 0,15 | ≈ 77,31 |
| medium | 3 | M4 1, M5 1, M6 1, M8 3, M9 2, M10 2 | M4 gegen M7 L1 (4 k€) | upgrade M7 L1 to L2 | 3/3/2 | 42, 40, 42, 57, +5, 62 | 46 | ≈ 0,07 | ≈ 69,28 |
| high | 1 | M4 1, M5 1, M6 1, M8 3, M9 3, M10 2 | M4 gegen M7 L1 (4 k€) | upgrade M7 L1 to L2 | 3/3/2 | 34, 34, 37, 57, +5, 62 | 45 | ≈ 0,06 | ≈ 68,10 |
| high | 2 | M4 1, M5 2, M6 1, M7 1, M8 1, M9 3, M10 3 | M4 gegen M3 L1 (8 k€) | add M4 L1 again | 3/2/3 | 34, 37, 44, 57, +5, 62 | 28 | ≈ 0,20 | ≈ 82,48 |
| high | 3 | M4 1, M5 2, M6 3, M9 3, M10 3 | M4 gegen M8 L2 (20 k€) | cancel M6 | 3/2/3 | 34, 40, 37, 57, +5, 62 | 42 | ≈ 0,45 | ≈ 107,33 |

Medium 1H was a hand pick (D-22): the finder's medium 1 cancels M5, which it had brought in one window earlier, so the move was replaced by a downgrade of the spent wave-2 bonus measure M7. It was re-evaluated with `rules.path_trace` (`build/referenzpfade/handauswahl_medium.txt`): W1 E-Wert 24,6, Fall 3, Schaden 115.200 € (vor Recovery 128.000 €), KZ change −3 (exakt −2,8); W2 E-Wert 24,2, Fall 2, Schaden 0 €, +10; W3 E-Wert 22,5, Fall 1, Schaden 140.000 €, +3; Budget Review +10, KZ final 62, Restbudget 56 k€, Gesamtschaden 255.200 €.

Recommendation given: Low 2, Medium 1H, High 3.

## User answer (checkpoint, D-26 Q2)

Verbatim: "Empfehlung (Low 2, Med 1H, High 3)".

## Pinned reference paths

Notation: measure and level, all other measures 0. Window 1 follows wave 1 (Kurswechsel swap), window 2 follows wave 2 (voluntary move).

| Tier | Start | Window 1 selection (swap) | Window 2 selection |
|------|-------|---------------------------|--------------------|
| low | M4 1, M6 3, M7 1, M9 3, M10 1 | M5 2, M6 3, M7 1, M9 3, M10 1 (M4 gegen M5) | M5 2, M7 1, M9 3, M10 1 (M6 cancelled) |
| medium | M4 1, M7 2, M8 1, M9 3, M10 3 | M5 1, M7 2, M8 1, M9 3, M10 3 (M4 gegen M5) | M5 1, M7 1, M8 1, M9 3, M10 3 (M7 2 to 1) |
| high | M4 1, M5 2, M6 3, M9 3, M10 3 | M5 2, M6 3, M8 2, M9 3, M10 3 (M4 gegen M8) | M5 2, M8 2, M9 3, M10 3 (M6 cancelled) |

Traced with `rules.path_trace` after pinning: low KZ final 60, Restbudget 30 k€, RoS 8/31, Fälle 3/2/1; medium KZ final 62, Restbudget 56 k€, RoS 77/835, Fälle 3/2/1; high KZ final 62, Restbudget 42 k€, RoS 451/995, Fälle 3/2/3; all in budget. These match the numbers shown at the checkpoint.

## Verification

- `uv run pytest -q`: 2219 passed, 140 deselected (baseline 2144, +75 new tests), 107 s.
- `uv run planspiel validate`: 0 errors, 1 warning (the known 17/7 KZ-slope warning).
- `uv run planspiel gate`: bestanden (the block is outside the enumeration).
- `uv run pytest -m slow tests/test_digest.py tests/test_overspend_gate.py -q`: 9 passed in 590.62 s; enumeration digests and gate goldens are unchanged.
- `uv run pytest -m pdf -q`: 118 passed (142 s), run as a safety check because the config file changed.
- `uv run pytest tests/test_reference_plans.py tests/test_refpaths.py tests/test_characterization.py tests/test_enumeration.py tests/test_validate.py -q`: 148 passed.
- `git status --porcelain final_documents/generated`: empty.

## Task Commits

1. Task 1 RED: `58a0b7b` test(05-14): add failing reference path and format_approx tests
2. Task 1 GREEN: `e35b44b` feat(05-14): propose legal reference paths per tier
3. Task 2: checkpoint decision, no commit (candidates in `build/referenzpfade/`, not committed)
4. Task 3 RED: `4602d88` test(05-14): add failing real-config reference path tests
5. Task 3 GREEN: `554e9a3` feat(05-14): pin the approved reference paths per tier

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `Config.reference_plans` placed before `practice`, not after it**
- **Found during:** Task 1 full-suite run
- **Issue:** The plan says "trailing, after `practice`", but `tests/test_final_index_config.py::test_final_index_precedes_practice_in_the_config_fields` (05-13) and the orchestrator note require `practice` to stay the last field; the test failed with `reference_plans` last.
- **Fix:** both fields have defaults, so `reference_plans` was moved above `practice`; `tests/test_reference_plans.py` asserts the order.
- **Files modified:** planspiel/config.py, tests/test_reference_plans.py
- **Commit:** e35b44b

### Other notes

- The finder picks candidates from different starts first (not in the plan), so the checkpoint showed three distinct proposals.
- `format_approx` rejects `places < 1` with `ValueError`.
- Voluntary moves are searched for every swap path, not only in-budget ones (the plan text says in-budget swap paths); the final path must still be in budget and within 2 of the median.
- Two scratch slips during the run (an empty heredoc piped into `uv run python -I -` twice, one `python3 -c`) exited immediately and changed nothing.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. T-05-52 (illegal or unapproved path as answer key) is mitigated: candidates come only from rules-legal paths, the validator checks references and ranges, real-config tests check legality, budget, swap window, voluntary move and mechanics, and the paths were pinned verbatim from the recorded answer (05-15 adds the build guard). T-05-53 (wrong rounding or approximation shown as exact) is mitigated by `format_approx` through `rounding.round_half_away_frac` with tests for both signs and exact values, and its registration in `FORMULA_FUNCTIONS`. T-05-49 is accepted as planned (about 5 minutes per tier, one-off command, not in the default suite).

## Next Phase Readiness

05-15 can read `refpaths.reference_path(cfg, tier)`, `rules.path_trace` and `fmt.format_approx` for the facilitator master sheet and must add its own build guard that the pinned paths stay legal. The paths and the final-index weights are provisional until the Phase 6 rebalance (D-18, BAL-03); `uv run planspiel referenzpfade` re-proposes candidates then.

## Self-Check: PASSED

- Created files exist: `planspiel/refpaths.py`, `tests/test_refpaths.py`, `tests/test_reference_plans.py`.
- Commits `58a0b7b`, `e35b44b`, `4602d88`, `554e9a3` are in `git log`.
- `build/referenzpfade/referenzpfade_low.txt`, `_medium.txt`, `_high.txt` exist (not committed).
