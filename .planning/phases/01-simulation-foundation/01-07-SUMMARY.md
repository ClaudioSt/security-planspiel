---
phase: 01-simulation-foundation
plan: 07
subsystem: simulation-enumeration
tags: [enumeration, kernel, memoization, compact-store, report, pareto, percentiles, performance, tdd]
requires: ["01-06"]
provides:
  - "planspiel/rules.py: BudgetLedger/budget_ledger, e_target_check, apply_final_events (single definitions shared by evaluate_plan and the kernel), CompactOutcome, memoized TierKernel"
  - "planspiel/enumerate.py: STORE_LAYOUT, ResultStore (16 B per combination), CompactRecord, enumerate_tier, code_from_index"
  - "planspiel/report.py: top-K x3, nearest-rank percentiles in/over budget, best in vs over budget, Pareto front, summary JSON, German console table, JSONL dump record"
  - "planspiel/simulate.py: summary default mode, --summary, --dump-jsonl, --top; legacy --output unchanged"
  - "tests: kernel conformance (incl. slow pinned-digest equality), enumeration brute-force checks, slow measured-bounds tests"
affects: [phase-02, phase-06]
tech-stack:
  added: []
  patterns:
    - "lean kernel = second composition of shared rules primitives inside rules.py, memoized by small integer tuples"
    - "array-based struct-of-arrays store, integers only; RoS derived exactly on access"
    - "kernel equality proven through the pinned golden digests of every tier (all 782,336 combinations)"
key-files:
  created:
    - planspiel/report.py
    - tests/test_kernel_conformance.py
    - tests/test_enumeration.py
    - tests/test_enumeration_perf.py
    - tests/support/peak_memory.py
  modified:
    - planspiel/rules.py
    - planspiel/enumerate.py
    - planspiel/simulate.py
    - tests/support/harness.py
    - tests/support/digest.py
    - tests/test_single_definition.py
    - .gitignore
    - README.md
    - CLAUDE.md
key-decisions:
  - "Over-budget has one definition: rules.budget_ledger (total cost incl. event OPEX > budget + event budget delta); evaluate_plan and the kernel both call it (D-11, D-25)"
  - "Store keeps integers only (16 B per combination); RoS is exact and derived on access, None at cost 0 (D-17, D-27)"
  - "Percentile RoS values are built from a counter over distinct (damage, total cost) pairs sorted by exact Fraction value, then expanded; identical to sorting all values, but avoids 700k Fraction comparisons"
  - "--budget-max quirk preserved and pinned (it only scales --budget-utilization); legacy filter flags without --output and summary flags with --output are rejected with exit 2"
requirements-completed: [FOUND-06]
duration: ~3h wall clock (about 1 h of that waiting for slow suites)
completed: 2026-10-01
status: complete
---

# Phase 1 Plan 07: Full enumeration with a compact store and report Summary

A plain `uv run python simulate_outcomes.py --budget-tier <t>` now evaluates all 782,336 dependency-valid combinations of a tier (in budget and over budget), keeps them as 16 bytes each, and writes a deterministic summary JSON plus a German console table in 44-51 s and at most 129 MB peak working set; a memoized `TierKernel` reproduces `evaluate_plan` exactly, proven by the pinned digests of all three tiers.

## Tasks

| Task | Name | Commits |
|------|------|---------|
| 1 | Shared plan helpers and memoized tier kernel | RED `5c028cd`, extraction `242ebf4`, GREEN `4bdaf1f` |
| 2 | Compact store and report (top-K, percentiles, best in/over, Pareto) | RED `4097369`, GREEN `f81cbbb` |
| 3 | Summary as default CLI mode, bounds, docs | RED `db89cdc`, GREEN `d6fdbe3`, docs `929bda4` |

## RED runs (quoted)

