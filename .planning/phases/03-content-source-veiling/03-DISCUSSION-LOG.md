# Phase 3: Content Source & Veiling - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-06
**Phase:** 03-content-source-veiling
**Areas discussed:** Content source shape, Digit lint boundaries, Veiled vs revealed texts, Clue matrix & pre-wave docs

Todo cross-reference: "Angriffe und Aktionen nur indirekt vermitteln" was **folded** (close after Phase 5).

---

## Content source shape

| Option | Description | Selected |
|--------|-------------|----------|
| One content/texte.toml | Single file, sections per id, stdlib tomllib | ✓ |
| Split per domain | measures/attacks/events/sheets.toml | |
| Markdown with front-matter | One .md per id, needs parser | |

| Option | Description | Selected |
|--------|-------------|----------|
| Strip prose, keep short labels | Descriptions to TOML; config keeps ids + labels; waves[].name removed | ✓ |
| Strip everything incl. names | Config ids + numbers only | |
| Keep config, TOML overrides | Two places for the same text | |

| Option | Description | Selected |
|--------|-------------|----------|
| Leave legacy generators untouched | Until LEG-01 (D-29) | ✓ |
| Rewire legacy generators to TOML | Touches code being retired | |

| Option | Description | Selected |
|--------|-------------|----------|
| Narrative + generated effect line | No numbers in TOML | ✓ |
| Allow {param} placeholders | Flexible, mixes mechanics into prose | |
| Both | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Rule texts in TOML (narrative + rule keys) | One place to edit wording | ✓ |
| Rule texts generated in code | Editorial edits need code | |

| Option | Description | Selected |
|--------|-------------|----------|
| Reviewed text-only snapshot change | Like 02-07 | ✓ |
| Goldens read names from TOML | Sim depends on content source | |

| Option | Description | Selected |
|--------|-------------|----------|
| Keep all four measure text fields as-is | Phase 5 decides what to print | ✓ |
| Reduce to description + levels_simple | | |
| Rework wording now | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Measures describe themselves | Only attack names + wave links banned | ✓ |
| Scrub attack-type words from measures | Stronger veil, less clarity | |

---

## Digit lint boundaries

| Option | Description | Selected |
|--------|-------------|----------|
| Strict with reviewed flavor allowlist | | ✓ |
| Strict, rewrite flavor numbers | | |
| Lint only number-shaped game values | Heuristic | |

| Option | Description | Selected |
|--------|-------------|----------|
| All of texte.toml | | ✓ |
| Only narrative keys | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Number words allowed | Digits only | ✓ |
| Also flag number words | Noisy | |

Later addition (from the story-docs decision): `[story.*]` is exempt from the digit lint, chosen over allowlisting each token.

---

## Veiled vs revealed texts

| Option | Description | Selected |
|--------|-------------|----------|
| Neutral title + indirect hints | | |
| Neutral title only | No teaser; clues only in story docs | ✓ |
| Evocative title + hints | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Names + core technique terms | Case-insensitive, stems | ✓ |
| Attack names only | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Claude drafts, user reviews | | ✓ |
| User writes them | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Events stay named | Keeps 2026-09-29 decision | ✓ |
| Veil events until drawn | | |
| Veil event names too | | |

| Option | Description | Selected |
|--------|-------------|----------|
| "Angriff 1/2/3" | Matches worksheet naming | ✓ |
| "Vorfall 1/2/3" | | |
| "Welle 1/2/3" | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Giveaway lint on veiled attack texts only | Exactly SC3; resolves the M6 "Phishing" conflict | ✓ |
| All pre-wave keys, measures exempt for techniques | | |
| All pre-wave keys, rewrite M6 | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Name + scenario + CIA rationale | Bonus reasons revealed-only | ✓ |
| Name + scenario only | | |

---

## Clue matrix & pre-wave docs

Story docs: the user asked "Also tex / toml? Recommend?" Claude then found that Anfrage-Mail also names Ransomware and that Audit-Mail.pdf is image-only, and pointed to SCEN-04. Follow-up:

| Option | Description | Selected |
|--------|-------------|----------|
| TOML now, LaTeX in Phase 5 | New PRINT-12 + ROADMAP amendment | ✓ |
| TOML now, docx stays printed copy | Manual sync remains | |
| Stay hand-maintained docx | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Rewrite Zeitungsartikel veiled in Phase 3 | | ✓ |
| Accept as deliberate hint | Contradicts VEIL-02 | |
| Defer rewrite to Phase 5 | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Data file with verbatim quotes | content/clues.toml, quotes verified | ✓ |
| Data file, count only | | |

| Option | Description | Selected |
|--------|-------------|----------|
| ≥2 distinct sources | | ✓ |
| Any two clues | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Exempt [story.*] from digit lint | | ✓ |
| Allowlist each token | | |

---

## Claude's Discretion

- Allowlist location/syntax; how measure ids (M1…M10) pass the digit lint
- TOML key names; inventory format
- Declared `[sheets.*]` keys before templates exist
- Audit-Mail transcription method

## Deferred Ideas

- Story-doc LaTeX generation → Phase 5 (PRINT-12)
- VEIL-02 rendered-PDF scan → Phase 5
- Per-scenario story texts/clues → v4 (SCEN-04)
