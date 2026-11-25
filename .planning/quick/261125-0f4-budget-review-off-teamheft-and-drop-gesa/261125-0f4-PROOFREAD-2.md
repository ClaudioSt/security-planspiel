# Proofreading report, pass 2: print RC6 (2026-11-25)

Read-only second pass over the 15 PDFs in `final_documents/generated/` (stamp `95ed03c`, clean build). Every PDF was extracted with pypdf and read in full; Teamheft, Übung, Welle page, event cards, attack sheets, Was ist neu, Zeitungsartikel and parts of the Spielleitungsheft and Maßnahmenkarten were also rendered with `pdftoppm` and checked as images. Source keys refer to `content/texte.toml` unless marked otherwise. Nothing was edited besides this file.

Category codes used in the tables: **A** breaks play or lacks a source/instruction, **B** pass-1 fix that went wrong or stayed incomplete, **C** terminology leftover, **D** language or clarity, **E** layout.

Suggested replacements avoid new digits (digit lint). Where a number is needed, it has to come from the config through code; this is noted.

## Top findings

1. **The Budget Review card is never handed out** (Spielleitungsheft p2, block Abschluss). Teamheft p5 says the KZ change is read "von der Eventkarte ab, die ihr zum Abschluss bekommt", and by design the tiers and the penalty exist only on that card. The Abschluss instruction does not mention the card. It also names the pages in the wrong order: p5 needs "Eigene Kosten" from the RoS page (p4). Key: `sheets.ablauf.blocks.closing.direction`. Suggested: "Gebt die Eventkarte „Budget Review“ aus. Die Teams rechnen im Teamheft erst die RoS-Seite, dann das Budget Review aus und füllen im Risikoregister die Spalte Rückblick aus. Sammelt die Ergebnisse ein."
2. **Event cards must be cut and sorted, and nothing says so** (Druckliste p3; Eventkarten p1 and p2). The PDF prints four cards per sheet with cut lines; p1 mixes Welle 1 and Welle 2, p2 mixes Welle 2, Welle 3 and the Budget Review card. A facilitator who hands out a sheet reveals later events and the Budget Review tiers. Key: `sheets.ablauf.print_intro`. Suggested addition: "Schneidet Maßnahmen- und Eventkarten an den Schnittlinien aus und sortiert die Eventkarten nach Welle; die Karte „Budget Review“ gebt ihr erst im Abschluss aus."
3. **RoS page: "Die Summen übernehmt ihr von den vorherigen Seiten"** (Teamheft p4). The nearest sums are the planned ones on p2 ("Summe Init-Kosten", "Summe OPEX je Welle"), which are wrong after any change window. The correct sources are rows of the Tracking-Bogen. Key: `sheets.teamheft.ros_carry_hint`. Suggested: "Die Werte übernehmt ihr aus dem Tracking-Bogen: Init-Kosten aus der Spalte Start, dazu die Summen der Zeilen Init-Differenz netto und OPEX dieser Welle sowie den Schaden jeder Welle. Die Planung von der Seite davor zählt hier nicht."
4. **Δ Init / "Init-Differenz" is never defined for players** (Teamheft p3, Welle page, Maßnahmenkarten legend). "Init zahlt ihr einmal, wenn ihr … ihr Level erhöht" can be read as the full Init of the new level; the code charges new minus old (`rules.window_cost`). A newly added measure is not covered by "bei einer Erhöhung" either. Keys: `sheets.tracking.window_intro`, `sheets.karten.legend_costs`, `sheets.welle.window_rules`. Suggested for the tracking page: "Δ Init ist die Init des neuen Levels minus die Init des bisherigen Levels; bei einer neuen Maßnahme die volle Init."
5. **Übung, tracking example: "Restbudget (laufend) 96.000 €" has no source** (Übung p3). The sheet shows Init 104.000 € but never the practice budget (`practice.budget` = 200 in the config) and never says why KZ starts at 98. A team following "Schritt für Schritt" cannot reproduce the first Restbudget. Source: `planspiel/practice.py` and the practice template (needs a new text key, numbers from config). Suggested line above the table: "Das Beispielteam startet mit einem Übungsbudget von <Budget aus der Config> und einer KZ von <KZ-Start aus der Config>. Restbudget am Start = Budget − Init-Kosten."
6. **Schutzbedarf: players are not told they may ask** (Teamheft p1). The facilitator has a whole page of answers ("Geschäftsfolgen: Antworten der Geschäftsführung") for questions the Teamheft never invites; teams will guess euro bands instead. Key: `sheets.register.need_instruction`. Suggested addition: "Könnt ihr eine Folge nicht einschätzen, fragt die Geschäftsführung von MechTech (die Spielleitung)."
7. **Angriff 3 has no Recovery step and does not say why** (Angriff 3 p2). The Welle page promises "Ob die Welle Recovery zulässt, steht auf dem Angriffsblatt." A team with M4 will ask whether the step was forgotten. Source: attack-sheet template plus a new key under `sheets.angriff`. Suggested line after step 5: "Bei diesem Angriff gibt es keine Recovery: Abgeflossene Daten lassen sich nicht zurückholen."
8. **Planning page never relates the plan to the Tier-Budget** (Teamheft p2). "Geplante Gesamtkosten" is computed but not compared with anything, and no page says whether a plan above the Tier-Budget is allowed. This is the first question teams will ask, and the answer does not need the veiled review values. Key: `sheets.teamheft.planning_instruction` or `sheets.budget.anticipated_sum_intro`. Suggested: "Vergleicht die geplanten Gesamtkosten mit eurem Tier-Budget. Was am Ende übrig bleibt oder fehlt, bewertet das Budget Review."
9. **Was ist neu, Kurswechsel: "bis zur Höhe der alten"** (p1). The shortening dropped "Init der", so the sentence now compares an amount with a measure. See next section.
10. **Rounding hint breaks in the middle of the parenthesis** (all attack sheets p2, Übung p2): the formula line ends with "gerundet (bei" and the next line starts with ",5 weg von der Null …". See next section.

