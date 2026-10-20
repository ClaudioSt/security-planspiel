---
phase: 4
slug: print-pipeline-attack-worksheets
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-10-20
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (existing); markers `slow` (existing) and new `pdf` |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]`: `addopts = -m 'not slow and not pdf' --strict-markers`, `pdf` marker registered |
| **Quick run command** | `uv run pytest tests/test_print_*.py tests/test_worksheet_equivalence.py -x -q` |
| **Full suite command** | `uv run pytest` (fast), then `uv run pytest -m slow` and `uv run pytest -m pdf` |
| **Estimated runtime** | quick ~10 s; fast suite ~60 s; `-m pdf` ~30 s; slow replay ~3 × 48 s |

---

## Sampling Rate

- **After every task commit:** Run the quick run command (no TeX needed)
- **After every plan wave:** Run `uv run pytest`, `uv run planspiel validate`, `uv run planspiel texts`
- **Before `/gsd-verify-work`:** fast suite + `uv run pytest -m slow tests/test_worksheet_equivalence_full.py` + `uv run pytest -m pdf` + `uv run planspiel print` + `uv run planspiel print --check` all green; one printed sheet reviewed by a human
- **Max feedback latency:** 60 seconds (fast suite)

---

## Per-Task Verification Map

Filled in by the planner per task; the requirement-level map is:

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| PRINT-01 | Preflight reports missing packages (`kpsewhich --miktex-disable-installer`) | unit | `uv run pytest tests/test_print_preflight.py -x` | ❌ W0 | ⬜ pending |
| PRINT-01 | Pass loop stops on stable aux; timeout raises; missing-package log surfaced | unit (fake runner) | `uv run pytest tests/test_print_driver.py -x` | ❌ W0 | ⬜ pending |
| PRINT-01 | Two builds byte-identical; missing package fails fast; runaway doc killed by timeout | integration | `uv run pytest -m pdf tests/test_print_smoke.py` | ❌ W0 | ⬜ pending |
| PRINT-11 | Content hash ignores stamp, CRLF-insensitive, changes on .tex/sty/asset change | unit | `uv run pytest tests/test_print_stamp.py -x` | ❌ W0 | ⬜ pending |
| PRINT-11 | UTC commit date of data inputs; "+lokal" scoped to build inputs | unit (temp git) | `uv run pytest tests/test_print_stamp.py -x` | ❌ W0 | ⬜ pending |
| PRINT-11 | `--check` fresh → 0, stale → 1 listing docs, no TeX invoked | unit | `uv run pytest tests/test_print_stamp.py -x` | ❌ W0 | ⬜ pending |
| PRINT-11 | Stamp on every page of every PDF; `.fls` inputs ⊆ hashed set | integration | `uv run pytest -m pdf tests/test_print_worksheets_pdf.py` | ❌ W0 | ⬜ pending |
| PRINT-03 | Print model numbers derived from config; D-06/D-08/D-09 guards | unit | `uv run pytest tests/test_print_model.py -x` | ❌ W0 | ⬜ pending |
| PRINT-03 | StrictUndefined render, escaping, SC2 (threshold change changes print) | unit | `uv run pytest tests/test_print_render.py -x` | ❌ W0 | ⬜ pending |
| PRINT-03 | New wording digit-free | lint | `uv run planspiel texts` | ✅ | ⬜ pending |
| PRINT-03 | Built PDFs ≤ 2 pages, printed fragments present | integration | `uv run pytest -m pdf tests/test_print_worksheets_pdf.py` | ❌ W0 | ⬜ pending |
| PRINT-04 | Fast grid replay == rules; key guard (D-21); negative controls; D-09 hint brute force | unit | `uv run pytest tests/test_worksheet_equivalence.py -x` | ❌ W0 | ⬜ pending |
| PRINT-04 | Slow replay of every enumerated plan per tier | slow | `uv run pytest -m slow tests/test_worksheet_equivalence_full.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Test files: `tests/test_print_preflight.py`, `test_print_driver.py`, `test_print_smoke.py`, `test_print_stamp.py`, `test_print_model.py`, `test_print_render.py`, `test_print_worksheets_pdf.py`, `test_worksheet_equivalence.py`, `test_worksheet_equivalence_full.py`
- [ ] `pyproject.toml`: `pdf` marker, `addopts` update, `jinja2==3.1.6`, dev `pypdf==6.19.0` (+ `uv.lock`)
- [ ] `.gitignore` build dir; `.gitattributes` for `print/**` (LF) and generated PDFs (binary)
- [ ] `tests/test_single_definition.py`: register new `rules.py` helpers / decide `printmodel.py` handling
- [ ] `tests/support`: temp git repo helper; session-scoped built-worksheets fixture that skips without TeX

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| MiKTeX update + `colortbl`/`tikzfill` install | PRINT-01 | User action (D-17) | Update MiKTeX via the console, install packages, then rerun the smoke gate |
| Printed sheet usability (page fit, handwriting space, colours) | PRINT-03 | Physical print | Print one worksheet in colour on A4, fill in a sample wave by hand |
| jinja2/pypdf legitimacy | PRINT-01 | Supply-chain judgment | Confirm the pinned packages are the upstream projects |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
