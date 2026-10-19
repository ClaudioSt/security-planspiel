# Phase 4: Print Pipeline & Attack Worksheets - Context

**Gathered:** 2026-10-19
**Status:** Ready for planning

<domain>
## Phase Boundary

One non-interactive, reproducible LaTeX → PDF build (`uv run planspiel print`) generates the Angriff 1–3 worksheets from `simulation_config.json` and `content/texte.toml`. An equivalence test proves that the printed hand-calculation steps give the same results as the simulation, and every generated page carries a version stamp.

Not in this phase: measure/event/Budget Review cards, budget/RoS sheets, tracking sheet, "So funktioniert eine Welle", Welle 0, facilitator master sheet, story documents, the VEIL-02 scan (all Phase 5). Making awkward constants hand-friendly, such as the wave-3 slope 17/7 (Phase 6, BAL-02). Archiving the old `Angriff-*.docx` (Phase 7, LEG-01).

Requirements: PRINT-01, PRINT-03, PRINT-04, PRINT-11 (ROADMAP Phase 4 success criteria 1–4).

</domain>

<decisions>
## Implementation Decisions

### Carried forward (decided earlier, not re-asked)
- Renderer is **LaTeX, not Typst** (PROJECT.md Key Decisions 2026-09-29). Research stack: LuaLaTeX + Jinja2 with `\VAR{}`/`\BLOCK{}` delimiters, `StrictUndefined`, LaTeX escaping via `finalize`, latexmk (`.planning/research/STACK.md`).
- The attack worksheet is **revealed** material. Its title reads "Angriff N: <Name>" (Phase 3 D-13, D-27). Wave CIA weights and measure→bonus links appear only here (VEIL-04). Revealed texts come only through `planspiel.texts.RevealView`.
- **No numbers in TOML prose** (Phase 3 D-03). Every printed number is computed from config in code (pattern: `planspiel/review_text.py`). Worksheet wording is in `[sheets.angriff]`, `[sheets.labels]` and `attacks.*.revealed.*`.
- **Paper rounding** (Phase 1, 01-06): the KZ change per wave (attack + events) is rounded once, half away from zero, then clamped to 0..100. Everything else stays exact.
- Excel attack calculator is retired. Legacy generators stay untouched until LEG-01 (Phase 2 D-29).
- Known hazard (STATE.md): MiKTeX `AutoInstall=ask` hangs scripted builds, so the **first plan is a non-interactive smoke build**.

### Worksheet content and layout (PRINT-03)
- **D-01:** **MHP order with numbered steps.** Keep the MHP flow (narrative → CIA table → E-value → bonus → Gesamtreduktion → Fall 1/2/3) but number the steps (Schritt 1…n) and give each step a fill-in box. People who ran the MHP version should recognise the sheet.
- **D-02:** **The E-value step prints the formula with the wave weights from config and fill-in boxes**, e.g. "E-Wert = C ___ × 0,4 + I ___ × 0,4 + A ___ × 0,2 = ___". The MHP sheets did not print the weights at all.
- **D-03:** **Recovery is an extra step on the worksheet**, only when the attack has `allow_recovery = true` (attacks 1 and 2 today): "Schaden nach Recovery = Schaden × (1 − r)", with a small table M4 level → r taken from `measures.M4.levels.*.recovery` (0 / 10 % / 30 % / 50 % today). Attack 3 has no recovery step. The worksheet must record every mechanic the sim applies (see D-11).
- **D-04:** **Each team fills in its own copy** (3 teams × 3 waves = 9 sheets). Wording addresses the team ("Tragt eure …"), as in the docx and `[sheets.angriff]`.
- **D-05:** **Page budget: one A4 page is ideal, two pages are allowed if necessary.** The CIA table does **not** have to reach the maximum possible number of measures. Choose a practical number of rows (the MHP sheet has 6).

