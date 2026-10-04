
# CIA-Planspiel Automotive (deterministisch, konfigurierbar)

Ein **konfigurationsgetriebenes IT‑Security‑Planspiel** für einen Automotive‑Zulieferer. Die Teilnehmenden agieren als Beratungsteams, **verhandeln ein Budget**, wählen **Sicherheitsmaßnahmen in drei Reifegraden (L1/L2/L3)**, reagieren auf **deterministische Events** und **Angriffe** und optimieren **Kundenzufriedenheit (KZ)**, **CIA‑Ziele** und **Return on Security (RoS)**.

> **Wichtig:** Diese README hält sich **rein an die Funktion und das Spieldesign**.  
> Es werden **keine festen Zahlenvorgaben** (Werte/Variablen) gemacht. **Alle Parameter sind konfigurierbar**.  
> Das Spiel ist so gestaltet, dass eine **Auswertung mit 1–2 Tabellen** genügt.

---

## Ziele & Lernwerte

- **Determinismus statt Zufall:** Keine Würfel, keine Hidden‑Randomness. Alle Ergebnisse sind **vorhersehbar** aus **Konfiguration + Entscheidungen** ableitbar.
- **Spieler‑Agency:** Entscheidungen haben **sichtbare, nachvollziehbare Effekte** (KZ, CIA‑Erfüllung, Schäden, RoS).
- **Realitätsnähe:** Maßnahmen, Abhängigkeiten, Events und Angriffe spiegeln gängige Security‑Praxis in der **Fertigungs‑/OT‑ und SaaS‑Realität**.
- **Einfach auswertbar:** Das Ergebnis lässt sich mit **max. zwei Tabellen** transparent darstellen.

---

## Rollen

- **Beratungsteams**: Treffen Budget‑ und Maßnahmenentscheidungen, reagieren auf Events/Angriffe, kommunizieren Changes.
- **Unternehmensvertreter (Facilitator)**: Spielt den Kunden, moderiert Discovery, setzt deterministische Trigger, erklärt Effekte.
- Optional: **Attack/Rules Controller** (kann der Facilitator mit übernehmen).

---

## Kernelemente (Objekte)

- **Budget (B):** Punkte für Erst‑Invest (Init) und laufende Kosten (OPEX). Überziehung kostet linear KZ, siehe Budget Review.
- **Kundenzufriedenheit (KZ):** Skala mit fester Klammerung (0…100), Effekte **linear und konfigurierbar**.
- **Maßnahmen (L1/L2/L3):**  
  - Attribute: `costInit`, `costOpex`, `cia={c,i,a}`, `mitigations` (gegen Angriffe), `eventEffects`, `dependencies`.
  - **Level‑Intuition:** L1 = Basis (gering), L2 = Standard (mittel), L3 = erweitert (hoch). Stärkegrade sind **parametrierbar**.
- **Wellen:** Jede Welle besitzt **Gewichte (wC,wI,wA)**, eine **E‑Schwelle** und **Angriffe** (Anzahl frei konfigurierbar).
- **Events:** Regelbasierte Trigger (Zeit, Signale, Maßnahmen‑Level) mit klaren Effekten (Budget/KZ/Severity‑Mod/Faktoren).
- **Discovery‑Signale:** Kontextscores (z. B. OT‑Dauerbetrieb, Auditdruck, SaaS‑Kritikalität, Lieferkette), die Gewichte/Angriffe/Erwartungen **deterministisch** steuern.
- **Angriffe:** `baseSeverity`, `sUnit` (Schaden je Stufe), `kzUnit` (KZ‑Verlust je Stufe), `ciaImpactPerStep`, referenzierte Mitigations.

---

## Spielablauf (State‑Machine)

1. **Discovery (Roleplay)**  
   Teams stellen Fragen; der Facilitator beantwortet **kontextbezogen** (keine Lücken benennen).  
   → Setze **Discovery‑Signale** (Skalen frei konfigurierbar).
2. **Budgetverhandlung**  
   Teams einigen sich auf ein Startbudget. **KZ‑Effekt** und **Erwartungen** sind regelbasiert (konfigurierbar).
3. **Maßnahmenwahl**  
   Teams wählen Maßnahmen und **Level**. **Abhängigkeiten** werden geprüft. **OPEX** wird notiert.
4. **Welle**  
   a) Events anwenden (Trigger)  
   b) Angriffe deterministisch auflösen (siehe „Deterministische Auflösung“)  
   c) **OPEX** zahlen & **Erholung** anwenden (falls konfiguriert)
