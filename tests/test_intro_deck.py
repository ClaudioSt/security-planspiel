"""Regression test of the approved intro deck changes (LEG-02, D-18, D-19; RISK-09, D-19, D-26).

The deck `final_documents/Planspiel_Einführung + Grundlagen.pptx` is maintained by hand (no generator). Its rows were
approved in `.planning/phases/07-session-flow-handoff/07-DECK-CHECKLIST.md` and, for the Risiko-Matrix slide and the
35/40 minute figures, in `.planning/phases/07.1-risk-based-learning-chain-cia-risk-register-from-the-mechtec/
07.1-DECK-CHECKLIST.md`; this test pins them. Every minute figure and the team size are composed from
`session_schedule` at test time, so a later schedule or team-format change fails here until the deck follows. Set
`PLANSPIEL_DECK` to run the test against a working copy.

Slide 32 was turned into the protection-need slide (Schutzbedarf) per
`.planning/phases/07.2-protection-need-analysis-instead-of-likelihood-axis-per-asse/07.2-DECK-CHECKLIST.md`
(PROT-05, D-16); its expected words come from `content/texte.toml` `[sheets.register]` and the band order from
`cfg.risk_matrix.bands`, only the approved title and the literal "Maximumprinzip" are typed here.

Quick task 261123-oav added the Übungswelle slide 33 and fixed slides 31, 21 and 22 and the slide-number fields per
`.planning/quick/261123-oav-close-open-items-after-07-2-deck-review-/261123-oav-DECK-CHECKLIST.md` (follow-up to
PROT-05 and LEG-02); minute, title and material words come from config and texte.toml, only the approved slide texts
are typed here.

Quick task 261125-fsu (print RC9) removed the joint practice wave: the Übungswelle slide and the `wave_0` block are
gone, so every slide after the old slide 33 moved up by one (37 slides), and the Teamheft is named on the material
lines as "Teamheft (<chapter>)" because its sheets are handed out per block.
"""
import os
import re
from pathlib import Path

import pytest
from pptx import Presentation

from planspiel import audience, veil
from planspiel.config import load_config
from planspiel.texts import load_content
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT
from tests.test_readme_current import RETIRED_MATRIX_PATTERNS

DECK = REPO_ROOT / "final_documents" / "Planspiel_Einführung + Grundlagen.pptx"

# slide number -> block ids behind its minute figure (slide 36: closing plus debrief; slide 35 is composed per wave
# below); the Übungswelle slide is gone since quick task 261125-fsu
MINUTE_SLIDES = {
    26: ("break_1",),
    31: ("story_groups",),
    33: ("measures_budget",),
    34: ("break_2",),
    36: ("closing", "debrief"),
}
MINUTE_TEXT = {
    26: "{n} Minuten Pause",
    31: "{n} min",
    33: "{n} min",
    34: "{n} Minuten Pause",
    36: "{n} min",
}
SUMMED_SLIDES = {36}
MINUTE_FIGURE = re.compile(r"(\d+)\s*(?:Minuten|min)\b")
CLOCK_TIME = re.compile(r"(?<!\d)\d{1,2}:\d{2}(?!\d)")

# The wave slide names wave 1 and the other waves separately since the D-34 re-budget of wave 1 (user-approved
# 2026-11-04); it is slide 35 since the Übungswelle slide was removed again (quick task 261125-fsu)
WAVE_SLIDE = 35
WAVE_TEXT = "{first} min Welle 1, je {rest} min Welle 2 und 3"

TEAM_SIZE_SLIDE = 30
# the consulting firm of the game is MHP (user, 2026-11-24)
TEAM_SIZE_TEXT = "Beratungsteam von MHP aus {n} Personen"
PERSON_FIGURE = re.compile(r"[\d–\-]+\s*Personen")

FLOW_SLIDE = 28
FLOW_PHASES_TAIL = ("Angriffswellen",)
DATE_SLIDE = 1
DATE_FIGURE = re.compile(r"\d{1,2}\.\d{1,2}\.\d{4}")