### Fall-3 formulas (PRINT-03, hand-calculability)
- **D-06:** **Damage uses the rearranged form plus a hard guard:** "Schaden = (Obergrenze − Gesamtreduktion) × s_unit", with derived numbers (e.g. "(31 − GR) × 20.000 €", Obergrenze = `e_threshold + mitigation_cap`). This is only correct while `base_severity == mitigation_cap` and `severity_multiplier == 1` (both hold today). If either invariant breaks, **the build fails** instead of printing a wrong formula. There is no auto-switch to the general form.
- **D-07:** **One KZ formula shape on every sheet:** "KZ = kz_at_full_damage + (GR − e_threshold) × Steigung", e.g. "KZ = −6 + (GR − 23) × 2". This replaces the three MHP variants.
- **D-08:** **The slope is printed exactly.** An integer or terminating-decimal slope prints as "× 2" / "× 1,2"; any other fraction prints as "× a ÷ b" (wave 3 today: "× 17 ÷ 7"). The equivalence test stays exact, and the validator warning for 17/7 stays until Phase 6 (BAL-02).
- **D-09:** **Intermediate values are exact, with a printed hint.** E-value and GR are exact (one decimal place with the current weights). For the Fall-3 KZ the sheet says that two decimal places are enough. Research must prove that carrying two decimal places can never flip the final per-wave rounding for any reachable input. If it can, adjust the hint (more places or a different instruction) and say so.
- Fall 1 / Fall 2 lines print their pre-computed outcomes (full damage in €, KZ at full damage / full mitigation), derived in code as on the MHP sheet.

### Equivalence test (PRINT-04)
- **D-10:** **The once-per-wave KZ rounding is the last step on the worksheet:** "KZ-Änderung dieser Welle = KZ Angriff + KZ Events, gerundet (ab ,5 vom Betrag aufrunden)". The test therefore covers the full wave KZ change including rounding. Clamping to 0..100 needs the running KZ and stays on the Phase-5 tracking sheet.
- **D-11:** **Proof link:** the hand-calc replay reads **only** from the same worksheet print model that the template renders. If the sim applies a mechanic the model and sheet do not carry, the results differ and the test fails (SC3). A slow PDF test extracts the text of each built worksheet (pypdf) and asserts that every number in the print model appears on the page.
- **D-12:** **Grid = synthetic grid plus full replay.**
  - Fast test: every GR step of 0,1 from below Fall 1 to above Fall 2 (exact boundaries included) × every bonus subset × every M4 level × every event-KZ value the config can produce for that wave, compared with `planspiel.rules`.
  - Slow test (`-m slow`): replay every enumerated plan's waves through the worksheet steps and compare with the simulation.

### Build, output and stamp (PRINT-01, PRINT-11)
- **D-13:** **Command: `uv run planspiel print`**, a new subcommand of the existing CLI next to `validate`, `gate`, `texts` and `clues`. Phase 4 builds the three worksheets; Phase 5 adds its documents to the same command (PRINT-01: one command for all print material).
- **D-14:** **Output:** rendered `.tex`, aux files and logs go to a gitignored build directory. The final PDFs are **committed to `final_documents/generated/`**. Rebuilds are byte-identical, so git shows a PDF diff only when the content changed. Never hand-edit these files.
- **D-15:** **Stamp = input hash + commit date** in every page footer, e.g. "Stand 2026-10-19 · a1b2c3d". The hash covers all inputs (config, `texte.toml`, templates/sty and any other file the build reads). The date is the last commit date of those inputs, never the wall clock, so builds stay reproducible. A dirty working tree adds a marker such as "+lokal". This is broader than SC4's "config hash": a wording change also changes the stamp.
- **D-16:** **Font: system Arial** (as on the MHP Word worksheets; user decision). Consequence: byte-identical rebuilds are guaranteed only on machines with the same Arial version. The SC1 reproducibility test runs on the build machine (two builds, same inputs, identical bytes). Accept this; do not commit a substitute font.
- **D-17:** **MiKTeX: one-time update plus a pinned package list plus a preflight.** The user updates MiKTeX once (23.10 → current) and installs a documented package list (research: `tikzfill`, `tabularray`, `ninecolors`, `siunitx` and whatever the templates need). `planspiel print` first runs a fast preflight (e.g. `kpsewhich` per required `.sty`) and fails with the missing package names. LuaLaTeX always runs with `--disable-installer` and a subprocess timeout, so a missing package fails fast and never hangs. The first plan is this smoke gate. The MiKTeX update itself is a user action (checkpoint), not something the executor does silently.
- **D-18:** **Colour style like the MHP decks:** use the MHP theme colours from `content/assets/GUIDELINES.md` (accent1 `000099` for headings, level colours L1 `00CC67` / L2 `DDEF03` / L3 `575757` where levels appear, etc.). The worksheets are designed for colour printing. Layout facts such as A4 and the margins left 3.0 / right 1.5 / top 2.0 / bottom 2.0 cm come from the Word worksheets in GUIDELINES.md, as a starting point rather than a hard rule.

