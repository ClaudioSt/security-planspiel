# PARAMETER-TABELLE - MVP v2.0

**Alle Spielwerte auf einen Blick**
*Diese Tabelle in Excel/Google Sheets übertragen für einfache Anpassungen*

---

## 1. BUDGET-PARAMETER

| Parameter | Wert | Beschreibung |
|-----------|------|--------------|
| **Budget-Einheit** | 1.000 Euro | 1 Budgetpunkt = 1.000 Euro |
| **Budget-Schritte** | 100k | Feste Schritte zwischen Tiers |
| **Budget-Tiers** | 300 (low), 400 (medium), 500 (high) | |

### Budget-Tiers (GLEICHES UNTERNEHMEN)

**WICHTIG:** Alle Tiers repräsentieren das GLEICHE Unternehmen mit identischen Angriffen!

| Tier | Budget (k Euro) | KZ-Start | E-Ziel W1 | E-Ziel W2 | E-Ziel W3 | Sev-Mult |
|------|-----------------|----------|-----------|-----------|-----------|----------|
| **Low** | 300 | 60 | 15 | 17 | 19 | 1.0 |
| **Medium** | 400 | 60 | 17 | 19 | 21 | 1.0 |
| **High** | 500 | 60 | 19 | 21 | 23 | 1.0 |

**Hinweis:** Die E-Ziele (KZ-Bonus/Malus-Check, siehe FORMULARE.md) skalieren mit dem Budget-Tier: Medium = Low + 2, High = Low + 4 (pro Welle). Dies hält die Erreichungswahrscheinlichkeit über alle Tiers annähernd konstant (~99% W1, ~94-95% W2, ~89-91% W3). Der `e_threshold` der Angriffsformel (Welle 2 unten) ist davon unabhängig und bleibt für alle Tiers fix bei 15/17/19, da er auf dem gedruckten Papier-Arbeitsblatt steht.

**Simulierte Ergebnisse (27 Strategien getestet):**
| Tier | Strategien moeglich | Best Score | Worst Score | Positive (KZ>=50) |
|------|---------------------|------------|-------------|-------------------|
| Low | 11 | 71.4 | 29.3 | 64% |
| Medium | 18 | 80.6 | 29.3 | 78% |
| High | 24 | 79.5 | 29.3 | 83% |

---

## 2. WELLEN-PARAMETER

| Welle | Angriff | wC | wI | wA | e_threshold | baseSev | sUnit | mitigation_cap | kz_at_full_damage | kz_at_full_mitigation | KZ-Bonus | KZ-Malus |
|-------|---------|----|----|----|--------------------|---------|-------|-----------------|---------------------|--------------------------|----------|----------|
| 1 | Ransomware | 0.4 | 0.4 | 0.2 | **15** | 8 | 20 | 8 | -6 | 5 | +5 | -3 |
| 2 | OT-Stoerung | 0.2 | 0.2 | 0.6 | **17** | 10 | 32 | 10 | -5 | 3.5 | +7 | -5 |
| 3 | Exfiltration | 0.5 | 0.3 | 0.2 | **19** | 7 | 20 | 7 | -7 | 5 | +10 | -7 |

*Hinweis: `e_threshold` in dieser Tabelle ist der Angriffs-Schwellwert (fix für alle Budget-Tiers), nicht zu verwechseln mit dem tier-abhängigen E-Ziel der KZ-Bonus/Malus-Prüfung (siehe Tabelle in Abschnitt 1).*

**Basis-Verluste:** 8x20 + 10x32 + 7x20 = 160 + 320 + 140 = **620k Euro**

### Bonus-Measures pro Welle

| Welle | Bonus-Massnahmen (L2+) | Bonus | Max |
|-------|------------------------|-------|-----|
| 1 Ransomware | M3 (+2), M4 (+2), M6 (+1) | +5 | +5 |
| 2 OT-Stoerung | M5 (+3), M7 (+2) | +5 | +5 |
| 3 Exfiltration | M1 (+2), M2 (+2), M8 (+1) | +5 | +5 |

---

## 3. MASSNAHMEN-PARAMETER

### Kosten-Referenz (Init + 3*OPEX)

| Level | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 | M9 | M10 |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| **L1** | 42 | 26 | 36 | 34 | 46 | 16 | 32 | 28 | 27 | 18 |
| **L2** | 90 | 74 | 86 | 76 | 88 | 42 | 68 | 60 | 61 | 43 |

