---
phase: 06-rebalance
plan: 02
subsystem: validator
tags: [validator, hand-calculability, bal-02]

requires:
  - phase: 06-rebalance
    provides: candidate-config test infrastructure (TUNING_TARGET, balance_config_path, balance marker)
provides:
  - "validate(raw, hand_calc_level='warning'|'error') and HAND_CALC_LEVELS in planspiel/validate.py"
  - "_Validator._hand_calc: single routing point for every hand_calc.* finding"
  - "new code hand_calc.final_index_weights (integer weights, weight_kz = 1)"
  - "slow TUNING_TARGET check test_configured_config_is_hand_friendly (BAL-02 target on any candidate)"
affects: [06-03, 06-10]

tech-stack:
  added: []
  patterns:
    - "severity parameter on the validator instead of a second rule set; default unchanged until the adopted config flips it"

key-files:
  created:
    - tests/test_hand_calc_level.py
  modified:
    - planspiel/validate.py

key-decisions:
  - "Default stays 'warning' (research Q4): promoting now would make load_config(simulation_config.json) raise; 06-10 flips the default together with the adopted config"
  - "Final-index rule lives in a small method check_final_index_weights called from check_hand_calc; it skips silently when a weight is missing or not a number (check_final_index reports that)"
  - "Exfil fix option kz -5 ... 9 at cap 7 (slope 2.0) is balance-neutral and is the only change needed for BAL-02 on today's config"

requirements-completed: [BAL-02]

coverage:
  - id: D1
    description: "All six existing hand_calc codes plus hand_calc.final_index_weights follow hand_calc_level; other warnings stay warnings; invalid level raises ValueError"
    requirement: BAL-02
    verification:
      - kind: unit
        ref: "tests/test_hand_calc_level.py::test_hand_calc_code_follows_the_level, ::test_other_warnings_stay_warnings_in_error_mode, ::test_unknown_level_is_rejected"
        status: pass
    human_judgment: false
  - id: D2
    description: "Final-index weights rule: 1/20 fine, 1/20.5 and 2/20 each exactly one finding at path final_index, today's real and mini configs none"
    requirement: BAL-02
    verification:
      - kind: unit
        ref: "tests/test_hand_calc_level.py::test_bad_final_index_weights_yield_exactly_one_finding, ::test_todays_final_index_weights_are_fine"
        status: pass
    human_judgment: false
  - id: D3
    description: "Exfil 17/7 is the only error-mode issue of today's config; one-decimal variant (kz -5 ... 9) has none and passes planspiel validate --strict"
    requirement: BAL-02
    verification:
      - kind: unit
        ref: "tests/test_hand_calc_level.py::test_real_config_in_error_mode_has_only_the_exfil_slope, ::test_exfil_with_one_decimal_slope_has_no_issue_in_error_mode, ::test_cli_strict_gate_accepts_the_one_decimal_variant_only"
        status: pass
    human_judgment: false
  - id: D4
    description: "Slow BAL-02 target check xfails on today's config and passes on a one-decimal candidate"
    requirement: BAL-02
    verification:
      - kind: unit
        ref: "tests/test_hand_calc_level.py::test_configured_config_is_hand_friendly (XFAIL on simulation_config.json, passed with --runxfail on a candidate with exfil -5/9)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-10-28
status: complete
---

# Phase 6 Plan 02: hand_calc severity level Summary

**`validate(raw, hand_calc_level="error")` raises every hand-calculability finding (kz slope, severity cap, multiplier, weights, recovery, penalty step, new final-index weight rule) to an error while the default stays "warning"; a slow TUNING_TARGET check measures the BAL-02 target on any candidate config.**

## Accomplishments

