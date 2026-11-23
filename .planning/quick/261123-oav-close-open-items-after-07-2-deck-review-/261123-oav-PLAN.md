---
phase: quick-261123-oav
plan: 261123-oav
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/test_booklet_model.py
  - tests/test_risk_matrix_config.py
  - planspiel/validate.py
  - README.md
  - .planning/codebase/CONCERNS.md
  - .planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-DECK-CHECKLIST.md
  - tests/test_intro_deck.py
  - "final_documents/Planspiel_Einführung + Grundlagen.pptx"
  - content/INVENTORY.md
autonomous: true
requirements: [LEG-02, PROT-01, PROT-05]

must_haves:
  truths:
    - "The intro deck has an Übungswelle slide 33 between Schutzbedarf (32) and Budget und Maßnahmenwahl (34), with 15 min from session_schedule wave_0 and the material line built from the print labels of uebung-welle-0 and spieler-so-funktioniert-eine-welle; it names no attack and no amount"
    - "Every slide-number field in the deck caches its real slide position (no footer shows 32 on slide 34, 34 on slide 36 or 35 on slide 37)"
    - "Slide 31's Risikobeurteilung step asks for the business damage per protection goal and the Schutzbedarf, with no likelihood word; slide 21 keeps its general likelihood x damage theory and the matrix graphic, plus one bridge line saying the game rates only the damage per protection goal; slide 22 is titled Schutzbedarf"
    - "A candidate config in which c, i or a has no business case fails uv run planspiel validate with risk.case_goal_coverage (D-12); the shipped config passes"
    - "A gesamt computation that takes the first rating or the lexicographic maximum fails tests/test_booklet_model.py"
    - "CONCERNS.md quotes the 215-minute session"
    - "The RC4 print set stays current: uv run planspiel print --check exits 0 and uv run pytest -q is green"
  artifacts:
    - path: "tests/test_intro_deck.py"
      provides: "PRACTICE_SLIDE = 33, renumbered block slides, slide-number field test, bridge-text and schedule-order tests"
      contains: "PRACTICE_SLIDE = 33"
    - path: "final_documents/Planspiel_Einführung + Grundlagen.pptx"
      provides: "38-slide intro deck"
    - path: "planspiel/validate.py"
      provides: "coverage rule in check_risk_cases"
      contains: "risk.case_goal_coverage"
    - path: "tests/test_risk_matrix_config.py"
      provides: "candidate tests for the coverage rule, deduplicated coverage assertion"
      contains: "risk.case_goal_coverage"
    - path: "tests/test_booklet_model.py"
      provides: "maximum-principle test with the highest band off the first position"
    - path: ".planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-DECK-CHECKLIST.md"
      provides: "deck checklist with extracted texts, rows, approval note, result section"
    - path: "content/INVENTORY.md"
      provides: "deck row with 38 slides and the quick-task note"
      contains: "38 slides"
  key_links:
    - from: "tests/test_intro_deck.py MINUTE_SLIDES[33]"
      to: "simulation_config.json session_schedule block wave_0"
      via: "_expected_minutes"
      pattern: "wave_0"
    - from: "tests/test_intro_deck.py practice material test"
      to: "content/texte.toml [sheets.ablauf.print]"
      via: "content.texts.subtree"
      pattern: "uebung-welle-0"
    - from: "planspiel/validate.py check_risk_cases"
      to: "CIA_KEYS"
      via: "set difference of the case goals"
      pattern: "case_goal_coverage"
---

<objective>
Close the open items after phase 07.2 before the dry run on 2026-11-25: (1) finish the intro deck (slide 31 assessment step, slide 21 bridge line, slide 22 title, a new Übungswelle slide, correct slide-number fields), pinned test-first; (2) fix review warnings WR-01 and WR-02 of `07.2-REVIEW.md`; (3) correct the minute figure in `.planning/codebase/CONCERNS.md`.

Purpose: the deck the facilitator shows must match the game the teams play (no likelihood rating, practice wave in schedule order, readable slide numbers), and the protection-goal coverage rule (07.2 D-12) must protect candidate configs, not only the shipped one.

Output: one 38-slide deck commit, test and validator commits, a deck checklist in the quick dir, PowerPoint renders for the user's review after the run. No config value, no `content/texte.toml` value and no print input changes, so RC4 stays current.
</objective>

<execution_context>
@$HOME/.claude/gsd-core/workflows/execute-plan.md
@$HOME/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@CLAUDE.md
@.claude/CLAUDE.md
@.planning/phases/07.2-protection-need-analysis-instead-of-likelihood-axis-per-asse/07.2-REVIEW.md
@.planning/phases/07.2-protection-need-analysis-instead-of-likelihood-axis-per-asse/07.2-05-SUMMARY.md
@.planning/phases/07.2-protection-need-analysis-instead-of-likelihood-axis-per-asse/07.2-DECK-CHECKLIST.md
@.planning/phases/07.1-risk-based-learning-chain-cia-risk-register-from-the-mechtec/07.1-09-SUMMARY.md
@tests/test_intro_deck.py

