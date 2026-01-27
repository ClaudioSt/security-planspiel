# Mitigation-Bewertungsblatt

**Team: ________________**  |  **Budget-Tier: ☐ Low  ☐ Medium  ☐ High**

---

## Teil 1: CIA-Werte der gewählten Maßnahmen

Tragen Sie das **gewählte Level (0-3)** ein und übertragen Sie die entsprechenden CIA-Werte:

| Maßnahme | Gew. Level | C | I | A |
|----------|:----------:|:-:|:-:|:-:|
| **M1** IAM/PAM | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ |
| **M2** Logging & SIEM/MDR | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ |
| **M3** EDR/XDR | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ |
| **M4** Backup & DR | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ |
| **M5** OT/IT-Segmentierung | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ |
| **M6** Security Awareness | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ |
| **M7** Vulnerability Mgmt | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ |
| **M8** Supply Chain Security | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ |
| **M9** Cloud Security (CSPM) | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ |
| **M10** Mobile Device Mgmt | ☐ 0 ☐ 1 ☐ 2 ☐ 3 | ___ | ___ | ___ |
| | | | | |
| **Summe Maßnahmen** | | ___ | ___ | ___ |
| **+ Basis-CIA** | | +10 | +10 | +10 |
| **= GESAMT-CIA** | | **___** | **___** | **___** |

---

## Teil 2: E-Wert-Berechnung pro Angriffswelle

### Welle 1: Ransomware
| CIA | Wert | × Gewicht | = Teilwert |
|-----|:----:|:---------:|:----------:|
| C (Confidentiality) | ___ | × 0,4 | = ___ |
| I (Integrity) | ___ | × 0,4 | = ___ |
| A (Availability) | ___ | × 0,2 | = ___ |
| | | **E-Wert** | **= ___** |
| | | **E-Ziel** | **≥ 18** |
| | | **Erreicht?** | ☐ Ja (+3 KZ) ☐ Nein (-5 KZ) |

### Welle 2: OT-Störung
| CIA | Wert | × Gewicht | = Teilwert |
|-----|:----:|:---------:|:----------:|
| C (Confidentiality) | ___ | × 0,2 | = ___ |
| I (Integrity) | ___ | × 0,2 | = ___ |
| A (Availability) | ___ | × 0,6 | = ___ |
| | | **E-Wert** | **= ___** |
| | | **E-Ziel** | **≥ 20** |
| | | **Erreicht?** | ☐ Ja (+5 KZ) ☐ Nein (-8 KZ) |

### Welle 3: Daten-Exfiltration
| CIA | Wert | × Gewicht | = Teilwert |
|-----|:----:|:---------:|:----------:|
| C (Confidentiality) | ___ | × 0,5 | = ___ |
| I (Integrity) | ___ | × 0,3 | = ___ |
| A (Availability) | ___ | × 0,2 | = ___ |
| | | **E-Wert** | **= ___** |
| | | **E-Ziel** | **≥ 22** |
| | | **Erreicht?** | ☐ Ja (+8 KZ) ☐ Nein (-10 KZ) |

---

## Teil 3: Mitigation durch spezifische Maßnahmen

Tragen Sie die Mitigation-Werte Ihrer gewählten Maßnahmen-Level ein:

### Ransomware-Mitigation
| Maßnahme | L0 | L1 | L2 | L3 | Ihr Wert |
|----------|:--:|:--:|:--:|:--:|:--------:|
| M1 IAM/PAM | 0 | -1 | -2 | -3 | ___ |
| M2 Logging & SIEM | 0 | -1 | -2 | -3 | ___ |
| M3 EDR/XDR | 0 | -2 | -3 | **-5** | ___ |
| M4 Backup & DR | 0 | -1 | -2 | **-5** | ___ |
| M5 OT/IT-Seg. | 0 | 0 | -1 | -2 | ___ |
| M6 Awareness | 0 | -1 | **-4** | **-6** | ___ |
| M7 Vulnerability | 0 | -1 | -2 | -3 | ___ |
| M8 Supply Chain | 0 | 0 | 0 | 0 | ___ |
| M9 Cloud Security | 0 | 0 | 0 | 0 | ___ |
| M10 MDM | 0 | 0 | -1 | -1 | ___ |
| **Summe** | | | | | **___** |

### OT-Störung-Mitigation
| Maßnahme | L0 | L1 | L2 | L3 | Ihr Wert |
|----------|:--:|:--:|:--:|:--:|:--------:|
| M1 IAM/PAM | 0 | 0 | 0 | 0 | ___ |
| M2 Logging & SIEM | 0 | 0 | -1 | -2 | ___ |
| M3 EDR/XDR | 0 | 0 | 0 | 0 | ___ |
| M4 Backup & DR | 0 | 0 | -1 | -2 | ___ |
| M5 OT/IT-Seg. | 0 | -1 | **-5** | **-7** | ___ |
| M6 Awareness | 0 | 0 | 0 | 0 | ___ |
| M7 Vulnerability | 0 | -1 | -3 | **-4** | ___ |
| M8 Supply Chain | 0 | 0 | -1 | -2 | ___ |
| M9 Cloud Security | 0 | 0 | 0 | 0 | ___ |
| M10 MDM | 0 | 0 | 0 | 0 | ___ |
| **Summe** | | | | | **___** |

