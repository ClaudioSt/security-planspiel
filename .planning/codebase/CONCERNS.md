# Codebase Concerns

**Analysis Date:** 2026-11-09

## Tech Debt

**Repository size and binary history:**
- Issue: The `.git` directory is about 1.8 GB. Several versions of the 55 to 83 MB intro and event decks are stored as full blobs in history, and two simulation dumps (`sim_med.json`, `simulation_results_medium.json`, about 52 MB each) were committed earlier and only removed from tracking in `44aa1a2` and `b15b588`.
- Files: `final_documents/Planspiel_Einführung + Grundlagen.pptx` (81 MB at HEAD, at least 6 historical versions), `final_documents/13052026_VWI meets MHP_Offenes Treffen.pptx` (83 MB), `final_documents/MHP Company Profile DE - Jubilee Logo.pptx` (55 MB)
- Impact: Every clone and fetch downloads the full history. Each re-commit of a deck adds another 80 MB blob.
- Fix approach: Track `*.pptx` under Git LFS (for example via `.gitattributes`) for future commits. History rewrite (`git filter-repo`) would reclaim space but rewrites shared history, so it needs an explicit user decision first.

**Git LFS configuration is inert:**
- Issue: `.gitattributes` declares LFS filters for `simulation_results.json`, `simulation_results_high.json` and `sim_high.json`. `git lfs ls-files` reports no tracked objects, and `.gitignore` already excludes all three names. The LFS rules do nothing and make the intent unclear.
- Files: `.gitattributes`, `.gitignore`
- Impact: Misleading configuration. A contributor could assume large dumps are LFS-managed when they are simply ignored.
- Fix approach: Remove the three LFS lines from `.gitattributes`, or add LFS rules for the pptx decks if LFS is adopted (see above).

**Large simulation dumps in the working tree:**
- Issue: `sim_high.json` (361 MB), `sim_med.json` (237 MB) and `sim_low.json` (131 MB) sit in the repo root. `build/` takes 226 MB.
- Files: `sim_high.json`, `sim_med.json`, `sim_low.json`, `build/`
- Impact: Gitignored, so they are not committed, but tools that scan the tree (IDE indexing, Glob, Grep, backup sync via SynologyDrive) slow down or read them by accident.
- Fix approach: Move dumps to a directory outside the repo (or to `build/` with a documented path) and point `balance_analysis.py --out` there.

**Local settings file is tracked and carries personal paths:**
- Issue: `.claude/settings.local.json` is tracked, although it is a per-user file. The working copy has been emptied of an allowlist that contained personal document paths (`final_documents\Budget.docx`, `Angriff-1_Ransomware.docx`). `.gitignore` does not exclude it.
- Files: `.claude/settings.local.json`, `.gitignore`
- Impact: Machine-specific permissions and file paths land in history and in every clone. The working-tree change is currently unstaged.
- Fix approach: Add `.claude/settings.local.json` to `.gitignore` and remove it from the index (`git rm --cached`), keeping `.claude/settings.json` tracked.

**Print-only wave logic in long functions:**
- Issue: Several functions are very long and mix data selection with text building. Measured by function length in lines: `build_attack_sheet` (163, `planspiel/printmodel.py`), `main` (160, `planspiel/cli.py`), `summarize_tier` (148, `planspiel/report.py`), `_print_command` (134, `planspiel/cli.py`), `build_balance_report` (115, `planspiel/balance.py`), `path_trace` (109, `planspiel/rules.py`), `_narrow_family` (102, `planspiel/gate.py`), `load_config` (102, `planspiel/config.py`).
- Impact: Hard to review and to verify against the hand-calculation worksheets, which is a stated design criterion.
- Fix approach: Split by responsibility when touching these functions. Add characterization tests before splitting `path_trace` and `build_attack_sheet`, since they feed printed values.

**Oversized modules:**
- Issue: `planspiel/rules.py` (1299 lines), `planspiel/validate.py` (1079), `planspiel/texts.py` (909), `planspiel/gate.py` (865), `planspiel/was_neu.py` (813), `planspiel/balance.py` (723).
- Files: as listed
- Impact: `rules.py` is the single definition of all formulas (guarded by `tests/test_single_definition.py`), so its size makes review and audit harder.
- Fix approach: Keep `rules.py` as the one formula home, but move non-formula helpers (path enumeration, swap search helpers) to their own modules.