<interfaces>
Facts extracted by the planner on 2026-11-23 (read-only, python-pptx and zipfile on the committed deck; re-verify before editing, never trust part names without resolving them):

Deck: 37 slides, 522 zip entries, all deflated, no `p14:sectionLst`, no custom shows, no `p14:creationId` in the slide parts, not LFS-tracked. `docProps/app.xml` CRC 63C77E31 and never edited (PowerPoint rewrites it on its next save).

Position to zip part (resolved via `p:sldIdLst` of `ppt/presentation.xml` and `ppt/_rels/presentation.xml.rels`): 21 slide21.xml (sldId 276); 22 slide22.xml (sldId 277, root carries show="0", the slide is HIDDEN); 28 slide28.xml; 31 slide31.xml (285, rId38); 32 slide36.xml (291, rId52, Schutzbedarf); 33 slide32.xml (286, rId39, Budget und Maßnahmenwahl); 34 slide33.xml (2147477873, rId40, 15 Minuten Pause, no slide-number field); 35 slide34.xml (287, rId41, Angriffswellen und Events, rels: slideLayout13 plus notesSlide33.xml); 36 slide35.xml (288, rId42, Abschluss und Debriefing); 37 slide37.xml (290, rId44, closing photo slide, no slide-number field). Highest relationship id in presentation.xml.rels is rId52; sldId 292 is unused. Note: python-pptx renames slide parts in list order when it loads a deck, so `slide.part.partname` is NOT the zip name.

Slide numbers: the footer placeholder "Foliennummernplatzhalter 5" holds an `a:fld type="slidenum"` whose cached `a:t` text is stale on slide 33 (32), slide 35 (34) and slide 36 (35) since the 07.1-09 insertion; all other cached values equal their position. The fix is the cached `a:t` text, not static text.

Slide 21 "Sicherheitsrisiken" (theory, visible): three steps; the Risikobeurteilung step text box (shape id 674216540, "Text Placeholder 14") reads "Ermittlung der Eintrittswahrscheinlichkeit und der potenziellen Schadensauswirkung" / "→ Welche Wirkung haben die Risiken?"; the 3 x 3 matrix is drawn from rectangles "Rechteck 126" to "Rechteck 134" and text boxes 135-149 with axis labels "Schadenspotential" and "Eintrittswahrscheinlichkeit" ("Textfeld 124" at 9369776 / 4297489). Free area right of the matrix: about x 9369776 to 11784013, y 3133393 to 4250000. Separator line of the row at y 4611001. Text boxes use bodyPr wrap square with zero insets.

Slide 22 "Sicherheitsbedarf" (hidden): five questions 01-05: "Wie wird grundsätzlich mit Risiken umgegangen?", "Welche Schäden können maximal akzeptiert werden?", "Wie stark und umfangreich soll der Schutz vor Bedrohungen sein?", "Welche Sicherheitsziele sind wichtig?", "Ist die Einhaltung von Gesetzen (z.B. BDSG) verpflichtend? Sind Sicherheitszertifikate relevant?". Slide 20 is titled "Sicherheitsziele" (CIA-Triade), so question 04 matches the deck's own term.

Slide 28 "SPIELPHASEN": six groups 1 Einführung, 2 Story-Gruppenarbeit, 3 Übungswelle, 4 Maßnahmen und Budget, 5 Angriffswellen, 6 Abschluss und Debriefing. Already correct, no change (pinned by `test_flow_overview_is_visible_and_lists_the_phases_in_order` via `sheets.ablauf.practice_label`).

Slide 31 "Planspiel / Sicherheitsrisiken": Risikobeurteilung text box (shape id 809549495, at 4329813 / 4478454, size 3073078 x 549000) holds one run: "Wie hoch sind Eintrittswahrscheinlichkeit und potenzielle Schadensauswirkung? → Welche Wirkung haben die Risiken?". Material line at y 6082102.

Slide 35 "Angriffswellen und Events" (source layout for the new slide): kicker placeholder run "Planspiel"; title runs "Angriffswellen" + " und Events"; body text box id 785419173 ("Textfeld 785419172", Segoe UI 18 pt, spAutoFit) with paragraphs: text, empty, "Ermittelt daraus:", two bullet paragraphs (marL 283879, buChar •), empty, text, empty; material text box id 2 ("Material: Arbeitsblatt der Welle, Eventkarten, So funktioniert eine Welle"); minutes text box id 3 at 8101554 / 5783680 size 3210988 x 706405 with runs "25" + " min Welle 1, je 20 min Welle 2 und 3". Slide 36's single-line minutes box sits at 8101554 / 6090680 size 3210988 x 399405.

