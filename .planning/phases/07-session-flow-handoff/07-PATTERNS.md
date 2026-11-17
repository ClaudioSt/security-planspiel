# Phase 7: Session Flow & Handoff - Pattern Map

**Mapped:** 2026-11-02
**Files analyzed:** 27 new/modified (code, config, content, tests); docs and the intro deck are listed separately
**Analogs found:** 25 / 27 (the rest are manual or human events)

All paths are relative to the repo root. Run Python only via `uv run`. Line numbers come from the files as read on 2026-11-02.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `simulation_config.json` (+ `session_schedule` block) | config | batch (read-only block) | `practice` block in the same file | exact |
| `planspiel/config.py` (+ `SessionSchedule`, `Block`, `Stage`, `PrintRow`, field `session_schedule`) | model | transform | `Practice` dataclass, `config.py:74,107,216-243` | exact |
| `planspiel/validate.py` (+ `check_session_schedule`) | validator | transform | `check_practice`, `validate.py:593-664`, call site `:228-231` | exact |
| `planspiel/texts.py` (+ key tuples, `required_keys` extension) | utility | transform | `_SPIELLEITUNG_KEYS`, `SHEET_KEYS`, `required_keys` (`texts.py:80`, `:300-330`) | exact |
| `content/texte.toml` (+ `sheets.spielleitung.schedule.*`, `sheets.debrief.*`, was-neu, probelauf sections) | config (prose) | batch | `[sheets.spielleitung]`, `texte.toml:481-575` | exact |
| `planspiel/schedule.py` (optional shared helper) | utility | transform | `fmt.py` helpers plus `master._tier_results` style | role-match |
| `planspiel/master.py` (+ schedule, print list, debrief fields in `MasterSheet`) | model | transform | `master.py` itself (`build_master_sheet`, `:453-526`) | exact |
| `print/templates/master.tex.j2` (+ schedule, print-list, debrief pages) | template | transform | the same template (contents list, `how_to` loop, `tabularx` blocks) | exact |
| `planspiel/was_neu.py` | model | transform | `planspiel/wave_page.py` (one page) plus `practice.py` (isolation) | role-match |
| `print/templates/was_neu.tex.j2` | template | transform | `print/templates/welle.tex.j2` | exact |
| `content/mhp_baseline.json` | config (frozen data) | file-I/O | `content/clues.toml` (separate content file, one reader) | role-match |
| `planspiel/stamp.py` (+ baseline in `DATA_INPUTS`/`BUILD_INPUTS`) | config | file-I/O | `content/clues.toml` entries, `stamp.py:22-41` | exact |
| `planspiel/cli.py` (+ baseline loader in `_print_command`) | controller | request-response | clues loader, `cli.py:246-263,290` | exact |
| `planspiel/render.py` (+ `was_neu`, `probelauf` builders, `baseline` arg) | service | transform | `wave_page`, `master_sheet` builders, `render.py:100-172` | exact |
| `planspiel/probelauf.py` | model | transform | `planspiel/wave_page.py` (flat dataclass + `printed_fragments`) | role-match |
| `print/templates/probelauf.tex.j2` | template | transform | `welle.tex.j2` (table + `\fillreport{1}`) | role-match |
| `final_documents/generated/*` + `manifest.json` | generated output | batch | single-writer print commit (05-16, 06-10 precedent) | process |
| `tests/test_session_schedule_config.py` | test | transform | `tests/test_practice_config.py` | exact |
| `tests/test_schedule_model.py`, `test_debrief_model.py` | test | transform | `tests/test_master_model.py` | exact |
| `tests/test_master_pdf.py` (adapt) | test | transform | itself (`_section_pages`, fill report, fragments) | exact |
| `tests/test_was_neu_model.py`, `test_probelauf_model.py` | test | transform | `tests/test_wave_page.py` | exact |
| `tests/test_was_neu_pdf.py`, `test_probelauf_pdf.py` | test | file-I/O | `tests/test_wave_page_pdf.py` | exact |
| `tests/test_baseline_isolation.py` | test | transform | `test_practice_config.py:102-135` plus `test_print_stamp.py:136-160` | role-match |
| `tests/test_no_archive_references.py` | test | file-I/O | `tests/test_single_definition.py` (source scan) | role-match |
| `tests/test_inventory.py` (adapt) + `content/INVENTORY.md` | test/doc | file-I/O | itself (`EXPECTED_FILES`, `_rows()`) | exact |
| `tests/test_legacy_generators_smoke.py` (delete), `test_texts_migration.py`, `test_environment.py`, `test_single_definition.py` (adapt) | test | file-I/O | themselves | exact |
| README anchor tests (7 files) | test | file-I/O | `test_e_target_removed.py:173-180` | exact |
| `README.md`, `CLAUDE.md`, `.planning/codebase/*.md`, `.claude/CLAUDE.md`, `docs/folienkonzept...md` | docs | n/a | no code analog; constraints below | n/a |
| Intro deck `.pptx` edit | manual asset | file-I/O | RESEARCH §Q6e snippet | no analog in repo |

