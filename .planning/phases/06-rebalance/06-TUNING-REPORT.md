# Phase 6 Tuning Report: D-04 review of the tuned candidate (plan 06-09)

**Status:** the candidate is verified with the real tooling on both layers and waits for the D-04 decision.
**Not adopted:** `simulation_config.json`, `content/`, `tests/golden/`, `final_documents/` and `print/` are unchanged; plan 06-10 adopts the candidate only after approval.

**Candidate files (all under `.planning/phases/06-rebalance/`):**

| File | Content |
|---|---|
| `candidate_config.json` | tuned values, `reference_strategies` (new), re-chosen `reference_plans`, X = 3, k = 10 |
| `candidate_content/clues.toml` | clue to measure mapping (`measures`, `weight`) for all 21 clues (7 new clues) |
| `candidate_content/texte.toml` | two wording edits: Exzellenz-Bonus narrative, `sheets.spielleitung.final_index_note` |
| `candidate_content/digit_allowlist.toml`, `giveaway_terms.toml` | byte copies, unchanged |
| `candidate_config_soft.json` | not created: D-13a does not apply (X = 3 <= 5 without capping and without voiding bonuses) |

## Verdict

The consolidated report on the candidate (`uv run python balance_analysis.py --config .planning/phases/06-rebalance/candidate_config.json --content-dir .planning/phases/06-rebalance/candidate_content --layers all --paths --jobs 3 --baseline-config simulation_config.json --baseline-content-dir content`, 38 min) ends with `Gesamturteil: alle berechneten Prüfungen bestanden`. That run read `final_index.weight_ros` = 15; its Final-Index block then recommended k = 10 (raw 11.6), and the candidate was set to k = 10. The k-dependent checks (reference strategy placement, non-clue share, Final-Index share) were re-run for k = 10 (see "Final-Index"), and the full balance suite `pytest -m balance --runxfail` on the final file passes (23 passed, see "Command results").

| Check | low | medium | high |
|---|---|---|---|
| Overspend gate (static, swap layer, window 1, window 2) at X = 3 | pass | pass | pass |
| Calibration: configured X equals recommended X (max + 1 = 3) | pass (global) | | |
| Decisions BAL-06 (dominance, near-mandatory, overpowered, decision points) | pass | pass | pass |
| Tier-pair decisions BAL-06 (band Jaccard, different best plans) | pass (global) | | |
| Reference strategies BAL-07 (good top quartile, bad bottom quartile, mediocre between) | pass | pass | pass |
| Rewarding BAL-08 (median above start, comeback) | pass | pass | pass |
| Spread BAL-09 (best 90..98, corridor, IQR, width, median bound) | pass (global) | | |
| Final-Index BAL-03 (KZ share 0.60..0.73) | pass (global) | | |
| Hand-calc BAL-02 (`planspiel validate --strict`: 0 errors, 0 warnings) | pass (global) | | |
| Clue mapping D-18 (`check_clues(require_mapping=True)`) | pass (global) | | |

Four of the checks pass with little room; the D-04 list at the end marks them: low-tier best KZ is 90 on the static and 98 on the legal layer (the allowed window is 90..98, so it sits on both bounds), the low-tier legal IQR is 13 (bound 13), the window-move share is 0.53 (bound 0.50), and the largest band share is 0.86 in the high tier (bound 0.90).

## Baseline (committed configuration, 2026-11-01 re-run)

`uv run python balance_analysis.py --config simulation_config.json --content-dir content --layers all --paths --jobs 3` (22 min) reproduces the research baseline exactly: static X 9/5/3 (recommended X 10, above the target 5), best in budget 98/100/100 (legal layer 100/100/100), median 63/65/66 (legal 60/62/62), IQR 17, M7 near-mandatory in every tier (band share 1.00) and overpowered (drop 14/16/18), M2 near-mandatory in medium/high (drop 7/11), in the high tier also M1 0.96, M4 0.97 and M5 0.93 above the 0.9 bound; Final-Index KZ share 0.98 at k = 1 (recommended k 20); hand-calc error `attacks.exfil` 17/7; no clue mapping and no `reference_strategies`; 11 checks failed. Differences to the research text: none in the numbers; the extra near-mandatory measures in the high tier (M1, M4, M5) are new detail. The Final-Index based numbers of this standalone run are not used for any decision (committed k = 1 is the interim value of plan 06-03); every before/after comparison below comes from `--baseline-config`, which evaluates the baseline with the candidate's k.


## Config diff (old -> new, with rationale)

Every changed JSON path of `simulation_config.json` against `candidate_config.json` (from `balance.config_diff`; the committed config is the "old" column). Formulas are untouched; only operands, tier lists and the Exzellenz level changed. All attack slopes are one decimal now (ransomware 2.0, OT 1.4, exfil 2.0). Group rationales apply to the rows marked "(same)".


| JSON path | old | new | rationale |
|---|---|---|---|
| `attacks.exfil.kz_at_full_damage` | -7 | -6 | BAL-02: slope 17/7 becomes 14/7 = 2.0 (one decimal); range centred lower so the wave-3 swing stays balance-neutral |
| `attacks.exfil.kz_at_full_mitigation` | 10 | 8 | (same) |
| `attacks.ot.kz_at_full_damage` | -5 | -6 | Range 14 at cap 10 (slope 1.4) widens the in-budget spread (IQR >= 13/14) without raising the required X |
| `attacks.ot.kz_at_full_mitigation` | 7 | 8 | (same) |
| `attacks.ransomware.kz_at_full_damage` | -6 | -8 | Range 16 (slope 2.0) unchanged, window moved from -6..10 to -8..8: lowers the level of every tier (replaces a larger start-KZ cut), keeps best below 98 |
| `attacks.ransomware.kz_at_full_mitigation` | 10 | 8 | (same) |
| `budget_tiers.high.budget` | 450 | 405 | Budgets 370/390/405 (was 350/400/450): the gain over start KZ grows with budget, so a narrower spread keeps the median gain of the high tier under the 28 KZ bound; tiers still differ in plans (Jaccard of the bands <= 0.2) |
| `budget_tiers.high.kz_start` | 34 | 33 | Start KZ 39/36/33 (was 50/42/34): equalises the tier medians (59/60/60) so no tier is clearly better (D-07); low best on the legal layer lands at 98 |
| `budget_tiers.low.budget` | 350 | 370 | Budgets 370/390/405 (was 350/400/450): the gain over start KZ grows with budget, so a narrower spread keeps the median gain of the high tier under the 28 KZ bound; tiers still differ in plans (Jaccard of the bands <= 0.2) |
| `budget_tiers.low.kz_start` | 50 | 39 | Start KZ 39/36/33 (was 50/42/34): equalises the tier medians (59/60/60) so no tier is clearly better (D-07); low best on the legal layer lands at 98 |
| `budget_tiers.medium.budget` | 400 | 390 | Budgets 370/390/405 (was 350/400/450): the gain over start KZ grows with budget, so a narrower spread keeps the median gain of the high tier under the 28 KZ bound; tiers still differ in plans (Jaccard of the bands <= 0.2) |
| `budget_tiers.medium.kz_start` | 42 | 36 | Start KZ 39/36/33 (was 50/42/34): equalises the tier medians (59/60/60) so no tier is clearly better (D-07); low best on the legal layer lands at 98 |
| `events.wave_2[1].tiers[0][1]` | -15 | -2 | OEM-Audit stepped (-15..+15, jumps of 10) becomes linear 1 KZ per checked measure (D-01 allows linear tiers): no jackpot at 4 or 5 checked measures |
| `events.wave_2[1].tiers[1][1]` | -5 | -1 | (same) |
| `events.wave_2[1].tiers[3][1]` | 0 | 1 | (same) |
| `events.wave_2[1].tiers[4][1]` | 5 | 2 | (same) |
| `events.wave_2[1].tiers[5][1]` | 15 | 3 | (same) |
| `events.wave_2[2].tiers.0` | -5 | -3 | Kritische Schwachstelle {-5,0,3,7} becomes {-3,0,0,4}: the M7 event swing (12) is flattened to 7; M7 removal drop falls from 14-18 to at most 1-4 |
| `events.wave_2[2].tiers.2` | 3 | 0 | (same) |
| `events.wave_2[2].tiers.3` | 7 | 4 | (same) |
| `events.wave_3[0].kz_per_measure` | 5 | 3 | Exzellenz-Bonus 5 -> 3 per measure: step reward softened (Phase 2 D-18) |
| `events.wave_3[0].level` | 3 | 2 | Exzellenz-Bonus now from Level 2 (was Level 3): many equivalent mixes reach it, so the best plans differ (needs the narrative edit 'gehobenem Niveau') |
| `events.wave_3[1].kz_delta` | -10 | -6 | Nervige Authentifizierung -10 -> -6: M6 was forced into every plan with M1 (near-mandatory) |
| `final_events[0].overspend_penalty.kz_per_step` | 9 | 3 | X = max(required X over static + swap + window-1 + window-2) + 1 (D-13), strict, start-lowered trim |
| `final_events[0].tiers[1][1]` | 5 | 9 | Budget Review 0/5/10/15 -> 0/9/18/27 per 25 k EUR remaining: the strongest X lever (the trimmed version collects it); side effect: hoarding is rewarded more (hoard archetype still bottom quartile) |
| `final_events[0].tiers[2][1]` | 10 | 18 | (same) |
| `final_events[0].tiers[3][1]` | 15 | 27 | (same) |
| `final_index.weight_ros` | 1 | 10 | k = 10 (recommended: raw 11.6 from the pooled in-budget IQR, nearest multiple of 5): KZ share about 0.70 (target 0.60-0.73, D-15) |
| `measures.M6.levels.1.init` | 10 | 16 | M6 init +6 at every level: cheapest measure was in every near-optimal plan; dearer entry removes the pull |
| `measures.M6.levels.2.init` | 24 | 30 | (same) |
| `measures.M6.levels.3.init` | 40 | 46 | (same) |
| `measures.M7.levels.1.cia.a` | 2 | 0 | M7 CIA -2 per dimension (floored at 0): M7 L1/L2 were the best CIA-per-cost buys; now its value comes from the event and the bonus |
| `measures.M7.levels.1.cia.c` | 2 | 0 | (same) |
| `measures.M7.levels.1.cia.i` | 3 | 1 | (same) |
| `measures.M7.levels.2.cia.a` | 3 | 1 | (same) |
| `measures.M7.levels.2.cia.c` | 4 | 2 | (same) |
| `measures.M7.levels.2.cia.i` | 5 | 3 | (same) |
| `measures.M7.levels.3.cia.a` | 4 | 2 | (same) |
| `measures.M7.levels.3.cia.c` | 6 | 4 | (same) |
| `measures.M7.levels.3.cia.i` | 7 | 5 | (same) |
| `reference_plans` | (see below) | (see below) | Re-chosen answer-key paths near the legal median with a voluntary move (Phase 5 carry-over) |
| `reference_strategies` | (see below) | (see below) | New block (D-06, D-25): good derived from the clue scores, mediocre, bad (ignore, all-in, hoard) |
| `waves[0].bonus_measures[1].bonus` | 6 | 5 | M4 bonus 6 -> 5: bonus x slope = 10 KZ at stake, graduated against the clue evidence (backup) |
| `waves[0].bonus_measures[2].bonus` | 3 | 4 | M6 bonus 3 -> 4: with the dearer M6 (init +6) the cheap measure no longer dominates; stake 8 KZ |
| `waves[0].e_threshold` | 23 | 22 | Wave 1 and wave 3 threshold -1 (wave 2 unchanged): more plans reach mitigation, which spreads the near-optimal band over many measure mixes (no near-mandatory measure) |
| `waves[1].bonus_measures[1].bonus` | 6 | 3 | M7 bonus 6 -> 3: M7 was near-mandatory and overpowered (drop 14/16/18); stake 4.2 KZ |
| `waves[2].bonus_measures[0].bonus` | 8 | 4 | M1 bonus 8 -> 4: stake 8 KZ instead of 16, balances the wave-3 measures |
| `waves[2].bonus_measures[2].bonus` | 9 | 3 | M8 bonus 9 -> 3: M8 (cheap, balanced CIA) became near-mandatory at 4-5; stake 6 KZ |
| `waves[2].e_threshold` | 25 | 24 | Wave 1 and wave 3 threshold -1 (wave 2 unchanged): more plans reach mitigation, which spreads the near-optimal band over many measure mixes (no near-mandatory measure) |


