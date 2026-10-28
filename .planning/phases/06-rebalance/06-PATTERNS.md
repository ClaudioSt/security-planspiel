# Phase 6: Rebalance - Pattern Map

**Mapped:** 2026-10-28
**Files analyzed:** 22 new/modified (code, tests, config, content)
**Analogs found:** 20 / 22 (two partial: `metrics.py` family, candidate-config option)

All excerpts are from the working tree at 2026-10-28. Paths are relative to the repo root.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `planspiel/gate.py` (modify: move-path gate, `calibrate`, `--paths`) | service (pure check) | batch (columns/tables in, numbers out) | `planspiel/gate.py` itself (`gate_from_columns`, `lowering_closure`) | exact (extend) |
| `planspiel/cli.py` (modify: `gate --paths`, `balance`, `validate` level) | route (argparse command) | request-response | `cli._gate_command` (cli.py:158-175) | exact |
| `planspiel/metrics.py` (new: dominance, band, overpowered, quartile, comeback, corridor, spread) | utility (pure functions) | transform over columns | `gate.py` (column-based pure functions) + `report.summarize_tier` | role-match |
| `planspiel/rules.py` (modify: `final_index`) | service (single formula definition) | transform | `rules.final_index` (rules.py:629-632) | exact (edit) |
| `planspiel/report.py` (modify: in-budget top-K/Pareto, drop `FINAL_INDEX_STATUS`) | service (report) | batch | `report.summarize_tier` / `pareto_front` | exact (edit) |
| `planspiel/balance.py` (modify: `--config`, read `reference_strategies`) | utility (CLI report) | batch | `balance.run_analysis` + `refpaths.reference_path` | role-match |
| `planspiel/validate.py` (modify: `hand_calc_level`, `reference_strategies` rules) | service (validator) | request-response | `check_hand_calc` (813-865), `check_reference_plans` (698-738) | exact |
| `planspiel/config.py` (modify: `reference_strategies` field, severity param) | config loader | request-response | `reference_plans` field (config.py:105, 241), `check_config` (152-162) | exact |
| `planspiel/texts.py` (modify: `Clue.measures/weight`, `check_clues`, matrix) | model + validator | transform | `Clue`, `load_clues`, `check_clues`, `format_clue_matrix` (texts.py:544-714) | exact |
| `planspiel/master.py`, `print/templates/master.tex.j2` (modify: clue matrix cell, no `~`/vorläufig) | view model + template | transform | existing `master._clue_groups` / `ClueEntry` path | exact |
| `content/clues.toml` (modify: `measures`, `weight`) | content/config | file-I/O | `tests/fixtures/mini_content/clues.toml` + current `[[clue]]` entries | exact |
| `simulation_config.json` (`reference_strategies` key, tuned values) | config | file-I/O | `reference_plans` block (simulation_config.json:301) | exact |
| `tests/test_gate_paths.py` (new) | test | brute force vs fast path | `tests/test_overspend_gate.py` | exact |
| `tests/test_balance_metrics.py` (new) | test | synthetic columns + mini brute force | `tests/test_overspend_gate.py` (`_synthetic`, `_mini_brute`) | role-match |
| `tests/test_balance_report.py` (new) | test | CLI/report on mini config | `tests/test_final_index_config.py` (digests/summaries on mini) | role-match |
| `tests/test_reference_strategies.py` (new) | test | validator + legality | `tests/test_reference_plans.py` | exact |
| `tests/test_clues_mapping.py` (new) | test | validator on fixtures | `tests/test_clues.py` | exact |
| `tests/test_validate.py`, `test_final_index_config.py`, `test_enumeration.py` (extend) | test | unit | self | exact |
| `tests/fixtures/mini_config.json` (add `reference_strategies`) | fixture | file-I/O | its `reference_plans`-style blocks / `test_reference_plans.VALID_BLOCK` | role-match |
| `tests/fixtures/mini_content/clues.toml` (add keys) | fixture | file-I/O | itself (6 clues) | exact |
| `tests/golden/gate_paths_{tier}.json` (new, slow) | golden | file-I/O | `tests/golden/gate_{tier}.json` via `check_golden` | exact |
| Candidate-config selection for slow tests (conftest option / env) | test support | config | `tests/support/__init__.py` `CONFIG_PATH`, `harness.load_config()` | partial |