## Pattern Assignments

### `simulation_config.json` + `planspiel/config.py` (config block `session_schedule`)

**Analog:** the `practice` block. It is optional, read by one module, and invisible to the rules.

**Loader pattern** (`planspiel/config.py:216-243`):
```python
practice = None
if "practice" in raw:
    block = raw["practice"]
    practice = Practice(
        kz_start=block["kz_start"],
        budget=block["budget"],
        ...
    )
return Config(..., practice=practice, reference_plans=dict(raw.get("reference_plans", {})), ...)
```
Copy this: `session_schedule = None; if "session_schedule" in raw: ...`. Build frozen dataclasses (`Block(id, minutes)`, `Stage`, `PrintRow(job, per_team, facilitator)`). Add `teams` (3) to the block (D-27). Add `session_schedule: Optional[SessionSchedule] = None` next to `practice: Optional[Practice] = None` (`config.py:107`).

**Do not** add the block to `tests/fixtures/mini_config.json`. Builders return `{}` or `None` when `cfg.session_schedule is None`, the way `build_master_sheet` returns `None` without `reference_plans`.

### `planspiel/validate.py` (`check_session_schedule`)

**Analog:** `check_practice` (`validate.py:593-664`) and its call site.

**Call-site pattern** (`validate.py:228-231`):
```python
if "practice" in raw:
    self.check_practice(raw["practice"], attacks, measures)
if "reference_plans" in raw:
    self.check_reference_plans(raw["reference_plans"], measures)
```
Add `if "session_schedule" in raw: self.check_session_schedule(raw["session_schedule"], raw.get("waves"))` there.

**Helpers to copy** (`validate.py:177-188`): `self.int_field(obj, key, path, lo=…)`, `self.container(value, dict|list, path)`, `self.error(code, path, message)`. The error codes use the form `"practice.severity_cap"`, so use `"schedule.sum"`, `"schedule.stage_sum"`, `"schedule.wave_block"` and so on. Messages are in German.

**Unknown-key guard** (`validate.py:32,600-602`):
```python
PRACTICE_KEYS = ("kz_start", "budget", "attack", "wave", "event", "selection")
for key in block:
    if key not in PRACTICE_KEYS:
        self.error("schema.keys", f"{path}.{key}", f"Unbekannter Schlüssel '{key}' im Übungsblock")
```
Define `SCHEDULE_KEYS` the same way.

**Rules (RESEARCH §Q4):**
- Block minutes sum to `total_minutes` (190).
- Stage minutes sum to the `debrief` block.
- Unique ids.
- `wave_N` blocks match `waves[].id`.
- `wave_0` exists only if `practice` is present.
- Quantities are ints >= 0.
- No prose strings.
- Product rules (wave 1 = 20, total 190) go in a test, not in the validator.

### `content/texte.toml` + `planspiel/texts.py` (labels, directions, debrief, was-neu, probelauf prose)

**Analog:** `[sheets.spielleitung]` (`texte.toml:481-500`) with `how_to = [ ... ]` lists, mirrored in `_SPIELLEITUNG_KEYS` (`texts.py:80`).

