---
phase: 01-simulation-foundation
reviewed: 2026-10-01T00:52:45Z
depth: standard
files_reviewed: 48
files_reviewed_list:
  - planspiel/__init__.py
  - planspiel/__main__.py
  - planspiel/cli.py
  - planspiel/config.py
  - planspiel/validate.py
  - planspiel/rounding.py
  - planspiel/rules.py
  - planspiel/enumerate.py
  - planspiel/simulate.py
  - planspiel/report.py
  - planspiel/analyze.py
  - planspiel/balance.py
  - simulate_outcomes.py
  - analyze_simulation_results.py
  - balance_analysis.py
  - pyproject.toml
  - .gitignore
  - .gitattributes
  - .python-version
  - simulation_config.json
  - README.md
  - CLAUDE.md
  - .claude/CLAUDE.md
  - tests/conftest.py
  - tests/support/__init__.py
  - tests/support/digest.py
  - tests/support/golden.py
  - tests/support/golden_cases.py
  - tests/support/harness.py
  - tests/support/peak_memory.py
  - tests/fixtures/mini_config.json
  - tests/test_characterization.py
  - tests/test_config_text.py
  - tests/test_digest.py
  - tests/test_encoding_lint.py
  - tests/test_enumeration.py
  - tests/test_enumeration_perf.py
  - tests/test_environment.py
  - tests/test_golden_support.py
  - tests/test_harness_vs_run_simulation.py
  - tests/test_kernel_conformance.py
  - tests/test_legacy_generators_smoke.py
  - tests/test_rounding.py
  - tests/test_rules_exact.py
  - tests/test_rules_semantics.py
  - tests/test_single_definition.py
  - tests/test_validate.py
  - tests/test_wrappers.py
findings:
  critical: 1
  warning: 10
  info: 10
  total: 21
status: issues_found
---

# Phase 1: Code Review Report

**Reviewed:** 2026-10-01T00:52:45Z
**Depth:** standard
**Files Reviewed:** 48
**Status:** issues_found

## Narrative Findings (AI reviewer)

## Summary

I reviewed the new `planspiel` package (rules, config, validation, rounding, enumeration, report, CLI wrappers), the thin root wrappers, the config and doc changes, and the test suite. The fast suite passes (`uv run pytest -q`: 240 passed, 11 deselected).

**What holds up (checked, no finding):**
- **Exact arithmetic.** `e_value_scaled`, `reduction_above_threshold_scaled`, `severity_scaled` and `damage_euros` stay integral. `check_exactness` makes this hold for every config that loads: severity x multiplier x WS must be integral, and the per-step damage `s_unit*1000*(1-r)/WS` must be a whole number of euros. That is enough, because the damage is an integer severity_scaled times that per-step amount.
- **Rounding.** `round_half_away` is correct for both signs and for ties. There is exactly one rounding point per wave (`wave_kz_change`), and the clamp comes after it. Final events are validated as integers, so they need no rounding.
- **TierKernel vs. `evaluate_plan`.** Each memo key covers every input of its cached value:
  - `_e_scaled` uses (wave, c, i, a).
  - `_attack` uses (wave, reduction, recovery); the tier multiplier is fixed per kernel.
  - `_e_target` uses (wave, e_scaled).
  - `_change` uses (wave, e_target_delta, reduction, event_kz).
  - The return-tuple order of `apply_events` and `evaluate_event` is consumed correctly at every call site.
- **ResultStore.** The fixed-width columns fail loudly (`OverflowError`) instead of wrapping.

**Problems found:**
- **Rule disagreement.** The simulation disagrees with the config's own printed rule text at the Budget Review boundaries (CR-01).
- **Crashes instead of clean errors.** Several CLI and validator paths crash with tracebacks: cp1252 or BOM configs, an unknown tier in legacy mode, and a non-string default tier.
- **CLI flags.** Some flags are unvalidated or documented wrongly.
- **Final-Index.** The fallback for zero-cost plans ignores the KZ weight.
- **Robustness and tests.** The enumeration size is unbounded, `balance.py` hard-codes tier names, and one slow test conflicts with the README's own instructions.