5. **Change‑Fenster**  
   Upgrades/Swaps gemäß Regeln (wirksam **ab nächster Welle**), mit **Kommunikationseffekten** auf KZ.
6. **Abschluss & Debrief**  
   Einfache **Auswertung** (1–2 Tabellen) und Reflexion.

> **Hinweis:** Anzahl Wellen, Events und Angriffe pro Welle sind **frei konfigurierbar**.

---

## Discovery (Hinweis‑Logik, ohne „Lücken“ zu nennen)

- **Signale**: Jedes Themenfeld (z. B. OT‑Betrieb, OEM‑Audit, SaaS‑Abhängigkeit, Lieferanteneinbindung, Schutz von IP) erhält einen **Kontextscore**.  
- **Deterministische Effekte (konfigurierbar):**
  - **Gewichts‑Deltas** je CIA‑Dimension (z. B. A höher bei OT‑Dauerbetrieb).
  - **Angriffsselektion** (z. B. OT‑Störung/SaaS‑Outage/Exfiltration/Supply‑Chain).
  - **Schwere‑ oder Erwartungs‑Mods** (z. B. Anhebung `baseSeverity` oder `kzUnit` für besonders kritische Themen).
- **Mini‑Tipps**: Der Facilitator gibt **kontextuelle Hinweise** („Wiederanlauf steigert Lieferfähigkeit“), **ohne** konkrete Lücken zu benennen.

---

## Maßnahmen (L1/L2/L3) & Abhängigkeiten

- **Level‑Wirkung (funktional):**
  - **CIA‑Beiträge:** L1 < L2 < L3 (Steigerungskurven frei konfigurierbar).
  - **Mitigation gegen Angriffe:** L1 = gering, L2 = mittel, L3 = hoch (z. B. –1/–2/–3; **Werte frei**).
- **Abhängigkeiten (Beispiele, inhaltlich realistisch; Werte/Level frei):**
  - EDR/XDR auf hohem Level verlangt ein Mindest‑Level bei SIEM/MDR.
  - PAM auf hohem Level verlangt ein Mindest‑Level bei Asset‑/CMDB.
  - Backups mit hohem Schutzgrad empfehlen Mindest‑Level bei DR/BCP.
  - OT‑Allow‑Listing ist wirksamer in Kombination mit Netzsegmentierung.
- **Breite statt Monokultur:** Das Design belohnt **breite Abdeckung** über **einseitige Maximierung**.

---

## Events (regelbasiert)

- **Trigger‑Typen:** Zeit/Welle, Discovery‑Signal, Maßnahme(n) vorhanden/nicht vorhanden, Team‑entscheidungsabhängig.  
- **Effekt‑Typen:** `budgetDelta`, `kzDelta`, `severityMod` (global/targeted), `kzFactor`, `damageFactor`, `opexPenalty`, **oder** KZ‑Bonus bei Compliance‑Treffern.  
- **Planbarkeit:** Alle Events ergeben sich **deterministisch** aus den Triggern – **keine Überraschungen** bei aufmerksamer Discovery & Planung.

---

## Angriffe (konfigurierbar)

- **Felder:** `id`, `name`, `targetCIA`, `baseSeverity`, `sUnit`, `kzUnit`, `ciaImpactPerStep={c,i,a}`, `mitigationRefs`.  
- **Beispiele (Domänenbezug):** Ransomware (Office‑IT), Phishing/BEC, OT‑Netzstörung (MES/PLC), SaaS‑Outage, Datenexfiltration (IP), Supply‑Chain/CI‑CD.  
- **Domänenlogik:** Jeder Angriff adressiert **primär** eines der CIA‑Ziele, kann aber **sekundäre** Effekte auf andere haben.

---

## Deterministische Auflösung (Formeln, symbolisch)

> Alle Variablen sind **konfigurierbar**; die Formeln bleiben **fix**.

- **Mitigation‑Summe:**  
  `M_sum = min(MIT_CAP, Summe(Level‑Mitigations aller passenden Maßnahmen))`
- **Endschwere:**  
  `G = max(0, baseSeverity + Σ(eventSeverityMods) − M_sum)`
- **Auswirkungen:**  
  - **Schaden:** `Damage = G * sUnit * Π(damageFactors)`  
  - **KZ:** `ΔKZ = − G * kzUnit * Π(kzFactors)` (Klammerung auf 0…100)  
  - **CIA‑Mali:** je Stufe `G` nach Angriffsspezifikation (`ciaImpactPerStep`)
- **Erholung (Ende Welle):** Optionaler **Recovery‑Faktor** (z. B. über Backups/DR) reduziert temporäre CIA‑Mali um einen **konfigurierbaren Anteil**.

