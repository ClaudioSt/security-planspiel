---
phase: 06-rebalance
plan: 09
subsystem: testing
tags: [tuning, calibration, d-04-checkpoint, candidate-config, clue-mapping]

requires:
  - phase: 06-rebalance
    provides: gate paths and X calibration (06-01), hand-calc errors (06-02), Final-Index k (06-03), choices (06-04), rewarding (06-05), spread (06-06), strategies and clue mapping (06-07), consolidated report (06-08)
provides:
  - candidate_config.json that passes every Phase-6 check (X = 3, k = 10, reference_strategies, re-chosen reference_plans)
  - candidate_content/ with the clue to measure mapping for 21 clues and two wording edits
  - 06-TUNING-REPORT.md (D-04 review document with change log) and the recorded D-04 approval
affects: [06-10]

tech-stack:
  added: []
  patterns:
    - "Tuning on a candidate file with a scratch driver that only calls enumerate_tier, gate.gate_from_columns and choices.*; verdict from the real tooling"
    - "Targeted text edits of the candidate (one line per value) so the adoption diff stays reviewable"

key-files:
  created:
    - .planning/phases/06-rebalance/candidate_config.json
    - .planning/phases/06-rebalance/candidate_content/clues.toml
    - .planning/phases/06-rebalance/candidate_content/texte.toml
    - .planning/phases/06-rebalance/candidate_content/digit_allowlist.toml
    - .planning/phases/06-rebalance/candidate_content/giveaway_terms.toml
    - .planning/phases/06-rebalance/06-TUNING-REPORT.md
  modified: []

key-decisions:
  - "D-04 answer (verbatim): \"Freigeben\" (2026-11-01), read as approval of all 13 points with the recommendations: start-lowered trim, raw/capped reading, X = 3, thresholds unchanged, structural value changes, k = 10, clue mapping incl. clue 21, reference strategies/paths, wording edits and labels, 06-08 interface choices, 06-10 consequences; D-13a not triggered"
  - "X = 3 (max over static, swap, window-1, window-2 families + 1); the narrow diagnostic needs 3 / 3 / 2 and passes at 3 with zero margin"
  - "k = 10 (tool recommendation, raw 11.6): KZ share 0.70 against 0.60..0.73"
  - "No story document edited; seven new clues quote existing sentences; the Confidentiality all-in is not a bad archetype (top quartile), bad_all_in is Integrity"

patterns-established:
  - "Constant start-KZ shifts are exact: they move best/median by the same amount and leave X, bands, drops, IQR and placements unchanged (used to put the low tier at best 90 static / 98 legal)"

requirements-completed: [BAL-01, BAL-02, BAL-03, BAL-06, BAL-07, BAL-08, BAL-09]

coverage:
  - id: D1
    description: "Candidate passes every Phase-6 check on both layers (gate with path families, decisions, strategies, rewarding, spread, Final-Index, hand-calc, clue mapping)"
    requirement: BAL-06
    verification:
      - kind: integration
        ref: "uv run python balance_analysis.py --config <cand> --layers all --paths --jobs 3 --baseline-config simulation_config.json: Gesamturteil alle berechneten Prüfungen bestanden"
        status: pass
      - kind: integration
        ref: "uv run pytest tests -m balance --runxfail --planspiel-config <cand> --planspiel-content-dir <cand_content> -q: 23 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "X calibrated at max + 1 = 3, gate and --narrow diagnostic"
    requirement: BAL-01
    verification:
      - kind: integration
        ref: "uv run planspiel gate --config <cand> --paths --jobs 3 (exit 0, kalibriert, 0 x 'nicht kalibriert'); --narrow exit 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "Hand-calc, texts and clues on the candidate"
    requirement: BAL-02
    verification:
      - kind: integration
        ref: "planspiel validate --strict, texts, clues: 0 errors, 0 warnings"
        status: pass
    human_judgment: false
  - id: D4
    description: "Frozen files unchanged, fast suite green"
    requirement: BAL-04
    verification:
      - kind: integration
        ref: "git diff --exit-code -- simulation_config.json content tests/golden final_documents print; uv run pytest -q: 2678 passed, 1 xfailed"
        status: pass
    human_judgment: false
  - id: D5
    description: "Value changes, thresholds, clue mapping, reference strategies and paths are acceptable"
    requirement: BAL-09
    verification: []
    human_judgment: true
    rationale: "Approved by the user at D-04 (\"Freigeben\", 2026-11-01)"

duration: about 7h (including about 3h of compute: baseline 22 min, search batches, three full reports of 36 min, gate 10 + 19 min, tausch 11 min, balance pytest 18 min)
completed: 2026-11-01
status: complete
---

# Phase 6 Plan 09: Tuning and D-04 checkpoint Summary

**A tuned candidate config and candidate content pass every Phase-6 check with the real tooling (X = 3 calibrated over static, swap and window families, k = 10, flatter event tiers, evened bonus stakes, clue mapping for 21 clues, reference strategies and paths); the user approved it at D-04 with "Freigeben".**

## Accomplishments

