---
phase: 7
slug: session-flow-handoff
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-11-02
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (+ pypdf 6.19.0 for PDF text) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`addopts = -m 'not slow and not pdf'`; markers `slow`, `pdf`, `balance`) |
| **Quick run command** | `uv run pytest -q -x tests/test_<area>.py` |
| **Full suite command** | `uv run pytest -q -x` (fast suite) + `uv run pytest -m pdf -q` (PDF suite) + `uv run planspiel print --check` |
| **Estimated runtime** | ~180 s fast suite, ~220 s PDF suite |

Do not run `-m slow`, `-m balance`, `balance_analysis.py --layers all` or `planspiel gate --paths`: this phase changes no rule and no balance number.

---

## Sampling Rate

- **After every task commit:** the area's quick command; for config/text changes also `uv run planspiel validate && uv run planspiel texts`
- **After every plan wave:** `uv run pytest -q -x`, plus the touched PDF tests (`tests/test_master_pdf.py`, `tests/test_was_neu_pdf.py`, `tests/test_probelauf_pdf.py`) for print-affecting plans
- **Before `/gsd-verify-work`:** fast suite, full `-m pdf` and `uv run planspiel print --check` green, and the dry-run protocol from 2026-11-25 recorded
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

Filled in by the planner per task. The requirement-level map is:

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| FLOW-02 | blocks sum to total 190; wave 1 = 20; debrief 15..20; no whiteboard block; block invisible to rules; validator rejects broken blocks | unit | `uv run pytest tests/test_session_schedule_config.py -q` | ❌ W0 | ⬜ pending |
| FLOW-02 | schedule rows (labels/direction from texte, cumulative minutes, empty clock column, print list ⊆ rendered jobs, team count from config) | unit | `uv run pytest tests/test_schedule_model.py tests/test_master_model.py -q` | ❌ W0 / ✅ extend | ⬜ pending |
| FLOW-02 | schedule + print-list pages fit, stamp | pdf | `uv run pytest -m pdf tests/test_master_pdf.py -q` | ✅ extend | ⬜ pending |
| FLOW-03 | four stages in order, 2–3 questions each, guide minutes sum to the debrief block, clue-matrix prompt | unit | `uv run pytest tests/test_debrief_model.py -q` | ❌ W0 | ⬜ pending |
| FLOW-03 | debrief page fits in booklet | pdf | `uv run pytest -m pdf tests/test_master_pdf.py -q` | ✅ extend | ⬜ pending |
| FLOW-04 | diff-driven value rows, all rule topics (D-13 + D-29), numbers from config, no attack names | unit | `uv run pytest tests/test_was_neu_model.py -q` | ❌ W0 | ⬜ pending |
| FLOW-04 | baseline isolation + provenance | unit | `uv run pytest tests/test_baseline_isolation.py tests/test_print_stamp.py -q` | ❌ W0 / ✅ extend | ⬜ pending |
| FLOW-04 | exactly one page, no overfull | pdf | `uv run pytest -m pdf tests/test_was_neu_pdf.py -q` | ❌ W0 | ⬜ pending |
| FLOW-05 | protocol rows = schedule blocks with planned minutes; wording fixes D-28 | unit | `uv run pytest tests/test_probelauf_model.py -q` | ❌ W0 | ⬜ pending |
| FLOW-05 | protocol one page | pdf | `uv run pytest -m pdf tests/test_probelauf_pdf.py -q` | ❌ W0 | ⬜ pending |
| LEG-01 | inventory at new locations; no build/package reference to `archive/` or retired files | unit | `uv run pytest tests/test_inventory.py tests/test_no_archive_references.py -q` | ✅ update / ❌ W0 | ⬜ pending |
| LEG-02 | README anchors pass; README/CLAUDE.md describe `planspiel print`, `--check`, order config → README → texte → print; CLAUDE.md English; no stale `.claude/CLAUDE.md` text | unit | `uv run pytest tests/test_docs_current.py -q` (+ existing README anchor tests) | ❌ W0 | ⬜ pending |
| all | print set fresh and committed | cli | `uv run planspiel print --check` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_session_schedule_config.py`, `tests/test_schedule_model.py` (FLOW-02)
- [ ] `tests/test_debrief_model.py` (FLOW-03)
- [ ] `tests/test_was_neu_model.py`, `tests/test_was_neu_pdf.py`, `tests/test_baseline_isolation.py` (FLOW-04)
- [ ] `tests/test_probelauf_model.py`, `tests/test_probelauf_pdf.py` (FLOW-05)
- [ ] `tests/test_no_archive_references.py`; update `test_inventory.py`, `test_environment.py`, `test_single_definition.py`; delete `test_legacy_generators_smoke.py`; retarget or retire `test_texts_migration.py` (LEG-01)
- [ ] `tests/test_docs_current.py` (LEG-02)

No framework install needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Timed dry run: waves within planned minutes, total within 190, no author help (D-25) | FLOW-05 | Human timing with a test group | Non-author facilitator runs the full game on 2026-11-25; author fills `spielleitung-probelauf.pdf` |
| Print-list quantities confirmed (D-27) | FLOW-02 | User decision | Checkpoint before printing |
| Physical print review | FLOW-02..05 | Layout on paper | Print the set, check each new page |
| Intro deck checklist approval and result review (D-18) | LEG-02 | User approval, PowerPoint rendering | Approve checklist before edits; open deck after edits |
| README prose quality | LEG-02 | Editorial | User reads README |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 240s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
