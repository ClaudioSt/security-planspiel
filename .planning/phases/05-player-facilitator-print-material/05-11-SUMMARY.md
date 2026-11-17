---
phase: 05-player-facilitator-print-material
plan: 11
subsystem: rules
tags: [path-trace, practice, welle-0, config, validator, worked-example]

requires:
  - phase: 05-player-facilitator-print-material
    provides: rules.card_facts (05-02), rules.KZ_MIN/KZ_MAX (05-07), evaluate_path and the swap layer (Phase 2), PrintModelError and min_half_distance (Phase 4)
provides:
  - rules.WaveTrace, WindowTrace, ReviewTrace, PathTrace and path_trace(cfg, tier_name, path, enforce_kurswechsel=True)
  - config.Practice and the trailing Config.practice field (None without the block)
  - top-level practice block in simulation_config.json with its own attack, wave, event, start KZ, budget and the pinned example selection
  - validate._Validator.check_practice (plus check_attack and check_wave_scoring extracted from the real-wave checks)
  - planspiel.practice with PRACTICE_JOB, PRACTICE_TIER, practice_config and check_example
affects: [05-12, 05-14, 05-15]

tech-stack:
  added: []
  patterns:
    - "Read-only trace beside evaluate_path: legality, window costs and ledger come from the single definition, per-wave detail from the same primitives, no key added to simulate_waves or evaluate_plan (F2)"
    - "Practice as a configuration view: a throw-away Config in which the practice wave is the only wave; only practice.py reads cfg.practice"

key-files:
  created:
    - planspiel/practice.py
    - tests/test_path_trace.py
    - tests/test_practice_config.py
  modified:
    - planspiel/rules.py
    - planspiel/config.py
    - planspiel/validate.py
    - simulation_config.json
    - tests/test_single_definition.py

key-decisions:
  - "Pinned parameter set is the illustrated one from research FLOW-01 (the re-run confirmed every guard); no search over other sets was needed"
  - "check_example requires the unrounded wave change to be an exact half, not just a non-integer, because the exact half is what makes half away from zero visibly differ from half to even"
  - "The practice view sets practice=None and default_budget_tier to the practice tier, so the throw-away Config is self-consistent and cannot recurse"
  - "check_attacks and the scoring part of check_waves were split into check_attack and check_wave_scoring so the practice block reuses the real schema checks with a practice. path prefix"

patterns-established:
  - "Config blocks that must stay invisible to the real machinery are proven so by full Config equality with and without the block, equal evaluate_plan and TierKernel outcomes, and an unchanged overspend gate"

requirements-completed: []

duration: ~45 min (11:24 to about 12:10 on 2026-10-26)
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 11: Rules trace and practice configuration Summary

**`rules.path_trace` exposes every printed hand-calculation value of a game path and equals `evaluate_path`, the ledger and the independent worksheet replay; the new top-level `practice` block holds the Welle 0 incident with a pinned, guard-checked example (Fall 3, one bonus met and one missed, recovery, exact half 5/2 rounded to +3, clamp 101 to 100) and is provably invisible to waves 1-3.**

FLOW-01 spans this plan and 05-12 (document, story, golden test), so the requirement is intentionally not marked complete here.

## Accomplishments

- `rules.path_trace` (Task 1): per wave the CIA, E-value, bonus met and missed, Gesamtreduktion, Fall, damage before and after recovery, recovery factor, attack KZ, event KZ, the exact and the rounded wave change, KZ before, unclamped and after the clamp, own OPEX, external event budget and OPEX, the window cost after the wave and the running remaining budget. Per window the increases, credit and net cost; for the review the pre-review and final KZ, the review change, own spend, remaining budget, total damage, RoS and the final events. `PathError` and legality come from `evaluate_path`, so the trace raises exactly where it raises. Registered in `FORMULA_FUNCTIONS`.
- Practice block (Task 2): `practice` in `simulation_config.json`, `Practice` and `Config.practice` (trailing, default None), `check_practice` in the validator and `planspiel/practice.py` with the view and the guards.
- Invisibility proof: the real config with and without the block gives equal `Config` objects (except the `practice` field), equal `base_losses` (620), equal `scale_factors`, equal `evaluate_plan` and `TierKernel` results, and `planspiel gate` output equals the pinned `tests/golden/gate_*.json` for all three tiers.

## RED runs

- Task 1: `uv run pytest tests/test_path_trace.py -x -q` gave `AttributeError: module 'planspiel.rules' has no attribute 'path_trace'` (1 failed, 1 passed). Commit `1c9b614`.
- Task 2: `uv run pytest tests/test_practice_config.py -x -q` gave `ImportError: cannot import name 'practice' from 'planspiel'` (collection error). Commit `b0bef61`.