## Fixes from pass 1 that went wrong or stayed incomplete

| Document, page | Quote | Problem | Suggested replacement | Source key | Cat. |
|---|---|---|---|---|---|
| Was ist neu 1 | "der Kunde trägt die Init der neuen Maßnahme bis zur Höhe der alten." | Shortened too far: "der alten" has no noun (Höhe der alten Maßnahme?). | "… bis zur Höhe der Init der alten." | `sheets.was_neu.rules.kurswechsel.text` | B |
| Was ist neu 1 | "der RoS wird vorher auf Hundertstel gerundet" | Gender was fixed, but the wording still differs from the Spielleitungsheft p11 ("auf zwei Nachkommastellen"). | "der RoS wird vorher auf zwei Nachkommastellen gerundet" | `sheets.was_neu.rules.final_index.text` | B |
| Was ist neu 1 | row heads "Herabstufen", "Init bei Hochstufung" | The texts now say "senken / erhöhen", the headings kept the old words. | "Senken und Kündigen", "Init beim Erhöhen" | `sheets.was_neu.rules.downgrade.heading`, `sheets.was_neu.rules.init_window.heading` | B |
| Eventkarten 1 | "Weitere Levelwechsel im selben Fenster bleiben erlaubt." | "Levelwechsel" came in with the pass-1 suggestion; players never get the term (it is defined only in Was ist neu) and elsewhere read "Änderungen". | "Weitere Änderungen im selben Fenster bleiben erlaubt." | `events.kurswechsel.rule` | B |
| Teamheft 3 | "(gekündigt: Level null), bei einer Erhöhung auch Δ Init" | "Level null" next to "Level 0" on the event cards and the Recovery table; "bei einer Erhöhung" leaves out a newly added measure (see top finding 4). | "(gekündigt: Level 0), bei einer Erhöhung oder einer neuen Maßnahme auch Δ Init" (needs "0" in the digit allowlist; otherwise keep "null" and add the new-measure part) | `sheets.tracking.window_intro` | B |
| Teamheft 2 | "Im Planspiel wählt ihr zu Beginn ein Budget-Tier. Je höher das Budget, desto … Dafür erwartet der Kunde mehr: Je höher das Budget, desto niedriger …" | "Je höher das Budget" twice in a row; "zu Beginn" is not when it happens (block "Maßnahmen und Budget", after story and Übung), and the Teamheft is already in the teams' hands in the story block. | "Vor der Auswahl eurer Maßnahmen wählt ihr ein Budget-Tier. Mit mehr Budget könnt ihr mehr oder stärkere Maßnahmen umsetzen. Dafür erwartet der Kunde mehr: Je höher das Budget, desto niedriger der Startwert der Kundenzufriedenheit (KZ)." | `sheets.budget.tier_intro` | B |
| Angriff 1–3 p2, Übung p2 | "…, gerundet (bei / ,5 weg von der Null, also zum größeren Betrag):" | The longer hint no longer fits the formula line; the break falls before ",5". | Put the hint on its own line: formula line ends after the unrounded box; next line "gerundet: [Feld]" with the note "Bei ,5 rundet ihr weg von der Null, also zum größeren Betrag." | attack-sheet template; `sheets.angriff.wave_kz_rounding` | B |
| Angriff 1 p1 | "Ein Mitarbeitender hat auf eine gefälschte E-Mail geklickt. … und ggf. exfiltriert … wird im Folgenden anhand eurer Sicherheitsmaßnahmen berechnet." | Angriff 2 and 3 were rewritten (MechTech named, "ermittelt ihr jetzt"), Angriff 1 was not: MechTech is not named, "ggf.", passive ending, "auf eine E-Mail geklickt". | "Ein Mitarbeitender von MechTech hat auf einen Link in einer gefälschten E-Mail geklickt. Die Angreifer versuchen, Ransomware zu platzieren, die Daten verschlüsselt und möglicherweise abzieht, um anschließend Lösegeld zu erpressen. Ob die Verschlüsselung tatsächlich gelingt und wie stark die Auswirkungen sind, ermittelt ihr jetzt anhand eurer Sicherheitsmaßnahmen." | `attacks.ransomware.revealed.narrative` | B |

