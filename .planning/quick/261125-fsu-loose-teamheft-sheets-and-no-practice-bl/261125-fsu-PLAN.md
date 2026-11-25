---
quick_id: 261125-fsu
type: quick
autonomous: true
created: 2026-11-25
---

# Quick 261125-fsu: No joint practice wave, Teamheft as loose sheets (print RC9)

Branch `teamheft-loose-sheets` (PR #21, open). It is based on `main` with RC8 (stamp "Stand 2026-11-25 · 018111b") and already holds the slide-31 change (c77b80a).

## Why (user, 2026-11-25)
1. **Practice wave:** "Das obere Kästchen raus. Wir geben das Blatt als Hilfe aus, rechnen es aber nicht gemeinsam durch."
   - The box is `practice.intro` on page 1 of `uebung-welle-0.pdf`.
   - The user chose "Block streichen, Blatt als Hilfe". The 15-minute `wave_0` block leaves `session_schedule`, and the session total drops from 215 to 200 minutes.
   - The practice sheet is still printed and handed out as a reference aid. It goes out with "So funktioniert eine Welle" in the "Maßnahmen und Budget" block.
2. **Teamheft as loose sheets:** the Teamheft is not handed out as one booklet. Its pages are handed out per block. The user chose "Ja, mit in RC9":
   - Story-Gruppenarbeit: page 1, Schutzbedarf und Risikoregister.
   - Maßnahmen und Budget: page 2, Budget und Planung, and page 3, Tracking-Bogen. The Start column is filled in this block.
   - Abschluss: pages 4 and 5, Return on Security and Budget Review, together with the Budget Review event card.

## Decisions
- D-1 (config → README → texts → print): remove the `wave_0` block from `simulation_config.json` `session_schedule.blocks` and set `total_minutes` to 200. Keep the `practice` block, because the sheet still uses it.
  - Check the validator: it sums the blocks, and some rule may require a wave-0 block.
  - Check `planspiel/schedule.py`, `probelauf.py`, `was_neu.py` and the deck test. They derive minutes, clock times and the phase list from the schedule.
  - Update every pinned minute figure test-first. The "Was ist neu" sheet shows the new total and that the practice wave is now a handout.
  - README: the flow steps, the 215-minute mentions and the description of `uebung-welle-0.pdf` (reference sheet, not a joint calculation).
  - `.planning/codebase/CONCERNS.md`: the 215 mentions become 200.
- D-2: `practice.intro` goes completely: the template box, the text key and the model field. If one sentence is needed so the sheet stands alone, say "Beispiel, zählt nicht für die Wertung" in the sheet title or subtitle, not in a box. Executor decides; keep it minimal. The sheet otherwise stays as in RC8.
- D-3: Spielleitungsheft Ablaufplan:
  - The `wave_0` block direction goes.
  - The `measures_budget` direction hands out the measure cards, Teamheft pages 2 and 3, the Übungsblatt and "So funktioniert eine Welle" as aids.
  - `story_groups` hands out Teamheft page 1 instead of "das Teamheft".
  - `closing` hands out Teamheft pages 4 and 5 with the event card. Its sentence "die Teamhefte bleiben bei den Teams" becomes "die Blätter bleiben bei den Teams".
  - The print list notes that the Teamheft is printed per team and not stapled, because its pages are handed out per block. Page numbers come from code, not prose digits.
  - Check every other text that says "Teamheft" as a whole booklet handed out at once: player and facilitator documents, plus the debrief "legt ihr Teamheft bereit".
  - Cross-references like "Seite 5" and "Tracking-Bogen" stay, because each page has its title.
- D-4: Intro deck `final_documents/Planspiel_Einführung + Grundlagen.pptx`. Use python-pptx with run-text edits and keep the formatting, as in the earlier quick tasks.
  - Slide 33 "Übungswelle": delete the slide. Its block no longer exists.
  - Slide 28 "SPIELPHASEN": remove the Übungswelle phase and renumber the remaining phases. If the slide is a graphic that cannot be edited cleanly, report it instead of breaking the layout.
  - Slide 34, Budget, which becomes slide 33: the material line names Teamheft pages 2 and 3 by their sheet titles, the Maßnahmenkarten, the Übungsblatt and "So funktioniert eine Welle". Use the labels the print list uses.
  - Slide 37, Abschluss, which becomes slide 36: the material line names the RoS and Budget Review sheets and the event card Budget Review.
  - Slide 36, Wellen: drop "So funktioniert eine Welle" from its material line if it is now handed out earlier, or keep it if the user's flow needs it again. Keep it, since it is the same sheet the teams already hold.
  - Minute figures stay pinned against the config.
  - Fix the slide-number caches after the deletion.
  - Update `tests/test_intro_deck.py` test-first: slide count 37, MATERIAL maps, PRACTICE_SLIDE pins removed.
  - Render the changed slides with PowerPoint COM to `build/deck/rc9/` and look at them.
- D-5: No game value changes. `rules.py`, `uv.lock`, `pyproject.toml` and the attack and wave values stay unchanged. Only `session_schedule` changes in the config. `planspiel gate` must stay unchanged.

## Tasks
1. D-1 and D-2. Code and behaviour changes are test-first (RED commit). Wording-only changes update their pins in the same commit.
2. D-3 and D-4.
3. Gates:
   - `validate`, `texts` and `clues` with 0 errors, `gate`, `pytest -q`.
   - Commit the inputs, then `print`.
   - `print --check` must exit 0. Run `pytest -m pdf`. The stamp must be clean.
   - Render the changed pages to `build/rc9/` and look at them: Übung page 1, Spielleitungsheft pages with the Ablaufplan and the print list, Was ist neu, Probelauf.
   - Commit `final_documents/generated/` as `docs(quick-261125-fsu): regenerate the complete print set (release candidate 9)`.
   - Update the 07-DRYRUN "Material used" section: RC9 supersedes RC8. List which PDFs changed. Print single-sided and do not staple the Teamheft.
   - Write the SUMMARY with status complete and add a STATE row. current_phase stays 07.
