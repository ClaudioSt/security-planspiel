# Phase 5: Player & Facilitator Print Material - Pattern Map

**Mapped:** 2026-10-23
**Files analyzed:** 41 new/modified (grouped by requirement, one plan each)
**Analogs found:** 38 / 41 (3 partial or none, listed at the end)

Scope note: `.planning/codebase/*.md` is stale. Everything below was read from `planspiel/`, `print/`, `tests/`, `content/`. Line numbers refer to the files as of this mapping (2026-10-23). Companion research (F1..F15, probe results) lives in `05-RESEARCH.md`; this file only supplies the copy-from excerpts.

## The one analog that matters most

Phase 4 delivered a complete vertical slice. Almost every new document is a copy of it:

| Layer | Analog file | What to copy |
|-------|-------------|--------------|
| Model (frozen dataclass of finished strings + `printed_fragments()`) | `planspiel/printmodel.py` | `AttackSheet`, `Box`, `Line`, `PrintModelError`, `build_attack_sheet(s)` |
| Registry / Jinja env | `planspiel/render.py` | `DOCUMENT_BUILDERS`, `render_all`, `tex_escape` as `finalize` |
| Template | `print/templates/angriff.tex.j2` | `\BLOCK{}`/`\VAR{}` delimiters, `fillline` macro, `\fillreport{n}`, plain-name variables only |
| Style | `print/planspiel.sty` | colours, `\step`, `\hint`, `\refline`, fill boxes, footer + `LastPage` |
| Text access | `planspiel/texts.py` `PreAttackView` / `RevealView` / `FacilitatorView` | veiled vs revealed vs facilitator access |
| Formatting | `planspiel/fmt.py`, `planspiel/review_text.py` | `format_number/_signed/_money/_factor/_percent`, `format_eur`, `penalty_rows`, `boundary_text` |
| Numbers | `planspiel/rules.py` | `worksheet_constants`, `evaluate_path`, `evaluate_plan`, `swap_credit`, `wave_kz_change`, `clamp_kz` |
| Tests | `tests/test_print_model.py`, `tests/test_print_render.py`, `tests/test_print_worksheets_pdf.py`, `tests/conftest.py::printed_set` | SETUPS mini/real parametrisation, fragment-in-tex, fragment-in-pdf, fill markers |

## File Classification (grouped by requirement / plan)

### VEIL-02 (wave 1, owns audience registry)
| New/Modified File | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|
| `planspiel/audience.py` (new) | utility | request-response (lookup) | `texbuild.check_job_name` (`planspiel/texbuild.py:63`) | role-match |
| `planspiel/veil.py` (new) | utility (scanner) | transform | `texts.giveaway_hits` / `normalize_for_matching` / `check_clues` (`planspiel/texts.py:341-570`) | role-match |
| `planspiel/render.py` (mod: call `audience_of` per job) | service | batch | itself (`render_all`, lines 78-87) | exact |
| `planspiel/cli.py` (mod: `ERROR print.veil` gate in `_print_command`) | controller | request-response | `_print_command` error blocks (`cli.py:151-190`) | exact |
| `planspiel/texts.py` (mod: `PREWAVE_SHEETS`, `SHEET_KEYS`) | config | CRUD | itself (lines 26-88) | exact |
| `tests/test_veil_*.py`, `tests/test_veil_pdf.py` (new) | test | transform | `tests/test_story_veil.py`, `tests/test_texts_giveaway.py`, `tests/test_print_worksheets_pdf.py` | role-match |
| `tests/test_print_render.py`, `tests/test_print_model.py` (mod: job lists to prefix filters) | test | request-response | themselves (`test_print_render.py:52-58`, `test_print_model.py:51`) | exact |

### PRINT-05 (wave 2)
| `planspiel/cards.py` (new) | model | transform | `planspiel/printmodel.py` | exact (role) |
| `planspiel/rules.py` (mod: `card_facts`, `level_requirements`) | service | transform | `rules.compute_cia` / `_requirements_met` (`rules.py:10-30`) | exact |
| `print/templates/karten.tex.j2` (new) | template | transform | `print/templates/angriff.tex.j2` | role-match |
| `print/planspiel.sty` (mod: card sheet macros) | config | n/a | itself | exact |
| `planspiel/texbuild.py` (mod: `TEX_PROBES` tikz/pgf) | config | n/a | `TEX_PROBES` (`texbuild.py:19-28`) | exact |
| `print/miktex-packages.txt` (mod) | config | n/a | itself | exact |
| `tests/test_cards_*.py`, `tests/test_cards_pdf.py`, `tests/test_print_documents_pdf.py` (new) | test | transform | `tests/test_print_model.py`, `tests/test_print_worksheets_pdf.py` | exact |
| `tests/fixtures/mini_content/texte.toml`, `content/texte.toml` (mod) | config | n/a | existing `[sheets.*]` keys | exact |

