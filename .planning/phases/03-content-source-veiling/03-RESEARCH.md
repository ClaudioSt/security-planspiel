# Phase 3: Content Source & Veiling - Research

**Researched:** 2026-10-08
**Domain:** offline content tooling (stdlib `tomllib` content source, text lints, golden characterization tests, story-document veiling); no runtime, no new dependencies
**Confidence:** HIGH for the code/consumer map, golden procedure and matching rules (all read or executed in this session); MEDIUM for the TOML key design and clue authoring (design recommendations, user review pending at D-13d / D-25)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Carried forward (decided earlier, not re-asked)**
- Attack names are veiled only in material players see **before** a wave and revealed by name when the wave hits. Mechanics (CIA weights, E-value, damage, event effects) stay fully transparent (PROJECT.md Key Decisions, 2026-09-29).
- Measure cards show CIA values, costs and dependencies only. Wave weights and measure→attack bonus links appear only on the revealed attack worksheet (VEIL-04, Phase 5).
- Config is the single source for numbers; order of change is config → README → print material.
- `MEASURE_META` in legacy generators stays untouched until LEG-01 (Phase 2 D-29).

**Content source shape (PRINT-02)**
- **D-01:** One file, **`content/texte.toml`** (stdlib `tomllib`), sections keyed by config id, e.g. `[measures.M1]`, `[attacks.ransomware]`, `[events.kurswechsel]`, `[final_events.budget_review]`, `[sheets.*]`, `[story.*]`. A loader module (research name: `planspiel/texts.py`) loads and validates it.
- **D-02:** **Prose is stripped from `simulation_config.json`.** Attack/event/final-event `description`, `waves[].name` and `waves[].bonus_measures[].description` move to TOML and are removed from config. Config keeps ids, numbers, mechanics and **short technical labels** used by sim/balance reports (e.g. measure `name` "IAM/PAM", event `name`). A wave is identified by its `attack_id`, so nothing in config names an attack in prose.
- **D-03:** **No numbers in TOML prose.** TOML holds only the narrative sentence. Every line with a game number (e.g. "OPEX −2.000 € pro aktiver Maßnahme", "Gesamtbudget −20.000 €", "KZ −10") is **generated from event type + params in code**, following the `planspiel/review_text.py` pattern. No `{param}` placeholders in TOML.
- **D-04:** **Rule texts live in TOML as prose.** For example, the Kurswechsel rule wording (D-09..D-13, D-22, D-23 of Phase 2) and the Sparprogramm end-check sentence go into TOML, with separate keys for `narrative` (story) and `rule` (how it works). Code only generates the numeric effect line.
- **D-05:** **Measure texts are carried over 1:1** from `MEASURE_META`: `focus`, `description`, `levels_desc` (technical), `levels_simple` (plain). No editorial rework now; Phase 5 decides what the card prints.
- **D-06:** Measure texts **may say what they defend against** (e.g. M6 "Phishing abwehren"). Only attack names and wave links are banned from pre-wave material (enforced in Phase 5 by VEIL-02).
- **D-07:** **Legacy generators untouched.** `generate_pptx_cards.py` and `generate_from_template.py` keep their own `MEASURE_META`/`ATTACK_NAMES` copies until they are archived (LEG-01, Phase 7). The single-definition guard already excludes `generate_*.py`.
- **D-08:** Removing text fields from config changes text in the pinned goldens. Handle it as a **reviewed text-only snapshot change, like 02-07**. The executor shows a diff proving only text keys changed (numbers and digests identical) and regenerates via `--update-golden` only after user approval.
- **D-09:** **Coverage check:** fails on any config id (measure, attack, event, final event) without its required TOML keys, and on any orphaned TOML key without a config id (SC1). `[sheets.*]` and `[story.*]` are checked against a declared key list rather than config ids.

**Digit lint (SC2)**
- **D-10:** **Strict:** any digit in `texte.toml` fails the lint, except tokens on an **explicit, reviewed allowlist** of flavor tokens that are not game parameters (e.g. "24/7", "30 Tage", "NIS2"). Each allowlist entry is a conscious decision.
- **D-11:** The lint covers **all of `texte.toml`** (measures, attacks incl. revealed texts, events, sheets), **except the `[story.*]` section** (D-15).
- **D-12:** German number words ("drei Fertigungslinien", "zwei Admins") are **allowed**; the lint checks digits only.

**Veiled vs revealed attack texts (VEIL-01)**
- **D-13:** **Veiled = neutral title only.** Before the wave an attack appears only as **"Angriff 1" / "Angriff 2" / "Angriff 3"**, with no teaser text. All inference comes from the clues in the pre-wave story documents (D-17). On reveal the title becomes "Angriff 1: Ransomware" etc. (matches the existing worksheet naming).
- **D-13a:** **Revealed text per attack** = attack name + scenario narrative (from the current config `description` / `Angriff-*.docx`) + the CIA rationale sentence ("Bei Ransomware zählen C und I stärker …"). Bonus-measure reasons ("EDR/XDR erkennt Ransomware früh") move to TOML as **revealed-only** keys.
- **D-13b:** **Giveaway-term lint** runs on the **veiled attack keys only** (exactly SC3). Banned list = attack names plus core technique terms, matched case-insensitively with word stems: Ransomware, Verschlüsselung/verschlüsselt, Lösegeld, Erpress*, Phishing, Emotet, OT-Störung, SPS, Sinumerik(-Schwachstelle), Exfiltration, Datendiebstahl, Darknet, APT, plus the attack ids. The same list is reused for story texts by the clue/veil check (D-16).
- **D-13c:** **Events are not veiled.** They keep their names (they are drawn after a wave and are rules, not threats to infer). The only constraint is that event texts must not name an upcoming attack. This narrows the todo's "Aktionen" part, consistent with the 2026-09-29 clarification.
- **D-13d:** **Authoring:** Claude drafts the revealed texts (from config/docx) and the veiled story rewrites; the **user reviews them at a checkpoint before commit**.

**Story documents and clue matrix (VEIL-03, SC5)**
- **D-14:** **Story-document prose moves into `texte.toml` now** under `[story.*]`: Unternehmenssteckbrief MechTech, Zeitungsartikel, Anfrage-Mail, Audit-Mail. They are **generated via LaTeX in Phase 5**. This adds requirement **PRINT-12** (story documents generated from the content source) to Phase 5 (REQUIREMENTS.md + ROADMAP amended 2026-10-06). Rationale: two of the four docs name the attack, `Audit-Mail.pdf` is image-only (needs transcription), SCEN-04 (v4) needs per-scenario story docs, and the clue check becomes exact against TOML keys.
- **D-15:** `[story.*]` is **exempt from the digit lint** (world facts such as "ca. 80 Mitarbeitende", "15 Mio. EUR", dates, addresses). Rule: story texts must not state game mechanics or game amounts (budget tiers, KZ, costs).
- **D-16:** **Veil the story texts in this phase.** The Zeitungsartikel (headline "Phishing stoppt Fertigung", "Ransomware legt Zulieferer tagelang lahm", body) and the Anfrage-Mail ("Täglich lesen wir von Ransomware-Angriffen") are rewritten without attack names or giveaway terms while keeping their clue value (e.g. "Erpresser legen Zulieferer lahm", "verdächtige E-Mail in der Buchhaltung"). Claude drafts, the user reviews (D-13d). Story texts are checked against the giveaway list from D-13b.
- **D-17:** **Clue matrix = data file with verbatim quotes:** `content/clues.toml`. Per attack it lists clues as {source key in `texte.toml` `[story.*]` (or other pre-wave key), verbatim quote, why it points to the attack}. The check fails if an attack has fewer than two clues, if a quote is not found verbatim in its source key, or if a source is not pre-wave material. The facilitator view is rendered in Phase 5 (PRINT-10).
- **D-18:** **≥ 2 clues per attack from ≥ 2 distinct source documents** (e.g. Steckbrief + Zeitungsartikel).
- **D-19:** **Inventory (SC5)** of the hand-maintained docx/pptx (`final_documents/`): every item (wording, colours, branding, images) is marked carried into the content source, kept manual (intro deck, MHP company profile, per PROJECT.md Out of Scope) or deliberately dropped, with a reason.

**Requirement review (plan-phase, 2026-10-08)**
- **D-20:** **Story-text giveaway check = the D-13b list with two exceptions** (user decision). (1) The word **"OT"** is allowed in story texts as a domain term (the Steckbrief uses it in headings and in the clue "kein separates OT-Netz"; the M5 card already prints "OT/IT-Netz-Segmentierung"). Only the attack name "OT-Störung" stays banned, so the attack id `ot` must not match the word "OT" in story texts. (2) The stem **Erpress*** is allowed in story texts as a clue word (e.g. "Erpresser legen Zulieferer lahm"). The veiled attack keys keep the full D-13b list without exceptions.
- **D-21:** **All story texts are veiled**, including the Unternehmenssteckbrief ("Sinumerik" appears twice), not only the Zeitungsartikel and Anfrage-Mail. Audit-Mail is checked after transcription.
- **D-22:** **Assets folder for branding (user decision, refines D-19):** a git-tracked folder for company assets and guidelines (logos, colour palettes, fonts, images, brand guidelines), with a README stating its purpose. The user drops further files there. Inventory items for colours, logos, branding and images are carried into this folder (files extracted or copied, colour/font values recorded in a guidelines file there) or marked kept manual / dropped with a reason. `texte.toml` stays text-only. Exact path: Claude's discretion (suggested `content/assets/`).
- **D-23:** The pre-wave title **"Angriff N" is generated in code from the wave position**; `texte.toml` holds no digit for it, and a scenario variant (SCEN, v4) can reorder attacks without text changes.
- **D-24:** **Print effect lines for event cards are built in Phase 5 (PRINT-06).** Phase 3 only keeps the simulation's effect labels generated from event params (`flat_budget` no longer returns the config description) and shows that every number removed from prose maps to a config param.
- **D-25:** The digit-allowlist entries (D-10) are **reviewed by the user at the PRINT-02 checkpoint**, together with the text-only golden diff (D-08).

