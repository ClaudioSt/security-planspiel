"""band_of, the single band lookup (RISK-01, D-24): inclusive lower limits."""
import pytest

from planspiel.config import load_config
from planspiel.risk import band_of
from tests.support import CONFIG_PATH


@pytest.fixture(scope="module")
def bands():
    return load_config(CONFIG_PATH).risk_matrix.bands


@pytest.mark.parametrize(
    "amount, expected",
    [(0, "low"), (49, "low"), (50, "medium"), (149, "medium"), (150, "high"), (620, "high")],
)
def test_band_of_uses_inclusive_lower_limits(bands, amount, expected):
    assert band_of(bands, amount).id == expected


def test_band_of_rejects_an_amount_below_the_first_limit(bands):
    with pytest.raises(ValueError):
        band_of(bands, -1)