### Exfiltration-Mitigation
| Maßnahme | L0 | L1 | L2 | L3 | Ihr Wert |
|----------|:--:|:--:|:--:|:--:|:--------:|
| M1 IAM/PAM | 0 | -1 | -2 | **-4** | ___ |
| M2 Logging & SIEM | 0 | -1 | -2 | **-4** | ___ |
| M3 EDR/XDR | 0 | -1 | -2 | -3 | ___ |
| M4 Backup & DR | 0 | 0 | 0 | 0 | ___ |
| M5 OT/IT-Seg. | 0 | 0 | 0 | 0 | ___ |
| M6 Awareness | 0 | 0 | 0 | 0 | ___ |
| M7 Vulnerability | 0 | 0 | -1 | -2 | ___ |
| M8 Supply Chain | 0 | 0 | -1 | -3 | ___ |
| M9 Cloud Security | 0 | 0 | 0 | -1 | ___ |
| M10 MDM | 0 | 0 | 0 | 0 | ___ |
| **Summe** | | | | | **___** |

---

## Teil 4: Endwert-Berechnung (Schadensreduktion)

### Welle 1: Ransomware
```
Mitigation-Summe:           ___ (aus Teil 3)
Reduktion = |Summe|:        ___ (Vorzeichen umkehren)
Mitigation-Cap:             10 (Maximum)
Effektive Reduktion:        ___ (min aus Reduktion und Cap)

Basis-Severity:             8
- Effektive Reduktion:    - ___
─────────────────────────────────
= Finale Severity:          ___ (min. 0)

× Schadenseinheit:        × 20k€
─────────────────────────────────
= SCHADEN:                  ___k€

× KZ-Einheit:             × (-3)
─────────────────────────────────
= KZ-DELTA:                 ___
```

### Welle 2: OT-Störung
```
Mitigation-Summe:           ___ (aus Teil 3)
Reduktion = |Summe|:        ___
Mitigation-Cap:             12 (Maximum)
Effektive Reduktion:        ___

Basis-Severity:             10
- Effektive Reduktion:    - ___
─────────────────────────────────
= Finale Severity:          ___

× Schadenseinheit:        × 32k€
─────────────────────────────────
= SCHADEN:                  ___k€

× KZ-Einheit:             × (-3)
─────────────────────────────────
= KZ-DELTA:                 ___
```

### Welle 3: Exfiltration
```
Mitigation-Summe:           ___ (aus Teil 3)
Reduktion = |Summe|:        ___
Mitigation-Cap:             10 (Maximum)
Effektive Reduktion:        ___

Basis-Severity:             7
- Effektive Reduktion:    - ___
─────────────────────────────────
= Finale Severity:          ___

× Schadenseinheit:        × 20k€
─────────────────────────────────
= SCHADEN:                  ___k€

× KZ-Einheit:             × (-3)
─────────────────────────────────
= KZ-DELTA:                 ___
```

---

## Teil 5: Zusammenfassung

| Welle | E-Wert | Ziel erreicht? | Mitigation | Severity | Schaden | KZ aus E-Ziel | KZ aus Angriff |
|-------|:------:|:--------------:|:----------:|:--------:|--------:|:-------------:|:--------------:|
| 1 Ransomware | ___ | ☐ Ja ☐ Nein | ___ | ___ | ___k€ | ___ | ___ |
| 2 OT-Störung | ___ | ☐ Ja ☐ Nein | ___ | ___ | ___k€ | ___ | ___ |
| 3 Exfiltration | ___ | ☐ Ja ☐ Nein | ___ | ___ | ___k€ | ___ | ___ |
| **GESAMT** | | | | | **___k€** | **___** | **___** |

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

## Schnellübersicht: Welche Maßnahmen helfen gegen welchen Angriff?

| Angriff | Beste Maßnahmen | Unwirksame Maßnahmen |
|---------|-----------------|----------------------|
| **Ransomware** | M6 (L3: -6), M3 (L3: -5), M4 (L3: -5) | M5, M8, M9 |
| **OT-Störung** | M5 (L3: -7), M7 (L3: -4), M4 (L3: -2) | M1, M3, M6, M9, M10 |
| **Exfiltration** | M1 (L3: -4), M2 (L3: -4), M3 (L3: -3), M8 (L3: -3) | M4, M5, M6, M10 |

---

*Security-Planspiel - Mitigation-Bewertungsblatt v1.0*