### Claude's Discretion
- Number of CIA table rows (D-05) and the exact step numbering and wording of new step labels. New wording goes into `[sheets.angriff]` / `[sheets.labels]`, digit-free, and passes `planspiel texts`.
- Module layout for the print model, formatting and rendering (research suggests `printmodel.py`, `fmt.py`, `render.py`, `print/planspiel.sty` and thin Jinja templates) and the build directory name.
- The exact hash algorithm and length, how "dirty" is detected, and how the commit date is fed to LuaLaTeX (`SOURCE_DATE_EPOCH`, `FORCE_SOURCE_DATE`, `\pdfvariable trailerid {}`).
- German number formatting rules (thousands dot, decimal comma, real minus sign "−") and whether `format_eur` from `review_text.py` is reused or moved.
- Whether the PDF tests use a new `pdf` marker or the existing `slow` marker, and that they skip when no TeX engine is present.
- File names under `final_documents/generated/` (they may name the attack: these are revealed sheets).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope and prior decisions
- `.planning/PROJECT.md` — Key Decisions (LaTeX, single source of truth, veiling, paper rounding), Constraints (hand-calculability)
- `.planning/REQUIREMENTS.md` — PRINT-01, PRINT-03, PRINT-04, PRINT-11 (this phase); PRINT-05..12, VEIL-02/04 (Phase 5 consumers of the same pipeline); BAL-02 (Phase 6, 17/7)
- `.planning/ROADMAP.md` §Phase 4 — success criteria 1–4 and research flag (non-interactive MiKTeX, spike-compile only)
- `.planning/STATE.md` — Blockers/Concerns: MiKTeX hang, first plan is the smoke build
- `.planning/phases/03-content-source-veiling/03-CONTEXT.md` — D-03 (no numbers in prose), D-13/D-23/D-27 (titles), D-22 (assets folder), D-29 (backup & recovery text)
- `.planning/phases/02-rule-changes/02-CONTEXT.md` — rule vocabulary and the Phase 2 rules the worksheet must reflect
- `.planning/phases/01-simulation-foundation/01-CONTEXT.md` and `01-EXACT-SWITCH-DIFF.md` — exact arithmetic and the rounding rule

### Pipeline research
- `.planning/research/STACK.md` — LuaLaTeX/Jinja2/latexmk stack, `tex_escape` finalize, `build_pdf` sketch with `--disable-installer`, missing MiKTeX packages, pypdf text assertions, anti-patterns (`[most]`, autoescape)
- `.planning/research/ARCHITECTURE.md` — Pattern 1 (print model derives everything, `AttackWorksheet.hand_calc`), Pattern 2 (hand-calc invariants), Pattern 5 (Jinja for LaTeX), output layout `final_documents/generated/` + manifest
- `.planning/research/PITFALLS.md` — Pitfall 9 (worksheet speed), Pitfall 12 (MiKTeX hang, `SOURCE_DATE_EPOCH`, trailer id, sorted iteration), Pitfall 13 (version stamp)

