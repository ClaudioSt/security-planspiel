# QUICK-REFERENCE CARD - Moderatoren

**CIA-Planspiel Automotive | 1-Seiter zum Ausdrucken**

---

## BUDGET-TIERS

| Tier | Budget | KZ-Start | E-Ziele | Balancing-Event |
|------|--------|----------|---------|-----------------|
| **LOW** | 200-250k | 70 | 18/20/22 | -3 KZ (nach W2) |
| **MED** | 300-350k | 60 | 18/20/22 | - |
| **HIGH** | 400-450k | 50 | 18/20/22 | +8 KZ (nach W3) |

---

## WELLEN-PARAMETER

| Welle | Angriff | baseSev | sUnit | kzUnit | Cap | wC/wI/wA | E-Ziel | Bonus/Malus |
|-------|---------|---------|-------|--------|-----|----------|--------|-------------|
| **1** | Ransomware | 8 | 20 | 3 | 10 | 0.4/0.4/0.2 | 18 | +3 / -5 |
| **2** | OT-Stoerung | 10 | 32 | 3 | 12 | 0.2/0.2/0.6 | 20 | +5 / -8 |
| **3** | Exfiltration | 7 | 20 | 3 | 10 | 0.5/0.3/0.2 | 22 | +8 / -10 |

**Base Losses: 620k** (160 + 320 + 140)

---

## FORMELN (Schritt fuer Schritt)

```
1. M_sum = min(CAP, Summe aller Mitigations)
2. G = max(0, baseSeverity - M_sum)
3. Damage = G x sUnit
4. Damage_final = Damage x (1 - Recovery%)  [M4: L1=10%, L2=30%, L3=50%]
5. Delta_KZ = -(G x kzUnit)
6. E = Team_C x wC + Team_I x wI + Team_A x wA
7. E >= E-Ziel? -> KZ-Bonus, sonst KZ-Malus
```

---

## TOP-MITIGATIONS PRO WELLE

| Welle | Beste Massnahmen |
|-------|------------------|
| **1 Ransomware** | M6 L3 (-6), M3 L3 (-5), M4 L3 (-5), M1/M2 L3 (-3) |
| **2 OT-Stoerung** | M5 L3 (-7), M7 L3 (-4), M2 L3 (-2), M4/M8 L3 (-2) |
| **3 Exfiltration** | M1 L3 (-4), M2 L3 (-4), M8 L3 (-3), M3 L3 (-3) |

---

## EVENTS-CHECKLISTE

| Event | Wann | Bedingung | Effekt |
|-------|------|-----------|--------|
| OEM-Audit | Nach W2 | E(W1) >= 18? | Ja: +5 KZ / Nein: -3 KZ |
| Fluktuation | Nach W1 | M6 < L2? | OPEX +5, KZ -2 |
| DSGVO-Bonus | Nach W2 | M1>=L2 UND M2>=L2? | KZ +3, Budget +10 |
| Compliance-Gap | Nach W2 | Nur LOW-Tier | KZ -3 (automatisch) |
| Investor Conf. | Nach W3 | Nur HIGH-Tier | KZ +8 (automatisch) |

---

## ABLAUF-CHECKLISTE

```
[ ] DISCOVERY (25 Min)
    -> Budget-Tier festlegen

[ ] MASSNAHMENWAHL (20 Min)
    -> Abhaengigkeiten pruefen!
    -> Init + 3x OPEX <= Budget?

[ ] WELLE 1 - Ransomware
    -> M_sum berechnen
    -> G, Damage, KZ-Delta
    -> E-Wert pruefen (Ziel: 18)
    -> Event: Fluktuation pruefen

[ ] CHANGE 1 (15 Min)

[ ] WELLE 2 - OT-Stoerung
    -> M_sum berechnen (Cap: 12!)
    -> G, Damage, KZ-Delta
    -> E-Wert pruefen (Ziel: 20)
    -> Events: OEM-Audit, DSGVO, Compliance-Gap

[ ] CHANGE 2 (15 Min)

[ ] WELLE 3 - Exfiltration
    -> M_sum berechnen
    -> G, Damage, KZ-Delta
    -> E-Wert pruefen (Ziel: 22)
    -> Event: Investor Confidence (HIGH)

[ ] AUSWERTUNG
    -> RoS berechnen
    -> Final-Index (KZ + RoS x 0.25)
```

---

## RoS-BERECHNUNG

```
Gesamtkosten = Init + (OPEX x 3) + Event-Strafen
Verluste = Summe(Damage_final)
Vermieden = 620 - Verluste
RoS = (Vermieden - Gesamtkosten) / Gesamtkosten x 100%
```

---

## ABHAENGIGKEITEN

| Massnahme L3 | Benoetigt |
|--------------|-----------|
| M1 (IAM) L3 | M2 >= L2 |
| M3 (EDR) L3 | M2 >= L2 |
| M7 (Patch) L3 | M2 >= L1 |

---

## NOTFALL-ANPASSUNGEN

Falls Balance off:
- **Zu leicht:** sUnit +5 pro Welle
- **Zu schwer:** kzUnit auf 2 reduzieren
- **KZ kollabiert:** E-Ziele um 2 senken

---

*Drucken: A4, beidseitig = 1 Blatt pro Moderator*
