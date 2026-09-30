---
phase: 01-simulation-foundation
plan: 05
subsystem: validation
tags: [validator, config-check, hand-calculability, exactness-preconditions, cli, kz-slope]
requires: ["01-04"]
provides:
  - "planspiel/validate.py: Issue, ConfigError, HandCalcWarning, KNOWN_EVENT_TYPES, REQUIRED_EVENT_PARAMS, validate(raw), scale_factors(raw)"
  - "planspiel/rules.py: kz_slope (exact Fraction) as the single slope formula"
  - "planspiel/config.py: read_raw_config + check_config, called by load_config on every load"
  - "planspiel validate [--config PATH] [--strict] subcommand"
  - "tests/test_validate.py: 38 tests (17 error mutations, 6 warning mutations, load hook, CLI, subprocess wrappers)"
affects: [01-06, 01-07]
tech-stack:
  added: []
  patterns: ["collect-all-issues validator on raw dicts", "exact Fraction arithmetic for checks (float via repr, bool never a number)", "lazy import of validate inside check_config to avoid a config/rules/validate import cycle"]
key-files:
  created:
    - planspiel/validate.py
    - tests/test_validate.py
  modified:
    - planspiel/rules.py
    - planspiel/config.py
    - planspiel/cli.py
    - tests/test_single_definition.py
key-decisions:
  - "Dependency cycles are detected on the measure graph (any-level edges), as the plan's mutation test requires; this is coarser than a per-level analysis and can flag mutually dependent measures whose level requirements are actually satisfiable"
  - "Missing required fields are reported as schema.keys (not a separate code); missing top-level sections as schema.top_level"
  - "config.check_config imports planspiel.validate lazily: validate imports rules, rules imports config, so a top-level import would be circular"
requirements-completed: [FOUND-07]
duration: ~35min
completed: 2026-09-30
status: complete
---

# Phase 1 Plan 05: Config validator Summary

`planspiel.validate` rejects every broken reference or schema violation on every `load_config` (all errors collected, each with code and JSON path), reports hand-calculability problems as `HandCalcWarning` warnings, guards the exactness preconditions plan 01-06 needs, and is also available as `uv run planspiel validate [--config PATH] [--strict]`.

## Tasks

| Task | Name | Commits |
|------|------|---------|
| 1 | Validator core (errors, warnings, scale factors) with `kz_slope` in rules | RED 0a8fe65, GREEN e78d34a |
| 2 | Validate on every load and expose `planspiel validate` | RED 9108a24, GREEN c22d5cf |

## What was built

- `planspiel/validate.py`: `_Validator` walks the raw dict defensively (a malformed section never crashes the checks) and collects `Issue(level, code, path, message)`. Errors: `schema.top_level/type/keys/levels/range/wave_ids/e_targets/unknown_event_type/event_params/event_placement/tiers_order/duplicate_id`, `ref.unknown_tier/attack/measure/wave/dependency_cycle`, `exact.severity_scaling/damage_whole_euros`. Warnings: `hand_calc.kz_slope/severity_cap/severity_multiplier/weights/recovery` and `schema.default_used`. Numbers are read as `Fraction` (int, `Fraction(repr(float))`, or Fraction), so the checks are exact today and after the planned `parse_float=Fraction` switch. `scale_factors(raw)` returns `(WS, RS)` (lcm of weight / recovery denominators, `(10, 10)` today).
- `planspiel/rules.py`: `kz_slope(kz_at_full_damage, kz_at_full_mitigation, mitigation_cap) -> Fraction`; registered in `FORMULA_FUNCTIONS`. `apply_attack` is untouched (float bits stay pinned until 01-06).
- `planspiel/config.py`: `read_raw_config` (single UTF-8 read/parse place) and `check_config(raw, source)` (raises `ConfigError` with all errors, else one `HandCalcWarning` per warning); `load_config` calls both before building dataclasses.
- `planspiel/cli.py`: `validate` subcommand printing `ERROR|WARN <code> <path>: <message>` and `<n> Fehler, <m> Warnung(en)`; exit 1 on errors or (with `--strict`) warnings; unreadable or invalid JSON prints `ERROR schema.json`.

## Verification output

RED, Task 1 (`uv run pytest tests/test_validate.py -q` before the module existed): collection error `ImportError: cannot import name 'kz_slope' from 'planspiel.rules'`. RED, Task 2: `10 failed, 28 passed in 83.50s` (the two wrapper-refusal tests were slow because unvalidated `simulate_outcomes.py` ran the full enumeration).

```
uv run pytest tests/test_validate.py -q
38 passed, 1 warning in 0.65s
```
Collected: 17 `test_broken_config_is_reported` cases, 6 `test_hand_calc_issue_is_a_warning_not_an_error` cases.

```
uv run planspiel validate
WARN hand_calc.kz_slope attacks.exfil: KZ-Steigung 17/7 hat mehr als eine Nachkommastelle (verwendet in Welle 3)
0 Fehler, 1 Warnung(en)
exit=0
```
`uv run planspiel validate | grep -c "^WARN "` prints `1`; `uv run planspiel validate --strict` exits `1`.

```
uv run pytest -q
123 passed, 4 deselected, 15 warnings in 4.59s
```
The warnings summary lists `HandCalcWarning: hand_calc.kz_slope attacks.exfil: ... (verwendet in Welle 3)`.

Slow suite (load path changed, so run; no `--update-golden`): `uv run pytest -m slow -q` -> `4 passed, 123 deselected, 5 warnings in 347.59s (0:05:47)`. `git status --porcelain` is empty afterwards: goldens and digests unchanged.

## Deviations from Plan

None - plan executed as written. Notes:

- The plan's acceptance text mentions "exactly one WARN line"; the message additionally carries the German suffix `(verwendet in Welle 3)`, satisfying the required "Welle 3" and "17/7" content.
- `tests/fixtures/broken_*.json` from the research sketch were not created; the plan specifies in-memory mutations of the real config and `tmp_path` files instead.

## Auth gates

None.

## Known Stubs

None.

## Threat Flags

None. T-01-13 (malformed config) and T-01-14 (crash-at-simulation-time configs: missing e_target, unknown event type, misplaced final_budget_tier) are mitigated at load time and covered by tests, including the simulate and analyze scripts exiting non-zero before writing output; T-01-15 (JSON parsing) uses only `json.loads`, bool-as-number and non-finite floats are `schema.type` errors.

## Self-Check: PASSED

`planspiel/validate.py`, `tests/test_validate.py` exist; commits 0a8fe65, e78d34a, 9108a24, c22d5cf present in `git log`.
