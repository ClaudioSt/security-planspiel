# Stack Research

**Domain:** Config-driven generation of print-ready, German-language game material (A4 worksheets with fill-in tables, cut-out card sheets, tracking sheet) from `simulation_config.json`, plus test tooling for the Python simulation
**Researched:** 2026-09-29
**Confidence:** HIGH for versions and the local-environment findings (checked against the PyPI JSON API and CTAN, and by compiling on this machine); MEDIUM for layout-package choices (the spikes compiled, but no full card sheet was built)

---

## Read This First: Four Findings That Change the Plan

These came from running things on this machine. They were not visible in `PROJECT.md` or `.planning/codebase/STACK.md`.

1. **"Python 3.12" is Inkscape's bundled Python.** In Git Bash, `python` resolves to `C:/Program Files/Inkscape/bin/python.exe` (MinGW build 3.12.9, **no pip**, and `python -m venv` produces a broken `bin/`-layout venv). `pip` belongs to a *different* interpreter: Microsoft Store CPython **3.11.7**. That interpreter has Jinja2 3.1.2, pytest 9.0.2, python-pptx 1.0.2, openpyxl 3.1.5 and python-docx 1.2.0 installed. So **Jinja2 is installed after all**, but only for the Store Python that `pip` targets, not for the Inkscape `python` that Git Bash runs. Which interpreter a script gets depends on how it is invoked. **Fix:** a project-local venv, with every command run through it (uv, see below). Confidence: HIGH (verified locally).
2. **MiKTeX is three years stale, and its package installer hangs headless builds.** Installed: MiKTeX 23.10.12, last updated 2023-12-10. Latest is 25.12 (2025-12-31). `[MPM]AutoInstall=2` ("ask") opens a GUI dialog when a package is missing. A `latexmk` run started from Python sat there **until killed** (two orphaned `lualatex`/`kpsewhich` processes had to be terminated). Missing locally: `tikzfill` (required by tcolorbox's `skins` library and by `[most]`), `tabularray`, `ninecolors`, `colortbl`, `siunitx`. With `lualatex --disable-installer` the same build fails in about 13 s with `File 'tikzfill.image.sty' not found` instead of hanging. Confidence: HIGH (verified locally).
3. **The config's German text uses ASCII transliterations.** Examples: `"Massnahmenwechsel"`, `"Geschaeftsfuehrung"`, `"Operative Unterstuetzung"`, `"prueft"`, `"Stoerung"`. Printed material would show "ae/oe/ue/ss". Every display string in `simulation_config.json` needs to become proper UTF-8 German (`ä ö ü ß €`) before generation. IDs (`M1`, `kurswechsel`) stay ASCII. The existing loaders already use `encoding="utf-8"`, so the simulation is unaffected. Confidence: HIGH (grep of config).
4. **Config strings contain LaTeX special characters.** There are 9 occurrences of `&` (`"Logging & SIEM/MDR"`, `"Backup & Disaster Recovery"` and others), plus `_` in IDs and `%`/`€` in descriptions. Without escaping, any LaTeX template breaks on the first measure card. Confidence: HIGH (grep plus a Jinja spike that reproduced it).

---

## Decision Flag: LaTeX vs. Typst (please decide before the generation phase)

`PROJECT.md` records "Print material generated via LaTeX → PDF" as decided (2026-09-29). The goals behind that decision were no manual print-sync and precise print layout. Both are fully met by **Typst**, and on this repo Typst is simpler to run and maintain. Per the user's decision-making rule, this is flagged rather than silently followed or silently overruled.

| Criterion | LaTeX (LuaLaTeX + Jinja2 + latexmk) | Typst (PyPI `typst` binding) |
|---|---|---|
| Install | Update MiKTeX 23.10 → 25.12, add ~6 packages, Perl needed for latexmk (Git/Strawberry Perl present) | `uv add typst`. A single wheel with no system dependencies, so it goes into the lockfile like any other dependency |
| Data → document | Python renders `.tex` source with Jinja2. Every string must be LaTeX-escaped (bug class #1) | Python writes a JSON view-model and the template reads it with `json()`. Data never becomes source code, so **no escaping exists** |
| Spike on this machine | `latexmk -lualatex`, 3 tcolorbox cards + tabularx, Arial, umlauts/€: **~30 s**, OK | `typst.compile()`, same content: **~2.5–3.8 s** warm (11.8 s first run while scanning system fonts), OK. `Logging & SIEM`, `_#$%`, umlauts and € printed verbatim |
| Card grid / fill-in tables | tcolorbox raster / tabularray: mature, very capable | Built-in `grid`/`table` with fixed `rows: 88mm` and `stroke`. Enough for cards and worksheets |
| Hand-written formulas on worksheets | Excellent | Good (`$C dot w_C + I dot w_I$`) |
| Stability | Decades-stable | 0.x (0.15.1 as of 2026-07-17). Breaking changes between minors, so **pin the exact version** |
| User familiarity | High (user writes LaTeX for university) | New syntax to learn |

**Recommendation:** If the user is open to it, **switch the renderer to Typst**: fewer moving parts, no escaping bug class, 10× faster builds, reproducible via the lockfile. If the user prefers LaTeX (familiarity, tcolorbox polish), the LaTeX stack below is fully specified and verified to compile on this machine once MiKTeX is updated. **Everything else in this document (Python env, pyproject/uv, view-model builder, pytest/syrupy tests, PDF text assertions) is identical in both variants.** The choice only affects the last stage of the pipeline and can be made at the start of the generation phase.

The rest of this file specifies the **LaTeX variant as primary** (current decision). The Typst variant is in "Stack Patterns by Variant".

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended | Confidence |
|---|---|---|---|---|
| CPython (via uv-managed venv) | 3.12.x or 3.13.x (`requires-python = ">=3.12"`) | Runs simulation, generators, tests | Gets rid of the Inkscape/Store-Python split (finding 1). uv can install CPython itself (`uv python install 3.13`), so no python.org installer is needed | HIGH |
| uv | 0.12.x (0.12.5 installed; 0.12.20 latest) | Env + dependency + lockfile manager, command runner | Already installed. `uv run pytest` / `uv run python -m gen` always uses the project venv, so nobody can accidentally hit Inkscape's Python again. A project without `[build-system]` is not built or installed ("uv will not attempt to build or install the project itself, just its dependencies"), which is exactly right for a flat script repo. `uv.lock` makes generated PDFs reproducible | HIGH |
| Jinja2 | 3.1.6 (latest, 2025-03-05) | Renders `.tex` from a Python view-model | Only sane templating for LaTeX. f-strings clash with every `{}` (you would double all braces). `string.Template` uses `$`, which is LaTeX math. Jinja2 lets you swap delimiters to `\VAR{}` / `\BLOCK{}` and has `StrictUndefined` + `finalize` hooks for safety. Verified locally | HIGH |
| LuaLaTeX (LuaHBTeX) | MiKTeX 25.12 (update from 23.10) | PDF engine | Native UTF-8 + OpenType via `fontspec`: umlauts, `€` and `·` work directly from config strings. Uses any system/OTF font. Verified locally (Arial, `Maßnahme`, `Größe`, `30.000 €` OK). About 2× slower than pdfLaTeX, which is irrelevant for about 10 pages | HIGH |
| latexmk | 4.87 installed (4.88 latest, 2026-03-09) | Runs LaTeX the right number of times | Bundled with MiKTeX. Works from `subprocess` because Git's Perl and Strawberry Perl are on PATH (verified). Replaces a Makefile, which the repo does not need on Windows | HIGH |
| tcolorbox (+ `raster`, `skins`) | 6.10.0 on CTAN (2026-05-28); 6.1.0 installed | Card styling + card grid | One `\newtcolorbox{massnahmenkarte}` defines the look (title bar in level colour, fixed `width`/`height`). `tcbraster` with `raster columns=3`, `raster column skip=0mm` places them edge-to-edge so shared frames become the cut lines. Raster verified locally; `skins` needs the `tikzfill` package installed | HIGH (raster) / MEDIUM (skins after install) |
| tabularray | 2025C (2025-11-27) | Worksheet fill-in tables (Angriff-Arbeitsblätter, Tracking-Bogen) | Fixed row heights for handwriting (`rows={ht=9mm}`), cell colours, spans and rules in one key-value interface, with no `colortbl`/`\rule` strut hacks. Actively maintained. Needs LaTeX kernel ≥ 2022-11-01 (installed kernel is 2023-11, so OK) plus `ninecolors`. **Not installed yet** | MEDIUM |
| pytest | 9.1.1 (2026-06-19) | Test runner (TDD for simulation + generator) | Standard. Already used by the user elsewhere. 9.0.2 already present in Store Python | HIGH |
| syrupy | 6.1.1 (2026-09-13) | Golden/snapshot tests for generated `.tex` (and view-model JSON) | Zero-dependency pytest plugin. `--snapshot-update` regenerates. A custom 3-line extension stores each snapshot as a real `.tex` file, so git diffs of printed content are readable. Verified locally (see snippet) | HIGH |

### Supporting Libraries

| Library | Version | Purpose | When to Use | Confidence |
|---|---|---|---|---|
| pypdf | 6.19.0 (2026-09-16) | Extract text from built PDFs in slow smoke tests | Assert that key numbers (e.g. each `e_threshold`, `mitigation_cap`, each bonus) appear in the compiled worksheet PDF. This is the final proof of "printed number = config". Assert on number tokens, not prose: extraction splits kerned words (spike output: `T ext`) | HIGH |
| python-pptx | 1.0.2 | Existing card/event deck generators | Keep only until the LaTeX/Typst cards replace `generate_pptx_cards.py` / `generate_from_template.py`. Then drop from dependencies | HIGH |
| openpyxl | 3.1.5 | Existing `generate_attack_calculator.py` | Keep while the Excel calculator is still used | HIGH |
| python-docx | 1.2.0 | Manual one-off edits of legacy `Angriff-*.docx` | Only for the transition period until the generated PDFs replace the docx worksheets. Do not add to the lockfile if no script imports it | HIGH |

### LaTeX Packages (MiKTeX package names)

| Package | Status here | Purpose | Notes |
|---|---|---|---|
| `fontspec` | installed | OTF fonts under LuaLaTeX | `\setmainfont{...}` |
| `babel` + `babel-german` | installed | `\usepackage[ngerman]{babel}`: German hyphenation, "Tabelle" etc. | Use `ngerman` (new spelling) |
| `geometry` | installed | A4 margins sized for the 3×3 card grid | Card sheet: `margin=0mm` + centred raster, or explicit margins of (210−189)/2 = 10.5 mm and (297−264)/2 = 16.5 mm |
| `tcolorbox` 6.x | installed (6.1.0), update | Cards | Load **only** needed libraries: `\tcbuselibrary{raster,skins}`. **Never `[most]`**, because it pulls in listings, breakable/pdfcol, theorems and more (the local `[most]` build hung on a missing package) |
| `tikzfill` | **missing** | Required by tcolorbox `skins` since tcolorbox 6 | `miktex packages install tikzfill` |
| `tabularray`, `ninecolors` | **missing** | Worksheet tables | `miktex packages install tabularray ninecolors` |
| `pgf`/TikZ | installed | Crop marks, CIA icons if wanted | Loaded by tcolorbox anyway |
| `xcolor` | installed | Level colours (L1/L2/L3), wave colours | Define colours from config values if they ever move into config |
| `tabularx`, `array` | installed | Fallback for simple tables | Verified locally. Use if tabularray is rejected |
| `lmodern` / OTF Latin Modern | installed | Default font | Too thin for cards; prefer a sans (below) |

**Font:** Use a sans family for readability at arm's length on a table. **Option A (simplest, verified):** `\setmainfont{Arial}`, available on every Windows machine. **Option B (reproducible, recommended if anyone else ever builds):** commit an SIL-OFL font (e.g. Source Sans 3, 4 OTF styles ≈ 1–2 MB) under `print/fonts/` and load it by file (`\setmainfont{SourceSans3}[Path=fonts/, Extension=.otf, UprightFont=*-Regular, BoldFont=*-Bold]`). The same files work for Typst via `font_paths`. Confidence: MEDIUM (A verified; B standard fontspec usage, not spiked).

### Development Tools

| Tool | Purpose | Notes |
|---|---|---|
| uv | `uv sync`, `uv run pytest`, `uv run python -m printgen` | Put the canonical commands in `README.md`. Never call bare `python` in docs/scripts |
| MiKTeX Console / `miktex` CLI | Update distribution, install the missing packages | One-time: update MiKTeX to 25.12+, then `miktex packages install tikzfill tabularray ninecolors`. Optionally set `initexmf --set-config-value=[MPM]AutoInstall=1` (install silently) for interactive use, but the **build must still pass `--disable-installer`** so CI-like runs fail fast instead of hanging |
| latexmk | Build driver, called from Python | See invocation below. Put flags in `print/latexmkrc` so manual runs match scripted runs |
| pytest markers | Separate fast unit/snapshot tests from slow PDF builds | `@pytest.mark.pdf` for tests that call LaTeX. Skip automatically when `shutil.which("latexmk")` is None |

---

## Key Patterns (verified snippets)

### Jinja2 environment for LaTeX (escape by default, opt out explicitly)

Jinja's `autoescape` is HTML-only, so LaTeX escaping must go through `finalize`. It is applied to **every** `\VAR{}` output. Pre-built LaTeX fragments are marked safe with a tiny `str` subclass.

```python
import re
from jinja2 import Environment, FileSystemLoader, StrictUndefined

class Tex(str):
    """Marks a string as already-valid LaTeX (never escaped)."""

_TEX_ESCAPES = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}
_TEX_RE = re.compile("|".join(re.escape(k) for k in _TEX_ESCAPES))

def tex_escape(value: object) -> str:
    if isinstance(value, Tex):
        return value
    if isinstance(value, bool) or value is None:
        raise TypeError(f"refusing to print {value!r} into LaTeX")  # catches template bugs
    if isinstance(value, (int, float)):
        raise TypeError("format numbers explicitly with |num or |eur")  # German formatting is mandatory
    return _TEX_RE.sub(lambda m: _TEX_ESCAPES[m.group()], str(value))

env = Environment(
    loader=FileSystemLoader("print/templates"),
    block_start_string=r"\BLOCK{", block_end_string="}",
    variable_start_string=r"\VAR{", variable_end_string="}",
    comment_start_string=r"\#{", comment_end_string="}",
    trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True,
    autoescape=False, undefined=StrictUndefined, finalize=tex_escape,
)
env.filters["num"] = lambda n: Tex(format_de(n))        # 30000 -> "30.000", 0.5 -> "0,5"
env.filters["eur"] = lambda n: Tex(format_de(n) + r"\,€")
```

- Do **not** enable `line_statement_prefix="%%"`. Decorative `%%` comments in LaTeX would then be parsed as Jinja statements.
- Format numbers in **one Python function** (`format_de`: thousands `.`, decimal `,`). Do not use `locale` (machine-dependent) or `siunitx` (not installed, and an extra layer for about 20 numbers). Inside math mode, emit `0{,}5` or keep numbers in text mode.
- The syntax was verified locally (Jinja2 3.1.6, `\BLOCK{for}` / `\VAR{}` rendering). The spike also confirmed that **without** `finalize`, `Logging & SIEM` reaches the `.tex` unescaped.

### latexmk invocation from Python (no Makefile)

```python
import shutil, subprocess
from pathlib import Path

def build_pdf(tex: Path, outdir: Path) -> Path:
    if shutil.which("latexmk") is None:
        raise RuntimeError("latexmk not found – install/update MiKTeX")
    cmd = [
        "latexmk", "-lualatex",
        "-lualatex=lualatex --disable-installer %O %S",   # fail fast, never pop MiKTeX dialog
        "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
        f"-outdir={outdir}", tex.name,
    ]
    r = subprocess.run(cmd, cwd=tex.parent, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    if r.returncode != 0:
        log = (outdir / tex.with_suffix(".log").name).read_text(encoding="utf-8", errors="replace")
        errors = [l for l in log.splitlines() if l.startswith("!") or ":error" in l.lower() or "Error:" in l]
        raise RuntimeError(f"LaTeX failed for {tex.name}:\n" + "\n".join(errors[:20]))
    return outdir / tex.with_suffix(".pdf").name
```

- Always pass `timeout=` as a second guard against hangs.
- Write `.tex` files with `path.write_text(s, encoding="utf-8", newline="\n")`. The Windows default cp1252 would corrupt `ä`/`€`, and printing non-cp1252 characters to the console crashed a spike (`UnicodeEncodeError` for `𝐶`). Set `PYTHONUTF8=1` in the environment or keep console output ASCII.
- Build into a gitignored `print/build/` and copy only final PDFs to `final_documents/`.

### Card sheet layout (tcolorbox raster, deterministic pages)

- Card size **63 × 88 mm** (standard poker size, fits sleeves). **3 × 3 = 9 cards per A4 page** (189 × 264 mm) with a zero gap, so neighbouring frames are the cut lines.
- **Chunk cards into pages in Python** (`[cards[i:i+9] for i in range(0, len(cards), 9)]`) and emit one `tcbraster` per page followed by `\newpage`. Do not rely on raster page-breaking, because paging then depends on content height.
- 10 measures × 3 levels = 30 measure cards → 4 pages (last page 3 cards). Event cards go on their own pages with a different colour scheme.
- If double-sided printing (card backs) is ever needed, mirror the column order per row for the back page. That is a Python list operation, not LaTeX logic.

### Snapshot tests for generated `.tex` (syrupy 6)

```python
import pytest
from syrupy.extensions.single_file import SingleFileSnapshotExtension, WriteMode

class TexSnapshot(SingleFileSnapshotExtension):
    file_extension = "tex"          # syrupy 6.x: public attr; `_file_extension` is silently ignored (-> .raw)
    _write_mode = WriteMode.TEXT

@pytest.fixture
def snapshot_tex(snapshot):
    return snapshot.use_extension(TexSnapshot)

def test_attack_sheet_wave1(snapshot_tex, config):
    assert render_attack_sheet(config, wave=1) == snapshot_tex
```

Verified locally: this writes `__snapshots__/test_x/test_y.tex`. The `_file_extension` spelling produced `.raw`.

### Test pyramid for this repo

1. **Unit (fast, TDD):** simulation pure functions (`apply_attack`, `compute_e_value`, budget-overrun penalty, RoS without event OPEX) with small hand-built configs, never the real enumeration.
2. **View-model tests (fast, the most valuable):** `build_attack_sheet_context(config, wave)` returns plain dicts. Assert that every printed number equals the config value (thresholds, caps, bonus table, CIA weights). This is where "printed number = config" is enforced cheaply.
3. **Golden `.tex` snapshots (fast):** catch unintended layout/text changes; review diffs in git.
4. **PDF smoke (slow, `-m pdf`):** compile once, extract text with pypdf, assert key number tokens are present. Skip if no TeX engine.

---

## Installation

```bash
# one-time: machine
uv python install 3.13                       # real CPython, not Inkscape's
# MiKTeX: update to 25.12+ via MiKTeX Console (Updates tab), then:
miktex packages install tikzfill tabularray ninecolors

# project (from repo root)
uv init --bare                               # creates pyproject.toml only (no package layout)
uv add jinja2==3.1.6 python-pptx==1.0.2 openpyxl==3.1.5
uv add --dev pytest==9.1.1 syrupy==6.1.1 pypdf==6.19.0
uv sync
uv run pytest
```

Resulting `pyproject.toml` (no `[build-system]`, so uv installs dependencies only):

```toml
[project]
name = "security-planspiel"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["jinja2==3.1.6", "python-pptx==1.0.2", "openpyxl==3.1.5"]

[dependency-groups]
dev = ["pytest==9.1.1", "syrupy==6.1.1", "pypdf==6.19.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = ["pdf: compiles real PDFs via LaTeX/Typst (slow)"]
addopts = "-m 'not pdf'"
```

Commit `pyproject.toml` **and** `uv.lock`. Add `.venv/` and `print/build/` to `.gitignore`.

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|---|---|---|
| pyproject.toml + uv.lock | `requirements.txt` (+ `requirements-dev.txt`) | Only if uv must not be used. Then pin with `==`, keep pytest config in `pyproject.toml` `[tool.pytest.ini_options]`, and always call `<venv>/Scripts/python -m pip`. Don't use `pip install -e .`: setuptools flat-layout discovery fails on a repo with 6 top-level modules |
| LuaLaTeX | pdfLaTeX | If compile speed ever matters (roughly 2× faster). UTF-8 input works since kernel 2018, but you are limited to TeX-packaged fonts (`helvet`) and must care about `fontenc`/`€` (`eurosym`/textcomp). Not worth it for about 10 pages |
| LuaLaTeX | XeLaTeX | Equivalent font handling. LuaLaTeX is the LaTeX team's recommended Unicode engine and gets better maintenance. No reason to pick XeLaTeX here |
| tabularray | `tabularx` + `array` (+ `colortbl`) | If tabularray is rejected or MiKTeX can't be updated. `tabularx` is installed and verified; fixed handwriting row height needs `\rule{0pt}{8mm}` struts; colours need `colortbl` (missing) |
| tcolorbox raster | Custom TikZ grid (`\foreach` + absolute `\node` placement) | If exact cut marks outside the card area or mirrored back pages become a requirement. More code, full control |
| syrupy | pytest-regressions 2.11.0 (`file_regression.check(s, extension=".tex")`) | Equally good. It pulls in `pytest-datadir` + PyYAML and uses `--force-regen`. Pick it if YAML `data_regression` for simulation summaries is wanted |
| Jinja2 | Pure Python string building | Only for tiny fragments (one table row). Whole documents in f-strings mean doubled braces everywhere, which is unreadable and hard to review |

## What NOT to Use

| Avoid | Why | Use Instead |
|---|---|---|
| Bare `python` / `pip` in Git Bash | Resolves to Inkscape's Python 3.12 (no pip) vs. Store Python 3.11 (has pip): two different environments | `uv run ...` (or an explicit `.venv/Scripts/python.exe`) |
| `\usepackage[most]{tcolorbox}` | Loads about 10 libraries. On this machine it triggered a missing-package dialog and hung the build indefinitely | `\tcbuselibrary{raster,skins}` only |
| MiKTeX auto-install during scripted builds | "Ask" mode = invisible GUI dialog = hung subprocess | `lualatex --disable-installer` + explicit `miktex packages install` list |
| `flashcards` class (1.0.2, 2022) | Built for two-sided Q/A study cards at fixed Avery sizes. Hard to restyle (level colours, CIA rows) | tcolorbox cards |
| `ticket` package (0.4d) | Label/visiting-card sheets; very basic styling; old | tcolorbox cards |
| PyLaTeX (1.4.2, last release 2023-10) | Builds LaTeX through a Python object tree: verbose, no template readability, stagnant | Jinja2 templates |
| `latexbuild` (0.2.2, 2017) | Abandoned Jinja+LaTeX wrapper | The 30-line `build_pdf` above |
| Jinja `autoescape=True` | HTML-escapes (`&` → `&amp;`), which is wrong for LaTeX | `finalize=tex_escape` |
| Default Jinja `{{ }}` / `{% %}` delimiters in `.tex` | `{{` appears naturally in LaTeX (`\textbf{{\large x}}`); unreadable collisions | `\VAR{}` / `\BLOCK{}` |
| `siunitx` / `locale` for German numbers | siunitx not installed + extra layer; `locale` output depends on the machine | One `format_de()` in Python, unit-tested |
| Makefile | Needs `make` on Windows; the repo has none | Python build entry point (`python -m printgen`) |
| Snapshotting PDFs byte-for-byte | PDFs embed timestamps/IDs; binary diffs are unreviewable | Snapshot the `.tex` (or view-model JSON); assert PDF **text** with pypdf |

---

## Stack Patterns by Variant

**If the renderer stays LaTeX (current decision):**
- Python view-model → Jinja2 (`\VAR{}`, `finalize=tex_escape`) → `.tex` → `latexmk -lualatex` (`--disable-installer`) → PDF
- Prerequisite phase task: update MiKTeX 23.10 → 25.12+, install `tikzfill tabularray ninecolors`
- Snapshot artefact: `.tex`

**If the user switches to Typst (recommended alternative):**
- Python view-model → `json` file (with `ensure_ascii=False`) → static `.typ` templates that `json("...")` it → `typst.compile(path, output=..., font_paths=[...], ignore_system_fonts=True)` → PDF
- Dependencies: add `typst==0.15.0` (PyPI binding, 2026-06-16; CLI is 0.15.1). No MiKTeX, no Perl, no Jinja2, no escaping layer
- Cards: `#grid(columns: (63mm,)*3, rows: 88mm, stroke: 0.3pt + gray, ..cards.map(card))`; worksheets: `#table(columns: ..., rows: (auto, 10mm))`; German: `#set text(lang: "de")`
- Snapshot artefact: view-model JSON (syrupy `JSONSnapshotExtension`), since the `.typ` templates are static
- Verified locally: Python 3.11 venv + `typst` 0.15.0 compiled cards and a table with `&`, `_#$%`, umlauts and `€` verbatim in about 3 s

---

## Version Compatibility

| Package A | Compatible With | Notes |
|---|---|---|
| syrupy 6.1.1 | pytest ≥ 8, Python ≥ 3.10 | Tested with pytest 9.1.1 |
| pytest 9.1.1 | Python ≥ 3.10 | The Store Python 3.11 works; target 3.12+/3.13 via uv |
| pypdf 6.19.0 | Python ≥ 3.9 | Pure Python |
| typst (PyPI) 0.15.0 | Python ≥ 3.8 | Pin exactly; Typst 0.x minors can break template syntax |
| tabularray 2025C | LaTeX kernel ≥ 2022-11-01, `ninecolors` | Kernel here: 2023-11 (l3kernel 2023-11-09), so OK even before the MiKTeX update |
| tcolorbox ≥ 6.0 `skins` | `tikzfill` | Missing locally, which is why `skins` currently fails |
| latexmk 4.87/4.88 | Perl on PATH | Git's `/usr/bin/perl` and Strawberry Perl both present; works from Python `subprocess` |
| MiKTeX 23.10 → 25.12 | Existing documents | Major jump. Rebuild the font cache once (first LuaLaTeX run after the update is slow while luaotfload re-indexes fonts) |

## Sources

- Local environment probes on this machine (2026-09-29): `python -c sys.executable`, `pip --version`, `pip list`, `initexmf --report`, `kpsewhich`, latexmk/LuaLaTeX spike compiles, Typst spike compile, syrupy + Jinja2 spike tests. **HIGH** (direct execution)
- PyPI JSON API (`pypi.org/pypi/<pkg>/json`): jinja2 3.1.6, pytest 9.1.1, syrupy 6.1.1, pytest-regressions 2.11.0, pypdf 6.19.0, python-pptx 1.0.2, openpyxl 3.1.5, python-docx 1.2.0, typst 0.15.0, pylatex 1.4.2, latexbuild 0.2.2, uv 0.12.20, pip 26.2.1. **HIGH** (official registry)
- GitHub API `typst/typst` releases/latest: v0.15.1 (2026-07-17). **HIGH**
- [CTAN tcolorbox](https://ctan.org/pkg/tcolorbox): 6.10.0, 2026-05-28. **HIGH**
- [CTAN tabularray](https://ctan.org/pkg/tabularray): 2025C, 2025-11-27, maintained. **HIGH**. Kernel ≥ 2022-11-01 / ninecolors requirement from a [web search summary](https://ctan.org/tex-archive/macros/latex/contrib/tabularray) (seam-classified **LOW**; consistent with the package docs, but not read directly)
- [CTAN latexmk](https://ctan.org/pkg/latexmk): 4.88, 2026-03-09. **HIGH**
- [CTAN flashcards](https://ctan.org/pkg/flashcards) (1.0.2, 2022) and [CTAN ticket](https://ctan.org/pkg/ticket) (0.4d). **HIGH**
- [MiKTeX download page](https://miktex.org/download): 25.12, 2025-12-31. **HIGH**
- [Jinja2 API docs](https://jinja.palletsprojects.com/en/stable/api/): delimiter options, `finalize`, `StrictUndefined`, `autoescape`. **HIGH**
- [syrupy README](https://github.com/syrupy-project/syrupy) + installed source `syrupy/extensions/single_file.py` (`file_extension` attr). **HIGH**
- [uv project config docs](https://docs.astral.sh/uv/concepts/projects/config/): no build-system means dependencies only; `tool.uv.package`. **HIGH**. Default syncing of the `dev` dependency group: from knowledge, **MEDIUM**

---
*Stack research for: config-driven print-material generation (LaTeX/Typst) + Python test tooling*
*Researched: 2026-09-29*
