# Design guidelines carried from the hand-maintained documents

Facts read from the files in `final_documents/` (now partly in `archive/mhp_print_material_2026-07/`; extracted 2026-10-08). They are the starting point for the
LaTeX templates of Phases 4 and 5, not a binding style guide. Phase 4 decides what is kept.

## MHP theme (measure cards and event cards, theme name "MHP")

| Role | Value |
|------|-------|
| dk1 | `262626` |
| dk2 | `575757` |
| lt2 | `B0B0B0` |
| accent1 | `000099` |
| accent2 | `1612FF` |
| accent3 | `CDD6FF` |
| accent4 | `DDEF03` |
| accent5 | `00CC67` |
| accent6 | `575757` |
| hyperlink | `262626` |

- Font: Segoe UI
- Slide size: 13.33 x 7.50 in

## Card semantics

- Level badge fill: L1 = accent5 `00CC67`, L2 = accent4 `DDEF03`, L3 = accent6 `575757`
- Badge text: white, 32 pt
- Dependency label and value: `C00000`
- Headings: accent1
- Event cards: narrative in accent2, 28 pt; rule text 24 pt; title 40 pt

## Word worksheets (attack sheets, budget sheet, RoS sheet)

- Font: Arial; the document uses the Office theme (accent1 `5B9BD5`, accent2 `ED7D31`, accent3 `A5A5A5`,
  accent4 `FFC000`, accent5 `4472C4`, accent6 `70AD47`)
- Paper: A4; margins left 3.0 cm (punch margin), right 1.5 cm, top 2.0 cm, bottom 2.0 cm
- Title 12 pt, body 10 pt

## Story documents

- Unternehmenssteckbrief: A4, margins left 2.5 cm, top 4.0 cm, bottom 1.8 cm (the 4.0 cm top margin was
  reserved for a template header that is not carried); Arial theme, title 12 pt, body 10 pt. Phase 5
  re-evaluates the top margin.
- Zeitungsartikel: masthead "AUTO TIMES" in Georgia 48 pt; serif body 9.5 pt; two columns with a
  separator from the second section on; grayscale images; the original is US Letter (21.6 x 27.9 cm,
  margins 1.8 / 1.5 cm), LaTeX uses A4
- Anfrage-Mail: Calibri 11 pt; the original is US Letter, LaTeX uses A4

## Fonts

Segoe UI, Georgia, Calibri and Arial are Windows system fonts. Phase 4 decides on embeddable alternatives
so that the LuaLaTeX builds are reproducible on other machines.
