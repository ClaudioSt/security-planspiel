"""Team booklet shell and page partials: Jinja rendering of the booklet model (PRINT-07, D-05, D-08).

No TeX is involved here; the built PDF is covered by tests/test_booklet_pdf.py.
"""
import re

import pytest

from planspiel import audience, render, veil
from planspiel.booklet import BOOKLET_JOB, build_team_booklet
from planspiel.config import load_config
from planspiel.texts import load_content, load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"
STYLE = REPO_ROOT / "print" / "planspiel.sty"
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]
SHELL, PLANNING, ROS = "teamheft.tex.j2", "teamheft_planung.tex.j2", "teamheft_ros.tex.j2"
PLAIN_VARIABLE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\[\]'\"]*$")
VARIABLE = re.compile(r"\\VAR\{([^}]*)\}")


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    cfg = load_config(config_path)
    texts = load_texts(content_dir / "texte.toml")
    booklet = build_team_booklet(cfg, texts)
    return cfg, texts, booklet, render.render_all(cfg, texts, TEMPLATES)[BOOKLET_JOB]


def _lines(source):
    return [line for line in source.splitlines() if line.strip()]


def test_the_print_set_holds_the_team_booklet(loaded):
    cfg, texts, _, _ = loaded
    jobs = list(render.render_all(cfg, texts, TEMPLATES))
    assert BOOKLET_JOB in jobs
    assert jobs == sorted(jobs)
    assert audience.audience_of(BOOKLET_JOB) == audience.PREWAVE
    assert audience.scan_profile(BOOKLET_JOB) == audience.PROFILE_STORY


def test_the_shell_is_a_document_and_includes_the_two_partials():
    shell = (TEMPLATES / SHELL).read_text(encoding="utf-8")
    assert "\\documentclass[" in shell
    assert "\\usepackage{planspiel}" in shell
    assert f'include "{PLANNING}"' in shell
    assert f'include "{ROS}"' in shell
    assert shell.index(PLANNING) < shell.index(ROS)
    for partial in (PLANNING, ROS):
        text = (TEMPLATES / partial).read_text(encoding="utf-8")
        assert "\\documentclass" not in text, partial
        assert "\\begin{document}" not in text, partial


def test_the_shell_leaves_a_commented_insertion_point_for_the_tracking_page():
    shell = (TEMPLATES / SHELL).read_text(encoding="utf-8")
    between = shell[shell.index(PLANNING):shell.index(ROS)]
    comment = re.search(r"\\#\{([^}]*)\}", between)
    assert comment is not None, "a Jinja comment between the two includes marks the insertion point"
    assert "tracking" in comment.group(1)


def test_the_rendered_booklet_is_a_complete_document(loaded):
    source = loaded[3]
    assert source.startswith("\\documentclass")
    assert "\\usepackage{planspiel}" in source
    assert source.endswith("\\end{document}\n")
    assert source.count("\\begin{document}") == 1
    assert "\r" not in source


def test_every_printed_fragment_is_in_the_tex(loaded):
    _, _, booklet, source = loaded
    fragments = booklet.printed_fragments()
    assert fragments
    for fragment in fragments:
        assert render.tex_escape(fragment) in source, fragment


def test_planning_comes_first_and_the_ros_part_starts_on_a_new_page(loaded):
    _, _, booklet, source = loaded
    planning = source.index(render.tex_escape(booklet.planning.title))
    ros = source.index(render.tex_escape(booklet.ros.title))
    review = source.rindex(render.tex_escape(booklet.ros.review_title))  # the RoS title names the review too
    assert planning < ros < review
    assert "\\clearpage" in source[planning:ros]
    assert "\\clearpage" in source[ros:review], "the Budget Review has its own page"


def test_every_page_break_and_the_end_of_the_document_follow_a_fill_report(loaded):
    lines = _lines(loaded[3])
    breaks = [index for index, line in enumerate(lines) if line.strip() == "\\clearpage"]
    assert len(breaks) == 2
    for index in [*breaks, lines.index("\\end{document}")]:
        assert lines[index - 1].startswith("\\fillreport{"), lines[index - 1]


def test_the_planning_table_rows_are_writable(loaded):
    _, _, booklet, source = loaded
    planning = (TEMPLATES / PLANNING).read_text(encoding="utf-8")
    assert "\\rowstrut" in planning
    assert "\\newcommand{\\rowstrut}{\\rule[-2.3mm]{0pt}{7mm}}" in STYLE.read_text(encoding="utf-8")
    for label in booklet.planning.planning_rows:
        assert render.tex_escape(label) in source


@pytest.mark.parametrize("template", [SHELL, PLANNING, ROS])
def test_templates_print_only_plain_variables(template):
    text = (TEMPLATES / template).read_text(encoding="utf-8")
    expressions = VARIABLE.findall(text)
    assert expressions or template == SHELL
    for expression in expressions:
        assert PLAIN_VARIABLE.match(expression), f"{template}: {expression}"


def test_the_budget_review_prints_every_tier_and_penalty_row(loaded):
    _, _, booklet, source = loaded
    for span, value in (*booklet.ros.tier_rows, *booklet.ros.penalty_rows):
        assert render.tex_escape(span) in source
        assert render.tex_escape(value) in source


@pytest.mark.parametrize("setup", SETUPS)
def test_the_booklet_passes_the_story_veil_scan(setup):
    config_path, content_dir = setup
    cfg = load_config(config_path)
    content = load_content(content_dir)
    documents = {BOOKLET_JOB: render.render_all(cfg, content.texts, TEMPLATES)[BOOKLET_JOB]}
    assert veil.scan_documents(cfg, content.texts, content.terms, documents) == []


def test_the_booklet_has_no_final_index(loaded):
    assert "index" not in loaded[3].lower()
