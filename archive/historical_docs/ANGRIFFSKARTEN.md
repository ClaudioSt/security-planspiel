# ANGRIFFSKARTEN v3.0

**Druckvorlagen für 3 Wellen-Angriffe**
*Format: A4, gut lesbar, mit E-Wert-basiertem Rechenbeispiel*

---

## WELLE 1: RANSOMWARE-ANGRIFF (Office-IT)

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           WELLE 1: RANSOMWARE-ANGRIFF                     ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  NARRATIVE:                                               ║
║  ─────────────────────────────────────────────────────────║
║  Montag, 08:15 Uhr. Ein Mitarbeiter in der Buchhaltung    ║
║  oeffnet eine E-Mail mit dem Betreff "Rechnung ueberfaellig".║
║                                                           ║
║  Der Anhang enthaelt Emotet-Malware. Innerhalb von 2 Stunden║
║  sind Dateifreigaben, SharePoint und der Office-File-Server║
║  verschluesselt. Die Erpresser fordern 50.000 Euro Loesegeld.║
║                                                           ║
║  Die IT bemerkt den Angriff erst, als Mitarbeitende sich  ║
║  beschweren: "Alle Dateien haben die Endung .locked!"     ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  ANGRIFFS-PARAMETER:                                      ║
║  ─────────────────────────────────────────────────────────║
║  baseSeverity:        8                                   ║
║  sUnit (Schaden/G):   20k Euro                            ║
║  kzUnit (KZ-Verlust/G): 2                                 ║
║  CIA-Impact/Stufe:    C-2, I-2, A-1                       ║
║  Mitigation-Cap:      8 (max. Reduktion)                  ║
║  E-Schwelle:          15                                  ║
║  CIA-Gewichte:        C=0.4, I=0.4, A=0.2                 ║
║  KZ-Bonus/Malus:      +5 / -3                             ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  BONUS-MASSNAHMEN (bei Level 2+):                         ║
║  ─────────────────────────────────────────────────────────║
║  M3 (EDR/XDR):        +2 Bonus (erkennt Ransomware frueh) ║
║  M4 (Backup):         +2 Bonus (schnelle Wiederherstellung)║
║  M6 (Awareness):      +1 Bonus (erkennt Phishing)         ║
║                                                           ║
║  BESTE ABWEHR: M3 L2 + M4 L2 + M6 L2 (max. +5 Bonus)     ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  BERECHNUNGS-BEISPIEL (gut vorbereitet):                  ║
║  ─────────────────────────────────────────────────────────║
║  Team hat:                                                ║
║  - M3 (EDR) L2     -> CIA: C+5, I+4, A+2                  ║
║  - M4 (Backup) L2  -> CIA: C+1, I+6, A+5, Recovery 30%    ║
║  - M6 (Awareness) L2 -> CIA: C+3, I+2, A+2                ║
║  - M2 (SIEM) L1    -> CIA: C+1, I+3, A+0                  ║
║                                                           ║
║  Team-CIA: C=10+5+1+3+1=20, I=10+4+6+2+3=25, A=10+2+5+2=19║
║                                                           ║
║  Schritt 1: E-Wert berechnen                              ║
║  E = 0.4*20 + 0.4*25 + 0.2*19 = 8+10+3.8 = 21.8           ║
║                                                           ║
║  Schritt 2: Severity-Reduktion                            ║
║  sev_red = (21.8 - 15) / 1 = 6.8                          ║
║                                                           ║
║  Schritt 3: Bonus-Reduktion                               ║
║  M3 L2 (+2) + M4 L2 (+2) + M6 L2 (+1) = +5                ║
║                                                           ║
║  Schritt 4: Final Severity                                ║
║  G = max(0, 8 - 6.8 - 5) = max(0, -3.8) = 0               ║
║                                                           ║
║  Schritt 5: Schaden & KZ                                  ║
║  Damage = 0 * 20 = 0k Euro                                ║
║  KZ: E >= 15? Ja -> +5 Bonus                              ║
║                                                           ║
║  ANGRIFF KOMPLETT GESTOPPT! KZ +5                         ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  WENN SCHLECHT VORBEREITET (Worst Case):                  ║
║  ─────────────────────────────────────────────────────────║
║  Team hat: Nur M1 (IAM) L1 -> CIA: C+2, I+1, A+0          ║
║                                                           ║
║  Team-CIA: C=12, I=11, A=10                               ║
║  E = 0.4*12 + 0.4*11 + 0.2*10 = 4.8+4.4+2 = 11.2          ║
║                                                           ║
║  sev_red = (11.2 - 15) / 1 = -3.8 (negativ = keine!)      ║
║  bonus = 0 (keine Bonus-Measures auf L2+)                 ║
║  G = max(0, 8 - 0 - 0) = 8                                ║
║                                                           ║
║  Damage = 8 * 20 = 160k Euro                              ║
║  KZ-Verlust = -(8 * 2) = -16                              ║
║  E < 15? -> KZ-Malus -3                                   ║
║  Gesamt KZ-Delta: -16 + (-3) = -19                        ║
║                                                           ║
║  ABER: Falls M4 L2 vorhanden -> Recovery 30%              ║
║  Damage_final = 160 * 0.7 = 112k Euro                     ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  LERNZIEL WELLE 1:                                        ║
║  ─────────────────────────────────────────────────────────║
║  - EDR erkennt Ransomware frueh (M3)!                     ║
║  - Backups retten im Notfall (M4)!                        ║
║  - Awareness verhindert Phishing-Klicks (M6)!             ║
║  - Ohne Vorbereitung: Schaden bis 160k Euro!              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## WELLE 2: OT-STOERUNG (Produktionsausfall)

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║      WELLE 2: OT-STOERUNG (PRODUKTIONSAUSFALL)            ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  NARRATIVE:                                               ║
║  ─────────────────────────────────────────────────────────║
║  Mittwoch, 14:30 Uhr. Die Fertigungslinie 2 stoppt        ║
║  unerwartet. Das MES-System zeigt Fehlermeldungen.        ║
║                                                           ║
║  Ursache: Eine Schwachstelle in der SPS-Software (Siemens ║
║  Sinumerik) wurde ausgenutzt. Malware infiltrierte das    ║
║  OT-Netz und manipulierte Steuerungsbefehle.              ║
║                                                           ║
║  Folgen:                                                  ║
║  - Fertigungslinie 2 faellt fuer 18 Stunden aus           ║
║  - Liefertermine an OEM gefaehrdet (JIT!)                 ║
║  - Neustart dauert (MES-Konfiguration wiederherstellen)   ║
║  - Vertragsstrafen drohen                                 ║
║                                                           ║
║  Der OEM ruft an: "Wo bleiben unsere Teile?"              ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  ANGRIFFS-PARAMETER:                                      ║
║  ─────────────────────────────────────────────────────────║
║  baseSeverity:        10  (sehr hoch!)                    ║
║  sUnit (Schaden/G):   32k Euro  (Produktion = teuer!)     ║
║  kzUnit (KZ-Verlust/G): 2                                 ║
║  CIA-Impact/Stufe:    C-1, I-2, A-3                       ║
║  Mitigation-Cap:      10                                  ║
║  E-Schwelle:          17                                  ║
║  CIA-Gewichte:        C=0.2, I=0.2, A=0.6                 ║
║  KZ-Bonus/Malus:      +7 / -5                             ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  BONUS-MASSNAHMEN (bei Level 2+):                         ║
║  ─────────────────────────────────────────────────────────║
║  M5 (OT-Segmentierung): +3 Bonus (isoliert Produktion)    ║
║  M7 (Patch Management): +2 Bonus (schliesst OT-Luecken)   ║
║                                                           ║
║  BESTE ABWEHR: M5 L2+ (max. +5 Bonus moeglich)            ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  BERECHNUNGS-BEISPIEL (gut vorbereitet):                  ║
║  ─────────────────────────────────────────────────────────║
║  Team hat:                                                ║
║  - M5 (OT-Seg) L2   -> CIA: C+3, I+2, A+6                 ║
║  - M7 (Patching) L2 -> CIA: C+4, I+5, A+3                 ║
║  - M2 (SIEM) L1     -> CIA: C+1, I+3, A+0                 ║
║                                                           ║
║  Team-CIA: C=10+3+4+1=18, I=10+2+5+3=20, A=10+6+3+0=19    ║
║                                                           ║
║  Schritt 1: E-Wert berechnen (Fokus auf Availability!)    ║
║  E = 0.2*18 + 0.2*20 + 0.6*19 = 3.6+4+11.4 = 19.0         ║
║                                                           ║
║  Schritt 2: Severity-Reduktion                            ║
║  sev_red = (19.0 - 17) / 1 = 2.0                          ║
║                                                           ║
║  Schritt 3: Bonus-Reduktion                               ║
║  M5 L2 (+3) + M7 L2 (+2) = +5                             ║
║                                                           ║
║  Schritt 4: Final Severity                                ║
║  G = max(0, 10 - 2 - 5) = max(0, 3) = 3                   ║
║                                                           ║
║  Schritt 5: Schaden & KZ                                  ║
║  Damage = 3 * 32 = 96k Euro                               ║
║  KZ-Verlust = -(3 * 2) = -6                               ║
║  KZ: E >= 17? Ja -> +7 Bonus                              ║
║  Gesamt KZ-Delta: -6 + 7 = +1                             ║
║                                                           ║
║  Schaden begrenzt auf 96k, KZ sogar leicht positiv!       ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  WENN SCHLECHT VORBEREITET (Worst Case):                  ║
║  ─────────────────────────────────────────────────────────║
║  Team hat: Nur M7 (Patching) L1 -> CIA: C+2, I+3, A+2     ║
║                                                           ║
║  Team-CIA: C=12, I=13, A=12                               ║
║  E = 0.2*12 + 0.2*13 + 0.6*12 = 2.4+2.6+7.2 = 12.2        ║
║                                                           ║
║  sev_red = (12.2 - 17) / 1 = -4.8 (negativ = keine!)      ║
║  bonus = 0 (M7 nur L1, braucht L2+)                       ║
║  G = max(0, 10 - 0 - 0) = 10                              ║
║                                                           ║
║  Damage = 10 * 32 = 320k Euro (Katastrophe!)              ║
║  KZ-Verlust = -(10 * 2) = -20                             ║
║  E < 17? -> KZ-Malus -5                                   ║
║  Gesamt KZ-Delta: -20 + (-5) = -25                        ║
║                                                           ║
║  Recovery durch M4 (Backup) L2 moeglich:                  ║
║  Damage_final = 320 * 0.7 = 224k Euro (immer noch schlimm!)║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  LERNZIEL WELLE 2:                                        ║
║  ─────────────────────────────────────────────────────────║
║  - OT-Segmentierung ist KRITISCH (M5 +3 Bonus)!           ║
║  - OT-Patching reduziert Angriffsflaeche (M7)!            ║
║  - Ohne OT-Schutz: Schaden bis 320k Euro!                 ║
║  - A-Wert ist hier am wichtigsten (60% Gewicht)!          ║
║                                                           ║
║  Event: OEM-Audit wird nach dieser Welle ausgeloest!      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## WELLE 3: DATENEXFILTRATION (IP-DIEBSTAHL)

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       WELLE 3: DATENEXFILTRATION (IP-DIEBSTAHL)           ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  NARRATIVE:                                               ║
║  ─────────────────────────────────────────────────────────║
║  Freitag, 10:00 Uhr. Ein Anruf vom BSI (Bundesamt fuer    ║
║  Sicherheit in der Informationstechnik):                  ║
║                                                           ║
║  "Wir haben Hinweise, dass Konstruktionsdaten Ihres       ║
║  Unternehmens im Darknet zum Verkauf angeboten werden."   ║
║                                                           ║
║  Forensische Analyse ergibt: Ueber einen kompromittierten ║
║  Lieferanten-Zugang (CAD-Support) gelangte ein APT-       ║
║  aehnlicher Angreifer ins Netz. Unbemerkt wurden ueber    ║
║  3 Wochen CAD-Dateien und Prozessdokumente exfiltriert.   ║
║                                                           ║
║  Folgen:                                                  ║
║  - Wettbewerbsnachteil (Know-how abgeflossen)             ║
║  - OEM verliert Vertrauen (TISAX-Zertifizierung fraglich) ║
║  - Medienecho ("Mittelstaendler gehackt")                 ║
║  - Potenzielle Schadensersatzforderungen                  ║
║                                                           ║
║  Der Geschaeftsfuehrer: "Wie konnte das passieren?"       ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  ANGRIFFS-PARAMETER:                                      ║
║  ─────────────────────────────────────────────────────────║
║  baseSeverity:        7                                   ║
║  sUnit (Schaden/G):   20k Euro                            ║
║  kzUnit (KZ-Verlust/G): 2                                 ║
║  CIA-Impact/Stufe:    C-3, I-1, A-0  (Confidentiality!)   ║
║  Mitigation-Cap:      7                                   ║
║  E-Schwelle:          19                                  ║
║  CIA-Gewichte:        C=0.5, I=0.3, A=0.2                 ║
║  KZ-Bonus/Malus:      +10 / -7                            ║
║  allow_recovery:      NEIN (Daten sind raus!)             ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  BONUS-MASSNAHMEN (bei Level 2+):                         ║
║  ─────────────────────────────────────────────────────────║
║  M1 (IAM/PAM):        +2 Bonus (verhindert unbef. Zugriff)║
║  M2 (SIEM):           +2 Bonus (erkennt Datenabfluss)     ║
║  M8 (Supplier Sec.):  +1 Bonus (schuetzt Schnittstellen)  ║
║                                                           ║
║  BESTE ABWEHR: M1 L2 + M2 L2 + M8 L2 (max. +5 Bonus)     ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  BERECHNUNGS-BEISPIEL (gut vorbereitet):                  ║
║  ─────────────────────────────────────────────────────────║
║  Team hat:                                                ║
║  - M1 (IAM) L2     -> CIA: C+4, I+3, A+0                  ║
║  - M2 (SIEM) L2    -> CIA: C+2, I+5, A+1                  ║
║  - M8 (Supplier) L2 -> CIA: C+2, I+4, A+4                 ║
║  - M3 (EDR) L1     -> CIA: C+3, I+2, A+1                  ║
║                                                           ║
║  Team-CIA: C=10+4+2+2+3=21, I=10+3+5+4+2=24, A=10+0+1+4+1=16║
║                                                           ║
║  Schritt 1: E-Wert berechnen (Fokus auf Confidentiality!) ║
║  E = 0.5*21 + 0.3*24 + 0.2*16 = 10.5+7.2+3.2 = 20.9       ║
║                                                           ║
║  Schritt 2: Severity-Reduktion                            ║
║  sev_red = (20.9 - 19) / 1 = 1.9                          ║
║                                                           ║
║  Schritt 3: Bonus-Reduktion                               ║
║  M1 L2 (+2) + M2 L2 (+2) + M8 L2 (+1) = +5                ║
║                                                           ║
║  Schritt 4: Final Severity                                ║
║  G = max(0, 7 - 1.9 - 5) = max(0, 0.1) = 0                ║
║  (gerundet, da Severity ganzzahlig)                       ║
║                                                           ║
║  Schritt 5: Schaden & KZ                                  ║
║  Damage = 0 * 20 = 0k Euro                                ║
║  KZ: E >= 19? Ja -> +10 Bonus                             ║
║                                                           ║
║  Angriff erkannt und gestoppt! KZ +10                     ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  WENN SCHLECHT VORBEREITET (Worst Case):                  ║
║  ─────────────────────────────────────────────────────────║
║  Team hat: Nur M1 (IAM) L1 -> CIA: C+2, I+1, A+0          ║
║                                                           ║
║  Team-CIA: C=12, I=11, A=10                               ║
║  E = 0.5*12 + 0.3*11 + 0.2*10 = 6+3.3+2 = 11.3            ║
║                                                           ║
║  sev_red = (11.3 - 19) / 1 = -7.7 (negativ = keine!)      ║
║  bonus = 0 (keine Bonus-Measures auf L2+)                 ║
║  G = max(0, 7 - 0 - 0) = 7                                ║
║                                                           ║
║  Damage = 7 * 20 = 140k Euro (Wettbewerbsnachteil!)       ║
║  KZ-Verlust = -(7 * 2) = -14                              ║
║  E < 19? -> KZ-Malus -7                                   ║
║  Gesamt KZ-Delta: -14 + (-7) = -21                        ║
║                                                           ║
║  KEINE Recovery moeglich! (Daten sind abgeflossen)        ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  LERNZIEL WELLE 3:                                        ║
║  ─────────────────────────────────────────────────────────║
║  - PAM haette Lieferanten-Zugang abgesichert (M1)!        ║
║  - SIEM/MDR haette Anomalien erkannt (M2)!                ║
║  - Supplier Security ist kein "Nice-to-have" (M8)!        ║
║  - IP-Verlust = langfristiger Schaden, nicht recoverable  ║
║  - C-Wert ist hier am wichtigsten (50% Gewicht)!          ║
║                                                           ║
║  Event: NIS2-Pruefung nach dieser Welle!                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## WELLENUEBERSICHT (fuer Moderatoren)

