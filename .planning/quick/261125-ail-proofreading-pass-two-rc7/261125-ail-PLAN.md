---
quick_id: 261125-ail
type: quick
autonomous: true
created: 2026-11-25
---

# Quick 261125-ail: Apply proofreading pass 2 and ship print RC7

Branch `overspend-table-rc5` (PR #18), on top of RC6 (quick 261125-0f4, print commit e1a94ec, stamp "Stand 2026-11-25 · 95ed03c").

## Why
A second independent proofreading pass over RC6 found 54 points: 13 that break play, 8 pass-1 fixes that went wrong, 10 terminology leftovers, 19 language points and 4 layout points. Report: `.planning/quick/261125-0f4-budget-review-off-teamheft-and-drop-gesa/261125-0f4-PROOFREAD-2.md`. The user decided on 2026-11-25 ("Alles jetzt"): apply all 54 before the dry run and ship them as **print RC7**. RC7 supersedes RC6, and the user reprints the full set.

## Decisions
- D-1: Apply every finding at its source (`content/texte.toml`, `content/clues.toml`, templates, print models). Keep the terminology decided in 261125-0f4. Respect the digit lint (add a digit string such as "0" to `content/digit_allowlist.toml` only where the report needs it, e.g. "Level 0"), the number-word lint and the veil.
- D-2: **Play-breakers (A):**
  - The Abschluss direction hands out the Budget Review card and puts the RoS page before the Budget Review.
  - The print list says to cut the measure and event cards and sort the event cards by wave; the Budget Review card goes out only at the Abschluss.
  - The RoS page carry hint names the Tracking-Bogen rows.
  - Δ Init is defined as the Init of the new level minus the old one, and the full Init for a new measure. Check against `rules.window_cost`. This goes on the tracking page, the card legend and the Welle page.
  - The Übung prints the practice budget and the KZ start from config, through code.
  - The Teamheft invites teams to ask the Geschäftsführung.
  - The exfil sheet states that it has no Recovery. Phrase it generically from config (`allow_recovery`), not hard-coded per attack.
  - The planning page relates the planned costs to the Tier-Budget without revealing the review values, and gets an optional tier field.
  - The RoS precision hint.
  - Page 5 names its sources and the cross-check.
  - The Übung event order or a note.
  - The clue-matrix section names match the printed documents.
  - The clue-weight legend.
- D-3: **Layout (E):**
  - The Teamheft computed rows get value cells, and "Summe der Schäden" and "Vermiedener Schaden" are separated.
  - The clinic example rows carry no W1 label.
  - The Übung amount format and the spacing.
  - The Spielleitungsheft contents get page numbers, and the Übung key moves before Angriff 1.
  - Every document must keep its page count unless the extra page is unavoidable and reported. The fill reports and pdf tests decide.
- D-4: Verify every suggestion against the rules code before applying it. Examples: whether "KZ-Steigung je GR-Punkt × 2" really means a slope of +2, and the Sparprogramm "letzte Welle" wording against the config's wave order. A suggestion that is wrong against the code is skipped and listed in the SUMMARY with the reason.
- D-5: No game value changes. `simulation_config.json` unchanged; `rules.py`, `tests/golden` (except worksheet/text goldens that pin wording), `uv.lock`, `pyproject.toml` unchanged; `planspiel gate` unchanged.

## Tasks
1. Apply the A and B findings. Code changes are test-first (RED commit); pure wording changes update the pinning tests in the same commit.
2. Apply the C, D and E findings, the same way.
3. Gates: `validate`/`texts`/`clues` must show 0 errors, `gate`, `pytest -q`. Commit the inputs, then `print`, `print --check` (exit 0), `pytest -m pdf`. The stamp must be clean. Render the changed pages to `build/rc7/` and look at them. Commit `final_documents/generated/` as `docs(quick-261125-ail): regenerate the complete print set (release candidate 7)`. Update the `07-DRYRUN.md` "Material used" section (RC7 supersedes RC6, full reprint), write the SUMMARY (status complete) and add a STATE row.
