<!-- refreshed: 2026-06-23 -->
# Architecture

**Analysis Date:** 2026-06-23

## System Overview

This repository has **no runtime application architecture**. There is no server, no frontend, no API, no database, and no deployed software product. The "system" being modeled is a **live tabletop game** played by humans with paper and a whiteboard. The repository's code exists solely as **offline content-tooling**: it lets the game designer enumerate, balance-check, and pretty-print the deterministic rules before the game is printed and played.

Two things are layered on top of each other and should not be confused:

1. **The game's own logic** — a deterministic state machine and a set of fixed formulas, defined in prose in `README.md` and parametrized in `simulation_config.json`. This is "the architecture" in the sense that matters for this project: a rules engine that exists conceptually and on paper, executed by a human facilitator during play.
2. **The Python tooling** — standalone scripts that mirror the same formulas in code, purely to (a) enumerate all possible outcomes ahead of time and (b) generate print materials. None of these scripts run during actual gameplay.

```text
┌─────────────────────────────────────────────────────────────┐
│              GAME RULES (played live, on paper)              │
│   State machine + formulas, documented in `README.md`       │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ parametrized by
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 `simulation_config.json`                     │
│   Single source of truth for ALL numeric values:             │
│   budget_tiers, waves (wC/wI/wA, E-thresholds), attacks,      │
│   measures (L1/L2/L3), events, base_cia                      │
└───────┬───────────────────────────┬──────────────────────────┘
        │                           │
        ▼                           ▼
┌──────────────────────┐   ┌──────────────────────────────────┐
│ `simulate_outcomes.py`│   │ generator scripts:                │
│ enumerates ALL valid │   │  `generate_attack_calculator.py`  │
│ measure combinations │   │  `generate_from_template.py`      │
│ deterministically    │   │  `generate_pptx_cards.py`         │
└──────────┬────────────┘   └────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐   ┌──────────────────────────────────┐
│ `sim_low.json`        │   │  `pptx_output/` (generated decks) │
│ `sim_med.json`        │   │  `final_documents/` (print-ready  │
│ (large pre-computed   │   │   docx/pptx/pdf/xlsx)             │
│  result sets)         │   │                                    │
└──────────┬────────────┘   └────────────────────────────────────┘
           │
           ▼
┌──────────────────────┐   ┌──────────────────────────────────┐
│`analyze_simulation_   │   │ `balance_analysis.py`             │
│ results.py`            │   │ checks for dominant strategies    │
│ ranks outcomes by      │   │ (imports core functions directly  │
│ Final-Index (KZ/RoS)   │   │ from `simulate_outcomes.py`)      │
└────────────────────────┘   └────────────────────────────────────┘
```

There is no inverse data flow: nothing the scripts produce is read back into the game at play-time. The facilitator computes outcomes live, by hand, using the formulas and the printed `BERECHNUNGSBOGEN_WELLE{1,2,3}_*.md` worksheets — the Python scripts exist only to validate, in advance, that the configured rules behave sensibly.

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

**Overall:** Config-driven offline batch tooling. Not a software architecture in the traditional sense — closer to a set of independent CLI scripts that share one JSON config file as their only common interface.

**Key Characteristics:**
- No persistence layer beyond flat JSON files (`simulation_config.json` as input, `sim_low.json`/`sim_med.json` as cached output)
- No concurrency, no networking, no users/sessions — every script is a single-process batch job invoked via `argparse` from the command line
- Determinism is the central design constraint: the same config + same measure selection must always produce the same numbers, both in the live game (by hand) and in the simulation scripts (in code). There is deliberate duplication of formula logic between `README.md` (human-readable spec) and `simulate_outcomes.py` (executable spec) — keeping these two in sync is a documented project convention (see `CLAUDE.md`)
- The Python scripts are siblings, not a layered application: `balance_analysis.py` is the only script with an internal code dependency, importing functions directly from `simulate_outcomes.py` (see `balance_analysis.py:15`)

## Layers

