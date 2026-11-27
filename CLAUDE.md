# CLAUDE.md

Guide for Claude Code when working in this repository. The generated stack, conventions and architecture summaries live in `.claude/CLAUDE.md`; this file covers purpose, layout, game mechanics and working rules. Game content and print material are German; code, docs and commit messages are English.

## What this is

An **offline IT-security business game** ("CIA-Planspiel Automotive") for students and teams. Participants act as consulting teams for a fictional automotive supplier (MechTech), negotiate a budget, choose security measures at levels L1/L2/L3, react to deterministic events and three attack waves, and optimize customer satisfaction (KZ), CIA goal fulfilment (Confidentiality/Integrity/Availability) and Return on Security (RoS).

Core principle: **determinism instead of chance.** The same inputs always give the same outputs, there are no dice. Every number is parametrized in `simulation_config.json`, none is hard-coded.

The game is played live on **paper only**: teams work on their printed Teamheft, worksheets and cards, and the facilitator leads from the printed facilitator booklet. There is no board write-up step. The repo does not run the game; it holds the config, the rules code, the balance tooling and the generator of **all print material**, which is rendered from config and texts.

## Repository layout

- `simulation_config.json`: the single source of every number (budget tiers, waves, attacks, measures, events, final events, `final_index`, `practice`, `session_schedule`, reference plans and strategies).
- `planspiel/`: the package behind the `planspiel` console script. `rules.py` is the single definition of the game formulas; `config.py`/`validate.py` load and check the config; `enumerate.py`, `gate.py`, `balance.py` and friends do the full enumeration and balance checks; the print models (`printmodel.py`, `cards.py`, `booklet.py`, `wave_page.py`, `story.py`, `practice.py`, `master.py`, `schedule.py`, `debrief.py`, `was_neu.py`, `probelauf.py`), `render.py`, `texbuild.py` and `stamp.py` build the PDFs.
- `content/`: `texte.toml` (all prose), `clues.toml` (which story document points to which attack), `digit_allowlist.toml` (digits allowed in prose), `giveaway_terms.toml` (terms the veil forbids on player-facing pages), `mhp_baseline.json` (frozen state of the MHP round, read only by the Was-ist-neu sheet), `assets/` (images), `INVENTORY.md`.
- `print/`: `planspiel.sty` and the Jinja2 LaTeX templates in `print/templates/`.
- `tests/`: pytest suite with the markers `slow`, `pdf` and `balance` (see below); `tests/golden/` holds pinned reference data.
- `final_documents/generated/`: the **only** game material. Every PDF there, plus `manifest.json`, is produced by `uv run planspiel print`; never edit one by hand. Next to it `final_documents/` holds five kept manual files: the intro deck (`Planspiel_Einführung + Grundlagen.pptx`), the MHP company profile deck, the VWI deck and two portrait photos. They are inputs of the event, not generated.
- `archive/`: history, outside the build (a test proves nothing in the build reads it). `archive/historical_docs/` holds the earlier markdown design documents (including the former `docs/` folienkonzept); they use formulas and numbers that differ from the current config (`M_sum`/`kzUnit` model) and must not be used as reference or kept in sync. `archive/legacy_generators/` holds the three retired generator scripts, the Excel calculator and `pptx_output/`. `archive/mhp_print_material_2026-07/` holds the superseded docx/pptx/pdf print material of the MHP round. `archive/obsolete_*` hold old quick-reference pages and simulation dumps. Touch `archive/` only on explicit request.
- Root: `README.md` is the current rulebook (German, no fixed numbers). `simulate_outcomes.py`, `analyze_simulation_results.py` and `balance_analysis.py` are thin entry-point wrappers around the package.

## Game mechanics in brief (implemented in `planspiel/rules.py`)

