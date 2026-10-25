---
phase: 05-player-facilitator-print-material
plan: 03
subsystem: print
tags: [cards, tikz, lualatex, layout, pdf-tests, print-test]

requires:
  - phase: 05-player-facilitator-print-material
    provides: cards.py deck model, karten.tex.j2 kind-dispatched template, planspiel.sty card-sheet macros (05-02)
provides:
  - spieler-massnahmenkarten.pdf as 8 A4 landscape sheets, four A6 landscape cards per sheet, cut lines, stamp and page counter once per sheet
  - tests/test_cards_pdf.py (8 sheets, A4 landscape, stamp per sheet, strings per page, dependency strings, fit per card, one-line titles)
  - tests/test_print_documents_pdf.py (log hygiene for every job of the print set)
  - CARD and CARDTITLE log-marker regexes in tests/support/pdf_text.py (reused by the event deck in 05-05)
  - \cardheader (logged one-line title bar), \factbox (label bound to its value), \cardplain, \cardtechgap, card type set in planspiel.sty
  - user-approved physical print layout (5 rounds), reused unchanged by the event deck
affects: [05-04, 05-05, 05-07, 05-12]

tech-stack:
  added: []
  patterns:
    - "Layout limits are logged by LaTeX (PLANSPIEL-CARD used/limit, PLANSPIEL-CARDTITLE width/avail) and asserted by pdf tests parsing the log"
    - "Dimension arguments are not passed through Jinja \\VAR; the legend sample group uses \\renewcommand on length macros"
    - "Cards are A6 landscape, 2x2 on an A4 landscape page with zero margins; the outer card edge is the paper edge"

key-files:
  created:
    - tests/test_cards_pdf.py
    - tests/test_print_documents_pdf.py
  modified:
    - tests/support/pdf_text.py
    - print/planspiel.sty
    - print/templates/karten.tex.j2

key-decisions:
  - "Card layout is A6 landscape (148.5 x 105 mm), 2x2 on A4 landscape; body 12/14.5 pt, technical line 10/12 pt, title 17/20 pt bold, figures bold 14/16.5 pt, text columns 82 mm left and 48 mm right"
  - "Init-Kosten, OPEX and Voraussetzung are \\factbox boxes: a shaded caption band directly above its value, so a value reads only together with its label"
  - "Padding inside card boxes: cardcaptop 1.6 / cardcapbot 0.8 / cardvaltop 1.3 / cardvalbot 0.6 / cardplaintop 1.4 / cardplainbot 1 / cardplainside 2 / cardtechgap 1.6 mm; title bar padding cardheadsep 1.8 mm; badge box padding 3 pt"
  - "Every card title is set on one line and guarded: \\cardheader measures the title against the room before the level badge (minus 2 mm) and logs it; a pdf test fails if width exceeds avail"
  - "The event deck (05-05) reuses this layout through the same macros; any card using card_header is covered by the title guard"

patterns-established:
  - "A user print test is a blocking checkpoint; each round ends with a rebuilt preview in build/preview-rN and PNG renders in build/png"

requirements-completed: [PRINT-05]

duration: ~95 min active (14:19-14:31 on 2026-10-23, then 12:17-13:35 on 2026-10-25), plus the wait for the print test
completed: 2026-10-25
status: complete
---

# Phase 5 Plan 03: Measure deck layout on A4 card sheets Summary

**The measure deck builds as 8 A4 landscape sheets of A6 landscape cards (12/14.5 pt body, 17/20 pt one-line guarded titles), all 31 cards fit their cells and the user approved the printed layout in round 5.**

## Performance

- **Deck build time:** a full `uv run planspiel print` (all 4 documents, clean build directory, LuaLaTeX two-pass) took 23.5 s. The measure deck is one of the four, so its own share is below that.
- **Task 1 (RED + GREEN):** 14:19 to 14:31 on 2026-10-23.
- **Task 2 (five print-test rounds):** 12:17 to 13:35 on 2026-10-25.
- **Tasks:** 2 (Task 1 auto with TDD, Task 2 blocking print-test decision, approved "Freigeben")
- **Files modified:** 5 (2 tests created, `pdf_text.py`, `planspiel.sty`, `karten.tex.j2`)

