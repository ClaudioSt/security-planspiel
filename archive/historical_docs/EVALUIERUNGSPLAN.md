# Evaluierungsplan: Security-Planspiel

## 1. Spielkontext und Ziele

### 1.1 Rahmenbedingungen
| Parameter | Wert |
|-----------|------|
| **Zielgruppe** | Studenten (keine Security-Experten) |
| **Spielmodus** | Kompetitiv: 3 Teams à 5 Personen |
| **Industriekontext** | Automotive Zulieferer (OT-Fokus, Supply-Chain) |
| **Spiellänge** | 3 Wellen mit Events |
| **Angriffstransparenz** | Nur bekannt: "3 Wellen werden kommen" |

### 1.2 Lernziele
1. **CIA-Triade verstehen**: Wie beeinflussen Confidentiality, Integrity und Availability verschiedene Angriffsszenarien?
2. **Trade-off-Denken**: Begrenztes Budget optimal auf identifizierte Risiken verteilen
3. **Risikobasiertes Arbeiten**: Gute Risikoanalyse führt zu besseren Entscheidungen

### 1.3 Erfolgskriterien
| Kriterium | Gewichtung | Beschreibung |
|-----------|------------|--------------|
| **Kundenzufriedenheit (KZ)** | 60% | Primärer Indikator, Start bei 60, Ziel: ≥50 am Ende |
| **Return on Security (ROS)** | 30% | (Vermiedener Schaden - Kosten) / Kosten |
| **Gesamtschaden (€)** | 10% | Kumulierter Schaden über alle Wellen |

---

## 2. Schadensberechnung (CIA-basiert)

### 2.1 Basis-CIA-Werte
```
Standard-Basis (vor Maßnahmen): C=10, I=10, A=10
```

Diese Werte repräsentieren den Grundschutz eines typischen mittelständischen Unternehmens ohne dedizierte Security-Maßnahmen.

### 2.2 CIA-Berechnung
```
CIA_gesamt = Basis_CIA + Σ(Maßnahmen_CIA)
```

**Beispiel:**
- Basis: C=10, I=10, A=10
- M1 (IAM) L2: C+4, I+3, A+0
- M4 (Backup) L2: C+1, I+6, A+5
- **Gesamt**: C=15, I=19, A=15

### 2.3 E-Value (Effektivitätswert)
Der E-Value gewichtet die CIA-Werte basierend auf dem jeweiligen Angriff:

```
E-Value = C × w_C + I × w_I + A × w_A
```

| Angriff | C-Gewicht | I-Gewicht | A-Gewicht | Schwerpunkt |
|---------|-----------|-----------|-----------|-------------|
| Ransomware | 0.4 | 0.4 | 0.2 | Balanced (C/I) |
| OT-Disruption | 0.2 | 0.2 | 0.6 | Availability |
| Exfiltration | 0.5 | 0.3 | 0.2 | Confidentiality |

### 2.4 Mitigation-Berechnung

```
Basis-Reduktion = max(0, (E-Value - E-Schwelle) / E-Divisor)
Bonus-Reduktion = Σ(Bonus-Maßnahmen wenn Level erreicht)
Gesamt-Reduktion = min(Basis + Bonus, Mitigation-Cap)
Effektive-Severity = max(0, Basis-Severity × Tier-Multiplikator - Reduktion)
```

**Schaden-Formel:**
```
Schaden = Effektive-Severity × Schaden-pro-Severity × (1 - Recovery-Faktor)
KZ-Verlust = Effektive-Severity × KZ-pro-Severity
CIA-Mali = Effektive-Severity × CIA-Impact
```

---

## 3. Maßnahmen und CIA-Zuordnung

### 3.1 Maßnahmen-Übersicht mit CIA-Fokus

