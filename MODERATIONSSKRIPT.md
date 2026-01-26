# MODERATIONSSKRIPT

**CIA-Planspiel Automotive | Wer sagt was wann**

---

## PHASE 0: BEGRUESSUNG (5 Min)

### Moderator sagt:

> "Willkommen zum CIA-Planspiel! Heute seid ihr Sicherheitsberater fuer die MechTech GmbH - einen Automobilzulieferer, der dringend seine IT-Sicherheit verbessern muss.
>
> Ihr werdet ein Sicherheitsbudget verwalten, Massnahmen auswaehlen und drei Angriffswellen ueberstehen.
>
> Euer Ziel: Die Kundenzufriedenheit hoch halten und einen guten Return on Security erzielen.
>
> Wir arbeiten in Teams. Jedes Team beratet MechTech unabhaengig. Am Ende vergleichen wir, wer die beste Strategie hatte."

### Dann:
- Teams einteilen (3 Teams a 3-5 Personen)
- Materialien verteilen (Spieleranleitung, Formulare)

---

## PHASE 1: DISCOVERY (25 Min)

### Moderator sagt:

> "Erste Phase: Discovery. Lest euch die Spieleranleitung durch und lernt MechTech kennen.
>
> Wichtige Fragen:
> - Was produziert MechTech?
> - Welche Risiken seht ihr?
> - Welche Sicherheitsmassnahmen koennten helfen?
>
> Ihr habt 25 Minuten. Danach muesst ihr euch fuer ein Budget entscheiden."

### Timer: 25 Min

### Moderator beobachtet:
- Verstehen Teams die Ausgangslage?
- Welche Fragen kommen auf?
- Diskutieren alle mit?

### Bei Fragen:
- "Schaut in die Spieleranleitung auf Seite X"
- "Das klaert sich in der naechsten Phase"
- Keine Strategietipps geben!

---

## PHASE 2: BUDGET-ENTSCHEIDUNG (10 Min)

### Moderator sagt:

> "Jetzt wird's ernst: Ihr muesst euch fuer ein Budget-Tier entscheiden.
>
> **LOW (200-250k):** Wenig Geld, aber ihr startet mit hoher Kundenzufriedenheit (70).
>
> **MEDIUM (300-350k):** Ausgewogen, KZ-Start bei 60.
>
> **HIGH (400-450k):** Viel Geld, aber der Kunde ist anfangs skeptisch - nur 50 KZ.
>
> Das ist ein Trade-off! Mehr Budget heisst nicht automatisch besser.
>
> Bitte entscheidet euch jetzt. Schreibt euer Budget und KZ-Start auf das Team-Uebersichtsblatt."

### Timer: 10 Min

### An Whiteboard notieren:
| Team | Budget | KZ-Start |
|------|--------|----------|
| A | ___k | ___ |
| B | ___k | ___ |
| C | ___k | ___ |

---

## PHASE 3: MASSNAHMENWAHL (20 Min)

### Moderator sagt:

> "Jetzt waehlt ihr eure Sicherheitsmassnahmen. Schaut euch die Tabelle in der Anleitung an.
>
> **Wichtig:**
> 1. Init + 3x OPEX muss in euer Budget passen!
> 2. Manche Massnahmen haben Abhaengigkeiten - M1 L3 braucht z.B. M2 L2.
> 3. Nicht jede Massnahme passt zu MechTech - ueberlegt, was sinnvoll ist.
>
> Ihr habt 20 Minuten. Tragt eure Wahl auf dem Team-Uebersichtsblatt ein."

### Timer: 20 Min

### Moderator prueft am Ende:
- Budget eingehalten?
- Abhaengigkeiten erfuellt?
- Keine Massnahme vergessen?

---

## PHASE 4: WELLE 1 - RANSOMWARE (15 Min)

### Moderator sagt:

> "Erste Angriffswelle!
>
> **Szenario:** Ein Mitarbeiter klickt auf einen Phishing-Link. Emotet-Trojaner installiert sich. Der File-Server wird verschluesselt. Produktion steht!
>
> *[Angriffskarte Welle 1 zeigen]*
>
> baseSeverity: 8
> Cap: 10
> Fokus: Confidentiality (40%) + Integrity (40%) + Availability (20%)
>
> Berechnet jetzt auf eurem Wellenprotokoll:
> 1. M_sum: Summe eurer Mitigations (max. Cap!)
> 2. G: baseSeverity minus M_sum
> 3. Damage: G mal 20 (sUnit)
> 4. KZ-Verlust: G mal 3 (kzUnit)
> 5. E-Wert: Eure CIA-Werte gewichtet
>
> E-Ziel ist 18. Schafft ihr das?"

### Timer: 15 Min

### Moderator sammelt Ergebnisse:

| Team | M_sum | G | Damage | Delta-KZ | E-Wert | Bonus/Malus |
|------|-------|---|--------|----------|--------|-------------|
| A | | | | | | |
| B | | | | | | |
| C | | | | | | |

### Event pruefen: FLUKTUATION
> "Hat ein Team M6 (Awareness) unter L2? Dann tritt Fluktuation ein: OPEX +5, KZ -2."

### KZ am Whiteboard aktualisieren!

---

## PHASE 5: CHANGE 1 (15 Min)

### Moderator sagt:

> "Ihr habt die erste Welle ueberstanden. Jetzt habt ihr die Chance, nachzubessern.
>
> Ihr koennt:
> - Massnahmen upgraden (L1 auf L2, L2 auf L3)
> - Neue Massnahmen kaufen
>
> Ihr koennt NICHT:
> - Massnahmen abwaehlen
>
> Aenderungen kosten Init-Differenz und erhoehen OPEX. Rechnet genau!
> Aenderungen wirken ab Welle 2."

