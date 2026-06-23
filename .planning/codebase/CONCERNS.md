# Codebase Concerns

**Analysis Date:** 2026-06-23

## Tech Debt

**Large generated simulation result files committed to git despite `.gitignore`:**
- Issue: `sim_low.json` (14 MB) and `sim_med.json` (50 MB) are listed in `.gitignore` (lines for `sim_low.json` and `sim_med.json`) but are tracked in git anyway (`git ls-files sim_low.json sim_med.json` returns both). The `.gitignore` itself is messy/contradictory — it lists overlapping and seemingly accidental entries (e.g. a malformed line `sim_high.jsonsimulation_results.json` with no separator, repeated duplicate lines for `simulation_results_high.json`).
- Files: `.gitignore`, `sim_low.json`, `sim_med.json`
- Impact: Every clone of the repo downloads 64 MB of generated JSON that is supposedly meant to be ignored. Git history will permanently retain every committed version of these files, bloating repo size over time. CLAUDE.md explicitly warns not to read these files fully into context — but nothing prevents a future `cat`/`Read` of the whole file by a human or another agent unaware of the warning.
- Fix approach: Decide intentionally — either commit via Git LFS (the `.gitattributes` already configures LFS filters for similarly-named files like `sim_high.json`, `simulation_results.json`, `simulation_results_high.json`, but not for `sim_low.json`/`sim_med.json` themselves) or actually exclude them from git and regenerate via `simulate_outcomes.py` on demand. Clean up `.gitignore` to remove the malformed/duplicate lines.

**Compiled Python bytecode committed to git:**
- Issue: `__pycache__/simulate_outcomes.cpython-311.pyc` is tracked in git (`git ls-files` confirms it).
- Files: `__pycache__/simulate_outcomes.cpython-311.pyc`
- Impact: Bytecode artifacts are environment/version-specific (tied to CPython 3.11) and provide no value in version control; they will silently go stale and clutter diffs/history.
- Fix approach: Remove from git tracking (`git rm --cached`) and add `__pycache__/` to `.gitignore`.

**No tooling enforces sync between prose Markdown docs and `simulation_config.json`:**
- Issue: CLAUDE.md explicitly states "Keine festen Zahlen in Prosa-Dokumenten einführen, ohne sie auch in `simulation_config.json` zu reflektieren" — but this is a written instruction only. No script, pre-commit hook, or CI check cross-validates numeric values mentioned in `README.md`, `PARAMETER_TABELLE.md`, `BACKUP_PARAMETER.md`, `MASSNAHMENKARTEN.md`, `ANGRIFFSKARTEN.md`, the `BERECHNUNGSBOGEN_WELLE*.md` files, etc. against the actual values in `simulation_config.json`.
- Files: `simulation_config.json` (source of truth), all prose docs listing parameters (`README.md`, `PARAMETER_TABELLE.md`, `BACKUP_PARAMETER.md`, `MASSNAHMENKARTEN.md`, `ANGRIFFSKARTEN.md`, `BERECHNUNGSBOGEN_WELLE1_RANSOMWARE.md`, `BERECHNUNGSBOGEN_WELLE2_OT_STOERUNG.md`, `BERECHNUNGSBOGEN_WELLE3_EXFILTRATION.md`)
- Impact: This is a pure-discipline process risk. Since the game is played live with printed/whiteboard materials referencing these numbers, drift between docs and config would mean facilitators and players see different numbers than what the simulation/balance scripts actually validated — undermining the "Determinismus statt Zufall" principle and potentially producing an unbalanced or inconsistent live session.
- Fix approach: A lightweight script that parses `simulation_config.json` and greps the Markdown docs for known parameter labels (e.g. `wC`, `wI`, `wA`, `baseSeverity`, `MIT_CAP`) to flag numeric mismatches would close this gap. Not present anywhere in the repo currently (`TODO.md` section 3.2 even acknowledges this as optional/non-blocking: "optional zusätzlich ein Skript/CI-Check für Redaktionsqualität (aber nicht für die Durchführung notwendig)").