Levers not touched: wave weights (`c/i/a`), `base_cia`, severity multipliers, `base_severity`, `s_unit`, `mitigation_cap`, the `recovery` values, all measure CIA values except M7, all costs except M6 init, `opex`, the events Kurswechsel, Operative Unterstützung, Sparprogramm, the Budget Review `step`, `practice`. The M5 bonus (9), M3 (6) and M2 (6) bonuses stayed at their committed values.

Design reading of the result (an interpretation of the measured data, for D-04): the near-mandatory M7 and M2 of the baseline most likely came from four coupled effects: the M7 event swing (Kritische Schwachstelle 12), the OEM-Audit jackpot steps, M7's cheap CIA per cost and its wave-2 bonus, and the M2 wave-3 bonus with the Exzellenz level 3 dependency chain. The candidate flattens the three event shapes (all still integer and linear), evens the bonus stakes to 6..12.6 KZ, lowers the thresholds of waves 1 and 3 so that many different measure mixes reach mitigation, and sets the Exzellenz-Bonus at Level 2. The tier trade-off (budget against start KZ) is kept: low 370 EUR / start 39, medium 390 / 36, high 405 / 33.

## Content diff

No story document was edited. The existing story already carries the evidence for every bonus measure; the missing support of the baseline (M6, M2, M3, M1) is closed by seven new clue entries that quote existing sentences verbatim (veil, giveaway, digit and verbatim checks pass: `planspiel texts` and `planspiel clues` report 0 errors, 0 warnings on the candidate content).

### Clue mapping (facilitator-only, `candidate_content/clues.toml`)

Weights: 3 = strong, 2 = clear, 1 = weak, 0 = atmospheric (no measure). Rows 15 to 21 are new. Rule checked by `check_clues(require_mapping=True)`: importance order implies score order, every bonus measure has >= 2 points, the most important has >= 4.


| Nr. | Attack | Source key | Quote (verbatim) | Measures | Weight | New |
|---|---|---|---|---|---|---|
| 1 | ransomware | `story.steckbrief.it_ot_landschaft.saas_cloud.bullets` | Cloud-Backup: Veeam für Office-Daten (monatliche Sicherung) | M4 | 2 |  |
| 2 | ransomware | `story.anfrage_mail.lage.paragraphs` | Wir haben einen Virenscanner und Backups, aber keine strukturierte Security-Strategie. | M3, M4 | 1 |  |
| 3 | ransomware | `story.zeitungsartikel.bericht_vorfall.ablauf.paragraphs` | Wir hatten kein funktionierendes Backup-Konzept | M4 | 2 |  |
| 4 | ransomware | `story.zeitungsartikel.bericht_vorfall.headline` | Erpresser legen Zulieferer tagelang lahm | - | 0 |  |
| 5 | ot | `story.steckbrief.it_ot_landschaft.ot_produktion.bullets` | Office-IT und OT/Produktion nutzen dasselbe LAN (kein separates OT-Netz) | M5 | 3 |  |
| 6 | ot | `story.steckbrief.betrieb_service.bullets` | Patch-/Update-Praxis in der Produktion: Umsetzung im Rahmen verfügbarer Wartungsfenster | M7 | 2 |  |
| 7 | ot | `story.zeitungsartikel.meldung_audit.paragraphs` | bis zur sauberen Trennung von Büro- und Fertigungsnetzen | M5 | 2 |  |
| 8 | ot | `story.zeitungsartikel.bericht_vorfall.folgen.paragraphs` | Drei Fertigungslinien standen still | - | 0 |  |
| 9 | ot | `story.audit_mail.nachweise.bullets` | OT-Segmentierung | M5 | 1 |  |
| 10 | exfil | `story.steckbrief.betrieb_service.bullets` | Remote-Zugänge durch fünf Lieferanten (u. a. MES, CAD, IT) | M8 | 1 |  |
| 11 | exfil | `story.steckbrief.it_ot_landschaft.saas_cloud.bullets` | Lieferanten-Portal: extern erreichbare Web-Applikation | M8 | 1 |  |
| 12 | exfil | `story.anfrage_mail.lage.paragraphs` | wissen wir auch nicht genau, wer aktuell überall administrativen Zugriff auf unsere Systeme hat | M1 | 2 |  |
| 13 | exfil | `story.zeitungsartikel.meldung_audit.paragraphs` | Supply Chain Security ist geschäftskritisch | M8 | 1 |  |
| 14 | exfil | `story.audit_mail.einleitung.paragraphs` | insb. Datenverlust, Supply-Chain-Angriffe | - | 0 |  |
| 15 | ransomware | `story.zeitungsartikel.bericht_vorfall.ablauf.paragraphs` | Einbruch über eine gefälschte E-Mail, die ein Mitarbeiter in der Buchhaltung öffnete | M6 | 2 | yes |
| 16 | ransomware | `story.zeitungsartikel.bericht_vorfall.ablauf.paragraphs` | Der klassische Virenschutz des Unternehmens schlug nicht rechtzeitig Alarm | M3 | 3 | yes |
| 17 | exfil | `story.zeitungsartikel.bericht_vorfall.ablauf.paragraphs` | Erst nach Stunden bemerkte die IT ungewöhnliche Aktivitäten im Netz | M2 | 3 | yes |
| 18 | exfil | `story.steckbrief.betrieb_service.bullets` | gemeinsam genutzte Admin-Konten für Server- und Netzwerkkomponenten | M1 | 2 | yes |
| 19 | ot | `story.zeitungsartikel.bericht_vorfall.ablauf.paragraphs` | Zentrale Systeme waren zudem seit Monaten nicht mehr aktualisiert worden | M7 | 1 | yes |
| 20 | ransomware | `story.zeitungsartikel.ticker` | Verdächtige E-Mail stoppt Fertigung | M6 | 1 | yes |
| 21 | exfil | `story.steckbrief.betrieb_service.bullets` | Sicherheitsbetrieb: SIEM/EDR nicht als feste Plattformkomponenten genannt | M2, M3 | 2 | yes |

