---
phase: 02-rule-changes
verified: 2026-10-05T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
advisory_findings:
  - id: WR-01
    classification: latent, not blocking
    note: "swap_possible only checks one active and one inactive measure; a config with L1 dependencies could leave a plan with no legal swap. Shipped configs are safe (no L1/L2 dependencies). Does not affect any success criterion on the shipped rule set."
  - id: WR-02
    classification: latent validator gap, not blocking
    note: "Validator does not enforce exactly one final_budget_tier event; shipped config has exactly one."
  - id: WR-03
    classification: wording, not blocking (path-level gate deferred by D-25 to Phase 6, recorded in CONTEXT.md, STATE.md, README line 268)
    note: "README heading 'Überziehen lohnt sich nie (automatisch geprüft)' oversells scope; the body names the reference plan. Recommend rewording and printing the margin config_x - min_x_strict in the gate report. Low tier has zero X headroom (9 = strict minimum)."
  - id: WR-04
    classification: maintainability, not blocking
    note: "Wave loop and ledger composition exist in 3-4 copies; conformance tests (exhaustive on mini config, 2000 random real paths under -m slow) guard drift."
  - id: WR-05
    classification: validator coverage gap, not blocking
    note: "event_without_window warns only for negative flat_budget in the last wave, not for OPEX-raising events there; README sentence is slightly broader than the check."
  - id: WR-06
    classification: naming/API hazard, not blocking
    note: "started_steps(amount_eur, step_eur=10_000) is named in euros but called with k EUR everywhere; results are correct for all current callers."
---

# Phase 2: Rule Changes Verification Report

**Phase Goal:** Every rule participants stumbled over at MHP is defined unambiguously, implemented test-first in the shared rules module and documented in README. Templates can then be written against a settled rule set. Numeric values (X, slopes, weights) stay provisional until Phase 6.
**Verified:** 2026-10-05
**Status:** passed
**Re-verification:** No, initial verification

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | README and config distinguish Levelwechsel from Maßnahmentausch (replaces MHP term "Maßnahmenwechsel"); Kurswechsel event names exactly which move it allows; simulation models change-window moves incl. a downgrade with sunk Init and lower OPEX from the next wave | VERIFIED | README.md section "Begriffe: Levelwechsel und Maßnahmentausch" (l.149-152) defines both terms and states that "Maßnahmentausch" replaces "Maßnahmenwechsel". Section "Kurswechsel (Maßnahmentausch)" (l.154-163). `simulation_config.json` wave_1 event `kurswechsel` (type `kurswechsel`) describes the single forced swap: one active measure drops out, one inactive measure joins, customer carries Init up to the dropped measure's Init, no refund. README "Change-Fenster" (l.140-147) allows Levelwechsel up and down, cancel, add. `rules.evaluate_path`, `rules.window_cost` (net Init per measure, never a refund, OPEX/CIA from next wave) are covered by `tests/test_paths.py` and `tests/test_kurswechsel.py`; both pass in the fast run. |
| 2 | Over budget costs X KZ per started 10.000 € (X from config; lookup table derivable for print); an event-induced overrun (Sparprogramm) is penalised only if still over budget after the change window | VERIFIED | `simulation_config.json` final_events `overspend_penalty {kz_per_step: 9, step: 10}`. `rules.budget_review_delta` and `rules.penalty_params` read X from config. `review_text.penalty_rows(9, 10)` prints `[(1, 10000, -9), (10001, 20000, -18), ...]` (executed). Single end check after the last wave, so a trim in the window removes the penalty; pinned by 15 scenarios in `tests/test_sparprogramm.py` on `evaluate_path` (trim, alternative trim, no trim, partial trim, forced swap). The Sparprogramm description and README bullet "Event-induzierte Überziehung" state the rule. |
| 3 | Overspend gate runs per tier in the test suite, compares every over-budget plan with its own trimmed in-budget version, reports the minimum X, fails naming the offending plan when config X is too low | VERIFIED | `planspiel/gate.py` (`lowering_closure`, `required_penalty_x`, `gate_tier`, `format_gate_report`), `planspiel gate` in `cli.py`. `tests/test_overspend_gate.py` fast tests pass (closure vs brute force, `test_synthetic_gate_names_the_offending_plan_when_x_is_too_low`, untrimmable/unlosable failures, mini brute force). Slow per-tier tests `test_overspending_never_pays_with_the_configured_x` and pinned `gate_{low,medium,high}.json` goldens (min X strict 9/5/3, weak 8/4/3, passed in every tier); the full slow suite was reported as 19 passed in 1527 s after the last plan and was not re-run here by instruction. Scope is the static reference plan (see WR-03 below); the criterion as written is met. |
| 4 | RoS identical with and without event cost effects (only Init, regular OPEX, Kurswechsel Init difference count); Budget Review tiers identical in sim and print at 25k/50k/75k, boundary text derived from the tier list | VERIFIED | `rules.security_spend` is the RoS denominator; `tests/test_ros_ledger.py::test_ros_is_invariant_under_event_cost_effects` (per tier) and `test_event_variants_do_change_the_budget_total` pass. Tiers `[[0,0],[25,5],[50,10],[75,15]]` in config; `review_text.boundary_text` generates card text from the list; `tests/test_budget_review_text.py` parses the text back and compares with the simulation at 24.999/25.000/49.999/50.000/74.999/75.000 € and for a mutated tier list; passes. README states "ab"-inclusive boundaries. |
| 5 | Per-wave E-target KZ bonus/malus resolved against printed MHP material and decision logged in PROJECT.md; removed or registered | VERIFIED | Removed. `.planning/PROJECT.md` l.115: "Decided 2026-10-01: removed from the simulation (RULE-08, D-19); no printed MHP material uses it". `rules.wave_kz_change(attack_kz_delta, event_kz)` has two arguments; validator reports stale `e_targets`/`kz_bonus`/`kz_malus` keys as `schema.removed_key`; `tests/test_e_target_removed.py` passes; README l.127 states there is no E-target bonus/malus. Snapshot change reviewed and approved (02-01-GOLDEN-DIFF.md). |

