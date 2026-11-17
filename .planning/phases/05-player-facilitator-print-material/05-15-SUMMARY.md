---
phase: 05-player-facilitator-print-material
plan: 15
subsystem: print
tags: [facilitator-booklet, answer-keys, check-rows, clue-matrix, stamp-inputs, format-approx, print-10]

requires:
  - phase: 05-player-facilitator-print-material
    provides: rules.path_trace and practice.check_example (05-11), Welle 0 document (05-12), cfg.final_index weights (05-13), reference_plans and fmt.format_approx (05-14)
provides:
  - planspiel.master with MASTER_JOB, build_master_sheet, MasterSheet and its parts, KEY_ROW_IDS, FINAL_ROW_IDS
  - print/templates/master.tex.j2 and the facilitatornotice style macro (spielleitung-uebersicht.pdf, 12 pages)
  - "[sheets.spielleitung] texts (digit-free, final_index_provisional = vorläufig, approximation hint)"
  - render_all(..., clues=()) with builder signature (cfg, texts, env, clues) and render.master_sheet
  - ERROR print.clues in planspiel print and --check; content/clues.toml in stamp.DATA_INPUTS and BUILD_INPUTS
  - tests/golden/answer_keys.json pinning every printed answer-key string
affects: [05-16]

tech-stack:
  added: []
  patterns:
    - "Facilitator booklet model reads revealed texts through RevealView and FacilitatorView, formats only; every number comes from rules.worksheet_constants, rules.path_trace and rules.final_index"
    - "Answer keys are columns of formatted WaveTrace fields in a fixed row order (KEY_ROW_IDS); one builder serves the waves and Welle 0"
    - "Build guard in the model: missing, illegal, over-budget or swap-only reference path is a PrintModelError naming the tier"
    - "Per-page fill report (\\pagereport counter) so the PDF test can prove one report per page and no overflow"

key-files:
  created:
    - planspiel/master.py
    - print/templates/master.tex.j2
    - tests/test_master_model.py
    - tests/test_master_render.py
    - tests/test_master_pdf.py
    - tests/golden/answer_keys.json
  modified:
    - planspiel/render.py
    - planspiel/cli.py
    - planspiel/stamp.py
    - planspiel/texts.py
    - content/texte.toml
    - tests/fixtures/mini_content/texte.toml
    - print/planspiel.sty
    - tests/conftest.py
    - tests/test_print_stamp.py
    - tests/test_print_cli.py
    - tests/test_print_render_env.py
    - tests/test_veil_audience.py

key-decisions:
  - "Values without a finite decimal form on the facilitator sheet (17/7 slope, attack KZ in wave 3, RoS, final index) go through fmt.format_approx; a signed wrapper (approx_signed) keeps the sign for KZ values; E-value and GR also use format_approx so a future weight like a third cannot crash the build"
  - "The overview page also lists the pinned reference path per tier (start, swap, voluntary move) because the answer keys are only meaningful together with that path"
  - "Every wave is two pages: parameters, bonus table and check rows on the first; event schedule and answer keys on the second (the wave-two schedule plus a 9-row GR table did not fit one page)"
  - "The GR step table is transposed (one column per whole GR step, three rows) to keep wave pages inside the text height"
  - "Clue matrix: one attack per page, document and section stacked in one column; hyphenation stays off so the PDF text matches the model strings"
  - "Final index cells carry the vorläufig label in every cell, not only in a note"

patterns-established:
  - "Builders of the render registry take (cfg, texts, env, clues); only the master builder reads clues"
  - "Facilitator job (spielleitung- prefix) is rendered, stamped and logged like every document but never veil-scanned"

requirements-completed: []

duration: 35 min
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 15: Facilitator master sheet Summary

**`uv run planspiel print` now builds `spielleitung-uebersicht.pdf`, a 12-page facilitator booklet with per-wave parameters, GR quick-check rows, the event schedule and answer keys for the three pinned reference paths (all from `rules.path_trace`), the Budget Review, the final table with the final index marked `vorläufig`, the Welle 0 key and the clue matrix, with `content/clues.toml` as a stamped, checked print input.**

PRINT-10 spans 05-13 to 05-16, so the requirement is intentionally not marked complete here; 05-16 regenerates the committed set and closes it.

## Accomplishments

