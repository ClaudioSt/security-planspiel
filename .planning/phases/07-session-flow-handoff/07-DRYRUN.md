# Dry-run record (FLOW-05, plan 07-12)

Timed dry run of the full game with a test group. Prepared on 2026-11-06 from the committed config; the actual columns are filled in after the run (Task 3 of plan 07-12). Planned values were generated with `schedule_rows` from `simulation_config.json` (`session_schedule`), not typed from memory.

## Run

- **Date:** 2026-11-25 (D-05)
- **Facilitator:** to be filled in (name or role; did not write the rules, prepares only from the facilitator booklet and the intro deck)
- **Observer:** the author; records clock times and actual minutes, gives no help (D-05)
- **Test group:** to be filled in (group size, teams)
- **Scope:** Welle 0, waves 1-3, closing, debrief (D-05); the recording instrument is the printed protocol `spielleitung-probelauf.pdf` (D-07)

## Material used

- **Print set:** release candidate 6, commit e1a94ec, stamp `Stand 2026-11-25 · 95ed03c`, `dirty: false` (quick 261125-0f4, built 2026-11-25, freshness checked with `uv run planspiel print --check`: exit 0, 15 documents current). RC6 supersedes RC5 (commit c1ffdee, stamp `Stand 2026-11-24 · cd836f6`), which supersedes RC4 (commit 4cd9d8d, stamp `Stand 2026-11-22 · 7420259`, approved on paper 2026-11-23). RC6 changes: Teamheft page 5 no longer prints the Budget Review tiers or an overspend table (the event card carries them; page 5 ends in one write-in line for the KZ change from the event card), the protection-need table on Teamheft page 1 has no gesamt column, and all 87 findings of the RC5 proofreading report are applied. **Every one of the 15 PDFs differs in content from RC5, so the user reprints the complete set**; RC4 and RC5 printouts are obsolete. The stamp on every RC6 page reads `Stand 2026-11-25 · 95ed03c`. RC4 supersedes release candidate 3 (09a8f05, 07.1-10), which was built but never printed (07.2 D-17).
- **Intro deck:** `final_documents/Planspiel_Einführung + Grundlagen.pptx`, last changed in commit ca224cb (quick 261125-0f4: slide 32 shows the protection-need table without the gesamt column and drops the maximum principle, slide 22 question 04 asks which protection goal hits the asset hardest); earlier: 07.2-05 slide 32 explains the protection-need table, 07.1-09 story block 35 min, closing and debriefing 40 min.
- **Session total:** the stated total is 215 min. D-22 named 190 min; the D-34 deviation (07-09) raised it to 195; Phase 07.1 D-16 (story block 25 -> 35, debriefing 20 -> 30, stages 3/5/14/8) raised it to 215, superseding D-22 and D-34 only for these blocks. The booked slot is 240 min. The verdict below is judged against 215.

## Pass rule (D-25, verbatim from 07-CONTEXT.md)

> Pass rule for the dry run (the literal reading of ROADMAP success criterion 5): every wave block finishes within its planned minutes, the whole session finishes within the stated total (D-22), and the facilitator gets no help from the author. Each overrun, unclear point or calculation error recorded on the protocol (D-07) becomes a gap-closure item (D-06), unless the user explicitly accepts it at verification.

Reading used for the verdict: every wave block including Welle 0 (wave_0, wave_1, wave_2, wave_3) within its planned minutes; the whole session within 215 min; `## Help given` empty. PASS needs all three; a Welle 0 overrun fails the run like any other wave overrun.

## Protocol

| Block | Planned (min) | Planned span | Actual start | Actual (min) | Within plan | Questions / unclear | Calculation errors |
|---|---|---|---|---|---|---|---|
| intro (Einführung) | 10 | 0 - 10 | | | | | |
| break_1 (Pause) | 5 | 10 - 15 | | | | | |
| story_groups (Story-Gruppenarbeit) | 35 | 15 - 50 | | | | | |
| wave_0 (Übungswelle (Welle 0)) | 15 | 50 - 65 | | | | | |
| measures_budget (Maßnahmen und Budget) | 30 | 65 - 95 | | | | | |
| break_2 (Pause) | 15 | 95 - 110 | | | | | |
| wave_1 (Welle 1) | 25 | 110 - 135 | | | | | |
| wave_2 (Welle 2) | 20 | 135 - 155 | | | | | |
| wave_3 (Welle 3) | 20 | 155 - 175 | | | | | |
| closing (Abschluss) | 10 | 175 - 185 | | | | | |
| debrief (Debriefing) | 30 | 185 - 215 | | | | | |
| **Total** | 215 | 0 - 215 | | | | | |

## Help given

(empty until the run; one entry per help the author or anyone else gave the facilitator, with block and clock time)

## Gap items

(empty until Task 3; numbered `G-NN`, one per overrun, unclear point, calculation error and help given)

## Earlier timings

Reference values from the MHP round (PROJECT.md timing table) and the solo run before the release (`07-SOLO-TIMING.md`, D-32, D-34).

| Block | MHP round | Planned now | Solo run (RC1, 2026-11-04) | Dry run |
|---|---|---|---|---|
| Measures + budget (measures_budget) | 35 min | 30 min | 30 min actual, within plan | to be filled in |
| Wave 1 (Attack 1 + Event 1 at MHP) | 34 min | 25 min (was 20 before D-34) | 30 min actual, +10 over the then planned 20 | to be filled in |

- Solo block measures_budget: WITHIN (planned 30, actual 30).
- Solo block wave_1: OVERRUN (planned 20, actual 30). Resolved by user decision on 2026-11-04: wave 1 re-budgeted to 25 min (D-34 deviation), total 195; re-measured in this dry run. The solo 30 min still exceeds 25; this was accepted because a team of five splits the work. This run measures the real wave-1 time and decides whether 25 holds.
- Per D-34, Welle 0 and waves 2 and 3 were not timed before; they get their first timing in this dry run. The "Maßnahmen + Budget" block and wave 1 were timed solo before the release (D-32).

## Verdict

**Verdict:** pending
