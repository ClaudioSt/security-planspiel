---
phase: 04-print-pipeline-attack-worksheets
verified: 2026-10-22T18:40:00Z
status: human_needed
score: 4/4 must-haves verified
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Colour, duplex A4 test print of final_documents/generated/angriff-1_ransomware.pdf with a sample wave filled in by hand (seven measures, Gesamtreduktion in Fall 3, M4 at level 2, KZ Events +5)"
    expected: "Enough handwriting space in the CIA table and fill-in boxes, usable punch margin, MHP colours legible in print, page 1 and page 2 line up when printed duplex, no clipped text"
    why_human: "Physical print, handwriting space, colour legibility and duplex alignment cannot be judged from PDF text or the log fill report (plan 04-06 Task 2)"
  - test: "Confirm the WR-07 semantics: a build with a non-default --config, --content or --print-dir is stamped '+lokal' and a Hinweis line is printed, instead of being rejected"
    expected: "Maintainer accepts 'mark, do not reject' as the intended behaviour"
    why_human: "Judgment call recorded in 04-REVIEW-FIX.md; the code and tests implement it, but the review asked for a human decision"
gaps: []
deferred: []
---

# Phase 4: Print Pipeline & Attack Worksheets Verification Report

**Phase Goal:** The Angriff 1-3 worksheets are generated from config through a proven, non-interactive LaTeX pipeline and provably compute the same results as the simulation.
**Verified:** 2026-10-22
**Status:** human_needed (all automated checks pass; two human items remain)
**Re-verification:** No, initial verification

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | One command rebuilds the worksheets from config without an interactive MiKTeX prompt (missing package fails fast); two builds from identical inputs give byte-identical PDFs | VERIFIED | `uv run planspiel print` exists (`planspiel/cli.py`, `render.py`, `texbuild.py`). Every TeX call uses `--disable-installer` / `kpsewhich --miktex-disable-installer`, closed stdin and a timeout with process-tree kill. `uv run pytest -m pdf -q`: 21 passed, including `test_rebuild_is_byte_identical`, `test_pdfs_are_byte_identical` (two real CLI builds of the set), `test_missing_package_fails_fast_and_names_the_file`, `test_runaway_document_is_killed_at_the_time_limit`, `test_pdf_carries_no_dates_producer_or_trailer_id`. `planspiel print --check` reports the committed PDFs fresh (exit 0). |
| 2 | Generated Angriff 1-3 show thresholds, caps, bonus tables and Fall 1/2/3 steps, all from config; changing a threshold in config changes the printed number with no template edit | VERIFIED | Extracted text of `angriff-1_ransomware.pdf` and `angriff-3_exfil.pdf` matches `simulation_config.json`: wave 1 weights 0,4/0,4/0,2, Schwelle 23, Kappung 8, Obergrenze 31, Fall 1 160.000 € / KZ -6, Fall 2 KZ +10, Schaden = (31 - GR) × 20.000 €, KZ = -6 + (GR - 23) × 2, bonus rows M3/M4/M6 at level 2 (+6/+6/+3), M4 recovery table 0/10/30/50 %. Wave 3: weights 0,5/0,3/0,2, Schwelle 25, Kappung 7, Obergrenze 32, 140.000 €, KZ -7, slope printed as "× 17 ÷ 7", bonus M1/M2/M8 (+8/+6/+9), no recovery step. `tests/test_print_render.py::test_a_threshold_change_reaches_the_sheet_without_a_template_change` and `::test_a_cap_change_...` render a modified config and assert the new numbers appear and the old ones do not. Template `print/templates/angriff.tex.j2` is thin (Jinja inserts only model strings; `test_template_variables_are_plain_names`). Check is at the rendered-.tex level, not a rebuilt PDF; acceptable. |
| 3 | An equivalence test replays the printed hand-calculation steps over a dense grid and matches the simulation for every input; it fails if the simulation applies a mechanic the worksheet does not print | VERIFIED | `tests/support/worksheet_replay.py` replays from `AttackSheet` exact fields only (AST test bars importing `planspiel.rules`/`rounding`). `tests/test_worksheet_equivalence.py`: dense grid (both bounds, all bonus subsets, M4 levels, event KZ range) compares E, bonus, GR, damage, recovery factor, KZ delta and rounded wave change; four negative controls (recovery, attack KZ, bonus, rounding mutations) are detected; the `apply_attack` key set is pinned (`REPLAYED | DERIVED_NOT_PRINTED | UNPRINTED_UNSCORED={cia_delta}`); D-09 two-decimal brute force. Fast suite: 1172 passed. Slow full replay `tests/test_worksheet_equivalence_full.py` exists and was reported run by the caller: 3 passed, 0 mismatches over 782,336 plans per tier (not re-run here, per instruction). |
| 4 | Every generated page carries a version stamp (hash and date) in its footer | VERIFIED | Both pages of the inspected PDFs end with "Stand 2026-10-22 · 0d24b7d Seite n von 2". `planspiel.sty` stops the build when `stamp.tex` is missing (`test_build_without_stamp_tex_fails_naming_the_file`). `stamp.py` hashes the rendered .tex of the whole set plus style and assets, uses the UTC date of the last data-input commit and appends "+lokal" for a dirty build input; `manifest.json` records `dirty: false`, hash `0d24b7d6...` and per-document tex/PDF SHA-256. `--check` recomputes and agrees. Stamp is a content hash (D-15/D-19), broader than "config hash"; it covers config. |

