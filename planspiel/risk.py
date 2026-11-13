"""Risk-matrix helpers (RISK-01, D-04, D-24): pure functions over `cfg.risk_matrix`; read by the validator's band
checks, print models and tests. Reads no formula operand (the unprotected damage comes from
`rules.unprotected_damage`)."""
from planspiel import fmt
from planspiel.config import RiskBand


def band_of(bands: tuple[RiskBand, ...], amount_k) -> RiskBand:
    """Band of an amount in thousand euros: the band with the largest inclusive lower limit not above the amount."""
    fitting = [band for band in bands if band.minimum <= amount_k]
    if not fitting:
        raise ValueError(f"Betrag {amount_k} liegt unter der ersten Bandgrenze")
    return max(fitting, key=lambda band: band.minimum)


# Zone id and the largest product of the two 1-based levels it covers; a layout constant of the printed 3 x 3 matrix,
# not a game number (A7).
ZONES = (("green", 2), ("yellow", 4), ("red", 9))


def zone_of(likelihood: int, impact: int) -> str:
    """Zone of a matrix cell from its 1-based likelihood and impact levels."""
    product = likelihood * impact
    for zone, limit in ZONES:
        if product <= limit:
            return zone
    raise ValueError(f"Zelle ({likelihood}, {impact}) liegt außerhalb der Matrix")


def band_ranges(bands: tuple[RiskBand, ...], words: dict) -> tuple[str, ...]:
    """Printed € range of each band, composed from the config limits (thousand euros) and the range words (D-04)."""

    def money(amount_k: int) -> str:
        return fmt.format_money(amount_k * 1000)

    last = len(bands) - 1
    ranges = []
    for index, band in enumerate(bands):
        if index == 0:
            ranges.append(f"{words['range_below']} {money(bands[1].minimum)}")
        elif index == last:
            ranges.append(f"{words['range_from']} {money(band.minimum)}")
        else:
            ranges.append(f"{money(band.minimum)} {words['range_to']} {money(bands[index + 1].minimum)}")
    return tuple(ranges)