### M1: IAM/PAM

| Level | CIA (C/I/A) | Init | OPEX | Total (3W) | Abhaengigkeit |
|-------|-------------|------|------|------------|---------------|
| L1 | 2/1/0 | 30 | 4 | 42 | - |
| L2 | 4/3/0 | 60 | 10 | 90 | - |
| L3 | 6/5/1 | 100 | 20 | 160 | M2 >= L2 |

**Bonus Welle 3 (Exfil):** +2 bei L2+

---

### M2: Logging & SIEM/MDR

| Level | CIA (C/I/A) | Init | OPEX | Total (3W) | Abhaengigkeit |
|-------|-------------|------|------|------------|---------------|
| L1 | 1/3/0 | 20 | 2 | 26 | - |
| L2 | 2/5/1 | 50 | 8 | 74 | - |
| L3 | 3/7/2 | 80 | 24 | 152 | - |

**Bonus Welle 3 (Exfil):** +2 bei L2+

---

### M3: EDR/XDR

| Level | CIA (C/I/A) | Init | OPEX | Total (3W) | Abhaengigkeit |
|-------|-------------|------|------|------------|---------------|
| L1 | 3/2/1 | 24 | 4 | 36 | - |
| L2 | 5/4/2 | 56 | 10 | 86 | - |
| L3 | 7/6/3 | 90 | 18 | 144 | M2 >= L2 |

**Bonus Welle 1 (Ransomware):** +2 bei L2+

---

### M4: Backup & Disaster Recovery

| Level | CIA (C/I/A) | Init | OPEX | Total (3W) | Recovery | Abhaengigkeit |
|-------|-------------|------|------|------------|----------|---------------|
| L1 | 0/4/3 | 16 | 6 | 34 | 10% | - |
| L2 | 1/6/5 | 40 | 12 | 76 | 30% | - |
| L3 | 1/8/7 | 80 | 20 | 140 | 50% | - |

**Bonus Welle 1 (Ransomware):** +2 bei L2+
**Recovery:** Reduziert Schaden nach Angriff (nur bei allow_recovery=true)

---

### M5: OT/IT-Netz-Segmentierung

| Level | CIA (C/I/A) | Init | OPEX | Total (3W) | Abhaengigkeit |
|-------|-------------|------|------|------------|---------------|
| L1 | 2/1/4 | 40 | 2 | 46 | - |
| L2 | 3/2/6 | 70 | 6 | 88 | - |
| L3 | 4/3/8 | 110 | 12 | 146 | - |

**Bonus Welle 2 (OT):** +3 bei L2+ (Kern-Massnahme!)

---

### M6: Security Awareness & Training

| Level | CIA (C/I/A) | Init | OPEX | Total (3W) | Abhaengigkeit |
|-------|-------------|------|------|------------|---------------|
| L1 | 2/1/1 | 10 | 2 | 16 | - |
| L2 | 3/2/2 | 24 | 6 | 42 | - |
| L3 | 5/3/3 | 40 | 10 | 70 | - |

**Bonus Welle 1 (Ransomware):** +1 bei L2+

---

### M7: Vulnerability & Patch Management

| Level | CIA (C/I/A) | Init | OPEX | Total (3W) | Abhaengigkeit |
|-------|-------------|------|------|------------|---------------|
| L1 | 2/3/2 | 20 | 4 | 32 | - |
| L2 | 4/5/3 | 44 | 8 | 68 | - |
| L3 | 6/7/4 | 76 | 14 | 118 | M2 >= L1 |

**Bonus Welle 2 (OT):** +2 bei L2+

---

### M8: Supplier Security & Supply Chain

| Level | CIA (C/I/A) | Init | OPEX | Total (3W) | Abhaengigkeit |
|-------|-------------|------|------|------------|---------------|
| L1 | 1/2/2 | 16 | 4 | 28 | - |
| L2 | 2/4/4 | 36 | 8 | 60 | - |
| L3 | 3/6/6 | 70 | 16 | 118 | - |

**Bonus Welle 3 (Exfil):** +1 bei L2+

---

### M9: Cloud Security (CSPM) - SUBOPTIMAL

