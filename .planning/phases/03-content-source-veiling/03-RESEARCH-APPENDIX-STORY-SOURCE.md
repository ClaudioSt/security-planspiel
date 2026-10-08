# Phase 3 Research Appendix: Verbatim Source Prose

**Purpose:** executor input for the 1:1 migration into `content/texte.toml` (PRINT-02) and for the veiled rewrites (VEIL-03). Extracted on 2026-10-08 from `final_documents/` with `uv run --with python-docx` / python-pptx (ephemeral, no dependency added). Nothing below is edited: typos, formal/informal mixes and hyphenation artefacts are reproduced as found and listed under "Editorial deltas to confirm" at the end.

Line format: `P <style; colour; font; size> text` for a paragraph, `TABLE:` rows as `| cell | cell |`. Style names are Word styles ("List Paragraph" = bullet). Digits in story texts are world facts (exempt, D-15). Extraction caveat: python-docx does not see text inside text boxes; the only text boxes in these files are empty (`Return on Security und Final Wert.docx`: 4 empty boxes).

## A. Unternehmenssteckbrief MechTech.docx (story, pre-wave)

```text
=== final_documents/Unternehmenssteckbrief MechTech.docx
page: 21.0x29.7cm margins L2.5 R2.5 T4.0 B1.8
Normal font: None None
P <Normal; sz=[12.0]> MECHTECH GmbH: Unternehmenssteckbrief
P <Normal; sz=[10.0]> Kurzprofil
P <Normal; sz=[10.0]> Die MECHTECH GmbH ist ein mittelständischer Präzisionsfertiger mit Schwerpunkt auf Komponenten für E-Antriebe. Am Standort Göppingen (Baden-Württemberg) werden hochgenaue CNC-Komponenten gefertigt und Entwicklungsleistungen für Prototypen sowie Kleinserien erbracht. Der Betrieb ist auf hohe Wiederholgenauigkeit, stabile Prozessketten und termintreue Auslieferung ausgelegt.
P <Normal; sz=[10.0]> Produkte & Leistungen
P <List Paragraph; sz=[10.0]> Präzisions-Getriebeteile für E-Antriebe
P <List Paragraph; sz=[10.0]> CNC-gefräste Komponenten (Toleranzen < 10 µm)
P <List Paragraph; sz=[10.0]> Prototyping und Kleinserien für OEMs
P <List Paragraph; sz=[10.0]> Zerspanungstechnik: 5-Achs-Fräsen und Drehen
P <Normal; sz=[10.0]> Standort & Organisation
P <List Paragraph; sz=[10.0]> Hauptsitz/Produktion: Göppingen, 1 Halle (3.500 m²)
P <List Paragraph; sz=[10.0]> Mitarbeitende: ca. 80
P <List Paragraph; sz=[10.0]> Produktion: 50 (Facharbeiter, Meister, Qualität)
P <List Paragraph; sz=[10.0]> Verwaltung: 20 (Vertrieb, Einkauf, Buchhaltung)
P <List Paragraph; sz=[10.0]> Konstruktion/Entwicklung: 8 (CAD, Prozessplanung)
P <List Paragraph; sz=[10.0]> IT: 2 Admins (1 Vollzeit, 1 Teilzeit)
P <Normal; sz=[10.0]> Wirtschaftliche Eckdaten
P <List Paragraph; sz=[10.0]> Umsatz: ca. 15 Mio. EUR p. a.
P <List Paragraph; sz=[10.0]> Kundenstruktur: 1 deutscher Premium-OEM als Hauptkunde (ca. 60 % Umsatz)
P <List Paragraph; sz=[10.0]> Weitere Kunden: ca. 25 (Tier-1-Zulieferer, Maschinenbau)
P <List Paragraph; sz=[10.0]> Wachstum: ca. +12 % p. a. (getrieben durch E-Mobility-Nachfrage)
P <Normal; sz=[10.0]> Produktion & Betrieb
P <List Paragraph; sz=[10.0]> Betriebsmodell: 24/5 (Mo. bis Fr., 3 Schichten)
P <List Paragraph; sz=[10.0]> Anlagenpark: 12 CNC-Maschinen, 3 Fertigungslinien
P <List Paragraph; sz=[10.0]> Produktionssteuerung: MES Siemens Opcenter; SCADA/HMI zur Visualisierung
P <List Paragraph; sz=[10.0]> CNC-Steuerungen u. a.: Siemens Sinumerik, Heidenhain
P <List Paragraph; sz=[10.0]> Liefermodell: Just-in-Time an OEM, Liefertermintreue > 98 %
P <List Paragraph; sz=[10.0]> Operative Prämisse: Unterbrechungen > 4 Stunden wirken sich unmittelbar auf Auslieferungen aus und sind in Vertragskontexten relevant
P <Normal; sz=[10.0]> IT-/OT-Landschaft
P <Normal; sz=[10.0]> Office / Engineering
P <List Paragraph; sz=[10.0]> Windows Server 2019 (Active Directory)
P <List Paragraph; sz=[10.0]> ca. 30 Windows-PCs (Office, SharePoint, E-Mail)
P <List Paragraph; sz=[10.0]> CAD: Siemens NX (8 Arbeitsplätze)
P <List Paragraph; sz=[10.0]> File-Server (Konstruktionsdaten, Dokumente)
P <Normal; sz=[10.0]> OT / Produktion
P <List Paragraph; sz=[10.0]> MES (Siemens, Windows-Server)
P <List Paragraph; sz=[10.0]> SCADA/HMI-Systeme
P <List Paragraph; sz=[10.0]> 12 CNC-Steuerungen (Sinumerik/Heidenhain)
P <List Paragraph; sz=[10.0]> Office-IT und OT/Produktion nutzen dasselbe LAN (kein separates OT-Netz)
P <Normal; sz=[10.0]> SaaS / Cloud / Externe Anwendungen
P <List Paragraph; sz=[10.0]> CRM: Salesforce
P <List Paragraph; sz=[10.0]> Cloud-Backup: Veeam für Office-Daten (monatliche Sicherung)
P <List Paragraph; sz=[10.0]> Lieferanten-Portal: extern erreichbare Web-Applikation
P <List Paragraph; sz=[10.0]> Cloud-Nutzung ist auf Vertriebsprozesse (Salesforce) und die monatliche Backup-Sicherung beschränkt, keine weiteren Fachanwendungen in der Cloud im Einsatz
P <List Paragraph; sz=[10.0]> Mobilgeräte: Außendienst und Vertrieb nutzen firmeneigene Notebooks, kein separates Mobile-Device-Programm im Einsatz
P <Normal; sz=[10.0]> Betriebs- & Service-Setup
P <List Paragraph; sz=[10.0]> IT-Betrieb durch 2 Administratoren (Generalistenprofil)
P <List Paragraph; sz=[10.0]> Administratorzugänge: gemeinsam genutzte Admin-Konten für Server- und Netzwerkkomponenten, keine gesonderte Verwaltung privilegierter Zugriffe
P <List Paragraph; sz=[10.0]> Externe IT-Dienstleister bei Bedarf, Remote-Zugriff für Support
P <List Paragraph; sz=[10.0]> Remote-Zugänge durch fünf Lieferanten (u. a. MES, CAD, IT)
P <List Paragraph; sz=[10.0]> Policies/Standards: derzeit nicht als dokumentierter Satz beschrieben
P <List Paragraph; sz=[10.0]> Sicherheitsbetrieb: SIEM/EDR nicht als feste Plattformkomponenten genannt
P <List Paragraph; sz=[10.0]> Patch-/Update-Praxis in der Produktion: Umsetzung im Rahmen verfügbarer Wartungsfenster
P <Normal; sz=[10.0]> Abhängigkeiten
P <List Paragraph; sz=[10.0]> Hohe Kopplung zwischen Liefermodell (JIT/Termintreue) und Verfügbarkeit von MES/SCADA sowie Engineering- und File-Services
P <List Paragraph; sz=[10.0]> Relevanz von Konstruktions- und Prozessdaten für Fertigungsfähigkeit und Kundenkommunikation
P <List Paragraph; sz=[10.0]> Mehrere Remote-Zugänge in Kombination mit schlankem IT-Team und stark integrierter Netzwerkinfrastruktur
P <List Paragraph; sz=[10.0]> Auslastungs- und Stillstandsfenster als Taktgeber für Änderungen/Updates in der produktionsnahen Umgebung
images: []
```

