# Feature Research

**Domain:** Facilitated, paper-based IT-security serious game / cyber tabletop exercise for student teams (3 teams x 5, one ~3h afternoon, deterministic, hand-calculated)
**Researched:** 2026-09-29
**Confidence:** MEDIUM overall. Patterns come from primary game documents I read in full: the Decisions & Disruptions rulebook and GM cheat sheet, the Backdoors & Breaches visual guide v2, the Control-Alt-Hack CCS'13 evaluation, the *Threats & Trade-offs* 2025 paper and the TOPSIM participant handbook. Debriefing and exercise-doctrine claims (Crookall, Impulse-Debriefing-Spiral, NIST SP 800-84, CISA CTEP, ENISA) come from search summaries and abstracts, not full texts, so they are MEDIUM/LOW.

**Scope note:** This file does not redesign the game. It shows how comparable games solve the six MHP feedback points and the timing overrun. Each finding is mapped onto the existing mechanics (E-value, 3-case resolution, KZ, RoS, change window, events) and the Active requirements in `PROJECT.md`.

---

## How the reference games solve the seven questions

| Question | Decisions & Disruptions 1 (Lancaster/Bristol) | Backdoors & Breaches (BHIS) | Threats & Trade-offs (2025) / TOPSIM / CyberCIEGE / KIPS | Exercise doctrine (NIST 800-84, CISA CTEP, ENISA) |
|---|---|---|---|---|
| **(a) Teaching mechanics fast** | GM reads a scripted intro, walks the board, then presents every defence card one by one while reading its text aloud. The FAQ is scripted, including in-character answers. Players are told not to read the rulebook. Turn 1 is slower and "players take their decisions much more quickly after the first turn". | The visual guide has an annotated **"Reading the Cards"** anatomy (title / description / what detects it / tools / resources), a 4-step **Sequence of Play**, and a full-page **worked example game**. | TOPSIM uses an **ungraded trial period (Probeperiode)** before the graded periods. Control-Alt-Hack: the top educator critique was "takes a long time to learn" (4/14). The fixes were a 10-min rules video and **pre-briefed people who seed each group**. | The Situation Manual (SitMan) is a participant handout with scenario, agenda and objectives. The Facilitator/Evaluator Handbook is separate. |
| **(b) Budget / overspend** | Fixed 100k per round, **underspend carries over, no borrowing or debt** (hard cap). | n/a (no budget) | T&T: a negative budget forces an investor draw, otherwise a **loan with interest** tracked on a loan pad. TOPSIM: **automatic overdraft at penal interest (17%)**, repaid next period. The penalty is linear and always costs more than planning. CyberCIEGE: you cannot spend money you don't have. | n/a |
| **(c) Upgrade / downgrade** | Purchases are permanent. Cards are removed from the table and figures placed on the board. **No selling**. | Established vs other procedures; no purchasing. | T&T: **cannot sell or downgrade**. Defences need periodic renewal, and unbought defences get more expensive. | n/a |
| **(d) Threat reveal** | Intel is purchasable (Threat Assessment, Asset Audit). In round summaries the GM is told "**you don't need to read out the attack type**". **All attackers are revealed at the end of the game**. | The opening narrative must give "a place to start **without giving away the specifics** of any Attack card". Attack cards are revealed **one at a time** on detection, and the full chain at the end. | T&T: attack cards are drawn at round end. The GM describes the attack, and the consequences only if defences are missing. | Injects are scripted in a Master Scenario Events List (MSEL). |
| **(e) ROI scoring / external shocks** | Losses and penalties "**do not impact your budget the next year but represent your overall performance**". Budget and performance are **two separate ledgers**. Score = total losses. | Win/lose only. | T&T: the round sequence separates **external draws** (investor card, attack card) from **player decisions**. The KIPS score is company revenue/profit. ENISA ROSI = (ALE x mitigation ratio - cost of solution) / cost of solution. External cost shocks are not part of "cost of solution". | n/a |
| **(f) Paper state tracking** | GM keeps a **photocopied attack table** (hidden from players). Each round they circle countered stages and strike out finished attack lines, then focus only on open lines. | Cards face-up on the table *are* the state. | T&T: **physical counters on a printed track** (budget, satisfaction, customers) plus a **loan pad**. | A dedicated **scribe / data collector** role; decisions are logged in a template, not by the facilitator. |
| **(g) Debrief** | GM reveals all attackers, then compares against a **"perfect game" purchase sequence** round by round. | "If a procedure fails, ask *why* it would fail in reality." The game calls this "the most important part of the educational process". | T&T: recorded post-game discussion. | **Hot wash** straight after the exercise, then a participant feedback form, then the AAR. Crookall: debriefing *is* the core of a serious game (description, analysis, application). Impulse-Debriefing-Spiral: **short reflection impulses between rounds**, not only at the end. |

