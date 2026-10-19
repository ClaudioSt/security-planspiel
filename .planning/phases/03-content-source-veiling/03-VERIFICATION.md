---
phase: 03-content-source-veiling
verified: 2026-10-19T12:30:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
gaps: []
deferred:
  - truth: "Rendered pre-wave material (PDFs, file names, metadata) is scanned for attack names and wave CIA weights"
    addressed_in: "Phase 5"
    evidence: "REQUIREMENTS.md VEIL-02 (Phase 5); 03-03-PLAN scope boundary"
  - truth: "sheets.budget.init_when ('Einmal zu Spielbeginn') is outdated since RULE-02"
    addressed_in: "Phase 5"
    evidence: "Flagged in 03-01-SUMMARY and content/INVENTORY.md for PRINT-07; see warning W2"
---

# Phase 3: Content Source & Veiling Verification Report

**Phase Goal:** All German prose exists once, in a content source keyed by config id, with separate veiled and revealed attack texts. Templates then contain only layout, and players can infer the coming attack but never read its name.
**Verified:** 2026-10-19
**Status:** passed
**Re-verification:** No, initial verification

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All print prose in one UTF-8 content source keyed by config id; coverage check fails on missing or orphaned keys | VERIFIED | `content/texte.toml` carries measures, attacks, events, final_events, sheets, story. My own check: all 10 `MEASURE_META` entries (focus, description, `levels_desc` 1..3) from `generate_pptx_cards.py` equal the TOML values (diff empty). `simulation_config.json` has no prose string over 40 characters except the developer `_comment_events`. Mutation probes on copies of `content/`: an orphan `[measures.M99]` gives `ERROR texts.orphan_key`, deleting `attacks.ransomware.veiled.title` gives `ERROR texts.missing_key`, both exit 1. `uv run planspiel texts` gives 0 Fehler. |
| 2 | A lint fails if narrative prose contains digits | VERIFIED | Mutation probe: `title = "Angriff 7"` gives `ERROR texts.digit`, exit 1. Real content: exactly 7 non-story strings contain digits (30 Tage x2, 24/7, 14 Tage, 3-2-1, <4h, 30 Min), all on the reviewed 7-entry `content/digit_allowlist.toml` with reasons. Stale entries fail by design (`tests/test_texts_digits.py`). |
| 3 | Each attack has a veiled pre-attack text and a revealed at-wave text; veiled texts hold no attack names or listed giveaway terms | VERIFIED | Each of ransomware, ot, exfil has `[attacks.<id>.veiled] title = "Angriff"` plus `attacks.<id>.revealed.*`. My independent `giveaway_hits(..., profile="veiled")` on all three veiled titles returns `[]`. All story strings pass the story profile (no hit). `PreAttackView` has no reveal accessor, and `tests/test_texts_views.py` holds the leak test. Attack number comes from the wave position (`attack_title(texts, id, position)`), not TOML. |
| 4 | Facilitator clue matrix, at least two clues per attack with location, and a check that fails below two | VERIFIED | `uv run planspiel clues` prints 14 clues (ransomware 4, ot 5, exfil 5), each with document, section, verbatim quote and reason, exit 0. Mutation probe: a clues file with one `ot` clue gives `ERROR clues.too_few clues.ot`, exit 1. Quote-verbatim, distinct-document and pre-wave-source checks are covered in `tests/test_clues.py` and `tests/test_story_veil.py`. |
| 5 | Inventory of the hand-maintained docx/pptx shows each item carried or dropped | VERIFIED | `content/INVENTORY.md` names all 20 files in `final_documents/` (my loop: 20 of 20 found), each with a disposition (carried→TOML, carried→assets, generated, kept manual, dropped) and a reason. `tests/test_inventory.py` enforces this. `content/assets/` holds both images and `GUIDELINES.md`. |

**Score:** 5/5 truths verified, 0 behavior-unverified.

### Plan must-haves (beyond the roadmap criteria)

| Truth | Status | Evidence |
|-------|--------|----------|
| Config prose rejected by validator (`schema.prose_in_config`) | VERIFIED (narrow) | Present for the four prose keys; see warning W5. |
| Golden change text-only | VERIFIED | 03-01-GOLDEN-DIFF.md records `unexpected: 0` for all tiers; `git diff` touched only the three characterization goldens. I did not re-run the slow digest test; full suite is green. |
| Legacy generators untouched (D-07) | VERIFIED | `generate_*.py` not in the phase diff (`git diff 609e64e..HEAD --name-only`). |
| Story docs veiled, clues still inferable | VERIFIED | No story giveaway hits; clue check passes with 2+ documents per attack. |

### Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `planspiel/texts.py` | VERIFIED | Loader, coverage, digit lint, giveaway, views, clue check, wired into `planspiel/cli.py` (`texts`, `clues`). |
| `content/texte.toml`, `digit_allowlist.toml`, `giveaway_terms.toml`, `clues.toml` | VERIFIED | Present, loaded by `load_content`, exercised by CLI and tests. |
| `content/INVENTORY.md`, `content/assets/` | VERIFIED | See truth 5. |
| `schema.prose_in_config` in `planspiel/validate.py` | VERIFIED | Present; see W5 for coverage limits. |

