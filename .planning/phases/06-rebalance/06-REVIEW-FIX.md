---
phase: 06-rebalance
fixed_at: 2026-11-01T22:57:54Z
review_path: .planning/phases/06-rebalance/06-REVIEW.md
iteration: 1
findings_in_scope: 6
fixed: 6
skipped: 0
status: all_fixed
---

# Phase 06: Code Review Fix Report

**Fixed at:** 2026-11-01T22:57:54Z
**Source review:** .planning/phases/06-rebalance/06-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 6 (WR-01 to WR-06; IN-01 to IN-07 out of scope by user decision)
- Fixed: 6
- Skipped: 0

Fast suite after the last fix: `uv run pytest -q` 2681 passed, 185 deselected.

## Fixed Issues

### WR-01: The "Handrechnung" check can never fail, and `--baseline-config` rejects any non-hand-calculable baseline

**Files modified:** `planspiel/config.py`, `planspiel/enumerate.py`, `planspiel/gate.py`, `planspiel/balance.py`, `tests/test_balance_report.py`
**Commit:** 1d7a378
**Applied fix:** `load_config` and `check_config` take `hand_calc_level` (default `"error"`). The balance report, its
baseline and the store, swap-layer and path workers load at level `"warning"`. A config whose only defects are
hand-calc findings now gives a report with a failed "Handrechnung" block and exit 1, not an abort with exit 2. A 17/7
baseline can be compared again. Tests: mini config with a 17/7 slope (block fails, `main` returns 1, baseline
comparison works).

### WR-05: `planspiel clues` blames clues.toml for an invalid simulation config

**Files modified:** `planspiel/cli.py`, `tests/test_clues.py`
**Commit:** 4e4f4f8
**Applied fix:** config, texte.toml and clues.toml are loaded one at a time. Errors name the file that carries them
(`ERROR config <path>`, `ERROR texte.toml <path>`, `ERROR clues.toml <path>`).

### WR-06: Suppressing `HandCalcWarning` now hides only the non-hand-calc schema warnings

**Files modified:** `planspiel/validate.py`, `planspiel/config.py`, `planspiel/balance.py`, `tests/support/candidate.py`, `tests/test_validate.py`, `tests/test_balance_report.py`
**Commit:** f172185
**Applied fix:** new `ConfigWarning(UserWarning)` for every warning-level finding that is not `hand_calc.*`.
`HandCalcWarning` is now emitted only for hand-calc findings loaded at level `"warning"`. The balance report keeps
suppressing `HandCalcWarning`, because its block judges those findings, and now does so inside its tier workers too.
Schema and rule warnings stay visible. The dead suppression in the balance-test loader was removed.

### WR-04: CLI exit codes conflate crashes and invalid input with "check failed"

**Files modified:** `planspiel/cli.py`, `planspiel/balance.py`, `tests/test_overspend_gate.py`, `tests/test_balance_report.py`
**Commit:** 2c9efe6
**Applied fix:** `planspiel gate` (static and `--paths`) maps `OSError` and `ValueError` to `FEHLER` on stderr and exit
2. This includes `ConfigError` and errors re-raised from workers. `balance.main` also maps any other exception to exit
2 and prints the traceback. Exit 1 now means only that a check failed.

### WR-02: Cross-tier checks pass vacuously or change their population under `--tier`

**Files modified:** `planspiel/balance.py`, `planspiel/spread.py`, `planspiel/cli.py`, `README.md`, `tests/test_balance_report.py`, `tests/test_spread.py`, `tests/test_gate_paths.py`, `tests/test_final_index_config.py`
**Commit:** 5e62b99
**Applied fix:** when `--tier` selects a subset, the report marks three blocks as "nicht berechnet (nur über alle
Tiers)" and leaves them out of the verdict: choices between tiers, Final-Index weight and calibration of X. The spread
block keeps its per-tier criteria and skips the corridor and the IQR tier difference (`check_spread` / `check_iqr`
take `cross_tier`). It names the skip in a note. `planspiel gate --paths` prints no calibration for a subset. One
existing test (`test_balance_report_reads_the_config_weights`) read the Final-Index block from a single-tier run; it
now runs over all mini tiers.