Config and texts: `session_schedule.blocks` order intro 10, break_1 5, story_groups 35, wave_0 15 (wave 0), measures_budget 30, break_2 15, wave_1 25, wave_2 20, wave_3 20, closing 10, debrief 30; total 215. `content/texte.toml`: `[sheets.ablauf] practice_label = "Übungswelle"`; `[sheets.ablauf.print] uebung-welle-0 = "Übungsblatt"`, `spieler-so-funktioniert-eine-welle = "So funktioniert eine Welle"`; `[practice] intro` contains "zählt nicht für eure Wertung". Veil terms live in `content/giveaway_terms.toml` (ransomware, verschlüssel, lösegeld, erpress, phishing, emotet, exfil, datendiebstahl, darknet, sinumerik; tokens sps, apt; OT-Störung).

Validator (`planspiel/validate.py`): `CIA_KEYS = {"c", "i", "a"}`; `check_risk_cases(self, block, band_ids, bands, attacks, waves)` loops over `block["cases"]` (path "risk_matrix.cases"), reports `risk.case_goal` for a missing or unknown goal and `risk.case_goal_attack` for an anchored goal outside the attack's strongest goals; the loop `continue`s early for unanchored cases; errors go through `self.error(code, path, message)` with German messages. Shipped cases: design_data c, audit_findings c, data_trust i (the only i case, anchored to ransomware, whose strongest goals are {c, i}), production_day a, production_days a, production_week a, oem_hold a, single_pc a.

Tests: `tests/test_risk_matrix_config.py` helpers `_raw()`, `_codes(raw)`, `_mutated(mutate)` (mutates `raw["risk_matrix"]`), `_case(block, case_id)`; `test_every_case_carries_a_goal_of_c_i_or_a` and `test_every_protection_goal_has_a_case` both assert the goal set equals {"c", "i", "a"}, and the latter also has a redundant `any(case.goal == "i")`. `tests/test_booklet_model.py` `test_the_need_example_follows_the_maximum_principle` recomputes the expected word with the same max expression; `test_a_need_example_word_that_is_no_band_word_stops_the_build` shows the texte.toml patch pattern (partition at "[sheets.register.need_example]", write to tmp_path, `build_team_booklet(load_config(CONFIG_PATH), load_texts(path))`). `booklet.register.need_example` is (f"{W1} {asset}", c, i, a, gesamt). The `[sheets.register.need_example]` section is asset "Patientenakten", c "hoch", i "mittel", a "hoch", followed by `[sheets.register.example]`.

Stamp: `planspiel/stamp.py` DATA_INPUTS are simulation_config.json, content/texte.toml, content/clues.toml, content/mhp_baseline.json, content/assets/images, print/planspiel.sty, print/templates; BUILD_INPUTS add the whole print dir, planspiel/, pyproject.toml, uv.lock. README.md, content/INVENTORY.md, tests and the deck are neither, so this plan cannot make the print set stale once code changes are committed.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Review warnings WR-01 and WR-02 (test-first) and the CONCERNS minute figure</name>
  <files>tests/test_booklet_model.py, tests/test_risk_matrix_config.py, planspiel/validate.py, README.md, .planning/codebase/CONCERNS.md</files>
  <read_first>.planning/phases/07.2-protection-need-analysis-instead-of-likelihood-axis-per-asse/07.2-REVIEW.md (WR-01, WR-02), tests/test_booklet_model.py (lines 1-40 imports and fixtures, 370-395), planspiel/booklet.py (the need-example block around `highest = max(...)`, about line 246-253), tests/test_risk_matrix_config.py (lines 1-50 helpers, 200-205 `_case`, 270-330), planspiel/validate.py (lines 718-783 `check_risk_cases`), README.md (line 230, the risk_matrix paragraph), .planning/codebase/CONCERNS.md (lines 134-150), .planning/phases/07.2-protection-need-analysis-instead-of-likelihood-axis-per-asse/07.2-CONTEXT.md (D-12)</read_first>
  <behavior>
    - WR-01: parametrized test `test_the_need_example_total_is_the_highest_band_wherever_it_sits` with literal cases (c, i, a, expected): ("gering", "hoch", "mittel", "hoch"), ("mittel", "gering", "hoch", "hoch"), ("gering", "mittel", "gering", "mittel"); it patches only the `[sheets.register.need_example]` section of a tmp copy of texte.toml and asserts `booklet.register.need_example[1:] == (c, i, a, expected)`. Case 1 and 2 fail an implementation that returns the first rating or the lexicographic maximum; case 3 fails one that always returns the top band.
    - WR-02: `test_a_protection_goal_without_a_business_case_is_rejected` parametrized over two candidate mutations of the shipped config, (a) the `data_trust` case removed, (b) `data_trust` retagged to goal "c": `"risk.case_goal_coverage" in _codes(raw)`, and the matching issue's path is "risk_matrix.cases" and its message names the missing goal i.
    - WR-02: `test_the_shipped_config_covers_every_protection_goal`: `"risk.case_goal_coverage" not in _codes(_raw())`.
    - WR-02 dedupe: `test_every_case_carries_a_goal_of_c_i_or_a` keeps only its all-goals-valid assertion; `test_every_protection_goal_has_a_case` keeps the set equality and the 6..8 count and drops the redundant any-i line.
    - Existing goal-mutation tests (`test_an_anchored_goal_must_be_a_strongest_goal_of_its_attack`, `test_an_unanchored_case_may_carry_any_goal`, `test_a_case_without_a_goal_is_rejected`, `test_an_unknown_goal_is_rejected`) stay green unchanged.
  </behavior>
  <action>
