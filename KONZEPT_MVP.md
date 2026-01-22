# MVP-Konzept für Workshop 28.1.2026

**Status:** ENTWURF - Feedback erwünscht!
**Ziel:** 3 Wellen, 3-4 Stunden Spielzeit, Wirtschaftsingenieur-Studierende

---

## 1. SZENARIO & SETTING

**Unternehmen:** MechTech GmbH - Automotive-Zulieferer
**Produkte:** Präzisionsteile für E-Antriebe (hohe Qualitätsanforderungen)
**IT-Landschaft:**
- Office-IT (ca. 80 Mitarbeitende, SharePoint, E-Mail, CAD-Systeme)
- OT/Produktion (MES-System steuert 3 Fertigungslinien, 24/5-Betrieb)
- SaaS-Anwendungen (CRM, Lieferanten-Portal, Cloud-Backup)
- IP-Assets (Konstruktionsdaten, Prozess-Know-how)

**Kontext:**
- Wichtiger OEM-Kunde (Automotive-Hersteller) fordert ISO 27001-Zertifizierung bis Q3
- Wettbewerbsdruck: Liefertermintreue ist kritisch
- Ihr seid das externe Beratungsteam

---

## 2. MASSNAHMEN-KATALOG (8 Maßnahmen)

### M1: Identity & Access Management (IAM/PAM)
**Fokus:** Wer darf was? Privilegierte Zugriffe absichern

- **L1 (Basis):** Zentrale AD, MFA für Admins, Passwortrichtlinie
- **L2 (Standard):** PAM für privilegierte Accounts, Rollenkonzept dokumentiert
- **L3 (Erweitert):** JIT-Access, Session-Recording, regelmäßige Access-Reviews

**CIA-Beitrag:** C+2/I+1/A+0 (L1), C+4/I+3/A+0 (L2), C+6/I+5/A+1 (L3)
**Kosten:** Init 15/30/50, OPEX 2/5/10 (pro Welle)
**Abhängigkeiten:** L3 benötigt M2 (Logging) mind. L2
**Mitigation gegen:** Ransomware (-1/-2/-3), Phishing/BEC (-0/-1/-2), Datenexfiltration (-1/-2/-3)

---

### M2: Logging & SIEM/MDR
**Fokus:** Sichtbarkeit schaffen, Angriffe erkennen

- **L1 (Basis):** Windows Event Logs zentral sammeln, 30 Tage Aufbewahrung
- **L2 (Standard):** SIEM mit Use Cases (Failed Logins, Privilege Escalation), 90 Tage
- **L3 (Erweitert):** MDR (Managed Detection & Response) mit 24/7-SOC

**CIA-Beitrag:** C+1/I+3/A+0 (L1), C+2/I+5/A+1 (L2), C+3/I+7/A+2 (L3)
**Kosten:** Init 10/25/40, OPEX 1/4/12
**Abhängigkeiten:** keine
**Mitigation gegen:** Ransomware (-1/-2/-3), OT-Störung (-0/-1/-2), Datenexfiltration (-1/-2/-3)

---

### M3: Endpoint Detection & Response (EDR/XDR)
**Fokus:** Schadsoftware auf Clients/Servern erkennen und stoppen

- **L1 (Basis):** Aktueller Virenscanner, automatische Updates
- **L2 (Standard):** EDR mit Behavioral Analysis, Auto-Isolation
- **L3 (Erweitert):** XDR (Korrelation über Endpoints, Netzwerk, Cloud)

**CIA-Beitrag:** C+3/I+2/A+1 (L1), C+5/I+4/A+2 (L2), C+7/I+6/A+3 (L3)
**Kosten:** Init 12/28/45, OPEX 2/5/9
**Abhängigkeiten:** L3 benötigt M2 (SIEM) mind. L2
**Mitigation gegen:** Ransomware (-2/-3/-4), Phishing/BEC (-1/-2/-3), OT-Störung (-0/-1/-2)

---

### M4: Backup & Disaster Recovery
**Fokus:** Daten wiederherstellen, Betrieb aufrechterhalten

