# Obsolete — hand-maintained MHP print material (config state of commit `1cfb2fa`)

These 15 files are the hand-maintained docx, pptx and pdf material that was printed for the MHP run:
the worksheets (`Angriff-*.docx`, `Budget.docx`, `Return on Security und Final Wert.docx`), the card
decks (`Massnahmenkarten_Security-Game.pptx`, `Events_Security-Game.pptx`), the story documents
(`Unternehmenssteckbrief MechTech.docx`, `Zeitungsartikel.*`, `Anfrage-Mail.*`, `Audit-Mail.pdf`) and the
two newspaper images.

Their numbers equal `simulation_config.json` at commit `1cfb2fa`, except for the Budget Review
boundaries, which are printed as "25.001". They are **not** synchronised with the current
`simulation_config.json` and must not be used at a session.

The current game material is `final_documents/generated/`, produced by `uv run planspiel print`. The
frozen old values for the "Was ist neu" sheet live in `content/mhp_baseline.json`.

The folder name `2026-07` is the date of the material (config commit `1cfb2fa`, 2026-07-06), not a
statement about the workshop date, which stays open (D-33).
