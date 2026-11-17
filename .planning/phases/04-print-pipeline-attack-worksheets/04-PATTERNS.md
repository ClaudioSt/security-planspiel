# Phase 4: Print Pipeline & Attack Worksheets - Pattern Map

**Mapped:** 2026-10-20
**Files analyzed:** 17 new/modified
**Analogs found:** 12 / 17 (5 have no code analog: TeX/Jinja/subprocess; use 04-RESEARCH.md sketches)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `planspiel/cli.py` (add `print` subcommand, `--check`) | route/CLI | request-response | `planspiel/cli.py` `_texts_command` / `_clues_command` | exact |
| `planspiel/printmodel.py` | model | transform | `planspiel/texts.py` `RevealView` + `review_text.py` | role-match |
| `planspiel/rules.py` (derived-constant helpers: Obergrenze, full damage, slope, Fall bounds) | utility (formula) | transform | `rules.kz_slope`, `rules.compute_bonus_reduction` | exact |
| `planspiel/fmt.py` (German numbers, `tex_escape`) | utility | transform | `planspiel/review_text.py` `format_eur` | exact |
| `planspiel/render.py` (Jinja env, `render_all`) | service | transform | none for Jinja; shape like `review_text.py` pure functions | partial |
| `planspiel/texbuild.py` (preflight, lualatex, timeout) | service | batch/subprocess | none in repo (git/subprocess absent) | no analog |
| `planspiel/stamp.py` (hash, date, dirty, manifest) | service | file-I/O | `planspiel/report.py` `write_summary` (file output) | partial |
| `print/planspiel.sty`, `print/templates/angriff.tex.j2`, `print/miktex-packages.txt` | config/template | transform | none (`content/texte.toml` for wording only) | no analog |
| `pyproject.toml` (jinja2, pypdf, `pdf` marker, addopts) | config | n/a | existing `[tool.pytest.ini_options]` | exact |
| `.gitignore` (`build/`), `.gitattributes` (`print/** text eol=lf`) | config | n/a | existing `.gitignore` entries | exact |
| `content/texte.toml` (`[sheets.angriff]`, `[sheets.labels]` additions, digit-free) | config/content | n/a | existing `sheets.*` keys, `RevealView.sheet` | exact |
| `tests/test_single_definition.py` (register new rules helpers / possible exemption) | test | n/a | itself, lines 19-96 | exact |
| `tests/test_print_preflight.py`, `test_print_driver.py`, `test_print_smoke.py` | test | subprocess | `tests/test_clues.py` CLI tests | role-match |
| `tests/test_print_stamp.py`, `test_print_model.py`, `test_print_render.py` | test | transform | `tests/test_budget_review_text.py`, `tests/test_texts_views.py` | role-match |
| `tests/test_worksheet_equivalence.py` (fast grid + `slow` replay + `pdf` text check) | test | batch | `tests/test_kernel_conformance.py`, `tests/test_enumeration.py` (slow) | role-match |
| `final_documents/generated/*.pdf`, `manifest.json` | output | file-I/O | `planspiel/report.py` summary writers | partial |

## Pattern Assignments

### `planspiel/cli.py` (add `print` subcommand)

**Analog:** `planspiel/cli.py` `_texts_command` (lines 32-50) and `_clues_command` (53-85).

**Command-function pattern**: lazy imports inside the function, catch `OSError`/parse errors, print `ERROR ...` plus a count line, return int exit code.
```python
def _texts_command(config: str, content_dir: str) -> int:
    import tomllib

    from planspiel.config import load_config
    from planspiel.texts import check_texts, load_content

    try:
        issues = check_texts(load_config(Path(config)), load_content(Path(content_dir)))
    except (OSError, tomllib.TOMLDecodeError) as error:
        print(f"ERROR texts.toml {content_dir}: {error}")
        print("1 Fehler, 0 Warnung(en)")
        return 1
    ...
    return 1 if errors else 0
```
**Parser registration** (lines 185-195): `subparsers.add_parser("texts", help=...)`, `--config` default `"simulation_config.json"`, `--content-dir` default `"content"`; add `--print-dir`, `--out-dir`, `--build-dir`, `--check` (`action="store_true"`, like `--strict`, line 149-153). Dispatch is an `if args.command == ...` chain at lines 212-220; add `if args.command == "print": return _print_command(...)` before the `validate` fall-through. Keep help text German. `print` build errors (PrintModelError, TexBuildError, missing packages) become `ERROR ...` lines plus return 1, not tracebacks. Test via `main([...])` + `capsys` (see `tests/test_clues.py:284-312`).

---

### `planspiel/printmodel.py` (model, transform)

**Analog:** `planspiel/texts.py` `RevealView` (618-642) for text access; `planspiel/rules.py` for every number.

