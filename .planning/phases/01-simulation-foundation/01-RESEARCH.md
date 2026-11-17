# Phase 1: Simulation Foundation - Research

**Researched:** 2026-09-30
**Domain:** Python tooling and refactoring of a deterministic simulation (uv/pytest environment, characterization tests, exact integer arithmetic, memory-safe enumeration, config validation)
**Confidence:** HIGH (all performance, memory, diff and uv-layout claims were measured on this machine in this session; open points are flagged in Assumptions Log and Open Questions)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Paper rounding rule (FOUND-05)**
- **D-01:** Rounding happens at exactly one point: each wave's **KZ-Delta is rounded to a whole number**, and the waves are then summed. ("KZ-Delta" here = the wave total, see D-23.) The E-value, Gesamtreduktion, reduction above threshold and severity stay exact. The E-value always has ≤1 decimal because CIA values are integers and weights have 1 decimal.
- **D-02:** Rounding mode is **kaufmännisch, symmetric (half away from zero)**: +2,5 → +3, −2,5 → −3. Never use Python's `round()`, which rounds half to even. Use `Fraction`/`Decimal` with ROUND_HALF_UP semantics on the absolute value.
- **D-03:** **Damage stays exact in whole euros**, with no rounding. Budget units are thousands, so s_unit × severity (0,1 steps) × (1 − recovery 0,1/0,3/0,5) always ends in whole euros. RoS stays exact.
- **D-04:** The rounding helper is also the single place for the "per started 10.000 €" step logic that Phase 2 will need. Test it at the boundaries (exactly 10.000 €, 10.001 €, 0, negative).
- **D-05:** Sequencing: (1) pin the raw float outputs; (2) refactor into `planspiel/` with **zero snapshot diff**; (3) switch to exact arithmetic plus KZ rounding in a **separate commit** with an explicit, reviewed snapshot diff, in Phase 1 itself.
- **D-06:** Clamp KZ to 0…100 after applying the rounded wave delta, keeping the current order. The planner verifies that the order matches the current code.

**Characterization baseline (FOUND-02)**
- **D-07:** A **readable golden JSON per tier** with about 30–50 selections: the named strategies from `balance_analysis.py` `define_strategies`, boundary and dependency edge cases, and a fixed-seed random sample. All output fields are pinned (KZ, per-wave values, damage, costs, event effects, RoS).
- **D-08:** A **full digest** per tier: one hash over the canonical outputs of *all* combinations, which catches regressions the sample misses. It is opt-in via `@pytest.mark.slow` (`uv run pytest -m slow`), and the default `uv run pytest` stays fast.
- **D-09:** Over-budget selections are pinned at the `simulate_selection` level, including today's final-event behaviour (Budget Review −15 for negative remaining budget, event OPEX added to cost). That is the behaviour Phase 2 changes, so it needs a baseline.
- **D-10:** Intentional snapshot changes go through an explicit `uv run pytest --update-golden` flag. It rewrites the golden files and prints a diff summary: selection → field → old → new. The commit message states the reason. Tests never update silently.

**Enumeration report (FOUND-06)**
- **D-11:** "Over budget" keeps the **current definition**: `init + opex × waves + event opex > budget + event budget delta`. It lives in one function so that Phase 2 can swap the ledger (RULE-05/06).
- **D-12:** The report shows top-K three ways: **by final KZ, by RoS, by Final-Index**. Final-Index uses the current weights and is labelled provisional until the Phase 6 rescale. Percentiles cover KZ and RoS, split in-budget vs over-budget.
- **D-13:** "Best in-budget vs best over-budget" is compared on **final KZ**, the metric the RULE-04 overspend gate uses.
- **D-14:** The Pareto front is **final KZ vs total own cost**. Report its point count and the front points.
- **D-15:** Output is a small **per-tier JSON summary** (gitignored) plus a short console table. A full per-combination dump (JSONL) is written only on explicit request.
- **D-16:** The **old CLI keeps working**. `simulate_outcomes.py --budget-tier X --budget-utilization 0.85 --output file.json` still writes the full result, since `--output` counts as an explicit request. Without `--output`, the default is the new summary. `--budget-utilization` stays until Phase 6 drops it (BAL-03).
- **D-17:** Aggregation uses **compact in-memory per-combination tuples** (selection code, KZ, own cost, RoS, damage, in/over-budget flag), not true one-pass streaming. The user is getting a RAM upgrade, and tens of MB is fine. Phase 6 reuses the same tuples for its trim-back calibration sweep instead of re-enumerating.

**Refactor scope & cleanup (FOUND-03/04/07)**
- **D-18:** The old generators (`generate_pptx_cards.py`, `generate_from_template.py`, `generate_attack_calculator.py`) are **left untouched**. They contain no game formulas and are archived in Phase 7. At most, add a smoke/import check that they still load the umlaut-fixed config.
- **D-19:** FOUND-03's thin wrappers cover `simulate_outcomes.py`, `analyze_simulation_results.py` and `balance_analysis.py`. Their documented commands keep working via `uv run`.
- **D-20:** Umlauts: fix **display strings only** (name/description/text fields, e.g. "OT-Störung", "Geschäftsführung", "Unterstützung"). **Ids and keys stay ASCII** (`operative_unterstuetzung`, `ot`, `M1` …). A test fails if a display field contains a transliteration from an allow-list of known words.
- **D-21:** Validator: **broken references are hard errors on every config load**, so no script runs on a broken config. **Hand-calculability issues are warnings** in Phase 1: non-1-decimal KZ slope (flag wave 3 17/7), `base_severity != mitigation_cap`, `severity_multiplier != 1.0`, weights not summing to 1.0 or having >1 decimal, recovery >1 decimal. Warnings appear in pytest and via a standalone CLI (e.g. `uv run planspiel validate`), and Phase 6 promotes them to errors.
- **D-22:** Repo hygiene is already done: `sim_*.json` and `__pycache__` are untracked and gitignored, so `.planning/codebase/CONCERNS.md` is stale there. No git cleanup in this phase. `angriff_berechnung.xlsx` stays tracked until Phase 7.

**Plan-phase gap review (2026-09-30)**
- **D-23:** The rounded "KZ-Delta" of D-01 is the **wave total**: attack KZ-Delta + E-target bonus/malus + that wave's event KZ deltas, summed exactly, then rounded once per wave (half away from zero, D-02), then clamped (D-06). The final Budget Review is integer and applied after the waves. With today's config the only .5 tie is wave 3 at reduction-above-threshold 3.5 (attack KZ-Delta +1.5): e.g. −7 + 1.5 = −5.5 → −6. The golden set includes this tie with a negative and a positive wave total.
- **D-24:** One canonical semantics for all scripts = today's enumeration path in `simulate_outcomes.py`: final KZ includes the Budget Review; over-budget per D-11; RoS per README = (Σ base losses − damage − total cost) / total cost, with base losses = Σ base_severity × s_unit over waves (620) and total cost incl. event OPEX as today; ranking by Final-Index. `balance_analysis.py` adopts all of this. Its `combined_score`, its own budget check (init + 3·OPEX vs budget) and its simulated-baseline RoS are removed. Its printed numbers change on purpose; they are not pinned by golden files.
- **D-25:** Own cost (Pareto front D-14, tuple store D-17) = init + OPEX × waves, **excluding** event effects (RULE-06 "own spend"). The over-budget flag still follows D-11, and RoS keeps today's total cost incl. event OPEX until Phase 2.
- **D-26:** Legacy `--output` keeps writing today's JSON unchanged: in-budget only, `--budget-utilization`/`--budget-min`/`--budget-max` filters, same structure and sort, so `analyze_simulation_results.py` still reads it. The full per-combination dump incl. over-budget combos is a **new explicit flag** (JSONL, with an in/over-budget field). A run without `--output` writes the new summary (D-15/D-16).
- **D-27:** RoS is undefined (JSON `null`) when its cost denominator is 0 (today only the empty selection). Such entries are excluded from RoS top-K and percentiles; Final-Index falls back to KZ, as `compute_final_index` does today. (Today `analyze_simulation_results.py` divides by zero there.)
- **D-28:** The characterization baseline must not depend on the machine's code page. The config is read as UTF-8 before the golden capture (this machine's ANSI code page is 1252; today's `read_text()` in `simulate_outcomes.py` and `analyze_simulation_results.py` turns "früh" into "frÃ¼h"). Recommended order: FOUND-04 before FOUND-02. The old generators already read UTF-8.
- **D-29:** `generate_attack_calculator.py` re-encodes the wave formulas as Excel formulas (D-18's "no game formulas" does not hold for it). It still stays untouched (retired, archived in Phase 7 / LEG-01) and is a documented exception to FOUND-03's "exactly once" until then.
- **D-30:** FOUND-06's "within memory limits" becomes concrete: research measures peak memory and runtime per tier (this machine has 48 GB RAM; the timestamps of the existing `sim_*.json` files suggest roughly 1 min per tier for today's float enumeration, unverified), and the plan states measured bounds as acceptance criteria.

### Claude's Discretion
- Python version pin, dependency set and pins in `pyproject.toml`, and `planspiel/` module layout.
- The exact golden-set selection list and random seed, the digest canonicalization format, and the K for top-K.
- Whether arithmetic uses `Fraction` throughout or integer scaling (e.g. weights ×10), as long as results are exact and D-01…D-03 hold.
- Validator CLI naming and the warning output format.

