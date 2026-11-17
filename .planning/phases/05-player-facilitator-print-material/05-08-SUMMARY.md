---
phase: 05-player-facilitator-print-material
plan: 08
subsystem: print
tags: [wave-explainer, tikz-flow-diagram, recovery-table, lualatex, jinja, veil]

requires:
  - phase: 05-player-facilitator-print-material
    provides: rules.KZ_MIN/KZ_MAX and [sheets.tracking] wording (05-07), eventtext.EFFECT_KINDS (05-05), fill report and page conventions (05-03, 05-06)
provides:
  - spieler-so-funktioniert-eine-welle.pdf, one A4 page with a TikZ flow diagram, the steps table, the attacks-vs-events table and the Backup & Recovery table
  - planspiel/wave_page.py (WAVE_PAGE_JOB, FlowStep, WavePage, build_wave_page, WavePage.effect_rows, printed_fragments)
  - rules.recovery_carriers and rules.recovery_table (single recovery measure and its factor per level, independent of any attack)
  - "[sheets.welle] wording; \"angriff\" and \"welle\" are now pre-wave sheets"
  - textrowtop / textrowend text-cell struts in planspiel.sty
affects: [05-11, 05-15, 05-16]

tech-stack:
  added: []
  patterns:
    - "A pre-wave page reuses the worksheet's step headings and the tracking sheet's labels verbatim; equality tests tie the vocabularies together"
    - "Table text cells open with \\textrowtop and close with \\textrowend, so the clearance to the rules does not stretch the leading between lines"
    - "A diagram laid out for a fixed number of nodes is guarded by a test on the label count"

key-files:
  created:
    - planspiel/wave_page.py
    - print/templates/welle.tex.j2
    - tests/test_wave_page.py
    - tests/test_wave_page_pdf.py
  modified:
    - planspiel/rules.py
    - planspiel/render.py
    - planspiel/texts.py
    - print/planspiel.sty
    - content/texte.toml
    - tests/fixtures/mini_content/texte.toml
    - tests/test_texts_views.py
    - tests/test_veil_models.py
    - tests/test_single_definition.py

key-decisions:
  - "The recovery factor is printed as a percentage (fmt.format_percent: 0 %, 10 %, 30 %, 50 %), like the Recovery-Faktor r column of the attack worksheet. The plan's test line said fmt.format_number; a player would otherwise read 0,3 on the explainer and 30 % on the worksheet"
  - "The steps carry no numbers. The worksheet numbers its own steps by position and skips the recovery step for waves without recovery, so an explainer numbering (events first) would contradict the worksheet. Order is shown by the arrows and the table order"
  - "The window step heading is the leading word of the tracking sheet's window title ('Change-Fenster' in 'Change-Fenster nach Welle'), checked by a startswith test and a build-time PrintModelError; the clamp step heading equals the tracking row label 'KZ nach der Welle'"
  - "Step texts are digit-free wording from [sheets.welle]; the case numbers, the KZ bounds and the recovery table are the only digits on the page (ascertained by a test that strips the allowed strings and finds no digit left; the allowlisted ',5' of the rounding wording is one of them)"
  - "Fit fallbacks applied: 9 pt text in the steps table (a), recovery narrative left of the recovery table (c), trimmed wording. The diagram stays in two rows of five"

patterns-established:
  - "rules.recovery_carriers is the one place that lists recovery measures; worksheet_constants and recovery_table both use it"

requirements-completed: [PRINT-09]

duration: ~30 min (10:07 to 10:37 on 2026-10-26)
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 08: Wave explainer "So funktioniert eine Welle" Summary

**`uv run planspiel print` now builds `spieler-so-funktioniert-eine-welle.pdf`: one A4 page with a ten-node TikZ flow diagram, the wave steps in the worksheet's and the tracking sheet's own words, an attacks-vs-events table, and the Backup & Recovery section with the generated recovery table, using symbols only and no wave values.**

## Performance

- **Duration:** about 30 minutes
- **Tasks:** 2 (both auto, TDD)
- **Files modified:** 13 (4 created, 9 modified)

## Accomplishments

