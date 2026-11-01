---
phase: 06-rebalance
reviewed: 2026-11-01T21:51:03Z
depth: standard
files_reviewed: 29
files_reviewed_list:
  - planspiel/analyze.py
  - planspiel/balance.py
  - planspiel/booklet.py
  - planspiel/choices.py
  - planspiel/cli.py
  - planspiel/config.py
  - planspiel/enumerate.py
  - planspiel/gate.py
  - planspiel/index_weights.py
  - planspiel/master.py
  - planspiel/parallel.py
  - planspiel/refpaths.py
  - planspiel/report.py
  - planspiel/rewarding.py
  - planspiel/rules.py
  - planspiel/simulate.py
  - planspiel/spread.py
  - planspiel/strategies.py
  - planspiel/texts.py
  - planspiel/validate.py
  - print/planspiel.sty
  - print/templates/master.tex.j2
  - print/templates/teamheft_ros.tex.j2
  - tests/conftest.py
  - tests/support/candidate.py
  - tests/support/golden_cases.py
  - tests/support/ties.py
  - tests/test_gate_paths.py
  - tests/test_balance_report.py
findings:
  critical: 0
  warning: 6
  info: 7
  total: 13
status: issues_found
---

# Phase 06: Code Review Report

**Reviewed:** 2026-11-01T21:51:03Z
**Depth:** standard
**Files Reviewed:** 29 (all primary files; changed tests skimmed, two read closely)
**Status:** issues_found

## Summary

I reviewed the Phase-6 balance tooling (gate, path gate and X calibration, BAL-06..09 metric modules, final-index
weight measurement, the consolidated balance report and its CLI), the 06-10 adoption changes (strict hand-calc
validation, RoS₂ in the Final-Index, the master/booklet print changes) and the test support code.

The core arithmetic holds up under tracing:
- `required_penalty_x` gives the smallest X with `pre - X*steps < trimmed` (strict) or `<=` (weak), with no
  off-by-one. D-13 deliberately adds the `+1` in `calibrate`.
- `lowering_closure` is a correct per-dimension prefix maximum.
- The packed pool keys (`kz * 4^n + 4^n-1-code`) fit their typecodes.
- The `PathScan` compression to the maximum pre-review KZ per (start, steps) gives the exact X.
- `ros_two_decimals` uses `round_half_away_frac` on exact Fractions.
- Worker aggregation in `parallel.map_tiers` keys results by tier name, so tiers cannot be mixed up.

The fast suite passes (2659 passed).

The defects are in what the report can claim, not in the per-cell arithmetic:
1. The strict hand-calc default added in 06-10 makes the report's "Handrechnung" check unable to fail. It also breaks
   the documented before/after comparison against any config that is not hand-calculable. I reproduced this with the
   pre-rebalance config.
2. Several cross-tier checks pass vacuously, or are recomputed on the wrong population, when `--tier` narrows the run.
3. The path gate does not cover the path shape teams actually play (mandatory swap plus voluntary move). Two of its
   three families enumerate paths that are illegal when a swap is mandatory.
4. The CLIs conflate crash or invalid-input exits with "check failed" (exit 1).

No Critical issues were found.

## Warnings

### WR-01: The "Handrechnung" check can never fail, and `--baseline-config` rejects any non-hand-calculable baseline

**File:** `planspiel/validate.py:925`, `planspiel/config.py:156-158`, `planspiel/balance.py:179-182,243,644-658`
**Issue:** 06-10 changed the `validate()` default to `hand_calc_level="error"`. `load_config` -> `check_config` calls
`validate(raw)` with that default and raises `ConfigError` on every error. `build_balance_report` calls
`load_config(config_path)` on line 182, before the `hand_calc` block is built on line 243. So any config with a
hand-calc issue aborts the whole report with exit 2, and `cross["hand_calc"]` is only ever computed for configs that
already have no hand-calc errors. The block is vacuous: it always reports "bestanden". The
`warnings.catch_warnings(... HandCalcWarning)` wrappers around the load are dead for hand-calc issues.

