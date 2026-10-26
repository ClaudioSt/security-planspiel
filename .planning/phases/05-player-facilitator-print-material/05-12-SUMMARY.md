---
phase: 05-player-facilitator-print-material
plan: 12
subsystem: print
tags: [welle-0, worked-example, practice-story, golden-test, shared-partial, filled-worksheet, lualatex]

requires:
  - phase: 05-player-facilitator-print-material
    provides: rules.path_trace, practice block, practice.check_example and practice_config (05-11), tracking sheet rows (05-07), event effect rows (05-05), veil scan with the practice audience (05-01)
provides:
  - user-approved practice story under [practice.*] in content/texte.toml (D-16), with required_keys and the story giveaway scope in planspiel/texts.py
  - printmodel.Box.value, fill_line, build_attack_sheet(view=, job=), AttackSheet.cia_filled / cia_sum / bonus_fulfilled
  - practice.PracticeView, PracticeDocument and build_practice_document, registered through render.practice_document (job uebung-welle-0)
  - shared worksheet partial print/templates/angriff_blatt.tex.j2 (angriff.tex.j2 is now a shell), print/templates/uebung.tex.j2, sty macros \ifilled and \tickfilled
  - eventtext.effect_rows(..., event_texts=None)
  - goldens tests/golden/welle0.json and tests/golden/worksheet_tex.json
affects: [05-14, 05-15, 05-16]

tech-stack:
  added: []
  patterns:
    - "A filled worksheet is the real worksheet model with its boxes filled by fill_line from the rules trace; the template prints a box with a value as a filled box and an empty one as before"
    - "Template split pinned by SHA-256 digests of the rendered .tex recorded before the refactor"
    - "A practice story lives under practice.* and is read through a view with the same methods as the revealed view, so the worksheet builder is reused unchanged"

key-files:
  created:
    - print/templates/angriff_blatt.tex.j2
    - print/templates/uebung.tex.j2
    - tests/test_practice_texts.py
    - tests/test_welle0_golden.py
    - tests/test_welle0_render.py
    - tests/test_welle0_pdf.py
    - tests/golden/welle0.json
    - tests/golden/worksheet_tex.json
  modified:
    - content/texte.toml
    - planspiel/texts.py
    - planspiel/printmodel.py
    - planspiel/practice.py
    - planspiel/eventtext.py
    - planspiel/render.py
    - print/templates/angriff.tex.j2
    - print/planspiel.sty

key-decisions:
  - "Bonus met is printed as a cross and missed as a dash in the Erfuellt box (Arial has no tick glyph; an empty box would read as not yet filled in)"
  - "The first box of the recovery line holds the damage before recovery without the euro sign: 20.000 € does not fit the short box and wrapped to two lines"
  - "The weight mutation test uses weights 0,3 / 0,1 / 0,6 with threshold 17: with the validator's weight scale of one decimal, only such a pair keeps the example on an exact half in Fall 3 with the clamp acting"
  - "The intro sits as a bold bar under the title through an optional intro variable of the shared partial (nothing is printed on the real worksheets)"

patterns-established:
  - "check_example is the single guard of the document: the selection rows, the event row and the tracking cells are additionally compared with the trace and raise PrintModelError on any divergence"

requirements-completed: [FLOW-01]

duration: ~100 min (11:52 to about 13:32 on 2026-10-26, with the story checkpoint in between)
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 12: Welle 0 worked example Summary

**`uv run planspiel print` now builds `uebung-welle-0.pdf` ("Welle 0 – Übung"): the real worksheet layout with every box filled from `rules.path_trace`, then a page with the example selection, the practice event and a filled tracking excerpt. The numbers are pinned by a golden file and replayed independently; the practice story was approved by the user before it was committed.**

FLOW-01 is complete with this plan (05-11 built the trace, config block and guards; this plan holds the story and the document).

## The practice story and the checkpoint (D-16)

Claude drafted the story (a failed storage system in the office file server after a firmware update; no mail lure, encryption or ransom, no production or OT outage, no data theft, supplier access or leak, no lost phone or cloud share). The draft was committed only after the user's answer.

User answer, verbatim: **"Freigeben + Fälle neutral"**. The three case texts were therefore phrased neutrally (no Ihr/Eure voice) to match the Beispielteam framing; every other key stayed as drafted.

Final story text (committed in `df4269c`):

