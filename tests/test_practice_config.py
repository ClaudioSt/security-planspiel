"""The practice block of Welle 0: config shape, validator, view and example guards (FLOW-01, D-12, D-13, D-15).

The block is read only by `planspiel/practice.py`. These tests pin the example, check that every guard fires on its
own mutation, and prove that the real machinery (waves, attacks, events, enumeration inputs) cannot see the block.
"""
import copy
import dataclasses
import json
from fractions import Fraction

import pytest

from planspiel import fmt, practice, rules
from planspiel.config import Practice, load_config
from planspiel.printmodel import PrintModelError, min_half_distance
from planspiel.validate import scale_factors, validate
from tests.support import CONFIG_PATH

PINNED_SELECTION = {"M1": 0, "M2": 0, "M3": 0, "M4": 1, "M5": 0, "M6": 0, "M7": 0, "M8": 2, "M9": 2, "M10": 1}


def _raw():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _errors(issues):
    return [issue for issue in issues if issue.level == "error"]


def _load(raw, tmp_path, name="config.json"):
    target = tmp_path / name
    target.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    return load_config(target)


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


def _with_practice(cfg, **changes):
    return dataclasses.replace(cfg, practice=dataclasses.replace(cfg.practice, **changes))


def _with_wave(cfg, **changes):
    return _with_practice(cfg, wave=dataclasses.replace(cfg.practice.wave, **changes))


def _with_attack(cfg, **changes):
    return _with_practice(cfg, attack=dataclasses.replace(cfg.practice.attack, **changes))


# --- config shape --------------------------------------------------------------------------------------------


def test_the_real_config_carries_the_pinned_practice_block(cfg):
    practice_block = cfg.practice
    assert isinstance(practice_block, Practice)
    assert practice_block.kz_start == 98
    assert practice_block.budget == 200
    assert practice_block.selection == PINNED_SELECTION

    attack = practice_block.attack
    assert attack.attack_id == "practice"
    assert (attack.base_severity, attack.mitigation_cap, attack.s_unit) == (6, 6, 20)
    assert (attack.kz_at_full_damage, attack.kz_at_full_mitigation) == (-6, 9)
    assert attack.allow_recovery is True

    wave = practice_block.wave
    assert wave.wave_id == 0
    assert wave.attack_id == "practice"
    assert wave.e_threshold == 18
    assert wave.weights == {"c": Fraction(3, 10), "i": Fraction(3, 10), "a": Fraction(2, 5)}
    assert [(bm.measure, bm.min_level, bm.bonus) for bm in wave.bonus_measures] == [("M9", 2, 4), ("M10", 2, 3)]

    event = practice_block.event
    assert event.type == "measure_level_tier"
    assert event.params["measure"] == "M2"
    assert "uebung" in event.id
    assert not any(character.isdigit() for character in event.name)


def test_a_config_without_the_block_has_no_practice(cfg, tmp_path):
    raw = _raw()
    del raw["practice"]
    assert _load(raw, tmp_path).practice is None


def test_pinned_weights_and_bonus_measures_differ_from_every_real_wave(cfg):
    weights = tuple(cfg.practice.wave.weights[key] for key in "cia")
    for wave in cfg.waves:
        real = tuple(wave.weights[key] for key in "cia")
        assert weights != real
        assert sorted(weights) != sorted(real)
    used = {bm.measure for wave in cfg.waves for bm in wave.bonus_measures}
    assert used.isdisjoint(bm.measure for bm in cfg.practice.wave.bonus_measures)
    assert all(cfg.ws % weight.denominator == 0 for weight in weights)
    constants = rules.worksheet_constants(practice.practice_config(cfg), cfg.practice.wave)
    assert fmt.terminates(constants.slope)


# --- invisible to the real machinery (D-12, T-05-38) -----------------------------------------------------------


