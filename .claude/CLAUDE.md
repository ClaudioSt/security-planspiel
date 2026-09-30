<!-- GSD:project-start source:PROJECT.md -->

## Project

**CIA-Planspiel Automotive — Post-Workshop Refinement**

An offline, paper/whiteboard IT-security business game ("CIA-Planspiel Automotive") for student teams (3 teams × 5 people, one afternoon, ~3h). Teams act as consultants for the fictional automotive supplier MechTech: they negotiate a budget, pick security measures at levels L1–L3, and face deterministic events and three attack waves, optimizing customer satisfaction (KZ), CIA goal fulfilment and Return on Security (RoS). This repo holds the game design, the central parameter config and the Python tooling for simulation, balance checks and print-material generation — not a runtime for playing the game.

This project refines the game after its live run at the MHP workshop (2026-09): fix the rule issues participants hit, make the mechanics understandable, generate all print material from `simulation_config.json`, and rebalance.

**Core Value:** Facilitators and players can run the game by hand without ambiguity: every rule is unambiguous, every printed number matches `simulation_config.json`, and no strategy exploits a rule loophole.

### Constraints

- **Hand-calculability**: all worksheet formulas stay linear and computable by hand — facilitators calculate live on paper
- **Determinism**: same inputs → same outputs within a session; no randomness in outcomes. Scenario draw between sessions is allowed (v4, SCEN) — v1 code must not hard-code "exactly one scenario"
- **Single source of truth**: every number comes from `simulation_config.json`; order of change is config → README → print material
- **Format**: 3 teams × 5, one afternoon (~3h), paper/whiteboard — unchanged
- **Language**: game content/UI German; code, commits bodies, docs English (commit subject per user convention)
- **Timeline**: no fixed next workshop date — refine at own pace
- **Workflow**: TDD for simulation changes; balance verified by full enumeration, not only `balance_analysis.py`

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages

- Markdown — the vast majority of the repo (game design, rules, facilitator scripts, printable forms; ~30 top-level `.md` files plus `docs/`)
- Python 3 — supporting scripts for simulation, balance-checking, and print-material generation (`simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`, `generate_attack_calculator.py`, `generate_from_template.py`, `generate_pptx_cards.py`)
- JSON — `simulation_config.json` (central parameter source), `sim_low.json` / `sim_med.json` (pre-generated simulation result dumps, gitignored variants also exist: `simulation_results*.json`)

## Runtime

- Python 3.12, uv-managed (`.python-version`); dependencies pinned in `pyproject.toml` and locked in `uv.lock`; setup: `uv sync`; run everything via `uv run`.
- `pyproject.toml` + `uv.lock` (uv_build, flat layout, console script `planspiel`); dev dependency pytest.

## Frameworks

- None — these are standalone scripts, not an application framework. No web framework, no CLI framework beyond stdlib `argparse`.
- None detected. No `pytest`/`unittest` test files, no test config, no CI test runner found in the repo.
- None — no bundler, linter config, formatter config, or task runner found (no `.eslintrc`, `Makefile`, `tox.ini`, etc.).

## Key Dependencies

- `openpyxl` — used in `generate_attack_calculator.py` (imports `Workbook`, `Font`, `Alignment`, `Border`, `Side`, `PatternFill`, `Protection`, `DataBarRule`, `FormulaRule`, `DataValidation`, `get_column_letter`) to programmatically build the Excel attack-damage calculator (`angriff_berechnung.xlsx`)
- `python-pptx` (import name `pptx`) — used in `generate_pptx_cards.py` (imports `Presentation`, `RGBColor`, `MSO_SHAPE`, `MSO_SHAPE_TYPE`, `PP_ALIGN`, `MSO_ANCHOR`, `Inches`, `Pt`) to generate measure/attack/event card decks as `.pptx` files
- `simulate_outcomes.py` — `argparse`, `itertools`, `json`, `dataclasses`, `typing`, `copy`
- `analyze_simulation_results.py` — `argparse`, `json`, `typing`; also does `from simulate_outcomes import (...)` (intra-repo dependency, not a package — both scripts must live in the same directory)
- `balance_analysis.py` — stdlib only (`json`, `itertools`-style enumeration logic, `dataclasses`)
- `generate_from_template.py` — uses `pathlib.Path`, `sys`, `json`, plus `python-pptx`/`openpyxl` depending on which template it targets (mixed generator script)
- Git LFS — `.gitattributes` declares `filter=lfs diff=lfs merge=lfs` for `simulation_results.json`, `simulation_results_high.json`, `sim_high.json`. Note: `sim_low.json` (14 MB) and `sim_med.json` (52 MB) are present in the working tree but are **not** listed in `.gitattributes` for LFS tracking — they are tracked as regular (large) blobs in git history as currently configured.