### Claude's Discretion
- Where the digit allowlist lives (TOML header table, separate file or Python constant) and its exact syntax.
- How measure ids in prose (e.g. OEM-Audit "M1 IAM/PAM, M2 …", Nervige Authentifizierung "M1 ≥ Level 2") pass the digit lint: an id pattern such as `M\d+` on the allowlist, generating those references in code, or rewording.
- TOML key names inside each section, and the format of the inventory (markdown table in the phase dir is fine).
- How the coverage check declares the expected `[sheets.*]` keys before the Phase 4/5 templates exist (start with what PRINT-03..10 obviously need; extend in later phases).
- How Audit-Mail.pdf is transcribed (read the image PDF visually).

### Deferred Ideas (OUT OF SCOPE)
- Generating the story documents as LaTeX: Phase 5 (new PRINT-12).
- VEIL-02 automated scan over rendered pre-wave PDFs (text, file names, metadata): Phase 5.
- Per-scenario story texts and clues: v4 (SCEN-04); the TOML layout should not hard-code a single scenario.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRINT-02 | All German prose lives in one content source keyed by config id; printed numbers are never typed into prose (plus ROADMAP SC5: inventory of hand-maintained docx/pptx, no own REQ-ID, mapped here) | Sections "TOML schema", "Digit lint", "Config strip consumer map", "Golden procedure", "Inventory", "Assets folder"; appendix `03-RESEARCH-APPENDIX-STORY-SOURCE.md` holds all verbatim source prose |
| VEIL-01 | Config/content hold separate veiled (pre-attack) and revealed (at-wave) texts per attack | Section "Veiled vs revealed representation" (per-attack `veiled`/`revealed` sub-tables, audience views, title generated from wave position), "Giveaway matching" |
| VEIL-03 | A facilitator clue matrix shows every attack is inferable from at least two clues in the pre-wave material | Sections "Story veiling" (current hits, rewrite feasibility), "Clue matrix" (`content/clues.toml` schema, checks, draft clue candidates with verbatim quotes) |
</phase_requirements>

## Summary

Phase 3 is a pure text-and-lint phase: no rule or number may change. The work is (1) a UTF-8 TOML content source (`content/texte.toml`) plus a loader/lint module `planspiel/texts.py` that reuses the existing `Issue` type, (2) stripping prose from `simulation_config.json` with a small, fully mapped set of code edits (config dataclasses, validator, two lines in `rules.py`, one return-signature change, ~9 test sites), (3) a reviewed text-only golden change, (4) veiled story rewrites plus a verbatim-quote clue file, and (5) an inventory and a git-tracked assets folder. The code surface is small: only `rules.py:298` (flat_budget label), `rules.py:94-100/146/171/435/430` (bonus descriptions, wave name) and the config loader/validator touch prose. Legacy generators are safe: nothing imports the stripped fields at import time, only `tests/test_legacy_generators_smoke.py` asserts `waves[1]["name"]` and needs a one-line retarget to an event name.

Three findings change the assumptions in the orchestrator brief. (a) The printed event narratives in `Events_Security-Game.pptx` differ from the config `description` texts; the pptx narrative is digit-free (except two "Prüft die Umsetzung von M4/M7" sentences) and is the correct migration source, with the current config `description` supplying only the *rule* sentences (Kurswechsel, Sparprogramm end-check). The pptx also holds a "Backup & Recovery" event that has no config entry. (b) The hand-maintained `Massnahmenkarten_Security-Game.pptx` contains two copy-paste errors (M6 L3 and M10 L1 show M2 texts) and prints the `levels_simple` text WITHOUT the "Grundschutz:/Besser:/Premium:" prefix that `generate_pptx_cards.py` carries; the two `MEASURE_META` copies are not identical. (c) The Steckbrief carries template residue (header "Projekthandbuch" + WMF logo, footer "- 54 © Stand 07.05.2002 © 2000-2002 Solutions GmbH") that must be dropped, and the two Zeitungsartikel images are OpenAI-generated (C2PA credentials, no prompt text) with the ransomware lock-screen image itself being a visual clue.

The giveaway lint is specified exactly in "Giveaway matching": lower-cased NFC text, dash and zero-width normalisation, substring match for terms of 5+ letters (covers prefixes, hyphenated and inner compounds and umlaut forms), whole-token match for short terms (`sps`, `apt`, id `ot`), and a phrase rule for `OT[-\s]*Stör`. The story profile removes token `ot` and substring `erpress`. A runnable prototype against 27 must-pass/must-fail strings passed 27/27, and scanning the real story texts reproduces the known hit list (Steckbrief 2, Zeitungsartikel 5 lines, Anfrage-Mail 1, Audit-Mail 1) so VEIL-03 has a ready RED test.

**Primary recommendation:** one plan per requirement in the order PRINT-02 → VEIL-01 → VEIL-03; PRINT-02 migrates ALL prose verbatim (story texts un-veiled, giveaway lint not yet wired on `story.*`), VEIL-01 adds the veiled/revealed structure, audience views and giveaway lint on veiled keys and events, VEIL-03 wires the story giveaway check RED (known hits) then rewrites to GREEN and adds `content/clues.toml` with its checks.

## Architectural Responsibility Map

This project is offline tooling, so tiers are modules, not browser/server tiers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Numbers, ids, mechanics, short technical labels | `simulation_config.json` + `planspiel/config.py` | `planspiel/validate.py` | Single source for numbers; D-02 keeps names/labels, drops prose |
| German prose (measures, attacks, events, sheets, stories) | `content/texte.toml` | `planspiel/texts.py` | Templates must contain layout only; one place for wording |
| Number-bearing text lines (effect lines, "Angriff N") | Code (`rules.py` labels, `review_text.py` pattern, `texts.attack_title`) | — | D-03/D-23: numbers never typed into prose |
| Coverage, digit, giveaway, clue checks | `planspiel/texts.py` (+ CLI `planspiel texts` / `planspiel clues`) | `tests/` | Mirrors `validate` for config; fails fast, exit code 1 |
| Audience scoping (pre-attack never sees revealed keys) | `planspiel/texts.py` view classes | Phase 5 templates | Veiling by construction (ARCHITECTURE.md Pattern 4) |
| Digit allowlist, giveaway term list, clue matrix data | `content/*.toml` data files | — | Reviewable data, user edits without touching code |
| Branding assets and guidelines | `content/assets/` | Phase 4/5 LaTeX | D-22; `texte.toml` stays text-only |
| Golden text-only proof | throwaway script in phase dir + `tests/golden` | `pytest --update-golden` | D-08, 02-07 precedent |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `tomllib` (stdlib) | Python 3.12.14 in project venv [VERIFIED: `uv run python`] | Read `content/*.toml`; open in binary mode (`tomllib.load(open(p, "rb"))`) | No dependency; supports multiline strings and comments; CRLF input verified to give identical results as LF [VERIFIED: local run, both line endings gave `'A\nB'` and a correctly trimmed line-ending backslash] |
| `unicodedata`, `re`, `dataclasses` (stdlib) | 3.12 | NFC normalisation, token/phrase matching, loader dataclasses | Same style as existing `planspiel/*.py` |
| `pytest` | 9.1.1 (pinned in `pyproject.toml`) [VERIFIED: pyproject.toml] | TDD for all new modules | Already the project test runner; baseline `551 passed, 19 deselected` in 24 s [VERIFIED: ran 2026-10-08] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `python-pptx` | 1.0.2 (existing runtime pin) | Only if the executor re-reads pptx | Not needed; the appendix holds the verbatim text |
| `python-docx` | 1.2.0, ephemeral via `uv run --with python-docx` [VERIFIED: ran] | Only if the executor re-extracts docx | Not needed; do NOT add to `pyproject.toml`/`uv.lock` (verified: `git status` stayed clean after ephemeral use) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Per-attack `veiled`/`revealed` sub-tables in one TOML | Separate files per audience | One file keeps coverage and key paths simple (D-01) |
| Allowlist `[[allow]]` array in a data file | Regex such as `M\d+` | A regex silently allows future game numbers; per-key exact tokens make each entry a conscious decision (D-10) |
| Substring match for long giveaway terms | Word-start prefix only | Prefix misses inner compounds such as "Datenverschlüsselung"; substring is stricter and simpler, false positives are impossible for the 12 long terms in the scoped keys |

**Installation:** none. No new runtime or dev dependency.

**Version verification:** Python 3.12.14, uv 0.12.5, git 2.43.0, Node 24.11.1 present [VERIFIED: ran]. `python-docx 1.2.0` imported OK under `uv run --with`.

## Package Legitimacy Audit

No external package is installed by this phase. Two packages were checked because the research used them ephemerally.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| python-pptx | PyPI | existing pin (1.0.2, published 2024-08-07) | n/a (seam returned null) | github.com/scanny/python-pptx | SUS (unknown-downloads only) | Already a project dependency (Phase 1); no action |
| python-docx | PyPI | 1.2.0 (published 2025-06-16) | n/a (seam returned null) | github.com/python-openxml/python-docx | SUS (unknown-downloads only) | NOT added to the project. Ephemeral `uv run --with` only, optional, not required because the appendix contains all extracted text |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** python-pptx, python-docx (seam reason is only "unknown-downloads", both have well-known source repos). If the planner wants an executor to re-run docx extraction, insert a `checkpoint:human-verify` before the first `uv run --with python-docx`. Recommended: do not re-extract.

## Architecture Patterns

### System Architecture Diagram

```
                 content/texte.toml ──┐     content/digit_allowlist.toml ─┐
                 content/giveaway_terms.toml ─┐                           │
                 content/clues.toml ─┐        │                           │
                                     ▼        ▼                           ▼
simulation_config.json ──► config.load_config ──► texts.load_texts ──► texts.check_*  ──✖ fail: Issue list, exit 1
 (numbers, ids, labels)        │                       │                  │
                               │                       │                  └─► CLI: planspiel texts | planspiel clues
                               ▼                       ▼
                         rules.* (labels from    audience views
                         params, no prose)       ├─ PreAttackView  (attacks.*.veiled, story.*, measures.*, sheets pre-wave)
                               │                 ├─ RevealView     (attacks.*.revealed, bonus_reasons)
                               ▼                 └─ FacilitatorView(clue matrix, both)
                        tests/golden (text-only        │
                        change, D-08)                  ▼
                                              Phase 4/5 templates (consume views only)
```

