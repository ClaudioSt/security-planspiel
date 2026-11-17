from fractions import Fraction

import pytest

from planspiel.rounding import exact_to_json, round_half_away, round_half_away_frac, started_steps


@pytest.mark.parametrize(
    ("n", "d", "expected"),
    [
        (11, 2, 6),
        (-11, 2, -6),
        (5, 2, 3),
        (-5, 2, -3),
        (-3, 2, -2),
        (1, 2, 1),
        (-1, 2, -1),
        (0, 1, 0),
        (3, 7, 0),
        (-3, 7, 0),
        (17, 7, 2),
        (-81, 7, -12),
    ],
)
def test_round_half_away(n, d, expected):
    assert round_half_away(n, d) == expected


def test_round_half_away_default_denominator_is_one():
    assert round_half_away(7) == 7
    assert round_half_away(-7) == -7


def test_round_half_away_frac():
    assert round_half_away_frac(Fraction(-11, 2)) == -6
    assert round_half_away_frac(Fraction(23, 2)) == 12


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (10_000, 1),
        (10_001, 2),
        (0, 0),
        (-5_000, 0),
        (1, 1),
        (20_000, 2),
        (20_001, 3),
        (Fraction(20_001, 2), 2),
    ],
)
def test_started_steps(amount, expected):
    assert started_steps(amount) == expected


def test_started_steps_custom_step():
    assert started_steps(35, step_eur=10) == 4


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Fraction(56, 25), "2.24"),
        (Fraction(-56, 25), "-2.24"),
        (Fraction(17, 7), "17/7"),
        (Fraction(1, 20), "0.05"),
        (Fraction(-1, 2), "-0.5"),
    ],
)
def test_exact_to_json_strings_round_trip(value, expected):
    result = exact_to_json(value)
    assert result == expected
    assert Fraction(result) == value


@pytest.mark.parametrize("value", [3, Fraction(6, 2), Fraction(-4)])
def test_exact_to_json_integral_values_are_ints(value):
    result = exact_to_json(value)
    assert isinstance(result, int)
    assert result == value
