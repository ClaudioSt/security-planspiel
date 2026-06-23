# Coding Conventions

**Analysis Date:** 2026-06-23

## Scope Note

This repository is primarily a Markdown game-design document set (rules, cards, facilitator scripts, printable forms). Python exists only as a small set of standalone support scripts for simulation, balance analysis, and print-material generation:

- `simulate_outcomes.py` (545 lines) — deterministic outcome enumeration
- `analyze_simulation_results.py` (197 lines) — result summarization/top-N reporting
- `balance_analysis.py` (431 lines) — strategy comparison / dominance checks
- `generate_attack_calculator.py` (522 lines) — Excel calculator generation (openpyxl)
- `generate_from_template.py` (642 lines) — PPTX generation from existing templates (python-pptx)
- `generate_pptx_cards.py` (694 lines) — PPTX generation from scratch (python-pptx)

There is no application framework, no package structure (`src/`, `__init__.py`), no build tool, and no shared internal library — each script is self-contained and runnable directly via `python3 <script>.py`. Conventions below describe the actual, observed style across these six files, not an idealized standard.

## Naming Patterns

**Files:**
- Lowercase snake_case, verb-first for action scripts: `simulate_outcomes.py`, `analyze_simulation_results.py`, `generate_pptx_cards.py`, `generate_attack_calculator.py`.
- `balance_analysis.py` is the one noun-first exception.

**Functions:**
- snake_case throughout, no exceptions observed: `load_config`, `compute_cia`, `compute_e_value`, `apply_attack`, `check_event_condition`, `selection_to_key`, `run_simulation`.
- Verb-prefixed and descriptive: `compute_*`, `apply_*`, `check_*`, `load_*`, `run_*`, `format_*`, `summarize_*`.
- Every script's entry point is named `main()` and guarded by `if __name__ == "__main__":` (`simulate_outcomes.py:531-545`).

**Variables:**
- snake_case for locals (`kz_start`, `total_damage`, `e_value`, `cia_mali`).
- Domain abbreviations used consistently and without redefinition across files: `kz` (Kundenzufriedenheit), `cia` (Confidentiality/Integrity/Availability dict with keys `c`/`i`/`a`), `e_value`/`e_threshold` (Effektivitätswert and its fixed per-wave threshold), `mitigation_cap` (width of the linear interpolation zone above `e_threshold`), `kz_at_full_damage`/`kz_at_full_mitigation` (KZ endpoints used to interpolate `kz_delta`), `opex`/`init` (cost categories), `ros` (Return on Security). These map 1:1 to terms defined in `simulation_config.json` and `README.md` — do not introduce new abbreviations without adding them to the README glossary.
- Constants/lookup tables are SCREAMING_SNAKE_CASE module-level dicts: `COLORS`, `MEASURE_META` (`generate_pptx_cards.py:23-36`, `generate_from_template.py:23+`), `HEADER_FONT`, `INPUT_FILL`, `THIN_BORDER` (`generate_attack_calculator.py:16-29`).

**Types (dataclasses):**
- PascalCase, singular nouns matching domain entities from `simulation_config.json`: `Attack`, `BonusMeasure`, `Wave`, `MeasureLevel`, `Measure`, `BudgetTier`, `Event` (`simulate_outcomes.py:10-74`).
- All declared with `@dataclass`; no manual `__init__`. Optional/defaulted fields use `= 0.0` or `field(default_factory=list)` rather than mutable default arguments.

## Code Style

**Formatting:**
- No formatter config detected (no `pyproject.toml`, `.flake8`, `black`/`ruff` config files in the repo). Indentation is consistently 4 spaces; line lengths are generally kept under ~110 characters but this is not enforced by tooling — it appears to be manual discipline only.

**Linting:**
- No linter config detected. No CI workflow runs linting (no `.github/workflows/`).
- Type hints are used for function signatures (`Dict`, `List`, `Tuple`, `Optional` from `typing`) in the simulation/analysis scripts (`simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`) but are absent from the two PPTX/Excel generator scripts, which favor large literal dict/constant blocks over typed helpers.

