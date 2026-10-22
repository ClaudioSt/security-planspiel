---
phase: 04-print-pipeline-attack-worksheets
plan: 03
subsystem: print-pipeline
tags: [jinja2, latex, cli, render, reproducible-pdf, pypdf, tdd]

requires:
  - phase: 04-print-pipeline-attack-worksheets
    provides: texbuild preflight and build_documents driver, planspiel.sty (plan 04-01)
provides:
  - planspiel/render.py with tex_escape, make_env, DOCUMENT_BUILDERS, render_all
  - "`uv run planspiel print` (preflight, render, build, publish to final_documents/generated/)"
  - session fixture printed_set (two real CLI builds of the print set plus an injected smoke document)
  - pinned jinja2==3.1.6 (runtime) and pypdf==6.19.0 (dev) in pyproject.toml and uv.lock
affects: [04-05 stamp and manifest, 04-06 attack worksheet template]

tech-stack:
  added: [jinja2==3.1.6, markupsafe==3.0.4 (transitive), pypdf==6.19.0 (dev)]
  patterns:
    - "tex_escape is the Jinja finalize hook: a template can print only strings, never a raw number or an undefined name"
    - "CLI calls texbuild/render through their modules so tests monkeypatch preflight, render_all and build_documents"
    - "printed_set wraps render_all to inject the smoke document, so every document registered later joins the byte-identity test"

key-files:
  created:
    - planspiel/render.py
    - tests/test_print_render_env.py
    - tests/test_print_cli.py
    - tests/test_print_cli_pdf.py
    - tests/fixtures/print/smoke.tex.j2
  modified:
    - planspiel/cli.py
    - tests/conftest.py
    - pyproject.toml
    - uv.lock

key-decisions:
  - "StrictUndefined is surfaced from inside tex_escape (str() on the Undefined object), so a missing variable raises UndefinedError naming it instead of a misleading TypeError"
  - "The CLI reports Jinja and escaping failures as ERROR print.render (not in the plan's list of codes) so a template mistake is not mistaken for a TeX failure"
  - "out-dir is created only after a successful build, so a failed run leaves no half-published directory"

patterns-established:
  - "Error lines `ERROR print.<stage> <message>` per stage: preflight, input, render, tex"

requirements-completed: [PRINT-01]

duration: 35min
completed: 2026-10-22
status: complete
---

# Phase 4 Plan 03: Render Stage and `planspiel print` Summary

**One command, `uv run planspiel print`, runs the TeX preflight, renders every registered document through a strict escaping Jinja environment, builds with the installer-disabled driver and publishes byte-identical PDFs to `final_documents/generated/`.**

## Performance

- **Duration:** about 35 min of work plus a pause for a DNS block (see Task 1)
- **Completed:** 2026-10-22
- **Tasks:** 3 (1 checkpoint, 2 TDD)
- **Files modified:** 9 (5 created)

## Accomplishments

- `tex_escape` escapes the ten LaTeX specials in one pass and rejects non-strings and control characters; `make_env` uses `\VAR{}`/`\BLOCK{}`/`\#{}` delimiters, `StrictUndefined` and `finalize=tex_escape`.
- `planspiel print` fails within seconds on a missing TeX package or engine (missing files, MiKTeX package ids, install hint) before anything is rendered or built.
- The `printed_set` fixture builds the print set plus a Jinja smoke document twice through the real command; the PDFs are byte-identical and the text shows "Seite 1 von 2" / "Seite 2 von 2" and the escaped specials.
- Today the registry holds no production document, so the real `uv run planspiel print` exits 0 with "0 Dokument(e) gebaut"; plan 04-06 registers the worksheets.

## Task 1: Supply-chain check (blocking checkpoint)

jinja2 3.1.6, pypdf 6.19.0 and the transitive markupsafe were flagged SUS by the research audit (heuristics only). The user's reply, verbatim:

> 04-03 approved

This approves the pins exactly as written. No PyPI dependency was added before this reply. The `uv add` commands below ran after it, and the commit that changes `uv.lock` is the Task 2 RED commit (5f754ab).

**DNS pause:** an earlier attempt at the install failed because the user's Pi-hole sinkholed `files.pythonhosted.org`. The user allowlisted the host; `nslookup files.pythonhosted.org` then returned real addresses (151.101.x.223) and the install succeeded on the normal path. No mirror, alternative resolver or manually downloaded wheel was used.

```
uv add jinja2==3.1.6          -> + jinja2==3.1.6, + markupsafe==3.0.4
uv add --dev pypdf==6.19.0    -> + pypdf==6.19.0
```

## Task Commits

