---
phase: 05-player-facilitator-print-material
plan: 06
subsystem: print
tags: [team-booklet, budget-planning, ros, budget-review, lualatex, formula-replay, jinja-partials]

requires:
  - phase: 05-player-facilitator-print-material
    provides: review_text.tier_rows and eventtext.effect_rows (05-05), card macros and fill-report conventions (05-03), veil scan and PREWAVE_MODULES AST guard (05-04)
provides:
  - spieler-teamheft.pdf, one booklet per team: Budget und Planung, Return on Security, Budget Review (3 A4 pages)
  - planspiel/booklet.py (TeamBooklet, PlanningPage, RosPage, Metric, build_team_booklet, BOOKLET_JOB, MAX_PENALTY_ROWS = 12)
  - teamheft.tex.j2 shell with page partials teamheft_planung.tex.j2 and teamheft_ros.tex.j2 and a commented insertion point for the tracking page (05-07)
  - [sheets.teamheft] wording (digit-free) in content/texte.toml and the mini texte
  - \rowpad, \rowstrutbig and a centred stretch column type Z in planspiel.sty
  - replay tests proving the printed RoS and remaining-budget formulas equal rules.evaluate_path
affects: [05-07, 05-15, 05-16]

tech-stack:
  added: []
  patterns:
    - "A booklet is a shell template that includes page partials; the shell logs a fill report (\\fillreport{\\thepage}) before every page break and before \\end{document}, so inserting a page needs no renumbering"
    - "A formula line names its operands in a grey note under its label instead of asking for them again, so no value is entered twice"
    - "Printed formulas are replayed in the test with independent arithmetic and compared with evaluate_path on three legal paths"

key-files:
  created:
    - planspiel/booklet.py
    - print/templates/teamheft.tex.j2
    - print/templates/teamheft_planung.tex.j2
    - print/templates/teamheft_ros.tex.j2
    - tests/test_booklet_model.py
    - tests/test_booklet_render.py
    - tests/test_booklet_pdf.py
  modified:
    - planspiel/render.py
    - planspiel/texts.py
    - print/planspiel.sty
    - content/texte.toml
    - tests/fixtures/mini_content/texte.toml
    - tests/test_veil_models.py

key-decisions:
  - "The RoS part is two pages, not one: RoS (own costs, damages, avoided damage, RoS) and a separate Budget Review page (remaining-budget ledger, tier rows, full overspend table). One page needed about 258 mm of 257 mm text height at the readable type size"
  - "Remaining budget is printed as the ledger of rules.budget_ledger: Verfügbares Budget = Tier-Budget + Budgetänderung durch Events; Gesamtkosten = Eigene Kosten + OPEX-Änderung durch Events; Restbudget = Verfügbares Budget − Gesamtkosten. Event values are entered with the sign the event card prints; the OPEX relief (a minus) stays inside the cost sum, so no double negative is needed"
  - "The overspend table is printed as two side-by-side tables (6 + 6 rows); RosPage.penalty_split holds the left row count"
  - "Fill reports use \\thepage, not literal page numbers, so plan 05-07 can insert the tracking page without touching the numbering"
  - "Own costs, Init total and OPEX total on the RoS and Review pages are carried sums from the earlier pages; only the start levels are guaranteed single-entry (planning table)"

patterns-established:
  - "MAX_PENALTY_ROWS guard: more overspend rows than the layout proof covers stops the build with PrintModelError naming the constant"
  - "Jinja macros do not suit this environment (finalize escapes macro output); partial templates repeat short rows inline instead"

requirements-completed: [PRINT-07]

duration: ~30 min active (08:56 to 09:25 on 2026-10-26)
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 06: Team booklet (planning, RoS, Budget Review) Summary

**`uv run planspiel print` now builds `spieler-teamheft.pdf` with a Budget und Planung page, a Return on Security page and a Budget Review page including the full overspend table; every printed formula is replayed against `rules.evaluate_path` on three legal paths.**

## Performance

- **Duration:** about 30 minutes
- **Tasks:** 2 (both auto, TDD)
- **Files modified:** 13 (7 created, 6 modified)

## Accomplishments

- `build_team_booklet(cfg, texts)` models three pages from config only: tier table `Tier | Verfügbares Budget | KZ Start` (`Low | 350.000 € | 50`), cost-type table, one planning row per measure, the anticipated-sum line `Summe Init-Kosten + Summe OPEX je Welle × 3`, the own-cost rows without any event row (RULE-06, F8), veiled damage rows `Schaden Angriff N`, `620.000 € − Summe der Schäden` from `rules.base_losses`, the RoS formula, the remaining-budget ledger, the tier rows (`review_text.tier_rows`) and the full overspend table (`review_text.penalty_rows`).
- `MAX_PENALTY_ROWS = 12` equals today's row count (X = 9, ceil(100 / 9)); a test pins exactly 12 rows on the real config, and a config copy with X = 5 (20 rows) raises `PrintModelError` naming `MAX_PENALTY_ROWS`.
- Replay tests (static plan, Kurswechsel swap with a positive window cost of 30 k€, swap plus a downgrade and an upgrade in window 2) recompute own costs, RoS and remaining budget with independent arithmetic and match `evaluate_path` exactly. The Sparprogramm cut lowers the remaining budget, the OPEX relief raises it.
- `booklet.py` is in the pre-wave AST guard; the booklet passes the story-profile veil scan (layers 1 and 2) and shows no Final-Index.
- `render.team_booklet` registers the job; the shell leaves a commented insertion point between the planning and RoS includes for plan 05-07.

