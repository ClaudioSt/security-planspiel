# CLAUDE.md

Anleitung für Claude Code beim Arbeiten in diesem Repository.

## Was ist das hier?

Ein **offline durchführbares IT-Security-Planspiel** ("CIA-Planspiel Automotive") für Studierende/Teams. Teilnehmende agieren als Beratungsteams für einen fiktiven Automotive-Zulieferer (MechTech), verhandeln ein Budget, wählen Sicherheitsmaßnahmen (Level L1/L2/L3), reagieren auf deterministische Events und Angriffswellen und optimieren Kundenzufriedenheit (KZ), CIA-Zielerfüllung (Confidentiality/Integrity/Availability) und Return on Security (RoS).

Kernprinzip: **Determinismus statt Zufall** — gleiche Inputs führen immer zu gleichen Outputs, keine Würfel. Alle Zahlen sind über `simulation_config.json` parametrisiert, nicht hartcodiert.

Das Spiel wird **live mit Papier/Whiteboard** gespielt (3 Teams à 5 Personen). Der Code in diesem Repo dient nicht der Spieldurchführung selbst, sondern der **Content-Erstellung, Balance-Prüfung und Simulation** im Vorfeld.

## Repo-Struktur

Das Repo ist überwiegend **Markdown-Dokumentation** (Spieldesign, Regelwerk, Druckvorlagen) plus ein paar **Python-Skripte** für Simulation/Balance und PPTX-Generierung.

**⚠️ Zwei Generationen von Content existieren parallel im Repo:**

1. **`final_documents/` — die einzige aktuelle, workshop-relevante Quelle.** Das sind die tatsächlich gedruckten/verteilten Materialien (docx/pptx/pdf), synchron zu `simulation_config.json`. Bei jeder inhaltlichen Änderung an Config-Werten (Schwellen, Boni, CIA, Kosten) **hier** nachziehen.
2. **Die 26 historischen `.md`-Dateien in `archive/historical_docs/`** (früher im Repo-Root; `MODERATORENLEITFADEN.md`, `MODERATIONSSKRIPT.md`, `ANGRIFFSKARTEN.md`, `MASSNAHMENKARTEN.md`, `PARAMETER_TABELLE.md`, `KONZEPT_MVP*.md`, `ROADMAP_6_TAGE.md`, `TODO.md`, `BERECHNUNGSBOGEN_WELLE*.md`, `FORMULARE.md`, `TEAM_TRACKING_BOGEN.md`, `BALANCE_ANALYSE.md`, `EVALUIERUNGSPLAN.md`, `BEOBACHTUNGSBOGEN_PLAYTEST.md`, `ENDAUSWERTUNG_ROS_VERGLEICHSWERT.md`, u.a.) sind **historische Entwicklungsstände aus früheren Spiel-Iterationen** (u.a. datiert auf einen bereits vergangenen Workshop, "MVP 1.0, 28.1.2026"). Sie nutzen teils komplett andere Formeln/Zahlen als die aktuelle Config (z.B. `M_sum`/`kzUnit`-Mechanik statt der aktuellen `Gesamtreduktion`/Fall-1-2-3-Systematik) und sind **nicht** mit `simulation_config.json` synchronisiert. Nicht als aktuelle Referenz verwenden, nicht automatisch mitpflegen — nur auf explizite Anfrage anfassen.

`README.md` bleibt die aktuelle Quelle der Wahrheit für Spielregeln/Formeln (prosa-abstrakt, ohne feste Zahlen). `docs/` enthält kurze, weiterhin gültige Referenzblätter.

`pptx_output/` — generierte PowerPoint-Dateien (Karten/Events), Output der Generator-Skripte.

Python-Skripte:
- `simulation_config.json` — **zentrale Konfiguration**: Budget-Tiers, Wellen (Gewichte wC/wI/wA, E-Schwellen), Angriffe, Maßnahmen, Events. Einzige Quelle für alle Zahlenwerte der Simulation.
- `simulate_outcomes.py` — enumeriert deterministisch alle zulässigen Maßnahmen-Kombinationen und deren Outcomes (KZ, Schäden, CIA-Mali, Kosten) basierend auf `simulation_config.json`.
- `analyze_simulation_results.py` — wertet Simulationsergebnisse aus (Top-N nach Final-Index aus KZ/RoS-Gewichtung).
- `balance_analysis.py` — prüft auf dominante Strategien/Maßnahmen.
- `generate_attack_calculator.py`, `generate_from_template.py`, `generate_pptx_cards.py` — generieren Druckmaterial (Excel-Rechner, PPTX-Karten) aus den Content-Quellen.

