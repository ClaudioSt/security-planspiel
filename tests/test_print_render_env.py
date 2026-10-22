"""Render stage: tex_escape, the strict Jinja environment and the document registry."""
from fractions import Fraction

import pytest
from jinja2.exceptions import UndefinedError

from planspiel import render


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Backup & Disaster Recovery", r"Backup \& Disaster Recovery"),
        ("100 %", r"100 \%"),
        ("$5", r"\$5"),
        ("#1", r"\#1"),
        ("a_b", r"a\_b"),
        ("{x}", r"\{x\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
        ("\\", r"\textbackslash{}"),
        (r"\input{x}", r"\textbackslash{}input\{x\}"),
        ("Größe Ä Ö Ü ß € − × ÷ ≤ ≥ ▢", "Größe Ä Ö Ü ß € − × ÷ ≤ ≥ ▢"),
    ],
)
def test_tex_escape_translates_specials_in_one_pass(raw, expected):
    assert render.tex_escape(raw) == expected


@pytest.mark.parametrize("value", [3, Fraction(1, 2), None, 1.5, b"x"])
def test_tex_escape_rejects_non_strings(value):
    with pytest.raises(TypeError):
        render.tex_escape(value)


@pytest.mark.parametrize("char", ["\x00", "\x08", "\x0b", "\x0c", "\x1f"])
def test_tex_escape_rejects_control_characters(char):
    with pytest.raises(ValueError):
        render.tex_escape(f"a{char}b")


def test_tex_escape_keeps_tab_and_newline():
    assert render.tex_escape("a\tb\nc") == "a\tb\nc"


def _env(tmp_path, name, body):
    (tmp_path / name).write_text(body, encoding="utf-8", newline="\n")
    return render.make_env(tmp_path).get_template(name)


def test_variable_is_escaped(tmp_path):
    template = _env(tmp_path, "t.tex.j2", "\\textbf{\\VAR{name}}\n")
    assert template.render(name="A&B") == "\\textbf{A\\&B}\n"


def test_block_loop_works(tmp_path):
    template = _env(tmp_path, "t.tex.j2", "\\BLOCK{for x in items}\\VAR{x}\\BLOCK{endfor}\n")
    assert template.render(items=["a", "b", "c"]) == "abc\n"


def test_undefined_variable_raises(tmp_path):
    template = _env(tmp_path, "t.tex.j2", "\\VAR{missing}\n")
    with pytest.raises(UndefinedError):
        template.render()


def test_number_cannot_reach_the_page(tmp_path):
    template = _env(tmp_path, "t.tex.j2", "\\VAR{n}\n")
    with pytest.raises(TypeError):
        template.render(n=3)


def test_latex_braces_and_comments_pass_through(tmp_path):
    body = "\\begin{center}% a comment\n{\\bfseries x}\n\\end{center}\n"
    assert _env(tmp_path, "t.tex.j2", body).render() == body


def test_jinja_comment_delimiters_do_not_clash_with_tex(tmp_path):
    body = "\\#{ removed }kept\n"
    assert _env(tmp_path, "t.tex.j2", body).render() == "kept\n"


def test_render_all_with_empty_registry(monkeypatch, tmp_path):
    monkeypatch.setattr(render, "DOCUMENT_BUILDERS", ())
    assert render.render_all(None, None, tmp_path) == {}


def test_render_all_merges_builders_sorted_by_job(monkeypatch, tmp_path):
    monkeypatch.setattr(
        render,
        "DOCUMENT_BUILDERS",
        (lambda cfg, texts, env: {"zeta": "z"}, lambda cfg, texts, env: {"alpha": "a", "mid": "m"}),
    )
    result = render.render_all(None, None, tmp_path)
    assert list(result) == ["alpha", "mid", "zeta"]
    assert result == {"alpha": "a", "mid": "m", "zeta": "z"}


def test_render_all_rejects_duplicate_jobs(monkeypatch, tmp_path):
    monkeypatch.setattr(
        render,
        "DOCUMENT_BUILDERS",
        (lambda cfg, texts, env: {"same": "1"}, lambda cfg, texts, env: {"same": "2"}),
    )
    with pytest.raises(ValueError, match="same"):
        render.render_all(None, None, tmp_path)
