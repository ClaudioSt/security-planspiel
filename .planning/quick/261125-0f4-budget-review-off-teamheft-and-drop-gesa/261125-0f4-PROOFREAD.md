# Proofreading report RC5 (2026-11-25)

# Proofreading report: German print material (`final_documents/generated/`, 15 PDFs)

Read-only; nothing edited. All 15 PDFs were extracted with pypdf and compared against `content/texte.toml`. Source keys refer to `C:/Users/Claudio/Documents/Git/security_game/security-planspiel/content/texte.toml` unless marked `clues.toml`, template or code. The in-flight items (Teamheft p5 Budget Review tables, "gesamt" column, "Maximumprinzip") are left out.

Two cautions for whoever fixes these:
- Several story sentences are literal clue quotes in `content/clues.toml`; changing them means changing the quote there too. They are marked "(clue quote)".
- Suggested replacements avoid new digits because of the digit lint; where an example with digits would help, that is noted.

## Top findings

1. **Operative Unterstützung contradicts itself** (Eventkarten p1). The narrative says "Für die nächste Runde wird der Betrieb günstiger", the rule says "in dieser Welle aktiv", and the Lösungsschlüssel books the −12.000 € in Welle 1. "Runde" is also not a game term. Key: `events.operative_unterstuetzung.narrative`.
2. **"KZ Events … die Spielleitung nennt sie euch"** (all attack sheets, step 7; Übung p2). The event KZ depends on each team's own measures (OEM-Audit, Kritische Schwachstelle, Exzellenz-Bonus), the teams get the event cards, and the Spielleitungsheft only has event KZ for the reference paths. As written, teams will wait for a number nobody has. Key: `sheets.angriff.events_hint`.
3. **Init "Einmal zu Spielbeginn"** (Teamheft p2, cost table) contradicts the paragraph below it, the Maßnahmenkarten legend and the Change-Fenster rules (Init is also due when adding or raising a measure later). Key: `sheets.budget.init_when`.
4. **Exfiltration narrative contradicts its own cases** (Angriff 3 p1). The data "wurden … abgegriffen" and "werden im Darknet angeboten", then "Ob (und wie stark) der Abfluss gelingt", and Fall 2 says "Ihr verhindert die Exfiltration vollständig". Key: `attacks.exfil.revealed.narrative`.
5. **"berechnet euren Gesamtschutz über alle Schutzziele"** (attack sheets and Übung, step 1). The table wants one sum per column (C, I, A), not one total across the goals. Key: `sheets.angriff.cia_table_instruction`.
6. **"Der Bonus wird zur Gesamtreduktion addiert"** (step 3). Step 4 defines Gesamtreduktion = E-Wert + Gesamtbonus, so the bonus is added to the E-Wert. Key: `sheets.angriff.bonus_intro`.
7. **Rounding rule is phrased three ways, two of them hard to understand**: "ab ,5 vom Betrag aufrunden" (players) and "halbe Werte vom Betrag weg" (Was ist neu). For −2,5 students will not know whether −2 or −3 is meant. Keys: `sheets.angriff.wave_kz_rounding`, `sheets.was_neu.rules.rounding`.
8. **Grammar and address errors on player pages**: "Trag die folgenden Werte ein" (singular), "So liest du eine Maßnahmenkarte" (du instead of ihr), "kein Recovery" next to "starke Recovery", "Zentrale AD", five missing commas on the Maßnahmenkarten, "Audit Checkliste", "Automotive Zulieferer".
9. **"der RoS" and "die RoS" are mixed** across Teamheft, Welle page, Spielleitungsheft and Was ist neu.
10. **Budget has four names**: "Verfügbares Budget" means the Tier-Budget on Teamheft p2 but Tier-Budget plus event change on p5; the event card says "Gesamtbudget", the tracking sheet "Event: Budget".
11. **Kurswechsel card**: narrative and rule say the same thing twice, the rule switches to third person ("jedes Team", "das Team") on a player card, and the dependency sentence is hard to parse. Key: `events.kurswechsel`.
12. **Role confusion**: players are MHP consultants ("euch Beratern"), yet the attack sheets say "Euer Unternehmen", "In eurer Produktionssteuerung", "Eure Daten werden im Darknet angeboten".

---

## spieler-teamheft.pdf