Pass-1 fixes checked and found correct: Operative Unterstützung ("in dieser Welle"), KZ Events source ("ihr lest sie an den Eventkarten ab"), Init "Einmalig bei Einführung oder Level-Erhöhung", exfiltration narrative and cases, step-1 and step-3 texts, "der RoS" everywhere, Tier-Budget / Verfügbares Budget split, "Budget −20.000 €", Kurswechsel card in "ihr" form, Recovery labels, mail headers and closings, audit-mail bullets, "MechTech GmbH" in the Steckbrief, all changed clue quotes still match their story text word for word, colon capitalisation in the clue matrix, Probelauf sentence. No "Maßnahmenwechsel", no "gesamt" column, no Budget Review values in the Teamheft, no "Band", "Basiswert", "KZ Start", "die RoS", "Ereignis" (except log events on the M2 card, which is correct), no "du". "Sie" only in the two mails. "Arbeitsblatt" only in facilitator documents.

## spieler-teamheft.pdf

| Page | Quote | Problem | Suggested replacement | Source key | Cat. |
|---|---|---|---|---|---|
| 1 | "kreuzt je Schutzziel an, wie groß der Schaden fürs Geschäft wäre" | No hint that the Geschäftsführung can be asked (top finding 6). | add: "Könnt ihr eine Folge nicht einschätzen, fragt die Geschäftsführung von MechTech (die Spielleitung)." | `sheets.register.need_instruction` | A |
| 1 | example row "W1 Patientenakten", then the first empty row "W1" | The clinic example and the first real row carry the same label; the register example also points to "W1". | Label the example rows without a number ("Beispiel") or keep the number only in the real rows. | register template / `planspiel/booklet.py` | E |
| 2 | "Geplante Gesamtkosten = Summe Init-Kosten + Summe OPEX je Welle × 3 =" | Not related to the Tier-Budget; overspending rule unknown to players (top finding 8). The page also has no field for the chosen tier. | "Vergleicht die geplanten Gesamtkosten mit eurem Tier-Budget. Was am Ende übrig bleibt oder fehlt, bewertet das Budget Review." Optionally a field "Unser Tier:". | `sheets.teamheft.planning_instruction`; template | A |
| 3 | "Restbudget = Restbudget der Spalte davor + Event: Budget − OPEX dieser Welle − Init-Differenz netto − Event: OPEX." | Correct (recomputed against all three reference paths), but with the card value "OPEX −2.000 €" teams must subtract a negative number; many will subtract 12.000 again. | add after the formula: "Ein Minus bei Event: OPEX erhöht also das Restbudget." | `sheets.tracking.external_hint` | D |
| 3 and 5 | "Event: Budget", "Event: OPEX" (p3) vs "Budgetänderung durch Events", "OPEX-Änderung durch Events" (p5) | Same amounts, two names; p5 does not say they are the row sums of p3. | Keep the p5 labels and add the source in the grey line: "Summe der Zeile Event: Budget im Tracking-Bogen" / "Summe der Zeile Event: OPEX im Tracking-Bogen". | `sheets.teamheft.budget_event`, `sheets.teamheft.event_opex`, `sheets.tracking.row_external_budget`, `sheets.tracking.row_external_opex` | C |
| 3 and 5 | "KZ-Änderung Review" (p3) vs "KZ-Änderung Budget Review" (p5) | Two labels for one value. | "KZ-Änderung Budget Review" in both places | `sheets.tracking.row_kz_review` | C |
| 4 | "Die Summen übernehmt ihr von den vorherigen Seiten." | Top finding 3. | see above | `sheets.teamheft.ros_carry_hint` | A |
| 4 | "RoS = (Vermiedener Schaden − Eigene Kosten) ÷ Eigene Kosten" | No precision given; the facilitator's comparison uses two decimals. | add: "Rechnet den RoS auf zwei Nachkommastellen." | `sheets.ros.purpose` or a new hint key | A |
| 4 | "= 620.000 € − Summe der Schäden" | The amount is not explained. | grey line: "620.000 € ist der volle Schaden aller Angriffe ohne Maßnahmen" (amount from config through code) | `planspiel/booklet.py`; `sheets.labels.avoided_damage` | D |
| 4, 5 | rows "Eigene Kosten", "Summe der Schäden", "Vermiedener Schaden", "RoS", "Verfügbares Budget", "Gesamtkosten inkl. OPEX-Änderung", "Restbudget", "KZ-Änderung Budget Review" | The computed rows are a blue band without a value cell, while the input rows have a boxed cell; on p4 "Summe der Schäden" and "Vermiedener Schaden" share one band. The most important results have no visible field. | Give each computed row a value cell like the input rows and separate the two p4 rows. | Teamheft template | E |
| 5 | "Am Ende des Spiels rechnet ihr zuerst euer Restbudget aus." | Does not say that "Eigene Kosten" comes from the RoS page, nor that the result must match the last "Restbudget (laufend)" of the Tracking-Bogen (a free cross-check). | "Am Ende des Spiels rechnet ihr zuerst euer Restbudget aus; die eigenen Kosten übernehmt ihr von der RoS-Seite. Das Ergebnis muss zum letzten Restbudget im Tracking-Bogen passen. Die KZ-Änderung …" | `sheets.teamheft.review_intro` | A |

