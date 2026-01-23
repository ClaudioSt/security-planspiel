# TAG 2 (23.1.) - DETAILLIERTER ARBEITSPLAN

**Ziel:** Material-Erstellung parallel (Moderatorenleitfaden, Spieleranleitung, Formulare, Druckvorbereitung)

**Team:** 3 Personen
**Zeitrahmen:** 8h (Ganztag, 09:00-17:00 + Puffer)

---

## ⏰ ZEITPLAN ÜBERSICHT

| Zeit | Person 1 | Person 2 | Person 3 |
|------|----------|----------|----------|
| **09:00-09:30** | Kick-off (alle gemeinsam) | Kick-off (alle gemeinsam) | Kick-off (alle gemeinsam) |
| **09:30-12:30** | Moderatorenleitfaden Teil 1 | Spieleranleitung | Assets drucken + Layout |
| **12:30-13:00** | Mittagspause | Mittagspause | Mittagspause |
| **13:00-16:00** | Moderatorenleitfaden Teil 2 | Formulare erstellen | Whiteboard-Layout + Maßnahmenübersicht |
| **16:00-17:00** | Review & Sync (alle gemeinsam) | Review & Sync (alle gemeinsam) | Review & Sync (alle gemeinsam) |

---

## 09:00-09:30: KICK-OFF (ALLE 3 GEMEINSAM)

### Ziel: Arbeitstag organisieren, Klarheit schaffen

**Aktivitäten:**

1. **Material-Review (10 Min)**
   - Kurz durchgehen: Was wurde gestern erstellt?
   - KONZEPT_MVP_v2.md: Sind alle Änderungen klar?
   - PARAMETER_TABELLE.md: Zahlen plausibel?

2. **Aufgabenverteilung bestätigen (10 Min)**
   - Person 1: Moderatorenleitfaden (Hauptdokument, 6-8 Seiten)
   - Person 2: Spieleranleitung + Formulare (Spieler-Perspektive)
   - Person 3: Druckvorbereitung + Visualisierung (Material + Layout)

3. **Tools & Vorlagen festlegen (5 Min)**
   - Wo arbeiten wir? (Google Docs / Word / Markdown?)
   - Gemeinsamer Ordner? (Google Drive / Dropbox?)
   - Namenskonventionen: "Moderatorenleitfaden_v1.0.docx"

4. **Offene Fragen klären (5 Min)**
   - Gibt's Unklarheiten aus gestern?
   - Braucht jemand Unterstützung?

**Output:** Jeder kennt seine Aufgabe, Tools sind ready, los geht's!

---

## 09:30-12:30: VORMITTAG (PARALLEL ARBEITEN)

---

### 👤 PERSON 1: MODERATORENLEITFADEN (Teil 1)

**Ziel:** Erste 3-4 Seiten fertigstellen (Überblick, Vorbereitung, Discovery, Budget)

**Zeit:** 3 Stunden

---

#### 09:30-10:15 (45 Min): Struktur & Überblick

**Aufgabe:** Kapitel 1-2 schreiben

**Kapitel 1: ÜBERBLICK**
- Spielziele (Was lernen Studierende?)
- Zeitplan (4h10min)
- Rollen (3 Moderatoren, 3 Teams à 5 Personen)
- Materialübersicht (was wird benötigt?)

**Vorlage:**
```markdown
# MODERATORENLEITFADEN - CIA-Planspiel MechTech

## 1. ÜBERBLICK

### 1.1 Lernziele
Die Teilnehmenden sollen verstehen:
- CIA-Trade-offs (Confidentiality, Integrity, Availability)
- Budget vs. Risiko-Abwägung
- Maßnahmen im Kontext bewerten (nicht jede "moderne" Lösung passt!)
- Return on Security (RoS) berechnen
- Kommunikation mit Stakeholdern (OEM-Audit)

### 1.2 Zeitplan (Gesamt: 4h10min)
[Tabelle aus KONZEPT_MVP_v2.md übernehmen]

### 1.3 Rollenverteilung (3 Moderatoren)
- Moderator 1 (Hauptmoderator): Discovery, Regeln, Zeitmanagement
- Moderator 2 (Angriffsmeister): Wellen auflösen, Berechnungen
- Moderator 3 (Team-Coach): Zwischen Teams rotieren, Fragen

### 1.4 Material-Checkliste
[Alle benötigten Materialien auflisten]
```

**Output:** Kapitel 1-2 fertig (ca. 1,5 Seiten)

---

#### 10:15-11:15 (60 Min): Vorbereitung & Discovery

**Aufgabe:** Kapitel 3-4 schreiben

**Kapitel 3: VORBEREITUNG (vor dem Workshop)**
- Raum-Setup (Whiteboard, Tische, Material-Station)
- Material auslegen (Assets, Karten, Formulare)
- Whiteboard vorbereiten (Maßnahmen-Markt, Formeln)
- Technische Tests (falls Beamer/Präsentation)

**Kapitel 4: PHASE 1 - DISCOVERY (25 Min)**
- Ablauf Schritt-für-Schritt
- Wie Assets verteilen (1-3 sofort, 4-5 bei Bedarf)
- Fragebogen nutzen (DISCOVERY_FRAGEBOGEN.md referenzieren)
- Signal-Scoring (OT/Compliance/IP)
- Budget-Empfehlung ableiten
- Zusammenfassung für Teams

