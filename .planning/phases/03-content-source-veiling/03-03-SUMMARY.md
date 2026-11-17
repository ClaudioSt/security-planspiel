---
phase: 03-content-source-veiling
plan: 03
subsystem: content-source
tags: [toml, tomllib, clue-matrix, story-veiling, giveaway-lint, facilitator-view]

requires:
  - phase: 03-content-source-veiling
    provides: audience views, giveaway lint with story profile (plan 03-02)
provides:
  - content/clues.toml with 14 verbatim-checked clues over the pre-wave documents
  - Clue, load_clues, check_clues, FacilitatorView, format_clue_matrix and `planspiel clues`
  - PreAttackView.story and the story scope of the giveaway lint
  - veiled story documents (Unternehmenssteckbrief, Zeitungsartikel, Anfrage-Mail, Audit-Mail)
affects: [04 sheets, 05 cards and PDFs, 06 rebalance]

tech-stack:
  added: []
  patterns:
    - "Clue matrix as data (content/clues.toml) checked against texte.toml: attack ids from the config, quote verbatim after NFC, at least two clues from at least two documents per attack"
    - "FacilitatorView resolves a clue source key to a document title and the nearest heading or headline"

key-files:
  created:
    - content/clues.toml
  modified:
    - planspiel/texts.py
    - content/texte.toml
    - tests/test_clues.py

key-decisions:
  - "Audit-Mail 'insb. Erpressung, Supply-Chain-Angriffe' became 'insb. Datenverlust, Supply-Chain-Angriffe' to reduce stacked Erpress* pointers at Wave 1 (user selection)"
  - "Ransomware keeps four clues from three documents; Exfiltration's audit-mail clue is re-quoted against the new wording"
  - "'OT-Segmentierung' is usable as an ot clue (research had judged it too short)"

patterns-established:
  - "Story documents are pre-wave material: they pass the story giveaway profile (only the domain word OT and the stem Erpress* allowed)"
  - "Rows whose source has no heading show the raw source key in the matrix; candidates for headings in Phase 5"

requirements-completed: [VEIL-03]

coverage:
  - id: D1
    description: "Clue check: each config attack has at least two clues from at least two distinct pre-wave documents, quotes verbatim, why non-empty"
    requirement: VEIL-03
    verification:
      - kind: unit
        ref: "tests/test_clues.py"
        status: pass
      - kind: other
        ref: "uv run planspiel clues -> 0 Fehler, 0 Warnung(en)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Story documents contain no attack name or giveaway term under the story profile; PreAttackView exposes the story and the leak test covers it"
    requirement: VEIL-03
    verification:
      - kind: unit
        ref: "tests/test_story_veil.py"
        status: pass
      - kind: other
        ref: "uv run planspiel texts -> 0 Fehler, 0 Warnung(en)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Story rewrites and clue matrix reviewed and approved by the user"
    requirement: VEIL-03
    verification: []
    human_judgment: true
    rationale: "Wording of player-facing story documents and the clue selection are content decisions (D-13d); approved at the Task 3 checkpoint with one change"

duration: multi-session (Tasks 1-2 on 2026-10-17 to 2026-10-19, Task 3 on 2026-10-19)
completed: 2026-10-19
status: complete
---

# Phase 3 Plan 3: Story Veiling and Facilitator Clue Matrix (VEIL-03) Summary

**All four story documents are veiled (no attack name, no giveaway term beyond the domain word OT and the stem Erpress*), and a verbatim-checked clue matrix of 14 clues proves every attack stays inferable from at least two pre-wave documents, printed by `uv run planspiel clues`.**

## Commits

| Task | RED | GREEN / result |
|------|-----|----------------|
| 1 Clue check, FacilitatorView, `planspiel clues` | 26449f5 `test(03-03): add failing clue matrix tests` | 6792b92 `feat(03-03): add the clue matrix check and planspiel clues` |
| 2 Story veil and real clue matrix (incl. Task 3 decision) | 33bc568 `test(03-03): add failing story veil and real clue matrix tests` | 52c4b2f `feat(03-03): veil the story documents and add the facilitator clue matrix` |
| 3 Review of rewrites and matrix (checkpoint:decision) | n/a | applied in 52c4b2f |

RED evidence: Task 1 failed with `ImportError: cannot import name 'Clue' from 'planspiel.texts'`. Task 2 failed with 16 failed, 7 passed, 3 errors (missing story scope in `check_giveaway`, missing `PreAttackView.story`, missing `content/clues.toml`). The real-content hit list before the rewrites was: steckbrief `sinumerik` (two hits); zeitungsartikel `phishing` (ticker), `ransomware` (headline, lead), `phishing` + `verschlüssel` + `lösegeld` (ablauf); anfrage_mail `ransomware` (lage); audit_mail `ransomware` (einleitung).

## Task 3 decision