The same thing breaks the documented acceptance workflow. Reproduced:
`uv run python balance_analysis.py --config simulation_config.json --baseline-config <pre-rebalance config> --tier low`
prints `FEHLER: Ungültige Konfiguration ... ERROR hand_calc.kz_slope attacks.exfil: KZ-Steigung 17/7 ...` and exits
with code 2. No before/after table is produced. Any future baseline or candidate with one non-terminating slope cannot
be compared or reported. The user gets an abort instead of a report whose failure lines name the issue.
**Fix:** Load leniently inside the report and let the block judge:
```python
# planspiel/config.py
def load_config(path: Path, hand_calc_level: str = "error") -> Config:
    raw = read_raw_config(path)
    check_config(raw, str(path), hand_calc_level)
    ...
def check_config(raw, source, hand_calc_level="error"):
    issues = validate(raw, hand_calc_level=hand_calc_level)
    ...
# planspiel/balance.py (build_balance_report) and the workers it spawns
cfg = load_config(config_path, hand_calc_level="warning")
```
Pass the level through `store_worker` / `swap_layer_worker` / `gate.paths_worker`. Add a test in which a mini config
with a 17/7 slope yields `cross_tier.hand_calc.passed is False` and exit 1 (not 2).

### WR-02: Cross-tier checks pass vacuously or change their population under `--tier`

**File:** `planspiel/balance.py:183,231-250`, `planspiel/spread.py:91-96,108-122,150-156`, `planspiel/choices.py:312-324`, `planspiel/gate.py:599-642`, `planspiel/cli.py:205-208`, `planspiel/index_weights.py:67-88`
**Issue:** `--tier` (repeatable, documented) narrows `names`. Every cross-tier block is then evaluated on that subset,
and its verdict still counts toward exit 0:
- `spread.check_corridor` and the IQR tier difference return no failure when `_window` sees fewer than 2 tiers.
  `--tier low` reports "Streuung (BAL-09): bestanden" without measuring the corridor.
- `choices._tiers` (Jaccard similarity and same best plan) has no pairs with one tier, so it passes.
- `gate.calibrate` takes the maximum over the subset only. With `--tier low --paths`, a tier whose own requirement is
  lower than the binding tier's reports "nicht kalibriert" and fails the report (exit 1) for a correctly calibrated
  config. Conversely, `planspiel gate --paths --tier <non-binding tier>` can print "kalibriert" for an X that is too
  small for the binding tier. D-13 defines X as the maximum over all tiers.
- `final_index_block` pools the IQR over the subset, so the recommended k and the KZ-share verdict depend on which
  tiers were passed.

In the committed config all tiers have the same maximum required X (2), so calibration is not affected today. The
spread and choices vacuity applies to any single-tier run.
**Fix:** Compute cross-tier blocks only when every configured tier is evaluated. Otherwise mark them as not computed:
```python
all_tiers = set(names) == set(cfg.budget_tiers)
cross["spread"] = _checked(spread.check_spread(spreads), spreads) if all_tiers else _skipped(NOT_COMPUTED_TIERS)
# same for cross["choices"], cross["final_index"], cross["calibration"]
```
Also make `check_corridor` / `check_iqr` report a failure (or the caller skip the check) when fewer than 2 tiers are
present. In `_gate_paths_command`, print the calibration only for a full-tier run, or label it "Teilmenge".

### WR-03: The path gate omits the path shape teams actually play, and two of its families model illegal paths

**File:** `planspiel/gate.py:11-17,389-411,556-559`
**Issue:** The `--paths` gate checks three families:
- `tausch`: Kurswechsel swap with minimal repair, no voluntary move.
- `fenster1` / `fenster2`: one move in window 1 or 2, explicitly without the swap.

Two problems follow:
1. **Missing family.** When a Kurswechsel swap is possible it is mandatory (D-22), so every legal game with a voluntary
   change-window move combines the swap and that move. All configured reference plans and reference strategies have
   this shape, and the master answer keys require a voluntary move. This combination, as well as several moves per
   window and moves in both windows (allowed: "beliebig viele"), is never gated. CLAUDE.md states that overspending
   never pays "auch auf den Spielpfaden mit Tausch und Fenster-Zug", but no family contains both.
2. **Illegal families.** `_window_stream` yields `(start, target, target)` / `(start, start, target)` from every valid
   start, including starts where `swap_possible` is true. Under D-22 those paths are illegal, so `fenster1` /
   `fenster2` gate paths no team can play. Their in-budget members also feed the `union` pool that serves as the
   trimmed comparator.