### PRINT-06 (wave 3)
| `planspiel/eventtext.py` (new) | service | transform | `planspiel/review_text.py` + `rules.evaluate_event` (`rules.py:374`) | role-match |
| `planspiel/review_text.py` (mod: `tier_rows`) | utility | transform | `boundary_text`, `penalty_rows` | exact |
| `planspiel/cards.py` (mod: event deck builder) | model | transform | PRINT-05 deck | exact |
| `tests/test_event_text.py`, `tests/test_event_cards.py` (new) | test | transform | `tests/test_budget_review_text.py`, `tests/test_rules_semantics.py` | role-match |

### PRINT-07 (wave 4)
| `planspiel/booklet.py` (new) | model | transform | `planspiel/printmodel.py` | exact (role) |
| `print/templates/teamheft.tex.j2` + `teamheft_budget.tex.j2` + `teamheft_ros.tex.j2` (new) | template | transform | `angriff.tex.j2` | role-match |
| `tests/test_booklet_*.py` (new) | test | transform | `tests/test_print_model.py` | role-match |

### PRINT-08 (wave 5)
| `planspiel/booklet.py` (mod: `TrackingRow`, tracking page) | model | transform | `AttackSheet` + `rules.evaluate_path` | role-match |
| `planspiel/rules.py` (mod: `KZ_MIN/KZ_MAX`) | utility | n/a | `clamp_kz` (`rules.py:84`) | exact |
| `print/templates/teamheft_tracking.tex.j2` (new) | template | transform | `angriff.tex.j2` | role-match |
| `tests/test_tracking_*.py` (new) | test | transform | `tests/test_kurswechsel.py`, `tests/test_ros_ledger.py` | role-match |

### PRINT-09 (wave 6)
| `planspiel/wave_page.py` (new) | model | transform | `printmodel.py` | role-match |
| `print/templates/welle.tex.j2` (new, TikZ flow diagram) | template | transform | `angriff.tex.j2` | partial (TikZ is new) |
| `tests/test_wave_page.py` (new) | test | transform | `tests/test_print_model.py` | role-match |

### PRINT-12 (wave 7)
| `planspiel/story.py` (new) | model | transform | `PreAttackView.story` (`texts.py:447`) + `printmodel.py` | role-match |
| `print/templates/story_*.tex.j2` x4 (new) | template | transform | `angriff.tex.j2` | partial |
| `planspiel/texbuild.py`, `planspiel/stamp.py` (mod: asset set) | service | file-I/O | `STATIC_FILES` handling (`texbuild.py:31,236`), `stamp.DATA_INPUTS` (`stamp.py:22`) | exact |
| `tests/test_story_*.py` (new) | test | file-I/O | `tests/test_clues.py`, `tests/test_story_veil.py`, `tests/test_print_stamp.py:151` | role-match |

### FLOW-01 (wave 8)
| `simulation_config.json` + `planspiel/config.py` (mod: `practice`) | config | CRUD | `Config` trailing fields / `Attack`, `Wave` dataclasses (`config.py:9-40`) | exact |
| `planspiel/validate.py` (mod: `check_practice`) | service | transform | existing raw-dict checks in `validate.py` | role-match |
| `planspiel/practice.py` (new) | service | transform | `printmodel.build_attack_sheet` + `dataclasses.replace(cfg, ...)` | role-match |
| `print/templates/angriff.tex.j2` (mod: filled variant) | template | transform | itself | exact |
| `planspiel/printmodel.py` (mod: `Box.value`) | model | transform | itself | exact |
| `content/texte.toml` `[practice.*]`, `planspiel/texts.py` (mod) | config | n/a | `[attacks.*.revealed]` shape + `required_keys` (`texts.py:232`) | role-match |
| `tests/test_practice_*.py`, `tests/test_welle0_*.py`, `tests/golden/welle0.json` | test | transform | `tests/test_worksheet_equivalence.py`, `tests/support/worksheet_replay.py`, `tests/golden/*` | exact |

### PRINT-10 (wave 9, final regeneration)
| `planspiel/master.py` (new) | model | transform | `printmodel.py` + `FacilitatorView.clue_matrix` | role-match |
| `planspiel/rules.py` (mod: `path_trace`) | service | transform | `evaluate_path` (`rules.py:703`) | exact |
| `planspiel/fmt.py` (mod: `format_approx`) | utility | transform | `format_number` | exact |
| `simulation_config.json`, `config.py`, `validate.py` (mod: `reference_plans`, `final_index`) | config | CRUD | as FLOW-01 | exact |
| `rules.final_index` callers (`report.py:104,397`, `balance.py:316`, `analyze.py:71,90,126,138`) | service | transform | self | exact |
| `planspiel/stamp.py` (mod: add `content/clues.toml` to inputs) | service | file-I/O | `DATA_INPUTS`/`BUILD_INPUTS` | exact |
| `print/templates/master.tex.j2` (new) | template | transform | `angriff.tex.j2` | role-match |
| `tests/test_master_*.py`, `tests/test_path_trace.py`, `tests/test_reference_plans.py`, `tests/golden/answer_keys.json` | test | transform | `tests/test_worksheet_equivalence.py`, `tests/test_characterization.py` | role-match |

