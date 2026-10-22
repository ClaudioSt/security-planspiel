---
phase: 04-print-pipeline-attack-worksheets
reviewed: 2026-10-22T15:51:29Z
depth: standard
files_reviewed: 43
files_reviewed_list:
  - planspiel/texbuild.py
  - planspiel/render.py
  - planspiel/stamp.py
  - planspiel/printmodel.py
  - planspiel/fmt.py
  - planspiel/cli.py
  - planspiel/rules.py
  - planspiel/analyze.py
  - planspiel/texts.py
  - print/planspiel.sty
  - print/templates/angriff.tex.j2
  - print/miktex-packages.txt
  - content/texte.toml
  - content/digit_allowlist.toml
  - pyproject.toml
  - .gitattributes
  - .gitignore
  - tests/conftest.py
  - tests/support/tex.py
  - tests/support/gitrepo.py
  - tests/support/worksheet_replay.py
  - tests/fixtures/print/smoke.tex
  - tests/fixtures/print/smoke.tex.j2
  - tests/fixtures/mini_content/texte.toml
  - tests/test_print_check.py
  - tests/test_print_cli.py
  - tests/test_print_cli_pdf.py
  - tests/test_print_driver.py
  - tests/test_print_fmt.py
  - tests/test_print_model.py
  - tests/test_print_preflight.py
  - tests/test_print_render.py
  - tests/test_print_render_env.py
  - tests/test_print_smoke.py
  - tests/test_print_stamp.py
  - tests/test_print_stamp_pdf.py
  - tests/test_print_worksheets_pdf.py
  - tests/test_single_definition.py
  - tests/test_texts_migration.py
  - tests/test_worksheet_constants.py
  - tests/test_worksheet_equivalence.py
  - tests/test_worksheet_equivalence_full.py
  - tests/test_worksheet_replay.py
findings:
  critical: 1
  warning: 7
  info: 9
  total: 17
status: issues_found
---

# Phase 4: Code Review Report

**Reviewed:** 2026-10-22T15:51:29Z
**Depth:** standard
**Files Reviewed:** 43 (for rules.py, analyze.py, texts.py, cli.py, conftest.py and test_single_definition.py only the Phase 4 diff `4ad2362^..HEAD`)
**Status:** issues_found

## Summary

The printed worksheet values and formulas match the rules. I rendered all three worksheets without TeX and checked them by hand against `rules.apply_attack`:
- Threshold, cap and upper bound are correct: 23/8/31, 20/10/30 and 25/7/32.
- The Fall-1 and Fall-2 damage and KZ values are correct.
- The Fall-3 lines `(upper − GR) × s_unit·1000` and `kz_full_damage + (GR − lower) × slope` are correct, and the slope 17/7 prints as "× 17 ÷ 7".
- The recovery table (0/10/30/50 %) and the case boundaries (≤ lower, ≥ upper) are consistent with `reduction_above_threshold_scaled`.

The D-06 and D-09 guards are sound for the current config. I also checked them by hand for the "2,43" approximation of 17/7, and it cannot flip a rounding. The replay in `tests/support/worksheet_replay.py` is properly independent of `rules`.

The defects are in the pipeline around the worksheets:
- The LaTeX escaper does not neutralise babel-ngerman's active `"` or the TeX input ligatures. I confirmed this with a bounded LuaLaTeX run: `"aktiv"` prints as `äktiv` with the quotes gone. The content source already contains such strings for Phase 5.
- The `--check` exit-code contract (0 fresh / 1 stale / 2 environment error) is broken by several uncaught exceptions. I reproduced exit 1 with a traceback for a print dir that has no `planspiel.sty`.
- Orphan cleanup deletes every `*.pdf` in whatever `--out-dir` is given.
- The print command never runs the content checks that enforce "no numbers in prose" and the veil.
- The recovery step never says which measure's level to read.
- On POSIX, the "kill the whole process tree" claim of the TeX driver is false.

## Critical Issues

### CR-01: `tex_escape` lets babel-ngerman's `"` shorthand and TeX ligatures corrupt printed text silently

**File:** `planspiel/render.py:246-273` (together with `print/planspiel.sty:11-14`)
**Issue:** `tex_escape` is the single escaping boundary for every string that reaches a page. It escapes only the ten LaTeX specials. `planspiel.sty` loads `babel` with `ngerman`, which makes `"` an active shorthand character. `fontspec` also enables the TeX input ligatures by default (`--`, `---`, `<<`, `>>`, `''`, ` `` `, `,,`, `!``, `?``).