A passing `planspiel gate --paths` therefore does not support the stated claim for the real game shape.
**Fix:** Add a family `tausch_fenster2`: each swap path, then each `single_moves(end)` in window 2, cost = swap cost +
move cost, compared against a pool that holds the swap-layer paths plus these paths. Restrict `fenster1` / `fenster2`
to starts with `not swap_possible(selection)`, or document them explicitly as a diagnostic over non-legal paths and
exclude them from the verdict. Name the remaining uncovered shapes (several moves, both windows) in the gate docstring
and the report.

**Probe (reviewer, not a gate result):** I checked the missing family by sampling in tier low (starts with index divisible by 997): 981,974 over-budget paths of the form swap, then one window-2 move, against the swap-only legal pool, which is a conservative comparator. Required X was at most 1 and there were 0 violations at X = 3. So no exploit was found on that sample. The finding is a gap in coverage and in the claim, not a demonstrated loophole. The full family and the other tiers remain unverified.

### WR-04: CLI exit codes conflate crashes and invalid input with "check failed"

**File:** `planspiel/cli.py:158-211`, `planspiel/balance.py:633-658,686`
**Issue:** `planspiel gate` (with and without `--paths`) does not catch `ConfigError`, `OSError` or exceptions
re-raised from worker processes. An invalid config, which since 06-10 includes any hand-calc issue, ends in a
traceback with exit code 1. That is the same code the command uses for "Überziehungs-Gate: NICHT bestanden".

`balance.main` maps only `OSError` / `ValueError` to exit 2. Any other exception (KeyError on a malformed content
key, IndexError, an AttributeError in a metric) also exits 1. A script or CI step that reads exit 1 as "balance
failed" cannot tell a broken run from a real verdict. `balance.main` documents exit 0 / 1 / 2 semantics, so the
inconsistency matters.
**Fix:** Wrap both entry points:
```python
try:
    ...
except (OSError, ValueError) as error:          # ConfigError is a ValueError
    print(f"FEHLER: {error}", file=sys.stderr)
    return 2
```
In `balance.main`, add a final `except Exception` that prints the traceback and returns 2. Add a test that
`planspiel gate --config <invalid>` returns 2.

### WR-05: `planspiel clues` blames clues.toml for an invalid simulation config

**File:** `planspiel/cli.py:67-75`
**Issue:** This phase added `ValueError` to the `except` around a block that also calls `load_config(Path(config))`.
`ConfigError` subclasses `ValueError`, so any config error, including every hand-calc error now that they are strict,
is printed as `ERROR clues.toml <content>/clues.toml: Ungültige Konfiguration ...` and counted as "1 Fehler". A
facilitator then edits the wrong file.
**Fix:** Separate the loads:
```python
try:
    cfg = load_config(Path(config))
except (OSError, ValueError) as error:
    print(f"ERROR config {config}: {error}"); return 1
try:
    texts = load_texts(...); clues = load_clues(clues_path)
except (OSError, ValueError) as error:
    print(f"ERROR clues.toml {clues_path}: {error}"); ...
```

### WR-06: Suppressing `HandCalcWarning` now hides only the non-hand-calc schema warnings

**File:** `planspiel/config.py:159-162`, `planspiel/balance.py:180-182,634-636`, `tests/support/candidate.py:46-50`
**Issue:** `check_config` emits every warning-level issue as `HandCalcWarning`. Since 06-10 all `hand_calc.*` issues
are errors, so the only warnings left are `schema.removed_key`, `schema.default_used` and
`rules.event_without_window`. The `simplefilter("ignore", HandCalcWarning)` blocks in the balance report and the
balance-test loader now silence exactly these schema and rule warnings, for example a config that still carries a
removed key or relies on a default. That is the opposite of their stated purpose.
**Fix:** Introduce `ConfigWarning(UserWarning)` for non-hand-calc warnings in `check_config`. Keep `HandCalcWarning`
only for `hand_calc.*` codes when loading at level `warning` (see WR-01). Drop the suppressions that no longer apply.

## Info

### IN-01: The "gekappt" X is always identical to the raw X

