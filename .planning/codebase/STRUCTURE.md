# Codebase Structure

**Analysis Date:** 2026-06-23

This repository is **overwhelmingly Markdown game-design documentation**, with a small set of standalone Python scripts for simulation/balance analysis and print-material generation. There is no `src/` directory, no package structure, no test suite — files live flat at the project root, grouped only by naming convention and a few subdirectories.

## Directory Layout

```
security-planspiel/
├── .claude/                          # Claude Code project config (skills, settings)
├── .planning/                        # GSD planning artifacts (this codebase map lives here)
│   └── codebase/                     # Generated codebase analysis docs (ARCHITECTURE.md, STRUCTURE.md, ...)
├── docs/                             # Short player-facing reference sheets
├── final_documents/                  # Finalized, print-ready game material (docx/pptx/pdf)
├── pptx_output/                      # Generated PowerPoint decks (intermediate/draft output)
├── __pycache__/                      # Python bytecode cache (not source)
│
├── README.md                         # Game rules, mechanics, formulas — SOURCE OF TRUTH for game logic
├── KONZEPT_MVP.md                    # Concept paper (MVP)
├── KONZEPT_MVP_v2.md                 # Concept paper (MVP, v2)
├── TODO.md                           # Development roadmap, milestones M1-M6
├── ROADMAP_6_TAGE.md                 # 6-day production schedule
├── TAG_2_DETAILPLAN.md               # Detailed plan for day 2 of production
├── SPIEL_DURCHFUEHRBARKEIT.md        # Playability/feasibility assessment
├── MATERIAL_CHECKLISTE.md            # Physical-materials checklist for facilitators
│
├── MODERATORENLEITFADEN.md           # Facilitator guide (long-form)
├── MODERATIONSSKRIPT.md              # Facilitator script (session-by-session)
├── SPIELERANLEITUNG.md               # Player briefing/instructions
├── DISCOVERY_FRAGEBOGEN.md           # Discovery-phase questionnaire (facilitator Q&A script)
├── QUICK_REFERENCE_CARD.md           # One-page quick reference for play
│
├── MASSNAHMENKARTEN.md               # Measure card content (source for measure slides/cards)
├── ANGRIFFSKARTEN.md                 # Attack card content (source for attack slides/cards)
│
├── PARAMETER_TABELLE.md              # Parameter overview table (human-readable mirror of config)
├── BACKUP_PARAMETER.md               # Backup/alternate parameter set
│
├── BERECHNUNGSBOGEN_WELLE1_RANSOMWARE.md      # Paper calculation worksheet, wave 1 (ransomware)
├── BERECHNUNGSBOGEN_WELLE2_OT_STOERUNG.md     # Paper calculation worksheet, wave 2 (OT disruption)
├── BERECHNUNGSBOGEN_WELLE3_EXFILTRATION.md    # Paper calculation worksheet, wave 3 (data exfiltration)
│
├── FORMULARE.md                      # Printable forms (general)
├── TEAM_TRACKING_BOGEN.md            # Printable team tracking sheet
├── ASSETS_DRUCKVORLAGEN.md           # Print template/asset reference
│
├── BALANCE_ANALYSE.md                # Balance analysis write-up (QA)
├── EVALUIERUNGSPLAN.md               # Evaluation plan (QA/playtest methodology)
├── BEOBACHTUNGSBOGEN_PLAYTEST.md     # Playtest observation sheet
├── ENDAUSWERTUNG_ROS_VERGLEICHSWERT.md  # Final scoring/RoS benchmark reference
│
├── simulation_config.json            # CENTRAL CONFIG — single source of truth for all numeric values
├── simulate_outcomes.py              # Enumerates all deterministic outcomes from config
├── analyze_simulation_results.py     # Ranks/analyzes simulation results (Final-Index = KZ + RoS)
├── balance_analysis.py               # Checks for dominant strategies (imports simulate_outcomes.py)
├── generate_attack_calculator.py     # Generates Excel attack-calculation workbook
├── generate_from_template.py         # Fills an existing .pptx template with config-derived text
├── generate_pptx_cards.py            # Builds .pptx decks (measure/event cards) from scratch
│
├── sim_low.json                      # Pre-computed simulation results, "low" budget tier (~14 MB)
├── sim_med.json                      # Pre-computed simulation results, "medium" budget tier (~52 MB)
├── angriff_berechnung.xlsx           # Generated Excel attack calculator (output artifact)
│
├── .gitattributes
└── .gitignore
```

