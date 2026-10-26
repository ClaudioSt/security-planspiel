"""German number formatting for the printed worksheets: decimal comma, thousands dot, true minus (U+2212).

Only exact values are formatted. A value that has no finite decimal form raises ValueError, so a rounded number
can never reach a sheet by accident (D-08).
"""
from fractions import Fraction

from planspiel.review_text import format_eur
from planspiel.rounding import round_half_away_frac

MINUS = "−"
TIMES = "×"
DIVIDED = "÷"
PLUS_MINUS = "±"


def terminates(value) -> bool:
    """True when the value has a finite decimal expansion (denominator of the form 2^a * 5^b)."""
    denominator = Fraction(value).denominator
    for prime in (2, 5):
        while denominator % prime == 0:
            denominator //= prime
    return denominator == 1


def format_number(value) -> str:
    exact = Fraction(value)
    if not terminates(exact):
        raise ValueError(f"{exact} has no finite decimal form")
    magnitude = abs(exact)
    whole, rest = divmod(magnitude.numerator, magnitude.denominator)
    text = format_eur(whole)
    if rest:
        scaled = Fraction(rest, magnitude.denominator)
        fraction_text = ""
        while scaled:
            scaled *= 10
            digit = scaled.numerator // scaled.denominator
            fraction_text += str(digit)
            scaled -= digit
        text += "," + fraction_text
    return f"{MINUS}{text}" if exact < 0 else text


def format_signed(value) -> str:
    exact = Fraction(value)
    if exact == 0:
        return f"{PLUS_MINUS}0"
    text = format_number(exact)
    return text if exact < 0 else f"+{text}"


def format_money(amount_eur: int) -> str:
    text = format_number(amount_eur)
    return f"{text} €"


def format_factor(value) -> str:
    """Slope as a multiplication: '× 2', '× 1,2', or '× 17 ÷ 7' for a non-terminating fraction (D-08)."""
    exact = Fraction(value)
    if terminates(exact):
        return f"{TIMES} {format_number(exact)}"
    return f"{TIMES} {format_number(exact.numerator)} {DIVIDED} {format_number(exact.denominator)}"


def format_percent(value) -> str:
    return f"{format_number(Fraction(value) * 100)} %"


def format_approx(value, places: int = 2) -> str:
    """Facilitator-side value: exact text when it terminates within `places` decimals, otherwise '≈ ' plus the value
    rounded half away from zero to exactly `places` decimals (D-26 Q6). Never for a printed player worksheet."""
    if places < 1:
        raise ValueError("format_approx needs at least one decimal place")
    exact = Fraction(value)
    scale = 10**places
    if (exact * scale).denominator == 1:
        return format_number(exact)
    scaled = round_half_away_frac(exact * scale)
    whole, rest = divmod(abs(scaled), scale)
    text = f"{format_eur(whole)},{str(rest).rjust(places, '0')}"
    return f"≈ {MINUS}{text}" if scaled < 0 else f"≈ {text}"
