"""Tracking sheet model: columns, rows in calculation order, shaded cells, change-window grid (PRINT-08, D-09, D-10).

The replay tests fill the printed rows of the sheet in printed order with the numbers a team would have (card costs,
the worksheet's rounded wave change, the damage, the event cards' effects) and compare the outcome with
`rules.evaluate_path` on three legal paths (T-05-25). The replay module is a second encoding of the printed procedure
and must not import the path evaluator itself.
"""
import ast
import re
from pathlib import Path as FilePath

import pytest

from planspiel import booklet, fmt, rules, texts as texts_module
from planspiel.booklet import (
    MAX_WINDOWS,
    TRACKING_ROW_ORDER,
    TeamBooklet,
    TrackingPage,
    TrackingRow,
    WindowBlock,
    build_team_booklet,
    build_tracking_page,
)
from planspiel.cards import printed_strings
from planspiel.config import load_config
from planspiel.printmodel import PrintModelError
from planspiel.review_text import penalty_rows
from planspiel.rules import Path, Window
from planspiel.texts import PREWAVE_SHEETS, PreAttackView, load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT
from tests.support.tracking_replay import replay_tracking

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]
WRITE, SHADED = "write", "shaded"
REPLAY_MODULE = REPO_ROOT / "tests" / "support" / "tracking_replay.py"
FORBIDDEN_IN_REPLAY = {"evaluate_path", "simulate_waves", "budget_ledger", "evaluate_plan", "simulate_selection"}
RETIRED_KEYS = (
    "sheets.budget.status_tracker_intro",
    "sheets.labels.status_tracker",
    "sheets.labels.point_in_time",
    "sheets.labels.kz_cumulative",
)


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    cfg = load_config(config_path)
    texts = load_texts(content_dir / "texte.toml")
    return cfg, texts, build_tracking_page(cfg, texts)


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, texts, build_tracking_page(cfg, texts)


def _row(page, key):
    return next(row for row in page.rows if row.key == key)


def _all_text(value) -> str:
    return "\n".join(printed_strings(value))


# ---- clamp bounds live in rules -----------------------------------------------------------------------------------


def test_the_kz_bounds_are_named_in_rules_and_clamp_uses_them():
    assert (rules.KZ_MIN, rules.KZ_MAX) == (0, 100)
    assert rules.clamp_kz(-5) == rules.KZ_MIN == 0
    assert rules.clamp_kz(105) == rules.KZ_MAX == 100
    assert rules.clamp_kz(42) == 42


# ---- columns and rows ---------------------------------------------------------------------------------------------


def test_the_columns_are_start_one_per_wave_and_budget_review(loaded):
    cfg, texts, page = loaded
    view = PreAttackView(cfg, texts)
    expected = (
        view.sheet("labels")["start"],
        *(f"{view.sheet('tracking')['wave']} {wave.wave_id}" for wave in cfg.waves),
        view.sheet("teamheft")["review_title"],
    )
    assert page.columns == expected
    assert page.columns[0] == "Start" and page.columns[-1] == "Budget Review"


def test_the_real_columns_read_start_welle_1_to_3_budget_review(real):
    assert real[2].columns == ("Start", "Welle 1", "Welle 2", "Welle 3", "Budget Review")


def test_the_row_order_is_the_calculation_order(loaded):
    page = loaded[2]
    assert TRACKING_ROW_ORDER == (
        "kz_before", "kz_change", "kz_after", "damage", "own_init", "own_opex", "own_window",
        "external_budget", "external_opex", "remaining",
    )
    assert tuple(row.key for row in page.rows) == (*TRACKING_ROW_ORDER, "kz_review", "kz_final")
    assert all(isinstance(row, TrackingRow) for row in page.rows)
    assert all(len(row.cells) == len(page.columns) for row in page.rows)


def test_the_groups_separate_own_costs_from_external_effects(loaded):
    page = loaded[2]
    groups = {row.key: row.group for row in page.rows}
    assert groups == {
        "kz_before": "kz", "kz_change": "kz", "kz_after": "kz", "damage": "damage",
        "own_init": "own", "own_opex": "own", "own_window": "own",
        "external_budget": "external", "external_opex": "external",
        "remaining": "budget", "kz_review": "review", "kz_final": "review",
    }
    assert "RoS" in page.block_own and "zählen für" in page.block_own
    assert "zählen nicht für" in page.block_external and "RoS" in page.block_external


def test_the_real_block_titles_are_the_ones_of_the_decision(real):
    assert real[2].block_own == "Eigene Kosten (zählen für den RoS)"
    assert real[2].block_external == "Externe Effekte (zählen nicht für den RoS)"


