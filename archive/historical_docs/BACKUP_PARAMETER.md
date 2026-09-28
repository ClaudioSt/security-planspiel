# BACKUP-PARAMETER

**Notfall-Anpassungen waehrend des Playtests**

---

## WANN ANPASSEN?

Greife zu diesen Backup-Werten, wenn du **waehrend des Spiels** merkst:

| Problem | Symptom | Loesung |
|---------|---------|---------|
| **Zu leicht** | Alle Teams Severity=0 in Welle 1 | sUnit erhoehen |
| **Zu schwer** | KZ faellt unter 20 nach W2 | kzUnit reduzieren |
| **Frustration** | Teams erreichen nie E-Ziele | E-Ziele senken |
| **Langeweile** | Kein Unterschied zwischen Teams | Events aktivieren |

---

## PARAMETER-STANDARD (aktuell getestet)

| Parameter | Welle 1 | Welle 2 | Welle 3 |
|-----------|---------|---------|---------|
| baseSeverity | 8 | 10 | 7 |
| sUnit | 20 | 32 | 20 |
| kzUnit | 2 | 2 | 2 |
| Cap | 8 | 10 | 7 |
| E-Ziel | 15 | 17 | 19 |
| e_divisor | 1 | 1 | 1 |

### Budget-Tiers (gleiches Unternehmen)

| Tier | Budget | KZ-Start | Severity-Mult | E-Ziele |
|------|--------|----------|---------------|---------|
| Low | 300k | 60 | 1.0 | 15/17/19 |
| Medium | 400k | 60 | 1.0 | 15/17/19 |
| High | 500k | 60 | 1.0 | 15/17/19 |

---

## OPTION A: LEICHTER (falls Teams ueberfordert)

| Parameter | Welle 1 | Welle 2 | Welle 3 |
|-----------|---------|---------|---------|
| baseSeverity | 8 | 10 | 7 |
| sUnit | 16 | 26 | 16 |
| kzUnit | **1** | **1** | **1** |
| Cap | 8 | 10 | 7 |
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
| kzUnit | **3** | **3** | **3** |
| Cap | 8 | 10 | 7 |
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
- ODER: kzUnit fuer W2/W3 auf 1 reduzieren

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

### KZ-Verlust bei Severity=X

| Sev | kzUnit=1 | kzUnit=2 | kzUnit=3 |
|-----|----------|----------|----------|
| 1 | -1 | -2 | -3 |
| 2 | -2 | -4 | -6 |
| 3 | -3 | -6 | -9 |
| 4 | -4 | -8 | -12 |
| 5 | -5 | -10 | -15 |

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
