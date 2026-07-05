# Folienkonzept: MechTech & Spielphasen-Block

Ausführlicher Bericht zu den 9 Folien, die in `final_documents/Planspiel_Einführung + Grundlagen.pptx`
nach dem SPIELPHASEN-Divider eingefügt wurden (Folie 23–30). Für jede Folie: Kernbotschaft, warum sie
an dieser Stelle steht, was Daniel/Claudio dabei betonen sollten, und wie sie sich zu den Nachbarfolien
verhält. Gedacht als Vorbereitungs- und Nachschlage-Unterlage, nicht als Skript zum Ablesen.

---

## 1. Der Kunde: MECHTECH GmbH

**Kernbotschaft:** MechTech ist kein austauschbares Blindtext-Unternehmen, sondern ein konkreter,
glaubwürdiger Automotive-Zulieferer mit Eigenschaften, die später die gesamte Bedrohungslage erklären.

**Warum diese Folie hier steht:** Alle drei Teams brauchen denselben faktischen Ausgangspunkt, bevor
die Discovery-Rollenspielphase beginnt. Die Folie liefert die Fakten, die *für alle sichtbar* sind –
alles Zusätzliche muss in der Informations- und Lesephase gezielt erfragt werden.

**Was betont werden sollte:**
- Die drei genannten Fakten (Fertigung, Kunde/OEM, IT/OT-Landschaft) sind bewusst *neutral* formuliert –
  keiner davon wird als "Schwachstelle" benannt. Das ist Absicht: Teams sollen selbst erkennen, welche
  Risiken sich daraus ergeben (z. B. dass ein gemeinsames LAN für Office-IT und Produktion eine
  OT-Angriffsfläche schafft, oder dass Liefertermintreue >98 % Verfügbarkeit zum kritischen Schutzziel
  macht). Das explizite Vorsagen würde den Lerneffekt der Discovery-Phase zerstören.
- Diese drei Fakten sind kein Zufall, sondern korrespondieren grob mit den drei CIA-Dimensionen, die im
  weiteren Spielverlauf bewertet werden – ohne das an dieser Stelle schon so zu benennen.

**Bezug zu Nachbarfolien:** Direkter Vorlauf zur *Spieleinführung* und *Informations- und Lesephase* –
diese Folie liefert das "Was ist gegeben", die folgenden Folien liefern das "Was dürft/müsst ihr tun".

---

## 2. Spieleinführung

**Kernbotschaft:** Ihr seid keine MechTech-Mitarbeitenden, sondern ein externes Beratungsteam – das
prägt die gesamte Spielhaltung. Und: Erfolg ist keine einzelne "richtige" Antwort, sondern eine Balance
aus drei Zielgrößen.

**Warum diese Folie hier steht:** Sie ist der erste der fünf offiziellen Agenda-Schritte (siehe
SPIELPHASEN-Folie) und damit der Ort, an dem Rollen, Ziel und Bewertungsmaßstab ein für alle Mal geklärt
werden, bevor irgendeine Entscheidung fällt.

**Was betont werden sollte:**
- **Rolle:** externe Berater, kein Insider-Wissen – Informationen müssen aktiv erfragt werden (Brücke
  zur nächsten Folie).
- **Ziel:** die drei Metriken Kundenzufriedenheit (KZ), CIA-Zielerfüllung und Return on Security (RoS)
  tauchen in *jeder* späteren Phase wieder auf. Es lohnt sich, hier schon zu sagen: "Es gibt keine
  Maximalpunktzahl in nur einer Metrik zu gewinnen – ihr müsst zwischen allen dreien abwägen."
- **Moderator:** klarstellen, dass dieselbe Person zwei Hüte trägt – Kunde (in Discovery) und
  Spielleitung (Trigger/Effekte). Das nimmt später Verwirrung, wenn der Moderator zwischen beiden
  Rollen wechselt.

**Bezug zu Nachbarfolien:** Führt die drei Metriken ein, die auf jeder folgenden Folie im "Worauf
achten"-Baustein wieder auftauchen.

---

## 3. Informations- und Lesephase

**Kernbotschaft:** Dies ist die einzige Phase, in der noch Informationen gesammelt werden können – die
Qualität der gestellten Fragen bestimmt die Qualität der Entscheidungsgrundlage für den Rest des Spiels.

**Warum diese Folie hier steht:** Sie überführt die reinen MechTech-Fakten (Folie 1) in
spielrelevante Signale, die später die Gewichtung von Wellen und Angriffen deterministisch beeinflussen
(siehe README, Abschnitt "Discovery-Signale").

