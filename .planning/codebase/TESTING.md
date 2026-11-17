# Testing Patterns

**Analysis Date:** 2026-11-09

## Test Framework

**Runner:**
- pytest 9.1.1 (dev dependency group in `pyproject.toml`), run through uv.
- Config: `[tool.pytest.ini_options]` in `pyproject.toml`
  - `testpaths = ["tests"]`, `pythonpath = ["."]`
  - `addopts = "-m 'not slow and not pdf' --strict-markers"`: the default run excludes the `slow` and `pdf` markers, and unknown markers are errors.
  - Registered markers: `slow`, `pdf`, `balance`.

**Assertion Library:**
- Plain `assert` statements (pytest rewriting). No assertion library is used.
- `pytest.raises(..., match=...)` for expected errors (see `tests/test_print_render_env.py` and `tests/test_rules_exact.py`).
- `pytest.approx` is not used for game values; exact comparisons use `Fraction` equality.

**Other test-time dependencies:**
- `pypdf==6.19.0` (dev group) reads built PDFs in the `pdf` tests (`tests/support/pdf_text.py`).
- LuaLaTeX via MiKTeX for `pdf` tests; the marker is skipped when the engine or packages are missing.

**Run Commands:**

```bash
uv run pytest                          # fast suite (excludes slow and pdf); about 2900 tests, about 4 min
uv run pytest -m pdf                   # real LuaLaTeX builds; skips without TeX
uv run pytest -m slow                  # full enumeration over all dependency-valid combinations per tier
uv run pytest tests -m balance         # Phase-6 design-principle checks on the chosen config
uv run pytest tests -m balance --planspiel-config <candidate> --planspiel-content-dir <dir>   # candidate check
uv run pytest tests/test_rules_exact.py          # single file
uv run pytest tests --update-golden              # rewrite tests/golden/*.json (review the diff before commit)
uv run pytest --collect-only -q | tail -3        # test count only
```

Never use the `python` on PATH; always `uv run pytest` or `uv run python ...`.

## Test File Organization

**Location:**
- All tests live in the top-level `tests/` directory, separate from the source in `planspiel/`. There are no co-located tests.
- Shared helpers, constants and adapters live in `tests/support/`; fixtures for config and print tests live in `tests/fixtures/`.

**Naming:**
- `tests/test_<topic>.py`, where the topic matches a module or a requirement area: `test_rules_exact.py`, `test_overspend_gate.py`, `test_print_render.py`, `test_veil_cards_pdf.py`.
- Test functions: `test_<behaviour_in_snake_case>`, describing the rule or property: `test_wave_kz_change_rounds_once_half_away`, `test_clamp_kz`, `test_damage_euros_whole_euros_with_recovery`.
- Test classes are not used (no `class Test...` in `tests/`). Group by module and by function.

**Structure:**
```
tests/
  conftest.py              # pytest options (--update-golden, --planspiel-config, --planspiel-content-dir), session fixtures
  support/                 # REPO_ROOT, CONFIG_PATH, CONTENT_DIR, harness, golden, tex, candidate, pdf_text, ...
  fixtures/
    mini_config.json       # small config for enumeration and gate tests
    mini_content/          # content directory belonging to the mini config
    print/                 # smoke.tex.j2, smoke.tex used by print pipeline tests
  golden/                  # pinned reference data (*.json), updated only with --update-golden
  test_*.py                # 120 modules
```

## Test Structure

**Suite Organization:**
Function-based tests with module-level constants, module-scoped fixtures and parametrization. A typical rule test (from `tests/test_rules_exact.py`):

```python
@pytest.mark.parametrize(
    ("attack_delta", "event_kz", "expected"),
    [
        (Fraction(3, 2), 0, 2),
        (Fraction(3, 2), -7, -6),
        (Fraction(5, 2), 0, 3),
        (Fraction(-5, 2), 0, -3),
    ],
)
def test_wave_kz_change_rounds_once_half_away(attack_delta, event_kz, expected):
    assert wave_kz_change(attack_delta, event_kz) == expected
```

A test that needs the real config loads it from the repository (`tests/test_rules_exact.py`):

```python
def test_config_numbers_are_exact():
    cfg = load_config(CONFIG_PATH)
    weight = cfg.waves[0].weights["c"]
    assert isinstance(weight, Fraction)
    assert weight == Fraction(2, 5)
```

