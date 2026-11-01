from fractions import Fraction

from planspiel.config import Config, load_config
from planspiel.rules import base_losses, evaluate_plan, final_index, over_budget, penalty_params, ros, ros_two_decimals
from tests.support import CONFIG_PATH


def _selection(cfg, level):
    return {m: level for m in cfg.measure_ids}


def test_ros_is_none_when_cost_is_zero():
    assert ros(620, 0, 0) is None


def test_ros_formula():
    assert ros(620, 96.0, 250) == ((620 - 96.0) - 250) / 250


def test_ros_is_exact_for_exact_inputs():
    assert ros(620, Fraction(96), 250) == Fraction(137, 125)
    assert ros(620, 96, 250) == Fraction(137, 125)


def test_final_index_falls_back_to_kz_without_ros():
    assert final_index(80, None, Fraction(1), Fraction(20)) == 80


def test_final_index_without_ros_honours_the_kz_weight():
    assert final_index(80, None, Fraction(2), Fraction(1)) == 160
    assert final_index(80, None, Fraction(1), Fraction(1)) == 80


def test_ros_two_decimals_rounds_half_away_from_zero():
    assert ros_two_decimals(Fraction(1234, 10000)) == Fraction(12, 100)
    assert ros_two_decimals(Fraction(-125, 1000)) == Fraction(-13, 100)
    assert ros_two_decimals(Fraction(5, 1000)) == Fraction(1, 100)
    assert ros_two_decimals(Fraction(-5, 1000)) == Fraction(-1, 100)
    assert ros_two_decimals(Fraction(4, 1000)) == 0


def test_final_index_is_kz_plus_k_times_the_two_decimal_ros():
    assert final_index(80, Fraction(1234, 10000), Fraction(1), Fraction(20)) == Fraction(824, 10)
    assert final_index(80, None, 1, 20) == 80
    assert final_index(80, Fraction(1, 2), 1, 1) == Fraction(161, 2)
    assert final_index(80, Fraction(1, 2), Fraction(2), Fraction(1, 2)) == Fraction(641, 4)


def test_over_budget_boundary():
    assert over_budget(381, 380) is True
    assert over_budget(380, 380) is False


def test_base_losses_from_config():
    cfg = load_config(CONFIG_PATH)
    assert base_losses(cfg.waves, cfg.attacks) == 620


def test_load_config_returns_config_object():
    cfg = load_config(CONFIG_PATH)
    assert isinstance(cfg, Config)
    assert cfg.default_budget_tier == "medium"
    assert cfg.waves[1].attack_id == "ot"


def test_evaluate_plan_empty_selection_medium():
    cfg = load_config(CONFIG_PATH)
    rec = evaluate_plan(cfg, "medium", _selection(cfg, 0))
    assert rec["kz_final"] == 38
    assert [w["kz_after"] for w in rec["waves"]] == [28, 17, 11]
    assert rec["total_damage"] == 620
    assert rec["costs"]["total"] == 0
    assert rec["costs"]["budget_available"] == 370
    assert rec["final_events"][0]["kz_delta"] == 27
    assert rec["ros"] is None
    assert rec["over_budget"] is False


def test_evaluate_plan_all_l3_low_is_over_budget_with_final_event_penalty():
    cfg = load_config(CONFIG_PATH)
    x, _ = penalty_params(cfg.final_events)
    rec = evaluate_plan(cfg, "low", _selection(cfg, 3))
    assert rec["over_budget"] is True
    assert rec["final_events"][0]["kz_delta"] == -x * 88
    assert rec["kz_final"] == 0