- **L1 (Basis):** Tägliche Backups Office-IT, 14 Tage Aufbewahrung, kein Restore-Test
- **L2 (Standard):** 3-2-1-Regel (3 Kopien, 2 Medien, 1 offsite), monatliche Restore-Tests
- **L3 (Erweitert):** Immutable Backups (Air-Gap), DR-Plan dokumentiert + geübt, RTO <4h

**CIA-Beitrag:** C+0/I+4/A+3 (L1), C+1/I+6/A+5 (L2), C+1/I+8/A+7 (L3)
**Kosten:** Init 8/20/40, OPEX 3/6/10
**Abhängigkeiten:** keine
**Mitigation gegen:** Ransomware (-1/-2/-4), OT-Störung (-0/-1/-2)
**Spezial:** **Recovery-Faktor** (reduziert Schaden nach Angriff): L1=10%, L2=30%, L3=50%

---

### M5: OT/IT-Netz-Segmentierung
**Fokus:** Produktionsnetz vom Office-Netz trennen

- **L1 (Basis):** Logische VLANs, keine Firewall-Regeln
- **L2 (Standard):** Firewall zwischen OT/IT, Whitelist-Prinzip
- **L3 (Erweitert):** IDS/IPS in OT, Micro-Segmentierung (Zonen pro Fertigungslinie)

**CIA-Beitrag:** C+2/I+1/A+4 (L1), C+3/I+2/A+6 (L2), C+4/I+3/A+8 (L3)
**Kosten:** Init 20/35/55, OPEX 1/3/6
**Abhängigkeiten:** keine
**Mitigation gegen:** OT-Störung (-1/-3/-5), Ransomware (-0/-1/-2)

---

### M6: Security Awareness & Training
**Fokus:** Mitarbeitende sensibilisieren, Social Engineering abwehren

- **L1 (Basis):** Jährliche Pflicht-Schulung (E-Learning, 30 Min)
- **L2 (Standard):** Quartalsweise Schulungen + simulierte Phishing-Kampagnen
- **L3 (Erweitert):** Rollenspezifisches Training, monatliche Mini-Sessions, Incident-Meldeprozess etabliert

**CIA-Beitrag:** C+2/I+1/A+1 (L1), C+3/I+2/A+2 (L2), C+5/I+3/A+3 (L3)
**Kosten:** Init 5/12/20, OPEX 1/3/5
**Abhängigkeiten:** keine
**Mitigation gegen:** Phishing/BEC (-1/-3/-4), Ransomware (-0/-1/-2)

---

### M7: Vulnerability & Patch Management
**Fokus:** Schwachstellen schließen, bevor sie ausgenutzt werden

- **L1 (Basis):** Automatische Windows-Updates, sporadische Patch-Zyklen
- **L2 (Standard):** Monatliche Patch-Zyklen, Vulnerability-Scanning (quartalsweise)
- **L3 (Erweitert):** Risk-basiertes Patching (CVSS), wöchentliche Scans, Patch-Management-Tool

**CIA-Beitrag:** C+2/I+3/A+2 (L1), C+4/I+5/A+3 (L2), C+6/I+7/A+4 (L3)
**Kosten:** Init 10/22/38, OPEX 2/4/7
**Abhängigkeiten:** L3 benötigt M2 (Logging) mind. L1
**Mitigation gegen:** Ransomware (-1/-2/-3), OT-Störung (-1/-2/-3), Datenexfiltration (-0/-1/-2)

---

### M8: Supplier Security & Supply Chain
**Fokus:** Lieferanten-Risiken managen, Abhängigkeiten absichern

- **L1 (Basis):** Vertragliche Security-Klauseln, Ad-hoc-Checks
- **L2 (Standard):** Supplier-Assessments (jährlich), SLA-Monitoring
- **L3 (Erweitert):** Continuous Monitoring, Dual-Sourcing-Strategie, Escrow-Vereinbarungen

