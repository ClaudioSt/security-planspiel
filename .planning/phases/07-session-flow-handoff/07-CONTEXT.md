# Phase 7: Session Flow & Handoff - Context

**Gathered:** 2026-11-02
**Status:** Ready for planning

<domain>
## Phase Boundary

A facilitator who did not write the rules can run the new version in one afternoon from the generated material alone. Phase 7 delivers:

- a revised session schedule with Welle 0 and a 15–20 min debrief, without the whiteboard step (FLOW-02)
- a debrief question set (reaction → description → analysis → application) (FLOW-03)
- a one-page "Was ist neu" sheet for facilitators who ran the MHP version (FLOW-04)
- a timed dry run with a test group on **2026-11-25** (FLOW-05)
- legacy hand-maintained files, old generators and `pptx_output/` moved to `archive/` (LEG-01)
- README.md and CLAUDE.md rewritten for the new pipeline and rules; the intro deck and the other hand-maintained documents cleared of outdated rules (LEG-02)

No new game mechanics, no rebalance, no new print documents beyond the ones named here.

</domain>

<decisions>
## Implementation Decisions

### Session schedule (FLOW-02)
- **D-01:** The schedule is a page in the facilitator booklet (`spielleitung-uebersicht.pdf`), not a separate PDF and not Markdown. The block durations live in `simulation_config.json` (new block, e.g. `session_schedule`), the block labels in `content/texte.toml`. The validator checks that the blocks add up to the stated total.
- **D-02:** Time frame of about 3h15 with two breaks, like MHP (14:55–18:10): Intro 10 · Pause 5 · Story + Gruppen 25 · Welle 0 15 · Maßnahmen + Budget 30 · Pause 15 · Welle 1 20 · Welle 2 20 · Welle 3 20 · Abschluss/Budget Review 10 · Debrief 20. The whiteboard write-up step is gone.
- **D-03:** Each change window is part of its wave's 20 minutes (events → attack → OPEX → change window). There are no separate window blocks.
- **D-04:** The page shows durations and cumulative minutes from the start, plus an empty clock-time column the facilitator fills in by hand. No start time in config.

### Dry run (FLOW-05)
- **D-05:** The test run takes place on **2026-11-25**: a test group plays the full game (Welle 0, waves 1–3, closing, debrief), led by someone who did not write the rules and who uses only the material. The author watches without helping and times each block.
- **D-06:** Phase 7 ends with that run. Verification waits for it, and its findings become gap-closure plans in Phase 7. All other plans must be finished and printed before 2026-11-25.
- **D-07:** A generated one-page protocol template (`spielleitung-` prefix, e.g. `spielleitung-probelauf.pdf`). It lists the schedule blocks with their planned minutes from config (D-01) and has columns for actual time, questions or unclear points, and calculation errors.

### Debrief (FLOW-03)
- **D-08:** The debrief is a section in the facilitator booklet (`spielleitung-uebersicht.pdf`), with texts under a new `texte.toml` key (e.g. `sheets.debrief`). There is no separate sheet and no player version.
- **D-09:** Fixed questions for each stage (reaction → description → analysis → application), plus prompts that use game data: compare teams by KZ, RoS and Final-Index; ask which clues could have been read (refers to the clue matrix); ask what the team would have done differently in a change window.
- **D-10:** The application stage includes transfer to real IT-security practice (e.g. "Which measure would you implement first in your company?", "Where do you make real CIA trade-offs?"). These are questions only, no new teaching content.
- **D-11:** 2–3 questions per stage, about 10 in total; the facilitator picks from them. A guide time per stage is printed, and those minutes add up to the debrief block from D-02.

### "Was ist neu" sheet (FLOW-04)
- **D-12:** Generated PDF with the `spielleitung-` prefix (e.g. `spielleitung-was-ist-neu.pdf`). Prose in `texte.toml`, every number from config (X per 10k, k, Budget Review tiers, …), so the sheet stays correct after a future rebalance.
- **D-13:** Content: all four categories. Rule changes RULE-01..08 (Levelwechsel vs. Maßnahmentausch, Kurswechsel as one forced swap, downgrade, overspend −X per started 10k, Sparprogramm end check, RoS without event effects, Budget Review boundaries "ab", E-target bonus removed). Flow changes (no whiteboard, Welle 0, debrief, new schedule). New material (generated PDFs instead of docx/pptx, veiled attacks, clue matrix, team booklet with tracking page). Rebalance values as an old → new table.
- **D-14:** Old values come from a frozen MHP config committed as `content/mhp_baseline.json`. Only the "Was ist neu" builder reads it, never the rules, simulation or other builders. The table shows only the values that changed. Candidate source: config at commit `1cfb2fa` (2026-07-06, last config change before the September workshop). The planner or researcher must confirm it matches the MHP state.
- **D-15:** Strictly one page, enforced by a fill-report test as for the cards and the booklet. If space runs out, the priority is rules > flow > material > values: the values table shrinks first (only key values, or a summary line pointing to the cards and worksheets), and the rule changes always stay complete.

