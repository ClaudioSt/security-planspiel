"""Welle 0 document: Jinja rendering, shared worksheet partial and the veil (FLOW-01, D-12, D-14, ROADMAP SC3).

No TeX is involved here; the built PDF is covered by tests/test_welle0_pdf.py.
"""
import hashlib
import json
import re

import pytest

from planspiel import fmt, practice, render, veil
from planspiel.config import load_config
from planspiel.printmodel import PrintModelError
from planspiel.texts import load_content, load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT
from tests.support.golden import check_golden

TEMPLATES = REPO_ROOT / "print" / "templates"
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"
REAL_WORKSHEETS = ("angriff-1_ransomware", "angriff-2_ot", "angriff-3_exfil")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
PLAIN_VARIABLE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\[\]'\"]*$")
VARIABLE = re.compile(r"\\VAR\{([^}]*)\}")


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, texts, render.render_all(cfg, texts, TEMPLATES)


def test_real_worksheets_render_unchanged(real, update_golden, golden_report):
    """The three revealed worksheets stay byte-identical when the template is split into a shared partial (T-05-41)."""
    documents = real[2]
    digests = {job: hashlib.sha256(documents[job].encode("utf-8")).hexdigest() for job in REAL_WORKSHEETS}
    check_golden(GOLDEN_DIR / "worksheet_tex.json", {"sha256": digests}, update_golden, golden_report)


# ---- the Welle 0 document -------------------------------------------------------------------------------------


def test_the_practice_job_is_rendered_for_the_real_config_only(real):
    assert practice.PRACTICE_JOB in real[2]
    assert list(real[2]) == sorted(real[2])
    mini = load_config(MINI)
    mini_texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    assert practice.PRACTICE_JOB not in render.render_all(mini, mini_texts, TEMPLATES)


def test_the_practice_document_skeleton(real):
    source = real[2][practice.PRACTICE_JOB]
    assert source.startswith("\\documentclass")
    assert "\\usepackage{planspiel}" in source
    assert source.endswith("\\end{document}\n")
    assert "\r" not in source


def test_the_worksheet_body_is_a_shared_partial():
    assert (TEMPLATES / "angriff_blatt.tex.j2").is_file()
    for name in ("angriff.tex.j2", "uebung.tex.j2"):
        assert 'include "angriff_blatt.tex.j2"' in (TEMPLATES / name).read_text(encoding="utf-8"), name


@pytest.mark.parametrize("name", ["angriff_blatt.tex.j2", "uebung.tex.j2"])
def test_templates_print_plain_variables_only(name):
    source = (TEMPLATES / name).read_text(encoding="utf-8")
    expressions = VARIABLE.findall(source)
    assert expressions
    assert all(PLAIN_VARIABLE.match(expression) for expression in expressions), name


def test_every_box_of_the_practice_sheet_is_filled_in_the_tex(real):
    source = real[2][practice.PRACTICE_JOB]
    assert "\\ibox{" not in source
    assert "\\ifilled{" in source
    assert "\\ibox{" in real[2]["angriff-1_ransomware"]
    assert "\\ifilled{" not in real[2]["angriff-1_ransomware"]


def test_every_printed_fragment_of_the_practice_document_is_in_the_tex(real):
    cfg, texts, documents = real
    doc = practice.build_practice_document(cfg, texts)
    source = documents[practice.PRACTICE_JOB]
    for fragment in doc.printed_fragments():
        assert render.tex_escape(fragment) in source, f"{fragment!r}"
    assert render.tex_escape(doc.title) in source


def test_the_practice_document_passes_the_practice_veil_scan(real):
    cfg = real[0]
    content = load_content(CONTENT_DIR)
    source = real[2][practice.PRACTICE_JOB]
    assert veil.scan_documents(cfg, content.texts, content.terms, {practice.PRACTICE_JOB: source}) == []
    ctx = veil.context(cfg, content.texts, content.terms)
    assert len(ctx.signatures) == len(cfg.waves)
    assert veil.weight_hits(veil.detex(source), ctx.signatures) == []


def test_the_practice_document_prints_its_own_weights_not_those_of_a_real_wave(real):
    cfg, texts, _ = real
    doc = practice.build_practice_document(cfg, texts)
    printed = "".join(part for part in doc.sheet.e_value_line if isinstance(part, str))
    weights = re.findall(r"× ([0-9,]+)", printed)
    assert weights == ["0,3", "0,3", "0,4"]
    for wave in cfg.waves:
        assert sorted(weights) != sorted(fmt.format_number(wave.weights[key]) for key in "cia")


def test_the_build_stops_with_a_model_error_when_the_example_breaks(tmp_path):
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    raw["practice"]["selection"] = {key: 0 for key in raw["practice"]["selection"]}
    path = tmp_path / "config.json"
    path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8", newline="\n")
    cfg = load_config(path)
    with pytest.raises(PrintModelError):
        render.render_all(cfg, load_texts(CONTENT_DIR / "texte.toml"), TEMPLATES)


# ---- the reality-check line (RISK-04, D-12) --------------------------------------------------------------------


def test_the_reality_question_follows_the_result_line_and_precedes_the_fill_report(real):
    cfg, texts, documents = real
    question = render.tex_escape(texts.get("sheets.angriff.reality_question"))
    result_label = render.tex_escape(texts.get("sheets.angriff.label_result"))
    for job in REAL_WORKSHEETS:
        source = documents[job]
        assert source.count(question) == 1, job
        assert source.index(result_label + ":") < source.index(question) < source.index(r"\fillreport{2}"), job


def test_the_practice_sheet_has_no_reality_question(real):
    _, texts, documents = real
    assert render.tex_escape(texts.get("sheets.angriff.reality_question")) not in documents[practice.PRACTICE_JOB]