| ID | Maßnahme | C-Fokus | I-Fokus | A-Fokus | Primär gegen |
|----|----------|---------|---------|---------|--------------|
| M1 | IAM/PAM | ★★★ | ★★ | ★ | Exfiltration |
| M2 | SIEM/MDR | ★ | ★★★ | ★ | Alle (Detection) |
| M3 | EDR/XDR | ★★★ | ★★ | ★★ | Ransomware |
| M4 | Backup & DR | ★ | ★★★ | ★★★ | Ransomware (Recovery) |
| M5 | Segmentierung | ★★ | ★ | ★★★ | OT-Disruption |
| M6 | Awareness | ★★ | ★★ | ★★ | Ransomware (Prävention) |
| M7 | Patch Mgmt | ★★ | ★★★ | ★★ | OT-Disruption |
| M8 | Supply Chain | ★★ | ★★ | ★★ | Exfiltration |
| M9 | Cloud Security | ★★ | ★★ | ★ | *Suboptimal - nur CIA-Bonus* |
| M10 | MDM | ★★ | ★★ | ★ | *Suboptimal - nur CIA-Bonus* |

> **Design-Entscheidung M9/M10:** Diese Maßnahmen bleiben im Spiel als bewusste "Fallen". Sie bieten zwar CIA-Werte, sind aber für den Automotive-Kontext weniger relevant:
> - **Kein Bonus-Effekt** bei Angriffen (anders als M1-M8)
> - Studenten sollen lernen: **Kontextpassung ist wichtig** - nicht jede Security-Maßnahme passt zu jedem Unternehmen
> - Wer M9/M10 hoch ausbaut, verschwendet Budget, das bei M1-M8 effektiver wäre

### 3.2 Maßnahmen-Tiers und Kosten

**Tier-Struktur:**
- **L0**: Nicht implementiert (keine Kosten, kein Schutz)
- **L1**: Basis (niedriger Schutz, niedrige Kosten)
- **L2**: Standard (mittlerer Schutz, moderate Kosten)
- **L3**: Advanced (hoher Schutz, hohe Kosten, evtl. Dependencies)

**Beispiel M4 (Backup & DR):**
| Level | C | I | A | Init (k€) | OPEX (k€/Welle) | Recovery |
|-------|---|---|---|-----------|-----------------|----------|
| L0 | 0 | 0 | 0 | 0 | 0 | 0% |
| L1 | 0 | 4 | 3 | 16 | 6 | 10% |
| L2 | 1 | 6 | 5 | 40 | 12 | 30% |
| L3 | 1 | 8 | 7 | 80 | 20 | 50% |

### 3.3 Abhängigkeiten

```
M1 L3 → erfordert M2 ≥ L2 (IAM braucht Logging für Session-Tracking)
M3 L3 → erfordert M2 ≥ L2 (EDR braucht SIEM für Korrelation)
M7 L3 → erfordert M2 ≥ L1 (Patching braucht Monitoring zur Validierung)
```

**Logik:** SIEM/Logging (M2) ist die Grundlage für Sichtbarkeit. Ohne Sichtbarkeit können fortgeschrittene Maßnahmen nicht ihr volles Potenzial entfalten.

---

## 4. Angriffsszenarien und Gewichtung

### 4.1 Welle 1: Ransomware (Office-IT)

| Parameter | Wert |
|-----------|------|
| **Basis-Severity** | 8 |
| **Schaden/Severity** | 20k€ |
| **KZ-Verlust/Severity** | -3 |
| **CIA-Gewichte** | C=0.4, I=0.4, A=0.2 |
| **E-Schwelle** | 18 |
| **Mitigation-Cap** | 8 |
| **Recovery möglich** | ✓ (M4 reduziert Schaden) |

**Bonus-Maßnahmen:**
- M3 (EDR) ≥ L2: +2 Reduktion
- M4 (Backup) ≥ L2: +2 Reduktion
- M6 (Awareness) ≥ L2: +1 Reduktion

**Realitätsbezug:** Ransomware zielt auf Verschlüsselung (I) und Datendiebstahl (C). Mit guten Backups (M4) kann der Schaden durch Recovery reduziert werden.

### 4.2 Welle 2: OT-Disruption (Produktion)

| Parameter | Wert |
|-----------|------|
| **Basis-Severity** | 10 |
| **Schaden/Severity** | 32k€ |
| **KZ-Verlust/Severity** | -3 |
| **CIA-Gewichte** | C=0.2, I=0.2, A=0.6 |
| **E-Schwelle** | 20 |
| **Mitigation-Cap** | 10 |
| **Recovery möglich** | ✓ |

**Bonus-Maßnahmen:**
- M5 (Segmentierung) ≥ L2: +3 Reduktion
- M7 (Patching) ≥ L2: +2 Reduktion