**Coverage rule:** every TOML key must appear in a tuple of `SHEET_KEYS`, or be generated in `required_keys(cfg)`. A key with no tuple entry is `orphan_key`. A tuple entry with no key is `missing_key`.

**Config-driven keys** (`texts.py:300-330`, `required_keys`):
```python
for attack_id in cfg.attacks:
    keys.add(f"attacks.{attack_id}.veiled.title")
...
keys.update(SHEET_KEYS)
if cfg.practice is not None:
    keys.update(PRACTICE_KEYS)
```
Extend with `if cfg.session_schedule is not None:`. Generate `sheets.spielleitung.schedule.<block_id>.label` and `.direction`, `sheets.spielleitung.print_list.<job>`, and `sheets.debrief.<stage_id>.*` from the config ids.

**Digit lint** (`tests/test_texts_digits.py`; `check_digits` in `texts.py`): no digit outside `story.*`.
- Do not type "Welle 1", "10 Minuten", "3-4" or "Level 2" in prose.
- Compose labels in the model, for example `f"{words['wave_label']} {wave_id}"`.
- Leave `content/digit_allowlist.toml` untouched.

**D-28 wording fixes** (text only):
- `eventkarten.per_measure_at_level` must read Level 2 "oder höher".
- `sheets.labels.event_after_wave` must match `sheets.welle.text_events`, where events are step 1 of the wave.
- Check the `texte.toml` key before editing.

### `planspiel/master.py` + `print/templates/master.tex.j2` (schedule, print list, debrief)

**Analog:** `build_master_sheet` (`master.py:453-526`) and the template.

**Model pattern** (`master.py:42-60`, `:453-526`):
```python
@dataclass(frozen=True)
class ParameterBlock:
    rows: tuple[tuple[str, str], ...]
    ...

def build_master_sheet(cfg, texts, clues) -> Optional[MasterSheet]:
    if not cfg.reference_plans:
        return None
    view = RevealView(cfg, texts)
    words = view.sheet("spielleitung")
    ...
    return MasterSheet(job=MASTER_JOB, title=words["title"], ..., how_to=tuple(words["how_to"]), ...)
```
Add dataclasses `ScheduleRow(label, minutes, cumulative, direction)`, `PrintListRow(label, per_team, facilitator)` and `DebriefStage(title, guide_minutes, items)`. Format numbers as strings in the model, using `fmt` helpers. The template only loops. Add the new fields to `MasterSheet`. `printed_fragments()` (via `printed_strings`) then gets them for free, and `test_every_model_fragment_is_in_the_pdf_text` covers them.

**Template pattern** (`master.tex.j2`):
```
\#{ Facilitator booklet: loops and inserts only; every number arrives as a finished string ... }
\documentclass[a4paper,10pt]{article}
\usepackage{planspiel}
\newcounter{masterreport}
\newcommand{\pagereport}{\stepcounter{masterreport}\fillreport{\themasterreport}}
...
\step{\VAR{sheet.how_to_title}}
\begingroup\small\setlength{\parskip}{1mm}
\BLOCK{for text in sheet.how_to}
\BLOCK{set number = loop.index|string}
\noindent\hangindent=6mm\hangafter=1\textbf{\VAR{number}.}\hspace{1.5mm}\VAR{text}\par
\BLOCK{endfor}
\endgroup
```
Every page ends with `\pagereport`. Table pattern: `\begin{tabularx}{\linewidth}{|C{20mm}|L|}` (`master.tex.j2:40`). The empty clock-time column (D-04) is an empty cell.

**Placement:**
- Schedule page (and print-list page) directly after page 1, before the waves.
- Debrief page after the Endergebnis page (p8) and before the Welle 0 key and the clue matrix.
- Add both to the contents list on page 1 (`master.tex.j2:15-26`).

**Test impact:** `tests/test_master_pdf.py::_section_pages` searches for wave titles from page index 1 (RESEARCH Anti-Patterns). Keep revealed wave titles off the new pages and use "Welle N". Fill-report test (`test_master_pdf.py:162-169`): `len(reports) == len(pages)` and `used <= text`. The new pages must each end with `\pagereport`.