## spieler-so-funktioniert-eine-welle.pdf

| Page | Quote | Problem | Suggested replacement | Source key | Cat. |
|---|---|---|---|---|---|
| 1 | "Jede Welle läuft in dieser Reihenfolge ab" with the last box "Change-Fenster" | After the last wave there is no change window (Tracking-Bogen has two windows, the schedule says so). | add to the Change-Fenster text: "Nach der letzten Welle gibt es kein Change-Fenster." | `sheets.welle.window_rules` | D |
| 1 | "Passende Maßnahmen auf dem verlangten Level bringen einen Bonus." | A higher level qualifies too (sheet: "mindestens das genannte Level"). | "Passende Maßnahmen bringen einen Bonus, wenn sie mindestens das verlangte Level haben." | `sheets.welle.text_bonus` | D |
| 1 | section title "Backup & Recovery" | The measure is "Backup & Disaster Recovery" in the table right below. | "Recovery-Faktor" or "Backup & Disaster Recovery" | `sheets.backup_recovery.title` | C |

## uebung-welle-0.pdf

| Page | Quote | Problem | Suggested replacement | Source key | Cat. |
|---|---|---|---|---|---|
| 3 | "Restbudget (laufend) 96.000 € · 73.000 €", "KZ vor der Welle 98" | Top finding 5: practice budget and KZ start are not printed. | line above the table with both values from the config | `planspiel/practice.py`, practice template, new key under `practice` | A |
| 2, 3 | "KZ Events −4" in step 7 (p2); the event itself follows on p3; "ihr lest sie an den Eventkarten ab" | The Welle page puts events first, here the event comes after the step that uses it, and there is no Eventkarte in the Übung. | Move the "Events" box before step 1 (or to the top of p2), or add to the practice sheet: "Das Event dieser Übung steht auf der letzten Seite." | practice template; `sheets.angriff.events_hint` is reused | A |
| 1 | "wie groß der Schaden wird, wird im Folgenden … berechnet" | "wird, wird". | "Ob der Betrieb schnell wieder läuft und wie groß der Schaden ausfällt, zeigt die folgende Rechnung anhand der Sicherheitsmaßnahmen des Beispielteams." | `practice.narrative` | D |
| 2 | "Schaden vor Recovery [20.000] × (1 − r [10 %]) = [18.000 €]" | The first box has no "€" while every other amount has one; the formula line sits directly on the table edge. | Format the box value as "20.000 €"; add space above the formula. | `planspiel/practice.py` / template | E |

