---
phase: 06-rebalance
plan: 01
subsystem: testing
tags: [overspend-gate, move-paths, calibration, test-infrastructure, parallel]

requires:
  - phase: 02-rule-changes
    provides: static overspend gate (D-17), swap layer (D-24), TierTables, evaluate_path
provides:
  - move-path overspend gate (swap layer, window-1 and window-2 single moves, start-lowered trim) in planspiel/gate.py
  - X calibration report (X = max + 1, raw and capped) behind `planspiel gate --paths [--narrow] [--jobs N]`
  - candidate-config test infrastructure (--planspiel-config, --planspiel-content-dir, TUNING_TARGET, cached enumerations)
  - parallel.map_tiers, swap-layer per-start aggregates, TierTables.single_moves
affects: [06-02, 06-03, 06-04, 06-05, 06-06, 06-07, 06-08, 06-09, 06-10]

tech-stack:
  added: []
  patterns:
    - "xfail TUNING_TARGET plus --runxfail for candidate-config checks (single approach for all Phase-6 checks)"
    - "single-pass family scan: pool arrays plus per-(start, started steps) maximum pre-review KZ, evaluated after lowering_closure"
    - "module-level worker functions plus ProcessPoolExecutor per tier (Windows spawn)"

key-files:
  created:
    - planspiel/parallel.py
    - tests/support/candidate.py
    - tests/test_candidate_support.py
    - tests/test_gate_paths.py
  modified:
    - planspiel/gate.py
    - planspiel/enumerate.py
    - planspiel/rules.py
    - planspiel/cli.py
    - tests/conftest.py
    - tests/test_swap_layer.py
    - tests/test_single_definition.py
    - pyproject.toml
    - README.md
    - CLAUDE.md

key-decisions:
  - "Trim definition of the path gate is start-lowered (lower or cancel levels of the START plan, then any legal continuation of the family's pool); the narrow same-swap-pair definition is a diagnostic behind --narrow and never enters the verdict or the calibration"
  - "Raw/capped KZ reading (research A1) implemented as pair: min_x_strict on the unfloored penalty, min_x_capped on the 0..100-clamped outcome; both reported, calibration uses the maximum of both; flagged for confirmation at D-04"
  - "Single-pass aggregation per (start, started steps) for the main families: min X, weak X, unlosable and untrimmable path counts and the witness are exact; histogram and violations count groups, labelled as such in the report"
  - "xfail (TUNING_TARGET) plus --runxfail chosen over a separate default-deselected marker, so the targets stay visible in every -m slow run"

patterns-established:
  - "Candidate checks: `uv run pytest -m balance --runxfail --planspiel-config <cand> --planspiel-content-dir <dir>`"
  - "Brute-force oracle for gate families built only from rules.Path / rules.evaluate_path, never TierTables"

requirements-completed: [BAL-01]

coverage:
  - id: D1
    description: "Move-path overspend gate (swap, window-1, window-2; start-lowered; narrow diagnostic) equal to a brute force over rules.evaluate_path on the mini config"
    requirement: BAL-01
    verification:
      - kind: unit
        ref: "tests/test_gate_paths.py::test_mini_path_gate_equals_brute_force, ::test_mini_narrow_diagnostic_equals_brute_force"
        status: pass
    human_judgment: false
  - id: D2
    description: "Calibration X = max + 1 over raw and capped minima, tiers and families with binding cell; planspiel gate --paths report"
    requirement: BAL-01
    verification:
      - kind: unit
        ref: "tests/test_gate_paths.py::test_calibrate_*, ::test_gate_paths_*"
        status: pass
      - kind: integration
        ref: "uv run planspiel gate --paths --jobs 3 (real config, 9m49s)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Candidate-config test infrastructure (options, fixtures, TUNING_TARGET, cached enumerations, map_tiers)"
    verification:
      - kind: unit
        ref: "tests/test_candidate_support.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "Raw/capped interpretation (research A1) and start-lowered trim definition acceptable for the calibration"
    requirement: BAL-01
    verification: []
    human_judgment: true
    rationale: "Both are definition choices that move the recommended X (narrow definition would force a much larger X); the user confirms them at checkpoint D-04"

