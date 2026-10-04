"""Kurswechsel as a forced Maßnahmentausch: leaf functions, validator rules, config text (RULE-01).

D-09..D-13, D-22, D-23, D-28. The path evaluator and the swap layer are built on these functions in plan 02-06.
"""
import copy
import json
from itertools import product

import pytest

from planspiel import rules
from planspiel.config import Event, load_config
from planspiel.validate import validate
from tests.support import CONFIG_PATH, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"

REAL_IDS = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10"]

KURSWECHSEL_EFFECT = (
    "Kurswechsel: Pflicht-Maßnahmentausch im folgenden Change-Fenster "
    "(im Referenzplan ohne Change-Fenster-Züge nicht angewendet)"
)


@pytest.fixture(scope="module")
def real():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def mini():
    return load_config(MINI)


def plan(ids, **levels):
    return {measure_id: levels.get(measure_id, 0) for measure_id in ids}


def real_plan(**levels):
    return plan(REAL_IDS, **levels)


def test_swap_possible_needs_an_active_and_an_inactive_measure():
    assert rules.swap_possible({measure_id: 1 for measure_id in REAL_IDS}) is False
    assert rules.swap_possible({measure_id: 3 for measure_id in REAL_IDS}) is False
    assert rules.swap_possible(real_plan()) is False
    assert rules.swap_possible(real_plan(M1=1)) is True
    assert rules.swap_possible(real_plan(**{m: 2 for m in REAL_IDS[:9]})) is True


def test_swap_exempt_plans_of_the_real_config_number_48115(real):
    exempt = 0
    for levels in product((1, 2, 3), repeat=len(REAL_IDS)):
        selection = dict(zip(REAL_IDS, levels))
        if rules.dependencies_satisfied(selection, real.measures):
            exempt += 1
            assert rules.swap_possible(selection) is False
    empty = real_plan()
    assert rules.dependencies_satisfied(empty, real.measures)
    assert rules.swap_possible(empty) is False
    assert exempt + 1 == 48_115


@pytest.mark.parametrize(
    ("wave1", "end", "dropped", "incoming", "expected"),
    [
        pytest.param({"M1": 2, "M2": 0}, {"M1": 0, "M2": 2}, "M1", "M2", True, id="legal"),
        pytest.param({"M1": 2, "M2": 0}, {"M1": 0, "M2": 1}, "M1", "M2", True, id="legal-any-level"),
        pytest.param({"M1": 2, "M2": 1}, {"M1": 0, "M2": 2}, "M1", "M2", False, id="incoming-was-active-in-wave-1"),
        pytest.param({"M1": 2, "M2": 0}, {"M1": 1, "M2": 2}, "M1", "M2", False, id="dropped-not-zero-at-window-end"),
        pytest.param({"M1": 2, "M2": 0}, {"M1": 0, "M2": 0}, "M1", "M2", False, id="incoming-zero-at-window-end"),
        pytest.param({"M1": 0, "M2": 0}, {"M1": 0, "M2": 2}, "M1", "M2", False, id="dropped-inactive-in-wave-1"),
        pytest.param({"M1": 2, "M2": 0}, {"M1": 2, "M2": 0}, "M1", "M1", False, id="dropped-is-incoming"),
    ],
)
def test_swap_legal(wave1, end, dropped, incoming, expected):
    assert rules.swap_legal(wave1, end, dropped, incoming) is expected


@pytest.mark.parametrize(
    ("wave1", "end", "dropped", "incoming", "credit"),
    [
        pytest.param({"M6": 1}, {"M2": 2}, "M6", "M2", 10, id="dearer-incoming-credit-is-dropped-init"),
        pytest.param({"M5": 3}, {"M8": 2}, "M5", "M8", 36, id="cheaper-incoming-credit-capped-no-refund"),
        pytest.param({"M3": 1}, {"M6": 2}, "M3", "M6", 24, id="equal-init"),
        pytest.param({"M10": 3}, {"M1": 1}, "M10", "M1", 30, id="cheaper-incoming-again"),
        pytest.param({"M6": 1}, {"M6": 3, "M2": 2}, "M6", "M2", 10, id="credit-uses-wave-1-level"),
    ],
)
def test_swap_credit_is_capped_at_both_inits(real, wave1, end, dropped, incoming, credit):
    assert rules.swap_credit(real.measures, wave1, dropped, incoming, end) == credit