## Pattern Assignments

### `planspiel/gate.py` move-path gate (service, batch)

**Analog:** `planspiel/gate.py` (static gate). New functions go next to it and must reuse `lowering_closure`, `required_penalty_x`, `GateResult`-style result and `gate_result_json`.

**Imports pattern** (gate.py:11-17):
```python
from array import array
from typing import Dict, NamedTuple, Optional

from planspiel import rules
from planspiel.enumerate import code_from_index, enumerate_tier
from planspiel.report import REFERENCE_LABEL, REFERENCE_LAYER
from planspiel.rounding import started_steps
```

**Closure to reuse for the start-lowered pool** (gate.py:38-48):
```python
def lowering_closure(best: array, n: int) -> None:
    size = LEVELS**n
    for j in range(n):
        stride = LEVELS ** (n - 1 - j)
        for i in range(stride, size):
            if (i // stride) % LEVELS:
                lower = best[i - stride]
                if lower > best[i]:
                    best[i] = lower
```

**Required X per path** (gate.py:51-55), use for the scan `max(1, (pre - pool[s0]) // steps + 1)`:
```python
def required_penalty_x(kz_pre_review: int, trimmed_final: int, steps: int, strict: bool = True) -> int:
    gap = kz_pre_review - trimmed_final
    if strict:
        return max(1, gap // steps + 1)
    return max(1, -(-gap // steps))
```

**Pool pattern** (gate.py:58-67 `trim_keys`: write key `kz_final * size + (size-1-code)` into a `4**n` array, then close). The path gate does the same with `pool[s0] = max in-budget final over all legal continuations` (RESEARCH Pattern 2), iterating `rules.TierTables.swap_paths()` (rules.py:1230) and window families via `rules.evaluate_path` (rules.py:748; `Path`/`Window` NamedTuples at 704-709).

**Result/JSON/format shape** (gate.py:22-35, 173-213): a `NamedTuple` result with `passed`, a `*_json` function with fixed key order (a test asserts `list(data) == [...]`), a German `format_*_report`. Follow this for `gate_paths_result_json` and keep keys stable (golden `gate_paths_{tier}.json`: per family min X strict/weak, histogram tail, witness, counts).

**CLI wiring** (cli.py:158-175):
```python
def _gate_command(parser, config, tiers) -> int:
    from planspiel.config import load_config
    from planspiel.gate import format_gate_report, gate_tier
    cfg = load_config(Path(config))
    names = tiers or list(cfg.budget_tiers)
    unknown = [name for name in names if name not in cfg.budget_tiers]
    if unknown:
        parser.error(f"Unbekanntes Budget-Tier '{unknown[0]}'. Verfügbar: {', '.join(cfg.budget_tiers)}.")
    all_passed = True
    for name in names:
        result = gate_tier(cfg, name)
        print(format_gate_report(result)); print()
        all_passed = all_passed and result.passed
    print("Überziehungs-Gate: bestanden" if all_passed else "Überziehungs-Gate: NICHT bestanden")
    return 0 if all_passed else 1
```
Add `--paths` to the `gate_parser` (cli.py:376-388, parser has `--config`); imports stay function-local; exit 0/1.

**Rules:** no second formula definition in `planspiel/` (`tests/test_single_definition.py` AST guard); numpy engine, if adopted, belongs in `tests/support/` with a conformance test, never in `planspiel/`. Over-budget definition only via `rules.budget_ledger`.

---

