"""PDF smoke gate: reproducible rebuilds, fail-fast on a missing package, timeout kill.

Run with `uv run pytest -m pdf tests/test_print_smoke.py -v`.
"""
import re
import shutil
import time

import pytest

from planspiel import texbuild
from planspiel.stamp import stamp_tex
from planspiel.texbuild import TexBuildError
from tests.support.tex import PRINT_DIR, SMOKE_TEX, tex_skip_reason

pytestmark = pytest.mark.pdf

TEST_STAMP_TEX = stamp_tex("Stand 2000-01-01 · test000")


@pytest.fixture(scope="module")
def toolchain():
    reason = tex_skip_reason()
    if reason is not None:
        pytest.skip(reason)


@pytest.fixture(scope="module")
def engine():
    reason = tex_skip_reason(require_packages=False)
    if reason is not None:
        pytest.skip(reason)


def _smoke_document() -> dict:
    return {"smoke": SMOKE_TEX.read_text(encoding="utf-8")}


@pytest.fixture(scope="module")
def smoke_builds(toolchain, tmp_path_factory):
    """Warm-up build (font indexing), then two builds in separate directories."""
    root = tmp_path_factory.mktemp("smoke")
    kwargs = {"stamp_tex": TEST_STAMP_TEX}
    texbuild.build_documents(_smoke_document(), PRINT_DIR, root / "warmup", **kwargs)
    first = texbuild.build_documents(_smoke_document(), PRINT_DIR, root / "one", **kwargs)["smoke"]
    second = texbuild.build_documents(_smoke_document(), PRINT_DIR, root / "two", **kwargs)["smoke"]
    return first, second


def test_rebuild_is_byte_identical(smoke_builds):
    first, second = smoke_builds
    assert first.read_bytes() == second.read_bytes()


def test_last_page_label_resolves_to_page_two(smoke_builds):
    first, _ = smoke_builds
    aux = (first.parent / "smoke.aux").read_text(encoding="utf-8", errors="replace")
    assert re.search(r"\\newlabel\{LastPage\}\{\{\}\{2\}\}", aux)
    log = (first.parent / "smoke.log").read_text(encoding="utf-8", errors="replace")
    assert "undefined references" not in log


def test_pdf_carries_no_dates_producer_or_trailer_id(smoke_builds):
    data = smoke_builds[0].read_bytes()
    for key in (b"/CreationDate", b"/ModDate", b"/Producer"):
        assert key not in data
    assert not re.search(rb"/ID\s*\[", data)


def test_build_without_stamp_tex_fails_naming_the_file(toolchain, tmp_path):
    shutil.copyfile(PRINT_DIR / "planspiel.sty", tmp_path / "planspiel.sty")
    shutil.copyfile(SMOKE_TEX, tmp_path / "smoke.tex")
    assert not (tmp_path / "stamp.tex").exists()
    with pytest.raises(TexBuildError, match="stamp.tex"):
        texbuild.run_lualatex(tmp_path, "smoke.tex", timeout_s=120)
    assert not (tmp_path / "smoke.pdf").exists()


def test_missing_package_fails_fast_and_names_the_file(engine, tmp_path):
    (tmp_path / "bad.tex").write_text(
        r"\documentclass{article}" "\n" r"\usepackage{planspielmissingpkg}" "\n"
        r"\begin{document}x\end{document}" "\n",
        encoding="utf-8",
        newline="\n",
    )
    start = time.monotonic()
    with pytest.raises(TexBuildError, match="planspielmissingpkg"):
        texbuild.run_lualatex(tmp_path, "bad.tex", timeout_s=50)
    assert time.monotonic() - start < 60


def test_runaway_document_is_killed_at_the_time_limit(engine, tmp_path):
    job = tmp_path / "loop"
    job.mkdir()
    (job / "loop.tex").write_text(
        r"\documentclass{article}" "\n" r"\def\forever{\forever}" "\n"
        r"\begin{document}\forever\end{document}" "\n",
        encoding="utf-8",
        newline="\n",
    )
    start = time.monotonic()
    with pytest.raises(TexBuildError, match="5 s"):
        texbuild.run_lualatex(job, "loop.tex", timeout_s=5)
    assert time.monotonic() - start < 60
    shutil.rmtree(job)  # fails on Windows while a surviving process holds a file open
    assert not job.exists()
