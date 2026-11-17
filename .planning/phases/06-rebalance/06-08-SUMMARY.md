---
phase: 06-rebalance
plan: 08
subsystem: testing
tags: [balance-report, top-k, pareto, baseline-comparison, bal-04]

requires:
  - phase: 06-rebalance
    provides: gate.paths_worker/calibrate (06-01), validate hand-calc error mode (06-02), index_weights (06-03), choices (06-04), rewarding (06-05), spread (06-06), strategies and clue mapping (06-07)
provides:
  - summarize_tier keys top_in_budget and pareto_in_budget, pareto_front(store, in_budget_only)
  - planspiel/balance.py: build_balance_report, report_json, format_balance_report, config_diff, format_config_diff, compare_reports, format_comparison, MISSING, main(argv) with the full CLI
  - one consolidated, config- and content-aware report command (balance_analysis.py) with a per-block verdict and an exit code
affects: [06-09, 06-10]

tech-stack:
  added: []
  patterns:
    - "Every report block is {passed: True/False/None, failures, data}; None marks an informational block or a part the run did not compute (with a German note), and does not count toward the verdict"
    - "Final-Index override by dataclasses.replace(cfg, final_index=weights) so every FI-based metric follows one weight source (baseline column uses the candidate's weights)"

key-files:
  created:
    - tests/test_balance_report.py
  modified:
    - planspiel/report.py
    - planspiel/balance.py
    - tests/test_enumeration.py
    - tests/test_final_index_config.py
    - tests/test_wrappers.py
    - tests/test_environment.py
    - README.md
    - CLAUDE.md

key-decisions:
  - "--layers static computes the static enumeration, the static gate, hand-calc, Final-Index block, clue mapping and the static part of the spread; choices, reference strategies, rewarding and the cross-tier choice block need the swap layer and are reported as 'nicht berechnet (nur mit --layers all)' (choices_tier is monolithic, so its static half is not split out)"
  - "Per-tier blocks hold their own failures (check_x called with a single tier); the cross-tier choices block carries only the tier-pair lines (check_choices over all tiers minus the per-tier lines), so no failure is counted twice"
  - "Verdict count N is the number of failed blocks; failure lines are prefixed with the block label (tier name not repeated, the lines carry it)"
  - "Input errors (invalid config, missing texts or clues) raise from build_balance_report and main prints FEHLER and returns 2 instead of a partial verdict; 0/1 are reserved for the verdict (T-06-20)"
  - "Final-Index block keeps the weights of the config file as configured_weights (information row only); the data-based k and the KZ share use the override weights"

patterns-established:
  - "Baseline comparison builds the baseline report with index_weights=<candidate>.final_index, so the interim k = 1 of the committed config never enters a tuning comparison"

requirements-completed: [BAL-04]

coverage:
  - id: D1
    description: "In-budget top-K (KZ, RoS, Final-Index) and in-budget Pareto front next to the unfiltered optima; additive keys, format stays 1"
    requirement: BAL-04
    verification:
      - kind: unit
        ref: "tests/test_balance_report.py (brute-force equality on the mini config, synthetic Pareto), tests/test_enumeration.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "Consolidated report: blocks per tier and across tiers with verdicts, static and all layers, paths, Final-Index override, JSON form, German text"
    requirement: BAL-04
    verification:
      - kind: unit
        ref: "tests/test_balance_report.py (mini config and content, layers static and all, paths on)"
        status: pass
      - kind: integration
        ref: "uv run python balance_analysis.py on the real config (static 2 min 12 s, all+paths 21 min 53 s)"
        status: pass
    human_judgment: false
  - id: D3
    description: "config_diff, compare_reports and the --baseline-config comparison with the candidate's Final-Index weights"
    requirement: BAL-04
    verification:
      - kind: unit
        ref: "tests/test_balance_report.py (diff examples, identical and edited reports, CLI with baseline, weight spy)"
        status: pass
    human_judgment: false
  - id: D4
    description: "CLI, root wrapper, docs: argparse options, --out writes only on request, input errors give exit 2, README/CLAUDE.md describe the command"
    requirement: BAL-04
    verification:
      - kind: unit
        ref: "tests/test_balance_report.py, tests/test_wrappers.py, tests/test_environment.py"
        status: pass
    human_judgment: false
  - id: D5
    description: "Verdict boundaries: error exit code 2 for unreadable input and the static/all split of what the default run computes"
    requirement: BAL-04
    verification: []
    human_judgment: true
    rationale: "Interface choices for the tuning workflow; shown at the D-04 checkpoint together with the first before/after table"

duration: 190min
completed: 2026-10-29
status: complete
---