# Material lines (approved rows) and the print_list jobs behind them
MATERIAL = {
    # the Teamheft is handed out as loose sheets per block and named "Teamheft (<chapter>)" with the printed page
    # titles (user, 2026-11-25); the waves slide drops "So funktioniert eine Welle" because the teams already hold it
    31: "Material: Unternehmenssteckbrief, Anfrage-Mail, Zeitungsartikel, Audit-Mail, Teamheft (Schutzbedarf und Risikoregister)",
    33: "Material: Maßnahmenkarten, Übungsblatt Welle 0, So funktioniert eine Welle, Teamheft (Budget und Planung, Tracking-Bogen)",
    35: "Material: Arbeitsblatt der Welle, Eventkarten",
    36: "Material: Eventkarte Budget Review, Teamheft (Return on Security, Budget Review)",
}
MATERIAL_JOBS = {
    31: ("spieler-unternehmenssteckbrief", "spieler-anfrage-mail", "spieler-zeitungsartikel", "spieler-audit-mail",
         "spieler-teamheft"),
    33: ("spieler-massnahmenkarten", "uebung-welle-0", "spieler-so-funktioniert-eine-welle", "spieler-teamheft"),
    35: ("angriff-1_ransomware", "angriff-2_ot", "angriff-3_exfil", "spieler-eventkarten"),
    36: ("spieler-eventkarten", "spieler-teamheft"),
}
# the Teamheft chapters named on each slide, as printed (texte.toml keys of the page titles)
TEAMHEFT_CHAPTER_KEYS = {
    31: ("sheets.register.page_title",),
    33: ("sheets.teamheft.planning_title", "sheets.tracking.title"),
    36: ("sheets.teamheft.ros_title", "sheets.teamheft.review_title"),
}
BARE_TEAMHEFT = re.compile(r"Teamheft(?! \()")

# PROT-05 (D-16): the Schutzbedarf slide sits directly after the story slide 31; checklist 07.2-DECK-CHECKLIST.md
# (it replaced the 07.1 Risiko-Matrix slide); title and second example row are the user-approved wording
NEED_SLIDE = 32
NEED_TITLE = "Schutzbedarf"
NEED_SECOND_ROW = ("Speiseplan der Kantine", "gering", "gering", "mittel")
CLOSING_REVIEW_TEXT = "Und wie gut stimmte euer Risikoregister im Rückblick (richtig, unterschätzt, überschätzt)?"
MONEY_FIGURE = re.compile(r"\d[\d.]*\s*(€|Euro)")

# Quick task 261123-oav: the damage-per-protection-goal wording on the story slide 31, the bridge line on theory
# slide 21 and the shown theory slide 22; the texts are the approved ones of the deck checklist
STORY_SLIDE = 31
RISK_ASSESSMENT_TEXT = (
    "Wie groß wäre der Schaden fürs Geschäft, wenn Vertraulichkeit, Integrität oder Verfügbarkeit verletzt würde? "
    "→ Welchen Schutzbedarf haben eure Werte?"
)
THEORY_RISK_SLIDE = 21
THEORY_BRIDGE_TEXT = "Im Planspiel tritt jeder Angriff ein: Bewertet wird nur der Schaden je Schutzziel (Schutzbedarf)."
THEORY_NEED_SLIDE = 22
RETIRED_NEED_TITLE = "Sicherheitsbedarf"
THEORY_NEED_QUESTIONS = (
    "Welche Werte braucht das Unternehmen: Daten, Anlagen, Know-how?",
    "Wie groß wäre der Schaden fürs Geschäft: gering, mittel oder hoch?",
    "Was wäre schlimmer: Offenlegung (C), Verfälschung (I) oder Ausfall (A) von IT-Systemen?",
    "Welches Schutzziel trifft den Wert am härtesten? Das ist das Hauptziel im Register.",
    "Verlangen Gesetze (z.B. DSGVO) oder Kunden (z.B. Audit, Zertifikate) mehr Schutz?",
)