I verified this with a bounded `lualatex --disable-installer` run using fontspec/Arial and babel ngerman. The source text `X "aktiv" "Auch" "Dr. Weber" a--b <<c>> Y` came out of the PDF as `X äktivAuchDr. Weberä–b «c» Y`:
- every `"` was swallowed,
- `"a` became `ä`,
- the space after a closing quote was eaten,
- `--` became an en dash and `<<`/`>>` became guillemets.

The build exits 0 with no warning. `content/texte.toml` already holds such strings for the next print documents, for example lines 485-486 and 527-528: `von = "\"Dr. Thomas Weber\" <t.weber@mechtech-gmbh.de>"`. A text such as `"-5"` or `"0,5"` would lose characters next to a number. That breaks the core value that every printed string matches its source. The current smoke title (`tests/conftest.py:39`) and the escape tests (`tests/test_print_render_env.py:10-27`) contain none of these characters, so the gap is not caught.
**Fix:** Neutralise the shorthand and the ligatures inside the escaper, and add them to the smoke title and the parametrised escape tests:
```python
_TEX_SPECIALS = str.maketrans({
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    '"': r"\textquotedbl{}",          # babel ngerman shorthand
    "-": "-{}",                        # breaks -- / --- ligatures
    "<": "<{}", ">": ">{}",            # breaks << / >> ligatures
    "'": "'{}", "`": "`{}", ",": ",{}", "!": "!{}", "?": "?{}",
})
```
Alternatively, set `\shorthandoff{"}` and use `\setmainfont{Arial}[Ligatures=NoCommon]` (without TeX ligatures) in `planspiel.sty`. In that case, add a PDF test that prints `"aktiv" a--b <<c>>` verbatim.

## Warnings

### WR-01: `print --check` exit-code contract is broken by uncaught exceptions, and the build path tracebacks on common Windows errors

**File:** `planspiel/cli.py:160-218`, `planspiel/stamp.py:103`, `planspiel/texbuild.py:181-182, 219-221`
**Issue:** `--check` documents exit codes 0 = fresh, 1 = stale and 2 = environment error. Several environment failures escape the `except` clauses and end in a Python traceback with exit code 1, which a caller reads as "stale":
- `compute_stamp` reads `print_dir/planspiel.sty` before any `try` handles `OSError`. I reproduced this with `uv run planspiel print --check --print-dir <dir with only templates/>`: the result was a `FileNotFoundError` traceback and exit 1.
- `Texts.get` raises `KeyError` for a missing text key, for example a `bonus_reasons` entry for a new bonus measure. `render_all` catches only `TemplateError`, `TypeError` and `ValueError`.
- `build_documents` raises `ValueError` for a job name that fails `JOB_NAME`, for example a config attack id with an upper-case letter. This happens after preflight, render and stamp, and `--check` never validates the names at all.
- On Windows, a published PDF that is open in a viewer makes `shutil.copyfile` or `old.unlink()` raise `PermissionError` (cli.py:202-212). The same happens for `unlink` in `run_lualatex`. The result is a half-published output directory and a traceback.
**Fix:** Wrap each stage with an `OSError`/`KeyError` handler that maps to `failure`, and validate job names in the render stage, not only in `build_documents`:
```python
try:
    version = stamp.compute_stamp(documents, Path(print_dir), stamp.repo_root())
except (stamp.StampError, OSError) as error:
    print(f"ERROR print.stamp {error}"); print("1 Fehler"); return failure
```
Also catch `KeyError` next to `PrintModelError` in the render block. In the publish loop, catch `OSError` and report which file is locked.

### WR-02: Orphan cleanup deletes every PDF in an arbitrary `--out-dir`

**File:** `planspiel/cli.py:208-212`
**Issue:** After a build, `for old in target.glob("*.pdf"): if old.name not in keep: old.unlink()` removes every PDF in the target that this run did not produce. It does this whether or not the pipeline ever wrote that file. `final_documents/` itself holds hand-maintained PDFs (`Anfrage-Mail.pdf`, `Audit-Mail.pdf`, `Zeitungsartikel.pdf`). One mistyped `--out-dir final_documents`, or `--out-dir .`, silently deletes them. Untracked or uncommitted PDFs would be lost for good.
**Fix:** Delete only files that the previous manifest lists, and leave unknown PDFs for `--check` to report:
```python
previous = {}
manifest_path = target / stamp.MANIFEST_NAME
if manifest_path.is_file():
    previous = json.loads(manifest_path.read_text(encoding="utf-8")).get("documents", {})
for job, entry in previous.items():
    name = entry.get("pdf", f"{job}.pdf")
    if name not in keep and "/" not in name and "\\" not in name:
        (target / name).unlink(missing_ok=True)
```

