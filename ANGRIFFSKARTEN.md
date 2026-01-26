# ANGRIFFSKARTEN v2.0

**Druckvorlagen für 3 Wellen-Angriffe**
*Format: A4, gut lesbar, mit Rechenbeispiel*

---

## WELLE 1: RANSOMWARE-ANGRIFF (Office-IT)

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🔥 WELLE 1: RANSOMWARE-ANGRIFF 🔥               ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  NARRATIVE:                                               ║
║  ─────────────────────────────────────────────────────────║
║  Montag, 08:15 Uhr. Ein Mitarbeiter in der Buchhaltung    ║
║  öffnet eine E-Mail mit dem Betreff "Rechnung überfällig".║
║                                                           ║
║  Der Anhang enthält Emotet-Malware. Innerhalb von 2 Stunden
║  sind Dateifreigaben, SharePoint und der Office-File-Server
║  verschlüsselt. Die Erpresser fordern 50.000€ Lösegeld.   ║
║                                                           ║
║  Die IT bemerkt den Angriff erst, als Mitarbeitende sich  ║
║  beschweren: "Alle Dateien haben die Endung .locked!"     ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  ANGRIFFS-PARAMETER:                                      ║
║  ─────────────────────────────────────────────────────────║
║  baseSeverity:        8                                   ║
║  sUnit (Schaden/G):   20k€                                ║
║  kzUnit (KZ-Verlust/G): 3                                 ║
║  CIA-Impact/Stufe:    C-2, I-2, A-1                       ║
║  Mitigation-Cap:      10 (max. Reduktion)                 ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  WELCHE MASSNAHMEN WIRKEN?                                ║
║  ─────────────────────────────────────────────────────────║
║  ✓ M1 (IAM):       -1 / -2 / -3   (L1/L2/L3)              ║
║  ✓ M2 (SIEM):      -1 / -2 / -3                           ║
║  ✓ M3 (EDR):       -2 / -3 / -5   (L3: +1 Kontext-Bonus!) ║
║  ✓ M4 (Backup):    -1 / -2 / -5   (L3: +1 Kontext-Bonus!) ║
║  ✓ M5 (OT-Seg):     0 / -1 / -2                           ║
║  ✓ M6 (Awareness): -1 / -4 / -6   (L2+L3: Kontext-Bonus!) ║
║  ✓ M7 (Patching):  -1 / -2 / -3                           ║
║  ✓ M8-M10:         Keine Wirkung                          ║
║                                                           ║
║  ⭐ BESTE ABWEHR: M6 (Awareness) L3 + M3 (EDR) L3!        ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  BERECHNUNGS-BEISPIEL:                                    ║
║  ─────────────────────────────────────────────────────────║
║  Team hat:                                                ║
║  - M3 (EDR) L3      → Mitigation -5                       ║
║  - M6 (Awareness) L2 → Mitigation -4                      ║
║  - M4 (Backup) L2   → Mitigation -2                       ║
║                                                           ║
║  Schritt 1: Mitigation-Summe                              ║
║  M_sum = min(10, 5+4+2) = min(10, 11) = 10                ║
║                                                           ║
║  Schritt 2: Endschwere                                    ║
║  G = max(0, 8 - 10) = max(0, -2) = 0  ← PERFEKT ABGEWEHRT!║
║                                                           ║
║  Schritt 3: Schaden                                       ║
║  Damage = 0 × 20 = 0k€                                    ║
║                                                           ║
║  Schritt 4: KZ-Delta                                      ║
║  ΔKZ = -(0 × 3) = 0  (keine KZ-Einbuße!)                  ║
║                                                           ║
║  Schritt 5: CIA-Mali                                      ║
║  Keine (da G=0)                                           ║
║                                                           ║
║  ✅ Angriff komplett gestoppt!                            ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  WENN SCHLECHT VORBEREITET (Worst Case):                  ║
║  ─────────────────────────────────────────────────────────║
║  Team hat: Nur M1 (IAM) L1 → Mitigation -1                ║
║                                                           ║
║  G = max(0, 8 - 1) = 7                                    ║
║  Damage = 7 × 20 = 140k€                                  ║
║  ΔKZ = -(7 × 3) = -21  (KZ sinkt!)                        ║
║  CIA-Mali: C-14, I-14, A-7                                ║
║                                                           ║
║  ABER: M4 (Backup) L2 -> Recovery 30%                     ║
║  Damage_final = 140 × 0.7 = 98k€  (etwas besser)          ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  LERNZIEL WELLE 1:                                        ║
║  ─────────────────────────────────────────────────────────║
║  • Awareness ist Gold wert (M6)!                          ║
║  • EDR kann Ransomware früh stoppen (M3)!                 ║
║  • Backups retten im Notfall (M4)!                        ║
║  • Ohne Vorbereitung: Schaden >140k€!                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## WELLE 2: OT-STÖRUNG (Produktionsausfall)

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║      ⚠️ WELLE 2: OT-STÖRUNG (PRODUKTIONSAUSFALL) ⚠️       ║
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
║  - Fertigungslinie 2 fällt für 18 Stunden aus             ║
║  - Liefertermine an OEM gefährdet (JIT!)                  ║
║  - Neustart dauert (MES-Konfiguration wiederherstellen)   ║
║  - Vertragsstrafen drohen                                 ║
║                                                           ║
║  Der OEM ruft an: "Wo bleiben unsere Teile?"              ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  ANGRIFFS-PARAMETER:                                      ║
║  ─────────────────────────────────────────────────────────║
║  baseSeverity:        10  (sehr hoch!)                    ║
║  sUnit (Schaden/G):   32k€  (Produktion = teuer!)         ║
║  kzUnit (KZ-Verlust/G): 3                                 ║
║  CIA-Impact/Stufe:    C-1, I-2, A-3                       ║
║  Mitigation-Cap:      12                                  ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  WELCHE MASSNAHMEN WIRKEN?                                ║
║  ─────────────────────────────────────────────────────────║
║  ✓ M2 (SIEM):       0 / -1 / -2                           ║
║  ✓ M4 (Backup):     0 / -1 / -2   (hilft bei Recovery)    ║
║  ✓ M5 (OT-Seg):    -1 / -5 / -7   (L2+L3: +2 Bonus!) ⭐   ║
║  ✓ M7 (Patching):  -1 / -3 / -4   (L2+L3: +1 Bonus!)      ║
║  ✓ M8 (Supplier):   0 / -1 / -2                           ║
║  ✓ M1, M3, M6, M9, M10: Keine Wirkung                     ║
║                                                           ║
║  ⭐ BESTE ABWEHR: M5 (OT-Segmentierung) L3!               ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  BERECHNUNGS-BEISPIEL (gut vorbereitet):                  ║
║  ─────────────────────────────────────────────────────────║
║  Team hat:                                                ║
║  - M5 (OT-Seg) L3   → Mitigation -7  (inkl. Bonus!)       ║
║  - M7 (Patching) L2 → Mitigation -3  (inkl. Bonus!)       ║
║  - M2 (SIEM) L2     → Mitigation -1                       ║
║                                                           ║
║  Schritt 1: Mitigation-Summe                              ║
║  M_sum = min(12, 7+3+1) = min(12, 11) = 11                ║
║                                                           ║
║  Schritt 2: Endschwere                                    ║
║  G = max(0, 10 - 11) = max(0, -1) = 0  ← PERFEKT!         ║
║                                                           ║
║  Schritt 3: Schaden                                       ║
║  Damage = 0 × 32 = 0k€                                    ║
║                                                           ║
║  Produktion läuft weiter!                              ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  WENN SCHLECHT VORBEREITET (Worst Case):                  ║
║  ─────────────────────────────────────────────────────────║
║  Team hat: Nur M7 (Patching) L1 → Mitigation -1           ║
║                                                           ║
║  G = max(0, 10 - 1) = 9                                   ║
║  Damage = 9 × 32 = 288k€  (Katastrophe!)                  ║
║  ΔKZ = -(9 × 3) = -27  (KZ sinkt stark!)                  ║
║  CIA-Mali: C-9, I-18, A-27  (Availability stark getroffen)║
║                                                           ║
║  Recovery durch M4 (Backup) L2 moeglich:                  ║
║  Damage_final = 288 × 0.7 = 202k€  (immer noch schlimm!)  ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  LERNZIEL WELLE 2:                                        ║
║  ─────────────────────────────────────────────────────────║
║  • OT-Segmentierung ist KRITISCH (M5)!                    ║
║  • OT-Patching reduziert Angriffsfläche (M7)!             ║
║  • Ohne OT-Schutz: Schaden >280k€ + OEM-Aerger!           ║
║  • 24/5-Betrieb + JIT = hohe Ausfallkosten                ║
║                                                           ║
║  📌 Event: OEM-Audit wird nach dieser Welle ausgelöst!    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## WELLE 3: DATENEXFILTRATION (IP-DIEBSTAHL)

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       🕵️ WELLE 3: DATENEXFILTRATION (IP-DIEBSTAHL) 🕵️      ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  NARRATIVE:                                               ║
║  ─────────────────────────────────────────────────────────║
║  Freitag, 10:00 Uhr. Ein Anruf vom BSI (Bundesamt für     ║
║  Sicherheit in der Informationstechnik):                  ║
║                                                           ║
║  "Wir haben Hinweise, dass Konstruktionsdaten Ihres       ║
║  Unternehmens im Darknet zum Verkauf angeboten werden."   ║
║                                                           ║
║  Forensische Analyse ergibt: Über einen kompromittierten  ║
║  Lieferanten-Zugang (CAD-Support) gelangte ein APT-       ║
║  ähnlicher Angreifer ins Netz. Unbemerkt wurden über      ║
║  3 Wochen CAD-Dateien und Prozessdokumente exfiltriert.   ║
║                                                           ║
║  Folgen:                                                  ║
║  - Wettbewerbsnachteil (Know-how abgeflossen)             ║
║  - OEM verliert Vertrauen (TISAX-Zertifizierung fraglich) ║
║  - Medienecho ("Mittelständler gehackt")                  ║
║  - Potenzielle Schadensersatzforderungen                  ║
║                                                           ║
║  Der Geschäftsführer: "Wie konnte das passieren?"         ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  ANGRIFFS-PARAMETER:                                      ║
║  ─────────────────────────────────────────────────────────║
║  baseSeverity:        7                                   ║
║  sUnit (Schaden/G):   20k€  (mittelfristig!)              ║
║  kzUnit (KZ-Verlust/G): 3                                 ║
║  CIA-Impact/Stufe:    C-3, I-1, A-0  (Confidentiality!)   ║
║  Mitigation-Cap:      10                                  ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  WELCHE MASSNAHMEN WIRKEN?                                ║
║  ─────────────────────────────────────────────────────────║
║  ✓ M1 (IAM):       -1 / -2 / -4   (L3: +1 Bonus!) ⭐      ║
║  ✓ M2 (SIEM):      -1 / -2 / -4   (L3: +1 Bonus!)         ║
║  ✓ M3 (EDR):       -1 / -2 / -3                           ║
║  ✓ M7 (Patching):   0 / -1 / -2                           ║
║  ✓ M8 (Supplier):   0 / -1 / -3   (L3: +1 Bonus!) ⭐      ║
║  ✓ M4, M5, M6, M9, M10: Keine Wirkung                     ║
║                                                           ║
║  ⭐ BESTE ABWEHR: M1 (IAM) L3 + M2 (SIEM) L3 + M8 L3!     ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  BERECHNUNGS-BEISPIEL (gut vorbereitet):                  ║
║  ─────────────────────────────────────────────────────────║
║  Team hat:                                                ║
║  - M1 (IAM) L3      → Mitigation -4  (inkl. Bonus!)       ║
║  - M2 (SIEM) L3     → Mitigation -4  (inkl. Bonus!)       ║
║  - M8 (Supplier) L2 → Mitigation -1                       ║
║                                                           ║
║  Schritt 1: Mitigation-Summe                              ║
║  M_sum = min(10, 4+4+1) = min(10, 9) = 9                  ║
║                                                           ║
║  Schritt 2: Endschwere                                    ║
║  G = max(0, 7 - 9) = max(0, -2) = 0  ← PERFEKT!           ║
║                                                           ║
║  Schritt 3: Schaden                                       ║
║  Damage = 0 × 20 = 0k€                                    ║
║                                                           ║
║  Angriff erkannt und gestoppt!                         ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  WENN SCHLECHT VORBEREITET (Worst Case):                  ║
║  ─────────────────────────────────────────────────────────║
║  Team hat: Nur M1 (IAM) L1 → Mitigation -1                ║
║                                                           ║
║  G = max(0, 7 - 1) = 6                                    ║
║  Damage = 6 × 20 = 120k€  (Wettbewerbsnachteil!)          ║
║  ΔKZ = -(6 × 3) = -18  (OEM verliert Vertrauen!)          ║
║  CIA-Mali: C-18, I-6, A-0  (Confidentiality massiv!)      ║
║                                                           ║
║  ⚠️ Keine Recovery möglich (Daten sind raus!)             ║
║                                                           ║
║  ─────────────────────────────────────────────────────────║
║  LERNZIEL WELLE 3:                                        ║
║  ─────────────────────────────────────────────────────────║
║  • PAM hätte Lieferanten-Zugang abgesichert (M1)!         ║
║  • SIEM/MDR hätte Anomalien erkannt (M2)!                 ║
║  • Supplier Security ist kein "Nice-to-have" (M8)!        ║
║  • IP-Verlust = langfristiger Schaden, schwer zu beziffern║
║                                                           ║
║  📌 Event: DSGVO-Bonus möglich (wenn M1+M2 ≥L2)!          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## WELLENÜBERSICHT (für Moderatoren)

