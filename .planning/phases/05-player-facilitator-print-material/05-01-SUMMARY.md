---
phase: 05-player-facilitator-print-material
plan: 01
subsystem: print
tags: [veil, audience, pdf, pypdf, tex, tdd]

requires:
  - phase: 04-print-pipeline
    provides: render_all, planspiel print, stamp, texbuild, attack worksheets
  - phase: 03-texts-and-veil
    provides: giveaway list D-13b, story exceptions D-20, revealed namespace in texte.toml
provides:
  - job-prefix audience registry (spieler-, uebung-, angriff-, spielleitung-) enforced in render_all
  - two-layer veil scan (de-TeXed source and built PDFs) with the print.veil build gate
  - AST guard for pre-wave builder modules (PREWAVE_MODULES, empty until 05-02)
  - shared PDF text helpers for all Phase 5 pdf tests
affects: [05-02, 05-03, 05-04, 05-05, 05-06, 05-07, 05-08, 05-09, 05-10, 05-11, 05-12, 05-13, 05-14, 05-15, 05-16]

tech-stack:
  added: []
  patterns:
    - "Audience by job prefix: audience_of raises for an unclassified job, scan_profile picks names / story / other_attacks"
    - "Layer 1 scans detex(source) in the default suite and as a build gate; layer 2 scans pypdf text squashed of whitespace and hyphens"
    - "Weight triples only through rules.worksheet_constants + fmt.format_number (no .weights outside rules/config)"

key-files:
  created:
    - planspiel/audience.py
    - planspiel/veil.py
    - tests/support/pdf_text.py
    - tests/test_veil_audience.py
    - tests/test_veil_scan.py
    - tests/test_veil_models.py
    - tests/test_veil_pdf.py
  modified:
    - planspiel/render.py
    - planspiel/printmodel.py
    - planspiel/cli.py
    - tests/conftest.py
    - tests/test_print_cli.py
    - tests/test_print_cli_pdf.py
    - tests/test_print_render.py
    - tests/test_print_render_env.py
    - tests/test_print_check.py

key-decisions:
  - "Squash for the PDF layer removes whitespace and hyphens on both sides: LuaLaTeX hyphenation at a line end ('Datenex-filtration') must not hide a leaked name"
  - "Layer 1 also runs the squashed pass so a name split by TeX macros (Ran\\textbf{som}ware) is still found, while detex itself keeps macro-separated words apart"
  - "The revealed name is reported once as veil.name; veil.revealed_text covers the other attack-specific strings (narrative, cia_rationale, bonus reasons); case texts are shared wording and excluded"
  - "Unclassified or unknown revealed jobs are a veil.audience finding in the scan, in addition to render_all raising"

patterns-established:
  - "Later plans append their pre-wave builder module to tests/test_veil_models.py::PREWAVE_MODULES"
  - "New pdf tests import tests.support.pdf_text instead of private helpers"

requirements-completed: [VEIL-02]

duration: 90min
completed: 2026-10-23
status: complete
---

# Phase 5 Plan 01: Veil scan and audience registry Summary

**Automated two-layer veil scan (rendered .tex as a `print.veil` build gate, built PDFs in the pdf suite) over a job-prefix audience registry, so every later Phase 5 document is classified and scanned the moment it is registered.**

## Performance

- **Duration:** about 90 min
- **Completed:** 2026-10-23
- **Tasks:** 3 (all TDD, RED then GREEN)
- **Files created/modified:** 7 created, 9 modified

## Accomplishments

- `planspiel/audience.py`: prefix registry, `audience_of` (raises with the four allowed prefixes), `scan_profile` (names for `spieler-massnahmenkarten`, story for other pre-wave and practice jobs, other_attacks for revealed jobs, None for facilitator jobs). `render_all` calls `audience_of` for every job, so an unclassified document cannot be rendered.
- `planspiel/veil.py`: `detex`, weight triple detection (three consecutive number tokens plus the joined form), weight symbol rule (pre-wave only, practice exempt per D-12/D-14), name profiles, revealed-string match, `scan_text`, `scan_documents` (including job names, `veil.file_name`).
- `planspiel print` and `planspiel print --check` stop with `ERROR print.veil <code> <job>: <message>` before the stamp and before TeX (exit 1 and 2).
- `tests/test_veil_models.py`: AST guard with a self-test; `PREWAVE_MODULES` is empty until 05-02 appends `cards.py`.
- `tests/test_veil_pdf.py` plus `tests/support/pdf_text.py`: empty metadata, no XMP, outline or annotations on every built PDF; pre-wave/practice PDF text clean; revealed sheets name no other attack and print only their own weights; file names and manifest keys clean; a negative control built from `angriff-2_ot.pdf` fails the pdf layer.
- Today's print set (three worksheets plus the injected `spieler-smoke`) passes both layers; `uv run planspiel print --check` still reports the committed set fresh.

## Task Commits

1. Task 1 RED: `3a6c0b7` test(05-01): add failing audience registry tests
2. Task 1 GREEN: `9b1146a` feat(05-01): classify every print job by audience prefix
3. Task 2 RED: `e6eb038` test(05-01): add failing layer-1 veil scan tests
4. Task 2 GREEN: `44207c5` feat(05-01): add the layer-1 veil scan and the print.veil gate
5. Task 3 RED: `071b1f9` test(05-01): add failing pdf-layer veil tests
6. Task 3 GREEN: `fd3c5e0` feat(05-01): scan the built PDFs for leaks, metadata and file names

