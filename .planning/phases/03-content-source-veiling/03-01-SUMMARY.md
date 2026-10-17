---
phase: 03-content-source-veiling
plan: 01
subsystem: content-source
tags: [toml, tomllib, content-lint, digit-lint, golden-baseline, inventory]

requires:
  - phase: 02-rule-changes
    provides: typed config, rules kernel, characterization goldens and digests
provides:
  - content/texte.toml as the single source of all German print prose, keyed by config id
  - planspiel/texts.py loader, coverage check, digit lint and story mechanics lint; CLI `planspiel texts`
  - reviewed digit allowlist (content/digit_allowlist.toml, seven entries)
  - prose-free simulation_config.json and validator error schema.prose_in_config
  - content/INVENTORY.md (SC5) and git-tracked content/assets/ (images and GUIDELINES.md)
  - text-only golden rewrite with classifier proof
affects: [03-02 veiling, 03-03 story veiling, 04 sheets, 05 cards and PDFs, 07 LEG-01]

tech-stack:
  added: []
  patterns:
    - "Prose lives in TOML keyed by config id; required keys are derived from the typed config, never hard-coded per attack"
    - "Digit lint with per-key exact-token allowlist; stale entries fail"
    - "Golden rewrite only through a classifier (allowed path patterns, unexpected: 0) plus a blocking user decision"

key-files:
  created:
    - planspiel/texts.py
    - content/texte.toml
    - content/digit_allowlist.toml
    - content/INVENTORY.md
    - content/assets/README.md
    - content/assets/GUIDELINES.md
    - content/assets/images/zeitungsartikel_bild_audit.png
    - content/assets/images/zeitungsartikel_bild_fabrik.png
    - tests/fixtures/mini_content/texte.toml
    - tests/fixtures/mini_content/digit_allowlist.toml
    - tests/test_texts_loader.py
    - tests/test_texts_coverage.py
    - tests/test_texts_digits.py
    - tests/test_texts_migration.py
    - tests/test_inventory.py
    - tests/test_config_prose_removed.py
    - .planning/phases/03-content-source-veiling/tools/golden_text_diff.py
    - .planning/phases/03-content-source-veiling/03-01-GOLDEN-DIFF.md
  modified:
    - planspiel/cli.py
    - planspiel/config.py
    - planspiel/rules.py
    - planspiel/validate.py
    - simulation_config.json
    - tests/fixtures/mini_config.json
    - tests/golden/characterization_low.json
    - tests/golden/characterization_medium.json
    - tests/golden/characterization_high.json
    - tests/test_config_text.py
    - tests/test_validate.py
    - .gitattributes
    - .planning/PROJECT.md

key-decisions:
  - "Prose lives in content/texte.toml; config holds numbers, ids and short labels; prose in config is a validator error (D-01/D-02/A3)"
  - "Sparprogramm simulation label is generated from params (Gesamtbudget -20k€), not read from config (D-03/D-24/A4)"
  - "Digit allowlist pinned at seven reviewed entries (30 Tage x2, 24/7, 14 Tage, 3-2-1, <4h, 30 Min); a new entry needs a conscious test edit (D-10/D-25)"
  - "levels_simple carried without level prefix; M6 L3 and M10 L1 deck copy-paste errors dropped (D-28)"
  - "sheets.budget.init_when 'Einmal zu Spielbeginn' carried verbatim although outdated since RULE-02; fix proposed for PRINT-07"
  - "ASCII closing quotes in the newspaper text carried as found"

patterns-established:
  - "texts.* Issue codes reuse planspiel.validate.Issue and the `ERROR code path: message` CLI format"
  - "TOML read in binary mode (tomllib), content/*.toml pinned to LF via .gitattributes"

requirements-completed: [PRINT-02]

