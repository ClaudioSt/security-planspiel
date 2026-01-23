# MVP-Konzept v2.0 - ÜBERARBEITETE VERSION

**Änderungen basierend auf Feedback vom 22.1.2026**

---

## WICHTIGSTE ÄNDERUNGEN

### ✅ Beibehalten:
- 8 Maßnahmen (gut so!)
- 3 Wellen mit je 1 Angriff
- Strukturierte + explorative Discovery
- Zeitrahmen 3-4h

### 🔄 Angepasst:
1. **Budget-System:** Realistischere Zahlen (200-500k€)
2. **Kontext-Bonus-Mechanik:** Maßnahmen wirken extra, wenn sie zum Szenario passen
3. **Suboptimale Maßnahmen:** 2-3 Maßnahmen passen bewusst NICHT optimal
4. **Discovery-Assets:** Immersive Materialien (Email, Zeitung, Präsentation)
5. **Feedback-Runde:** 15 Min Spiel-Feedback explizit eingeplant

---

## 1. NEUES BUDGET-SYSTEM

### Budget-Logik (realistischer)

**1 Budgetpunkt = 1.000€ Beratungsbudget**

**Kontext:**
- 5 Berater á 100€/Stunde
- 1 Beratertag (8h) = 800€ × 5 Personen = 4.000€
- 1 Beraterwoche = 20.000€ = 20 Budgetpunkte
- 1 Quartal (12 Wochen) = 240 Budgetpunkte

**Budget-Range: 200-500 Budgetpunkte** (= 200.000€ - 500.000€)

### Trade-offs (neu)

| Startbudget | KZ-Start | Erwartung (E-Ziele) | Trade-off |
|-------------|----------|---------------------|-----------|
| **200-280 (niedrig)** | **KZ = 70** | E-Ziele: 30/40/50 | "Kostenoptimiert" - Kunde zahlt wenig, erwartet weniger |
| **281-380 (mittel)** | **KZ = 60** | E-Ziele: 40/50/60 | "Standard-Projekt" - normale Erwartungen |
| **381-500 (hoch)** | **KZ = 50** | E-Ziele: 50/60/70 | "Premium-Engagement" - hohe Investition, hohe Erwartungen |

**Discovery-Einfluss:**
Je nach Discovery-Signalen gibt Moderator Budget-Empfehlung:
- Hohe OT-Kritikalität + Audit-Druck → "Kunde bietet 380-500"
- Niedrige Risiken → "Kunde denkt 200-280"

**Verhandlung:**
Teams können höheres Budget begründen:
- "Wir brauchen 420k€, weil OT-Segmentierung kritisch ist" → Moderator entscheidet (+ evt. KZ-Malus für höheres Budget)

---

## 2. KONTEXT-BONUS-MECHANIK

### Konzept: CIA-Basis + Szenario-Fit

**Jede Maßnahme hat:**
1. **CIA-Beitrag** (grundsätzliche Wirkung)
2. **Basis-Mitigation** (gegen alle passenden Angriffe)
3. **Kontext-Bonus** (wenn besonders zum Szenario passend)

**Beispiel: OT-Segmentierung gegen OT-Störung (Welle 2)**

- **Basis-Mitigation:** -1/-3/-5 (L1/L2/L3) - wirkt durch CIA-A-Beitrag
- **Kontext-Bonus:** +2 zusätzlich auf L2 und L3 (weil explizit für OT designed)
- **Effektiv:** -1/-5/-7 Mitigation gegen OT-Störung

**Beispiel: EDR gegen Ransomware (Welle 1)**

- **Basis-Mitigation:** -2/-3/-4 (L1/L2/L3) - wirkt durch CIA-C+I-Beitrag
- **Kontext-Bonus:** +1 auf L3 (weil moderne EDR Ransomware besonders gut erkennt)
- **Effektiv:** -2/-3/-5 Mitigation gegen Ransomware

### Wie kommunizieren im Spiel?

**Auf Maßnahmenkarten:**
```
M5: OT/IT-Netz-Segmentierung

L2 (Standard):
- CIA: C+3, I+2, A+6
- Kosten: Init 70, OPEX 6
- Mitigation:
  • OT-Störung: -3 (Basis) +2 (OT-Bonus) = -5
  • Ransomware: -1
```

