# DISCOVERY-FRAGEBOGEN

**Für Moderatoren: Geführte Exploration mit Scoring**

---

## WIE NUTZEN?

**Konzept:** Strukturiert + Explorativ
- Teams haben **Assets** (Email, Zeitung, Steckbrief) gelesen
- Teams stellen **eigene Fragen**
- Moderator nutzt **diesen Fragebogen** als Hilfe:
  - Wenn Team passende Frage stellt → Antwort geben + Score notieren
  - Wenn Team nicht weiterfragt → Moderator kann **Hilfestellung** geben ("Wollt ihr noch was über... wissen?")

**Ziel:** Nach 15-20 Min haben wir **3 Signal-Scores** (OT-Kritikalität, Compliance-Druck, IP-Schutz)

---

## FRAGENKATALOG (15 Kern-Fragen)

### BLOCK A: GESCHÄFTSKONTEXT

#### Frage A1: "Wie ist die Kundensituation? Wie abhängig seid ihr vom OEM?"

**Musterlösung:**
"Der OEM macht 60% unseres Umsatzes. Die Verträge laufen jährlich, aber bei schlechter Performance (Lieferverzug, Qualität) gibt es Malus-Zahlungen oder Vertragsausstieg. Der Markt ist hart umkämpft."

**Scoring:**
- **Compliance-Druck:** +2 (OEM hat Macht)
- **OT-Kritikalität:** +1 (Liefertermintreue wichtig)

**Moderator-Tipp (falls Teams nicht fragen):**
"Denkt an die Geschäftsbeziehung: Wer ist euer Kunde, wie kritisch ist die Zusammenarbeit?"

---

#### Frage A2: "Was passiert, wenn die Produktion ausfällt?"

**Musterlösung:**
"Jede Stunde Stillstand kostet uns ca. 8.000€ (Maschinenlaufzeit, Lohnkosten, Verzugsstrafen). Ab 4h Ausfall drohen Lieferverzug und Vertragsstrafen vom OEM. Bei >24h Ausfall: Verlust des Quartalsauftrags (ca. 2 Mio.€)."

**Scoring:**
- **OT-Kritikalität:** +4 (sehr hoch!)
- **Compliance-Druck:** +1 (Vertragsstrafen)

**Moderator-Tipp:**
"Was wären die Konsequenzen eines Produktionsausfalls?"

---

#### Frage A3: "Wie kritisch sind eure Konstruktionsdaten?"

**Musterlösung:**
"Unsere CAD-Daten und Fertigungsprozesse sind unser Wettbewerbsvorteil. Toleranzen <10µm sind Know-how, das Jahre Entwicklung gekostet hat. Wenn ein Wettbewerber die Daten bekommt, verlieren wir den USP."

**Scoring:**
- **IP-Schutz:** +4 (sehr hoch!)

**Moderator-Tipp:**
"Welche Daten sind besonders wertvoll für euch?"

---

### BLOCK B: IT/OT-INFRASTRUKTUR

#### Frage B1: "Wie ist euer Netzwerk aufgebaut? Sind IT und OT getrennt?"

**Musterlösung:**
"Nein, aktuell sind Office-IT und Produktionsnetz im selben Netz. Es gibt VLANs, aber keine Firewall dazwischen. Das MES-System (Siemens) ist direkt aus dem Office erreichbar."

**Scoring:**
- **OT-Kritikalität:** +3 (Risiko!)
- **IP-Schutz:** +1 (Office → OT Zugriff)

**Moderator-Tipp:**
"Wie sieht eure Netzwerkarchitektur aus?" (→ Evtl. **Asset 5 (Netzwerk-Skizze)** zeigen!)

---

#### Frage B2: "Welche Security-Maßnahmen habt ihr aktuell?"

**Musterlösung:**
"Wir haben einen Standard-Virenscanner (Kaspersky) auf allen Windows-PCs. Backups laufen täglich auf NAS (im gleichen Netz). Firewall am Internet-Übergang. Keine zentrale Log-Sammlung, kein SIEM."

**Scoring:**
- **OT-Kritikalität:** +1 (wenig Schutz)
- **IP-Schutz:** +1 (Backup nicht isoliert)

**Moderator-Tipp:**
"Was habt ihr bisher an Security-Maßnahmen umgesetzt?"

---

#### Frage B3: "Wie läuft das Patch-Management?"

**Musterlösung:**
"Office-IT: Automatische Windows-Updates. OT: Wir patchen ungern, weil Produktions-Downtime nötig ist. Letzte OT-Patches vor 8 Monaten. Es gab schon Probleme nach Updates (MES-Kompatibilität)."

**Scoring:**
- **OT-Kritikalität:** +2 (ungepatchte OT = Risiko!)

**Moderator-Tipp:**
"Wie haltet ihr eure Systeme aktuell?"

---

#### Frage B4: "Habt ihr ein Backup-Konzept? Wurden Restores getestet?"

**Musterlösung:**
"Backups laufen täglich auf ein NAS (gleiche Netzwerk). Aufbewahrung: 14 Tage. Restore-Tests: Noch nie gemacht. Cloud-Backup (Veeam) für Office-Daten (monatlich)."