coverage:
  - id: D1
    description: "All print prose in content/texte.toml keyed by config id; `planspiel texts` fails on missing and orphaned keys"
    requirement: PRINT-02
    verification:
      - kind: unit
        ref: "tests/test_texts_coverage.py, tests/test_texts_migration.py"
        status: pass
      - kind: other
        ref: "uv run planspiel texts -> 0 Fehler, 0 Warnung(en)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Digit lint with reviewed allowlist and story mechanics lint"
    requirement: PRINT-02
    verification:
      - kind: unit
        ref: "tests/test_texts_digits.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "Config without prose; schema.prose_in_config rejects its return"
    requirement: PRINT-02
    verification:
      - kind: unit
        ref: "tests/test_config_prose_removed.py, tests/test_validate.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "Golden change is text-only (classifier unexpected 0, slow digests unchanged)"
    requirement: PRINT-02
    verification:
      - kind: other
        ref: "uv run python .planning/phases/03-content-source-veiling/tools/golden_text_diff.py -> differences: 0 on all tiers"
        status: pass
      - kind: integration
        ref: "uv run pytest -m slow tests/test_digest.py -q -> 3 passed"
        status: pass
    human_judgment: true
    rationale: "Golden rewrite, allowlist and migration choices needed explicit human approval (D-08, D-25); given at the Task 6 checkpoint"
  - id: D5
    description: "Inventory of all 20 final_documents/ files and the assets folder"
    requirement: PRINT-02
    verification:
      - kind: unit
        ref: "tests/test_inventory.py"
        status: pass
    human_judgment: true
    rationale: "Dispositions (carried, generated, kept manual, dropped) are design decisions reviewed by the user at Task 6"

duration: multi-session (planned 2026-10-10, completed 2026-10-17)
completed: 2026-10-17
status: complete
---

# Phase 3 Plan 1: Content Source (PRINT-02) Summary

**All German print prose now lives once in `content/texte.toml` keyed by config id, guarded by `planspiel texts` (coverage plus strict digit lint with a reviewed allowlist), and `simulation_config.json` carries no prose; the golden rewrite was proven text-only.**

## Performance

- **Tasks:** 6 of 6 (5 auto TDD tasks, 1 checkpoint:decision)
- **Final test state:** `uv run pytest -q` 669 passed (19 slow deselected); slow digest check 3 passed
- **Files:** 18 created, 13 modified (see frontmatter)

## Commits

| Task | RED | GREEN / result |
|------|-----|----------------|
| 1 Loader, coverage, digit lint, `planspiel texts` | 9881a3b `test(03-01): add failing tests for the content source loader and lints` | b608a54 `feat(03-01): add planspiel.texts loader, coverage and digit lint with planspiel texts` |
| 2 Migrate prose into content/texte.toml | 4328d1c `test(03-01): add failing migration fidelity tests for content/texte.toml` | 104eae1 `feat(03-01): migrate measure, attack, event, sheet and story prose into content/texte.toml` |
| 3 Assets folder and inventory | d9cbf35 `test(03-01): add failing inventory and assets tests` | b917395 `feat(03-01): add content/assets and the inventory of hand-maintained documents` |
| 4 Strip prose from config | af0b12a `test(03-01): add failing tests for a prose-free config` | e36f24d (GREEN, held back until the Task 6 approval, see below) |
| 5 Golden classifier and report | n/a | 0f9890a `chore(03-01): add the text-only golden classifier and its report` |
| 6 Approved golden rewrite | n/a | e36f24d `feat(03-01): move prose out of simulation_config.json (text-only golden change)`, 805e6ff `docs(03-01): log the content-source decision` |

Each RED commit contains only new or extended test files (test modules and fixtures listed in the commit stats) and was run red before its GREEN commit. The per-test failure listings were captured in the first execution run, not re-captured in this continuation. Between Task 4 and Task 6 the suite was in the planned red window: exactly `tests/test_characterization.py::test_golden_sample_matches[low|medium|high]` failed (3 failed, 666 passed), nothing else.

## Task 6 decision

The user selected: **approve** ("Approve", as presented): text-only golden change, the seven-entry digit allowlist, the generated label `Gesamtbudget -20k€`, all migration choices and inventory dispositions exactly as reported, including keeping `sheets.budget.init_when` "Einmal zu Spielbeginn" verbatim with the proposal to fix it in PRINT-07, and the ASCII closing quotes in the newspaper text carried as found.

Only after this selection were goldens rewritten (`uv run pytest --update-golden -q`).