## Pinned practice parameters and their trace

Re-run on the practice view with `path_trace`: the illustrated set of research FLOW-01 holds every guard, so it is pinned unchanged.

| Part | Value |
|------|-------|
| Start KZ, budget | 98, 200 k€ |
| Attack | base severity 6 = cap 6, 20 k€ per step, KZ -6 at full damage, +9 at full mitigation (slope 5/2), recovery allowed |
| Wave | weights 0,3 / 0,3 / 0,4, threshold 18 (upper 24), bonus M9 L2 +4 and M10 L2 +3 |
| Event | `uebung_ereignis` "Übung", `measure_level_tier` on M2, tiers 0:-4, 1:-2, 2:+1, 3:+3 |
| Selection | M4 L1, M8 L2, M9 L2, M10 L1 (others 0), Init 104 k€, OPEX 23 k€ |

Trace: CIA 16 / 22 / 19, E-value 19, M9 met (+4), M10 missed, Gesamtreduktion 23, Fall 3, damage 20.000 € before and 18.000 € after recovery (r = 0,1), attack KZ +6,5, event -4, wave change before rounding +2,5, rounded +3, KZ 98 + 3 = 101 clamped to 100, remaining budget 73 k€, own spend 127 k€, RoS -25/127. Half-distance guard value 1/4 (limit 1/100). The weights differ from (0,4 0,4 0,2), (0,2 0,2 0,6) and (0,5 0,3 0,2) also as multisets; the bonus measures M9 and M10 are used by no real wave.

## Verification

- `uv run pytest -q`: 2075 passed, 131 deselected (baseline 1683; +348 path trace tests, +44 practice tests).
- `uv run planspiel validate`: 0 errors, 1 warning (the known 17/7 KZ-slope warning).
- `uv run planspiel gate`: bestanden for low (X strict 9, weak 8, witness 1121103000, 712882 over budget), medium (5/4, 1101103113, 658015) and high (3/3, 0011311033, 584583); identical to the pinned `tests/golden/gate_*.json`.
- `uv run pytest -m slow tests/test_digest.py tests/test_overspend_gate.py -q`: 9 passed (the pinned enumeration digests and the full gate goldens are unchanged).
- `git status --porcelain final_documents/generated`: empty. The pdf suite was not run (no TeX action in this plan; nothing it covers changed).

## Task Commits

1. Task 1 RED: `1c9b614` test(05-11): add failing path trace tests
2. Task 1 GREEN: `2fb8720` feat(05-11): add rules.path_trace for worked examples and answer keys
3. Task 2 RED: `b0bef61` test(05-11): add failing practice configuration tests
4. Task 2 GREEN: `1b922ae` feat(05-11): add the practice configuration and its view

## Deviations from Plan

### Auto-fixed Issues

None needed fixing. Two small choices go beyond the plan text:

- `check_example` is stricter than the behavior list: the unrounded wave change must be an exact half (the must-have truth says so), and the guard messages name the broken property in German. A non-integer, non-half change is rejected too.
- The shared real-wave schema code was split into `check_attack` and `check_wave_scoring` (pure moves, no behavior change; all of `tests/test_validate.py` stays green) so the practice block reuses it with a `practice.` path prefix instead of a copy.

### Test-only note

The exact-half test compares with the builtin `round()` on purpose to show that half to even gives 2 where the rules give 3. The ban on `round()` applies to `planspiel/rules.py` and `planspiel/rounding.py`, which stay clean.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. The only new surface is a config block read by one module; T-05-38 (block leaking into the real machinery), T-05-39 (weights or bonus measures hinting at a real attack) and T-05-51 (trace diverging from the simulation, example not teaching the mechanics) are mitigated and tested as described above.

## Next Phase Readiness

05-12 can build the Welle 0 document on `practice.check_example(cfg)` (the trace of the example) and `practice.practice_config(cfg)`; it must add the `[practice.*]` texts, the D-16 review checkpoint and the golden test. 05-13 must keep `Config.practice` last when it inserts `final_index`. 05-14 and 05-15 can use `path_trace` for the reference-path candidates and answer keys.

## Self-Check: PASSED

- Created files exist: `planspiel/practice.py`, `tests/test_path_trace.py`, `tests/test_practice_config.py`.
- Commits `1c9b614`, `2fb8720`, `b0bef61`, `1b922ae` are in `git log`.
