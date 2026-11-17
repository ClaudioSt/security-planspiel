# Coding Conventions

**Analysis Date:** 2026-11-09

## Naming Patterns

**Files:**
- Python modules are `snake_case.py` in the flat package `planspiel/` (for example `planspiel/rules.py`, `planspiel/printmodel.py`, `planspiel/balance.py`).
- Print models are named after the document they build: `planspiel/cards.py`, `planspiel/booklet.py`, `planspiel/wave_page.py`, `planspiel/debrief.py`, `planspiel/was_neu.py`.
- Tests are `tests/test_<topic>.py`; tests that need a LaTeX engine end in `_pdf.py` or `_pdf` in the name (for example `tests/test_cards_pdf.py`) and carry `pytestmark = pytest.mark.pdf`.
- Test helpers live in `tests/support/` (for example `tests/support/harness.py`, `tests/support/golden.py`, `tests/support/tex.py`).
- Print templates are `print/templates/*.tex.j2`; the shared LaTeX style is `print/planspiel.sty`.

**Functions:**
- `snake_case`, with verb-first names for public operations: `compute_cia`, `compute_costs`, `compute_recovery` (`planspiel/rules.py`), `build_*` for print models, `check_*` for validators, `load_*` for readers (`load_config` in `planspiel/config.py`, `load_content` in `planspiel/texts.py`), `render_all` in `planspiel/render.py`.
- Private helpers carry a leading underscore: `_requirements_met` and `_to_int` in `planspiel/rules.py`, `_validate_command` and `_texts_command` in `planspiel/cli.py`.
- Predicates read as questions: `dependencies_satisfied`, `swap_possible`, `swap_legal`, `over_budget`.
- Exact-arithmetic variants carry a suffix: `e_value_scaled`, `severity_scaled`, `round_half_away_frac`.

**Variables:**
- `snake_case` throughout. Module-level constants are `UPPER_SNAKE_CASE`: `CARDS_PER_SHEET`, `LEVELS`, `EVENT_DECK_JOB` in `planspiel/cards.py`, `DEFAULT_CONFIG_PATH` in `planspiel/config.py`, `MAX_WINDOWS` in `planspiel/gate.py`.
- Short domain abbreviations are used without explanation and must stay in the vocabulary of the README glossary: `kz`, `cia`, `e_value`, `e_threshold`, `opex`, `init`, `ros`. Do not invent new abbreviations without a glossary entry in `README.md`.
- CIA components are single lowercase keys: `"c"`, `"i"`, `"a"` (see `compute_cia` in `planspiel/rules.py`).
- Measure and wave identifiers come from the config and keep their config spelling: `"M4"`, `wave_id`, `attack_id`.

**Types:**
- PascalCase for dataclasses and NamedTuples named after domain entities: `Config`, `Wave`, `Attack`, `Measure`, `MeasureLevel`, `BudgetTier`, `Event` in `planspiel/config.py`; `CardFacts` in `planspiel/rules.py` follows the same convention.
- Exception classes end in `Error`: `ConfigError` (`planspiel/config.py`), `PrintModelError` (`planspiel/printmodel.py`), `WorksheetInvariantError` (`planspiel/rules.py`), `TexBuildError` (`planspiel/texbuild.py`), `StampError` (`planspiel/stamp.py`).

## Code Style

**Formatting:**
- No formatter is configured (no `ruff`, `black` or `.editorconfig`). Follow the existing code.
- 4-space indentation, double quotes, trailing commas in multi-line literals.
- Lines are kept near 110 characters by discipline; long docstrings and German string literals exceed this in places (`planspiel/rules.py`, `planspiel/cards.py`).

**Linting:**
- No linter configuration. Two project tests are the only static rules:
  - `tests/test_encoding_lint.py` parses every `planspiel/**/*.py`, `tests/**/*.py` and the root wrapper scripts with `ast` and requires an explicit `encoding=` on every text-mode `open()`/`read_text()`/`write_text()`. The machine code page is cp1252, so this is mandatory.
  - `tests/test_single_definition.py` enforces that each game formula is defined once, in `planspiel/rules.py`.
- Do not assume UTF-8 default encodings anywhere. Use `path.read_text(encoding="utf-8")`.

## Type Hints

- Every function signature carries type hints (CLAUDE.md, module style).
- Two spellings coexist. Older modules (`planspiel/rules.py`, `planspiel/config.py`, `planspiel/rounding.py`) use `typing` (`Dict`, `List`, `Optional`, `Tuple`, `Sequence`). Newer modules (`planspiel/cards.py`, `planspiel/booklet.py`, `planspiel/printmodel.py`, `planspiel/master.py`) use builtin generics: `tuple[str, ...]`, `tuple[tuple[str, str], ...]`.
- For new code, use builtin generics (`dict[str, int]`, `tuple[str, ...]`) and `Optional[X]` or `X | None` consistently within the module you edit. Do not rewrite the typing style of an untouched module.
- Values that must stay exact are typed `Fraction` (`planspiel/config.py` `Wave.weights: Dict[str, Fraction]`, `MeasureLevel.recovery: Fraction`). Never store exact game values as `float`.