WR-01 (test only, the code is correct): add the parametrized test from the behavior block next to `test_the_need_example_follows_the_maximum_principle` in `tests/test_booklet_model.py`. Patch texte.toml like `test_a_need_example_word_that_is_no_band_word_stops_the_build` does, but rewrite only the body of the `[sheets.register.need_example]` section (from the marker up to the next line that starts with "[") so the following `[sheets.register.example]` section stays untouched; keep the `asset` line, set `c`, `i`, `a` from the parameters. Expected words are literals, never recomputed with the implementation's expression. Because the implementation is already right, this test cannot be RED against it; prove its power with a mutation check instead: temporarily replace the right-hand side of the `highest` assignment in `planspiel/booklet.py` with the first rating of the tuple, run the new test (cases 1 and 2 must fail), then with the plain built-in maximum over the tuple without a key (cases 1 and 2 must fail), then restore the file and confirm `git diff --quiet planspiel/booklet.py`. Record the three runs in the SUMMARY. Never commit the mutation. Commit the test alone: `test(quick-261123-oav): pin gesamt when the highest band is not the first rating (WR-01)`.

WR-02 RED: in `tests/test_risk_matrix_config.py` under the "protection goal per case (PROT-01, D-11, D-12)" heading add the two tests of the behavior block (mutations through `_mutated`; removing a case filters `block["cases"]` by id; for the path and message check read the issues from `validate(raw)` filtered by `issue.code == "risk.case_goal_coverage"`), and apply the dedupe. Run `uv run pytest tests/test_risk_matrix_config.py -q`: the two candidate cases fail because the code does not exist yet, the shipped-config test passes. Commit: `test(quick-261123-oav): a protection goal without a business case fails validation (WR-02, RED)`.

WR-02 GREEN, per 07.2 D-12 (each of C, I and A has at least one case) and the orchestrator's choice of a validator error (not a warning, not the balance-suite alternative of the review): in `check_risk_cases` of `planspiel/validate.py`, after the case loop, collect the goals of all dict cases that are valid goal strings, compute the CIA_KEYS missing from them, and if any are missing report one `self.error("risk.case_goal_coverage", path, message)` on `path` ("risk_matrix.cases") with a German message in the style of the neighbouring messages that names the missing goals in sorted order, for example "Kein Geschäftsfall für Schutzziel i: jedes Schutzziel (c, i, a) braucht mindestens einen Fall". Do the collection after the loop (the loop `continue`s for unanchored cases). Add D-12 to the decision list in the method's docstring (the method is being changed). In `README.md` line 230 (risk_matrix paragraph) add one digit-free German sentence after the sentence about the business cases: "Jedes Schutzziel c, i und a hat mindestens einen Fall." No other README change. Run `uv run pytest tests/test_risk_matrix_config.py tests/test_readme_current.py -q` (green) and `uv run planspiel validate` (0 errors on the shipped config). Commit `planspiel/validate.py` and `README.md`: `fix(quick-261123-oav): require a business case for each protection goal (WR-02, D-12)`.

CONCERNS: in `.planning/codebase/CONCERNS.md` replace the three stale session totals (the pre-07.1 figure on lines 136, 148 and 149) with 215 and name the source once as `session_schedule.total_minutes`; line 148 becomes "3 teams of 5, one afternoon (215 minutes planned in `session_schedule.total_minutes`)" because 215 minutes is no longer "about 3 hours"; keep the rest of each sentence. Commit: `docs(quick-261123-oav): CONCERNS quotes the 215-minute session`.

