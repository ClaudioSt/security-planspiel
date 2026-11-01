---
phase: 06-rebalance
plan: 10
subsystem: print
tags: [adoption, goldens, print-regeneration, hand-calc, final-index, clue-matrix]

requires:
  - phase: 06-rebalance
    provides: D-04-approved candidate config and content (06-09), gate paths and X calibration (06-01), hand-calc errors (06-02), Final-Index k (06-03), clue mapping (06-07), consolidated balance report (06-08)
provides:
  - simulation_config.json and content/ adopted byte for byte from the D-04-approved candidate (X = 3, k = 10, reference_strategies, re-chosen reference_plans)
  - hand-calc findings are errors by default, the clue mapping is required by default
  - Final-Index printed without a provisional label (RoS2 and index exact, weight row), facilitator clue matrix with the Massnahmen (Gewicht) column
  - all goldens re-pinned through --update-golden, new gate_paths_{low,medium,high}.json and test_path_gate_matches_golden
  - regenerated generated print set (13 PDFs and manifest.json), print --check exits 0
affects: [07-legacy-documents]

tech-stack:
  added: []
  patterns:
    - "Tie rounding is tested on a test-only copy of the real config with a 3/2 slope (tests/support/ties.py) because the tuned config has no .5 tie"
    - "Real-config literals in tests are derived from config values or rules where practical; the rest is re-pinned with a hand check of the arithmetic"

key-files:
  created:
    - .planning/phases/06-rebalance/06-10-GOLDEN-DIFF.md
    - tests/support/ties.py
    - tests/golden/gate_paths_low.json
    - tests/golden/gate_paths_medium.json
    - tests/golden/gate_paths_high.json
  modified:
    - simulation_config.json
    - content/texte.toml
    - content/clues.toml
    - planspiel/validate.py
    - planspiel/texts.py
    - planspiel/booklet.py
    - planspiel/master.py
    - planspiel/report.py
    - planspiel/refpaths.py
    - print/planspiel.sty
    - print/templates/master.tex.j2
    - print/templates/teamheft_ros.tex.j2
    - final_documents/generated/ (13 PDFs and manifest.json)
    - README.md
    - CLAUDE.md

key-decisions:
  - "The pre-flight regex of the plan matched neither the recorded answer (\"Freigeben\") nor the word \"approval\"; the plan went ahead on the verbatim D-04 answer recorded in 06-TUNING-REPORT.md and the orchestrator's confirmation (deviation 1)"
  - "Budget Review page: 34 penalty rows fit on the page with compact lookup rows (rowstrutlookup 4 mm + 0.8 mm), 8.5 mm write-in rows (rowstrutmid) and the lookup tier table; type size unchanged; fill report 706.7 pt of 731.2 pt"
  - "A third clue-section label (clue_section_zeitungsartikel) was added: clue 21 quotes the newspaper ticker, which has no heading of its own and would have printed its raw source key in the facilitator matrix"

patterns-established:
  - "Golden bootstrap: delete characterization_<tier>.json and run --update-golden to rebuild the census sample for a new config (tests/support/golden_cases.py)"

requirements-completed: [BAL-05]

coverage:
  - id: D1
    description: "Approved candidate adopted byte for byte; hand-calc errors and required clue mapping on by default"
    requirement: BAL-05
    verification:
      - kind: integration
        ref: "cmp simulation_config.json candidate_config.json; uv run planspiel validate --strict, texts, clues: 0 errors, 0 warnings"
        status: pass
    human_judgment: false
  - id: D2
    description: "Fast, slow and pdf suites green on the adopted config incl. path-gate golden, print equals simulation and Welle-0 goldens"
    requirement: BAL-05
    verification:
      - kind: integration
        ref: "uv run pytest -q: 2659 passed; uv run pytest -m pdf -q: 137 passed; uv run pytest -m slow -q: 48 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "Generated print set rebuilt from the adopted config, freshness check passes, no approximation sign, penalty table fits the RoS page"
    requirement: BAL-05
    verification:
      - kind: integration
        ref: "uv run planspiel print --check: exit 0 (stamp 84b7976); tests/test_booklet_pdf.py fill report 706.7 of 731.2 pt"
        status: pass
    human_judgment: false
  - id: D4
    description: "Printed layouts are readable and complete (team booklet RoS and Budget Review pages, facilitator booklet with weight row and clue column, attack worksheets)"
    verification: []
    human_judgment: true
    rationale: "Visual readability of printed material cannot be proven by fill reports; the executor looked at team booklet page 4 and facilitator pages 8 to 10 only"

duration: about 5h (including about 1h 40m of slow-suite compute: two full runs plus the reference-path run)
completed: 2026-11-01
status: complete
---

# Phase 6 Plan 10: Adopt the approved candidate Summary

**The D-04-approved candidate is the committed config and content (X = 3, k = 10, clue mapping for 21 clues), hand-calc errors and the required clue mapping are the defaults, every golden is re-pinned through the reviewed path, and the 13 generated PDFs are rebuilt from the rebalanced numbers.**

