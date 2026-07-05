# Obsolete — pre-rebalance simulation data (generated 2026-01-24 to 2026-01-28)

These files were generated against a `simulation_config.json` that no longer
exists. The config was substantially rewritten on 2026-06-23 and 2026-07-03
(commits `caa757e`, `faad8b4`, `a55d275`, `742b9d1`):

- Budget tiers changed: low 200k→350k, medium 300k→400k, high 400k→450k
- `kz_start` became per-tier (70/60/50) instead of one global value (60)
- E-targets changed: 18/20/22 → 15/17/19
- Wave `e_threshold`/`kz_bonus`/`kz_malus` and all bonus-measure values changed
- The damage/KZ formula changed from `kz_unit` + `e_divisor` to
  `kz_at_full_damage`/`kz_at_full_mitigation` linear interpolation
- All wave events were replaced (different IDs, different mechanic types);
  `final_events` (Budget Review) didn't exist at all before
- Only the M1-M10 measure CIA/cost tables stayed the same

None of these files are usable for current balance analysis. Kept here for
historical reference only; not tracked by git (see `.gitignore`). Current
data lives at the repo root: `sim_low.json`, `sim_med.json`, `sim_high.json`.
