# Balance-Analyse: Security-Planspiel

## Design-Grundsatz: Gleiches Unternehmen, verschiedene Budgets

**WICHTIG:** Alle Budget-Tiers repräsentieren das GLEICHE Unternehmen!
- Gleiche Angriffe, gleiche Severity
- Gleiche E-Targets (15/17/19)
- Gleicher KZ-Start (60)
- **Nur das Budget unterscheidet sich**

Die Teams konkurrieren unter verschiedenen Budget-Restriktionen, aber gegen identische Bedrohungen.

---

## Finale Parameter

### Budget-Tiers (gleiches Unternehmen)

| Parameter | Alle Tiers |
|-----------|------------|
| **KZ-Start** | 60 |
| **Severity-Mult** | 1.0 |
| **E-Targets** | 15/17/19 |

| Tier | Budget |
|------|--------|
| Low | 300k |
| Medium | 400k |
| High | 500k |

### Angriffs-Parameter

| Angriff | Base Severity | kz_unit | s_unit | e_threshold | e_divisor |
|---------|---------------|---------|--------|-------------|-----------|
| Ransomware | 8 | 2 | 20 | 15 | 1 |
| OT-Störung | 10 | 2 | 32 | 17 | 1 |
| Exfiltration | 7 | 2 | 20 | 19 | 1 |

### Wellen-Parameter

| Welle | Angriff | kz_bonus | kz_malus | CIA-Gewichte |
|-------|---------|----------|----------|--------------|
| 1 | Ransomware | +5 | -3 | C=0.4, I=0.4, A=0.2 |
| 2 | OT-Störung | +7 | -5 | C=0.2, I=0.2, A=0.6 |
| 3 | Exfiltration | +10 | -7 | C=0.5, I=0.3, A=0.2 |

---

## Simulationsergebnisse (27 Strategien getestet)

### Tier-Vergleich (beste Strategien)

| Tier | Beste Strategie | KZ | Schaden | ROS | Score |
|------|-----------------|---:|--------:|----:|------:|
| **Low** | Awareness Heavy | 73 | 106k | 0.76 | 71.4 |
| **Medium** | Ransomware Focus | 90 | 45k | 0.66 | 80.6 |
| **High** | Balanced High | 94 | 0k | 0.31 | 79.5 |

### Strategie-Übersicht nach Score

#### Top 10 Strategien (über alle Tiers)

| Rang | Strategie | Low Score | Medium Score | High Score |
|------|-----------|----------:|-------------:|-----------:|
| 1 | Ransomware Focus | - | 80.6 | 80.6 |
| 2 | Optimal Balanced | - | 80.6 | 80.6 |
| 3 | Balanced High | - | - | 79.5 |
| 4 | OT Festung | - | - | 79.4 |
| 5 | Defense Depth | - | 78.2 | 78.2 |
| 6 | Suboptimal Overkill | - | - | 76.4 |
| 7 | OT Protection | - | 75.4 | 75.4 |
| 8 | Supply Chain Heavy | - | - | 74.9 |
| 9 | Cloud Fokus High | - | - | 74.4 |
| 10 | Awareness Heavy | 71.4 | 71.4 | 71.4 |

#### Schlechte Strategien (Score < 50)

| Strategie | Problem | KZ | Score |
|-----------|---------|---:|------:|
| **Nur Backup** | Zu einseitig - keine E-Abdeckung | 0 | 29.3 |
| **Minimum Viable** | Zu wenig Investition | 31 | 38.1 |
| **Keine Detection** | Fehlende SIEM/EDR | 33 | 39.9 |
| **Suboptimal Cloud** | M9+M10 Trap - keine Bonus-Measures | 40 | 44.6 |

---

## Detaillierte Ergebnisse

### Low Tier (Budget: 300k) - 11 Strategien möglich

| Strategie | KZ | Status | Schaden | ROS | Score |
|-----------|---:|--------|--------:|----:|------:|
| Awareness Heavy | 73 | OK | 106k | 0.76 | 71.4 |
| OT Fokus Low | 66 | OK | 109k | 1.16 | 71.2 |
| Alles L1 breit | 64 | OK | 155k | 0.75 | 65.9 |
| Balanced L1 | 58 | OK | 224k | 0.67 | 61.5 |
| Nur L2 Core | 53 | OK | 259k | 0.48 | 56.6 |
| Smart Basis | 50 | OK | 309k | 0.60 | 56.0 |
| Ransomware Fokus L1 | 50 | OK | 330k | 0.40 | 54.0 |
| Suboptimal Cloud | 40 | KRIT | 404k | 0.06 | 44.6 |
| Keine Detection | 33 | KRIT | 442k | 0.01 | 39.9 |
| Minimum Viable | 31 | KRIT | 471k | -0.05 | 38.1 |
| Nur Backup | 0 | KRIT | 448k | 0.93 | 29.3 |

