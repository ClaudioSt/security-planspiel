# Evaluierung der Durchführbarkeit (MVP v2.0)

## Ziel & Vorgehen
Diese Evaluierung spielt das Spiel drei Mal **deterministisch** anhand der in der Parameter-Tabelle definierten Werte durch und leitet daraus eine **Range möglicher Ergebnisse** ab. Grundlage sind die in `PARAMETER_TABELLE.md` dokumentierten **E-Ziele**, **Angriffswerte**, **Mitigation-Caps**, **KZ-Effekte** sowie die Formeln zur Auflösung.  

### Annahmen (klar gekennzeichnet)
- Es werden **keine Discovery-Kontextboni** außer den explizit angegebenen verwendet (konservativ).  
- **Recovery-Faktor (M4)** reduziert den Schaden aller Wellen, sobald M4 vorhanden ist (wie in der Formel beschrieben).  
- Event 1 (OEM-Audit) wird in **Welle 2** ausgelöst, abhängig von E-Wert der **Welle 1**.  
- Event 2 (Fluktuation) wird **nach Welle 1** ausgelöst, wenn M6 < L2.  

Diese Annahmen sind transparent und können in einer Variante mit Kontextboni oder alternativen Eventinterpretationen angepasst werden.

---

## Szenarien (3 Durchläufe)

### Szenario A – **niedriges Budget** (240)
**Ziel:** Minimal solides Set, viele L1, budgetschonend.  
**Start-KZ:** 70 (Budget-Range „niedrig“)  
**Maßnahmen:** M1 L1, M2 L1, M3 L1, M4 L1, M5 L1, M6 L1, M7 L1, M8 L1  
**CIA-Summe:** C=13 / I=17 / A=13  

**E-Werte:**
- W1: 14,6  
- W2: 13,8  
- W3: 14,2  

**Ergebnis (kurz):**
- E-Ziele werden in allen Wellen **deutlich verfehlt** ⇒ KZ sinkt schnell auf 0.
- Schäden sind trotz niedriger Mitigation relativ hoch (insb. W2).  

**Schäden gesamt:** **208,8 T€**  
**Finale KZ:** **0**  

---

### Szenario B – **mittleres Budget** (320)
**Ziel:** Breite Abdeckung mit L2-Fokus, OPEX im Blick.  
**Start-KZ:** 60 (Budget-Range „mittel“)  
**Maßnahmen:** M1 L2, M2 L2, M3 L2, M4 L2, M5 L1, M6 L2, M7 L2  
**CIA-Summe:** C=21 / I=26 / A=17  

**E-Werte:**
- W1: 22,2  
- W2: 19,6  
- W3: 21,7  

**Ergebnis (kurz):**
- Mitigation wirkt: W1 und W3 werden praktisch neutralisiert.  
- **Trotzdem** werden E-Ziele nicht erreicht ⇒ KZ fällt in W2/W3 auf 0.  

**Schäden gesamt:** **70 T€**  
**Finale KZ:** **0**  

---

### Szenario C – **hohes Budget** (400)
**Ziel:** Maximale Wirksamkeit bei Kernmaßnahmen, dennoch budgetkonform.  
**Start-KZ:** 50 (Budget-Range „hoch“)  
**Maßnahmen:** M1 L3, M2 L3, M3 L2, M4 L3, M5 L1, M6 L2, M7 L1  
**CIA-Summe:** C=22 / I=30 / A=20  

**E-Werte:**
- W1: 24,8  
- W2: 22,4  
- W3: 24,0  

**Ergebnis (kurz):**
- Angriffe W1/W3 werden durch hohe Mitigation nahezu vollständig neutralisiert.  
- **E-Ziele (50/60/70)** bleiben dennoch unerreichbar ⇒ KZ fällt auf 0.  

**Schäden gesamt:** **40 T€**  
**Finale KZ:** **0**  

---

## Range der Ergebnisse (aus den 3 Durchläufen)

| Kennzahl | Niedriges Budget | Mittleres Budget | Hohes Budget | Beobachtete Range |
|---|---:|---:|---:|---:|
| **Gesamtschaden (T€)** | 208,8 | 70 | 40 | **40 – 208,8** |
| **Finale KZ** | 0 | 0 | 0 | **0 – 0** |
| **E-Werte (typisch)** | ~14–14 | ~19–22 | ~22–25 | **~14 – 25** |