**Vorlage:**
```markdown
## 4. PHASE 1: DISCOVERY (25 Min)

### 4.1 Ablauf (Minute für Minute)

**Min 0-2: Assets verteilen**
- Jedes Team erhält:
  ✓ Asset 1 (Email)
  ✓ Asset 2 (Zeitung)
  ✓ Asset 3 (Steckbrief)
- Moderator: "Ihr seid Berater. Diese Anfrage ist heute gekommen. Lest euch ein (5 Min)."

**Min 2-7: Teams lesen**
- Teams lesen Assets still
- Moderator bereitet Fragebogen vor (DISCOVERY_FRAGEBOGEN.md)

**Min 7-22: Fragen-Runde**
- Teams stellen Fragen
- Moderator beantwortet mit Fragebogen
- Signal-Scoring intern notieren (OT/Compliance/IP)
- Bei passenden Fragen:
  → Asset 4 (OEM-Brief) ausgeben
  → Asset 5 (Netzwerk) ausgeben

**Scoring-Beispiel:**
Team fragt: "Wie kritisch ist Produktionsausfall?"
→ Antwort: "8.000€/h, ab 4h Vertragsstrafen"
→ Score: OT-Kritikalität +4

**Min 22-25: Zusammenfassung**
- Moderator fasst zusammen:
  "Ich sehe: OT sehr kritisch (18 Punkte), Compliance-Druck hoch (12), IP-Schutz mittel (8)."
- Budget-Empfehlung: "Kunde wäre bereit, 350-400k€ zu investieren."

### 4.2 Troubleshooting
- **Team fragt nicht weiter:** Hilfestellungen geben (siehe Fragebogen)
- **Team zu detailliert:** "Fokussiert auf Business-Impact!"
- **Zeit überzogen:** Nach 20 Min abbrechen, zusammenfassen
```

**Output:** Kapitel 3-4 fertig (ca. 2 Seiten)

---

#### 11:15-12:00 (45 Min): Budget-Verhandlung & Maßnahmenwahl

**Aufgabe:** Kapitel 5-6 schreiben

**Kapitel 5: PHASE 2 - BUDGET-VERHANDLUNG (10 Min)**
- Wie Teams zur Entscheidung führen
- Trade-offs erklären (niedrig/mittel/hoch)
- Budget notieren (Whiteboard)

**Kapitel 6: PHASE 3 - MASSNAHMENWAHL (20 Min)**
- Maßnahmen-Markt am Whiteboard zeigen
- Abhängigkeiten prüfen (z.B. M1 L3 braucht M2 L2)
- Kosten berechnen (Init + OPEX)
- Teams notieren auf Team-Übersichtsblatt
- CIA-Werte summieren

**Vorlage:**
```markdown
## 6. PHASE 3: MASSNAHMENWAHL (20 Min)

### 6.1 Maßnahmen-Markt präsentieren
- Moderator zeigt Whiteboard: 10 Maßnahmen (M1-M10)
- Hinweis: "M9 (Cloud) und M10 (MDM) könnten suboptimal sein!"
- Teams haben 15 Min Entscheidungszeit

### 6.2 Abhängigkeiten prüfen
- Wenn Team M1 L3 wählt:
  → Prüfen: Ist M2 ≥ L2 gewählt?
  → Wenn nein: "M1 L3 braucht M2 L2 als Voraussetzung!"

### 6.3 Kosten & CIA berechnen
- Teams füllen Team-Übersichtsblatt aus:
  | Maßnahme | Level | Init | OPEX | CIA |
  |----------|-------|------|------|-----|
  | M5 OT-Seg | L3 | 110 | 12 | 4/3/8 |
  | ... | ... | ... | ... | ... |

- SUMME berechnen:
  - Gesamt Init: [...]
  - Gesamt OPEX/Welle: [...]
  - Team-CIA: C=[...], I=[...], A=[...]

### 6.4 Budget-Check
- Moderator prüft: "Passt Init ins Budget?"
- Warnung: "Denkt an 3 Wellen OPEX!"
```

**Output:** Kapitel 5-6 fertig (ca. 1,5 Seiten)

---

#### 12:00-12:30 (30 Min): Puffer / Feinschliff

- Kapitel 1-6 nochmal durchlesen
- Formatierung verbessern
- Offene Fragen notieren

**Output Teil 1:** Moderatorenleitfaden Seiten 1-4 fertig!

---

### 👤 PERSON 2: SPIELERANLEITUNG

**Ziel:** 2-seitige Spieleranleitung für Studierende

**Zeit:** 3 Stunden

---

#### 09:30-10:30 (60 Min): Seite 1 - Szenario & Ziele

**Aufgabe:** Seite 1 erstellen

**Inhalt Seite 1:**
1. **Szenario** (MechTech GmbH, was ist die Situation?)
2. **Eure Rolle** (Beratungsteam)
3. **Spielziel** (Budget, KZ, RoS optimieren)
4. **Kernkonzepte** (Budget, KZ, CIA, E-Wert)

**Vorlage:**
```markdown
# SPIELERANLEITUNG - CIA-Planspiel

## WILLKOMMEN!

Ihr seid ein Beratungsteam. Euer Kunde, die MechTech GmbH (Automotive-Zulieferer), braucht eure Hilfe: Ein wichtiger OEM fordert IT-Sicherheit. Gleichzeitig bedrohen Cyberangriffe die Produktion.

### EURE AUFGABE
- Budget verhandeln (200-500k€)
- Sicherheitsmaßnahmen auswählen (10 zur Auswahl)
- 3 Angriffswellen überstehen
- Kundenzufriedenheit (KZ) hochhalten
- Return on Security (RoS) maximieren

### WICHTIGE KENNZAHLEN

**Budget (B):**
- Euer Projektbudget in 1.000€
- Wird für Maßnahmen ausgegeben (Init + OPEX)

**Kundenzufriedenheit (KZ):**
- Skala 0-100
- Start je nach Budget (50-70)
- Sinkt bei Angriffen, steigt bei guter Performance
- Bei KZ <20: Vertrag verloren!

**CIA-Werte (Schutzziele):**
- **C** (Confidentiality): Vertraulichkeit (Daten schützen)
- **I** (Integrity): Integrität (Daten korrekt)
- **A** (Availability): Verfügbarkeit (Systeme laufen)
- Jede Maßnahme trägt zu C/I/A bei

**E-Wert (Erfüllungsgrad):**
- E = Team_C × wC + Team_I × wI + Team_A × wA
- Jede Welle hat andere Gewichte (wC/wI/wA)
- Ziel: E-Wert ≥ E-Ziel erreichen (KZ-Bonus!)

### SPIELABLAUF (3-4h)
1. Discovery: Kunde befragen (25 Min)
2. Budget verhandeln (10 Min)
3. Maßnahmen wählen (20 Min)
4. Welle 1: Ransomware (25 Min)
5. Change-Fenster (15 Min)
6. Welle 2: OT-Störung (25 Min)
7. Change-Fenster (15 Min)
8. Welle 3: Datenexfiltration (25 Min)
9. Auswertung & Debrief (50 Min)
```