### Legacy archive (LEG-01)
- **D-16:** Archive everything that `content/INVENTORY.md` marks as superseded: `Angriff-1/2/3_*.docx`, `Budget.docx`, `Return on Security und Final Wert.docx`, `Events_Security-Game.pptx`, `Massnahmenkarten_Security-Game.pptx`, `Unternehmenssteckbrief MechTech.docx`, `Zeitungsartikel.docx/.pdf/*.png`, `Anfrage-Mail.docx/.pdf`, `Audit-Mail.pdf`. Also archive `generate_attack_calculator.py`, `generate_from_template.py`, `generate_pptx_cards.py` and `pptx_output/`. These stay in `final_documents/`: the intro deck, the MHP company profile, the VWI talk deck and the two portraits.
- **D-17:** A test proves that the build and the package no longer reference anything under `archive/`. `tests/test_inventory.py` and `content/INVENTORY.md` are updated to the new locations, since they currently check 20 files in `final_documents/`.

### Intro deck & docs (LEG-02)
- **D-18:** Claude edits the intro deck `Planspiel_Einführung + Grundlagen.pptx` with python-pptx, replacing run text so formatting survives. It first produces a checklist of every finding (slide → problem → proposed change). The user approves the list before any edit and reviews the result.
- **D-19:** Slide 36 ("Spielplan / Vorlage für die Pinnwand") is replaced by an overview of the new flow (Welle 0 → waves → debrief) with no attack names and no budget figure. "Beratungsteam aus 3–4 Personen" is changed to the project format.
- **D-20:** Language: README.md stays **German** (rulebook for German-speaking facilitators) and is updated in content. The root CLAUDE.md is rewritten in **English**. This is a deliberate exception to the global "docs in English" rule for the README.
- **D-21:** The CLAUDE.md print-sync section is rewritten. The manual `python-docx`/`python-pptx` trap for the Angriff docx files is gone; it now describes the `planspiel print` pipeline, `--check` and the order config → README → texte.toml → print.

### Requirements review (plan-phase, 2026-11-02)
- **D-22:** The stated session total is **190 min** (3h10). The D-02 blocks add up to 190, and the MHP frame 14:55–18:10 leaves 5 min of buffer. The config holds every block duration plus the total, and the validator checks that the blocks sum to the total (D-01).
- **D-23:** The schedule page also has a direction column: each block gets one line saying what the facilitator does and what is handed out, with the prose in `texte.toml`. The page also carries a print list: which PDF, and how many copies per team and for the facilitator. The quantities live in config and are never typed into prose. Reason: no current moderation guide exists (the old one is in `archive/historical_docs/`), and a facilitator who did not write the rules has to prepare and run the session from the material alone.
- **D-24:** LEG-02 also covers `.claude/CLAUDE.md`. GSD generates it from `.planning/codebase/` (state of late September), so it still describes the old pipeline (M_sum, `sim_low.json`, old generators as live, "no tests") and it is loaded into every session. Bring the three source maps `.planning/codebase/STACK.md`, `CONVENTIONS.md` and `ARCHITECTURE.md` up to date, then regenerate `.claude/CLAUDE.md` with `gsd-tools generate-claude-md`.
- **D-25:** Pass rule for the dry run (the literal reading of ROADMAP success criterion 5): every wave block finishes within its planned minutes, the whole session finishes within the stated total (D-22), and the facilitator gets no help from the author. Each overrun, unclear point or calculation error recorded on the protocol (D-07) becomes a gap-closure item (D-06), unless the user explicitly accepts it at verification.
- **D-26:** (clarifies D-14) "MHP state" means what was printed and played at the MHP workshop. Check the config at `1cfb2fa` against the printed MHP material in `final_documents/`, which still carries the MHP numbers until LEG-01. Where the two disagree, `content/mhp_baseline.json` takes the printed value, and the difference is recorded in RESEARCH.md.

