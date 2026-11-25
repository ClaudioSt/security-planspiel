# Review 3: play-through of print RC7 (2026-11-25)

Read-only third pass over the 15 PDFs in `final_documents/generated/` (stamp `Stand 2026-11-25 · 4fe9685`, `uv run planspiel print --check` exit 0). Method: the game was played on paper as one Low-tier team and as the facilitator, block by block along the Ablaufplan, with only the documents handed out at each point. All 48 pages were rendered with `pdftoppm` into `build/proof3/img/` and viewed as images, including all 16 Spielleitungsheft pages and all 8 card pages. Nothing was edited besides this file.

Result in one line: **no wrong number, no attack named too early, no pass-2 regression in the numbers.** The Low reference path reproduces every answer-key value by hand. What remains are gaps in the instructions, mostly at the start of tracking and in the Abschluss.

Category codes: **A** stuck or missing instruction, **B** pass-2 change that did not land cleanly, **C** label mismatch between sheets, **D** language, **E** layout, **V** veil observation (a decision, not a certain error).

## 1. Blocking for the dry run

Nothing stops play outright. Four points will cost time or mislead today unless the facilitator announces them or they are checked before printing:

1. **Print single-sided (check before printing).** The Druckliste (Spielleitungsheft p3) says to cut the Maßnahmen- and Eventkarten but not that they must be printed single-sided. A duplex print destroys the cards when cut, and it puts the Tracking-Bogen (Teamheft p3) on the back of the planning page and the RoS page (p4) behind the sheet it copies from. Key: `sheets.ablauf.print_intro`. Suggested addition: "Druckt alles einseitig."
2. **Nobody tells the teams to fill the Start column of the Tracking-Bogen.** After "Maßnahmen und Budget" the Start column needs KZ-Start, Init-Kosten and Restbudget (Tier-Budget − Init-Kosten). The block instruction (Spielleitungsheft p2) only says "trägt seine Maßnahmen im Teamheft ein"; the Tracking-Bogen itself only says "Pro Welle eine Spalte". Teams that skip it get stuck at the first Restbudget in Welle 1. Announce it at minute 95.
3. **Welle 1, "KZ Events": neither Welle-1 card carries a KZ value.** The sheet says "ihr lest sie an den Eventkarten ab"; Kurswechsel and Operative Unterstützung show no KZ. Teams will ask or wait. The answer is ±0 (answer key p7). Announce it.
4. **Abschluss: the path to "KZ final" and to the comparison table is not written down.** Teamheft p5 ends with "KZ-Änderung Budget Review"; KZ final is computed on the Tracking-Bogen (p3), and no text sends the teams back there. The facilitator's instruction says "Sammelt die Ergebnisse ein", while the Debriefing needs the Teamheft in the teams' hands and a filled Vergleichstabelle (p13) by its second phase. Decide before the run: teams keep the Teamheft, the facilitator notes KZ final and RoS per team.

## 2. Walkthrough log

Plan used: Low reference path (Spielleitungsheft p1): Start M4 L1, M6 L2, M7 L1, M8 L1, M9 L3, M10 L2; Kurswechsel swap M8 → M5 L1; after Welle 2 cancel M6.