## Critical Issues

### CR-01: Budget Review awards +5/+10/+15 at exactly 25.000/50.000/75.000 EUR, contradicting the printed rule text

**File:** `simulation_config.json:301-302`, `planspiel/rules.py:179-188`, `tests/test_kernel_conformance.py:67-72`
**Issue:** The event description, which is printed for players and facilitators, says: `0-25.000 -> KZ 0, 25.001-50.000 -> KZ +5, 50.001-75.000 -> KZ +10, >=75.001 -> KZ +15`. But `tiers` is `[[0, 0], [25, 5], [50, 10], [75, 15]]`, and `_tier_lookup` uses `value >= min_inclusive`. Remaining budget is always an integer number of k€, so a team with exactly 25.000 EUR left gets +5 in the simulation and 0 by hand. The same happens at 50 and 75. This is not hypothetical: a full medium-tier run has **2,772 dependency-valid combinations** whose remaining budget is exactly 25, 50 or 75 (1,148 / 889 / 735). Each of them is off by 5 KZ against the paper rule, and that skews the balance statistics and the in-budget/over-budget comparison. The behaviour existed before this phase. However, this phase newly pins it as correct (`test_apply_final_events_boundary_is_inclusive`, plus the golden `census:remaining_25/50/75` cases), so the contradiction is now built into the tests. The core value says every printed number must match the simulation.
**Fix:** This needs a rule decision; flag it to the user before changing anything. Then make the config and its text agree. Either shift the minima so the code matches the text:
```json
"tiers": [[-100000, -15], [0, 0], [26, 5], [51, 10], [76, 15]]
```
or reword the description to inclusive lower bounds ("0-24.999 -> KZ 0, ab 25.000 -> KZ +5, ..."). After that, update `test_apply_final_events_boundary_is_inclusive`, regenerate the goldens with `--update-golden`, and review the diff.

## Warnings

### WR-01: `planspiel validate` crashes on a cp1252-encoded or BOM-prefixed config; every other entry point shows a raw traceback

