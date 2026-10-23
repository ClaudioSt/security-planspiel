# Phase 5: Player & Facilitator Print Material - Research

**Researched:** 2026-10-23
**Domain:** Python print model, Jinja and LuaLaTeX print pipeline (A6 cards, A4 sheets, story documents), deterministic worked example and answer keys from the rules module, automated information-leak scan over pre-wave PDFs
**Confidence:** HIGH for what the existing code and toolchain do (read and probed in this session); MEDIUM for card fit and scan thresholds (the first pdf tests must prove them); LOW only where tagged `[ASSUMED]`.

Provenance tags used below: `[VERIFIED: codebase]` read in the repo this session, `[VERIFIED: probe]` measured with a command or a throw-away LuaLaTeX build in this session, `[CITED: file]` stated by a project document, `[ASSUMED]` reasoning or estimate that was not measured.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Carried forward (decided earlier, not re-asked)
- **Pipeline (Phase 4):**
  - Jinja to LuaLaTeX through `planspiel.render` / `planspiel.texbuild`, with the shared `print/planspiel.sty`.
  - Font is system Arial. Colours are the MHP theme from `content/assets/GUIDELINES.md` (accent1 `000099`; level colours L1 `00CC67`, L2 `DDEF03`, L3 `575757`).
  - The build is non-interactive and bounded, and rebuilds are byte-identical.
  - One content-hash stamp per print set appears on every page. `manifest.json` lists the documents and `planspiel print --check` checks them.
  - PDFs are committed to `final_documents/generated/` after the inputs, in the D-19 order.
  - New TeX packages go into `print/miktex-packages.txt`. The user installs them; the executor never touches MiKTeX (Phase 4 D-17). `tikzfill` is already installed for card skins.
- **Numbers:** every printed number is computed from config in code. `texte.toml` holds digit-free prose (Phase 3 D-03; digit allowlist D-10). Event effect lines are generated from event type and parameters (Phase 3 D-24).
- **Veiling:**
  - Before a wave, an attack appears only as "Angriff N", with N generated from the wave position (Phase 3 D-13, D-23, D-26).
  - Events are not veiled, but their texts must not name an upcoming attack (D-13c).
  - Measure texts may say what they defend against (D-06).
  - Measure cards show CIA values, costs and dependencies only. Wave weights and measure→attack bonus links appear only on the revealed attack worksheets (VEIL-04).
- **Story documents:**
  - Their prose is already in `[story.*]`, rewritten so it no longer names the attacks.
  - `content/clues.toml` holds the verbatim clue quotes, and SC6 checks every quote against the rendered PDF.
  - The giveaway list with the story exceptions "OT" and "Erpress*" applies (Phase 3 D-13b, D-20).
- **Clamping:** clamping KZ to 0..100 happens on the tracking sheet, not on the attack worksheet (Phase 4 D-10, deferred here).
- **Rounding:** the KZ change per wave is rounded once, half away from zero, then clamped (Phase 1).
- **Stamp builds:** a build from non-default `--config`, `--content-dir` or `--print-dir` gets "+lokal" (Phase 4 WR-07, user-confirmed option A).
- **Clean-up:** it deletes only PDFs listed in the previous manifest (Phase 4 WR-02). The hand-maintained story PDFs in `final_documents/` stay until Phase 7 (LEG-01).

### Measure and event cards (PRINT-05, PRINT-06, VEIL-04)
- **D-01:** **One card per measure level.** That makes 30 measure cards (10 measures × L1/L2/L3), as in today's deck.
- **D-02:** **Card size A6 (105×148 mm), four cards per A4 sheet**, with cut lines. Event cards and the Budget Review card use the same A6 format.
- **D-03:** **A separate legend card** in the measure deck. It is an annotated sample card with callouts for:
  - the CIA contribution and how it feeds the E-value;
  - Init vs OPEX;
  - the dependency icon (D-06);
  - the level colours.
  Ordinary cards carry no legend text.
- **D-04:** **Card text is plain plus technical.** Each card shows:
  - the measure title (id and short label from config);
  - the `focus` line and the measure `description`;
  - the plain level sentence (`levels_simple`) as the main text;
  - the technical keywords (`levels_desc`) in small print;
  - CIA contribution, Init and OPEX, generated from config.
  No wave weights, no bonus links, no attack names.
