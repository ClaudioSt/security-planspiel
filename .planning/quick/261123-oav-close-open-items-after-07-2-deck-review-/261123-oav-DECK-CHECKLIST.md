# Quick 261123-oav: Intro deck checklist for the open 07.2 deck items

Deck: `final_documents/Planspiel_Einführung + Grundlagen.pptx` (37 slides before this task, 38 after; slide 22 hidden before, shown after). Nothing in the deck has been edited when this file is written. Task 3 edits a copy under `build/deck/quick-261123-oav/`, checks it, and commits the binary once.

Extraction (2026-11-23, read-only, zipfile + lxml on the committed deck, `uv run python`): every text shape of slides 21, 22, 31, 32, 33, 34, 35, 36 and 37 with position, size and paragraphs, the slide-number fields, the `show` attribute. Slide parts resolved through `p:sldIdLst` and `ppt/_rels/presentation.xml.rels`, not by name. Target words come from `content/texte.toml` (`[sheets.ablauf]`, `[sheets.ablauf.print]`, `[practice]`) and `session_schedule`.

Facts behind the rows:

- Position to zip part: 21 `slide21.xml` (sldId 276, rId28); 22 `slide22.xml` (sldId 277, rId29, root carries `show="0"`, hidden); 31 `slide31.xml` (285, rId38); 32 `slide36.xml` (291, rId52, Schutzbedarf); 33 `slide32.xml` (286, rId39, Budget und Maßnahmenwahl); 34 `slide33.xml` (2147477873, rId40, Pause, no slide-number field); 35 `slide34.xml` (287, rId41, Angriffswellen und Events); 36 `slide35.xml` (288, rId42, Abschluss und Debriefing); 37 `slide37.xml` (290, rId44, closing photo slide, no slide-number field).
- Slide numbers are `a:fld type="slidenum"` fields with a cached text. The cache is stale since the 07.1-09 insertion: position 33 shows "32", position 35 shows "34", position 36 shows "35". All other cached values equal their position. PowerPoint shows the cached text until it recalculates, so the fix is the cached `a:t` text, not static text.
- Slide 21 "Sicherheitsrisiken" (theory, visible): the Risikobeurteilung step text (shape id 674216540) reads "Ermittlung der Eintrittswahrscheinlichkeit und der potenziellen Schadensauswirkung" / "→ Welche Wirkung haben die Risiken?"; a 3 x 3 matrix with the axis labels "Schadenspotential" and "Eintrittswahrscheinlichkeit" is drawn from rectangles and text boxes. Free area right of the matrix: about x 9369776 to 11784013, y 3133393 to 4250000.
- Slide 22 (hidden) is titled "Sicherheitsbedarf" and holds five questions 01 to 05; question 04 reads "Welche Sicherheitsziele sind wichtig?" and matches slide 20 "Sicherheitsziele".
- Slide 28 "SPIELPHASEN" already lists six phases, 3 = Übungswelle (pinned by `test_flow_overview_is_visible_and_lists_the_phases_in_order`).
- Slide 31 "Planspiel / Sicherheitsrisiken": the Risikobeurteilung step text (shape id 809549495) reads "Wie hoch sind Eintrittswahrscheinlichkeit und potenzielle Schadensauswirkung? → Welche Wirkung haben die Risiken?".
- `session_schedule.blocks` order: intro 10, break_1 5, story_groups 35, wave_0 15, measures_budget 30, break_2 15, wave_1 25, wave_2 20, wave_3 20, closing 10, debrief 30; total 215. The deck has no slide for wave_0 although it sits between story_groups (slide 31/32) and measures_budget (slide 33).
- `[sheets.ablauf.print]` labels: `uebung-welle-0` = "Übungsblatt", `spieler-so-funktioniert-eine-welle` = "So funktioniert eine Welle"; `[sheets.ablauf] practice_label` = "Übungswelle"; `[practice] intro` contains "zählt nicht für eure Wertung".
- `docProps/app.xml` is never edited (PowerPoint rewrites it on its next save).

## Requirements review

Done before the plan, repeated here (user rule: review for missing or unclear points first).

1. Slide 22 is hidden. The user was asked and answered "Einblenden" (2026-11-23): rename it to "Schutzbedarf" and remove `show="0"`, so the slide is shown. The deck test pins visibility.
2. Footer numbers: stale cached field text, fixed by setting the cached text.
3. Slide 28 already lists Übungswelle: no change.
4. Slide 21's matrix graphic stays (planner decision, delegated by the user): slide 21 is the general risk-management method; one bridge line says what the game does differently.
5. Slide 22's five questions stay unchanged: they ask what protection is needed in general, question 02 fits the game's damage rating, question 04's "Sicherheitsziele" matches slide 20.

## Slide findings

Slide numbers are the positions after the edit (new slide 33 inserted; old 33 to 37 move to 34 to 38 in the text below only where named "old").

