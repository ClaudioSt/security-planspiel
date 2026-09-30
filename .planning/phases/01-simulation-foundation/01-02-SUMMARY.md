---
phase: 01-simulation-foundation
plan: 02
subsystem: infra
tags: [utf-8, encoding, umlauts, ast-lint, pytest, config]
requires: ["01-01"]
provides:
  - "UTF-8 read/write in simulate_outcomes.py and analyze_simulation_results.py"
  - "AST lint test that every text-mode open/read_text/write_text declares encoding="
  - "planspiel.cli.configure_utf8_stdio(), called first in main()"
  - "simulation_config.json display strings with real umlauts/ß, ids and keys unchanged ASCII"
  - "import-only smoke test proving the untouched legacy generators still load the fixed config"
affects: [01-03, 01-04, 01-05, 01-06, 01-07]
tech-stack:
  added: []
  patterns: ["explicit encoding= on all text I/O, enforced by AST lint", "config edited by targeted string replacement, never re-serialized"]
key-files:
  created: [tests/test_encoding_lint.py, tests/test_config_text.py, tests/test_legacy_generators_smoke.py]
  modified: [simulate_outcomes.py, analyze_simulation_results.py, planspiel/cli.py, simulation_config.json]
key-decisions:
  - "Config text fixed in place (11 lines) with byte-level replacements that keep CRLF line endings, key order and compact levels objects"
  - "json.dumps defaults kept for the legacy results file (ensure_ascii=True), so its bytes stay ASCII-identical"
requirements-completed: [FOUND-04]
duration: 12min
completed: 2026-09-30
status: complete
---

# Phase 1 Plan 02: UTF-8 I/O and umlaut-fixed config Summary

Config and results files are now read and written as UTF-8 on this cp1252 machine, CLIs can emit UTF-8 on a pipe, and all transliterated German display strings in `simulation_config.json` use real umlauts/ß, guarded by an AST encoding lint and a transliteration allow-list test.

## Tasks

| Task | Name | Commits |
|------|------|---------|
| 1 | UTF-8 file I/O, encoding lint, UTF-8 stdout helper | RED e869e02, GREEN 1c24e50 |
| 2 | Real umlauts in config display strings, ASCII ids, generator smoke test | RED 1bf7cba, GREEN 4858642 |

## TDD runs

Task 1 RED (`uv run pytest tests/test_encoding_lint.py tests/test_config_text.py -q`): `4 failed`.
- lint: `assert ['simulate_ou...esults.py:15'] == []`, "Left contains 4 more items, first extra item: 'simulate_outcomes.py:586'" (violations at simulate_outcomes.py:77, :586, analyze_simulation_results.py:9, :15)
- loader: `'EDR/XDR erkennt Ransomware frÃ¼h' == 'EDR/XDR erkennt Ransomware früh'` failed
- mojibake: first offender `('EDR/XDR erkennt Ransomware frÃ¼h', 'Ã')`, 4 more
- stdio: `ImportError: cannot import name 'configure_utf8_stdio' from 'planspiel.cli'`

Task 1 GREEN: `4 passed in 0.12s`; whole suite `12 passed in 0.57s`.

Task 2 RED (`uv run pytest tests/test_config_text.py -q`): `2 failed, 4 passed`. `test_wave_names_use_umlauts`: `'OT-Stoerung' == 'OT-Störung'` failed; `test_display_strings_have_no_transliterations`: 16 offenders, first `$.waves[1].name: 'OT-Stoerung' (stem stoerung)`. `test_ids_and_keys_stay_ascii` passes before and after, as intended.

Task 2 GREEN:
```
uv run pytest tests/test_config_text.py tests/test_encoding_lint.py tests/test_legacy_generators_smoke.py -q
........                                                                 [100%]
8 passed in 1.12s

uv run pytest -q
................                                                         [100%]
16 passed in 0.92s
```

Other checks:
- `git diff HEAD~4 --stat -- simulation_config.json`: `1 file changed, 11 insertions(+), 11 deletions(-)`
- `git status --porcelain angriff_berechnung.xlsx`: empty
- `simulation_config.json` starts with `{` (no BOM), still contains `"id": "operative_unterstuetzung"` and `"attack_id": "ot"` (one match each)

## Config strings changed

- `waves[1].name`: OT-Stoerung -> OT-Störung
- `events.wave_1[0].description`: Geschaeftsfuehrung -> Geschäftsführung, Massnahmenwechsel -> Maßnahmenwechsel, durchzufuehren -> durchzuführen
- `events.wave_1[1].name`: Operative Unterstuetzung -> Operative Unterstützung; description "pro aktiver Massnahme" -> "pro aktiver Maßnahme" (id `operative_unterstuetzung` unchanged)
- `events.wave_2[0].description`: verkuendet -> verkündet
- `events.wave_2[1].description`: prueft -> prüft
- `events.wave_2[2].description`: haengt -> hängt
- `events.wave_3[0].description`: Fuer jede Massnahme auf hoechstem Niveau -> Für jede Maßnahme auf höchstem Niveau
- `events.wave_3[1].description`: Verschaerfte -> Verschärfte
- `final_events[0].description`: geprueft -> geprüft
- `_comment_events`: aufgefuehrt -> aufgeführt

No stem in the allow-list produced a false positive on correct text, so no pattern was tightened or removed.

## Deviations from Plan

None - plan executed exactly as written. The config edit used a small Python script doing exact-count-1 byte replacements instead of the Edit tool, because the file has CRLF line endings; the result is the same targeted replacement (11 changed lines, no reflow).

## Known Stubs

None.

## Threat Flags

None.

## Self-Check: PASSED

Created files exist (`tests/test_encoding_lint.py`, `tests/test_config_text.py`, `tests/test_legacy_generators_smoke.py`); commits e869e02, 1c24e50, 1bf7cba, 4858642 present in `git log`.
