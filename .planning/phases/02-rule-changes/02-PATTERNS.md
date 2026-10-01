# Phase 2: Rule Changes - Pattern Map

**Mapped:** 2026-10-01
**Files analyzed:** 27 (new/modified, grouped)
**Analogs found:** 24 / 27 (3 with no in-repo analog: path evaluator, lowering closure, tier tables)
**Line numbers** refer to the live code on 2026-10-01 (before any Phase 2 edit). They will shift as RULE-08 lands first; re-grep by function name.

Execution order (02-RESEARCH): RULE-08, 06, 07, 03, 01, 02, 05, 04. One plan per requirement.

## File Classification

| New/Modified File | Req | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|---|
| `planspiel/rules.py` (remove `e_target_check`, simplify `wave_kz_change`, `TierKernel`, `CompactOutcome`) | 08 | service (formulas) | transform | itself (`TierKernel`, lines 107-109, 292-294, 464-564) | exact |
| `planspiel/rules.py` (`BudgetLedger`+`security_spend`, `ros` input, `evaluate_plan`) | 06 | service | transform | `budget_ledger` (lines 403-418) | exact |
| `planspiel/rules.py` (`_tier_lookup` domain, `budget_review_delta`, `evaluate_event` branch) | 07, 03 | service | transform | `_tier_lookup` (179-188), `apply_final_events` (421-434) | exact |
| `planspiel/rules.py` (`swap_possible/legal/credit`, `kurswechsel` branch in `evaluate_event`) | 01 | service | transform | `evaluate_event` `noop` branch (203-208) | role-match |
| `planspiel/rules.py` (`Path`, `Window`, `window_cost`, `evaluate_path`) | 02, 05 | service | batch / transform | `simulate_selection` (297-374) + `evaluate_plan` (437-461) | role-match |
| `planspiel/rules.py` (`TierTables`) | 04 | service | batch | `TierKernel` memo tables (476-491) | partial |
| `planspiel/config.py` (drop `e_targets`, `kz_bonus/malus`; penalty fields) | 08, 03 | model/config | CRUD (load) | itself (lines 36-37, 63, 134, 168-169) | exact |
| `planspiel/validate.py` (drop E-target checks; new codes; `kurswechsel` type) | 08, 07, 03, 01, 05 | validator | request-response | `event_final_budget_tier` / `check_tiers` / `check_event` / `check_hand_calc` | exact |
| `planspiel/enumerate.py` (`STORE_LAYOUT` + `kz_pre_review`, `remaining`) | 03 | store | batch | itself (lines 10-17, 38-45) | exact |
| `planspiel/report.py` (`ros_of`, `entry`, `dump_record`; drop `e_reached`) | 06, 08 | utility | transform | itself (lines 69-135, 276-289) | exact |
| `planspiel/analyze.py`, `planspiel/balance.py`, `planspiel/simulate.py` | 06, 08 | consumers | transform | themselves | exact |
| `planspiel/gate.py` (NEW) | 04 | service | batch | `planspiel/enumerate.py` + `report.summarize_tier` (columns over `ResultStore`) | role-match |
| `planspiel/review_text.py` (NEW) | 07, 03 | utility | transform | `planspiel/rounding.py` (small pure-function module, German print rule in docstring) | role-match |
| `planspiel/cli.py` (`planspiel gate`) | 04 | controller (CLI) | request-response | `_validate_command` + `main` subparser (13-54) | exact |
| `simulation_config.json` | 08, 07, 03, 01 | config | CRUD | `final_events`, `events.wave_1` (233-305) | exact |
| `tests/fixtures/mini_config.json` | 08, 07, 03, 01 | config | CRUD | itself (`e_targets` l.13-33, `kz_malus` 52-93, `noop` 345) | exact |
| `tests/test_single_definition.py` | all | test (AST guard) | transform | itself (17-80) | exact |
| `tests/test_kernel_conformance.py` | 08, 06, 03 | test | transform | itself (29-90) | exact |
| `tests/test_digest.py`, `tests/support/digest.py`, `harness.py`, `golden_cases.py` | 08 | test support | batch | themselves | exact |
| `tests/test_e_target_removed.py` (NEW) | 08 | test | request-response | `tests/test_validate.py` (`_raw`, `_set`, `_delete`, `validate`) | role-match |
| `tests/test_ros_ledger.py` (NEW) | 06 | test | transform | `tests/test_rules_semantics.py` (1-70) | exact |
| `tests/test_budget_review_text.py`, `tests/test_budget_review.py` (NEW) | 07, 03 | test | transform | `test_kernel_conformance.py` `apply_final_events` tests (73-88) | exact |
| `tests/test_kurswechsel.py`, `tests/test_paths.py`, `tests/test_sparprogramm.py` (NEW) | 01, 02, 05 | test | transform | `test_rules_semantics.py` + mini config fixture | role-match |
| `tests/test_overspend_gate.py` + `tests/golden/gate_<tier>.json` (NEW) | 04 | test (slow) | batch | `tests/test_digest.py::test_full_digest_matches` | exact |
| `README.md`, root `CLAUDE.md`, `.planning/PROJECT.md`, `STATE.md` | 08, 06, 01, 02, 03, 05 | doc | n/a | existing README sections (lines 55-60, 129, 138-190) | exact |