**File:** `planspiel/cli.py:17-22`, `planspiel/config.py:103-104`
**Issue:** `_validate_command` only catches `OSError` and `json.JSONDecodeError`. If the config is saved in cp1252 (the machine's code page), `read_text(encoding="utf-8")` raises `UnicodeDecodeError` and the user gets a traceback, not an `ERROR schema.json` line. I reproduced this: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xfc`. A config saved with a UTF-8 BOM by a Windows editor is caught by `validate`. It still crashes `simulate_outcomes.py`, `analyze_simulation_results.py` and `balance_analysis.py`, which call `load_config` directly (reproduced: `JSONDecodeError: Unexpected UTF-8 BOM`). A `ConfigError` also reaches the user only as a traceback from those scripts.
**Fix:**
```python
# config.py
def read_raw_config(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8-sig"), parse_float=Fraction)

# cli.py
except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
```
Also have the wrapper `main()` functions catch `ConfigError`, `UnicodeDecodeError` and `json.JSONDecodeError`, print `str(error)` to stderr and return 1.

### WR-02: The validator raises `TypeError` instead of reporting an issue when `default_budget_tier` is not a string

**File:** `planspiel/validate.py:350`
**Issue:** `default_tier not in tiers` raises `TypeError: unhashable type: 'list'` for `"default_budget_tier": ["medium"]` or for any object value (reproduced). That breaks the validator's contract to collect every error and report it with a code and path. `planspiel validate` then crashes with a traceback.
**Fix:**
```python
if default_tier is not None and (not isinstance(default_tier, str) or default_tier not in tiers):
    self.error("ref.unknown_tier", "default_budget_tier", f"Unbekannter Budget-Tier {default_tier!r}")
```

### WR-03: Legacy mode (`--output`) crashes with `KeyError` on an unknown `--budget-tier`; summary mode handles it cleanly

**File:** `planspiel/simulate.py:41`
**Issue:** In summary mode, `main()` checks the tier and calls `parser.error(...)`, which exits with code 2 and lists the valid tiers. `run_simulation` instead indexes `cfg.budget_tiers[...]` directly. `simulate_outcomes.py --budget-tier huge --output x.json` therefore ends in a `KeyError: 'huge'` traceback (reproduced). The test (`test_cli_unknown_tier_lists_tier_names`) only covers summary mode.
**Fix:** In `main()`, load the config and check the tier before branching on `args.output`. Run the same `parser.error` for both modes, or raise a clear `ValueError` inside `run_simulation`.

### WR-04: The `--budget-max` help text contradicts its behaviour, the README example using it does nothing, and legacy filter values are not range-checked

**File:** `planspiel/simulate.py:100-107`, `README.md` (legacy budget-filter example)
**Issue:**
- The README now says `--budget-max` is not a hard cap; it only scales `--budget-utilization`. The argparse help still says `"Maximum total cost filter (points)."`.
- The README example `--budget-min 300 --budget-max 380 --output ...` has no `--budget-utilization`, so `--budget-max 380` has no effect at all. Readers will believe they set a 300-380 window.
- `--budget-utilization` accepts negative values and values above 1.
- `--budget-min` greater than the budget is accepted silently, and the run returns zero results.
**Fix:** Change the help to something like `"Basis für --budget-utilization (keine harte Obergrenze)."`. In `parse_args`, reject `--budget-max` without `--budget-utilization` and reject utilization outside `(0, 1]`. Remove or correct the README example.

### WR-05: `analyze_simulation_results.py --top` is not validated; negative values silently print the wrong slice

**File:** `planspiel/analyze.py:37-42, 125, 137, 148`
**Issue:** `sorted(...)[:top_n]` with `--top -2` returns every entry except the last two. `--top 0` prints empty sections. `simulate.py` rejects `--top < 1`, but `analyze.py` has no matching check. On a full legacy file, a negative `--top` prints hundreds of thousands of entries.
**Fix:**
```python
args = parser.parse_args(argv)
if args.top < 1:
    parser.error("--top muss mindestens 1 sein.")
```

### WR-06: `final_index` ignores `weight_kz` when RoS is undefined, so zero-cost plans are ranked on a different scale

**File:** `planspiel/rules.py:391-396`
**Issue:** When `ros is None` (total cost 0), the function returns `kz_final` instead of `weight_kz * kz_final`. With `analyze --weight-kz 2`, the do-nothing plan scores `kz`, while every other plan scores `2*kz + weight_ros*RoS*100`. Verified: `final_index(40, None, 2, 1) == 40` but `final_index(40, 0, 2, 1) == 80`. The behaviour is inherited from the old `compute_final_index`. It is now the single canonical definition and is pinned by `test_final_index_falls_back_to_kz_without_ros` (that test uses weight 1.0, so it never sees the bug).
**Fix:**
```python
if ros is None:
    return weight_kz * kz_final
```
Add a test case with `weight_kz != 1`.

### WR-07: `_tier_lookup` returns the first tier's value for inputs below the first minimum, and the validator does not prevent such configs

**File:** `planspiel/rules.py:179-188`, `planspiel/validate.py:475-494`
**Issue:** The docstring says it "returns the value of the highest tier whose min_inclusive <= value". When no tier qualifies, it still returns `tiers[0][1]`. Example: a `checklist_tier` with tiers starting at `[1, -5]` gives a count of 0 the `-5` reward. A remaining budget below `-100000` gets the `-15` tier only by accident. `check_tiers` checks ordering and the maximum minimum, but never checks that the first minimum covers the whole input domain (0 for checklist counts). A config edit can therefore change outcomes silently.
**Fix:** In `check_tiers`, require `minima[0] == 0` for `checklist_tier`, and require `minima[0] <= 0` (or a documented sentinel) for `final_budget_tier`. Or make `_tier_lookup` raise `ValueError` when `value < tiers[0][0]`.

### WR-08: `balance.py` hard-codes the tier names `low`/`medium`/`high`

**File:** `planspiel/balance.py:360, 373, 390-391`
**Issue:** The tier comparison, the KZ distribution and the budget-coverage sections loop over the literal list `["low", "medium", "high"]`. `cfg.budget_tiers[tier_name]` at line 391 raises `KeyError` if a tier is renamed. An additional tier is silently left out of every summary even though the per-tier loop above it evaluated it. This breaks the single-source-of-truth rule and the requirement that v1 code must not hard-code the scenario.
**Fix:** Replace the three literal lists with `cfg.budget_tiers` (for example `for tier_name in cfg.budget_tiers:`).

### WR-09: The full-enumeration size has no upper bound and `--top` has no upper bound

**File:** `planspiel/enumerate.py:87-99`, `planspiel/validate.py:198-213`, `planspiel/simulate.py:151-152`
**Issue:**
- **Combination count.** The enumeration always walks `4 ** len(measures)` combinations. Neither the validator nor `simulate.main` caps the number of measures. Today that is 10 measures and about 40 s per tier. With 12 measures, the default `simulate_outcomes.py` run becomes 16.7M combinations (hours per tier), with no warning. At 16 measures, `code_index` overflows the `"I"` column partway through the run, after a long wait.
- **Top-K.** `--top` has no upper limit. `--top 1000000` makes `summarize_tier` materialize three full sorted lists of all 782k entries in the JSON, which defeats the memory bound the phase measured.
**Fix:** Before enumerating, check `4 ** len(cfg.measures)` against a documented limit (for example the `array("I")` range and a soft limit with an explicit `--allow-large` override). Fail fast with a German error message. Cap `--top` (for example at 1000), or reject values above the number of valid combinations.

### WR-10: A slow perf test fails whenever the README's own dump command has been run in the repo root

**File:** `tests/test_enumeration_perf.py:79`
**Issue:** `test_summary_run_stays_within_the_measured_bounds` asserts `not list(REPO_ROOT.glob("simulation_full*.jsonl"))`. The README tells users to run `uv run python simulate_outcomes.py --budget-tier medium --dump-jsonl simulation_full_medium.jsonl`, which writes exactly that file into the working directory, normally the repo root. The file is gitignored, so it stays on disk, and from then on the slow suite fails for a reason unrelated to the code under test.
**Fix:** Assert only on `tmp_path` (the child run already writes the summary there). Or snapshot the glob before the run and compare after, so the test checks that the run created no new dump file.

## Info

### IN-01: `base_losses` ignores `severity_multiplier`, so RoS is wrong for any tier with a multiplier other than 1

**File:** `planspiel/rules.py:376-381`
**Issue:** Avoided losses are computed against `base_severity * s_unit`, but the damage is scaled by the tier's `severity_multiplier`. All tiers use 1.0 today, and `hand_calc.severity_multiplier` warns otherwise. The defect is latent and was inherited from the legacy code.
**Fix:** Pass the tier into `base_losses` and multiply by `severity_multiplier`, or document that RoS is defined against unscaled losses.

### IN-02: User-facing number formatting rounds half-to-even, not half-away

**File:** `planspiel/balance.py:302, 337-342, 363`, `planspiel/report.py:210`, `planspiel/analyze.py:17-25`
**Issue:** In Python 3.12, `Fraction.__format__` rounds half to even (`f"{Fraction(5,2):.0f}" == "2"`). The printed damage (`:.0f`), RoS and Final-Index values can therefore differ by one unit in the last digit from the project's documented paper rule (+2.5 -> 3). The stored values are exact and correct; only the display is affected.
**Fix:** Add a small display helper in `rounding.py` that formats through `round_half_away` at the requested number of decimals.

### IN-03: Planning-phase references leak into user-facing text

**File:** `planspiel/cli.py:48`, `planspiel/report.py:15`
**Issue:** The `--strict` help reads "(wird in Phase 6 verwendet)". `FINAL_INDEX_STATUS` ("bis zur Neuskalierung in Phase 6") is written into every summary JSON and console run. Facilitators do not know the GSD phase numbers.
**Fix:** Use wording that does not refer to phase numbers, for example "vorläufig (Gewichte werden noch neu skaliert)".

### IN-04: Hidden loader defaults duplicate config values in code

**File:** `planspiel/config.py:132, 167`
**Issue:** `kz_start` defaults to 60 and `e_threshold` to 18. Both are game numbers that live outside `simulation_config.json`. A warning is emitted, but the values still apply.
**Fix:** Make both fields required (validator error) now that the real config defines them everywhere.

### IN-05: Stale `float` type hints on exact values

**File:** `planspiel/config.py:14-15`, `planspiel/rules.py:179, 194, 384, 399`
**Issue:** `kz_at_full_damage: float`, `_tier_lookup(value: float, ...) -> float` and `ros(base_losses: float, total_damage: float, total_cost: float)` all hold or require exact int/Fraction values. Because of these hints, `ros()` silently accepts floats (as `test_ros_formula` does), which reintroduces inexact results.
**Fix:** Annotate with `int`/`Fraction`.

### IN-06: Alias wave keys (`wave_01` and `wave_1`) pass validation and silently overwrite each other on load

**File:** `planspiel/validate.py:34, 382-384`, `planspiel/config.py:194-197`
**Issue:** `WAVE_KEY` accepts `wave_01`, and the loader maps it to wave 1. If both keys are present, one wave's events are silently dropped.
**Fix:** Require the canonical form `wave_{id}` (regex `wave_([1-9]\d*)`) and reject duplicates after `int()` conversion.

### IN-07: Two weak tests

**File:** `tests/test_kernel_conformance.py:162-171`, `tests/test_encoding_lint.py:30-34`
**Issue:**
- `test_kernel_memoization_never_changes_a_result` only compares the kernel with itself. A memo key that is missing a dimension would return the same wrong value both times. The cross-checks against `evaluate_plan` are what actually protect the kernel.
- The encoding lint does not flag `Path.open(...)` without `encoding=`.
**Fix:** Have the memoization test evaluate selections in two different orders against `evaluate_plan`. Add `"open"` to the attribute check when the receiver is not a builtin.

### IN-08: `analyze` now parses legacy result files with `parse_float=Fraction`

**File:** `planspiel/analyze.py:12-13`
**Issue:** Legacy inputs are 130-360 MB (`sim_*.json`). Every float becomes a `Fraction` object, which multiplies the memory used and the load time compared with the previous float parse. That is a practical out-of-memory risk on the documented file sizes.
**Fix:** Parse floats normally and convert only the fields actually used (`total_damage`) to `Fraction`, or stream the input.

### IN-09: Stale documentation pointers

**File:** `CLAUDE.md:45`, `.claude/CLAUDE.md` (Frameworks section)
**Issue:**
- CLAUDE.md still says the Final-Index is defined "siehe `analyze_simulation_results.py`", which is now a thin wrapper; the definition is `planspiel/rules.py:final_index`.
- `.claude/CLAUDE.md` was edited in this phase, but right next to the edit it still states "No `pytest`/`unittest` test files, no test config".
**Fix:** Point both to `planspiel/rules.py` and `pyproject.toml`/`tests/`.

### IN-10: `started_steps` is unused in Phase 1

**File:** `planspiel/rounding.py:20-28`
**Issue:** The function is only used by tests ("Phase 2 nutzt das"). That conflicts with the project's YAGNI rule.
**Fix:** Move it into Phase 2 together with its first caller, or accept it explicitly as Phase 2 groundwork.

---

_Reviewed: 2026-10-01T00:52:45Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
