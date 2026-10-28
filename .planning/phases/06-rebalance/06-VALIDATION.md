---
phase: 6
slug: rebalance
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-10-28
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (markers `slow`, `pdf`; `addopts = -m 'not slow and not pdf' --strict-markers`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `uv run pytest -q` |
| **Full suite command** | `uv run pytest -q && uv run pytest -m slow -q && uv run pytest -m pdf -q` |
| **Estimated runtime** | ~125 s fast; slow suite several minutes per tier (real-kernel enumeration, move-path gate) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest -q` plus the touched test file
- **After every plan wave:** Run the fast suite; during tuning also the candidate-config report (static layer, ~1 min)
- **Tuning checkpoint (before D-04):** `uv run pytest -m slow -q` against the candidate config, `uv run planspiel validate --config <cand>`, `uv run planspiel gate --config <cand>`, `uv run planspiel tausch --config <cand>`
- **Before `/gsd-verify-work`:** fast, `-m slow` and `-m pdf` suites green; `uv run planspiel print --check` exits 0
- **Max feedback latency:** 125 seconds (fast suite)

---

## Per-Task Verification Map

Filled in by the planner/executor per task. Requirement → test map from research:

| Req | Behavior | Test Type | Automated Command | File Exists | Status |
|-----|----------|-----------|-------------------|-------------|--------|
| BAL-01 | required-X closure on synthetic columns; move-path gate equals brute force on mini config; calibrated X = max + 1; real-config path gate per tier | unit + brute force; slow | `uv run pytest tests/test_overspend_gate.py tests/test_gate_paths.py -q` | gate ✅ / paths ❌ W0 | ⬜ pending |
| BAL-02 | `hand_calc.*` severity parameter; `planspiel validate` exit codes; 17/7 candidate fails, fixed passes | unit | `uv run pytest tests/test_validate.py -q` | ✅ extend | ⬜ pending |
| BAL-03 | `rules.final_index` = `weight_kz·KZ + k·RoS` with integer k from config; 0.85 filter removed or documented out | unit | `uv run pytest tests/test_final_index_config.py tests/test_enumeration.py -q` | ✅ extend | ⬜ pending |
| BAL-04 | per-tier report: in-budget top-K, Pareto, unfiltered optima, percentile blocks; `balance` accepts `--config` | unit + CLI | `uv run pytest tests/test_balance_report.py -q` | ❌ W0 | ⬜ pending |
| BAL-05 | goldens re-pinned; `print --check` exit 0; print≡sim equivalence; booklet row cap | fast + pdf | `uv run pytest -q && uv run pytest -m pdf -q && uv run planspiel print --check` | ✅ existing | ⬜ pending |
| BAL-06 | dominance, band near-mandatory, overpowered drop, decision-point effect | unit; slow | `uv run pytest tests/test_balance_metrics.py -q` | ❌ W0 | ⬜ pending |
| BAL-07 | `reference_strategies` validator + legality; quartile placement; clue-derived good strategy | unit; slow | `uv run pytest tests/test_reference_strategies.py tests/test_clues_mapping.py -q` | ❌ W0 | ⬜ pending |
| BAL-08 | median − start KZ on both layers; comeback after wave 1 | unit; slow | `uv run pytest tests/test_balance_metrics.py -q` | ❌ W0 | ⬜ pending |
| BAL-09 | tier corridor, IQR range, p5–p95 width, best-in-budget band | unit; slow | `uv run pytest tests/test_balance_metrics.py -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Real-config variants of the Wave-1 checks are expected to fail on today's `simulation_config.json` (they are the tuning target). They are marked `slow` and kept out of the green gate until BAL-05 adopts the tuned config; fast variants run on `tests/fixtures/mini_config.json` and must be green.

---

## Wave 0 Requirements

- [ ] `tests/test_gate_paths.py` (+ goldens if pinned)
- [ ] `tests/test_balance_metrics.py`
- [ ] `tests/test_balance_report.py`
- [ ] `tests/test_reference_strategies.py`
- [ ] `tests/test_clues_mapping.py`
- [ ] mini-fixture additions: `reference_strategies` in `mini_config.json`, clue→measure keys in `mini_content/clues.toml`
- [ ] shared way to point slow real-config checks at a candidate config (`--config` CLI + test option/env), since `tests.support.CONFIG_PATH` is fixed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Tuned values, X, k, thresholds, reference strategies and clue edits approved | BAL-01..09 (D-04) | Design judgment; single human review checkpoint | Review the consolidated per-tier report and the diff of candidate vs current config; approve or request changes |
| Printed material readable with new numbers | BAL-05 | Visual layout | Open regenerated PDFs in `final_documents/generated/`, check worksheets, penalty table and RoS page |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 125s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