- `planspiel/master.py` (Task 1): `build_master_sheet(cfg, texts, clues)` returns None without reference plans (mini config). Per wave it holds the parameters (weights, threshold, cap, upper bound, unit damage, slope with `≈` when non-terminating, KZ at both bounds, recovery applicability with the r table), the bonus table with the revealed reasons, check rows (Fall 1/2/3 bounds with damage and KZ, a table for every whole GR step), the event schedule (name, effect kind, heading, effect lines from `eventtext.effect_rows`) and the answer keys: 21 rows in calculation order per tier column (selection, CIA, E-value, bonus with met/missed marks, GR, Fall, damage before recovery, r, damage after recovery, attack KZ, event KZ, KZ before rounding, rounded change, KZ before/after clamp, own OPEX, window cost, external budget and OPEX, remaining budget). The final table (7 rows) uses `rules.final_index` with the config weights; the Welle 0 key comes from `practice.check_example`. The clue matrix is grouped per attack from `FacilitatorView`.
- Build guard (T-05-44): `PrintModelError` naming the tier when `reference_plans` misses a tier, a path is illegal, a path is over budget, or a path has no voluntary move beyond the swap.
- `[sheets.spielleitung]` (86 keys, digit-free) in the real and the mini texte, registered in `SHEET_KEYS`, not in `PREWAVE_SHEETS`.
- Render stage (Task 2): builders take `(cfg, texts, env, clues)`, `render_all(..., clues=())`, `render.master_sheet` appended to `DOCUMENT_BUILDERS`; `cli._print_command` loads `content/clues.toml` from `--content-dir`, runs `check_clues` after the text check and before render (`ERROR print.clues <code> <path>: <message>`, failure code 1 or 2 under `--check`); a missing clues file stops with `ERROR print.input`.
- `stamp.DATA_INPUTS` and `BUILD_INPUTS` contain `content/clues.toml` (T-05-46); `test_print_stamp.py` moved the file from the not-dirty to the dirty parametrisation and tests the date.
- Template and style: A4 portrait, page-one `\facilitatornotice` (dark red full-width bar), overview with contents, how to use the check rows and the reference paths, then per wave two pages, Budget Review plus final table, Welle 0 key, one page per attack for the clue matrix. Preview inspected as PNG: `build/preview-master/spielleitung-uebersicht.pdf` (12 pages, every page fills 268 to 693 pt of the 731 pt text height).
- `≈` occurs in the master PDF and in no other PDF (PDF test over the whole print set); every page with `≈` carries the hint "≈: auf zwei Nachkommastellen gerundet, nur zur Kontrolle".

## RED runs

- Task 1: `uv run pytest tests/test_master_model.py -x -q` failed at collection with `ImportError: cannot import name 'master' from 'planspiel'`. Commit `0cb3253`.
- Task 2: `uv run pytest tests/test_master_render.py tests/test_print_stamp.py tests/test_print_cli.py -q` gave `13 failed, 68 passed, 8 errors` (errors: `TypeError: render_all() got an unexpected keyword argument 'clues'`; failures: builder registry and signature, missing `master.tex.j2`, `\facilitatornotice`, `content/clues.toml` stamp inputs, the four `print.clues` CLI cases). Commit `d885daf`.

## Verification

- `uv run pytest -q`: 2269 passed, 153 deselected (baseline 2219 / 140; +30 model, +14 render, +4 CLI, +2 stamp), 112 s.
- `uv run pytest -m pdf -q`: 131 passed (baseline 118; +13 master PDF tests, none skipped), 154 s.
- `uv run pytest tests/test_master_model.py tests/test_reference_plans.py tests/test_single_definition.py -q`: 126 passed.
- `uv run planspiel texts`: 0 errors; `uv run planspiel clues`: 0 errors; `uv run planspiel validate`: 0 errors, 1 warning (the known 17/7 KZ-slope warning).
- `git status --porcelain final_documents/generated`: empty.
- Answer-key values were compared with an independent formatting of `path_trace` in the test (not through the model) and, per wave and tier, with `tests/support/worksheet_replay.replay_steps`; the check-row table was replayed on a GR with no bonus and no event.

## Pinned values worth knowing (from `tests/golden/answer_keys.json`)

Final table (Low, Medium, High): KZ at the end 60, 62, 62; own spend 310.000 €, 334.000 €, 398.000 €; total damage 230.000 €, 255.200 €, 41.600 €; RoS ≈ 0,26, ≈ 0,09, ≈ 0,45; final index ≈ 85,81, ≈ 71,22, ≈ 107,33 (each followed by "(vorläufig)"). Welle 0 key: GR 23, damage 20.000 € before and 18.000 € after recovery, KZ change +2,5 rounded to +3, KZ 101 clamped to 100. These match the 05-14 summary numbers for the pinned paths.