### `tests/test_gate_paths.py` (test, brute force vs fast path)

**Analog:** `tests/test_overspend_gate.py`.

**Header/fixtures** (lines 1-26):
```python
import random
from array import array
import pytest
from planspiel import gate, rules
from planspiel.enumerate import code_from_index, enumerate_tier
from tests.support import REPO_ROOT, harness
from tests.support.golden import check_golden

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"

@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)
```

**Closure vs brute force** (34-42): `random.Random(seed)` initial arrays, compare `lowering_closure` to `max(initial[j] for j in range(size) if _below(j, i, n))` with `_digits`/`_below` helpers (24-30). Reuse these helpers (import or copy) for the start-lowered pool.

**Synthetic columns** (62-75): `_synthetic(rows, config_x, step)` builds `array("I"/"B"/"h")` columns on an `n = 2` lattice; asserts witness, histogram, `passed`. Mirror for synthetic path tables.

**Mini brute force** (141-226, `_mini_brute` + `test_mini_gate_equals_brute_force`): enumerate every plan via `harness.iter_codes/evaluate/selection_of/compact_from_plan`, compute trimmed candidates with `[t for t in in_budget if _below(t, index, n)]`, pick `min(candidates, key=lambda t: (-in_budget[t].kz_final, t))`, compare every field to the fast result parametrized over `TIERS`. For paths: enumerate all legal paths on the 256-plan mini config through `rules.evaluate_path` and compare per family.

**Slow golden** (297-301):
```python
@pytest.mark.slow
@pytest.mark.parametrize("tier", TIERS)
def test_gate_result_matches_golden(tier, update_golden, golden_report):
    path = REPO_ROOT / "tests" / "golden" / f"gate_{tier}.json"
    check_golden(path, gate.gate_result_json(_real_gate(tier)), update_golden, golden_report)
```
Use a module-level `_GATE_CACHE` like `_real_gate` (290-294). Real-config checks that fail today are the target: mark `slow` and `xfail(strict=False, reason="target of Phase 6 tuning")` or keep them out of default `-m slow` until adoption (RESEARCH Validation Architecture).

**JSON stability test** (249-269): assert `list(data) == [...]` for the new `*_json`.

---

### `planspiel/metrics.py` (new; utility, transform over columns)

**Analog:** no module of this shape exists. Closest: `gate.py` (pure functions over `ResultStore` columns, `array` grids, `lowering_closure`-style slices) and `report.summarize_tier` (column access + nearest-rank).

**Column access pattern** (report.py:73-83):
```python
def summarize_tier(cfg, tier_name: str, store: ResultStore, top_k: int = DEFAULT_TOP_K) -> Dict:
    code_col = store.column("code_index")
    kz_col = store.column("kz_final")
    own_col = store.column("own_cost")
    over_col = store.column("over_budget")
    n = len(store)
```
**Percentiles: do not hand-roll** (report.py:22-25):
```python
def nearest_rank(sorted_values: List, p: int):
    if not sorted_values:
        return None
    return sorted_values[max(0, (p * len(sorted_values) + 99) // 100 - 1)]
```
**Pareto** `report.pareto_front(store)` (28-57) already exists: extend with an `in_budget_only` option rather than duplicating.
**Exact ROS/final index:** `rules.ros(base, Fraction(damage, 1000), own)` and `rules.final_index(...)` (report.py:92, 104); never reimplement.
Use `Fraction`; no builtin `round()` (use `rounding.round_half_away_frac`). Metrics take columns/arrays and return numbers so they test on synthetic columns, mini brute force, and a slow real-config variant (same three-way pattern as the gate tests). Context-level dominance = slice comparison on the `4**n` grid (stride arithmetic as in `lowering_closure`). Near-optimal band (B = 5, > 90 %) per RESEARCH Pattern 3.

---

### `tests/test_balance_metrics.py` (test)

