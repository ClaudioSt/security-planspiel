---
phase: 04-print-pipeline-attack-worksheets
plan: 05
subsystem: print-version-stamp
tags: [stamp, content-hash, manifest, freshness-check, git, latex, tdd, print-pipeline]

requires:
  - phase: 04-print-pipeline-attack-worksheets
    provides: render stage, `planspiel print` CLI and TeX driver (plans 04-01, 04-03)
provides:
  - planspiel/stamp.py, the content-hash version stamp with UTC input commit date and scoped "+lokal"
  - stamp slot in print/planspiel.sty that stops the build when stamp.tex is missing
  - manifest.json writing, orphan PDF removal and `planspiel print --check` (exit 0/1/2)
affects: [04-06 attack worksheet template and first committed build]

tech-stack:
  added: []
  patterns:
    - "The stamp reaches TeX through stamp.tex written after hashing, so it can never feed back into its own hash"
    - "Dirty detection uses fixed pathspecs over build inputs only; output dirs (final_documents, build) and .planning are never listed"
    - "Git is called with argument lists, `-C <repo>`, constant pathspecs and a 30 s timeout; failures become StampError with German messages"
    - "A -recorder .fls check proves TeX read nothing in the build dir outside the hashed set"

key-files:
  created:
    - planspiel/stamp.py
    - tests/support/gitrepo.py
    - tests/test_print_stamp.py
    - tests/test_print_stamp_pdf.py
    - tests/test_print_check.py
  modified:
    - planspiel/texbuild.py
    - planspiel/cli.py
    - print/planspiel.sty
    - .gitattributes
    - tests/test_print_driver.py
    - tests/test_print_smoke.py
    - tests/test_print_cli.py

key-decisions:
  - "--check compares the stamp text and the full hash, the per-document rendered .tex hash and the PDF SHA-256; a dirty tree whose stamp text equals the manifest's still counts as fresh (no extra dirty rule), because the manifest of a dirty build carries +lokal and so only matches another identical dirty state"
  - "`texbuild.STAMP_FILE = \"stamp.tex\"` names the file in one place; `stamp.MANIFEST_NAME` was introduced with Task 1 instead of Task 3 because the constant is needed by the shared module"
  - "A missing manifest is reported as one STALE finding and ends the check; a malformed manifest likewise"

patterns-established:
  - "Stale findings are printed as `STALE <job-or-pdf>: <reason>` followed by the D-19 order hint (commit inputs, `uv run planspiel print`, commit final_documents/generated/)"

requirements-completed: [PRINT-11]

duration: 30min
completed: 2026-10-22
status: complete
---

# Phase 4 Plan 05: Version Stamp, Manifest and Freshness Check Summary

**Every page of every PDF from `planspiel print` carries "Stand <UTC date of the last data-input commit> · <7 hex of the content hash>" (plus "+lokal" on a dirty build input), and `planspiel print --check` finds stale, missing, hand-edited and orphaned PDFs from a committed manifest without running TeX.**

## Accomplishments

- `planspiel/stamp.py`: `content_hash` (SHA-256 over the rendered .tex strings and `planspiel.sty` with CRLF normalised, name and content NUL-separated, no stamp parameter), `input_date_utc` (`git log -1 --format=%ct` over `DATA_INPUTS`, converted with `timezone.utc`), `is_dirty` (`git status --porcelain --untracked-files=all` over `BUILD_INPUTS`), `compute_stamp`, `stamp_tex`, `recorded_local_inputs`, `write_manifest`, `check_freshness`.
- `print/planspiel.sty` reads `stamp.tex` with `\InputIfFileExists` and raises `\PackageError` when it is missing; the footer shows the stamp left and "Seite x von y" right. `build_documents` has a required `stamp_tex` keyword and writes `stamp.tex` after copying the static files and before TeX runs.
- `planspiel print` computes the stamp from the rendered set before building, prints `Stand: ...`, publishes the PDFs, removes PDFs in the out dir that are no longer in the print set, and writes `manifest.json` (stamp, hash, date, dirty flag, per document `pdf`, `tex_sha256`, `pdf_sha256`; sorted keys, two-space indent, LF).
- `planspiel print --check` renders without TeX (preflight and `build_documents` are never called), recomputes the stamp, and exits 0 (current), 1 (one `STALE` line per finding plus the order hint) or 2 (`ERROR print.input`, `print.render`, `print.stamp`).
- `.gitattributes` pins `final_documents/generated/manifest.json` to LF.

## Task Commits

1. Task 1 RED: `a402fb9` test(04-05): add failing version stamp tests
2. Task 1 GREEN: `a6d1fbd` feat(04-05): add the content-hash version stamp
3. Task 2 RED: `a4fc95e` test(04-05): require the stamp on every built page
4. Task 2 GREEN: `8524086` feat(04-05): print the version stamp on every page
5. Task 3 RED: `8cb7b72` test(04-05): add failing manifest and freshness check tests
6. Task 3 GREEN: `260f5c6` feat(04-05): add the print manifest and the freshness check