---

## Pattern Assignments

### Shared: the print model (applies to cards.py, booklet.py, wave_page.py, story.py, practice.py, master.py)

**Analog:** `planspiel/printmodel.py`

**Module docstring + imports** (lines 1-24): the docstring states "template inserts strings only; no formula derived here". Imports are from `planspiel.fmt`, `planspiel.config`, `planspiel.rules`, `planspiel.texts`. Copy this shape:
```python
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional

from planspiel import fmt
from planspiel.config import Config, Wave
from planspiel.rules import (BonusRow, RecoveryRow, WorksheetConstants, WorksheetInvariantError, attack_kz_delta, worksheet_constants)
from planspiel.texts import RevealView, Texts
```

**Error type** (lines 36-37): `class PrintModelError(ValueError)`. `cli._print_command` already maps it to `ERROR print.model`. Reuse it for every new build guard (card overflow estimate, practice properties, reference-plan legality). Do not invent a new exception unless `cli.py` is also extended.

**Frozen dataclass, exact fields + display strings** (lines 60-106): exact values carry the `WorksheetConstants` field names, display strings are separate fields. New models follow: `@dataclass(frozen=True)`, `job: str` field, finished strings only, `tuple[...]` not `list`.

**`printed_fragments()` convention** (lines 108-146): take only strings containing a digit, strip boxes, `dict.fromkeys` de-dupe. Every new model gets this method; the pdf test asserts each fragment appears in the squashed PDF text.

**Build order** (lines 183-205): view first (`RevealView(cfg, texts)`), constants via `worksheet_constants` inside `try/except WorksheetInvariantError` converted to `PrintModelError(f"Welle {n}: {error}")`.

**Money and numbers** (lines 207, 253): `number = fmt.format_number`; money via `fmt.format_money(eur)`. D-25: euros with thousands dot everywhere, no k€. Config costs are in k€ in `Event`/`MeasureLevel` (see `rules.swap_credit` returning k€ units); multiply by 1000 before `fmt.format_money`, as `review_text.boundary_text` does (`minimum * 1000`).

**Veiled title** (line 304): `view.attack_title(wave)` yields "Angriff N". Pre-wave models must call `PreAttackView.attack_title`, never `RevealView`.

---

### VEIL-02: `planspiel/audience.py`, `planspiel/veil.py`

**Analog (job-name validation):** `planspiel/texbuild.py:63` `check_job_name`. `audience.py` is the same size and shape. Use the research sketch (`_BY_PREFIX`, `audience_of` raising `ValueError`, German message).

**Analog (text matching):** `planspiel/texts.py`
- `normalize_for_matching` (line 341), `_DASHES`/`_INVISIBLE` tables (335-336), `_WORD` (337), `PROFILES = ("veiled", "story")` (338)
- `giveaway_hits(text, terms, attack_ids, *, profile)` (347): profile-based term sets, token vs stem. The scanner must reuse `GiveawayTerms` and `normalize_for_matching`, not reimplement.
- `check_clues` (528-575): squash + NFC + case-sensitivity precedent for matching quotes against rendered text.
- `Issue` objects (`level`, `code`, `path`, `message`) are printed by the CLI as `ERROR print.texts {code} {path}: {message}` (`cli.py:~164`). The veil gate should print `ERROR print.veil ...` in the same format right after the render step.

**Build gate integration** (`planspiel/cli.py:176-190`): insert after `documents = render.render_all(...)` and before `stamp.compute_stamp(...)`, copying this block:
```python
    except PrintModelError as error:
        print(f"ERROR print.model {error}")
        print("1 Fehler")
        return failure
```

**Scan input:** layer 1 scans the dict returned by `render_all` (`{job: .tex}`); layer 2 uses `printed_set` (`tests/conftest.py:49-60`) and `pypdf.PdfReader`.

**Test excerpt to copy for the pdf layer** (`tests/test_print_worksheets_pdf.py:22-37`):
```python
pytestmark = pytest.mark.pdf

def _squash(text: str) -> str:
    return re.sub(r"\s+", "", text.replace(" ", " "))

def _pages(pdf_path):
    return [_squash(page.extract_text()) for page in PdfReader(pdf_path).pages]
```
Use `printed_set.out_a / f"{job}.pdf"` and `printed_set.jobs`.

