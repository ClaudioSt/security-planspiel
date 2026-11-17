# Phase 3: Content Source & Veiling - Pattern Map

**Mapped:** 2026-10-10
**Files analyzed:** 19 (new and modified)
**Analogs found:** 17 / 19

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `planspiel/texts.py` (new: load, required_keys, check_coverage/digits/giveaway/clues, views, attack_title) | service/validator | transform + request-response | `planspiel/validate.py` (Issue type) + `planspiel/review_text.py` (text from params) | role-match |
| `planspiel/cli.py` (add `texts`, `clues` subcommands) | route/CLI | request-response | `planspiel/cli.py` `_validate_command` + `validate`/`gate` parsers | exact |
| `planspiel/config.py` (drop prose fields) | model/loader | transform | itself, lines 22-36, 96, 116+ | exact (modify) |
| `planspiel/validate.py` (`schema.prose_in_config` error) | validator | transform | `_Validator.removed_key` (validate.py:114-119) | exact |
| `planspiel/rules.py` (flat_budget label, bonus descriptions) | service | transform | sibling event-label branches in `evaluate_event` | exact (modify) |
| `content/texte.toml` | config/content | file-I/O | none in repo (JSON `simulation_config.json` is the structural sibling) | no analog |
| `content/digit_allowlist.toml`, `content/giveaway_terms.toml`, `content/clues.toml` | config/data | file-I/O | none | no analog |
| `content/assets/README.md`, `GUIDELINES.md` | docs | n/a | none | no analog |
| `tests/test_texts_*.py`, `tests/test_clues.py` | test | transform | `tests/test_config_text.py`, `tests/test_validate.py` | role-match |
| `tests/test_config_prose_removed.py` | test | transform | `tests/test_validate.py` | role-match |
| `tests/test_texts_migration.py`, `tests/test_inventory.py` | test | file-I/O | `tests/test_config_text.py` | partial |
| `tests/test_config_text.py` (retarget to TOML) | test | transform | itself | exact (modify) |
| `tests/fixtures/mini_texte.toml` (+ `mini_clues.toml`) | fixture | file-I/O | `tests/fixtures/mini_config.json` | role-match |
| `tests/test_encoding_lint.py` | test | static lint | itself (binary `open(p, "rb")` exempt) | exact (unchanged, constraint) |
| `.planning/phases/03-content-source-veiling/tools/golden_text_diff.py` | utility (throwaway) | batch/transform | `.planning/phases/02-rule-changes/tools/golden_diff.py` + `tests/support/golden.py` | role-match |
| `tests/golden/characterization_*.json` | data | snapshot | 02-07 text-only update procedure | exact (procedure) |
| `tests/test_legacy_generators_smoke.py`, `test_rules_semantics.py`, `test_kurswechsel.py`, `test_sparprogramm.py`, `test_budget_review_text.py`, `test_rules_exact.py`, `test_kernel_conformance.py`, `test_e_target_removed.py` | test | modify | consumer map in RESEARCH.md ("Config strip") | exact |
| `simulation_config.json`, `tests/fixtures/mini_config.json` | config | strip fields | themselves | exact |
| `03-INVENTORY.md` | docs | n/a | none | no analog |

## Pattern Assignments

### `planspiel/texts.py` (service/validator, transform)

**Analog 1:** `planspiel/validate.py` for the `Issue` result type. Reuse it, do not create a new one.

**Issue type to import** (validate.py:37-42):
```python
@dataclass(frozen=True)
class Issue:
    level: str
    code: str
    path: str
    message: str
```
Use `from planspiel.validate import Issue`. Codes are dotted: `texts.missing_key`, `texts.orphan_key`, `texts.digit`, `texts.giveaway`, `clues.too_few`, `clues.single_source`, `clues.quote_not_found`, `clues.not_prewave`. Messages are German, as in validate.py.

**Validator style** (validate.py:101-119): a small class collecting `Issue`s via `error(code, path, message)`. Mirror it, or use plain functions that return `List[Issue]` (`check_*`).
```python
class _Validator:
    def __init__(self, raw: dict):
        self.raw = raw
        self.issues: List[Issue] = []
    def error(self, code: str, path: str, message: str) -> None:
        self.issues.append(Issue("error", code, path, message))
```

