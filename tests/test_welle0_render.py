"""Welle 0 document: Jinja rendering, shared worksheet partial and the veil (FLOW-01, D-12, D-14, ROADMAP SC3).

No TeX is involved here; the built PDF is covered by tests/test_welle0_pdf.py.
"""
import hashlib

import pytest

from planspiel import render
from planspiel.config import load_config
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT
from tests.support.golden import check_golden

TEMPLATES = REPO_ROOT / "print" / "templates"
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"
REAL_WORKSHEETS = ("angriff-1_ransomware", "angriff-2_ot", "angriff-3_exfil")


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