## Directory Purposes

**`docs/`:**
- Purpose: Short, focused reference sheets meant to be handed to players/teams during play, distinct from the long-form facilitator/design documents at the root
- Contains: `cia_schnellreferenz.md` (CIA & mitigation quick reference — budget tiers, KZ-start, E-targets per wave), `mitigation_bewertungsblatt.md` (mitigation scoring worksheet for teams to fill in)
- Key files: `docs/cia_schnellreferenz.md`, `docs/mitigation_bewertungsblatt.md`

**`final_documents/`:**
- Purpose: Finalized, print-ready game materials distributed/printed for the live session
- Contains: `.docx`/`.pptx`/`.pdf` files — e.g. `Unternehmenssteckbrief MechTech.docx` (company profile), `Budget.docx`, `Angriff-1_Ransomware.docx`, `Angriff-2_OT-Störung.docx`, `Angriff-3_Datenexfiltration.docx`, `Anfrage-Mail.pdf`, `Audit-Mail.pdf`, `Zeitungsartikel.pdf` (newspaper-article prop), `Return on Security und Final Wert.docx`, `Events_Security-Game.pptx`, `Folien_security-game.pptx`, `Massnahmenkarten_Security-Game.pptx`
- Generated: Partially — some files originate from generator scripts (the `*_Security-Game.pptx` decks), others (docx/pdf props) are authored directly and not regenerable by any script in this repo
- Committed: Yes — these are the binary deliverables

**`pptx_output/`:**
- Purpose: Intermediate/draft output of the PPTX generator scripts, used for review before promoting a deck into `final_documents/`
- Contains: `Events.pptx`, `Events_Generated.pptx`, `Events_Security-Game.pptx`, `Massnahmenkarten.pptx`, `Massnahmenkarten_Generated.pptx`, `Massnahmenkarten_Generated_updatedTemp.pptx`, `Massnahmenkarten_Security-Game.pptx`
- Generated: Yes, by `generate_pptx_cards.py` (the `*_Generated.pptx` files) and `generate_from_template.py` (the `*_Security-Game.pptx` files)
- Committed: Yes (per `ls -la` these are tracked, not gitignored) — treat as build output, regenerate rather than hand-edit

**`__pycache__/`:**
- Purpose: Python bytecode cache
- Generated: Yes, automatically by the interpreter
- Committed: Should not be (verify against `.gitignore`); not source material

**`.planning/`:**
- Purpose: GSD (this tool's) planning and codebase-mapping artifacts
- Contains: `.planning/codebase/` — this document and its siblings (ARCHITECTURE.md, STACK.md, etc., as produced by other mapper runs)

## Key File Locations

**Source of truth for game logic:**
- `README.md`: Rules, state machine, all formulas (M_sum, G, E-value, RoS) — read this first for any rule change

**Central data/config:**
- `simulation_config.json`: Every numeric value used by the simulation (budget tiers, wave weights/thresholds, attacks, measures, events, base CIA)

**Simulation/analysis entry points:**
- `simulate_outcomes.py`: `python3 simulate_outcomes.py --config simulation_config.json --budget-tier medium --output simulation_results.json`
- `analyze_simulation_results.py`: `python3 analyze_simulation_results.py --input simulation_results.json --config simulation_config.json --top 5`
- `balance_analysis.py`: `python3 balance_analysis.py` (no args; defines and compares fixed strategies internally)

**Print-material generators:**
- `generate_attack_calculator.py` → `angriff_berechnung.xlsx`
- `generate_from_template.py` → `pptx_output/*_Security-Game.pptx`
- `generate_pptx_cards.py` → `pptx_output/*_Generated.pptx`

**Pre-computed result caches (large files — parse selectively, never read in full):**
- `sim_low.json` (~14 MB), `sim_med.json` (~52 MB)

**Project/AI tooling instructions:**
- `CLAUDE.md`: Repo orientation and editing conventions for AI assistants working in this repo

## Naming Conventions

**Files:**
- Game-design documents at root use German, all-caps, underscore-separated names matching their content's purpose, e.g. `MASSNAHMENKARTEN.md` (measure cards), `ANGRIFFSKARTEN.md` (attack cards), `BERECHNUNGSBOGEN_WELLEn_<ANGRIFFSTYP>.md` (per-wave calculation worksheet, numbered and named after the wave's attack theme)
- Python scripts use lowercase snake_case verbs describing their action: `simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`, `generate_<artifact>.py`
- Generated/output files in `pptx_output/` append `_Generated` (built from scratch via `generate_pptx_cards.py`) or `_Security-Game` (built by filling a template via `generate_from_template.py`) to the base name, allowing both pipelines' outputs to coexist for comparison

