---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 07
current_phase_name: session-flow-handoff
status: executing
stopped_at: Phase 7 context gathered
last_updated: "2026-11-03T19:03:36.342Z"
last_activity: 2026-11-03
last_activity_desc: Phase 07 execution started
progress:
  total_phases: 7
  completed_phases: 6
  total_plans: 62
  completed_plans: 55
  percent: 86
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-27)

**Core value:** Facilitators and players can run the game by hand without ambiguity: every rule is unambiguous, every printed number matches `simulation_config.json`, and no strategy exploits a rule loophole.
**Current focus:** Phase 07 — session-flow-handoff

## Current Position

Phase: 07 (session-flow-handoff) — EXECUTING
Plan: 6 of 12
Status: Ready to execute
Last activity: 2026-11-03 — Phase 07 execution started

Progress: [█████████░] 86% (6 of 7 phases)

## Performance Metrics

**Velocity:**

- Total plans completed: 50
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 7 | - | - |
| 2 | 8 | - | - |
| 03 | 3 | - | - |
| 4 | 6 | - | - |
| 5 | 16 | - | - |
| 6 | 10 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
| Phase 01 P01 | 15min | 2 tasks | 13 files |
| Phase 01 P02 | 12min | 2 tasks | 7 files |
| Phase 01 P03 | 55min | 3 tasks | 21 files |
| Phase 01 P04 | 50min | 3 tasks | 17 files |
| Phase 01 P05 | 35min | 2 tasks | 6 files |
| Phase 01 P06 | 9h | 4 tasks | 25 files |
| Phase 01 P07 | 3h | 3 tasks | 14 files |
| Phase 02 P01 | multi-session | 4 tasks | 31 files |
| Phase 02 P02 | multi-session | 3 tasks | 18 files |
| Phase 02 P03 | multi-session | 3 tasks tasks | 26 files files |
| Phase 02 P04 | single session | 2 tasks | 11 files |
| Phase 02 P05 | multi-session | 3 tasks | 17 files |
| Phase 02 P06 | 31min | 3 tasks | 11 files |
| Phase 02 P07 | ~1h | 2 tasks | 10 files |
| Phase 02 P08 | 2h | 3 tasks | 12 files |
| Phase 03 P01 | multi-session | 6 tasks | 31 files |
| Phase 03 P03-03 | multi-session | 3 tasks | 4 files |
| Phase 04 P02 | 40min | 3 tasks | 13 files |
| Phase 04 P01 | 35min | 3 tasks | 11 files |
| Phase 04 P03 | 35min | 3 tasks | 9 files |
| Phase 04 P04 | 40min | 3 tasks | 4 files |
| Phase 04 P05 | 30min | 3 tasks | 12 files |
| Phase 04 P06 | 75min | 3 tasks | 12 files |
| Phase 05 P01 | 90min | 3 tasks | 16 files |
| Phase 05 P02 | 85min | 2 tasks | 17 files |
| Phase 05 P03 | 95min | 2 tasks | 5 files |
| Phase 05 P04 | 30min | 2 tasks | 7 files |
| Phase 05 P05 | 30min | 2 tasks | 15 files |
| Phase 05 P06 | 30 min | 2 tasks | 13 files |
| Phase 05 P07 | 40min | 2 tasks | 15 files |
| Phase 05 P08 | 30min | 2 tasks | 13 files |
| Phase 05 P09 | 25 min | 1 tasks | 12 files |
| Phase 05 P10 | 30 min | 2 tasks | 12 files |
| Phase 05 P11 | 45min | 2 tasks | 8 files |
| Phase 05 P12 | 100 min | 3 tasks | 16 files |
| Phase 05 P13 | 60min | 1 tasks | 13 files |
| Phase 05 P14 | ~55 min | 3 tasks | 10 files |
| Phase 05 P15 | 35 min | 2 tasks | 18 files |
| Phase 05 P16 | 40 min | 2 tasks | 22 files |
| Phase 06 P01 | 60min | 3 tasks | 14 files |
| Phase 06 P02 | 25min | 2 tasks | 2 files |
| Phase 06 P03 | 75min | 2 tasks | 16 files |
| Phase 06 P04 | 70min | 2 tasks | 3 files |
| Phase 06 P05 | 35min | 2 tasks | 2 files |
| Phase 06 P06 | 30min | 2 tasks | 2 files |
| Phase 06 P07 | 55min | 3 tasks | 15 files |
| Phase 06 P08 | 190min | 3 tasks | 9 files |
| Phase 06 P09 | 7h | 4 tasks | 6 files |
| Phase 06 P10 | 5h | 3 tasks | 75 files |
| Phase 07 P01 | 25min | 3 tasks | 30 files |
| Phase 07 P02 | 50 min | 3 tasks | 12 files |
| Phase 07 P03 | 45min | 3 tasks | 9 files |
| Phase 07 P04 | 45min | 3 tasks | 12 files |
| Phase 07 P05 | 25 min | 2 tasks | 1 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Rule *definitions* before templates (Phase 2 before 4/5); *numeric values* after the generator exists (Phase 6)
- [Roadmap]: Overspend gate built in Phase 2 with provisional X; final X calibrated in Phase 6 (trim-back criterion)
- [Init]: uv + `pyproject.toml` + `uv.lock` (FOUND-01); LaTeX kept over Typst; Excel attack calculator retired
- [Init]: Downgrade allowed (no init refund, OPEX drops next wave); RoS counts own spend only, event effects out both ways
- [Init]: Measure cards show CIA/costs/dependencies only; wave weights and bonus links revealed on attack worksheets
- [Phase 01-01]: uv_build range >=0.12,<0.13; python-preference only-managed; openpyxl/python-pptx runtime deps for legacy generators only
- [Phase 01]: Config umlaut fix via byte-level targeted replacement (CRLF kept); json.dumps ensure_ascii default kept for legacy results
- [Phase 01]: 01-03: wave-3 tie golden cases deduplicated per (wave, bonus, E-value); check_golden uses strict type-aware equality so representation-only changes are reported
- [Phase 01]: 01-04: over-budget plans are evaluated and flagged (not skipped) in balance report; legacy run_simulation filters via rules.over_budget and drops over_budget/ros keys, output byte-identical
- [Phase 01]: 01-04: dead selection_to_key removed; single-definition AST guard in tests/test_single_definition.py (generate_*.py excluded, D-29)
- [Phase 01]: Validator detects dependency cycles on the measure graph (any-level edges); config.check_config lazily imports validate to avoid a rules/config cycle
- [Phase 01]: 01-06: rounding rule (half away from zero, once per wave, then clamp 0..100) and float-to-exact snapshot change approved by the user; committed as one explicit commit 0d342f6
- [Phase 01]: 01-07: over-budget has one definition (rules.budget_ledger) shared by evaluate_plan and the memoized TierKernel; store is 16 B per combination, RoS derived exactly on access; --budget-max quirk pinned, not fixed
- [Phase 02]: RULE-08/D-19: per-wave E-target bonus/malus removed from the simulation (not printed on MHP material); D-20 reviewed snapshot change
- [Phase 02]: RULE-06/D-21: RoS divides by own security spend only; total_cost keeps budget meaning (digest-stable); plan arithmetic 250+100+20=370 corrected
- [Phase 02]: RULE-03/D-15: over-budget plans lose X KZ per started 10.000 EUR (provisional X=9, step 10 kEUR, config overspend_penalty), measured once at the end (D-14); kz_pre_review and remaining stored for the RULE-04 gate; no validator warning for large X
- [Phase 02]: RULE-07/D-16: Budget Review tiers inclusive (ab), first minimum 0, card text generated via review_text.boundary_text; _tier_lookup raises below domain (WR-07); closes CR-01
- [Phase 02-05]: Kurswechsel is one forced Massnahmentausch (D-09..D-13, D-22, D-23, D-28); static enumeration is the reference plan without change-window moves (D-24); goldens changed text-only
- [Phase 02]: 02-06 RULE-02: evaluate_path models Levelwechsel up/down, cancel and add with net Init pricing per measure (D-27), no refund, no fee, effects and OPEX from the next wave, dependencies valid after every window
- [Phase 02]: 02-06 D-24: the swap layer (every valid wave-1 plan x every legal Kurswechsel swap with minimal repair; exempt plans static) is the legal minimum and is labelled; 37,300,736 swap paths per tier, about 4 min and 62 MB per tier; low-tier legal best in budget KZ 100 vs static reference 98
- [Phase 02]: [02-07] RULE-05/D-14: event-induced overruns need no rules change (single end check); Sparprogramm description carries the end-check sentence, characterization goldens regenerated text-only (user decision, option 1); budget cut in last wave warns via rules.event_without_window
- [Phase 02-08]: RULE-04 gate measured strict min X 9/5/3 (weak 8/4/3) on static reference; config X=9 passes, zero headroom in low; Phase 6 softens step rewards (D-18); move-path gate deferred (D-25)
- [Phase 03]: Phase 3 (03-01): prose lives in content/texte.toml; config holds numbers, ids and short labels; prose in config is a validator error (schema.prose_in_config)
- [Phase 03]: Phase 3 (03-01): digit allowlist pinned at seven reviewed entries; golden rewrite proven text-only by classifier
- [Phase 03]: 03-03: Audit-Mail wording 'insb. Datenverlust, Supply-Chain-Angriffe' replaces 'Erpressung' to avoid stacked Erpress* pointers at Wave 1; clue matrix has 14 clues
- [Phase 04-02]: D-05: CIA table gets one blank row per measure (10 today); cap printed as its own number (Kappung) via reduction_cap; rounding token ,5 allowlisted (eight entries)
- [Phase 04-01]: kpsewhich always runs with --miktex-disable-installer and lualatex with --disable-installer, stdin closed, timeout with process-tree kill
- [Phase 04-01]: PDF byte identity comes from planspiel.sty (suppressoptionalinfo 1023) plus an aux-stable pass loop; Arial set by name, never by Path=
- [Phase 04-03]: tex_escape raises UndefinedError for StrictUndefined; render failures report as ERROR print.render
- [Phase 04-04]: worksheet replay is an independent encoding reading only AttackSheet exact fields; equivalence proven on 36,467 grid comparisons and all 782,336 plans per tier, with negative controls
- [Phase 04-05]: version stamp = UTC date of last data-input commit + 7 hex of content hash over rendered .tex and planspiel.sty; +lokal only for build inputs; planspiel print --check compares manifest, rendered content and PDF SHA-256 without TeX
- [Phase 04]: 04-06: result line at the end of the worksheet after the wave-KZ step; layout page 1 = steps 1-4, page 2 from the Fall step, only spacing fallback (a) needed
- [Phase 05]: 05-01: PDF-layer veil scan squashes whitespace and hyphens on both sides so line-end hyphenation cannot hide a leaked name
- [Phase 05]: 05-01: Job-name prefix (spieler-, uebung-, angriff-, spielleitung-) is the single audience classification; render_all raises for unclassified jobs
- [Phase 05]: 05-02: CardDeck carries CardLabels so the 13-field MeasureCard stays pinned; legend formula is the last legend line (a digit after wA trips the weight-symbol veil rule); cardsheet starts a new page except for the first so LastPage equals the sheet count — see 05-02-SUMMARY.md key-decisions
- [Phase 05-03]: Card layout: A6 landscape (148.5x105 mm), 2x2 on A4 landscape; body 12/14.5 pt, technical line 10/12 pt, title 17/20 pt bold, text columns 82/48 mm; the 05-05 event deck reuses this layout — Approved by the user in print-test round 5 (Freigeben)
- [Phase 05-03]: Init-Kosten, OPEX and Voraussetzung use factbox (caption band directly above its value); padding captop 1.6, capbot 0.8, valtop 1.3, valbot 0.6, plaintop 1.4, plainbot 1, plainside 2, techgap 1.6 mm, headsep 1.8 mm, badge sep 3 pt — Round 2 and 3 user feedback: label must belong visibly to its value, text must not touch box edges
- [Phase 05-03]: One-line title guard: cardheader logs PLANSPIEL-CARDTITLE width/avail and a pdf test asserts width <= avail for all 31 headers (longest M10 116.2 of 121.8 mm); every card_header user, incl. the 05-05 event deck, is covered — 17 pt title chosen by the user in round 4; a wrapped title would break the bar
- [Phase 05]: Measure deck keeps the names-only veil profile; reveal note in legend, formula stays last line — VEIL-04: weights and bonus links appear only on revealed worksheets; D-24 keeps Phishing on M6
- [Phase 05-05]: Operative Unterstuetzung rule text aligned to the rule (user: Text an Regel anpassen); rules and simulation unchanged — The text said every existing measure in the coming round, evaluate_event counts measures active in the event's own wave; user decided 2026-10-26
- [Phase 05-05]: Event cards carry no caption band over the effect box; Budget Review keeps its caption — Kurswechsel card overflowed its cell by 15 pt with a caption (274 vs 259 pt); band dropped, no type reduced, 98% fill; check in the print test
- [Phase 05-05]: Event deck: eventtext.effect_rows generates every effect line; each row proven equal to rules.evaluate_event / budget_review_delta; kinds window, external_opex, external_budget, kz, review — PRINT-06; plans 05-07 and 05-15 consume the kinds; cardheader takes badge material plus a kicker argument
- [Phase 05]: Team booklet RoS part is two pages: RoS page and a separate Budget Review page — One page needed about 258 mm of the 257 mm text height at readable type; the overspend table is two side-by-side tables guarded by MAX_PENALTY_ROWS = 12
- [Phase 05]: Booklet fill reports use thepage; remaining budget printed as the budget_ledger ledger with event values entered with the card sign — 05-07 can insert the tracking page without renumbering; the OPEX relief stays inside the cost sum so no double negative is needed
- [Phase 05-07]: Both change windows share one measure grid (Level nach dem Fenster and Δ Init per window); credit cell shaded outside the Kurswechsel window — Stacked per-window grids needed about 186 mm and did not fit one A4 page
- [Phase 05-07]: Tracking rows are 6 mm instead of 7 mm; MAX_WINDOWS = 2 guards the layout proof (about 2 mm spare) — The one-page proof needs 6 mm rows; a third window or a fourth wave needs a new proof
- [Phase 05]: Wave explainer prints the recovery factor as a percentage like the worksheet — One spelling of r on worksheet and explainer; steps unnumbered because worksheet numbering shifts without recovery
- [Phase 05-09]: Asset names are code constants (texbuild.ASSET_FILES); content_hash gains an optional assets mapping; mini content carries 1x1 PNG fixtures — Images stay inside the hashed, read-guarded set (D-19); the pure hash keeps its static_files shape; CLI tests need a valid content dir without 3.6 MB images
- [Phase 05]: Story documents: images pass tex_escape only as render.AssetName (fixed ASSET_FILES names); story walker is strict (unknown keys, wrong types, nesting beyond one level, caption/image count mismatch stop the build) — An escaped underscore breaks the includegraphics lookup, and a lenient walker would drop story text silently
- [Phase 05]: Practice example pinned to the illustrated Welle 0 parameter set; check_example requires an exact half before rounding — The exact half (5/2) makes half away from zero (+3) visibly differ from half to even (+2); all guards held on the first parameter set, so no search was needed
- [Phase 05]: Practice block is a top-level config key read only by planspiel/practice.py — Full Config equality with and without the block, equal evaluate_plan/TierKernel results and an unchanged overspend gate prove the real machinery cannot see it
- [Phase 05]: Welle 0 practice story approved by the user with neutral case texts (D-16) — User answered 'Freigeben + Fälle neutral'; the case texts avoid the Ihr/Eure voice to match the Beispielteam framing
- [Phase 05]: Welle 0 bonus marks: cross for met, dash for missed; damage before recovery printed without euro sign in the short box — Arial has no tick glyph and an empty box reads as unfilled; 20.000 euro does not fit the 13 mm box
- [Phase 05]: Final-index weights live in simulation_config.json (final_index block), no defaults in rules.final_index — D-23: one source for reports and PRINT-10 answer keys; outputs unchanged at 1 and 1
- [Phase 05]: Reference paths pinned: Low 2, Medium 1H, High 3 (user-approved, re-choose after Phase 6) — Legal paths from rules.path_trace near the swap-layer median (60/62/62); Config.reference_plans sits before practice
- [Phase 05]: Facilitator master sheet prints non-terminating values (17/7 slope, wave-3 attack KZ, RoS, final index) with format_approx on the facilitator booklet only — D-26 Q6: players never see an approximation; a PDF test proves the approximation sign appears in no other PDF
- [Phase 05]: Each wave of the facilitator booklet is two pages: parameters, bonus and check rows, then event schedule and answer keys; the GR step table is transposed — Wave 2 with its schedule and a 9-row table overflowed one page; the per-page fill report now proves every page fits
- [Phase 05]: content/clues.toml is a stamped print input checked at print time (ERROR print.clues) and passed to every builder as the fourth argument — Research F15: a clues change must move the stamp date and mark the tree dirty; the quotes must match the pre-wave texts verbatim
- [Phase 05-16]: Clue matrix section labels for headingless mail sections come from digit-free sheets.spielleitung keys, raw key only as last fallback — Keeps story texts, veil scan and player documents untouched; guarded by a test over real and mini content
- [Phase 05-16]: The committed print set is written only by the last plan of a phase in the D-19 order — Stamp and manifest do not churn per plan; --check and a byte-identical rebuild prove freshness
- [Phase 05 UAT]: All eight human print checks passed 2026-10-27, so the open layout calls stand as is: event effect-box padding, 43 % empty RoS page, 1.3–1.5 mm tracking clearance, 9 pt explainer text, damage before recovery without euro sign
- [Phase 06-01]: Path gate trim is start-lowered (lower/cancel START levels, then any legal continuation of the family pool); narrow same-swap-pair is a diagnostic only. Measured X: static 9/5/3, swap 9/5/2, window-1 9/5/3, window-2 5/2/1, narrow 14/7/5; recommended X = 10 (low, static); raw/capped reading A1 and the definition are confirmed at D-04
- [Phase 06-01]: Candidate checks use xfail TUNING_TARGET plus --runxfail with --planspiel-config/--planspiel-content-dir; gate --paths --jobs 3 takes about 10 min, with --narrow about 19 min
- [Phase 06-02]: hand_calc_level default stays warning until 06-10 flips it with the adopted config; exfil fix option kz -5..9 at cap 7 is hand-friendly
- [Phase 06-03]: Final-Index = weight_kz*KZ + weight_ros*RoS2 (two-decimal RoS); today's pooled IQR KZ 18 / RoS 0.43 gives k_raw 20.8, recommended k = 20 (KZ share 0.68); moved golden row final.final_index tracked by strict xfail until the 06-10 re-pin
- [Phase 06-04]: Near-mandatory band is the 5-KZ band widened to the 200 best in-budget plans (200 in every tier today). Today near-mandatory: M7 all tiers, M2 medium/high, M1/M4/M5 also in high; overpowered: M7 (drop 14/16/18), M2 in high (11); dominance, swing, tier optima, Kurswechsel and window move pass. Thresholds go to D-04 for re-approval.
- [Phase 06]: BAL-08 thresholds (median margin 5, comeback drop 5 / gain 10 / share 0.9) are proposals for D-04; low-tier comeback share 0.915 has only 1.5 pp headroom
- [Phase 06-06]: BAL-09 spread thresholds (corridor 6, best 90..98, IQR 13..21, IQR diff 4, p5-p95 50, median-start 28) are module constants in planspiel/spread.py for D-04 re-approval; D-11 band and median bound are TUNING_TARGET today
- [Phase 06-07]: Clue score = sum of clue weights, importance = bonus x KZ slope, graduation I(a)>I(b) => S(a)>=S(b), floors 2 and 4; placement on both populations (static Final-Index, swap-layer KZ); proposals for D-04
- [Phase 06-07]: Today's clue-derived good start is top quartile only in low (FI 77 / swap-layer KZ 81); medium 58/64 and high 62/69 miss it; all-in-C is top quartile everywhere; require_mapping stays False until 06-10
- [Phase 06]: [06-08] Balance report: static layer skips swap-dependent blocks (choices, strategies, rewarding) and labels them not computed; input errors exit 2, verdict 0/1; baseline report built with the candidate's Final-Index weights
- [Phase 06-09]: D-04 approved 2026-11-01 (verbatim: Freigeben): start-lowered trim, X = 3, k = 10, thresholds unchanged, candidate config/content adopted in 06-10
- [Phase 06-10]: D-04-approved candidate adopted byte for byte; hand-calc findings are errors and the clue mapping is required by default; Final-Index printed as KZ + k x RoS2 (k = 10) without provisional label; Budget Review page proven for 34 penalty rows — Phase 6 adoption
- [Phase 07]: Phase 7 plan 02: schedule product rules (190 min, D-02 order, 3 teams of 5) live in tests, the validator guards structure and sum only
- [Phase 07]: Phase 7 plan 02: print list on its own booklet page after the schedule page; Config.session_schedule sits before reference_plans (practice stays last)
- [Phase 07-03]: ValueChange uses tuple-valued fields; three meaning-changed entries (Exzellenz level, Budget Review boundary and overspend rule); was_neu.py is the only operand reader allowed by the single-definition guard
- [Phase 07-04]: Debrief guide minutes reaction 3, description 4, analysis 8, application 5; sum equals the debrief block (schedule.debrief_sum)