### Recommended Project Structure
```
content/
├── texte.toml                 # all German prose, keyed by config ids (UTF-8)
├── digit_allowlist.toml       # [[allow]] key / token / why  (user-reviewed, D-25)
├── giveaway_terms.toml        # banned terms + story exceptions (D-13b, D-20)
├── clues.toml                 # [[clue]] attack / source / quote / why (D-17)
└── assets/
    ├── README.md              # purpose, how to add files, provenance rules
    ├── GUIDELINES.md          # colours, fonts, page geometry, layout notes
    └── images/                # zeitungsartikel_bild_*.png (copied, see Assets)
planspiel/
├── texts.py                   # load, required_keys, check_coverage/digits/giveaway/clues, views, attack_title
└── cli.py                     # + `texts` and `clues` subcommands (existing pattern)
tests/
├── fixtures/mini_texte.toml (+ mini_clues.toml)
├── test_texts_loader.py  test_texts_coverage.py  test_texts_digits.py
├── test_texts_giveaway.py  test_texts_views.py  test_clues.py
├── test_config_prose_removed.py  test_texts_migration.py  test_inventory.py
.planning/phases/03-content-source-veiling/
├── 03-INVENTORY.md            # SC5 deliverable (draft table below)
└── tools/golden_text_diff.py  # throwaway proof script (02-07 precedent, committed)
```

### Pattern 1: TOML schema (keys per section)

Top-level tables and required keys (the coverage spec lives in `texts.required_keys(cfg)`; keys are derived from the typed `Config` so a new measure/attack/event id immediately fails coverage):

| Section | Required keys per id | Source of current text |
|---------|---------------------|------------------------|
| `measures.<Mx>` | `focus`, `description`, `levels_desc.1..3`, `levels_simple.1..3` | `generate_pptx_cards.py:39` `MEASURE_META` (`levels_desc` only exists there), `levels_simple` from `generate_from_template.py` copy (printed wording, no level prefix; see A1) |
| `attacks.<id>.veiled` | `title` (neutral word, see VEIL-01 section) | new |
| `attacks.<id>.revealed` | `name`, `narrative`, `cia_rationale`, `case_1`, `case_2`, `case_3`, `bonus_reasons.<Mx>` for every `waves[].bonus_measures` entry of that attack | `Angriff-*.docx` (scenario, CIA rationale, per-case sentence) and config `bonus_measures[].description` |
| `events.<id>` | `narrative`; by type also `rule`, `checklist_heading` (checklist_tier), `tier_labels.<n>` for every key of `params.tiers` (measure_level_tier) | pptx narrative; config `description` supplies `rule` for `kurswechsel` and `sparprogramm` |
| `final_events.<id>` | `narrative` | pptx slide 9 narrative (config description is a one-liner) |
| `sheets.*` | declared list in `texts.SHEET_KEYS` (seed below) | docx/pptx inventory |
| `story.<doc>` | `doc_title` plus free-form named blocks (`heading`, `text` or `bullets`) | verbatim in the appendix |

Event keys by type (derive from `cfg.events`/`final_events`):

| Event id | type | `narrative` source | other keys |
|----------|------|--------------------|-----------|
| kurswechsel | kurswechsel | pptx slide 2 with `Maßnahmenwechsel` → `Maßnahmentausch` | `rule` = current config description (digit-free, vocabulary test already exists) |
| operative_unterstuetzung | opex_discount_per_active_measure | pptx slide 3 | `rule` = "Zählt für jede bestehende Maßnahme in der kommenden Runde" |
| sparprogramm | flat_budget | pptx slide 4 | `rule` = end-check sentence from config ("Geprüft wird das Restbudget erst am Ende; … Init wird nicht erstattet") |
| oem_audit | checklist_tier | pptx slide 5 | `checklist_heading` = "Audit Checkliste"; code appends "(mindestens auf Level 1)" and the M1..M7 list from `params` + `measures.*.name` |
| kritische_schwachstelle | measure_level_tier | pptx slide 6, reworded: drop "Prüft die Umsetzung von M7." | `tier_labels.0..3` = "Patch verzögert/chaotisch", "Patch gelingt, aber mit Reibung", "Patch planbar und zügig", "Patch routiniert, mit Nachweis/Reporting" |
| exzellenz_bonus | level_bonus_per_measure | pptx slide 7 (no digits) | none (code builds "Für jede Maßnahme auf Level 3 … +5 KZ") |
| nervige_authentifizierung | and_condition | pptx slide 8 | none (code builds the condition line from `clauses`) |
| budget_review | final_budget_tier | pptx slide 9 | table lines via `review_text.boundary_text` |
| (not in config) Backup & Recovery | — | pptx slide 1, drop "Prüft die Umsetzung von M4." | `[sheets.backup_recovery]` with `narrative`, `level_0..3` labels ("kein Recovery", "Basis-Recovery", "teilw. Recovery", "starke Recovery"); numbers from `measures.M4.levels.*.recovery` (A13) |

Example (shape only, values from the appendix):
```toml
# content/texte.toml  (UTF-8)
[measures.M1]
focus = "Zugriffskontrolle, privilegierte Accounts"
description = "Wer darf was im Unternehmen? ..."
[measures.M1.levels_desc]
1 = "Zentrale AD, MFA für Admins, Passwortrichtlinie"
[measures.M1.levels_simple]
1 = "Zentrale Benutzerverwaltung, Admins brauchen zwei Faktoren zum Einloggen."

[attacks.ransomware.veiled]
title = "Angriff"
[attacks.ransomware.revealed]
name = "Ransomware"
narrative = "Ein Mitarbeiter hat auf eine gefälschte E-Mail geklickt. ..."
cia_rationale = "Bei Ransomware zählen Vertraulichkeit (C) und Integrität (I) stärker (...)"
case_1 = "Eure Maßnahmen reichen nicht aus, der Angriff setzt sich durch."
[attacks.ransomware.revealed.bonus_reasons]
M3 = "EDR/XDR erkennt Ransomware früh"

[events.sparprogramm]
narrative = "Der CFO verkündet ein konzernweites Sparprogramm, ..."
rule = "Geprüft wird das Restbudget erst am Ende; ..."
```
TOML notes: bare numeric keys (`1 = "..."`) are valid and arrive as string keys `"1"`; tomllib preserves file order (documents keep their block order); avoid line-ending backslashes, use plain multiline `"""` strings.

**`[sheets.*]` seed list** (what the inventory shows PRINT-03..10 need; extend per phase, coverage fails on missing/orphaned):
- `sheets.angriff`: `start_values_intro` (reworded without "10"), `cia_table_instruction`, `e_value_intro`, `bonus_intro`, `case_3_hint` ("Berechnet Schaden und KZ:"), table `labels` (Maßnahme, Level, Basisschutz, Summe, Ab Level, Bonus, Erfüllt, Gesamtbonus, Gesamtreduktion, Schaden, Kundenzufriedenheit)
- `sheets.budget`: `intro`, `cost_types` rows (Init-Kosten/OPEX: `what`, `when`), `tier_intro`, `anticipated_sum_intro`, `status_tracker_intro`, labels (Zeitraum, Maßnahmen, Antizipierte Summe, Status-Tracker, Start, Nach Welle)
- `sheets.ros`: `instruction`, `purpose`, row labels (Gesamt Init-Kosten, Gesamt OPEX Kosten, Schaden, Summe Event-Strafen, Gesamtkosten, Vermiedener Schaden); "Schaden Angriff 1" is `label` + code-generated attack title
- `sheets.backup_recovery`: see table above

### Pattern 2: Veiled vs revealed representation (VEIL-01, D-13, D-23, SCEN-04)

Tension to surface: D-13 says veiled = neutral title only, no teaser, and D-23 says the digit comes from code, so the only veiled content per attack is the word "Angriff". SC3/VEIL-01 still demand "a veiled text per attack". Recommendation: keep the key per attack (`attacks.<id>.veiled.title = "Angriff"`), because it is the hook for v4 scenario-specific hints and keeps the audience split structural; do NOT invent teaser prose. All real inference value lives in `story.*` (VEIL-03). Flag to the user as Open Question 1.

```python
# planspiel/texts.py (sketch)
def attack_title(texts, attack_id, position, *, revealed=False) -> str:
    base = texts.get(f"attacks.{attack_id}.veiled.title")          # "Angriff"
    if not revealed:
        return f"{base} {position}"                                 # "Angriff 1"
    return f"{base} {position}: {texts.get(f'attacks.{attack_id}.revealed.name')}"  # "Angriff 1: Ransomware"

class PreAttackView:    # exposes only veiled keys + story + measures + pre-wave sheets; no `revealed` accessor exists
class RevealView:       # revealed keys, bonus_reasons
class FacilitatorView:  # both + clue matrix
```
`position` is `Wave.wave_id` (1..n, contiguous, validator-enforced), passed in by the caller, so a v4 scenario can reorder attacks with no text change and nothing hard-codes "three attacks" or "one scenario". Enforcement test: for each attack, no string reachable from `PreAttackView` contains `revealed.name`, the attack id, or any bonus reason; and `hasattr(PreAttackView, "revealed")` is false.

### Pattern 3: Effect labels generated from params (D-03, D-24)

`rules.evaluate_event` already builds labels from params for every type except `flat_budget`. Change `rules.py:298` to `return 0, 0, p["budget_delta"], f"Gesamtbudget {p['budget_delta']}k€"` (same k€ style as the siblings, e.g. `f"{active} aktive Maßnahmen x {p['opex_per_measure']}k€"`; A4). Print effect lines stay Phase 5 (PRINT-06). The `kurswechsel` branch keeps its hard-coded German sim label (rules.py:295); it is a simulation report label with no digits, not print material, so leave it (documented exception).

