# Phase 7: Session Flow & Handoff - Research

**Researched:** 2026-11-02
**Domain:** Python print pipeline (Jinja2 → LuaLaTeX) extension, config/validator extension, repo archive move, documentation rewrite, manual dry run
**Confidence:** HIGH for repo facts (all read or run in this session), MEDIUM for layout/page-fit estimates, LOW only where tagged `[ASSUMED]`

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Session schedule (FLOW-02)**
- **D-01:** The schedule is a page in the facilitator booklet (`spielleitung-uebersicht.pdf`), not a separate PDF and not Markdown. The block durations live in `simulation_config.json` (new block, e.g. `session_schedule`), the block labels in `content/texte.toml`. The validator checks that the blocks add up to the stated total.
- **D-02:** Time frame of about 3h15 with two breaks, like MHP (14:55–18:10): Intro 10 · Pause 5 · Story + Gruppen 25 · Welle 0 15 · Maßnahmen + Budget 30 · Pause 15 · Welle 1 20 · Welle 2 20 · Welle 3 20 · Abschluss/Budget Review 10 · Debrief 20. The whiteboard write-up step is gone.
- **D-03:** Each change window is part of its wave's 20 minutes (events → attack → OPEX → change window). There are no separate window blocks.
- **D-04:** The page shows durations and cumulative minutes from the start, plus an empty clock-time column the facilitator fills in by hand. No start time in config.

**Dry run (FLOW-05)**
- **D-05:** The test run takes place on **2026-11-25**: a test group plays the full game (Welle 0, waves 1–3, closing, debrief), led by someone who did not write the rules and who uses only the material. The author watches without helping and times each block.
- **D-06:** Phase 7 ends with that run. Verification waits for it, and its findings become gap-closure plans in Phase 7. All other plans must be finished and printed before 2026-11-25.
- **D-07:** A generated one-page protocol template (`spielleitung-` prefix, e.g. `spielleitung-probelauf.pdf`). It lists the schedule blocks with their planned minutes from config (D-01) and has columns for actual time, questions or unclear points, and calculation errors.

**Debrief (FLOW-03)**
- **D-08:** The debrief is a section in the facilitator booklet (`spielleitung-uebersicht.pdf`), with texts under a new `texte.toml` key (e.g. `sheets.debrief`). There is no separate sheet and no player version.
- **D-09:** Fixed questions for each stage (reaction → description → analysis → application), plus prompts that use game data: compare teams by KZ, RoS and Final-Index; ask which clues could have been read (refers to the clue matrix); ask what the team would have done differently in a change window.
- **D-10:** The application stage includes transfer to real IT-security practice (e.g. "Which measure would you implement first in your company?", "Where do you make real CIA trade-offs?"). These are questions only, no new teaching content.
- **D-11:** 2–3 questions per stage, about 10 in total; the facilitator picks from them. A guide time per stage is printed, and those minutes add up to the debrief block from D-02.

**"Was ist neu" sheet (FLOW-04)**
- **D-12:** Generated PDF with the `spielleitung-` prefix (e.g. `spielleitung-was-ist-neu.pdf`). Prose in `texte.toml`, every number from config (X per 10k, k, Budget Review tiers, …), so the sheet stays correct after a future rebalance.
- **D-13:** Content: all four categories. Rule changes RULE-01..08 (Levelwechsel vs. Maßnahmentausch, Kurswechsel as one forced swap, downgrade, overspend −X per started 10k, Sparprogramm end check, RoS without event effects, Budget Review boundaries "ab", E-target bonus removed). Flow changes (no whiteboard, Welle 0, debrief, new schedule). New material (generated PDFs instead of docx/pptx, veiled attacks, clue matrix, team booklet with tracking page). Rebalance values as an old → new table.
- **D-14:** Old values come from a frozen MHP config committed as `content/mhp_baseline.json`. Only the "Was ist neu" builder reads it, never the rules, simulation or other builders. The table shows only the values that changed. Candidate source: config at commit `1cfb2fa` (2026-07-06, last config change before the September workshop). The planner or researcher must confirm it matches the MHP state.
- **D-15:** Strictly one page, enforced by a fill-report test as for the cards and the booklet. If space runs out, the priority is rules > flow > material > values: the values table shrinks first (only key values, or a summary line pointing to the cards and worksheets), and the rule changes always stay complete.

**Legacy archive (LEG-01)**
- **D-16:** Archive everything that `content/INVENTORY.md` marks as superseded: `Angriff-1/2/3_*.docx`, `Budget.docx`, `Return on Security und Final Wert.docx`, `Events_Security-Game.pptx`, `Massnahmenkarten_Security-Game.pptx`, `Unternehmenssteckbrief MechTech.docx`, `Zeitungsartikel.docx/.pdf/*.png`, `Anfrage-Mail.docx/.pdf`, `Audit-Mail.pdf`. Also archive `generate_attack_calculator.py`, `generate_from_template.py`, `generate_pptx_cards.py` and `pptx_output/`. These stay in `final_documents/`: the intro deck, the MHP company profile, the VWI talk deck and the two portraits.
- **D-17:** A test proves that the build and the package no longer reference anything under `archive/`. `tests/test_inventory.py` and `content/INVENTORY.md` are updated to the new locations, since they currently check 20 files in `final_documents/`.

**Intro deck & docs (LEG-02)**
- **D-18:** Claude edits the intro deck `Planspiel_Einführung + Grundlagen.pptx` with python-pptx, replacing run text so formatting survives. It first produces a checklist of every finding (slide → problem → proposed change). The user approves the list before any edit and reviews the result.
- **D-19:** Slide 36 ("Spielplan / Vorlage für die Pinnwand") is replaced by an overview of the new flow (Welle 0 → waves → debrief) with no attack names and no budget figure. "Beratungsteam aus 3–4 Personen" is changed to the project format.
- **D-20:** Language: README.md stays **German** (rulebook for German-speaking facilitators) and is updated in content. The root CLAUDE.md is rewritten in **English**. This is a deliberate exception to the global "docs in English" rule for the README.
- **D-21:** The CLAUDE.md print-sync section is rewritten. The manual `python-docx`/`python-pptx` trap for the Angriff docx files is gone; it now describes the `planspiel print` pipeline, `--check` and the order config → README → texte.toml → print.

**Requirements review (plan-phase, 2026-11-02)**
- **D-22:** The stated session total is **190 min** (3h10). The D-02 blocks add up to 190, and the MHP frame 14:55–18:10 leaves 5 min of buffer. The config holds every block duration plus the total, and the validator checks that the blocks sum to the total (D-01).
- **D-23:** The schedule page also has a direction column: each block gets one line saying what the facilitator does and what is handed out, with the prose in `texte.toml`. The page also carries a print list: which PDF, and how many copies per team and for the facilitator. The quantities live in config and are never typed into prose. Reason: no current moderation guide exists (the old one is in `archive/historical_docs/`), and a facilitator who did not write the rules has to prepare and run the session from the material alone.
- **D-24:** LEG-02 also covers `.claude/CLAUDE.md`. GSD generates it from `.planning/codebase/` (state of late September), so it still describes the old pipeline (M_sum, `sim_low.json`, old generators as live, "no tests") and it is loaded into every session. Bring the three source maps `.planning/codebase/STACK.md`, `CONVENTIONS.md` and `ARCHITECTURE.md` up to date, then regenerate `.claude/CLAUDE.md` with `gsd-tools generate-claude-md`.
- **D-25:** Pass rule for the dry run (the literal reading of ROADMAP success criterion 5): every wave block finishes within its planned minutes, the whole session finishes within the stated total (D-22), and the facilitator gets no help from the author. Each overrun, unclear point or calculation error recorded on the protocol (D-07) becomes a gap-closure item (D-06), unless the user explicitly accepts it at verification.
- **D-26:** (clarifies D-14) "MHP state" means what was printed and played at the MHP workshop. Check the config at `1cfb2fa` against the printed MHP material in `final_documents/`, which still carries the MHP numbers until LEG-01. Where the two disagree, `content/mhp_baseline.json` takes the printed value, and the difference is recorded in RESEARCH.md.

### Claude's Discretion
- What happens to `docs/folienkonzept_spielphasen_mechtech.md`, which still mentions the E-target check: update it or move it to `archive/`.
- The check of the MHP company profile deck and of the generated Audit-Mail and Steckbrief for outdated rules. The two story documents are generated now, so their checks run through `texte.toml` and the veil and text checks.
- The exact config key names, page layout and position of the schedule, debrief and "Was ist neu" pages inside the booklet.
- The guide minutes per debrief stage, as long as they add up to the debrief block.
- Whether the root wrappers `simulate_outcomes.py`, `analyze_simulation_results.py` and `balance_analysis.py` stay. They stay unless a reason to archive them turns up, because CLAUDE.md documents them as live entry points.

### Deferred Ideas (OUT OF SCOPE)
None. The discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FLOW-02 | Session schedule revised: whiteboard removed, wave 1 fits 20 min, 15–20 min debrief, total one afternoon | §Q4 config block `session_schedule`; §Q2 booklet page; schedule math (190 min) |
| FLOW-03 | Debrief question set (reaction → description → analysis → application) in the facilitator material | §Q8 key design; §Q2 placement; data already printed in booklet |
| FLOW-04 | "Was ist neu" sheet for facilitators who ran the MHP version | §Q1 baseline + old→new table; §Q7 content list; §Q3 new job |
| FLOW-05 | Timed dry run by someone who did not write the rules | §Q9 protocol design + plan list for 2026-11-25 |
| LEG-01 | Legacy docx/pptx, old generators, `pptx_output/`, Excel calculator moved to `archive/` | §Q5 complete reference list, test breakage list, proof test |
| LEG-02 | README.md and CLAUDE.md describe new pipeline and rules; hand-maintained docs checked | §Q6 (a)–(f), including tests that pin README phrases |
</phase_requirements>

## Summary

Everything this phase needs already exists as a pattern in the repo. A new top-level config block read by one module (`practice`) is the model for `session_schedule`; a one-page generated PDF with a fill-report test (`wave_page` / `welle.tex.j2` / `tests/test_wave_page_pdf.py`) is the model for "Was ist neu" and the dry-run protocol; the `clues.toml` pattern (separate content file, in `stamp.DATA_INPUTS`/`BUILD_INPUTS`, loaded in `cli._print_command`, passed to exactly one builder) is the model for `content/mhp_baseline.json`. No new third-party package is needed. The fast suite is green today (2681 passed, 185 deselected, 180 s; `uv run planspiel print --check` reports "Druckmaterial aktuell").

The MHP baseline question is resolved: the printed MHP material in `final_documents/` agrees with the config at `1cfb2fa` on every number I could compare (30 measure cards, 3 attack worksheets, Budget.docx, 9 event slides), with exactly one numeric disagreement (Budget Review boundaries: print says "25.001–50.000", config used "≥ 25.000") and two non-numeric ones (Kurswechsel was a `noop` in the config but a forced swap with refund wording in print; E-target bonus/malus and `e_targets` exist only in the config). `1cfb2fa` is the last commit that touched `simulation_config.json` before the next one on 2026-09-30, and the printed files were last touched on 2026-07-06 (72f54b2). One thing to confirm with the user: the intro deck title slide, the commit dates and the auto date fields all say 06.07.2026 / July, while PROJECT.md and CONTEXT say the workshop was in September; this does not change the baseline.

Four findings the planner must not miss: (1) README.md and root CLAUDE.md are pinned by seven existing tests (exact phrases, one allowed "Maßnahmenwechsel", one "Gesamtkosten" line) so the LEG-02 rewrite must keep those anchors or change the tests in the same plan; (2) archiving the generators breaks four tests (`test_legacy_generators_smoke`, `test_texts_migration` reads `MEASURE_META` from the generators, `test_inventory` incl. a byte-identity test against `final_documents/Zeitungsartikel_bild_*.png`, `test_single_definition` docstring/exclusion, plus the `openpyxl` pin in `test_environment`); (3) the Exzellenz-Bonus card now reads "Je Maßnahme auf Level 2: KZ +3" but the rule counts measures **at or above** Level 2, which is ambiguous for players (Phase 6 changed it from Level 3), and the event cards say "Event: Nach Welle N" while the wave page makes events step 1 of the wave; (4) the intro deck is shorter on outdated rules than the CONTEXT assumed: it has no E-target, no "Maßnahmenwechsel", no −15 and no Budget Review boundaries; its real problems are slide 30 (3–4 Personen), 31 (20 min, 3 of 4 story documents), 32 (350.000 €), 26/33 (clock-time pauses), 28 (five phases) and the hidden slide 36 (150.000 €, wrong attack names).