**Generated binary deliverables risk silent hand-editing:**
- Issue: `final_documents/` (docx/pptx/pdf) and `pptx_output/` (pptx) contain binary files explicitly marked as generated/final, with CLAUDE.md warning "diese nicht händisch bearbeiten, sondern über die Generator-Skripte ... neu erzeugen." There is no checksum, lock file, or generation timestamp embedded that would let someone detect if a file was hand-edited outside the generator scripts before being overwritten by a regeneration run.
- Files: `final_documents/*.docx`, `final_documents/*.pptx`, `final_documents/*.pdf`, `pptx_output/*.pptx`
- Impact: If someone manually tweaks a `.pptx` in `final_documents/` (e.g. fixing a typo directly in PowerPoint) and then a teammate reruns `generate_pptx_cards.py` or `generate_from_template.py`, the manual fix is silently lost with no warning.
- Fix approach: Document this risk prominently (already done in CLAUDE.md) and consider a generation marker (e.g. a hash comment in a sidecar file) to detect drift, or treat `final_documents/` as fully ephemeral/regenerable and exclude it from manual review workflows.

**Redundant/stale generated pptx files in `pptx_output/`:**
- Issue: `pptx_output/` contains multiple overlapping variants of the same content with unclear provenance: `Events.pptx` (43 KB), `Events_Generated.pptx` (2.1 MB), `Events_Security-Game.pptx` (2.2 MB); and `Massnahmenkarten.pptx` (51 KB), `Massnahmenkarten_Generated.pptx` (2.3 MB), `Massnahmenkarten_Generated_updatedTemp.pptx` (2.2 MB, name suggests a temp/WIP artifact), `Massnahmenkarten_Security-Game.pptx` (2.4 MB).
- Files: `pptx_output/Events.pptx`, `pptx_output/Events_Generated.pptx`, `pptx_output/Events_Security-Game.pptx`, `pptx_output/Massnahmenkarten.pptx`, `pptx_output/Massnahmenkarten_Generated.pptx`, `pptx_output/Massnahmenkarten_Generated_updatedTemp.pptx`, `pptx_output/Massnahmenkarten_Security-Game.pptx`
- Impact: It's unclear which file is current/authoritative for printing, especially the `_updatedTemp` file which by name suggests an intermediate/throwaway artifact that should not have been left in the output directory. Risk of someone printing a stale or wrong variant.
- Fix approach: Clarify in a README inside `pptx_output/` (or the generator scripts) which file is canonical, and delete stale/temp variants like `Massnahmenkarten_Generated_updatedTemp.pptx`.

## Known Bugs

Not detected. No bug tracker, issue list, or in-code bug markers (no `TODO`/`FIXME`/`HACK`/`XXX` comments found in any `.py` file via search across `simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`, `generate_attack_calculator.py`, `generate_from_template.py`, `generate_pptx_cards.py`).

## Security Considerations

Not applicable in the traditional sense — this is an offline, non-networked content/simulation toolset with no user input, no auth, no external services, and no secrets in scope. No `.env` or credential files are present.

## Performance Bottlenecks

**Large in-memory JSON outputs from simulation runs:**
- Problem: `sim_med.json` is 50 MB and `sim_low.json` is 14 MB. `analyze_simulation_results.py` and any ad-hoc inspection of these files risks loading the entire structure into memory/context rather than streaming or using `jq`.
- Files: `sim_low.json`, `sim_med.json`, `analyze_simulation_results.py`
- Cause: `simulate_outcomes.py` enumerates all valid measure combinations exhaustively per budget tier, and the full combinatorial output is serialized as one JSON document rather than a streamed/JSONL format.
- Improvement path: CLAUDE.md already instructs not to fully read these files and to use `jq`/targeted Python parsing instead — this is documented as a known constraint rather than an oversight, but the underlying enumeration approach (full combinatorial dump vs. streaming/top-N output) is the root cause and could be revisited if budget tiers grow (a `high` tier is referenced in `.gitattributes`/`.gitignore` but no `sim_high.json` currently exists in the repo root, suggesting it may already be too large to generate/store directly).

## Fragile Areas

