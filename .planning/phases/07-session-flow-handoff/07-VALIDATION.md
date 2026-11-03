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

- **After every task commit:** the plan's own test files (never the full fast suite while a same-wave sibling may have a RED test in flight); for config/text changes also `uv run planspiel validate && uv run planspiel texts`
- **Integration gate per wave (plan check, revision 2):** the full fast suite `uv run pytest -q -x` runs once where no same-wave RED test can exist: at the start of 07-04 (gate for wave 1: 07-01, 07-02, 07-03), at the end of 07-04 (wave 2: sibling 07-05 adds no test), at the start of 07-08 (gate for wave 3: 07-06, 07-07), at the end of 07-08 (alone in wave 4), and in the 07-09 phase gate (wave 6, after the wave-5 plans 07-10 and 07-11); plus the touched PDF tests (`tests/test_master_pdf.py`, `tests/test_was_neu_pdf.py`, `tests/test_probelauf_pdf.py`) inside print-affecting plans
- **Shared environment:** only 07-01 Task 3 (its last task) changes `uv.lock`/`.venv`: `uv remove --no-sync`, then one `uv sync`, retried if a sibling uv command holds the environment
- **Before `/gsd-verify-work`:** fast suite, full `-m pdf` and `uv run planspiel print --check` green, and the dry-run protocol from 2026-11-25 recorded
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

Filled in by the planner per task. The requirement-level map is:

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| FLOW-02 | blocks sum to total 190; wave 1 = 20; debrief 15..20; no whiteboard block; teams 3 and persons_per_team 5 (D-19 source for the deck); block invisible to rules; validator rejects broken blocks | unit | `uv run pytest tests/test_session_schedule_config.py -q` | ❌ W0 | ⬜ pending |
| FLOW-02..05 | phase-7 prose (sheets.ablauf, sheets.debrief, sheets.was_neu, sheets.probelauf, changed eventkarten/labels keys) has no number word for a count; ALLOWED list with reasons | unit | `uv run pytest tests/test_texts_number_words.py -q` | ❌ W0 (07-02, extended by 07-04, 07-06, 07-08) | ⬜ pending |
| FLOW-02 | schedule rows (labels/direction from texte, cumulative minutes, empty clock column, print list ⊆ rendered jobs, team count from config) | unit | `uv run pytest tests/test_schedule_model.py tests/test_master_model.py -q` | ❌ W0 / ✅ extend | ⬜ pending |
| FLOW-02 | schedule + print-list pages fit, stamp | pdf | `uv run pytest -m pdf tests/test_master_pdf.py -q` | ✅ extend | ⬜ pending |
| FLOW-03 | four stages in order, 2–3 questions each, guide minutes sum to the debrief block, clue-matrix prompt | unit | `uv run pytest tests/test_debrief_model.py -q` | ❌ W0 | ⬜ pending |
| FLOW-03 | debrief page fits in booklet | pdf | `uv run pytest -m pdf tests/test_master_pdf.py -q` | ✅ extend | ⬜ pending |
| FLOW-04 | diff-driven value rows, all rule topics (D-13 + D-29), numbers from config, no attack names | unit | `uv run pytest tests/test_was_neu_model.py -q` | ❌ W0 | ⬜ pending |
| FLOW-04 | baseline isolation + provenance against 1cfb2fa + printed-override record checked against the printed MHP file (Events_Security-Game.pptx slide 9, in final_documents/ or archive/, D-26) | unit | `uv run pytest tests/test_baseline_isolation.py tests/test_print_stamp.py -q` | ❌ W0 / ✅ extend | ⬜ pending |
| FLOW-04 | exactly one page, no overfull | pdf | `uv run pytest -m pdf tests/test_was_neu_pdf.py -q` | ❌ W0 | ⬜ pending |
| FLOW-05 | protocol rows = schedule blocks with planned minutes; wording fixes D-28 | unit | `uv run pytest tests/test_probelauf_model.py -q` | ❌ W0 | ⬜ pending |
| FLOW-05 | protocol one page | pdf | `uv run pytest -m pdf tests/test_probelauf_pdf.py -q` | ❌ W0 | ⬜ pending |
| LEG-01 | inventory at new locations; no build/package reference to `archive/` or retired files | unit | `uv run pytest tests/test_inventory.py tests/test_no_archive_references.py -q` | ✅ update / ❌ W0 | ⬜ pending |
| LEG-02 | README anchors pass; README/CLAUDE.md describe `planspiel print`, `--check`, order config → README → texte → print; CLAUDE.md English, paper-only flow, no "Whiteboard"; no stale `.claude/CLAUDE.md` text | unit | `uv run pytest tests/test_readme_current.py tests/test_claude_md_current.py -q` (+ existing README anchor tests) | ❌ W0 | ⬜ pending |
| LEG-02 | intro deck: minute figures from `session_schedule.blocks`, slide-30 team size from `session_schedule.persons_per_team`, no attack names on the flow slide | unit | `uv run pytest tests/test_intro_deck.py -q` | ❌ W0 (07-07) | ⬜ pending |
| all | print set fresh and committed | cli | `uv run planspiel print --check` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Per-task map (planner, 2026-11-02; revised 2026-11-03 after the second plan check)