1. **Task 1: supply-chain approval** - no commit (checkpoint; approval quoted above)
2. **Task 2 RED + dependencies:** `5f754ab` test(04-03): add failing render stage tests
3. **Task 2 GREEN:** `e611d0c` feat(04-03): add the Jinja render stage
4. **Task 3 RED:** `59089bf` test(04-03): add failing planspiel print tests
5. **Task 3 GREEN:** `533fca1` feat(04-03): add the planspiel print command

RED runs:

- Task 2: `tests/test_print_render_env.py` failed at collection, `ImportError: cannot import name 'render' from 'planspiel'`.
- Task 3: `tests/test_print_cli.py` failed 6 of 6 with `argument command: invalid choice: 'print' (choose from validate, tausch, gate, texts, clues)`; the three pdf tests errored in the `printed_set` fixture for the same reason.

## Verification

- `uv run pytest -q`: 1016 passed, 27 deselected (baseline 979 + 31 render env tests + 6 CLI tests), no pdf-marked test runs.
- `uv run pytest -m pdf -v`: 8 passed, 0 skipped (3 in `tests/test_print_cli_pdf.py`, 5 in `tests/test_print_smoke.py`).
- `uv run planspiel print`: exit 0, "0 Dokument(e) gebaut: final_documents\generated", nothing written.
- `uv run planspiel print --help` lists `--config`, `--content-dir`, `--print-dir`, `--out-dir`, `--build-dir`.

## Decisions Made

See key-decisions in the frontmatter. No MiKTeX installation was touched and no TeX package manager was run (D-17); all TeX calls went through the bounded, installer-disabled driver of plan 04-01.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] RED test expected a trailing newline that `trim_blocks` removes**
- **Found during:** Task 2 GREEN
- **Issue:** `test_block_loop_works` expected `"abc\n"`; with `trim_blocks=True` (required by the plan) the newline after `\BLOCK{endfor}` is consumed.
- **Fix:** expectation corrected to `"abc"` with a comment; renderer unchanged.
- **Files modified:** tests/test_print_render_env.py
- **Commit:** e611d0c

**2. [Rule 2 - Missing critical functionality] `StrictUndefined` would have surfaced as TypeError**
- **Found during:** Task 2 design
- **Issue:** Jinja passes the Undefined object to `finalize`; a plain `isinstance(str)` check would raise `TypeError` and hide the variable name the behaviour list requires (`UndefinedError`).
- **Fix:** `tex_escape` calls `str()` on an `Undefined`, which raises `UndefinedError` for `StrictUndefined`.
- **Files modified:** planspiel/render.py
- **Commit:** e611d0c

**3. [Rule 2 - Missing critical functionality] Render errors had no CLI error line**
- **Found during:** Task 3
- **Issue:** the plan names `print.preflight`, `print.input` and `print.tex` only; a template error (`UndefinedError`, `TypeError`, `ValueError` from `tex_escape`) would escape as a traceback.
- **Fix:** added `ERROR print.render` and a catch of `jinja2.TemplateError`, `TypeError`, `ValueError` around `render_all`. A kpsewhich hang inside `preflight` (`TexBuildError`) is reported as `print.preflight` as well.
- **Files modified:** planspiel/cli.py
- **Commit:** 533fca1

**4. [Process] Commit trailer typo fixed by amend**
- The Task 3 GREEN commit first carried "Claudio Sonnet" in the co-author trailer; I amended that unpushed commit (cd6bc7e became 533fca1). No other content changed.

### Auth gates

None. The DNS block of Task 1 was an environment gate resolved by the user allowlisting the host.

## Known Stubs

None. `DOCUMENT_BUILDERS = ()` is intentional and documented in the plan; plan 04-06 registers the attack worksheets.

## Threat Flags

None beyond the plan's threat model (T-04-10 mitigated by `tex_escape` and `StrictUndefined`; T-04-SC by the Task 1 gate and exact pins; T-04-11 by preflight before any build).

## Issues Encountered

`HandCalcWarning hand_calc.kz_slope attacks.exfil` (slope 17/7) appears on every `load_config`, including `planspiel print`. It is the known warning that stays until Phase 6 (D-08, BAL-02), not an error.

## Next Phase Readiness

Plans 04-05 (stamp, manifest, `--check`) and 04-06 (worksheet template, registration in `DOCUMENT_BUILDERS`) can plug into `render.py` and `_print_command`; the `printed_set` byte-identity test covers anything they register.

## Self-Check: PASSED

- Files: planspiel/render.py, tests/test_print_render_env.py, tests/test_print_cli.py, tests/test_print_cli_pdf.py, tests/fixtures/print/smoke.tex.j2 exist; planspiel/cli.py and tests/conftest.py modified.
- Commits 5f754ab, e611d0c, 59089bf, 533fca1 present in `git log`.