**Directories:**
- Lowercase, purpose-named: `docs/`, `final_documents/`, `pptx_output/` — no nested package/module hierarchy

## Where to Add New Code

**New game rule or formula:**
- First add/adjust the underlying numbers in `simulation_config.json`
- Then update the prose description and formula in `README.md` if the rule itself (not just a parameter) changed
- Then update any affected card/worksheet documents (`MASSNAHMENKARTEN.md`, `ANGRIFFSKARTEN.md`, `BERECHNUNGSBOGEN_WELLE*.md`) so prose and config stay in sync (mandatory per `CLAUDE.md`)

**New attack, measure, or event:**
- Add the entry to `simulation_config.json` under `attacks`, `measures`, or `events`
- Add matching descriptive content to `ANGRIFFSKARTEN.md` or `MASSNAHMENKARTEN.md`
- Re-run `simulate_outcomes.py` + `balance_analysis.py` to check for dominance/inconsistency before regenerating print material

**New simulation/analysis capability:**
- Add a new top-level script at the repo root following the existing `snake_case_verb.py` naming pattern (mirroring `analyze_simulation_results.py` / `balance_analysis.py`)
- If it needs core simulation primitives (loading config, computing CIA/costs/E-value), import them from `simulate_outcomes.py` rather than reimplementing — this is the existing pattern used by `balance_analysis.py`

**New print/generated artifact:**
- Add a new `generate_*.py` script at the repo root
- Write its draft output into `pptx_output/` (or an analogous new folder for a new artifact type, e.g. an `xlsx_output/` if multiple Excel artifacts emerge)
- Only promote a finished, reviewed artifact into `final_documents/` once it is print-ready; do not edit files inside `final_documents/` directly

**New facilitator/player-facing reference material:**
- Short, in-session reference sheets belong in `docs/` (following `cia_schnellreferenz.md` / `mitigation_bewertungsblatt.md`)
- Long-form facilitator guidance belongs at the root alongside `MODERATORENLEITFADEN.md` / `MODERATIONSSKRIPT.md`

## Special Directories

**`pptx_output/`:**
- Purpose: Draft/intermediate generated decks
- Generated: Yes
- Committed: Yes (treat as reviewable build output, not hand-edited source)

**`final_documents/`:**
- Purpose: Finalized print deliverables for the live session
- Generated: Mixed — some originate from generator scripts, others are manually authored props (emails, newspaper article, company profile) with no generator counterpart in this repo
- Committed: Yes

**`__pycache__/`:**
- Purpose: Python bytecode cache
- Generated: Yes
- Committed: No (should be excluded via `.gitignore` — verify if untracked)

**`.planning/`:**
- Purpose: GSD workflow state and generated codebase documentation (not game content)
- Generated: Yes (by GSD tooling)
- Committed: Project-dependent; not part of the game design itself

---

*Structure analysis: 2026-06-23*
