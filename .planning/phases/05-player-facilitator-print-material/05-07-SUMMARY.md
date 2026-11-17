---
phase: 05-player-facilitator-print-material
plan: 07
subsystem: print
tags: [tracking-sheet, team-booklet, change-windows, kz-clamp, formula-replay, lualatex, jinja-partials]

requires:
  - phase: 05-player-facilitator-print-material
    provides: team booklet shell with fill reports and page partials (05-06), eventtext.EFFECT_KINDS and effect_rows (05-05), card and fill-report conventions (05-03)
provides:
  - one-page tracking sheet in spieler-teamheft.pdf between Budget und Planung and Return on Security (4 booklet pages now)
  - rules.KZ_MIN and rules.KZ_MAX used by clamp_kz and printed on the sheet
  - planspiel/booklet.py TrackingRow, WindowBlock, TrackingPage, TRACKING_ROW_ORDER, REVIEW_ROWS, MAX_WINDOWS, build_tracking_page, TeamBooklet.tracking
  - teamheft_tracking.tex.j2, [sheets.tracking] wording, shadedcell / rowstrutgrid / hdrs / column type L in planspiel.sty
  - tests/support/tracking_replay.py, an independent fill-in of the printed rows compared with rules.evaluate_path
affects: [05-08, 05-11, 05-15, 05-16]

tech-stack:
  added: []
  patterns:
    - "A table row model carries one cell state per column (write or shaded); the template only loops and emits a grey cell for each shaded state, so layout and event kinds cannot drift apart"
    - "The printed procedure is replayed column by column from card costs, the once-rounded worksheet change, printed event values and printed tier tables; the replay module is AST-checked to never touch the path evaluator"
    - "A layout guard constant (MAX_WINDOWS) stops the build with a message naming the constant when the config outgrows the proven page"

key-files:
  created:
    - print/templates/teamheft_tracking.tex.j2
    - tests/support/tracking_replay.py
    - tests/test_tracking_model.py
    - tests/test_tracking_pdf.py
  modified:
    - planspiel/rules.py
    - planspiel/booklet.py
    - planspiel/cards.py
    - planspiel/texts.py
    - print/templates/teamheft.tex.j2
    - print/planspiel.sty
    - content/texte.toml
    - tests/fixtures/mini_content/texte.toml
    - tests/test_booklet_model.py
    - tests/test_booklet_render.py
    - tests/test_booklet_pdf.py

key-decisions:
  - "The two change windows share one measure grid: a label column of the ten measures plus two columns (Level nach dem Fenster, Δ Init) per window, with the summary rows (Summe Init-Erhöhungen, Kurswechsel: Gutschrift Kunde, Init-Differenz netto) under it. The credit cell is shaded in every window except the Kurswechsel window. Stacked grids needed about 186 mm and did not fit"
  - "The Budget Review column reuses the table: Restbudget (all columns), plus two rows KZ-Änderung Review and KZ final that are writable only in that column; KZ final names its operands in its label (KZ final = KZ nach der letzten Welle + KZ-Änderung Review)"
  - "Writable tracking rows are 6 mm (new \\rowstrutgrid) instead of the 7 mm of the planning table; with 9 to 10 pt text this keeps about 1.3 to 1.5 mm clearance. The plan allowed 6 to 7 mm; the page does not fit at 7 mm"
  - "Init-Differenz netto is written in the column of the wave before the window (the window after Welle 1 is booked in the Welle 1 column), so the running Restbudget of the next column starts from the right value; the sheet says so"
  - "Δ Init is written only for increases; Senken and Kündigen leave it empty, so the Summe Init-Erhöhungen cannot contain a refund"
  - "The legacy status tracker is gone: sheets.budget.status_tracker_intro, sheets.labels.status_tracker, point_in_time and kz_cumulative are removed from SHEET_KEYS, content/texte.toml and the mini texte (a repo grep showed no reader besides texts.py and the two toml files)"

