"""Version stamp on every page of every built PDF (PRINT-11, ROADMAP SC4, D-19).

Run with `uv run pytest -m pdf tests/test_print_stamp_pdf.py -v`.
"""
import json
import re

import pytest
from pypdf import PdfReader

from planspiel import stamp, texbuild

pytestmark = pytest.mark.pdf

STAMP = re.compile(r"Stand\d{4}-\d{2}-\d{2}·[0-9a-f]{7}(?:\+lokal)?")


def _squashed(page) -> str:
    return re.sub(r"\s+", "", page.extract_text().replace(" ", " "))


def _stamps_of(pdf_path):
    reader = PdfReader(pdf_path)
    total = len(reader.pages)
    found = []
    for number, page in enumerate(reader.pages, start=1):
        text = _squashed(page)
        matches = STAMP.findall(text)
        assert len(matches) == 1, f"{pdf_path.name} Seite {number}: {len(matches)} Stempel statt genau einem"
        assert f"Seite{number}von{total}" in text, f"{pdf_path.name} Seite {number}: Seitenzähler fehlt"
        found.append(matches[0])
    return found


def test_every_page_of_every_pdf_carries_the_same_stamp(printed_set):
    assert printed_set.jobs, "kein Dokument gebaut"
    seen = set()
    for out in (printed_set.out_a, printed_set.out_b):
        for job in printed_set.jobs:
            seen.update(_stamps_of(out / f"{job}.pdf"))
    assert len(seen) == 1, f"mehrere Stempel in einem Satz: {sorted(seen)}"


def test_stamp_uses_the_dirty_marker_only_for_a_dirty_tree(printed_set):
    (found,) = {s for job in printed_set.jobs for s in _stamps_of(printed_set.out_a / f"{job}.pdf")}
    assert found.endswith("+lokal") == stamp.is_dirty(stamp.repo_root())


def test_tex_read_nothing_outside_the_hashed_set(printed_set):
    for job in printed_set.jobs:
        fls = printed_set.build_a / f"{job}.fls"
        assert fls.exists(), f"{fls.name} fehlt: lualatex lief ohne -recorder"
        allowed = {f"{job}.tex", f"{job}.aux", "stamp.tex", *texbuild.STATIC_FILES, *texbuild.ASSET_FILES}
        extra = stamp.recorded_local_inputs(fls, printed_set.build_a) - allowed
        assert not extra, f"{job}: TeX las Dateien außerhalb des gehashten Satzes: {sorted(extra)}"


def test_manifest_stamp_equals_the_stamp_on_the_pages(printed_set):
    manifest = json.loads((printed_set.out_a / "manifest.json").read_text(encoding="utf-8"))
    (found,) = {s for job in printed_set.jobs for s in _stamps_of(printed_set.out_a / f"{job}.pdf")}
    assert re.sub(r"\s+", "", manifest["stamp"]) == found
    assert set(manifest["documents"]) == set(printed_set.jobs)


def test_manifests_of_two_runs_are_byte_identical(printed_set):
    first = (printed_set.out_a / "manifest.json").read_bytes()
    second = (printed_set.out_b / "manifest.json").read_bytes()
    assert first == second