**Scoring:**
- **OT-Kritikalität:** +1 (kein DR-Plan)
- **IP-Schutz:** +1 (Backup im gleichen Netz = Ransomware-Risiko)

**Moderator-Tipp:**
"Wie sicher sind eure Daten im Notfall?"

---

### BLOCK C: PERSONAL & PROZESSE

#### Frage C1: "Wie groß ist euer IT-Team? Wie ist deren Security-Kompetenz?"

**Musterlösung:**
"Wir haben 2 IT-Admins (einer davon Teilzeit). Beide sind Generalisten, keine spezielle Security-Ausbildung. Bei größeren Projekten holen wir externe Dienstleister."

**Scoring:**
- **OT-Kritikalität:** +1 (wenig Ressourcen)
- **Compliance-Druck:** +1 (ISO 27001 schwierig ohne Know-how)

**Moderator-Tipp:**
"Wer kümmert sich um IT-Sicherheit bei euch?"

---

#### Frage C2: "Gab es schon Security-Vorfälle?"

**Musterlösung:**
"Vor 2 Jahren hatten wir eine Crypto-Trojaner-Infektion (verschlüsselte 3 PCs). Wir haben neu aufgesetzt, Backups hatten wir. Ansonsten: Phishing-Mails täglich, aber keine größeren Vorfälle."

**Scoring:**
- **OT-Kritikalität:** +1 (Erfahrung vorhanden, aber nicht schlimm)
- **IP-Schutz:** +1 (Sensibilisierung da)

**Moderator-Tipp:**
"Hattet ihr schon mal einen Cyberangriff?"

---

#### Frage C3: "Werden Mitarbeitende geschult (Security Awareness)?"

**Musterlösung:**
"Einmal jährlich gibt's eine Pflicht-Schulung (30 Min E-Learning, Thema Datenschutz). Phishing-Simulationen machen wir nicht."

**Scoring:**
- **OT-Kritikalität:** +1 (Phishing = Risiko)
- **Compliance-Druck:** +1 (DSGVO-Schulung vorhanden)

**Moderator-Tipp:**
"Wie sensibel sind eure Mitarbeitenden für Security?"

---

### BLOCK D: COMPLIANCE & REGULIERUNG

#### Frage D1: "Was fordert der OEM konkret? Gibt's einen Zeitplan?"

**Musterlösung:**
"Der OEM schickt in KW 20 (Mitte Mai) ein Audit-Team. Sie prüfen:
- ISO 27001 (mind. in Vorbereitung)
- OT/IT-Segmentierung
- Incident Response Plan
- Backup-Konzept

Wenn wir durchfallen, riskieren wir Auftragsstopp."

**Scoring:**
- **Compliance-Druck:** +4 (sehr hoch! Deadline!)
- **OT-Kritikalität:** +1 (Audit prüft OT)

**Moderator-Tipp (wichtig!):**
"Was genau erwartet der OEM von euch?" (→ Evtl. **Asset 4 (OEM-Brief)** zeigen!)

---

#### Frage D2: "Gibt es andere regulatorische Anforderungen (DSGVO, NIS2, ...)?

**Musterlösung:**
"DSGVO ist relevant (Kundendaten, Mitarbeiterdaten). NIS2 betrifft uns nicht (zu klein). Aber: Branchenverband empfiehlt TISAX (Automotive-Standard), das könnte künftig gefordert werden."

**Scoring:**
- **Compliance-Druck:** +2 (DSGVO, evtl. TISAX)

**Moderator-Tipp:**
"Welche Gesetze/Standards müsst ihr einhalten?"

---

### BLOCK E: LIEFERANTEN & EXTERNE

#### Frage E1: "Wie viele Lieferanten/Dienstleister haben Zugriff auf eure Systeme?"

**Musterlösung:**
"5 kritische Lieferanten:
- MES-Wartung (Remote-Zugang zum OT-Netz)
- CAD-Software-Support (Remote-Desktop)
- Veeam-Cloud-Backup (SaaS)
- CRM (Salesforce, SaaS)
- Externe IT-Dienstleister (Admin-Zugang bei Bedarf)

Wir prüfen die Security unserer Lieferanten nicht systematisch."

**Scoring:**
- **OT-Kritikalität:** +2 (MES-Remote = Risiko!)
- **IP-Schutz:** +2 (CAD-Support hat Zugriff!)
- **Compliance-Druck:** +1 (Lieferanten-Management für ISO 27001 nötig)

**Moderator-Tipp:**
"Wer hat von außen Zugriff auf eure Systeme?"

---

#### Frage E2: "Wie sichert ihr die Remote-Zugänge ab?"

**Musterlösung:**
"VPN mit Passwort. Kein MFA. Die Lieferanten bekommen Admin-Accounts (teilweise mit generischen Passwörtern wie 'Service2024')."

**Scoring:**
- **OT-Kritikalität:** +2 (unsichere Remote-Zugänge = großes Risiko!)
- **IP-Schutz:** +1

**Moderator-Tipp:**
"Wie schützt ihr Fernzugriffe?"

