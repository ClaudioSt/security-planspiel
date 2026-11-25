---
phase: quick-261125-djw
plan: 261125-djw
subsystem: print-booklet, print-texts, master-sheet, attack-sheets
tags: [playthrough-review, teamheft, spielleitungsheft, veil, rc8]
requires: [quick-261125-ail RC7]
provides:
  - "all 22 findings of the third review (play-through of RC7) applied at their source, none skipped"
  - "print release candidate 8: stamp Stand 2026-11-25 · 018111b, commit 56d69e5; the user reprints the complete set single-sided"
affects: [07-12 dry run materials]
tech-stack:
  added: []
  patterns: ["event rows of the tracking sheet are open in every wave so the grey pattern cannot reveal an event", "an attack without Recovery has one damage row in sheet and key"]
key-files:
  modified:
    - content/texte.toml
    - content/digit_allowlist.toml
    - planspiel/booklet.py
    - planspiel/printmodel.py
    - planspiel/master.py
    - planspiel/was_neu.py
    - planspiel/debrief.py
    - planspiel/texts.py
    - print/planspiel.sty
    - print/templates/angriff_blatt.tex.j2
    - print/templates/teamheft_planung.tex.j2
    - tests/golden/answer_keys.json
    - tests/golden/welle0.json
    - tests/golden/worksheet_tex.json
    - final_documents/generated/*.pdf
    - final_documents/generated/manifest.json
  created:
    - tests/test_playthrough_rc8.py
decisions:
  - "V1 (user decision, Alle Felder offen): Event: Budget and Event: OPEX are open in every wave column; a hint says to leave the cell empty or enter null"
  - "V2: the 620.000 EUR explanation on the RoS page is kept (names neither an attack nor a single value)"
  - "No game value changed: simulation_config.json, rules.py, uv.lock, pyproject.toml untouched; planspiel gate unchanged"
metrics:
  completed: 2026-11-25
status: complete
---

# Quick 261125-djw: Play-through review applied, print RC8

RC8 on top of RC7: the 22 findings of `261125-ail-REVIEW-3.md` (a play-through along the Low reference path, no wrong number, no veil breach) are applied, 4 dry-run blockers first. Page counts of all 15 PDFs are unchanged against RC7; every PDF differs in content, so the complete set is reprinted, single-sided.

## Commits

1. `f9945a4` test: pin the open event rows of the tracking sheet (RED), with the REVIEW-3 report
2. `5e22b95` feat: open event rows and the four dry-run instructions (D-2, D-3)
3. `db7acc8` test: pin the play-through code changes (RED)
4. `cd67bc6` feat: play-through code changes (GREEN): C1, B2, E1, E2, C4, D2, D3
5. `f735f31` docs: wording findings A6, A7, A8, B1, C2, C3, D1 and the page-fit changes
6. `42d740f` docs: first RC8 build (stamp 443fbb1, superseded)
7. `d821deb` fix: Was-ist-neu schedule line shortened so the capped worst case fits one page
8. `56d69e5` docs: regenerate the complete print set (release candidate 8), stamp `Stand 2026-11-25 · 018111b`

## Gates

- `uv run planspiel validate`, `texts`, `clues`: 0 Fehler, 0 Warnung(en) each
- `uv run planspiel gate`: bestanden (X = 3 unchanged)
- `uv run pytest -q`: 3125 passed, 3 skipped, 213 deselected (final committed state)
- `uv run pytest -m pdf -q`: 165 passed (final committed state)
- `uv run planspiel print`: 15 documents, manifest `dirty: false`, stamp `Stand 2026-11-25 · 018111b`; `uv run planspiel print --check` exit 0 on the committed state

## Findings: applied, adapted, skipped

All 22 applied; none skipped.

**Blocking four (D-2):** A5 print list "Druckt alles einseitig."; A3 Start column in the Tracking-Bogen intro and the Maßnahmen-und-Budget direction (KZ-Start, Init-Kosten, Restbudget = Tier-Budget minus Init-Kosten); A4 "tragt ±0 ein" on the attack sheets (digit allowlist entry for the token `±0`, pinned in `test_texts_migration.py`); A1 Teamheft page 5 sends the teams back to the Tracking-Bogen; A2 the Abschluss direction keeps the Teamheft with the teams, names KZ final and has the facilitator note KZ final and RoS in the comparison table.

**V1 (user decision) and V2:** event rows open in every wave (model, rendered TeX and the pdf fill report all pass); hint "Ohne Event dieser Art bleibt das Feld leer oder ihr tragt null ein." V2 kept as decided.

**Adapted after checking against the code and the page budget:**

- **A6:** instead of greying the Budget Review Restbudget cell, the Restbudget hint ends with "Spalte Budget Review: das Restbudget von der Seite Budget Review." (new key `sheets.tracking.review_remaining_hint`, also in the mini fixture). The cell has to stay open because the value is carried from page 5.
- **A8:** "Die Stufe tragt ihr nicht ein, sie steht oben in der Schutzbedarfstabelle (Zeile des Werts, Spalte des Hauptziels)." The suggested longer wording pushed Teamheft page 1 onto a second page.
- **C3:** wave-key labels are the Tracking-Bogen labels ("Event: Budget", "Event: OPEX", "Restbudget (laufend)"); the "(Plus: Kosten)" note is dropped, the sign rule stays in the tracking hint.
- **C4:** a wave without Recovery has the rows "Schaden" (key `damage_after`) only; the rows "Schaden vor Recovery" and "Recovery-Faktor r" are dropped from the key. Pinning tests and the golden `answer_keys.json` follow.
- **B2:** the first box of the Recovery line is the long box, the line keeps its last five parts together (breaks before the first box) and sits 3 mm below the table.
- **E1:** the hint is its own line ("Tragt die R-Nummer ein oder „nicht im Register“; ..."), the box is the long box; new model field `reality_hint`.
- **E2:** the planning Summe row shades only its label and closes the Level and "gegen R#" cells.
- **D2:** "Siehe die Hinweis-Matrix für die Story-Gruppenarbeit am Ende dieses Hefts." (the matrix really is the end of the booklet, pages 14 to 16); new key `clue_pointer_end`.
- **D3:** built from the schedule in wave order: "(215 Min. gesamt; Welle 1: 25, Welle 2: 20, Welle 3: 20 Min.)". The first version with "Min." per wave wrapped and broke the capped worst-case page (caught by `pytest -m pdf`), so the unit is stated once. The unused text key `parts.per_wave` of Was ist neu is removed.
- **E3:** checked at 220 and 500 dpi: every rule around the OPEX cell of Welle 3 and its grey neighbours is intact. The gap in the 110 dpi view of RC7 was a rendering artifact; no change.
- **Page fit:** the added instructions cost lines on Teamheft page 3, so the change-window rows of the tracking sheet are 6.6 mm (was 7.4 mm, `\rowstrutwin`), the Start sentence in the intro is compact and the window footer is one line. Teamheft stays at 5 pages.
- **B1, C1, C2, D1, A7:** applied as suggested (C1 also fixes the Übung sheet, same template).

## Deviations from Plan

None beyond the adaptations above. The pdf gate found one problem after the first print (Was-ist-neu worst case, fixed in `d821deb`, reprinted).

## Known Stubs

None.

## Threat Flags

None. The veil guard tests pass unchanged; V1 removes a (weak) leak of event timing from the Teamheft.

## Self-Check: PASSED

Commits f9945a4, 5e22b95, db7acc8, cd67bc6, f735f31, 42d740f, d821deb and 56d69e5 exist; `print --check` exit 0; 15 documents in `final_documents/generated`.