| Measure | Importance (KZ at stake = bonus x slope) | Clue points |
|---|---|---|
| M5 | 12.6 | 6 |
| M2 | 12 | 5 |
| M3 | 12 | 6 |
| M4 | 10 | 5 |
| M1 | 8 | 4 |
| M6 | 8 | 3 |
| M8 | 6 | 3 |
| M7 | 4.2 | 3 |


Clue 14 ("insb. Datenverlust, Supply-Chain-Angriffe") is now atmospheric (weight 0) because M8 lost importance (bonus 3, stake 6 KZ) and the graduation rule needs M8 <= M6.

Reading notes (to confirm at D-04): (a) clue 9 quotes the OEM audit checklist bullet "OT-Segmentierung"; the audit mail and the steckbrief bullet "Sicherheitsbetrieb: SIEM/EDR nicht als feste Plattformkomponenten genannt" (clue 21) already name measure terms in the committed story, so D-17 "story texts never name measures" is already relaxed there; I mapped them with low weights (1, 2) and did not rewrite the story. (b) The `attack` column only decides which attack's "two clues from two documents" rule a clue serves; clue 17 (log review) and 18 (shared admin accounts) are filed under exfil, 19 under OT.

### Wording edits (before -> after, `candidate_content/texte.toml`)

| Key | Before | After | Why |
|---|---|---|---|
| `events.exzellenz_bonus.narrative` | ... Für jede auf **höchstem** Niveau betriebene Kontrolle gibt es einen Bonus auf eure Kundenzufriedenheit. | ... Für jede auf **gehobenem** Niveau betriebene Kontrolle gibt es einen Bonus auf eure Kundenzufriedenheit. | The bonus now starts at Level 2, so "höchstem Niveau" would be untrue. The card rows (level, KZ per measure) are generated from the config. |
| `sheets.spielleitung.final_index_note` | Der Final-Index ist ein Vergleichswert der Spielleitung und gilt vorläufig, bis die Gewichte nach der Neubalancierung feststehen. | Der Final-Index ist der Vergleichswert der Spielleitung für das Debriefing: KZ am Ende plus k mal RoS, der RoS vorher auf zwei Nachkommastellen gerundet. | Final wording without digits and without "vorläufig". The key `final_index_provisional` stays (the current code still requires it; 06-10 removes it together with the code). No key was added (`texts.orphan_key`). |



## Metrics before -> after per tier

Tool output of `--baseline-config` (German, quoted as is). Final-Index based rows (placement of the strategies, share of best plans with a non-clue measure) were computed in the run with k = 15 for both columns; they were re-checked for k = 10 (next section). The columns "vorher" use the committed config, so the strategy rows are empty there (the block does not exist).

```

Kennzahlen vorher → nachher
Final-Index-Kennzahlen beider Spalten mit k der Kandidatenkonfiguration
Kennzahl                                                                Tier          vorher     nachher
Nötiges X (strikt), statisches Gate                                     low                9           2
Nötiges X (strikt), Pfade tausch                                        low                9           2
Nötiges X (strikt), Pfade fenster1                                      low                9           1
Nötiges X (strikt), Pfade fenster2                                      low                5           1
Bestes End-KZ im Budget, statische Schicht                              low               98          90
Median der End-KZ im Budget, statische Schicht                          low               63          59
Bestes End-KZ im Budget, legale Tausch-Schicht                          low              100          98
Median der End-KZ im Budget, legale Tausch-Schicht                      low               60          56
Interquartilsabstand der End-KZ im Budget, statische Schicht            low               17          14
Interquartilsabstand der End-KZ im Budget, legale Tausch-Schicht        low               16          13
Größter Band-Anteil (Level >= 1)                                        low                1      ≈ 0,80
Maßnahme des größten Band-Anteils                                       low               M7          M6
Größter Wegfall-Abfall der besten End-KZ                                low               14           1
Maßnahme des größten Wegfall-Abfalls                                    low               M7          M2
Anteil bester Pläne mit Maßnahme ohne Hinweis                           low                1      ≈ 0,69
Nötiges X (strikt), statisches Gate                                     medium             5           2
Nötiges X (strikt), Pfade tausch                                        medium             5           1
Nötiges X (strikt), Pfade fenster1                                      medium             5           1
Nötiges X (strikt), Pfade fenster2                                      medium             2           1
Bestes End-KZ im Budget, statische Schicht                              medium           100          93
Median der End-KZ im Budget, statische Schicht                          medium            65          60
Bestes End-KZ im Budget, legale Tausch-Schicht                          medium           100          97
Median der End-KZ im Budget, legale Tausch-Schicht                      medium            62          58
Interquartilsabstand der End-KZ im Budget, statische Schicht            medium            17          14
Interquartilsabstand der End-KZ im Budget, legale Tausch-Schicht        medium            17          14
Größter Band-Anteil (Level >= 1)                                        medium             1      ≈ 0,84
Maßnahme des größten Band-Anteils                                       medium            M7          M2
Größter Wegfall-Abfall der besten End-KZ                                medium            16           4
Maßnahme des größten Wegfall-Abfalls                                    medium            M7          M2
Anteil bester Pläne mit Maßnahme ohne Hinweis                           medium             1      ≈ 0,73
Nötiges X (strikt), statisches Gate                                     high               3           2
Nötiges X (strikt), Pfade tausch                                        high               2           1
Nötiges X (strikt), Pfade fenster1                                      high               3           1
Nötiges X (strikt), Pfade fenster2                                      high               1           1
Bestes End-KZ im Budget, statische Schicht                              high             100          93
Median der End-KZ im Budget, statische Schicht                          high              66          60
Bestes End-KZ im Budget, legale Tausch-Schicht                          high             100          97
Median der End-KZ im Budget, legale Tausch-Schicht                      high              62          57
Interquartilsabstand der End-KZ im Budget, statische Schicht            high              17          14
Interquartilsabstand der End-KZ im Budget, legale Tausch-Schicht        high              17          14
Größter Band-Anteil (Level >= 1)                                        high               1        0,86
Maßnahme des größten Band-Anteils                                       high              M2          M2
Größter Wegfall-Abfall der besten End-KZ                                high              18           4
Maßnahme des größten Wegfall-Abfalls                                    high              M7          M2
Anteil bester Pläne mit Maßnahme ohne Hinweis                           high               1      ≈ 0,74
KZ-Anteil bei dem verwendeten k                                         -             ≈ 0,74      ≈ 0,61
Empfohlenes k (aus den Daten)                                           -                 20          10
Konfiguriertes k der Konfigurationsdatei (nur zur Information)          -                  1          15
Empfohlenes X (Maximum + 1)                                             -                 10           3

```

Other numbers from the same run (candidate; low / medium / high):

| Metric | low | medium | high |
|---|---|---|---|
| Start KZ | 39 | 36 | 33 |
| In-budget plans (static, of 782,336) | 84,702 | 106,747 | 125,332 |
| Best in budget static / legal layer | 90 / 98 | 93 / 97 | 93 / 97 |
| Median in budget static / legal layer | 59 / 56 | 60 / 58 | 60 / 57 |
| Median minus start KZ static / legal (needs >= 5, <= 28) | +20 / +17 | +24 / +22 | +27 / +24 |
| IQR static / legal (13..21) | 14 / 13 | 14 / 14 | 14 / 14 |
| p5..p95 width static / legal (<= 50) | 30 / 31 | 32 / 32 | 33 / 34 |
| Band size (plans) | 200 | 200 | 200 |
| Largest band share (Level >= 1) | 0.80 (M6) | 0.84 (M2) | 0.86 (M2) |
| Largest removal drop (best KZ) | 1 (M2, M6, M8) | 4 (M2) | 4 (M2) |
| Smallest improvement share of a level | 0.04 (M1 L3) | 0.06 (M1 L3) | 0.08 (M1 L3) |
| Smallest swing share (>= 3 KZ) | 0.77 (M3) | 0.78 (M4) | 0.79 (M4) |
| Kurswechsel: starts with spread >= 3 KZ | 0.98 | 0.98 | 0.98 |
| Window move after wave 2: paths with gain >= 3 KZ | 0.53 | 0.54 | 0.56 |
| Comeback: starts reaching start KZ + 10 | 0.96 | 0.99 | 1.00 |
| Comeback: starts ending above start KZ | 0.99 | 1.00 | 1.00 |
| Band Jaccard (low-medium / low-high / medium-high) | 0.09 / 0.13 / 0.08 | | |
| Best over budget vs best in budget (static) | 77 vs 90 | 77 vs 93 | 75 vs 93 |


## Overspend gate

Definition used (D-13, research Q2, **to confirm at D-04**): an over-budget path loses if its KZ after the penalty is strictly below the best final KZ of every start plan with levels only lowered or cancelled, followed by any legal continuation ("start-lowered" trim). The raw reading (penalty without floor) and the capped reading (KZ clamped to 0..100 after the penalty) are both computed; unlosable (trimmed version ends at 0) and untrimmable counts are 0 in every cell. Raw and capped minima are identical in every cell, because the clamp only matters at KZ 0 and no trimmed version ends there. **Research A1 (raw vs capped KZ) is flagged for confirmation**: the implementation reads BAL-01 "raw and capped KZ" as the pair "unfloored penalty" and "KZ clamped after the penalty, unlosable plans as diagnostic".

Required X (strict; raw = capped everywhere), `planspiel gate --paths`:

