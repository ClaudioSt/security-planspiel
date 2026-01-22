# 6-TAGE-ROADMAP zum Workshop am 28.1.2026

**Ziel:** Spielbares, getestetes MVP mit 3 Wellen für Wirtschaftsingenieur-Studierende
**Team:** 3 Personen (alle IT-Security-Berater, keine Planspiel-Erfahrung)

---

## ÜBERSICHT

| Tag | Datum | Schwerpunkt | Kritische Deliverables |
|-----|-------|-------------|------------------------|
| **Tag 1** | 22.1. (heute) | Konzept-Freigabe + Parameter | Finales Konzept, Parametertabelle |
| **Tag 2** | 23.1. | Material-Erstellung (parallel) | Moderatorenleitfaden, Spieleranleitung, Formulare |
| **Tag 3** | 24.1. | Interner Testlauf | Getestete Version 1.0, Issue-Liste |
| **Tag 4** | 25.1. | Externer Playtest | Feedback-Protokoll, Revision-Backlog |
| **Tag 5** | 26.1. | Iteration + Finalisierung | Version 2.0 (final), Druckmaterial |
| **Tag 6** | 27.1. | Generalprobe + Setup | Moderations-Choreografie, Material-Check |
| **Tag 7** | 28.1. | **WORKSHOP** | 🎉 Durchführung |

---

## TAG 1: 22.1. (HEUTE) – Konzept-Freigabe & Parametrisierung

### VORMITTAG (3h) - GEMEINSAM

#### 1. Konzept-Review & Feedback (60 Min)
**Wer:** Alle 3
**Was:**
- KONZEPT_MVP.md durchgehen
- Offene Fragen klären (siehe Abschnitt 8 im Konzept)
- Entscheidungen treffen:
  - Maßnahmen final (8 oder weniger?)
  - Budget-Range bestätigen
  - Angriffs-Reihenfolge ok?
  - Discovery-Format bestätigen

**Output:** Freigabe-Protokoll (kurz: "Was ist beschlossen?")

---

#### 2. Parameter-Session (90 Min)
**Wer:** Alle 3
**Was:** Gemeinsam die Zahlen festlegen (Excel/Google Sheets)

**Tabelle: Maßnahmen-Parameter**

| Maßnahme | Level | CIA (C/I/A) | Init | OPEX | Mitigation Ransomware | Mitigation OT | Mitigation Exfil | Abhängigkeiten |
|----------|-------|-------------|------|------|----------------------|---------------|------------------|----------------|
| M1 IAM | L1 | 2/1/0 | 15 | 2 | -1 | 0 | -1 | - |
| M1 IAM | L2 | 4/3/0 | 30 | 5 | -2 | 0 | -2 | - |
| M1 IAM | L3 | 6/5/1 | 50 | 10 | -3 | 0 | -3 | M2≥L2 |
| M2 SIEM | L1 | 1/3/0 | 10 | 1 | -1 | 0 | -1 | - |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Tabelle: Angriffe**

| Welle | Angriff | baseSev | sUnit | kzUnit | CIA-Impact | Mitigations |
|-------|---------|---------|-------|--------|------------|-------------|
| 1 | Ransomware | 8 | 12 | 5 | C-2, I-2, A-1 | M1,M2,M3,M6,M7 |
| 2 | OT-Störung | 10 | 20 | 8 | C-1, I-2, A-3 | M2,M5,M7,M8 |
| 3 | Exfiltration | 7 | 15 | 6 | C-3, I-1, A-0 | M1,M2,M3,M7,M8 |

**Tabelle: Wellen**

| Welle | wC | wI | wA | E-Ziel (niedrig/mittel/hoch) | KZ-Bonus | KZ-Malus |
|-------|----|----|----|-----------------------------|----------|----------|
| 1 | 0.4 | 0.4 | 0.2 | 20/25/30 | +3 | -5 |
| 2 | 0.2 | 0.2 | 0.6 | 25/30/35 | +5 | -8 |
| 3 | 0.5 | 0.3 | 0.2 | 30/35/40 | +8 | -10 |

**Wichtig:** Nicht zu viel Zeit mit Feintuning! Erste sinnvolle Werte nehmen, Rest im Test anpassen.

**Output:** Excel/Google Sheet "Parameter_MVP_v1.xlsx"

---