## angriff-1_ransomware.pdf, angriff-2_ot.pdf, angriff-3_exfil.pdf

| Page | Quote | Problem | Suggested replacement | Source key | Cat. |
|---|---|---|---|---|---|
| A3, 2 | step 5 is followed by "Schritt 6: KZ-Änderung dieser Welle" | Top finding 7: no word on Recovery. | "Bei diesem Angriff gibt es keine Recovery: Abgeflossene Daten lassen sich nicht zurückholen." | template + new key under `sheets.angriff` | A |
| A3, 1 | "Bei Exfiltration zählt Vertraulichkeit (C) am meisten (Diebstahl von Know-how), Integrität (I) ist relevant (Daten werden kopiert/weiterverarbeitet), Verfügbarkeit (A) bleibt oft weitgehend erhalten." | Three main clauses joined by commas; slash; "oft weitgehend". | "Bei Datenexfiltration zählt Vertraulichkeit (C) am meisten (Diebstahl von Know-how). Integrität (I) zählt mit, weil Daten kopiert und weiterverarbeitet werden; die Verfügbarkeit (A) bleibt meist erhalten." | `attacks.exfil.revealed.cia_rationale` | D |
| A2, 1; A3, 1 | "OT/IT-Segmentierung isoliert Produktion"; "Supply Chain Security schützt Schnittstellen" | Missing article; M8 is called "Supplier Security & Supply Chain" everywhere else. | "OT/IT-Segmentierung isoliert die Produktion"; "Supplier Security schützt die Schnittstellen zu Lieferanten" | `attacks.ot.revealed.bonus_reasons.M5`, `attacks.exfil.revealed.bonus_reasons.M8` | C |
| all, 2 | rounding hint line break | see pass-1 section | | | |
| A1, 1 | narrative | see pass-1 section | | | |

Numbers on the three sheets (weights, thresholds, caps, case values, slopes, bonuses) match the Spielleitungsheft.

## spieler-eventkarten.pdf

| Page | Quote | Problem | Suggested replacement | Source key | Cat. |
|---|---|---|---|---|---|
| 2 | "Ihr werdet von einem Softwarehersteller informiert: In einem von euch genutzten System wurde …" | Client-role leftover: the system belongs to MechTech, the players are consultants. | "Ein Softwarehersteller informiert MechTech: In einem dort genutzten System wurde eine kritische Schwachstelle entdeckt, die aktiv ausgenutzt werden könnte." | `events.kritische_schwachstelle.narrative` | C |
| 1 | "Senken oder Kündigen spart OPEX der folgenden Wellen" | After this window only one wave follows. | "Senken oder Kündigen spart OPEX in der letzten Welle" | `events.sparprogramm.rule` | D |
| 2 | "Event: Zum Abschluss" | The other cards read "Event in Welle …"; colon plus capital is odd. | "Event zum Abschluss" | `sheets.eventkarten.review_header` | D |
| 2 | "ab 75.000 € → KZ +27" / "Überzogen: −3 KZ je angefangene 10.000 €" | Value and unit in opposite order within one box. | "Überzogen: KZ −3 je angefangene 10.000 €" | `planspiel/cards.py` (rendering), `sheets.eventkarten.overspend_label` | D |
| 2 | "Für jede auf gehobenem Niveau betriebene Kontrolle gibt es einen Bonus" | "Kontrolle" for what the rule line and every other card call "Maßnahme". | "Für jede Maßnahme auf gehobenem Niveau gibt es einen Bonus auf eure Kundenzufriedenheit." | `events.exzellenz_bonus.narrative` | C |
| 1, 2 | sheet composition | Cards of different waves and the Budget Review card share a sheet (top finding 2). | cutting and sorting note in the Druckliste | `sheets.ablauf.print_intro` | A |
| 1 | Kurswechsel, last sentence | see pass-1 section | | | |