def test_the_cell_states_follow_the_calculation(loaded):
    cfg, _, page = loaded
    waves = len(cfg.waves)
    start, wave_cols, review = 0, range(1, waves + 1), waves + 1

    def states(key):
        return _row(page, key).cells

    assert states("kz_before")[start] == WRITE and all(states("kz_before")[c] == WRITE for c in wave_cols)
    assert states("kz_before")[review] == SHADED
    for key in ("kz_change", "kz_after", "damage", "own_opex"):
        cells = states(key)
        assert cells[start] == SHADED and cells[review] == SHADED, key
        assert all(cells[c] == WRITE for c in wave_cols), key
    own_init = states("own_init")
    assert own_init[start] == WRITE and all(c == SHADED for c in own_init[1:])
    window = states("own_window")
    assert window[start] == SHADED and window[review] == SHADED
    assert [window[c] for c in wave_cols] == [WRITE] * (waves - 1) + [SHADED], "no window after the last wave"
    remaining = states("remaining")
    assert all(cell == WRITE for cell in remaining)
    for key in ("kz_review", "kz_final"):
        cells = states(key)
        assert cells[review] == WRITE and all(c == SHADED for c in cells[:review]), key


def test_the_external_cells_are_open_in_every_wave_so_the_grey_pattern_does_not_reveal_the_events(loaded):
    """V1 (quick 261125-djw): a grey cell would tell the teams in which wave a budget or OPEX event comes."""
    cfg, _, page = loaded
    for key in ("external_budget", "external_opex"):
        assert list(_row(page, key).cells) == [SHADED] + [WRITE] * len(cfg.waves) + [SHADED], key


def test_on_the_real_config_the_external_rows_are_open_in_all_waves_and_the_window_row_in_two(real):
    page = real[2]
    assert _row(page, "external_budget").cells == (SHADED, WRITE, WRITE, WRITE, SHADED)
    assert _row(page, "external_opex").cells == (SHADED, WRITE, WRITE, WRITE, SHADED)
    assert _row(page, "own_window").cells == (SHADED, WRITE, WRITE, SHADED, SHADED)


def test_the_clamp_text_names_the_bounds_from_rules_and_no_other_digit(loaded):
    page = loaded[2]
    assert str(rules.KZ_MIN) in page.clamp_text and str(rules.KZ_MAX) in page.clamp_text
    assert "".join(char for char in page.clamp_text if char.isdigit()) == f"{rules.KZ_MIN}{rules.KZ_MAX}"


def test_the_real_clamp_text_reads_begrenzt_auf_0_bis_100(real):
    assert real[2].clamp_text.endswith("begrenzt auf 0 bis 100")


def test_the_kz_final_row_names_its_operands_and_the_sheet_has_no_gr_abbreviation(loaded):
    page = loaded[2]
    final = _row(page, "kz_final").label
    assert _row(page, "kz_review").label in final and "=" in final and "+" in final
    assert not re.search(r"\bGR\b", _all_text(page))


# ---- change windows -----------------------------------------------------------------------------------------------


def test_there_is_one_window_block_per_gap_between_waves(loaded):
    cfg, _, page = loaded
    assert len(page.windows) == len(cfg.waves) - 1
    assert all(isinstance(block, WindowBlock) for block in page.windows)
    title = PreAttackView(cfg, loaded[1]).sheet("tracking")["window_title"]
    assert [block.after_wave for block in page.windows] == [f"{title} {wave.wave_id}" for wave in cfg.waves[:-1]]


def test_every_window_lists_every_measure_once_with_its_label(loaded):
    cfg, _, page = loaded
    expected = tuple(f"{measure_id} – {measure.name}" for measure_id, measure in cfg.measures.items())
    for block in page.windows:
        assert block.measure_rows == expected


def test_only_the_kurswechsel_window_has_the_credit_row(loaded):
    cfg, texts, page = loaded
    kurswechsel = rules.kurswechsel_wave(cfg.events)
    words = PreAttackView(cfg, texts).sheet("tracking")
    for wave, block in zip(cfg.waves, page.windows):
        assert block.with_credit == (wave.wave_id == kurswechsel)
        assert (words["window_credit"] in block.summary_rows) == block.with_credit
        assert words["window_sum"] in block.summary_rows
    assert sum(block.with_credit for block in page.windows) == 1


def test_the_net_difference_row_says_there_is_never_a_refund(loaded):
    cfg, texts, page = loaded
    words = PreAttackView(cfg, texts).sheet("tracking")
    net = next(row for row in page.summary_rows if row.key == "window_net")
    assert words["window_net"] in net.label and words["never_refund"] in net.label
    assert words["window_credit"] in next(row for row in page.summary_rows if row.key == "window_credit").label
    assert [row.key for row in page.summary_rows] == ["window_sum", "window_credit", "window_net"]
    for row in page.summary_rows:
        assert len(row.cells) == len(page.windows)
    credit = next(row for row in page.summary_rows if row.key == "window_credit")
    assert list(credit.cells) == [WRITE if block.with_credit else SHADED for block in page.windows]