## B. Zeitungsartikel.docx (story, pre-wave; two columns from the second section on)

```text
=== final_documents/Zeitungsartikel.docx
page: 21.6x27.9cm margins L1.8 R1.8 T1.5 B1.5
[footer] Aktuelles	Seite 1
[footer] Aktuelles	Seite 1
Normal font: Georgia 127000
P <Normal; sz=[9.0]> Ausgabe 1, 2026	Aktuelles in der Automobilindustrie	Nürnberg
P <Normal; font=['Georgia']; sz=[48.0]> AUTO TIMES
P <Normal> Phishing stoppt Fertigung      •      Backup? Fehlanzeige!      •      MES im Lockdown
P <Normal; sz=[13.0]> OEM VERSCHÄRFT SECURITY-ANFORDERUNGEN
P <Normal; sz=[9.5]> Stuttgart. Ein führender deutscher Automobilhersteller kündigte an, alle Tier-1- und Tier-2-Zulieferer ab Q2/2026 einem IT-Security-Audit zu unterziehen.
P <Normal; sz=[9.5]> Erwartet werden belastbare Nachweise, dass Zulieferer nicht nur reagieren, sondern strukturiert vorsorgen: von der Fähigkeit, nach einem Vorfall schnell wieder anlaufen zu können, bis zur sauberen Trennung von Büro- und Fertigungsnetzen.
P <Normal; sz=[9.5]> „Supply Chain Security ist geschäftskritisch", so ein Sprecher. Bei gravierenden Lücken behalte man sich vor, Aufträge zurückzustellen.
P <Normal ; IMAGE> 
P <Normal; font=['Georgia']; sz=[8.0]> Symbolbild: Verschärfte Audits für Zulieferer.
P <Normal; sz=[15.0]> Ransomware legt Zulieferer tagelang lahm
P <Normal; sz=[9.0]> Kassel, 10.01.2026
P <Normal; sz=[9.5]> Ein mittelständischer Automotive Zulieferer aus Nordhessen wurde Opfer eines schweren Ransomware-Angriffs. Die Produktion stand für 72 Stunden still, der Schaden wird auf über 500.000 Euro geschätzt.
P <Normal ; IMAGE> 
P <Normal; font=['Georgia']; sz=[8.0]> Symbolbild: Stillstand in der Fertigung nach Cyberangriff.
P <Normal; sz=[9.0]> DER ANGRIFF
P <Normal; sz=[9.5]> Laut Informationen des Unternehmens erfolgte der Einbruch über eine Phishing-Mail, die ein Mitarbeiter in der Buchhaltung öffnete. Der klassische Virenschutz des Unternehmens schlug nicht rechtzeitig Alarm. Die Erpresser-Software verschlüsselte innerhalb von 2 Stunden nicht nur Office-Daten, sondern auch das produktionssteuernde MES-System. Erst nach Stunden bemerkte die IT ungewöhnliche Aktivitäten im Netz. Zentrale Systeme waren zudem seit Monaten nicht mehr aktualisiert worden.
P <Normal; sz=[9.5]> „Wir hatten kein funktionierendes Backup-Konzept", so der Geschäftsführer unter der Bedingung der Anonymität. Die Angreifer forderten ein Lösegeld von 250.000 Euro in Bitcoin.
P <Normal; sz=[9.0]> FOLGEN
P <Normal; sz=[9.5]> Das Unternehmen entschied sich gegen die Zahlung und setzte die Systeme mit Unterstützung externer Forensiker neu auf. Drei Fertigungslinien standen still, Liefertermine konnten nicht eingehalten werden. Ein OEM-Kunde verhängte Vertragsstrafen wegen Lieferverzugs.
P <Normal; sz=[9.5]> „Auch kleine Zulieferer sind Ziele", warnt Dr. Sabine Müller vom BSI. „Angreifer wissen: Produktionsausfälle erzeugen Zahlungsbereitschaft."
images: ['media/image1.png', 'media/image2.png']
```

