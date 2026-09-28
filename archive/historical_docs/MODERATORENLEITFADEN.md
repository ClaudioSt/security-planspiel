# MODERATORENLEITFADEN

**CIA-Planspiel Automotive - Version MVP 1.0**
**Workshop 28.1.2026**

---

## ÜBERBLICK

### Spielziel
Teams beraten als externe Consultants den Automobilzulieferer **MechTech GmbH** zur IT-Sicherheit. Sie wählen Sicherheitsmaßnahmen, verteidigen gegen 3 Angriffswellen und optimieren Kundenzufriedenheit (KZ) und Budget.

### Rahmenbedingungen
- **Dauer:** 3-4 Stunden
- **Teams:** 3 Teams à 5 Personen
- **Moderatoren:** 1 Hauptmoderator + 2 Co-Moderatoren (optional)
- **Material:** Whiteboard, Marker, Formulare, Maßnahmenkarten

### Lernziele
1. CIA-Trade-offs verstehen (Confidentiality, Integrity, Availability)
2. Risikoorientiertes Denken entwickeln
3. Budget-Sicherheits-Balance finden
4. Stakeholder-Kommunikation üben

---

## VORBEREITUNG (30 Min vor Workshop)

### Material-Checkliste

**Pro Team:**
- [ ] 1x Spieleranleitung (2 Seiten)
- [ ] 1x Team-Übersichtsblatt
- [ ] 3x Wellenprotokoll (eins pro Welle)
- [ ] 1x Auswertungstabelle
- [ ] Stifte (5 Stück)
- [ ] Taschenrechner

**Für Moderatoren:**
- [ ] Dieser Leitfaden
- [ ] PARAMETER_TABELLE.md (ausgedruckt)
- [ ] DISCOVERY_FRAGEBOGEN.md (ausgedruckt)
- [ ] Timer/Stoppuhr

**Raum:**
- [ ] Whiteboard (groß, gut sichtbar)
- [ ] Whiteboard-Marker (3-5 Farben)
- [ ] Post-its (optional)
- [ ] 3 Tische für Teams (räumlich getrennt)