---

## Durchführbarkeit – Bewertung

### ✅ Positive Aspekte
- **Determinismus & Nachvollziehbarkeit** sind gegeben: Alle Outcomes lassen sich mit der Tabelle reproduzieren.  
- **Mitigation wirkt** messbar auf Schäden, d. h. Investitionen haben klaren Effekt.  
- Die **Schaden-Range** ist plausibel und differenziert zwischen niedriger und hoher Reife.

### ⚠️ Kritischer Befund: **E-Ziele sind zu hoch im Verhältnis zur CIA-Skala**
Selbst bei sehr starker Maßnahmenwahl liegen die E-Werte in allen Wellen **unter 25**.  
Die niedrigsten E-Ziele beginnen jedoch bei **30** (niedriges Budget) und reichen bis **70** (hohes Budget).  
Dadurch entstehen systematisch:
- **KZ-Mali in jeder Welle**, unabhängig von Strategie.  
- **Event 1 Malus** (Audit) bei allen Varianten.  
- **Finale KZ = 0** als nahezu unvermeidliches Ergebnis.  

### Konsequenz
**Das Spiel ist in der aktuellen Parametrisierung zwar spielbar, aber für die Teams praktisch nicht „gewinnbar“.**  
Die Motivation kann leiden, weil gute Strategien (hohes Budget, starke Maßnahmen) **nicht sichtbar belohnt** werden.

---

## Empfehlung zur Kalibrierung (kurz & konkret)

1. **E-Ziele absenken** (z. B. ca. 12/18/24 für niedrig–hoch) **oder**  
2. **CIA-Werte der Maßnahmen skalieren** (z. B. ×2) **oder**  
3. **E-Formel skalieren** (z. B. `E = (Team_C*wC + Team_I*wI + Team_A*wA) * 2`).  

Damit würden E-Ziele erreichbar, **KZ-Boni** realistisch eintreten und die Spielbalance verbessert.

---

## Test einer vorgeschlagenen Alternative (Beispiel)

### Alternative: **E-Formel skalieren (×2)** im mittleren Budget-Szenario
Diese Variante prüft die Empfehlung **„E skaliert“** auf Durchführbarkeit und sichtbare Belohnung guter Entscheidungen.  

**Annahmen:** Gleiche Maßnahmen wie in Szenario B, nur `E = (Team_C*wC + Team_I*wI + Team_A*wA) * 2`.  
**E-Werte (skaliert):** W1: **44,4**, W2: **39,2**, W3: **43,4**  
**E-Ziele (mittel):** 40 / 50 / 60  

**Kurzfazit:**  
- **W1** erreicht (KZ-Bonus)  
- **W2/W3** verfehlt (KZ-Malus)  
- Ergebnis: **sichtbar differenzierter Verlauf** statt automatischem KZ-Absturz in allen Wellen.  

> Hinweis: Mit dieser Alternative entstehen **messbare Unterschiede** zwischen Strategie-Qualitäten, ohne die Angriffswerte zu ändern.

---

## Zwischen den Wellen: Maßnahmen & Events (Erweiterungsideen)

### Maßnahmen zwischen den Wellen anpassen?
Das Konzept sieht bereits ein **Change-Fenster** zwischen den Wellen vor.  
Zusätzlich wäre möglich, **Maßnahmen vorübergehend zu stoppen** (OPEX sparen, aber CIA/Mitigation verlieren) oder **gezielt kurzfristig hochzufahren**, um **Zwischenziele (E)** zu erreichen.  
**Empfehlung:** Wenn eingeführt, sollte es klare Regeln geben:
- **Aktivieren/Deaktivieren** nur im Change-Fenster, wirksam **ab nächster Welle**.  
- **KZ-Effekt** für Kommunikation (positiv bei transparentem Vorgehen, negativ bei „Sparen auf Risiko“).  
- Optional: **Change-Gebühr** oder **Einmalrisiko** (z. B. Minderung der Mitigation in der Umstellungswelle).  

