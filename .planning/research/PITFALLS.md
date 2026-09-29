# Pitfalls Research

**Domain:** Deterministic, hand-calculated tabletop security business game (CIA-Planspiel Automotive). Covers rebalancing via exhaustive enumeration, mid-design scoring-formula changes, and migrating hand-maintained print material to LaTeX generated from `simulation_config.json`.
**Researched:** 2026-09-29
**Confidence:** HIGH for the simulation/balance pitfalls. They were checked against the current code and config by running the enumeration (numbers below). MEDIUM for LaTeX/MiKTeX toolchain pitfalls: tool docs plus local checks of the MiKTeX config. MEDIUM for facilitator-communication pitfalls: based on the MHP feedback plus general game-design practice.

> **Suggested phase labels used below.** No roadmap exists yet. The roadmapper should map these to real phase numbers.
> - **P-Sim**: simulation foundation (golden tests, exact arithmetic, encoding, streaming enumeration)
> - **P-Rules**: rule changes in config and sim (overspend penalty, RoS ledger, downgrade, Maßnahmen-/Levelwechsel, boundary semantics)
> - **P-TeX**: LaTeX toolchain and template pipeline
> - **P-Print**: content generation (worksheets, cards, tracking sheet, explainer, veiling, worked example)
> - **P-Balance**: rebalance and calibration of X by full enumeration
> - **P-Handoff**: facilitator briefing, dry run, release

---

## Evidence Gathered for This Research (reproducible)

A scratch script imported `simulate_outcomes.py` unchanged and ran it over all 4^10 = 1,048,576 selections per tier. 782,336 of them satisfy the dependencies. "Raw KZ" means KZ without the per-wave clamp to [0,100].

| Finding | low | medium | high |
|---|---|---|---|
| Valid combos that are **over budget** (event-adjusted) | 712,882 (91%) | ~658k | ~585k |
| In-budget combos whose KZ **saturates at 100** | 6,453 | 15,611 | 26,703 |
| Best in-budget raw KZ (incl. Budget Review) | 119.96 | 123.0 | 125.0 |
| Best over-budget raw KZ (before review) | 171 | 163 | 155 |
| ...with the current flat −15 | **156** (beats in-budget by 36) | 148 | 140 |
| Min X per started 10k so that **no over-budget combo beats the global best in-budget** (raw KZ) | 2.21 | 0.83 | 0.39 |
| Max KZ gain per started 10k from **one single level upgrade that crosses the budget line** | **34.0** (M7 0→1, 8k over) | 28.0 | 25.4 |

Other verified facts:
- Best low-tier Final-Index (KZ + 100·RoS, event OPEX excluded, no utilization filter) = 249.4. That combo has KZ 100 (clamped), RoS 1.49 and uses **72% of budget**. The CLAUDE.md-prescribed `--budget-utilization 0.85` filter would have **excluded the true optimum**.
- `simulate_outcomes.py:77` and `analyze_simulation_results.py:9,15` use `Path.read_text()` with no encoding. On this machine `locale.getpreferredencoding()` is `cp1252`, so `"früh"` loads as `"frÃ¼h"` (mojibake).
- Float E-values: with `weights = 0.5/0.3/0.2`, the CIA triples (12,36,11) and (15,31,11) give an exact E = 19 but a float E = 18.999999999999996. That makes `e_value >= e_target` false where paper says true. Probably unreachable with the current measures, but a latent flip for any rebalanced weights.
- The Budget Review text says "0–25.000 → 0, 25.001–50.000 → +5". The sim tier `[25, 5]` uses `>=`, so at exactly 25k left **the sim gives +5 and the printed rule gives 0**. The same off-by-one happens at 50k and 75k. Costs are integer k, so these values are reachable.
- MiKTeX on this machine: version 23.10 (setup 2023-12, last update check 2023-12). `[MPM]AutoInstall = 2` (the "ask" mode). A scripted build that needs a package it does not have will open a GUI prompt.
- Full-output size today: ~5.1 KB per result (`sim_low.json` = 131 MB / 25,685 results). Including all ~782k valid combos means **~4 GB per tier**. Pure-Python evaluation takes ~170 s per tier for 1M selections.

---

## Critical Pitfalls

### Pitfall 1: Calibrating X against the "best in-budget combo" is ill-posed. The KZ clamp at 100 and step rewards make the number meaningless

**What goes wrong:**
The planned criterion is "X such that overspending never beats the best in-budget combo". It has three separate problems:

1. **Clamp saturation.** With clamped KZ, the best in-budget combo already hits 100 in every tier, so *any* X > 0 "passes". The calibration then proves nothing. (Measured: at X = 0.5 the best over-budget KZ is 99.5 < 100 = pass.)
2. **Global vs local.** With unclamped KZ, the global criterion needs only X ≈ 0.4–2.2 depending on tier. Real teams are not global optimizers, though. A team sitting at its own budget edge gains up to **+34 KZ by going 8k over** with one upgrade (low tier, M7 0→1). This flips the OEM-Audit tier and the "Kritische Schwachstelle" tier at the same time. Any linear X below ~34 leaves overspending *locally* profitable, and X = 34 per started 10k is absurd.
3. **Step rewards vs linear penalty.** The KZ rewards are step functions: OEM-Audit tiers, M7 level tiers, E-target bonus/malus, Exzellenz +5 per L3 measure (up to +50). A linear penalty cannot neutralize a step gain near the boundary. The worst-case marginal gain is set by the biggest step, not by the average slope.

**Why it happens:**
The criterion was phrased before anyone looked at the shape of the reward surface. "Best in-budget" is the natural baseline for an optimizer, but workshop teams are satisficers who make one more purchase.