| Level | CIA (C/I/A) | Init | OPEX | Total (3W) | Abhaengigkeit |
|-------|-------------|------|------|------------|---------------|
| L1 | 2/2/1 | 18 | 3 | 27 | - |
| L2 | 3/3/2 | 40 | 7 | 61 | - |
| L3 | 4/4/3 | 70 | 14 | 112 | - |

**TRAP:** Keine Bonus-Measures! Nur CIA-Wert.

---

### M10: Mobile Device Management (MDM) - SUBOPTIMAL

| Level | CIA (C/I/A) | Init | OPEX | Total (3W) | Abhaengigkeit |
|-------|-------------|------|------|------------|---------------|
| L1 | 1/1/0 | 12 | 2 | 18 | - |
| L2 | 2/2/1 | 28 | 5 | 43 | - |
| L3 | 3/3/2 | 50 | 10 | 80 | - |

**TRAP:** Keine Bonus-Measures! Nur CIA-Wert.

---

## 4. EVENT-PARAMETER

### Welle 1 Events

| Event | Bedingung | Positiv | Negativ |
|-------|-----------|---------|---------|
| Phishing-Kampagne | M6 >= L2? | KZ +2 | KZ -3 |
| Versicherung Pruefung | E >= 16? | Budget +10 | Budget -15 |
| Kritische Schwachstelle | M7 >= L1? | KZ 0 | KZ -2 |

### Welle 2 Events

| Event | Bedingung | Positiv | Negativ |
|-------|-----------|---------|---------|
| OEM-Audit | E >= 18? | KZ +5 | KZ -5 |
| Produktionsdruck | M5 >= L1? | KZ 0 | OPEX +8 |
| Security-Experte kuendigt | M2 >= L2? | KZ 0 | KZ -3, OPEX +5 |

### Welle 3 Events

| Event | Bedingung | Positiv | Negativ |
|-------|-----------|---------|---------|
| NIS2-Pruefung | 4+ Massnahmen auf L2? | KZ +5 | KZ -5, Budget -15 |
| Lieferanten-Panne | M8 >= L2? | KZ +3 | KZ -3 |
| Vorstandspraesentation | E >= 20? | KZ +3 | KZ -2 |

---

## 5. FORMELN

### Mitigation-Berechnung (E-Value basiert)
```
1. E = Team_C x wC + Team_I x wI + Team_A x wA
2. gesamtreduktion = E + bonus_reduction  [bonus_reduction = Summe der Bonus-Measures bei Level >= 2]
3. reduktion_ueber_schwelle = clamp(0, mitigation_cap, gesamtreduktion - e_threshold)
4. effective_base_severity = baseSeverity x severity_multiplier
5. final_severity = max(0, effective_base_severity - reduktion_ueber_schwelle)
```

### Schaden-Berechnung
```
Damage = final_severity x sUnit
Damage_final = Damage x (1 - Recovery%)  [falls allow_recovery=true]
```

### KZ-Delta
```
mitigation_fraction = reduktion_ueber_schwelle / mitigation_cap
Delta_KZ = kz_at_full_damage + mitigation_fraction x (kz_at_full_mitigation - kz_at_full_damage)
E >= E-Ziel? -> +KZ_Bonus, sonst +KZ_Malus   [E-Ziel = tier-abhaengiges Ziel aus Abschnitt 1, separat von e_threshold]
KZ_neu = clamp(KZ_alt + Delta_KZ + Bonus/Malus, 0, 100)
```

### Return on Security (RoS)
```
Gesamtkosten = Init + (OPEX x 3) + Event-Strafen
Verluste = Summe(Damage_final)
Vermieden = 620 - Verluste
RoS = (Vermieden - Gesamtkosten) / Gesamtkosten
```

### Combined Score
```
Score = KZ_final x 0.6 + ROS_normalized x 0.3 + Damage_component x 0.1
wobei:
  ROS_normalized = max(0, min(100, (ROS + 1) x 33.33))
  Damage_component = max(0, min(100, 100 - (Damage / 5000)))
```

---

## 6. ABHAENGIGKEITEN

| Massnahme L3 | Benoetigt |
|--------------|-----------|
| M1 (IAM) L3 | M2 >= L2 |
| M3 (EDR) L3 | M2 >= L2 |
| M7 (Patch) L3 | M2 >= L1 |

---

**Diese Tabelle ist die zentrale Referenz fuer alle Zahlen im Spiel!**