## Configuration

- No `.env` files or environment-variable-based configuration. All simulation parameters live in `simulation_config.json` (top-level keys: `default_budget_tier`, `base_cia`, `budget_tiers`, `waves`, `attacks`, `measures`, `events`).
- Scripts accept config path via CLI flag, not env var: `simulate_outcomes.py --config simulation_config.json` (default), `analyze_simulation_results.py --config <path>` (optional, used for RoS calculation).
- No formal build config. "Build" in this repo means running the generator scripts directly:

## Platform Requirements

- Any OS with uv installed; `uv sync` provisions Python 3.12 and all dependencies.
- `jq` recommended (per `CLAUDE.md`) for inspecting the large `sim_low.json` / `sim_med.json` files without loading them fully into an editor or Python REPL
- None — this is not a deployed application. "Production" output is the printed/exported game material in `final_documents/` (docx/pptx/pdf) used live at the tabletop session; there is no server, hosting, or runtime deployment target.

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Scope Note

- `simulate_outcomes.py` (545 lines) — deterministic outcome enumeration
- `analyze_simulation_results.py` (197 lines) — result summarization/top-N reporting
- `balance_analysis.py` (431 lines) — strategy comparison / dominance checks
- `generate_attack_calculator.py` (522 lines) — Excel calculator generation (openpyxl)
- `generate_from_template.py` (642 lines) — PPTX generation from existing templates (python-pptx)
- `generate_pptx_cards.py` (694 lines) — PPTX generation from scratch (python-pptx)

## Naming Patterns

- Lowercase snake_case, verb-first for action scripts: `simulate_outcomes.py`, `analyze_simulation_results.py`, `generate_pptx_cards.py`, `generate_attack_calculator.py`.
- `balance_analysis.py` is the one noun-first exception.
- snake_case throughout, no exceptions observed: `load_config`, `compute_cia`, `compute_e_value`, `apply_attack`, `check_event_condition`, `selection_to_key`, `run_simulation`.
- Verb-prefixed and descriptive: `compute_*`, `apply_*`, `check_*`, `load_*`, `run_*`, `format_*`, `summarize_*`.
- Every script's entry point is named `main()` and guarded by `if __name__ == "__main__":` (`simulate_outcomes.py:531-545`).
- snake_case for locals (`kz_start`, `total_damage`, `e_value`, `cia_mali`).
- Domain abbreviations used consistently and without redefinition across files: `kz` (Kundenzufriedenheit), `cia` (Confidentiality/Integrity/Availability dict with keys `c`/`i`/`a`), `e_value`/`e_threshold`/`e_divisor` (Effektivitätswert), `opex`/`init` (cost categories), `ros` (Return on Security). These map 1:1 to terms defined in `simulation_config.json` and `README.md` — do not introduce new abbreviations without adding them to the README glossary.
- Constants/lookup tables are SCREAMING_SNAKE_CASE module-level dicts: `COLORS`, `MEASURE_META` (`generate_pptx_cards.py:23-36`, `generate_from_template.py:23+`), `HEADER_FONT`, `INPUT_FILL`, `THIN_BORDER` (`generate_attack_calculator.py:16-29`).
- PascalCase, singular nouns matching domain entities from `simulation_config.json`: `Attack`, `BonusMeasure`, `Wave`, `MeasureLevel`, `Measure`, `BudgetTier`, `Event` (`simulate_outcomes.py:10-74`).
- All declared with `@dataclass`; no manual `__init__`. Optional/defaulted fields use `= 0.0` or `field(default_factory=list)` rather than mutable default arguments.

## Code Style

- No formatter config detected (no `pyproject.toml`, `.flake8`, `black`/`ruff` config files in the repo). Indentation is consistently 4 spaces; line lengths are generally kept under ~110 characters but this is not enforced by tooling — it appears to be manual discipline only.
- No linter config detected. No CI workflow runs linting (no `.github/workflows/`).
- Type hints are used for function signatures (`Dict`, `List`, `Tuple`, `Optional` from `typing`) in the simulation/analysis scripts (`simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`) but are absent from the two PPTX/Excel generator scripts, which favor large literal dict/constant blocks over typed helpers.
- Every script starts with `#!/usr/bin/env python3`.
- `balance_analysis.py` additionally declares `# -*- coding: utf-8 -*-` (needed because of German umlauts in print strings); the other scripts rely on Python 3's UTF-8 default and have no explicit encoding declaration despite also containing umlauts in string literals.