**Revealed-text access** (only path allowed):
```python
class RevealView:
    def __init__(self, cfg: Config, texts: Texts) -> None: ...
    def attack_title(self, wave: Wave) -> str: ...
    def attack(self, attack_id: str) -> dict:   # name, narrative, cia_rationale, cases[], bonus_reasons{}
    def sheet(self, name: str) -> dict:         # deepcopy of sheets.<name> subtree
```
**Formula calls to reuse (never re-derive)** (`rules.py`): `kz_slope(kz_at_full_damage, kz_at_full_mitigation, mitigation_cap)` -> `Fraction` (101-102); `compute_bonus_reduction(wave, selection)` (88-98); `e_value_scaled(cia, weights, ws)` (61-63); `compute_recovery(selection, measures)` (48-52); `wave_kz_change(attack_kz_delta, event_kz)` (114-116, the only rounding point).

**CRITICAL constraint** (`tests/test_single_definition.py:83-96, 137-146`): any `ast.Attribute` named `s_unit, base_severity, mitigation_cap, kz_at_full_damage, kz_at_full_mitigation, e_threshold, recovery, init, opex, weights, bonus, kz_per_step` outside `rules.py`/`config.py` fails the fast suite. So: put derived numbers (Obergrenze = threshold + cap, full damage, slope, Fall bounds, M4 recovery table, bonus rows, weights) in new `rules.py` helpers returning a NamedTuple; `printmodel.py` reads only that tuple. Name model fields `points`, `factor`, `w_c`, `unit_eur` (not the guarded names). Do not define functions named like any `FORMULA_FUNCTIONS` entry (e.g. `apply_attack`, `wave_kz_change`) anywhere else.

D-06 guard: raise `PrintModelError` (build failure) when `base_severity != mitigation_cap` or any tier `severity_multiplier != 1`; do this check inside a `rules.py` helper (attribute access is allowed there). Model holds exact `Fraction` fields plus parallel display strings (D-11); expose `printed_fragments()`.

---

### `planspiel/rules.py` (new derived helpers)

**Analog:** `rules.kz_slope` (101-102), small pure function returning `Fraction`:
```python
def kz_slope(kz_at_full_damage, kz_at_full_mitigation, mitigation_cap) -> Fraction:
    return (Fraction(kz_at_full_mitigation) - Fraction(kz_at_full_damage)) / mitigation_cap
```
New helpers follow this style (no docstring unless it explains a rule, exact arithmetic, no builtin `round()`). Register each new name in `FORMULA_FUNCTIONS` in `tests/test_single_definition.py` (`name: RULES`).

---

### `planspiel/fmt.py` (German formatting + tex_escape)

**Analog:** `planspiel/review_text.py` (whole file, 41 lines).
```python
def format_eur(amount_eur: int) -> str:
    """Betrag in Euro mit Punkt als Tausendertrenner; negative Werte mit echtem Minuszeichen (U+2212)."""
    text = f"{abs(amount_eur):,}".replace(",", ".")
    return f"−{text}" if amount_eur < 0 else text
```
Reuse by import (it is registered in `FORMULA_FUNCTIONS` against `REVIEW_TEXT` at test line 66; moving it requires updating that map). Signs use `−`; `_tier_value_text` (23-26) shows the "+/−/±0" convention. Decimal comma and exact `Fraction` -> string formatting are new; keep each function defined once (the guard scans all `planspiel/*.py` and `tests/*.py` for duplicate names in the map).

---

### `planspiel/stamp.py`, `planspiel/render.py`, `planspiel/texbuild.py`

No close code analog. Use 04-RESEARCH.md: Pattern 1 (`run_lualatex`, lines ~238-266), Pattern 2 (`missing_tex_files` with `--miktex-disable-installer`), Pattern 5 (Jinja env), and the "Stamp mechanics" sketch. Repo conventions to follow: lazy imports in the CLI command, German user-facing messages, English identifiers, `pathlib.Path`, `encoding="utf-8"` on every read/write, `newline="\n"` for generated `.tex`. For manifest output follow the `write_summary` / `SUMMARY_FILENAME` style in `planspiel/report.py` (summary written to a target dir with `mkdir(parents=True, exist_ok=True)`, as in `cli.py` lines 100-107).

---

### `content/texte.toml` (`[sheets.angriff]`, `[sheets.labels]`)

**Analog:** existing `sheets.*` subtrees read via `RevealView.sheet(name)`. New wording must be digit-free (lint `uv run planspiel texts`, `tests/test_texts_digits.py`); numbers in text come from `str.format` in the model on a digit-free template string (RESEARCH Pitfall 8). Verify with `uv run planspiel texts` after each addition.

---

### `pyproject.toml`, `.gitignore`, `.gitattributes`

