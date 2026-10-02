from fractions import Fraction


def round_half_away(n: int, d: int = 1) -> int:
    """n/d (d > 0) auf eine ganze Zahl runden, ab ,5 vom Betrag aufrunden (kaufmännisch).

    Druckbare Regel: "KZ-Änderung je Welle (Angriff + Events) auf ganze Zahl runden,
    ab ,5 vom Betrag aufrunden". Nur Ganzzahl-Arithmetik; Pythons eingebautes Runden
    (halb zur geraden Zahl) wird bewusst nicht benutzt.
    """
    if n >= 0:
        return (2 * n + d) // (2 * d)
    return -((-2 * n + d) // (2 * d))


def round_half_away_frac(x: Fraction) -> int:
    return round_half_away(x.numerator, x.denominator)


def started_steps(amount_eur, step_eur: int = 10_000) -> int:
    """Anzahl angefangener Schritte, "je angefangene 10.000 €".

    0 für Beträge <= 0; genau 10.000 € -> 1; 10.001 € -> 2. Phase 2 nutzt das für die
    Überziehungsstrafe.
    """
    if amount_eur <= 0:
        return 0
    return -((-amount_eur) // step_eur)


def exact_to_json(x):
    """int -> int; endlicher Dezimalbruch -> "2.24"; sonst "p/q". Fraction(str) liest alle zurück."""
    x = Fraction(x)
    if x.denominator == 1:
        return int(x)
    d, twos, fives = x.denominator, 0, 0
    while d % 2 == 0:
        d //= 2
        twos += 1
    while d % 5 == 0:
        d //= 5
        fives += 1
    if d != 1:
        return f"{x.numerator}/{x.denominator}"
    digits = max(twos, fives)
    scaled = x * 10**digits
    sign = "-" if scaled < 0 else ""
    s = str(abs(int(scaled))).rjust(digits + 1, "0")
    return f"{sign}{s[:-digits]}.{s[-digits:]}"
