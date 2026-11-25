---
phase: quick-261125-ail
plan: 261125-ail
subsystem: print-booklet, print-texts, master-sheet
tags: [proofreading, teamheft, uebung, spielleitungsheft, rc7]
requires: [quick-261125-0f4 RC6]
provides:
  - "all 54 findings of proofreading pass 2 applied at their source (texte.toml, clues quotes untouched, templates, print models)"
  - "print release candidate 7: stamp Stand 2026-11-25 · 4fe9685, commit d372291; the user reprints the complete set"
affects: [07-12 dry run materials]
tech-stack:
  added: []
  patterns: ["a computed table row shades its label cell only; consecutive shaded rows get their own boxes (colortbl overpaints rules)", "contents with aux-stable \\pageref labels"]
key-files:
  modified:
    - content/texte.toml
    - content/digit_allowlist.toml
    - README.md
    - planspiel/texts.py
    - planspiel/printmodel.py
    - planspiel/practice.py
    - planspiel/booklet.py
    - planspiel/master.py
    - planspiel/eventtext.py
    - planspiel/was_neu.py
    - print/planspiel.sty
    - print/templates/angriff_blatt.tex.j2
    - print/templates/uebung.tex.j2
    - print/templates/master.tex.j2
    - print/templates/teamheft_planung.tex.j2
    - print/templates/teamheft_ros.tex.j2
    - print/templates/teamheft_tracking.tex.j2
    - tests/golden/answer_keys.json
    - tests/golden/welle0.json
    - tests/golden/worksheet_tex.json
    - final_documents/generated/*.pdf
    - final_documents/generated/manifest.json
  created:
    - tests/test_proofreading_two.py
decisions:
  - "No game value changed: simulation_config.json, rules.py, uv.lock, pyproject.toml untouched; planspiel gate unchanged (X = 3)"
  - "Findings are verified against the code before they are applied (slope sign, window_cost, wave order, printed paragraph positions)"
metrics:
  completed: 2026-11-25
status: complete
---

# Quick 261125-ail: Proofreading pass 2 applied, print RC7

RC7 on top of RC6: the 54 findings of `261125-0f4-PROOFREAD-2.md` are applied (13 play-breakers, 8 pass-1 fixes, 10 terminology leftovers, 19 language points, 4 layout points). Page counts of all 15 PDFs are unchanged against RC6; every PDF differs in content, so the complete set is reprinted.

## Commits

1. `76b25b7` test: pin the behaviour changes of proofreading pass 2 (RED)
2. `11ca309` docs: apply the wording findings (texts, allowlist, README, mini fixture, pinning tests)
3. `29ad802` feat: behaviour changes (GREEN)
4. `a66a909` fix: register example without asset in the narrow column, Was-ist-neu worst case on one page, pdf tests follow the new master order
5. `abe2754` test: find the debrief span by the clue matrix intro
6. `d372291` docs: regenerate the complete print set (release candidate 7)

## Gates

- `uv run planspiel validate`, `texts`, `clues`: 0 Fehler, 0 Warnung(en) each
- `uv run planspiel gate`: bestanden (X = 3 unchanged)
- `uv run pytest -q`: 3107 passed, 3 skipped, 213 deselected
- `uv run pytest -m pdf -q`: 165 passed (run on the final committed state)
- `uv run planspiel print`: 15 documents, manifest `dirty: false`, stamp `Stand 2026-11-25 · 4fe9685`; `uv run planspiel print --check` exit 0 on the committed state

## Findings: applied, adapted, skipped

All 54 are applied; none is skipped. These were adapted after checking them against the code, the config or the printed documents:

- **Clue-matrix section names (A):** the report named "zweiter Absatz" (Anfrage-Mail) and "erster Absatz" (Audit-Mail). The printed mails show the clue quotes in the third paragraph of the Anfrage-Mail and the second paragraph of the Audit-Mail; the names are "dritter Absatz" and "zweiter Absatz" ("Schlagzeilenleiste" as suggested).
- **Sparprogramm (D):** "in der letzten Welle" became "in der nächsten Welle": the window after wave 2 is followed by exactly one wave in this config, and "nächste Welle" stays correct if the wave order changes.
- **KZ-Steigung (D):** verified against `rules.attack_kz_delta` (slope positive, `KZ = -8 + (GR - 22) × 2`); the row prints "+2". A non-terminating slope would keep the fraction form.
- **Δ Init (A):** verified against `rules.window_cost` (per measure, Init of the new level minus the old one, never negative; full Init for a new measure); defined on the tracking page, the Welle page and the card legend.
- **Level 0 (B):** the tracking window text says "Level 0" (allowlist entry for that one digit string, the wording-piece digit test strips it).
- **Digits in the Spielleitung how-to (D):** the suggested "Fall 1 und Fall 2" would need digit allowlist entries; the text says "im ersten und im zweiten Fall, im dritten Fall".
- **RoS precision in Was ist neu (B):** "auf zwei Nachkommastellen gerundet" needs an entry in the number-word lint (`ALLOWED`, reason: rounding precision, not a config count).
- **Register risk example (E):** the example row shows a dash in the narrow Wert column ("Patientenakten" overflowed it); the need-table example row shows the asset without a W label.
- **Übung euro format (E):** the euro sign follows the short box in the line text instead of sitting inside the 13 mm box; space added above the Recovery line.
- **Übung event order (A):** a note in the KZ Events hint says where the event stands ("das Event dieser Übung steht auf der letzten Seite") instead of moving the box.
- **Exfiltration no-Recovery step (A):** generic text from `allow_recovery` naming the damage step ("Bei diesem Angriff gibt es keine Recovery. Der Schaden aus Schritt 5 bleibt unverändert."), not a sentence about data.
- **Teamheft value cells (E):** the computed rows shade only the label cell and keep a plain value cell; Vermiedener Schaden, RoS and Restbudget stand in their own boxes because colortbl paints over the rule between two consecutive shaded rows.
- **Rounding hint (B):** "gerundet: [Feld]" with the note "Bei ,5 rundet ihr weg von der Null, also zum größeren Betrag." on its own line; the rounded box stays with its label.
- **Page fit (layout):** the tracking sheet needed a tighter change-window grid (7.4 mm rows, `\rowstrutwin`) and "KZ final = KZ nach Welle 3 + ..." (wave number from the config) to stay one page; the Welle page and the Was-ist-neu worst case lost one line each (shorter `window_rules`, `ros_note`, overspend row).
- **Spielleitungsheft contents (E):** page numbers via `\label`/`\pageref` (aux-stable build); the Übung key now sits before Angriff 1.
- **RoS sign (D):** the final table prints "+0,06"; the golden `answer_keys.json` changed from "0,06" to "+0,06" (wording golden).
- **Audit-findings cheat-sheet case (D):** reworded towards confidentiality as the report offered.

## Deviations from Plan

None beyond the adaptations above. The pdf and fill gates found four problems after the first inputs commit (register overfull, Was-ist-neu worst case, two pdf tests that assumed the old master order and a title that now also appears in instructions); all were fixed in commit a66a909 and abe2754 before the final build.

## Known Stubs

None.

## Threat Flags

None. The veil guard tests pass unchanged: no player document names an attack before its wave, and no player document except the event deck prints Budget Review tiers.

## Self-Check: PASSED

Commits 76b25b7, 11ca309, 29ad802, a66a909, abe2754 and d372291 exist; `print --check` exit 0; 15 documents in `final_documents/generated`.