**How to avoid:**
- Before calibrating, **decide and write down the criterion** (a user decision; flag it in P-Rules). Candidates:
  - (a) *Global*: max over-budget score ≤ max in-budget score, per tier, on **unclamped** KZ and on Final-Index.
  - (b) *Trim-back*: for every over-budget combo O, some in-budget combo reachable by downgrading only O's measures scores at least as well. This is the realistic "would the team have been better off trimming?" test.
  - (c) *Marginal*: X ≥ the max single-upgrade gain across the boundary. This one is infeasible as shown above.
- Recommend (b), or (a) plus a cap. If (b) needs X > ~5, the linear rule is fighting the step rewards. Then say so and propose alternatives instead of silently picking a huge X:
  - Overspending allowed only up to a cap (e.g. max 30k), with the rest forbidden.
  - The penalty applies to **all** KZ-relevant step rewards (the "over budget → Exzellenz-Bonus and OEM-Audit bonus void" style).
  - Soften the steps themselves in P-Balance. For example, Exzellenz +5 per L3 is the main driver of over-budget raw KZ 155–171.
- Run the calibration on **raw (unclamped) KZ** *and* on the clamped KZ the players actually see. Report both.
- Calibrate per tier. Take the **max X across tiers** (one printed X for all tiers) and check that the low tier (which needs the largest X) does not make the high tier's penalty feel draconian.

**Warning signs:**
- The calibration script reports "passes at X = 0.5" (clamp artifact).
- The required X differs by more than 3× between tiers (0.39 vs 2.21 today).
- The top over-budget combos all contain many L3 measures (Exzellenz-driven).

**Phase to address:** P-Rules (define the criterion, implement X as a config parameter). P-Balance (calibrate X and possibly soften the step rewards).

---

### Pitfall 2: Including over-budget combos makes the enumeration output explode (~4 GB/tier) and the analysis tools unusable

**What goes wrong:**
`simulate_outcomes.py:539` currently drops over-budget combos. That is why today's outputs are "only" 131–362 MB. Removing the filter, which you must do to test the penalty, multiplies the output by ~30×: ~782k results × ~5.1 KB ≈ 4 GB per tier. `analyze_simulation_results.py` does `json.loads(path.read_text())`, so it loads everything into RAM (Python dicts cost ~5–10× the JSON size). The run crashes or swaps. The dataset is also >1 GB, which breaks the git/LFS/.gitignore conventions again.

**Why it happens:**
The enumerator writes the full per-wave audit trail for every combo. That was fine when a strict filter left ~25k survivors.

**How to avoid:**
- Split the enumerator into (1) a pure `evaluate(selection, tier, rules) -> Outcome` function and (2) **streaming aggregators**. Aggregators produce: running max/argmax per metric, top-K heaps (K ≈ 100) per metric, histograms of KZ/RoS/Final-Index, counts by over-budget step, and per-measure-level inclusion frequencies in the top 1%.
- Write per-combo detail only for the top-K and for named strategies. Make the full dump opt-in (`--dump-jsonl`) and use JSONL, not one JSON document.
- Keep the calibration loop (varying X) *outside* the expensive evaluation. Compute raw KZ, overrun and cost once per combo (782k small tuples fit in memory, as tested). Then sweep X over the cached arrays in seconds. Do not re-enumerate per X.
- Budget for ~3 min per tier in pure Python. If Kurswechsel/downgrade paths are ever enumerated (see Pitfall 7), the count multiplies by ~30–90×. At that point, vectorize with numpy over the 4^10 grid or prune to the top-K base combos.

**Warning signs:**
- An output file > 500 MB.
- `MemoryError` or a swapping laptop in the analysis script.
- Someone commits `sim_*.json` again.

**Phase to address:** P-Sim (streaming and aggregation refactor, before any rule change needs over-budget data).

---

### Pitfall 3: Final-Index is Goodhart-prone. RoS·100 dominates, KZ saturates, and the utilization filter hides the real optimum

**What goes wrong:**
- `Final-Index = KZ + 100·RoS`. KZ is capped at 100 and thousands of combos per tier hit that cap, so KZ **stops discriminating** among good strategies and RoS decides everything. The best low-tier combo gets 149 points from RoS and 100 from KZ.
- RoS rewards spending *less*: `(620 − damage − cost)/cost` has cost in the denominator. The Budget Review *also* rewards unspent budget (+15 KZ at ≥75k left). Underspending is therefore rewarded twice. The measured optimum uses only 72% of the budget.
- The standard analysis workflow (`--budget-utilization 0.85`) filters out exactly these combos. The balance check then looks at a different population than the one players can reach. Dominant cheap strategies go unseen.
- Averaging hides dominance. The mean KZ/RoS over ~25k–780k combos says nothing about what a team that reads the cards well will do. Most combos are strategies nobody would pick.

**Why it happens:**
Composite indices built from a bounded metric (KZ) and an unbounded ratio (RoS) are dominated by the ratio. Filters added for speed turn into silent assumptions.

**How to avoid:**
- Report balance on **top-K and dominance**, not means. For each tier give: the top-20 by Final-Index, by clamped KZ and by RoS; how often each measure-level appears in the top 1%; and the number of Pareto-optimal (KZ, RoS) combos. A healthy game has many diverse Pareto points.
- Run without the utilization filter, or at least report the unfiltered argmax next to the filtered one. Drop or lower `0.85` in the CLAUDE.md workflow if it hides the optimum.
- Check the scale: over the realistic top-K, the spread of `100·RoS` should be comparable to the spread of KZ. If not, reweight (e.g. `weight_ros`) or rescale RoS. This is a design decision to flag, not to fix silently.
- Consider whether the per-wave `min(100, …)` clamp should stay. It also makes hand calculation path-dependent (see Pitfall 9).

**Warning signs:**
- The top-10 by Final-Index all have utilization < 80%.
- The top-10 all share the same 3–4 measures.
- KZ = 100 for all top-50 combos.

