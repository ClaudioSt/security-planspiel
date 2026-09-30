# Phase 1: Simulation Foundation - Pattern Map

**Mapped:** 2026-09-30
**Files analyzed:** 32 (new/modified)
**Analogs found:** 9 code-source analogs / 32 (the rest are greenfield: no tests, package or pyproject exist)

Scope note: the only existing Python is the three simulation scripts (`simulate_outcomes.py` 620 lines, `analyze_simulation_results.py` 197, `balance_analysis.py` 430) plus the untouched generators. Most new files have no analog and use the verified snippets in `01-RESEARCH.md` § Code Examples. For the `planspiel/*` modules the "analog" is the source of the logic being moved verbatim (D-05 step 2: zero snapshot diff, so do not reorder float operations).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog / Source | Match Quality |
|---|---|---|---|---|
| `planspiel/config.py` | config loader + dataclasses | file-I/O, transform | `simulate_outcomes.py` L10-74 (dataclasses), L76-172 (`load_config`) | move (exact) |
| `planspiel/validate.py` | validator | transform | none (RESEARCH Q8 lists checks) | no analog |
| `planspiel/rounding.py` | utility | transform | none (RESEARCH § Code Examples) | no analog |
| `planspiel/rules.py` | service (all formulas) | transform | `simulate_outcomes.py` L175-497, `analyze_simulation_results.py` L60-63, `balance_analysis.py` L264-268 | move + dedupe |
| `planspiel/enumerate.py` | service | batch | `simulate_outcomes.py` L500-587 (`iter_selections`, `run_simulation`) | role-match |
| `planspiel/report.py` | service | batch/transform | `analyze_simulation_results.py` L43-176 | partial |
| `planspiel/legacy_output.py` | utility | file-I/O | `simulate_outcomes.py` L567-586 (results sort + JSON shape) | move (exact) |
| `planspiel/cli.py`, `planspiel/__init__.py` | CLI | request-response | `simulate_outcomes.py` L590-620 (argparse + `main`) | role-match |
| `simulate_outcomes.py` (wrapper) | CLI wrapper | request-response | itself (L590-620 pattern) | modify |
| `analyze_simulation_results.py` (wrapper) | CLI wrapper | request-response | itself (L179-197) | modify |
| `balance_analysis.py` (wrapper) | CLI wrapper | batch | itself (L28 `define_strategies`, L280 `run_analysis`) | modify |
| `simulation_config.json` | config | - | itself | modify (display strings only) |
| `pyproject.toml`, `.python-version`, `uv.lock` | config | - | none | no analog (RESEARCH pyproject block) |
| `.gitignore`, `.gitattributes` | config | - | existing files | modify |
| `README.md`, `CLAUDE.md`, `.claude/CLAUDE.md` | docs | - | existing command lines | modify |
| `tests/conftest.py` | test config | event-driven | none (RESEARCH `--update-golden` plumbing) | no analog |
| `tests/support/golden.py`, `digest.py`, `peak_memory.py` | test utility | transform | none (RESEARCH snippets) | no analog |
| `tests/support/legacy_harness.py` | test utility | transform | `simulate_outcomes.py` L531-565 (loop body) | source-of-logic |
| `tests/golden/*.json` | fixture | file-I/O | none (generated) | no analog |
| `tests/fixtures/mini_config.json`, `broken_*.json` | fixture | - | `simulation_config.json` (shrunk copy) | partial |
| `tests/test_characterization.py`, `test_digest.py`, `test_harness_vs_run_simulation.py` | test | batch | `balance_analysis.py` L28 (strategies) | partial |
| `tests/test_single_definition.py`, `test_thin_wrappers.py`, `test_encoding_lint.py` | test (AST) | transform | none | no analog |
| `tests/test_rounding.py`, `test_rules_exact.py`, `test_kernel_conformance.py` | test | transform | none | no analog |
| `tests/test_validate.py`, `test_config_text.py`, `test_enumeration.py`, `test_enumeration_perf.py`, `test_environment.py`, `test_legacy_generators_smoke.py` | test | mixed | none | no analog |

## Pattern Assignments

### `planspiel/config.py` (config, file-I/O + transform)

**Analog:** `simulate_outcomes.py` L10-172. Move the dataclasses and `load_config` verbatim, then change only: `read_text(encoding="utf-8")`, call `validate()` before building dataclasses, and (D-05 step 3) `parse_float=Fraction`.