## C. Anfrage-Mail.docx (story, pre-wave)

```text
=== final_documents/Anfrage-Mail.docx
page: 21.6x27.9cm margins L2.5 R2.5 T2.0 B2.0
Normal font: Calibri 139700
P <Normal> Betreff: Anfrage: IT-Security-Beratung für MechTech GmbH
P <Normal> Von: "Dr. Thomas Weber" <t.weber@mechtech-gmbh.de>
P <Normal> An: "VWI Security Consulting <security-consulting@vwi.de>"
P <Normal> Sehr geehrte Damen und Herren,
P <Normal> ich wende mich an Sie im Namen der MechTech GmbH. Wir sind ein mittelständischer Zulieferer für die Automotive-Industrie und produzieren Präzisionsteile für E-Antriebe.
P <Normal> Täglich lesen wir von Ransomware-Angriffen auf Unternehmen unserer Größe und Branche.
P <Normal> Ehrlich gesagt sind wir mit dem Thema IT-Sicherheit bisher eher reaktiv umgegangen. Wir haben einen Virenscanner und Backups, aber keine strukturierte Security-Strategie. Ehrlich gesagt wissen wir auch nicht genau, wer aktuell überall administrativen Zugriff auf unsere Systeme hat.
P <Normal> Wir möchten das ändern, wissen aber nicht, wo wir anfangen sollen.
P <Normal> IHRE AUFGABE:
P <Normal> Können Sie uns dabei unterstützen, ein sinnvolles Security-Konzept zu entwickeln? Wir hätten Budget für ein Beratungs-projekt und möchten verstehen:
P <List Bullet> Wo sind unsere größten Risiken?
P <List Bullet> Welche Maßnahmen sind sinnvoll und umsetzbar?
P <Normal> Könnten Sie sich zunächst ein Bild von unserer Situation machen? Ich stehe für ein Erstgespräch gerne zur Verfügung.
P <Normal> Mit freundlichen Grüßen,
P <Normal> Dr. Thomas Weber
P <Normal> Geschäftsführer
P <Normal> MechTech GmbH
P <Normal> _________________________________________________________________
P <Normal> www.mechtech-gmbh.de | Industriestr. 42, 73033 Göppingen
images: []
```

## D. Audit-Mail.pdf (story, pre-wave; image-only PDF, transcribed visually 2026-10-08)

Source file `final_documents/Audit-Mail.pdf` has no text layer (single page, rendered image). Transcription (layout markers added: `B:` bold run, `-` bullet, blank line = paragraph break):

```text
B:Betreff: Information Security Assessment - Supplier Audit Q2/2026
B:Von: "Klaus Hoffmann" <k.hoffmann@premium-oem.com>
B:An: "Dr. Thomas Weber <t.weber@mechtech-gmbh.de>"

Sehr geehrter Herr Dr. Weber,

im Rahmen unserer Supplier Security Initiative werden wir alle strategischen Zulieferer in Q2/2026 einem umfassenden IT-Security-Audit unterziehen.

Angesichts steigender Cyberbedrohungen (insb. Ransomware, Supply-Chain-Angriffe) stellen wir sicher, dass unsere Lieferkette angemessen abgesichert ist.

ERWARTETE NACHWEISE:

Im Audit werden wir vor allem folgende Punkte prüfen:

- IAM/ PAM
- Backup & Disaster Recovery
- Patch Management
- Logging & SIEM
- OT-Segmentierung

KONSEQUENZEN:

Bei kritischen Lücken behalten wir uns vor:

- Aufträge zurückzustellen (bis Maßnahmen umgesetzt)
- Vertragsstrafen bei Sicherheitsvorfällen
- Im Wiederholungsfall: Beendigung der Geschäftsbeziehung

UNTERSTÜTZUNG:

Wir empfehlen Ihnen dringend, externe Beratung hinzuzuziehen und umgehend mit den Vorbereitungen zu beginnen.

Bei Fragen stehe ich gerne zur Verfügung.

Mit freundlichen Grüßen,

Klaus Hoffmann

Supplier Quality Management

Premium Automotive AG
_________________________________________________________________   (short rule)
Tel: +49-711-12345| k.hoffmann@premium-oem.com
=================================================================   (double rule across the page)
```