| Welle | Angriff | Fokus | baseSev | sUnit | kzUnit | E-Ziel | Cap | KZ +/- | Top-Abwehr |
|-------|---------|-------|---------|-------|--------|--------|-----|--------|------------|
| 1 | Ransomware | C+I | 8 | 20 | 2 | 15 | 8 | +5/-3 | M3+M4+M6 (L2) |
| 2 | OT-Stoerung | A | 10 | 32 | 2 | 17 | 10 | +7/-5 | M5+M7 (L2) |
| 3 | Exfiltration | C | 7 | 20 | 2 | 19 | 7 | +10/-7 | M1+M2+M8 (L2) |

### CIA-Gewichte pro Welle

| Welle | C-Gewicht | I-Gewicht | A-Gewicht |
|-------|-----------|-----------|-----------|
| 1 Ransomware | 0.4 | 0.4 | 0.2 |
| 2 OT-Stoerung | 0.2 | 0.2 | **0.6** |
| 3 Exfiltration | **0.5** | 0.3 | 0.2 |

### Bonus-Measures Uebersicht

| Welle | Measure | Bonus | Begruendung |
|-------|---------|-------|-------------|
| 1 | M3 (EDR) L2+ | +2 | Erkennt Ransomware frueh |
| 1 | M4 (Backup) L2+ | +2 | Ermoeglicht schnelle Wiederherstellung |
| 1 | M6 (Awareness) L2+ | +1 | Geschulte Mitarbeiter erkennen Phishing |
| 2 | M5 (OT-Seg) L2+ | +3 | Isoliert Produktion vom Office-Netz |
| 2 | M7 (Patching) L2+ | +2 | Schliesst OT-Schwachstellen |
| 3 | M1 (IAM) L2+ | +2 | Verhindert unbefugten Zugriff |
| 3 | M2 (SIEM) L2+ | +2 | Erkennt Datenabfluss |
| 3 | M8 (Supplier) L2+ | +1 | Schuetzt Lieferanten-Schnittstellen |