# Phase 6 Plan 08: BAL-04 consolidated balance report Summary

**`balance_analysis.py` is now the config-aware full-enumeration report of every Phase-6 check (distribution with in-budget top-K and Pareto, gate with path families and X calibration, hand-calc, Final-Index weight, choices, reference strategies and clue mapping, rewarding, spread) with a verdict per block, an exit code, a per-value config diff and a before/after table against a baseline config.**

## Performance

- **Duration:** about 190 min (including one 22 min and one 2 min measurement run on the real config and two full fast suites)
- **Completed:** 2026-10-29
- **Tasks:** 3 (Task 1 and 2 RED then GREEN; Task 3 see Deviations)
- **Files modified:** 9 (1 new)

## Accomplishments

- `planspiel/report.py`: `pareto_front(store, in_budget_only=False)`, summary keys `top_in_budget` and `pareto_in_budget` (placed after `top` and `pareto`; `format` stays 1, the unfiltered sections are unchanged), console sections "Top im Budget nach End-KZ / RoS / Final-Index" and "Pareto-Front im Budget".
- `planspiel/balance.py` rewritten. Removed `Strategy`, `define_strategies`, `POSITIVE_KZ_THRESHOLD`, `run_analysis`. New: `build_balance_report(config_path, content_dir, tiers, layers, paths, jobs, index_weights, log)`, `report_json`, `format_balance_report`, `config_diff`, `format_config_diff`, `compare_reports`, `format_comparison`, `MISSING`, `build_parser`, `main(argv)`.
- Report layout: per tier `distribution`, `gate`, `choices`, `strategies`, `rewarding`, `spread_input`; across tiers `spread`, `choices`, `final_index`, `hand_calc`, `clue_mapping` (plus `calibration` with `--paths`); `verdict` = {passed, failed_checks, checks, failures}. `index_weights_source` is "Konfiguration" or "Kandidat".
- CLI: `--config`, `--content-dir`, `--tier` (repeatable, unknown tier is a parser error), `--layers {static,all}`, `--paths`, `--jobs`, `--out` (writes `balance_report.json` and `balance_report.txt`, nothing without it), `--baseline-config`, `--baseline-content-dir`; progress lines on stderr, "Laufzeit" on stdout. The root wrapper is unchanged (6 lines).
- `--baseline-config` prints "Konfigurationsänderungen (alt → neu)" (JSON path, old, new) and "Kennzahlen vorher → nachher" with the note that Final-Index metrics of both columns use the candidate's k; the baseline's own configured k is an information row. Rows: required X per family and the recommended X, best and median in budget (both layers), IQR, largest band share and its measure, largest removal drop and its measure, placement shares per strategy, non-clue share, KZ share and recommended k.
- README ("Balance-Bericht") and CLAUDE.md (script list, "Balance verifizieren", "Nach inhaltlichen Änderungen") describe the command; no game numbers in the prose.

## Runtime and today's verdict (real simulation_config.json, content/)

Static layer, `uv run python balance_analysis.py --jobs 3 --out build/balance-real-static`: **2 min 12 s** wall (131.5 s reported; static enumeration plus summaries about 107 s, the gate the rest).

All layers, `--layers all --paths --jobs 3`: **21 min 53 s** (static enumeration 86 s, gate and path gate about 740 s, swap layer about 290 s, choices/rewarding/strategies about 60 s per tier, sequential). Measured with nothing else running.

Verdict per check (overall: 11 checks not passed, exit 1):

| Check | low | medium | high | Reason today |
|-------|-----|--------|------|--------------|
| Overspend gate (static and paths) | pass | pass | pass | required X 9 / 5 / 3 (static), config X = 9 |
| Calibration of X | fail | | | config X = 9 not calibrated (recommended 10), above target X <= 5 |
| Choices BAL-06 | fail | fail | fail | M7 near-mandatory in all tiers and overpowered (drops 14 / 16 / 18), M2 and more near-mandatory in medium/high, M2 overpowered in high |
| Cross-tier choices | pass | | | band similarity and best plan differ per tier |
| Reference strategies BAL-07 | fail | fail | fail | no `reference_strategies` block yet |
| Rewarding BAL-08 | pass | pass | pass | median margins +13/+10, +23/+20, +32/+28; comeback 0.91 / 0.96 / 0.96 |
| Spread BAL-09 | fail | | | best 100 in medium/high and on the legal layer in low, high median 32 over start |
| Final-Index | fail | | | KZ share about 0.98 at k = 1 (target 0.60 to 0.73), recommended k 20 |
| Hand-calc (error mode) | fail | | | exfil KZ slope 17/7 |
| Clue mapping | fail | | | `content/clues.toml` carries no mapping |