Visual: plain sans-serif (Calibri-like) e-mail printout, black on white, no logo, single column.

## E. Angriff-1_Ransomware.docx (revealed worksheet)

```text
=== final_documents/Angriff-1_Ransomware.docx
page: 21.0x29.7cm margins L3.0 R1.5 T2.0 B2.0
Normal font: None None
P <Normal; sz=[12.0]> Angriff 1: Ransomware
P <Normal; sz=[10.0]> Ein Mitarbeiter hat auf eine gefälschte E-Mail geklickt. Die Angreifer versuchen, Ransomware zu platzieren, die Daten verschlüsselt und ggf. exfiltriert, um anschließend Lösegeld zu erpressen. Ob die Verschlüsselung tatsächlich gelingt und wie stark die Auswirkungen sind, wird im Folgenden anhand Ihrer Sicherheitsmaßnahmen berechnet.
P <Normal; sz=[10.0]> Euer Unternehmen startet je Schutzziel mit einem Basiswert von 10. Eure gewählten Maßnahmen erhöhen diese Werte. Tragt die CIA-Werte eurer Maßnahmen ein und berechnet euren Gesamtschutz über alle Schutzziele.
TABLE:
  | Maßnahme | Level | C | I | A
  | Basisschutz | - | 10 | 10 | 10
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | Summe | - |  |  | 
P <Normal; sz=[10.0]> Als Nächstes berechnet ihr den Effektivitätswert (E-Wert). Er zeigt, wie gut ihr gegen diesen Angriffstyp geschützt seid: Bei Ransomware zählen Vertraulichkeit (C) und Integrität (I) stärker (Datendiebstahl + Verschlüsselung), Verfügbarkeit (A) ist häufig die Folge daraus.
P <Normal; sz=[10.0]> Zusätzlich bekommt ihr einen Bonus, wenn ihr passende Maßnahmen für diesen Angriff mindestens auf dem richtigen Level habt. Der Bonus wird zur Gesamtreduktion addiert.
TABLE:
  | Maßnahme | Ab Level | Bonus  | Erfüllt
  | M3 - EDR/XDR  | 2 | +6 | (✓ / ✗)
  | M4 - Backup  | 2 | +6 | (✓ / ✗)	
  | M6 - Awareness  | 2 | +3 | (✓ / ✗)
P <Normal; sz=[10.0]> Gesamtbonus: ______________
P <Normal; sz=[10.0]> Gesamtreduktion  = E-Wert ___________ + Gesamtbonus ___________ = _____________
P <Normal; sz=[10.0]> Fall 1: Gesamtreduktion ≤ 23 → Eure Maßnahmen reichen nicht aus, der Angriff setzt sich durch. Schaden: 160.000 €. KZ: −6.
P <Normal; sz=[10.0]> Fall 2: Gesamtreduktion ≥ 31 → Ihr wehrt den Angriff vollständig ab. Schaden: 0 €. KZ: +10.
P <Normal; sz=[10.0]> Fall 3: Gesamtreduktion > 23 und < 31 → Ihr mindert die Auswirkungen teilweise. Berechnet Schaden und KZ:
P <Normal; sz=[10.0]> Schaden = (31 - Gesamtreduktion ____________) * 20.000 € = ____________ 
P <Normal; sz=[10.0]> Kundenzufriedenheit (KZ) = (Gesamtreduktion ____________ - 23) * 2 - 6 = ____________ 
P <Normal; sz=[10.0]> Schaden = ____________                   Kundenzufriedenheit = ____________ 
images: []
```

## F. Angriff-2_OT-Störung.docx (revealed worksheet)

