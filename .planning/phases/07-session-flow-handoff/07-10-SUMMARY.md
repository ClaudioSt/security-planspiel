---
phase: 07-session-flow-handoff
plan: 10
subsystem: documentation
tags: [readme, german, rulebook, print-pipeline, legacy-cleanup]
requires: [07-01, 07-08]
provides:
  - "README.md: current German rulebook (Gesamtreduktion model, three cases, linear KZ interpolation, rounding once per wave, Final-Index) and pipeline description"
  - "README sections Spielmaterial (erzeugt) and Druckmaterial erzeugen (config -> README -> texte.toml -> print -> print --check -> commit)"
  - "tests/test_readme_current.py (RETIRED_TOKENS, REQUIRED_TERMS, ORDER_LINE, COUNT_PHRASES, ALLOWED_COUNT_PHRASES)"
affects: [07-09, 07-11]
tech-stack:
  added: []
  patterns: ["README pinned by retired-token, required-term and count-phrase tests", "PDF names in README checked against render_all jobs"]
key-files:
  created:
    - tests/test_readme_current.py
  modified:
    - README.md
key-decisions:
  - "README stays German (D-20); no fixed numbers and no count words for config values (waves, teams, stages, minutes)"
  - "The Change-Fenster, Kurswechsel, Budget Review and Simulation sections were kept (current and pinned by seven anchor tests); only the stale Kartentext bullet of Kurswechsel was reworded"
  - "Hyphens in rewritten sections are plain; kept sections still carry U+2011, the tests normalise"
requirements-completed: []
duration: ~35 min
completed: 2026-11-04
status: complete
---

# Phase 7 Plan 10: README currency Summary

README.md now teaches the current rules (E-Wert, Gesamtbonus, Gesamtreduktion, Reduktion über Schwelle, linear KZ interpolation, one rounding per wave, Final-Index) and the generated-material pipeline; the retired M_sum / kzUnit / Discovery-Signale model and the two evaluation tables are gone.

LEG-02 is deliberately not marked complete here: it closes only after 07-11 (CLAUDE.md side).

## Tasks and commits

| Task | Commit | Result |
|------|--------|--------|
| 1 RED | 223e542 | `tests/test_readme_current.py`: 15 retired tokens, 12 required terms, order line, PDF names vs `render_all`, count-phrase lint (21 assertion failures on the old README, no collection errors) |
| 2 GREEN | c46c393 | README rewritten: Kernelemente, Spielablauf, Story/Hinweise/Schleier (replaces Discovery), Maßnahmen, Events, Angriffe, Deterministische Auflösung, Wellen-Ziel (Final-Index added), Spielbarkeit, new Spielmaterial (erzeugt), Parametrisierung, new Druckmaterial erzeugen, Qualitätssicherung; Kurswechsel stale-card bullet reworded |

## Verification

- `uv run pytest tests/test_readme_current.py tests/test_budget_review.py tests/test_budget_review_text.py tests/test_kurswechsel.py tests/test_paths.py tests/test_ros_ledger.py tests/test_sparprogramm.py tests/test_e_target_removed.py -q`: 264 passed.
- `uv run planspiel validate`: 0 Fehler, 0 Warnung(en).
- Only `README.md` and `tests/test_readme_current.py` changed (no print input touched).
- Number-word check on added lines: one hit, "zwei Nachkommastellen" in the Final-Index bullet (RoS rounding precision, not a count the config holds); the Change-Fenster phrase "Zwischen zwei Wellen" is in `ALLOWED_COUNT_PHRASES` (any two consecutive waves).
- Full fast suite (`uv run pytest -q`): 2910 passed, 205 deselected in 190.63s (2879 before plus 31 new README tests)

## Deviations from Plan

None - plan executed as written. README names the 15 rendered PDFs (including the two that 07-09 will first commit under `final_documents/generated/`); the test checks them against `render_all`, not against the checked-in files.

## Known Stubs

None.

## Threat Flags

None.

## Self-Check: PASSED

README.md and tests/test_readme_current.py exist; commits 223e542 and c46c393 exist.