**Patterns:**
- Setup: module-scoped fixtures load configs once (`@pytest.fixture(scope="module") def mini(): return harness.load_config(MINI)` in `tests/test_overspend_gate.py`).
- Session-scoped fixtures for expensive artifacts: `printed_set` in `tests/conftest.py` runs the real `planspiel print` twice and returns both output directories so the tests can compare reproducibility.
- Teardown: `tmp_path` (pytest built-in) for every filesystem test; `tmp_path_factory.mktemp(...)` for session-scoped output. No manual cleanup.
- Assertions: exact equality on `Fraction`/`int` values; golden comparison for structured output (below); `pytest.raises(match=...)` for expected errors.
- Parametrize heavily: `@pytest.mark.parametrize("tier", TIERS)` with `TIERS = ("low", "medium", "high")` is the standard way to run a check on every budget tier (54 uses in `tests/`).

## Golden Files

- `tests/golden/*.json` pin reference outputs: `characterization_{low,medium,high}.json`, `gate_*.json`, `digest_*.json`, `answer_keys.json`, `welle0.json`, `worksheet_tex.json`.
- `tests/support/golden.py` compares values with a domain-readable diff. Fractions are serialised through `planspiel.rounding.exact_to_json` (exact decimals or `p/q`). Numeric noise above `NOISE_TOLERANCE = Fraction(1, 10**9)` is a failure. The diff shows at most `MAX_SHOWN_LINES = 30` lines.
- Rewrite only with `--update-golden`. The summary is printed under "golden updates (review before commit)" by `pytest_terminal_summary` in `tests/conftest.py`. Review every changed value before committing. Golden updates on a rules change must come with a RED-GREEN commit history.

## Mocking

**Framework:** none for game logic. `monkeypatch` (pytest built-in) is used for environment and module substitution in about 29 test modules; `unittest.mock` appears once (`tests/test_print_render_env.py`, to inject a bad job registry into `render.DOCUMENT_BUILDERS`).

**Patterns:**
```python
def test_...(monkeypatch, tmp_path):
    monkeypatch.setattr(render, "render_all", fake)   # only for the pipeline wiring, not for the rules
```

- The session fixture `printed_set` in `tests/conftest.py` monkeypatches `render.render_all` to add one injected smoke document, so the real pipeline runs with an extra job.
- Process and environment helpers (`tests/support/gitrepo.py`, `tests/support/peak_memory.py`) wrap real git and memory measurement rather than fakes.

**What to Mock:**
- Environment boundaries that cannot run here: a missing TeX engine (prefer skipping with `tex_skip_reason()` instead), a foreign registry used to test a validation error, the output directory of a print run.
- Only replace a wiring point (a registry or entry function), never a formula.

**What NOT to Mock:**
- The rules in `planspiel/rules.py`, the rounding in `planspiel/rounding.py`, the config loader and validator. The project rule is: no mocks for rules and no mocked database or integration; use the real config and real code.
- The config. Tests use `CONFIG_PATH` (the real `simulation_config.json`) or the small fixture `tests/fixtures/mini_config.json`, both through `harness.load_config`.
- Do not stub `texbuild`, `stamp` or `render` in pipeline tests to fake a result. Run the real pipeline or skip.

## Fixtures and Factories

**Test Data:**
- `tests/fixtures/mini_config.json` with `tests/fixtures/mini_content/` is a complete, small game config. Use it for enumeration, gate and balance logic where the full config is too large.
- `tests/fixtures/print/smoke.tex.j2` and `smoke.tex` drive the print pipeline smoke test (`SMOKE_TITLE` in `tests/conftest.py` contains the characters that must survive LaTeX escaping).
- `tests/support/ties.py` provides `write_tie_config(...)` and related helpers that build a config variant with a tie on purpose (writes a JSON file into `tmp_path`).
- `tests/support/harness.py` offers `load_config`, `selection_of(cfg, code)` (convert an enumeration code to a selection) and `evaluate(cfg, tier, selection)` (wrap `rules.evaluate_plan`).
- `tests/support/golden_cases.py` builds the named golden cases.

**Location:**
- Config and content fixtures: `tests/fixtures/`.
- Factories and adapters: `tests/support/`.
- Pinned outputs: `tests/golden/`.

**Real data preference:** the real `simulation_config.json` is used whenever a number is asserted. Synthetic configs are created only when the scenario needs a specific shape (ties, mutated tiers).

## Coverage

**Requirements:** None enforced. No coverage tool is configured (`pytest-cov` is not a dependency).

**View Coverage:** Not configured. Use `uv run pytest --collect-only -q | tail -3` for the test count.

## Test Types

**Unit Tests:**
- Pure rule functions with parametrized exact values: `tests/test_rules_exact.py`, `tests/test_rounding.py`, `tests/test_budget_review.py`, `tests/test_swap_layer.py`, `tests/test_kurswechsel.py`.
- Print model strings and veil rules without TeX: `tests/test_*_model.py`, `tests/test_*_render.py`, `tests/test_veil_*.py`.

