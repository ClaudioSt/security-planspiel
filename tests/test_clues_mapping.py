"""Hinweis -> Maßnahme: Zuordnung, Wichtigkeit, Prüfungen und Matrixspalte (BAL-07, D-17 ... D-19)."""
import dataclasses
from fractions import Fraction

import pytest

from planspiel import rules
from planspiel.cli import main
from planspiel.config import load_config
from planspiel.texts import (
    CLUE_SCORE_MIN,
    CLUE_SCORE_TOP,
    CLUE_WEIGHTS,
    Clue,
    FacilitatorView,
    check_clues,
    clue_scores,
    format_clue_matrix,
    load_clues,
    load_texts,
)
from tests.support import MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
CLUES_PATH = MINI_CONTENT_DIR / "clues.toml"
HEADER = "| Angriff | Nr. | Dokument | Abschnitt | Zitat | Warum | Maßnahmen (Gewicht) |"

CFG = load_config(MINI)
TEXTS = load_texts(MINI_CONTENT_DIR / "texte.toml")
CLUES = load_clues(CLUES_PATH)


def _codes(issues):
    return [(issue.code, issue.path) for issue in issues]


def _mapped(clues):
    return check_clues(CFG, TEXTS, clues, require_mapping=True)


def _replace(index, **changes):
    clues = list(CLUES)
    clues[index] = dataclasses.replace(clues[index], **changes)
    return tuple(clues)


def _bonus_measures():
    return {bonus.measure for wave in CFG.waves for bonus in wave.bonus_measures}


# ---- importance -----------------------------------------------------------------------------------------------


def _expected_importance():
    expected = {}
    for wave in CFG.waves:
        attack = CFG.attacks[wave.attack_id]
        slope = rules.kz_slope(attack.kz_at_full_damage, attack.kz_at_full_mitigation, attack.mitigation_cap)
        for bonus in wave.bonus_measures:
            expected[bonus.measure] = expected.get(bonus.measure, Fraction(0)) + bonus.bonus * slope
    return expected


def test_bonus_importance_is_bonus_times_slope_per_bonus_measure():
    importance = rules.bonus_importance(CFG)
    assert importance == _expected_importance()
    assert set(importance) == _bonus_measures()
    assert all(isinstance(value, Fraction) for value in importance.values())


def test_bonus_importance_adds_up_over_waves():
    wave = dataclasses.replace(CFG.waves[2], wave_id=4, bonus_measures=[CFG.waves[0].bonus_measures[0]])
    longer = dataclasses.replace(CFG, waves=[*CFG.waves, wave])
    m4 = CFG.waves[0].bonus_measures[0]
    attack = CFG.attacks[CFG.waves[0].attack_id]
    attack3 = CFG.attacks[wave.attack_id]
    slope = rules.kz_slope(attack.kz_at_full_damage, attack.kz_at_full_mitigation, attack.mitigation_cap)
    slope3 = rules.kz_slope(attack3.kz_at_full_damage, attack3.kz_at_full_mitigation, attack3.mitigation_cap)
    assert rules.bonus_importance(longer)[m4.measure] == m4.bonus * slope + m4.bonus * slope3


def test_the_mini_importance_order_is_m1_then_m2_tied_with_m4_then_m6():
    importance = rules.bonus_importance(CFG)
    assert importance["M1"] > importance["M2"] == importance["M4"] > importance["M6"]


# ---- loading --------------------------------------------------------------------------------------------------


def test_the_mini_clues_carry_the_mapping():
    assert [(clue.measures, clue.weight) for clue in CLUES] == [
        (("M4",), 2),
        (("M6",), 2),
        ((), 0),
        ((), 0),
        (("M1", "M2"), 3),
        (("M1",), 2),
    ]
    assert clue_scores(CLUES) == {"M4": 2, "M6": 2, "M1": 5, "M2": 3}


def test_a_clue_defaults_to_no_mapping():
    clue = Clue(attack="ot", source="story.x", quote="q", why="w")
    assert clue.measures == () and clue.weight == 0


def test_the_constants_are_pinned():
    assert CLUE_WEIGHTS == (1, 2, 3)
    assert CLUE_SCORE_MIN == 2
    assert CLUE_SCORE_TOP == 4


def _write_clues(tmp_path, body):
    path = tmp_path / "clues.toml"
    path.write_text(
        '[[clue]]\nattack = "ot"\nsource = "story.x"\nquote = "q"\nwhy = "w"\n' + body, encoding="utf-8", newline="\n"
    )
    return path


@pytest.mark.parametrize(
    "body",
    [
        'measures = "M4"\n',
        "measures = [4]\n",
        'measures = ["M4"]\nweight = "2"\n',
        'measures = ["M4"]\nweight = 2.0\n',
        'measures = ["M4"]\nweight = true\n',
    ],
)
def test_a_malformed_mapping_raises_a_value_error_naming_the_clue(tmp_path, body):
    with pytest.raises(ValueError, match="1"):
        load_clues(_write_clues(tmp_path, body))


def test_a_well_formed_mapping_loads(tmp_path):
    clues = load_clues(_write_clues(tmp_path, 'measures = ["M4", "M6"]\nweight = 3\n'))
    assert clues[0].measures == ("M4", "M6") and clues[0].weight == 3


