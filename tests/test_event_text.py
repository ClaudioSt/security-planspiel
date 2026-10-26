"""Event effect rows: every printed row equals the simulation for every input it covers (PRINT-06, T-05-17).

The expectations come only from `rules.evaluate_event` / `rules.budget_review_delta`; the rows come from
`eventtext.effect_rows`. Numbers in a row come from config params, wording from `[sheets.eventkarten]`.
"""
import math
from fractions import Fraction

import pytest

from planspiel import fmt, rules
from planspiel.config import Event, load_config
from planspiel.eventtext import EFFECT_KINDS, EffectRow, EventEffect, effect_rows, event_wave
from planspiel.printmodel import PrintModelError
from planspiel.review_text import _tier_value_text, tier_rows
from planspiel.texts import PreAttackView, load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    return load_config(config_path), load_texts(content_dir / "texte.toml")


def _wave_events(cfg):
    return [event for events in cfg.events.values() for event in events]


def _of_type(cfg, event_type):
    return [event for event in _wave_events(cfg) if event.type == event_type]


def _selection(cfg, **levels):
    selection = {measure_id: 0 for measure_id in cfg.measures}
    selection.update(levels)
    return selection


def _with_levels(cfg, measure_ids, level):
    return _selection(cfg, **{measure_id: level for measure_id in measure_ids})


def test_every_event_type_has_an_effect_kind(loaded):
    cfg, texts = loaded
    for event in [*_wave_events(cfg), *cfg.final_events]:
        effect = effect_rows(event, cfg, texts)
        assert isinstance(effect, EventEffect)
        assert effect.event_id == event.id
        assert effect.kind == EFFECT_KINDS[event.type]
        assert effect.rows, event.id
        assert all(isinstance(row, EffectRow) and row.text for row in effect.rows)


def test_the_kinds_are_the_five_documented_ones():
    assert EFFECT_KINDS == {
        "kurswechsel": "window",
        "opex_discount_per_active_measure": "external_opex",
        "flat_budget": "external_budget",
        "checklist_tier": "kz",
        "measure_level_tier": "kz",
        "level_bonus_per_measure": "kz",
        "and_condition": "kz",
        "final_budget_tier": "review",
    }
    assert set(EFFECT_KINDS.values()) == {"kz", "external_budget", "external_opex", "window", "review"}


def test_an_unknown_event_type_is_a_print_model_error(loaded):
    cfg, texts = loaded
    with pytest.raises(PrintModelError, match="bogus"):
        effect_rows(Event(id="x", name="X", type="bogus", params={}), cfg, texts)


def test_the_wording_pieces_hold_no_digit(loaded):
    _, texts = loaded
    pieces = texts.strings("sheets.eventkarten")
    assert pieces
    for key, text in pieces:
        assert not any(char.isdigit() for char in text), key


def test_event_wave_is_the_config_wave_key(loaded):
    cfg, _ = loaded
    for wave_id, events in cfg.events.items():
        for event in events:
            assert event_wave(cfg, event.id) == wave_id
    assert event_wave(cfg, cfg.final_events[0].id) is None


# --- checklist_tier -----------------------------------------------------------------------------------


def test_checklist_rows_cover_each_count_exactly_once_and_equal_the_simulation(loaded):
    cfg, texts = loaded
    for event in _of_type(cfg, "checklist_tier"):
        measures = event.params["measures"]
        effect = effect_rows(event, cfg, texts)
        covered = [count for row in effect.rows for count in row.covers]
        assert sorted(covered) == list(range(len(measures) + 1))
        for row in effect.rows:
            assert row.covers
            for count in row.covers:
                selection = _with_levels(cfg, measures[:count], event.params["min_level"])
                assert rules.evaluate_event(event, selection)[0] == row.value, (event.id, count)


def test_checklist_merges_adjacent_counts_with_the_same_kz_into_one_row(loaded):
    cfg, texts = loaded
    for event in _of_type(cfg, "checklist_tier"):
        effect = effect_rows(event, cfg, texts)
        values = [row.value for row in effect.rows]
        assert all(left != right for left, right in zip(values, values[1:]))
        for row in effect.rows:
            assert list(row.covers) == list(range(row.covers[0], row.covers[-1] + 1))


def test_the_real_audit_rows_read_as_designed():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    effect = effect_rows(next(event for event in _wave_events(cfg) if event.id == "oem_audit"), cfg, texts)
    assert [row.covers for row in effect.rows] == [(0,), (1,), (2, 3), (4,), (5,)]
    assert [row.value for row in effect.rows] == [-15, -5, 0, 5, 15]
    assert [row.text for row in effect.rows] == [
        "0 erfüllt → KZ −15",
        "1 erfüllt → KZ −5",
        "2–3 erfüllt → KZ ±0",
        "4 erfüllt → KZ +5",
        "5 erfüllt → KZ +15",
    ]