- Task 1: `uv run pytest tests/test_kernel_conformance.py tests/test_single_definition.py -q` -> `24 failed, 33 passed` (`AttributeError`: `rules.budget_ledger`, `rules.TierKernel`, ... missing; `AssertionError: e_target_check defined at []` for the three single-definition checks).
- Task 2: `uv run pytest tests/test_enumeration.py -q` -> `ImportError: cannot import name 'STORE_LAYOUT' from 'planspiel.enumerate'` (collection error, `1 error`).
- Task 3: `uv run pytest tests/test_enumeration.py tests/test_enumeration_perf.py -q` -> `8 failed, 25 passed` (summary-mode CLI tests failed; the `--budget-max` pin, the legacy `--output` test and some rejection cases passed immediately because they pin existing behaviour or are already argparse errors).

## GREEN runs

- Extraction commit `242ebf4`: `uv run pytest -q --ignore=tests/test_kernel_conformance.py` -> `186 passed, 4 deselected`; `uv run pytest -m slow tests/test_digest.py -q` -> `3 passed in 540.82s`; `git status --porcelain tests/golden` empty (zero golden diff).
- Kernel commit `4bdaf1f`: `uv run pytest tests/test_kernel_conformance.py tests/test_single_definition.py tests/test_characterization.py tests/test_rules_semantics.py tests/test_rules_exact.py -q` -> `95 passed`; `uv run pytest -m slow tests/test_kernel_conformance.py -q` -> `3 passed in 157.95s` (kernel digest == golden digest, all fields, every tier).
- Final verification after all commits:
  - `uv run pytest -q` -> `240 passed, 11 deselected, 44 warnings in 14.95s`
  - `uv run pytest -m slow -q -s` -> `11 passed, 240 deselected, 8 warnings in 1287.08s (0:21:27)` (3 rich digests, 3 kernel digests, harness cross-check, 3 perf tiers, dump at scale)
  - `uv run planspiel validate` -> `0 Fehler, 1 Warnung(en)` (the known exfil kz_slope 17/7 hand-calc warning)
  - `git status --porcelain` empty; `git status --porcelain tests/golden` empty; no `--update-golden` run anywhere.

## Measured bounds (Windows 11, 48 GB, uv CPython 3.12; PERF lines from the final full slow suite)

```
PERF tier=low wall_seconds=51.0 child_seconds=50.8 peak_mb=121
PERF tier=medium wall_seconds=47.6 child_seconds=47.4 peak_mb=129
PERF tier=high wall_seconds=46.8 child_seconds=46.7 peak_mb=125
PERF tier=low wall_seconds=87.5 child_seconds=87.3 peak_mb=121   (with --dump-jsonl, 782,336 lines)
```

The earlier dedicated run of `tests/test_enumeration_perf.py` gave 45.4 / 44.0 / 43.6 s and 121 / 129 / 125 MB (dump 77.3 s, 121 MB). Bounds: 120 s and 500 MB; no constant was loosened.

| Tier | Seconds | Peak MB | Bytes/record | Valid | In budget | Over budget | Best in | Best over | Gap | Pareto points |
|------|--------:|--------:|-------------:|------:|----------:|------------:|--------:|----------:|----:|--------------:|
| low | 51.0 | 121 | 16 | 782,336 | 69,454 | 712,882 | 100 | 85 | -15 | 22 |
| medium | 47.6 | 129 | 16 | 782,336 | 124,321 | 658,015 | 100 | 85 | -15 | 23 |
| high | 46.8 | 125 | 16 | 782,336 | 197,753 | 584,583 | 100 | 85 | -15 | 25 |

The per-tier one-liners printed `69454 100 85 -15 22`, `124321 100 85 -15 23`, `197753 100 85 -15 25`, exactly the expected values. Summary files are about 31 KB each; the dump check counted 782,336 lines with `over_budget` true equal to the golden 712,882.

## What was built