### Deferred Ideas (OUT OF SCOPE)
- Dropping `--budget-utilization` / the 0.85 filter and rescaling Final-Index weights → Phase 6 (BAL-03).
- Promoting validator warnings to errors → Phase 6 (BAL-02).
- Redefining the budget/RoS ledger and Budget Review boundaries → Phase 2 (RULE-05/06/07).
- Reviewed todo `2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md` (veiling) is already assigned to Phase 3/5, not folded in.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FOUND-01 | One-command uv environment; all scripts via `uv run`, independent of Inkscape `python` | Q3: installable uv project (uv_build, flat layout, `[project.scripts]`), `.python-version` 3.12, `python-preference = "only-managed"`; fresh-clone run measured (6 s, works with Inkscape python first on PATH); README/CLAUDE.md command list |
| FOUND-02 | Characterization tests pin KZ/damage/costs/RoS per selection and tier before refactoring | Q4: harness that composes existing functions like the `run_simulation` loop body, golden JSON format, must-include cases with measured census, digest canonicalization, `--update-golden` |
| FOUND-03 | Every formula exactly once in `planspiel/`; root scripts thin wrappers | Q6: inventory of duplicated/divergent formulas; module layout; AST guard tests for "exactly once" and "thin wrapper" |
| FOUND-04 | UTF-8 config reads everywhere; real umlauts in German display strings | Q7: inventory of transliterated strings, allow-list, which strings reach outputs; encoding lint; console encoding trap |
| FOUND-05 | Exact arithmetic + one tested rounding/step helper matching paper | Q1/Q5: integer scaling benchmark, `round_half_away`/`started_steps`, exact-switch diff experiment over all 3×782,336 combinations |
| FOUND-06 | Full enumeration incl. over-budget within measured bounds; compact aggregates; dump only on request | Q1/Q2: kernel timing, struct-of-arrays vs tuples memory, measured acceptance bounds, report design |
| FOUND-07 | Validator rejects broken references; warns on hand-calc violations | Q8: full check list for the current schema, warning surfacing in pytest/CLI, today's expected warnings |
</phase_requirements>

## Summary

Phase 1 is a tooling and refactoring phase on a small, fully deterministic Python code base (three scripts, ~1,300 lines, stdlib only). Everything the planner needs was measured on this machine with the uv-managed CPython 3.12.14. The current float loop takes roughly 70-130 s per tier (782,336 dependency-valid selections of 1,048,576; in-budget 69,454 / 124,321 / 197,753 for low / medium / high). A naive `Fraction` port is 3-5x slower (about 6 min per tier) and would make the D-08 digest painful. An integer-scaled kernel with precomputed per-measure-level contributions is faster than today's float code (about 37 s per tier, measured on all three tiers) and is exact. Recommended: integer scaling (weights ×10, recovery ×100, all derived from the config by LCM of denominators), `Fraction` only at the output boundary.

The exact-switch experiment (all three tiers, every valid combination, float legacy vs exact + D-23 rounding) shows that the switch is small and explainable: 0 flips of the E-target check, 0 flips of the over-budget flag, 0 damage differences beyond float noise (179,084 combinations per tier carry float noise below 0.5 €), and final KZ changes for 121,306 / 168,625 / 194,360 combinations (15.5% / 21.6% / 24.8%), all of them the combinations whose legacy KZ was fractional; about 2% move by a full point or more because rounding accumulates per wave. **One D-23 requirement cannot be met literally:** the wave-3 tie at reduction 3.5 occurs in 1,050 combinations per tier, but *always with a positive wave total* (the E-target is always reached there), so no real (tier, selection) pair produces the negative tie −5.5. It must be covered by helper unit tests plus a test-only tier override (see Open Question 1).

The uv project should be installable (uv_build backend, flat layout `module-root = ""`, `[project.scripts] planspiel = "planspiel.cli:main"`). This makes `uv run planspiel validate` (D-21) real; without a build system it works only by accident from the repo root. A fresh copy with the Inkscape Python first on PATH ran `uv run --locked pytest` in 6 s. Memory for the D-17 store: 20 bytes/combination with `array` (15.6 MB per tier, 213 MB peak process with unoptimised aggregation) versus 284 MB peak with a list of tuples; both are far below the 48 GB available, so the acceptance bounds below are generous but concrete.

**Primary recommendation:** Build `planspiel/` in the order FOUND-01 → FOUND-04 → FOUND-02 → FOUND-03 → FOUND-07 → FOUND-05 → FOUND-06 (one PLAN.md each). Use integer-scaled arithmetic in one `rules` module whose primitives are shared by the rich (dict/golden) path and the lean enumeration kernel; keep floats only until the D-05 step-3 commit.

## Architectural Responsibility Map

This is an offline batch/CLI code base, not a multi-tier application. "Tiers" here are code layers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Config load (UTF-8, exact numbers) + validation | `planspiel.config` / `planspiel.validate` | root wrappers (call only) | One loader means no script can run on a broken or mis-decoded config (D-21, D-28) |
| Game formulas (E-value, reduction, severity, KZ delta, rounding, events, costs, RoS, Final-Index) | `planspiel.rules` (+ `planspiel.rounding`) | — | FOUND-03: exactly once; enumeration kernel and rich path share the primitives |
| Full enumeration, aggregates, report | `planspiel.enumerate` / `planspiel.report` | `planspiel.rules` | Needs the lean kernel; must not duplicate formulas |
| CLI argument parsing and console output | `planspiel.cli` (thin) | root wrappers `simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py` | Documented commands keep working; wrappers contain no logic (D-19) |
| Characterization baseline | `tests/` (golden JSON, digest) | `tests/support/` harness | Pins behaviour independent of implementation; swapped adapter between D-05 steps 1 and 2 |
| Legacy generators (pptx/xlsx) | untouched root scripts | smoke test only | D-18/D-29; archived in Phase 7 |
| Environment | `pyproject.toml`, `uv.lock`, `.python-version` | README/CLAUDE.md commands | FOUND-01 |

## Standard Stack

### Core
| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| CPython (uv-managed) | 3.12.14 (already installed via uv) `[VERIFIED: uv python list]` | Runtime; `.python-version` = `3.12`, `requires-python = ">=3.12"` | Managed by uv, no python.org installer, independent of Inkscape 3.12.9 and Store 3.11.7 |
| uv | 0.12.5 installed (0.12.21 latest on PyPI `uv-build`) `[VERIFIED: uv --version, PyPI]` | env, lockfile, command runner | Already installed; `uv run` never touches PATH python |
| uv_build | `>=0.12.21,<0.13` per uv docs `[CITED: docs.astral.sh/uv/concepts/build-backend/]` (tested with `>=0.12`, resolved 0.12.21) | Build backend so the project is installed editable and `[project.scripts]` works | `[CITED: docs.astral.sh/uv/concepts/projects/config/]`: "Using the entry point tables requires a build system to be defined." Flat layout: `module-root = ""`, `module-name = "planspiel"` |
| pytest | 9.1.1 (2026-06-19) `[VERIFIED: PyPI + installed in test project]` | Test runner | Project standard (STACK.md) |
| stdlib only for simulation | `fractions`, `decimal`, `hashlib`, `array`, `heapq`, `itertools`, `json`, `argparse` | Exact arithmetic, digest, compact store, aggregation | No new dependency needed for any Phase 1 capability (measured) |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| openpyxl | 3.1.5 (2024-06-28) `[VERIFIED: PyPI]` | Only so the untouched legacy generators still import (D-18 smoke test) | Runtime dependency until Phase 7 archives the generators; remove then |
| python-pptx | 1.0.2 (2024-08-07) `[VERIFIED: PyPI]` | Same as above | Same as above |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| uv_build + `[project.scripts]` | No `[build-system]`, `uv run python -m planspiel validate` | Simpler pyproject, but `uv run planspiel validate` then only "works" from the repo root by accident on Windows (verified: `program not found` from any subdirectory). STACK.md chose no build system for a flat repo; this research recommends the build system because D-21 names the CLI and Phase 4 adds another command |
| stdlib `array` store | list of tuples | Tuples: 284 MB peak, simplest code; `array`: 213 MB peak (mostly aggregation temporaries; 15.6 MB payload). Both fine on 48 GB; `array` matches D-17's "tens of MB". Hide the choice behind a small `ResultStore` class |
| psutil for peak memory | ctypes/`resource` helper (stdlib, 20 lines, verified) | Avoids a new dependency |
| syrupy (STACK.md) | hand-rolled golden JSON + `--update-golden` | D-10 wants a domain-readable "selection → field → old → new" summary, which syrupy does not give; keep the hand-rolled harness for FOUND-02 |

**Installation (repo root, run by the plan, not by research):**
```bash
uv python pin 3.12          # writes .python-version
uv add openpyxl==3.1.5 python-pptx==1.0.2
uv add --dev pytest==9.1.1
uv sync                     # fresh clone: `uv sync` or simply `uv run pytest`
```

**Version verification:** pytest 9.1.1, openpyxl 3.1.5, python-pptx 1.0.2 were read from the PyPI JSON API on 2026-09-30; pytest 9.1.1 was installed by `uv sync` in a scratch project.

## Package Legitimacy Audit

Seam: `gsd-tools query package-legitimacy check --ecosystem pypi ...`. **All verdicts are `SUS` for the same reason: `unknown-downloads`** (the PyPI JSON API returns no weekly download statistics, so the seam cannot rate downloads). No package has a `postinstall` signal, a missing repo, or a deprecation flag. `uv-build` additionally reports `too-new` because its latest release was published 2026-09-29; the package itself is Astral's official backend.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| pytest | PyPI | 15+ yrs (9.1.1 on 2026-06-19) | n/a (seam: unknown) | github.com/pytest-dev/pytest | SUS (data gap only) | Approved with one human-verify checkpoint (see below) |
| openpyxl | PyPI | 15+ yrs (3.1.5 on 2024-06-28) | n/a | foss.heptapod.net/openpyxl/openpyxl | SUS (data gap only) | Approved; already used by the repo's generators; checkpoint |
| python-pptx | PyPI | 10+ yrs (1.0.2 on 2024-08-07) | n/a | github.com/scanny/python-pptx | SUS (data gap only) | Approved; already used by the repo's generators; checkpoint |
| uv-build | PyPI | official Astral backend (docs.astral.sh) | n/a | github.com/astral-sh/uv | SUS (`too-new` = latest release yesterday, `unknown-downloads`) | Approved; named in official uv docs; checkpoint |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** pytest, openpyxl, python-pptx, uv-build. Per protocol the planner adds **one** `checkpoint:human-verify` task in the FOUND-01 plan before the first `uv add`/`uv sync`, covering all four (the user recognises all four; `uv.lock` records hashes afterwards). `psutil` was used only in throwaway experiments and is **not** recommended for the project.

