# External Integrations

**Analysis Date:** 2026-11-09

## APIs & External Services

**Network APIs:**
- None. The project makes no HTTP or API calls at runtime. Package installation goes through the uv registry (`https://pypi.org/simple`, recorded in `uv.lock`); no service is called by the game tooling or the print pipeline.

**Local external tools (subprocess integrations):**
- LuaLaTeX (MiKTeX) - PDF compilation. Invoked in `planspiel/texbuild.py` (`LUALATEX` argument list, `run_lualatex`) with `--disable-installer`, `-interaction=nonstopmode`, `-halt-on-error`, `-file-line-error`, `-recorder`; stdin closed; timeouts kill the process tree
  - Preflight: `kpsewhich --miktex-disable-installer` (`texbuild.py`, timeout 30 s) detects missing packages and names the MiKTeX package ids from `TEX_PROBES`
  - Package list: `print/miktex-packages.txt`
- MiKTeX CLI - suggested installation command for missing packages: `miktex packages install --package-id-file print/miktex-packages.txt` (message in `planspiel/cli.py`); not called automatically
- git - `planspiel/stamp.py` runs `git -C <repo> rev-parse --show-toplevel`, `git log -1 --format=%ct -- <DATA_INPUTS>` and `git status --porcelain` to build the stamp; `tests/support/gitrepo.py` runs git in temporary repositories for tests

## Data Storage

**Databases:**
- None. No database, ORM or SQL client.

**File Storage:**
- Local filesystem only.
  - Inputs: `simulation_config.json`, `content/` (TOML, JSON, `content/assets/images/*.png`), `print/` (`planspiel.sty`, `templates/`), `final_documents/` (manual decks and portrait photos: `final_documents/Planspiel_Einführung + Grundlagen.pptx`, `final_documents/MHP Company Profile DE - Jubilee Logo.pptx`, `final_documents/13052026_VWI meets MHP_Offenes Treffen.pptx`, two JPG portraits)
  - Outputs: `final_documents/generated/*.pdf` and `final_documents/generated/manifest.json` (committed); temporary build directories under `build/` (gitignored)
  - Large generated dumps: `simulation_results*.json`, `sim_{low,med,high}.json`, `simulation_full_*.jsonl` (gitignored, Git LFS filter declared in `.gitattributes`)
- Historical material in `archive/` is outside the build; no code reads it (guarded by `tests/test_no_archive_references.py`)

**Caching:**
- None. Parallel enumeration (`planspiel/parallel.py`, `--jobs`) keeps no persistent cache.

## Authentication & Identity

**Auth Provider:**
- Not applicable. The game has no users, accounts or sessions; it is played on paper.

## Monitoring & Observability

**Error Tracking:**
- None.

**Logs:**
- Console output only. CLI messages are German and printed via `print()` in `planspiel/cli.py`; TeX logs are read back by `texbuild.py` to form error excerpts.

## CI/CD & Deployment

**Hosting:**
- Not applicable. Deliverable is the printed material; the repository is the source of truth on the local machine (Windows 11, Synology Drive path for the project folder in the user's notes).

**CI Pipeline:**
- None detected (no `.github/workflows`, no CI configuration in the repo). Verification is manual: `uv run pytest`, `uv run planspiel print --check`, `uv run planspiel gate`.

**Claude Code / GSD tooling:**
- `.claude/settings.json` registers one `SessionStart` hook: `$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh`. The script exits immediately unless `CLAUDE_CODE_REMOTE=true`; in remote sessions it runs `npx -y @opengsd/gsd-core@latest` (external npm package).
- `.claude/settings.local.json` holds local permission settings only.

## Environment Configuration

**Required env vars:**
- None for the game tooling.
- `CLAUDE_CODE_REMOTE` and `CLAUDE_PROJECT_DIR` are read only by the Claude Code session hook (optional).
- `SOURCE_DATE_EPOCH` and `FORCE_SOURCE_DATE` are set by the code for LuaLaTeX runs (not read from the user environment).

**Secrets location:**
- No secrets are used or required. No `.env` file is part of the project; keys, certificates and tokens are not referenced anywhere in the code.

## Git and Version Control Integrations

**Git:**
- Repository on `main`; `.gitattributes` sets LF line endings for config, text and template files and binary handling for PDFs and images.
- Git LFS filter declared for `simulation_results.json`, `simulation_results_high.json` and `sim_high.json` in `.gitattributes`. These are local dump files, gitignored and not part of the build.
- Commit date of the data inputs determines the print stamp date (`planspiel/stamp.py`, `DATA_INPUTS`).

## Document Inputs (external authoring tools)

**PowerPoint:**
- The intro deck and company/VWI decks are maintained by hand in PowerPoint and read by `python-pptx` only in tests (`tests/test_intro_deck.py`, `tests/test_inventory.py`). The build does not write PPTX files; the former generator scripts are archived.

**Webhooks & Callbacks:**
- Incoming: None
- Outgoing: None

---

*Integration audit: 2026-11-09*
