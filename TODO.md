# TODO – Entwicklung des CIA-Planspiels (Automotive, **offline**)

Dieses Dokument beschreibt **Vorgehen, Abhängigkeiten und Reihenfolge** für die Entwicklung eines **deterministischen, konfigurationsgetriebenen IT-Security-Planspiels** (Automotive-Zulieferer), das **vor Ort** mit **Whiteboard, Stiften und optional gedrucktem Material** gespielt wird.  
Die Spielleitung soll **nicht von digitalen Medien abhängig** sein; das Spiel muss **rein offline** durchführbar sein.

> Leitprinzipien (aus dem Spieldesign):
> - **Determinismus**: gleiche Inputs → gleiche Outputs (keine Würfel).
> - **Konfigurierbarkeit**: keine festen Zahlen „im Kopf“; Parameter sind **im Material** (Karten/Tabellen) definiert.
> - **Transparenz/Auswertbarkeit**: Ergebnisse in **1–2 Papier-Tabellen** erfassbar.
> - **Agency**: Maßnahmen und Changes müssen nachvollziehbare Effekte erzeugen.
> - **Offline-by-design**: Berechnungen über **Lookup-Tabellen, Rechenwege und Formularfelder** – kein Laptop erforderlich.

---

## 0) Projekt-Setup (Voraussetzungen)

### 0.1 Repository & Struktur (auch wenn Spiel offline ist)
- [ ] Repo-Struktur festlegen (z. B. `/docs`, `/printables`, `/content`, `/templates`)
- [ ] Konventionen: Namensschema für IDs (Maßnahmen, Angriffe, Events, Wellen), Versionierung der Inhalte
- [ ] Druck-Standards: Papierformat (A4), Schwarzweiß-Tauglichkeit, Lesbarkeit aus 1–2 m

**Abhängigkeit:** keine

### 0.2 Rollen & Arbeitsmodus
- [ ] Verantwortlichkeiten definieren (Game Design, Content, Print-Layout, QA/Playtest, Facilitator-Kit)
- [ ] Definition of Done (DoD) für: Mechanik, Content, Printables, Moderationsleitfaden, Playtest

**Abhängigkeit:** keine

---

## 1) Zielbild & Scope (Spielrahmen fixieren)

### 1.1 Zielgruppe und Lernziele
- [ ] Lernziele finalisieren (z. B. CIA-Trade-offs, Budgetlogik, RoS, Stakeholder-Kommunikation)
- [ ] Ziel-Spielzeit, Teamgröße, benötigte Moderationskompetenz
- [ ] Ziel-Setup festlegen: **3 Teams à 5 Personen**
- [ ] Raum-Setup definieren: Whiteboard-Flächen, Teams, Materialstation

**Abhängigkeit:** 0

### 1.2 Spielumfang (MVP vs. Ausbau)
- [ ] MVP festlegen: Anzahl Wellen, Anzahl Maßnahmenkarten, Anzahl Angriffe, Anzahl Eventtypen
- [ ] „Nicht-Ziele“ definieren (z. B. keine technischen Deep-Dives, keine Zufallsmechanik)

**Abhängigkeit:** 1.1

---

## 2) Mechanik-Spezifikation (Regeln als „Single Source of Truth“)

> Ergebnis dieser Phase: ein **Regelwerk**, das von Content + Moderation + Printables gleichermaßen genutzt wird.

### 2.1 State Machine und Rundenlogik
- [ ] State Machine finalisieren: Discovery → Budget → Maßnahmenwahl → Welle (Events+Angriffe+E-Ziel+OPEX/Recovery) → Change-Fenster → Abschluss
- [ ] Zeitpunkte definieren, ab wann Änderungen wirksam werden (z. B. „wirksam ab nächster Welle“)
- [ ] Offline-Logik: Welche Werte stehen permanent am Whiteboard, welche auf Papier je Team?

**Abhängigkeit:** 1

