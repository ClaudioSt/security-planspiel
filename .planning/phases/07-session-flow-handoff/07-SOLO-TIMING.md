# Solo timing record (D-32, D-34), plan 07-09

Walk-through of the blocks "Maßnahmen + Budget" and wave 1 by one person alone, with only the generated material, timed against the planned minutes of `session_schedule`. Welle 0 and waves 2 and 3 are not timed here; their first timing is the dry run (07-12, D-34).

## Planned minutes and direction lines

Generated with (never typed from memory):

```
uv run python -c "from pathlib import Path; from planspiel.config import load_config; from planspiel.texts import load_texts; from planspiel.schedule import schedule_rows; ..."  # schedule_rows(load_config('simulation_config.json'), load_texts('content/texte.toml'))
```

| Block | Label | Planned minutes | Offset (start - end) |
|---|---|---|---|
| measures_budget | Maßnahmen und Budget | 30 | 55 - 85 |
| wave_1 | Welle 1 | 20 | 100 - 120 |

Direction line measures_budget: Gebt das Teamheft und die Maßnahmenkarten aus. Die Teams verhandeln ihr Budget-Tier und wählen ihre Maßnahmen.

Direction line wave_1: Lest die Ereignisse dieser Welle vor und gebt ihre Eventkarten aus. Gebt erst jetzt das Arbeitsblatt dieser Welle aus, nie früher. Die Teams rechnen. Danach folgt innerhalb dieses Blocks das Change-Fenster mit dem Pflichttausch des Kurswechsels.

## Timed set

Stamp: Stand 2026-11-03 · 13d4090 (manifest `dirty: false`; print-set commit release candidate 1: see `git log -1 -- final_documents/generated`).

Material by file name (from the print list):

- measures_budget: `spieler-teamheft.pdf`, `spieler-massnahmenkarten.pdf`
- wave_1: `spieler-teamheft.pdf`, `spieler-eventkarten.pdf`, `spieler-so-funktioniert-eine-welle.pdf`, `angriff-1_ransomware.pdf`

## MHP comparison (PROJECT.md timing table)

- "Measures + budget": 35 min at MHP, planned now: 30 min
- "Attack 1 + Event 1": 34 min at MHP, planned now: 20 min

## Timing

### Round 1, 2026-11-04 (release candidate 1, stamp Stand 2026-11-03 · 13d4090)

One person alone, generated material only.

- measures_budget: 30 min actual, 30 min planned, difference 0.
- wave_1: 30 min actual, 20 min planned, difference +10.

Chosen plan and final wave-1 values: not reported.

## Questions and errors

None. No unclear points, no hesitations, no printed errors. The time went to calculating and filling in, not to ambiguity.

## Gap items

None. There are no ST gap items; the overrun is a budgeting question, not a material gap.

## Verdict

**Block measures_budget:** WITHIN (planned 30, actual 30)
**Block wave_1:** OVERRUN (planned 20, actual 30)

**Verdict:** OVERRUN resolved by user decision: wave_1 re-budgeted to 25 min (D-34 deviation, user-approved 2026-11-04), re-measured in 07-12.

The strict rule (an overrun blocks the release) was replaced by the user's decision: every other block stays as it is, so `session_schedule.total_minutes` goes 190 -> 195. The solo run (30 min) still exceeds the new 25 min; this is accepted because a team of five splits the work. The dry run on 2026-11-25 (plan 07-12) measures the real wave-1 time and decides whether 25 holds.

## Release

Release candidate 2 (commit 8cf1972, stamp `Stand 2026-11-04 · 737ba65`, `dirty: false`) was built from the re-budgeted schedule (wave_1 25 min, total 195) and the adapted intro deck slide 34.

User decision, 2026-11-06, after printing the set and checking it on paper (including slide 34 of the intro deck): "freigeben". The set is released for the dry run on 2026-11-25. The released print-set commit is 8cf1972; the wave-1 timing is not re-measured solo, it is measured in the dry run (07-12).