### Current worksheets (to reproduce and improve)
- `final_documents/Angriff-1_Ransomware.docx`, `final_documents/Angriff-2_OT-Störung.docx`, `final_documents/Angriff-3_Datenexfiltration.docx` — MHP structure and wording; they print no wave weights and no recovery step
- `content/texte.toml` — `[sheets.angriff]`, `[sheets.labels]`, `[sheets.backup_recovery]`, `attacks.*.revealed.*`
- `content/assets/GUIDELINES.md` — MHP colours, Word worksheet font/margins

### Rules and config
- `planspiel/rules.py` — `e_value_scaled`, `reduction_above_threshold_scaled`, `severity_scaled`, `damage_euros`, `compute_recovery`, `compute_bonus_reduction`, `kz_slope`, `attack_kz_delta`, `wave_kz_change`, `apply_attack`, `evaluate_event`
- `planspiel/rounding.py` — `round_half_away`
- `planspiel/validate.py` — `check_hand_calc`, `HandCalcWarning` (base_severity / cap / slope invariants)
- `simulation_config.json` — `waves[].weights`, `e_threshold`, `bonus_measures`; `attacks.*`; `measures.M4.levels.*.recovery`; `budget_tiers.*.severity_multiplier`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `planspiel/texts.py` `RevealView` (`attack_title`, `attack`, `sheet`): the only access path to revealed texts; the worksheet model builds on it.
- `planspiel/review_text.py` `format_eur`: existing German € formatting; reuse or move into a shared formatter.
- `planspiel/rules.py`: every formula exists once; the print model calls these helpers and must not re-implement them (single-definition guard `tests/test_single_definition.py`).
- `planspiel/validate.py` `check_hand_calc`: already detects the base_severity/cap and slope invariants; D-06 turns the print-relevant ones into a build failure.
- `planspiel/enumerate.py` / `TierKernel`: source of all plans for the slow full replay (D-12).

### Established Patterns
- CLI subcommands in `planspiel/cli.py` (`validate`, `tausch`, `gate`, `texts`, `clues`): `print` follows the same style.
- TDD; slow tests behind `-m slow`; always `uv run`.
- Exact arithmetic with scaled integers/`Fraction`; Python's `round()` is banned in `rules.py`/`rounding.py`.
- Text lints (`planspiel texts`) must stay green when new sheet labels are added.

### Integration Points
- New print model reads `Config` + `Texts` (via `RevealView`) and calls `rules`; the templates receive only formatted values.
- Phase 5 reuses the same render pipeline, preflight, stamp and `final_documents/generated/` output.
- `.gitignore` needs the build directory.

</code_context>

<specifics>
## Specific Ideas

- Example lines the user approved in discussion: "E-Wert = C ___ × 0,4 + I ___ × 0,4 + A ___ × 0,2 = ___", "Schaden = (31 − GR) × 20.000 €", "KZ = −6 + (GR − 23) × 2", "× 17 ÷ 7", "KZ-Änderung dieser Welle = KZ Angriff + KZ Events, gerundet".
- Stamp example: "Stand 2026-10-19 · a1b2c3d" (+ "+lokal" when the tree is dirty).

</specifics>

<deferred>
## Deferred Ideas

- Clamping KZ to 0..100 on the running total: Phase 5 tracking sheet (PRINT-08).
- Hand-friendly wave-3 slope (replacing 17/7): Phase 6 (BAL-02).
- Archiving `final_documents/Angriff-*.docx` once the generated sheets replace them: Phase 7 (LEG-01).

### Reviewed Todos (not folded)
- "Angriffe und Aktionen nur indirekt vermitteln, nie explizit benennen" (`.planning/todos/pending/2026-06-23-angriffe-und-aktionen-nur-indirekt-vermitteln-nie-explizit-b.md`): already covered by Phase 3 and closed out by Phase 5 (VEIL-02, VEIL-04). The attack worksheets are revealed material, so the todo does not constrain this phase.

</deferred>

---

*Phase: 04-print-pipeline-attack-worksheets*
*Context gathered: 2026-10-19*
