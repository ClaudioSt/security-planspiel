"""Play-through review of print RC7 (quick 261125-djw, print RC8): behaviour changes pinned test-first.

Wording-only changes are pinned next to their texts; this module covers what the code prints differently.
"""
import pytest

from planspiel import render
from planspiel.config import load_config
from planspiel.texts import load_clues, load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"
BS = chr(92)
ROWSTRUT = BS + "rowstrutgrid{}"
SHADED = BS + "shadedcell{}"


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def texts():
    return load_texts(CONTENT_DIR / "texte.toml")


@pytest.fixture(scope="module")
def clues():
    return load_clues(CONTENT_DIR / "clues.toml")


@pytest.fixture(scope="module")
def rendered(cfg, texts, clues):
    return render.render_all(cfg, texts, TEMPLATES, clues)


def _tracking_row(source: str, label: str) -> str:
    return next(line for line in source.splitlines() if line.startswith(ROWSTRUT) and label in line)


def test_v1_the_event_rows_of_the_tracking_sheet_print_no_grey_cell_in_a_wave_column(texts, rendered):
    """Only the Start and the Budget Review column stay crossed out: no wave column tells where an event comes."""
    source = rendered["spieler-teamheft"]
    for key in ("row_external_budget", "row_external_opex"):
        line = _tracking_row(source, texts.get(f"sheets.tracking.{key}"))
        cells = line.split("&")
        assert line.count(SHADED) == 2, (key, line)
        assert SHADED in cells[1] and SHADED in cells[-1], key