**Analog 2:** `planspiel/review_text.py` for code-generated number text (D-03, D-23). Module docstring in German, pure functions, typed, no I/O, exact integers.
```python
def format_eur(amount_eur: int) -> str:
    text = f"{abs(amount_eur):,}".replace(",", ".")
    return f"−{text}" if amount_eur < 0 else text
```
Use the true minus U+2212 and `format_eur` for any generated effect line. `attack_title(texts, attack_id, position, *, revealed=False)` follows this style: the digit comes from the caller (`Wave.wave_id`), never from the TOML.

**Loading TOML:** `config.py:100-101` reads JSON with `path.read_text(encoding="utf-8")`. For TOML use binary mode, which `tests/test_encoding_lint.py:17-35` exempts:
```python
with open(path, "rb") as handle:
    data = tomllib.load(handle)
```
Never `read_text()` without `encoding=` (the lint fails; its targets are all `planspiel/**/*.py` and `tests/**/*.py`). Locate `content/` relative to the repo root the way `tests/support/__init__.py` does (`Path(__file__).resolve().parents[N]`), and take an optional path argument for tests.

**Key derivation:** `required_keys(cfg)` is derived from the typed `Config` (`cfg.measures`, `cfg.waves[].attack_id`, `cfg.events`, `cfg.final_events`), so a new id fails coverage. Do not hard-code three attacks (SCEN, v4).

---

### `planspiel/cli.py` (route, request-response)

**Analog:** `_validate_command` and the `validate` subparser (cli.py:13-29, 87-97).

**Command function pattern** (cli.py:13-29): lazy imports inside the function, `Issue` printing, summary line, exit code 1 on errors.
```python
def _validate_command(config: str, strict: bool) -> int:
    from planspiel.config import read_raw_config
    from planspiel.validate import validate
    ...
    errors = [issue for issue in issues if issue.level == "error"]
    for issue in issues:
        label = "ERROR" if issue.level == "error" else "WARN"
        print(f"{label} {issue.code} {issue.path}: {issue.message}")
    print(f"{len(errors)} Fehler, {len(warnings)} Warnung(en)")
    return 1 if errors or (strict and warnings) else 0
```
Copy the printing and exit-code block exactly for `_texts_command` and `_clues_command`.

**Parser registration** (cli.py:87-97, 116-128):
```python
validate_parser = subparsers.add_parser("validate", help="Prüft die Konfiguration auf Fehler und Handrechenbarkeit.")
validate_parser.add_argument("--config", default="simulation_config.json", help="Pfad zur Konfigurationsdatei.")
```
Add `--texts` / `--clues` path options with defaults `content/texte.toml` / `content/clues.toml`, German help text. Dispatch at cli.py:133-137 is an if-chain; add two branches before the `validate` fallthrough. The `clues` command also prints the Markdown matrix table (no committed generated file). Output goes through `configure_utf8_stdio()` (already called in `main`).

**Tests for the CLI:** `from planspiel.cli import main` and call `main([...])`, as in `tests/test_validate.py:9`.

---

### `planspiel/validate.py` (add `schema.prose_in_config`)

**Analog:** `removed_key` (validate.py:114-119). Same helper shape, but `self.error(...)` instead of `self.warning(...)`:
```python
def removed_key(self, key: str, path: str) -> None:
    self.warning("schema.removed_key", path,
        f"Schlüssel '{key}' wird nicht mehr verwendet (E-Ziel-Bonus/Malus entfernt) und ignoriert")
```
New helper `prose_key(key, path)` emits `schema.prose_in_config` ("Prosa gehört nach content/texte.toml"). Call it for `attacks.*.description`, `waves[].name`, `bonus_measures[].description`, `events/final_events[].description`. Replace the required-field checks at validate.py:323, 349, 429-430. Keep event `name` and measure `name` required. The existing test `tests/test_validate.py:31-40` (one slope warning on the real config) must stay green because the real config ends up clean.

---

### `planspiel/config.py` (strip prose fields)

