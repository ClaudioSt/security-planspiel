---
phase: 03-content-source-veiling
plan: 02
subsystem: content-source
tags: [toml, tomllib, content-lint, veiling, giveaway-lint, audience-views]

requires:
  - phase: 03-content-source-veiling
    provides: content/texte.toml loader, coverage check, digit lint (plan 03-01)
provides:
  - veiled pre-attack titles generated from the wave position (attack_title)
  - PreAttackView and RevealView audience-scoped text views with a leak test
  - content/giveaway_terms.toml and the texts.giveaway lint (veiled profile and story profile)
  - user-reviewed revealed attack texts in content/texte.toml
affects: [03-03 story veiling, 04 sheets, 05 cards and PDFs]

tech-stack:
  added: []
  patterns:
    - "Audience views: PreAttackView has no reveal accessor, RevealView is the only way to reach attack names and bonus reasons"
    - "Giveaway lint with two profiles (veiled without exceptions, story with the D-20 exceptions); term list pinned by a test"
    - "Required text keys derived from the typed config (attacks.<id>.veiled.title per attack)"

key-files:
  created:
    - content/giveaway_terms.toml
    - tests/fixtures/mini_content/giveaway_terms.toml
    - tests/test_texts_views.py
    - tests/test_texts_giveaway.py
  modified:
    - planspiel/texts.py
    - planspiel/cli.py
    - content/texte.toml
    - tests/fixtures/mini_content/texte.toml
    - tests/test_texts_coverage.py
    - tests/test_texts_migration.py

key-decisions:
  - "Veiled title is the bare word 'Angriff' for every attack; the wave position, not the text, distinguishes them (D-13d)"
  - "Revealed attack names stay Ransomware / OT-Stoerung / Datenexfiltration; bonus reasons are verbatim and reachable only through RevealView"
  - "Measure texts are guarded against attack names, ids and bonus reasons by the leak test, not by the giveaway lint (intentional, D-06); the substring match on 'exfil' is intentional"
  - "Revealed ransomware narrative uses 'eurer' like all other texts (only formal Sie/Ihr form removed)"

patterns-established:
  - "Pre-wave material is built only from PreAttackView; revealed material only from RevealView"
  - "A new giveaway term or story exception needs a conscious edit of the pinned terms test"

requirements-completed: [VEIL-01]

coverage:
  - id: D1
    description: "Each attack has a veiled pre-attack title and a revealed at-wave text; titles are generated from the wave position"
    requirement: VEIL-01
    verification:
      - kind: unit
        ref: "tests/test_texts_views.py (38 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "PreAttackView cannot reach revealed names or bonus reasons (leak test over every reachable string, real and mini content)"
    requirement: VEIL-01
    verification:
      - kind: unit
        ref: "tests/test_texts_views.py::test_pre_attack_view_cannot_reach_a_revealed_name_or_bonus_reason"
        status: pass
    human_judgment: false
  - id: D3
    description: "Giveaway lint on veiled keys and event texts (texts.giveaway) with a pinned term list"
    requirement: VEIL-01
    verification:
      - kind: unit
        ref: "tests/test_texts_giveaway.py (96 tests)"
        status: pass
      - kind: other
        ref: "uv run planspiel texts -> 0 Fehler, 0 Warnung(en)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Revealed attack texts reviewed and approved by the user"
    requirement: VEIL-01
    verification: []
    human_judgment: true
    rationale: "Wording of player-facing revealed texts is a content decision (D-13d); approved at the Task 3 checkpoint with one edit"

duration: multi-session (Tasks 1-2 on 2026-10-17, Task 3 on 2026-10-19)
completed: 2026-10-19
status: complete
---

# Phase 3 Plan 2: Veiled Attack Titles and Giveaway Lint (VEIL-01) Summary

**Attack titles before a wave are the bare word "Angriff", generated from the wave position; a PreAttackView with no reveal accessor plus a leak test and a pinned giveaway lint in `planspiel texts` keep attack names out of pre-wave material, and the revealed texts were user-reviewed.**

## Commits

