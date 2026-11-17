# Berechnungsbogen Welle 2: OT-Stoerung (Produktionsausfall)

**Handzettel zur Berechnung von Schaden und Kundenzufriedenheit**

---

## Was ist passiert?

Eine Schwachstelle in der Produktionssteuerung wurde ausgenutzt. Die Fertigungslinie steht still. Der OEM-Kunde wartet auf seine Lieferung. Jetzt muessen Sie berechnen, wie gut Ihre Sicherheitsmassnahmen Sie geschuetzt haben.

---

## Schritt 1: Ihre CIA-Werte zusammenzaehlen

Die CIA-Werte zeigen, wie gut Ihr Unternehmen geschuetzt ist:
- **C = Confidentiality** (Vertraulichkeit): Schutz vor Datendiebstahl
- **I = Integrity** (Integritaet): Schutz vor Manipulation
- **A = Availability** (Verfuegbarkeit): Schutz vor Ausfaellen

**Jedes Unternehmen startet mit diesen Basiswerten:**
| C (Vertraulichkeit) | I (Integritaet) | A (Verfuegbarkeit) |
|:---:|:---:|:---:|
| 10 | 10 | 10 |

**Tragen Sie Ihre gewaehlten Massnahmen ein und addieren Sie die CIA-Werte:**

| Massnahme | Level | C-Wert | I-Wert | A-Wert |
|-----------|:-----:|:------:|:------:|:------:|
| M1 - IAM/PAM | ___ | ___ | ___ | ___ |
| M2 - Logging & SIEM | ___ | ___ | ___ | ___ |
| M3 - EDR/XDR | ___ | ___ | ___ | ___ |
| M4 - Backup & Recovery | ___ | ___ | ___ | ___ |
| M5 - Netz-Segmentierung | ___ | ___ | ___ | ___ |
| M6 - Security Awareness | ___ | ___ | ___ | ___ |
| M7 - Patch Management | ___ | ___ | ___ | ___ |
| M8 - Supplier Security | ___ | ___ | ___ | ___ |
| M9 - Cloud Security | ___ | ___ | ___ | ___ |
| M10 - MDM | ___ | ___ | ___ | ___ |
| **Summe der Massnahmen** | | **___** | **___** | **___** |

**Ihre Gesamt-CIA-Werte (Basis + Massnahmen):**

```
C-Gesamt = 10 + _____ = _____

I-Gesamt = 10 + _____ = _____

A-Gesamt = 10 + _____ = _____
```

---

## Schritt 2: Den E-Wert (Effektivitaetswert) berechnen

Der E-Wert zeigt, wie wirksam Ihr Schutz gegen diesen speziellen Angriff ist.

**Fuer OT-Stoerungen sind die CIA-Werte unterschiedlich wichtig:**
- Vertraulichkeit (C) zaehlt zu **20%** - weniger relevant
- Integritaet (I) zaehlt zu **20%** - Steuerung wird manipuliert
- Verfuegbarkeit (A) zaehlt zu **60%** - Produktion steht still!

**WICHTIG: Bei OT-Angriffen ist Verfuegbarkeit (A) am wichtigsten!**

**Die Formel:**
```
E-Wert = (C-Gesamt x 0,2) + (I-Gesamt x 0,2) + (A-Gesamt x 0,6)
```

**Ihre Berechnung:**
```
E-Wert = (_____ x 0,2) + (_____ x 0,2) + (_____ x 0,6)

E-Wert = _____ + _____ + _____

E-Wert = _____
```

---

## Schritt 3: Die Basis-Reduktion berechnen

Die Basis-Reduktion zeigt, wie viel Schaden Sie durch Ihren E-Wert verhindern.

**Die Schwelle fuer OT-Stoerung liegt bei 17.**
Nur wenn Ihr E-Wert ueber 17 liegt, reduzieren Sie den Schaden.

**Die Formel:**
```
Basis-Reduktion = E-Wert - 17

(Wenn das Ergebnis negativ ist, ist die Reduktion = 0)
```

**Ihre Berechnung:**
```
Basis-Reduktion = _____ - 17 = _____

Wenn negativ, dann: Basis-Reduktion = 0
```

---

## Schritt 4: Die Bonus-Reduktion berechnen

Bestimmte Massnahmen sind besonders wirksam gegen OT-Angriffe und geben Extra-Schutz.

**Pruefen Sie, welche Bonus-Massnahmen Sie auf Level 2 oder hoeher haben:**

| Massnahme | Ihr Level | Bonus (bei L2+) |
|-----------|:---------:|:---------------:|
| M5 - Netz-Segmentierung (isoliert Produktion) | ___ | +3 wenn L2+ |
| M7 - Patch Management (schliesst OT-Luecken) | ___ | +2 wenn L2+ |

