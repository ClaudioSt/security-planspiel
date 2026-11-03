# Architecture

**Analysis Date:** 2026-11-04

## Pattern Overview

- Config-driven batch tooling: `simulation_config.json` and `content/` go in, enumerations, balance reports and stamped PDFs come out; there is no server, no persistence and no state between runs
- Determinism is the central constraint: same config and same decisions give the same numbers, in code and by hand on the worksheets
- One definition of the rules (`planspiel/rules.py`) feeds the enumeration, the balance checks and every printed value, so worksheets, cards and simulation cannot drift
- The package is layered; layers import downward only, the root scripts are thin wrappers

## Layers

| Layer | Modules | Responsibility |
|-------|---------|----------------|
| Config | `simulation_config.json`, `planspiel/config.py`, `planspiel/validate.py` | load into typed dataclasses, validate structure, hand-calculability and schedule |
| Content | `content/texte.toml`, `clues.toml`, `digit_allowlist.toml`, `giveaway_terms.toml`, `planspiel/texts.py` | load prose, digit lint, giveaway lint, clue matrix |
| Rules | `planspiel/rules.py`, `rounding.py`, `fmt.py`, `review_text.py`, `eventtext.py` | exact formulas, paper rounding, budget review, Kurswechsel, number and text formatting |
| Enumeration | `planspiel/enumerate.py`, `simulate.py`, `parallel.py`, `refpaths.py`, `choices.py` | all dependency-valid measure selections, swap layer, game paths |
| Balance | `planspiel/gate.py`, `balance.py`, `strategies.py`, `rewarding.py`, `spread.py`, `index_weights.py`, `report.py`, `analyze.py` | overspend gate, design-principle checks, Final-Index weight, reports |
| Print models | `planspiel/printmodel.py`, `cards.py`, `booklet.py`, `wave_page.py`, `story.py`, `practice.py`, `master.py`, `schedule.py`, `debrief.py`, `was_neu.py`, `probelauf.py` | build the finished strings of each document |
| Print pipeline | `planspiel/render.py`, `veil.py`, `audience.py`, `texbuild.py`, `stamp.py`, `print/templates/`, `print/planspiel.sty` | Jinja2 render, veil scan, LuaLaTeX build, stamp and manifest, freshness check |
| Entry points | `planspiel/cli.py` (`planspiel` console script), `simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py` | argparse commands and wrappers |

## Data Flow

- Print path: `simulation_config.json` + `content/texte.toml` -> `config.load_config` and `validate` / `texts` checks -> rules and enumeration for derived values (answer keys, reference paths, key figures) -> print models -> Jinja2 templates (`render.render_all`) -> veil scan per audience -> `texbuild` runs LuaLaTeX -> `stamp` adds "Stand <date> · <hash>" and writes `manifest.json` -> PDFs in `final_documents/generated/`
- Freshness path: `uv run planspiel print --check` recomputes the rendered TeX and the stamp hash without TeX and compares them with `manifest.json`; exit 0 current, 1 stale, 2 environment problem
- Balance path: config -> full enumeration per budget tier (static layer, swap layer, game paths) -> `report` summaries -> `balance`, `gate`, `strategies`, `rewarding`, `spread` -> `balance_analysis.py` report with verdicts; `pytest -m slow` and `-m balance` run the same checks as tests
- The MHP baseline `content/mhp_baseline.json` is read only by `was_neu.py` for the Was-ist-neu sheet; nothing else may import it
- `archive/` (history, legacy generators, superseded MHP print material) is outside every data flow

## Key Abstractions

- `Config` and its dataclasses (`Wave`, `Attack`, `Measure`, `BudgetTier`, `Event`) mirror `simulation_config.json` one to one
- Print models: one model object per document, holding finished strings and fill lines; templates contain only layout and loops
- Print job: a named document (`spieler-teamheft`, `angriff-1_ransomware`, `spielleitung-uebersicht`, ...) registered in `render.py` with an audience prefix that selects its veil profile
- Stamp: content hash of the rendered TeX plus style, date of the last commit on the data inputs, "+lokal" for local changes
- Reference plans and strategies: approved example paths and named strategies in the config, the basis of the answer keys and the balance checks

## Entry Points

- `uv run planspiel <validate|texts|clues|print|gate|tausch|referenzpfade>`: the main interface; `print --check` is the freshness gate before every commit that touches an input
- `uv run python simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`: wrappers around the package for per-tier enumeration, ranking and the full balance report
- `uv run pytest` with the markers `slow`, `pdf` and `balance` verifies all of the above

## Constraints

- No global mutable state; every run reads the config fresh; parallelism only inside enumeration (`--jobs`, `planspiel/parallel.py`)
- Full enumerations are large; dumps are gitignored and parsed selectively
- The build needs git history (stamp) and a TeX engine; `print --check` needs only git
- Formulas stay linear so facilitators can recompute the worksheets by hand