## Accomplishments

- Deck laid out as 8 A4 landscape sheets, four A6 landscape cards each, with cut lines and one stamp plus `Seite x von 8` per sheet.
- Log hygiene test covers every job of the print set (missing glyphs and overfull lines), so later documents are covered automatically.
- Layout tuned over five user print-test rounds: larger type, cost labels tied to their values, padding inside boxes, a 17 pt title that is guaranteed to stay on one line.
- Layout approved on paper ("Freigeben") and fixed as the layout for the event deck in 05-05.

## Task Commits

1. **Task 1 RED: measure deck pdf layout tests** - `c59b4e5` (test)
2. **Task 1 GREEN: lay out the deck on A4 card sheets** - `491f5f1` (feat)
3. **Task 2 round 1: landscape A6 2x2 on A4 landscape, larger type** - `e91f20f` (fix)
4. **Task 2 round 2: card type 12/14.5 and 10/12, \factbox ties labels to values** - `813d296` (fix)
5. **Task 2 round 3: padding inside card boxes** - `85831ff` (fix)
6. **Task 2 round 4/5 RED: guard that every card title fits on one line** - `ca8c436` (test)
7. **Task 2 round 4/5 GREEN: enlarge the card title to 17 pt** - `39ccf2b` (fix)

Plan metadata: see the docs commit that adds this SUMMARY.

## RED runs

- **Task 1 (`c59b4e5`):** `2 failed / 7 passed`. `'M1-L3'` was missing in the PDF text (the test helper `printed_fragments` returned internal ids; fixed to use `cards.printed_strings`), plus the fit assertion on the first layout.
- **Round 1 (`e91f20f`):** the landscape test was written first: `1 failed / 6 passed` (sheets were portrait).
- **Round 4/5 (`ca8c436`):** `1 failed / 7 passed`, reason `assert {'M1-L1', 'M1...'M10-L3', ...} <= set()`: no `PLANSPIEL-CARDTITLE` marker existed yet. The test is parsed against the deck log for all 31 markers (30 measure cards plus the legend sample header).

## Final used/limit table (all 31 cards)

Source: `build/print/spieler-massnahmenkarten.log`, `PLANSPIEL-CARD` lines of the approved build. Heights are `ht+dp` of the card box in pt. Limit is the cell height minus the 7 mm safe margins and, in the lower row, the 8 mm footer strip. The legend has a higher limit because it is in an upper cell with a smaller body set. 0 Overfull boxes in the log.

| Card | used (pt) | limit (pt) | fill |
|------|-----------|------------|------|
| LEGEND | 252.8 | 258.9 | 98% |
| M1-L1 | 200.6 | 258.9 | 77% |
| M1-L2 | 213.2 | 236.2 | 90% |
| M1-L3 | 220.2 | 236.2 | 93% |
| M2-L1 | 186.7 | 258.9 | 72% |
| M2-L2 | 201.3 | 258.9 | 78% |
| M2-L3 | 196.8 | 236.2 | 83% |
| M3-L1 | 186.6 | 236.2 | 79% |
| M3-L2 | 215.7 | 258.9 | 83% |
| M3-L3 | 220.2 | 258.9 | 85% |
| M4-L1 | 218.0 | 236.2 | 92% |
| M4-L2 | 217.9 | 236.2 | 92% |
| M4-L3 | 232.5 | 258.9 | 90% |
| M5-L1 | 186.7 | 258.9 | 72% |
| M5-L2 | 201.2 | 236.2 | 85% |
| M5-L3 | 215.8 | 236.2 | 91% |
| M6-L1 | 202.7 | 258.9 | 78% |
| M6-L2 | 202.7 | 258.9 | 78% |
| M6-L3 | 212.6 | 236.2 | 90% |
| M7-L1 | 211.2 | 236.2 | 89% |
| M7-L2 | 213.3 | 258.9 | 82% |
| M7-L3 | 220.2 | 258.9 | 85% |
| M8-L1 | 190.5 | 236.2 | 81% |
| M8-L2 | 205.0 | 236.2 | 87% |
| M8-L3 | 216.0 | 258.9 | 83% |
| M9-L1 | 175.0 | 258.9 | 68% |
| M9-L2 | 201.1 | 236.2 | 85% |
| M9-L3 | 189.2 | 236.2 | 80% |
| M10-L1 | 186.7 | 258.9 | 72% |
| M10-L2 | 186.8 | 258.9 | 72% |
| M10-L3 | 198.8 | 236.2 | 84% |

