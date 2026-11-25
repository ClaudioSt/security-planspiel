---
phase: quick-261125-fsu
plan: 261125-fsu
subsystem: session-schedule, print-texts, intro-deck, tracking-sheet
tags: [practice-wave, teamheft-loose-sheets, event-veil, rc9]
requires: [quick-261125-djw RC8]
provides:
  - "no joint practice wave: wave_0 block removed, 200 minutes in total, the Übungsblatt is a handout of the Maßnahmen-und-Budget block"
  - "Teamheft handed out as loose sheets per block, named Teamheft (<chapter>) in the directions and on the deck material lines"
  - "no event name on player sheets except the event deck (Kurswechsel credit row made event-neutral)"
  - "Tracking-Bogen row Monetärer Schaden der Welle, set off from the KZ rows"
  - "print release candidate 9: stamp Stand 2026-11-25 · 7b6d555, print commit 77576b3"
affects: [07-12 dry run materials]
key-files:
  modified:
    - simulation_config.json
    - content/texte.toml
    - README.md
    - planspiel/practice.py
    - planspiel/probelauf.py
    - planspiel/schedule.py
    - planspiel/texts.py
    - planspiel/was_neu.py
    - planspiel/master.py
    - print/templates/uebung.tex.j2
    - print/templates/angriff_blatt.tex.j2
    - print/templates/teamheft_tracking.tex.j2
    - final_documents/Planspiel_Einführung + Grundlagen.pptx
    - final_documents/generated/*.pdf
  created:
    - tests/test_loose_sheets_rc9.py
decisions:
  - "Practice title carries the not-scored note: Welle 0 – Übung (Beispiel, zählt nicht für die Wertung); no box"
  - "Directions name the Teamheft by printed chapter titles from texte.toml, no page numbers in prose"
  - "Budget slide says Übungsblatt Welle 0 as the user worded it; the print-list label stays Übungsblatt (ablauf texts may not carry digits)"
  - "Dead practice-wave labels removed (practice_label, pass_wave_practice, the wave 0 branch of the schedule label and of the probelauf rule)"
  - "Event-name guard: only spieler-eventkarten names an event; the Budget Review chapter title of the Teamheft is the one allowed exception (values stay guarded)"
  - "Spielphasen slide: five columns stretched to the slide width, icons keep their aspect"
  - "No game value changed: rules.py, uv.lock, pyproject.toml untouched; planspiel gate unchanged"
metrics:
  completed: 2026-11-25
status: complete
---

# Quick 261125-fsu: No joint practice wave, Teamheft as loose sheets, print RC9

RC9 on top of RC8 (branch `teamheft-loose-sheets`, not pushed). Four user decisions of 2026-11-25 plus two follow-ups from the same day went in before the build: the practice sheet is a reference handout and not calculated together, the Teamheft goes out per block, no event may appear on a player sheet before its card, and the damage row of the Tracking-Bogen says it is money.

## Commits

| Commit | Message |
|---|---|
| d945dbd | test: pin no joint practice wave, 200 minutes, Teamheft by chapter and the 37-slide deck (RED) |
| 09c00a1 | feat: no joint practice wave, Teamheft handed out as loose sheets (GREEN) |
| 328de96 | docs(deck): intro deck without the Übungswelle slide, material lines name Teamheft chapters |
| 1005de1 | test: no event name on player sheets, monetary damage label and gap (RED) |
| 667a046 | feat: event-neutral change window and monetary damage row |
| 95becc0 | docs: shorten the Was-ist-neu Teamheft line so the capped worst case keeps one page |
| 2d26ad2, 90cf401 | test (RED) and docs (GREEN): RoS carry hint names the damage row by its tracking label |
| 77576b3 | docs: regenerate the complete print set (release candidate 9) |

## What changed

- **Schedule (D-1):** `wave_0` leaves `session_schedule.blocks`, `total_minutes` 215 to 200. The `practice` block stays. README flow steps renumbered, CONCERNS and INVENTORY follow. The validator needed no change.
- **Practice sheet (D-2):** the box `practice.intro` is gone (text key, model field, template box). The title now reads "Welle 0 – Übung (Beispiel, zählt nicht für die Wertung)".
- **Spielleitungsheft (D-3):** `wave_0` direction gone; `measures_budget` hands out Maßnahmenkarten, Übungsblatt, So funktioniert eine Welle and Teamheft (Budget und Planung, Tracking-Bogen) together; `story_groups` hands out Teamheft (Schutzbedarf und Risikoregister); `closing` hands out the Eventkarte "Budget Review" and Teamheft (Return on Security, Budget Review), the sentence ends "die Blätter bleiben bei den Teams". Print list: "Das Teamheft druckt ihr je Team, aber heftet es nicht: Seine Blätter gebt ihr je Block einzeln aus." Debrief: "legen dafür ihre Blätter ... bereit". Was ist neu: new flow row and material rows.
- **Deck (D-4):** 37 slides. Slide 33 (Übungswelle) deleted, caches renumbered. Slide 28 shows five phases (Einführung, Story-Gruppenarbeit, Maßnahmen und Budget, Angriffswellen, Abschluss und Debriefing), stretched to the slide width. Material lines: see the report; the waves slide lists only the attack sheet and the event cards.
- **Event veil:** Teamheft change-window credit row "Gutschrift durch Event (laut Eventkarte)", hint "Eine Gutschrift gibt es nur, wenn eine Eventkarte sie nennt; wie hoch sie ist, steht auf der Karte.", RoS row "Init-Differenzen aus Change-Fenstern". New guard test `test_no_player_document_but_the_event_deck_names_an_event` over all eight events.
- **Damage row:** "Monetärer Schaden der Welle" with a 1.2 mm gap and a second rule under the KZ rows; the wave answer keys and the practice excerpt use the same label; the RoS carry hint names the row.

## Gates (final committed state)

- `uv run planspiel validate`, `texts`, `clues`: 0 Fehler, 0 Warnung(en) each
- `uv run planspiel gate`: bestanden (see report, unchanged)
- `uv run pytest -q`: 3144 passed, 3 skipped, 213 deselected
- `uv run pytest -m pdf -q`: 165 passed
- `uv run planspiel print`: 15 documents, `dirty: false`, `Stand 2026-11-25 · 7b6d555`; `print --check` exit 0

## Deviations from Plan

- **[Rule 2] Dead code removed:** with no wave 0 block the practice-wave label and the practice clause of the Probelauf pass rule were unreachable; removed together with their text keys.
- **[Rule 1] Was-ist-neu page fit:** the first Teamheft material line wrapped and broke the capped worst case (caught by `pytest -m pdf`); shortened.
- **User follow-ups** (event-neutral Teamheft, damage label, deck chapter form, joint hand-out) were applied test-first before the build.
- **Open point:** the Budget slide says "Übungsblatt Welle 0" as worded by the user while the print list says "Übungsblatt".

## Known Stubs

None.

## Threat Flags

None. The new guard closes a veil leak (an event named on a player sheet before its card).

## Self-Check: PASSED

Commits exist; `print --check` exit 0; 15 PDFs in `final_documents/generated`; the deck holds 37 slides.