### WR-03: `planspiel print` does not enforce the content checks (digits in prose, veil, required keys)

**File:** `planspiel/cli.py:160-165`
**Issue:** The print command loads `texte.toml` with the bare `load_texts`, which does no validation. It never calls `check_texts`, so the rules from Phase 3 D-03 are not enforced at the moment material is printed:
- no numbers in TOML prose (digit allowlist),
- the giveaway/veil checks,
- `required_keys`.

A hint such as "Schwelle 23" in `[sheets.angriff]`, which would drift from the config, gets printed and stamped as clean. A missing key crashes with an uncaught `KeyError` (see WR-01) instead of producing a named error.
**Fix:** Load through `load_content(Path(content_dir))` and run `check_texts(cfg, content)` before rendering. On any `error`-level issue, print it as `ERROR print.texts ...` and return `failure`.

### WR-04: The recovery step never names the measure whose level sets r

**File:** `planspiel/printmodel.py:274-283`, `print/templates/angriff.tex.j2:180-193`, `content/texte.toml:259`
**Issue:** `worksheet_constants` derives `recovery_measure` (M4 today) from the config, and the replay uses it (`worksheet_replay.py:126`). The value is never printed:
- the table header is `Level | (empty) | Recovery-Faktor r`,
- the hint says "Lest den Faktor r am Level eurer Maßnahme ab" without saying which measure,
- the only link to M4 is the prose word "Backup" in `recovery_intro`, which is hard-coded in TOML.

A team cannot tell from the sheet which of its measures to read. This breaks "every rule is unambiguous". If the config moves `recovery` to another measure, the sheet stays silently wrong while the replay still passes, because the replay reads a field the sheet does not print. D-11 says the replay should read only printed fields.
**Fix:** Print the measure, for example a header `f"{labels['level']} {recovery_measure}"` or a hint line built in code with `_measure_name(cfg, recovery_measure)`. Add it to `printed_fragments()` so the PDF test enforces it.

### WR-05: On POSIX the timeout kills only the direct child, not the process tree

**File:** `planspiel/texbuild.py:62-79, 91-112`
**Issue:** The module docstring promises "a timeout that kills the whole process tree". The non-Windows branch calls `os.kill(pid, 9)`, which kills only `lualatex`. Because `Popen` is not started in a new session, grandchildren survive and keep the stdout/stderr pipes open. The reaping `communicate(timeout=10)` then always times out (the error is swallowed), and the orphans keep running.
**Fix:** On POSIX, start the process in its own session and kill the group:
```python
proc = popen(cmd, ..., start_new_session=(sys.platform != "win32"))
...
os.killpg(pid, signal.SIGKILL)   # in _kill_tree for non-win32
```

### WR-06: `print/** text eol=lf` will corrupt any binary asset placed under `print/`

**File:** `.gitattributes:5`
**Issue:** The rule forces the `text` attribute and LF conversion on every file below `print/`. D-19 already plans for "every asset file TeX reads", and Phase 5 card skins will add assets. A PNG, PDF or font committed under `print/` would have its CRLF byte pairs rewritten on checkout or commit, which corrupts it silently. The same `text` attribute also feeds the CRLF assumptions in `content_hash`.
**Fix:** Limit the rule to text extensions, for example `print/**/*.sty text eol=lf`, `print/**/*.tex text eol=lf`, `print/**/*.j2 text eol=lf` and `print/*.txt text eol=lf`. Add explicit `binary` lines for image and font types.

### WR-07: The stamp's date and `+lokal` flag describe fixed repo paths, not the inputs actually used

**File:** `planspiel/stamp.py:21-24, 65-67, 83-95`; `planspiel/cli.py:177`
**Issue:**
- `DATA_INPUTS` and `BUILD_INPUTS` are hard-coded repo-relative paths, while `--config`, `--content-dir` and `--print-dir` are free CLI options. A build with `--config experiment.json`, or an untracked config elsewhere, gets a stamp that has no `+lokal`. Its date is that of `simulation_config.json`, even though the printed numbers come from uncommitted data. That defeats PRINT-11's purpose of making mixed or unofficial printouts visible.
- `repo_root()` is derived from the current working directory, not from the inputs. Running from outside the checkout with absolute paths fails with `ERROR print.stamp ... not a git repository`, which I reproduced.
**Fix:** Derive the repo from the config path (`stamp.repo_root(Path(config).parent)`). Treat any input path that is not under a `BUILD_INPUTS` entry, or is not tracked (`git ls-files --error-unmatch`), as dirty. Or reject non-default input paths unless an explicit flag is given.

