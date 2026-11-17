---
phase: 05-player-facilitator-print-material
reviewed: 2026-10-26T15:09:36Z
depth: standard
files_reviewed: 40
files_reviewed_list:
  - planspiel/audience.py
  - planspiel/veil.py
  - planspiel/cards.py
  - planspiel/eventtext.py
  - planspiel/review_text.py
  - planspiel/booklet.py
  - planspiel/wave_page.py
  - planspiel/story.py
  - planspiel/practice.py
  - planspiel/refpaths.py
  - planspiel/master.py
  - planspiel/rules.py
  - planspiel/config.py
  - planspiel/validate.py
  - planspiel/texts.py
  - planspiel/render.py
  - planspiel/printmodel.py
  - planspiel/texbuild.py
  - planspiel/stamp.py
  - planspiel/cli.py
  - planspiel/fmt.py
  - planspiel/report.py
  - planspiel/simulate.py
  - planspiel/balance.py
  - planspiel/analyze.py
  - print/planspiel.sty
  - print/miktex-packages.txt
  - print/templates/karten.tex.j2
  - print/templates/teamheft.tex.j2
  - print/templates/teamheft_planung.tex.j2
  - print/templates/teamheft_ros.tex.j2
  - print/templates/teamheft_tracking.tex.j2
  - print/templates/welle.tex.j2
  - print/templates/story_steckbrief.tex.j2
  - print/templates/story_zeitungsartikel.tex.j2
  - print/templates/story_mail.tex.j2
  - print/templates/uebung.tex.j2
  - print/templates/angriff.tex.j2
  - print/templates/angriff_blatt.tex.j2
  - print/templates/master.tex.j2
  - simulation_config.json
  - tests/support/pdf_text.py
  - tests/support/tracking_replay.py
findings:
  critical: 0
  warning: 6
  info: 8
  total: 14
status: issues_found
---

# Phase 5: Code Review Report

**Reviewed:** 2026-10-26T15:09:36Z
**Depth:** standard
**Files Reviewed:** 40 production files plus test support helpers and a sample of the phase-5 tests
**Status:** issues_found

## Summary

Scope: `git diff 3a6c0b7^..HEAD -- planspiel print simulation_config.json` (41 files, about 5k lines), the two test support helpers, and a sample of the new phase-5 tests. The fast suite passes (`uv run pytest`: 2272 passed, 153 deselected).

The core invariants hold for the shipped config:

- Every printed number comes from `rules` through `fmt`. `path_trace` reuses `evaluate_path` for legality, window costs and the ledger. Its per-wave remaining budget reconciles with `budget_ledger.remaining_budget`.
- `tex_escape` is the Jinja `finalize` hook. `AssetName` is the only bypass, and only names in `ASSET_FILES` can produce one. Brace-protected macro arguments also cover the one optional argument that carries content (`multicols[...]`).
- The audience prefix gate in `render_all` and the CLI veil gate run before stamping.
- I found no builtin `round()` in `rules.py` or `rounding.py`.

I found no BLOCKER for the current config and content. The findings are mostly latent contract gaps. Each one can surface as a confusing crash or as silently missing print material once content or config changes:

- The validator accepts practice event types that the print model cannot print (WR-01).
- The story models accept fields that the templates never render (WR-02).
- One PDF layout assertion can never fail (WR-03).
- One printed formula is re-derived outside `rules`, and the single-definition guard misses it (WR-04).

I verified WR-01 and WR-02 empirically with a scratch probe; the probe did not modify any repo file.

## Warnings

### WR-01: Validator accepts practice event types that `build_practice_document` crashes on (KeyError)

**File:** `planspiel/validate.py:33` (`PRACTICE_EVENT_TYPES`), `planspiel/validate.py:619`; `planspiel/practice.py:308-312`
**Issue:** `PRACTICE_EVENT_TYPES` allows `checklist_tier`, `level_bonus_per_measure` and `and_condition`. `_event_block`, however, unconditionally reads `block.event.params["measure"]` and needs a row whose `covers` contains that measure's level. Only `measure_level_tier` satisfies both.

I verified this with the real config, changing only the practice event to `{"type": "level_bonus_per_measure", "level": 2, "kz_per_measure": 1}`:
- `validate()` returns no errors, and `check_example` passes.
- `build_practice_document` raises `KeyError: 'measure'`.
- The CLI reports this as `ERROR print.model measure`, which tells the author nothing.

For `checklist_tier`, the rows' `covers` are counts, not levels, so even with a `measure` key the wrong row would be selected or the build would fail.
**Fix:** Restrict the validator to what the print model supports, or make the print model handle every allowed type:
```python
PRACTICE_EVENT_TYPES = ("measure_level_tier",)  # practice._event_block selects the row by the measure's level
```
Alternatively, add a typed guard in `_event_block`:
```python
if block.event.type != "measure_level_tier":
    raise PrintModelError(f"{PREFIX}: Übungsereignis vom Typ {block.event.type} wird nicht gedruckt (nur measure_level_tier).")
```

### WR-02: Story models accept fields that the templates silently drop; this contradicts the "nothing is dropped" contract

