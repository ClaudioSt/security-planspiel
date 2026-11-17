# Codebase Structure

**Analysis Date:** 2026-11-09

## Directory Layout

```
security-planspiel/
├── simulation_config.json      # Single source of every number (committed)
├── README.md                   # German rulebook, no fixed numbers (committed)
├── CLAUDE.md                   # Repo working rules (committed)
├── pyproject.toml              # uv project, console script `planspiel`, pytest config
├── uv.lock                     # Locked dependencies
├── .python-version             # Python 3.12
├── simulate_outcomes.py        # Thin wrapper -> planspiel.simulate
├── analyze_simulation_results.py  # Thin wrapper -> planspiel.analyze
├── balance_analysis.py         # Thin wrapper -> planspiel.balance report
├── planspiel/                  # Python package: config, rules, analysis, print models, pipeline, CLI
├── content/                    # German prose, clue matrix, veil lists, MHP baseline, assets
├── print/                      # LaTeX style and Jinja2 templates
├── final_documents/            # generated/ (build output) + five manual input files
├── tests/                      # pytest suite, golden data, fixtures, support helpers
├── archive/                    # History only, outside the build (never read by code)
├── .planning/                  # GSD planning artifacts (roadmap, phases, codebase maps)
├── .claude/                    # Claude Code settings, hooks, generated CLAUDE.md
└── build/                      # Gitignored local output (balance reports)
```

## Directory Purposes

**`planspiel/`:**
- Purpose: the whole Python package. Layers import downward (see ARCHITECTURE.md).
- Contains: 50 modules (about 13,200 lines), flat layout, no subpackages.
- Key files: `rules.py` (formulas), `config.py` and `validate.py` (config), `texts.py` and `veil.py` (content and veil), `enumerate.py` and `gate.py` (analysis), `render.py` and `texbuild.py` and `stamp.py` (print pipeline), `cli.py` (entry point).

**`content/`:**
- Purpose: all German prose and content rules.
- Contains: `texte.toml` (all prose), `clues.toml` (which story document points to which attack), `digit_allowlist.toml` (digits allowed in prose), `giveaway_terms.toml` (terms forbidden on player-facing pages), `mhp_baseline.json` (frozen MHP-round values, read only by `planspiel/was_neu.py`), `assets/` (images), `INVENTORY.md`.
- Key files: `content/texte.toml`, `content/clues.toml`.
- Assets: `content/assets/images/zeitungsartikel_bild_audit.png`, `content/assets/images/zeitungsartikel_bild_fabrik.png`; `content/assets/GUIDELINES.md` and `content/assets/README.md` describe them.

**`print/`:**
- Purpose: LaTeX layer of the print pipeline.
- Contains: `planspiel.sty` (style), `miktex-packages.txt` (required MiKTeX packages), `templates/`.
- `print/templates/` holds 15 Jinja2 LaTeX templates (`*.tex.j2`):
  - Attack: `angriff.tex.j2` (worksheet), `angriff_blatt.tex.j2`
  - Cards: `karten.tex.j2`
  - Team booklet: `teamheft.tex.j2`, `teamheft_planung.tex.j2`, `teamheft_ros.tex.j2`, `teamheft_tracking.tex.j2`
  - Wave and practice: `welle.tex.j2`, `uebung.tex.j2`
  - Story: `story_mail.tex.j2`, `story_steckbrief.tex.j2`, `story_zeitungsartikel.tex.j2`
  - Facilitator: `master.tex.j2`, `probelauf.tex.j2`, `was_neu.tex.j2`

**`final_documents/`:**
- Purpose: the printed game material and its inputs.
- `final_documents/generated/`: the only game material. Written by `uv run planspiel print`; never edit by hand. Contains 15 PDFs and `manifest.json`:
  - `spieler-` (8): `spieler-anfrage-mail.pdf`, `spieler-audit-mail.pdf`, `spieler-eventkarten.pdf`, `spieler-massnahmenkarten.pdf`, `spieler-so-funktioniert-eine-welle.pdf`, `spieler-teamheft.pdf`, `spieler-unternehmenssteckbrief.pdf`, `spieler-zeitungsartikel.pdf`
  - `uebung-` (1): `uebung-welle-0.pdf`
  - `angriff-` (3): `angriff-1_ransomware.pdf`, `angriff-2_ot.pdf`, `angriff-3_exfil.pdf`
  - `spielleitung-` (3): `spielleitung-probelauf.pdf`, `spielleitung-uebersicht.pdf`, `spielleitung-was-ist-neu.pdf`
