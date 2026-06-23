# CLAUDE.md

Anleitung für Claude Code beim Arbeiten in diesem Repository.

## Was ist das hier?

Ein **offline durchführbares IT-Security-Planspiel** ("CIA-Planspiel Automotive") für Studierende/Teams. Teilnehmende agieren als Beratungsteams für einen fiktiven Automotive-Zulieferer (MechTech), verhandeln ein Budget, wählen Sicherheitsmaßnahmen (Level L1/L2/L3), reagieren auf deterministische Events und Angriffswellen und optimieren Kundenzufriedenheit (KZ), CIA-Zielerfüllung (Confidentiality/Integrity/Availability) und Return on Security (RoS).

Kernprinzip: **Determinismus statt Zufall** — gleiche Inputs führen immer zu gleichen Outputs, keine Würfel. Alle Zahlen sind über `simulation_config.json` parametrisiert, nicht hartcodiert.

Das Spiel wird **live mit Papier/Whiteboard** gespielt (3 Teams à 5 Personen). Der Code in diesem Repo dient nicht der Spieldurchführung selbst, sondern der **Content-Erstellung, Balance-Prüfung und Simulation** im Vorfeld.

## Repo-Struktur

Das Repo ist überwiegend **Markdown-Dokumentation** (Spieldesign, Regelwerk, Druckvorlagen) plus ein paar **Python-Skripte** für Simulation/Balance und PPTX-Generierung.

Wichtige Dokumente (Lesereihenfolge bei Einstieg):
- `README.md` — Spielregeln, Mechanik, Formeln (die Quelle der Wahrheit für die Spiellogik)
- `KONZEPT_MVP.md` / `KONZEPT_MVP_v2.md` — Konzeptpapiere
- `TODO.md` — Entwicklungsfahrplan mit Meilensteinen (M1–M6)
- `ROADMAP_6_TAGE.md`, `TAG_2_DETAILPLAN.md` — Zeitplanung für Produktion
- `MODERATORENLEITFADEN.md`, `MODERATIONSSKRIPT.md` — Facilitator-Material
- `SPIELERANLEITUNG.md` — Spieler-Briefing
- `MASSNAHMENKARTEN.md`, `ANGRIFFSKARTEN.md` — Karteninhalte (Maßnahmen, Angriffe)
- `PARAMETER_TABELLE.md`, `BACKUP_PARAMETER.md` — Parameterübersichten
- `BERECHNUNGSBOGEN_WELLE{1,2,3}_*.md` — Papier-Rechenwege je Welle
- `FORMULARE.md`, `TEAM_TRACKING_BOGEN.md` — druckbare Formulare
- `BALANCE_ANALYSE.md`, `EVALUIERUNGSPLAN.md`, `BEOBACHTUNGSBOGEN_PLAYTEST.md` — QA/Playtest
- `ENDAUSWERTUNG_ROS_VERGLEICHSWERT.md` — Auswertung/Scoring
- `docs/` — kurze Referenzblätter (CIA, Mitigation-Bewertung)
- `final_documents/` — finale Spielunterlagen (docx/pptx/pdf) für den Druck
- `pptx_output/` — generierte PowerPoint-Dateien (Karten/Events)

Python-Skripte:
- `simulation_config.json` — **zentrale Konfiguration**: Budget-Tiers, Wellen (Gewichte wC/wI/wA, E-Schwellen), Angriffe, Maßnahmen, Events. Einzige Quelle für alle Zahlenwerte der Simulation.
- `simulate_outcomes.py` — enumeriert deterministisch alle zulässigen Maßnahmen-Kombinationen und deren Outcomes (KZ, Schäden, CIA-Mali, Kosten) basierend auf `simulation_config.json`.
- `analyze_simulation_results.py` — wertet Simulationsergebnisse aus (Top-N nach Final-Index aus KZ/RoS-Gewichtung).
- `balance_analysis.py` — prüft auf dominante Strategien/Maßnahmen.
- `generate_attack_calculator.py`, `generate_from_template.py`, `generate_pptx_cards.py` — generieren Druckmaterial (Excel-Rechner, PPTX-Karten) aus den Content-Quellen.
- `sim_low.json`, `sim_med.json` — große, vorab generierte Simulationsergebnisse (Budget-Tiers low/medium). **Große Dateien (>10 MB)** — beim Lesen nicht vollständig einlesen, sondern gezielt mit `jq`/Python parsen.

## Spielmechanik in Kürze (siehe README.md für Details)

- **State Machine pro Durchlauf:** Discovery → Budgetverhandlung → Maßnahmenwahl → Welle (Events → Angriffe → E-Ziel-Check → OPEX/Recovery) → Change-Fenster → Abschluss.
- **Deterministische Auflösung:** `M_sum = min(MIT_CAP, Σ Level-Mitigations)`, `G = max(0, baseSeverity + Σ eventSeverityMods − M_sum)`, daraus Schaden/ΔKZ/CIA-Mali.
- **E-Wert je Welle:** `E = Team_C*wC + Team_I*wI + Team_A*wA`, verglichen mit konfigurierbarer Schwelle.
- **RoS:** `(Vermeidete Verluste − Gesamtkosten) / Gesamtkosten`.
- Alle Formeln sind **fix**, alle Werte dazu **konfigurierbar** über `simulation_config.json`.

## Beim Arbeiten in diesem Repo

- **Keine festen Zahlen in Prosa-Dokumenten einführen**, ohne sie auch in `simulation_config.json` zu reflektieren — Doku und Konfiguration müssen synchron bleiben.
- Änderungen an Spielmechanik/Werten gehören zuerst in `simulation_config.json`, dann (falls Formeln/Regeln betroffen sind) in `README.md` und die betroffenen Karten-/Formulardokumente.
- Nach inhaltlichen Änderungen an Maßnahmen/Angriffen/Events: `simulate_outcomes.py` + `balance_analysis.py` laufen lassen, um Dominanzstrategien/Inkonsistenzen zu prüfen, bevor Druckmaterial neu generiert wird.
- Die `.md`-Dokumente sind das **Game-Design-Dokument**, kein Software-Produkt — Änderungen daran sind inhaltliche/redaktionelle Arbeit, keine Code-Refaktorierung.
- `final_documents/` und `pptx_output/` enthalten generierte/finale Binärdateien (docx/pptx/pdf/xlsx) — diese nicht händisch bearbeiten, sondern über die Generator-Skripte bzw. die Ursprungsvorlagen neu erzeugen.
