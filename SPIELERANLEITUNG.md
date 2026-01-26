# SPIELERANLEITUNG

**CIA-Planspiel Automotive - Kurzanleitung für Teams**

---

## EUER AUFTRAG

Ihr seid ein **externes Beraterteam** und beratet den Automobilzulieferer **MechTech GmbH** zur IT-Sicherheit.

**MechTech GmbH:**
- Produziert Präzisionsteile für E-Antriebe (Toleranzen <10µm)
- 80 Mitarbeitende, 3 Fertigungslinien, 24/5-Betrieb
- Hauptkunde (OEM) fordert ISO 27001-Zertifizierung bis Q3
- IT und OT aktuell im gleichen Netzwerk (Risiko!)

**Eure Ziele:**
1. Sicherheitsmaßnahmen auswählen (Budget einhalten!)
2. 3 Angriffswellen überstehen
3. Kundenzufriedenheit (KZ) maximieren
4. Return on Security (RoS) optimieren

---

## SPIELABLAUF

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  DISCOVERY  │ ──► │   BUDGET    │ ──► │ MASSNAHMEN  │
│  (25 Min)   │     │  (10 Min)   │     │  (20 Min)   │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
       ┌───────────────────────────────────────┘
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   WELLE 1   │ ──► │  CHANGE 1   │ ──► │   WELLE 2   │
│  Ransomware │     │  (15 Min)   │     │ OT-Störung  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                       │
       └───────────────────────────────────────┘
                          │
       ┌──────────────────┘
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  CHANGE 2   │ ──► │   WELLE 3   │ ──► │ AUSWERTUNG  │
│  (15 Min)   │     │ Exfiltration│     │  + DEBRIEF  │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## BUDGET-ENTSCHEIDUNG

| Budget (k€) | KZ-Start | E-Ziele (W1/W2/W3) | Trade-off |
|-------------|----------|---------------------|-----------|
| **200-250** (Low) | 70 | 18 / 20 / 22 | Wenig Geld, hoher KZ-Start |
| **300-350** (Medium) | 60 | 18 / 20 / 22 | Standard |
| **400-450** (High) | 50 | 18 / 20 / 22 | Viel Geld, niedriger KZ-Start |

**Trade-off:** Höheres Budget = mehr Maßnahmen möglich, ABER niedrigerer KZ-Start!
E-Ziele sind für alle Tiers gleich. Budget-Schritte: 50k€.

---

## MASSNAHMEN-ÜBERSICHT

| ID | Maßnahme | L1 Init/OPEX | L2 Init/OPEX | L3 Init/OPEX | Fokus |
|----|----------|--------------|--------------|--------------|-------|
| **M1** | IAM/PAM | 30/4 | 60/10 | 100/20 | Zugriffsschutz |
| **M2** | SIEM/MDR | 20/2 | 50/8 | 80/24 | Erkennung |
| **M3** | EDR/XDR | 24/4 | 56/10 | 90/18 | Endpoint-Schutz |
| **M4** | Backup/DR | 16/6 | 40/12 | 80/20 | Wiederherstellung |
| **M5** | OT-Segmentierung | 40/2 | 70/6 | 110/12 | OT-Schutz |
| **M6** | Awareness | 10/2 | 24/6 | 40/10 | Menschen |
| **M7** | Patching | 20/4 | 44/8 | 76/14 | Schwachstellen |
| **M8** | Supplier Security | 16/4 | 36/8 | 70/16 | Lieferanten |

**Suboptimal (Vorsicht!):**
| **M9** | Cloud Security | 18/3 | 40/7 | 70/14 | Kaum Cloud bei MechTech! |
| **M10** | MDM | 12/2 | 28/5 | 50/10 | Kaum Mobilgeräte relevant! |

**Abhängigkeiten:**
- M1 L3 benötigt M2 ≥ L2
- M3 L3 benötigt M2 ≥ L2
- M7 L3 benötigt M2 ≥ L1

---

## KOSTEN-RECHNUNG

```
Budget:                    ______ k€

Initiale Kosten:
  M__ L__: Init ____
  M__ L__: Init ____
  M__ L__: Init ____
  M__ L__: Init ____
  M__ L__: Init ____
  ─────────────────
  Summe Init:              ______ k€

OPEX pro Welle:
  M__ L__: OPEX ____
  M__ L__: OPEX ____
  M__ L__: OPEX ____
  M__ L__: OPEX ____
  M__ L__: OPEX ____
  ─────────────────
  Summe OPEX/Welle:        ______ k€
  × 3 Wellen =             ______ k€

Gesamt (Init + 3×OPEX):    ______ k€
Restbudget:                ______ k€  (muss ≥ 0!)
```

