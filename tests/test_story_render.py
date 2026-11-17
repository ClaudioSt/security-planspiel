"""Story templates: the four documents are registered, every model string reaches the .tex escaped, fonts by name, veil layer 1 (PRINT-12).

No TeX is run here; the built PDFs are covered in tests/test_story_pdf.py.
"""
import re

import pytest

from planspiel import render, texbuild, veil
from planspiel.config import load_config
from planspiel.story import STORY_JOBS, Mail, Steckbrief, Zeitungsartikel, build_story_documents
from planspiel.texts import load_content
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
TEMPLATES = REPO_ROOT / "print" / "templates"
STORY_TEMPLATES = ("story_steckbrief.tex.j2", "story_zeitungsartikel.tex.j2", "story_mail.tex.j2")
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]
PLAIN_VARIABLE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\[\]'\"]*$")
VARIABLE = re.compile(r"\\VAR\{([^}]*)\}")
INCLUDEGRAPHICS = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}")


@pytest.fixture(params=SETUPS)
def rendered(request):
    config_path, content_dir = request.param
    cfg = load_config(config_path)
    content = load_content(content_dir)
    models = build_story_documents(cfg, content.texts)
    return cfg, content, models, render.render_all(cfg, content.texts, TEMPLATES)


@pytest.fixture(scope="module")
def real_sources():
    cfg = load_config(CONFIG_PATH)
    content = load_content(CONTENT_DIR)
    return build_story_documents(cfg, content.texts), render.render_all(cfg, content.texts, TEMPLATES)


def test_render_all_holds_the_four_story_jobs_in_sorted_order(rendered):
    cfg, content, _, documents = rendered
    assert set(STORY_JOBS.values()) <= set(documents)
    assert list(documents) == sorted(documents)


def test_every_story_tex_is_an_a4_document_using_the_shared_style(rendered):
    _, _, _, documents = rendered
    for job in STORY_JOBS.values():
        source = documents[job]
        assert source.startswith("\\documentclass[a4paper"), job
        assert "\\usepackage{planspiel}" in source, job
        assert source.rstrip().endswith("\\end{document}"), job
        assert "\r" not in source, job


def test_the_story_functions_and_templates_are_registered():
    assert render.story_documents in render.DOCUMENT_BUILDERS
    for name in STORY_TEMPLATES:
        assert (TEMPLATES / name).is_file(), name


def test_every_model_string_is_in_its_tex_escaped(rendered):
    _, _, models, documents = rendered
    for model in models:
        source = documents[model.job]
        for text in model.printed_strings():
            assert render.tex_escape(text) in source, (model.job, text)


def test_the_templates_print_only_plain_variables():
    for name in STORY_TEMPLATES:
        text = (TEMPLATES / name).read_text(encoding="utf-8")
        expressions = VARIABLE.findall(text)
        assert expressions, name
        for expression in expressions:
            assert PLAIN_VARIABLE.match(expression), (name, expression)


def test_no_story_template_upper_cases_or_names_a_font_path_or_a_file():
    for name in STORY_TEMPLATES:
        text = (TEMPLATES / name).read_text(encoding="utf-8")
        assert "MakeUppercase" not in text and "uppercase" not in text.lower().replace("lowercase", ""), name
        assert "Path=" not in text and ".ttf" not in text.lower() and ".otf" not in text.lower(), name
        assert ".png" not in text.lower(), name


def test_the_steckbrief_uses_the_guideline_margins_and_type(rendered):
    _, _, _, documents = rendered
    source = documents[STORY_JOBS["steckbrief"]]
    assert "\\newgeometry{" in source
    assert "left=2.5cm" in source and "top=2cm" in source and "bottom=1.8cm" in source
    assert "\\fontsize{12}" in source
    assert "\\begin{itemize}" in source


def test_the_newspaper_uses_multicol_graphicx_and_georgia_by_name(rendered):
    _, _, _, documents = rendered
    source = documents[STORY_JOBS["zeitungsartikel"]]
    assert "\\usepackage{multicol}" in source and "\\usepackage{graphicx}" in source
    assert "\\newfontfamily\\newspaperfont{Georgia}" in source
    assert "\\fontsize{48}" in source
    assert "\\begin{multicols}{2}" in source


def test_the_newspaper_includes_exactly_the_two_fixed_images(rendered):
    _, _, _, documents = rendered
    source = documents[STORY_JOBS["zeitungsartikel"]]
    assert INCLUDEGRAPHICS.findall(source) == list(texbuild.ASSET_FILES)
    for job, other in documents.items():
        if job != STORY_JOBS["zeitungsartikel"]:
            assert "\\includegraphics" not in other, job


def test_only_the_fixed_image_names_pass_tex_escape_unescaped():
    for name in texbuild.ASSET_FILES:
        assert render.tex_escape(render.asset_name(name)) == name and "_" in name
        assert render.tex_escape(name) != name  # the same text as a plain string is escaped
    for bad in ("other.png", "../zeitungsartikel_bild_audit.png", "", "zeitungsartikel_bild_audit.png\\input{x}"):
        with pytest.raises(ValueError):
            render.asset_name(bad)


def test_the_mail_header_block_prints_label_and_value_as_stored(real_sources):
    models, documents = real_sources
    for mail in (m for m in models if isinstance(m, Mail)):
        source = documents[mail.job]
        for label, value in (
            (mail.labels.sender, mail.sender),
            (mail.labels.recipient, mail.recipient),
            (mail.labels.subject, mail.subject),
        ):
            assert render.tex_escape(label) in source and render.tex_escape(value) in source
        assert "\\textquotedbl{}" in source
        assert '"' not in source, mail.job


def test_the_real_mail_headers_are_escaped_not_interpreted(real_sources):
    _, documents = real_sources
    anfrage = documents[STORY_JOBS["anfrage_mail"]]
    assert "\\textquotedbl{}Dr. Thomas Weber\\textquotedbl{} <t.weber@mechtech-gmbh.de>" in anfrage
    audit = documents[STORY_JOBS["audit_mail"]]
    assert "\\textquotedbl{}Klaus Hoffmann\\textquotedbl{} <k.hoffmann@premium-oem.com>" in audit


def test_the_models_are_the_documents_of_the_story_jobs(real_sources):
    models, _ = real_sources
    assert [type(model) for model in models] == [Steckbrief, Zeitungsartikel, Mail, Mail]


@pytest.mark.parametrize("setup", SETUPS)
def test_the_rendered_story_documents_pass_the_story_veil_scan(setup):
    config_path, content_dir = setup
    cfg = load_config(config_path)
    content = load_content(content_dir)
    rendered = render.render_all(cfg, content.texts, TEMPLATES)
    documents = {job: rendered[job] for job in STORY_JOBS.values()}
    assert veil.scan_documents(cfg, content.texts, content.terms, documents) == []