def test_the_real_credit_and_net_labels_use_the_decision_wording(real):
    page = real[2]
    assert next(row for row in page.summary_rows if row.key == "window_credit").label == "Kurswechsel: Gutschrift Kunde"
    net = next(row for row in page.summary_rows if row.key == "window_net").label
    assert net.startswith("Init-Differenz netto = Summe Init-Erhöhungen " + fmt.MINUS) and net.endswith("nie eine Erstattung")
    assert page.window_columns == ("Level nach dem Fenster", "Δ Init")


def test_more_windows_than_the_layout_holds_stop_the_build(monkeypatch):
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    assert MAX_WINDOWS == len(cfg.waves) - 1 == 2
    monkeypatch.setattr(booklet, "MAX_WINDOWS", 1)
    with pytest.raises(PrintModelError, match="MAX_WINDOWS"):
        build_tracking_page(cfg, texts)


# ---- printed text -------------------------------------------------------------------------------------------------


def test_the_booklet_carries_the_tracking_page_between_planning_and_ros(loaded):
    cfg, texts, page = loaded
    team = build_team_booklet(cfg, texts)
    assert isinstance(team, TeamBooklet) and team.tracking == page


def test_printed_fragments_are_unique_and_hold_the_bounds_and_the_wave_numbers(loaded):
    cfg, _, page = loaded
    fragments = page.printed_fragments()
    assert len(set(fragments)) == len(fragments) and all(fragments)
    assert page.clamp_text in fragments
    for column in page.columns:
        assert column in fragments
    text = "\n".join(fragments)
    for wave in cfg.waves[:-1]:
        assert str(wave.wave_id) in text


def test_the_wording_pieces_of_the_sheet_hold_no_digit(loaded):
    cfg, texts, _ = loaded
    for key, value in PreAttackView(cfg, texts).sheet("tracking").items():
        # `Level 0` is the one allowlisted digit string (sheets.tracking.window_intro, content/digit_allowlist.toml)
        assert not any(char.isdigit() for char in value.replace("Level 0", "")), key


def test_the_tracking_sheet_is_pre_wave_and_legacy_tracker_keys_are_retired(loaded):
    cfg, texts, _ = loaded
    assert "tracking" in PREWAVE_SHEETS
    for key in RETIRED_KEYS:
        assert key not in texts_module.SHEET_KEYS
        with pytest.raises(KeyError):
            texts.get(key)
    assert all(key.startswith("sheets.tracking.") for key in texts_module.SHEET_KEYS if "tracking" in key)


def test_no_wave_weights_or_attack_names_on_the_tracking_page(real):
    cfg, texts, page = real
    text = _all_text(page)
    assert "wC" not in text
    for attack_id in cfg.attacks:
        assert texts.get(f"attacks.{attack_id}.revealed.name") not in text


# ---- the printed procedure replayed against the simulation --------------------------------------------------------


REAL_IDS = tuple(f"M{number}" for number in range(1, 11))


def _selection(level=0, **levels):
    return {measure_id: levels.get(measure_id, level) for measure_id in REAL_IDS}


def _paths():
    start = _selection(M1=2, M2=1, M3=1, M4=1, M5=1)
    swapped = _selection(M1=2, M2=1, M3=1, M4=1, M8=3)
    downgraded = _selection(M1=1, M2=1, M3=1, M4=2, M8=3)
    swap = ("M5", "M8")
    return [
        pytest.param(Path(_selection(level=1)), id="all-active-no-swap-possible"),
        pytest.param(Path(start, (Window(swapped, swap),)), id="kurswechsel-swap"),
        pytest.param(Path(start, (Window(swapped, swap), Window(downgraded))), id="swap-and-downgrade-in-window-2"),
    ]


@pytest.fixture(scope="module")
def world():
    return load_config(CONFIG_PATH), load_texts(CONTENT_DIR / "texte.toml")


def _worksheet_inputs(record):
    """What a team copies from its attack worksheets: the once-rounded change of each wave and the damage."""
    changes = [
        rules.wave_kz_change(wave["kz_delta_attack"], sum(event["kz_delta"] for event in wave["events"]))
        for wave in record["waves"]
    ]
    return changes, [wave["damage"] for wave in record["waves"]]


