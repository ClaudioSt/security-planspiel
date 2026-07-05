# Obsolete — pre-rebalance reference sheets (last touched 2026-01-27)

`mitigation_bewertungsblatt.md` and `cia_schnellreferenz.md` predate the
2026-06-23/2026-07-03 mechanics rewrite:

- Damage formula still uses `e_divisor` + a flat `KZ-Einheit x(-2)` per
  severity point, instead of the current `kz_at_full_damage`/
  `kz_at_full_mitigation` linear interpolation
- Budget tiers shown as 300k/400k/500k (current: 350k/400k/450k)
- `KZ-Start` shown as a flat 60 for all tiers (current: per-tier 50/42/34)
- Bonus-measure values are the pre-rebalance ones (e.g. M3 +2, M5 +3, M1 +2
  instead of current +6/+9/+8)
- All 9 listed events (Phishing-Kampagne, Cyber-Versicherung, Zero-Day-
  Schwachstelle, OEM-Audit [old boolean form], Produktionsdruck,
  Security-Experte kündigt, NIS2-Prüfung, Lieferanten-Datenpanne,
  Vorstandspräsentation) were replaced entirely on 2026-06-23 — none of
  them exist in the current `simulation_config.json`

Not updated in place because they duplicate content that `final_documents/`
already carries correctly (`Budget.docx`, `Angriff-{1,2,3}_*.docx`), which
is the single current source of truth for workshop print material per
`CLAUDE.md`. Kept here for historical reference only.