**Score:** 5/5 truths verified (0 present but behavior-unverified)

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|-------------|-------------|--------|----------|
| RULE-01 | 02-05 | SATISFIED | Truth 1: terms defined in README and config; Kurswechsel is exactly one forced Maßnahmentausch |
| RULE-02 | 02-06 | SATISFIED | Truth 1: `evaluate_path` models downgrade/cancel/add with net Init pricing; `tests/test_paths.py`, `tests/test_swap_layer.py` |
| RULE-03 | 02-03 | SATISFIED | Truth 2: `overspend_penalty` in config, linear, `penalty_rows` lookup |
| RULE-04 | 02-08 | SATISFIED | Truth 3: `planspiel/gate.py`, tests and goldens, `planspiel gate` exits 0 at X = 9 |
| RULE-05 | 02-07 | SATISFIED | Truth 2: single end check, `tests/test_sparprogramm.py` |
| RULE-06 | 02-02 | SATISFIED | Truth 4: own-spend RoS, invariance test per tier |
| RULE-07 | 02-04 | SATISFIED | Truth 4: generated boundary text and parse-back equivalence test |
| RULE-08 | 02-01 | SATISFIED | Truth 5: removed, logged in PROJECT.md |

All 8 IDs appear in plan frontmatter (02-01 .. 02-08, one requirement per plan), are marked `[x]` and "Complete" in REQUIREMENTS.md, and no Phase 2 ID in REQUIREMENTS.md lacks a plan. No orphaned requirements.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Fast suite | `uv run pytest -q` | 551 passed, 19 deselected | PASS |
| Phase test subset | `uv run pytest -q tests/test_overspend_gate.py tests/test_sparprogramm.py tests/test_budget_review_text.py tests/test_ros_ledger.py tests/test_kurswechsel.py tests/test_paths.py` | 177 passed, 6 deselected | PASS |
| Config validation | `uv run planspiel validate` | 0 errors, 1 warning (known `hand_calc.kz_slope attacks.exfil`, 17/7, Phase 6 input) | PASS |
| Penalty lookup | `penalty_rows(9, 10)[:2]` | `[(1, 10000, -9), (10001, 20000, -18)]` | PASS |
| Full slow suite | not re-run (instruction) | reported 19 passed in 1527 s after plan 02-08 | accepted per instruction |

### Anti-Patterns

Debt-marker scan (`TBD|FIXME|XXX`) over `planspiel/*.py`, `tests/test_*.py`, `tests/support/*.py`, `README.md`: no matches. No stubs found in the rule code paths; `generate_attack_calculator.py` is deliberately retired (D-29, archived in Phase 7).

### Code Review Findings (02-REVIEW.md, 6 warnings, 0 blockers) and success-criterion impact

None of the warnings makes a success criterion unmet on the shipped rule set.

- **WR-01 (swap without a legal swap):** latent. It triggers only for a config where every possible incoming measure has an L1 dependency on the dropped one. The shipped config has no L1/L2 dependencies (confirmed by the reviewer with mutated configs only). SC1 requires the Kurswechsel to name exactly which move it allows and the simulation to model it, both true. Recommended hardening: derive `swap_possible` from actual swap legality, or add a validator error for L1 dependencies, before Phase 6 changes the config.
- **WR-02 (several/no `final_budget_tier`):** validator gap only; shipped config has exactly one. Cheap to fix.
- **WR-03 (gate only on the static reference plan, zero margin in low tier):** SC3 asks for per-tier comparison of every over-budget plan with its own trimmed version, X reporting and failure naming; this is delivered. The path-level gate was explicitly deferred to Phase 6 by D-25 (CONTEXT.md l.63 and l.148, STATE.md l.102/110), and the README body (l.174, l.268) and gate report name the reference-plan scope. The remaining issue is the README heading wording "Überziehen lohnt sich nie (automatisch geprüft)", which implies a general guarantee. Not a gap against the roadmap; recommend rewording and printing the margin `config_x - min_x_strict`. The low-tier zero headroom is a known Phase 6 input (D-18).
- **WR-04 (duplicated wave loop and ledger tail):** maintainability and drift risk, mitigated by exhaustive mini-config and sampled real-config conformance tests; not a success-criterion issue.
- **WR-05 (event-overrun warning limited to negative `flat_budget`):** RULE-05 behavior is unaffected (the end check already handles it); only the validator warning is narrower than the README sentence.
- **WR-06 (`started_steps` unit naming):** all callers pass k EUR with a k EUR step; results correct.

### Human Verification Required

None. All five criteria are verified by tests or direct code and documentation inspection; checkpoint approvals for snapshot changes and the Sparprogramm description decision (plans 02-01, 02-02, 02-03, 02-05, 02-07, 02-08) are recorded in the SUMMARYs and treated as approved.

### Gaps Summary

No gaps. The phase goal is achieved: the rule set (Levelwechsel/Maßnahmentausch, downgrade, linear overspend penalty with gate, event-induced overruns, own-spend RoS, Budget Review boundaries, E-target removal) is defined, implemented test-first in `planspiel/rules.py`, and documented in README. Numeric values remain provisional (X = 9, 17/7 slope warning) and are routed to Phase 6. Recommended non-blocking follow-ups: README heading reword (WR-03), validator hardening (WR-01, WR-02, WR-05), and the `started_steps` signature (WR-06).

---

_Verified: 2026-10-05_
_Verifier: Claude (gsd-verifier)_