**Analog:** itself.
- config.py:22-26 `BonusMeasure` loses `description`.
- config.py:30-33 `Wave` loses `name`.
- `Event` loses `description` (positional constructor change; update test call sites).
- config.py:96 params exclusion becomes `("id", "name", "type")`:
```python
params={k: v for k, v in ev.items() if k not in ("id", "name", "description", "type")},
```
- `load_config` (config.py:116) calls `check_config`, so the new validator error is enforced on every load.

---

### `planspiel/rules.py` (labels from params)

**Analog:** the other event-label branches in `evaluate_event`, which already build labels from params (RESEARCH.md pattern 3). Change `rules.py:298` (`flat_budget`) from returning `event.description` to `f"Gesamtbudget {p['budget_delta']}k€"`, the same k€ style as the siblings (e.g. `f"{active} aktive Maßnahmen x {p['opex_per_measure']}k€"`). Note: the research cites rules.py lines 88-100, 146, 171, 430, 435, 741, 854 for `compute_bonus_reduction` returning descriptions and `bonus_descriptions`/`wave_name` record keys; read those lines fresh before editing (I did not re-verify the line numbers in this mapping).

---

### `tests/test_texts_*.py`, `tests/test_clues.py` (test)

**Analog:** `tests/test_config_text.py` and `tests/test_validate.py`.

**Imports and helpers** (test_validate.py:1-28):
```python
from planspiel.config import load_config
from tests.support import CONFIG_PATH, REPO_ROOT
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"

def _errors(issues):
    return [issue for issue in issues if issue.level == "error"]
```
Issue-code assertions use `warning.code == "..."`, `warning.path == "..."`, and substring checks on `message`.

**Reusable lints** (test_config_text.py:9, 61-85): `MOJIBAKE_MARKERS = ("Ã", "Â", "â€")` and `TRANSLITERATION_PATTERNS` (regex stems `stoerung`, `fuehr`, `massnahm`, ...). Move `_display_strings`, the mojibake test and the transliteration walk to iterate all TOML strings. Import `TRANSLITERATION_PATTERNS` into the giveaway tests instead of copying (research item 6).

**Offender-list assertion style** (test_config_text.py:121-128): build a list of offender strings and `assert offenders == []`.
```python
offenders = [f"{path}: {text!r} (stem {pattern.pattern})" for path, text in ... for pattern in ... if pattern.search(text)]
assert offenders == []
```

**Retarget** `tests/test_config_text.py:28-30` (bonus description assert) and `:117-118` (`waves[1]["name"] == "OT-Störung"`) to `attacks.ot.revealed.name == "OT-Störung"` in TOML (RESEARCH consumer map). Keep `test_utf8_stdio_helper` (:44-58) as is.

**Fixtures:** mirror `tests/fixtures/mini_config.json` with `tests/fixtures/mini_texte.toml` (+ `mini_clues.toml`), so the lints are tested without the real content.

---

### `.planning/phases/03-content-source-veiling/tools/golden_text_diff.py` (throwaway utility)

**Analog:** `.planning/phases/02-rule-changes/tools/golden_diff.py`.

**Header/imports/paths** (golden_diff.py:1-22):
```python
"""... Imports only the installed `planspiel` package, never `tests`."""
import argparse, json, ...
from pathlib import Path
from planspiel import rules
from planspiel.config import load_config
PHASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
CONFIG_PATH = REPO_ROOT / "simulation_config.json"
```
**Caveat:** that docstring says "never `tests`", but the Phase 3 script must rebuild goldens through `tests.support.harness` / `golden_cases` and `tests.support.golden.flatten` (RESEARCH step 3). Run it via `uv run` from the repo root so `tests` is importable.

**Reuse from `tests/support/golden.py`:** `flatten(obj, prefix)` (:34-45) produces dotted paths like `expected.waves[0].wave_name`; `_same(a, b)` (:62-67) is type-strict equality; `_field_name`/`_counter_name` (:91-98) strip the `expected.` prefix and index digits. Classify each differing path against the allowed patterns (`wave_name`, `bonus_descriptions[...]`, sparprogramm `effect_description`), print per-tier counts and `unexpected: N`, and `sys.exit(1)` when N > 0.

**Output style:** `out_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")` (golden_diff.py:364); binary writes use `open(..., "wb")`; `json.loads((p).read_text(encoding="utf-8"))`.