## Import Organization

## Config-Driven Design Pattern (the core convention)

- `simulation_config.json` is the **only** source of numeric game-balance values (budgets, severities, weights, costs, thresholds, event effects).
- Every script that touches game numbers loads this file at runtime via `load_config()` / `json.loads(path.read_text())` and converts it into typed dataclasses (`simulate_outcomes.py:77-163`) or plain dicts (`generate_attack_calculator.py:14-18`, `generate_pptx_cards.py`/`generate_from_template.py` load `MEASURE_META` for descriptive text only, not numbers).
- **Rule enforced by `CLAUDE.md`:** no fixed numeric value may be introduced into prose Markdown documents (README, card decks, parameter tables, calculation worksheets) without that same value existing in `simulation_config.json`. Documentation and config must never drift apart. When changing a number, change `simulation_config.json` first, then propagate to `README.md` and any affected card/form documents.
- Formulas themselves (e.g., `M_sum = min(MIT_CAP, ΣLevel-Mitigations)`, `G = max(0, baseSeverity + ΣeventSeverityMods − M_sum)`, `E = C*wC + I*wI + A*wA`, RoS formula) are fixed in code/`README.md` — only the operands are configurable, never the formula shape.
- Descriptive/narrative content (measure names, focus descriptions, level explanations in `MEASURE_META`) is hardcoded in the generator scripts (`generate_pptx_cards.py`, `generate_from_template.py`) because it is prose, not a balance number — this is consistent with the "no numbers in prose without config sync" rule, which targets quantities, not descriptive text.

## Comment Style

- Present in the generator and balance scripts, absent in `simulate_outcomes.py` and `analyze_simulation_results.py`.
- When present, written in German, describing purpose and sometimes important caveats in capitals, e.g. `WICHTIG: Zusätzliche Boni werden NICHT angezeigt (nur Basis-Mitigationswerte)` (`generate_pptx_cards.py:10`, `generate_from_template.py:13`).
- Inconsistent: some functions have triple-quoted docstrings describing return tuples (`compute_mitigation_from_e_value`, `apply_attack`, `apply_events` in `simulate_outcomes.py:209-352`), most do not (e.g. `compute_cia`, `compute_costs`, `load_config` have no docstring, relying on type hints and naming).
- Where present, docstrings use a lightweight "Returns:" block style rather than full Google/NumPy docstring format.
- Used sparingly to mark logical sections within long functions, e.g. `# Check E-Target`, `# Apply attack damage to KZ`, `# Apply events`, `# Clamp KZ` inside `simulate_selection` (`simulate_outcomes.py:383-400`).
- `balance_analysis.py` uses inline comments to annotate manually verified cost totals next to each `Strategy` definition, e.g. `# 26+36+34+46+16+32=190` (`balance_analysis.py:43`) — these are load-bearing sanity checks against `simulation_config.json` values and must be updated if measure costs change.

## Language Mixing (German/English)

- **Code identifiers (functions, variables, classes): English.** `compute_cia`, `apply_attack`, `BudgetTier`, `kz_delta` (despite `kz` itself being a German-origin abbreviation for Kundenzufriedenheit, it is treated as a domain term, not translated).
- **CLI help text, docstrings, print/report output: German**, matching the target audience (German-speaking students/facilitators) — e.g. `parser.add_argument("--budget-tier", ..., help="Budget tier name (low|medium|high).")` is in English in `simulate_outcomes.py:518`, but `balance_analysis.py` print statements (`"BALANCE-ANALYSE: Security-Planspiel"`, `"BUDGET-TIER: ..."`) are entirely in German.
- **No fixed rule enforced by tooling** — the split is pragmatic: code stays in English (as is conventional for Python), anything user/facilitator-facing (docstrings explaining intent, console output, error-adjacent messaging) is German. Follow this split when adding new scripts: keep identifiers English, keep human-readable output German.
- `MEASURE_META` dict content (focus/description/levels_desc) is German prose describing measures for non-technical players — this mirrors the corresponding German Markdown documents (`MASSNAHMENKARTEN.md`) and must stay consistent with them.

## Documentation Conventions (the cross-cutting rule)

