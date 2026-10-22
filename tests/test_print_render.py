"""Attack worksheet template: thin Jinja rendering of the print model (PRINT-03, D-05, D-11, ROADMAP SC2).

No TeX is involved here; the built PDFs are covered by tests/test_print_worksheets_pdf.py.
"""
import json
import re

import pytest

from planspiel import render
from planspiel.config import load_config
from planspiel.printmodel import build_attack_sheets
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]
CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b-\x1f]")
PLAIN_VARIABLE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\[\]'\"]*$")
VARIABLE = re.compile(r"\\VAR\{([^}]*)\}")


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    cfg = load_config(config_path)
    texts = load_texts(content_dir / "texte.toml")
    return cfg, texts, render.render_all(cfg, texts, TEMPLATES)


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, texts, render.render_all(cfg, texts, TEMPLATES)


def _modified_render(tmp_path, change):
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    change(raw)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    cfg = load_config(path)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, build_attack_sheets(cfg, texts), render.render_all(cfg, texts, TEMPLATES)


def test_jobs_equal_the_model_jobs(loaded):
    cfg, texts, documents = loaded
    assert list(documents) == sorted(sheet.job for sheet in build_attack_sheets(cfg, texts))


def test_real_jobs_are_the_three_attack_worksheets(real):
    assert list(real[2]) == ["angriff-1_ransomware", "angriff-2_ot", "angriff-3_exfil"]


def test_document_skeleton(loaded):
    assert loaded[2], "no document rendered"
    for job, source in loaded[2].items():
        assert source.startswith("\\documentclass"), job
        assert "\\usepackage{planspiel}" in source, job
        assert source.endswith("\\end{document}\n"), job
        assert CONTROL_CHARACTERS.search(source) is None, job
        assert "\r" not in source, job


def test_every_printed_fragment_is_in_the_tex(loaded):
    cfg, texts, documents = loaded
    for sheet in build_attack_sheets(cfg, texts):
        source = documents[sheet.job]
        for fragment in sheet.printed_fragments():
            assert render.tex_escape(fragment) in source, f"{sheet.job}: {fragment!r}"


def test_exactly_one_clearpage_between_reduction_and_cases(loaded):
    cfg, texts, documents = loaded
    for sheet in build_attack_sheets(cfg, texts):
        source = documents[sheet.job]
        assert source.count("\\clearpage") == 1, sheet.job
        reduction = source.index(render.tex_escape(sheet.step_headings["reduction"]))
        cases = source.index(render.tex_escape(sheet.step_headings["cases"]))
        assert reduction < source.index("\\clearpage") < cases, sheet.job


def test_recovery_step_only_for_waves_with_recovery(loaded):
    cfg, texts, documents = loaded
    for sheet in build_attack_sheets(cfg, texts):
        source = documents[sheet.job]
        if sheet.with_recovery:
            assert render.tex_escape(sheet.step_headings["recovery"]) in source, sheet.job
            assert render.tex_escape(sheet.recovery_header[2]) in source, sheet.job
            for line_part in sheet.recovery_line:
                if isinstance(line_part, str):
                    assert render.tex_escape(line_part) in source, sheet.job
        else:
            assert "recovery" not in sheet.step_headings, sheet.job
            assert sheet.recovery_table == ()
            assert sheet.recovery_line is None


def test_recovery_present_in_waves_one_and_two_and_absent_in_wave_three(real):
    _, texts, documents = real
    assert "Recovery anrechnen" in documents["angriff-1_ransomware"]
    assert "Recovery anrechnen" in documents["angriff-2_ot"]
    assert "Recovery anrechnen" not in documents["angriff-3_exfil"]
    assert "Recovery-Faktor" not in documents["angriff-3_exfil"]


def test_measure_names_are_escaped(real):
    assert "Backup \\& Disaster Recovery" in real[2]["angriff-1_ransomware"]
    assert "Backup & Disaster Recovery" not in real[2]["angriff-1_ransomware"]


def test_mini_config_renders_the_wave_without_bonus_measures():
    cfg = load_config(MINI)
    texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    sheets = build_attack_sheets(cfg, texts)
    assert any(not sheet.bonus_table for sheet in sheets)
    documents = render.render_all(cfg, texts, TEMPLATES)
    assert len(documents) == len(cfg.waves)


def test_template_variables_are_plain_names():
    templates = sorted(TEMPLATES.glob("*.j2"))
    assert templates, "no template under print/templates"
    for template in templates:
        for expression in VARIABLE.findall(template.read_text(encoding="utf-8")):
            assert PLAIN_VARIABLE.match(expression), f"{template.name}: \\VAR{{{expression}}} is not a plain name"


def test_cap_line_sits_between_the_cases_heading_and_fall_one(loaded):
    cfg, texts, documents = loaded
    for sheet in build_attack_sheets(cfg, texts):
        source = documents[sheet.job]
        (cap_line,) = sheet.cap_line
        cap = source.index(render.tex_escape(cap_line))
        assert source.index(render.tex_escape(sheet.step_headings["cases"])) < cap, sheet.job
        assert cap < source.index(render.tex_escape(sheet.cases[0].heading)), sheet.job


def test_real_cap_line_reads_threshold_cap_and_upper_bound(real):
    assert "Schwelle: 23 · Kappung: 8 · Obergrenze: 23 + 8 = 31" in real[2]["angriff-1_ransomware"]


def test_a_threshold_change_reaches_the_sheet_without_a_template_change(tmp_path):
    def raise_threshold(raw):
        raw["waves"][0]["e_threshold"] += 1

    cfg, sheets, documents = _modified_render(tmp_path, raise_threshold)
    original = load_config(CONFIG_PATH)
    threshold = cfg.waves[0].e_threshold
    cap = sheets[0].reduction_cap
    assert threshold == original.waves[0].e_threshold + 1
    source = documents[sheets[0].job]
    assert f"≤ {threshold}" in source
    assert f"Schwelle: {threshold}" in source
    assert f"({threshold + cap} − GR" in source
    assert f"≤ {threshold - 1}" not in source
    assert f"Schwelle: {threshold - 1}" not in source


def test_a_cap_change_reaches_the_sheet_without_a_template_change(tmp_path):
    def raise_cap(raw):
        attack = raw["attacks"][raw["waves"][0]["attack_id"]]
        attack["mitigation_cap"] += 2
        attack["base_severity"] += 2

    cfg, sheets, documents = _modified_render(tmp_path, raise_cap)
    original = build_attack_sheets(load_config(CONFIG_PATH), load_texts(CONTENT_DIR / "texte.toml"))[0]
    threshold = cfg.waves[0].e_threshold
    cap = sheets[0].reduction_cap
    assert cap == original.reduction_cap + 2
    source = documents[sheets[0].job]
    assert f"Kappung: {cap}" in source
    assert f"Obergrenze: {threshold} + {cap} = {threshold + cap}" in source
    assert f"({threshold + cap} − GR" in source
    assert f"Kappung: {original.reduction_cap}" not in source
