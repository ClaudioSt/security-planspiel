"""`.gitattributes`: LF normalisation for print sources, never for binary assets under print/ or content/assets/images."""
import subprocess

import pytest

from tests.support import REPO_ROOT


def _attrs(path: str) -> dict:
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "check-attr", "text", "eol", "binary", "--", path],
        capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL, timeout=30, check=True,
    ).stdout
    result = {}
    for line in out.splitlines():
        _, name, value = line.split(": ", 2)
        result[name] = value
    return result


@pytest.mark.parametrize(
    "path",
    [
        "print/planspiel.sty",
        "print/templates/angriff.tex.j2",
        "print/templates/cards/skin.tex",
        "print/miktex-packages.txt",
        "content/mhp_baseline.json",
    ],
)
def test_print_sources_are_normalised_to_lf(path):
    attrs = _attrs(path)
    assert attrs["text"] == "set" and attrs["eol"] == "lf", path


@pytest.mark.parametrize(
    "path",
    [
        "print/assets/skin.png",
        "print/assets/photo.jpg",
        "print/assets/page.pdf",
        "print/fonts/Arial.ttf",
        "print/fonts/Arial.otf",
        "content/assets/images/zeitungsartikel_bild_audit.png",
        "content/assets/images/zeitungsartikel_bild_fabrik.png",
    ],
)
def test_binary_assets_under_print_are_never_converted(path):
    attrs = _attrs(path)
    assert attrs["binary"] == "set", path
    assert attrs["text"] == "unset", path