Waves: 1 = 07-01, 07-02, 07-03; 2 = 07-04, 07-05; 3 = 07-06, 07-07; 4 = 07-08; 5 = 07-10, 07-11; 6 = 07-09; 7 = 07-12.

| Plan / Task | Requirement | Automated command | Wave 0 file created by the task |
|-------------|-------------|------------------|---------------------------------|
| 07-01 T1 (RED) | LEG-01 | `uv run pytest tests/test_inventory.py tests/test_no_archive_references.py -q` (expected fail) | `tests/test_no_archive_references.py` |
| 07-01 T2 | LEG-01 | `uv run pytest tests/test_inventory.py tests/test_no_archive_references.py tests/test_texts_migration.py tests/test_single_definition.py -q` (generator-coupled tests retired before the move) | — |
| 07-01 T3 (last; shared uv.lock/.venv) | LEG-01 | own files + `tests/test_environment.py` + validate/texts + absent-package check | — |
| 07-02 T1 | FLOW-02 | `uv run pytest tests/test_session_schedule_config.py tests/test_practice_config.py tests/test_validate.py -q && uv run planspiel validate` (incl. `persons_per_team`) | `tests/test_session_schedule_config.py` |
| 07-02 T2 | FLOW-02 | `uv run pytest tests/test_schedule_model.py tests/test_texts_number_words.py tests/test_texts_coverage.py tests/test_texts_digits.py -q && uv run planspiel texts` | `tests/test_schedule_model.py`, `tests/test_texts_number_words.py` |
| 07-02 T3 | FLOW-02 | `uv run pytest -m pdf tests/test_master_pdf.py -q` + the plan's own fast test files | — |
| 07-03 T1 | FLOW-04 | `uv run pytest tests/test_baseline_isolation.py -q` (config and printed provenance) | `tests/test_baseline_isolation.py` |
| 07-03 T2 | FLOW-04 | `uv run pytest tests/test_was_neu_values.py tests/test_baseline_isolation.py -q` | `tests/test_was_neu_values.py` |
| 07-03 T3 | FLOW-04 | `uv run pytest tests/test_baseline_isolation.py tests/test_print_stamp.py tests/test_print_gitattributes.py tests/test_was_neu_values.py -q` | — |
| 07-04 T1 | FLOW-03 | step 0: `uv run pytest -q -x` (wave-1 integration gate); then `uv run pytest tests/test_session_schedule_config.py tests/test_practice_config.py -q && uv run planspiel validate` | — |
| 07-04 T2 | FLOW-03 | `uv run pytest tests/test_debrief_model.py tests/test_texts_number_words.py tests/test_texts_coverage.py tests/test_texts_digits.py -q && uv run planspiel texts` | `tests/test_debrief_model.py` |
| 07-04 T3 | FLOW-03 | `uv run pytest -m pdf tests/test_master_pdf.py -q && uv run pytest -q -x` (wave-2 gate; 07-05 adds no test) | — |
| 07-05 T1 | LEG-02 | checklist sections present, `session_schedule.persons_per_team` cited, board-term search recorded + `uv run planspiel texts` | — |
| 07-05 T2 (checkpoint) | LEG-02 | approval recorded in the checklist | — |
| 07-06 T1 | FLOW-04 | `uv run pytest tests/test_was_neu_model.py tests/test_was_neu_values.py tests/test_baseline_isolation.py tests/test_texts_number_words.py tests/test_texts_coverage.py tests/test_texts_digits.py -q && uv run planspiel texts` | `tests/test_was_neu_model.py` |
| 07-06 T2 | FLOW-04 | `uv run pytest tests/test_master_render.py tests/test_schedule_model.py tests/test_print_cli.py tests/test_print_check.py tests/test_baseline_isolation.py -q` | — |
| 07-06 T3 | FLOW-04 | `uv run pytest -m pdf tests/test_was_neu_pdf.py -q` + the plan's own fast test files | `tests/test_was_neu_pdf.py` |
| 07-07 T1 (RED) | LEG-02 | `uv run pytest tests/test_intro_deck.py -q` (expected fail; incl. the config-composed team size) | `tests/test_intro_deck.py` |
| 07-07 T2 | LEG-02 | `uv run pytest tests/test_intro_deck.py tests/test_inventory.py -q` | — |
| 07-07 T3 (checkpoint) | LEG-02 | `uv run pytest tests/test_intro_deck.py -q` on the committed deck | — |
| 07-08 T1 | FLOW-05 | step 0: `uv run pytest -q -x` (wave-3 integration gate); then `uv run pytest tests/test_probelauf_model.py tests/test_texts_number_words.py tests/test_texts_coverage.py tests/test_texts_digits.py -q && uv run planspiel texts` | `tests/test_probelauf_model.py` |
| 07-08 T2 | FLOW-05 | `uv run pytest -m pdf tests/test_probelauf_pdf.py -q` + schedule/render tests | `tests/test_probelauf_pdf.py` |
| 07-08 T3 | FLOW-05 (D-28) | `uv run pytest tests/test_event_cards.py tests/test_event_text.py tests/test_master_model.py tests/test_wave_page.py tests/test_texts_coverage.py tests/test_texts_number_words.py -q` + card/master PDF tests; plan end: `uv run pytest -q -x` | — |
| 07-10 T1 (RED) / T2 | LEG-02 | `uv run pytest tests/test_readme_current.py` + the seven README anchor test files (no full suite: 07-11 RED in the same wave) | `tests/test_readme_current.py` |
| 07-11 T1 (RED) / T2 / T3 | LEG-02 | `uv run pytest tests/test_claude_md_current.py tests/test_e_target_removed.py -q` (no full suite: 07-10 RED in the same wave) | `tests/test_claude_md_current.py` |
| 07-09 T1 (checkpoint) | FLOW-05 (D-27) | `uv run planspiel validate` + schedule tests | — |
| 07-09 T2 | FLOW-05 | phase gate (`uv run pytest -q`, `-m pdf`, validate, texts, clues; also the wave-4/5 integration gate); build via explicit `uv run planspiel print` action step; verify non-mutating: `uv run planspiel print --check`, clean `git status`, `tests/test_print_check.py`; one print-set commit per release candidate | — |
| 07-09 T3 (human action) | FLOW-05 (D-32, D-34) | `07-SOLO-TIMING.md`: `grep -Eq '^\*\*Block measures_budget:\*\* (WITHIN\|OVERRUN)'`, the same for `wave_1`, `grep -Eq '^\*\*Verdict:\*\* (WITHIN\|OVERRUN)'`, exactly one `**Verdict:**` line | — |
| 07-09 T4 (checkpoint) | FLOW-05 | `uv run planspiel print --check && grep -Eq '^\*\*Verdict:\*\* WITHIN' 07-SOLO-TIMING.md` | — |
| 07-12 T1 | FLOW-05 | `uv run planspiel print --check`; record sections present incl. `## Earlier timings` and the D-34 note | — |
| 07-12 T2 (human action) | FLOW-05 | manual: dry run on 2026-11-25 | — |
| 07-12 T3 | FLOW-05 | `grep -Eq '^\*\*Verdict:\*\* (PASS\|FAIL)' 07-DRYRUN.md`, exactly one `**Verdict:**` line, wave_0 line in `## Verdict` | — |

