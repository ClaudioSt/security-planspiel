# Phase 7: Intro deck checklist (LEG-02, D-18)

Deck: `final_documents/Planspiel_Einführung + Grundlagen.pptx` (37 slides, hidden: 6, 7, 22, 28, 36). Nothing in the deck has been edited yet. Plan 07-07 edits it only after the approval at the bottom of this file.

Extraction (2026-11-03, read-only, python-pptx): all 37 slides, every shape and group, the table cells, the hidden flag (`show="0"`), the speaker notes and the field elements. Compared with `simulation_config.json` (`session_schedule`, `budget_tiers`), `content/texte.toml` (`story.*`, `sheets.ablauf`) and `README.md`.

Searches over the intro deck (slides and notes), case-insensitive:

| Search terms | Result |
|--------------|--------|
| Whiteboard, Pinnwand, Tafel (D-02: the board write-up step is gone) | 1 hit: slide 36 title "Spielplan / Vorlage für die Pinnwand" (finding row slide 36). No hit in the notes. |
| Maßnahmenwechsel, E-Ziel, E-Wert, E-Target, -15, 25.001, Bonus, Malus, Change, Erstattung, Kurswechsel, Sparprogramm, Überzieh, Recovery, Level, Final-Index, Debrief, Welle 0, Übungswelle, a euro-figure pattern | Only false positives ("Change" in MHP marketing text, "rund" inside "grundlegende"). See "Not present in the deck". |
| `veil.name_hits` with profile `names` over every slide and the notes | One slide: 36 ("Ransomware"). No other slide names an attack (config names: Ransomware, OT-Störung, Datenexfiltration). Profile `story` additionally finds the generic word "Phishing" on slides 19 and 21 (decision d). |

Speaker notes contain MHP marketing text only, no game rules and no board terms.

## Slide findings

Proposed texts are German (the deck language). "Hidden" is the state in the file today. Every minute figure and the team size name their config key in the Source cell. Clock times are removed, not replaced (D-04: the facilitator fills them in by hand).