**Realitätsbezug:** OT-Angriffe zielen auf Produktionsverfügbarkeit (A). Netzwerksegmentierung verhindert Lateral Movement. Der höchste Schaden pro Severity (32k€) reflektiert Produktionsausfall.

### 4.3 Welle 3: Exfiltration (Datendiebstahl)

| Parameter | Wert |
|-----------|------|
| **Basis-Severity** | 7 |
| **Schaden/Severity** | 20k€ |
| **KZ-Verlust/Severity** | -3 |
| **CIA-Gewichte** | C=0.5, I=0.3, A=0.2 |
| **E-Schwelle** | 22 |
| **Mitigation-Cap** | 7 |
| **Recovery möglich** | ✗ (Daten bereits gestohlen) |

**Bonus-Maßnahmen:**
- M1 (IAM) ≥ L2: +2 Reduktion
- M2 (SIEM) ≥ L2: +2 Reduktion
- M8 (Supply Chain) ≥ L2: +1 Reduktion

**Realitätsbezug:** Datenexfiltration betrifft primär Vertraulichkeit (C). Backup hilft nicht - gestohlene Daten sind draußen. Hohe E-Schwelle (22) bedeutet: nur gut aufgestellte Teams mitigieren effektiv.

---

## 5. Budget-System

### 5.1 Budget-Tiers mit Trade-offs

| Tier | Budget | KZ-Start | Severity-Multiplikator | E-Ziele (W1/W2/W3) |
|------|--------|----------|------------------------|-------------------|
| **Low** | 200k€ | 65 | ×0.7 | 15/17/19 |
| **Medium** | 300k€ | 60 | ×1.0 | 18/20/22 |
| **High** | 400k€ | 55 | ×1.3 | 21/23/25 |

**Logik:**
- **Niedriges Budget**: Weniger Maßnahmen möglich, aber Angriffe sind weniger schwer (kleines Unternehmen = kleineres Ziel). Höherer KZ-Start als Puffer.
- **Hohes Budget**: Mehr Maßnahmen möglich, aber höhere Erwartungen (E-Ziele) und schwerere Angriffe.

### 5.2 Kostenstruktur
```
Gesamtkosten = Init-Kosten + (OPEX × Wellenanzahl) + Event-OPEX
```

**Empfehlung für Studenten:** Medium-Tier (300k€) als Standardwahl.

### 5.3 Realismus der Budgets

| Maßnahme L2 | Init | OPEX/Jahr | Marktvergleich |
|-------------|------|-----------|----------------|
| IAM/PAM | 40k€ | 12k€ | ✓ Realistisch (Azure AD P2 + PAM) |
| SIEM/MDR | 30k€ | 18k€ | ✓ Realistisch (Managed SIEM) |
| EDR/XDR | 25k€ | 12k€ | ✓ Realistisch (CrowdStrike o.ä.) |
| Backup L2 | 40k€ | 12k€ | ✓ Realistisch (Veeam + Cloud) |
| Segmentierung | 50k€ | 8k€ | ✓ Realistisch (Firewalls + VLANs) |

---

## 6. Kombinationsboni (OPTIONAL)

> **Hinweis:** Kombinationsboni sind eine optionale Erweiterung und nicht zwingend für das Basisspiel erforderlich. Sie können hinzugefügt werden, um fortgeschrittene Spieler zu belohnen.

### 6.1 Statische Synergien (Optional)

| Kombination | Bonus | Logik |
|-------------|-------|-------|
| M2 ≥ L2 + M3 ≥ L2 | +1 E-Value global | SIEM + EDR = korrelierte Erkennung |
| M1 ≥ L2 + M2 ≥ L2 | +1 gegen Exfiltration | IAM-Logs in SIEM = Insider-Erkennung |
| M4 ≥ L2 + M5 ≥ L2 | +1 gegen Ransomware | Segmentierte Backups = schnellere Recovery |
| M6 ≥ L2 + M7 ≥ L2 | +1 gegen OT | Awareness + Patching = Defense-in-Depth |
| M3 ≥ L2 + M6 ≥ L2 | +1 gegen Ransomware | EDR + Awareness = Endpoint-Schutz |

### 6.2 Event-basierte Synergien (Optional)