MEASURE_CATEGORY_TEXT = {
    "Physische": "Schutz von Gebäuden, Räumen und Hardware vor unbefugtem Zutritt und Umwelteinflüssen.",
    "Technische": "Technische Verfahren und Systeme, die Daten und IT-Systeme schützen.",
    "Organisatorische": "Regeln, Abläufe und Schulungen, die den sicheren Umgang mit IT festlegen.",
}

# Decision (d): "Phishing" is generic teaching content on these slides and stays (checklist, ## Approval)
ACCEPTED_STORY_HITS = {19: ["phishing"], 21: ["phishing"]}
OLD_PHRASES = ("3–4 Personen", "350.000", "150.000", "Bewilligtes Budget", "Spielplan / Vorlage")
BOARD_TERM = re.compile(r"Whiteboard|Pinnwand|Tafel", re.IGNORECASE)


def _texts_of(shapes):
    for shape in shapes:
        if shape.shape_type == 6:
            yield from _texts_of(shape.shapes)
        elif shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                yield "".join(run.text for run in paragraph.runs)
        elif getattr(shape, "has_table", False) and shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    for paragraph in cell.text_frame.paragraphs:
                        yield "".join(run.text for run in paragraph.runs)


def _slide_text(slide) -> str:
    return "\n".join(_texts_of(slide.shapes))


@pytest.fixture(scope="module")
def slides():
    presentation = Presentation(str(Path(os.environ.get("PLANSPIEL_DECK", DECK))))
    return list(presentation.slides)


@pytest.fixture(scope="module")
def slide_texts(slides):
    return {number: _slide_text(slide) for number, slide in enumerate(slides, start=1)}


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def content():
    return load_content(CONTENT_DIR)


def _expected_minutes(cfg, number: int) -> int:
    by_id = {block.id: block.minutes for block in cfg.session_schedule.blocks}
    figures = [by_id[block_id] for block_id in MINUTE_SLIDES[number]]
    if number in SUMMED_SLIDES:
        return sum(figures)
    assert len(set(figures)) == 1, f"slide {number} shows one figure but the blocks differ: {figures}"
    return figures[0]


# --- minute figures ----------------------------------------------------------------------------------------------


@pytest.mark.parametrize("number", sorted(MINUTE_SLIDES))
def test_minute_figure_equals_the_session_schedule(cfg, slide_texts, number):
    expected = MINUTE_TEXT[number].format(n=_expected_minutes(cfg, number))
    assert expected in slide_texts[number]
    figures = {int(figure) for figure in MINUTE_FIGURE.findall(slide_texts[number])}
    assert figures == {_expected_minutes(cfg, number)}


def test_wave_slide_composes_the_minutes_per_wave_from_the_session_schedule(cfg, slide_texts):
    by_id = {block.id: block.minutes for block in cfg.session_schedule.blocks}
    assert by_id["wave_2"] == by_id["wave_3"], "the wave slide shows one figure for waves 2 and 3"
    expected = WAVE_TEXT.format(first=by_id["wave_1"], rest=by_id["wave_2"])
    assert expected in slide_texts[WAVE_SLIDE]
    figures = {int(figure) for figure in MINUTE_FIGURE.findall(slide_texts[WAVE_SLIDE])}
    assert figures == {by_id["wave_1"], by_id["wave_2"]}


@pytest.mark.parametrize("number", [26, 34])
def test_break_slides_carry_no_clock_time(slide_texts, number):
    assert not CLOCK_TIME.search(slide_texts[number])
    assert not re.search(r"bis\s*\d", slide_texts[number])


# --- team size (D-19) --------------------------------------------------------------------------------------------


def test_team_size_follows_the_project_format(cfg, slide_texts):
    text = slide_texts[TEAM_SIZE_SLIDE]
    assert TEAM_SIZE_TEXT.format(n=cfg.session_schedule.persons_per_team) in text
    figures = PERSON_FIGURE.findall(text)
    assert figures == [f"{cfg.session_schedule.persons_per_team} Personen"]


# --- approved text rows ------------------------------------------------------------------------------------------


def test_title_slide_has_no_date(slide_texts):
    assert not DATE_FIGURE.search(slide_texts[DATE_SLIDE])