def test_team_pays_max_zero_of_the_difference(real):
    wave1, end = {"M6": 1}, {"M2": 2}
    paid = rules.compute_costs(end, real.measures, 0)[0] - rules.swap_credit(real.measures, wave1, "M6", "M2", end)
    assert paid == 40
    wave1, end = {"M5": 3}, {"M8": 2}
    paid = rules.compute_costs(end, real.measures, 0)[0] - rules.swap_credit(real.measures, wave1, "M5", "M8", end)
    assert paid == 0


@pytest.mark.parametrize(
    ("selection", "dropped", "expected"),
    [
        pytest.param(
            {"M1": 3, "M2": 2, "M3": 3, "M7": 3},
            "M2",
            {"M1": 2, "M2": 0, "M3": 2, "M7": 2},
            id="drop-m2-lowers-three-dependents",
        ),
        pytest.param({"M2": 1, "M7": 3}, "M2", {"M2": 0, "M7": 2}, id="m7-needs-only-m2-level-1"),
        pytest.param({"M1": 2, "M2": 2}, "M2", {"M1": 2, "M2": 0}, id="m1-level-2-has-no-dependency"),
        pytest.param({"M5": 3, "M2": 2, "M1": 3}, "M5", {"M5": 0, "M2": 2, "M1": 3}, id="drop-without-dependents"),
    ],
)
def test_swap_repair_vectors(real, selection, dropped, expected):
    full = real_plan(**selection)
    repaired = rules.swap_repair(full, dropped, real.measures)
    assert repaired == real_plan(**expected)
    assert full == real_plan(**selection), "the input selection must not be modified"


def _valid_plans(cfg):
    ids = cfg.measure_ids
    for levels in product((0, 1, 2, 3), repeat=len(ids)):
        selection = dict(zip(ids, levels))
        if rules.dependencies_satisfied(selection, cfg.measures):
            yield selection


def test_swap_repair_is_valid_downward_and_minimal_on_every_mini_plan(mini):
    checked = 0
    for selection in _valid_plans(mini):
        for dropped, level in selection.items():
            if level == 0:
                continue
            repaired = rules.swap_repair(selection, dropped, mini.measures)
            checked += 1
            assert repaired[dropped] == 0
            assert rules.dependencies_satisfied(repaired, mini.measures)
            assert all(repaired[m] <= selection[m] for m in selection)
            for measure_id, lowered in repaired.items():
                if measure_id == dropped or lowered == selection[measure_id]:
                    continue
                raised = dict(repaired, **{measure_id: lowered + 1})
                assert not rules.dependencies_satisfied(raised, mini.measures), (selection, dropped, measure_id)
    assert checked > 0


def test_every_non_exempt_mini_plan_has_a_legal_swap(mini):
    ids = mini.measure_ids
    for selection in _valid_plans(mini):
        if not rules.swap_possible(selection):
            continue
        found = False
        for dropped, incoming, level in product(ids, ids, (1, 2, 3)):
            if selection[dropped] == 0 or selection[incoming] != 0:
                continue
            end = rules.swap_repair(selection, dropped, mini.measures)
            end[incoming] = level
            if rules.dependencies_satisfied(end, mini.measures) and rules.swap_legal(selection, end, dropped, incoming):
                found = True
                break
        assert found, selection


@pytest.mark.parametrize("cfg_name", ["real", "mini"])
def test_kurswechsel_wave_is_wave_1(cfg_name, request):
    cfg = request.getfixturevalue(cfg_name)
    assert rules.kurswechsel_wave(cfg.events) == 1


def test_kurswechsel_wave_is_none_without_the_event():
    other = Event("x", "X", "text", "flat_budget", {"budget_delta": 1})
    assert rules.kurswechsel_wave({1: [other], 2: []}) is None
    assert rules.kurswechsel_wave({}) is None


def test_evaluate_event_does_not_apply_the_kurswechsel_in_a_static_plan(real):
    event = real.events[1][0]
    assert event.type == "kurswechsel"
    for selection in (real_plan(), real_plan(M1=2, M2=3), {m: 3 for m in REAL_IDS}):
        assert rules.evaluate_event(event, selection) == (0, 0, 0, KURSWECHSEL_EFFECT)


