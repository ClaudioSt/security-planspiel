# Berechnungsbogen Welle 3: Datenexfiltration (IP-Diebstahl)

**Handzettel zur Berechnung von Schaden und Kundenzufriedenheit**

---

## Was ist passiert?

Ueber einen kompromittierten Lieferanten-Zugang wurden ueber Wochen hinweg geheime Konstruktionsdaten gestohlen. Das BSI informiert Sie: Ihre Daten werden im Darknet angeboten. Jetzt muessen Sie berechnen, wie gut Ihre Sicherheitsmassnahmen Sie geschuetzt haben.

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

**Fuer Datenexfiltration sind die CIA-Werte unterschiedlich wichtig:**
- Vertraulichkeit (C) zaehlt zu **50%** - geheime Daten wurden gestohlen!
- Integritaet (I) zaehlt zu **30%** - Daten wurden kopiert
- Verfuegbarkeit (A) zaehlt zu **20%** - Systeme laufen weiter

**WICHTIG: Bei Exfiltration ist Vertraulichkeit (C) am wichtigsten!**

**Die Formel:**
```
E-Wert = (C-Gesamt x 0,5) + (I-Gesamt x 0,3) + (A-Gesamt x 0,2)
```

**Ihre Berechnung:**
```
E-Wert = (_____ x 0,5) + (_____ x 0,3) + (_____ x 0,2)

E-Wert = _____ + _____ + _____

E-Wert = _____
```

---

## Schritt 3: Die Basis-Reduktion berechnen

Die Basis-Reduktion zeigt, wie viel Schaden Sie durch Ihren E-Wert verhindern.

**Die Schwelle fuer Exfiltration liegt bei 19 - die hoechste im Spiel!**
Nur wenn Ihr E-Wert ueber 19 liegt, reduzieren Sie den Schaden.

**Die Formel:**
```
Basis-Reduktion = E-Wert - 19

(Wenn das Ergebnis negativ ist, ist die Reduktion = 0)
```

**Ihre Berechnung:**
```
Basis-Reduktion = _____ - 19 = _____

Wenn negativ, dann: Basis-Reduktion = 0
```

---

## Schritt 4: Die Bonus-Reduktion berechnen

Bestimmte Massnahmen sind besonders wirksam gegen Datendiebstahl und geben Extra-Schutz.

**Pruefen Sie, welche Bonus-Massnahmen Sie auf Level 2 oder hoeher haben:**

| Massnahme | Ihr Level | Bonus (bei L2+) |
|-----------|:---------:|:---------------:|
| M1 - IAM/PAM (kontrolliert Zugriffsrechte) | ___ | +2 wenn L2+ |
| M2 - SIEM (erkennt ungewoehnlichen Datenabfluss) | ___ | +2 wenn L2+ |
| M8 - Supplier Security (sichert Lieferanten-Zugaenge) | ___ | +1 wenn L2+ |

**Ihre Berechnung:**
```
Bonus-Reduktion = ___ + ___ + ___ = _____
```

---

## Schritt 5: Die Gesamt-Reduktion berechnen

Jetzt addieren Sie Basis-Reduktion und Bonus-Reduktion.

**Wichtig:** Die maximale Reduktion ist auf 7 begrenzt (Mitigation-Cap).

**Die Formel:**
```
Gesamt-Reduktion = Basis-Reduktion + Bonus-Reduktion

Falls groesser als 7: Gesamt-Reduktion = 7
```

**Ihre Berechnung:**
```
Gesamt-Reduktion = _____ + _____ = _____

Ist das mehr als 7? Dann: Gesamt-Reduktion = 7
```

---

## Schritt 6: Die effektive Schwere (G) berechnen

Die Schwere zeigt, wie stark der Angriff Sie trifft.

**Der Exfiltrations-Angriff hat eine Basis-Schwere von 7.**

**Die Formel:**
```
Schwere (G) = 7 - Gesamt-Reduktion

(Wenn das Ergebnis negativ ist, ist G = 0)
```

**Ihre Berechnung:**
```
Schwere (G) = 7 - _____ = _____

Wenn negativ, dann: G = 0
```

---

## Schritt 7: Den finanziellen Schaden berechnen

Jeder Schwere-Punkt kostet Sie 20.000 Euro.

**Die Formel:**
```
Schaden = Schwere (G) x 20.000 Euro
```

**Ihre Berechnung:**
```
Schaden = _____ x 20.000 Euro = __________ Euro
```

---

## Schritt 8: Recovery - NICHT MOEGLICH!

**ACHTUNG: Bei Datenexfiltration gibt es KEINE Recovery!**

Gestohlene Daten sind draussen - sie koennen nicht "zurueckgeholt" werden.
Backups helfen hier nicht!

```
Endschaden = Schaden = __________ Euro
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
Ihr E-Wert: _____     Schwelle: 19

[ ] E-Wert >= 19? --> Sie erhalten: KZ-Bonus = +10
[ ] E-Wert < 19?  --> Sie erhalten: KZ-Malus = -7
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
| Finanzieller Schaden | Euro |
| KZ-Aenderung | |
| Neue Kundenzufriedenheit | |

---

## Lernziele dieser Welle

- **IAM/PAM (M1)** haette den Lieferanten-Zugang besser abgesichert
- **SIEM (M2)** haette den Datenabfluss erkannt
- **Supplier Security (M8)** ist kein "Nice-to-have" - Lieferanten sind ein Risiko!
- Der **C-Wert (Vertraulichkeit)** zaehlt hier am meisten (50% Gewicht!)
- **Keine Recovery moeglich** - gestohlene Daten sind weg!
- Ohne Vorbereitung drohen bis zu **140.000 Euro Schaden** und **-21 KZ-Punkte**

---

*Berechnungsbogen fuer Security-Planspiel - Welle 3 Exfiltration*