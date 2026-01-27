# Mitigation-Bewertungsblatt

**Team: ________________**  |  **Budget-Tier: ☐ Low (200k€)  ☐ Medium (300k€)  ☐ High (400k€)**

| Tier | KZ-Start | Severity-Mult. | E-Ziele (W1/W2/W3) |
|------|:--------:|:--------------:|:------------------:|
| Low | 65 | ×0.7 | 15/17/19 |
| Medium | 60 | ×1.0 | 18/20/22 |
| High | 55 | ×1.3 | 21/23/25 |

---

## Teil 1: CIA-Werte der gewählten Maßnahmen

Tragen Sie das **gewählte Level (0-3)** ein und übertragen Sie die entsprechenden CIA-Werte:

| Maßnahme | Gew. Level | C | I | A | Init | OPEX |
|----------|:----------:|:-:|:-:|:-:|-----:|-----:|
| **M1** IAM/PAM | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ | ___ | ___ |
| **M2** Logging & SIEM/MDR | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ | ___ | ___ |
| **M3** EDR/XDR | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ | ___ | ___ |
| **M4** Backup & DR | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ | ___ | ___ |
| **M5** OT/IT-Segmentierung | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ | ___ | ___ |
| **M6** Security Awareness | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ | ___ | ___ |
| **M7** Vulnerability Mgmt | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ | ___ | ___ |
| **M8** Supply Chain Security | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ | ___ | ___ |
| **M9** Cloud Security (CSPM) | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ | ___ | ___ |
| **M10** Mobile Device Mgmt | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ | ___ | ___ |
| | | | | | | |
| **Summe Maßnahmen** | | ___ | ___ | ___ | ___ | ___ |
| **+ Basis-CIA** | | +10 | +10 | +10 | | |
| **= GESAMT-CIA** | | **___** | **___** | **___** | | |

**Gesamtkosten:** Init ___k€ + (OPEX ___k€ × 3 Wellen) = **___k€**

---

## Teil 2: Schadensberechnung pro Welle

### Das neue vereinfachte System

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. E-Wert berechnen:     E = C×Gew_C + I×Gew_I + A×Gew_A          │
│  2. Basis-Reduktion:      (E-Wert - Schwellenwert) ÷ 2             │
│  3. Bonus-Reduktion:      +X für bestimmte Maßnahmen ≥ Level 2     │
│  4. Gesamt-Reduktion:     min(Basis + Bonus, Cap)                  │
│  5. Severity:             Basis-Severity - Gesamt-Reduktion        │
│  6. Schaden:              Severity × Schadenseinheit               │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Welle 1: Ransomware

**E-Wert berechnen** (Gewichtung: C×0,4 + I×0,4 + A×0,2)

| CIA | Wert | × Gewicht | = Teilwert |
|-----|:----:|:---------:|:----------:|
| C (Confidentiality) | ___ | × 0,4 | = ___ |
| I (Integrity) | ___ | × 0,4 | = ___ |
| A (Availability) | ___ | × 0,2 | = ___ |
| | | **E-Wert** | **= ___** |

**E-Ziel prüfen:** E-Wert ≥ 18? → ☐ Ja (+3 KZ) ☐ Nein (-5 KZ)

**Schadensreduktion berechnen:**

| Schritt | Berechnung | Wert |
|---------|------------|:----:|
| E-Wert | (aus Tabelle oben) | ___ |
| - Schwellenwert | - 18 | |
| = Überschuss | | ___ |
| ÷ 2 | | |
| **= Basis-Reduktion** | (abgerundet) | **___** |

**Bonus-Maßnahmen prüfen:**

| Maßnahme | Bedingung | Bonus | Erfüllt? |
|----------|-----------|:-----:|:--------:|
| M3 EDR/XDR | ≥ Level 2 | +2 | ☐ Ja → +2 |
| M4 Backup & DR | ≥ Level 2 | +2 | ☐ Ja → +2 |
| M6 Awareness | ≥ Level 2 | +1 | ☐ Ja → +1 |
| **Bonus-Summe** | | | **___** |