### WR-03: The path gate omits the path shape teams actually play, and two of its families model illegal paths

**Files modified:** `planspiel/gate.py`, `planspiel/cli.py`, `tests/test_gate_paths.py`, `tests/test_balance_report.py`, `README.md`, `CLAUDE.md`
**Commit:** f3b4e79
**Status:** fixed: requires human verification (logic change in the gate; golden re-pin pending, see below)
**Applied fix:**
- New family `tausch_fenster2`: the mandatory Kurswechsel swap, then one voluntary move in window 2. The reference
  paths and answer keys have this shape (`refpaths.candidate_paths`: swap window, then a single voluntary move in
  window 2). The family needs one pass over the swap layer. For each window state it evaluates only the Pareto front of
  the window-2 moves (wave-3 KZ change against budget need). A dominated move cannot raise the required X. If its
  dominator is over budget, the dominator has at most as many steps and at least the same pre-review KZ. If the
  dominator is in budget, the trimmed version ends at least at the dominator's final KZ. That relies on rising,
  non-negative Budget Review tiers, which the gate now checks, so the dominated move needs X = 1. Required X (raw, weak
  and capped), the verdict, path counts and the unlosable and untrimmable counts are exact. The histogram counts
  front groups. The gate docstring states this.
- D-22 point holds: whenever a swap is possible, `rules.evaluate_path` raises `kurswechsel_missing` for a path without
  it. `fenster1` and `fenster2` now start only from plans without a possible swap (no active measure or no inactive
  one). On the real config this is 1,373,463 paths per family and tier, down from 22,274,048. The union comparator
  drops its static pass, which also contained illegal static paths of swappable starts. It now holds exactly the legal
  paths of all four families. The tausch family and its legal pool are unchanged.
- Guards: the gate raises if the Kurswechsel is not in wave 1 or the Budget Review tiers are not rising and
  non-negative.
- The family is wired into `planspiel gate --paths`, the calibration and the balance report (all iterate
  `PATH_FAMILIES`). The calibration output names the shapes that are still not gated: several moves in one window,
  moves in both windows, and an extra move in the swap window.
- Tests (red first): the mini brute force evaluates every path of every family as `rules.Path` with
  `enforce_kurswechsel=True` and compares all exact fields. Further tests cover the swap-mandatory predicate and both
  guards.

**Real config, `uv run planspiel gate --paths --jobs 3`** (exit 0, 9 min 20 s wall):

| Family | low | medium | high |
|--------|-----|--------|------|
| static reference | 2 | 2 | 2 |
| tausch | 2 | 1 | 1 |
| fenster1 (legal starts only) | 1 | 1 | 1 |
| fenster2 (legal starts only) | 1 | 1 | 1 |
| tausch_fenster2 (new) | 1 | 1 | 1 |

Required X (raw = capped) per cell. tausch_fenster2 has 1,059,867,648 paths per tier, and 971.8 M / 943.3 M / 918.5 M
of them are over budget. Unlosable and untrimmable counts are 0 in every cell, and no group fails at X = 3. Calibration:
"Empfohlenes X = Maximum + 1 = 3 (bestimmend: Tier low, Familie statisch, roh); Konfiguration X = 3: kalibriert".
`simulation_config.json` is unchanged.

**Pending (not done because of the "do not change tests/golden" constraint):** `tests/golden/gate_paths_{low,medium,high}.json`
still pin the old `fenster1`/`fenster2` values and have no `tausch_fenster2` entry. The slow test
`tests/test_gate_paths.py::test_path_gate_matches_golden` therefore fails until it is re-pinned with
`uv run pytest -m slow tests/test_gate_paths.py --update-golden` (about 10 min). The static and `tausch` entries do not
change.

---

_Fixed: 2026-11-01T22:57:54Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