**Primary recommendation:** Sequence plans as LEG-01 → FLOW-02 → FLOW-03 → FLOW-04 → FLOW-05a (protocol + the single print-set commit + physical-print checkpoint) → LEG-02 docs → FLOW-05b (2026-11-25 run) → gap-closure plans; give each of FLOW-02..05 and LEG-01 its own PLAN.md, split LEG-02 into README / CLAUDE.md-and-maps / intro-deck-checklist / intro-deck-edit plans.

## Project Constraints (from CLAUDE.md)

Sources: `./CLAUDE.md` (German, root), `./.claude/CLAUDE.md` (generated, partly outdated per D-24), global `~/.claude/CLAUDE.md`.

- Python only via `uv run ...`; never the `python` on PATH (Inkscape's). Tests: `uv run pytest` (fast), `-m slow` (full enumeration), `-m pdf` (LuaLaTeX via MiKTeX), `-m balance`.
- No fixed numbers in prose; every number from `simulation_config.json`; order of change config → README → texte.toml → print. Prose in config is a validator error.
- Hand-calculability is a hard design criterion (not relevant to this phase's content, but no new formulas).
- TDD for features; run verification before claiming done; conventional commits in English; no `--no-verify`; no force-push to main; prefer new commits.
- One requirement = one PLAN.md; review requirements for gaps before planning (this research lists gaps in §Open Questions).
- Do **not** run the slow checks (`-m slow`, `-m balance`, `balance_analysis.py --layers all`, `planspiel gate --paths`); none of them is needed for Phase 7 (no rule or number change).
- GSD workflow enforcement: file edits go through a GSD command.
- Questions to the user in German (memory), docs and code in English; README stays German (D-20).
- `.claude/CLAUDE.md` says "trust code and root CLAUDE.md over its Technology Stack/Conventions/Architecture sections" (D-24).

## Architectural Responsibility Map

This is a batch tool, not a web app; "tiers" are the repo's layers.

| Capability | Primary layer | Secondary layer | Rationale |
|------------|--------------|-----------------|-----------|
| Block durations, total, debrief stage minutes, print-list quantities | `simulation_config.json` block (+ `Config` field, validator) | — | Numbers only in config (D-01, D-23); read only by the booklet and protocol builders |
| Block labels, direction lines, debrief questions, "Was ist neu" prose | `content/texte.toml` (+ key tuples in `planspiel/texts.py`) | — | Prose only in texte.toml; coverage/digit lint apply |
| Old (MHP) values | `content/mhp_baseline.json` | `planspiel/was_neu.py` (only reader) | D-14 isolation |
| Cumulative minutes, clock column, change rows | print model (`planspiel/master.py`, new `was_neu.py`, `probelauf.py`) | `planspiel/fmt.py` | Models format; templates only loop |
| Layout, page fit | `print/templates/*.tex.j2`, `print/planspiel.sty` (`\fillreport`) | tests parse the TeX log | Fill report is the page-fit proof |
| Audience / veil | `planspiel/audience.py` (job prefix), `planspiel/veil.py` | new name-hit tests | `spielleitung-` is unscanned by design |
| Stamp / freshness | `planspiel/stamp.py`, `final_documents/generated/manifest.json` | `uv run planspiel print --check` | New input file must be added to `DATA_INPUTS`/`BUILD_INPUTS` |
| Archive move | git (`git mv`) + tests | `content/INVENTORY.md` | History-preserving, test-proven |
| Docs | README.md (German), CLAUDE.md (English), `.planning/codebase/*` → `.claude/CLAUDE.md` | tests that pin phrases | Order config → README → texte.toml → print |
| Intro deck | manual file edited with python-pptx | user approval gate | Out of scope for regeneration (PROJECT.md) |
| Dry run | human event 2026-11-25 + printed protocol | `.planning/phases/07-*/07-DRYRUN.md` (recommended record) | Cannot be automated |

## Standard Stack

### Core (all already in the repo; no new packages)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12 (uv-managed) | all code | `pyproject.toml` `requires-python >=3.12` [VERIFIED: pyproject.toml] |
| jinja2 | 3.1.6 | `.tex.j2` rendering, `finalize=tex_escape` | pinned [VERIFIED: pyproject.toml] |
| LuaLaTeX (MiKTeX) | LuaHBTeX 1.25.7, MiKTeX 26.5 | PDF build | `lualatex --version` run in this session [VERIFIED] |
| pytest | 9.1.1 | tests, markers `slow`/`pdf`/`balance` | pinned [VERIFIED: pyproject.toml] |
| pypdf | 6.19.0 (dev) | PDF text/page tests | pinned [VERIFIED: pyproject.toml] |
| python-pptx | 1.0.2 | intro-deck edit (D-18) | already a dependency; keep it [VERIFIED: pyproject.toml] |
| openpyxl | 3.1.5 | only used by `generate_attack_calculator.py` | becomes unused after LEG-01; see §Q5 for the drop decision |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| New `planspiel/was_neu.py` + separate PDF | extra pages in `master.py` | D-12 says separate PDF; a separate model keeps the booklet's page-by-page tests stable |
| `balance.config_diff` on raw configs for "Was ist neu" | curated row registry | Raw diff misreports Budget Review (tier rows shift by index) and cannot express meaning changes; use the registry (see §Q1) |
| python-docx | — | not needed; docx files are archived, not edited |

**Installation:** none. `uv sync` is enough.

## Package Legitimacy Audit

This phase installs no external package. All dependencies are already pinned in `pyproject.toml`/`uv.lock` (jinja2, openpyxl, python-pptx, pypdf, pytest). The only dependency change considered is **removing** `openpyxl` (see §Q5). No `package-legitimacy` run is needed.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| (none new) | — | — | — | — | — | — |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
simulation_config.json ──load_config──▶ Config(+session_schedule)  ──validate (sum==total, ids, waves)
        │                                    │
content/texte.toml ──load_content──▶ Texts ──┤  coverage/digit lint (planspiel texts, also at print time)
content/clues.toml ──load_clues────▶ clues ──┤
content/mhp_baseline.json ─load (cli)─▶ baseline ──▶ ONLY was_neu builder
                                             ▼
                      render.render_all(cfg, texts, templates, clues, baseline)
            ┌──────────────┬───────────────┬───────────────────┬───────────────────┐
            ▼              ▼               ▼                   ▼                   ▼
   master.py (booklet) was_neu.py     probelauf.py      (existing builders)   audience.audience_of(job)
   + schedule page     spielleitung-  spielleitung-                            (prefix required)
   + print list        was-ist-neu    probelauf
   + debrief page
            └────────── .tex strings ({job: tex}) ───────────────┘
                                │ veil.scan_documents (spielleitung- = unscanned, file name checked)
                                │ stamp.compute_stamp (content hash + git date + "+lokal" if dirty)
                                ▼
                texbuild.build_documents (LuaLaTeX, bounded, aux-stable)
                                ▼
          final_documents/generated/*.pdf + manifest.json  ──▶ planspiel print --check (no TeX needed)
```

### Recommended Project Structure (delta only)
```
planspiel/was_neu.py            # model: rule rows, flow/material rows, diff-driven value rows
planspiel/probelauf.py          # model: protocol rows from session_schedule
planspiel/schedule.py (optional)# small shared helper: blocks → rows with cumulative minutes (used by master + probelauf)
print/templates/was_neu.tex.j2, probelauf.tex.j2
content/mhp_baseline.json       # frozen old values (D-14)
archive/mhp_print_material/     # 15 moved files (name is discretionary)
archive/legacy_generators/      # 3 scripts, pptx_output/, angriff_berechnung.xlsx
tests/test_session_schedule_config.py, test_schedule_model.py, test_debrief_model.py,
tests/test_was_neu_model.py, test_was_neu_pdf.py, test_probelauf_model.py, test_probelauf_pdf.py,
tests/test_no_archive_references.py, test_baseline_isolation.py
```

### Pattern 1: optional top-level config block read by one module (model: `practice`)
**What:** `Config` gets `session_schedule: Optional[SessionSchedule] = None`; `load_config` builds it only if the key is present (as for `practice`, `planspiel/config.py:216-243`); `validate.py` calls `check_session_schedule` only `if "session_schedule" in raw` (as `check_practice`, `planspiel/validate.py:228-231`). The validator does **not** reject unknown top-level keys (it only requires `budget_tiers`, `waves`, `attacks`, `measures`, `default_budget_tier`, `final_index`) [VERIFIED: validate.py:197-231], so the block is silently accepted until the check exists.
**Invisibility proof:** copy `tests/test_practice_config.py::test_the_block_never_reaches_the_real_config_fields` (lines 105-119: delete the key, `load_config`, compare all real fields, `dataclasses.replace(cfg, session_schedule=None) == plain`) and `test_evaluation_and_kernel_ignore_the_block`.
**Mini config:** builders must return `{}` when `cfg.session_schedule is None` (as `render.master_sheet` returns `{}` without `reference_plans`, `render.py:129-135`), because `tests/fixtures/mini_config.json` + `mini_content/` are rendered by several tests (`test_veil_audience.py::test_every_rendered_job_has_an_audience`, `test_booklet_*`, `test_cards_*`) and carry no such block.

### Pattern 2: separate content file passed to exactly one builder (model: `clues.toml`)
`cli._print_command` loads `clues` (`cli.py:262-263`), `render_all(..., clues=clues)` passes it to every builder as 4th arg, "only the master sheet reads the clues" (`render.py:154`). Do the same with a `baseline` argument; `stamp.DATA_INPUTS`/`BUILD_INPUTS` list `content/clues.toml` and `tests/test_print_stamp.py:137-138` pins that. Add `content/mhp_baseline.json` to both tuples and pin it the same way, otherwise an uncommitted baseline edit would not mark the print "+lokal" and would not move the stamp date.

### Pattern 3: one-page generated PDF with fill proof (model: `wave_page.py`, `welle.tex.j2`, `tests/test_wave_page_pdf.py`)
`\fillreport{1}` at the end prints `PLANSPIEL-FILL page=1 used=… text=…` into the log (`print/planspiel.sty:144`); the test asserts `len(pages)==1`, exactly one report and `used <= text` (`test_wave_page_pdf.py:37,47,89-90`; in `test_master_pdf.py:162-169` the check is `len(reports)==len(pages)` and `used<=text` per page). A page that overflows breaks to a second page, so `len(pages)==1` fails: that is the enforcement of D-15.

### Pattern 4: new document job
1. Builder function `(cfg, texts, env, clues[, baseline])` returning `{job: tex}`; append to `render.DOCUMENT_BUILDERS` (`render.py:156`).
2. Job name must match `^[a-z0-9][a-z0-9_-]*$` (`texbuild.JOB_NAME`) and start with a prefix (`audience.PREFIXES`); `render_all` calls `check_job_name` and `audience_of` and rejects duplicates (`render.py:166-171`). `spielleitung-` → `FACILITATOR`, `scan_profile` returns `None`.
3. Veil: `veil.scan_documents` scans nothing for facilitator jobs except the file name (`veil.py:248-262`).
4. Stamp/manifest: automatic (`stamp.write_manifest`); `planspiel print --check` reports `STALE` until the new PDFs are built and committed.
5. Preflight keeps MiKTeX package probes in `texbuild.TEX_PROBES`; new templates must not use packages outside that list (otherwise add the probe and `print/miktex-packages.txt`).

### Anti-Patterns to Avoid
- **Typing numbers in `texte.toml`.** `check_digits` rejects any digit outside `story.*` unless allowlisted (`texts.py:380-390`), and there are no `{param}` placeholders (header of `texte.toml`, line 6). Compose "label + generated value" in the model (e.g. rule row: prose cell + number string from `fmt`), never write "3 KZ" in prose. The same applies to the debrief text ("Final-Index", "RoS" without numbers) and to the direction column.
- **Reading the baseline anywhere else.** No `Config` field, no `load_config` branch, no parameter on any other builder.
- **Attack names in new facilitator prose or block labels.** Use "Welle N" in schedule labels and "Welle N" (not attack names) in "Was ist neu" value rows. The booklet already names the attacks, but a schedule or "Was ist neu" sheet lies on the table.
- **Committing generated PDFs from several plans.** The stamp date is the last commit touching the data inputs; a PDF built before the last input commit is stale. One plan writes the print set (precedent 05-16, 06-10).
- **Putting wave titles on the schedule page.** `tests/test_master_pdf.py::_section_pages` finds each wave section by searching its title from page index 1 on (`test_master_pdf.py:57-60`); a schedule page that contains the revealed wave titles would be found first and break the test.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Old → new value comparison | ad-hoc string diff | a row registry over `Config` + baseline with `fmt.format_money/format_signed`; reuse `balance.config_diff` only for a provenance test, not for rendering | raw diff misreports `final_events[0].tiers` (rows shift by index) |
| Budget Review boundary and overspend text | new wording | `review_text.boundary_text`, `penalty_rows`, `rules.penalty_params`, `rules.budget_review_delta` | single definition, already tested |
| One-page proof | manual page-count reasoning | `\fillreport` + `FILL` regex in `tests/support/pdf_text.py` | exact log measurement |
| PDF text assertions | raw pypdf text | `squash`/`squashed_pages` helpers (pypdf drops word spaces) | known quirk |
| Legacy MHP-state check | re-reading docx by hand each time | the stdlib `zipfile`+`xml.etree` extraction used in this research (python-docx is not a dependency) | no new dependency |
| Archive move | copy + delete | `git mv` (rename history preserved) | audit trail |
| `.claude/CLAUDE.md` | hand edit | fix the three `.planning/codebase/*.md` sources, then `gsd-tools generate-claude-md` | generator owns the marked sections |
| Intro-deck edits | rebuild the deck | python-pptx run-level edits (below) | MHP branding stays manual |

**Key insight:** every artefact this phase adds is a variation of something that already has tests; copy the test shape first (TDD), then the implementation.

## Q1. MHP baseline (D-14, D-26)

### Does `1cfb2fa` represent the MHP state?
**Yes, with the exceptions below.** [VERIFIED: `git log -- simulation_config.json`, `git show 1cfb2fa:simulation_config.json`, extraction of the docx/pptx XML via `zipfile`, scripted comparison in this session]
- Config history: `1cfb2fa` (2026-07-06, "KZ-Startwerte pro Budget-Tier neu balanciert (50/42/34)") is followed by `4858642` (2026-09-30, umlauts only, Phase 1) and `7d3f239` (2026-10-02, Phase 2). Nothing touched the config between 2026-07-06 and 2026-09-30.
- Printed material last touched: `72f54b2` (2026-07-06, "farbige level und welle": Angriff-1/2/3, Events, Massnahmenkarten); Budget.docx and RoS docx earlier. Nothing in `final_documents/` was modified between 2026-07-09 and the Phase 3 era.
- **Date caveat (confirm with user):** the intro deck title slide says "06.07.2026", `docProps/core.xml` `modified` is `2026-07-06T14:29Z`, and all MHP print files date from 2026-07-03..06, whereas PROJECT.md/CONTEXT say the workshop was in September (2026-09). The slide footers are auto date fields (`type="datetime1"`), so only the title slide date is real text. This does not change the baseline (no config or print change after 2026-07-09), but the workshop date in PROJECT.md may be wrong.

### Comparison results (printed value wins, D-26)
| Item | Printed MHP | Config at `1cfb2fa` | Agreement |
|------|-------------|---------------------|-----------|
| 30 measure cards (CIA, Init, OPEX, dependency lines) | `Massnahmenkarten_Security-Game.pptx` | `measures.*.levels` | all 30 agree (script compared every card); dependencies M1 L3 / M3 L3 need M2 ≥ L2, M7 L3 needs M2 ≥ L1 agree |
| Card description text M6 L3 (slide 18), M10 L1 (slide 28) show M2 text | known (INVENTORY) | n/a | numbers right, text wrong; not relevant to values |
| Attack 1: thresholds/caps | Fall 1 ≤ 23, Fall 2 ≥ 31, damage 160.000 €, KZ −6/+10, slope `(GR−23)*2−6`; bonuses M3 +6, M4 +6, M6 +3 (from level 2) | `e_threshold 23`, cap 8, 8×20, −6/+10, same bonuses | agrees |
| Attack 2 | ≤ 20, ≥ 30, 320.000 €, KZ −5/+7, slope 1,2; M5 +9, M7 +6 | 20, cap 10, 10×32, −5/+7 | agrees |
| Attack 3 | ≤ 25, ≥ 32, 140.000 €, KZ −7/+10, slope `/7*17`; M1 +8, M2 +6, M8 +9 | 25, cap 7, 7×20, −7/+10 | agrees |
| Budget.docx tiers | Low 350.000 / KZ 50, Medium 400.000 / 42, High 450.000 / 34 | `budget_tiers` | agrees |
| Events pptx numbers | Operative Unterstützung −2.000 € je Maßnahme; Sparprogramm −20.000 €; OEM-Audit −15/−5/±0/±0/+5/+15; Kritische Schwachstelle −5/±0/+3/+7; Exzellenz +5 je Maßnahme auf Level 3; Nervige Authentifizierung −10 | same values | agrees |
| Budget Review | "< 0 → −15; 0–25.000 → ±0; **25.001**–50.000 → +5; **50.001**–75.000 → +10; ≥ **75.001** → +15" | tiers `[[-100000,-15],[0,0],[25,5],[50,10],[75,15]]` evaluated with **≥** (CR-01) | **disagrees on boundary semantics** → baseline takes the printed "strictly above" boundaries |
| Kurswechsel | printed: forced "Maßnahmenwechsel", difference "gezahlt oder erstattet" | event type `noop` (the simulation ignored it) | **disagrees** (text row only, not a number) |
| E-targets (15/17/19 per tier), per-wave `kz_bonus`/`kz_malus` (5/−3, 7/−5, 10/−7) | not printed anywhere | present | config-only; excluded from the baseline (RULE-08) |
| Budget.docx Init column | "Einmal zu Spielbeginn", yet the later paragraph says Init is also due on upgrade | sim: Init only at start | internal contradiction in print; no number |
| RoS docx | Gesamtkosten = Init + OPEX + **Summe Event-Strafen**; avoided damage `620.000 − …` | event OPEX added to total cost | agrees (this is the rule RULE-06 removed) |
| Final-Index | not printed (docx title only) | analysis script only (`--weight-ros`) | MHP had no printed Final-Index |

### Schema mapping old → current keys
| Old key (1cfb2fa) | Current key | Note |
|-------------------|-------------|------|
| `budget_tiers.*.budget / kz_start / severity_multiplier` | same | |
| `budget_tiers.*.e_targets` | removed | RULE-08 |
| `waves[].name`, `bonus_measures[].description`, `attacks.*.description`, `events.*[].description`, `final_events[].description` | `content/texte.toml` | prose left config (validator error now) |
| `waves[].kz_bonus / kz_malus` | removed | RULE-08 |
| `waves[].e_threshold`, `weights`, `bonus_measures[].bonus/min_level` | same | |
| `attacks.*.{base_severity,s_unit,kz_at_full_damage,kz_at_full_mitigation,cia_impact,mitigation_cap,allow_recovery}` | same | |
| `events.wave_1[0].type: "noop"` | `"kurswechsel"` | RULE-01 |
| `final_events[0].tiers [[-100000,-15],[0,0],[25,5],[50,10],[75,15]]` | `tiers [[0,0],[25,9],[50,18],[75,27]]` + `overspend_penalty {kz_per_step:3, step:10}` | tier rows shift by index; flat −15 became a linear penalty |
| (absent) | `final_index {weight_kz:1, weight_ros:10}`, `practice`, `reference_plans`, `reference_strategies`, `session_schedule` (new) | |

### Old → new values for "Was ist neu" (current `simulation_config.json`)
| Group | MHP (printed) | Now |
|-------|---------------|-----|
| Budget Low / Medium / High | 350.000 / 400.000 / 450.000 € | 370.000 / 390.000 / 405.000 € |
| KZ-Start Low / Medium / High | 50 / 42 / 34 | 39 / 36 / 33 |
| Schwelle Welle 1 / 2 / 3 | 23 / 20 / 25 | 22 / 20 (unchanged) / 24 |
| Printed Fall-2 bound (Schwelle + Kappung) Welle 1 / 3 | 31 / 32 | 30 / 31 (derived) |
| Boni Welle 1 | M3 +6, M4 +6, M6 +3 | M3 +6 (same), M4 +5, M6 +4 |
| Boni Welle 2 | M5 +9, M7 +6 | M5 +9 (same), M7 +3 |
| Boni Welle 3 | M1 +8, M2 +6, M8 +9 | M1 +4, M2 +6 (same), M8 +3 |
| KZ bei vollem Schaden / voller Abwehr Welle 1 | −6 / +10 | −8 / +8 |
| Welle 2 | −5 / +7 | −6 / +8 |
| Welle 3 | −7 / +10 | −6 / +8 |
| M6 Init L1/L2/L3 (k€) | 10 / 24 / 40 | 16 / 30 / 46 |
| M7 CIA L1 (C/I/A) | 2/3/2 | 0/1/0 |
| M7 CIA L2 | 4/5/3 | 2/3/1 |
| M7 CIA L3 | 6/7/4 | 4/5/2 |
| OEM-Audit, 0..5 erfüllt | −15, −5, ±0, ±0, +5, +15 | −2, −1, ±0, +1, +2, +3 |
| Kritische Schwachstelle, M7 L0..L3 | −5, ±0, +3, +7 | −3, ±0, ±0, +4 |
| Nervige Authentifizierung | −10 | −6 |
| Exzellenz-Bonus | +5 je Maßnahme auf Level 3 | +3 je Maßnahme ab Level 2 (**meaning changed**) |
| Budget Review, Restbudget ≥ 0 | +5 / +10 / +15 ab 25.001 / 50.001 / 75.001 € | +9 / +18 / +27 ab 25.000 / 50.000 / 75.000 € |
| Budget Review, Restbudget < 0 | pauschal −15 | −3 KZ je angefangene 10.000 € (**meaning changed**) |

Unchanged (do not list): attack base severity, s_unit, caps, CIA impact, damage 160.000/320.000/140.000 €, recovery factors 0,9/0,7/0,5, Sparprogramm −20.000 €, Operative Unterstützung −2.000 €, all other measure costs/CIA/dependencies, base CIA 10, base losses 620.000 €.

**Not 1:1 comparable (mark in the sheet):** Budget Review (linear penalty, "ab" boundaries), Exzellenz-Bonus (level condition), RoS (own spend only, so MHP RoS numbers are not comparable), Kurswechsel (forced swap, customer covers Init up to the dropped measure, no refund), KZ per wave rounded once (new), Final-Index (new; MHP printed none). About 21 changed value rows result.

### Recommended structure of `content/mhp_baseline.json`
Curated, current-schema-named, numbers only (no prose), full set of rebalance-able parameters so a future rebalance changes the sheet automatically; unchanged values simply drop out of the diff.
```json
{
  "schema": 1,
  "source": {"config_commit": "1cfb2fa", "printed_files_last_changed": "72f54b2",
             "printed_overrides": ["budget_review.boundary = above (print: 25.001, config: >= 25.000)"]},
  "budget_tiers": {"low": {"budget": 350, "kz_start": 50}, "medium": {"budget": 400, "kz_start": 42}, "high": {"budget": 450, "kz_start": 34}},
  "waves": {"1": {"e_threshold": 23, "bonus": {"M3": 6, "M4": 6, "M6": 3}}, "2": {"e_threshold": 20, "bonus": {"M5": 9, "M7": 6}}, "3": {"e_threshold": 25, "bonus": {"M1": 8, "M2": 6, "M8": 9}}},
  "attacks": {"ransomware": {"kz_at_full_damage": -6, "kz_at_full_mitigation": 10, "mitigation_cap": 8, "base_severity": 8, "s_unit": 20}},
  "measures": {"M6": {"init": [10, 24, 40]}, "M7": {"cia": [[2,3,2],[4,5,3],[6,7,4]]}},
  "events": {"oem_audit": {"tiers": [-15,-5,0,0,5,15]}, "kritische_schwachstelle": {"tiers": [-5,0,3,7]},
             "exzellenz_bonus": {"level": 3, "kz_per_measure": 5}, "nervige_authentifizierung": {"kz_delta": -10}},
  "budget_review": {"boundary": "above", "tiers": [[0,0],[25,5],[50,10],[75,15]], "overspend": {"kind": "flat", "kz": -15}}
}
```
Include all 10 measures and all three attacks in the real file (shown shortened). Keys are attack ids and measure ids; rendered rows use "Welle N" and `measures.<id>.name`, never attack names.

**Builder mechanics:** a registry of rows `(group_key, label_key, old_text, new_text)`; each extractor reads the baseline and the `Config` (via `fmt`, `review_text`, `rules.penalty_params`), and emits a row only if old ≠ new. Meaning-changed rows always emit (flagged). Row count is capped by a model test (proxy for the one-page proof).

**Isolation (model: `tests/test_practice_config.py` 102-135):**
1. AST/grep test: the string `mhp_baseline` occurs only in `planspiel/was_neu.py`, the one loader line in `planspiel/cli.py` (or inside `was_neu.py` if the loader lives there), `planspiel/stamp.py` (input lists) and tests.
2. `Config` has no baseline field; `rules`, `enumerate`, `simulate`, `gate`, `balance`, other builders never import `was_neu`.
3. The file is loaded by a fixed constant name (like `texbuild.ASSET_FILES`: "no content string ever chooses a file name").
4. Provenance test: `git show 1cfb2fa:simulation_config.json` mapped through the schema table equals the baseline, except the single listed override; skip when the commit is not available (shallow clone). `tests/support/gitrepo.py` exists for git-based tests.
5. `.gitattributes`: add `content/*.json text eol=lf` (current rule covers only `content/*.toml`).

## Q2. Facilitator booklet (`spielleitung-uebersicht.pdf`)

**Build chain:** `render.master_sheet` → `master.build_master_sheet(cfg, texts, clues)` (`master.py:453`) → dataclass `MasterSheet` → `print/templates/master.tex.j2` → job `spielleitung-uebersicht` (`MASTER_JOB`, `master.py:23`). The model holds only formatted strings; the template only loops (header comment of the template). `MasterSheet.printed_fragments()` feeds `test_every_model_fragment_is_in_the_pdf_text`, so any new string field is automatically asserted in the PDF.

**Current structure (12 pages, from `final_documents/generated/spielleitung-uebersicht.pdf` and the build log):** p1 cover (notice, intro, GR legend, contents, how-to, reference paths; 473 pt of 731 pt used) · pp2–7 per wave two pages (parameters + bonus table + check rows; event schedule + answer keys) · p8 Budget Review + final results + Final-Index weight · p9 Welle 0 key · pp10–12 clue matrix (one page per attack). Each page ends with `\pagereport`; fill used/text height in pt: 473/522/540/505/690/502/560/451/429/488/347/483 of 731.2 [VERIFIED: `build/print/spielleitung-uebersicht.log`, may be from the last build].
**Page-count constraint:** none found. No test asserts a multiple of 4; Phase 5 D-07 makes single-sided printing the default (`05-CONTEXT.md:71`). 12 is a coincidence.
**Page-fit tests:** `test_every_page_fits_the_text_height_as_measured_in_the_log` (one fill report per page, `used ≤ text`), no overfull box in the log, stamp on every page, `printed_fragments` all present (`tests/test_master_pdf.py`).

**Where to add**
- (a) **Schedule + print list: new page(s) directly after page 1** (before the waves). Page 1 has about 91 mm free, which is not enough for 11 rows with a direction column plus a print list. Plan for two pages: "Ablauf" (11 rows: label, minutes, cumulative minutes, empty clock cell, direction) and "Druckliste" (one row per PDF: label, copies per team, copies for the facilitator); let the fill report decide whether both fit on one. Add both to the contents list on page 1. Keep wave titles off these pages (see Anti-Patterns).
- (b) **Debrief: one page after the p8 "Endergebnis" page, before the Welle 0 key and the clue matrix.** It follows the numbers it refers to and precedes the clue matrix it points to. Expected page count 14–15.
- Existing tests to adapt when pages move: `_section_pages` (start search from index 1 is fine for pages inserted before the waves), `test_the_budget_review_the_final_table_and_welle_zero_follow_the_waves` takes `tail = pages[review:]` and expects welle0 in that tail: a debrief page inserted between p8 and p9 stays inside the tail, so these tests keep passing; only an insertion *before* `review` that contains `sheet.review.intro` would break them.

**Existing `[sheets.spielleitung]` in `content/texte.toml` (lines 481–575):** `title, notice, intro, gr_legend, contents_title, how_to_title, how_to (list of 3), paths_title/intro/start/window/swap, params_*, param_*, recovery_*, bonus_*, check_*, events_*, kind_*, keys_*, key_* (21 row labels), review_intro/x/step, final_*, final_index_note, welle0_*, clues_*, clue_head_*, clue_section_*`. All listed in `texts.py::_SPIELLEITUNG_KEYS` (line 80); adding a key to the TOML without adding it to a tuple is an `orphan_key` error, and a tuple entry without a TOML key is a `missing_key` error.

## Q3. Print pipeline for new jobs

- **Add a job:** Pattern 4 above. `spielleitung-was-ist-neu` and `spielleitung-probelauf` are valid job names and need no change in `audience.py`.
- **Veil:** `audience.scan_profile` returns `None` for `spielleitung-`, so the documents' text is not scanned; only the file name is (`veil.scan_documents`). `was ist neu` and the protocol are read at the facilitator table, so add a model-level test that none of their strings contains an attack name (`veil.name_hits(text, ctx, audience.PROFILE_NAMES)`, `veil.py:259`). `sheets.*` keys are not covered by `check_giveaway` (it scans `attacks.*.veiled`, `events`, `final_events`, `story`, `practice`; `texts.py:452-453`), so the new debrief/schedule/baseline prose needs its own test.
- **Stamp:** `Stand <date> · <7-char hash>[+lokal]`; hash over rendered `.tex`, `print/planspiel.sty`, images (`stamp.content_hash`); date = last commit touching `DATA_INPUTS` (config, texte, clues, images, `.sty`, templates); `+lokal` if `BUILD_INPUTS` (adds `print`, `planspiel`, `pyproject.toml`, `uv.lock`) are dirty or non-default paths are used (`stamp.py:22-41,141-166`). `planspiel/` is a build input: **every code change must be committed before the final print**.
- **Reproducibility:** `texbuild.run_lualatex` loops until the `.aux` is stable (max 3 passes), `SOURCE_DATE_EPOCH=0`; the session fixture `printed_set` builds the set twice and tests compare.
- **Commit the print set:** (1) commit all inputs; (2) `uv run planspiel print` (needs MiKTeX; builds to `build/print`, copies to `final_documents/generated/`, rewrites `manifest.json`, removes only PDFs the previous manifest listed); (3) `uv run planspiel print --check` must exit 0 (works without TeX, verified now: "Druckmaterial aktuell: Stand 2026-11-01 · 84b7976 (13 Dokument(e))"); (4) commit `final_documents/generated/`. Precedent: 05-16 carried PRINT-10, 06-10 carried BAL-05.
- **Tests that pin the print set by name:** none (grep). `tests/test_print_check.py` uses "Anfrage-Mail.pdf" only as a hand-placed fake file in a temp dir.

## Q4. Config block, validator, texts

**Recommended shape** (key names are discretionary):
```json
"session_schedule": {
  "total_minutes": 190,
  "blocks": [
    {"id": "intro", "minutes": 10}, {"id": "break_1", "minutes": 5}, {"id": "story_groups", "minutes": 25},
    {"id": "wave_0", "minutes": 15}, {"id": "measures_budget", "minutes": 30}, {"id": "break_2", "minutes": 15},
    {"id": "wave_1", "minutes": 20}, {"id": "wave_2", "minutes": 20}, {"id": "wave_3", "minutes": 20},
    {"id": "closing", "minutes": 10}, {"id": "debrief", "minutes": 20}
  ],
  "debrief_stages": [{"id": "reaction", "minutes": 3}, {"id": "description", "minutes": 4},
                     {"id": "analysis", "minutes": 8}, {"id": "application", "minutes": 5}],
  "print_list": [{"job": "spieler-teamheft", "per_team": 1, "facilitator": 1}]
}
```
The block sum is 10+5+25+15+30+15+20+20+20+10+20 = **190** [VERIFIED by arithmetic]; MHP frame 14:55–18:10 = 195 min, so 5 min buffer (D-22). Stage minutes above are a proposal that sums to the 20-minute block (discretionary).

**Validator (`check_session_schedule`, only when the key exists):** positive ints; unique ids; `sum(blocks) == total_minutes`; `sum(debrief_stages) == minutes of the "debrief" block`; wave blocks `wave_N` exist exactly for every `waves[].id`; `wave_0` iff `practice` is present; print-list `per_team`/`facilitator` are ints ≥ 0 and `job` names unique; no prose strings (ids only, snake_case). Keep product rules (wave 1 = 20, debrief 15–20, no whiteboard block, total 190) in a **test** (`tests/test_session_schedule_config.py`), not in the generic validator, so a future schedule change is a deliberate test edit (as with the pinned practice example).
**Print-list ↔ real jobs:** the validator cannot know job names; add a model/test check that every `print_list.job` is a key of `render.render_all(...)` and that every player/practice/attack document appears in the list. `angriff-*` jobs carry attack ids in their names (`angriff-1_ransomware`), facilitator-only page, fine.
**Team count:** not in config (grep). "Per team" columns need no team count. Add `teams` only if the debrief comparison table or a total column needs it (see Open Questions).
**Texte keys:** `required_keys(cfg)` (`texts.py:304`) is where config ids generate mandatory keys; extend it for `session_schedule`: `sheets.spielleitung.schedule.<block_id>.label` and `.direction`, `sheets.spielleitung.print_list.<job>` (label of the PDF), `sheets.debrief.stage_<stage_id>.*`. Static page labels go into a new tuple appended to `SHEET_KEYS` (e.g. `_SCHEDULE_KEYS`, `_DEBRIEF_KEYS`, `_WAS_NEU_KEYS`, `_PROBELAUF_KEYS`). Coverage check: `uv run planspiel texts` (0 errors today).
**Digit rules:** `check_digits` flags any numeric character outside `story.*`; allowlist entries (`content/digit_allowlist.toml`) are per key and token with a `why`, and an unused entry is itself an error. So: no "3–4", no "10 min", no "Level 2", no years in new prose. Keep the allowlist untouched.
**Mini fixtures:** `tests/fixtures/mini_content/texte.toml` carries almost no `sheets.spielleitung` keys; because builders return `{}` without the config block, no mini fixture change is needed. Do not add the block to `mini_config.json`.
**Print-list quantities:** the user decides them (see Open Questions); the proposal in `[ASSUMED]` form: story documents, Teamheft, measure cards, event cards, "So funktioniert eine Welle", Welle-0 sheet → per team; attack worksheets → per team and wave; booklet, "Was ist neu", protocol → facilitator only.

## Q5. LEG-01: every reference to the archived files

**Files to move (`git ls-files` confirms all are tracked, including `pptx_output/*` (6 files) and the root `angriff_berechnung.xlsx`):** 15 in `final_documents/` (3 Angriff docx, Budget, RoS docx, Events pptx, Massnahmenkarten pptx, Steckbrief docx, Zeitungsartikel docx/pdf/2 png, Anfrage-Mail docx/pdf, Audit-Mail pdf), 3 scripts, `pptx_output/`, `angriff_berechnung.xlsx`. Stay: intro deck, MHP profile, VWI deck, 2 portraits (5 files) and `final_documents/generated/`. 15 + 5 = the 20 files `test_inventory.py` pins.

**References found (grep over the repo excluding `.git`, `.planning`, `archive`, binaries):**
| Where | What | Action |
|-------|------|--------|
| `tests/test_inventory.py` | `FINAL_DOCUMENTS = final_documents`, `EXPECTED_FILES` (20), `test_pinned_file_set_equals_the_directory_listing`, `test_every_final_document_has_a_row_of_its_own`, `..._names_only_real_files`, **`test_newspaper_images_are_byte_identical_copies` (reads `final_documents/Zeitungsartikel_bild_*.png`)** | split `EXPECTED_FILES` into archived (in `archive/<dir>`) and kept (in `final_documents`); assert each location and that archived ones are absent from `final_documents`; replace the byte test by an md5 check against the values already recorded in `content/assets/README.md` |
| `content/INVENTORY.md` | header path, intro sentence "20 files in final_documents/", Audit-Mail row ("original stays in final_documents until LEG-01"), observations for LEG-02 on slide 36 | add a location column or section, update wording; keep row structure (the test parses 4 cells) |
| `tests/test_legacy_generators_smoke.py` | imports the three generators, asserts `angriff_berechnung.xlsx` unchanged | delete (its purpose ends) |
| `tests/test_texts_migration.py` | `_measure_meta("generate_pptx_cards.py")` / `("generate_from_template.py")` via AST at import time → the whole module fails on collection after the move | decide: retire the fidelity tests (migration is complete) or retarget `_measure_meta` to the archive path; the second keeps tests coupled to `archive/` (fine for tests, not for build/package). Keep the non-generator tests in that module (`ALLOWLIST_PINNED`, revealed names) |
| `tests/test_single_definition.py` | docstring "D-29 exception: generate_*.py excluded"; scans `planspiel/`, `tests/`, three root wrappers | update docstring; behaviour unchanged (no root `generate_*` scan exists) |
| `tests/test_environment.py::test_pinned_packages` | asserts `openpyxl==3.1.5` and `python-pptx==1.0.2` installed | if openpyxl is dropped, remove that line |
| `pyproject.toml` | deps `openpyxl==3.1.5`, `python-pptx==1.0.2`; `[tool.uv.build-backend] module-root="" module-name="planspiel"` (package contains only `planspiel/`; `archive/` is not packaged) | recommend: drop `openpyxl` (only the archived calculator used it), keep `python-pptx` (D-18); `uv lock` updates `uv.lock`; both are `BUILD_INPUTS` so commit before the final print |
| `.gitattributes` | no entry for the moved files (only `final_documents/generated/*`) | none |
| `README.md` | no mention of the generators or `pptx_output` (grep) | none beyond LEG-02 |
| root `CLAUDE.md` | lines 19, 24, 31, 54–56, 61 (final_documents as current source, `pptx_output/`, generators, print-sync trap) | rewritten in LEG-02 |
| `.claude/CLAUDE.md` | many lines (stack, architecture, conventions) | regenerated in LEG-02 |
| `content/assets/README.md` lines 24–27, `content/assets/GUIDELINES.md` line 3, 47 | "Copied from `final_documents/Zeitungsartikel_bild_*.png` … originals stay until LEG-01" | update to the archive location |
| `docs/folienkonzept_spielphasen_mechtech.md` | references the intro deck | see §Q6 (d) |
| `planspiel/rules.py:286,438` | docstrings mention `Angriff-1_Ransomware.docx`, `Events_Security-Game.pptx` | comments only; optional touch-up |
| `planspiel/story.py:240` | docstring "Anfrage-Mail, Audit-Mail" | refers to document kinds, not files; leave |
| `planspiel/cli.py:329,497` | `final_documents/generated` default out dir | **stays** (generated set remains there) |
| Root generators | `generate_from_template.py` reads/writes `pptx_output/`; `generate_pptx_cards.py` writes `pptx_output/`; `generate_attack_calculator.py` writes `angriff_berechnung.xlsx` (relative to cwd); none is imported by `planspiel/` | all move together; they will not run from `archive/` (they use `Path(__file__).parent`/cwd) and need no fixing |

**Generated documents reading assets from `final_documents/`: none.** The only images TeX reads are `content/assets/images/zeitungsartikel_bild_audit.png` and `..._fabrik.png` via `texbuild.ASSET_DIR`/`asset_paths` (fixed names), and these are byte copies already [VERIFIED: texbuild.py:35-38, grep of `planspiel/` and `print/` for `final_documents`: only `cli.py`]. Portraits are not used by any generated document.

**Tracking facts:** `pptx_output/` is tracked (6 files); `angriff_berechnung.xlsx` is tracked; `sim_low.json`, `sim_med.json`, `sim_high.json`, `simulation_summary*.json` are gitignored (untracked working files, not part of the move). `archive/` has 31 tracked files (`historical_docs`, `obsolete_docs_reference_sheets`, `obsolete_simulation_data_2026-01/README.md` etc.) plus 6.1 GB of untracked simulation dumps in `archive/obsolete_simulation_data_2026-01/` (ignored by pattern): do not run any bulk `git add archive`.

**Archive layout already in use:** `archive/historical_docs/`, `archive/obsolete_docs_reference_sheets/`, `archive/obsolete_simulation_data_2026-01/` (state/date-named folders with a README). Follow it: `archive/mhp_print_material_2026-07/` (15 files) and `archive/legacy_generators/` (3 scripts, `pptx_output/`, xlsx), each with a short README that says "MHP state at commit 1cfb2fa, not synchronised with the config, do not use".

**D-17 proof tests (recommended):**
1. Static: no file under `planspiel/`, `print/`, `pyproject.toml`, `.gitattributes`, the three root wrappers or `content/*.toml|json` contains `archive/`, `pptx_output`, `generate_pptx_cards`, `generate_from_template`, `generate_attack_calculator`, `angriff_berechnung`.
2. Dynamic (stronger): `sys.addaudithook` recording `open` events while `load_config`, `load_content`, `render.render_all`, `texbuild.asset_paths` and `stamp.compute_stamp` run; assert no opened path is under `archive/` or under `final_documents/` except the output directory. [ASSUMED: audit hook works with the pytest process; hooks cannot be removed, so gate the recorder with a flag]
3. Tree test: `git ls-files` contains no `pptx_output/` and no root `*.xlsx`, and `final_documents/` holds exactly the five kept files plus `generated/`.
4. Optional end-to-end: copy `simulation_config.json`, `content/`, `print/`, `planspiel/` to a temp dir without `archive/`/`final_documents/` and run `planspiel print --check`-equivalent model rendering there.

**Move discipline:** `git mv` per file (names contain umlauts and NFC/NFD matters on Windows; the inventory test already NFC-normalises names). Commit the move separately from content edits.

## Q6. LEG-02

### (a) README.md (German, 326 lines): outdated against current rules/pipeline
1. **"Deterministische Auflösung"** (formulas `M_sum`, `G = max(0, baseSeverity + Σ eventSeverityMods − M_sum)`, `Damage = G * sUnit * Π(damageFactors)`, `ΔKZ = −G * kzUnit * Π(kzFactors)`, CIA-Mali per step): the retired pre-2026-01 model. Replace by Gesamtreduktion, three cases, `reduktion_ueber_schwelle`, `severity`, linear KZ interpolation (the formulas are in root CLAUDE.md "Spielmechanik in Kürze", `planspiel/rules.py`).
2. **"Kernelemente"**: Maßnahmen attributes `mitigations`, `eventEffects`; Angriffe fields `kzUnit`, `mitigationRefs`, `targetCIA`; Wellen "Angriffe (Anzahl frei konfigurierbar)"; Events effect types (`severityMod`, `kzFactor`, `damageFactor`, `opexPenalty`).
3. **"Discovery (Hinweis-Logik)"**: Discovery-Signale with weight deltas, attack selection and severity mods are not implemented; discovery is reading the four story documents with the facilitator's clue matrix (`planspiel clues`), attacks veiled until they hit.
4. **"Spielablauf"**: no Welle 0, no schedule, the debrief is one line; add the session flow of FLOW-02 (numbers from config, so refer to the booklet page rather than typing minutes; the "no fixed numbers in README" rule).
5. **"Auswertungsvorlagen (2 Tabellen genügen)"** with `A1: G=…` rows and "Finale Kennzahlen": replaced by the generated team booklet (budget, tracking page, RoS and Budget Review).
6. **"Parametrisierung (ohne feste Zahlen)"**: lists `kzUnit`, "Mitigation-Cap", "KZ-Effekte je Budgetspanne"; update to the real parameter groups.
7. **Missing sections:** the `planspiel` CLI (`validate`, `texts`, `clues`, `gate`, `tausch`, `print`, `print --check`), the print pipeline, `content/texte.toml`/`clues.toml`/`digit_allowlist.toml`, the veil, Welle 0, Final-Index meaning for the debrief, KZ rounding is already there.
8. "Überholter Kartentext: Die MHP-Karte … gilt nicht mehr" (Kurswechsel section): the MHP card is archived, reword (but see pinned phrases).
9. Simulation section is current (`uv run` commands, tausch, gate). Keep.
**Pinned by tests (must survive the rewrite or be changed in the same plan):** `tests/test_budget_review.py:290-293` ("Budget Review und Überziehung", "angefangene", "overspend_penalty"); `test_budget_review_text.py:135-137` ("einschließlich", "boundary_text"); `test_kurswechsel.py:268-273` ("Levelwechsel", "Maßnahmentausch", "Begriffe: Levelwechsel und Maßnahmentausch", "Kurswechsel (Maßnahmentausch)", `count("Maßnahmenwechsel") == 1`); `test_paths.py:349-354` ("Netto-Änderung", "ab der nächsten Welle", "planspiel tausch"; forbids "Change-Gebühr", "Kommunikationseffekt", "Zwangs-Change"); `test_ros_ledger.py:158-163` (exactly one line starting with "Gesamtkosten", containing "Kurswechsel", without "Straf"); `test_sparprogramm.py:190-192` ("Sparprogramm", "am Ende noch überzogen"); `test_e_target_removed.py:173-180` (README must not contain "E-Ziel prüfen", "E-Ziel erreicht", "Angriff + E-Ziel"; root CLAUDE.md must not contain "E-Ziel-Check" or "Angriff + E-Ziel").

### (b) Root CLAUDE.md (62 lines, German → English)
Outdated: "Was ist das hier?" ("code does not serve the game, only content creation/balance"): it now also generates the print set; the "Repo-Struktur" block: `final_documents/` "einzige aktuelle Quelle" (now `final_documents/generated/` is the only game material; legacy archived), `pptx_output/` and the three generators as live; missing `planspiel/` package, `content/`, `print/`, `tests/`, `archive/` layout; the **Print-Sync-Falle** paragraph (Angriff docx edited by hand with python-docx; there is no generator) is wrong since Phase 4; "final_documents enthält teils generierte, teils direkt gepflegte Binärdateien"; "Die .md-Dokumente sind das Game-Design-Dokument" (the historical md are archived); the order "config → README → final_documents" must become config → README → `content/texte.toml` → `uv run planspiel print` → `print --check` → commit `final_documents/generated/`; the verification commands are fine but missing `uv run planspiel validate|texts|clues`, test markers (`pdf`, `slow`, `balance`) and "+lokal" stamp rule. "Spielmechanik in Kürze" is current (verified against `rules.py` notions); add Welle 0 and the veil. Constraint from `test_e_target_removed`: no "E-Ziel-Check"/"Angriff + E-Ziel".

### (c) `.claude/CLAUDE.md` and `gsd-tools generate-claude-md`
[VERIFIED: `~/.claude/gsd-core/bin/lib/profile-output.cjs` `cmdGenerateClaudeMd`, lines 975–1170, and `.planning/config.json` `claude_md_path: ./.claude/CLAUDE.md`]
- Managed sections between `<!-- GSD:<name>-start -->`/`-end -->` markers: `project` (from `.planning/PROJECT.md`: H1, "What This Is", "Core Value", "Constraints"), `stack` (`.planning/codebase/STACK.md`, fallback `research/STACK.md`), `conventions` (CONVENTIONS.md), `architecture` (ARCHITECTURE.md), `skills` (`.claude/skills` etc.), `workflow` (GSD defaults). A `profile` section (`<!-- GSD:profile-start -->`) is left alone.
- Without `--auto` it **overwrites** the content of every marked section, including manual edits; with `--auto` it skips sections whose body differs from the generated body (manual-edit detection). Text outside markers is preserved. A file without any GSD marker is skipped unless `--force`.
- It summarises sources (the stack generator keeps headings, table rows and bullets), so map files must be edited **in the summarised form** (short bullet lists).
- Commands: `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" generate-claude-md` (add `--auto` to protect manual edits; `--output` to write elsewhere for a diff first).
- **State of the maps:** `.planning/codebase/*.md` all carry `Analysis Date: 2026-06-23` (git: b1dfa40, 2026-06-23), not late September. Outdated: STACK ("no pyproject, no tests, no lockfile, Python 3.9+, scripts only, generators live, `sim_low.json` caches"), CONVENTIONS ("no formatter/linter config", `M_sum`/`G` formulas as fixed, "generated binary outputs in final_documents must never be hand-edited … regenerated via generator scripts", German-comments rule, `Strategy` hand-sums), ARCHITECTURE ("treating this as software application" anti-pattern, scripts-only layers, generators as presentation layer, `sim_low/med.json` caches, entry points = generators). Also stale (not feeding CLAUDE.md but read by GSD agents): STRUCTURE.md, TESTING.md ("none"), CONCERNS.md, INTEGRATIONS.md.
- Options: rewrite by hand, or `/gsd-map-codebase` to regenerate all seven maps, then review and trim; both then `generate-claude-md --auto`. Recommended: `/gsd-map-codebase` for the four non-feeding maps plus hand-trimmed STACK/CONVENTIONS/ARCHITECTURE (they must stay short because they are inlined into every session).
- Root CLAUDE.md and `.claude/CLAUDE.md` both load; the rewritten root file should not duplicate the generated sections.

### (d) `docs/` sweep
Only one file, `docs/folienkonzept_spielphasen_mechtech.md` (197 lines, written 2026-07-06 with the deck). Outdated: "Discovery-Signale" (README section that no longer exists), "E-Ziel-Check" in slide 6 ("erst Events, dann Angriffe, dann **E-Ziel-Check**, dann OPEX/Recovery"), "KZ-Bonus/-Malus als Feedback", "Kommunikation an den Kunden hat eigenen KZ-Effekt" (never a rule; `test_paths` forbids "Kommunikationseffekt" in README), "Upgrades/Swaps", Reflexion without the debrief structure, slide numbers 23–30 (the deck is now 27–35) and "alle acht Folien" for nine, Tabelle 1/2 (now the team booklet), Moderator in-character Discovery roleplay (now document-based). **Recommendation: archive** to `archive/historical_docs/` (it is speaker prep for deck slides that change in this phase; the debrief and schedule replace its function; updating it duplicates the deck checklist). Then update the CLAUDE.md line that says `docs/` holds "kurze, weiterhin gültige Referenzblätter" and the README link if any. No test reads `docs/`.

### (e) Intro deck `final_documents/Planspiel_Einführung + Grundlagen.pptx`
[VERIFIED: XML extraction of all 37 slides and speaker notes; slide order equals file order; 82 MB]
Hidden slides: 6, 7, 22, **28 (SPIELPHASEN agenda)**, **36 (Pinnwand)**. Speaker notes contain no game rules (only MHP marketing text). Auto date fields (`datetime1`) show 06.07.2026 / 7/6/2026 and must not be edited; title slide 1 carries a plain "06.07.2026".
**Candidate checklist for the user (slide → problem → proposed change):**
| Slide | Current text | Problem | Proposed change |
|-------|--------------|---------|-----------------|
| 1 | "06.07.2026" (title) | event date of the MHP run | ask user: new date or remove |
| 26 | "5 Minuten Pause bis 15:00" | clock time fixed to the MHP run; new schedule has a 5-min break and the facilitator fills clock times by hand | "5 Minuten Pause" |
| 28 (hidden) | five phases: Spieleinführung, Informations- und Lesephase, Budgetverhandlung, Angriffssimulation (3 Runden), Reflexion im Plenum | no Welle 0, "Reflexion" is now the debrief; Maßnahmenwahl is merged with budget | rename phases to the new flow (Einführung, Story und Gruppen, Übungswelle, Maßnahmen und Budget, Angriffswellen, Auswertung und Debrief); a sixth step needs a shape copy, not run text only. **Best vehicle for D-19:** unhide this slide as the flow overview |
| 29 | MechTech facts | none | none |
| 30 | "Beratungsteam aus 3–4 Personen" | project format is 5 per team | "5 Personen" (D-19) |
| 31 | "20 min"; Material: Unternehmenssteckbrief, Beauftragungsmail, Zeitungsartikel | schedule gives 25 min; the generated set has a fourth pre-wave document (Audit-Mail) | "25 min"; add Audit-Mail |
| 32 | "ein Budget von 350.000 €"; "Budgetübersicht" | tiers are 370.000/390.000/405.000 € (single figure in a hand-maintained deck drifts) | name the budget tiers without a figure; Material: Teamheft, Maßnahmenkarten |
| 33 | "20 Minuten Pause bis 16:50" | second break is 15 min, clock time fixed | "15 Minuten Pause" |
| 34 | "Material: Angriffsblatt, Events (pro Welle)"; "20 min pro Welle" | matches the schedule; material names are old | "Angriffsblatt, Eventkarten, So funktioniert eine Welle"; optionally add Change-Fenster |
| 35 | "Endergebnis und Reflexion … Endergebnisblatt … 30 min" | now Abschluss/Budget Review 10 + Debrief 20; sheet is the Teamheft | adjust title/material; keep 30 min total or split |
| 36 (hidden) | Pinnwand template: "Bewilligtes Budget: 150.000 €", "Ransomware Angriff 1", "Phishing Angriff 2", "Supply Chain Attack Angriff 3" | whiteboard step removed; wrong attack names (real ones: Ransomware, OT-Störung, Datenexfiltration); shows attack names and a budget before the game | D-19: replace by the flow overview (or delete and unhide 28) with no attack names and no budget figure |
Candidates from the CONTEXT that are **not present** in the deck: E-target bonus/malus, "Maßnahmenwechsel", flat −15, Budget Review "25.001" boundaries, RoS including events (slide 25 is a generic definition and is fine). State this so the checklist is not padded.
**python-pptx editing with formatting preserved:** python-pptx 1.0.2 is a project dependency [VERIFIED: pyproject.toml]. Iterate `slide.shapes` → `shape.text_frame.paragraphs` → `paragraph.runs`; set `run.text = new` on the first run of the sentence and `run.text = ""` on the following runs of the same paragraph; never assign `paragraph.text` or `text_frame.text` (collapses runs and loses character formatting). Skip auto date/number fields (`a:fld` is not a run). Adding a sixth phase on slide 28 or building slide 36's replacement needs shape duplication or deletion (`shape._element.getparent().remove(shape._element)`); flag it to the user in the checklist. Work on a copy, reload and re-extract the text to diff against the approved list, and have the user open the result in PowerPoint. The file is 82 MB: a committed edit adds roughly that much to `.git` again (four prior versions are already in history).
### (f) MHP company profile and generated story documents
- `MHP Company Profile DE - Jubilee Logo.pptx`: grep for planspiel, Kundenzufriedenheit, MechTech, Budget, Angriff, Ransomware, Welle returns nothing; it contains no game rules. Disposition: no change.
- `13052026_VWI meets MHP_Offenes Treffen.pptx`: unrelated talk deck, no game terms.
- Generated Audit-Mail / Steckbrief / Anfrage-Mail / Zeitungsartikel live in `texte.toml` `story.*` and are covered by `check_story_mechanics` (forbids KZ, Kundenzufriedenheit, OPEX, Init-Kosten, Budget-Tier, RoS, E-Wert, "Level N" and tier amounts) and `check_giveaway` (story profile) at `planspiel texts` and at print time. The Audit-Mail text names five audit topics (IAM/PAM, Backup, Patch, Logging/SIEM, OT-Segmentierung) which are the OEM-Audit checklist measures M1, M2, M4, M5, M7 (a deliberate clue), and no rule. Disposition: no outdated rules; closing evidence is `uv run planspiel texts` = 0 errors plus a read-through.

## Q7. "Was ist neu": complete content list

**Rules (D-13; one row each, numbers generated):**
1. RULE-01 Levelwechsel vs Maßnahmentausch; "Maßnahmenwechsel" retired; Kurswechsel forces exactly one Maßnahmentausch (customer covers Init of the new measure up to the dropped one, no refund).
2. RULE-02 Downgrade allowed in the change window; Init never refunded; OPEX falls from the next wave.
3. RULE-03 Overspend: −X KZ per started step (X = `overspend_penalty.kz_per_step`, step = `overspend_penalty.step` k€; currently 3 and 10.000 €); replaces flat −15.
4. RULE-05 Sparprogramm (or any event-induced overrun): penalty only if still over budget at the end; the change window is the chance to return.
5. RULE-06 RoS counts own spend only (Init, OPEX, Init-differences, Kurswechsel difference); event effects excluded both ways.
6. RULE-07 Budget Review tiers "ab" (inclusive): generated by `review_text.boundary_text`.
7. RULE-08 No E-target KZ bonus/malus (never printed in MHP; nothing to do on paper).
8. RULE-04 (overspend gate) is internal; mention only as one line "Überziehen lohnt sich nie" or omit (RULE-04 is not in D-13's list).
**Additional rule/flow items not in D-13 (propose to the user):** KZ change per wave is rounded once (half away from zero) then clamped 0–100; Init is also due on upgrade or new measure in a change window (net per window; Budget.docx said "einmal zu Spielbeginn"); Exzellenz-Bonus now counts Level 2 and above; Final-Index = KZ + k × RoS₂ (k from `final_index.weight_ros`, currently 10) as the facilitator comparison value (new; MHP printed none); event order: MHP printed Angriff → Events (Budget.docx rows, "Event: Nach Welle N", PROJECT.md timing "Attack 1 + Event 1"), the wave page now lists Events as step 1 (see Open Questions).
**Flow:** no whiteboard write-up; Welle 0 worked example; debrief block; new schedule (total and wave minutes from `session_schedule`; refer to the booklet page).
**Material:** generated PDFs replace docx/pptx; veiled attacks (names only when the wave hits); clue matrix in the booklet; Teamheft (planning, tracking page, RoS and Budget Review) replaces Budget.docx + RoS docx; "So funktioniert eine Welle"; Welle-0 sheet.
**Values:** the old → new table of §Q1 (≈21 rows).
**One-page estimate [ASSUMED, MEDIUM]:** `\small` rules table of 8 rows × 2 lines ≈ 190 pt, flow and material lists ≈ 140 pt, headings and notice ≈ 110 pt, value table at `\footnotesize` with grouped rows (budget tier row = budget + KZ-Start, bonuses per wave, events one row each) ≈ 210 pt: ≈ 650 pt of the 731 pt text height. It fits if values are grouped; an ungrouped cell-per-value table (≈60 lines) does not.
**Enforcement (D-15):** model with an ordered priority list (rules, flow, material, values) and a test that fails when the value table exceeds a row budget (fast proxy), plus the PDF test: `len(pages)==1`, one `PLANSPIEL-FILL` report with `used ≤ text` and the stamp on the page. Build a `compact` flag only if the PDF test fails: values collapse to key rows plus a sentence pointing to cards and worksheets (generated, not typed); rule rows never collapse.

## Q8. Debrief

**Key design (all prose digit-free, lists allowed as in `how_to`):**
```
[sheets.debrief]            title, intro, guide_label, data_label, clue_matrix_pointer, compare_label (+ row labels)
[sheets.debrief.reaction]   title, questions = [...], prompts = [...]
[sheets.debrief.description] / .analysis / .application   (same shape)
```
Stage ids come from `session_schedule.debrief_stages[].id` (config) so a stage added in config demands its keys through `required_keys`. Model test: four stages in the fixed order; each stage 2–3 entries counting `questions` + `prompts` (D-11); total between 8 and 12; guide minutes printed from config and summing to the `debrief` block. Stage model (reaction → description → analysis → application) is the common three-phase debrief model (description, analysis, application) plus an opening reaction stage [CITED: absel-ojs-ttu.tdl.org/absel/article/view/53/51 (search snippet; Gillespie 1992 three phases), not opened in full].
**Proposed content (German drafts for the planner; no digits):** reaction: "Wie fühlt ihr euch nach den drei Wellen?", "Welcher Moment war der überraschendste?"; description: "Was habt ihr in jeder Welle entschieden und warum?", data prompt "Vergleicht die Teams nach KZ, RoS und Final-Index"; analysis: "Welche Hinweise in den Unterlagen hättet ihr lesen können?" (points to the clue matrix pages), "Was hättet ihr im Change-Fenster anders gemacht?", optionally the README sentence "Hätte das Team zu Spielbeginn weniger oder niedrigere Maßnahmen gewählt, wäre es im Budget geblieben und besser gelandet" (README, gate section); application (D-10): "Welche Maßnahme würdet ihr in eurem Unternehmen zuerst umsetzen?", "Wo trefft ihr im Alltag echte CIA-Abwägungen?".
**Data the facilitator already has:** Final-Index formula, weight k and a worked tier table on booklet p8 (`final_title`, `final_index_note`: "Vergleichswert der Spielleitung für das Debriefing"); the full **clue matrix is printed in the booklet** (pp10–12; `planspiel clues` is only the CLI view of the same data); reference paths with change windows (answer keys); team results come from each team's Teamheft RoS/Budget Review page and tracking page. What is missing for the "compare teams" prompt is a place to write the team values: add a small empty comparison table (rows = teams) to the debrief page, which needs a team count or free lines (Open Question).

## Q9. Dry run (FLOW-05, D-05..D-07, D-25)

- **Protocol template (`spielleitung-probelauf`, one A4 page, from config):** one row per `session_schedule` block: label (texte), planned minutes, cumulative planned minutes, then empty cells: actual start (clock), actual minutes, overrun?, unclear points / questions, calculation errors. Footer: total planned minutes from config, pass rule (D-25) as prose without numbers ("Jede Welle im geplanten Zeitfenster, Gesamtdauer im Rahmen, keine Hilfe durch die Autorin oder den Autor"), a line to log each help given, and observer name/date lines. 11 rows × about 16 mm writing height fit on one portrait A4; verify with the fill report (landscape is the fallback). Model: reuse the schedule row helper from the booklet so both read the same config. Attack names must not appear (use "Welle N" labels).
- **Pass rule (D-25):** per wave `actual ≤ planned`, session `≤ total_minutes`, no author help; each overrun, unclear point or calculation error becomes a gap-closure item unless the user accepts it at verification.
- **What the plans must deliver before 2026-11-25 (23 days from today):** all FLOW-02/03/04 content committed; print set regenerated and committed once (stamp without "+lokal"); a human checkpoint with physical prints (precedent: Phase 5 needed five print rounds and a UAT); the intro deck edited and approved if the test group will see it; the print list followed to assemble the sets for the test group; the protocol printed.
- **Recording results:** write the transcribed protocol into `.planning/phases/07-session-flow-handoff/07-DRYRUN.md` [ASSUMED name], then run `/gsd-plan-phase 7 --gaps`-style gap-closure plans (D-06). Verification (`human_verify_mode: end-of-phase`) waits for the run.
- **Plan split:** FLOW-05a (protocol builder + print-set commit + checkpoint) is automatable and sits before the run; FLOW-05b is the non-autonomous event (a `checkpoint:human-verify`-type plan with the run script, stopwatch, the protocol and the recording step).

## Plan sequencing: files touched by each requirement

| File / area | LEG-01 | FLOW-02 | FLOW-03 | FLOW-04 | FLOW-05a | LEG-02 |
|-------------|:-:|:-:|:-:|:-:|:-:|:-:|
| `simulation_config.json`, `config.py`, `validate.py` | | ✔ (block) | ✔ (stage minutes) | | reads | |
| `content/texte.toml`, `planspiel/texts.py` | | ✔ | ✔ | ✔ | ✔ | |
| `planspiel/master.py`, `print/templates/master.tex.j2`, `tests/test_master_*` | | ✔ | ✔ | | | |
| `planspiel/render.py`, `cli.py`, `stamp.py` | | | | ✔ (builder arg, loader, inputs) | ✔ (builder) | |
| `planspiel/was_neu.py`, `content/mhp_baseline.json` | | | | ✔ | | |
| `planspiel/probelauf.py` + template | | | | | ✔ | |
| `pyproject.toml`, `uv.lock`, `tests/test_inventory.py`, `test_legacy_generators_smoke.py`, `test_texts_migration.py`, `test_environment.py`, `content/INVENTORY.md`, `content/assets/*.md` | ✔ | | | | | |
| `README.md`, `CLAUDE.md`, `.planning/codebase/*`, `.claude/CLAUDE.md`, `docs/` | | | | | | ✔ |
| `final_documents/generated/*` + `manifest.json` | | | | | ✔ (single writer) | |
| intro deck | | | | | | ✔ |

Recommended order (waves): **1** LEG-01 (independent, unblocks doc paths) ∥ FLOW-02 (config + booklet page; no conflict with LEG-01) → **2** FLOW-03 (same files as FLOW-02: sequential) → **3** FLOW-04 (shares `texte.toml`/`texts.py`/`render.py`; reads schedule for its flow rows) → **4** FLOW-05a (last print-affecting plan: protocol + regenerate + commit print set + checkpoint) ∥ LEG-02 README / CLAUDE.md+maps (needs LEG-01 paths and final pipeline) → **5** LEG-02 intro-deck checklist (user approval) → deck edit → **6** FLOW-05b run on 2026-11-25 → **7** gap-closure plans. If LEG-02 docs must mention the final print command output, run them after FLOW-05a.
One requirement per PLAN.md holds: FLOW-02, FLOW-03, FLOW-04, LEG-01 one plan each; FLOW-05 and LEG-02 split as above because their parts have different files, gates (print set, user approval, a calendar-bound event) and owners. Wave-0 test scaffolding belongs to the plan that owns each feature (TDD).

## Common Pitfalls

### Pitfall 1: README/CLAUDE.md rewrite breaks seven tests
**What goes wrong:** `uv run pytest` fails after the German rewrite. **Why:** tests assert exact phrases (§Q6a). **Avoid:** list the anchors in the plan; keep them or update the tests in the same commit; run `uv run pytest tests/test_budget_review*.py tests/test_kurswechsel.py tests/test_paths.py tests/test_ros_ledger.py tests/test_sparprogramm.py tests/test_e_target_removed.py -q` after each README edit. **Signs:** assertion on `"Maßnahmenwechsel"` count.

### Pitfall 2: moving generators makes `test_texts_migration` fail at collection
**What goes wrong:** the module executes `_measure_meta("generate_pptx_cards.py")` at import. **Avoid:** decide in the LEG-01 plan (retire vs retarget) and make the change in the same commit as the move.

### Pitfall 3: stamp reads "+lokal" on the committed print set
**Why:** `planspiel/`, `print/`, `pyproject.toml`, `uv.lock` or the new baseline file uncommitted when printing. **Avoid:** commit everything first, build, `print --check`, then commit PDFs; add `content/mhp_baseline.json` to the stamp inputs.

### Pitfall 4: schedule page found as a wave section
**What goes wrong:** `_section_pages` locates wave titles; keep wave titles (revealed) off new pages and use "Welle N".

### Pitfall 5: digit lint on direction/debrief prose
**What goes wrong:** `texts.digit` error for "Welle 1", "10 Minuten", "3–4". **Avoid:** labels via model composition (`f"{label} {wave_id}"` from config) and never type numbers.

### Pitfall 6: new required text keys without tuples (or vice versa)
`orphan_key` / `missing_key` errors from `check_coverage`; update `texts.py` tuples and `required_keys` together with `texte.toml`.

### Pitfall 7: Exzellenz-Bonus and event timing wording
The Phase 6 retune made the Exzellenz-Bonus condition "Level 2" while the rule counts `>= 2` (`rules.count_measures_at_level`, `rules.py:335-337`); the card prints "Je Maßnahme auf Level 2: KZ +3" (`eventkarten` key `per_measure_at_level`). Event cards say "Event: Nach Welle N" (`sheets.labels.event_after_wave`) while `sheets.welle.text_events` and the wave page put events first. Both are exactly what a facilitator who did not write the rules trips over; the dry run would find them. Decide in plan-phase whether to fix wording now (small `texte.toml` change, regenerates the print set once anyway) or log them as dry-run candidates.

### Pitfall 8: direction column leaks hand-out order
Telling the facilitator to hand out `angriff-N` sheets "with the cards" reveals attacks early. Write "Angriffsblatt erst zu Beginn der Welle austeilen" style directions; the pre-wave documents are `spieler-*`/`uebung-*`.

## Code Examples

### Optional-block loader and invisibility test (pattern from `planspiel/config.py` + `tests/test_practice_config.py`)
```python
# config.py (sketch)
session_schedule = None
if "session_schedule" in raw:
    block = raw["session_schedule"]
    session_schedule = SessionSchedule(
        total_minutes=block["total_minutes"],
        blocks=tuple(Block(b["id"], b["minutes"]) for b in block["blocks"]),
        debrief_stages=tuple(Stage(s["id"], s["minutes"]) for s in block["debrief_stages"]),
        print_list=tuple(PrintRow(r["job"], r["per_team"], r["facilitator"]) for r in block["print_list"]),
    )

# tests/test_session_schedule_config.py (sketch)
def test_the_block_never_reaches_the_real_config_fields(cfg, tmp_path):
    raw = _raw(); del raw["session_schedule"]
    plain = _load(raw, tmp_path)
    assert dataclasses.replace(cfg, session_schedule=None) == plain
    assert rules.evaluate_plan(cfg, "medium", SEL) == rules.evaluate_plan(plain, "medium", SEL)
```

### One-page PDF proof (from `tests/test_wave_page_pdf.py` shape)
```python
def test_the_sheet_is_exactly_one_page_within_the_text_height(printed_set):
    pdf = printed_set.out_a / "spielleitung-was-ist-neu.pdf"
    assert len(PdfReader(pdf).pages) == 1
    reports = FILL.findall(unwrapped_log(printed_set.build_a / "spielleitung-was-ist-neu.log"))
    assert len(reports) == 1 and float(reports[0][1]) <= float(reports[0][2])
```

### Run-level pptx edit (D-18)
```python
from pptx import Presentation
prs = Presentation(src)
for shape in prs.slides[29].shapes:                 # slide 30 (0-based 29)
    if not shape.has_text_frame: continue
    for para in shape.text_frame.paragraphs:
        runs = para.runs
        text = "".join(r.text for r in runs)
        if "3–4 Personen" in text:
            runs[0].text = text.replace("3–4 Personen", "5 Personen")
            for r in runs[1:]: r.text = ""
prs.save(dst)                                        # work on a copy, never paragraph.text
```

## State of the Art

| Old approach | Current approach | When changed | Impact |
|--------------|------------------|--------------|--------|
| Hand-edited docx/pptx worksheets and cards | Jinja → LuaLaTeX from config + `texte.toml` | Phases 4–5 | LEG-01 only moves the leftovers |
| Print-sync trap (numbers typed in Angriff docx) | numbers generated, `print --check` stale detection | Phase 4 | CLAUDE.md section is obsolete |
| Flat −15 overspend | −X per started step | Phase 2/6 | "Was ist neu" row |
| `.claude/CLAUDE.md` from June maps | maps to be refreshed | now (D-24) | session context is wrong until regenerated |

**Deprecated/outdated:** `generate_*.py`, `pptx_output/`, `angriff_berechnung.xlsx`, `docs/folienkonzept_spielphasen_mechtech.md`, the MHP docx/pptx in `final_documents/`.

## Runtime State Inventory

Phase 7 contains a move/rename (LEG-01).

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None. No database; JSON/TOML in git. `final_documents/generated/manifest.json` holds hashes of generated PDFs only | none; regenerated by the print plan |
| Live service config | None (no external service) | none |
| OS-registered state | None | none |
| Secrets/env vars | None; `.claude/hooks/session-start.sh` runs `npx @opengsd/gsd-core` only in remote sessions | none |
| Build artifacts / installed packages | `build/` (gitignored, old logs from Phase 5/6); `__pycache__` for root scripts; `.venv` console script `planspiel` (unaffected); `uv.lock` if `openpyxl` is dropped; `.pytest_cache` node ids mention stamp tests only; untracked `sim_*.json` and `simulation_summary*.json` at root (gitignored, not part of the move); `.claude/CLAUDE.md` (generated, stale) | `uv lock` + `uv sync` after the dependency change; delete nothing in `build/`; regenerate `.claude/CLAUDE.md` in LEG-02 |

**Nothing found in:** stored data, live service config, OS-registered state, secrets: verified by reading `pyproject.toml`, `.claude/settings.json`, `.claude/hooks/session-start.sh`, `.gitignore`, and grepping for services.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The "Was ist neu" page fits (~650 of 731 pt) when values are grouped | Q7 | needs the D-15 compaction; discovered by the PDF test, low cost |
| A2 | `sys.addaudithook` recording of `open` events works inside pytest for the D-17 proof | Q5 | fall back to the static scan plus the temp-dir run |
| A3 | Proposed print-list quantities (per team / facilitator) per document | Q4 | wrong counts printed on the page; user must confirm (Open Question 1) |
| A4 | Debrief stage minutes 3/4/8/5 | Q4 | discretionary; any split summing to the debrief block is valid |
| A5 | Stage model citation (description, analysis, application plus reaction) from a search snippet, not read in full | Q8 | cosmetic; the order is given by FLOW-03 anyway |
| A6 | Workshop date: evidence says early July, PROJECT.md says September | Q1 | none for the baseline; correct PROJECT.md/CONTEXT wording |
| A7 | `07-DRYRUN.md` as the recording artifact | Q9 | naming only |
| A8 | MHP order was Angriff → Events (Budget.docx rows, "Nach Welle N", timing table) and the current order is Events → Angriff | Q7, Pitfall 7 | "Was ist neu" flow row may be wrong or unnecessary; confirm with the user |

## Open Questions

1. **Print-list quantities and team count** (D-23).
   - Known: three teams of five, single-sided printing, 13 current PDFs (+2 new).
   - Unclear: copies per team for each document (one per team or one per person: story documents, Teamheft, cards), whether the attack worksheet is one per team per wave, and whether `teams` should be in config for the debrief comparison table.
   - Recommendation: ask the user in plan-phase; encode the answer only in config; avoid a `teams` key unless the comparison table needs rows.
2. **Exzellenz-Bonus wording** ("auf Level 2" vs rule "ab Level 2") and **event timing wording** ("Nach Welle N" vs events first). Fix the card/wave-page texts in this phase (one extra `texte.toml` edit, no mechanics change) or leave them to the dry run?
3. **Workshop date** (July vs September) for PROJECT.md and the "Was ist neu" source note.
4. **Items beyond D-13 for "Was ist neu":** KZ rounding once per wave, Init on upgrades in change windows, Exzellenz-Bonus condition, Final-Index, event order. Include? (Recommended: yes, as one-line rows in the rule category; they are the changes a former MHP facilitator will otherwise hit during the run.)
5. **`test_texts_migration` fate** and **dropping `openpyxl`** (recommended: retire the generator-reading tests, drop `openpyxl`, keep `python-pptx`).
6. **`docs/folienkonzept_spielphasen_mechtech.md`:** archive (recommended) or update.
7. **Intro deck slide 28/36:** use the hidden slide 28 (SPIELPHASEN) as the new flow overview and unhide it, delete slide 36, versus rebuilding slide 36. The six-step flow needs a new shape (not run text only).
8. **Schedule page placement:** one page with print list or two (decided by the fill report); and whether the first page's contents list gets the new sections.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| uv | all `uv run` | ✓ | working (tests ran) | — |
| Python 3.12 (uv-managed) | everything | ✓ | via uv | — |
| LuaLaTeX (MiKTeX) | print build, `-m pdf` tests | ✓ | LuaHBTeX 1.25.7, MiKTeX 26.5 | none; `print --check` works without TeX |
| git | stamp, moves, provenance test | ✓ | — | — |
| node + gsd-tools | `generate-claude-md` | ✓ | `gsd-tools.cjs` ran with `--help` | hand-edit `.claude/CLAUDE.md` (not recommended) |
| python-pptx | deck edit | ✓ | 1.0.2 (pinned) | zip/XML edit |
| Printer + A4 paper | physical print review (precedent: Phase 5 UAT) | not testable here | — | user-side |
| PowerPoint | user review of the edited deck | user-side | — | LibreOffice/Impress |

**Missing dependencies with no fallback:** none for automation. The physical print review and the dry run are human steps.

## Validation Architecture

Nyquist validation is enabled (`.planning/config.json` `workflow.nyquist_validation: true`).

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (+ pypdf 6.19.0 for PDF text) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`addopts = -m 'not slow and not pdf'`, markers `slow`, `pdf`, `balance`) |
| Quick run command | `uv run pytest -q -x tests/test_<area>.py` (single area, seconds) |
| Full fast suite | `uv run pytest -q -x` (2681 passed, 185 deselected, 180 s measured today) |
| PDF suite | `uv run pytest -m pdf -q` (137 tests, about 220 s, needs MiKTeX; builds the full set twice) |
| Freshness | `uv run planspiel print --check` (no TeX; fast) |
| Do not run | `-m slow`, `-m balance`, `balance_analysis.py --layers all`, `planspiel gate --paths` (no rule or number change in this phase) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FLOW-02 | block sum == total (190); wave_1 == 20; debrief in 15..20; no whiteboard block; wave ids ↔ `waves`; `wave_0` ↔ `practice`; validator rejects broken blocks; block invisible to rules | unit | `uv run pytest tests/test_session_schedule_config.py -q` | ❌ Wave 0 |
| FLOW-02 | schedule rows: label/direction from texte, cumulative minutes from config, empty clock column, print list jobs ⊆ rendered jobs, no typed numbers | unit | `uv run pytest tests/test_schedule_model.py tests/test_master_model.py -q` | ❌ / ✅ extend |
| FLOW-02 | schedule + print list pages exist, fill within text height, page count, stamp | pdf | `uv run pytest -m pdf tests/test_master_pdf.py -q` | ✅ extend |
| FLOW-02 | texte keys covered, no digits | unit | `uv run planspiel texts` ; `uv run pytest tests/test_texts_coverage.py tests/test_texts_digits.py -q` | ✅ |
| FLOW-03 | four stages in order, 2–3 entries each, ~10 total, minutes sum to debrief block, clue-matrix pointer present | unit | `uv run pytest tests/test_debrief_model.py -q` | ❌ Wave 0 |
| FLOW-03 | debrief page in booklet, fill report | pdf | `uv run pytest -m pdf tests/test_master_pdf.py -q` | ✅ extend |
| FLOW-04 | value rows are diff-driven (mutate cfg → rows change; unchanged values absent); all 8 rule topics; numbers from cfg; meaning-changed rows flagged | unit | `uv run pytest tests/test_was_neu_model.py -q` | ❌ Wave 0 |
| FLOW-04 | baseline isolation (string only in builder, loader, stamp, tests), provenance vs `git show 1cfb2fa`, stamp input pinned | unit | `uv run pytest tests/test_baseline_isolation.py tests/test_print_stamp.py -q` | ❌ / ✅ extend |
| FLOW-04 | exactly one page, `used ≤ text`, stamp, no overfull | pdf | `uv run pytest -m pdf tests/test_was_neu_pdf.py -q` | ❌ Wave 0 |
| FLOW-04 | no attack name in the sheet | unit | in `test_was_neu_model.py` via `veil.name_hits` | ❌ Wave 0 |
| FLOW-05 | protocol rows == schedule blocks with planned minutes from config; columns; no attack names | unit | `uv run pytest tests/test_probelauf_model.py -q` | ❌ Wave 0 |
| FLOW-05 | protocol one page within text height | pdf | `uv run pytest -m pdf tests/test_probelauf_pdf.py -q` | ❌ Wave 0 |
| FLOW-05 | the timed dry run (waves within minutes, total within 190, no author help) | manual | protocol filled on 2026-11-25 | manual |
| LEG-01 | 20 files accounted for at new locations; none of the 15 left in `final_documents/`; `pptx_output`, xlsx not tracked at root | unit | `uv run pytest tests/test_inventory.py -q` | ✅ update |
| LEG-01 | no reference to `archive/` or the retired files in build, package, wrappers, content | unit | `uv run pytest tests/test_no_archive_references.py -q` | ❌ Wave 0 |
| LEG-01 | tests that read generators removed or retargeted; env pins consistent | unit | `uv run pytest tests/test_environment.py tests/test_texts_migration.py tests/test_single_definition.py -q` | ✅ update |
| LEG-02 | README anchors still pass; README names `planspiel print`, `--check`, order config → README → texte → print; no retired formulas (`M_sum`, `kzUnit`) | unit | `uv run pytest tests/test_docs_current.py tests/test_kurswechsel.py tests/test_paths.py tests/test_budget_review*.py tests/test_ros_ledger.py tests/test_sparprogramm.py tests/test_e_target_removed.py -q` | ❌ / ✅ |
| LEG-02 | CLAUDE.md in English, no print-sync trap, no generator references; `.claude/CLAUDE.md` has no `sim_low.json`/"no tests" text after regeneration | unit | `uv run pytest tests/test_docs_current.py -q` | ❌ Wave 0 |
| LEG-02 | story documents contain no rules | unit | `uv run planspiel texts` | ✅ |
| LEG-02 | intro deck edited text equals the approved checklist (re-extract and diff) | scripted + manual | script from this research (`zipfile` extraction) vs checklist; user opens in PowerPoint | manual |
| all | print set fresh and committed | cli | `uv run planspiel print --check` | ✅ |

**Manual-only (justified):** the dry run (human timing), physical print review (layout on paper, as in Phase 5), the intro-deck review in PowerPoint, README prose quality, user approval of the deck checklist.

### Sampling Rate
- **Per task commit:** the area's quick command (seconds); for texts/config changes also `uv run planspiel validate && uv run planspiel texts`.
- **Per wave merge:** `uv run pytest -q -x` (≈3 min) and, for any print-affecting plan, `uv run pytest -m pdf tests/test_master_pdf.py tests/test_was_neu_pdf.py tests/test_probelauf_pdf.py -q`.
- **Phase gate:** fast suite + full `-m pdf` + `uv run planspiel print --check` exit 0 + dry-run protocol before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_session_schedule_config.py`, `tests/test_schedule_model.py` (FLOW-02)
- [ ] `tests/test_debrief_model.py` (FLOW-03)
- [ ] `tests/test_was_neu_model.py`, `tests/test_was_neu_pdf.py`, `tests/test_baseline_isolation.py` (FLOW-04)
- [ ] `tests/test_probelauf_model.py`, `tests/test_probelauf_pdf.py` (FLOW-05)
- [ ] `tests/test_no_archive_references.py` (LEG-01), updates to `test_inventory.py`, `test_environment.py`, `test_single_definition.py`; delete `test_legacy_generators_smoke.py`; decide `test_texts_migration.py`
- [ ] `tests/test_docs_current.py` (LEG-02)
- Framework install: none.

## Security Domain

`security_enforcement` is enabled (ASVS level 1, block on high). The phase has no network, auth or user data. Relevant categories:

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication / V3 Session / V4 Access Control | no | no users, no service |
| V5 Input Validation | yes | validator for `session_schedule`; fixed file names (no content string selects a path, `texbuild.check_job_name`, `check_asset_name`); strict JSON schema for the baseline; `finalize=tex_escape` for every rendered string |
| V6 Cryptography | no (SHA-256 content hash is integrity labelling only) | `hashlib` |
| V10 Malicious code / V14 Config | yes | no new dependencies; pinned deps; no network in build; MiKTeX installer disabled in bounded subprocesses |

### Known Threat Patterns
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Veil leakage: attack names in schedule labels, direction lines, "Was ist neu", protocol, or in a hand-out instruction that releases `angriff-*` sheets early | Information disclosure | facilitator jobs are unscanned by design: add name-hit tests on the new models (profile `names`), use "Welle N" labels, direction wording "Angriffsblatt erst zu Beginn der Welle", keep `spielleitung-` jobs out of the player rows of the print list |
| TeX injection through baseline/texte strings | Tampering | all strings pass `tex_escape`; the baseline is numbers plus short ids; no free text rendered unescaped |
| Accidental data loss during LEG-01 (delete instead of move, `git add -A` over 6 GB of ignored dumps, overwrite of the 82 MB deck) | Tampering / Denial | `git mv` only, separate commit, verify `git status` shows renames and 15+8 entries, work on a copy of the deck, never `git clean`/`reset --hard`, check ignored dumps stay untracked |
| Dangling references to `archive/` after the move | Reliability | D-17 tests (static scan, audit-hook run, tree test) |
| Stale or locally modified print set handed out | Integrity | `print --check`, stamp without "+lokal", one commit for the PDFs after all inputs |
| Generator output in `final_documents/generated` hand-edited | Tampering | manifest hashes via `--check` |
| Supply chain | Tampering | no new package; removing `openpyxl` only shrinks the surface |

## Sources

### Primary (HIGH confidence, read or executed in this session)
- `.planning/phases/07-session-flow-handoff/07-CONTEXT.md`, `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/config.json`
- `simulation_config.json` (current) and `git show 1cfb2fa:simulation_config.json`; `git log` on config and `final_documents`
- Extracted text of `final_documents/*.docx|pptx` (zip/XML scripts in the scratchpad, not committed)
- `planspiel/{master,audience,render,texbuild,stamp,veil,texts,validate,config,cli,review_text,wave_page,eventtext,rules}.py`, `print/templates/master.tex.j2`, `print/planspiel.sty`
- `tests/{test_master_pdf,test_wave_page_pdf,test_practice_config,test_inventory,test_legacy_generators_smoke,test_texts_migration,test_single_definition,test_environment,test_veil_audience,test_print_check,conftest}.py` and the README-reading tests listed in §Q6a
- `content/texte.toml`, `INVENTORY.md`, `digit_allowlist.toml`, `giveaway_terms.toml`, `docs/folienkonzept_spielphasen_mechtech.md`, `README.md`, `CLAUDE.md`, `.claude/CLAUDE.md`, `.planning/codebase/STACK.md`
- `~/.claude/gsd-core/bin/lib/profile-output.cjs` (`cmdGenerateClaudeMd`)
- Command runs: `uv run planspiel validate` (0 errors), `uv run planspiel texts` (0 errors), `uv run planspiel print --check` (current), `uv run pytest -q -x` (2681 passed in 180 s), `uv run pytest --co -m pdf` (137 tests), `lualatex --version`

### Secondary (MEDIUM confidence)
- [ABSEL: debriefing three-phase model (search snippet only)](https://absel-ojs-ttu.tdl.org/absel/article/view/53/51)

### Tertiary (LOW confidence)
- layout/page-fit estimates (A1), print-list quantities (A3)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, no new packages, versions read from `pyproject.toml`
- Architecture: HIGH for patterns (copied from existing code and tests), MEDIUM for page fit
- Pitfalls: HIGH, each traced to a file and line or a command output
- MHP baseline: HIGH for numbers (scripted comparison of all 30 cards, 3 worksheets, tiers, events); MEDIUM for the workshop date

**Research date:** 2026-11-02
**Valid until:** 2026-11-25 (dry run); repo-internal facts stay valid until the next change of `planspiel/`, `print/` or `content/`
