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

| Req | Plan | Behavior | Test Type | Automated Command | File Exists | Status |
|-----|------|----------|-----------|-------------------|-------------|--------|
| BAL-01 | 06-01 | required-X closure on synthetic columns; move-path gate equals brute force on mini config; raw and capped minimum X; calibrated X = max + 1; configured-config path gate per tier | unit + brute force; slow | `uv run pytest tests/test_overspend_gate.py tests/test_gate_paths.py tests/test_candidate_support.py -q` | gate ✅ / paths ❌ W0 (06-01) | ⬜ pending |
| BAL-02 | 06-02 | `hand_calc_level` severity parameter; final-index weight rule; 17/7 fails in error mode, one-decimal variant passes | unit; slow | `uv run pytest tests/test_hand_calc_level.py tests/test_validate.py -q` | ❌ W0 (06-02) | ⬜ pending |
| BAL-03 | 06-03 | `rules.final_index` = `weight_kz·KZ + k·RoS₂`; k recommendation from pooled IQR; 0.85 filter removed; answer-key golden compared strictly except the final-index row (TUNING_TARGET until the 06-10 re-pin) | unit; slow | `uv run pytest tests/test_index_weights.py tests/test_final_index_config.py tests/test_enumeration.py -q` | partly ✅ extend / index_weights ❌ W0 (06-03) | ⬜ pending |
| BAL-04 | 06-08 | per-tier report: in-budget top-K, Pareto, unfiltered optima, percentile blocks; consolidated report with `--config`, `--baseline-config` | unit + CLI | `uv run pytest tests/test_balance_report.py tests/test_wrappers.py -q` | ❌ W0 (06-08) | ⬜ pending |
| BAL-05 | 06-10 | goldens re-pinned (incl. gate_paths); `print --check` exit 0; print≡sim equivalence; booklet row cap; no approximation sign | fast + slow + pdf | `uv run pytest -q && uv run pytest -m slow -q && uv run pytest -m pdf -q && uv run planspiel print --check` | ✅ existing | ⬜ pending |
| BAL-06 | 06-04 | dominance, band near-mandatory, overpowered drop, decision-point effects | unit; slow | `uv run pytest tests/test_choices.py -q` | ❌ W0 (06-04) | ⬜ pending |
| BAL-07 | 06-07 | clue mapping checks; `reference_strategies` validator + legality; quartile placement; clue-derived good strategy | unit; slow | `uv run pytest tests/test_clues_mapping.py tests/test_reference_strategies.py tests/test_strategies.py -q` | ❌ W0 (06-07) | ⬜ pending |
| BAL-08 | 06-05 | median − start KZ on both layers; comeback after wave 1 | unit; slow | `uv run pytest tests/test_rewarding.py -q` | ❌ W0 (06-05) | ⬜ pending |
| BAL-09 | 06-06 | tier corridor, D-11 band, IQR range, p5–p95 width, median bound | unit; slow | `uv run pytest tests/test_spread.py -q` | ❌ W0 (06-06) | ⬜ pending |
| BAL-01/02/03/06/07/08/09 targets | 06-09 | candidate passes every balance check as a hard check | slow | `uv run pytest -m balance --runxfail --planspiel-config .planning/phases/06-rebalance/candidate_config.json --planspiel-content-dir .planning/phases/06-rebalance/candidate_content -q` | built by 06-01 … 06-08 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Configured-config variants of the check plans are marked `slow` + `balance`; those that fail on today's `simulation_config.json` (the tuning target) additionally carry the shared xfail marker `TUNING_TARGET` from `tests/support/candidate.py` (one approach for all plans). `uv run pytest -m slow` stays green; the tuning plan runs them as hard checks with `--runxfail --planspiel-config <cand> --planspiel-content-dir <dir>`; 06-10 removes the marker after adoption. Fast variants run on `tests/fixtures/mini_config.json` and must be green.

---

## Wave 0 Requirements

- [ ] `tests/test_gate_paths.py`, `tests/test_candidate_support.py` (06-01; gate_paths goldens pinned in 06-10)
- [ ] `tests/test_hand_calc_level.py` (06-02)
- [ ] `tests/test_index_weights.py` (06-03)
- [ ] `tests/test_choices.py` (06-04), `tests/test_rewarding.py` (06-05), `tests/test_spread.py` (06-06)
- [ ] `tests/test_clues_mapping.py`, `tests/test_reference_strategies.py`, `tests/test_strategies.py` (06-07)
- [ ] `tests/test_balance_report.py` (06-08)
- [ ] mini-fixture additions: `reference_strategies` in `mini_config.json`, clue→measure keys in `mini_content/clues.toml` (06-07)
- [ ] candidate-config mechanism: pytest options `--planspiel-config` / `--planspiel-content-dir`, marker `balance`, `TUNING_TARGET` (06-01)

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