---

## DRAMATURGIE (Moderator-Hinweise)

### Welle 1: "Der Klassiker"
**Ziel:** Teams verstehen Ransomware-Bedrohung, Awareness-Wert, Backup-Notwendigkeit.
**Spannung:** Moderat (viele Massnahmen wirken, E-Ziel 15 erreichbar)
**Lerneffekt:** Bonus-Measures zeigen (M3+M4+M6 = +5!)

---

### Welle 2: "Das OT-Desaster"
**Ziel:** Teams erkennen OT-Spezifika, Segmentierung-Wert, Produktionskritikalitaet.
**Spannung:** Hoch (baseSev=10, sUnit=32 -> grosse Schaeden moeglich!)
**Lerneffekt:** Wer M5 vernachlaessigt hat, zahlt jetzt drauf. A-Wert zählt 60%!

**Event danach:** OEM-Audit (KZ-Effekt je nach E-Wert)

---

### Welle 3: "Das stille Leck"
**Ziel:** Teams verstehen APT, Supplier-Risiken, Langzeitschaeden.
**Spannung:** Mittel-Hoch (E-Ziel 19 ist anspruchsvoll, keine Recovery!)
**Lerneffekt:** Lieferanten-Sicherheit ist wichtig (M8). C-Wert zaehlt 50%!

