---
phase: 05-player-facilitator-print-material
plan: 05
subsystem: print
tags: [event-cards, effect-rows, budget-review, tikz, lualatex, equivalence-tests]

requires:
  - phase: 05-player-facilitator-print-material
    provides: card deck model, kind-dispatched karten.tex.j2 and card macros (05-02), approved A6 layout and title guard (05-03), VEIL-04 guard of cards.py (05-04)
provides:
  - spieler-eventkarten.pdf as 2 A4 landscape sheets with 8 A6 landscape cards (7 wave events in play order plus the Budget Review card)
  - planspiel/eventtext.py (EFFECT_KINDS, EffectRow, EventEffect, effect_rows, event_wave) generating every effect line from event type and params
  - review_text.tier_rows (structured Budget Review tiers with inclusive boundaries)
  - cards.EventCard, ReviewCard, EVENT_DECK_JOB, build_event_deck; render.event_cards builder
  - effect kinds window, external_opex, external_budget, kz, review for plans 05-07 and 05-15
  - tests/support/pdf_text.unwrapped_log (TeX wraps log lines at 79 characters)
affects: [05-06, 05-07, 05-15, 05-16]

tech-stack:
  added: []
  patterns:
    - "Every printed effect row carries its exact value and the counts or levels it covers; tests compare it with rules.evaluate_event and rules.budget_review_delta for each covered input"
    - "A framed effect box with an optional caption band (empty label: plain frame) shares one macro with the fact box"

key-files:
  created:
    - planspiel/eventtext.py
    - tests/test_event_text.py
    - tests/test_event_cards.py
    - tests/test_event_cards_pdf.py
  modified:
    - planspiel/review_text.py
    - planspiel/cards.py
    - planspiel/render.py
    - planspiel/texts.py
    - print/planspiel.sty
    - print/templates/karten.tex.j2
    - content/texte.toml
    - tests/fixtures/mini_content/texte.toml
    - tests/support/pdf_text.py
    - tests/test_veil_models.py
    - tests/test_single_definition.py

key-decisions:
  - "Operative Unterstuetzung: user decision \"Text an Regel anpassen\" (2026-10-26): the rule text now reads \"Zählt für jede Maßnahme, die in dieser Welle aktiv ist.\"; rules and simulation unchanged"
  - "Event cards carry no caption band over the effect box; the Kurswechsel card overflowed its cell by 15 pt with one, and no type size was reduced"
  - "Event and review card ids use hyphens (oem-audit) because the id is written to the TeX log"
  - "The Budget Review card prints the tier rows and one overspend line; the full penalty lookup stays out (team booklet, 05-06)"

patterns-established:
  - "Effect rows are generated per event type in eventtext.py; a new event type without an EFFECT_KINDS entry is a PrintModelError, never a silent empty card"
  - "Log parsing for long ids goes through tests.support.pdf_text.unwrapped_log"

requirements-completed: [PRINT-06]

duration: ~30 min active (08:2x to 08:5x on 2026-10-26)
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 05: Event deck Summary

**Seven wave event cards and the Budget Review card build on two A4 sheets in the approved card layout, every effect line is generated from the event type and params and proven equal to the simulation for each input it covers.**

## Performance

- **Duration:** about 30 minutes
- **Tasks:** 2 (both auto, TDD) plus the user-decided wording fix as its own commit
- **Files modified:** 15 (4 created, 11 modified)

## Accomplishments

- `eventtext.effect_rows` produces the printed effect for all eight event types. Numbers come from event params, `rules.penalty_params`, `rules.kurswechsel_wave` and `rules._tier_lookup`; words come from `[sheets.eventkarten]` (digit-free) and the event's own text subtree through `PreAttackView`.
- Checklist rows merge adjacent counts with equal KZ (`2–3 erfüllt → KZ ±0`); the covered counts are exactly `0..n`, each once. Level tiers, the level-3 bonus, the and-condition (true and each falsifying case), the flat budget cut and the OPEX discount per active measure equal `rules.evaluate_event`. The Budget Review tiers equal `rules.budget_review_delta` at each boundary, one euro below it and below zero.
- `review_text.tier_rows([[0,0],[25,5],[50,10],[75,15]]) == [(0, 24999, 0), (25000, 49999, 5), (50000, 74999, 10), (75000, None, 15)]`, registered in the single-definition guard.
- `build_event_deck`: 8 cards in play order, header `Event: Nach Welle N` with N from the `cfg.events` key, 2 sheets of 4. `cards.py` still passes the VEIL-04 AST scan (no `.waves`/`.attacks`); `eventtext.py` is in `PREWAVE_MODULES`.
- `spieler-eventkarten` is classified `spieler-` (pre-wave, story veil profile) and passes the layer-1 and PDF veil scans; no duplex backs.
- A budget cut changed to -30 renders `Gesamtbudget −30.000 €` without a template change.

## Task Commits

0. **Wording fix (user decision): align the Operative Unterstuetzung rule text** - `069f011` (fix, text only)
1. **Task 1 RED: failing event effect row tests** - `911b5e7` (test)
2. **Task 1 GREEN: effect rows from type and parameters** - `cfeea68` (feat)
3. **Task 2 RED: failing event deck tests** - `7c976f3` (test)
4. **Task 2 GREEN: event and Budget Review cards** - `68c0853` (feat)