| Family | paths per tier | low | medium | high |
|---|---|---|---|---|
| static reference (pinned gate) | 782,336 plans | 2 | 2 | 2 |
| tausch (swap layer, start-lowered) | 37,348,851 | 2 | 1 | 1 |
| fenster1 (window-1 move, union pool) | 22,274,048 | 1 | 1 | 1 |
| fenster2 (window-2 move, union pool) | 22,274,048 | 1 | 1 | 1 |
| tausch_eng (narrow: same swap pair, diagnostic, not in the verdict) | 37,300,736 swap paths | 3 | 3 | 2 |
| baseline static / tausch / fenster1 / fenster2 | | 9/9/9/5 | 5/5/5/2 | 3/2/3/1 |

Binding cell: tier low, static family, plan `0100113322` (remaining budget -70 k EUR = 7 started steps, KZ before review 77, final KZ 56 at X = 3 (77 - 3 x 7); its trimmed version `0100112220` keeps 79 k EUR and ends at KZ 70, so X = 2 is the smallest value that makes the overspender strictly worse). **Recommended X = max + 1 = 3** (D-13); configured X = 3 is "kalibriert"; the target X <= 5 (D-12) is met, so no soft alternative is needed (D-13a not applicable). The weak reading (a tie counts as not losing) needs 2 / 2 / 1 in the static family. Narrow trim: the narrow family needs 3 / 3 / 2 and passes at the configured X = 3 with zero margin (max + 1 would be 4). Because the narrow diagnostic is the more conservative reading, the choice between the two trim definitions is the one decision that moves X (see D-04 list).

Over budget never pays by a wide margin: the best over-budget plan ends at KZ 77 / 77 / 75 against the best in-budget plan 90 / 93 / 93 (static layer, low / medium / high; at X = 3).

## Final-Index

`final_index = weight_kz * KZ + weight_ros * RoS2`, `weight_kz` = 1, `weight_ros` = k an integer, RoS2 = RoS rounded to two decimals (06-03, D-15). Measured on the in-budget plans with own cost > 0 (IQR): KZ low/medium/high/pooled 14/14/14/14, RoS 0.67/0.60/0.54/0.60.

| k | KZ share low / medium / high / pooled |
|---|---|
| 10 (**chosen**, recommended by the tool: raw 11.6, nearest multiple of 5) | 0.68 / 0.70 / 0.72 / 0.70 |
| 15 (run of the full report) | 0.58 / 0.61 / 0.63 / 0.61 |

Target KZ share 2/3 within 0.60..0.73 (D-15). k = 10 is closer to 2/3 and has margin to both bounds; k = 15 passed too but only just (0.61). The committed config reads k = 1 under the 06-03 formula until adoption, and `tests/golden/answer_keys.json` is re-pinned once in 06-10. At the chosen k the reference strategies still place correctly (table below), the share of the best 1 % of plans (by Final-Index) containing a measure without clue points (M9 or M10) is 0.69 / 0.73 / 0.75 (needs >= 0.20), i.e. most of the best plans include M9 or M10, so "just buy the bonus measures" is not automatically the best plan (D-19).

## Planned labels (proposal for 06-10, which adds them with code)

- `sheets.spielleitung.final_index_weight` = "Gewicht k des RoS im Final-Index"
- `sheets.spielleitung.clue_head_measures` = "Maßnahmen (Gewicht)"

The candidate content contains neither key (adding them would be `texts.orphan_key` before the code reads them).

## Thresholds for approval (module constants; none changed)

| Constant (module) | Value | Candidate measured | Margin / remark |
|---|---|---|---|
| `BAND_KZ` / `BAND_MIN_SIZE` (choices) | 5 KZ / 200 plans | band within 5 KZ is smaller than 200 in every tier, so the 200-plan widening decides | the widening, not the 5 KZ, defines the band; see D-04 item |
| `NEAR_MANDATORY_SHARE` | 0.90 | largest share 0.80 / 0.84 / 0.86 | 0.04 to the bound (high) |
| `OVERPOWERED_DROP` | 10 KZ | largest drop 1 / 4 / 4 | 6 |
| strictly dominated | share must be > 0 | smallest 0.04 (M1 L3, low) | positive, but small: M1 L3 rarely beats M1 L2 |
| `DECISION_SHIFT_KZ` / `DECISION_SHARE` | 3 KZ / 0.5 | swing >= 0.77, Kurswechsel 0.98, window move 0.53 | window move is the thinnest (0.03) |
| `TIER_JACCARD_MAX` | 0.5 | 0.09 / 0.13 / 0.08 | wide |
| `MEDIAN_MARGIN` (rewarding) | 5 KZ | +17 legal (low), +20 static | wide |
| `COMEBACK_DROP` / `COMEBACK_GAIN` / `COMEBACK_SHARE` | 5 / 10 / 0.9 | 0.96 / 0.99 / 1.00 | low tier 0.06 above the bound |
| `CORRIDOR_WIDTH` | 6 | best static 90..93 (3), legal 97..98 (1); median static 59..60, legal 56..58 (2) | wide |
| `BEST_MIN` / `BEST_MAX` | 90 / 98 | low 90 static / 98 legal; medium 93 / 97; high 93 / 97 | low tier sits on both bounds (static-to-legal gap of the low tier is 8 KZ) |
| `IQR_MIN` / `IQR_MAX` | 13 / 21 | 14 static; legal 13 / 14 / 14 | low legal on the lower bound |
| `IQR_TIER_DIFF` | 4 | 0 static, 1 legal | wide |
| `P5_P95_MAX` | 50 | 30..34 | wide |
| `MEDIAN_START_MAX` | 28 | +20 / +24 / +27 static | high +27, 1 below the bound |
| quartiles (strategies) | 3/4 and 1/4 | good >= 0.93 below in both populations; bad >= 0.90 above; mediocre >= 0.31 on each side | mediocre 0.31 vs 0.25 |
| `NON_CLUE_SHARE_MIN` | 0.2 | 0.69 / 0.73 / 0.75 | wide |
| `CLUE_SCORE_MIN` / `CLUE_SCORE_TOP` | 2 / 4 | smallest 3, top 6 | wide |
| `TARGET_KZ_SHARE`, `KZ_SHARE_MIN/MAX`, `K_STEP` (index_weights) | 2/3, 0.60, 0.73, 5 | 0.70 at k = 10 | 0.03 to the upper bound |
| `X_TARGET` (gate) | 5 | X = 3 | 2 |

Two proposals if the user wants more room at the low tier: (a) widen `BEST_MAX` to 99 or `BEST_MIN` to 89 (then start KZ low could be 40 and the static best 91 / legal 99), or (b) accept the current exact fit. I did not change any threshold in code.


## Reference strategies (BAL-07, D-06, D-19, D-23, D-25)

Definitions (all legal in-budget paths with the forced Kurswechsel swap in window 1, stored in `reference_strategies`):

- **good**: start = `strategies.clue_good_start` (clue points in descending order, importance and config order as tie-break, Level 2 while it fits, then the balanced-CIA fill); the swap drops a wave-1-only bonus measure (M3, M4 or M6, whose bonus is spent after wave 1) for the best later-wave bonus measure (M1, M2, M5, M7 or M8) that fits the budget. The check asserts that the stored start equals what the algorithm returns from the current clues, so a clue edit that changes the good plan breaks visibly.
- **mediocre**: a plan within one KZ of the in-budget median with a swap near the median of the legal swaps (chosen by search so that all four placement shares are >= 0.25).
- **bad_ignore** ("ignores the clues"): M9 L3 only, swap to M10 L3 (the two measures without clue points; the story says cloud use and mobile devices are marginal).
- **bad_all_in** ("all-in on one CIA dimension, ignoring the bonus measures of the other waves"): Integrity-heavy M2 L2 + M4 L2, swap M4 -> M9 L1. A Confidentiality all-in (M1, M3, M6, M7) lands in the top quartile in every tier because those are bonus measures of waves 1 and 3, so the archetype must not be built from them (Pitfall 7, research Q8); the archetype definition is the research one (all-in on Integrity); only its concrete levels changed once: M2 L3 + M4 L3 with swap M4 -> M9 L3 missed the 0.75 bound by 0.01 in the medium tier of an intermediate candidate, so the levels were lowered to L2 + L2 with swap M4 -> M9 L1 for all tiers (written reason, Pitfall 7).
- **bad_hoard** ("keeps most of the budget"): M6 L1 only, swap M6 -> M10 L1. The larger Budget Review tiers reward hoarding (+27 at 75 k EUR remaining instead of +15), yet the hoard ends 41 / 38 / 35: below 4 % / 2 % / 1 % of the legal in-budget games.
- The **overspender** is not a strategy entry (D-23); the overspend gate judges it.

Placement (shares of the static in-budget Final-Index population / of the legal in-budget swap-layer KZ population strictly below and strictly above; good needs >= 0.75 below in both, bad >= 0.75 above in both, mediocre >= 0.25 on each side; evaluated at the final k = 10 on the stores of the F1 enumeration, whose start KZ low was 40 instead of 39, which only moves the low KZ cells by at most one rank; the pytest run in "Command results" repeats it on the exact file):