| Page | Quote | Problem | Suggested replacement | Source key |
|---|---|---|---|---|
| 1 | "Welches Schutzziel trifft das Risiko vor allem (Hauptziel), und was hieße der Schaden fürs Geschäft?" | Subject and object are ambiguous; "was hieße der Schaden" is clumsy and does not match the column head "Folge fürs Geschäft". | "Welches Schutzziel wäre vor allem verletzt (Hauptziel), und welche Folge hätte das fürs Geschäft?" | `sheets.register.instruction` |
| 1 | "Das Band des Risikos lest ihr in der Tabelle ab" | "Band" is never introduced to players (the table above says "Stufe" and "gering/mittel/hoch"); "in der Tabelle" does not say which table. | "Die Schadensstufe des Risikos lest ihr oben in der Schutzbedarfstabelle ab: Zeile des Werts, Spalte des Hauptziels." Then use Stufe (or Band) consistently in `review_hint` and the Spielleitung cheat sheet. | `sheets.register.instruction`, `sheets.register.review_hint`, `sheets.cheatsheet.*` |
| 1 | "Vergebt jeden Rang genau einmal, das wichtigste Risiko zuerst:" | "zuerst" does not say that the top rank is the lowest number. | "Vergebt jeden Rang genau einmal; der erste Rang ist das wichtigste Risiko:" | `sheets.register.rank_hint` |
| 1 | "wenn Vertraulichkeit (C), Integrität (I) oder Verfügbarkeit (A) verletzt würden" | With "oder" the verb is singular. | "… verletzt würde" | `sheets.register.need_instruction` |
| 1 | "Rückblick im Abschluss: Euer Band ist … Liegt es höher als euer Band, habt ihr unterschätzt; …" | One paragraph with a nested semicolon-colon chain; "es" is far from its referent; the central instruction is very hard to follow. | Split into steps: "Rückblick im Abschluss. Erstens: Eure Stufe ist das Kreuz in der Schutzbedarfstabelle (Zeile des Werts, Spalte des Hauptziels). Zweitens: Getroffen ist ein Risiko, wenn ihr es in der Realitätscheck-Zeile eines Angriffsblatts genannt habt. Drittens: Sucht die Stufe, in der der volle Schaden dieses Angriffs liegt (Schaden im ersten Fall des Angriffsblatts); bei mehreren Angriffen zählt der größte. Liegt diese Stufe höher als eure, habt ihr das Risiko unterschätzt; liegt sie niedriger, überschätzt; ist sie gleich, lagt ihr richtig. Hat kein Angriff das Risiko getroffen, gilt es als überschätzt." | `sheets.register.review_hint` |
| 1 | "Realitätscheck-Zeile eines Arbeitsblatts" | Players know the sheet only as "Angriffsblatt" (Welle page, Tracking-Bogen, Maßnahmenkarten); "Arbeitsblatt" is the facilitator term. | "eines Angriffsblatts" | `sheets.register.review_hint` |
| 1 | "behandeln: der Schaden wäre zu hoch" | A full sentence after a colon starts with a capital. | "behandeln: Der Schaden wäre zu hoch" | `sheets.register.example.decision` |
| 2 | "das euch Beratern … zur Verfügung steht. Mit dem Budget müsst ihr Maßnahmen initiieren und betreiben." | Masculine only; "initiieren" is unusual, elsewhere "einführen". | "Das Budget ist das Geld, das euch als Beratungsteam für eure Maßnahmen zur Verfügung steht. Daraus bezahlt ihr die Einführung und den Betrieb der Maßnahmen." | `sheets.budget.intro` |
| 2 | "Einmal zu Spielbeginn" | Contradiction, see top finding 3. | "Einmalig, wenn ihr die Maßnahme einführt oder ihr Level erhöht" | `sheets.budget.init_when` |
| 2 | "Gleichzeitig sind die Erwartungen höher, was sich in einem entsprechend angepassten Startwert der Kundenzufriedenheit (KZ) widerspiegelt. Legt daher zuerst … fest, bevor …" | Does not say the direction (a higher budget means a lower KZ start); "zuerst … bevor" is redundant; "mehr bzw. stärkere". | "Je höher euer Budget, desto mehr oder stärkere Maßnahmen könnt ihr umsetzen. Dafür erwartet der Kunde mehr: Je höher das Budget, desto niedriger euer Startwert der Kundenzufriedenheit (KZ). Legt euer Budget-Tier fest, bevor ihr Maßnahmen auswählt." | `sheets.budget.tier_intro` |
| 2 | "wählt ihr zu Beginn ein Budget-Tier" | The Spielleitungsheft says "Die Teams verhandeln ihr Budget-Tier". Neither document says with whom or how. | Use one verb in both places and add one sentence for the facilitator on how the negotiation runs. | `sheets.budget.tier_intro`, `sheets.ablauf.blocks.measures_budget.direction` |
| 2 | "In diesem Sheet plant und trackt ihr euer Budget über alle Wellen. … auf ein höheres Level upgraded." | "Sheet" and "trackt" are jargon, and tracking happens on the next page; "upgraded" is misspelled (would be "upgradet"); the legend says "hebt". | "Auf dieser Seite plant ihr euer Budget für alle Wellen. Init-Kosten fallen einmalig an, wenn ihr eine Maßnahme einführt oder auf ein höheres Level hebt. OPEX fallen in jeder Welle an, in der die Maßnahme aktiv ist." | `sheets.budget.anticipated_sum_intro` |
| 2 | "Antizipierte Summe" | Stilted. | "Geplante Gesamtkosten" | `sheets.labels.anticipated_sum` |
| 2 and 5 | "Verfügbares Budget" | Two meanings, see top finding 10. | p2 table head: "Tier-Budget"; keep "Verfügbares Budget" only for the p5 sum. | `sheets.labels.available_budget` (used twice in `planspiel/booklet.py`, lines 300 and 334) |
| 3 | "Eigene Kosten (zählen für den RoS)" and p4 "Die RoS ist …" | Mixed gender, see section "Cross-document terminology". | "der RoS" everywhere | `sheets.tracking.block_own`, `sheets.ros.purpose` and others |
| 3 | "bei Event: OPEX gilt der Wert je aktive Maßnahme mal der Zahl eurer aktiven Maßnahmen" | Clumsy; case differs from the event card ("je aktiver Maßnahme"). | "bei Event: OPEX rechnet ihr den Wert je aktiver Maßnahme mal die Zahl eurer aktiven Maßnahmen" | `sheets.tracking.external_hint` |
| 3 | "Je Änderung das Level nach dem Fenster eintragen, …" | Infinitive instead of the ihr-imperative used everywhere else; it is unclear what to enter for a cancelled measure. | "Tragt je Änderung das Level nach dem Fenster ein (gekündigt: Level null), bei einer Erhöhung auch Δ Init; beim Senken und Kündigen bleibt Δ Init leer. Unveränderte Maßnahmen bleiben leer. Ihr dürft beliebig viele Änderungen vornehmen." | `sheets.tracking.window_intro` |
| 3 | "Init-Differenz netto: in die Spalte der Welle davor." | Cryptic; "davor" has no reference point. | "Tragt die Init-Differenz netto oben im Tracking-Bogen in die Spalte der Welle ein, nach der das Fenster liegt." | `sheets.tracking.next_wave_hint` |
| 4 | "Trag die folgenden Werte ein:" | Singular imperative; players are "ihr". | "Tragt die folgenden Werte ein:" | `sheets.ros.instruction` |
| 4 | "Gesamt OPEX Kosten" next to "Gesamt Init-Kosten" | Missing hyphens, inconsistent. | "Gesamt-OPEX" and "Gesamt-Init-Kosten" (or "OPEX gesamt" / "Init-Kosten gesamt") | `sheets.labels.total_opex`, `sheets.labels.total_init` |
| 4 | Title "Return on Security und Budget Review" | The page holds only the RoS; Budget Review has its own title on p5. May belong to the in-flight change. | "Return on Security" | `sheets.teamheft.ros_title` |
| 5 | "Ein Minus bei der OPEX-Änderung ist eine Entlastung: Sie senkt die Kosten und steht deshalb bei den Kosten." | "steht deshalb bei den Kosten" reads as circular. | "Ein Minus bei der OPEX-Änderung ist eine Entlastung. Tragt sie trotzdem in der Kostenzeile ein: Dort senkt sie eure Gesamtkosten." | `sheets.teamheft.sign_hint` |

