---
phase: 05-player-facilitator-print-material
plan: 09
subsystem: print
tags: [assets, content-hash, stamp, texbuild, images, gitattributes]

requires:
  - phase: 05-player-facilitator-print-material
    provides: texbuild/stamp/cli print pipeline (Phase 4), TeX read-guard test, wave explainer (05-08)
provides:
  - texbuild.ASSET_DIR, texbuild.ASSET_FILES, texbuild.asset_paths(content_dir), build_documents(assets=...), check_asset_name
  - stamp.content_hash(documents, static_files, assets=None) and compute_stamp(..., assets=...) with asset bytes in the digest
  - content/assets/images as DATA_INPUTS and BUILD_INPUTS entry
  - CLI asset resolution under --content-dir with ERROR print.input for a missing image
  - TeX probes graphicx.sty -> graphics, multicol.sty -> tools; graphics in print/miktex-packages.txt
  - .gitattributes rule content/assets/images/*.png binary
  - 1x1 PNG fixtures in tests/fixtures/mini_content/assets/images
affects: [05-10, 05-15, 05-16]

tech-stack:
  added: []
  patterns:
    - "Images enter the build only through a code-constant name list; asset bytes are hashed with an 'asset' domain prefix after the static files"
    - "Asset bytes are hashed raw (no line-ending normalisation), unlike .sty/.tex/.cls static files"

key-files:
  created:
    - tests/test_print_assets.py
    - tests/fixtures/mini_content/assets/images/zeitungsartikel_bild_audit.png
    - tests/fixtures/mini_content/assets/images/zeitungsartikel_bild_fabrik.png
  modified:
    - planspiel/texbuild.py
    - planspiel/stamp.py
    - planspiel/cli.py
    - print/miktex-packages.txt
    - .gitattributes
    - tests/test_print_stamp.py
    - tests/test_print_stamp_pdf.py
    - tests/test_print_cli.py
    - tests/test_print_gitattributes.py

key-decisions:
  - "content_hash keeps its (documents, static_files) positional shape and gains a third optional `assets` mapping of name -> bytes; the plan text named `print_dir` as second argument, but the existing signature (pinned by test_hash_cannot_take_a_stamp) takes already-read static files, so the hash stays pure and compute_stamp reads the asset files"
  - "Asset name check is stricter than Path(name).name == name: it also rejects '', '.', '..', '/', backslash and ':' so the rule holds identically on Windows and POSIX"
  - "The mini content fixture carries two 1x1 PNGs (67 bytes each) instead of the 1.7 and 2.0 MB real images, so the CLI tests that run against MINI_CONTENT_DIR still pass the new asset resolution"
  - "Asset resolution sits right after the content load in _print_command, before text checks and render: a missing image is an input error (ERROR print.input), exit 1 for print and 2 for --check"

patterns-established:
  - "Any new print asset is added to texbuild.ASSET_FILES only; it is then copied, hashed and covered by the read-guard automatically"

requirements-completed: []

duration: ~25 min (10:39 to 11:05 on 2026-10-26)
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 09: Reproducible asset path for print images Summary

**The two newspaper images can now enter the LaTeX build only through the fixed-name list `texbuild.ASSET_FILES`: they are resolved under `--content-dir`, copied into the build directory, hashed byte for byte into the stamp, tracked as a data and build input, and a missing image stops `planspiel print` and `--check` with `ERROR print.input`. No document uses an image yet.**

PRINT-12 spans this plan and 05-10; the requirement is not marked complete here.

## Accomplishments

- `texbuild.ASSET_DIR = Path("assets") / "images"`, `ASSET_FILES = ("zeitungsartikel_bild_audit.png", "zeitungsartikel_bild_fabrik.png")`, `asset_paths(content_dir)` (raises `TexBuildError` naming the first missing file, also when the entry is a directory) and `build_documents(..., assets=...)`, which validates every name with `check_asset_name` before writing anything and copies the files next to the `.tex` before LuaLaTeX runs.
- `stamp.content_hash` hashes `asset\0 name \0 bytes \0` for each asset in sorted name order after the static files. Without assets the digest is unchanged (pinned by a test with the literal pre-change hash `015c946c...717c`), a one-byte change moves it, dict order does not, and an asset named like a static file does not collide with it.
- `DATA_INPUTS` and `BUILD_INPUTS` gain `content/assets/images`: a commit touching an image moves the stamp date, a modified or untracked image makes the tree dirty (`+lokal`).
- `_print_command` resolves the assets under `--content-dir` and passes them to `compute_stamp` and `build_documents` (to `compute_stamp` only with `--check`).
- `TEX_PROBES` covers `graphicx.sty` and `multicol.sty`; `print/miktex-packages.txt` gains `graphics` (`tools` was listed); `.gitattributes` marks `content/assets/images/*.png binary`.
- The TeX read-guard test now allows `texbuild.ASSET_FILES` next to the static files (the `.fls` of an image document lists the PNGs).

## Task Commits

1. **Task 1 RED: failing asset pipeline tests** - `5106555` (test)
2. **Task 1 GREEN: hashed, fixed-name asset path** - `cd54b3f` (feat)

Plan metadata: see the docs commit that adds this SUMMARY.

## RED run (`5106555`)

- `tests/test_print_cli.py`: collection error `AttributeError: module 'planspiel.texbuild' has no attribute 'ASSET_FILES'`.
- `tests/test_print_assets.py tests/test_print_stamp.py tests/test_print_preflight.py tests/test_print_gitattributes.py`: 32 failed, 69 passed (asset constants, `asset_paths`, copy and name validation, hash with `assets=`, the two input tuples, `compute_stamp(assets=)`, probes, `graphics` in the package list, signature pin, the image date/dirty/untracked parametrisations, `.gitattributes` binary attribute).

After GREEN: 179 passed in the eight named suites; `uv run pytest -q` 1624 passed, 108 deselected (baseline 1587 plus 37 new); `uv run pytest -m pdf -q` 86 passed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The existing CLI tests ran against a content dir without images**
- **Found during:** Task 1 RED (design of the CLI asset resolution)
- **Issue:** `tests/test_print_cli.py` and `tests/test_print_check.py` pass `tests/fixtures/mini_content` as `--content-dir`; with the required "missing image stops the build" rule every success-path test there would fail.
- **Fix:** two valid 1x1 grayscale PNGs (67 bytes each) under `tests/fixtures/mini_content/assets/images/` with the real file names, instead of copying the 3.6 MB originals. Generated once with `zlib`/`struct` (scratchpad script), committed in the RED commit.
- **Files modified:** tests/fixtures/mini_content/assets/images/*.png
- **Commit:** 5106555

**2. [Rule 1 - Plan/code mismatch] `content_hash` signature**
- **Found during:** reading the code before writing tests
- **Issue:** the plan's interface block says `content_hash(documents, print_dir, assets=...)`; the real signature is `content_hash(documents, static_files)` with `test_hash_cannot_take_a_stamp` pinning the parameter list.
- **Fix:** added `assets: Optional[Mapping[str, bytes]] = None` as third parameter and updated the pin to `["documents", "static_files", "assets"]`; `compute_stamp` reads the asset files. The hash function stays free of file access and of any stamp.
- **Commit:** 5106555, cd54b3f

**3. [Rule 3 - Blocking, minor] `.gitattributes` test lives in an existing file**
- **Issue:** the plan lists no `tests/test_print_gitattributes.py` change, but the binary-attribute check belongs there.
- **Fix:** the two image paths were added to the existing `test_binary_assets_under_print_are_never_converted` parametrisation (docstring adjusted).
- **Commit:** 5106555

**Total deviations:** 3 auto-fixed; no scope change. `tests/conftest.py` needed no change (the `printed_set` fixture passes arguments through unchanged).

## Issues Encountered

- A first scripted edit through a Bash heredoc collapsed `\0` and `\n` escapes (as in earlier plans); the script aborted on its own assert before writing, and the affected edits were redone with the Edit tool. A new test line with a collapsed `\n` was found in the diff and fixed before the RED commit.
- One bare `python -` call without `uv run` was issued by mistake with empty stdin; it produced no output and changed nothing.

## Verification

- `uv run pytest tests/test_print_assets.py tests/test_print_stamp.py tests/test_print_cli.py tests/test_print_preflight.py tests/test_inventory.py tests/test_print_gitattributes.py tests/test_print_check.py tests/test_print_driver.py -q`: 179 passed.
- `uv run pytest -q`: 1624 passed, 108 deselected.
- `uv run pytest -m pdf -q`: 86 passed (whole set still builds; no document uses the images; the read-guard passes with the extended allowed set).
- `uv run planspiel validate`: 0 Fehler, 1 Warnung (the existing KZ slope 17/7 warning).
- `git status --porcelain final_documents`: empty.

## Known Stubs

None. The images are deliberately unused until plan 05-10 adds the story documents.

## Threat Flags

None beyond the plan's register. T-05-33 (asset name traversal): names are code constants and `check_asset_name` rejects separators, drive colons, `.` and `..` (tests with 8 bad names, nothing written). T-05-34 (image change not reflected in the stamp): asset bytes are in the content hash, `content/assets/images` is a data and build input, and the read-guard allows only hashed files.

## Next Phase Readiness

- 05-10 can pass `\includegraphics{zeitungsartikel_bild_audit.png}` (plain file name) in a story template; `graphicx` and `multicol` are probed. Its fit proof must cover full-resolution 1448 x 1086 grayscale images (about 1.7 and 2.0 MB each) in the PDF size.
- PRINT-12 stays open for 05-10.
- No blockers.

## Self-Check: PASSED

- Files: planspiel/texbuild.py (`ASSET_FILES = (`, `def asset_paths(`, `"graphicx.sty": "graphics"`, `"multicol.sty": "tools"`), planspiel/stamp.py (`"content/assets/images"` in both tuples), print/miktex-packages.txt (`graphics`), .gitattributes (`content/assets/images/*.png binary`), tests/test_print_assets.py, tests/fixtures/mini_content/assets/images/ (2 PNGs) exist.
- Commits 5106555 and cd54b3f exist in `git log`.