| Event-Trigger | Bedingung | Effekt |
|---------------|-----------|--------|
| "Security Operations Center etabliert" | M2 ≥ L2 + M3 ≥ L2 | KZ +3, OPEX -5k€ |
| "Compliance-Audit bestanden" | ≥4 Maßnahmen auf L2 | KZ +5, Budget +15k€ |
| "Security-Champion-Programm" | M6 ≥ L2 + M1 ≥ L1 | Reduziert Impact von Phishing-Events |

---

## 7. Event-System

### 7.1 Event-Struktur

```
Event {
  id: string
  name: string
  description: string
  timing: "pre_wave" | "post_wave"
  condition: { measure?, min_level?, e_value_min?, measures_at_level_2? }
  effect_if_met: { kz?, budget?, opex? }
  effect_if_not_met: { kz?, budget?, opex? }
}
```

### 7.2 Realistische Events (Automotive-Kontext)

#### Welle 0 (Vor dem Spiel)

| Event | Bedingung | Erfüllt | Nicht erfüllt |
|-------|-----------|---------|---------------|
| **Lieferanten-Fragebogen** | M8 ≥ L1 | KZ +2 | Budget -10k€ |
| **ISO 27001 Quick-Check** | ≥3 Maßnahmen ≥ L1 | KZ +3 | KZ -2 |

#### Welle 1 (Nach Ransomware)

| Event | Bedingung | Erfüllt | Nicht erfüllt |
|-------|-----------|---------|---------------|
| **Phishing-Kampagne entdeckt** | M6 ≥ L2 | KZ +2 | KZ -3 |
| **Cyber-Versicherung Prüfung** | E-Value ≥ 16 | Budget +10k€ | Budget -15k€ |
| **Kritische Schwachstelle (CVE)** | M7 ≥ L1 | KZ 0 | KZ -2 |

#### Welle 2 (Nach OT-Disruption)

| Event | Bedingung | Erfüllt | Nicht erfüllt |
|-------|-----------|---------|---------------|
| **OEM-Sicherheitsaudit** | E-Value ≥ 18 | KZ +5 | KZ -5 |
| **Produktionsdruck** | M5 ≥ L1 | KZ 0 | OPEX +8k€ |
| **Security-Experte kündigt** | M2 ≥ L2 | KZ 0 | KZ -3, OPEX +5k€ |

#### Welle 3 (Nach Exfiltration)

| Event | Bedingung | Erfüllt | Nicht erfüllt |
|-------|-----------|---------|---------------|
| **NIS2/KRITIS-Prüfung** | ≥4 Maßnahmen ≥ L2 | KZ +5 | KZ -8, Budget -20k€ |
| **Lieferanten-Datenpanne** | M8 ≥ L2 | KZ +2 | KZ -4 |
| **Vorstandspräsentation** | E-Value ≥ 20 | KZ +3 | KZ -2 |

### 7.3 Neue Events (Vorschläge)

| Event | Timing | Bedingung | Erfüllt | Nicht erfüllt |
|-------|--------|-----------|---------|---------------|
| **Media-Berichterstattung** | Post-W1 | Severity ≤ 3 | KZ +4 | KZ -6 |
| **OEM-Notfall-Meeting** | Post-W2 | KZ ≥ 50 | KZ +2 | KZ -10 |
| **TISAX-Zertifizierung** | Pre-W3 | M1≥L2 + M2≥L2 | Budget +25k€ | - |
| **Praktikant klickt Link** | Post-W1 | M6 ≥ L2 | KZ 0 | KZ -5 |
| **Firmware-Update verfügbar** | Pre-W2 | M7 ≥ L2 | Severity -1 | - |

---

## 8. Anpassungsmöglichkeit zwischen Wellen

### 8.1 Regeln für Anpassungen

```
Nach jeder Welle:
- Teams können EIN Upgrade ODER EIN Downgrade durchführen
- Upgrade: Zahle Init-Differenz + 50% Aufpreis
- Downgrade: Erhalte 25% der Init-Differenz zurück
- Neue OPEX gilt ab nächster Welle
```

### 8.2 Beispiel

**Situation:** Nach Welle 1 (Ransomware) erkennt Team, dass M4 wichtiger ist als gedacht.