**CIA-Beitrag:** C+1/I+2/A+2 (L1), C+2/I+4/A+4 (L2), C+3/I+6/A+6 (L3)
**Kosten:** Init 8/18/35, OPEX 2/4/8
**Abhängigkeiten:** keine
**Mitigation gegen:** OT-Störung (-0/-1/-2), Datenexfiltration (-0/-1/-1)

---

## 3. ANGRIFFE (3 Wellen)

### WELLE 1: Ransomware-Angriff (Office-IT)
**Fokus:** Confidentiality & Integrity
**Gewichte:** wC=0.4, wI=0.4, wA=0.2
**E-Ziel:** 25 (bei Erreichen: KZ +3, bei Verfehlen: KZ -5)

**Angriff:** Emotet-basierte Ransomware verschlüsselt File-Server und SharePoint

- **baseSeverity:** 8
- **sUnit:** 12 (Schaden pro Schwerestufe G)
- **kzUnit:** 5 (KZ-Verlust pro Schwerestufe G)
- **ciaImpactPerStep:** C-2, I-2, A-1 (pro Stufe G)
- **Mitigations:** M1 (IAM), M2 (SIEM), M3 (EDR), M6 (Awareness), M7 (Patching)

**Narrative:**
"Ein Mitarbeiter öffnet einen Anhang in einer Phishing-Mail. Innerhalb von 2 Stunden sind Dateifreigaben und SharePoint verschlüsselt. Die Angreifer fordern 50.000€ Lösegeld."

**Learnings:** Awareness ist Gold wert, Backups retten den Tag, EDR kann früh stoppen.

---

### WELLE 2: OT-Störung (Produktionsausfall)
**Fokus:** Availability
**Gewichte:** wC=0.2, wI=0.2, wA=0.6
**E-Ziel:** 30 (bei Erreichen: KZ +5, bei Verfehlen: KZ -8)

**Angriff:** Malware infiltriert MES-System über ungepatchte OT-Komponente

- **baseSeverity:** 10
- **sUnit:** 20 (hoher wirtschaftlicher Schaden: Produktionsstillstand!)
- **kzUnit:** 8
- **ciaImpactPerStep:** C-1, I-2, A-3
- **Mitigations:** M2 (SIEM), M5 (Segmentierung), M7 (Patching), M8 (Supplier Security)

**Narrative:**
"Eine Schwachstelle in der SPS-Software wird ausgenutzt. Fertigungslinie 2 fällt für 18 Stunden aus. Liefertermine an den OEM sind gefährdet."

**Learnings:** OT ist kritisch, Segmentierung wirkt wie eine Firewall, Patching auch in der Produktion wichtig.

---

### WELLE 3: Datenexfiltration (IP-Diebstahl)
**Fokus:** Confidentiality (aber auch Integrity)
**Gewichte:** wC=0.5, wI=0.3, wA=0.2
**E-Ziel:** 35 (bei Erreichen: KZ +8, bei Verfehlen: KZ -10)

**Angriff:** APT-ähnlicher Angreifer stiehlt Konstruktionsdaten über kompromittierten Admin-Account

- **baseSeverity:** 7
- **sUnit:** 15 (mittelfristig: Wettbewerbsnachteil, Vertrauensverlust OEM)
- **kzUnit:** 6
- **ciaImpactPerStep:** C-3, I-1, A-0
- **Mitigations:** M1 (IAM/PAM), M2 (SIEM), M3 (EDR), M7 (Patching), M8 (Supplier)

**Narrative:**
"Über einen kompromittierten Lieferanten-Zugang gelangt ein Angreifer ins Netzwerk. Unbemerkt werden CAD-Dateien und Prozessdokumente exfiltriert. Der OEM-Kunde erfährt davon durch einen Hinweis des BSI."

**Learnings:** PAM hätte geholfen, SIEM hätte Anomalien erkannt, Supplier Security ist kein "Nice-to-have".

---

## 4. EVENTS (2-3 Stück)

### Event 1: "OEM-Audit angekündigt"
**Trigger:** Automatisch in Welle 2 (zeitbasiert)
**Effekt:**
- Wenn E-Wert Welle 1 ≥ 25: KZ +5 ("Audit läuft smooth")
- Wenn E-Wert Welle 1 < 25: KZ -3 ("Audit findet Lücken")

