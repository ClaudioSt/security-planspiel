"""README currency (LEG-02, D-20, ROADMAP SC4): the German rulebook describes the current rules and the print pipeline.

The retired pre-2026 model must be gone, the pipeline terms must be present, every PDF name must be a job the
print pipeline renders today, and the prose must not type a count that the config holds (waves, teams, stages).
"""
import re

import pytest

from planspiel import render
from planspiel.config import load_config
from planspiel.texts import load_clues, load_texts
from planspiel.was_neu import BASELINE_FILE, load_baseline
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"

RETIRED_TOKENS = (
    "M_sum",
    "baseSeverity",
    "eventSeverityMods",
    "kzUnit",
    "mitigationRefs",
    "targetCIA",
    "kzFactor",
    "damageFactor",
    "opexPenalty",
    "Discovery-Signal",
    "Auswertungsvorlagen (2 Tabellen",
    "pptx_output",
    "generate_pptx_cards",
    "generate_from_template",
    "generate_attack_calculator",
)

REQUIRED_TERMS = (
    "Gesamtreduktion",
    "Reduktion über Schwelle",
    "uv run planspiel print",
    "uv run planspiel print --check",
    "content/texte.toml",
    "content/clues.toml",
    "content/mhp_baseline.json",
    "final_documents/generated",
    "Welle 0",
    "Debriefing",
    "Was ist neu",
    "Final-Index",
)

ORDER_LINE = re.compile(r"simulation_config\.json.*README\.md.*content/texte\.toml.*planspiel print")

COUNT_PHRASES = re.compile(
    r"\b(eins|zwei|drei|vier|fünf|sechs)\s+"
    r"(Wellen|Teams|Angriffe|Story-Dokumente|Dokumente|Stufen|Budget-Stufen|Blöcke|Pausen|Phasen)\b",
    re.IGNORECASE,
)
WAVES_ONE_TO_THREE = re.compile(r"Wellen eins bis drei", re.IGNORECASE)

# Kept prose that matches COUNT_PHRASES but is not a count the config holds.
ALLOWED_COUNT_PHRASES = {
    "zwei Wellen": "Zwischen zwei Wellen: any two consecutive waves (Change-Fenster), not the number of waves",
}

PDF_NAME = re.compile(r"\b([a-z][a-z0-9_-]*)\.pdf\b")


@pytest.fixture(scope="module")
def readme():
    return (REPO_ROOT / "README.md").read_text(encoding="utf-8").replace("‑", "-")


@pytest.mark.parametrize("token", RETIRED_TOKENS)
def test_retired_model_is_gone(readme, token):
    assert token not in readme


@pytest.mark.parametrize("term", REQUIRED_TERMS)
def test_current_terms_are_present(readme, term):
    assert term in readme


def test_the_change_order_is_stated_on_one_line(readme):
    assert any(ORDER_LINE.search(line) for line in readme.splitlines())


def test_every_pdf_name_is_a_rendered_job(readme):
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    clues = load_clues(CONTENT_DIR / "clues.toml")
    baseline = load_baseline(CONTENT_DIR / BASELINE_FILE)
    jobs = set(render.render_all(cfg, texts, TEMPLATES, clues=clues, baseline=baseline))
    names = set(PDF_NAME.findall(readme))
    assert names, "README names no generated PDF"
    assert names <= jobs, sorted(names - jobs)


def test_allowed_count_phrases_still_occur(readme):
    for phrase in ALLOWED_COUNT_PHRASES:
        assert phrase in readme, phrase


def test_prose_types_no_config_count(readme):
    text = readme
    for phrase in ALLOWED_COUNT_PHRASES:
        text = text.replace(phrase, "")
    assert COUNT_PHRASES.findall(text) == []
    assert WAVES_ONE_TO_THREE.search(text) is None
