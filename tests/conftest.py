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