## Task Commits

1. **Task 1 RED:** `ad01777` test(06-08): add failing tests for in-budget top-K and Pareto in the tier summary
2. **Task 1 GREEN:** `5bc52c2` feat(06-08): in-budget top-K and Pareto front in the tier summary
3. **Task 2 RED:** `c0191cf` test(06-08): add failing tests for the consolidated balance report
4. **Task 2 GREEN:** `43c8ae4` feat(06-08): consolidated balance report with metric blocks and baseline comparison
5. **Task 3 tests:** `5fbc8ef` test(06-08): cover the balance_analysis.py command line, baseline comparison and root wrapper
6. **Task 3 docs:** `758185a` docs(06-08): document the consolidated balance report and its baseline comparison
7. **Fixes:** `aa7c6ac` fix(06-08): shorten balance wrapper smoke test and drop duplicate Final-Index prefix; `0dbcd59` fix(06-08): do not repeat the tier name in the verdict failure lines

## Decisions Made

See `key-decisions`. Open for D-04: whether the static layer should also compute the static half of the choices block (needs a split of `choices_tier`), and exit code 2 for unreadable input.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The no-argument wrapper smoke test in tests/test_environment.py timed out**
- **Found during:** final full fast suite
- **Issue:** `test_documented_wrappers_run[balance_analysis]` ran `balance_analysis.py` without arguments; it now enumerates the real config (over 2 minutes) and hit the 120 s test timeout.
- **Fix:** the test calls `balance_analysis.py --help`; the full run is covered on the mini config in `tests/test_wrappers.py` and `tests/test_balance_report.py`.
- **Files modified:** tests/test_environment.py (not listed in the plan)
- **Commit:** aa7c6ac

### Process note on Task 3

`main(argv)` with its argparse options had to exist for the module to stay runnable after the rewrite of Task 2, so it was implemented in the Task 2 GREEN commit. The Task 3 CLI tests (`5fbc8ef`) therefore passed on arrival instead of failing first; they were written against the plan's behaviour list (out files, baseline sections, candidate weights passed to the baseline build, repeatable `--tier`, wrapper) and the weight-spy and no-write-without-`--out` tests assert behaviour that no earlier code had. No separate RED commit exists for Task 3.

Otherwise the plan was executed as written. Choices, reference strategies, rewarding and the cross-tier choice block are `None` ("nicht berechnet") in the static layer by design.

## Known Stubs

None.

## Threat Flags

None. T-06-20: invalid config, missing or malformed texts/clues raise (ConfigError/ValueError/OSError) and `main` prints FEHLER with exit 2 (tests `test_malformed_config_raises_instead_of_a_partial_verdict`, `test_missing_clue_file_raises`, `test_main_reports_unreadable_input_instead_of_a_partial_verdict`). T-06-21: every block carries its own verdict and failure lines, uncomputed parts are labelled and listed as "nicht berechnet", the exit code follows the verdict. T-06-22: nothing is written without `--out` (`test_main_writes_nothing_without_out`), docs use the gitignored `build/`. `git diff --exit-code -- content simulation_config.json tests/golden final_documents print` is clean.

## Issues Encountered

- Worker processes print the pre-existing `HandCalcWarning` (exfil slope 17/7) on stderr for every tier; the hand-calc block reports it as an error in the verdict. Not suppressed in the children.
- The path gate dominates the all-layers runtime (about 740 s of 1312 s reported by the tool); `--layers all` without `--paths` takes roughly 10 min.

## Next Phase Readiness

06-09 can iterate on a candidate with `uv run python balance_analysis.py --config <candidate> --content-dir <dir> --layers all --paths --jobs 3 --out build/balance`, and print the D-04 comparison with `--baseline-config simulation_config.json`. The quick loop is the default static layer (about 2 min).

## Self-Check: PASSED

- Files exist: tests/test_balance_report.py, planspiel/balance.py, planspiel/report.py, this SUMMARY
- Commits exist: ad01777, 5bc52c2, c0191cf, 43c8ae4, 5fbc8ef, 758185a, aa7c6ac, 0dbcd59
- `uv run pytest -q`: 2678 passed, 1 xfailed (3 min 14 s); `uv run python balance_analysis.py --config tests/fixtures/mini_config.json --content-dir tests/fixtures/mini_content --out build/balance-mini` exits 1 (verdict) and writes `balance_report.json`; `grep -c "def build_balance_report"` 1, `"def config_diff"` 1, `POSITIVE_KZ_THRESHOLD` and `def define_strategies` 0; content/, print/, tests/golden, final_documents and simulation_config.json unchanged
