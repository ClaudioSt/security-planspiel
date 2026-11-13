"""Risk-matrix helpers (RISK-01, D-04, D-24): pure functions over `cfg.risk_matrix`; read by the validator's band
checks, print models and tests. Reads no formula operand (the unprotected damage comes from
`rules.unprotected_damage`)."""
from planspiel.config import RiskBand


def band_of(bands: tuple[RiskBand, ...], amount_k) -> RiskBand:
    """Band of an amount in thousand euros: the band with the largest inclusive lower limit not above the amount."""
    fitting = [band for band in bands if band.minimum <= amount_k]
    if not fitting:
        raise ValueError(f"Betrag {amount_k} liegt unter der ersten Bandgrenze")
    return max(fitting, key=lambda band: band.minimum)