## Arithmetic and Rounding

This is the most important convention of the codebase. The printed rules and the code must agree exactly.

- Use `fractions.Fraction` or integer scaling for E-Wert, Gesamtreduktion, reduction over threshold, severity and damage. Convert with `int(...)` only after an explicit `_to_int` check (`planspiel/rules.py`), which raises `ValueError` on a non-integral value.
- The KZ change of a wave is rounded exactly once, half away from zero, through `planspiel/rounding.py`:

```python
def round_half_away(n: int, d: int = 1) -> int:
    if n >= 0:
        return (2 * n + d) // (2 * d)
    return -((-2 * n + d) // (2 * d))
```

- Python's built-in `round()` (banker's rounding) is forbidden in `planspiel/rules.py` and `planspiel/rounding.py`. Use `round_half_away` or `round_half_away_frac`.
- `started_steps` in `planspiel/rounding.py` implements "je angefangene 10.000 EUR" (per started 10,000 EUR). Use it for overspend steps; do not reimplement ceiling division.
- RoS to two decimals goes only through `rules.ros_two_decimals`. The Final-Index is `weight_kz * KZ + weight_ros * RoS2`.
- Float values in the config (`kz_at_full_damage`, `kz_at_full_mitigation` on `Attack`) are converted to exact values before any arithmetic in the rules.

## Formulas

- Each game formula has exactly one definition in `planspiel/rules.py`. Enumeration, balance checks and print models call these functions; they never re-implement them.
- Formulas stay linear and free of exponents so facilitators can recompute the worksheets by hand. Only operands come from `simulation_config.json`.
- New formula code belongs in `planspiel/rules.py`. Helpers that only support printing belong in the print model module that uses them.

## Numbers and Prose

- Numbers live only in `simulation_config.json`. Never write a literal game number into code that is printed or compared against the config. The validator (`planspiel validate`) and the digit lint (`planspiel texts`) guard this.
- Prose lives only in `content/texte.toml`. Print models pass strings through `planspiel.texts` and `planspiel/fmt.py`; they never embed German sentences as literals if the sentence is printed.
- German number formatting goes through `planspiel/fmt.py` (`format_approx`, exact-to-decimal helpers). Do not format numbers with f-strings directly in print output.

## Import Organization

**Order:**
1. Standard library (`import json`, `from fractions import Fraction`, `from pathlib import Path`).
2. Third-party (`import pytest`, `import jinja2`, `from pypdf import ...`).
3. Project imports: `from planspiel import rules, fmt` or `from planspiel.config import Config`.

Blank lines separate the groups. In tests, a `tests.support` import group follows the project group (see `tests/test_rules_exact.py`).

**Style:**
- Prefer `from planspiel import module` followed by `module.function()` for modules that are used as namespaces (`rules`, `fmt`, `audience`, `texbuild`).
- Use `from planspiel.config import ...` for dataclasses and named functions.
- Imports inside functions are used deliberately for CLI subcommands, so `planspiel --help` does not import TeX, Jinja2 or the enumeration code (`planspiel/cli.py`, see `_validate_command` and `_texts_command`). Keep this lazy pattern for new heavy subcommands.
- Module aliases are used to avoid shadowing the builtin: `from planspiel import enumerate as enum` in `tests/test_candidate_support.py`.

**Path Aliases:**
- None. The package is imported by name from the repository root (`pythonpath = ["."]` in `pyproject.toml`).

## Dataclasses and Value Types

- Config objects are plain `@dataclass` and are read-only after loading (`planspiel/config.py`). Do not mutate them in rules or enumeration code.
- Print models are `@dataclass(frozen=True)` and hold finished strings only:

```python
@dataclass(frozen=True)
class MeasureCard:
    kind: str
    card_id: str
    measure_id: str
    title: str
    ...
```

- Use `NamedTuple` for small immutable results of pure functions (`CardFacts`, `BonusRow`, `RecoveryRow` and `WorksheetConstants` in `planspiel/rules.py`).
- Use `dataclasses.replace` to derive variants of frozen objects.
- Prefer pure functions over state. There is no global mutable state; every run loads the config fresh. Parallelism exists only inside enumeration (`planspiel/parallel.py`).

## Error Handling

**Strategy:** validate early, raise specific exceptions, convert to exit codes at the CLI boundary.