**Output:** Seite 1 fertig (ca. 1 Seite)

---

#### 10:30-11:30 (60 Min): Seite 2 - Regeln & Formeln

**Aufgabe:** Seite 2 erstellen

**Inhalt Seite 2:**
1. **Maßnahmen-Levels** (L1/L2/L3)
2. **Angriffe** (wie funktioniert die Auflösung?)
3. **Formeln** (vereinfacht!)
4. **Glossar** (wichtige Begriffe)

**Vorlage:**
```markdown
## MASSNAHMEN (L1/L2/L3)

Ihr könnt 10 Maßnahmen wählen. Jede in 3 Leveln:
- **L1 (Basis):** Günstig, wenig Wirkung
- **L2 (Standard):** Mittel, gute Wirkung
- **L3 (Erweitert):** Teuer, hohe Wirkung

**Wichtig:**
- Manche Maßnahmen haben **Abhängigkeiten** (z.B. M1 L3 braucht M2 L2)
- **Kontext-Boni:** Manche Maßnahmen wirken besonders gut in bestimmten Szenarien!
  (z.B. M5 OT-Segmentierung gegen OT-Angriff: +2 Bonus!)

**Kosten:**
- **Init:** Einmalig bei Auswahl
- **OPEX:** Pro Welle (3 Wellen = 3× OPEX!)

## ANGRIFFE (3 Wellen)

Jede Welle bringt 1 Angriff:
- **Welle 1:** Ransomware (Office-IT)
- **Welle 2:** OT-Störung (Produktion)
- **Welle 3:** Datenexfiltration (IP-Diebstahl)

**Wie werden Angriffe aufgelöst?**

1. **Mitigation-Summe:** Eure Maßnahmen reduzieren den Angriff
   - M_sum = Summe aller passenden Maßnahmen (inkl. Kontext-Boni!)

2. **Endschwere:** G = baseSeverity - M_sum (min. 0)
   - Je niedriger G, desto besser!

3. **Schaden:** Damage = G × sUnit (in 1.000€)
   - Kommt vom Budget ab!

4. **KZ-Verlust:** ΔKZ = -(G × kzUnit)
   - KZ sinkt!

5. **CIA-Mali:** Temporäre Reduktion eurer CIA-Werte

**Beispiel:**
- Angriff: baseSeverity = 8, sUnit = 12
- Eure Mitigations: -5 (EDR) -4 (Awareness) = 9
- G = max(0, 8 - 9) = 0 ← Perfekt abgewehrt!
- Damage = 0, ΔKZ = 0

## FORMELN (QUICK REFERENCE)

**E-Wert:**
```
E = Team_C × wC + Team_I × wI + Team_A × wA
```

**Return on Security (RoS):**
```
Gesamtkosten = Init + (OPEX × 3 Wellen)
Verluste = Summe(Damage)
Basisverluste = Summe(baseSeverity × sUnit) ohne Mitigation
Vermiedene Verluste = Basisverluste - Verluste
RoS = (Vermiedene Verluste - Gesamtkosten) / Gesamtkosten
```

## GLOSSAR

- **baseSeverity:** Ausgangsschwere eines Angriffs
- **sUnit:** Schaden pro Schwerestufe (in 1.000€)
- **kzUnit:** KZ-Verlust pro Schwerestufe
- **Mitigation:** Reduktion der Angriffsschwere durch Maßnahmen
- **wC/wI/wA:** Gewichte pro Welle (ändern sich!)
- **E-Ziel:** Mindest-E-Wert für KZ-Bonus

## TIPPS

✓ **Breite schlägt Tiefe:** Lieber mehrere Maßnahmen auf L2 als eine auf L3!
✓ **Kontext beachten:** M5 (OT-Seg) ist GOLD gegen Welle 2!
✓ **OPEX einkalkulieren:** 3 Wellen × OPEX = viel Geld!
✓ **Suboptimale Maßnahmen meiden:** M9 (Cloud) + M10 (MDM) passen nicht zu MechTech!

**VIEL ERFOLG! 🚀**
```

**Output:** Seite 2 fertig (ca. 1 Seite)

---

#### 11:30-12:30 (60 Min): Layout & Feinschliff

- Formatierung verbessern (Überschriften, Boxen, Listen)
- Grafiken einfügen? (z.B. Formel-Diagramm, Ablauf-Flowchart)
- Als PDF exportieren

**Output:** Spieleranleitung_v1.0.pdf fertig (2 Seiten)!

---

### 👤 PERSON 3: ASSETS DRUCKEN & LAYOUT

**Ziel:** Discovery-Assets drucken, Whiteboard-Layout entwerfen, Maßnahmenübersicht erstellen

**Zeit:** 3 Stunden

---

#### 09:30-10:30 (60 Min): Assets drucken

**Aufgabe:** Alle Discovery-Assets als A4 drucken (oder druckfertig machen)

**Checkliste:**

