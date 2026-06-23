# Technology Stack

**Analysis Date:** 2026-06-23

## Languages

**Primary:**
- Markdown — the vast majority of the repo (game design, rules, facilitator scripts, printable forms; ~30 top-level `.md` files plus `docs/`)
- Python 3 — supporting scripts for simulation, balance-checking, and print-material generation (`simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`, `generate_attack_calculator.py`, `generate_from_template.py`, `generate_pptx_cards.py`)

**Secondary:**
- JSON — `simulation_config.json` (central parameter source), `sim_low.json` / `sim_med.json` (pre-generated simulation result dumps, gitignored variants also exist: `simulation_results*.json`)

## Runtime

**Environment:**
- Python 3.11 (verified via `python3 --version` → 3.11.15 in this environment; all scripts use `#!/usr/bin/env python3` and only rely on the standard library plus two third-party packages, so any modern Python 3.9+ should work, no version pin exists in the repo)

**Package Manager:**
- None present. There is no `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`, or `environment.yml` anywhere in the repo.
- No lockfile of any kind — third-party dependencies are unpinned and undocumented; they must be inferred from `import` statements.
- This means dependency installation is currently manual/tribal knowledge (`pip install openpyxl python-pptx`) — not enforced or reproducible from the repo alone.

## Frameworks

**Core:**
- None — these are standalone scripts, not an application framework. No web framework, no CLI framework beyond stdlib `argparse`.

**Testing:**
- None detected. No `pytest`/`unittest` test files, no test config, no CI test runner found in the repo.

**Build/Dev:**
- None — no bundler, linter config, formatter config, or task runner found (no `.eslintrc`, `Makefile`, `tox.ini`, etc.).

## Key Dependencies

**Critical (third-party, inferred from imports, not installed in this analysis environment — `pip show` returned "not found"):**
- `openpyxl` — used in `generate_attack_calculator.py` (imports `Workbook`, `Font`, `Alignment`, `Border`, `Side`, `PatternFill`, `Protection`, `DataBarRule`, `FormulaRule`, `DataValidation`, `get_column_letter`) to programmatically build the Excel attack-damage calculator (`angriff_berechnung.xlsx`)
- `python-pptx` (import name `pptx`) — used in `generate_pptx_cards.py` (imports `Presentation`, `RGBColor`, `MSO_SHAPE`, `MSO_SHAPE_TYPE`, `PP_ALIGN`, `MSO_ANCHOR`, `Inches`, `Pt`) to generate measure/attack/event card decks as `.pptx` files

**Standard library only (no third-party deps):**
- `simulate_outcomes.py` — `argparse`, `itertools`, `json`, `dataclasses`, `typing`, `copy`
- `analyze_simulation_results.py` — `argparse`, `json`, `typing`; also does `from simulate_outcomes import (...)` (intra-repo dependency, not a package — both scripts must live in the same directory)
- `balance_analysis.py` — stdlib only (`json`, `itertools`-style enumeration logic, `dataclasses`)
- `generate_from_template.py` — uses `pathlib.Path`, `sys`, `json`, plus `python-pptx`/`openpyxl` depending on which template it targets (mixed generator script)

**Infrastructure:**
- Git LFS — `.gitattributes` declares `filter=lfs diff=lfs merge=lfs` for `simulation_results.json`, `simulation_results_high.json`, `sim_high.json`. Note: `sim_low.json` (14 MB) and `sim_med.json` (52 MB) are present in the working tree but are **not** listed in `.gitattributes` for LFS tracking — they are tracked as regular (large) blobs in git history as currently configured.

## Configuration

**Environment:**
- No `.env` files or environment-variable-based configuration. All simulation parameters live in `simulation_config.json` (top-level keys: `default_budget_tier`, `base_cia`, `budget_tiers`, `waves`, `attacks`, `measures`, `events`).
- Scripts accept config path via CLI flag, not env var: `simulate_outcomes.py --config simulation_config.json` (default), `analyze_simulation_results.py --config <path>` (optional, used for RoS calculation).

**Build:**
- No formal build config. "Build" in this repo means running the generator scripts directly:
  - `simulate_outcomes.py` → writes `simulation_results*.json` (gitignored variants) or one of the checked-in `sim_low.json` / `sim_med.json`
  - `generate_pptx_cards.py` → writes into `pptx_output/` (hardcoded as `Path(__file__).parent / "pptx_output"`)
  - `generate_attack_calculator.py` → writes `angriff_berechnung.xlsx`
  - `generate_from_template.py` → mixed-purpose generator producing docx/pptx output, presumably feeding `final_documents/`

## Platform Requirements

**Development:**
- Any OS with Python 3.9+ installed plus `pip install openpyxl python-pptx` run manually (no automated dependency bootstrap exists)
- `jq` recommended (per `CLAUDE.md`) for inspecting the large `sim_low.json` / `sim_med.json` files without loading them fully into an editor or Python REPL

**Production:**
- None — this is not a deployed application. "Production" output is the printed/exported game material in `final_documents/` (docx/pptx/pdf) used live at the tabletop session; there is no server, hosting, or runtime deployment target.

---

*Stack analysis: 2026-06-23*