---

## Wave 0 Requirements

- [ ] `tests/test_session_schedule_config.py`, `tests/test_schedule_model.py`, `tests/test_texts_number_words.py` (FLOW-02; the number-word lint is extended by 07-04, 07-06, 07-08)
- [ ] `tests/test_debrief_model.py` (FLOW-03)
- [ ] `tests/test_was_neu_model.py`, `tests/test_was_neu_pdf.py`, `tests/test_baseline_isolation.py` (FLOW-04)
- [ ] `tests/test_probelauf_model.py`, `tests/test_probelauf_pdf.py` (FLOW-05)
- [ ] `tests/test_no_archive_references.py`; update `test_inventory.py`, `test_environment.py`, `test_single_definition.py`; delete `test_legacy_generators_smoke.py`; retarget or retire `test_texts_migration.py` (LEG-01)
- [ ] `tests/test_readme_current.py` (07-10) and `tests/test_claude_md_current.py` (07-11) instead of one `tests/test_docs_current.py`, so the two LEG-02 doc plans run in parallel without sharing a file; `tests/test_intro_deck.py` (07-07) (LEG-02)

No framework install needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Solo timing of the "Maßnahmen + Budget" block and wave 1 before the print release (D-32, D-34) | FLOW-05 | One person plays both blocks by hand | 07-09 T3: measure selection and wave 1 with only the generated material, each timed against its `session_schedule` block (measures_budget, wave_1); `07-SOLO-TIMING.md` holds one line per block and one `**Verdict:**` line; OVERRUN of either block blocks the release and goes to gap closure; Welle 0 and waves 2/3 are first timed in the dry run |
| Timed dry run: every wave block, Welle 0 included, within planned minutes, total within 190, no author help (D-25) | FLOW-05 | Human timing with a test group | Non-author facilitator runs the full game on 2026-11-25; author fills `spielleitung-probelauf.pdf` |
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
