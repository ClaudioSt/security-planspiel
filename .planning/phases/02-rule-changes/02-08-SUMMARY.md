---
phase: 02-rule-changes
plan: 08
subsystem: rules
tags: [overspend-gate, trim-back, rule-04, d-17, d-18, d-24, d-25, golden]
requires: [02-07, 02-03, 02-01]
provides:
  - "planspiel/gate.py: lowering_closure, required_penalty_x, GateResult, gate_from_columns, gate_tier, gate_result_json, format_gate_report, public helper trim_keys"
  - "CLI subcommand `planspiel gate [--config] [--tier ...]` (exit 0 = passed in every tier)"
  - "tests/test_overspend_gate.py: fast tests (closure vs brute force, synthetic failure naming, mini-config brute force, CLI) and slow per-tier gate tests"
  - "pinned goldens tests/golden/gate_{low,medium,high}.json"
  - "02-08-GATE-REPORT.md: reviewed per-tier gate report against research M1"
  - "STATE.md Phase-6 input: soften step rewards (D-18), no cap, no voiding; move-path gate deferred (D-25)"
affects: [phase-06-rebalance]
tech-stack:
  added: []
  patterns: ["prefix-maximum closure over the 4^n level lattice instead of a pairwise search", "gate compares each over-budget plan with its own trimmed in-budget version (clamp-aware)", "goldens created via --update-golden and committed only after a blocking review"]
key-files:
  created:
    - planspiel/gate.py
    - tests/test_overspend_gate.py
    - tests/golden/gate_low.json
    - tests/golden/gate_medium.json
    - tests/golden/gate_high.json
    - .planning/phases/02-rule-changes/02-08-GATE-REPORT.md
  modified:
    - planspiel/cli.py
    - tests/test_single_definition.py
    - README.md
    - CLAUDE.md
    - .planning/PROJECT.md
    - .planning/STATE.md
key-decisions:
  - "RULE-04 / D-17: overspending never pays under the trim-back criterion; measured strict minimum X on the static reference is 9 / 5 / 3 (weak 8 / 4 / 3), identical to research M1 including the full X histograms"
  - "Config X = 9 passes in every tier but has zero headroom in the low tier (strict minimum 9, worst margin 1 KZ); low 9 > ~5 is the Phase-6 input: soften step rewards per D-18, no cap, no voiding"
  - "The slow gate over move paths (swap/window families) stays deferred to Phase 6 (D-25); the static reference is the gate basis (D-24)"
duration: ~2h (including the review checkpoint and the 25 min full slow suite)
completed: 2026-10-05
status: complete
requirements-completed: [RULE-04]
---

# Phase 2 Plan 08: Overspend Trim-Back Gate Summary

An automated gate now proves per tier that no over-budget plan beats its own best trimmed in-budget version (levels only lowered or measures cancelled), reports the minimum X required, and fails naming the offending plan when the config X is too low. The measured strict minimum X is 9 / 5 / 3 (weak 8 / 4 / 3), exactly as research predicted, so the provisional config X = 9 passes in every tier, with zero headroom in the low tier.

## Tasks

| Task | Name | Commit |
|------|------|--------|
| 1 RED | Failing tests for the overspend trim-back gate | 5b3e459 |
| 1 GREEN | Lowering closure, required X, gate result | 2b2c723 |
| 2 | `planspiel gate` command and fast CLI test | 10a5034 |
| 2 (extra) | Grammatical wording of the started steps in the gate report | 94bbee4 |
| 3 | Pinned gate goldens and slow gate tests (after user approval) | 2fe2fbe |
| 3 | README, CLAUDE.md, PROJECT.md, STATE.md, gate report | 8e1170d |

## Measured gate result (static reference, X = 9 per started 10 kEUR)

| Tier | over-budget plans | min X strict | min X weak | unlosable | untrimmable | violations at X = 9 | worst margin at X = 9 | passed |
|------|-------------------|--------------|------------|-----------|-------------|---------------------|-----------------------|--------|
| low | 712,882 | 9 | 8 | 0 | 0 | 0 | 1 KZ | yes |
| medium | 658,015 | 5 | 4 | 0 | 0 | 0 | 5 KZ | yes |
| high | 584,583 | 3 | 3 | 0 | 0 | 0 | 7 KZ | yes |

Strict-X histograms equal research M1 in every tier (low {1: 679,007, 2: 31,617, 3: 1,724, 4: 299, 5: 146, 6: 64, 7: 20, 8: 2, 9: 3}, medium {1: 651,931, 2: 5,778, 3: 258, 4: 37, 5: 11}, high {1: 584,030, 2: 529, 3: 24}).

Witness plans (largest strict X, ties: lowest code index): low `1121103000` (remaining -10, 1 step, KZ before review 91, End-KZ 82) vs trimmed `0121103000` (End-KZ 83); medium `1101103113` vs `1101103111` (End-KZ 80 vs 85); high `0011311033` (2 steps, End-KZ 47) vs `0010211033` (End-KZ 61).

## Verification

