
# CIA-Planspiel Automotive (deterministisch, konfigurierbar)

Ein **konfigurationsgetriebenes IT-Security-Planspiel** für einen Automotive-Zulieferer. Die Teilnehmenden agieren als Beratungsteams, **verhandeln ein Budget**, wählen **Sicherheitsmaßnahmen in Reifegraden (L1/L2/L3)**, reagieren auf **deterministische Events** und **Angriffe** und optimieren **Kundenzufriedenheit (KZ)**, **CIA-Ziele** und **Return on Security (RoS)**.

> **Wichtig:** Diese README hält sich **rein an die Funktion und das Spieldesign**.  
> Es werden **keine festen Zahlenvorgaben** (Werte/Variablen) gemacht. **Alle Parameter stehen in `simulation_config.json`**; Dauern, Budgets, Strafen und Anzahlen (Wellen, Teams, Debriefing-Stufen) stehen dort oder auf der gedruckten Seite, nicht hier.  
> Das Spiel wird nur mit Papier gespielt. Das gesamte Druckmaterial wird aus Konfiguration und Texten **erzeugt** (siehe „Druckmaterial erzeugen“).

---

## Ziele & Lernwerte

- **Determinismus statt Zufall:** Keine Würfel, keine Hidden-Randomness. Alle Ergebnisse sind **vorhersehbar** aus **Konfiguration + Entscheidungen** ableitbar.
- **Spieler-Agency:** Entscheidungen haben **sichtbare, nachvollziehbare Effekte** (KZ, CIA-Erfüllung, Schäden, RoS).
- **Realitätsnähe:** Maßnahmen, Abhängigkeiten, Events und Angriffe spiegeln gängige Security-Praxis in der **Fertigungs-/OT- und SaaS-Realität**.
- **Von Hand rechenbar:** Alle Formeln sind linear; die Spielleitung rechnet am Arbeitsblatt live nach.
- **Risikobasiert entscheiden:** Die Teams stellen aus dem Unternehmensprofil den Schutzbedarf ihrer Werte je Schutzziel C / I / A fest, leiten daraus ihre Risiken mit dem Schaden fürs Geschäft ab, wählen darauf ihre Maßnahmen und priorisieren mit dem Budget.

---

## Rollen

- **Beratungsteams:** Treffen Budget- und Maßnahmenentscheidungen, reagieren auf Events und Angriffe, setzen Changes im Change-Fenster um.
- **Spielleitung (Facilitator):** Spielt den Kunden, führt durch den Ablauf (Ablaufplan im Spielleitungs-Heft), gibt die Angriffsarbeitsblätter erst zu Beginn ihrer Welle aus, rechnet mit den Teams nach und leitet das Debriefing.
- Optional: **Attack/Rules Controller** (kann die Spielleitung mit übernehmen).

---

## Kernelemente (Objekte)

- **Budget (B):** Punkte für Erst-Invest (Init) und laufende Kosten (OPEX). Der Budgetrahmen hängt vom Budget-Tier ab (`budget_tiers`). Überziehung kostet linear KZ, siehe Budget Review.
- **Kundenzufriedenheit (KZ):** Skala mit fester Klammerung (0…100), Startwert je Tier, Effekte **linear und konfigurierbar**.
- **Maßnahmen (L1/L2/L3):**  
  - Attribute je Level: Init-Kosten, OPEX, CIA-Beiträge; dazu die Abhängigkeiten der Maßnahme.
  - **Level-Intuition:** L1 = Basis, L2 = Standard, L3 = erweitert. Stärkegrade sind **parametrierbar**.
- **Wellen (`waves`):** Jede Welle besitzt **Gewichte (wC, wI, wA)**, eine **E-Schwelle**, **Bonusmaßnahmen** (`bonus_measures`, thematisch passende Maßnahmen mit einem Bonus ab einem Mindest-Level) und genau einen **Angriff**.
- **Angriffe (`attacks`):** Grundschweregrad, Schaden je Stufe (`s_unit`), KZ-Änderung bei vollem Schaden und bei voller Abwehr (`kz_at_full_damage`, `kz_at_full_mitigation`), Deckel der Abwehr (`mitigation_cap`), CIA-Auswirkung (`cia_impact`) und ob Recovery wirkt (`allow_recovery`).
- **Events (`events`):** Regelbasierte Karten je Welle mit klaren Effekten: KZ-Änderung, Budgetänderung, OPEX-Rabatt oder -Zuschlag je aktiver Maßnahme, Bonus je Maßnahme ab einem Level, Staffeln nach Maßnahmenlevel, Checklisten-Staffeln sowie der Kurswechsel (Pflicht-Maßnahmentausch im Change-Fenster).
- **Abschluss-Event (`final_events`):** Das Budget Review mit Restbudget-Stufen und Überziehungsstrafe.
- **Story:** Unternehmenssteckbrief, Anfrage- und Audit-Mail sowie Zeitungsartikel geben den Teams die Hinweise, die sie für ihre Planung brauchen.

---

## Spielablauf (State-Machine)

Der Ablaufplan mit Blöcken, Dauern und Pausen steht in `session_schedule` und wird als Seite „Ablaufplan der Veranstaltung“ im Spielleitungs-Heft gedruckt; hier steht nur die Reihenfolge.

1. **Einführung (Intro)**  
   Das Intro-Deck erklärt Spielidee und Rollen.