## spieler-so-funktioniert-eine-welle.pdf

| Page | Quote | Problem | Suggested replacement | Source key |
|---|---|---|---|---|
| 1 | "gerundet (ab ,5 vom Betrag aufrunden)" | Hard to understand, see top finding 7. | "gerundet (bei ,5 weg von der Null, also zum größeren Betrag)"; an example such as "−2,5 wird −3" would help most but needs digit allowlist entries. | `sheets.angriff.wave_kz_rounding` |
| 1 | "Ihr dürft Level hoch oder runter setzen, Maßnahmen kündigen und neue hinzufügen, beliebig viele." | "hoch oder runter setzen" is colloquial and misspelled; "beliebig viele" dangles. | "Ihr dürft beliebig viele Änderungen vornehmen: Level erhöhen oder senken, Maßnahmen kündigen und neue hinzufügen." | `sheets.welle.window_rules` |
| 1 | "Greift eure Backup- und Recovery-Maßnahme, senkt der Faktor r …" | "Greift" is vague; the measure has a name in the table below. | "Habt ihr die Maßnahme Backup & Disaster Recovery, senkt der Faktor r den Schaden (Tabelle unten)." | `sheets.welle.text_recovery` |
| 1 | "Event: Nach jeder Welle mit Recovery-Option" | Recovery is a calculation step, not an event; the same page says events act on KZ, Budget and OPEX, not on damage. | "Schritt Recovery: in jeder Welle, die Recovery zulässt" | `sheets.backup_recovery.subtitle` |
| 1 | "Nach einem Angriff mit entstandenem Schaden prüft ihr, ob … Falls überhaupt ein Schaden entstanden ist, … finanziellen Impact senken könnt." | Says the same condition twice; "finanziellen Impact" instead of "Schaden". | "Ist bei einem Angriff Schaden entstanden, entscheidet eure Backup- und Recovery-Fähigkeit, wie stark ihr ihn senken könnt." | `sheets.backup_recovery.narrative` |
| 1 | "kein Recovery" / "starke Recovery" / "teilw. Recovery" | Gender mismatch within one table; needless abbreviation. | "keine Recovery", "Basis-Recovery", "teilweise Recovery", "starke Recovery" | `sheets.backup_recovery.level_labels` |
| 1 | "Für den RoS zählen …" | RoS gender, see below. | keep "den RoS", align the others | `sheets.welle.ros_note` |

## uebung-welle-0.pdf

| Page | Quote | Problem | Suggested replacement | Source key |
|---|---|---|---|---|
| 1 | Narrative first, then "Bevor die erste Welle beginnt, rechnet ihr gemeinsam ein Beispiel durch." | The framing sentence comes after the incident text. | Put the intro before the narrative. | template (practice sheet order) |
| 1–2 | "Eure gewählten Maßnahmen …", "Tragt die CIA-Werte eurer Maßnahmen ein", "Erreicht ihr die Obergrenze, wehrt ihr den Angriff vollständig ab", "Berechnet Schaden und KZ" | The intro says all fields are prefilled and belong to a Beispielteam, yet the reused sheet texts tell the players to enter and compute their own values; "Angriff" is used for a failure. | Either give the practice sheet its own step texts ("Das Beispielteam trägt … ein") or add one line to `practice.intro`: "Die Anleitungstexte sind dieselben wie später auf euren Angriffsblättern." | `practice.intro`; reused `sheets.angriff.*` (code: `planspiel/practice.py`) |
| 1 | "berechnet euren Gesamtschutz über alle Schutzziele" | See top finding 5. | "Tragt die CIA-Werte eurer Maßnahmen ein und bildet je Schutzziel die Summe." | `sheets.angriff.cia_table_instruction` |
| 1 | "Er zeigt, wie gut ihr gegen diesen Angriffstyp geschützt seid:" | The colon leads into an explanatory paragraph, not the formula. | End with a full stop. | `sheets.angriff.e_value_intro` |
| 1 | "mindestens auf dem richtigen Level habt. Der Bonus wird zur Gesamtreduktion addiert." | "richtigen" is vague (table says "Ab Level", Welle page says "verlangten"); second sentence is imprecise, see top finding 6. | "Zusätzlich bekommt ihr einen Bonus für jede passende Maßnahme, die mindestens das genannte Level hat. Gesamtbonus und E-Wert ergeben zusammen die Gesamtreduktion." | `sheets.angriff.bonus_intro` |
| 1 | "Geprüfte Cloud-Einstellungen: die Ersatzablage … steht sofort bereit" | Capital after colon (full sentence). | "… Cloud-Einstellungen: Die Ersatzablage …" | `practice.bonus_reasons.M9` |
| 3 | "Wirkung des Ereignisses auf das Beispielteam" under the heading "Events" | Event and Ereignis mixed on one page. | "Wirkung des Events auf das Beispielteam" | `practice.event_result` |