def test_the_checklist_heading_names_the_measures_and_the_minimum_level(loaded):
    cfg, texts = loaded
    for event in _of_type(cfg, "checklist_tier"):
        heading = effect_rows(event, cfg, texts).heading
        assert heading
        for measure_id in event.params["measures"]:
            assert f"{measure_id} – {cfg.measures[measure_id].name}" in heading
        assert f"{event.params['min_level']}" in heading
        assert PreAttackView(cfg, texts).event(event.id)["checklist_heading"] in heading


# --- measure_level_tier -------------------------------------------------------------------------------


def test_level_tier_rows_equal_the_simulation_for_each_level(loaded):
    cfg, texts = loaded
    for event in _of_type(cfg, "measure_level_tier"):
        effect = effect_rows(event, cfg, texts)
        levels = sorted(int(level) for level in event.params["tiers"])
        assert [row.covers for row in effect.rows] == [(level,) for level in levels]
        labels = PreAttackView(cfg, texts).event(event.id)["tier_labels"]
        for row, level in zip(effect.rows, levels):
            selection = _selection(cfg, **{event.params["measure"]: level})
            assert rules.evaluate_event(event, selection)[0] == row.value
            assert labels[str(level)] in row.text
            assert _tier_value_text(row.value) in row.text
        assert event.params["measure"] in effect.heading


def test_level_tier_labels_must_match_the_tier_keys(loaded):
    cfg, texts = loaded
    event = _of_type(cfg, "measure_level_tier")[0]
    broken = Event(
        id=event.id,
        name=event.name,
        type=event.type,
        params={**event.params, "tiers": {**event.params["tiers"], "9": 1}},
    )
    with pytest.raises(PrintModelError, match="tier_labels"):
        effect_rows(broken, cfg, texts)


# --- level_bonus_per_measure --------------------------------------------------------------------------


def test_level_bonus_row_scales_with_the_number_of_measures_at_that_level(loaded):
    cfg, texts = loaded
    for event in _of_type(cfg, "level_bonus_per_measure"):
        (row,) = effect_rows(event, cfg, texts).rows
        level = event.params["level"]
        assert row.text == f"Je Maßnahme auf Level {level}: KZ {_tier_value_text(row.value)}"
        for count in range(len(cfg.measures) + 1):
            selection = _with_levels(cfg, list(cfg.measures)[:count], level)
            assert rules.evaluate_event(event, selection)[0] == count * row.value


# --- and_condition ------------------------------------------------------------------------------------


def _clause_selection(cfg, clauses, satisfied):
    """A selection making every clause true (satisfied=None) or exactly the clause at index `satisfied` false."""
    selection = _selection(cfg)
    for index, clause in enumerate(clauses):
        holds = satisfied is None or index != satisfied
        if "min_level" in clause:
            selection[clause["measure"]] = clause["min_level"] if holds else clause["min_level"] - 1
        else:
            selection[clause["measure"]] = clause["level_eq"] if holds else clause["level_eq"] + 1
    return selection


def test_and_condition_rows_equal_the_simulation_when_true_and_when_false(loaded):
    cfg, texts = loaded
    for event in _of_type(cfg, "and_condition"):
        clauses = event.params["clauses"]
        effect = effect_rows(event, cfg, texts)
        when_true, otherwise = effect.rows
        true_selection = _clause_selection(cfg, clauses, None)
        assert rules.evaluate_event(event, true_selection)[0] == when_true.value == event.params["kz_delta"]
        for index in range(len(clauses)):
            selection = _clause_selection(cfg, clauses, index)
            assert rules.evaluate_event(event, selection)[0] == otherwise.value == 0
        for clause in clauses:
            assert clause["measure"] in when_true.text


def test_the_real_and_condition_names_both_clauses():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    event = next(event for event in _wave_events(cfg) if event.id == "nervige_authentifizierung")
    when_true, otherwise = effect_rows(event, cfg, texts).rows
    assert "M1" in when_true.text and "mindestens auf Level 2" in when_true.text
    assert "M6" in when_true.text and "auf Level 0" in when_true.text
    assert when_true.text.endswith("KZ −10")
    assert otherwise.text.endswith("KZ ±0")


# --- external budget and OPEX -------------------------------------------------------------------------


def test_flat_budget_row_equals_the_simulation(loaded):
    cfg, texts = loaded
    for event in _of_type(cfg, "flat_budget"):
        effect = effect_rows(event, cfg, texts)
        (row,) = effect.rows
        assert effect.kind == "external_budget"
        assert rules.evaluate_event(event, _selection(cfg))[2] == row.value
        assert row.text == f"Gesamtbudget {fmt.format_signed(row.value * 1000)} €"


def test_the_real_flat_budget_row_reads_minus_twenty_thousand_euros():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    event = next(event for event in _wave_events(cfg) if event.id == "sparprogramm")
    assert effect_rows(event, cfg, texts).rows[0].text == "Gesamtbudget −20.000 €"