**Event danach:** NIS2-Pruefung (4+ Massnahmen auf L2?)

---

## MODERATOR-CHEAT-SHEET (E-Wert-Rechenschritte)

**Fuer jede Welle:**

1. **Team-CIA sammeln:**
   - Basis: C=10, I=10, A=10
   - Pro Massnahme: CIA-Werte addieren

2. **E-Wert berechnen:**
   ```
   E = wC × Team_C + wI × Team_I + wA × Team_A
   ```
   - Welle 1: E = 0.4×C + 0.4×I + 0.2×A
   - Welle 2: E = 0.2×C + 0.2×I + 0.6×A
   - Welle 3: E = 0.5×C + 0.3×I + 0.2×A

3. **Severity-Reduktion:**
   ```
   sev_red = max(0, (E - E_threshold) / 1)
   ```

4. **Bonus-Reduktion:**
   - Nur wenn Measure auf Level 2+!
   - Addieren aller aktiven Boni

5. **Final Severity:**
   ```
   G = max(0, baseSeverity - sev_red - bonus_red)
   ```

6. **Schaden:**
   ```
   Damage = G × sUnit (in 1.000 Euro)
   ```

7. **Recovery (nur Welle 1+2, wenn M4 vorhanden):**
   ```
   Damage_final = Damage × (1 - Recovery%)
   L1: 10%, L2: 30%, L3: 50%
   ```

8. **KZ-Delta:**
   ```
   Base: -(G × kzUnit)
   Bonus/Malus: E >= E_threshold? +KZ_Bonus : +KZ_Malus
   KZ_neu = clamp(KZ_alt + Delta, 0, 100)
   ```

---

## SCHNELLREFERENZ: Worst-Case Schaeden (ohne Massnahmen)

| Welle | baseSev | sUnit | Max Schaden | kzUnit | Max KZ-Verlust | KZ-Malus |
|-------|---------|-------|-------------|--------|----------------|----------|
| 1 | 8 | 20 | 160k Euro | 2 | -16 | -3 |
| 2 | 10 | 32 | 320k Euro | 2 | -20 | -5 |
| 3 | 7 | 20 | 140k Euro | 2 | -14 | -7 |
| **TOTAL** | - | - | **620k Euro** | - | **-50** | **-15** |

---

**Diese Angriffskarten visualisieren die Bedrohungen und helfen beim Nachvollziehen!**