```text
=== final_documents/Angriff-2_OT-Störung.docx
page: 21.0x29.7cm margins L3.0 R1.5 T2.0 B2.0
Normal font: None None
P <Normal; sz=[12.0]> Angriff 2: OT-Störung (Produktionsausfall)
P <Normal; sz=[10.0]> In eurer Produktionssteuerung wurde eine Schwachstelle ausgenutzt. Die Angreifer zielen darauf, die Fertigung zu stören bzw. stillzulegen. Ob die Produktion wirklich ausfällt und wie stark die Auswirkungen sind, ermittelt ihr im nächsten Schritt anhand eurer Sicherheitsmaßnahmen.
P <Normal; sz=[10.0]> Euer Unternehmen startet je Schutzziel mit einem Basiswert von 10. Eure gewählten Maßnahmen erhöhen diese Werte. Tragt die CIA-Werte eurer Maßnahmen ein und berechnet euren Gesamtschutz über alle Schutzziele.
TABLE:
  | Maßnahme | Level | C | I | A
  | Basisschutz | - | 10 | 10 | 10
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | Summe | - |  |  | 
P <Normal; sz=[10.0]> Als Nächstes berechnet ihr den Effektivitätswert (E-Wert). Er zeigt, wie gut ihr gegen diesen Angriffstyp geschützt seid: Bei OT-Störungen ist Verfügbarkeit (A) entscheidend, weil ein Stillstand direkt zu Produktionsausfall und Lieferverzug führt; C und I sind hier nachgelagert.
P <Normal; sz=[10.0]> Zusätzlich bekommt ihr einen Bonus, wenn ihr passende Maßnahmen für diesen Angriff mindestens auf dem richtigen Level habt. Der Bonus wird zur Gesamtreduktion addiert.
TABLE:
  | Maßnahme | Ab Level | Bonus  | Erfüllt
  | M5 - Netz-Segmentierung | 2 | +9 | (✓ / ✗)
  | M7 - Patch Management | 2 | +6 | (✓ / ✗)	
P <Normal; sz=[10.0]> Gesamtbonus: ______________
P <Normal; sz=[10.0]> Gesamtreduktion  = E-Wert ___________ + Gesamtbonus ___________ = _____________
P <Normal; sz=[10.0]> Fall 1: Gesamtreduktion ≤ 20 → Eure Maßnahmen reichen nicht aus, die Produktion fällt aus. Schaden: 320.000 €. KZ: −5.
P <Normal; sz=[10.0]> Fall 2: Gesamtreduktion ≥ 30 → Ihr verhindert den Ausfall vollständig. Schaden: 0 €. KZ: +7.
P <Normal; sz=[10.0]> Fall 3: Gesamtreduktion > 20 und < 30 → Ihr mindert die Auswirkungen teilweise. Berechnet Schaden und KZ:
P <Normal; sz=[10.0]> Schaden = (30 - Gesamtreduktion ____________) * 32.000 € = ____________ 
P <Normal; sz=[10.0]> Kundenzufriedenheit (KZ) = -5 + (Gesamtreduktion ____________ - 20) * 1,2 = ____________ 
P <Normal; sz=[10.0]> Schaden = ____________                   Kundenzufriedenheit = ____________ 
images: []
```

## G. Angriff-3_Datenexfiltration.docx (revealed worksheet)

```text
=== final_documents/Angriff-3_Datenexfiltration.docx
page: 21.0x29.7cm margins L3.0 R1.5 T2.0 B2.0
Normal font: None None
P <Normal; sz=[12.0]> Angriff 3: Datenexfiltration
P <Normal; sz=[10.0]> Über einen kompromittierten Lieferanten-Zugang wurden über Wochen hinweg vertrauliche Konstruktionsdaten abgegriffen. Das Bundesamt für Sicherheit in der Informationstechnik (BSI) informiert euch: Eure Daten werden im Darknet angeboten. Ob (und wie stark) der Abfluss gelingt und welche Folgen daraus entstehen, ermittelt ihr jetzt anhand eurer Sicherheitsmaßnahmen.
P <Normal; sz=[10.0]> Euer Unternehmen startet je Schutzziel mit einem Basiswert von 10. Eure gewählten Maßnahmen erhöhen diese Werte. Tragt die CIA-Werte eurer Maßnahmen ein und berechnet euren Gesamtschutz über alle Schutzziele.
TABLE:
  | Maßnahme | Level | C | I | A
  | Basisschutz | - | 10 | 10 | 10
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | M__ | (1 / 2 / 3) |  |  | 
  | Summe | - |  |  | 
P <Normal; sz=[10.0]> Als Nächstes berechnet ihr den Effektivitätswert (E-Wert). Er zeigt, wie gut ihr gegen diesen Angriffstyp geschützt seid: Bei Exfiltration zählt Vertraulichkeit (C) am meisten (IP-Diebstahl), Integrität (I) ist relevant (Daten werden kopiert/weiterverarbeitet), Verfügbarkeit (A) bleibt oft weitgehend erhalten.
P <Normal; sz=[10.0]> Zusätzlich bekommt ihr einen Bonus, wenn ihr passende Maßnahmen für diesen Angriff auf dem richtigen Level habt. Der Bonus wird zur Gesamtreduktion addiert.
TABLE:
  | Maßnahme | Ab Level | Bonus  | Erfüllt
  | M1 - IAM/PAM | 2 | +8 | (✓ / ✗)
  | M2 - Logging & SIEM | 2 | +6 | (✓ / ✗)	
  | M8 - Supplier Security | 2 | +9 | (✓ / ✗)	
P <Normal; sz=[10.0]> Gesamtbonus: ______________
P <Normal; sz=[10.0]> Gesamtreduktion  = E-Wert ___________ + Gesamtbonus ___________ = _____________
P <Normal; sz=[10.0]> Fall 1: Gesamtreduktion ≤ 25 → Eure Maßnahmen reichen nicht aus, der Datenabfluss gelingt. Schaden: 140.000 €. KZ: −7.
P <Normal; sz=[10.0]> Fall 2: Gesamtreduktion ≥ 32 → Ihr verhindert die Exfiltration vollständig. Schaden: 0 €. KZ: +10.
P <Normal; sz=[10.0]> Fall 3: Gesamtreduktion > 25 und < 32 → Ihr reduziert die Auswirkungen teilweise. Berechnet Schaden und KZ:
P <Normal; sz=[10.0]> Schaden = (32 - Gesamtreduktion ____________) * 20.000 € = ____________ 
P <Normal; sz=[10.0]> Kundenzufriedenheit (KZ) = -7 + (Gesamtreduktion ____________ - 25) / 7 * 17 = ____________ 
P <Normal; sz=[10.0]> Schaden = ____________                   Kundenzufriedenheit = ____________ 
images: []
```

