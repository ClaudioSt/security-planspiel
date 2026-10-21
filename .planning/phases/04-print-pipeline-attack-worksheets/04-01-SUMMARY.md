---
phase: 04-print-pipeline-attack-worksheets
plan: 01
subsystem: print-pipeline
tags: [lualatex, miktex, texbuild, reproducible-pdf, smoke-gate, tdd]

requires:
  - phase: 03-content-source-veiling
    provides: tests/support helpers and the pytest layout the print tests extend
provides:
  - planspiel/texbuild.py with TEX_PROBES, STATIC_FILES, TexBuildError, MissingTex, missing_tex_files, preflight, run_lualatex, build_documents
  - print/planspiel.sty shared style (suppressoptionalinfo 1023, Arial by name, A4 worksheet margins, MHP colours, "Seite x von y" footer)
  - print/miktex-packages.txt (MiKTeX package ids incl. colortbl and tikzfill)
  - pytest marker pdf (default run excludes slow and pdf) and the five-test pdf smoke gate
affects: [04-03 render stage and print command, 04-05 version stamp, 04-06 attack worksheet template, Phase 5 card skins]

tech-stack:
  added: []
  patterns:
    - "Every TeX subprocess: argument list, installer disabled, stdin closed, timeout with process-tree kill (taskkill /F /T)"
    - "Aux-stable pass loop: re-run until the aux bytes repeat, error out instead of emitting a non-deterministic PDF"
    - "Byte-identical PDFs come from the style file (suppressoptionalinfo 1023), not from SOURCE_DATE_EPOCH"
    - "Injected fake runners for driver tests; real engine only under the pdf marker"

key-files:
  created:
    - planspiel/texbuild.py
    - print/planspiel.sty
    - print/miktex-packages.txt
    - tests/support/tex.py
    - tests/fixtures/print/smoke.tex
    - tests/test_print_preflight.py
    - tests/test_print_driver.py
    - tests/test_print_smoke.py
  modified:
    - pyproject.toml
    - .gitignore
    - .gitattributes

key-decisions:
  - "kpsewhich is always called with --miktex-disable-installer; lualatex with --disable-installer (a bare call hangs on MiKTeX's invisible installer dialog)"
  - "Reproducibility lives in print/planspiel.sty; SOURCE_DATE_EPOCH/FORCE_SOURCE_DATE are belt and braces only"
  - "Arial is set by name and never by Path=, because the two give different (each deterministic) bytes"
  - "MiKTeX was updated by the user (23.10.12 to 26.5); the executor never touched the installation (D-17)"

patterns-established:
  - "pdf-marked tests are opt-in (uv run pytest -m pdf); fast suite stays TeX-free"
  - "Drift test ties the packages loaded by print/planspiel.sty and print/templates/*.j2 to TEX_PROBES and print/miktex-packages.txt"

requirements-completed: [PRINT-01]

coverage:
  - id: D1
    description: "TeX driver whose every subprocess is installer-disabled, stdin-closed and time-bounded, with an aux-stable pass loop and safe job names"
    requirement: PRINT-01
    verification:
      - kind: unit
        ref: "tests/test_print_preflight.py, tests/test_print_driver.py (34 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Shared print style and package list; two builds of the smoke document are byte-identical without date, producer or trailer ID"
    requirement: PRINT-01
    verification:
      - kind: integration
        ref: "uv run pytest -m pdf tests/test_print_smoke.py (5 passed, 0 skipped)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Missing package fails fast naming the file; runaway document is killed at its time limit and leaves no process holding the build dir"
    requirement: PRINT-01
    verification:
      - kind: integration
        ref: "tests/test_print_smoke.py::test_missing_package_fails_fast_and_names_the_file, ::test_runaway_document_is_killed_at_the_time_limit"
        status: pass
    human_judgment: false