- **D-05:** **Everything per team.** Each team gets its own measure deck (30 cards plus the legend card) and its own event deck (7 events plus the Budget Review card). The build emits one deck of each, and the facilitator prints three copies.
- **D-06:** **Dependencies are shown as an icon plus id**, e.g. a lock icon with "M2 ≥ L2", generated from config and explained on the legend card. A card without a dependency shows nothing.
- **D-07:** **Single-sided printing is the default.** A plain back with a type label ("Maßnahme" / "Event" in the MHP colour) may be offered as an optional build output for duplex printing. It is not required, and it must not reveal anything (an event's name shows only on its front).
- Event cards print the narrative from `texte.toml`, the rule text where one exists, and the effect line generated from event type and parameters. The Budget Review card prints its tiers and the overspend rule generated from config, reusing `planspiel.review_text`.

### Team booklet, tracking sheet and wave explainer (PRINT-07, PRINT-08, PRINT-09)
- **D-08:** **One team booklet**, one per team, combining:
  1. budget tier choice and measure planning (today's Budget sheet: cost types, tier table, planned sum);
  2. the tracking sheet over all waves;
  3. RoS and Budget Review at the end.
  The tracking sheet replaces the old status tracker of the Budget sheet. No value is entered twice, and everything follows calculation order.
- **D-09:** **The tracking sheet has one column per wave** (Start / Welle 1 / Welle 2 / Welle 3 / Budget Review) and fits on one A4 page for the whole game. Rows follow calculation order and include:
  - start KZ;
  - KZ change from the attack worksheet, i.e. attack plus events, rounded once;
  - KZ after clamping to 0..100;
  - own costs (Init, OPEX) as separate rows;
  - external event effects (budget or OPEX effects from events) as separate rows;
  - remaining budget.
  Own costs vs external effects must be distinguishable, because RoS counts own spend only (`rules.security_spend`).
- **D-10:** **Change-window moves get their own rows on the tracking sheet**:
  - one row "Init-Differenz netto" per change window;
  - a small measure table (measure, level before / after; cancel and add included);
  - for the Kurswechsel, a row for the customer-covered Init (`rules.swap_credit`) and the team's remainder.
  The rules match Phase 2 (net, immediate, never refunded; effect and OPEX from the next wave).
- **D-11:** **"So funktioniert eine Welle" is its own A4 page** (single-sided printing, so not on a back side). It covers the flow:
  - events → attack (E-value, bonus, Gesamtreduktion, Fall 1/2/3) → recovery → KZ rounding once → clamp → change window;
  - what attacks affect vs what events affect;
  - a small flow diagram.

### Worked example "Welle 0" (FLOW-01)
- **D-12:** **The practice incident is its own practice attack in `simulation_config.json`**, with its own weights, threshold, cap, bonus measures and recovery flag. It is marked as practice:
  - it never counts toward KZ, budget, RoS, the enumeration, the balance reports or the gate;
  - its weights and bonus measures must differ from waves 1–3 so it reveals nothing about a real attack;
  - the validator and the golden digests for waves 1–3 stay unchanged.
  Research or the planner chooses the config shape (e.g. a `practice` block or a flagged wave) so that the static enumeration ignores it.
- **D-13:** **A fixed, deliberately mediocre example selection lives in config.** It lands in Fall 3, meets one bonus measure and misses another, and triggers recovery. A golden test pins every printed number against the rules module (SC3).
- **D-14:** **"Welle 0 – Übung" is a pre-printed, fully filled-in document** in the same layout as the real attack worksheets (reuse `angriff.tex.j2` / the print model with filled values), plus a filled tracking excerpt. The facilitator walks all teams through it step by step. It is its own PDF in the print set, separate from the wave explainer.
- **D-15:** **Scope of the example:**
  - one simple event with a KZ effect;
  - the attack with Fall 3 and recovery;
  - the once-per-wave rounding and the clamp;
  - the entry in the tracking sheet.
  No change window.
- **D-16:** **The practice story is drafted by Claude in `texte.toml`, and the user reviews it at a checkpoint before commit** (like Phase 3 D-13d). It must not hint at any real attack and must pass the giveaway and digit checks.

### Facilitator master sheet (PRINT-10)
- **D-17:** **Answer keys cover one typical selection per budget tier (low/medium/high) plus the Welle 0 selection**, with every intermediate value per wave. These include E-value, bonus, Gesamtreduktion, Fall, damage incl. recovery, attack KZ, events, the rounded wave KZ change, the clamp, costs, remaining budget, Budget Review, RoS and the final index. The plans live in config, and a golden test compares the sheet with the simulation (SC4).
- **D-18:** **The typical tier plans are chosen from the full enumeration** (per tier a plan near the median: in budget, middling KZ, touching as many mechanics as possible). They are proposed to the user at a checkpoint and fixed in config after approval. They must be re-chosen after the Phase 6 rebalance; record this as a Phase 6 item.
- **D-19:** **Check rows = quick-check table per wave**:
  - GR bounds for Fall 1/2/3;
  - damage and KZ at the bounds;
  - a table GR → attack KZ in whole GR steps.
  The facilitator can check any team's sheet in seconds without a reference plan.
- **D-20:** **The master sheet also contains**:
  - the clue matrix (`content/clues.toml`: quote, source document, why it points to the attack);
  - the event schedule per wave (which events after which wave, condition, effect line);
  - Budget Review tiers and the overspend rule;
  - per-wave thresholds, caps and bonus tables.
- **D-21:** **Form: one booklet** with an overview page, then one section (about a double page) per wave with parameters, check rows, events and answer keys, and finally the Budget Review and the clues. Multi-page is fine. It is facilitator-only, so it may name attacks; it is excluded from the pre-wave veil scan but must never be handed to players.

### Requirement review before planning (2026-10-23)
The game rules stay as they are: the Kurswechsel event forces exactly one swap after wave 1, and otherwise teams may make any number of changes after each wave within their own budget. The two decisions below only concern the facilitator answer keys (PRINT-10).
- **D-22:** **The answer keys follow a legal game path with change-window moves** (refines D-17 and D-18). Per tier the example team:
  - makes the mandatory Kurswechsel swap after wave 1 (`rules.swap_credit`);
  - makes one or two voluntary changes on top, e.g. a downgrade after the Sparprogramm in wave 2. The answer keys are the only fully worked example of the change-window rows on the tracking sheet, because Welle 0 has no change window (D-15).
  The base path is chosen from the enumeration's swap layer (`planspiel tausch`: in budget, near the median). The extra moves are picked by hand, and every number comes from `rules.evaluate_path`. The three paths live in config, and the user approves them at the D-18 checkpoint.
- **D-23:** **The final-index weights move into `simulation_config.json`**, unchanged at 1 and 1. Every caller of `rules.final_index` (report, balance, analyze, the master sheet) reads them from config, and simulation outputs stay identical. The master sheet prints the final index marked "vorläufig" until the Phase 6 rescale (BAL-03).

### Claude's Discretion
- **Story documents (PRINT-12):** layout follows `content/assets/GUIDELINES.md`.
  - Zeitungsartikel: "AUTO TIMES" masthead, two columns, the two images from `content/assets/images`.
  - Mails: email look with header block.
  - Steckbrief: re-evaluate the 4.0 cm top margin.
  - All on A4. Audit-Mail from its `[story.audit_mail]` transcription.
- **Veil scan (VEIL-02):** its exact mechanics.
  - Coverage: rendered text via pypdf, file names and PDF metadata of all pre-wave documents.
  - It looks for attack names, giveaway terms and wave CIA weights.
  - It needs an explicit list of which documents are pre-wave vs revealed vs facilitator-only.
- **Weights:** how "wave CIA weights" are detected in the scan (e.g. the exact weight tuples or "wC"/"× 0,4" patterns).
- **Card layout:** cut marks, card skin details, how the legend card annotates, the icon choice.
- **Template and module layout:** e.g. one template per document type, `printmodel` builders per document. Job and file names under `final_documents/generated/`; pre-wave file names must not name attacks.
- Whether the optional duplex backs (D-07) are built at all in this phase.
- How the build emits per-team copies (D-05): one PDF that the facilitator prints three times is the default.

### Folded Todos
- **"Angriffe und Aktionen nur indirekt vermitteln, nie explizit benennen"** (`.planning/todos/pending/2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md`).
  - Phase 3 delivered the veiled content and the clue matrix.
  - This phase closes the todo: the generated pre-wave material plus the automated veil scan (VEIL-02, VEIL-04).
  - Move the todo to completed when Phase 5 completes.

### Deferred Ideas (OUT OF SCOPE)

- Re-choose the typical tier reference paths and re-pin their answer keys after the Phase 6 rebalance (D-18, D-22).
- Rescale the final-index weights in config during the Phase 6 rebalance and drop the "vorläufig" mark (D-23, BAL-03).
- Session schedule, debrief questions, "Was ist neu" and the timed dry run: Phase 7 (FLOW-02..05).
- Archiving the hand-maintained docx/pptx/pdf in `final_documents/` once generated replacements exist: Phase 7 (LEG-01).

</user_constraints>


<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRINT-05 | Measure cards (10 x 3 levels) plus legend card | A6 2x2 sheet prototype built and extracted; text-length fit estimate; `rules` accessor needed because of the operand-attribute guard (F1) |
| PRINT-06 | Event cards and Budget Review card, effect lines from type and parameters | No generator exists (F6); `eventtext.py` with `effect_rows`, equivalence test against `rules.evaluate_event`; `review_text` extension |
| PRINT-07 | Budget sheet and RoS sheet | Existing keys in `[sheets.budget]`, `[sheets.ros]`, `[sheets.labels]`; legacy RoS sheet is stale against RULE-06 (F8); booklet shell |
| PRINT-08 | Tracking sheet in calculation order, own costs vs external effects | Change windows after waves 1 and 2 only; external effects = flat_budget and opex_discount; level-matrix layout; KZ 0..100 constants must come from `rules` |
| PRINT-09 | One-page "So funktioniert eine Welle" | TikZ available; generic symbols only; recovery text from `[sheets.backup_recovery]` (open question) |
| PRINT-10 | Facilitator master sheet with check rows and answer keys | `rules.path_trace` (new), reference-plan config shape, candidate finder cost, D-23 caller list, `fmt.format_approx` for the 17/7 slope |
| PRINT-12 | Four story documents from `[story.*]` | Image assets must join the hashed static set; Georgia/Times installed; clue-in-PDF check (squashed matching) |
| VEIL-02 | Automated scan of pre-wave material | Audience registry by job prefix, two-layer scan, token vs substring rules, weight-tuple detection, metadata probe |
| VEIL-04 | Cards show CIA, costs, dependencies only | Card model has no bonus or weight field; AST guard plus PDF-level checks |
| FLOW-01 | Worked example "Welle 0" | `practice` block outside `waves`/`attacks`; `practice_config` view reuses `rules` unchanged; concrete parameter set verified with `rules` |
</phase_requirements>

## Summary

Phase 4 delivered a complete, tested pipeline (config + `content/texte.toml` to `PreAttackView`/`RevealView` to `printmodel.AttackSheet` to Jinja to LuaLaTeX, stamp, manifest, `--check`). Phase 5 adds nine more print documents and one cross-cutting scanner on the same rails. Nothing in the toolchain blocks the phase: TikZ (with `arrows.meta`, `positioning`, `shapes.geometric`, `calc`, `backgrounds`, `fit`), `multicol`, `graphicx` with the two PNGs, and `tikzfill` all compile under `--disable-installer` on this machine today, so **no MiKTeX installation is needed** [VERIFIED: probe]. Two packages (`pgf`, `graphics`) only have to be added to `TEX_PROBES` and `print/miktex-packages.txt` so the preflight and the drift test know them.

The real risks are in the repo's guard rails, not in TeX. Several existing tests and structures will fail or constrain the design the moment Phase 5 code lands (section "Findings that change planning"): the AST guard that bans `.init`/`.opex`/`.weights`/`.bonus` outside `rules.py` and `config.py`; the characterization goldens that pin the whole per-wave record (so `simulate_waves` must not gain keys); hard-coded job lists in two test files (`test_print_render.py`, `test_print_model.py`); the `mini_config.json` and `mini_content` fixtures that every new text key and config block must also satisfy; the stamp that hashes all rendered `.tex` (every new document changes every PDF byte); and the fact that **no test checks the committed PDFs for freshness** (only `planspiel print --check`, run by hand). The veil scan also has traps: pypdf drops spaces, so token terms (`ot`, `sps`, `apt`) cannot be matched on PDF text; M6 legitimately prints "Phishing" (D-06); and the current revealed worksheets already pass the "does not name other attacks" check, but only when matching full attack names, not stems (wave 1 says "exfiltriert").

**Primary recommendation:** Build the audience registry and the two-layer veil scan first (VEIL-02, wave 1) so every later document is classified and scanned the moment it exists; then add documents one plan at a time in a sequential order (PRINT-05, PRINT-06, PRINT-07, PRINT-08, PRINT-09, PRINT-12, FLOW-01, PRINT-10); keep `final_documents/generated/` untouched until the last plan regenerates and commits the whole set once in the Phase 4 D-19 order.

### Findings that change planning (read first)

| # | Finding | Evidence | Consequence for the plans |
|---|---------|----------|---------------------------|
| F1 | `tests/test_single_definition.py::test_no_formula_operands_outside_rules_and_config` bans attribute access `.s_unit .base_severity .mitigation_cap .kz_at_full_damage .kz_at_full_mitigation .e_threshold .recovery .init .opex .weights .bonus .kz_per_step` in every `planspiel/*.py` except `rules.py` and `config.py`. | [VERIFIED: codebase] test lines 140-150 | Card, practice and master code cannot read `level.init`, `level.opex`, `wave.weights`, `bm.bonus`. Put a read accessor in `rules.py` (`card_facts`, `level_requirements`) and take wave numbers from `worksheet_constants` (as `printmodel.py` already does). PRINT-05 owns the accessor. |
| F2 | The characterization goldens pin the **entire** per-wave dict that `evaluate_plan` returns. | [VERIFIED: codebase] `tests/golden/characterization_*.json` contain every key of each wave record | Never add keys to `simulate_waves` / `evaluate_plan`. Add a separate `rules.path_trace` for recovery factor, Fall, rounded wave change, running budget. |
| F3 | No test compares the committed `final_documents/generated/` with the inputs. Freshness is `uv run planspiel print --check` only (D-20, manual). It currently reports fresh (stamp `2026-10-22 · 0d24b7d`). | [VERIFIED: probe] ran it, exit 0; grep of tests | Intermediate plans cannot break a test by leaving the PDFs stale. Regenerate and commit once, in the last plan. |
| F4 | The stamp hash covers all rendered `.tex` plus `planspiel.sty`. Adding one document or editing the style changes the footer of every page of every PDF and rewrites `manifest.json`. | [VERIFIED: codebase] `stamp.content_hash`, `compute_stamp` | Per-plan rebuild-and-commit would churn the whole set nine times (about 6 MB per set because the story PDF alone is 3.7 MB with the two PNGs, [VERIFIED: probe]). |
| F5 | `render_all(cfg, texts, template_dir)` has a fixed 3-argument signature that `tests/conftest.py::printed_set` wraps; `tests/test_print_render.py` (lines 52-58) and `test_print_model.py` (line 51) hard-code the 3 job names; the mini fixtures are rendered through `render_all` in `SETUPS` parametrisations. | [VERIFIED: codebase] | The first plan that registers a builder must make those tests prefix-aware. New optional inputs (clues) go in as keyword arguments with defaults. |
| F6 | There is **no** existing code that generates event effect lines for print. `rules.evaluate_event` returns internal strings such as "Gesamtbudget -20k€". Phase 3 D-24 deferred the print generator to PRINT-06. | [VERIFIED: codebase] `rules.evaluate_event` | PRINT-06 builds `planspiel/eventtext.py`. |
| F7 | `review_text.boundary_text` returns one comma-joined string; `penalty_rows` returns up to `ceil(100/X)` rows (12 today with X=9). | [VERIFIED: codebase] | Cards need structured tier rows: add `review_text.tier_rows`. Print the full lookup table in the booklet, only the rule plus tiers on the A6 card. |
| F8 | The legacy RoS sheet still lists "Summe Event-Strafen" in the cost sum. RULE-06 says event effects are excluded from RoS. | [VERIFIED: probe] docx dump; `rules.security_spend` | Do not carry that row over. RoS cost = Init + OPEX + change-window Init differences (incl. Kurswechsel). |
| F9 | Measure texts legitimately contain giveaway stems: M6 `focus`, `levels_desc.2`, `levels_simple.2` contain "Phishing"; M5 and M7 contain the token "OT". `tests/test_texts_giveaway.py::test_measure_texts_are_not_giveaway_linted` pins that measures are not linted. | [VERIFIED: probe] `giveaway_hits` run over `measures.*`; test line 234 | The VEIL-02 scan must use a narrower profile for measure cards: attack names only (D-06). Do not edit `giveaway_terms.toml` (pinned by test). |
| F10 | pypdf text extraction loses most word spaces ("EinMitarbeiter hat auf einegef..."). Existing PDF tests match whitespace-squashed text. | [VERIFIED: probe] | In the PDF layer only multi-character substring terms may be matched (squashed, lower-cased). Token terms (`ot`, `sps`, `apt`) are matched on the rendered `.tex` source layer instead. |
| F11 | Current revealed worksheets contain no full name and no weight triple of any *other* attack. They do contain the stem "exfil" (wave 1: "ggf. exfiltriert") and "datendiebstahl", so the "other attacks" check must use the full revealed names plus the `ot` + `stör` compound, not the stem list. | [VERIFIED: probe] scan of the three committed PDFs | The orchestrator's recommended check already passes; encode it as a permanent test with the name-based profile. |
| F12 | A6 x 4 does not fit an A4 page with a footer: 2 x 148 mm = 296 mm of 297 mm, 2 x 105 mm = 210 mm. | [VERIFIED: probe] prototype page | The stamp and "Seite x von y" must sit in the reserved bottom safe strip of the two lower cards, placed absolutely (hook `shipout/foreground` + TikZ overlay). The prototype extracts as "Stand ... Seite 1 von 1". |
| F13 | `Config` is a plain dataclass with no defaults after `rs`; tests build variants with `dataclasses.replace`. | [VERIFIED: codebase] `planspiel/config.py` | New config blocks (`practice`, `reference_plans`, `final_index`) are added as trailing dataclass fields with defaults, and a top-level key the loader ignores keeps enumeration, swap layer, gate, balance reports and digests unchanged (`scale_factors` reads only `waves` and `measures`). |
| F14 | `KZ` clamp bounds 0 and 100 are literals inside `rules.clamp_kz`; the tracking sheet and wave explainer must print them. | [VERIFIED: codebase] `rules.py:84-85` | Introduce `rules.KZ_MIN`/`KZ_MAX` (used by `clamp_kz`) and print from them. Same for the wave count (`len(cfg.waves)`) and `rules.base_losses`. |
| F15 | `texbuild.STATIC_FILES = ("planspiel.sty",)` is both copied into the build dir and hashed; `test_tex_read_nothing_outside_the_hashed_set` fails if TeX reads any other local file (the `.fls` lists the PNGs). `BUILD_INPUTS` deliberately excludes `content/clues.toml` and a test pins that. | [VERIFIED: probe] `.fls` of an image build; `tests/test_print_stamp.py:151-156` | PRINT-12 must extend the static set (images) and PRINT-10 must add `content/clues.toml` to `DATA_INPUTS`/`BUILD_INPUTS` and change that test knowingly. |

## Architectural Responsibility Map

This is a batch print pipeline, so the "tiers" are the layers of the repo, not web tiers.

| Capability | Primary Layer | Secondary Layer | Rationale |
|------------|---------------|-----------------|-----------|
| Every game number (costs, CIA, thresholds, tiers, practice and reference plans) | `simulation_config.json` (+ `rules.py` accessors) | - | Single source of truth; F1 forbids reading operands outside `rules`/`config` |
| Every formula, rounding, clamp, Fall, recovery, budget ledger | `planspiel/rules.py` | - | One definition (`test_single_definition.py`); print code only calls it |
| German prose (card text, sheet wording, practice story, story documents) | `content/texte.toml` | `texts.py` views | Digit-free except the reviewed allowlist; numbers generated in code |
| Effect lines, tier tables, check rows, answer keys | New print-model modules (`eventtext.py`, `cards.py`, `booklet.py`, `practice.py`, `master.py`) | `fmt.py`, `review_text.py` | Templates never compute; models carry finished strings |
| Audience classification and leak scan | New `audience.py`, `veil.py` | `texts.py` views, pdf tests | Veil by construction (models) plus verification (scan) |
| Layout (A6 deck, A4 sheets, TikZ diagrams) | `print/planspiel.sty`, `print/templates/*.j2` | - | Packages loaded per template so the probe drift test sees them |
| Reproducible build, stamp, manifest, freshness | `texbuild.py`, `stamp.py`, `cli.py` | - | Already built in Phase 4; extended only for assets and new inputs |
| Equivalence and golden proof | `tests/` (default, `-m pdf`, `-m slow`) | `tests/support/worksheet_replay.py` | Independent second encoding of the hand calculation |

## Standard Stack

### Core (all already in the repo)

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python (uv-managed) | 3.12 | Print models, rules, CLI | `pyproject.toml` `requires-python >=3.12` [VERIFIED: codebase] |
| Jinja2 | 3.1.6 | Templates with `\VAR{}`/`\BLOCK{}` delimiters, `StrictUndefined`, `finalize=tex_escape` | pinned in `pyproject.toml` [VERIFIED: codebase] |
| LuaHBTeX (MiKTeX) | 1.25.7 (MiKTeX 26.5) | PDF engine, run with `--disable-installer` | `lualatex --version` [VERIFIED: probe] |
| pypdf | 6.19.0 (dev) | Text, metadata, outline extraction in `-m pdf` tests | `pyproject.toml` dev group [VERIFIED: codebase] |
| pytest | 9.1.1 (dev) | Test runner; markers `slow`, `pdf` | `pyproject.toml` [VERIFIED: codebase] |

### Supporting (TeX packages; all present on this machine)

| Package | MiKTeX id | Needed by | Present now | Action |
|---------|-----------|-----------|-------------|--------|
| `tikz.sty` + libraries `arrows.meta positioning shapes.geometric calc backgrounds fit` | `pgf` | wave-explainer flow diagram (D-11), legend callouts, lock icon | yes [VERIFIED: probe] | add probe `tikz.sty: pgf`, add `pgf` to `miktex-packages.txt` |
| `graphicx.sty` | `graphics` | newspaper PNGs | yes [VERIFIED: probe] | add probe `graphicx.sty: graphics`, add `graphics` to the list |
| `multicol.sty` | `tools` (already listed) | two-column newspaper | yes [VERIFIED: probe] | add probe `multicol.sty: tools` (no new package id) |
| `tikzfill.sty` | `tikzfill` (already listed, not probed) | optional card skins | yes | optional probe; not needed for plain TikZ cards |
| `enumitem`, `multirow`, `longtable`, `booktabs`, `tcolorbox` | various | not required | yes | do not add unless a plan needs them |

Not available and not needed: `fontawesome5`, `pifont`, `wasysym`, `marvosym`, `bbding`, `background` [VERIFIED: probe]. Arial lacks the glyphs for the box and tick symbols U+25A2, U+2713, U+2610 (log "Missing character"), but has `≥ ≤ → ← − × ÷ € ± „ “ · ½ µ ² ° ‰ •` [VERIFIED: probe]. The lock icon (D-06) must therefore be drawn with TikZ; level badges and "M2 ≥ L2" use existing glyphs.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Plain TikZ nodes for cards | `tcolorbox` / `tikzfill` skins | More packages and probe entries for no visible gain; plain `\fcolorbox`/TikZ is enough |
| New `.sty` file per document family | Extend `planspiel.sty` with sectioned macros, packages loaded per template | A second `.sty` needs `STATIC_FILES`, hash and drift-test changes; a single sty is simpler. Packages stay out of the sty so worksheets are not slowed |
| Georgia (system) for the newspaper masthead | Arial everywhere | Georgia, Times New Roman, Cambria, Calibri and Segoe UI are installed [VERIFIED: probe]; D-16 accepted machine-dependent bytes for Arial, the same logic covers Georgia. Fallback Arial if the user prefers one font |
| Duplex card backs (D-07) | none | Recommended: skip (YAGNI). Printing is single-sided by default |

**Installation:** none for Python. For TeX, on a machine that lacks them: `miktex packages install --package-id-file print/miktex-packages.txt` (the user runs this; the executor never touches MiKTeX, Phase 4 D-17). Verified present here, so no user action is needed on this machine.

**Version verification:** `lualatex --version` -> LuaHBTeX 1.25.7, MiKTeX 26.5; `kpsewhich --miktex-disable-installer` found every file listed above [VERIFIED: probe]. `uv run pytest -q` -> 1172 passed, 43 deselected in 69 s; `uv run pytest -m pdf -q` -> 21 passed in 56 s; `uv run planspiel print --check` -> fresh [VERIFIED: probe].

## Package Legitimacy Audit

This phase installs **no** Python or JavaScript packages: Jinja2, pypdf and pytest are already pinned in `uv.lock`. The two TeX packages to add to the preflight list (`pgf`, `graphics`) are CTAN core packages that are already installed on the build machine; they are installed (if ever) from the MiKTeX repository by the user, with the installer disabled for every scripted call. The `package-legitimacy` seam covers npm, PyPI and crates only, so it does not apply.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| pgf, graphics (TeX) | MiKTeX/CTAN | decades | n/a | CTAN | n/a (not npm/PyPI/crates) | Approved, add to `print/miktex-packages.txt` |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
 simulation_config.json ──load_config──► Config ──┬─ waves/attacks/events (unchanged: enumeration, swap layer, gate, goldens)
   + practice {attack, wave, event, selection}     ├─ practice (new, ignored by all of the above)
   + reference_plans {tier: start+windows}         ├─ reference_plans (new)
   + final_index {weight_kz, weight_ros}           └─ final_index weights (new, D-23)
                                                         │
 content/texte.toml ──Texts──► PreAttackView ────────────┤  (veiled titles, measures, events, prewave sheets, story, practice)
 content/clues.toml ─────────► FacilitatorView           │  RevealView (angriff sheets only)
                                                         ▼
                 rules.py  ◄── single definition of every formula
                 (card_facts, level_requirements, path_trace, KZ_MIN/KZ_MAX, worksheet_constants, evaluate_path, evaluate_plan)
                                                         │
                 print models (finished strings only) ───┤
                 cards.py  eventtext.py  booklet.py  practice.py  master.py  story.py  printmodel.py(AttackSheet)
                                                         ▼
                 render.py: render_all ─► {job: .tex}  ─► audience.audience_of(job)   (unknown prefix = build error)
                                                         │                ▼
                                                         │        veil.scan_documents (layer 1, .tex)  ── ERROR print.veil
                                                         ▼
                 stamp.compute_stamp (hash of all .tex + static files) ─► texbuild.build_documents (LuaLaTeX, bounded)
                                                         ▼
                 final_documents/generated/<job>.pdf + manifest.json        (committed once, last plan)
                                                         ▼
                 tests -m pdf: veil layer 2 (PDF text squashed, metadata, names), fragments in PDF, fit markers, clue quotes
```

### Recommended Project Structure

```
planspiel/
  audience.py       # job-name prefix -> audience, scan profile (VEIL-02)
  veil.py           # name list, weight signatures, detex, scan_text/scan_documents/scan_pdf (VEIL-02)
  cards.py          # CardDeck/Card models: measure deck + legend (PRINT-05), event deck (PRINT-06)
  eventtext.py      # effect_rows(event) per type, grouped tiers, effect kind (PRINT-06)
  booklet.py        # team booklet pages: planning, tracking, RoS/Review (PRINT-07/08)
  wave_page.py      # "So funktioniert eine Welle" (PRINT-09)
  story.py          # four story document models (PRINT-12)
  practice.py       # practice_config view, Welle 0 model, build guards (FLOW-01)
  master.py         # facilitator master sheet model, check rows, answer keys (PRINT-10)
print/
  planspiel.sty     # + sectioned macros: card sheet, tracking rows, story (packages stay in templates)
  templates/        # karten.tex.j2, teamheft*.tex.j2, welle.tex.j2, welle0 (angriff.tex.j2 filled variant), master.tex.j2, story_*.tex.j2
tests/
  test_veil_*.py  test_cards_*.py  test_event_text.py  test_booklet_*.py  test_tracking_*.py
  test_wave_page.py  test_story_*.py  test_practice_*.py  test_welle0_*.py  test_reference_plans.py
  test_path_trace.py  test_master_*.py  test_print_documents_pdf.py (generic hygiene for every job)
```

Job names (regex `^[a-z0-9][a-z0-9_-]*$`, must not name an attack for non-revealed audiences):

| Audience | Job (file `<job>.pdf`) | Document |
|----------|------------------------|----------|
| prewave | `spieler-massnahmenkarten` | measure deck + legend (31 cards, 8 sheets) |
| prewave | `spieler-eventkarten` | 7 events + Budget Review (8 cards, 2 sheets) |
| prewave | `spieler-teamheft` | budget/planning, tracking, RoS/Review |
| prewave | `spieler-so-funktioniert-eine-welle` | wave explainer |
| prewave | `spieler-unternehmenssteckbrief`, `spieler-zeitungsartikel`, `spieler-anfrage-mail`, `spieler-audit-mail` | story documents |
| practice | `uebung-welle-0` | Welle 0 worked example |
| revealed | `angriff-1_ransomware`, `angriff-2_ot`, `angriff-3_exfil` | existing (names unchanged) |
| facilitator | `spielleitung-uebersicht` | master sheet |

### Pattern 1: Audience by job prefix, enforced at build time

**What:** one small module maps the job-name prefix to an audience; `render_all` calls it for every job and raises on an unknown prefix, so a new document cannot be added without being classified. The manifest and the folder already list job names, so the prefix is visible to the person printing.
**When to use:** always; this is the "explicit pre-wave / revealed / facilitator-only classification" the veil scan requires.

```python
# planspiel/audience.py  (new, owned by VEIL-02)
PREWAVE, PRACTICE, REVEALED, FACILITATOR = "prewave", "practice", "revealed", "facilitator"
_BY_PREFIX = (("spieler-", PREWAVE), ("uebung-", PRACTICE), ("angriff-", REVEALED), ("spielleitung-", FACILITATOR))

def audience_of(job: str) -> str:
    for prefix, audience in _BY_PREFIX:
        if job.startswith(prefix):
            return audience
    raise ValueError(f"Dokument {job!r} hat kein Zielgruppen-Präfix ({', '.join(p for p, _ in _BY_PREFIX)})")
```

Scan profile per prewave job: `spieler-massnahmenkarten` uses the **names-only** profile (F9); every other prewave and practice job uses the **story** profile (D-13b list minus the D-20 exceptions OT and Erpress*). Revealed jobs are checked against the *other* attacks only (F11). Facilitator jobs are not scanned for names but must carry the `spielleitung-` prefix.

### Pattern 2: Two-layer veil scan

| Layer | Runs in | Input | Checks |
|-------|---------|-------|--------|
| 1 (fast) | default suite and as a build gate in `planspiel print` (`ERROR print.veil`) | rendered `.tex` after a light de-TeX (drop `\commands`, braces, unescape `\&`) | attack names (`revealed.name` of all attacks), attack ids, compound `ot`+`stör`, profile stems incl. token terms with word boundaries, weight triples, strings of the revealed namespace (`bonus_reasons`, narrative), job names |
| 2 (`-m pdf`) | `printed_set` fixture | pypdf text of each built PDF (squashed, NFC, lower-case), `metadata`, `xmp_metadata`, `outline`, annotations; file names; `manifest.json` | substring terms only (F10), weight triples (digit-token windows plus joined form), revealed strings, metadata empty/neutral |

Weight detection that avoids the false positives of single values like "0,2" (recovery factors, other numbers): extract number tokens `\d+(?:,\d+)?` from the **raw** extracted text and flag any window of three consecutive tokens equal to the formatted `(w_c, w_i, w_a)` of a real wave; additionally flag the joined form (`"0,40,40,2"`) in the squashed text, which covers table cells whose spaces were lost. Take the triples from `rules.worksheet_constants(cfg, wave)` formatted with `fmt.format_number` (F1 forbids `.weights`). Also flag `w[CIA]\s*[=:]?\s*\d,\d` (a symbol with a value) in prewave text. The generic symbols `wC wI wA` and "E-Wert = C · wC + I · wI + A · wA" are legal on the legend card and the explainer because they carry no values. Today's triples: (0,4 0,4 0,2), (0,2 0,2 0,6), (0,5 0,3 0,2) [VERIFIED: codebase]. A probe over the three committed revealed PDFs found none of the *other* waves' triples [VERIFIED: probe].

Model-level guard (cheap, default suite): an AST test lists the pre-wave builder modules (`cards.py`, `eventtext.py`, `booklet.py`, `wave_page.py`, `story.py`) and fails if they reference `RevealView`, `worksheet_constants`, `bonus_measures`, `bonus_reasons` or `FacilitatorView`. `practice.py` and `master.py` are exempt by design and covered by the PDF layer instead.

### Pattern 3: Card deck on an A4 sheet (prototype verified)

Zero-margin page, four A6 cells placed from the top-left corner, a bottom safe strip reserved in each card, stamp and page counter drawn in that strip by a shipout hook. This compiled in two passes under `--disable-installer` and extracted as `Karte 00 ... Stand test Seite 1 von 1` [VERIFIED: probe].

```latex
% Source: probe in this session (LuaHBTeX 1.25.7), adapt in print/planspiel.sty + karten.tex.j2
\documentclass[a4paper,10pt]{article}
\usepackage{planspiel}\usepackage{tikz}
\newgeometry{left=0pt,right=0pt,top=0pt,bottom=0pt,nohead,nofoot}\pagestyle{empty}
\makeatletter\AtEndDocument{\immediate\write\@auxout{\string\newlabel{LastPage}{{}{\thepage}}}}\makeatother
\AddToHook{shipout/foreground}{\begin{tikzpicture}[remember picture,overlay]
  \node[anchor=south west,font=\scriptsize,text=mhpgrey] at ([xshift=7mm,yshift=3.5mm]current page.south west){\footerstamp};
  \node[anchor=south east,font=\scriptsize,text=mhpgrey] at ([xshift=-7mm,yshift=3.5mm]current page.south east){Seite \thepage\ von \pageref{LastPage}};
\end{tikzpicture}}
% four cells: anchor=north west at current page.north west shifted by (col*105mm, -row*148mm), each a 105x148 mm box
```

Geometry: card 105 x 148 mm, safe margin about 7 mm, text area about 91 x 134 mm, bottom 8 mm strip reserved for the footer. 31 measure cards fill 8 sheets (last sheet 3 cards); 8 event cards fill exactly 2 sheets. Cut lines: thin grey lines through the page centre plus short ticks at the page edges (printers cannot print to the edge, so the outer edge of each card is the paper edge). The existing check "exactly one stamp per page and `Seite x von y`" (`test_print_stamp_pdf.py`) stays valid with one footer per sheet; if the user wants the stamp on every card, that test must be relaxed for card jobs (open question Q4).

Fit estimate `[ASSUMED]` (to be proven by the log markers below): the longest measure card (M4 L3) carries 385 characters (focus 46, description 159, `levels_simple` 133, `levels_desc` 47). At 9 pt Arial about 55 characters fit a 91 mm line, so body text is about 9-10 lines (about 45 mm) plus title block 15 mm, CIA/cost block 25 mm, dependency line 8 mm: about 100-115 mm of 134 mm. The longest event card is Kurswechsel (narrative 245 + rule 752 characters, about 18 lines, about 80 mm at 9 pt, 8.5 pt as fallback). Fallbacks if a card overflows: 8.5 pt body, `levels_desc` at 7 pt, drop `focus` below the title into the subtitle line. **Proof mechanism:** emit `\typeout{PLANSPIEL-CARD id=<id> used=<pt> limit=<pt>}` per card (same idea as `\fillreport` for pages) and assert used <= limit for all cards in a `-m pdf` test; also assert no `Overfull \hbox` in the log.

### Pattern 4: Effect rows from event type and parameters, proven against the simulation

`eventtext.effect_rows(event, cfg)` returns structured rows per `event.type` (all seven config types plus `final_budget_tier`), and each row carries the exact value the simulation must produce. The test builds a matching selection per row and compares with `rules.evaluate_event` (the pattern recommended in `.planning/research/ARCHITECTURE.md`, Pattern 3).

| Type (config) | Printed effect lines | Kind (for tracking rows) |
|---------------|----------------------|--------------------------|
| `kurswechsel` | rule text (exists) + generated "im Change-Fenster nach Welle N" (N from `rules.kurswechsel_wave`) | window rule, own cost via swap credit |
| `opex_discount_per_active_measure` | "OPEX-Kosten −2.000 € pro aktiver Maßnahme" (`fmt.format_money(opex_per_measure * 1000)`) | **external** (opex) |
| `flat_budget` | "Gesamtbudget −20.000 €" | **external** (budget) |
| `checklist_tier` | heading (exists) + measure list "M1 IAM/PAM ..." (config `name`) + rows "0 erfüllt → KZ −15", "2–3 erfüllt → KZ ±0": merge adjacent tiers with equal value; upper bound is `len(measures)` | KZ (goes into "KZ Events") |
| `measure_level_tier` | one row per level with `tier_labels` text and generated "KZ −5" | KZ |
| `level_bonus_per_measure` | "Für jede Maßnahme auf Level 3: +5 KZ" | KZ |
| `and_condition` | "Wenn M1 ≥ Level 2 und M6 = Level 0 → KZ −10" (clauses `min_level` -> "≥", `level_eq` -> "=") | KZ |
| `final_budget_tier` | `review_text.tier_rows` (new) plus the overspend rule from `rules.penalty_params`; full lookup via `penalty_rows` in the booklet | KZ at review |

The "Kind" column also answers which event effects are external for the tracking sheet (PRINT-08) and the master event schedule (PRINT-10).

### Pattern 5: Practice (Welle 0) as a configuration view, not a fork of the rules

Top-level key `practice` that `load_config` stores in a trailing `Config.practice` field and **nothing else reads**. A helper builds a throw-away `Config` whose only wave is the practice wave, then every existing function works unchanged. Probe result: with the view below, `rules.worksheet_constants`, `rules.simulate_waves` and `rules.evaluate_plan` ran and reproduced a Fall-3 example [VERIFIED: probe].

```python
# planspiel/practice.py (sketch, verified in a throw-away script)
def practice_config(cfg):
    p = cfg.practice
    tier = BudgetTier("practice", p.budget, p.kz_start, Fraction(1))
    return dataclasses.replace(
        cfg,
        attacks={**cfg.attacks, "practice": p.attack},
        waves=[p.wave],                     # Wave(0, "practice", weights, e_threshold, bonus_measures)
        events={p.wave.wave_id: [p.event]},
        final_events=[],
        budget_tiers={"practice": tier},
    )
```

Why the real machinery ignores it: `Config.waves/attacks/events` are untouched, `scale_factors` reads only `waves` and `measures`, the digests and characterization goldens come from the enumeration, and the validator gets a separate `check_practice`. The practice weights must have denominators dividing `cfg.ws` (10 today) so `ws` does not change.

### Pattern 6: `rules.path_trace` for answer keys (do not touch `simulate_waves`)

`rules.evaluate_path` exposes per wave: `selection`, `cia`, `e_value`, `bonus_reduction`, `gesamtreduktion`, `capped_reduction`, `severity`, `damage` (k€, after recovery), `kz_delta_attack` (Fraction), `events[]` (`kz_delta`, `budget_delta`, `opex_delta`), `kz_after`; plus `windows[]` (`swap`, `cost`), `costs{init, window_costs, opex_by_wave, security_spend, event_opex, event_budget, total, budget_available, remaining}`, `final_events[0].kz_delta`, `kz_pre_review`, `kz_final`, `ros` [VERIFIED: probe, output printed for a swap path]. D-17 additionally lists values it does not expose: recovery factor, the Fall, damage before recovery, the rounded wave KZ change, KZ before and pre-clamp, and the running remaining budget per wave. Add one read-only function in `rules.py` that derives them from the same primitives (`compute_recovery`, `worksheet_constants` for the bounds, `damage_euros`, `wave_kz_change`, `clamp_kz`, `budget_ledger`), tested against `evaluate_path` (final remaining must equal `costs.remaining`). The independent second encoding for the golden test is `tests/support/worksheet_replay.replay_steps`, which already returns `case`, `damage_before_eur`, `damage_eur`, `kz_attack`, `change` from the printed constants only.

### Anti-Patterns to Avoid

- **Arithmetic or rounding in templates or model strings.** Everything is a finished string from a model field; `tex_escape` rejects non-strings (`Fraction`, `int`, `bool` raise `TypeError`) [VERIFIED: codebase].
- **Reading `level.init` / `wave.weights` in print modules.** Trips F1; use accessors.
- **Adding keys to `simulate_waves`/`evaluate_plan` records.** Breaks the characterization goldens (F2).
- **Using `evaluate_plan` (static reference plan) for answer keys.** It ignores the forced Kurswechsel swap; use `evaluate_path` (D-22).
- **Matching token terms on squashed PDF text.** `ot`, `sps`, `apt` match inside ordinary words after squashing (F10).
- **Rebuilding into `final_documents/generated/` mid-phase.** Use `uv run planspiel print --out-dir build/preview` for visual checks (the out-dir is not a stamp input; build dir `build/` is gitignored).
- **Rounded numbers on player sheets.** `fmt.format_number` raises on non-terminating values by design; only the facilitator sheet may print an explicitly marked approximation (`fmt.format_approx`, PRINT-10).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| German numbers, money, percent, signed values | new formatters in templates | `fmt.format_number/format_signed/format_money/format_percent/format_factor` | exactness guard, real minus, thousands dot |
| Tier text for the Budget Review | string assembly in the model | `review_text.boundary_text`, `penalty_rows`, new sibling `tier_rows` | RULE-07 inclusive boundaries are tested there |
| Which requirements apply at a level | a second `if level >= dependency["level"]` loop | `rules.level_requirements` next to `_requirements_met` | one definition of the rule |
| Wave constants (threshold, cap, bonus rows, slope, recovery rows) | re-derive from config | `rules.worksheet_constants` | already guarded by D-06 |
| TeX-safe escaping | manual `\&` handling | `render.tex_escape` via `finalize` | covers `"` shorthand and ligatures (CR-01) |
| Paper rounding / clamp | `round()` or `min/max` | `rules.wave_kz_change`, `rules.clamp_kz` (`round()` is banned in `rules.py`/`rounding.py`) | half away from zero |
| Hand-calc replay | a new replay | `tests/support/worksheet_replay.py` | independent encoding with negative controls |
| PDF text matching | exact-string compare | squash whitespace on both sides, NFC (pattern in `test_print_worksheets_pdf.py`) | pypdf drops spaces (F10) |
| Version stamp, manifest, freshness | new mechanism | `stamp.py` | extend inputs only |
| Candidate search for near-median reference plans | a 4-minute swap-layer rerun inside tests | static `enumerate_tier` (about 42 s per tier) + `evaluate_path` on the few legal swaps of a handful of starts | see PRINT-10 |

**Key insight:** every number on a new sheet must be reachable from `rules` or `worksheet_constants`; every new text must be digit-free in `texte.toml`. The cheapest way to stay inside both rules is to give each new sheet a model dataclass with finished strings and a `printed_fragments()` method, as `AttackSheet` does, and let the pdf test assert those fragments appear in the PDF.

## Per-Requirement Guidance (one section per PLAN.md)

Each section lists scope, verified facts, shared items owned, RED tests to write first, pitfalls and acceptance. Order and dependencies follow in "Plan Order".

### VEIL-02: Automated scan of pre-wave material (wave 1, owns the audience registry)

- **Scope:** `audience.py`, `veil.py`, build gate in `cli._print_command`, tests; classification of the three existing revealed jobs; names-only profile for measure cards.
- **Facts:** see F9, F10, F11, Pattern 1 and 2. PDF metadata of built PDFs is empty: `PdfReader.metadata == {}`, `xmp_metadata is None`, `outline == []`, and image builds contain no file names or `PTEX` strings [VERIFIED: probe]. `PreAttackView.sheet()` only accepts `PREWAVE_SHEETS = (budget, ros, backup_recovery, labels)`; each later plan adds its sheet names there, and `PreAttackView.strings()` (basis of the leak tests in `tests/test_texts_views.py:149` and `tests/test_story_veil.py:137,144`) must include them.
- **Owns:** registry, scan, build gate, the "revealed N does not name attacks other than N or print their weights" permanent test, the rule that `render_all` raises for an unclassified job. Later plans only add rows.
- **Does not own:** the generic "no `Missing character`, no `Overfull \hbox` in any job log" test (PRINT-05, first new document).
- **RED tests:** (1) `audience_of` for each prefix and an unknown prefix raises; (2) completeness: every job from `render_all` on the real config has an audience; (3) injecting "Ransomware", "Datenexfiltration", "OT-Störung", a real weight triple, a `bonus_reasons` string into a prewave synthetic `.tex` is reported, the same string in an `angriff-` job for its own wave is not; (4) revealed job N reports attacks other than N; (5) weight window rule on text with spaces lost; (6) a token term (`ot`) is matched at layer 1 only; (7) AST guard for prewave modules; (8) `-m pdf`: metadata/outline/xmp clean for every job; (9) file names and manifest keys of non-revealed jobs contain no attack name.
- **Pitfalls:** de-TeX must keep word boundaries (replace commands by spaces); NFC and `normalize_for_matching` already exist in `texts.py`; the wave explainer and legend legitimately contain `wC wI wA`.
- **Acceptance:** `uv run pytest tests/test_veil_*.py -q`, `uv run pytest -m pdf tests/test_veil_pdf.py`, `uv run planspiel texts`.

### PRINT-05: Measure cards and legend (owns the card layout, the rules accessor, TikZ probe)

- **Scope (D-01..D-07):** 30 level cards + 1 legend card, 31 cards on 8 A4 sheets, one PDF `spieler-massnahmenkarten`; per card title (`M1: IAM/PAM` from config `name`), `focus`, `description`, `levels_simple` (main text), `levels_desc` (small), C/I/A contribution, Init, OPEX, dependency (lock icon + "M2 ≥ L2") only where a requirement applies at that level (config: `dependencies[].level` is the first level at which the requirement holds; M1 L3 -> M2 ≥ 2, M3 L3 -> M2 ≥ 2, M7 L3 -> M2 ≥ 1; every other card shows nothing) [VERIFIED: codebase].
- **Shared items owned:** `rules.card_facts(measures, measure_id, level)` returning cia/init/opex and `rules.level_requirements(measure, level)` (F1); sheet macros in `planspiel.sty`; `karten.tex.j2` as a generic deck template (cards carry a `kind` and a list of blocks so PRINT-06 reuses it); TEX_PROBES `tikz.sty: pgf` and `pgf` in the package list; the generic hygiene test over all jobs; first prefix-aware change to the three test files with hard-coded job lists (F5); mini-fixture rule below.
- **Legend card (D-03):** a real sample card (suggest M1 L3 so the dependency shows) with numbered TikZ callouts and a legend list: CIA contribution and how it enters the E-value (symbolic `E-Wert = C · wC + I · wI + A · wA`, no values), Init vs OPEX, dependency icon, level colours (L1 `00CC67`, L2 `DDEF03`, L3 `575757`; `\levelbadge` exists, IN-04: add an `\else` error branch). Callout digits come from the model.
- **Unit convention:** print euros (`30.000 €`, `4.000 € je Welle`) because RoS and damage are in euros and sheet sums must not mix units (open question Q3; legacy cards used k€).
- **VEIL-04 here:** the card dataclass has no field for bonus, weights, wave or attack; test: no card string equals a `bonus_reasons` string; PDF layer: no weight triple.
- **Mini fixtures:** `tests/fixtures/mini_config.json` has only M1, M2, M4, M6 and mini texts must satisfy `required_keys`. Add every new `sheets.*` key to `tests/fixtures/mini_content/texte.toml` in the same commit (values may be short placeholders), and keep `SETUPS`-parametrised tests green with 4 measures (13 cards: 12 + legend).
- **RED tests:** card count and order (31); per card fragments (cia, init, opex strings) equal `rules` values for all 30; dependency shown exactly on the three cards above; no digit in new texts (`uv run planspiel texts`); template variables are plain names (extends `test_template_variables_are_plain_names`); `-m pdf`: 8 pages, each page has stamp and "Seite x von 8", fit markers `used <= limit`, no `Missing character`/`Overfull`; preflight drift test updated.
- **Pitfalls:** 1 mm of vertical slack only; keep text clear of the bottom strip; `tex_escape` of names with `&` ("Logging & SIEM/MDR"); long unbreakable tokens in 91 mm (hyphenation is off by design, check the log); TikZ `remember picture` needs two passes (the pass loop does this).
- **Acceptance:** `uv run pytest tests/test_cards_*.py -q`, `uv run pytest -m pdf tests/test_cards_pdf.py tests/test_print_documents_pdf.py`, `uv run planspiel print --out-dir build/preview`, then a human prints one sheet (physical check of cut and legibility; cannot be automated).

### PRINT-06: Event cards and Budget Review card (owns `eventtext.py`)

- **Scope (D-05, D-07):** 7 event cards + Budget Review card (8 cards, 2 sheets, one PDF `spieler-eventkarten`), reusing the PRINT-05 deck template. Header "Event · Welle N" from the config wave key (legacy "Event: Nach Welle N" is the same schedule); narrative and rule from `texte.toml`; effect lines from Pattern 4. Events: wave 1 kurswechsel, operative_unterstuetzung; wave 2 sparprogramm, oem_audit, kritische_schwachstelle; wave 3 exzellenz_bonus, nervige_authentifizierung; `final_events.budget_review` [VERIFIED: codebase].
- **Budget Review card:** narrative + `rule` + tier rows (`review_text.tier_rows`) + overspend rule ("−9 KZ je angefangene 10.000 € Überziehung", from `penalty_params`). The 12-row lookup (`penalty_rows`) goes to the booklet (PRINT-07), not onto the A6 card.
- **Owned shared items:** `eventtext.effect_rows`, the effect "kind" classifier (consumed by PRINT-08, FLOW-01, PRINT-10), `review_text.tier_rows`, PreAttackView additions for events if needed, the equivalence tests.
- **RED tests:** for every event and every row, build a selection and assert `rules.evaluate_event(...)[0]` (or the budget/opex component) equals the row value: checklist counts 0..5, M7 levels 0..3 (`tier_labels` keys must equal the tier keys), level-3 count, and-condition true/false, flat budget, opex discount (needs `n` active measures), Budget Review remaining values at every boundary and below zero via `rules.budget_review_delta`; grouped checklist rows cover each count exactly once; card text contains no attack name (story profile) and no digit in prose.
- **Decision needed (Q5):** `[sheets.backup_recovery]` (title, subtitle, narrative, level labels) is in `PREWAVE_SHEETS` but D-05 lists 7 events + Budget Review. Recommendation: no ninth card (8 cards fill exactly 2 sheets); use the narrative and the generated M4 recovery table on the wave explainer (PRINT-09). The legacy slide carried a "Welle 1" badge, which would also hint which waves have recovery.
- **Pitfalls:** Kurswechsel text is long (about 1000 characters, F12 estimate); the `rule` of Operative Unterstützung is a fragment ("Zählt für jede bestehende Maßnahme in der kommenden Runde") that must be followed by the generated line; tier merge must respect `_tier_lookup` semantics (highest tier whose minimum <= value).
- **Acceptance:** `uv run pytest tests/test_event_text.py tests/test_event_cards.py -q`; `-m pdf` fit markers.

### PRINT-07: Budget sheet and RoS sheet (owns the booklet shell)

- **Scope (D-08 parts 1 and 3):** `spieler-teamheft`: page 1 budget and planning (intro, cost-type table Init/OPEX with "Was ist das?/Wann fällig?", tier table `Tier | Verfügbares Budget | KZ Start` from `budget_tiers`, planning table), the tracking page is inserted by PRINT-08, last page RoS and Budget Review. Existing keys cover most wording: `sheets.budget.*`, `sheets.ros.*`, `sheets.labels.*` (including tracker labels such as `status_tracker`, `kz_cumulative`, `damage_wave`) [VERIFIED: codebase].
- **Design to avoid double entry (D-08):** the planning table (measure, Level, Init, OPEX, sums, "Antizipierte Summe = Init + OPEX x number of waves" with the wave count from `len(cfg.waves)`) is the only place the start levels are written; the tracking page records only changes. Tier names via `str.capitalize()` of the config key (Low/Medium/High).
- **RoS page:** `Gesamt Init-Kosten`, `Init-Differenzen aus Change-Fenstern (inkl. Kurswechsel)`, `Gesamt OPEX` -> eigene Kosten; `Schaden Angriff 1/2/3` (veiled titles via `PreAttackView.attack_title`); `Vermiedener Schaden = 620.000 − Summe der Schäden` with 620.000 from `rules.base_losses` (not typed); `RoS = (Vermiedener Schaden − eigene Kosten) ÷ eigene Kosten`; **no event-penalty row** (F8). The Final-Index is not on the player sheet (facilitator comparator).
- **Budget Review block:** `Restbudget = Tier-Budget + Budget-Events − eigene Kosten − Event-OPEX` (events are external, can be negative), tier table, full overspend lookup from `penalty_rows` (12 rows today; add a build guard on a maximum row count because Phase 6 changes X).
- **Shell:** `teamheft.tex.j2` includes partials `teamheft_budget.tex.j2`, `teamheft_ros.tex.j2`; PRINT-08 adds `teamheft_tracking.tex.j2` between them, so the two plans do not edit the same template body.
- **RED tests:** fragments equal config (tier budgets, KZ starts, base losses, penalty rows vs `review_text.penalty_rows`); no event-penalty row; pages stay on their sheet; `-m pdf` page count and stamp.
- **Acceptance:** `uv run pytest tests/test_booklet_*.py -q`, `-m pdf`.

### PRINT-08: Tracking sheet (adds the tracking page to the booklet)

- **Structure facts [VERIFIED: codebase]:** change windows exist after waves 1 and 2 only (`evaluate_path` allows at most `len(waves) − 1` windows; window i follows wave i+1; no window after wave 3, the Budget Review follows). The Kurswechsel (wave 1 event) forces exactly one Maßnahmentausch in window 1; any number of voluntary changes are allowed in both windows. External effects: `opex_discount_per_active_measure` (wave 1, −2.000 € x active measures, `event_opex`) and `flat_budget` (wave 2, −20.000 €, `event_budget`); both change the budget but not RoS (`rules.security_spend` excludes them). KZ-type events feed "KZ Events" on the attack worksheet, not the budget rows.
- **One-page layout (D-09, D-10), columns Start | Welle 1 | Welle 2 | Welle 3 | Budget Review, rows in calculation order:**
  1. KZ vor der Welle (Start column: Start-KZ from the chosen tier)
  2. KZ-Änderung der Welle (from the attack worksheet, already rounded once)
  3. KZ nach der Welle, begrenzt auf `KZ_MIN` bis `KZ_MAX` (F14)
  4. Schaden der Welle (feeds RoS)
  5. Block "Eigene Kosten (zählen für den RoS)": Init (Start), OPEX dieser Welle, Init-Differenz netto (windows after waves 1 and 2)
  6. Block "Externe Effekte (zählen nicht für den RoS)": Event: Budget, Event: OPEX; cells that no event of that wave can fill are shaded, derived from the effect kind (Pattern 4)
  7. Restbudget (laufend)
  8. Review column: Restbudget, KZ-Änderung Review, KZ final
  Window block per window: a measure grid M1..M10 x (Level nach Fenster 1, Δ Init, Level nach Fenster 2, Δ Init) for any number of moves, blank = unchanged; rows "Summe Init-Erhöhungen", "Kurswechsel: Gutschrift Kunde" (Init of the dropped measure at its wave-1 level, capped at the Init of the incoming measure: `rules.swap_credit`), "Init-Differenz netto = Erhöhungen − Gutschrift, nie eine Erstattung". About 30 writable rows at 6-7 mm fit the 257 mm text height; prove it with the `\fillreport` log marker (`used <= text`).
- **Owned shared items:** `rules.KZ_MIN/KZ_MAX`; the row model (`TrackingRow`) that FLOW-01 reuses for its two-column excerpt; vocabulary labels "GR" introduced explicitly (IN-02).
- **RED tests:** row order equals calculation order; shaded cells equal event kinds per wave; the number of window blocks equals `len(waves) − 1`; the swap-credit sentence uses `rules.swap_credit` semantics (test with a worked Kurswechsel from `evaluate_path`: Δ rows sum to `windows[0]["cost"]`); `-m pdf`: one page for the tracking part, fragments present.
- **Pitfalls:** do not print any wave weight or bonus link here; do not add "Final-Index"; the Init paid at the start belongs to the Start column, not to wave 1.

### PRINT-09: "So funktioniert eine Welle" (one A4 page)

- **Scope (D-11):** `spieler-so-funktioniert-eine-welle`, one page: sequence Events -> Angriff (E-Wert, Bonus, Gesamtreduktion, Fall 1/2/3) -> Recovery -> KZ einmal runden -> begrenzen -> Change-Fenster, a TikZ flow diagram, and a two-column "Angriffe wirken auf Schaden und KZ / Events wirken auf KZ, Budget, OPEX" table. Symbols only (`wC wI wA`, `Schwelle`, `Kappung`); no wave values, no attack names.
- **Content sources:** step vocabulary from the worksheet (`sheets.angriff.step_*`, `sheets.labels.*`) so the page and the tracking rows use the same words; the recovery explanation from `[sheets.backup_recovery]` with the table generated from the M4 levels (open question Q5); generic Fall explanation from `sheets.angriff.cap_intro`-style prose (move digit-free text only).
- **Pitfalls:** state the rounding rule via the allowlisted `,5` token only where `wave_kz_rounding` already does; the page must not hint which waves allow recovery.
- **RED tests:** page count 1 (fill marker), no real weight triple, no attack name, all step headings present, probe list updated.

### PRINT-12: Story documents (owns asset handling in the static set)

- **Scope:** four jobs from `[story.*]`; layout per `content/assets/GUIDELINES.md` (Steckbrief A4, margins 2.5 cm left, re-evaluate the 4.0 cm top margin: no header template is carried, so use the standard top margin; Zeitungsartikel masthead "AUTO TIMES" 48 pt serif, two columns via `multicol`, the two images; mails with an e-mail header block; Audit-Mail from its transcription).
- **Content shapes [VERIFIED: codebase]:** `story.steckbrief.*` sections with `heading`, `text`, `bullets`, nested `it_ot_landschaft.*`; `story.zeitungsartikel` has `kopfzeile`, `ticker`, `fusszeile`, `meldung_audit` and `bericht_vorfall` (`headline`, `dateline`, `lead`, `caption`, `ablauf`, `folgen`); `story.anfrage_mail` and `story.audit_mail` have `kopf` (`von`, `an`), `anrede`, paragraphs, `gruss.lines`, `fusszeile.lines`. The mail `kopf` values contain straight quotes and angle brackets; `tex_escape` turns `"` into `\textquotedbl{}`, so they print straight (acceptable; do not "fix" them in the template).
- **Assets (F15):** the PNGs are RGB 8-bit 1448 x 1086 (1.7 and 2.0 MB); a build with both gives a 3.7 MB PDF, byte-identical across runs, no file names or XMP in the PDF [VERIFIED: probe]. The `.fls` lists the PNGs as local inputs, so they must be copied into the build dir, hashed (`content_hash` static files) and allowed in `test_tex_read_nothing_outside_the_hashed_set`. Extend `texbuild`/`stamp` with an asset mapping (do not let content-provided strings choose file names: fixed names only), add `content/assets/images` to `DATA_INPUTS` and `BUILD_INPUTS`, and add a graphics probe. Optionally downscale copies to about 200 dpi at 8 cm width (about 630 px) to cut the PDF size, recorded in the assets README; not required.
- **SC6 check:** every clue in `content/clues.toml` must appear in the rendered PDF. Match the squashed NFC quote against the squashed text of the PDF for its source document (`story.<doc>` -> job; `measures.*` -> card deck). Do not upper-case anything (`check_clues` is case-sensitive; the headline "Erpresser legen Zulieferer tagelang lahm" must print as stored). pypdf returns column text in stream order, so a quote crossing a column or page break stays contiguous after squashing.
- **Fonts:** Georgia, Times New Roman, Cambria, Calibri, Segoe UI are installed [VERIFIED: probe]; select by name, never by path (same rule as Arial). Arial remains the default.
- **RED tests:** every clue quote in PDF; images present (two image XObjects in the newspaper); two-column page count; veil layer 1 and 2 clean under the story profile; no `Missing character`.
- **Pitfalls:** headings from toml keep their case; avoid `\MakeUppercase`; keep `\hyphenpenalty` rule (no hyphenation) and use `\raggedright` in 8 cm columns; check `Overfull \hbox`.

### FLOW-01: Welle 0 worked example (owns `practice`)

- **Config shape (D-12):**

```json
"practice": {
  "kz_start": 98, "budget": 200,
  "attack": {"base_severity": 6, "s_unit": 20, "kz_at_full_damage": -6, "kz_at_full_mitigation": 9,
             "cia_impact": {"c": -1, "i": -1, "a": -1}, "mitigation_cap": 6, "allow_recovery": true},
  "wave": {"weights": {"c": 0.3, "i": 0.3, "a": 0.4}, "e_threshold": 18,
           "bonus_measures": [{"measure": "M9", "min_level": 2, "bonus": 4}, {"measure": "M10", "min_level": 2, "bonus": 3}]},
  "event": {"id": "uebung_ereignis", "name": "Übung", "type": "measure_level_tier", "measure": "M2",
            "tiers": {"0": -4, "1": -2, "2": 1, "3": 3}},
  "selection": {"M1": 0, "M2": 0, "M3": 0, "M4": 1, "M5": 0, "M6": 0, "M7": 0, "M8": 2, "M9": 2, "M10": 1}
}
```

  These parameters were run through the real rules in a throw-away script that builds the practice view (Pattern 5) and calls `worksheet_constants` and `evaluate_plan` [VERIFIED: probe]. Results: threshold 18, cap 6, upper 24; weights (0,3 0,3 0,4) differ from every real wave, also as a multiset; bonus measures M9 and M10 are used by none of waves 1-3 (D-12 distinctness); slope (9 − (−6)) / 6 = 5/2, printed "× 2,5" (terminating, so it passes the D-08/D-09 guards; the half-distance guard `min_half_distance` returns 1/4, well above 1/100). The example selection M4 L1, M8 L2, M9 L2, M10 L1 (Init 104.000 €, OPEX 23.000 € per wave, inside the 200.000 € practice budget) gives CIA 16 / 22 / 19, E-value 19, M9 L2 meets its bonus (+4), M10 L1 misses (needs L2), Gesamtreduktion 23 -> Fall 3, damage (24 − 23) x 20.000 = 20.000 € before recovery and 18.000 € after M4 L1 (r = 10 %), attack KZ +6,5, event (M2 on level 0) −4, wave KZ before rounding +2,5. An exact half teaches the rule and distinguishes half away from zero (+3) from half to even (+2); start KZ 98 + 3 = 101 triggers the clamp to 100. **The executor must re-run the search and pin the final numbers; the set above illustrates the feasible region (a search over thresholds 18 to 22, Init up to 130.000 € and the selection space of M2..M10 found 24 sets with a positive exact half in Fall 3).** Required properties as build guards (`PrintModelError`): Fall 3, one bonus met and one missed, recovery factor > 0, non-integer wave KZ before rounding, clamp active, hand-calc shape (D-06).
- **Validator (`check_practice`, raw dict):** schema like `attacks.*`/`events`, selection covers all measure ids with valid levels, weights not equal to any wave (as ordered tuple or multiset), bonus measures disjoint from every real wave's bonus measures, weight denominators divide `ws`, `practice` not present in `attacks`/`waves`. Deep checks that need `rules` (Fall 3 etc.) live in `practice.py` and tests.
- **Texts (D-16):** a `[practice.*]` section (not `attacks.practice.*`, so `required_keys` loops and the revealed namespace stay clean): title "Welle 0 – Übung", narrative, `cia_rationale`, three case texts, `bonus_reasons.M9/M10`, event narrative and `tier_labels`. Declared through `required_keys` when `cfg.practice` exists; strict digit lint applies (not exempt like `story`); `check_giveaway` needs the new prefix in its `scoped` list with the story profile; reviewed by the user at a checkpoint before commit. Suggested incident (not near any real attack): a lost company smartphone and a misconfigured cloud share are close to exfiltration; prefer an incident about a failed hardware or a mis-sent internal mail (to be drafted, user decides).
- **Rendering (D-14):** reuse `angriff.tex.j2` with a filled variant: `Box` gains an optional `value`; the `fillline` macro prints the value instead of an empty box; the CIA table gets filled rows (the example's measures) and a sum row; `build_attack_sheet` takes the practice texts through a small adapter (today it reads `attacks.<id>.revealed.*` via `RevealView`). Real sheets must render byte-identically (value `None`). The document adds a page with the example selection table (via `rules.card_facts`) and the event with its `eventtext` rows, and a two-column tracking excerpt reusing the PRINT-08 row model.
- **Golden test (SC3):** (a) recompute with `rules.evaluate_plan(practice_config(cfg), "practice", selection)` and `replay_steps` and assert every printed fragment equals the result; (b) a small pinned `tests/golden/welle0.json` so a change to the practice block shows as a visible diff; (c) mutation test: change a practice weight in a copy of the config and the printed E-line changes.
- **Ignored by the rest (D-12), each proven by a test:** enumeration count unchanged (782,336 valid per tier from the digest), `rules.base_losses` still 620, gate and balance untouched, `scale_factors` unchanged, `planspiel validate` clean.
- **Scan class:** `uebung-welle-0` is `practice`: story profile, must contain no real weight triple, may contain its own.
- **Mini fixtures:** the mini config lacks M9/M10. Either extend `mini_config.json` with a practice block using only M1/M2/M4/M6 (bonus measures must still be disjoint from the mini waves: mini wave 1 uses M4 and M6, so use M1/M2) or let the builder return `{}` when `cfg.practice is None`, with a real-config test asserting the job exists.

### PRINT-10: Facilitator master sheet (owns reference plans, D-23, final regeneration)

- **Scope (D-17..D-23):** `spielleitung-uebersicht`: overview page; per wave (about two pages): parameters (weights, threshold, cap, upper, unit damage, slope, KZ at both bounds, bonus table with reasons from `RevealView`, recovery applicability), events of the wave with effect lines (Pattern 4) and the external/KZ kind, quick-check rows (D-19) and answer keys; Budget Review (tiers, overspend rule, X); clue matrix from `FacilitatorView.clue_matrix()`; answer keys for low, medium, high and Welle 0; Final-Index marked "vorläufig".
- **D-23 (move the final-index weights):** new top-level `"final_index": {"weight_kz": 1, "weight_ros": 1}` (required key, validator checks non-negative and not both zero), loaded into a trailing `Config` field. Callers of `rules.final_index` [VERIFIED: codebase grep]: `planspiel/report.py:104` (`summarize_tier`, has `cfg`) and `:397` (`dump_record(measure_ids, code_index, outcome, base_losses)`, called from `simulate.py:164` and from `tests/test_enumeration.py:358`, `tests/test_ros_ledger.py:144`: add a weights parameter), `planspiel/balance.py:316` (has `cfg`), `planspiel/analyze.py:71,90,126,138` (CLI `--weight-kz/--weight-ros` default `Fraction(1)`: default to the config values when `--config` is given), `tests/test_enumeration.py:87`, `tests/test_rules_semantics.py:25` (explicit weights). Remove the defaults from `rules.final_index` so no second source remains. Outputs stay identical because both weights are 1; prove with the unchanged `simulation_summary` fields, the digests (`-m slow` test_digest) and the characterization goldens. Not a rename phase, so no runtime-state inventory is needed: the only stored artifacts are gitignored `simulation_summary_*.json` and `sim_*.json` files, computed with weights 1/1 and still valid. Print the label from a `texte.toml` key ("vorläufig"), not from `report.FINAL_INDEX_STATUS`, which mentions "Phase 6" (project jargon on paper).
- **Reference plans (D-22), config shape:**

```json
"reference_plans": {
  "medium": {
    "start": {"M1": 0, "M2": 1, "M3": 1, "...": 0},
    "windows": [
      {"selection": {"...": 0}, "swap": ["M3", "M8"]},
      {"selection": {"...": 0}}
    ]
  },
  "low": {}, "high": {}
}
```

  `windows[i]` is the full selection after the change window that follows wave i+1 (matches `rules.Window`); `swap` only in the window of the Kurswechsel wave. Loader stores plain dicts (config.py cannot import rules); a helper converts to `rules.Path`. Validator checks refs and ranges only (tier exists, measure ids exact, levels valid, at most `len(waves) − 1` windows, swap pair of known ids). Legality needs `rules`: `rules.evaluate_path(cfg, tier, path)` raises `PathError` for dependency violations, an illegal swap or a missing forced swap (default `enforce_kurswechsel=True`); a build guard in `master.py` plus a default-suite test additionally assert in budget, at least one voluntary move beyond the swap, and mechanics touched (see below). The first probe showed the call is cheap (a swap plus a voluntary downgrade evaluated in milliseconds) [VERIFIED: probe].
- **Choosing near-median plans without the 4-minute swap rerun:** static in-budget medians of the final KZ (nearest rank) are low 63, medium 65, high 66, with p25/p75 54/71, 56/73, 56/73; plans within ±1 of the median number 6,802 / 11,196 / 19,841 [VERIFIED: probe, `enumerate_tier` about 42 s per tier including the summary]. Proposed helper (committed, not in the default suite, exercised on the mini config): (1) run `enumerate_tier`, take in-budget starts near the median that have at least one active and one inactive measure; (2) score each start by mechanics touched through `evaluate_path`/`path_trace` (Falls across waves, M4 recovery used, bonuses met and missed, events with non-zero KZ, a clamp or review tier hit, Budget Review tier other than the extremes); (3) for the best few dozen starts enumerate every legal swap (`rules.swap_repair`, `rules.swap_legal`) with `evaluate_path`, then add one hand-picked voluntary move in window 2 (for example a downgrade after the Sparprogramm); (4) keep paths whose *path* final KZ is near the swap-layer median. For step 4 the exact swap-layer median comes from `uv run planspiel tausch --tier X` (about 4 minutes and 62 MB per tier, run once in the background during checkpoint preparation; summary files are gitignored); otherwise use the static median ±3. Present three candidates per tier at the D-18 checkpoint; pin the approved ones in config. Record "re-choose after the Phase 6 rebalance" in the Phase 6 context.
- **Check rows (D-19):** from `worksheet_constants` (bounds Fall 1 and Fall 2, damage and KZ at both bounds) plus a table GR -> damage before recovery and attack KZ in whole GR steps from `lower + 1` to `upper − 1`; the damage rows use the rearranged formula `(upper − GR) x unit`. Wave 3 has slope 17/7, so the KZ column cannot be exact decimals: add `fmt.format_approx(value, places=2)` (explicit "≈", round half away via the existing rounding helper) used **only** on this sheet, with a hint; the same function prints RoS and the final index (non-terminating in general). Phase 6 (BAL-02) removes 17/7. Test: each table value equals `rules.attack_kz_delta(kz_at_full_damage, slope, (GR − lower) * ws, ws)` formatted.
- **Answer keys (D-17):** from `rules.path_trace` (Pattern 6), per wave: selection, CIA, E-value, bonus, Gesamtreduktion, Fall, damage before and after recovery, recovery factor, attack KZ, events with their kind, wave KZ before and after rounding, KZ before and after clamp, own OPEX, window cost, event budget/OPEX, remaining budget, then Budget Review, own spend, RoS, final index (`rules.final_index` with the config weights). Welle 0 uses `practice_config`.
- **Golden test (SC4):** every printed value equals `path_trace`; `path_trace` equals `evaluate_path` (remaining, kz_final, ros); each wave's numbers equal `replay_steps` from the wave's `AttackSheet` (independent encoding); pinned `tests/golden/answer_keys.json`.
- **Stamp inputs:** add `content/clues.toml` to `DATA_INPUTS` and `BUILD_INPUTS` and update `test_changes_outside_the_build_inputs_are_not_dirty` (it lists `content/clues.toml` as clean today) knowingly. Load clues in `_print_command` and pass them to `render_all` as an optional keyword argument.
- **Final task of the phase (last plan):** commit inputs, `uv run planspiel print` on a clean tree, `uv run planspiel print --check` exit 0, commit `final_documents/generated/`, move the folded todo to completed.

## Plan Order, Waves and PDF Regeneration

True dependencies: VEIL-02 before everything (registry, scan). PRINT-06 after PRINT-05 (deck template). PRINT-08 after PRINT-07 (booklet shell) and PRINT-06 (event kinds). PRINT-09 after PRINT-08 (shared vocabulary) and PRINT-06 (if it prints event kinds). FLOW-01 after PRINT-06 and PRINT-08 (event rows, tracking row model). PRINT-10 after FLOW-01 (Welle 0 answer key, `practice_config`), PRINT-06 (event rows). PRINT-12 depends only on VEIL-02 (and on the asset mechanism it owns).

**Recommended: strictly sequential, one plan per wave (9 waves), because nearly every plan edits the same append-only shared files:** `planspiel/render.py` (builder registry), `content/texte.toml`, `tests/fixtures/mini_content/texte.toml`, `planspiel/texts.py` (`SHEET_KEYS` and `PREWAVE_SHEETS` lists), `print/planspiel.sty`, `tests/test_print_render.py`, `tests/test_print_model.py`, `print/miktex-packages.txt` with `planspiel/texbuild.py` (probes), and some touch `simulation_config.json`, `planspiel/validate.py`, `planspiel/config.py`, `planspiel/rules.py`. With `parallelization: true` GSD may run same-wave plans together; if the planner does so, plans must declare these files in `files_modified` so overlap detection serialises them. Optional parallel chains under isolated worktrees with manual merge of the append-only files: {PRINT-05 -> PRINT-06}, {PRINT-07 -> PRINT-08 -> PRINT-09}, {PRINT-12}.

| Wave | Plan | Checkpoint | Shared items it creates |
|------|------|------------|--------------------------|
| 1 | VEIL-02 | - | audience registry, scan, build gate, prefix-aware test fixes |
| 2 | PRINT-05 | human print test of one card sheet | card sty and template, `rules.card_facts`/`level_requirements`, tikz probe, hygiene test |
| 3 | PRINT-06 | - | `eventtext.py`, `review_text.tier_rows` |
| 4 | PRINT-07 | - | booklet shell and partials |
| 5 | PRINT-08 | - | `KZ_MIN/KZ_MAX`, tracking row model |
| 6 | PRINT-09 | - | wave page, shared vocabulary |
| 7 | PRINT-12 | - | asset mechanism in `texbuild`/`stamp`, graphics probe |
| 8 | FLOW-01 | user reviews the practice story (D-16) | `practice` config, validator, `practice.py`, filled worksheet variant |
| 9 | PRINT-10 | user approves the three reference paths (D-18/D-22) | reference plans, D-23, `path_trace`, `format_approx`, clues input, final regeneration |

**PDF regeneration strategy (answer to the shared-file and stamp conflict):**
1. No test or default check requires fresh committed PDFs (F3), so stale PDFs between plans break nothing.
2. Plans verify with `-m pdf` tests (they build the whole set into pytest tmp dirs through the `printed_set` fixture) and, for a visual check, `uv run planspiel print --out-dir build/preview --build-dir build/print` (gitignored). Plans must not run a bare `uv run planspiel print`: that would overwrite `final_documents/generated/` and mix stamps with the committed Phase 4 PDFs.
3. The last plan (PRINT-10) ends with the D-19 order: commit all inputs; run `uv run planspiel print` on a clean tree (otherwise the stamp reads "+lokal"); `uv run planspiel print --check` must exit 0; commit `final_documents/generated/` including `manifest.json`.
4. Why not per-plan commits: each full regeneration rewrites every PDF (stamp) and the set is about 6 MB (the story PDF is 3.7 MB with the PNGs, [VERIFIED: probe]; the rest is small) `[ASSUMED]` about 5-6 MB total, so nine commits would add on the order of 50 MB of binary history.
5. Add a plan-level reminder: the committed generated PDFs and the manifest are considered stale until wave 9; `git status` after tests must stay clean (tests write to tmp or `build/`).

## Common Pitfalls

### Pitfall 1: Operand attribute guard fires on the first card model
**What goes wrong:** `test_no_formula_operands_outside_rules_and_config` fails with `planspiel/cards.py:NN .init`.
**Why:** F1.
**How to avoid:** accessor in `rules.py`; `.cia`, `.name`, `.levels`, `.dependencies` are allowed attributes elsewhere, `.init .opex .weights .bonus .e_threshold` are not.
**Warning signs:** red AST test in the very first card commit.

### Pitfall 2: Squashed PDF text makes the scan lie
**What goes wrong:** false positives for `apt` ("Kapital"), `sps`, `ot`; or missed weight triples when spaces vanish.
**How to avoid:** substring terms only at PDF layer; tokens at the `.tex` layer; weight detection by number windows plus the joined form (Pattern 2).

### Pitfall 3: Real "Phishing" in M6 trips a naive scan
**What goes wrong:** the card deck fails the scan although D-06 allows it.
**How to avoid:** names-only profile for measure cards (F9); never edit the pinned giveaway list; if the user wants it gone, that is a content edit to `measures.M6.*`, not a scan change (open question Q1).

### Pitfall 4: New text key without mini fixtures
**What goes wrong:** `test_texts_coverage`, `test_print_render[mini]` and others fail with missing keys because `required_keys` includes every declared sheet key for the mini config too.
**How to avoid:** add keys to `tests/fixtures/mini_content/texte.toml` and, for config blocks, either to `mini_config.json` or make the builder return `{}` when the block is absent plus a real-config test pinning the job.

### Pitfall 5: Hard-coded job lists
**What goes wrong:** `test_print_render.py:56-58`, `test_print_model.py:51` fail the moment a second builder registers.
**How to avoid:** the first plan that registers a builder changes them to prefix filters (`angriff-`), and later plans assert their own prefix.

### Pitfall 6: Hidden fourth input of the stamp
**What goes wrong:** images or `clues.toml` change, but the stamp neither moves its date nor shows "+lokal" (and the `.fls` test rejects the unhashed PNG read).
**How to avoid:** F15: extend static files, `DATA_INPUTS`, `BUILD_INPUTS`, tests.

### Pitfall 7: Jinja comment delimiter collision (IN-06)
**What goes wrong:** `\#{` in a template swallows text up to the next `}`; likely in templates with literal `\#`.
**How to avoid:** do not write `\#{}` in templates; keep the comment line style used in `angriff.tex.j2`; optionally change the delimiter in `make_env` (rendered output unchanged, so the stamp hash is unaffected, only the template-date input moves).

### Pitfall 8: Lost glyphs do not fail the build (IN-09)
**What goes wrong:** a card prints a symbol Arial lacks (box, tick, lock); LuaTeX only logs "Missing character". `\tracinglostchars=3` also only logged in this MiKTeX build [VERIFIED: probe].
**How to avoid:** draw icons in TikZ; run the generic hygiene test (log scan for `Missing character` and `Overfull \hbox`) over every job, not only the worksheets.

### Pitfall 9: Clamp/rounding semantics on the tracking sheet
**What goes wrong:** sheet rounds twice or clamps before rounding. Rule: round the wave KZ change once, then add to the previous KZ and clamp (`rules.wave_kz_change`, `rules.clamp_kz`) [CITED: CLAUDE.md]. Print "gerundet" only on the worksheet line, "begrenzt" on the tracking row.

### Pitfall 10: Static reference plan used as the answer key
**What goes wrong:** the key omits the forced swap and the budget impact of window moves; the low tier legal best is 100 versus the static reference 98 (STATE.md).
**How to avoid:** `evaluate_path` only; test that the swap window exists.

### Pitfall 11: `TEX_PROBES`/package list drift
**What goes wrong:** `test_every_loaded_package_is_a_probe` and `test_miktex_package_list_covers_the_probes_and_is_sorted` fail when a template loads `tikz` or `graphicx` without probe and list entry.
**How to avoid:** change both in the same commit; the list must stay sorted and equal to `set(TEX_PROBES.values()) | {"tikzfill"}`.

### Pitfall 12: Practice leaking into the real machinery
**What goes wrong:** putting practice under `attacks` or `waves` changes enumeration, `base_losses` (620 -> 740), digests and goldens.
**How to avoid:** top-level `practice` block, `practice_config` view, tests that pin enumeration counts and base losses.

## Code Examples

### Weight triple detection (layer 2 sketch)

```python
# planspiel/veil.py, uses rules.worksheet_constants (F1) and fmt.format_number
NUMBER = re.compile(r"\d+(?:,\d+)?")

def weight_signatures(cfg) -> dict[tuple[str, str, str], int]:
    found = {}
    for wave in cfg.waves:
        c = rules.worksheet_constants(cfg, wave)
        found[(fmt.format_number(c.w_c), fmt.format_number(c.w_i), fmt.format_number(c.w_a))] = wave.wave_id
    return found

def weight_hits(text: str, signatures) -> list[int]:
    numbers = NUMBER.findall(text)
    squashed = re.sub(r"\s+", "", text)
    hits = {signatures[tuple(numbers[i:i + 3])] for i in range(len(numbers) - 2) if tuple(numbers[i:i + 3]) in signatures}
    hits |= {wave for triple, wave in signatures.items() if "".join(triple) in squashed}
    return sorted(hits)
```

### Event row equivalence test (pattern)

```python
# tests/test_event_text.py
def test_checklist_rows_match_evaluate_event(cfg):
    event = next(e for events in cfg.events.values() for e in events if e.type == "checklist_tier")
    for row in eventtext.effect_rows(event, cfg).rows:
        for count in row.counts:                       # e.g. (2, 3) for the merged row "2–3 erfüllt"
            selection = {m: 0 for m in cfg.measures}
            for measure in event.params["measures"][:count]:
                selection[measure] = event.params["min_level"]
            assert rules.evaluate_event(event, selection)[0] == row.kz
```

### Filled worksheet macro (template change must leave real sheets byte-identical)

```
\BLOCK{macro fillline(parts)}
\fillline{\BLOCK{for part in parts}\BLOCK{if part is string}\VAR{part}\BLOCK{elif part.value}\ifilled{\VAR{part.size}}{\VAR{part.value}}\BLOCK{else}\ibox{\VAR{part.size}}\BLOCK{endif}\BLOCK{endfor}}
\BLOCK{endmacro}
```

### Practice view call (verified shape)

```python
pcfg = practice_config(cfg)
constants = rules.worksheet_constants(pcfg, pcfg.waves[0])      # lower 20, cap 6, slope 5/2
record = rules.evaluate_plan(pcfg, "practice", cfg.practice.selection)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hand-maintained PPTX/DOCX cards and sheets, k€ on cards | Generated from config through Jinja and LuaLaTeX | Phases 3-4 | Print sync by construction; Phase 7 archives the legacy files |
| Event penalties inside RoS | Own spend only (RULE-06) | Phase 2 | Legacy RoS sheet row "Summe Event-Strafen" must not be carried |
| Flat Budget Review "< 0 -> −15" | Inclusive tiers plus linear overspend penalty (RULE-03, RULE-07) | Phase 2 | Card text from `review_text` |
| Wave weights not printed | Weights on the revealed worksheet, symbols only before the wave | Phase 4 | The scan keys on values, not symbols |
| Whiteboard write-up | Printed tracking sheet | this phase | PRINT-08 |

**Deprecated/outdated:** `final_documents/Budget.docx`, `Return on Security und Final Wert.docx`, `Events_Security-Game.pptx`, `Massnahmenkarten_Security-Game.pptx` (read-only references, archived in Phase 7); `status tracker` table of the Budget sheet (replaced by the tracking sheet).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Card text fits A6 at 9-10 pt (about 100-115 mm of 134 mm for the longest measure card; Kurswechsel about 80 mm) | Pattern 3 | Cards overflow; fallback sizes listed; proven by fit markers in the first pdf test |
| A2 | Whole print set is about 5-6 MB per regeneration | Plan Order | Only affects the argument for one-time regeneration |
| A3 | Euros (not k€) on cards and sheets | PRINT-05 | Players add small numbers by hand; user may prefer k€; template change only |
| A4 | Georgia for the newspaper masthead and serif body | PRINT-12 | Fonts differ on another machine (same caveat as Arial, D-16) |
| A5 | The practice parameter set illustrated in FLOW-01 is final | FLOW-01 | Executor re-runs the search; guards enforce the required properties |
| A6 | Skipping duplex backs (D-07) is acceptable | Standard Stack | Optional output; can be added later |
| A7 | Stamp once per sheet in the bottom strip satisfies PRINT-11 for cards | Pattern 3 | If the user wants a stamp on every card, relax the per-page stamp test for card jobs |
| A8 | `uebung-` prefix is acceptable for the practice sheet; players see "Welle 0 – Übung" | Pattern 1 | Cosmetic |

## Open Questions

1. **Q1: "Phishing" on the M6 measure card (D-06) versus the VEIL-02 wording "no attack names".**
   - What we know: M6 `focus`, `levels_desc.2`, `levels_simple.2` contain "Phishing" (a stem on the D-13b list); M5/M7 contain "OT" (a story-profile exception). D-06 allows defences to be named.
   - What's unclear: whether the user wants the scan to accept this.
   - Recommendation: names-only profile for the card deck (accepts "Phishing"); the user may instead edit the M6 wording, a content change outside the scan.
2. **Q2: Is the reference-plan checkpoint (D-18/D-22) one approval for three paths or per tier?** Recommendation: one checkpoint, three candidates per tier shown with per-wave numbers.
3. **Q3: Units on cards and sheets.** Recommendation: euros with thousands dot everywhere, because RoS and damage are in euros; the legacy cards used k€.
4. **Q4: Stamp on every card or once per sheet?** Recommendation: once per sheet (bottom strip), which keeps the existing per-page test valid.
5. **Q5: Where does `[sheets.backup_recovery]` go?** Recommendation: not a ninth card; use it on the wave explainer with the generated M4 table (8 cards = exactly 2 sheets).
6. **Q6: Approximate values for the 17/7 slope on the master sheet.** Recommendation: explicit "≈" with two decimals on the facilitator sheet only; disappears when Phase 6 makes the slope hand-friendly.
7. **Q7: Newspaper typography.** Recommendation: Georgia masthead and body (installed); fall back to Arial if the user wants a single font.
8. **Q8: Practice story topic (D-16).** Needs the user's review of Claude's draft; avoid incidents close to exfiltration, ransomware or OT outage.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` + Python 3.12 | everything | yes | project-managed | - |
| `lualatex` (LuaHBTeX, MiKTeX) | `-m pdf`, `planspiel print` | yes | 1.25.7, MiKTeX 26.5 | none (PDF tests skip without it) |
| `kpsewhich --miktex-disable-installer` | preflight | yes | MiKTeX 26.5 | - |
| TeX packages `fontspec babel babel-german geometry xcolor colortbl tools tikzfill` | existing | yes | - | user installs from `print/miktex-packages.txt` |
| TeX packages `pgf` (tikz + 6 libraries), `graphics` (graphicx), `tools` (multicol) | new templates | yes (loadable now) | - | add to list; user install elsewhere |
| System fonts Arial, Georgia, Times New Roman, Cambria, Calibri, Segoe UI | cards, story | yes (`C:\Windows\Fonts`) | - | Arial |
| `pypdf` 6.19.0 | pdf tests | yes (dev group) | 6.19.0 | - |
| `git` | stamp, manifest | yes | - | stamp errors without it |
| Symbol fonts (fontawesome5, pifont, wasysym, marvosym, bbding) | not needed | no | - | draw icons in TikZ |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** icon fonts (not needed).

## Validation Architecture

Nyquist validation is enabled (`workflow.nyquist_validation: true`).

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (dev group), pypdf 6.19.0 for PDF text |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]`: `addopts = -m 'not slow and not pdf' --strict-markers`, markers `slow`, `pdf` |
| Quick run command | `uv run pytest tests/test_<module>.py -x -q` (the plan's own files, seconds) |
| Full suite command | `uv run pytest -q` (default fast suite: 1172 passed in about 69 s today), `uv run pytest -m pdf -q` (21 passed in about 56 s today; grows to a few minutes), `uv run pytest -m slow` (full enumeration, only for D-23 digests) |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VEIL-02 | audience for every job; unknown prefix raises | unit | `uv run pytest tests/test_veil_audience.py -x` | ❌ Wave 0 |
| VEIL-02 | layer 1 scan finds injected names, weight triples, revealed strings; own-wave strings pass on `angriff-` | unit | `uv run pytest tests/test_veil_scan.py -x` | ❌ Wave 0 |
| VEIL-02 | pre-wave builder modules never touch revealed or wave internals | unit (AST) | `uv run pytest tests/test_veil_models.py -x` | ❌ Wave 0 |
| VEIL-02 | all built PDFs: text, metadata, outline, names clean; revealed N does not name other attacks | pdf | `uv run pytest -m pdf tests/test_veil_pdf.py` | ❌ Wave 0 |
| PRINT-05 | 31 cards, values equal `rules`, dependency only on M1/M3/M7 level 3 | unit | `uv run pytest tests/test_cards_model.py -x` | ❌ Wave 0 |
| PRINT-05 | template renders from model, plain variables | unit | `uv run pytest tests/test_cards_render.py -x` | ❌ Wave 0 |
| PRINT-05 | 8 sheets, stamp and page counter, fit markers, fragments in PDF | pdf | `uv run pytest -m pdf tests/test_cards_pdf.py` | ❌ Wave 0 |
| PRINT-05 | no `Missing character`/`Overfull` in any job log | pdf | `uv run pytest -m pdf tests/test_print_documents_pdf.py` | ❌ Wave 0 |
| PRINT-06 | every effect row equals `rules.evaluate_event` / `budget_review_delta` | unit | `uv run pytest tests/test_event_text.py -x` | ❌ Wave 0 |
| PRINT-06 | 8 cards, 2 sheets, fit | unit + pdf | `uv run pytest tests/test_event_cards.py -x`; `-m pdf` | ❌ Wave 0 |
| PRINT-07 | budget and RoS sheets from config; no event-penalty row | unit + pdf | `uv run pytest tests/test_booklet_model.py -x`; `-m pdf tests/test_booklet_pdf.py` | ❌ Wave 0 |
| PRINT-08 | row order, shaded cells by event kind, window blocks, swap credit | unit | `uv run pytest tests/test_tracking_model.py -x` | ❌ Wave 0 |
| PRINT-08 | tracking part on one page | pdf | `uv run pytest -m pdf tests/test_tracking_pdf.py` | ❌ Wave 0 |
| PRINT-09 | one page, no values or names, vocabulary equals worksheet | unit + pdf | `uv run pytest tests/test_wave_page.py -x`; `-m pdf` | ❌ Wave 0 |
| PRINT-12 | four documents from `[story.*]`; every clue quote in the PDF; images embedded | unit + pdf | `uv run pytest tests/test_story_model.py -x`; `-m pdf tests/test_story_pdf.py` | ❌ Wave 0 |
| FLOW-01 | practice validator rules; view ignored by enumeration/base losses | unit | `uv run pytest tests/test_practice_config.py -x` | ❌ Wave 0 |
| FLOW-01 | golden: printed numbers equal rules and replay; pinned JSON | unit | `uv run pytest tests/test_welle0_golden.py -x` | ❌ Wave 0 |
| FLOW-01 | filled worksheet pages, real sheets byte-identical | pdf | `uv run pytest -m pdf tests/test_welle0_pdf.py` | ❌ Wave 0 |
| PRINT-10 | final-index weights from config; outputs unchanged | unit (+ slow digests) | `uv run pytest tests/test_final_index_config.py -x`; `-m slow tests/test_digest.py` | ❌ Wave 0 |
| PRINT-10 | reference plans legal, in budget, mechanics touched | unit | `uv run pytest tests/test_reference_plans.py -x` | ❌ Wave 0 |
| PRINT-10 | `path_trace` equals `evaluate_path`; keys equal replay | unit | `uv run pytest tests/test_path_trace.py -x` | ❌ Wave 0 |
| PRINT-10 | master sheet values and check rows equal rules; pinned `answer_keys.json` | unit + pdf | `uv run pytest tests/test_master_model.py -x`; `-m pdf tests/test_master_pdf.py` | ❌ Wave 0 |
| All | texts: coverage, digits, giveaway including new sections | lint | `uv run planspiel texts`, `uv run planspiel clues` | ✅ |
| All | config validates, enumeration unchanged | lint | `uv run planspiel validate` | ✅ |

### Sampling Rate

- **Per task commit:** the plan's own quick files (seconds) plus `uv run planspiel texts`.
- **Per wave merge:** `uv run pytest -q` (about 70 s, must stay green), `uv run planspiel validate`, `uv run planspiel texts`, `uv run planspiel clues`, `uv run pytest -m pdf -q` for plans that add a document.
- **Phase gate (before `/gsd-verify-work`):** fast suite + `-m pdf` + `uv run pytest -m slow tests/test_digest.py` (after D-23) + `uv run planspiel print` on a clean tree + `uv run planspiel print --check` exit 0.
- **Manual (cannot be automated):** physical print of one card sheet (cut, margins, legibility) and one booklet; user review of the Welle 0 story and the reference plans (checkpoints).

### Wave 0 Gaps

- [ ] `tests/support/pdf_text.py` shared helpers (squash, pages, fragments, fit-marker regex); today `_squash`/`_pages` are duplicated in `test_print_worksheets_pdf.py` and `test_print_stamp_pdf.py`.
- [ ] Make `tests/test_print_render.py`, `tests/test_print_model.py` job assertions prefix-aware (F5).
- [ ] `tests/test_print_documents_pdf.py` generic hygiene over `printed_set.jobs`.
- [ ] Mini fixtures extended per plan (texts; config blocks or graceful `{}` builders).
- [ ] No new framework needed.

## Security Domain

`security_enforcement` is on (ASVS level 1, block on high). This is an offline batch tool with no network, no users and no secrets; the relevant surfaces are TeX injection through content strings, subprocess handling, file paths, and information leakage of the game itself.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | - |
| V3 Session Management | no | - |
| V4 Access Control | partly | audience separation of documents (facilitator-only sheet never shipped with player material): `spielleitung-` prefix, audience registry |
| V5 Input Validation | yes | `tex_escape` as Jinja `finalize` (TypeError for non-strings, ValueError for control characters), `StrictUndefined`, config validator, texts lints (coverage, digit, giveaway, story mechanics) |
| V6 Cryptography | no (SHA-256 only for integrity of the manifest, not a security control) | `hashlib` |
| V7 Error handling and logging | yes | build errors reported as `ERROR print.*` with exit codes; no stack traces needed in output |
| V8 Data protection | yes (the veil) | VEIL-02 scan, empty PDF metadata |
| V10 Malicious code / supply chain | yes | no new Python dependency; TeX packages from MiKTeX only, installer disabled |
| V12 Files and resources | yes | fixed asset names, `Path(name).name == name` checks, cleanup limited to PDFs the previous manifest lists |
| V14 Configuration | yes | validator for new config blocks; non-default inputs stamped "+lokal" |

### Known Threat Patterns (lift into each plan's `<threat_model>`)

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| TeX injection through a content string (`\write18`, `\input`, `\directlua`) | Tampering / Elevation | all text passes `tex_escape`; backslash becomes `\textbackslash{}`; no `--shell-escape`; templates never emit raw TeX from data; test that a string with `\input{x}` renders inert |
| Template prints an unescaped number or object | Tampering | `finalize` rejects non-str; numbers pre-formatted in the model; plain-variable template test |
| Runaway or hanging TeX build (large TikZ deck) | Denial of service | `texbuild._run_bounded` with timeout and process-tree kill, `--disable-installer`, stdin closed; measure deck build time and raise `timeout_s` only knowingly |
| Path traversal via `--out-dir`, `--build-dir`, `--print-dir`, manifest entries | Tampering | existing guards (`previous_pdf_names`, `check_freshness` name checks, IN-08 open); asset file names fixed in code, never taken from content |
| Facilitator sheet or answer keys reach players | Information disclosure | audience prefix, separate job, not in any pre-wave print list, overview page states it |
| Pre-wave document names an attack or prints wave weights/bonus links | Information disclosure | VEIL-02 layers 1 and 2, AST guard on pre-wave modules, `PreAttackView` only |
| PDF metadata, XMP, outlines or image names leak terms | Information disclosure | `suppressoptionalinfo 1023`; pdf test asserts empty `metadata`, no XMP, no outline, no annotations |
| Tampered or stale committed PDFs | Tampering / Repudiation | `manifest.json` SHA-256 per document, `planspiel print --check`, stamp on every page |
| Poisoned input (untrusted TOML/JSON) | Tampering | repo-controlled files parsed with `tomllib` and `json` + `Fraction` (no `eval`); validator rejects malformed shapes before any rendering |

## Project Constraints (from CLAUDE.md)

- Everything in English (code, commits, docs); game content and printed text German; UI/questions to the user in German in discussions (memory). Conventional commits.
- Always `uv run`, never the `python` on PATH (Inkscape's). `uv run pytest` fast; `-m slow`; `-m pdf`.
- TDD with RED commits; do not batch requirements: one PLAN.md per requirement; review requirements for gaps before planning (done by the orchestrator).
- Numbers: config first, then README, then print material; no fixed numbers in prose; hand-calculability of printed formulas is a hard criterion (linear formulas only; the approximated 17/7 table is the one flagged exception, disappearing in Phase 6).
- `final_documents/generated/*.pdf` are never hand-edited; legacy `final_documents/*` and `pptx_output/` untouched until Phase 7.
- New TeX packages go into `print/miktex-packages.txt`; the user installs them; the executor never touches MiKTeX.
- Rounding: `round()` banned in `rules.py`/`rounding.py`; half away from zero once per wave, then clamp.
- Prefer editing existing files; no speculative features (skip duplex backs).
- Git: never `--no-verify`, no force push to main, commits end with the attribution lines from the session reminder.
- GSD workflow enforcement: work starts through a GSD command.
- Deferred to Phase 6: re-choose reference plans and re-pin answer keys, rescale final-index weights and drop "vorläufig".

## Sources

### Primary (HIGH confidence, read or measured this session)
- `planspiel/` (`render.py`, `texbuild.py`, `stamp.py`, `printmodel.py`, `rules.py`, `config.py`, `texts.py`, `validate.py`, `report.py`, `analyze.py`, `balance.py`, `enumerate.py`, `fmt.py`, `review_text.py`, `cli.py`), `print/planspiel.sty`, `print/templates/angriff.tex.j2`, `print/miktex-packages.txt`
- `tests/` (`conftest.py`, `test_single_definition.py`, `test_print_*`, `test_texts_*`, `test_characterization.py`, `support/worksheet_replay.py`, fixtures)
- `simulation_config.json`, `content/texte.toml`, `content/clues.toml`, `content/giveaway_terms.toml`, `content/digit_allowlist.toml`, `content/assets/*`
- `.planning/phases/05-*/05-CONTEXT.md`, `04-CONTEXT.md`, `03-CONTEXT.md`, `04-REVIEW.md`, `04-VERIFICATION.md`, `.planning/research/ARCHITECTURE.md`, `FEATURES.md`, `REQUIREMENTS.md`, `STATE.md`, `ROADMAP.md`
- Local probes: LuaLaTeX compiles (tikz and libraries, multicol, graphicx, A6 2x2 sheet, images), pypdf extraction modes, `enumerate_tier` timings and medians, `evaluate_path` output, practice parameter search, default and pdf suite baselines, `planspiel print --check`

### Secondary (MEDIUM confidence)
- Legacy `final_documents/*.pptx` and `*.docx` dumped via zipfile/python-pptx (structure of cards, events, budget and RoS sheets)

### Tertiary (LOW confidence)
- Layout fit estimates and the print-set size (tagged `[ASSUMED]`)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, every package and font probed on the build machine.
- Architecture: HIGH for pipeline reuse and guard-rail conflicts; MEDIUM for card fit and the stamp strip until the first pdf tests run.
- Pitfalls: HIGH, each one traced to a file or a probe.

**Research date:** 2026-10-23
**Valid until:** 2026-11-22 (stable code base; re-check if Phase 6 starts changing config values before Phase 5 ships)