**Schaden berechnen:**

```
Basis-Reduktion:        ___
+ Bonus-Reduktion:    + ___
= Gesamt-Reduktion:     ___
Cap (Maximum):          8
Effektive Reduktion:    ___ (min aus Gesamt und Cap)

Basis-Severity:         8
- Effektive Reduktion: -___
= Finale Severity:      ___ (min. 0)

× Schadenseinheit:    × 20k€
= SCHADEN:              ___k€

× KZ-Einheit:         × (-3)
= KZ-Delta Angriff:     ___
```

---

### Welle 2: OT-Störung

**E-Wert berechnen** (Gewichtung: C×0,2 + I×0,2 + A×0,6)

| CIA | Wert | × Gewicht | = Teilwert |
|-----|:----:|:---------:|:----------:|
| C (Confidentiality) | ___ | × 0,2 | = ___ |
| I (Integrity) | ___ | × 0,2 | = ___ |
| A (Availability) | ___ | × 0,6 | = ___ |
| | | **E-Wert** | **= ___** |

**E-Ziel prüfen:** E-Wert ≥ 20? → ☐ Ja (+5 KZ) ☐ Nein (-8 KZ)

**Schadensreduktion berechnen:**

| Schritt | Berechnung | Wert |
|---------|------------|:----:|
| E-Wert | | ___ |
| - Schwellenwert | - 20 | |
| = Überschuss | | ___ |
| ÷ 2 | | |
| **= Basis-Reduktion** | | **___** |

**Bonus-Maßnahmen prüfen:**

| Maßnahme | Bedingung | Bonus | Erfüllt? |
|----------|-----------|:-----:|:--------:|
| M5 OT/IT-Segmentierung | ≥ Level 2 | +3 | ☐ Ja → +3 |
| M7 Vulnerability Mgmt | ≥ Level 2 | +2 | ☐ Ja → +2 |
| **Bonus-Summe** | | | **___** |

**Schaden berechnen:**

```
Basis-Reduktion:        ___
+ Bonus-Reduktion:    + ___
= Gesamt-Reduktion:     ___
Cap (Maximum):          10
Effektive Reduktion:    ___

Basis-Severity:         10
- Effektive Reduktion: -___
= Finale Severity:      ___

× Schadenseinheit:    × 32k€
= SCHADEN:              ___k€

× KZ-Einheit:         × (-3)
= KZ-Delta Angriff:     ___
```

---

### Welle 3: Daten-Exfiltration

**E-Wert berechnen** (Gewichtung: C×0,5 + I×0,3 + A×0,2)

| CIA | Wert | × Gewicht | = Teilwert |
|-----|:----:|:---------:|:----------:|
| C (Confidentiality) | ___ | × 0,5 | = ___ |
| I (Integrity) | ___ | × 0,3 | = ___ |
| A (Availability) | ___ | × 0,2 | = ___ |
| | | **E-Wert** | **= ___** |

**E-Ziel prüfen:** E-Wert ≥ 22? → ☐ Ja (+8 KZ) ☐ Nein (-10 KZ)

**Schadensreduktion berechnen:**

| Schritt | Berechnung | Wert |
|---------|------------|:----:|
| E-Wert | | ___ |
| - Schwellenwert | - 22 | |
| = Überschuss | | ___ |
| ÷ 2 | | |
| **= Basis-Reduktion** | | **___** |

**Bonus-Maßnahmen prüfen:**

| Maßnahme | Bedingung | Bonus | Erfüllt? |
|----------|-----------|:-----:|:--------:|
| M1 IAM/PAM | ≥ Level 2 | +2 | ☐ Ja → +2 |
| M2 SIEM/MDR | ≥ Level 2 | +2 | ☐ Ja → +2 |
| M8 Supply Chain | ≥ Level 2 | +1 | ☐ Ja → +1 |
| **Bonus-Summe** | | | **___** |

