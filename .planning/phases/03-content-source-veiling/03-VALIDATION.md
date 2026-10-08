---
phase: 3
slug: content-source-veiling
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-10-08
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | `pyproject.toml` (`testpaths = ["tests"]`, `addopts = "-m 'not slow' --strict-markers"`, marker `slow`) |
| **Quick run command** | `uv run pytest -q` |
| **Full suite command** | `uv run pytest -q && uv run pytest -m slow tests/test_digest.py -q` |
| **Extra gates** | `uv run planspiel validate` (0 errors), `uv run planspiel texts` (new), `uv run planspiel clues` (new, after VEIL-03) |
| **Estimated runtime** | ~30 seconds quick; slow digests several minutes (full slow suite ~21 min, not needed per task) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest -q` plus the task's own test file
- **After every plan wave:** Run `uv run pytest -q`, `uv run planspiel validate`, `uv run planspiel texts`
- **Before `/gsd-verify-work`:** quick suite green, `uv run pytest -m slow tests/test_digest.py -q` green without `--update-golden`, all user checkpoints done
- **Max feedback latency:** 60 seconds (quick suite)

---

## Per-Task Verification Map

Filled by the planner per task; requirement-level map from research:

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| PRINT-02 | `texte.toml` loads as UTF-8 (umlauts, typographic quotes, CRLF-safe) | unit | `uv run pytest tests/test_texts_loader.py -q` | ❌ W0 | ⬜ pending |
| PRINT-02 | coverage fails on missing and orphaned keys; real file passes | unit + mutation | `uv run pytest tests/test_texts_coverage.py -q` | ❌ W0 | ⬜ pending |
| PRINT-02 | digit lint: digits fail, allowlisted tokens pass, stale entry fails, `story` exempt, number words pass | unit | `uv run pytest tests/test_texts_digits.py -q` | ❌ W0 | ⬜ pending |
| PRINT-02 | config has no prose; validator error `schema.prose_in_config`; `flat_budget` label generated; removed numbers map to params | unit | `uv run pytest tests/test_config_prose_removed.py -q` | ❌ W0 | ⬜ pending |
| PRINT-02 | 1:1 migration fidelity (MEASURE_META, pre-strip config) | unit | `uv run pytest tests/test_texts_migration.py -q` | ❌ W0 | ⬜ pending |
| PRINT-02 | golden change is text-only; digests unchanged | script + slow | `uv run python .planning/phases/03-content-source-veiling/tools/golden_text_diff.py` and `uv run pytest -m slow tests/test_digest.py -q` | ❌ W0 | ⬜ pending |
| PRINT-02 (SC5) | every `final_documents/` file in the inventory with a valid disposition | unit | `uv run pytest tests/test_inventory.py -q` | ❌ W0 | ⬜ pending |
| VEIL-01 | `Angriff N` / `Angriff N: <Name>` titles from wave position; no digit in TOML | unit | `uv run pytest tests/test_texts_views.py -q` | ❌ W0 | ⬜ pending |
| VEIL-01 | pre-attack view cannot reach revealed name, id or bonus reason | unit | `uv run pytest tests/test_texts_views.py -q` | ❌ W0 | ⬜ pending |
| VEIL-01 | giveaway matcher must-pass/must-fail table; veiled keys and event narratives clean | unit | `uv run pytest tests/test_texts_giveaway.py -q` | ❌ W0 | ⬜ pending |
| VEIL-03 | story texts pass the story profile (D-20 exceptions), RED first | unit | `uv run pytest tests/test_texts_giveaway.py -k story -q` | ❌ W0 | ⬜ pending |
| VEIL-03 | clue check: ≥2 clues per attack, ≥2 documents, verbatim, pre-wave source, mutations | unit | `uv run pytest tests/test_clues.py -q` | ❌ W0 | ⬜ pending |
| VEIL-03 | `planspiel clues` prints matrix, exits 0/1 | integration | `uv run pytest tests/test_clues.py -k cli -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_texts_loader.py`, `test_texts_coverage.py`, `test_texts_digits.py`, `test_config_prose_removed.py`, `test_texts_migration.py`, `test_inventory.py` — PRINT-02
- [ ] `tests/test_texts_views.py`, `test_texts_giveaway.py` — VEIL-01
- [ ] `tests/test_clues.py` (+ story cases in `test_texts_giveaway.py`) — VEIL-03
- [ ] `tests/fixtures/mini_texte.toml`, `tests/fixtures/mini_clues.toml` — hand-verifiable fixtures
- [ ] `.planning/phases/03-content-source-veiling/tools/golden_text_diff.py` — text-only golden classifier

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Golden diff is text-only and the digit allowlist is acceptable (D-08, D-25) | PRINT-02 | User approval required before `--update-golden` | Review classifier output and allowlist at checkpoint |
| Revealed attack texts read well (D-13d) | VEIL-01 | Editorial review | User reviews drafted texts at checkpoint |
| Veiled story rewrites keep clue value (D-13d, D-16) | VEIL-03 | Editorial judgement | User reviews rewrites and clue matrix at checkpoint |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