- **State machine per run:** Intro, story and group work, Welle 0 (practice wave, worked example, not scored), budget negotiation, measure choice, then per wave: events, attack, OPEX and recovery; a change window after every wave but the last; closing and budget review; debrief.
- **Veil:** before its wave an attack stays veiled; its name and exact values appear only on its worksheet, handed out when the wave starts, and in facilitator documents. The mechanics themselves (formulas, weights, thresholds) are always open. Story documents carry clues, never a named gap (`content/clues.toml`, `uv run planspiel clues`).
- **E-Wert per wave:** `E-Wert = Team_C*wC + Team_I*wI + Team_A*wA`, team CIA = `base_cia` + sum of the measures' CIA contributions.
- **Gesamtbonus:** sum of the `bonus_measures` bonuses whose measure reaches its `min_level` (2-3 thematically fitting measures per wave).
- **Gesamtreduktion:** `E-Wert + Gesamtbonus`.
- **Deterministic resolution (three cases on the attack worksheets):**
  - `reduction_over_threshold = min(mitigation_cap, max(0, Gesamtreduktion - e_threshold))`: case 1 at or below the threshold (no reduction), case 2 cap reached (no damage), case 3 between threshold and cap (linear), as on the worksheet and in `rules.path_trace`.
  - `severity = max(0, base_severity*severity_multiplier - reduction_over_threshold)`
  - `damage = severity * s_unit`, times `(1 - recovery_factor)` when `allow_recovery` is set and a recovery measure is active.
  - `KZ delta = kz_at_full_damage + (reduction_over_threshold / mitigation_cap) * (kz_at_full_mitigation - kz_at_full_damage)`: **linearly interpolated on purpose** (see the comment in `attack_kz_delta()` in `planspiel/rules.py`), not the case-3 sub-formula of older documents.
- **Rounding (as on paper):** the KZ change of a wave (attack plus events) is rounded exactly once to a whole number, half away from zero (+2.5 becomes +3, -2.5 becomes -3; `planspiel.rounding.round_half_away`), then KZ is clamped to 0-100. E-Wert, Gesamtreduktion, reduction over threshold and severity stay exact (integer arithmetic via `Fraction`/scaling); damage stays exact in whole euros. Python's built-in `round()` (half to even) is forbidden in `planspiel/rules.py` and `planspiel/rounding.py`.
- **RoS:** `(620,000 - total damage - own cost) / own cost`; own cost = init + OPEX per wave + init differences and the Kurswechsel difference, without event effects (`rules.security_spend`). **Final-Index** (facilitator-side comparison across teams and tiers): `weight_kz * KZ + weight_ros * RoS2`, RoS2 being RoS rounded to two decimals half away from zero (`rules.ros_two_decimals`); weights are in the config block `final_index` (`weight_kz` = 1, `weight_ros` = k, an integer chosen from the spread in `planspiel/index_weights.py`).
- **Budget review:** remaining-budget bands for a remainder >= 0; an overspend costs -X KZ per started step (`overspend_penalty.kz_per_step`, calibrated as the largest X any static or play path needs plus 1, `planspiel gate --paths`; `rules.budget_review_delta`). Once at the end, then clamp to 0-100.
- **Change window:** level up or down, cancel, add, any number of moves; init differences are netted and paid immediately, init is never refunded; effect and OPEX from the next wave (`rules.evaluate_path`). `planspiel tausch` computes the legal minimum swap layer.
- **Kurswechsel (wave 1):** exactly one mandatory measure swap in the change window after it (an active measure out, a measure inactive in wave 1 in, level free); the customer bears the init up to the value of the swapped-out measure (`rules.swap_credit`). The static enumeration is the reference plan without change-window moves.
- All formulas are **fixed**, all values **configurable** via `simulation_config.json`. Hand-calculability (linear formulas, no exponents) is a hard design criterion: facilitators recompute the worksheets by hand.

## Print pipeline

All print material is generated; nothing in `final_documents/generated/` is maintained by hand and there is no manual docx/pptx trap any more.