**Weight triples:** take from `rules.worksheet_constants(cfg, wave)` (`w_c, w_i, w_a`) formatted with `fmt.format_number` (F1 forbids `.weights` outside `rules`/`config`; `printmodel.py:309-311` shows the allowed access).

**Hard-coded job lists to fix first** (F5): `tests/test_print_render.py:52-58` (`test_jobs_equal_the_model_jobs`, `test_real_jobs_are_the_three_attack_worksheets`) and `tests/test_print_model.py:51`. Change to `[j for j in documents if j.startswith("angriff-")]`.

---

### PRINT-05: `planspiel/cards.py`, `rules.card_facts`, `karten.tex.j2`

**Analog (model):** `printmodel.py` as above. Card dataclass has a `kind` and a block list (so PRINT-06 reuses it); no field for bonus, weights, wave, attack (VEIL-04).

**Analog (rules accessor), `planspiel/rules.py:10-30` (read via `_requirements_met`, `dependencies_satisfied`, `compute_cia`):** put `card_facts(measures, measure_id, level)` and `level_requirements(measure, level)` right beside `_requirements_met` so the dependency rule has one definition. The AST guard `tests/test_single_definition.py:140-150` bans `.init .opex .weights .bonus .e_threshold ...` outside `rules.py`/`config.py`; `.cia`, `.name`, `.levels`, `.dependencies` are fine elsewhere. Pattern from `rules.swap_credit` (lines 337-345) shows how accessors read `measures[x].levels[lvl].init` inside rules.

**Text access:** `PreAttackView.measure(id)` (`texts.py:426-435`) returns `focus`, `description`, `levels_desc`, `levels_simple` (dict level -> text). Use this, not raw `Texts`.

**Template skeleton to copy** (`print/templates/angriff.tex.j2:1-12`): Jinja comment line `\#{ ... }`, `\documentclass[a4paper,10pt]{article}`, `\usepackage{planspiel}`. Cards additionally `\usepackage{tikz}` in the template (packages stay out of the sty). Loops: `\BLOCK{for row in ...}` ... `\BLOCK{endfor}`. Variables must be plain names (test `test_template_variables_are_plain_names` in `tests/test_print_render.py` uses `PLAIN_VARIABLE = ^[A-Za-z_][A-Za-z0-9_.\[\]'\"]*$`).

**Footer/stamp on a zero-margin card page:** copy research Pattern 3 (shipout hook with TikZ overlay, `\footerstamp`, `LastPage` label). Existing footer mechanism to mirror: `planspiel.sty` lines 38-52 (`\ps@planspiel`, `\AtEndDocument{...\newlabel{LastPage}...}`).

**Fit proof:** copy the `\fillreport{n}` mechanism (defined in `planspiel.sty`, used at `angriff.tex.j2` "\fillreport{1}") and regex from `tests/test_print_worksheets_pdf.py:21`:
```python
FILL = re.compile(r"PLANSPIEL-FILL page=(\d+) used=([0-9.]+)pt text=([0-9.]+)pt")
```
Add a sibling `PLANSPIEL-CARD id=.. used=.. limit=..` marker.

**Colours / badges:** `planspiel.sty` lines 24-33 define `mhpblue, mhpaccent, mhplight, mhpgrey, mhpdark, levelone, leveltwo, levelthree`; `\levelbadge` is used in `angriff.tex.j2` bonus table (`\levelbadge{\VAR{row[1]}}`). IN-04: add the `\else` error branch when extending it for levels > 3.

**TeX probes:** add to `TEX_PROBES` (`texbuild.py:19-28`) in the same one-line-per-file format, plus `pgf` and `graphics` lines in `print/miktex-packages.txt`:
```python
    "tikz.sty": "pgf",
    "graphicx.sty": "graphics",
    "multicol.sty": "tools",
```

**Mini fixtures:** mini config has only M1, M2, M4, M6 (`tests/fixtures/mini_config.json`). Cards for the mini set: 4 x 3 + legend = 13. Add every new `sheets.*` key to `tests/fixtures/mini_content/texte.toml` in the same commit.

**Test shape:** copy `tests/test_print_model.py` (SETUPS parametrisation lines 21-28, `loaded`/`real` fixtures lines 31-42) and `tests/test_print_render.py` (SETUPS lines 17-26, `loaded` fixture lines 29-35, `test_every_printed_fragment_is_in_the_tex` line ~72).

---

### PRINT-06: `planspiel/eventtext.py`, `review_text.tier_rows`, event deck

