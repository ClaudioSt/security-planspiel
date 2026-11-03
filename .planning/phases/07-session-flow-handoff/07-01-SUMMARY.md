---
phase: 07-session-flow-handoff
plan: 01
subsystem: repo-layout
tags: [archive, legacy, inventory, tests, dependencies]
requires: []
provides:
  - "archive/mhp_print_material_2026-07/ (15 superseded MHP files + README)"
  - "archive/legacy_generators/ (3 generators, xlsx, pptx_output/, README)"
  - "tests/test_no_archive_references.py (D-17 proof)"
affects: [07-02, 07-03, 07-04]
tech-stack:
  added: []
  patterns: ["static scan of build inputs for retired paths plus git tree layout test"]
key-files:
  created:
    - tests/test_no_archive_references.py
    - archive/mhp_print_material_2026-07/README.md
    - archive/legacy_generators/README.md
  modified:
    - tests/test_inventory.py
    - tests/test_texts_migration.py
    - tests/test_single_definition.py
    - tests/test_environment.py
    - content/INVENTORY.md
    - content/assets/README.md
    - content/assets/GUIDELINES.md
    - archive/historical_docs/README.md
    - tests/fixtures/mini_config.json
    - planspiel/rules.py
    - pyproject.toml
    - uv.lock
  removed:
    - tests/test_legacy_generators_smoke.py
key-decisions:
  - "Generator-fidelity tests in test_texts_migration.py retired instead of retargeted to archive/ (keeps the suite decoupled from archive/, D-17)"
  - "python-pptx stays; the Excel library and its transitive et-xmlfile are removed"
requirements-completed: [LEG-01]
duration: ~25 min
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 01: Archive legacy material Summary

The 15 superseded MHP files, the three old generators, `pptx_output/`, the Excel calculator and the folienkonzept now live under `archive/` as pure git renames. A test proves the build reads none of them.

## Tasks and commits

| Task | Commit | Result |
|------|--------|--------|
| 1 RED | 71a4a64 | `KEPT_FILES`/`ARCHIVED_FILES` layout checks, md5-based image check, `tests/test_no_archive_references.py` (6 expected layout failures) |
| 2a | 9a2fdb3 | Retired generator-coupled tests (smoke test, two fidelity tests, helpers) |
| 2b | 3c3346d | Move commit: 26 `R` entries, no `D`/`A` (15 MHP + 3 scripts + xlsx + 6 pptx + folienkonzept) |
| 2c | 44cc1d0 | Archive READMEs, inventory `## Location`, asset notes, deck comments retargeted |
| 3 | 5a860d6 | Dropped the Excel dependency (`uv remove --no-sync`, then one `uv sync`) |

## Verification

- Task 3 gate: `107 passed, 213 warnings in 53.82s` (test_environment, test_inventory, test_no_archive_references, test_texts_migration, test_single_definition); `planspiel validate` and `planspiel texts`: 0 Fehler, 0 Warnung(en); the Excel library is absent from the environment.
- `git ls-files final_documents` outside `generated/`: 5; `archive/mhp_print_material_2026-07`: 16; `archive/legacy_generators`: 11; `docs`: 0.
- `git ls-files archive/obsolete_simulation_data_2026-01` count: 1 before and after (ignored dumps stayed untracked).
- Full fast suite deliberately not run (wave-1 siblings carry RED tests; 07-04 runs it as the integration gate).

## Deviations from Plan

- **Pragmatic call (as flagged in the plan):** the two generator-fidelity tests were retired, not retargeted.
- **[Rule 3] NFC normalisation:** `tests/test_no_archive_references.py` normalises `git ls-files` output to NFC (and sets `core.quotepath=off`), because umlaut file names would otherwise not match.
- Otherwise the plan was executed as written. The `simulation_config.json` comment is left to 07-02 Task 1, as planned.

## Known Stubs

None. `archive/mhp_print_material_2026-07/README.md` mentions `content/mhp_baseline.json`, which is created by a later Phase 7 plan (07-03).

## Self-Check: PASSED

Commits 71a4a64, 9a2fdb3, 3c3346d, 44cc1d0, 5a860d6 exist; both archive READMEs and the new test module exist.