## Task Commits

1. **Task 1 RED: failing team booklet model tests** - `a046d86` (test)
2. **Task 1 GREEN: team booklet model for planning and RoS** - `2f45e61` (feat)
3. **Task 2 RED: failing team booklet render and pdf tests** - `7f489c6` (test)
4. **Task 2 GREEN: team booklet with planning and RoS pages** - `50c383b` (feat)

Plan metadata: see the docs commit that adds this SUMMARY.

## RED runs

- **Task 1 (`a046d86`):** collection error `ModuleNotFoundError: No module named 'planspiel.booklet'` for `tests/test_booklet_model.py`; `tests/test_veil_models.py` also failed because `booklet.py` did not exist. After GREEN one test failed (`KeyError: 'params'`: the overspend penalty sits directly under the final event in the raw config); fixed in the test. Final: 40 tests in `tests/test_booklet_model.py` pass.
- **Task 2 (`7f489c6`):** `tests/test_booklet_render.py`: 7 failed, 16 errors (the `spieler-teamheft` job did not exist); `tests/test_booklet_pdf.py`: 2 failed, 7 errors (same reason). After GREEN: 25 render tests pass; three test fixes were needed (the Jinja shell starts with a comment, so the test asserts the document class instead of the file start; the review title also occurs inside the RoS title, so `rindex`).

## PLANSPIEL-FILL values (build `build/print-0506/spieler-teamheft.log`)

| Page | content | used (pt) | text height (pt) | fill |
|------|---------|-----------|------------------|------|
| 1 | Budget und Planung | 675.9 | 731.2 | 92% |
| 2 | Return on Security | 416.9 | 731.2 | 57% |
| 3 | Budget Review | 669.1 | 731.2 | 92% |

0 Overfull boxes, no missing glyph. With the real X the 12 overspend rows stand as 6 + 6; more rows would overflow page 3, which is exactly what `MAX_PENALTY_ROWS` guards.

## Visual inspection

PNG renders (110 to 150 dpi, `pdftoppm`) of `build/preview-0506/spieler-teamheft.pdf`, not written to `final_documents/generated`; files `C:\Users\Claudio\Documents\Git\security_game\security-planspiel\build\png\teamheft-0506-3.png` (page 3 at 150 dpi) and earlier iterations in the same folder:

- **Page 1, Budget und Planung:** title and budget intro, blue step bars `Kostenarten`, `Budget-Tier`, `Planung eurer Maßnahmen`. Cost table (Init-Kosten and OPEX with what and when), tier table with Low 350.000 € / 50, Medium 400.000 € / 42, High 450.000 € / 34, planning table with ten measure rows of 7 mm and a shaded Summe row, then the anticipated-sum line with a write-in box.
- **Page 2, Return on Security:** purpose, carry hint, then one `Kennzahl | Wert` table in 10 mm rows: Gesamt Init-Kosten, Init-Differenzen aus Change-Fenstern (inkl. Kurswechsel), Gesamt OPEX Kosten, shaded Eigene Kosten with its formula note, Schaden Angriff 1 to 3, shaded Summe der Schäden, Vermiedener Schaden (`= 620.000 € − Summe der Schäden`) and RoS (`= (Vermiedener Schaden − Eigene Kosten) ÷ Eigene Kosten`). About 43% of the page stays empty.
- **Page 3, Budget Review:** the sign hint, the remaining-budget ledger (Tier-Budget, Budgetänderung durch Events, shaded Verfügbares Budget, Eigene Kosten, OPEX-Änderung durch Events, shaded Gesamtkosten, shaded Restbudget), the four tier rows (`0 – 24.999 €` to `ab 75.000 €`), the bold overspend rule and the 12-row overspend table in two columns (`1 – 10.000 € → −9` to `110.001 – 120.000 € → −108`).

Text clearance follows the print-test preferences from 05-03: row struts give about 2 mm above and below single lines, `\rowpad` keeps the last line of multi-line cells about 1.9 mm above the rule below.

## Decisions Made

See key-decisions in the frontmatter. Additional points:

- Planning table rows stay at the Phase 4 minimum of 7 mm; the calculation pages (RoS, Budget Review ledger) use 10 mm rows because they have room and a value is written in each.
- The planning intro reuses the existing `sheets.budget.*` wording (budget intro, tier intro, anticipated-sum intro) instead of new text.
- A value cell in a shaded formula row stays shaded: `\cellcolor{white}` on the value cell was tried and dropped because it painted over the horizontal rules around it.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The RoS and Budget Review parts do not fit one page**
- **Found during:** Task 2 layout estimate and first build
- **Issue:** one page would need about 258 mm of the 257 mm text height at 10 pt with 7 mm rows and the 12-row overspend table.
- **Fix:** RoS and Budget Review are two pages inside the `teamheft_ros.tex.j2` partial (one `\clearpage` and one fill report between them). The plan's tests (RoS part starts on a new page, holds the formula, tier rows and penalty rows) are satisfied; the booklet has 3 pages.
- **Files modified:** print/templates/teamheft_ros.tex.j2, tests/test_booklet_render.py, tests/test_booklet_pdf.py
- **Commit:** 50c383b