**Encoding bug to fix** (L76-77):
```python
def load_config(path: Path):
    raw = json.loads(path.read_text())          # cp1252 on this machine -> "frÃ¼h"; must become encoding="utf-8"
```

**Hidden defaults to preserve (warn in validator, do not change behaviour)** (L85-87, L120):
```python
kz_start=info.get("kz_start", 60),
severity_multiplier=info.get("severity_multiplier", 1.0),
e_targets={int(k): v for k, v in info["e_targets"].items()},
...
e_threshold=wave.get("e_threshold", 18),
```

**Event params convention** (L150-157, repeated at L161-170; unify into one helper):
```python
Event(id=ev["id"], name=ev["name"], description=ev["description"], type=ev["type"],
      params={k: v for k, v in ev.items() if k not in ("id", "name", "description", "type")})
```

**Return shape** (L172): 8-tuple `default_budget_tier, budget_tiers, attacks, waves, measures, events, base_cia, final_events`. Existing callers (`balance_analysis.py` L282, `run_simulation` L518) unpack it; the `planspiel` version may return a `Config` object, but then all three callers change together.

Naming/style to keep (`.claude/CLAUDE.md` Conventions): `@dataclass`, PascalCase singular domain nouns, `= 0.0` or `field(default_factory=list)` defaults, snake_case, English identifiers.

---

### `planspiel/rules.py` (service, transform: every formula once)

**Analog / source:** `simulate_outcomes.py` L175-497. Move in the D-05 step-2 commit unchanged. Formula inventory to preserve:

**Dependencies** (L175-183):
```python
for measure_id, level in selection.items():
    measure = measures[measure_id]
    for dependency in measure.dependencies:
        if level >= dependency["level"]:
            for req in dependency["requires"]:
                if selection.get(req["measure"], 0) < req["min_level"]:
                    return False
```

**Costs / recovery / E-value / bonus** (L195-230): `compute_costs` returns `(init, opex_per_wave, init + opex*wave_count)`; `compute_recovery` is a `max` over levels; `compute_e_value = c*wc + i*wi + a*wa`; `compute_bonus_reduction` sums `bm.bonus` when `selection.get(bm.measure,0) >= bm.min_level`.

**Attack core, linear interpolation on purpose** (L253-283):
```python
gesamtreduktion = e_value + bonus_reduction
reduktion_ueber_schwelle = min(attack.mitigation_cap, max(0, gesamtreduktion - wave.e_threshold))
effective_base_severity = attack.base_severity * severity_multiplier
severity = max(0.0, effective_base_severity - reduktion_ueber_schwelle)
damage = severity * attack.s_unit
mitigation_fraction = reduktion_ueber_schwelle / attack.mitigation_cap if attack.mitigation_cap else 0.0
kz_delta = attack.kz_at_full_damage + mitigation_fraction * (attack.kz_at_full_mitigation - attack.kz_at_full_damage)
...
if attack.allow_recovery:
    recovery_factor = compute_recovery(selection, measures)
    damage = damage * (1 - recovery_factor)
```
Keep the German comment block at L267-271 (explains why the Fall-3 subformula is not used).

**Event dispatcher** (L317-376): `if event.type == ...` chain returning `(kz_delta, opex_delta, budget_delta, description)`; `_tier_lookup` (L305-314) is the `[min_inclusive, value]` ascending lookup; ends with `raise ValueError(f"Unknown event type: {event.type}")`. Effect-description strings with real umlauts and `€` live here (they flow into golden files).

**Wave loop and ORDER OF OPERATIONS (D-06/D-23 to verify)** (L446-463):
```python
e_reached = e_value >= e_target
kz += wave.kz_bonus if e_reached else wave.kz_malus
kz += attack_result["kz_delta"]
event_kz, event_budget, event_opex, event_results = apply_events(wave.wave_id, selection, events)
kz += event_kz
...
kz = max(0, min(100, kz))
```
Today: attack delta, E-target bonus and event KZ are summed onto running `kz`, then clamped once per wave. D-23 inserts `round_half_away(wave_total)` on the sum of the three deltas before adding to `kz` and before the clamp. The final Budget Review is applied after the waves (`run_simulation` L546-550) with its own clamp.

**Per-wave record** (L469-487): `e_value`, `gesamtreduktion`, `capped_reduction` use `round(x, 1)` for display only while the comparison at L448 uses the raw value (Pitfall 6). Python `round()` must not appear in `planspiel/rules.py`/`rounding.py` after step 3 (AST test); exact values render via `exact_to_json`.