### Whiteboard-Layout vorbereiten

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        WHITEBOARD-LAYOUT                                │
├───────────────────┬─────────────────────┬───────────────────────────────┤
│   WELLEN-STATUS   │    TEAM-ÜBERSICHT   │      MASSNAHMEN-MARKT         │
│                   │                     │                               │
│  Aktuelle Welle:  │  Team A:            │  M1 IAM: L1/L2/L3             │
│  [ 1 / 2 / 3 ]    │   Budget: ___       │    30/60/100 | 4/10/20        │
│                   │   KZ: ___           │                               │
│  Gewichte:        │                     │  M2 SIEM: L1/L2/L3            │
│  wC: ___          │  Team B:            │    20/50/80 | 2/8/24          │
│  wI: ___          │   Budget: ___       │                               │
│  wA: ___          │   KZ: ___           │  M3 EDR: L1/L2/L3             │
│                   │                     │    24/56/90 | 4/10/18         │
│  E-Ziel: ___      │  Team C:            │                               │
│  KZ-Bonus: +___   │   Budget: ___       │  ...weitere Maßnahmen...      │
│  KZ-Malus: -___   │   KZ: ___           │                               │
│                   │                     │  Format: Init | OPEX/Welle    │
└───────────────────┴─────────────────────┴───────────────────────────────┘
```

---

## ABLAUF IM DETAIL

### PHASE 1: INTRO (10 Min)

**Ziel:** Teams verstehen Setting und Regeln

**Moderator sagt:**

> "Willkommen zum IT-Security-Planspiel! Ihr seid heute Berater-Teams, die den Automobilzulieferer MechTech GmbH zur IT-Sicherheit beraten.
>
> MechTech produziert Präzisionsteile für E-Antriebe. Euer Hauptkunde, ein großer OEM, fordert bis Q3 eine ISO 27001-Zertifizierung. Es gibt Risiken: Ransomware, OT-Störungen, Datendiebstahl.
>
> Eure Aufgabe:
> 1. Budget mit dem Kunden verhandeln
> 2. Sicherheitsmaßnahmen auswählen
> 3. 3 Angriffswellen überstehen
> 4. Kundenzufriedenheit (KZ) maximieren
>
> Das Spiel ist deterministisch - es gibt keine Würfel. Eure Entscheidungen bestimmen das Ergebnis."

**Spieleranleitung verteilen, kurz durchgehen.**

---

### PHASE 2: DISCOVERY (25 Min)

**Ziel:** Teams erkunden das Szenario, Moderator ermittelt Signal-Scores

**Ablauf:**

| Zeit | Aktivität |
|------|-----------|
| 0-5 Min | Teams lesen Spieleranleitung (Szenario-Teil) |
| 5-20 Min | Teams stellen Fragen, Moderator antwortet |
| 20-25 Min | Moderator fasst zusammen, leitet Budget-Empfehlung ab |

**Moderator-Aktionen:**

1. **Fragen beantworten** (siehe DISCOVERY_FRAGEBOGEN.md)
   - Bei jeder relevanten Frage: Score notieren
   - Signal-Kategorien: OT-Kritikalität, Compliance-Druck, IP-Schutz

2. **Hilfestellung geben** (wenn Teams stocken):
   > "Denkt an: Geschäftsbeziehung, Netzwerk-Architektur, Mitarbeitende, externe Zugänge, Regulierung."

3. **Signal-Scores auswerten:**

| Signal | Punkte | Konsequenz |
|--------|--------|------------|
| OT-Kritikalität >10 | Welle 2 härter | wA=0.7, sUnit +2 |
| Compliance-Druck >10 | Event 1 härter | Malus -5 statt -3 |
| IP-Schutz >10 | Welle 3 härter | wC=0.6, kzUnit +1 |

4. **Zusammenfassung:**
   > "Ihr habt erkannt: OT ist kritisch, der OEM erwartet Zertifizierung, Konstruktionsdaten sind wertvoll. Basierend darauf würde der Kunde ca. 300-400k investieren."

---

### PHASE 3: BUDGET-VERHANDLUNG (10 Min)

**Ziel:** Teams einigen sich auf Startbudget

**Moderator erklärt Trade-offs:**

| Budgetbereich | KZ-Start | E-Ziele (W1/W2/W3) | Beschreibung |
|---------------|----------|---------------------|--------------|
| 200-280k (niedrig) | 70 | 30/40/50 | Sparfuchs - niedrige Erwartungen |
| 281-380k (mittel) | 60 | 40/50/60 | Standard |
| 381-500k (hoch) | 50 | 50/60/70 | Premium - hohe Erwartungen |

**Moderator sagt:**
> "Höheres Budget = mehr Maßnahmen möglich, ABER niedrigerer KZ-Start und höhere E-Ziele. Überlegt gut!"

**Teams diskutieren intern, nennen dann ihre Entscheidung.**

**Moderator trägt ein:**
- Budget auf Whiteboard (Team-Übersicht)
- KZ-Start auf Whiteboard
- E-Ziele für alle 3 Wellen (abhängig vom Budget-Range)

---

### PHASE 4: MASSNAHMENWAHL (20 Min)

**Ziel:** Teams wählen initiale Sicherheitsmaßnahmen

**Ablauf:**

1. **Maßnahmen erklären** (kurz, Whiteboard zeigen):
   - 8 optimale Maßnahmen (M1-M8)
   - 2 suboptimale (M9-M10) als Lernerfahrung
   - Jede Maßnahme: L1/L2/L3 mit unterschiedlichen Kosten und Wirkung

2. **Teams wählen:**
   - Welche Maßnahmen?
   - Welches Level (L1/L2/L3)?
   - Budget für Init-Kosten + OPEX für alle 3 Wellen beachten!

3. **Abhängigkeiten prüfen:**
   - M1 L3 benötigt M2 ≥ L2
   - M3 L3 benötigt M2 ≥ L2
   - M7 L3 benötigt M2 ≥ L1

**Budget-Rechnung (Teams selbst):**
```
Verfügbar:      ___ k
- Init-Summe:   ___ k
- OPEX × 3:     ___ k
= Restbudget:   ___ k  (muss ≥ 0 sein!)
```

**Moderator prüft:**
- Abhängigkeiten erfüllt?
- Budget nicht überschritten?
- Werte auf Team-Sheet eingetragen?

---

### PHASE 5: WELLE AUFLÖSEN (25 Min pro Welle)

**Ablauf pro Welle:**

#### Schritt 1: Wellen-Parameter verkünden (2 Min)

**Moderator sagt:**
> "Welle [X] beginnt! Der Angriff: [Narrative vorlesen]"

**Parameter am Whiteboard eintragen:**
- wC / wI / wA (CIA-Gewichte)
- E-Ziel (abhängig vom Budget-Range)
- KZ-Bonus / KZ-Malus

| Welle | Angriff | wC | wI | wA | baseSev | sUnit | kzUnit |
|-------|---------|----|----|-----|---------|-------|--------|
| 1 | Ransomware | 0.4 | 0.4 | 0.2 | 8 | 12 | 5 |
| 2 | OT-Störung | 0.2 | 0.2 | 0.6 | 10 | 20 | 8 |
| 3 | Exfiltration | 0.5 | 0.3 | 0.2 | 7 | 15 | 6 |

---

#### Schritt 2: Mitigation berechnen (5 Min)

**Für jedes Team:**

1. Team nennt gewählte Maßnahmen + Level
2. Moderator schlägt Mitigation nach (PARAMETER_TABELLE.md)
3. Summe bilden (Kontext-Boni beachten!)
4. Cap anwenden: M_sum = min(MIT_CAP, Summe)

**Kontext-Boni (wichtig!):**
- Welle 1 (Ransomware): M3 L3 +1, M4 L3 +1, M6 L2 +1, M6 L3 +2
- Welle 2 (OT-Störung): M5 L2/L3 +2, M7 L2/L3 +1
- Welle 3 (Exfiltration): M1 L3 +1, M2 L3 +1, M8 L3 +1

---

#### Schritt 3: Endschwere & Schaden berechnen (3 Min)

```
G = max(0, baseSeverity - M_sum)
Damage = G × sUnit
ΔKZ = -(G × kzUnit)
```

**Wenn M4 (Backup) vorhanden - Recovery anwenden:**
```
Damage_final = Damage × (1 - Recovery_Faktor)
```
- L1: 10%
- L2: 30%
- L3: 50%

---

#### Schritt 4: CIA-Mali berechnen (2 Min)

```
ΔC = -G × ciaImpactPerStep_C
ΔI = -G × ciaImpactPerStep_I
ΔA = -G × ciaImpactPerStep_A
```

| Welle | C/Stufe | I/Stufe | A/Stufe |
|-------|---------|---------|---------|
| 1 | -2 | -2 | -1 |
| 2 | -1 | -2 | -3 |
| 3 | -3 | -1 | 0 |

---

#### Schritt 5: E-Wert berechnen (3 Min)

```
Team_C = Basis_C + Maßnahmen_C + ΔC
Team_I = Basis_I + Maßnahmen_I + ΔI
Team_A = Basis_A + Maßnahmen_A + ΔA