**File:** `planspiel/story.py:129-155`; `print/templates/story_mail.tex.j2:21-35`; `print/templates/story_zeitungsartikel.tex.j2:49-59,72-82`; `print/templates/story_steckbrief.tex.j2:13-52`
**Issue:** The `story.py` docstring promises that "nothing a subtree holds is dropped, and an unexpected key … stops the build instead of silently losing text". But `_section` accepts every key in `_SECTION_KEYS`, plus one level of nested subsections, for every document type, and each template renders only a subset:
- `story_mail.tex.j2` never renders `section.subsections`, `dateline`, `lead` or `caption`.
- `story_zeitungsartikel.tex.j2` never renders `section.bullets`, nor `sub.bullets`, `sub.caption`, `sub.dateline` or `sub.lead`. A nested `caption` is also ignored by `_images`.
- `story_steckbrief.tex.j2` never renders `dateline`, `lead` or `caption`.

I verified this by injecting `bullets=("UNIQUEBULLETTEXT",)` into the first newspaper section and a subsection into a mail section. The text appears in `printed_strings()` but not in the rendered `.tex`. These are pre-wave player documents carrying clue quotes. A dropped section means the facilitator clue matrix (VEIL-03) cites a quote that is not on paper. `planspiel print` does not catch this; only the slow PDF test `tests/test_story_pdf.py:121` would.
**Fix:** Give each document type an allow-list in the model and raise `PrintModelError` for anything its template does not render:
```python
_ALLOWED = {
    "steckbrief": {"heading", "headline", "text", "paragraphs", "bullets", "subsections"},
    "zeitungsartikel": {"heading", "headline", "text", "paragraphs", "dateline", "lead", "caption", "subsections"},
    "mail": {"heading", "headline", "text", "paragraphs", "bullets"},
}
# _section(path, node, allowed=..., nested=...): raise PrintModelError for a key (or a nested table) outside `allowed`
```
Alternatively, render the missing fields in the templates.

### WR-03: The "Overfull \vbox" layout assertion can never fail (`\v` is a vertical-tab escape)

**File:** `tests/test_wave_page_pdf.py:105`
**Issue:** `assert "Overfull \vbox" not in log` uses a non-raw string. `\v` is the valid escape for U+000B, so the needle is `"Overfull \x0bbox"`, which never occurs in a TeX log. The wave-page PDF test therefore never detects an overfull vbox, the one layout failure that matters most on a one-page explainer. The neighbouring `"Overfull \hbox"` only works by accident (an invalid escape kept literally, with a SyntaxWarning). The same file family also emits SyntaxWarnings for `"\clearpage"` (`tests/test_event_cards.py:179`).
**Fix:**
```python
assert r"Overfull \hbox" not in log
assert r"Overfull \vbox" not in log
```
Consider adding `-W error::SyntaxWarning` (or `filterwarnings = error::SyntaxWarning` in the pytest config) so this class of bug fails at collection.

### WR-04: Master check table re-derives the damage formula outside `rules`, and the single-definition guard does not see it

**File:** `planspiel/master.py:267-274`
**Issue:** `table_rows` computes each damage value as `(constants.upper - step) * constants.unit_eur`. This is a second encoding of severity × `s_unit` (`rules.damage_euros` via `severity_scaled`). It is only correct while the `worksheet_constants` invariants hold (`base_severity == mitigation_cap`, multiplier 1). `tests/test_single_definition.py` only flags operand attributes such as `.s_unit`, `.mitigation_cap` and `.init`, and does not know `upper`, `lower` or `unit_eur`, so the duplication passes the guard. The KZ column in the same table correctly goes through `rules.attack_kz_delta`; the damage column does not. The same pattern appears in `practice._selection` (`facts.init_k`/`opex_k` sums), but that one is cross-checked against the trace and raises on a mismatch.
**Fix:** Derive the value through the primitive:
```python
damage = rules.damage_euros(
    rules.severity_scaled(attack.base_severity, Fraction(1), (step - constants.lower) * cfg.ws, cfg.ws),
    attack.s_unit, 0, cfg.ws, cfg.rs,
)
```
Alternatively, add a rules helper such as `worksheet_damage_at(constants, gr)`. Extend `OPERAND_ATTRIBUTES` with `upper`, `lower`, `unit_eur`, `init_k` and `opex_k`, so that future re-derivations are flagged.

### WR-05: Facilitator booklet and Welle 0 sheet disappear silently, and their published PDFs are deleted, when a config block is missing

**File:** `planspiel/master.py:455-456`, `planspiel/practice.py:356-357`, `planspiel/render.py` (`master_sheet`, `practice_document` return `{}`), `planspiel/cli.py:296-305`
**Issue:** `build_master_sheet` returns `None` when `reference_plans` is empty, and `build_practice_document` returns `None` without `practice`. Neither block is required by `validate.py`, so removing or misspelling `reference_plans` passes validation. `planspiel print` then builds the set without `spielleitung-uebersicht`, and the publish step deletes the previously published PDF ("Entfernt (nicht mehr im Druckumfang)"). The facilitator answer keys vanish from `final_documents/generated/` with exit code 0. The `None` path exists for the mini test config, but the production CLI cannot tell "intentionally absent" from "accidentally lost".
**Fix:** Require both blocks when printing from the repository config. One option is a validator error for a missing `reference_plans`/`practice`, with the mini config opting out explicitly. Another is for `_print_command` to fail when `render_all` does not produce every job in an expected-jobs list (`MASTER_JOB`, `PRACTICE_JOB`, the story, card and booklet jobs).