| Block | What I did | Result | Stumbles |
|---|---|---|---|
| Einführung, Pause | Facilitator: slides, lay out story documents. | – | "Story-Unterlagen" is never listed; the Druckliste has no grouping (finding A7). |
| Story-Gruppenarbeit | Read Steckbrief, Zeitungsartikel, both mails; filled W1–W4 and R1–R5. Asked the "Geschäftsführung" for one day of standstill. | Answer "mittel" (p4) fits the Steckbrief (about 15 Mio. EUR per year gives roughly 60.000 € per working day). Clue matrix sections "dritter Absatz" (Anfrage-Mail) and "zweiter Absatz" (Audit-Mail) match the printed mails. | The register text says "Die Stufe des Risikos lest ihr oben … ab", but there is no field for it (A8). Otherwise clear. |
| Übungswelle | Recomputed every box. | CIA 16/22/19, E-Wert 19, bonus 4, GR 23, damage 20.000 €, KZ +6,5, Recovery 18.000 €, event −4, +2,5 → +3, KZ 98 → 101 → 100, Restbudget 96.000 € → 73.000 €. All match the sheet and the key on p5. | None in the numbers. Step 5 says "KZ", step 7 "KZ Angriff" (C1). |
| Maßnahmen und Budget | Chose Low, filled the planning page from the cards. | Init 180.000 €, OPEX 39.000 € per wave, planned total 297.000 € against 370.000 €. | Start column of the Tracking-Bogen not instructed (blocking 2, A3). Start values: KZ 39, Init 180.000 €, Restbudget 190.000 €. |
| Welle 1 | Events read, sheet filled, tracking, change window with the swap. | CIA 20/25/21, E-Wert 22,2, bonus 4 (M6), GR 26,2, Fall 3, 76.000 € → 68.400 €, KZ Angriff +0,4, KZ Events ±0, rounded ±0, KZ 39. Event: OPEX −12.000 €. Window: M8 → Level 0, M5 Level 1 Δ Init 40.000 €, Gutschrift 16.000 €, netto 24.000 €. Restbudget 139.000 €. All match p7. | KZ Events without a source value (blocking 3, A4). The Restbudget of Welle 1 can only be closed after the change window, because its Init-Differenz belongs in the Welle-1 column; the footnote "oben in die Spalte vor dem Fenster" says so, but tersely (D1). "Schaden vor Recovery" box too small for the amount (B2). |
| Welle 2 | Same. | CIA 21/24/23, E-Wert 22,8, bonus 0, Fall 3, 230.400 € → 207.360 €, KZ Angriff −2,08, OEM-Audit 3 erfüllt +1, Kritische Schwachstelle ±0, −1,08 → −1, KZ 38. Budget −20.000 €, OPEX 37.000 €, window: M6 cancelled, 0 €. Restbudget 82.000 €. All match p9. | None. |
| Welle 3 | Same. | CIA 18/22/21, E-Wert 19,8, Fall 1, 140.000 €, KZ −6, Exzellenz-Bonus +6, Nervige Authentifizierung ±0, ±0, KZ 38. OPEX 31.000 €, Restbudget 51.000 €. All match p11. | The no-Recovery sentence is there and clear. |
| Abschluss | RoS page, Budget Review page with the event card, Rückblick. | Eigene Kosten 311.000 €, Schäden 415.760 €, Vermiedener Schaden 204.240 €, RoS −0,34. Verfügbares Budget 350.000 €, Gesamtkosten 299.000 €, Restbudget 51.000 € (equals the Tracking-Bogen), card: +18, KZ final 56. All match p12. Rückblick rule works with the three full damages (160.000 € hoch, 320.000 € hoch, 140.000 € mittel). | No pointer back to the Tracking-Bogen for KZ final (blocking 4, A1); open Restbudget cell in the Budget Review column without instruction (A6); three names for the final KZ (C2). Ten minutes are tight for three tasks. |
| Debriefing | Facilitator: questions p13, comparison table. | Final-Index 56 + 10 × (−0,34) = 52,6, matches p12. Contents page numbers on p1 match the real pages (2, 3, 4, 5, 6, 8, 10, 12, 12, 13, 14). | "Sammelt die Ergebnisse ein" against "Die Teams legen … ihr Teamheft … bereit" (A2). |

Veil: no player page names an attack before its wave; Budget Review values appear only on the event card; no "Maßnahmenwechsel", no "gesamt" column, "Arbeitsblatt" only in facilitator documents. Two observations are listed under V.

Pass-2 changes checked on the pages and found in place: Budget Review card in the Abschluss instruction, cutting and sorting note, RoS carry hint, Δ Init definition (matches `rules.window_cost`), Übungsbudget and KZ line, Geschäftsführung hint, no-Recovery sentence, Tier comparison and "Unser Tier", rounding hint on its own line, "+2" slope, "+0,06", contents with page numbers, Übung key before Angriff 1, example rows without W number, value cells on p4 and p5.

## 3. Remaining findings by document

### spieler-teamheft.pdf