- `HAND_CALC_LEVELS`, `_Validator(raw, hand_calc_level)`, `validate(raw, hand_calc_level="warning")`; other values raise `ValueError`.
- All six existing hand_calc emissions (five in `check_hand_calc`, `penalty_step` in `event_final_budget_tier`) go through `_Validator._hand_calc`; messages unchanged. No hand_calc code is emitted through `warning` any more.
- New code `hand_calc.final_index_weights` at path `final_index` (D-14/D-15): fires when `weight_ros` is not an integer or `weight_kz != 1`.
- `planspiel/config.py` and `planspiel/cli.py` untouched; `load_config`, the fast suite and `planspiel print` behave as before.

## Error-mode issue list of today's config

`validate(read_raw_config(simulation_config.json), hand_calc_level="error")` yields exactly one error:

`hand_calc.kz_slope  attacks.exfil  "KZ-Steigung 17/7 hat mehr als eine Nachkommastelle (verwendet in Welle 3)"`

Fix option (tested, research Q4, balance-neutral for the validator): `attacks.exfil.kz_at_full_damage = -5`, `kz_at_full_mitigation = 9` at `mitigation_cap = 7` gives slope 2.0 and no hand_calc issue. Whether it is balance-neutral for the game is a question for the tuning plan.

## Interim candidate gate for the tuning plan (until 06-10)

```
uv run planspiel validate --strict --config .planning/phases/06-rebalance/candidate_config.json
uv run pytest -m balance --runxfail --planspiel-config <cand> tests/test_hand_calc_level.py
```

Verified: with `--runxfail` the slow check fails on today's config and passes on a candidate with exfil -5/9.

## Notes for 06-10 (flip the default)

Change the default of `validate(..., hand_calc_level=...)` (and `_Validator`) to `"error"` together with the adopted config, then update:

- the exfil-warning assertions in tests/test_budget_review.py (lines ~276, 284), tests/test_config_prose_removed.py:99, tests/test_kurswechsel.py:205, tests/test_practice_config.py (lines ~356, 360);
- tests/test_validate.py: the one-warning test (`test_real_config_has_no_errors_and_one_slope_warning`), the CLI one-warning / strict tests and the module entry point test that expects "17/7";
- the mini fixture tests/fixtures/mini_config.json, whose exfil slope also has kz -7 ... 10 at cap 7;
- remove `TUNING_TARGET` from `test_configured_config_is_hand_friendly`.

`planspiel/config.py::check_config` then no longer needs the `HandCalcWarning` path for these codes (they become `ConfigError`); decide in 06-10 whether `HandCalcWarning` stays for the non-promoted case.

## Task Commits

1. **Task 1 RED:** `15b6399` test(06-02): add failing tests for hand_calc_level and the final-index weight rule
2. **Task 1 GREEN:** `8c77282` feat(06-02): add hand_calc_level to the validator and the final-index weight rule
3. **Task 2:** `87da7c7` test(06-02): add BAL-02 target checks for the exfil fix option and candidate configs

## Deviations from Plan

None - plan executed as written. Task 2 has no separate RED commit: all of its behaviours are implemented by Task 1, so its fast tests pass on arrival and the only new target (the slow check) is an expected xfail by design.

## Known Stubs

None.

## Threat Flags

None. No new surface; T-06-05 to T-06-07 mitigated as planned (error mode routes every hand_calc code through `_hand_calc`, default unchanged, invalid level raises).

## Verification

- `uv run pytest tests/test_hand_calc_level.py tests/test_validate.py -q`: 65 passed + 20 (new file) passing
- `uv run pytest -q`: 2352 passed, 156 deselected (fast suite, default level unchanged)
- `uv run pytest tests/test_hand_calc_level.py -m slow -q -rx`: 1 xfailed (`test_configured_config_is_hand_friendly`)

## Self-Check: PASSED

- Files exist: planspiel/validate.py, tests/test_hand_calc_level.py
- Commits exist: 15b6399, 8c77282, 87da7c7
- Acceptance greps: `def _hand_calc` 1, `hand_calc.final_index_weights` 1, no `warning(...hand_calc` left