def test_the_cli_reports_a_malformed_mapping(tmp_path, capsys):
    for name in ("texte.toml", "digit_allowlist.toml", "giveaway_terms.toml"):
        (tmp_path / name).write_text((MINI_CONTENT_DIR / name).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    _write_clues(tmp_path, 'measures = "M4"\n')
    assert main(["clues", "--config", str(MINI), "--content-dir", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "ERROR clues.toml" in out
    assert "1 Fehler, 0 Warnung(en)" in out


# ---- checks ---------------------------------------------------------------------------------------------------


def test_the_mapped_mini_clues_pass_with_and_without_the_requirement():
    assert check_clues(CFG, TEXTS, CLUES) == []
    assert _mapped(CLUES) == []


def test_the_real_content_carries_the_mapping_and_passes_the_default_check():
    cfg = load_config(REPO_ROOT / "simulation_config.json")
    texts = load_texts(REPO_ROOT / "content" / "texte.toml")
    clues = load_clues(REPO_ROOT / "content" / "clues.toml")
    mapped = [clue for clue in clues if clue.measures]
    assert mapped and all(1 <= clue.weight <= 3 for clue in mapped)
    assert all(clue.weight == 0 for clue in clues if not clue.measures)
    assert check_clues(cfg, texts, clues) == []
    assert check_clues(cfg, texts, clues, require_mapping=True) == []


def test_an_unknown_measure_is_reported_even_without_the_requirement():
    clues = _replace(0, measures=("M99",))
    assert _codes(check_clues(CFG, TEXTS, clues, require_mapping=False)) == [("clues.unknown_measure", "clues[1]")]


@pytest.mark.parametrize("weight", [0, 4, -1])
def test_a_weight_outside_one_to_three_with_measures_is_bad(weight):
    clues = _replace(0, weight=weight)
    assert _codes(check_clues(CFG, TEXTS, clues, require_mapping=False)) == [("clues.bad_weight", "clues[1]")]


def test_a_weight_without_measures_is_bad():
    clues = _replace(2, weight=1)
    assert _codes(check_clues(CFG, TEXTS, clues, require_mapping=False)) == [("clues.bad_weight", "clues[3]")]


def test_clues_on_non_bonus_measures_raise_nothing():
    assert "M5" not in _bonus_measures()
    clues = _replace(2, measures=("M4",), weight=1)
    assert _mapped(clues) == []


def test_a_bonus_measure_without_support_is_reported():
    clues = _replace(1, measures=(), weight=0)
    assert _codes(_mapped(clues)) == [("clues.unsupported_bonus", "clues.measures.M6")]
    assert check_clues(CFG, TEXTS, clues, require_mapping=False) == []


def test_a_bonus_measure_with_a_single_weak_clue_is_unsupported():
    clues = _replace(1, weight=1)
    assert _codes(_mapped(clues)) == [("clues.unsupported_bonus", "clues.measures.M6")]


def test_a_less_important_measure_outranking_a_more_important_one_is_not_graduated():
    clues = _replace(1, weight=3)
    # M6 scores 3, M4 2, M1 5, M2 3: M4 is more important than M6 but scores less.
    assert clue_scores(clues) == {"M4": 2, "M6": 3, "M1": 5, "M2": 3}
    issues = _mapped(clues)
    assert _codes(issues) == [("clues.not_graduated", "clues.measures.M4")]
    assert "M6" in issues[0].message


def test_equal_scores_for_different_importance_are_graduated():
    clues = _replace(5, weight=1)
    assert clue_scores(clues)["M1"] == 4 and clue_scores(clues)["M2"] == 3
    assert _mapped(clues) == []


def test_a_top_measure_below_the_floor_is_too_weak():
    clues = _replace(5, weight=1)
    clues = tuple(dataclasses.replace(clue, weight=2) if index == 4 else clue for index, clue in enumerate(clues))
    assert clue_scores(clues)["M1"] == 3
    assert _codes(_mapped(clues)) == [("clues.top_too_weak", "clues.measures.M1")]


def test_the_mapping_messages_are_german_errors():
    issues = _mapped(_replace(1, measures=(), weight=0))
    assert [issue.level for issue in issues] == ["error"]
    assert "Hinweis" in issues[0].message


# ---- facilitator matrix ---------------------------------------------------------------------------------------


def test_the_matrix_rows_carry_the_mapping_text():
    rows = FacilitatorView(CFG, TEXTS, CLUES).clue_matrix()
    assert [row.measures for row in rows] == ["M4 (2)", "M6 (2)", "", "", "M1 (3), M2 (3)", "M1 (2)"]


def test_the_matrix_text_is_empty_without_a_mapping():
    stripped = tuple(dataclasses.replace(clue, measures=(), weight=0) for clue in CLUES)
    assert {row.measures for row in FacilitatorView(CFG, TEXTS, stripped).clue_matrix()} == {""}


def test_the_console_matrix_has_seven_columns():
    rows = FacilitatorView(CFG, TEXTS, CLUES).clue_matrix()
    table = format_clue_matrix(rows).splitlines()
    assert table[0] == HEADER
    assert table[1] == "|" + "---|" * 7
    assert table[2].endswith("| M4 (2) |")
    assert table[4].endswith("|  |")


def test_the_cli_matrix_shows_the_column_and_passes(capsys):
    assert main(["clues", "--config", str(MINI), "--content-dir", str(MINI_CONTENT_DIR)]) == 0
    out = capsys.readouterr().out
    assert HEADER in out
    assert "M1 (3), M2 (3)" in out
    assert out.rstrip().endswith("0 Fehler, 0 Warnung(en)")


def test_the_pre_wave_view_never_sees_the_mapping():
    from planspiel.texts import PreAttackView

    texts = load_texts(MINI_CONTENT_DIR / "texte.toml")
    strings = PreAttackView(CFG, texts).strings()
    assert not any("Gewicht" in text for text in strings)