## H. Budget.docx (pre-wave planning sheet)

```text
=== final_documents/Budget.docx
page: 21.0x29.7cm margins L3.0 R1.5 T2.0 B2.0
Normal font: None None
P <Normal; sz=[12.0]> Budget
P <Normal; sz=[10.0]> Das Budget ist das Geld, das euch Beratern für die Umsetzung von Maßnahmen zur Verfügung steht. Mit dem Budget müsst ihr Maßnahmen initiieren und betreiben.
TABLE:
  | Kostenart | Was ist das? | Wann fällig?
  | Init-Kosten | Einmalige Anschaffungskosten für eine Maßnahme (Hardware, Software, Einrichtung) | Einmal zu Spielbeginn
  | OPEX | Laufende Betriebskosten (Lizenzen, Personal, Wartung) | Jede Welle erneut
P <Normal; sz=[10.0]> Im Planspiel wählt ihr zu Beginn ein Budget-Tier. Je höher euer Budget, desto mehr bzw. stärkere Maßnahmen könnt ihr umsetzen. Gleichzeitig sind die Erwartungen höher, was sich in einem entsprechend angepassten Startwert der Kundenzufriedenheit (KZ) widerspiegelt. Legt daher zuerst euer Budget-Tier fest, bevor ihr eure Maßnahmen auswählt.
TABLE:
  | Tier | Verfügbares Budget | Kundenzufriedenheit
  | Low | 350.000 Euro | 50
  | Medium | 400.000 Euro | 42
  | High | 450.000 Euro | 34
P <Normal; sz=[10.0]> Antizipierte Summe
P <Normal; sz=[10.0]> In diesem Sheet plant und trackt ihr euer Budget über alle Wellen. INIT-Kosten fallen nur einmalig an, wenn ihr eine Maßnahme einführt oder auf ein höheres Level upgraded. OPEX-Kosten fallen dagegen in jeder Welle an, in der die Maßnahme aktiv ist.
TABLE:
  | Zeitraum | Maßnahmen | Level | Init-Kosten | OPEX
  | Angriff 1 | M__ / M__ / M__ / M__ / M__ / M__ / M__ / M__ | (1 / 2 / 3) / (1 / 2 / 3) / (1 / 2 / 3) / (1 / 2 / 3) / (1 / 2 / 3) / (1 / 2 / 3) / (1 / 2 / 3) / (1 / 2 / 3) |  | 
  | Events 1 | Event__ / Event__ |  |  | 
  | Angriff 2 | M__ / M__ / M__ | (1 / 2 / 3) / (1 / 2 / 3) / (1 / 2 / 3) |  | 
  | Events 2 | Event__ / Event__ |  |  | 
  | Angriff 3 | M__ / M__ / M__ | (1 / 2 / 3) / (1 / 2 / 3) / (1 / 2 / 3) |  | 
  | Events 3 | Event__ / Event__ |  |  | 
  |  |  |  |  | 
  | Summe | - | - |  | 
P <Normal; sz=[10.0]> Antizipierte Summe: ___________
P <Normal; sz=[10.0]> Status-Tracker
P <Normal; sz=[10.0]> Trackt hier nach jeder Welle euren aktuellen Stand: verbleibendes Budget, die aktuellen CIA-Werte (Summe aus Basisschutz + Maßnahmen, siehe jeweilige Angriffskarte) und die kumulierte Kundenzufriedenheit. So habt ihr den Überblick, ohne in den Angriffskarten zurückblättern zu müssen.
TABLE:
  | Zeitpunkt | Budget verbleibend | C | I | A | KZ (kumuliert) | Schaden (Welle)
  | Start |  | 10 | 10 | 10 |  | -
  | Nach Welle 1 |  |  |  |  |  | 
  | Nach Welle 2 |  |  |  |  |  | 
  | Nach Welle 3 |  |  |  |  |  | 
images: []
```

## I. Return on Security und Final Wert.docx