**Float type hints in exact-arithmetic code:**
- Issue: The project rule is exact arithmetic (`Fraction` or integer scaling), but several rules helpers are typed `float`: `_tier_lookup` (`planspiel/rules.py:340`), `budget_review_delta` (`:355`), the `remaining_budget` parameter (`:435`) and `over_budget` (`:651`). The values are integer k€ in practice.
- Files: `planspiel/rules.py`
- Impact: Type hints promise a float domain that the code does not need. A caller passing a float would get float comparison semantics without any warning.
- Fix approach: Change the annotations to `int` (or `Fraction`) and add a test that the budget path rejects or preserves non-integer input.

**Stale planning state:**
- Issue: `.planning/STATE.md` frontmatter reports `completed_plans: 61` of `total_plans: 62`, `status: executing`, and `last_activity: 2026-11-03`, while commits up to 2026-11-09 exist. The "Performance Metrics" table lists only phases 1 to 6 with `-` values. Plan `07-12` has a PLAN but no SUMMARY, which is expected because it is pending.
- Files: `.planning/STATE.md`, `.planning/ROADMAP.md` (line 345, `07-12` unchecked)
- Impact: Orchestration commands read the frontmatter and may route incorrectly.
- Fix approach: Update the frontmatter and metrics through the GSD state tooling after the dry run.

**Previous codebase maps deleted in the working tree:**
- Issue: `git status` shows the seven `.planning/codebase/*.md` files as deleted (unstaged). This run replaces them with fresh maps.
- Files: `.planning/codebase/`
- Impact: Until the new maps are committed, the repo has no codebase maps in HEAD.
- Fix approach: Commit the regenerated set in one `docs:` commit after review.

**Empty untracked `docs/` directory:**
- Issue: `docs/` exists in the repo root with no content. Git does not track empty directories, so it is invisible to history.
- Files: `docs/`
- Impact: Negligible, but it suggests an intended location that does not exist. The archived design documents live in `archive/historical_docs/`.
- Fix approach: Remove the directory, or add a file if it is meant to hold live docs.

## Known Bugs

**Invalid escape sequences in test string literals (SyntaxWarning):**
- Symptoms: Python 3.12 emits `SyntaxWarning: invalid escape sequence` on import or compile. Confirmed by compiling each file with Python 3.12: `'\c'` in `tests/test_event_cards.py` (compile reports line 198 of the file, the source-text reference in the brief is line 180), `'\d'` in `tests/test_print_cli.py` (line 257), `'\h'` in `tests/test_wave_page_pdf.py` (line 104).
- Files: `tests/test_event_cards.py`, `tests/test_print_cli.py`, `tests/test_wave_page_pdf.py`
- Trigger: Compiling or importing these test modules.
- Workaround: None needed for behaviour. The fix is to make the literals raw strings (`r"..."`) or escape the backslashes. Python planned to turn these into `SyntaxError`, which would break collection.

## Security Considerations

**Unpinned `npx` in the session hook:**
- Risk: `.claude/hooks/session-start.sh` runs `npx -y @opengsd/gsd-core@latest` on every remote session start. The package version is not pinned, so a compromised or changed release runs automatically in the environment.
- Files: `.claude/hooks/session-start.sh`
- Current mitigation: The hook exits early unless `CLAUDE_CODE_REMOTE` is `"true"`, so it runs only in remote sessions.
- Recommendations: Pin the version (`@opengsd/gsd-core@<exact-version>`) and record the pin in the repo. Review the package when bumping.

**Veil enforcement depends on term lists:**
- Risk: Player-facing pages must never name an attack before its wave. The check in `planspiel/veil.py` compares printed text against `content/giveaway_terms.toml`. A term missing from the list lets a name leak into a player print.
- Files: `planspiel/veil.py`, `planspiel/audience.py`, `content/giveaway_terms.toml`
- Current mitigation: Print jobs carry an audience prefix (`spieler-`, `uebung-`, `angriff-`, `spielleitung-`), and an unclassified job is a build error. Clue matrix checks in `content/clues.toml` run through `uv run planspiel clues`.
- Recommendations: Add a check that every attack name and each attack's distinctive German terms from `config` appear in `giveaway_terms.toml`, so the list cannot silently fall behind the config.

