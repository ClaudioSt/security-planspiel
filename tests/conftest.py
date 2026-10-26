from pathlib import Path
from typing import List, NamedTuple

import pytest

_REPORT: list[str] = []
_MAX_REPORT_LINES = 200


def pytest_addoption(parser):
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="rewrite tests/golden/*.json and print a 'tier code | field | old -> new' summary",
    )


@pytest.fixture
def update_golden(request):
    return request.config.getoption("--update-golden")


@pytest.fixture
def golden_report():
    return _REPORT


def pytest_terminal_summary(terminalreporter):
    if not _REPORT:
        return
    terminalreporter.section("golden updates (review before commit)")
    for line in _REPORT[:_MAX_REPORT_LINES]:
        terminalreporter.write_line(line)
    if len(_REPORT) > _MAX_REPORT_LINES:
        terminalreporter.write_line(f"... {len(_REPORT) - _MAX_REPORT_LINES} more lines")


SMOKE_TITLE = "Backup & Disaster Recovery – 100 % € −6 × ÷ ≤ ≥ _#$ \"aktiv\" \"Auch\" a--b <<c>> ,,d'' 0,5"


class PrintedSet(NamedTuple):
    out_a: Path
    out_b: Path
    build_a: Path
    build_b: Path
    jobs: List[str]


@pytest.fixture(scope="session")
def printed_set(tmp_path_factory):
    """Two real `planspiel print` runs over the whole print set plus an injected Jinja smoke document."""
    from planspiel import render
    from planspiel.cli import main
    from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT
    from tests.support.tex import PRINT_DIR, tex_skip_reason

    reason = tex_skip_reason()
    if reason is not None:
        pytest.skip(reason)
    original = render.render_all
    smoke_dir = REPO_ROOT / "tests" / "fixtures" / "print"

    def with_smoke(cfg, texts, template_dir, *args, **kwargs):
        documents = dict(original(cfg, texts, template_dir, *args, **kwargs))
        template = render.make_env(smoke_dir).get_template("smoke.tex.j2")
        documents["spieler-smoke"] = template.render(title=SMOKE_TITLE)
        return {job: documents[job] for job in sorted(documents)}

    root = tmp_path_factory.mktemp("printed_set")
    paths = {name: root / name for name in ("out_a", "out_b", "build_a", "build_b")}
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(render, "render_all", with_smoke)
        for suffix in ("a", "b"):
            code = main(
                [
                    "print",
                    "--config", str(CONFIG_PATH),
                    "--content-dir", str(CONTENT_DIR),
                    "--print-dir", str(PRINT_DIR),
                    "--out-dir", str(paths[f"out_{suffix}"]),
                    "--build-dir", str(paths[f"build_{suffix}"]),
                ]
            )
            assert code == 0, f"planspiel print (Lauf {suffix}) endete mit Exit-Code {code}"
    jobs = sorted(path.stem for path in paths["out_a"].glob("*.pdf"))
    return PrintedSet(paths["out_a"], paths["out_b"], paths["build_a"], paths["build_b"], jobs)