- Task 1 RED (5b3e459): collection error `ImportError` in `tests/test_overspend_gate.py` (module `planspiel.gate` missing), plus `2 failed` in `tests/test_single_definition.py` (the new `GATE` file entry pointing at a missing module).
- Task 1 GREEN (2b2c723): targeted run `87 passed`, full fast suite `549 passed`.
- Task 2: `uv run pytest -m slow --update-golden tests/test_overspend_gate.py -q` created the three goldens, `6 passed in 114.0 s`; rerun without the flag `6 passed in 118.8 s`.
- Final fast suite after the commits: `uv run pytest -q` gave `551 passed, 19 deselected, 101 warnings in 25.02s`.
- Full slow suite, run once after the commits: `uv run pytest -m slow -q` gave `19 passed, 551 deselected, 13 warnings in 1527.49s (0:25:27)`, exit 0.
- `uv run planspiel validate`: `WARN hand_calc.kz_slope attacks.exfil: KZ-Steigung 17/7 hat mehr als eine Nachkommastelle (verwendet in Welle 3)` then `0 Fehler, 1 Warnung(en)`, exit 0.
- `uv run planspiel gate`: exit code 0, final line `Überziehungs-Gate: bestanden`.
- `git log -4 --format="%h %s"` after the commits: `8e1170d docs(02-08): ...`, `2fe2fbe test(02-08): ...`, `94bbee4 fix(02-08): ...`, `10a5034 feat(02-08): ...`.
- Approval: the user replied "approved" at the Task 3 checkpoint, including the deviations below; nothing was committed before that.

## Deviations from Plan

### Auto-fixed / noted

**1. [Rule 1 - Naming] Tie-break names different trimmed example plans in low and high**
- **Found during:** Task 2 (report vs research)
- **Issue:** several trimmed versions tie at the same End-KZ. The gate names the lowest code index (as the plan specifies), research named other tied versions: low `1121102000` (research) vs `0121103000` (gate), high `0011311031` vs `0010211033`.
- **Fix:** none needed. Both research versions were re-evaluated and reach exactly the same End-KZ (low 83, high 61), so the required X is unaffected. Documented in the gate report.

**2. [Rule 1 - Accuracy] Partial explanation of the low-tier driver plan**
- **Issue:** research attributes the 13 KZ gap before review to the M7 L3 step rewards (wave-2 M7 event +7 vs +3, Exzellenz +5 in wave 3). The M1 variant `0121103000` reaching the same 78 was not decomposed further, so the explanation holds for the M7 L3 to L2 trim only.
- **Fix:** the gate report states this caveat instead of generalising.

**3. [Rule 1 - Date] PROJECT.md says gate implemented 2026-10-04**
- **Issue:** the plan text said 2026-10-01, but the gate was implemented on 2026-10-04.
- **Fix:** the actual date was written. Commit 8e1170d.

**4. [Rule 1 - Wording] Extra commit 94bbee4**
- **Issue:** `format_gate_report` printed "1 angefangene Schritte", which is ungrammatical.
- **Fix:** reworded to "angefangene Schritte 1"; numbers unchanged. The console output pasted in the gate report predates this wording (noted there). Commit 94bbee4.

**5. [Rule 3 - Structure] Public helper `gate.trim_keys`**
- **Issue:** the plan places the key building and closure inside `gate_from_columns`. The slow tests and the mini-config brute-force tests need the trimmed keys per code.
- **Fix:** the key construction was extracted into the public helper `trim_keys(n_measures, code_index, kz_final, over_budget) -> array`, which `gate_from_columns` calls. Behaviour matches the plan.
- **Commit:** 2b2c723

### Notes

- Pinned goldens and docs were committed only after the user's approval (T-02-28).
- Line endings were preserved (CRLF); git only warned about LF to CRLF conversion on touched files.
- The Phase-6 input in STATE.md uses the measured numbers (they equal the plan's).

## Phase-6 inputs

- Low tier: strict minimum X 9 is far above the medium 5 and high 3; direction decided in D-18: soften step rewards (Exzellenz, OEM-Audit tiers, M7 tiers), no overspend cap, no voiding of bonuses.
- Research M2 numbers: partial softening reaches low 6, flattening all step rewards gives 4 / 2 / 1.
- Config X = 9 is provisional (D-25); the slow gate over move paths (swap/window families) is deferred to Phase 6.

## Auth gates

None.

## Known Stubs

None.

## Threat Flags

None. T-02-28 (golden repudiation) mitigated by the blocking review; T-02-29 (trivial pass at KZ 0) by comparing against each plan's own trimmed version with `unlosable`, `untrimmable` and `violations_at_config_x` all failing the gate; T-02-30 (closure bug) by brute-force equality on random lattices and on the mini config for all tiers; T-02-31 (runtime) by the existing enumeration plus a 10-pass closure (about 40 s plus 2.5 s per tier, slow marker only).

## Self-Check

- FOUND: planspiel/gate.py with `def lowering_closure(`, `def required_penalty_x(`, `class GateResult(NamedTuple)`, `def gate_from_columns(`, `def gate_tier(`
- FOUND: tests/test_overspend_gate.py, tests/golden/gate_low.json, gate_medium.json, gate_high.json, 02-08-GATE-REPORT.md
- FOUND commits: 5b3e459, 2b2c723, 10a5034, 94bbee4, 2fe2fbe, 8e1170d
- `uv run pytest -q`: 551 passed; `uv run pytest -m slow -q`: 19 passed in 1527.49s; `uv run planspiel validate`: 0 Fehler; `uv run planspiel gate`: exit 0

## Self-Check: PASSED
