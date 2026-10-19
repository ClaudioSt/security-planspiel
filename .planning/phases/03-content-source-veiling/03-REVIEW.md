---
phase: 03-content-source-veiling
reviewed: 2026-10-19T10:20:00Z
depth: standard
files_reviewed: 40
files_reviewed_list:
  - planspiel/texts.py
  - planspiel/cli.py
  - planspiel/config.py
  - planspiel/rules.py
  - planspiel/validate.py
  - content/texte.toml
  - content/clues.toml
  - content/digit_allowlist.toml
  - content/giveaway_terms.toml
  - content/INVENTORY.md
  - content/assets/README.md
  - content/assets/GUIDELINES.md
  - simulation_config.json
  - .gitattributes
  - tests/support/__init__.py
  - tests/fixtures/mini_config.json
  - tests/fixtures/mini_content/texte.toml
  - tests/fixtures/mini_content/clues.toml
  - tests/fixtures/mini_content/digit_allowlist.toml
  - tests/fixtures/mini_content/giveaway_terms.toml
  - tests/test_texts_loader.py
  - tests/test_texts_coverage.py
  - tests/test_texts_digits.py
  - tests/test_texts_migration.py
  - tests/test_texts_views.py
  - tests/test_texts_giveaway.py
  - tests/test_clues.py
  - tests/test_story_veil.py
  - tests/test_inventory.py
  - tests/test_config_prose_removed.py
  - tests/test_config_text.py
  - tests/test_validate.py
  - tests/test_kurswechsel.py
  - tests/test_sparprogramm.py
  - tests/test_budget_review_text.py
  - tests/test_rules_semantics.py
  - tests/test_rules_exact.py
  - tests/test_kernel_conformance.py
  - tests/test_e_target_removed.py
  - tests/test_legacy_generators_smoke.py
findings:
  critical: 0
  warning: 6
  info: 8
  total: 14
status: issues_found
---

# Phase 3: Code Review Report

**Reviewed:** 2026-10-19T10:20:00Z
**Depth:** standard
**Files Reviewed:** 40
**Status:** issues_found

## Summary

I reviewed the phase diff `609e64e..HEAD`: the content loader and lints (`planspiel/texts.py`), the `texts` and `clues` CLI subcommands, the prose strip from config/validator/rules, the four content TOML files, the inventory and assets docs, and the new and retargeted tests. Verification: `uv run pytest -q` passes (873 passed, 19 deselected). `uv run planspiel texts`, `uv run planspiel clues` and `uv run planspiel validate` all report 0 errors. `planspiel/rules.py` has no `round(` call, and the phase changes there are limited to removing the description plumbing.

The shipped content is clean today. I found no revealed attack name, bonus reason or giveaway term in anything `PreAttackView` can reach. The event rule texts and CIA rationales match the config: the weights, `wave_N` placement and event params are consistent. No BLOCKER was found.

The weak points are the guards, not the current content. I ran probes against the real terms file:
- The giveaway normalization misses several realistic spellings.
- The story-mechanics lint does no normalization and covers less than D-15 asks for.
- The leak guard for measure and sheet texts (D-06) exists only in pytest, not in `planspiel texts`.
- The new CLI commands crash with tracebacks on malformed input.

These gaps matter because Phase 5 (VEIL-02, PRINT-*) will rely on these lints as its gate.

## Warnings

### WR-01: Giveaway normalization misses split words, NFKC forms, some invisible characters and slash or underscore compounds

**File:** `planspiel/texts.py:310-339`
**Issue:** `normalize_for_matching` does NFC, maps the U+2010..U+2015 and U+2212 dashes to "-", strips only five invisible characters, and lower-cases. Probes against `content/giveaway_terms.toml` show that each of these returns `[]` in **both** profiles:
- `"Ransom-ware"`, `"Ransom ware"`, `"Daten-diebstahl"`: a hyphen or space inside a substring term breaks the match.
- `"Exﬁltration"` (U+FB01 ligature, typical in text copied from a PDF, and the Audit-Mail was transcribed from an image PDF), and fullwidth `"Ｒａｎｓｏｍｗａｒｅ"`: NFC does not fold compatibility forms.
- `"Ransom⁠ware"`: U+2060 WORD JOINER is not in `_INVISIBLE`. U+180E and U+2061..U+2064 are not either.