| Page | Quote | Problem | Suggested German fix | Source | Cat. |
|---|---|---|---|---|---|
| 5 | "Die KZ-Änderung des Budget Reviews lest ihr danach von der Eventkarte ab, die ihr zum Abschluss bekommt." | The page ends there. KZ final is computed on the Tracking-Bogen (p3), and nothing sends the teams back. | add: "Tragt sie auch im Tracking-Bogen in der Spalte Budget Review ein und berechnet dort die KZ final." | `sheets.teamheft.review_intro` | A1 |
| 3 | "Pro Welle eine Spalte, von oben nach unten: …" | The Start column is not explained: KZ-Start goes into "KZ vor der Welle", and it must be filled before Welle 1. | add: "Die Spalte Start füllt ihr nach der Planung aus: KZ-Start eures Tiers, Init-Kosten und Restbudget." | `sheets.tracking.intro` | A3 |
| 3 | row "Restbudget (laufend)", column "Budget Review" | The cell is open, but the formula gives no value for it; p5 computes the same amount again. | Grey the cell out, or add: "In der Spalte Budget Review steht das Restbudget von der Seite Budget Review." | `planspiel/booklet.py` / `print/templates/teamheft_tracking.tex.j2`; `sheets.tracking.external_hint` | A6 |
| 1 | "Die Stufe des Risikos lest ihr oben in der Schutzbedarfstabelle ab: Zeile des Werts, Spalte des Hauptziels." | There is no field for the Stufe in the register; teams look for one. | "Die Stufe des Risikos steht oben in der Schutzbedarfstabelle (Zeile des Werts, Spalte des Hauptziels); ihr müsst sie nicht noch einmal eintragen." | `sheets.register` (register instruction) | A8 |
| 3 | "Init-Differenz netto: oben in die Spalte vor dem Fenster." | Too terse; "Spalte vor dem Fenster" is not a column name. | "Die Init-Differenz netto tragt ihr oben in der Spalte der Welle ein, auf die das Fenster folgt." | `sheets.tracking` (window footer) | D1 |
| 3 | "KZ final" (also Spielleitungsheft p12 "KZ am Ende", p13 "KZ") | Three names for one value. | "KZ final" in all three places | `sheets.spielleitung` (final table label), `sheets.debrief.compare_head_kz` | C2 |
| 2 | row "Summe" of the planning table | The row is shaded across all cells, the Level cell is open although nothing belongs there, and the OPEX sum cell is merged with "gegen R#". | Shade only the label; close the Level and "gegen R#" cells. | `print/templates/teamheft_planung.tex.j2` | E2 |
| 3 | cell "OPEX dieser Welle", Welle 3 | The cell seems to lose its lower and right rule next to the grey block below (visible in the 110 dpi rendering). | Check on the printout; same colortbl effect as in pass 2. | `print/templates/teamheft_tracking.tex.j2` | E3 |
| 3 | rows "Event: Budget" (open only in Welle 2) and "Event: OPEX" (open only in Welle 1) | The grey pattern tells the teams during the story block in which wave a budget event and an OPEX event come. | Leave all three wave cells open, if the timing should stay unknown. | `planspiel/booklet.py` | V1 |
| 4 | "620.000 € ist der volle Schaden aller Angriffe ohne Maßnahmen" | Came in with pass 2. The teams hold the sum of all three full damages from minute 15. It names no attack and no single value. | Keep, or shorten to "= 620.000 € − Summe der Schäden" and let the facilitator explain the amount in the Abschluss. | `planspiel/booklet.py`; `sheets.labels.avoided_damage` | V2 |

### angriff-1_ransomware.pdf, angriff-2_ot.pdf, angriff-3_exfil.pdf, uebung-welle-0.pdf

| Page | Quote | Problem | Suggested German fix | Source | Cat. |
|---|---|---|---|---|---|
| A1 p2 (same text on A2, A3) | "KZ Events ist die KZ-Wirkung aller Events dieser Welle zusammen; ihr lest sie an den Eventkarten ab." | In Welle 1 no card shows a KZ value. | add: "Nennt keine Eventkarte eine KZ-Wirkung, tragt ±0 ein." | `sheets.angriff.events_hint` | A4 |
| all p2; Übung p2 | "Schaden vor Recovery: 160.000 € · KZ: −8", "KZ = −8 + (GR … − 22) × 2", then step 7 "KZ Angriff" | The value is called "KZ" in step 5 and "KZ Angriff" in step 7; "KZ: −8" can be read as the new KZ. | "KZ Angriff" in step 5 as well | `sheets.angriff.label_kz` | C1 |
| A1, A2 p2; Übung p2 | "Schaden nach Recovery = Schaden vor Recovery [ ] € × (1 − r [ ]) =" | The line still sits directly on the lower table rule, and the first box is 13 mm wide: "230.400" does not fit by hand. | Add space above the line and make the box as wide as the result box. | `print/templates/angriff_blatt.tex.j2`, `print/templates/uebung.tex.j2` | B2 |
| all p2 | "… hat dieser Angriff getroffen? [ ] R-Nummer / oder „nicht im Register“; ihr braucht die Zeile für den Rückblick." | The hint breaks after "R-Nummer", and the 13 mm box cannot hold "nicht im Register". | Put the hint on its own line and widen the box: "Tragt die R-Nummer ein oder „nicht im Register“; ihr braucht die Zeile für den Rückblick." | `sheets.angriff.reality_hint`; template | E1 |

### spielleitung-uebersicht.pdf

