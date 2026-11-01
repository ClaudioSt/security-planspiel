---
phase: 06-rebalance
verified: 2026-11-01T22:30:00Z
status: human_needed
score: 5/5 roadmap success criteria verified (9/9 requirements satisfied, 3 warnings open)
behavior_unverified: 0
overrides_applied: 0
re_verification: false
gaps: []
deferred:
  - truth: "Legacy hand-maintained docx/pptx (Angriff-*.docx, Massnahmenkarten pptx, Budget.docx, Events pptx) still carry pre-rebalance numbers"
    addressed_in: "Phase 7"
    evidence: "ROADMAP Phase 7 SC3 and REQUIREMENTS LEG-01 (Pending): legacy docx/pptx, old generators, pptx_output/ and the Excel calculator move to archive/ and the build no longer uses them; 06-CONTEXT D-24 scopes BAL-05 to the generated print set"
human_verification:
  - test: "Decide whether the move-path overspend gate must also cover the played path shape (mandatory Kurswechsel swap followed by a voluntary window move) before the next release (06-REVIEW WR-03)"
    expected: "Either a tausch_fenster2 family is added and passes at X = 3 for all tiers, or the claim 'auch auf den Spielpfaden mit Tausch und Fenster-Zug' in CLAUDE.md is narrowed to the three gated families"
    why_human: "Scope decision. D-13 defines the families as swap layer plus window-1 and window-2, and those pass. The reviewer's sampled probe of the missing family (tier low) found required X <= 1 and 0 violations at X = 3, so no exploit is known, but the full family and the other tiers are unmeasured."
  - test: "Read the facilitator booklet (spielleitung-uebersicht.pdf pages 8-10: clue matrix with Massnahmen (Gewicht) column, answer keys with weight row) and the attack worksheets (angriff-1..3) as a facilitator would"
    expected: "Readable, complete, no clipped table, printed numbers match the tuned config (X 3, k 10, review 0/9/18/27)"
    why_human: "Visual layout cannot be proven by fill reports. The verifier looked only at team booklet pages 3-4 (RoS and the 34-row Budget Review table), which render correctly. 06-10 coverage D4 is marked human_judgment."
  - test: "Confirm the D-04 open item that M7 Level 1 (CIA 0,1,0, only event insurance) reads as intended in the card text"
    expected: "Players understand M7 L1 as event insurance"
    why_human: "Content judgment recorded as 'please confirm' in the tuning report; the single-word D-04 answer 'Freigeben' covered it, but nobody has looked at the printed card."
---

# Phase 6: Rebalance Verification Report

**Phase Goal:** The config is tuned so the design principles hold under full enumeration: overspending never pays, every choice matters, good play wins, mediocre play still ends positive, and tiers stay comparable. All print material reflects the final numbers.
**Verified:** 2026-11-01
**Status:** human_needed (no failed truth; 3 human decisions and 3 tooling warnings)
**Re-verification:** No, initial verification

## Verifier Evidence (run in this verification, not taken from SUMMARY)

| Check | Command | Result |
|---|---|---|
| Fast suite | `uv run pytest -q` | 2659 passed, 185 deselected |
| Hand-calc / schema | `uv run planspiel validate --strict` | 0 Fehler, 0 Warnung(en) |
| Prose / clues | `uv run planspiel texts`, `uv run planspiel clues` | 0 Fehler, 0 Warnung(en) each |
| Print freshness | `uv run planspiel print --check` | "Druckmaterial aktuell: Stand 2026-11-01 . 84b7976 (13 Dokumente)", exit 0 |
| Static gate | `uv run planspiel gate` | bestanden in all 3 tiers; strict X needed 2 / 2 / 2 at configured X = 3 |
| Static balance report | `uv run python balance_analysis.py --jobs 3` (static layer, 93 s) | exit 0; top-K, Pareto fronts, in-budget and over-budget optima, Final-Index block, spread block all present; "Gesamturteil: alle berechneten Pruefungen bestanden" |
| Legal swap layer | `uv run planspiel tausch` (all tiers, 37.3 M paths each, ~12 min) | best legal in-budget KZ 98 / 97 / 97; medians 58 / 57 (medium, high) |
| Adoption fidelity | `cmp simulation_config.json .planning/phases/06-rebalance/candidate_config.json` | identical (the D-04-approved candidate) |
| Threshold drift | `git diff 1685810 HEAD` on choices/spread/rewarding/strategies/gate/index_weights | empty: no threshold changed after the D-04 approval |
| Print text scan | pypdf over all 13 PDFs in `final_documents/generated/` | no approximation sign, no "vorlaeufig", no "17/7" |
| Layout | Read of `spieler-teamheft.pdf` pages 3-4 | RoS page and Budget Review page render complete; table 0/9/18/27 and 34 penalty rows (-3 per started 10 k EUR) fit |

Not re-run (hours): `uv run pytest -m slow` (06-10 records 48 passed in 53 min on the adopted config) and the full `--layers all --paths` report (06-09 records "alle berechneten Pruefungen bestanden" on the byte-identical candidate). The static values reproduced here match 06-09 exactly (best 90 / 93 / 93, median 59 / 60 / 60, IQR 14, k = 10, KZ share 0.68 / 0.70 / 0.72), and the legal-layer bests reproduced (98 / 97 / 97), so the recorded slow-layer numbers are credible.

