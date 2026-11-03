# Coding Conventions

**Analysis Date:** 2026-11-04

## Single sources

- Numbers live only in `simulation_config.json`; prose lives only in `content/texte.toml`. Order of a content change: `simulation_config.json` -> `README.md` -> `content/texte.toml` -> `uv run planspiel print` -> `uv run planspiel print --check` -> commit `final_documents/generated/`
- The validator rejects prose in the config (`schema.prose_in_config`); the digit lint rejects digits in prose unless the exact digit string is in `content/digit_allowlist.toml`
- Game formulas have exactly one definition, in `planspiel/rules.py` (guarded by `tests/test_single_definition.py`); the root wrappers, enumeration, balance code and print models call it and never re-implement it
- Formulas stay fixed and linear (hand-calculable on the worksheets); only operands are configurable

## Arithmetic and rounding

- Exact arithmetic with `fractions.Fraction` or integer scaling for E-Wert, Gesamtreduktion, reduction over threshold and severity; damage stays exact in whole euros
- The KZ change of a wave (attack plus events) is rounded once, half away from zero (`planspiel.rounding.round_half_away`), then KZ is clamped to 0-100; the built-in `round()` is forbidden in `planspiel/rules.py` and `planspiel/rounding.py`
- RoS2 (RoS to two decimals) goes through `rules.ros_two_decimals`; the Final-Index is `weight_kz * KZ + weight_ros * RoS2`

## Print model rules

- Print models (`planspiel/printmodel.py`, `cards.py`, `booklet.py`, `wave_page.py`, `story.py`, `practice.py`, `master.py`, `schedule.py`, `debrief.py`, `was_neu.py`, `probelauf.py`) hold finished strings; templates only loop and place, they never format numbers
- Numbers reach TeX only as strings built in code; `render.tex_escape` is the Jinja `finalize` hook and rejects raw numbers and undefined names
- Every print job name carries an audience prefix (`spieler-`, `uebung-`, `angriff-`, `spielleitung-`, see `planspiel/audience.py`); an unclassified job is a build error
- Veil: player-facing pages never name an attack before its wave and never print a real wave's weights or bonus links (`planspiel/veil.py`, `content/giveaway_terms.toml`); story documents carry clues from `content/clues.toml`, never a named gap
- Every PDF carries the stamp "Stand <date> · <hash>", ending in "+lokal" for a dirty build; only a clean, committed build is committed (`planspiel/stamp.py`)
- Generated PDFs in `final_documents/generated/` are never edited by hand; `archive/` is never read by the build (`tests/test_no_archive_references.py`)

## Naming and language

- snake_case modules, functions and variables; verb-first function names (`compute_*`, `build_*`, `check_*`, `load_*`); PascalCase dataclasses and NamedTuples named after domain entities (`Wave`, `Attack`, `Measure`, `Config`)
- Domain abbreviations are used unexplained and must not be extended without a README glossary entry: `kz`, `cia`, `e_value`, `e_threshold`, `opex`, `init`, `ros`
- Code identifiers, docs and commit messages are English; all game content, print output, CLI output and test-facing messages for the facilitator are German
- Commit messages follow conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, with a phase-plan scope such as `(07-11)`)

## Testing

- TDD for rules and simulation changes: write the failing test first, commit RED, then GREEN
- pytest markers: `slow` (full enumeration), `pdf` (real LuaLaTeX builds), `balance` (design-principle checks on a chosen config); the fast suite excludes `slow` and `pdf`
- Tests use the real code and real config, no mocks for the rules; golden files in `tests/golden/` pin reference outputs
- Balance is verified by full enumeration, not by hand-picked strategies; `uv run planspiel gate` guards that overspending never pays off

## Module and comment style

- Type hints on function signatures, with builtin generics such as `tuple[str, ...]`
- Module docstrings state the requirement ID and decision IDs they implement (for example `BAL-06 (D-16)`); inline comments explain why, in German or English
- Config dataclasses are plain `@dataclass` and treated as read-only after loading; pure functions over the result store and config are preferred to stateful classes
- No linter or formatter configuration; 4-space indentation, lines kept near 110 characters by discipline