---

## Wellen‑Ziel (E‑Wert) & Scoring

- **Team‑CIA:** `Team_C`, `Team_I`, `Team_A` = Summe der Maßnahmen‑CIA.  
- **Gewichteter Erfüllungsgrad:**  
  `E = Team_C * wC + Team_I * wI + Team_A * wA`
- **E‑Schwelle:** pro Welle konfigurierbar; nur die Gesamtreduktion (E‑Wert + Gesamtbonus) oberhalb der Schwelle mindert den Angriff. Einen eigenen KZ‑Bonus/Malus für ein E‑Ziel gibt es nicht.
- **Rundung (wie auf Papier):** Die KZ-Änderung je Welle (Angriff + Events) wird genau einmal auf eine ganze Zahl gerundet, ab ,5 vom Betrag aufgerundet (+2,5 → +3, −2,5 → −3); danach wird die KZ auf 0–100 begrenzt. E-Wert, Gesamtreduktion, Reduktion über Schwelle und Schweregrad bleiben exakt; der Schaden bleibt exakt in ganzen Euro.
- **Return on Security (RoS):**
Gesamtkosten  = eigene Sicherheitsausgaben = Σ Init + Σ Init‑Differenzen aus Upgrades und neuen Maßnahmen + Σ OPEX je Welle (Level der jeweiligen Welle) + Kurswechsel‑Differenz
Verluste      = Sum(Damage über alle Angriffe)
Vermeidete Verluste = Sum(Basisverluste ohne Mitigation) − Verluste
RoS           = (Vermeidete Verluste − Gesamtkosten) / Gesamtkosten

Nicht enthalten: Event‑Effekte auf Kosten oder Budget (Straf‑OPEX, OPEX‑Rabatte wie „Operative Unterstützung“, Budget‑Kürzungen wie „Sparprogramm“); sie zählen nur für das Budget.

> **Einfach auswertbar:** Alle relevanten Größen (Kosten, Verluste, KZ, E) lassen sich in **1–2 Tabellen** zusammenfassen (siehe Vorlagen unten).

---

## Change‑Fenster (Planbarkeit + Agency)

- **Zeitpunkte:** Zwischen den Wellen.  
- **Erlaubt:** Upgrades L1→L2→L3 (wirksam **ab nächster Welle**), Swaps (eine raus, eine rein) mit konfigurierbarer **Change‑Gebühr**.  
- **Kommunikationseffekt:** Reife Business‑/BCP‑Kommunikation kann KZ‑Effekte der Changes positiv beeinflussen (konfigurierbar).  
- **Zwangs‑Change (optional):** Bei starker Zielverfehlung kann ein **mindestens ein relevantes Upgrade** erforderlich sein (Regel konfigurierbar).

---

## Budget Review und Überziehung

- **Zeitpunkt:** Das Restbudget (Budget + Budget‑Änderungen durch Events − eigene Kosten − Event‑OPEX) wird **einmal** geprüft, nach der letzten Welle. Zwischenstände unter null sind während des Spiels erlaubt.
- **Restbudget ≥ 0:** KZ‑Bonus nach den Restbudget‑Stufen aus der Config.
- **Stufengrenzen:** Eine Restbudget‑Stufe gilt ab ihrem Mindestbetrag einschließlich („ab …“). Die Kartentexte werden aus der Stufenliste der Konfiguration erzeugt (`planspiel.review_text.boundary_text`), nie von Hand geschrieben; dieselbe Liste nutzt die Simulation.
- **Restbudget < 0 (Überziehung):** −X KZ **je angefangene Schrittweite** Überziehung. X (`overspend_penalty.kz_per_step`) und die Schrittweite (`overspend_penalty.step`) stehen in der Config und sind bis zur Neuskalierung vorläufig. Die Nachschlagetabelle für die Karte wird daraus erzeugt (`planspiel.review_text.penalty_rows`).
- **Begrenzung:** Nach dem Budget Review wird die KZ auf 0–100 begrenzt; weitere Überziehung senkt sie dann nicht unter null.

---

## Spielbarkeit & Moderation

- **Einfachheit wahren:**  
- Beschränke Anzahl Maßnahmenkarten, Angriffe und Events auf ein **überschaubares Set** (alles konfigurierbar).  
- **Transparenz**: Formeln und Trigger offenlegen; Effekte **kurz begründen** („B X − M Y + Event Z ⇒ G“).
- **Discovery‑Hinweise:** Immer **kontextualisiert** (Zielbild), niemals **Lücke benennen**.
- **Realitätsnähe:** OT‑Abhängigkeiten, SaaS‑Prozesse, Lieferkette, Identity/Logging/Backups in stimmigen Relationen halten (über Parameter).