- `rules.recovery_carriers(measures)` and `rules.recovery_table(cfg)` return the single recovery measure ("M4") with a `RecoveryRow` per level, independent of any attack or wave; a second carrier raises `WorksheetInvariantError`, no carrier gives `(None, ())`. `worksheet_constants` uses `recovery_carriers` and still raises only for an attack that allows recovery (goldens and worksheet tests unchanged). Both names are registered in `FORMULA_FUNCTIONS`.
- `build_wave_page(cfg, texts)` models ten steps in order `events, cia, e_value, bonus, reduction, cases, recovery, wave_kz, clamp, window`. The headings of `cia ... wave_kz` equal `sheets.angriff.step_*`, `events` equals the label "Events", `clamp` equals the tracking row "KZ nach der Welle". The reduction step defines "Gesamtreduktion (GR)" (IN-02), the e-value step reuses the card legend formula `E-Wert = C · wC + I · wI + A · wA`, the cases step describes Fall 1/2/3 in words with Schwelle, Kappung and Obergrenze, the rounding sentence embeds the allowlisted `gerundet (ab ,5 vom Betrag aufrunden)`, and the clamp sentence is built from `rules.KZ_MIN`/`KZ_MAX` with the tracking sheet's own lead words ("... begrenzt auf 0 bis 100").
- The attacks-vs-events table lists what attacks affect (Schaden in Euro, KZ) and what events affect (KZ, Budget, OPEX, derived from `eventtext.EFFECT_KINDS`, leaving out `window` and `review`); a note says own costs and damage count for the RoS and event effects on budget and OPEX do not (RULE-06). The empty cell of the shorter column is shaded.
- The Backup & Recovery section takes title, subtitle and narrative from `[sheets.backup_recovery]`, labels the table "M4 – Backup & Disaster Recovery" and shows level badge, level label and factor for levels 0 to 3 (0 %, 10 %, 30 %, 50 %). It names no wave, and the recovery step only says that the worksheet states whether a wave allows recovery (D-26).
- `"angriff"` and `"welle"` joined `PREWAVE_SHEETS`: the worksheet wording is generic, a new test shows every `sheets.angriff` string clean under the story giveaway profile, and the existing pre-attack leak test covers it. `wave_page.py` is in the pre-wave AST guard.
- `welle.tex.j2` uses TikZ `positioning` and `arrows.meta` only: ten rounded `mhplight` nodes with `mhpblue` borders in two rows of five (the second row read right to left), nine arrows, one `tikzpicture`.

## Task Commits

1. **Task 1 RED: failing wave explainer tests** - `e19473d` (test)
2. **Task 1 GREEN: wave explainer model** - `9af9008` (feat)
3. **Task 2 RED: failing render and pdf tests** - `9fa52ee` (test)
4. **Task 2 GREEN: one-page wave explainer** - `c837167` (feat)

Plan metadata: see the docs commit that adds this SUMMARY.

## RED runs

- **Task 1 (`e19473d`):** `tests/test_wave_page.py` collection error `ImportError: cannot import name 'recovery_table' from 'planspiel.rules'`; the other suites ran: 5 failed, 113 passed (`test_pre_attack_view_reaches_the_angriff_and_welle_sheets` x2, `test_formula_defined_once_in_rules[recovery_carriers]`, `[recovery_table]`, `test_prewave_modules_do_not_reference_revealed_data[wave_page.py]`). After GREEN: 185 passed in the six named suites, 1572 passed in the full suite.
- **Task 2 (`9fa52ee`):** `tests/test_wave_page.py`: 3 failed, 47 passed, 12 errors (`KeyError: 'spieler-so-funktioniert-eine-welle'` from `render_all`, no `welle.tex.j2`); `uv run pytest -m pdf tests/test_wave_page_pdf.py`: 4 failed, 6 errors (no PDF for the job). After GREEN: all 10 pdf tests PASSED, none skipped.

## PLANSPIEL-FILL value (build `build/print-0508/spieler-so-funktioniert-eine-welle.log`)

`PLANSPIEL-FILL page=1 used=715.71292pt text=731.23584pt` (98 %, about 15.5 pt or 5.5 mm to spare). No Overfull box, no missing glyph, no undefined control sequence. Any extra line on the page needs a new fit proof.

### Fallback steps applied to fit one page