`[ASSUMED]` none: every package above was found in official documentation or is already used by the repo.

## Architecture Patterns

### System Architecture Diagram

```
simulation_config.json (UTF-8, ASCII ids, German display strings with umlauts)
        │  planspiel.config.load_config()   ── json.loads(parse_float=Fraction), encoding="utf-8"
        ▼
   validate(raw) ──errors──► ConfigError (hard stop, every load)          ┌── warnings ──► pytest summary / `planspiel validate`
        │ ok (+ HandCalcWarning for 17/7 etc.)  ───────────────────────────┘
        ▼
   Config (dataclasses; scale factors WS/RS derived from denominators)
        │
        ├────────────► rules.* primitives (integer-scaled, single definition)
        │                 e_value, gesamtreduktion, reduction_above_threshold, severity,
        │                 attack_kz_delta, wave_total → round_half_away → clamp, events,
        │                 costs, over_budget(), ros(), final_index()
        │                         ▲                         ▲
        │             rich path (dicts, Fraction     lean kernel (ints only, no dicts)
        │             at the boundary)                       │
        │                         │                         ▼
        │                 tests golden (30-55 selections)   enumerate_tier(): 782,336 valid combos
        │                 + `--update-golden` diff           │  append to ResultStore (array SoA, 20 B/record)
        ▼                                                     ▼
 root wrappers (3 lines each)                     report: top-K x3, percentiles, best in/over,
 simulate_outcomes.py  ─ --output ─► legacy JSON      Pareto(KZ vs own cost) → per-tier summary JSON + console table
 analyze_simulation_results.py ◄─ legacy JSON        --dump-jsonl (explicit): every combo incl. in/over flag
 balance_analysis.py (canonical semantics D-24)
```

### Recommended Project Structure
```
planspiel/
├── __init__.py
├── cli.py            # main() for `planspiel validate`; shared helpers (utf-8 stdout)
├── config.py         # load_config (utf-8, Fraction), dataclasses, ConfigError
├── validate.py       # Issue(level, code, path, message), validate(raw), HandCalcWarning
├── rounding.py       # round_half_away, started_steps (D-04), exact_to_json/from_json
├── rules.py          # every formula, once (float in D-05 step 2, integer-scaled in step 3)
├── enumerate.py      # iter_selections, kernel, ResultStore, enumerate_tier
├── report.py         # top-K, percentiles (nearest rank), Pareto, summary JSON, console table
└── legacy_output.py  # writes/reads the D-26 legacy results JSON (run_simulation shape)
simulate_outcomes.py, analyze_simulation_results.py, balance_analysis.py   # thin wrappers
tests/
├── conftest.py       # --update-golden option, terminal summary hook
├── support/          # golden.py (compare/update/diff), legacy_harness.py, digest.py, peak_memory.py
├── golden/           # characterization_{low,medium,high}.json, digest_{low,medium,high}.json
├── fixtures/         # mini_config.json (2-3 measures), broken_*.json
└── test_*.py
pyproject.toml, uv.lock, .python-version   # committed; .venv/, .pytest_cache/ gitignored
```

### Pattern 1: Integer scaling with derived scale factors (recommended, Q1)
**What:** At config load compute `WS` = lcm of the weight denominators (10 today), `RS` = lcm of recovery denominators (10 today), then evaluate wave math in integers: `E_s = C*wc_s + I*wi_s + A*wa_s`; `r_s = clamp(E_s + bonus*WS − thr*WS, 0, cap*WS)`; `sev_s = max(0, base_sev*mult*WS − r_s)`; damage in whole euros = `sev_s * s_unit * 1000 * (RS − rec_s) / (WS*RS)` (assert exact division); attack KZ delta as the integer fraction `(kz_dmg*cap_s + r_s*span) / cap_s`; wave total = `(attack_num + cap_s*(e_target_delta + event_kz)) / cap_s`; round with `round_half_away(n, d)`; clamp. **Why:** exact, no `Fraction` objects in the hot loop, 47 µs/selection measured. `Fraction` only when building dicts for golden/report.
**Validator link:** the loader must reject configs where scaling is not integral (weights/recovery/multiplier not finite decimals, damage not whole euros); see Q8.

### Pattern 2: One rules module, two callers (rich path and lean kernel)
The lean kernel must call the *same primitive functions* (or be generated from them) so FOUND-03 "exactly once" holds. Precompute per-measure-level tables (`cia`, `init`, `opex`, `recovery` as ints) once per tier and evaluate events through precompiled closures. A conformance test compares kernel and rich path on the golden sample and on the first N thousand combinations; the slow digest test covers all.

### Pattern 3: Adapter-swap characterization (D-05)
`tests/support/legacy_harness.py::evaluate(selection, tier)` is the only function the golden tests call. Step 1: it composes the legacy `simulate_outcomes` functions exactly like the `run_simulation` loop body (see Q4). Step 2: its body is replaced by a call into `planspiel.rules`; golden JSON is untouched and must still match with `==` (floats compare bit-exact; JSON `repr` round-trips floats losslessly). Step 3: exact values; golden regenerated via `--update-golden`.

### Anti-Patterns to Avoid
- **Reordering float operations during the D-05 step-2 refactor:** breaks the zero-diff guarantee at the last bit. Move code verbatim; change types only in step 3.
- **Holding per-combination dict trees:** one legacy outcome is ≈6 KB (measured 6,040 B); 782,336 of them ≈ 5 GB per tier, and legacy `run_simulation` already holds all in-budget ones (0.4-1.3 GB).
- **Python `round()` anywhere in `planspiel`:** half-to-even. Add an AST test forbidding it (except in display-only formatting).
- **Text-mode I/O without `encoding=`:** the machine default is cp1252 here. Add an AST test.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Exact decimal parsing of config numbers | float math + tolerance | `json.loads(..., parse_float=Fraction)` (receives the literal text, so `0.4` → `2/5` exactly) | Removes float noise at the source |
| Half-away-from-zero rounding | `round()` / ad-hoc `+0.5` | `round_half_away(n, d)` integer function (below) | Half-to-even and sign bugs are the classic failure |
| Digest | custom checksum | `hashlib.sha256` fed with canonical text lines in enumeration order | Standard, stable |
| CLI dispatch | manual `sys.argv` | `argparse` (already used) | Existing pattern |
| Golden diff summary | raw JSON diff | small flatten-and-compare helper producing "selection → field → old → new" | D-10; ~40 lines |
| Peak memory | psutil | 20-line stdlib helper (Code Examples) | No new dependency |
| Env bootstrap | Makefile / scripts | `uv sync` / `uv run` | FOUND-01 |

**Key insight:** every hard part here (exactness, hashing, aggregation) is solvable with the standard library; the risk is semantic (which formula, which unit, which order), not technical.

## Runtime State Inventory

This phase refactors and fixes display strings (umlauts), so the inventory applies.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `sim_low.json` (131 MB), `sim_med.json` (237 MB), `sim_high.json` (362 MB) in repo root: gitignored outputs of the legacy code. Bytes/record math (131,267,826 B / 69,454 in-budget low combos ≈ 1.9 KB) is consistent with unfiltered in-budget runs. They contain pre-fix strings and pre-exact floats. | None in git. Treat as stale, never as baseline; regenerate or delete after Phase 1. Never read whole (CLAUDE.md). |
| Live service config | None: no external services. | None |
| OS-registered state | None. | None |
| Secrets/env vars | None. `PYTHONUTF8` is not set; nothing depends on env. | None |
| Build artifacts | `__pycache__/` (gitignored). After Phase 1: `.venv/`, `.pytest_cache/`, `uv.lock` (committed). `angriff_berechnung.xlsx` (tracked) was built from the config with the wave name "OT-Stoerung" as sheet title; it goes stale after the umlaut fix but D-22/D-29 keep it untouched until Phase 7. | Add `.venv/`, `.pytest_cache/`, `simulation_summary*.json`, `simulation_full*.jsonl` to `.gitignore`. Do not regenerate the xlsx. |

**Repo references to the transliterated names:** a repo-wide search of `*.py`/`*.md` outside `archive/` and `.planning/` finds none (generators hard-code "OT-Störung" with the umlaut already). So the display-string fix has no downstream key dependency. `[VERIFIED: grep]`

## Common Pitfalls

### Pitfall 1: Windows code page corrupts config text and console output
**What goes wrong:** `Path.read_text()` decodes as cp1252 (ANSI 1252 verified): "früh" → "frÃ¼h". Separately, piped stdout is also cp1252: `print('Störung')` emits byte 0xF6 (garbage in a UTF-8 terminal) and `print('−')` or `'≥'` raises `UnicodeEncodeError` (verified).
**How to avoid:** explicit `encoding="utf-8"` on every text read/write (`write_text(..., encoding="utf-8", newline="\n")`); CLI entry points call `sys.stdout.reconfigure(encoding="utf-8")` (and stderr) once; AST test bans text-mode `open`/`read_text`/`write_text` without `encoding` in `planspiel/`, the three wrappers and `tests/`. Legacy `--output` JSON keeps default `ensure_ascii=True` (machine-independent).
**Warning signs:** `Ã` or `â€` in any string; golden files that differ between machines.