## angriff-1_ransomware.pdf, angriff-2_ot.pdf, angriff-3_exfil.pdf

| Page | Quote | Problem | Suggested replacement | Source key |
|---|---|---|---|---|
| all, 1 | "Euer Unternehmen startet je Schutzziel mit einem Basiswert." | Role confusion (players are consultants); "Basiswert" is called "Basisschutz" in the table right below. | "MechTech startet je Schutzziel mit einem Basisschutz. Eure gewählten Maßnahmen erhöhen ihn." | `sheets.angriff.start_values_intro` |
| all, 1 | step 1 and step 3 texts | See Übung rows above (same keys). | as above | `sheets.angriff.cia_table_instruction`, `sheets.angriff.bonus_intro` |
| all, 2 | "KZ Events ist die KZ-Wirkung aller Events dieser Welle zusammen; die Spielleitung nennt sie euch." | See top finding 2. | "KZ Events ist die KZ-Wirkung aller Events dieser Welle zusammen; ihr lest sie an den Eventkarten ab." If the facilitator really is meant to compute it per team, the Spielleitungsheft needs that instruction. | `sheets.angriff.events_hint` |
| all, 2 | "gerundet (ab ,5 vom Betrag aufrunden)" | See top finding 7. | as on the Welle page | `sheets.angriff.wave_kz_rounding` |
| A1, 1 | "zählen Vertraulichkeit (C) und Integrität (I) stärker (Datendiebstahl + Verschlüsselung), Verfügbarkeit (A) ist häufig die Folge daraus" | Comparative without a comparison; "+" in prose. | "Bei Ransomware zählen Vertraulichkeit (C) und Integrität (I) am stärksten (Datendiebstahl und Verschlüsselung); der Ausfall der Verfügbarkeit (A) ist meist die Folge daraus." | `attacks.ransomware.revealed.cia_rationale` |
| A1, 1 | "Geschulte Mitarbeiter erkennen Phishing" | The M6 card says "Mitarbeitende" in its focus line and "Mitarbeiter" in the description. | Use "Mitarbeitende" throughout. | `attacks.ransomware.revealed.bonus_reasons.M6`, `measures.M6.description`, `measures.M10.description`, `attacks.ransomware.revealed.narrative` |
| A2, 1 | "In eurer Produktionssteuerung … Die Angreifer zielen darauf, die Fertigung zu stören bzw. stillzulegen. … ermittelt ihr im nächsten Schritt" | Role confusion; "zielen darauf" lacks "ab"; "bzw."; the calculation takes all steps, not the next one. | "In der Produktionssteuerung von MechTech wurde eine Schwachstelle ausgenutzt. Die Angreifer zielen darauf ab, die Fertigung zu stören oder stillzulegen. Ob die Produktion wirklich ausfällt und wie stark die Auswirkungen sind, ermittelt ihr jetzt anhand eurer Sicherheitsmaßnahmen." | `attacks.ot.revealed.narrative` |
| A2, 1 | "C und I sind hier nachgelagert" | Jargon. | "C und I zählen hier weniger." | `attacks.ot.revealed.cia_rationale` |
| A3, 1 | "wurden über Wochen hinweg … abgegriffen. … informiert euch: Eure Daten werden im Darknet angeboten. Ob (und wie stark) der Abfluss gelingt …" | See top finding 4; role confusion; parenthesis. | "Über einen kompromittierten Lieferanten-Zugang versuchen Angreifer seit Wochen, vertrauliche Konstruktionsdaten von MechTech abzugreifen. Das Bundesamt für Sicherheit in der Informationstechnik (BSI) warnt: Im Darknet werden angeblich Daten von MechTech angeboten. Ob und wie viel tatsächlich abgeflossen ist und welche Folgen daraus entstehen, ermittelt ihr jetzt anhand eurer Sicherheitsmaßnahmen." | `attacks.exfil.revealed.narrative` |
| A3, 1 | "(IP-Diebstahl)" | Students may read IP as IP address. | "(Diebstahl von Know-how)" | `attacks.exfil.revealed.cia_rationale` |
| A3, 2 | "Ihr reduziert die Auswirkungen teilweise." | The other two sheets say "Ihr mindert …". | "Ihr mindert die Auswirkungen teilweise." | `attacks.exfil.revealed.case_3` |

## spieler-massnahmenkarten.pdf

| Page | Quote | Problem | Suggested replacement | Source key |
|---|---|---|---|---|
| 1 | "So liest du eine Maßnahmenkarte" | "du", while the same legend continues with "eurem", "ihr". | "So lest ihr eine Maßnahmenkarte" | `sheets.karten.legend_title` |
| 1 | "Zentrale AD, MFA für Admins" | Active Directory is neuter. | "Zentrales AD, …" | `measures.M1.levels_desc.1` |
| 1 | "klare Rollen wer was darf" | Missing comma. | "klare Rollen, wer was darf" | `measures.M1.levels_simple.2` |
| 3 | "ohne regelmäßige Tests ob die Wiederherstellung funktioniert" | Missing comma. | "… Tests, ob die Wiederherstellung funktioniert" | `measures.M4.levels_simple.1` |
| 3 | "monatlich wird geprüft ob Wiederherstellung klappt" | Missing comma and article. | "monatlich wird geprüft, ob die Wiederherstellung klappt" | `measures.M4.levels_simple.2` |
| 7 | "Automatische Prüfung ob Cloud-Einstellungen …" | Missing comma. | "Automatische Prüfung, ob die Cloud-Einstellungen …" | `measures.M9.levels_simple.2` |
| 8 | "kontrolliert welche Apps genutzt werden dürfen" | Missing comma. | "kontrolliert, welche Apps …" | `measures.M10.description` |
| several | "haben - wie ein digitaler Türsteher", "Sicherheitssysteme - erkennt", "getrennt - selbst Hacker", "Produktion - nur explizit" | Hyphen with spaces used as a dash. | Use the en dash "–". | `measures.M1.description`, `measures.M3.levels_simple.3`, `measures.M4.levels_simple.3`, `measures.M5.levels_simple.2` |
| 2, 7 | "z.B." | Missing space. | "z. B." | `measures.M2.levels_simple.2`, `measures.M9.levels_desc.2` |
| 5 | "Vulnerability-Scans (quartal)" / "wöchentliche Scans, Tool" | "quartal" is not a word here; "Tool" at the end says nothing. | "(quartalsweise)" / "Risk-based Patching (CVSS), wöchentliche Scans mit Tool-Unterstützung" | `measures.M7.levels_desc.2`, `measures.M7.levels_desc.3` |
| 6 | "Backup-Lieferanten für kritische Teile" | "Backup" collides with measure M4. | "Ersatzlieferanten für kritische Teile" | `measures.M8.levels_simple.3` |
| 5 | "Pflicht-Schulung" | Written as one word. | "Pflichtschulung" | `measures.M6.levels_desc.1` |