#### 3. Arbeitsteilung für Tag 2 festlegen (30 Min)
**Wer:** Alle 3
**Was:**
- Rollen verteilen für Tag 2 (siehe unten)
- Templates/Strukturen klären (damit alle wissen, was sie erstellen)

**Output:** Aufgabenverteilung + Deadlines (bis wann fertig?)

---

### NACHMITTAG (3h) - PARALLEL ARBEITEN

**Person 1:** Discovery-Fragebogen ausarbeiten
- 15 Fragen mit Musterlösungen
- Signal-Scoring-Tabelle (OT/Compliance/IP: 0-10)
- Budgetempfehlung ableiten

**Person 2:** Whiteboard-Layout skizzieren
- Welche Bereiche (Maßnahmen-Markt, Team-Status, Formeln, Wellen-Info)?
- Als Powerpoint/Sketch (später auf echtes Whiteboard übertragen)

**Person 3:** Formel-Rechenwege dokumentieren
- "Wie berechnen wir G, Damage, KZ-Delta, E-Wert, RoS?"
- Als Cheat-Sheet für Moderatoren (1 Seite)

**Output:** 3 Arbeitsergebnisse (Entwürfe)

---

### ABEND (1h) - SYNC

**Wer:** Alle 3
**Was:**
- Ergebnisse teilen, Feedback geben
- Klären: "Was fehlt noch für Tag 2?"

**Output:** Bereit für Tag 2

---

## TAG 2: 23.1. – Material-Erstellung (parallel)

### GANZTAG (8h) - PARALLEL

#### Person 1: Moderatorenleitfaden (6-8 Seiten)

**Struktur:**
1. **Überblick** (Ziele, Ablauf, Timing)
2. **Vorbereitung** (Material-Checkliste, Raum-Setup)
3. **Phase 1: Discovery** (Fragebogen, wie moderieren, Signal-Scoring)
4. **Phase 2: Budget-Verhandlung** (wie moderieren, Trade-offs erklären)
5. **Phase 3: Maßnahmenwahl** (Abhängigkeiten prüfen, Kosten berechnen)
6. **Phase 4: Welle auflösen** (Schritt-für-Schritt, Formeln, Whiteboard-Update)
7. **Phase 5: Change-Fenster** (Regeln, KZ-Effekte)
8. **Auswertung & Debrief** (Tabellen ausfüllen, Reflexionsfragen)
9. **Troubleshooting** (FAQs, häufige Fehler)

**Format:** Word/Google Docs, gut strukturiert, Screenshots vom Whiteboard-Layout

**Output:** "Moderatorenleitfaden_v1.0.docx"

---

#### Person 2: Spieleranleitung (2 Seiten) + Formulare

**Spieleranleitung:**
- **Seite 1:** Szenario, Ziele, Regeln (Budget, KZ, CIA, E-Wert)
- **Seite 2:** Ablauf (Phasen), Formeln (vereinfacht), Glossar

**Formulare (A4-Vorlagen):**
1. **Team-Übersichtsblatt:**
   - Budget (Start, Ausgaben, Rest)
   - KZ (Startwert, Deltas, aktuell)
   - Gewählte Maßnahmen (Maßnahme, Level, Init, OPEX)
   - CIA-Werte (Team_C, Team_I, Team_A)

2. **Wellenprotokoll:**
   - Welle-Nr, Gewichte (wC/wI/wA), E-Ziel
   - Angriff (Name, baseSev, M_sum, G, Damage, KZ-Delta, CIA-Mali)
   - Events (Name, Effekt)
   - E-Wert (berechnet), Ziel erreicht? (Bonus/Malus)

3. **Auswertungstabelle:**
   - Gesamtkosten, Gesamtverluste, Vermeidete Verluste, RoS, finale KZ

**Format:** Word/Excel-Templates, ausdruckbar

**Output:** "Spieleranleitung_v1.0.pdf", "Formulare_v1.0.xlsx"

---

#### Person 3: Maßnahmenkarten + Angriffskarten (Inhalte)

**Maßnahmenkarten (8 Stück, je 1 Seite oder Karteikarten-Format):**