**Analog (text generation from config):** `planspiel/review_text.py`
```python
def penalty_rows(kz_per_step: int, step_k: int, max_kz: int = 100) -> List[Tuple[int, int, int]]:
    count = -(-max_kz // kz_per_step)
    return [((i - 1) * step_k * 1000 + 1, i * step_k * 1000, -kz_per_step * i) for i in range(1, count + 1)]

def boundary_text(tiers: List[List[int]]) -> str:   # lines 29-39
    ...
    parts = [f"0 – {format_eur(tiers[1][0] * 1000 - 1)} € → {_tier_value_text(tiers[0][1])}"]
```
`tier_rows` returns a list of structured rows with the same inclusive-boundary semantics as `boundary_text` and `rules._tier_lookup` (`rules.py:282`, highest tier whose minimum <= value). Keep `_tier_value_text` (uses real minus and "±0").

**Analog (what the effect must equal):** `rules.evaluate_event(event, selection, remaining_budget)` (`rules.py:374`) returns a tuple; `rules.penalty_params(final_events)` (`rules.py:309`) gives `(kz_per_step, step)`; `rules.kurswechsel_wave(events)` (`rules.py:366`) for the "nach Welle N" line.

**Equivalence test pattern:** `tests/test_budget_review.py`, `tests/test_rules_semantics.py` (explicit-input vs `rules` function). Build a selection per row, assert `rules.evaluate_event(...)[0]` equals the row's value.

**Event texts:** `PreAttackView.event(event_id)` (`texts.py:444`) -> narrative/rule/tier_labels subtree; `EVENT_KEYS_BY_TYPE` (`texts.py:88`) lists the keys per type. Never generate digits in `texte.toml` (digit lint); numbers come from `eventtext`.

**Budget Review on the card:** reuse `review_text.tier_rows` and `penalty_params`; the 12-row lookup (`penalty_rows`) goes to the booklet, not the A6 card.

---

### PRINT-07: `planspiel/booklet.py` (planning + RoS pages)

**Analog:** `printmodel.py` for model shape; text keys already exist under `sheets.budget.*`, `sheets.ros.*`, `sheets.labels.*` (read through `PreAttackView.sheet("budget")` etc., `texts.py:452-455`, whitelist `PREWAVE_SHEETS`).

**Tier table values:** `cfg.budget_tiers` (dataclass `BudgetTier(name, budget, kz_start, severity_multiplier)`; see `rules`/`config.py`), formatted `fmt.format_money(budget * 1000)`. Tier names via `str.capitalize()` of the key.

**RoS base losses:** `rules.base_losses(cfg.waves, cfg.attacks)` (`rules.py:567`). Do not type 620.000. No "Event-Strafen" row (F8; `rules.security_spend` at `rules.py:43` is the definition: `security_spend(init, opex_by_wave, window_costs)`).

**Template composition:** `teamheft.tex.j2` uses Jinja `\BLOCK{include "teamheft_budget.tex.j2"}` for partials so PRINT-08 adds a partial without editing the same body. Partials must not repeat `\documentclass`.

**Penalty table:** `review_text.penalty_rows(kz_per_step, step_k)`; add a build guard on a maximum row count (12 today) raising `PrintModelError`.

---

### PRINT-08: tracking sheet (`TrackingRow` in `booklet.py`)

**Analog (numbers):** `rules.evaluate_path` (`rules.py:703`) is the reference for window/ledger semantics: windows after waves 1 and 2 only (`len(path.windows) > wave_count - 1` raises `PathError`), `rules.window_cost` (`rules.py:675`) for "Init-Differenz netto":
```python
def window_cost(measures, before, after, swap=None) -> int:
    cost = 0
    for measure_id, measure in measures.items():
        gain = measure.levels[after.get(measure_id, 0)].init - measure.levels[before.get(measure_id, 0)].init
        cost += max(0, gain)
    if swap is not None:
        dropped, incoming = swap
        cost -= swap_credit(measures, before, dropped, incoming, after)
    return cost
```
Kurswechsel credit row uses `rules.swap_credit` semantics (lines 337-345, shown in file above).

**KZ clamp constants:** replace the literals in `clamp_kz` (`rules.py:84-85`):
```python
def clamp_kz(value: int) -> int:
    return max(0, min(100, value))
```
with module constants `KZ_MIN = 0`, `KZ_MAX = 100` used by both `clamp_kz` and print code. Rounded wave change: `rules.wave_kz_change(attack_kz_delta, event_kz)` (`rules.py:211`).

**External vs own costs:** own = Init + OPEX + window Init differences = `rules.security_spend`; external = `flat_budget` and `opex_discount_per_active_measure` event kinds (`eventtext` kind classifier from PRINT-06). `rules.budget_ledger(tier_budget, own_spend, event_opex, event_budget)` (`rules.py:602`) returns a `BudgetLedger` NamedTuple for the remaining-budget row.

**Tests:** `tests/test_kurswechsel.py`, `tests/test_ros_ledger.py`, `tests/test_swap_layer.py` for how a worked swap path is built; assert the delta rows sum to `evaluate_path(...)["windows"][0]["cost"]`.