## Pattern Assignments

### `planspiel/rules.py` - RULE-08 removal (service, transform)

**Analog:** the current `TierKernel` and `wave_kz_change`.

**Rounding point to simplify** (lines 107-109). New signature `wave_kz_change(attack_kz_delta, event_kz)`; keep the single rounding point:
```python
def wave_kz_change(e_target_delta, attack_kz_delta, event_kz) -> int:
    """Einziger Rundungspunkt: KZ-Änderung der Welle (Angriff + E-Ziel + Events), ab ,5 vom Betrag aufrunden."""
    return round_half_away_frac(Fraction(e_target_delta) + attack_kz_delta + Fraction(event_kz))
```
Update the docstring too (drop "E-Ziel"); same text appears in `planspiel/rounding.py` lines 7-8 (docstring "Angriff + E-Ziel + Events").

**Kernel memo to cut** (lines 483-491, 508-544): remove the 4th element `self.tier.e_targets[...]`, `self._e_target`, the `target_key` block, and `e_reached`; the change memo key becomes:
```python
change_key = (index, reduction, event_kz)
change = self._change.get(change_key)
if change is None:
    change = self._change[change_key] = wave_kz_change(attack_kz, event_kz)
```
Also remove `e_reached` from `CompactOutcome` (line 473) and from `simulate_selection` (lines ~327-329, 351-352, 360 per research). `e_value_scaled` stays (still used for reduction).

**Test follow-up:** `tests/test_kernel_conformance.py` lines 63-70 (`test_e_target_check_*`) are deleted; `_digest_view` (29-44) drops `e_reached` from the `waves` entries; `tests/test_enumeration.py` `_outcome(...)` (53-64) drops `e_reached=`.

---

### `planspiel/rules.py` - RULE-06 ledger split (service, transform)

**Analog:** `budget_ledger` / `BudgetLedger` (lines 403-418) and `evaluate_plan` (437-461).

**Current shape to extend:**
```python
class BudgetLedger(NamedTuple):
    total_cost: int
    budget_available: int
    over_budget: bool
    remaining_budget: int

def budget_ledger(tier_budget: int, own_cost: int, event_opex: int, event_budget: int) -> BudgetLedger:
    total_cost = own_cost + event_opex
    budget_available = tier_budget + event_budget
    return BudgetLedger(
        total_cost=total_cost,
        budget_available=budget_available,
        over_budget=over_budget(total_cost, budget_available),
        remaining_budget=budget_available - total_cost,
    )
```
Add `security_spend` (= `own_cost`) as a field; keep `total_cost` as the budget total (digest-stable).