def test_the_block_never_reaches_the_real_config_fields(cfg, tmp_path):
    raw = _raw()
    del raw["practice"]
    plain = _load(raw, tmp_path)

    for name in (
        "default_budget_tier", "budget_tiers", "attacks", "waves", "measures", "events", "base_cia",
        "final_events", "ws", "rs",
    ):
        assert getattr(cfg, name) == getattr(plain, name), name
    assert dataclasses.replace(cfg, practice=None) == plain
    assert "practice" not in cfg.attacks
    assert rules.base_losses(cfg.waves, cfg.attacks) == rules.base_losses(plain.waves, plain.attacks) == 620
    assert scale_factors(_raw()) == scale_factors(raw)
    assert [wave.wave_id for wave in cfg.waves] == [1, 2, 3]


def test_evaluation_and_kernel_ignore_the_block(cfg, tmp_path):
    raw = _raw()
    del raw["practice"]
    plain = _load(raw, tmp_path)
    selection = {"M1": 2, "M2": 2, "M3": 1, "M4": 1, "M5": 0, "M6": 1, "M7": 0, "M8": 0, "M9": 0, "M10": 0}

    assert rules.evaluate_plan(cfg, "medium", selection) == rules.evaluate_plan(plain, "medium", selection)
    assert rules.TierKernel(cfg, "medium").evaluate(selection) == rules.TierKernel(plain, "medium").evaluate(selection)


# --- the view ------------------------------------------------------------------------------------------------


def test_the_view_holds_only_the_practice_wave(cfg):
    view = practice.practice_config(cfg)
    assert [wave.wave_id for wave in view.waves] == [0]
    assert view.waves == [cfg.practice.wave]
    assert view.attacks["practice"] is cfg.practice.attack
    assert view.events == {0: [cfg.practice.event]}
    assert view.final_events == []
    assert list(view.budget_tiers) == [practice.PRACTICE_TIER] == ["practice"]
    tier = view.budget_tiers["practice"]
    assert (tier.budget, tier.kz_start, tier.severity_multiplier) == (200, 98, Fraction(1))
    assert practice.PRACTICE_JOB == "uebung-welle-0"
    assert cfg.waves != view.waves  # the real config is not touched by building the view


def test_the_view_runs_through_the_rules(cfg):
    view = practice.practice_config(cfg)
    constants = rules.worksheet_constants(view, view.waves[0])
    assert (constants.lower, constants.upper) == (18, 24)
    trace = rules.path_trace(view, practice.PRACTICE_TIER, rules.Path(start=dict(cfg.practice.selection)))
    assert len(trace.waves) == 1 and trace.windows == ()


def test_the_view_needs_the_block(cfg):
    with pytest.raises(PrintModelError, match="Übung"):
        practice.practice_config(dataclasses.replace(cfg, practice=None))


def test_the_example_selection_trace(cfg):
    trace = practice.check_example(cfg)
    wave = trace.waves[0]
    assert wave.cia == {"c": 16, "i": 22, "a": 19}
    assert wave.e_value == 19
    assert (wave.bonus_met, wave.bonus_missed) == (("M9",), ("M10",))
    assert wave.gesamtreduktion == 23
    assert wave.case == 3
    assert (wave.damage_before_eur, wave.recovery_factor, wave.damage_eur) == (20000, Fraction(1, 10), 18000)
    assert wave.kz_attack == Fraction(13, 2)
    assert wave.kz_event == -4
    assert wave.kz_change_exact == Fraction(5, 2)
    assert wave.kz_change == 3
    assert (wave.kz_before, wave.kz_unclamped, wave.kz_after) == (98, 101, 100)
    assert (trace.init_k, wave.own_opex_k) == (104, 23)
    assert wave.remaining_k == 73


def test_half_away_from_zero_and_half_to_even_differ_on_the_example(cfg):
    wave = practice.check_example(cfg).waves[0]
    assert wave.kz_change == 3
    assert round(float(wave.kz_change_exact)) == 2  # builtin rounding goes to the even neighbour


# --- every guard fires on its own mutation -----------------------------------------------------------------