Plan metadata: see the docs commit that adds this SUMMARY.

## RED runs

- **Task 1 (`911b5e7`):** collection error `ModuleNotFoundError: No module named 'planspiel.eventtext'` (the module and the `PREWAVE_MODULES` entry did not exist). After GREEN the first run had 4 failures in two tests (`KeyError: 0`: the tier labels are keyed by the TOML strings, the code and one test looked them up by integer); fixed to `labels[str(level)]`. Final: 43 new tests pass (`tests/test_event_text.py`).
- **Task 2 (`7c976f3`):** collection error `ImportError: cannot import name 'EVENT_DECK_JOB' from 'planspiel.cards'` for `tests/test_event_cards.py` and `tests/test_event_cards_pdf.py`. After GREEN: `tests/test_event_cards.py` 28 passed (one test of mine asserted that the tex contains no "back", which tripped on "Backup"; replaced by a no-`\clearpage` assertion); the PDF title test first failed because TeX wraps log lines at 79 characters and splits `PLANSPIEL-CARDTITLE id=operative-unterstuetzung ...`; fixed with `unwrapped_log`.

## Operative Unterstuetzung wording (user decision)

The plan flagged that the rule text said "Zählt für jede bestehende Maßnahme in der kommenden Runde" while `rules.evaluate_event` counts the measures active in the event's own wave. The user decided: **"Text an Regel anpassen"** (2026-10-26). `events.operative_unterstuetzung.rule` in `content/texte.toml` and the mini fixture now read "Zählt für jede Maßnahme, die in dieser Welle aktiv ist." (digit-free, no giveaway term; `uv run planspiel texts` stays at 0 errors). Rules and simulation are untouched. No golden or characterization test pinned the old text, so no regeneration was needed. The card prints this rule directly above the generated line `OPEX −2.000 € je aktiver Maßnahme`; a test pins that order.

## Final used/limit table (8 cards)

Source: `build/print-0505/spieler-eventkarten.log`, `PLANSPIEL-CARD` lines. Heights are `ht+dp` in pt; the limit is the cell height minus the 7 mm safe margins (and the 8 mm footer strip in the lower row). 0 Overfull boxes, no missing glyph.

| Card | cell | used (pt) | limit (pt) | fill |
|------|------|-----------|------------|------|
| kurswechsel | upper left | 254.3 | 258.9 | 98% |
| operative-unterstuetzung | upper right | 146.2 | 258.9 | 56% |
| sparprogramm | lower left | 141.3 | 236.2 | 60% |
| oem-audit | lower right | 215.0 | 236.2 | 91% |
| kritische-schwachstelle | upper left | 176.5 | 258.9 | 68% |
| exzellenz-bonus | upper right | 116.3 | 258.9 | 45% |
| nervige-authentifizierung | lower left | 145.3 | 236.2 | 62% |
| budget-review | lower right | 211.9 | 236.2 | 90% |

Title guard (`PLANSPIEL-CARDTITLE`, 8 markers): every title is on one line; the widest is "Kritische Schwachstelle im System" at 284.4 pt of 365.3 pt available.

## Visual inspection

PNG renders (110 dpi, `pdftoppm`) of the preview `build/preview-0505/spieler-eventkarten.pdf`, not written to `final_documents/generated`:

- `C:\Users\Claudio\Documents\Git\security_game\security-planspiel\build\png\events-0505-1.png`, sheet 1: Kurswechsel (kicker `Event: Nach Welle 1`, narrative in accent blue, the long rule in small grey type, one effect line in a frame), Operative Unterstützung (rule line plus `OPEX −2.000 € je aktiver Maßnahme`), Sparprogramm (`Gesamtbudget −20.000 €`), OEM-Audit (checklist heading naming M1, M2, M4, M5, M7 with their names and the minimum level, then five rows `0 erfüllt → KZ −15` to `5 erfüllt → KZ +15` with `2–3 erfüllt → KZ ±0` merged). Stamp and `Seite 1 von 2` in the footer.
- `...\build\png\events-0505-2.png`, sheet 2: Kritische Schwachstelle (heading `Level der Maßnahme M7 – ...`, four level rows), Exzellenz-Bonus (`Je Maßnahme auf Level 3: KZ +5`), Nervige Authentifizierung (`Wenn M1 ... und M6 ...: KZ −10`, `Sonst: KZ ±0`), Budget Review (kicker `Event: Zum Abschluss`, caption band `Restbudget am Ende`, the four tier rows, bold `Überzogen: −9 KZ je angefangene 10.000 €`). Footer `Seite 2 von 2`.
- Many cards are half empty; none is crowded except the Kurswechsel card (98%).

## Decisions Made

See key-decisions in the frontmatter. Additional points:

