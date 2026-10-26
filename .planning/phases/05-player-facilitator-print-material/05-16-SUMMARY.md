---
phase: 05-player-facilitator-print-material
plan: 16
subsystem: print
tags: [print-regeneration, manifest, phase-closeout, roadmap-handover, clue-matrix, print-10]

requires:
  - phase: 05-player-facilitator-print-material
    provides: the facilitator master sheet and clues stamp input (05-15), plus every earlier plan that changed an input of the print set
provides:
  - final_documents/generated/ with the 13 Phase 5 PDFs and manifest.json (dirty false), committed in the D-19 order
  - ROADMAP Phase 6 "Carried over from Phase 5" follow-ups
  - the veiling todo closed under .planning/todos/completed/
  - readable German section labels in the facilitator clue matrix
affects: [06-rebalance]

tech-stack:
  added: []
  patterns:
    - "Facilitator-only section labels live in [sheets.spielleitung] as digit-free keys named clue_section_<doc>_<section>, looked up by FacilitatorView after the heading search"

key-files:
  created:
    - final_documents/generated/spieler-massnahmenkarten.pdf
    - final_documents/generated/spieler-eventkarten.pdf
    - final_documents/generated/spieler-teamheft.pdf
    - final_documents/generated/spieler-so-funktioniert-eine-welle.pdf
    - final_documents/generated/spieler-unternehmenssteckbrief.pdf
    - final_documents/generated/spieler-zeitungsartikel.pdf
    - final_documents/generated/spieler-anfrage-mail.pdf
    - final_documents/generated/spieler-audit-mail.pdf
    - final_documents/generated/uebung-welle-0.pdf
    - final_documents/generated/spielleitung-uebersicht.pdf
    - .planning/todos/completed/2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md
  modified:
    - final_documents/generated/manifest.json
    - final_documents/generated/angriff-1_ransomware.pdf
    - final_documents/generated/angriff-2_ot.pdf
    - final_documents/generated/angriff-3_exfil.pdf
    - planspiel/texts.py
    - content/texte.toml
    - tests/fixtures/mini_content/texte.toml
    - tests/test_clues.py
    - .planning/ROADMAP.md

key-decisions:
  - "Section labels for headingless mail sections are two digit-free keys in [sheets.spielleitung] (Lage, Einleitung) instead of a label inside the story texts, so the story texts, the veil scan and the player documents stay untouched"
  - "The raw source key stays as the last fallback of _clue_section; the guard is the new test over the real and the mini content, not a new check_clues error code (YAGNI)"
  - "ROADMAP follow-ups carry MAX_WINDOWS (05-07) next to MAX_PENALTY_ROWS as one bullet, so the five plan bullets stay five"

patterns-established:
  - "The committed print set is written only by the last plan of a phase: inputs committed, clean planspiel print, commit, --check, second build byte-identical"

requirements-completed: [PRINT-10]

duration: 40 min
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 16: Final print regeneration and phase closeout Summary

**The complete Phase 5 print set (13 PDFs plus `manifest.json`, `"dirty": false`, stamp `Stand 2026-10-26 · 3878dab`) is committed from clean inputs in the D-19 order and reproduces byte-identically, the Phase 6 follow-ups are on the roadmap, and the clue matrix on the facilitator booklet no longer prints raw source keys.**

PRINT-10 (05-13 to 05-16) is complete with this plan.

## Pre-step bugfix (Rule 1)

The clue matrix on `spielleitung-uebersicht` printed `story.anfrage_mail.lage.paragraphs` and `story.audit_mail.einleitung.paragraphs` in the "Abschnitt" column, because `_clue_section` falls back to the source key when no `heading` or `headline` exists on the path (reported by 05-15).

- RED `0e35bea`: three tests in `tests/test_clues.py`: no matrix cell of the real content starts with `story.` or `measures.` or contains `.paragraphs` or `.bullets`; the same for the mini content; the two mail sections print `Lage` and `Einleitung`. Result: 2 failed (real content, label), the mini guard already passed.
- GREEN `dfca7d1`: `_clue_section` looks up `sheets.spielleitung.clue_section_<doc>_<section>` after the heading search and before the key fallback; two digit-free keys (`clue_section_anfrage_mail_lage = "Lage"`, `clue_section_audit_mail_einleitung = "Einleitung"`) in `_SPIELLEITUNG_KEYS`, in `content/texte.toml` and in the mini fixture. `uv run planspiel texts` 0 errors; `uv run planspiel clues` 0 errors and no `story.` string left in the table. `tests/golden/answer_keys.json` does not pin the clue matrix (0 matches), so it is unchanged. 283 related tests passed before the full gate.

## Task 1: phase gate, regeneration and commit (`3b2bfb6`)

Phase gate before regeneration (after the bugfix commits):

