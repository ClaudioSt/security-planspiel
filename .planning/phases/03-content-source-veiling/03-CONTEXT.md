# Phase 3: Content Source & Veiling - Context

**Gathered:** 2026-10-06
**Status:** Ready for planning

<domain>
## Phase Boundary

All German prose used on print material moves into one content source, `content/texte.toml`, keyed by config id. That covers measure texts, attack texts, event narratives and rule texts, sheet instructions, and (new, D-14) the prose of the pre-wave story documents. Each attack gets a veiled pre-wave text and a revealed at-wave text. A facilitator clue matrix proves every attack is inferable from at least two clues in distinct pre-wave sources. Coverage, digit and giveaway lints guard the source.

Not in this phase: LaTeX templates and PDFs (Phases 4 and 5), the VEIL-02 scan of rendered pre-wave PDFs and the VEIL-04 card layout (Phase 5), and numeric rebalancing (Phase 6).

Requirements: PRINT-02, VEIL-01, VEIL-03 (ROADMAP Phase 3 success criteria 1–5).

</domain>

<decisions>
## Implementation Decisions

### Carried forward (decided earlier, not re-asked)
- Attack names are veiled only in material players see **before** a wave and revealed by name when the wave hits. Mechanics (CIA weights, E-value, damage, event effects) stay fully transparent (PROJECT.md Key Decisions, 2026-09-29).
- Measure cards show CIA values, costs and dependencies only. Wave weights and measure→attack bonus links appear only on the revealed attack worksheet (VEIL-04, Phase 5).
- Config is the single source for numbers; order of change is config → README → print material.
- `MEASURE_META` in legacy generators stays untouched until LEG-01 (Phase 2 D-29).

### Content source shape (PRINT-02)
- **D-01:** One file, **`content/texte.toml`** (stdlib `tomllib`), sections keyed by config id, e.g. `[measures.M1]`, `[attacks.ransomware]`, `[events.kurswechsel]`, `[final_events.budget_review]`, `[sheets.*]`, `[story.*]`. A loader module (research name: `planspiel/texts.py`) loads and validates it.
- **D-02:** **Prose is stripped from `simulation_config.json`.** Attack/event/final-event `description`, `waves[].name` and `waves[].bonus_measures[].description` move to TOML and are removed from config. Config keeps ids, numbers, mechanics and **short technical labels** used by sim/balance reports (e.g. measure `name` "IAM/PAM", event `name`). A wave is identified by its `attack_id`, so nothing in config names an attack in prose.
- **D-03:** **No numbers in TOML prose.** TOML holds only the narrative sentence. Every line with a game number (e.g. "OPEX −2.000 € pro aktiver Maßnahme", "Gesamtbudget −20.000 €", "KZ −10") is **generated from event type + params in code**, following the `planspiel/review_text.py` pattern. No `{param}` placeholders in TOML.
- **D-04:** **Rule texts live in TOML as prose.** For example, the Kurswechsel rule wording (D-09..D-13, D-22, D-23 of Phase 2) and the Sparprogramm end-check sentence go into TOML, with separate keys for `narrative` (story) and `rule` (how it works). Code only generates the numeric effect line.
- **D-05:** **Measure texts are carried over 1:1** from `MEASURE_META`: `focus`, `description`, `levels_desc` (technical), `levels_simple` (plain). No editorial rework now; Phase 5 decides what the card prints.
- **D-06:** Measure texts **may say what they defend against** (e.g. M6 "Phishing abwehren"). Only attack names and wave links are banned from pre-wave material (enforced in Phase 5 by VEIL-02).
- **D-07:** **Legacy generators untouched.** `generate_pptx_cards.py` and `generate_from_template.py` keep their own `MEASURE_META`/`ATTACK_NAMES` copies until they are archived (LEG-01, Phase 7). The single-definition guard already excludes `generate_*.py`.
- **D-08:** Removing text fields from config changes text in the pinned goldens. Handle it as a **reviewed text-only snapshot change, like 02-07**. The executor shows a diff proving only text keys changed (numbers and digests identical) and regenerates via `--update-golden` only after user approval.
- **D-09:** **Coverage check:** fails on any config id (measure, attack, event, final event) without its required TOML keys, and on any orphaned TOML key without a config id (SC1). `[sheets.*]` and `[story.*]` are checked against a declared key list rather than config ids.