duration: 60min
completed: 2026-10-28
status: complete
---

# Phase 6 Plan 01: Move-path overspend gate and X calibration Summary

**`planspiel gate --paths` checks the legal swap layer plus single moves in windows 1 and 2 with a start-lowered trim, reports raw and capped minimum X per tier and family, and states `X = max + 1` with the binding cell; the shared candidate-config test infrastructure for all later Phase-6 checks is in place.**

## Performance

- **Duration:** about 60 min (including 3 long measurement runs)
- **Started:** 2026-10-28T19:06Z
- **Completed:** 2026-10-28T20:05Z
- **Tasks:** 3 (all TDD: RED commit, then GREEN commit)
- **Files modified:** 14 (4 new)

## Accomplishments

- Path gate in `planspiel/gate.py`: `PATH_FAMILIES`, `PathScan`, `path_gate_from_scan`, `gate_paths_tier`, narrow diagnostic `tausch_eng`, `capped_required_x`, `Calibration`/`calibrate`, JSON and German report functions, `paths_worker`. `GateResult` gained `min_x_capped` as last field (not serialized, golden `gate_<tier>.json` unchanged; slow golden test passes).
- Brute-force equality: for every tier of the mini config each family (and the narrow diagnostic) equals a brute force that builds every path as `rules.Path` and evaluates it with `rules.evaluate_path` (over-budget counts, min X strict/weak/capped, histogram, violations, unlosable, untrimmable, verdict, witness start).
- `planspiel gate` without `--paths` is unchanged (stdout identical to the pre-change output on the mini config, apart from the Windows CRLF capture); with `--paths` it prints the static report, one report per family and tier, the calibration block and the verdict (exit code from static gate and non-narrow families only).
- Test infrastructure: `--planspiel-config`, `--planspiel-content-dir`, session fixtures `balance_config_path` / `balance_content_dir`, `balance` marker, `TUNING_TARGET`, cached static stores, summaries, swap layers and tier tables, `parallel.map_tiers` with module-level workers, `enumerate_swap_layer(...)["starts"]` (best/worst in-budget final and count per start), `TierTables.single_moves`.
- README ("Überziehungs-Gate") and CLAUDE.md document the new command, the trim definition and the candidate-check command. No X value is written into prose.

## Measured results on the real config (today's simulation_config.json)

Minimum X (strict = raw; capped is identical in every cell because the clamp only matters at KZ 0 and no trimmed version ends there; unlosable and untrimmable are 0 in every cell):

| Family | low | medium | high |
|--------|-----|--------|------|
| static reference (pinned gate) | 9 | 5 | 3 |
| tausch (swap layer, start-lowered) | 9 | 5 | 2 |
| fenster1 (window-1 move, union pool) | 9 | 5 | 3 |
| fenster2 (window-2 move, union pool) | 5 | 2 | 1 |
| tausch_eng (narrow diagnostic, not in verdict) | 14 | 7 | 5 |

Weak X: static 8/4/3, tausch 8/4/2, fenster1 8/4/2, fenster2 4/2/1, narrow 13/6/4. This reproduces the research table exactly (swap 9/5/2, window-1 9/5/3, window-2 5/2/1, narrow 14/7/5). Path counts per tier: swap layer 37,348,851 legal games, window-1 and window-2 22,274,048 each (narrow family 37,300,736 swap paths).

Calibration line: `Empfohlenes X = Maximum + 1 = 10 (bestimmend: Tier low, Familie statisch, roh)`; config X = 9 is "nicht kalibriert"; target X <= 5 is "verfehlt". The move families add no demand beyond the static gate at today's config. Every static and non-narrow family passes at config X = 9.

Wall times (6-core Windows machine):