**Narrative:**
"Euer Hauptkunde kündigt ein Security-Audit für Q2 an. Je nach eurem Reifegrad wirkt sich das auf die Geschäftsbeziehung aus."

---

### Event 2: "Mitarbeiter-Fluktuation im IT-Team"
**Trigger:** Wenn M6 (Awareness) < L2 am Ende Welle 1
**Effekt:**
- OPEX +5 (Nachbesetzung, Knowledge-Loss)
- KZ -2 (Instabilität)

**Narrative:**
"Zwei erfahrene Admins verlassen das Unternehmen. Fehlende Wertschätzung und Überlastung waren Gründe."

---

### Event 3 (optional): "Neue Datenschutz-Anforderung (DSGVO-Audit)"
**Trigger:** Wenn M1 (IAM) ≥ L2 UND M2 (Logging) ≥ L2 am Ende Welle 2
**Effekt:**
- KZ +3 ("Compliance ready")
- Budget +10 (Förderung vom Branchenverband)

**Narrative:**
"Durch eure gute Vorbereitung könnt ihr kurzfristig eine Datenschutz-Zertifizierung erlangen. Das bringt Wettbewerbsvorteile."

---

## 5. BUDGET-MECHANIK (Trade-offs)

### Budget-Range & KZ-Start

**Verhandlungsziel:** Teams einigen sich auf ein Startbudget zwischen 80 und 150 Punkten.

| Startbudget | KZ-Start | Erwartung (E-Ziele) | Trade-off |
|-------------|----------|---------------------|-----------|
| **80-100 (niedrig)** | **KZ = 70** | E-Ziele: 20/25/30 (niedriger) | "Sparfuchs" - Kunde erwartet weniger, aber ihr habt wenig Spielraum |
| **101-120 (mittel)** | **KZ = 60** | E-Ziele: 25/30/35 (normal) | "Balanced" - Standard-Erwartungen |
| **121-150 (hoch)** | **KZ = 50** | E-Ziele: 30/35/40 (höher) | "Premium" - Kunde zahlt, erwartet aber Top-Performance |

**Mechanik:**
- Teams diskutieren: "Was können wir realistisch umsetzen?"
- Höheres Budget erlaubt mehr/bessere Maßnahmen, ABER:
  - Niedrigere KZ-Start (Kunde ist kritischer: "Ihr kostet viel!")
  - Höhere E-Ziele (mehr Erwartungsdruck)

**Discovery-Einfluss:**
Je nach Discovery-Signalen gibt der Moderator einen **Budgetvorschlag-Korridor**:
- Hohe OT-Kritikalität → "Kunde bietet eher 120-150"
- Niedriger Audit-Druck → "Kunde denkt eher 80-100"

**KZ-Klammerung:** 0-100 (bei 0: Vertrag verloren; bei 100: Vertragsverlängerung garantiert)

---

## 6. DISCOVERY-FORMAT (strukturiert + explorativ)

### Konzept: "Geführte Exploration"

**Ablauf (20-30 Min):**

1. **Einführung (5 Min):**
   Moderator: "Ihr seid Berater, der Kunde MechTech GmbH hat euch beauftragt. Stellt Fragen, um die Situation zu verstehen."

2. **Fragenkatalog (15-20 Min):**
   Moderator hat **15 vorbereitete Fragen** (mit Musterlösungen), Teams können aber **frei fragen**.

   **Beispiel-Fragen:**
   - "Wie kritisch ist der Produktionsbetrieb? 24/7?"
     → Antwort: "24/5, aber Ausfälle >4h gefährden Liefertermine."

   - "Gibt es besonders sensible Daten?"
     → Antwort: "Ja, CAD-Daten und Prozess-Know-how. Wettbewerbsrelevant."

   - "Wie ist die IT-Sicherheit aktuell aufgestellt?"
     → Antwort: "Standard-Virenscanner, keine zentrale Logs, Backups teilweise."

   - "Gibt es regulatorische Anforderungen?"
     → Antwort: "OEM fordert ISO 27001 bis Q3."