duration: ~35min active (excludes the user's MiKTeX update wait)
completed: 2026-10-21
status: complete
---

# Phase 4 Plan 01: TeX Toolchain Smoke Gate Summary

**Non-interactive LuaLaTeX driver (bounded runner with process-tree kill, MiKTeX-installer-disabled preflight, aux-stable pass loop) plus a shared style that makes rebuilt PDFs byte-identical, proven on this machine by a five-test pdf smoke gate.**

## Performance

- **Duration:** ~35 min of agent work; the user's MiKTeX update/install checkpoint is not counted
- **Started:** 2026-10-20 (first commit 15:19 +0200)
- **Completed:** 2026-10-21
- **Tasks:** 3 of 3 (Task 3 is the user checkpoint plus verification)
- **Files modified:** 11 (8 created, 3 modified)

## Accomplishments

- `planspiel/texbuild.py`: preflight lists each missing probe file with its MiKTeX package id; `run_lualatex` runs with `--disable-installer`, `-halt-on-error`, closed stdin and a timeout whose expiry kills the whole process tree; `build_documents` validates job names against `^[a-z0-9][a-z0-9_-]*$` and writes LF-only UTF-8 sources.
- `print/planspiel.sty`: hardening (`\pdfvariable suppressoptionalinfo 1023`), Arial by name, A4 with the Word-worksheet margins, MHP colours, footer "Seite x von y" resolved through the pass loop.
- Smoke gate on the real engine after the user's MiKTeX update: byte-identical rebuild, LastPage label on page 2, no `/CreationDate`, `/ModDate`, `/Producer` or trailer `/ID`, fail-fast on a missing package, timeout kill.

## Task Commits

1. **Task 1 RED: failing driver and preflight tests** - `4ad2362` (test)
2. **Task 1 GREEN: TeX driver and preflight** - `886a99e` (feat)
3. **Task 2 RED: failing style drift and pdf smoke tests** - `54eb226` (test)
4. **Task 2 GREEN: shared style, package list and smoke gate** - `126d746` (feat)
5. **Task 3: user checkpoint, verification only** - no file change; `print/miktex-packages.txt` already listed `colortbl` and `tikzfill`

**Plan metadata:** see the `docs(04-01)` commit that adds this summary.

## Task 3 Checkpoint (human-action, resolved)

User reply, verbatim: "done". The orchestrator verified: `lualatex --disable-installer --version` printed "This is LuaHBTeX, Version 1.25.7 (MiKTeX 26.5)"; `kpsewhich --miktex-disable-installer colortbl.sty tikzfill.sty` printed both paths, exit 0. MiKTeX was 23.10.12 before; the user updated it and installed `tikzfill` (and `colortbl`) per D-17.

Re-verified by the continuation executor (all bounded with `timeout`):

| Check | Result |
|-------|--------|
| `timeout 60 kpsewhich --miktex-disable-installer colortbl.sty tikzfill.sty` | `.../tex/latex/colortbl/colortbl.sty` and `.../tex/latex/tikzfill/tikzfill.sty`, exit 0 (research assumption A1 holds on MiKTeX 26.5) |
| `timeout 60 lualatex --disable-installer --version` | LuaHBTeX, Version 1.25.7 (MiKTeX 26.5), Development id 7740 |
| `uv run pytest tests/test_print_preflight.py tests/test_print_driver.py -q` | 34 passed |
| `uv run pytest -m pdf tests/test_print_smoke.py -v` | 5 passed, 0 skipped (26.99 s) |
| `uv run pytest -q` | 979 passed, 24 deselected (slow and pdf), 38.00 s |
| `git status --porcelain build` | empty (build output ignored) |

## Decisions Made

- Kept the flagged `kpsewhich` call; no fallback was needed on MiKTeX 26.5, so nothing is reported as a blocker for plan 04-03.
- RED evidence: both RED commits (`4ad2362`, `54eb226`) precede their GREEN commits in `git log`; the RED runs failed by design because `planspiel.texbuild` and `print/planspiel.sty` did not exist yet.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Timeout test left the build directory locked after the process-tree kill**
- **Found during:** Task 2 (runaway-document pdf test)
- **Issue:** `taskkill /F /T` returns before the killed processes have released their file handles, so `shutil.rmtree` of the build dir right after the kill could fail on Windows.
- **Fix:** `_kill_tree` now sleeps `KILL_SETTLE_S = 1.0` after taskkill.
- **Files modified:** `planspiel/texbuild.py`
- **Verification:** `test_runaway_document_is_killed_at_the_time_limit` passes (rmtree succeeds right after the kill)
- **Committed in:** `126d746`

### Environment change

**2. MiKTeX 23.10.12 updated to 26.5 by the user.** The plan expected "the current release" (research saw 25.12). The newer engine (LuaHBTeX 1.25.7 instead of 1.17.0) was verified by the smoke gate; byte identity was measured on the new engine, not the one in the research notes. This was the planned user action, not an executor deviation.

**Total deviations:** 1 auto-fixed bug, 1 expected environment change. **Impact:** none on scope.

## Known Stubs

None.

## Threat Flags

None. The surface added (TeX subprocesses, job-name validation, package install by the user) is exactly the plan's threat register T-04-01 to T-04-05; each mitigation is exercised by a test.

## Issues Encountered

None beyond the settle-time fix above.

## Next Phase Readiness

Plan 04-03 can build the Jinja render stage and `uv run planspiel print` on `texbuild.build_documents`. `tikzfill` is installed for Phase 5. Note for later plans: any new LaTeX package must be added to `TEX_PROBES` and `print/miktex-packages.txt` (the drift test enforces this) and installed by the user.

## Self-Check: PASSED

- Files found: planspiel/texbuild.py, print/planspiel.sty, print/miktex-packages.txt, tests/support/tex.py, tests/fixtures/print/smoke.tex, tests/test_print_preflight.py, tests/test_print_driver.py, tests/test_print_smoke.py
- Commits found in `git log`: 4ad2362, 886a99e, 54eb226, 126d746
- Final test runs quoted above are from this session.
