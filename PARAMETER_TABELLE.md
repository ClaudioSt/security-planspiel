# PARAMETER-TABELLE - MVP v2.0

**Alle Spielwerte auf einen Blick**
*Diese Tabelle in Excel/Google Sheets übertragen für einfache Anpassungen*

---

## 1. BUDGET-PARAMETER

| Parameter | Wert | Beschreibung |
|-----------|------|--------------|
| **Budget-Einheit** | 1.000€ | 1 Budgetpunkt = 1.000€ |
| **Budget-Schritte** | 50k | Feste Schritte zwischen Tiers |
| **Empfohlene Ranges** | 200-250 (low), 300-350 (medium), 400-450 (high) | |

### Budget-Trade-offs (BALANCIERT)

| Tier | Budget (k€) | KZ-Start | E-Ziel W1 | E-Ziel W2 | E-Ziel W3 | Balancing-Event |
|------|-------------|----------|-----------|-----------|-----------|-----------------|
| **Low** | 200-250 | 70 | 18 | 20 | 22 | -3 KZ (Compliance-Gap) |
| **Medium** | 300-350 | 60 | 18 | 20 | 22 | - |
| **High** | 400-450 | 50 | 18 | 20 | 22 | +8 KZ (Investor Confidence) |

**Balancierte Final-Index-Werte (mit weight_ros=0.25):**
| Tier | Max KZ (mit Events) | Max RoS | Erwarteter Max FI |
|------|---------------------|---------|-------------------|
| Low | 67 | ~95% | ~91 |
| Medium | 76 | ~72% | ~94 |
| High | 80 | ~54% | ~94 |

**Spread: < 5 Punkte** (Ziel erreicht!)

---

## 2. WELLEN-PARAMETER

| Welle | Angriff | wC | wI | wA | E-Ziel (alle Tiers) | KZ-Bonus (erreicht) | KZ-Malus (verfehlt) |
|-------|---------|----|----|----|--------------------|---------------------|---------------------|
| 1 | Ransomware | 0.4 | 0.4 | 0.2 | **18** | +3 | -5 |
| 2 | OT-Störung | 0.2 | 0.2 | 0.6 | **20** | +5 | -8 |
| 3 | Exfiltration | 0.5 | 0.3 | 0.2 | **22** | +8 | -10 |

*E-Ziele sind jetzt einheitlich - Balancing erfolgt über KZ-Start und Events*

---

## 3. MASSNAHMEN-PARAMETER

### M1: IAM/PAM

| Level | CIA (C/I/A) | Init | OPEX | Mitigation Ransomware | Mitigation OT | Mitigation Exfil | Abhängigkeiten |
|-------|-------------|------|------|----------------------|---------------|------------------|----------------|
| L1 | 2/1/0 | 30 | 4 | -1 | 0 | -1 | - |
| L2 | 4/3/0 | 60 | 10 | -2 | 0 | -2 | - |
| L3 | 6/5/1 | 100 | 20 | -3 | 0 | -3 (+1 Kontext) | M2 ≥ L2 |

**Kontext-Bonus L3 Exfil:** PAM verhindert Lateral Movement (+1)

---

### M2: Logging & SIEM/MDR

| Level | CIA (C/I/A) | Init | OPEX | Mitigation Ransomware | Mitigation OT | Mitigation Exfil | Abhängigkeiten |
|-------|-------------|------|------|----------------------|---------------|------------------|----------------|
| L1 | 1/3/0 | 20 | 2 | -1 | 0 | -1 | - |
| L2 | 2/5/1 | 50 | 8 | -2 | -1 | -2 | - |
| L3 | 3/7/2 | 80 | 24 | -3 | -2 | -3 (+1 Kontext) | - |

**Kontext-Bonus L3 Exfil:** MDR erkennt APT-Muster (+1)

---

### M3: EDR/XDR