## Accomplishments

- **Adoption:** `simulation_config.json` is a byte copy of `candidate_config.json` (`cmp` exits 0); `content/clues.toml` and `content/texte.toml` are the candidate files. `planspiel validate --strict`, `texts` and `clues` report 0 errors and 0 warnings.
- **Switches:** `validate()` defaults to `hand_calc_level="error"`, `check_clues()` to `require_mapping=True`. The mini fixture slope of the third attack is now -5..9 (cap 7), so it loads.
- **Final-Index carry-over (06-03):** master answer keys print RoS2 and the index exactly (52,6 / 54,7 / 57,6) with a weight row (k = 10); report, refpaths and console labels lost the provisional wording; the `final_index_provisional` key is gone; the 06-03 golden substitution and its strict-xfail row test are removed and `answer_keys.json` is pinned once.
- **Facilitator clue matrix:** new column "Maßnahmen (Gewicht)" (`ClueEntry.measures`, label `clue_head_measures`), 21 clues.
- **Approximations:** `approx_hint` is removed from model, template, content and key list; tests assert no printed master string and no rendered or built document contains an approximation sign.
- **Goldens (only through `--update-golden`):** characterization re-bootstrapped, `answer_keys`, `worksheet_tex`, `digest_*`, `gate_*` re-pinned, new `gate_paths_*` with `test_path_gate_matches_golden`. `welle0.json` is unchanged (the practice block is untouched). Details and the update summaries: `06-10-GOLDEN-DIFF.md`.
- **Reference paths:** `planspiel referenzpfade` on the adopted config confirms the pinned paths: medians 56 / 58 / 57, the pinned plans end on exactly those values, are legal and in budget and carry the swap plus a voluntary move.
- **TUNING_TARGET** and its definition are gone; the balance checks are plain slow checks.
- **Print set:** `planspiel print` rebuilt 13 PDFs and `manifest.json`, `print --check` exits 0 ("Druckmaterial aktuell", stamp 84b7976), `git status` clean afterwards. Page counts: team booklet 4, facilitator booklet 12.
- **Docs:** README, CLAUDE.md and PROJECT.md state the final rules without provisional notes.

## Task Commits

1. Task 1: `d55392c` feat(06-10): adopt the rebalanced config approved at D-04
2. Task 2: `e952690` test(06-10): pin slow goldens and the move-path gate on the rebalanced config; `c9d5c4b` docs(06-10): final rules after the rebalance
3. Task 3: `cc60e9b` feat(06-10): remove approximation hints, prove layouts for the rebalanced print set; `45cc36c` feat(06-10): regenerate print material from the rebalanced config

## Verification

| Check | Result |
|---|---|
| `cmp simulation_config.json .planning/phases/06-rebalance/candidate_config.json` | exit 0 |
| `uv run pytest -q` | 2659 passed (fast, 185 deselected) |
| `uv run pytest -m pdf -q` | 137 passed (3 min 39 s) |
| `uv run pytest -m slow --update-golden -q` (once, 56 min 50 s) | all balance checks without markers passed; one count pin of `test_swap_layer` updated by hand (see deviations) |
| `uv run pytest -m slow -q` (final, without flag) | 48 passed, 0 failed (53 min 14 s) |
| `uv run planspiel validate --strict` / `texts` / `clues` | 0 Fehler, 0 Warnung(en) |
| `uv run planspiel gate --paths --jobs 3` | exit 0: all three tiers and all families passed, "Konfiguration X = 3: kalibriert", recommended X = max + 1 = 3, "Ziel X <= 5: erreicht" |
| `uv run planspiel print --check` | "Druckmaterial aktuell: Stand 2026-11-01 · 84b7976 (13 Dokument(e) ...)", exit 0 |
| `git status --porcelain -- final_documents/generated simulation_config.json content planspiel tests print` | empty |

## Deviations from Plan

### Auto-fixed Issues