In the `story` profile, `"OT/Störung"`, `"OT_Störung"` and `"OT-Systemstörung"` also pass, because the compound pattern only allows `[\s-]*` between the parts and the story profile drops the bare `ot` token (D-20). On top of that, the terms themselves are only `.lower()`ed, not run through `normalize_for_matching`. A future term containing an en dash or a decomposed umlaut would never match.

**Fix:**
```python
_INVISIBLE = {code: None for code in (0x00AD, 0x180E, 0x200B, 0x200C, 0x200D, 0x2060, 0x2061, 0x2062, 0x2063, 0x2064, 0xFEFF)}

def normalize_for_matching(text: str) -> str:
    folded = unicodedata.normalize("NFKC", text).translate(_DASHES).translate(_INVISIBLE)
    return folded.lower()

# in giveaway_hits: also match substrings against a "squeezed" form without separators
squeezed = re.sub(r"[\s\-_/]+", "", normalised)
hits = {t for t in substrings if t in normalised or t in squeezed}
# compound separator: [\s\-_/]* instead of [\s-]*
# and normalise the terms with the same function: {normalize_for_matching(t) for t in terms.substrings}
```
Add the probe strings above to `BOTH_HIT` in `tests/test_texts_giveaway.py`. Check `BOTH_PASS` again afterwards, because squeezing can create false positives across word boundaries. If it does, limit squeezing to single intra-word separators.

### WR-02: Story-mechanics lint does no normalization and covers less than D-15

**File:** `planspiel/texts.py:74-83, 292-307`
**Issue:** D-15 says story texts "must not state game mechanics or game amounts (budget tiers, KZ, costs)". `check_story_mechanics` falls short in three ways:
- It runs its regexes on the raw text without `normalize_for_matching`. In probes, `"E‑Wert"` and `"Init‑Kosten"` (non-breaking hyphen) pass.
- It does not recognise the game's own level shorthand: `"L3 Maßnahmen"` passes, because only `Level\s?\d` is banned.
- It checks only budget-tier amounts, and only in the exact `format_eur` form `"350.000"`. `"350 000 €"` and `"350k€"` pass. `kz_start` values, measure Init and OPEX costs, the RoS base loss and `budget_delta` are not checked at all.

**Fix:** Normalize first, then add a level-shorthand pattern and the remaining amount forms:
```python
STORY_MECHANICS_PATTERNS = (..., re.compile(r"\bL[1-3]\b"), re.compile(r"Return on Security", re.IGNORECASE))

def _story_amounts(cfg):
    ks = {t.budget for t in cfg.budget_tiers.values()}
    # add measure init/opex totals and the base loss as needed
    for k in ks:
        yield from (format_eur(k * 1000), f"{k} 000", f"{k}k", f"{k} k", f"{k} Tsd")

text = normalize_for_matching(raw)  # then match patterns case-insensitively
```
If checking all costs gives too many false positives against world facts, record that narrowing as a decision. Right now the code checks less than D-15 states.

### WR-03: Pre-wave leak guard for measure and sheet texts exists only in pytest, with weaker normalization

**File:** `planspiel/texts.py:347-373`; `tests/test_texts_views.py:156-178`; `tests/test_story_veil.py:155-163`
**Issue:** `check_giveaway` lints veiled titles, events, final events and story texts. It does not lint `measures.*` (deliberate, D-06) or the pre-wave `sheets.{budget,ros,backup_recovery,labels}`, and both are served by `PreAttackView`. The only guard against a revealed attack name or bonus reason in those texts is the `_leaks` helper in the test suite.

The `texte.toml` header (line 8) tells authors to check with `uv run planspiel texts`. That command passes a measure or sheet text that says "Schutz vor Ransomware". The tests use only `NFC + lower()` (test_story_veil uses `lower()` alone) and exact substring matches against the revealed names. So `"OT Störung"`, `"OT‑Störung"` or `"Ransom­ware"` in a measure focus would pass the tests as well.