**Key takeaways for this game**

1. **D&D1 is the closest analog.** It is deterministic, budgeted, round-based, run by a GM and paper-trackable. It already uses three patterns the milestone needs:
   - separate budget and performance ledgers, which supports taking event costs out of RoS;
   - a GM master sheet you tick off each round, which replaces the whiteboard;
   - a "perfect game" debrief.
2. **Nobody in the reference set lets overspending pay off.** Either the budget is a hard cap (D&D, CyberCIEGE), or overspending costs a *linear penal rate* above its benefit (TOPSIM overdraft, T&T loans). The planned "-X KZ per started 10k" rule matches the TOPSIM pattern and is the simplest hand-calculable version of it.
3. **Nobody in the reference set allows refunds.** Downgrade or sell is either forbidden (T&T, D&D) or not modelled. "Sunk cost stays sunk" is the norm.
4. **Rules are always taught with three artifacts:** an annotated card anatomy, a one-page turn sequence, and a worked example. The classroom-tested fix for learning curve is a practice round (TOPSIM) or pre-briefed rule-seeders (Control-Alt-Hack), not a longer lecture.
5. **The MHP schedule had no debrief slot.** The timeline ends at "17:52 Attack 3 —". Every reference source treats the debrief as the core learning step, so this is the biggest gap that none of the Active requirements covers.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Missing any of these means players can't follow the game or facilitators calculate inconsistently. That is exactly what the MHP feedback shows.