## Task Commits

1. Task 1 RED: `0cb3253` test(05-15): add failing master sheet model tests
2. Task 1 GREEN: `68ecc6c` feat(05-15): add the master sheet model with answer keys from the rules
3. Task 2 RED: `d885daf` test(05-15): add failing master sheet render and pdf tests
4. Task 2 GREEN: `f763656` feat(05-15): add the facilitator master sheet

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Three-argument builder lambdas in tests that were not in the plan's file list**
- **Found during:** Task 2 GREEN
- **Issue:** The plan fixes the builder signature to `(cfg, texts, env, clues)`; `tests/test_print_render_env.py` and `tests/test_veil_audience.py` (and one lambda in `tests/test_print_cli.py`) register `lambda cfg, texts, env: ...` builders and would fail with a TypeError.
- **Fix:** the lambdas take `clues` as the fourth parameter; no assertion changed.
- **Files modified:** tests/test_print_render_env.py, tests/test_veil_audience.py, tests/test_print_cli.py
- **Commit:** f763656

**2. [Rule 1 - Bug] Test slips found while turning the model tests green**
- **Found during:** Task 1 GREEN
- **Issue:** four test bugs, none in the model: a `swap = None` reference window is rejected by the config validator (the illegal-path test now deletes the key), the clue row number is an int in `ClueRow`, a terminating slope (2) trivially contains its own approximation text, and one comparison was too loose.
- **Fix:** the tests state the intended property; the model was untouched.
- **Commit:** 68ecc6c

**3. [Rule 1 - Bug] Hyphenation in the clue table broke the PDF text match**
- **Found during:** Task 2 GREEN
- **Issue:** allowing hyphenation in narrow clue columns printed `Unterneh-menssteckbrief`, so the squashed PDF text no longer contained the model strings.
- **Fix:** hyphenation stays off (package default); the clue table has four columns with document and section stacked in one 55 mm column, which also fits the raw source-key fallback of the section column.
- **Commit:** f763656

### Layout choices beyond the plan wording

- The overview also prints the three pinned reference paths; the event schedule sits on the second page of each wave; the GR step table is transposed. All three came from rendering the preview (a wave-two page with schedule and a 9-row table overflowed the text height).
- Added text keys beyond the plan's list: `contents_title`, `recovery_allowed`, `recovery_not_allowed`, the `key_*` and `final_*` labels. `welle0_title` avoids the digit lint; the column header builds "Welle 0" from the tracking vocabulary and the wave id.
- `master.approx_signed` (signed variant of `format_approx`) is new; it exists in `master.py` only, so `≈` still reaches no player document.

## Open items

- Human check (plan `<human-check>`, facilitator usability under time pressure) is not done: print `build/preview-master/spielleitung-uebersicht.pdf`, check a filled team sheet or an invented wave-two GR against the check rows, and follow the medium path with the keys. The booklet is regenerated into `final_documents/generated/` only in 05-16.
- The clue matrix shows the raw source key in the "Abschnitt" column for the two mail documents (`story.anfrage_mail.lage.paragraphs`, `story.audit_mail.einleitung.paragraphs`), because `FacilitatorView._clue_section` falls back to the key when no heading exists on the path. Out of scope here (it changes `texts.py` and the `planspiel clues` output); worth a heading or label in a later content pass.
- The paths and final-index weights stay provisional until the Phase 6 rebalance (D-18, BAL-03); the golden and the printed `vorläufig` labels mark that.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. T-05-43 (booklet reaching players) is mitigated by the `spielleitung-` prefix, a separate PDF, the page-one notice and the absence from every pre-wave list. T-05-44 (keys diverging from the simulation) by `rules.path_trace` on the pinned legal paths, the independent replay, the pinned golden and the four-way build guard. T-05-46 (clues change not in the stamp) by the two input lists, `check_clues` at print time and the moved stamp test. T-05-47 (approximations on player material) by the PDF test that `≈` appears in no other PDF. T-05-48 (TeX injection) by the `tex_escape` finalize hook, the plain-variable lint test on `master.tex.j2` and `check_clues`.

## Self-Check: PASSED

- Created files exist: `planspiel/master.py`, `print/templates/master.tex.j2`, `tests/test_master_model.py`, `tests/test_master_render.py`, `tests/test_master_pdf.py`, `tests/golden/answer_keys.json`.
- Commits `0cb3253`, `68ecc6c`, `d885daf`, `f763656` are in `git log`.
- `build/preview-master/spielleitung-uebersicht.pdf` exists (not committed).
