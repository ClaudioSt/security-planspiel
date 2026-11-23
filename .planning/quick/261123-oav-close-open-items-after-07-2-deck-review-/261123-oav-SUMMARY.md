---
phase: quick-261123-oav
plan: 261123-oav
subsystem: intro-deck, validator, tests
tags: [deck, validator, tdd, leg-02, prot-01, prot-05]
requires: [07.2 RC4]
provides:
  - 38-slide intro deck with the Übungswelle slide 33 and correct slide-number fields
  - risk.case_goal_coverage validator rule (07.2 D-12)
affects: [07-12 dry run materials]
tech-stack:
  added: []
  patterns: [surgical zip patch on a copy, mutation check for a test that cannot be RED]
key-files:
  created:
    - .planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-DECK-CHECKLIST.md
  modified:
    - tests/test_booklet_model.py
    - tests/test_risk_matrix_config.py
    - tests/test_intro_deck.py
    - planspiel/validate.py
    - README.md
    - .planning/codebase/CONCERNS.md
    - content/INVENTORY.md
    - "final_documents/Planspiel_Einführung + Grundlagen.pptx"
decisions:
  - "Slide 22 renamed to Schutzbedarf and shown (user answer Einblenden, 2026-11-23); pinned in the deck test"
  - "Slide 21 keeps its likelihood x damage matrix (general method) and gets one bridge line"
  - "risk.case_goal_coverage is a validator error, not a warning"
metrics:
  completed: 2026-11-23
status: complete
---

# Quick 261123-oav: Close the open items after phase 07.2 Summary

Intro deck finished (new Übungswelle slide 33, slide 31 asks for the damage per protection goal, slide 21 bridge line, slide 22 shown as Schutzbedarf, slide-number caches fixed) and the review warnings WR-01 and WR-02 closed, with the RC4 print set still current.

## Commits

| Commit | Message |
|--------|---------|
| cbfa0a2 | test(quick-261123-oav): pin gesamt when the highest band is not the first rating (WR-01) |
| 4334a9a | test(quick-261123-oav): a protection goal without a business case fails validation (WR-02, RED) |
| 84ab11e | fix(quick-261123-oav): require a business case for each protection goal (WR-02, D-12) |
| 8b2b0ae | docs(quick-261123-oav): CONCERNS quotes the 215-minute session |
| d0708d3 | docs(quick-261123-oav): intro deck checklist for the open 07.2 deck items |
| 6719283 | test(quick-261123-oav): pin the Übungswelle slide, the slide 21/22/31 texts and the slide-number fields (RED) |
| 3a9e2b0 | docs(quick-261123-oav): intro deck with the Übungswelle slide and correct slide numbers |

## Task 1: WR-01, WR-02, CONCERNS

- WR-01: `test_the_need_example_total_is_the_highest_band_wherever_it_sits` with three literal cases (gering/hoch/mittel to hoch, mittel/gering/hoch to hoch, gering/mittel/gering to mittel). The implementation in `planspiel/booklet.py` was already right, so the test cannot be RED; its power was proven by mutation, never committed:
  1. `highest = rated[0]` (first rating): 3 of 3 cases failed.
  2. `highest = max(rated)` (lexicographic maximum): 2 of 3 failed (highest-in-the-middle, highest-last), the third passes by construction.
  3. File restored, `git diff --quiet planspiel/booklet.py` clean; all 6 need-example tests green.
- WR-02: RED commit first (2 candidate cases failed: data_trust removed, data_trust retagged to c; shipped-config test passed), then GREEN: `check_risk_cases` collects the goals of all cases and reports one `risk.case_goal_coverage` error on `risk_matrix.cases` naming the missing goals. README states the rule. The redundant `any(case.goal == "i")` and the duplicated set assertion were removed. `uv run planspiel validate`: 0 errors, 0 warnings.
- CONCERNS.md: the three 195-minute figures now say 215 and cite `session_schedule.total_minutes`.

## Task 2 and 3: deck

Checklist: `.planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-DECK-CHECKLIST.md` (extracted texts, rows 1 to 7, approval, result review).

RED: `tests/test_intro_deck.py` retargeted to 38 slides, 19 of 37 tests failed by assertion on the committed 37-slide deck, none at collection. GREEN: the patched copy passed all 37 on `PLANSPIEL_DECK` before it replaced the committed file; the committed deck passes 37/37 plus `tests/test_inventory.py`.

### Zip comparison (old to new)

