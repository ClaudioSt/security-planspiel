---
phase: 05-player-facilitator-print-material
plan: 04
subsystem: print
tags: [veil, cards, legend, pdf-tests, information-boundary]

requires:
  - phase: 05-player-facilitator-print-material
    provides: MeasureCard/LegendCard model and karten.tex.j2 (05-02), built and laid out deck (05-03), veil scan module (05-01)
provides:
  - LegendCard.reveal_note and text key sheets.karten.legend_reveal (digit-free sentence printed in the legend)
  - tests/test_veil_cards.py (20 default-suite tests: pinned MeasureCard field set, AST scan of cards.py with self-tests, model and .tex negatives, D-24 profile documentation)
  - tests/test_veil_cards_pdf.py (13 pdf tests: deck negatives, positives on the three revealed worksheets)
affects: [05-05, 05-16]

tech-stack:
  added: []
  patterns:
    - "The information boundary is proven on three layers: model (field set, AST scan), .tex (names-only profile, weights, symbols) and PDF (squashed, hyphen-free text)"
    - "Expectations for pdf tests are built from the model and the veil context, never typed numbers"

key-files:
  created:
    - tests/test_veil_cards.py
    - tests/test_veil_cards_pdf.py
  modified:
    - planspiel/cards.py
    - planspiel/texts.py
    - print/templates/karten.tex.j2
    - content/texte.toml
    - tests/fixtures/mini_content/texte.toml

key-decisions:
  - "Reveal note sits in the legend between the numbered callouts and the formula; the formula stays the last line"
  - "The deck keeps the names-only veil profile; a test documents that the story profile would flag only phishing (M6 defence term, D-24)"
  - "Task 2 tests needed no source fix: the deck and the Phase 4 worksheets already had the right shape, the tests are the permanent proof"

patterns-established:
  - "AST scan of a pre-wave builder module for wave, attack and bonus access, with a parametrised self-test that each forbidden form is reported"

requirements-completed: [VEIL-04]

duration: ~30 min
completed: 2026-10-25
status: complete
---

# Phase 5 Plan 04: Measure card information boundary (VEIL-04) Summary

**The measure card model is pinned to descriptive text, CIA values, costs and dependencies, the legend says where weights and bonus come from, and 33 new tests prove that weights and bonus links appear on the three revealed worksheets and nowhere in the deck.**

## Performance

- **Duration:** about 30 min
- **Tasks:** 2 (both auto, TDD)
- **Files modified:** 7 (2 tests created, 5 source/content files changed)

## Accomplishments

- `MeasureCard` field set pinned by an exact-equality test; an AST scan of `planspiel/cards.py` rejects any access to `waves`, `attacks`, `bonus_measures`, `bonus_rows`, `bonus_reasons`, `weights`, the reveal views, `worksheet_constants` and `build_attack_sheets`, with a self-test for six forbidden forms.
- No measure card string (mini and real) contains a bonus reason, a revealed attack name, a veiled title `Angriff N`, a wave reference `Welle <digit>`, the bonus label or a weight triple; a hit-finder self-test proves each kind of leak is detected.
- Legend card gets `reveal_note`: "Wie stark C, I und A in einer Welle zählen (wC, wI, wA) und welche Maßnahmen gegen den Angriff einen Bonus bringen, erfahrt ihr erst mit dem Angriffsblatt der Welle." No digit, no measure id, no attack name.
- Rendered deck `.tex` passes the names-only profile (plain and squashed), the revealed-text check, the weight check and the weight-symbol check; the story profile returns exactly `["phishing"]`, which documents D-24.
- PDF proof: the deck PDF carries no weight triple, bonus reason, revealed text, attack name or veiled title and contains the reveal note; each worksheet PDF has `weight_hits == [N]`, every bonus table row (measure label, signed points, reason) and every part of the E-value line on page 1.

## Task Commits

1. **Task 1 RED: failing measure card veil tests** - `6d0046c` (test)
2. **Task 1 GREEN: pin the card shape, add the legend reveal note** - `ff15d16` (feat)
3. **Task 2: PDF proof of the deck and worksheet boundary** - `e447b3f` (test)

Plan metadata: see the docs commit that adds this SUMMARY.

## RED run (Task 1, `6d0046c`)

`4 failed, 16 passed`. The four failures were exactly the reveal-note tests: `AttributeError: 'LegendCard' object has no attribute 'reveal_note'` (model test for mini and real, wording test, rendered-legend test). The 16 passing tests were the negatives and the field-set and AST pins, which pass on the existing 05-02/05-03 shape by design (they pin it).

## Task 2 outcome

All 13 pdf tests passed on the first run (`uv run pytest -m pdf tests/test_veil_cards_pdf.py -v`: 13 passed, none skipped, 3 parametrised cases per worksheet test). Plans 05-02, 05-03 and Phase 4 had already built the shapes correctly, so no RED commit with an inverted assertion and no source fix was needed; the tests are the permanent proof. The positive worksheet tests double as negative controls for the matching helpers (the same hyphen-free squashed comparison finds the bonus reasons on the worksheets and finds none on the deck).

## Legend layout

The note was added to the right column of the legend; the left column (annotated sample) is the taller one, so the legend height is unchanged: `PLANSPIEL-CARD id=LEGEND used=252.8pt limit=258.9pt` (98%), 0 Overfull boxes. Visual check of `build/png/karten-0504-1.png` (from `build/preview-0504`, not `final_documents/generated`): note in small grey italic under callout 4, formula still last.

## Verification

- `uv run pytest -q`: 1321 passed, 76 deselected (baseline 1301 plus 20 new).
- `uv run pytest -m pdf -q`: 54 passed (baseline 41 plus 13 new).
- `uv run planspiel texts`: 0 Fehler, 0 Warnung(en).
- `git status --porcelain final_documents/generated`: empty.

## Decisions Made

See key-decisions in the frontmatter. `content/giveaway_terms.toml` and `measures.M6.*` were not touched.

## Deviations from Plan

None - plan executed exactly as written. The "wording question" flagged by the orchestrator ("Operative Unterstützung") did not arise in this plan's scope; no decision was left open.

## Issues Encountered

None.

## Known Stubs

None.

## Threat Flags

None. The only new printed text is a static, digit-free sentence passing `tex_escape`, the digit lint and `uv run planspiel texts`.

## Next Phase Readiness

- 05-05 (event deck) extends `content/texte.toml`, the mini texte, `texts.py` and `karten.tex.j2` next; `PREWAVE_MODULES` in `tests/test_veil_models.py` already covers `cards.py`.
- No blockers.

## Self-Check: PASSED

- Files: tests/test_veil_cards.py, tests/test_veil_cards_pdf.py, planspiel/cards.py (contains `reveal_note`), content/texte.toml and tests/fixtures/mini_content/texte.toml (contain `legend_reveal`) exist.
- Commits 6d0046c, ff15d16, e447b3f exist in `git log`.
