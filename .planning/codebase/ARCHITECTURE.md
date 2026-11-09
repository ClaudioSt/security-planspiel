<!-- refreshed: 2026-11-09 -->
# Architecture

**Analysis Date:** 2026-11-09

## System Overview

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                 Inputs (committed, hand-edited)                             │
│  `simulation_config.json`   `content/texte.toml` + clues / allowlist /      │
│                             giveaway terms   `content/mhp_baseline.json`    │
│                             `final_documents/*.pptx|jpg` (kept manual)      │
└───────────┬────────────────────────┬──────────────────────────┬────────────┘
            │                        │                          │
            ▼                        ▼                          ▼ (only was_neu.py)
┌──────────────────────┐  ┌──────────────────────┐   ┌──────────────────────┐
│ Config layer         │  │ Content layer        │   │ Baseline loader      │
│ `planspiel/config.py`│  │ `planspiel/texts.py` │   │ `planspiel/was_neu.py`│
│ `planspiel/validate.py`│ │ `planspiel/veil.py`  │   └──────────┬───────────┘
└──────────┬───────────┘  │ `planspiel/audience.py`│             │
           │              └──────────┬───────────┘             │
           ▼                         │                         │
┌────────────────────────────────────────────────────────────────────────────┐
│ Rules layer  `planspiel/rules.py` (single definition of every formula)     │
│ + `rounding.py`, `review_text.py`, `fmt.py`, `eventtext.py`                  │
└───────┬───────────────────────────────────────────────┬────────────────────┘
        │                                               │
        ▼                                               ▼
┌──────────────────────────────────────┐   ┌──────────────────────────────────┐
│ Analysis layer                        │   │ Print models (strings only)      │
│ `enumerate.py`, `simulate.py`,        │   │ `printmodel.py`, `booklet.py`,   │
│ `parallel.py`, `refpaths.py`,         │   │ `cards.py`, `wave_page.py`,      │
│ `choices.py`, `gate.py`, `balance.py` │   │ `story.py`, `practice.py`,       │
│ `strategies.py`, `rewarding.py`,      │   │ `master.py`, `schedule.py`,      │
│ `spread.py`, `index_weights.py`,      │   │ `debrief.py`, `probelauf.py`,    │
│ `report.py`, `analyze.py`             │   │ `was_neu.py`                     │
└──────────────┬───────────────────────┘   └────────────────┬─────────────────┘
               │                                            │
               ▼                                            ▼
┌──────────────────────────────────┐   ┌──────────────────────────────────────┐
│ Console output, JSON summaries,  │   │ Print pipeline                        │
│ balance report (German, stdout)  │   │ `render.py` (Jinja2, registry) ->     │
└──────────────────────────────────┘   │ `veil.py` scan -> `texbuild.py`       │
                                       │ (LuaLaTeX) -> `stamp.py` + manifest   │
                                       └────────────────┬──────────────────────┘
                                                        ▼
                                       ┌──────────────────────────────────────┐
                                       │ `final_documents/generated/`          │
                                       │ 15 PDFs + `manifest.json` (committed) │
                                       └──────────────────────────────────────┘