**Transparenz:** Teams sehen, WELCHE Maßnahmen besonders zum Kontext passen!

---

## 3. ÜBERARBEITETE MASSNAHMEN (8 + 2 suboptimal)

### KERNMASSNAHMEN (optimal für MechTech)

#### M1: Identity & Access Management (IAM/PAM) ✅
**Passt zu:** Alle Angriffe (Zugriffsschutz)

- **L1:** CIA C+2/I+1/A+0, Init 30, OPEX 4
  - Ransomware: -1, Exfiltration: -1
- **L2:** CIA C+4/I+3/A+0, Init 60, OPEX 10
  - Ransomware: -2, Exfiltration: -2
- **L3:** CIA C+6/I+5/A+1, Init 100, OPEX 20
  - Ransomware: -3, Exfiltration: -3 +1 (Kontext: PAM verhindert Lateral Movement)
  - **Abhängigkeit:** M2 ≥ L2

---

#### M2: Logging & SIEM/MDR ✅
**Passt zu:** Alle Angriffe (Sichtbarkeit)

- **L1:** CIA C+1/I+3/A+0, Init 20, OPEX 2
  - Ransomware: -1, OT-Störung: 0, Exfiltration: -1
- **L2:** CIA C+2/I+5/A+1, Init 50, OPEX 8
  - Ransomware: -2, OT-Störung: -1, Exfiltration: -2
- **L3:** CIA C+3/I+7/A+2, Init 80, OPEX 24
  - Ransomware: -3, OT-Störung: -2, Exfiltration: -3 +1 (Kontext: MDR erkennt APT-Muster)

---

#### M3: Endpoint Detection & Response (EDR/XDR) ✅
**Passt zu:** Ransomware, Exfiltration (Malware-Schutz)

- **L1:** CIA C+3/I+2/A+1, Init 24, OPEX 4
  - Ransomware: -2, Exfiltration: -1
- **L2:** CIA C+5/I+4/A+2, Init 56, OPEX 10
  - Ransomware: -3, Exfiltration: -2
- **L3:** CIA C+7/I+6/A+3, Init 90, OPEX 18
  - Ransomware: -4 +1 (Kontext: Behavioral Analysis stoppt Crypto-Trojaner)
  - Exfiltration: -3
  - **Abhängigkeit:** M2 ≥ L2

---

#### M4: Backup & Disaster Recovery ✅
**Passt zu:** Ransomware, OT-Störung (Wiederherstellung)

- **L1:** CIA C+0/I+4/A+3, Init 16, OPEX 6
  - Ransomware: -1, OT-Störung: 0
  - **Recovery-Faktor:** 10% (Schaden-Reduktion nach Angriff)
- **L2:** CIA C+1/I+6/A+5, Init 40, OPEX 12
  - Ransomware: -2, OT-Störung: -1
  - **Recovery-Faktor:** 30%
- **L3:** CIA C+1/I+8/A+7, Init 80, OPEX 20
  - Ransomware: -4 +1 (Kontext: Immutable Backups verhindern Verschlüsselung)
  - OT-Störung: -2
  - **Recovery-Faktor:** 50%

---

#### M5: OT/IT-Netz-Segmentierung ✅
**Passt zu:** OT-Störung (OT-Schutz!)

- **L1:** CIA C+2/I+1/A+4, Init 40, OPEX 2
  - OT-Störung: -1, Ransomware: 0
- **L2:** CIA C+3/I+2/A+6, Init 70, OPEX 6
  - OT-Störung: -3 +2 (Kontext: Kern-Maßnahme für OT-Schutz!)
  - Ransomware: -1
- **L3:** CIA C+4/I+3/A+8, Init 110, OPEX 12
  - OT-Störung: -5 +2 (Kontext: Micro-Segmentierung + IDS/IPS)
  - Ransomware: -2

---

#### M6: Security Awareness & Training ✅
**Passt zu:** Ransomware (Phishing-Abwehr!)

- **L1:** CIA C+2/I+1/A+1, Init 10, OPEX 2
  - Ransomware: -1
- **L2:** CIA C+3/I+2/A+2, Init 24, OPEX 6
  - Ransomware: -3 +1 (Kontext: Simuliertes Phishing reduziert Klickrate drastisch)