**Phase to address:** P-Balance (metrics and reports). P-Sim (the aggregators that produce them).

---

### Pitfall 4: Changing the RoS ledger breaks the denominator and splits "cost" into two numbers players must track

**What goes wrong:**
- **Two ledgers.** Removing event OPEX from RoS means "cost for budget" (includes Sparprogramm −20, the Operative-Unterstützung discount and Kurswechsel init differences) and "cost for RoS" (own spend only) now differ. If the tracking sheet has one "Gesamtkosten" line, facilitators will put the wrong one into RoS.
- **Symmetry.** Today the only event OPEX effect is a *discount* (−2k per active measure). It currently *lowers* cost and so *raises* RoS for many-measure strategies. Removing it shifts the optimum toward fewer measures. That can move the balance, so re-run the enumeration. PROJECT.md already flags "symmetry for discounts to confirm". Decide explicitly whether the Kurswechsel init difference counts as own spend (a team decision) or as an event effect (forced by an event).
- **Division edge cases.** The zero-cost combo (all L0) exists (1 per tier) and gives RoS = x/0. Very cheap combos (e.g. one L1 measure at 16k) give extreme ratios. If any future event or refund makes RoS-cost ≤ 0 (e.g. a downgrade refund exceeding spend), RoS flips sign or becomes infinite.
- **Stale constant.** `620` (base losses = Σ base_severity·s_unit) is computed in `analyze_simulation_results.py` and appears in print. It ignores `severity_multiplier`, which is 1.0 today. If P-Balance changes severities, s_units or multipliers, the printed 620 goes stale.

**How to avoid:**
- Define both ledgers in README and on the tracking sheet as **separately labelled rows** ("Budgetverbrauch" vs "Sicherheitsinvestition (für RoS)"). Generate both from the same config.
- In code: have `compute_ros(own_cost, damage, base_losses)` guard `own_cost <= 0` (define RoS = 0 or "n/a", and write that rule on paper too), and unit-test the zero-cost and minimal-cost cases.
- Derive `base_losses` in one place (config or sim) and **generate** it into every print document. Never type 620 by hand.
- Re-run the full enumeration after the ledger change and compare the argmax before and after.

**Warning signs:**
- The worked example and the tracking sheet show different "Kosten" numbers for the same team.
- The literal `620` appears in any template.
- The RoS argmax changes composition after the ledger change with no one noticing.

**Phase to address:** P-Rules (ledger definition, guards, tests). P-Print (tracking sheet rows). P-Balance (re-verification).

---

### Pitfall 5: Off-by-one and sign errors in "per started 10k" and in tier boundaries (sim vs paper disagree)

**What goes wrong:**
- "Je angefangene 10.000 €" means `steps = ceil(overrun_k / 10)` for overrun > 0, so 1k over → 1 step, 10k → 1 step, 10.5k → 2 steps. Common wrong implementations:
  - `overrun // 10 + 1` gives 1 step at 0 over and 2 steps at exactly 10k.
  - `ceil(remaining / 10)` on the *negative* remaining budget gives `ceil(-0.8) = 0`.
  - `int(-8/10) = 0`.
  - The penalty is computed on the budget *before* event adjustments (Sparprogramm −20).
- This inconsistency already exists. The Budget Review prints "25.001–50.000 → +5" while the sim uses `>= 25`, so they disagree at exactly 25k/50k/75k (reachable with integer-k costs).
- **Order vs clamp.** If the penalty is applied after the final `min(100, …)` clamp, a saturated team pays it in full. If it is applied before, a team at 130 raw pays nothing visible. The sim clamps **per wave**, so the order is already path-dependent.
- **Involuntary overrun.** Teams plan their budget before the wave-2 "Sparprogramm −20". A team that planned 331–350k in the low tier ends up over budget through no decision of its own. The linear penalty then punishes an event, which contradicts the spirit of "event effects out of RoS".

**How to avoid:**
- Implement one helper `started_steps(overrun_k, step_k)` and unit-test it at the edges: −1, 0, 0.5, 1, 9, 10, 10.001, 11, 20, 21.
- Write the rule on paper in the **same inclusive/exclusive form** the code uses, and generate the boundary text from the tier list, never by hand. Fix the Budget Review boundary now (choose `>` or `≥` and align both).
- Fix the order in writing: "Strafe wird vor/nach der Begrenzung auf 0–100 abgezogen". Test both saturated and unsaturated teams.
- Decide how Sparprogramm-induced overruns are treated. Options: the penalty counts only overrun against the *original* plan, or teams get a free re-plan window after the Sparprogramm.

**Warning signs:**
- A golden-run test at exactly 10k/20k over fails or gives different results by hand vs in code.
- Facilitators ask "zählt 10.000 schon als zwei?".

**Phase to address:** P-Rules.

---

### Pitfall 6: Float arithmetic and Python rounding make the simulation disagree with hand calculation

**What goes wrong:**
- E-values are float sums with weights like 0.4/0.2/0.3. Exact integers can come out as x.999999999996, which flips the discrete `e_value >= e_target` check (±8 to ±17 KZ). This is latent today and could become live after rebalancing the weights.
- KZ interpolation produces non-terminating decimals. Exfil: −7 + (r/7)·17 means steps of 2.428…; OT has steps of 1.2. The sim carries 119.96000000000001 while facilitators round on paper. Neither the rounding step nor the rounding mode is defined.
- Python `round()` rounds half to even (`round(2.5) == 2`). German facilitators round half up (kaufmännisch). A sim that "rounds like paper" with `round()` still disagrees on every .5.
- `round(e_value, 1)` is used for display, but the comparison uses the unrounded value. The printed audit trail can show "E = 19.0, target 19, not reached".

