# BACKUP-PARAMETER

**Notfall-Anpassungen waehrend des Playtests**

---

## WANN ANPASSEN?

Greife zu diesen Backup-Werten, wenn du **waehrend des Spiels** merkst:

| Problem | Symptom | Loesung |
|---------|---------|---------|
| **Zu leicht** | Alle Teams G=0 in Welle 1 | sUnit erhoehen |
| **Zu schwer** | KZ faellt unter 20 nach W2 | kzUnit reduzieren |
| **Frustration** | Teams erreichen nie E-Ziele | E-Ziele senken |
| **Langeweile** | Kein Unterschied zwischen Teams | Events aktivieren |
| **Unbalance** | Ein Tier klar im Vorteil | Tier-Event anpassen |

---

## PARAMETER-ALTERNATIVEN

### Standard-Werte (aktuell)

| Parameter | Welle 1 | Welle 2 | Welle 3 |
|-----------|---------|---------|---------|
| baseSeverity | 8 | 10 | 7 |
| sUnit | 20 | 32 | 20 |
| kzUnit | 3 | 3 | 3 |
| Cap | 10 | 12 | 10 |
| E-Ziel | 18 | 20 | 22 |

### Option A: LEICHTER (falls Teams ueberfordert)

| Parameter | Welle 1 | Welle 2 | Welle 3 |
|-----------|---------|---------|---------|
| baseSeverity | 8 | 10 | 7 |
| sUnit | 16 | 26 | 16 |
| kzUnit | **2** | **2** | **2** |
| Cap | 10 | 12 | 10 |
| E-Ziel | **16** | **18** | **20** |

**Effekt:**
- Weniger KZ-Verlust pro Severity
- Niedrigere E-Ziele = leichter Bonus zu erreichen
- Base Losses sinken auf ~504k

### Option B: SCHWERER (falls zu einfach)

| Parameter | Welle 1 | Welle 2 | Welle 3 |
|-----------|---------|---------|---------|
| baseSeverity | 8 | 10 | 7 |
| sUnit | **24** | **38** | **24** |
| kzUnit | **4** | **4** | **4** |
| Cap | 10 | 12 | 10 |
| E-Ziel | 18 | 20 | 22 |

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
- ODER: kzUnit fuer W2/W3 auf 2 reduzieren

### Nach Welle 2: Alle Teams am Boden?

**Problem:** Alle Teams KZ < 30

**Fix:**
- "OEM gibt Aufschub fuer Zertifizierung"
- Alle Teams +5 KZ
- E-Ziel W3 auf 20 senken

### Nach Welle 2: Ein Tier dominiert?

**Problem:** LOW-Team hat viel hoehere KZ als HIGH

**Fix:**
- Investor Confidence auch nach W2 anwenden (+5 statt +8)
- ODER: Compliance-Gap auf -5 erhoehen

**Problem:** HIGH-Team hat viel hoehere KZ als LOW

**Fix:**
- Compliance-Gap streichen
- ODER: zusaetzlicher "Startup-Agilitaets-Bonus" fuer LOW: +5 KZ

---

## EVENT-VARIANTEN

### Standard-Events

| Event | Trigger | Effekt |
|-------|---------|--------|
| Fluktuation | M6 < L2 | OPEX +5, KZ -2 |
| OEM-Audit | Nach W2 | E1>=18: +5 / <18: -3 |
| DSGVO-Bonus | M1>=L2, M2>=L2 | KZ +3, Budget +10 |
| Compliance-Gap | LOW nach W2 | KZ -3 |
| Investor Confidence | HIGH nach W3 | KZ +8 |

### Alternative Events (bei Bedarf aktivieren)

| Event | Trigger | Effekt | Wann nutzen |
|-------|---------|--------|-------------|
| **Supply Chain Bonus** | M8 >= L2 | KZ +4 | Falls W3 zu hart |
| **Patch-Luecke** | M7 < L2 nach W2 | KZ -4 | Falls W2 zu leicht |
| **Recovery-Held** | M4 = L3 | Schaden W3 -20% extra | Belohnung fuer Backup-Fokus |
| **OT-Desaster** | M5 < L2 nach W2 | KZ -6 | Falls OT ignoriert wird |

---

## FORMELN ZUM NACHRECHNEN

### Base Losses (zur Kontrolle)

```
Standard:  8×20 + 10×32 + 7×20 = 160 + 320 + 140 = 620k
Option A:  8×16 + 10×26 + 7×16 = 128 + 260 + 112 = 500k
Option B:  8×24 + 10×38 + 7×24 = 192 + 380 + 168 = 740k
```

### KZ-Verlust bei G=X

| G | kzUnit=2 | kzUnit=3 | kzUnit=4 |
|---|----------|----------|----------|
| 1 | -2 | -3 | -4 |
| 2 | -4 | -6 | -8 |
| 3 | -6 | -9 | -12 |
| 4 | -8 | -12 | -16 |
| 5 | -10 | -15 | -20 |

### Schaden bei G=X

| G | sUnit=16 | sUnit=20 | sUnit=24 |
|---|----------|----------|----------|
| 1 | 16k | 20k | 24k |
| 2 | 32k | 40k | 48k |
| 3 | 48k | 60k | 72k |
| 4 | 64k | 80k | 96k |
| 5 | 80k | 100k | 120k |

---

## ENTSCHEIDUNGSBAUM

```
Nach Welle 1:
│
├── KZ aller Teams > 50?
│   └── Weiter mit Standard
│
├── Ein Team KZ < 40?
│   └── Option: +10 KZ Recovery-Bonus
│
└── Alle Teams KZ < 40?
    └── kzUnit auf 2 fuer Rest


Nach Welle 2:
│
├── Spread zwischen Teams < 15?
│   └── Weiter mit Standard
│
├── LOW-Team fuehrt deutlich?
│   └── Investor Confidence vorziehen
│
└── HIGH-Team fuehrt deutlich?
    └── Compliance-Gap streichen


Nach Welle 3:
│
├── RoS negativ fuer alle?
│   └── Fuer Debrief: "Base Losses waren 620k"
│
└── Final-Index Spread > 20?
    └── Fuer naechstes Spiel: Events anpassen
```

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