Stage every commit by explicit path; never stage `.claude/settings.local.json` or the untracked 07.2 `.gitkeep`; never `--no-verify`. Every commit message ends with the two trailer lines `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_01WKuGHjqP3x1zRgsE8aFz57`.
  </action>
  <verify>
    <automated>uv run pytest tests/test_booklet_model.py tests/test_risk_matrix_config.py tests/test_readme_current.py -q && uv run planspiel validate && git diff --quiet planspiel/booklet.py && test "$(grep -c '195' .planning/codebase/CONCERNS.md)" -eq 0 && test "$(grep -c '215 minutes' .planning/codebase/CONCERNS.md)" -ge 3</automated>
  </verify>
  <done>The three WR-01 cases pass and the SUMMARY shows they failed under both mutations; a candidate without an integrity case (removed or retagged) yields `risk.case_goal_coverage`, the shipped config validates with 0 errors; the duplicated coverage assertion is gone; README states the rule; CONCERNS says 215; four commits with the quick scope (WR-01 test, WR-02 RED, WR-02 GREEN, CONCERNS).</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Deck checklist and the RED deck test (new Übungswelle slide 33, bridge texts, slide-number fields)</name>
  <files>.planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-DECK-CHECKLIST.md, tests/test_intro_deck.py</files>
  <read_first>tests/test_intro_deck.py (whole file), .planning/phases/07.2-protection-need-analysis-instead-of-likelihood-axis-per-asse/07.2-DECK-CHECKLIST.md (format), final_documents/Planspiel_Einführung + Grundlagen.pptx (read-only with python-pptx and zipfile: slides 21, 22, 28, 31, 32, 33, 35, 36 and the part mapping; re-verify the interfaces block), content/texte.toml ([sheets.ablauf], [sheets.ablauf.print], [practice] intro), simulation_config.json (session_schedule)</read_first>
  <behavior>
    Renumbering for the new slide 33 (every slide from old 33 on moves up by one):
    - `MINUTE_SLIDES` = {26: break_1, 31: story_groups, 33: wave_0, 34: measures_budget, 35: break_2, 37: closing + debrief}; `MINUTE_TEXT` gains 33 "{n} min", and the keys 34 ("{n} min"), 35 ("{n} Minuten Pause"), 37 ("{n} min"); `SUMMED_SLIDES = {37}`; `WAVE_SLIDE = 36`
    - `MATERIAL` / `MATERIAL_JOBS` keys 34 (Teamheft, Maßnahmenkarten), 36 (wave slide), 37 (Teamheft), plus 33: "Material: Übungsblatt, So funktioniert eine Welle" with jobs ("uebung-welle-0", "spieler-so-funktioniert-eine-welle")
    - budget slide test reads slide 34, break-slide test uses [26, 35], closing test reads slide 37, `test_the_deck_has_the_expected_slides` expects 38; `NEED_SLIDE = 32`, `TEAM_SIZE_SLIDE = 30`, `FLOW_SLIDE = 28`, `ACCEPTED_STORY_HITS` unchanged
    New tests:
    - `test_practice_slide_is_visible_and_titled`: `PRACTICE_SLIDE = 33` is visible and its title equals `sheets.ablauf.practice_label`
    - `test_practice_slide_material_uses_the_print_labels`: "Material: " joined with ", " over the `sheets.ablauf.print` labels of `MATERIAL_JOBS[PRACTICE_SLIDE]` equals `MATERIAL[PRACTICE_SLIDE]` and stands on the slide
    - `test_practice_slide_explains_one_wave_without_scoring`: the slide holds "E-Wert", "Gesamtreduktion", "Schaden", "Kundenzufriedenheit" and `PRACTICE_NOT_SCORED = "zählt nicht für eure Wertung"`, which also stands in `[practice] intro`; no "€", no "Euro", no `MONEY_FIGURE`
    - `test_block_slides_follow_the_session_schedule`: mapping every block id to its slide (from `MINUTE_SLIDES` plus wave_1..wave_3 to `WAVE_SLIDE`), the slide numbers taken in `cfg.session_schedule.blocks` order never decrease (pins story_groups, then wave_0, then measures_budget)
    - `test_slide_number_fields_show_the_slide_position`: for every slide, the cached text of each `a:fld` with type slidenum (xpath on `slide._element`) equals the slide's 1-based position
    - `test_story_slide_assesses_damage_per_protection_goal`: slide 31 holds `RISK_ASSESSMENT_TEXT` and "Schutzbedarf" and matches none of `RETIRED_MATRIX_PATTERNS`
    - `test_theory_risk_slide_keeps_the_method_and_bridges_to_the_game`: slide 21 still holds "Eintrittswahrscheinlichkeit" (general method kept) and holds `THEORY_BRIDGE_TEXT`
    - `test_theory_need_slide_is_titled_schutzbedarf`: slide 22's title equals `NEED_TITLE`, and the word "Sicherheitsbedarf" stands on no slide
  </behavior>
  <action>
Requirements review first (user rule): the planner already found and resolved these points; repeat the extraction to confirm them, and record them in the checklist. (i) Slide 22 is hidden (show="0"): rename it as asked, keep it hidden unless the execution prompt carries the user's answer to "Folie 22 einblenden?"; if the answer is "einblenden", remove the attribute in Task 3 and add `slide._element.get("show") != "0"` to the slide-22 test. (ii) Footer numbers are slidenum fields with stale cached text (see interfaces), fixed by setting the cached text. (iii) Slide 28 already lists Übungswelle, no change. (iv) The slide-21 matrix graphic stays: slide 21 is the general risk-management method (planner decision delegated by the user), only a bridge line is added. (v) Slide 22's five questions stay unchanged: they ask what protection is needed in general, question 02 (acceptable damage) fits the game's damage rating, and question 04's "Sicherheitsziele" matches the title of slide 20.

