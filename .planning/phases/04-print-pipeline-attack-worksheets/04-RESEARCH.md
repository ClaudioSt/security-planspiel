# Phase 4: Print Pipeline & Attack Worksheets - Research

**Researched:** 2026-10-20
**Domain:** Config-driven LaTeX (LuaLaTeX) build of hand-calculation worksheets on Windows/MiKTeX; reproducible PDFs; hand-calc/sim equivalence testing
**Confidence:** HIGH for toolchain, reproducibility, D-09 proof and equivalence design (all verified by spikes/brute force on this machine); MEDIUM for final one-page layout (spiked with a hand-written page, not the real Jinja output)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Carried forward (decided earlier, not re-asked)**
- Renderer is **LaTeX, not Typst** (PROJECT.md Key Decisions 2026-09-29). Research stack: LuaLaTeX + Jinja2 with `\VAR{}`/`\BLOCK{}` delimiters, `StrictUndefined`, LaTeX escaping via `finalize`, latexmk (`.planning/research/STACK.md`).
- The attack worksheet is **revealed** material. Its title reads "Angriff N: <Name>" (Phase 3 D-13, D-27). Wave CIA weights and measure→bonus links appear only here (VEIL-04). Revealed texts come only through `planspiel.texts.RevealView`.
- **No numbers in TOML prose** (Phase 3 D-03). Every printed number is computed from config in code (pattern: `planspiel/review_text.py`). Worksheet wording is in `[sheets.angriff]`, `[sheets.labels]` and `attacks.*.revealed.*`.
- **Paper rounding** (Phase 1, 01-06): the KZ change per wave (attack + events) is rounded once, half away from zero, then clamped to 0..100. Everything else stays exact.
- Excel attack calculator is retired. Legacy generators stay untouched until LEG-01 (Phase 2 D-29).
- Known hazard (STATE.md): MiKTeX `AutoInstall=ask` hangs scripted builds, so the **first plan is a non-interactive smoke build**.

**Worksheet content and layout (PRINT-03)**
- **D-01:** **MHP order with numbered steps.** Keep the MHP flow (narrative → CIA table → E-value → bonus → Gesamtreduktion → Fall 1/2/3) but number the steps (Schritt 1…n) and give each step a fill-in box. People who ran the MHP version should recognise the sheet.
- **D-02:** **The E-value step prints the formula with the wave weights from config and fill-in boxes**, e.g. "E-Wert = C ___ × 0,4 + I ___ × 0,4 + A ___ × 0,2 = ___". The MHP sheets did not print the weights at all.
- **D-03:** **Recovery is an extra step on the worksheet**, only when the attack has `allow_recovery = true` (attacks 1 and 2 today): "Schaden nach Recovery = Schaden × (1 − r)", with a small table M4 level → r taken from `measures.M4.levels.*.recovery` (0 / 10 % / 30 % / 50 % today). Attack 3 has no recovery step. The worksheet must record every mechanic the sim applies (see D-11).
- **D-04:** **Each team fills in its own copy** (3 teams × 3 waves = 9 sheets). Wording addresses the team ("Tragt eure …"), as in the docx and `[sheets.angriff]`.
- **D-05:** **Page budget: one A4 page is ideal, two pages are allowed if necessary.** The CIA table does **not** have to reach the maximum possible number of measures. Choose a practical number of rows (the MHP sheet has 6).

**Fall-3 formulas (PRINT-03, hand-calculability)**
- **D-06:** **Damage uses the rearranged form plus a hard guard:** "Schaden = (Obergrenze − Gesamtreduktion) × s_unit", with derived numbers (e.g. "(31 − GR) × 20.000 €", Obergrenze = `e_threshold + mitigation_cap`). This is only correct while `base_severity == mitigation_cap` and `severity_multiplier == 1` (both hold today). If either invariant breaks, **the build fails** instead of printing a wrong formula. There is no auto-switch to the general form.
- **D-07:** **One KZ formula shape on every sheet:** "KZ = kz_at_full_damage + (GR − e_threshold) × Steigung", e.g. "KZ = −6 + (GR − 23) × 2". This replaces the three MHP variants.
- **D-08:** **The slope is printed exactly.** An integer or terminating-decimal slope prints as "× 2" / "× 1,2"; any other fraction prints as "× a ÷ b" (wave 3 today: "× 17 ÷ 7"). The equivalence test stays exact, and the validator warning for 17/7 stays until Phase 6 (BAL-02).
- **D-09:** **Intermediate values are exact, with a printed hint.** E-value and GR are exact (one decimal place with the current weights). For the Fall-3 KZ the sheet says that two decimal places are enough. Research must prove that carrying two decimal places can never flip the final per-wave rounding for any reachable input. If it can, adjust the hint (more places or a different instruction) and say so.
- Fall 1 / Fall 2 lines print their pre-computed outcomes (full damage in €, KZ at full damage / full mitigation), derived in code as on the MHP sheet.

**Equivalence test (PRINT-04)**
- **D-10:** **The once-per-wave KZ rounding is the last step on the worksheet:** "KZ-Änderung dieser Welle = KZ Angriff + KZ Events, gerundet (ab ,5 vom Betrag aufrunden)". The test therefore covers the full wave KZ change including rounding. Clamping to 0..100 needs the running KZ and stays on the Phase-5 tracking sheet.
- **D-11:** **Proof link:** the hand-calc replay reads **only** from the same worksheet print model that the template renders. If the sim applies a mechanic the model and sheet do not carry, the results differ and the test fails (SC3). A slow PDF test extracts the text of each built worksheet (pypdf) and asserts that every number in the print model appears on the page.
- **D-12:** **Grid = synthetic grid plus full replay.**
  - Fast test: every GR step of 0,1 from below Fall 1 to above Fall 2 (exact boundaries included) × every bonus subset × every M4 level × every event-KZ value the config can produce for that wave, compared with `planspiel.rules`.
  - Slow test (`-m slow`): replay every enumerated plan's waves through the worksheet steps and compare with the simulation.

**Build, output and stamp (PRINT-01, PRINT-11)**
- **D-13:** **Command: `uv run planspiel print`**, a new subcommand of the existing CLI next to `validate`, `gate`, `texts` and `clues`. Phase 4 builds the three worksheets; Phase 5 adds its documents to the same command (PRINT-01: one command for all print material).
- **D-14:** **Output:** rendered `.tex`, aux files and logs go to a gitignored build directory. The final PDFs are **committed to `final_documents/generated/`**. Rebuilds are byte-identical, so git shows a PDF diff only when the content changed. Never hand-edit these files.
- **D-15:** **Stamp = input hash + commit date** in every page footer, e.g. "Stand 2026-10-19 · a1b2c3d". The hash covers all inputs (config, `texte.toml`, templates/sty and any other file the build reads). The date is the last commit date of those inputs, never the wall clock, so builds stay reproducible. A dirty working tree adds a marker such as "+lokal". This is broader than SC4's "config hash": a wording change also changes the stamp. The hash scope is refined by D-19.
- **D-16:** **Font: system Arial** (as on the MHP Word worksheets; user decision). Consequence: byte-identical rebuilds are guaranteed only on machines with the same Arial version. The SC1 reproducibility test runs on the build machine (two builds, same inputs, identical bytes). Accept this; do not commit a substitute font.
- **D-17:** **MiKTeX: one-time update plus a pinned package list plus a preflight.** The user updates MiKTeX once (23.10 → current) and installs a documented package list (research: `tikzfill`, `tabularray`, `ninecolors`, `siunitx` and whatever the templates need). `planspiel print` first runs a fast preflight (e.g. `kpsewhich` per required `.sty`) and fails with the missing package names. LuaLaTeX always runs with `--disable-installer` and a subprocess timeout, so a missing package fails fast and never hangs. The first plan is this smoke gate. The MiKTeX update itself is a user action (checkpoint), not something the executor does silently.
- **D-18:** **Colour style like the MHP decks:** use the MHP theme colours from `content/assets/GUIDELINES.md` (accent1 `000099` for headings, level colours L1 `00CC67` / L2 `DDEF03` / L3 `575757` where levels appear, etc.). The worksheets are designed for colour printing. Layout facts such as A4 and the margins left 3.0 / right 1.5 / top 2.0 / bottom 2.0 cm come from the Word worksheets in GUIDELINES.md, as a starting point rather than a hard rule.

**Resolved in the plan-phase requirement review (2026-10-20)**
- **D-19:** **Stamp hash = rendered content (refines D-15).** One hash per build over the generated `.tex` sources of the whole print set (the stamp text itself excluded, e.g. fed in through a separate macro or file) plus `planspiel.sty` and every asset file TeX reads. It changes exactly when printed content changes, whether the change came from config, `texte.toml`, templates or Python code (e.g. a formula change in `rules.py`); a pure code refactor leaves the PDFs byte-identical (D-14). One stamp for the whole set, so mixed old/new printouts are visible at the table. The date stays the last commit date of the data inputs (config, `texte.toml`, templates/sty/assets), not of Python code. "+lokal" marks a build where any build input, including `planspiel/`, differs from HEAD or is untracked; the output directories never count, so a rebuild cannot make itself dirty.
- **D-20:** **Manifest plus a manual freshness check.** `planspiel print` writes `final_documents/generated/manifest.json` (stamp hash, date, and per document the `.tex` and PDF SHA-256). `uv run planspiel print --check` renders the `.tex` without running TeX, recomputes the stamp hash and reports stale PDFs with a non-zero exit. It is not part of the test suite; the suite stays independent of MiKTeX rebuilds.
- **D-21:** **CIA-Mali stays off the worksheet.** The sim's per-wave `cia_delta` (severity × `cia_impact`) feeds no score (KZ, damage, RoS, final index), and the MHP sheets never printed it. The equivalence test covers every scored output (the rounded wave KZ change and the damage incl. recovery) and names `cia_delta` explicitly as an unprinted, unscored sim output. The test also fails when `apply_attack` returns a key that is neither replayed nor on that explicit list, so D-11/SC3 keep their bite.