### Medium Tier (Budget: 400k) - 18 Strategien möglich

| Strategie | KZ | Status | Schaden | ROS | Score |
|-----------|---:|--------|--------:|----:|------:|
| Optimal Balanced | 92 | OK | 22k | 0.54 | 80.6 |
| Ransomware Focus | 90 | OK | 45k | 0.66 | 80.6 |
| Defense Depth | 88 | OK | 67k | 0.54 | 78.2 |
| OT Protection | 79 | OK | 0k | 0.80 | 75.4 |
| Exfil Defense | 79 | OK | 86k | 0.52 | 72.6 |
| Awareness Heavy | 73 | OK | 106k | 0.76 | 71.4 |
| Alles L1 High | 72 | OK | 58k | 0.81 | 71.3 |
| OT Fokus Low | 66 | OK | 109k | 1.16 | 71.2 |
| Suboptimal Mix | 72 | OK | 58k | 0.65 | 69.7 |
| Alles L1 breit | 64 | OK | 155k | 0.75 | 65.9 |
| Balanced L1 | 58 | OK | 224k | 0.67 | 61.5 |
| Nur L2 Core | 53 | OK | 259k | 0.48 | 56.6 |
| Smart Basis | 50 | OK | 309k | 0.60 | 56.0 |
| Ransomware Fokus L1 | 50 | OK | 330k | 0.40 | 54.0 |
| Suboptimal Cloud | 40 | KRIT | 404k | 0.06 | 44.6 |
| Keine Detection | 33 | KRIT | 442k | 0.01 | 39.9 |
| Minimum Viable | 31 | KRIT | 471k | -0.05 | 38.1 |
| Nur Backup | 0 | KRIT | 448k | 0.93 | 29.3 |

### High Tier (Budget: 500k) - 24 Strategien möglich

| Strategie | KZ | Status | Schaden | ROS | Score |
|-----------|---:|--------|--------:|----:|------:|
| Balanced High | 94 | OK | 0k | 0.31 | 79.5 |
| OT Festung | 94 | OK | 0k | 0.30 | 79.4 |
| Optimal Balanced | 92 | OK | 22k | 0.54 | 80.6 |
| Ransomware Focus | 90 | OK | 45k | 0.66 | 80.6 |
| Suboptimal Overkill | 89 | OK | 0k | 0.30 | 76.4 |
| Defense Depth | 88 | OK | 67k | 0.54 | 78.2 |
| Cloud Fokus High | 86 | OK | 0k | 0.28 | 74.4 |
| Supply Chain Heavy | 85 | OK | 0k | 0.39 | 74.9 |
| OT Protection | 79 | OK | 0k | 0.80 | 75.4 |
| Exfil Defense | 79 | OK | 86k | 0.52 | 72.6 |
| Nur Detection High | 73 | OK | 86k | 0.25 | 66.3 |
| Awareness Heavy | 73 | OK | 106k | 0.76 | 71.4 |
| Alles L1 High | 72 | OK | 58k | 0.81 | 71.3 |
| Suboptimal Mix | 72 | OK | 58k | 0.65 | 69.7 |
| OT Fokus Low | 66 | OK | 109k | 1.16 | 71.2 |
| Alles L1 breit | 64 | OK | 155k | 0.75 | 65.9 |
| Balanced L1 | 58 | OK | 224k | 0.67 | 61.5 |
| Nur L2 Core | 53 | OK | 259k | 0.48 | 56.6 |
| Smart Basis | 50 | OK | 309k | 0.60 | 56.0 |
| Ransomware Fokus L1 | 50 | OK | 330k | 0.40 | 54.0 |
| Suboptimal Cloud | 40 | KRIT | 404k | 0.06 | 44.6 |
| Keine Detection | 33 | KRIT | 442k | 0.01 | 39.9 |
| Minimum Viable | 31 | KRIT | 471k | -0.05 | 38.1 |
| Nur Backup | 0 | KRIT | 448k | 0.93 | 29.3 |

---

## Balance-Bewertung

