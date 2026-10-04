"""Druckfertige Texte zum Budget Review, abgeleitet aus der Config (nur exakte Ganzzahlen)."""
from typing import List, Tuple


def format_eur(amount_eur: int) -> str:
    """Betrag in Euro mit Punkt als Tausendertrenner; negative Werte mit echtem Minuszeichen (U+2212)."""
    text = f"{abs(amount_eur):,}".replace(",", ".")
    return f"\u2212{text}" if amount_eur < 0 else text


def penalty_rows(kz_per_step: int, step_k: int, max_kz: int = 100) -> List[Tuple[int, int, int]]:
    """Zeilen der Überziehungstabelle als (von_eur, bis_eur, kz_delta).

    Eine Zeile je angefangener Schrittweite, bis die Strafe allein die KZ-Skala erreicht.
    """
    count = -(-max_kz // kz_per_step)
    return [
        ((i - 1) * step_k * 1000 + 1, i * step_k * 1000, -kz_per_step * i)
        for i in range(1, count + 1)
    ]


def _tier_value_text(value: int) -> str:
    if value == 0:
        return "±0"
    return f"+{value}" if value > 0 else f"−{-value}"


def boundary_text(tiers: List[List[int]]) -> str:
    """Kartentext der Restbudget-Stufen, erzeugt aus der Stufenliste (k€, erstes Minimum 0).

    D-16: "ab" gilt einschließlich, dieselbe Liste nutzt die Simulation (≥).
    """
    if len(tiers) == 1:
        return f"ab 0 € → {_tier_value_text(tiers[0][1])}"
    parts = [f"0 – {format_eur(tiers[1][0] * 1000 - 1)} € → {_tier_value_text(tiers[0][1])}"]
    parts.extend(
        f"ab {format_eur(minimum * 1000)} € → {_tier_value_text(value)}" for minimum, value in tiers[1:]
    )
    return ", ".join(parts)