**CLI style:** `argparse` subcommands with `main()` + `if __name__ == "__main__": main()` (golden_diff.py:368-394). A single no-subcommand `check` mode is enough here.

---

## Shared Patterns

### UTF-8 text I/O
**Source:** `tests/test_encoding_lint.py:17-47`
**Apply to:** `planspiel/texts.py`, every new test, `golden_text_diff.py`
Every `open()` in text mode, `read_text` and `write_text` needs `encoding="utf-8"`; TOML goes through `open(path, "rb")`. The lint covers `planspiel/**`, `tests/**` and three legacy scripts, not `.planning/` tools, but follow the rule there too.

### Issue reporting and exit code
**Source:** `planspiel/validate.py:37-42`, `planspiel/cli.py:23-29`
**Apply to:** `texts.check_*`, `clues`, new CLI commands
`Issue(level, code, path, message)`, German messages, `ERROR code path: message` lines, final `N Fehler, M Warnung(en)`, exit 1 on any error.

### Generated number text, no `{param}` placeholders
**Source:** `planspiel/review_text.py` (`format_eur`, `boundary_text`, `penalty_rows`)
**Apply to:** event effect labels (rules.py), the `attack_title` helper, any line carrying a game number
Pure functions from config params; U+2212 for negatives; numbers never enter TOML (D-03).

### Golden handling (D-08)
**Source:** `tests/support/golden.py:156` `check_golden(path, actual, update, report)`, 02-07 precedent
**Apply to:** the strip of config prose
Do not run `--update-golden` before the golden_text_diff report shows `unexpected: 0` and the user approves (D-25). Digest and gate goldens must stay byte-identical.

### Test-support paths
**Source:** `tests/support/__init__.py` (`REPO_ROOT`, `CONFIG_PATH`)
**Apply to:** all new tests. Add `TEXTE_PATH = REPO_ROOT / "content" / "texte.toml"` here (or in the test modules) instead of recomputing the path.

### Run commands
Always `uv run pytest -q` (baseline 551 passed, 19 deselected); `uv run planspiel validate|texts|clues`. Never the `python` on PATH.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `content/texte.toml` | content | file-I/O | No TOML or prose content file exists; structure comes from RESEARCH.md "Pattern 1" and the appendix `03-RESEARCH-APPENDIX-STORY-SOURCE.md` (verbatim source texts). Use plain `"""` multiline strings, bare digit keys (`1 = "..."`) only for level tables, no line-ending backslashes. |
| `content/digit_allowlist.toml`, `giveaway_terms.toml`, `clues.toml` | data | file-I/O | New data formats; schemas are in RESEARCH.md (`[[allow]]` key/token/why; substrings/tokens/compounds/story_exceptions; `[[clue]]` attack/source/quote/why). |
| `content/assets/README.md`, `GUIDELINES.md`, `03-INVENTORY.md` | docs | n/a | Pure documentation; formats in RESEARCH.md "Assets folder" and the inventory draft. |

## Notes for the planner

- There is no `content/` directory yet; `tests/fixtures/` holds only `mini_config.json`.
- `planspiel/config.py` params exclusion is at line 96 (research said 93-96); line numbers in `rules.py` and `validate.py` come from RESEARCH.md and were not re-verified here.
- `tests/test_single_definition.py` excludes `generate_*.py`; new modules in `planspiel/` fall under it, so do not duplicate function names defined in `rules.py`/`review_text.py` (for example `format_eur`); import them.
- Legacy generators (`generate_*.py`) stay untouched (D-07). Only `tests/test_legacy_generators_smoke.py:18,22` is retargeted to `config["events"]["wave_1"][1]["name"]`.

## Metadata

**Analog search scope:** `planspiel/*.py`, `tests/`, `tests/support/`, `tests/fixtures/`, `.planning/phases/02-rule-changes/tools/`
**Files read:** validate.py (1-140), review_text.py, cli.py, config.py (1-60, 96-125), test_config_text.py, test_encoding_lint.py, test_validate.py (1-50), golden.py (28-102), golden_diff.py, CONTEXT.md, RESEARCH.md (1-486 of 781)
**Pattern extraction date:** 2026-10-10
