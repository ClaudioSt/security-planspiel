"""Team booklet model: planning and RoS / Budget Review pages from config, printed formulas replayed (PRINT-07).

Every number on these two parts comes from config through `rules`, `review_text` and `fmt`. The replay tests fill the
printed RoS and remaining-budget formulas with the numbers of legal paths, using only the operations and signs the
sheet prints, and compare them with `rules.evaluate_path` (T-05-21).
"""
import json
from fractions import Fraction

import pytest

from planspiel import fmt, review_text, risk, rules
from planspiel.booklet import (
    BOOKLET_JOB,
    MAX_PENALTY_ROWS,
    PlanningPage,
    RosPage,
    TeamBooklet,
    build_team_booklet,
)
from planspiel.cards import printed_strings
from planspiel.config import load_config
from planspiel.eventtext import effect_rows
from planspiel.printmodel import PrintModelError
from planspiel.rules import Path, Window
from planspiel.texts import PreAttackView, load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]
MINUS = fmt.MINUS
TIMES = fmt.TIMES
DIVIDED = fmt.DIVIDED


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    cfg = load_config(config_path)
    texts = load_texts(content_dir / "texte.toml")
    return cfg, texts, build_team_booklet(cfg, texts)


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, texts, build_team_booklet(cfg, texts)


def _all_text(value) -> str:
    return "\n".join(printed_strings(value))


def test_the_booklet_is_one_pre_wave_job_with_a_planning_and_a_ros_part(loaded):
    booklet = loaded[2]
    assert BOOKLET_JOB == "spieler-teamheft"
    assert isinstance(booklet, TeamBooklet)
    assert booklet.job == BOOKLET_JOB
    assert isinstance(booklet.planning, PlanningPage)
    assert isinstance(booklet.ros, RosPage)


def test_the_planning_title_is_budget_und_planung(real):
    assert real[2].planning.title == "Budget und Planung"


def test_tier_rows_equal_the_config_in_config_order(loaded):
    cfg, texts, booklet = loaded
    expected = tuple(
        (name.capitalize(), fmt.format_money(tier.budget * 1000), str(tier.kz_start))
        for name, tier in cfg.budget_tiers.items()
    )
    assert booklet.planning.tier_rows == expected
    labels = PreAttackView(cfg, texts).sheet("labels")
    assert booklet.planning.tier_header[:2] == (labels["tier"], labels["available_budget"])


def test_the_real_tier_table_starts_with_the_low_tier_of_the_config(real):
    cfg, _, booklet = real
    low = cfg.budget_tiers["low"]
    assert booklet.planning.tier_rows[0] == ("Low", fmt.format_money(low.budget * 1000), str(low.kz_start))


def test_the_anticipated_sum_line_multiplies_opex_by_the_wave_count_and_has_no_other_digit(loaded):
    cfg, _, booklet = loaded
    line = booklet.planning.anticipated_line
    waves = len(cfg.waves)
    assert f"{TIMES} {waves}" in line
    assert booklet.planning.wave_count_text == f"{TIMES} {waves}"
    digits = "".join(char for char in line if char.isdigit())
    assert digits == str(waves)


def test_the_real_anticipated_sum_multiplies_by_three(real):
    assert "× 3" in real[2].planning.anticipated_line


def test_the_planning_table_has_one_label_row_per_measure_in_config_order(loaded):
    cfg, _, booklet = loaded
    assert booklet.planning.planning_rows == tuple(f"{measure_id} – {measure.name}" for measure_id, measure in cfg.measures.items())


def test_the_cost_table_explains_init_and_opex(loaded):
    cfg, texts, booklet = loaded
    view = PreAttackView(cfg, texts)
    budget, labels = view.sheet("budget"), view.sheet("labels")
    assert booklet.planning.cost_header == (labels["cost_type"], labels["what"], labels["when"])
    assert booklet.planning.cost_rows == (
        (labels["init_costs"], budget["init_what"], budget["init_when"]),
        (labels["opex"], budget["opex_what"], budget["opex_when"]),
    )