**The one-line RoS fix** (line 460): `evaluate_plan` currently passes the budget total:
```python
outcome["ros"] = ros(base_losses(cfg.waves, cfg.attacks), outcome["total_damage"], ledger.total_cost)
```
Change to `ledger.security_spend`; add `"security_spend"` to `outcome["costs"]` (lines 450-457). Same fix at three other call sites:
- `planspiel/enumerate.py:61` `rules.ros(self.base_losses, Fraction(damage_eur, 1000), total_cost)` -> use `columns["own_cost"][i]`.
- `planspiel/report.py:88` `ros_cache[key] = rules.ros(base, Fraction(key[0], 1000), key[1])` (key built from `total_col`, line 76) -> key on `own_cost`; also the percentile filter `own != 0` and `entry()` (lines 112-125).
- `planspiel/report.py:277` `dump_record`: `rules.ros(base_losses, Fraction(outcome.damage_eur, 1000), outcome.total_cost)` -> `outcome.own_cost`.
`ros` itself (lines 384-388) is unchanged (parameter rename only: `total_cost` -> `own_spend`).

**Test pattern to copy** (`tests/test_rules_semantics.py` 12-22): `ros(620, 0, 0) is None`; exact `Fraction` equality; property test = same selection on a config copy with all event OPEX/budget zeroed gives identical `rec["ros"]`.

**WR-06 incidental fix:** `final_index(kz_final, ros, weight_kz, weight_ros)` (lines 391-396) returns bare `kz_final` when `ros is None` ignoring `weight_kz`; fix to `weight_kz * kz_final`. Existing tests `test_final_index_*` (rules_semantics 25-31) show the call style.

---

### `planspiel/rules.py` - RULE-07 / RULE-03 Budget Review (service, transform)

**Analog:** `_tier_lookup` (179-188), `evaluate_event` `final_budget_tier` branch (246-248), `apply_final_events` (421-434).

**Current lookup (no domain check, fix WR-07):**
```python
def _tier_lookup(value: float, tiers: List[List[float]]) -> float:
    result = tiers[0][1]
    for min_inclusive, tier_value in tiers:
        if value >= min_inclusive:
            result = tier_value
    return result
```
Add: raise `ValueError` when `value < tiers[0][0]` (first minimum is 0 after RULE-07). `checklist_tier` also uses it (line 223) with tiers starting at 0; check its config first minimum is 0 before adding the raise.

**Branch to replace** (lines 246-248):
```python
if event.type == "final_budget_tier":
    kz_delta = _tier_lookup(remaining_budget, p["tiers"])
    return kz_delta, 0, 0, f"Restbudget {remaining_budget:.0f}k€"
```
New: `kz_delta = budget_review_delta(remaining_budget, p["tiers"], p["overspend_penalty"]["kz_per_step"], p["overspend_penalty"]["step"])`; negative branch first: `-penalty * started_steps(-remaining, step)`. **Unit trap:** ledger is in k EUR; `started_steps(amount, step_eur=10_000)` defaults to euros. Pass `step=10` explicitly (config `step` in k EUR). Import: `from planspiel.rounding import round_half_away_frac, started_steps`.

**Application order stays** (`apply_final_events`, 421-434): `kz = clamp_kz(kz + ev_kz)` once after the last wave.

**Existing tests that must stay green / get new siblings** (`tests/test_kernel_conformance.py` 73-88):
```python
def test_apply_final_events_boundary_is_inclusive():
    cfg = harness.load_config()
    kz, records = rules.apply_final_events(cfg.final_events, {}, 25, 50)
    assert kz == 55
    assert list(records[0]) == ["id", "name", "effect_description", "kz_delta"]

def test_apply_final_events_negative_remaining_budget():
    cfg = harness.load_config()
    assert rules.apply_final_events(cfg.final_events, {}, -1, 50)[0] == 35   # becomes 50 - X (50 - 9 = 41)
```
The `-1` test value changes with the linear penalty (flat -15 -> -X); update it in RULE-03. Add boundary cases at deficit 0, 10, 11, 20, 21 k EUR.
Also `tests/test_rules_semantics.py:64-68` (`final_events[0]["kz_delta"] == -15`, all-L3 low) changes: compute from X and started steps.