patterns-established:
  - "MAX_WINDOWS guard: a config with more change windows than the grid is proven for raises PrintModelError naming the constant"
  - "Shaded cells are a model state, not a template decision; the render test counts one \\shadedcell per shaded model cell"

requirements-completed: [PRINT-08]

duration: ~40 min active (09:24 to 10:04 on 2026-10-26)
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 07: Team tracking sheet Summary

**`uv run planspiel print` now builds a one-page tracking sheet inside `spieler-teamheft.pdf`: one column per point in time, rows in calculation order, own costs and external effects as separate blocks, a shared change-window grid with credit and net Init difference, and a replay of the printed rows that reproduces `rules.evaluate_path` for six legal paths on three tiers.**

## Performance

- **Duration:** about 40 minutes
- **Tasks:** 2 (both auto, TDD)
- **Files modified:** 15 (4 created, 11 modified)

## Accomplishments

- `rules.KZ_MIN = 0` and `rules.KZ_MAX = 100` replace the literals in `clamp_kz`; the sheet prints "KZ nach der Welle und KZ final werden begrenzt auf 0 bis 100" from those constants, and the characterization goldens are unchanged.
- `build_tracking_page(cfg, texts)` models columns `Start | Welle 1 | Welle 2 | Welle 3 | Budget Review` and twelve rows: KZ vor der Welle, KZ-Änderung der Welle, KZ nach der Welle, Schaden der Welle, then the block "Eigene Kosten (zählen für den RoS)" (Init-Kosten in Start only, OPEX dieser Welle, Init-Differenz netto only in waves followed by a window), the block "Externe Effekte (zählen nicht für den RoS)" (Event: Budget writable only in Welle 2, Event: OPEX only in Welle 1, derived from `EFFECT_KINDS`), Restbudget (laufend), KZ-Änderung Review and KZ final.
- The running Restbudget formula is printed under the table (`Restbudget = Restbudget der Spalte davor + Event: Budget − OPEX dieser Welle − Init-Differenz netto − Event: OPEX`, Start: `Tier-Budget − Init-Kosten`), consistent with the Budget Review ledger of 05-06 (event values with the sign of the event card, a OPEX relief stays inside the costs).
- The window grid lists `M1 – IAM/PAM` to `M10 – Mobile Device Management (MDM)` once, with Level and Δ Init per window; only the window after the Kurswechsel wave has the credit row ("Kurswechsel: Gutschrift Kunde"), and the net row reads "Init-Differenz netto = Summe Init-Erhöhungen − Gutschrift, nie eine Erstattung".
- `tests/support/tracking_replay.py` fills the printed rows with plain integer arithmetic (card costs through `rules.card_facts`, the once-rounded wave change and the damage as inputs, printed event values through `effect_rows`, printed tier and overspend tables through `review_text`, the clamp bounds). It matches `evaluate_path` for KZ after every wave, KZ final, own spend, remaining budget, window nets, Init and OPEX per wave and total damage on: all measures at level 1 (no swap possible), the Kurswechsel swap, swap plus a downgrade in window 2, each on low, medium and high; plus an overspend row of the printed table and the all-level-3 plan that clamps KZ at 100 after the waves and at 0 after the review.
- Negative control: with the credit row left out the first window difference (40 k EUR credit missing, 70 instead of 30) and the own spend no longer match; an AST test proves the replay never names `evaluate_path`, `simulate_waves`, `budget_ledger`, `evaluate_plan` or `simulate_selection`.

## Task Commits

1. **Task 1 RED: failing tracking sheet tests** - `24ec189` (test)
2. **Task 1 GREEN: tracking sheet model with clamp bounds from rules** - `e7e92b1` (feat)
3. **Task 2 RED: failing tracking page render and pdf tests** - `146cb8b` (test)
4. **Task 2 GREEN: one-page tracking sheet in the team booklet** - `78fcb5e` (feat)

