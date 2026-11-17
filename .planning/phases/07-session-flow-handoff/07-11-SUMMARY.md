---
phase: 07-session-flow-handoff
plan: 11
subsystem: documentation
tags: [claude-md, codebase-maps, gsd-context, print-pipeline, legacy-cleanup]
requires: [07-01, 07-08, 07-10]
provides:
  - "CLAUDE.md: English project guide (What this is, Repository layout, Game mechanics in brief, Print pipeline, Working in this repo)"
  - "Refreshed .planning/codebase/STACK.md, CONVENTIONS.md, ARCHITECTURE.md"
  - ".claude/CLAUDE.md regenerated with gsd-tools generate-claude-md"
  - "tests/test_claude_md_current.py (ROOT_REQUIRED, ROOT_FORBIDDEN, GENERATED_FORBIDDEN, MAPS)"
affects: [07-09]
tech-stack:
  added: []
  patterns: ["agent-facing context files pinned by currency tests", "maps written as bullets and tables because the generator keeps only those lines"]
key-files:
  created:
    - tests/test_claude_md_current.py
  modified:
    - CLAUDE.md
    - .claude/CLAUDE.md
    - .planning/codebase/STACK.md
    - .planning/codebase/CONVENTIONS.md
    - .planning/codebase/ARCHITECTURE.md
    - .planning/PROJECT.md
key-decisions:
  - "Root CLAUDE.md keeps purpose, layout, mechanics and working rules only; stack and architecture detail stays in the generated file"
  - "The three maps use bullets and tables only, because generate-claude-md drops prose lines (and keeps only the fence lines of code blocks)"
  - "Dry run on a copy of .claude/CLAUDE.md (not a fresh --output file) so the diff proves that text outside the markers and the profile block survive"
requirements-completed: [LEG-02]
duration: ~40 min
completed: 2026-11-04
status: complete
---

# Phase 7 Plan 11: CLAUDE.md and GSD context currency Summary

The root CLAUDE.md is rewritten in English for the generated print pipeline, the three GSD source maps describe the current stack, conventions and architecture, and `.claude/CLAUDE.md` is regenerated from them. LEG-02 is complete (parts 07-05, 07-07, 07-10 and this plan).

## Tasks and commits

| Task | Commit | Result |
|------|--------|--------|
| 1 RED | 1585bd2 | `tests/test_claude_md_current.py`: 10 tests, 9 failed on the old files (assertion failures, no collection errors) |
| 2 GREEN | 090ed33 | CLAUDE.md rewritten in English; print-sync trap replaced by the "Print pipeline" section with the order `simulation_config.json -> README.md -> content/texte.toml -> uv run planspiel print -> uv run planspiel print --check -> commit final_documents/generated/`, the stamp and "+lokal" |
| 3 | 049b693 | STACK, CONVENTIONS, ARCHITECTURE refreshed; `.claude/CLAUDE.md` regenerated; PROJECT.md wording fixed |

## Verification

- `uv run pytest tests/test_claude_md_current.py tests/test_e_target_removed.py tests/test_readme_current.py -q`: green (the two new-plan files 33 passed; with the README test 54 passed).
- Dry run: `generate-claude-md --output <copy of .claude/CLAUDE.md>`; diff showed that only project, stack, conventions and architecture changed; the `GSD:profile-start`..`GSD:profile-end` block and everything after `GSD:architecture-end` (skills, workflow) were byte-identical. The real run (without `--auto`) gave the same result, `sections_skipped: []`, `profile_status: exists`. `git diff` confirmed the profile block unchanged against HEAD.
- Full fast suite (`uv run pytest -q`): 2920 passed, 205 deselected in 190.50s (2910 before plus the 10 new tests).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] PROJECT.md still said "paper/whiteboard"**
- **Found during:** Task 3 (dry run of the generator)
- **Issue:** `.claude/CLAUDE.md`'s project section is generated from `.planning/PROJECT.md` ("What This Is" and "Constraints"), which still named the whiteboard. The regenerated file would have contradicted the root CLAUDE.md (D-02: the board write-up step is gone).
- **Fix:** Two wording changes in PROJECT.md ("paper-only" in What This Is, "paper only" in the Format constraint). The historical MHP schedule table further down is untouched.
- **Files modified:** `.planning/PROJECT.md`
- **Commit:** 049b693

Otherwise the plan was executed as written.

## Follow-ups (not part of this plan)

- `README.md` line 8 still says "Das Spiel wird mit Papier und Whiteboard gespielt." (written in 07-10, not pinned by a test). It contradicts D-02 and should read paper only; one-line fix for 07-09 or a quick task.
- `.planning/codebase/STRUCTURE.md`, `TESTING.md`, `CONCERNS.md` and `INTEGRATIONS.md` are also stale (outside D-24, they do not feed `.claude/CLAUDE.md`); `/gsd-map-codebase` would refresh them.
- `docs/` is an empty untracked directory at the repo root and can be deleted.

## Known Stubs

None.

## Threat Flags

None. T-07-37 is mitigated by `tests/test_claude_md_current.py`; T-07-38 by the dry-run diff and the unchanged-profile check.

## Self-Check: PASSED

CLAUDE.md, tests/test_claude_md_current.py and the three maps exist; commits 1585bd2, 090ed33 and 049b693 exist.