---

### `planspiel/rules.py` - RULE-01 Kurswechsel leaf functions (service, transform)

**Analog:** `evaluate_event` branch layout (203-250): one `if event.type == ...:` returning `(kz_delta, opex_delta, budget_delta, description)`.

**Replace the `noop` branch** (lines 203-208) with a `kurswechsel` branch returning zeros plus a fixed German description ("im Referenzplan nicht angewendet"), same 4-tuple:
```python
if event.type == "noop":
    return 0, 0, 0, "Kurswechsel: kostenneutral angenommen (Spielerentscheidung, nicht simuliert)"
```
New leaf functions (signatures from 02-RESEARCH Pattern 2: `swap_possible(selection)`, `swap_legal(wave1, window_end, dropped, incoming)`, `swap_credit(measures, wave1, dropped, incoming, window_end)`) follow the style of `dependencies_satisfied` (lines 8-16): plain functions taking `Dict[str, int]` and `Dict[str, Measure]`, level data via `measures[id].levels[level].init`. These `.init` reads are legal only inside `rules.py` (operand guard).

---

### `planspiel/rules.py` - RULE-02 / RULE-05 path evaluator (service, batch)

**Analog:** `evaluate_plan` (437-461) for the orchestration order and `simulate_selection` (297-374) for the per-wave loop. **No in-repo analog for per-wave selections** (the current code reuses one selection for all waves); this is the deliberate new part.

**Orchestration order to copy** (lines 437-461): `compute_costs` -> `simulate_selection` -> `budget_ledger` -> `apply_final_events` -> assemble `outcome["costs"]` / `over_budget` / `ros`. `evaluate_path` must call the same primitives (`compute_cia`, `apply_attack`, `apply_events`, `wave_kz_change`, `clamp_kz`, `budget_ledger`, `apply_final_events`) once per wave with the selection in force in that wave. D-07 check reuses `dependencies_satisfied(sel, cfg.measures)` (lines 8-16).

**Conformance pattern to copy:** `tests/test_kernel_conformance.py` `test_kernel_equals_evaluate_plan_on_golden_cases` (starts line 91) is the template for `evaluate_path(Path(s, ())) == evaluate_plan(s)` (golden cases + all 256 mini plans).

Do NOT reuse `compute_costs` for moves (it is `init + opex * waves`, lines 28-36); add `window_cost` (net-change pricing, D-27) beside it.

---

### `planspiel/rules.py` - RULE-04 `TierTables` (service, batch) - partial analog

**Analog:** `TierKernel` memoization (`self._e_scaled`, `self._attack`, `self._change` dicts, lines 488-491, 508-544). Tables must be built from kernel primitives inside `rules.py` and exposed as `array` objects, because `.init/.opex/.weights/.bonus` reads outside `rules.py`/`config.py` fail `test_no_formula_operands_outside_rules_and_config`. Phase 2 may defer the path layer to Phase 6 (D-25); the static gate does not need `TierTables`.

---

### `planspiel/validate.py` (validator, request-response)

**Analog for every new check:** existing `event_*` handlers and `check_tiers`.

**Event-type registry to edit** (lines 10-30): replace `"noop"` with `"kurswechsel"` in both `KNOWN_EVENT_TYPES` and `REQUIRED_EVENT_PARAMS` (`"kurswechsel": ()`); add `"final_budget_tier": ("tiers", "overspend_penalty")`.

