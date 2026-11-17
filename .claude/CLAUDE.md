<!-- GSD:project-start source:PROJECT.md -->

## Project

**CIA-Planspiel Automotive — Post-Workshop Refinement**

An offline, paper-only IT-security business game ("CIA-Planspiel Automotive") for student teams (3 teams × 5 people, one afternoon, ~3h). Teams act as consultants for the fictional automotive supplier MechTech: they negotiate a budget, pick security measures at levels L1–L3, and face deterministic events and three attack waves, optimizing customer satisfaction (KZ), CIA goal fulfilment and Return on Security (RoS). This repo holds the game design, the central parameter config and the Python tooling for simulation, balance checks and print-material generation — not a runtime for playing the game.

This project refines the game after its live run at the MHP workshop (2026-09): fix the rule issues participants hit, make the mechanics understandable, generate all print material from `simulation_config.json`, and rebalance.

**Core Value:** Facilitators and players can run the game by hand without ambiguity: every rule is unambiguous, every printed number matches `simulation_config.json`, and no strategy exploits a rule loophole.

### Constraints

- **Hand-calculability**: all worksheet formulas stay linear and computable by hand — facilitators calculate live on paper
- **Determinism**: same inputs → same outputs within a session; no randomness in outcomes. Scenario draw between sessions is allowed (v4, SCEN) — v1 code must not hard-code "exactly one scenario"
- **Single source of truth**: every number comes from `simulation_config.json`; order of change is config → README → print material
- **Format**: 3 teams × 5, one afternoon (~3h), paper only — unchanged
- **Language**: game content/UI German; code, commits bodies, docs English (commit subject per user convention)
- **Timeline**: no fixed next workshop date — refine at own pace
- **Workflow**: TDD for simulation changes; balance verified by full enumeration, not only `balance_analysis.py`

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

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

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Single sources

- Numbers live only in `simulation_config.json`; prose lives only in `content/texte.toml`. Order of a content change: `simulation_config.json` -> `README.md` -> `content/texte.toml` -> `uv run planspiel print` -> `uv run planspiel print --check` -> commit `final_documents/generated/`
- The validator rejects prose in the config (`schema.prose_in_config`); the digit lint rejects digits in prose unless the exact digit string is in `content/digit_allowlist.toml`
- Game formulas have exactly one definition, in `planspiel/rules.py` (guarded by `tests/test_single_definition.py`); the root wrappers, enumeration, balance code and print models call it and never re-implement it
- Formulas stay fixed and linear (hand-calculable on the worksheets); only operands are configurable

## Arithmetic and rounding

- Exact arithmetic with `fractions.Fraction` or integer scaling for E-Wert, Gesamtreduktion, reduction over threshold and severity; damage stays exact in whole euros
- The KZ change of a wave (attack plus events) is rounded once, half away from zero (`planspiel.rounding.round_half_away`), then KZ is clamped to 0-100; the built-in `round()` is forbidden in `planspiel/rules.py` and `planspiel/rounding.py`
- RoS2 (RoS to two decimals) goes through `rules.ros_two_decimals`; the Final-Index is `weight_kz * KZ + weight_ros * RoS2`

## Print model rules

- Print models (`planspiel/printmodel.py`, `cards.py`, `booklet.py`, `wave_page.py`, `story.py`, `practice.py`, `master.py`, `schedule.py`, `debrief.py`, `was_neu.py`, `probelauf.py`) hold finished strings; templates only loop and place, they never format numbers
- Numbers reach TeX only as strings built in code; `render.tex_escape` is the Jinja `finalize` hook and rejects raw numbers and undefined names
- Every print job name carries an audience prefix (`spieler-`, `uebung-`, `angriff-`, `spielleitung-`, see `planspiel/audience.py`); an unclassified job is a build error
- Veil: player-facing pages never name an attack before its wave and never print a real wave's weights or bonus links (`planspiel/veil.py`, `content/giveaway_terms.toml`); story documents carry clues from `content/clues.toml`, never a named gap
- Every PDF carries the stamp "Stand <date> · <hash>", ending in "+lokal" for a dirty build; only a clean, committed build is committed (`planspiel/stamp.py`)
- Generated PDFs in `final_documents/generated/` are never edited by hand; `archive/` is never read by the build (`tests/test_no_archive_references.py`)

## Naming and language

- snake_case modules, functions and variables; verb-first function names (`compute_*`, `build_*`, `check_*`, `load_*`); PascalCase dataclasses and NamedTuples named after domain entities (`Wave`, `Attack`, `Measure`, `Config`)
- Domain abbreviations are used unexplained and must not be extended without a README glossary entry: `kz`, `cia`, `e_value`, `e_threshold`, `opex`, `init`, `ros`
- Code identifiers, docs and commit messages are English; all game content, print output, CLI output and test-facing messages for the facilitator are German
- Commit messages follow conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, with a phase-plan scope such as `(07-11)`)

## Testing

- TDD for rules and simulation changes: write the failing test first, commit RED, then GREEN
- pytest markers: `slow` (full enumeration), `pdf` (real LuaLaTeX builds), `balance` (design-principle checks on a chosen config); the fast suite excludes `slow` and `pdf`
- Tests use the real code and real config, no mocks for the rules; golden files in `tests/golden/` pin reference outputs
- Balance is verified by full enumeration, not by hand-picked strategies; `uv run planspiel gate` guards that overspending never pays off

## Module and comment style

- Type hints on function signatures, with builtin generics such as `tuple[str, ...]`
- Module docstrings state the requirement ID and decision IDs they implement (for example `BAL-06 (D-16)`); inline comments explain why, in German or English
- Config dataclasses are plain `@dataclass` and treated as read-only after loading; pure functions over the result store and config are preferred to stateful classes
- No linter or formatter configuration; 4-space indentation, lines kept near 110 characters by discipline

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

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

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
