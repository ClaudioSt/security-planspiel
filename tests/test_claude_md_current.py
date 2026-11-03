"""LEG-02 (part 4): the agent-facing context files describe the current pipeline.

Pins the root CLAUDE.md (English), the three GSD source maps and the generated .claude/CLAUDE.md so
that no agent session is steered to hand-edit documents, read caches that no longer exist or run
retired generators.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

ROOT_CLAUDE = REPO_ROOT / "CLAUDE.md"
GENERATED_CLAUDE = REPO_ROOT / ".claude" / "CLAUDE.md"
MAPS = tuple(REPO_ROOT / ".planning" / "codebase" / name for name in ("STACK.md", "CONVENTIONS.md", "ARCHITECTURE.md"))

ROOT_REQUIRED = (
    "uv run planspiel print --check",
    "content/texte.toml",
    "final_documents/generated",
    "archive/legacy_generators",
    "archive/mhp_print_material_2026-07",
)
# Matched case-insensitively. The German section titles mark the old German file; "Whiteboard" is gone
# because the board write-up step was dropped (D-02) and the game is paper-only.
ROOT_FORBIDDEN = (
    "Was ist das hier",
    "Repo-Struktur",
    "Spielmechanik in Kürze",
    "Beim Arbeiten in diesem Repo",
    "python-docx",
    "Whiteboard",
)
LEGACY_NAMES = ("generate_pptx_cards", "generate_from_template", "generate_attack_calculator", "pptx_output")
ORDER_LINE = re.compile(r"simulation_config\.json.*README\.md.*content/texte\.toml.*planspiel print")

GENERATED_REQUIRED_MARKERS = (
    "GSD:stack-start",
    "GSD:conventions-start",
    "GSD:architecture-start",
    "GSD:profile-start",
)
GENERATED_FORBIDDEN = ("sim_low.json", "M_sum", "No `pytest`")
MAP_REQUIRED = ("planspiel print", "pytest")
MAP_FORBIDDEN = ("sim_low.json", "M_sum")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("‑", "-")


def _section(text: str, title: str) -> str:
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == f"## {title}")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[start + 1 : end])


def test_root_claude_md_has_the_required_statements():
    text = _read(ROOT_CLAUDE)
    missing = [needle for needle in ROOT_REQUIRED if needle not in text]
    assert not missing, f"CLAUDE.md lacks: {missing}"


def test_root_claude_md_is_english_and_free_of_retired_wording():
    text = _read(ROOT_CLAUDE).casefold()
    present = [needle for needle in ROOT_FORBIDDEN if needle.casefold() in text]
    assert not present, f"CLAUDE.md still contains: {present}"


def test_root_claude_md_what_this_is_states_the_paper_only_flow():
    section = _section(_read(ROOT_CLAUDE), "What this is")
    assert "paper" in section.casefold()


def test_root_claude_md_mentions_legacy_generators_only_as_archived():
    stray = [
        line
        for line in _read(ROOT_CLAUDE).splitlines()
        if any(name in line for name in LEGACY_NAMES) and "archive/" not in line
    ]
    assert not stray, f"legacy generators mentioned as live: {stray}"


def test_root_claude_md_states_the_change_order_on_one_line():
    assert any(ORDER_LINE.search(line) for line in _read(ROOT_CLAUDE).splitlines())


def test_root_claude_md_does_not_present_docs_as_reference_sheets():
    stray = [
        line
        for line in _read(ROOT_CLAUDE).splitlines()
        if "`docs/`" in line and re.search(r"reference sheet|Referenzbl", line, re.IGNORECASE)
    ]
    assert not stray, f"docs/ presented as current reference: {stray}"


def test_generated_claude_md_keeps_its_markers():
    text = _read(GENERATED_CLAUDE)
    missing = [marker for marker in GENERATED_REQUIRED_MARKERS if marker not in text]
    assert not missing, f".claude/CLAUDE.md lacks markers: {missing}"


def test_generated_claude_md_describes_the_print_pipeline():
    assert "planspiel print" in _read(GENERATED_CLAUDE)


def test_generated_claude_md_has_no_stale_statements():
    text = _read(GENERATED_CLAUDE)
    present = [needle for needle in GENERATED_FORBIDDEN if needle in text]
    assert not present, f".claude/CLAUDE.md still contains: {present}"


def test_codebase_maps_describe_the_current_pipeline():
    for path in MAPS:
        text = _read(path)
        missing = [needle for needle in MAP_REQUIRED if needle not in text]
        present = [needle for needle in MAP_FORBIDDEN if needle in text]
        assert not missing, f"{path.name} lacks: {missing}"
        assert not present, f"{path.name} still contains: {present}"
