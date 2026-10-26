"""Built story documents: every clue quote is on the page of its source document, the newspaper carries its two images (PRINT-12, ROADMAP SC6).

Run with `uv run pytest -m pdf tests/test_story_pdf.py -v`.
"""
import re
import unicodedata

import pytest
from pypdf import PdfReader

from planspiel import audience, veil
from planspiel.config import load_config
from planspiel.story import STORY_JOBS, build_story_documents
from planspiel.texts import _clue_document, load_clues, load_content
from tests.support import CONFIG_PATH, CONTENT_DIR
from tests.support.pdf_text import pdf_text, squash, squashed_pages, unwrapped_log

pytestmark = pytest.mark.pdf

CLUES = load_clues(CONTENT_DIR / "clues.toml")
NEWSPAPER_PAGES = 1
STAMP = re.compile(r"Stand\d{4}-\d{2}-\d{2}·[0-9a-f]{7}(?:\+lokal)?")


def _job_of(source: str) -> str:
    document = _clue_document(source)
    if document == "measures":
        return audience.MEASURE_DECK_JOB
    assert document is not None and document.startswith("story."), source
    return STORY_JOBS[document.removeprefix("story.")]


@pytest.fixture(scope="module")
def setup():
    cfg = load_config(CONFIG_PATH)
    content = load_content(CONTENT_DIR)
    return cfg, content, build_story_documents(cfg, content.texts)


def _pdf(printed_set, job):
    return printed_set.out_a / f"{job}.pdf"


def test_the_clue_matrix_has_the_expected_size():
    assert len(CLUES) == 14


@pytest.mark.parametrize("number", range(1, len(CLUES) + 1), ids=lambda number: f"clue-{number:02d}")
def test_every_clue_quote_is_in_the_pdf_of_its_source_document(printed_set, number):
    clue = CLUES[number - 1]
    job = _job_of(clue.source)
    assert job in printed_set.jobs, job
    pages = squashed_pages(_pdf(printed_set, job))
    quote = squash(unicodedata.normalize("NFC", clue.quote))
    text = unicodedata.normalize("NFC", "".join(pages))
    assert quote in text, (clue.source, clue.quote)


def test_the_four_story_pdfs_exist_and_are_a4(printed_set):
    for job in STORY_JOBS.values():
        assert job in printed_set.jobs, job
        box = PdfReader(_pdf(printed_set, job)).pages[0].mediabox
        assert (round(float(box.width) / 72 * 25.4), round(float(box.height) / 72 * 25.4)) == (210, 297), job


def test_the_newspaper_embeds_exactly_two_images_and_the_masthead_is_on_page_one(printed_set):
    reader = PdfReader(_pdf(printed_set, STORY_JOBS["zeitungsartikel"]))
    assert sum(len(page.images) for page in reader.pages) == 2
    assert "AUTOTIMES" in squash(reader.pages[0].extract_text())
    assert len(reader.pages) == NEWSPAPER_PAGES


def test_no_image_file_name_reaches_any_story_pdf(printed_set):
    for job in STORY_JOBS.values():
        data = _pdf(printed_set, job).read_bytes()
        assert b"zeitungsartikel_bild" not in data and b".png" not in data.lower(), job


def test_every_story_pdf_has_empty_metadata_and_passes_the_layer_two_veil_scan(printed_set, setup):
    cfg, content, _ = setup
    ctx = veil.context(cfg, content.texts, content.terms)
    for job in STORY_JOBS.values():
        reader = PdfReader(_pdf(printed_set, job))
        assert not reader.metadata, job
        assert reader.xmp_metadata is None, job
        assert audience.scan_profile(job) == audience.PROFILE_STORY
        assert veil.scan_text(pdf_text(_pdf(printed_set, job)), job, ctx, layer="pdf") == [], job


def test_every_story_page_has_the_stamp_and_the_page_counter(printed_set):
    for job in STORY_JOBS.values():
        pages = squashed_pages(_pdf(printed_set, job))
        for number, text in enumerate(pages, start=1):
            assert len(STAMP.findall(text)) == 1, (job, number)
            assert f"Seite{number}von{len(pages)}" in text, (job, number)


def test_the_story_logs_have_no_missing_glyph_overfull_box_or_undefined_control_sequence(printed_set):
    for job in STORY_JOBS.values():
        log = unwrapped_log(printed_set.build_a / f"{job}.log")
        assert "Missing character" not in log, job
        assert "Overfull \\hbox" not in log, job
        assert "Overfull \\vbox" not in log, job
        assert "Undefined control sequence" not in log, job


def test_each_model_string_with_digits_is_on_its_page(printed_set, setup):
    _, _, models = setup
    for model in models:
        text = "".join(squashed_pages(_pdf(printed_set, model.job)))
        for string in model.printed_strings():
            if any(char.isdigit() for char in string):
                assert squash(string) in text, (model.job, string)