| Tier | Strategy | Kind | Start | Kurswechsel swap -> window selection | End KZ | Final-Index (k = 10) | FI below/above | KZ below/above (legal) |
|---|---|---|---|---|---|---|---|---|
| low | good | good | M2 L2, M3 L2, M4 L2, M5 L2, M6 L1 | M4 -> M7: M2 L2, M3 L2, M5 L2, M6 L1, M7 L1 | 76 | 82.9 | 0.98 / 0.02 | 0.97 / 0.02 |
| low | mediocre | mediocre | M2 L1, M3 L2, M4 L1, M5 L1, M6 L2, M7 L1, M8 L1, M10 L2 | M7 -> M1: M1 L1, M2 L1, M3 L2, M4 L1, M5 L1, M6 L2, M8 L1, M10 L2 | 56 | 57.3 | 0.42 / 0.58 | 0.42 / 0.54 |
| low | bad_ignore | bad | M9 L3 | M9 -> M10: M10 L3 | 44 | 34.0 | 0.01 / 0.98 | 0.07 / 0.92 |
| low | bad_all_in | bad | M2 L2, M4 L2 | M4 -> M9: M2 L2, M9 L1 | 45 | 38.6 | 0.05 / 0.95 | 0.08 / 0.90 |
| low | bad_hoard | bad | M6 L1 | M6 -> M10: M10 L1 | 41 | 31.0 | 0.01 / 0.99 | 0.04 / 0.96 |
| medium | good | good | M1 L1, M2 L2, M3 L2, M4 L2, M5 L2 | M3 -> M7: M1 L1, M2 L2, M4 L2, M5 L2, M7 L1 | 73 | 78.2 | 0.93 / 0.07 | 0.94 / 0.05 |
| medium | mediocre | mediocre | M1 L1, M2 L1, M3 L2, M5 L2, M9 L3 | M3 -> M6: M1 L1, M2 L1, M5 L2, M6 L3, M9 L3 | 62 | 65.4 | 0.64 / 0.36 | 0.65 / 0.31 |
| medium | bad_ignore | bad | M9 L3 | M9 -> M10: M10 L3 | 41 | 31.0 | 0.01 / 0.99 | 0.04 / 0.95 |
| medium | bad_all_in | bad | M2 L2, M4 L2 | M4 -> M9: M2 L2, M9 L1 | 42 | 35.6 | 0.04 / 0.96 | 0.05 / 0.94 |
| medium | bad_hoard | bad | M6 L1 | M6 -> M10: M10 L1 | 38 | 28.0 | 0.00 / 1.00 | 0.02 / 0.98 |
| high | good | good | M1 L1, M2 L2, M3 L2, M4 L2, M5 L2, M6 L1 | M4 -> M7: M1 L1, M2 L2, M3 L2, M5 L2, M6 L1, M7 L1 | 73 | 78.7 | 0.93 / 0.06 | 0.93 / 0.05 |
| high | mediocre | mediocre | M1 L1, M2 L1, M3 L1, M5 L2, M6 L2, M7 L2, M9 L1, M10 L2 | M10 -> M4: M1 L1, M2 L1, M3 L1, M4 L1, M5 L2, M6 L2, M7 L2, M9 L1 | 60 | 63.9 | 0.58 / 0.42 | 0.58 / 0.39 |
| high | bad_ignore | bad | M9 L3 | M9 -> M10: M10 L3 | 38 | 28.0 | 0.00 / 0.99 | 0.02 / 0.97 |
| high | bad_all_in | bad | M2 L2, M4 L2 | M4 -> M9: M2 L2, M9 L1 | 39 | 32.6 | 0.03 / 0.97 | 0.03 / 0.96 |
| high | bad_hoard | bad | M6 L1 | M6 -> M10: M10 L1 | 35 | 25.0 | 0.00 / 1.00 | 0.01 / 0.99 |

### Reference paths (answer keys)

| Tier | Start | Kurswechsel swap | Voluntary move (window 2) | End KZ | legal median |
|---|---|---|---|---|---|
| low | M4 L1, M6 L2, M7 L1, M8 L1, M9 L3, M10 L2 | M8 -> M5 | M6 L2 -> L0 | 56 | 56 |
| medium | M4 L1, M6 L3, M7 L1, M8 L1, M9 L2, M10 L3 | M4 -> M5 | M5 L1 -> L0 | 58 | 58 |
| high | M4 L1, M5 L2, M7 L1, M8 L1, M9 L2, M10 L3 | M4 -> M6 | M3 L0 -> L1 | 57 | 57 |


The three answer-key paths of `reference_plans` were re-chosen with `planspiel referenzpfade --tier <t> --median 56|58|57` (candidate 1 of each, 7 of 7 mechanics points, legal, in budget, one voluntary move in window 2, final KZ equal to the legal in-budget median of its tier). The measure costs changed, so the committed paths no longer sat near the median (medium 53, high 51 in an intermediate candidate). `master.build_master_sheet` builds on the candidate without a `PrintModelError`.

## Practice changes (Welle 0)

None. `practice.check_example(load_config(candidate))` passes on the candidate with the committed `practice` block (selection and values unchanged). 06-10 still re-pins `welle0.json` and `worksheet_tex.json` because they read the real measure costs.

## Print consequences

- **`MAX_PENALTY_ROWS`:** `len(review_text.penalty_rows(3, 10))` = 34 rows (X = 3), 25 rows at X = 4, 20 rows at X = 5; the constant is 12 today. Plan 06-10 must raise `booklet.MAX_PENALTY_ROWS` to 34 (or to the final value) and re-prove the RoS page layout (`tests/test_booklet_pdf.py` fill report, `teamheft_ros.tex.j2` already splits the table in two columns at `penalty_split`). `MAX_WINDOWS` stays 2 (no wave added).
- **Approximations that disappear:** every attack slope is one decimal (2.0, 1.4, 2.0), so the `≈` hints and the fraction branch of `format_factor` for slopes become dead code; E values and Gesamtreduktion have at most one decimal; RoS stays rounded by rule (RoS2).
- **Generated text:** OEM-Audit rows print one row per checked measure (linear), the Kritische-Schwachstelle table prints {-3, 0, 0, 4}, Exzellenz prints "ab Level 2". The Budget Review table prints 0 / 9 / 18 / 27 per 25 k EUR remaining and the penalty table 3 KZ per started 10 k EUR.
- **Goldens to re-pin after approval (06-10):** `characterization_*`, `digest_*`, `gate_*` (+ new `gate_paths_*`), `answer_keys.json` (reference paths, Final-Index text), `welle0.json`, `worksheet_tex.json`; then `planspiel print` and `print --check`.

## D-13a options

Not applicable: the recommended X is 3 (<= 5) after softening, with no cap and no voided bonuses. No `candidate_config_soft.json` was created. For information, the lever that made this possible is the larger Budget Review (0/9/18/27); the soft route (flat Exzellenz, linear OEM, flat M7 tiers) is already used. The price of the low X is the 34-row penalty table above; if you prefer a smaller table, X = 4 (25 rows) or X = 5 (20 rows) still passes the gate (X >= required) but is no longer "calibrated" in the sense of D-13 (max + 1).

## Open items and deviations from research

- Research proposed the hand-built candidate "review 9/18/27, start 38/28/18" and the search seed 25. Neither was used as is. The final candidate keeps the review tiers at 9/18/27, but the hand-built candidate failed the structural checks the research did not search for, and seed 25 uses an all-zero OEM-Audit event (rejected: a zero-valued event card is not truthful). The search objective of the research (static) was extended by the legal-layer bounds, the band widening, the clue graduation and the strategy placement.
- Research expected the M7 problem to need "structural work, not value nudges". It did: flat event tiers (Kritische Schwachstelle, OEM-Audit), M7 CIA -2 and bonus 3, but also the Exzellenz level and wave thresholds; no new measure, attack, wave or event type (D-01).
- The window-move share (0.53) and the low-tier legal best (98) and IQR (13) are the thinnest margins of the candidate.
- M7 Level 1 now has CIA (0, 1, 0): its value is the event (Kritische Schwachstelle -3 -> 0) and nothing else; M7 L1 is "event insurance", not a control with effect. Please confirm that this reads as intended.
- The cost lever tried by the search (M2, M4, M9, M10 init) was removed again as noise; only M6 init +6 and M7 CIA remain.
- The `HandCalcWarning` of the committed config still fires on every load of `simulation_config.json` (pre-existing, removed by adoption).
- No package was installed; the research vector engine was not adopted (all measurement ran through `planspiel` and a scratch driver that only calls `enumerate_tier`, `gate.gate_from_columns` and `choices.*`).


## Decisions to confirm at D-04 (options and recommendation)

