---
phase: 06-rebalance
plan: 03
subsystem: final-index
tags: [final-index, balance-workflow, bal-03]

requires:
  - phase: 06-rebalance
    provides: candidate-config test infrastructure (TUNING_TARGET, balance_config_path, static_stores)
provides:
  - "rules.ros_two_decimals and rules.final_index in the D-15 form: weight_kz * KZ + weight_ros * RoS2"
  - "planspiel/index_weights.py: pooled_iqr, kz_share, recommended_k, final_index_block, format_final_index_block"
  - "slow TUNING_TARGET check test_configured_k_gives_kz_two_thirds (KZ share in [0.60, 0.73])"
  - "simulate_outcomes.py without --budget-max and --budget-utilization; run_simulation(config_path, budget_tier_name, output_path, budget_min)"
affects: [06-08, 06-09, 06-10]

tech-stack:
  added: []
  patterns:
    - "scoped golden: the one row the formula moves is substituted from the golden itself and tracked by an xfail(strict=True) test"

key-files:
  created:
    - planspiel/index_weights.py
    - tests/test_index_weights.py
  modified:
    - planspiel/rules.py
    - planspiel/simulate.py
    - planspiel/analyze.py
    - tests/test_master_model.py
    - tests/test_final_index_config.py
    - tests/test_rules_semantics.py
    - tests/test_single_definition.py
    - tests/test_enumeration.py
    - tests/test_harness_vs_run_simulation.py
    - tests/test_validate.py
    - tests/test_wrappers.py
    - README.md
    - CLAUDE.md
    - .planning/PROJECT.md

key-decisions:
  - "Golden approach (b): answer_keys.json untouched; test_every_printed_answer_key_is_pinned takes final.final_index from the golden file, every other field stays strict; test_final_index_row_matches_golden is xfail(strict=True) and is deleted by 06-10 in the re-pin task"
  - "Interim meaning of the committed {1, 1} weights pinned by a strict test (k = 1 under the new formula); it never feeds a tuning decision"
  - "recommended_k = multiple of 5 nearest to k_raw = IQR_KZ / (2 * IQR_RoS), ties away from zero; no lower clamp"

requirements-completed: [BAL-03]

coverage:
  - id: D1
    description: "Final-Index = weight_kz * KZ + weight_ros * RoS2, RoS2 exact half-away rounding to two decimals, defined once in rules.py"
    requirement: BAL-03
    verification:
      - kind: unit
        ref: "tests/test_rules_semantics.py::test_ros_two_decimals_rounds_half_away_from_zero, ::test_final_index_is_kz_plus_k_times_the_two_decimal_ros; tests/test_single_definition.py::test_formula_defined_once_in_rules[ros_two_decimals]"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every caller follows the weights of its config (summary, dump_record, analyze, balance); weight_ros 0 gives the KZ"
    requirement: BAL-03
    verification:
      - kind: unit
        ref: "tests/test_final_index_config.py (weight tests, analyze float-damage regression)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Scoped golden check: all answer-key fields strict except final.final_index; moved row tracked by strict xfail; interim k = 1 meaning pinned"
    requirement: BAL-03
    verification:
      - kind: unit
        ref: "tests/test_master_model.py::test_every_printed_answer_key_is_pinned, ::test_final_index_row_matches_golden (XFAIL), ::test_interim_real_config_index_is_kz_plus_two_decimal_ros"
        status: pass
    human_judgment: false
  - id: D4
    description: "k is measurable from data; slow check on the configured k xfails on today's config"
    requirement: BAL-03
    verification:
      - kind: unit
        ref: "tests/test_index_weights.py (13 fast tests); ::test_configured_k_gives_kz_two_thirds (XFAIL, -m slow)"
        status: pass
    human_judgment: false
  - id: D5
    description: "0.85 utilization filter gone from code and docs"
    requirement: BAL-03
    verification:
      - kind: unit
        ref: "tests/test_enumeration.py::test_cli_rejects_inconsistent_flags, ::test_legacy_signature_has_no_upper_budget_or_utilization_parameter; grep budget-utilization = 0 in simulate.py, README, CLAUDE.md, PROJECT.md"
        status: pass
    human_judgment: false

duration: 75min
completed: 2026-10-28
status: complete
---

# Phase 6 Plan 03: Final-Index KZ + k x RoS Summary

**Final-Index is now `weight_kz * KZ + weight_ros * RoS2` with an exact two-decimal RoS, k can be measured and recommended from the pooled in-budget IQR, and the 0.85 utilization filter is gone from code and docs; config, content, goldens and final_documents are untouched.**

## Measured on today's config (static reference enumeration, in budget, own cost > 0)