| Welle | Angriff | Schwerpunkt | baseSev | sUnit | kzUnit | Top-Abwehr |
|-------|---------|-------------|---------|-------|--------|------------|
| 1 | Ransomware | C+I | 8 | 20 | 3 | M6 (Awareness) L3, M3 (EDR) L3 |
| 2 | OT-Störung | A | 10 | 32 | 3 | M5 (OT-Seg) L3, M7 (Patching) L2 |
| 3 | Exfiltration | C | 7 | 20 | 3 | M1 (IAM) L3, M2 (SIEM) L3 |

---

## DRAMATURGIE (Moderator-Hinweise)

### Welle 1: "Der Klassiker"
**Ziel:** Teams verstehen Ransomware-Bedrohung, Awareness-Wert, Backup-Notwendigkeit.
**Spannung:** Moderat (viele Maßnahmen wirken)
**Lerneffekt:** Kontext-Boni zeigen (M6 L3 = -6!)

---

### Welle 2: "Das OT-Desaster"
**Ziel:** Teams erkennen OT-Spezifika, Segmentierung-Wert, Produktionskritikalität.
**Spannung:** Hoch (baseSev=10, sUnit=32 -> grosse Schaeden moeglich!)
**Lerneffekt:** Wer M5 vernachlässigt hat, zahlt jetzt drauf.