- **Numbers-in-sync rule:** Any concrete number appearing in prose (e.g., a budget figure, a severity value, an E-target threshold, a cost) must also exist in `simulation_config.json`. If you change a number in a `.md` file, you must change it in `simulation_config.json` too (and vice versa) — never let one drift from the other.
- **Order of changes:** `simulation_config.json` → `README.md` (if a formula/rule changed) → affected card/form documents (`MASSNAHMENKARTEN.md`, `ANGRIFFSKARTEN.md`, `PARAMETER_TABELLE.md`, `BERECHNUNGSBOGEN_WELLE*.md`, etc.).
- **Verification step after content changes:** run `simulate_outcomes.py` then `balance_analysis.py` to confirm no dominant strategy or numeric inconsistency was introduced before regenerating any print material.
- The `.md` documents are the actual game-design product; editing them is content/editorial work, not refactoring, but the numeric-sync discipline still applies as if it were code.
- Generated binary outputs (`final_documents/*.docx,.pptx,.pdf`, `pptx_output/*.pptx`) must never be hand-edited — only regenerated via the generator scripts or their source templates.

## Function Design

## Module Design

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## System Overview

```text

```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Game rules / formulas (source of truth) | Defines state machine, all formulas (M_sum, G, E, RoS) | `README.md` |
| Central numeric configuration | Single source for budget tiers, waves, attacks, measures, events, base CIA | `simulation_config.json` |
| Outcome enumerator | Deterministically enumerates all valid measure-level combinations and their resulting KZ/damage/CIA/cost | `simulate_outcomes.py` |
| Result analyzer | Loads enumerated results, ranks by Final-Index (weighted KZ + RoS) | `analyze_simulation_results.py` |
| Balance checker | Defines named "strategies" (e.g. all-L3, cheap-only) and compares their outcomes to detect dominant/broken strategies; reuses `simulate_outcomes.py` internals via direct import | `balance_analysis.py` |
| Excel attack calculator generator | Builds `angriff_berechnung.xlsx`-style worksheets from config, for paper-free wave calculation | `generate_attack_calculator.py` |
| PPTX template filler | Loads a PowerPoint template and find/replaces placeholder text (CIA values, costs, dependencies) per measure/event slide | `generate_from_template.py` |
| PPTX deck builder (from scratch) | Programmatically builds measure-card and event-card slide decks using `python-pptx` shapes | `generate_pptx_cards.py` |
| Pre-computed result caches | Large (10–50 MB) JSON dumps of `simulate_outcomes.py` runs for the low/medium budget tiers, used by analysis/balance scripts without recomputation | `sim_low.json`, `sim_med.json` |

## Pattern Overview

- No persistence layer beyond flat JSON files (`simulation_config.json` as input, `sim_low.json`/`sim_med.json` as cached output)
- No concurrency, no networking, no users/sessions — every script is a single-process batch job invoked via `argparse` from the command line
- Determinism is the central design constraint: the same config + same measure selection must always produce the same numbers, both in the live game (by hand) and in the simulation scripts (in code). There is deliberate duplication of formula logic between `README.md` (human-readable spec) and `simulate_outcomes.py` (executable spec) — keeping these two in sync is a documented project convention (see `CLAUDE.md`)
- The Python scripts are siblings, not a layered application: `balance_analysis.py` is the only script with an internal code dependency, importing functions directly from `simulate_outcomes.py` (see `balance_analysis.py:15`)

## Layers

- Purpose: Define all tunable numbers for the game
- Location: `simulation_config.json`
- Contains: `default_budget_tier`, `base_cia`, `budget_tiers`, `waves`, `attacks`, `measures`, `events`
- Used by: every Python script below
- Purpose: Compute every legal outcome deterministically
- Location: `simulate_outcomes.py`
- Depends on: `simulation_config.json` (loaded via `load_config()`, `simulate_outcomes.py:77`)
- Used by: `balance_analysis.py` (direct import), manually piped into `analyze_simulation_results.py` via JSON file
- Purpose: Rank outcomes, detect dominant strategies, sanity-check balance
- Location: `analyze_simulation_results.py`, `balance_analysis.py`
- Depends on: simulation result JSON (either freshly generated or `sim_low.json`/`sim_med.json`)
- Used by: human game designer, before content/print finalization
- Purpose: Turn config/content into printable or presentable artifacts
- Location: `generate_attack_calculator.py`, `generate_from_template.py`, `generate_pptx_cards.py`
- Depends on: `simulation_config.json` plus existing `.pptx` templates (for `generate_from_template.py`)
- Produces: files in `pptx_output/`, source material for `final_documents/`
- Purpose: Actual game execution
- Location: Printed Markdown forms (`FORMULARE.md`, `BERECHNUNGSBOGEN_WELLE*.md`, `TEAM_TRACKING_BOGEN.md`) and `final_documents/`
- Depends on: nothing computational at runtime — facilitator applies the formulas from `README.md` by hand

