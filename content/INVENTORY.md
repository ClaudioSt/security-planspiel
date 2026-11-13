# Inventory of the hand-maintained documents of the MHP run

Success criterion 5 of Phase 3 (D-19): every item of the hand-maintained docx, pptx, pdf and image files is
accounted for, item by item. The inventory covers the 20 files that were in `final_documents/` at the MHP run.
The file `tests/test_inventory.py` checks that each of them has a row of its own and that the targets exist.

## Location

The 15 superseded files are in `archive/mhp_print_material_2026-07/` (Phase 7, LEG-01). The five kept manual
files (intro deck, MHP company profile, VWI deck, two portraits) stay in `final_documents/`.

Disposition vocabulary:

- `carried→TOML`: the text now lives in `content/texte.toml`; the Target column names the key prefix.
- `carried→assets`: a fact or file now lives in `content/assets/`; the Target column names the path.
- `generated`: Phase 4 or 5 produces it from `simulation_config.json` or the rules module; nothing to carry.
- `kept manual`: stays a hand-maintained file (Out of Scope in PROJECT.md or not game material); reason given.
- `dropped`: deliberately not carried; reason given.

Shared rows list several full file names. Every file also has at least one row that names only that file.

| File | Item | Disposition | Target / reason |
|------|------|-------------|-----------------|
| `Unternehmenssteckbrief MechTech.docx` | Body prose: eleven headings, bullet lists and the three IT/OT sub-lists | carried→TOML | `story.steckbrief` (verbatim and un-veiled; veiling in plan 03-03) |
| `Unternehmenssteckbrief MechTech.docx` | Header "Projekthandbuch", WMF logo, footer "Stand 07.05.2002 ... Solutions GmbH" | dropped | Template residue from an unrelated 2002 document with wrong branding (A9) |
| `Unternehmenssteckbrief MechTech.docx` | Page layout: A4, margins, Arial theme, 12 pt title, 10 pt body | carried→assets | `content/assets/GUIDELINES.md`; the 4.0 cm top margin was reserved for the dropped header and is re-evaluated in Phase 5 |
| `Zeitungsartikel.docx` | Masthead, dateline, ticker, both articles, captions, quotes, footer | carried→TOML | `story.zeitungsartikel` (verbatim and un-veiled; veiling in plan 03-03) |
| `Zeitungsartikel.docx` | Type scale (Georgia, 48 pt masthead, 9.5 pt body) and two-column layout with separator | carried→assets | `content/assets/GUIDELINES.md` |
| `Zeitungsartikel.docx` | US Letter paper size | dropped | LaTeX builds A4 (A8) |
| `Zeitungsartikel.docx` | Embedded newspaper images | carried→assets | `content/assets/images/zeitungsartikel_bild_audit.png` and `content/assets/images/zeitungsartikel_bild_fabrik.png` (identical copies) |
| `Zeitungsartikel.pdf` | PDF render of `Zeitungsartikel.docx` | dropped | No content beyond the docx; PRINT-12 renders it from TOML; it also carries the un-veiled text |
| `Zeitungsartikel_bild_audit.png` | Newspaper picture "Verschärfte Audits für Zulieferer" | carried→assets | `content/assets/images/zeitungsartikel_bild_audit.png` (copy, A15) |
| `Zeitungsartikel_bild_fabrik.png` | Newspaper picture of the production stop | carried→assets | `content/assets/images/zeitungsartikel_bild_fabrik.png` (copy, A15; the padlock screen is kept as a deliberate visual clue, D-30) |
| `Anfrage-Mail.docx` | Header lines, body, task list, signature, footer line | carried→TOML | `story.anfrage_mail` (verbatim and un-veiled, including the stray hyphen in "Beratungs-projekt"; both decided in 03-03) |
| `Anfrage-Mail.docx` | Calibri 11 pt | carried→assets | `content/assets/GUIDELINES.md` |
| `Anfrage-Mail.docx` | US Letter paper size | dropped | LaTeX builds A4 (A8) |
| `Anfrage-Mail.pdf` | PDF render of `Anfrage-Mail.docx` | dropped | No content beyond the docx; PRINT-12 renders it from TOML |
| `Audit-Mail.pdf` | Image-only mail, transcribed in the research appendix | carried→TOML | `story.audit_mail` (the original is in `archive/mhp_print_material_2026-07/`) |
| `Angriff-1_Ransomware.docx` | Heading, scenario paragraph, CIA rationale, case sentences | carried→TOML | `attacks.ransomware.revealed` |
| `Angriff-2_OT-Störung.docx` | Heading, scenario paragraph, CIA rationale, case sentences | carried→TOML | `attacks.ot.revealed` |
| `Angriff-3_Datenexfiltration.docx` | Heading, scenario paragraph, CIA rationale, case sentences | carried→TOML | `attacks.exfil.revealed` |
| `Angriff-1_Ransomware.docx`, `Angriff-2_OT-Störung.docx`, `Angriff-3_Datenexfiltration.docx` | Shared instructions: CIA table, E-value intro, bonus intro, Fall 3 hint | carried→TOML | `sheets.angriff` (bonus intro with "mindestens", as on sheets 1 and 2) |
| `Angriff-1_Ransomware.docx`, `Angriff-2_OT-Störung.docx`, `Angriff-3_Datenexfiltration.docx` | Table vocabulary: Maßnahme, Level, Basisschutz, Summe, Ab Level, Bonus, Erfüllt, Gesamtbonus, Gesamtreduktion, Schaden | carried→TOML | `sheets.labels` |
| `Angriff-1_Ransomware.docx`, `Angriff-2_OT-Störung.docx`, `Angriff-3_Datenexfiltration.docx` | Sentence about the base value of each protection goal | carried→TOML | `sheets.angriff.start_values_intro` (the number is removed and printed from `base_cia` in Phase 4) |
| `Angriff-1_Ransomware.docx`, `Angriff-2_OT-Störung.docx`, `Angriff-3_Datenexfiltration.docx` | Thresholds, caps, bonus values, damage and KZ formulas, Fall numbers, "Angriff N" headings | generated | PRINT-03: the numbers come from `simulation_config.json`, which removes the print-sync trap |
| `Angriff-1_Ransomware.docx`, `Angriff-2_OT-Störung.docx`, `Angriff-3_Datenexfiltration.docx` | Short labels in the bonus table ("M3 - EDR/XDR", "M5 - Netz-Segmentierung", ...) | dropped | Shorter than `measures.*.name`; Phase 4 decides between the config names and a short-label key |
| `Budget.docx` | Intro, cost-type explanations (Init-Kosten, OPEX), tier paragraph, anticipated-sum and tracker prose | carried→TOML | `sheets.budget` (spelling "Init-Kosten" unified; L6) |
| `Budget.docx` | Column "Wann fällig?" entry "Einmal zu Spielbeginn" for Init-Kosten | carried→TOML | `sheets.budget.init_when` (verbatim; outdated since RULE-02, because Init is also due when a level is raised or a measure is added in a change window; wording is fixed when PRINT-07 builds the budget sheet) |
| `Budget.docx` | Table vocabulary (Kostenart, Zeitraum, Antizipierte Summe, Status-Tracker, Nach Welle, ...) | carried→TOML | `sheets.labels` |
| `Budget.docx` | Tier table values, planning rows "Angriff 1" and "Events 1", start values | generated | PRINT-07: from `budget_tiers`, `base_cia` and the wave positions |
| `Return on Security und Final Wert.docx` | Instruction line, purpose sentence, row labels | carried→TOML | `sheets.ros` and `sheets.labels` |
| `Return on Security und Final Wert.docx` | Row "Summe Event-Strafen" and the event-penalty term of the Gesamtkosten formula | dropped | RULE-06: event effects are not part of RoS; PRINT-07 and PRINT-08 define the rows |
| `Return on Security und Final Wert.docx` | Four empty text boxes | dropped | Empty, no content to carry |
| `Return on Security und Final Wert.docx` | Base-loss amount and the cost and avoided-damage formulas | generated | From `rules.base_losses` and the rules module |
| `Events_Security-Game.pptx` | Narratives, rule lines and tier labels of the event slides | carried→TOML | `events.` (narrative and rule per event, tier labels of Kritische Schwachstelle, checklist heading of OEM-Audit) |
| `Events_Security-Game.pptx` | Budget Review slide narrative and rule line | carried→TOML | `final_events.` |
| `Events_Security-Game.pptx` | Backup & Recovery slide (title, subtitle, narrative, level labels) | carried→TOML | `sheets.backup_recovery` (D-29; the recovery factors come from `measures.M4.levels.*.recovery`) |
| `Events_Security-Game.pptx` | Effect lines such as the OPEX discount, the budget cut, KZ values and thresholds | generated | PRINT-06 (D-24): built from event type and params |
| `Events_Security-Game.pptx` | Kurswechsel rule line with the retired term "Maßnahmenwechsel" and the refund wording | dropped | Superseded by `events.kurswechsel.rule` (RULE-01 vocabulary, Phase 2 rule wording) |
| `Events_Security-Game.pptx` | Measure-check sentences "Prüft die Umsetzung von M4" and "Prüft die Umsetzung von M7" | dropped | Digit lint; Phase 5 generates the measure reference from `params` |
| `Events_Security-Game.pptx` | MHP template, Segoe UI, accent colours, card typography | carried→assets | `content/assets/GUIDELINES.md` |
| `Massnahmenkarten_Security-Game.pptx` | Focus, description and level text of the 30 cards (M1 to M10, three levels each) | carried→TOML | `measures.` (focus, description, levels_desc and levels_simple carried from MEASURE_META per D-05 and D-28; the deck and MEASURE_META are identical except on three slides) |
| `Massnahmenkarten_Security-Game.pptx` | M6 L3 and M10 L1 slide texts (slides 18 and 28) | dropped | Copy-paste errors in the printed deck: both show M2 texts (D-28); the MEASURE_META wording is carried |
| `Massnahmenkarten_Security-Game.pptx` | Missing final period on the M1 L1 card | dropped | Cosmetic; the MEASURE_META wording with the period is carried |
| `Massnahmenkarten_Security-Game.pptx` | CIA values, costs and dependency lines | generated | PRINT-05: from `simulation_config.json` |
| `Massnahmenkarten_Security-Game.pptx` | Level badge colours and the red dependency colour | carried→assets | `content/assets/GUIDELINES.md` |
| `Planspiel_Einführung + Grundlagen.pptx` | Intro deck (37 slides, MHP branding, speaker biographies) | kept manual | Out of Scope in PROJECT.md. Edited by hand in Phase 7 per `.planning/phases/07-session-flow-handoff/07-DECK-CHECKLIST.md` (LEG-02, D-18, D-19): the Pinnwand slide is deleted, slide 28 is the six-phase flow overview without attack names or figures, and team size, minute figures, material lines and break slides follow `session_schedule`; `tests/test_intro_deck.py` pins them against config. Phase 07.1 added the Risiko-Matrix slide after slide 31 and set the story-block and debriefing minutes per `.planning/phases/07.1-risk-based-learning-chain-cia-risk-register-from-the-mechtec/07.1-DECK-CHECKLIST.md` (RISK-09, D-19) |
| `MHP Company Profile DE - Jubilee Logo.pptx` | Company profile deck | kept manual | MHP-branded, Out of Scope in PROJECT.md |
| `13052026_VWI meets MHP_Offenes Treffen.pptx` | Talk deck (33 slides) | kept manual | Unrelated to the game, not game material |
| `DanielGhebreselassie 1.jpg` | Speaker portrait for the intro deck | kept manual | Personal image; not copied into `content/assets/` |
| `Stanullo Claudio_2022_04.jpg` | Speaker portrait for the intro deck | kept manual | Personal image; not copied into `content/assets/` |