| Slide | Hidden | Current text | Problem | Proposed change | Source |
|-------|--------|--------------|---------|-----------------|--------|
| 1 | no | Subtitle "06.07.2026" (plain run, not a field) | Date of the MHP run; there is no fixed date for the next workshop | Decision (a). Recommended: empty the run (no date) | none (no date in config) |
| 23 | no | Under "Sicherheitsmaßnahmen" the three category boxes (Physische, Technische, Organisatorische) carry the descriptions of slide 19: "Diese Bedrohungen entstehen durch absichtliche, oft kriminelle Handlungen ...", "Natürliche und physikalische Gefahren ...", "Hierzu zählen Bedrohungen die durch Fehler ... " | Copy error from the threats slide: a measures slide describes threats. Not an outdated rule, found during extraction | Decision (e1). Physische: "Schutz von Gebäuden, Räumen und Hardware vor unbefugtem Zutritt und Umwelteinflüssen." Technische: "Technische Verfahren und Systeme, die Daten und IT-Systeme schützen." Organisatorische: "Regeln, Abläufe und Schulungen, die den sicheren Umgang mit IT festlegen." | none (teaching content) |
| 26 | no | "5 Minuten Pause bis 15:00" | Clock time fixed to the MHP run | "5 Minuten Pause" | `session_schedule.blocks.break_1` (5 min) |
| 28 | yes | SPIELPHASEN: five phases "Spiel-einführung", "Informations- und Lesephase", "Budget-verhandlung", "Angriffs-simulation (3 Runden)", "Reflexion im Plenum" | No Welle 0, no debrief; "Reflexion im Plenum" and the phase list describe the MHP run. Best vehicle for D-19 (decision b) | Unhide and rewrite as the flow overview, six phases in the order of the schedule: 1 "Einführung", 2 "Story-Gruppenarbeit", 3 "Übungswelle", 4 "Maßnahmen und Budget", 5 "Angriffswellen", 6 "Abschluss und Debriefing". No figures, no attack names (labels follow `sheets.ablauf.blocks.*.label`; "Übungswelle" is `sheets.ablauf.practice_label`). Phase 6 needs a copied shape group (run text alone cannot add a sixth phase) | `session_schedule.blocks` order (intro, story_groups, wave_0, measures_budget, wave_1..3, closing, debrief); no minute figures on the slide |
| 30 | no | "Ihr seid ein Beratungsteam aus 3–4 Personen und wurdet beauftragt, MechTech langfristig sicherer zu machen ..." (runs: "...aus 3–4 Personen und wurdet beauftragt, ", "MechTech", " langfristig sicherer zu ") | Project format is 5 persons per team (D-19) | "Ihr seid ein Beratungsteam aus 5 Personen und wurdet beauftragt, ..." (first run only; 07-07 pins the composed string "Beratungsteam aus N Personen" against config) | `session_schedule.persons_per_team` (5) |
| 31 | no | Time box "20" + " min" | Schedule gives the story and group block more time | "25 min" | `session_schedule.blocks.story_groups` (25 min) |
| 31 | no | "Material: Unternehmenssteckbrief, Beauftragungsmail, Zeitungsartikel" | The generated set calls it Anfrage-Mail and has a fourth pre-wave document, the Audit-Mail | "Material: Unternehmenssteckbrief, Anfrage-Mail, Zeitungsartikel, Audit-Mail" | `session_schedule.print_list` (spieler-unternehmenssteckbrief, spieler-anfrage-mail, spieler-zeitungsartikel, spieler-audit-mail) and `sheets.ablauf.print.*` |
| 32 | no | "MechTech macht euch folgendes Angebot: ein Budget von 350.000 € zur Umsetzung eurer Maßnahmen. Mit guter Argumentation lässt sich mehr Budget herausschlagen - allerdings steigen dann auch die Erwartungen." (one run after "MechTech") | 350.000 € is not a tier any more (config tiers: low 370, medium 390, high 405 thousand euro); a single figure in a hand-maintained deck drifts | Budget tiers without a figure: " macht euch folgendes Angebot: ein Budget zur Umsetzung eurer Maßnahmen, dessen Höhe ihr aushandelt. Mit guter Argumentation lässt sich ein höheres Budget herausschlagen - allerdings steigen dann auch die Erwartungen." The figures live on the generated Teamheft | `budget_tiers` (no figure on the slide) |
| 32 | no | "Material: Budgetübersicht, Maßnahmenkarten" | Budget overview is now a page of the Teamheft | "Material: Teamheft, Maßnahmenkarten" | `session_schedule.print_list` (spieler-teamheft, spieler-massnahmenkarten) |
| 33 | no | "20 Minuten Pause bis16:50" | Second break is shorter; clock time fixed to the MHP run | "15 Minuten Pause" | `session_schedule.blocks.break_2` (15 min) |
| 34 | no | "Material: Angriffsblatt, Events (pro Welle)" | Material names are the old ones | "Material: Arbeitsblatt der Welle, Eventkarten, So funktioniert eine Welle" | `session_schedule.print_list` (angriff-1..3, spieler-eventkarten, spieler-so-funktioniert-eine-welle), `sheets.ablauf.print_attack_sheet` |
| 35 | no | Title "Endergebnis und Reflexion" | Last block is now Abschluss (Budget Review, RoS) plus Debriefing | Title "Abschluss und Debriefing" | `session_schedule.blocks.closing`, `blocks.debrief` |
| 35 | no | "Material: Endergebnisblatt" | The result sheet is now the Teamheft (Budget Review and RoS page) | "Material: Teamheft" | `session_schedule.print_list` (spieler-teamheft) |
| 35 | no | "30 min" | Still the right total, but it is now two blocks | Keep "30 min" (closing 10 + debrief 20). The 07-07 deck test pins it as the sum | `session_schedule.blocks.closing` (10) + `blocks.debrief` (20) |
| 36 | yes | "Spielplan / Vorlage für die Pinnwand" with budget template ("Bewilligtes Budget: 150.000 €"), attack boxes "Ransomware Angriff 1", "Phishing Angriff 2", "Supply Chain Attack Angriff 3", event boxes, CIA boxes | The board write-up step is gone (D-02). Shows a budget figure and attack names before the game; the names are also wrong (real: Ransomware, OT-Störung, Datenexfiltration) | D-19: delete the slide; the flow overview is slide 28 (decision b). Nothing of the Pinnwand template is kept | none (no figure, no attack name remains) |
| 34 (optional) | no | Body has no mention of the Change-Fenster | The change window is a rule the deck never introduced; the wave page "So funktioniert eine Welle" explains it | Decision (e2). Recommended: skip (adding it needs a copied paragraph and the wave page covers it) | none |

Candidates from the research that the file does not confirm or that need no change:

- Slide 29 (MechTech facts): checked against `story.steckbrief` (Göppingen, 1 Halle 3.500 m², 12 CNC-Maschinen, ca. 80 Mitarbeitende, ca. 15 Mio. EUR, ca. 60 % Umsatz OEM, Liefertermintreue > 98 %, 2 Administratoren). All match. No change.
- Slide 32 "30 min" matches `session_schedule.blocks.measures_budget` (30). Slide 34 "20 min pro Welle" matches `blocks.wave_1` to `wave_3` (20 each). No change.
- Slide 25 (Return on Security definition) is generic and consistent with the rules (RoS counts own spend). No change.
- Slides 22 and 6/7 (hidden, Sicherheitsbedarf, Vision, Mission): no game rule. They stay hidden and unchanged.
- Auto date fields (`datetime1`, slides 2 to 36) are fields, not runs. They update on opening and are not edited. Only slide 1 carries a plain date.
- Typos in teaching slides (for example "Vier grundlegende Strategie" on slide 21) are outside this plan's scope.