- **L3:** CIA C+5/I+3/A+3, Init 40, OPEX 10
  - Ransomware: -4 +2 (Kontext: Incident-Meldeprozess beschleunigt Reaktion)

---

#### M7: Vulnerability & Patch Management ✅
**Passt zu:** Alle Angriffe (Schwachstellen schließen)

- **L1:** CIA C+2/I+3/A+2, Init 20, OPEX 4
  - Ransomware: -1, OT-Störung: -1, Exfiltration: 0
- **L2:** CIA C+4/I+5/A+3, Init 44, OPEX 8
  - Ransomware: -2, OT-Störung: -2 +1 (Kontext: OT-Patches reduzieren Angriffsfläche)
  - Exfiltration: -1
- **L3:** CIA C+6/I+7/A+4, Init 76, OPEX 14
  - Ransomware: -3, OT-Störung: -3 +1 (Kontext)
  - Exfiltration: -2
  - **Abhängigkeit:** M2 ≥ L1

---

#### M8: Supplier Security & Supply Chain ⚠️ (moderat passend)
**Passt zu:** Exfiltration, OT-Störung (Lieferanten-Risiken)

- **L1:** CIA C+1/I+2/A+2, Init 16, OPEX 4
  - OT-Störung: 0, Exfiltration: 0
- **L2:** CIA C+2/I+4/A+4, Init 36, OPEX 8
  - OT-Störung: -1, Exfiltration: -1
- **L3:** CIA C+3/I+6/A+6, Init 70, OPEX 16
  - OT-Störung: -2, Exfiltration: -2 +1 (Kontext: Lieferant war Einfallstor in Welle 3)

**Warum moderat?** Passt zum Szenario, aber KEIN starker Kontext-Bonus (nur auf L3 gegen Exfiltration).

---

### SUBOPTIMALE MASSNAHMEN (bewusst weniger passend)

#### M9: Cloud Security Posture Management (CSPM) ❌
**Warum suboptimal?** MechTech nutzt wenig Cloud (nur Backup-SaaS).

- **L1:** CIA C+2/I+2/A+1, Init 18, OPEX 3
  - **KEINE Mitigation gegen Angriffe** (Cloud nicht im Angriffsvektor)
- **L2:** CIA C+3/I+3/A+2, Init 40, OPEX 7
  - **KEINE Mitigation**
- **L3:** CIA C+4/I+4/A+3, Init 70, OPEX 14
  - Exfiltration: -1 (nur minimal, falls Cloud-Backup kompromittiert)

**Narrative:** "Ihr könntet Cloud-Security stärken, aber ist das wirklich eure Priorität?"

**Lerneffekt:** Teams sollen erkennen: Passt nicht zum Kontext!

---

#### M10: Mobile Device Management (MDM) ❌
**Warum suboptimal?** Kaum Mobilgeräte im OT/Produktion.

- **L1:** CIA C+1/I+1/A+0, Init 12, OPEX 2
  - Ransomware: 0 (Mobilgeräte nicht primäres Einfallstor)
- **L2:** CIA C+2/I+2/A+1, Init 28, OPEX 5
  - Ransomware: -1 (minimal)
- **L3:** CIA C+3/I+3/A+2, Init 50, OPEX 10
  - Ransomware: -1

**Narrative:** "Außendienst nutzt Tablets für Bestellungen, aber ist MDM kritisch für euch?"

**Lerneffekt:** Klar suboptimal - wenig Wirkung.

---

## 4. DISCOVERY-ASSETS (immersiv!)

### Material-Paket für Teams

#### Asset 1: Email-Anfrage (Initialzündung)
```
Von: Dr. Thomas Weber <t.weber@mechtech-gmbh.de>
An: security-consulting@ihr-team.de
Betreff: Anfrage: IT-Security-Beratung für MechTech GmbH

Sehr geehrte Damen und Herren,

wir sind MechTech GmbH, Zulieferer für Präzisionsteile im E-Mobility-Bereich.
Unser Hauptkunde (großer OEM) fordert bis Q3 eine ISO 27001-Zertifizierung.

Parallel lesen wir täglich von Ransomware-Angriffen in unserer Branche.
Wir möchten unsere IT-Sicherheit systematisch aufbauen, wissen aber nicht,
wo wir anfangen sollen.

Könnten Sie uns unterstützen? Wir hätten ein Budget für ein Beratungsprojekt.

Beste Grüße,
Dr. Thomas Weber
Geschäftsführer, MechTech GmbH
```

