---
quick_id: 261125-djw
type: quick
autonomous: true
created: 2026-11-25
---

# Quick 261125-djw: Apply the play-through review and ship print RC8

Work on branch `playthrough-rc8`, which is based on `main` 60ae3e6 (RC7 merged through PR #19).

## Why
A third review played the game by hand with RC7 along the Low reference path. It found no wrong number and no veil breach. It did find 22 points: missing instructions, label mismatches, small boxes and two veil observations. The report is `.planning/quick/261125-ail-proofreading-pass-two-rc7/261125-ail-REVIEW-3.md`. The user decided on 2026-11-25 to apply all of them now as **print RC8**. RC8 supersedes RC7 and the full set is reprinted.

## Decisions
- D-1: Apply every finding at its source (`content/texte.toml`, templates, print models). Keep the decided terminology. Respect the digit lint, the number-word lint and the veil.
- D-2: **The four points that slow the dry run come first:**
  - The print list says "Druckt alles einseitig."
  - The Tracking-Bogen and the "Maßnahmen und Budget" direction tell the teams to fill the Start column: KZ-Start of their tier, Init-Kosten, and Restbudget = Tier-Budget − Init-Kosten.
  - The attack sheets say to enter ±0 when no event card names a KZ effect.
  - Teamheft page 5 sends the teams back to the Tracking-Bogen for KZ final.
  - The Abschluss direction lets the teams keep their Teamheft, has them compute KZ final, and has the facilitator note KZ final and RoS per team in the comparison table. It replaces "Sammelt die Ergebnisse ein".
- D-3: **Veil V1, user decision "Alle Felder offen":** the Tracking-Bogen rows "Event: Budget" and "Event: OPEX" are open in every wave. No grey pattern may reveal which wave has a budget or OPEX event. Add a test for this. Check the pdf fill report still passes. Teams enter 0 or leave the cell empty when there is no event, so add a short hint.
- D-4: **Veil V2, the 620.000 € explanation on the RoS page:** keep it. It names neither an attack nor a single value. List it as "kept" in the SUMMARY.
- D-5: Apply all other findings as suggested in the report, after checking each one against the code:
  - A6: the Budget Review column Restbudget cell.
  - A7: name the story documents.
  - A8: the register Stufe sentence.
  - B1: "im dritten Fall" heading.
  - B2: Recovery line spacing and box width.
  - C1: "KZ Angriff" in step 5.
  - C2: "KZ final" in all three places.
  - C3: the facilitator key labels follow the Tracking-Bogen.
  - C4: one "Schaden" row when Recovery is not allowed.
  - D1: Init-Differenz column wording.
  - D2: Hinweis-Matrix pointer.
  - D3: Was-ist-neu wave minutes in wave order, built from the schedule.
  - E1: reality-check hint on its own line with a wider box.
  - E2: planning Summe row cells.
  - E3: check the tracking cell rule at higher dpi and fix it if it is real.
- D-6: No game value changes:
  - `simulation_config.json`, `rules.py`, `uv.lock` and `pyproject.toml` stay unchanged.
  - Golden files may change only for wording or layout hashes.
  - `planspiel gate` stays unchanged.
  - Page counts stay unchanged unless an extra page is unavoidable and reported.

## Tasks
1. D-2 and D-3. Code and behaviour changes go test-first with a RED commit; wording-only changes update their pinning tests in the same commit.
2. D-5, the same way. Commit the REVIEW-3 report together with the first commit.
3. Run the gates:
   - `validate`, `texts` and `clues` with 0 errors
   - `gate`
   - `pytest -q`
   - commit the inputs, then `print`
   - `print --check` exits 0
   - `pytest -m pdf`
   - a clean stamp
   Render the changed pages to `build/rc8/` and look at them: Teamheft p2, p3, p5; one attack sheet p2; Spielleitungsheft p2 and p3. Then:
   - commit `final_documents/generated/` as `docs(quick-261125-djw): regenerate the complete print set (release candidate 8)`
   - update 07-DRYRUN "Material used" (RC8 supersedes RC7, full reprint, single-sided)
   - write the SUMMARY (status complete) and add a STATE row; current_phase stays 07.
