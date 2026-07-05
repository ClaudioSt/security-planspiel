# CIA & Mitigation - Schnellreferenz v2.0

## Budget-Optionen (gleiches Unternehmen)

| Tier | Budget | KZ-Start | Severity | E-Ziele (W1/W2/W3) |
|------|:------:|:--------:|:--------:|:------------------:|
| Low | 300k | 60 | x1.0 | 15/17/19 |
| Medium | 400k | 60 | x1.0 | 15/17/19 |
| High | 500k | 60 | x1.0 | 15/17/19 |

**Hinweis:** Alle Teams beraten das GLEICHE Unternehmen - nur das Budget unterscheidet sich!

---

## Gesamt-CIA berechnen

```
GESAMT-CIA = BASIS (10/10/10) + SUMME ALLER MASSNAHMEN
```

---

## E-Value basierte Schadensberechnung

```
1. E-Wert berechnen:      E = C x Gew_C + I x Gew_I + A x Gew_A
2. Basis-Reduktion:       (E-Wert - Schwellenwert) / e_divisor  [e_divisor=1]
3. Bonus-Reduktion:       Summe der aktiven Bonus-Massnahmen (L2+)
4. Gesamt-Severity:       max(0, Basis-Severity - Reduktionen)
5. Schaden:               Severity x Schadenseinheit
```

---

## E-Wert-Formeln pro Welle

| Welle | Angriff | Formel | Schwelle | Cap | Bonus/Malus |
|:-----:|---------|--------|:--------:|:---:|:-----------:|
| **1** | Ransomware | E = C x 0.4 + I x 0.4 + A x 0.2 | 15 | 8 | +5 / -3 |
| **2** | OT-Stoerung | E = C x 0.2 + I x 0.2 + A x 0.6 | 17 | 10 | +7 / -5 |
| **3** | Exfiltration | E = C x 0.5 + I x 0.3 + A x 0.2 | 19 | 7 | +10 / -7 |

---

## Angriffs-Parameter

| Angriff | Basis-Severity | Cap | Schadenseinheit | KZ/Severity |
|---------|:--------------:|:---:|:---------------:|:-----------:|
| Ransomware | 8 | 8 | 20k | -2 |
| OT-Stoerung | 10 | 10 | 32k | -2 |
| Exfiltration | 7 | 7 | 20k | -2 |

---

## Bonus-Massnahmen (ab Level 2)

### Ransomware
| Massnahme | Bonus | Begruendung |
|----------|:-----:|------------|
| M3 EDR/XDR | +2 | Erkennt Ransomware frueh |
| M4 Backup & DR | +2 | Schnelle Wiederherstellung |
| M6 Awareness | +1 | Mitarbeiter erkennen Phishing |
| **Max. Bonus** | **+5** | |

### OT-Stoerung
| Massnahme | Bonus | Begruendung |
|----------|:-----:|------------|
| M5 OT/IT-Seg. | +3 | Isoliert Produktion |
| M7 Vulnerability | +2 | Schliesst OT-Schwachstellen |
| **Max. Bonus** | **+5** | |

### Exfiltration
| Massnahme | Bonus | Begruendung |
|----------|:-----:|------------|
| M1 IAM/PAM | +2 | Verhindert unbefugten Zugriff |
| M2 SIEM/MDR | +2 | Erkennt Datenabfluss |
| M8 Supply Chain | +1 | Schuetzt Schnittstellen |
| **Max. Bonus** | **+5** | |

---

## CIA-Werte Uebersicht (Level 2 und 3)