**Fix:** Add the check to the shipped lint so the CLI enforces D-06. Reuse the giveaway normalizer:
```python
def check_prewave_leaks(cfg: Config, texts: Texts, terms: GiveawayTerms) -> list[Issue]:
    names = [normalize_for_matching(str(texts.get(f"attacks.{a}.revealed.name"))) for a in cfg.attacks]
    reasons = [normalize_for_matching(t) for k, t in texts.strings("attacks") if ".revealed.bonus_reasons." in k]
    issues = []
    for prefix in ("measures", *(f"sheets.{n}" for n in PREWAVE_SHEETS)):
        for key, text in texts.strings(prefix):
            norm = normalize_for_matching(text)
            hits = [t for t in (*names, *reasons) if t in norm]
            hits += [h for h in giveaway_hits(text, terms, cfg.attacks, profile="story")
                     if h in {"ransomware", "exfil", "ot-stör", "ot-stoer"}]  # names/ids only, D-06 keeps technique words
            if hits:
                issues.append(Issue("error", "texts.prewave_leak", key, f"Vorab-Text nennt einen Angriff: {', '.join(sorted(set(hits)))}"))
    return issues
```
Then add it to `check_texts`.

### WR-04: `planspiel texts` and `planspiel clues` crash with tracebacks on malformed input

**File:** `planspiel/cli.py:32-85`
**Issue:** I confirmed these by running them:
- `planspiel texts --config bad.json` raises an uncaught `json.decoder.JSONDecodeError`. `_validate_command` catches it, the new commands only catch `OSError` and `TOMLDecodeError`. A config that fails validation behaves the same way, because `load_config` raises.
- An allowlist entry without `key` raises `KeyError: 'key'` (`load_allowlist`, texts.py:174). A `compounds` pair of the wrong length raises `ValueError` (texts.py:186).
- `planspiel clues` with a `texte.toml` that lacks `attacks.ot.veiled.title` raises `KeyError`, because `_clues_command` renders `FacilitatorView.clue_matrix()` before any coverage check.
- The error prefix is wrong in some cases: `_clues_command` prints `ERROR clues.toml <path>` even when `texte.toml` or the config was the file that failed.

**Fix:** Catch `json.JSONDecodeError`, `KeyError`, `ValueError` and `TypeError` around loading, and name the file that actually failed. In `_clues_command`, run `check_coverage` (or `check_texts`) first and skip the matrix when there are errors:
```python
except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError, KeyError, ValueError, TypeError) as error:
    print(f"ERROR content.load {content_dir}: {error!r}")
    print("1 Fehler, 0 Warnung(en)")
    return 1
...
coverage = check_coverage(cfg, texts)
if not coverage:
    print(format_clue_matrix(FacilitatorView(cfg, texts, clues).clue_matrix()))
issues = [*coverage, *check_clues(cfg, texts, clues)]
```

### WR-05: Budget sheet text contradicts itself and the current Init rule

**File:** `content/texte.toml:244, 248`
**Issue:** `sheets.budget.init_when = "Einmal zu Spielbeginn"` says Init is due once at the start. Four lines later, `sheets.budget.anticipated_sum_intro` says Init is also due on upgrades. RULE-02 and the Kurswechsel rule (`events.kurswechsel.rule`) also charge Init in change windows. `PreAttackView.sheet("budget")` serves both strings. INVENTORY.md records this as deferred to PRINT-07, but the content source is now the single source of truth. Nothing fails if PRINT-07 prints the key unchanged, which goes against the project's core value of unambiguous rules.

**Fix:** Correct the text now. For example: `init_when = "Bei Einführung einer Maßnahme und bei jedem Level-Upgrade (auch im Change-Fenster)"`. Alternatively, add a failing-until-fixed marker test that PRINT-07 has to resolve.

### WR-06: The prose guard in the config validator is a four-key denylist

**File:** `planspiel/validate.py:121-127, 307-308, 332-333, 359-360, 441-442`; `planspiel/config.py:91`
**Issue:** D-02 strips prose from `simulation_config.json`, but the validator only rejects `attacks.*.description`, `waves[].name`, `bonus_measures[].description` and `events[].description`. There is no unknown-key check. Prose can come back unflagged, for example as `measures.M1.description`, `attacks.ot.name` or `budget_tiers.low.description`. For events, `_build_event` silently moves any extra key (e.g. `narrative`, `rule`) into `params`, where nothing reads it.

**Fix:** Validate each entity against an allowlist of known keys, and report everything else as `schema.unknown_key`. Report known prose names (`description`, `name` where not allowed, `narrative`, `rule`, `text`) as `schema.prose_in_config`. For events, derive the allowed param keys from the event type that `validate.py` already checks.

## Info