### Pitfall 2: The D-23 negative tie is unreachable in the real config
**What goes wrong:** the plan promises a golden case "tie with negative wave total"; no such selection exists (details in Q5). The implementer searches for hours or silently drops the case.
**How to avoid:** cover negative half-away rounding with `round_half_away` unit tests (−5.5 → −6, −2.5 → −3, −0.5 → −1) and a test-only override (tier copy with wave-3 `e_targets["3"]` raised above any reachable E, e.g. 40) evaluated at step 3. Positive ties: use the census examples (Q4).

### Pitfall 3: KZ = 100 plateau makes "top-K by KZ" meaningless without tie-breaks
Measured: 7,013 / 16,651 / 28,095 combinations end at exactly 100 (low/medium/high), and 372k-626k combinations hit the wave-level upper clamp. Legacy `results.sort` breaks ties by damage then enumeration order. Define the report's tie-break explicitly (see Assumptions A4) and keep legacy sort for `--output` (D-26).

### Pitfall 4: Legacy `--budget-max` does not cap anything
In `run_simulation`, `max_cost` (= `--budget-max` or tier budget) only feeds `utilization_threshold`; the upper filter is `total_cost > adjusted_budget`. The README documents `--budget-max 380` as a hard limit. D-26 says "unchanged". Preserve the behaviour, pin it in a test, and record it as a known quirk (Open Question 2).

### Pitfall 5: Over-budget selections never reach final events in legacy code
`run_simulation` applies Budget Review and the cost dict only after the budget filter. A harness that calls `simulate_selection` alone would silently skip final events and cost logic (D-09). Compose the full loop body (Q4).

### Pitfall 6: Zero-cost division
Empty selection: total cost 0. `analyze_simulation_results.py` raises `ZeroDivisionError`; `balance_analysis.calculate_ros` returns 0.0. Canonical (D-27): `None`, excluded from RoS statistics, Final-Index = KZ.

### Pitfall 7: `uv run planspiel validate` only works by accident without a build system
Verified: with `planspiel/__main__.py` and no `[build-system]`, `uv run planspiel validate` runs from the repo root (Windows resolves the directory) and fails with `Failed to spawn: planspiel — program not found` from any subdirectory. Use the installable layout.

### Pitfall 8: pytest `-m` and `--update-golden` plumbing
`addopts = "-m 'not slow' --strict-markers"` plus a CLI `-m slow` works (last `-m` wins; verified). `pytest_addoption` in `tests/conftest.py` works with `testpaths = ["tests"]` (verified). Register the `slow` marker or `--strict-markers` fails.

### Pitfall 9: golden file line endings and floats
Write golden files with `newline="\n"`, `ensure_ascii=False`, `indent=2`, trailing newline; add `tests/golden/*.json text eol=lf` to `.gitattributes`. Compare parsed JSON, never text. Legacy floats round-trip exactly through `json` (repr), so compare with `==`.

## Code Examples

### Rounding and step helpers (D-01, D-02, D-04) - integer only
```python
# planspiel/rounding.py
from fractions import Fraction

def round_half_away(n: int, d: int = 1) -> int:
    """n/d (d > 0) rounded to a whole number, half away from zero (kaufmännisch)."""
    if n >= 0:
        return (2 * n + d) // (2 * d)
    return -((-2 * n + d) // (2 * d))

def round_half_away_frac(x: Fraction) -> int:
    return round_half_away(x.numerator, x.denominator)

def started_steps(amount_eur: int | Fraction, step_eur: int = 10_000) -> int:
    """Number of started steps: 0 for amount <= 0, 1 for 0 < amount <= step, 2 for step < amount <= 2*step ...
    Exactly 10.000 EUR -> 1; 10.001 EUR -> 2; 0 -> 0; negative -> 0.  (ASSUMPTION A1: ceil semantics)"""
    if amount_eur <= 0:
        return 0
    return -((-amount_eur) // step_eur)          # ceil; works for int and Fraction (verified)
```
Boundary tests (all verified in a scratch run): `round_half_away(11, 2) == 6`, `(-11, 2) == -6`, `(5, 2) == 3`, `(-5, 2) == -3`, `(-3, 2) == -2`, `(1, 2) == 1`, `(-1, 2) == -1`, `(0, 1) == 0`, `(3, 7) == 0`, `(-3, 7) == 0`; `started_steps` for 10000 / 10001 / 0 / −5000 / 1 / 20000 / 20001 → 1 / 2 / 0 / 0 / 1 / 2 / 3; `exact_to_json` for 56/25 → `"2.24"`, −56/25 → `"-2.24"`, 17/7 → `"17/7"`, 1/20 → `"0.05"`, −1/2 → `"-0.5"`, 3 → `3`, each decoding back with `Fraction(str)`.

### Exact values in JSON (Q5)
```python
def exact_to_json(x):
    """int -> int; finite decimal -> "2.24"; otherwise "p/q". Fraction(str) parses all of them back."""
    x = Fraction(x)
    if x.denominator == 1:
        return int(x)
    d, twos, fives = x.denominator, 0, 0
    while d % 2 == 0: d //= 2; twos += 1
    while d % 5 == 0: d //= 5; fives += 1
    if d != 1:
        return f"{x.numerator}/{x.denominator}"
    digits = max(twos, fives)
    scaled = x * 10**digits                      # integer
    sign = "-" if scaled < 0 else ""
    s = str(abs(int(scaled))).rjust(digits + 1, "0")
    return f"{sign}{s[:-digits]}.{s[-digits:]}"
```

### `--update-golden` plumbing (D-10)
```python
# tests/conftest.py
import pytest

def pytest_addoption(parser):
    parser.addoption("--update-golden", action="store_true", default=False,
                     help="rewrite tests/golden/*.json and print a selection -> field -> old -> new summary")

@pytest.fixture
def update_golden(request):
    return request.config.getoption("--update-golden")

_REPORT: list[str] = []
@pytest.fixture
def golden_report():
    return _REPORT

def pytest_terminal_summary(terminalreporter):
    if _REPORT:
        terminalreporter.section("golden updates (review before commit)")
        for line in _REPORT[:200]:
            terminalreporter.write_line(line)
        if len(_REPORT) > 200:
            terminalreporter.write_line(f"... {len(_REPORT) - 200} more lines")
```
`support/golden.py::check(tier, actual, update, report)`: flatten both sides (`waves[2].kz_after`), on mismatch either fail with the first N lines or (with `--update-golden`) rewrite and append `"<key> | <field> | <old> -> <new>"` lines. Classify numeric changes where `abs(old - new) < 1e-9` as "noise cleanup" and aggregate them per field name (thousands of lines otherwise, D-05 step 3).

### pyproject.toml (verified layout)
```toml
[project]
name = "security-planspiel"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["openpyxl==3.1.5", "python-pptx==1.0.2"]   # legacy generators only; drop in Phase 7

[project.scripts]
planspiel = "planspiel.cli:main"

[build-system]
requires = ["uv_build>=0.12.21,<0.13"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-root = ""
module-name = "planspiel"

[tool.uv]
python-preference = "only-managed"

[dependency-groups]
dev = ["pytest==9.1.1"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]          # root wrappers are importable in tests
addopts = "-m 'not slow' --strict-markers"
markers = ["slow: full 782,336-combination checks per tier, run with `uv run pytest -m slow`"]
```
`.python-version`: `3.12`. `.gitignore` additions: `.venv/`, `.pytest_cache/`, `simulation_summary*.json`, `simulation_full*.jsonl`. Add `tests/golden/*.json text eol=lf` to `.gitattributes`.

### Peak-memory helper (stdlib, verified on Windows)
```python
# tests/support/peak_memory.py
import sys
def peak_rss_bytes() -> int:
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        class PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
        k32 = ctypes.WinDLL("kernel32", use_last_error=True); psapi = ctypes.WinDLL("psapi", use_last_error=True)
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        pmc = PMC(); pmc.cb = ctypes.sizeof(PMC)
        if not psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return pmc.PeakWorkingSetSize
    import resource
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss * 1024 if sys.platform.startswith("linux") else rss
```
Run the memory-bound test in a **subprocess** (`sys.executable -m planspiel...`) so the peak belongs to the enumeration only. Do not use `tracemalloc` for this: it slowed the enumeration 10x (420 s instead of 40 s; traced peak 184 MB).

### Encoding lint (FOUND-04)
AST-walk `planspiel/**/*.py`, the three wrappers and `tests/**/*.py`: fail on `open(...)` in text mode, `Path.read_text(...)`, `Path.write_text(...)` without an `encoding=` keyword, and on `round(` calls in `planspiel/rules.py`/`rounding.py`.

## Research Answers (Q1-Q9)

### Q1. Exact arithmetic and speed (measured, uv CPython 3.12.14, this machine)

Dependency-valid selections per tier: **782,336** of 1,048,576 (same for all tiers; tiers differ only in budget/KZ start). In-budget: 69,454 / 124,321 / 197,753; over-budget: 712,882 / 658,015 / 584,583 (low/medium/high). Full loop = `dependencies_satisfied` + `compute_costs` + `simulate_selection` + event OPEX/budget + final events for in-budget selections (as in `run_simulation`, without JSON output):

| Variant | µs/selection | Full tier | Notes |
|---|---|---|---|
| (a) today's float code (legacy functions) | 90-165 (varies with machine load) | **70-130 s** (77/129/126 s parallel, 115/81/70 s single runs) | Matches D-30's "roughly 1 min" guess within 2x. Timestamps of `sim_*.json` (01:26-01:28) agree |
| (b1) naive `Fraction` port of the same code (dicts kept) | ~460 | ~6 min (est. from 20k sample) | 3-5x slower; makes the D-08 digest ≈ 18 min for 3 tiers |
| (b2) `Fraction` kernel, precomputed tables, no dicts | ~261 | ~3.4 min (est. from 30k sample) | Still slower than float |
| **(c) integer-scaled kernel, precomputed per-measure-level tables** | **~47** (one outlier run 18) | **~37 s** (36.3 / 37.2 / 36.7 s, full, 3 tiers) | Exact; recommended |

