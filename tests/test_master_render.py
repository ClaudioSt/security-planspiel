"""Facilitator booklet: Jinja rendering of the master sheet and the clue input of the render stage (PRINT-10, D-21).

No TeX is involved here; the built PDF is covered by tests/test_master_pdf.py.
"""
import inspect
import re

import pytest

from planspiel import audience, master, render, veil
from planspiel.config import load_config
from planspiel.texts import load_clues, load_content, load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
TEMPLATE = TEMPLATES / "master.tex.j2"
PLAIN_VARIABLE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\[\]'\"]*$")
VARIABLE = re.compile(r"\\VAR\{([^}]*)\}")


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    clues = load_clues(CONTENT_DIR / "clues.toml")
    documents = render.render_all(cfg, texts, TEMPLATES, clues=clues)
    return cfg, texts, clues, documents


@pytest.fixture(scope="module")
def sheet(real):
    cfg, texts, clues, _ = real
    return master.build_master_sheet(cfg, texts, clues)


def test_the_master_job_is_rendered_for_the_real_config_only(real):
    assert master.MASTER_JOB in real[3]
    assert list(real[3]) == sorted(real[3])
    assert audience.audience_of(master.MASTER_JOB) == audience.FACILITATOR
    mini = load_config(MINI)
    mini_texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    mini_clues = load_clues(MINI_CONTENT_DIR / "clues.toml")
    assert master.MASTER_JOB not in render.render_all(mini, mini_texts, TEMPLATES, clues=mini_clues)


def test_the_master_builder_is_registered():
    assert render.master_sheet in render.DOCUMENT_BUILDERS


def test_every_builder_takes_the_clues():
    for builder in render.DOCUMENT_BUILDERS:
        assert list(inspect.signature(builder).parameters) == ["cfg", "texts", "env", "clues"], builder.__name__


def test_render_all_hands_the_clues_to_every_builder(monkeypatch, tmp_path):
    seen = []

    def spy(cfg, texts, env, clues):
        seen.append(clues)
        return {}

    monkeypatch.setattr(render, "DOCUMENT_BUILDERS", (spy, spy))
    assert render.render_all(None, None, tmp_path, clues=("a", "b")) == {}
    assert render.render_all(None, None, tmp_path) == {}
    assert seen == [("a", "b"), ("a", "b"), (), ()]


def test_the_master_skeleton(real):
    source = real[3][master.MASTER_JOB]
    assert source.startswith("\\documentclass")
    assert "\\usepackage{planspiel}" in source
    assert source.endswith("\\end{document}\n")
    assert "\r" not in source


def test_the_template_prints_plain_variables_only():
    source = TEMPLATE.read_text(encoding="utf-8")
    expressions = VARIABLE.findall(source)
    assert expressions
    assert all(PLAIN_VARIABLE.match(expression) for expression in expressions)


def test_every_printed_fragment_is_in_the_tex(real, sheet):
    source = real[3][master.MASTER_JOB]
    fragments = sheet.printed_fragments()
    assert len(fragments) > 200
    for fragment in fragments:
        assert render.tex_escape(fragment) in source, f"{fragment!r}"


def test_the_notice_comes_before_anything_else_on_the_first_page(real, sheet):
    source = real[3][master.MASTER_JOB]
    first_break = source.index("\\clearpage")
    assert source.index(render.tex_escape(sheet.notice)) < source.index(render.tex_escape(sheet.intro)) < first_break


def test_every_wave_section_starts_on_a_new_page(real, sheet):
    source = real[3][master.MASTER_JOB]
    for section in sheet.waves:
        heading = r"\attacktitle{" + render.tex_escape(section.title) + "}"
        assert source.count(heading) == 1, section.title
        before = source[: source.index(heading)]
        assert before.rstrip().endswith(r"\clearpage"), section.title


def test_the_clue_matrix_is_split_per_attack_and_holds_every_clue(real, sheet):
    source = real[3][master.MASTER_JOB]
    quotes = [entry.quote for group in sheet.clue_groups for entry in group.rows]
    assert len(quotes) == len(load_clues(CONTENT_DIR / "clues.toml"))
    for quote in quotes:
        assert render.tex_escape(quote) in source
    for group in sheet.clue_groups:
        assert render.tex_escape(group.title) in source[source.rindex(render.tex_escape(sheet.clues_title)):]


def test_without_clues_the_matrix_stays_empty_but_the_sheet_builds():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    source = render.render_all(cfg, texts, TEMPLATES)[master.MASTER_JOB]
    clues = load_clues(CONTENT_DIR / "clues.toml")
    assert all(render.tex_escape(clue.quote) not in source for clue in clues)


def test_the_approximation_sign_is_in_no_rendered_document(real):
    assert [job for job, source in real[3].items() if "≈" in source] == []


def test_the_master_sheet_is_outside_the_pre_wave_scan(real):
    cfg, texts, _, documents = real
    content = load_content(CONTENT_DIR)
    assert veil.scan_documents(cfg, content.texts, content.terms, {master.MASTER_JOB: documents[master.MASTER_JOB]}) == []
    assert audience.scan_profile(master.MASTER_JOB) is None


def test_the_page_one_notice_is_a_dedicated_style_macro():
    style = (REPO_ROOT / "print" / "planspiel.sty").read_text(encoding="utf-8")
    assert "\\facilitatornotice" in style
    assert "\\facilitatornotice" in TEMPLATE.read_text(encoding="utf-8")