**Handler convention** (lines 419-422, 472-473): dispatch is `getattr(self, f"event_{event_type}")(event, path, measures)`, so add `event_kurswechsel` (no-op `pass`, like `event_noop` at 421) and extend `event_final_budget_tier`:
```python
def event_final_budget_tier(self, event: dict, path: str, measures: dict) -> None:
    self.check_tiers(event["tiers"], f"{path}.tiers")
```
New body also: `penalty = event["overspend_penalty"]`; `self.container(penalty, dict, ...)`; `self.int_value(penalty["kz_per_step"], f"{path}.overspend_penalty.kz_per_step", lo=1)`; same for `step`; and a first-minimum-0 error with code `schema.tiers_order` (add to `check_tiers` via a parameter, e.g. `first_minimum=0`; `check_tiers` at 475-494 already emits `schema.tiers_order` for non-ascending minima).

**Placement rule pattern** (lines 412-414):
```python
if (event_type == "final_budget_tier") != final:
    where = "nur in final_events" if event_type == "final_budget_tier" else "nicht in final_events"
    self.error("schema.event_placement", path, f"Event-Typ {event_type} ist {where} erlaubt")
```
Extend for `kurswechsel` (not in `final_events`, not in the last wave). `schema.kurswechsel_count` is a new error emitted from `check_events` (378-391) after the loop.

**Warning pattern** (lines 563-564, in `check_hand_calc` 543-596): `self.warning("hand_calc.severity_cap", path, f"...")`. Copy for `hand_calc.penalty_step` (step != 10), `hand_calc.penalty_x` (X > 5, D-18 marker), `rules.event_without_window` (negative `flat_budget` in last wave), `schema.removed_key` (leftover `e_targets`/`kz_bonus`/`kz_malus`).

**Remove** (lines 330-331 `kz_bonus`/`kz_malus` `int_field`; lines 366-376 `e_targets` block, code `schema.e_targets`).

**Known test impact:** `tests/test_validate.py:31-40` pins "exactly one warning (`hand_calc.kz_slope`)". A `hand_calc.penalty_x` warning at X = 9 would break `test_real_config_has_no_errors_and_one_slope_warning`; either update that test deliberately (the research phase gate says "17/7 warning remains") or fire `penalty_x` only above a documented threshold. Decide in the RULE-03 plan; flag it.

**Test helpers to copy** (`tests/test_validate.py` 19-70): `_raw(path)`, `_errors(issues)`, `_warnings(issues)`, `_set(path_parts, value)`, `_delete(path_parts)` mutators applied to `copy.deepcopy(raw)`.

---

### `planspiel/enumerate.py` (store, batch) - RULE-03

**Analog:** itself. Column registry and append (lines 10-17, 38-45):
```python
STORE_LAYOUT = (
    ("code_index", "I"),
    ("kz_final", "B"),
    ("own_cost", "H"),
    ("total_cost", "i"),
    ("damage_eur", "I"),
    ("over_budget", "B"),
)
...
columns["kz_final"].append(outcome.kz_final)
columns["over_budget"].append(1 if outcome.over_budget else 0)
```
Add `("kz_pre_review", "B")` and `("remaining", "h")`; extend `append` and `CompactOutcome` (`rules.py:464-473`) with `kz_pre_review` and `remaining`. `bytes_per_record` is computed from columns (line 67-69), so the docstring "16-byte record" and any perf test asserting it (`tests/test_enumeration_perf.py`) need updating. `tests/test_enumeration.py` asserts `STORE_LAYOUT` and `ENTRY_KEYS` (lines 35-45), adjust.

---

### `planspiel/gate.py` (NEW; service, batch) - RULE-04

**Analog:** `planspiel/enumerate.py` for column access over `ResultStore` (`store.column("kz_final")`, `store.record(i)`, lines 50-65) and `planspiel/report.py` `summarize_tier` (69-135) for iterating columns without materialising records.

**Core pattern:** use the lowering closure and `required_x` from 02-RESEARCH "Code Examples" (lines 608-625) verbatim; they are verified against brute force. Index convention: `code_index` is the lattice index (measure 0 most significant, base 4, same as `code_from_index` in enumerate.py:78-84). No in-repo analog for the closure; use RESEARCH.