| Massnahme | L2 (C/I/A) | L3 (C/I/A) | Staerke |
|----------|:----------:|:----------:|--------|
| M1 IAM/PAM | 4/3/0 | 6/5/1 | Zugriff (C) |
| M2 SIEM | 2/5/1 | 3/7/2 | Sichtbarkeit (I) |
| M3 EDR/XDR | 5/4/2 | 7/6/3 | Malware (C) |
| M4 Backup | 1/6/5 | 1/8/7 | Recovery (I+A) |
| M5 OT/IT-Seg. | 3/2/6 | 4/3/8 | Netzwerk (A) |
| M6 Awareness | 3/2/2 | 5/3/3 | Mensch (C) |
| M7 Vulnerability | 4/5/3 | 6/7/4 | Patches (I) |
| M8 Supply Chain | 2/4/4 | 3/6/6 | Extern (I+A) |
| M9 Cloud | 3/3/2 | 4/4/3 | Cloud (C+I) - TRAP |
| M10 MDM | 2/2/1 | 3/3/2 | Mobile (C+I) - TRAP |

---

## Rechenbeispiel

**Massnahmen:** M3 L2, M4 L2, M5 L2, M7 L2

**CIA:**
```
Basis:     C=10  I=10  A=10
M3 L2:     C+5   I+4   A+2
M4 L2:     C+1   I+6   A+5
M5 L2:     C+3   I+2   A+6
M7 L2:     C+4   I+5   A+3
-----------------------------
Gesamt:    C=23  I=27  A=26
```

### Welle 1: Ransomware

**E-Wert:**
```
E = 23 x 0.4 + 27 x 0.4 + 26 x 0.2
E = 9.2 + 10.8 + 5.2 = 25.2
E-Ziel 15 -> ERREICHT (+5 KZ)
```

**Schadensreduktion:**
```
E-Ueberschuss: 25.2 - 15 = 10.2
Basis-Reduktion: 10.2 / 1 = 10 (abgerundet)

Bonus-Massnahmen:
  M3 L2 >= L2? Ja -> +2
  M4 L2 >= L2? Ja -> +2
  M6 nicht vorhanden -> +0
Bonus-Summe: +4

Gesamt-Reduktion: 10 + 4 = 14
Basis-Severity: 8
Final-Severity: max(0, 8 - 14) = 0
```

**Schaden:**
```
Severity: 0
Schaden: 0 x 20k = 0k
KZ-Delta: 0 x (-2) = 0
```

---

## Events pro Welle (Uebersicht)

### Welle 1
| Event | Bedingung | Positiv | Negativ |
|-------|-----------|---------|---------|
| Phishing-Kampagne | M6 >= L2 | KZ +2 | KZ -3 |
| Cyber-Versicherung | E-Wert >= 16 | Budget +10k | Budget -15k |
| Zero-Day-Schwachstelle | M7 >= L1 | KZ +/-0 | KZ -2 |

### Welle 2
| Event | Bedingung | Positiv | Negativ |
|-------|-----------|---------|---------|
| OEM-Audit | E-Wert >= 18 | KZ +5 | KZ -5 |
| Produktionsdruck | M5 >= L1 | KZ +/-0 | OPEX +8k |
| Security-Experte kuendigt | M2 >= L2 | KZ +/-0 | KZ -3, OPEX +5k |

### Welle 3
| Event | Bedingung | Positiv | Negativ |
|-------|-----------|---------|---------|
| NIS2-Pruefung | 4+ Massnahmen >= L2 | KZ +5 | KZ -5, Budget -15k |
| Lieferanten-Datenpanne | M8 >= L2 | KZ +3 | KZ -3 |
| Vorstandspraesentation | E-Wert >= 20 | KZ +3 | KZ -2 |

---

## KZ-Uebersicht

| Ereignis | KZ-Effekt |
|----------|:---------:|
| **E-Ziel erreicht** | |
| Welle 1 | +5 |
| Welle 2 | +7 |
| Welle 3 | +10 |
| **E-Ziel verfehlt** | |
| Welle 1 | -3 |
| Welle 2 | -5 |
| Welle 3 | -7 |
| **Angriffs-Schaden** | -2 pro Severity |

---

*Security-Planspiel - Schnellreferenz v2.0*