## spieler-eventkarten.pdf

| Page | Quote | Problem | Suggested replacement | Source key |
|---|---|---|---|---|
| 1 | Kurswechsel, narrative: "… Daher zählt nur die Kostendifferenz." followed by rule: "Die Geschäftsführung richtet die Sicherheitsstrategie neu aus. …" | The rule repeats the narrative's first sentence; "bestehende Investitionen teilweise weiterverwenden" and "nur die Kostendifferenz" are vaguer than the rule and invite a wrong reading. | Narrative: "Nach den neuesten Erkenntnissen richtet die Geschäftsführung die Sicherheitsstrategie neu aus. Ihr müsst eine Maßnahme austauschen; der Kunde beteiligt sich an den Kosten." Drop the first sentence of the rule. | `events.kurswechsel.narrative`, `events.kurswechsel.rule` |
| 1 | Kurswechsel rule: "führt jedes Team …", "zahlt das Team", "senkt das Team … passend ab" | Third person on a player card (all other cards use "ihr"); the dependency sentence ("Abhängige Maßnahmen der wegfallenden Maßnahme") is hard to parse; very dense block. | "Im Change-Fenster nach dieser Welle tauscht ihr genau eine Maßnahme: Eine in dieser Welle aktive Maßnahme fällt ganz weg, eine in dieser Welle nicht aktive kommt auf einem Level eurer Wahl hinzu. Der Kunde übernimmt die Init-Kosten der neuen Maßnahme bis zur Höhe der Init-Kosten der wegfallenden (auf ihrem Level in dieser Welle). Einen Mehrbetrag zahlt ihr; ist die neue Maßnahme günstiger, gibt es keine Erstattung. Braucht eine andere Maßnahme die wegfallende als Voraussetzung, senkt ihr sie im selben Fenster auf ein Level ohne diese Voraussetzung. Ist in dieser Welle keine oder jede Maßnahme aktiv, entfällt der Tausch. Weitere Levelwechsel im selben Fenster bleiben erlaubt." | `events.kurswechsel.rule` |
| 1 | "Für die nächste Runde wird der Betrieb günstiger" | See top finding 1; also "Rahmenvertrag bzw. Shared-Service". | "Ein zentraler Rahmenvertrag senkt in dieser Welle die laufenden Betriebskosten eurer Security-Maßnahmen, ohne dass ihr an Leistung verliert." | `events.operative_unterstuetzung.narrative` |
| 1 | "ein konzernweites Sparprogramm" | MechTech is a mid-sized GmbH with one site. | "ein unternehmensweites Sparprogramm" | `events.sparprogramm.narrative` |
| 1 | "Gesamtbudget −20.000 €" | Third name for the budget, see top finding 10. | "Budget" or "Tier-Budget" | `sheets.eventkarten.total_budget` |
| 1 | "ob ihr „Best-in-Class“ seid - sondern ob ihr …" | Hyphen used as a dash where a comma belongs. | "Im Audit zählt nicht, ob ihr „Best-in-Class“ seid, sondern ob ihr die grundlegenden Kontrollen verlässlich umgesetzt habt." | `events.oem_audit.narrative` |
| 1 | "Audit Checkliste" | Missing hyphen (the clue matrix writes "Audit-Checkliste"). | "Audit-Checkliste" | `events.oem_audit.checklist_heading` |
| 2 | "Support-Tickets und Frust - intern entsteht …" | Hyphen as dash. | "… und Frust – intern entsteht …" | `events.nervige_authentifizierung.narrative` |
| 2 | "Wenn M1 (IAM/PAM) mindestens auf Level 2 und M6 (…) auf Level 0" | Measure names are written "M1 – IAM/PAM" on every other card; "auf Level 0" for "not active" is unexplained here. | Use the same name format; "und M6 – Security Awareness & Training nicht aktiv (Level 0)". | code (event condition rendering), `sheets.eventkarten.level_equals` |

## Story documents (spieler-anfrage-mail, spieler-audit-mail, spieler-zeitungsartikel, spieler-unternehmenssteckbrief)

