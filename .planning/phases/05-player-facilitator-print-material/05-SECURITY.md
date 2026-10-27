---
phase: 5
slug: player-facilitator-print-material
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-10-27
---

# Phase 5 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Content/config → TeX | `simulation_config.json`, `content/*.toml` and asset files are rendered into LaTeX templates | Free text and numbers; TeX-injection surface, mitigated by `tex_escape` finalize |
| Revealed data → pre-wave player documents | Attack names, wave weights and bonus links must not reach `spieler-`/`uebung-` documents before a wave | Veiled game information (confidentiality of the game, not of personal data) |
| Facilitator → player material | `spielleitung-uebersicht` holds answer keys and clue matrix | Answer keys; separated by job prefix, separate PDF and page-one notice |
| Build → committed print set | `final_documents/generated/` plus `manifest.json` stamp | Integrity of printed numbers; stale/dirty builds rejected by `print --check` |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-05-01 | Information disclosure | pre-wave and practice documents (text) | high | mitigate | Layer-1 scan on every rendered `.tex` as a build gate (`ERROR print.veil`), layer-2 scan on the PDFs, story / names-only profiles, revealed-string and weight-triple detection | closed |
| T-05-02 | Information disclosure | PDF metadata, XMP, outline, annotations, file names, manifest | medium | mitigate | `suppressoptionalinfo` stays in `planspiel.sty`; pdf test asserts empty metadata, no XMP/outline/annotations; job names of non-revealed documents scanned with the names profile | closed |
| T-05-03 | Information disclosure | a new document registered without classification | high | mitigate | `render_all` raises on an unknown prefix; completeness test over all jobs | closed |
| T-05-04 | Information disclosure | a pre-wave builder module importing revealed views or wave internals | medium | mitigate | AST guard `tests/test_veil_models.py` with `PREWAVE_MODULES` appended by each later plan | closed |
| T-05-05 | Tampering | de-TeX hiding a term (word merge across macros) | medium | mitigate | `detex` replaces control words by spaces; tests with names split by macros | closed |
| T-05-06 | Denial of service | false positives blocking the build (Phishing on M6, OT in measure names, shared case texts) | low | mitigate | names-only profile for the measure deck (D-24), D-20 story exceptions, case texts excluded from the attack-specific list; negative controls prove the scan still fails on real leaks | closed |
| T-05-07 | Elevation of privilege | TeX injection through content strings | low | accept | Unchanged from Phase 4: every value passes `tex_escape`, no shell escape; this plan adds no template | closed |
| T-05-08 | Tampering / Elevation of privilege | TeX injection via measure texts | medium | mitigate | Every value passes `tex_escape` (finalize); plain-variable template lint; render test with `Logging \& SIEM/MDR`; no shell escape | closed |
| T-05-09 | Information disclosure | measure cards revealing wave weights, bonus links or attack names | high | mitigate | Model has no such field (pinned in 05-04), pre-wave AST guard lists `cards.py`, layer-1 veil scan with the names-only profile (D-24) in the default suite; layer 2 runs on the built deck from 05-03 on | closed |
| T-05-10 | Tampering (integrity of printed numbers) | a lost glyph (`−`, `≥`, `€`) or an overflowing card hiding a number | medium | mitigate | Lock icon drawn in TikZ (05-02); card fit markers with used ≤ limit; `Missing character`/`Overfull` hygiene test over every job | closed |
| T-05-11 | Denial of service | slow or hanging TeX build of the TikZ deck | low | mitigate | Existing bounded driver (`--disable-installer`, timeout, process-tree kill); build time of the deck quoted in the SUMMARY | closed |
| T-05-12 | Tampering (supply chain) | new TeX package | low | accept | `pgf` is a CTAN core package already installed; added only to the probe list; the executor never runs the MiKTeX installer (Phase 4 D-17) | closed |
| T-05-13 | Information disclosure | a future field or text on measure cards leaking weights or bonus links | high | mitigate | Pinned `MeasureCard` field set; AST scan of `cards.py`; model, `.tex` and PDF negative tests (weights, bonus reasons, names, wave references) | closed |
| T-05-14 | Repudiation / integrity | worksheets silently losing the weights or bonus table (players could not compute) | medium | mitigate | Positive pdf tests per worksheet: own weight triple and every bonus row present | closed |
| T-05-15 | Denial of service | over-strict test rejecting the legitimate Phishing defence term | low | mitigate | Names-only profile for the deck (D-24) with an explicit test that documents the story-profile hit | closed |
| T-05-16 | Tampering | TeX injection via the new legend text | low | mitigate | Text passes `tex_escape`; digit lint and coverage via `uv run planspiel texts` | closed |
| T-05-17 | Tampering (integrity of printed numbers) | effect line diverging from the simulation | high | mitigate | Every row carries its exact value; equivalence tests per covered input against `rules.evaluate_event` / `budget_review_delta`; Budget Review boundaries tested at b, b − 1 and below zero | closed |
| T-05-18 | Information disclosure | event text naming an upcoming attack | medium | mitigate | Story-profile giveaway lint on `events.*` (`planspiel texts`), layer-1 and layer-2 veil scan of `spieler-eventkarten` | closed |
| T-05-19 | Tampering | TeX injection via event texts or names | low | mitigate | `tex_escape` finalize; plain-variable lint | closed |
| T-05-20 | Denial of service | unknown event type silently printing nothing | low | mitigate | `PrintModelError` for unknown types (`ERROR print.model`) | closed |
| T-05-21 | Tampering (integrity of printed numbers) | RoS / Restbudget formula diverging from the simulation (e.g. the stale event-penalty row) | high | mitigate | Formula replay tests against `evaluate_path` on three legal paths; no event row in own costs (RULE-06, F8); base losses from `rules.base_losses` | closed |
| T-05-22 | Denial of service | Phase 6 lowering X so the penalty table overflows the page silently | medium | mitigate | `MAX_PENALTY_ROWS` (12 today) guard raises `PrintModelError`; fill markers in the pdf test; review of the constant recorded as a Phase 6 follow-up by plan 05-16 | closed |
| T-05-23 | Information disclosure | booklet naming an attack or showing weights | medium | mitigate | Veiled titles only (`PreAttackView`), pre-wave AST guard, veil scan layers 1 and 2 | closed |
| T-05-24 | Tampering | TeX injection via texts | low | mitigate | `tex_escape` finalize, plain-variable lint | closed |
| T-05-25 | Tampering (integrity of results) | procedure on paper diverging from the simulation (double rounding, clamp before rounding, credit misapplied, Init in the wrong column) | high | mitigate | Independent replay of the printed rows against `evaluate_path` on three paths plus a negative control; clamp bounds from `rules`; rounding stays on the worksheet only (Pitfall 9) | closed |
| T-05-26 | Repudiation | own vs external costs mixed, making RoS disputable | medium | mitigate | Separate labelled blocks; shading from event kinds; replay checks own spend equals `security_spend` | closed |
| T-05-27 | Information disclosure | tracking sheet showing weights or names | low | mitigate | Pre-wave AST guard on `booklet.py`; veil scan layers 1 and 2 | closed |
| T-05-28 | Tampering | TeX injection | low | mitigate | `tex_escape` finalize, plain-variable lint | closed |
| T-05-29 | Information disclosure | explainer printing wave weights, thresholds or which waves have recovery | medium | mitigate | Symbols only; tests that the only digits are clamp bounds, levels and recovery factors; veil scan layers 1 and 2; no wave number in the recovery section (D-26) | closed |
| T-05-30 | Tampering (integrity of rules on paper) | wording diverging from worksheet / tracking sheet (two vocabularies) | medium | mitigate | Step headings taken from `sheets.angriff`, clamp/window labels from `sheets.tracking`; equality tests | closed |
| T-05-31 | Information disclosure | `sheets.angriff` becoming reachable from the pre-wave view | low | mitigate | Deliberate: wording is generic; explicit story-profile test on every `sheets.angriff` string; existing leak test covers it | closed |
| T-05-32 | Tampering | TeX injection | low | mitigate | `tex_escape` finalize, plain-variable lint | closed |
| T-05-33 | Tampering | path traversal via asset names | medium | mitigate | Asset names are code constants; `Path(name).name == name` check; content never names files (V12) | closed |
| T-05-34 | Repudiation / integrity | an image change not reflected in the stamp (stale PDFs look fresh) | high | mitigate | Asset bytes in `content_hash`; `content/assets/images` in `DATA_INPUTS` and `BUILD_INPUTS`; TeX read-guard test allows only hashed files | closed |
| T-05-35 | Information disclosure | story documents naming an attack, or image file names / XMP in the PDF | high | mitigate | Story-profile giveaway lint (`planspiel texts`), veil scan layers 1 and 2, metadata test; images embedded without file names (research probe) | closed |
| T-05-36 | Tampering / Elevation of privilege | TeX injection via mail headers (`"`, `<`, `>`) | medium | mitigate | `tex_escape` finalize (`\textquotedbl{}`), plain-variable lint, render test on the real `kopf` values | closed |
| T-05-37 | Denial of service | large PNGs slowing the build | low | accept | 3.7 MB PDF, byte-identical builds measured by research; bounded TeX driver | closed |
| T-05-38 | Tampering (integrity of results) | practice block leaking into enumeration, base losses, gate or digests | high | mitigate | Top-level block read only by `practice.py`; equality test of all real config fields and `base_losses` with and without the block; characterization and enumeration tests; `planspiel gate` output unchanged | closed |
| T-05-39 | Information disclosure | practice weights or bonus measures hinting at a real attack | high | mitigate | Validator rejects equal weights (ordered and multiset) and shared bonus measures; the story side is covered in 05-12 (T-05-50) | closed |
| T-05-40 | Tampering (integrity of printed numbers) | worked example diverging from the rules (wrong rounding or clamp teaches the wrong rule) | high | mitigate | Values from `rules.path_trace` via `check_example`; independent replay; pinned golden; mutation test (changed practice weight changes the E-value line); build guards for Fall 3, bonus met/missed, recovery, exact half, clamp | closed |
| T-05-41 | Tampering | template refactor changing the real worksheets | medium | mitigate | Pinned SHA-256 of the three real worksheet `.tex` files, recorded before the refactor | closed |
| T-05-42 | Tampering / Elevation of privilege | TeX injection via practice texts | low | mitigate | `tex_escape` finalize, plain-variable lint, strict digit lint | closed |
| T-05-43 | Information disclosure | facilitator booklet handed out with player material | high | mitigate | `spielleitung-` job prefix (audience registry), separate PDF, facilitator-only notice on page 1, not in any pre-wave list (V4) | closed |
| T-05-44 | Tampering (integrity of answer keys) | keys diverging from the simulation or using the static reference plan | high | mitigate | Keys from `rules.path_trace` on the legal paths pinned in 05-14 (`evaluate_path` enforces the Kurswechsel, Pitfall 10); independent replay; pinned `answer_keys.json`; build guard on illegal or out-of-budget paths | closed |
| T-05-45 | Tampering | final-index weights with two sources after the move | medium | mitigate | Defaults removed from `rules.final_index`; config required and validated; caller wiring test; outputs proven identical (goldens, summaries, slow digests) | closed |
| T-05-46 | Repudiation / integrity | a clues change not reflected in the stamp | high | mitigate | `content/clues.toml` in `DATA_INPUTS`/`BUILD_INPUTS`; `check_clues` at print time; stamp test moved knowingly (F15) | closed |
| T-05-47 | Tampering | approximated values presented as exact on player material | medium | mitigate | `format_approx` used only in `master.py` (and the console output of 05-14); test that `≈` appears in no other PDF; explicit hint on the sheet | closed |
| T-05-48 | Tampering / Elevation of privilege | TeX injection via clue quotes or reasons | low | mitigate | `tex_escape` finalize, plain-variable lint, `check_clues` at print time | closed |
| T-05-49 | Denial of service | long-running candidate search | low | accept | One-off command, bounded by the measured enumeration times (about 5 minutes per tier); not part of the default suite | closed |
| T-05-50 | Information disclosure | practice story hinting at a real attack | high | mitigate | Story-profile giveaway lint on `practice.*`; strict digit lint; veil scan of `uebung-welle-0` (no real triple, names, revealed strings); user review at the D-16 checkpoint before commit | closed |
| T-05-51 | Tampering (integrity of printed numbers) | trace values diverging from the simulation, or an example that does not show the taught mechanics | high | mitigate | `path_trace` reuses `evaluate_path` and the rules primitives (no duplicated formula), equality tests against `evaluate_path` on three path kinds and against the independent worksheet replay; `check_example` guards for Fall 3, bonus met/missed, recovery, exact half, clamp | closed |
| T-05-52 | Tampering (integrity of answer keys) | a reference path that is illegal, out of budget, lacks the swap or a voluntary move, or differs from what the user approved (Pitfall 10: static plan as key) | high | mitigate | Candidates only from `rules.evaluate_path`-legal paths; validator for references and ranges; real-config tests for legality, budget, swap window, voluntary move and mechanics; paths pinned verbatim from the recorded checkpoint answer; 05-15 adds a build guard | closed |
| T-05-53 | Tampering (integrity of printed numbers) | approximated values rounded the wrong way or shown as exact | medium | mitigate | `format_approx` via `rounding.round_half_away_frac`, exact text when the value terminates, tests for both signs and for exact values; registered in `FORMULA_FUNCTIONS` | closed |
| T-05-54 | Repudiation / integrity | stale or dirty committed PDFs | high | mitigate | D-19 commit order with a clean-tree gate; manifest `"dirty": false`; `--check` exit 0; byte-identical second build | closed |
| T-05-55 | Tampering (integrity after the rebalance) | Phase 6 changing X, weights or slopes while answer keys, Welle 0 and the overspend table stay pinned to Phase 5 values | medium | mitigate | Explicit "Carried over from Phase 5" bullets on the roadmap (reference paths, final-index weights, goldens, `MAX_PENALTY_ROWS`, `≈`); the goldens and build guards fail loudly when values move | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

