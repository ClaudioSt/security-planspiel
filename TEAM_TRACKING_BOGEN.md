# Team-Tracking-Bogen: Budget und Spielverlauf

**Arbeitsblatt fuer das gesamte Spiel - von der Budgetwahl bis zum Endergebnis**

---

## Teil 1: Budgetwahl verstehen

### Was bedeutet das Budget?

Das Budget ist das Geld, das Ihrem Unternehmen fuer IT-Sicherheit zur Verfuegung steht. Sie muessen damit:
- **Massnahmen kaufen** (einmalige Investition)
- **Massnahmen betreiben** (laufende Kosten pro Welle)

### Die zwei Kostenarten

| Kostenart | Was ist das? | Wann faellig? |
|-----------|--------------|---------------|
| **Init-Kosten** | Einmalige Anschaffungskosten fuer eine Massnahme (Hardware, Software, Einrichtung) | Einmal zu Spielbeginn |
| **OPEX** | Laufende Betriebskosten (Lizenzen, Personal, Wartung) | Jede Welle erneut |

**Beispiel M3 (EDR/XDR) Level 2:**
- Init-Kosten: 56k Euro (einmalig fuer Kauf und Einrichtung)
- OPEX: 10k Euro (pro Welle fuer Lizenzen und Betrieb)
- Bei 3 Wellen: Gesamtkosten = 56k + (3 x 10k) = 86k Euro

### Budget-Tiers zur Auswahl

| Tier | Verfuegbares Budget | Fuer wen geeignet? |
|:----:|:-------------------:|-------------------|
| **Low** | 300.000 Euro | Kleines Unternehmen, weniger Ressourcen |
| **Medium** | 400.000 Euro | Mittelstaendler, ausgewogene Ressourcen |
| **High** | 500.000 Euro | Groesseres Unternehmen, mehr Moeglichkeiten |

**Alle Teams starten mit einer Kundenzufriedenheit von 60 Punkten.**

---

## Teil 2: Ihr Team

| Feld | Eintrag |
|------|---------|
| **Teamname** | |
| **Gewaehlter Budget-Tier** | [ ] Low (300k) [ ] Medium (400k) [ ] High (500k) |
| **Verfuegbares Budget** | _____________ Euro |

---

## Teil 3: Massnahmenwahl zu Spielbeginn

**Tragen Sie Ihre gewaehlten Massnahmen mit Level, Init-Kosten und OPEX ein:**

| ID | Massnahme | Level | Init (k Euro) | OPEX/Welle (k Euro) |
|----|-----------|:-----:|:-------------:|:-------------------:|
| M1 | IAM/PAM | | | |
| M2 | Logging & SIEM | | | |
| M3 | EDR/XDR | | | |
| M4 | Backup & Recovery | | | |
| M5 | Netz-Segmentierung | | | |
| M6 | Security Awareness | | | |
| M7 | Patch Management | | | |
| M8 | Supplier Security | | | |
| M9 | Cloud Security | | | |
| M10 | MDM | | | |
| | **SUMME** | | **_____** | **_____** |

### Budget-Pruefung

```
Verfuegbares Budget:                    _____________ Euro

- Init-Kosten (einmalig):             - _____________ Euro
- OPEX Welle 1:                       - _____________ Euro
- OPEX Welle 2:                       - _____________ Euro
- OPEX Welle 3:                       - _____________ Euro
                                       ─────────────────────
= Verbleibendes Budget (Reserve):     = _____________ Euro
```

**Achtung:** Das Budget muss fuer Init + 3x OPEX reichen!

---

## Teil 4: CIA-Werte Ihres Teams

**Berechnen Sie Ihre Gesamt-CIA-Werte (einmal zu Beginn, gilt fuer alle Wellen):**

| CIA-Wert | Basis | + Summe Massnahmen | = Gesamt |
|----------|:-----:|:------------------:|:--------:|
| **C** (Vertraulichkeit) | 10 | + _____ | = _____ |
| **I** (Integritaet) | 10 | + _____ | = _____ |
| **A** (Verfuegbarkeit) | 10 | + _____ | = _____ |

---

## Teil 5: Tracking ueber die 3 Wellen

### Welle 1: Ransomware-Angriff

| Kennzahl | Berechnung | Wert |
|----------|------------|:----:|
| E-Wert | (C x 0,4) + (I x 0,4) + (A x 0,2) | |
| Basis-Reduktion | max(0, E-Wert - 15) | |
| Bonus-Reduktion | M3 L2+ (+2), M4 L2+ (+2), M6 L2+ (+1) | |
| Gesamt-Reduktion | min(Basis + Bonus, 8) | |
| Schwere (G) | max(0, 8 - Reduktion) | |
| Schaden | G x 20k Euro | Euro |
| Recovery (M4) | L1: 10%, L2: 30%, L3: 50% | % |
| **Endschaden** | Schaden x (1 - Recovery) | Euro |
| KZ-Verlust | G x 2 | |
| KZ-Bonus/Malus | E >= 15: +5 / E < 15: -3 | |
| **KZ-Aenderung** | -Verlust + Bonus/Malus | |

