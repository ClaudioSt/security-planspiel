# Phase 1: Simulation Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-29
**Phase:** 01-simulation-foundation
**Areas discussed:** Paper rounding rule, Characterization baseline, Enumeration report, Refactor scope & cleanup

---

## Paper rounding rule

| Option | Description | Selected |
|--------|-------------|----------|
| KZ-Delta per wave | Round each wave's KZ-Delta to whole number; E/Gesamtreduktion/damage stay exact | ✓ |
| Only final KZ | Carry decimals across waves, round once at the end | |
| No rounding by design | Validator enforces clean slopes; helper only for 10k steps | |

| Option | Description | Selected |
|--------|-------------|----------|
| Kaufmännisch, symmetric | Half away from zero (+2,5→+3, −2,5→−3) | ✓ |
| Always up (toward +∞) | −2,5 → −2 | |
| Truncate | Drop decimals | |

| Option | Description | Selected |
|--------|-------------|----------|
| Keep exact whole € | Damage always ends in whole euros | ✓ |
| Round to full 1.000 € | Second rounding point | |
| You decide | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 1, as reviewed snapshot change | Pin raw → no-diff refactor → exact+rounding commit with reviewed diff | ✓ |
| Helper now, switch on in Phase 2 | Rounding goes live with rule changes | |

**User's choice:** all recommended options.

---

## Characterization baseline

| Option | Description | Selected |
|--------|-------------|----------|
| Readable golden set + full digest | ~30–50 selections/tier readable + hash over all combos (slow test) | ✓ |
| Golden set only | Fast, may miss rare combos | |
| Full per-combination snapshot | Huge, unreadable diffs | |

| Option | Description | Selected |
|--------|-------------|----------|
| Pin over-budget at simulate_selection level | Incl. Budget Review −15 behaviour | ✓ |
| Pin only current run_simulation output | Over-budget has no baseline | |

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit regen flag + diff summary | `pytest --update-golden`, domain diff printout | ✓ |
| syrupy / snapshot library | Standard plugin | |
| You decide | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Opt-in slow marker | Default pytest fast | ✓ |
| Always run | Minutes per run | |

---

## Enumeration report

| Option | Description | Selected |
|--------|-------------|----------|
| Several views, KZ first | Top-K by KZ, RoS, Final-Index; in vs over budget on KZ | ✓ |
| Final-Index only | | |
| Final KZ only | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Final KZ vs total own cost | Feeds overspend gate / trim-back | ✓ |
| Final KZ vs RoS | | |
| Both fronts | | |

| Option | Description | Selected |
|--------|-------------|----------|
| JSON summary + console table | Full JSONL dump only on request | ✓ |
| Also Markdown report | Committed report per tier | |
| Console only | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Keep old CLI working, dump stays explicit | `--output` = explicit full dump | ✓ |
| Replace with new subcommand | Deprecation hint | |

| Option | Description | Selected |
|--------|-------------|----------|
| Compact in-memory tuples | Reusable by Phase 6 sweeps | ✓ |
| True one-pass streaming | Heaps, streaming quantiles | |

**Notes:** When asked about the old CLI, the user first asked whether to wait for the RAM upgrade they're getting that afternoon. Claude said there was no need to wait, since this is design only. It proposed in-memory tuples instead of one-pass streaming, given the extra RAM, and the user accepted.

---

## Refactor scope & cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Leave old generators untouched | No formulas; archived Phase 7 | ✓ |
| Port onto planspiel/ loaders | Throwaway work | |

| Option | Description | Selected |
|--------|-------------|----------|
| Display strings only; ids stay ASCII | Plus transliteration test | ✓ |
| Also rename ids | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Validator inside load + standalone CLI | Broken refs = errors; hand-calc = warnings | ✓ |
| Standalone CLI + test only | | |

**Notes:** The repo hygiene items from CONCERNS.md (sim JSONs, `__pycache__`) turned out to be already untracked, so there's no git cleanup to do.

## Claude's Discretion

- Python version, dependency pins, `planspiel/` layout
- Golden-set list, seed, digest format, K
- Fraction vs integer scaling
- Validator CLI naming and output

## Deferred Ideas

- 0.85 filter removal and Final-Index rescale → Phase 6
- Validator warnings → errors → Phase 6
- Ledger/Budget Review redefinition → Phase 2