## Verification (after the final code commit)

- `uv run python .planning/phases/03-content-source-veiling/tools/golden_text_diff.py`: `differences: 0` and `unexpected: 0` for low, medium and high (pre-rewrite counts in 03-01-GOLDEN-DIFF.md: wave_name 177/174/180, bonus_descriptions 220/217/225, sparprogramm_label 59/58/60, unexpected 0)
- `git diff --stat tests/golden`: exactly the three characterization files
- `uv run pytest -q`: 669 passed, 19 deselected
- `uv run pytest -m slow tests/test_digest.py -q`: 3 passed (digests unchanged)
- `uv run planspiel validate`: `0 Fehler, 1 Warnung(en)` (the existing hand_calc.kz_slope exfil warning)
- `uv run planspiel texts`: `0 Fehler, 0 Warnung(en)`

## Deviations from Plan

None in scope or behaviour. Execution notes:

1. **CRLF / autocrlf handling.** `core.autocrlf=true` and several tracked files are CRLF (for example `.planning/PROJECT.md`). TOML sources are pinned to LF via `.gitattributes` (`content/*.toml text eol=lf`) and read in binary mode with `tomllib`; a loader test covers a CRLF TOML file. Edits to CRLF files used the Edit tool so line endings were preserved.
2. **Mini fixture choice.** Tests run on a hand-verifiable `tests/fixtures/mini_content/` set (own allowlist with one entry, four story docs, a world-fact digit in story) rather than the real content, so lint behaviour does not depend on migrated wording. Retargeted vocabulary tests also run on the mini content.
3. **Throwaway builder scripts not committed.** The `measures.*` block of texte.toml was generated with a scratchpad script (AST-parse of MEASURE_META in `generate_pptx_cards.py` / `generate_from_template.py`, TOML emitted), never retyped. The script stays in the session scratchpad and is not part of the repo.
4. **Task 4 GREEN held uncommitted by design** until the Task 6 approval, so the pinned goldens were never rewritten without review (T-03-01).
5. **Classifier report status line** in 03-01-GOLDEN-DIFF.md updated from "awaiting decision" to "approved" after the rewrite.

### Auto-fixed Issues

None.

## Known Issues for Phase 7 (LEG-01, accepted under D-07)

The legacy generators and their embedded copies are untouched by decision D-07, so removing prose from the config degrades them further:

- `generate_attack_calculator.py` raises `KeyError`: `wave_data['name']` (line 45), `bm['description']` (line 83), `wave['name']` (line 464). It was already broken on `kz_bonus` since plan 02-01.
- `generate_pptx_cards.py` still runs but prints blank event descriptions.

`tests/test_legacy_generators_smoke.py` was adjusted to the new config shape in e36f24d.

## Known Stubs

None. Story texts in `content/texte.toml` are carried verbatim and un-veiled (attack-revealing words remain until plan 03-03, VEIL-03); they are never rendered in this phase (threat T-03-04, accepted).

## Flags carried forward

- `sheets.budget.init_when` ("Einmal zu Spielbeginn") is outdated since RULE-02 (Init is also due when adding or raising a level in a change window); fix the wording in PRINT-07.
- Digit allowlist review flag: "14 Tage", "30 Tage", "<4h", "30 Min" look like parameters but none is in config; the alternative (number words) would break the 1:1 carry of D-05. Accepted.
- Two PNGs (about 3.7 MB) are duplicated in `content/assets/images/` and `final_documents/` until LEG-01.

## Threat Flags

None beyond the plan's threat model.

## Self-Check: PASSED

- Files present: planspiel/texts.py, content/texte.toml, content/digit_allowlist.toml, content/INVENTORY.md, content/assets/README.md, content/assets/GUIDELINES.md, both PNGs, tests/test_texts_*.py, tests/test_inventory.py, tests/test_config_prose_removed.py, tools/golden_text_diff.py, 03-01-GOLDEN-DIFF.md
- Commits present: 9881a3b, b608a54, 4328d1c, 104eae1, d9cbf35, b917395, af0b12a, 0f9890a, e36f24d, 805e6ff