```toml
[practice]
title = "Übung"
intro = "Bevor die erste Welle beginnt, rechnet ihr gemeinsam ein Beispiel durch. Der Vorfall ist erfunden und zählt nicht für eure Wertung. Alle Felder sind schon ausgefüllt: Verfolgt Schritt für Schritt, wie aus den Maßnahmen eines Beispielteams Schutzwerte, Schaden und Kundenzufriedenheit werden."
narrative = "Nach einem Firmware-Update fällt das zentrale Speichersystem im Büro aus. Der Dateiserver ist nicht mehr erreichbar, Projektordner und Vorlagen stehen niemandem mehr zur Verfügung. Ob der Betrieb schnell wieder läuft und wie groß der Schaden wird, wird im Folgenden anhand der Sicherheitsmaßnahmen des Beispielteams berechnet."
cia_rationale = "Hier zählt Verfügbarkeit (A) am meisten, weil ohne Dateiserver niemand an die Daten kommt. Vertraulichkeit (C) und Integrität (I) zählen gleich viel, aber weniger."
case_1 = "Die Maßnahmen reichen nicht aus, der Ausfall trifft das Unternehmen voll."
case_2 = "Der Ausfall wird vollständig abgefangen."
case_3 = "Die Auswirkungen werden teilweise gemindert."
selection_title = "Auswahl des Beispielteams"
event_result = "Wirkung des Ereignisses auf das Beispielteam"
tracking_title = "So sieht der Eintrag im Tracking-Bogen aus"

[practice.bonus_reasons]
M9 = "Geprüfte Cloud-Einstellungen: die Ersatzablage der Projektdaten in der Cloud steht sofort bereit"
M10 = "Verwaltete Smartphones und Tablets mit freigegebenen Apps halten das Team auch ohne Dateiserver arbeitsfähig"

[practice.event]
narrative = "Schon Tage vor dem Ausfall meldet das Speichersystem Plattenwarnungen und Fehler in den Protokollen. Wer die Protokolle auswertet, sieht die Warnungen rechtzeitig. Wer sie nicht auswertet, merkt es erst, wenn alles steht."

[practice.event.tier_labels]
0 = "Warnungen bleiben unbemerkt"
1 = "Warnungen liegen in den Protokollen, werden aber spät gelesen"
2 = "Alarm kommt rechtzeitig an"
3 = "Fachleute greifen sofort ein und dokumentieren den Fall"
```

The printed title `Welle 0 – Übung` is composed in code (word from the tracking sheet, number from the wave id, name from `practice.title`).

## Accomplishments

- **Document (Task 3):** page 1 and 2 are the real worksheet pages with every box filled (CIA rows of the four selected measures and their sum, E-value, bonus table with a cross for M9 and a dash for M10, Gesamtreduktion 23, Fall 3, damage 20.000 €, recovery 10 % to 18.000 €, attack KZ +6,5, event −4, exact +2,5 rounded to +3, result line). Page 3: the example selection (Init 104.000 €, OPEX 23.000 € je Welle), the practice event with its generated effect rows and the row that applies, and the tracking excerpt (Start and Welle 0, KZ 98 to 100 with the hint 101 → 100, Restbudget 96.000 € to 73.000 €). No change window.
- **Single source:** every filled value comes from `rules.path_trace` through `practice.check_example`; the selection totals, the event row value and the tracking cells are compared with the trace again and raise `PrintModelError` otherwise.
- **Golden test (SC3):** filled values equal the trace; `tests/support/worksheet_replay.py` replayed on the sheet's exact fields (CIA from the filled rows) gives the same case, damage, attack KZ and change; `tests/golden/welle0.json` pins every printed string; a config copy with other practice weights (0,3 / 0,1 / 0,6, threshold 17) changes the printed E-value line (18,4).
- **Real worksheets unchanged (T-05-41):** the SHA-256 of the three `.tex` files was recorded before the template split (`6a5ca22`) and is identical after it.
- **Veil:** the `uebung-welle-0` document passes the layer-1 and layer-2 practice scans (no real weight triple, name or revealed string); it prints its own weights on purpose (D-12/D-14 exception); the mini config renders no practice job.

## RED runs