@pytest.mark.parametrize("number", sorted(MATERIAL))
def test_material_line_matches_the_print_list(cfg, slide_texts, number):
    assert MATERIAL[number] in slide_texts[number]
    jobs = {row.job for row in cfg.session_schedule.print_list}
    assert set(MATERIAL_JOBS[number]) <= jobs


def test_measures_slide_describes_measures_not_threats(slide_texts):
    text = slide_texts[23]
    for label, description in MEASURE_CATEGORY_TEXT.items():
        assert label in text
        assert description in text
    for stem in ("Diese Bedrohungen entstehen", "Natürliche und physikalische Gefahren", "Hierzu zählen Bedrohungen"):
        assert stem not in text


def test_budget_slide_names_no_amount(slide_texts):
    assert "Budget zur Umsetzung eurer Maßnahmen" in slide_texts[33]
    assert "€" not in slide_texts[33]


def test_last_block_slide_is_closing_and_debriefing(slide_texts):
    assert "Abschluss und Debriefing" in slide_texts[36]
    assert "Endergebnis und Reflexion" not in slide_texts[36]
    assert CLOSING_REVIEW_TEXT in slide_texts[36]


def test_no_old_phrase_and_no_board_term_remains(slide_texts):
    for number, text in slide_texts.items():
        for phrase in OLD_PHRASES:
            assert phrase not in text, (number, phrase)
        assert not BOARD_TERM.search(text), number


def test_the_deck_has_the_expected_slides(slides):
    assert len(slides) == 37


# --- Übungswelle slide and the bridged theory slides (quick task 261123-oav) -------------------------------------


def test_there_is_no_practice_wave_slide_any_more(slides, content, cfg):
    # quick 261125-fsu: the practice sheet is a handout of the Maßnahmen und Budget block, not a block of its own
    practice_label = content.texts.subtree("sheets.ablauf")["practice_label"]
    for number, slide in enumerate(slides, start=1):
        title = slide.shapes.title.text_frame.text if slide.shapes.title is not None else ""
        assert title != practice_label, number
    assert not [block for block in cfg.session_schedule.blocks if block.wave == 0]


def _material_line(content, number):
    labels = content.texts.subtree("sheets.ablauf.print")
    chapters = ", ".join(content.texts.get(key) for key in TEAMHEFT_CHAPTER_KEYS[number])
    teamheft = f"{labels['spieler-teamheft']} ({chapters})"
    items = {
        31: [labels[job] for job in MATERIAL_JOBS[31] if job != "spieler-teamheft"],
        33: [
            labels["spieler-massnahmenkarten"],
            f"{labels['uebung-welle-0']} Welle 0",
            labels["spieler-so-funktioniert-eine-welle"],
        ],
        36: [f"Eventkarte {content.texts.get('sheets.teamheft.review_title')}"],
    }[number]
    return "Material: " + ", ".join([*items, teamheft])


@pytest.mark.parametrize("number", [31, 33, 36])
def test_material_line_names_the_teamheft_by_its_printed_chapters(content, slide_texts, number):
    line = _material_line(content, number)
    assert line == MATERIAL[number]
    assert line in slide_texts[number]


def test_the_waves_slide_lists_only_the_attack_sheet_and_the_event_cards(content, slide_texts):
    labels = content.texts.subtree("sheets.ablauf.print")
    assert "So funktioniert eine Welle" not in slide_texts[WAVE_SLIDE]
    assert labels["spieler-eventkarten"] in MATERIAL[WAVE_SLIDE]


def test_no_material_line_names_the_teamheft_without_a_chapter(slide_texts):
    for number, text in slide_texts.items():
        for line in text.splitlines():
            if line.startswith("Material:"):
                assert not BARE_TEAMHEFT.search(line), (number, line)


def test_block_slides_follow_the_session_schedule(cfg):
    slide_of = {block_id: number for number, ids in MINUTE_SLIDES.items() for block_id in ids}
    slide_of.update({f"wave_{wave}": WAVE_SLIDE for wave in (1, 2, 3)})
    numbers = [slide_of[block.id] for block in cfg.session_schedule.blocks if block.id in slide_of]
    assert numbers == sorted(numbers), numbers
    ids = [block.id for block in cfg.session_schedule.blocks]
    assert ids.index("story_groups") < ids.index("measures_budget")
    assert slide_of["story_groups"] < slide_of["measures_budget"]