**Do not reimplement enumeration:** call `enumerate_tier(cfg, tier_name)` and read the new columns (`kz_pre_review`, `remaining`). Register `lowering_closure` and `required_penalty_x` in `FORMULA_FUNCTIONS` mapped to `planspiel/gate.py`.

---

### `planspiel/review_text.py` (NEW; utility, transform) - RULE-07 / RULE-03

**Analog:** `planspiel/rounding.py`: small, pure, exact-integer functions with a German "Druckbare Regel" docstring (lines 4-13, 20-28). Copy the functions `eur`, `boundary_text`, `penalty_rows` from RESEARCH "Boundary text and penalty rows" (lines 654-668). Parse-back test must read numbers out of the generated string with simple anchored regexes, not from the tier list.

---

### `planspiel/cli.py` (controller, request-response) - RULE-04

**Analog:** `_validate_command` and the subparser wiring (lines 13-54). New `gate` subcommand mirrors it:
```python
subparsers = parser.add_subparsers(dest="command")
validate_parser = subparsers.add_parser("validate", help="Prüft die Konfiguration auf Fehler und Handrechenbarkeit.")
validate_parser.add_argument("--config", default="simulation_config.json", help="Pfad zur Konfigurationsdatei.")
...
return _validate_command(args.config, args.strict)
```
Note `main` currently dispatches unconditionally to `_validate_command` after the `None` check (line 54); adding a second command requires a dispatch on `args.command`. Imports stay lazy inside the command function (lines 14-15). Output via `print`, German, 0/1 exit code, `configure_utf8_stdio()` at the top of `main`.

---

### `planspiel/config.py` (model) - RULE-08 / RULE-03

Remove `Wave.kz_bonus/kz_malus` (lines 36-37), `BudgetTier.e_targets` (63), loader reads (134, 168-169). `Event.params` already carries arbitrary per-type params (used as `event.params` in `evaluate_event` line 201), so `overspend_penalty` and `tiers` need no dataclass change; they arrive via `event.params`. Verify how `final_events` loads params before assuming it (read `config.py` lines 120-212 when planning RULE-03).

---

### `simulation_config.json` and `tests/fixtures/mini_config.json` (config)

**Analog for the final event** (lines 296-305, current):
```json
"final_events": [{
  "id": "budget_review", "name": "Budget Review",
  "description": "Nach Abschluss wird das Restbudget geprüft: <0 EUR -> KZ -15, 0-25.000 -> KZ 0, ...",
  "type": "final_budget_tier",
  "tiers": [[-100000, -15], [0, 0], [25, 5], [50, 10], [75, 15]]
}]
```
Target shape: see 02-RESEARCH "Config Schema and Validator" (tiers `[[0,0],[25,5],[50,10],[75,15]]` + `"overspend_penalty": {"kz_per_step": 9, "step": 10}`; description reduced to the German intro, boundary text generated).

**Kurswechsel event** (lines 233-239, current `"type": "noop"`, description says "Maßnahmenwechsel"): change type to `kurswechsel`, rewrite the description with D-09..D-11 and the single term "Maßnahmentausch" (real umlauts; `tests/test_config_text.py` rejects transliterations). Event ids stay ASCII.

**Sparprogramm** (lines 250-255): unchanged type `flat_budget`; description may mention the change window (RULE-05).

**E-target keys to delete:** `budget_tiers.*.e_targets`, `waves[].kz_bonus`, `waves[].kz_malus` (mini config: `e_targets` lines 13/23/33, `kz_malus` 52/79/93, plus the `kz_bonus` siblings; `noop` at 345).

---

### `tests/test_single_definition.py` (test, AST guard) - every plan