---

## SIGNAL-SCORING (intern auswerten)

### Auswertung nach Discovery-Phase

**Moderator zählt Punkte zusammen:**

| Signal-Kategorie | Punkte | Interpretation | Konsequenz |
|------------------|--------|----------------|------------|
| **OT-Kritikalität** | 0-5 | Niedrig | Welle 2 (OT) standard |
| | 6-10 | Mittel | Welle 2: wA=0.6 (wie geplant) |
| | 11+ | Hoch | Welle 2: wA=0.7, sUnit +2 (härter!) |
| **Compliance-Druck** | 0-5 | Niedrig | Event 1 (Audit) standard |
| | 6-10 | Mittel | Event 1: Malus -3 (wie geplant) |
| | 11+ | Hoch | Event 1: Malus -5 (härter!), Bonus +6 |
| **IP-Schutz** | 0-5 | Niedrig | Welle 3 (Exfil) standard |
| | 6-10 | Mittel | Welle 3: wC=0.5 (wie geplant) |
| | 11+ | Hoch | Welle 3: wC=0.6, kzUnit +1 (härter!) |

---

### Budget-Empfehlung ableiten

**Nach Scoring:**

| Gesamt-Risiko (OT + Compliance + IP) | Budget-Empfehlung | Begründung |
|--------------------------------------|-------------------|------------|
| 0-15 Punkte | 200-280k€ | "Risiken überschaubar" |
| 16-25 Punkte | 281-380k€ | "Standard-Risiko" |
| 26+ Punkte | 381-500k€ | "Hochrisiko-Szenario, Kunde zahlt mehr" |

**Moderator kommuniziert:**
"Basierend auf euren Erkenntnissen schätze ich, dass der Kunde bereit wäre, 320-400k€ zu investieren. Ihr könnt aber verhandeln!"

---

## HILFESTELLUNGEN (wenn Teams nicht weiterfragen)

**Nach 10 Min, wenn Teams stocken:**

**Moderator:**
"Ihr habt schon viel erfahren. Hier ein paar Denkanstöße:
- **Geschäft:** Wie kritisch ist die Lieferket tenleistung für den OEM?
- **Technik:** Wie ist das Netzwerk aufgebaut? Wo könnten Schwachstellen sein?
- **Menschen:** Wie fit sind Mitarbeitende in Sachen Security?
- **Externe:** Wer hat von außen Zugriff?
- **Regulierung:** Was fordert der Kunde/Gesetzgeber?"

---

## TIMING (Discovery-Phase gesamt: 25 Min)

| Minute | Aktivität |
|--------|-----------|
| 0-5 | Teams lesen Assets (Email, Zeitung, Steckbrief) |
| 5-20 | Teams stellen Fragen, Moderator antwortet + scored |
| 20-22 | Moderator fasst zusammen: "Ich sehe folgende Risiken..." |
| 22-25 | Budget-Empfehlung + Übergang zur Budget-Verhandlung |

---

## MODERATOR-CHEAT-SHEET

**Wichtigste Take-Aways für Teams:**
1. ✅ **OT ist kritisch:** 24/5-Betrieb, hohe Ausfallkosten
2. ✅ **OEM fordert Zertifizierung:** Deadline Mai, Audit kommt
3. ✅ **Kein OT/IT-Trennung:** Großes Risiko!
4. ✅ **Konstruktionsdaten wertvoll:** IP-Schutz wichtig
5. ✅ **Lieferanten haben Zugriff:** Supply-Chain-Risiko
6. ✅ **Wenig Security-Reifegrad:** Vieles fehlt (SIEM, EDR, Segmentierung)

**Wenn Teams diese Punkte verstanden haben → Discovery erfolgreich! ✅**

---

## BEISPIEL-DIALOG (wie es laufen könnte)

**Team:** "Wie ist euer Netzwerk aufgebaut?"
**Moderator:** "Office und Produktion sind im gleichen Netz, nur VLANs, keine Firewall." (→ Score OT +3)

**Team:** "Was passiert bei Produktionsausfall?"
**Moderator:** "8.000€/Stunde Kosten, ab 4h drohen Vertragsstrafen." (→ Score OT +4)

**Team:** "Gibt's MFA?"
**Moderator:** "Nein, nur Passwörter. Auch für Lieferanten-Zugriffe." (→ Score OT +2)

**Team:** "Wann ist das OEM-Audit?"
**Moderator:** *(zeigt Asset 4 - OEM-Brief)* "Hier, KW 20. Sie prüfen ISO 27001, Segmentierung, Backups." (→ Score Compliance +4)

**Moderator (nach 15 Min):**
"Ihr habt gut gefragt! Ich sehe: OT sehr kritisch (18 Punkte), Compliance-Druck hoch (12 Punkte), IP-Schutz mittel (8 Punkte). Der Kunde wäre bereit, 350-400k€ zu investieren. Was denkt ihr?"

**→ Übergang zur Budget-Verhandlung!**

---

**Dieser Fragebogen ist euer Leitfaden für eine strukturierte, aber flexible Discovery! 🎯**