2. **Story und Gruppenarbeit**  
   Teams lesen die Story-Dokumente und erhalten dazu das Teamheft. Auf seiner ersten Seite stellen sie den Schutzbedarf fest: Sie listen die Werte des Unternehmens und schätzen je Schutzziel C / I / A den Schaden fürs Geschäft als gering, mittel oder hoch; gesamt ist die höchste Stufe (Maximumprinzip). Im Risikoregister darunter zeigt jedes Risiko auf einen Wert und sein Hauptziel, sein Band steht in der Tabelle; die Teams vergeben einen Rang und entscheiden, welche Risiken sie behandeln oder akzeptieren. Die Spielleitung beantwortet Fragen **kontextbezogen** und benennt keine Lücken. Fragen die Teams je Wert und Schutzziel, was ein Schaden fürs Geschäft bedeuten würde, antwortet die Spielleitung als Geschäftsführung mit einem Band, nie mit einem genauen Betrag.
3. **Welle 0 (Übung)**  
   Ein durchgerechnetes Übungsbeispiel (`uebung-welle-0.pdf`) mit eigenen Werten aus dem Block `practice`; es zählt nicht für die Wertung.
4. **Budgetverhandlung und Maßnahmenwahl**  
   Teams einigen sich auf ein Budget-Tier, wählen Maßnahmen und **Level**. **Abhängigkeiten** werden geprüft, **OPEX** wird notiert. Freiwillig tragen sie je Maßnahme ein, gegen welche Risiken ihres Registers sie wirkt („gegen R#“); die Spalte wird nicht bewertet.
5. **Die Wellen**  
   Jede Welle: a) Events anwenden, b) den Angriff deterministisch auflösen (siehe „Deterministische Auflösung“), c) **OPEX** zahlen und **Erholung** anwenden (falls konfiguriert), d) Realitätscheck: In der letzten Zeile des Arbeitsblatts tragen die Teams ein, welches Risiko ihres Registers der Angriff getroffen hat, oder „nicht im Register“.
6. **Change-Fenster**  
   Nach jeder Welle außer der letzten: Levelwechsel, Kündigen, Hinzufügen (wirksam **ab der nächsten Welle**); nach der Kurswechsel-Welle zusätzlich der Pflicht-Maßnahmentausch.
7. **Abschluss und Budget Review**  
   Einmal nach der letzten Welle: Restbudget-Bonus oder Überziehungsstrafe, danach Klammerung der KZ. Dazu füllen die Teams die Spalte Rückblick im Risikoregister: Welches Risiko hat ein Angriff getroffen, und stimmte das Band aus der Schutzbedarfstabelle?
8. **Debriefing**  
   Feste Reihenfolge der Stufen (Reaktion, Beschreibung, Analyse, Anwendung) mit den Fragen der Seite „Debriefing-Fragen“ im Spielleitungs-Heft. Die Fragen folgen der Kette: Risikoregister gegen die Wirklichkeit, getroffene akzeptierte Risiken, der eigene Schutzbedarf nach Vertraulichkeit, Integrität und Verfügbarkeit gegen die Gewichtung der Wellen samt der Wahl des Hauptziels, wo sich das Geld ausgezahlt hat (RoS), Übertrag auf echtes Risikomanagement. Wenn Zeit bleibt, folgt ein kurzer Management-Pitch je Team ohne eigene Richtzeit.

> **Hinweis:** Anzahl der Wellen, Events und der Blöcke des Ablaufs sind in der Konfiguration festgelegt.

---

## Story, Hinweise und Schleier

- **Schleier:** Vor der Welle bleiben die Angriffe verschleiert. Den Namen und die genauen Werte eines Angriffs erfahren die Teams erst, wenn seine Welle läuft (Angriffsarbeitsblatt). Die Mechanik selbst ist immer transparent: Formeln, Gewichte und Schwellen sind offen.
- **Hinweise statt Lücken:** Die Story-Dokumente enthalten Hinweise, die auf die späteren Angriffe zeigen, ohne eine Lücke zu benennen. Die **Hinweis-Matrix** im Spielleitungs-Heft zeigt, welcher Angriff aus welchen Dokumenten erschlossen werden kann.
- **Pflege:** Die Zuordnung liegt in `content/clues.toml`. `uv run planspiel clues` zeigt die Matrix und prüft sie: Jeder Angriff braucht Hinweise aus mehreren Dokumenten.
- **Mini-Tipps:** Die Spielleitung gibt **kontextuelle Hinweise** („Wiederanlauf steigert Lieferfähigkeit“), **ohne** konkrete Lücken zu benennen.

---

## Maßnahmen (L1/L2/L3) & Abhängigkeiten

- **Level-Wirkung (funktional):**
  - **CIA-Beiträge:** L1 < L2 < L3 (Steigerungskurven frei konfigurierbar). Die Summe der Beiträge über alle aktiven Maßnahmen ergibt das Team-CIA.
  - **Bonus je Welle:** Jede Welle hat Bonusmaßnahmen, die ab einem Mindest-Level einen Bonus zur Gesamtreduktion beitragen.
- **Abhängigkeiten (Beispiele, inhaltlich realistisch; Werte/Level frei):**
  - EDR/XDR auf hohem Level verlangt ein Mindest-Level bei SIEM/MDR.
  - PAM auf hohem Level verlangt ein Mindest-Level bei Asset-/CMDB.
  - Backups mit hohem Schutzgrad empfehlen Mindest-Level bei DR/BCP.
  - OT-Allow-Listing ist wirksamer in Kombination mit Netzsegmentierung.
- **Breite statt Monokultur:** Das Design belohnt **breite Abdeckung** über **einseitige Maximierung**.

---

## Events (regelbasiert)