| Document, page | Quote | Problem | Suggested replacement | Source key |
|---|---|---|---|---|
| Anfrage-Mail 1 | `An: "MHP Cyber Security <cyber-security@mhp.com>"` | The closing quote encloses the address; the Von line has it right. Same in the Audit-Mail. | `"MHP Cyber Security" <cyber-security@mhp.com>` / `"Dr. Thomas Weber" <t.weber@mechtech-gmbh.de>` | `story.anfrage_mail.kopf.an`, `story.audit_mail.kopf.an` |
| Anfrage-Mail 1 | "Ehrlich gesagt sind wir … Ehrlich gesagt wissen wir auch nicht genau …" | Same opener in two consecutive sentences. | Second sentence: "Offen gestanden wissen wir auch nicht genau, wer …" (clue quote starts at "wissen wir auch nicht genau", so it stays intact). | `story.anfrage_mail.lage.paragraphs` |
| Anfrage-Mail 1 | "IHRE AUFGABE:" | A prospective client does not assign a "task" in an inquiry; reads like a game instruction inside the mail. | "UNSER ANLIEGEN:" | `story.anfrage_mail.aufgabe.heading` |
| both mails | "Mit freundlichen Grüßen," | No comma after the closing formula in German. | "Mit freundlichen Grüßen" | `story.anfrage_mail.gruss.lines`, `story.audit_mail.gruss.lines` |
| Audit-Mail 1 | "IAM/ PAM" | Stray space. | "IAM/PAM" | `story.audit_mail.nachweise.bullets` |
| Audit-Mail 1 | "behalten wir uns vor: Aufträge zurückzustellen (bis Maßnahmen umgesetzt) / Vertragsstrafen bei Sicherheitsvorfällen / Im Wiederholungsfall: Beendigung …" | The three bullets do not continue the lead-in the same way. | "Aufträge zurückzustellen, bis die Maßnahmen umgesetzt sind" / "bei Sicherheitsvorfällen Vertragsstrafen zu verhängen" / "im Wiederholungsfall die Geschäftsbeziehung zu beenden" | `story.audit_mail.konsequenzen.bullets` |
| Audit-Mail 1 | "Tel: +49-711-12345\| k.hoffmann@…" | Missing full stop and space. | "Tel.: +49-711-12345 \| k.hoffmann@…" | `story.audit_mail.fusszeile.lines` |
| Audit-Mail, Zeitungsartikel | "in Q2/2026", "ab Q2/2026", "Kassel, 10.01.2026" | The story announces a future audit for a quarter that is already past (page stamp reads 2026-11-24). | Move the story dates forward or make them relative ("im kommenden Quartal"); the Audit-Mail subject is also the document title used in the clue matrix. | `story.audit_mail.doc_title`, `story.audit_mail.einleitung`, `story.zeitungsartikel.*` |
| Zeitungsartikel 1 | "Ein mittelständischer Automotive Zulieferer" | Missing hyphen. | "Automotive-Zulieferer" | `story.zeitungsartikel.bericht_vorfall.lead` |
| Zeitungsartikel 1 | "so der Geschäftsführer unter der Bedingung der Anonymität" | Calque, clumsy. | "so der Geschäftsführer, der anonym bleiben möchte" (the quoted sentence itself is a clue quote and stays) | `story.zeitungsartikel.bericht_vorfall.ablauf.paragraphs` |
| Zeitungsartikel 1 | "innerhalb von 2 Stunden" | Small number as digit in running newspaper text. | "innerhalb von zwei Stunden" | same key |
| Steckbrief 1–2 | "MECHTECH GmbH" | The mails, the footer and the facilitator texts write "MechTech". | "MechTech GmbH" in title and body (the title appears in the clue matrix) | `story.steckbrief.doc_title`, `story.steckbrief.kurzprofil.text` |
| Steckbrief 2 | "Policies/Standards: derzeit nicht als dokumentierter Satz beschrieben" | Unclear ("dokumentierter Satz"). | "Policies/Standards: derzeit nicht dokumentiert" | `story.steckbrief.betrieb_service.bullets` |
| Steckbrief 2 | "Remote-Zugänge durch fünf Lieferanten" (clue quote) | Wrong preposition. | "Remote-Zugänge für fünf Lieferanten" (update `clues.toml`) | same key |
| Steckbrief 2 | "SIEM/EDR nicht als feste Plattformkomponenten genannt" (clue quote) | "genannt" by whom? Students cannot tell whether it exists. | "Sicherheitsbetrieb: kein SIEM/EDR als feste Plattformkomponente" (update `clues.toml`) | same key |
| Steckbrief 1 | "sind in Vertragskontexten relevant" | Bureaucratic, meaning unclear. | "… und können Vertragsstrafen auslösen" | `story.steckbrief.produktion_betrieb.bullets` |
| Steckbrief 2 | "Auslastungs- und Stillstandsfenster als Taktgeber für Änderungen/Updates in der produktionsnahen Umgebung" | Heavy noun chain; this is a clue-bearing section. | "Änderungen und Updates an produktionsnahen Systemen sind nur in Stillstandsfenstern möglich" | `story.steckbrief.abhaengigkeiten.bullets` |

## spielleitung-uebersicht.pdf