RED runs:

- Task 1: `tests/test_print_stamp.py` failed at collection with `ImportError: cannot import name 'stamp' from 'planspiel'`.
- Task 2: `tests/test_print_driver.py` and `tests/test_print_cli.py`: 14 failed, 15 passed (`TypeError` on the new `stamp_tex` keyword); pdf: `test_every_page_of_every_pdf_carries_the_same_stamp` failed.
- Task 3: `tests/test_print_check.py`: 19 failed; `tests/test_print_stamp_pdf.py`: the 2 manifest tests failed, 3 passed.

## Verification

- `uv run pytest tests/test_print_stamp.py -q`: 32 passed (UTC date `2026-10-19` from a `+02:00` 01:30 commit, code-only commit leaves the date, template commit moves it, untracked `print/new.sty` and modified `content/texte.toml` dirty, `final_documents/generated`, `build/`, `.planning/` and `content/clues.toml` not dirty, CRLF/LF style hash equal).
- `uv run pytest tests/test_print_check.py -q`: 19 passed.
- `uv run pytest -m pdf -v`: 14 passed, none skipped (stamp exactly once on every page of every PDF including the 2-page smoke document, one stamp for the whole set and both runs, recorder inputs within `{job.tex, job.aux, stamp.tex, planspiel.sty}`, manifest stamp equals the page stamp, manifests of two runs byte-identical, build without `stamp.tex` fails naming it).
- `git ls-files final_documents/generated` prints nothing.

### Real repository demo (clean build inputs, HEAD `260f5c6`)

```
$ uv run planspiel print --out-dir build/print-demo
Stand: Stand 2026-10-22 · 1162c5c
0 Dokument(e) gebaut: build\print-demo          (exit 0)
$ uv run planspiel print --check --out-dir build/print-demo
Druckmaterial aktuell: Stand 2026-10-22 · 1162c5c (0 Dokument(e) in build/print-demo)   (exit 0)
```

`build/print-demo/manifest.json`:

```
{
  "date": "2026-10-22",
  "dirty": false,
  "documents": {},
  "hash": "1162c5c97ee1a3bb0318f86478946ae8b6840866cf3e10994e235c557b09d642",
  "stamp": "Stand 2026-10-22 · 1162c5c"
}
```

A stray `stale.pdf` in the demo dir gave `STALE stale.pdf: nicht im Manifest (verwaiste Datei)`, `1 veraltet.`, the order hint and exit 1 (file removed afterwards). The production set is still empty, so the manifest lists no documents until plan 04-06.

## Deviations from Plan

None - plan executed as written, with two small placements: `MANIFEST_NAME` lives in `stamp.py` from Task 1 (one shared constants block), and `texbuild.STAMP_FILE` names the `stamp.tex` file once.

## Decisions Made

See key-decisions in the frontmatter.

## Known Stubs

None.

## Threat Flags

None beyond the plan's threat model. T-04-16 (stale printouts): stamp on every page (pdf test) and `--check`. T-04-17 (hand-edited PDFs): `pdf_sha256` plus orphan removal. T-04-18 (feedback into the hash, self-dirtying rebuild): `stamp.tex` outside the hash, dirty pathspecs exclude output dirs (temp-repo tests), recorder test. T-04-19 (git injection): argument lists, `-C`, constant pathspecs, timeout. T-04-20 (path disclosure): the stamp holds date and hash only; the manifest holds relative names and hashes.

## Issues Encountered

- During Task 2 I started an accidental bare `python -` (Inkscape's interpreter) in a shell command; it waited on stdin, was identified by its command line and killed. The heredoc edit it was part of produced garbled test code, which I reverted with `git checkout -- tests/test_print_driver.py` before redoing the edit with the Edit tool. No commit or tracked file was affected, and no process is left running.
- `HandCalcWarning hand_calc.kz_slope attacks.exfil` (17/7) still shows on every `load_config`; it is the known warning that stays until Phase 6.

## Next Phase Readiness

Plan 04-06 builds the worksheets and commits `final_documents/generated/` in the D-19 order: commit inputs, run `uv run planspiel print`, run `uv run planspiel print --check` (must exit 0), commit the PDFs and `manifest.json`. PRINT-03 stays pending until 04-06.

## Self-Check: PASSED

- Files exist: planspiel/stamp.py, tests/support/gitrepo.py, tests/test_print_stamp.py, tests/test_print_stamp_pdf.py, tests/test_print_check.py.
- Commits a402fb9, a6d1fbd, a4fc95e, 8524086, 8cb7b72, 260f5c6 present in `git log`.