**Integration Tests:**
- Full print pipeline without TeX (`tests/test_print_check.py`, `tests/test_print_stamp.py`, `tests/test_print_driver.py`).
- CLI commands through `planspiel.cli.main([...])` with real arguments (`tests/test_print_cli.py`, `tests/test_overspend_gate.py`).
- Config, content and clue checks on the real repository files (`tests/test_validate.py`, `tests/test_texts_coverage.py`, `tests/test_clues.py`, `tests/test_texts_digits.py`, `tests/test_texts_giveaway.py`).

**Slow tests (`@pytest.mark.slow`, 33 uses):**
- Full enumeration over all dependency-valid combinations per tier (782,336 combinations per the marker description in `pyproject.toml`). Run with `uv run pytest -m slow`. These are the authoritative balance checks, not hand-picked strategies.

**Balance tests (`@pytest.mark.balance`, 24 uses):**
- Phase-6 design-principle checks on the config chosen with `--planspiel-config`, defaulting to `simulation_config.json`. Use the `balance_config_path` and `balance_content_dir` session fixtures from `tests/conftest.py`; do not hard-code the config path in a balance test.
- Hand-calculation findings are errors. The clue mapping in `content/clues.toml` is mandatory.
- Whole-report verification is `uv run python balance_analysis.py --layers all --paths --jobs 3 --out build/balance`, not a single test.

**PDF tests (`@pytest.mark.pdf`):**
- Module-level marker `pytestmark = pytest.mark.pdf` (for example `tests/test_cards_pdf.py`, `tests/test_booklet_pdf.py`, `tests/test_master_pdf.py`).
- Skip reasons come from `tex_skip_reason()` in `tests/support/tex.py`: no `lualatex` on PATH, or a required MiKTeX package missing. A skip is not a pass; report it.

**E2E Tests:** Not used. The game is paper-only; the nearest equivalent is the printed-set run in `tests/conftest.py`.

## Common Patterns

**Expected errors:**
```python
def test_...():
    with pytest.raises(ValueError, match="Angriff-X"):
        render.render_all(None, None, tmp_path)
```

**Exact arithmetic checks:**
```python
def test_attack_kz_delta_exfil_slope():
    slope = kz_slope(-7, 10, 7)
    assert attack_kz_delta(-7, slope, 10, 10) == Fraction(-32, 7)
```

**Parametrized tiers:**
```python
TIERS = ("low", "medium", "high")

@pytest.mark.parametrize("tier", TIERS)
def test_...(tier):
    ...
```

**Golden comparison:** call `check_golden(...)` from `tests/support/golden.py` with the golden name; do not write ad-hoc JSON comparisons.

**Print tests:**
- Model tests check the strings a print model produces (`tests/test_cards_model.py`).
- Veil tests check that no player-facing string contains a giveaway term from `content/giveaway_terms.toml` (`tests/test_veil_cards.py`, `tests/test_veil_pdf.py`).
- Text tests check digits in prose against `content/digit_allowlist.toml` (`tests/test_texts_digits.py`).
- Freshness tests check that committed PDFs match the current inputs without TeX (`tests/test_print_check.py`).

**Async Testing:** Not applicable.

**Error Testing:** Use `pytest.raises` with `match=` on the German or English message fragment, not the full message.

## Rules for New Tests

- TDD for rules and simulation changes: write the failing test first, commit RED, then GREEN.
- Use the real config (`CONFIG_PATH`) or the mini config; no mocks for rules, config or validation.
- Put tests in `tests/test_<topic>.py`; mark `@pytest.mark.slow` for full enumerations and `@pytest.mark.pdf` for LuaLaTeX builds, and use the module-level `pytestmark` when a whole module needs a marker.
- Use `tmp_path` for every written file. Pass `encoding="utf-8"` to every text read and write (enforced by `tests/test_encoding_lint.py`).
- Do not run the full suite as a quick check. Run the single module, then `uv run pytest` for the fast suite before claiming done.

## Verification Before Completion

- Run `uv run pytest <file>` for the changed module.
- For config or formula changes also run `uv run planspiel validate`, `uv run planspiel gate` (or `gate --paths --jobs 3`) and the affected `-m balance` tests.
- For content or template changes run `uv run planspiel print` and `uv run planspiel print --check` (the PDF tests are a separate, slower step).
- Never claim a balance result from a hand-picked strategy; use the full enumeration.

---

*Testing analysis: 2026-11-09*