| Level | CIA (C/I/A) | Init | OPEX | Mitigation Ransomware | Mitigation OT | Mitigation Exfil | Abhängigkeiten |
|-------|-------------|------|------|----------------------|---------------|------------------|----------------|
| L1 | 3/2/1 | 24 | 4 | -2 | 0 | -1 | - |
| L2 | 5/4/2 | 56 | 10 | -3 | 0 | -2 | - |
| L3 | 7/6/3 | 90 | 18 | -4 (+1 Kontext) | 0 | -3 | M2 ≥ L2 |

**Kontext-Bonus L3 Ransomware:** Behavioral Analysis stoppt Crypto-Trojaner (+1)

---

### M4: Backup & Disaster Recovery

| Level | CIA (C/I/A) | Init | OPEX | Mitigation Ransomware | Mitigation OT | Mitigation Exfil | Recovery-Faktor | Abhängigkeiten |
|-------|-------------|------|------|----------------------|---------------|------------------|-----------------|----------------|
| L1 | 0/4/3 | 16 | 6 | -1 | 0 | 0 | 10% | - |
| L2 | 1/6/5 | 40 | 12 | -2 | -1 | 0 | 30% | - |
| L3 | 1/8/7 | 80 | 20 | -4 (+1 Kontext) | -2 | 0 | 50% | - |

**Kontext-Bonus L3 Ransomware:** Immutable Backups verhindern Verschlüsselung (+1)
**Recovery-Faktor:** Reduziert Schaden NACH Angriff um angegebenen Prozentsatz

---

### M5: OT/IT-Netz-Segmentierung

| Level | CIA (C/I/A) | Init | OPEX | Mitigation Ransomware | Mitigation OT | Mitigation Exfil | Abhängigkeiten |
|-------|-------------|------|------|----------------------|---------------|------------------|----------------|
| L1 | 2/1/4 | 40 | 2 | 0 | -1 | 0 | - |
| L2 | 3/2/6 | 70 | 6 | -1 | -3 (+2 Kontext) | 0 | - |
| L3 | 4/3/8 | 110 | 12 | -2 | -5 (+2 Kontext) | 0 | - |

**Kontext-Bonus L2/L3 OT:** Kern-Maßnahme für OT-Schutz! (+2)

---

### M6: Security Awareness & Training

| Level | CIA (C/I/A) | Init | OPEX | Mitigation Ransomware | Mitigation OT | Mitigation Exfil | Abhängigkeiten |
|-------|-------------|------|------|----------------------|---------------|------------------|----------------|
| L1 | 2/1/1 | 10 | 2 | -1 | 0 | 0 | - |
| L2 | 3/2/2 | 24 | 6 | -3 (+1 Kontext) | 0 | 0 | - |
| L3 | 5/3/3 | 40 | 10 | -4 (+2 Kontext) | 0 | 0 | - |

**Kontext-Bonus L2:** Simuliertes Phishing reduziert Klickrate (+1)
**Kontext-Bonus L3:** Incident-Meldeprozess beschleunigt Reaktion (+2)

---

### M7: Vulnerability & Patch Management

| Level | CIA (C/I/A) | Init | OPEX | Mitigation Ransomware | Mitigation OT | Mitigation Exfil | Abhängigkeiten |
|-------|-------------|------|------|----------------------|---------------|------------------|----------------|
| L1 | 2/3/2 | 20 | 4 | -1 | -1 | 0 | - |
| L2 | 4/5/3 | 44 | 8 | -2 | -2 (+1 Kontext) | -1 | - |
| L3 | 6/7/4 | 76 | 14 | -3 | -3 (+1 Kontext) | -2 | M2 ≥ L1 |

**Kontext-Bonus L2/L3 OT:** OT-Patches reduzieren Angriffsfläche (+1)

---

### M8: Supplier Security & Supply Chain

| Level | CIA (C/I/A) | Init | OPEX | Mitigation Ransomware | Mitigation OT | Mitigation Exfil | Abhängigkeiten |
|-------|-------------|------|------|----------------------|---------------|------------------|----------------|
| L1 | 1/2/2 | 16 | 4 | 0 | 0 | 0 | - |
| L2 | 2/4/4 | 36 | 8 | 0 | -1 | -1 | - |
| L3 | 3/6/6 | 70 | 16 | 0 | -2 | -2 (+1 Kontext) | - |