## Goal Achievement: ROADMAP Success Criteria

| # | Success Criterion | Status | Evidence |
|---|---|---|---|
| 1 | X calibrated per tier on trim-back (raw and capped); gate passes; D-13a decision if X impractical | VERIFIED | Config X = 3 (`overspend_penalty kz_per_step 3, step 10`). Static gate re-run: required X 2 / 2 / 2, passes. 06-10 `gate --paths --jobs 3` records exit 0 for static, tausch, fenster1, fenster2 in all tiers, "Konfiguration X = 3: kalibriert", max + 1 = 3, target X <= 5 met, so D-13a never triggered (no cap, no voided bonuses; D-22 respected). Raw and capped minima coincide in every cell (IN-01, harmless). `tests/golden/gate_paths_{low,medium,high}.json` and `test_path_gate_matches_golden` pin the result. Caveat: see warning W3 (played path shape swap + voluntary move not gated). |
| 2 | Validator runs hand-calc checks as errors and passes; no 17/7 slope | VERIFIED | `validate()` defaults to `hand_calc_level="error"` (`planspiel/validate.py`), `validate --strict` returns 0 errors on the committed config; all three slopes are one-decimal per the tuning report (2.0, 1.4, 2.0); `tests/test_hand_calc_level.py` in the fast suite. |
| 3 | Balance report without 0.85 filter, shows top-K, Pareto, unfiltered optima; Final-Index rescaled so RoS*100 no longer dominates KZ | VERIFIED | `grep` for 0.85 / utilization / Auslastung over `planspiel/` and the root scripts: no hit. Report output shows Top nach End-KZ / RoS / Final-Index (all and in budget), Pareto front all and in budget (28 / 30 / 32 points), and best in budget vs over budget per tier. Config `final_index = {weight_kz 1, weight_ros 10}`; measured IQR gives KZ share 0.68 / 0.70 / 0.72 (target 2/3, band 0.60..0.73), recommended k 10. "Vorlaeufig" label gone from README, CLAUDE.md, code, content, PDFs. |
| 4 | Design-principle checks pass per tier under full enumeration | VERIFIED (static layer re-run here; move layers via recorded slow suite and legal-layer re-run) | BAL-06..09 numbers below. 23 balance checks passed as hard checks (`--runxfail`, TUNING_TARGET since removed) on the candidate at 06-09 and the 48-test slow suite passed on the adopted config at 06-10. |
| 5 | All print material regenerated from the rebalanced config with one command; print equals sim and Welle-0 goldens pass | VERIFIED | `planspiel print --check` exit 0 (stamp 84b7976); `git log` shows `final_documents/generated` last written in 45cc36c after the config adoption d55392c; fast suite includes print-equals-sim and Welle-0 tests (green); `welle0.json` unchanged because the practice block is untouched, `worksheet_tex.json` and `answer_keys.json` re-pinned via `--update-golden` (06-10-GOLDEN-DIFF.md). |

**Score:** 5/5 criteria verified.

## Requirements Coverage

