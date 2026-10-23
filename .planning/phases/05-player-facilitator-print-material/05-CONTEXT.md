# Phase 5: Player & Facilitator Print Material - Context

**Gathered:** 2026-10-22
**Status:** Ready for planning

<domain>
## Phase Boundary

The same `uv run planspiel print` command that builds the Angriff 1–3 worksheets (Phase 4) also builds every
remaining card and sheet that players and facilitators use, all generated from `simulation_config.json` and
`content/texte.toml`:

- measure cards (10 measures × 3 levels) with a legend card, event cards and the Budget Review card;
- the team booklet (budget and planning, tracking sheet, RoS and Budget Review);
- the one-page "So funktioniert eine Welle";
- the worked example "Welle 0 – Übung";
- the facilitator master sheet;
- the four story documents (Unternehmenssteckbrief, Zeitungsartikel, Anfrage-Mail, Audit-Mail, PRINT-12).

An automated veil scan proves that no pre-wave material names an attack or prints wave CIA weights (VEIL-02, VEIL-04).

Requirements: PRINT-05, PRINT-06, PRINT-07, PRINT-08, PRINT-09, PRINT-10, PRINT-12, VEIL-02, VEIL-04, FLOW-01.
The session schedule, debrief questions, "Was ist neu" sheet and dry run (FLOW-02..05) are Phase 7.

</domain>

<decisions>
## Implementation Decisions

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

### Open questions from research, resolved (2026-10-23)
- **D-24:** **"Phishing" stays on the M6 card.** The veil scan checks the measure deck with a names-only profile: it flags the real attack names, not defence terms from D-06.
- **D-25:** **Money is printed in euros with a thousands dot everywhere** (e.g. 30.000 €), on cards and sheets alike, with no k€.
- **D-26:** **Smaller defaults accepted:**
  - one checkpoint covers all three reference paths, with per-tier candidates and numbers per wave (Q2);
  - the version stamp appears once per A4 sheet in the bottom strip, not on each card (Q4);
  - `[sheets.backup_recovery]` becomes a section of the wave explainer with the generated M4 table, not a ninth card (Q5);
  - values with the 17/7 slope appear as "≈" with two decimals on the facilitator sheet only, until Phase 6 (Q6);
  - the newspaper uses Georgia, everything else Arial (Q7).

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and requirements
- `.planning/ROADMAP.md` (Phase 5 section): goal and success criteria SC1–SC6.
- `.planning/REQUIREMENTS.md`: PRINT-05..10, PRINT-12, VEIL-02, VEIL-04, FLOW-01.
- `.planning/PROJECT.md`: core value, constraints and Key Decisions (veil timing, LaTeX, hand-calculability).

### Prior phase decisions
- `.planning/phases/03-content-source-veiling/03-CONTEXT.md`: content-source shape, digit lint, veiled/revealed texts, story docs, clue matrix, giveaway list (D-01..D-30).
- `.planning/phases/04-print-pipeline-attack-worksheets/04-CONTEXT.md`: pipeline, stamp, manifest, colours, fonts, MiKTeX rules (D-01..D-21).
- `.planning/phases/04-print-pipeline-attack-worksheets/04-REVIEW.md` and `04-REVIEW-FIX.md`: open Info findings IN-01..IN-09 (e.g. the "GR" abbreviation is not introduced, a missing glyph does not fail the build, `\levelbadge` > 3) that Phase 5 templates should not repeat.
- `.planning/research/ARCHITECTURE.md` and `.planning/research/FEATURES.md`: print-model architecture, card anatomy, turn sequence, worked example, facilitator handbook patterns.