### IN-01: `check_clues` counts a clue before validating it

**File:** `planspiel/texts.py:516-527`
**Issue:** `counts[...] += 1` and `documents[...].add(...)` run before the pre-wave, source and quote checks. An invalid clue therefore still counts toward the two-clue and two-document minimum, which hides `clues.too_few` and `clues.single_source` until it is fixed. The run still fails, so this only affects diagnostics. A clue with only `attack` set reports only `clues.not_prewave`, not its empty quote or reason.
**Fix:** Increment the counters only after the clue passes all checks, and stop using `continue` so that every problem with a clue is reported.

### IN-02: Line-ending attribute does not cover the fixture TOMLs; a BOM gives a cryptic error

**File:** `.gitattributes:5`
**Issue:** `content/*.toml text eol=lf` does not match `tests/fixtures/mini_content/*.toml` (`git check-attr` shows no attributes there) or any future nested `content/**/*.toml`. This machine has `core.autocrlf=true`. `tomllib` normalizes CRLF (verified), so behaviour is unaffected, but the stated "UTF-8 with LF" invariant is not enforced. A UTF-8 BOM, which Windows editors sometimes add, makes `tomllib` fail with "Invalid statement (at line 1, column 1)".
**Fix:** Use `content/**/*.toml text eol=lf` and `tests/fixtures/**/*.toml text eol=lf`. Optionally detect a leading `\xef\xbb\xbf` in `load_texts` and report it clearly.

### IN-03: INVENTORY.md is stale after 03-03

**File:** `content/INVENTORY.md:21, 24, 31`
**Issue:** The rows still say "verbatim and un-veiled; veiling in plan 03-03" and "including the stray hyphen in 'Beratungs-projekt'". `texte.toml` is now veiled and reads "Beratungsprojekt" (line 478). The file was last touched in b917395 (03-01).
**Fix:** Update the Target column to describe the veiled state and the 03-03 edits.

### IN-04: Inventory target check uses a loose prefix match

**File:** `tests/test_inventory.py:105-112`
**Issue:** `any(key.startswith(match.group(1)) ...)` accepts `measures.M1` because `measures.M10.*` exists, and it would accept truncated targets such as `story.s`.
**Fix:** Require `key == target or key.startswith(target + ".")`.

### IN-05: `generate_attack_calculator.py` now always fails, and the smoke test only imports it

**File:** `tests/test_legacy_generators_smoke.py:17-22`; `generate_attack_calculator.py:45, 83, 464`
**Issue:** This is accepted under D-07 and recorded in 03-01-SUMMARY, but `CLAUDE.md` still lists the script as a print-material generator, and running it raises `KeyError: 'name'`.
**Fix:** Add a note to CLAUDE.md's script list ("broken since Phase 3, archived in LEG-01") so nobody runs it expecting output.

### IN-06: The `PreAttackView` "no access" guarantee is by convention only

**File:** `planspiel/texts.py:388-396`
**Issue:** The docstring says the view gives no access to `attacks.<id>.revealed`, but `view._texts` holds the full `Texts`, and Phase 5 renderers could read revealed keys through it.
**Fix:** Have the constructor keep a deep copy with every `attacks.*.revealed` subtree removed (and `sheets.angriff`), so the guarantee holds structurally.

### IN-07: Sparprogramm effect label format differs from the other money formatting

**File:** `planspiel/rules.py:295`
**Issue:** `f"Gesamtbudget {p['budget_delta']}k€"` produces `"Gesamtbudget -20k€"` with an ASCII hyphen, and a positive delta gets no `+`. `review_text.format_eur` uses U+2212. This is a simulation label, not print text (D-24), so the effect is cosmetic.
**Fix:** Use a signed format (`f"{delta:+d}k€"`), or reuse `format_eur` when PRINT-06 builds the card lines.

### IN-08: About 3.7 MB of PNG duplicates stored as regular git blobs

**File:** `content/assets/images/zeitungsartikel_bild_{audit,fabrik}.png`
**Issue:** These are byte-identical copies of the files in `final_documents/` and are not tracked by LFS, even though the repo uses LFS for large artifacts.
**Fix:** Add `content/assets/images/*.png filter=lfs diff=lfs merge=lfs -text`, or accept the duplication until LEG-01 removes the originals.

---

_Reviewed: 2026-10-19T10:20:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