**Shebang & encoding:**
- Every script starts with `#!/usr/bin/env python3`.
- `balance_analysis.py` additionally declares `# -*- coding: utf-8 -*-` (needed because of German umlauts in print strings); the other scripts rely on Python 3's UTF-8 default and have no explicit encoding declaration despite also containing umlauts in string literals.

## Import Organization

**Order observed (not enforced by tooling, but consistent):**
1. Standard library (`argparse`, `itertools`, `json`, `sys`, `pathlib.Path`, `dataclasses`, `typing`)
2. Third-party (`openpyxl.*`, `pptx.*`)
3. Local/sibling module imports, via explicit `sys.path.insert(0, str(Path(__file__).parent))` followed by `from simulate_outcomes import (...)` — see `balance_analysis.py:14-18`. This is the only cross-script import in the repo; there is no installed package, so this `sys.path` hack is required for `balance_analysis.py` to reuse `simulate_outcomes.py`'s functions.

**Path aliases:** None. No `src/` layout, no `__init__.py`, no namespace packages.

## Config-Driven Design Pattern (the core convention)

This is the single most important pattern in the codebase and the one most likely to be violated by careless changes:

- `simulation_config.json` is the **only** source of numeric game-balance values (budgets, severities, weights, costs, thresholds, event effects).
- Every script that touches game numbers loads this file at runtime via `load_config()` / `json.loads(path.read_text())` and converts it into typed dataclasses (`simulate_outcomes.py:77-163`) or plain dicts (`generate_attack_calculator.py:14-18`, `generate_pptx_cards.py`/`generate_from_template.py` load `MEASURE_META` for descriptive text only, not numbers).
- **Rule enforced by `CLAUDE.md`:** no fixed numeric value may be introduced into prose Markdown documents (README, card decks, parameter tables, calculation worksheets) without that same value existing in `simulation_config.json`. Documentation and config must never drift apart. When changing a number, change `simulation_config.json` first, then propagate to `README.md` and any affected card/form documents.
- Formulas themselves (e.g., `M_sum = min(MIT_CAP, ΣLevel-Mitigations)`, `G = max(0, baseSeverity + ΣeventSeverityMods − M_sum)`, `E = C*wC + I*wI + A*wA`, RoS formula) are fixed in code/`README.md` — only the operands are configurable, never the formula shape.
- Descriptive/narrative content (measure names, focus descriptions, level explanations in `MEASURE_META`) is hardcoded in the generator scripts (`generate_pptx_cards.py`, `generate_from_template.py`) because it is prose, not a balance number — this is consistent with the "no numbers in prose without config sync" rule, which targets quantities, not descriptive text.

## Comment Style

**Module docstrings:**
- Present in the generator and balance scripts, absent in `simulate_outcomes.py` and `analyze_simulation_results.py`.
- When present, written in German, describing purpose and sometimes important caveats in capitals, e.g. `WICHTIG: Zusätzliche Boni werden NICHT angezeigt (nur Basis-Mitigationswerte)` (`generate_pptx_cards.py:10`, `generate_from_template.py:13`).

**Function docstrings:**
- Inconsistent: some functions have triple-quoted docstrings describing return tuples (`compute_mitigation_from_e_value`, `apply_attack`, `apply_events` in `simulate_outcomes.py:209-352`), most do not (e.g. `compute_cia`, `compute_costs`, `load_config` have no docstring, relying on type hints and naming).
- Where present, docstrings use a lightweight "Returns:" block style rather than full Google/NumPy docstring format.

**Inline comments:**
- Used sparingly to mark logical sections within long functions, e.g. `# Check E-Target`, `# Apply attack damage to KZ`, `# Apply events`, `# Clamp KZ` inside `simulate_selection` (`simulate_outcomes.py:383-400`).
- `balance_analysis.py` uses inline comments to annotate manually verified cost totals next to each `Strategy` definition, e.g. `# 26+36+34+46+16+32=190` (`balance_analysis.py:43`) — these are load-bearing sanity checks against `simulation_config.json` values and must be updated if measure costs change.