---

## Auswertungsvorlagen (2 Tabellen genügen)

> Kopiere die Vorlagen und trage **nur eure Entscheidungen & Ergebnisse** ein (keine zusätzlichen Tools nötig).

### Tabelle 1 – Entscheidungen & Kosten (Team‑Übersicht)
| Phase | Entscheidung | Maßnahme/Level | Init‑Kosten | OPEX/Welle | Begründung/Notizen |
|---|---|---|---|---|---|
| Discovery | Signale (Kurz) | – | – | – | z. B. OT‑Betrieb ausgeprägt, OEM‑Audit bald |
| Budget | Startbudget | – | – | – | Trade‑off Erwartung/KZ |
| Wellen‑Start | Maßnahmen‑Set | Mx L* … | Σ | Σ | Abhängigkeiten erfüllt? |
| Change‑Fenster | Upgrades/Swaps | Mx L* → L* | Δ | Δ | Kommunikation (KZ‑Effekt) |

### Tabelle 2 – Ergebnisse je Welle (E, KZ, Schäden, CIA)
| Welle | Gewichte (wC/wI/wA) | Team‑CIA (C/I/A) | **E** | KZ Δ (Welle) | Angriffe (kurz) | Sum Schaden | CIA‑Mali (temporär) | Recovery angewandt? |
|---|---|---|---:|---:|---|---:|---|---|
| 1 | [ ] / [ ] / [ ] | [ ] / [ ] / [ ] | [ ] | [ ] | A1: G=…, A2: G=… | [ ] | C−… I−… A−… | Ja/Nein |
| 2 | [ ] / [ ] / [ ] | [ ] / [ ] / [ ] | [ ] | [ ] | A1: G=…, A2: G=… | [ ] | C−… I−… A−… | Ja/Nein |
| 3 | [ ] / [ ] / [ ] | [ ] / [ ] / [ ] | [ ] | [ ] | A1: G=…, A2: G=… | [ ] | C−… I−… A−… | Ja/Nein |

> **Finale Kennzahlen (unter der Tabelle):**  
> **Gesamtkosten:** [ ] **Gesamtverluste:** [ ] **Vermeidete Verluste:** [ ] **RoS:** [ ] **Finale KZ:** [ ]

---

## Parametrisierung (ohne feste Zahlen)

> Alle Werte sind **frei wählbar** und sollten vor dem Spiel **einfach** auf einer Seite dokumentiert werden.

- **KZ‑Startwert**, **KZ‑Effekte** je Budgetspanne/Change‑Kommunikation.  
- **Gewichte pro Welle (wC,wI,wA)** und **E‑Schwellen**.  
- **Mitigation‑Cap** pro Angriff, **Level‑Mitigation** (L1/L2/L3).  
- **Überziehungsstrafe X** je angefangene Schrittweite (Budget Review).  
- **Angriffswerte**: `baseSeverity`, `sUnit`, `kzUnit`, `ciaImpactPerStep`.  
- **Event‑Trigger** und **Effekt‑Faktoren** (Budget/KZ/Severity/Straf‑OPEX).  
- **Recovery‑Faktor** und Bedingungen (z. B. über Backups/DR).  
- **Abhängigkeitsmatrix** für L3‑Maßnahmen.

> **Empfehlung:** Beginne mit **wenigen** Maßnahmen/Angriffen/Events und **skalieren** bei Bedarf.

---

## Qualitätssicherung (ohne Zufall, ohne Komplexität)

- **Determinismus prüfen:** Gleiche Inputs führen zu gleichen Outcomes.  
- **Balance testen:** Keine einzelne Maßnahme/Strategie darf **dominant** sein.  
- **Realitätscheck:** Mapping zu echten Szenarien (OT‑Stillstand, Exfil, SaaS‑Ausfall, Phishing, Supply‑Chain) plausibel?  
- **Spielzeit & Verständlichkeit:** In einem Durchlauf sollte die Dokumentation **auf eine Seite + 2 Tabellen** passen.

---

## Simulation (alle Outcomes)

Für eine vollständige, deterministische Enumeration aller möglichen Outcomes gibt es eine kleine Simulation. Die Regeln folgen den Parametern aus der `simulation_config.json`, inklusive Abhängigkeiten, Events, CIA‑Gewichtung und Angriffsauswertung.  