- **Numbers** live only in `simulation_config.json`, **prose** only in `content/texte.toml`. A digit lint rejects digits in prose unless they are listed in `content/digit_allowlist.toml`, and the validator rejects prose in the config (`prose_in_config`). Never write a fixed number into a prose document without it existing in the config.
- **Order of a content change:** `simulation_config.json` -> `README.md` -> `content/texte.toml` -> `uv run planspiel print` -> `uv run planspiel print --check` -> commit `final_documents/generated/` together with the inputs.
- `uv run planspiel validate` checks the config (structure, hand-calculability, schedule); `uv run planspiel texts` checks `texte.toml` (coverage, digits, story rules); `uv run planspiel clues` shows and checks the clue matrix.
- `uv run planspiel print` renders the Jinja2 templates and builds every PDF with LuaLaTeX (MiKTeX) into `final_documents/generated/`, plus `manifest.json`. Every page carries a stamp "Stand <date> · <hash>" computed from the committed inputs; if an input has local changes the stamp ends in **"+lokal"**, and such a build is not meant to be committed. Build only after the inputs are committed, then commit the PDFs.
- `uv run planspiel print --check` builds no TeX; it verifies that the committed PDFs match the current config, texts and templates (exit 0 current, 1 stale, 2 environment problem). Run it before every commit that touches an input.
- Veil and audience rules apply to every page: player-facing pages never name an attack before its wave (`content/giveaway_terms.toml`, `planspiel/veil.py`, `planspiel/audience.py`).

## Working in this repo

- **Environment:** run `uv sync` once. Always run scripts as `uv run python <script>.py`, the console script as `uv run planspiel <command>`, and tests as `uv run pytest`. Never use the `python` on PATH (on this machine it is Inkscape's interpreter without pip).
- **Tests:** `uv run pytest` is the fast suite (excludes the markers below). `uv run pytest -m pdf` builds real PDFs with LuaLaTeX and skips when no TeX engine or package is available. `uv run pytest -m slow` runs the full enumeration over all dependency-valid combinations per tier. `uv run pytest tests -m balance` runs the Phase-6 design-principle checks.
- **Candidate check:** the `balance` tests read the config from `--planspiel-config` (default `simulation_config.json`) and the content directory from `--planspiel-content-dir` (default `content/`); for a new candidate run `uv run pytest tests -m balance --planspiel-config <candidate> --planspiel-content-dir <dir>` (the `tests` path is needed so the options load). Hand-calculation findings are errors (`validate` and `load_config`); the clue mapping in `content/clues.toml` is mandatory.
- **Verify balance by full enumeration.** `uv run python balance_analysis.py --layers all --paths --jobs 3 --out build/balance` is the full report: distribution with top-K and Pareto front within budget next to the optima over budget, the overspend gate with paths and the calibration of X, the hand-calculation check, the Final-Index weight, decisions, reference strategies with clue mapping, reward and spread, each with a verdict and failing lines; exit 0 only if every computed check passes. Without `--layers all` only the static layer runs (quick check). `--baseline-config simulation_config.json` adds the before/after comparison for the acceptance checkpoint. Single tiers: `uv run python simulate_outcomes.py --budget-tier {low,medium,high}`.
- After value changes also run `uv run planspiel gate` (or `uv run planspiel gate --paths --jobs 3`): the trim-back criterion, overspending must never pay off, also on the play paths with swap and one window move; it fails naming the determining plan if X is too small and gives the calibration X = maximum + 1.
- When changing a formula (for example the interpolation), first check that the values on the attack worksheets stay hand-recomputable (linear formulas, no exponents).
- **Large artifacts:** full enumeration dumps (`simulation_results*.json`, `sim_low.json`, `sim_med.json`, `sim_high.json`, `simulation_full_*.jsonl` with `--dump-jsonl`) are huge, gitignored and must never be committed or read whole; parse them selectively with `jq` or Python. `build/` and `simulation_summary_*.json` are gitignored too.
- **Workflow:** TDD for simulation and rules changes; planning artifacts live in `.planning/` and work starts through a GSD command.
