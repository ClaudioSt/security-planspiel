---
phase: 2
slug: rule-changes
status: draft
nyquist_compliant: false
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
| **Estimated runtime** | ~15 s quick; ~21 min slow today, +2–3 min for the static gate (path-layer gate deferred to Phase 6, D-25) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest -q`
- **After every plan wave:** Run `uv run pytest -q` plus the relevant slow check for the changed layer (`uv run pytest -m slow <affected file> -q`)
- **Before `/gsd-verify-work`:** `uv run pytest -m slow` and `uv run pytest -q` green, `uv run planspiel validate` 0 errors (known 17/7 warning stays until Phase 6), all golden diffs approved
- **Max feedback latency:** 30 seconds (fast set)

---

## Per-Task Verification Map

Filled per task by the planner; requirement-level map from 02-RESEARCH.md:

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | RULE-01 plan | TBD | RULE-01 | — | N/A | unit + lint | `uv run pytest tests/test_kurswechsel.py -q` | ❌ W0 | ⬜ pending |
| TBD | RULE-02 plan | TBD | RULE-02 | — | N/A | unit + conformance | `uv run pytest tests/test_paths.py -q` | ❌ W0 | ⬜ pending |
| TBD | RULE-03 plan | TBD | RULE-03 | — | N/A | unit | `uv run pytest tests/test_budget_review.py -q` | ❌ W0 | ⬜ pending |
| TBD | RULE-04 plan | TBD | RULE-04 | — | N/A | unit (fast) + integration (slow) | `uv run pytest tests/test_overspend_gate.py -q`; `uv run pytest -m slow tests/test_overspend_gate.py -q` | ❌ W0 | ⬜ pending |
| TBD | RULE-05 plan | TBD | RULE-05 | — | N/A | unit (mini) + slow sample | `uv run pytest tests/test_sparprogramm.py -q` | ❌ W0 | ⬜ pending |
| TBD | RULE-06 plan | TBD | RULE-06 | — | N/A | unit + property | `uv run pytest tests/test_ros_ledger.py -q` | ❌ W0 | ⬜ pending |
| TBD | RULE-07 plan | TBD | RULE-07 | — | N/A | unit | `uv run pytest tests/test_budget_review_text.py -q` | ❌ W0 | ⬜ pending |
| TBD | RULE-08 plan | TBD | RULE-08 | — | N/A | unit + slow digests | `uv run pytest tests/test_e_target_removed.py -q`; `uv run pytest -m slow tests/test_digest.py -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] New test modules per requirement (RED first; names are suggestions, may merge into existing modules)
- [ ] `tests/fixtures/mini_config.json` migrated to the new schema (no `e_targets`/`kz_bonus`/`kz_malus`, `kurswechsel` type, tier list from 0, overspend penalty)
- [ ] Support updates for removed fields (`tests/support/digest.py`, `harness.py`, `golden_cases.py`)
- [ ] Gate golden bootstrap (`tests/golden/gate_<tier>.json` via `--update-golden`)
- [ ] Framework install: none needed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Reviewed golden/snapshot diffs (KZ changed counts, best in- vs over-budget before/after, in-budget count unchanged) | RULE-08, RULE-06, RULE-03 (any plan that changes goldens) | Snapshot changes need human approval (D-20, Phase 1 01-06 precedent) | Executor stops at a human-verify checkpoint with the all-combination diff report per tier; goldens regenerated only via `--update-golden` after approval |
| German README rule text reads unambiguously (Levelwechsel vs Maßnahmentausch, Kurswechsel, penalty, Budget Review) | RULE-01, RULE-03, RULE-07 | Wording clarity is a human judgement | Read the rewritten README sections against CONTEXT D-01..D-28 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