**Final events + costs (must move into a shared `evaluate_plan`, per Q4/Pitfall 5)** (`run_simulation` L534-565):
```python
init, opex_per_wave, total_cost = compute_costs(selection, measures, len(waves))
outcome = simulate_selection(...)
total_cost += outcome["total_event_opex"]
adjusted_budget = tier_budget + outcome["total_event_budget"]
remaining_budget = adjusted_budget - total_cost
for event in final_events:
    ev_kz, _, _, description = evaluate_event(event, selection, remaining_budget=remaining_budget)
    outcome["kz_final"] = max(0, min(100, outcome["kz_final"] + ev_kz))
```
The over-budget predicate `total_cost > adjusted_budget` (L539) must become a single function `over_budget(...)` (D-11). Note L539-542 also carry the `min_cost` and utilization filters, which belong only to the legacy `--output` path (D-26), not the canonical evaluation.

**RoS and Final-Index (dedupe, D-24/D-27).** Sources to collapse into one `ros()` and one `final_index()`:
- `analyze_simulation_results.py` L12-23 (`base_losses = sum(base_severity * s_unit)` over waves, 620 today), L60-63:
```python
def compute_final_index(kz_final: int, ros: Optional[float], weight_kz: float, weight_ros: float) -> float:
    if ros is None:
        return kz_final
    return (weight_kz * kz_final) + (weight_ros * (ros * 100))
```
- RoS is written inline five times (L80-172), e.g. L143: `(base_losses - item["total_damage"]) / item["costs"]["total"] - 1`, which is algebraically `(base - damage - cost)/cost` and crashes at cost 0. New `ros()` returns `None` for cost 0.
- `balance_analysis.py` L264-277 `calculate_ros` (returns 0.0 at cost 0) and `calculate_combined_score` are to be deleted, not moved.

---

### `planspiel/enumerate.py` (service, batch)

**Analog:** `simulate_outcomes.py` L504-507, `run_simulation` L510-587.

**Enumeration order** (L504-507; the golden `code` string and digest depend on this order):
```python
def iter_selections(measure_ids, level_options):
    measure_list = list(measure_ids)
    for levels in itertools.product(level_options, repeat=len(measure_list)):
        yield {measure: level for measure, level in zip(measure_list, levels)}
```
`level_options = [0, 1, 2, 3]`, `measure_ids = list(measures.keys())` (config order). `selection_to_key` (L500-501) sorts ids lexicographically (`M1,M10,M2...`), so it differs from the 10-digit golden `code`.

**What differs from `run_simulation` (do not copy the filtering):** the new loop must keep over-budget plans and append compact per-combination records to a `ResultStore` (RESEARCH Q2: `array` SoA: `I` code, `B` kz, `H` own cost, `d`/exact ros, `I` damage, `B` over flag; own cost = init + opex x waves without event effects, D-25). The legacy loop holds full dict trees (about 6 KB each), which is the anti-pattern.

**Legacy sort to retain for `--output` (D-26)** (L567): `results.sort(key=lambda item: (-item["kz_final"], item["total_damage"]))` (stable over enumeration order). Budget-max quirk (L528-529, `max_cost` only feeds `utilization_threshold`) is preserved and pinned (Pitfall 4).

---

### `planspiel/legacy_output.py` (utility, file-I/O)

**Analog:** `simulate_outcomes.py` L569-586. Preserve the structure exactly:
```python
summary = {"total_outcomes": len(results), "budget_tier": budget_tier.name, "budget": tier_budget,
           "kz_start": kz_start,
           "budget_filter": {"min": min_cost, "max": max_cost, "utilization_min": utilization_threshold},
           "measures": measure_ids}
output = {"summary": summary, "results": results}
output_path.write_text(json.dumps(output, indent=2))   # add encoding="utf-8"; keep ensure_ascii default (True)
```
Each result carries `selection, kz_final, total_damage, total_event_opex, total_event_budget, cia_mali, waves, final_events, costs{init, opex_per_wave, total, event_opex, event_budget, budget_available}`; `analyze_simulation_results.py` reads `costs.total`, `total_damage`, `kz_final` from it.

---

### `planspiel/report.py` (service, batch/transform)