**How to avoid:**
- Do sim arithmetic in `fractions.Fraction` or in integers (weights in percent, e.g. 40/40/20, dividing only at the end). The data size makes this cheap enough, or it can be vectorized.
- Define on paper **where** rounding happens (e.g. "KZ-Delta je Welle auf ganze Zahl runden, ab ,5 aufrunden") and **mirror exactly that** in code with `Decimal.quantize(ROUND_HALF_UP)`.
- Better: design values so no rounding is needed. Choose mitigation caps and KZ endpoints so that (kz_full_mitigation − kz_full_damage)/cap is an integer or a simple half (e.g. cap 8 with span 16 gives 2 per point, which is what Ransomware does already). Exfil (cap 7, span 17) and OT (cap 10, span 12) do not. This is a P-Balance design constraint that directly serves hand-calculability.
- Golden tests compare the sim to a hand-computed value **after the paper rounding rule**.

**Warning signs:**
- Any sim KZ with a non-integer or float-noise value.
- A facilitator's hand result differs from the answer key by 1.
- The E-target check differs between the printed lookup and the sim.

**Phase to address:** P-Sim (exact arithmetic, rounding helper). P-Balance (choose "clean" slopes).

---

### Pitfall 7: Rules that let the selection change mid-game (Kurswechsel, downgrade) are invisible to a static enumeration

**What goes wrong:**
The sim evaluates one static selection across all three waves. Kurswechsel is a `noop` ("kostenneutral angenommen, nicht simuliert"). Any exploit that uses a mid-game change is never tested, for example:
- Downgrade with an init refund: rent L3 for wave 1, downgrade for a refund, use the cash elsewhere.
- Swap into Exzellenz-L3 right before wave 3.
- A "Maßnahmenwechsel" that breaks a dependency (M1 L3 requires M2 ≥ L2).

"Maßnahmenwechsel" (swap measure A for measure B) and "Levelwechsel" (change level of one measure) are different move sets with different exploit surfaces. The MHP feedback shows players read them differently.

**How to avoid:**
- Define the move set precisely in config terms: what counts as one change, and whether a swap includes level choice. State what happens to dependencies (the change is illegal, or dependents auto-downgrade), to init costs (difference charged, no refunds on downgrade?) and to OPEX (from which wave?).
- Recommended default for downgrade: allowed, **no init refund**, lower OPEX from the next wave. That removes the "rent-and-refund" loop and keeps hand calculation trivial. It is a user decision, so flag it.
- Extend the sim with a **bounded** change model: after wave 1, apply at most one legal change. To keep the cost manageable, evaluate changes only from the top-K base combos and from named strategies (≈ 782k × up to 90 changes is too many in pure Python). Verify that the best "with change" score does not beat the best static score by more than a tolerance you choose.
- Make the sim handle per-wave selections (`selection_by_wave`). Events like Exzellenz-Bonus and OEM-Audit then read the selection *at that wave*.

**Warning signs:**
- The rule text uses "Wechsel" without saying "Maßnahme" or "Level".
- There is no test with a dependency-breaking change.
- The sim still has `type == "noop"` for Kurswechsel after P-Rules.

**Phase to address:** P-Rules (definitions, sim support). P-Balance (bounded change enumeration).

---

### Pitfall 8: `load_config` reads UTF-8 as cp1252 on Windows, so reusing it in the LaTeX generator prints mojibake

**What goes wrong:**
`simulate_outcomes.py:77` and `analyze_simulation_results.py` call `Path.read_text()` without `encoding=`. On this machine (cp1252, UTF-8 mode off) `"früh"` becomes `"frÃ¼h"`. Numbers are unaffected, so nobody noticed. The first generator that reuses `load_config()` for text (bonus descriptions, attack descriptions, event texts) will print "Ã¼" on every card. Separately, the config **mixes spellings**: event texts use transliterations ("Geschaeftsfuehrung", "Massnahmenwechsel", "verkuendet") while attacks use real umlauts. Printed material will look inconsistent.

**How to avoid:**
- Fix `read_text(encoding="utf-8")` everywhere as a P-Sim task with a test that loads a known umlaut string.
- Normalize all player-facing config strings to proper German (ä/ö/ü/ß) in one pass. Add a lint test that fails on `ae|oe|ue|ss` inside the known word list (or at least on "Massnahme") in player-facing fields.
- Run generators with `PYTHONUTF8=1` as belt-and-braces, but do not rely on it.

**Warning signs:**
- "Ã" in any generated .tex or PDF.
- The same word spelled two ways across cards.

**Phase to address:** P-Sim (encoding fix). P-Print (text normalization, before the first real render).

---

### Pitfall 9: Worksheets that are "linear" but still too slow under live time pressure

**What goes wrong:**
Wave 1 took 34 min against a 20 min plan. Linear formulas can still be slow when each wave requires, per team:
1. Recompute team CIA from ~10 measure cards.
2. Compute E with decimal weights.
3. Look up 2–3 bonus conditions.
4. Pick Fall 1/2/3.
5. Interpolate KZ with an awkward slope (2.43 per point).
6. Apply recovery (%).
7. Clamp per wave.
8. Apply events.
9. Apply the overspend penalty (ceil).

A new rule (penalty, second ledger, change rule) adds steps. The facilitator also has to explain *and* compute for 3 teams at once.

**How to avoid:**
- Move work out of the wave. Compute team CIA and all three E-values **once**, at the end of measure selection, on the tracking sheet (the selection is static unless a Kurswechsel happens). Only recompute on a change.
- Replace formulas with **printed lookup tables** generated from config: "Reduktion über Schwelle → Schaden / KZ-Delta" per attack in integer (or 0.5) steps. That is still hand-checkable and deterministic, but it is a lookup instead of arithmetic. It also removes rounding ambiguity (Pitfall 6).
- Use clean numbers by design (P-Balance): integer slopes, E-weights that give at most one decimal, recovery factors like 50%/25%.
- Time each worksheet with a stopwatch on the worked example: the target is ≤ 5 min per team per wave for an experienced facilitator. Count the arithmetic operations per wave and fail the design review if a rule change adds more than ~2.
- Worked example before wave 1. Generate it from the same `evaluate()` as a golden run so its numbers can never drift. Use a **fictional practice incident** with a neutral name and a deliberately mediocre selection, so it neither reveals an attack (veiling) nor anchors teams on an optimal strategy.