**Kontext-Bonus L3 Exfil:** Lieferant war Einfallstor (+1)

---

### M9: Cloud Security (CSPM) ❌ SUBOPTIMAL

| Level | CIA (C/I/A) | Init | OPEX | Mitigation Ransomware | Mitigation OT | Mitigation Exfil | Abhängigkeiten |
|-------|-------------|------|------|----------------------|---------------|------------------|----------------|
| L1 | 2/2/1 | 18 | 3 | 0 | 0 | 0 | - |
| L2 | 3/3/2 | 40 | 7 | 0 | 0 | 0 | - |
| L3 | 4/4/3 | 70 | 14 | 0 | 0 | -1 | - |

**Warum suboptimal:** MechTech nutzt kaum Cloud (nur Backup-SaaS). Kaum Wirkung!

---

### M10: Mobile Device Management (MDM) ❌ SUBOPTIMAL

| Level | CIA (C/I/A) | Init | OPEX | Mitigation Ransomware | Mitigation OT | Mitigation Exfil | Abhängigkeiten |
|-------|-------------|------|------|----------------------|---------------|------------------|----------------|
| L1 | 1/1/0 | 12 | 2 | 0 | 0 | 0 | - |
| L2 | 2/2/1 | 28 | 5 | -1 | 0 | 0 | - |
| L3 | 3/3/2 | 50 | 10 | -1 | 0 | 0 | - |

**Warum suboptimal:** Kaum Mobilgeräte im OT/Produktion. Wenig Wirkung!

---

## 4. ANGRIFFS-PARAMETER

### Basis-Verluste (für RoS-Berechnung)
```
Base Losses = 8×20 + 10×32 + 7×20 = 160 + 320 + 140 = 620k€
```

### Welle 1: Ransomware (Office-IT)

| Parameter | Wert | Beschreibung |
|-----------|------|--------------|
| **baseSeverity** | 8 | Ausgangsschwere |
| **sUnit** | **20** | Schaden pro Schwerestufe G (in 1.000€) |
| **kzUnit** | **3** | KZ-Verlust pro Schwerestufe G |
| **CIA-Impact/Stufe** | C-2, I-2, A-1 | Pro Stufe G |
| **Mitigation-Cap** | 10 | Max. Mitigation (verhindert "Over-Mitigation") |

**Welche Maßnahmen wirken:**
- M1 (IAM): -1/-2/-3 (L1/L2/L3)
- M2 (SIEM): -1/-2/-3
- M3 (EDR): -2/-3/-5 (L3 mit Kontext-Bonus!)
- M4 (Backup): -1/-2/-5 (L3 mit Kontext-Bonus!)
- M6 (Awareness): -1/-4/-6 (L2/L3 mit Kontext-Bonus!)
- M7 (Patching): -1/-2/-3

---

### Welle 2: OT-Störung (Produktionsausfall)

| Parameter | Wert | Beschreibung |
|-----------|------|--------------|
| **baseSeverity** | 10 | Ausgangsschwere (hoch!) |
| **sUnit** | **32** | Schaden pro G (Produktion teuer!) |
| **kzUnit** | **3** | KZ-Verlust pro G |
| **CIA-Impact/Stufe** | C-1, I-2, A-3 | Pro Stufe G |
| **Mitigation-Cap** | 12 | Max. Mitigation |

**Welche Maßnahmen wirken:**
- M2 (SIEM): 0/-1/-2
- M5 (OT-Segmentierung): -1/-5/-7 (L2/L3 mit Kontext-Bonus!)
- M7 (Patching): -1/-3/-4 (L2/L3 mit Kontext-Bonus!)
- M8 (Supplier): 0/-1/-2
- M4 (Backup): 0/-1/-2 (hilft bei Recovery)

---