```text
=== final_documents/Return on Security und Final Wert.docx
page: 21.0x29.7cm margins L3.0 R1.5 T2.0 B2.0
Normal font: None None
P <Normal; col=['000000']; font=['Arial']; sz=[11.0, 12.0]> Return on Security
P <Normal; col=['000000']> Trag die folgenden Werte ein:
TABLE:
  | Kennzahl | Wert
  | Gesamt Init-Kosten	 | €
  | Gesamt OPEX Kosten | €
  | Schaden Angriff 1 | €
  | Schaden Angriff 2 | €
  | Schaden Angriff 3 | €
  | Summe Event-Strafen | €
P <Normal; col=['000000']> Der RoS zeigt, ob sich eure Security-Investition finanziell gelohnt hat.
P <Normal; col=['000000']> Gesamtkosten = Gesamt Init-Kosten + Gesamt OPEX Kosten + Summe Event-Strafen
P <Normal; col=['000000']>                         = _____________ + _____________  + _____________ = _____________ 
P <Normal; col=['000000']> Vermiedener Schaden = 620.000 - Schaden Welle 1 - Schaden Welle 2 - Schaden Welle 3
P <Normal; col=['000000']>                         =620.000 -  ___________ - ___________  - ___________ = ___________ 
P <Normal; col=['000000'] ; IMAGE> 
images: []
```

## J. Events_Security-Game.pptx (event narratives as printed, 9 slides)

Per slide: title, subtitle line, then every other text shape in shape order (the narrative is the accent-coloured `Text Placeholder 7`; the remainder are rule/effect lines that become code-generated effect lines or `rule` keys).

```text
--- slide 1
[Title 2] Backup & Recovery
[Content Placeholder 26] Event: Nach jeder Welle mit Recovery-Option
[Text Placeholder 7] Nach einem Angriff mit entstandenem Schaden prüft ihr, ob Systeme wiederhergestellt werden müssen oder ob der Betrieb stabil geblieben ist. Falls überhaupt ein Schaden entstanden ist, entscheidet eure Backup- und Recovery-Fähigkeit darüber, wie stark ihr den finanziellen Impact senken könnt. Prüft die Umsetzung von M4.
[Text Placeholder 8] Keine Umsetzung: kein Recovery → Endschaden = 100%  //  Level 1: Basis-Recovery → Endschaden = Schaden × 0,90  //  Level 2: teilw. Recovery → Endschaden = Schaden × 0,70  //  Level 3: starke Recovery → Endschaden = Schaden × 0,50
[Rechteck: abgerundete Ecken 1] Welle 1
--- slide 2
[Title 2] Kurswechsel
[Content Placeholder 26] Event: Nach Welle 1
[Text Placeholder 7] Nach den neuesten Erkenntnissen entscheidet die Geschäftsführung: Eure Sicherheitsstrategie wird neu ausgerichtet. Ihr müsst euer Setup anpassen, könnt aber bestehende Investitionen teilweise weiterverwenden. Daher zählt nur die Kostendifferenz.
[Text Placeholder 8] Ihr müsst genau einen Maßnahmenwechsel durchführen.  //  Die Differenz der Init-Kosten muss gezahlt werden oder wird „erstattet“.
[Rechteck: abgerundete Ecken 1] Welle 1
--- slide 3
[Title 2] operative Unterstützung
[Content Placeholder 26] Event: Nach Welle 1
[Text Placeholder 7] Ihr bekommt operative Unterstützung: Ein zentraler Rahmenvertrag bzw. Shared-Service senkt kurzfristig die laufenden Betriebskosten eurer Security-Maßnahmen. Für die nächste Runde wird der Betrieb günstiger, ohne dass ihr an Leistung verliert.
[Text Placeholder 8] Zählt für jede bestehende Maßnahme in der kommenden Runde
[Text Placeholder 8] OPEX Kosten −2.000 € pro aktiver Maßnahme
[Rechteck: abgerundete Ecken 1] Welle 1
--- slide 4
[Title 2] Sparprogramm
[Content Placeholder 26] Event: Nach Welle 2
[Text Placeholder 7] Der CFO verkündet ein konzernweites Sparprogramm, und auch eure Security-Initiativen bleiben nicht verschont. Das Budget wird gekürzt.
[Text Placeholder 8] Gesamtbudget −20.000 €  //  
[Rechteck: abgerundete Ecken 1] Welle 2
--- slide 5
[Title 2] OEM-Audit
[Content Placeholder 26] Event: Nach Welle 2
[Text Placeholder 7] Der große Automobilkunde prüft die Sicherheitsstandards. Im Audit zählt nicht, ob ihr „Best-in-Class“ seid - sondern ob ihr die grundlegenden Kontrollen überhaupt verlässlich umgesetzt habt. 
[Text Placeholder 8] Audit Checkliste (mindestens auf Level 1):  //  M1 IAM/PAM  //  M2 Logging & SIEM/MDR  //  M4 Backup & Disaster Recovery  //  M5 OT/IT-Netz-Segmentierung  //  M7 Vulnerability & Patch Management
[TextBox 41] Bedingung erfüllt:
[TextBox 41] Auswirkung:
[Text Placeholder 8] 0 erfüllt → KZ -15  //  1 erfüllt → KZ -5  //  2-3 erfüllt → KZ +-0  //  4 erfüllt → KZ +5  //  5 erfüllt → KZ +15  //  
[Rechteck: abgerundete Ecken 2] Welle 2
--- slide 6
[Title 2] Kritische Schwachstelle im System
[Content Placeholder 26] Event: Nach Welle 2
[Text Placeholder 7] Ihr werdet von einem Softwarehersteller informiert: In einem von euch genutzten System wurde eine kritische Schwachstelle entdeckt, die aktiv ausgenutzt werden könnte. Prüft die Umsetzung von M7. 
[Text Placeholder 8] Keine Umsetzung (L0): Patch verzögert/chaotisch → KZ −5  //  Level 1: Patch gelingt, aber mit Reibung → KZ ±0  //  Level 2: Patch planbar und zügig → KZ +3  //  Level 3: Patch routiniert, mit Nachweis/Reporting → KZ +7
[Rechteck: abgerundete Ecken 1] Welle 2
--- slide 7
[Title 2] Exzellenz-Bonus
[Content Placeholder 26] Event: Nach Welle 3
[Text Placeholder 7] Maßnahmen, die nachweislich „enterprise-ready“ umgesetzt sind, erhöhen das Vertrauen. Für jede auf höchstem Niveau betriebene Kontrolle gibt es einen Bonus auf eure Kundenzufriedenheit.
[Text Placeholder 8] Für jede Maßnahme auf Level 3 erhaltet ihr +5 KZ.
[Rechteck: abgerundete Ecken 1] Welle 3
--- slide 8
[Title 2] Nervige Authentifizierung
[Content Placeholder 26] Event: Nach Welle 3
[Text Placeholder 7] Ihr zieht die Zugriffskontrollen an, aber die Belegschaft wurde nicht vorbereitet. Die Folge sind viele Support-Tickets und Frust - intern entsteht der Eindruck, dass Security die Arbeit blockiert.
[Text Placeholder 8] Wenn M1 ≥ Level 2 und M6 = Level 0 → KZ -10
[Rechteck: abgerundete Ecken 1] Welle 3
--- slide 9
[Title 2] Budget Review
[Content Placeholder 26] Event: Nach Welle 3
[Text Placeholder 7] Nach Abschluss eurer Beauftragung macht der CFO den Kassensturz: Nicht nur das Sicherheitsniveau zählt, sondern auch, ob ihr das Budget im Griff hattet.
[Text Placeholder 8] Prüft euer Restbudget.  //  Restbudget < 0 € → KZ −15  //  0–25.000 € → KZ ±0  //  25.001–50.000 € → KZ +5  //  50.001–75.000 € → KZ +10  //  ≥ 75.001 € → KZ +15
[Rechteck: abgerundete Ecken 1] Welle 3
```

