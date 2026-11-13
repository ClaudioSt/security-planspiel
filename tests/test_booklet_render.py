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
SHELL, PLANNING, TRACKING, ROS = (
    "teamheft.tex.j2", "teamheft_planung.tex.j2", "teamheft_tracking.tex.j2", "teamheft_ros.tex.j2"
)
REGISTER = "teamheft_register.tex.j2"
UNESCAPED_AMPERSAND = re.compile(r"(?<!\\)&")
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


def test_the_shell_is_a_document_and_includes_the_three_partials():
    shell = (TEMPLATES / SHELL).read_text(encoding="utf-8")
    assert "\\documentclass[" in shell
    assert "\\usepackage{planspiel}" in shell
    assert f'include "{PLANNING}"' in shell
    assert f'include "{TRACKING}"' in shell
    assert f'include "{ROS}"' in shell
    assert shell.index(PLANNING) < shell.index(TRACKING) < shell.index(ROS)
    for partial in (PLANNING, TRACKING, ROS):
        text = (TEMPLATES / partial).read_text(encoding="utf-8")
        assert "\\documentclass" not in text, partial
        assert "\\begin{document}" not in text, partial


def test_the_tracking_partial_sits_between_planning_and_ros_with_its_own_fill_report():
    lines = [line for line in (TEMPLATES / SHELL).read_text(encoding="utf-8").splitlines() if line.strip()]
    include = next(index for index, line in enumerate(lines) if TRACKING in line)
    assert lines[include + 1].startswith("\\fillreport{\\thepage}")
    assert lines[include + 2].strip() == "\\clearpage"
    assert lines[include - 1].strip() == "\\clearpage"


def test_the_register_partial_comes_first_inside_its_guard_with_its_own_fill_report():
    lines = [line.strip() for line in (TEMPLATES / SHELL).read_text(encoding="utf-8").splitlines() if line.strip()]
    include = next(index for index, line in enumerate(lines) if REGISTER in line)
    assert lines[include - 1] == "\\BLOCK{if booklet.register}"
    assert lines[include + 1].startswith("\\fillreport{\\thepage}")
    assert lines[include + 2] == "\\clearpage"
    assert lines[include + 3] == "\\BLOCK{endif}"
    assert PLANNING in lines[include + 4]


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


def test_the_register_page_is_rendered_only_with_a_risk_matrix(loaded):
    cfg, _, booklet, source = loaded
    if cfg.risk_matrix is None:
        assert booklet.register is None
        assert "Risikoregister" not in source
    else:
        assert render.tex_escape(booklet.register.title) in source
        assert source.index(render.tex_escape(booklet.register.title)) < source.index(
            render.tex_escape(booklet.planning.title)
        )


def _register_body_rows(source, booklet):
    rows = []
    for label in booklet.register.rows:
        start = source.index(f"\\textbf{{{label}}}")
        end = source.index("\\\\", start)
        rows.append(UNESCAPED_AMPERSAND.split(source[start:end]))
    return rows


def test_every_register_row_has_seven_cells_with_its_writing_areas(loaded):
    cfg, _, booklet, source = loaded
    if cfg.risk_matrix is None:
        pytest.skip("the mini config has no register")
    register = booklet.register
    rows = _register_body_rows(source, booklet)
    assert len(rows) == cfg.risk_matrix.register_rows
    for cells in rows:
        assert len(cells) == 7, cells
        asset, threat, goal, impact, rank, decision, review = cells
        assert "\\writeline" in asset
        assert threat.count("\\writeline") >= 2 and render.tex_escape(register.source_label) in threat
        assert threat.index("\\writeline") < threat.index(render.tex_escape(register.source_label))
        assert goal.count("\\tickbox") == 3 and all(render.tex_escape(tick) in goal for tick in register.goal_ticks)
        assert impact.count("\\tickbox") == 4 and "\\writeline" in impact
        assert all(render.tex_escape(tick) in impact for tick in register.category_ticks)
        assert "\\tickbox" not in rank and "\\writeline" not in rank
        assert decision.count("\\tickbox") == 2 and "\\writeline" in decision
        assert render.tex_escape(register.reason_label) in decision
        assert all(render.tex_escape(tick) in decision for tick in register.decision_ticks)
        review_ticks = all(render.tex_escape(tick) in review for tick in register.review_ticks)
        assert review.count("\\tickbox") == 3 and review_ticks
    header = source[source.index("\\rowcolor{mhpblue}", source.index(render.tex_escape(register.title))):]
    header = header[: header.index("\\\\")]
    assert len(UNESCAPED_AMPERSAND.split(header)) == 7
    for text in register.header:
        assert render.tex_escape(text) in header
    example = source[source.index(render.tex_escape(register.example[0])):]
    example = example[: example.index("\\\\")]
    assert len(UNESCAPED_AMPERSAND.split(example)) == 7