**Recommendation:** integer scaling as in Pattern 1, with scale factors derived from the config. Precomputing per-measure-level contributions is cheap and already assumed in (c). The kernel reproduced the legacy in-budget counts exactly (69,454 / 124,321 / 197,753) and all discrete outcomes (Q5). Memoising wave results was not needed.

### Q2. Memory of the D-17 store and acceptance bounds for FOUND-06 (D-30)

Measured for 782,336 records (medium tier, kernel + store + full aggregation: three top-K rankings, percentiles, best in/over, Pareto):

| Variant | Enumeration | Aggregation | Peak working set | Payload |
|---|---|---|---|---|
| kernel only, no store | 47 s | - | 22 MB | - |
| list of 6-tuples `(code, kz, own_cost, ros, damage, over)` | 38 s | 2.7 s | **284 MB** | ~160 MB above baseline (~235 B/record) |
| `array` struct-of-arrays (`I` code, `B` kz, `H` own cost, `d` ros, `I` damage, `B` flag) | 41 s | 5.4 s | **213 MB** (mostly aggregation temporaries: index lists, sorted copies) | **15.6 MB** (20 B/record) |

Legacy reference: one outcome dict tree ≈ 6 KB, so a naive "keep everything incl. over-budget" run would need ≈ 5 GB per tier. Legacy in-budget-only lists are 0.4 / 0.8 / 1.3 GB.

**Proposed acceptance bounds (2.5x headroom over measured, for this machine):**
1. Full enumeration + report for one tier ≤ **120 s** wall clock (measured 40-46 s); all three tiers sequentially ≤ 6 min.
2. Peak working set of the enumeration process ≤ **500 MB** (measured 213 MB with `array`, 284 MB with tuples).
3. Store payload ≤ **32 bytes per combination** (measured 20 B; assert via `array.itemsize` sum, machine independent).
4. Legacy `--output` of an in-budget-only run is I/O-bound and excluded from bounds; the JSONL dump likewise.
5. Measured numbers are recorded in the plan SUMMARY; bounds apply to the machine documented there (Windows 11, 48 GB, CPython 3.12.14).
Automated: a `slow` test runs `python -m planspiel...` (or the wrapper) for `low` in a subprocess, checks time and `peak_rss_bytes()` from inside the child (print it, parse it), and asserts the report fields. Recommendation for D-17: `array` behind a small `ResultStore` (append/len/record(i) → namedtuple), with the tuple layout of D-17 as the logical record. Phase 6 reads `ResultStore` unchanged.

Report values measured with the prototype (exact + D-23 rounding, own cost excluding event effects, Budget Review included); use them as expected values after FOUND-05, not before: best in-budget final KZ = 100 in all tiers, best over-budget = 85 in all tiers; Pareto (KZ vs own cost) front sizes **22 / 23 / 25** (low/medium/high).

### Q3. uv project layout

Decision: **installable project** (verified end to end in scratch projects; nothing was created in the repo).
- `uv sync` created `.venv`, `uv.lock` and installed the project editable (`security_planspiel.pth`); edits to `planspiel/cli.py` took effect immediately.
- `uv run planspiel validate` works from any subdirectory; `uv run python root_script.py` imports `planspiel` (script dir is on `sys.path`); `uv run pytest` works with `pythonpath = ["."]`.
- Fresh-clone simulation (files copied, no `.venv`, `PATH` with Inkscape first): `uv run --locked pytest -q` → 6 s, interpreter = managed 3.12.14. `uv python find` with `only-system` cannot even inspect Inkscape's Python ("Can't use Python"), so it cannot be picked accidentally; `python-preference = "only-managed"` makes that explicit.
- Python pin: `.python-version` `3.12`, `requires-python = ">=3.12"` (3.12 is already managed on this machine; STACK.md allowed 3.12 or 3.13; 3.13 would need a download).
- Dependency set: runtime `openpyxl==3.1.5`, `python-pptx==1.0.2` (only for legacy generator smoke test until Phase 7); dev `pytest==9.1.1`. No psutil, no syrupy.
- One setup command: `uv sync` (or just `uv run pytest`, which syncs). Documented run form: `uv run python simulate_outcomes.py ...` (also `uv run simulate_outcomes.py ...` works).

Commands/documentation that must change to `uv run ...` (success criterion 1):
- `README.md` lines 213, 220, 225, 230, 235 (`python3 ...` → `uv run python ...`); add a short "Setup: `uv sync`" line above them.
- `CLAUDE.md` (root) line 52 (`simulate_outcomes.py --budget-tier ... --output <file>` without interpreter) and line 53/56 mentions; add `uv run` prefix and the new summary default.
- `.claude/CLAUDE.md` (auto-generated codebase sections, stale): lines 37-40 and 66 say "no version pin", "manual `pip install openpyxl python-pptx`"; line 53 claims `analyze` imports from `simulate_outcomes` (it does not). Fix only the environment lines in Phase 1; the rest is LEG-02.
- `.planning/codebase/*.md` are stale; do not touch.
Wrappers keep their shebang and work under plain `python3` only if `planspiel` is importable; the documented path is `uv run`.

### Q4. Characterization harness (FOUND-02)

**Harness:** `tests/support/legacy_harness.py::evaluate(cfg, tier, selection)` composes, in this order, exactly what the `run_simulation` loop does: `dependencies_satisfied` → `compute_costs(..., len(waves))` → `simulate_selection` → `total_cost += total_event_opex` → `adjusted_budget = tier.budget + total_event_budget` → `over_budget = total_cost > adjusted_budget` → `remaining = adjusted_budget - total_cost` → for each final event `evaluate_event(event, selection, remaining_budget=remaining)` with `kz_final = max(0, min(100, kz_final + ev_kz))` → `costs` dict. RoS (harness-level, mirrors `analyze`): `base_losses = load_base_losses(config)` (620), `ros = (base_losses - total_damage - total_cost) / total_cost`, `None` if `total_cost == 0`. This avoids modifying legacy code before the pin (no extraction needed). A behaviour-preserving extraction into `planspiel.rules.evaluate_plan` happens in FOUND-03; the golden test then only swaps the adapter body. One `slow` cross-check ties the harness to the real code: run `run_simulation` with a narrow window (`budget_min = tier budget − 2`, `budget_utilization=0`) to a temp file (small) and assert each record equals the harness record (uses the real filter/sort/JSON path; ≈ 1-2 min).

**Golden file per tier** `tests/golden/characterization_{tier}.json`:
```json
{"format": 1, "tier": "medium", "config_note": "stage: legacy-float",
 "cases": [{"code": "0000012313", "tags": ["census:final_kz_100"],
            "valid": true, "over_budget": false,
            "expected": {"kz_final": 100, "total_damage": 96.0, "cia_mali": {...}, "costs": {...},
                         "final_events": [...], "waves": [ {... all fields of per_wave incl. events ...} ], "ros": 1.08}}]}
```
`code` = 10 level digits in config measure order (readable, stable); invalid selections store `{"valid": false}`. Sample membership is stored in the file (explicit codes), not re-derived from a seed (`random.sample` is not guaranteed stable across Python versions); the generation seed (e.g. `20260930`) is documented in `meta` only.

**Selection list (target ≤ 55 per tier):**
- 27 named strategies from `define_strategies` (all unique names, all dependency-valid; 11/9/7 are over budget for low/medium/high, so over-budget with Budget Review −15 is covered by them).
- Empty selection (`0000000000`, cost 0, RoS `null`, wave-level clamp low), all-L1, all-L3.
- Dependency edges: M1=3 with M2=1 (invalid), M1=3 with M2=2 (valid), M3=3 with M2=1 (invalid), M7=3 with M2=0 (invalid) and M2=1 (valid).
- Census hits (measured feasible in all tiers; medium examples in config order): `E==target` w1 `0000000202`, w2 `0000000230`, w3 `0000101013`; `G==thr` w1 `0000002223`, w2 `0000001303`, w3 `0000010300`; `G==thr+cap` w1 `0000022333`, w2 `0000012313`, w3 `0000101223`; final KZ 100 `0000012313`; wave-level clamp high `0000022333`; remaining budget exactly −1/0/1/24/25/49/50/74/75 k€ (tier-specific, e.g. medium 0 → `0000032233`, 25 → `0000111332`, 50 → `0000111331`, 75 → `0000102223`). Today's code gives Budget Review +5 at exactly 25k and +10 at 50k (`>=` on tier minimum) although the description text says "25.001"; pin it (Phase 2/RULE-07 changes it).
- Wave-3 tie (positive totals only, see Q5; tier independent because E and the deltas do not depend on the tier; codes found by the census, one per signature): `0102112122` (bonus 0, E 28.5, event KZ 0), `0002221123` (event KZ +5), `2000200120` (bonus 8, E 20.5, event KZ −10 via "Nervige Authentifizierung"), `0200102012` (bonus 6, E 22.5), `0001100211` (bonus 9, E 19.5). Regenerate with a throwaway finder, do not hand-pick.
- 8-10 seeded random dependency-valid selections.
Use a throwaway `find_golden_cases` script (not committed) or a documented helper to regenerate; the golden file is the source of truth.

**Digest (D-08):** `tests/support/digest.py` iterates all valid combinations in enumeration order (`itertools.product(range(4), repeat=10)` over config measure order), builds one canonical line per combination and feeds `sha256`: `code|kz_final|damage|cost_total|event_opex|event_budget|kz_after_w1,kz_after_w2,kz_after_w3|e_reached_bits|over` with `int → str`, legacy `float → repr(float)`, exact values via `exact_to_json`/`p/q`, `None → "-"`, `bool → 0/1`. Store `tests/golden/digest_{tier}.json` = `{"digest", "count", "in_budget", "over_budget", "kz_histogram": [101 ints], "sum_damage"}` so a mismatch prints a readable histogram diff. Legacy-path digest cost ≈ 2-3 min per tier (parametrise tiers so they can run separately). `--update-golden` rewrites digest files too.