---

### PRINT-09: `planspiel/wave_page.py`, `welle.tex.j2`

**Analog (step vocabulary):** `printmodel.py:211-217` builds `step_headings` from `angriff[f'step_{key}']` and `labels['step']`; the wave page must reuse the same `sheets.angriff.step_*`/`sheets.labels.*` keys through the `RevealView.sheet("angriff")`-equivalent for pre-wave. NOTE: `PreAttackView.sheet()` only allows `PREWAVE_SHEETS`; either add the needed step keys to a new pre-wave sheet section (`sheets.welle`) or extend `PREWAVE_SHEETS` knowingly. Do not call `RevealView` from `wave_page.py` (AST guard from VEIL-02).

**Recovery table:** generated from `worksheet_constants(...).recovery_rows` is revealed-only; for the generic M4 table use the new `rules.card_facts`/recovery accessor from PRINT-05 (not `.recovery` directly: banned attribute, F1). Narrative text from `[sheets.backup_recovery]` via `PreAttackView.sheet("backup_recovery")` (`printmodel.py:201` shows `level_labels` access).

**TikZ:** no in-repo analog (see "No Analog Found"). Copy the research Pattern 3 overlay for placement; probes as in PRINT-05.

**Rounding sentence:** copy how `wave_kz_rounding` is used (`printmodel.py:291`, text key `angriff["wave_kz_rounding"]`): the `,5` token is digit-allowlisted.

---

### PRINT-12: `planspiel/story.py`, `story_*.tex.j2`, asset mechanism

**Analog (text access):** `PreAttackView.story(doc)` (`texts.py:447-450`), `STORY_DOCS` (`texts.py:25`); content shapes in `[story.*]` (see research PRINT-12).

**Analog (static file copy + hash):** `texbuild.py:31` `STATIC_FILES = ("planspiel.sty",)`, loop at `texbuild.py:236` (`for name in STATIC_FILES:`), and `stamp.py:22,25` `DATA_INPUTS` / `BUILD_INPUTS`. Extend with a fixed-name asset tuple (e.g. `ASSET_FILES = ("zeitung_1.png", "zeitung_2.png")` mapped from `content/assets/images`); never let content strings choose file names. Add `content/assets/images` to `DATA_INPUTS` and `BUILD_INPUTS`. The guard test `test_tex_read_nothing_outside_the_hashed_set` (`tests/test_print_stamp*.py`) must list the PNGs as allowed.

**Analog (SC6 clue check):** `texts.check_clues` / `_clue_document` / `_source_strings` (`texts.py:507-575`) and `tests/test_clues.py`; the new PDF test squashes both sides (same `_squash` helper as the worksheet pdf test) and matches `clues.toml` quotes against the PDF for their source document. Do not upper-case headings.

**Fonts:** Georgia selected by name (like Arial in `planspiel.sty:13-16`: `\setmainfont{Arial}[RawFeature={-tlig}]`); newspaper template uses `\newfontfamily` with Georgia by name only.

**Layout packages:** `multicol`, `graphicx`: add per template + TEX_PROBES (see PRINT-05).

---

### FLOW-01: practice block, `planspiel/practice.py`, Welle 0 document

**Analog (config dataclasses):** `planspiel/config.py` lines 9-40 (`Attack`, `BonusMeasure`, `Wave` plain dataclasses). F13: add `practice` as a trailing `Config` field with a default of `None`; `load_config` reads the optional top-level key; nothing else reads it. Tests build variants with `dataclasses.replace(cfg, ...)`.

**Practice config view (verified in research probe):**
```python
def practice_config(cfg):
    p = cfg.practice
    tier = BudgetTier("practice", p.budget, p.kz_start, Fraction(1))
    return dataclasses.replace(
        cfg, attacks={**cfg.attacks, "practice": p.attack}, waves=[p.wave],
        events={p.wave.wave_id: [p.event]}, final_events=[], budget_tiers={"practice": tier})
```
Everything downstream (`worksheet_constants`, `simulate_waves`, `evaluate_plan` at `rules.py:630`) runs unchanged on this view.

**Filled worksheet:** modify `printmodel.Box` (line 41-44, `size: str`) to add `value: Optional[str] = None`, and the `fillline` macro in `angriff.tex.j2` (lines 2-6):
```
\fillline{\BLOCK{for part in parts}\BLOCK{if part is string}\VAR{part}\BLOCK{else}\ibox{\VAR{part.size}}\BLOCK{endif}\BLOCK{endfor}}
```
to print `part.value` when set. Real sheets must stay byte-identical (value `None`). `build_attack_sheet` (`printmodel.py:183`) reads revealed text through `RevealView.attack(...)`; add a small adapter that supplies practice texts from `[practice.*]`.

