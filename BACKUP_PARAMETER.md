# BACKUP-PARAMETER

**Notfall-Anpassungen waehrend des Playtests**

---

## WANN ANPASSEN?

Greife zu diesen Backup-Werten, wenn du **waehrend des Spiels** merkst:

| Problem | Symptom | Loesung |
|---------|---------|---------|
| **Zu leicht** | Alle Teams Severity=0 in Welle 1 | sUnit erhoehen |
| **Zu schwer** | KZ faellt unter 20 nach W2 | kz_at_full_damage/kz_at_full_mitigation Spanne reduzieren |
| **Frustration** | Teams erreichen nie E-Ziele | E-Ziele senken |
| **Langeweile** | Kein Unterschied zwischen Teams | Events aktivieren |

---

## PARAMETER-STANDARD (aktuell getestet)

| Parameter | Welle 1 | Welle 2 | Welle 3 |
|-----------|---------|---------|---------|
| baseSeverity | 8 | 10 | 7 |
| sUnit | 20 | 32 | 20 |
| kz_at_full_damage | -6 | -5 | -7 |
| kz_at_full_mitigation | 10 | 7 | 10 |
| mitigation_cap | 8 | 10 | 7 |
| e_threshold (Angriffsformel, fix) | 15 | 17 | 19 |

### Budget-Tiers (gleiches Unternehmen)

| Tier | Budget | KZ-Start | Severity-Mult | E-Ziele (KZ-Bonus/Malus) |
|------|--------|----------|---------------|---------------------------|
| Low | 300k | 60 | 1.0 | 15/17/19 |
| Medium | 400k | 60 | 1.0 | 17/19/21 |
| High | 500k | 60 | 1.0 | 19/21/23 |

*Die E-Ziele (KZ-Bonus/Malus-Check) skalieren mit dem Budget-Tier (Medium = Low+2, High = Low+4 je Welle). Der `e_threshold` der Angriffsformel oben bleibt unabhaengig davon fix fuer alle Tiers.*

---

## OPTION A: LEICHTER (falls Teams ueberfordert)

| Parameter | Welle 1 | Welle 2 | Welle 3 |
|-----------|---------|---------|---------|
| baseSeverity | 8 | 10 | 7 |
| sUnit | 16 | 26 | 16 |
| kz_at_full_damage | **-3** | **-3** | **-4** |
| kz_at_full_mitigation | 10 | 7 | 10 |
| mitigation_cap | 8 | 10 | 7 |
| E-Ziel | **13** | **15** | **17** |

**Effekt:**
- Weniger KZ-Verlust pro Severity
- Niedrigere E-Ziele = leichter Bonus zu erreichen
- Base Losses sinken auf ~500k

---

## OPTION B: SCHWERER (falls zu einfach)

| Parameter | Welle 1 | Welle 2 | Welle 3 |
|-----------|---------|---------|---------|
| baseSeverity | 8 | 10 | 7 |
| sUnit | **24** | **38** | **24** |
| kz_at_full_damage | **-9** | **-8** | **-10** |
| kz_at_full_mitigation | 10 | 7 | 10 |
| mitigation_cap | 8 | 10 | 7 |
| E-Ziel | **17** | **19** | **21** |

**Effekt:**
- Hoeherer KZ-Verlust pro Severity
- Base Losses steigen auf ~764k
- RoS wird attraktiver

---

## SCHNELL-ANPASSUNGEN (Mid-Game)

### Nach Welle 1: KZ zu niedrig?

**Problem:** Team hat nach W1 schon KZ < 40

**Fix:**
- Recovery-Bonus: "MechTech hat gute Cyber-Versicherung entdeckt"
- +10 KZ einmalig
- ODER: kz_at_full_damage fuer W2/W3 abmildern (naeher an 0)

### Nach Welle 2: Alle Teams am Boden?

**Problem:** Alle Teams KZ < 30

**Fix:**
- "OEM gibt Aufschub fuer Zertifizierung"
- Alle Teams +5 KZ
- E-Ziel W3 auf 17 senken

---

## EVENT-UEBERSICHT (aktuell)

### Welle 1 Events
| Event | Bedingung | Positiv | Negativ |
|-------|-----------|---------|---------|
| Phishing-Kampagne | M6 >= L2 | KZ +2 | KZ -3 |
| Versicherung | E >= 16 | Budget +10 | Budget -15 |
| Schwachstelle | M7 >= L1 | KZ 0 | KZ -2 |

### Welle 2 Events
| Event | Bedingung | Positiv | Negativ |
|-------|-----------|---------|---------|
| OEM-Audit | E >= 18 | KZ +5 | KZ -5 |
| Produktionsdruck | M5 >= L1 | KZ 0 | OPEX +8 |
| Security-Experte | M2 >= L2 | KZ 0 | KZ -3, OPEX +5 |

### Welle 3 Events
| Event | Bedingung | Positiv | Negativ |
|-------|-----------|---------|---------|
| NIS2-Pruefung | 4+ Mass. L2 | KZ +5 | KZ -5, Budget -15 |
| Lieferanten-Panne | M8 >= L2 | KZ +3 | KZ -3 |
| Vorstandspraes. | E >= 20 | KZ +3 | KZ -2 |

---

## FORMELN ZUM NACHRECHNEN

### Base Losses (zur Kontrolle)

```
Standard:  8x20 + 10x32 + 7x20 = 160 + 320 + 140 = 620k
Option A:  8x16 + 10x26 + 7x16 = 128 + 260 + 112 = 500k
Option B:  8x24 + 10x38 + 7x24 = 192 + 380 + 168 = 740k
```

### KZ-Delta bei mitigation_fraction=X (Welle 1, kz_at_full_damage=-6, kz_at_full_mitigation=10)

```
kz_delta = kz_at_full_damage + mitigation_fraction * (kz_at_full_mitigation - kz_at_full_damage)
```

| mitigation_fraction | kz_delta |
|----------------------|----------|
| 0.0 (Fall 1: keine Reduktion) | -6 |
| 0.25 | -2 |
| 0.5 | 2 |
| 0.75 | 6 |
| 1.0 (Fall 2: volle Mitigation) | 10 |

---

## BALANCE-REFERENZ (27 Strategien getestet)

| Tier | Best Score | Worst Score | Positive (KZ>=50) |
|------|------------|-------------|-------------------|
| Low | 71.4 | 29.3 | 64% (7/11) |
| Medium | 80.6 | 29.3 | 78% (14/18) |
| High | 79.5 | 29.3 | 83% (20/24) |

---

## NOTIZEN-FELD

Waehrend Playtest hier notieren, welche Anpassungen gemacht wurden:

| Zeitpunkt | Anpassung | Grund | Effekt |
|-----------|-----------|-------|--------|
| | | | |
| | | | |
| | | | |
| | | | |

---

*Dieses Blatt griffbereit halten, aber nur bei echten Problemen nutzen!*