- **Trigger:** Welle, in der die Karte gezogen wird, und der Stand der Maßnahmen (aktiv oder nicht, Mindest-Level, Level-Staffel).  
- **Effekt-Typen:** KZ-Änderung, Budgetänderung, OPEX-Rabatt je aktiver Maßnahme, KZ-Bonus je Maßnahme ab einem Level, Staffeln und Checklisten nach Maßnahmenlevel sowie der Kurswechsel.  
- **Karten:** Jede Eventkarte nennt ihre Welle („Event in Welle N“).  
- **Planbarkeit:** Alle Events ergeben sich **deterministisch** aus dem Stand der Maßnahmen, **keine Überraschungen** bei sorgfältiger Planung.

---

## Angriffe (konfigurierbar)

- **Felder:** `base_severity`, `s_unit`, `kz_at_full_damage`, `kz_at_full_mitigation`, `mitigation_cap`, `cia_impact`, `allow_recovery`; je Welle zusätzlich Gewichte, E-Schwelle und Bonusmaßnahmen (`waves`).  
- **Beispiele (Domänenbezug):** Ransomware (Office-IT), OT-Netzstörung (MES/PLC), Datenexfiltration (IP).  
- **Domänenlogik:** Jeder Angriff adressiert **primär** eines der CIA-Ziele, kann aber **sekundäre** Effekte auf andere haben; die Gewichte der Welle bilden das ab.

---

## Deterministische Auflösung (Formeln, symbolisch)

> Alle Variablen sind **konfigurierbar**; die Formeln bleiben **fix** und **linear**.

- **E-Wert:** `E-Wert = Team_C * wC + Team_I * wI + Team_A * wA`
- **Gesamtbonus:** Summe der Boni der Bonusmaßnahmen der Welle, die ihr Mindest-Level erreichen.
- **Gesamtreduktion:** `Gesamtreduktion = E-Wert + Gesamtbonus`
- **Reduktion über Schwelle:**  
  `Reduktion über Schwelle = min(mitigation_cap, max(0, Gesamtreduktion − e_threshold))`  
  Das sind die Fälle des Arbeitsblatts: Fall 1 (Gesamtreduktion höchstens Schwelle: keine Reduktion), Fall 2 (zwischen Schwelle und Deckel) und Fall 3 (Deckel erreicht).
- **Schweregrad:**  
  `Schweregrad = max(0, base_severity * severity_multiplier − Reduktion über Schwelle)`
- **Schaden:**  
  `Schaden = Schweregrad * s_unit`, wenn der Angriff `allow_recovery` erlaubt, zusätzlich `* (1 − Recovery)`; Recovery ist der höchste Recovery-Wert (je Level in der Maßnahme) unter den aktiven Maßnahmen.
- **KZ-Änderung des Angriffs (linear interpoliert):**  
  `KZ-Delta = kz_at_full_damage + (Reduktion über Schwelle / mitigation_cap) * (kz_at_full_mitigation − kz_at_full_damage)`
- **Rundung (wie auf Papier):** Die KZ-Änderung je Welle (Angriff + Events) wird genau einmal auf eine ganze Zahl gerundet, ab ,5 vom Betrag aufgerundet (+2,5 → +3, −2,5 → −3); danach wird die KZ auf 0–100 begrenzt. E-Wert, Gesamtreduktion, Reduktion über Schwelle und Schweregrad bleiben exakt; der Schaden bleibt exakt in ganzen Euro.
- **Erholung (Ende Welle):** Der **Recovery-Wert** der Maßnahme (z. B. Backups/DR, je Level konfiguriert) reduziert den Schaden um einen **konfigurierbaren Anteil**, sofern der Angriff Recovery erlaubt.

---

## Wellen-Ziel (E-Wert) & Scoring

- **Team-CIA:** `Team_C`, `Team_I`, `Team_A` = Summe der Maßnahmen-CIA.  
- **E-Schwelle:** pro Welle konfigurierbar; nur die Gesamtreduktion (E-Wert + Gesamtbonus) oberhalb der Schwelle mindert den Angriff. Einen eigenen KZ-Bonus/Malus für ein E-Ziel gibt es nicht.
- **Return on Security (RoS):**
Gesamtkosten  = eigene Sicherheitsausgaben = Σ Init + Σ Init-Differenzen aus Hochstufungen und neuen Maßnahmen im Change-Fenster + Σ OPEX je Welle (Level der jeweiligen Welle) + Kurswechsel-Differenz
Verluste      = Sum(Damage über alle Angriffe)
Vermeidete Verluste = Sum(Basisverluste ohne Mitigation) − Verluste
RoS           = (Vermeidete Verluste − Gesamtkosten) / Gesamtkosten

Nicht enthalten: Event-Effekte auf Kosten oder Budget (Straf-OPEX, OPEX-Rabatte wie „Operative Unterstützung“, Budget-Kürzungen wie „Sparprogramm“); sie zählen nur für das Budget.

Lesart: Die RoS zeigt, wie viel Schaden jeder investierte Euro über seine eigenen Kosten hinaus verhindert hat; liegt sie über null, hat die Sicherheit mehr Schaden verhindert, als sie gekostet hat.

- **Final-Index:** Der Vergleichswert für die Spielleitung über Teams und Tiers ist `weight_kz * KZ + weight_ros * RoS₂`; RoS₂ ist die RoS auf zwei Nachkommastellen gerundet (ab ,5 vom Betrag aufrunden). Die Gewichte stehen im Config-Block `final_index`; das Teamheft führt die RoS-Seite, das Debriefing vergleicht die Teams anhand von KZ, RoS und Final-Index.

---

## Change‑Fenster (Planbarkeit + Agency)

