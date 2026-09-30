---
phase: 01-simulation-foundation
plan: 01
subsystem: infra
tags: [uv, python-3.12, pytest, uv_build, packaging]
requires: []
provides:
  - "uv project (pyproject.toml, uv.lock, .python-version) with pinned pytest 9.1.1, openpyxl 3.1.5, python-pptx 1.0.2"
  - "installable planspiel package skeleton with console script and python -m entry point"
  - "tests skeleton (tests/support REPO_ROOT / CONFIG_PATH) and registered slow marker"
affects: [01-02, 01-03, 01-04, 01-05, 01-06, 01-07]
tech-stack:
  added: [uv, uv_build, pytest 9.1.1, openpyxl 3.1.5, python-pptx 1.0.2]
  patterns: ["all commands via uv run", "python-preference = only-managed", "pytest -m 'not slow' by default"]
key-files:
  created: [pyproject.toml, uv.lock, .python-version, planspiel/__init__.py, planspiel/__main__.py, planspiel/cli.py, tests/__init__.py, tests/support/__init__.py, tests/test_environment.py]
  modified: [.gitignore, README.md, CLAUDE.md, .claude/CLAUDE.md]
key-decisions:
  - "uv_build range >=0.12,<0.13 (matches installed uv 0.12.x)"
  - "openpyxl and python-pptx are runtime deps only for the legacy generators (dropped in Phase 7)"
  - "python-preference = only-managed so Inkscape's pip-less python is never picked"
requirements-completed: [FOUND-01]
duration: 15min
completed: 2026-09-30
status: complete
---

# Phase 1 Plan 01: uv environment and planspiel skeleton Summary

One-command reproducible environment (`uv sync`) with a committed hashed lockfile, a uv-managed CPython 3.12 pin, and an installable `planspiel` package (console script plus `python -m planspiel`) so later plans run `uv run pytest` regardless of the `python` on PATH.

## Tasks

| Task | Name | Commit |
|------|------|--------|
| 1 | uv project, planspiel skeleton, environment smoke tests | 51d4e8b |
| 2 | Document uv commands, fresh-clone proof | ae6595c |

TDD: `tests/test_environment.py` was written before `planspiel/cli.py` and `planspiel/__main__.py`. RED run: `2 failed, 6 passed` (console script and `-m planspiel` missing). GREEN after the two files: `8 passed`. Both went into one commit because the tests and the skeleton are one scaffolding unit.

## Verification output

`uv sync --locked`:
```
Resolved 14 packages in 0.74ms
Checked 14 packages in 1ms
```

`uv run pytest -q`:
```
........                                                                 [100%]
8 passed in 0.50s
```

`uv run planspiel --help` from repo root and from `planspiel/` both exit 0 (usage: `planspiel [-h] {} ...`, description "Werkzeuge für das CIA-Planspiel (Simulation, Prüfungen).").

`uv run python simulate_outcomes.py --help` exits 0 (`usage: simulate_outcomes.py [-h] [--config CONFIG] ...`); `analyze_simulation_results.py --help` and `balance_analysis.py` exit 0 via `test_documented_wrappers_run`.

Fresh-clone check (`git clone` of committed state, `PATH="/c/Program Files/Inkscape/bin:$PATH"`, `which python` -> `/c/Program Files/Inkscape/bin/python`):
```
Using CPython 3.12.14
Creating virtual environment at: .venv
Installed 14 packages in 339ms
........                                                                 [100%]
8 passed in 0.73s
rc=0
```

Acceptance greps: README `uv run python simulate_outcomes.py` = 3, `uv run python analyze_simulation_results.py` = 2, `^python3 ` = 0; CLAUDE.md contains `uv run python balance_analysis.py` and `uv sync`; `.claude/CLAUDE.md` contains `uv.lock` and `uv sync`; `uv.lock` has `name = "pytest"` / `version = "9.1.1"`; `git ls-files angriff_berechnung.xlsx` still lists the file; `sim_low.json`, `sim_med.json`, `sim_high.json` are ignored and untracked (D-22).

## Deviations from Plan

None - plan executed exactly as written. `uv add` produced the `dependencies` list and `[dependency-groups] dev` entries in `pyproject.toml` as planned; the two tasks' commits were split per task rather than one combined commit (Task 2 says "commit all", but per-task commits are the executor protocol).

## Known Stubs

None. `planspiel/cli.py` has an empty subparser set by design; plan 01-0x adds `validate`.

## Threat Flags

None.

## Self-Check: PASSED

All created files exist; commits 51d4e8b and ae6595c present in `git log`.