### Anti-Patterns to Avoid
- **`{param}` placeholders in TOML:** forbidden by D-03. Split sentences around numbers: prose in TOML, number part in code.
- **A regex allowlist like `M\d+`:** lets any game number through. Reword and generate measure references from `params.measure(s)` and `measures.*.name`.
- **`str.casefold()` for matching:** folds `ß` to `ss` and requires casefolding the term list too; `lower()` on both sides plus explicit ASCII-transliteration terms is simpler and symmetric.
- **Reading TOML via `read_text()` or `open(p)` without `"rb"`:** violates `tests/test_encoding_lint.py`'s intent; use `tomllib.load(open(p, "rb"))` (binary mode is exempt from the encoding lint).
- **Putting a "name" or reveal text into any structure a pre-wave view can reach.**

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| TOML parsing, multiline strings | custom parser / JSON with `\n` | `tomllib` | Handles CRLF, escapes, ordering |
| Issue reporting | new result type | `planspiel.validate.Issue(level, code, path, message)` and the CLI print pattern of `_validate_command` | Same output/exit-code conventions |
| German number/amount formatting | f-string hacks | `planspiel.review_text.format_eur`, `boundary_text` | Existing, golden-tested |
| Golden diff output and classification | custom JSON differ | `tests/support/golden.py` (`flatten`, `_same`, `diff_lines`, `check_golden`) | Already type-aware and domain-readable |
| Unicode/umlaut/dash normalisation | per-term hacks | `unicodedata.normalize("NFC")` + a dash/zero-width translate table | Docx text arrives with U+00AD, U+2011, U+2212 |
| docx/pptx text extraction | new extractor in the repo | the appendix (already extracted) | No new dependency, no re-extraction |

**Key insight:** every hard part already has a precedent in `planspiel/` or `tests/support/`; the phase adds a data layer and lints, not new machinery.

## Runtime State Inventory

This phase migrates prose out of config (a refactor/migration), so all five categories are answered.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `tests/golden/characterization_{low,medium,high}.json` contain `wave_name`, `bonus_descriptions`, Sparprogramm `effect_description` [VERIFIED: read]. `digest_*.json` and `gate_*.json` contain no text. Gitignored big caches `sim_low/med/high.json`, `simulation_summary_*.json` are legacy outputs read only by `analyze_simulation_results.py` | Golden: reviewed text-only change (data migration of snapshots). Caches: none, regenerate on demand |
| Live service config | None. No external service, no UI-held configuration | None, verified by repo structure (offline tooling) |
| OS-registered state | None. No scheduled tasks, services or env registrations | None |
| Secrets/env vars | None. No `.env`, no secret keys reference these names | None |
| Build artifacts / installed packages | `angriff_berechnung.xlsx` (committed) and `pptx_output/*.pptx` embed old wave names and config descriptions; `__pycache__` | Not regenerated (D-07). Retired in Phase 7 (LEG-01). `tests/test_legacy_generators_smoke.py` asserts the XLSX mtime unchanged, keep that |

**Code edit vs data migration:** the config strip and loader changes are code edits; `tests/golden/*.json` is the only data migration (regenerated under the D-08 procedure).

## Config strip: consumer map (file:line) [VERIFIED: grep + read 2026-10-08]

| File:line | Today | Change |
|-----------|-------|--------|
| `planspiel/config.py:26` | `BonusMeasure.description: str` | remove field |
| `planspiel/config.py:32` | `Wave.name: str` | remove field (wave identified by `attack_id`/`wave_id`) |
| `planspiel/config.py:66-67` | `Event.name`, `Event.description` | keep `name` (short label), remove `description` |
| `planspiel/config.py:93-96` | `_build_event` reads `ev["description"]`; params exclude `description` | stop reading `description`; params exclusion tuple becomes `("id", "name", "type")`; a stray `description` is rejected by the validator so it cannot leak into params |
| `planspiel/config.py:154, 160` | `description=bm["description"]`, `name=wave["name"]` | drop both |
| `planspiel/validate.py:323` | `text_value(field(wave, "name"))` required | replace with prose-in-config error |
| `planspiel/validate.py:349` | `bonus_measures[].description` required | replace with prose-in-config error |
| `planspiel/validate.py:429-430` | event `name` required, `description` required | keep `name`; `description` becomes forbidden |
| `planspiel/validate.py:210` | measure `name` required | unchanged (D-02 keeps it) |
| `planspiel/validate.py:114-119` | `removed_key` is a warning with E-Ziel wording | add a new error `schema.prose_in_config` ("Prosa gehört nach content/texte.toml") for `attacks.*.description`, `waves[].name`, `bonus_measures[].description`, `events/final_events[].description`; error not warning so prose cannot creep back (A3). `test_shipped_configs_have_exactly_the_known_slope_warning` stays green because the real config is clean |
| `planspiel/rules.py:88-100` | `compute_bonus_reduction` returns `(bonus, descriptions)` | return `int` only; update `rules.py:146` and the two `bonus, _ =` callers at `rules.py:741`, `:854`. `tests/test_single_definition.py:33` pins only the name |
| `planspiel/rules.py:171, 435, 430` | records carry `bonus_descriptions`, `wave_name` | remove both keys (no consumer outside goldens; `attack` id is already in the record) |
| `planspiel/rules.py:298` | `flat_budget` returns `event.description` | `f"Gesamtbudget {p['budget_delta']}k€"` |
| `simulation_config.json` | `attacks.*.description` (3), `waves[].name` (3), `bonus_measures[].description` (8), `events.*.description` (7), `final_events[0].description` (1); `_comment_events` stays | delete the 22 prose fields; keep event `name`, measure `name` |
| `tests/fixtures/mini_config.json` | same prose fields (lines 28-91, 105, 119, 323-418) | strip identically |
| `tests/test_config_text.py:10-30, 117-118` | `_display_strings` iterates `wave.name`, `bonus.description`, `event.description`; asserts bonus text and `waves[1]["name"]` | iterate config names plus all TOML strings; mojibake and transliteration lints move to TOML too; retarget the umlaut test to `attacks.ot.revealed.name == "OT-Störung"` |
| `tests/test_kurswechsel.py:176, 258-263, 273-284` | positional `Event("x","X","text","flat_budget",...)`; raw `description` vocabulary and digit asserts; retired-term sweep over `event.description`, `wave.name`, `bonus.description` | `Event` loses a positional arg; vocabulary/digit asserts run on `events.kurswechsel.narrative/rule` in TOML (real config only, mini has no TOML); sweep covers all TOML strings |
| `tests/test_sparprogramm.py:113-118, 184-189` | `Event(... description="Test" ...)`; asserts description text | drop kwarg; assert `events.sparprogramm.rule` in TOML |
| `tests/test_budget_review_text.py:113-117` | asserts no digits in final-event `description` | drop (global digit lint covers it) |
| `tests/test_rules_semantics.py:53` | `cfg.waves[1].name == "OT-Störung"` | `cfg.waves[1].attack_id == "ot"` |
| `tests/test_rules_exact.py:104`, `tests/test_kernel_conformance.py:133`, `tests/test_e_target_removed.py:21` | synthetic raw events with `"description"` | remove the key (otherwise the new validator error fires) |
| `tests/test_legacy_generators_smoke.py:18, 22` | asserts `waves[1]["name"] == "OT-Störung"` through the legacy generators | retarget to `config["events"]["wave_1"][1]["name"] == "Operative Unterstützung"` (umlaut-bearing field that stays). Purpose (FOUND-04 UTF-8 decode through legacy loaders) preserved |
| `tests/golden/characterization_*.json` | see golden procedure | text-only change |

**Legacy generator risk (D-07/D-29):** `generate_attack_calculator.py` reads `wave_data['name']` (`:45`), `bm['description']` (`:83`), `wave['name']` (`:464`) inside functions only, and is already KeyError-broken on `kz_bonus` since 02-01; module import only loads the JSON, so the smoke test still imports it. `generate_pptx_cards.py:521` uses `.get("description", "")`, so it would print blank event descriptions instead of crashing; `generate_from_template.py` only calls `load_config()`. Minimal handling: leave all three untouched and retarget the one smoke assertion. Record the degraded legacy output in the plan summary; Phase 7 archives them.

## Golden procedure (D-08, 02-07 precedent) [VERIFIED: read 02-07-SUMMARY, golden support, test_characterization.py]

What changes in `tests/golden/characterization_*.json` (61 to 63 cases per tier, 58 to 60 of them valid): per wave the keys `wave_name` and `bonus_descriptions` disappear, and the Sparprogramm `effect_description` becomes `Gesamtbudget -20k€`. Digest and gate goldens contain no text and must stay byte-identical. 02-07 did this with a throwaway script diffing the goldens field by field against HEAD, then the user chose the option; here the approval comes BEFORE any rewrite (D-08 literal).

Executor steps:
1. Baseline: `uv run pytest -q` green (551 passed, 19 deselected); note `git rev-parse HEAD`.
2. Implement the strip (RED: golden tests fail, the new tests fail until code is done). Do NOT run `--update-golden` yet.
3. Run `.planning/phases/03-content-source-veiling/tools/golden_text_diff.py` (new, modelled on `02-rule-changes/tools/golden_diff.py`). It rebuilds every golden case in memory exactly like `test_golden_sample_matches` (`harness.evaluate(cfg, tier, harness.selection_of(cfg, code))`, then `expected_of`), flattens old (disk) and new with `tests.support.golden.flatten`, and classifies each differing path:
   - allowed: `expected.waves[i].wave_name` (present → `<missing>`), `expected.waves[i].bonus_descriptions` or `...[j]` (present → `<missing>`), `expected.waves[i].events[j].effect_description` only where the event id is `sparprogramm` (old text → `Gesamtbudget -20k€`)
   - everything else must satisfy `_same(old, new)`; any other difference is "unexpected" and the script exits 1.
   It prints per tier and pattern the number of changed fields (02-07 reported 59/58/60 for one field) and `unexpected: 0`.
4. Also run `uv run pytest -m slow tests/test_digest.py -q` WITHOUT `--update-golden` (all 782,336 combinations per tier; proves numbers, damage, costs, kz-after unchanged by digest equality) and the fast `tests/test_overspend_gate.py` golden compare. A slow run of both files was started in this session; the slow suite as a whole was ~21 min in Phase 2 (02-VALIDATION.md), the digest part is a fraction of that [ASSUMED runtime].
5. USER CHECKPOINT (D-25): show the script report, the 7-entry digit allowlist and the `Gesamtbudget` label; user approves in the same checkpoint.
6. Only then `uv run pytest --update-golden`; re-run the script (expects zero differences now, i.e. files equal the in-memory documents) and `git diff --stat tests/golden` shows exactly the three characterization files; `uv run pytest -q` green. Commit goldens in one explicit commit (01-06/02-07 precedent).
7. If `unexpected > 0`, fix the code, never widen the allowed patterns.