**2. [Rule 1 - Bug] The shell must not hard-code page numbers**
- **Found during:** Task 2 design
- **Issue:** plan 05-07 inserts a page between planning and RoS; literal `\fillreport{1}`, `{2}` would then lie.
- **Fix:** `\fillreport{\thepage}`; the pdf test compares the number of fill reports with the number of pages.
- **Commit:** 50c383b

**3. [Rule 3 - Blocking] Jinja macros are not usable for repeated table rows**
- **Issue:** the strict environment applies `tex_escape` to every `\VAR`, including a macro's returned text, so a row macro called as an expression would be escaped twice.
- **Fix:** the short row patterns are repeated inline in the partials; the plain-variable lint passes for all three templates.
- **Commit:** 50c383b

**4. [Rule 1 - Bug] Fixed-width columns in `tabularx` produced a ragged table edge**
- **Issue:** the tier tables had only `C{..}` columns, so `tabularx` found no stretch column and the rules ran past the table.
- **Fix:** new column type `Z` (centred `X`) in `planspiel.sty` for the two tier tables.
- **Commit:** 50c383b

**Total deviations:** 4 auto-fixed. No impact on scope; PRINT-07 is complete.

## Issues Encountered

- Writing `\\` through a Bash heredoc collapsed it to `\`, so the first template build failed with `Misplaced \noalign`; the templates and the tests were then written with the Write tool.
- The static-plan replay uses `enforce_kurswechsel=False`, because the static plan of that start selection would otherwise (correctly) demand the Kurswechsel swap. This is the reference plan of the enumeration, not a legal full game, and is named in the test.
- Low-resolution PNGs (80 to 110 dpi) hide some 0.5 pt rules between shaded rows; the 150 dpi renders show them.

## Verification

- `uv run pytest -q`: 1456 passed, 91 deselected (baseline 1392 plus 64 new).
- `uv run pytest -m pdf -q`: 69 passed (baseline 60 plus 9 new), none skipped.
- `uv run pytest -m pdf tests/test_booklet_pdf.py tests/test_print_documents_pdf.py tests/test_veil_pdf.py -v`: 21 passed.
- `uv run planspiel texts`: 0 Fehler, 0 Warnung(en). `uv run planspiel validate`: 0 Fehler, 1 Warnung (the existing KZ slope 17/7 hand-calculation warning).
- `git status --porcelain final_documents/generated`: empty.

## Human check pending (end-of-phase)

Print `build/preview-0506/spieler-teamheft.pdf` single-sided in colour at 100 %, plan a medium-tier selection of five measures on page 1 with the printed measure cards, then fill page 2 and 3 with invented damages and event values. Points to look at: whether the sums carried to the RoS and Review pages (Gesamt Init-Kosten, Gesamt OPEX Kosten, Eigene Kosten) feel like a second entry; whether the OPEX-Änderung sign hint is clear; whether the half-empty RoS page should carry something else; the 10 mm rows on pages 2 and 3.

## Known Stubs

None.

## Threat Flags

None. The new printed text is digit-free wording from `[sheets.teamheft]` passing `tex_escape`, the digit lint and the story-profile veil scans (T-05-21 to T-05-24 mitigated as planned: formula replay on three paths with no event row in the own costs, `MAX_PENALTY_ROWS` guard and fill markers, veiled titles only with `booklet.py` in the AST guard, `tex_escape` plus plain-variable lint).

## Next Phase Readiness

- 05-07 inserts `teamheft_tracking.tex.j2` at the commented line in `teamheft.tex.j2` (followed by its own `\fillreport{\thepage}` and `\clearpage`), adds `tracking` to `TeamBooklet`, and updates the page-count expectations in `tests/test_booklet_pdf.py` (`len(pages) >= 3` today; the RoS and Budget Review page lookups are by content).
- 05-16 records `MAX_PENALTY_ROWS` under ROADMAP Phase 6 "Carried over from Phase 5": reviewing it together with a new proof of the Budget Review page is a Phase 6 item when X is calibrated (X = 5 gives 20 rows and stops the build).
- No blockers.

## Self-Check: PASSED

- Files: planspiel/booklet.py, print/templates/teamheft.tex.j2, teamheft_planung.tex.j2, teamheft_ros.tex.j2, tests/test_booklet_model.py, tests/test_booklet_render.py, tests/test_booklet_pdf.py exist; `def team_booklet(` in planspiel/render.py; `BOOKLET_JOB = "spieler-teamheft"`, `MAX_PENALTY_ROWS = 12`, `def build_team_booklet(` in planspiel/booklet.py.
- Commits a046d86, 2f45e61, 7f489c6, 50c383b exist in `git log`.
