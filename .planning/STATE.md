---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 2
current_phase_name: Rule Changes
status: executing
stopped_at: Phase 2 context gathered
last_updated: "2026-10-02T12:42:57.513Z"
last_activity: 2026-10-02
last_activity_desc: Phase 2 execution started
progress:
  total_phases: 7
  completed_phases: 1
  total_plans: 15
  completed_plans: 7
  percent: 14
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-29)

**Core value:** Facilitators and players can run the game by hand without ambiguity: every rule is unambiguous, every printed number matches `simulation_config.json`, and no strategy exploits a rule loophole.
**Current focus:** Phase 2 — Rule Changes

## Current Position

Phase: 2 (Rule Changes) — EXECUTING
Plan: 1 of 8
Status: Executing Phase 2
Last activity: 2026-10-02 — Phase 2 execution started

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**

- Total plans completed: 7
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 7 | - | - |

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

### Pending Todos

1 pending: `.planning/todos/pending/2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md` (veil attacks/events). Covered by Phase 3 (VEIL-01, VEIL-03) and Phase 5 (VEIL-02, VEIL-04); close it when Phase 5 completes.

### Blockers/Concerns

- [Phase 2/6]: Step rewards (OEM-Audit tiers, M7 tiers, Exzellenz +5/L3, E-target bonus) can make going ~8k over budget worth up to +34 KZ, so the trim-back X may be impractical. If Phase 2's gate reports X > ~5, decide on capping overspend or softening step rewards in Phase 2, not Phase 6, because either choice changes printed rules.
- [Phase 7]: the retired `generate_attack_calculator.py` raises KeyError on `kz_bonus`/`kz_malus` since plan 02-01 (D-29: untouched until LEG-01); `docs/folienkonzept_spielphasen_mechtech.md` still mentions the E-Ziel-Check (LEG-02).
- [Phase 4]: MiKTeX AutoInstall=ask hangs scripted builds; the first Phase 4 plan must be a non-interactive smoke build.
- [Phase 1]: Interpreter trap until FOUND-01 lands (`python` on PATH is Inkscape's 3.12 without packages); full enumeration JSONs are >100 MB, so never read them whole.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-10-01T09:19:27.453Z
Stopped at: Phase 2 context gathered
Resume file: .planning/phases/02-rule-changes/02-CONTEXT.md