---

#### Asset 2: Zeitungsartikel (Kontext schaffen)
```
═══════════════════════════════════════════════
  AUTOMOTIVE WEEKLY | 12. Januar 2026
═══════════════════════════════════════════════

RANSOMWARE LEGT ZULIEFERER LAHM

Kassel. Ein mittelständischer Automotive-Zulieferer wurde
Opfer eines Ransomware-Angriffs. Die Produktion stand für
72 Stunden still. Lösegeld: 250.000 Euro.

"Wir hatten kein Backup-Konzept", so der Geschäftsführer.
Der Angriff erfolgte über eine Phishing-Mail an einen
Mitarbeiter. Die Erpresser verschlüsselten nicht nur
Office-Daten, sondern auch das MES-System.

Experten raten: "OT und IT müssen getrennt werden.
Awareness-Schulungen sind Gold wert."

Der Vorfall zeigt: Auch kleine Zulieferer sind Ziele.
═══════════════════════════════════════════════
```

---

#### Asset 3: Unternehmens-Steckbrief (1 Seite)
```
╔═══════════════════════════════════════════════════╗
║         MECHTECH GMBH - UNTERNEHMENSPROFIL        ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║  PRODUKTE:                                        ║
║  • Präzisions-Getriebeteile für E-Antriebe        ║
║  • CNC-gefräste Komponenten (Toleranz <10µm)      ║
║  • Prototyping für OEMs                           ║
║                                                   ║
║  STANDORT:                                        ║
║  • Hauptsitz Süddeutschland, 1 Produktionshalle   ║
║  • ~80 Mitarbeitende (50 Produktion, 30 Verwaltung)
║                                                   ║
║  UMSATZ:                                          ║
║  • ~15 Mio. EUR/Jahr                              ║
║  • Hauptkunde: Deutscher Premium-OEM (60% Umsatz) ║
║                                                   ║
║  IT-INFRASTRUKTUR (vereinfacht):                  ║
║  • Office-IT: Windows-Domäne, SharePoint, CAD     ║
║  • OT/Produktion: MES-System (Siemens), 3 CNC-Linien
║  • SaaS: CRM (Salesforce), Cloud-Backup (Veeam)   ║
║  • IT-Team: 2 Admins (extern unterstützt)         ║
║                                                   ║
║  BESONDERHEITEN:                                  ║
║  • 24/5-Betrieb (Produktion Mo-Fr, 3 Schichten)   ║
║  • Liefertermintreue kritisch (JIT für OEM)       ║
║  • Konstruktionsdaten = Wettbewerbsvorteil        ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

---

#### Asset 4: OEM-Audit-Ankündigung (Druck aufbauen)
```
Von: Klaus Hoffmann <k.hoffmann@oem-customer.com>
An: Dr. Thomas Weber <t.weber@mechtech-gmbh.de>
Betreff: Information Security Assessment - Q2/2026

Sehr geehrter Herr Dr. Weber,

im Rahmen unserer Supplier-Security-Initiative werden wir
alle Zulieferer in Q2/2026 einem IT-Security-Audit unterziehen.

Erwartete Nachweise:
- ISO 27001-Zertifizierung (mind. in Vorbereitung)
- Incident Response Plan
- Netz-Segmentierung OT/IT
- Backup-Konzept mit Restore-Tests
- Awareness-Schulungen dokumentiert

Termin: KW 20 (Mitte Mai 2026)

Bei kritischen Lücken behalten wir uns vor, Aufträge
zurückzustellen.

Beste Grüße,
Klaus Hoffmann
Supplier Quality Management
```

---

#### Asset 5 (Optional): Netzwerk-Skizze (vereinfacht)
```
         ┌─────────────────────────────────┐
         │     INTERNET / FIREWALL         │
         └──────────┬──────────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
    ┌────▼─────┐         ┌────▼──────┐
    │ OFFICE-IT │         │ SaaS-Cloud│
    │           │         │ (CRM/Backup)
    │ - AD/Mail │         └───────────┘
    │ - SharePoint│
    │ - CAD      │
    └────┬───────┘
         │ ⚠️ KEINE Firewall!
    ┌────▼────────┐
    │ OT/PRODUKTION│
    │             │
    │ - MES       │
    │ - 3× CNC    │
    │ - SPS/PLC   │
    └─────────────┘