**Pattern (lines 17-58):** names must be defined exactly once and in the mapped module.
```python
FORMULA_FUNCTIONS = {name: RULES for name in ("dependencies_satisfied", ..., "budget_ledger", "e_target_check", "apply_final_events")}
FORMULA_FUNCTIONS.update({name: ROUNDING for name in ("round_half_away", "round_half_away_frac", "started_steps")})
RETIRED_FUNCTIONS = {"calculate_ros", ...}
OPERAND_ATTRIBUTES = {"s_unit", ..., "e_threshold", "kz_bonus", "kz_malus", "recovery", "init", "opex", "weights", "bonus"}
```
Edits: move `e_target_check` to `RETIRED_FUNCTIONS` and drop `kz_bonus`/`kz_malus` from `OPERAND_ATTRIBUTES` (RULE-08); add `budget_review_delta`, `security_spend`, `window_cost`, `swap_possible`, `swap_legal`, `swap_credit`, `evaluate_path` (RULES); `lowering_closure`, `required_penalty_x` -> `planspiel/gate.py`; `boundary_text`, `penalty_rows` -> `planspiel/review_text.py` (add `GATE = "planspiel/gate.py"`, `REVIEW_TEXT = ...` constants like `RULES`); add `kz_per_step`, `overspend_penalty` to `OPERAND_ATTRIBUTES`. Note the operand scan (121-130) covers all `planspiel/*.py` except `rules.py`/`config.py`: `gate.py`, `review_text.py` and `enumerate.py` must never read `.init/.opex/...` or `.kz_per_step`.

---

### Golden / digest process (D-20; RULE-08 G1, RULE-06 G2, RULE-03 G3)

**Analog:** `tests/test_digest.py` lines 13-18 and `tests/support/golden.py` `check_golden` (156-169):
```python
@pytest.mark.slow
@pytest.mark.parametrize("tier", TIERS)
def test_full_digest_matches(tier, update_golden, golden_report):
    cfg = harness.load_config()
    path = REPO_ROOT / "tests" / "golden" / f"digest_{tier}.json"
    check_golden(path, compute_digest(cfg, tier), update_golden, golden_report)
```
`--update-golden` is defined in `tests/conftest.py` (7-13), the `update_golden` / `golden_report` fixtures at 16-23; the report prints at terminal summary. Gate golden `tests/golden/gate_<tier>.json` copies this exactly (`check_golden(path, gate_result_dict, update_golden, golden_report)`).

Sensitivity test to repair (RULE-08): `test_digest_is_deterministic_and_sensitive` (21-32) mutates `mutated["waves"][0]["kz_malus"] -= 1`; pick another KZ-relevant field (e.g. `waves[0]["e_threshold"]` or an attack `kz_at_full_damage`). Support files to patch: `tests/support/digest.py` (`canonical_line` includes `e_reached`), `harness.py` (`compact_from_plan`, line 59), `golden_cases.py` (`census:e_eq_target_w*`, `kz_delta_e_target`).

D-20 checkpoint must be a human-verify task with the diff report (KZ changed counts per tier, best in-budget vs over-budget before/after, in-budget count unchanged; expected values M3 in RESEARCH: 512,006 / 648,246 / 739,828 changed, in-budget 69,454 / 124,321 / 197,753).

---

### README.md (doc)

Sections to rewrite (current text):
- Step 4c "E-Ziel prüfen (KZ-Bonus/Malus)" and step 5 "Change-Fenster ... mit Kommunikationseffekten auf KZ" (lines ~55-60).
- "Rundung" bullet, line 129: "Angriff + E-Ziel + Events" -> "Angriff + Events".
- "Change-Fenster (Planbarkeit + Agency)" lines 140-145: replace with D-01..D-07 (Levelwechsel up/down, cancel, add; no Change-Gebühr, no Kommunikationseffekt, no Zwangs-Change; Init differences immediately, effects next wave, no refund, dependencies valid, unlimited moves, net pricing).
- Table 1 row line 169 ("Change-Fenster | Upgrades/Swaps | ... | Kommunikation (KZ-Effekt)") and Parametrisierung line 187 ("E-Ziel/Change-Kommunikation").
- New short sections "Kurswechsel (Maßnahmentausch)" and "Budget Review und Überziehung" (symbolic, no fixed numbers; numbers only in generated text).
Style: German, `‑` (non-breaking hyphen) is used in headings like "Change‑Fenster"; keep it.