**Analog:** `tests/test_overspend_gate.py` synthetic and mini sections (above). Add real-config slow variants that run against the candidate (see "Candidate config" below). BAL-08/09 checks (median above start on both layers, corridor, IQR, D-11 band) take summary dicts, so they test on `summarize_tier(mini, tier, enumerate_tier(mini, tier))` output.

---

### `planspiel/rules.py` `final_index` (service, transform; BAL-03)

**Analog/current** (rules.py:629-632):
```python
def final_index(kz_final: int, ros: Optional[Fraction], weight_kz: Fraction, weight_ros: Fraction) -> Fraction:
    if ros is None:
        return weight_kz * kz_final
    return (weight_kz * kz_final) + (weight_ros * (ros * 100))
```
Change to `weight_ros * ros2` with `ros2 = round_half_away_frac(ros * 100) / 100` (RESEARCH Code Examples). All callers pass through this function (report.py:104, analyze.py, balance.py, master.py, refpaths.py). Config block `final_index` loaded as `FinalIndexWeights` (config.py:85); validator `check_final_index`. Tests to update/extend: `tests/test_final_index_config.py` (pins sha256 digests of summaries, `ONE = FinalIndexWeights(Fraction(1), Fraction(1))`: the digests will change by design, regenerate at the D-04 reviewed snapshot), `test_rules_semantics.py`, `test_ros_ledger.py`, `test_enumeration.py` (lines ~431-475 hold the 0.85 filter tests to remove).
"vorläufig" removals: `report.FINAL_INDEX_STATUS` (report.py:15), `report.format_console`, `balance.py`, `refpaths.py:302`, `content/texte.toml` keys `final_index_provisional`/`final_index_note` and the key list in `texts.py:88`.

---

### `planspiel/validate.py` (modify; BAL-02 `hand_calc_level`, BAL-07 `reference_strategies`)

**Analog:** `check_hand_calc` (validate.py:813-865). All five codes call `self.warning(...)`. Parameterize by a `hand_calc_level` attribute on `_Validator` and route via a helper (`self._hand_calc(code, path, msg)` -> `self.error` or `self.warning`):
```python
slope = kz_slope(ints[0], ints[1], ints[2])
if not _one_decimal(slope):
    ...
    self.warning(
        "hand_calc.kz_slope", path,
        f"KZ-Steigung {slope.numerator}/{slope.denominator} hat mehr als eine Nachkommastelle{suffix}",
    )
```
Entry point (validate.py:868-869): `def validate(raw: dict) -> List[Issue]: return _Validator(raw).run()`; add `hand_calc_level: str = "warning"`. **Do not flip the default before BAL-05**: `config.check_config` (config.py:152-162) raises `ConfigError` on any `error` and turns warnings into `HandCalcWarning`, so an early flip breaks `load_config(simulation_config.json)` and the whole suite. `planspiel validate` passes `"error"`; `planspiel validate --strict` already exists as an interim gate. Six tests assert the exfil warning (`test_budget_review.py` 276/284, `test_config_prose_removed.py:99`, `test_kurswechsel.py:205`, `test_practice_config.py` 356/360): update only in BAL-05.

**`reference_strategies` validator:** copy `check_reference_plans` (698-738), `check_reference_selection` (740-756), `check_reference_swap` (758-765) and the `container/field/int_value/error` helper style. Same `{start, windows}` shape, plus a `kind` key in {good, mediocre, bad}:
```python
for key in plan:
    if key not in ("start", "windows"):
        self.error("schema.keys", f"{plan_path}.{key}", f"Unbekannter Schlüssel '{key}' im Referenzpfad")
```
(extend the allowed key set with `kind`). New error codes in the `ref.*` namespace. Legality is checked in the check function through `rules.evaluate_path` (as `refpaths.reference_path` builds a `Path` from config, refpaths.py:29-36):
```python
def reference_path(cfg, tier_name: str) -> Path:
    block = cfg.reference_plans[tier_name]
    windows = tuple(
        Window(dict(window["selection"]), tuple(window["swap"]) if window.get("swap") is not None else None)
        for window in block["windows"]
    )
    return Path(dict(block["start"]), windows)
```
Generalize to accept a block, not a tier, to serve both `reference_plans` and `reference_strategies`.