| Row | Slide | Current text | Proposed change | Source |
|-----|-------|--------------|-----------------|--------|
| 1 | 21 | No bridge text; Risikobeurteilung step and matrix talk about Eintrittswahrscheinlichkeit | New text box right of the matrix: "Im Planspiel tritt jeder Angriff ein: Bewertet wird nur der Schaden je Schutzziel (Schutzbedarf)."; matrix and step text unchanged | D-01, D-16 |
| 2 | 22 | Title "Sicherheitsbedarf", slide hidden | Title "Schutzbedarf", `show="0"` removed (user: Einblenden); five questions unchanged | `sheets.register.need_title`, user decision |
| 3 | 31 | "Wie hoch sind Eintrittswahrscheinlichkeit und potenzielle Schadensauswirkung? → Welche Wirkung haben die Risiken?" | "Wie groß wäre der Schaden fürs Geschäft, wenn Vertraulichkeit, Integrität oder Verfügbarkeit verletzt würden? → Welchen Schutzbedarf haben eure Werte?" | D-01, D-16 |
| 4 | 33 (new) | no slide for wave 0 | New slide "Übungswelle" between Schutzbedarf (32) and Budget und Maßnahmenwahl: kicker "Planspiel", body (see below), material "Material: Übungsblatt, So funktioniert eine Welle", "15 min" | `practice_label`, `sheets.ablauf.print`, `session_schedule` wave_0, LEG-02 |
| 5 | 33, 34, 36, 37 | cached slide numbers 32 (old 33), 34 (old 35), 35 (old 36) | cached numbers equal the position: 33 (new), 34, 36, 37 | slide positions |
| 6 | 28 | six phases incl. 3 Übungswelle | No change | `practice_label` |
| 7 | docProps | `docProps/app.xml` | Untouched | never edited |

### Row 4: text of the new slide 33 "Übungswelle"

No MechTech name, no attack, no amount. Same layout and run properties as slide 35 "Angriffswellen und Events" (kicker, title, 18 pt body, material line, minutes box at the single-line position of slide 36). Title "Übungswelle", kicker "Planspiel". Body paragraphs in this order:

1. "Bevor die erste Welle beginnt, rechnet ihr gemeinsam ein Beispiel durch. Es zählt nicht für eure Wertung."
2. (empty)
3. "Verfolgt am Beispielteam Schritt für Schritt:"
4. bullet: "den E-Wert aus den CIA-Werten und den Gewichten der Welle"
5. bullet: "die Gesamtreduktion aus E-Wert und Gesamtbonus"
6. bullet: "den Schaden und die Wirkung auf die Kundenzufriedenheit"
7. (empty)
8. "Genauso rechnet ihr danach jede echte Welle."
9. (empty)

Material line: "Material: Übungsblatt, So funktioniert eine Welle". Minutes: "15 min". The new slide carries no notes slide (a notes slide belongs to exactly one slide).

## Approval

Date: 2026-11-23. The user's instruction "setze fehlendes um" (relayed by the orchestrator) approves the items 1a to 1e of the quick task as listed: the finished deck items (slide 31 assessment step, slide 21 bridge line, slide 22 title, the Übungswelle slide, correct slide-number fields). The approved slide texts above are the planner's proposal inside that approval.

Planner decisions inside the approval: (iv) slide 21 keeps its matrix and gets only a bridge line; (v) slide 22 keeps its five questions.

Slide-22 visibility, answered 2026-11-23 via the orchestrator's question dialog: "Einblenden". The hidden flag is removed in Task 3.

| Row | Status |
|-----|--------|
| 1 | approved (bridge line) |
| 2 | approved; slide shown, not only renamed |
| 3 | approved |
| 4 | approved |
| 5 | approved |
| 6 | no change |
| 7 | no change |

## Result review

Date: 2026-11-23. The user's look-over of the renders is pending via the orchestrator; the render PNGs are under `build/deck/quick-261123-oav/renders/` (slides 21, 22, 28, 31, 32, 33, 34, 36, 37 of the patched deck, plus `committed-old-slide-33.png` of the committed deck).

Build facts: surgical zip patch of the committed deck, script in the session scratchpad, not committed. 522 entries before, 524 after; `[Content_Types].xml` first, original entry order kept, every entry deflated. Changed entries (9): `[Content_Types].xml`, `ppt/presentation.xml`, `ppt/_rels/presentation.xml.rels`, `ppt/slides/slide21.xml` (row 1), `slide22.xml` (row 2), `slide31.xml` (row 3), `slide32.xml` (cached number 34, row 5), `slide34.xml` (cached number 36, row 5), `slide35.xml` (cached number 37, row 5). Added (2): `ppt/slides/slide38.xml` (new slide 33, row 4) and `ppt/slides/_rels/slide38.xml.rels` (layout relationship only, no notes slide). Removed: none. `docProps/app.xml` byte-identical (CRC 63C77E31).

Text diff of all slides (python-pptx, old against new, mapped around the insertion): only slides 21, 22 and 31 differ, plus the new slide 33; every difference maps to rows 1 to 4. The `show` attribute of slide 22 went from "0" to absent (shown).

Render findings: the bridge line on slide 21 stands right of the matrix without touching cells, axis label or separator; slide 31's reworded box needs four lines and clears the material line; slide 33 reads like slides 34 and 36 (kicker, title, 18 pt body, material line, "15 min" at the single-line position); footers show 33, 34, 36 on the patched deck. PowerPoint recomputes slide-number fields when it renders: the committed deck already showed the right number 33 on the old budget slide, so the stale cache was visible only to tools that read the cached text (python-pptx, other viewers), not in PowerPoint itself.

Slide 22 visibility as applied: shown (user answer "Einblenden").