**Was betont werden sollte:**
- Es gibt keine "versteckten Fallen" oder Trickfragen – der Moderator antwortet ehrlich und
  kontextbezogen. Aber er wird **nie** von sich aus eine Lücke benennen ("Wir haben kein separates
  OT-Netz" käme nur auf gezielte Nachfrage, nie unaufgefordert).
- Das ist ausdrücklich Rollenspiel: Der Moderator spricht "in character" als MechTech-Vertreter, nicht
  als Facilitator.
- Notizen sind kein Bonus, sondern Pflicht: Die hier gesammelten Signale sind die einzige Begründung,
  die Teams später für ihre Maßnahmenwahl vorweisen können.

**Bezug zu Nachbarfolien:** Bildet die Brücke zwischen "Der Kunde: MECHTECH GmbH" (Fakten) und
"Budgetverhandlung"/"Maßnahmenwahl" (Entscheidungen) – alles, was hier nicht erfragt wird, fehlt später
als Begründung.

---

## 4. Budgetverhandlung

**Kernbotschaft:** Budget ist nicht nur eine Ressourcengrenze, sondern hat einen unmittelbaren Effekt
auf die Kundenzufriedenheit – mehr Budget bedeutet auch höhere Erwartungen.

**Warum diese Folie hier steht:** Sie ist der dritte Agenda-Schritt und der Moment, an dem aus
gesammelten Signalen eine harte Zahl wird, die den gesamten weiteren Handlungsspielraum begrenzt.

**Was betont werden sollte:**
- Das ist eine echte Verhandlung, kein Blankoscheck: Das Team muss den geforderten Betrag mit den
  Discovery-Signalen begründen ("Wir haben gehört, dass ... deshalb schlagen wir X € vor").
- Der Trade-off ist gewollt, kein Störfaktor: Höheres Budget ermöglicht mehr/bessere Maßnahmen, senkt
  aber gleichzeitig die Toleranzschwelle des Kunden (höhere Erwartung an messbare Ergebnisse).

**Bezug zu Nachbarfolien:** Setzt die harte Obergrenze für die nachfolgende Maßnahmenwahl – ohne
Budgetentscheidung keine sinnvolle Diskussion über L1/L2/L3-Maßnahmen.

---

## 5. Angriffssimulation – Maßnahmenwahl

**Kernbotschaft:** Mehr Maßnahmen sind nicht automatisch besser – Budget ist begrenzt, Abhängigkeiten
zwischen Maßnahmen müssen erfüllt sein, und jede Wahl wirkt sich direkt auf den späteren CIA-Wert aus.

**Warum diese Folie hier steht:** Sie ist der erste von drei Teilschritten, die sich innerhalb von
"Angriffssimulation (3 Runden)" in jeder Runde wiederholen – das muss explizit gesagt werden, sonst
wirkt die Nummerierung (kein eigener Nummernschritt in der Agenda) verwirrend.

**Was betont werden sollte:**
- L1/L2/L3 als Reifegrad erklären: mehr Wirkung, aber auch mehr Kosten – keine Maßnahme ist per se
  "richtig", es kommt auf das Verhältnis zum Budget und zu den Discovery-Signalen an.
- Abhängigkeiten explizit ansprechen: Manche Maßnahmen setzen andere voraus (im Detail auf den
  Maßnahmenkarten nachzulesen) – das vor der ersten Runde einmal exemplarisch zeigen, sonst wird es in
  der Praxis übersehen.
- Diese Phase wiederholt sich: In Runde 2 und 3 kommen Teams wieder hierher zurück (nach dem
  Change-Fenster), meist mit angepasster Strategie.

**Bezug zu Nachbarfolien:** Der hier gewählte Maßnahmen-Mix ergibt den Team-CIA-Wert, der auf der
nächsten Folie ("Welle") gegen das E-Ziel geprüft wird.

---

## 6. Angriffssimulation – Welle

**Kernbotschaft:** Es wird nicht gewürfelt. Alles ist deterministisch aus dem Team-CIA-Wert (Ergebnis
der Maßnahmenwahl) und dem E-Ziel der Welle berechenbar – das ist der zentrale Lernmoment des Spiels.

**Warum diese Folie hier steht:** Sie ist der Kern der "Angriffssimulation" – hier wird sichtbar, ob
sich die vorherigen Entscheidungen ausgezahlt haben.

**Was betont werden sollte:**
- Die Reihenfolge ist fix und sollte einmal laut vorgelesen werden: erst Events, dann Angriffe, dann
  E-Ziel-Check, dann OPEX/Recovery. Teams, die diese Reihenfolge verstehen, können das Ergebnis vorab
  grob abschätzen – das ist gewollt (Determinismus als Lernprinzip, nicht als Blackbox).
- Der CIA-Wert ist keine Zufallszahl, sondern eine direkte, nachvollziehbare Konsequenz der
  Maßnahmenwahl aus der vorherigen Folie – diesen Zusammenhang explizit verbal herstellen.
- KZ-Bonus/-Malus als unmittelbares, sichtbares Feedback verstehen: Das Team bekommt hier zum ersten
  Mal eine Rückmeldung, ob die Strategie aufgeht.

**Bezug zu Nachbarfolien:** Ergebnis (Schäden, CIA-Mali, KZ-Delta) wird in Tabelle 2 festgehalten und
bildet die Ausgangslage für das nachfolgende Change-Fenster.

---

## 7. Angriffssimulation – Change-Fenster

**Kernbotschaft:** Eine Fehleinschätzung in Runde 1 ist nicht endgültig – es gibt eine Chance zur
Nachjustierung. Aber: *Wie* man das kommuniziert, ist selbst ein bewertungsrelevanter Faktor.

**Warum diese Folie hier steht:** Sie schließt den Runden-Zyklus ab und ist der Übergang zurück in die
nächste Welle (bzw. zur Reflexion nach der letzten Runde).

**Was betont werden sollte:**
- Upgrades/Swaps wirken erst **ab der nächsten Welle** – kein rückwirkender Schutz für die gerade
  abgelaufene Welle. Das erzeugt bewusst Erwartungsdruck und verhindert reines Reagieren im Nachhinein.
- Kommunikation an den Kunden hat einen eigenen, vom technischen Nutzen der Maßnahme unabhängigen
  KZ-Effekt: Transparent kommunizierte Changes wirken sich positiv aus, auch wenn die Maßnahme selbst
  noch nicht wirkt. Das lohnt sich hervorzuheben, weil es oft unterschätzt wird.

**Bezug zu Nachbarfolien:** Schließt den Kreis zurück zu "Angriffssimulation – Maßnahmenwahl" für die
nächste Runde; nach der dritten Runde führt dieser Schritt stattdessen direkt in die Reflexion.

---

## 8. Reflexion im Plenum

**Kernbotschaft:** Erfolg bemisst sich nicht daran, "keine Angriffe abbekommen zu haben", sondern an
einer Gesamtbilanz aus Kosten, Schäden, RoS und finaler KZ – Sicherheit muss ökonomisch bewertet werden,
nicht nur technisch.

**Warum diese Folie hier steht:** Sie ist der letzte Agenda-Schritt und der Ort, an dem die eigentliche
Lernreflexion stattfindet – die Zahlen sind das Vehikel, nicht das Ziel.

**Was betont werden sollte:**
- Die RoS-Formel einmal Schritt für Schritt vorrechnen (620.000 € als fixer Referenzwert – das ist der
  Schaden, der ohne jegliche Sicherheitsmaßnahmen entstanden wäre). Das macht sichtbar: RoS setzt
  vermiedenen Schaden ins Verhältnis zu den investierten Kosten, nicht nur "wie viel wurde ausgegeben".
- Die Reflexionsfragen ("was lief gut, was würdet ihr anders machen") sind der eigentliche didaktische
  Kern – das sollte im Vortrag stärker betont werden als die reine Punktzahl, damit die Diskussion
  danach nicht zum bloßen Ranking-Vergleich verkommt.
- Falls mehrere Teams verglichen werden: transparent machen, dass der Vergleich über einen Final-Index
  (Gewichtung aus KZ und RoS) läuft, nicht über eine einzelne Metrik allein.

**Bezug zu Nachbarfolien:** Schließt den gesamten Spielablauf ab; greift auf alle in Tabelle 1 und
Tabelle 2 während des Spiels gesammelten Werte zurück.

---

## Roter Faden über alle acht Folien

Die drei Metriken (KZ, CIA, RoS), die in der *Spieleinführung* eingeführt werden, ziehen sich durch
jede folgende Folie – jede "Worauf achten"-Zeile verweist auf mindestens eine davon. Der zweite rote
Faden ist der Determinismus: von den MechTech-Fakten über die Discovery-Signale bis zur E-Ziel-Prüfung
in der Welle ist jeder Schritt nachvollziehbar aus dem vorherigen ableitbar – kein Schritt sollte sich
für die Teilnehmenden wie Zufall anfühlen. Beide Fäden lohnt es sich, in der Moderation immer wieder
explizit zu benennen, weil sie über die einzelnen Folien hinweg leicht auseinanderfallen.
