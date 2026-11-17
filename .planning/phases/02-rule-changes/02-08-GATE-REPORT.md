# 02-08 Gate Report: overspend trim-back gate (RULE-04)

Basis: Referenzplan ohne Change-Fenster-Züge (D-24, D-25), 782,336 dependency-valid plans per tier. Config X = 9 per started 10 kEUR (provisional, D-25). Metric: End-KZ including the positive Budget-Review tier of the trimmed plan. A plan "loses" when its End-KZ is strictly lower than its best trimmed version (only levels lowered or measures cancelled, in budget).

Pinned results: `tests/golden/gate_low.json`, `gate_medium.json`, `gate_high.json` (created with `--update-golden`, not yet committed).

## Measured vs research (M1)

| Kennzahl | low gemessen | low Research | medium gemessen | medium Research | high gemessen | high Research |
|----------|--------------|--------------|-----------------|-----------------|---------------|---------------|
| over_budget | 712,882 | 712,882 | 658,015 | 658,015 | 584,583 | 584,583 |
| min_x_strict | 9 | 9 | 5 | 5 | 3 | 3 |
| min_x_weak | 8 | 8 | 4 | 4 | 3 | 3 |
| x_histogram | {1: 679,007, 2: 31,617, 3: 1,724, 4: 299, 5: 146, 6: 64, 7: 20, 8: 2, 9: 3} | identical | {1: 651,931, 2: 5,778, 3: 258, 4: 37, 5: 11} | identical | {1: 584,030, 2: 529, 3: 24} | identical |
| unlosable | 0 | 0 | 0 | 0 | 0 | 0 |
| untrimmable | 0 | not stated (implicitly 0) | 0 | not stated | 0 | not stated |
| violations_at_config_x (X = 9) | 0 | n/a | 0 | n/a | 0 | n/a |
| passed | true | pass expected | true | pass expected | true | pass expected |
| margin at X = 9: worst (trimmed End-KZ minus End-KZ of the over-budget plan) | 1 KZ | n/a | 5 KZ | n/a | 7 KZ | n/a |

Every numeric value equals the research expectation. No difference to explain away.

## Witness plans (largest strict X, ties: lowest code index)

| Tier | Plan p | remaining | steps | KZ before review | End-KZ at X = 9 | required X | Trimmed version t | t remaining | t End-KZ |
|------|--------|-----------|-------|------------------|-----------------|------------|-------------------|-------------|----------|
| low | `1121103000` | -10 | 1 | 91 | 82 | 9 | `0121103000` | +30 | 83 |
| medium | `1101103113` | -5 | 1 | 89 | 80 | 5 | `1101103111` | +57 | 85 |
| high | `0011311033` | -12 | 2 | 65 | 47 | 3 | `0010211033` | +78 | 61 |

Note on the named trimmed version: several trimmed versions tie at the same End-KZ, and the gate names the lowest code index (plan 02-08). Research named other tied versions: low `1121102000` (KZ before review 78, remaining +40, End-KZ 83), high `0011311031` (KZ before review 51, remaining +50, End-KZ 61). Both were re-evaluated with `evaluate_plan`; they reach exactly the same End-KZ as the named versions, so the required X is unaffected. Medium is named identically to research.

Other plans binding the strict minimum (scratch run, not pinned):
- low (3 plans need X = 9): `1121103000` (83 vs 91 - 9 = 82), `1221102000` (remaining -8, KZ before review 95, trimmed `0221102000` End-KZ 87), `2100133000` (remaining -10, KZ before review 95, trimmed `2100033000` End-KZ 87). Two more need X = 8 (`0200033003`, `1210103100`).
- medium (11 plans need X = 5): `1101103113`, `1110103113`, `1110311013`, `1111013113`, `1111103013` (2 steps), `1111211113`, and others.
- high (24 plans need X = 3): `0011311033`, `0100330133`, `0101301133`, `0110301133`, `0111300133`, `0111311033` (4 steps), and others.

## Reading

Low tier: the plan `1121103000` goes 10 kEUR over budget (one started step) and reaches 91 before the review. Both trimmed versions checked (`1121102000`: M7 L3 to L2, `0121103000`: M1 L1 cancelled) end in budget, score 78 before the review and gain the +5 Budget-Review tier, ending at 83. With X = 9 the over-budget plan ends at 82, one KZ below. Research attributes the 13 KZ gap before review to the M7 L3 step rewards (wave-2 M7 event +7 vs +3, Exzellenz +5 in wave 3); the M1 variant reaching the same 78 was not decomposed further. X = 9 is therefore exactly the strict minimum in the low tier (zero margin in X, 1 KZ margin in the outcome). Medium and high have headroom (X = 9 versus 5 and 3).

## Console output (`uv run planspiel gate`, runtime 120.1 s for three tiers including enumeration)

```
Überziehungs-Gate, Tier low: Referenzplan ohne Change-Fenster-Züge
  nötiges X (strikt) 9, (schwach) 8; Konfiguration X = 9 je angefangene 10 k€
  Pläne über Budget: 712882
  nicht verlierbar (gekürzte Version endet bei KZ 0): 0; nicht kürzbar (kein Plan im Budget darunter): 0
  Pläne, die mit X = 9 nicht strikt verlieren: 0
  bestimmender Plan 1121103000: Restbudget -10 k€, 1 angefangene Schritte, KZ vor Review 91, End-KZ 82, nötiges X 9
  gekürzte Version 0121103000: Restbudget 30 k€, End-KZ 83
  bestanden

Überziehungs-Gate, Tier medium: Referenzplan ohne Change-Fenster-Züge
  nötiges X (strikt) 5, (schwach) 4; Konfiguration X = 9 je angefangene 10 k€
  Pläne über Budget: 658015
  nicht verlierbar (gekürzte Version endet bei KZ 0): 0; nicht kürzbar (kein Plan im Budget darunter): 0
  Pläne, die mit X = 9 nicht strikt verlieren: 0
  bestimmender Plan 1101103113: Restbudget -5 k€, 1 angefangene Schritte, KZ vor Review 89, End-KZ 80, nötiges X 5
  gekürzte Version 1101103111: Restbudget 57 k€, End-KZ 85
  bestanden

Überziehungs-Gate, Tier high: Referenzplan ohne Change-Fenster-Züge
  nötiges X (strikt) 3, (schwach) 3; Konfiguration X = 9 je angefangene 10 k€
  Pläne über Budget: 584583
  nicht verlierbar (gekürzte Version endet bei KZ 0): 0; nicht kürzbar (kein Plan im Budget darunter): 0
  Pläne, die mit X = 9 nicht strikt verlieren: 0
  bestimmender Plan 0011311033: Restbudget -12 k€, 2 angefangene Schritte, KZ vor Review 65, End-KZ 47, nötiges X 3
  gekürzte Version 0010211033: Restbudget 78 k€, End-KZ 61
  bestanden

Überziehungs-Gate: bestanden
```

(Run before the commit `fix(02-08)` that rewords "1 angefangene Schritte" to "angefangene Schritte 1"; the numbers are unchanged.)

## Runtimes

- `uv run pytest -m slow --update-golden tests/test_overspend_gate.py -q`: 6 passed in 114.0 s (3 golden creations, 3 gate-pass tests; one `gate_tier` per tier through the module cache).
- `uv run pytest -m slow -q tests/test_overspend_gate.py` (no flag, goldens in place): 6 passed in 118.8 s.
- `uv run planspiel gate`: 120.1 s, all tiers passed.
- Fast suite `uv run pytest -q`: see SUMMARY.