**`generate_from_template.py` / `generate_pptx_cards.py` reliance on `simulation_config.json` shape:**
- Files: `generate_pptx_cards.py` (loads `simulation_config.json` at line 206), `generate_from_template.py` (loads `simulation_config.json` at line 200), `generate_attack_calculator.py` (loads `simulation_config.json` at line 15 via relative path `'simulation_config.json'` rather than a `Path(__file__).parent`-relative path like the other two scripts use)
- Why fragile: `generate_attack_calculator.py` opens `simulation_config.json` using a bare relative path (`open('simulation_config.json', ...)`) instead of resolving it relative to the script's own directory the way `generate_pptx_cards.py` and `generate_from_template.py` do (`Path(__file__).parent / "simulation_config.json"`). If `generate_attack_calculator.py` is ever invoked from a different working directory (e.g. via a task runner, cron, or another script that `cd`s elsewhere first), it will fail to find the config file while the other two generators continue to work correctly.
- Safe modification: Run all generator scripts from the repo root (current implicit assumption) until this inconsistency is fixed by aligning `generate_attack_calculator.py` with the `Path(__file__).parent`-relative pattern used elsewhere.
- Test coverage: None — see Test Coverage Gaps below.

## Scaling Limits

Not applicable — this is a fixed-scope content/simulation project for a one-time/repeatable live tabletop session (3 teams x 5 people), not a deployed system with user-driven scaling concerns. The only scaling-relevant artifact is combinatorial growth of `simulate_outcomes.py` output size as the measure catalog or budget tiers grow (see Performance Bottlenecks above).

## Dependencies at Risk

Not assessed — no `requirements.txt`, `pyproject.toml`, or dependency lock file was found in the repo root, so Python script dependencies (e.g. `python-pptx`, `python-docx`, `openpyxl`-equivalents implied by `.xlsx`/`.pptx`/`.docx` generation) are not pinned anywhere. This means environment reproducibility for running the generator scripts depends entirely on whatever is installed system-wide / ad hoc, with no recorded version constraints.

## Missing Critical Features

Not in scope for this audit — `TODO.md` already tracks substantial unfinished work as an explicit roadmap (Meilensteine M1–M6), not as a hidden gap. Notably still open per `TODO.md`:
- Section 4 (Content-Produktion: Maßnahmenkatalog, Angriffsset, Events & Triggerlogik, Wellen-Design) has unchecked items, suggesting the MVP content set referenced as "final" in CLAUDE.md may still have open items per the roadmap doc.
- Section 6 (Playtest & Validation: golden-run reproducibility checks, dominance analysis, internal/external playtests) is fully unchecked — i.e., the explicit QA/validation milestone (M6, "classroom ready") has not yet been completed according to `TODO.md`.

## Test Coverage Gaps

**No automated tests exist anywhere in the repo:**
- What's not tested: All simulation/balance logic in `simulate_outcomes.py`, `analyze_simulation_results.py`, and `balance_analysis.py` — the formulas for `M_sum`, `G` (Endschwere), damage, ΔKZ, CIA-Mali, and RoS calculations have no unit tests verifying them against known expected outputs.
- Files: `simulate_outcomes.py`, `analyze_simulation_results.py`, `balance_analysis.py`
- Risk: Any future change to `simulation_config.json` values or to the Python formula implementations could silently produce incorrect simulation results with nothing to catch a regression except manual inspection of `sim_low.json`/`sim_med.json` output or manual balance review. CLAUDE.md's own guidance ("Nach inhaltlichen Änderungen ... simulate_outcomes.py + balance_analysis.py laufen lassen") relies entirely on a human remembering to run these scripts and eyeballing the results — there is no assertion-based regression test (e.g. a fixed "golden run" input/output pair) to mechanically confirm determinism is preserved after a content/config change, even though `TODO.md` section 6.1 explicitly calls for "Golden-Runs als Papierbeispiele: gleiche Inputs → identische Outputs" as a planned (but unchecked/unimplemented) validation step.
- Priority: Medium — the project intentionally treats `.py` scripts as supporting tools rather than a software product, and the actual "production" is the printed/whiteboard material. But because `simulate_outcomes.py` and `balance_analysis.py` are the only mechanism for catching unbalanced or inconsistent content before printing, a regression here would propagate directly into printed game materials without any automated safety net.

---

*Concerns audit: 2026-06-23*
