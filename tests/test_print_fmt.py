"""German number formatting for the printed worksheets (PRINT-03, D-08)."""
from fractions import Fraction

import pytest

from planspiel.fmt import (
    format_approx,
    format_factor,
    format_money,
    format_number,
    format_percent,
    format_signed,
    terminates,
)


@pytest.mark.parametrize(
    "value, expected",
    [
        (23, "23"),
        (0, "0"),
        (20000, "20.000"),
        (Fraction(2, 5), "0,4"),
        (Fraction(6, 5), "1,2"),
        (Fraction(1, 4), "0,25"),
        (Fraction(31, 1), "31"),
        (-6, "−6"),
        (Fraction(-1, 2), "−0,5"),
        (Fraction(-3, 2), "−1,5"),
    ],
)
def test_format_number(value, expected):
    assert format_number(value) == expected


def test_format_number_rejects_non_terminating_fractions():
    with pytest.raises(ValueError):
        format_number(Fraction(17, 7))


@pytest.mark.parametrize(
    "value, expected", [(10, "+10"), (-6, "−6"), (0, "±0"), (Fraction(3, 2), "+1,5")]
)
def test_format_signed(value, expected):
    assert format_signed(value) == expected


@pytest.mark.parametrize("value, expected", [(160000, "160.000 €"), (0, "0 €"), (-2000, "−2.000 €")])
def test_format_money(value, expected):
    assert format_money(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (2, "× 2"),
        (Fraction(6, 5), "× 1,2"),
        (Fraction(17, 7), "× 17 ÷ 7"),
        (Fraction(1, 4), "× 0,25"),
    ],
)
def test_format_factor_prints_the_slope_exactly(value, expected):
    assert format_factor(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [(Fraction(1, 10), "10 %"), (0, "0 %"), (Fraction(1, 2), "50 %"), (Fraction(3, 10), "30 %")],
)
def test_format_percent(value, expected):
    assert format_percent(value) == expected


def test_format_percent_rejects_non_terminating_percentages():
    with pytest.raises(ValueError):
        format_percent(Fraction(1, 3))


def test_terminates():
    assert terminates(Fraction(17, 7)) is False
    assert terminates(Fraction(6, 5)) is True
    assert terminates(Fraction(1, 8)) is True
    assert terminates(3) is True


@pytest.mark.parametrize(
    "value, places, expected",
    [
        (Fraction(17, 7), 2, "≈ 2,43"),
        (Fraction(5, 2), 2, "2,5"),
        (Fraction(-1, 8), 2, "≈ −0,13"),
        (Fraction(1, 3), 1, "≈ 0,3"),
    ],
)
def test_format_approx(value, places, expected):
    assert format_approx(value, places) == expected


@pytest.mark.parametrize(
    "value, places, expected",
    [
        (Fraction(1, 8), 3, "0,125"),
        (Fraction(1, 8), 2, "≈ 0,13"),
        (7, 2, "7"),
        (Fraction(-7, 2), 2, "−3,5"),
        (Fraction(1, 3), 2, "≈ 0,33"),
        (Fraction(2, 3), 2, "≈ 0,67"),
        (Fraction(-2, 3), 2, "≈ −0,67"),
        (Fraction(12001, 5000), 2, "≈ 2,40"),
        (Fraction(1234567, 700), 2, "≈ 1.763,67"),
        (Fraction(-1, 300), 2, "≈ 0,00"),
        (Fraction(1, 200), 2, "≈ 0,01"),
    ],
)
def test_format_approx_edges(value, places, expected):
    assert format_approx(value, places) == expected


def test_format_approx_defaults_to_two_decimals_and_rounds_half_away_from_zero():
    assert format_approx(Fraction(17, 7)) == "≈ 2,43"
    assert format_approx(Fraction(1, 16)) == "≈ 0,06"
    assert format_approx(Fraction(-1, 16)) == "≈ −0,06"
    assert format_approx(Fraction(3, 8)) == "≈ 0,38"
    assert format_approx(Fraction(-3, 8)) == "≈ −0,38"