The user selected: **approve, with one change** (the orchestrator's recommendation, accepted by the user as "your take sounds good"):

- In `story.audit_mail.einleitung.paragraphs`, change "(insb. Erpressung, Supply-Chain-Angriffe)" to "(insb. Datenverlust, Supply-Chain-Angriffe)" to reduce the stacked "Erpress..." pointers at Wave 1.
- Consequently remove Ransomware clue 5 (the Audit-Mail quote) from `content/clues.toml`. The Datenexfiltration clue from the same sentence is re-quoted as "insb. Datenverlust, Supply-Chain-Angriffe" so it stays verbatim; its "Warum" stays about supply-chain attacks.
- Keep all other extra clues (14 clues total). Everything else approved as presented: all other rewrites, typographic quotes, Beratungsprojekt fix, padlock image.

No test pinned the old Audit-Mail wording or a 15-clue count (`tests/test_story_veil.py` only requires at least two clues per attack), so no test needed updating for this change.

## Final clue matrix (`uv run planspiel clues`)

| Angriff | Nr. | Dokument | Abschnitt | Zitat |
|---|---|---|---|---|
| Angriff 1: Ransomware | 1 | Unternehmenssteckbrief | SaaS / Cloud / Externe Anwendungen | Cloud-Backup: Veeam für Office-Daten (monatliche Sicherung) |
| Angriff 1: Ransomware | 2 | Anfrage-Mail | story.anfrage_mail.lage.paragraphs | Wir haben einen Virenscanner und Backups, aber keine strukturierte Security-Strategie. |
| Angriff 1: Ransomware | 3 | AUTO TIMES | DER ANGRIFF | Wir hatten kein funktionierendes Backup-Konzept |
| Angriff 1: Ransomware | 4 | AUTO TIMES | Erpresser legen Zulieferer tagelang lahm | Erpresser legen Zulieferer tagelang lahm |
| Angriff 2: OT-Störung | 1 | Unternehmenssteckbrief | OT / Produktion | Office-IT und OT/Produktion nutzen dasselbe LAN (kein separates OT-Netz) |
| Angriff 2: OT-Störung | 2 | Unternehmenssteckbrief | Betriebs- & Service-Setup | Patch-/Update-Praxis in der Produktion: Umsetzung im Rahmen verfügbarer Wartungsfenster |
| Angriff 2: OT-Störung | 3 | AUTO TIMES | OEM VERSCHÄRFT SECURITY-ANFORDERUNGEN | bis zur sauberen Trennung von Büro- und Fertigungsnetzen |
| Angriff 2: OT-Störung | 4 | AUTO TIMES | FOLGEN | Drei Fertigungslinien standen still |
| Angriff 2: OT-Störung | 5 | Audit-Mail | ERWARTETE NACHWEISE: | OT-Segmentierung |
| Angriff 3: Datenexfiltration | 1 | Unternehmenssteckbrief | Betriebs- & Service-Setup | Remote-Zugänge durch fünf Lieferanten (u. a. MES, CAD, IT) |
| Angriff 3: Datenexfiltration | 2 | Unternehmenssteckbrief | SaaS / Cloud / Externe Anwendungen | Lieferanten-Portal: extern erreichbare Web-Applikation |
| Angriff 3: Datenexfiltration | 3 | Anfrage-Mail | story.anfrage_mail.lage.paragraphs | wissen wir auch nicht genau, wer aktuell überall administrativen Zugriff auf unsere Systeme hat |
| Angriff 3: Datenexfiltration | 4 | AUTO TIMES | OEM VERSCHÄRFT SECURITY-ANFORDERUNGEN | Supply Chain Security ist geschäftskritisch |
| Angriff 3: Datenexfiltration | 5 | Audit-Mail | story.audit_mail.einleitung.paragraphs | insb. Datenverlust, Supply-Chain-Angriffe |

(The printed table also carries the "Warum" column; shortened here. Document titles abbreviated.) Every attack has at least two clues from at least two documents; Ransomware has four clues from three documents.

## Verification

- `uv run pytest -q`: 873 passed, 19 deselected
- `uv run planspiel texts`: `0 Fehler, 0 Warnung(en)`
- `uv run planspiel clues`: table above, `0 Fehler, 0 Warnung(en)`

## Deviations from Plan

1. **[Rule 3] "OT-Segmentierung" usable as an ot clue.** Research had judged it too short; it passes the 15-character minimum and is a direct pointer.
2. **[Rule 2 - Missing critical functionality] FacilitatorView section fallback.** When a source has no `heading`, the view also falls back to the nearest `headline`, so newspaper rows show a readable section. Covered by a new test in `tests/test_clues.py`.
3. **Anfrage-Mail `lage` and Audit-Mail `einleitung` rows show the raw source key** because the source has no heading. Possible headings in Phase 5.
4. **Typographic quotes.** The „...“ closing quotes were fixed in three newspaper strings (beyond the plan, per the user's 03-01 note).
5. **RED test design.** The real-content hit list is asserted through `giveaway_hits`, and `real_clues` is a fixture in `tests/test_story_veil.py`.
6. **M6 "Phishing" in the pre-wave measure text is unchanged** (D-06, measure texts are outside the giveaway lint).
7. **Pre-existing HandCalcWarning** `hand_calc.kz_slope attacks.exfil` (17/7) appears in test and CLI output; unrelated to this plan.

## Known Stubs

None.

## Threat Flags

None. The story veil and the clue check are covered by the plan's threat model (giveaway lint, leak test, verbatim quote check, blocking decision checkpoint).

## Self-Check: PASSED

- Files: content/clues.toml, planspiel/texts.py, content/texte.toml, tests/test_clues.py found
- Commits 26449f5, 6792b92, 33bc568, 52c4b2f found in `git log`
