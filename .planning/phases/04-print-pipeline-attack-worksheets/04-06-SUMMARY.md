---
phase: 04-print-pipeline-attack-worksheets
plan: 06
subsystem: print-attack-worksheets
tags: [latex, jinja, worksheets, a4, print-pipeline, tdd, d-19]

requires:
  - phase: 04-print-pipeline-attack-worksheets
    provides: AttackSheet model (04-02), render stage and CLI (04-03), equivalence replay (04-04), stamp, manifest and --check (04-05)
provides:
  - print/templates/angriff.tex.j2, a thin template that loops over and inserts model strings only
  - worksheet macros in print/planspiel.sty (step bar, fill-in boxes, tick box, level badge, hint, reference line, row struts, page fill report)
  - render.attack_worksheets registered in DOCUMENT_BUILDERS, so `planspiel print` builds the three Angriff worksheets
  - ERROR print.model for PrintModelError in `print` and `print --check`
  - final_documents/generated/angriff-1_ransomware.pdf, angriff-2_ot.pdf, angriff-3_exfil.pdf and manifest.json, committed in the D-19 order
affects: [Phase 5 documents reuse the planspiel.sty macros, Phase 7 legacy retirement (LEG-01, LEG-02)]

tech-stack:
  added: []
  patterns:
    - "Fill-in lines are a Jinja macro called as a statement (call ... endcall), because finalize would escape the macro's TeX if it were called inside a variable tag; the macro mentions `caller` so Jinja accepts the call block"
    - "Every PDF page is measured: \\fillreport writes PLANSPIEL-FILL page=n used=... text=... to the log and a pdf test asserts used <= text for both pages"
    - "Fixed-height rows come from a 7 mm strut; gray small text in table cells uses \\textcolor{..}{\\footnotesize ..} because {\\footnotesize\\color{..}..} added 1.5 mm per row"

key-files:
  created:
    - print/templates/angriff.tex.j2
    - tests/test_print_render.py
    - tests/test_print_worksheets_pdf.py
    - final_documents/generated/angriff-1_ransomware.pdf
    - final_documents/generated/angriff-2_ot.pdf
    - final_documents/generated/angriff-3_exfil.pdf
    - final_documents/generated/manifest.json
  modified:
    - print/planspiel.sty
    - planspiel/render.py
    - planspiel/cli.py
    - tests/test_print_cli.py
    - tests/test_print_preflight.py

key-decisions:
  - "Layout: page 1 holds Schritt 1 to 4, page 2 starts with the Fall step (the planned D-05 split); only fallback (a) from the plan was needed, no (b), (c) or (d)"
  - "The result line (Ergebnis dieses Angriffs) sits at the end of page 2, after the wave-KZ step, instead of inside the Fall step: it names 'Schaden nach Recovery', which exists only after the recovery step"
  - "Hyphenation is switched off in planspiel.sty so a digit-bearing fragment can never be split by a hyphen in the PDF text check"
  - "The drift test for loaded packages ignores the local `planspiel` style, which every template loads"

patterns-established:
  - "Rendered .tex is checked fragment by fragment (tex_escape of each printed fragment must occur in the source) and the PDF text is checked with whitespace-free composite fragments"

requirements-completed: [PRINT-03]

duration: 75min
completed: 2026-10-22
status: complete
---

# Phase 4 Plan 06: Attack Worksheets Summary

**`uv run planspiel print` now builds the three Angriff worksheets as two-page A4 sheets from config and texts, with threshold, cap and Obergrenze, the Fall 1/2/3 formulas and the recovery step printed from the model, and the stamped PDFs plus manifest are committed from a clean tree (Stand 2026-10-22 · 202d6c8).**

## Accomplishments

- A thin Jinja template (`angriff.tex.j2`) renders each `AttackSheet` in MHP order: title and narrative, Schritt 1 (CIA table with the base row, 10 blank 7 mm rows and a sum row), Schritt 2 (E-Wert), Schritt 3 (bonus table with level badges and a tick box), Schritt 4 (Gesamtreduktion), a page break, Schritt 5 (cap line, Fall 1, Fall 2, Fall 3 with fill-in lines), Schritt 6 (recovery, waves 1 and 2 only), the wave-KZ step and the result line.
- No template edit is needed when numbers change: the SC2 tests copy the config, raise wave 1's `e_threshold` (and separately the attack's `mitigation_cap` with `base_severity`), and assert that "Schwelle", "Kappung", "Obergrenze", "≤ t" and "(U − GR" change on the rendered sheet.
- `PrintModelError` now ends `planspiel print` (exit 1) and `planspiel print --check` (exit 2) with `ERROR print.model <message>`.
- The first stamped build is committed: `final_documents/generated/` holds exactly the three PDFs and `manifest.json` (`"dirty": false`, stamp without "+lokal"); `planspiel print --check` exits 0 and a rebuild leaves `git status --porcelain final_documents/generated` empty.