### `planspiel/was_neu.py` + `print/templates/was_neu.tex.j2` (one-page sheet)

**Analog:** `planspiel/wave_page.py` (model) and `print/templates/welle.tex.j2` (template). Both are one A4 page with a fill proof.

**Model pattern** (`wave_page.py:1-131`):
```python
WAVE_PAGE_JOB = "spieler-so-funktioniert-eine-welle"

@dataclass(frozen=True)
class WavePage:
    job: str
    title: str
    ...
    def printed_fragments(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(text for text in printed_strings(self) if text and text != self.job))

def build_wave_page(cfg: Config, texts: Texts) -> WavePage:
    view = PreAttackView(cfg, texts)
    words, welle, labels = view.sheet("angriff"), view.sheet("welle"), view.sheet("labels")
    ...
    if measure_id is None:
        raise PrintModelError("...")
```
Use `WAS_NEU_JOB = "spielleitung-was-ist-neu"`. Use `RevealView` or `FacilitatorView` for sheet access (as `master.py` does), not `PreAttackView`. Signature: `build_was_neu(cfg, texts, baseline)`.

**Numbers come from existing single definitions:**
- `review_text.boundary_text`, `penalty_rows`, `rules.penalty_params`, `rules.budget_review_delta` (X and step).
- `cfg.final_index.weight_ros` (k) via `fmt.format_number`.
- `fmt.format_money` and `fmt.format_signed`.

**Value table:** a row registry `(group, label_key, old_text, new_text)` that emits a row only when old != new. "Meaning changed" rows (Budget Review, Exzellenz, Kurswechsel, RoS, KZ rounding, Final-Index) always emit. Rows are grouped and capped. A model test enforces a row budget as a fast proxy for the one-page proof (D-15, priority rules > flow > material > values). RULE rows plus D-29 items (KZ rounding once per wave, Init on upgrade, Final-Index, event order) never collapse.

**Template pattern** (`welle.tex.j2`):
```
\documentclass[a4paper,10pt]{article}
\usepackage{planspiel}
\begin{document}
\raggedright
\attacktitle{\VAR{page.title}}
...
\begingroup\small\noindent\begin{tabularx}{\linewidth}{|>{\raggedright\arraybackslash}p{40mm}|X|}
\hline
\BLOCK{for step in page.steps}
\textrowtop{}\textbf{\color{mhpblue}\VAR{step.heading}}\textrowend{} & \textrowtop{}\VAR{step.text}\textrowend{} \\
\hline
\BLOCK{endfor}
\end{tabularx}\par\endgroup
...
\fillreport{1}
\end{document}
```
For the facilitator-only sheet, open with `\facilitatornotice{...}` as `master.tex.j2:8` does. Use `\footnotesize` for the values table.

**Veil:** `spielleitung-` is not scanned (`audience.scan_profile` returns `None`). Add a model test that no string contains an attack name: `veil.name_hits(text, ctx, audience.PROFILE_NAMES)` (`veil.py:259`). Use "Welle N" in value rows, never attack names.

### `content/mhp_baseline.json` + isolation (D-14)

**Analog:** `content/clues.toml`, a separate content file loaded in the CLI and passed to one builder (RESEARCH Pattern 2), plus `practice` for the isolation tests.

**Loader pattern** (`planspiel/cli.py:246-263`, `:290`):
```python
from planspiel.texts import CLUES_FILE, check_clues, check_texts, load_clues, load_content
...
try:
    cfg = load_config(Path(config))
    content = load_content(Path(content_dir))
    clues = load_clues(Path(content_dir) / CLUES_FILE)
except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError, ValueError) as error:
    print(f"ERROR print.input {config} / {content_dir}: {error}")
...
documents = render.render_all(cfg, texts, Path(print_dir) / "templates", clues=clues)
```
Add `baseline = load_baseline(Path(content_dir) / BASELINE_FILE)` with a fixed constant name. `json.JSONDecodeError` is already caught. Extend `render_all(..., clues=(), baseline=None)`.