- Task 1: `uv run pytest tests/test_practice_texts.py -q` gave 8 failed, 8 passed (the practice keys were not required and the practice scope was not scanned). Commit `ef68330`.
- Task 3: `uv run pytest tests/test_welle0_golden.py tests/test_welle0_render.py` gave an ImportError (`cannot import name 'fill_line'`) and 10 failed render tests; `uv run pytest -m pdf tests/test_welle0_pdf.py` gave 6 failed, 3 errors (no practice job). Commit `deb124e`.

## Verification

- `uv run pytest -q`: 2122 passed, 140 deselected (baseline 2075 after 05-11; +16 text tests, +31 Welle 0 tests).
- `uv run pytest -m pdf -q`: 118 passed (109 before; +9 in `tests/test_welle0_pdf.py`, none skipped).
- `uv run pytest -m pdf tests/test_welle0_pdf.py tests/test_print_worksheets_pdf.py tests/test_print_documents_pdf.py tests/test_veil_pdf.py -v`: 27 passed.
- `uv run planspiel validate`: 0 errors, 1 warning (the known 17/7 KZ-slope warning); `uv run planspiel texts` and `uv run planspiel clues`: 0 errors.
- `git status --porcelain final_documents/generated`: empty (nothing written there; previews went to `build/preview-w0`).
- The preview PNGs of all three pages were inspected: every box is filled and readable, the recovery line fits after the fix below, the page fill is 639, 569 and 542 pt of 731 pt.

## Task Commits

1. Task 1 RED: `ef68330` test(05-12): add failing practice text coverage tests
2. Task 2 (after the user's answer): `df4269c` feat(05-12): add the reviewed practice story
3. Task 3 digest pin: `6a5ca22` test(05-12): pin the real worksheet tex digests before the template split
4. Task 3 RED: `deb124e` test(05-12): add failing Welle 0 document tests
5. Task 3 GREEN: `1c59023` feat(05-12): generate the Welle 0 worked example

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Damage before recovery wrapped in the short box**
- **Found during:** Task 3 (preview inspection)
- **Issue:** `20.000 €` does not fit the 13 mm short box of the recovery line and wrapped to two lines.
- **Fix:** the first box of that line holds the number without the euro sign (the other boxes of the line and the result keep the unit); test and golden updated.
- **Files modified:** planspiel/practice.py, tests/test_welle0_golden.py, tests/golden/welle0.json
- **Commit:** 1c59023

**2. [Rule 1 - Bug] Level hint counted as a printed fragment of the filled sheet**
- **Found during:** Task 3 (render test)
- **Issue:** `printed_fragments` listed the blank-row hint `(1 / 2 / 3)`, which a filled CIA table does not print.
- **Fix:** the hint counts only while the CIA table has blank rows.
- **Files modified:** planspiel/printmodel.py
- **Commit:** 1c59023

### Other adjustments

- The mutation test could not use the plan's example of "any other weight": the validator's weight scale of one decimal and the build guards (exact half, clamp) reject most weight sets. The test sets weights 0,3 / 0,1 / 0,6 together with threshold 17, which keeps every guard satisfied (documented in the test).
- The Task 1 behavior bullet "the title is composed in code" is tested in Task 3 (`tests/test_welle0_golden.py::test_job_and_title`), where `PracticeDocument.title` lives.
- Bonus marks: a cross for met and a dash for missed (see key decisions); the plan only said "text".

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. T-05-50 (story hinting at a real attack): story-profile lint plus a stricter veiled-profile test on all practice texts, the veil scans of the document, and the user review before commit. T-05-40: values from `path_trace`, replay, golden and mutation test, build guards. T-05-41: pinned digests. T-05-42: `tex_escape` and the plain-variable lint on the new templates.

## Next Phase Readiness

`print --check` against the committed `final_documents/generated` will report the new `uebung-welle-0` document as missing until 05-16 regenerates that folder (nothing was written there on purpose). 05-14 and 05-15 can reuse `path_trace` and `practice.check_example`; `Config.practice` must stay the last Config field.

## Self-Check: PASSED

- Created files exist: `print/templates/angriff_blatt.tex.j2`, `print/templates/uebung.tex.j2`, `tests/test_practice_texts.py`, `tests/test_welle0_golden.py`, `tests/test_welle0_render.py`, `tests/test_welle0_pdf.py`, `tests/golden/welle0.json`, `tests/golden/worksheet_tex.json`.
- Commits `ef68330`, `df4269c`, `6a5ca22`, `deb124e`, `1c59023` are in `git log`.
