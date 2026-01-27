# CIA & Mitigation - Schnellreferenz

## Gesamt-CIA berechnen

```
┌─────────────────────────────────────────────────────────────┐
│  GESAMT-CIA = BASIS (10/10/10) + SUMME ALLER MAÄSSNAHMEN    │
└─────────────────────────────────────────────────────────────┘
```

---

## E-Wert-Formeln pro Welle

| Welle | Angriff | Formel | Ziel |
|:-----:|---------|--------|:----:|
| **1** | Ransomware | E = C×0,4 + I×0,4 + A×0,2 | ≥18 |
| **2** | OT-Störung | E = C×0,2 + I×0,2 + A×0,6 | ≥20 |
| **3** | Exfiltration | E = C×0,5 + I×0,3 + A×0,2 | ≥22 |

**Erreicht → KZ-Bonus** | **Verfehlt → KZ-Malus**

---

## Schadensberechnung

```
┌────────────────────────────────────────────────────────────────┐
│  1. Mitigation summieren (alle Werte sind negativ)             │
│  2. Reduktion = Betrag der Summe (z.B. -8 → 8)                 │
│  3. Effektiv = min(Reduktion, Cap)                             │
│  4. Severity = max(0, Basis-Severity - Effektiv)               │
│  5. Schaden = Severity × Schadenseinheit                       │
└────────────────────────────────────────────────────────────────┘
```

---

## Angriffs-Parameter

| Angriff | Basis-Severity | Cap | Schadenseinheit | KZ pro Severity |
|---------|:--------------:|:---:|:---------------:|:---------------:|
| Ransomware | 8 | 10 | 20k€ | -3 |
| OT-Störung | 10 | 12 | 32k€ | -3 |
| Exfiltration | 7 | 10 | 20k€ | -3 |

---

## Top-Mitigation pro Angriff

### Ransomware (Fokus: C & I)
| Rang | Maßnahme | L3 Mitigation |
|:----:|----------|:-------------:|
| 1 | M6 Awareness | **-6** |
| 2 | M3 EDR/XDR | **-5** |
| 2 | M4 Backup | **-5** |
| 4 | M1 IAM/PAM | -3 |
| 4 | M2 SIEM | -3 |
| 4 | M7 Vulnerability | -3 |

### OT-Störung (Fokus: A)
| Rang | Maßnahme | L3 Mitigation |
|:----:|----------|:-------------:|
| 1 | M5 OT/IT-Seg. | **-7** |
| 2 | M7 Vulnerability | **-4** |
| 3 | M2 SIEM | -2 |
| 3 | M4 Backup | -2 |
| 3 | M8 Supply Chain | -2 |

### Exfiltration (Fokus: C)
| Rang | Maßnahme | L3 Mitigation |
|:----:|----------|:-------------:|
| 1 | M1 IAM/PAM | **-4** |
| 1 | M2 SIEM | **-4** |
| 3 | M3 EDR/XDR | -3 |
| 3 | M8 Supply Chain | -3 |
| 5 | M7 Vulnerability | -2 |

---

## CIA-Werte Übersicht (Level 3)

| Maßnahme | C | I | A | Stärke |
|----------|:-:|:-:|:-:|--------|
| M1 IAM/PAM | **+6** | +5 | +1 | Zugriff |
| M2 SIEM | +3 | **+7** | +2 | Sichtbarkeit |
| M3 EDR/XDR | **+7** | +6 | +3 | Malware |
| M4 Backup | +1 | **+8** | **+7** | Recovery |
| M5 OT/IT-Seg. | +4 | +3 | **+8** | Netzwerk |
| M6 Awareness | +5 | +3 | +3 | Mensch |
| M7 Vulnerability | +6 | **+7** | +4 | Patches |
| M8 Supply Chain | +3 | +6 | +6 | Extern |
| M9 Cloud | +4 | +4 | +3 | Cloud |
| M10 MDM | +3 | +3 | +2 | Mobile |

---

## Rechenbeispiel

**Maßnahmen:** M3 L3, M4 L3, M6 L2

**CIA:**
```
Basis:     C=10  I=10  A=10
M3 L3:     C+7   I+6   A+3
M4 L3:     C+1   I+8   A+7
M6 L2:     C+3   I+2   A+2
────────────────────────────
Gesamt:    C=21  I=26  A=22
```

**E-Wert Ransomware:**
```
E = 21×0,4 + 26×0,4 + 22×0,2
E = 8,4 + 10,4 + 4,4 = 23,2
Ziel 18 → ERREICHT ✓
```

**Mitigation Ransomware:**
```
M3 L3: -5
M4 L3: -5
M6 L2: -4
Summe: -14
```

**Schaden:**
```
Reduktion: 14
Cap: 10 → Effektiv: 10
Severity: 8 - 10 = 0 (min. 0)
Schaden: 0 × 20k€ = 0€ ✓
```

---

*Security-Planspiel - Schnellreferenz v1.0*