### 2.2 Formeln und Invarianten
- [ ] Deterministische Auflösung formal fixieren (Mitigation-Summe, Endschwere G, Damage, ΔKZ, CIA-Mali, Recovery)
- [ ] Klammerungen/Constraints definieren (z. B. KZ 0…100; G ≥ 0; Caps)
- [ ] **Papier-Rechenweg** definieren: Jede Berechnung muss als **Schrittfolge** auf einem Blatt abbildbar sein

**Abhängigkeit:** 2.1

### 2.3 Wirtschaftlichkeits-Logik
- [ ] Budgetkomponenten: Init vs. OPEX; wann wird was gezahlt
- [ ] RoS-Formel finalisieren inkl. „Basisverluste ohne Mitigation“ Definition
- [ ] Change-Gebühren / Straf-OPEX aus Events (falls genutzt)

**Abhängigkeit:** 2.2

### 2.4 Abhängigkeiten & Regeln für Maßnahmenlevel
- [ ] Abhängigkeitsmodell spezifizieren (Mindestlevel anderer Maßnahmen, harte vs. weiche Abhängigkeit)
- [ ] Regel, wie fehlende Abhängigkeiten behandelt werden (Blockieren? Abschwächung? KZ-Malus?)
- [ ] Offline-Darstellung: Abhängigkeiten müssen auf Karten **so klar** sein, dass keine App nötig ist

**Abhängigkeit:** 2.2

**Meilenstein M1:** Mechanik-Spezifikation ist „frozen“ (Änderungen nur via Change Request).

---

## 3) Datenmodell & Content-Bausteine (druckbar, aber konsistent)

> Auch ohne Software braucht ihr ein **konsistentes Datenmodell**: es lebt als Quelle in Text/Tabellen und wird als Karten/Sheets gedruckt.

### 3.1 Content-Bausteine definieren (Minimalstandard, ohne technische Festlegung)
- [ ] Festlegen, **welche Bausteine** das Spiel benötigt (z. B. Maßnahmen, Angriffe, Events, Wellen, Discovery-Hinweise)
- [ ] Für jeden Baustein einen **Minimalstandard** definieren: Welche Informationen müssen auf Karte/Sheet stehen, damit das Spiel offline deterministisch läuft?
  - Beispiele (nicht final, bewusst offen): Name, kurze Beschreibung, Wirkung/Trade-off, Kostenlogik, Abhängigkeiten/Voraussetzungen, Rechenhinweise
- [ ] Wichtig: **keine Festlegung auf Variablennamen oder technische Felder**, sondern auf **druckbare Inhalte** und **Rechenwege**

**Abhängigkeit:** 2

### 3.2 Konsistenzregeln & Qualitätschecks (ohne Engine)
- [ ] Konsistenzregeln dokumentieren (z. B. „jede Karte referenziert nur existierende Karten/Regeln“, keine widersprüchlichen Abhängigkeiten)
- [ ] Content-Review-Checklist erstellen (manuell); optional zusätzlich ein Skript/CI-Check für Redaktionsqualität (aber **nicht** für die Durchführung notwendig)
- [ ] Versionierung: Inhaltssatz (MVP) bekommt eine feste Versionsnummer, die auf allen Printables steht
- [ ] **Evaluation aufnehmen:** Welche Daten-/Dokumentationsform passt am besten (Markdown-Tabellen, Google Sheets nur zur Erstellung, InDesign, etc.) – Durchführung bleibt offline

**Abhängigkeit:** 3.1

**Meilenstein M2:** Erstes konsistentes Content-Format + Review-Checkliste.

---

## 4) Content-Produktion (Bibliothek: Maßnahmen, Angriffe, Events, Wellen)

> Ziel: ein **überschaubares, spielbares Set** (MVP), das realistisch wirkt und nicht „dominant strategies“ zulässt.