There is no layered application architecture (no UI/business-logic/data-access split). The closest analogue is a **pipeline of independent stages**, each one a standalone script invoked manually in sequence:

**Stage 1 — Config:**
- Purpose: Define all tunable numbers for the game
- Location: `simulation_config.json`
- Contains: `default_budget_tier`, `base_cia`, `budget_tiers`, `waves`, `attacks`, `measures`, `events`
- Used by: every Python script below

**Stage 2 — Enumeration:**
- Purpose: Compute every legal outcome deterministically
- Location: `simulate_outcomes.py`
- Depends on: `simulation_config.json` (loaded via `load_config()`, `simulate_outcomes.py:77`)
- Used by: `balance_analysis.py` (direct import), manually piped into `analyze_simulation_results.py` via JSON file

**Stage 3 — Analysis / QA:**
- Purpose: Rank outcomes, detect dominant strategies, sanity-check balance
- Location: `analyze_simulation_results.py`, `balance_analysis.py`
- Depends on: simulation result JSON (either freshly generated or `sim_low.json`/`sim_med.json`)
- Used by: human game designer, before content/print finalization

**Stage 4 — Generation:**
- Purpose: Turn config/content into printable or presentable artifacts
- Location: `generate_attack_calculator.py`, `generate_from_template.py`, `generate_pptx_cards.py`
- Depends on: `simulation_config.json` plus existing `.pptx` templates (for `generate_from_template.py`)
- Produces: files in `pptx_output/`, source material for `final_documents/`

**Stage 5 — Live play (no code):**
- Purpose: Actual game execution
- Location: Printed Markdown forms (`FORMULARE.md`, `BERECHNUNGSBOGEN_WELLE*.md`, `TEAM_TRACKING_BOGEN.md`) and `final_documents/`
- Depends on: nothing computational at runtime — facilitator applies the formulas from `README.md` by hand

## Data Flow

### Primary Content-Validation Path

1. Game designer edits numeric parameters in `simulation_config.json`
2. Designer runs `simulate_outcomes.py --config simulation_config.json --budget-tier <low|medium|high>` (see `README.md:213`), which loads config (`simulate_outcomes.py:77`), iterates all measure-level combinations (`iter_selections`, `simulate_outcomes.py:442`), checks dependencies (`dependencies_satisfied`, `simulate_outcomes.py:166`), applies events (`apply_events`, `simulate_outcomes.py:313`) and attacks (`apply_attack`, `simulate_outcomes.py:237`), and computes the E-value (`compute_e_value`, `simulate_outcomes.py:204`) per wave via `simulate_selection` (`simulate_outcomes.py:355`)
3. Output written to a results JSON (e.g. `simulation_results.json`, or pre-baked as `sim_low.json` / `sim_med.json`)
4. Designer runs `analyze_simulation_results.py --input <results.json> --config simulation_config.json --top N` to rank outcomes by a weighted Final-Index of KZ and RoS (`compute_final_index`, `analyze_simulation_results.py:60`)
5. Designer runs `balance_analysis.py`, which defines hand-picked named strategies (`define_strategies`, `balance_analysis.py:28`), re-derives their CIA/cost/RoS using functions imported from `simulate_outcomes.py`, and flags whether any strategy dominates
6. If imbalance is found, designer edits `simulation_config.json` again and the cycle repeats — this loop is documented as a required step in `CLAUDE.md` ("Nach inhaltlichen Änderungen ... simulate_outcomes.py + balance_analysis.py laufen lassen")

### Print Material Generation Path