## Digit lint (SC2, D-10..D-12, D-15) [VERIFIED: scanned MEASURE_META, pptx, docx]

Scope: every string value (and list-of-string element) in `texte.toml` except the top-level table `story`. Keys are not checked (bare digit keys like `1 = "..."` are fine). Use `ch.isnumeric()` (superset of `isdigit`, also catches `½`, superscripts, Roman-numeral glyphs).

Allowlist location: `content/digit_allowlist.toml`, one reviewed entry per occurrence:
```toml
[[allow]]
key = "measures.M2.levels_desc.1"
token = "30 Tage"
why = "Aufbewahrungsdauer der Protokolle, kein Spielparameter"
```
Rules: the lint removes each allowed token from that key's string and fails if any digit remains; it also fails on a stale entry (key missing or token not present), so the allowlist cannot rot. The seven entries needed for a 1:1 measure carry (everything else in measures is digit-free):

| Key | Token | Note for the user review |
|-----|-------|--------------------------|
| `measures.M2.levels_desc.1` | `30 Tage` | log retention |
| `measures.M2.levels_simple.1` | `30 Tage` | same fact in plain wording |
| `measures.M2.levels_desc.3` | `24/7` | SOC availability |
| `measures.M4.levels_desc.1` | `14 Tage` | backup retention |
| `measures.M4.levels_desc.2` | `3-2-1` | backup rule name ("3-2-1-Regel") |
| `measures.M4.levels_desc.3` | `<4h` | RTO target |
| `measures.M6.levels_desc.1` | `30 Min` | e-learning length |

Review flag: "14 Tage", "30 Tage", "<4h", "30 Min" look like parameters although none is in config; D-12 offers number words as the alternative (rewording breaks 1:1, D-05).

Digit-bearing prose elsewhere and its handling (every removed number maps to a config param, D-24):

| Where | Removed number | Handling | Config param |
|-------|----------------|----------|--------------|
| event operative_unterstuetzung (config text) | "−2.000 EUR" | line generated | `params.opex_per_measure = -2` (k€) |
| event sparprogramm (config text) | "−20.000 EUR" | line generated | `params.budget_delta = -20` |
| event oem_audit (config text) | "M1 … M7", "Level 1" | list/level generated | `params.measures`, `params.min_level`, `measures.*.name` |
| event kritische_schwachstelle (config + pptx) | "(M7)", "Prüft die Umsetzung von M7" | reword narrative, generated condition line | `params.measure`, `params.tiers` |
| Backup & Recovery (pptx) | "M4", "0,90/0,70/0,50" | reword, generated | `measures.M4.levels.*.recovery` |
| event exzellenz_bonus (config) | "Level 3", "+5 KZ" | line generated | `params.level`, `params.kz_per_measure` |
| event nervige_authentifizierung (config) | "M1 >= Level 2", "M6 = Level 0", "KZ -10" | line generated | `params.clauses[0].min_level`, `clauses[1].level_eq`, `params.kz_delta` |
| Angriff sheets | "Basiswert von 10" | reword to "Basiswert" (table row shows 10) | `base_cia` |
| Angriff sheets | "Angriff 1", "Fall 1/2/3", "(1 / 2 / 3)", "M__" | code/layout | wave position, case index, levels |
| Budget/RoS sheets | "Schaden Angriff 1", "Events 1", "620.000", tier table | generated | wave position, `rules.base_losses`, `budget_tiers` |

No `M\d+` pattern allowance is needed (A14).

## Giveaway matching (D-13b, D-20) [VERIFIED: prototype run, 27/27 must-pass/must-fail correct]

Data file `content/giveaway_terms.toml` (terms pinned by a test against the D-13b list):
```toml
substrings = ["ransomware", "verschlüssel", "verschluessel", "lösegeld", "loesegeld", "erpress",
              "phishing", "emotet", "exfil", "datendiebstahl", "darknet", "sinumerik"]
tokens = ["sps", "apt"]                 # whole-token only, too short for substring
compounds = [["ot", "stör"], ["ot", "stoer"]]   # OT-Störung in any dash/space form
[story_exceptions]                      # D-20
tokens = ["ot"]
substrings = ["erpress"]
```
Attack ids from config (`ransomware`, `ot`, `exfil`) are added at runtime: ids with 5+ letters as substrings (already covered), ids of 4 letters or fewer as whole tokens (`ot`).

Algorithm:
1. `n = unicodedata.normalize("NFC", text)`, translate U+2010-2015 and U+2212 to `-`, delete U+00AD and U+200B/C/D/FEFF, then `.lower()` (not `casefold`, see Anti-Patterns).
2. Substring terms: hit if `term in n` (covers word-start prefixes, hyphenated compounds "Ransomware-Angriff", inner compounds "Datenverschlüsselung", umlaut forms and ASCII transliterations).
3. Tokens: `re.findall(r"[^\W\d_]+", n)`; hit if a banned token is in the list (so "OT/IT-Netz" yields `ot`, "Hotel" does not).
4. Compounds: regex `(?<![^\W\d_])ot[\s-]*st(?:ö|oe)r` (so "OT-Störung", "OT‑Störung", "OT Störungen" hit; "Störung in der OT" does not).
5. Profiles: `veiled` = full list, no exceptions (veiled attack keys, VEIL-01); `story` = list minus `story_exceptions` (story texts, VEIL-03, and event/final-event texts per D-13c, A7).
6. Also run the existing transliteration patterns (`tests/test_config_text.py` `TRANSLITERATION_PATTERNS`) over every TOML string, so "Loesegeld" style slips fail even in unscoped keys.

Must-pass / must-fail table for tests:

| Input | veiled profile | story profile |
|-------|----------------|---------------|
| `Ransomware legt Zulieferer lahm`, `Ransomware-Angriff`, `Anti-Ransomware`, `RANSOMWARE` | fail | fail |
| `Datenverschlüsselung`, `Die Daten wurden verschlüsselt`, `VERSCHLÜSSELUNG`, `Verschluesselung` | fail | fail |
| `Lösegeldforderung`, `Loesegeld`, `Phishing-Mail`, `Sinumerik-Schwachstelle`, `12 CNC-Steuerungen (Sinumerik/Heidenhain)`, `Datenexfiltration`, `im Darknet angeboten` | fail | fail |
| `OT-Störung`, `OT‑Störung` (U+2011), `OT Störungen im Werk` | fail | fail |
| `SPS-Steuerung`, `APT-Gruppe` | fail | fail |
| `Erpresser legen Zulieferer lahm` | fail | pass |
| `OT/IT-Netz, kein separates OT-Netz`, `OT / Produktion` | fail | pass |
| `Eine Störung in der Produktion`, `Schaden durch Ausfall der Fertigung`, `Spaß und Spiele`, `Apotheke, Kapt'n, Optik`, `Hotel, Pilot, Robot` | pass | pass |

## Story veiling and clue matrix (VEIL-03) [VERIFIED: scan of verbatim story texts with the prototype]

Current giveaway hits under the story profile (these are the RED expectations for VEIL-03):

| Document | Hits |
|----------|------|
| Unternehmenssteckbrief | `sinumerik` in "CNC-Steuerungen u. a.: Siemens Sinumerik, Heidenhain" and "12 CNC-Steuerungen (Sinumerik/Heidenhain)"; the word "OT" (headings "IT-/OT-Landschaft", "OT / Produktion", clue "kein separates OT-Netz") passes by D-20 |
| Zeitungsartikel | masthead `phishing`; headline `ransomware`; body "Ransomware-Angriffs"; "Phishing-Mail" and "verschlüsselte"; "Lösegeld" (and "Erpresser-Software" passes by D-20) |
| Anfrage-Mail | "Täglich lesen wir von Ransomware-Angriffen" |
| Audit-Mail (transcribed) | "(insb. Ransomware, Supply-Chain-Angriffe)" |

Feasible rewrites that keep clue value (Claude drafts at the D-13d checkpoint, examples only): masthead "Verdächtige E-Mail stoppt Fertigung"; headline "Erpresser legen Zulieferer tagelang lahm"; "Opfer eines schweren Cyberangriffs"; "gefälschte E-Mail, die ein Mitarbeiter in der Buchhaltung öffnete"; "Die Erpresser-Software sperrte … Office-Daten"; "Die Angreifer forderten 250.000 Euro in Bitcoin"; Steckbrief "Siemens, Heidenhain"; Anfrage-Mail "Täglich lesen wir von Cyberangriffen auf Unternehmen unserer Größe und Branche"; Audit-Mail "(insb. Erpressung, Supply-Chain-Angriffe)". Non-text clue: the factory image (`Zeitungsartikel_bild_fabrik.png`) shows a padlock ransom screen; that is a deliberate visual clue and must keep a neutral file name and caption ("Stillstand in der Fertigung nach Cyberangriff").

`content/clues.toml` (flat `[[clue]]` array, grouped by attack at check time):
```toml
[[clue]]
attack = "ot"
source = "story.steckbrief.it_ot_produktion.bullets"   # a key in texte.toml; value is a string or a list of strings
quote = "Office-IT und OT/Produktion nutzen dasselbe LAN (kein separates OT-Netz)"
why = "Kein getrenntes Produktionsnetz: ein Angriff im Büro erreicht die Fertigung."
```
Checks (`texts.check_clues(cfg, texts, clues)`, Issue codes `clues.*`):
1. For every `attack_id` in `cfg.waves` (not hard-coded to three): at least two clues (`clues.too_few`).
2. Clues of one attack come from at least two distinct documents (`clues.single_source`); document = `story.<doc>` segment, or `measures` for `measures.*` sources (D-18).
3. `source` resolves to a key in `texte.toml` and `quote` is a verbatim substring of one string at that key after NFC only, no case folding (`clues.quote_not_found`); this also fails if the source was edited and the clue forgot to follow.
4. `source` starts with a declared pre-wave prefix (`story.`, `measures.`); `attacks.*.revealed`, `sheets.angriff` etc. are rejected (`clues.not_prewave`).
5. `attack` is a config attack (orphan check), `why` non-empty, `quote` at least 15 characters (no one-word "quotes").