## spieler-massnahmenkarten.pdf

| Page | Quote | Problem | Suggested replacement | Source key | Cat. |
|---|---|---|---|---|---|
| 8 | "PIN-Schutz Pflicht, bei Verlust kann das Gerät aus der Ferne gelöscht werden." | Verb missing in the first clause. | "PIN-Schutz ist Pflicht, bei Verlust kann das Gerät aus der Ferne gelöscht werden." | `measures.M10.levels_simple.1` | D |
| 1 | "Init zahlt ihr einmal, wenn ihr die Maßnahme einführt oder ihr Level erhöht." | Does not say that raising a level costs only the difference (top finding 4). | "Init zahlt ihr einmal, wenn ihr die Maßnahme einführt. Erhöht ihr später das Level, zahlt ihr die Differenz zur Init des neuen Levels." | `sheets.karten.legend_costs` | A (counted with top finding 4) |

All pass-1 comma, dash and "z. B." fixes are in; the 30 cards show no overflow in the pages viewed (p1 to p3).

## Story documents

No new errors found in `spieler-anfrage-mail.pdf`, `spieler-audit-mail.pdf` and `spieler-zeitungsartikel.pdf`; headers, closings, relative dates ("im kommenden Quartal") and the rewritten bullets are correct, and the newspaper layout is clean.

| Document, page | Quote | Problem | Suggested replacement | Source key | Cat. |
|---|---|---|---|---|---|
| Steckbrief 2 | "die monatliche Backup-Sicherung" | Tautology. | "die monatliche Datensicherung" | `story.steckbrief.it_ot_landschaft.saas_cloud.bullets` (not the clue quote, which is the other bullet) | D |

## spielleitung-uebersicht.pdf

| Page | Quote | Problem | Suggested replacement | Source key | Cat. |
|---|---|---|---|---|---|
| 2 | Abschluss: "Die Teams rechnen das Budget Review und die RoS-Seite im Teamheft aus …" | Top finding 1: card not handed out, page order reversed. | see above | `sheets.ablauf.blocks.closing.direction` | A |
| 3 | "Die Liste zeigt für jede Datei, wie oft ihr sie druckt …" | Top finding 2: no cutting or sorting note. | see above | `sheets.ablauf.print_intro` | A |
| 14–16 | section names "Lage", "Einleitung", "Ticker" | These headings are not printed in the mails or the newspaper (the mails only have "UNSER ANLIEGEN:", "ERWARTETE NACHWEISE:" …), so a facilitator cannot find them. | "zweiter Absatz", "erster Absatz", "Schlagzeilenleiste" | `sheets.spielleitung.clue_section_anfrage_mail_lage`, `clue_section_audit_mail_einleitung`, `clue_section_zeitungsartikel` | A |
| 14 | column "Maßnahmen (Gewicht)" | The intro explains source, quote and reason, not the weight. | add: "Die Zahl in Klammern zeigt, wie stark der Hinweis auf die Maßnahme deutet (höher ist stärker)." | `sheets.spielleitung.clues_intro` | A |
| 1 | "In den beiden äußeren Fällen … im mittleren Fall …"; "Liegt die GR zwischen zwei Zeilen" | The Prüfzeilen list Fall 1, Fall 2, Fall 3, so "äußere" and "mittlere" do not map to positions; the GR steps are columns, not rows. | "In Fall 1 und Fall 2 sind Schaden und KZ fest, in Fall 3 lest ihr sie aus der Tabelle der ganzen GR-Schritte ab." / "Liegt die GR zwischen zwei ganzen Schritten, …" | `sheets.spielleitung.how_to` | D |
| 6, 8, 10, 13 | "Eigene OPEX dieser Welle", "Kosten des Change-Fensters danach" | The Tracking-Bogen the facilitator compares against says "OPEX dieser Welle" and "Init-Differenz netto". | Use the Teamheft labels. | `sheets.spielleitung.key_own_opex`, `sheets.spielleitung.key_window_cost` | C |
| 2 | "Change-Fenster mit dem Pflichttausch des Kurswechsels" | Third word for the swap next to "Maßnahmentausch" and "Tausch". | "… mit dem Maßnahmentausch des Kurswechsels" | `sheets.ablauf.blocks.wave_1.direction` | C |
| 12 | "Die Richtzeiten der Stufen füllen zusammen …" | "Stufe" is now the damage scale (gering / mittel / hoch); here it means the four debriefing stages. | "Die Richtzeiten der Phasen …" | `sheets.debrief.intro` | C |
| 12 | "Welche Maßnahme würdet ihr in eurem Unternehmen zuerst umsetzen" | Student teams usually have no company; also collides with the client-role decision. | "Welche Maßnahme würdet ihr in einem echten Unternehmen zuerst umsetzen, und warum?" | `sheets.debrief.stages.application.questions` | D |
| 4 | "müssen Satz für Satz geprüft werden" | Reads as sentence by sentence. | "müssen Datensatz für Datensatz geprüft werden" | `sheets.cheatsheet.cases.data_trust.case` | D |
| 4 | "Ein Audit findet Mängel, die nachgebessert werden müssen." with Ziel C | Still the one case whose protection goal is not evident (pass 1 flagged it; only the voice was changed). Worth a decision, not a certain error. | Either reword towards confidentiality ("Im Audit fällt auf, dass vertrauliche Daten unzureichend geschützt sind; das muss nachgebessert werden.") or drop the case. | `sheets.cheatsheet.cases.audit_findings.case` | D |
| 5, 7, 9 | "KZ-Steigung je GR-Punkt × 2" | A slope with a multiplication sign. | "KZ-Steigung je GR-Punkt: +2" | `planspiel/master.py` (rendering), `sheets.spielleitung.param_slope` | D |
| 11 | "RoS −0,34 · −0,33 · 0,06" | Positive value without a sign while KZ values are signed. | "+0,06" | `planspiel/fmt.py` / `master.py` | D |
| 6, 8, 10 | "Eventplan der Welle: Angriff 1: Ransomware" | Double colon in a heading. | "Eventplan zu Angriff 1: Ransomware" | master template, `sheets.spielleitung.events_title` | D |
| 1, 13 | "Inhalt" without page numbers; "Lösungsschlüssel der Übungswelle" on p13 | A 16-page booklet used live needs page numbers in the contents; the Übung key is needed at minute 50 but sits behind the debriefing. | Add page numbers; move the Übung key before "Angriff 1". | master template | E |