**Schaden berechnen:**

```
Basis-Reduktion:        ___
+ Bonus-Reduktion:    + ___
= Gesamt-Reduktion:     ___
Cap (Maximum):          7
Effektive Reduktion:    ___

Basis-Severity:         7
- Effektive Reduktion: -___
= Finale Severity:      ___

× Schadenseinheit:    × 20k€
= SCHADEN:              ___k€

× KZ-Einheit:         × (-3)
= KZ-Delta Angriff:     ___
```

---

## Teil 3: Zusammenfassung

| Welle | E-Wert | E-Ziel | Basis-Red. | Bonus-Red. | Severity | Schaden | KZ (E-Ziel) | KZ (Angriff) |
|-------|:------:|:------:|:----------:|:----------:|:--------:|--------:|:-----------:|:------------:|
| 1 Ransomware | ___ | ≥18 | ___ | ___ | ___ | ___k€ | ___ | ___ |
| 2 OT-Störung | ___ | ≥20 | ___ | ___ | ___ | ___k€ | ___ | ___ |
| 3 Exfiltration | ___ | ≥22 | ___ | ___ | ___ | ___k€ | ___ | ___ |

**KZ-Verlauf:**

```
Start-KZ:                    60
+ KZ Welle 1 (E-Ziel):     ___
+ KZ Welle 1 (Angriff):    ___
+ KZ Welle 1 (Events):     ___
─────────────────────────────
= KZ nach Welle 1:         ___

+ KZ Welle 2 (E-Ziel):     ___
+ KZ Welle 2 (Angriff):    ___
+ KZ Welle 2 (Events):     ___
─────────────────────────────
= KZ nach Welle 2:         ___

+ KZ Welle 3 (E-Ziel):     ___
+ KZ Welle 3 (Angriff):    ___
+ KZ Welle 3 (Events):     ___
─────────────────────────────
= FINALER KZ-WERT:         ___
```

**Gesamtschaden:** ___k€

---

## Referenz: CIA-Werte nach Maßnahme und Level

| Maßnahme | Level 1 | Level 2 | Level 3 |
|----------|---------|---------|---------|
| M1 IAM/PAM | C+2, I+1, A+0 | C+4, I+3, A+0 | C+6, I+5, A+1 |
| M2 Logging & SIEM | C+1, I+3, A+0 | C+2, I+5, A+1 | C+3, I+7, A+2 |
| M3 EDR/XDR | C+3, I+2, A+1 | C+5, I+4, A+2 | C+7, I+6, A+3 |
| M4 Backup & DR | C+0, I+4, A+3 | C+1, I+6, A+5 | C+1, I+8, A+7 |
| M5 OT/IT-Seg. | C+2, I+1, A+4 | C+3, I+2, A+6 | C+4, I+3, A+8 |
| M6 Awareness | C+2, I+1, A+1 | C+3, I+2, A+2 | C+5, I+3, A+3 |
| M7 Vulnerability | C+2, I+3, A+2 | C+4, I+5, A+3 | C+6, I+7, A+4 |
| M8 Supply Chain | C+1, I+2, A+2 | C+2, I+4, A+4 | C+3, I+6, A+6 |
| M9 Cloud Security | C+2, I+2, A+1 | C+3, I+3, A+2 | C+4, I+4, A+3 |
| M10 MDM | C+1, I+1, A+0 | C+2, I+2, A+1 | C+3, I+3, A+2 |

---

## Bonus-Maßnahmen Übersicht

| Angriff | Bonus-Maßnahmen (jeweils ≥ Level 2) |
|---------|-------------------------------------|
| **Ransomware** | M3 EDR (+2), M4 Backup (+2), M6 Awareness (+1) |
| **OT-Störung** | M5 Segmentierung (+3), M7 Vulnerability (+2) |
| **Exfiltration** | M1 IAM (+2), M2 SIEM (+2), M8 Supply Chain (+1) |

---

*Security-Planspiel - Mitigation-Bewertungsblatt v2.0*