- **Zeitpunkt:** Zwischen zwei Wellen. Nach der letzten Welle gibt es kein Change‑Fenster.  
- **Erlaubte Züge** (beliebig viele, nur das Budget begrenzt): Levelwechsel hoch, Levelwechsel runter, Maßnahme kündigen (Levelwechsel auf Level 0) und neue Maßnahme hinzufügen. Einen freien Maßnahmentausch gibt es nicht: Kündigen und Hinzufügen sind zwei getrennte Züge. Den Maßnahmentausch gibt es nur durch den Kurswechsel (siehe unten).  
- **Kosten:** Hochstufen und Hinzufügen kosten die **Init‑Differenz** (neue Maßnahme: das volle Init des gewählten Levels). Je Maßnahme zählt nur die **Netto‑Änderung** im Fenster: Init auf dem Level am Fensterende minus Init auf dem Level am Fensteranfang, wenn das positiv ist. Runterstufen und Kündigen **erstatten nie** Init. Züge kosten keine zusätzliche Gebühr.  
- **Wirkung:** Init‑Differenzen werden sofort im Fenster gebucht. CIA‑Werte, Boni, Level‑Effekte und das OPEX des neuen Levels gelten ab der nächsten Welle.  
- **Abhängigkeiten:** Nach jedem Fenster müssen alle Abhängigkeiten erfüllt sein, mit derselben Prüfung wie zu Spielbeginn. Wer eine Abhängigkeit bricht, passt die abhängige Maßnahme im selben Fenster an.

### Begriffe: Levelwechsel und Maßnahmentausch

- **Levelwechsel:** dieselbe Maßnahme, anderes Level, hoch oder runter. Kündigen ist ein Levelwechsel auf Level 0. Eine neue Maßnahme hinzufügen ist ein eigener Zug.
- **Maßnahmentausch:** eine Maßnahme raus, eine andere rein. Es gibt ihn nur durch das Event Kurswechsel. Der Begriff ersetzt den früheren MHP‑Begriff „Maßnahmenwechsel“.

### Kurswechsel (Maßnahmentausch)

- **Wirkung:** Im Change‑Fenster nach der Welle mit dem Event Kurswechsel führt jedes Team **genau einen Maßnahmentausch** durch, zusätzlich zu allen normalen Levelwechseln und neuen Maßnahmen dieses Fensters.
- **Was getauscht wird:** Die wegfallende Maßnahme war in der Kurswechsel‑Welle aktiv und endet auf Level 0. Die neue Maßnahme war in der Kurswechsel‑Welle nicht aktiv (kein Kündigen und Wiederaufnehmen im selben Fenster) und kann auf jedem Level starten.
- **Kosten:** Das Team zahlt **max(0, Init neu − Init weg)**. Init weg ist das Init der wegfallenden Maßnahme auf ihrem Level in der Kurswechsel‑Welle, Init neu das Init der neuen Maßnahme auf ihrem gewählten Level. Der Kunde übernimmt die Init‑Kosten der neuen Maßnahme also bis zur Höhe der wegfallenden. Eine günstigere neue Maßnahme bringt **keine Erstattung**. Das ist der einzige Fall, in dem das Init einer wegfallenden Maßnahme angerechnet wird; sonst wird Init nie erstattet. Der vom Team gezahlte Mehrbetrag zählt als eigene Ausgabe im RoS. Die OPEX der wegfallenden Maßnahme entfällt, die der neuen zahlt das Team ab der nächsten Welle.
- **Abhängigkeiten:** Hängen andere Maßnahmen von der wegfallenden ab, senkt oder kündigt das Team sie im selben Fenster passend, denn nach jedem Fenster müssen alle Abhängigkeiten gültig sein. Die Simulation senkt dafür minimal ab: jede betroffene Maßnahme auf das höchste Level, dessen Abhängigkeiten noch erfüllt sind.
- **Kein Tausch möglich:** War in der Kurswechsel‑Welle keine oder jede Maßnahme aktiv, entfällt der Tausch für das Team. Normale Züge im Fenster bleiben erlaubt.
- **Platzierung:** Es gibt höchstens einen Kurswechsel, und nicht in der letzten Welle, weil danach kein Change‑Fenster folgt.
- **Maßgeblich:** Die Beschreibung des Events in der Config und dieser Abschnitt; die alte Erstattung der Differenz gibt es nicht mehr.

---

## Budget Review und Überziehung

