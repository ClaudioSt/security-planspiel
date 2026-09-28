# Endauswertung: RoS und Finaler Vergleichswert

**Berechnungsanleitung nach Abschluss aller 3 Angriffswellen**

---

## Teil 1: Daten sammeln

Tragen Sie folgende Werte aus dem Team-Tracking-Bogen ein:

| Kennzahl | Wert | Quelle |
|----------|:----:|--------|
| **Init-Kosten** | _______ k Euro | Teil 3 (Summe Init) |
| **OPEX pro Welle** | _______ k Euro | Teil 3 (Summe OPEX) |
| **Endschaden Welle 1** | _______ k Euro | Teil 5 |
| **Endschaden Welle 2** | _______ k Euro | Teil 5 |
| **Endschaden Welle 3** | _______ k Euro | Teil 5 |
| **Event-Strafen** | _______ k Euro | Falls Events gespielt wurden |
| **Finale Kundenzufriedenheit** | _______ | Nach Welle 3 (0-100) |

---

## Teil 2: Return on Security (RoS) berechnen

Der RoS zeigt, ob sich Ihre Security-Investition finanziell gelohnt hat.

### Schritt 1: Gesamtkosten ermitteln

```
Gesamtkosten = Init-Kosten + (OPEX x 3 Wellen) + Event-Strafen

Gesamtkosten = _______ + (_______ x 3) + _______

Gesamtkosten = _______ k Euro
```

### Schritt 2: Gesamtschaden berechnen

```
Gesamtschaden = Endschaden W1 + Endschaden W2 + Endschaden W3

Gesamtschaden = _______ + _______ + _______

Gesamtschaden = _______ k Euro
```

### Schritt 3: Vermiedenen Schaden berechnen

Der maximale Schaden ohne jegliche Massnahmen betraegt **620k Euro** (Worst-Case).

```
Vermiedener Schaden = 620k - Gesamtschaden

Vermiedener Schaden = 620 - _______

Vermiedener Schaden = _______ k Euro
```

### Schritt 4: RoS berechnen

```
RoS = (Vermiedener Schaden - Gesamtkosten) / Gesamtkosten

RoS = (_______ - _______) / _______

RoS = _______  (als Dezimalzahl, z.B. 0.5)

RoS in Prozent = _______ x 100 = _______ %
```

### RoS-Interpretation

| RoS-Wert | Bedeutung |
|----------|-----------|
| **RoS > 1.0 (100%)** | Exzellent! Fuer jeden investierten Euro wurden mehr als 2 Euro Schaden vermieden |
| **RoS = 0.5-1.0 (50-100%)** | Gut! Die Investition hat sich deutlich gelohnt |
| **RoS = 0-0.5 (0-50%)** | Solide! Die Investition hat sich gelohnt |
| **RoS = 0 (0%)** | Break-even: Kosten = Vermiedener Schaden |
| **RoS < 0 (negativ)** | Verlust: Mehr investiert als Schaden vermieden |

---

## Teil 3: Finaler Vergleichswert (Combined Score) berechnen

Der Combined Score ermoeglicht den fairen Vergleich zwischen Teams mit unterschiedlichen Budget-Tiers. Er beruecksichtigt:
- **60%** Kundenzufriedenheit (Kernmetrik)
- **30%** Return on Security (Effizienz)
- **10%** Schadensminimierung (absoluter Erfolg)

### Schritt 1: RoS normalisieren (0-100 Skala)

Der RoS wird auf eine 0-100 Skala umgerechnet, damit er mit den anderen Komponenten vergleichbar ist.

```
RoS_normalized = (RoS + 1) x 33.33

RoS_normalized = (_______ + 1) x 33.33

RoS_normalized = _______
```

**Begrenzen auf 0-100:**
- Falls RoS_normalized < 0: RoS_normalized = 0
- Falls RoS_normalized > 100: RoS_normalized = 100

```
RoS_normalized (begrenzt) = _______
```

### Schritt 2: Schadenskomponente berechnen

Die Schadenskomponente belohnt niedrigen absoluten Schaden.

```
Damage_component = 100 - (Gesamtschaden / 5)

Damage_component = 100 - (_______ / 5)

Damage_component = 100 - _______

Damage_component = _______
```

**Begrenzen auf 0-100:**
- Falls Damage_component < 0: Damage_component = 0
- Falls Damage_component > 100: Damage_component = 100

```
Damage_component (begrenzt) = _______
```

### Schritt 3: Combined Score berechnen

```
Combined Score = (KZ_final x 0.6) + (RoS_normalized x 0.3) + (Damage_component x 0.1)

Combined Score = (_______ x 0.6) + (_______ x 0.3) + (_______ x 0.1)

Combined Score = _______ + _______ + _______

Combined Score = _______
```

---

## Teil 4: Ergebnis-Uebersicht

| Kennzahl | Ihr Ergebnis | Benchmark |
|----------|:------------:|:---------:|
| **Gesamtkosten** | _______ k Euro | Je nach Budget-Tier |
| **Gesamtschaden** | _______ k Euro | < 200k ist gut |
| **Vermiedener Schaden** | _______ k Euro | > 400k ist gut |
| **RoS** | _______ % | > 50% ist gut |
| **Finale KZ** | _______ | >= 50 = positiv |
| **Combined Score** | _______ | Vergleich mit anderen Teams |

---

## Teil 5: Team-Ranking (fuer Moderator)

Alle Teams eintragen und nach Combined Score sortieren:

| Rang | Team | Budget-Tier | KZ final | RoS (%) | Combined Score |
|:----:|------|:-----------:|:--------:|:-------:|:--------------:|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

---

## Rechenbeispiel

**Team "CyberShield"** mit Medium Budget (400k):

| Eingangswerte | |
|---------------|---------|
| Init-Kosten | 180k |
| OPEX pro Welle | 50k |
| Endschaden W1 | 64k |
| Endschaden W2 | 112k |
| Endschaden W3 | 40k |
| Event-Strafen | 15k |
| Finale KZ | 58 |

**Berechnung:**

```
Gesamtkosten = 180 + (50 x 3) + 15 = 180 + 150 + 15 = 345k

Gesamtschaden = 64 + 112 + 40 = 216k

Vermiedener Schaden = 620 - 216 = 404k

RoS = (404 - 345) / 345 = 59 / 345 = 0.171 = 17.1%

RoS_normalized = (0.171 + 1) x 33.33 = 1.171 x 33.33 = 39.03

Damage_component = 100 - (216 / 5) = 100 - 43.2 = 56.8

Combined Score = (58 x 0.6) + (39.03 x 0.3) + (56.8 x 0.1)
               = 34.8 + 11.71 + 5.68
               = 52.19
```

**Ergebnis Team CyberShield:**
- RoS: **17.1%** (solide Investition)
- Combined Score: **52.19** (gutes Ergebnis)

---

## Schnellreferenz: Formeln

| Formel | Berechnung |
|--------|------------|
| **Gesamtkosten** | Init + (OPEX x 3) + Event-Strafen |
| **Gesamtschaden** | Summe aller Endschaeden (W1 + W2 + W3) |
| **Vermiedener Schaden** | 620k - Gesamtschaden |
| **RoS** | (Vermieden - Kosten) / Kosten |
| **RoS_normalized** | min(100, max(0, (RoS + 1) x 33.33)) |
| **Damage_component** | min(100, max(0, 100 - Schaden/5)) |
| **Combined Score** | KZ x 0.6 + RoS_norm x 0.3 + Damage x 0.1 |

---

*Endauswertung fuer Security-Planspiel - Version 2.0*