**Score:** 4/4 truths verified (0 behavior-unverified; the behavior-dependent equivalence truth is backed by passing named tests with negative controls).

### Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `planspiel/texbuild.py`, `print/planspiel.sty`, `print/miktex-packages.txt` | VERIFIED | Present, substantive, wired through `build_documents`; drift test ties loaded packages to probes. |
| `planspiel/render.py`, `planspiel/cli.py` (`print`, `print --check`) | VERIFIED | Registered `DOCUMENT_BUILDERS`; the command ran for `--check`. |
| `planspiel/printmodel.py`, `planspiel/fmt.py`, `rules.worksheet_constants` | VERIFIED | D-06/D-09 guards raise `PrintModelError`; single-definition guard green. |
| `planspiel/stamp.py` | VERIFIED | Wired into CLI, manifest and `--check`. |
| `print/templates/angriff.tex.j2` | VERIFIED | Renders three sheets. |
| `final_documents/generated/angriff-{1_ransomware,2_ot,3_exfil}.pdf`, `manifest.json` | VERIFIED | Two pages each; fresh per `--check`; committed from a clean tree. |
| `tests/support/worksheet_replay.py` + three equivalence test modules | VERIFIED | Run and passing. |

### Key Link Verification

| From | To | Status | Details |
|------|----|--------|---------|
| config + texts -> `build_attack_sheets` -> template -> .tex -> PDF | WIRED | Fragments from the model are asserted in the .tex and in the PDF text (pdf tests). |
| `rules.apply_attack` outputs -> replay | WIRED | Key guard fails on an unlisted new key. |
| stamp -> `stamp.tex` -> footer on every page | WIRED | Seen in extracted text of both pages. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Fast suite | `uv run pytest -q` | 1172 passed, 43 deselected | PASS |
| PDF suite (real LuaLaTeX, bounded) | `uv run pytest -m pdf -q` | 21 passed | PASS |
| Freshness of committed PDFs | `uv run planspiel print --check` | "Druckmaterial aktuell: Stand 2026-10-22 · 0d24b7d (3 Dokument(e))", exit 0 | PASS |
| Config validator | `uv run planspiel validate` | 0 errors, 1 warning (17/7 slope, wave 3; expected, Phase 6 BAL-02) | PASS |

Working tree after the runs: only the pre-existing `.claude/settings.local.json` modification; the PDF/manifest were not rewritten.

### Requirements Coverage

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| PRINT-01 | One command, non-interactive, reproducible LaTeX -> PDF | SATISFIED | SC1 evidence |
| PRINT-03 | Attack worksheets generated incl. thresholds, caps, bonus tables, Fall 1/2/3 steps | SATISFIED | SC2 evidence |
| PRINT-04 | Equivalence test of printed steps vs simulation over a dense grid | SATISFIED | SC3 evidence |
| PRINT-11 | Version stamp on every generated page | SATISFIED | SC4 evidence |

No orphaned requirements: REQUIREMENTS.md maps only these four IDs to Phase 4.

### Anti-Patterns Found

None blocking. No TBD/FIXME/XXX in the Phase 4 source files or templates. Remaining open items are non-blocking:

| Item | Severity | Note |
|------|----------|------|
| IN-01 to IN-09 from 04-REVIEW.md (e.g. "GR" never introduced on the sheet, `\levelbadge` silent above level 3, missing glyph does not fail the build) | Info | Out of fix scope by decision; none breaks a success criterion. "GR" abbreviation is worth a glance during the print test. |
| Page 1 of waves 1 and 3 has only 3.5-4.5 mm spare height | Info | A longer narrative in `content/texte.toml` can push it over; the pdf fill-report test will flag it. |
| Wave-3 slope 17/7 | Info | Known; deferred to Phase 6 (BAL-02), printed exactly and validator warning kept by decision D-08. |
| Legacy `Angriff-*.docx` and the print-sync text in CLAUDE.md | Info | Intentionally untouched until Phase 7 (LEG-01/LEG-02). |
| POSIX process-group kill (WR-05) | Info | Tested with fakes only; this machine is Windows. |

### Human Verification Required

1. **Colour/duplex A4 test print of `angriff-1_ransomware.pdf` with a sample wave filled in by hand.**
   Test: print in colour, duplex, A4; fill in seven measures, a Fall-3 Gesamtreduktion, M4 at level 2 and KZ Events +5.
   Expected: enough handwriting space, usable punch margin, legible colours, pages align duplex, nothing clipped.
   Why human: physical output and handwriting usability cannot be checked programmatically (plan 04-06 Task 2).
2. **Accept the WR-07 design choice** (non-default input paths mark the stamp "+lokal" instead of being rejected). Low risk; recorded in 04-REVIEW-FIX.md for human confirmation.

### Gaps Summary

No gaps. All four ROADMAP success criteria are backed by code, committed artifacts and passing tests run in this verification. The phase is `human_needed` only because the physical test print is an open, known manual check.

---

_Verified: 2026-10-22_
_Verifier: Claude (gsd-verifier)_