### Claude's Discretion
- Number of CIA table rows (D-05) and the exact step numbering and wording of new step labels. New wording goes into `[sheets.angriff]` / `[sheets.labels]`, digit-free, and passes `planspiel texts`.
- Module layout for the print model, formatting and rendering (research suggests `printmodel.py`, `fmt.py`, `render.py`, `print/planspiel.sty` and thin Jinja templates) and the build directory name.
- The exact hash algorithm and length, how "dirty" is detected, and how the commit date is fed to LuaLaTeX (`SOURCE_DATE_EPOCH`, `FORCE_SOURCE_DATE`, `\pdfvariable trailerid {}`).
- German number formatting rules (thousands dot, decimal comma, real minus sign "−") and whether `format_eur` from `review_text.py` is reused or moved.
- Whether the PDF tests use a new `pdf` marker or the existing `slow` marker, and that they skip when no TeX engine is present.
- File names under `final_documents/generated/` (they may name the attack: these are revealed sheets).
- The fast grid's GR step (D-12 says 0,1) is derived from config so it is never coarser than the reachable GR lattice, e.g. 1/lcm(10, weight denominators). With today's weights this is 0,1.

### Deferred Ideas (OUT OF SCOPE)
- Clamping KZ to 0..100 on the running total: Phase 5 tracking sheet (PRINT-08).
- Hand-friendly wave-3 slope (replacing 17/7): Phase 6 (BAL-02).
- Archiving `final_documents/Angriff-*.docx` once the generated sheets replace them: Phase 7 (LEG-01).
- CIA-Mali (D-21): decide whether to drop `cia_impact`/`cia_delta` from the sim or make it count toward a score. `README.md` lines 117–118 still say recovery reduces temporary CIA-Mali, while the code applies recovery to the damage; fix that wording together with the decision (Phase 6 or Phase 7, LEG-02).
- Reviewed todo not folded: "Angriffe und Aktionen nur indirekt vermitteln, nie explizit benennen" (covered by Phase 3/5; the attack worksheets are revealed material).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRINT-01 | One command rebuilds all print material via LaTeX → PDF, non-interactively and reproducibly | Direct `lualatex --disable-installer` driver with timeout and aux-stable pass loop; `kpsewhich --miktex-disable-installer` preflight (bare `kpsewhich` HANGS); reproducibility recipe `\pdfvariable suppressoptionalinfo 1023` verified byte-identical across runs, time zones and SOURCE_DATE_EPOCH values (see "Reproducibility") |
| PRINT-03 | Attack worksheets 1–3 generated incl. thresholds, caps, bonus tables, case 1/2/3 steps | Spiked one worksheet page in Arial/MHP colours; print-model design; D-06 guard; D-08 slope printing; single-definition-guard constraints on the model (see "Pitfall 3") |
| PRINT-04 | Equivalence test proves printed steps = simulation over a dense grid | Prototype replay vs `rules.apply_attack` over 148,952 grid points, 0 mismatches, 2.2 s; GR lattice, event-KZ sets, D-09 proof, `apply_attack` key guard, slow full replay via `enumerate_tier(on_outcome=...)` (47.7 s per tier enumeration) |
| PRINT-11 | Every generated page carries a version stamp | Stamp-from-separate-file mechanism (`stamp.tex`), content hash scope, commit-date via `git log -1 --format=%ct` converted to UTC, dirty detection scoped to build inputs, manifest/`--check`, `-recorder` guard that the hash covers every file TeX read |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Extracted from `./CLAUDE.md`, `./.claude/CLAUDE.md` and the global `~/.claude/CLAUDE.md`; treat as locked:

