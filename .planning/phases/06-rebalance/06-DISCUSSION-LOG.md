# Phase 6: Rebalance - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-28
**Phase:** 06-rebalance
**Areas discussed:** Stellschrauben, Messbasis & Schwellen, Überziehungs-X, Final-Index, Hinweise → Maßnahmen (raised by the user)

---

## Stellschrauben

| Question | Options | Selected |
|----------|---------|----------|
| Scope of change | Values + event tiers / Values only / Also structure | Values + event tiers ✓ |
| Taboo values | Budgets / Start KZ / Wave weights / Nothing taboo | Nothing taboo ✓ |
| Hand-friendly | Max. one decimal / Integers only / Any terminating decimal | Max. one decimal ✓ |
| Approval | One review checkpoint / Checkpoint per lever / Variants to choose from | One review checkpoint ✓ |

## Messbasis & Schwellen

| Question | Options | Selected |
|----------|---------|----------|
| Plan set for BAL checks | Both layers / Legal paths only / Static only | Both layers ✓ |
| Reference strategies | Claude proposes, user approves / User defines / Rule-based | Claude proposes ✓ |
| Tier comparability | Final KZ comparable / Gain comparable / Tiers may differ | Final KZ comparable ✓ |
| Principle priority | Order 1→4 / Rewarding first / Present conflicts | Order 1→4 ✓ |
| Quartile population | In-budget only / All plans / Near-budget plans | In-budget only ✓ |
| "Mediocre ends positive" | Median > start / P25 > start / Reference mediocre plan | Median > start ✓ |
| KZ 100 reachable | Slightly below 100 / 100 reachable / Don't care | Slightly below 100 ✓ |

## Überziehungs-X

| Question | Options | Selected |
|----------|---------|----------|
| Global or per tier | One global X / X per tier | One global X ✓ |
| Margin | +1 KZ / Exactly minimum / Round number | +1 KZ ✓ |
| Move-path gate | Yes, as slow test / Static only | Yes ✓ |
| Fallback if X > ~5 | Present with numbers / Accept higher X / Soften further | Present with numbers ✓ (after Claude explained what X is) |

**Notes:** The user asked "was ist das X?". Claude explained the overspend penalty per started 10.000 €, the trim-back gate with the Phase 2 low-tier witness plan (82 vs 83 at X = 9), and why step rewards drive the required X.

## Final-Index

| Question | Options | Selected |
|----------|---------|----------|
| Purpose | Winner in the debrief / Balance tool only / Teams compute it | Winner in the debrief ✓ |
| Weighting | KZ leads, RoS corrects / Equal / RoS leads | KZ leads ✓ |
| Form | KZ + k·RoS, k integer / Free weights / Rank-based | KZ + k·RoS ✓ |

## Hinweise → Maßnahmen (raised by the user)

**User's concern:** Players must be able to choose the right measures from the clues, without too many clues, and no measure may be overpowered.

**Claude's status check:** Clue → attack is verified (≥2 clues per attack, Phase 3). Clue → measure is not verified, and there is no upper bound on clues. Overpowered is BAL-06.

| Question | Options | User's answer |
|----------|---------|---------------|
| Clue → measure chain | Check + reward / Measure reward only / Manual review | Free text: clues not too unambiguous, measures never named; teams should work it out from the description texts. Learning goal: risk-based protection, i.e. analyse the company, then choose measures |
| Clue dosage | Keep clues, measure effect / Cap per attack / Defuse clues | Free text: a plenum discussion of CIA weighting and risks is an option (or collect without comment, or not discuss at all); number and importance of clues should be graduated by measure importance |
| Overpowered thresholds | Claude proposes / User sets | Claude proposes ✓ |
| Mismatch: clue weight vs importance | Config first / Story follows config / Measure only | Free text: either story or config may change; story is probably easier; in the end everything must fit together |
| Measure mapping in the clue matrix | Yes, facilitator only / No | Yes ✓ |

## Claude's Discretion

- Calibration method and search strategy over config values
- Exact BAL-06…09 thresholds (corridor width, spread measure, overpowered criteria), proposed with data at the review checkpoint
- Clue weight scale and graduation rule
- Report presentation (BAL-04); `MAX_PENALTY_ROWS` / RoS-page re-proof depending on final X

## Deferred Ideas

- Plenum analysis step (discuss and steer / collect uncommented / no discussion) → Phase 7 (FLOW-02/03)
