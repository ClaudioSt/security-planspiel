---
phase: 5
slug: player-facilitator-print-material
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-10-23
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `05-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (dev group); pypdf 6.19.0 for PDF text |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`addopts = -m 'not slow and not pdf' --strict-markers`) |
| **Quick run command** | `uv run pytest tests/test_<plan module>.py -x -q` |
| **Full suite command** | `uv run pytest -q` and `uv run pytest -m pdf -q` (plus `uv run pytest -m slow tests/test_digest.py` after D-23) |
| **Estimated runtime** | ~70 s fast suite; pdf suite a few minutes |

---

## Sampling Rate

- **After every task commit:** the plan's own quick test files plus `uv run planspiel texts`
- **After every plan wave:** `uv run pytest -q`, `uv run planspiel validate`, `uv run planspiel texts`, `uv run planspiel clues`; `uv run pytest -m pdf -q` for plans that add a document
- **Before `/gsd-verify-work`:** fast suite + `-m pdf` + `-m slow tests/test_digest.py` + clean `uv run planspiel print` + `uv run planspiel print --check` exit 0
- **Max feedback latency:** ~70 seconds (fast suite)

---

## Per-Requirement Verification Map

Plan IDs are filled in by the planner (one plan per requirement).

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| VEIL-02 | every print job has an audience; unknown prefix raises | unit | `uv run pytest tests/test_veil_audience.py -x` | ❌ W0 | ⬜ pending |
| VEIL-02 | layer-1 scan catches injected names, weight triples, revealed strings | unit | `uv run pytest tests/test_veil_scan.py -x` | ❌ W0 | ⬜ pending |
| VEIL-02 | pre-wave builders never touch revealed or wave internals | unit (AST) | `uv run pytest tests/test_veil_models.py -x` | ❌ W0 | ⬜ pending |
| VEIL-02 | built PDFs: text, metadata, file names clean; revealed N names no other attack | pdf | `uv run pytest -m pdf tests/test_veil_pdf.py` | ❌ W0 | ⬜ pending |
| VEIL-04 | measure-card model exposes CIA/costs/dependencies only; deck has no weights or bonus links; worksheets carry weights and bonus table | unit + pdf | planner defines (e.g. `tests/test_veil_cards.py`) | ❌ W0 | ⬜ pending |
| PRINT-05 | 31 cards, values equal `rules`, dependency icons | unit | `uv run pytest tests/test_cards_model.py -x` | ❌ W0 | ⬜ pending |
| PRINT-05 | sheets, stamp, fit, no missing glyphs or overfull boxes | pdf | `uv run pytest -m pdf tests/test_cards_pdf.py tests/test_print_documents_pdf.py` | ❌ W0 | ⬜ pending |
| PRINT-06 | every effect line equals `rules.evaluate_event` / `budget_review_delta` | unit | `uv run pytest tests/test_event_text.py -x` | ❌ W0 | ⬜ pending |
| PRINT-06 | 8 cards on 2 sheets | unit + pdf | `uv run pytest tests/test_event_cards.py -x` | ❌ W0 | ⬜ pending |
| PRINT-07 | budget and RoS sheets from config; no event-penalty row | unit + pdf | `uv run pytest tests/test_booklet_model.py -x` | ❌ W0 | ⬜ pending |
| PRINT-08 | row order, own vs external rows, window blocks, swap credit; one page | unit + pdf | `uv run pytest tests/test_tracking_model.py -x` | ❌ W0 | ⬜ pending |
| PRINT-09 | one page, no values or attack names, vocabulary equals worksheet | unit + pdf | `uv run pytest tests/test_wave_page.py -x` | ❌ W0 | ⬜ pending |
| PRINT-12 | four story docs from `[story.*]`; every clue quote in the PDF; images embedded | unit + pdf | `uv run pytest tests/test_story_model.py -x` | ❌ W0 | ⬜ pending |
| FLOW-01 | practice config ignored by enumeration, gate, digests | unit | `uv run pytest tests/test_practice_config.py -x` | ❌ W0 | ⬜ pending |
| FLOW-01 | golden: printed numbers equal rules and replay | unit | `uv run pytest tests/test_welle0_golden.py -x` | ❌ W0 | ⬜ pending |
| PRINT-10 | final-index weights from config, outputs unchanged | unit + slow | `uv run pytest tests/test_final_index_config.py -x` | ❌ W0 | ⬜ pending |
| PRINT-10 | reference paths legal; `path_trace` equals `evaluate_path`; master values equal rules | unit + pdf | `uv run pytest tests/test_reference_plans.py tests/test_path_trace.py tests/test_master_model.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/support/pdf_text.py` — shared PDF text helpers (squash, pages, fragments)
- [ ] Prefix-aware job assertions in `tests/test_print_render.py` and `tests/test_print_model.py`
- [ ] `tests/test_print_documents_pdf.py` — generic log hygiene over all jobs
- [ ] Mini fixtures extended per plan for new text keys and config blocks

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Card sheet cut, margins, legibility | PRINT-05, PRINT-06 | physical print | Print one card sheet and cut it; check text size and safe strip |
| Team booklet usable in calculation order | PRINT-07, PRINT-08, PRINT-09 | needs a human run-through | Play one wave on the printed sheets without a whiteboard |
| Practice story contains no hint at real attacks | FLOW-01 | content judgment | User reviews the draft at the D-16 checkpoint |
| Reference paths are typical | PRINT-10 | judgment | User approves the paths at the D-18/D-22 checkpoint |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 70s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