- Baseline re-run reproduced the research numbers (11 failed checks); the candidate fails none. Before and after (low / medium / high): required X static 9/5/3 to 2/2/2, best in budget 98/100/100 to 90/93/93 (legal layer 100 to 98/97/97), median 63/65/66 to 59/60/60, IQR 17 to 14, largest removal drop 14/16/18 to 1/4/4, largest band share 1.00 to 0.80/0.84/0.86.
- Tuning method: hand-guided structural batches plus a simulated-annealing driver over about 40 levers (scratch, outside the repo) using only `enumerate_tier`, `gate.gate_from_columns` and `choices.*`; no package installed; each accepted state verified with `balance_analysis.py`, `planspiel gate --paths`, `tausch` and `pytest -m balance --runxfail`. Full change log (24 hand batches, 85 search rows) is in the report.
- Content: `clues.toml` carries `measures` and `weight` for all 21 clues (seven new, quoting existing story sentences); no story document edited; two wording edits (Exzellenz narrative "gehobenem Niveau", final-index note without "vorläufig").
- Reference strategies (good derived from clue scores, mediocre, bad: ignore, all-in on Integrity, hoard) and re-chosen reference paths (end KZ 56/58/57 = legal medians) are in the candidate config.

## Approved values and consequences 06-10 must adopt

Adopt `candidate_config.json` and `candidate_content/` mechanically (copy over `simulation_config.json` and `content/`), then:

- Config values: attacks exfil -6..8, OT -6..8, ransomware -8..8 (slopes 2.0 / 1.4 / 2.0); budgets 370/390/405; start KZ 39/36/33; `e_threshold` 22 / 20 / 24; bonuses M4 5, M6 4, M7 3, M1 4, M8 3 (M3 6, M5 9, M2 6 unchanged); OEM-Audit tiers -2..3 linear; Kritische Schwachstelle {-3, 0, 0, 4}; Exzellenz Level 2 with 3 KZ; Nervige Authentifizierung -6; Budget Review 0/9/18/27 per 25 k EUR; `kz_per_step` X = 3; `final_index.weight_ros` k = 10; M6 init +6 at all levels; M7 CIA -2 per dimension (floored at 0).
- Thresholds: all module constants unchanged.
- `booklet.MAX_PENALTY_ROWS` 12 to 34 (X = 3) and re-prove the RoS page layout; `MAX_WINDOWS` stays 2.
- Flip the `hand_calc` default to error and update the six tests that assert the exfil warning; switch `require_mapping` on; build the facilitator clue column and add labels `sheets.spielleitung.final_index_weight` = "Gewicht k des RoS im Final-Index" and `clue_head_measures` = "Maßnahmen (Gewicht)" (the candidate content does not contain them yet); remove `final_index_provisional`, the "vorläufig" strings and the `≈`/fraction branch for slopes.
- Re-pin goldens (`characterization_*`, `digest_*`, `gate_*`, new `gate_paths_*`, `answer_keys.json`, `welle0.json`, `worksheet_tex.json`), re-run `practice.check_example`, then `planspiel print` and `print --check`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `pytest -m balance --runxfail --planspiel-config ...` needs the `tests` path**
- **Found during:** Task 3
- **Issue:** without a path argument pytest does not load `tests/conftest.py` before parsing, so the plan's command fails with "unrecognized arguments: --planspiel-config --planspiel-content-dir".
- **Fix:** run `uv run pytest tests -m balance --runxfail --planspiel-config <cand> --planspiel-content-dir <cand_content> -q` (23 passed). Recorded in the report; 06-10 should use the same form.
- **Files modified:** none

### Other deviations

- The plan's Task 2 step 4 asked for the gate to set X; X was set from the final calibrated run (3) after the start-KZ shift; k was changed from 15 to 10 after the full report recommended it, and the k-dependent checks were re-run (strategies placement, balance pytest on the final file) instead of repeating the 36 min report.
- Research seed candidates (hand-built review candidate, search seed 25) were not used as the final state; see "Open items" in the report.

## Known Stubs

None. The labels `final_index_weight` and `clue_head_measures` are proposals for 06-10 by design (adding them without code would be `texts.orphan_key`).

## Threat Flags

None. All edits are on candidate files; `git diff --exit-code -- simulation_config.json content tests/golden final_documents print` is clean (T-06-23); story text untouched, clue quotes verified verbatim and veil/giveaway/digit checks at 0 errors (T-06-24); no check or threshold was changed in code (T-06-25); scratch outputs only in gitignored `build/tuning/` (T-06-26); no package installed (T-06-SC).

## Task Commits

1. Task 1: `becfdde` feat(06-09): tuned candidate config with reference strategies, calibrated X and data-based k
2. Task 2: `bd94e9f` feat(06-09): candidate content with clue to measure mapping and two wording edits
3. Task 3: `39e4f77` docs(06-09): tuned candidate config and D-04 report
4. Task 4 (D-04 approval "Freigeben"): `1685810` docs(06-09): record D-04 approval

## Self-Check: PASSED

- Files exist: candidate_config.json, candidate_content/{clues,texte,digit_allowlist,giveaway_terms}.toml, 06-TUNING-REPORT.md (contains "D-04 decision")
- Commits exist: becfdde, bd94e9f, 39e4f77, 1685810
- `git diff --exit-code -- simulation_config.json content tests/golden final_documents print` exits 0; `uv run pytest -q` 2678 passed, 1 xfailed