| Req | Verdict | Evidence |
|---|---|---|
| BAL-01 | SATISFIED (warning W3) | Calibrated global X = 3 = max + 1, gate passes on static plus swap/window-1/window-2 families in all tiers (D-13 definition). Best over-budget plan ends 77 / 77 / 75 against best in-budget 90 / 93 / 93. `planspiel/gate.py` has `_swap_stream`, `_static_stream`, `_window_stream`; `X_TARGET = 5`. Coverage gap: the swap-then-voluntary-move family is not gated and fenster1/2 include starts where the swap would be mandatory (confirmed in `gate.py:403-411`: no `swap_possible` filter). Reviewer sample probe found no exploit. |
| BAL-02 | SATISFIED | Hand-calc issues are errors by default; `validate --strict` 0/0; slopes one decimal; `approx_hint` and every printed approximation removed (PDF scan clean). The `master.py` `APPROX` helper remains as a formatter for any future non-terminating value, not used on the current numbers. |
| BAL-03 | SATISFIED | 0.85 filter absent; Final-Index = `KZ + 10 * RoS2` (`rules.final_index`, `index_weights.py`), k measured from pooled IQR, KZ share 0.70 reproduced. |
| BAL-04 | SATISFIED | Report reproduces top-K, in-budget top-K, Pareto fronts, unfiltered (all-combination) and in-budget optima per tier; `balance_analysis.py` is the entry point; `--baseline-config` comparison worked for the D-04 checkpoint. Warning W1 below concerns later baseline use only. |
| BAL-05 | SATISFIED | See criterion 5. `MAX_PENALTY_ROWS` raised to 34 with layout proof (fill 706.7 of 731.2 pt per 06-10; page visually checked here), `MAX_WINDOWS` = 2 unchanged and justified, reference paths re-chosen and pinned, "vorlaeufig" dropped, approximations removed. Legacy docx/pptx intentionally excluded per D-24; deferral is real (see Deferred). |
| BAL-06 | SATISFIED | No measure near-mandatory: largest band share 0.80 / 0.84 / 0.86 (< 0.90). Largest removal drop 1 / 4 / 4 KZ (< 10; baseline M7 was 14 / 16 / 18). Smallest improvement share of a level 0.04 (M1 L3), so none strictly dominated. Decision points: Kurswechsel spread >= 3 KZ in 0.98 of starts, window move 0.53 (bound 0.50, thinnest margin), tier band Jaccard 0.09 / 0.13 / 0.08 (<= 0.5). Static numbers from the 06-09 report; thresholds untouched since. Thin-margin items listed under Human Verification context. |
| BAL-07 | SATISFIED | `reference_strategies` key exists (D-25) with good, mediocre, bad_ignore, bad_all_in, bad_hoard per tier; good derived from the clue mapping and asserted equal to `strategies.clue_good_start`; good places 0.93-0.98 below, bad 0.90-0.99 above (needs 0.75 in both populations); non-clue plan share 0.69 / 0.73 / 0.75 (>= 0.20) so buying only bonus measures is not automatically best. Overspender judged by the gate (D-23). 21 clues carry measure and weight; `planspiel clues` (require_mapping default true) passes. |
| BAL-08 | SATISFIED | Median in-budget minus start KZ +20 / +24 / +27 static, +17 / +22 / +24 legal (needs >= 5, <= 28). Comeback: 0.96 / 0.99 / 1.00 of starts reach start + 10 (bound 0.9); 0.99 / 1.00 / 1.00 end above start. Legal medians re-observed here (58 / 57 for medium and high). |
| BAL-09 | SATISFIED | Re-run here: best static 90 / 93 / 93 (window 90..98), legal 98 / 97 / 97; medians 59 / 60 / 60 static; corridor 3 (limit 6); IQR 14 all tiers (13..21, tier diff 0); p5..p95 width 30 / 32 / 33 (<= 50). Low tier sits on the 90 bound (static) and the 98 bound (legal); passes, thinnest margin. |

No orphaned requirements: REQUIREMENTS.md maps exactly BAL-01..09 to Phase 6.

## Deferred Items

| Item | Addressed in | Evidence |
|---|---|---|
| Legacy hand-maintained Angriff-1/2/3 docx, Massnahmenkarten pptx, Budget.docx, Events pptx still show pre-rebalance numbers | Phase 7 (LEG-01, Pending) | ROADMAP Phase 7 SC3: they move to `archive/` and the build no longer uses them; STATE.md also records LEG-01 follow-ups. The deferral is planned and explicit, not dropped. Until Phase 7 runs, `final_documents/` contains stale legacy files next to `generated/`; do not print from the legacy files. |

## Anti-Patterns

TBD/FIXME/XXX scan over `planspiel/` and `print/templates` returned nothing. No stub or hollow-prop pattern applies (CLI and PDF generation, no UI state). No blockers.

## Code Review Findings Weighed (06-REVIEW.md, 0 critical, 6 warnings)

| Finding | Does it break a requirement or criterion? | Verdict |
|---|---|---|
| WR-01 strict hand-calc default makes the report's Handrechnung block unable to fail; `--baseline-config` with a non-hand-calculable config aborts with exit 2 | No. BAL-02 requires the validator to enforce hand-calc as errors, and it does (config load fails). The report block is redundant, not wrong. The before/after comparison was produced for D-04 before the default flipped. Residual: future comparison against the pre-rebalance config no longer works until `load_config` takes a lenient level. | WARNING W1, tooling debt |
| WR-02 cross-tier checks vacuous under `--tier` | No. Full runs (default, all tiers) evaluate every cross-tier block; verified in the static run above. Only single-tier runs are weaker. | WARNING W2, tooling debt |
| WR-03 path gate lacks the swap-plus-voluntary-move family; fenster1/2 include starts where a swap would be mandatory | No requirement text demands it (D-13 names swap layer and window-1/window-2 families), SC1 holds as written. It weakens the CLAUDE.md claim about "Spielpfaden mit Tausch und Fenster-Zug" and the confidence that overspending never pays on the actually played path shape. Reviewer probe: no violations. | WARNING W3, routed to human decision |
| WR-04, WR-05, WR-06, IN-01..07 | Error-code hygiene, misattributed messages, dead filters, report rounding in float formatting; no goal impact. | Informational |

## Gaps Summary

No gap blocks the phase goal. Every roadmap success criterion and all nine BAL requirements are supported by code, config and regenerated print material, and the independently re-run checks (fast suite, validator, gate, static balance report, legal swap layer, print freshness, PDF scan) agree with the recorded 06-09 and 06-10 numbers. Status is `human_needed` rather than `passed` because three items need a person: the scope decision on the unmeasured swap-plus-voluntary-move gate family (W3), a visual read of the facilitator material, and confirmation of the M7 L1 card wording. W1 and W2 are suggested follow-ups (candidate for a Phase 7 hygiene task or `/gsd-code-review --fix`), not blockers.

---

_Verified: 2026-11-01_
_Verifier: Claude (gsd-verifier)_