### Key Link Verification

| From | To | Status |
|------|----|--------|
| `required_keys(cfg)` | typed `Config` ids | WIRED (a new config id fails coverage; orphan and missing probes confirm) |
| `check_texts` | `check_giveaway` | WIRED (`planspiel texts` runs it; 0 Fehler on real content) |
| `clues.toml` quote | `texte.toml` story strings | WIRED (`clues.quote_not_found` check) |
| `_clues_command` | `FacilitatorView.clue_matrix` | WIRED (table printed) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full test suite | `uv run pytest -q` | 873 passed, 19 deselected | PASS |
| Content lints | `uv run planspiel texts` | 0 Fehler, 0 Warnung(en), exit 0 | PASS |
| Clue matrix | `uv run planspiel clues` | 14 rows, 0 Fehler, exit 0 | PASS |
| Config validator | `uv run planspiel validate` | 0 Fehler, 1 Warnung (pre-existing `hand_calc.kz_slope attacks.exfil` 17/7, Phase 6 BAL-02) | PASS |
| Mutations (orphan, missing key, digit, too few clues) | CLI on temp copies | each exits 1 with the expected code | PASS |

Step 7c (probes): no probe scripts declared. Slow digest test (`pytest -m slow tests/test_digest.py`) was started but not awaited; the golden proof rests on the classifier report and the green fast suite.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|-------------|-------------|--------|----------|
| PRINT-02 | 03-01 | SATISFIED | Truths 1, 2, 5. REQUIREMENTS.md marks it Complete. |
| VEIL-01 | 03-02 | SATISFIED | Truth 3. REQUIREMENTS.md marks it Complete. |
| VEIL-03 | 03-03 | SATISFIED | Truth 4 and veiled story. REQUIREMENTS.md marks it Complete. |

All three phase IDs appear in plan frontmatter (`requirements: [PRINT-02]`, `[VEIL-01]`, `[VEIL-03]`) and in REQUIREMENTS.md traceability as Phase 3. No orphaned requirements: VEIL-02 and VEIL-04 are mapped to Phase 5, and PRINT-12 (added in Phase 3 discussion) is mapped to Phase 5. The roadmap marks no other IDs for Phase 3.

### Anti-Patterns Found

No TBD/FIXME/XXX in `planspiel/texts.py`, `cli.py`, `validate.py`, `content/*.toml` or `INVENTORY.md`. No `round(` in `rules.py`/`rounding.py`. No stubs found.

### Review findings considered (03-REVIEW.md, 0 blockers, 6 warnings)

None of the six undermines a success criterion on today's content. They concern guard robustness:

- **W1 (WR-01)**: giveaway normalization misses split words (`Ransom-ware`), NFKC ligatures, `U+2060`, `OT/Störung`. Real content is clean (my scan found no hit). This weakens future edits, not the current state. Recommend fixing before Phase 5 relies on it.
- **W2 (WR-05)**: `sheets.budget.init_when = "Einmal zu Spielbeginn"` contradicts the current Init rule (RULE-02). It sits in a pre-wave sheet served by `PreAttackView`. Recorded and deferred to PRINT-07 by user decision at the 03-01 checkpoint. It is a rules-correctness risk for Phase 5, not a veiling or content-source defect.
- **W3 (WR-03)**: measure and pre-wave sheet texts are guarded against revealed names and bonus reasons only in pytest, not by `planspiel texts`.
- **W4 (WR-04)**: `texts`/`clues` CLI tracebacks on malformed input.
- **W5 (WR-06)**: config prose guard is a four-key denylist; prose could return under other keys.
- **W6 (WR-02)**: story-mechanics lint has no normalization and checks only budget-tier amounts.

Info items worth noting: IN-03 (`content/INVENTORY.md` still says story rows are "un-veiled; veiling in plan 03-03" although they are now veiled), IN-05 (`generate_attack_calculator.py` raises KeyError; accepted under D-07, LEG-01), and the stale `_comment_events` string in `simulation_config.json`.

Observation: M6 measure texts name "Phishing" (a D-13b term) before the wave. This is allowed by D-06 (user decision: only attack names and wave links are banned from pre-wave material, enforced by VEIL-02 in Phase 5). SC3 as written scopes the term check to veiled attack texts, so this does not fail SC3.

### Human Verification Required

None blocking. The wording of revealed texts, story rewrites and the clue matrix was reviewed and approved by the user at the blocking checkpoints of plans 03-02 and 03-03 (D-13d). Whether the clues are actually solvable by players is a playtest question (FLOW-05, Phase 7). The `zeitungsartikel_bild_fabrik.png` padlock image is kept as a deliberate visual clue and falls under the Phase 5 rendered-material scan.

### Gaps Summary

No gaps. The phase goal is met in the codebase: one TOML content source keyed by config id with enforced coverage and digit lint, prose-free config, separate veiled and revealed attack texts behind audience-scoped views, veiled story documents, a checked clue matrix, and a complete inventory. Warnings W1 to W6 are advisory and should be triaged before Phase 5 builds its veiling scan on these lints.

---

_Verified: 2026-10-19_
_Verifier: Claude (gsd-verifier)_