def test_slide_number_fields_show_the_slide_position(slides):
    for number, slide in enumerate(slides, start=1):
        cached = slide._element.xpath('.//a:fld[@type="slidenum"]/a:t/text()')
        assert all(text == str(number) for text in cached), (number, cached)


def test_story_slide_assesses_damage_per_protection_goal(slide_texts):
    text = slide_texts[STORY_SLIDE]
    assert RISK_ASSESSMENT_TEXT in text
    assert "Schutzbedarf" in text
    for pattern in RETIRED_MATRIX_PATTERNS:
        assert re.search(pattern, text.replace("‑", "-"), re.IGNORECASE) is None, pattern


def test_theory_risk_slide_keeps_the_method_and_bridges_to_the_game(slide_texts):
    assert "Eintrittswahrscheinlichkeit" in slide_texts[THEORY_RISK_SLIDE]
    assert THEORY_BRIDGE_TEXT in slide_texts[THEORY_RISK_SLIDE]


def test_theory_need_slide_is_titled_schutzbedarf_and_shown(slides, slide_texts):
    slide = slides[THEORY_NEED_SLIDE - 1]
    assert slide.shapes.title.text_frame.text == NEED_TITLE
    assert slide._element.get("show") != "0"
    for number, text in slide_texts.items():
        assert RETIRED_NEED_TITLE not in text, number


def test_theory_need_slide_asks_the_protection_need_questions_in_order(slides):
    # Quick task 261123-oav follow-up: the five questions lead through the method (values, damage, C/I/A,
    # maximum principle, external requirements) instead of generic security requirements
    slide = slides[THEORY_NEED_SLIDE - 1]
    questions = sorted(
        (shape.top, shape.text_frame.text.strip())
        for shape in slide.shapes
        if shape.has_text_frame and shape.name.startswith("Textfeld")
    )
    assert tuple(text for _, text in questions) == THEORY_NEED_QUESTIONS


# --- Schutzbedarf slide (PROT-05, D-16) --------------------------------------------------------------------------


def _need_table(slide):
    tables = [shape.table for shape in slide.shapes if getattr(shape, "has_table", False) and shape.has_table]
    assert len(tables) == 1, "the Schutzbedarf slide holds exactly one table"
    return tables[0]


def test_need_slide_is_visible_and_titled(slides):
    slide = slides[NEED_SLIDE - 1]
    assert slide._element.get("show") != "0"
    assert slide.shapes.title.text_frame.text == NEED_TITLE


def test_need_slide_table_rates_assets_by_goal(slides, content, cfg):
    register = content.texts.subtree("sheets.register")
    band_words = [register["bands"][band.id] for band in cfg.risk_matrix.bands]
    table = _need_table(slides[NEED_SLIDE - 1])
    assert len(table.columns) == 4, "asset and the three protection goals, no gesamt column"
    header = [table.cell(0, column).text_frame.text for column in range(4)]
    goals = register["goals"]
    assert header == [register["need_head_asset"], goals["c"], goals["i"], goals["a"]]
    rows = [[table.cell(row, column).text_frame.text for column in range(4)] for row in range(1, len(table.rows))]
    assert len(rows) == 2
    for asset, *ratings in rows:
        assert asset
        assert all(word in band_words for word in ratings), rows
    example = register["need_example"]
    assert rows[0] == [example["asset"], example["c"], example["i"], example["a"]]
    assert tuple(rows[1]) == NEED_SECOND_ROW
    widths = [column.width for column in table.columns]
    assert max(widths[1:]) - min(widths[1:]) <= 1, "the three rating columns share the width"
    assert sum(widths) >= 9_000_000, "the table keeps its width after the column is gone"