```

Entry points for all of the above: the `planspiel` console script (`planspiel/cli.py`) and the root wrapper scripts (`simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`).

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Config loader | Reads `simulation_config.json` into typed read-only dataclasses (`Config`, `Wave`, `Attack`, `Measure`, `BudgetTier`, `Event`, `Practice`, `SessionSchedule`, `FinalIndexWeights`) | `planspiel/config.py` |
| Config validator | Structure, hand-calculability, schedule and prose-in-config checks; a hard error on failure | `planspiel/validate.py` |
| Rules kernel | The one definition of every game formula (E-Wert, Gesamtreduktion, severity, damage, KZ delta, RoS, budget review, swap credit, final index, worksheet constants, path trace) | `planspiel/rules.py` |
| Rounding | Half-away-from-zero rounding on integers and `Fraction`; `round()` is forbidden in rules | `planspiel/rounding.py` |
| German formatting | Decimal comma, thousands dot, true minus; refuses inexact values | `planspiel/fmt.py`, `planspiel/review_text.py` |
| Event wording | Effect lines generated from event params, verified against `rules.evaluate_event` | `planspiel/eventtext.py` |
| Text source | Loads `content/texte.toml`, checks coverage against config, digit lint, story lint, clue matrix | `planspiel/texts.py` |
| Veil and audience | Classifies every job by prefix; scans pre-wave pages for giveaways | `planspiel/audience.py`, `planspiel/veil.py` |
| Enumeration | All dependency-valid measure selections, swap layer, game paths, result store as typed arrays | `planspiel/enumerate.py`, `planspiel/choices.py` |
| Simulation driver | Per-tier run, JSON summary and optional JSONL dump | `planspiel/simulate.py`, `planspiel/report.py` |
| Parallelism | Process pool across budget tiers (`--jobs`) | `planspiel/parallel.py` |
| Reference paths | Proposes candidate game paths for the answer keys | `planspiel/refpaths.py` |
| Overspend gate | Proves overspending never pays off; calibrates `overspend_penalty.kz_per_step` | `planspiel/gate.py` |
| Balance checks | Consolidated balance report with verdicts; Final-Index weight, decisions, strategies, reward, spread | `planspiel/balance.py`, `planspiel/index_weights.py`, `planspiel/choices.py`, `planspiel/strategies.py`, `planspiel/rewarding.py`, `planspiel/spread.py` |
| Practice view | Throw-away `Config` with only the practice wave (Welle 0) | `planspiel/practice.py` |
| Attack worksheets | Exact values plus German display strings per wave | `planspiel/printmodel.py` |
| Cards | Measure and event card decks (pre-wave, no weights or bonus links) | `planspiel/cards.py` |
| Team booklet | Facilitator-ordered calculation pages, budget ledger, RoS, final index | `planspiel/booklet.py` |
| Wave explainer | One-page "So funktioniert eine Welle" (symbols only) | `planspiel/wave_page.py` |
| Story documents | Steckbrief, newspaper article, two mails | `planspiel/story.py` |
| Master sheet | Facilitator overview: parameters, checks, event schedule, answer keys, clue matrix, debrief | `planspiel/master.py` |
| Schedule | Block durations and minutes from `session_schedule`; no clock times | `planspiel/schedule.py` |
| Debrief | Four facilitator debrief stages with fixed questions | `planspiel/debrief.py` |
| Dry-run protocol | One-page observer sheet for the full-session dry run | `planspiel/probelauf.py` |
| "Was ist neu" sheet | Old MHP baseline vs. new values (only module reading the baseline) | `planspiel/was_neu.py` |
| Render | Strict Jinja2 environment (`tex_escape` as `finalize`), document registry, `render_all` | `planspiel/render.py` |
| LaTeX driver | Non-interactive LuaLaTeX runs with timeouts and aux-stable pass loop | `planspiel/texbuild.py` |
| Stamp | "Stand <date> · <hash>" and `manifest.json`, "+lokal" for dirty builds | `planspiel/stamp.py` |
| CLI | argparse subcommands `validate`, `tausch`, `referenzpfade`, `gate`, `texts`, `clues`, `print` | `planspiel/cli.py` |

## Pattern Overview

**Overall:** Config-driven batch tooling with a single rules kernel. There is no server, no database, no persistence and no state between runs. Inputs are committed files; outputs are console reports, JSON summaries and committed PDFs.

**Key Characteristics:**
- **Determinism:** no randomness anywhere. The same config and the same decisions give the same numbers, in code and by hand on the worksheets.
- **Single definition of the rules:** `planspiel/rules.py` is the only place formulas are written. Enumeration, balance checks, print models and root wrappers call it. `tests/test_single_definition.py` guards this.
- **Single source of numbers and prose:** numbers only in `simulation_config.json`, prose only in `content/texte.toml`. Print models format numbers in code; templates never format.
- **Exact arithmetic:** `fractions.Fraction` or integer scaling for E-Wert, Gesamtreduktion, reduction over threshold and severity. Only the KZ change per wave is rounded (once, half away from zero), then KZ is clamped to 0-100.
- **Layered package, downward imports:** config, content and rules sit at the bottom; analysis and print models sit above rules; the print pipeline and entry points sit on top.
- **Audience classification by filename prefix:** `spieler-`, `uebung-`, `angriff-`, `spielleitung-` (see `planspiel/audience.py`). An unclassified job is a build error.

## Layers

**Config layer:**
- Purpose: load and validate the one source of numbers.
- Location: `simulation_config.json` (data), `planspiel/config.py`, `planspiel/validate.py`.
- Contains: frozen dataclasses (`@dataclass`, treated read-only after loading), structural and hand-calculability checks, schedule checks.
- Depends on: standard library only (`config.py`); `validate.py` imports `rules.kz_slope`.
- Used by: every other layer.

**Content layer:**
- Purpose: all German prose and the veil rules.
- Location: `content/texte.toml`, `content/clues.toml`, `content/digit_allowlist.toml`, `content/giveaway_terms.toml`, `planspiel/texts.py`, `planspiel/veil.py`, `planspiel/audience.py`.
- Contains: coverage check of texts against the config IDs, digit lint (no digits in prose unless allowlisted), story lint, giveaway scan, clue matrix.
- Depends on: `config`, `rules` (for derived mechanics), `review_text`, `validate.Issue`.
- Used by: print models and CLI (`texts`, `clues`).

**Rules layer:**
- Purpose: the game formulas, fixed and linear (hand-calculable), with operands from config.
- Location: `planspiel/rules.py` (about 1300 lines, 48 functions), `planspiel/rounding.py`, `planspiel/review_text.py`, `planspiel/fmt.py`, `planspiel/eventtext.py`.
- Contains: `evaluate_path`, `path_trace`, `evaluate_event`, `budget_review_delta`, `budget_ledger`, `security_spend`, `swap_credit`, `worksheet_constants`, `final_index`, `ros_two_decimals`, `card_facts`, `level_requirements`, `recovery_table`.
- Depends on: `config` and `rounding` only.
- Used by: enumeration, gate, balance, print models.

**Analysis layer:**
- Purpose: enumerate every legal plan and judge the balance.
- Location: `planspiel/enumerate.py` (static enumeration into compact arrays), `planspiel/choices.py`, `planspiel/simulate.py`, `planspiel/report.py`, `planspiel/parallel.py`, `planspiel/refpaths.py`, `planspiel/gate.py`, `planspiel/balance.py`, `planspiel/strategies.py`, `planspiel/rewarding.py`, `planspiel/spread.py`, `planspiel/index_weights.py`, `planspiel/analyze.py`.
- Contains: the result store (`array`-based), summaries per tier, the swap layer (`rules.swap_credit`, change-window moves), the overspend gate (`gate.gate_tier`, `--paths`), the consolidated report (`balance.build_balance_report`).
- Depends on: `rules`, `config`, `report`.
- Used by: CLI (`tausch`, `referenzpfade`, `gate`), root wrappers, `balance_analysis.py`, tests with `-m slow` and `-m balance`.

**Print models layer:**
- Purpose: turn rules results and texts into finished German strings per document. Templates only loop and place these strings.
- Location: `planspiel/printmodel.py` (attack worksheets), `planspiel/cards.py`, `planspiel/booklet.py`, `planspiel/wave_page.py`, `planspiel/story.py`, `planspiel/practice.py`, `planspiel/master.py`, `planspiel/schedule.py`, `planspiel/debrief.py`, `planspiel/probelauf.py`, `planspiel/was_neu.py`.
- Contains: one builder per document family; `PreAttackView` (pre-wave text view), `RevealView` and `FacilitatorView` (revealed text view, facilitator-only).
- Depends on: `rules`, `texts`, `fmt`, `review_text`, `eventtext`, `schedule` (for booklet and probelauf), `practice` (for master).
- Used by: `render.py` through `DOCUMENT_BUILDERS` and `render_all`.

**Print pipeline layer:**
- Purpose: render, scan, typeset, stamp.
- Location: `planspiel/render.py`, `planspiel/veil.py`, `planspiel/texbuild.py`, `planspiel/stamp.py`, `print/templates/*.tex.j2`, `print/planspiel.sty`, `print/miktex-packages.txt`.
- Contains: Jinja2 environment (`StrictUndefined`-style strictness, `tex_escape` finalize hook), job-name check, per-audience veil scan, LuaLaTeX subprocess driver, stamp and manifest, freshness comparison for `print --check`.
- Depends on: `jinja2`, `git` (stamp reads commit date and dirty state), MiKTeX (LuaLaTeX, `kpsewhich`).
- Used by: `planspiel print` and `planspiel print --check`.

**Entry-point layer:**
- Purpose: command-line surface.
- Location: `planspiel/cli.py`, `planspiel/__main__.py` (`python -m planspiel`), root `simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py` (thin wrappers that call `planspiel.simulate.main` and related functions).
- Depends on: everything above, lazily imported inside each subcommand.

## Data Flow

### Primary Request Path: print build

1. `planspiel print` loads `simulation_config.json` through `config.load_config` (`planspiel/cli.py`).
2. `texts.load_content` reads `content/texte.toml` and related files; `texts.check_texts` and `texts.check_clues` run before rendering.
3. `render.render_all` (`planspiel/render.py`) calls each builder in `DOCUMENT_BUILDERS` (attack worksheets, measure and event cards, team booklet, wave page, story documents, practice document, master sheet, probelauf sheet) plus `was_neu.was_neu_sheet`, which receives the baseline.
4. Each builder uses `rules` for every number, `texts` for every word, and returns `{job_name: tex_source}`. `render.register` checks the job name (`texbuild.check_job_name`) and classifies it (`audience.audience_of`).
5. `veil.py` scans each rendered source by audience profile (pre-wave, practice, revealed, facilitator). A giveaway aborts the build.
6. `texbuild.py` runs LuaLaTeX per job with a timeout and the MiKTeX installer disabled.
7. `stamp.py` hashes the rendered TeX and the style, writes `stamp.tex` (not part of the hash), and writes `final_documents/generated/manifest.json`.

### Freshness path: `planspiel print --check`

1. Same config, texts and render steps as above, without TeX.
2. Recomputed `tex_sha256` and stamp hash are compared with the entries in `final_documents/generated/manifest.json`.
3. Exit 0 current, 1 stale, 2 environment problem (no git, unreadable inputs).

### Analysis path: enumeration and balance

1. `config.load_config` and `texts.load_content` (for the clue matrix in the balance report).
2. `enumerate` builds all dependency-valid measure selections per budget tier; `choices` and `report` compute summaries; the swap layer uses `rules.swap_credit` and change-window moves.
3. `gate.gate_tier` and `balance.build_balance_report` consume the summaries; `parallel.map_tiers` distributes tiers over processes when `--jobs > 1`.
4. Output: console report with verdicts and optional JSON summary (`simulation_summary_*.json`, gitignored) and JSONL dump (`simulation_full_*.jsonl`, gitignored).

### Validation path: `planspiel validate`, `texts`, `clues`

1. `config.read_raw_config` and `config.check_config` run structural checks; `validate.validate` adds hand-calculability and schedule checks.
2. `texts.check_texts` covers coverage, digits and giveaway lint; `texts.check_clues` checks the clue matrix in `content/clues.toml`.
3. Findings are `validate.Issue` records; any error exits non-zero.

**State Management:**
- No runtime state. Each run reads the config fresh. Module-level constants (for example `LEVEL_OPTIONS` in `enumerate.py`, `DOCUMENT_BUILDERS` in `render.py`, job constants such as `BOOKLET_JOB`, `MASTER_JOB`, `WAS_NEU_JOB`) are fixed identifiers, not mutable state.
- Parallel workers are separate processes that load the config from a path, never shared memory.

## Key Abstractions

**Config dataclasses:**
- Purpose: typed mirror of `simulation_config.json`.
- Examples: `planspiel/config.py` (`Config`, `Wave`, `Attack`, `Measure`, `BudgetTier`, `Event`, `Practice`, `ScheduleBlock`, `PrintRow`, `DebriefStage`, `SessionSchedule`, `FinalIndexWeights`).
- Pattern: plain `@dataclass`, built by private `_build_*` helpers, no mutation after loading.

**Rules kernel:**
- Purpose: the only definition of game formulas.
- Examples: `planspiel/rules.py` (`evaluate_path`, `path_trace`, `worksheet_constants`, `security_spend`, `budget_ledger`, `final_index`).
- Pattern: pure functions over `Config` and plain values; `TierTables` holds precomputed tier data for the analysis layer.

**Print model:**
- Purpose: one model per document, holding finished strings and fill lines.
- Examples: `planspiel/printmodel.py` (`AttackSheet`), `planspiel/booklet.py`, `planspiel/master.py`, `planspiel/was_neu.py`.
- Pattern: builder function returns a model; a `*_sources` or `*_document` function returns `{job: tex}`.

**Views (text access by audience):**
- Purpose: enforce veil at the type level.
- Examples: `PreAttackView` (pre-wave text, never revealed names), `RevealView` (revealed texts), `FacilitatorView` (facilitator texts incl. clue matrix), all defined in `planspiel/texts.py`.
- Pattern: a view object is handed to a builder; the pre-wave builders (`cards.py`, `eventtext.py`, `probelauf.py`) receive only `PreAttackView`.

**Print job:**
- Purpose: a named document with an audience prefix and a veil profile.
- Examples: `spieler-teamheft`, `angriff-1_ransomware`, `uebung-welle-0`, `spielleitung-uebersicht`.
- Pattern: job name = audience prefix plus slug; the `angriff-<n>_<attack_id>` names are derived in `printmodel.py`.

**Stamp:**
- Purpose: freshness marker on every page ("Stand <date> · <hash>").
- Examples: `planspiel/stamp.py`, `final_documents/generated/manifest.json`.
- Pattern: hash over rendered TeX plus style with normalised line endings; date from the last commit touching data inputs; "+lokal" for dirty trees.

**Result store and summaries:**
- Purpose: compact per-plan results for balance checks without rebuilding each plan.
- Examples: `planspiel/enumerate.py` (array-based store), `planspiel/report.py` (`summarize_tier`, `summarize_swap_layer`).
- Pattern: integer-coded plan indices (base 4 per measure, level 0-3), analysis functions read columns only.

## Entry Points

**`planspiel` console script:**
- Location: `planspiel/cli.py` (`main`), declared in `pyproject.toml` as `planspiel = planspiel.cli:main`; also `python -m planspiel` via `planspiel/__main__.py`.
- Subcommands:
  - `validate` (config structure, hand-calculability, schedule)
  - `tausch` (legal minimum swap layer per tier)
  - `referenzpfade` (candidate reference paths per tier)
  - `gate` (overspend gate; `--paths` for play paths; `--jobs`)
  - `texts` (text coverage, digits, story rules)
  - `clues` (clue matrix)
  - `print` (build PDFs; `--check` for freshness without TeX)
- Triggers: manual, from the facilitator or developer; the `print` path is the only one that writes into `final_documents/generated/`.

**Root wrapper scripts:**
- `simulate_outcomes.py`: calls `planspiel.simulate.main` (per-tier enumeration, `--budget-tier {low,medium,high}`).
- `analyze_simulation_results.py`: ranking and analysis over summaries (`planspiel.analyze`).
- `balance_analysis.py`: full balance report (`--layers all --paths --jobs 3 --out build/balance`), delegates to `planspiel.balance`.

**Test suite:**
- Location: `tests/`, pytest with markers `slow`, `pdf`, `balance`.
- Triggers: `uv run pytest` (fast), `-m pdf` (LuaLaTeX builds), `-m slow` (full enumeration), `tests -m balance` (design checks on a candidate config).

## Architectural Constraints

- **Threading:** single-threaded per process. Parallelism is process-based only, inside enumeration (`planspiel/parallel.py`, Windows spawn: worker functions at module level).
- **Global state:** none mutable. Module-level constants only. `tests/support/` holds helpers; no shared runtime state.
- **Circular imports:** avoided by layering. `rules.py` imports only `config` and `rounding`; `texts.py` imports `rules`, `audience`, `config`, `review_text`, `validate.Issue`; `validate.py` imports `rules.kz_slope`. `cli.py` imports its dependencies lazily inside each subcommand.
- **Isolation of the MHP baseline:** only `planspiel/was_neu.py` reads `content/mhp_baseline.json`; `render.py`, `cli.py` and `stamp.py` import the module, and `Config` has no baseline field. A test (`tests/test_baseline_isolation.py`) enforces this.
- **Isolation of the practice block:** `planspiel/practice.py` builds a throw-away `Config` with only the practice wave; the real waves, enumeration and gate never see it.
- **Archive:** `archive/` is outside every data flow. The build never reads it (`tests/test_no_archive_references.py`).
- **Generated output:** `final_documents/generated/` is written only by `planspiel print`. Five manual inputs (intro deck, MHP profile deck, VWI deck, two portrait photos) sit next to it and are not generated.
- **Large artifacts:** full enumeration dumps are gitignored and must not be read whole.

## Anti-Patterns

### Printing a number from a template

**What happens:** a template formats or computes a number inline.
**Why it's wrong:** the printed value can drift from the rules kernel; `render.tex_escape` rejects raw numbers and undefined names, so the build fails.
**Do this instead:** compute the string in the print model (for example `planspiel/booklet.py`) with `planspiel/fmt.py` from `rules` results, and insert it in the template.

### Re-implementing a formula outside the kernel

**What happens:** a helper in analysis, a print model or a wrapper repeats a formula from `rules.py`.
**Why it's wrong:** `tests/test_single_definition.py` fails, and the balance verdict and the worksheets can diverge.
**Do this instead:** add or call a function in `planspiel/rules.py` and keep the caller to formatting or aggregation.

### Using built-in `round()` for printed values

**What happens:** Python's `round()` (half to even) is used for KZ or RoS.
**Why it's wrong:** the printed rule is half away from zero; `round()` is forbidden in `planspiel/rules.py` and `planspiel/rounding.py`.
**Do this instead:** `planspiel.rounding.round_half_away` for integers and `round_half_away_frac` for `Fraction` values; `rules.ros_two_decimals` for RoS2.

### Revealed names in pre-wave builders

**What happens:** a pre-wave builder (cards, event text, probelauf, wave page) reads attack names or revealed texts.
**Why it's wrong:** the veil breaks before the wave; `veil.py` scans and fails the build, but the design should prevent it.
**Do this instead:** take a `PreAttackView` (from `planspiel/texts.py`) and put the job under a `spieler-` or `uebung-` prefix. Facilitator sheets use `RevealView` or `FacilitatorView` and the `spielleitung-` prefix.

### Writing directly into `final_documents/generated/`

**What happens:** a PDF or `manifest.json` is edited or copied by hand.
**Why it's wrong:** the stamp and hashes no longer match `print --check`, and the freshness gate fails.
**Do this instead:** change the inputs (config, README, texts), run `uv run planspiel print`, then `uv run planspiel print --check`, then commit the generated set together with the inputs.

### Importing the baseline outside `was_neu.py`

**What happens:** a module reads `content/mhp_baseline.json` for a non-"Was ist neu" purpose.
**Why it's wrong:** the frozen MHP values must not leak into the rules or the player material.
**Do this instead:** keep baseline reads inside `planspiel/was_neu.py` and extend that module.

## Error Handling

**Strategy:** fail fast at build and validation time. Any inconsistency is a `validate.Issue` (error) or a `PrintModelError` / `ValueError` raised by a builder; the CLI exits non-zero.

**Patterns:**
- `fmt.py` raises `ValueError` for values without a finite decimal form, so a rounded number never reaches a sheet.
- `render.register` raises on duplicate job names; `audience.audience_of` raises on an unclassified prefix.
- `texbuild.py` runs LuaLaTeX with a timeout and kills the process tree; MiKTeX installer is disabled so a missing package fails instead of hanging.
- `config.load_config` raises on structural problems; warnings are emitted via `warnings` for soft issues.

## Cross-Cutting Concerns

**Logging:** console output only (`print` to stdout, German, facilitator-facing). No logging framework.
**Validation:** `planspiel/validate.py` (config), `planspiel/texts.py` (texts, digits, story, clues), `planspiel/veil.py` (giveaways per audience), `tests/` (golden files and characterization).
**Authentication:** not applicable (offline, no users, no network service).

---

*Architecture analysis: 2026-11-09*