def test_own_cost_rows_are_init_window_differences_opex_and_the_sum(loaded):
    cfg, texts, booklet = loaded
    labels = PreAttackView(cfg, texts).sheet("labels")
    own = [row.label for row in booklet.ros.own_cost_rows]
    assert own[0] == labels["total_init"]
    assert own[2] == labels["total_opex"]
    assert len(own) == 4
    assert "Kurswechsel" in own[1] and "Change-Fenster" in own[1]
    for row in booklet.ros.own_cost_rows:
        assert "event" not in f"{row.label} {row.note}".lower(), "no event-penalty row in the own costs (F8, RULE-06)"
    assert "+" in booklet.ros.own_cost_rows[3].note


def test_damage_rows_use_the_veiled_attack_titles(loaded):
    cfg, texts, booklet = loaded
    view = PreAttackView(cfg, texts)
    damage = view.sheet("labels")["damage"]
    assert [row.label for row in booklet.ros.damage_rows] == [f"{damage} {view.attack_title(wave)}" for wave in cfg.waves]
    assert len(booklet.ros.damage_rows) == len(cfg.waves)


def test_the_avoided_damage_line_prints_the_base_losses_from_rules(loaded):
    cfg, _, booklet = loaded
    base = fmt.format_money(rules.base_losses(cfg.waves, cfg.attacks) * 1000)
    note = booklet.ros.avoided_line.note
    assert base in note
    assert booklet.ros.damage_sum.label in note
    assert note.index(base) < note.index(MINUS) < note.index(booklet.ros.damage_sum.label)


def test_the_real_avoided_damage_starts_from_620000_euros(real):
    assert "620.000 €" in real[2].ros.avoided_line.note


def test_the_ros_formula_divides_by_the_own_costs(loaded):
    booklet = loaded[2]
    note = booklet.ros.ros_line.note
    own = booklet.ros.own_cost_rows[3].label
    avoided = booklet.ros.avoided_line.label
    assert note == f"= ({avoided} {MINUS} {own}) {DIVIDED} {own}"


def test_the_budget_review_tiers_equal_review_tier_rows(loaded):
    cfg, texts, booklet = loaded
    final = next(event for event in cfg.final_events if event.type == "final_budget_tier")
    start = str(texts.get("sheets.eventkarten.tier_from"))
    expected = []
    for index, (from_eur, to_eur, kz) in enumerate(review_text.tier_rows(final.params["tiers"])):
        if index == 0 and to_eur is not None:
            span = f"{review_text.format_eur(from_eur)} – {review_text.format_eur(to_eur)} €"
        else:
            span = f"{start} {review_text.format_eur(from_eur)} €"
        value = "±0" if kz == 0 else (f"+{kz}" if kz > 0 else f"−{-kz}")
        expected.append((span, value))
    assert list(booklet.ros.tier_rows) == expected


def test_the_overspend_rule_is_the_card_line(loaded):
    cfg, texts, booklet = loaded
    final = next(event for event in cfg.final_events if event.type == "final_budget_tier")
    assert booklet.ros.overspend_rule == effect_rows(final, cfg, texts).rows[-1].text


def test_the_penalty_table_equals_review_penalty_rows(loaded):
    cfg, _, booklet = loaded
    expected = [
        (f"{review_text.format_eur(low)} – {review_text.format_eur(high)} €", f"−{-kz}")
        for low, high, kz in review_text.penalty_rows(*rules.penalty_params(cfg.final_events))
    ]
    assert list(booklet.ros.penalty_rows) == expected


