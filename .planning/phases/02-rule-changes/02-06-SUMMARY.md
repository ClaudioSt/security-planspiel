---
phase: 02-rule-changes
plan: 06
subsystem: rules
tags: [change-window, path-evaluator, swap-layer, legal-minimum, rule-02, d-01, d-02, d-03, d-04, d-05, d-06, d-07, d-09, d-12, d-21, d-22, d-23, d-24, d-27, d-28]
requires: [02-05, 02-02, 02-03]
provides:
  - "rules.simulate_waves(selections, budget_tier, waves, attacks, measures, events, base_cia, kz_start, ws, rs); simulate_selection delegates with identical output"
  - "rules.Window(selection, swap=None), rules.Path(start, windows=()), rules.PathError(reason, message) with the seven reason codes"
  - "rules.window_cost(measures, before, after, swap=None) with net pricing per measure (D-27)"
  - "rules.evaluate_path(cfg, tier_name, path, *, enforce_kurswechsel=True) with costs {init, window_costs, opex_by_wave, security_spend, event_opex, event_budget, total, budget_available, remaining}"
  - "rules.TierTables(cfg, tier_name) with path_outcome(codes, window_cost_total), swap_paths() and the per-state arrays"
  - "enumerate.enumerate_swap_layer(cfg, tier_name), report.SWAP_LAYER / SWAP_LABEL / summarize_swap_layer / format_swap_console"
  - "CLI: planspiel tausch [--config] [--tier ...] [--summary-dir] writing simulation_summary_tausch_<tier>.json"
  - "tests/support/harness.compact_from_path, tests/test_paths.py, tests/test_swap_layer.py"
affects: [02-07, 02-08]
tech-stack:
  added: []
  patterns: ["per-wave selections with a single wave loop", "per-state tables + index arithmetic for the swap layer, checked exhaustively against the exact evaluator", "histograms instead of per-path storage"]
key-files:
  created:
    - tests/test_paths.py
    - tests/test_swap_layer.py
  modified:
    - planspiel/rules.py
    - planspiel/enumerate.py
    - planspiel/report.py
    - planspiel/cli.py
    - tests/support/harness.py
    - tests/test_single_definition.py
    - README.md
    - CLAUDE.md
    - .planning/PROJECT.md
key-decisions:
  - "RULE-02 / D-01..D-07, D-27: the simulation models Levelwechsel up and down, cancel and add, any number per window; each measure is priced at its net Init change in the window, never a refund, no change fee; CIA/bonus/level effects and the new OPEX apply from the next wave"
  - "D-09 / D-12 / D-22 / D-23 / D-28: evaluate_path enforces exactly one legal Maßnahmentausch in the window after the Kurswechsel wave unless the wave-1 selection admits no swap; its Init delta is window cost and own spend in RoS"
  - "D-24: the swap layer (every valid wave-1 plan x every legal swap with the canonical minimal repair, exempt plans as static paths) is the legal minimum; it is labelled 'Pflicht-Maßnahmentausch (Kurswechsel), legales Minimum' next to the labelled static reference"
requirements-completed: [RULE-02]
duration: 31min
completed: 2026-10-04
status: complete
---

# Phase 2 Plan 06: Change-Window Paths and the Kurswechsel Swap Layer Summary

`evaluate_path` resolves every wave with the selection in force and prices change windows exactly (net Init change per measure, no refund, no fee, OPEX from the next wave, dependencies valid after every window), enforces the Kurswechsel swap with the 02-05 leaf functions, and books window costs as own spend. On top, `TierTables` evaluates all 37,300,736 legal swap paths per tier (plus 48,115 exempt static plans) in about 4 minutes, exactly equal to the evaluator, and `planspiel tausch` reports the legal minimum with its own label. No golden changed.

## Tasks

| Task | Name | Commit |
|------|------|--------|
| 1 RED | Failing tests for change-window paths | 3e02fd5 |
| 1 GREEN | Exact change-window path evaluator | 5a9c0be |
| 2 RED | Failing tests for the Kurswechsel swap layer | a977411 |
| 2 GREEN | Swap layer: TierTables, enumerate_swap_layer, report, CLI | 8824f05 |
| 3 | README change-window rules, CLAUDE.md, PROJECT.md | e2bdfaa |

## Verification

- Task 1 RED (3e02fd5): `49 failed, 428 passed, 11 deselected` (46 path tests plus the three single-definition registrations).
- Task 1 GREEN: `uv run pytest -q` gave `477 passed, 11 deselected`; goldens untouched (`git status` showed only `planspiel/rules.py`).
- Task 2 RED (a977411): fast file `17 failed, 1 passed, 2 deselected` plus the two new single-definition checks.
- Task 2 GREEN: `uv run pytest -q` gave `497 passed, 13 deselected`; no golden file changed.
- Final: `uv run pytest -q` gave `498 passed, 13 deselected, 97 warnings in 21.14s`.
- `uv run planspiel validate`: `0 Fehler, 1 Warnung(en)` (the known `hand_calc.kz_slope attacks.exfil`).
- Slow tests, run once: `uv run pytest -m slow -q tests/test_swap_layer.py -s` gave `2 passed, 18 deselected in 278.50s`. Low tier `enumerate_swap_layer` including the table build: **248.0 s** (bound 900 s), counts equal to the plan; 2,000 seeded random real swap paths equal `evaluate_path` exactly.
- `uv run planspiel tausch --tier low --tier medium --tier high --summary-dir <scratch>` run once, exit 0.
- Static reference goldens (characterization and digest) unchanged; the kernel and `evaluate_plan` were not edited.