1. Designer finalizes measure/attack/event content in `simulation_config.json` and the prose Markdown documents (`MASSNAHMENKARTEN.md`, `ANGRIFFSKARTEN.md`)
2. `generate_pptx_cards.py` builds slide decks programmatically from config (`generate_massnahmen_pptx`, `generate_events_pptx`, lines 620/648) → written to `pptx_output/Massnahmenkarten_Generated.pptx`, `pptx_output/Events_Generated.pptx`
3. `generate_from_template.py` instead loads an existing template `.pptx` and replaces placeholder text per shape (`update_massnahmen_template`, `generate_from_template.py:335`; `update_events_template`, `generate_from_template.py:486`) → written to `pptx_output/Massnahmenkarten_Security-Game.pptx`, `pptx_output/Events_Security-Game.pptx`
4. `generate_attack_calculator.py` builds an Excel workbook (`create_attack_worksheet`, line 42; `create_overview_sheet`, line 420) → `angriff_berechnung.xlsx`
5. Finalized, print-ready versions of these and other documents (briefing letters, audit emails, newspaper article props) are hand-curated into `final_documents/` as docx/pptx/pdf — these are **not** regenerated automatically from the generator scripts; the scripts produce drafts that are manually polished into the final set

**State Management:**
There is no persistent application state. "State" only exists (a) transiently within a single script invocation (in-memory dicts/dataclasses in `simulate_outcomes.py`, e.g. the `Measure` dataclass), and (b) as paper/whiteboard state during actual play, tracked by humans using `TEAM_TRACKING_BOGEN.md` and `BERECHNUNGSBOGEN_WELLE*.md`.

## Key Abstractions

**Measure (Maßnahme):**
- Purpose: Represents a security control selectable at level 0-3 (L1/L2/L3), with `costInit`, `costOpex`, `cia={c,i,a}`, `mitigations`, `eventEffects`, `dependencies`
- Examples: `simulate_outcomes.py` `Measure` dataclass; content described in `MASSNAHMENKARTEN.md`; raw data in `simulation_config.json` under `measures`
- Pattern: Plain dataclass loaded straight from JSON, no inheritance/polymorphism

**Wave (Welle):**
- Purpose: One round of play with CIA weights (`wC`, `wI`, `wA`), an E-target threshold, and a set of attacks
- Examples: `simulation_config.json` under `waves`; described conceptually in `README.md` ("Wellen‑Ziel (E‑Wert) & Scoring")

**Attack (Angriff):**
- Purpose: A deterministic threat event with `baseSeverity`, `sUnit`, `kzUnit`, `ciaImpactPerStep`, and references to measures that mitigate it
- Examples: `simulation_config.json` under `attacks`; applied via `apply_attack` (`simulate_outcomes.py:237`); described in `ANGRIFFSKARTEN.md`

**Event:**
- Purpose: Rule-based trigger (time/discovery-signal/measure-presence condition) with deterministic effects (`budgetDelta`, `kzDelta`, `severityMod`, `kzFactor`, `damageFactor`, `opexPenalty`)
- Examples: `simulation_config.json` under `events`; checked via `check_event_condition` (`simulate_outcomes.py:288`) and applied via `apply_events` (`simulate_outcomes.py:313`)

**Strategy (balance-testing only):**
- Purpose: A hand-authored, named measure-selection used solely to probe for dominance/imbalance — not a concept that exists in the game itself
- Examples: `define_strategies` (`balance_analysis.py:28`)

## Entry Points

**`simulate_outcomes.py` (CLI):**
- Location: `simulate_outcomes.py`
- Triggers: Manual invocation by game designer, e.g. `python3 simulate_outcomes.py --config simulation_config.json --budget-tier medium --output simulation_results.json`
- Responsibilities: Full deterministic enumeration of outcomes; argument parsing in `parse_args()` (line 515), orchestration in `main()` (line 531)

**`analyze_simulation_results.py` (CLI):**
- Location: `analyze_simulation_results.py`
- Triggers: Manual invocation after `simulate_outcomes.py` has produced a results file
- Responsibilities: Ranking/summarizing outcomes by weighted Final-Index

**`balance_analysis.py` (CLI):**
- Location: `balance_analysis.py`
- Triggers: Manual invocation, no arguments required (`run_analysis()`, line 280)
- Responsibilities: Strategy-vs-strategy comparison, dominance detection