## RED runs (quoted)

Task 1, `uv run pytest tests/test_veil_audience.py -x -q`:

```
E   ImportError: cannot import name 'audience' from 'planspiel' (...\planspiel\__init__.py)
ERROR tests/test_veil_audience.py
1 error in 0.36s
```

Task 2, `uv run pytest tests/test_veil_scan.py ...` failed at collection with
`ImportError: cannot import name 'veil' from 'planspiel'`; the other new tests ran RED:

```
FAILED tests/test_print_cli.py::test_a_veil_leak_stops_the_build_before_the_stamp_and_tex
FAILED tests/test_print_cli.py::test_a_veil_leak_makes_check_fail_with_two
2 failed, 25 passed, 1 skipped
```

(`tests/test_veil_models.py` passes in the RED state by design: it tests the guard function itself and `PREWAVE_MODULES` is empty.)

Task 3, `uv run pytest -m pdf tests/test_veil_pdf.py -q` with `NotImplementedError` stubs:

```
FAILED test_squash_removes_all_whitespace_including_nbsp
FAILED test_helpers_read_the_built_pdfs - NotImplementedError
FAILED test_prewave_and_practice_pdfs_leak_nothing
FAILED test_revealed_pdfs_name_no_other_attack_and_print_only_their_own_weights
FAILED test_negative_control_the_pdf_layer_can_fail
5 failed, 4 passed
```

## Verification

- `uv run pytest -q`: 1266 passed, 1 skipped (the empty `PREWAVE_MODULES` parametrisation), 52 deselected (baseline was 1172 passed).
- `uv run pytest -m pdf -q`: 30 passed; `tests/test_veil_pdf.py` 9 passed, none skipped (LuaLaTeX present).
- `uv run pytest tests/test_single_definition.py -q`: 61 passed (no operand attribute in `veil.py`).
- `uv run planspiel texts`: 0 errors; `uv run planspiel validate`: 0 errors, the one expected 17/7 HandCalcWarning.
- `uv run planspiel print --check`: `Druckmaterial aktuell: Stand 2026-10-22 · 0d24b7d (3 Dokument(e) ...)`, exit 0.
- `git status --porcelain final_documents/generated`: empty.

## Decisions Made

See `key-decisions` above. The scan behaviour needed no change after the real PDFs were scanned: the three committed worksheets pass, so no profile was weakened.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Existing tests used unprefixed fake job names**
- **Found during:** Task 1 (`tests/test_print_render_env.py::test_render_all_merges_builders_sorted_by_job` failed once `render_all` classifies jobs) and Task 2 (20 tests in `tests/test_print_check.py` failed because the veil gate reports unclassified fake jobs `alpha`/`beta`/`gamma`).
- **Fix:** gave the fake jobs audience prefixes (`spieler-alpha` and so on) and made the duplicate-job test match the duplicate message instead of the job name. No production behaviour changed.
- **Files modified:** `tests/test_print_render_env.py`, `tests/test_print_check.py` (neither is in the plan's `files_modified`)
- **Commits:** `9b1146a`, `44207c5`

**2. [Rule 1 - Bug in own test input] Raw TeX passed to `scan_text`**
- **Found during:** Task 2 GREEN. `scan_text` takes already de-TeXed text (as the interface says, `scan_documents` de-TeXes first); three tests passed raw `\textbf{...}` input.
- **Fix:** the test helper de-TeXes at layer `tex`. Also reworded one deck test whose input accidentally contained the full M6 bonus reason, and stopped double-reporting the revealed name (it is reported once as `veil.name`, not additionally as `veil.revealed_text`).
- **Commit:** `44207c5`

**3. Squashing also removes hyphens (addition beyond the plan text)**
- The plan says squashed text; pypdf output of hyphenated words ("Datenex-" newline "filtration") would otherwise hide a leaked name. Both haystack and needles are squashed of whitespace and hyphens, tested in `test_pdf_layer_matches_names_on_squashed_text`.

**Stray command note:** one early `python3 -` invocation (no script) hung waiting on stdin and was moved to the background by the harness; it ran no code and changed nothing. All real Python runs used `uv run`.

## Known Stubs

None.

## Threat Flags

None. Threat register T-05-01 to T-05-06 are mitigated as planned; T-05-07 accepted (no template added).

## Issues Encountered

None beyond the deviations above.

## Next Phase Readiness

- Plan 05-02 can import `audience.MEASURE_DECK_JOB` for the deck job name and must append `cards.py` to `PREWAVE_MODULES`.
- Every new builder must name its jobs with one of the four prefixes; later pdf tests should import `tests.support.pdf_text`.

## Self-Check: PASSED

- Files exist: `planspiel/audience.py`, `planspiel/veil.py`, `tests/support/pdf_text.py`, `tests/test_veil_audience.py`, `tests/test_veil_scan.py`, `tests/test_veil_models.py`, `tests/test_veil_pdf.py`.
- Commits `3a6c0b7`, `9b1146a`, `e6eb038`, `44207c5`, `071b1f9`, `fd3c5e0` are in `git log`.
