---
phase: 04-print-pipeline-attack-worksheets
fixed_at: 2026-10-22T18:45:00+02:00
review_path: .planning/phases/04-print-pipeline-attack-worksheets/04-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 8
skipped: 0
status: all_fixed
---

# Phase 4: Code Review Fix Report

**Fixed at:** 2026-10-22
**Source review:** .planning/phases/04-print-pipeline-attack-worksheets/04-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 8 (CR-01, WR-01 to WR-07; Info findings were out of scope)
- Fixed: 8
- Skipped: 0

Every fix has a test that failed before the change (RED) and passes now. The worksheet PDFs were
regenerated once at the end (D-19) because CR-01 changes `planspiel.sty` and WR-04 changes the
rendered recovery table. `uv run planspiel print --check` exits 0 and the stamp is
`Stand 2026-10-22 · 0d24b7d` without `+lokal`.

Final test runs: `uv run pytest -q` gives 1172 passed, 43 deselected. `uv run pytest -m pdf -q`
gives 21 passed, 1194 deselected. The pdf layout tests (page fill, steps whole on their page,
fragments in the PDF text) stayed green.

## Fixed Issues

### CR-01: `tex_escape` lets babel-ngerman's `"` shorthand and TeX ligatures corrupt printed text silently

**Files modified:** `planspiel/render.py`, `print/planspiel.sty`, `tests/test_print_render_env.py`, `tests/conftest.py`, `tests/test_print_cli_pdf.py`
**Commit:** 06e0a28
**Applied fix:** The review's escape table for the ligature characters did not work. A bounded
LuaLaTeX run showed that an empty group `{}` between `-` `-` or `<` `<` does not interrupt the
`tlig` feature, so `a--b` still came out as an en dash. The fix therefore has two parts:
- `tex_escape` maps `"` to `\textquotedbl{}`, which neutralises babel-ngerman's active shorthand.
- `planspiel.sty` loads Arial with `RawFeature={-tlig}`, which switches the TeX input ligatures
  (`--`, `---`, `<<`, `>>`, `''`, `,,`, `!``, `?``) off. No template or text relies on them.

The smoke title now contains `"aktiv" "Auch" a--b <<c>> ,,d'' 0,5`, and a new `-m pdf` test asserts
that these characters appear verbatim in the extracted PDF text. Escape tests cover `"`. The test
failed first (quotes swallowed, then the ligatures after the `{}` attempt) and passes now.

### WR-01: `print --check` exit-code contract broken by uncaught exceptions

**Files modified:** `planspiel/cli.py`, `planspiel/render.py`, `planspiel/texbuild.py`, `tests/test_print_cli.py`, `tests/test_print_driver.py`, `tests/test_print_render_env.py`
**Commit:** 0ce503b
**Applied fix:**
- `OSError` next to `StampError` around `compute_stamp`, so a missing `planspiel.sty` gives `ERROR print.stamp` (exit 2 under `--check`, exit 1 on a build) instead of a traceback.
- `KeyError` (missing text key) is reported as `ERROR print.model`.
- `texbuild.check_job_name` is now called in `render_all`, so `--check` also validates job names. `build_documents` uses the same function.
- The build stage also catches `ValueError` and `OSError`.
- The publish loop catches `OSError` per file and reports `ERROR print.publish <file>` with exit 1.
- `run_lualatex` turns an `OSError` on deleting stale outputs (PDF open in a viewer) into a `TexBuildError` that names the file.

### WR-02: Orphan cleanup deletes every PDF in an arbitrary `--out-dir`

**Files modified:** `planspiel/cli.py`, `planspiel/stamp.py`, `tests/test_print_check.py`
**Commit:** 9ae3f20
**Applied fix:** New `stamp.previous_pdf_names(out_dir)` reads the manifest left by the earlier build
and returns the PDF names it lists. It returns nothing for an unreadable manifest and ignores names
that are not plain file names (`../x.pdf`). Cleanup removes only `previous - keep`. A PDF that the
pipeline never wrote, such as `Anfrage-Mail.pdf`, stays, and `--check` still reports it as an
orphan. The old test that expected an unlisted PDF to be deleted was replaced by four tests (listed
file removed, foreign file kept, path-escape ignored, unreadable manifest).