1. **Trim definition of the move-path gate.** (a) start-lowered (shown above, X = 3) or (b) narrow "same swap pair" (diagnostic row: 3 / 3 / 2, which would force X = 4 (max 3 + 1, 25 penalty rows)). Recommendation (a): the debrief sentence is "had the team started with fewer or lower measures it would have stayed in budget and ended better"; (b) would move X by 1 (and one more safety step; the narrow family passes at X = 3 with zero margin) for no debrief benefit.
2. **Reading of "raw and capped KZ" (research A1).** Implemented as the pair "unfloored penalty" and "KZ clamped to 0..100 after the penalty, unlosable plans reported"; both coincide in every cell. Recommendation: accept.
3. **Global X.** X = 3 (D-13, calibrated) or a larger X (4 -> 25 penalty rows, 5 -> 20 rows; gate still passes, not "calibrated"). Recommendation: X = 3 and a 34-row table in 06-10.
4. **Thresholds** (table above, no code change): approve as proposed, or change. Items that deserve a look: (i) `BAND_MIN_SIZE` 200 decides the band in every tier (the 5 KZ band alone is smaller); (ii) `BEST_MIN/MAX` 90..98 puts the low tier on both bounds, (iii) `IQR_MIN` 13 equals the low-tier legal IQR, (iv) window-move share 0.5 vs 0.53, (v) `MEDIAN_START_MAX` 28 vs +27 (high), (vi) comeback share 0.9 vs 0.96. Recommendation: approve all as proposed; if you want slack, widen `BEST_MAX` to 99 rather than touching the others.
5. **Structural value changes** (Config diff): M7 CIA -2 per dimension with bonus 3 and flatter Kritische Schwachstelle; OEM-Audit linear; Exzellenz-Bonus from Level 2 with 3 KZ; Nervige Authentifizierung -6; Budget Review 0/9/18/27; budgets 370/390/405 and start KZ 39/36/33; wave thresholds -1 in waves 1 and 3. Options: approve, or name a lever to revert (I then re-tune). Recommendation: approve. Two things to look at: M7 L1 has CIA (0, 1, 0) (event insurance only), and 405 EUR for the high budget is a search value, not a round number (400 made medium and high identical in plans).
6. **Final-Index.** `KZ + k * RoS2` with k = 10 (KZ share 0.70) or k = 15 (0.61, passes too) or k = 5 (outside the 0.60..0.73 band). Recommendation: k = 10.
7. **Clue mapping** (21 clues, weights 1..3, floors 2 and 4, graduation by bonus x slope). Options: approve; or drop clue 21 ("SIEM/EDR ...", names two measure terms), which lowers M2 to 3 and M3 to 4 points and breaks the graduation (M2 and M3 outrank M4, which has 5), so other clue weights would have to be re-cut. Recommendation: approve. D-20: no story rewrite was needed.
8. **Reference strategies** (good derived from clues, mediocre, bad: ignore, all-in on Integrity, hoard; both-population rule from 06-07). Recommendation: approve. The Confidentiality all-in is intentionally not a bad archetype (it is a top-quartile plan).
9. **Reference paths** (answer keys) near the legal median with one voluntary move; practice unchanged. Recommendation: approve.
10. **Wording edits** (Exzellenz narrative, Final-Index note) and **planned labels** (`final_index_weight`, `clue_head_measures`). Recommendation: approve.
11. **Plan 06-08 interface choices:** the static layer leaves the choices block "not computed" and unreadable input exits with code 2. Recommendation: approve.
12. **Consequence for 06-10:** `MAX_PENALTY_ROWS` rises from 12 to 34 (with X = 3) and the RoS page layout is re-proven; `hand_calc` default flips to error; `require_mapping` is switched on; `final_index_provisional` and the "vorläufig" strings are removed with the code.
13. **D-13a:** not triggered (X = 3). Nothing to decide.

Answer format for the checkpoint: "approved", "approved with" followed by the numbers and changes above, or a list of changes.


## Command results

All commands ran on the committed candidate files (`candidate_config.json` with k = 10 and X = 3, `candidate_content/`); logs are in the gitignored `build/tuning/final3/`.

| Command | Result | Wall time |
|---|---|---|
| `uv run planspiel validate --strict --config <cand>` | `0 Fehler, 0 Warnung(en)` (exit 0) | seconds |
| `uv run planspiel texts --config <cand> --content-dir <cand_content>` | `0 Fehler, 0 Warnung(en)` | seconds |
| `uv run planspiel clues --config <cand> --content-dir <cand_content>` | `0 Fehler, 0 Warnung(en)`; with `require_mapping=True` `check_clues` returns no issue | seconds |
| `uv run planspiel gate --config <cand> --paths --jobs 3` | exit 0, `Konfiguration X = 3: kalibriert`, `Ziel X <= 5: erreicht`, `grep -c "nicht kalibriert"` = 0 | 10 min |
| `uv run planspiel gate --config <cand> --paths --narrow --jobs 3` | exit 0 (narrow family 3 / 3 / 2, passes at X = 3) | 19 min |
| `uv run planspiel tausch --config <cand> --summary-dir build/tuning/final3/tausch` | exit 0; best legal in-budget result 98 / 97 / 97 | 11 min |
| `uv run python balance_analysis.py --config <cand> ... --layers all --paths --jobs 3 --baseline-config simulation_config.json --baseline-content-dir content` | `Gesamturteil: alle berechneten Prüfungen bestanden` (run with k = 15, see Verdict) | 36 min |
| `uv run pytest tests -m balance --runxfail --planspiel-config <cand> --planspiel-content-dir <cand_content> -q` (final file, k = 10) | **23 passed**, 2832 deselected (every Phase-6 check as a hard check) | 18 min |
| `uv run pytest -q` (fast suite, committed config) | 2678 passed, 176 deselected, 1 xfailed | 2 min 42 s |
| `practice.check_example(load_config(<cand>))`, `master.build_master_sheet(...)` | no exception | seconds |
| `git diff --exit-code -- simulation_config.json content tests/golden final_documents print` | exit 0 | |

Note on the command in the plan: `pytest -m balance --runxfail --planspiel-config ...` without a path fails with "unrecognized arguments" because the options are registered by `tests/conftest.py`; add `tests` (done above).


## Change log

Baseline row first; every candidate that was evaluated appears once (hand-guided batches and the search iterations). All values are the static layer unless stated. Scratch outputs are under the gitignored `build/tuning/` (reports `baseline/`, `iter-t1/`, `final/`, `final2/`, `final3/`).


Hand-guided structural batches (static layer, three tiers low/medium/high; "band" = largest share of Level >= 1 in the near-optimal band, "drop" = largest removal drop of the tier best):

| Run | Change against the previous row | X | best KZ | median | IQR | band | drop |
|---|---|---|---|---|---|---|---|
| baseline | committed configuration | 9/5/3 | 98/100/100 | 63/65/66 | 17/17/17 | 1.00/1.00/1.00 | 14/16/18 |
| A | review 9/18/27 per 25 k EUR, exfil -5..9 (slope 2.0), start KZ 46/38/30 | 3/1/1 | 100/100/100 | 65/67/68 | 14/16/17 | 1.00/1.00/1.00 | 9/9/11 |
| B | A + Kritische Schwachstelle {-2,0,1,3}, OEM-Audit linear 1 per measure, M7 bonus 3, M7 CIA -1, M7 init +10 | 2/2/1 | 94/96/98 | 63/64/64 | 12/12/13 | 0.97/0.99/0.94 | 5/6/7 |
| C0 | B + evened bonuses (M3 5, M4 5, M6 4, M5 8, M7 5, M1 5, M2 5, M8 5), start KZ 46/40/36 | 3/2/1 | 89/97/100 | 61/65/70 | 11/12/13 | 0.99/0.96/0.96 | 6/8/2 |
| C1 | C0, budgets -10 | 3/2/1 | 88/96/100 | 59/63/68 | 10/12/14 | 0.98/0.97/0.97 | 5/6/4 |
| C3 | C0, ransomware range 20 | 5/2/1 | 91/99/100 | 61/66/71 | 12/13/15 | 0.99/0.97/0.95 | 6/8/1 |
| C5 | C0, every e_threshold -2 | 2/1/1 | 98/100/100 | 68/71/74 | 11/12/14 | 0.96/0.97/0.91 | 7/1/0 |
| R1 | Exzellenz-Bonus from Level 2 (was Level 3), 2 KZ per measure, M9 init -6 | 2/1/1 | 100/100/100 | 66/67/73 | 13/14/14 | 1.00/1.00/0.93 | 8/6/0 |
| R2 | R1, review 7/14/21 | 6/5/1 | 98/98/97 | 63/64/70 | 13/14/13 | 1.00/1.00/0.98 | 12/10/3 |
| R4 | R1, M8 bonus 6 | 2/1/1 | 97/99/100 | 65/67/73 | 12/13/15 | 0.89/0.99/0.92 | 6/5/0 |
| R5 | R1, Exzellenz 3 KZ, M8 bonus 5 | 2/2/1 | 100/100/100 | 67/69/76 | 12/14/15 | 0.90/0.97/0.85 | 6/2/0 |
| R7 | R5, M8 bonus 4, budgets 375/400/425, start KZ 42/38/34 | 2/2/1 | 99/100/100 | 68/69/69 | 13/14/14 | 0.89/0.95/0.91 | 3/3/3 |
| R8 | R7, review 8/16/24, budgets 380/400/420 | 3/3/1 | 99/98/100 | 67/67/67 | 14/14/14 | 0.93/0.95/0.94 | 5/4/7 |
| T2a | state of search s4-19 (below) with M2 and M3 bonus 5, high budget 410 | 3/2/1 | 90/92/91 | 61/63/62 | 12/13/13 | 0.92/0.92/0.94 | 5/4/3 |
| T2c | T2a with M2 and M3 bonus 6 (clue graduation) | 3/2/1 | 90/92/91 | 62/63/62 | 13/13/13 | 0.84/0.84/0.84 | 3/1/2 |
| P2 | T2c without the noise levers (M2/M4/M9/M10 init back to the committed value) | 2/2/2 | 90/92/91 | 60/62/61 | 13/13/13 | 0.80/0.84/0.83 | 3/3/3 |
| P3 | P2 without the M6 init +6 (rejected: M6 near-mandatory again) | 3/2/1 | 92/93/91 | 61/63/62 | 13/13/13 | 0.89/0.90/0.89 | 4/3/3 |
| P4 | P2 with the committed OT range (rejected: median and best fall, X rises) | 3/2/2 | 89/90/89 | 59/61/59 | 13/13/13 | 0.81/0.86/0.82 | 4/3/3 |
| P5 | P2 with the committed ransomware range (rejected: best 92/94/93 on the static layer, legal layer above 98 expected) | 2/2/2 | 92/94/93 | 62/64/63 | 13/13/13 | 0.80/0.84/0.83 | 3/3/3 |
| V3 | P2, review 9/18/27, OT range 14 | 2/2/1 | 93/96/95 | 62/64/63 | 13/14/14 | not read | not read |
| W2 | V3, Exzellenz 3 KZ, start KZ 40/36/33 | 2/2/2 | 95/98/97 | 63/65/64 | 14/14/14 | 0.81/0.84/0.81 | 3/2/3 |
| Y1 | search s5-15 (below) | 2/2/1 | 91/95/94 | 60/62/61 | 14/14/14 | 0.80/0.85/0.91 | 1/4/4 |
| Y4 | Y1, high budget 400 (rejected: same budget as medium, identical bands) | 2/2/2 | 91/95/92 | 60/62/59 | 14/14/14 | 0.80/0.85/0.85 | 1/4/4 |
| Z2 | Y1, budgets 370/390/405 | 2/2/2 | 91/93/93 | 60/60/60 | 14/14/14 | 0.80/0.83/0.86 | 1/4/4 |
| final | Z2 with start KZ low 39 (legal-layer best of low was 99, above the allowed 98) | 2/2/2 | 90/93/93 | 59/60/60 | 14/14/14 | 0.80/0.84/0.86 | 1/4/4 |