**Config loader:** add `reference_strategies: Dict[str, Dict] = field(default_factory=dict)` next to config.py:105 and `reference_strategies=dict(raw.get("reference_strategies", {}))` next to config.py:241.

---

### `tests/test_reference_strategies.py` (test; BAL-07)

**Analog:** `tests/test_reference_plans.py` (shape, validator references, legality).

**Pattern** (lines 1-50):
```python
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
VALID_BLOCK = {"medium": {"start": {"M1": 2, "M2": 2, "M4": 1, "M6": 0},
    "windows": [{"selection": {...}, "swap": ["M4", "M6"]}, {"selection": {...}}]}}

def _raw():
    return json.loads(MINI.read_text(encoding="utf-8"))

def _with_block(block):
    raw = _raw(); raw["reference_plans"] = block; return raw

def _errors(raw):
    return [issue for issue in validate(raw) if issue.level == "error"]
```
Copy with `raw["reference_strategies"] = {...}` and the extra `kind` key; assert the unknown-tier/measure-set/window-count/swap errors as in the analog. Add: legality via `rules.evaluate_path` (a Kurswechsel needs a swap window), quartile placement on `summarize_tier` columns of the mini config, "good" equals the algorithm output derived from the clue mapping. The overspender archetype is NOT an entry (D-23), judged by the gate.

---

### `planspiel/texts.py` clue mapping (BAL-07 / D-18)

**Analog:** the existing clue code (texts.py:544-714).

**Dataclass + loader** (544-575): extend `Clue` and `load_clues`, which reads exactly four keys via `entry.get(...)`:
```python
@dataclass(frozen=True)
class Clue:
    attack: str
    source: str
    quote: str
    why: str
# add: measures: tuple[str, ...] = (); weight: int = 0   (defaults keep old fixtures loading)
...
Clue(attack=str(entry.get("attack", "")), source=str(entry.get("source", "")),
     quote=str(entry.get("quote", "")), why=str(entry.get("why", "")))
```
**Check pattern** (599-646): `check_clues` returns `list[Issue]` with `Issue("error", "clues.<code>", path, German message)`; add `clues.unknown_measure`, `clues.bad_weight`, `clues.unsupported_bonus`, `clues.not_graduated` the same way (path `f"clues[{number}]"` per clue, `f"clues.{attack_id}"` per attack, a measure path for graduation). Importance `I(m) = sum(bonus * slope)` with `Fraction` and `rules`/config slopes (do not recompute elsewhere).
**Matrix** (554-561 `ClueRow`, 683-699 `clue_matrix`, 706-714 `format_clue_matrix`): add a "Maßnahmen (Gewicht)" column to header, separator and cells; facilitator-only (`FacilitatorView`), never into `PreAttackView`.
**Print side:** `master._clue_groups` -> `ClueEntry`, `print/templates/master.tex.j2` (5 columns, headers `clue_head_*` in `[sheets.spielleitung]` of `content/texte.toml`); add `clue_head_measures`.

### `tests/test_clues_mapping.py` (test)

