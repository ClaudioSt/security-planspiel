"""Layer 2 of the veil scan: the built PDFs (text, metadata, file names) (VEIL-02, ROADMAP SC5, T-05-01, T-05-02).

Run with `uv run pytest -m pdf tests/test_veil_pdf.py -v`.
"""
import json

import pytest
from pypdf import PdfReader

from planspiel import audience, veil
from planspiel.config import load_config
from planspiel.printmodel import build_attack_sheets, worksheet_job
from planspiel.texts import load_content
from tests.support import CONFIG_PATH, CONTENT_DIR
from tests.support.pdf_text import FILL, page_texts, pdf_text, squash, squashed_pages

pytestmark = pytest.mark.pdf


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def ctx(cfg):
    content = load_content(CONTENT_DIR)
    return veil.context(cfg, content.texts, content.terms)


def _pdf(printed_set, job):
    return printed_set.out_a / f"{job}.pdf"


def _jobs(printed_set, *groups):
    return [job for job in printed_set.jobs if audience.audience_of(job) in groups]


def test_squash_removes_all_whitespace_including_nbsp():
    assert squash("a b c\n") == "abc"
    assert squash("a b\t c") == "abc"


def test_fill_regex_is_the_worksheet_one():
    assert FILL.pattern == r"PLANSPIEL-FILL page=(\d+) used=([0-9.]+)pt text=([0-9.]+)pt"
    assert FILL.search("PLANSPIEL-FILL page=1 used=200.5pt text=300pt")


def test_helpers_read_the_built_pdfs(printed_set):
    path = _pdf(printed_set, "spieler-smoke")
    raw = page_texts(path)
    assert len(raw) == len(PdfReader(path).pages) == len(squashed_pages(path))
    assert pdf_text(path) == "\n".join(raw)
    assert all(squash(text) == squashed for text, squashed in zip(raw, squashed_pages(path)))


def test_every_pdf_has_no_metadata_outline_or_annotations(printed_set):
    assert printed_set.jobs
    for job in printed_set.jobs:
        reader = PdfReader(_pdf(printed_set, job))
        assert not reader.metadata, f"{job}: Metadaten {dict(reader.metadata or {})}"
        assert reader.xmp_metadata is None, job
        assert reader.outline == [], job
        assert all("/Annots" not in page for page in reader.pages), job


def test_prewave_and_practice_pdfs_leak_nothing(printed_set, ctx):
    jobs = _jobs(printed_set, audience.PREWAVE, audience.PRACTICE)
    assert "spieler-smoke" in jobs
    for job in jobs:
        issues = veil.scan_text(pdf_text(_pdf(printed_set, job)), job, ctx, layer="pdf")
        assert issues == [], f"{job}: {issues}"


def test_revealed_pdfs_name_no_other_attack_and_print_only_their_own_weights(printed_set, cfg, ctx):
    revealed = _jobs(printed_set, audience.REVEALED)
    assert revealed == sorted(worksheet_job(wave) for wave in cfg.waves)
    for wave in cfg.waves:
        job = worksheet_job(wave)
        text = pdf_text(_pdf(printed_set, job))
        squashed = "".join(squashed_pages(_pdf(printed_set, job)))
        hits = veil.name_hits(squashed, ctx, audience.PROFILE_OTHER_ATTACKS, exclude_attack=wave.attack_id, squashed=True)
        assert hits == [], job
        assert set(veil.weight_hits(text, ctx.signatures)) == {wave.wave_id}, job
        assert veil.scan_text(text, job, ctx, layer="pdf") == [], job


def test_file_names_and_manifest_keys_of_non_revealed_jobs_name_no_attack(printed_set, ctx):
    manifest = json.loads((printed_set.out_a / "manifest.json").read_text(encoding="utf-8"))
    non_revealed = _jobs(printed_set, audience.PREWAVE, audience.PRACTICE, audience.FACILITATOR)
    assert set(non_revealed) <= set(manifest["documents"])
    for job in non_revealed:
        entry = manifest["documents"][job]
        for name in (job, entry["pdf"]):
            assert veil.name_hits(name, ctx, audience.PROFILE_NAMES) == [], name
    for path in printed_set.out_a.iterdir():
        if path.name != "manifest.json" and not path.name.startswith("angriff-"):
            assert veil.name_hits(path.name, ctx, audience.PROFILE_NAMES) == [], path.name


def test_negative_control_the_pdf_layer_can_fail(printed_set, ctx):
    leaked = pdf_text(_pdf(printed_set, "angriff-2_ot"))
    codes = {issue.code for issue in veil.scan_text(leaked, "spieler-test", ctx, layer="pdf")}
    assert {"veil.name", "veil.weights"} <= codes


def test_the_sheet_model_and_the_pdf_agree_on_the_job_names(printed_set, cfg):
    sheets = build_attack_sheets(cfg, load_content(CONTENT_DIR).texts)
    assert {sheet.job for sheet in sheets} <= set(printed_set.jobs)
