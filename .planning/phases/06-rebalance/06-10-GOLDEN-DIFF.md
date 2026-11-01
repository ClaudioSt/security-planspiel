# 06-10 Golden diff (adoption of the D-04-approved candidate)

**Reference:** D-04 decision recorded in `06-TUNING-REPORT.md` (answer "Freigeben", 2026-11-01, approval of all 13 points).
Adopted files: `simulation_config.json` (byte copy of `candidate_config.json`) and `content/` (copies of `candidate_content/clues.toml` and `candidate_content/texte.toml`; `digit_allowlist.toml` and `giveaway_terms.toml` were identical).

All golden files were written only through the reviewed path (`--update-golden`), after the D-04 approval and after the code and test updates of this plan. Raw terminal output: `build/06-10-golden-fast.txt` (gitignored).

## Changed golden files (fast set)

| File | Change | Why |
|---|---|---|
| `tests/golden/characterization_{low,medium,high}.json` | re-bootstrapped (54 cases per tier, 51 valid); 2044 to 2057 lines added per file | The census tags (`census:remaining_*`, `g_eq_threshold_*`) mark plans that sit on the budget-review and threshold boundaries of the old config. With the new budgets, thresholds and costs the old sample no longer touches those boundaries, so the sample was rebuilt by the bootstrap path (file removed, then `--update-golden`). The 27 named strategy plans, the edge cases and the dependency cases are kept (same codes). No wave-3 `.5` tie exists on the tuned config any more (all slopes are one decimal), so the tie rounding rule is covered by the test-only config in `tests/support/ties.py` |
| `tests/golden/answer_keys.json` | 212 lines changed | thresholds 22/20/24, slopes 2.0/1.4/2.0, bonuses, tier budgets and start KZ, the three re-chosen reference paths (end KZ 56/58/57), review tiers 0/9/18/27, X = 3; the Final-Index row is re-pinned here once: `KZ + 10 * RoS2` printed exactly (52,6 / 54,7 / 57,6), no suffix |
| `tests/golden/worksheet_tex.json` | 3 sha256 values (angriff-1_ransomware, angriff-2_ot, angriff-3_exfil) | worksheet constants and case texts follow the new waves |
| `tests/golden/welle0.json` | unchanged | the practice block was not part of the tuning (`practice.check_example` still holds) |

## Golden update summary (fast)

Condensed from the terminal section "golden updates (review before commit)" of `uv run pytest --update-golden -q` (only the first 30 lines are printed by the harness; the complete list is the git diff of the files above):

```
== answer_keys.json ==
waves.1.check_cases[0][0]   "Fall 1: GR <= 23" -> "Fall 1: GR <= 22"
waves.1.check_cases[0][2]   "-6" -> "-8"
waves.1.check_cases[1][0]   "Fall 2: GR >= 31" -> "Fall 2: GR >= 30"
waves.1.check_cases[1][2]   "+10" -> "+8"
waves.1.check_cases[2][0]   "Fall 3: 23 < GR < 31" -> "Fall 3: 22 < GR < 30"
waves.1.check_cases[2][2]   "-6 + (GR - 23) x 2" -> "-8 + (GR - 22) x 2"
waves.1.check_table[...]    thresholds shifted by one, KZ column from -6..+8 to -8..+6 (wave 1)
waves.1.keys.*              reference selections, CIA, E value, bonus, damage, KZ per tier
waves.3.check_table[5][2]   "approx +7,57" -> "+6"   (no approximation any more)
waves.3.keys.kz_attack[2]   "approx +9,76" -> "-5"
paths.{Low,Medium,High}     start and both windows: the re-chosen reference paths
final.remaining             30.000/56.000/42.000 EUR -> 51.000/57.000/54.000 EUR
final.review_delta          +5 -> +18 (and the other tiers)
final.final_index           row re-pinned (this is the single re-pin of the Final-Index row held back by 06-03)
== worksheet_tex.json ==
sha256.angriff-1_ransomware, sha256.angriff-2_ot, sha256.angriff-3_exfil
```

## Golden update summary (slow)

_Filled in by Task 2 after `uv run pytest -m slow --update-golden`._