Beispiel M1 (IAM/PAM):
```
╔═══════════════════════════════════════════╗
║  M1: IDENTITY & ACCESS MANAGEMENT (IAM)   ║
╠═══════════════════════════════════════════╣
║ Fokus: Zugriffskontrolle, Privilegien     ║
║                                           ║
║ L1 (BASIS):                               ║
║  - Zentrale AD, MFA für Admins            ║
║  - CIA: C+2, I+1, A+0                     ║
║  - Kosten: Init 15, OPEX 2/Welle          ║
║  - Mitigation: Ransomware -1, Exfil -1    ║
║                                           ║
║ L2 (STANDARD):                            ║
║  - PAM, Rollenkonzept                     ║
║  - CIA: C+4, I+3, A+0                     ║
║  - Kosten: Init 30, OPEX 5/Welle          ║
║  - Mitigation: Ransomware -2, Exfil -2    ║
║                                           ║
║ L3 (ERWEITERT):                           ║
║  - JIT-Access, Session-Recording          ║
║  - CIA: C+6, I+5, A+1                     ║
║  - Kosten: Init 50, OPEX 10/Welle         ║
║  - Mitigation: Ransomware -3, Exfil -3    ║
║  - Abhängigkeit: M2 (SIEM) ≥ L2           ║
╚═══════════════════════════════════════════╝
```

**Angriffskarten (3 Stück):**

Beispiel Welle 1 (Ransomware):
```
╔═══════════════════════════════════════════╗
║       WELLE 1: RANSOMWARE-ANGRIFF         ║
╠═══════════════════════════════════════════╣
║ Narrative:                                ║
║ Phishing-Mail → Emotet → File-Server      ║
║ verschlüsselt. Lösegeld: 50.000€          ║
║                                           ║
║ Parameter:                                ║
║ - baseSeverity: 8                         ║
║ - sUnit: 12 (Schaden/Stufe)               ║
║ - kzUnit: 5 (KZ-Verlust/Stufe)            ║
║ - CIA-Impact: C-2, I-2, A-1 (pro Stufe G) ║
║                                           ║
║ Mitigationen:                             ║
║ - M1 (IAM): -1/-2/-3 (L1/L2/L3)           ║
║ - M2 (SIEM): -1/-2/-3                     ║
║ - M3 (EDR): -2/-3/-4                      ║
║ - M6 (Awareness): -1/-3/-4                ║
║ - M7 (Patching): -1/-2/-3                 ║
║                                           ║
║ Berechnung:                               ║
║ G = max(0, 8 - M_sum)                     ║
║ Damage = G × 12                           ║
║ KZ-Delta = -(G × 5)                       ║
╚═══════════════════════════════════════════╝
```

**Format:** Powerpoint-Slides oder Word (für Druck auf A5-Karteikarten)

**Output:** "Maßnahmenkarten_v1.0.pptx", "Angriffskarten_v1.0.pptx"

---

### ABEND (1h) - SYNC & REVIEW

**Wer:** Alle 3
**Was:**
- Dokumente teilen, gegenseitig reviewen
- Konsistenz prüfen (stimmen Zahlen überein?)
- Klären: "Ist alles für den Testlauf morgen fertig?"

**Output:** Material-Review-Protokoll

---

## TAG 3: 24.1. – Interner Testlauf

### VORMITTAG (3h) - TESTDURCHLAUF

**Setup:**
- Ihr 3 spielt das Spiel selbst durch (1 Team, komprimiert)
- 1 Person moderiert, 2 spielen
- Nach jeder Phase: Notizen machen

**Ablauf:**
- Discovery (15 Min)
- Budget (5 Min)
- Maßnahmen (10 Min)
- Welle 1 (15 Min)
- Change (10 Min)
- Welle 2 (15 Min)
- Change (10 Min)
- Welle 3 (15 Min)
- Auswertung (10 Min)

**Was beobachten:**
- ⏱ Timing: Passen die Zeiten?
- 🧮 Rechenwege: Sind Formeln klar? Fehler passiert?
- 📖 Verständlichkeit: Waren Regeln/Karten klar?
- 🎯 Balance: War ein Angriff zu hart/leicht?
- 😊 Spaßfaktor: Würde es Studierenden Spaß machen?

**Output:** Beobachtungsbogen mit Issues

---

### NACHMITTAG (3h) - ITERATION

**Wer:** Alle 3 (parallel nach Issues)
**Was:**
- Kritische Fixes (Unklarheiten beseitigen)
- Zahlen anpassen (falls Balance-Probleme)
- Material überarbeiten

**Output:** Version 1.1 (getestet)

---

### ABEND (1h) - VORBEREITUNG PLAYTEST