**Ihre Berechnung:**
```
Bonus-Reduktion = ___ + ___ = _____
```

---

## Schritt 5: Die Gesamt-Reduktion berechnen

Jetzt addieren Sie Basis-Reduktion und Bonus-Reduktion.

**Wichtig:** Die maximale Reduktion ist auf 10 begrenzt (Mitigation-Cap).

**Die Formel:**
```
Gesamt-Reduktion = Basis-Reduktion + Bonus-Reduktion

Falls groesser als 10: Gesamt-Reduktion = 10
```

**Ihre Berechnung:**
```
Gesamt-Reduktion = _____ + _____ = _____

Ist das mehr als 10? Dann: Gesamt-Reduktion = 10
```

---

## Schritt 6: Die effektive Schwere (G) berechnen

Die Schwere zeigt, wie stark der Angriff Sie trifft.

**Der OT-Angriff hat eine Basis-Schwere von 10 - der hoechste Wert im Spiel!**

**Die Formel:**
```
Schwere (G) = 10 - Gesamt-Reduktion

(Wenn das Ergebnis negativ ist, ist G = 0)
```

**Ihre Berechnung:**
```
Schwere (G) = 10 - _____ = _____

Wenn negativ, dann: G = 0
```

---

## Schritt 7: Den finanziellen Schaden berechnen

**Produktionsausfall ist teuer!** Jeder Schwere-Punkt kostet Sie 32.000 Euro.

**Die Formel:**
```
Schaden = Schwere (G) x 32.000 Euro
```

**Ihre Berechnung:**
```
Schaden = _____ x 32.000 Euro = __________ Euro
```

---

## Schritt 8: Recovery durch Backup anwenden (falls vorhanden)

**Nur wenn Sie M4 (Backup) haben, koennen Sie einen Teil des Schadens wiederherstellen!**

| Backup-Level | Recovery-Rate | Sie zahlen nur... |
|:------------:|:-------------:|:-----------------:|
| L0 (kein Backup) | 0% | 100% des Schadens |
| L1 | 10% | 90% des Schadens |
| L2 | 30% | 70% des Schadens |
| L3 | 50% | 50% des Schadens |

**Ihr Backup-Level:** ___

**Ihre Berechnung:**
```
Falls L0: Endschaden = Schaden = __________ Euro

Falls L1: Endschaden = Schaden x 0,90 = __________ Euro

Falls L2: Endschaden = Schaden x 0,70 = __________ Euro

Falls L3: Endschaden = Schaden x 0,50 = __________ Euro
```

**Ihr Endschaden:** __________ Euro

---

## Schritt 9: Die Kundenzufriedenheit berechnen

Die Kundenzufriedenheit sinkt durch den Angriff - aber gute Vorbereitung wird belohnt!

### Teil A: Verlust durch Schwere

Jeder Schwere-Punkt kostet 2 KZ-Punkte.

```
KZ-Verlust durch Schwere = Schwere (G) x 2 = _____ x 2 = _____
```

### Teil B: Bonus oder Malus

War Ihr E-Wert gut genug?

```
Ihr E-Wert: _____     Schwelle: 17

[ ] E-Wert >= 17? --> Sie erhalten: KZ-Bonus = +7
[ ] E-Wert < 17?  --> Sie erhalten: KZ-Malus = -5
```

### Teil C: Gesamte KZ-Aenderung

```
KZ-Aenderung = -(KZ-Verlust) + (Bonus oder Malus)

KZ-Aenderung = -_____ + _____ = _____
```

### Teil D: Neue Kundenzufriedenheit

```
Alte KZ: _____

Neue KZ = Alte KZ + KZ-Aenderung = _____ + _____ = _____
```

**Ihre neue Kundenzufriedenheit:** _____

---

## Zusammenfassung Ihrer Ergebnisse

| Kennzahl | Ihr Wert |
|----------|:--------:|
| E-Wert | |
| Schwere (G) | |
| Finanzieller Schaden (vor Recovery) | Euro |
| Finanzieller Endschaden | Euro |
| KZ-Aenderung | |
| Neue Kundenzufriedenheit | |

---

## Lernziele dieser Welle

- **Netz-Segmentierung (M5)** ist KRITISCH - sie isoliert die Produktion vom Buero-Netz
- **Patch Management (M7)** schliesst Sicherheitsluecken in Industriesteuerungen
- Der **A-Wert (Verfuegbarkeit)** zaehlt hier am meisten (60% Gewicht!)
- Ohne Vorbereitung drohen bis zu **320.000 Euro Schaden** und **-25 KZ-Punkte**
- Das ist der teuerste Angriff im Spiel!

---

*Berechnungsbogen fuer Security-Planspiel - Welle 2 OT-Stoerung*