**Analog (partial):** `analyze_simulation_results.py` L43-52 (top/bottom sorting) and L55-57 (section printing). The new report differs: top-K three ways (KZ, RoS, Final-Index), percentiles, Pareto front, per-tier summary JSON (D-12...D-15). Copy the helper style:
```python
def summarize_top(results, key, top_n):
    return sorted(results, key=lambda item: get_value(item, key), reverse=True)[:top_n]

def print_section(title: str):
    print(f"\n{title}")
    print("-" * len(title))
```
German console output, English identifiers. German-locale number format helper at L26-31 (`format_currency`, `format_percent`) can be reused for console tables. Tie-break, nearest-rank percentiles and K=10 are per RESEARCH A3-A5.

---

### `planspiel/cli.py` and the three root wrappers (CLI, request-response)

**Analog:** `simulate_outcomes.py` L590-620:
```python
def parse_args():
    parser = argparse.ArgumentParser(description="Enumerate all deterministic outcomes for the planspiel.")
    parser.add_argument("--config", default="simulation_config.json", help="Path to simulation config JSON.")
    parser.add_argument("--budget-tier", default=None, help="Budget tier name (low|medium|high).")
    parser.add_argument("--output", default="simulation_results.json", help="Output JSON file path.")
    parser.add_argument("--budget-min", type=int, default=None, ...)
    parser.add_argument("--budget-max", type=int, default=None, ...)
    parser.add_argument("--budget-utilization", type=float, default=0.0, ...)
    return parser.parse_args()

def main():
    args = parse_args()
    summary = run_simulation(Path(args.config), ...)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
```
Change for D-16: `--output` default becomes `None` (no `--output` means new summary; `--output` means legacy full JSON); new explicit flag for the JSONL dump (D-26). Keep `--config`, `--budget-tier`, `--budget-min/max`, `--budget-utilization` spellings. `analyze_simulation_results.py` args (L179-186) keep `--input`, `--config`, `--top`, `--weight-kz`, `--weight-ros`, with German help strings. Wrapper shape: shebang, `from planspiel.<x> import main`, `if __name__ == "__main__": main()`; no logic (AST test `test_thin_wrappers.py`). `cli.py` calls `sys.stdout.reconfigure(encoding="utf-8")` once (Pitfall 1).

**`balance_analysis.py` specifics:**
- Import at L14-18 (`sys.path.insert` + `from simulate_outcomes import ...`) goes away; imports come from `planspiel`.
- `Strategy` dataclass (L21-25) and `define_strategies()` (L28+, 27 unique named strategies with inline cost comments such as `# 26+36+34+46+16+32=190`) stay in the wrapper or move to `tests/support` for the golden set. The comment costs are load-bearing; stale "Budget: 300k" comments (tiers are 350/400/450) are Open Question territory.
- Delete `calculate_ros`, `calculate_combined_score` (L264-277) and the local budget check (D-24); keep the `====` banner printing style (L285-286, L302-304, L313-316), all German.
- L281 reads config with the script-relative path: `Path(__file__).parent / "simulation_config.json"`.

---

### `tests/support/legacy_harness.py` (test utility, transform)

**Source of logic:** `simulate_outcomes.py` L531-565 (see rules.py "Final events + costs" excerpt above). Per RESEARCH Q4 it composes `dependencies_satisfied` -> `compute_costs` -> `simulate_selection` -> event OPEX/budget -> `over_budget` -> `remaining` -> final events -> costs dict, and computes RoS as `(base_losses - total_damage - total_cost) / total_cost`, `None` at cost 0. It must import the legacy functions from `simulate_outcomes` at step 1 and be swapped to `planspiel.rules` at step 2. Do not call `simulate_selection` alone (it skips final events, Pitfall 5).

---

### `tests/*` and `pyproject.toml` (no analog)

There is no test infrastructure and no package metadata in the repo. Use the verified RESEARCH snippets:
- `pyproject.toml`, `.python-version` (`3.12`): RESEARCH § "pyproject.toml (verified layout)".
- `tests/conftest.py` (`--update-golden`, `pytest_terminal_summary`): RESEARCH § "`--update-golden` plumbing (D-10)".
- `planspiel/rounding.py` (`round_half_away`, `started_steps`, `exact_to_json`): RESEARCH § "Rounding and step helpers" and "Exact values in JSON".
- `tests/support/peak_memory.py`: RESEARCH § "Peak-memory helper".
- `tests/test_encoding_lint.py`: RESEARCH § "Encoding lint" (AST walk).
- Golden format, selection list, digest canonicalization: RESEARCH Q4. Named strategies come from `balance_analysis.py` `define_strategies` (27 of them).
- `tests/fixtures/mini_config.json`: shrink `simulation_config.json` to 2-3 measures and 1-2 waves; `broken_*.json`: one copy per validator rule (Q8).
- Generator smoke test: `generate_attack_calculator.py` reads the config at import time relative to cwd and `main()` overwrites the tracked xlsx. `monkeypatch.chdir(repo_root)`, import only, never call `main()` (RESEARCH Q7).