**Operand-access guard is weakened by a module-level exemption:**
- Risk: `tests/test_single_definition.py` forbids reading operand attributes (`s_unit`, `base_severity`, `init`, `opex`, `weights`, `bonus`, and so on) outside `planspiel/rules.py`, `planspiel/config.py` and the modules in `OPERAND_READERS`. That set is `{"planspiel/was_neu.py"}` (line 112), so the whole module is exempt. `was_neu.py` reads `init`, `opex` and `weights` at lines 365, 404 and 405. Arithmetic on those values could be added there without the guard catching it.
- Files: `tests/test_single_definition.py`, `planspiel/was_neu.py`
- Current mitigation: The module docstring says it compares and shows values only, and its output is the Was-ist-neu diff.
- Recommendations: Narrow the exemption to specific functions, or add a check that `was_neu.py` contains no `BinOp` on operand attributes. Keep the allowlist entry short and reviewed.

**Printed secrets risk is limited, but the forbidden-files rule is not enforced in code:**
- Risk: The repo has no `.env` or credentials files, so exposure is low. The protection is a process rule (CLAUDE.md, `.claude` guidance), not a check in the code.
- Files: repository root
- Current mitigation: `.gitignore` covers `build/`, dumps and caches.
- Recommendations: Add `.env*` and `*.pem`/`*.key` to `.gitignore` as a defensive default. It costs nothing.

## Performance Bottlenecks

**Full enumeration is the dominant runtime cost:**
- Problem: `uv run pytest -m slow` and `uv run python balance_analysis.py --layers all --paths` run a full enumeration over all dependency-valid measure combinations per budget tier. Output dumps reach 361 MB per tier.
- Files: `planspiel/enumerate.py`, `planspiel/parallel.py`, `planspiel/simulate.py`, `planspiel/gate.py`
- Cause: Exhaustive search by design (determinism plus balance by enumeration, not by sampling).
- Improvement path: The `--jobs` flag already parallelises. Dumps (`--dump-jsonl`) should be streamed and not held in memory. Cache per-plan results keyed by config hash if reruns become frequent.

**PDF build time:**
- Problem: `uv run planspiel print` runs LuaLaTeX for every print job, with up to multiple passes per file (`planspiel/texbuild.py`).
- Files: `planspiel/texbuild.py`, `planspiel/render.py`
- Cause: One LuaLaTeX run per document with stable-aux loops, plus MiKTeX package preflight.
- Improvement path: Skip unchanged jobs using the content hash already computed for the stamp (`planspiel/stamp.py`). `--check` already does this without TeX.

## Fragile Areas

**Print pipeline depends on git state and MiKTeX:**
- Files: `planspiel/stamp.py`, `planspiel/texbuild.py`, `print/miktex-packages.txt`, `planspiel/cli.py`
- Why fragile: The stamp reads the commit date and working-tree state through `git` (`subprocess.run` at `planspiel/stamp.py:63`). A missing git, a shallow clone or a dirty tree changes the stamp. TeX runs depend on MiKTeX's package set (`kpsewhich`, `miktex packages install`). Both are Windows-centred: `tests/test_print_preflight.py:28` and `tests/test_print_stamp.py:280` hard-code `C:\Users\...\MiKTeX` paths.
- Safe modification: Run `uv run planspiel print --check` (no TeX, needs only git) before every commit that touches an input. Keep the `+lokal` stamp behaviour when changing `planspiel/stamp.py`.
- Test coverage: The stamp logic is tested against fixtures, but no test runs on a shallow clone or without git.

**Hand-calculability as a hard constraint on formulas:**
- Files: `planspiel/rules.py`, `simulation_config.json`, `planspiel/validate.py`
- Why fragile: Changing the KZ interpolation or the rounding has already required re-checking the attack worksheets (see `attack_kz_delta()` comments). Any formula change ripples into printed numbers, the stamp and the golden files in `tests/golden/`.
- Safe modification: Follow the documented order (config, README, texts, print, `print --check`, commit). Run `uv run planspiel gate --paths --jobs 3` after any value change, since overspend must never pay off.
- Test coverage: `tests/golden/` pins reference outputs; slow tests cover full enumeration but run only on demand.

**Veil and print materials are generated from one config:**
- Files: `planspiel/printmodel.py`, `planspiel/cards.py`, `planspiel/booklet.py`, `planspiel/wave_page.py`, `print/templates/`
- Why fragile: Print models hold finished strings and templates only place them. A template edit that formats a number, or a model that concatenates a raw number, bypasses `render.tex_escape`. The guard `tex_escape` rejects raw numbers, but only for values that pass through it.
- Safe modification: Keep numbers as strings built in code. Verify with `uv run pytest -m pdf` after template changes (LuaLaTeX required).
- Test coverage: `pdf` tests skip when no TeX engine is present, so they can be silently absent.