E = Team_C × wC + Team_I × wI + Team_A × wA
```

**Basis-CIA:** C=10, I=10, A=10 (vor Maßnahmen)

**E-Ziel prüfen:**
- E ≥ E-Ziel → KZ + Bonus
- E < E-Ziel → KZ + Malus (negativ!)

---

#### Schritt 6: State aktualisieren (3 Min)

**Am Whiteboard:**
- KZ aktualisieren: KZ_neu = clamp(KZ_alt + ΔKZ + Bonus/Malus, 0, 100)
- Budget aktualisieren: Budget_neu = Budget_alt - OPEX - Damage_final
- Event prüfen (siehe unten)

**Auf Team-Sheet:**
- Wellenprotokoll ausfüllen
- Neue Werte eintragen

---

#### Schritt 7: Events prüfen (2 Min)

**Welle 2 - Event 1: OEM-Audit**
- Trigger: Automatisch
- Wenn E-Wert Welle 1 ≥ E-Ziel: KZ +5
- Wenn E-Wert Welle 1 < E-Ziel: KZ -3 (oder -5 bei hohem Compliance-Druck)

**Welle 2 - Event 2: Mitarbeiter-Fluktuation**
- Trigger: M6 (Awareness) < L2 am Ende Welle 1
- Effekt: OPEX +5, KZ -2

**Welle 3 - Event 3: DSGVO-Bonus**
- Trigger: M1 ≥ L2 UND M2 ≥ L2 am Ende Welle 2
- Effekt: KZ +3, Budget +10

---

### PHASE 6: CHANGE-FENSTER (15 Min pro Fenster)

**Nach Welle 1 und 2:**

**Teams können:**
- Maßnahmen upgraden (L1→L2, L2→L3)
- Neue Maßnahmen kaufen
- Maßnahmen NICHT abwählen (bereits investiert!)

**Kosten:**
- Init-Kosten für neues Level/neue Maßnahme
- OPEX ab nächster Welle

**Moderator prüft:**
- Budget ausreichend?
- Abhängigkeiten erfüllt?

**Änderungen wirksam:** Ab nächster Welle

---

### PHASE 7: AUSWERTUNG (20 Min)

**Nach Welle 3:**

#### Return on Security (RoS) berechnen

```
Gesamtkosten = Init-Summe + (OPEX × 3) + Event-Strafen

Verluste = Σ(Damage_final über alle Wellen)

Basisverluste = Σ(baseSeverity × sUnit) = 8×20 + 10×32 + 7×20 = 620k

Vermiedene_Verluste = Basisverluste - Verluste