- Effect kinds: `kurswechsel` window; `opex_discount_per_active_measure` external_opex; `flat_budget` external_budget; `checklist_tier`, `measure_level_tier`, `level_bonus_per_measure`, `and_condition` kz; `final_budget_tier` review. External kinds change the budget but not the RoS (`rules.security_spend`, RULE-06).
- The and-condition prints a second row `Sonst: KZ ±0` so the false case is on the card; row 1 and row 2 each equal the simulation.
- The review effect is one `EventEffect`: tier rows first, the overspend row last; the card splits them into `tier_lines` and `overspend_line`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The event card needs a header without a level badge, and a kicker line**
- **Found during:** Task 2 GREEN
- **Issue:** `\cardheader` always set `\levelbadge{#4}`; an event has no level (level 0 would print "0").
- **Fix:** `\cardheader` now takes the badge as material (`{\levelbadge{N}}` from the measure template, empty for events) and a sixth argument for the kicker line above the title. Measure and legend cards render as before (all 31 title markers and the measure PDF tests pass unchanged). The one-line title guard covers the event titles (8 `PLANSPIEL-CARDTITLE` markers).
- **Files modified:** print/planspiel.sty, print/templates/karten.tex.j2
- **Commit:** 68c0853

**2. [Rule 1 - Bug] Kurswechsel card overflowed its cell by 15 pt**
- **Found during:** Task 2 GREEN (first PDF build: used 274.1 pt, limit 258.9 pt)
- **Issue:** narrative (about 245 characters) plus the 750-character rule plus a captioned effect box did not fit the upper cell.
- **Fix:** the effect box of an event card has no caption band (`\effectbox{}` skips the band when the label is empty), saving about 19 pt: 254.3 pt, 98%. No type size was reduced and no text was shortened; plan fallbacks (a) narrative 8.5 pt and (b) rule 8 pt were not applied. The Budget Review card keeps its caption band (`Restbudget am Ende`). This is a layout judgement for the print test of the phase, not a type change.
- **Files modified:** print/planspiel.sty, print/templates/karten.tex.j2, planspiel/cards.py (the `effect_label` field was dropped again)
- **Commit:** 68c0853

**3. [Rule 1 - Bug] TeX log lines are wrapped at 79 characters**
- **Found during:** Task 2 GREEN (PDF title test)
- **Issue:** `PLANSPIEL-CARDTITLE id=operative-unterstuetzung width=... avail=365.333` is cut, so the regex missed the card.
- **Fix:** `tests/support/pdf_text.unwrapped_log` joins lines of exactly 79 characters; the event PDF tests read the log through it. The measure deck test is unchanged (its ids are short).
- **Commit:** 68c0853

**4. Judgement: card ids use hyphens**
- `card_id` is `event.id` with underscores replaced by hyphens (`oem-audit`), because `\typeout` of an escaped underscore does not round-trip in the log.

**Total deviations:** 3 auto-fixed, 1 judgement. No impact on scope.

## Issues Encountered

- A `\vspace` directly after `\cardheader` (horizontal mode) was deferred until after the first narrative line; fixed with `\par` after the header, which leaves the measured heights unchanged.
- A row text starting a line after `\par` ran together (`\parLevel`) and `\bfseries` followed by a capital umlaut ran together; fixed with `\par{}` and `\bfseries{}` in the template.

## Verification

- `uv run pytest -q`: 1392 passed, 82 deselected (baseline 1321 plus 71 new).
- `uv run pytest -m pdf -q`: 60 passed (baseline 54 plus 6 new).
- `uv run planspiel texts`: 0 Fehler, 0 Warnung(en). `uv run planspiel validate`: 0 Fehler, 1 Warnung (the existing KZ slope 17/7 hand-calculation warning).
- `git status --porcelain final_documents/generated`: empty.

## Human check pending (end-of-phase)

Print `build/preview-0505/spieler-eventkarten.pdf` (both sheets) single-sided in colour at 100 %, cut the cards, and read the Kurswechsel, OEM-Audit and Budget Review cards aloud as a facilitator would. Points to look at: the Kurswechsel card is at 98% of its cell; event cards have no caption band over the effect box (a layout choice made to keep the type size).

## Known Stubs

None.

## Threat Flags

None. The new printed text is digit-free wording from `[sheets.eventkarten]` passing `tex_escape`, the digit lint, `uv run planspiel texts` and the story-profile veil scans (T-05-17 to T-05-20 mitigated as planned: equivalence tests per covered input, giveaway lint and veil scan, `tex_escape`, `PrintModelError` for an unknown type).

## Next Phase Readiness

- 05-06 (team booklet) can reuse `review_text.tier_rows` and the full penalty table via `penalty_rows`; 05-07 and 05-15 can read `eventtext.EFFECT_KINDS` and `effect_rows`.
- `\effectbox`, `\cardheader`'s kicker argument and `unwrapped_log` are available to later card or sheet documents.
- No blockers.

## Self-Check: PASSED

- Files: planspiel/eventtext.py, tests/test_event_text.py, tests/test_event_cards.py, tests/test_event_cards_pdf.py exist; `tier_rows` in planspiel/review_text.py; `build_event_deck` in planspiel/cards.py; `def event_cards(` in planspiel/render.py.
- Commits 069f011, 911b5e7, cfeea68, 7c976f3, 68c0853 exist in `git log`.