| Page | Quote | Problem | Suggested German fix | Source | Cat. |
|---|---|---|---|---|---|
| 2 | "… und füllen im Risikoregister die Spalte Rückblick aus. Sammelt die Ergebnisse ein." | The Debriefing needs the Teamheft with the teams (p13) and a filled Vergleichstabelle; "einsammeln" contradicts that, and KZ final is not mentioned. | "… die Spalte Rückblick aus. Zuletzt berechnen sie im Tracking-Bogen die KZ final. Notiert je Team KZ final und RoS in der Vergleichstabelle; die Teamhefte bleiben bei den Teams." | `sheets.ablauf.blocks.closing.direction` | A2 |
| 2 | "Jedes Team einigt sich intern auf sein Budget-Tier und trägt seine Maßnahmen im Teamheft ein." | The Start column of the Tracking-Bogen is missing. | add: "Am Ende füllen die Teams im Tracking-Bogen die Spalte Start aus." | `sheets.ablauf.blocks.measures_budget.direction` | A3 (counted once) |
| 3 | "Schneidet die Maßnahmen- und Eventkarten an den Schnittlinien aus …" | No word on single-sided printing. | add at the start: "Druckt alles einseitig." | `sheets.ablauf.print_intro` | A5 |
| 2, 3 | "Gebt jedem Team die Story-Unterlagen und das Teamheft." | The four story documents are never named as a group. | "Gebt jedem Team die Story-Unterlagen (Unternehmenssteckbrief, Zeitungsartikel, Anfrage-Mail, Audit-Mail) und das Teamheft." | `sheets.ablauf.blocks.story_groups.direction` | A7 |
| 6, 8, 10 | "Ganze GR-Schritte im mittleren Fall" | Pass 2 changed the how-to on p1 to "im dritten Fall"; this heading kept "mittleren". | "Ganze GR-Schritte im dritten Fall" (digit-free) | `sheets.spielleitung.check_table_intro` | B1 |
| 7, 9, 11 | "Budgetänderung durch Events", "OPEX-Änderung durch Events (Plus: Kosten)", "Restbudget nach der Welle" | The Tracking-Bogen the facilitator compares against says "Event: Budget", "Event: OPEX", "Restbudget (laufend)". | Use the Tracking-Bogen labels in the wave keys. | `sheets.spielleitung` (key labels) | C3 |
| 11 | "Schaden vor Recovery 140.000 € / Recovery-Faktor r – / Schaden nach Recovery 140.000 €" | The sheet of Angriff 3 and the Prüfzeilen on p10 know only "Schaden". | One row "Schaden" when Recovery is not allowed. | `planspiel/master.py`; `sheets.spielleitung.key_damage_before` | C4 |
| 13 | "Siehe Hinweis-Matrix für die Story-Gruppenarbeit" | No full stop, no page. | "Siehe die Hinweis-Matrix für die Story-Gruppenarbeit am Ende dieses Hefts." | `sheets.debrief.stages.analysis` (data prompt) | D2 |

Layout of all 16 pages: no overflow, no cut-off text, no table touching the footer; the nine-column table on p8 is tight but readable.

### spielleitung-was-ist-neu.pdf

| Page | Quote | Problem | Suggested German fix | Source | Cat. |
|---|---|---|---|---|---|
| 1 | "(215 Min. gesamt, je Welle 20 / 25 Min.)" | Welle 1 is the long one, so the order reads backwards. | "(215 Min. gesamt, Welle 1 länger als die anderen Wellen)" or build the text from the schedule in wave order | `planspiel/was_neu.py` | D3 |

The page is dense but fits and stays readable.

### Documents without findings

`spieler-massnahmenkarten.pdf` (all 8 pages, 30 cards plus legend: no overflow, all values as used in the walkthrough), `spieler-eventkarten.pdf` (2 pages), `spieler-so-funktioniert-eine-welle.pdf`, `spieler-unternehmenssteckbrief.pdf`, `spieler-zeitungsartikel.pdf`, `spieler-anfrage-mail.pdf`, `spieler-audit-mail.pdf`, `spielleitung-probelauf.pdf`.

## 4. Count per category

| Category | Findings |
|---|---|
| A. Stuck or missing instruction | 8 |
| B. Pass-2 change not landed cleanly | 2 |
| C. Label mismatch | 4 |
| D. Language | 3 |
| E. Layout | 3 |
| V. Veil observation | 2 |
| Total | 22 |

Wrong or inconsistent numbers: 0. Attack names or Budget Review values revealed too early: 0. The A3 row in the Spielleitungsheft table belongs to the A3 finding of the Teamheft and is counted once.