- Entries 522 to 524; `[Content_Types].xml` first; original order kept; all entries deflated; `testzip` clean.
- Changed (9): `[Content_Types].xml`, `ppt/presentation.xml`, `ppt/_rels/presentation.xml.rels`, `ppt/slides/slide21.xml`, `slide22.xml`, `slide31.xml`, `slide32.xml`, `slide34.xml`, `slide35.xml`.
- Added (2): `ppt/slides/slide38.xml`, `ppt/slides/_rels/slide38.xml.rels`. Removed: none.
- `docProps/app.xml` CRC 63C77E31 before and after.

### Slide-text diff (python-pptx, all slides)

Only slides 21 (bridge line added), 22 (title Schutzbedarf, show="0" removed), 31 (Risikobeurteilung text) and the new slide 33 differ; the cached slide numbers of old 33, 35 and 36 now equal their position.

### Renders

PowerPoint COM export, 1920 x 1080, no POWERPNT process left afterwards. Under `C:\Users\Claudio\Documents\Git\security_game\security-planspiel\build\deck\quick-261123-oav\renders\` (gitignored):

- `slide-21.png`, `slide-22.png`, `slide-28.png`, `slide-31.png`, `slide-32.png`, `slide-33.png`, `slide-34.png`, `slide-36.png`, `slide-37.png` (patched deck, positions after the insertion)
- `committed-old-slide-33.png` (committed deck before the change, old Budget slide)

Findings: no overlaps, footers show 33, 34, 36. PowerPoint recomputes the slide-number field when it renders: the committed deck already displayed the correct 33 on the old Budget slide, so the stale cache (32, 34, 35) was visible only to tools that read the cached text, not in PowerPoint.

## Final gates

| Gate | Result |
|------|--------|
| `uv run planspiel validate` | 0 errors, 0 warnings |
| `uv run planspiel texts` | 0 errors, 0 warnings |
| `uv run planspiel print --check` | exit 0, "Druckmaterial aktuell: Stand 2026-11-22 · 7420259 (15 Dokument(e))" |
| `uv run pytest -q` | 3088 passed, 3 skipped, 0 failed, 0 xfailed (3 min 41 s) |

## Deviations from Plan

None. The user's decision for slide 22 (Einblenden) resolved the plan's open question; the plan's conditional branch (remove `show`, pin visibility in the test) was applied.

## Open for the user

- Slide 21 bridge line placement and wording, slide 31 Risikobeurteilung wording, slide 33 Übungswelle text, material and 15 min: look at the renders.
- `docProps/app.xml` still lists 37 slides and the old titles; PowerPoint rewrites it on the next save.

## Known Stubs

None.

## Threat Flags

None. Threat T-oav-01 (veil): all deck veil tests green on every slide; no attack name, no amount on the new text. T-oav-05: `print --check` exit 0.

## Self-Check: PASSED

- Files present: DECK-CHECKLIST.md, the 38-slide deck (`git show --stat HEAD~0` of 3a9e2b0), INVENTORY.md row with "38 slides", renders on disk.
- Commits cbfa0a2, 4334a9a, 84ab11e, 8b2b0ae, d0708d3, 6719283, 3a9e2b0 exist; RED commits precede the validator GREEN and the deck commit.
- `git log -- "final_documents/Planspiel_Einführung + Grundlagen.pptx"` shows exactly one quick-task commit (3a9e2b0) on top of b550f8b.

## Follow-up (2026-11-23): slide 22 questions

After the review of the renders the user asked to correct slide 22 ("Korrigiere"): its five generic security-requirement questions did not match the new title "Schutzbedarf". They now lead through the method, one run text each, icons and layout unchanged:

1. Welche Werte braucht das Unternehmen: Daten, Anlagen, Know-how?
2. Wie groß wäre der Schaden fürs Geschäft: gering, mittel oder hoch?
3. Was wäre schlimmer: bekannt (C), verfälscht (I) oder nicht verfügbar (A)?
4. Welcher Schaden ist der höchste? Er bestimmt den Schutzbedarf des Werts.
5. Verlangen Gesetze (z.B. DSGVO) oder Kunden (z.B. OEM-Audit) mehr Schutz?

RED test 0628edd pins the questions in order; the deck test and inventory test pass (49), `print --check` exit 0. python-pptx renumbered the slide part names on save (same 524 entries, slide content unchanged apart from slide 22). Render: `build/deck/quick-261123-oav/renders/slide-22-v2.png`.