def test_the_real_overspend_table_has_exactly_the_proven_row_count(real):
    cfg, _, booklet = real
    kz_per_step, step_k = rules.penalty_params(cfg.final_events)
    rows = booklet.ros.penalty_rows
    assert MAX_PENALTY_ROWS == -(-100 // kz_per_step)
    assert len(rows) == MAX_PENALTY_ROWS
    assert rows[0] == (f"1 – {fmt.format_money(step_k * 1000)}", f"{MINUS}{kz_per_step}")
    assert rows[-1][1] == f"{MINUS}{kz_per_step * MAX_PENALTY_ROWS}"


def test_a_smaller_penalty_step_adds_rows_and_stops_the_build(tmp_path):
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    raw["final_events"][0]["overspend_penalty"]["kz_per_step"] = 2
    path = tmp_path / "config.json"
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    cfg = load_config(path)
    assert len(review_text.penalty_rows(*rules.penalty_params(cfg.final_events))) == 50
    texts = load_texts(CONTENT_DIR / "texte.toml")
    with pytest.raises(PrintModelError, match="MAX_PENALTY_ROWS"):
        build_team_booklet(cfg, texts)


def test_the_budget_review_explains_the_remaining_budget_with_signed_event_values(loaded):
    cfg, texts, booklet = loaded
    ros = booklet.ros
    rows = ros.budget_rows
    assert len(rows) == 6
    assert ros.remaining_line.label not in [row.label for row in rows]
    assert "+" in rows[2].note and MINUS not in rows[2].note, "available budget = tier budget + budget event"
    assert rows[3].label == ros.own_cost_rows[3].label, "own costs are carried, not recomputed"
    assert "+" in rows[5].note and MINUS not in rows[5].note, "total costs = own costs + OPEX event"
    assert MINUS in ros.remaining_line.note and "+" not in ros.remaining_line.note
    assert rows[1].note == "" and rows[4].note == "", "event values are entered, not calculated"
    assert ros.sign_hint


def test_no_final_index_on_any_booklet_page(loaded):
    text = _all_text(loaded[2]).lower()
    assert "final-index" not in text and "final index" not in text and "finalindex" not in text
    assert "index" not in text


def test_no_wave_weights_or_attack_names_in_the_booklet(real):
    cfg, texts, booklet = real
    text = _all_text(booklet)
    assert "wC" not in text
    for attack_id in cfg.attacks:
        assert texts.get(f"attacks.{attack_id}.revealed.name") not in text


def test_printed_fragments_are_non_empty_and_unique(loaded):
    booklet = loaded[2]
    for part in (booklet, booklet.planning, booklet.tracking, booklet.ros):
        fragments = part.printed_fragments()
        assert fragments
        assert len(set(fragments)) == len(fragments)
    assert (
        set(booklet.planning.printed_fragments())
        | set(booklet.tracking.printed_fragments())
        | set(booklet.ros.printed_fragments())
    ) == set(booklet.printed_fragments())


# ---- the printed formulas replayed against the simulation ---------------------------------------------------------


REAL_IDS = tuple(f"M{number}" for number in range(1, 11))


def _selection(**levels):
    return {measure_id: levels.get(measure_id, 0) for measure_id in REAL_IDS}


def _init_k(cfg, selection):
    return sum(cfg.measures[measure_id].levels[level].init for measure_id, level in selection.items())


def _opex_k(cfg, selection):
    return sum(cfg.measures[measure_id].levels[level].opex for measure_id, level in selection.items())


def _window_difference_k(cfg, before, after, swap):
    """Init-Differenz of one change window as the sheet states it: net rises, never a refund, Kurswechsel credit."""
    rises = sum(
        max(0, cfg.measures[measure_id].levels[after[measure_id]].init - cfg.measures[measure_id].levels[before[measure_id]].init)
        for measure_id in cfg.measures
    )
    if swap is None:
        return rises
    dropped, incoming = swap
    credit = min(
        cfg.measures[dropped].levels[before[dropped]].init, cfg.measures[incoming].levels[after[incoming]].init
    )
    return rises - credit


def _paths():
    start = _selection(M1=2, M2=1, M3=1, M4=1, M5=1)
    swapped = _selection(M1=2, M2=1, M3=1, M4=1, M8=3)
    downgraded = _selection(M1=1, M2=1, M3=1, M4=2, M8=3)
    swap = ("M5", "M8")
    return [
        pytest.param(Path(start), False, id="static-plan"),
        pytest.param(Path(start, (Window(swapped, swap),)), True, id="kurswechsel-swap"),
        pytest.param(Path(start, (Window(swapped, swap), Window(downgraded))), True, id="swap-and-downgrade-in-window-2"),
    ]


@pytest.fixture(scope="module")
def replay_world():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, texts, build_team_booklet(cfg, texts)


def _event_value_k(cfg, texts, event_type):
    for events in cfg.events.values():
        for event in events:
            if event.type == event_type:
                row = effect_rows(event, cfg, texts).rows[0]
                return event, row
    raise AssertionError(event_type)


@pytest.mark.parametrize(("path", "enforce"), _paths())
def test_the_printed_formulas_reproduce_evaluate_path(replay_world, path, enforce):
    cfg, texts, booklet = replay_world
    record = rules.evaluate_path(cfg, "medium", path, enforce_kurswechsel=enforce)
    selections = record["selections"]

    # Own costs = Gesamt Init-Kosten + Init-Differenzen + Gesamt OPEX Kosten (the sheet's operations: only plus).
    own_note = booklet.ros.own_cost_rows[3].note
    assert own_note.count("+") == 2 and MINUS not in own_note, "the own costs only add three rows"
    init_total = _init_k(cfg, path.start)
    differences = sum(
        _window_difference_k(cfg, selections[index], window.selection, window.swap)
        for index, window in enumerate(path.windows)
    )
    opex_total = sum(_opex_k(cfg, selection) for selection in selections)
    own = init_total + differences + opex_total
    assert own == record["costs"]["security_spend"]
    assert init_total == record["costs"]["init"]
    assert differences == sum(record["costs"]["window_costs"])
    assert differences > 0 or not path.windows, "a replayed change window must carry a cost"
    assert opex_total == sum(record["costs"]["opex_by_wave"])

    # RoS = (Vermiedener Schaden - eigene Kosten) / eigene Kosten, Vermiedener Schaden = base losses - Summe der Schaeden.
    damages = [wave["damage"] for wave in record["waves"]]
    assert len(damages) == len(booklet.ros.damage_rows)
    base = rules.base_losses(cfg.waves, cfg.attacks)
    avoided = Fraction(base) - sum(Fraction(damage) for damage in damages)
    assert (avoided - own) / own == record["ros"]

    # Restbudget = (Tier-Budget + Budgetaenderung) - (eigene Kosten + OPEX-Aenderung), event values as the cards print.
    budget_event, budget_row = _event_value_k(cfg, texts, "flat_budget")
    opex_event, opex_row = _event_value_k(cfg, texts, "opex_discount_per_active_measure")
    assert fmt.format_signed(budget_row.value * 1000) in budget_row.text
    assert fmt.format_signed(opex_row.value * 1000) in opex_row.text
    event_wave = next(wave_id for wave_id, events in cfg.events.items() if opex_event in events)
    wave_index = [wave.wave_id for wave in cfg.waves].index(event_wave)
    active = sum(1 for level in selections[wave_index].values() if level >= 1)
    event_budget = budget_row.value
    event_opex = opex_row.value * active
    available = cfg.budget_tiers["medium"].budget + event_budget
    costs = own + event_opex
    assert available - costs == record["costs"]["remaining"]
    assert event_budget < 0 < -event_opex, "the cut lowers the remaining budget, the OPEX relief raises it"
    assert (available - costs) == (cfg.budget_tiers["medium"].budget - own) + event_budget - event_opex


# ---- the risk register helpers (RISK-02, D-03, D-04) ---------------------------------------------------------------


def test_risk_zone_of_gives_three_cells_per_zone():
    zones = {(likelihood, impact): risk.zone_of(likelihood, impact) for likelihood in (1, 2, 3) for impact in (1, 2, 3)}
    assert sorted(zones.values()).count("green") == 3
    assert sorted(zones.values()).count("yellow") == 3
    assert sorted(zones.values()).count("red") == 3
    assert zones[(1, 1)] == "green"
    assert zones[(1, 3)] == "yellow"
    assert zones[(3, 1)] == "yellow"
    assert zones[(2, 2)] == "yellow"
    assert zones[(2, 3)] == "red"
    assert zones[(3, 3)] == "red"


def test_risk_band_ranges_compose_the_axis_labels():
    cfg = load_config(CONFIG_PATH)
    words = {"range_below": "unter", "range_to": "bis unter", "range_from": "ab"}
    bands = cfg.risk_matrix.bands
    assert risk.band_ranges(bands, words) == ("unter 50.000 €", "50.000 € bis unter 150.000 €", "ab 150.000 €")
    assert risk.band_ranges(bands, words) == (
        f"unter {fmt.format_money(bands[1].minimum * 1000)}",
        f"{fmt.format_money(bands[1].minimum * 1000)} bis unter {fmt.format_money(bands[2].minimum * 1000)}",
        f"ab {fmt.format_money(bands[2].minimum * 1000)}",
    )