| Task | RED | GREEN / result |
|------|-----|----------------|
| 1 Veiled titles and audience views | f0d46ef `test(03-02): add failing tests for veiled titles and audience views` | abecb71 `feat(03-02): add veiled attack titles and audience-scoped text views` |
| 2 Giveaway lint | 68612f8 `test(03-02): add failing giveaway matcher tests` | 9403d3a `feat(03-02): add the giveaway lint for veiled attack keys and event texts` |
| 3 Reviewed revealed texts (checkpoint:decision) | n/a | c3c7650 `feat(03-02): apply the reviewed revealed attack texts` |

RED evidence: Task 1 failed with `texts.orphan_key` on the new mini `veiled.title` keys in the coverage tests (24 failed, 3 passed) and `ImportError: cannot import name 'PreAttackView'` in `tests/test_texts_views.py`. Task 2 failed with `ImportError: cannot import name 'GiveawayTerms'`. Both RED commits contain only new or extended tests and fixtures.

## Task 3 decision

The user selected: **approve-proposals**. Proposal P1 only was applied: in `attacks.ransomware.revealed.narrative`, "anhand Ihrer Sicherheitsmaßnahmen berechnet." became "anhand eurer Sicherheitsmaßnahmen berechnet." (the only formal Sie/Ihr form in `content/texte.toml`). P2 to P4 were confirmed unchanged: attack names Ransomware / OT-Störung / Datenexfiltration; the veiled text is the title word "Angriff" only; bonus reasons verbatim and revealed-only. The edit was made only after this selection. No migration-fidelity test pinned the old wording.

Revealed set after the edit (names, narratives, CIA rationales, case texts and bonus reasons) is unchanged apart from P1: ransomware (M3, M4, M6 reasons), ot (M5, M7), exfil (M1, M2, M8).

## Verification

- `uv run pytest -q`: 807 passed, 19 deselected (after the Task 3 commit)
- `uv run pytest tests/test_texts_views.py tests/test_texts_giveaway.py -q`: 134 passed (38 views, 96 giveaway; scenarios cover title generation by position, reordered waves, leak test for names and bonus reasons, no reveal member, term list pinned to D-13b, story exceptions, decomposed umlauts, hidden characters, CLI failure on a giveaway)
- `uv run planspiel texts`: `0 Fehler, 0 Warnung(en)`
- `git log -5 --format="%h %s"`: c3c7650 apply the reviewed revealed attack texts; 9403d3a add the giveaway lint; 68612f8 add failing giveaway matcher tests; abecb71 add veiled attack titles and audience-scoped text views; f0d46ef add failing tests for veiled titles and audience views

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Migration test expected the old attack key set**
- **Found during:** Task 1
- **Issue:** `tests/test_texts_migration.py` attack-table test expected only `revealed`; the new `veiled.title` keys broke it.
- **Fix:** Updated to expect `{"veiled", "revealed"}`.
- **Commit:** abecb71

**2. [Rule 1 - Bug] Views-test parametrization bug from RED**
- **Found during:** Task 1 GREEN
- **Fix:** Corrected the parametrization in `tests/test_texts_views.py`.
- **Commit:** abecb71

### Other deviations and notes

1. "Störung in der OT" hits in the veiled profile through the whole-token id `ot` (with config ids) and passes the story profile. The plan's behavior list assumed it passes both. This is stricter on veiled keys and has no effect on real content.
2. The coverage CLI tests copy `giveaway_terms.toml` into their tmp content dirs (68612f8).
3. The `--content-dir` help text in `planspiel/cli.py` now names `giveaway_terms.toml` (9403d3a).
4. `PreAttackView.measure()` returns int level keys; `RevealView.attack()` returns `bonus_reasons {}` when there are none.
5. Observation, no change: the M6 measure text names "Phishing" before the wave. Allowed by D-06 (measure texts are outside the giveaway lint).

## Known Stubs

None.

## Threat Flags

None. T-03-06 to T-03-09 are mitigated by the views and leak test, the giveaway lint, the pinned term list and the blocking decision checkpoint.

## Self-Check: PASSED

- Files: content/giveaway_terms.toml, tests/fixtures/mini_content/giveaway_terms.toml, tests/test_texts_views.py, tests/test_texts_giveaway.py found
- Commits f0d46ef, abecb71, 68612f8, 9403d3a, c3c7650 found in `git log`
