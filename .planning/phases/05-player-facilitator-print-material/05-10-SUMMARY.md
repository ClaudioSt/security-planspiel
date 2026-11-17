---
phase: 05-player-facilitator-print-material
plan: 10
subsystem: print
tags: [story-documents, latex, newspaper, mail, clues, veil, templates]

requires:
  - phase: 05-player-facilitator-print-material
    provides: texbuild.ASSET_FILES, hashed asset path and graphicx/multicol probes (05-09), planspiel.sty, render pipeline, veil scan (05-01)
  - phase: 03-content-source-veiling
    provides: veiled [story.*] content in content/texte.toml and the clue matrix content/clues.toml
provides:
  - planspiel.story with STORY_JOBS, Section, Steckbrief, Zeitungsartikel, MailLabels, Mail, build_story_documents
  - render.story_documents (template chosen by model type) registered in DOCUMENT_BUILDERS; render.AssetName / asset_name
  - templates story_steckbrief, story_zeitungsartikel, story_mail (both mails)
  - sheets.labels.mail_from, mail_to, mail_subject in _SHEET_LABELS, texte.toml and the mini texte
  - jobs spieler-unternehmenssteckbrief, spieler-zeitungsartikel, spieler-anfrage-mail, spieler-audit-mail built by the one print command
  - proof that every clue quote of content/clues.toml (14) is on the rendered page of its source document (ROADMAP SC6)
affects: [05-12, 05-15, 05-16]

tech-stack:
  added: []
  patterns:
    - "Story models walk the TOML subtree by key role (heading/headline, text, paragraphs, bullets, dateline, lead, caption, nested tables); an unknown key, an unexpected value type or a second nesting level stops the build instead of dropping text"
    - "A fixed image name reaches TeX unescaped only as render.AssetName, created by asset_name() for names in texbuild.ASSET_FILES"
    - "Unbreakable sections in LaTeX are minipages with \\raggedright (samepage does not keep a heading with its list)"

key-files:
  created:
    - planspiel/story.py
    - print/templates/story_steckbrief.tex.j2
    - print/templates/story_zeitungsartikel.tex.j2
    - print/templates/story_mail.tex.j2
    - tests/test_story_model.py
    - tests/test_story_render.py
    - tests/test_story_pdf.py
  modified:
    - planspiel/render.py
    - planspiel/texts.py
    - content/texte.toml
    - tests/fixtures/mini_content/texte.toml
    - tests/test_veil_models.py

key-decisions:
  - "Section carries optional dateline, lead, caption and image fields besides heading/paragraphs/bullets/subsections: the newspaper sections need them, and one recursive type keeps the walker generic"
  - "The newspaper images are assigned to the captioned top-level sections in ASSET_FILES order (audit image to meldung_audit, factory image to bericht_vorfall); the number of captions must equal the number of images, else PrintModelError"
  - "Mail kopf (von, an) is required, anrede/gruss/fusszeile are optional; the mini content gained kopf and newspaper captions so both setups exercise the same shape"
  - "Image file names go through render.AssetName, because tex_escape would write zeitungsartikel\\_bild\\_audit.png into \\includegraphics"
  - "Steckbrief stays at the guideline 10 pt and runs over two pages (page break never separates a heading from its list); the newspaper fits one A4 page at 9.5 pt"

patterns-established:
  - "Pre-wave story documents are plain models plus one template per layout; clue verification runs on the model (default suite) and on the built PDF (pdf suite)"

requirements-completed: [PRINT-12]

duration: ~30 min (10:50 to 11:25 on 2026-10-26)
completed: 2026-10-26
status: complete
---

# Phase 5 Plan 10: Story documents Summary

**`uv run planspiel print` now builds the four pre-wave story documents (Steckbrief, Zeitungsartikel with its two grayscale images, Anfrage-Mail, Audit-Mail) from the veiled `[story.*]` content, and a pdf test per clue proves that all 14 clue quotes stand verbatim on the page of their source document.**

PRINT-12 is complete with this plan (asset path in 05-09, documents here).

## Accomplishments