The first full build needed about 746 pt of 731 pt (the recovery block moved to a second page). In the order of the plan, plus text cuts:

1. (a) The steps and effects tables are set in 9 pt (`\small`).
2. (c) The recovery narrative sits left of the recovery table (33 % / 65 % of the line) instead of above it, and the table column widths keep the measure title on one line.
3. Wording trimmed: the intro to one sentence, the cases lead to one sentence, the Fall 3 sentence without the worksheet pointer, shorter event and recovery step texts. Diagram nodes 11 mm high, section gaps 2 mm.
4. Text cell struts instead of generic row height: `\textrowtop` (1.6 mm clear above the first 9 pt line) and `\textrowend` (1.5 mm below the last line). Putting a strut with depth on the first line widened the leading of multi-line cells; the split into a top and an end strut fixed that.

No step was dropped.

## Visual inspection

PNG renders (80, 110 and 150 dpi, `pdftoppm`, bounded with `timeout 60`) of `build/preview-0508/spieler-so-funktioniert-eine-welle.pdf`, nothing written to `final_documents/generated`; the final 150 dpi render is `C:\Users\Claudio\Documents\Git\security_game\security-planspiel\build\png\w0508final-1.png` (iterations `w0508*-1.png` in the same folder):

- **Top:** blue title, one intro sentence, then the diagram: Events, CIA-Werte eintragen, E-Wert berechnen, Bonus prüfen, Gesamtreduktion berechnen in the top row left to right, an arrow down, then Fall bestimmen ..., Recovery anrechnen, KZ-Änderung dieser Welle, KZ nach der Welle, Change-Fenster right to left.
- **Steps table:** bold blue heading left, explanation right, ten rows, about 1.5 mm clear between text and rules.
- **Effects table:** blue header "Angriffe wirken auf | Events wirken auf", two attack rows and three event rows, the empty attack cell grey, the bold RoS note under it.
- **Recovery:** blue bar "Backup & Recovery", grey italic subtitle, narrative on the left, table on the right with green, yellow and grey level badges for levels 1 to 3 and a plain 0.

## Decisions Made

See key-decisions in the frontmatter.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Consistency] Recovery factor printed as percentage, not `fmt.format_number`**
- **Found during:** Task 1 (model) while comparing with the worksheet
- **Issue:** the worksheet prints the recovery factor as `fmt.format_percent` ("10 %") under "Recovery-Faktor r"; the plan's behavior line asked for `fmt.format_number` ("0,1"). Two spellings of the same number on two pages of one set would confuse players, against the plan's "one vocabulary" aim.
- **Fix:** `recovery_rows` use `fmt.format_percent`; the test pins this.
- **Files modified:** planspiel/wave_page.py, tests/test_wave_page.py
- **Commit:** 9af9008

**2. [Rule 3 - Blocking] Existing pre-wave view tests encoded the old sheet boundary**
- **Found during:** Task 1 GREEN (adding `"angriff"` to `PREWAVE_SHEETS`, as the plan requires)
- **Issue:** `test_pre_attack_view_refuses_the_attack_worksheet` expected a KeyError for `sheet("angriff")`, and `test_pre_attack_strings_cover_every_text_family` expected `sheets.angriff.case_3_hint` not to be reachable.
- **Fix:** the first test now asserts that non-pre-wave sheet names ("attacks", "revealed") raise; the second asserts the opposite for the angriff and welle strings. Both changes are the plan's deliberate design choice (T-05-31), covered by the new story-profile test.
- **Files modified:** tests/test_texts_views.py
- **Commit:** 9af9008

**3. [Rule 2 - Missing critical] Guards for a diagram laid out for ten steps and for a config without recovery**
- **Found during:** Task 1 / Task 2
- **Issue:** the template draws exactly ten nodes; a changed step list would silently misdraw. A config without a recovery measure would leave the recovery section without a table.
- **Fix:** a test pins `len(diagram_labels) == 10` and the node/arrow counts of the rendered diagram; `build_wave_page` raises `PrintModelError` when `recovery_table` finds no carrier or when the window heading is not the start of the tracking window title.
- **Files modified:** planspiel/wave_page.py, tests/test_wave_page.py
- **Commit:** 9af9008, c837167