**Wer:** Alle 3
**Was:**
- Playtest für morgen organisieren (Testpersonen einladen?)
- Material vorbereiten (ausdrucken?)
- Beobachtungsbogen für Playtest erstellen

**Output:** Playtest-Plan

---

## TAG 4: 25.1. – Externer Playtest

### VORMITTAG (30 Min) - SETUP

- Raum vorbereiten
- Whiteboard aufbauen
- Material auslegen

---

### VORMITTAG/MITTAG (3-4h) - PLAYTEST MIT TESTPERSONEN

**Ideal:** 3-5 Personen (idealerweise WiIng-ähnlich, nicht IT-Security-Experten)

**Ihr 3:**
- Person 1: Moderiert (wie im echten Workshop)
- Person 2+3: Beobachten, Notizen machen

**Beobachtungsbogen:**
- Verständlichkeit (1-10): Waren Regeln klar?
- Timing: Wo wurde es zu lang/kurz?
- Engagement: Wann waren Teilnehmende frustriert/gelangweilt/begeistert?
- Fragen: Welche Fragen kamen immer wieder?
- Fehler: Wo haben Teams Fehler gemacht (Regelverständnis)?

**Output:** Feedback-Protokoll (ausführlich!)

---

### NACHMITTAG (2h) - RETROSPEKTIVE

**Wer:** Alle 3 + Testpersonen (wenn möglich, 20 Min Feedback-Runde)
**Was:**
- "Was war gut?"
- "Was war unklar?"
- "Was würdet ihr ändern?"

**Output:** Priorisierte Issue-Liste für Tag 5

---

## TAG 5: 26.1. – Iteration & Finalisierung

### VORMITTAG (4h) - KRITISCHE FIXES

**Wer:** Alle 3 (parallel nach Issues)
**Was:**
- Spieleranleitung überarbeiten (Unklarheiten beseitigen)
- Moderatorenleitfaden ergänzen (FAQs aus Playtest)
- Zahlen anpassen (Balance-Tweaks)
- Formulare vereinfachen (falls zu komplex)

**Output:** Version 2.0 (finale!)

---

### NACHMITTAG (3h) - DRUCK & FINALISIERUNG

**Wer:** Aufteilen
- Person 1: Druckauftrag (Arbeit) oder selbst drucken
  - Spieleranleitung (3 Teams × 2 Seiten)
  - Formulare (3 Teams × 3 Blätter)
  - Maßnahmenkarten (1 Satz, evtl. laminieren?)
  - Angriffskarten (3 Stück)
  - Moderatorenleitfaden (1× für euch 3)

- Person 2: Whiteboard-Layout vorbereiten
  - Vorlage erstellen (Foto/Sketch)
  - Marker, Post-its besorgen

- Person 3: Material-Checkliste erstellen
  - Was muss am 28.1. dabei sein?
  - Backup-Plan (falls Drucker ausfällt → alles auf Whiteboard)

**Output:** Fertige Druckunterlagen, Material-Kit

---

### ABEND (1h) - FINAL CHECK

**Wer:** Alle 3
**Was:**
- Material durchgehen (alles da?)
- Rollen für 28.1. final klären
- Letzte offene Fragen

**Output:** Ready for Generalprobe

---

## TAG 6: 27.1. – Generalprobe & Setup

### VORMITTAG (2h) - MODERATIONS-PROBE

**Wer:** Alle 3
**Was:**
- Moderations-Choreografie durchgehen:
  - Wer sagt was in welcher Phase?
  - Wie teilt ihr euch auf (3 Teams à 5 Personen)?
  - Wer macht Berechnungen? Wer erklärt Formeln?

**Ablauf simulieren (ohne zu spielen):**
- Intro (Person 1)
- Discovery (Person 1 moderiert, Person 2+3 notieren Signale)
- Maßnahmenwahl (Person 2+3 bei Teams, Person 1 am Whiteboard)
- Wellen (Person 1 erklärt, Person 2 rechnet, Person 3 unterstützt Teams)
- Debrief (alle 3)

**Output:** Moderationsskript (wer macht was, wann)

---

### NACHMITTAG (2h) - RAUM-SETUP (falls möglich)

**Falls Zugang zum Raum:**
- Whiteboard vorbereiten (Layout aufzeichnen)
- Tische arrangieren (3 Teams, räumlich getrennt)
- Material-Station einrichten

**Falls kein Zugang:**
- Raumplan zeichnen (wo steht was?)
- Material packen (Kiste mit allem)

