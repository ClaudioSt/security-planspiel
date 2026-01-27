# QUICK-REFERENCE CARD - Moderatoren

**CIA-Planspiel Automotive | 1-Seiter zum Ausdrucken**

---

## BUDGET-TIERS (gleiches Unternehmen, nur Budget variiert)

| Tier | Budget | KZ-Start | E-Ziele | Sev-Mult |
|------|--------|----------|---------|----------|
| **LOW** | 300k | 60 | 15/17/19 | 1.0 |
| **MED** | 400k | 60 | 15/17/19 | 1.0 |
| **HIGH** | 500k | 60 | 15/17/19 | 1.0 |

---

## WELLEN-PARAMETER

| Welle | Angriff | baseSev | sUnit | kzUnit | Cap | wC/wI/wA | E-Ziel | Bonus/Malus |
|-------|---------|---------|-------|--------|-----|----------|--------|-------------|
| **1** | Ransomware | 8 | 20 | 2 | 8 | 0.4/0.4/0.2 | 15 | +5 / -3 |
| **2** | OT-Stoerung | 10 | 32 | 2 | 10 | 0.2/0.2/0.6 | 17 | +7 / -5 |
| **3** | Exfiltration | 7 | 20 | 2 | 7 | 0.5/0.3/0.2 | 19 | +10 / -7 |

**Base Losses: 620k** (160 + 320 + 140)

---

## FORMELN (Schritt fuer Schritt)

```
1. E = Team_C x wC + Team_I x wI + Team_A x wA
2. severity_reduction = (E - e_threshold) / e_divisor  [e_divisor=1]
3. bonus_reduction = Summe der Bonus-Measures (wenn >= L2)
4. final_severity = max(0, baseSeverity - severity_reduction - bonus_reduction)
5. Damage = final_severity x sUnit
6. Damage_final = Damage x (1 - Recovery%)  [M4: L1=10%, L2=30%, L3=50%]
7. Delta_KZ = -(final_severity x kzUnit)
8. E >= E-Ziel? -> KZ-Bonus, sonst KZ-Malus
```

---

## BONUS-MEASURES PRO WELLE

| Welle | Bonus-Massnahmen (L2+) | Max Bonus |
|-------|------------------------|-----------|
| **1 Ransomware** | M3 (+2), M4 (+2), M6 (+1) | +5 |
| **2 OT-Stoerung** | M5 (+3), M7 (+2) | +5 |
| **3 Exfiltration** | M1 (+2), M2 (+2), M8 (+1) | +5 |

---

## EVENTS-CHECKLISTE

| Event | Wann | Bedingung | Effekt positiv | Effekt negativ |
|-------|------|-----------|----------------|----------------|
| Phishing-Kampagne | W1 | M6 >= L2? | KZ +2 | KZ -3 |
| Versicherung | W1 | E >= 16? | Budget +10 | Budget -15 |
| Schwachstelle | W1 | M7 >= L1? | KZ 0 | KZ -2 |
| OEM-Audit | W2 | E >= 18? | KZ +5 | KZ -5 |
| Produktionsdruck | W2 | M5 >= L1? | KZ 0 | OPEX +8 |
| Security-Experte kuendigt | W2 | M2 >= L2? | KZ 0 | KZ -3, OPEX +5 |
| NIS2-Pruefung | W3 | 4+ Mass. auf L2? | KZ +5 | KZ -5, Budget -15 |
| Lieferanten-Panne | W3 | M8 >= L2? | KZ +3 | KZ -3 |
| Vorstandspraesentation | W3 | E >= 20? | KZ +3 | KZ -2 |

---

## ABLAUF-CHECKLISTE

```
[ ] DISCOVERY (25 Min)
    -> Budget-Tier festlegen

[ ] MASSNAHMENWAHL (20 Min)
    -> Abhaengigkeiten pruefen!
    -> Init + 3x OPEX <= Budget?

[ ] WELLE 1 - Ransomware
    -> E-Wert berechnen (Ziel: 15)
    -> Severity-Reduktion berechnen
    -> Bonus-Measures pruefen (M3, M4, M6)
    -> Damage, KZ-Delta
    -> Events pruefen

[ ] CHANGE 1 (15 Min)

[ ] WELLE 2 - OT-Stoerung
    -> E-Wert berechnen (Ziel: 17)
    -> Bonus-Measures (M5, M7)
    -> Damage, KZ-Delta
    -> Events pruefen

[ ] CHANGE 2 (15 Min)

[ ] WELLE 3 - Exfiltration
    -> E-Wert berechnen (Ziel: 19)
    -> Bonus-Measures (M1, M2, M8)
    -> Damage, KZ-Delta
    -> Events pruefen

[ ] AUSWERTUNG
    -> RoS berechnen
    -> Combined Score (KZ*0.6 + ROS*0.3 + Dmg*0.1)
```

---

## RoS-BERECHNUNG

```
Gesamtkosten = Init + (OPEX x 3) + Event-Strafen
Verluste = Summe(Damage_final)
Vermieden = 620 - Verluste
RoS = (Vermieden - Gesamtkosten) / Gesamtkosten
```

---

## ABHAENGIGKEITEN

| Massnahme L3 | Benoetigt |
|--------------|-----------|
| M1 (IAM) L3 | M2 >= L2 |
| M3 (EDR) L3 | M2 >= L2 |
| M7 (Patch) L3 | M2 >= L1 |

---

## BALANCE-REFERENZ (getestet mit 27 Strategien)

| Tier | Best Score | Worst Score | Positive Outcomes |
|------|------------|-------------|-------------------|
| Low | 71.4 | 29.3 | 7/11 (64%) |
| Medium | 80.6 | 29.3 | 14/18 (78%) |
| High | 79.5 | 29.3 | 20/24 (83%) |

---

*Drucken: A4, beidseitig = 1 Blatt pro Moderator*