**4. [Rule 3 - Blocking] Additions beyond the planned interface**
- **Issue:** the table header and the paired effect cells needed data the planned `WavePage` fields did not carry.
- **Fix:** `WavePage.recovery_header` (level, measure label, factor label), `WavePage.effect_rows()` (padded pairs), `FlowStep` unchanged, the text key `sheets.welle.step_window` ("Change-Fenster").
- **Files modified:** planspiel/wave_page.py, content/texte.toml, mini texte
- **Commit:** 9af9008

**Total deviations:** 4 auto-fixed. No scope change; PRINT-09 is complete.

## Issues Encountered

- Python in a Bash heredoc collapsed `\\` and `\b`/`\r` sequences, so a first edit of `print/planspiel.sty` and the template wrote form feeds and carriage returns; both were restored (`git checkout` for the style file, a fresh Write for the template) and all later TeX edits went through the Edit and Write tools or `chr(92)`.
- A `\color` set in a `>{...}` column specification put the heading cell on a lower baseline than the text cell; the colour is applied inside the cell with `\textbf{\color{...}}` instead.
- `\rule[-2.6mm]{0pt}{4.2mm}` (the first `\textrow`) only reaches 1.6 mm above the baseline (height minus raise), which put 9 pt text 1 mm from the rule; the final struts are explicit.

## Verification

- `uv run pytest -q`: 1587 passed, 108 deselected (baseline 1518 plus 69 new: model, render and the updated suites).
- `uv run pytest -m pdf -q`: 86 passed, none skipped (baseline 76 plus the 10 tests of `tests/test_wave_page_pdf.py`).
- `uv run pytest -m pdf tests/test_wave_page_pdf.py tests/test_print_documents_pdf.py tests/test_veil_pdf.py -v`: 22 passed.
- `uv run planspiel texts`: 0 Fehler, 0 Warnung(en). `uv run planspiel validate`: 0 Fehler, 1 Warnung (the existing KZ slope 17/7 hand-calculation warning).
- `git status --porcelain final_documents/generated`: empty.

## Human check pending (end-of-phase)

Give `build/preview-0508/spieler-so-funktioniert-eine-welle.pdf` to someone who has not read the rules, together with a blank attack worksheet and the tracking page, and ask them to explain the order of one wave. Expected: events, attack steps, recovery, round once, clamp, change window; events change KZ, budget and OPEX, attacks change damage and KZ; no hint which attack comes. Points to look at: whether the diagram's second row (read right to left) is followed without help, whether the 9 pt step text is readable on paper, whether the page is understood as a reference next to the worksheet.

## Known Stubs

None.

## Threat Flags

None. The page prints only digit-free wording from `[sheets.welle]`, the generic `sheets.angriff` step words, the KZ bounds, the case numbers and the recovery table; it passes `tex_escape`, the plain-variable lint and the story-profile veil scans on the model, the TeX and the PDF (T-05-29 to T-05-32 mitigated as planned: only-digits test, equality tests for the step headings, story-profile test on every `sheets.angriff` string, `tex_escape` finalize).

## Next Phase Readiness

- The explainer is a registered pre-wave job (`spieler-` prefix, story profile); 05-11 (Welle 0) can point to it and 05-15 and 05-16 find it in the printed set automatically.
- The fit proof leaves about 5.5 mm; a longer step text, a longer measure name or a second recovery table row needs a new layout check.
- No blockers.

## Self-Check: PASSED

- Files: planspiel/wave_page.py (`WAVE_PAGE_JOB = "spieler-so-funktioniert-eine-welle"`, `def build_wave_page(`), planspiel/rules.py (`def recovery_table(`, `def recovery_carriers(`), planspiel/render.py (`def wave_page(`), print/templates/welle.tex.j2 (`tikzpicture`, `\fillreport{1}`), tests/test_wave_page.py, tests/test_wave_page_pdf.py exist; `[sheets.welle]` in content/texte.toml and the mini texte; `"angriff"` and `"welle"` in `PREWAVE_SHEETS`; `"wave_page.py"` in `PREWAVE_MODULES`.
- Commits e19473d, 9af9008, 9fa52ee, c837167 exist in `git log`.