## Spielmechanik in Kürze (Stand: aktuell implementiert in `planspiel/rules.py`)

- **State Machine pro Durchlauf:** Discovery → Budgetverhandlung → Maßnahmenwahl → Welle (Events → Angriffe → OPEX/Recovery) → Change-Fenster → Abschluss.
- **E-Wert je Welle:** `E-Wert = Team_C*wC + Team_I*wI + Team_A*wA` (Team-CIA = `base_cia` + Summe der Maßnahmen-CIA-Beiträge).
- **Gesamtbonus:** Summe der `bonus_measures`-Boni, deren Maßnahme das jeweilige `min_level` erreicht (pro Welle 2-3 thematisch passende Maßnahmen).
- **Gesamtreduktion:** `E-Wert + Gesamtbonus`.
- **Deterministische Auflösung (3 Fälle, siehe Angriff-*.docx-Arbeitsblätter):**
  - `reduktion_ueber_schwelle = min(mitigation_cap, max(0, Gesamtreduktion − e_threshold))`
  - `severity = max(0, base_severity*severity_multiplier − reduktion_ueber_schwelle)`
  - `Schaden = severity * s_unit`, ggf. `* (1 − recovery_factor)` wenn `allow_recovery` und M4 aktiv
  - `KZ-Delta = kz_at_full_damage + (reduktion_ueber_schwelle / mitigation_cap) * (kz_at_full_mitigation − kz_at_full_damage)` — **linear interpoliert**, absichtlich (siehe Kommentar in `attack_kz_delta()` in `planspiel/rules.py`), nicht die ggf. abweichende Fall-3-Subformel aus älteren Dokumenten.
- **Rundung (wie auf Papier):** Die KZ-Änderung je Welle (Angriff + Events) wird genau einmal auf eine ganze Zahl gerundet, ab ,5 vom Betrag aufgerundet (+2,5 → +3, −2,5 → −3; `planspiel.rounding.round_half_away`); danach wird die KZ auf 0–100 begrenzt. E-Wert, Gesamtreduktion, Reduktion über Schwelle und Schweregrad bleiben exakt (Ganzzahl-Arithmetik über `Fraction`/Skalierung), der Schaden bleibt exakt in ganzen Euro. Pythons eingebautes `round()` (halb zur geraden Zahl) ist in `planspiel/rules.py` und `planspiel/rounding.py` verboten.
- **RoS:** `(620.000 − Gesamtschaden − eigene Kosten) / eigene Kosten`; eigene Kosten = Init + OPEX je Welle + Init-Differenzen/Kurswechsel-Differenz, ohne Event-Effekte (`rules.security_spend`). **Final-Index** (facilitatorseitiger Vergleichswert über Teams/Tiers): `weight_kz * KZ + weight_ros * (RoS * 100)`, Default-Gewichte 1.0/1.0 (siehe `analyze_simulation_results.py`).
- **Budget Review:** Restbudget-Stufen (≥ 0) bzw. Überziehung −X KZ je angefangene 10.000 € (X = `overspend_penalty.kz_per_step`, vorläufig bis Phase 6; `rules.budget_review_delta`), einmal am Ende, danach Begrenzung auf 0–100.
- **Change-Fenster:** Levelwechsel hoch/runter, Kündigen, Hinzufügen, beliebig viele; Init-Differenz netto und sofort, nie Erstattung; Wirkung und OPEX ab der nächsten Welle (`rules.evaluate_path`); Tausch-Schicht `planspiel tausch` = legales Minimum.
- **Kurswechsel (Welle 1):** genau ein Pflicht-Maßnahmentausch im Change-Fenster danach (aktive Maßnahme raus, in Welle 1 inaktive rein, Level frei); Kunde trägt Init bis zur Höhe der getauschten Maßnahme (`rules.swap_credit`); die statische Enumeration ist der Referenzplan ohne Change-Fenster-Züge.
- Alle Formeln sind **fix**, alle Werte dazu **konfigurierbar** über `simulation_config.json`.

## Beim Arbeiten in diesem Repo