- `rules.py`: `budget_ledger`/`BudgetLedger` (single over-budget definition), `e_target_check`, `apply_final_events` extracted verbatim from `evaluate_plan`/`simulate_selection` (goldens unchanged), then `CompactOutcome` and `TierKernel`, which composes only shared primitives and memoizes `(wave, c, i, a)`, `(wave, reduction, recovery)`, `(wave, e_scaled)` and `(wave, e_target_delta, reduction, event_kz)`.
- `enumerate.py`: `ResultStore` with columns `I B H i I B`, `enumerate_tier` (one kernel, no filter, optional streamed `on_outcome`), `code_from_index`.
- `report.py`: summary with top-K by KZ, RoS, Final-Index (tie-breaks as in the plan), nearest-rank percentiles of KZ and RoS split in/over budget, best in vs over with `kz_gap`, Pareto front over `(own_cost, kz_final)`, deterministic `write_summary` (UTF-8, LF), German `format_console`, `dump_record`.
- `simulate.py`: default summary mode, `--summary`, `--dump-jsonl`, `--top`; `--output` path unchanged; rejections (exit 2) for legacy filters without `--output` and summary flags with `--output`; unknown tier names the valid tiers.
- Tests: `tests/test_kernel_conformance.py` (golden, mini, random, negative-tie override, slow digest), `tests/test_enumeration.py` (brute force on the mini config, CLI modes, `--budget-max` pin), `tests/test_enumeration_perf.py` and `tests/support/peak_memory.py`.
- Docs: README "Simulation (alle Outcomes)" and CLAUDE.md balance/large-file bullets; `.gitignore` covers `simulation_summary*.json` and `simulation_full*.jsonl`.

## Deviations from Plan

None - plan executed as written. Implementation details worth noting (no behaviour change versus the plan):

- `--top` defaults to `None` internally (the default K is applied after validation), so that `--top` together with `--output` is rejected regardless of the value given.
- `parse_args` is built from a new `build_parser()` so that `main` can raise the unknown-tier error through the same parser.
- The summary memoizes exact RoS and Final-Index by integer keys (distinct damage/cost pairs) and builds sorted RoS percentile lists from a counter over those pairs; the result is identical to sorting all values.

## Interface differences from the `<interfaces>` block

None that matter. `planspiel/enumerate.py` still contains `LEVEL_OPTIONS` and `iter_selections` unchanged. `e_target_check(wave, e_value, e_target)` receives the exact E-value (`Fraction(e_scaled, ws)` in the kernel).

## Known Stubs

None.

## Threat Flags

None. Dump and summary paths are explicit user choices (T-01-21 accepted); mitigations for T-01-19 (kernel digests equal goldens), T-01-20 (16 B store, 121-129 MB, streamed dump), T-01-22 (gitignore, `git status` clean) and T-01-23 (fixed argument lists, explicit cwd) are in place.

## Notes for later phases

- Phase 2 swaps the ledger rules inside `budget_ledger` and `apply_final_events`; the kernel and `evaluate_plan` pick the change up together, and the kernel digests must then be regenerated with the rich goldens.
- Phase 6 sweeps can reuse `TierKernel.evaluate` and `enumerate_tier` directly; the store is the hand-off (`ResultStore.record(i)` gives code index, KZ, own cost, exact RoS, damage in euros, over-budget flag).
- Final-Index in the report is labelled provisional (default weights 1/1) until Phase 6 rescales it (BAL-03).

## Self-Check: PASSED

- Commits `5c028cd`, `242ebf4`, `4bdaf1f`, `4097369`, `f81cbbb`, `db89cdc`, `d6fdbe3`, `929bda4` exist in `git log`.
- `planspiel/report.py`, `tests/test_kernel_conformance.py`, `tests/test_enumeration.py`, `tests/test_enumeration_perf.py`, `tests/support/peak_memory.py` exist.
- Fast suite 240 passed, slow suite 11 passed, goldens untouched, working tree clean before this summary.