Plan metadata: see the docs commit that adds this SUMMARY.

## RED runs

- **Task 1 (`24ec189`):** collection error `ImportError: cannot import name 'MAX_WINDOWS' from 'planspiel.booklet'` for `tests/test_tracking_model.py` (the tracking model did not exist, the replay was a `NotImplementedError` stub). After GREEN all 51 tests passed on the first run; a follow-up test for overspend and both clamps was added before the commit (53 tests).
- **Task 2 (`146cb8b`):** `tests/test_booklet_render.py` and `tests/test_booklet_model.py`: 17 failed (no `teamheft_tracking.tex.j2`, no `\shadedcell`, 3 page breaks expected, tracking fragments missing); `uv run pytest -m pdf tests/test_tracking_pdf.py tests/test_booklet_pdf.py`: 2 failed, 6 errors (the booklet had 3 pages and no tracking page). After GREEN: 125 render/model tests and 28 pdf tests pass.

## PLANSPIEL-FILL values (build `build/print-0507/spieler-teamheft.log`)

| Page | content | used (pt) | text height (pt) | fill |
|------|---------|-----------|------------------|------|
| 1 | Budget und Planung | 675.9 | 731.2 | 92% |
| 2 | Tracking-Bogen | 725.5 | 731.2 | 99% |
| 3 | Return on Security | 416.9 | 731.2 | 57% |
| 4 | Budget Review | 669.1 | 731.2 | 92% |

0 Overfull boxes, no missing glyph. The tracking page has 5.8 pt (about 2 mm) to spare; any extra line of text on it needs a new fit proof.

### Fallback steps applied to fit one page

The first build needed about 300 mm of 257 mm. In the order of the plan, plus text cuts:

1. (b) Writable rows 6 mm (`\rowstrutgrid`) in the main table and the window grid, compact blue header rows (`\hdrs`, 4.8 mm), block bars in `\small`.
2. (c) Both windows in one grid with two columns each (not stacked); label column left-aligned (`L`), grid labels in `\small`.
3. Wording trimmed: the step bars were dropped, the intro and the window intro shortened, the Budget-Review hint removed (the label "KZ-Änderung Review" and the Eventkarte carry it), the hints cut to one or two lines, the net label shortened to "Gutschrift" for its operand.
4. Table paragraphs end with `\par`, so hints do not run into the table line (this also fixed a stray word at the right margin).

No D-09 or D-10 row was dropped.

## Visual inspection

PNG renders (80, 110 and 150 dpi, `pdftoppm`, bounded with `timeout 60`) of `build/preview-0507/spieler-teamheft.pdf`, nothing written to `final_documents/generated`; the final 150 dpi render of the tracking page is `C:\Users\Claudio\Documents\Git\security_game\security-planspiel\build\png\tr0507d-2.png` (earlier iterations `tr0507*-2.png` in the same folder):

- **Top:** title, a one-line intro, then the main table with blue header (`Start`, `Welle 1`, `Welle 2`, `Welle 3`, `Budget Review`).
- **Main table:** the four KZ and damage rows, a blue bar "Eigene Kosten (zählen für den RoS)" with Init-Kosten (writable in Start only), OPEX dieser Welle and Init-Differenz netto (shaded in Welle 3), a blue bar "Externe Effekte (zählen nicht für den RoS)" with Event: Budget (writable in Welle 2) and Event: OPEX (writable in Welle 1), then the bold rows Restbudget (laufend), KZ-Änderung Review and the two-line KZ final. Grey cells are not applicable; adjacent grey cells merge into bands because the colour panel covers the thin rules between them (the same effect as on the 05-06 pages).
- **Under the table:** the clamp sentence (bold), then the rounding, external-effect and Restbudget hints in 8 pt grey italics.
- **Window grid:** blue header `Maßnahme | Change-Fenster nach Welle 1 | Change-Fenster nach Welle 2`, light-blue sub-header `Level nach dem Fenster | Δ Init` twice, ten 6 mm measure rows, then Summe Init-Erhöhungen, Kurswechsel: Gutschrift Kunde (shaded in window 2) and the two-line Init-Differenz netto row; two grey hint lines (credit rule, effect and OPEX from the next wave).