### Digit lint (SC2)
- **D-10:** **Strict:** any digit in `texte.toml` fails the lint, except tokens on an **explicit, reviewed allowlist** of flavor tokens that are not game parameters (e.g. "24/7", "30 Tage", "NIS2"). Each allowlist entry is a conscious decision.
- **D-11:** The lint covers **all of `texte.toml`** (measures, attacks incl. revealed texts, events, sheets), **except the `[story.*]` section** (D-15).
- **D-12:** German number words ("drei Fertigungslinien", "zwei Admins") are **allowed**; the lint checks digits only.

### Veiled vs revealed attack texts (VEIL-01)
- **D-13:** **Veiled = neutral title only.** Before the wave an attack appears only as **"Angriff 1" / "Angriff 2" / "Angriff 3"**, with no teaser text. All inference comes from the clues in the pre-wave story documents (D-17). On reveal the title becomes "Angriff 1: Ransomware" etc. (matches the existing worksheet naming).
- **D-13a:** **Revealed text per attack** = attack name + scenario narrative (from the current config `description` / `Angriff-*.docx`) + the CIA rationale sentence ("Bei Ransomware zählen C und I stärker …"). Bonus-measure reasons ("EDR/XDR erkennt Ransomware früh") move to TOML as **revealed-only** keys.
- **D-13b:** **Giveaway-term lint** runs on the **veiled attack keys only** (exactly SC3). Banned list = attack names plus core technique terms, matched case-insensitively with word stems: Ransomware, Verschlüsselung/verschlüsselt, Lösegeld, Erpress*, Phishing, Emotet, OT-Störung, SPS, Sinumerik(-Schwachstelle), Exfiltration, Datendiebstahl, Darknet, APT, plus the attack ids. The same list is reused for story texts by the clue/veil check (D-16).
- **D-13c:** **Events are not veiled.** They keep their names (they are drawn after a wave and are rules, not threats to infer). The only constraint is that event texts must not name an upcoming attack. This narrows the todo's "Aktionen" part, consistent with the 2026-09-29 clarification.
- **D-13d:** **Authoring:** Claude drafts the revealed texts (from config/docx) and the veiled story rewrites; the **user reviews them at a checkpoint before commit**.

### Story documents and clue matrix (VEIL-03, SC5)
- **D-14:** **Story-document prose moves into `texte.toml` now** under `[story.*]`: Unternehmenssteckbrief MechTech, Zeitungsartikel, Anfrage-Mail, Audit-Mail. They are **generated via LaTeX in Phase 5**. This adds requirement **PRINT-12** (story documents generated from the content source) to Phase 5 (REQUIREMENTS.md + ROADMAP amended 2026-10-06). Rationale: two of the four docs name the attack, `Audit-Mail.pdf` is image-only (needs transcription), SCEN-04 (v4) needs per-scenario story docs, and the clue check becomes exact against TOML keys.
- **D-15:** `[story.*]` is **exempt from the digit lint** (world facts such as "ca. 80 Mitarbeitende", "15 Mio. EUR", dates, addresses). Rule: story texts must not state game mechanics or game amounts (budget tiers, KZ, costs).
- **D-16:** **Veil the story texts in this phase.** The Zeitungsartikel (headline "Phishing stoppt Fertigung", "Ransomware legt Zulieferer tagelang lahm", body) and the Anfrage-Mail ("Täglich lesen wir von Ransomware-Angriffen") are rewritten without attack names or giveaway terms while keeping their clue value (e.g. "Erpresser legen Zulieferer lahm", "verdächtige E-Mail in der Buchhaltung"). Claude drafts, the user reviews (D-13d). Story texts are checked against the giveaway list from D-13b.
- **D-17:** **Clue matrix = data file with verbatim quotes:** `content/clues.toml`. Per attack it lists clues as {source key in `texte.toml` `[story.*]` (or other pre-wave key), verbatim quote, why it points to the attack}. The check fails if an attack has fewer than two clues, if a quote is not found verbatim in its source key, or if a source is not pre-wave material. The facilitator view is rendered in Phase 5 (PRINT-10).
- **D-18:** **≥ 2 clues per attack from ≥ 2 distinct source documents** (e.g. Steckbrief + Zeitungsartikel).
- **D-19:** **Inventory (SC5)** of the hand-maintained docx/pptx (`final_documents/`): every item (wording, colours, branding, images) is marked carried into the content source, kept manual (intro deck, MHP company profile, per PROJECT.md Out of Scope) or deliberately dropped, with a reason.