**Warning signs:**
- A worksheet has more than one division per wave.
- Any step needs a calculator for more than a 2-digit multiplication.
- The dry-run wave takes more than 20 min.

**Phase to address:** P-Print (tracking sheet, lookup tables, worked example). P-Balance (clean numbers). P-Handoff (timed dry run).

---

### Pitfall 10: Veiled attack names leak through mechanics, file names and metadata

**What goes wrong:**
The decision is: veil attack names before a wave, reveal when it hits, keep mechanics transparent. Leaks happen through:
- `bonus_measures[].description` ("EDR/XDR erkennt **Ransomware** früh"), which feedback item #2 wants shown on measure cards ("was haben Angriffe für Effekte").
- Per-wave CIA weights printed before the wave (a = 0.6 obviously means OT).
- File names (`Angriff-2_OT-Störung.pdf`), PDF titles and bookmarks (`hyperref` `pdftitle`), running headers and footers.
- The wave `name` field ("Ransomware") reused in templates for pre-wave material.
- The Audit-Mail and newspaper-article PDFs (manually maintained) naming the threats.

There is a real tension here: transparency about "what does this measure help against" versus veiling.

**How to avoid:**
- Split the config text fields: `name_veiled` / `teaser` (pre-wave, allusive) vs `name` / `reveal` (worksheet, post-hit). Split measure effects into a `hint` (veiled, e.g. "hilft bei Vorfällen mit verschlüsselten Daten") vs the bonus description on the reveal worksheet.
- Have each template declare its audience phase (`pre_wave` / `reveal` / `facilitator`). A test greps the rendered **pre-wave** outputs (text extracted from the PDF, file name, PDF metadata) for a forbidden-term list derived from the attack names and synonyms (Ransomware, Exfiltration, OT, Emotet, Phishing, SPS ...).
- Decide whether wave weights are shown pre-wave. Showing them is fine only if they are labelled neutrally ("Welle 2: Schwerpunkt Verfügbarkeit"), which may itself be the intended clue.

**Warning signs:**
- A pre-wave PDF contains any attack keyword in text, title, bookmarks or file name.
- Measure cards list bonus descriptions verbatim.

**Phase to address:** P-Rules/P-Print (config field split in P-Rules, templates and leak test in P-Print).

---

### Pitfall 11: The LaTeX pipeline breaks on content: escaping, German babel shorthands, €, and template-delimiter clashes

**What goes wrong:**
- Unescaped `& % $ # _ { } ~ ^ \` in config strings. `%` silently comments out the rest of the line, so a card loses text **without an error**. `&` breaks tables. `_` in IDs (`kritische_schwachstelle`, `wave_1`) errors outside math mode.
- `babel` with `ngerman` makes `"` an active shorthand (`"a` → ä, `"-` → hyphenation point). ASCII quotes in config text get mangled or silently vanish.
- `€`: under pdflatex it needs `\texteuro` (textcomp, in the kernel since 2020) or `eurosym`'s `\euro`, plus a font that has the glyph. With lualatex/fontspec the font must contain U+20AC. A missing glyph is **only a log warning**: the PDF has a blank where € should be.
- German number format: the config has 0.4 and 20 (k€), the print needs "0,4" and "20.000 €". Mixing `siunitx` locale settings with pre-formatted strings gives "20{,}000" or doubled separators. Unit confusion (k vs €) shows up as "20 €" on a budget card.
- Jinja2's default `{{ }}`/`{% %}` clash with LaTeX braces and `%` comments. jinja2 is also not installed and there is no dependency manifest.
- Umlauts in file names (`OT-Störung`) passed to `\input`/`\includegraphics` under pdflatex on Windows can fail or work only by accident.
- `article` defaults to **letterpaper**. Forgetting `a4paper` shifts everything on German printers.

**How to avoid:**
- One `tex_escape()` function, unit-tested with a string that contains every special character plus `"`, `€`, `ä ö ü ß`, `–`. Apply it **automatically** in the template environment (auto-escape filter), never by remembering to call it.
- Use jinja2 with LaTeX-safe delimiters (`\VAR{}`, `\BLOCK{}`, `%#` comments; a common, documented pattern), or plain Python `string.Template`. Pin it in a `requirements.txt`.
- Format numbers in Python (`de_number()`, `de_eur()`, including k→€ conversion) and pass finished strings to LaTeX. Do not mix this with siunitx.
- Prefer lualatex + fontspec with a font known to have € and German glyphs. If you use pdflatex: `\usepackage[T1]{fontenc}`, `lmodern`, `babel[ngerman]`, and write `\glqq/\grqq` or `\enquote` (csquotes) instead of raw `"`.
- ASCII-only generated file names (`angriff-2.pdf`). The German title goes inside the document.
- Treat LaTeX warnings as errors for missing characters: grep the log for `Missing character` and `Overfull \hbox` (text overflowing card edges) and fail the build.

**Warning signs:**
- A card text is shorter in the PDF than in the config.
- Blank space where € should be.
- `Missing character: There is no € in font` in the log.
- `Overfull \hbox` warnings.

**Phase to address:** P-TeX.

---

### Pitfall 12: MiKTeX on Windows hangs scripted builds (on-the-fly install prompt) and builds are not reproducible

