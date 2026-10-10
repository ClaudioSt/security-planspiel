# Assets for the generated print material

This folder holds company assets and design guidelines for the print material that is generated from
`simulation_config.json` and `content/texte.toml` (Phases 4 and 5). `content/texte.toml` stays text-only:
logos, images, fonts and colour or layout facts live here, never in the text source.

## How to add files

Create the subfolder you need and drop the file in:

- `images/` for illustrations and photos
- `logos/` for company logos
- `fonts/` for embeddable font files
- `brand/` for brand guidelines or colour palettes

Record every new file in the provenance table below (origin and licence or credentials). Design facts
that were read from the hand-maintained documents (colours, fonts, page geometry) are in
`GUIDELINES.md`.

## Provenance

| File | Origin | Licence / credentials |
|------|--------|-----------------------|
| `images/zeitungsartikel_bild_audit.png` | Copied byte for byte from `final_documents/Zeitungsartikel_bild_audit.png` (md5 `9d607b1920cd012c57f91ed1442aee37`), the image embedded in `Zeitungsartikel.docx` | Carries C2PA content credentials issued through OpenAI's media service; no prompt text. Grayscale, 1448 x 1086 |
| `images/zeitungsartikel_bild_fabrik.png` | Copied byte for byte from `final_documents/Zeitungsartikel_bild_fabrik.png` (md5 `2557114b903d7ecb5377304949e13a1d`), the image embedded in `Zeitungsartikel.docx` | Carries C2PA content credentials issued through OpenAI's media service; no prompt text. Grayscale, 1448 x 1086. The picture shows a padlock screen and is kept deliberately as a visual clue |

The originals stay in `final_documents/` until the legacy files are archived (LEG-01); the copies avoid
changing that folder.

## Rules

- Material players see before a wave must not use file names or metadata that name an attack. The file
  names above are neutral (they describe the newspaper picture, not an attack). The automated check over
  rendered pre-wave material comes in Phase 5 (VEIL-02).
- No MechTech logo exists yet. The header image of `Unternehmenssteckbrief MechTech.docx` is template
  residue from an unrelated document and was not carried. A logo can be added under `logos/`.
- The two speaker photos and the MHP decks in `final_documents/` are not copied here (see
  `content/INVENTORY.md`).