### Welle 3: Datenexfiltration (IP-Diebstahl)

| Parameter | Wert | Beschreibung |
|-----------|------|--------------|
| **baseSeverity** | 7 | Ausgangsschwere |
| **sUnit** | **20** | Schaden pro G (Wettbewerbsnachteil) |
| **kzUnit** | **3** | KZ-Verlust pro G |
| **CIA-Impact/Stufe** | C-3, I-1, A-0 | Pro Stufe G |
| **Mitigation-Cap** | 10 | Max. Mitigation |

**Welche Maßnahmen wirken:**
- M1 (IAM): -1/-2/-4 (L3 mit Kontext-Bonus!)
- M2 (SIEM): -1/-2/-4 (L3 mit Kontext-Bonus!)
- M3 (EDR): -1/-2/-3
- M7 (Patching): 0/-1/-2
- M8 (Supplier): 0/-1/-3 (L3 mit Kontext-Bonus!)

---

## 5. EVENT-PARAMETER

### Allgemeine Events (alle Tiers)

#### Event 1: OEM-Audit angekündigt

| Parameter | Wert |
|-----------|------|
| **Trigger** | Automatisch in Welle 2 |
| **Bedingung (Bonus)** | E-Wert Welle 1 >= E-Ziel |
| **Effekt (Bonus)** | KZ +5 |
| **Bedingung (Malus)** | E-Wert Welle 1 < E-Ziel |
| **Effekt (Malus)** | KZ -3 |

#### Event 2: Mitarbeiter-Fluktuation

| Parameter | Wert |
|-----------|------|
| **Trigger** | M6 (Awareness) < L2 am Ende Welle 1 |
| **Effekt** | OPEX +5, KZ -2 |
| **Narrative** | IT-Admins verlassen Firma (Überlastung) |

#### Event 3: DSGVO-Zertifizierung (Bonus)

| Parameter | Wert |
|-----------|------|
| **Trigger** | M1 >= L2 UND M2 >= L2 am Ende Welle 2 |
| **Effekt** | KZ +3, Budget +10 (Förderung) |
| **Narrative** | Compliance-Vorteil nutzen |

---

### BALANCING-EVENTS (Tier-spezifisch)

Diese Events gleichen die unterschiedlichen Final-Index-Werte zwischen den Budget-Tiers aus.

#### Event 4: Compliance-Gap (nur LOW-Tier)

| Parameter | Wert |
|-----------|------|
| **Trigger** | Nach Welle 2 (automatisch) |
| **Gilt für** | Nur Budget-Tier LOW (200-250k) |
| **Effekt** | KZ **-3** |
| **Narrative** | Begrenztes Budget führt zu Compliance-Lücken bei OEM-Audit |

#### Event 5: Investor Confidence (nur HIGH-Tier)

| Parameter | Wert |
|-----------|------|
| **Trigger** | Nach Welle 3 (automatisch) |
| **Gilt für** | Nur Budget-Tier HIGH (400-450k) |
| **Effekt** | KZ **+8** |
| **Narrative** | Hohe Sicherheitsinvestitionen stärken Investorenvertrauen und Marktposition |

**Balancing-Effekt:**
- Low: Max KZ 70 - 3 = 67 -> FI ~91
- Medium: Max KZ 76 -> FI ~94
- High: Max KZ 72 + 8 = 80 -> FI ~94
- **Spread: ~3 Punkte** (statt 39 ohne Events!)

---

## 6. FORMELN (zur Erinnerung)

### Mitigation-Summe
```
M_sum = min(MIT_CAP, Σ(Maßnahmen-Mitigations inkl. Kontext-Boni))
```

### Endschwere
```
G = max(0, baseSeverity - M_sum)
```

### Schaden
```
Damage = G × sUnit  (in 1.000€)
```

### KZ-Delta
```
ΔKZ = -(G × kzUnit)
KZ_neu = clamp(KZ_alt + ΔKZ, 0, 100)
```