Matrix output: `uv run planspiel clues` prints a Markdown table (attack name from `FacilitatorView`, clue number, document title from `story.<doc>.doc_title`, section heading, verbatim quote, why) and exits 1 when the check fails; no generated file is committed (stale-file risk). Phase 5 renders it as PRINT-10.

Draft clue candidates that survive the veil rewrite (verbatim substrings of the CURRENT texts, so the clue file can be authored before the Zeitungsartikel rewrite and re-verified after):

| Attack | Clue (document) | Quote |
|--------|-----------------|-------|
| ransomware | Steckbrief | `Cloud-Backup: Veeam für Office-Daten (monatliche Sicherung)` |
| ransomware | Anfrage-Mail | `Wir haben einen Virenscanner und Backups, aber keine strukturierte Security-Strategie.` |
| ransomware | Zeitungsartikel | `Wir hatten kein funktionierendes Backup-Konzept` (quote without the typographic quotation marks) |
| ot | Steckbrief | `Office-IT und OT/Produktion nutzen dasselbe LAN (kein separates OT-Netz)` |
| ot | Steckbrief | `Unterbrechungen > 4 Stunden wirken sich unmittelbar auf Auslieferungen aus` (same document, so it cannot be the second distinct source) |
| ot | Zeitungsartikel | `Drei Fertigungslinien standen still` |
| ot | Audit-Mail | `OT-Segmentierung` is shorter than 15 characters: use the surrounding bullet line or quote `Patch Management` plus `OT-Segmentierung` as separate clues of length ≥ 15 only if the bullet is stored as one string |
| exfil | Steckbrief | `Remote-Zugänge durch fünf Lieferanten (u. a. MES, CAD, IT)` |
| exfil | Steckbrief | `Lieferanten-Portal: extern erreichbare Web-Applikation` |
| exfil | Anfrage-Mail | `wissen wir auch nicht genau, wer aktuell überall administrativen Zugriff auf unsere Systeme hat` |
| exfil | Zeitungsartikel | `Supply Chain Security ist geschäftskritisch` |

All three attacks reach at least two clues from at least two distinct documents with text that needs no rewriting; the executor finalises the set at the user checkpoint.

Optional cheap guard (A16, discretionary): a "mechanics vocabulary" lint on `story.*` rejecting `KZ`, `Kundenzufriedenheit`, `OPEX`, `Init-Kosten`, `Budget-Tier`, `RoS`, `E-Wert`, `Level \d`, backing D-15's "story texts must not state game mechanics". The current story texts contain none of these (checked by eye against the appendix; the planner should add the test only after a scan).

## Assets folder (D-22) and guidelines [VERIFIED: extracted theme/XML from the pptx/docx files]

Path: `content/assets/` (git-tracked, outside the Python package; `texts.py` locates `content/` relative to the repo root and takes an optional path argument for tests).

- `README.md`: purpose ("company assets and guidelines for the generated print material; `texte.toml` stays text-only"), how to add files (drop them in `images/`, `logos/`, `fonts/`, `brand/`), rule that each file's origin/licence is recorded in the README table, and that the pre-wave material must not use file names or metadata naming an attack (Phase 5 VEIL-02 scans).
- `GUIDELINES.md`: carried design facts:
  - MHP theme (Massnahmenkarten and Events pptx, name "MHP"): dk1 `262626`, dk2 `575757`, lt2 `B0B0B0`, accent1 `000099`, accent2 `1612FF`, accent3 `CDD6FF`, accent4 `DDEF03`, accent5 `00CC67`, accent6 `575757`, hyperlink `262626`; font Segoe UI; slide size 13.33 x 7.50 in.
  - Card semantics: level badge fill L1 = accent5 `00CC67`, L2 = accent4 `DDEF03`, L3 = accent6 `575757`, badge text white 32 pt; dependency label/value `C00000`; headings accent1; event narrative accent2 28 pt, rules 24 pt, title 40 pt.
  - Word sheets: Arial (Office theme: accent1 `5B9BD5`, accent2 `ED7D31`, accent3 `A5A5A5`, accent4 `FFC000`, accent5 `4472C4`, accent6 `70AD47`), A4, margins L 3.0 cm (punch margin), R 1.5, T 2.0, B 2.0 cm, title 12 pt, body 10 pt.
  - Zeitungsartikel: masthead "AUTO TIMES" Georgia 48 pt, serif body 9.5 pt, two columns with separator, grayscale images, US Letter 21.6 x 27.9 cm, margins 1.8/1.5 cm; Anfrage-Mail Calibri 11 pt, Letter.
  - Fonts Segoe UI, Georgia, Calibri, Arial are Windows system fonts: Phase 4 must decide embeddable alternatives for reproducible LuaLaTeX builds.
- `images/zeitungsartikel_bild_audit.png`, `zeitungsartikel_bild_fabrik.png`: COPY from `final_documents/` (md5 `9d607b19…` audit, `2557114b…` fabrik, byte-identical to the images embedded in `Zeitungsartikel.docx`). Copy, do not move, so `final_documents/` stays untouched until LEG-01 (A15). Provenance note for the README: both PNGs carry C2PA content credentials issued through OpenAI's media service and no prompt text [VERIFIED: PNG chunk scan]; both are grayscale, 1448 x 1086.
- Not copied: the two personal photos `DanielGhebreselassie 1.jpg` and `Stanullo Claudio_2022_04.jpg` (speaker portraits for the intro deck; keep manual, no reason to duplicate personal images into a reusable assets folder), MHP logos and MHP template media (embedded in the MHP pptx decks, kept manual).
- No MechTech logo exists in any source file. The Steckbrief WMF header image is template residue (see Inventory), so Phase 5 starts without a MechTech logo unless the user drops one into `content/assets/logos/`.

## Inventory (SC5, D-19): draft for `03-INVENTORY.md`

Disposition vocabulary: **carried→TOML** (key in `texte.toml`), **carried→assets**, **generated** (Phase 4/5 produces it from config, nothing to carry), **kept manual**, **dropped**. A `tests/test_inventory.py` check asserts every file in `final_documents/` appears in the table with one of these values.

| File | Item | Disposition | Reason / target |
|------|------|-------------|-----------------|
| `Unternehmenssteckbrief MechTech.docx` | all body prose (11 headings, bullets) | carried→TOML | `story.steckbrief.*`, veiled (D-21): "Sinumerik" ×2 removed |
| same | header "Projekthandbuch" + WMF logo (`word/media/image1.wmf`), footer "- 54 © Stand 07.05.2002 © 2000-2002 Solutions GmbH" | dropped | template residue from an unrelated 2002 document, wrong branding |
| same | layout: A4, margins L 2.5 / T 4.0 / B 1.8 cm (T 4.0 was reserved for that header), Arial theme, 12 pt title, 10 pt body | carried→assets | `GUIDELINES.md`; top margin to be re-evaluated in Phase 5 |
| `Zeitungsartikel.docx` | masthead "AUTO TIMES", dateline, ticker, 3 articles, captions, quotes | carried→TOML | `story.zeitungsartikel.*`, rewritten without Phishing/Ransomware/verschlüsselt/Lösegeld |
| same | footer "Aktuelles Seite 1", Georgia type scale, 2-column layout with separator, Letter size | carried→assets (layout facts), Letter size dropped | LaTeX is A4; recorded as an A15 style decision for Phase 5 |
| same | embedded images image1/image2 | carried→assets | identical to the two `Zeitungsartikel_bild_*.png` |
| `Zeitungsartikel.pdf` | export of the docx | dropped | regenerated by PRINT-12; also carries the un-veiled text |
| `Zeitungsartikel_bild_audit.png`, `_fabrik.png` | images | carried→assets | `content/assets/images/` (copy) |
| `Anfrage-Mail.docx` | mail header lines, body, task list, signature | carried→TOML | `story.anfrage_mail.*`, "Ransomware-Angriffen" rewritten, "Beratungs-projekt" fixed |
| `Anfrage-Mail.pdf` | export | dropped | regenerated by PRINT-12 |
| `Audit-Mail.pdf` | image-only mail | carried→TOML | transcribed in the appendix; "Ransomware" rewritten; original kept until LEG-01 |
| `Angriff-1/2/3_*.docx` | headings, scenario paragraph, CIA rationale, per-case sentences, shared instructions, table labels | carried→TOML | `attacks.*.revealed.*` and `sheets.angriff.*` |
| same | thresholds, caps, bonus values, damage/KZ formulas, "Basiswert von 10", Fall 1/2/3 numbers | generated | Phase 4 (PRINT-03); numbers come from config (print-sync trap removed) |
| same | bonus-table short labels (M3 - EDR/XDR, M5 - Netz-Segmentierung, …) | dropped (labels), decision for Phase 4 | config `measures.*.name` or a short-label key |
| `Budget.docx` | intro, cost-type explanations, tier paragraph, tracker prose, table labels | carried→TOML | `sheets.budget.*` |
| same | tier table values, "Angriff 1/Events 1" rows | generated | PRINT-07 |
| `Return on Security und Final Wert.docx` | instruction, purpose, row labels | carried→TOML | `sheets.ros.*`; "Final Wert" part is missing in the source, PRINT-07 adds it |
| same | "620.000", formulas | generated | `rules.base_losses`, rules module |
| `Events_Security-Game.pptx` | 9 event narratives, subtitle "Event: Nach Welle N", rule lines, tier labels | carried→TOML | `events.*`, `final_events.*`, `sheets.backup_recovery` |
| same | effect lines (−2.000 €, KZ ±) | generated | PRINT-06 (D-24) |
| same | MHP template, Segoe UI, accent colours | carried→assets | `GUIDELINES.md` |
| same | retired term "Maßnahmenwechsel" | dropped | RULE-01 vocabulary |
| `Massnahmenkarten_Security-Game.pptx` | focus, description, level text per card (30 slides) | carried→TOML | `measures.*` via `MEASURE_META` (identical except 3 slides) |
| same | M6 L3 and M10 L1 slide texts | dropped | copy-paste errors (show M2 texts) |
| same | CIA, cost, dependency lines | generated | PRINT-05 from config |
| same | level badge colours, red dependency colour | carried→assets | `GUIDELINES.md` |
| `Planspiel_Einführung + Grundlagen.pptx` | intro deck (37 slides, MHP branding, speaker bios) | kept manual | PROJECT.md Out of Scope; observations for LEG-02: slide 36 "Spielplan / Vorlage für die Pinnwand" still shows a 150.000 € budget, "Ransomware" as Angriff 1 and "Phishing" as Angriff 2 next to the label "Angriff"; whiteboard is removed by FLOW-02; "Beratungsteam aus 3–4 Personen" vs project format |
| `MHP Company Profile DE - Jubilee Logo.pptx` | company profile | kept manual | Out of Scope (MHP-branded) |
| `13052026_VWI meets MHP_Offenes Treffen.pptx` | unrelated talk deck (33 slides) | kept manual | not game material |
| `DanielGhebreselassie 1.jpg`, `Stanullo Claudio_2022_04.jpg` | speaker photos | kept manual | personal images for the intro deck, not copied |