**Zu drucken (pro Team = 3× Teams):**
- [ ] 3× Asset 1 (Email-Anfrage)
- [ ] 3× Asset 2 (Zeitungsartikel)
- [ ] 3× Asset 3 (Unternehmens-Steckbrief)
- [ ] 3× Asset 4 (OEM-Audit-Brief) - bereithalten
- [ ] 3× Asset 5 (Netzwerk-Skizze) - bereithalten

**Gesamt: 15 Blätter A4**

**Vorgehen:**
1. ASSETS_DRUCKVORLAGEN.md öffnen
2. Jedes Asset in Word/Google Docs kopieren
3. Formatierung prüfen (A4, gut lesbar, evtl. Rahmen/Boxen)
4. Drucken oder als PDF speichern (für Druckauftrag morgen)

**Tipp:** Falls kein Drucker heute verfügbar → als PDFs speichern, morgen früh drucken lassen

**Output:** 15 Seiten gedruckt oder druckfertig!

---

#### 10:30-11:30 (60 Min): Whiteboard-Layout entwerfen

**Aufgabe:** Whiteboard-Layout skizzieren (als Vorlage für 28.1.)

**Was muss aufs Whiteboard?**

**Links (1/3 des Boards): WELLEN-INFO**
```
┌─────────────────────────────┐
│ AKTUELLE WELLE: 1           │
│ Angriff: Ransomware         │
│ Gewichte: wC=0.4, wI=0.4,   │
│           wA=0.2            │
│ E-Ziel: [30/40/50]          │
│                             │
│ EVENTS:                     │
│ - (leer am Start)           │
└─────────────────────────────┘
```

**Mitte (1/3): TEAM-ÜBERSICHT**
```
┌────────────────────────────────────────┐
│ TEAM 1    │ TEAM 2    │ TEAM 3        │
│───────────│───────────│───────────    │
│ Budget:   │ Budget:   │ Budget:       │
│ 320       │ 350       │ 280           │
│           │           │               │
│ KZ: 60    │ KZ: 55    │ KZ: 70        │
│           │           │               │
│ CIA:      │ CIA:      │ CIA:          │
│ 19/24/16  │ 22/20/18  │ 15/18/20      │
└────────────────────────────────────────┘
```

**Rechts (1/3): MASSNAHMEN-MARKT**
```
┌─────────────────────────────┐
│ MASSNAHMEN (10 Stück)       │
│─────────────────────────────│
│ M1: IAM/PAM                 │
│  L1: 30/4  L2: 60/10  L3: ..│
│                             │
│ M2: SIEM/MDR                │
│  L1: 20/2  L2: 50/8  L3: .. │
│                             │
│ M3: EDR/XDR                 │
│ ...                         │
│                             │
│ M9: Cloud ❌ (suboptimal!)   │
│ M10: MDM ❌ (suboptimal!)    │
└─────────────────────────────┘
```

**Unten: FORMELN (Referenz)**
```
┌──────────────────────────────────────────────────┐
│ FORMELN:                                         │
│ G = max(0, baseSeverity - M_sum)                 │
│ Damage = G × sUnit                               │
│ ΔKZ = -(G × kzUnit)                              │
│ E = Team_C × wC + Team_I × wI + Team_A × wA      │
└──────────────────────────────────────────────────┘
```

**Vorgehen:**
1. Skizze zeichnen (Powerpoint/Sketch/Papier+Foto)
2. Bereiche markieren, Größen abschätzen
3. Als Foto/PDF speichern (Vorlage für 28.1.)

**Output:** Whiteboard-Layout-Vorlage.pdf oder .jpg!

---

#### 11:30-12:30 (60 Min): Maßnahmenübersicht (A4 für Teams)

**Aufgabe:** Kompakte Maßnahmen-Übersicht erstellen (1-2 Seiten A4 pro Team)

**Inhalt:**
- Alle 10 Maßnahmen auf einen Blick
- Pro Maßnahme: L1/L2/L3 (CIA, Kosten, Mitigations, Abhängigkeiten)
- Kontext-Boni markieren!

**Vorlage (Tabelle):**

```
MASSNAHMEN-ÜBERSICHT (MechTech-Planspiel)

M1: IAM/PAM - Zugriffskontrolle
┌──────┬──────────┬─────────┬──────────────────────────────┬────────────┐
│ Level│ CIA      │ Kosten  │ Mitigation                   │ Abhängigkeit│
│      │          │ Init/OPEX│                              │            │
├──────┼──────────┼─────────┼──────────────────────────────┼────────────┤
│ L1   │ 2/1/0    │ 30/4    │ Ransomware -1, Exfil -1      │ -          │
│ L2   │ 4/3/0    │ 60/10   │ Ransomware -2, Exfil -2      │ -          │
│ L3   │ 6/5/1    │ 100/20  │ Ransomware -3, Exfil -4 ⭐   │ M2 ≥ L2    │
└──────┴──────────┴─────────┴──────────────────────────────┴────────────┘
⭐ = Kontext-Bonus (+1): PAM verhindert Lateral Movement

M2: Logging & SIEM/MDR - Sichtbarkeit
[...]

(alle 10 Maßnahmen)
```

**Vorgehen:**
1. MASSNAHMENKARTEN.md als Quelle nutzen
2. In Word/Excel als Tabelle formatieren
3. Kontext-Boni mit ⭐ markieren
4. Als PDF exportieren (3× drucken für Teams)

**Output:** Massnahmen-Uebersicht.pdf (1-2 Seiten), 3× drucken!

---

## 12:30-13:00: MITTAGSPAUSE (ALLE)

- Gemeinsam Pause machen
- Kurzer informeller Austausch: "Wie läuft's?"
- Energie tanken!

---

## 13:00-16:00: NACHMITTAG (PARALLEL ARBEITEN)

---

### 👤 PERSON 1: MODERATORENLEITFADEN (Teil 2)