- **Zeitpunkt:** Das Restbudget (Budget + Budget‑Änderungen durch Events − eigene Kosten − Event‑OPEX) wird **einmal** geprüft, nach der letzten Welle. Zwischenstände unter null sind während des Spiels erlaubt.
- **Restbudget ≥ 0:** KZ‑Bonus nach den Restbudget‑Stufen aus der Config.
- **Stufengrenzen:** Eine Restbudget‑Stufe gilt ab ihrem Mindestbetrag einschließlich („ab …“). Die Kartentexte werden aus der Stufenliste der Konfiguration erzeugt (`planspiel.review_text.boundary_text`), nie von Hand geschrieben; dieselbe Liste nutzt die Simulation.
- **Restbudget < 0 (Überziehung):** −X KZ **je angefangene Schrittweite** Überziehung. X (`overspend_penalty.kz_per_step`) und die Schrittweite (`overspend_penalty.step`) stehen in der Config; X ist so kalibriert, dass sich Überziehen auch auf den Spielpfaden nie lohnt (siehe unten). Auf der Eventkarte „Zum Abschluss“ steht nur die Regel „je angefangene Schrittweite“; eine Nachschlagetabelle gibt es nirgends (`planspiel.review_text.penalty_rows` rechnet die Strafe für die Prüfungen nach).
- **Nur auf der Eventkarte:** Das Budget Review ist ein Event. Restbudget‑Stufen und Überziehungsregel stehen allein auf der Eventkarte „Zum Abschluss“, die erst am Ende ausgegeben wird; das Teamheft führt nur durch die Rechnung des Restbudgets und lässt eine Zeile für die KZ‑Änderung von der Eventkarte frei. Kein Spielerdokument außer dem Kartenspiel der Events nennt Stufen oder Strafe; die Unterlagen der Spielleitung dürfen sie nennen.
- **Begrenzung:** Nach dem Budget Review wird die KZ auf 0–100 begrenzt; weitere Überziehung senkt sie dann nicht unter null.
- **Event‑induzierte Überziehung:** Events wie das Sparprogramm können ein Team zwischenzeitlich über das Budget bringen. Im folgenden Change‑Fenster kann es durch Herabstufen oder Kündigen zurück ins Budget kommen; das spart nur OPEX späterer Wellen, Init wird nie erstattet. Bestraft wird nur, wer am Ende noch überzogen hat. Eine Budgetkürzung in der letzten Welle sollte es nicht geben, weil danach kein Change‑Fenster mehr folgt (der Validator warnt).
- **Überziehen lohnt sich nie (automatisch geprüft):** Zu jedem Plan über Budget gibt es eine gekürzte Version – nur Level gesenkt oder Maßnahmen gekündigt, im Budget –, die eine höhere End‑KZ erreicht. `uv run planspiel gate` prüft das je Tier auf dem Referenzplan ohne Change‑Fenster‑Züge, nennt das nötige X und den Plan, der es bestimmt; `uv run planspiel gate --paths` prüft zusätzlich die legalen Spielpfade (Tausch‑Schicht, Tausch mit einem Zug im Fenster nach Welle 2 und, wo kein Tausch möglich ist, je ein Zug im Fenster nach Welle 1 oder 2) und nennt das X, das sich aus allen Tiers und Familien ergibt (kalibriert heißt: größtes nötiges X plus 1).

---

## Spielbarkeit & Moderation

- **Einfachheit wahren:**  
  - Beschränke Maßnahmenkarten, Angriffe und Events auf ein **überschaubares Set** (alles konfigurierbar).  
  - **Transparenz:** Formeln und Trigger offenlegen; Effekte **kurz begründen** („E-Wert + Gesamtbonus − Schwelle ⇒ Reduktion ⇒ Schweregrad“).
- **Hinweise:** Immer **kontextualisiert** (Zielbild), niemals **Lücke benennen**; der Schleier vor den Angriffen bleibt bis zu ihrer Welle bestehen.
- **Realitätsnähe:** OT-Abhängigkeiten, SaaS-Prozesse, Lieferkette, Identity/Logging/Backups in stimmigen Relationen halten (über Parameter).
- **Probelauf:** Vor der Veranstaltung führt die Spielleitung den Ablauf allein nach den ausgedruckten Unterlagen durch und trägt Zeiten, Unklarheiten und Rechenfehler in das Probelauf-Protokoll ein.

---

## Spielmaterial (erzeugt)

Alle Dateien liegen als PDF in `final_documents/generated/` und werden aus `simulation_config.json` und `content/texte.toml` erzeugt, nie von Hand gepflegt. Die Druckliste im Spielleitungs-Heft nennt je Datei, wie oft sie für jedes Team und für die Spielleitung gedruckt wird.

**Für die Teams:**

