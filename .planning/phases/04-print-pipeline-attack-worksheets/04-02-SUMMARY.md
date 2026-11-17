---
phase: 04-print-pipeline-attack-worksheets
plan: 02
subsystem: print-model
tags: [print-model, worksheet, fractions, german-formatting, tdd]

requires:
  - phase: 03-content-source-veiling
    provides: RevealView, texte.toml content source, digit lint and allowlist
provides:
  - rules.worksheet_constants with BonusRow, RecoveryRow, WorksheetConstants, WorksheetInvariantError
  - planspiel/fmt.py German number formatting (format_number, format_signed, format_money, format_factor, format_percent, terminates)
  - planspiel/printmodel.py AttackSheet per wave with exact values, display strings and printed_fragments()
  - 25 worksheet wording keys under [sheets.angriff] and one reviewed allowlist entry
affects: [04-04 equivalence replay, 04-06 attack worksheet template]

tech-stack:
  added: []
  patterns:
    - "Derived printed numbers come from one rules.py NamedTuple helper built on existing primitives, so the single-definition guard stays green"
    - "Print model keeps exact fields and display strings side by side; the template inserts strings only, the replay reads exact fields only"
    - "Build guards turn a broken hand-calculation shape into PrintModelError (D-06, D-09)"

key-files:
  created:
    - planspiel/fmt.py
    - planspiel/printmodel.py
    - tests/test_worksheet_constants.py
    - tests/test_print_fmt.py
    - tests/test_print_model.py
  modified:
    - planspiel/rules.py
    - planspiel/texts.py
    - planspiel/analyze.py
    - content/texte.toml
    - content/digit_allowlist.toml
    - tests/fixtures/mini_content/texte.toml
    - tests/test_texts_migration.py
    - tests/test_single_definition.py

key-decisions:
  - "D-05: the CIA table gets one blank row per measure in the config (10 today), because 6 rows fit only 56 to 78 % of in-budget plans per tier"
  - "The cap is printed as its own number: the Fall step opens with 'Schwelle: 23 · Kappung: 8 · Obergrenze: 23 + 8 = 31' from the integer field reduction_cap"
  - "The D-10 phrase 'ab ,5 vom Betrag aufrunden' stays in MHP form through one reviewed allowlist entry; the pinned allowlist set grows from seven to eight"
  - "min_half_distance(cfg, constants) is public in printmodel.py so tests and the later replay can read the exact D-09 margins (1/10, 1/50, 1/70 on the real config)"

patterns-established:
  - "Display lines are tuples of strings and Box sentinels; the cap line is exactly one string so it is one composite PDF fragment"
  - "Fragments are the strings between boxes or single table cells that contain a digit, so the PDF check matches composite fragments, not bare digits"

requirements-completed: [PRINT-03]

duration: 40min
completed: 2026-10-20
status: complete
---

# Phase 4 Plan 02: Attack Worksheet Print Model Summary

**One AttackSheet per wave carries the exact worksheet numbers from `rules.worksheet_constants` next to the German display strings (weights, explicit Kappung and Obergrenze, rearranged Fall-3 formulas, exact slope, recovery step), with build guards for D-06 and D-09.**

## Performance

- **Duration:** about 40 min
- **Completed:** 2026-10-20
- **Tasks:** 3 (all TDD, RED and GREEN committed separately)
- **Files modified:** 13 (5 created, 8 modified)

## Accomplishments

- `rules.worksheet_constants(cfg, wave)` derives lower, `reduction_cap`, upper, euros per severity point, Fall-1 and Fall-2 damage and KZ, slope, bonus rows and the recovery table through `damage_euros`, `severity_scaled` and `kz_slope`. `WorksheetInvariantError` fires when base severity differs from the cap, when any tier has a severity multiplier other than 1 (D-06), or when an attack that allows recovery has more than one recovery-carrying measure (D-03).
- `planspiel/fmt.py` formats German numbers exactly (decimal comma, thousands dot, U+2212); `format_factor` prints `× 2`, `× 1,2` and `× 17 ÷ 7`; non-terminating values raise `ValueError` so nothing rounded can reach a sheet.
- `planspiel/printmodel.py` builds `angriff-1_ransomware`, `angriff-2_ot` and `angriff-3_exfil`. The D-09 guard checks every Fall-3 KZ value on the 1/ws lattice and refuses a config whose value lies closer than 1/100 to a half-integer (a mutated exfil attack with cap 11 gives 1/110 and fails; the real config has 1/10, 1/50, 1/70).
- 25 new wording keys in `[sheets.angriff]` (real and mini content), digit-free except the allowlisted `,5` in `wave_kz_rounding`.

## Task Commits

1. Task 1 RED: `3bac6d1` test(04-02): add failing worksheet constants and print formatting tests
2. Task 1 GREEN: `274cdec` feat(04-02): derive worksheet constants in rules and add print formatting
3. Task 2 RED: `3c130e3` test(04-02): require the attack worksheet wording keys
4. Task 2 GREEN: `148fc22` feat(04-02): add the attack worksheet step wording
5. Task 3 RED: `382d80a` test(04-02): add failing attack worksheet model tests
6. Task 3 GREEN: `57cd5d7` feat(04-02): add the attack worksheet print model