- **Aktuell:** M4 L1 (Init: 16k€ bezahlt)
- **Upgrade auf L2:** Init-Differenz = 40k - 16k = 24k€
- **Kosten:** 24k€ × 1.5 = 36k€
- **Neuer OPEX:** 12k€/Welle (statt 6k€)

### 8.3 Events die Anpassung beeinflussen

| Event | Effekt |
|-------|--------|
| "Notfall-Budget freigegeben" | Einmaliges Upgrade ohne Aufpreis |
| "Budgetkürzung" | Kein Upgrade in dieser Runde möglich |
| "Expertise gewonnen" | +1 Level in einer Maßnahme (kostenlos) |

---

## 9. Risikobasiertes Arbeiten

### 9.1 Risikoanalyse-Phase (Spielbeginn)

**Ablauf:**
1. Teams erhalten Informationen über das Unternehmen (Automotive Zulieferer)
2. Teams identifizieren potenzielle Bedrohungen (ohne Wissen über konkrete Angriffe)
3. Teams priorisieren Risiken und wählen Maßnahmen

**Hilfsmaterial:**
- Branchenübliche Bedrohungslandschaft (z.B. ENISA-Report Automotive)
- CIA-Schnellreferenz (welche Maßnahme schützt was)
- Budget-Kalkulationstool

### 9.2 Wie gute Risikoanalyse belohnt wird

| Analyseergebnis | Spielauswirkung |
|-----------------|-----------------|
| "OT-Risiko erkannt" → M5 gewählt | Weniger Schaden in Welle 2 |
| "Ransomware-Risiko erkannt" → M4+M3 gewählt | Weniger Schaden + Recovery in Welle 1 |
| "Datenexfiltration erkannt" → M1+M2 gewählt | Weniger Schaden in Welle 3 |
| "Breite Abdeckung" → viele L1-Maßnahmen | Moderate Schutzwirkung überall |
| "Fokussierte Strategie" → wenige L3-Maßnahmen | Starker Schutz bei Match, Lücken bei Mismatch |

### 9.3 Optimale vs. suboptimale Strategien

**Gut (risikobasiert):**
- M5 L2 + M7 L2 + M4 L2 + M3 L1 (fokussiert auf wahrscheinlichste Risiken)
- E-Values: ~20-24 für alle Wellen

**Suboptimal:**
- M9 L3 + M10 L3 (Cloud/MDM bei Automotive = wenig Nutzen)
- Hohe Kosten, niedrige E-Values

---

## 10. Evaluierungs-Metriken

### 10.1 Team-Bewertung

```
Gesamtpunktzahl = (KZ_final × 0.6) + (ROS × 100 × 0.3) + ((100 - Schaden/10) × 0.1)
```

### 10.2 Vergleichsmatrix

| Metrik | Team A | Team B | Team C |
|--------|--------|--------|--------|
| KZ Final | | | |
| Gesamtschaden | | | |
| ROS | | | |
| Gesamtpunktzahl | | | |

### 10.3 Lernerfolgsmessung

**Post-Game-Fragebogen:**
1. Welche CIA-Dimension war für Welle X am wichtigsten?
2. Warum war Maßnahme Y gegen Angriff Z besonders effektiv?
3. Wie würden Sie mit dem Wissen von heute anders entscheiden?

---

## 11. Implementierungs-Checkliste

### 11.1 Bereits implementiert ✓
- [x] Basis-CIA-Berechnung
- [x] E-Value-System mit Gewichtung
- [x] 10 Maßnahmen mit 4 Tiers
- [x] 3 Angriffswellen
- [x] Budget-Tier-System
- [x] Abhängigkeiten (4 Maßnahmen)
- [x] Basis-Events (9 Stück)
- [x] Recovery-Mechanismus (M4)
- [x] Bonus-Maßnahmen pro Welle

### 11.2 Zu implementieren ○
- [ ] Zwischen-Wellen-Anpassung (Upgrade/Downgrade-Regeln)
- [ ] Neue realistische Events (Event-Pool erweitern)
- [ ] Pre-Wave Events (optionale Hinweise)
- [ ] Risikoanalyse-Hilfsmaterial für Studenten
- [ ] Team-Arbeitsblätter (Druckvorlagen)
- [ ] Team-Bewertungsmatrix
- [ ] Post-Game-Evaluation / Debriefing-Leitfaden

