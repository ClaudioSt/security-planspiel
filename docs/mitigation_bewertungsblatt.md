# Mitigation-Bewertungsblatt

**Team: ________________**  |  **Budget-Tier: [ ] Low (300k)  [ ] Medium (400k)  [ ] High (500k)**

| Tier | KZ-Start | Severity-Mult. | E-Ziele (W1/W2/W3) |
|------|:--------:|:--------------:|:------------------:|
| Low | 60 | x1.0 | 15/17/19 |
| Medium | 60 | x1.0 | 15/17/19 |
| High | 60 | x1.0 | 15/17/19 |

**WICHTIG:** Alle Teams beraten das GLEICHE Unternehmen - nur das Budget unterscheidet sich!

---

## Teil 1: CIA-Werte der gewaehlten Massnahmen

Tragen Sie das **gewaehlte Level (0-3)** ein und uebertragen Sie die entsprechenden CIA-Werte:

| Massnahme | Gew. Level | C | I | A | Init | OPEX |
|----------|:----------:|:-:|:-:|:-:|-----:|-----:|
| **M1** IAM/PAM | [ ] 0 [ ] 1 [ ] 2 [ ] 3 | ___ | ___ | ___ | ___ | ___ |
| **M2** Logging & SIEM/MDR | [ ] 0 [ ] 1 [ ] 2 [ ] 3 | ___ | ___ | ___ | ___ | ___ |
| **M3** EDR/XDR | [ ] 0 [ ] 1 [ ] 2 [ ] 3 | ___ | ___ | ___ | ___ | ___ |
| **M4** Backup & DR | [ ] 0 [ ] 1 [ ] 2 [ ] 3 | ___ | ___ | ___ | ___ | ___ |
| **M5** OT/IT-Segmentierung | [ ] 0 [ ] 1 [ ] 2 [ ] 3 | ___ | ___ | ___ | ___ | ___ |
| **M6** Security Awareness | [ ] 0 [ ] 1 [ ] 2 [ ] 3 | ___ | ___ | ___ | ___ | ___ |
| **M7** Vulnerability Mgmt | [ ] 0 [ ] 1 [ ] 2 [ ] 3 | ___ | ___ | ___ | ___ | ___ |
| **M8** Supply Chain Security | [ ] 0 [ ] 1 [ ] 2 [ ] 3 | ___ | ___ | ___ | ___ | ___ |
| **M9** Cloud Security (CSPM) | [ ] 0 [ ] 1 [ ] 2 [ ] 3 | ___ | ___ | ___ | ___ | ___ |
| **M10** Mobile Device Mgmt | [ ] 0 [ ] 1 [ ] 2 [ ] 3 | ___ | ___ | ___ | ___ | ___ |
| | | | | | | |
| **Summe Massnahmen** | | ___ | ___ | ___ | ___ | ___ |
| **+ Basis-CIA** | | +10 | +10 | +10 | | |
| **= GESAMT-CIA** | | **___** | **___** | **___** | | |

**Gesamtkosten:** Init ___k + (OPEX ___k x 3 Wellen) = **___k**

---

## Teil 2: Schadensberechnung pro Welle

### Das E-Value basierte System

```
1. E-Wert berechnen:     E = C x Gew_C + I x Gew_I + A x Gew_A
2. Basis-Reduktion:      (E-Wert - Schwellenwert) / 1  (e_divisor=1)
3. Bonus-Reduktion:      +X fuer bestimmte Massnahmen >= Level 2
4. Gesamt-Reduktion:     Basis + Bonus
5. Severity:             max(0, Basis-Severity - Gesamt-Reduktion)
6. Schaden:              Severity x Schadenseinheit
```

---

### Welle 1: Ransomware

**E-Wert berechnen** (Gewichtung: C x 0.4 + I x 0.4 + A x 0.2)

| CIA | Wert | x Gewicht | = Teilwert |
|-----|:----:|:---------:|:----------:|
| C (Confidentiality) | ___ | x 0.4 | = ___ |
| I (Integrity) | ___ | x 0.4 | = ___ |
| A (Availability) | ___ | x 0.2 | = ___ |
| | | **E-Wert** | **= ___** |

**E-Ziel pruefen:** E-Wert >= 15? -> [ ] Ja (+5 KZ) [ ] Nein (-3 KZ)

**Schadensreduktion berechnen:**

| Schritt | Berechnung | Wert |
|---------|------------|:----:|
| E-Wert | (aus Tabelle oben) | ___ |
| - Schwellenwert | - 15 | |
| = Ueberschuss | | ___ |
| / 1 (e_divisor) | | |
| **= Basis-Reduktion** | (abgerundet) | **___** |

**Bonus-Massnahmen pruefen:**

| Massnahme | Bedingung | Bonus | Erfuellt? |
|----------|-----------|:-----:|:--------:|
| M3 EDR/XDR | >= Level 2 | +2 | [ ] Ja -> +2 |
| M4 Backup & DR | >= Level 2 | +2 | [ ] Ja -> +2 |
| M6 Awareness | >= Level 2 | +1 | [ ] Ja -> +1 |
| **Bonus-Summe** | | | **___** |

**Schaden berechnen:**

```
Basis-Reduktion:        ___
+ Bonus-Reduktion:    + ___
= Gesamt-Reduktion:     ___

Basis-Severity:         8
- Gesamt-Reduktion:   -___
= Finale Severity:      ___ (min. 0)

x Schadenseinheit:    x 20k
= SCHADEN:              ___k

x KZ-Einheit:         x (-2)
= KZ-Delta Angriff:     ___
```

---

### Welle 2: OT-Stoerung

**E-Wert berechnen** (Gewichtung: C x 0.2 + I x 0.2 + A x 0.6)