**Ziel:** Seiten 5-8 fertigstellen (Wellen, Auswertung, Troubleshooting)

**Zeit:** 3 Stunden

---

#### 13:00-14:00 (60 Min): Wellen auflösen

**Aufgabe:** Kapitel 7 schreiben

**Kapitel 7: PHASE 4 - WELLEN AUFLÖSEN (3× 25 Min)**

**Inhalt:**
- Schritt-für-Schritt-Ablauf (gilt für alle 3 Wellen)
- Berechnungen durchführen
- Whiteboard aktualisieren
- Teams informieren

**Vorlage:**
```markdown
## 7. PHASE 4: WELLEN AUFLÖSEN (je 25 Min)

### 7.1 Ablauf (gilt für alle 3 Wellen)

**Schritt 1: Narrative vorlesen (2 Min)**
- Moderator liest Angriffs-Narrative vor (siehe ANGRIFFSKARTEN.md)
- Spannung aufbauen!
- Beispiel Welle 1: "Montag, 08:15 Uhr. Ein Mitarbeiter öffnet..."

**Schritt 2: Teams sammeln Mitigations (5 Min)**
- Teams schauen: Welche Maßnahmen wirken gegen diesen Angriff?
- Teams notieren auf Wellenprotokoll:
  | Maßnahme | Level | Mitigation |
  |----------|-------|------------|
  | M3 EDR | L3 | -5 (inkl. Bonus!) |
  | M6 Awareness | L2 | -4 (inkl. Bonus!) |

**Schritt 3: Moderator berechnet (5 Min)**
- M_sum = Summe Mitigations (min. MIT_CAP)
- G = max(0, baseSeverity - M_sum)
- Damage = G × sUnit
- ΔKZ = -(G × kzUnit)
- CIA-Mali = G × ciaImpactPerStep

**Wichtig:** Laut rechnen! Transparenz!

**Beispiel (Welle 1, gut vorbereitet):**
```
Team hat: M3 L3 (-5), M6 L2 (-4), M4 L2 (-2)
M_sum = min(10, 5+4+2) = 10
G = max(0, 8 - 10) = 0
→ Perfekt abgewehrt!
Damage = 0
ΔKZ = 0
```

**Schritt 4: Recovery anwenden (falls M4 vorhanden)**
- Wenn Team M4 (Backup) hat:
  - Recovery-Faktor anwenden
  - Damage_final = Damage × (1 - Recovery_Faktor)
  - Beispiel L2: Damage_final = Damage × 0.7

**Schritt 5: E-Ziel prüfen (3 Min)**
- E-Wert berechnen: E = Team_C × wC + Team_I × wI + Team_A × wA
- Mit E-Ziel vergleichen
- KZ-Bonus (+3/+5/+8) oder Malus (-5/-8/-10)

**Schritt 6: Whiteboard aktualisieren (5 Min)**
- Neues Budget (alt - Damage)
- Neue KZ (alt + ΔKZ + E-Bonus/Malus)
- Neue CIA (temporär reduziert)

**Schritt 7: Teams informieren (5 Min)**
- Moderator erklärt Ergebnisse
- Teams notieren auf Wellenprotokoll
- Kurze Reflexion: "Was hättet ihr anders machen können?"

### 7.2 Besonderheiten pro Welle

**Welle 1: Ransomware**
- Fokus: C+I (wC=0.4, wI=0.4, wA=0.2)
- Beste Abwehr: M6 (Awareness), M3 (EDR)
- Lerneffekt: Awareness + Backup sind Gold wert!

**Welle 2: OT-Störung** ⚠️
- Fokus: A (wC=0.2, wI=0.2, wA=0.6)
- Beste Abwehr: M5 (OT-Segmentierung) ⭐
- baseSev=10, sUnit=20 → HÄRTE!
- **Event danach:** OEM-Audit auslösen
  - Wenn E_Welle1 ≥ E-Ziel → KZ +5
  - Wenn E_Welle1 < E-Ziel → KZ -3

**Welle 3: Datenexfiltration**
- Fokus: C (wC=0.5, wI=0.3, wA=0.2)
- Beste Abwehr: M1 (IAM) L3, M2 (SIEM) L3, M8 (Supplier)
- Lerneffekt: Lieferanten-Sicherheit wichtig!
- **Event möglich:** DSGVO-Bonus
  - Wenn M1 ≥ L2 UND M2 ≥ L2 → KZ +3, Budget +10
```

**Output:** Kapitel 7 fertig (ca. 2 Seiten)

---

#### 14:00-15:00 (60 Min): Change-Fenster, Auswertung, Debrief

**Aufgabe:** Kapitel 8-10 schreiben

**Kapitel 8: PHASE 5 - CHANGE-FENSTER (2× 15 Min)**
- Regeln: Upgrades (L1→L2→L3), Swaps (eine raus, eine rein)
- Wirksam ab nächster Welle
- Kommunikationseffekt auf KZ (optional)
- Change-Gebühren (optional)

**Kapitel 9: PHASE 6 - AUSWERTUNG (15 Min)**
- Tabellen ausfüllen (aus README.md)
- RoS berechnen
- Finale Kennzahlen vergleichen

**Kapitel 10: DEBRIEF (20 Min + 15 Min Feedback)**
- Reflexionsfragen:
  - "Was waren eure wichtigsten Learnings?"
  - "Welche Trade-offs habt ihr erlebt?"
  - "Was würdet ihr anders machen?"
  - "Wie habt ihr Kontext-Boni genutzt?"
- Spiel-Feedback (15 Min):
  - "War das Spiel verständlich?"
  - "Waren Regeln klar?"
  - "Spaßfaktor?"
  - "Verbesserungsvorschläge?"

**Output:** Kapitel 8-10 fertig (ca. 1,5 Seiten)

---

#### 15:00-16:00 (60 Min): Troubleshooting & FAQ

