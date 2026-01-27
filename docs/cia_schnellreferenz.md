# CIA & Mitigation - Schnellreferenz v2.0

## Budget-Optionen

| Tier | Budget |
|------|:------:|
| Low | 200k€ |
| Medium | 300k€ |
| High | 400k€ |

**Start-KZ für alle Teams: 60**

---

## Gesamt-CIA berechnen

```
┌─────────────────────────────────────────────────────────────┐
│  GESAMT-CIA = BASIS (10/10/10) + SUMME ALLER MAÄSSNAHMEN    │
└─────────────────────────────────────────────────────────────┘
```

---

## Neue vereinfachte Schadensberechnung

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. E-Wert berechnen:      E = C×Gew_C + I×Gew_I + A×Gew_A         │
│  2. Basis-Reduktion:       (E-Wert - Schwellenwert) ÷ 2            │
│  3. Bonus-Reduktion:       Summe der aktiven Bonus-Maßnahmen       │
│  4. Gesamt-Reduktion:      min(Basis + Bonus, Cap)                 │
│  5. Severity:              Basis-Severity - Gesamt-Reduktion       │
│  6. Schaden:               Severity × Schadenseinheit              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## E-Wert-Formeln pro Welle

| Welle | Angriff | Formel | Schwelle | E-Ziel | Cap |
|:-----:|---------|--------|:--------:|:------:|:---:|
| **1** | Ransomware | E = C×0,4 + I×0,4 + A×0,2 | 18 | ≥18 | 8 |
| **2** | OT-Störung | E = C×0,2 + I×0,2 + A×0,6 | 20 | ≥20 | 10 |
| **3** | Exfiltration | E = C×0,5 + I×0,3 + A×0,2 | 22 | ≥22 | 7 |

---

## Angriffs-Parameter

| Angriff | Basis-Severity | Cap | Schadenseinheit | KZ/Severity |
|---------|:--------------:|:---:|:---------------:|:-----------:|
| Ransomware | 8 | 8 | 20k€ | -3 |
| OT-Störung | 10 | 10 | 32k€ | -3 |
| Exfiltration | 7 | 7 | 20k€ | -3 |

---

## Bonus-Maßnahmen (ab Level 2)

### Ransomware
| Maßnahme | Bonus | Begründung |
|----------|:-----:|------------|
| M3 EDR/XDR | +2 | Erkennt Ransomware früh |
| M4 Backup & DR | +2 | Schnelle Wiederherstellung |
| M6 Awareness | +1 | Mitarbeiter erkennen Phishing |
| **Max. Bonus** | **+5** | |

### OT-Störung
| Maßnahme | Bonus | Begründung |
|----------|:-----:|------------|
| M5 OT/IT-Seg. | +3 | Isoliert Produktion |
| M7 Vulnerability | +2 | Schließt OT-Schwachstellen |
| **Max. Bonus** | **+5** | |

### Exfiltration
| Maßnahme | Bonus | Begründung |
|----------|:-----:|------------|
| M1 IAM/PAM | +2 | Verhindert unbefugten Zugriff |
| M2 SIEM/MDR | +2 | Erkennt Datenabfluss |
| M8 Supply Chain | +1 | Schützt Schnittstellen |
| **Max. Bonus** | **+5** | |

---

## CIA-Werte Übersicht (Level 2 und 3)

| Maßnahme | L2 (C/I/A) | L3 (C/I/A) | Stärke |
|----------|:----------:|:----------:|--------|
| M1 IAM/PAM | 4/3/0 | 6/5/1 | Zugriff (C) |
| M2 SIEM | 2/5/1 | 3/7/2 | Sichtbarkeit (I) |
| M3 EDR/XDR | 5/4/2 | 7/6/3 | Malware (C) |
| M4 Backup | 1/6/5 | 1/8/7 | Recovery (I+A) |
| M5 OT/IT-Seg. | 3/2/6 | 4/3/8 | Netzwerk (A) |
| M6 Awareness | 3/2/2 | 5/3/3 | Mensch (C) |
| M7 Vulnerability | 4/5/3 | 6/7/4 | Patches (I) |
| M8 Supply Chain | 2/4/4 | 3/6/6 | Extern (I+A) |
| M9 Cloud | 3/3/2 | 4/4/3 | Cloud (C+I) |
| M10 MDM | 2/2/1 | 3/3/2 | Mobile (C+I) |