### Requirement review (plan-phase, 2026-10-08)
- **D-20:** **Story-text giveaway check = the D-13b list with two exceptions** (user decision). (1) The word **"OT"** is allowed in story texts as a domain term (the Steckbrief uses it in headings and in the clue "kein separates OT-Netz"; the M5 card already prints "OT/IT-Netz-Segmentierung"). Only the attack name "OT-Störung" stays banned, so the attack id `ot` must not match the word "OT" in story texts. (2) The stem **Erpress*** is allowed in story texts as a clue word (e.g. "Erpresser legen Zulieferer lahm"). The veiled attack keys keep the full D-13b list without exceptions.
- **D-21:** **All story texts are veiled**, including the Unternehmenssteckbrief ("Sinumerik" appears twice), not only the Zeitungsartikel and Anfrage-Mail. Audit-Mail is checked after transcription.
- **D-22:** **Assets folder for branding (user decision, refines D-19):** a git-tracked folder for company assets and guidelines (logos, colour palettes, fonts, images, brand guidelines), with a README stating its purpose. The user drops further files there. Inventory items for colours, logos, branding and images are carried into this folder (files extracted or copied, colour/font values recorded in a guidelines file there) or marked kept manual / dropped with a reason. `texte.toml` stays text-only. Exact path: Claude's discretion (suggested `content/assets/`).
- **D-23:** The pre-wave title **"Angriff N" is generated in code from the wave position**; `texte.toml` holds no digit for it, and a scenario variant (SCEN, v4) can reorder attacks without text changes.
- **D-24:** **Print effect lines for event cards are built in Phase 5 (PRINT-06).** Phase 3 only keeps the simulation's effect labels generated from event params (`flat_budget` no longer returns the config description) and shows that every number removed from prose maps to a config param.
- **D-25:** The digit-allowlist entries (D-10) are **reviewed by the user at the PRINT-02 checkpoint**, together with the text-only golden diff (D-08).