**Analog:** `pyproject.toml` lines 22-27:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "-m 'not slow' --strict-markers"
markers = ["slow: full-enumeration checks over all 782,336 dependency-valid combinations per tier; run with `uv run pytest -m slow`"]
```
Change to `addopts = "-m 'not slow and not pdf' --strict-markers"` and append a `pdf: ...` marker string (strict markers). Add `jinja2==3.1.6` to `dependencies`, `pypdf==6.19.0` to the `dev` group via `uv add` (checkpoint first, per RESEARCH audit). `.gitignore`: add `build/` (existing style is one path per line, plus `__pycache__/`, `.venv/`).

---

### Tests

**CLI tests** (analog `tests/test_clues.py:284-312`): `from planspiel.cli import main`; `assert main([...]) == 0`; `capsys`; mini fixtures via `tests.support` (`CONFIG_PATH`, `CONTENT_DIR`, `MINI_CONTENT_DIR`, `REPO_ROOT`) and `tests/fixtures/mini_config.json`.

**Parametrised real+mini fixture** (analog `tests/test_texts_views.py:21-31`):
```python
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]
@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    return load_config(config_path), load_texts(content_dir / "texte.toml")
```
**Equivalence test**: replay lives in `tests/` as an independent encoding of the printed steps (do not name it `apply_attack`/`wave_kz_change`); compare against `rules.apply_attack` and `rules.wave_kz_change`; add the explicit unscored-output list (`cia_delta`) and a key-set guard on the `apply_attack` result (D-21). Slow full replay uses `enumerate_tier(cfg, tier, on_outcome=cb)` from `planspiel/enumerate.py` under `@pytest.mark.slow` (existing marker, ~48 s per tier). PDF tests: new `@pytest.mark.pdf`, skip when `shutil.which("lualatex") is None` or the preflight reports missing packages.

**Single-definition test**: edit `tests/test_single_definition.py` lines 19-66 (`FORMULA_FUNCTIONS`) for new rules helpers; only if unavoidable add `planspiel/printmodel.py` to the exemption tuple at line 141 (document why).

---

## Shared Patterns

### Single source of truth / no re-derivation
**Source:** `planspiel/rules.py`, guard `tests/test_single_definition.py`
**Apply to:** `printmodel.py`, `fmt.py`, `render.py`, `stamp.py`, all tests. Printed numbers come from config via `rules` helpers; templates receive strings only.

### Revealed texts only through `RevealView`
**Source:** `planspiel/texts.py:618-642`
**Apply to:** `printmodel.py`. Sheets are revealed material, title "Angriff N: <Name>" from `RevealView.attack_title(wave)`.

### CLI error style
**Source:** `planspiel/cli.py:38-50`
**Apply to:** `_print_command`. German messages, `ERROR <code> <path>: <msg>` lines, exit codes 0/1, `configure_utf8_stdio()` already applied in `main`.

### Exact arithmetic and rounding
**Source:** `planspiel/rounding.py` `round_half_away_frac`, `rules.wave_kz_change`
**Apply to:** printmodel, tests. Never use builtin `round()` in `rules.py`/`rounding.py`; Fractions throughout.

### Determinism and no hang (environment)
**Source:** 04-RESEARCH.md Pitfalls 1, 2, 7
**Apply to:** `texbuild.py`, `stamp.py`, `.gitattributes`. `kpsewhich --miktex-disable-installer`, `lualatex --disable-installer`, `stdin=DEVNULL`, timeouts, `\pdfvariable suppressoptionalinfo 1023` in the `.sty`, CRLF-normalised hashing.

### Always `uv run`
`uv run pytest`, `uv run pytest -m slow`, `uv run pytest -m pdf`, `uv run planspiel print`; never bare `python`.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `planspiel/texbuild.py` | service | subprocess/batch | No subprocess/external-tool code in `planspiel/`; use RESEARCH Patterns 1-2 |
| `planspiel/render.py` | service | transform | No templating exists; use RESEARCH Pattern 5 (Jinja, `StrictUndefined`, `tex_escape` finalize) |
| `planspiel/stamp.py` | service | file-I/O + git | No git access in code today; use RESEARCH "Stamp mechanics" sketch |
| `print/planspiel.sty`, `print/templates/angriff.tex.j2` | template | transform | No TeX in repo; use RESEARCH Pattern 3 skeleton; colours from `content/assets/GUIDELINES.md` |
| `print/miktex-packages.txt` | config | n/a | New; list `colortbl` plus `tikzfill` (D-17 refined) |

## Metadata

**Analog search scope:** `planspiel/*.py` (15 modules), `tests/` (about 45 files), `pyproject.toml`, `.gitignore`
**Files scanned/read:** cli.py, review_text.py, texts.py (RevealView), rules.py (formulas, 86-165), test_single_definition.py, conftest.py, tests/support/__init__.py, test_texts_views.py, test_budget_review_text.py
**Pattern extraction date:** 2026-10-20