**Builder signature pattern** (`render.py:156-160`): every builder takes `(cfg, texts, env, clues)` and "only the master sheet reads the clues". Add `baseline` the same way. Existing builders ignore it. Keep the 4-positional signature working by adding `baseline=None` as a keyword in all builders, or by giving `was_neu` a different call path. The planner should pick one.
```python
DOCUMENT_BUILDERS = (
    attack_worksheets, measure_cards, event_cards, team_booklet, wave_page, story_documents, practice_document,
    master_sheet,
)
```
Append `was_neu_sheet` and `probelauf_sheet`, each returning `{}` when `cfg.session_schedule is None` or `baseline is None`.

**Stamp inputs** (`stamp.py:22-41`): add `"content/mhp_baseline.json"` to both `DATA_INPUTS` and `BUILD_INPUTS`, next to `"content/clues.toml"`. Pin it like `tests/test_print_stamp.py:136-160`:
```python
assert "content/clues.toml" in stamp.DATA_INPUTS
assert "content/clues.toml" in stamp.BUILD_INPUTS
```
Also update the fixture list at `test_print_stamp.py:71,159`.

**Isolation tests**, copied from `tests/test_practice_config.py:102-119`:
```python
def test_the_block_never_reaches_the_real_config_fields(cfg, tmp_path):
    raw = _raw()
    del raw["practice"]
    plain = _load(raw, tmp_path)
    for name in ("default_budget_tier", "budget_tiers", ...):
        assert getattr(cfg, name) == getattr(plain, name), name
    assert dataclasses.replace(cfg, practice=None) == plain
```
For the baseline: a grep or AST test that `mhp_baseline` occurs only in `was_neu.py`, `cli.py`, `stamp.py` and tests, and that `Config` has no baseline field. Also add the provenance test via `tests/support/gitrepo.py` and `git show 1cfb2fa:simulation_config.json` (skip if the commit is absent). Add `.gitattributes` `content/*.json text eol=lf`.

**Content (RESEARCH §Q1):** use the printed override "boundary = above (25.001)". Record the printed-versus-config difference in the file's `source` block.

### `planspiel/probelauf.py` + `print/templates/probelauf.tex.j2` (`spielleitung-probelauf`)

**Analog:** `wave_page.py` plus `welle.tex.j2` (flat dataclass, `printed_fragments`, `\fillreport{1}`). Reuse the shared schedule rows from the booklet so both read the same config. If a helper is wanted, put it in `planspiel/schedule.py` (optional).

Table: one row per block, with columns label, planned minutes, cumulative minutes, then empty cells (actual start, actual minutes, questions or unclear points, calculation errors). Footer: the pass rule (D-25) as digit-free prose. Landscape is the fallback if 11 rows do not fit portrait. Labels use "Welle N" with no attack names.

### Tests for the new PDFs

**Analog:** `tests/test_wave_page_pdf.py` (marker `pytestmark = pytest.mark.pdf`).

**One-page proof** (`test_wave_page_pdf.py:37-47,81-89`):
```python
def test_the_explainer_is_exactly_one_a4_page(pdf_path):
    reader = PdfReader(pdf_path)
    assert len(reader.pages) == 1
    box = reader.pages[0].mediabox
    assert (round(float(box.width) / 72 * 25.4), round(float(box.height) / 72 * 25.4)) == (210, 297)

def test_the_page_fits_the_text_height_as_measured_in_the_log(printed_set):
    reports = FILL.findall(_log(printed_set))
    assert len(reports) == 1
    number, used, limit = reports[0]
    assert float(used) <= float(limit)
```
Also copy `test_every_printed_fragment_is_on_the_page`, the stamp regex `STAMP = re.compile(r"Stand\d{4}-\d{2}-\d{2}·[0-9a-f]{7}(?:\+lokal)?")` test, and the "no Missing character, Overfull, Undefined control sequence" log test. Skip the layer-two veil test. For `spielleitung-` jobs instead assert `audience.scan_profile(JOB) is None` and run the attack-name check. Helpers: `tests/support/pdf_text.py` (`FILL`, `squash`, `squashed_pages`, `unwrapped_log`, `pdf_text`). Fixture `printed_set` is session-scoped in `conftest.py`.