## Data Flow

### Primary Content-Validation Path

### Print Material Generation Path

## Key Abstractions

- Purpose: Represents a security control selectable at level 0-3 (L1/L2/L3), with `costInit`, `costOpex`, `cia={c,i,a}`, `mitigations`, `eventEffects`, `dependencies`
- Examples: `simulate_outcomes.py` `Measure` dataclass; content described in `MASSNAHMENKARTEN.md`; raw data in `simulation_config.json` under `measures`
- Pattern: Plain dataclass loaded straight from JSON, no inheritance/polymorphism
- Purpose: One round of play with CIA weights (`wC`, `wI`, `wA`), an E-target threshold, and a set of attacks
- Examples: `simulation_config.json` under `waves`; described conceptually in `README.md` ("Wellen‑Ziel (E‑Wert) & Scoring")
- Purpose: A deterministic threat event with `baseSeverity`, `sUnit`, `kzUnit`, `ciaImpactPerStep`, and references to measures that mitigate it
- Examples: `simulation_config.json` under `attacks`; applied via `apply_attack` (`simulate_outcomes.py:237`); described in `ANGRIFFSKARTEN.md`
- Purpose: Rule-based trigger (time/discovery-signal/measure-presence condition) with deterministic effects (`budgetDelta`, `kzDelta`, `severityMod`, `kzFactor`, `damageFactor`, `opexPenalty`)
- Examples: `simulation_config.json` under `events`; checked via `check_event_condition` (`simulate_outcomes.py:288`) and applied via `apply_events` (`simulate_outcomes.py:313`)
- Purpose: A hand-authored, named measure-selection used solely to probe for dominance/imbalance — not a concept that exists in the game itself
- Examples: `define_strategies` (`balance_analysis.py:28`)

## Entry Points

- Location: `simulate_outcomes.py`
- Triggers: Manual invocation by game designer, e.g. `python3 simulate_outcomes.py --config simulation_config.json --budget-tier medium --output simulation_results.json`
- Responsibilities: Full deterministic enumeration of outcomes; argument parsing in `parse_args()` (line 515), orchestration in `main()` (line 531)
- Location: `analyze_simulation_results.py`
- Triggers: Manual invocation after `simulate_outcomes.py` has produced a results file
- Responsibilities: Ranking/summarizing outcomes by weighted Final-Index
- Location: `balance_analysis.py`
- Triggers: Manual invocation, no arguments required (`run_analysis()`, line 280)
- Responsibilities: Strategy-vs-strategy comparison, dominance detection
- Location: project root
- Triggers: Manual invocation when print material needs regenerating after content changes
- Responsibilities: Produce `.xlsx`/`.pptx` artifacts into `pptx_output/`

## Architectural Constraints

- **Threading:** None. Every script is single-threaded, synchronous, batch-style.
- **Global state:** None beyond normal Python module-level constants (e.g. `MIT_CAP` style caps loaded from config at call time). No singletons, no shared mutable state across script invocations — each run reads `simulation_config.json` fresh.
- **Circular imports:** None observed. `balance_analysis.py` imports from `simulate_outcomes.py` (one-directional); no other script imports another.
- **Combinatorial explosion:** `simulate_outcomes.py` enumerates the full cross-product of measure-level selections, which is why `sim_low.json` is ~14 MB and `sim_med.json` is ~52 MB. Both files are explicitly flagged in `CLAUDE.md` as too large to read in full — must be parsed with `jq`/targeted Python rather than loaded wholesale.
- **No runtime/production environment:** There is no deployment target, no server process, no persistent service. "Production" for this project means the printed contents of `final_documents/` used at the live game session.

## Anti-Patterns

### Treating this as a software application

### Editing generated/binary output directly

### Letting prose documentation and config drift apart

## Error Handling

- Config loading functions (`load_config` in `simulate_outcomes.py:77`, `load_config` in `generate_from_template.py:197`, `load_config` in `generate_pptx_cards.py:203`) assume well-formed JSON and will raise on malformed input rather than validating gracefully
- Dependency/condition checks (`dependencies_satisfied`, `check_event_condition`) return booleans used to skip invalid combinations rather than raising — invalid measure combinations are filtered out of the enumeration, not flagged as errors

## Cross-Cutting Concerns

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