**1. [Pre-flight, Rule 3] The D-04 pre-flight regex gave a false negative**
- **Found during:** Task 1 step 0
- **Issue:** the command looks for `approved|freigegeben` in the "D-04 decision" section; the section says "Freigeben" (the user's verbatim answer) and "approval", which match neither word.
- **Fix:** none to the report. The section records date 2026-11-01, the verbatim answer "Freigeben" and the reading "approval of all 13 points"; together with the orchestrator's explicit statement of the approval this is the approval the gate is meant to find, so the plan went ahead. The check was not edited to pass.

**2. [Rule 3 - Blocking] The characterization bootstrap path was dead**
- **Found during:** Task 1 step 4 (the old census sample no longer touches the budget-review and threshold boundaries, so the boundary-mutation test could not fail)
- **Issue:** `tests/support/golden_cases.py` imported `balance_analysis.define_strategies`, which 06-08 removed.
- **Fix:** the 27 named sample plans are now a constant (`STRATEGY_CODES`, same codes as in the pinned files); the three characterization files were removed and rebuilt through `--update-golden` (9 min 20 s).
- **Files modified:** tests/support/golden_cases.py, tests/golden/characterization_*.json

**3. [Rule 1 - Bug in test premise] No .5 tie exists on the tuned config**
- **Issue:** one-decimal slopes and one-decimal E values make a half-integer attack delta impossible, so tests that took a `census:tie_w3` case from the golden had nothing to take.
- **Fix:** `tests/support/ties.py` builds a test-only copy of the real config with a 3/2 slope for the third attack; the positive and negative tie tests, the kernel conformance tie test and the characterization category test use it (the pure rounding function tests stay).

**4. [Rule 2 - Missing critical content] Section label for clue 21**
- **Issue:** clue 21 quotes the newspaper ticker (`story.zeitungsartikel.ticker`), which has no heading, so the facilitator matrix printed the raw source key (caught by `test_no_clue_matrix_cell_of_the_real_content_is_a_source_key`).
- **Fix:** label `sheets.spielleitung.clue_section_zeitungsartikel = "Ticker"` in `content/texte.toml`, the mini content and the key list. This is a third label beyond the two approved at D-04; it carries no number and no veiled information (facilitator sheet only).

**5. [Rule 1 - Bug] Weight row without a row end**
- **Issue:** the new weight row in `master.tex.j2` lacked its closing `\\`, so LuaLaTeX stopped ("Misplaced \noalign"); the fast suite does not build PDFs, so the Task 1 commit contains the broken template.
- **Fix:** repaired in the Task 3 commit (found by the first `-m pdf` run); no build was made from the broken state.

**6. [Rule 1 - Layout] Budget Review page and clue column overflowed**
- **Issue:** with 34 penalty rows the page needed 893 pt of 731 pt; the new clue column produced overfull lines.
- **Fix:** `\rowstrutlookup` (read-only lookup rows) for the overspend and tier tables, `\rowstrutmid` (8.5 mm) for the write-in rows of the review page, two tables side by side kept (`penalty_split` became `penalty_per_table`, constant `PENALTY_TABLES = 2`); clue table columns 47 mm / 19 mm. A three-table layout was tried and rejected (the column header "KZ-Änderung" needs 22 mm). Type size is unchanged.

**7. Tests that pinned pre-tuning real-config facts (about 130 failures after adoption)**
- Re-derived from config where practical: tier table, penalty rows, Budget Review tiers and penalty, hand-calc expectations (validate, load_config, CLI), worksheet constants and replay, print model, clue counts, event text, final-index config.
- Redesigned scenarios: `test_sparprogramm.py` (exempt and Kurswechsel plans re-searched for the new budgets: `1211111211` with trims, low `1111112211`, Kurswechsel `0010032223`), reference path structure in `test_reference_plans.py`.
- Hand-checked re-pins: empty-selection outcomes (KZ 28 / 17 / 11, final 38), paths costs (M6 init +6), `test_swap_layer` swap counts (`swap_in_budget` 4_457_231, `swap_over_budget` 32_843_505, total unchanged).
- `test_digest` and `test_validate` mutations changed to keep the mutated config hand-calculable.

## Known Stubs

None.

## Threat Flags

None. The adoption is a byte copy of the approved candidate (T-06-27), golden files were written only through `--update-golden` with the summaries recorded (T-06-28), `planspiel print` ran the text, clue and veil scans and `-m pdf` passed including the veil tests (T-06-29), no scratch output was committed (T-06-31), no package was installed (T-06-SC).

## Follow-up (not in this plan)

- **Legacy documents in `final_documents/` are not updated** (D-24; Phase 7, LEG-01). They carry hand-maintained numbers that changed with this adoption: `Angriff-1_Ransomware.docx`, `Angriff-2_OT-Störung.docx`, `Angriff-3_Datenexfiltration.docx` (thresholds, caps, case constants, bonus table), `Massnahmenkarten_Security-Game.pptx` (M6 init, M7 CIA), `Budget.docx` (tier budgets and start KZ), `Events_Security-Game.pptx` (event tiers, Budget Review 0/9/18/27, X), `Return on Security und Final Wert.docx` (Final-Index). The generated PDFs in `final_documents/generated/` replace them for the workshop.
- A visual read of the printed material by a human (Task 3 human check): the executor checked team booklet page 4 and facilitator pages 8 to 10 as images; the attack worksheets, Welle-0 sheet and remaining pages were verified by the PDF tests only.

## Self-Check: PASSED

- Files exist: 06-10-GOLDEN-DIFF.md, tests/support/ties.py, tests/golden/gate_paths_{low,medium,high}.json, final_documents/generated/manifest.json
- Commits exist: d55392c, e952690, c9d5c4b, cc60e9b, 45cc36c
- `cmp simulation_config.json .planning/phases/06-rebalance/candidate_config.json` exits 0; `uv run pytest -q` 2659 passed, `-m pdf` 137 passed, `-m slow` 48 passed; `planspiel print --check` exit 0