**Phase 7 timing depends on a single dry run:**
- Files: `.planning/phases/07-session-flow-handoff/07-DRYRUN.md`, `simulation_config.json` (`session_schedule`), `planspiel/schedule.py`
- Why fragile: The session plan targets a total of 215 minutes (`session_schedule.total_minutes`). The solo measurement of wave 1 was 30 minutes against a re-budget of 25 (D-34 deviation, user-approved 2026-11-04). The dry run on 2026-11-25 (FLOW-05) decides whether the 25-minute budget holds.
- Safe modification: Change timings only in `session_schedule` in the config, then regenerate the intro deck slide and print set.
- Test coverage: Schedule rows are generated from the config, but real durations are measured only in the dry run.

## Scaling Limits

**Enumeration size by budget tier:**
- Current capacity: Full enumeration covers all dependency-valid measure selections for three tiers (`low`, `medium`, `high`). Dumps reach 361 MB for `high`.
- Limit: Adding measures or levels multiplies the combinations. Memory and runtime grow with the product, and the output dump grows with it.
- Scaling path: Prune with the existing dependency rules before enumeration; keep the balance report at summary granularity.

**Team and session count:**
- Current capacity: 3 teams of 5, one afternoon (215 minutes planned in `session_schedule.total_minutes`).
- Limit: The schedule has no slack beyond the planned total of 215 minutes. A larger group or a longer session breaks the timed plan.
- Scaling path: Re-run the schedule validator (`uv run planspiel validate`) with the new numbers in the config.

## Dependencies at Risk

**LuaLaTeX and MiKTeX:**
- Risk: The print build requires a Windows MiKTeX installation with specific packages (`print/miktex-packages.txt`). MiKTeX's installer can open a dialog, which `texbuild.py` disables with `stdin` closed and a timeout.
- Impact: Without MiKTeX, `uv run planspiel print` fails and the PDFs in `final_documents/generated/` cannot be rebuilt.
- Migration plan: `uv run planspiel print --check` covers the committed state without TeX. A TeX Live setup would need the same package list and a new preflight.

**`python-pptx` and the intro deck:**
- Risk: `python-pptx==1.0.2` reads the hand-maintained intro deck in tests and the inventory check. The deck is an 81 MB binary that the tests open on every run.
- Impact: Test runtime and repository size, not correctness.
- Migration plan: Keep the deck in LFS or outside the repo, and move the slide-34 check to a small extracted fixture.

## Missing Critical Features

**No CI runner:**
- Problem: No CI configuration exists (`.github/` is absent and the tooling notes say "No CI runner"). Markers `slow` and `pdf` are excluded from `uv run pytest`, so they run only when someone remembers.
- Blocks: Automatic detection of balance regressions and of stale PDFs. `print --check` only runs when invoked manually.

**No linter or formatter configuration:**
- Problem: Style is enforced by discipline (`110` columns), not tooling. There is no ruff or black configuration in `pyproject.toml`.
- Blocks: Consistent style checks in review. This is also why the SyntaxWarnings above went unnoticed.

## Test Coverage Gaps

**Test suite health (run during this analysis):**
- What's not tested: The fast suite (`uv run pytest`, excluding `slow` and `pdf`) was started during this analysis. At 66% it had reported no failures or errors; the run had not finished when this document was written, so its final result is unknown here. Re-run `uv run pytest` to confirm.
- Files: `tests/`
- Risk: A passing fast suite does not cover full enumeration or PDF output.
- Priority: Medium

**Operand-guard exemption untested:**
- What's not tested: Whether `planspiel/was_neu.py` contains arithmetic on operand attributes.
- Files: `tests/test_single_definition.py`, `planspiel/was_neu.py`
- Risk: A formula can be duplicated in the Was-ist-neu sheet, and the printed "old vs new" values could drift from `rules.py`.
- Priority: High

**Veil term coverage:**
- What's not tested: That every attack's distinctive terms (from `simulation_config.json`) appear in `content/giveaway_terms.toml`.
- Files: `content/giveaway_terms.toml`, `planspiel/veil.py`
- Risk: A new attack leaks its name on a player page before its wave.
- Priority: High

**Tests that depend on Windows paths:**
- What's not tested: Behaviour on non-Windows or without MiKTeX beyond the skip paths. `tests/test_print_preflight.py` and `tests/test_print_stamp.py` use Windows-style fixture paths.
- Files: `tests/test_print_preflight.py`, `tests/test_print_stamp.py`
- Risk: Low for this project, since it runs on one machine, but the stamp and preflight code is not exercised on other platforms.
- Priority: Low

---

*Concerns audit: 2026-11-09*