Fullest measure cards: M1-L3 (93%), M4-L1 and M4-L2 (92%), M5-L3 (91%). No card overflows.

## Card title width at 17 pt (`PLANSPIEL-CARDTITLE`)

Available width is the bar width minus the level badge minus a 2 mm gap (346.5 pt = 121.8 mm for measure cards).

| Title | width | avail | slack |
|-------|-------|-------|-------|
| M10 - Mobile Device Management (MDM) (longest) | 330.6 pt = 116.2 mm | 346.5 pt = 121.8 mm | 5.6 mm |
| M7 - Vulnerability & Patch Management | 320.6 pt = 112.7 mm | 346.5 pt = 121.8 mm | 9.1 mm |
| M8 - Supplier Security & Supply Chain | 312.7 pt = 109.9 mm | 346.5 pt = 121.8 mm | 11.9 mm |

All 31 markers satisfy width <= avail. The longest title by width is M10, not M7/M8 (which have more characters but narrower ones); this corrects the earlier character-count answer given to the user.

## Fallback steps (plan steps a to d)

None of the plan's fallbacks (a) tighten spacing, (b) body 8.5 pt, (c) technical 7 pt, (d) focus into the subtitle line was applied: Task 1 fitted on the first layout, and the user's print test then asked for larger type, not smaller (see rounds below). Body went from the plan baseline up to 12 pt, technical to 10 pt, title to 17 pt. `content/texte.toml` was never changed.

## Visual inspection

PNG renders (110 dpi, `pdftoppm`) of the approved preview `build/preview-r5/spieler-massnahmenkarten.pdf`:

- `C:\Users\Claudio\Documents\Git\security_game\security-planspiel\build\png\karten-1.png`: legend card with annotated M1-L3 sample and four numbered explanations, plus M1 L1 to L3.
- `...\build\png\karten-2.png` to `karten-5.png`: M2 to M6 cards, text left and C/I/A plus fact boxes right, level strip in the level colour under the title bar.
- `...\build\png\karten-6.png`: M7 L2/L3 and M8 L1/L2, titles on one line (M7 and M8 have the longest multi-word titles).
- `...\build\png\karten-7.png`: M8 L3, M9 L1 to L3.
- `...\build\png\karten-8.png`: M10 L1 to L3 (longest title by width), fourth cell empty, footer stamp and `Seite 8 von 8`.

## User print test rounds (answers quoted verbatim)

Questions were asked in German. User answers:

1. Round 1: "querformat würde größer und besser passen" -> A6 landscape, larger type (`e91f20f`).
2. Round 2: "kann die größe optimiert werden? Text ist klein und viel platz übrig. init kosten und opex - die zugehörigkeit ist nicht direkt ersichtlich zu dem Kosten Wert..." -> type 12/14.5 body, 10/12 technical, 15/18 title, `\factbox` (`813d296`).
3. Round 3: "teilweise (z B beim Text "Init Kosten" stößt die Schrift an der Tabelle oben an. Kann man hier einen Abstand einfügen? bspw auch bei "Tägliche backups Office-IT ..."" -> padding inside all boxes (`85831ff`).
4. Round 4: "Kann die Überschrift noch etwas größer gemacht werden oder könnte es dann an einer stelle zu einem zeilenumbruch kommen? was ist der längste maßnahmen titel" -> longest titles reported; the user chose card title 17 pt (`ca8c436`, `39ccf2b`).
5. Round 5: "Freigeben" -> layout approved.