- Manual inputs (not generated, not touched by the build): `Planspiel_Einführung + Grundlagen.pptx` (intro deck), `MHP Company Profile DE - Jubilee Logo.pptx`, `13052026_VWI meets MHP_Offenes Treffen.pptx`, `Stanullo Claudio_2022_04.jpg` and `DanielGhebreselassie 1.jpg` (portrait photos).

**`tests/`:**
- Purpose: pytest suite (114 test modules), golden references, fixtures, support helpers.
- `tests/golden/`: pinned reference data (`characterization_*.json`, `digest_*.json`, `gate_*.json`, `gate_paths_*.json`, `answer_keys.json`, `welle0.json`, `worksheet_tex.json`).
- `tests/fixtures/`: `mini_config.json`, `mini_content/`, `print/`.
- `tests/support/`: helpers (`harness.py`, `golden.py`, `golden_cases.py`, `digest.py`, `candidate.py`, `gitrepo.py`, `pdf_text.py`, `tex.py`, `ties.py`, `tracking_replay.py`, `worksheet_replay.py`, `peak_memory.py`).
- `tests/conftest.py`: registers the `--planspiel-config` and `--planspiel-content-dir` options for `balance` tests.
- Test name prefixes map to areas: `test_rules_*`, `test_enumeration*`, `test_gate*`, `test_balance_report.py`, `test_print_*`, `test_*_pdf.py` (LuaLaTeX, marker `pdf`), `test_*_model.py` (print models), `test_veil_*`, `test_texts_*`, `test_validate.py`, `test_readme_current.py`, `test_no_archive_references.py`.

**`archive/`:**
- Purpose: history, outside the build. Touch only on explicit request.
- Contents: `historical_docs/` (earlier design documents, different formulas, not reference), `legacy_generators/` (retired generator scripts, Excel calculator, `pptx_output/`), `mhp_print_material_2026-07/` (superseded MHP docx/pptx/pdf material), `obsolete_docs_reference_sheets/`, `obsolete_simulation_data_2026-01/`.
- Not mapped as live code. No file under `planspiel/`, `tests/` or `print/` reads it.