Notes on the batches: R3 and R6 are omitted (no new information). T2b (M5 bonus 7 instead of 9) gave bit-identical metrics to T2a, so the M5 bonus of wave 2 is capped away and is kept at its committed value.

Local search (simulated annealing over 40 levers, objective = weighted sum of violated static thresholds; runs s1 to s5, rows below): the objective was tightened between runs (s1-s4: best 92..96, median margin <= 25, IQR >= 13; s5: best 91..95, margin <= 27, IQR >= 14, band <= 0.88); random neighbours change one to three levers; "accepted" follows the Metropolis rule. Rejected neighbours are listed as well, so the table has one line per evaluated candidate.



Search iterations (state before = last accepted state of the same run; lever names as in the scratch driver: `review_a` Budget Review step per 25 k EUR, `ks_*` Kritische Schwachstelle tiers, `oem_s` OEM-Audit slope, `exz_*` Exzellenz level and KZ, `nervig` Nervige Authentifizierung, `ran_/ot_/exf_fd` and `_rng` attack KZ window start and width, `thr1..3` e_threshold change, `b_Mx` bonus, `ini_Mx` init change of a measure, `m7_cia`/`m7_init`, `bud_*`, `start_*`):


| Iteration | Levers old → new | X (low/medium/high) | best KZ | median | largest band share | largest removal drop | objective | accepted |
|---|---|---|---|---|---|---|---|---|
| s1-00 | start_high 36→35 | 2/2/1 | 94/96/100 | 63/64/69 | 0.99 | 6 | 40.21 | yes |
| s1-01 | b_M5 9→10 | 2/2/1 | 94/96/100 | 63/64/69 | 0.99 | 6 | 40.21 | yes |
| s1-02 | bud_medium 400→410, m7_cia 1→0 | 2/1/1 | 96/100/100 | 64/67/71 | 0.98 | 7 | 46.11 | yes |
| s1-03 | m2_cia_i 0→1, review_a 9→10 | 2/1/1 | 99/100/100 | 65/68/72 | 0.98 | 7 | 45.19 | yes |
| s1-04 | ot_fd -5→-3 | 2/1/1 | 100/100/100 | 67/70/74 | 0.98 | 6 | 45.32 | no |
| s1-05 | review_sp 25→30 | 3/1/1 | 98/100/100 | 63/67/70 | 1.00 | 9 | 49.55 | no |
| s1-06 | review_sp 25→30 | 3/1/1 | 98/100/100 | 63/67/70 | 1.00 | 9 | 49.55 | no |
| s1-07 | b_M5 10→11, nervig -10→-8 | 2/1/1 | 99/100/100 | 65/68/72 | 0.98 | 7 | 45.89 | yes |
| s1-08 | b_M4 6→5 | 2/1/1 | 99/100/100 | 65/68/72 | 0.98 | 9 | 47.54 | no |
| s1-09 | b_M8 9→11, bud_medium 410→400 | 2/1/1 | 99/100/100 | 65/67/72 | 1.00 | 7 | 46.3 | yes |
| s1-10 | bud_high 450→470, thr1 0→2 | 2/1/1 | 98/99/100 | 63/65/73 | 0.99 | 9 | 49.32 | no |
| s2-00 | bud_low 350→340 | 3/1/1 | 89/98/100 | 62/68/72 | 0.96 | 6 | 58.25 | no |
| s2-01 | b_M7 5→4 | 3/1/1 | 89/97/100 | 63/67/72 | 0.96 | 4 | 56.05 | yes |
| s2-02 | b_M3 5→3 | 3/2/1 | 89/97/100 | 63/67/71 | 0.96 | 4 | 55.49 | yes |
| s2-03 | m2_cia_i 0→2, m7_init 10→30 | 3/2/1 | 88/94/100 | 60/64/68 | 0.98 | 6 | 56.7 | no |
| s2-04 | ini_M1 0→3, ot_fd -5→-7, thr3 -1→0 | 2/2/1 | 87/93/100 | 60/64/68 | 0.97 | 6 | 57.7 | no |
| s2-05 | ini_M2 0→-3, m7_cia 1→2 | 3/2/1 | 90/95/100 | 62/66/70 | 0.97 | 5 | 49.53 | yes |
| s2-06 | ks_l3 3→4, nervig -10→-6 | 3/2/1 | 90/96/100 | 62/66/70 | 0.97 | 5 | 51.56 | yes |
| s2-07 | ks_l0 -2→-3 | 3/2/1 | 89/96/100 | 61/65/70 | 0.96 | 5 | 54.91 | no |
| s2-08 | b_M1 5→6, m2_init 0→20, oem_s 1→2 | 5/2/1 | 88/94/100 | 60/64/69 | 0.99 | 7 | 67.7 | no |
| s2-09 | ini_M10 0→-3, thr3 -1→0 | 3/2/1 | 89/94/100 | 61/65/70 | 0.98 | 6 | 53.4 | yes |
| s2-10 | b_M8 4→11, ini_M2 -3→3 | 2/3/1 | 96/99/100 | 62/66/70 | 1.00 | 9 | 48.34 | yes |
| s2-11 | ini_M5 0→3, ot_fd -5→-4, ran_fd -6→-5 | 2/2/1 | 98/100/100 | 64/67/72 | 1.00 | 9 | 54.25 | no |
| s3-00 | ini_M10 -3→0 | 2/3/1 | 96/99/100 | 62/65/70 | 1.00 | 9 | 48.67 | yes |
| s3-01 | b_M3 3→5, bud_medium 400→390, ini_M9 0→-6 | 2/2/1 | 96/98/100 | 63/64/70 | 1.00 | 8 | 45.03 | yes |
| s3-02 | exz_level 3→2, ot_rng 12→13 | 3/3/1 | 100/100/100 | 73/75/83 | 0.95 | 0 | 53.63 | no |
| s3-03 | b_M3 5→6, ini_M2 3→6 | 3/2/1 | 96/98/100 | 63/64/70 | 1.00 | 11 | 49.56 | no |
| s3-04 |  | 2/2/1 | 96/98/100 | 63/64/70 | 1.00 | 8 | 45.03 | yes |
| s3-05 | ini_M6 0→3 | 3/2/1 | 96/97/100 | 62/64/70 | 1.00 | 10 | 48.87 | no |
| s3-06 | m7_init 10→20 | 2/2/1 | 96/97/100 | 62/63/70 | 1.00 | 10 | 47.67 | yes |
| s4-00 | review_a 8→6 | 8/7/5 | 93/92/94 | 64/64/64 | 0.97 | 7 | 77.5 | no |
| s4-01 | m7_cia 2→0 | 2/1/1 | 100/100/100 | 71/71/70 | 0.98 | 4 | 77.32 | no |
| s4-02 | exz_kz 3→2, ini_M6 0→3 | 3/3/1 | 92/94/94 | 64/64/63 | 0.96 | 6 | 22.0 | yes |
| s4-03 | exf_fd -5→-6, start_low 42→41 | 3/3/1 | 90/93/93 | 62/63/62 | 0.96 | 6 | 22.0 | yes |
| s4-04 | thr3 0→2 | 3/2/2 | 88/90/92 | 60/61/60 | 0.99 | 7 | 34.0 | no |
| s4-05 | thr3 0→-1 | 3/2/1 | 91/93/93 | 63/64/64 | 0.93 | 4 | 19.0 | yes |
| s4-06 | b_M2 5→7, ot_fd -5→-4 | 3/2/1 | 95/95/94 | 65/65/65 | 0.86 | 3 | 12.0 | yes |
| s4-07 | b_M7 4→3, thr1 -1→-2 | 2/1/1 | 96/95/93 | 66/66/66 | 0.83 | 4 | 17.5 | no |
| s4-08 | ini_M4 0→-3 | 3/2/1 | 95/95/95 | 65/66/65 | 0.92 | 4 | 19.82 | yes |
| s4-09 | ini_M5 0→6, oem_s 1→2 | 3/3/1 | 96/96/96 | 65/66/66 | 0.97 | 7 | 38.5 | no |
| s4-10 | b_M6 3→4, bud_low 380→370 | 3/1/1 | 95/95/95 | 64/66/66 | 0.87 | 6 | 15.0 | yes |
| s4-13 | b_M3 5→7, ini_M6 3→6 | 3/2/1 | 92/95/94 | 63/66/65 | 0.80 | 2 | 16.0 | yes |
| s4-14 | exz_level 2→3 | 3/2/1 | 86/89/89 | 60/62/61 | 0.88 | 3 | 33.65 | no |
| s4-15 | b_M4 5→6, start_low 41→40 | 3/2/1 | 91/96/95 | 63/66/66 | 0.84 | 3 | 18.5 | no |
| s4-16 | ini_M1 0→-3, m7_init 10→0 | 2/1/1 | 92/97/96 | 65/67/67 | 0.86 | 3 | 21.5 | no |
| s4-17 | start_low 41→42 | 3/2/1 | 93/95/94 | 64/66/65 | 0.80 | 2 | 16.0 | yes |
| s4-18 | b_M1 5→4, ran_fd -6→-8, start_high 34→35 | 3/2/1 | 91/93/93 | 62/64/64 | 0.79 | 2 | 11.5 | yes |
| s4-19 | ks_l2 1→0 | 3/2/1 | 91/93/92 | 62/64/64 | 0.82 | 2 | 9.0 | yes |
| s4-20 | start_medium 38→40 | 3/2/1 | 91/95/92 | 62/66/64 | 0.82 | 2 | 9.0 | yes |
| s4-21 | start_medium 40→39, thr2 -1→-2 | 3/2/1 | 91/94/94 | 63/65/65 | 0.87 | 4 | 10.5 | no |
| s4-22 | ran_fd -8→-9, thr3 -1→0 | 2/2/2 | 89/94/91 | 60/63/62 | 0.91 | 4 | 14.1 | no |
| s4-23 | b_M7 4→5, m7_init 10→0 | 3/1/1 | 91/97/95 | 63/67/65 | 0.88 | 3 | 20.0 | no |
| s4-24 | ks_l2 0→1 | 3/2/1 | 91/95/93 | 62/66/64 | 0.79 | 2 | 11.5 | no |
| s4-25 | ot_rng 13→14, start_high 35→36 | 3/2/1 | 92/96/94 | 63/66/66 | 0.80 | 2 | 9.0 | yes |
| s4-26 | b_M5 8→7 | 3/2/1 | 92/96/94 | 62/66/66 | 0.80 | 2 | 9.0 | yes |
| s4-28 | nervig -6→-8 | 3/2/1 | 92/96/94 | 62/66/66 | 0.80 | 2 | 9.0 | yes |
| s5-00 | b_M4 5→7, ini_M8 0→-6, ot_fd -4→-3 | 2/2/1 | 100/100/100 | 65/67/66 | 0.91 | 5 | 40.0 | no |
| s5-01 | ks_l3 4→3 | 2/2/1 | 95/98/97 | 63/65/64 | 0.84 | 3 | 19.0 | yes |
| s5-02 | ini_M2 0→-6, ran_rng 16→20 | 3/2/2 | 100/100/100 | 66/69/68 | 0.86 | 2 | 43.52 | no |
| s5-03 | ks_l3 3→4 | 2/2/2 | 95/98/97 | 63/65/64 | 0.84 | 3 | 16.5 | yes |
| s5-04 | m7_init 10→0, thr2 -1→0 | 2/2/1 | 95/98/97 | 63/65/64 | 0.82 | 3 | 16.5 | yes |
| s5-05 | b_M7 4→3 | 2/2/1 | 95/98/97 | 63/65/64 | 0.82 | 3 | 19.0 | yes |
| s5-08 | ks_l0 -2→-3 | 2/2/1 | 94/97/96 | 62/65/64 | 0.82 | 2 | 16.0 | yes |
| s5-09 | b_M8 4→3 | 2/2/1 | 93/97/96 | 62/64/63 | 0.89 | 4 | 14.0 | yes |
| s5-10 | b_M5 8→9 | 2/2/1 | 93/97/96 | 62/64/63 | 0.91 | 4 | 13.0 | yes |
| s5-12 | b_M1 4→3 | 2/2/1 | 93/97/96 | 62/64/63 | 0.91 | 4 | 15.5 | no |
| s5-13 | b_M2 6→4, nervig -6→-8 | 3/2/1 | 92/95/96 | 61/64/63 | 0.94 | 6 | 18.5 | no |
| s5-14 | b_M4 5→6, m7_cia 2→1 | 2/1/1 | 98/98/98 | 64/66/65 | 0.86 | 6 | 25.5 | no |
| s5-15 | ot_fd -4→-6 | 2/2/1 | 91/95/94 | 60/62/61 | 0.91 | 4 | 4.0 | yes |
| s5-16 | b_M2 6→4, ini_M4 0→3 | 3/2/1 | 90/93/93 | 59/61/60 | 0.93 | 5 | 9.0 | no |
| s5-17 | ks_l2 0→2, thr1 -1→0, thr2 0→1 | 3/2/1 | 91/94/93 | 58/61/60 | 0.83 | 3 | 2.5 | yes |
| s5-18 | start_medium 36→35 | 3/2/1 | 91/93/93 | 58/60/60 | 0.83 | 3 | 2.5 | yes |
| s5-19 | b_M3 6→7, b_M4 5→6 | 3/2/1 | 92/94/94 | 59/60/60 | 0.84 | 4 | 2.5 | yes |
| s5-20 | b_M2 6→4, ini_M10 0→6 | 3/2/1 | 92/92/94 | 57/58/59 | 0.89 | 6 | 3.0 | no |
| s5-21 | b_M6 4→2, start_high 33→31 | 3/2/1 | 90/94/92 | 58/59/57 | 0.81 | 4 | 4.0 | yes |
| s5-22 | start_low 40→42 | 3/2/1 | 92/94/92 | 60/59/57 | 0.81 | 4 | 2.5 | yes |
| s5-23 | m7_cia 2→1, ot_fd -6→-7, thr1 0→-2 | 2/1/1 | 99/96/94 | 63/62/60 | 0.87 | 7 | 12.5 | no |
| s5-24 | b_M4 6→5, ks_l3 4→2 | 3/2/1 | 92/94/91 | 59/59/57 | 0.81 | 4 | 2.5 | yes |
| s5-25 | bud_low 370→360, ini_M7 0→3, ks_l0 -3→-2 | 3/2/2 | 89/95/91 | 57/59/57 | 0.82 | 4 | 12.0 | no |
| s5-26 | b_M4 5→4, exz_kz 3→5 | 3/3/2 | 100/100/98 | 64/64/62 | 0.75 | 3 | 28.5 | no |
| s5-27 | b_M1 4→3, start_high 31→33 | 2/2/2 | 92/94/93 | 59/58/58 | 0.81 | 4 | 2.5 | yes |
| s5-28 | b_M3 7→5, nervig -6→-8, start_high 33→35 | 2/2/2 | 92/93/95 | 59/58/60 | 0.85 | 3 | 2.5 | yes |
| s5-29 | b_M4 5→4, m7_cia 2→0 | 2/1/1 | 96/97/99 | 62/62/64 | 0.99 | 6 | 45.0 | no |