Points that are tight, not wrong: the window titles nearly touch the cell edges in the blue header, and text clearance in the 6 mm rows is about 1.3 to 1.5 mm (the print-test preference is about 1.5 to 2 mm). Both are worth a look in the end-of-phase print test.

## Decisions Made

See key-decisions in the frontmatter. Additional points:

- The Budget Review column is a column of the same table (Restbudget, KZ-Änderung Review, KZ final) instead of a separate block, so the whole bookkeeping reads left to right in time and top to bottom in calculation order.
- `cards._NOT_PRINTED` now also holds `key`, `group` and `cells`, because the tracking rows carry a row key, a group name and write/shaded cell states that must not count as printed text.
- `TeamBooklet.printed_fragments` included the tracking page only from the commit that adds the template (Task 2 GREEN), so the suite stayed green at the Task 1 commit.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The tracking page did not fit one A4 page as planned**
- **Found during:** Task 2 first builds (page overflow, the unbreakable window grid moved to the next page)
- **Issue:** stacked per-window grids plus 7 mm rows, intro and hints needed about 300 mm of 257 mm.
- **Fix:** the fallback steps listed above (6 mm rows, one shared grid for both windows, shortened wording, no step bars). This dropped the text keys `step_waves`, `step_windows` and `review_hint` that Task 1 had introduced, and added `window_credit_short`.
- **Files modified:** print/templates/teamheft_tracking.tex.j2, print/planspiel.sty, planspiel/booklet.py, planspiel/texts.py, content/texte.toml, tests/fixtures/mini_content/texte.toml
- **Commit:** 78fcb5e