Checklist: write `.planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-DECK-CHECKLIST.md` in the 07.2 format: facts (deck, part mapping resolved by relationships, the current texts extracted with `uv run python` and python-pptx, never typed from memory), `## Slide findings` table (Row | Slide | Current text | Proposed change | Source) with rows: 1 slide 21 bridge text box (new); 2 slide 22 title (hidden slide, questions unchanged); 3 slide 31 Risikobeurteilung text; 4 new slide 33 Übungswelle (title, body, material, minutes); 5 slide-number cached values on slides 34, 36, 37 and the new 33; 6 slide 28 unchanged; 7 `docProps/app.xml` untouched. `## Approval`: the user's instruction "setze fehlendes um" (2026-11-23), relayed by the orchestrator, approves items 1a-1e as listed in the quick task; name the planner's decisions (iv), (v) and the open slide-22 visibility question (i). `## Result review`: left for Task 3. Commit: `docs(quick-261123-oav): intro deck checklist for the open 07.2 deck items`.

Approved slide texts (German, digit-free, no MechTech, no attack name, no amount), to be pinned as constants in the test:
- `RISK_ASSESSMENT_TEXT` (slide 31, replaces the one run of the Risikobeurteilung box): "Wie groß wäre der Schaden fürs Geschäft, wenn Vertraulichkeit, Integrität oder Verfügbarkeit verletzt würden? → Welchen Schutzbedarf haben eure Werte?"
- `THEORY_BRIDGE_TEXT` (slide 21, new text box): "Im Planspiel tritt jeder Angriff ein: Bewertet wird nur der Schaden je Schutzziel (Schutzbedarf)."
- Slide 22 title: `NEED_TITLE` ("Schutzbedarf").
- Slide 33 title "Übungswelle" (from `practice_label`, the same word as phase 3 on slide 28), kicker "Planspiel"; body paragraphs in this order: "Bevor die erste Welle beginnt, rechnet ihr gemeinsam ein Beispiel durch. Es zählt nicht für eure Wertung." / empty / "Verfolgt am Beispielteam Schritt für Schritt:" / bullet "den E-Wert aus den CIA-Werten und den Gewichten der Welle" / bullet "die Gesamtreduktion aus E-Wert und Gesamtbonus" / bullet "den Schaden und die Wirkung auf die Kundenzufriedenheit" / empty / "Genauso rechnet ihr danach jede echte Welle." / empty; material line `MATERIAL[33]`; minutes "15 min" (wave_0).

RED: edit `tests/test_intro_deck.py` to the behavior block. Extend the module docstring with one paragraph: quick task 261123-oav added the Übungswelle slide 33 and fixed slide 31, 21 and 22 and the slide-number fields per `.planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-DECK-CHECKLIST.md` (follow-up to PROT-05 and LEG-02); minute, title and material words come from config and texte.toml, only the approved slide texts above are typed. Update the comments above `MINUTE_SLIDES` and `WAVE_SLIDE` to the new numbers. Run `uv run pytest tests/test_intro_deck.py -q` against the committed deck: the renumbered and new tests fail, nothing errors at collection (no exception outside assertions). Commit: `test(quick-261123-oav): pin the Übungswelle slide, the slide 21/22/31 texts and the slide-number fields (RED)`.
  </action>
  <verify>
    <automated>uv run pytest tests/test_intro_deck.py -q -p no:cacheprovider; test $? -eq 1 && grep -q "PRACTICE_SLIDE = 33" tests/test_intro_deck.py && grep -q "## Slide findings" .planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-DECK-CHECKLIST.md</automated>
  </verify>
  <done>The checklist holds the extracted texts, rows 1-7, the approval note and the open slide-22 question; the deck test pins the 38-slide target and fails only by assertions on the committed 37-slide deck; two commits (checklist, RED test).</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Surgical deck patch on a copy (GREEN), renders, single deck commit, final gates</name>
  <files>final_documents/Planspiel_Einführung + Grundlagen.pptx, content/INVENTORY.md, .planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-DECK-CHECKLIST.md</files>
  <read_first>.planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-DECK-CHECKLIST.md (rows), tests/test_intro_deck.py (constants), .planning/phases/07.1-risk-based-learning-chain-cia-risk-register-from-the-mechtec/07.1-09-SUMMARY.md (how a slide part was added: sldId, rels, content types), content/INVENTORY.md (deck row), tests/test_inventory.py (4 cells per row)</read_first>
  <behavior>
    - On the patched copy: `PLANSPIEL_DECK=<copy> uv run pytest tests/test_intro_deck.py -q` passes with 0 xfailed; python-pptx opens it with 38 slides
    - Zip comparison old to new: changed exactly `[Content_Types].xml`, `ppt/presentation.xml`, `ppt/_rels/presentation.xml.rels`, `ppt/slides/slide21.xml`, `slide22.xml`, `slide31.xml`, `slide32.xml`, `slide34.xml`, `slide35.xml`; added exactly `ppt/slides/slide38.xml` and `ppt/slides/_rels/slide38.xml.rels`; removed none; 524 entries; `docProps/app.xml` CRC unchanged
    - Text diff of all slides: every difference maps to a checklist row
  </behavior>
  <action>