## D-04 decision

**Date:** 2026-11-01
**Answer (verbatim):** "Freigeben"

Read as approval of all 13 points with the recommendations given:

1. Trim definition: start-lowered (narrow stays a diagnostic).
2. Raw/capped KZ reading (A1): accepted as the pair implemented.
3. Global X = 3 (calibrated, D-13); 06-10 raises `MAX_PENALTY_ROWS` to 34 and re-proves the RoS page.
4. Thresholds: unchanged, no module constant is edited in 06-10.
5. Structural value changes: as listed in "Config diff" (M7 CIA -2 and bonus 3, flatter Kritische Schwachstelle, linear OEM-Audit, Exzellenz from Level 2 with 3 KZ, Nervige Authentifizierung -6, Budget Review 0/9/18/27, budgets 370/390/405, start KZ 39/36/33, thresholds -1 in waves 1 and 3, M6 init +6).
6. Final-Index: `KZ + k * RoS2` with k = 10.
7. Clue mapping: 21 clues including clue 21.
8. Reference strategies and archetype definitions.
9. Reference paths; practice unchanged.
10. Wording edits (Exzellenz narrative, Final-Index note) and planned labels `final_index_weight`, `clue_head_measures`.
11. Plan 06-08 interface choices.
12. Consequences for 06-10 noted (penalty rows 34, `hand_calc` default to error, `require_mapping` on, "vorläufig" removed, goldens re-pinned).
13. D-13a not triggered.

Candidate files are final; 06-10 adopts `candidate_config.json` and `candidate_content/` mechanically.