**Analog:** `tests/test_clues.py` (lines 1-90).
```python
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
CFG = load_config(MINI)
TEXTS = load_texts(MINI_CONTENT_DIR / "texte.toml")
CLUES = load_clues(MINI_CONTENT_DIR / "clues.toml")

def _codes(issues): return [(issue.code, issue.path) for issue in issues]

def test_a_single_clue_for_an_attack_is_too_few():
    issues = check_clues(CFG, TEXTS, _without(_of("ot")[0]))
    assert _codes(issues) == [("clues.too_few", "clues.ot")]

clues[1] = dataclasses.replace(clues[1], quote="...")     # mutate frozen Clue via dataclasses.replace
assert _codes(check_clues(CFG, TEXTS, tuple(clues))) == [("clues.quote_not_found", "clues[2]")]
```
Same style for each new code (remove the only clue for a bonus measure -> `clues.unsupported_bonus`; swap weights to break monotonicity -> `clues.not_graduated`). Also update `tests/test_clues.py` `HEADER` constant (line 23) and `test_texts_*`, `test_story_veil`, `test_veil_*` if the header or texts change. Story edits must pass: `uv run planspiel texts`, `clues`, digit allowlist, giveaway list, veil scan.

### `content/clues.toml`, `tests/fixtures/mini_content/clues.toml` (content)

**Analog** (mini clues.toml lines 1-20): `[[clue]]` with `attack`, `source`, `quote`, `why`. Add `measures = ["M5"]` and `weight = 3` per RESEARCH Code Examples; empty list allowed for atmospheric clues. M6 and M2 currently have no clue (RESEARCH Q9). Candidate story edits live in a candidate content dir (`--content-dir`) until BAL-05.

---

### `planspiel/balance.py` (BAL-04/07; utility, batch)

**Analog:** itself plus `refpaths.reference_path`. Current: hard-coded `define_strategies()` (balance.py:26) with stale cost comments, `run_analysis(config_path=DEFAULT_CONFIG_PATH)` (270), `main(argv=None)` ignoring args (400), `POSITIVE_KZ_THRESHOLD = 50` (line 14; "wird in Phase 6 (BAL-08) überprüft"). Replace with `reference_strategies` from config and a `--config` flag. Imports to keep (balance.py:6-12):
```python
from planspiel import rules
from planspiel.cli import configure_utf8_stdio
from planspiel.config import DEFAULT_CONFIG_PATH, load_config
from planspiel.report import REFERENCE_LABEL
```
Root wrappers (`balance_analysis.py`, `simulate_outcomes.py`, `analyze_simulation_results.py`) are 6-line shims and must keep working (`tests/test_wrappers.py`).

### `tests/test_balance_report.py` (test; BAL-04)

**Analog:** `tests/test_final_index_config.py` (mini config, `summarize_tier`, `enumerate_tier`, `contextlib`/`io` capture of printed output, digest pins) and `tests/test_wrappers.py`. Assert in-budget-only top-K and Pareto, unfiltered optima, percentile blocks, and that `balance --config` works.

---

### Candidate config for slow checks (partial analog)

`tests/support/__init__.py:4-7` fixes `CONFIG_PATH = REPO_ROOT / "simulation_config.json"` and `harness.load_config()` defaults to it. No override exists. Recommended: add an env var or pytest option read by a shared fixture (extend `tests/conftest.py`, which already provides `update_golden` and `golden_report`), defaulting to `CONFIG_PATH`. Never edit `simulation_config.json`, `content/` or goldens before the D-04 approval. Candidate lives at `.planning/phases/06-rebalance/candidate_config.json`; real tools run with `--config` (`validate`, `gate`, `tausch`, `referenzpfade`, `texts`, `clues`, `print`, `simulate_outcomes.py`).

---

### `simulation_config.json` `reference_strategies` and tuned values (config)

**Analog:** `reference_plans` block (line 301):
```json
"reference_plans": { "<tier>": {"start": {"M1": 2, ...}, "windows": [ {"selection": {...}, "swap": ["M4","M6"]} ]}}
```
Add top-level `reference_strategies: {tier: {name: {kind, start, windows}}}` (RESEARCH Q8). Final index block becomes `{"weight_kz": 1, "weight_ros": 20}` (integers, candidate k 15/20/25). Exfil fix: `"mitigation_cap": 7, "base_severity": 7, kz -5 .. 9` (slope 2.0) as in RESEARCH Code Examples. Order of change: config -> README -> print.

