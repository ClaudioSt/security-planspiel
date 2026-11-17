---
phase: 3
slug: content-source-veiling
status: draft
nyquist_compliant: true
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

Filled by the planner (2026-10-10). Every task writes its tests RED first, so the Wave 0 files are created by the first task that needs them.

| Task | Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|------|-------------|----------|-----------|-------------------|-------------|--------|
| 03-01 T1 | PRINT-02 | `texte.toml` loads as UTF-8 (umlauts, typographic quotes, CRLF-safe) | unit | `uv run pytest tests/test_texts_loader.py -q` | ❌ W0 (T1) | ⬜ pending |
| 03-01 T1 | PRINT-02 | coverage fails on missing and orphaned keys (mini fixture + mutations); CLI `planspiel texts` exits 0/1 | unit + mutation | `uv run pytest tests/test_texts_coverage.py -q` | ❌ W0 (T1) | ⬜ pending |
| 03-01 T1 | PRINT-02 | digit lint: digits fail, allowlisted tokens pass, stale entry fails, `story` exempt, number words pass; story mechanics lint (D-15) | unit | `uv run pytest tests/test_texts_digits.py -q` | ❌ W0 (T1) | ⬜ pending |
| 03-01 T2 | PRINT-02 | 1:1 migration fidelity (both MEASURE_META copies, bonus reasons, rule texts, story spot checks); real content passes `check_texts`; pinned allowlist | unit | `uv run pytest tests/test_texts_migration.py tests/test_config_text.py -q` | ❌ W0 (T2) | ⬜ pending |
| 03-01 T3 | PRINT-02 (SC5) | every `final_documents/` file in `content/INVENTORY.md` with a valid disposition; asset copies byte-identical | unit | `uv run pytest tests/test_inventory.py -q` | ❌ W0 (T3) | ⬜ pending |
| 03-01 T4 | PRINT-02 | config has no prose; validator error `schema.prose_in_config`; `flat_budget` label generated; removed numbers map to params | unit | `uv run pytest tests/test_config_prose_removed.py tests/test_validate.py -q` | ❌ W0 (T4) | ⬜ pending |
| 03-01 T5 | PRINT-02 | golden change is text-only; digests and gate goldens unchanged | script + slow | `uv run python .planning/phases/03-content-source-veiling/tools/golden_text_diff.py` and `uv run pytest -m slow tests/test_digest.py -q` | ❌ W0 (T5) | ⬜ pending |
| 03-01 T6 | PRINT-02 | goldens rewritten only after user decision (D-08, D-25) | decision + regression | `uv run pytest -q` | ✅ | ⬜ pending |
| 03-02 T1 | VEIL-01 | `Angriff N` / `Angriff N: <Name>` titles from wave position, reorder; pre-attack view cannot reach revealed name, id or bonus reason | unit | `uv run pytest tests/test_texts_views.py tests/test_texts_coverage.py -q` | ❌ W0 (T1) | ⬜ pending |
| 03-02 T2 | VEIL-01 | giveaway matcher must-pass/must-fail table, D-13b pin; veiled keys and event texts clean | unit | `uv run pytest tests/test_texts_giveaway.py -q` | ❌ W0 (T2) | ⬜ pending |
| 03-02 T3 | VEIL-01 | revealed texts reviewed before commit (D-13d) | decision + regression | `uv run pytest -q && uv run planspiel texts` | ✅ | ⬜ pending |
| 03-03 T1 | VEIL-03 | clue check: ≥2 clues per attack, ≥2 documents, verbatim, pre-wave source, mutations; `planspiel clues` exits 0/1 | unit + integration | `uv run pytest tests/test_clues.py -q` | ❌ W0 (T1) | ⬜ pending |
| 03-03 T2 | VEIL-03 | story texts pass the story profile (D-20 exceptions), RED first; real clue matrix passes; leak test covers story | unit | `uv run pytest tests/test_story_veil.py tests/test_texts_views.py -q` | ❌ W0 (T2) | ⬜ pending |
| 03-03 T3 | VEIL-03 | rewrites and matrix reviewed before commit (D-13d) | decision + regression | `uv run pytest -q && uv run planspiel clues` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_texts_loader.py`, `test_texts_coverage.py`, `test_texts_digits.py`, `test_config_prose_removed.py`, `test_texts_migration.py`, `test_inventory.py` — PRINT-02
- [ ] `tests/test_texts_views.py`, `test_texts_giveaway.py` — VEIL-01
- [ ] `tests/test_clues.py`, `tests/test_story_veil.py` — VEIL-03
- [ ] `tests/fixtures/mini_content/` (`texte.toml`, `digit_allowlist.toml`, `giveaway_terms.toml`, `clues.toml`) — hand-verifiable fixture content dir mirroring `content/`
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