**Patterns:**
- Input and structure problems in the config raise `ConfigError` with a list of issues (`planspiel/config.py`). `planspiel validate` prints every issue and returns exit code 1 on errors (`planspiel/cli.py`).
- Print model violations raise `PrintModelError`, which the CLI reports and maps to a failing build. A missing hand-calculation shape raises at build time instead of printing a wrong formula (build guards in `planspiel/printmodel.py`, `WorksheetInvariantError` in `planspiel/rules.py`).
- Bad arguments and impossible states raise `ValueError` with a message that names the offending value: `raise ValueError(f"Unbekannte Schicht '{layers}'. Verfügbar: ...")` (`planspiel/balance.py`).
- `planspiel/cli.py` converts `OSError`, `json.JSONDecodeError`, `tomllib.TOMLDecodeError`, `jinja2.TemplateError` and `texbuild.TexBuildError` into a message plus a non-zero exit code. It does not print stack traces for expected failures.
- Exit codes are part of the contract: `planspiel print --check` returns 0 current, 1 stale, 2 environment problem; `balance_analysis.py` returns 0 only when every check passes and reserves 1 for "check failed". A crash is not a verdict (`planspiel/balance.py` catches `Exception` and reports it separately).
- Catch narrow exception types. Do not add a bare `except:`.
- Do not swallow errors in the print pipeline; a stale or inconsistent document must fail the build.

**Messages:**
- Facilitator-facing messages (CLI output, validation issues, build errors) are German, following the pattern `ERROR <code> <path>: <message>` used by `validate`.
- Developer-facing exception text may be German or English; the existing modules mix both. Keep new messages in the language of the surrounding module.

## Logging

**Framework:** none. No `logging` import exists in `planspiel/`.

**Patterns:**
- Command output uses `print()` in `planspiel/cli.py` and the balance report modules. The CLI reconfigures stdout and stderr to UTF-8 (`configure_utf8_stdio` in `planspiel/cli.py`) because the Windows console code page is cp1252.
- Reports are generated as text or JSON, not as log lines. Do not introduce `logging` for report output.

## Comments and Docstrings

**Module docstrings** state the requirement IDs and decision IDs the module implements, in the first line or paragraph:

```python
"""Overspend trim-back gate (RULE-04, D-17, D-24): closure, required X and gate result against brute force."""
```

Examples: `PRINT-07, D-05, D-08` in `planspiel/booklet.py`, `VEIL-02` in `planspiel/audience.py`, `BAL-04` in `planspiel/report.py`. Keep this pattern for new modules that belong to a numbered requirement.

**Function docstrings** are short, usually one sentence, in German or English, describing the rule being implemented, not the mechanics of Python. Several rule functions describe the printed rule in the German words used on the worksheet (`level_requirements` in `planspiel/rules.py`).

**Inline comments** explain why, not what. Typical examples: the reason for interpolating KZ linearly (see `attack_kz_delta()` in `planspiel/rules.py`), the reason a rounding helper avoids `round()`.

**When to comment:**
- Explain a rounding choice, a hand-calculation constraint or a veil rule.
- Do not add comments or docstrings to code you did not change (project rule).
- Do not restate the code in comments.

**JSDoc/TSDoc:** Not applicable.

## Function Design

**Size:** Pure formula functions are short. Enumeration and balance functions are longer; split out helpers rather than adding nested state.

**Parameters:**
- Pass the `Config` and the exact selection (`Dict[str, int]` mapping measure id to level) explicitly. Do not read the config from a module global.
- Use keyword arguments for flags: `strict=True`, `allow_recovery`.

**Return Values:**
- Return exact values (`Fraction`, `int`) from rule functions; convert to strings only in print models or `fmt`.
- Return tuples for multiple results: `compute_costs` returns `(init, opex_per_wave, total)`.

## Module Design

**Exports:** Modules expose plain functions and dataclasses; there are no `__all__` lists.

**Barrel Files:** `planspiel/__init__.py` does not re-export symbols. Import from the defining module.

**Layering:** Layers import downward only (config, content, rules, enumeration, balance, print models, print pipeline, entry points). A rules module must not import a print model. Respect this when adding a module; see `ARCHITECTURE.md`.

**Entry-point wrappers:** `simulate_outcomes.py`, `analyze_simulation_results.py` and `balance_analysis.py` stay thin: they call into `planspiel` and contain no formulas.

## Documents and Generated Content

- `final_documents/generated/` and `manifest.json` are generated by `uv run planspiel print`. Never edit them by hand.
- `archive/` is history outside the build. Do not import from it and do not map it as live code (`tests/test_no_archive_references.py`).
- Order of a content change: `simulation_config.json` -> `README.md` -> `content/texte.toml` -> `uv run planspiel print` -> `uv run planspiel print --check` -> commit the generated PDFs together with the inputs.
- Agent context files are pinned by `tests/test_claude_md_current.py`; statements there (for example the `planspiel print --check` command) must stay in the docs.

## Commits

- Conventional commits with an English subject: `feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:`, optionally with a phase-plan scope such as `docs(07-12): ...`.
- Simulation and rules changes follow TDD: a RED commit with the failing test, then GREEN.

---

*Convention analysis: 2026-11-09*
