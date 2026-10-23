---
phase: 05-player-facilitator-print-material
plan: 02
subsystem: print
tags: [cards, tikz, jinja, lualatex, rules, tdd]

requires:
  - phase: 05-player-facilitator-print-material
    provides: audience.MEASURE_DECK_JOB, job-prefix registry, veil scan, PREWAVE_MODULES guard
provides:
  - rules.card_facts and rules.level_requirements (one definition of the dependency rule)
  - cards.py deck model: MeasureCard, LegendCard, CardLabels, CardDeck, build_measure_deck (31 cards, 8 sheets)
  - karten.tex.j2, a kind-dispatched A6 deck template (event cards in 05-05 add branches)
  - planspiel.sty card-sheet macros (cardsheet, cardcell, cardreport, lockicon, callout, sheet footer overlay)
  - spieler-massnahmenkarten registered in DOCUMENT_BUILDERS and veil-scanned
affects: [05-03, 05-04, 05-05, 05-07, 05-12]

tech-stack:
  added: []
  patterns:
    - "Deck model: frozen dataclasses of finished strings, CardDeck.printed_fragments() as in AttackSheet"
    - "Card body set into a global box so \\cardreport can log used/limit height after the environment"
    - "Cell position from a TeX counter reset per cardsheet, so the template never prints an int"

key-files:
  created:
    - planspiel/cards.py
    - print/templates/karten.tex.j2
    - tests/test_cards_model.py
    - tests/test_cards_render.py
  modified:
    - planspiel/rules.py
    - planspiel/render.py
    - planspiel/texts.py
    - planspiel/texbuild.py
    - print/planspiel.sty
    - print/miktex-packages.txt
    - content/texte.toml
    - tests/fixtures/mini_content/texte.toml
    - tests/test_veil_models.py
    - tests/test_single_definition.py
    - tests/test_print_render.py
    - tests/test_veil_audience.py
    - tests/test_veil_scan.py

key-decisions:
  - "CardDeck carries a CardLabels value (Level, Init-Kosten, OPEX, Voraussetzung) next to the cards, so the 13-field MeasureCard stays pinned for 05-04 and the template inserts only model strings"
  - "The legend sample is the first card with a dependency (M1-L3 on the real config), chosen generically so the mini config also gets a sample"
  - "The legend prints the symbolic E-value formula as its last line: a digit right after wA (the next callout number) tripped the weight-symbol veil rule"
  - "Per-position text limit: 134 mm in the upper cells, 126 mm in the lower cells (8 mm footer strip), logged by \\cardreport"
  - "Cut lines are dashed full-length lines through the page centre plus 4 mm solid ticks at the page edges"

patterns-established:
  - "cardsheet starts a new page unless it is the first sheet, so the last page is not flushed early and LastPage stays equal to the sheet count"
  - "Tests that used 'every rendered job is a worksheet' now filter on the angriff- prefix"

requirements-completed: [PRINT-05]

duration: 85min
completed: 2026-10-23
status: complete
---

# Phase 5 Plan 02: Measure Deck Summary

**Measure deck (legend card plus 30 level cards, four A6 cards per A4 sheet, 8 sheets) generated from config through `rules.card_facts`, with the dependency rule defined once in `rules.level_requirements`, compiled by the existing LuaLaTeX pipeline and veil-scanned with the names-only profile.**

## Performance

- **Duration:** about 85 min
- **Completed:** 2026-10-23
- **Tasks:** 2 (both TDD, RED then GREEN)
- **Files:** 4 created, 13 modified

## Accomplishments

- `rules.card_facts(measures, id, level)` returns CIA and k€ costs; `rules.level_requirements(measure, level)` returns the requirements that apply at a level; `_requirements_met` is now built on it. A truth-table test (76 cases) pins that behaviour equals the old loop.
- `planspiel/cards.py` builds 31 cards (legend first, then M1 L1 ... M10 L3): title `M<n> – <name>`, focus, description, plain level text, technical keywords, C/I/A, Init and OPEX in euros with a thousands dot, dependency `M2 ≥ L2` only on M1-L3, M3-L3 and M7-L3 (`M2 ≥ L1` on M7-L3). `MeasureCard` has exactly the 13 pinned fields, with no field for weights, bonus, wave or attack.
- The legend card is an annotated sample (M1-L3) with four numbered callouts (CIA and E-value, Init versus OPEX, lock icon, level colours) and the symbolic formula `E-Wert = C · wC + I · wI + A · wA`; ordinary cards carry no legend text.
- `print/templates/karten.tex.j2` renders the deck with plain variables only; the card macros live in `print/planspiel.sty`. `\lockicon` is a TikZ padlock because Arial has no lock glyph. IN-04 is closed (`\levelbadge` raises a package error for an unknown level).
- `spieler-massnahmenkarten` is in `DOCUMENT_BUILDERS`; the layer-1 and layer-2 veil scans pass on it (names-only profile, D-24); `tikz.sty -> pgf` is probed and `pgf` is in `print/miktex-packages.txt` (package already installed, MiKTeX untouched).
- A config change (M1 L1 Init raised by 1) shows up on the card text with no template change (render test).

## Task Commits

1. Task 1 RED: `7059a71` test(05-02): add failing measure card model tests
2. Task 1 GREEN: `74a6bf7` feat(05-02): add the measure deck print model
3. Task 2 RED: `ff26ca1` test(05-02): add failing measure deck render tests
4. Task 2 GREEN: `4a541cc` feat(05-02): add the card template and register the measure deck