- **D-27:** Print-list quantities (D-23): the team count (3) goes into config. The planner proposes the copies per PDF for each team and for the facilitator, derived from the schedule. The user confirms them at a checkpoint before anything is printed.
- **D-28:** Two wording issues in the current print material are fixed before the dry run. This is text only (`texte.toml`/templates), with no rule change. The Exzellenz-Bonus must say Level 2 **or higher**, and the event cards' "Nach Welle N" must match the wave page, where events are step 1 of the wave. This work belongs to FLOW-05's preparation, because the material has to be self-explanatory for the run.
- **D-29:** "Was ist neu" also lists these items as rule changes, at the highest space priority (D-15): KZ is rounded once per wave, Init is paid on upgrades in the change window, the new Final-Index, and the event order within a wave.
- **D-30:** (discretion resolved) `docs/folienkonzept_spielphasen_mechtech.md` is moved to `archive/`, since it is outdated in about 8 places (see RESEARCH §Q6d).

### Claude's Discretion
- What happens to `docs/folienkonzept_spielphasen_mechtech.md`, which still mentions the E-target check: update it or move it to `archive/`.
- The check of the MHP company profile deck and of the generated Audit-Mail and Steckbrief for outdated rules. The two story documents are generated now, so their checks run through `texte.toml` and the veil and text checks.
- The exact config key names, page layout and position of the schedule, debrief and "Was ist neu" pages inside the booklet.
- The guide minutes per debrief stage, as long as they add up to the debrief block.
- Whether the root wrappers `simulate_outcomes.py`, `analyze_simulation_results.py` and `balance_analysis.py` stay. They stay unless a reason to archive them turns up, because CLAUDE.md documents them as live entry points.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and requirements
- `.planning/ROADMAP.md` § Phase 7 — goal and five success criteria
- `.planning/REQUIREMENTS.md` — FLOW-02..05, LEG-01, LEG-02
- `.planning/PROJECT.md` — Core value, constraints (numbers from config, hand-calculability), MHP timing table and workshop feedback, Key Decisions (the full list of rule changes for "Was ist neu")

### Legacy inventory
- `content/INVENTORY.md` — row-by-row disposition of every file in `final_documents/` (source for D-16), observations on intro deck slide 36
- `tests/test_inventory.py` — checks the inventory; has to follow the move

### Print pipeline (where new pages plug in)
- `content/texte.toml` § `sheets.spielleitung` — current facilitator booklet texts
- `planspiel/master.py`, `planspiel/booklet.py`, `planspiel/texbuild.py`, `planspiel/audience.py` — facilitator booklet builder, build orchestration, job-name prefix audience classification
- `planspiel/practice.py` — pattern for a top-level config block read by a single builder only (model for `content/mhp_baseline.json` isolation, D-14)
- `planspiel/validate.py` — where the schedule sum check goes (D-01)

### Rules to summarize
- `README.md` — current German rulebook (to be updated, D-20)
- `CLAUDE.md` (root) — to be rewritten in English (D-20, D-21)
- `docs/folienkonzept_spielphasen_mechtech.md` — outdated E-target check (discretion)
- `final_documents/Planspiel_Einführung + Grundlagen.pptx` — intro deck (D-18, D-19)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `planspiel print` pipeline (Jinja → LuaLaTeX, byte-reproducible, version stamp, `--check` manifest): new spielleitung pages and PDFs plug in as further jobs
- Fill-report / per-page fit proofs (cards, booklet, facilitator booklet): reuse for the one-page "Was ist neu" sheet (D-15) and the protocol template
- Veil scan by job-name prefix: `spielleitung-` documents are not veil-scanned like player documents, but "Was ist neu" must still contain no attack names if it can reach a player. Researcher should confirm it is facilitator-only.
- `rules.budget_review_delta`, `review_text.boundary_text`, `overspend_penalty`, `final_index` config: sources for the numbers on "Was ist neu"

### Established Patterns
- Numbers from `simulation_config.json`, prose from `content/texte.toml`; prose in config is a validator error
- Digit allowlist (`content/digit_allowlist.toml`): new prose must not type numbers; generated numbers go through the templates
- The committed print set is written only by the last plan of the phase (D-19 order from Phase 5)
- Config-only blocks read by a single module (practice block) are proven invisible to the rules machinery by tests

### Integration Points
- New config blocks: schedule durations (D-01, also read by the protocol template D-07); new content file `content/mhp_baseline.json` (D-14)
- `final_documents/` → `archive/` move touches `tests/test_inventory.py`, `content/INVENTORY.md`, `.gitattributes`/paths in docs

</code_context>

<specifics>
## Specific Ideas

- Test run on 2026-11-25 with a test group. All material must be printed and checked before that date.
- The MHP timing table in PROJECT.md is the reference to beat: wave 1 took 34 min there and must fit 20.
- In the debrief, data prompts should point to the clue matrix ("which clues could you have read?"), because veiling is a core learning element.

</specifics>

<deferred>
## Deferred Ideas

None. The discussion stayed within phase scope.

</deferred>

---

*Phase: 07-session-flow-handoff*
*Context gathered: 2026-11-02*