## Swap layer results (real config, CLI run, summaries in a scratch directory)

| Tier | Runtime | Start plans | Exempt static | Swap paths | Swap in budget | Swap over budget | Legal games in / over budget |
|------|---------|-------------|---------------|------------|----------------|------------------|------------------------------|
| low | 240.6 s | 782,336 | 48,115 | 37,300,736 | 3,587,803 | 33,712,933 | 3,587,812 / 33,761,039 |
| medium | 219.0 s | 782,336 | 48,115 | 37,300,736 | 6,630,851 | 30,669,885 | 6,630,926 / 30,717,925 |
| high | 220.1 s | 782,336 | 48,115 | 37,300,736 | 10,699,761 | 26,600,975 | 10,700,130 / 26,648,721 |

All three tiers match research M9 and the plan exactly (low 3,587,803 / 33,712,933, medium 6,630,851 / 30,669,885, high 10,699,761 / 26,600,975). The runtimes include the table build (about 31 s) and the summary; the pure path iteration is about 21 s, `path_outcome` about 5.5 µs per path. Peak working set measured for table build plus 3 M paths: 62 MB (baseline interpreter 18 MB), so the per-state arrays (about 40 MB) dominate and the 37.3 M paths are never stored.

Best results of the legal minimum (End-KZ; ties by lower own cost, then lower start and end index):

| Tier | Best in budget | Best over budget |
|------|----------------|------------------|
| low | KZ 100, own cost 248, start `0002130200`, M4 -> M7 at level 2 | KZ 91, own cost 343 |
| medium | KZ 100, own cost 270, start `0120030200`, M3 -> M7 at level 3 | KZ 91, own cost 394 |
| high | KZ 100, own cost 322, start `1121100200`, M3 -> M7 at level 3 | KZ 89, own cost 445 |

Note for the RULE-04/Phase-6 reading: in the low tier the legal minimum reaches KZ 100 in budget, while the labelled static reference reaches 98 (02-03 summary). The swap moves a plan's level mix into waves 2 and 3, so the static reference is not an upper or lower bound of the legal results.

## Deviations from Plan

### Auto-fixed Issues

None. The plan's expected values (385 / 405, 36, 387, 31 OPEX, 126, 417, window cost 20, 32 net pricing) were all arithmetically correct and every vector test passed on the first GREEN run.

### Notes

- **RED shape:** `tests/test_paths.py` and the swap-layer tests access `rules.Path`, `rules.Window`, `rules.TierTables` etc. through the module so the RED run shows individual failures instead of a collection error.
- **Fast path in `swap_paths`:** `swap_repair` is only called when the dropped measure is required by another measure (`M2` in the real config). For every other dropped measure the canonical repair is the selection with that measure at 0, so the end index is `start - level * stride`; the full path iteration without outcomes took 21.3 s (low tier, measured) and the shortcut is covered by the mini brute force (which uses `swap_repair` for every swap) and the 2,000 seeded real paths (which use `swap_repair` through the evaluator).
- **`TierTables` duplicates the per-state wave loop of `TierKernel`** (the plan says the kernel stays unchanged and golden-protected); the exhaustive mini conformance against `TierKernel` and `evaluate_path` guards drift.
- **Best-path tie-break** includes the dropped and incoming measure indexes as last keys so the result is deterministic and equals the brute force.
- **README:** besides the plan's bullets, the "Rollen" line ("kommunizieren Changes") and the RoS cost line ("Init-Differenzen aus Upgrades") were reworded so no stale change-communication or upgrade wording remains; the three retired phrases are guarded by `test_readme_change_window_rules`.
- **CLI:** `--summary-dir` is created if missing (`mkdir(parents=True, exist_ok=True)`); an unknown `--tier` is rejected through the parser (exit code 2) before any file is written.
- Line endings preserved: CRLF kept in `rules.py`, `report.py`, `README.md`, `CLAUDE.md`, `PROJECT.md`, `test_single_definition.py`; new test files are CRLF, `cli.py`/`enumerate.py`/`harness.py` stay LF like before.
- The slow trim-back gate over move paths stays deferred to Phase 6 (D-25).

## Auth gates

None.

## Known Stubs

None.

## Threat Flags

None. T-02-22 (PathError reason for every malformed case, no silent repair) and T-02-23 (exhaustive mini conformance plus 2,000 seeded real paths) are covered by tests; T-02-24 (runtime and memory) measured at 4 minutes and 62 MB per tier; T-02-25 (user-chosen `--summary-dir`) accepted as planned.

## Self-Check

- FOUND: tests/test_paths.py, tests/test_swap_layer.py, `def evaluate_path(`, `def window_cost(`, `class TierTables`, `def enumerate_swap_layer(`, `SWAP_LABEL`
- FOUND commits: 3e02fd5, 5a9c0be, a977411, 8824f05, e2bdfaa
- `uv run pytest -q`: 498 passed; slow swap-layer tests: 2 passed; `uv run planspiel validate`: 0 Fehler
- `git log -5` shows test, feat, test, feat, docs in order

## Self-Check: PASSED