**TDD vs characterization:** golden/digest tests pass immediately by construction; verify they can fail with a mutation check in the plan (temporarily change one config value or one formula constant, see red, revert). TDD proper applies to FOUND-04, -05, -06, -07 (write failing test first).

### Q5. Exact switch review (D-05 step 3), measured over ALL combinations

Experiment: legacy float functions vs exact integer kernel with D-23 rounding (wave total rounded once, then clamped, final Budget Review afterwards), every dependency-valid combination per tier (3 × 782,336). Per-tier results:

| Metric | low | medium | high |
|---|---|---|---|
| final KZ changed (exact-rounded ≠ legacy) | 121,306 (15.5%) | 168,625 (21.6%) | 194,360 (24.8%) |
| … of which legacy KZ already integer | 0 | 0 | 2 |
| KZ shift ≥ 0.5 (rounds to ±1) | 7,986 down / 7,914 up | 8,637 / 8,845 | 8,973 / 9,242 |
| E-target (`e_value >= e_target`) result differs | **0** | **0** | **0** |
| over-budget flag differs | **0** | **0** | **0** |
| damage differs by > 0.5 € | **0** | **0** | **0** |
| damage has float noise only (non-integer euros in float) | 179,084 | 179,084 | 179,084 |
| max |legacy − exact-unrounded| KZ | 4.3e-14 | 2.8e-14 | 2.8e-14 |
| wave-3 ties (reduction above threshold = 3.5) | 1,050 | 1,050 | 1,050 |

Explanation: all KZ changes come from the D-23 rounding (unrounded exact KZ equals legacy up to 4e-14 noise for every combination); float noise never flips a discrete check in today's config (the Pitfall-6 risk is latent). The per-wave rounding of the OT slope 1.2/point and the exfil slope 17/7 produces the fractional legacy values. Damage becomes integer euros for all selections.

Ties: all 1,050 wave-3 tie combinations per tier have the E-target reached (+10), wave total = 10 + 1.5 + event KZ (event KZ ranges −10 … +20) ∈ [1.5, 31.5], i.e. **positive only** (signature census: bonus 0/6/8/9 with E = 28.5/22.5/20.5/19.5; bonus ≥ 14 would need E ≤ 14.5, which the measures make unreachable). The negative case −7 + 1.5 = −5.5 → −6 from D-23 exists only in the prose example.

**Representation in golden JSON:** ints as JSON ints; other exact numbers as strings via `exact_to_json` (`"2.24"` when finite, `"17/7"` otherwise); decode with `Fraction(str)`. RoS is `"p/q"` mostly; `null` for zero cost.

**How to produce the explicit semantic diff over ALL combinations (recommended):** before starting the FOUND-05 plan's numeric change, at the last float commit run a dump tool that writes the compact per-combination arrays (`array.tofile`: code, final KZ as float64, damage as float64, total cost, e-reached bits, over flag; ~25 MB per tier, gitignored under `.planning/phases/01-simulation-foundation/pre-exact/`). After the switch, the same dump runs with exact values and a small diff script compares field by field and reports exactly the table above plus top-K movers and sample selections. Commit the resulting text report (counts and 10 examples per category, not the dumps) as `01-EXACT-SWITCH-DIFF.md` next to the plan; the golden `--update-golden` output shows the sample-level diff. A frozen float "oracle" module in `tests/` is the alternative but leaves a second copy of every formula in the repo; if used it must be deleted in the same plan.

### Q6. Canonical semantics: inventory of duplicated/divergent formulas (D-24…D-27)