### WR-06: `analyze` without `--config` mixes config sources (weights from the repo config, RoS disabled)

**File:** `planspiel/analyze.py:163-173`
**Issue:** Without `--config`, `main` now loads `DEFAULT_CONFIG_PATH` but only reads its final-index weights; `base_losses` stays `None`, so RoS stays disabled. There are two consequences:
- A previously standalone tool (input JSON only) now fails if the repo config does not validate.
- When the results file came from a different config, the Final-Index silently uses weights from a config the results were not generated with, while RoS is ignored.
**Fix:** Either load one config and use it for both, or keep the old explicit behaviour:
```python
cfg = load_config(Path(args.config) if args.config else DEFAULT_CONFIG_PATH)
base_losses = rules.base_losses(cfg.waves, cfg.attacks)
```
Alternatively, require `--weight-*` when `--config` is omitted.

## Info

### IN-01: `ReviewTrace.kz_review_change` is the unclamped sum of the final-event deltas

**File:** `planspiel/rules.py:983`; printed at `planspiel/master.py:399` and `planspiel/refpaths.py:293`
**Issue:** `apply_final_events` clamps after each event. The trace reports `sum(kz_delta)`, so whenever the clamp acts (or with more than one final event), the printed "Budget Review" delta does not reconcile with `kz_final - kz_pre_review`. The current reference paths do not hit the clamp.
**Fix:** Either print `kz_final - kz_pre_review` as the effective change next to the nominal one, or assert in `_reference_traces` that the two agree.

### IN-02: Event-effect filter on the wave page is a no-op

**File:** `planspiel/wave_page.py:100-101`
**Issue:** `kinds = dict.fromkeys(EFFECT_KINDS.values())` is built from the static type map, not from `cfg.events`, so `if kind in kinds` is always true. The page always explains budget, OPEX and KZ event effects, even for a config without such events.
**Fix:** Use `{EFFECT_KINDS[e.type] for events in cfg.events.values() for e in events}` if config-dependence is intended; otherwise drop the filter.

### IN-03: Runtime guard implemented with `assert`

**File:** `planspiel/booklet.py:329`
**Issue:** The tracking-row order check disappears under `python -O`.
**Fix:** `if ...: raise PrintModelError(...)`.

### IN-04: `loop.previtem.group` relies on short-circuiting under StrictUndefined

**File:** `print/templates/teamheft_tracking.tex.j2:11,15`
**Issue:** On the first row `loop.previtem` is undefined. This only works because the first row's group is `kz`. If a group `own` or `external` row is ever first, the template raises `UndefinedError`.
**Fix:** `\BLOCK{if row.group == "own" and (loop.first or loop.previtem.group != "own")}`.

### IN-05: `candidate_paths` hard-codes the swap into window 1

**File:** `planspiel/refpaths.py:171-177`
**Issue:** `Path(start, (swap_window, move))` assumes the Kurswechsel follows wave 1. With a Kurswechsel after wave 2, every candidate raises `swap_without_kurswechsel`, is skipped, and the tool reports "Keine Kandidaten" without a reason.
**Fix:** Place the swap at `[w.wave_id for w in cfg.waves].index(rules.kurswechsel_wave(cfg.events))`.

### IN-06: Practice `kz_start` is not range-checked

**File:** `planspiel/validate.py:587`
**Issue:** `int_field(block, "kz_start", path)` has no `lo=0, hi=100`. A `kz_start` outside the scale makes the "clamp must act" guard in `check_example` pass trivially.
**Fix:** `self.int_field(block, "kz_start", path, lo=KZ_MIN, hi=KZ_MAX)`.

### IN-07: Tracking replay returns `-KZ_MAX` beyond the printed penalty table

**File:** `tests/support/tracking_replay.py:57`
**Issue:** The rule is `-kz_per_step * started_steps` (for example `-108`). The replay reports `-100`. `kz_final` agrees after clamping, but any assertion on `kz_review` for deep overspend would compare different numbers.
**Fix:** Return `-penalty["kz_per_step"] * -(-overspend // (penalty["step"] * 1000))`, or document that only `kz_final` is comparable.

### IN-08: Test literal contains a backspace character

**File:** `tests/test_print_cli.py:257`
**Issue:** `LEAK = "\documentclass{article}\begin{document}..."`: `\b` becomes U+0008, so the fake TeX source is malformed. The veil test still passes because "Ransomware" is present, but the fixture is not what it claims to be.
**Fix:** Use a raw string: `LEAK = r"\documentclass{article}\begin{document}Ransomware\end{document}"`.

---

_Reviewed: 2026-10-26T15:09:36Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