## Info

### IN-01: `fmt.format_number` accepts floats and prints their binary expansion

**File:** `planspiel/fmt.py:244-260`
**Issue:** `Fraction(0.1)` has a power-of-two denominator, so `terminates` is True. I verified that `format_number(0.1)` returns `0,1000000000000000055511151231257827021181583404541015625` and `format_percent(0.3)` returns `29,99…%`. Today every input is exact, but the module says rounded values "can never reach a sheet by accident".
**Fix:** Reject `float` explicitly: `if isinstance(value, float): raise TypeError(...)`.

### IN-02: The abbreviation "GR" is used on the sheet but never introduced

**File:** `planspiel/printmodel.py:244, 254-261`; `content/texte.toml:247`
**Issue:** The Fall-3 lines read `(31 − GR ▢)` and `KZ = −6 + (GR ▢ − 23) × 2`. Neither step 4 nor the case headings say that GR means Gesamtreduktion.
**Fix:** Print step 4 as `Gesamtreduktion (GR) = …`, or use the full label in the Fall-3 lines.

### IN-03: The D-09 half-distance guard assumes integer event KZ

**File:** `planspiel/printmodel.py:147-161`
**Issue:** The guard measures only the distance of the attack KZ to a half-integer. A fractional event KZ, which the config format does not forbid, shifts the rounding boundary, and the guard would no longer prove D-09.
**Fix:** Assert that every event KZ value is an integer, for example in `worksheet_constants` or the validator, or fold the event KZ range into the distance check.

### IN-04: `\levelbadge` prints nothing for levels above 3

**File:** `print/planspiel.sty:92-96`
**Issue:** `\ifcase` has no `\else`, so a config with level 4 renders an empty badge silently.
**Fix:** Add `\else\PackageError{planspiel}{Unbekanntes Level #1}{}`.

### IN-05: `label_*` keys silently override `[sheets.labels]` keys

**File:** `planspiel/printmodel.py:200-202`
**Issue:** `labels[key[len(LABEL_PREFIX):]] = text` overwrites any key of the same name, for example a future `sheets.labels.kz`, without notice.
**Fix:** Raise if `key[len(LABEL_PREFIX):] in labels`.

### IN-06: The Jinja comment delimiter `\#{` collides with LaTeX's escaped hash

**File:** `planspiel/render.py:282-283`
**Issue:** Template text such as `\#{}` (a literal `#` followed by a group) is parsed as a Jinja comment and swallows text up to the next `}`.
**Fix:** Use a delimiter that cannot occur in LaTeX, for example `((#` / `#))`, or document the restriction in the template header.

### IN-07: The slow full-replay module does real work at collection time

**File:** `tests/test_worksheet_equivalence_full.py:58`
**Issue:** `@pytest.mark.parametrize("tier_name", list(_setup()[0].budget_tiers))` loads the config and builds every sheet during collection, even in the default `-m 'not slow'` run. A broken config or text then aborts collection of the whole suite instead of failing individual tests.
**Fix:** Parametrise from `json.loads(CONFIG_PATH.read_text())["budget_tiers"]` keys, or move `_setup()` into a fixture.

### IN-08: `check_freshness` trusts the manifest's structure and file names

**File:** `planspiel/stamp.py:150-177`
**Issue:** A manifest with `documents` as a list raises `AttributeError` at `recorded.get`, outside the `try`. A `pdf` entry such as `../x.pdf` makes the check read a file outside `out_dir`.
**Fix:** Validate that `documents` is a dict of dicts and that `Path(name).name == name` inside the `try`. Report violations as "unexpected format".

### IN-09: A missing glyph does not fail the production build

**File:** `print/planspiel.sty:10-12`
**Issue:** A character that is missing in Arial is dropped from the PDF, with only a log line. Losing `−` would turn `−6` into `6`. Only the `-m pdf` test (`test_build_logs_show_no_missing_glyph_and_no_overfull_line`) catches this, and only for the worksheets.
**Fix:** Add `\tracinglostchars=3` (an error in current LuaTeX) to `planspiel.sty`, so that `planspiel print` itself stops.

---

_Reviewed: 2026-10-22T15:51:29Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