### 11.3 Optional ◇
- [ ] Statische Kombinationsboni (für fortgeschrittene Spieler)
- [ ] Event-basierte Synergien
- [ ] Zufällige Event-Auswahl (aus Pool)
- [ ] Variable Angriffsreihenfolge
- [ ] Schwierigkeitsgrade
- [ ] Timer für Entscheidungsphasen

---

## 12. Spielablauf und Zeitplan

### 12.1 Gesamtdauer: 3-4 Stunden

| Phase | Dauer | Inhalt |
|-------|-------|--------|
| **Anmoderation** | 15-20 min | Spielregeln, CIA-Triade erklären, Szenario vorstellen |
| **Risikoanalyse** | 20-30 min | Teams analysieren Bedrohungen, priorisieren |
| **Maßnahmenwahl** | 15-20 min | Budget verteilen, Maßnahmen wählen |
| **Welle 1** | 25-30 min | Angriff aufdecken, berechnen, Events, Anpassung |
| **Welle 2** | 25-30 min | Angriff aufdecken, berechnen, Events, Anpassung |
| **Welle 3** | 20-25 min | Angriff aufdecken, berechnen, Events, Finale |
| **Auswertung** | 15-20 min | Ergebnisse vergleichen, Sieger küren |
| **Debriefing** | 20-30 min | Learnings diskutieren, optimale Strategie zeigen |

### 12.2 Berechnung: Schriftlich in Tabellen

Die Berechnung erfolgt manuell mit vorbereiteten Tabellen:

**Team-Arbeitsblatt (pro Team):**
```
┌─────────────────────────────────────────────────────┐
│ TEAM: ____________     BUDGET-TIER: □ Low □ Med □ High │
├─────────────────────────────────────────────────────┤
│ MAASSNAHMEN                                          │
│ M1 IAM:     □ L0 □ L1 □ L2 □ L3    Init: ___ OPEX: ___│
│ M2 SIEM:    □ L0 □ L1 □ L2 □ L3    Init: ___ OPEX: ___│
│ ...                                                  │
├─────────────────────────────────────────────────────┤
│ SUMMEN: Init: ___k€  OPEX/Welle: ___k€  Gesamt: ___k€│
├─────────────────────────────────────────────────────┤
│ CIA-WERTE:  C = 10 + ___ = ___                       │
│             I = 10 + ___ = ___                       │
│             A = 10 + ___ = ___                       │
└─────────────────────────────────────────────────────┘
```

**Angriffsauswertungsblatt (nach Aufdeckung):**
```
┌─────────────────────────────────────────────────────┐
│ WELLE _: _______________                             │
├─────────────────────────────────────────────────────┤
│ E-VALUE = C×___ + I×___ + A×___ = ___               │
│                                                      │
│ Basis-Reduktion = (E-Value - ___) / ___ = ___       │
│ Bonus-Reduktion: ___ + ___ + ___ = ___              │
│ Gesamt (max ___): ___                                │
│                                                      │
│ Severity = ___ - ___ = ___                          │
│ Schaden = ___ × ___k€ = ___k€                       │
│ Recovery (falls M4): × (1 - ___) = ___k€            │
│                                                      │
│ KZ-Änderung: -___ × 3 = ___                         │
│ KZ-Bonus/Malus (E-Ziel erreicht?): ___              │
└─────────────────────────────────────────────────────┘
```

### 12.3 Transparenz-Konzept

| Information | Vor Angriff | Nach Angriff |
|-------------|-------------|--------------|
| Eigene CIA-Werte | ✓ Bekannt | ✓ Bekannt |
| Eigene Kosten | ✓ Bekannt | ✓ Bekannt |
| Berechnungsformeln | ✓ Bekannt | ✓ Bekannt |
| Angriffstyp | ✗ Unbekannt | ✓ Aufgedeckt |
| CIA-Gewichtung | ✗ Unbekannt | ✓ Aufgedeckt |
| Bonus-Maßnahmen | ✗ Unbekannt | ✓ Aufgedeckt |
| E-Schwelle | ✗ Unbekannt | ✓ Aufgedeckt |

**Begründung:** Teams müssen Risiken einschätzen ohne zu wissen, welche Angriffe kommen. Nach dem Angriff können sie ihre Entscheidungen evaluieren.

---

## 13. Event-Pool (Abwechslungsreich)