## Common Pitfalls

### Pitfall 1: "text-only" golden change that hides a number change
**What goes wrong:** `--update-golden` rewrites everything, including an accidental numeric drift.
**Why it happens:** the golden test diff output is capped at 30 lines.
**How to avoid:** the in-memory classifier script with an allow-list of three path patterns, the slow digest test without the update flag, user approval before rewrite.
**Warning signs:** any changed path outside `wave_name`, `bonus_descriptions`, Sparprogramm `effect_description`.

### Pitfall 2: veil leaks through structure, not text
**What goes wrong:** the revealed name reaches a pre-wave document through a shared key, file name, image or metadata.
**How to avoid:** audience views with no `revealed` accessor, a leak test over every reachable string, neutral asset file names, and (Phase 5) VEIL-02.
**Warning signs:** `attacks.<id>.name` placed outside `revealed`; wave bonus reasons stored on measures.

### Pitfall 3: digits in rule sentences nobody classified as game numbers
**What goes wrong:** sentences like "Basiswert von 10" or "Prüft die Umsetzung von M7" fail the lint late.
**How to avoid:** the digit table above; reword in TOML, generate the number in code; the lint runs in the first RED test over the full migrated file.

### Pitfall 4: allowlist rot
**What goes wrong:** an edit removes "30 Tage" but the allowlist entry survives and later hides a real game number in that key.
**How to avoid:** stale-entry failure (key missing or token absent).

### Pitfall 5: verbatim quote drift
**What goes wrong:** story edit changes a sentence; the clue silently no longer points anywhere.
**How to avoid:** the quote-substring check runs after NFC on the exact stored string; typographic quotation marks in the source ("„…“") must be excluded from quotes.

### Pitfall 6: encoding and line endings on Windows
**What goes wrong:** cp1252 default decoding or CRLF in multiline strings.
**How to avoid:** `tomllib.load(open(path, "rb"))` only; no line-ending backslashes; the Windows machine has `core.autocrlf=true`, `tests/golden/*.json` is pinned `eol=lf` in `.gitattributes`: add `content/*.toml text eol=lf` for stable diffs [ASSUMED useful].

### Pitfall 7: single-scenario hard-coding (SCEN-04)
**What goes wrong:** `story` keys named after the ransomware scenario, "three attacks" loops, or title digits in TOML.
**How to avoid:** loop over `cfg.waves`, titles from position, clue file keyed by attack id, story blocks named by topic.

## Code Examples

### Coverage derived from the typed config (sketch)
```python
# Source: derived from planspiel/config.py dataclasses [VERIFIED: codebase]
def required_keys(cfg: Config) -> set[str]:
    keys = set()
    for mid in cfg.measures:
        keys |= {f"measures.{mid}.focus", f"measures.{mid}.description"}
        keys |= {f"measures.{mid}.levels_{kind}.{n}" for kind in ("desc", "simple") for n in (1, 2, 3)}
    for wave in cfg.waves:
        for bm in wave.bonus_measures:
            keys.add(f"attacks.{wave.attack_id}.revealed.bonus_reasons.{bm.measure}")
    for aid in cfg.attacks:
        keys |= {f"attacks.{aid}.veiled.title", f"attacks.{aid}.revealed.name", ...}
    ...
    return keys   # orphan = leaf keys in texte.toml not in required_keys | optional_keys | SHEET_KEYS | story keys
```

### Digit lint with allowlist (sketch)
```python
def check_digits(texts, allow):
    for path, value in texts.leaf_strings(skip_top=("story",)):
        remaining = value
        for token in allow.get(path, ()):
            if token not in remaining:
                yield Issue("error", "texts.allowlist_stale", path, f"Token {token!r} nicht im Text")
            remaining = remaining.replace(token, "")
        if any(ch.isnumeric() for ch in remaining):
            yield Issue("error", "texts.digit", path, f"Ziffer im Text: {remaining!r}")
```

### Test-first order for PRINT-02 (TDD RED list)
`test_texts_loader` (loads fixture, UTF-8 umlauts survive) → `test_texts_coverage` (real file passes; deleting `measures.M3.focus` gives `texts.missing_key`; adding `measures.M99.focus` gives `texts.orphan_key`) → `test_texts_digits` → `test_config_prose_removed` (validator error, dataclass fields gone, `flat_budget` label, removed-number ledger) → golden proof → migration fidelity (below).