⚠️ Problem: Office + OT im selben Netz!
```

---

### Wie einsetzen im Workshop?

**Phase 1: Intro (10 Min)**
- Teams erhalten **Asset 1 (Email)** + **Asset 2 (Zeitung)** + **Asset 3 (Steckbrief)**
- Moderator präsentiert: "Ihr habt diese Anfrage bekommen. Was macht ihr?"

**Phase 2: Discovery (25 Min)**
- Teams lesen Assets (5 Min)
- Stellen Fragen (15 Min)
  - Bei guten Fragen → Moderator gibt **Asset 4 (OEM-Brief)** oder **Asset 5 (Netzwerk)**
  - Bei Fragen zu "Budget": Moderator nennt Range basierend auf Signalen
- Zusammenfassung (5 Min)

**Vorteil:** Teams haben greifbares Material, fühlen sich wie echte Berater!

---

## 5. ANGEPASSTER ZEITPLAN (mit Feedback-Runde)

| Phase | Dauer | Aktivität |
|-------|-------|-----------|
| **Intro** | 10 Min | Begrüßung, Spielregeln, Asset-Verteilung |
| **Discovery** | 25 Min | Assets lesen + Fragen + Signale sammeln |
| **Budget-Verhandlung** | 10 Min | Teams verhandeln Budget (200-500k€) |
| **Maßnahmenwahl** | 20 Min | Teams wählen aus 10 Maßnahmen (inkl. suboptimale) |
| **Welle 1** | 25 Min | Ransomware-Angriff auflösen |
| **Change 1** | 15 Min | Upgrades/Swaps |
| **Welle 2** | 25 Min | OT-Störung + Event |
| **Change 2** | 15 Min | Letzte Anpassungen |
| **Welle 3** | 25 Min | Datenexfiltration + Event |
| **Pause** | 10 Min | ☕ Kurze Verschnaufpause |
| **Auswertung** | 15 Min | Tabellen ausfüllen, RoS berechnen |
| **Debrief (Learnings)** | 20 Min | Reflexion: Was gelernt? Trade-offs? |
| **Feedback zum Spiel** | 15 Min | Meta-Ebene: War Spiel klar? Spaß? Verbesserungen? |
| **Gesamt** | **~4h 10 Min** | (inkl. Puffer) |

**Feedback-Runde-Fragen:**
1. War das Spiel verständlich? (1-10)
2. Waren die Regeln klar? Was war unklar?
3. Hattet ihr Spaß? Wo war es langweilig/stressig?
4. Waren die Materialien hilfreich?
5. Was würdet ihr ändern?
6. Würdet ihr es weiterempfehlen?

---

## 6. OFFENE FRAGEN / NÄCHSTE SCHRITTE

### Feedback benötigt:

1. **Budget 200-500k€:** Passt die Range? Zu hoch/niedrig?
2. **Kontext-Bonus:** Ist die Mechanik verständlich? (Basis + Kontext-Bonus)
3. **Suboptimale Maßnahmen:** CSPM + MDM ok? Oder andere Ideen?
4. **Discovery-Assets:** Sind 5 Assets (Email, Zeitung, Steckbrief, OEM-Brief, Netzwerk) genug? Zu viel?
5. **Zeitplan 4h10min:** Passt das? Oder kürzen?
6. **10 Maßnahmen (8 gut + 2 suboptimal):** Zu viele zum Auswählen? Oder gut für Lerneffekt?

### Was ich als Nächstes erstellen kann:

- ✅ **Discovery-Fragebogen** (15 Fragen + Antworten für Moderatoren)
- ✅ **Parametertabelle (Excel)** mit allen neuen Zahlen
- ✅ **Assets als Druckvorlagen** (Email, Zeitung, Steckbrief, etc.)
- ✅ **Maßnahmenkarten v2** (mit Kontext-Boni)
- ✅ **Angriffskarten v2** (mit Kontext-Bonus-Logik)

**Gebt grünes Licht, und ich lege los! 🚀**