def test_opex_discount_row_scales_with_the_active_measures(loaded):
    cfg, texts = loaded
    for event in _of_type(cfg, "opex_discount_per_active_measure"):
        effect = effect_rows(event, cfg, texts)
        (row,) = effect.rows
        assert effect.kind == "external_opex"
        for active in range(len(cfg.measures) + 1):
            selection = _with_levels(cfg, list(cfg.measures)[:active], 1)
            assert rules.evaluate_event(event, selection)[1] == active * row.value
        assert row.text == f"OPEX {fmt.format_signed(row.value * 1000)} € je aktiver Maßnahme"


def test_the_real_opex_row_reads_minus_two_thousand_euros_per_measure():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    event = next(event for event in _wave_events(cfg) if event.id == "operative_unterstuetzung")
    assert effect_rows(event, cfg, texts).rows[0].text == "OPEX −2.000 € je aktiver Maßnahme"


# --- kurswechsel --------------------------------------------------------------------------------------


def test_the_kurswechsel_row_names_the_window_after_the_kurswechsel_wave(loaded):
    cfg, texts = loaded
    for event in _of_type(cfg, "kurswechsel"):
        effect = effect_rows(event, cfg, texts)
        wave = rules.kurswechsel_wave(cfg.events)
        assert effect.kind == "window"
        (row,) = effect.rows
        assert row.text == f"Maßnahmentausch im Change-Fenster nach Welle {wave}"
        assert rules.evaluate_event(event, _selection(cfg))[:3] == (0, 0, 0)


def test_a_moved_kurswechsel_changes_the_window_wave(loaded):
    cfg, texts = loaded
    event = _of_type(cfg, "kurswechsel")[0]
    moved = {wave_id: [e for e in events if e.type != "kurswechsel"] for wave_id, events in cfg.events.items()}
    moved[max(moved)].append(event)
    cfg.events = moved
    (row,) = effect_rows(event, cfg, texts).rows
    assert row.text.endswith(f"Welle {max(moved)}")


# --- Budget Review ------------------------------------------------------------------------------------


def test_tier_rows_use_inclusive_ab_boundaries():
    assert tier_rows([[0, 0], [25, 5], [50, 10], [75, 15]]) == [
        (0, 24999, 0), (25000, 49999, 5), (50000, 74999, 10), (75000, None, 15),
    ]
    assert tier_rows([[0, 3]]) == [(0, None, 3)]
    assert tier_rows([[0, 0], [30, 4], [60, 8]]) == [(0, 29999, 0), (30000, 59999, 4), (60000, None, 8)]


def _review(cfg, texts):
    event = cfg.final_events[0]
    return event, effect_rows(event, cfg, texts)


def test_review_rows_equal_budget_review_delta_at_every_boundary(loaded):
    cfg, texts = loaded
    event, effect = _review(cfg, texts)
    kz_per_step, step_k = rules.penalty_params(cfg.final_events)
    tiers = event.params["tiers"]
    expected_rows = tier_rows(tiers)
    tier_effect_rows, overspend = effect.rows[:-1], effect.rows[-1]
    assert effect.kind == "review"
    assert [row.value for row in tier_effect_rows] == [kz for _, _, kz in expected_rows]
    for (from_eur, to_eur, kz), row in zip(expected_rows, tier_effect_rows):
        assert row.value == kz
        assert rules.budget_review_delta(Fraction(from_eur, 1000), tiers, kz_per_step, step_k) == kz
        if to_eur is not None:
            assert rules.budget_review_delta(Fraction(to_eur, 1000), tiers, kz_per_step, step_k) == kz
        if from_eur > 0:
            below = rules.budget_review_delta(Fraction(from_eur - 1, 1000), tiers, kz_per_step, step_k)
            assert below == _previous_value(expected_rows, from_eur)
    assert overspend.value == -kz_per_step
    for remaining_k in (-1, -10, -11, -100):
        started = math.ceil(Fraction(-remaining_k, step_k))
        assert rules.budget_review_delta(Fraction(remaining_k), tiers, kz_per_step, step_k) == overspend.value * started


def _previous_value(rows, from_eur):
    return next(kz for start, end, kz in rows if end == from_eur - 1)


def test_the_review_rows_read_inclusive_boundaries_and_the_overspend_rule():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    effect = effect_rows(cfg.final_events[0], cfg, texts)
    assert [row.text for row in effect.rows] == [
        "0 – 24.999 € → KZ ±0",
        "ab 25.000 € → KZ +5",
        "ab 50.000 € → KZ +10",
        "ab 75.000 € → KZ +15",
        "Überzogen: −9 KZ je angefangene 10.000 €",
    ]


def test_the_overspend_rule_follows_the_config(loaded):
    cfg, texts = loaded
    event = cfg.final_events[0]
    changed = Event(
        id=event.id,
        name=event.name,
        type=event.type,
        params={**event.params, "overspend_penalty": {"kz_per_step": 5, "step": 20}},
    )
    cfg.final_events = [changed]
    overspend = effect_rows(changed, cfg, texts).rows[-1]
    assert overspend.text == "Überzogen: −5 KZ je angefangene 20.000 €"
    assert overspend.value == -5