### 4.1 Maßnahmenkatalog (L1/L2/L3)
- [ ] Maßnahmenliste erstellen (z. B. IAM/PAM, Logging/SIEM/MDR, EDR/XDR, Backup/DR, Segmentierung/OT, Awareness, Supplier Security, Incident Response)
- [ ] Pro Maßnahme: Levelbeschreibung (L1/L2/L3), CIA-Beiträge, Mitigations, Abhängigkeiten, Kostenfelder
- [ ] Offline-Design: Werte/Regeln sind **auf Karten** und in **Tabellen** enthalten, keine Nachschlage-App

**Abhängigkeit:** 3

### 4.2 Angriffsset (Domänenbezug)
- [ ] Angriffe definieren (z. B. Ransomware IT, Phishing/BEC, OT-Störung MES/PLC, SaaS-Outage, Datenexfiltration IP, Supply-Chain)
- [ ] Pro Angriff: Impact-Profil (CIA), baseSeverity, Units, MitigationRefs, Sekundäreffekte
- [ ] Angriffskarten so gestalten, dass der Rechenweg eindeutig startbar ist (Inputs klar)

**Abhängigkeit:** 3

### 4.3 Events & Triggerlogik
- [ ] Eventtypen definieren (Zeit/Welle, Signalbasiert, Maßnahme-basiert, Teamentscheidung)
- [ ] Effekte festlegen (budgetDelta, kzDelta, severityMod, kzFactor, damageFactor, opexPenalty)
- [ ] Determinismus prüfen: Triggerbedingungen sind eindeutig aus State ableitbar

**Abhängigkeit:** 3

### 4.4 Wellen-Design (Szenario-Dramaturgie)
- [ ] Wellengewichte (wC/wI/wA) + E-Ziele definieren
- [ ] Angriffe und Events pro Welle zusammenstellen (MVP: wenige, klar unterscheidbar)
- [ ] Change-Fenster einplanen (was wird typischerweise erst ab Welle 2/3 relevant?)

**Abhängigkeit:** 4.1–4.3

**Meilenstein M3:** MVP-Content ist final (in Karten/Tabellen abbildbar).

---

## 5) Offline-Rechenhilfen & Formulare (Determinismus ohne digitale Tools)

> Ergebnis: **druckbare Rechen- und Auswertungsunterlagen**, die deterministische Ergebnisse liefern – mit klarer Aufgabenteilung:
> - **Teams** rechnen einfache Additionen/Subtraktionen selbst (Budget, laufende Kosten, einfache Summen).
> - **Spielleitung** übernimmt „Blackbox“-Berechnungen, wenn sie komplexer sind oder in Stresssituationen Fehler vermeiden sollen (z. B. Endschwere/Impact-Logik über Lookup-Tabellen).

### 5.1 Rechenpfad „Welle auflösen“ als Papier-Workflow
- [ ] Schrittfolge als 1-seitige Checkliste definieren:
  1) Events anwenden  
  2) Angriff(e) auflösen (Mitigation → Endschwere → Damage → CIA-Mali → ΔKZ)  
  3) E-Ziel prüfen (Bonus/Malus)  
  4) OPEX/Recovery/Change-Kosten buchen  
  5) State aktualisieren (Budget, KZ, aktive Maßnahmenlevel)
- [ ] Jeder Schritt bekommt Felder: **Input**, **Zwischenergebnis**, **Output**

**Abhängigkeit:** 2, 4

### 5.2 Lookup-Tabellen und Rechenhilfen (Fehlerarm, schnell, offline)
- [ ] Entscheiden, **welche Teile Teams selbst rechnen** (einfach) und **welche die Spielleitung** via Tabellen/Schablonen (Blackbox)
- [ ] Lookup-Tabellen entwerfen für die „Blackbox“-Teile (Beispiele, bewusst offen):
  - Wirkungsstärke aus Maßnahmen/Level-Kombinationen
  - Ableitung von Auswirkungen aus einem Schweregrad/Status
  - Recovery-/Folgekostenregeln