### Research follow-up (plan-phase, 2026-10-08, user decisions)
- **D-26:** **Veiled text = title word only.** Each attack keeps a per-attack key `veiled.title = "Angriff"` (hook for v4 scenario hints); no teaser sentence. The number comes from code (D-23).
- **D-27:** **Revealed attack names = worksheet names:** "Ransomware", "OT-Störung", "Datenexfiltration" (as on the printed worksheets and file names; no "(Produktionsausfall)" subtitle).
- **D-28:** **`levels_simple` without the "Grundschutz:/Besser:/Premium:" prefix** (printed-deck wording). The deck's copy-paste errors (M6 L3, M10 L1 showing M2 texts) are not carried over.
- **D-29:** **Backup & Recovery slide text → `[sheets.backup_recovery]`** (explains the M4 recovery mechanic, numbers from `measures.M4.levels.*.recovery` in code); no config event; Phase 5 decides whether it is printed.
- **D-30:** Research defaults (Claude's recommendation, not separately asked; user may override at the checkpoints): single-word table labels (Maßnahme, Level, Summe …) are carried into `texte.toml` as sheet vocabulary; both Zeitungsartikel images are carried into the assets folder (D-22), including the padlock image as a visual clue.

### Claude's Discretion
- Where the digit allowlist lives (TOML header table, separate file or Python constant) and its exact syntax.
- How measure ids in prose (e.g. OEM-Audit "M1 IAM/PAM, M2 …", Nervige Authentifizierung "M1 ≥ Level 2") pass the digit lint: an id pattern such as `M\d+` on the allowlist, generating those references in code, or rewording.
- TOML key names inside each section, and the format of the inventory (markdown table in the phase dir is fine).
- How the coverage check declares the expected `[sheets.*]` keys before the Phase 4/5 templates exist (start with what PRINT-03..10 obviously need; extend in later phases).
- How Audit-Mail.pdf is transcribed (read the image PDF visually).

### Folded Todos
- **"Angriffe und Aktionen nur indirekt vermitteln, nie explizit benennen"** (`.planning/todos/pending/2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md`). Problem: attacks/events named explicitly in player material. Phase 3 delivers the veiled/revealed content (VEIL-01), the veiled story texts and the clue matrix (VEIL-03). Events stay named (D-13c). Close the todo when Phase 5 (VEIL-02, VEIL-04) completes, as STATE.md already notes.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope and prior decisions
- `.planning/PROJECT.md` — Key Decisions (veiling rule 2026-09-29, measure cards CIA-only, LaTeX, single source of truth)
- `.planning/REQUIREMENTS.md` — PRINT-02, VEIL-01, VEIL-03 (this phase); VEIL-02, VEIL-04, PRINT-10, PRINT-12 (Phase 5 consumers); SCEN-04 (v4 per-scenario print)
- `.planning/ROADMAP.md` §Phase 3 — success criteria 1–5
- `.planning/phases/02-rule-changes/02-CONTEXT.md` — D-08 vocabulary, D-09..D-13/D-22/D-23 Kurswechsel rule wording, D-29 legacy generators untouched, 02-07 text-only golden handling
- `.planning/todos/pending/2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md` — folded todo (veiling problem statement)

### Architecture research (content source design)
- `.planning/research/ARCHITECTURE.md` — `content/texte.toml` layout, `texts.py` coverage + digit lint, Pattern 3 (effect lines from type+params), Pattern 4 (audience-scoped view models PRE_ATTACK / REVEAL / FACILITATOR), Anti-Pattern 2
- `.planning/research/PITFALLS.md`, `.planning/research/FEATURES.md` — veiling/clue pitfalls

### Current prose sources (to migrate)
- `simulation_config.json` — `attacks.*.description`, `waves[].name`, `waves[].bonus_measures[].description`, `events.*.description`, `final_events[].description`
- `generate_pptx_cards.py:39` (`MEASURE_META`), `:196` (`ATTACK_NAMES`); `generate_from_template.py:24` (`MEASURE_META` copy)
- `final_documents/Angriff-1_Ransomware.docx`, `Angriff-2_OT-Störung.docx`, `Angriff-3_Datenexfiltration.docx` — revealed narratives, CIA rationale sentences
- `final_documents/Events_Security-Game.pptx` — event narratives
- `final_documents/Unternehmenssteckbrief MechTech.docx`, `Zeitungsartikel.docx` (+ `.pdf`, `Zeitungsartikel_bild_*.png`), `Anfrage-Mail.docx`, `Audit-Mail.pdf` (image-only) — story documents (D-14)
- `final_documents/Massnahmenkarten_Security-Game.pptx`, `Budget.docx`, `Return on Security und Final Wert.docx`, `Planspiel_Einführung + Grundlagen.pptx`, `MHP Company Profile DE - Jubilee Logo.pptx` — inventory scope (D-19)

### Codebase maps
- `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONVENTIONS.md`, `.planning/codebase/TESTING.md`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `planspiel/review_text.py` (`format_eur`, `boundary_text`, `penalty_rows`): the established pattern for generating numeric text from config params. Event effect lines (D-03) follow it.
- `planspiel/config.py` (`load_config`, `check_config`, `_build_event`): the config loader; text fields removed per D-02 must be dropped from the dataclasses/loader.
- `planspiel/validate.py`: config validator; it is the natural home or model for the coverage/lint checks.
- `.planning/phases/02-rule-changes/tools/golden_diff.py`: golden diff tool for the reviewed text-only snapshot change (D-08).
- `tests/test_config_text.py`, `tests/test_encoding_lint.py`: existing text/UTF-8 lint tests to extend or mirror.

### Established Patterns
- TDD with golden characterization tests; snapshot changes only via `--update-golden` after a human-verify checkpoint.
- UTF-8 everywhere with real umlauts (FOUND-04); always `uv run`.
- Single-definition AST guard (`tests/test_single_definition.py`) excludes `generate_*.py`.

### Integration Points
- Sim/balance reports read `waves[].name` / descriptions today: switch them to `attack_id` or short labels when the prose leaves config (D-02).
- Phase 4/5 templates consume `texts.py` through audience-scoped view models (PRE_ATTACK sees only `attacks.*.veiled`).
- `content/clues.toml` feeds the Phase 5 facilitator master sheet (PRINT-10).

</code_context>

<specifics>
## Specific Ideas

- Strong clue candidates already in the Steckbrief: shared office/OT LAN ("kein separates OT-Netz") → OT attack; monthly cloud backup and the reactive virus scanner → attack 1; "Remote-Zugänge durch fünf Lieferanten" and the externally reachable supplier portal → exfiltration; shared admin accounts.
- Zeitungsartikel rewrite should keep its punch (OEM audit pressure, a supplier crippled for days, a suspicious e-mail in accounting, no working backup) without the words "Ransomware" and "Phishing".
- The pre-wave title is "Angriff N", and the reveal reads "Angriff N: <Name>".

</specifics>

<deferred>
## Deferred Ideas

- Generating the story documents as LaTeX: Phase 5 (new PRINT-12).
- VEIL-02 automated scan over rendered pre-wave PDFs (text, file names, metadata): Phase 5.
- Per-scenario story texts and clues: v4 (SCEN-04); the TOML layout should not hard-code a single scenario.

</deferred>

---

*Phase: 03-content-source-veiling*
*Context gathered: 2026-10-06*