**2. [Rule 3 - Blocking] Row keys, groups and cell states counted as printed text**
- **Found during:** Task 1 (printed fragments must all appear in the TeX)
- **Issue:** `printed_strings` walks every string field, so `kz_before`, `own` and `write` would have been treated as printed fragments.
- **Fix:** `key`, `group` and `cells` added to `cards._NOT_PRINTED` (a file outside the plan's list, one line plus comment).
- **Files modified:** planspiel/cards.py
- **Commit:** e7e92b1

**3. [Rule 2 - Missing critical] The replay needed texts and a credit switch**
- **Found during:** Task 1 (the event card values come from `effect_rows(event, cfg, texts)`; the negative control needs the credit left out)
- **Issue:** the planned signature `replay_tracking(cfg, tier_name, path, worksheet_changes, damages)` had neither.
- **Fix:** `replay_tracking(cfg, tier_name, path, worksheet_changes, damages, texts, ignore_credit=False)`.
- **Files modified:** tests/support/tracking_replay.py
- **Commit:** e7e92b1

**4. [Rule 2 - Missing critical] MAX_WINDOWS guard**
- **Found during:** Task 2 layout proof
- **Issue:** the grid is proven for two windows; a config with more would silently overflow.
- **Fix:** `MAX_WINDOWS = 2`; `build_tracking_page` raises `PrintModelError` naming the constant, with a test (monkeypatched to 1).
- **Files modified:** planspiel/booklet.py, tests/test_tracking_model.py
- **Commit:** e7e92b1

**Total deviations:** 4 auto-fixed. No scope change; PRINT-08 is complete.

## Issues Encountered

- Python in a Bash heredoc collapses `\\` and `\f` sequences: `\fillreport` became a form feed and test strings lost a backslash, so template and test edits went through the Edit and Write tools.
- `\small`, `\bfseries` and `\hint` followed directly by `\VAR{...}` printed `\smallM`-style undefined control sequences; each is followed by `{}` or a space now.
- A table paragraph without `\par` let the next hint run on the same line to the right of the table.
- An unbreakable `tabularx` jumps to the next page as a whole, so the overflow showed up as a nearly empty extra page until the total height was cut by about 45 mm.

## Verification

- `uv run pytest -q`: 1518 passed, 98 deselected (baseline 1456 plus 62 new: 53 in `tests/test_tracking_model.py`, 4 new render tests and net changes in the booklet tests).
- `uv run pytest -m pdf -q`: 76 passed, none skipped (baseline 69 plus 7 in `tests/test_tracking_pdf.py`).
- `uv run pytest -m pdf tests/test_tracking_pdf.py tests/test_booklet_pdf.py tests/test_print_documents_pdf.py tests/test_veil_pdf.py -v`: 28 passed.
- `uv run pytest tests/test_characterization.py -q`: unchanged goldens (part of the full run).
- `uv run planspiel texts`: 0 Fehler, 0 Warnung(en). `uv run planspiel validate`: 0 Fehler, 1 Warnung (the existing KZ slope 17/7 hand-calculation warning).
- `git status --porcelain final_documents/generated`: empty.

## Human check pending (end-of-phase)

Print `build/preview-0507/spieler-teamheft.pdf` (page 2), the measure deck, the event deck and `angriff-1_ransomware.pdf` single-sided in colour at 100 %. Play wave 1 for one medium-tier team with five measures: fill the worksheet, copy the rounded KZ change and the damage into the column Welle 1, enter OPEX and the OPEX relief (Event: OPEX), then perform the Kurswechsel swap plus one upgrade in change window 1 with the measure grid. Points to look at: whether every step has exactly one place to write; whether own costs and external effects read as separate; whether the swap credit and the net Init difference are computable without help; whether the remaining budget after wave 1 is obvious; whether the 6 mm rows leave enough room for handwriting and the clamp and rounding sentences are noticed; whether the Init-Differenz netto belonging in the column before the window is clear.

## Known Stubs

None.

## Threat Flags

None. The new printed text is digit-free wording from `[sheets.tracking]` (the only digits on the page are the wave numbers and the KZ bounds, both from config and `rules`), passes `tex_escape`, the plain-variable lint and the story-profile veil scans, and `booklet.py` stays in the pre-wave AST guard (T-05-25 to T-05-28 mitigated as planned: replay on legal paths plus negative control, separate labelled blocks with shading from the event kinds, veil and AST guards, `tex_escape` finalize).

## Next Phase Readiness

- `rules.KZ_MIN` and `rules.KZ_MAX` are ready for the wave explainer (05-08) and the Welle 0 guards (05-11); `TrackingPage` is part of `TeamBooklet` for the manifest and release checks (05-15, 05-16).
- 05-16 should record `MAX_WINDOWS` next to `MAX_PENALTY_ROWS` under ROADMAP Phase 6 "Carried over from Phase 5": a third window or a fourth wave needs a new layout proof of the tracking page (it has about 2 mm to spare).
- No blockers.

## Self-Check: PASSED

- Files: planspiel/booklet.py (`class TrackingRow`, `class WindowBlock`, `class TrackingPage`, `TRACKING_ROW_ORDER`, `def build_tracking_page(`), planspiel/rules.py (`KZ_MIN = 0`, `KZ_MAX = 100`), print/templates/teamheft_tracking.tex.j2, print/templates/teamheft.tex.j2 (`include "teamheft_tracking.tex.j2"`), tests/support/tracking_replay.py (`def replay_tracking(`), tests/test_tracking_model.py, tests/test_tracking_pdf.py exist; `[sheets.tracking]` in content/texte.toml and the mini texte; `"tracking"` in `PREWAVE_SHEETS`.
- Commits 24ec189, e7e92b1, 146cb8b, 78fcb5e exist in `git log`.