All reference-path values were recomputed by hand from the cards and the event cards (CIA sums, E-Wert, bonus, GR, damage, KZ, event KZ, OPEX, window costs, Restbudget, own costs, RoS, Final-Index for all three tiers): no deviation. The Restbudget formula of the Tracking-Bogen reproduces every "Restbudget nach der Welle".

## spielleitung-was-ist-neu.pdf

| Page | Quote | Problem | Suggested replacement | Source key | Cat. |
|---|---|---|---|---|---|
| 1 | "kostet das Überziehen am Ende −3 KZ je angefangene 10.000 €" | "kostet minus" is a double negative. | "… kostet das Überziehen am Ende 3 KZ je angefangene 10.000 € über dem Budget" (sign comes from code) or "bringt … −3 KZ" | `sheets.was_neu.rules.overspend.text`, `planspiel/was_neu.py` | D |
| not printed now | field label "Basis-CIA" | Decided term is "Basisschutz"; it would surface as soon as a base value changes. | "Basisschutz" | `sheets.was_neu.fields.base_cia` | C |
| 1 | Kurswechsel, Final-Index, two row heads | see pass-1 section | | | |

The page still fits on one sheet and is dense but readable. "ersetzt den alten Begriff der MHP-Runde" does not name the old term; that follows from the decision that the retired term must not appear and is not counted.

## spielleitung-probelauf.pdf

No findings. Block names, durations and minute spans match the Ablaufplan.

## Count per category

| Category | Findings |
|---|---|
| A. Breaks play, or an instruction/field without a source | 13 |
| B. Pass-1 fixes that went wrong or stayed incomplete | 8 |
| C. Terminology leftovers | 10 |
| D. Language and clarity | 19 |
| E. Layout | 4 |
| Total | 54 |

Counting notes: the cutting and sorting note appears in two tables (Eventkarten, Spielleitungsheft) and is counted once; the Maßnahmenkarten legend row is the category-A entry of top finding 4, whose tracking-page half is counted under B.