| # | Feature | Why Expected | Complexity | Notes (for THIS game) |
|---|---------|--------------|------------|------------------------|
| T1 | **Annotated measure-card legend ("So liest du eine Maßnahmenkarte")** | B&B "Reading the Cards" is the reference pattern. Feedback #2 was "Wie funktionieren Maßnahmen → auf Zettel und Folie vermerken". | LOW | One printed legend (and matching slide) that labels every field on a card: Level L1/L2/L3, CIA contribution (c/i/a), Init cost, OPEX per wave, dependency ("L3 erfordert M2 ≥ L2"). Generated from the same LaTeX template as the cards so it never drifts. Do **not** print "counters attack X" on measure cards (see conflict C1). |
| T2 | **One-page "So funktioniert eine Welle" rule reference (player aid)** | The turn-sequence player aid is "by far the most useful player aid". D&D and B&B both put the round sequence on one page. | LOW | Sequence: Events → E-value (Team-CIA x weights) → + bonus → Gesamtreduktion → case 1/2/3 → damage, KZ-Delta → OPEX → change window. Show the formulas symbolically with the wave's numbers as blanks. One copy per team. This is the "how-it-works sheet" already listed in `PROJECT.md`. |
| T3 | **Worked example before the first scored wave ("Welle 0")** | TOPSIM ungraded trial period. Worked-example effect: for novices, studying a worked solution beats problem-solving, which is HIGH-confidence learning science. D&D notes that turn 1 is always the slow one. MHP: wave 1 took 34 min vs 20 planned, waves 2-3 fit once the procedure was known. | MEDIUM | Facilitator computes **one fictional example team** through a full wave on a slide and on the tracking sheet, in about 8-10 min. Use a fictional wave or wave 1 with a non-player measure set so no team's real outcome is spoiled. Fading: Welle 0 fully worked, Welle 1 teams compute while the facilitator narrates each step, Welle 2/3 teams compute alone. Numbers must come from `simulation_config.json` via the generator (the example is itself print material and falls under the print-sync trap). |
| T4 | **Printed per-team tracking sheet (Team-Laufzettel) replacing the whiteboard write-up** | T&T uses counters on a printed track; TTX doctrine uses scribe templates. The 15-min whiteboard write-up at MHP was a serial bottleneck: one board, three teams, facilitator transcribing. | MEDIUM | Pre-structured cells **in calculation order** (matching T2): measure list with level/CIA/Init/OPEX, then per wave: Team-C/I/A, E-value, bonus, Gesamtreduktion, case, severity, damage, KZ-Delta, budget remaining. Teams fill it in parallel. A carbon-copy or tear-off "order form" for the measure purchase can go to the facilitator instead of being copied to the whiteboard. Generated from config, since wave weights, thresholds and caps are pre-printed per wave. |
| T5 | **Facilitator master sheet (Moderations-Cheat-Sheet)** | D&D GM cheat sheet plus photocopied attack table. CISA CTEP facilitator handbook. Core Value: "facilitators … run the game by hand without ambiguity". | MEDIUM | Per wave: threshold, cap, bonus table, the three case formulas, event effects, and a per-team check row so the facilitator verifies team numbers instead of computing them. **Missing from the Active requirements.** The print list names attack worksheets, cards, budget/event cards and the tracking sheet, but not a current facilitator guide (the old ones are archived and out of sync). |
| T6 | **Unambiguous change-window vocabulary** | Feedback #3 "Maßnahmenwechsel ≠ Levelwechsel". Card games handle this with a glossary of fixed keywords used verbatim on every card and rule. | LOW | Define exactly two terms on T2 and use them verbatim in the Kurswechsel event text and config `description`: **Levelwechsel** (same measure, level changes) and **Maßnahmentausch** (one measure out, another in). The Kurswechsel event must name which one it forces. Upgrade cost = **difference of Init costs** (already the Kurswechsel wording, and the common board-game upgrade pattern). |
| T7 | **Decided, printed downgrade rule** | Feedback #4 "Level runterstufen sinnvoll?" shows players didn't know. T&T and D&D both forbid selling/downgrading, and no reference game refunds sunk cost. | LOW (rule) / MEDIUM (sim) | **Recommendation: no downgrade in the free change window** (Init stays sunk, OPEX keeps running). That matches the reference games, needs zero new enumeration paths, and makes a clean debrief point ("versunkene Kosten"). If the user wants downgrade anyway: no Init refund, OPEX drops from the next wave, and the full enumeration must model change paths (see Pitfalls). Either way, print the rule on T2. |
| T8 | **Linear, never-profitable overspend penalty** | TOPSIM overdraft and T&T loans are linear penal rates. D&D and CyberCIEGE use a hard cap. The current flat "<0 → KZ -15" makes heavy overspend profitable (feedback #5). | LOW (rule) / MEDIUM (calibration) | "-X KZ per started 10k over budget", matching the Key Decision. "Per started 10k" is a ceiling function, but it stays hand-calculable (count the started 10k blocks). X must be calibrated by full enumeration **including** over-budget combinations, which `simulate_outcomes.py:539` currently drops. Print a small lookup table (0-10k: -X, 10-20k: -2X, …) on the budget card so nobody computes the ceiling live. |
| T9 | **RoS measures only the team's own spend (separate external ledger)** | D&D keeps penalties apart from budget, the ENISA ROSI "cost of solution" is the defender's own investment, and T&T separates external draws from player decisions. Feedback #6: "Eventstrafen bei RoS rausnehmen". | LOW | Tracking sheet gets **two cost columns**: *eigene Kosten* (Init, OPEX, change costs, which go into RoS) and *externe Effekte* (event budget deltas, event OPEX penalties **and discounts**, which change available budget but not RoS). Symmetry for discounts (Operative Unterstützung, Sparprogramm) is still pending in `PROJECT.md`. Research supports **excluding both directions**, because a discount is just as much an external shock as a penalty. |
| T10 | **Veiled pre-wave material, explicit reveal at the wave** | D&D (no attack type in round summaries), B&B ("place to start without giving away specifics"). Decided 2026-09-29. | LOW-MEDIUM | Config needs a player-facing `display_name` / veiled teaser per attack and event, separate from the internal `name`. Pre-wave materials (Unternehmenssteckbrief, Zeitungsartikel, Audit-Mail, Discovery answers, measure cards) use only veiled phrasing. The Angriff worksheet and wave slide reveal the name. Fairness requirement (README: "keine Überraschungen bei aufmerksamer Discovery"): **every attack must be inferable from at least 2 clues** in pre-material. Record that as a facilitator-side clue matrix. |
| T11 | **Scheduled debrief slot (15-20 min minimum)** | Crookall: the debrief is the core of a serious game. NIST 800-84 / CISA: hot wash immediately after. B&B: "the most important part of the educational process". D&D: the reveal plus "perfect game" is the end of every session. MHP timeline: **no debrief slot**. | LOW | Structure: (1) reaction, a 1-min round of feelings; (2) description, where each team shows its tracking-sheet trajectory; (3) analysis, covering why waves hit or missed, sunk cost and overspend decisions; (4) application, the real-world transfer (ROSI thinking, budget negotiation). Time comes from the whiteboard write-up that T4 removes (15 min) and the shorter wave 1 that T3 gives. |

### Differentiators (Competitive Advantage)

These go beyond what players expect. They build on this game's Core Value (determinism and hand-calculability) and on assets the repo already has (full enumeration).

| # | Feature | Value Proposition | Complexity | Notes |
|---|---------|-------------------|------------|-------|
| D1 | **"Perfekte Strategie" debrief sheet from full enumeration** | D&D's "perfect game" is hand-written. This game can *prove* the best strategy per budget tier from `simulate_outcomes.py` and show where each team landed in the distribution (percentile of KZ / RoS). No reference game can do that. | MEDIUM | Generate one debrief page per tier: best in-budget combination, median, each team's percentile. It reuses `analyze_simulation_results.py`, so the only new work is the LaTeX template. Needs the rebalanced config and depends on T8/T9 being in the sim. |
| D2 | **Per-wave impulse debrief (2-3 min after each wave)** | Impulse-Debriefing-Spiral: reflection moments during play, not only at the end. Cheap, and it connects each wave's outcome to the decision that caused it while memory is fresh. | LOW | Two fixed questions printed on the facilitator sheet (T5), e.g. "Welche eurer Maßnahmen hat in dieser Welle gewirkt, und woran erkennt ihr das?" / "Was hättet ihr mit dem Wissen von jetzt anders gekauft?" Keep it short: waves 2-3 must still fit 20 min. |
| D3 | **Designated team role "Controller:in" (rule seeder / scribe)** | Control-Alt-Hack's fix for the learning curve: pre-briefed people seed each group. TTX doctrine: dedicated scribe. Spreads the calculation load and stops all five people from watching one pen. | LOW | One person per team owns the tracking sheet and is briefed on T2 during team formation. They can be briefed live in 3 min while other members read the company profile. No new material beyond a role card. |
| D4 | **Shrinking decision timers per wave** | D&D uses 12 / 9 / 7.5 / 7.5 min decision windows. That enforces the schedule and matches the observed learning curve. | LOW | Print the target times on the facilitator sheet (e.g. wave 1 25 min incl. impulse debrief, waves 2-3 20 min). Visible countdown on the slide. |
| D5 | **Facilitator "quick vote" deadlock breaker** | D&D rulebook: every player names the one most important measure; that narrows options without the GM steering. Solves slow measure selection (the 35-min measures+budget phase at MHP). | LOW | One paragraph on T5, no material. |
| D6 | **In-character FAQ for the facilitator** | D&D scripts answers for predictable questions, e.g. "Can we have more budget?" is answered as the board ("make a case…"). Keeps role-play intact and answers consistent across facilitators. | LOW | Short section on T5. Seed it from the MHP questions (downgrade, measure vs level change, overspend). |
| D7 | **Participant feedback form (1 page)** | CISA CTEP has a participant feedback form template. The MHP feedback was handwritten notes. A form makes the next iteration's feedback comparable. | LOW | Five Likert items plus two free-text items. Optional, generated or static. |

### Anti-Features (Commonly Requested, Often Problematic)

| # | Feature | Why Requested | Why Problematic | Alternative |
|---|---------|---------------|-----------------|-------------|
| A1 | **Dice / probabilistic mitigation** (B&B d20, D&D2 "firewall 60% effective") | Makes reference games replayable and adds "tension". | Breaks the core determinism principle; players can't learn cause and effect ("Pech" becomes the explanation, as B&B itself admits). Out of Scope in `PROJECT.md`. | Keep deterministic. Tension comes from veiled threats (T10) and events. |
| A2 | **Digital GM assistant / app** (D&D2 Java tool, KIPS platform) | Removes hand calculation. | Out of Scope (paper game). Adds a device dependency to a live workshop and hides the mechanics players asked to understand. | Printed facilitator sheet (T5) plus team self-calculation (T4) with facilitator spot checks. The Python sim stays a prep-time tool. |
| A3 | **Hiding the mechanics** (D&D: "players should not read the rulebook") | Surprise and immersion. | Contradicts the MHP feedback (mechanics unclear) and the 2026-09-29 decision ("mechanics always transparent"). | Hide only *which* threat comes (T10); print all formulas (T2). |
| A4 | **Refund on downgrade / selling measures** | Feels realistic ("Vertrag kündigen"). | Creates a buy-then-sell exploit, multiplies the enumeration space (change paths per wave) and no reference game does it. | T7: no downgrade, or at most an OPEX saving without Init refund, and only if the sim models it. |
| A5 | **Loan / interest mechanics for overspend** (T&T loan pad, TOPSIM 17% overdraft) | "Realistic finance". | Extra state to track (principal, rate, maturity) and extra calculations per wave. Violates the ~3h budget and the hand-calculability constraint. | T8: a single linear KZ penalty per started 10k, looked up from a printed table. |
| A6 | **Flat or tiered penalty bands** (the current Budget Review "<0 → -15") | Simple to print. | A flat penalty has zero marginal cost past the first euro, which is the exact exploit from feedback #5. | T8 linear per-10k penalty. Tiered *bonuses* for leftover budget can stay, but the negative side must be linear. |
| A7 | **Purchasable threat intel card** (D&D Threat Assessment) | Nice mechanic: pay to see the future. | New measure type, new balance axis, new enumeration dimension. Duplicates the existing Discovery phase, which already plays this role for free. | Keep the Discovery role-play as the intel channel. Make sure the clues are sufficient (T10 fairness rule). |
| A8 | **Live public full leaderboard after every wave** | Competition drives engagement. | Teams that fall behind early disengage. Full numbers on a board also bring back the whiteboard bottleneck (T4). | Show at most KZ per team after each wave. The full comparison (KZ, RoS, percentile) comes in the debrief (D1). The Final-Index stays on the facilitator side (existing). |
| A9 | **Non-linear formulas on worksheets** (e.g. curved KZ interpolation, multiplicative factor chains) | "More realistic" damage curves. | Hard design criterion: facilitators calculate by hand. Out of Scope. | Linear interpolation (existing) plus printed lookup tables where a step function is unavoidable (T8). |
| A10 | **Reading attack names/technical detail in pre-wave material** | Easier for facilitators ("just read the card"). | Removes the inference part players enjoyed ("interaktiv ++"), per the pending todo. | T10 veiled `display_name` plus the facilitator clue matrix. |

---

## Feature Dependencies

```
simulation_config.json changes (T8 penalty X, T9 RoS split, T10 display_name, T7/T6 rule text)
    └──required by──> LaTeX print generator (all printed artifacts)
                          ├──> T1 card legend  (same template as measure cards)
                          ├──> T2 rule reference
                          ├──> T3 worked example "Welle 0"  ──requires──> T2, T4 (example is shown ON the tracking sheet)
                          ├──> T4 tracking sheet  ──requires──> T9 (two cost columns), T8 (penalty lookup)
                          ├──> T5 facilitator sheet ──requires──> T4 (per-team check rows mirror sheet cells)
                          └──> D1 perfect-strategy sheet ──requires──> rebalanced config + full enumeration incl. over-budget combos

T8 overspend penalty ──requires──> simulate_outcomes.py stops dropping over-budget combos (line ~539)
T9 RoS split          ──requires──> simulate_outcomes.py stops adding event OPEX to total cost (line ~536)
T7 downgrade rule     ──(if downgrade allowed)──requires──> sim models change-window paths (big enumeration growth)

T3 worked example ──enhances──> T4 (teams learn the sheet by watching it filled)
D3 Controller role ──enhances──> T4, T3
D2 impulse debrief ──enhances──> T11 final debrief
T4 (removes 15-min whiteboard) + T3 (shortens wave 1) ──enable──> T11 debrief slot (time budget)

T10 veiled pre-wave material ──conflicts──> "measure cards show what attacks they counter" (see C1)
A4 downgrade refund ──conflicts──> T8 (sell-back becomes a way to launder overspend)
```

### Dependency Notes

- **All printed artifacts require the config changes first.** This follows the project order (config → README → print). It confirms the 2026-09-29 decision "generate docs before rebalancing": the generator must exist before any rebalance, but the *rule* fields it prints (T6/T7 text, T8 table, T9 columns, T10 display names) must be in the config schema before the templates are written, or the templates get written twice.
- **T3 requires T2 and T4.** The worked example is only useful if it is demonstrated on the exact sheet and in the exact step order the teams will use. Build the tracking sheet first, then the example on top of it.
- **T8 and T9 require sim changes before balancing.** The sim currently drops over-budget combinations and adds event OPEX to cost, so neither rule can be calibrated or verified until those two code paths change (TDD per `PROJECT.md`).
- **T4 + T3 buy the time for T11.** The MHP schedule had no free minutes. Removing the 15-min whiteboard write-up and cutting wave 1 from 34 to about 25 min recovers roughly 25 min, which pays for Welle 0 (~10 min) plus a 15-min debrief.
- **Conflict C1: T1 legend vs T10 veiling.** Feedback #2 asks "was haben Angriffe … für Effekte" on the cards, but the veiling decision forbids naming attacks before the wave. Resolution, following B&B (the attack card lists what detects it, not the other way round): **measure cards show CIA contribution only.** The measure-to-attack link (`bonus_measures`) lives on the Angriff worksheet, which is revealed at the wave. The legend (T1) explains the *mechanics* ("CIA-Werte zählen über die Wellen-Gewichte in euren E-Wert; manche Maßnahmen geben in passenden Wellen einen Bonus"). This needs explicit user confirmation.
- **Conflict: A4 refund vs T8.** If measures can be sold back, a team can overspend, sell, and dodge the penalty. That is another reason to keep T7 as "no downgrade".

## MVP Definition

### Launch With (next workshop)

- [ ] **T6 + T7**: vocabulary and downgrade rule decided and printed. This resolves feedback #3/#4 and costs nothing.
- [ ] **T8**: linear overspend penalty, calibrated by full enumeration. Resolves feedback #5, the only actual exploit.
- [ ] **T9**: RoS split into own vs external costs, discounts included. Resolves feedback #6.
- [ ] **T10**: veiled pre-wave names plus a clue matrix. Decided; the todo is pending.
- [ ] **T1 + T2**: card legend and one-page rule reference. Resolves feedback #2.
- [ ] **T4**: tracking sheet. Removes the 15-min whiteboard bottleneck.
- [ ] **T5**: facilitator master sheet. Core Value; missing from the Active list.
- [ ] **T3**: worked example Welle 0. Fixes the wave 1 overrun.
- [ ] **T11**: debrief slot in the schedule plus a question set on T5. Biggest pedagogical gap.

### Add After Validation

- [ ] **D1** "perfect strategy" sheet: once the rebalanced config is stable, since every rebalance would change it.
- [ ] **D2** impulse debrief questions: add if wave timing at the next run leaves slack.
- [ ] **D3** Controller role card: add if the next run still shows one-pen bottlenecks inside teams.
- [ ] **D7** feedback form: add before the next run if comparable evaluation data is wanted.

### Future Consideration

- [ ] **D4** shrinking timers, **D5** quick vote, **D6** in-character FAQ: pure facilitation text. Fold them into T5 when it is written. They are listed separately only because they are optional.
- [ ] Downgrade with OPEX saving (the T7 alternative): only if a future run shows players really want it, and only with change-path enumeration in the sim.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| T8 linear overspend penalty | HIGH | MEDIUM (sim + calibration) | P1 |
| T9 RoS own vs external | HIGH | LOW-MEDIUM (sim + sheet column) | P1 |
| T6 / T7 vocabulary + downgrade rule | HIGH | LOW | P1 |
| T4 tracking sheet | HIGH | MEDIUM (template) | P1 |
| T2 rule reference | HIGH | LOW | P1 |
| T1 card legend | HIGH | LOW | P1 |
| T3 worked example Welle 0 | HIGH | MEDIUM (generated example numbers) | P1 |
| T5 facilitator master sheet | HIGH | MEDIUM | P1 |
| T10 veiled names + clue matrix | MEDIUM | LOW-MEDIUM (config field + text pass over materials) | P1 |
| T11 debrief slot + questions | HIGH | LOW | P1 |
| D1 perfect-strategy debrief sheet | MEDIUM-HIGH | MEDIUM | P2 |
| D2 impulse debrief | MEDIUM | LOW | P2 |
| D3 Controller role | MEDIUM | LOW | P2 |
| D7 feedback form | MEDIUM | LOW | P2 |
| D4 / D5 / D6 facilitation tips | LOW-MEDIUM | LOW | P3 (fold into T5) |

## Competitor Feature Analysis

| Feature | Decisions & Disruptions 1 | Backdoors & Breaches | Threats & Trade-offs / TOPSIM | Our Approach |
|---------|---------------------------|----------------------|-------------------------------|--------------|
| Rule teaching | Scripted GM intro, cards read aloud, FAQ | Card anatomy + sequence + worked example | Trial period (TOPSIM) | T1 + T2 + T3 (legend, one-pager, Welle 0) |
| Budget cap | Hard, carry-over allowed | n/a | Loans / penal overdraft | Linear per-10k KZ penalty (T8) |
| Downgrade | Not possible | n/a | Not possible (T&T) | Not allowed (T7), sunk cost as debrief point |
| Threat reveal | Type withheld per round, all revealed at end | Veiled opening, one card at a time | Attack card at round end | Veiled before the wave, named at the wave (T10) |
| External shocks vs score | Losses separate from budget | n/a | External draws separated in round sequence | Two cost columns; events out of RoS (T9) |
| State tracking | GM photocopied attack table | Cards on table | Counters on board + loan pad | Team sheet (T4) + facilitator master (T5) |
| Debrief | Reveal + "perfect game" | "Why would it fail in reality?" | Recorded discussion | T11 structured debrief + D1 enumeration-backed "perfect strategy" |

## Sources

Confidence tiers come from the `classify-confidence` seam: unverified web = LOW, cross-checked or primary document = MEDIUM.

- Decisions & Disruptions rulebook and GM cheat sheet (primary PDFs, read in full): https://github.com/benshreeve/decisions-disruptions-kit and https://www.decisions-disruptions.org/. MEDIUM.
- D&D session description (penalties don't hit budget, "perfect game" debrief, round timers): https://southeastcyber.police.uk/decisions/. MEDIUM (consistent with the rulebook).
- Decisions & Disruptions 2 paper (D-D1 deterministic paths; D-D2 probabilistic, Java GM tool): https://arxiv.org/html/2306.12168. MEDIUM.
- Backdoors & Breaches Visual Guide v2 (primary PDF): https://www.blackhillsinfosec.com/wp-content/uploads/2024/03/BnB_VisualGuide_v2_03052024.pdf and How-to-Play: https://www.blackhillsinfosec.com/wp-content/uploads/2019/09/How-to-Play-BB.pdf. MEDIUM.
- Control-Alt-Hack CCS'13 evaluation (primary PDF; "takes a long time to learn", rule-seeders, 10-min video): https://adalerner.com/cah-eval-ccs2013.pdf. MEDIUM.
- Threats & Trade-offs (2025; loans, no downgrade, counters on board, separated external draws): https://pmc.ncbi.nlm.nih.gov/articles/PMC13201351/. MEDIUM.
- TOPSIM participant handbook (automatic overdraft at penal interest; trial period): https://www.thm.de/wi/images/user/arnold-75/01_Teilnehmerhandbuch_Basics_2_5.pdf and https://uol.de/f/2/dept/wire/fachgebiete/accounting/download/Ablauf_des_Unternehmensplanspiels_TOPSI1.pdf. LOW-MEDIUM (search summary of the primary handbook).
- CyberCIEGE (budget/productivity/security trade-off): https://nps.edu/web/c3o/cyberciege. LOW.
- Kaspersky KIPS overview (teams of 4-6, 2h, revenue-based score): https://media.kaspersky.com/en/business-security/enterprise/KL_SA_KIPS_overview_A4_Eng_web.pdf. MEDIUM (primary PDF).
- NIST SP 800-84 (hot wash, facilitator + data collector roles): https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-84.pdf. LOW-MEDIUM (search summary).
- CISA Tabletop Exercise Packages (SitMan, facilitator/evaluator handbook, participant feedback form): https://www.cisa.gov/resources-tools/services/cisa-tabletop-exercise-packages. LOW-MEDIUM.
- ENISA Cybersecurity Exercise Methodology (2026) and National Exercise Good Practice Guide (MSEL/injects): https://www.enisa.europa.eu/publications/national-exercise-good-practice-guide. LOW.
- ENISA ROSI formula: https://www.infosecurity-magazine.com/news/an-introduction-to-return-on-security-investment/. LOW-MEDIUM.
- Crookall, "Serious games, debriefing, and simulation/gaming as a discipline" (2010): https://journals.sagepub.com/doi/10.1177/1046878110390784. LOW-MEDIUM (abstract level).
- Schwägele et al., "Design of an Impulse-Debriefing-Spiral for Simulation Game Facilitation" (2021): https://research.tudelft.nl/en/publications/design-of-an-impulse-debriefing-spiral-for-simulation-game-facili-3/. LOW-MEDIUM (abstract level).
- Worked-example effect (cognitive load theory): https://en.wikipedia.org/wiki/Worked-example_effect. MEDIUM (well-established learning science).
- Player aids / reference cards in board-game UX: https://therewillbe.games/articles-essays/9006-player-aids. LOW.
- Project inputs: `.planning/PROJECT.md` (MHP feedback + timing), `README.md`, `simulation_config.json` (events `kurswechsel`, `operative_unterstuetzung`, `sparprogramm`, `final_events.budget_review`), pending todo `2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln…`.

---
*Feature research for: facilitated paper-based IT-security serious game (CIA-Planspiel Automotive, post-MHP refinement)*
*Researched: 2026-09-29*