**Nach Welle 1:**
| Feld | Wert |
|------|:----:|
| Schaden Welle 1 | Euro |
| KZ nach Welle 1 | |
| Verbrauchtes Budget (kumuliert) | Euro |

---

### Welle 2: OT-Stoerung (Produktionsausfall)

| Kennzahl | Berechnung | Wert |
|----------|------------|:----:|
| E-Wert | (C x 0,2) + (I x 0,2) + (A x 0,6) | |
| Basis-Reduktion | max(0, E-Wert - 17) | |
| Bonus-Reduktion | M5 L2+ (+3), M7 L2+ (+2) | |
| Gesamt-Reduktion | min(Basis + Bonus, 10) | |
| Schwere (G) | max(0, 10 - Reduktion) | |
| Schaden | G x 32k Euro | Euro |
| Recovery (M4) | L1: 10%, L2: 30%, L3: 50% | % |
| **Endschaden** | Schaden x (1 - Recovery) | Euro |
| KZ-Verlust | G x 2 | |
| KZ-Bonus/Malus | E >= 17: +7 / E < 17: -5 | |
| **KZ-Aenderung** | -Verlust + Bonus/Malus | |

**Nach Welle 2:**
| Feld | Wert |
|------|:----:|
| Schaden Welle 2 | Euro |
| KZ nach Welle 2 | |
| Verbrauchtes Budget (kumuliert) | Euro |

---

### Welle 3: Datenexfiltration (IP-Diebstahl)

| Kennzahl | Berechnung | Wert |
|----------|------------|:----:|
| E-Wert | (C x 0,5) + (I x 0,3) + (A x 0,2) | |
| Basis-Reduktion | max(0, E-Wert - 19) | |
| Bonus-Reduktion | M1 L2+ (+2), M2 L2+ (+2), M8 L2+ (+1) | |
| Gesamt-Reduktion | min(Basis + Bonus, 7) | |
| Schwere (G) | max(0, 7 - Reduktion) | |
| Schaden | G x 20k Euro | Euro |
| Recovery | **KEINE** (Daten sind weg!) | 0% |
| **Endschaden** | = Schaden | Euro |
| KZ-Verlust | G x 2 | |
| KZ-Bonus/Malus | E >= 19: +10 / E < 19: -7 | |
| **KZ-Aenderung** | -Verlust + Bonus/Malus | |

**Nach Welle 3:**
| Feld | Wert |
|------|:----:|
| Schaden Welle 3 | Euro |
| KZ nach Welle 3 | |
| Verbrauchtes Budget (kumuliert) | Euro |

---

## Teil 6: Endergebnis

### Zusammenfassung

| Kennzahl | Wert |
|----------|:----:|
| **Gesamtschaden** (Welle 1 + 2 + 3) | Euro |
| **Finale Kundenzufriedenheit** | |
| **Gesamtkosten** (Init + 3x OPEX) | Euro |
| **Vermiedener Schaden** (620k - Gesamtschaden) | Euro |

### Return on Security Investment (ROSI)

Der ROSI zeigt, ob sich Ihre Investition gelohnt hat:

```
ROSI = (Vermiedener Schaden - Gesamtkosten) / Gesamtkosten x 100%

ROSI = (_________ - _________) / _________ x 100% = _________%
```

**Interpretation:**
- ROSI > 0%: Ihre Investition hat sich gelohnt
- ROSI < 0%: Sie haben mehr ausgegeben als gespart
- ROSI > 100%: Sie haben mehr als das Doppelte Ihrer Investition gespart

---

## Schnellreferenz: Worst-Case ohne Massnahmen

| Welle | Max. Schaden | Max. KZ-Verlust |
|:-----:|:------------:|:---------------:|
| 1 Ransomware | 160k Euro | -19 |
| 2 OT-Stoerung | 320k Euro | -25 |
| 3 Exfiltration | 140k Euro | -21 |
| **Gesamt** | **620k Euro** | **-65** |

---

## Schnellreferenz: Welche Massnahme wirkt wo?

| Massnahme | Welle 1 (Ransomware) | Welle 2 (OT) | Welle 3 (Exfil) |
|-----------|:--------------------:|:------------:|:---------------:|
| M1 IAM/PAM | CIA | CIA | **+2 Bonus** |
| M2 SIEM | CIA | CIA | **+2 Bonus** |
| M3 EDR/XDR | **+2 Bonus** | CIA | CIA |
| M4 Backup | **+2 Bonus** + Recovery | Recovery | - |
| M5 Segmentierung | CIA | **+3 Bonus** | CIA |
| M6 Awareness | **+1 Bonus** | CIA | CIA |
| M7 Patching | CIA | **+2 Bonus** | CIA |
| M8 Supplier Sec. | CIA | CIA | **+1 Bonus** |
| M9 Cloud Sec. | CIA | CIA | CIA |
| M10 MDM | CIA | CIA | CIA |

*CIA = traegt nur zu den allgemeinen CIA-Werten bei (kein Spezial-Bonus)*

---

*Team-Tracking-Bogen fuer Security-Planspiel*