| CIA | Wert | x Gewicht | = Teilwert |
|-----|:----:|:---------:|:----------:|
| C (Confidentiality) | ___ | x 0.2 | = ___ |
| I (Integrity) | ___ | x 0.2 | = ___ |
| A (Availability) | ___ | x 0.6 | = ___ |
| | | **E-Wert** | **= ___** |

**E-Ziel pruefen:** E-Wert >= 17? -> [ ] Ja (+7 KZ) [ ] Nein (-5 KZ)

**Schadensreduktion berechnen:**

| Schritt | Berechnung | Wert |
|---------|------------|:----:|
| E-Wert | | ___ |
| - Schwellenwert | - 17 | |
| = Ueberschuss | | ___ |
| / 1 (e_divisor) | | |
| **= Basis-Reduktion** | | **___** |

**Bonus-Massnahmen pruefen:**

| Massnahme | Bedingung | Bonus | Erfuellt? |
|----------|-----------|:-----:|:--------:|
| M5 OT/IT-Segmentierung | >= Level 2 | +3 | [ ] Ja -> +3 |
| M7 Vulnerability Mgmt | >= Level 2 | +2 | [ ] Ja -> +2 |
| **Bonus-Summe** | | | **___** |

**Schaden berechnen:**

```
Basis-Reduktion:        ___
+ Bonus-Reduktion:    + ___
= Gesamt-Reduktion:     ___

Basis-Severity:         10
- Gesamt-Reduktion:   -___
= Finale Severity:      ___ (min. 0)

x Schadenseinheit:    x 32k
= SCHADEN:              ___k

x KZ-Einheit:         x (-2)
= KZ-Delta Angriff:     ___
```

---

### Welle 3: Daten-Exfiltration

**E-Wert berechnen** (Gewichtung: C x 0.5 + I x 0.3 + A x 0.2)

| CIA | Wert | x Gewicht | = Teilwert |
|-----|:----:|:---------:|:----------:|
| C (Confidentiality) | ___ | x 0.5 | = ___ |
| I (Integrity) | ___ | x 0.3 | = ___ |
| A (Availability) | ___ | x 0.2 | = ___ |
| | | **E-Wert** | **= ___** |

**E-Ziel pruefen:** E-Wert >= 19? -> [ ] Ja (+10 KZ) [ ] Nein (-7 KZ)

**Schadensreduktion berechnen:**

| Schritt | Berechnung | Wert |
|---------|------------|:----:|
| E-Wert | | ___ |
| - Schwellenwert | - 19 | |
| = Ueberschuss | | ___ |
| / 1 (e_divisor) | | |
| **= Basis-Reduktion** | | **___** |

**Bonus-Massnahmen pruefen:**

| Massnahme | Bedingung | Bonus | Erfuellt? |
|----------|-----------|:-----:|:--------:|
| M1 IAM/PAM | >= Level 2 | +2 | [ ] Ja -> +2 |
| M2 SIEM/MDR | >= Level 2 | +2 | [ ] Ja -> +2 |
| M8 Supply Chain | >= Level 2 | +1 | [ ] Ja -> +1 |
| **Bonus-Summe** | | | **___** |

**Schaden berechnen:**

```
Basis-Reduktion:        ___
+ Bonus-Reduktion:    + ___
= Gesamt-Reduktion:     ___

Basis-Severity:         7
- Gesamt-Reduktion:   -___
= Finale Severity:      ___ (min. 0)

x Schadenseinheit:    x 20k
= SCHADEN:              ___k

x KZ-Einheit:         x (-2)
= KZ-Delta Angriff:     ___
```

---

## Teil 3: Zusammenfassung

| Welle | E-Wert | E-Ziel | Basis-Red. | Bonus-Red. | Severity | Schaden | KZ (E-Ziel) | KZ (Angriff) |
|-------|:------:|:------:|:----------:|:----------:|:--------:|--------:|:-----------:|:------------:|
| 1 Ransomware | ___ | >=15 | ___ | ___ | ___ | ___k | ___ | ___ |
| 2 OT-Stoerung | ___ | >=17 | ___ | ___ | ___ | ___k | ___ | ___ |
| 3 Exfiltration | ___ | >=19 | ___ | ___ | ___ | ___k | ___ | ___ |

**KZ-Verlauf:**

```
Start-KZ:                    60
+ KZ Welle 1 (E-Ziel):     ___
+ KZ Welle 1 (Angriff):    ___
+ KZ Welle 1 (Events):     ___
-------------------------------
= KZ nach Welle 1:         ___

+ KZ Welle 2 (E-Ziel):     ___
+ KZ Welle 2 (Angriff):    ___
+ KZ Welle 2 (Events):     ___
-------------------------------
= KZ nach Welle 2:         ___

+ KZ Welle 3 (E-Ziel):     ___
+ KZ Welle 3 (Angriff):    ___
+ KZ Welle 3 (Events):     ___
-------------------------------
= FINALER KZ-WERT:         ___
```

**Gesamtschaden:** ___k

---

## Referenz: CIA-Werte nach Massnahme und Level

| Massnahme | Level 1 | Level 2 | Level 3 |
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

## Bonus-Massnahmen Uebersicht

| Angriff | Bonus-Massnahmen (jeweils >= Level 2) |
|---------|-------------------------------------|
| **Ransomware** | M3 EDR (+2), M4 Backup (+2), M6 Awareness (+1) |
| **OT-Stoerung** | M5 Segmentierung (+3), M7 Vulnerability (+2) |
| **Exfiltration** | M1 IAM (+2), M2 SIEM (+2), M8 Supply Chain (+1) |

---

*Security-Planspiel - Mitigation-Bewertungsblatt v2.0*