### Timer: 15 Min

---

## PHASE 6: WELLE 2 - OT-STOERUNG (15 Min)

### Moderator sagt:

> "Zweite Welle - diesmal trifft es die Produktion!
>
> **Szenario:** Angreifer nutzen eine Schwachstelle in einer SPS aus. Fertigungslinie 2 faellt 18 Stunden aus. Der OEM ist nicht amuesiert.
>
> *[Angriffskarte Welle 2 zeigen]*
>
> baseSeverity: 10
> Cap: 12 (!)
> Fokus: Availability (60%) + Confidentiality (20%) + Integrity (20%)
>
> Berechnet wieder auf einem neuen Wellenprotokoll."

### Timer: 15 Min

### Events pruefen (nacheinander):

**1. OEM-AUDIT:**
> "Der OEM prueft eure Sicherheit! War euer E-Wert in Welle 1 mindestens 18?
> - Ja: KZ +5
> - Nein: KZ -3"

**2. DSGVO-BONUS:**
> "Hat ein Team M1 >= L2 UND M2 >= L2? Dann gibt's den DSGVO-Bonus: KZ +3, Budget +10"

**3. COMPLIANCE-GAP (nur LOW-Tier):**
> "Teams mit LOW-Budget (200-250k): Das knappe Budget fuehrt zu Compliance-Luecken. KZ -3."

### KZ am Whiteboard aktualisieren!

---

## PHASE 7: CHANGE 2 (15 Min)

### Moderator sagt:

> "Letzte Chance fuer Anpassungen! Nach dieser Phase kommt die finale Welle.
>
> Gleiche Regeln wie bei Change 1. Nutzt eure Erkenntnisse!"

### Timer: 15 Min

---

## PHASE 8: WELLE 3 - EXFILTRATION (15 Min)

### Moderator sagt:

> "Finale Welle - der gefaehrlichste Angriff!
>
> **Szenario:** Angreifer haben ueber einen kompromittierten Lieferanten-Zugang CAD-Daten gestohlen. Eure geheimen Fertigungstoleranzen sind jetzt in dunklen Foren...
>
> *[Angriffskarte Welle 3 zeigen]*
>
> baseSeverity: 7
> Cap: 10
> Fokus: Confidentiality (50%) + Integrity (30%) + Availability (20%)
>
> Berechnet die finale Runde!"

### Timer: 15 Min

### Event pruefen: INVESTOR CONFIDENCE (nur HIGH-Tier)
> "Teams mit HIGH-Budget (400-450k): Eure hohen Sicherheitsinvestitionen ueberzeugen Investoren. KZ +8."

### KZ am Whiteboard finalisieren!

---

## PHASE 9: AUSWERTUNG (10 Min)

### Moderator sagt:

> "Zeit fuer die Abrechnung!
>
> Berechnet euren Return on Security:
>
> 1. Gesamtkosten = Init + (OPEX x 3) + Event-Strafen
> 2. Gesamtverluste = Summe aller Damages (nach Recovery)
> 3. Vermiedene Verluste = 620k - Gesamtverluste
> 4. RoS = (Vermieden - Kosten) / Kosten x 100%
>
> Und euren Final-Index:
> Final-Index = KZ_final + RoS x 0.25"

### Ergebnisse sammeln:

| Team | KZ-Final | Gesamtkosten | Gesamtverluste | RoS | Final-Index |
|------|----------|--------------|----------------|-----|-------------|
| A | | | | | |
| B | | | | | |
| C | | | | | |

### Gewinner verkuenden:
> "Das Team mit dem hoechsten Final-Index ist... [TEAM X]! Herzlichen Glueckwunsch!"

---

## PHASE 10: DEBRIEF (10 Min)

### Moderator fragt:

> "Lasst uns reflektieren:
>
> 1. Was hat euch ueberrascht?
> 2. Welche Entscheidung war rueckblickend falsch?
> 3. Was wuerdet ihr beim naechsten Mal anders machen?
> 4. Welche Parallelen seht ihr zur echten Welt?"

### Diskussion leiten (Stichpunkte):
- Trade-off Budget vs. KZ-Start
- OT-Sicherheit oft vernachlaessigt
- Awareness ist guenstig und effektiv
- Abhaengigkeiten in der echten Welt noch komplexer
- 100% Sicherheit ist unmoeglich - es geht um Risikomanagement

### Abschluss:

> "Vielen Dank fuers Mitspielen! Ihr habt heute erlebt, wie komplex IT-Sicherheit sein kann.
>
> Key Takeaways:
> - Sicherheit ist eine Investition, kein Kostenfaktor
> - Der richtige Mix aus Massnahmen zaehlt
> - Manchmal ist weniger Budget mit klugerer Strategie besser
>
> Feedback-Boegen bitte ausfuellen und abgeben!"

---

## ZEITPLAN-ZUSAMMENFASSUNG

| Phase | Zeit | Kumuliert |
|-------|------|-----------|
| Begruessung | 5 | 5 |
| Discovery | 25 | 30 |
| Budget | 10 | 40 |
| Massnahmen | 20 | 60 |
| Welle 1 | 15 | 75 |
| Change 1 | 15 | 90 |
| Welle 2 | 15 | 105 |
| Change 2 | 15 | 120 |
| Welle 3 | 15 | 135 |
| Auswertung | 10 | 145 |
| Debrief | 10 | 155 |
| **GESAMT** | **~2.5h** | |

---

*Tipp: Dieses Skript am Tag vorher laut durchlesen!*

