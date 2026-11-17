# Project Research Summary

**Project:** CIA-Planspiel Automotive — Post-Workshop Refinement
**Domain:** Deterministic, hand-calculated paper security business game with a single JSON config driving both an exhaustive balance simulation and generated print material
**Researched:** 2026-09-29
**Confidence:** MEDIUM-HIGH (sim/balance/toolchain findings are HIGH — verified by running code on this machine; game-design and debrief patterns are MEDIUM — from reference games and doctrine summaries)

## Executive Summary

This is not a software product but a content build pipeline for a live paper game: one `simulation_config.json` must feed two consumers that must never disagree — a deterministic enumeration that proves balance, and printed sheets that facilitators calculate by hand. The closest reference game (*Decisions & Disruptions* — deterministic, budgeted, GM-run, paper-tracked) already answers most MHP feedback points: separate ledgers for budget vs performance, no selling/downgrading, a GM master sheet, and a "perfect game" debrief. No reference game lets overspending pay off, and none refunds downgrades.

The recommended approach is to extract the formulas into one small shared package (`planspiel/`: config, rules, enumerate, printmodel, fmt, render) with the existing root scripts as thin shims, derive every printed number through the same `rules.py` the sim uses, and make templates format-only. An equivalence test replays the printed hand-calculation steps against the sim over a dense input grid. Order: test harness + characterization → extraction → rule changes (TDD) → print pipeline proven on the attack worksheet first → remaining documents → rebalance → retire legacy docx/pptx generators. Rules change before templates are written; numbers change after the generator exists.

The dominant risk is game-design, not tooling. Running the full enumeration showed the planned overspend-penalty calibration is ill-posed: KZ clamps at 100 (so any X>0 "passes" a naive check), and step rewards (OEM-Audit tiers, M7 tiers, Exzellenz +5/L3, E-target bonus) let a team at its budget edge gain up to **+34 KZ for going 8k over** with one upgrade — no sane linear X neutralizes that. The criterion must be decided before calibration, and softening step rewards or capping overspend may be required. Other verified risks: 91% of valid combos are over budget (~4 GB JSON/tier unless the enumeration streams), the Final-Index is dominated by RoS·100 and the 0.85 utilization filter hides the real optimum (72% utilization), the sim applies a per-wave E-target KZ bonus/malus that is printed nowhere, MiKTeX hangs scripted builds on a GUI install prompt, and the config loader reads UTF-8 as cp1252.

## Key Findings

### Recommended Stack

