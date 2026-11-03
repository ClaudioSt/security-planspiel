# Technology Stack

**Analysis Date:** 2026-11-04

## Languages

- Python 3.12, uv-managed (`.python-version`, `python-preference = "only-managed"`): the `planspiel` package, root wrapper scripts and the tests
- LaTeX (LuaLaTeX) via Jinja2 templates in `print/templates/*.tex.j2` and `print/planspiel.sty`: the print material
- TOML: `content/texte.toml` (all prose), `content/clues.toml`, `content/digit_allowlist.toml`, `content/giveaway_terms.toml`
- JSON: `simulation_config.json` (single source of every number), `content/mhp_baseline.json` (frozen MHP-round values), `tests/golden/*.json`
- Markdown: `README.md` (German rulebook) and `.planning/` artifacts

## Runtime and package management

- `pyproject.toml` + `uv.lock`; setup `uv sync`, run everything through `uv run` (never the PATH `python`)
- Build backend `uv_build` (flat layout, `module-name = "planspiel"`); console script `planspiel = planspiel.cli:main`
- LuaLaTeX from MiKTeX; the required packages are listed in `print/miktex-packages.txt`
- `git` is a runtime dependency of `uv run planspiel print` (the stamp reads the commit date and the working-tree state of the inputs)

## Dependencies

- `jinja2==3.1.6`: strict-undefined template rendering of the print set (`planspiel/render.py`)
- `python-pptx==1.0.2`: reads the hand-maintained intro deck in tests and the inventory check; the generator scripts that wrote decks are archived
- `pytest==9.1.1` (dev group): test runner
- `pypdf==6.19.0` (dev group): inspects built PDFs in the `pdf` tests
- No Excel library any more (the calculator generator is archived)

## Commands

| Command | Purpose |
|---------|---------|
| `uv run planspiel validate` | check `simulation_config.json` (structure, hand-calculability, schedule) |
| `uv run planspiel texts` / `clues` | check `content/texte.toml` and the clue matrix |
| `uv run planspiel print` | build all PDFs into `final_documents/generated/` plus `manifest.json` |
| `uv run planspiel print --check` | verify the committed PDFs against the current inputs, no TeX run |
| `uv run planspiel gate [--paths]` | overspend gate and calibration of X |
| `uv run planspiel tausch` / `referenzpfade` | swap layer and reference game paths |
| `uv run python balance_analysis.py --layers all --paths` | full balance report over the full enumeration |
| `uv run python simulate_outcomes.py --budget-tier <tier>` | per-tier enumeration and summary |

## Testing

- `uv run pytest`: fast suite, `addopts = "-m 'not slow and not pdf' --strict-markers"`
- `uv run pytest -m pdf`: builds real PDFs with LuaLaTeX; skips when no TeX engine or package is available
- `uv run pytest -m slow`: full enumeration over all dependency-valid combinations per tier
- `uv run pytest tests -m balance`: Phase-6 design-principle checks, options `--planspiel-config` and `--planspiel-content-dir` select a candidate
- No CI runner; no formatter or linter configuration

## Configuration and generated data

- All numbers come from `simulation_config.json`; the script paths take `--config`, there are no environment variables
- `build/`, `simulation_summary_*.json`, `simulation_results*.json`, `sim_{low,med,high}.json` and `simulation_full_*.jsonl` are gitignored (large or local artifacts)
- `final_documents/generated/` is committed output of `uv run planspiel print`; `archive/` is history outside the build

## Platform requirements

- Windows 11 with bash, uv, MiKTeX (LuaLaTeX, `kpsewhich`) and git; no server, no deployment target: production is the printed set