## RED runs (quoted)

Task 1, `uv run pytest tests/test_cards_model.py tests/test_veil_models.py -x -q`:

```
E   ModuleNotFoundError: No module named 'planspiel.cards'
ERROR tests/test_cards_model.py
1 error in 0.17s
```

and `tests/test_veil_models.py::test_prewave_modules_do_not_reference_revealed_data[cards.py]` failed because `planspiel/cards.py` did not exist.

Task 2, `uv run pytest tests/test_cards_render.py -q`:

```
FAILED tests/test_cards_render.py::test_the_real_print_set_holds_the_deck_next_to_the_worksheets
FAILED tests/test_cards_render.py::test_the_mini_config_renders_13_cards - Ke...
...
10 failed, 12 warnings, 8 errors in 0.54s
```

## Verification

- `uv run pytest -q`: 1301 passed, 52 deselected (baseline after 05-01: 1266 passed, 1 skipped; the skip is gone because `PREWAVE_MODULES` now lists `cards.py`).
- `uv run pytest -m pdf -q`: 30 passed (the deck compiles and passes the layer-2 veil, byte-identity and read-guard tests).
- `uv run planspiel texts`: 0 errors, 0 warnings. `uv run planspiel validate`: 0 errors, the one expected 17/7 HandCalcWarning.
- `git status --porcelain final_documents/generated`: empty. The preview was built into `build/preview` only.
- Fit markers from the preview build (log only, not yet asserted): used 153 to 252 pt against limits of 358 to 381 pt, so every card has more than half of its room free; no `Overfull` or `Missing character` in the deck log (only `Underfull \hbox` warnings from justified text). Plan 05-03 owns the layout tuning and the assertions.

## Decisions Made

See `key-decisions` above.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Existing tests assumed every rendered job is an attack worksheet**
- **Found during:** Task 2 (registering the deck made `render_all` return a fourth job).
- **Issue:** `test_print_render.py::test_mini_config_renders_the_wave_without_bonus_measures`, `test_veil_audience.py::test_the_three_real_jobs_are_revealed` and two tests in `test_veil_scan.py` compared the job count or the audience of all jobs with the waves.
- **Fix:** filter on the `angriff-` prefix; the print-set scan test additionally asserts the deck is in the set and the whole set passes layer 1. None of these files are in the plan's `files_modified`.
- **Commit:** `4a541cc`

**2. [Rule 1 - Bug] LastPage said 9 for an 8-sheet deck**
- **Found during:** Task 2 visual check of the preview build.
- **Issue:** `\clearpage` after the last sheet advanced `\thepage` before `\AtEndDocument` wrote the `LastPage` label.
- **Fix:** each `cardsheet` starts with `\clearpage` unless it is the first sheet; nothing is flushed at the end. Footer now reads `Seite 1 von 8`.
- **Commit:** `4a541cc`

**3. [Rule 1 - Bug] Card box and limit were lost after the environment**
- **Found during:** Task 2 first successful compile (`\cardreport` logged `used=0.0pt limit=0.0pt`).
- **Fix:** the body box and the limit dimension are set globally (`\global\setbox ... \hbox\bgroup`) instead of `lrbox`.
- **Commit:** `4a541cc`

**4. [Rule 1 - Bug] Legend tripped its own veil rule**
- **Found during:** Task 2 (`test_scan_documents_returns_nothing_for_todays_print_set`): `veil.weight_symbol 'wA  \n   2'`, the formula was followed by the callout number 2.
- **Fix:** the formula is the last line of the legend card. A short Jinja comment in the template records why.
- **Commit:** `4a541cc`

**5. Test expectation corrected in Task 1.** My first sanity count of the `_requirements_met` truth table was wrong (`> 100`); the exact count is 76 (10 measures times 4 levels, times the 4 levels of the one required measure for M1, M3 and M7). Fixed before the GREEN commit.

## Known Stubs

None.

## Threat Flags

None. T-05-08 (TeX injection) is mitigated by `tex_escape` as `finalize`, the plain-variable lint covering `karten.tex.j2`, and the `Logging \& SIEM/MDR` render test. T-05-09 (disclosure on pre-wave cards) is mitigated by the model having no weight, bonus, wave or attack field, `cards.py` in the pre-wave AST guard, and both veil layers passing. T-05-12 is accepted (`pgf` was already installed).

## Notes for the next plans

- `print --check` reports STALE (`spieler-massnahmenkarten` is not in the committed manifest). That is expected: `final_documents/generated/` is regenerated once at the end of the phase, not per plan.
- 05-03: the cards use only 40 to 70 percent of the available height at 9 pt, so the body can be set larger; the callout 1 dot in the legend sample wraps onto its own line below the C/I/A row; justified text in the plain-text box was fixed with `\raggedright`, other boxes still show `Underfull \hbox`.
- 05-05 adds `event` and `review` branches to `karten.tex.j2` and can reuse `cardsheet`, `cardcell`, `cardreport` and `\cardsheetfooter` unchanged.

## Self-Check: PASSED

- Files exist: `planspiel/cards.py`, `print/templates/karten.tex.j2`, `tests/test_cards_model.py`, `tests/test_cards_render.py`.
- Commits `7059a71`, `74a6bf7`, `ff26ca1`, `4a541cc` are in `git log`.