## Task Commits

1. Task 1 RED: `9ff1cde` test(04-06): add failing attack worksheet render tests
2. Task 1 GREEN: `7a81ed8` feat(04-06): add the attack worksheet template
3. Task 2 RED: `bda2615` test(04-06): add worksheet pdf layout and fragment tests
4. Task 2 GREEN: `aa6587a` feat(04-06): lay out the attack worksheets on two A4 pages
5. Task 3: `3717276` docs(04-06): add the generated attack worksheets

### RED runs (quoted)

Task 1 (`uv run pytest tests/test_print_render.py tests/test_print_cli.py -q`): `20 failed, 11 passed` (every render test failed because `DOCUMENT_BUILDERS` was empty, the template did not exist, and `ERROR print.model` was not printed; the 11 passes were the existing CLI tests).

Task 2 (`uv run pytest -m pdf tests/test_print_worksheets_pdf.py -q`, with the template of Task 1 plus two TeX fixes): `3 failed, 3 passed`.
- `test_each_worksheet_has_exactly_two_pages`: `assert 3 == 2` for `angriff-1_ransomware` (page 1 overflowed by about 27 mm).
- `test_steps_stay_whole_on_their_page`: `ValueError: too many values to unpack (expected 2)` (three pages).
- `test_both_pages_fit_the_text_height_as_measured_in_the_log`: `[] == ['1', '2']` (no PLANSPIEL-FILL lines yet).
- Passing from the start: fragments in the PDF text, no "Missing character", no "Overfull \hbox".

## Page fill (measured, final build)

Text height 257.0 mm (731.24 pt). Values are the `PLANSPIEL-FILL` lines of the committed build; "estimate" is the objective's planning number.

| Sheet | Page 1 used | Page 1 estimate | Page 2 used | Page 2 estimate |
|-------|-------------|-----------------|-------------|-----------------|
| angriff-1_ransomware (recovery) | 252.5 mm | about 244 mm | 199.9 mm | about 186 mm |
| angriff-2_ot (recovery, 2 bonus rows) | 238.2 mm | about 244 mm | 199.9 mm | about 186 mm |
| angriff-3_exfil (no recovery, 3 bonus rows) | 253.5 mm | about 244 mm | 143.4 mm | about 130 mm |

Page 1 of waves 1 and 3 keeps a reserve of 4.5 and 3.5 mm. The first build (before tuning) measured 283.3, 268.9 and 284.2 mm on page 1 and 220.1, 220.1 and 150.6 mm on page 2.

Fallback steps: only (a), tightening vertical spacing, was needed, plus one correction that is not on the plan's list: the CIA level-hint cell cost 1.5 mm per row. The measured row pitch is 7.0 mm (handwriting rows are 7 mm, header rows 5 mm). Steps taken: step bar spacing 2 mm before and 1 mm after reduced to 1.2 mm and 0.5 mm, `\parskip` 1.2 mm to 0.8 mm, header rows 6 mm to 5 mm, the hint cell written as `\textcolor{mhpgrey}{\footnotesize ...}`. Fallbacks (b), (c) and (d) were not used; the page break stays before the Fall step.

## Visual check

PNG renders (80 dpi, gitignored) are in `C:/Users/Claudio/Documents/Git/security_game/security-planspiel/build/preview/`; I looked at them after the final layout.
- `angriff-1_ransomware-1.png`: blue step bars, a 10-row CIA table with the base row and the sum row shaded, the E-Wert line with three short boxes and one long box, the bonus table with level-2 badges and tick boxes, the Gesamtreduktion line at the bottom of the page.
- `angriff-1_ransomware-2.png`: the cap line "Schwelle: 23 · Kappung: 8 · Obergrenze: 23 + 8 = 31" on a light bar, Fall 1 to 3 with the two Fall-3 fill-in lines, the recovery table with level badges 1/2/3, the wave-KZ line and the result line, about 50 mm free at the bottom.
- `angriff-2_ot-1.png` and `angriff-2_ot-2.png`: the same structure with two bonus rows and the OT numbers (20, 10, 30; 1,2 slope).
- `angriff-3_exfil-1.png`: three bonus rows and the tightest page 1.
- `angriff-3_exfil-2.png`: no recovery step, the Fall-3 KZ hint about multiplying first and dividing by 7 afterwards, and the wave-KZ step.

Known cosmetic point: the wave-KZ line wraps between "(ab" and ",5 vom Betrag aufrunden)", and in the result line the last short box moves to a second line on waves with recovery; the strings come from the model (plan 04-02) and are not changed here.

## Phase gate