### Migration fidelity test (retire with LEG-01)
```python
# parse MEASURE_META with ast.literal_eval from generate_pptx_cards.py / generate_from_template.py
# (no import side effects), assert texte.toml equals them: focus/description/levels_desc from pptx_cards,
# levels_simple equals the from_template copy; levels_simple of pptx_cards equals it after stripping
# "Grundschutz: " / "Besser: " / "Premium: ".
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Prose inside `simulation_config.json` descriptions with embedded numbers | Prose in `content/texte.toml`, numbers generated in code | this phase | Removes print/sim mismatch sources (22 prose fields) |
| Attack names in config and every pre-wave document | Veiled title "Angriff N" + clue documents; name only in `revealed` | this phase | Players infer, never read |
| Hand-maintained docx/pptx wording | Single content source, templates (Phase 4/5) contain layout only | Phase 3 → 5 | One edit point |

**Deprecated/outdated:** `description`/`name` prose fields in config (removed), `Maßnahmenwechsel` (retired term, still in the old event pptx), the whiteboard "Pinnwand" slide.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Store `levels_simple` WITHOUT the "Grundschutz:/Besser:/Premium:" prefix (printed deck wording), `levels_desc` from `generate_pptx_cards.py` | TOML schema | User wants the prefix text 1:1 from the generator copy: add prefix back, trivial |
| A2 | Veiled per-attack key is `veiled.title = "Angriff"` only, no neutral sentence | Veiled representation | User wants an identical neutral sentence on every veiled attack: add key `intro` |
| A3 | New validator code `schema.prose_in_config` is an error, not a warning | Consumer map | User prefers tolerant warning: use `removed_key` style |
| A4 | `flat_budget` label `Gesamtbudget -20k€` | Pattern 3 | Different wording: only the three golden text lines change |
| A5 | Substring matching (stricter than word-start prefixes) for terms of 5+ letters | Giveaway matching | Too strict if a benign word ever contains a term; none found in the real texts |
| A6 | `sps`, `apt`, id `ot` match as whole tokens only | Giveaway matching | Embedded forms like "SPS-Steuerung" still hit via token split; compound "Cyber-APT" also hits |
| A7 | Event and final-event narratives get the story-profile giveaway check (D-13c) | Giveaway matching | Extra test could flag benign wording; real texts currently clean |
| A8 | Letter paper size of Zeitungsartikel/Anfrage-Mail is dropped in favour of A4 | Inventory | User wants Letter: carry as layout fact |
| A9 | Steckbrief header/footer template residue is dropped | Inventory | Unlikely wrong |
| A10 | python-docx not needed by the executor | Standard Stack | Executor wastes time re-extracting |
| A11 | Allowlist is a data file with per-key `[[allow]]` entries | Digit lint | Python constant would also work |
| A12 | Runtime of the slow digest check is minutes per tier (Phase 2 measured ~21 min for the whole slow suite) | Golden procedure | Longer wait for the checkpoint |
| A13 | Backup & Recovery event text lives in `[sheets.backup_recovery]` since it has no config event | TOML schema | Could become a config event in Phase 5 |
| A14 | Measure ids in prose are avoided by rewording and generated lines, no `M\d+` allowance | Digit lint | Event narratives need ids: add them to the allowlist case by case |
| A15 | Copy (not move) the two PNGs; Letter-to-A4 | Assets | 3.7 MB duplicated until LEG-01 |
| A16 | Optional story "mechanics vocabulary" lint | Story veiling | Skip if not wanted |

## Open Questions

1. **What is the veiled text, really?**
   - What we know: D-13/D-23 reduce it to the title word; SC3 and VEIL-01 say "a veiled text per attack".
   - What's unclear: whether the user wants one neutral sentence per attack in addition.
   - Recommendation: ship `veiled.title` only; raise at the VEIL-01 checkpoint.
2. **Attack display names:** printed headings say "OT-Störung (Produktionsausfall)" and "Datenexfiltration"; config says "OT-Störung" and "Exfiltration".
   - Recommendation: `revealed.name` = "Ransomware" / "OT-Störung" / "Datenexfiltration" (printed worksheet names, file names `Angriff-3_Datenexfiltration`); decide at D-13d.
3. **Measure level wording:** prefix or not (A1).
4. **Table-label vocabulary in TOML:** whether single-word labels (Maßnahme, Level, Summe) belong to `texte.toml` or stay template layout. Recommendation: carry them (SC1 "sheet instructions", FLOW vocabulary consistency).
5. **Backup & Recovery as an event card:** the pptx has it, config does not (A13). Phase 5 owner decides whether to print it.
6. **Zeitungsartikel images:** keep both, including the padlock image? (visual ransomware clue; recommended keep).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| uv | all commands | yes | 0.12.5 | none needed |
| Python (project venv) | `tomllib`, tests | yes | 3.12.14 | none needed |
| git | commits, golden diff | yes | 2.43.0 | none needed |
| pytest | tests | yes | 9.1.1 | none needed |
| python-docx (ephemeral) | optional re-extraction | yes via `uv run --with` | 1.2.0 | use the appendix |
| LaTeX/MiKTeX | not this phase | n/a | n/a | Phase 4 |

**Missing dependencies with no fallback:** none. **Missing with fallback:** none.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 |
| Config file | `pyproject.toml` (`testpaths = ["tests"]`, `addopts = "-m 'not slow' --strict-markers"`, marker `slow`) |
| Quick run command | `uv run pytest -q` (551 passed, 19 deselected, ~25 s today; new tests add well under 5 s) |
| Full suite command | `uv run pytest -q && uv run pytest -m slow -q` (~21 min slow, only digests needed for D-08: `uv run pytest -m slow tests/test_digest.py -q`) |
| Extra gates | `uv run planspiel validate` (0 errors, the known 17/7 warning stays), `uv run planspiel texts` (new, exit 0), `uv run planspiel clues` (new, exit 0 after VEIL-03) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PRINT-02 | `texte.toml` loads as UTF-8, umlauts and typographic quotes survive, CRLF-safe | unit | `uv run pytest tests/test_texts_loader.py -q` | ❌ Wave 0 |
| PRINT-02 | coverage fails on missing key and orphan key; real file passes | unit + mutation | `uv run pytest tests/test_texts_coverage.py -q` | ❌ Wave 0 |
| PRINT-02 | digit lint: digits fail, allowlisted tokens pass, stale entry fails, `story` exempt, German number words pass | unit | `uv run pytest tests/test_texts_digits.py -q` | ❌ Wave 0 |
| PRINT-02 | config has no prose; validator error `schema.prose_in_config`; dataclass fields gone; `flat_budget` label generated; removed-number ledger maps to params | unit | `uv run pytest tests/test_config_prose_removed.py -q` | ❌ Wave 0 |
| PRINT-02 | 1:1 migration fidelity vs both `MEASURE_META` copies and vs the pre-strip config numbers | unit | `uv run pytest tests/test_texts_migration.py -q` | ❌ Wave 0 |
| PRINT-02 | golden change is text-only | script + slow | `uv run python .planning/phases/03-content-source-veiling/tools/golden_text_diff.py` and `uv run pytest -m slow tests/test_digest.py -q` | ❌ Wave 0 |
| PRINT-02 (SC5) | every `final_documents/` file listed in the inventory with a valid disposition | unit | `uv run pytest tests/test_inventory.py -q` | ❌ Wave 0 |
| PRINT-02 | updated old tests green (config_text, kurswechsel, sparprogramm, budget_review_text, rules_semantics, legacy smoke) | regression | `uv run pytest -q` | ✅ exist, need edits (list in consumer map) |
| VEIL-01 | `attack_title` gives "Angriff 1" / "Angriff 1: Ransomware"; reorder keeps working; no digit in TOML | unit | `uv run pytest tests/test_texts_views.py -q` | ❌ Wave 0 |
| VEIL-01 | PreAttackView leak test: no revealed name, id or bonus reason reachable | unit | `uv run pytest tests/test_texts_views.py -q` | ❌ Wave 0 |
| VEIL-01 | giveaway matcher table (must-pass/must-fail), veiled keys clean, event narratives clean (D-13c), term list pinned to D-13b | unit | `uv run pytest tests/test_texts_giveaway.py -q` | ❌ Wave 0 |
| VEIL-03 | story texts pass the story profile (RED first with the 9 known hits, then GREEN after rewrite) | unit | `uv run pytest tests/test_texts_giveaway.py -k story -q` | ❌ Wave 0 |
| VEIL-03 | clue check: ≥ 2 per attack, ≥ 2 documents, verbatim, pre-wave source, orphan attack, mutation cases | unit | `uv run pytest tests/test_clues.py -q` | ❌ Wave 0 |
| VEIL-03 | CLI `planspiel clues` prints the matrix and exits 0/1 | integration | `uv run pytest tests/test_clues.py -k cli -q` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest -q` (≈ 30 s) plus the task's own test file.
- **Per wave merge:** quick suite, `uv run planspiel validate`, `uv run planspiel texts`.
- **Phase gate:** quick suite green, `uv run pytest -m slow tests/test_digest.py -q` green without `--update-golden`, all user checkpoints done, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_texts_loader.py`, `test_texts_coverage.py`, `test_texts_digits.py`, `test_texts_giveaway.py`, `test_texts_views.py`, `test_clues.py`, `test_config_prose_removed.py`, `test_texts_migration.py`, `test_inventory.py`
- [ ] `tests/fixtures/mini_texte.toml` (and `mini_clues.toml`) small enough to hand-verify, mirroring the existing `mini_config.json`
- [ ] `.planning/phases/03-content-source-veiling/tools/golden_text_diff.py`
- [ ] Framework install: none (pytest already present)

## Security Domain

`security_enforcement` is enabled (absent = enabled). This is offline content tooling; most ASVS categories do not apply.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes (repo-controlled TOML/JSON, CLI paths) | `tomllib` strict parse, fail-closed lints that exit 1, no `eval`; extraction via `ast.literal_eval` only |
| V6 Cryptography | no | none used (md5 only to compare image copies) |
| V12 Files | yes (asset copy, image metadata) | verify copies by checksum; scan pre-wave assets for names/metadata (C2PA manifest present, no text) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Information leakage of attack names to players (the domain-relevant "disclosure") | Information disclosure | audience views, giveaway lint, leak test, neutral file names; Phase 5 VEIL-02 scan of rendered PDFs and metadata |
| Silent edit of untrusted/updated docx content via ephemeral package | Tampering / supply chain | no new dependency; `uv run --with` only optional and gated behind `checkpoint:human-verify` |
| Prose creeping back into config | Tampering (integrity of single source) | validator error `schema.prose_in_config` |

## Sources

### Primary (HIGH confidence)
- Repository, read and executed this session: `planspiel/{config,validate,rules,review_text,cli}.py`, `tests/**`, `simulation_config.json`, `tests/golden/*.json`, `tests/support/golden.py`, `.planning/phases/02-rule-changes/tools/golden_diff.py`, `02-07-SUMMARY.md`, `02-VALIDATION.md`, `final_documents/*` (docx/pptx/pdf extracted with python-docx 1.2.0 / python-pptx 1.0.2; `Audit-Mail.pdf` and `Zeitungsartikel.pdf` read visually).
- `.planning/research/ARCHITECTURE.md` (content source layout, Pattern 3 and 4), `.planning/research/PITFALLS.md` (Pitfall 10), `.planning/research/FEATURES.md` (T10).
- Local runs: `tomllib` CRLF/LF behaviour, giveaway prototype (27 strings), baseline `uv run pytest -q`.

### Secondary (MEDIUM confidence)
- `gsd-tools query package-legitimacy check` (verdict SUS only because download counts were unavailable).

### Tertiary (LOW confidence)
- Slow-test runtime estimate (A12).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, stdlib only, nothing new.
- Architecture / consumer map: HIGH, grep and read of every consumer; one planner decision (A3) on error vs warning.
- Golden procedure: HIGH, mirrors a completed precedent and the actual golden structure.
- Giveaway semantics: HIGH, executable prototype and real-text scan.
- TOML key design, clue authoring, veiled text content: MEDIUM, design choices awaiting the D-13d/D-25 user checkpoint.
- Pitfalls: HIGH.

**Research date:** 2026-10-08
**Valid until:** 2026-11-07 (stable internal codebase; invalid if Phase 2 follow-ups change the event schema)

## Plan structure and assignment

One PLAN.md per requirement (user rule), order PRINT-02 → VEIL-01 → VEIL-03. The evidence supports the suggested split with these refinements:

**PRINT-02 (largest; keep as ONE plan, 6 tasks):**
1. RED/GREEN `planspiel/texts.py` loader, `required_keys`, `check_coverage` on `tests/fixtures/mini_texte.toml`; CLI `planspiel texts`.
2. RED/GREEN digit lint + `content/digit_allowlist.toml` machinery.
3. Config strip + `compute_bonus_reduction` signature + `flat_budget` label + validator error + mini config + the nine old test sites; golden proof script; **user checkpoint** (golden diff + allowlist, D-08/D-25); then `--update-golden`.
4. Migrate all non-story prose verbatim into `texte.toml` (measures from both `MEASURE_META` copies, attack revealed texts and bonus reasons, event narratives/rules, sheets seed, backup_recovery) with migration-fidelity tests.
5. Migrate the four story documents verbatim (un-veiled) from the appendix, including the Audit-Mail transcription; `story.*` not yet giveaway-linted (stated in the test with a comment so VEIL-03 turns it on).
6. `content/assets/` (README, GUIDELINES, copied images) and `03-INVENTORY.md` with `tests/test_inventory.py`.

**VEIL-01 (small):** veiled/revealed key structure (`veiled.title`), `attack_title`, audience views and leak test, `content/giveaway_terms.toml` + matcher on veiled keys and events; user review checkpoint for revealed texts (D-13d) and the veiled-text question (Open Question 1, 2).

**VEIL-03:** RED story giveaway check (nine known hits), veiled story rewrites, user review checkpoint (D-13d), GREEN; `content/clues.toml` + `check_clues` + `planspiel clues`.

**Why not move the story transcription into VEIL-03:** the transcription and the verbatim migration are PRINT-02 scope (D-14, "all prose"); keeping them there gives VEIL-03 a clean RED (known hits against real text) and keeps the rewrite diff reviewable as a pure veil edit. The cost is one commit in which `story.*` still contains the original giveaway words; it is never printed in this phase (Phase 5 generates the PDFs), so no leak occurs.

## Project Constraints (from CLAUDE.md)

- Always `uv run`; never the `python` on PATH (Inkscape interpreter); tests `uv run pytest` (fast) / `-m slow` (full enumeration).
- Config is the single source of numbers; order of change is config → README → print material. No fixed numbers in prose documents without config sync (binding for `final_documents/`).
- Legacy generators stay untouched until LEG-01; the single-definition AST guard excludes `generate_*.py`.
- Golden snapshot changes only via `--update-golden` after a human-verify checkpoint.
- UTF-8 everywhere with real umlauts (FOUND-04); text I/O must declare `encoding=` (`tests/test_encoding_lint.py`), binary mode for `tomllib`.
- Hand-calculability: worksheet formulas stay linear; this phase changes no formula.
- Code identifiers English; facilitator/player-facing output German; conventional commits; TDD for features; one plan per requirement; review requirements for gaps before planning (done in the brief review).
- Do not modify `final_documents/` binaries by hand; generated outputs only via generators.