- [ ] Sonderfälle/Grenzwerte als klare Box („Wenn … dann …“), um Diskussionen zu vermeiden
- [ ] **Evaluation aufnehmen:** Welche Rechenhilfen sind für 3×5 Personen am praktikabelsten (A4-Tabellen, Drehscheibe, Karten-Overlays)?

**Abhängigkeit:** 2.2–2.3

### 5.3 Standard-Formulare (druckbar)
- [ ] Team-Board-Sheet (A4): Budget, KZ, Maßnahmenlevel, offene Abhängigkeiten, aktuelle Wellenwerte
- [ ] Wellenprotokoll (A4): Events, Angriffe, Rechenweg, Endwerte, Notizen für Debrief
- [ ] Maßnahmen-Auswahlbogen: pro Welle ausgewählte Maßnahmen/Level + Kostenaufschlüsselung
- [ ] Facilitator-Übersicht: „Master Sheet“ für alle Teams + Kontrollsummen

**Abhängigkeit:** 5.1–5.2

### 5.4 Whiteboard-Layout & Materiallogistik
- [ ] Whiteboard-Layout standardisieren (Vorlage als Druck/Foto-Guide):
  - Links: Wellenstatus (wC/wI/wA, E-Ziel, Events)  
  - Mitte: Team-Übersicht (Budget/KZ)  
  - Rechts: „Markt/Shop“ (Maßnahmenkarten, Preise, Abhängigkeiten)
- [ ] Materialpackliste: Karten-Sets, Marker, Post-its, Timer, Klemmbretter, Ersatzformulare

**Abhängigkeit:** 1.1, 5.3

**Meilenstein M4:** Offline-Berechnung funktioniert end-to-end mit Papier/Whiteboard.

---

## 6) Facilitator-Kit & Player-Material (spielbar machen)

### 6.1 Moderatorleitfaden
- [ ] Ablaufskript pro Phase (Discovery-Hinweislogik, Budgetverhandlung, Regeln, Trigger setzen)
- [ ] „Hinweise ohne Lücken zu nennen“: Beispielantworten und Signalzuordnung
- [ ] Transparenzregeln: welche Formeln offen gezeigt werden, wie Rechenwege erklärt werden
- [ ] Offline-Fehlerbehandlung: Was tun bei Rechenfehlern/Unklarheiten (Korrekturprotokoll)

**Abhängigkeit:** 2, 4, 5

### 6.2 Spielmaterial (druckfähig)
- [ ] Maßnahmenkarten (Beschreibung, Level-Effekte, Abhängigkeiten, Costs)
- [ ] Angriffskarten (Impact, Mitigationrefs, Narrative)
- [ ] Eventkarten (Trigger, Effekte, Begründung)
- [ ] Optional: „Discovery-Signal“-Karten (als Hinweis-Mechanik)

**Abhängigkeit:** 4, 5

### 6.3 Briefings & Debriefing
- [ ] Spielerbriefing (Ziel, Rollen, Regeln, Entscheidungslogik)
- [ ] Debriefing-Fragen entlang Lernziele (Trade-offs, Kommunikationsaspekte, RoS-Interpretation)
- [ ] Ergebnisdarstellung: wie Teams ihre KZ-/Budget-Entwicklung am Whiteboard präsentieren

**Abhängigkeit:** 1, 2, 5

**Meilenstein M5:** Vollständiges, durchführbares Offline-Spielpaket (MVP) inkl. Druckmaterial.

---

## 7) QA, Balance & Playtests (Determinismus + Spielbarkeit)

### 7.1 Determinismus-Tests (offline nachvollziehbar)
- [ ] Golden-Runs als **Papierbeispiele**: gleiche Inputs → identische Outputs
- [ ] Rechenweg-Audits: kann eine zweite Person die Welle nur mit Sheet+Karten reproduzieren?
- [ ] Edge-Cases: keine Maßnahmen, maximales Budget, minimale KZ, harte Abhängigkeitsverletzungen

**Abhängigkeit:** 5