| Scope | IQR KZ | IQR RoS | KZ share at k = 1 |
|-------|--------|---------|-------------------|
| pooled | 18 | 0.43 (28318/65569) | 0.98 |
| low | 17 | 0.70 | 0.96 |
| medium | 17 | 0.49 | 0.97 |
| high | 17 | 0.33 | 0.98 |

- k_raw = 590121/28318 = 20.84, **recommended k = 20** (multiple of 5; research Q6 had 20.5 -> 20, same result).
- KZ share at the recommended k: pooled 0.676 (inside [0.60, 0.73]); k = 15 gives 0.735 (just above the band), k = 25 gives 0.625.
- Configured k = 1: share 0.98, so `test_configured_k_gives_kz_two_thirds` xfails (target for 06-09 / 06-10).

## Accomplishments

- `rules.ros_two_decimals` (exact `round_half_away_frac`, no builtin round) and the new `rules.final_index`, registered in the single-definition guard.
- `planspiel/index_weights.py` (new, pure functions) with the constants `TARGET_KZ_SHARE`, `KZ_SHARE_MIN`, `KZ_SHARE_MAX`, `K_STEP`.
- `simulate_outcomes.py --output` only knows `--budget-min`; legacy summary key `budget_filter` is `{"min": ...}`; analyze.py never read the removed keys.
- Digest pins of the old scale in tests/test_final_index_config.py replaced by semantic weight tests.
- README formula paragraph, CLAUDE.md formula bullet and filter mentions, PROJECT.md feature list updated.

## Notes for later plans

- **06-10 owns:** the data-based k in the adopted config, removal of the "vorläufig" label (report, refpaths, master, balance console), the master-sheet weight row, the single re-pin of `tests/golden/answer_keys.json` and deletion of `test_final_index_row_matches_golden` plus the substitution in `test_every_printed_answer_key_is_pinned`; replace `test_interim_real_config_index_is_kz_plus_two_decimal_ros`.
- The committed print set in `final_documents/` is stale for the facilitator master final-index row until 06-10 rebuilds it (D-04); `planspiel print --check` would flag it. The fast and pdf/slow tests built from the model all pass.
- 06-08 should compute the baseline's Final-Index metrics with the candidate's k, not with the interim k = 1.

## Task Commits

1. **Task 1 RED:** `c5eb08e` test(06-03): add failing tests for k measurement and filter removal
2. **Task 1 GREEN:** `a1a93f3` feat(06-03): measure the final-index weight k and drop the utilization filter
3. **Task 2 RED:** `4842c83` test(06-03): add failing tests for the final index as KZ + k x two-decimal RoS
4. **Task 2 GREEN:** `34395d5` feat(06-03): final index as KZ + k x RoS with two-decimal RoS
5. **Deviation fix:** `46972fc` fix(06-03): analyze reads legacy damage as an exact fraction

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] analyze crashed on float total_damage from the legacy JSON**
- **Found during:** Task 2 (after the formula change, manual probe of analyze with a fractional damage)
- **Issue:** `analyze.item_ros` passed a JSON float into `rules.ros`, so the RoS became a float and the new `ros_two_decimals` (needs an exact value) raised AttributeError. The old formula tolerated floats.
- **Fix:** `Fraction(str(item["total_damage"]))` in `analyze.item_ros`; regression test `test_analyze_handles_fractional_damage_from_the_legacy_file`.
- **Files modified:** planspiel/analyze.py, tests/test_final_index_config.py
- **Verification:** full fast suite green; the fix commit carries its test (no separate RED commit).

**2. [Plan adaptation] test expectations**
- `test_recommended_k_rounds_to_multiples_of_five` first used a wrong expected value in my own RED test; corrected before GREEN. No production code involved.

## Known Stubs

None.

## Threat Flags

None. T-06-08 to T-06-11 mitigated as planned: `tests/golden` untouched, only the `final.final_index` row is substituted from the golden itself and tracked by a strict xfail, `ros_two_decimals` uses `rounding.round_half_away_frac`.

## Verification

- `uv run pytest -q`: 2371 passed, 157 deselected, 1 xfailed (strict row test)
- `uv run pytest tests/test_index_weights.py -m slow -q -rx`: 1 xfailed (k-share check)
- `uv run pytest tests/test_master_pdf.py tests/test_enumeration_perf.py tests/test_print_check.py -m "slow or pdf"`: 17 passed
- `git diff --exit-code -- simulation_config.json content tests/golden final_documents`: clean
- `simulate_outcomes.py ... --budget-utilization 0.85 --output build/x.json`: exit code 2

## Self-Check: PASSED