- `uv run pytest -q`: 1135 passed, 42 deselected.
- `uv run pytest -m pdf -q`: 20 passed (14 earlier ones plus the 6 worksheet tests: smoke gate, CLI byte-identity now covering the three worksheet PDFs, stamp on every page, worksheet layout); none skipped.
- `uv run pytest -m slow tests/test_worksheet_equivalence_full.py -q`: 3 passed in 251 s (re-run, because build inputs changed since 04-04).
- `uv run planspiel validate`: 0 errors, 1 warning (the expected `hand_calc.kz_slope` 17/7 of wave 3 until Phase 6, BAL-02); `uv run planspiel texts`: 0 errors, 0 warnings.
- `uv run planspiel print --check`: "Druckmaterial aktuell: Stand 2026-10-22 · 202d6c8 (3 Dokument(e) in final_documents/generated)", exit 0.
- A second `uv run planspiel print` leaves `git status --porcelain final_documents/generated` empty.
- The extracted text of each committed PDF contains the stamp on both pages and no "lokal".

Committed PDFs: `C:/Users/Claudio/Documents/Git/security_game/security-planspiel/final_documents/generated/angriff-1_ransomware.pdf`, `angriff-2_ot.pdf`, `angriff-3_exfil.pdf`, plus `manifest.json` in the same folder.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Template syntax and TeX fixes found while building**
- **Found during:** Task 1 and Task 2
- **Issue:** (a) A Jinja macro called with `call` must mention `caller`, otherwise Jinja raises "invoked with two values for the special caller argument". (b) `\rowstrut` and `{\bfseries\VAR{...}}` glued the control word to the following text. (c) The `\planspiel@...` helpers need `\makeatletter` inside the style. (d) The drift test counted the local `planspiel` style as an unknown TeX package.
- **Fix:** an empty `\BLOCK{if caller}\BLOCK{endif}` in the macro, `\rowstrut{}` and `\textbf{...}`, a `\makeatletter` / `\makeatother` pair, and `LOCAL_PACKAGES = {"planspiel"}` in `tests/test_print_preflight.py`.
- **Files modified:** print/templates/angriff.tex.j2, print/planspiel.sty, tests/test_print_preflight.py
- **Commits:** 7a81ed8, aa6587a

**2. [Rule 1 - Bug] Level hint cell and box alignment**
- **Found during:** Task 2 measurement
- **Issue:** `{\footnotesize\color{mhpgrey}...}` in a table cell added 1.5 mm per row (15 mm over ten rows); the fill-in boxes hung below the text line and overlapped the following hint line.
- **Fix:** `\textcolor{mhpgrey}{\footnotesize ...}`; boxes centred on the line with their 7 mm declared as height 4.4 mm and depth 2.6 mm; box widths 13 mm and 28 mm so the longest lines wrap less.
- **Commit:** aa6587a

### Plan deviations (recorded, not rule-driven)

- The result line sits at the end of page 2, after the wave-KZ step, not inside the Fall step as the template description in the plan lists it. The line names "Schaden nach Recovery", which is only known after Schritt 6; no test pins its position.
- `\fillreport` and its template calls were added in Task 2 (where the plan lists them) rather than Task 1, so the Task 2 RED run could fail on missing log lines.
- The Task 1 commit (7a81ed8) renders correctly (fast tests) but did not yet compile with TeX; the TeX fixes (1b, 1c above) arrived with the Task 2 commit. No intermediate PDF was committed.

## Auth gates

None.

## Known Stubs

None. The blank CIA rows and fill-in boxes are intended handwriting space.

## Threat Flags

None. No new network, auth or file-access surface; the template stays on the existing render path (T-04-21 to T-04-25 mitigations: template lint test, `tex_escape` finalize with the `Backup \& Disaster Recovery` test, D-19 commit order with `"dirty": false`, two-page and fragment tests).

## Open items

- Human print check (plan Task 2, collected into the phase UAT): print `final_documents/generated/angriff-1_ransomware.pdf` in colour, duplex, on A4, fill in a sample wave by hand (seven measures, Gesamtreduktion in Fall 3, M4 at level 2, KZ Events +5) and judge handwriting space, punch margin and colour legibility.
- `final_documents/Angriff-*.docx` stay untouched until Phase 7 (LEG-01). `CLAUDE.md` and `.claude/CLAUDE.md` still describe the docx print-sync trap for those legacy files; the documentation update belongs to Phase 7 (LEG-02).
- Page 1 of waves 1 and 3 has a reserve of only 3.5 to 4.5 mm; a longer narrative or intro text in `content/texte.toml` can push it over, and the pdf test `test_both_pages_fit_the_text_height_as_measured_in_the_log` will report it.

## Self-Check: PASSED

- Files exist: print/templates/angriff.tex.j2, tests/test_print_render.py, tests/test_print_worksheets_pdf.py, final_documents/generated/{angriff-1_ransomware.pdf, angriff-2_ot.pdf, angriff-3_exfil.pdf, manifest.json}
- Commits exist: 9ff1cde, 7a81ed8, bda2615, aa6587a, 3717276