| Page | Quote | Problem | Suggested replacement | Source key |
|---|---|---|---|---|
| 1 | "Es verrät die Angriffe und darf die Teams vor der jeweiligen Welle nicht erreichen." | Implies the booklet may reach teams later; the banner says never. | "Es verrät die Angriffe und darf die Teams nie erreichen." | `sheets.spielleitung.intro` |
| 2 | "Kein Team sieht sie vor dem Beginn seiner Welle." | Waves are shared, not per team. | "Kein Team sieht ein Arbeitsblatt vor Beginn der jeweiligen Welle." | `sheets.ablauf.blocks.break_2.direction` |
| 2 | "Lest die Ereignisse dieser Welle vor und gebt ihre Eventkarten aus." | "Ereignisse" for what every card calls "Event"; "ihre" is ambiguous. | "Lest die Events dieser Welle vor und gebt die zugehörigen Eventkarten aus." | `sheets.ablauf.blocks.wave_1.direction`, `wave_2`, `wave_3` |
| 2 | "… rechnen das Budget Review und die RoS-Seite im Teamheft aus und füllen im Risikoregister die Spalte Rückblick." | "füllen" lacks "aus". | "… und füllen im Risikoregister die Spalte Rückblick aus." | `sheets.ablauf.blocks.closing.direction` |
| 2 | "Die Teams verhandeln ihr Budget-Tier" | See Teamheft p2 row: no procedure given. | Add how and with whom. | `sheets.ablauf.blocks.measures_budget.direction` |
| 2 | "antwortet mit der Tabelle Geschäftsfolgen: Antworten der Geschäftsführung", "die Erklärseite So funktioniert eine Welle aus" | Document titles run into the sentence unmarked. | Set titles in „…“. | `sheets.ablauf.blocks.story_groups.direction`, `sheets.ablauf.blocks.wave_0.direction` |
| 3 | "Pro Datei steht, wie oft ihr sie ausdruckt: je Team und für die Spielleitung." | Clumsy. | "Die Liste zeigt für jede Datei, wie oft ihr sie druckt: je Team und für die Spielleitung." | `sheets.ablauf.print_intro` |
| 4 | "Sucht den Fall mit dem passenden Schutzziel und antwortet in der Rolle der Geschäftsführung von MechTech mit seinem Band, nie mit einem genauen Betrag, und nennt nie einen Angriff." | Overloaded; "mit seinem Band" is unclear. | "Sucht den Fall mit dem passenden Schutzziel. Antwortet in der Rolle der Geschäftsführung von MechTech und nennt dabei nur das Band des Falls, nie einen genauen Betrag und nie einen Angriff." | `sheets.cheatsheet.intro` |
| 4 | "Ein Audit findet Mängel, die wir nachbessern müssen." (Ziel C) | Only case written in the first person; assignment to C is not obvious. Worth a check, not a certain error. | "Ein Audit findet Mängel, die nachgebessert werden müssen." | `sheets.cheatsheet.cases.audit_findings.case` |
| 11 | "kostet jeder angefangene Schritt X Punkte KZ" | "Schritt" is used before it is defined below. | "kostet jeder angefangene Schritt (Schrittweite unten) X KZ-Punkte" | `sheets.spielleitung.review_intro` |
| 11 | "KZ am Ende plus k mal RoS, der RoS vorher auf zwei Nachkommastellen gerundet" | RoS gender differs from Teamheft p4 and Was ist neu ("die RoS", "auf Hundertstel"). | Keep "der RoS … auf zwei Nachkommastellen" and align the others. | `sheets.spielleitung.final_index_note`, `sheets.was_neu.rules.final_index.text` |
| 12 | "Welche Hinweise in den Unterlagen hättet ihr vorab lesen können?" | They did read them; the point is recognising them. | "Welche Hinweise in den Unterlagen hättet ihr vorab erkennen können?" | `sheets.debrief.prompts.clues` |
| 12, 14 | "Hinweis-Matrix für die Discovery-Phase", "Vorab-Dokumenten" | The schedule calls the phase "Story-Gruppenarbeit" and the documents "Story-Unterlagen". | "Hinweis-Matrix für die Story-Gruppenarbeit"; "in den Story-Unterlagen" | `sheets.spielleitung.clues_title`, `sheets.spielleitung.clues_intro` |
| 12 | "berechnet den Final-Index wie im Abschnitt zum Endergebnis" | The section is titled "Endergebnis je Tier". | "… wie im Abschnitt „Endergebnis je Tier“" | `sheets.debrief.compare_intro` |
| 12 | "Wenn Zeit bleibt: … Ihr entscheidet vor Ort, ob dafür Zeit ist; der Pitch hat keine Richtzeit." | Says "if time allows" twice. | "Optional: Jedes Team erklärt der Geschäftsführung von MechTech in einem kurzen Pitch, warum sein Budget gut investiert war. Der Pitch hat keine Richtzeit." | `sheets.debrief.pitch_text` |
| 14–16 | "Warum es hinweist" | Clumsy column head; the intro calls it "Begründung". | "Begründung" | `sheets.spielleitung.clue_head_why` |
| 14–16 | "Kein getrenntes Produktionsnetz: ein Vorfall im Büro erreicht die Fertigung." and ten similar lines | Full sentence after a colon starts lower-case (11 lines in total). | Capitalise the first word after the colon. | `content/clues.toml` (why texts) |
| 16 | "Der OEM betont die Sicherheit der Lieferkette, der dritte Angriff läuft über sie." | Comma splice. | "…; der dritte Angriff läuft über sie." | `content/clues.toml` |

## spielleitung-was-ist-neu.pdf

| Page | Quote | Problem | Suggested replacement | Source key |
|---|---|---|---|---|
| 1 | "Das Event erlaubt … genau einen Pflicht-Maßnahmentausch …; der Kunde trägt deren Init bis zur Höhe der weggefallenen." | "erlaubt" contradicts "Pflicht"; "deren" has no clear referent. | "Das Event verlangt im Change-Fenster danach genau einen Maßnahmentausch (eine aktive Maßnahme raus, eine inaktive rein); der Kunde trägt die Init der neuen Maßnahme bis zur Höhe der Init der weggefallenen." | `sheets.was_neu.rules.kurswechsel.text` |
| 1 | "ersetzt den alten Begriff der MHP-Runde" | Does not name the old term. | Name it: "ersetzt den Begriff „…“ der MHP-Runde". | `sheets.was_neu.rules.levelwechsel.text` |
| 1 | "Statt pauschal kostet das Überziehen am Ende −3 KZ …" | Clumsy opening. | "Statt eines pauschalen Abzugs kostet das Überziehen am Ende" | `sheets.was_neu.rules.overspend.text` |
| 1 | "kann es durch Herabstufen oder Kündigen zurück ins Budget" | Verb missing. | "… zurück ins Budget kommen" | `sheets.was_neu.rules.sparprogramm.text` |
| 1 | "genau einmal runden (halbe Werte vom Betrag weg)" | "vom Betrag weg" is not understandable; meant is away from zero. | "genau einmal runden (halbe Werte weg von der Null), danach auf die Skala begrenzen" | `sheets.was_neu.rules.rounding.text` |
| 1 | "Vergleich der Teams; die RoS wird vorher auf Hundertstel gerundet. Er rechnet:" | "Er" refers only to the heading; RoS gender. | "Vergleichswert der Teams; der RoS wird vorher auf zwei Nachkommastellen gerundet. Formel:" | `sheets.was_neu.rules.final_index.text` |
| 1 | "werden erst beim Treffer benannt" | "Treffer/getroffen" has another meaning in the risk register; the attack is named when its wave starts. | "werden erst zu Beginn ihrer Welle benannt" | `sheets.was_neu.material.veil` |
| 1 | "… und die Hinweis-Matrix für die Discovery-Phase" / "… die Erklärseite aus: So funktioniert eine Welle" | Two bullets end without a full stop, the other four have one. | Add the full stop after the inserted title. | template (`was_neu` template) or `sheets.was_neu.material.clues`, `sheets.was_neu.material.wave_page` |
| not printed now | field label "Obergrenze der Reduktion" for `mitigation_cap` | On the worksheets `mitigation_cap` is "Kappung" and "Obergrenze" means Schwelle plus Kappung; the label would mislead as soon as a cap change is listed. | "Kappung" | `sheets.was_neu.fields.mitigation_cap` |