3. **Signal-Scoring (Moderator notiert intern):**
   Jede Antwort → Punkte in 3 Dimensionen:
   - **OT-Kritikalität** (0-10): Wie wichtig ist Verfügbarkeit?
   - **Compliance-Druck** (0-10): Wie stark sind Audit-/Regulierungsanforderungen?
   - **IP-Schutz** (0-10): Wie wertvoll sind Daten?

4. **Zusammenfassung (5 Min):**
   Moderator fasst zusammen: "Ich sehe, dass OT sehr kritisch ist (8/10), Audit-Druck hoch (9/10), IP mittel (6/10). Daraus ergibt sich..."

**Hilfestellungen:**
- Wenn Teams nicht weiterfragen: "Wollt ihr noch etwas über [OT/Lieferanten/Mitarbeitende] wissen?"
- Wenn zu detailliert: "Das ist sehr technisch, fokussiert auf Business-Impact."

**Ergebnis:**
- Signal-Scores bestimmen Wellengewichte (wC/wI/wA)
- Signal-Scores beeinflussen Budget-Empfehlung
- Teams haben Kontext für Maßnahmenauswahl

---

## 7. ZEITPLAN (3-4h Workshop)

| Phase | Dauer | Aktivität |
|-------|-------|-----------|
| **Intro** | 10 Min | Begrüßung, Spielregeln, Ziele |
| **Discovery** | 25 Min | Geführte Exploration (siehe oben) |
| **Budget-Verhandlung** | 10 Min | Teams einigen sich auf Budget |
| **Maßnahmenwahl (Initital)** | 20 Min | Teams wählen Maßnahmen, rechnen Kosten |
| **Welle 1** | 25 Min | Angriff auflösen, Schäden berechnen, KZ aktualisieren |
| **Change-Fenster 1** | 15 Min | Teams können upgraden/swappen |
| **Welle 2** | 25 Min | Angriff + Event auflösen |
| **Change-Fenster 2** | 15 Min | Letzte Anpassungen |
| **Welle 3** | 25 Min | Finaler Angriff + Event |
| **Auswertung** | 20 Min | Tabellen ausfüllen, RoS berechnen |
| **Debrief** | 30 Min | Reflexion, Learnings, Q&A |
| **Gesamt** | **~3h 40 Min** | (+ Puffer für Fragen/Diskussionen) |

---

## 8. OFFENE FRAGEN / FEEDBACK BENÖTIGT

1. **Maßnahmen:** Passen die 8 Maßnahmen? Zu viele/wenige? Änderungswünsche?

2. **Zahlen-Balance:** Sind die Kosten/Mitigations/Schweregrade plausibel?
   (Ich habe bewusst "mittlere" Werte gewählt, müssen aber getestet werden!)

3. **Angriffe:** Sind 3 Angriffe mit der Dramaturgie sinnvoll? Reihenfolge ok?

4. **Budget 80-150:** Passt der Range? Oder lieber 100-200 (psychologisch "größer")?

5. **Discovery:** Ist die "geführte Exploration" das richtige Format für euch?

6. **Events:** Sind 2-3 Events genug, oder wollt ihr mehr Variabilität?

7. **Zeitplan:** Ist 3h40min realistisch, oder müssen wir kürzen?

---

## NÄCHSTE SCHRITTE (nach Feedback)

1. ✅ **Parameter finalisieren** (Zahlen testen/anpassen)
2. ✅ **Moderatorenleitfaden** schreiben (Schritt-für-Schritt)
3. ✅ **Spieleranleitung** erstellen (1-2 Seiten Quickstart)
4. ✅ **Formulare & Whiteboard-Layout** designen
5. ✅ **Discovery-Fragebogen** ausarbeiten (15 Fragen + Antworten)
6. ✅ **Testdurchlauf** vorbereiten

**Bitte gebt Feedback zu den offenen Fragen, dann geht's in die Umsetzung! 🚀**