**Output:** Setup-Plan

---

### NACHMITTAG (2h) - ENTSPANNEN 😊

**Ihr habt hart gearbeitet!** Nutzt die Zeit für:
- Mentale Vorbereitung
- Offene Fragen klären
- Evtl. Backup-Szenarien durchdenken ("Was, wenn...")

---

## TAG 7: 28.1. – WORKSHOP-DURCHFÜHRUNG 🎉

### VOR DEM WORKSHOP (1h vor Start)

- Raum aufbauen
- Whiteboard vorbereiten
- Material auslegen
- Technik testen (falls ihr was zeigen wollt?)

---

### WORKSHOP (3-4h)

**Ihr rockt das! 🚀**

**Wichtig:**
- Flexibel bleiben (wenn Zeit knapp: Welle 3 verkürzen/streichen)
- Energie managen (Pausen einplanen)
- Spaß haben!

---

### NACH DEM WORKSHOP (1h)

**Retrospektive (nur ihr 3):**
- Was lief gut?
- Was würden wir nächstes Mal ändern?
- Notizen für Version 3.0 (langfristig)

**Output:** Lessons-Learned-Dokument

---

## KRITISCHE ERFOLGSFAKTOREN

### ✅ DO's:
- **Früh testen** (Tag 3+4 sind kritisch!)
- **Flexibel bleiben** (Parameter anpassen ist ok!)
- **Kommunizieren** (täglich sync)
- **Priorisieren** (MVP first, Nice-to-haves später)

### ❌ DON'Ts:
- **Perfektionismus** (gut genug ist gut genug für Tag 1)
- **Feature-Creep** (keine zusätzlichen Events/Maßnahmen mehr!)
- **Solo-Arbeit** (tägliche Syncs sind Pflicht!)
- **Überkomplexität** (wenn unklar: vereinfachen!)

---

## BACKUP-PLÄNE

### Szenario 1: "Kein Playtest möglich (Tag 4)"
→ **Plan B:** Tag 3 interner Test ausführlicher (2× durchspielen), Tag 4 für Iteration nutzen

### Szenario 2: "Balance ist komplett off (Angriff zu stark/schwach)"
→ **Plan B:** Backup-Parameter vorbereiten (2 Sets: "leicht" und "schwer"), im Workshop flexibel anpassen

### Szenario 3: "Zeitüberschreitung im Workshop"
→ **Plan B:** Welle 3 optional machen (nur wenn Zeit), Auswertung verkürzen

### Szenario 4: "Druckmaterial kommt nicht rechtzeitig"
→ **Plan B:** Alles auf Whiteboard + Post-its (haben wir ja eh vorbereitet!)

---

## RESSOURCEN-CHECKLISTE (für 28.1.)

### Material:
- [ ] Spieleranleitung (3× gedruckt)
- [ ] Formulare (3 Teams × 3 Blätter = 9 Blätter)
- [ ] Maßnahmenkarten (8 Stück, evtl. laminiert)
- [ ] Angriffskarten (3 Stück)
- [ ] Moderatorenleitfaden (1×)
- [ ] Parametertabelle (1× für euch)
- [ ] Whiteboard-Marker (3-5 Stück, verschiedene Farben)
- [ ] Post-its (1-2 Blöcke)
- [ ] Stifte für Teams (15 Stück)
- [ ] Taschenrechner (3×)
- [ ] Timer/Stoppuhr (Handy)

### Raum:
- [ ] Whiteboard (groß genug für Layout)
- [ ] Tische für 3 Teams (je 5 Personen)
- [ ] Stühle (15 + evtl. Zuschauer)
- [ ] Evtl. Flipchart (Backup)
- [ ] Evtl. Beamer (für Intro-Slides?)

---

## FINAL THOUGHTS

**Ihr habt 6 Tage für etwas, wofür andere Monate brauchen.** Das ist sportlich, aber machbar!

**Schlüssel zum Erfolg:**
1. **Tag 1 richtig nutzen** (Konzept final, Parameter gesetzt)
2. **Parallel arbeiten** (Tag 2: jeder seine Aufgabe)
3. **Früh testen** (Tag 3+4 sind Gold wert)
4. **Pragmatisch bleiben** (MVP = Minimum VIABLE Product)

**Ihr schafft das! 💪🚀**

Bei Fragen/Problemen: Meldet euch! Ich unterstütze gerne.