- **Always `uv run`** (`uv run python`, `uv run pytest`, `uv run planspiel ...`); never the `python` on PATH (Inkscape's, no pip).
- **TDD** for all features; verify before claiming done. Slow tests behind `-m slow` (`uv run pytest -m slow`); the fast suite is `uv run pytest` (873 tests, about 35 s measured today).
- **Exact arithmetic** (`Fraction`/scaled ints). **Python's built-in `round()` is banned** in `planspiel/rules.py` and `planspiel/rounding.py`. Rounding goes through `planspiel.rounding.round_half_away(_frac)`.
- **Single source of truth**: every number comes from `simulation_config.json`; order of change is config → README → print material. No fixed numbers in prose; `content/texte.toml` prose is digit-free (lint `uv run planspiel texts`).
- **Every formula exists once** in `planspiel/rules.py` (guard `tests/test_single_definition.py`, see Pitfall 3).
- **Hand-calculability** is a hard criterion: worksheet formulas linear, computable by hand.
- Generated binaries in `final_documents/` are never hand-edited; Legacy generators and `final_documents/Angriff-*.docx` stay untouched until Phase 7.
- Language: code, commits, docs English; game text German; conventional commits (`feat:`, `fix:`, `test:`, `docs:`).
- **One requirement = one PLAN.md** (user rule, `requirement-plan-granularity` skill): PRINT-01, PRINT-11, PRINT-03, PRINT-04 each get their own plan; first plan is the non-interactive smoke build.
- GSD workflow enforcement: file changes go through GSD commands; never `--no-verify`; never force-push main.
- No project skills directory exists (`.claude/skills`, `.agents/skills` absent).

## Summary

The pipeline is feasible on this machine today, with one local package missing. A hand-written Angriff-1-style page (numbered steps, fill-in boxes, bonus table, Fall 1/2/3 block, recovery table, footer stamp, Arial 10 pt, MHP colours, A4 margins 3.0/1.5/1.6/2.0 cm) compiled in about 2.3 s per pass with `lualatex --disable-installer` on MiKTeX 23.10.12 using only installed packages (`fontspec`, `babel`/`ngerman`, `geometry`, `xcolor`, `array`, `tabularx`). Of the Phase-4 package needs only `colortbl` (header shading) is missing; `tabularray`, `ninecolors`, `siunitx` and `tikzfill` are **not needed** for the worksheets (`tikzfill` only matters for Phase 5 `tcolorbox` skins). Arial renders `−`, `×`, `≤`, `≥`, `€`, `ß`, umlauts correctly. The unsupported-Windows "critical issue" line MiKTeX 23.10 prints is noise: exit code stays 0.

Three things in the earlier research and CONTEXT are wrong or incomplete and change the plan: (1) **bare `kpsewhich <missing>.sty` hangs** on the MiKTeX installer dialog (reproduced: 25 s timeout); the preflight must use `kpsewhich --miktex-disable-installer`, which returns in about 1 s. (2) **`SOURCE_DATE_EPOCH` + `FORCE_SOURCE_DATE` do not make LuaTeX output identical** here (ARCHITECTURE.md claimed they do): the PDF trailer `/ID` still differs between runs, and the date string carries the local time-zone offset. What works, verified: `\pdfvariable suppressoptionalinfo 1023` in `planspiel.sty` plus a deterministic two-pass driver (identical bytes across runs, across `TZ`, and across `SOURCE_DATE_EPOCH` values). (3) **Existing guard `tests/test_single_definition.py::test_no_formula_operands_outside_rules_and_config` forbids attribute access to `.s_unit .base_severity .mitigation_cap .kz_at_full_damage .kz_at_full_mitigation .e_threshold .recovery .init .opex .weights .bonus .kz_per_step` in any `planspiel/*.py` outside `rules.py`/`config.py`**, so a naive `printmodel.py` fails the fast suite on the first run.

The D-09 question is answered: carrying two decimal places can never flip the final rounding on any lattice point, for both rounding and truncating to two places, **provided the sheet says "multiply first (× 17), then divide (÷ 7), round only the result"**. Rounding the slope itself (17 ÷ 7 ≈ 2,43) flips 2 cases and truncating it flips 37, and dividing first flips 78 (brute force over every 0,1 GR step and every possible event KZ). The hint wording therefore has to say more than "two decimals are enough". The equivalence design was prototyped end to end (worksheet replay over exact Fractions vs `rules.apply_attack`/`rules.wave_kz_change`): 148,952 grid points, zero mismatches, 2.2 s.

**Primary recommendation:** Build the print stack as `print model (exact Fractions) → Jinja → .tex → lualatex --disable-installer (direct, no latexmk) → PDF`, harden determinism inside `planspiel.sty`, put the version stamp in a separate `stamp.tex` read at `\begin{document}`, and split the work as four sequential plans: PRINT-01 (smoke gate and driver) → PRINT-11 (stamp, manifest, `--check`) → PRINT-03 (model, templates, three worksheets) → PRINT-04 (replay, grid, slow replay, PDF text check).

## Architectural Responsibility Map

This phase has no browser/server tiers; the relevant tiers are the pipeline layers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Derived worksheet numbers (Obergrenze, full damage, slope, Fall bounds) | `planspiel/rules.py` | — | "Every formula exists once"; model must not re-derive (Pattern 1, single-definition guard) |
| Print model (exact values, step structure, guards D-06/D-09) | `planspiel/printmodel.py` | `planspiel/texts.py` (`RevealView`) | Derives everything the sheet prints; the replay reads only this (D-11) |
| German formatting and LaTeX escaping | `planspiel/fmt.py` | `planspiel/review_text.py` (`format_eur` reused) | One formatter; templates never see numbers, only strings |
| Template rendering | `planspiel/render.py` + `print/templates/*.j2` | `print/planspiel.sty` | Jinja only loops and inserts; layout macros live in the `.sty` |
| TeX execution, preflight, pass loop, timeout | `planspiel/texbuild.py` | — | Isolates the only code that can hang |
| Reproducibility hardening (`suppressoptionalinfo`, fixed font mode) | `print/planspiel.sty` | `planspiel/texbuild.py` (env) | In the `.sty` it is part of the hashed inputs and independent of env |
| Version stamp (hash, date, dirty, manifest, `--check`) | `planspiel/stamp.py` | git CLI | Reads git; writes `stamp.tex` and `manifest.json` |
| Equivalence proof | `tests/` (replay + grid) | `planspiel/enumerate.py`, `rules.TierKernel` | Replay is an independent encoding of the printed steps by design |
| Committed outputs | `final_documents/generated/` | `build/print/` (gitignored) | D-14 |

## Standard Stack

### Core
| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| LuaHBTeX (MiKTeX) | 1.17.0 / MiKTeX 23.10.12 installed; current MiKTeX per miktex.org/download is 25.12 (2025-12-31), Wikipedia lists 26.5 (2026-05-14) | PDF engine | Native UTF-8, system Arial via `fontspec`; spike-verified [VERIFIED: local spike] [CITED: miktex.org/download] |
| Jinja2 | 3.1.6 (2025-03-05) | `.tex` rendering with `\VAR{}`/`\BLOCK{}` | Decided in STACK.md; not yet in `pyproject.toml` (add as runtime dependency) [VERIFIED: PyPI JSON API] |
| pypdf | 6.19.0 (2026-09-16) | PDF text extraction in `pdf` tests | Pure Python; behaviour spiked with 6.19.0. 6.21.1 is 3 days old, so pin 6.19.0 [VERIFIED: PyPI JSON API + local spike] |
| pytest | 9.1.1 (already pinned) | Test runner | existing |
| git CLI | present | commit date and dirty detection | existing |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `planspiel/rules.py`, `rounding.py`, `enumerate.py`, `texts.py`, `review_text.py` | in repo | Formulas, exact rounding, plan enumeration, revealed texts, `format_eur` | Reuse; do not re-implement |
| stdlib `hashlib`, `subprocess`, `shutil`, `tomllib`, `fractions`, `datetime` | stdlib | Hash, TeX runner, file ops | no new dependencies for stamp/driver |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Direct `lualatex` + Python pass loop | `latexmk` (4.87 installed) | latexmk needs Perl on PATH (present here via Git for Windows and Strawberry, so it works, but it is an extra machine dependency); timeout kills leave orphan children; pass count is trivially 2 here. Use direct lualatex. |
| `tabularx` + `array` + `colortbl` | `tabularray` | tabularray (and `ninecolors`) are not installed, add compile cost and a version-sensitivity surface; fixed row heights are easy with `\arraystretch`/struts. Not needed in Phase 4. |
| Own `\ps@planspiel` footer + end-of-document label | `fancyhdr` + `lastpage` | both are missing locally; the 6-line zero-dependency version was spiked and works (Pattern 3). |
| `\setmainfont{Arial}` (by name) | `Path=C:/Windows/Fonts/` by file | by name is portable; both are deterministic but produce different bytes (83,619 vs 83,622 bytes), so pick one and never switch silently. Recommend by name. |

**Installation:**
```bash
# runtime dependency + dev dependency (pyproject.toml, then uv.lock)
uv add jinja2==3.1.6
uv add --dev pypdf==6.19.0
# markupsafe is pulled in transitively by jinja2 (latest 3.0.4 is 18 days old; 3.0.3 is 2025-09-27)
```
**Version verification:** `jinja2 3.1.6` (2025-03-05), `pypdf 6.19.0` (2026-09-16; latest 6.21.1 on 2026-10-17), `markupsafe 3.0.4` (2026-10-02) checked against the PyPI JSON API on 2026-10-20. [VERIFIED: PyPI JSON API]

## Package Legitimacy Audit

Ran `gsd-tools query package-legitimacy check --ecosystem pypi jinja2 pypdf markupsafe`. All three returned **SUS**, but the stated reasons are heuristics, not red flags: `unknown-downloads` (the seam has no PyPI download statistics) and `too-new` (the *latest release* of pypdf and markupsafe is days to weeks old, not the project). All three have long-standing upstream repositories (pallets/jinja, py-pdf/pypdf, pallets/markupsafe), no postinstall (pure Python wheels).

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| jinja2 3.1.6 | PyPI | released 2025-03-05 (project long-established) | unknown to seam | github.com/pallets/jinja | SUS (unknown-downloads) | Flagged; planner adds `checkpoint:human-verify` before install |
| pypdf 6.19.0 | PyPI | 6.19.0 released 2026-09-16 (latest 6.21.1, 2026-10-17) | unknown to seam | github.com/py-pdf/pypdf | SUS (too-new, unknown-downloads for latest) | Flagged; pin 6.19.0 (5 weeks old); checkpoint |
| markupsafe (transitive) | PyPI | 3.0.4 released 2026-10-02 | unknown to seam | github.com/pallets/markupsafe | SUS (too-new, unknown-downloads) | Flagged; transitive; checkpoint covers it; 3.0.3 (2025-09-27) is an acceptable pin via `uv.lock` |

**Packages removed due to SLOP verdict:** none
**Packages flagged as suspicious (SUS):** jinja2, pypdf, markupsafe: planner inserts one `checkpoint:human-verify` before `uv add` (the user already chose Jinja2 in STACK.md; pypdf was named in STACK.md as well, so the check is mostly confirming the pins).

TeX packages (colortbl etc.) come from the MiKTeX repository via `miktex packages install`; they are the user's action (D-17), not part of this audit.

## Architecture Patterns

### System Architecture Diagram

```
 uv run planspiel print [--check]
        │
        ▼
 ┌───────────────┐   fail: missing package names + exact install command
 │ preflight     │── kpsewhich --miktex-disable-installer <probe .sty files>  (≈1 s, timeout 30 s)
 └──────┬────────┘   also: lualatex on PATH? Arial present?
        ▼
 simulation_config.json ─► load_config (+ validate) ──┐
 content/texte.toml ─────► load_texts ─► RevealView ──┤
                                                      ▼
                         rules.py helpers (Obergrenze, full damage, slope, bounds)
                                                      ▼
                         printmodel.py  ── guards: base_severity==cap, multiplier==1 (D-06),
                              │                    two-decimal hint valid (D-09)  ──✖ build fails
                              ▼
                         fmt.py (de numbers, U+2212, tex_escape) ─► Jinja env (StrictUndefined, finalize)
                              ▼
                         print/templates/angriff.tex.j2 × 3 waves ─► rendered .tex strings (in memory)
                              │
              ┌───────────────┴────────────────┐
              ▼                                ▼
   stamp.py: sha256(sorted .tex + sty + assets)      --check path stops here:
   date = last commit of data inputs (UTC)           recompute hash+date+dirty, compare with
   dirty = git status over build inputs only         manifest.json, exit 1 if stale (no TeX run)
              │
              ▼
   build/print/{angriff-N.tex, planspiel.sty, stamp.tex}   (stamp.tex excluded from the hash)
              ▼
   texbuild.py: lualatex --disable-installer -recorder ... (cwd=build dir, timeout, ≤3 passes until .aux stable)
              ▼
   build/print/angriff-N.pdf ─► copy ─► final_documents/generated/*.pdf + manifest.json
```

### Recommended Project Structure
```
planspiel/
├── rules.py          # + small derived-constant helpers (Obergrenze, full damage, slope, Fall bounds)
├── printmodel.py     # AttackSheet model: exact Fractions + step structure + guards
├── fmt.py            # German formatting + tex_escape (reuses review_text.format_eur)
├── render.py         # Jinja env, render_all() -> {name: tex}
├── texbuild.py       # preflight, lualatex runner, pass loop, timeout, error extraction
├── stamp.py          # content hash, commit date, dirty, stamp.tex, manifest.json, --check
└── cli.py            # + `print` subcommand (--check, --config, --content-dir, --print-dir, --out-dir, --build-dir)
print/
├── planspiel.sty     # fonts, geometry, colours, hardening, footer, \ibox, \step macros
├── templates/angriff.tex.j2
└── miktex-packages.txt   # package IDs for `miktex packages install --package-id-file`
build/print/          # GITIGNORED (add `build/` to .gitignore)
final_documents/generated/   # committed PDFs + manifest.json
tests/
├── test_print_preflight.py, test_print_driver.py, test_print_smoke.py (pdf marker)
├── test_print_stamp.py, test_print_model.py, test_print_render.py
└── test_worksheet_equivalence.py (+ slow replay, pdf text check)
```
Directory naming: a top-level folder called `print/` is fine (not a Python package, no `__init__.py`; `import print` is never used). Pass paths as CLI options with repo-relative defaults, like the existing subcommands.

### Pattern 1: Direct lualatex with an aux-stable pass loop (verified pieces)
**What:** Run `lualatex` with `cwd` = build dir, repeat until the `.aux` bytes stop changing (2 passes today because of "Seite x von y"; pass 3 produced identical PDF and aux in the spike), cap at 3.
**When to use:** every document. Never run a single pass: a 1-pass PDF differs from a 2-pass PDF (`dba124f5…` vs `aaf74d92…`).
```python
# planspiel/texbuild.py  (sketch; flags, exit codes and the pass behaviour were spiked)
import os, subprocess
from pathlib import Path

LUALATEX = ["lualatex", "--disable-installer", "-interaction=nonstopmode",
            "-halt-on-error", "-file-line-error", "-recorder"]

class TexBuildError(RuntimeError): ...

def run_lualatex(job_dir: Path, tex_name: str, *, timeout_s: int = 300, max_passes: int = 3) -> Path:
    aux = job_dir / (Path(tex_name).stem + ".aux")
    previous = None
    env = {**os.environ, "SOURCE_DATE_EPOCH": "0", "FORCE_SOURCE_DATE": "1"}  # belt and braces only
    for _ in range(max_passes):
        try:
            proc = subprocess.run([*LUALATEX, tex_name], cwd=job_dir, env=env,
                                  stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=timeout_s)
        except subprocess.TimeoutExpired as exc:
            raise TexBuildError(f"{tex_name}: lualatex exceeded {timeout_s}s (hung?)") from exc
        if proc.returncode != 0:
            log = (job_dir / (Path(tex_name).stem + ".log")).read_text(encoding="utf-8", errors="replace")
            errors = [ln for ln in log.splitlines() if ln.startswith("!") or "not found" in ln][:10]
            raise TexBuildError(f"{tex_name} failed (exit {proc.returncode}):\n" + "\n".join(errors))
        current = aux.read_bytes() if aux.exists() else b""
        if current == previous:
            break
        previous = current
    return job_dir / (Path(tex_name).stem + ".pdf")
```
Timeout: use a generous 300 s per pass because the first run after a MiKTeX update re-indexes fonts (STACK.md). A missing package exits in about 1 s with exit 1 and `! LaTeX Error: File 'x.sty' not found.` (spiked). Do not scan stderr for "critical issue" (MiKTeX 23.10 prints "unsupported version of Windows" on Windows 11 but exits 0).

### Pattern 2: Preflight with the MiKTeX installer disabled (the bare call HANGS)
**What:** one `kpsewhich` call for all probe files; found files are printed, missing ones are absent.
```python
def missing_tex_files(probe_files: list[str]) -> list[str]:
    def call(flag):
        cmd = ["kpsewhich", *flag, *probe_files]
        return subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=30)
    proc = call(["--miktex-disable-installer"])
    if "unrecognized option" in proc.stderr:        # TeX Live: no installer, no hang
        proc = call([])
    found = {Path(line.strip()).name.lower() for line in proc.stdout.splitlines() if line.strip()}
    return [f for f in probe_files if f.lower() not in found]
```
Verified on MiKTeX 23.10.12: `kpsewhich tikzfill.image.sty` (no flag) hung until the 25 s timeout; with `--miktex-disable-installer` it returned in 1 s with exit 1; `--disable-installer` is **rejected** by `kpsewhich` ("unrecognized option") although it is correct for `lualatex`. A batch of five names took 1.0 s total (exit code was 2 for two missing files, but parse stdout instead of relying on it). Keep the 30 s timeout as the second guard, and kill-on-timeout message: "kpsewhich hung: MiKTeX installer dialog? Re-run with the installer disabled."

Probe list (file → MiKTeX package ID for `miktex packages install`), derived from what `planspiel.sty` and the template load:

| Probe file | MiKTeX package | Status here |
|------------|----------------|-------------|
| `fontspec.sty` | fontspec | installed |
| `ngerman.ldf` | babel-german | installed |
| `babel.sty`, `geometry.sty`, `xcolor.sty`, `array.sty` (tools), `tabularx.sty` (tools) | babel, geometry, xcolor, tools | installed |
| `colortbl.sty` | colortbl | **MISSING** (needed for header shading with `\rowcolor`) |
| `tikzfill.sty`, updated `tcolorbox` | tikzfill, tcolorbox | missing/old; **not needed for Phase 4**, needed by Phase 5 card skins |

Keep the list in one constant plus `print/miktex-packages.txt` (usable as `miktex packages install --package-id-file print/miktex-packages.txt`, a documented option per docs.miktex.org/manual/miktex-packages.html), and add a fast test that parses the `\RequirePackage`/`\usepackage` lines of `print/planspiel.sty` and the templates and asserts they are covered by the probe list, so the list cannot drift from the templates.

### Pattern 3: planspiel.sty skeleton (spiked: compiled, deterministic)
```latex
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{planspiel}[2026/10/20]
\pdfvariable suppressoptionalinfo 1023     % no dates, no producer, no /ID: byte-identical rebuilds
\RequirePackage[a4paper,left=3cm,right=1.5cm,top=1.6cm,bottom=2cm,footskip=9mm]{geometry}
\RequirePackage{fontspec}
\RequirePackage[ngerman]{babel}
\RequirePackage[table]{xcolor}             % loads colortbl
\RequirePackage{array,tabularx}
\setmainfont{Arial}
\definecolor{mhpblue}{HTML}{000099}
\definecolor{mhplight}{HTML}{CDD6FF}
\definecolor{mhpgrey}{HTML}{575757}
\newcommand{\ibox}[1]{\fcolorbox{mhpblue}{white}{\parbox[c][5.2mm][c]{#1}{\strut\hfill}}}  % fill-in box
\newcommand{\step}[2]{\par\vspace{1.6mm}\colorbox{mhpblue}{\parbox{\dimexpr\linewidth-2\fboxsep}{\color{white}\bfseries Schritt #1\quad #2}}\par\vspace{0.8mm}}
\InputIfFileExists{stamp.tex}{}{\def\footerstamp{OHNE STAND}}   % stamp lives OUTSIDE the hashed .tex
\makeatletter
\def\ps@planspiel{\let\@oddhead\@empty\let\@evenhead\@empty
  \def\@oddfoot{\parbox{\textwidth}{\small\color{mhpgrey}\rule{\textwidth}{0.4pt}\par\vspace{-2pt}%
      \footerstamp\hfill Seite \thepage\ von \pageref{LastPage}}}\let\@evenfoot\@oddfoot}
\AtEndDocument{\immediate\write\@auxout{\string\newlabel{LastPage}{{}{\thepage}}}}
\makeatother
\pagestyle{planspiel}
```
(The spike used `\textbf{}` in place of `\rowcolor` because `colortbl` is missing; `\RequirePackage[table]{xcolor}` fails fast until it is installed, which is exactly what the preflight reports.) `\AtEndDocument{\immediate\write...}` replaces `lastpage`; a first attempt with `\clearpage\label{LastPage}` left the reference undefined because the label landed on an unshipped page 3.

### Pattern 4: Print model carries exact values, template carries strings only
The model holds `Fraction`/int fields (exact) and a parallel list of display strings; the replay (PRINT-04) reads the exact fields, the template reads the strings, both from the same object (D-11). Printed derived numbers come from `rules.py` helpers (Pitfall 3). The model raises `PrintModelError` (build failure, D-06) when `base_severity != mitigation_cap` for a used attack or any tier `severity_multiplier != 1`. Suggested step structure (D-01, D-03, D-10), which is also the replay's order:

1. CIA table: base values plus rows (practical: 6, the spike filled one page at 6 mm rows)
2. E-Wert = C × w_c + I × w_i + A × w_a (weights from config)
3. Bonus table (rows from `bonus_measures`; reason text from `RevealView.attack(...)["bonus_reasons"]`) and Gesamtbonus
4. Gesamtreduktion = E-Wert + Gesamtbonus
5. Fall 1 / Fall 2 / Fall 3 block: Fall 1 and 2 print outcomes; Fall 3 prints `Schaden = (U − GR) × s_unit` and `KZ = kz_dmg + (GR − thr) × slope`. **Fall 1 damage is "before recovery"**: the sim multiplies damage by `(1 − r)` in every case when `allow_recovery`, so the Fall-1 line "Schaden: 160.000 €" is the pre-recovery value
6. Recovery step (only `allow_recovery`): table M4 level → r from `measures.M4.levels.*.recovery`, `Schaden nach Recovery = Schaden × (1 − r)`
7. KZ-Änderung = KZ Angriff + KZ Events, rounded half away from zero (D-10)

### Pattern 5: Jinja environment (from STACK.md, unchanged, still correct)
`\VAR{}`/`\BLOCK{}`/`\#{}` delimiters, `StrictUndefined`, `autoescape=False`, `finalize=tex_escape` where `tex_escape` rejects non-`str` values so a number can only reach the page through `fmt`. Do **not** enable `line_statement_prefix`. Write `.tex` with `write_text(..., encoding="utf-8", newline="\n")`. Add a lint test: no `+ - * /` inside `\VAR{...}` in `print/templates/*.j2` (Anti-Pattern 1 of ARCHITECTURE.md).

### Anti-Patterns to Avoid
- **Bare `kpsewhich` or bare `lualatex` in any scripted call** (hang risk). Always the installer-disabled flag plus a subprocess timeout.
- **Relying on `SOURCE_DATE_EPOCH`/`FORCE_SOURCE_DATE` for byte-identical output** (does not fix the trailer `/ID`; dates stay timezone-dependent). Use `suppressoptionalinfo`.
- **Building TeX strings in Python with non-raw literals** or via shell heredocs: `"\footerstamp"` becomes a form-feed + "ooterstamp", and a Bash heredoc swallowed `\\\hline` in this session. Use raw strings or Jinja files; add a test that the rendered `.tex` contains no control characters (`\x00-\x08\x0b-\x1f`).
- **A single lualatex pass** with "Seite x von y".
- **Hashing raw file bytes of text inputs** (CRLF vs LF under `core.autocrlf=true`; `simulation_config.json` is `w/crlf` in this working tree). The stamp hash covers rendered `.tex` strings and normalizes `\r\n`→`\n` for `planspiel.sty`.
- **Arithmetic in templates**, **prose with digits in `texte.toml`** (the digit lint is strict; see Pitfall 8).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Formulas for E-value, GR, damage, KZ, rounding | A second implementation in the print model for what the sim already does | `rules.py` helpers + `rounding.round_half_away_frac`; the *replay* is the one deliberate second encoding and lives in tests | single-definition guard and drift prevention |
| German money formatting | New thousands-dot code | `planspiel.review_text.format_eur` (reuse by import; moving it needs a guard-map update) | already tested, uses U+2212 |
| Revealed texts | Direct `Texts.get` of revealed keys | `RevealView` | the only access path decided in Phase 3 |
| Attack/plan enumeration for the slow replay | A new enumerator | `enumerate_tier(cfg, tier, on_outcome=cb)` / `TierKernel` | 782,336 valid combos per tier, 47.7 s measured with a no-op callback |
| Page x of y | `lastpage`/`zref` packages (missing locally) | `\AtEndDocument` label (Pattern 3) | zero extra packages |
| LaTeX escaping | Ad-hoc `.replace` calls | `tex_escape` as Jinja `finalize` | measure names contain `&` ("Logging & SIEM/MDR", "Backup & Disaster Recovery") |
| Reading which files TeX opened | Guessing the asset list | `lualatex -recorder` and parse `.fls` | proves the stamp hash covers every non-system file TeX read |
| PDF text checks | OCR or regex on raw PDF bytes | pypdf `extract_text` with whitespace-insensitive matching | see Pitfall 6 |

**Key insight:** the risky parts are all *environment* (installer dialog, PDF metadata, git state, line endings), not layout. Each has a small, verified countermeasure; none needs a library.

## Runtime State Inventory

Not applicable: this is a greenfield build pipeline, not a rename/refactor/migration phase. (Nothing stored, registered or cached under an old name. The only machine state touched is the user's MiKTeX installation by the D-17 checkpoint, which is covered in Environment Availability.)

## Common Pitfalls

### Pitfall 1: Bare `kpsewhich` (or any TeX binary) hangs on a missing package
**What goes wrong:** `kpsewhich tikzfill.image.sty` blocked for 25 s until the timeout; probing ~30 files bare hung the whole tool call. **Why:** `[MPM]AutoInstall=2` ("ask") opens an invisible GUI prompt. **Avoid:** `kpsewhich --miktex-disable-installer`, `lualatex --disable-installer`, `stdin=DEVNULL`, timeouts on every subprocess. **Warning sign:** a test run that "just sits there"; stray `kpsewhich.exe`/`lualatex.exe` processes (kill with `taskkill /F /IM kpsewhich.exe`).

### Pitfall 2: PDFs differ between two identical builds
**What goes wrong:** two builds differ even with `SOURCE_DATE_EPOCH` + `FORCE_SOURCE_DATE` (s1/s2 in the spike): the trailer `/ID` changes, and the date string is `D:20261019120525+02'00'` (local time). **Avoid:** `\pdfvariable suppressoptionalinfo 1023` in `planspiel.sty` (no dates/producer/ID). Optional extras: set `/Title` with `\pdfextension info {/Title (...)}` (kept; the Info dict then contains only what you set). **Verified:** identical hash for runs at different times, `TZ=Pacific/Auckland`, `SOURCE_DATE_EPOCH=1`, and with the line in the `.sty` instead of the preamble. **Also:** same pass count every time; changing font selection mode (`Arial` by name vs by `Path=`) changes bytes. **Warning sign:** `git status` shows PDFs changed after a rebuild with unchanged inputs.

### Pitfall 3: The existing single-definition guard rejects a naive print model
**What goes wrong:** `tests/test_single_definition.py::test_no_formula_operands_outside_rules_and_config` flags any `ast.Attribute` named `s_unit`, `base_severity`, `mitigation_cap`, `kz_at_full_damage`, `kz_at_full_mitigation`, `e_threshold`, `recovery`, `init`, `opex`, `weights`, `bonus`, `kz_per_step` in any file under `planspiel/` (and the root wrappers) except `rules.py` and `config.py`. A `printmodel.py` that reads `wave.e_threshold`, `attack.s_unit`, `level.recovery`, `bm.bonus` or even a model field named `.bonus`/`.weights` fails the fast suite. Also `test_formula_defined_once_in_rules` makes any second `def` with a guarded name fail (do not name a replay function `apply_attack`, `wave_kz_change`, ...). **How to avoid (pick in plan 03):** (a) put derived numbers (Obergrenze = `e_threshold + mitigation_cap`, full damage, slope, bounds) into new `rules.py` helpers returning a `NamedTuple` and register the new names in `FORMULA_FUNCTIONS`; (b) for *display-only* operand access (bonus rows, weights, recovery table) either add the helper to `rules.py` too or add `planspiel/printmodel.py` to the exemption tuple in that test (a conscious, documented change); (c) name model fields so they do not collide (`points`, `factor`, `w_c`, `unit_eur`, ...). Recommendation: (a)+(c), exemption only if (a) gets unwieldy.

### Pitfall 4: Two decimals "are enough" only if the order of operations is printed
See "D-09 proof". Rounding the slope first (2,43) flips cases on wave 3; so does dividing before multiplying. **Avoid:** hint text = "erst malnehmen, dann teilen; erst das Ergebnis auf zwei Nachkommastellen runden, die Steigung nicht vorher runden", plus a build-time guard (below).

### Pitfall 5: Page overflow splits fill-in lines or tables
**What goes wrong:** at 8.5 mm CIA rows the Angriff-1 content needs about 1.25 A4 pages; even at 6 mm rows the final step line wrapped onto a second page (about 1.04 pages). Automatic breaks fall mid-formula. **How to avoid:** decide the page structure deliberately: either tighten to a true single page (6 rows × 6 mm, footnotesize intros) or insert an explicit `\clearpage` after Schritt 3 (steps 1–3 = protection, page 2 = steps 4+ = damage/KZ). Wave 3 has no recovery step and 3 bonus rows, so it will fit one page, which makes page count differ per sheet; "Seite x von y" makes that harmless. Add a test: page count ≤ 2 (pypdf) and a visual check as a human-verify item (handwriting row height ≥ 6 mm).

### Pitfall 6: pypdf drops word spaces
**What goes wrong:** extracted text reads `DieAngreifer versuchen`, `undggf.exfiltriert`, `Schaden= (31 − GR )× 20.000 € =`, `KZ:−6`. Numbers, `−` (U+2212), `×`, `≤`, `≥`, `€`, `ß` and umlauts survive correctly; boxes (empty `\parbox`) contribute no text. **Avoid:** normalize both sides with `re.sub(r"\s+", "", s.replace("\u00a0", " "))` and assert **composite fragments** (`"(31−GR"`, `")×20.000€="`, `"KZ:−6"`, `"×17÷7"`), not bare digits (a lone `2` matches anywhere). The model should expose `printed_fragments()` for this check (D-11).

### Pitfall 7: Dirty detection and line endings
`git config core.autocrlf` is `true` here; `simulation_config.json` is `w/crlf` while the index is `lf`; `.gitattributes` only pins `content/*.toml` and `tests/golden/*.json` to LF. Add `print/** text eol=lf` (and `final_documents/generated/*.pdf binary`) so `planspiel.sty`/templates hash the same on any checkout; also normalize in the hash function. `git status --porcelain` is already CRLF-aware.

### Pitfall 8: Digit-free prose versus printed constants
`planspiel texts` fails on any digit in `texte.toml` prose outside the seven allowlisted tokens. The MHP wording "gerundet (ab ,5 vom Betrag aufrunden)" contains a `5`, "(1 / 2 / 3)" level hints contain digits, "Basiswert von 10" contains digits. **Avoid:** keep the words digit-free in `texte.toml` (e.g. `round_hint = "gerundet (ab {half} vom Betrag aufrunden)"`, filled in code with `fmt` from the rule constant) or take an explicit allowlist decision with a reason. There is no placeholder API in `Texts`; use `str.format` in the model on a digit-free template string.

### Pitfall 9: First lualatex run after a MiKTeX update is slow
luaotfload re-indexes fonts (STACK.md; the first spike run here took 3 s with an existing cache). Use a generous per-pass timeout (300 s) and let the smoke plan do a warm-up build before the reproducibility comparison.

### Pitfall 10: `-m 'not slow'` addopts and a new `pdf` marker
`pyproject.toml` has `addopts = "-m 'not slow' --strict-markers"` and only the `slow` marker. A `pdf` marker must be registered (strict markers) and excluded by default: `addopts = "-m 'not slow and not pdf' --strict-markers"`. Running `uv run pytest -m pdf` then replaces the default selection (last `-m` wins). Skip PDF tests when `shutil.which("lualatex") is None` or the preflight reports missing packages.

## Code Examples

### Stamp mechanics (git is the date source, never the wall clock)
```python
# planspiel/stamp.py (sketch; the git commands were run against this repo)
import hashlib, subprocess
from datetime import datetime, timezone

DATA_INPUTS  = ["simulation_config.json", "content", "print"]               # drive the DATE
BUILD_INPUTS = ["simulation_config.json", "content", "print", "planspiel",  # drive "+lokal"
                "pyproject.toml", "uv.lock"]                                # never the output dirs

def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True,
                          encoding="utf-8", timeout=30).stdout

def input_date_utc() -> str:
    ct = _git("log", "-1", "--format=%ct", "--", *DATA_INPUTS).strip()      # epoch of last commit touching data inputs
    return datetime.fromtimestamp(int(ct), tz=timezone.utc).strftime("%Y-%m-%d")

def is_dirty() -> bool:
    return bool(_git("status", "--porcelain", "--untracked-files=all", "--", *BUILD_INPUTS).strip())

def content_hash(tex: dict[str, str], static_files: dict[str, bytes]) -> str:
    h = hashlib.sha256()
    for name in sorted(tex):                                                # the rendered .tex, stamp excluded
        h.update(b"tex\0" + name.encode() + b"\0" + tex[name].encode("utf-8") + b"\0")
    for rel in sorted(static_files):                                        # planspiel.sty (CRLF->LF) and any asset TeX reads
        data = static_files[rel]
        if rel.endswith((".sty", ".tex", ".cls")):
            data = data.replace(b"\r\n", b"\n")
        h.update(b"file\0" + rel.encode() + b"\0" + data + b"\0")
    return h.hexdigest()

def stamp_text(digest: str, date: str, dirty: bool) -> str:
    return f"Stand {date} · {digest[:7]}{'+lokal' if dirty else ''}"
```
`%ct` converted to UTC avoids the committer's time-zone offset in the date. `git log -1 --format=%ct -- simulation_config.json content planspiel` returned `1792404325` (2026-10-19) on this repo; a path that does not exist yet (`print`) is accepted after `--`. `stamp.tex` is then written as `\def\footerstamp{<stamp text, tex-escaped>}` into the build dir **after** hashing, so the stamp can never feed back into the hash. Because the spike's `planspiel.sty` reads `stamp.tex` with `\InputIfFileExists`, the same file serves all three documents (one stamp per build, D-19).

Commit workflow consequence (confirmed by the mechanics): the date comes from the last commit touching the data inputs and "+lokal" appears while any build input is modified or untracked. A clean stamp therefore needs this order: commit inputs (config, texts, templates, `planspiel/`), run `uv run planspiel print`, then commit `final_documents/generated/`. Committing the PDFs changes no build input, so the stamp stays valid. Document this in the plan's verification step and in `--check`'s message.

`manifest.json` (D-20): `{"stamp": "...", "hash": "<full sha256>", "date": "YYYY-MM-DD", "dirty": false, "documents": {"angriff-1_ransomware": {"tex_sha256": "...", "pdf_sha256": "...", "pdf": "angriff-1_ransomware.pdf"}}}`. `--check`: render only, recompute hash/date/dirty, exit 0 if the recomputed stamp string equals the manifest's and every committed PDF's SHA-256 matches; exit 1 listing stale documents (and why) otherwise; exit 2 for environment errors. A manifest written while dirty carries "+lokal" and can therefore never match a clean checkout, which is the intended signal.

Hash-scope guard (cheap, proves D-19's "every asset file TeX reads"): after the build, parse `<job>.fls` (written by `-recorder`) and assert every `INPUT` line that is relative (`.\x`) or inside the build dir is in `{<job>.tex, planspiel.sty, stamp.tex, <job>.aux}` ∪ hashed assets. System files (MiKTeX tree, `C:\WINDOWS\Fonts`) are absolute paths outside the build dir. `-recorder` did not change the PDF bytes in the spike.

### Fast grid replay (prototype, 148,952 points, 0 mismatches, 2.2 s)
```python
# Drive the sim at an exact GR without touching production code: put all of E into C with a Fraction CIA.
w_nobonus = dataclasses.replace(wave, bonus_measures=[])
cia = {"c": gr / wave.weights["c"], "i": Fraction(0), "a": Fraction(0)}         # e_value_scaled accepts integral Fractions
sim = rules.apply_attack({"M4": m4_level}, cfg.measures, attack, w_nobonus, cia, cfg.ws, cfg.rs)
change = rules.wave_kz_change(sim["kz_delta"], event_kz)
# worksheet replay reads only the print model (exact fields), in printed step order:
#   E = c*w_c + i*w_i + a*w_a ; GR = E + total_bonus ; Fall by thresholds ; damage = (U-GR)*unit ;
#   KZ = kz_dmg + (GR-thr)*slope ; damage *= (1 - r) if recovery step ; change = round_half_away(KZ + events)
assert replay.damage_eur == sim["damage"] * 1000 and replay.change == change
```
The bonus table is tested separately and cheaply: for every bonus measure and every level 0..3 the printed "Ab Level" rule (`level >= min_level`) must equal `compute_bonus_reduction`; for every subset the printed Gesamtbonus is the sum. Running bonus subsets × the full GR grid adds nothing, because the sim only sees GR; D-12's "every bonus subset" is satisfied by the subset test plus the `GR = E + bonus` step inside the grid.

### `apply_attack` result-key guard (D-21)
```python
REPLAYED = {"e_value", "bonus_reduction", "gesamtreduktion", "damage", "kz_delta", "recovery_factor"}
DERIVED_NOT_PRINTED = {"capped_reduction", "severity", "effective_base_severity"}  # intermediates implied by the replayed steps
UNPRINTED_UNSCORED = {"cia_delta"}                                                   # D-21, named explicitly

def test_apply_attack_returns_only_known_keys(cfg):
    result = rules.apply_attack(sel, cfg.measures, attack, wave, cia, cfg.ws, cfg.rs)
    assert set(result) == REPLAYED | DERIVED_NOT_PRINTED | UNPRINTED_UNSCORED
```
(Keys of `apply_attack` today: `e_value, bonus_reduction, gesamtreduktion, capped_reduction, effective_base_severity, severity, damage, kz_delta, cia_delta, recovery_factor`.) Add **negative controls** so SC3 is demonstrated, not assumed: monkeypatch `rules.compute_recovery` (+0,1), `rules.attack_kz_delta` (+1) or `rules.compute_bonus_reduction` (+1) and assert the comparison helper reports mismatches.

## D-09 proof (rounding with two decimal places)

**Setup.** Per-wave KZ change = `round_half_away(KZ_attack + event_kz)` with `event_kz` an integer, so only the fractional part of `KZ_attack` matters. In Fall 3, `KZ_attack = kz_dmg + slope × (GR − thr)`.

**Reachable GR lattice** (all values exact, `cfg.ws = 10`):

| Wave | Weights (c,i,a) | E denominators | Min step of reachable GR | Distinct reachable GR (all 4^10 CIA, superset) | Bonus sums | Slope | Fall 3 interval |
|------|-----------------|----------------|--------------------------|--------------|------------|-------|-----------------|
| 1 ransomware | 2/5, 2/5, 1/5 | 1, 5 | 0,2 | 295 (39 inside Fall 3) | 0,3,6,9,12,15 | 2 | (23, 31) |
| 2 ot | 1/5, 1/5, 3/5 | 1, 5 | 0,2 | 282 (49) | 0,6,9,15 | 6/5 | (20, 30) |
| 3 exfil | 1/2, 3/10, 1/5 | 1, 2, 5, 10 | 0,1 | 643 (69) | 0,6,8,9,14,15,17,23 | 17/7 | (25, 32) |

GR is always a multiple of 1/10 (bonus values are integers), so E-value and GR need at most one decimal place on the sheet, and a 0,1 grid is never coarser than the lattice (`1/cfg.ws`).

**Event-KZ values** per wave (enumerated over all 4^10 selections; the dependency-valid subset omits only `2` from wave 2):
- wave 1: {0}
- wave 2: {−20, −10, −5, −2, 0, 2, 3, 5, 7, 8, 12, 15, 18, 22}
- wave 3: {−10, −5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50}

**KZ_attack on the full 0,1 lattice inside Fall 3** (superset of reachable):
- wave 1: multiples of 0,4 on reachable GR (denominators 1, 5), minimal distance to a half-integer 0,1 → exact within one decimal;
- wave 2: denominators 1, 5, 25, i.e. exact within two decimals; minimal nonzero distance to a half-integer 1/50 = 0,02;
- wave 3: denominators {2, 5, 7, 10, 14, 35, 70}; minimal nonzero distance to a half-integer **1/70 ≈ 0,0143**; exactly one lattice point lands exactly on a half (GR − 25 = 3,5 → 17 × 3,5 ÷ 7 = 8,5 → KZ_attack = 1,5).

**Result.** Rounding to two places moves a value by at most 0,005; truncating moves it by less than 0,01. Both are smaller than 1/70, so neither can cross a half-integer boundary; the exact-half point is representable (1,50). Brute force over every 0,1 GR step from the lower bound to the cap × every event-KZ value above (checks: 81 + 1,414 + 923): **0 flips for `trunc2` and `round2`** on all three waves, so truncating or rounding the *result* to two places is safe. Contrast (wave 3, same grid): rounding the slope to 2,43 first flips **2** cases (first at GR − 25 = 3,5), truncating the slope to 2,42 flips **37**, and dividing by 7 before multiplying by 17 (rounded to two places) flips **78**.

**Consequence for the sheet:** the hint must read, in German and digit-free, along the lines of "Rechnet zuerst × (Zähler), dann ÷ (Nenner); rundet erst das Ergebnis auf zwei Nachkommastellen, nicht die Steigung." For slopes that are integers or terminating decimals (waves 1 and 2) no hint is needed beyond "ganze Zahl oder höchstens zwei Nachkommastellen". **Build-time guard (add to the print model):** for every wave compute the exact KZ_attack values on the 1/ws lattice in Fall 3; require the minimal nonzero distance to a half-integer to exceed 10^-2 (otherwise two places are not enough: raise `PrintModelError` naming wave and distance). Add a fast unit test replicating the brute-force above so a future config change that breaks the hint fails the suite instead of the table.

## Reproducibility (D-14, D-15, D-19)

Everything below was measured with two builds per row, 2 passes each, MiKTeX 23.10.12 / LuaHBTeX 1.17.0, same machine.

| Variant | Result |
|---------|--------|
| nothing set | different bytes |
| `SOURCE_DATE_EPOCH` only | different bytes |
| `SOURCE_DATE_EPOCH` + `FORCE_SOURCE_DATE=1` | **different bytes** (trailer `/ID` differs; dates are local time `+02'00'`) |
| `\pdfvariable trailerid {[<hex> <hex>]}` + `SOURCE_DATE_EPOCH` + `FORCE_SOURCE_DATE=1` | identical (dates still carry the local offset) |
| `\pdfvariable suppressoptionalinfo 1023` (preamble or in the `.sty`) | **identical**; independent of time, `TZ=Pacific/Auckland`, `SOURCE_DATE_EPOCH`; no Producer/CreationDate/ID in the file; `/Title` set via `\pdfextension info` survives |
| `suppressoptionalinfo` 511 (everything except the ID bit) | different bytes |
| 1 pass instead of 2 | different bytes (page x of y) |
| `\setmainfont{Arial}` vs `Path=C:/Windows/Fonts/` | each deterministic, but different bytes |

Also verified: `-recorder` leaves the bytes unchanged; Arial resolves from `C:/WINDOWS/Fonts/arial.ttf` (dated 2026-05-27, so a Windows update can change the embedded font data: accepted by D-16, but the SC1 test must always compare two builds on the same machine). luaotfload's name/font caches only affect speed in these runs [ASSUMED: a cache wipe was not tested to avoid touching user state]. `latexmk` is not needed: the document has no bibliography or index, and two direct passes reach a fixed point.

## Equivalence test design (D-10 to D-12, D-21)

- **Fast test (grid):** per wave, GR from `lower − 3` to `upper + 3` at step `1/cfg.ws` (boundaries `lower` and `upper` included; both Fall 1 and Fall 2 are tested at exact equality) × M4 level 0..3 (`recovery` factor only where `allow_recovery`) × event-KZ values. For the event axis use a **conservative integer range per wave** built from per-event extrema (tier-dict min/max, `count × kz_per_measure` for `level_bonus_per_measure`, `{0, kz_delta}` for `and_condition`) and fail loudly on an unknown event type; this avoids the 14.4 s brute-force over 4^10 selections that an exact event-KZ set costs. The exact sets above are still checked once in the slow tier. Measured prototype cost: 148,952 comparisons in 2.2 s (current fast suite: 873 tests, 35 s).
- **Fast test (bonus table):** table rows equal `bonus_measures` (measure, min level, points) and the printed rule equals `compute_bonus_reduction` for all levels and subsets; step 2 (E-value from a CIA triple and weights) is checked over all reachable CIA triples (7,971 in the DP superset) against `e_value_scaled`.
- **Slow test (`-m slow`):** call `enumerate_tier(cfg, tier, on_outcome=cb)`; for each valid plan decode its selection, replay the three waves through the worksheet steps, chain `clamp 0..100` from `tier.kz_start` (clamping lives on the Phase-5 tracking sheet, so the *test* applies it to compare against `kz_after`), and compare each wave's `kz_after` entry and the summed `damage_eur`. Enumeration alone is 47.7 s per tier (measured, medium); budget about 1–2 min per tier with the replay [ASSUMED], memoizing the replay on `(wave, cia, bonus total, recovery, event_kz)` if needed. All tiers share `severity_multiplier == 1` today, but the D-06 guard makes that a build precondition anyway.
- **Mechanic coverage:** `apply_attack` key guard and negative controls (see Code Examples). Also assert the per-wave sim events apply no KZ beyond what the sheet's "KZ Events" input represents (the sheet takes the event KZ sum as an input; `apply_events` supplies it in the sim).
- **PDF text test (`pdf` marker):** build the three worksheets once (session fixture), pypdf-extract, normalize whitespace, assert every `printed_fragments()` string and the stamp text appear and that page count ≤ 2; assert the footer stamp is on **every** page.
- **SC2 test (fast, no TeX):** copy the config to `tmp_path`, change `waves[0].e_threshold`, render `.tex`, assert the new number appears and the old one is gone with no template edit.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hand-maintained Angriff docx with three KZ formula variants | One generated formula shape with exact slope (D-07/D-08) | this phase | removes the Fall-3 sub-formula contradiction in the old sheets |
| Printed sheet silent on weights and recovery | Weights in the E-step and an explicit recovery step (D-02/D-03) | this phase | every sim mechanic has a printed home |
| `SOURCE_DATE_EPOCH` for reproducible PDFs (pdfTeX lore) | `\pdfvariable suppressoptionalinfo` on LuaTeX | verified here | `SOURCE_DATE_EPOCH` alone is insufficient on LuaHBTeX 1.17 / MiKTeX 23.10 |
| `latexmk` as build driver (STACK.md) | direct `lualatex` + Python pass loop | this research | no Perl dependency, clean timeout handling |

**Deprecated/outdated within this project's own research:**
- ARCHITECTURE.md "Reproducible PDFs (verified locally)": its claim that `SOURCE_DATE_EPOCH` + `FORCE_SOURCE_DATE` yields identical hashes did not reproduce on a Jinja-free spike here (differing trailer `/ID`).
- ARCHITECTURE.md "Freshness flow" hash scope (`planspiel/*.py` in the hash): superseded by D-19 (rendered content hash).
- STACK.md package need for `tabularray`, `ninecolors`, `siunitx`, and `tikzfill` in Phase 4: not required by the worksheet design.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `--miktex-disable-installer` for `kpsewhich` stays valid after the MiKTeX update (verified only on 23.10.12; not in the published manual) | Pattern 2 | Preflight would report "unrecognized option"; the retry-without-flag fallback would then hang on a missing package. Re-run the smoke gate after the update; the 30 s timeout is the backstop. |
| A2 | Latest MiKTeX is 25.12 (miktex.org/download, fetched 2026-10-20) while Wikipedia lists 26.5 (2026-05-14) | Standard Stack | Wrong version number in the user checkpoint text; harmless, say "current" and let the user read MiKTeX Console |
| A3 | `suppressoptionalinfo 1023` behaves the same on TeX Live LuaTeX | Reproducibility | Only matters if someone builds elsewhere; D-16 already limits byte-identity to the same machine |
| A4 | luaotfload cache state does not change output bytes (only speed) | Reproducibility | Two builds on the same machine could still differ after a cache rebuild; mitigated by the SC1 test comparing two builds |
| A5 | Slow replay costs about 1–2 min per tier | Equivalence test design | Slow suite longer than expected; mitigate with memoization |
| A6 | `miktex packages install colortbl` works on 23.10 without an update | Environment Availability | Possible that the repository demands the update first; the checkpoint already covers the update |
| A7 | Windows updates can change Arial's bytes (arial.ttf dated 2026-05-27 here) | Reproducibility | Affects only cross-time/cross-machine byte identity, accepted in D-16 |
| A8 | One A4 page at 6 mm handwriting rows is achievable for wave 1/2 only after trimming; otherwise an explicit page break after Schritt 3 | Pitfall 5 | Layout decision slips into execution; keep it a plan-level decision with a visual human-verify item |

## Open Questions

1. **One page or two?**
   - What we know: with 6 CIA rows at 6 mm the Angriff-1 content is about 1,04 A4 pages; at 8,5 mm rows about 1,25 pages. Wave 3 (no recovery step, same bonus row count) fits one page.
   - What's unclear: whether 6 mm handwriting rows are acceptable on paper.
   - Recommendation: build the template for a deterministic 2-page split at Schritt 3 if one page cannot hold ≥ 7 mm rows; keep the page count ≤ 2 test; make the final choice a human-verify item after printing one sheet.
2. **Does the MiKTeX update remain worthwhile (D-17)?**
   - What we know: only `colortbl` is missing for the Phase-4 design; the installed 23.10 prints an "unsupported Windows" line and is nearly three years old; Phase 5 will need `tikzfill` + current `tcolorbox`.
   - Recommendation (CONTEXT wins): keep the update checkpoint and install `colortbl` and `tikzfill` in the same session so Phase 5 needs no second user action; drop `tabularray`, `ninecolors`, `siunitx` from the list unless a Phase-5 plan asks for them. The user may alternatively skip the update and install `colortbl` alone (A6, untested).
3. **Where do display-only operands live (Pitfall 3 option b)?** A conscious call between "all operand reads via `rules.py` helpers" and "exempt `printmodel.py` in the guard". Recommendation in Pitfall 3; the plan author decides.
4. **PDF file naming:** recommend ASCII job/file names from ids (`angriff-1_ransomware`, `angriff-2_ot`, `angriff-3_exfil`) to keep TeX job names free of umlauts; display names come from `RevealView`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| uv | all `uv run` commands | ✓ | 0.12.5 | — |
| LuaHBTeX / `lualatex` (MiKTeX) | PDF build | ✓ | 1.17.0 / MiKTeX 23.10.12 | none (blocks PRINT-01) |
| `kpsewhich` (MiKTeX) | preflight | ✓ (hangs without `--miktex-disable-installer`) | 23.10.12 | probe via a one-package `lualatex --disable-installer` compile (slower, one package at a time) |
| `colortbl.sty` | header shading | ✗ missing | — | unshaded headers (bold + rules); user installs via MiKTeX (checkpoint) |
| `tikzfill.sty`, current `tcolorbox` | Phase 5 cards only | ✗ missing / 6.1.0 | — | not needed in Phase 4 |
| `tabularray`, `ninecolors`, `siunitx`, `fancyhdr`, `lastpage` | not used | ✗ missing | — | not needed (replaced by `tabularx`, own footer, `\AtEndDocument` label) |
| Arial (`C:\Windows\Fonts\arial.ttf` and bold/italic) | D-16 | ✓ | file dated 2026-05-27 | none by decision |
| Perl (Git for Windows `usr\bin\perl.exe`, Strawberry Perl) | only latexmk | ✓ | 5.36 | not used |
| git | stamp | ✓ | present | `--check`/stamp fails clearly when not a git checkout |
| `pdftoppm` (MiKTeX poppler) | optional visual check | ✓ | bundled | Inkscape PDF import |
| Jinja2, pypdf | render, tests | ✗ not in `pyproject.toml` | — | `uv add` (see Installation) |

**Missing dependencies with no fallback:** none (all gaps are user-installable or avoidable).
**Missing dependencies with fallback:** `colortbl` (unshaded headers). The MiKTeX update and package install are a user action (checkpoint); the executor must not run `miktex packages install` or update MiKTeX silently. Any compile in verification must use `--disable-installer` with a timeout.

## Validation Architecture

> `workflow.nyquist_validation` is `true` in `.planning/config.json`.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (existing); markers `slow` (existing) and new `pdf` |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`: change `addopts` to `-m 'not slow and not pdf' --strict-markers`, add `pdf` marker) |
| Quick run command | `uv run pytest tests/test_print_*.py tests/test_worksheet_equivalence.py -x -q` |
| Full suite command | `uv run pytest` (fast) then `uv run pytest -m slow` and `uv run pytest -m pdf` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PRINT-01 | Preflight reports missing probe files from fake `kpsewhich` output; flag fallback logic | unit | `uv run pytest tests/test_print_preflight.py -x` | ❌ Wave 0 |
| PRINT-01 | Pass loop stops when aux is stable; missing-package log is surfaced; timeout raises `TexBuildError` | unit (fake runner) | `uv run pytest tests/test_print_driver.py -x` | ❌ Wave 0 |
| PRINT-01 | Smoke doc builds twice → identical PDF bytes; a doc requiring a non-existent package fails in < 60 s with exit ≠ 0; an infinite-loop doc is killed by the timeout | integration | `uv run pytest -m pdf tests/test_print_smoke.py` | ❌ Wave 0 |
| PRINT-11 | Hash ignores stamp text and is stable; changes when a `.tex`/sty/asset changes; CRLF-insensitive | unit | `uv run pytest tests/test_print_stamp.py -x` | ❌ Wave 0 |
| PRINT-11 | Date = UTC date of last commit of data inputs; "+lokal" on modified/untracked build inputs but never from output dirs (temp git repo fixture) | unit (git) | `uv run pytest tests/test_print_stamp.py -x` | ❌ Wave 0 |
| PRINT-11 | `--check`: fresh manifest → exit 0; edited `.tex`/config → exit 1 listing stale docs; no TeX invoked | unit | `uv run pytest tests/test_print_stamp.py -x` | ❌ Wave 0 |
| PRINT-11 | Every page of every built PDF contains the stamp text; `.fls` inputs ⊆ hashed set | integration | `uv run pytest -m pdf tests/test_print_worksheets_pdf.py` | ❌ Wave 0 |
| PRINT-03 | Print model values equal config-derived numbers (thresholds, caps, bonus rows, weights, recovery table, Fall outcomes); D-06 guards raise on broken invariants; slope printing rules (D-08) | unit | `uv run pytest tests/test_print_model.py -x` | ❌ Wave 0 |
| PRINT-03 | Templates render under `StrictUndefined`; no arithmetic in `\VAR{}`; no control chars; LaTeX specials escaped; changing `e_threshold` in a temp config changes the printed number (SC2) | unit | `uv run pytest tests/test_print_render.py -x` | ❌ Wave 0 |
| PRINT-03 | New wording passes `planspiel texts` (digit-free) | unit | `uv run planspiel texts` | ✅ existing command |
| PRINT-03 | Built PDFs: page count ≤ 2, `printed_fragments()` present (whitespace-insensitive) | integration | `uv run pytest -m pdf tests/test_print_worksheets_pdf.py` | ❌ Wave 0 |
| PRINT-04 | Fast grid: replay == `rules` for every wave/GR/M4/event-KZ; bonus-table and E-step equivalence | unit | `uv run pytest tests/test_worksheet_equivalence.py -x` | ❌ Wave 0 |
| PRINT-04 | `apply_attack` key guard; negative controls fail as expected; D-09 hint-validity brute force | unit | `uv run pytest tests/test_worksheet_equivalence.py -x` | ❌ Wave 0 |
| PRINT-04 | Slow replay of all enumerated plans per tier | slow | `uv run pytest -m slow tests/test_worksheet_equivalence_full.py` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** quick run command (no TeX, a few seconds)
- **Per wave merge:** `uv run pytest` (fast suite, must stay green: 873 tests today) plus `uv run planspiel validate` and `uv run planspiel texts`
- **Phase gate:** fast suite + `uv run pytest -m slow tests/test_worksheet_equivalence_full.py` + `uv run pytest -m pdf` + `uv run planspiel print` followed by `uv run planspiel print --check`; one printed sheet reviewed by a human (page fit, handwriting space)

### Wave 0 Gaps
- [ ] `tests/test_print_preflight.py`, `test_print_driver.py`, `test_print_smoke.py`, `test_print_stamp.py`, `test_print_model.py`, `test_print_render.py`, `test_print_worksheets_pdf.py`, `test_worksheet_equivalence.py`, `test_worksheet_equivalence_full.py`
- [ ] `pyproject.toml`: `pdf` marker, `addopts` update, `jinja2==3.1.6` dependency, `pypdf==6.19.0` dev dependency (+ `uv.lock`)
- [ ] `.gitignore`: `build/`; `.gitattributes`: `print/** text eol=lf`, `final_documents/generated/*.pdf binary`
- [ ] `tests/test_single_definition.py`: register new `rules.py` helper names; decide on the `printmodel.py` exemption (Pitfall 3)
- [ ] A `tests/support` helper for a temp git repo (stamp tests) and a session-scoped "built worksheets" fixture skipped when no TeX engine/preflight failure

## Security Domain

> `security_enforcement` is enabled (`security_asvs_level: 1`).

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | offline CLI, no accounts |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | `tex_escape` as Jinja `finalize` (config/text strings are untrusted-ish LaTeX input), `StrictUndefined`, config validator before render; model guards (D-06, D-09) fail the build on invalid data |
| V6 Cryptography | partial | SHA-256 from `hashlib` for the content stamp only; integrity not secrecy, nothing hand-rolled |
| V12 Files/Resources | yes | write `.tex` as UTF-8/LF into the gitignored build dir; copy PDFs only to `final_documents/generated/`; no path derived from config strings (use ids) |
| V14 Config / supply chain | yes | `jinja2`/`pypdf` pinned in `uv.lock`; human-verify checkpoint (seam SUS verdicts); TeX packages only from the MiKTeX repository by the user |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| LaTeX injection through config/texts (`\input`, `\write18`, `\immediate\write`) | Tampering / Elevation | escape every string via `tex_escape` (non-`Tex` values only); lualatex restricted shell ("restricted system commands enabled" in the banner); never pass user strings as TeX control sequences |
| Command injection via subprocess | Tampering | argument lists, no `shell=True`; fixed command names; paths only from the repo |
| Hung/zombie TeX processes (denial of service) | Denial of Service | `--disable-installer`, `stdin=DEVNULL`, timeouts, error surfaced instead of waiting |
| Stale or mixed printouts treated as current | Repudiation / Information | content-hash stamp on every page, committed manifest, `--check` |
| Slopsquatted PyPI packages | Tampering | legitimacy audit above, pins, human-verify checkpoint |

## Suggested Plan Decomposition (one requirement = one plan)

| Plan | Requirement | Scope | Owns (shared pieces) |
|------|-------------|-------|----------------------|
| 04-01 | PRINT-01 | Smoke gate: `texbuild.py` (preflight, runner, pass loop, timeout), `print/planspiel.sty` base (fonts, geometry, hardening, `\footerstamp` slot, footer, LastPage), `planspiel print` skeleton building a tiny smoke document, tests incl. reproducibility (two builds identical), fail-fast and timeout; deps + markers + `.gitignore`; **user checkpoint**: MiKTeX update and `colortbl`/`tikzfill` install, then re-run the smoke gate | `texbuild.py`, `.sty` hardening, `print/miktex-packages.txt`, pass-count rule |
| 04-02 | PRINT-11 | `stamp.py` (content hash, UTC commit date, scoped dirty, `stamp.tex`, `manifest.json`, `--check`, `-recorder` hash-scope guard), footer text wired; developed against the smoke document through a `render_all()` interface that PRINT-03 plugs into; `.gitattributes` | commit-date logic and `render_all()` contract (PRINT-01 deliberately does **not** need the commit date, since `suppressoptionalinfo` removes dates; keep `SOURCE_DATE_EPOCH` a constant) |
| 04-03 | PRINT-03 | `rules.py` derived-constant helpers (+ guard registration), `printmodel.py`, `fmt.py`, `render.py`, `angriff.tex.j2`, `[sheets.angriff]`/`[sheets.labels]` additions (digit-free), D-06/D-09 guards, three worksheets built into `final_documents/generated/`, PDF fragment tests, one human-verify print check | model and `printed_fragments()` |
| 04-04 | PRINT-04 | replay over the model, fast grid, bonus/E-step tests, key guard, negative controls, hint-validity brute force, slow full replay, pdf text check wiring | test helpers (event-KZ extrema, GR lattice, Fraction-CIA driver) |

Ordering: 01 → 02 → 03 → 04 (04 needs 03's model; 02 can run against the smoke document so it does not wait for 03). ROADMAP success criterion 1 ("rebuilds the attack worksheets") is only fully demonstrable once 03 lands; verify SC1 at phase end with the real worksheets, and verify the mechanism in 01 with the smoke document.

## Sources

### Primary (HIGH confidence)
- Local spikes on this machine, 2026-10-20 (MiKTeX 23.10.12, LuaHBTeX 1.17.0, Windows 11 build 26200): `kpsewhich` hang and flag behaviour, package probes, `lualatex --disable-installer` fail-fast (exit 1, ~1 s), worksheet page compile (2.3 s/pass), reproducibility matrix, `-recorder`, pypdf 6.19.0 extraction, git stamp commands, `enumerate_tier` timing (47.7 s), fast suite baseline (873 passed, 35 s). Spike files live in the session scratchpad `phase4-spike/` (not in the repo).
- Brute-force/analysis scripts run through `uv run` against the repo: GR lattice, event-KZ sets, rounding flips (D-09), prototype replay (148,952 points, 0 mismatches).
- Repo sources: `planspiel/rules.py`, `rounding.py`, `config.py`, `texts.py` (`RevealView`), `review_text.py`, `validate.py`, `enumerate.py`, `cli.py`, `tests/test_single_definition.py`, `pyproject.toml`, `.gitattributes`, `content/texte.toml`, `content/digit_allowlist.toml`, `content/assets/GUIDELINES.md`, `final_documents/Angriff-1_Ransomware.docx` (text structure).
- PyPI JSON API: jinja2 3.1.6, pypdf 6.19.0/6.21.1, markupsafe 3.0.3/3.0.4 (versions, dates).

### Secondary (MEDIUM confidence)
- [MiKTeX download page](https://miktex.org/download): Windows installer 25.12 (2025-12-31), fetched 2026-10-20 [CITED].
- [MiKTeX manual, TeX features](https://docs.miktex.org/manual/texfeatures.html): `--disable-installer` / `--enable-installer` for the engines [CITED].
- [MiKTeX manual, miktex](https://docs.miktex.org/manual/miktex.html) and [miktex-packages](https://docs.miktex.org/manual/miktex-packages.html): `miktex packages install [--package-id-file <file>] <package-id...>`, `check-update`, `update`, `upgrade` [CITED].
- [MiKTeX on Wikipedia](https://en.wikipedia.org/wiki/MiKTeX): lists 26.5 (2026-05-14) as stable; conflicts with the download page (A2) [CITED, low weight].
- Existing project research: `.planning/research/STACK.md`, `ARCHITECTURE.md`, `PITFALLS.md` (Pitfall 9, 12, 13) as the starting point; deviations noted under State of the Art.

### Tertiary (LOW confidence)
- None used for load-bearing claims.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, every tool and flag was exercised locally; PyPI versions checked live (SUS seam verdicts are heuristic, see audit).
- Architecture: HIGH for driver, stamp and equivalence design (prototyped); MEDIUM for module boundaries around the single-definition guard until the plan chooses option (a) or (b).
- Pitfalls: HIGH, each pitfall was reproduced or read from the repo guard code.
- Layout: MEDIUM, one hand-written Angriff-1 page; the Jinja-generated pages and a printed sheet still need a human check.

**Research date:** 2026-10-20
**Valid until:** 2026-11-19 for the toolchain findings (MiKTeX version drift after the user's update can change flag names and package availability: re-run the smoke gate then); config-dependent numbers (lattice, event-KZ sets, flip counts) are valid until `simulation_config.json` changes (Phase 6 rebalance: re-run the brute force through the new hint-validity test).