## RED Runs

- Task 1: collection errors `ModuleNotFoundError: No module named 'planspiel.fmt'` for `tests/test_print_fmt.py` and the missing `rules.worksheet_constants` import for `tests/test_worksheet_constants.py` (`2 errors`, interrupted).
- Task 2: `uv run planspiel texts` printed `25 Fehler, 0 Warnung(en)` (all `texts.missing_key sheets.angriff.*`); `pytest tests/test_texts_coverage.py tests/test_texts_migration.py` gave `26 failed, 24 passed`.
- Task 3: `ModuleNotFoundError: No module named 'planspiel.printmodel'` at collection.

## Verification

- `uv run pytest -q`: 979 passed, 24 deselected (baseline before this plan: 907).
- `uv run pytest tests/test_worksheet_constants.py tests/test_print_fmt.py tests/test_print_model.py tests/test_single_definition.py -q`: 126 passed.
- `uv run planspiel texts`: 0 Fehler, 0 Warnung(en); same for the mini config and mini content dir.
- `uv run planspiel validate`: 0 Fehler, 1 Warnung (the expected 17/7 HandCalcWarning, BAL-02).
- `grep -c '^\[\[allow\]\]' content/digit_allowlist.toml`: 8.
- Printed wording of the real sheets (normalised, box shown as ▢):
  - Wave 1: `E-Wert = C ▢ × 0,4 + I ▢ × 0,4 + A ▢ × 0,2 = ▢`; `Schwelle: 23 · Kappung: 8 · Obergrenze: 23 + 8 = 31`; `Fall 1: Gesamtreduktion ≤ 23 | Schaden vor Recovery: 160.000 € · KZ: −6`; `Fall 2: Gesamtreduktion ≥ 31 | Schaden vor Recovery: 0 € · KZ: +10`; `Schaden vor Recovery = (31 − GR ▢) × 20.000 € = ▢`; `KZ = −6 + (GR ▢ − 23) × 2 = ▢`; `Schaden nach Recovery = Schaden vor Recovery ▢ × (1 − r ▢) = ▢`; `KZ-Änderung dieser Welle = KZ Angriff ▢ + KZ Events ▢ = ▢, gerundet (ab ,5 vom Betrag aufrunden): ▢`.
  - Wave 2: cap line `Schwelle: 20 · Kappung: 10 · Obergrenze: 20 + 10 = 30`; `KZ = −5 + (GR ▢ − 20) × 1,2 = ▢`; damage `(30 − GR ▢) × 32.000 €`.
  - Wave 3 (no recovery, six steps): cap line `Schwelle: 25 · Kappung: 7 · Obergrenze: 25 + 7 = 32`; `Schaden = (32 − GR ▢) × 20.000 € = ▢`; `KZ = −7 + (GR ▢ − 25) × 17 ÷ 7 = ▢`; fraction hint selected.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `format_percent` name clash with `planspiel/analyze.py`**
- **Found during:** Task 1 GREEN (`test_formula_defined_once_in_rules[format_percent]` failed: defined in `analyze.py:25` and `fmt.py`)
- **Issue:** `analyze.py` already defined an unrelated `format_percent` for RoS report output; the plan requires `fmt.format_percent` to be the only definition.
- **Fix:** renamed the existing function to `format_ros_percent` (three call sites in the same file, no other users, output unchanged).
- **Files modified:** `planspiel/analyze.py`
- **Commit:** `274cdec`

Otherwise the plan was executed as written. `printmodel.py` has no CRLF issue to note; `tests/test_single_definition.py` and `rules.py` kept their working-tree line endings.

## Decisions Made

See key-decisions above. One addition beyond the plan's interface list: `min_half_distance` is a public helper (the plan's tests need the exact margins), and `AttackSheet` also carries `bonus_header`, `recovery_header` and `result_line` so the template inserts strings only. Plan 04-06 decides the column layout (the bonus table rows are `(measure, min_level, points, reason)`; the header has three cells and the template appends the "Erfüllt" column from `labels`).

## Known Stubs

None.

## Threat Flags

None. Mitigations T-04-06 to T-04-09 are in place: numbers only from `rules.worksheet_constants`, D-06 and D-09 guards raising `PrintModelError`, wording only in `[sheets.angriff]` (not in `PREWAVE_SHEETS`, pre-wave leak test green), one reviewed allowlist entry with the pinned set at eight, and the single-recovery-table guard.

## Self-Check: PASSED

- Files exist: `planspiel/fmt.py`, `planspiel/printmodel.py`, `tests/test_worksheet_constants.py`, `tests/test_print_fmt.py`, `tests/test_print_model.py`.
- Commits present: `3bac6d1`, `274cdec`, `3c130e3`, `148fc22`, `382d80a`, `57cd5d7`.