### 13.1 Pool-Struktur

Jede Welle hat einen Pool von **6 Events**, aus dem **3 gezogen** werden (oder vom Spielleiter ausgewählt):

### 13.2 Welle 1 - Event-Pool (Office-IT Fokus)

| # | Event | Bedingung | Erfüllt | Nicht erfüllt |
|---|-------|-----------|---------|---------------|
| 1 | **Phishing-Kampagne entdeckt** | M6 ≥ L2 | KZ +2 | KZ -3 |
| 2 | **Cyber-Versicherung Prüfung** | E-Value ≥ 16 | Budget +10k€ | Budget -15k€ |
| 3 | **Kritische Schwachstelle (CVE)** | M7 ≥ L1 | KZ 0 | KZ -2 |
| 4 | **Praktikant klickt auf Link** | M6 ≥ L2 | KZ 0 | KZ -5, Severity +1 |
| 5 | **Verdächtige Login-Versuche** | M1 ≥ L2 | KZ +2 | KZ -2 |
| 6 | **Backup-Test angeordnet** | M4 ≥ L1 | Recovery +10% | KZ -3 |

### 13.3 Welle 2 - Event-Pool (OT/Produktion Fokus)

| # | Event | Bedingung | Erfüllt | Nicht erfüllt |
|---|-------|-----------|---------|---------------|
| 1 | **OEM-Sicherheitsaudit** | E-Value ≥ 18 | KZ +5 | KZ -5 |
| 2 | **Produktionsdruck durch Kunde** | M5 ≥ L1 | KZ 0 | OPEX +8k€ |
| 3 | **Security-Experte kündigt** | M2 ≥ L2 | KZ 0 | KZ -3, OPEX +5k€ |
| 4 | **Firmware-Update für SPS** | M7 ≥ L2 | Severity -1 | KZ -2 |
| 5 | **Netzwerkstörung erkannt** | M5 ≥ L2 | KZ +3 | Severity +1 |
| 6 | **Wartungszugang kompromittiert** | M1 ≥ L2 + M5 ≥ L1 | KZ +2 | KZ -4 |

### 13.4 Welle 3 - Event-Pool (Compliance/Exfiltration Fokus)

| # | Event | Bedingung | Erfüllt | Nicht erfüllt |
|---|-------|-----------|---------|---------------|
| 1 | **NIS2/KRITIS-Prüfung** | ≥4 Maßnahmen ≥ L2 | KZ +5 | KZ -8, Budget -20k€ |
| 2 | **Lieferanten-Datenpanne** | M8 ≥ L2 | KZ +2 | KZ -4 |
| 3 | **Vorstandspräsentation** | E-Value ≥ 20 | KZ +3 | KZ -2 |
| 4 | **TISAX-Audit angekündigt** | M1 ≥ L2 + M2 ≥ L2 | Budget +15k€ | KZ -5 |
| 5 | **Datenschutzanfrage (DSGVO)** | M1 ≥ L2 | KZ +2 | Budget -10k€ |
| 6 | **Medienbericht über Branche** | KZ ≥ 50 | KZ +5 | KZ -8 |

### 13.5 Pre-Wave Events (Optional)

Diese Events werden VOR dem Angriff aufgedeckt und können Hinweise geben:

| Event | Hinweis | Effekt |
|-------|---------|--------|
| **Erhöhte Ransomware-Aktivität** | "In der Branche häufen sich Ransomware-Fälle" | Kein direkter Effekt |
| **Lieferketten-Warnung** | "BSI warnt vor Supply-Chain-Angriffen" | Kein direkter Effekt |
| **OT-Schwachstelle publiziert** | "Neue Schwachstelle in Industriesteuerungen" | Kein direkter Effekt |

---

## 14. Offene Punkte für nächste Iteration

1. **Spielleiter-Unterlagen:** Detaillierte Moderationsanleitung erstellen
2. **Druckvorlagen:** Team-Arbeitsblätter, Event-Karten, Angriffskarten
3. **Beispielrechnung:** Komplette Durchrechnung als Referenz
4. **Schwierigkeitsanpassung:** Wie variiert man für unterschiedliche Gruppen?
5. **Feedback-Mechanismus:** Wie sammeln wir Spieler-Feedback zur Verbesserung?