**Setup (einmalig):** `uv sync` installiert die verwaltete Python-Version (3.12) und alle Abhängigkeiten exakt aus `uv.lock`. Alle Befehle laufen über `uv run` – unabhängig davon, welches `python` auf dem PATH liegt. Tests: `uv run pytest`.

**Zusammenfassung (Standardlauf):**
```
uv run python simulate_outcomes.py --config simulation_config.json --budget-tier medium
```

Der Standardlauf bewertet jede gültige Kombination des Tiers, auch die über Budget, und schreibt `simulation_summary_medium.json` (anderer Pfad über `--summary`) sowie eine kurze Konsolentabelle: Top-K (Standard 10, `--top K`) nach End-KZ, RoS und Final-Index (vorläufig bis zur Neuskalierung), Perzentile (Nearest-Rank) von KZ und RoS getrennt nach im/über Budget, das beste Ergebnis im Budget gegenüber dem besten über Budget (End-KZ) und die Pareto-Front End-KZ gegen eigene Kosten. Definitionen: "über Budget" heißt Init + OPEX × Wellen + Event-OPEX > Budget + Event-Budget; "eigene Kosten" sind Init + OPEX je Welle (plus Init-Differenzen bei Change-Fenster-Zügen), ohne Event-Effekte; der RoS rechnet nur mit den eigenen Kosten und ist bei eigenen Kosten 0 nicht definiert (n/a). Alle Tiers nacheinander:
```
for t in low medium high; do uv run python simulate_outcomes.py --budget-tier $t; done
```

**Vollständiger Dump nur auf Anfrage:**
```
uv run python simulate_outcomes.py --budget-tier medium --dump-jsonl simulation_full_medium.jsonl
```

Der Dump enthält eine JSON-Zeile je gültiger Kombination (Code-Ziffern in der Maßnahmen-Reihenfolge der Config) und ist sehr groß; nie vollständig einlesen, nur zeilenweise oder gezielt auswerten.

**Legacy-Vollausgabe (Eingabe für `analyze_simulation_results.py`):**
```
uv run python simulate_outcomes.py --config simulation_config.json --budget-tier medium --output simulation_results.json
```

Die Ausgabe enthält alle Maßnahmen-Kombinationen im Budget (inkl. Level 0-3), die End-KZ, Schäden, CIA-Mali sowie die Kostenübersicht.

**Legacy-Vollausgabe mit Budget-Filter (realistische Outcomes, Budget voll nutzen):**
```
uv run python simulate_outcomes.py --config simulation_config.json --budget-tier medium --budget-utilization 0.9 --output simulation_results.json
```

`--budget-max` ist keine harte Obergrenze: Es ist nur die Basis für `--budget-utilization` (Schwelle = Anteil × `--budget-max`); die harte Grenze ist das Tier-Budget inkl. Event-Budget. `--budget-min`, `--budget-max` und `--budget-utilization` wirken nur zusammen mit `--output`.
```
uv run python simulate_outcomes.py --config simulation_config.json --budget-min 300 --budget-max 380 --output simulation_results.json
```

**Auswertung der Simulationsergebnisse:**
```
uv run python analyze_simulation_results.py --input simulation_results.json --config simulation_config.json --top 5
```

Final-Index gewichtet KZ und RoS (Standard: 1.0/1.0):
```
uv run python analyze_simulation_results.py --input simulation_results.json --config simulation_config.json --weight-kz 1.0 --weight-ros 0.5
```

---
## Ziel des Spiels

Das Planspiel richtet sich an Studierende und vermittelt die Wichtigkeit von Sicherheitsmaßnahmen – nicht über tiefes Technik‑Know‑how, sondern über risikoorientiertes Denken und unternehmerische Abwägungen. Im Fokus steht, wie man Security im Kontext von Budget, Geschäftszielen und Stakeholder‑Erwartungen sinnvoll priorisiert. Die Teilnehmenden erleben den Berateralltag realistisch und nachvollziehbar: von der Auftragsklärung über die Begründung von Maßnahmen bis zur Kommunikation bei Störungen. Ziel ist es, Entscheidungen nachvollziehbar zu treffen, Trade‑offs transparent zu machen und den Business‑Nutzen von Security (z. B. Vermeidung von Ausfällen, Schutz von IP, Compliance‑Fähigkeit) sichtbar zu machen – ohne dass tiefes technisches Detailwissen erforderlich ist.

## Lizenz & Beiträge

- Lizenz & Beitragshinweise nach Bedarf ergänzen.  
- Vorschlag: Issues/Feedback sammeln zu **Spielbarkeit**, **Realitätsnähe** und **Auswertbarkeit** (bitte ohne konkrete Zahlenvorgaben einzureichen).

---