- `planspiel/story.py`: frozen models built only through `PreAttackView` (story subtrees and the `sheets.labels` mail captions). Headings keep their stored case, nothing a subtree holds is dropped (multiset tests per document), the images are referred to only through `texbuild.ASSET_FILES` (an AST test finds no file name literal in the module), and `story.py` is in the pre-wave AST guard.
- Templates: Steckbrief (Arial 10 pt, 12 pt blue title, left 2.5 cm, top 2 cm, bottom 1.8 cm, itemize bullets, each section an unbreakable box), Zeitungsartikel (`\newfontfamily\newspaperfont{Georgia}` by name with lining numerals, masthead 48 pt from `doc_title`, header line, shaded ticker band, first section full width with image left and text right, `multicols{2}` with a separator rule from the second section on, captions, footer line, no upper-casing), Mail (framed Von/An/Betreff block with hanging indent, salutation, sections with bullets, closing lines, footer rule, Arial 11 pt, one template for both mails).
- `render.story_documents` picks the template by model type; `render.AssetName` / `asset_name` let the fixed image names through `tex_escape` unescaped (and nothing else).
- Mail header values with `"`, `<`, `>` print exactly as stored (`\textquotedbl{}` through `tex_escape`); a render test pins the real `kopf` values and checks that no raw `"` is left in the `.tex`.
- `tests/test_story_pdf.py`: one case per clue (14, `clue-01` to `clue-14`), the clue to job mapping goes through `texts._clue_document`; plus A4, two image XObjects in the newspaper, masthead `AUTOTIMES` on page 1, no image file name in any story PDF, empty metadata, layer-2 veil scan with the story profile, stamp and `Seite x von y` on every page, clean logs, digit-bearing strings on the page, pinned page counts (Steckbrief 2, newspaper 1, mails 1 each).

## Task Commits

1. **Task 1 RED: failing story document model tests** - `c547348` (test)
2. **Task 1 GREEN: story document models** - `f66013f` (feat)
3. **Task 2 RED: failing render and pdf tests** - `f1573d9` (test)
4. **Task 2 GREEN: generate the four story documents** - `8c3696c` (feat)

Plan metadata: see the docs commit that adds this SUMMARY.

## RED runs

- `c547348`: `tests/test_story_model.py` collection error `ModuleNotFoundError: No module named 'planspiel.story'`; `tests/test_veil_models.py` 1 failed (`test_prewave_modules_do_not_reference_revealed_data[story.py]`, 10 passed).
- `f1573d9`: `tests/test_story_render.py` 19 failed, 1 passed (jobs missing from `render_all`, templates missing, no `story_documents`); `tests/test_story_pdf.py` clue-01 failed because `spieler-unternehmenssteckbrief` was not in `printed_set.jobs`.

After GREEN: `uv run pytest -q` 1683 passed, 131 deselected (baseline 1624, +59); `uv run pytest -m pdf -q` 109 passed (baseline 86, +23: 14 clue cases plus 9 others); `tests/test_story_pdf.py` all PASSED, none skipped.

## The built documents (preview `build/preview-story`, PNG renders compared with the plan's description)

- **Unternehmenssteckbrief** (2 pages, 82 KB): blue 12 pt title, blue section headings, bold dark subheadings for Office / OT / SaaS, bullet lists. Page 1 ends after the OT / Produktion list; page 2 starts with the SaaS / Cloud subsection (about 40 percent used). It reads like a company profile. It did not fit one A4 page at the guideline 10 pt (about 50 lines of bullets).
- **Zeitungsartikel** (1 page, 3.7 MB, two images embedded): large `AUTO TIMES` masthead, rule, small header line (Ausgabe, Aktuelles in der Automobilindustrie, Nürnberg), grey ticker band, `OEM VERSCHÄRFT SECURITY-ANFORDERUNGEN` full width with the audit image (hand stamping a folder labelled AUDIT) on the left and the three paragraphs on the right, rule, `Erpresser legen Zulieferer tagelang lahm` with dateline and bold lead, then two columns with the dark factory image (screen with a lock) and DER ANGRIFF / FOLGEN, footer line `Aktuelles ... Seite 1`. Both images are legible; the body is ragged right because hyphenation is off package wide (justified text showed wide gaps). The page is full: about 5 mm remain above the footer line.
- **Anfrage-Mail / Audit-Mail** (1 page each, 74 and 78 KB): blue framed header block with bold blue labels Von, An, Betreff and the subject in bold, salutation, paragraphs, blue bold headings (IHRE AUFGABE:, ERWARTETE NACHWEISE:, ...), bullet lists, closing lines, footer rule with the contact line. Mails are Arial 11 pt (the legacy Anfrage-Mail was Calibri 11 pt; D-26 says Arial for everything but the newspaper).

The human check of the plan (open the four preview PDFs next to the legacy files and print the newspaper) is still open for the user; `build/preview-story/` holds the PDFs (`build/preview` could not be rewritten because `spieler-massnahmenkarten.pdf` was open in a viewer).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Mail header labels in Task 1, not Task 2**
- **Found during:** Task 1 (the `Mail` model carries the labels)
- **Issue:** the plan adds `sheets.labels.mail_*` in Task 2, but `build_story_documents` reads them in Task 1.
- **Fix:** `_SHEET_LABELS`, `content/texte.toml` and the mini texte gained the three keys in the Task 1 GREEN commit.
- **Commit:** f66013f

