# Architecture Research

**Domain:** Config-driven offline build pipeline: one JSON config feeds (a) deterministic simulation/balance enumeration and (b) LaTeX-generated print material for a live paper-based business game
**Researched:** 2026-09-29
**Confidence:** HIGH for the component split, data flow and test strategy (based on reading the existing code and print material). HIGH for reproducible-PDF behaviour (checked on this machine). MEDIUM for LaTeX/Jinja tooling details (official docs plus a local smoke test).

---

## TL;DR (opinionated)

1. **Pull the shared core out into a small package `planspiel/`**: `config.py` (load + validate), `rules.py` (every formula, pure functions), `printmodel.py` (derived values the documents print), `texts.py` (German prose), `fmt.py` (German number formatting + LaTeX escaping), `render.py` (Jinja + lualatex). The root scripts (`simulate_outcomes.py` etc.) stay as thin CLI shims so the commands documented in CLAUDE.md/README keep working.
2. **Templates only format values. They never calculate.** Every number that appears on paper is computed in `printmodel.py` by calling `rules.py`. This covers derived values like `31 = e_threshold + mitigation_cap`, `160.000 € = base_severity × s_unit`, `620.000 € = Σ base damage` and the KZ slope. An **equivalence test** evaluates the printed hand-calculation steps against `rules.resolve_attack()` over a dense input grid.
3. **Numbers and mechanics stay in `simulation_config.json`. All German player-facing prose moves to `content/texte.toml`**, keyed by the same ids (stdlib `tomllib`, supports multiline strings and comments). Effect lines that contain numbers ("Gesamtbudget −20.000 €") are **generated from event type + params**, never written by hand.
4. **Veiling is enforced by construction.** Pre-attack documents get a view model that has no access to revealed attack names. A render test greps pre-attack `.tex` output for revealed names and attack ids.
5. **Output:** `build/` (gitignored) holds rendered `.tex`, aux files, logs and enumeration output. Final PDFs are **committed** to `final_documents/generated/` with a `manifest.json` of input hashes. Builds use a fixed `SOURCE_DATE_EPOCH`, so PDFs are byte-identical when inputs are unchanged (checked locally). Git therefore only shows a PDF change when the content actually changed.
6. **Single entry point: `python build.py {check|balance|docs|all}`**, run from a project `.venv`. Warning: on this machine `python` resolves to **Inkscape's bundled 3.12 without packages**. `python3` is the Store 3.11 that has jinja2/pytest.
7. **Build order:** harness + extraction with characterization tests → validator → mechanics changes (TDD) → text split → print pipeline proven on the attack worksheet → remaining documents → rebalance → retire legacy docx/pptx generators.

