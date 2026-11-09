# Technology Stack

**Analysis Date:** 2026-11-09

## Languages

**Primary:**
- Python 3.12 - the `planspiel` package (`planspiel/`), the root wrapper scripts (`simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`) and the pytest suite (`tests/`)

**Secondary:**
- LaTeX (LuaLaTeX) - all print material; source is Jinja2 templates in `print/templates/*.tex.j2` plus the style file `print/planspiel.sty`
- TOML - prose and rule matrices: `content/texte.toml`, `content/clues.toml`, `content/digit_allowlist.toml`, `content/giveaway_terms.toml`
- JSON - the central parameter file `simulation_config.json`, the frozen MHP-round values `content/mhp_baseline.json`, pinned reference data `tests/golden/*.json`, and the generated `final_documents/generated/manifest.json`
- Markdown - the German rulebook `README.md`, and planning artifacts in `.planning/`

## Runtime

**Environment:**
- CPython 3.12 (`.python-version` pins `3.12`; `pyproject.toml` requires `>=3.12`)
- `[tool.uv] python-preference = "only-managed"`: uv installs and uses its own managed interpreter, not the system Python
- The `python` on PATH is not the project interpreter on the development machine (it is Inkscape's interpreter without pip); always use `uv run`

**Package Manager:**
- uv (build backend `uv_build>=0.12,<0.13`, see `[build-system]` in `pyproject.toml`)
- Lockfile: present (`uv.lock`, version 1, pins every transitive dependency with hashes)
- Setup: `uv sync`; run scripts as `uv run python <script>.py`, the console script as `uv run planspiel <command>`, tests as `uv run pytest`

**Console script:**
- `planspiel = planspiel.cli:main` (declared in `[project.scripts]` in `pyproject.toml`); also runnable as a module through `planspiel/__main__.py`

## Frameworks

**Core:**
- No application framework. The project is a config-driven batch toolchain: JSON/TOML in, enumerations, balance reports and PDFs out (no server, no database, no runtime state)
- `argparse` (stdlib) - CLI in `planspiel/cli.py` with subcommands `validate`, `texts`, `clues`, `print` (with `--check`), `gate` (with `--paths`), `tausch`, `referenzpfade`
- `jinja2==3.1.6` - template rendering of the print set in `planspiel/render.py` (`make_env`): custom LaTeX-safe delimiters (`\VAR{}`, `\BLOCK{}`, `\#{}`), `StrictUndefined`, `autoescape=False`, and `finalize=tex_escape` as the only path numbers and strings reach TeX

**Testing:**
- `pytest==9.1.1` (dev dependency group) - test runner; configured in `[tool.pytest.ini_options]` in `pyproject.toml` with `addopts = "-m 'not slow and not pdf' --strict-markers"`, `pythonpath = ["."]`
- Markers: `slow` (full enumeration), `pdf` (real LuaLaTeX builds), `balance` (design-principle checks on a chosen config)
- `pypdf==6.19.0` (dev dependency group) - reads built PDFs in the `pdf` tests (`tests/support/pdf_text.py`)

**Build/Dev:**
- LuaLaTeX via MiKTeX - compiles every PDF; driven by `planspiel/texbuild.py` (non-interactive: `--disable-installer`, `-interaction=nonstopmode`, `-halt-on-error`, closed stdin, timeouts, process-tree kill)
- `kpsewhich` (MiKTeX) - used by `texbuild.py` as preflight to find required packages before a build
- `git` - runtime dependency of `uv run planspiel print`: `planspiel/stamp.py` reads commit dates and working-tree status of the build inputs for the "Stand <date> · <hash>" stamp and the "+lokal" marker
- `uv_build` - build backend, flat layout (`module-root = ""`, `module-name = "planspiel"`)

## Key Dependencies

**Runtime (declared in `pyproject.toml`):**
- `jinja2==3.1.6` - LaTeX template rendering; pulls `markupsafe==3.0.4`
- `python-pptx==1.0.2` - reads the hand-maintained intro deck (`final_documents/Planspiel_Einführung + Grundlagen.pptx`) in `tests/test_intro_deck.py` and the inventory check; the deck generators are archived. Pulls `lxml==6.1.3`, `pillow==12.3.0`, `typing-extensions==4.16.0`, `xlsxwriter==3.2.9` (transitive, not used directly by project code)

**Dev (dependency group `dev`):**
- `pytest==9.1.1`, `pypdf==6.19.0`
- Transitive: `pluggy==1.6.0`, `iniconfig==2.3.0`, `packaging==26.3`, `pygments==2.21.0`, `colorama==0.4.6`

**External tools (not Python packages):**
- LuaLaTeX, kpsewhich and `miktex` CLI (MiKTeX) - required packages listed in `print/miktex-packages.txt`: babel, babel-german, colortbl, fontspec, geometry, graphics, pgf, tikzfill, tools, xcolor
- git - history and stamp

**Infrastructure:**
- uv (Astral) - Python version, environment and lockfile management
- No CI runner, no container, no formatter/linter configuration

## Configuration

**Environment:**
- No environment variables are read by the project code (all tooling takes `--config` and `--planspiel-content-dir` style arguments); the only env override set is `SOURCE_DATE_EPOCH=0` and `FORCE_SOURCE_DATE=1` for the LuaLaTeX subprocess (`planspiel/texbuild.py`, `run_lualatex`)
- No `.env` file is used by the project; the Claude Code hook `.claude/hooks/session-start.sh` only acts when `CLAUDE_CODE_REMOTE=true`

**Game parameters:**
- `simulation_config.json` - the single source of every number. Top-level keys: `default_budget_tier`, `base_cia`, `final_index`, `budget_tiers`, `waves`, `attacks`, `measures`, `events`, `final_events`, `practice`, `session_schedule`, `reference_plans`, `reference_strategies`
- Loaded by `planspiel/config.py` (`load_config`, `read_raw_config`) into read-only `@dataclass` types; checked by `planspiel/validate.py`

**Build:**
- `pyproject.toml` - project metadata, dependencies, pytest configuration, uv build backend
- `uv.lock` - locked dependency set
- `.python-version` - `3.12`
- `print/planspiel.sty` - LaTeX style, copied into every TeX build directory (`STATIC_FILES` in `planspiel/texbuild.py`)
- `print/miktex-packages.txt` - MiKTeX package ids for `miktex packages install --package-id-file`
- `.gitattributes` - line endings (`eol=lf`) for TOML, JSON, `.sty`, `.tex`, `.j2`; binary handling for PDFs and images; Git LFS filter declared for the large simulation dumps `simulation_results.json`, `simulation_results_high.json`, `sim_high.json`
- `.gitignore` - ignores `build/`, `.venv/`, `.pytest_cache/`, `__pycache__/`, the simulation dumps and `simulation_summary*.json`, `simulation_full*.jsonl`

## Platform Requirements

**Development:**
- Windows 11 with Git Bash (bash shell; Unix paths)
- uv (manages Python 3.12 and `.venv/`)
- MiKTeX with LuaLaTeX and `kpsewhich` on PATH, required packages from `print/miktex-packages.txt`
- git (required for `planspiel print`, also for the stamp in `--check` mode)
- Node.js is only needed for the optional GSD tooling hook (`npx -y @opengsd/gsd-core@latest`, active only when `CLAUDE_CODE_REMOTE=true`)

**Production:**
- No deployment target. The production artifact is the printed set: PDFs in `final_documents/generated/` (16 files including `manifest.json`), committed to git after a clean build (`uv run planspiel print`, verified with `uv run planspiel print --check`, which needs no TeX)

---

*Stack analysis: 2026-11-09*