Project-local, uv-managed Python venv (the `python` in Git Bash is Inkscape's bundled 3.12 without pip; `pip` targets a different Store Python 3.11). Jinja2 → LuaLaTeX (current decision) or Typst (flagged alternative) render stage; pytest + syrupy snapshots + pypdf smoke checks. Everything upstream of the final render stage is identical for both renderers.

**Core technologies:**
- **uv + pyproject.toml + uv.lock** (Python ≥3.12): one reproducible env; `uv run …` kills the interpreter trap. *ARCHITECTURE.md suggests `requirements.txt` + `.venv` — STACK's uv recommendation is stronger (lockfile, uv already installed); pick one in phase 1.*
- **Jinja2 3.1.6** with `\VAR{}`/`\BLOCK{}` delimiters, `StrictUndefined`, `finalize=tex_escape`, numbers forced through `|num`/`|eur` filters — needed because the config contains 9× `&`, plus `_`, `%`, `€`.
- **LuaLaTeX + fontspec** on MiKTeX updated 23.10 → 25.12 with `tikzfill`, `tabularray`, `ninecolors` installed; always `--disable-installer` + subprocess timeout; tcolorbox `raster,skins` (never `[most]`) for 63×88 mm cards, 3×3 per A4, Python-side page chunking.
- **Reproducible PDFs**: `SOURCE_DATE_EPOCH` + `FORCE_SOURCE_DATE=1` (verified byte-identical); commit PDFs + `manifest.json` of input hashes.
- **pytest 9.1.1, syrupy 6.1.1** (`.tex` / view-model snapshots), **pypdf 6.19.0** (slow smoke: key number tokens in built PDFs).
- **Typst 0.15.0 (PyPI)** as alternative renderer: zero escaping, no MiKTeX, ~10× faster (~3 s vs ~30 s), lockfile-pinned; downside 0.x stability and new syntax for the user.

Minor toolchain disagreements to settle during planning: `latexmk` (STACK) vs direct `lualatex` (ARCHITECTURE); `line_statement_prefix="%%"` (STACK says don't, ARCHITECTURE example sets it — follow STACK).

### Expected Features

**Must have (table stakes, P1):**
- **T8** Linear overspend penalty, never profitable, with printed lookup table (0–10k: −X, 10–20k: −2X…)
- **T9** RoS split into *eigene Kosten* vs *externe Effekte* (two labelled rows on the tracking sheet)
- **T6/T7** Fixed vocabulary (*Levelwechsel* vs *Maßnahmentausch/-wechsel*) + decided, printed downgrade rule
- **T10** Veiled pre-wave names + facilitator clue matrix (every attack inferable from ≥2 clues)
- **T1** Card legend ("So liest du eine Maßnahmenkarte") + **T2** one-page "So funktioniert eine Welle"
- **T4** Printed team tracking sheet in calculation order (replaces 15-min whiteboard write-up)
- **T5** Facilitator master sheet — **missing from Active requirements**
- **T3** Worked example "Welle 0" (fixes 34-min wave 1) — **missing from Active requirements**
- **T11** Scheduled 15–20 min debrief with question set — **missing from Active requirements**; MHP schedule had no debrief slot

**Should have (P2, after validation):**
- **D1** "Perfekte Strategie" debrief sheet generated from full enumeration, showing each team's percentile — unique capability no reference game has
- **D2** 2–3 min impulse debrief after each wave; **D3** "Controller:in" scribe role per team; **D7** one-page feedback form

**Defer / fold into T5:** D4 shrinking timers, D5 quick vote, D6 in-character FAQ; downgrade-with-OPEX-saving only if a future run shows demand.

**Anti-features (do not build):** dice, digital GM app, hidden mechanics, downgrade refunds, loan/interest mechanics, flat penalty bands, purchasable threat intel, full live leaderboard after every wave, non-linear worksheet formulas.

### Architecture Approach

One-directional data flow: sources (`simulation_config.json`, `content/texte.toml` for all German prose, `print/planspiel.sty` + `templates/*.tex.j2`) → core (`config.validate` → `rules` → `enumerate` / `printmodel`) → outputs (`build/` gitignored, `final_documents/generated/*.pdf` + manifest committed), with a single `build.py {check|balance|docs|all}` driver.

**Major components:**
1. **`planspiel/config.py`** — load to frozen dataclasses, `validate()` incl. hand-calc invariants (`base_severity == mitigation_cap`, `severity_multiplier == 1`, weights ≤1 decimal, KZ slope ≤1 decimal — wave 3's 17/7 fails today)
2. **`planspiel/rules.py`** — the only copy of every formula; new `overbudget_penalty`, separate `security_spend` (RoS denominator) vs `budget_balance` (Budget Review / penalty); `evaluate_event` + `effect_rows` dispatched on the same event `type` so printed effect lines are generated, not typed
3. **`planspiel/enumerate.py`** — streaming generator + in-process aggregates (top-K, percentiles, best in- vs over-budget, dominance, Pareto count); full JSONL dump only on request; automated "overspend never profitable" gate
4. **`planspiel/printmodel.py`** — audience-scoped view models (PRE_ATTACK / REVEAL / FACILITATOR) so veiling is enforced by construction; all derived constants (Fall-2 threshold, full damage, KZ slope, RoS base loss 620)
5. **`planspiel/fmt.py` + `render.py`** — German number formatting (k€ → "20.000 €", "0,4", typographic minus) without `locale`; LaTeX escaping; lualatex driver
6. **`content/texte.toml`** — all prose keyed by config id, with veiled/revealed variants; lint forbids digits in narrative text; moves ~150 lines of `MEASURE_META` out of Python

### Critical Pitfalls

1. **X calibration is ill-posed** — clamp makes it trivially pass; step rewards give +34 KZ per started 10k near the budget line. *Avoid:* decide criterion first (global / trim-back / marginal), calibrate on raw and clamped KZ per tier, and if trim-back needs X > ~5, escalate softening step rewards or capping overspend to the user.
2. **Over-budget enumeration explodes** (~4 GB/tier, OOM in the analysis script). *Avoid:* streaming aggregators; cache per-combo tuples once and sweep X in memory instead of re-enumerating (~3 min/tier).
3. **Sim ≠ paper through float noise, rounding, and boundaries** — E = 18.999… flips the E-target; `round()` half-to-even; `ceil` on negatives; existing Budget Review off-by-one at 25k/50k/75k (sim `>=` vs print "25.001"). *Avoid:* integer/Fraction arithmetic, one `started_steps()` helper tested at edges, boundary text generated from the tier list, prefer clean slopes and printed lookup tables so nobody rounds.
4. **Hidden print invariants and unprinted E-target mechanic** — printed Fall-2 threshold, "Schaden = (31−GR)×20.000" and "620" rely on invariants a rebalance can silently break; E-target bonus/malus in `simulate_outcomes.py:448-449` is printed nowhere. *Avoid:* derive everything in `printmodel`, print≡sim equivalence test, mechanic-coverage test (fails today on `e_target`).
5. **Toolchain and content traps** — MiKTeX AutoInstall=ask hangs builds; `load_config` reads cp1252 (mojibake); config strings use transliterated umlauts; unescaped `%` silently drops text; veiling leaks via file names, PDF metadata, bonus descriptions, and wave weights; hand-made wording/colours/branding in the docx get lost. *Avoid:* first P-TeX plan is a non-interactive smoke build; UTF-8 fix + lint; auto-escape; forbidden-term scan incl. metadata; per-document content inventory and side-by-side before replacing.
6. **Goodhart-prone Final-Index** — RoS·100 dominates, KZ saturates, underspending is double-rewarded (RoS denominator + Budget Review). *Avoid:* report top-K, Pareto points, measure frequency in top 1%, unfiltered.

## Implications for Roadmap

Reconciles ARCHITECTURE's 9-step build order with PITFALLS' phase labels (P-Sim, P-Rules, P-TeX, P-Print, P-Balance, P-Handoff).

### Phase 1: Simulation Foundation (P-Sim)
**Rationale:** No tests exist and extraction touches every formula; every later phase needs exact arithmetic, UTF-8 loading and memory-safe over-budget enumeration.
**Delivers:** uv venv + lockfile; characterization tests pinning current outputs; extraction into `planspiel/config|rules|enumerate` with root-script shims; `read_text(encoding="utf-8")`; exact/integer arithmetic; streaming aggregates; `config.validate()` with hand-calc invariants (warnings for now).
**Avoids:** Pitfalls 2, 6, 8 and the interpreter trap.

### Phase 2: Rule Changes (P-Rules, TDD)
**Rationale:** Rules change printed content (Budget Review card, RoS sheet, tracking-sheet rows), so they must be settled before any template is written — definitions only, final values come in Phase 6.
**Delivers:** Linear overspend penalty as config parameter with `started_steps()`, clamp order and Sparprogramm handling defined; `security_spend`/`budget_balance` ledgers; RoS without event effects + zero-cost guard; removal of the line-539 over-budget filter + "never profitable" gate; downgrade/change move set; E-target print-or-remove; Budget Review boundary fix; config text split for veiling (`display_name`/veiled vs revealed).
**Addresses:** T6, T7, T8, T9, T10 (data side).
**Avoids:** Pitfalls 1 (criterion), 4, 5, 7.

### Phase 3: Content Source Split (parallel with Phase 2)
**Rationale:** Independent of rule changes once Phase 1 is done; templates need it.
**Delivers:** `content/texte.toml` with all prose (MEASURE_META, event narratives, veiled/revealed attack texts) in UTF-8 umlauts instead of transliterations; coverage + digit lint; per-document inventory of existing docx/pptx content, colours, branding.
**Avoids:** Pitfalls 8, 13.

### Phase 4: Print Pipeline on One Document (P-TeX)
**Rationale:** The attack worksheet carries the highest print-sync risk and exercises every pipeline piece.
**Delivers:** First plan = MiKTeX update + non-interactive smoke build (or Typst decision); `fmt`, Jinja env, `planspiel.sty`, `render.py`, reproducible build + manifest; generated `Angriff-{1,2,3}` worksheets (lookup tables where Fall-3 interpolation is awkward; recovery step moved onto the worksheet); print≡sim equivalence test.
**Uses:** Jinja2/LuaLaTeX/tcolorbox (or Typst), syrupy, pypdf.
**Avoids:** Pitfalls 11, 12.

### Phase 5: Remaining Print Material & Didactics (P-Print)
**Rationale:** Depends on the proven pipeline and final rule set; T3 depends on T2+T4.
**Delivers:** Measure cards + legend (T1), event & Budget Review cards, budget sheet, RoS sheet, tracking sheet (T4, two cost rows), "So funktioniert eine Welle" (T2), worked example "Welle 0" generated from `rules` (T3), facilitator master sheet with answer keys and debrief questions (T5, T11), revised schedule with debrief slot, version stamp in footers, veiling scan (text, file names, metadata), mechanic-coverage test green.
**Avoids:** Pitfalls 9, 10, 13.

### Phase 6: Rebalance (P-Balance)
**Rationale:** Needs the gate from Phase 2 and the generator from Phase 5 so every tuning iteration costs one command.
**Delivers:** X calibrated on the agreed criterion (raw + clamped, per tier); possibly softened step rewards; clean KZ slopes (fix wave 3's 17/7 and OT); hand-calc warnings promoted to errors; top-K/Pareto/unfiltered reports; regenerate all. May loop back to Phase 2 if the required X is absurd — that is a user decision.
**Addresses:** D1 (perfect-strategy sheet) once numbers are stable.
**Avoids:** Pitfalls 1 (value), 3, 6.

### Phase 7: Legacy Retirement & Facilitator Handoff (P-Handoff)
**Delivers:** Legacy docx/pptx, `pptx_output/` and old generators to archive (xlsx calculator per decision); CLAUDE.md "Print-Sync-Falle" rewritten; "Was ist neu" sheet; stale-rule lint on manual docs (intro deck, Audit-Mail, Steckbrief); timed dry run by someone who didn't write the rules; optional D2, D3, D7.
**Avoids:** Pitfall 14.

### Phase Ordering Rationale

- Characterization before extraction; rule definitions before templates; values after the generator. This preserves the 2026-09-29 decision "generate docs before rebalancing" in its refined form: *rules* before docs, *numbers* after.
- Phases 2 and 3 can run in parallel after Phase 1.
- The Phase 4 smoke build is a hard gate for all print work — a MiKTeX hang would block everything downstream.

### Research Flags

Needs `/gsd-plan-phase --research-phase`:
- **Phase 2:** overspend criterion and its interaction with step rewards; bounded change-model enumeration (if downgrade/swap moves are allowed).
- **Phase 4:** renderer choice, then card/worksheet layout (tcolorbox raster vs Typst grid, print scaling, cut lines) — only spikes compiled, no full card sheet.
- **Phase 6:** calibration method (trim-back sweep over cached tuples) and balance-metric selection.

Standard patterns (skip research): Phase 1 (pytest/uv/refactor behind characterization tests), Phase 3, Phase 5 (patterns in FEATURES), Phase 7.

## Decisions Needed from User

These feed requirements scoping — do not decide silently.

1. **Overspend penalty criterion for X.** (a) Global: max over-budget ≤ max in-budget per tier on unclamped KZ; (b) Trim-back: every over-budget combo loses to its own trimmed in-budget version (recommended); (c) Marginal: X ≥ largest single-upgrade gain (infeasible: ~34 KZ/started 10k due to step rewards). Measured global minimums: X = 2.21 / 0.83 / 0.39 (low/med/high). If (b) needs X > ~5: cap overspend (e.g. max 30k), void step bonuses when over budget, or soften steps (Exzellenz +5/L3 is the main driver).
2. **Penalty before or after the KZ clamp at 100** — and whether the sim's per-wave clamp should stay (it makes results path-dependent).
3. **Sparprogramm-induced overruns:** count overrun only against the original plan, allow a free re-plan window, or penalize anyway?
4. **Event discounts out of RoS too (symmetry)?** Research recommends yes for both directions; removing Operative Unterstützung shifts the optimum toward fewer measures. Also: does the Kurswechsel init difference count as own spend (team decision) or external?
5. **Level downgrade allowed?** FEATURES recommends no downgrade and no refund (reference-game norm, no new enumeration paths, clean "sunk cost" debrief point). PITFALLS offers "allowed, no Init refund, OPEX lower from next wave", which requires a change model in the sim. Refunds are out either way.
6. **E-target per-wave KZ bonus/malus** (`simulate_outcomes.py:448-449`, +5/7/10 or −3/−5/−7) exists in the sim but is printed nowhere — print it on the tracking sheet or remove it from the sim?
7. **Measure-card content: CIA only vs incident hints** (veiling conflict C1). Research recommends CIA only, with the measure→attack bonus link revealed on the attack worksheet, or at most a neutral "Bonus bei Vorfall N ab Level 2".
8. **Are wave CIA weights shown before the wave?** They effectively reveal the attack (a=0.6 ⇒ OT). Hide them, or show them neutrally labelled as a deliberate clue?
9. **LaTeX vs Typst** for the render step. LaTeX is currently decided; Typst is recommended as simpler (no escaping bug class, no MiKTeX, ~10× faster, lockfile-pinned).
10. **Config schema: printed quantities vs derived values.** Store hand-friendly printed quantities directly (e.g. `kz_per_point` instead of `kz_at_full_mitigation`, so nice numbers are guaranteed by construction) or keep current fields and validate derived values?
11. **Excel attack calculator** (`generate_attack_calculator.py`): keep and regenerate from `printmodel`, or retire?
12. **Final-Index weights and the 0.85 utilization filter.** RoS·100 dominates KZ, and the filter excludes the true optimum (72% utilization in low tier). Reweight/rescale RoS? Drop/lower the filter in the CLAUDE.md workflow?
13. Minor: `pyproject.toml`+uv vs `requirements.txt`; Budget Review boundary semantics (`>` vs `≥` at 25/50/75k); rounding rule written on paper (half up, at which step).

## Missing Requirements Found

Not in PROJECT.md's Active list:
- **Facilitator master sheet** (T5): per-wave thresholds, caps, bonus tables, event effects, per-team check rows, answer keys for reference selections — this is the Core Value.
- **Debrief slot + question set** (T11): 15–20 min, structured reaction → description → analysis → application; time funded by T4 + T3 (~25 min recovered).
- **Worked example "Welle 0"** (T3): fictional practice incident with a deliberately mediocre selection, generated from `rules` and golden-tested.
- **"Was ist neu" sheet** for facilitators who ran MHP, plus stale-rule lint on the manually maintained docs.
- **UTF-8 display strings in config:** replace transliterations (Massnahme, Geschaeftsfuehrung…) with ä/ö/ü/ß; fix the `read_text()` encoding.
- Also worth adding: veiling clue matrix (≥2 clues per attack), version stamp on printed pages, E-target print-gap resolution.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions verified against PyPI/CTAN; interpreter, MiKTeX, Jinja, syrupy and Typst spikes run locally. Layout packages MEDIUM (no full card sheet built) |
| Features | MEDIUM | Primary rulebooks read in full (D&D, B&B, CAH, T&T); debrief/exercise doctrine from abstracts and summaries |
| Architecture | HIGH | Grounded in reading existing code and extracting text from the current worksheets; reproducible-PDF verified |
| Pitfalls | HIGH (sim/balance), MEDIUM (TeX, facilitation) | Numbers from running the full 4^10 enumeration per tier |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- X calibration under the chosen criterion has not been run (only global minimum and marginal maximum measured).
- Balance impact of removing discounts from RoS — re-run and compare argmax.
- Bounded change-model enumeration needed if any mid-game move beyond a static selection stays legal.
- Full card/worksheet layout unproven in either renderer; print scaling and duplex untested.
- Time savings claimed for T3/T4 and the ≤5 min/team/wave target need a timed dry run.
- Content of manual docs (intro deck, Audit-Mail, Steckbrief) not inventoried for old-rule references.

## Sources

### Primary (HIGH confidence)
- Local enumeration runs of `simulate_outcomes.py` over all 4^10 selections per tier; locale/encoding probes; `initexmf` config; LaTeX/Typst/Jinja/syrupy spikes; `SOURCE_DATE_EPOCH` reproducibility test
- Codebase: `simulate_outcomes.py` (77, 448-449, 510, 536, 539), `analyze_simulation_results.py`, `generate_pptx_cards.py`, text of `final_documents/Angriff-*.docx`, `Budget.docx`, RoS sheet, Events pptx
- PyPI JSON API, CTAN (tcolorbox, tabularray, latexmk), MiKTeX download page, Jinja2/uv/syrupy docs

### Secondary (MEDIUM confidence)
- Decisions & Disruptions rulebook and GM cheat sheet; Backdoors & Breaches Visual Guide v2; Control-Alt-Hack CCS'13 evaluation; Threats & Trade-offs (2025); Kaspersky KIPS overview; worked-example effect
- pdfTeX manual (reproducibility), MiKTeX issues #1213/#748/#1598

### Tertiary (LOW confidence)
- TOPSIM handbook summaries, NIST SP 800-84, CISA CTEP, ENISA exercise guides and ROSI, Crookall (2010), Impulse-Debriefing-Spiral (2021), player-aid UX articles

---
*Research completed: 2026-09-29*
*Ready for roadmap: yes (after user decisions 1–8 are resolved during requirements)*