**Model tests:** copy the shape of `tests/test_wave_page.py` and `tests/test_master_model.py`. Cover the schedule block (cumulative minutes, sum 190, wave 1 = 20), debrief stages (four fixed stages in order, 2-3 items per stage, total 8-12, guide minutes sum to the debrief block), and the print list (every `print_list.job` is a key of `render.render_all(...)`).

### `tests/test_inventory.py` + `content/INVENTORY.md` (LEG-01)

**Analog:** the file itself.

**Pattern to change** (`test_inventory.py:11-40,60-78,106-110`):
```python
FINAL_DOCUMENTS = REPO_ROOT / "final_documents"
EXPECTED_FILES = ("13052026_VWI meets MHP_Offenes Treffen.pptx", ... )   # 20 names

def test_pinned_file_set_equals_the_directory_listing():
    assert _final_document_names() == sorted(_nfc(name) for name in EXPECTED_FILES)

def test_newspaper_images_are_byte_identical_copies():
    original = (FINAL_DOCUMENTS / f"Zeitungsartikel_bild_{name}.png").read_bytes()
```
Split into `KEPT_FILES` (5, in `final_documents/`) and `ARCHIVED_FILES` (15, in `archive/mhp_print_material_2026-07/`). Assert each location and that the archived names are absent from `final_documents/`. Names stay NFC-normalised via `_nfc`.

Replace the byte-identity test with an md5 check against the values recorded in `content/assets/README.md`. Keep `_rows()` parsing (4 cells per row). `INVENTORY.md` needs a location column or section that keeps 4 cells. Update `content/assets/README.md` lines 24-27 and `GUIDELINES.md` lines 3 and 47.

Other adaptations: delete `tests/test_legacy_generators_smoke.py`. In `tests/test_texts_migration.py`, `_measure_meta("generate_pptx_cards.py")` runs at import, so retire or retarget it in the same commit. Remove the `openpyxl==3.1.5` line from `tests/test_environment.py::test_pinned_packages` if openpyxl is dropped. Update the docstring in `tests/test_single_definition.py`. Use `git mv` per file.

### `tests/test_no_archive_references.py` (D-17)

**Analog:** `tests/test_single_definition.py` (scans source files for forbidden strings). Implement RESEARCH §Q5 proofs 1 and 3: a static scan of `planspiel/`, `print/`, `pyproject.toml`, `.gitattributes`, the three root wrappers and `content/*.toml|json` for `archive/`, `pptx_output`, `generate_pptx_cards`, `generate_from_template`, `generate_attack_calculator` and `angriff_berechnung`. A `git ls-files` tree test checks that no `pptx_output/` and no root `*.xlsx` remain and that `final_documents/` holds the five kept files plus `generated/`. The dynamic audit-hook proof is marked [ASSUMED] in RESEARCH; use it only if the hook is gated by a flag.

### README anchor tests (LEG-02)

**Analog:** `tests/test_e_target_removed.py:173-180`. Seven tests pin README and CLAUDE.md phrases:
```python
def test_readme_and_claude_md_describe_no_e_target_check():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8").replace("‑", "-")
    claude_md = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8").replace("‑", "-")
    assert "E-Ziel prüfen" not in readme
    assert "E-Ziel-Check" not in claude_md
    assert "Angriff + E-Ziel" not in claude_md
```
The anchors the rewrite must keep (or change in the same commit) are listed in RESEARCH §Q6a:
- `test_budget_review.py:290-293`
- `test_budget_review_text.py:135-137`
- `test_kurswechsel.py:268-273`, including exactly one "Maßnahmenwechsel"
- `test_paths.py:349-354`
- `test_ros_ledger.py:158-163`, with exactly one "Gesamtkosten" line that contains "Kurswechsel"
- `test_sparprogramm.py:190-192`
- `test_e_target_removed.py:173-180`