### 7.2 Balance-Tests
- [ ] Dominanzanalyse: gibt es „immer beste“ Maßnahmen/Strategien?
- [ ] Parameter-Tuning (über Karten/Tabellen, nicht über Code) zur Korrektur
- [ ] Dramaturgie: Wellen sollen unterscheidbare Schwerpunkte haben (wC/wI/wA)

**Abhängigkeit:** 4, 5

### 7.3 Playtests (mit Beobachtungsbogen)
- [ ] 1 interner Playtest (Designer/Facilitator)
- [ ] 1 externer Playtest (Zielgruppe)
- [ ] Beobachtung: Verständlichkeit, Zeit, Entscheidungsstress, Moderationsaufwand
- [ ] Iteration: Issues priorisieren (Mechanik vs. Content vs. Material)

**Abhängigkeit:** 6

**Meilenstein M6:** MVP „classroom ready“ (rein offline).

---

## 8) Release & Betrieb (offline Distribution)

### 8.1 Versionierung & Changelog
- [ ] Versionierung für Content-Set und Printables (z. B. `v1.0-offline-mvp`)
- [ ] Changelog mit „Breaking Changes“ (z. B. neue Kartenfelder, geänderte Tabellen)

**Abhängigkeit:** 5, 7

### 8.2 Druckpaket & Distribution
- [ ] „Print Pack“ bündeln:
  - Karten (Maßnahmen/Angriffe/Events/Signale)  
  - Formulare (Team-Sheets, Wellenprotokolle, Master Sheet)  
  - Whiteboard-Layout-Guide  
  - Moderatorleitfaden + Quickstart
- [ ] Druckstrategie: **einmal drucken**, optional **selbst laminieren** (wiederverwendbar) – Layout entsprechend anlegen (Schwarzweiß, hohe Kontraste, dicke Linien)
- [ ] Schneide-/Laminierhinweise (falls genutzt): Kartengrößen, Randabstände, Markierungen
- [ ] Quickstart (10 Minuten) + Troubleshooting (häufige Fehler im Ablauf/Rechenweg)

**Abhängigkeit:** 6, 8.1

### 8.3 Backlog (Ausbau)
- [ ] Zusätzliche Szenarien (andere Branche, andere Wellengewichte)
- [ ] Erweiterte Eventbibliothek
- [ ] „Facilitator-Assist“ optional (rein zur Vorbereitung), aber **nicht erforderlich** für Durchführung
- [ ] Mehrsprachigkeit (DE/EN)

**Abhängigkeit:** M6

---

## Abhängigkeitsübersicht (High-Level)

1. **Mechanik spezifizieren** (M1)  
2. **Content-Standard + Review-Checks** (M2)  
3. **MVP-Content definieren** (M3)  
4. **Offline-Rechenhilfen/Formulare** (M4)  
5. **Facilitator-Kit + Druckmaterial** (M5)  
6. **QA/Balance/Playtests** (M6)  
7. **Print-Pack Release & Ausbau**  

---

## Festgelegte Rahmenbedingungen (aus eurem Input)

- **Team-Setup:** 3 Teams à 5 Personen  
- **Material:** einmal drucken, optional selbst laminieren  
- **Rechnen:** Teams übernehmen einfache Additionen/Subtraktionen; „Blackbox“-Berechnungen können durch die Spielleitung erfolgen, wo es sinnvoll ist.

---

## Evaluation-Punkte (bewusst offen halten)

1. **Rechentiefe vs. Spieltempo:** Welche Berechnungen lohnen als Blackbox-Tabellen, welche sollen Teams transparent selbst machen?
2. **Komplexität der Lookup-Tabellen:** Matrix/Mapping vs. vereinfachte Direktzuordnung – was ist in Playtests robuster?
3. **Materialdesign:** Einweg-Druck vs. Laminierung (Abwischbarkeit) – welche Artefakte profitieren am meisten (Karten, Team-Sheets, Whiteboard-Guide)?
4. **Moderationslast:** Reicht ein Facilitator für 3 Teams (parallel), oder braucht es Co-Facilitator/Timekeeper?