## Decisions Made

See key-decisions in the frontmatter. In short: A6 landscape 2x2 on A4 landscape; body 12/14.5, technical 10/12, title 17/20; factbox for Init-Kosten, OPEX and Voraussetzung; padding values as listed; one-line title guard via logged width/avail; the event deck in 05-05 reuses the layout.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Test helper compared internal ids with PDF text**
- **Found during:** Task 1 RED
- **Issue:** `printed_fragments` returned internal ids, so `'M1-L3'` was reported missing in the PDF.
- **Fix:** tests use `cards.printed_strings`.
- **Files modified:** tests/test_cards_pdf.py
- **Commit:** c59b4e5 / 491f5f1

**2. [Rule 3 - Blocking] `\geometry`, not `\newgeometry`, for the landscape sheet (round 1)**
- **Issue:** `\newgeometry` in the template did not produce an A4 landscape page for every sheet.
- **Fix:** set `\geometry{a4paper,landscape,...}` in the preamble.
- **Commit:** e91f20f

**3. [Rule 1 - Bug] 13/15.5 pt body overflowed (round 2)**
- **Issue:** the first attempt at a larger body overflowed the cells; the dimension arguments could not go through Jinja `\VAR`.
- **Fix:** settled at 12/14.5 pt; the legend sample group uses `\renewcommand` for lengths; `\cardsmall` split into `\cardtech` and `\cardlegendfont`.
- **Commit:** 813d296

**4. [Rule 1 - Bug] `\VAR{'legend-sample' if legend else card.card_id}` failed the plain-name guard (round 5)**
- **Found during:** full `uv run pytest -q` (`test_template_variables_are_plain_names`)
- **Fix:** `BLOCK{if legend}legend-sample BLOCK{else}\VAR{card.card_id}BLOCK{endif}`.
- **Commit:** 39ccf2b

### Judgement calls in round 5 (confirmed by approval)

- A custom header strut (14 pt up, 4 pt down) replaces `\strut` for the 17 pt title so the capitals sit centred in the bar (about 2.3 mm above capitals, 1.8 mm below descenders).
- New `\cardbadgesep` (3 pt, 2 pt in the legend sample) keeps the level badge at its previous size, since the larger bar padding would otherwise have enlarged it from about 6.6 to 8.1 mm.

**Total deviations:** 4 auto-fixed, 2 judgement calls. No impact on scope.

## Issues Encountered

- `\cardreport` measurement verified correct (ht+dp of the minipage, matches pixel analysis within about 1 mm); no enlargement of body type is possible within the cells.
- The chosen legend sample is the first card with a dependency (M1-L3); its header logs as `legend-sample`, so the title test has 31 markers.

## Verification

- `uv run pytest -m pdf tests/test_cards_pdf.py tests/test_print_documents_pdf.py -q`: 11 passed.
- `uv run pytest -q`: 1301 passed, 63 deselected.
- `uv run pytest -m pdf -q`: 41 passed.
- `git status --porcelain final_documents/generated`: empty.

## Next Phase Readiness

- 05-05 builds the event deck on the same macros (`\cardheader`, `\factbox`, `\cardplain`, cell geometry) and the same CARD and CARDTITLE guards.
- No blockers.

## Known Stubs

None.

## Self-Check: PASSED

- Files: tests/test_cards_pdf.py, tests/test_print_documents_pdf.py, tests/support/pdf_text.py, print/planspiel.sty, print/templates/karten.tex.j2 exist.
- Commits c59b4e5, 491f5f1, e91f20f, 813d296, 85831ff, ca8c436, 39ccf2b exist in `git log`.