### Pending Todos

None. The veiling todo (2026-06-23) is closed (moved to `todos/completed/` in Phase 5).

### Blockers/Concerns

- [Phase 6]: Resolved direction (D-18): soften step rewards (Exzellenz, OEM-Audit tiers, M7 tiers) in Phase 6; no overspend cap, no voiding of bonuses. Phase-2 gate (plan 02-08) measured strict X 9 / 5 / 3 (weak 8 / 4 / 3); low tier 9 > ~5 is the Phase-6 input; research M2: partial softening reaches low 6, flattening all step rewards 4 / 2 / 1. Config X = 9 is provisional (D-25) and equals the strict low-tier minimum (no margin there); the slow gate over move paths (swap/window families) is deferred to Phase 6 (D-25).
- [Phase 7]: the retired `generate_attack_calculator.py` raises KeyError on `kz_bonus`/`kz_malus` since plan 02-01 (D-29: untouched until LEG-01); `docs/folienkonzept_spielphasen_mechtech.md` still mentions the E-Ziel-Check (LEG-02).
- [Phase 4]: MiKTeX AutoInstall=ask hangs scripted builds; the first Phase 4 plan must be a non-interactive smoke build.
- [Phase 1]: Interpreter trap until FOUND-01 lands (`python` on PATH is Inkscape's 3.12 without packages); full enumeration JSONs are >100 MB, so never read them whole.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-11-03T19:03:28.922Z
Stopped at: Phase 7 context gathered
Resume file: .planning/phases/07-session-flow-handoff/07-CONTEXT.md