- **Umgebung:** einmalig `uv sync`; Skripte immer über `uv run python <skript>.py`, Tests über `uv run pytest` (schnell) bzw. `uv run pytest -m slow` (volle Enumeration). Nie das `python` auf dem PATH verwenden (auf dieser Maschine Inkscapes Interpreter ohne pip).
- **Keine festen Zahlen in Prosa-Dokumenten einführen**, ohne sie auch in `simulation_config.json` zu reflektieren — Doku und Konfiguration müssen synchron bleiben. Das gilt **verbindlich nur für `final_documents/`** (siehe oben), nicht für die historischen `.md`-Dateien in `archive/historical_docs/`.
- Änderungen an Spielmechanik/Werten gehören zuerst in `simulation_config.json`, dann in `README.md` (falls Formeln/Regeln betroffen sind) und die betroffenen `final_documents/`-Dateien.
- **Print-Sync-Falle:** `wave.e_threshold`, `attack.mitigation_cap` und `bonus_measures[].bonus` stehen **wörtlich gedruckt** auf den `Angriff-{1,2,3}_*.docx`-Arbeitsblättern (Fall-1/2/3-Schwellen, Subformel-Konstanten, Bonus-Tabelle) — die Facilitator:innen rechnen von Hand danach. Für diese drei Dokumente (und `Massnahmenkarten_Security-Game.pptx` für CIA/Kosten/Abhängigkeiten) gibt es **keinen Generator**; Änderungen müssen manuell per `python-docx`/`python-pptx` nachgezogen werden (Run-Text direkt ersetzen, nicht Absatz-Text — sonst geht Formatierung verloren). `Budget.docx` und `Events_Security-Game.pptx` ebenfalls gegenprüfen, wenn Budget-Tiers/Events sich ändern.
- **Balance verifizieren = volle Enumeration, nicht nur `balance_analysis.py`.** `balance_analysis.py` testet nur eine feste Liste benannter Beispielstrategien — nützlich als schneller Sanity-Check, aber nicht repräsentativ für die tatsächliche Verteilung. Für echte Tuning-Entscheidungen: `uv run python simulate_outcomes.py --budget-tier {low,medium,high}` (volle Enumeration aller gültigen Kombinationen inkl. Über-Budget; schreibt `simulation_summary_<tier>.json` mit Top-K nach KZ/RoS/Final-Index, Perzentilen im/über Budget, bestem Ergebnis im vs. über Budget und Pareto-Front) — nicht nur Einzelbeispiele. Der Legacy-Lauf `--budget-utilization 0.85 --output <file>` bleibt nur als Eingabe für `analyze_simulation_results.py`. Bei Formel-Änderungen (z.B. Interpolationskurve) immer zuerst prüfen, ob die Werte auf den Angriff-*.docx-Arbeitsblättern **von Hand nachrechenbar** bleiben (lineare Formeln, keine Exponenten) — das ist ein hartes Designkriterium, keine Empfehlung.
- Nach inhaltlichen Änderungen an Maßnahmen/Angriffen/Events: `uv run python simulate_outcomes.py` (volle Enumeration) + `uv run python balance_analysis.py` laufen lassen, um Dominanzstrategien/Inkonsistenzen zu prüfen, bevor Druckmaterial angepasst wird. Nach Wertänderungen zusätzlich `uv run planspiel gate` (Trim-back-Kriterium, Überziehen darf sich nie lohnen; scheitert mit Nennung des bestimmenden Plans, wenn X zu klein ist).
- Die `.md`-Dokumente sind das **Game-Design-Dokument**, kein Software-Produkt — Änderungen daran sind inhaltliche/redaktionelle Arbeit, keine Code-Refaktorierung.
- `final_documents/` enthält teils generierte, teils direkt gepflegte Binärdateien (docx/pptx/pdf) — siehe Print-Sync-Punkt oben. `pptx_output/` ist reiner Skript-Output und wird über die Generator-Skripte neu erzeugt.
- Von `simulate_outcomes.py --budget-utilization ...` erzeugte volle Enumerationen (`simulation_results*.json`, `sim_low.json`, `sim_med.json`, `sim_high.json`, `simulation_full_*.jsonl` nur mit `--dump-jsonl`) sind groß (>100 MB bis >1 GB) und über `.gitignore` bewusst von Git ausgeschlossen — nicht committen, beim Lesen nie vollständig einlesen, sondern gezielt mit `jq`/Python parsen. Die `simulation_summary_*.json` sind klein, aber ebenfalls gitignored.