@pytest.mark.parametrize("path", _paths())
@pytest.mark.parametrize("tier", ["low", "medium", "high"])
def test_filling_the_printed_rows_reproduces_evaluate_path(world, path, tier):
    cfg, texts = world
    record = rules.evaluate_path(cfg, tier, path)
    changes, damages = _worksheet_inputs(record)
    result = replay_tracking(cfg, tier, path, changes, damages, texts)

    assert list(result.kz_after) == [wave["kz_after"] for wave in record["waves"]]
    assert result.kz_final == record["kz_final"]
    assert result.own_spend == record["costs"]["security_spend"]
    assert result.remaining_final == record["costs"]["remaining"]
    assert list(result.window_nets) == [window["cost"] for window in record["windows"]]
    assert result.own_init == record["costs"]["init"]
    assert list(result.own_opex) == record["costs"]["opex_by_wave"]
    assert sum(result.damages) == record["total_damage"]


def _printed_overspend_row(cfg, overspend_k):
    """The KZ value of the row of the printed overspend table that contains the overspend (in whole euros)."""
    over_eur = overspend_k * 1000
    for from_eur, to_eur, kz in penalty_rows(*rules.penalty_params(cfg.final_events)):
        if from_eur <= over_eur <= to_eur:
            return kz
    raise AssertionError("overspend beyond the printed table")


@pytest.mark.parametrize(
    ("path", "expected_review"),
    [
        pytest.param(Path(_selection(level=1, M1=2, M2=2, M3=2)), None, id="overspend-row-of-the-printed-table"),
        pytest.param(Path(_selection(level=3)), -rules.KZ_MAX, id="all-level-three-clamps-both-ends"),
    ],
)
def test_overspend_and_both_clamps_follow_the_printed_tables(world, path, expected_review):
    cfg, texts = world
    record = rules.evaluate_path(cfg, "low", path)
    result = replay_tracking(cfg, "low", path, *_worksheet_inputs(record), texts)
    assert result.remaining_final < 0 and result.remaining_final == record["costs"]["remaining"]
    if expected_review is None:
        expected_review = _printed_overspend_row(cfg, -result.remaining_final)
    assert result.kz_review == expected_review
    assert result.kz_final == record["kz_final"]
    assert list(result.kz_after) == [wave["kz_after"] for wave in record["waves"]]
    if expected_review == -rules.KZ_MAX:
        assert result.kz_final == rules.KZ_MIN and rules.KZ_MAX in result.kz_after


def test_the_replayed_windows_carry_a_cost_and_the_swap_credit(world):
    cfg, texts = world
    start = _selection(M1=2, M2=1, M3=1, M4=1, M5=1)
    path = Path(start, (Window(_selection(M1=2, M2=1, M3=1, M4=1, M8=3), ("M5", "M8")),))
    record = rules.evaluate_path(cfg, "medium", path)
    result = replay_tracking(cfg, "medium", path, *_worksheet_inputs(record), texts)
    assert result.window_nets[0] > 0
    assert result.credits[0] == min(
        rules.card_facts(cfg.measures, "M5", 1).init_k, rules.card_facts(cfg.measures, "M8", 3).init_k
    ) > 0
    assert result.window_nets[0] == result.increases[0] - result.credits[0]


def test_a_downgrade_adds_nothing_to_the_increases(world):
    cfg, texts = world
    path = _paths()[2].values[0]
    record = rules.evaluate_path(cfg, "medium", path)
    result = replay_tracking(cfg, "medium", path, *_worksheet_inputs(record), texts)
    before, after = record["selections"][1], record["selections"][2]
    assert any(after[m] < before[m] for m in cfg.measures), "window 2 holds a downgrade"
    rises = sum(
        max(0, rules.card_facts(cfg.measures, m, after[m]).init_k - rules.card_facts(cfg.measures, m, before[m]).init_k)
        for m in cfg.measures
    )
    assert result.increases[1] == rises
    assert result.credits[1] == 0


def test_without_the_credit_row_the_first_window_difference_is_wrong(world):
    cfg, texts = world
    path = _paths()[1].values[0]
    record = rules.evaluate_path(cfg, "medium", path)
    changes, damages = _worksheet_inputs(record)
    wrong = replay_tracking(cfg, "medium", path, changes, damages, texts, ignore_credit=True)
    assert wrong.window_nets[0] != record["windows"][0]["cost"]
    assert wrong.own_spend != record["costs"]["security_spend"]


def test_the_replay_never_touches_the_path_evaluator():
    tree = ast.parse(REPLAY_MODULE.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            names.update(alias.name.split(".")[-1] for alias in node.names)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Name):
            names.add(node.id)
    assert not names & FORBIDDEN_IN_REPLAY, names & FORBIDDEN_IN_REPLAY
    assert FilePath(REPLAY_MODULE).exists()