---

## WELLEN & ANGRIFFE

### Welle 1: Ransomware (Office-IT)
- **Narrative:** Phishing-Mail → Emotet → File-Server verschlüsselt
- **Fokus:** Confidentiality + Integrity
- **Beste Abwehr:** M6 (Awareness), M3 (EDR), M4 (Backup)

### Welle 2: OT-Störung (Produktion)
- **Narrative:** Schwachstelle in SPS → Fertigungslinie 18h Ausfall
- **Fokus:** Availability
- **Beste Abwehr:** M5 (OT-Segmentierung), M7 (Patching)

### Welle 3: Datenexfiltration (IP-Diebstahl)
- **Narrative:** Kompromittierter Lieferanten-Zugang → CAD-Daten gestohlen
- **Fokus:** Confidentiality
- **Beste Abwehr:** M1 (IAM/PAM), M2 (SIEM), M8 (Supplier)

---

## FORMELN (Kurzversion)

**Mitigation-Summe:**
```
M_sum = min(CAP, Summe aller Mitigationswerte eurer Maßnahmen)
```

**Endschwere:**
```
G = max(0, baseSeverity - M_sum)
```
→ G = 0 bedeutet: Angriff komplett abgewehrt!

**Schaden:**
```
Damage = G × sUnit (in 1.000€)
```

**KZ-Verlust:**
```
ΔKZ = -(G × kzUnit)
```

**E-Wert (Erfüllungsgrad):**
```
E = Team_C × wC + Team_I × wI + Team_A × wA
```
→ E ≥ E-Ziel: KZ-Bonus | E < E-Ziel: KZ-Malus

**Recovery (wenn M4 Backup vorhanden):**
```
Damage_final = Damage × (1 - Recovery%)
```
- L1: 10% | L2: 30% | L3: 50%

---

## EVENTS

### Allgemeine Events (alle Teams)

| Event | Trigger | Effekt |
|-------|---------|--------|
| **OEM-Audit** | Welle 2 (automatisch) | E-Wert W1 >= Ziel: KZ +5 / E-Wert W1 < Ziel: KZ -3 |
| **Fluktuation** | M6 < L2 nach Welle 1 | OPEX +5, KZ -2 |
| **DSGVO-Bonus** | M1 >= L2 UND M2 >= L2 nach W2 | KZ +3, Budget +10 |

### Budget-spezifische Events

| Event | Gilt für | Trigger | Effekt |
|-------|----------|---------|--------|
| **Compliance-Gap** | Nur LOW (200-250k) | Nach Welle 2 | KZ **-3** |
| **Investor Confidence** | Nur HIGH (400-450k) | Nach Welle 3 | KZ **+8** |

*Diese Events balancieren die unterschiedlichen Ausgangssituationen der Budget-Tiers.*

---

## CHANGE-FENSTER

Nach Welle 1 und 2 könnt ihr:
- Maßnahmen **upgraden** (L1→L2, L2→L3)
- **Neue** Maßnahmen kaufen
- **Nicht:** Maßnahmen abwählen

Änderungen wirken ab der **nächsten** Welle!

---

## GLOSSAR

| Begriff | Bedeutung |
|---------|-----------|
| **KZ** | Kundenzufriedenheit (0-100, bei 0: Vertrag verloren!) |
| **CIA** | Confidentiality, Integrity, Availability |
| **E-Wert** | Erfüllungsgrad (gewichtete CIA-Summe) |
| **E-Ziel** | Mindestwert für E-Wert pro Welle |
| **Init** | Einmalige Anschaffungskosten |
| **OPEX** | Laufende Kosten pro Welle |
| **RoS** | Return on Security (Rendite der Investition) |
| **OT** | Operational Technology (Produktionssysteme) |
| **baseSeverity** | Ausgangsschwere eines Angriffs |
| **Mitigation** | Abschwächung durch Maßnahmen |
| **G** | Endschwere nach Mitigation |

---

## TIPPS

1. **Budget klug einteilen:** Init + 3× OPEX + Puffer für Schäden!
2. **Kontext beachten:** Nicht jede Maßnahme passt zu MechTech
3. **OT nicht vergessen:** Welle 2 trifft OT hart!
4. **Awareness lohnt sich:** Günstig und hohe Wirkung
5. **Backups retten:** Reduzieren Schaden nach Angriff
6. **Abhängigkeiten prüfen:** Sonst wirkt L3 nicht!

---

**Viel Erfolg! Schützt MechTech!**
