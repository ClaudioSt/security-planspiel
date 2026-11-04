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

(pending)

## Questions and errors

(pending)

## Gap items

(none yet)

## Verdict

**Verdict:** pending