**Aufgabe:** Kapitel 11 schreiben

**Kapitel 11: TROUBLESHOOTING & FAQ**

**Häufige Fehler:**
- Team vergisst OPEX (3 Wellen!) → Budget-Defizit
- Team wählt M1 L3 ohne M2 L2 → Abhängigkeit nicht erfüllt
- Team rechnet Mitigation falsch (Kontext-Boni vergessen)
- Team verwechselt Init und OPEX

**FAQs:**
- "Können wir mehrere Level einer Maßnahme wählen?" → Nein, nur ein Level pro Maßnahme
- "Wirkt M4 (Backup) Recovery auch auf KZ?" → Nein, nur auf Damage
- "Was passiert bei KZ=0?" → Vertrag verloren, Spiel endet (theoretisch)
- "Können wir Maßnahmen verkaufen?" → Nein, nur Upgrades/Swaps im Change-Fenster

**Wenn Zeit überschritten:**
- Welle 3 verkürzen (nur Berechnung, kein Change-Fenster danach)
- Auswertung verkürzen (nur RoS, nicht alle Tabellen)

**Output:** Kapitel 11 fertig (ca. 1 Seite)

**GESAMT:** Moderatorenleitfaden komplett (6-8 Seiten)!

---

### 👤 PERSON 2: FORMULARE ERSTELLEN

**Ziel:** 3 Formular-Templates (A4, Excel oder Word)

**Zeit:** 3 Stunden

---

#### 13:00-14:00 (60 Min): Team-Übersichtsblatt

**Aufgabe:** Formular 1 erstellen

**Inhalt:**
- Budget (Start, Ausgaben, aktuell)
- KZ (Start, Deltas, aktuell)
- Gewählte Maßnahmen (Maßnahme, Level, Init, OPEX)
- Team-CIA (Summe C/I/A)

**Vorlage (Excel/Word-Tabelle):**
```
╔═══════════════════════════════════════════════════════════╗
║           TEAM-ÜBERSICHTSBLATT - TEAM [Nr]                ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  BUDGET                                                   ║
║  ─────────────────────────────────────────────────────────║
║  Startbudget:         [____] k€                           ║
║  Gesamt Init:         [____] k€                           ║
║  OPEX/Welle:          [____] k€                           ║
║  Budget nach Init:    [____] k€                           ║
║                                                           ║
║  Budget nach Welle 1: [____] k€                           ║
║  Budget nach Welle 2: [____] k€                           ║
║  Budget nach Welle 3: [____] k€                           ║
║                                                           ║
║  KUNDENZUFRIEDENHEIT (KZ)                                 ║
║  ─────────────────────────────────────────────────────────║
║  KZ-Start:            [____]                              ║
║  KZ nach Welle 1:     [____]                              ║
║  KZ nach Welle 2:     [____]                              ║
║  KZ nach Welle 3:     [____] (FINAL)                      ║
║                                                           ║
║  GEWÄHLTE MASSNAHMEN                                      ║
║  ─────────────────────────────────────────────────────────║
║  | Maßnahme   | Level | Init | OPEX | CIA (C/I/A) |      ║
║  |────────────|───────|──────|──────|─────────────|      ║
║  |            |       |      |      |             |      ║
║  |            |       |      |      |             |      ║
║  |            |       |      |      |             |      ║
║  |            |       |      |      |             |      ║
║  |            |       |      |      |             |      ║
║  |────────────|───────|──────|──────|─────────────|      ║
║  | SUMME      |       |[___] |[___] |[___/___/___]|      ║
║                                                           ║
║  TEAM-CIA (Summe):   C = [___]   I = [___]   A = [___]   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

**Output:** Team-Uebersichtsblatt.xlsx (3× drucken für Teams)

---

#### 14:00-15:00 (60 Min): Wellenprotokoll

**Aufgabe:** Formular 2 erstellen (pro Welle 1 Blatt)

**Inhalt:**
- Wellen-Info (Nr, Gewichte, E-Ziel)
- Angriff (Name, Parameter)
- Mitigation-Berechnung
- Damage, KZ-Delta, CIA-Mali
- Events
- E-Wert, Ziel erreicht?

**Vorlage:**
```
╔═══════════════════════════════════════════════════════════╗
║           WELLENPROTOKOLL - WELLE [Nr]                    ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  WELLEN-INFO                                              ║
║  ─────────────────────────────────────────────────────────║
║  Gewichte:  wC = [___]   wI = [___]   wA = [___]          ║
║  E-Ziel:    [___]                                         ║
║                                                           ║
║  ANGRIFF                                                  ║
║  ─────────────────────────────────────────────────────────║
║  Name:          [_________________]                       ║
║  baseSeverity:  [___]                                     ║
║  sUnit:         [___] k€                                  ║
║  kzUnit:        [___]                                     ║
║                                                           ║
║  MITIGATION-BERECHNUNG                                    ║
║  ─────────────────────────────────────────────────────────║
║  | Maßnahme   | Level | Mitigation (inkl. Bonus) |       ║
║  |────────────|───────|─────────────────────────|       ║
║  |            |       |                         |       ║
║  |            |       |                         |       ║
║  |────────────|───────|─────────────────────────|       ║
║  M_sum = [___] (min. MIT_CAP = [___])                     ║
║                                                           ║
║  ERGEBNIS                                                 ║
║  ─────────────────────────────────────────────────────────║
║  G (Endschwere):    [___]                                 ║
║  Damage:            [___] k€                              ║
║  Recovery-Faktor:   [___]% (falls M4 vorhanden)           ║
║  Damage (final):    [___] k€                              ║
║  ΔKZ:               [___]                                 ║
║  CIA-Mali:          C [___]  I [___]  A [___]             ║
║                                                           ║
║  E-WERT                                                   ║
║  ─────────────────────────────────────────────────────────║
║  E = Team_C × wC + Team_I × wI + Team_A × wA              ║
║  E = [___] × [___] + [___] × [___] + [___] × [___]        ║
║  E = [___]                                                ║
║                                                           ║
║  E-Ziel erreicht?   ☐ Ja (+[___] KZ)   ☐ Nein (-[___] KZ)║
║                                                           ║
║  EVENTS                                                   ║
║  ─────────────────────────────────────────────────────────║
║  [_______________________________________]                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

