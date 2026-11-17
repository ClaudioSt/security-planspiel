---
phase: 2
slug: rule-changes
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-10-01
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | `pyproject.toml` (`testpaths = ["tests"]`, `addopts = "-m 'not slow' --strict-markers"`, marker `slow`) |
| **Quick run command** | `uv run pytest -q` |
| **Full suite command** | `uv run pytest -m slow -q -s` (plus `uv run pytest -q` for the fast set) |
| **Estimated runtime** | ~15 s quick; ~21 min slow today, +2–3 min for the static gate (02-08), + a few minutes for the low-tier swap layer (02-06, bound 900 s); the slow move-path gate is deferred to Phase 6 (D-25) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest -q`
- **After every plan wave:** Run `uv run pytest -q` plus the relevant slow check for the changed layer (`uv run pytest -m slow <affected file> -q`)
- **Before `/gsd-verify-work`:** `uv run pytest -m slow` and `uv run pytest -q` green, `uv run planspiel validate` 0 errors (known 17/7 warning stays until Phase 6), all golden diffs approved
- **Max feedback latency:** 30 seconds (fast set)

---

## Per-Task Verification Map

Execution order (strictly sequential, one plan per wave): 02-01 RULE-08 → 02-02 RULE-06 → 02-03 RULE-03 → 02-04 RULE-07 → 02-05 RULE-01 → 02-06 RULE-02 → 02-07 RULE-05 → 02-08 RULE-04. RULE-03 runs before RULE-07 (deviation from the research order): RULE-07 drops the `[-100000, -15]` sentinel and makes `_tier_lookup` raise below 0, which needs RULE-03's negative penalty branch first.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 02-01 | 1 | RULE-08 | T-02-04 | Dumps stay in gitignored `golden-diff/` | tool + suite | `uv run pytest -q` (+ meta.json count check) | ❌ W0 (tool created in task) | ⬜ pending |
| 02-01-02 | 02-01 | 1 | RULE-08 | T-02-02, T-02-03 | Leftover E-target keys warn (`schema.removed_key`), never change results | unit (TDD) | `uv run pytest -q -k "not test_golden_sample_matches"` | ❌ W0 `tests/test_e_target_removed.py` (RED in task) | ⬜ pending |
| 02-01-03 | 02-01 | 1 | RULE-08 | T-02-01, T-02-02 | All-combination diff with hard expectations before `--update-golden` | unit + slow digests | `uv run pytest -q && uv run pytest -m slow -q` | ✅ goldens exist (regenerated) | ⬜ pending |
| 02-01-04 | 02-01 | 1 | RULE-08 | T-02-01 | Human review before commit | checkpoint | `uv run pytest -q` | ✅ | ⬜ pending |
| 02-02-01 | 02-02 | 2 | RULE-06 | T-02-07 | RoS from own spend in rules/store/report/dump/analyze; event invariance | unit + property (TDD) | `uv run pytest -q -k "not test_golden_sample_matches"` | ❌ W0 `tests/test_ros_ledger.py` (RED in task) | ⬜ pending |
| 02-02-02 | 02-02 | 2 | RULE-06 | T-02-08 | Budget total and digests unchanged | unit + slow digests | `uv run pytest -q && uv run pytest -m slow -q tests/test_digest.py tests/test_kernel_conformance.py` | ✅ | ⬜ pending |
| 02-02-03 | 02-02 | 2 | RULE-06 | T-02-06 | Human review before commit | checkpoint | `uv run pytest -q` | ✅ | ⬜ pending |
| 02-03-01 | 02-03 | 3 | RULE-03 | T-02-11, T-02-12, T-02-13, T-02-14 | Validator rejects bad penalty config; k€ step explicit; lookup rows equal sim | unit (TDD) | `uv run pytest tests/test_budget_review.py tests/test_kernel_conformance.py tests/test_rules_semantics.py tests/test_enumeration.py tests/test_validate.py tests/test_single_definition.py -q` | ❌ W0 `tests/test_budget_review.py` (RED in task) | ⬜ pending |
| 02-03-02 | 02-03 | 3 | RULE-03 | T-02-10 | Only over-budget KZ changes; in-budget untouched | unit + slow digests | `uv run pytest -q && uv run pytest -m slow -q` | ✅ | ⬜ pending |
| 02-03-03 | 02-03 | 3 | RULE-03 | T-02-10 | Human review before commit | checkpoint | `uv run pytest -q` | ✅ | ⬜ pending |
| 02-04-01 | 02-04 | 4 | RULE-07 | T-02-15, T-02-16, T-02-17 | Generated boundary text parses back to the sim; lookup below domain raises | unit (TDD) | `uv run pytest -q` | ❌ W0 `tests/test_budget_review_text.py` (RED in task) | ⬜ pending |
| 02-04-02 | 02-04 | 4 | RULE-07 | — | N/A (docs) | doc lint | `uv run pytest tests/test_budget_review_text.py -q && uv run pytest -q` | ✅ | ⬜ pending |
| 02-05-01 | 02-05 | 5 | RULE-01 | T-02-19, T-02-21 | Misplaced/duplicate Kurswechsel rejected; no refund via swap credit | unit (TDD) | `uv run pytest -q -k "not test_golden_sample_matches"` | ❌ W0 `tests/test_kurswechsel.py` (RED in task) | ⬜ pending |
| 02-05-02 | 02-05 | 5 | RULE-01 | T-02-20 | Static results labelled as reference (D-24); vocabulary lint | unit + lint + slow digests | `uv run pytest -q && uv run pytest -m slow -q tests/test_digest.py tests/test_kernel_conformance.py` | ✅ | ⬜ pending |
| 02-05-03 | 02-05 | 5 | RULE-01 | T-02-18 | Human review before commit | checkpoint | `uv run pytest -q` | ✅ | ⬜ pending |
| 02-06-01 | 02-06 | 6 | RULE-02 | T-02-22 | Malformed paths raise `PathError` with reason | unit + conformance (TDD) | `uv run pytest tests/test_paths.py -q && uv run pytest -q` | ❌ W0 `tests/test_paths.py` (RED in task) | ⬜ pending |
| 02-06-02 | 02-06 | 6 | RULE-02 | T-02-23, T-02-24 | Table results equal `evaluate_path`; bounded runtime | unit (mini) + slow (real low tier) | `uv run pytest tests/test_swap_layer.py -q && uv run pytest -q && uv run pytest -m slow -q tests/test_swap_layer.py` | ❌ W0 `tests/test_swap_layer.py` (RED in task) | ⬜ pending |
| 02-06-03 | 02-06 | 6 | RULE-02 | — | N/A (docs) | doc lint | `uv run pytest tests/test_paths.py -q && uv run pytest -q` | ✅ | ⬜ pending |
| 02-07-01 | 02-07 | 7 | RULE-05 | T-02-26 | Budget cut in the last wave warns | unit (TDD) | `uv run pytest tests/test_sparprogramm.py tests/test_validate.py -q && uv run pytest -q` | ❌ W0 `tests/test_sparprogramm.py` (RED in task) | ⬜ pending |
| 02-07-02 | 02-07 | 7 | RULE-05 | T-02-27 | N/A (docs) | doc lint | `uv run pytest tests/test_sparprogramm.py -q && uv run pytest -q` | ✅ | ⬜ pending |
| 02-08-01 | 02-08 | 8 | RULE-04 | T-02-29, T-02-30 | Clamp-aware gate equals brute force; names the offending plan | unit (TDD) | `uv run pytest tests/test_overspend_gate.py tests/test_single_definition.py -q && uv run pytest -q` | ❌ W0 `tests/test_overspend_gate.py` (RED in task) | ⬜ pending |
| 02-08-02 | 02-08 | 8 | RULE-04 | T-02-31 | Gate per tier passes at config X | slow integration + CLI | `uv run pytest -q && uv run pytest -m slow -q tests/test_overspend_gate.py && uv run planspiel gate` | ❌ W0 `tests/golden/gate_<tier>.json` (created via `--update-golden`) | ⬜ pending |
| 02-08-03 | 02-08 | 8 | RULE-04 | T-02-28 | Human review before commit | checkpoint | `uv run pytest -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] New test modules per requirement, each created RED in the first TDD task of its plan: `test_e_target_removed.py` (02-01), `test_ros_ledger.py` (02-02), `test_budget_review.py` (02-03), `test_budget_review_text.py` (02-04), `test_kurswechsel.py` (02-05), `test_paths.py` + `test_swap_layer.py` (02-06), `test_sparprogramm.py` (02-07), `test_overspend_gate.py` (02-08)
- [ ] `tests/fixtures/mini_config.json` migrated step by step with the real config: no `e_targets`/`kz_bonus`/`kz_malus` (02-01), `overspend_penalty` (02-03), tier list from 0 (02-04), `kurswechsel` type (02-05)
- [ ] Support updates for removed fields (`tests/support/digest.py`, `harness.py`, `golden_cases.py`) in 02-01; `harness.compact_from_path` in 02-06
- [ ] Golden diff tool `.planning/phases/02-rule-changes/tools/golden_diff.py` (02-01), reused by 02-02, 02-03, 02-05
- [ ] Gate golden bootstrap (`tests/golden/gate_<tier>.json` via `--update-golden`) in 02-08
- [ ] Framework install: none needed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Reviewed golden/snapshot diffs (KZ/RoS changed counts, best in- vs over-budget before/after, in-budget count unchanged) | RULE-08 (02-01), RULE-06 (02-02), RULE-03 (02-03), RULE-01 (02-05, text only), RULE-04 (02-08, new gate goldens) | Snapshot changes need human approval (D-20, Phase 1 01-06 precedent) | Executor stops at a human-verify checkpoint with the all-combination diff report per tier (`02-0N-GOLDEN-DIFF.md`, gate: `02-08-GATE-REPORT.md`); goldens regenerated only via `--update-golden` after approval |
| German README rule text reads unambiguously (Levelwechsel vs Maßnahmentausch, Kurswechsel, penalty, Budget Review) | RULE-01, RULE-03, RULE-07 | Wording clarity is a human judgement | Read the rewritten README sections against CONTEXT D-01..D-28 |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (each new test file is created RED inside the task that needs it)
- [x] No watch-mode flags
- [x] Feedback latency < 30s (per-commit `uv run pytest -q`; slow checks only at golden/gate tasks)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