Run after each README edit: `uv run pytest tests/test_budget_review*.py tests/test_kurswechsel.py tests/test_paths.py tests/test_ros_ledger.py tests/test_sparprogramm.py tests/test_e_target_removed.py -q`. README stays German (D-20). Root CLAUDE.md is rewritten in English (D-20, D-21) and must not contain "E-Ziel-Check".

## Shared Patterns

### Job registration and audience
**Source:** `planspiel/render.py:156-172`, `planspiel/audience.py`, `planspiel/texbuild.py` (`JOB_NAME`)
**Apply to:** `spielleitung-was-ist-neu`, `spielleitung-probelauf`
```python
for builder in DOCUMENT_BUILDERS:
    for job, source in builder(cfg, texts, env, clues).items():
        texbuild.check_job_name(job)      # ^[a-z0-9][a-z0-9_-]*$
        audience.audience_of(job)         # prefix required
        if job in documents:
            raise ValueError(...)
```

### Builder returns empty without its config block
**Source:** `render.master_sheet` / `render.practice_document` (`render.py:129-135`)
**Apply to:** schedule, was_neu, probelauf builders
```python
doc = build_practice_document(cfg, texts)
if doc is None:
    return {}
return {doc.job: env.get_template("uebung.tex.j2").render(doc=doc)}
```
Mini fixtures (`tests/fixtures/mini_config.json`, `mini_content/`) must stay unchanged.

### Models hold finished strings; templates only loop
**Source:** `master.tex.j2` header comment, `wave_page.py`, `printed_strings` (`planspiel/cards.py`)
**Apply to:** all new models. Provide `printed_fragments()`. Add a test that every fragment appears in the PDF text.

### Numbers from config; prose from texte.toml
**Source:** `texts.py` `check_digits` and `required_keys`; `validate.py` prose-in-config error
**Apply to:** every new string. No typed digits in prose, and no prose in `session_schedule`.

### Fill-report page proof
**Source:** `print/planspiel.sty:144` (`\fillreport{n}`), `tests/support/pdf_text.py` `FILL`
**Apply to:** the new booklet pages (`\pagereport`) and both new one-page PDFs (`\fillreport{1}` plus `len(pages) == 1`).

### Print set written once, last
**Source:** precedent 05-16, 06-10; `planspiel/stamp.py`
**Apply to:** the FLOW-05a plan only. Commit every input first (including `planspiel/`, `print/`, `pyproject.toml`, `uv.lock` and `content/mhp_baseline.json`). Then run `uv run planspiel print`, then `uv run planspiel print --check` (exit 0, no "+lokal"). Then commit `final_documents/generated/`. Do not run `-m slow`, `-m balance` or `gate --paths` (not needed, no rule change).

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| Intro deck `Planspiel_Einführung + Grundlagen.pptx` edit | manual asset | file-I/O | No repo code edits pptx in place. Use the python-pptx run-level snippet in RESEARCH Code Examples: set `runs[0].text`, blank the rest, never use `paragraph.text`, work on a copy, and get checklist approval first (D-18). |
| Dry-run record `07-DRYRUN.md` and the 2026-11-25 run | human event | n/a | Cannot be automated. Use the protocol PDF; findings become gap-closure plans (D-06, D-25). |
| `.planning/codebase/STACK.md`, `CONVENTIONS.md`, `ARCHITECTURE.md` and `.claude/CLAUDE.md` | docs | n/a | Hand-edit the three maps in short summarised form, then run `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" generate-claude-md --auto` (RESEARCH §Q6c). |
| `README.md`, `docs/folienkonzept_spielphasen_mechtech.md` | docs | n/a | Content rewrite or archive. The README is bound by the anchor tests above. The `docs/` file moves to `archive/historical_docs/` (D-30). |

## Metadata

**Analog search scope:** `planspiel/` (config, validate, texts, master, wave_page, practice, render, stamp, cli), `print/templates/`, `content/texte.toml`, `tests/` (practice config, wave page PDF, master PDF, inventory, print stamp, digits, e-target)
**Files read in full or in targeted ranges:** about 20, plus CONTEXT.md and RESEARCH.md
**Pattern extraction date:** 2026-11-02