**Build guards (Fall 3, one bonus met and one missed, recovery > 0, non-integer wave change, clamp active):** raise `PrintModelError` in the style of `printmodel.py:191-196`.

**Golden/equivalence:** `tests/support/worksheet_replay.py` (`replay_steps` returns `case`, `damage_before_eur`, `damage_eur`, `kz_attack`, `change`) and `tests/test_worksheet_equivalence.py`, `tests/test_worksheet_replay.py`. Pinned JSON follows `tests/golden/*` with `--update-golden` (`tests/conftest.py:12-35`).

**Texts:** `[practice.*]` section; add to `required_keys` (`texts.py:232`) only `if cfg.practice`; `check_giveaway` scoped list (`texts.py:372`) gets the new prefix with the `story` profile; strict digit lint.

---

### PRINT-10: `planspiel/master.py`, `rules.path_trace`, reference plans, D-23

**Analog (path evaluation, the reference for trace):** `rules.evaluate_path` (`rules.py:703-780`), `Path`/`Window` NamedTuples (659-666):
```python
class Window(NamedTuple):
    selection: Dict[str, int]
    swap: Optional[Tuple[str, str]] = None

class Path(NamedTuple):
    start: Dict[str, int]
    windows: Tuple[Window, ...] = ()
```
`path_trace` is a new read-only function in `rules.py` beside `evaluate_path`, deriving recovery factor (`compute_recovery`, line 48), Fall, damage before recovery (`damage_euros`, line 76), rounded change (`wave_kz_change`), clamp (`clamp_kz`), running remaining (`budget_ledger`). Never add keys to `simulate_waves` (F2: characterization goldens pin the whole per-wave dict).

**Analog (quick-check rows):** `worksheet_constants` (`rules.py:141-200`) + `rules.attack_kz_delta(kz_at_full_damage, slope, reduction_scaled, ws)` (line 202). Damage rows `(upper - GR) * unit_eur`. The `printmodel.min_half_distance` loop (`printmodel.py:149-163`) is the template for stepping GR over the `1/ws` lattice.

**Analog (approx format):** `fmt.format_number` (raises on non-terminating values by design, `fmt.py:30-34`). `format_approx(value, places=2)` is a sibling that prints "≈" and rounds half away from zero via `planspiel.rounding.round_half_away` (never builtin `round()`, banned in `rules.py`/`rounding.py`). Used on the facilitator sheet only.

**Analog (clue matrix):** `texts.FacilitatorView.clue_matrix()` (`texts.py:609`) returns `ClueRow`s; `format_clue_matrix` (632) is the existing text rendering to compare. Load clues in `_print_command` with `texts.load_clues(Path(content_dir)/CLUES_FILE)` and pass as an optional keyword to `render_all` (keep the 3-arg signature working; F5).

**Reveal access:** `master.py` may use `RevealView` (`texts.py:643`) for bonus reasons; it is exempt from the pre-wave AST guard.

**D-23 callers of `rules.final_index`** (`rules.py:582-587`, currently with default weights `Fraction(1)`):
```python
def final_index(kz_final, ros, weight_kz=Fraction(1), weight_ros=Fraction(1)) -> Fraction:
```
Remove the defaults; pass `cfg.final_index` weights from `report.py:104` (`summarize_tier`), `report.py:397` (`dump_record`, add a weights param), `balance.py:316`, `analyze.py:71,90,126,138` (CLI `--weight-kz/--weight-ros`: default to config when `--config` given), tests `tests/test_enumeration.py:87,358`, `tests/test_rules_semantics.py:25`, `tests/test_ros_ledger.py:144`.

**Reference plans config:** loader stores plain dicts (config.py cannot import rules); a helper in `master.py` builds `rules.Path`. Legality is asserted by calling `rules.evaluate_path` (raises `PathError`).

**Stamp inputs:** `stamp.py:22` and `:25`:
```python
DATA_INPUTS = ("simulation_config.json", "content/texte.toml", "print/planspiel.sty", "print/templates")
BUILD_INPUTS = ("simulation_config.json", "content/texte.toml", "print", "planspiel", "pyproject.toml", "uv.lock")
```
add `"content/clues.toml"` to both, and update `tests/test_print_stamp.py:151-156` (`test_changes_outside_the_build_inputs_are_not_dirty` currently lists clues.toml as clean) deliberately.

**Final task** (D-19 order): commit inputs, `uv run planspiel print` on a clean tree, `uv run planspiel print --check` exit 0, commit `final_documents/generated/` and `manifest.json`.

---

## Shared Patterns

