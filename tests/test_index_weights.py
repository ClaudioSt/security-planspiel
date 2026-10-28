"""k measurement for the Final-Index (BAL-03, D-15): pooled in-budget IQR, KZ share and the recommended integer k."""
from fractions import Fraction

import pytest

from planspiel import index_weights
from planspiel.config import FinalIndexWeights
from planspiel.enumerate import enumerate_tier
from planspiel.report import nearest_rank
from tests.support import REPO_ROOT, candidate, harness

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
TIERS = ("low", "medium", "high")


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


@pytest.fixture(scope="module")
def mini_stores(mini):
    return {tier: enumerate_tier(mini, tier) for tier in TIERS}


def _naive_iqr(stores):
    from planspiel import rules

    kz_values, ros_values = [], []
    for store in stores:
        for i in range(len(store)):
            record = store.record(i)
            if record.over_budget or record.own_cost == 0:
                continue
            kz_values.append(record.kz_final)
            ros_values.append(rules.ros(store.base_losses, Fraction(record.damage_eur, 1000), record.own_cost))
    kz_values.sort()
    ros_values.sort()
    return (
        nearest_rank(kz_values, 75) - nearest_rank(kz_values, 25),
        nearest_rank(ros_values, 75) - nearest_rank(ros_values, 25),
    )


def test_pooled_iqr_equals_the_naive_computation(mini_stores):
    stores = list(mini_stores.values())
    iqr_kz, iqr_ros = index_weights.pooled_iqr(stores)
    assert (iqr_kz, iqr_ros) == _naive_iqr(stores)
    assert iqr_kz > 0 and iqr_ros > 0
    assert isinstance(iqr_ros, Fraction)


def test_pooled_iqr_of_a_single_store_matches_too(mini_stores):
    store = mini_stores["medium"]
    assert index_weights.pooled_iqr([store]) == _naive_iqr([store])


def test_kz_share_formula():
    assert index_weights.kz_share(17, Fraction(705, 1000), 20) == Fraction(17) / (17 + 20 * Fraction(705, 1000))


def test_recommended_k_is_the_multiple_of_five_nearest_to_the_two_to_one_split():
    k_raw, k = index_weights.recommended_k(18, Fraction(44, 100))
    assert k_raw == Fraction(225, 11)
    assert k == 20


@pytest.mark.parametrize(
    ("iqr_kz", "iqr_ros", "expected"),
    [(25, Fraction(1, 2), 25), (11, Fraction(1, 2), 10), (15, Fraction(1, 2), 15)],
)
def test_recommended_k_rounds_to_multiples_of_five(iqr_kz, iqr_ros, expected):
    _, k = index_weights.recommended_k(iqr_kz, iqr_ros)
    assert k == expected and k % 5 == 0


def test_recommended_k_breaks_ties_away_from_zero():
    # k_raw = 12.5 is the midpoint between 10 and 15
    k_raw, k = index_weights.recommended_k(Fraction(25, 2), Fraction(1, 2))
    assert k_raw == Fraction(25, 2)
    assert k == 15


def test_recommended_k_needs_a_ros_spread():
    with pytest.raises(ValueError):
        index_weights.recommended_k(18, Fraction(0))


def test_constants():
    assert index_weights.TARGET_KZ_SHARE == Fraction(2, 3)
    assert index_weights.KZ_SHARE_MIN == Fraction(3, 5)
    assert index_weights.KZ_SHARE_MAX == Fraction(73, 100)
    assert index_weights.K_STEP == 5


def test_final_index_block_reports_pooled_and_per_tier_values(mini_stores):
    weights = FinalIndexWeights(Fraction(1), Fraction(1))
    block = index_weights.final_index_block(mini_stores, weights)
    pooled_kz, pooled_ros = index_weights.pooled_iqr(list(mini_stores.values()))
    assert block["pooled"]["iqr_kz"] == pooled_kz
    assert block["pooled"]["iqr_ros"] == pooled_ros
    assert set(block["tiers"]) == set(TIERS)
    for tier in TIERS:
        kz, ros = index_weights.pooled_iqr([mini_stores[tier]])
        assert block["tiers"][tier]["iqr_kz"] == kz
        assert block["tiers"][tier]["iqr_ros"] == ros
        assert block["tiers"][tier]["kz_share"] == index_weights.kz_share(kz, ros, 1)
    k_raw, k = index_weights.recommended_k(pooled_kz, pooled_ros)
    assert (block["k_raw"], block["k"]) == (k_raw, k)
    assert block["weight_ros"] == 1
    assert block["kz_share"] == index_weights.kz_share(pooled_kz, pooled_ros, 1)


def test_final_index_block_passes_exactly_inside_the_share_band(mini_stores):
    pooled_kz, pooled_ros = index_weights.pooled_iqr(list(mini_stores.values()))
    _, k = index_weights.recommended_k(pooled_kz, pooled_ros)
    inside = index_weights.final_index_block(mini_stores, FinalIndexWeights(Fraction(1), Fraction(k)))
    assert index_weights.KZ_SHARE_MIN <= inside["kz_share"] <= index_weights.KZ_SHARE_MAX
    assert inside["passed"] is True
    too_ros_heavy = index_weights.final_index_block(mini_stores, FinalIndexWeights(Fraction(1), Fraction(10 * k)))
    assert too_ros_heavy["passed"] is False
    too_kz_heavy = index_weights.final_index_block(mini_stores, FinalIndexWeights(Fraction(1), Fraction(0)))
    assert too_kz_heavy["passed"] is False
    wrong_kz_weight = index_weights.final_index_block(mini_stores, FinalIndexWeights(Fraction(2), Fraction(2 * k)))
    assert wrong_kz_weight["passed"] is False


def test_format_final_index_block_is_german_and_names_k(mini_stores):
    block = index_weights.final_index_block(mini_stores, FinalIndexWeights(Fraction(1), Fraction(1)))
    text = index_weights.format_final_index_block(block)
    assert "Empfohlenes k" in text
    assert str(block["k"]) in text
    assert "low" in text and "high" in text


@pytest.mark.slow
@pytest.mark.balance
@candidate.TUNING_TARGET
def test_configured_k_gives_kz_two_thirds(balance_config_path):
    cfg = candidate.load_balance_config(balance_config_path)
    block = index_weights.final_index_block(candidate.static_stores(balance_config_path), cfg.final_index)
    assert block["passed"], index_weights.format_final_index_block(block)
