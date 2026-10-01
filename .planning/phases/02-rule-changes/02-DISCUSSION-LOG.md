# Phase 2: Rule Changes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-01
**Phase:** 02-rule-changes
**Areas discussed:** Change-window moves, Overspend penalty, E-target bonus/malus, Budget Review boundary

Pre-discussion scan of printed MHP material (final_documents): no E-target anywhere; Kurswechsel slide refunds cheaper swaps ("gezahlt oder erstattet"); README mentions a change fee absent from config; Budget Review print says 25.001 while sim uses ≥ 25.000.

---

## Change-window moves

| Option | Description | Selected |
|--------|-------------|----------|
| Level up/down + add new | Levelwechsel both ways and adding; no free swap | |
| Everything incl. free swaps | As README today | |
| Upgrades + add only | No downgrade | |

**User's choice (free text):** Level up and down or cancel (lower OPEX, no refund of initial cost), add new.

| Option | Description | Selected |
|--------|-------------|----------|
| Init difference | Pay Init(new) − Init(old) | ✓ |
| Full Init of new level | Pay full Init again | |

| Option | Description | Selected |
|--------|-------------|----------|
| No fee | Drop the README Change-Gebühr | ✓ |
| Fee per move | Flat config value per move | |

| Option | Description | Selected |
|--------|-------------|----------|
| Tausch, pay difference, no refund | | |
| Tausch, difference both ways | As printed at MHP | |
| Tausch or Levelwechsel | | |

**User's choice (free text):** It's an event — the customer refunds the initial cost, so one measure must be changed at no additional cost; can be good or bad; it's about strategic thinking.

**Follow-up — incoming level:** options Same level / Any level / Any level up to outgoing. **User:** any level; customer only pays up to the dropped measure's Init, so if the new Init is more expensive the team pays the delta.

| Option | Description | Selected |
|--------|-------------|----------|
| Unlimited, budget is the limit | | ✓ |
| Max 1 move per window | | |
| Max 2 moves per window | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Next wave, costs immediately | | ✓ |
| Immediately | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Not allowed — must stay valid | | ✓ |
| Allowed, dependent level loses effect | | |

**Confirmation:** Kurswechsel cost = max(0, Init(new) − Init(old)), paid delta is own spend in RoS, swap in the window after wave 1. **User:** yes exactly — only the forced Kurswechsel credits the dropped measure's Init; otherwise Init is never refunded.

---

## Overspend penalty

| Option | Description | Selected |
|--------|-------------|----------|
| Once, at the end | Final remaining budget | ✓ |
| After every wave | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Replaces the flat −15 | Positive leftover tiers stay | ✓ |
| Replaces the whole card | No leftover bonus | |

| Option | Description | Selected |
|--------|-------------|----------|
| Step rewards void when over budget | | |
| Hard cap on overspend | | |
| Soften step rewards | Value change in Phase 6 | ✓ |
| Accept a large X | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Best plan by lowering levels only | | |
| Any in-budget plan of the tier | | |
| You decide | Research defines and justifies | ✓ |

---

## E-target bonus/malus

| Option | Description | Selected |
|--------|-------------|----------|
| Remove from sim | Matches MHP play; removes a step reward | ✓ |
| Print it | Extra worksheet line | |
| Replace by something simpler | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Reviewed diff like Phase 1 | Checkpoint with all-combination diff | ✓ |
| Just commit it | | |

---

## Budget Review boundary

| Option | Description | Selected |
|--------|-------------|----------|
| ≥ 25.000 → +5 | Keep sim semantics; generate card text from tier list | ✓ |
| Print wins: 25.001 → +5 | Change sim to strict > | |

---

## Claude's Discretion

- Definition of the trimmed in-budget version for the trim-back gate (research to define and justify).
- Bounded change-path enumeration model, config schema, validator rules, single term Maßnahmentausch vs Maßnahmenwechsel.

## Deferred Ideas

- Step-reward softening and final X → Phase 6.
- Printing cards/tables → Phases 4/5.
- Remaining Phase 1 review warnings → optional `/gsd-code-review 1 --fix`.
- Veiling todo stays in Phase 3/5 (user confirmed).