GUARDS = [
    pytest.param(lambda cfg: _with_wave(cfg, e_threshold=10), "Fall 3", id="fall-2"),
    pytest.param(lambda cfg: _with_wave(cfg, e_threshold=26), "Fall 3", id="fall-1"),
    pytest.param(
        lambda cfg: _with_wave(
            cfg, bonus_measures=[dataclasses.replace(cfg.practice.wave.bonus_measures[0], min_level=3),
                                 cfg.practice.wave.bonus_measures[1]]
        ),
        "genau eine",
        id="no-bonus-met",
    ),
    pytest.param(
        lambda cfg: _with_wave(
            cfg, bonus_measures=[cfg.practice.wave.bonus_measures[0],
                                 dataclasses.replace(cfg.practice.wave.bonus_measures[1], min_level=1, bonus=0)]
        ),
        "genau eine",
        id="both-bonus-met",
    ),
    pytest.param(lambda cfg: _with_attack(cfg, allow_recovery=False), "Recovery", id="no-recovery"),
    pytest.param(
        lambda cfg: _with_wave(
            cfg, bonus_measures=[dataclasses.replace(cfg.practice.wave.bonus_measures[0], bonus=3),
                                 cfg.practice.wave.bonus_measures[1]]
        ),
        "ganzzahlig",
        id="integer-wave-change",
    ),
    pytest.param(
        lambda cfg: _with_wave(cfg, weights={"c": Fraction(2, 5), "i": Fraction(3, 10), "a": Fraction(3, 10)}),
        "halben Punkt",
        id="no-exact-half",
    ),
    pytest.param(lambda cfg: _with_practice(cfg, kz_start=90), "Begrenzung", id="no-clamp-high"),
    pytest.param(lambda cfg: _with_practice(cfg, budget=100), "Budget", id="over-budget"),
    pytest.param(lambda cfg: _with_attack(cfg, base_severity=7), "D-06", id="d06-severity-cap"),
    pytest.param(
        lambda cfg: _with_attack(cfg, kz_at_full_mitigation=Fraction(9001, 1000)), "D-09", id="d09-half-distance"
    ),
]


@pytest.mark.parametrize(("mutate", "fragment"), GUARDS)
def test_check_example_raises_when_a_required_property_breaks(cfg, mutate, fragment):
    with pytest.raises(PrintModelError, match=fragment):
        practice.check_example(mutate(cfg))


def test_the_d09_mutation_really_breaks_the_half_distance(cfg):
    view = practice.practice_config(_with_attack(cfg, kz_at_full_mitigation=Fraction(9001, 1000)))
    constants = rules.worksheet_constants(view, view.waves[0])
    assert min_half_distance(view, constants) < Fraction(1, 100)


def test_a_clamp_at_the_low_end_also_counts(cfg):
    # the guard accepts either bound of the scale
    low = _with_practice(cfg, kz_start=-5)
    assert practice.check_example(low).waves[0].kz_unclamped == -2


def test_check_example_rejects_a_selection_that_breaks_a_dependency(cfg):
    selection = dict(cfg.practice.selection, M1=3)
    with pytest.raises(PrintModelError, match="Übung"):
        practice.check_example(_with_practice(cfg, selection=selection))


# --- validator -----------------------------------------------------------------------------------------------


def test_the_real_config_has_no_error_with_the_block():
    assert _errors(validate(_raw())) == []


def _set(path, value):
    def mutate(raw):
        target = raw
        for part in path[:-1]:
            target = target[part]
        target[path[-1]] = value

    return mutate


def _delete(path):
    def mutate(raw):
        target = raw
        for part in path[:-1]:
            target = target[part]
        del target[path[-1]]

    return mutate


def _selection_without_m10(raw):
    del raw["practice"]["selection"]["M10"]


def _practice_attack_in_attacks(raw):
    raw["attacks"]["practice"] = copy.deepcopy(raw["practice"]["attack"])