**Event danach:** OEM-Audit (KZ-Effekt je nach E-Wert Welle 1)

---

### Welle 3: "Das stille Leck"
**Ziel:** Teams verstehen APT, Supplier-Risiken, Langzeitschäden.
**Spannung:** Mittel (Schäden mittelfristig, aber KZ-Verlust spürbar)
**Lerneffekt:** Lieferanten-Sicherheit ist wichtig (M8 Kontext-Bonus!)

**Event möglich:** DSGVO-Bonus (wenn M1+M2 ≥L2)

---

## MODERATOR-CHEAT-SHEET (Rechenschritte)

**Für jede Welle:**

1. **Mitigation-Summe:**
   - Team nennt gewählte Maßnahmen + Level
   - Moderator schaut in Parametertabelle: Welche Mitigations?
   - Addieren (Kontext-Boni nicht vergessen!)
   - M_sum = min(MIT_CAP, Summe)

2. **Endschwere:**
   - G = max(0, baseSeverity - M_sum)

3. **Schaden:**
   - Damage = G × sUnit (in 1.000€)

4. **KZ-Delta:**
   - ΔKZ = -(G × kzUnit)
   - KZ_neu = clamp(KZ_alt + ΔKZ, 0, 100)

5. **CIA-Mali:**
   - ΔC = -G × ciaImpactPerStep_C
   - ΔI = -G × ciaImpactPerStep_I
   - ΔA = -G × ciaImpactPerStep_A

6. **Recovery (wenn M4 vorhanden):**
   - Damage_final = Damage × (1 - Recovery_Faktor)

---

**Diese Angriffskarten visualisieren die Bedrohungen und helfen beim Nachvollziehen! 🎯**