- `uv run pytest -q`: `2272 passed, 153 deselected` in 117 s (baseline 2269, +3 new tests).
- `uv run pytest -m pdf -q`: `131 passed, 2294 deselected` in 154 s.
- `uv run pytest -m slow tests/test_digest.py -q`: `3 passed, 1 deselected` in 464 s.
- `uv run planspiel validate`: `0 Fehler, 1 Warnung(en)` (the known `hand_calc.kz_slope attacks.exfil: KZ-Steigung 17/7` warning, until Phase 6).
- `uv run planspiel texts`: `0 Fehler, 0 Warnung(en)`.
- `uv run planspiel clues`: `0 Fehler, 0 Warnung(en)`.

D-19 order:

1. `git status --porcelain -- simulation_config.json content print planspiel pyproject.toml uv.lock` printed nothing.
2. `uv run planspiel print` (defaults): `Stand: Stand 2026-10-26 · 3878dab` (no `+lokal`), `13 Dokument(e) gebaut: final_documents\generated`: angriff-1_ransomware, angriff-2_ot, angriff-3_exfil, spieler-anfrage-mail, spieler-audit-mail, spieler-eventkarten, spieler-massnahmenkarten, spieler-so-funktioniert-eine-welle, spieler-teamheft, spieler-unternehmenssteckbrief, spieler-zeitungsartikel, spielleitung-uebersicht, uebung-welle-0.
3. Committed as `docs(05-16): regenerate the complete Phase 5 print set` (14 files: 3 worksheets changed, 10 PDFs new, manifest).
4. `uv run planspiel print --check`: `Druckmaterial aktuell: Stand 2026-10-26 · 3878dab (13 Dokument(e) in final_documents/generated)`, exit 0. A second `uv run planspiel print` left `git status --porcelain final_documents/generated` empty; `--check` exit 0 again.
5. `git ls-files final_documents/generated` lists 14 files; `manifest.json` has `"dirty": false`, the stamp above and an entry for `spielleitung-uebersicht`.

No PDF was locked; nothing was written outside the committed set.

## Task 2: Phase 6 follow-ups and the veiling todo (`c670e48`)

- `.planning/ROADMAP.md`, Phase 6 section only (8 inserted lines): "Carried over from Phase 5" with five bullets: re-choose the reference paths and re-pin `answer_keys.json` (D-18, D-22); rescale the `final_index` weights and drop `vorläufig` (D-23, BAL-03); re-run `practice.check_example` and re-pin `welle0.json` and `worksheet_tex.json` (BAL-05); review `booklet.MAX_PENALTY_ROWS` (12 at X = 9) and `booklet.MAX_WINDOWS` (2, about 2 mm to spare on the tracking page) with new layout proofs; remove the `≈` approximations (BAL-02).
- The veiling todo moved with `git mv` to `.planning/todos/completed/` and got a `## Resolution` section; `pending/` is empty.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Clue matrix printed raw source keys for two mail sections**
- **Found during:** pre-step, reported by 05-15
- **Issue:** `_clue_section` fell back to the dotted source key when a section had no heading.
- **Fix:** digit-free section labels in `[sheets.spielleitung]` and a lookup in `_clue_section` (see above).
- **Files modified:** planspiel/texts.py, content/texte.toml, tests/fixtures/mini_content/texte.toml, tests/test_clues.py
- **Commits:** 0e35bea (RED), dfca7d1 (GREEN)

### Other notes

- The bugfix changed `content/texte.toml` and `planspiel/texts.py`, both print inputs; they were committed before the regeneration, as D-19 requires, so the stamp date is 2026-10-26.
- The plan names five roadmap bullets; `MAX_WINDOWS` (requested for the handover by 05-07) is a second sentence of the `MAX_PENALTY_ROWS` bullet.
- Task 1 and Task 2 commits touch disjoint paths; the todo rename was already staged while the print set was committed, so the print commit used an explicit pathspec (`-- final_documents/generated`).

## Open items

- Human checks of plans 05-05 to 05-15 (including facilitator usability of the booklet and a visual look at the regenerated PDFs) go to the phase UAT (human_verify_mode end-of-phase).
- Phase 6 inherits the follow-ups listed on the ROADMAP.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. T-05-54 (stale or dirty committed PDFs) is mitigated by the clean-tree gate, `"dirty": false`, `--check` exit 0 and the byte-identical second build. T-05-55 (values moving in Phase 6 while pins stay at Phase 5 values) by the explicit roadmap bullets and the golden tests and build guards that fail on moved values.

## Self-Check: PASSED

- Commits `0e35bea`, `dfca7d1`, `3b2bfb6`, `c670e48` are in `git log`.
- `git ls-files final_documents/generated` lists 14 files incl. `manifest.json`; `.planning/todos/completed/2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md` exists with `## Resolution`; `pending/` copy is gone.