VALIDATOR_CASES = [
    pytest.param(
        _set(["practice", "wave", "weights"], {"c": 0.4, "i": 0.4, "a": 0.2}),
        "practice.weights_equal_wave", "practice.wave.weights", id="weights-equal-wave-1",
    ),
    pytest.param(
        _set(["practice", "wave", "weights"], {"c": 0.2, "i": 0.5, "a": 0.3}),
        "practice.weights_permutation", "practice.wave.weights", id="weights-same-multiset-as-wave-3",
    ),
    pytest.param(
        _set(["practice", "wave", "weights"], {"c": 0.4, "i": 0.2, "a": 0.4}),
        "practice.weights_permutation", "practice.wave.weights", id="weights-same-multiset-as-wave-1",
    ),
    pytest.param(
        _set(["practice", "wave", "bonus_measures", 0, "measure"], "M3"),
        "practice.bonus_measure_shared", "practice.wave.bonus_measures[0].measure", id="bonus-measure-of-a-real-wave",
    ),
    pytest.param(
        _set(["practice", "wave", "weights"], {"c": 0.15, "i": 0.35, "a": 0.5}),
        "practice.weight_scale", "practice.wave.weights", id="weight-denominator-does-not-divide-ws",
    ),
    pytest.param(_selection_without_m10, "practice.selection_measures", "practice.selection", id="selection-misses-a-measure"),
    pytest.param(
        _set(["practice", "selection", "M9"], 4),
        "practice.selection_level", "practice.selection.M9", id="selection-level-not-in-config",
    ),
    pytest.param(
        _set(["practice", "attack", "base_severity"], 7),
        "practice.severity_cap", "practice.attack", id="severity-differs-from-cap",
    ),
    pytest.param(
        _set(["practice", "event"], {"id": "uebung_ereignis", "name": "Übung", "type": "flat_budget", "budget_delta": -5}),
        "practice.event_type", "practice.event.type", id="event-without-a-kz-effect",
    ),
    pytest.param(
        _set(["practice", "event", "measure"], "M42"),
        "ref.unknown_measure", "practice.event.measure", id="event-names-an-unknown-measure",
    ),
    pytest.param(
        _set(["practice", "event", "id"], "sparprogramm"),
        "schema.duplicate_id", "practice.event.id", id="event-id-of-a-real-event",
    ),
    pytest.param(
        _set(["practice", "wave", "bonus_measures", 0, "measure"], "M99"),
        "ref.unknown_measure", "practice.wave.bonus_measures[0].measure", id="unknown-bonus-measure",
    ),
    pytest.param(_delete(["practice", "selection"]), "schema.keys", "practice.selection", id="selection-missing"),
    pytest.param(_delete(["practice", "wave", "e_threshold"]), "schema.keys", "practice.wave.e_threshold", id="threshold-missing"),
    pytest.param(_practice_attack_in_attacks, "practice.attack_id_taken", "attacks.practice", id="practice-attack-among-real-attacks"),
    pytest.param(_set(["practice", "description"], "Text"), "schema.keys", "practice.description", id="prose-key-in-the-block"),
    pytest.param(_set(["practice", "kz_start"], "98"), "schema.type", "practice.kz_start", id="kz-start-not-a-number"),
]


@pytest.mark.parametrize(("mutate", "code", "path"), VALIDATOR_CASES)
def test_validator_rejects_a_broken_practice_block(mutate, code, path):
    raw = _raw()
    mutate(raw)
    issues = [issue for issue in _errors(validate(raw)) if issue.code == code and issue.path == path]
    assert issues, [(i.code, i.path) for i in _errors(validate(raw))]


def test_a_config_without_the_block_validates_as_before():
    raw = _raw()
    del raw["practice"]
    assert _errors(validate(raw)) == []
    assert [issue.code for issue in validate(raw) if issue.level == "warning"] == ["hand_calc.kz_slope"]


def test_the_block_adds_no_warning_beyond_the_known_slope_warning():
    assert [issue.code for issue in validate(_raw()) if issue.level == "warning"] == ["hand_calc.kz_slope"]