### Goldens and print (BAL-05 only)

Re-pin via `--update-golden` after approval: `characterization_{tier}.json` (fast, `test_characterization.py`), `digest_{tier}.json` (slow, `test_digest.py`), `gate_{tier}.json` (slow), `answer_keys.json` (`test_master_model.py`), `welle0.json`, `worksheet_tex.json` (`test_welle0_golden.py`, `test_welle0_render.py`; first `practice.check_example`). Then `uv run planspiel referenzpfade`, review `booklet.MAX_PENALTY_ROWS` (cap 12, rows = ceil(100/X)) and `MAX_WINDOWS = 2`, `uv run planspiel print`, `print --check`.

## Shared Patterns

### Issue/validator codes
**Source:** `planspiel/validate.py` (`self.error(code, path, German message)`), `planspiel/texts.py` `Issue("error", code, path, message)`.
**Apply to:** `reference_strategies`, `hand_calc` severity, new `clues.*` codes. Codes are `<area>.<name>`, paths are JSON-style (`waves[0].weights`, `clues[2]`), messages German.

### Exact arithmetic and rounding
**Source:** `planspiel/rounding.py` (`round_half_away_frac`, `started_steps`, `exact_to_json`), `Fraction` everywhere in `rules.py`.
**Apply to:** every new metric, final index, importance score. Builtin `round()` is forbidden in `rules.py`/`rounding.py`; `tests/test_single_definition.py` guards a single formula definition.

### Three-way test pattern (no mocks)
**Source:** `tests/test_overspend_gate.py`.
**Apply to:** all BAL check tests. (1) synthetic columns, milliseconds; (2) brute force on `tests/fixtures/mini_config.json` (M1, M2, M4, M6; 256 plans) via `tests/support/harness`; (3) `@pytest.mark.slow` real-config test with `check_golden(path, data, update_golden, golden_report)`. Default `addopts = -m 'not slow and not pdf'`.

### CLI command shape
**Source:** `planspiel/cli.py` (`_gate_command`, subparsers each with `--config default="simulation_config.json"`, function-local imports, exit 0/1, German output via `configure_utf8_stdio`).
**Apply to:** `gate --paths`, `validate` (level error), a balance/calibrate command.

### Column store as cache
**Source:** `planspiel/enumerate.py` `ResultStore.column(name)`; columns `code_index, kz_final, own_cost, total_cost, damage_eur, over_budget, kz_pre_review, remaining`. Min X is independent of config X; the review-tier list, tier budget, step and final-index weights are sweepable from columns without re-enumeration.
**Apply to:** calibrate report, tuning loop. `kz_after` per wave is not stored (BAL-08 comeback needs `TierTables.change` or a new `kz_after_1` column).

### Prose without digits, config as only number source
**Source:** CLAUDE.md, `content/digit_allowlist.toml`, `giveaway_terms.toml`.
**Apply to:** clue/story edits and any new `texte.toml` key (e.g. `clue_head_measures`).

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `planspiel/metrics.py` | utility | transform | No existing metrics module; build from `gate.py` and `report.py` idioms (partial analog only) |
| Candidate-config test option | test support | config | Tests are hard-wired to `CONFIG_PATH`; needs a small new fixture/option in `tests/conftest.py` |
| Vectorised numpy engine (optional) | test support | batch | No second encoding exists in `tests/support/`; closest is `tests/support/worksheet_replay.py` (independent second encoding with conformance test). Requires a `checkpoint:human-verify` before `uv add --dev numpy` (audit verdict SUS) |

## Metadata

**Analog search scope:** `planspiel/` (gate, report, validate, config, texts, refpaths, balance, cli, rules), `tests/` (gate, clues, reference plans, final index, swap layer, support, fixtures, golden), `simulation_config.json`.
**Files scanned:** ~30 read or grepped.
**Pattern extraction date:** 2026-10-28