Build the copy with a script in the session scratchpad (not committed), working only on `build/deck/quick-261123-oav/` (gitignored). Use zipfile plus lxml (shipped with python-pptx) or exact string insertion; keep every untouched entry byte for byte, keep `[Content_Types].xml` as the first entry and the original entry order, deflate new and changed entries like the rest. Resolve every part through `p:sldIdLst` and the presentation rels and assert its title before editing it (never by part name alone).

1. Slide 31 (part `slide31.xml`): set the single run of shape id 809549495 to `RISK_ASSESSMENT_TEXT`, run properties kept.
2. Slide 21 (part `slide21.xml`): add one text box with `THEORY_BRIDGE_TEXT`, made by deep-copying the `p:sp` of the Risikobeurteilung step text (shape id 674216540) so font, colour and insets match: new shape id (highest id on the slide plus one), name "Textfeld Planspiel-Hinweis", one paragraph with one run (first run's properties), position in the free area right of the matrix (start at x 9369776, y 3133393, cx 2414237, cy 1000000) so it touches neither the matrix cells nor the axis label nor the row separator; adjust within that area after the render if needed. The matrix shapes stay untouched.
3. Slide 22 (part `slide22.xml`): title run text "Schutzbedarf" (later title runs emptied if any); `show="0"` stays unless the user's answer says "einblenden" (Task 2 point i).
4. New slide 33: copy the bytes of part `slide34.xml` (slide 35, assert its title "Angriffswellen und Events") to `ppt/slides/slide38.xml` and edit: title first run "Übungswelle", second run emptied or removed; body text box id 785419173 rebuilt to the approved paragraphs by copying the existing paragraph elements (normal paragraph, empty paragraph, bullet paragraph) so the 18 pt Segoe UI run properties and the bullet pPr are kept; material box id 2 text `MATERIAL[33]`; minutes box id 3 runs "15" and " min" with its xfrm set to slide 36's single-line geometry (8101554 / 6090680, 3210988 x 399405). Write `ppt/slides/_rels/slide38.xml.rels` with only the slideLayout13 relationship (rId1), without the notes relationship of the source (a notes slide belongs to one slide). Add the Override for `/ppt/slides/slide38.xml` (slide content type) to `[Content_Types].xml`, a slide relationship `rId53` with Target `slides/slide38.xml` to `ppt/_rels/presentation.xml.rels`, and `p:sldId id="292" r:id="rId53"` directly after the sldId 291 entry in `ppt/presentation.xml`; assert rId53 and 292 are unused before inserting.
5. Slide numbers: after the insertion, in every slide part set the cached `a:t` of each slidenum field to the slide's new position (this changes slide32.xml to 34, slide34.xml to 36, slide35.xml to 37 and the new slide38.xml to 33; all others are already right and must stay byte-identical).
6. Do not touch `docProps/app.xml`.

Check the copy: run the deck test with `PLANSPIEL_DECK` pointing at it (green, 0 xfailed); produce the zip comparison of the behavior block and the slide-text diff (python-pptx, all slides, original against copy) and put both in the SUMMARY.

Renders for the user's review: export slides 21, 22, 28, 31, 32, 33, 34, 36 and 37 of the copy to PNG with the PowerPoint COM export used in 07.1-09 and 07.2-05 (`powershell.exe -NoProfile`: PowerPoint.Application, `Presentations.Open(path, ReadOnly true, Untitled false, WithWindow false)`, `Slides(n).Export(png, "PNG", 1920, 1080)`, Close, Quit; afterwards no POWERPNT process may remain). A failed Open (repair needed) is a blocker: stop and report. Write the PNGs to `build/deck/quick-261123-oav/renders/` under the MAIN repository root (resolve it with `git rev-parse --path-format=absolute --git-common-dir` and take its parent) so they survive a worktree cleanup. Look at each render: no overlap of the new text boxes with shapes, footer or slide number; the new slide reads like slides 34 and 36; footers show 33, 34, 36, 37. Also render slide 33 of the committed deck once and note in the SUMMARY whether PowerPoint showed the stale number 32 there (explains where the user saw it).

Then copy the patched file over `final_documents/Planspiel_Einführung + Grundlagen.pptx` and run `uv run pytest tests/test_intro_deck.py tests/test_inventory.py -q`. Update the deck row of `content/INVENTORY.md` (keep 4 cells and `kept manual`, no pipe in a cell): "37 slides" becomes "38 slides", and append one sentence: quick task 261123-oav added the Übungswelle slide 33, reworded the Risikobeurteilung step of slide 31 to the damage per protection goal, added a bridge line on theory slide 21, renamed theory slide 22 to Schutzbedarf and corrected the slide-number fields per `.planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-DECK-CHECKLIST.md`. Fill `## Result review` in the checklist (zip comparison, text diff summary, render paths, the user's look-over pending via the orchestrator, slide-22 visibility as applied). Commit the deck, the inventory and the checklist together, nothing else, as the only deck commit: `docs(quick-261123-oav): intro deck with the Übungswelle slide and correct slide numbers`.

Final gates (stop and report instead of rebuilding if any fails): `uv run planspiel validate` (0 errors), `uv run planspiel texts`, `uv run planspiel print --check` (must exit 0; run it with every code change committed; if it reports stale, do not run `planspiel print`, report the reason), and the fast suite `uv run pytest -q` (about 5 minutes; use a 600000 ms timeout or a background run) with 0 failed and 0 xfailed. `git status --porcelain` afterwards lists only the pre-existing `.claude/settings.local.json` and the untracked 07.2 `.gitkeep` (plus the orchestrator's SUMMARY). In the SUMMARY list the render paths for the orchestrator to show the user, and the open question "Folie 22 ist ausgeblendet: so lassen oder einblenden?" if it was not answered.
  </action>
  <verify>
    <automated>uv run pytest tests/test_intro_deck.py tests/test_inventory.py -q && test -z "$(git status --porcelain 'final_documents/Planspiel_Einführung + Grundlagen.pptx')" && uv run planspiel validate && uv run planspiel print --check && uv run pytest -q</automated>
    <human-check>After the run the orchestrator shows the user the PNG renders from `build/deck/quick-261123-oav/renders/` (slides 21, 22, 28, 31, 32, 33, 34, 36, 37) and asks in German: Folie 33 Übungswelle (Text, Material, 15 min) ok? Folie 31 Risikobeurteilung und Folie 21 Hinweiszeile ok? Folie 22 ist ausgeblendet: so lassen oder einblenden? Fußzeilen 33/34/36/37 richtig? Any correction is a new follow-up commit.</human-check>
  </verify>
  <done>The committed deck has 38 slides and passes its test; the zip comparison and text diff match the checklist rows only; one deck commit exists for this quick task; renders are on disk for the user's review; validate, texts, print --check (exit 0) and the fast suite are green.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| intro deck → all teams | Projected before and during play; must not reveal an attack or a MechTech weak point before its wave |
| patch script → 81 MB hand-maintained binary | A script rewrites zip parts of a file that has no generator |
| candidate config → validator | Edited or candidate configs must be rejected when a protection goal has no business case |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-oav-01 | Information disclosure (veil) | new slide 33 text, slide 21 and 31 texts | high | mitigate | generic wording without attack names or amounts; deck tests run `veil.name_hits` with PROFILE_NAMES on every slide and PROFILE_STORY with the unchanged accepted hits, plus the no-euro checks on slide 33 |
| T-oav-02 | Tampering (data or formatting loss) | deck binary | high | mitigate | edit a copy in `build/deck/quick-261123-oav/`; parts resolved by relationships; untouched entries byte for byte; expected changed/added entry set checked by CRC; full slide-text diff; PowerPoint renders and a failed Open as blocker; one deck commit; the old deck stays in git history |
| T-oav-03 | Repudiation (slide and config drift) | minutes, material and order of the block slides | medium | mitigate | tests compose minutes from `session_schedule`, material from `sheets.ablauf.print`, the title from `practice_label`, and check the block order and every slide-number field |
| T-oav-04 | Denial of service (false positive) | `risk.case_goal_coverage` | low | mitigate | the rule fires only when a goal has no case; the shipped config passes; all existing goal-mutation tests stay green |
| T-oav-05 | Tampering (print set drift) | RC4 print set | medium | mitigate | no DATA_INPUT or template is touched; `planspiel print --check` must exit 0; stop and report instead of rebuilding |
</threat_model>

<verification>
- `uv run pytest tests/test_intro_deck.py tests/test_inventory.py tests/test_booklet_model.py tests/test_risk_matrix_config.py tests/test_readme_current.py -q` green on the committed deck
- `uv run planspiel validate` 0 errors; a candidate without an i case fails with `risk.case_goal_coverage` (pinned by test)
- `uv run planspiel print --check` exit 0; `uv run pytest -q` 0 failed, 0 xfailed
- `git log --oneline -- "final_documents/Planspiel_Einführung + Grundlagen.pptx"` shows exactly one `docs(quick-261123-oav)` commit on top of `b550f8b`
- Commit order shows a `test(...)` RED commit before the deck commit and before the validator GREEN commit
</verification>

<success_criteria>
- Deck: 38 slides; Übungswelle slide 33 between Schutzbedarf and Budget with 15 min and "Material: Übungsblatt, So funktioniert eine Welle"; slide 31 without likelihood; slide 21 bridge line with matrix kept; slide 22 titled Schutzbedarf; every slide-number field equals its position
- WR-01 and WR-02 closed as specified; duplicated assertion removed; README states the coverage rule
- CONCERNS.md says 215 minutes
- RC4 print set still current, fast suite green; renders and the slide-22 question handed to the orchestrator for the user
</success_criteria>

<output>
Create `.planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-SUMMARY.md` with `status: complete` in its frontmatter (the orchestrator commits it). Include the WR-01 mutation runs, the zip comparison, the slide-text diff, the render paths, the print --check and fast-suite results, and the open slide-22 question if unanswered.
</output>