### CIA-Mali
```
Temporär je Welle:
ΔC = -G × ciaImpactPerStep_C
ΔI = -G × ciaImpactPerStep_I
ΔA = -G × ciaImpactPerStep_A
```

### Recovery (nach Angriff)
```
Wenn M4 vorhanden:
Damage_final = Damage × (1 - Recovery_Faktor)
```

### E-Wert (Erfüllungsgrad)
```
E = Team_C × wC + Team_I × wI + Team_A × wA
```

### Return on Security (RoS)
```
Gesamtkosten = Σ(Init) + Σ(OPEX × Anzahl Wellen) + Σ(Event-Strafen)
Verluste = Σ(Damage über alle Wellen)
Basisverluste = Σ(baseSeverity × sUnit) = 620k€
Vermeidete Verluste = Basisverluste - Verluste
RoS = (Vermeidete Verluste - Gesamtkosten) / Gesamtkosten × 100%
```

### Final-Index (Gesamtbewertung)
```
Final-Index = KZ_final × weight_kz + RoS × weight_ros

Empfohlene Gewichte für Balancing:
  weight_kz = 1.0
  weight_ros = 0.25  (wichtig für Tier-Balance!)

Beispiel: KZ=72, RoS=54%
  FI = 72 × 1.0 + 54 × 0.25 = 72 + 13.5 = 85.5
```

**Hinweis:** Mit weight_ros = 0.25 wird der RoS-Vorteil niedriger Budgets ausgeglichen, sodass alle Tiers vergleichbare Final-Index-Werte erreichen können.

---

## 7. DISCOVERY-SIGNAL-SCORING (intern für Moderatoren)

| Frage-Thema | Antwort führt zu... | Signal-Kategorie | Punkte |
|-------------|---------------------|------------------|--------|
| Produktionsbetrieb 24/7? | Ja, 24/5 | **OT-Kritikalität** | +3 |
| Ausfallkosten pro Stunde? | >5.000€ | **OT-Kritikalität** | +2 |
| OEM-Anforderungen? | ISO 27001 gefordert | **Compliance-Druck** | +4 |
| Externe Audits? | Ja, in 3 Monaten | **Compliance-Druck** | +3 |
| Sensible Daten? | CAD, Know-how | **IP-Schutz** | +3 |
| Wettbewerber aktiv? | Ja, aggressiv | **IP-Schutz** | +2 |

**Scoring → Konsequenzen:**
- **OT-Kritikalität >7:** Welle 2 (OT) wird kritischer (wA höher, evtl. sUnit +2)
- **Compliance-Druck >7:** Event 1 (Audit) ist härter (Malus -5 statt -3)
- **IP-Schutz >7:** Welle 3 (Exfil) wird relevanter (wC höher)

---

## 8. QUICK-REFERENCE (für Moderatoren)

### Typische Team-Zusammenstellung (Beispiel mittel)

**Budget: 320k€ (320 Punkte)**

| Maßnahme | Level | Init | OPEX | CIA | Summe |
|----------|-------|------|------|-----|-------|
| M1 IAM | L2 | 60 | 10 | 4/3/0 | |
| M2 SIEM | L2 | 50 | 8 | 2/5/1 | |
| M3 EDR | L2 | 56 | 10 | 5/4/2 | |
| M4 Backup | L2 | 40 | 12 | 1/6/5 | |
| M5 OT-Seg | L1 | 40 | 2 | 2/1/4 | |
| M6 Awareness | L2 | 24 | 6 | 3/2/2 | |
| M7 Patching | L1 | 20 | 4 | 2/3/2 | |
| **TOTAL** | | **290** | **52/Welle** | **19/24/16** | |

**Budget nach Init:** 320 - 290 = 30 übrig
**OPEX 3 Wellen:** 52 × 3 = 156
**Ende:** 30 - 156 = -126 (Defizit!) → Team muss OPEX bedenken!

---

**Diese Tabelle ist die zentrale Referenz für alle Zahlen im Spiel!**
→ In Excel übertragen für einfache Anpassungen während Tests.