---

### `simulation_config.json` (config, display-string edit only)

Change only the strings listed in RESEARCH Q7 (`waves[1].name` "OT-Stoerung" -> "OT-Störung", event names/descriptions, `final_events[0].description`, `_comment_events`). Ids/keys stay ASCII. Attack descriptions and bonus descriptions already have real umlauts. Write the file as UTF-8 without BOM, LF endings, preserving the current indentation and key order.

## Shared Patterns

### UTF-8 everywhere
**Source problem:** `simulate_outcomes.py` L77 and L586, `analyze_simulation_results.py` L9 and L15 use `read_text()`/`write_text()` without an encoding. The generators already read UTF-8 (`generate_pptx_cards.py` `load_config` L203, `generate_from_template.py` L197).
**Apply to:** every text I/O in `planspiel/`, wrappers and tests (AST-enforced); stdout reconfigured in CLI entry points.

### Config-driven, no hard-coded numbers
**Source:** `.claude/CLAUDE.md` "Config-Driven Design Pattern". All numeric operands come from `simulation_config.json`. Hidden defaults in `load_config` (L85-87, L120) are kept behaviour-preserving and flagged by the validator as `schema.default_used`. The base-loss constant 620 is computed (`analyze_simulation_results.py` L18-22), never hard-coded.

### Single definition of derived quantities
**Apply to:** `rules.py` only. Today RoS exists 5x in `analyze_simulation_results.py` plus 1x in `balance_analysis.py`; Final-Index exists in `analyze_simulation_results.py` L60 and (as `combined_score`) in `balance_analysis.py` L271. Collapse to one `ros()`, one `final_index()`, one `over_budget()`, one `evaluate_plan()`; enforce with `tests/test_single_definition.py`.

### Naming, typing, comments
**Source:** `.claude/CLAUDE.md` Conventions and `simulate_outcomes.py`. snake_case verbs (`compute_*`, `apply_*`, `check_*`, `load_*`, `run_*`); domain abbreviations `kz`, `cia` (`c/i/a` dict), `e_value`, `e_threshold`, `opex`, `init`, `ros` are used unchanged; `typing` hints (`Dict`, `List`, `Tuple`, `Optional`) on simulation code; SCREAMING_SNAKE constants at module level; English code identifiers, German user-facing output; do not add docstrings or comments to moved code you do not change.

### Error handling
**Source:** `simulate_outcomes.py` L376 (`raise ValueError(f"Unknown event type: ...")`) and L175-183/L539 (invalid combos are skipped by returning False/`continue`, not raised). New code: `ConfigError` (all errors listed) for broken references at every load; invalid selections in the golden file stored as `{"valid": false}`; unknown event type stays a `ValueError`/validator error.

## No Analog Found

| File | Role | Data Flow | Reason / fallback |
|---|---|---|---|
| `pyproject.toml`, `.python-version`, `uv.lock` | config | - | No packaging exists (only `requirements` in prose). Use RESEARCH pyproject block |
| `planspiel/validate.py` | validator | transform | No validation today (`load_config` assumes well-formed JSON). Use RESEARCH Q8 check list and `Issue(level, code, path, message)` |
| `planspiel/rounding.py` | utility | transform | Only float math and Python `round()` exist. Use RESEARCH code |
| `tests/**` | test | - | No tests exist. Use RESEARCH Q4/Validation Architecture and code snippets |
| kernel (integer-scaled fast path, in `planspiel/enumerate.py`) | service | batch | Nothing comparable; Pattern 1 and 2 in RESEARCH; must call the same `rules` primitives |

## Metadata

**Analog search scope:** repo root `*.py`, `simulation_config.json`; `.planning/codebase` conventions via `.claude/CLAUDE.md`. `sim_*.json` never read.
**Files read:** `simulate_outcomes.py` (lines 76-620), `analyze_simulation_results.py` (8-68, 178-197), `balance_analysis.py` (14-53, 262-332), CONTEXT.md, RESEARCH.md.
**Pattern extraction date:** 2026-09-30