| Run | Wall time |
|-----|-----------|
| `uv run planspiel gate --paths --jobs 3` | 9 min 49 s (a 2 min fast suite ran concurrently) |
| `uv run pytest tests/test_gate_paths.py -m slow` (pass check + calibration check, `--jobs 3` inside) | 9 min 36 s: 1 passed, 1 xfailed |
| `uv run planspiel gate --paths --narrow --jobs 3` | 18 min 43 s (narrow adds two swap-layer passes and about 90 pair closures per tier) |
| `uv run planspiel gate` (static, mini) | under 1 s |

The runtime contract (at most 20 min with `--jobs 3`) holds, also with `--narrow`.

## Task Commits

1. **Task 1 RED:** `abab4b6` test(06-01): failing tests for candidate support, start aggregates and single moves
2. **Task 1 GREEN:** `96a15bb` feat(06-01): candidate-config test support, map_tiers, start aggregates and single moves
3. **Task 2 RED:** `897c300` test(06-01): failing tests for the move-path gate and calibration
4. **Task 2 GREEN:** `2db7ece` feat(06-01): move-path gate families, narrow diagnostic and X calibration
5. **Task 3 RED:** `b9855fd` test(06-01): failing tests for gate --paths and the slow balance checks
6. **Task 3 GREEN:** `25d7e62` feat(06-01): planspiel gate --paths with --narrow and --jobs
7. **Task 3 docs:** `c635df8` docs(06-01): document gate --paths, the trim definition and candidate checks

## Decisions Made

See `key-decisions` in the frontmatter. Open for D-04: confirm the raw/capped reading (A1) and the start-lowered definition. Under the start-lowered definition the demanded X is 10 (low, static); the narrow definition would demand 15, which the user should see next to the shipped numbers.

## Deviations from Plan

None - plan executed as written. Minor implementation notes:

- `capped_required_x` is implemented so that it literally uses `rules.clamp_kz` and verifies minimality in both directions; it equals the strict X whenever the trimmed final is above 0, as the plan states, so raw and capped columns are identical on the real config.
- The narrow witness carries no trimmed start code (the narrow pools are plain `b` arrays without tie-break keys); the report prints the trimmed end KZ only.
- Narrow witness choice differs from the research example (first path with the maximum X in swap-iterator order, e.g. low: start 0200133001, swap M10 -> M1 level 1, X 14), same X.

## Known Stubs

None.

## Issues Encountered

- A test assertion `narrow.min_x_strict >= tausch.min_x_strict` was wrong (the narrow family excludes the D-22 exempt static paths) and was removed; the brute-force comparison covers the narrow family exactly.
- Pre-existing, out of scope: `HandCalcWarning` for the exfil slope 17/7 appears in every load of the real and mini config (Phase-6 Pitfall 3, parameterised severity handled by a later plan).

## Threat Flags

None. The new surface is local CLI flags (`--paths`, `--narrow`, `--jobs`) and process workers that reload the config from its path through `load_config` (T-06-01); workers are capped at the tier count (T-06-02); the plain gate output is unchanged and narrow never enters the verdict (T-06-03); no output files are written (T-06-04).

## Next Phase Readiness

Plans 06-02 to 06-10 can use `tests/support/candidate.py` (cached `static_stores`, `static_summaries`, `swap_layers`, `tier_tables`, `TUNING_TARGET`) with `--planspiel-config` / `--planspiel-content-dir`; the tuning plan can run `uv run planspiel gate --config <cand> --paths [--narrow] --jobs 3`. The golden `gate_paths_<tier>.json` is intentionally created in plan 06-10 after the D-04 approval (D-04 freeze: simulation_config.json, content/, goldens and final_documents/ untouched).

## Self-Check: PASSED

- Files exist: planspiel/parallel.py, tests/support/candidate.py, tests/test_candidate_support.py, tests/test_gate_paths.py, planspiel/gate.py (path gate)
- Commits exist: abab4b6, 96a15bb, 897c300, 2db7ece, b9855fd, 25d7e62, c635df8
- `uv run pytest -q`: 2332 passed (fast suite); `uv run pytest -m slow tests/test_overspend_gate.py`: 6 passed (goldens unchanged); `uv run pytest tests/test_gate_paths.py -m slow`: 1 passed, 1 xfailed