---

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           SOURCES (hand-edited)                          │
│  simulation_config.json        content/texte.toml       print/           │
│  numbers, ids, mechanics,      German prose keyed by    planspiel.sty    │
│  event types+params            config ids (veiled /     templates/*.j2   │
│                                revealed / narrative)                     │
└──────────────┬─────────────────────────┬───────────────────────┬─────────┘
               │                         │                       │
               ▼                         ▼                       │
┌──────────────────────────┐  ┌──────────────────────┐           │
│ planspiel/config.py      │  │ planspiel/texts.py   │           │
│ load → frozen dataclasses│  │ load TOML, id-cover- │           │
│ validate(): refs +       │  │ age vs config, digit │           │
│ hand-calc invariants     │  │ lint on narratives   │           │
└──────────────┬───────────┘  └──────────┬───────────┘           │
               │ Config                  │ Texts                 │
               ▼                         │                       │
┌──────────────────────────┐             │                       │
│ planspiel/rules.py       │  ONE copy of every formula:         │
│ cia, e_value, bonus,     │  used by the sim AND by the         │
│ resolve_attack, recovery,│  print model (never duplicated)     │
│ evaluate_event, effect   │                                     │
│ text, overbudget penalty,│                                     │
│ security_spend, ros,     │                                     │
│ final_index              │                                     │
└───────┬──────────────────┘                                     │
        │                  \                                     │
        ▼                   ▼                                    │
┌─────────────────────┐  ┌─────────────────────────────────┐     │
│ planspiel/          │  │ planspiel/printmodel.py         │     │
│ enumerate.py        │  │ per-document view models,       │     │
│ streaming generator │  │ audience-scoped (PRE_ATTACK /   │     │
│ over all selections │  │ REVEAL / FACILITATOR); derived  │     │
│ → aggregates        │  │ constants + worked example      │     │
└───────┬─────────────┘  └───────────────┬─────────────────┘     │
        │                                │ + planspiel/fmt.py    │
        ▼                                ▼   (de-DE numbers,     │
┌─────────────────────┐  ┌─────────────────────────────────┐    │
│ build/balance/      │  │ planspiel/render.py             │◄───┘
│ report.md/.json,    │  │ Jinja (LaTeX-safe delimiters,   │
│ optional .jsonl     │  │ StrictUndefined, finalize=esc)  │
│ (gitignored)        │  │ → build/tex/*.tex → lualatex    │
└─────────────────────┘  └───────────────┬─────────────────┘
                                         ▼
                         ┌─────────────────────────────────┐
                         │ final_documents/generated/*.pdf │
                         │ + manifest.json (input hashes)  │
                         │ committed, byte-reproducible    │
                         └─────────────────────────────────┘

  build.py  ── orchestrates:  check → balance → docs   (all = everything)
  tests/    ── pytest: rules goldens, validator, print≡sim equivalence,
               render/veiling, worked example, (opt.) latex smoke
```

Data flows **one way only**: sources → core → outputs. Nothing downstream is ever read back as input. The committed PDFs and the manifest are the only generated artifacts in git.

### Component Responsibilities

| Component | Owns | Must NOT | Talks to |
|-----------|------|----------|----------|
| `simulation_config.json` | Every number, every id, event `type` + params, bonus relations, dependencies | Contain player-facing prose with numbers in it | read by `config.py` only |
| `content/texte.toml` | German prose: measure focus/description/level texts, attack `veiled_*` / `revealed_*` texts, event narratives, sheet headings/instructions | Contain game numbers (lint-enforced) or mechanics | read by `texts.py` only |
| `planspiel/config.py` | JSON → frozen dataclasses (reuse today's `Attack`, `Wave`, `Measure`, `Event`… from `simulate_outcomes.py:10-73`); `validate(cfg) -> list[Issue]` | Compute game results | `rules`, `printmodel`, `enumerate` |
| `planspiel/rules.py` | All formulas as pure functions over `Config` + `selection` | Do I/O, formatting or text | `enumerate`, `printmodel`, `balance_analysis.py` |
| `planspiel/enumerate.py` | Iterate all selections, apply `rules`, **stream** compact records; aggregate (mean/percentiles/best in- vs over-budget) | Hold results in memory or write one giant JSON by default | `rules`; writes `build/balance/` |
| `planspiel/texts.py` | Load TOML; coverage check (every config id has text and vice versa); narrative digit lint; `{param}` placeholder fill | Know about LaTeX | `printmodel` |
| `planspiel/printmodel.py` | One `build_<doc>_model()` per document. Computes **all** derived numbers via `rules`. Picks the audience-appropriate text. Also the worked example | Format for LaTeX, or do arithmetic that `rules` doesn't own | `rules`, `texts`, `config` |
| `planspiel/fmt.py` | `eur_k(20) → "20.000 €"`, `dec(0.4) → "0,4"`, `signed(-5) → "−5"`, `latex_escape()`. Knows the config money unit is 1.000 € | Use `locale` (unreliable on Windows) | used as Jinja filters |
| `planspiel/render.py` | Jinja env; render → `build/tex/`; run lualatex with pinned env; copy PDF; write manifest | Decide content | `printmodel`, `fmt`, filesystem |
| `print/planspiel.sty` | Layout macros (`\measurecard`, `\eventcard`, `\worksheetcase`…), colors (level/wave colors), fonts, card geometry | Contain game numbers | included by every template |
| `print/templates/*.tex.j2` | Document structure; loops over model rows; calls sty macros | Do arithmetic (`\VAR{a+b}` is banned) | receives a model object only |
| `build.py` | CLI: `check`, `balance`, `docs [--only X]`, `all` | Contain logic beyond wiring | everything above |
| Root shims `simulate_outcomes.py`, `balance_analysis.py`, `analyze_simulation_results.py` | Keep the documented CLI commands working | Keep their own formula copies | import from `planspiel` |

---

## Recommended Project Structure

```
security-planspiel/
├── simulation_config.json          # numbers + ids + mechanics (role unchanged)
├── content/
│   └── texte.toml                  # ALL German player-facing prose, keyed by config ids
├── planspiel/                      # NEW shared core (small package, no framework)
│   ├── __init__.py
│   ├── config.py                   # load + validate (dataclasses moved from simulate_outcomes.py)
│   ├── rules.py                    # every formula, pure (moved from simulate_outcomes.py + new rules)
│   ├── enumerate.py                # streaming enumeration + aggregates (from run_simulation)
│   ├── texts.py                    # TOML load, coverage + lint, placeholder fill
│   ├── printmodel.py               # per-document view models, derived constants, worked example
│   ├── fmt.py                      # German formatting + LaTeX escape (Jinja filters)
│   └── render.py                   # Jinja env, lualatex driver, manifest
├── print/
│   ├── planspiel.sty               # shared layout macros, colors, fonts
│   └── templates/
│       ├── angriff.tex.j2          # rendered 3x (one per wave): REVEAL audience
│       ├── massnahmenkarten.tex.j2 # 10 measures x 3 levels: PRE_ATTACK audience
│       ├── eventkarten.tex.j2      # per-wave events + final events (Budget Review)
│       ├── budget.tex.j2           # tiers table + planning grid
│       ├── ros.tex.j2              # RoS + Final-Index sheet (replaces "Return on Security…docx")
│       ├── tracking.tex.j2         # team tracking sheet (replaces whiteboard write-up)
│       └── so_funktionierts.tex.j2 # how-it-works + worked example
├── build.py                        # SINGLE entry point
├── simulate_outcomes.py            # thin shim → planspiel.enumerate (keeps documented CLI)
├── balance_analysis.py             # imports planspiel.rules instead of simulate_outcomes internals
├── analyze_simulation_results.py   # uses rules.ros / rules.final_index (no own RoS copy)
├── requirements.txt                # jinja2, pytest (+ python-docx/pptx only while legacy lives)
├── tests/
│   ├── test_rules.py               # golden values per formula (TDD for new rules)
│   ├── test_characterization.py    # pins CURRENT outcomes before refactor/rule changes
│   ├── test_config_validate.py     # real config passes; broken fixtures fail
│   ├── test_print_equivalence.py   # printed hand-steps == rules, dense grid
│   ├── test_mechanic_coverage.py   # every sim step has a printed home
│   ├── test_render.py              # all templates render (StrictUndefined), numbers present, veiling
│   ├── test_worked_example.py      # pinned golden run shown on how-it-works sheet
│   └── test_latex_smoke.py         # @pytest.mark.latex: compile all; skipped if no lualatex
├── build/                          # GITIGNORED: tex/, aux, logs, balance/
└── final_documents/
    ├── generated/                  # COMMITTED generated PDFs + manifest.json (never hand-edit)
    └── …                           # hand-authored props stay here (Mails, Zeitungsartikel, Steckbrief, intro deck)
```

### Structure Rationale

- **`planspiel/` package instead of more root scripts:** today each script parses the JSON itself (`simulate_outcomes.py:76`, `generate_from_template.py:197`, `generate_pptx_cards.py:203`, `generate_attack_calculator.py:15` via a bare relative path, `analyze_simulation_results.py:15`), and RoS base losses are recomputed separately in `analyze_simulation_results.py:12-23`. A print generator added as script #7 would be a 7th copy. One importable core is the smallest structure that lets sim, print and tests share code. It is 7 flat modules with no layering framework, so it is not over-engineering.
- **Root shims kept:** CLAUDE.md, README and the user's workflow all reference `simulate_outcomes.py --budget-tier … --budget-utilization …`. Breaking those commands costs more than a 10-line shim.
- **`content/` separate from config:** ~150 lines of German measure prose are currently **hardcoded in Python** (`generate_pptx_cards.py:39` `MEASURE_META`, `:196` `ATTACK_NAMES`). Veiled/revealed variants will roughly double the text volume. JSON has no multiline strings or comments. TOML (stdlib `tomllib`, Python ≥3.11) has both and needs no dependency. Keeping prose out of the config also keeps balance diffs readable.
- **`print/planspiel.sty` + thin templates:** TeX layout logic (card geometry, colors) lives in plain LaTeX that can be edited and tested in any TeX editor. Jinja only does loops and value insertion. This keeps templates readable and avoids fighting Jinja-vs-TeX brace syntax in complex layout code.
- **`final_documents/generated/` subfolder:** it makes the boundary between generated (never hand-edit) and hand-authored props (emails, newspaper article, company profile, intro deck) visible in the filesystem. CONCERNS.md flagged this boundary as unclear.

---

## Architectural Patterns

### Pattern 1: Single calculation module, print model derives everything

**What:** `rules.py` is the only place a formula exists. `printmodel.py` builds a typed model per document by calling `rules`. Templates receive fully computed values and only format them.

**Why it matters here (verified against the current worksheets):** the printed worksheets do **not** print config values directly. They print **derived** values that are currently computed by hand:

| Printed on `Angriff-1_Ransomware.docx` | Derivation | Config fields |
|---|---|---|
| `Fall 2: Gesamtreduktion ≥ 31` | `e_threshold + mitigation_cap` = 23 + 8 | waves[0].e_threshold, attacks.ransomware.mitigation_cap |
| `Schaden: 160.000 €` | `base_severity × s_unit × 1000` = 8 × 20 | attacks.ransomware |
| `Schaden = (31 − GR) × 20.000 €` | a rearrangement of `(base_sev − (GR − thr)) × s_unit`. **Only valid while `base_severity == mitigation_cap`** (currently 8/8, 10/10, 7/7) and `severity_multiplier == 1.0` | attacks.*, budget_tiers.*.severity_multiplier |
| `KZ = (GR − 23) × 2 − 6` | slope `(kz_full_mit − kz_full_dmg) / cap` = 16/8 | attacks.ransomware |
| Wave 3: `KZ = −7 + (GR − 25) / 7 × 17` | slope 17/7 ≈ 2.43, **not hand-friendly** | attacks.exfil |
| RoS sheet: `Vermiedener Schaden = 620.000 − …` | `Σ base_severity × s_unit` = 160+320+140 | all attacks (today recomputed separately in `analyze_simulation_results.py:22`) |

These hidden invariants are exactly what the manual print-sync trap breaks. For example, a rebalance that changes `base_severity` without changing `mitigation_cap` silently makes the printed Fall-2 "0 €" false.

**Example:**
```python
# planspiel/printmodel.py
@dataclass(frozen=True)
class AttackWorksheet:
    wave_no: int
    title: str                 # revealed name (REVEAL audience)
    narrative: str
    weights: dict[str, float]  # printed as "x 0,4"
    bonus_rows: list[BonusRow]
    lower: float               # Fall 1: GR <= lower
    upper: float               # Fall 2: GR >= upper
    full_damage_k: float
    s_unit_k: float
    kz_full_damage: float
    kz_full_mitigation: float
    kz_slope: float
    recovery_rows: list[RecoveryRow]   # printed if attack.allow_recovery

    def hand_calc(self, gr: float, recovery: float) -> tuple[float, float]:
        """Replays EXACTLY the steps printed on paper (case 1/2/3)."""
        if gr <= self.lower:   dmg, kz = self.full_damage_k, self.kz_full_damage
        elif gr >= self.upper: dmg, kz = 0.0, self.kz_full_mitigation
        else:
            dmg = (self.upper - gr) * self.s_unit_k
            kz = self.kz_full_damage + (gr - self.lower) * self.kz_slope
        return dmg * (1 - recovery), kz

def build_attack_worksheet(cfg, texts, wave) -> AttackWorksheet:
    a = cfg.attacks[wave.attack_id]
    return AttackWorksheet(
        lower=wave.e_threshold,
        upper=wave.e_threshold + a.mitigation_cap,
        full_damage_k=rules.full_damage(a, cfg.severity_multiplier),
        kz_slope=rules.kz_slope(a),
        ...)
```

**Trade-offs:** there is one more module to maintain. In exchange, the printed formula can no longer drift from the sim without a test failing.

### Pattern 2: Hand-calculability invariants as config validation

**What:** `config.validate()` returns issues for anything that would make the printed material wrong or impossible to calculate by hand. `build.py check` fails on errors. It also runs as a pytest on the real config.

**Checks to implement:**
- Referential: `waves[].attack_id ∈ attacks`, `bonus_measures[].measure ∈ measures`, dependency and event measure refs exist, every event `type` is known to `rules`
- Print invariants: `base_severity == mitigation_cap` for every attack (or the print model must print the general formula); `severity_multiplier == 1.0` unless the worksheet prints it; wave weights sum to 1.0 with at most 1 decimal; recovery factors at most 1 decimal
- Hand-calc: `kz_slope` is representable with at most 1 decimal (**wave 3's 17/7 fails today**). Treat this as a warning until the rebalance phase, then promote it to an error
- Text coverage: every measure, attack, event and final event id has text in `texte.toml`, and there are no orphan text keys

**Decision to raise with the user (do not decide silently):** since hand-calculability is a *hard* criterion, consider parametrizing attacks in the printed quantities. That means storing `kz_per_point` (the slope) instead of `kz_at_full_mitigation`, and deriving full-mitigation KZ = `kz_at_full_damage + kz_per_point × cap`. Nice numbers are then guaranteed by construction instead of by validation. The cost is a schema change touching `rules`, the config and the characterization tests.

### Pattern 3: Mechanics as data, effect text generated from mechanics

**What:** an event's `type` + params are the single source for both `rules.evaluate_event()` (the sim) and `rules.describe_effect()` (printed effect lines and tier tables). Put both in the same module and dispatch on the same `type`, so a new event type fails fast in both places. `texte.toml` holds only the **narrative** ("Der CFO verkündet ein konzernweites Sparprogramm"). It may reference params only via placeholders (`{budget_delta}`), which are filled by `fmt`.

**Why:** today's config descriptions duplicate params in prose. Examples: `"OPEX -2.000 EUR pro aktiver Massnahme"` alongside `opex_per_measure: -2`, and the whole Budget Review tier table written out in `final_events[0].description`. Each of these is a latent print/sim mismatch. For the new linear over-budget penalty, the printed rule ("−X KZ je angefangene 10.000 € Überschreitung") must come from the same params the sim uses.

**Example:**
```python
# planspiel/rules.py
def evaluate_event(ev, selection, remaining_budget=None) -> EventEffect: ...
def effect_rows(ev) -> list[EffectRow]:
    """Condition → KZ/budget/opex rows for printing, e.g. M7 L0 → −5, L1 → 0 …"""
```
A test builds a matching selection for each printed `EffectRow` and asserts that `evaluate_event` returns exactly that row's value.

### Pattern 4: Audience-scoped view models (veiling by construction)

**What:** each document declares an audience: `PRE_ATTACK` (measure cards, budget, how-it-works, tracking sheet, discovery), `REVEAL` (attack worksheets, wave slides) or `FACILITATOR`. `printmodel` builds a `PRE_ATTACK` model from `texts.attack(id).veiled` only. Revealed names are never in that model's reach.

**Enforcement:** `test_render.py` renders every `PRE_ATTACK` document and asserts that none of `{revealed_name, attack_id, wave.name}` occurs in the `.tex` output. Note that today's `generate_pptx_cards.py` prints mitigation relations **by attack name** on measure cards (`ATTACK_NAMES`), and the wave `bonus_measures[].description` strings contain "Ransomware"/"Datenabfluss". Those strings are fine on the REVEAL worksheet but must not leak onto measure cards.

**Open content decision (flag to the user):** mechanics must stay transparent, but attack names stay veiled. What should a measure card say about bonus relevance? Options are "Bonus bei Vorfall 1 ab Level 2", a veiled teaser, or nothing. This is an editorial decision, not an architectural one. The architecture supports any of them.

### Pattern 5: Jinja configured for LaTeX

**What:** a Jinja `Environment` with LaTeX-safe delimiters (`\VAR{…}`, `\BLOCK{…}`, `\#{…}`), `undefined=StrictUndefined` (a missing model field fails the build instead of silently printing nothing), `finalize=` a function that LaTeX-escapes every string output by default, and `trim_blocks`/`lstrip_blocks`. Jinja's `autoescape` is HTML-only and must not be relied on.

**Example:**
```python
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("print/templates"),
    block_start_string=r"\BLOCK{", block_end_string="}",
    variable_start_string=r"\VAR{", variable_end_string="}",
    comment_start_string=r"\#{", comment_end_string="}",
    line_statement_prefix="%%", line_comment_prefix="%#",
    trim_blocks=True, lstrip_blocks=True, autoescape=False,
    undefined=jinja2.StrictUndefined,
    finalize=lambda v: fmt.latex_escape(v) if isinstance(v, str) else v,
)
env.filters.update(eur=fmt.eur_k, dec=fmt.dec, signed=fmt.signed)
```
Use **lualatex + fontspec** so umlauts, `€`, `≤`/`≥` and `−` can be written directly as UTF-8. A local test compile of "Ärger 160.000 €" on MiKTeX 23.10 LuaHBTeX 1.17 succeeded.

### Pattern 6: Streaming enumeration with aggregate outputs

**What:** turn `run_simulation` (`simulate_outcomes.py:510`) into a generator that yields compact records. The balance command consumes it and computes aggregates per tier: KZ/RoS/Final-Index mean, median, p10/p90, best in-budget, best over-budget by overspend bucket, and dominance flags. It writes `build/balance/report.{md,json}`. A full dump becomes opt-in (`--jsonl`, one record per line, jq-friendly).

**Why now:** the new linear over-budget penalty requires removing the filter at `simulate_outcomes.py:539` (`total_cost > adjusted_budget: continue`). Otherwise the sim never tests the loophole the rule is meant to close. Existing filtered outputs are already 131–361 MB (`sim_low/med/high.json` on disk). Up to 4^10 ≈ 1.05M unfiltered combinations per tier would produce multi-GB JSON. The calibration question ("over-budget never beats best in-budget") is an aggregate query anyway, so it becomes an automated gate: `balance` fails if `max(FinalIndex | over budget) ≥ max(FinalIndex | in budget)` for any tier.

---

## Data Flow

### Build flow (`python build.py all`)

```
simulation_config.json ──► config.load ──► config.validate ──✖ errors → stop
content/texte.toml ──────► texts.load ───► texts.validate(cfg) ──✖ → stop
                                  │
             ┌────────────────────┴───────────────────────┐
             ▼                                            ▼
   balance: enumerate(cfg, tier)               docs: for doc in DOCUMENTS:
     └─ rules.* per selection                     model = printmodel.build_<doc>(cfg, texts)
     └─ aggregate → build/balance/report          tex   = render(template, model) → build/tex/<doc>.tex
     └─ gate: over-budget never profitable        pdf   = lualatex(tex, env=PINNED) → build/tex/<doc>.pdf
                                                  copy  → final_documents/generated/<doc>.pdf
                                                  write → final_documents/generated/manifest.json
```

### Key data flows

1. **Number flow (config → paper):** `config` value → `rules` function (derivation) → `printmodel` field (typed float/int, config units) → `fmt` filter (German string, unit conversion k€→€) → template slot. **Unit conversion happens only in `fmt`.** The config money unit is 1.000 € (`s_unit: 20` = 20.000 €, `budget: 400` = 400.000 €).
2. **Text flow (texte.toml → paper):** narrative by id → audience filter in `printmodel` → `{param}` placeholders filled via `fmt` → `finalize` LaTeX-escape → template.
3. **Cost flow (changed by this milestone):** keep two named aggregates everywhere so nobody conflates them:
   - `security_spend = Σ init + Σ opex × waves`: the **RoS denominator** and "Gesamtkosten" on the RoS sheet
   - `budget_balance = budget + Σ event budget_delta − security_spend − Σ event opex_delta`: this feeds **Budget Review** and the over-budget penalty

   Today `simulate_outcomes.py:536` adds event OPEX into `total_cost` and the printed RoS sheet adds "Summe Event-Strafen". Both change. Whether event *discounts* (Operative Unterstützung, −2 per measure) also leave RoS is still to be confirmed (PROJECT.md). With separate aggregates it is a one-line decision either way.
4. **Freshness flow:** `manifest.json` = sha256 over {config, texte.toml, sty, templates, `planspiel/*.py`} plus a per-PDF hash. `build.py check` recomputes it and reports **stale PDFs** ("config changed, run `build.py docs`"). This replaces the discipline-only rule in CLAUDE.md.

### Reproducible PDFs (verified locally)

MiKTeX 23.10.12 / LuaHBTeX 1.17.0 on this machine: two `lualatex` runs with `SOURCE_DATE_EPOCH=<fixed>` and `FORCE_SOURCE_DATE=1` produced **identical sha256**. Two runs without them produced different hashes. So `render.py` must always set both to a fixed constant. Committed PDFs then only change in git when their content changes. `latexmk` also works from Git Bash (it uses `/usr/bin/perl`). Calling `lualatex` directly from Python avoids the Perl-on-PATH dependency when run from PowerShell, and these documents have no bibliography or cross-refs that would need latexmk's rerun logic. **Use direct `lualatex -interaction=nonstopmode -halt-on-error -output-directory=build/tex`**, with one pass (two only for a document that uses `remember picture`/refs), and print the log tail on failure.

---

## Testing: proving printed numbers equal simulated numbers

In order of value:

| Test | Asserts | Catches |
|---|---|---|
| `test_characterization.py` (write FIRST, before extraction) | Pins current `simulate_selection` outputs for ~10 representative selections × 3 tiers, plus an aggregate fingerprint of a tier enumeration | Refactor regressions when moving code into `planspiel/` |
| `test_rules.py` | Golden values per formula; TDD for `overbudget_penalty` (`−X × ceil(overspend/10)`), `ros` excluding events, `security_spend` vs `budget_balance` | Formula bugs |
| `test_config_validate.py` | Real config passes (known warnings allowed until rebalance); broken fixtures produce the expected issues | Refs/invariants breaking during tuning |
| **`test_print_equivalence.py`** | For each wave, each recovery level and GR over a dense grid (e.g. 0 → upper+5, step 0.1): `AttackWorksheet.hand_calc(gr, r) == rules.resolve_attack(...)`. Plus `ros_model.base_losses == Σ rules.full_damage`. Plus for every printed `EffectRow`, `evaluate_event(matching selection)` gives the printed value. Plus the budget tier table equals config | **Any divergence between the printed procedure and the sim**, including broken hidden invariants |
| **`test_mechanic_coverage.py`** | `rules.WAVE_STEPS` (ordered list: cia, e_value, bonus, resolve, recovery, e_target, events, clamp, final_events) ⊆ ∪ `doc.covers` over all print models | Mechanics the sim applies but no sheet tells players to apply (**currently fails for `e_target`, see below**) |
| `test_render.py` | Every template renders under StrictUndefined; key formatted values (`fmt.eur_k(model.full_damage_k)`) appear in the `.tex`; veiling grep on PRE_ATTACK docs | Missing fields, typos, name leaks |
| `test_worked_example.py` | Worked example on the how-it-works sheet (fixed example selection) equals `rules`, step by step | Stale worked example after rebalance |
| `test_latex_smoke.py` (`-m latex`) | All docs compile; PDFs non-empty | TeX breakage (slow, opt-in) |

Test at the `.tex` level, not by extracting PDF text. The `.tex` is deterministic, fast to produce and needs no poppler. The PDF compile is a separate smoke test.

### Divergence already present (found during this research)

The sim applies a per-wave **E-target KZ bonus/malus** (`simulate_outcomes.py:448-449`: `e_value >= budget_tier.e_targets[wave]` → `kz_bonus` 5/7/10, else `kz_malus` −3/−5/−7). A text search of every `final_documents/*.docx|pptx` and of `README.md` found **no printed rule for it**. Either players never applied it at MHP, or it lives only in spoken moderation. In both cases the sim's KZ numbers differ from what teams calculated. **This must be resolved in requirements:** print it (the tracking sheet is the natural place) or remove it from the sim. The mechanic-coverage test turns this class of bug into a red test.

Also note: the M4 recovery factor (×0,90/0,70/0,50) is printed on an **event slide** ("Backup & Recovery"), not on the worksheet, even though it changes the worksheet's damage result. Consider moving it onto the attack worksheet as an explicit step for attacks with `allow_recovery`.

---

## Anti-Patterns

### Anti-Pattern 1: Arithmetic in templates
**What:** `\VAR{wave.e_threshold + attack.mitigation_cap}` in a `.tex.j2`.
**Why bad:** it creates a second, untested copy of the rules, which is exactly the drift this milestone is meant to eliminate.
**Instead:** add a field to the print model and compute it via `rules`. Consider a render-test lint that forbids `+ - * /` inside `\VAR{}`.

### Anti-Pattern 2: Prose in Python, numbers in prose
**What:** `MEASURE_META` in `generate_pptx_cards.py:39`; `"Gesamtbudget -20.000 EUR"` in config descriptions.
**Why bad:** editorial edits require code changes, and numbers in prose silently diverge from params.
**Instead:** put prose in `texte.toml`, generate effect lines from `type` + params, and lint narratives for digits.

### Anti-Pattern 3: One JSON dump per tier as the balance workflow
**What:** writing hundreds of MB to GB of results and then post-processing.
**Why bad:** it doesn't scale once over-budget combos are included. CLAUDE.md already forbids reading these files whole.
**Instead:** stream plus in-process aggregates. JSONL only on request.

### Anti-Pattern 4: Several generators, several formula copies
**What:** keeping `generate_attack_calculator.py` (formulas re-encoded as Excel formulas), `generate_pptx_cards.py` and `generate_from_template.py` alongside the LaTeX pipeline.
**Why bad:** every copy is another print-sync trap, and `pptx_output/` already holds 6 ambiguous variants.
**Instead:** once each LaTeX document is accepted, move its predecessor (docx/pptx and generator) to `archive/`. Ask the user whether the xlsx calculator is still used. If it is, regenerate it from `printmodel`; if not, retire it.

### Anti-Pattern 5: Relying on bare `python`
**What:** `python build.py` in a fresh shell.
**Why bad:** on this machine `python` resolves to `C:/Program Files/Inkscape/bin/python.exe` (3.12, no jinja2/pytest/docx). `pip`/`python3` point to the Store Python 3.11, which has them. PROJECT.md's statements "Python 3.12" and "jinja2 not installed" come from this confusion.
**Instead:** create a project `.venv` from the 3.11 interpreter, add a `requirements.txt`, and document `.venv/Scripts/python build.py …`. Optionally, `build.py` can check `sys.version_info >= (3, 11)` and that jinja2 is importable, and fail with a clear message.

### Anti-Pattern 6: German number formatting via `locale`
**Why bad:** Windows locale names and availability vary, so the output is non-deterministic across machines.
**Instead:** use explicit string formatting in `fmt.py` (thousands separator `.`, decimal `,`, typographic minus `−`, `€` suffix).

---

## Suggested Build Order

Dependencies drive this order. Each step is independently verifiable.

| # | Step | Depends on | Delivers | Verify by |
|---|------|------------|----------|-----------|
| 1 | **Harness + characterization:** `.venv`, `requirements.txt`, pytest; pin current sim outputs | nothing | Safety net | Tests green on untouched code |
| 2 | **Extract core:** `planspiel/config.py`, `rules.py`, `enumerate.py`; root scripts become shims; `analyze_simulation_results.py` and `balance_analysis.py` use `rules` | 1 | One formula copy | Characterization tests still green; documented CLI commands unchanged |
| 3 | **Validator:** referential + hand-calc invariants + `build.py check` | 2 | Early failure on bad config; surfaces wave-3 slope (warning) | `test_config_validate.py` |
| 4 | **Mechanics changes (TDD):** linear over-budget penalty (new final-event type in config), `security_spend` vs `budget_balance`, RoS without event costs, drop the over-budget filter, streaming aggregates, "over-budget never profitable" gate; **resolve the E-target print gap** (print or remove) | 2 (3 recommended) | New rules in sim | `test_rules.py`; characterization tests updated **deliberately** with a documented diff |
| 5 | **Text split:** `content/texte.toml` (MEASURE_META, config descriptions, event narratives from Events pptx, veiled/revealed attack texts); `texts.py` coverage + digit lint; strip prose from config | 2 (parallel with 4) | Prose outside code/config | Coverage test; sim unaffected |
| 6 | **Print pipeline, proven on ONE document: the attack worksheet** (`fmt`, Jinja env, `planspiel.sty`, `render.py`, manifest, pinned `SOURCE_DATE_EPOCH`, `build.py docs`) | 3, 4, 5 | Removes the worst print-sync trap first | `test_print_equivalence.py`, `test_render.py`, visual print review against the old docx |
| 7 | **Remaining documents:** measure cards → event cards (incl. Budget Review with the linear rule) → budget sheet → RoS sheet → tracking sheet → how-it-works + worked example | 6 | Full print set | Mechanic-coverage test green; veiling test green |
| 8 | **Rebalance:** tune config with `build.py balance` (full enumeration aggregates), fix wave-3 slope, promote hand-calc warnings to errors, regenerate all documents | 4, 7 | Balanced, printed, consistent | Balance gate + all tests + fresh manifest |
| 9 | **Retire legacy:** move replaced docx/pptx, `pptx_output/`, `generate_pptx_cards.py`, `generate_from_template.py` (and possibly the xlsx calculator) to `archive/`; rewrite CLAUDE.md "Print-Sync-Falle" to describe the generator workflow | 7 (8) | Single pipeline | No references to legacy scripts remain |

**Ordering rationale:**
- Characterization tests (1) must come before extraction (2). There are zero tests today, and extraction touches every formula.
- Mechanics changes (4) come **before** document generation (6–7) because they change printed content: the Budget Review card, the RoS sheet and the E-target rule. Documents are then built once against the final rules. This is consistent with the PROJECT.md decision "generate docs before rebalancing": *rules* change before docs, *numbers* (rebalance) after.
- The text split (5) and mechanics (4) are independent after (2) and can run in parallel.
- The attack worksheet goes first in (6) because it carries the highest print-sync risk (hand-maintained docx with derived constants) and exercises every pipeline piece: derived values, loops over bonus rows, formula typesetting and the REVEAL audience.
- The rebalance (8) needs the gate from (4) and the generator from (7), so tuning iterations cost one command instead of manual docx edits.

**Research flags for phases:**
- Step 6/7 (card layout on A4 with cut marks, e.g. tcolorbox rasters vs a dedicated card class) needs LaTeX-package research. This belongs to STACK.md, not here.
- Step 4 needs requirement decisions first: E-target print-or-remove, whether event discounts stay out of RoS, the X value, and whether the penalty applies per started 10k with `ceil`.
- Step 8 is standard (tooling exists after 4). No extra research needed.

---

## Scalability Considerations

Users don't scale here; the content does.

| Concern | Now (10 measures, 3 waves) | +2 measures | New document type |
|---|---|---|---|
| Enumeration size | 4^10 ≈ 1.05M combos/tier; streaming keeps memory flat | 4^12 ≈ 16.8M: add per-measure precomputed CIA/cost vectors or prune dominated levels | n/a |
| Print consistency | equivalence + coverage tests | automatic (templates loop over model) | add `build_<doc>_model` + template + declare `covers`/audience |
| Build time | ~7 small lualatex compiles, seconds each | same | +1 compile |

---

## Sources

- Local code and material (HIGH): `simulate_outcomes.py` (lines 76, 206-296, 418-497, 536, 539), `generate_pptx_cards.py` (39, 196), `analyze_simulation_results.py` (12-23), text extracted from `final_documents/Angriff-{1,2,3}_*.docx`, `Budget.docx`, `Return on Security und Final Wert.docx`, `Events_Security-Game.pptx`; `.planning/PROJECT.md`, `.planning/codebase/{ARCHITECTURE,STRUCTURE,CONCERNS}.md`
- Local empirical checks, 2026-09-29 (HIGH for this environment): lualatex + `SOURCE_DATE_EPOCH` gives byte-identical PDFs on MiKTeX 23.10.12; latexmk `-outdir` works from Git Bash; interpreter resolution (`python` → Inkscape 3.12, `python3`/`pip` → Store 3.11 with jinja2 3.1.2, pytest 9.0.2, python-docx, python-pptx); `tomllib` available
- [Jinja2 API docs: Environment delimiters, finalize, StrictUndefined](https://jinja.palletsprojects.com/en/stable/api/) (LOW via webfetch seam; standard, long-stable API)
- [pdfTeX user manual: SOURCE_DATE_EPOCH / FORCE_SOURCE_DATE](https://texdoc.org/serve/pdftex/0) (MEDIUM, cross-checked by local test)
- [latexmk manual: -outdir/-auxdir, MiKTeX aux-directory](https://texdoc.org/serve/latexmk/0) and [MiKTeX issue #1598: lualatex.fmt in output directory](https://github.com/MiKTeX/miktex/issues/1598) (MEDIUM)