### Content and design sources
- `simulation_config.json`: measures, events, budget tiers, waves; the practice attack and reference plans get added here.
- `content/texte.toml`: `[measures.*]`, `[events.*]`, `[final_events.budget_review]`, `[sheets.budget]`, `[sheets.ros]`, `[sheets.backup_recovery]`, `[sheets.labels]`, `[story.*]`.
- `content/clues.toml`, `content/giveaway_terms.toml`, `content/digit_allowlist.toml`.
- `content/assets/GUIDELINES.md` and `content/assets/images/`: MHP colours, card semantics, story-document layout facts.
- `content/INVENTORY.md`: what was carried from the hand-maintained documents.
- Legacy references, read only and never edited:
  - `final_documents/Massnahmenkarten_Security-Game.pptx` (30 measure-level slides);
  - `final_documents/Events_Security-Game.pptx` (9 slides);
  - `final_documents/Budget.docx`, `final_documents/Return on Security und Final Wert.docx`;
  - the story docs `Unternehmenssteckbrief MechTech.docx`, `Zeitungsartikel.pdf`, `Anfrage-Mail.pdf`, `Audit-Mail.pdf`.

### Rules
- `README.md`: rules and formulas (prose).
- `CLAUDE.md` (repo root): mechanics summary, rounding, RoS, change window, Kurswechsel.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `planspiel/render.py`: Jinja environment, `tex_escape` (handles `"` and the TeX ligatures since CR-01), `render_all` registry of print jobs. Phase 5 documents register here.
- `planspiel/texbuild.py`: bounded LuaLaTeX driver, preflight, `build_documents(stamp_tex=...)`.
- `planspiel/stamp.py`: content-hash stamp, manifest, `--check`. New documents are covered automatically once they are rendered by `render_all`.
- `planspiel/printmodel.py`: `AttackSheet` model, `printed_fragments()`, D-06/D-09 guards. The Welle 0 sheet and the master-sheet answer keys reuse it.
- `planspiel/fmt.py`: German number, euro and percent formatting (thousands dot, decimal comma, real minus).
- `planspiel/review_text.py`: Budget Review tier text from config.
- `planspiel/texts.py`: `PreAttackView` / `RevealView` access to veiled vs revealed texts, `check_texts`, giveaway and digit lints.
- `planspiel/rules.py`: `apply_attack`, `evaluate_plan`, `evaluate_path`, `security_spend`, `swap_credit`, `budget_review_delta`. Source for every printed number and every golden test.
- `planspiel/enumerate.py`: full enumeration, used to propose the typical tier plans (D-18).
- `print/planspiel.sty`, `print/templates/angriff.tex.j2`: shared style, level badges and the worksheet template.
- `tests/support/worksheet_replay.py`: independent hand-calc replay, usable for the Welle 0 and answer-key golden tests.

### Established Patterns
- Config → print model → Jinja template → LuaLaTeX. Templates do no arithmetic. Every printed number comes from a model field, and a pdf test checks that model numbers appear in the PDF text.
- TDD with RED commits. Fast tests run by default; `-m pdf` for real TeX builds; `-m slow` for the enumeration.
- Stamp and manifest are committed in the D-19 order.

### Integration Points
- `planspiel print` / `render_all`: register each new document.
- `simulation_config.json` schema plus `planspiel/validate.py`: the practice attack and the reference plans need schema and validator support, and must not leak into the enumeration or the gate.
- `planspiel/texts.py` declared `[sheets.*]` key lists: they grow with the new sheets.

</code_context>

<specifics>
## Specific Ideas

- Dependency icon example: a lock icon with "M2 ≥ L2".
- Tracking sheet columns: Start / Welle 1 / Welle 2 / Welle 3 / Budget Review.
- Welle 0 title: "Welle 0 – Übung".
- The user asked that discussion questions be asked in German. Documents and code stay as per project rules: German content, English code and docs.

</specifics>

<deferred>
## Deferred Ideas

- Re-choose the typical tier reference paths and re-pin their answer keys after the Phase 6 rebalance (D-18, D-22).
- Rescale the final-index weights in config during the Phase 6 rebalance and drop the "vorläufig" mark (D-23, BAL-03).
- Session schedule, debrief questions, "Was ist neu" and the timed dry run: Phase 7 (FLOW-02..05).
- Archiving the hand-maintained docx/pptx/pdf in `final_documents/` once generated replacements exist: Phase 7 (LEG-01).

</deferred>

---

*Phase: 05-player-facilitator-print-material*
*Context gathered: 2026-10-22*