Evidence (L1, grep depth, 2026-10-27): every mitigation was found in `planspiel/`, `tests/` or `print/`. Examples include the `print.veil` build gate, `PREWAVE_MODULES` AST guard, `detex`, `tex_escape` finalize, `class PrintModelError`, `MAX_PENALTY_ROWS`, `check_asset_name`, `check_example`, `check_clues`, `reference_plans` validation, the pinned `answer_keys` golden and `"dirty": false` in `final_documents/generated/manifest.json`. Each plan SUMMARY's Threat Flags section confirms these as well.

Related code-review notes (05-REVIEW.md, non-blocking): WR-03 means the wave-page test cannot detect an `Overfull \vbox`, which weakens part of T-05-10 for that one page. The per-job hygiene test and fill markers still cover it. WR-05 can drop the facilitator booklet when `reference_plans` is missing, which bears on T-05-43/T-05-54 integrity. Both are tracked as review warnings, not as open threats.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01 | T-05-07 | Unchanged from Phase 4: every value passes `tex_escape`, no shell escape; this plan adds no template | user (plan approval) | 2026-10-23 |
| AR-02 | T-05-12 | `pgf` is a CTAN core package already installed; added only to the probe list; the executor never runs the MiKTeX installer (Phase 4 D-17) | user (plan approval) | 2026-10-23 |
| AR-03 | T-05-37 | 3.7 MB PDF, byte-identical builds measured by research; bounded TeX driver | user (plan approval) | 2026-10-23 |
| AR-04 | T-05-49 | One-off command, bounded by the measured enumeration times (about 5 minutes per tier); not part of the default suite | user (plan approval) | 2026-10-23 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-27 | 55 | 55 | 0 | gsd-secure-phase (orchestrator, ASVS L1 short-circuit) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-27