| Item | `simulate_outcomes.py` (`run_simulation`) | `analyze_simulation_results.py` | `balance_analysis.py` | Canonical |
|---|---|---|---|---|
| Budget check | `total_cost (init+3·opex+event opex) > tier.budget + event budget delta` → filtered; extra `min_cost` and utilization filters | - | skip if `init+3·opex > tier.budget` (no event budget, no event OPEX) | D-11 (run_simulation's) |
| Final events (Budget Review) | applied after the filter with `remaining = adjusted − total` | reads them from JSON | **never applied** (KZ up to ±15 off) | applied for every plan incl. over-budget |
| Over-budget plans | never evaluated (dropped) | absent | [SKIP] | evaluated, flagged (D-09/D-11) |
| Cost used for RoS | `costs.total` incl. event opex (wave 1: −2 k€ per active measure) | uses `costs.total` | adds event opex after budget check | total incl. event OPEX until Phase 2 (D-24/D-25) |
| Own cost | - | - | - | init + opex×waves, excl. events (D-25), for Pareto/store |
| Base losses | - | `Σ base_severity·s_unit` from raw config (620, ignores severity multiplier) | simulated no-measure damage (620·multiplier) | Σ base_severity·s_unit (620) |
| RoS formula | - | written **5 times** inline | `calculate_ros` | one `ros()`; `None` if cost 0 |
| Score | - | Final-Index `w_kz·KZ + w_ros·100·RoS`, KZ only if RoS None | `combined_score = 0.6·KZ + 0.3·norm(RoS) + 0.1·norm(damage)` | Final-Index only (provisional labels, D-12) |
| Config load | `load_config` (no encoding) | separate raw `json.loads(read_text())` in `load_base_losses` | via import | one `planspiel.config.load_config` |
| Zero cost | - | `ZeroDivisionError` | returns 0.0 | `None` (D-27) |
| Hard-coded numbers | defaults `e_threshold=18`, `kz_start=60`, `severity_multiplier=1.0` (hidden defaults) | - | `KZ>=50` "positive", strategy budget comments "300/400/500k" (stale, tiers are 350/400/450) | keep defaults behaviour-preserving; list in validator as warnings; `KZ>=50` is a presentation constant (Open Question 4) |

**Behaviour changes `balance_analysis.py` will show:** over-budget strategies are evaluated and flagged instead of `[SKIP]`ped (the classification of the 27 named strategies is unchanged today: 11/9/7 over budget for low/medium/high, verified); Budget Review KZ adjustments (−15…+15) now included; RoS baseline from config (same 620 today); "Score" column replaced by Final-Index; best/worst and tier comparison rank by Final-Index; empty-cost RoS prints `n/a`. These printed numbers are intentionally not pinned by golden files.

**Legacy JSON output (D-26) details to preserve:** `results.sort(key=(-kz_final, total_damage))` is a stable sort over enumeration order (equal to tie-break by selection code ascending); structure `{summary: {total_outcomes, budget_tier, budget, kz_start, budget_filter{min,max,utilization_min}, measures}, results:[...]}`; `json.dumps(..., indent=2)` with default `ensure_ascii=True`. After step 3 damage values are exact decimals written as JSON numbers (floats), which `analyze` reads back via `json.loads(parse_float=Fraction)`; finite decimals round-trip exactly (`Fraction("2.24")`).

### Q7. Umlauts (FOUND-04, D-20, D-28)

Transliterated **display** strings in `simulation_config.json` (found by scanning all string values):
- `waves[1].name`: "OT-Stoerung" → "OT-Störung"
- `events.wave_1[0].description`: "Geschaeftsfuehrung", "Massnahmenwechsel", "durchzufuehren" → "Geschäftsführung", "Maßnahmenwechsel", "durchzuführen"
- `events.wave_1[1].name`: "Operative Unterstuetzung" → "Unterstützung"; `.description`: "Massnahme" → "Maßnahme"
- `events.wave_2[0].description` (Sparprogramm): "verkuendet" → "verkündet"
- `events.wave_2[1].description` (OEM-Audit): "prueft" → "prüft"
- `events.wave_2[2].description`: "haengt" → "hängt"
- `events.wave_3[0].description`: "Fuer", "Massnahme", "hoechstem" → "Für", "Maßnahme", "höchstem"
- `events.wave_3[1].description`: "Verschaerfte" → "Verschärfte"
- `final_events[0].description`: "geprueft" → "geprüft"
- `_comment_events` (not display, but German prose): "aufgefuehrt" → "aufgeführt" (fix too, cheap)
Already correct (real umlauts): all attack descriptions, all `bonus_measures[].description`. **Ids and keys stay ASCII** (`operative_unterstuetzung`, `ot`, `oem_audit`, ...).

Allow-list for the test (case-insensitive substrings, extend as needed): `stoerung`, `fuehrung`, `fuehren`, `unterstuetz`, `verkuend`, `prueft`, `geprueft`, `haengt`, `\bfuer\b`, `hoechst`, `verschaerf`, `aufgefuehrt`, `massnahme`, `ausfuehr`, `ueber`, `moeglich`, `koennen`, `muessen`, `waehrend`, `gross`, `schliess`. Scope: every string **value** except those under keys `id`, `measure`, `attack_id`, `type`, `default_budget_tier`, and dict keys; plus a mojibake check (`Ã`, `Â`, `â€` absent). Note "Sicherheitsstrategie" and "Beispiel" must not trigger, so use word-stem patterns, not generic `ae/oe/ue` regexes.

Config strings that **flow into simulation outputs** (and therefore golden files, so FOUND-04 must precede FOUND-02): `wave.name` → `per_wave.wave_name`; `bonus_measures[].description` → `per_wave.bonus_descriptions`; `event.name` → `events[].name` (and final events); `event.description` only for `flat_budget` events (Sparprogramm) → `effect_description`; other `effect_description`s are built in Python source ("… aktive Maßnahmen x …k€", "Restbudget …k€"; source already has real umlauts and `€`). `attacks.*.description`, other event descriptions and `_comment_events` do not reach outputs.

Smoke check for the untouched generators (D-18): `generate_pptx_cards.load_config()` and `generate_from_template.load_config()` read UTF-8 already; `generate_attack_calculator.py` reads `simulation_config.json` **at import time relative to cwd** and its `main()` overwrites the tracked `angriff_berechnung.xlsx`. The smoke test must `monkeypatch.chdir(repo_root)`, import only, assert a German display string (e.g. `config['waves'][1]['name'] == 'OT-Störung'`), and never call `main()`.

### Q8. Validator (FOUND-07, D-21)

`planspiel.validate.validate(raw) -> list[Issue]` with `Issue(level: "error"|"warning", code, path, message)`. `load_config` calls it on every load, raises `ConfigError` with **all** errors (not just the first), and emits `warnings.warn(..., HandCalcWarning, stacklevel=2)` for warnings (`HandCalcWarning(UserWarning)`); pytest shows them in its warnings summary; the tests additionally assert the exact set of expected warning codes for the real config.

**Errors (referential/schema, all reachable from today's schema):**
1. `waves[].attack_id` ∈ `attacks`; wave ids are 1..N consecutive and unique.
2. `waves[].bonus_measures[].measure` ∈ `measures`; `min_level` ∈ 1..3; `bonus` int ≥ 0.
3. `measures[*].dependencies[].requires[].measure` ∈ `measures`, not self-referencing; `level` ∈ 1..3; `min_level` ∈ 0..3; no dependency cycles.
4. `measures[*].levels` keys exactly `"0","1","2","3"`; each has `cia{c,i,a}` ints, `init`/`opex` ints ≥ 0; level 0 all zero; optional `recovery` in [0,1].
5. Events: `type` ∈ known set (`noop`, `flat_budget`, `opex_discount_per_active_measure`, `checklist_tier`, `measure_level_tier`, `level_bonus_per_measure`, `and_condition`, `final_budget_tier`); required params per type; `checklist_tier.measures` ∈ `measures` and `min_level` ∈ 1..3, tiers ascending and count keys ≤ len(measures); `measure_level_tier.measure` ∈ `measures` and `tiers` keys exactly `"0".."3"`; `and_condition.clauses[].measure` ∈ `measures`, each clause has exactly one of `min_level`/`level_eq`; `level_bonus_per_measure.level` ∈ 1..3; `final_budget_tier` only inside `final_events` (and only that type there; evaluating it without a remaining budget crashes today); tiers sorted ascending by minimum.
6. `events` keys `wave_N` ∈ wave ids; event ids unique and ASCII.
7. `budget_tiers[*].e_targets` keys == wave ids (today a missing key raises `KeyError` mid-simulation); `default_budget_tier` ∈ `budget_tiers`; `budget`, `kz_start` ints.
8. `waves[].weights` keys `c,i,a`; `attacks[*].cia_impact` keys `c,i,a`; `mitigation_cap` > 0; `allow_recovery` bool; numeric types (bool is not int).
9. Exactness preconditions (needed by FOUND-05; recommended as errors): all numbers are finite decimals (guaranteed by `parse_float=Fraction`), `base_severity·severity_multiplier·WS` integral, damage in whole euros for every severity step/recovery level.

**Warnings (hand-calculability, promoted to errors in Phase 6):**
- `hand_calc.kz_slope`: `(kz_at_full_mitigation − kz_at_full_damage) / mitigation_cap` must have ≤ 1 decimal → **fires today for exfil (17/7 = wave 3)**; ransomware 16/8 = 2 and OT 12/10 = 1.2 pass.
- `hand_calc.severity_cap`: `base_severity != mitigation_cap` (passes today: 8/8, 10/10, 7/7).
- `hand_calc.severity_multiplier`: any tier ≠ 1.0 (passes today).
- `hand_calc.weights`: per wave `wc+wi+wa != 1` (exact `Fraction` sum, never floats) or > 1 decimal (passes today).
- `hand_calc.recovery`: recovery with > 1 decimal (passes today: 0.1/0.3/0.5).
Expected result on the real config: **zero errors, exactly one warning (`hand_calc.kz_slope` for wave 3 / attack `exfil`)**; the hidden defaults (`e_threshold` 18, `kz_start` 60, `severity_multiplier` 1.0, `base_cia`) may additionally warn as `schema.default_used` (none triggers today).

**Surfacing:** pytest: warnings summary (default) plus `test_validate.py` asserts codes with `pytest.warns` / `warnings.catch_warnings(record=True)`; broken fixtures (`tests/fixtures/broken_*.json`, one per rule: unknown measure id in a bonus, unknown attack id, dependency to unknown measure, missing tier e_target, event ref to unknown measure) assert `ConfigError` mentions path + code. CLI: `uv run planspiel validate [--config PATH] [--strict]` prints `ERROR|WARN code path: message` lines (UTF-8 stdout), exit 0 with only warnings, 1 with errors, `--strict` (used by Phase 6) exits 1 on warnings.

### Q9. Validation Architecture: see the dedicated section below.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `python3 script.py` with system pip | `uv run` with committed `uv.lock` | project decision 2026-09-29 | reproducible, PATH-independent |
| float sums in the wave math | integer-scaled exact arithmetic + one rounding point | this phase (D-05 step 3) | KZ integer, damage whole euros, facilitators reproduce the sim |
| Python `round()` for display | `round_half_away` (kaufmännisch) | this phase | matches paper |
| Keep all outcome dicts in memory | compact `array` store + aggregates; dump on request | this phase | 5 GB → ~0.2 GB per tier |

**Deprecated/outdated:** `analyze_simulation_results.py` inline RoS ×5, `balance_analysis.calculate_combined_score` and its own budget check (removed per D-24); `.planning/codebase/CONCERNS.md` repo-hygiene notes (D-22).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | "per started 10.000 €" means ceil: exactly 10.000 € over → 1 step, 10.001 € → 2 steps, 0 or negative → 0 | Code Examples, Phase 2 hand-off | Off-by-one in Phase 2's penalty table. The user should confirm the wording printed on paper (D-04 names the boundaries but not the results) |
| A2 | Legacy `--budget-max` quirk (only feeds the utilization threshold) is preserved, not fixed | Pitfall 4 | Users expecting a hard cap; low, D-26 says unchanged |
| A3 | Percentiles use nearest-rank (returns an observed value): p ∈ {0,5,25,50,75,95,100}, index `ceil(p/100·n)−1` | Q2/report | Different percentile definition shifts reported numbers slightly |
| A4 | Report tie-break for top-K by KZ: KZ desc, own cost asc, damage asc, code asc (legacy `--output` keeps damage asc, then code) | Pitfall 3 | Different "top" lists; harmless but should be fixed once |
| A5 | K for top-K = 10 (`--top` overrides) | Q2 | none |
| A6 | Acceptance bounds (120 s, 500 MB, 32 B/record) are 2.5x the measured values on this machine | Q2 | Too loose/tight on other hardware |
| A7 | Use uv_build (not hatchling) as the backend | Standard Stack | Alternative works too; low |
| A8 | A negative-tie golden case is covered by a test-only tier override, not by a real selection | Pitfall 2 | Deviates from the literal wording of D-23; needs user confirmation (Open Question 1) |
| A9 | The pre-exact per-combination dump (gitignored) is preferred over keeping a frozen float oracle copy | Q5 | Extra sequencing constraint inside the FOUND-05 plan |
| A10 | Extra validator errors "exactness preconditions" (integral scaling, damage whole euros) beyond D-21's list | Q8 | Slightly stricter loader; needed by FOUND-05 |

## Open Questions

1. **D-23 negative-tie golden case is unreachable**
   - What we know: 1,050 wave-3 ties per tier, all with positive totals (E-target always reached); no negative tie in any of the 3×782,336 combinations.
   - What's unclear: whether the user accepts helper unit tests + a test-only tier override as the "negative" coverage.
   - Recommendation: accept the override approach (A8); implement at FOUND-05, not FOUND-02 (legacy floats do no rounding, so a negative tie cannot be pinned pre-switch).
2. **`--budget-max` no-op quirk** — preserve and pin (A2) or fix now? Recommendation: preserve; note in README that `--budget-max` only affects `--budget-utilization` until Phase 6.
3. **Seam verdicts SUS for pytest/openpyxl/python-pptx/uv-build** (unknown downloads only). Recommendation: one human-verify checkpoint, then proceed.
4. **`balance_analysis.py` constant `KZ >= 50` ("positive outcome")** is neither in config nor in D-24. Recommendation: keep as a labelled presentation constant or derive from `kz_start`; user decision, not blocking.
5. **Wrapper import compatibility** — `balance_analysis.py` currently does `from simulate_outcomes import ...`. Nothing else imports the root scripts (repo grep), so wrappers need no re-exports. Recommendation: none needed; confirm in the FOUND-03 plan by grep.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| uv | FOUND-01 (all) | ✓ | 0.12.5 | — |
| CPython via uv | all | ✓ | 3.12.14 managed (also 3.11.7 Store, Inkscape 3.12.9 without pip: unusable by uv) | uv downloads on demand |
| Network to PyPI | first `uv sync` (pytest, uv_build, openpyxl, python-pptx) | ✓ (worked in this session) | — | uv cache after first run |
| git | commits, `git clone` fresh-clone check | ✓ | — | — |
| jq | optional inspection of big JSON | not checked | — | Python |
| RAM | enumeration | ✓ | 47.9 GB (peak need ≈ 0.2-0.3 GB) | — |
| CPU | timing bounds | ✓ 6 cores (single-threaded runs; 3 parallel tier runs slowed each other by ~1.5x) | — | — |

**Missing dependencies with no fallback:** none. **With fallback:** none.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (Wave 0, see Code Examples) |
| Quick run command | `uv run pytest -q` (default `-m 'not slow'`; target < 15 s) |
| Full suite command | `uv run pytest -q -m "slow or not slow"` (slow ≈ 10-15 min on this machine after the exact switch, ≈ 15-20 min for legacy-float digest stage) |
| Golden update | `uv run pytest --update-golden` (add `-m slow` to refresh digests) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FOUND-01 | env sets up; interpreter is the managed 3.12; wrappers run under `uv run` regardless of PATH python | smoke + manual | `uv run pytest tests/test_environment.py -q`; manual fresh clone: `git clone . /tmp/fc && cd /tmp/fc && PATH="/c/Program Files/Inkscape/bin:$PATH" uv run --locked pytest -q`; `uv run python simulate_outcomes.py --help` (×3 wrappers) | ❌ Wave 0 |
| FOUND-02 | golden sample per tier equals current outputs (KZ, per-wave, damage, costs, events, RoS, over-budget) | characterization (fast) | `uv run pytest tests/test_characterization.py -q` | ❌ Wave 0 |
| FOUND-02 | full digest per tier equals pinned digest; harness ties to real `run_simulation` | characterization (slow) | `uv run pytest -m slow tests/test_digest.py tests/test_harness_vs_run_simulation.py` | ❌ Wave 0 |
| FOUND-03 | formulas defined once; wrappers thin; documented commands work; golden zero diff after refactor | structural + characterization | `uv run pytest tests/test_single_definition.py tests/test_thin_wrappers.py tests/test_characterization.py -q` | ❌ Wave 0 |
| FOUND-04 | config decodes as UTF-8, no mojibake, no allow-listed transliteration in display fields, no encoding-less text I/O; generators still load config | unit + lint + smoke | `uv run pytest tests/test_config_text.py tests/test_encoding_lint.py tests/test_legacy_generators_smoke.py -q` | ❌ Wave 0 |
| FOUND-05 | `round_half_away` and `started_steps` boundaries; exact arithmetic reproduces hand-computed waves; kernel == rich path; exact-switch diff report | unit + property/conformance | `uv run pytest tests/test_rounding.py tests/test_rules_exact.py tests/test_kernel_conformance.py -q` | ❌ Wave 0 |
| FOUND-06 | aggregation correct vs brute force on `mini_config.json`; report fields present; bounds (time ≤ 120 s, peak ≤ 500 MB, ≤ 32 B/record); dump only on request; legacy `--output` shape unchanged | unit (fast) + slow perf | `uv run pytest tests/test_enumeration.py -q`; `uv run pytest -m slow tests/test_enumeration_perf.py` | ❌ Wave 0 |
| FOUND-07 | broken references rejected (each fixture); expected single warning (wave 3 slope 17/7) on the real config; CLI exit codes | unit | `uv run pytest tests/test_validate.py -q`; `uv run planspiel validate` (exit 0, one warning) | ❌ Wave 0 |

Success criteria coverage: SC1 → FOUND-01 rows; SC2 → FOUND-02/03 rows plus reviewed `--update-golden` diff at step 3; SC3 → FOUND-04 + `test_rounding.py` boundary cases (`started_steps(10_000) == 1`, `(10_001) == 2`, `(0) == 0`, `(-5_000) == 0`, `round_half_away` ±0.5 cases); SC4 → FOUND-06 rows; SC5 → FOUND-07 rows including `base_severity != mitigation_cap` fixture and the wave-3 slope warning.

### Sampling Rate
- **Per task commit:** `uv run pytest -q` (fast suite).
- **Per wave merge:** fast suite plus `uv run pytest -q -m slow -k "digest or perf"` for the tier(s) touched.
- **Phase gate:** full suite green (`-m "slow or not slow"`), fresh-clone command green, `uv run planspiel validate` shows the one expected warning, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `pyproject.toml`, `uv.lock`, `.python-version`, `planspiel/__init__.py` + `cli.py` stub (FOUND-01)
- [ ] `tests/conftest.py` (`--update-golden`, terminal summary), `tests/support/{golden,legacy_harness,digest,peak_memory}.py`
- [ ] `tests/golden/` files (generated by the capture task, not hand-written), `tests/fixtures/mini_config.json`, `tests/fixtures/broken_*.json`
- [ ] `.gitignore` / `.gitattributes` additions
- [ ] All `tests/test_*.py` listed above (none exist today; there is no test infrastructure at all)

TDD note (user rule "TDD for all features and bugfixes"): FOUND-04, -05, -06, -07 are test-first (red → green). FOUND-02 is a characterization capture (green immediately; prove sensitivity with a mutation check). FOUND-03 is a refactor under the FOUND-02 tests (no new behaviour, except canonical semantics for `balance_analysis.py`, which is test-first for the new shared `ros()`/`final_index()`/`evaluate_plan()`). FOUND-01 has no red phase: its acceptance is the fresh-clone command.

## Security Domain

`security_enforcement` is enabled (ASVS level 1, block on high). Offline, single-user CLI tooling, no network service, no authentication.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | Config validator (Q8) with hard errors; `argparse` types for CLI; `json.loads` only, no `eval`/`pickle`/`yaml.load` |
| V6 Cryptography | no (sha256 only as a digest, not for security) | `hashlib` |
| V10/V14 Supply chain, dependencies, config | yes | `uv.lock` with hashes, exact pins (`==`), `--locked` in fresh-clone check, one human-verify checkpoint for first install |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed or malicious config JSON | Tampering / DoS | validator rejects before use; bounded schema (10 measures × 4 levels) |
| Output path from CLI flag overwrites arbitrary file | Tampering | local single-user tool; `--output` is an explicit user choice; write only to given path, no shell |
| Typosquatted/slopsquatted dependency | Tampering | packages checked via legitimacy seam and official docs; pins + lockfile |
| Subprocess use in tests | Elevation | fixed argument lists (`sys.executable`, `-m`), no `shell=True` |
| Accidental overwrite of tracked artifacts by generator smoke test | Tampering | import only, never call `main()` of `generate_attack_calculator.py` |

## Project Constraints (from CLAUDE.md)

- English for code, identifiers, commit bodies, docs; UI/game content German; conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`). The global CLAUDE.md is internally inconsistent (Language: commit messages English; Git: "conventional commits (German message)"); the project CLAUDE.md says commit bodies English, "commit subject per user convention". Follow existing repo history (English `docs(01): ...` subjects) unless the user says otherwise.
- GSD owns the workflow: no edits outside a GSD command; plan granularity **one requirement = one PLAN.md**; review requirements for gaps before planning (done by the plan-phase gap review, D-23…D-30).
- TDD for features and bugfixes; run `superpowers:verification-before-completion` before claiming done.
- Never `--no-verify`; never force-push main; prefer new commits over amend.
- YAGNI: no speculative abstractions; prefer editing existing files; do not add docstrings/comments/types to code you did not change (this applies to the legacy generators, which stay untouched).
- No mocks for DB/integration tests (no DB here; use the real config and real enumeration).
- Project rules: single source of truth = `simulation_config.json` (order of change: config → README → print material); no fixed numbers in prose without config; hand-calculability is a hard criterion (linear formulas only); determinism (same inputs → same outputs; no randomness in outcomes; v1 code must not hard-code "exactly one scenario"); balance verified by **full enumeration**, not only `balance_analysis.py`; never read `sim_*.json` whole; generated binaries are never hand-edited (`final_documents/`, `pptx_output/`).
- Windows 11 + Git Bash: Unix paths/syntax; `python` on PATH is Inkscape's 3.12 (no pip) → always `uv run`.
- Scripts' German console output/CLI conventions: identifiers English, human-readable output German (needs UTF-8 stdout, Pitfall 1).

## Sources

### Primary (HIGH confidence)
- Measured experiments in this session (throwaway scripts in the session scratchpad, deleted afterwards): full-enumeration timings for float legacy, `Fraction` port, `Fraction` kernel and integer kernel (3 tiers); memory for tuple vs `array` stores (psutil peak working set and tracemalloc); exact-switch diff over 3 × 782,336 combinations; wave-3 tie census; golden-case census; strategy classification; console encoding tests; uv layout tests (with and without build system; fresh-clone run; pytest `-m`/`--update-golden` plumbing).
- Repo files read: `simulate_outcomes.py`, `balance_analysis.py`, `analyze_simulation_results.py`, `simulation_config.json`, `README.md`, `CLAUDE.md`, `.claude/CLAUDE.md`, `.planning/{CONTEXT,REQUIREMENTS,STATE,ROADMAP,config}.json/md`, `.planning/research/{PITFALLS,ARCHITECTURE,STACK}.md`.
- [docs.astral.sh/uv/concepts/build-backend](https://docs.astral.sh/uv/concepts/build-backend/) - flat layout `module-root = ""`, recommended `uv_build>=0.12.21,<0.13`, `uv init` default.
- [docs.astral.sh/uv/concepts/projects/config](https://docs.astral.sh/uv/concepts/projects/config/) - no build system → project not installed; entry point tables require a build system; `tool.uv.package`.
- PyPI JSON API (pytest 9.1.1, openpyxl 3.1.5, python-pptx 1.0.2, uv-build 0.12.21, psutil 7.2.2).
- `gsd-tools query package-legitimacy check` (verdicts above).

### Secondary (MEDIUM confidence)
- STACK.md recommendation of no build-system (superseded here for the CLI reason).

### Tertiary (LOW confidence)
- none; items not verified are in the Assumptions Log.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - versions read from PyPI, layout verified by running `uv sync`/`uv run` in scratch projects.
- Architecture: HIGH for exactness/enumeration/memory (measured), MEDIUM for module layout (discretionary).
- Pitfalls: HIGH - each was reproduced on this machine (cp1252 decoding, piped stdout crash, negative tie unreachability, `--budget-max` quirk, missing final events in naive harness).
- Timing/memory bounds: HIGH for this machine, variable ±40% between runs (other processes running); bounds carry 2.5x headroom.

**Research date:** 2026-09-30
**Valid until:** 2026-10-30 (stable tooling; re-check `uv_build` version bound if uv is upgraded)