### Events zwischen den Wellen (Budgetänderung)
Zusätzliche **Zwischen-Events** können das Budget beeinflussen und schaffen Dynamik.  
Beispiele (nur wenn noch nicht implementiert):
- **Budget-Boost:** Förderung/Zertifizierung → **Budget +X**  
- **Budget-Cut:** Kostendruck/Compliance-Defizit → **Budget −X**  
- **Koppelung an Ziele:** Erreichen/Verfehlen von **E** oder KZ-Schwellen triggert Zu-/Abschläge  

Diese Events erhöhen die **Planungsspannung** und erlauben **strategische Anpassungen** zwischen den Wellen.

---

## Fazit
- **Durchführbarkeit:** gegeben (deterministisch, auswertbar, modular).  
- **Spielbalance:** derzeit zu „hart“ über E-Ziele; KZ fällt unabhängig von Strategie.  
- **Range der Ergebnisse:** Schäden 40–208,8 T€, KZ final 0–0 (bei aktuellem Setup).  

Mit einer einfachen E-Kalibrierung ist das Spiel **sofort** deutlich besser spielbar.

---

## Optimales Zielbild & Balancing-Leitplanken

### Was wäre „optimal“?
Ein **optimales Ergebnis** sollte erreichbar sein, wenn Teams **breit investieren**, Abhängigkeiten erfüllen, OPEX sauber planen und Change-Fenster sinnvoll nutzen. Dabei gilt:
- **Hohe, aber nicht maximale** E-Ziel-Erreichung in 2 von 3 Wellen.  
- **KZ bleibt stabil** (z. B. 40–70 je nach Budgetrange).  
- **Schäden moderat** (starke Mitigation reduziert G spürbar, aber nicht auf 0).  
- **RoS klar positiv**, weil vermiedene Schäden die Kosten übersteigen.

### Alle Einflussfaktoren auf den Outcome (kompakt)
- **Budget-Range** (KZ-Start + E-Zielschwellen).  
- **CIA-Summen** durch Maßnahmenwahl (breite Abdeckung vs. Monofokus).  
- **Mitigation pro Angriff** (inkl. Cap + Kontextboni).  
- **OPEX-Druck** (mehrere Wellen).  
- **Events** (Audit, Fluktuation, Budget-Events).  
- **Change-Fenster** (Upgrades/Stops wirken zeitversetzt).  
- **Recovery-Faktor** (M4 reduziert Schäden).  

### „Schlechteste Wahl“ soll nicht demotivieren
Ziel ist eine **fallende, aber nicht harte Kurve**:  
- **Schlechte Teams** erreichen **mind. 1 positives Signal** (z. B. E-Welle 1 knapp erreicht **oder** KZ bleibt >20).  
- **Gute Teams** erzielen klar bessere KZ-/Schadenswerte, aber der Abstand bleibt **motivationsfähig**.  

**Balancing-Hebel dafür:**  
1. **E-Ziel-Dreiklang enger fassen** (z. B. 18/24/30 statt 30/40/50).  
2. **KZ-Mali pro verfehltem Ziel etwas reduzieren** (z. B. -3/-5/-6).  
3. **Ein „Sicherheitsnetz“** einführen: einmaliger **KZ-Puffer +5**, wenn Budget niedrig ist und mindestens 5 Maßnahmen gewählt wurden.  

### RoS fast immer positiv – außer bei „falschen“ Entscheidungen
Um RoS im Normalfall positiv zu halten, muss gelten:  
`Vermeidete Verluste > Gesamtkosten` in den meisten Szenarien.  

**Empfohlene Leitplanken:**  
- **Mitigation-Caps** so setzen, dass **G** meist **2–6** liegt (nicht dauerhaft 0).  
- **sUnit** und **kzUnit** so dimensionieren, dass **ohne Maßnahmen** hoher Schaden entsteht, **mit Maßnahmen** aber deutlich reduziert wird.  
- **OPEX** nicht zu hoch ansetzen (OPEX darf nicht regelmäßig das Budget „auffressen“).  

**Negativer RoS nur bei Fehlentscheidungen:**  
- sehr einseitige Maßnahmenwahl ohne Abdeckung des primären Angriffs (z. B. nur Awareness gegen OT-Störung),  
- Ignorieren von Abhängigkeiten,  
- OPEX-Planung überdehnt,  
- Verzichten auf Recovery-Maßnahmen bei hohen Schadensszenarien.  

Damit bleibt **RoS positiv für solide Teams**, während „falsche Strategien“ sichtbar schlechter abschneiden.