- `spieler-teamheft.pdf`: Teamheft mit der Schutzbedarfstabelle (Werte aus der Story, je Schutzziel C / I / A gering, mittel oder hoch mit den € Bändern, gesamt nach dem Maximumprinzip) und dem Risikoregister (Risiken mit Wert W#, Hauptziel, Folge fürs Geschäft, Rang, behandeln oder akzeptieren und Rückblick; das Band jedes Risikos steht in der Tabelle), Budget und Planung, einer Tracking-Seite je Welle und der Seite zu RoS und Budget Review. Es ersetzt die früheren Auswertungstabellen.
- `spieler-massnahmenkarten.pdf` und `spieler-eventkarten.pdf`: die Karten, Werte und Texte aus der Konfiguration.
- `spieler-so-funktioniert-eine-welle.pdf`: die Erklärseite zum Ablauf einer Welle.
- `spieler-unternehmenssteckbrief.pdf`, `spieler-anfrage-mail.pdf`, `spieler-audit-mail.pdf`, `spieler-zeitungsartikel.pdf`: die Story-Dokumente mit den Hinweisen.
- `uebung-welle-0.pdf`: das durchgerechnete Übungsblatt für Welle 0.
- `angriff-1_ransomware.pdf`, `angriff-2_ot.pdf`, `angriff-3_exfil.pdf`: die Angriffsarbeitsblätter mit den Rechenschritten der Auflösung. Sie werden erst zu Beginn ihrer Welle ausgegeben.

**Nur für die Spielleitung (nicht an Teams ausgeben):**

- `spielleitung-uebersicht.pdf`: das Spielleitungs-Heft mit Ablaufplan, Druckliste, Kennwerten, Prüfzeilen, Lösungsschlüsseln, Debriefing-Fragen, Antworten zu Geschäftsfolgen (Band und Schutzziel je Fall) und der Hinweis-Matrix.
- `spielleitung-was-ist-neu.pdf`: das Blatt „Was ist neu“ für Spielleitungen der MHP-Runde mit den geänderten Regeln, dem geänderten Ablauf, dem neuen Material und der Gegenüberstellung alter und neuer Werte. Die alten Werte stammen aus `content/mhp_baseline.json`, dem eingefrorenen Stand der MHP-Runde; nur dieses Blatt liest die Datei.
- `spielleitung-probelauf.pdf`: das Probelauf-Protokoll.

---

## Parametrisierung (ohne feste Zahlen)

> Alle Werte sind **frei wählbar** und stehen an einer Stelle: `simulation_config.json`.

- **Budget-Tiers** (`budget_tiers`): Budget, KZ-Startwert und Schweregrad-Multiplikator je Tier.
- **Wellen** (`waves`): Gewichte (wC, wI, wA), E-Schwelle und Bonusmaßnahmen.
- **Angriffe** (`attacks`): Grundschweregrad, Schadenseinheit, KZ-Endpunkte, Deckel der Abwehr, CIA-Auswirkung, Recovery.
- **Maßnahmen** (`measures`): Init, OPEX, CIA-Beiträge und Recovery je Level sowie die Abhängigkeitsmatrix.
- **Events** (`events`) und **Abschluss-Event** (`final_events`): Effekte, Staffeln, Restbudget-Stufen und die Überziehungsstrafe `overspend_penalty` (X je angefangene Schrittweite).
- **Final-Index** (`final_index`): Gewichte von KZ und RoS.
- **Übung** (`practice`): die Werte des Übungsblatts für Welle 0.
- **Veranstaltung** (`session_schedule`): Blöcke mit Dauern, Teamzahl, Personen je Team, Druckliste, Debriefing-Stufen und die Redezeit des optionalen Management-Pitches.
- **Schutzbedarf und Register** (`risk_matrix`, der Name des Blocks ist historisch): Zahl der Zeilen der Schutzbedarfstabelle (`asset_rows`) und des Risikoregisters (`register_rows`), dazu die Untergrenzen der € Bänder gering, mittel und hoch. Die Bänder steigen streng an, und kein ungeschützter Angriffsschaden liegt auf einer Bandgrenze. Dazu kommen die Geschäftsfälle der Spielleitung mit Band und Schutzziel (c, i, a); ein Fall, der der Folge eines Angriffs entspricht, trägt dessen Band, und sein Schutzziel ist eines der am stärksten getroffenen Schutzziele dieses Angriffs. Jedes Schutzziel c, i und a hat mindestens einen Fall.
- **Referenzpläne** (`reference_plans`) und **Referenzstrategien** (`reference_strategies`): Grundlage der Lösungsschlüssel und der Balance-Prüfungen.
- **Prosa** liegt in `content/texte.toml`; Ziffern in dieser Prosa sind nur erlaubt, wenn sie in `content/digit_allowlist.toml` stehen. `content/clues.toml` ordnet die Hinweise den Angriffen zu, `content/mhp_baseline.json` hält den eingefrorenen Stand der MHP-Runde.

> **Empfehlung:** Beginne mit **wenigen** Maßnahmen/Angriffen/Events und **skaliere** bei Bedarf.

---

## Druckmaterial erzeugen

**Reihenfolge einer inhaltlichen Änderung:** `simulation_config.json` → `README.md` → `content/texte.toml` → `uv run planspiel print` → `uv run planspiel print --check` → `final_documents/generated/` committen. Zahlen stehen nur in der Konfiguration; die Texte und das Material ziehen nach.

```
uv run planspiel validate
uv run planspiel texts
uv run planspiel clues
uv run planspiel print
uv run planspiel print --check
```

- `validate` prüft die Konfiguration (Struktur, Handrechenbarkeit, Ablaufplan); `texts` prüft `content/texte.toml` (Abdeckung, Ziffern, Story-Regeln); `clues` zeigt und prüft die Hinweis-Matrix.
- `print` baut alle PDFs (LaTeX, LuaLaTeX über MiKTeX) in `final_documents/generated/` und schreibt eine `manifest.json`. Jede Datei trägt einen Stand-Stempel („Stand Datum · Hash“); auf einem Arbeitsstand mit lokalen Änderungen an einer Eingabe endet er auf „+lokal“. Solche Stände sind nicht zum Committen gedacht.
- `print --check` baut kein TeX, sondern prüft, ob die eingecheckten PDFs zum aktuellen Stand von Konfiguration, Texten und Vorlagen passen (Exit 0 aktuell, 1 veraltet, 2 Umgebungsfehler).
- Die Angriffsarbeitsblätter, Kartensätze, das Übungsblatt und das Spielleitungs-Heft haben keinen zweiten, von Hand gepflegten Stand. Das Intro-Deck und die Firmenfolien in `final_documents/` sind Eingaben der Veranstaltung, keine erzeugten Dateien.
- **Tests:** `uv run pytest` (schnell); Marker `pdf` baut echte PDFs (`uv run pytest -m pdf`), `slow` rechnet die volle Enumeration (`uv run pytest -m slow`), `balance` prüft die Design-Prinzipien einer Konfiguration (`uv run pytest tests -m balance`).
- Die früheren Druckstände der MHP-Runde und die alten Generator-Skripte liegen unter `archive/` und gehen nicht in den Bau ein.

---

## Qualitätssicherung (ohne Zufall, ohne Komplexität)

- **Determinismus prüfen:** Gleiche Inputs führen zu gleichen Outcomes.  
- **Balance testen:** Keine einzelne Maßnahme/Strategie darf **dominant** sein (siehe Balance-Bericht unten).  
- **Realitätscheck:** Mapping zu echten Szenarien (OT-Stillstand, Exfil, Ransomware) plausibel?  
- **Handrechnung:** Die Werte auf den Angriffsarbeitsblättern müssen von Hand nachrechenbar bleiben; das ist ein hartes Designkriterium.  
- **Spielzeit & Verständlichkeit:** Der Probelauf bestätigt, dass der Ablaufplan trägt und die Unterlagen ohne Rückfragen reichen.

---

## Simulation (alle Outcomes)

Für eine vollständige, deterministische Enumeration aller möglichen Outcomes gibt es eine kleine Simulation. Die Regeln folgen den Parametern aus der `simulation_config.json`, inklusive Abhängigkeiten, Events, CIA‑Gewichtung und Angriffsauswertung.  

**Setup (einmalig):** `uv sync` installiert die verwaltete Python-Version (3.12) und alle Abhängigkeiten exakt aus `uv.lock`. Alle Befehle laufen über `uv run` – unabhängig davon, welches `python` auf dem PATH liegt. Tests: `uv run pytest`.

**Zusammenfassung (Standardlauf):**
```
uv run python simulate_outcomes.py --config simulation_config.json --budget-tier medium
```

Der Standardlauf bewertet jede gültige Kombination des Tiers, auch die über Budget, und schreibt `simulation_summary_medium.json` (anderer Pfad über `--summary`) sowie eine kurze Konsolentabelle: Top-K (Standard 10, `--top K`) nach End-KZ, RoS und Final-Index, Perzentile (Nearest-Rank) von KZ und RoS getrennt nach im/über Budget, das beste Ergebnis im Budget gegenüber dem besten über Budget (End-KZ) und die Pareto-Front End-KZ gegen eigene Kosten. Definitionen: "über Budget" heißt Init + OPEX × Wellen + Event-OPEX > Budget + Event-Budget; "eigene Kosten" sind Init + OPEX je Welle (plus Init-Differenzen bei Change-Fenster-Zügen), ohne Event-Effekte; der RoS rechnet nur mit den eigenen Kosten und ist bei eigenen Kosten 0 nicht definiert (n/a). Alle Tiers nacheinander:
```
for t in low medium high; do uv run python simulate_outcomes.py --budget-tier $t; done
```

**Referenzplan:** Die Enumeration bewertet den **Referenzplan ohne Change‑Fenster‑Züge**: Der Plan der ersten Welle bleibt unverändert, der Kurswechsel wird nicht angewendet. Das ist nur für Pläne ein legales Spiel, bei denen kein Maßnahmentausch möglich ist; die besten Werte sind Referenzwerte und keine erreichbaren Spielergebnisse. Konsole, Summary‑JSON (`layer`, `layer_label`), Balance‑Report und Legacy‑Auswertung tragen dieses Label.

**Tausch‑Schicht (legales Minimum):**
```
uv run planspiel tausch --tier medium
```

Die Tausch‑Schicht bewertet jeden gültigen Plan der ersten Welle mit jedem legalen Maßnahmentausch des Kurswechsels (sonst unverändert; Pläne, bei denen kein Tausch möglich ist, wie sie sind). Die abhängigen Maßnahmen der wegfallenden Maßnahme werden dabei minimal abgesenkt; weitere Züge im Fenster werden nicht durchprobiert. Sie schreibt `simulation_summary_tausch_<tier>.json` und beschriftet ihre Zahlen mit „Pflicht‑Maßnahmentausch (Kurswechsel), legales Minimum“. Ohne `--tier` laufen alle Tiers der Konfiguration; `--summary-dir` wählt das Zielverzeichnis. Einzelne Spielpfade mit beliebigen Zügen wertet `planspiel.rules.evaluate_path` exakt aus.

**Überziehungs‑Gate:**
```
uv run planspiel gate --tier medium
```

Das Gate vergleicht je Tier jeden Plan über Budget mit seiner besten gekürzten Version (nur Level gesenkt oder Maßnahmen gekündigt, im Budget, inklusive der positiven Budget‑Review‑Stufe) auf dem Referenzplan ohne Change‑Fenster‑Züge. Es nennt das nötige X (strikt: jeder Plan über Budget verliert; schwach: Gleichstand erlaubt), zählt Pläne, die nicht verlieren können (gekürzte Version endet bei KZ 0) oder nicht kürzbar sind, und endet mit Fehlercode 1 samt dem bestimmenden Plan, wenn das X der Konfiguration zu klein ist. Ohne `--tier` laufen alle Tiers der Konfiguration.

```
uv run planspiel gate --paths [--narrow] [--jobs N]
```

Mit `--paths` prüft das Gate zusätzlich vier Pfadfamilien je Tier: die Tausch‑Schicht (Pflicht‑Maßnahmentausch, legales Minimum), den Pflicht‑Tausch mit einem freiwilligen Zug im Fenster nach Welle 2 (die Form der Referenzpfade) sowie einen einzelnen Zug im Fenster nach Welle 1 oder nach Welle 2 ohne Tausch. Die beiden letzten Familien gehen nur von Startplänen aus, in denen kein Tausch möglich ist; sonst ist der Tausch Pflicht und ein Zug ohne ihn kein legaler Pfad. Mehrere Züge in einem Fenster, Züge in beiden Fenstern und ein zusätzlicher Zug im Tausch‑Fenster prüft das Gate nicht; der Bericht nennt diese Lücke. Die gekürzte Version eines Pfads über Budget entsteht so: Startplan senken oder Maßnahmen kündigen, danach jede legale Fortsetzung der Familie. Das Debriefing dazu: „Hätte das Team zu Spielbeginn weniger oder niedrigere Maßnahmen gewählt, wäre es im Budget geblieben und besser gelandet.“ Je Familie nennt der Bericht das nötige X roh (Strafe ohne Untergrenze) und gekappt (KZ nach der Strafe auf 0–100 begrenzt, wie im Budget Review), die Verteilung, den bestimmenden Pfad sowie die Zahl der nicht verlierbaren und nicht kürzbaren Pfade. `--narrow` zeigt zusätzlich die enge Kürzung (gleiches Tauschpaar, Startplan und Level der neuen Maßnahme nur gesenkt) als Diagnose; sie geht nie in das Urteil ein. `--jobs N` rechnet die Tiers in bis zu N Prozessen. Die Kalibrierung lautet: **X = größtes nötiges X über Tiers und Familien + 1**; der Bericht endet mit dieser Empfehlung und nennt Tier und Familie, die sie bestimmen. Mit `--tier` (Teilmenge der Tiers) entfällt die Kalibrierung, weil X das Maximum über alle Tiers ist.

**Balance‑Bericht (alle Prüfungen in einem Lauf):**
```
uv run python balance_analysis.py [--config simulation_config.json] [--content-dir content]
uv run python balance_analysis.py --layers all --paths --jobs 3 --out build/balance
uv run python balance_analysis.py --config <kandidat.json> --baseline-config simulation_config.json --layers all --paths --jobs 3
```

`balance_analysis.py` wertet eine Konfiguration samt Inhalten über die volle Enumeration aus und druckt je Tier einen Bericht (Top‑K nach End‑KZ, RoS und Final‑Index sowie Pareto‑Front, jeweils über alle Kombinationen und nur im Budget, daneben die Optima im Budget und über Budget, Perzentile, Überziehungs‑Gate) und darüber hinaus die Blöcke über alle Tiers: Streuung, Entscheidungen, Final‑Index‑Gewicht, Handrechen‑Prüfung, Referenzstrategien samt Hinweis‑Zuordnung, Belohnung und, mit `--paths`, die Pfad‑Gates mit der Kalibrierung von X. Jeder Block nennt sein Urteil und seine Fehlerzeilen; der Exit‑Code ist 0 nur, wenn jede berechnete Prüfung besteht. `--layers static` (Standard) rechnet die statische Enumeration und das statische Gate (einige Minuten für drei Tiers mit `--jobs 3`); `--layers all` ergänzt die Tausch‑Schicht und alles, was von ihr abhängt. Teile, die ein Lauf nicht berechnet, sind benannt und zählen nicht zum Gesamturteil; mit `--tier` (Teilmenge der Tiers) gilt das für die Vergleiche zwischen den Tiers (Korridor und Unterschied des Interquartilsabstands, Entscheidungen zwischen den Tiers, Final‑Index‑Gewicht, Kalibrierung von X). Mit `--out <verzeichnis>` entstehen `balance_report.json` und `balance_report.txt` (ohne Angabe wird nichts geschrieben; `build/` ist nicht versioniert). Mit `--baseline-config` zeigt der Bericht zusätzlich jede geänderte Stelle der Konfiguration (JSON‑Pfad, alt, neu) und eine Vorher‑nachher‑Tabelle der Kennzahlen; die Final‑Index‑Kennzahlen beider Spalten nutzen dabei das k der Kandidatenkonfiguration. Das ist der Vergleich für den Abnahme‑Checkpoint der Abstimmung.

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

**Legacy-Vollausgabe mit Mindestkosten:**
```
uv run python simulate_outcomes.py --config simulation_config.json --budget-min 300 --output simulation_results.json
```

Es gibt keinen Auslastungsfilter: Die Ausgabe enthält jede Kombination im Budget, auch die mit geringer Auslastung. Die harte Obergrenze ist das Tier-Budget inkl. Event-Budget; `--budget-min` wirkt nur zusammen mit `--output`.

**Auswertung der Simulationsergebnisse:**
```
uv run python analyze_simulation_results.py --input simulation_results.json --config simulation_config.json --top 5
```

Final-Index = `weight_kz` · KZ + `weight_ros` · RoS, wobei die RoS vorher auf zwei Nachkommastellen gerundet wird (ab ,5 vom Betrag aufrunden). Die Gewichte stehen in der Config (Block `final_index`; `weight_kz` = 1, `weight_ros` = k ganzzahlig, k aus der Streuung von KZ und RoS bestimmt, `planspiel/index_weights.py`) und lassen sich für eine Auswertung überschreiben:
```
uv run python analyze_simulation_results.py --input simulation_results.json --config simulation_config.json --weight-ros 20
```

---
## Ziel des Spiels

Das Planspiel richtet sich an Studierende und vermittelt die Wichtigkeit von Sicherheitsmaßnahmen – nicht über tiefes Technik‑Know‑how, sondern über risikoorientiertes Denken und unternehmerische Abwägungen. Im Fokus steht, wie man Security im Kontext von Budget, Geschäftszielen und Stakeholder‑Erwartungen sinnvoll priorisiert. Die Teilnehmenden erleben den Berateralltag realistisch und nachvollziehbar: von der Auftragsklärung über die Begründung von Maßnahmen bis zur Kommunikation bei Störungen. Ziel ist es, Entscheidungen nachvollziehbar zu treffen, Trade‑offs transparent zu machen und den Business‑Nutzen von Security (z. B. Vermeidung von Ausfällen, Schutz von IP, Compliance‑Fähigkeit) sichtbar zu machen – ohne dass tiefes technisches Detailwissen erforderlich ist.

## Lizenz & Beiträge

- Lizenz & Beitragshinweise nach Bedarf ergänzen.  
- Vorschlag: Issues/Feedback sammeln zu **Spielbarkeit**, **Realitätsnähe** und **Auswertbarkeit** (bitte ohne konkrete Zahlenvorgaben einzureichen).

---