### Positive Outcomes
- **77%** aller Strategien (41/53) erreichen KZ >= 50
- Low Tier: 7/11 Strategien positiv (64%)
- Medium Tier: 14/18 Strategien positiv (78%)
- High Tier: 20/24 Strategien positiv (83%)

### Suboptimale Strategien werden bestraft

| Trap-Strategie | Problem | Score-Differenz |
|----------------|---------|-----------------|
| **Nur Backup** | Zu einseitig | -42 vs. Best |
| **Suboptimal Cloud** | M9/M10 ohne Bonus-Measures | -27 vs. Best |
| **Keine Detection** | Fehlende SIEM/EDR | -31 vs. Best |
| **Alles L1 High** | Budget verschwendet (305k im 500k Tier) | -8 vs. Best |

### Budget-Progression

| Tier | Strategien | Best Score | Worst Score | Spread |
|------|------------|------------|-------------|--------|
| Low | 11 | 71.4 | 29.3 | 42.1 |
| Medium | 18 | 80.6 | 29.3 | 51.3 |
| High | 24 | 79.5 | 29.3 | 50.2 |

**Beobachtungen:**
- **More Budget = More Options**: High Tier hat 13 mehr Strategien als Low
- **Nicht zwingend bessere Scores**: Medium's Best (80.6) = High's Best (80.6)
- **Höherer ROS bei geringerem Budget**: Low erreicht ROS=1.16, High nur ROS=0.31

---

## Mitigation-Mechanik

### Formel
```
severity_reduction = (E_value - e_threshold) / e_divisor
final_severity = max(0, base_severity - severity_reduction - bonus_reduction)
```

### Beispiel: "OT Fokus Low" - Welle 2 (OT-Störung)
```
CIA: C=21, I=25, A=23
E_value = 0.2*21 + 0.2*25 + 0.6*23 = 4.2 + 5.0 + 13.8 = 23.0
e_threshold = 17, e_divisor = 1
severity_reduction = (23.0 - 17) / 1 = 6.0
bonus_reduction = 3 (M5 L2 + M7 L1)
final_severity = max(0, 10 - 6 - 3) = 1
KZ-Verlust = 1 * 2 = 2, Schaden = 1 * 29k = 29k
```

---

## Was risikobasiertes Arbeiten belohnt

### 1. Richtige Maßnahmen-Auswahl

| Angriff | Bonus-Maßnahmen | Max Bonus |
|---------|-----------------|-----------|
| Ransomware | M3+M4+M6 (L2) | +5 |
| OT-Störung | M5+M7 (L2) | +5 |
| Exfiltration | M1+M2+M8 (L2) | +5 |

### 2. Trap-Maßnahmen vermeiden

| Measure | Problem |
|---------|---------|
| **M9 (Cloud)** | Nur CIA-Bonus, keine Bonus-Measures |
| **M10 (MDM)** | Nur CIA-Bonus, keine Bonus-Measures |

"Suboptimal Cloud" (M9+M10 L2) erreicht nur KZ=40 vs. "Balanced L1" mit KZ=58!

### 3. Budget-Effizienz beachten

| Strategie | Budget | ROS | Interpretation |
|-----------|--------|-----|----------------|
| OT Fokus Low | 237k | 1.16 | Sehr effizient |
| Balanced High | 474k | 0.31 | Weniger effizient |

---

## Fazit

Die aktuelle Balance erfüllt die Anforderungen:

1. **Gleiches Unternehmen**: Alle Tiers haben identische Severity und E-Targets
2. **Positive Outcomes**: 77% der Strategien erreichen KZ >= 50
3. **Differenzierung**:
   - Low Tier ist herausfordernd (7/11 positiv)
   - High Tier hat Komfort (20/24 positiv)
4. **Suboptimale Strategien werden bestraft**:
   - M9/M10 Traps funktionieren
   - Einseitige Strategien (Nur Backup) scheitern
5. **Risikobasiertes Arbeiten wird belohnt**:
   - Richtige Maßnahmenwahl für Angriffe gibt Bonus-Reduktion
   - Budget-Effizienz (ROS) variiert stark

### Score-Verteilung

```
Score 80+:  ████ (4 Strategien - nur Medium/High)
Score 70+:  ████████████ (12 Strategien)
Score 60+:  ██████ (6 Strategien)
Score 50+:  ██████████████████████ (22 Strategien)
Score <50:  ████████ (8 Strategien - kritische Fehler)
```
