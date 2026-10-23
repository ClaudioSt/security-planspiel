"""Audience registry: the job-name prefix classifies every printed document (VEIL-02, T-05-03)."""
import pytest

from planspiel import audience, render
from planspiel.config import load_config
from planspiel.printmodel import build_attack_sheets, worksheet_job
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]


@pytest.mark.parametrize(
    ("job", "expected"),
    [
        ("spieler-teamheft", "prewave"),
        ("uebung-welle-0", "practice"),
        ("angriff-1_ransomware", "revealed"),
        ("spielleitung-uebersicht", "facilitator"),
    ],
)
def test_each_prefix_maps_to_its_audience(job, expected):
    assert audience.audience_of(job) == expected


@pytest.mark.parametrize("job", ["smoke", "spieler", "Spieler-x", "x-spieler-y", ""])
def test_unknown_prefix_raises_and_names_the_allowed_prefixes(job):
    with pytest.raises(ValueError) as raised:
        audience.audience_of(job)
    for prefix in ("spieler-", "uebung-", "angriff-", "spielleitung-"):
        assert prefix in str(raised.value)


@pytest.mark.parametrize(
    ("job", "expected"),
    [
        ("spieler-massnahmenkarten", "names"),
        ("spieler-teamheft", "story"),
        ("uebung-welle-0", "story"),
        ("angriff-2_ot", "other_attacks"),
        ("spielleitung-uebersicht", None),
    ],
)
def test_scan_profile_per_job(job, expected):
    assert audience.scan_profile(job) == expected


def test_the_measure_deck_job_name_is_a_prewave_job():
    assert audience.MEASURE_DECK_JOB == "spieler-massnahmenkarten"
    assert audience.audience_of(audience.MEASURE_DECK_JOB) == audience.PREWAVE


def test_constants_and_prefix_order():
    assert audience.PREFIXES == (
        ("spieler-", audience.PREWAVE),
        ("uebung-", audience.PRACTICE),
        ("angriff-", audience.REVEALED),
        ("spielleitung-", audience.FACILITATOR),
    )
    assert (audience.PROFILE_NAMES, audience.PROFILE_STORY, audience.PROFILE_OTHER_ATTACKS) == (
        "names", "story", "other_attacks"
    )


@pytest.mark.parametrize("setup", SETUPS)
def test_every_rendered_job_has_an_audience(setup):
    config_path, content_dir = setup
    cfg = load_config(config_path)
    texts = load_texts(content_dir / "texte.toml")
    documents = render.render_all(cfg, texts, TEMPLATES)
    assert documents
    for job in documents:
        audience.audience_of(job)  # raises when unclassified


def test_the_three_real_jobs_are_revealed():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    documents = render.render_all(cfg, texts, TEMPLATES)
    assert [job for job in documents if job.startswith("angriff-")] == list(documents)
    assert {audience.audience_of(job) for job in documents} == {audience.REVEALED}


def test_render_all_rejects_a_job_without_a_known_prefix(monkeypatch):
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    monkeypatch.setattr(render, "DOCUMENT_BUILDERS", (lambda cfg, texts, env: {"lose-datei": "x"},))
    with pytest.raises(ValueError, match="spieler-"):
        render.render_all(cfg, texts, TEMPLATES)


def test_worksheet_job_is_the_existing_job_name():
    cfg = load_config(CONFIG_PATH)
    assert worksheet_job(cfg.waves[0]) == "angriff-1_ransomware"


@pytest.mark.parametrize("setup", SETUPS)
def test_every_attack_sheet_job_equals_worksheet_job(setup):
    config_path, content_dir = setup
    cfg = load_config(config_path)
    texts = load_texts(content_dir / "texte.toml")
    for wave, sheet in zip(cfg.waves, build_attack_sheets(cfg, texts)):
        assert sheet.job == worksheet_job(wave)