## K. Massnahmenkarten_Security-Game.pptx: divergences from MEASURE_META

The printed 30-slide deck shows `focus` as `Maßnahme - <focus>`, the measure `description`, and ONE level text (= `levels_simple` of `generate_from_template.py`, i.e. WITHOUT the `Grundschutz:/Besser:/Premium:` prefix of `generate_pptx_cards.py`). `levels_desc` is not printed. Three slides differ from the template copy of MEASURE_META:

| Slide | Card | Printed text | MEASURE_META text | Verdict |
|---|---|---|---|---|
| 1 | M1 L1 | `Zentrale Benutzerverwaltung, Admins brauchen zwei Faktoren zum Einloggen` (no final period) | same text with final period | cosmetic |
| 18 | M6 L3 | `Externe Sicherheitsexperten überwachen rund um die Uhr.` (M2 L3 text pasted by mistake) | `Spezielle Trainings je nach Rolle, klarer Prozess zum Melden von Verdachtsfällen.` | printed deck wrong, drop |
| 28 | M10 L1 | `Protokolle werden gesammelt und 30 Tage aufbewahrt.` (M2 L1 text pasted by mistake) | `PIN-Schutz Pflicht, bei Verlust kann das Gerät aus der Ferne gelöscht werden.` | printed deck wrong, drop |

## L. Editorial deltas to confirm at the D-13d review (found while extracting)

1. `Angriff-1_Ransomware.docx`: the scenario paragraph says `Ihrer Sicherheitsmaßnahmen` (formal) while every other sheet uses `ihr/euer`. Proposed: `eurer`.
2. `Angriff-3_Datenexfiltration.docx` bonus intro lacks `mindestens` ("auf dem richtigen Level") while sheets 1 and 2 say `mindestens auf dem richtigen Level`. Proposed: one shared `sheets.angriff.bonus_intro` with `mindestens` (the rule is `>= min_level`).
3. Worksheet headings differ from the config wave names: `Angriff 2: OT-Störung (Produktionsausfall)` and `Angriff 3: Datenexfiltration` vs config `OT-Störung` / `Exfiltration`. Proposed `attacks.<id>.name` = short config-equivalent name; `Produktionsausfall` is a subtitle if wanted.
4. `Anfrage-Mail.docx`: `Beratungs-projekt` (stray hyphen from a line wrap). Proposed: `Beratungsprojekt`.
5. `Events_Security-Game.pptx` slide 2 (Kurswechsel) still says `Maßnahmenwechsel` (retired term, RULE-01). The migrated narrative must say `Maßnahmentausch`; the rule text stays the current config text.
6. `Budget.docx` says `Verfügbares Budget ... Euro` and `Antizipierte Summe`; `INIT-Kosten` (caps) vs `Init-Kosten` elsewhere. Pick one spelling.
7. Bonus-table labels on the worksheets (`M3 - EDR/XDR`, `M4 - Backup`, `M5 - Netz-Segmentierung`, `M6 - Awareness`, `M7 - Patch Management`, `M8 - Supplier Security`, `M2 - Logging & SIEM`) are shorter than config `measures.*.name`. Phase 4 decides: use config names (wording change) or add a short-label key.