**2. [Rule 1 - Bug] Image file names were escaped by `tex_escape`**
- **Found during:** Task 2 design (the plan has the template print the plain names while `finalize` turns `_` into `\_`)
- **Issue:** `\includegraphics{zeitungsartikel\_bild\_audit.png}` is not a reliable file lookup.
- **Fix:** `render.AssetName` (a `str` subclass) passes `tex_escape` unchanged, `render.asset_name` creates one only for names in `texbuild.ASSET_FILES` matching `[A-Za-z0-9._-]+`; the template reads `asset[section.image]`. Test: only the fixed names pass unescaped, a path or injection string raises `ValueError`.
- **Commit:** 8c3696c

**3. [Rule 3 - Blocking] Mini fixture shape**
- **Issue:** the mini story had no mail headers and no newspaper captions, and `anrede` carried a heading; a required `kopf` and the two-image rule could not be tested on it.
- **Fix:** mini mails gained `kopf`, the mini `anrede` lost its heading, the two mini newspaper sections gained captions (RED commit); the real content is unchanged.
- **Commit:** c547348

**4. [Rule 2 - Missing safeguard] Strict story walker**
- **Issue:** the plan asks for a generic walk; an unknown key would silently lose text.
- **Fix:** key roles are named (`heading`/`headline`, `text`, `paragraphs`, `bullets`, `dateline`, `lead`, `caption`), unknown keys, wrong value types, a second nesting level (the templates set one) and a wrong number of newspaper captions raise `PrintModelError`; each case has a test.
- **Commit:** f66013f, 8c3696c

**5. [Design] Section type extended; `Mail.doc_title` omitted**
- `Section` has `dateline`, `lead`, `caption`, `image` beside the planned fields; `Mail` carries `subject` (the `doc_title`) and no second `doc_title` field, so `printed_strings()` does not count it twice. `print/planspiel.sty` needed no change (all story macros live in the templates), so it is not in the commits.

**Total deviations:** 5, no scope change.

## Issues Encountered

- Two TeX build errors in the newspaper template (`\hfill` and `\quad` directly followed by text swallowed the next word as a control word; fixed with `{}`), found by the first preview build.
- The first layout had the text column aligned to the bottom of the image (a `[t]` minipage whose first box is an image has its baseline at the image bottom) and spilled onto page 2; fixed with `\vspace{0pt}` first in both minipages, a tighter masthead and ragged-right columns. Mail header rows built from `parbox[t]` pairs did not share a baseline; replaced by a hanging indent with a fixed-width label box.
- A Steckbrief heading stayed alone at the foot of page 1 with `samepage`; sections are now `minipage` boxes.
- A bare `python -` call without `uv run` was issued once by mistake while preparing a quick edit; it waited for stdin and was moved to the background by the tool (no output, no change). Remaining scripted edits that mangled backslashes were redone with the Edit and Write tools.

## Verification

- `uv run pytest -q`: 1683 passed, 131 deselected.
- `uv run pytest -m pdf -q`: 109 passed (includes the two-run byte identity of the whole set, the generic log hygiene, the layer-2 veil scan and metadata test over all jobs).
- `uv run pytest -m pdf tests/test_story_pdf.py -v`: 23 passed (14 clue cases, none skipped).
- `uv run planspiel clues`, `texts`: 0 Fehler; `validate`: 0 Fehler, 1 Warnung (the existing KZ slope 17/7).
- `git status --porcelain final_documents`: empty.

## Known Stubs

None.

## Threat Flags

None beyond the register. T-05-35: story-profile giveaway lint, veil layers 1 and 2 and the metadata test pass for all four documents, and a test shows no image file name or `.png` in any story PDF. T-05-36: mail headers run through `tex_escape`; the real `kopf` values are pinned in a render test and no raw `"` remains; the only unescaped TeX input is `AssetName`, which is constructible only from the fixed constants. T-05-37 accepted: the set builds in about 50 s, the newspaper PDF is 3.7 MB, and two builds are byte-identical.

## Next Phase Readiness

- 05-12 can extend `PREWAVE_MODULES`, `planspiel/render.py` and the texte files from here.
- The newspaper page is full (about 5 mm slack above the footer line); a longer story text will need a smaller image or a second page, and the pinned page count test will say so.
- The visual human check of the four documents (and a print of the newspaper) remains with the user.
- No blockers.

## Self-Check: PASSED

- Files: planspiel/story.py (`STORY_JOBS`, `def build_story_documents(`, `ASSET_FILES`), planspiel/render.py (`def story_documents(`), print/templates/story_steckbrief.tex.j2, story_zeitungsartikel.tex.j2 (`\usepackage{multicol}`, `\usepackage{graphicx}`, `Georgia`), story_mail.tex.j2, tests/test_story_model.py, tests/test_story_render.py, tests/test_story_pdf.py, tests/test_veil_models.py (`"story.py"`) exist.
- Commits c547348, f66013f, f1573d9, 8c3696c exist in `git log`.