**File:** `planspiel/gate.py:86-96,157,344,616-624,697-698,729`
**Issue:** `capped_required_x` is only called when `trimmed_final > 0`. For `trimmed > 0`, `clamp(v) < trimmed` holds
exactly when `v < trimmed`: the lower clamp maps negatives to 0 < trimmed, and the upper clamp never applies because
`pre - X*steps < 100`. So `min_x_capped == min_x_strict` always. The test
`test_capped_required_x_equals_the_strict_x_above_zero` confirms this. The capped column, the second calibration cell
per family and the "roh/gekappt" wording add code and report text without information.
**Fix:** Drop the capped variant, or keep it with an explicit `assert capped == strict` and a one-line explanation in
the report.

### IN-02: `calibrated` demands X == max + 1, while `planspiel gate --paths` accepts any sufficient X

**File:** `planspiel/gate.py:634`, `planspiel/balance.py:131-142`, `planspiel/cli.py:210`
**Issue:** The balance report fails the "Kalibrierung von X" block for an X larger than recommended, and also for
X = max, which passes every gate cell. `planspiel gate --paths` exits 0 for both. This matches D-13 (exact +1 margin),
but the two entry points give opposite verdicts for the same config.
**Fix:** State the equality requirement in the `gate --paths` output ("nicht kalibriert" next to "bestanden"), or let
`gate --paths` return 1 when `not calibration.calibrated`.

### IN-03: k is derived from the IQR of unrounded RoS, while the index uses RoS₂

**File:** `planspiel/index_weights.py:46`
**Issue:** `pooled_iqr` ranks `rules.ros(...)` exactly, while `rules.final_index` uses `ros_two_decimals(ros)`. The
quartiles can differ by up to 0.005, so the measured KZ share differs slightly from the one actually in force.
**Fix:** Use `rules.ros_two_decimals(rules.ros(...))` in `pooled_iqr` (None-guarded).

### IN-04: Report numbers are rounded with float `:.2f` / `:.0f` (half-to-even on binary floats)

**File:** `planspiel/index_weights.py:91-92`, `planspiel/strategies.py:224-225,301,307`
**Issue:** `_decimal` and `_percent` and the strategy table format exact Fractions via `float(...)` with Python's
format rounding. Boundary values such as a KZ share of exactly 0.665 can print as "0,66" or "0,67", and the printed
shares near the 3/5 and 73/100 limits may disagree with the exact verdict. These are report-only, but the project
already has `fmt.format_approx` (half away from zero).
**Fix:** Use `fmt.format_approx(value, places)` for these cells.

### IN-05: The penalty-table constants and comment disagree with the template

**File:** `planspiel/booklet.py:28-29,101,290`, `print/templates/teamheft_ros.tex.j2:66,77`
**Issue:** The comment says "rows of the first and second table; the last one holds the rest", and `PENALTY_TABLES`
suggests the split is configurable. The template hard-codes two tables: the second prints
`penalty_rows[penalty_per_table:]`. Setting `PENALTY_TABLES = 3` would silently print all remaining rows in table 2.
**Fix:** Fix the comment ("rows of the first table; the second holds the rest") and either drop `PENALTY_TABLES` or
loop over table slices in the template.

### IN-06: `planspiel gate --jobs` accepts 0 or negative values and is silently ignored without `--paths`

**File:** `planspiel/cli.py:436-438`
**Issue:** `balance.main` rejects `--jobs < 1`, while `planspiel gate` accepts any int, treats `<= 1` as sequential and
ignores the flag without `--paths`.
**Fix:** `if jobs < 1: parser.error("--jobs muss mindestens 1 sein.")`, plus a parser error for `--jobs` without
`--paths`, mirroring `--narrow`.

### IN-07: A measure listed twice in one clue is counted twice

**File:** `planspiel/texts.py:600-606,691-695`
**Issue:** `clue_scores` adds `clue.weight` for each occurrence in `clue.measures`. Neither `_clue_mapping` nor
`check_clues` rejects duplicates, so `measures = ["M1", "M1"]` doubles M1's score. That can satisfy
`clues.top_too_weak` / `clues.not_graduated` and change `clue_good_start`.
**Fix:** Report `clues.duplicate_measure` in `check_clues` when `len(set(clue.measures)) != len(clue.measures)`.

---

_Reviewed: 2026-11-01T21:51:03Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