## Shared Patterns

### Single formula definition
**Source:** `tests/test_single_definition.py` 17-58, 121-130
**Apply to:** every new function in `rules.py`, `gate.py`, `review_text.py`; every plan registers its functions in the same commit as the code (a missing registration is not caught, a duplicate definition is).

### Exact arithmetic and one rounding per wave
**Source:** `planspiel/rounding.py` 4-28; `rules.wave_kz_change` 107-109
**Apply to:** every new KZ effect. No `round()`; `Fraction`/int only; round once with `round_half_away_frac`, then `clamp_kz` (0..100). Penalty uses `started_steps(amount, step)` with an explicit step in the amount's unit.

### Event dispatch
**Source:** `evaluate_event` (rules.py 191-250), `check_event` + `event_<type>` handlers (validate.py 393-473)
**Apply to:** `kurswechsel`, extended `final_budget_tier`. Add the same type string in `KNOWN_EVENT_TYPES`, `REQUIRED_EVENT_PARAMS`, `evaluate_event`, a validator `event_<type>` method, and the mini config.

### Validator issue style
**Source:** validate.py 108-112 (`self.error(code, path, msg)` / `self.warning(...)`), JSON-path strings like `f"{path}.overspend_penalty.kz_per_step"`; messages in German.
**Apply to:** all new codes in the table in RESEARCH "New validator codes".

### Golden snapshot changes
**Source:** `tests/conftest.py`, `tests/support/golden.py`, `tests/test_digest.py`
**Apply to:** RULE-08 (G1), RULE-06 (G2, `ros` only), RULE-03 (G3). Regenerate only via `uv run pytest --update-golden` (+ `-m slow` for digests) after human approval.

### Test layout
**Source:** `tests/test_rules_semantics.py` (module-level `load_config(CONFIG_PATH)`, small pure assertions); `tests/test_enumeration.py` 48-50 (`@pytest.fixture(scope="module") def mini()` -> `harness.load_config(MINI)`); slow tests with `@pytest.mark.slow`; commands via `uv run pytest`.
**Apply to:** all new tests; RED test commit before GREEN.

### Config text language
**Source:** `tests/test_config_text.py` (rejects transliterations such as "massnahm", "ueber", "pruef") and `tests/test_encoding_lint.py`.
**Apply to:** all new/changed config descriptions, README text, generated card text.

## No Analog Found

| File / Function | Role | Data Flow | Reason |
|---|---|---|---|
| `evaluate_path`, `window_cost` per-wave selection model | service | batch | Existing code applies one selection to all waves; use RESEARCH Pattern 1 + "Path evaluator skeleton" (lines 629-650) |
| `gate.lowering_closure` (4^n prefix-max DP) | service | batch | No lattice/DP code exists; use RESEARCH code (lines 610-625) |
| `TierTables` (per-state arrays, path families) | service | batch | Nothing equivalent; optional (slow path layer, deferrable to Phase 6 per D-25) |

## Metadata

**Analog search scope:** `planspiel/` (all modules), `tests/` (all top-level tests, `support/`, `conftest.py`, `fixtures/`, `golden/` listing), `simulation_config.json` (events and final_events), `README.md` (change-window sections), root and `.claude/CLAUDE.md`.
**Files scanned:** about 20 read or grepped; `sim_*.json`/`simulation_*.json` not touched.
**Pattern extraction date:** 2026-10-01
**Caveats for the planner:**
- Line numbers shift after RULE-08; plans should cite function names.
- `tests/test_validate.py:31-40` (exactly one warning) and `tests/test_rules_semantics.py:64-68`, `tests/test_kernel_conformance.py:81-83` (flat -15 / `35`) are tests that RULE-03 must update deliberately.
- `planspiel/cli.py:54` dispatches unconditionally to validate; RULE-04 must add real command dispatch.
- `planspiel/config.py` lines 120-212 not read in this mapping; read before writing the RULE-03/08 config tasks.