---

## Rechenbeispiel

**Maßnahmen:** M3 L2, M4 L2, M5 L2, M7 L2

**CIA:**
```
Basis:     C=10  I=10  A=10
M3 L2:     C+5   I+4   A+2
M4 L2:     C+1   I+6   A+5
M5 L2:     C+3   I+2   A+6
M7 L2:     C+4   I+5   A+3
────────────────────────────
Gesamt:    C=23  I=27  A=26
```

### Welle 1: Ransomware

**E-Wert:**
```
E = 23×0,4 + 27×0,4 + 26×0,2
E = 9,2 + 10,8 + 5,2 = 25,2
E-Ziel 18 → ERREICHT ✓ (+3 KZ)
```

**Schadensreduktion:**
```
E-Überschuss: 25,2 - 18 = 7,2
Basis-Reduktion: 7,2 ÷ 2 = 3 (abgerundet)

Bonus-Maßnahmen:
  M3 L2 ≥ L2? Ja → +2
  M4 L2 ≥ L2? Ja → +2
  M6 nicht vorhanden → +0
Bonus-Summe: +4

Gesamt: 3 + 4 = 7
Cap: 8 → Effektiv: 7
```

**Schaden:**
```
Severity: 8 - 7 = 1
Schaden: 1 × 20k€ = 20k€
KZ-Delta: 1 × (-3) = -3
```

### Welle 2: OT-Störung

**E-Wert:**
```
E = 23×0,2 + 27×0,2 + 26×0,6
E = 4,6 + 5,4 + 15,6 = 25,6
E-Ziel 20 → ERREICHT ✓ (+5 KZ)
```

**Schadensreduktion:**
```
E-Überschuss: 25,6 - 20 = 5,6
Basis-Reduktion: 5,6 ÷ 2 = 2 (abgerundet)

Bonus-Maßnahmen:
  M5 L2 ≥ L2? Ja → +3
  M7 L2 ≥ L2? Ja → +2
Bonus-Summe: +5

Gesamt: 2 + 5 = 7
Cap: 10 → Effektiv: 7
```

**Schaden:**
```
Severity: 10 - 7 = 3
Schaden: 3 × 32k€ = 96k€
KZ-Delta: 3 × (-3) = -9
```

---

## Events pro Welle (Übersicht)

### Welle 1
| Event | Bedingung | Positiv | Negativ |
|-------|-----------|---------|---------|
| Phishing-Kampagne | M6 ≥ L2 | KZ +2 | KZ -3 |
| Cyber-Versicherung | E-Wert ≥ 16 | Budget +10k€ | Budget -15k€ |
| Zero-Day-Schwachstelle | M7 ≥ L1 | KZ ±0 | KZ -2 |

### Welle 2
| Event | Bedingung | Positiv | Negativ |
|-------|-----------|---------|---------|
| OEM-Audit | E-Wert ≥ 18 | KZ +5 | KZ -5 |
| Produktionsdruck | M5 ≥ L1 | KZ ±0 | OPEX +8k€ |
| Security-Experte kündigt | M2 ≥ L2 | KZ ±0 | KZ -3, OPEX +5k€ |

### Welle 3
| Event | Bedingung | Positiv | Negativ |
|-------|-----------|---------|---------|
| NIS2-Prüfung | 4+ Maßnahmen ≥ L2 | KZ +5 | KZ -8, Budget -20k€ |
| Lieferanten-Datenpanne | M8 ≥ L2 | KZ +2 | KZ -4 |
| Vorstandspräsentation | E-Wert ≥ 20 | KZ +3 | KZ -2 |

---

## KZ-Übersicht

| Ereignis | KZ-Effekt |
|----------|:---------:|
| **E-Ziel erreicht** | |
| Welle 1 | +3 |
| Welle 2 | +5 |
| Welle 3 | +8 |
| **E-Ziel verfehlt** | |
| Welle 1 | -5 |
| Welle 2 | -8 |
| Welle 3 | -10 |
| **Angriffs-Schaden** | -3 pro Severity |

---

*Security-Planspiel - Schnellreferenz v2.0*