**`generate_attack_calculator.py`, `generate_from_template.py`, `generate_pptx_cards.py` (CLIs):**
- Location: project root
- Triggers: Manual invocation when print material needs regenerating after content changes
- Responsibilities: Produce `.xlsx`/`.pptx` artifacts into `pptx_output/`

There is no application "main" beyond these independent script entry points — there is no orchestrating top-level script that chains them together.

## Architectural Constraints

- **Threading:** None. Every script is single-threaded, synchronous, batch-style.
- **Global state:** None beyond normal Python module-level constants (e.g. `MIT_CAP` style caps loaded from config at call time). No singletons, no shared mutable state across script invocations — each run reads `simulation_config.json` fresh.
- **Circular imports:** None observed. `balance_analysis.py` imports from `simulate_outcomes.py` (one-directional); no other script imports another.
- **Combinatorial explosion:** `simulate_outcomes.py` enumerates the full cross-product of measure-level selections, which is why `sim_low.json` is ~14 MB and `sim_med.json` is ~52 MB. Both files are explicitly flagged in `CLAUDE.md` as too large to read in full — must be parsed with `jq`/targeted Python rather than loaded wholesale.
- **No runtime/production environment:** There is no deployment target, no server process, no persistent service. "Production" for this project means the printed contents of `final_documents/` used at the live game session.

## Anti-Patterns

### Treating this as a software application

**What happens:** Approaching the repo expecting MVC layers, REST endpoints, or a request/response cycle.
**Why it's wrong:** There is no application runtime to model this way; doing so invents structure that does not exist and will mislead any future planning.
**Do this instead:** Treat `README.md` + `simulation_config.json` as the actual "application" (the rules engine), and the Python scripts as one-off QA/build tooling around it, analogous to a static site generator's build scripts.

### Editing generated/binary output directly

**What happens:** Hand-editing files in `pptx_output/` or `final_documents/` (docx/pptx/pdf/xlsx).
**Why it's wrong:** These are generated or finalized binary artifacts; manual edits get silently lost the next time a generator script runs, and there's no diffing/reviewing such edits in git history.
**Do this instead:** Edit the source content (`simulation_config.json`, the relevant `.md` content file, or the `.pptx` template consumed by `generate_from_template.py`) and re-run the appropriate generator script (see `CLAUDE.md`).

### Letting prose documentation and config drift apart

**What happens:** Introducing a new fixed number (e.g. a budget figure or severity value) directly into a Markdown document without also updating `simulation_config.json`.
**Why it's wrong:** `simulation_config.json` is the single source of truth for all numeric values (per `CLAUDE.md` and `README.md`'s "Parametrisierung" section); a number that exists only in prose cannot be validated by `simulate_outcomes.py`/`balance_analysis.py` and will silently diverge from what the simulation actually computes.
**Do this instead:** Add/change the number in `simulation_config.json` first, then update `README.md` and any affected card/form documents to match.

## Error Handling

**Strategy:** Standard Python script-level error handling — `argparse` validates CLI inputs; malformed/missing config or selection data fails with Python exceptions/tracebacks. No custom error hierarchy, no retries, no logging framework.

**Patterns:**
- Config loading functions (`load_config` in `simulate_outcomes.py:77`, `load_config` in `generate_from_template.py:197`, `load_config` in `generate_pptx_cards.py:203`) assume well-formed JSON and will raise on malformed input rather than validating gracefully
- Dependency/condition checks (`dependencies_satisfied`, `check_event_condition`) return booleans used to skip invalid combinations rather than raising — invalid measure combinations are filtered out of the enumeration, not flagged as errors

## Cross-Cutting Concerns

**Logging:** None — scripts use `print()` for human-readable progress/summary output (e.g. `print_section` in `analyze_simulation_results.py:55`), not a logging framework.
**Validation:** Implicit, via the dependency/condition-check functions described above; no schema validation library is used on `simulation_config.json`.
**Authentication:** Not applicable — no users, no network surface.

---

*Architecture analysis: 2026-06-23*