## Decisions needed

**(a) Slide 1 date "06.07.2026".** Options: new date, remove, or keep as the MHP run date. Recommendation: remove the date (no fixed date for the next workshop exists; the test group sees the deck on 2026-11-25 and a wrong date is worse than none). Setting 25.11.2026 is possible but would be wrong for every later session.

**(b) Flow-overview vehicle (D-19).** Options: (1) unhide and rewrite hidden slide 28 as the overview with six phases and delete slide 36; (2) rebuild slide 36 in place. Recommendation: (1). The overview then sits right after the "Planspiel" chapter slide, before the customer slide, which is where the audience wants it. Both options need a duplicated shape for a sixth phase; the slide-36 template would be deleted either way. Welle 0 appears only as the phase "Übungswelle" in the overview (no extra slide, no minute figures on the overview).

**(c) Team size (D-19 "project format").** Recommendation: the slide-30 wording "Beratungsteam aus 5 Personen" composed from `session_schedule.persons_per_team`; 07-07 pins the composed string against config in the deck test. The only alternative is figure-free wording ("Beratungsteam") and is used only if you choose it as an override (recorded in `## Approval`).

**(d) Attack-like words outside slide 36.** Slides 19 and 21 name "Phishing / Social Engineering" (and slide 19 also "Malware" and "Supply Chain Attack") as generic threat examples in the IT-security basics part. They are not attack names of the game (`names` profile: no hit), only the story giveaway list knows "Phishing". Options: keep as teaching content, or reword. Recommendation: keep. The deck is generic teaching material shown before the story documents, and the veiled attack names (Ransomware, OT-Störung, Datenexfiltration) appear nowhere outside slide 36, which is deleted.

**(e) Optional additions (not outdated rules).** (e1) Fix the copy error on slide 23 (measure categories described with the threat texts), recommended yes. (e2) Add a Change-Fenster sentence to slide 34, recommended no.

## Not present in the deck

Searched slides and notes of the intro deck, so the list is not padded. None of these exist in the deck and none is changed:

- E-target bonus/malus ("E-Ziel", "E-Wert", "E-Target": no hit)
- "Maßnahmenwechsel" (no hit)
- the flat -15 overspend penalty (no hit; no "Überzieh", "Sparprogramm", "Kurswechsel", "Erstattung" either)
- Budget Review "25.001" boundaries (no hit; no euro figure except the two budget figures on slides 32 and 36 and the date on slide 1)
- RoS including event effects (slide 25 holds a generic definition only)
- board terms: Whiteboard, Pinnwand, Tafel (search terms; one hit, slide 36 title, listed above)

## Other hand-maintained documents (SC4)

Terms searched in the MHP company profile deck (29 slides) and in the VWI deck (33 slides), slides and notes, case-insensitive: Planspiel, Kundenzufriedenheit, KZ, MechTech, Budget, Angriff, Welle, Ransomware, Maßnahme, E-Wert, Return on Security, RoS, and Whiteboard, Pinnwand, Tafel. Result for both decks: 0 hits. They contain no game rule and are not edited.

Generated story documents (Audit-Mail, Steckbrief, Anfrage-Mail, Zeitungsartikel): `uv run planspiel texts` on 2026-11-03 printed `0 Fehler, 0 Warnung(en)`. That run includes `check_story_mechanics` (no KZ, OPEX, Level, tier amounts, RoS and so on in the story texts) and `check_giveaway`. Read-through of `story.audit_mail` and `story.steckbrief`: the Audit-Mail lists five audit topics (IAM/PAM, Backup & Disaster Recovery, Patch Management, Logging & SIEM, OT-Segmentierung) as a deliberate clue and states no rule; the Steckbrief holds company facts only. The Anfrage-Mail mentions "Budget für ein Beratungsprojekt" without a figure. No outdated rule in any of the four documents.

## Other deck findings

None found. Search terms: see the previous section (profile deck and VWI deck, both 0 hits).

## Approval

Verdict: (pending)
Date: (pending)
Requested changes: (pending)
Decisions: (a) pending, (b) pending, (c) pending, (d) pending, (e1) pending, (e2) pending
Other deck findings: none, no outcome line needed.
