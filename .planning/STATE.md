---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 04
current_phase_name: Print Pipeline & Attack Worksheets
status: executing
stopped_at: Completed 04-05-PLAN.md
last_updated: "2026-10-22T15:08:50.226Z"
last_activity: 2026-10-20
last_activity_desc: Phase 04 execution started
progress:
  total_phases: 7
  completed_phases: 3
  total_plans: 24
  completed_plans: 23
  percent: 43
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-29)

**Core value:** Facilitators and players can run the game by hand without ambiguity: every rule is unambiguous, every printed number matches `simulation_config.json`, and no strategy exploits a rule loophole.
**Current focus:** Phase 04 — Print Pipeline & Attack Worksheets

## Current Position

Phase: 04 (Print Pipeline & Attack Worksheets) — EXECUTING
Plan: 6 of 6 (04-01 to 04-05 complete; next 04-06)
Status: Ready to execute
Last activity: 2026-10-20 — Phase 04 execution started

Progress: [██████████] 96%

## Performance Metrics

**Velocity:**

- Total plans completed: 18
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 7 | - | - |
| 2 | 8 | - | - |
| 03 | 3 | - | - |

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

### Pending Todos

1 pending: `.planning/todos/pending/2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md` (veil attacks/events). Covered by Phase 3 (VEIL-01, VEIL-03) and Phase 5 (VEIL-02, VEIL-04); close it when Phase 5 completes.

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

Last session: 2026-10-22T15:08:42.917Z
Stopped at: Completed 04-05-PLAN.md
Resume file: None