RoS = (Vermiedene_Verluste - Gesamtkosten) / Gesamtkosten × 100%
```

**Interpretation:**
- RoS > 100%: Exzellent! Mehr gespart als investiert
- RoS 50-100%: Gut, Investition hat sich gelohnt
- RoS 0-50%: Akzeptabel
- RoS < 0%: Schlecht, zu viel investiert oder falsche Maßnahmen

---

#### Ranking erstellen

| Platz | Team | Finale KZ | RoS | Restbudget |
|-------|------|-----------|-----|------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

**Gewinner:** Höchste KZ (bei Gleichstand: höherer RoS)

---

### PHASE 8: DEBRIEF (30 Min)

**Ziel:** Reflexion, Learnings verankern

#### Reflexionsfragen (15 Min)

**An alle Teams:**

1. "Welche Maßnahmen haben am meisten gebracht?"
   - Erwartete Antworten: M5 (OT-Seg), M6 (Awareness), M4 (Backup)

2. "Was hättet ihr rückblickend anders gemacht?"
   - Typisch: Mehr OT-Fokus, früher in Awareness investieren

3. "Welche Trade-offs waren schwierig?"
   - Budget vs. Sicherheit, Init vs. OPEX, CIA-Schwerpunkte

4. "Was hat euch überrascht?"
   - Typisch: Kontext-Boni, Events, OT-Schadenskosten

#### Learnings zusammenfassen (10 Min)

**Moderator fasst zusammen:**

> "Was wir heute gelernt haben:
>
> 1. **Awareness ist Gold wert** - Menschen sind oft das schwächste Glied, aber auch die beste Verteidigung
>
> 2. **OT-Segmentierung ist kritisch** - Produktion muss vom Office getrennt sein
>
> 3. **Backups retten im Notfall** - Aber nur wenn getestet und isoliert!
>
> 4. **Kontext ist wichtig** - Nicht jede moderne Maßnahme passt (M9, M10)
>
> 5. **Budget-Trade-offs** - Mehr Geld ≠ automatisch besser (höhere Erwartungen!)
>
> 6. **Defense in Depth** - Mehrere Schichten schützen besser als eine teure"

#### Offene Fragen (5 Min)

**Raum für Diskussion:**
- Fragen der Teilnehmenden
- Bezug zur echten Arbeitswelt herstellen

---

## TROUBLESHOOTING

### Problem: Team hat Budget überschritten
**Lösung:** Team muss Maßnahmen reduzieren oder Level senken. Keine Schulden erlaubt.

### Problem: Abhängigkeit vergessen
**Lösung:** Maßnahme wirkt nicht auf dem gewählten Level. Team kann in Change-Fenster Abhängigkeit nachholen.

### Problem: Rechenfehler
**Lösung:** Moderator berechnet neu. Bei Unklarheiten: Moderator-Entscheidung gilt.

### Problem: Teams brauchen zu lange
**Lösung:** Timer setzen, freundlich mahnen. Notfalls Welle 3 verkürzen.

### Problem: KZ auf 0 gefallen
**Lösung:** Team hat verloren (Vertrag gekündigt). Trotzdem weiterspielen für Learnings.

---

## ZEITPLAN (Zusammenfassung)

| Phase | Dauer | Kumuliert |
|-------|-------|-----------|
| Intro | 10 Min | 0:10 |
| Discovery | 25 Min | 0:35 |
| Budget-Verhandlung | 10 Min | 0:45 |
| Maßnahmenwahl | 20 Min | 1:05 |
| Welle 1 | 25 Min | 1:30 |
| Change-Fenster 1 | 15 Min | 1:45 |
| Welle 2 + Events | 25 Min | 2:10 |
| Change-Fenster 2 | 15 Min | 2:25 |
| Welle 3 + Events | 25 Min | 2:50 |
| Auswertung | 20 Min | 3:10 |
| Debrief | 30 Min | 3:40 |

**Gesamt: ca. 3h 40min** (+ Pausen nach Bedarf)

---

## NOTIZEN FÜR MODERATOREN

```
Discovery-Scores:
- OT-Kritikalität:    ___ / 20
- Compliance-Druck:   ___ / 15
- IP-Schutz:          ___ / 12

Budget-Entscheidungen:
- Team A: ___k → KZ-Start: ___ → E-Ziele: ___/___/___
- Team B: ___k → KZ-Start: ___ → E-Ziele: ___/___/___
- Team C: ___k → KZ-Start: ___ → E-Ziele: ___/___/___

Beobachtungen:
_______________________________________________________
_______________________________________________________
_______________________________________________________
```

---

**Viel Erfolg beim Workshop! Ihr schafft das!**
