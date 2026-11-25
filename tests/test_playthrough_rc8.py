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


def test_d2_the_print_list_says_to_print_everything_single_sided(texts):
    assert texts.get("sheets.ablauf.print_intro").startswith("Druckt alles einseitig.")


def test_d2_the_start_column_of_the_tracking_sheet_is_instructed_twice(texts):
    for key in ("sheets.tracking.intro", "sheets.ablauf.blocks.measures_budget.direction"):
        text = texts.get(key)
        assert "Spalte Start" in text, key
        assert all(word in text for word in ("KZ-Start", "Init-Kosten", "Restbudget")), key
    assert "Tier-Budget minus Init-Kosten" in texts.get("sheets.ablauf.blocks.measures_budget.direction")


def test_d2_the_attack_sheets_say_to_enter_zero_without_a_kz_event_card(texts):
    assert texts.get("sheets.angriff.events_hint").endswith("Nennt keine Eventkarte eine KZ-Wirkung, tragt ±0 ein.")


def test_d2_teamheft_page_five_sends_the_teams_back_to_the_tracking_sheet(texts):
    text = texts.get("sheets.teamheft.review_intro")
    assert text.endswith("in der Spalte Budget Review ein und berechnet dort die KZ final.")
    assert texts.get("sheets.tracking.title") in text


def test_d2_the_closing_direction_keeps_the_teamheft_with_the_teams_and_notes_the_comparison(texts):
    text = texts.get("sheets.ablauf.blocks.closing.direction")
    assert "Sammelt" not in text and "einsammeln" not in text
    assert "berechnen zuletzt im Tracking-Bogen die KZ final" in text
    assert "Notiert je Team KZ final und RoS in der Vergleichstabelle" in text
    assert "die Teamhefte bleiben bei den Teams" in text
    assert texts.get("sheets.debrief.compare_title") in text


def test_d3_the_tracking_hint_says_what_to_enter_when_a_wave_has_no_event_of_that_kind(texts):
    text = texts.get("sheets.tracking.external_hint")
    assert "kein Event dieser Art" in text and "leer" in text and "null" in text


# ---- play-through findings with a code change (C1, B2, E1, E2) ------------------------------------------------------


def _joined(line):
    return "".join(part if isinstance(part, str) else "▢" for part in line)


def test_c1_step_five_names_the_attack_value_kz_angriff_like_step_seven(cfg, texts):
    from planspiel.printmodel import build_attack_sheets

    attack_kz = texts.get("sheets.angriff.label_kz_attack")
    for sheet in build_attack_sheets(cfg, texts):
        for case in sheet.cases[:2]:
            assert f" · {attack_kz}: " in case.outcome, sheet.job
            assert " · KZ: " not in case.outcome, sheet.job
        assert _joined(sheet.cases[2].lines[1]).startswith(f"{attack_kz} = "), sheet.job


def test_b2_the_recovery_line_has_a_wide_first_box_and_keeps_the_last_five_parts_together(cfg, texts, rendered):
    from planspiel.printmodel import Box, build_attack_sheets

    sheet = build_attack_sheets(cfg, texts)[0]
    assert [part.size for part in sheet.recovery_line if isinstance(part, Box)] == ["long", "short", "long"]
    source = rendered[sheet.job]
    start = source.index(BS + "fillline{" + sheet.recovery_line[0])
    assert BS + "mbox{" + BS + "ibox{long}" in source[start : start + 400]
    gap = source[source.rindex(BS + "end{tabularx}", 0, start) : start]
    assert BS + "vspace{2mm}" in gap, "the line must not sit directly on the lower table rule"


def test_e1_the_reality_hint_is_a_hint_line_of_its_own(cfg, texts, rendered):
    from planspiel.printmodel import build_attack_sheets

    for sheet in build_attack_sheets(cfg, texts):
        assert BS + "hint{" + render.tex_escape(sheet.reality_hint) + "}" in rendered[sheet.job], sheet.job
    assert texts.get("sheets.angriff.reality_hint").startswith("Tragt die R-Nummer ein oder")


def test_e2_the_planning_sum_row_shades_only_its_label_and_closes_the_level_and_risk_cells(texts, rendered):
    source = rendered["spieler-teamheft"]
    row = next(
        line
        for line in source.splitlines()
        if line.startswith(BS + "rowstrut{}") and BS + "cellcolor{mhplight}" in line and BS + "textbf{Summe}" in line
    )
    assert BS + "rowcolor" not in row
    cells = row.split("&")
    assert len(cells) == 5
    assert BS + "cellcolor{mhplight}" in cells[0]
    assert SHADED in cells[1] and SHADED in cells[4], row
    assert SHADED not in cells[2] and SHADED not in cells[3], row