### Config -> model -> template -> TeX (no arithmetic in templates)
**Source:** `planspiel/render.py:67-87`
```python
def attack_worksheets(cfg, texts, env):
    template = env.get_template("angriff.tex.j2")
    return {sheet.job: template.render(sheet=sheet) for sheet in build_attack_sheets(cfg, texts)}

DOCUMENT_BUILDERS: Tuple[DocumentBuilder, ...] = (attack_worksheets,)

def render_all(cfg, texts, template_dir: Path) -> Dict[str, str]:
    env = make_env(template_dir)
    documents = {}
    for builder in DOCUMENT_BUILDERS:
        for job, source in builder(cfg, texts, env).items():
            texbuild.check_job_name(job)
            if job in documents:
                raise ValueError(f"Dokument {job!r} wird von mehreren Erzeugern geliefert")
            documents[job] = source
    return {job: documents[job] for job in sorted(documents)}
```
**Apply to:** every new document. Add one `def <name>_documents(cfg, texts, env)` per family and append to `DOCUMENT_BUILDERS`. A builder returns `{}` when its config block is absent (mini fixtures), plus a real-config test pinning the job.

### Template escaping
**Source:** `planspiel/render.py:36-46` (`tex_escape` is `finalize`; non-strings raise `TypeError`, control chars raise `ValueError`). Never pass `Fraction`/`int` to `\VAR{}`; format in the model with `fmt`.

### Number formatting
**Source:** `planspiel/fmt.py` (`format_number`, `format_signed`, `format_money`, `format_factor`, `format_percent`, `MINUS`, `TIMES`, `DIVIDED`). Money everywhere in euros with a thousands dot (D-25).

### Formula operands only via rules/config (AST guard)
**Source:** `tests/test_single_definition.py:140-150`. Banned attributes outside `rules.py`/`config.py`: `.s_unit .base_severity .mitigation_cap .kz_at_full_damage .kz_at_full_mitigation .e_threshold .recovery .init .opex .weights .bonus .kz_per_step`. Wave numbers come from `worksheet_constants`; per-measure numbers from the new `rules.card_facts`.

### Style / page furniture
**Source:** `print/planspiel.sty`: stamp include with hard failure (lines 36-39), `suppressoptionalinfo` for byte-identical PDFs (line 5), `\hyphenpenalty=10000` (no hyphenation), footer `\ps@planspiel` (38-52), colours (24-33), `\step`, `\hint`, `\refline`, fill boxes.
**Apply to:** all documents. Extend the sty with sectioned macros only; keep package `\usepackage`s in the templates so the probe drift test sees them.

### Test conventions
**Source:** `tests/test_print_model.py:21-42`, `tests/test_print_render.py:17-35`, `tests/conftest.py` (`printed_set` session fixture, builds the whole set twice for byte-identity), markers `pdf` (real TeX), `slow` (enumeration). Fast tests by default.
```python
SETUPS = [pytest.param((MINI, MINI_CONTENT_DIR), id="mini"), pytest.param((CONFIG_PATH, CONTENT_DIR), id="real")]
```
**Apply to:** every new model/template test; every new text key must also exist in `tests/fixtures/mini_content/texte.toml`.

### Error reporting from the CLI
**Source:** `planspiel/cli.py:151-190`: `ERROR print.<stage> ...`, `"N Fehler"`, return `failure`. New stages (`print.veil`) follow this exactly.

### Veiling
**Source:** `planspiel/texts.py:413-470` (`PreAttackView` cannot read `attacks.*.revealed`), `RevealView` (643), `FacilitatorView` (590). Pre-wave builders use `PreAttackView` only; `practice.py` and `master.py` are exempt by design.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| TikZ flow diagram in `welle.tex.j2` and legend callouts/lock icon in `karten.tex.j2` | template | transform | No TikZ is used anywhere yet; use the research probes (Pattern 3 overlay, `arrows.meta positioning shapes.geometric calc backgrounds fit` verified present). |
| Image inclusion (`\includegraphics`) in story templates | template | file-I/O | No images in any current document; the asset copy+hash mechanism extends `STATIC_FILES` handling (see PRINT-12). |
| `veil.py` PDF layer (pypdf metadata/outline/xmp scan) | utility | transform | Only text extraction exists in tests; metadata scan is new (probe: metadata is `{}` today). |

## Metadata

**Analog search scope:** `planspiel/`, `print/`, `tests/`, `content/`
**Files read in full:** `render.py`, `printmodel.py`, `fmt.py`, `review_text.py`, `angriff.tex.j2` (first 80 lines), `planspiel.sty` (first 80 lines)
**Files read in part (targeted ranges):** `rules.py`, `texts.py`, `texbuild.py`, `cli.py`, `config.py`, `tests/conftest.py`, `tests/test_print_render.py`, `tests/test_print_model.py`, `tests/test_print_worksheets_pdf.py`, `tests/test_single_definition.py`
**Pattern extraction date:** 2026-10-23