### WR-03: `planspiel print` does not enforce the content checks

**Files modified:** `planspiel/cli.py`, `tests/test_print_cli.py`
**Commit:** 9cc570b
**Applied fix:** The command loads the content with `load_content` and runs `check_texts` before
rendering. Any error-level issue is printed as `ERROR print.texts <code> <path>: <message>` and the
command stops (exit 1, or 2 under `--check`). The real `content/texte.toml` passes (`planspiel
texts` reports 0 errors). Tests inject a number into the prose of a copy of the mini content.

### WR-04: The recovery step never names the measure whose level sets r

**Files modified:** `planspiel/printmodel.py`, `tests/test_print_model.py`, `tests/test_print_render.py`
**Commit:** 92138aa
**Applied fix:** The middle (previously empty) header cell of the recovery table now holds
`_measure_name(cfg, recovery_measure)`, which prints "M4 – Backup & Disaster Recovery" today. It
costs no vertical space (the page fill is unchanged). The header is part of `printed_fragments()`,
so the existing PDF text test enforces it, and the rendered `.tex` test checks it too.

### WR-05: On POSIX the timeout kills only the direct child

**Files modified:** `planspiel/texbuild.py`, `tests/test_print_preflight.py`
**Commit:** 83d088b
**Applied fix:** On non-Windows platforms `_run_bounded` passes `start_new_session=True`, and
`_kill_tree` calls `os.killpg(pid, SIGKILL)`. The Windows branch (`taskkill /T`) is unchanged.
Tests use fakes (platform patched), so the real group kill is untested on this Windows machine.
Verified RED by stashing the change: three of the four new tests failed.

### WR-06: `print/** text eol=lf` will corrupt binary assets under `print/`

**Files modified:** `.gitattributes`, `tests/test_print_gitattributes.py` (new)
**Commit:** aff88c6
**Applied fix:** The LF rule is limited to `*.sty`, `*.cls`, `*.tex`, `*.j2` and `*.txt` under
`print/`. `png`, `jpg`, `jpeg`, `pdf`, `ttf` and `otf` under `print/` are marked `binary`. The new
test uses `git check-attr` on sample paths. It is a new file because no existing test covered
`.gitattributes`.

### WR-07: The stamp's date and `+lokal` flag describe fixed repo paths, not the inputs used

**Files modified:** `planspiel/stamp.py`, `planspiel/cli.py`, `tests/test_print_stamp.py`, `tests/test_print_cli.py`, `tests/test_print_check.py`
**Commit:** 8514b6a (plus f56ba21 for the encoding argument that the repo's encoding lint requires)
**Applied fix:** This is a logic fix; the semantics should be confirmed by a human (see below).
- `repo_for_inputs(config)` derives the repository from the config path and falls back to the working directory for a loose config. Absolute paths now work from outside the checkout.
- `nondefault_inputs(repo, config, content_dir, print_dir)` names every option that does not point at the repository default (`samefile` comparison; missing paths count as non-default).
- `compute_stamp(..., unofficial=True)` sets the dirty flag, so the stamp ends in `+lokal` and the manifest records `dirty: true`. The CLI prints a "Hinweis" line naming the options.

I chose "mark as `+lokal`" from the review's options rather than "reject non-default paths", because
the tests and the experiments with a mini config need the other paths to keep working.

## Regenerated output

**Commit:** 1446eac (`docs(04): regenerate the attack worksheets after the review fixes`)
`uv run planspiel print` rebuilt the three PDFs and `manifest.json`. All three PDFs changed (new
style without `tlig`), and the tex of waves 1 and 2 changed (WR-04). Each worksheet still has two
pages. `uv run planspiel print --check` exits 0.

## Skipped Issues

None. The Info findings (IN-01 to IN-09) were out of scope for `fix_scope: critical_warning`.

## Notes for the orchestrator

- I worked in the main working tree, as the task said, not in a separate worktree. No recovery sentinel or temporary branch exists.
- `.claude/settings.local.json` was modified before this run and was never staged.
- No background processes were left. One accidental bare `python -` call (hung on stdin) was killed immediately; it changed no files.
- No new dependencies, no MiKTeX or package-manager calls; TeX only ran through the project's bounded driver.

---

_Fixed: 2026-10-22_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