**Output:** Wellenprotokoll.xlsx (3 Blätter pro Team, also 9 Blätter gesamt)

---

#### 15:00-16:00 (60 Min): Auswertungstabelle & RoS

**Aufgabe:** Formular 3 erstellen

**Inhalt:**
- Gesamtkosten
- Gesamtverluste
- Basisverluste (ohne Mitigation)
- Vermiedene Verluste
- RoS
- Finale KZ

**Vorlage:**
```
╔═══════════════════════════════════════════════════════════╗
║           AUSWERTUNG & RETURN ON SECURITY (RoS)           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  GESAMTKOSTEN                                             ║
║  ─────────────────────────────────────────────────────────║
║  Gesamt Init:               [____] k€                     ║
║  Gesamt OPEX (3 Wellen):    [____] k€                     ║
║  Event-Strafen:             [____] k€                     ║
║  ───────────────────────────────────────────────────      ║
║  GESAMT:                    [____] k€                     ║
║                                                           ║
║  VERLUSTE                                                 ║
║  ─────────────────────────────────────────────────────────║
║  Welle 1 Damage:            [____] k€                     ║
║  Welle 2 Damage:            [____] k€                     ║
║  Welle 3 Damage:            [____] k€                     ║
║  ───────────────────────────────────────────────────      ║
║  GESAMT:                    [____] k€                     ║
║                                                           ║
║  BASISVERLUSTE (ohne Mitigation)                          ║
║  ─────────────────────────────────────────────────────────║
║  Welle 1: 8 × 12 =          [____] k€                     ║
║  Welle 2: 10 × 20 =         [____] k€                     ║
║  Welle 3: 7 × 15 =          [____] k€                     ║
║  ───────────────────────────────────────────────────      ║
║  GESAMT:                    [____] k€                     ║
║                                                           ║
║  VERMIEDENE VERLUSTE                                      ║
║  ─────────────────────────────────────────────────────────║
║  Basisverluste - Tatsächliche Verluste:                   ║
║  [____] - [____] = [____] k€                              ║
║                                                           ║
║  RETURN ON SECURITY (RoS)                                 ║
║  ─────────────────────────────────────────────────────────║
║  RoS = (Vermiedene Verluste - Gesamtkosten) / Gesamtkosten
║                                                           ║
║  RoS = ([____] - [____]) / [____]                         ║
║  RoS = [____] / [____]                                    ║
║  RoS = [____]%                                            ║
║                                                           ║
║  FINALE KUNDENZUFRIEDENHEIT                               ║
║  ─────────────────────────────────────────────────────────║
║  KZ (final):    [____] / 100                              ║
║                                                           ║
║  FAZIT                                                    ║
║  ─────────────────────────────────────────────────────────║
║  [                                                    ]    ║
║  [                                                    ]    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

**Output:** Auswertung_RoS.xlsx (3× für Teams)

**GESAMT:** 3 Formulare fertig!

---

### 👤 PERSON 3: WHITEBOARD-LAYOUT & MASSNAHMEN-ÜBERSICHT

**Ziel:** Whiteboard-Vorlage finalisieren, Maßnahmenübersicht fertigstellen

**Zeit:** 3 Stunden

---

#### 13:00-14:30 (90 Min): Whiteboard-Layout detaillieren

**Aufgabe:** Whiteboard-Skizze vom Vormittag verfeinern

**Vorgehen:**
1. Vormittags-Skizze nehmen
2. Details ergänzen:
   - Welche Informationen wo?
   - Wie groß müssen Bereiche sein?
   - Welche Farben/Marker nutzen?

3. **Maßnahmen-Markt detaillieren:**
   ```
   M1: IAM/PAM
   L1: Init 30, OPEX 4, CIA 2/1/0
   L2: Init 60, OPEX 10, CIA 4/3/0
   L3: Init 100, OPEX 20, CIA 6/5/1, (Abhängig: M2≥L2)

   M2: SIEM/MDR
   [...]

   M9: Cloud ❌
   M10: MDM ❌
   ```

4. **Formeln-Bereich:**
   ```
   ┌─────────────────────────────────────────────┐
   │ BERECHNUNGEN:                               │
   │ 1. M_sum = Σ Mitigations (max. MIT_CAP)     │
   │ 2. G = max(0, baseSeverity - M_sum)         │
   │ 3. Damage = G × sUnit (in k€)               │
   │ 4. ΔKZ = -(G × kzUnit)                      │
   │ 5. E = Team_C×wC + Team_I×wI + Team_A×wA    │
   └─────────────────────────────────────────────┘
   ```

5. **Foto/Scan erstellen** (als Vorlage für 28.1.)

**Output:** Whiteboard-Layout_Final.pdf

---

#### 14:30-16:00 (90 Min): Maßnahmenübersicht finalisieren

**Aufgabe:** Vom Vormittag begonnene Übersicht fertigstellen

**Vorgehen:**
1. Vormittags-Entwurf nehmen
2. Alle 10 Maßnahmen eintragen
3. Kontext-Boni ⭐ markieren
4. Abhängigkeiten klar darstellen
5. Formatierung: Lesbar aus 1-2m Entfernung
6. Als PDF exportieren (3× drucken)

**Zusatz: Schnellreferenz-Karte erstellen (optional, 1 Seite)**
- Top-Maßnahmen pro Welle:
  - Welle 1: M6 L3, M3 L3, M4 L2
  - Welle 2: M5 L3, M7 L2
  - Welle 3: M1 L3, M2 L3, M8 L3
- Suboptimale Maßnahmen: M9, M10

**Output:** Massnahmen-Uebersicht_Final.pdf (3×)

---

## 16:00-17:00: REVIEW & SYNC (ALLE 3 GEMEINSAM)

### Ziel: Material gegenseitig reviewen, Konsistenz prüfen, Plan für morgen

**Aktivitäten:**

---

#### 16:00-16:30 (30 Min): Material-Review

**Person 1 präsentiert:** Moderatorenleitfaden (5 Min Schnelldurchlauf)
- Alle 3 lesen Kapitel 1-2
- Feedback: Verständlich? Vollständig?

**Person 2 präsentiert:** Spieleranleitung + Formulare (5 Min)
- Spieleranleitung durchblättern
- Formulare prüfen: Passen sie zusammen?

**Person 3 präsentiert:** Whiteboard-Layout + Maßnahmenübersicht (5 Min)
- Layout zeigen
- Maßnahmenübersicht prüfen

**Gegenseitiges Feedback:** (10 Min)
- Sind Zahlen konsistent? (Parameter überall gleich?)
- Passen Formulare zum Leitfaden?
- Fehlt etwas?

---

#### 16:30-16:50 (20 Min): Konsistenz-Check

**Gemeinsam durchgehen:**

1. **Zahlen-Check:**
   - Person 1: Zahlen im Leitfaden
   - Person 2: Zahlen in Formularen
   - Person 3: Zahlen auf Maßnahmenübersicht
   - → Vergleichen mit PARAMETER_TABELLE.md

2. **Vollständigkeits-Check:**
   - [ ] Moderatorenleitfaden: 6-8 Seiten ✓
   - [ ] Spieleranleitung: 2 Seiten ✓
   - [ ] Formulare: 3 Stück ✓
   - [ ] Assets: 5 Stück (15× für Teams) ✓
   - [ ] Whiteboard-Layout: Vorlage ✓
   - [ ] Maßnahmenübersicht: 3× ✓

3. **Issue-Liste erstellen:**
   - Was muss morgen noch gefixt werden?
   - Was fehlt noch?

---

#### 16:50-17:00 (10 Min): Plan für morgen (Tag 3)

**Morgen:** Interner Testdurchlauf!

**Vorbereitung heute Abend (jeder für sich, 30-60 Min):**
- Person 1: Leitfaden nochmal lesen, Notizen machen
- Person 2: Formulare ausdrucken (je 1× Probe)
- Person 3: Material packen (was nehmen wir morgen mit?)

**Morgen Ablauf (kurz besprechen):**
- 09:00: Setup (Whiteboard aufbauen, Material auslegen)
- 09:30: Start Testdurchlauf (1 Team = wir 3)
- 12:00: Testdurchlauf Ende
- 12:00-12:30: Pause
- 12:30-15:00: Iteration (Issues fixen)
- 15:00-16:00: Vorbereitung Playtest (Samstag)

---

## 17:00: FEIERABEND! 🎉

**Checklist für heute:**
- ✅ Moderatorenleitfaden fertig (6-8 Seiten)
- ✅ Spieleranleitung fertig (2 Seiten)
- ✅ 3 Formulare fertig
- ✅ 5 Discovery-Assets gedruckt/druckfertig (15×)
- ✅ Whiteboard-Layout-Vorlage
- ✅ Maßnahmenübersicht (3×)
- ✅ Review done, Konsistenz geprüft
- ✅ Plan für morgen steht

**Ihr habt heute:**
- 🎯 Alle Spieler- und Moderatoren-Materialien erstellt
- 🎯 Druckvorlagen vorbereitet
- 🎯 Visualisierungen designt
- 🎯 Alles reviewed und abgestimmt

**Morgen:** Testen, testen, testen! 🚀

---

## MATERIAL-CHECKLISTE (für 28.1.)

**Zum Drucken (bis Montag 27.1.):**
- [ ] 3× Spieleranleitung (2 Seiten)
- [ ] 3× Team-Übersichtsblatt
- [ ] 9× Wellenprotokoll (3 Wellen × 3 Teams)
- [ ] 3× Auswertung/RoS
- [ ] 15× Discovery-Assets (5 Assets × 3 Teams)
- [ ] 3× Maßnahmenübersicht
- [ ] 1× Moderatorenleitfaden (für euch)
- [ ] 1× Whiteboard-Layout-Vorlage (als Referenz)

**Gesamt:** ca. 40 Seiten

**Sonstiges Material:**
- [ ] Whiteboard-Marker (3-5 Stück, versch. Farben)
- [ ] Post-its (2 Blöcke)
- [ ] Stifte für Teams (15×)
- [ ] Taschenrechner (3×)
- [ ] Timer/Stoppuhr (Handy)

---

## TIPPS FÜR EFFIZIENTES ARBEITEN

### Kommunikation:
- **Kurze Syncs zwischendurch** (alle 90 Min, 5 Min):
  "Wie läuft's? Braucht jemand Hilfe?"
- **Gemeinsamer Chat/Kanal** für schnelle Fragen
- **Störungen minimieren:** Fokuszeit nutzen!

### Tools:
- **Gemeinsamer Ordner** (Google Drive/Dropbox):
  - `/Moderatorenleitfaden`
  - `/Spieleranleitung`
  - `/Formulare`
  - `/Assets`
  - `/Vorlagen`

### Pausen:
- Alle 90 Min: 5-10 Min Pause
- Mittagspause gemeinsam nutzen (sozialer Kit!)
- Bei Müdigkeit: Kurz rausgehen, Bewegung!

---

**Viel Erfolg morgen! Ihr schafft das! 💪🎯**