def _raw(path=CONFIG_PATH):
    return json.loads(path.read_text(encoding="utf-8"))


def _issues(raw, level="error"):
    return [issue for issue in validate(raw) if issue.level == level]


def _kurswechsel_event(raw):
    return copy.deepcopy(raw["events"]["wave_1"][0])


@pytest.mark.parametrize("path", [CONFIG_PATH, MINI], ids=["real", "mini"])
def test_both_configs_validate_with_the_one_known_warning(path):
    raw = _raw(path)
    assert _issues(raw) == []
    assert [(i.code, i.path) for i in _issues(raw, "warning")] == [("hand_calc.kz_slope", "attacks.exfil")]
    assert raw["events"]["wave_1"][0]["type"] == "kurswechsel"


def _noop(raw):
    raw["events"]["wave_1"][0]["type"] = "noop"


def _in_last_wave(raw):
    raw["events"]["wave_3"].append(_kurswechsel_event(raw))
    raw["events"]["wave_3"][-1]["id"] = "kurswechsel_spaet"


def _second_in_wave_2(raw):
    extra = _kurswechsel_event(raw)
    extra["id"] = "kurswechsel_zwei"
    raw["events"]["wave_2"].append(extra)


def _in_final_events(raw):
    extra = _kurswechsel_event(raw)
    extra["id"] = "kurswechsel_final"
    raw["final_events"].append(extra)


def _moved_to_last_wave(raw):
    raw["events"]["wave_3"].append(raw["events"]["wave_1"].pop(0))


@pytest.mark.parametrize(
    ("mutate", "code"),
    [
        pytest.param(_noop, "schema.unknown_event_type", id="noop-is-retired"),
        pytest.param(_moved_to_last_wave, "schema.event_placement", id="kurswechsel-in-last-wave"),
        pytest.param(_in_last_wave, "schema.event_placement", id="second-kurswechsel-in-last-wave"),
        pytest.param(_second_in_wave_2, "schema.kurswechsel_count", id="two-kurswechsel"),
        pytest.param(_in_final_events, "schema.event_placement", id="kurswechsel-in-final-events"),
    ],
)
@pytest.mark.parametrize("path", [CONFIG_PATH, MINI], ids=["real", "mini"])
def test_validator_rejects_misplaced_or_duplicated_kurswechsel(path, mutate, code):
    raw = copy.deepcopy(_raw(path))
    mutate(raw)
    assert code in {issue.code for issue in _issues(raw)}, [(i.code, i.path) for i in _issues(raw)]


def test_second_kurswechsel_is_reported_at_its_own_path():
    raw = copy.deepcopy(_raw())
    _second_in_wave_2(raw)
    paths = [issue.path for issue in _issues(raw) if issue.code == "schema.kurswechsel_count"]
    assert paths == [f"events.wave_2[{len(raw['events']['wave_2']) - 1}]"]


@pytest.mark.parametrize("path", [CONFIG_PATH, MINI], ids=["real", "mini"])
def test_kurswechsel_description_uses_the_one_vocabulary(path):
    description = _raw(path)["events"]["wave_1"][0]["description"]
    assert "Maßnahmentausch" in description
    assert "Levelwechsel" in description
    assert "Maßnahmenwechsel" not in description
    assert not any(char.isdigit() for char in description)


def test_readme_uses_the_one_vocabulary():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Levelwechsel" in readme
    assert "Maßnahmentausch" in readme
    assert "Begriffe: Levelwechsel und Maßnahmentausch" in readme
    assert "Kurswechsel (Maßnahmentausch)" in readme
    assert readme.count("Maßnahmenwechsel") == 1


@pytest.mark.parametrize("path", [CONFIG_PATH, MINI], ids=["real", "mini"])
def test_no_display_string_uses_the_retired_term(path):
    cfg = load_config(path)
    strings = [measure.name for measure in cfg.measures.values()]
    for wave_events in (*cfg.events.values(), cfg.final_events):
        for event in wave_events:
            strings += [event.name, event.description]
    for wave in cfg.waves:
        strings += [wave.name] + [bonus.description for bonus in wave.bonus_measures]
    assert [text for text in strings if "Maßnahmenwechsel" in text] == []