## spielleitung-probelauf.pdf

| Page | Quote | Problem | Suggested replacement | Source key |
|---|---|---|---|---|
| 1 | "Jede Überschreitung, jede unklare Stelle und jeder Rechenfehler, der hier steht, wird zu einer Aufgabe für die Überarbeitung, es sei denn, sie wird bei der Abnahme ausdrücklich akzeptiert." | "der hier steht" attaches only to Rechenfehler; "sie" has no matching referent. | "Alles, was hier notiert ist (Überschreitungen, unklare Stellen, Rechenfehler), wird zu einer Aufgabe für die Überarbeitung, sofern es bei der Abnahme nicht ausdrücklich akzeptiert wird." | `sheets.probelauf.pass_rules` |

## Cross-document terminology (one decision each, then align)

| Topic | Variants found | Recommendation | Keys |
|---|---|---|---|
| RoS gender | "die RoS" (`sheets.ros.purpose`, `sheets.debrief.stages.analysis.questions`, `sheets.was_neu.rules.ros.text`, `sheets.was_neu.rules.final_index.text`); "der/den RoS" (`sheets.tracking.block_own`, `block_external`, `external_hint`, `sheets.welle.ros_note`, `sheets.spielleitung.final_index_note`, `final_index_weight`) | "der RoS" (der Return) | as listed |
| Attack sheet name | "Angriffsblatt" (players), "Arbeitsblatt" (Spielleitung, Druckliste, `review_hint`) | One term; at least make the player-facing `review_hint` say "Angriffsblatt" | `sheets.register.review_hint`, `sheets.ablauf.*`, `sheets.spielleitung.how_to_title` |
| Event / Ereignis | "Events", "Eventkarten" vs "Ereignisplan", "Ereignisse dieser Welle", "Wirkung des Ereignisses" | "Event" everywhere | `sheets.spielleitung.events_title`, `sheets.spielleitung.intro`, `sheets.ablauf.blocks.wave_*`, `practice.event_result` |
| Budget | "Budget", "Tier-Budget", "Verfügbares Budget" (two meanings), "Gesamtbudget" | "Tier-Budget" for the starting amount, "Verfügbares Budget" only for the p5 sum | `sheets.labels.available_budget`, `sheets.eventkarten.total_budget` |
| Raising and lowering a level | "upgraded", "hebt", "Erhöhung", "Hochstufung", "hoch setzen" / "Senken", "Herabstufen", "runter setzen", "absenken" | "erhöhen" and "senken" (plus "kündigen") | `sheets.budget.anticipated_sum_intro`, `sheets.welle.window_rules`, `sheets.tracking.window_intro`, `events.sparprogramm.rule`, `events.kurswechsel.rule`, `sheets.was_neu.rules.*` |
| Damage scale | "Stufe" (`need_instruction`), "Band" (`instruction`, `review_hint`, cheat sheet) | One term | `sheets.register.*`, `sheets.cheatsheet.*` |
| Base value | "Basiswert" vs "Basisschutz" | "Basisschutz" | `sheets.angriff.start_values_intro` |
| KZ start | "KZ Start" (Teamheft) vs "KZ-Start" (Was ist neu) | "KZ-Start" | `sheets.teamheft.kz_start` |
| Company name | "MECHTECH GmbH" vs "MechTech GmbH" | "MechTech" | `story.steckbrief.*` |
| Client role | "euch Beratern" vs "Euer Unternehmen", "eurer Produktionssteuerung", "Eure Daten" | Name MechTech as the client on the attack sheets | `sheets.angriff.start_values_intro`, `attacks.ot.revealed.narrative`, `attacks.exfil.revealed.narrative` |

## Checked and found consistent

- Numbers agree between documents: thresholds, caps, bonuses, weights and case values on the three attack sheets match the Spielleitungsheft; Budget Review bands match on event card, Spielleitungsheft and Was ist neu; the Übung values match its Lösungsschlüssel.
- The reference-path arithmetic I recomputed is right: event KZ per wave, Restbudget, RoS and Final-Index for the Low tier, Final-Index for all three tiers.
- "Sie" appears only in the two story mails, as intended. The only stray address form is the "du" in the Maßnahmenkarten legend title.
- The level colours in the legend (grün, gelb, grau) match `print/planspiel.sty`.

## Count per category

| Category | Findings |
|---|---|
| 1. Spelling, grammar, punctuation, case, agreement | 34 |
| 2. Clumsy or unclear phrasing, misleading instructions, terminology, address form | 45 (including the 10 terminology groups) |
| 3. Content contradictions between or within documents | 8 (Operative Unterstützung; KZ Events source; Init "zu Spielbeginn"; exfiltration narrative vs cases; "Gesamtschutz über alle Schutzziele"; bonus "zur Gesamtreduktion"; "Verfügbares Budget" two meanings; Spielleitungsheft "vor der jeweiligen Welle") |
| Total | 87 |