def test_need_slide_uses_the_teamheft_vocabulary(content, slide_texts):
    register = content.texts.subtree("sheets.register")
    words = [
        register["need_title"],
        *register["bands"].values(),
        register["title"],
        register["head_goal"],
        register["head_review"],
    ]
    for word in words:
        assert word in slide_texts[NEED_SLIDE], word
    for gone in ("gesamt", "Maximumprinzip"):
        assert gone not in slide_texts[NEED_SLIDE], gone


def test_need_slide_shows_no_likelihood_or_zone(slides, slide_texts):
    text = slide_texts[NEED_SLIDE].replace("‑", "-")
    for pattern in RETIRED_MATRIX_PATTERNS:
        assert re.search(pattern, text, re.IGNORECASE) is None, pattern
    table = _need_table(slides[NEED_SLIDE - 1])
    for row in table.rows:
        for cell in row.cells:
            assert cell._tc.tcPr is None or not cell._tc.tcPr.xpath("./a:solidFill"), "no cell fill, no zone colour"


def test_need_slide_names_no_company_attack_or_amount(cfg, content, slide_texts):
    text = slide_texts[NEED_SLIDE]
    assert "mechtech" not in text.lower()
    assert "€" not in text and "Euro" not in text
    assert not MONEY_FIGURE.search(text)
    ctx = veil.context(cfg, content.texts, content.terms)
    assert veil.name_hits(text, ctx, audience.PROFILE_STORY) == []


# --- flow overview (D-19) ----------------------------------------------------------------------------------------


def _flow_phases(content) -> list:
    words = content.texts.subtree("sheets.ablauf")
    blocks = words["blocks"]
    return [
        blocks["intro"]["label"],
        blocks["story_groups"]["label"],
        blocks["measures_budget"]["label"],
        *FLOW_PHASES_TAIL,
        f"{blocks['closing']['label']} und {blocks['debrief']['label']}",
    ]


def _flow_columns(slide) -> list:
    """(number, label) of every phase group on the flow slide, left to right."""
    columns = []
    for shape in slide.shapes:
        if shape.shape_type == 6:
            texts = [t for t in _texts_of(shape.shapes) if t.strip()]
            assert len(texts) == 2, texts
            columns.append((shape.left, texts[0], texts[1]))
    return [(number, label) for _, number, label in sorted(columns)]


def test_flow_overview_is_visible_and_lists_the_phases_in_order(slides, content):
    slide = slides[FLOW_SLIDE - 1]
    assert slide._element.get("show") != "0"
    assert _flow_columns(slide) == [(str(i), phase) for i, phase in enumerate(_flow_phases(content), start=1)]


def test_flow_overview_has_no_attack_name_no_amount_and_no_minutes(cfg, content, slide_texts):
    text = slide_texts[FLOW_SLIDE]
    ctx = veil.context(cfg, content.texts, content.terms)
    assert veil.name_hits(text, ctx, audience.PROFILE_NAMES) == []
    assert not re.search(r"€|EUR|Euro", text)
    assert not MINUTE_FIGURE.search(text)
    assert not CLOCK_TIME.search(text)


def test_no_slide_names_an_attack_and_story_hits_are_the_accepted_ones(cfg, content, slide_texts):
    ctx = veil.context(cfg, content.texts, content.terms)
    for number, text in slide_texts.items():
        assert veil.name_hits(text, ctx, audience.PROFILE_NAMES) == [], number
    story = {
        number: hits
        for number, text in slide_texts.items()
        if (hits := veil.name_hits(text, ctx, audience.PROFILE_STORY))
    }
    assert story == ACCEPTED_STORY_HITS


def test_deck_uses_the_print_vocabulary_for_the_damage_scale(slide_texts):
    # RC6 proofreading (quick 261125-0f4): the print material calls gering/mittel/hoch a "Stufe", and "oder"
    # takes the singular verb; the deck follows
    for number, text in slide_texts.items():
        assert "Band" not in text, number
        assert "verletzt würden" not in text, number


def test_story_slide_hands_out_only_the_first_teamheft_chapter(slide_texts):
    assert "Teamheft (Schutzbedarf und Risikoregister)" in slide_texts[31]
    assert slide_texts[31].count("Teamheft") == 1