**`.planning/`:**
- Purpose: GSD project state. `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `config.json`, `phases/` (01 to 07 with plans, summaries, research, validation and verification files), `research/`, `todos/`, `codebase/` (these maps).
- Current phase at time of mapping: 07 (session flow and handoff), with the Phase 7 print models `schedule.py`, `debrief.py`, `was_neu.py` and `probelauf.py`.

**`.claude/`:**
- Purpose: Claude Code configuration. `CLAUDE.md` (generated stack and architecture summary), `settings.json`, `settings.local.json`, `hooks/session-start.sh`.

**`build/`:**
- Purpose: gitignored local output (for example `uv run python balance_analysis.py --out build/balance`).

## Key File Locations

**Entry Points:**
- `planspiel/cli.py`: `planspiel` subcommands (`validate`, `tausch`, `referenzpfade`, `gate`, `texts`, `clues`, `print`).
- `planspiel/__main__.py`: `python -m planspiel`.
- `simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`: root wrappers.

**Configuration:**
- `simulation_config.json`: all numbers (budget tiers, waves, attacks, measures, events, final events, `final_index`, `practice`, `session_schedule`, `reference_plans`, `reference_strategies`).
- `planspiel/config.py`: loader and dataclasses.
- `planspiel/validate.py`: config checks.
- `pyproject.toml`: packaging, console script, pytest options (`addopts = "-m 'not slow and not pdf' --strict-markers"`).
- `.python-version`: Python 3.12.

**Core Logic:**
- `planspiel/rules.py`: game formulas (single definition).
- `planspiel/enumerate.py`, `planspiel/choices.py`, `planspiel/report.py`: enumeration and summaries.
- `planspiel/gate.py`: overspend gate.
- `planspiel/balance.py`: consolidated balance report.
- `planspiel/render.py`: `DOCUMENT_BUILDERS` and `render_all`.

**Print Models (one per document family):**
- `planspiel/printmodel.py`: attack worksheets (job `angriff-<n>_<attack_id>`, derived in this module).
- `planspiel/cards.py`: `spieler-massnahmenkarten`, `spieler-eventkarten`.
- `planspiel/booklet.py`: `spieler-teamheft`.
- `planspiel/wave_page.py`: `spieler-so-funktioniert-eine-welle`.
- `planspiel/story.py`: `spieler-unternehmenssteckbrief`, `spieler-zeitungsartikel`, `spieler-anfrage-mail`, `spieler-audit-mail`.
- `planspiel/practice.py`: `uebung-welle-0` (throw-away config view).
- `planspiel/master.py`: `spielleitung-uebersicht` (facilitator master sheet, includes the debrief).
- `planspiel/schedule.py`: session schedule model shared by booklet and probelauf.
- `planspiel/debrief.py`: facilitator debrief stages.
- `planspiel/probelauf.py`: `spielleitung-probelauf` (dry-run protocol, FLOW-05).
- `planspiel/was_neu.py`: `spielleitung-was-ist-neu` (only reader of `content/mhp_baseline.json`).

**Content and Veil:**
- `planspiel/texts.py`: `content/texte.toml` loader, views, coverage, digit and story lint, clue check.
- `planspiel/veil.py`: giveaway scan per audience profile.
- `planspiel/audience.py`: job-prefix classification.
- `planspiel/eventtext.py`: event effect lines.
- `planspiel/review_text.py`, `planspiel/fmt.py`: German number and EUR text.

**Print Pipeline:**
- `planspiel/render.py`: Jinja2 environment and registry.
- `planspiel/texbuild.py`: LuaLaTeX driver and job-name check.
- `planspiel/stamp.py`: stamp, hash and `manifest.json`.
- `final_documents/generated/manifest.json`: committed hashes of each document.

**Testing:**
- `tests/conftest.py`: pytest options and fixtures.
- `tests/golden/`: pinned outputs.
- `tests/test_single_definition.py`: enforces the single rules definition.
- `tests/test_no_archive_references.py`: enforces the archive boundary.
- `tests/test_baseline_isolation.py`: enforces the MHP baseline boundary.

## Naming Conventions

**Files:**
- Python modules: snake_case, one domain concept per module (for example `index_weights.py`, `was_neu.py`, `wave_page.py`). Print model modules are named after the document family.
- Tests: `test_<area>.py`, with suffixes `_model`, `_render`, `_pdf` (LuaLaTeX, marker `pdf`), `_values`, `_coverage`.
- Templates: `<document>.tex.j2`; sub-pages of the team booklet use the prefix `teamheft_`, story templates `story_`.
- Print job names: `<audience>-<slug>` where audience is one of `spieler`, `uebung`, `angriff`, `spielleitung`. Attack jobs: `angriff-<wave>_<attack_id>`. The slug uses hyphens (`spielleitung-was-ist-neu`); the attack id uses underscores (`angriff-1_ransomware`).
- Generated PDFs: `<job>.pdf` in `final_documents/generated/`.

**Directories:**
- Lowercase, single words or hyphen-free (`planspiel`, `content`, `print`, `tests`, `archive`). Planning phase directories: `NN-slug` (for example `07-session-flow-handoff`).

**Identifiers in code:**
- snake_case functions, verb-first (`compute_*`, `build_*`, `check_*`, `load_*`, `render_*`, `summarize_*`).
- PascalCase dataclasses named after domain entities (`Wave`, `Attack`, `Measure`, `Config`).
- Domain abbreviations unexplained in code: `kz`, `cia`, `e_value`, `e_threshold`, `opex`, `init`, `ros`.
- Job-name constants: `*_JOB` (for example `BOOKLET_JOB`, `MASTER_JOB`, `WAS_NEU_JOB`, `PROBELAUF_JOB`, `PRACTICE_JOB`).

## Where to Add New Code

**New game formula or rule change:**
- Formula: `planspiel/rules.py` (only place). Add the failing test first (TDD) in `tests/test_rules_*.py` or `tests/test_rules_exact.py`.
- Operand: `simulation_config.json` and `planspiel/config.py` (dataclass field) plus `planspiel/validate.py` (structure check).
- Then: README, `content/texte.toml`, `uv run planspiel print`, `uv run planspiel print --check`, `uv run planspiel gate --paths --jobs 3`, and the full balance run.

**New printed document:**
- Print model: a new module in `planspiel/` named after the document family (follow `cards.py` or `wave_page.py`), returning `{job: source}`.
- Template: `print/templates/<name>.tex.j2`; the template only loops and places strings.
- Registration: add the builder to `DOCUMENT_BUILDERS` in `planspiel/render.py` (or call it from `render_all` as `was_neu.py` is). The job name must start with an audience prefix.
- Audience and veil: classify in `planspiel/audience.py`; check `planspiel/veil.py` profile rules.
- Tests: `tests/test_<name>_model.py` (model), `tests/test_<name>_render.py` (render), `tests/test_<name>_pdf.py` (marked `pdf`).

**New prose:**
- Text: `content/texte.toml` under the config ID path. Run `uv run planspiel texts`. No digits unless listed in `content/digit_allowlist.toml`.
- Clue: `content/clues.toml`; run `uv run planspiel clues`.
- Forbidden term on player pages: `content/giveaway_terms.toml`.

**New analysis or balance check:**
- Module: `planspiel/` next to the existing check (for example `spread.py`, `rewarding.py`). Pure functions over `report` summaries.
- Wire into `planspiel/balance.py` (`build_balance_report`) and, if it needs a CLI, `planspiel/cli.py` (lazy import inside the subcommand).
- Tests: `tests/test_<check>.py`, plus a `balance`-marked test if it is a design principle.

**New CLI subcommand:**
- `planspiel/cli.py`: add a `subparsers.add_parser(...)` and a `cmd` function with a lazy import of the module it calls. Do not put logic into `cli.py`.

**New test:**
- `tests/test_<area>.py`, real config and real rules (no mocks for rules). Golden data goes into `tests/golden/`; helpers into `tests/support/`.

**Utilities and shared helpers:**
- Number formatting: `planspiel/fmt.py` (German) and `planspiel/review_text.py` (EUR text).
- Rounding: `planspiel/rounding.py`.
- Parallel tier runs: `planspiel/parallel.py`.

**Do not add to:**
- `final_documents/generated/` (generated only).
- `archive/` (history, outside the build).
- `planspiel/rules.py` any I/O, print or text code.

## Special Directories

**`final_documents/generated/`:**
- Purpose: the printed game set plus `manifest.json`.
- Generated: Yes, by `uv run planspiel print`.
- Committed: Yes, together with the inputs that produced it. Never edit by hand; a dirty build ends its stamp in "+lokal" and is not committed.

**`archive/`:**
- Purpose: history (earlier design documents, legacy generators, superseded MHP print material, obsolete reference sheets and simulation data).
- Generated: No.
- Committed: Yes, but outside the build. Not read by code (enforced by `tests/test_no_archive_references.py`). Touch only on explicit request.

**`build/`:**
- Purpose: local balance report output.
- Generated: Yes.
- Committed: No (gitignored).

**Gitignored large artifacts (repo root):**
- `simulation_results*.json`, `sim_low.json`, `sim_med.json`, `sim_high.json`, `simulation_summary_*.json`, `simulation_full_*.jsonl`.
- Purpose: full enumeration dumps. Generated by the simulation. Never committed; parse selectively with `jq` or Python, never read whole.

**`.planning/phases/`:**
- Purpose: GSD phase records (plans, summaries, verification). Committed.
- Generated: by GSD commands. Current active phase: `07-session-flow-handoff`.

**`.planning/research/.cache/`:**
- Purpose: cached research responses. Committed as present in the repository.

---

*Structure analysis: 2026-11-09*