## Language Mixing (German/English)

- **Code identifiers (functions, variables, classes): English.** `compute_cia`, `apply_attack`, `BudgetTier`, `kz_delta` (despite `kz` itself being a German-origin abbreviation for Kundenzufriedenheit, it is treated as a domain term, not translated).
- **CLI help text, docstrings, print/report output: German**, matching the target audience (German-speaking students/facilitators) — e.g. `parser.add_argument("--budget-tier", ..., help="Budget tier name (low|medium|high).")` is in English in `simulate_outcomes.py:518`, but `balance_analysis.py` print statements (`"BALANCE-ANALYSE: Security-Planspiel"`, `"BUDGET-TIER: ..."`) are entirely in German.
- **No fixed rule enforced by tooling** — the split is pragmatic: code stays in English (as is conventional for Python), anything user/facilitator-facing (docstrings explaining intent, console output, error-adjacent messaging) is German. Follow this split when adding new scripts: keep identifiers English, keep human-readable output German.
- `MEASURE_META` dict content (focus/description/levels_desc) is German prose describing measures for non-technical players — this mirrors the corresponding German Markdown documents (`MASSNAHMENKARTEN.md`) and must stay consistent with them.

## Documentation Conventions (the cross-cutting rule)

This applies to the Markdown game-design documents, not just code:

- **Numbers-in-sync rule:** Any concrete number appearing in prose (e.g., a budget figure, a severity value, an E-target threshold, a cost) must also exist in `simulation_config.json`. If you change a number in a `.md` file, you must change it in `simulation_config.json` too (and vice versa) — never let one drift from the other.
- **Order of changes:** `simulation_config.json` → `README.md` (if a formula/rule changed) → affected card/form documents (`MASSNAHMENKARTEN.md`, `ANGRIFFSKARTEN.md`, `PARAMETER_TABELLE.md`, `BERECHNUNGSBOGEN_WELLE*.md`, etc.).
- **Verification step after content changes:** run `simulate_outcomes.py` then `balance_analysis.py` to confirm no dominant strategy or numeric inconsistency was introduced before regenerating any print material.
- The `.md` documents are the actual game-design product; editing them is content/editorial work, not refactoring, but the numeric-sync discipline still applies as if it were code.
- Generated binary outputs (`final_documents/*.docx,.pptx,.pdf`, `pptx_output/*.pptx`) must never be hand-edited — only regenerated via the generator scripts or their source templates.

## Function Design

**Size:** Functions are generally single-purpose and range from a few lines (`selection_to_key`, `compute_e_value`) to ~80 lines for orchestration functions (`run_simulation`, `simulate_selection`, `run_analysis`). No enforced limit; orchestration/`main`-adjacent functions are allowed to be long because they read top-to-bottom as a narrative of the simulation steps.

**Parameters:** Domain dataclasses and dicts are passed explicitly rather than bundled into a single config object — e.g. `simulate_selection(selection, budget_tier, waves, attacks, measures, events, base_cia, kz_start)` (`simulate_outcomes.py:355-364`) takes 8 positional parameters. New functions following this pattern should keep parameter order consistent with existing call sites rather than introducing kwargs-only signatures.

**Return values:** Functions that compute multiple related values return a `Dict` with named keys (e.g. `apply_attack` returns a dict with `e_value`, `severity`, `damage`, `kz_delta`, etc.) rather than a dataclass — this matches the JSON-serialization use case (results get written directly to `simulation_results.json` via `json.dumps`). Functions returning a small fixed tuple (e.g. `compute_costs -> Tuple[int, int, int]`) are used when the return shape is simple and stable.

## Module Design

**Exports:** No `__all__`, no public/private naming convention (no leading underscore for "private" helpers) — every function is a plain top-level function callable by any importer. `balance_analysis.py` imports specific named functions from `simulate_outcomes.py` rather than importing the module wholesale.

**No barrel files / no package `__init__.py`:** Each script is a flat module; there is nothing resembling a package index.

---

*Convention analysis: 2026-06-23*
