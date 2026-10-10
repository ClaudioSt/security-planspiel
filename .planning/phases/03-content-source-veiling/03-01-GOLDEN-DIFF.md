# Plan 03-01: text-only golden change (D-08, D-25)

Status: awaiting the user's decision at the Task 6 checkpoint. No golden file has been rewritten; the Task 4
changes (prose-free config and code) are in the working tree, uncommitted.

## Classifier (`tools/golden_text_diff.py`)

`uv run python .planning/phases/03-content-source-veiling/tools/golden_text_diff.py` rebuilds every golden case in
memory (as `test_golden_sample_matches` does) and compares it with `tests/golden/characterization_<tier>.json` on disk.
Allowed differences: `wave_name` and `bonus_descriptions` disappear, the Sparprogramm `effect_description` becomes the
label generated from the config. Everything else must be identical. Exit code 0.

```text
generated Sparprogramm label: Gesamtbudget -20k€

== low ==
valid cases: 59 of 62
wave_name: 177
bonus_descriptions: 220
sparprogramm_label: 59
unexpected: 0

== medium ==
valid cases: 58 of 61
wave_name: 174
bonus_descriptions: 217
sparprogramm_label: 58
unexpected: 0

== high ==
valid cases: 60 of 63
wave_name: 180
bonus_descriptions: 225
sparprogramm_label: 60
unexpected: 0
```

`wave_name` is 3 per valid case (three waves), `sparprogramm_label` is 1 per valid case, `bonus_descriptions` counts
the list field plus its elements. No differing field falls outside the three patterns.

## Slow checks, run without `--update-golden`

| Check | Result | Runtime |
|-------|--------|---------|
| `uv run pytest -m slow tests/test_digest.py -q` (all dependency-valid combinations per tier) | 3 passed, 1 deselected | 451 s (7 min 31 s) |
| `uv run pytest -m slow tests/test_overspend_gate.py -k matches_golden -q` | 3 passed, 38 deselected | 114 s (1 min 54 s) |

The digest goldens (numbers, damage, costs, kz-after over all combinations) and the gate goldens are therefore
byte-identical; only the three text fields changed.

## Generated label

The simulation label of the Sparprogramm event is now built from the event params:
`Gesamtbudget -20k€` (before: the config description "Der CFO verkündet ... Gesamtbudget -20.000 EUR. ...").
Prose in the config is now a validator error (`schema.prose_in_config`).

## Digit allowlist (`content/digit_allowlist.toml`, to be reviewed, D-25)

| Key | Token | Why |
|-----|-------|-----|
| `measures.M2.levels_desc.1` | `30 Tage` | Aufbewahrungsdauer der Protokolle, kein Spielparameter |
| `measures.M2.levels_simple.1` | `30 Tage` | Dieselbe Aufbewahrungsdauer in einfacher Sprache |
| `measures.M2.levels_desc.3` | `24/7` | Betriebszeit des SOC (rund um die Uhr), kein Spielparameter |
| `measures.M4.levels_desc.1` | `14 Tage` | Aufbewahrungsdauer der Backups, kein Spielparameter |
| `measures.M4.levels_desc.2` | `3-2-1` | Name der Backup-Regel (3-2-1-Regel), keine Spielzahl |
| `measures.M4.levels_desc.3` | `<4h` | Wiederanlaufziel (RTO) als Fachbegriff, kein Spielparameter |
| `measures.M6.levels_desc.1` | `30 Min` | Dauer des E-Learnings, kein Spielparameter |

Review flag: `14 Tage`, `30 Tage`, `<4h` and `30 Min` look like parameters although none of them is in the config.
The alternative (German number words) would break the 1:1 carry of the measure texts (D-05).

## `git status --short` at the time of this report

```text
 M .claude/settings.local.json     (unrelated user change, never staged)
 M .planning/STATE.md              (orchestrator state, not part of this plan)
 M planspiel/config.py
 M planspiel/rules.py
 M planspiel/validate.py
 M simulation_config.json
 M tests/fixtures/mini_config.json
 M tests/test_budget_review_text.py
 M tests/test_config_text.py
 M tests/test_e_target_removed.py
 M tests/test_kernel_conformance.py
 M tests/test_kurswechsel.py
 M tests/test_legacy_generators_smoke.py
 M tests/test_rules_exact.py
 M tests/test_rules_semantics.py
 M tests/test_sparprogramm.py
?? .planning/phases/03-content-source-veiling/tools/   (committed together with this report)
```

`tests/golden/` and the three legacy generators are untouched.