def test_planning_comes_first_then_the_tracking_page_then_the_ros_part(loaded):
    _, _, booklet, source = loaded
    planning = source.index(render.tex_escape(booklet.planning.title))
    tracking = source.index(render.tex_escape(booklet.tracking.title))
    ros = source.index(render.tex_escape(booklet.ros.title))
    review = source.rindex(render.tex_escape(booklet.ros.review_title))  # the RoS title names the review too
    assert planning < tracking < ros < review
    assert "\\clearpage" in source[planning:tracking]
    assert "\\clearpage" in source[tracking:ros], "the RoS part starts on a new page after the tracking page"
    assert "\\clearpage" in source[ros:review], "the Budget Review has its own page"


def test_every_page_break_and_the_end_of_the_document_follow_a_fill_report(loaded):
    lines = _lines(loaded[3])
    breaks = [index for index, line in enumerate(lines) if line.strip() == "\\clearpage"]
    assert len(breaks) == (4 if loaded[0].risk_matrix is not None else 3), "one break per page but the last"
    for index in [*breaks, lines.index("\\end{document}")]:
        assert lines[index - 1].startswith("\\fillreport{"), lines[index - 1]


def test_the_planning_table_rows_are_writable(loaded):
    _, _, booklet, source = loaded
    planning = (TEMPLATES / PLANNING).read_text(encoding="utf-8")
    assert "\\rowstrut" in planning
    assert "\\newcommand{\\rowstrut}{\\rule[-2.3mm]{0pt}{7mm}}" in STYLE.read_text(encoding="utf-8")
    for label in booklet.planning.planning_rows:
        assert render.tex_escape(label) in source


@pytest.mark.parametrize("template", [SHELL, REGISTER, PLANNING, TRACKING, ROS])
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


def test_every_shaded_cell_of_the_tracking_sheet_is_a_grey_cell_in_the_tex(loaded):
    _, _, booklet, source = loaded
    tracking = booklet.tracking
    shaded = sum(row.cells.count("shaded") for row in (*tracking.rows, *tracking.summary_rows))
    assert shaded > 0
    assert source.count("\\shadedcell") == shaded
    assert "\\newcommand{\\shadedcell}{\\cellcolor{mhpshade}}" in STYLE.read_text(encoding="utf-8")


def test_the_tracking_rows_are_writable_and_the_two_blocks_have_blue_header_rows(loaded):
    _, _, booklet, source = loaded
    partial = (TEMPLATES / TRACKING).read_text(encoding="utf-8")
    assert "\\rowstrut" in partial
    for title in (booklet.tracking.block_own, booklet.tracking.block_external):
        assert render.tex_escape(title) in source
    assert partial.count("\\rowcolor{mhpblue}") >= 3, "table header and the two block header rows"


def test_the_tracking_sheet_prints_every_window_measure_in_every_window(loaded):
    _, _, booklet, source = loaded
    for label in booklet.tracking.windows[0].measure_rows:
        assert render.tex_escape(label) in source
    for block in booklet.tracking.windows:
        assert render.tex_escape(block.after_wave) in source


def test_the_booklet_fragments_include_the_tracking_page(loaded):
    _, _, booklet, _ = loaded
    assert set(booklet.tracking.printed_fragments()) <= set(booklet.printed_fragments())
