---
phase: 05-player-facilitator-print-material
plan: 13
subsystem: config
tags: [final-index, config, validator, d-23, print-10]

requires:
  - phase: 05-player-facilitator-print-material
    provides: Config.practice as the trailing Config field (05-11)
provides:
  - top-level final_index block (weight_kz, weight_ros) in simulation_config.json and the mini fixture
  - config.FinalIndexWeights, Config.final_index (required, before practice) and config.DEFAULT_CONFIG_PATH
  - validate._Validator.check_final_index (schema.top_level, schema.keys, schema.type, schema.range)
  - rules.final_index(kz_final, ros, weight_kz, weight_ros) without default weights
  - report.dump_record(..., weights); summarize_tier, balance and analyze read the config weights
affects: [05-14, 05-15, 05-16]

tech-stack:
  added: []
  patterns:
    - "One source for a facilitator-side constant: required config block, validator, no function defaults, every caller threaded through cfg"

key-files:
  created:
    - tests/test_final_index_config.py
  modified:
    - simulation_config.json
    - tests/fixtures/mini_config.json
    - planspiel/config.py
    - planspiel/validate.py
    - planspiel/rules.py
    - planspiel/report.py
    - planspiel/simulate.py
    - planspiel/balance.py
    - planspiel/analyze.py
    - tests/test_rules_semantics.py
    - tests/test_enumeration.py
    - tests/test_ros_ledger.py

key-decisions:
  - "DEFAULT_CONFIG_PATH moved from balance.py to config.py (balance re-imports it) so analyze can resolve the repository config without importing balance"
  - "analyze without --config now loads the repository config only for its weights; base_losses (and with it the RoS lines) still require an explicit --config, so its output is unchanged"
  - "A one-sided zero weight is allowed; only both weights 0 is a validator error, because a final index of 0 for every plan ranks nothing"

patterns-established:
  - "Unchanged-output proof for a refactor: sha256 pins of the mini summary (three tiers), the analyze output (with and without RoS) and the balance output, taken before the change"

requirements-completed: []

duration: ~60 min
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 13: Final-index weights in config Summary

**The final-index weights (1 and 1) now live in `simulation_config.json` as a required, validated `final_index` block; `rules.final_index` has no defaults left and the report summary, dump records, balance and analyze all read the config, with every output byte-identical.**

PRINT-10 spans 05-13 to 05-16, so the requirement is intentionally not marked complete here. The printed final index of the answer keys (05-14, 05-15) can now read the same config source as the reports; it stays marked `vorläufig` until the Phase 6 rescale (BAL-03).

## Accomplishments

- Config block `"final_index": {"weight_kz": 1, "weight_ros": 1}` in the real and the mini config; `FinalIndexWeights(weight_kz, weight_ros)` as `Fraction`s; `Config.final_index` is required and sits before the trailing `practice`.
- Validator: missing block (`schema.top_level`), non-object (`schema.type`), missing weight key (`schema.keys`), non-number (`schema.type`), negative weight and both weights 0 (`schema.range`).
- `rules.final_index` has no default weights (calling it with two arguments raises `TypeError`).
- Callers: `report.summarize_tier` (cfg), `report.dump_record(..., weights)` with `simulate.py` and the tests, `balance.run_analysis`, `analyze.main`. `analyze --weight-kz/--weight-ros` default to None, resolve from `--config` or the repository config, and explicit flags still win. `report.FINAL_INDEX_STATUS` stays for the console.

## RED run

`uv run pytest tests/test_final_index_config.py -q` gave `ImportError: cannot import name 'FinalIndexWeights' from 'planspiel.config'` (collection error, 1 error). Commit `1dbce84`.

## Verification

- `uv run pytest tests/test_final_index_config.py tests/test_rules_semantics.py tests/test_enumeration.py tests/test_ros_ledger.py tests/test_validate.py tests/test_config_text.py tests/test_characterization.py -q`: 150 passed.
- `uv run planspiel validate`: 0 errors, 1 warning (the known 17/7 KZ-slope warning).
- `uv run pytest -q`: 2144 passed, 140 deselected (baseline 2122, +22 new tests), 92 s.
- `uv run pytest -m slow tests/test_digest.py tests/test_overspend_gate.py -q`: 9 passed in 592.89 s (0:09:52). The pinned enumeration digests and full gate goldens are unchanged.
- `uv run planspiel gate`: bestanden for low (X strict 9, weak 8, witness 1121103000, 712882 over budget) and medium (5/4, 1101103113, 658015), identical to the 05-11 values.
- `uv run pytest -m pdf -q`: 118 passed (139 s); the config file changed, so this was run as a safety check.
- Unchanged-output pins (taken before the change, asserted after): mini summary sha256 for low/medium/high, analyze output with and without RoS, balance output.
- `git status --porcelain final_documents/generated`: empty.

## Task Commits

1. Task 1 RED: `1dbce84` test(05-13): add failing final-index config tests
2. Task 1 GREEN: `3c455fd` feat(05-13): read the final-index weights from config

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `balance_reads_the_config_weights` test cannot use the mini config**
- **Found during:** Task 1 GREEN run
- **Issue:** `balance.run_analysis` evaluates hard-coded ten-measure strategies, which the mini config (four measures) does not have (`KeyError: 'M3'`).
- **Fix:** the test uses the real config and a tmp copy with `weight_kz: 2`.
- **Files modified:** tests/test_final_index_config.py
- **Commit:** 3c455fd

### Other notes

- `DEFAULT_CONFIG_PATH` was moved into `planspiel/config.py` (balance re-imports it); not listed in the plan, needed so analyze can resolve the repository config cleanly.
- `tests/test_validate.py` and `tests/test_config_text.py` needed no edits (they derive from the real and mini configs, which carry the block); the validator cases live in the new `tests/test_final_index_config.py`.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. T-05-45 (two sources for the weights) is mitigated: defaults removed from `rules.final_index`, block required and validated, caller wiring tested with a weighted config copy, outputs proven identical at 1 and 1.

## Next Phase Readiness

05-14 and 05-15 read `cfg.final_index` when they print the final index on the master sheet, marked `vorläufig`; 05-16 records the Phase 6 (BAL-03) rescale follow-up.

## Self-Check: PASSED

- Created file exists: `tests/test_final_index_config.py`.
- Commits `1dbce84` and `3c455fd` are in `git log`.