**What goes wrong:**
- `[MPM]AutoInstall = 2` on this machine (the "ask" mode). The first time a template uses a package that is not installed (fontspec, csquotes, tcolorbox, eurosym ...), MiKTeX opens a **GUI dialog** from inside `subprocess.run`. The build appears to hang; in an agent/CI context it hangs forever.
- The MiKTeX installation is from 2023 and has never been updated. Installing packages against a current remote repository can fail on an outdated package database, and MiKTeX nags with "you have not checked for updates" on stderr.
- `latexmk` on MiKTeX needs Perl (it works locally, but it is an implicit dependency).
- Non-determinism: PDFs embed `/CreationDate`, `/ModDate` and a random `/ID`. Every rebuild produces a binary diff even when nothing changed, so "did the print material change?" cannot be answered by diffing. Stale `.aux` files after a template change give wrong page references or crash the build. Mixing engines (pdflatex/lualatex) on the same aux directory causes errors.
- Python-side non-determinism: iterating a `set` of strings has an order that depends on hash randomization and changes between runs, so card order shuffles.

**How to avoid:**
- Before the first build, run `initexmf --set-config-value=[MPM]AutoInstall=1` (install without asking) **or** pre-install an explicit package list with `miktex packages install <pkg>`. Run `miktex packages update-package-database` once. Document this in the generator README.
- Call `latexmk` with `-interaction=nonstopmode -halt-on-error -file-line-error`, a per-document `-outdir` in a build dir (not `final_documents/`), and a timeout on the subprocess.
- Reproducibility: set the environment variables `SOURCE_DATE_EPOCH` (e.g. the config's last commit time) and `FORCE_SOURCE_DATE=1`, and set `\pdftrailerid{}` (pdfTeX) or `\pdfvariable trailerid {}` (LuaTeX). Then a byte-identical rebuild is testable. Also iterate in `sorted()` / config order only.
- Clean builds (`latexmk -C`, or a fresh temp outdir) in the "release" target.

**Warning signs:**
- The build takes more than 60 s with no output.
- A "Package Installation" window appears.
- Two consecutive builds without changes give different SHA-256.

**Phase to address:** P-TeX (the first plan in that phase should be a toolchain smoke test: build a hello-world with every planned package, non-interactively).

---

### Pitfall 13: Replacing hand-maintained docx/pptx with generated PDFs silently drops manual content and branding

**What goes wrong:**
The current `final_documents/` carry manual work that exists nowhere in the config:
- Humanized phrasing (commit b44937b: "humanize distributed materials, strip AI-style dashes").
- Colour-coded levels and waves (72f54b2 "farbige level und welle").
- The Fall-3 gap fix text (742b9d1).
- The recovery explanation.
- MHP/"VWI meets MHP" branding and logos.
- Images (newspaper article pictures).

A generator built from config alone reproduces only the numbers. The old wording, colours and layout knowledge are lost, and the first playtest reveals the regressions. There is also a hybrid risk: some documents stay manual (intro pptx, Unternehmenssteckbrief, Zeitungsartikel, Anfrage-/Audit-Mail). They still reference rules or values (the Audit-Mail names the OEM-audit measures; the intro deck explains Budget Review −15) and now go stale **unchecked**.

**How to avoid:**
- Before writing templates: make an **inventory per existing document**. Extract all text (python-docx/python-pptx) into a checklist of every paragraph and table, and mark each item: config value / static prose to carry over / obsolete. Carry prose into template files or a `content/` text source, not into Python string literals.
- Build a visual side-by-side (old docx exported to PDF vs new PDF) as the acceptance check for each document.
- Keep old docx in `final_documents/legacy/` (or archive) until one successful dry run with the new PDFs.
- Put branding (colours, logo, fonts) in one shared LaTeX style file. Encode the level/wave colours from the existing pptx as named colours.
- For documents that stay manual, add a **stale-rule lint**: extract their text and grep for old-rule markers ("−15", "KZ -15", "Restbudget < 0", "620", old thresholds) and for every config number that appears. Report mismatches. This closes the CONCERNS.md sync gap for the remaining manual docs.
- Stamp each generated page footer with the config version or short hash and the date, so mixed old/new printouts are detectable at the table.

**Warning signs:**
- A generated worksheet has fewer paragraphs than the old docx.
- Colours or logo are missing.
- An intro-deck slide still says "−15".

**Phase to address:** P-Print (inventory and parity check before replacing each document). P-Handoff (stale-rule lint on the manual docs).

---

### Pitfall 14: Rule changes do not reach facilitators, or reach them half-way

**What goes wrong:**
Facilitators who ran the MHP workshop carry the old rules in their heads: flat −15, event OPEX in RoS, ambiguous Kurswechsel. Old printouts circulate. The new rules change what "Kosten" means (two ledgers), add a ceil-based penalty and a downgrade rule. A single facilitator applying an old rule at one table breaks cross-team comparability, which is the core of a competitive deterministic game. Players who hear a rule on a slide but do not find it on their sheet will argue at the table and cost wave time.

**How to avoid:**
- Generate a one-page **"Was ist neu"** facilitator sheet from a changelog in the repo (rule, old, new, why). The same source updates README and the intro-deck content checklist.
- Every rule appears **where it is applied**. The overspend penalty goes on the tracking sheet at the step where it is computed, not only in the rules explainer. Card legend and how-it-works sheet use the exact terms from config ("Maßnahmenwechsel", "Levelwechsel") and no synonyms.
- Put a facilitator answer key per wave in the facilitator pack. Because the game is deterministic, precompute outcomes for the worked example and 2–3 reference selections, so a facilitator can sanity-check a team result in 10 seconds.
- Version stamp on every page (Pitfall 13). Hold an explicit "throw away old printouts" step in the release checklist.
- Do a dry run with someone who did *not* write the rules, before the next workshop. Record every question they ask. Each question is a rule-ambiguity defect.

**Warning signs:**
- The dry-run facilitator asks "gilt das auch für...?".
- Two facilitators get different results for the same reference selection.
- The intro deck still shows old rules.

**Phase to address:** P-Handoff (plus P-Print for rule placement on sheets).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Keep `--budget-utilization 0.85` as the default balance filter | 30× smaller output, fast | Hides the true optimum (72% utilization in low tier); balance judged on the wrong population | Only as an extra view next to an unfiltered top-K report |
| Calibrate X by one global max comparison | One number, done | Clamp artifact plus local exploits remain (+34 KZ single upgrade) | Never as the sole criterion |
| Leave Kurswechsel as `noop` in the sim | No path enumeration | Downgrade/change exploits never tested | Only if the rules forbid refunds and changes cannot increase score (then prove it with a bounded test) |
| Hardcode German number formatting inside templates | Quick | Inconsistent "20.000 €" vs "20k" across docs | Never; use one Python formatter |
| Type prose into Python string literals in generators | Fast first render | Content edits need code edits; humanized text gets lost | Never for player-facing prose |
| Keep float weights and `round()` | No refactor | Sim vs paper drift at .5 and at exact thresholds | Only if golden tests prove no divergence over the full enumeration |
| Re-run the full enumeration for every candidate X | Simple loop | 3 min × tiers × X values | Never; cache per-combo tuples and sweep X |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Python → MiKTeX | `subprocess.run(["pdflatex", ...])` with default interaction and AutoInstall=ask, which hangs | `latexmk -lualatex -interaction=nonstopmode -halt-on-error`, timeout, AutoInstall=1 or pre-installed packages |
| Python → config | `Path.read_text()` without encoding (cp1252 on Windows) | `read_text(encoding="utf-8")` plus an umlaut test |
| jinja2 → LaTeX | Default delimiters clash with `{}` and `%` | Custom delimiters plus an auto-escape filter |
| Config k-units → print € | Printing `20` as "20 €" | A single `de_eur(k)` formatter; unit test "20 → 20.000 €" |
| Generated PDFs → git | Committing nondeterministic PDFs, so every build is a diff | `SOURCE_DATE_EPOCH` + trailer ID fixed, or commit only on release |
| Manual docs ↔ config | Assuming the untouched docs are still correct | Text-extraction lint for old-rule markers and numbers |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Full per-combo JSON with over-budget combos | 4 GB files, OOM in analysis | Streaming aggregators, top-K heaps, optional JSONL | As soon as the line-539 filter is removed |
| `json.loads(read_text())` on result files | RAM spikes of 5–10× file size | Never reload full dumps; analysis consumes aggregates | Files > ~300 MB (already `sim_high.json` = 362 MB) |
| Enumerating mid-game changes naively | 782k × 30–90 changes in pure Python means hours | Top-K base combos only, or numpy vectorization | Any change model |
| Per-X re-enumeration | 10 X values × 3 tiers × 3 min | Cache (raw KZ, overrun, cost, damage) per combo, sweep X in memory | Calibration phase |

## Security Mistakes

Not a security-sensitive system (offline content tooling). The domain-relevant equivalent is **information leakage to players**:

| Mistake | Risk | Prevention |
|---------|------|------------|
| Attack names in pre-wave material (text, file name, PDF metadata, bookmarks) | Players learn which attack comes next, so the veiling design collapses | Audience-tagged templates plus forbidden-term test on the extracted text and metadata of pre-wave PDFs |
| Facilitator answer key printed in the same PDF as player sheets | Teams see optimal strategies | Separate facilitator pack, distinct file prefix, "MODERATION" watermark |
| Worked example uses a strong strategy | Anchoring: all teams copy it, which kills strategy diversity | Deliberately mediocre, fictional example selection |

## UX Pitfalls (players and facilitators at the table)

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Two different "Kosten" numbers without labels | Wrong RoS, disputes | Two clearly named rows, generated from the same ledger code |
| Rule stated only in the explainer, not at the point of use | Forgotten penalty or clamp step | Put every rule on the tracking sheet at the step where it applies |
| Fall-3 interpolation by formula | Slow wave, arithmetic errors | Printed lookup table per attack |
| Cards printed with "Fit to page" scaling | Cards 3–6% too small, cut lines off | `hyperref` `pdfprintscaling=None`; content inside ≥ 5 mm printer margin; cut marks outside the content |
| Duplex card backs misaligned | Backs do not match fronts | Mirror the column order on back pages (long-edge flip); test print one sheet |
| Kurswechsel says "Wechsel" | Players do different moves at different tables | Separate defined terms "Maßnahmenwechsel" / "Levelwechsel" with examples |

## "Looks Done But Isn't" Checklist

- [ ] **Overspend penalty:** often missing an edge test at exactly 0/10/20k over and the clamp-order decision. Check the golden tests at the boundaries and the saturated-team case.
- [ ] **X calibration:** often reported on clamped KZ only. Check unclamped raw KZ, the trim-back criterion and per-tier numbers.
- [ ] **RoS change:** often missing the zero-cost guard and the discount-symmetry decision. Check the unit test for cost = 0 and the re-run argmax diff.
- [ ] **Budget Review text:** often misaligned by one at 25k/50k/75k. Check the generated boundary text against a test at exactly 25.
- [ ] **LaTeX build:** often "works on my machine" with MiKTeX prompts answered by hand. Check a non-interactive build from a clean outdir with a timeout.
- [ ] **Escaping:** often tested without `%`. Check that a config string containing `%`, `&`, `_`, `"`, `€`, `ß` renders fully.
- [ ] **Veiling:** often checked only in visible text. Check file names, PDF title, bookmarks and headers.
- [ ] **Generated worksheets:** often lose humanized prose and colours. Check the paragraph-level inventory and visual side-by-side.
- [ ] **Worked example:** often hand-typed numbers. Check that it is rendered from `evaluate()` with golden-test equality.
- [ ] **Manual docs:** often still show old rules. Check the stale-rule lint on the intro deck, Audit-Mail and Steckbrief.
- [ ] **Encoding:** check that `load_config` reads UTF-8, that no "Ã" appears in any .tex, and that there are no transliterated umlauts in player text.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| X chosen on a meaningless criterion | MEDIUM | Re-run the cached sweep with the trim-back criterion; possibly soften step rewards; regenerate print (cheap once generated) |
| Balance judged on the filtered population | LOW | Re-run without the filter using the streaming aggregator; compare the top-K |
| Mojibake or missing € in print | LOW | Fix encoding or font, rebuild; the version stamp identifies bad printouts |
| Old printouts or old rules used at a workshop | HIGH (live) | Answer key plus "Was ist neu" sheet; discard printouts by version stamp; pre-workshop dry run |
| Manual content lost in the generated doc | MEDIUM | Restore from `final_documents/legacy/` docx via the inventory; move prose into the template content source |
| MiKTeX hang in automated build | LOW | Kill, set AutoInstall=1 / pre-install packages, add a timeout |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 2 Output explosion | P-Sim | Unfiltered run per tier finishes in < 5 min with < 50 MB output |
| 6 Float/rounding drift | P-Sim (exact math), P-Balance (clean slopes) | Golden tests; no float noise in outputs; the E-target edge test passes |
| 8 Encoding / mojibake | P-Sim, P-Print | Umlaut load test; no "Ã" in the build tree |
| 1 X criterion ill-posed | P-Rules (criterion), P-Balance (value) | Written criterion; sweep report on raw + clamped + trim-back, per tier |
| 4 RoS ledger / denominator | P-Rules | Unit tests at cost 0/min; two-ledger rows on the tracking sheet |
| 5 Started-10k off-by-one, boundaries | P-Rules | Boundary test table; generated boundary text matches code |
| 7 Mid-game changes unsimulated | P-Rules, P-Balance | Bounded change enumeration: best-with-change ≤ best-static + tolerance |
| 3 Goodhart / hidden dominance | P-Balance | Top-K, Pareto count, measure frequency in top 1%, unfiltered argmax |
| 11 Escaping / babel / € | P-TeX | Special-character render test; log lint for missing characters and overfull boxes |
| 12 MiKTeX prompts / nondeterminism | P-TeX (first plan) | Non-interactive clean build with timeout; two builds byte-identical |
| 10 Veiling leaks | P-Rules (fields), P-Print (templates) | Forbidden-term scan on text and metadata of pre-wave PDFs |
| 9 Hand-calc time | P-Print, P-Balance, P-Handoff | Stopwatch on the worked example ≤ 5 min/team/wave; operation count per wave |
| 13 Lost manual content / branding | P-Print, P-Handoff | Per-document inventory signed off; visual side-by-side; stale-rule lint |
| 14 Facilitator communication | P-Handoff | Dry run by a non-author; zero unresolved rule questions; answer keys match |

**Ordering implications for the roadmap:**
- P-Sim must come first. Every later phase depends on exact arithmetic, UTF-8 loading and the ability to enumerate over-budget combos without 4 GB files.
- P-Rules must fix the *definitions* (criterion for X, ledgers, boundaries, change moves, config text-field split for veiling) before P-TeX/P-Print templates are written. The *values* (X, thresholds) can follow in P-Balance. This is consistent with the decision "generate docs before rebalancing": templates read values from config, so rebalancing afterwards only needs a rebuild.
- P-TeX's first plan should be a toolchain smoke test (Pitfall 12), because a MiKTeX hang blocks every later print plan.
- P-Balance may reopen P-Rules. If the trim-back criterion demands a large X, the right fix is softening step rewards or capping overspend. That is a user decision and should be raised, not silently absorbed.

## Sources

- Local verification (HIGH): scratch runs of `simulate_outcomes.py` functions over all 4^10 selections per tier (calibration, marginal-gain, Final-Index, float-edge scripts); `locale.getpreferredencoding()` check; `initexmf --show-config-value=[MPM]AutoInstall` → 2; `initexmf --report` (MiKTeX 23.10, last update 2023-12); `simulation_config.json` Budget Review description vs `_tier_lookup` semantics.
- Codebase: `simulate_outcomes.py` (lines 77, 305–314, 329–334, 463, 536–540), `analyze_simulation_results.py` (lines 9–23, 60–63), `.planning/codebase/CONCERNS.md`, `.planning/PROJECT.md`, `.planning/todos/pending/2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md`, git log (b44937b, 72f54b2, 742b9d1).
- [pdfTeX user manual (texdoc)](https://texdoc.org/serve/pdftex/0): `SOURCE_DATE_EPOCH`, `FORCE_SOURCE_DATE`, `\pdftrailerid` (MEDIUM; MiKTeX support inferred from pdfTeX being its engine).
- [Creating Fully Reproducible, PDF/A Compliant Documents in LaTeX](https://shen.hong.io/reproducible-pdfa-compliant-latex/) (MEDIUM).
- [MiKTeX issue #1213: install problem under GitHub Actions](https://github.com/MiKTeX/miktex/issues/1213) and [MiKTeX issue #748](https://github.com/MiKTeX/miktex/issues/748): `[MPM]AutoInstall=1` for non-interactive on-the-fly installs (MEDIUM; the exact meaning of value 2 = "ask" is from training knowledge and matches the MiKTeX Console options "Always / Ask me / Never").
- LaTeX escaping, babel `ngerman` `"` shorthands, `letterpaper` default, jinja2 LaTeX-delimiter pattern, `pdfprintscaling`: established LaTeX practice (MEDIUM, training knowledge; verify during the P-TeX smoke test).

---
*Pitfalls research for: deterministic hand-calculated security business game, rebalance + LaTeX print generation*
*Researched: 2026-09-29*
