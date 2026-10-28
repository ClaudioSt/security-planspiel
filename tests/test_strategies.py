"""BAL-07 ("good strategies lead to good outcomes"): quartile placement, the clue-derived good strategy, the guard.

The behaviour tests run on the mini config against brute forces built only from rules.evaluate_plan,
rules.evaluate_path and the swap-layer brute force of tests/test_swap_layer.py. The slow checks run on the config and
content directory chosen with --planspiel-config / --planspiel-content-dir; all of them are tuning targets today
(no reference_strategies block, no clue mapping in content/clues.toml).
"""
import copy
import dataclasses
import functools
import math
from fractions import Fraction

import pytest

from planspiel import enumerate as enum
from planspiel import refpaths, rules, strategies
from planspiel.strategies import Placement
from planspiel.texts import check_clues, load_clues
from tests.support import MINI_CONTENT_DIR, REPO_ROOT, candidate, harness
from tests.test_swap_layer import _brute_games

TIERS = ("low", "medium", "high")
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
MINI_CLUES = load_clues(MINI_CONTENT_DIR / "clues.toml")


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


@functools.lru_cache(maxsize=None)
def _store(tier):
    return enum.enumerate_tier(harness.load_config(MINI), tier)


@functools.lru_cache(maxsize=None)
def _layer(tier):
    return enum.enumerate_swap_layer(harness.load_config(MINI), tier)


@functools.lru_cache(maxsize=None)
def _static_rows(tier):
    """(code, selection, kz, final index, own cost) of every in-budget static plan, via rules.evaluate_plan."""
    cfg = harness.load_config(MINI)
    weights = cfg.final_index
    rows = []
    for code in harness.iter_codes(cfg):
        selection = harness.selection_of(cfg, code)
        record = harness.evaluate(cfg, tier, selection)
        if not record["valid"] or record["over_budget"]:
            continue
        index = rules.final_index(record["kz_final"], record["ros"], weights.weight_kz, weights.weight_ros)
        rows.append((code, selection, record["kz_final"], index, record["costs"]["security_spend"]))
    return rows


def _swap_kz(tier):
    return [game[6].kz_final for game in _brute_games(tier) if not game[6].over_budget]


def _share(values, predicate):
    return Fraction(sum(1 for value in values if predicate(value)), len(values))


# ---------------------------------------------------------------------------------------------------------------
# constants and the placement rule
# ---------------------------------------------------------------------------------------------------------------


def test_constants_are_the_documented_proposals():
    assert strategies.QUARTILE == Fraction(3, 4)
    assert strategies.LOWER_QUARTILE == Fraction(1, 4)
    assert strategies.TOP_SHARE == Fraction(1, 100)
    assert strategies.NON_CLUE_SHARE_MIN == Fraction(1, 5)


QUARTER = Fraction(1, 4)
THREE_QUARTERS = Fraction(3, 4)


@pytest.mark.parametrize(
    "kind, shares, expected",
    [
        ("good", (THREE_QUARTERS, 0, THREE_QUARTERS, 0), True),
        ("good", (THREE_QUARTERS, 0, Fraction(74, 100), 0), False),
        ("good", (Fraction(74, 100), 0, THREE_QUARTERS, 0), False),
        ("bad", (0, THREE_QUARTERS, 0, THREE_QUARTERS), True),
        ("bad", (0, THREE_QUARTERS, 0, Fraction(74, 100)), False),
        ("bad", (0, Fraction(74, 100), 0, THREE_QUARTERS), False),
        ("mediocre", (QUARTER, QUARTER, QUARTER, QUARTER), True),
        ("mediocre", (Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)), True),
        ("mediocre", (Fraction(24, 100), QUARTER, QUARTER, QUARTER), False),
        ("mediocre", (QUARTER, QUARTER, QUARTER, Fraction(24, 100)), False),
        ("mediocre", (THREE_QUARTERS, QUARTER, THREE_QUARTERS, QUARTER), True),
        ("excellent", (1, 0, 1, 0), False),
    ],
)
def test_placed_by_kind_uses_inclusive_quartile_bounds(kind, shares, expected):
    fi_below, fi_above, kz_below, kz_above = (Fraction(value) for value in shares)
    assert strategies.placed_by_kind(kind, fi_below, fi_above, kz_below, kz_above) is expected


# ---------------------------------------------------------------------------------------------------------------
# place_strategies against brute forces
# ---------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("tier", TIERS)
def test_placement_equals_a_brute_force_over_both_populations(mini, tier):
    placements = strategies.place_strategies(mini, tier, _store(tier), _layer(tier))
    block = mini.reference_strategies[tier]
    assert [placement.name for placement in placements] == list(block)
    rows = _static_rows(tier)
    swap_kz = _swap_kz(tier)
    weights = mini.final_index
    for placement in placements:
        entry = block[placement.name]
        record = rules.evaluate_path(mini, tier, refpaths.path_from_block(entry))
        index = rules.final_index(record["kz_final"], record["ros"], weights.weight_kz, weights.weight_ros)
        assert isinstance(placement, Placement)
        assert (placement.tier, placement.kind) == (tier, entry["kind"])
        assert placement.legal is True and placement.in_budget is (not record["over_budget"])
        assert (placement.kz_final, placement.ros, placement.final_index) == (record["kz_final"], record["ros"], index)
        assert placement.fi_below == _share([row[3] for row in rows], lambda value: value < index)
        assert placement.fi_above == _share([row[3] for row in rows], lambda value: value > index)
        assert placement.kz_below == _share(swap_kz, lambda value: value < record["kz_final"])
        assert placement.kz_above == _share(swap_kz, lambda value: value > record["kz_final"])
        assert placement.placed is (
            placement.in_budget
            and strategies.placed_by_kind(
                placement.kind, placement.fi_below, placement.fi_above, placement.kz_below, placement.kz_above
            )
        )


def test_the_static_population_is_the_in_budget_plans_only(mini):
    store = _store("low")
    in_budget = sum(1 for flag in store.column("over_budget") if flag == 0)
    assert 0 < in_budget < len(store)
    assert len(_static_rows("low")) == in_budget


def _with_entries(cfg, tier, entries):
    return dataclasses.replace(cfg, reference_strategies={tier: entries})


def test_an_illegal_path_is_reported_not_placed(mini):
    tier = "medium"
    entry = copy.deepcopy(mini.reference_strategies[tier]["good"])
    entry["windows"] = []  # the Kurswechsel swap is missing
    cfg = _with_entries(mini, tier, {"good": entry})
    (placement,) = strategies.place_strategies(cfg, tier, _store(tier), _layer(tier))
    assert placement.legal is False and placement.placed is False and placement.in_budget is False
    assert placement.kz_final is None and placement.ros is None and placement.final_index is None
    assert placement.fi_below is None and placement.kz_above is None


def test_an_over_budget_path_is_legal_but_never_placed(mini):
    tier = "low"
    all_in = {"M1": 3, "M2": 2, "M4": 3, "M6": 3}
    entry = {"kind": "good", "start": all_in, "windows": []}
    cfg = _with_entries(mini, tier, {"good": entry})
    (placement,) = strategies.place_strategies(cfg, tier, _store(tier), _layer(tier))
    assert placement.legal is True and placement.in_budget is False and placement.placed is False
    assert placement.kz_final == rules.evaluate_path(mini, tier, refpaths.path_from_block(entry))["kz_final"]


def test_a_tier_without_entries_places_nothing(mini):
    cfg = dataclasses.replace(mini, reference_strategies={})
    assert strategies.place_strategies(cfg, "low", _store("low"), _layer("low")) == []


def test_strategy_path_is_the_shared_path_builder(mini):
    entry = mini.reference_strategies["low"]["good"]
    assert strategies.strategy_path(entry) == refpaths.path_from_block(entry)


# ---------------------------------------------------------------------------------------------------------------
# clue scores and the clue-derived good start (D-19)
# ---------------------------------------------------------------------------------------------------------------


def _expected_good_start(cfg, tier, clues):
    """The clue-following procedure written out independently of planspiel/strategies.py."""
    scores = {}
    for clue in clues:
        for measure_id in clue.measures:
            scores[measure_id] = scores.get(measure_id, 0) + clue.weight
    importance = rules.bonus_importance(cfg)
    ids = list(cfg.measures)
    ordered = sorted(
        (m for m in ids if scores.get(m, 0) > 0), key=lambda m: (-scores[m], -importance.get(m, 0), ids.index(m))
    )

    def fits(selection):
        return rules.dependencies_satisfied(selection, cfg.measures) and not rules.evaluate_plan(
            cfg, tier, selection
        )["over_budget"]

    selection = {m: 0 for m in ids}
    for measure_id in ordered:
        for level in (2, 1):
            trial = dict(selection, **{measure_id: level})
            if fits(trial):
                selection = trial
                break
    while True:
        cia = rules.compute_cia(selection, cfg.measures, cfg.base_cia)
        current = min(cia.values())
        best = None
        for position, measure_id in enumerate(ids):
            if selection[measure_id] >= 3:
                continue
            trial = dict(selection, **{measure_id: selection[measure_id] + 1})
            if not fits(trial):
                continue
            trial_cia = rules.compute_cia(trial, cfg.measures, cfg.base_cia)
            spend = rules.evaluate_plan(cfg, tier, trial)["costs"]["security_spend"]
            key = (-min(trial_cia.values()), -sum(trial_cia.values()), spend, position)
            if best is None or key < best[0]:
                best = (key, trial, min(trial_cia.values()))
        if best is None or best[2] <= current:
            return selection
        selection = best[1]


def test_clue_scores_are_re_exported_from_the_texts_module():
    from planspiel import texts

    assert strategies.clue_scores is texts.clue_scores
    assert strategies.clue_scores(MINI_CLUES) == {"M4": 2, "M6": 2, "M1": 5, "M2": 3}


@pytest.mark.parametrize("tier", TIERS)
def test_the_clue_good_start_follows_the_written_out_procedure(mini, tier):
    got = strategies.clue_good_start(mini, tier, MINI_CLUES)
    assert got == _expected_good_start(mini, tier, MINI_CLUES)
    assert rules.dependencies_satisfied(got, mini.measures)
    assert rules.evaluate_plan(mini, tier, got)["over_budget"] is False
    assert list(got) == list(mini.measures)


def test_the_clue_good_start_buys_in_score_order_at_level_two_first(mini):
    got = strategies.clue_good_start(mini, "medium", MINI_CLUES)
    # M1 (score 5) and M2 (3) come before M4 and M6 (2 each, M4 more important); all fit at level 2 in medium
    assert got["M1"] >= 2 and got["M2"] >= 2 and got["M4"] >= 2


def test_the_good_start_falls_back_to_level_one_when_level_two_does_not_fit(mini):
    tiers = dict(mini.budget_tiers)
    tiers["low"] = dataclasses.replace(tiers["low"], budget=80)
    tight = dataclasses.replace(mini, budget_tiers=tiers)
    got = strategies.clue_good_start(tight, "low", MINI_CLUES)
    assert got == _expected_good_start(tight, "low", MINI_CLUES)
    assert rules.evaluate_plan(tight, "low", got)["over_budget"] is False
    assert any(level == 1 for level in got.values())


def test_without_a_mapping_the_good_start_buys_nothing_clue_driven(mini):
    stripped = tuple(dataclasses.replace(clue, measures=(), weight=0) for clue in MINI_CLUES)
    got = strategies.clue_good_start(mini, "medium", stripped)
    assert got == _expected_good_start(mini, "medium", stripped)


def test_balancing_raises_only_while_the_weakest_dimension_strictly_improves(mini):
    got = strategies.clue_good_start(mini, "medium", MINI_CLUES)
    cia = rules.compute_cia(got, mini.measures, mini.base_cia)
    for measure_id, level in got.items():
        if level >= 3:
            continue
        trial = dict(got, **{measure_id: level + 1})
        if not rules.dependencies_satisfied(trial, mini.measures):
            continue
        if rules.evaluate_plan(mini, "medium", trial)["over_budget"]:
            continue
        assert min(rules.compute_cia(trial, mini.measures, mini.base_cia).values()) <= min(cia.values())


# ---------------------------------------------------------------------------------------------------------------
# non_clue_share (D-19 guard)
# ---------------------------------------------------------------------------------------------------------------


def _brute_non_clue(tier, clues, top=Fraction(1, 100)):
    rows = _static_rows(tier)
    ranked = sorted(rows, key=lambda row: (-row[3], -row[2], row[4], row[0]))
    count = math.ceil(len(rows) * top)
    scores = strategies.clue_scores(clues)
    unsupported = sum(
        1 for row in ranked[:count] if any(level >= 1 and scores.get(m, 0) == 0 for m, level in row[1].items())
    )
    return Fraction(unsupported, count)


@pytest.mark.parametrize("tier", TIERS)
@pytest.mark.parametrize("top", [Fraction(1, 100), Fraction(1, 10), Fraction(1, 1)])
def test_non_clue_share_equals_a_brute_force(mini, tier, top):
    assert strategies.non_clue_share(mini, _store(tier), MINI_CLUES, top) == _brute_non_clue(tier, MINI_CLUES, top)


def test_non_clue_share_defaults_to_the_top_one_percent(mini):
    assert strategies.non_clue_share(mini, _store("medium"), MINI_CLUES) == _brute_non_clue("medium", MINI_CLUES)


def test_without_any_clue_support_every_plan_counts_as_unsupported(mini):
    stripped = tuple(dataclasses.replace(clue, measures=(), weight=0) for clue in MINI_CLUES)
    assert strategies.non_clue_share(mini, _store("medium"), stripped, Fraction(1, 10)) == 1


def test_with_every_measure_supported_no_plan_counts_as_unsupported(mini):
    covering = tuple(
        dataclasses.replace(clue, measures=("M1", "M2", "M4", "M6"), weight=2) for clue in MINI_CLUES
    )
    assert strategies.non_clue_share(mini, _store("medium"), covering, Fraction(1, 10)) == 0


# ---------------------------------------------------------------------------------------------------------------
# check_strategies
# ---------------------------------------------------------------------------------------------------------------


def _placement(name, kind, **changes):
    values = dict(
        tier="medium", name=name, kind=kind, legal=True, in_budget=True, kz_final=60, ros=Fraction(1, 2),
        final_index=Fraction(70), fi_below=Fraction(1, 2), fi_above=Fraction(1, 2), kz_below=Fraction(1, 2),
        kz_above=Fraction(1, 2), placed=True,
    )
    values.update(changes)
    return Placement(**values)


def _good_config(mini, tier="medium", clues=MINI_CLUES):
    start = strategies.clue_good_start(mini, tier, clues)
    entries = {
        "good": {"kind": "good", "start": start, "windows": []},
        "middle": {"kind": "mediocre", "start": start, "windows": []},
        "poor": {"kind": "bad", "start": start, "windows": []},
    }
    return _with_entries(mini, tier, entries)


def _placements():
    return [_placement("good", "good"), _placement("middle", "mediocre"), _placement("poor", "bad")]


def test_a_complete_well_placed_set_passes(mini):
    cfg = _good_config(mini)
    assert strategies.check_strategies(cfg, "medium", _placements(), MINI_CLUES, Fraction(1, 3)) == []


def test_the_non_clue_share_boundary_is_inclusive(mini):
    cfg = _good_config(mini)
    assert strategies.check_strategies(cfg, "medium", _placements(), MINI_CLUES, Fraction(1, 5)) == []
    lines = strategies.check_strategies(cfg, "medium", _placements(), MINI_CLUES, Fraction(19, 100))
    assert len(lines) == 1 and "Hinweis" in lines[0]


def test_a_tier_without_entries_is_reported(mini):
    cfg = dataclasses.replace(mini, reference_strategies={})
    lines = strategies.check_strategies(cfg, "medium", [], MINI_CLUES, Fraction(1, 3))
    assert any("medium" in line and "Referenzstrategien" in line for line in lines)


@pytest.mark.parametrize("kind", ["good", "mediocre", "bad"])
def test_a_missing_kind_is_reported(mini, kind):
    cfg = _good_config(mini)
    placements = [placement for placement in _placements() if placement.kind != kind]
    lines = strategies.check_strategies(cfg, "medium", placements, MINI_CLUES, Fraction(1, 3))
    assert len(lines) == 1 and kind in lines[0]


def test_an_illegal_entry_is_reported_once(mini):
    cfg = _good_config(mini)
    placements = [_placement("good", "good"), _placement("middle", "mediocre"), _placement("poor", "bad", legal=False, in_budget=False, placed=False)]
    lines = strategies.check_strategies(cfg, "medium", placements, MINI_CLUES, Fraction(1, 3))
    assert len(lines) == 1 and "poor" in lines[0] and "legal" in lines[0]


def test_an_over_budget_entry_is_reported_once_and_refers_to_the_gate(mini):
    cfg = _good_config(mini)
    placements = [_placement("good", "good"), _placement("middle", "mediocre"), _placement("poor", "bad", in_budget=False, placed=False)]
    lines = strategies.check_strategies(cfg, "medium", placements, MINI_CLUES, Fraction(1, 3))
    assert len(lines) == 1 and "poor" in lines[0] and "Überziehungs-Gate" in lines[0]


def test_a_misplaced_entry_names_its_shares(mini):
    cfg = _good_config(mini)
    placements = [_placement("good", "good", placed=False, fi_below=Fraction(1, 2)), _placement("middle", "mediocre"), _placement("poor", "bad")]
    lines = strategies.check_strategies(cfg, "medium", placements, MINI_CLUES, Fraction(1, 3))
    assert len(lines) == 1 and "good" in lines[0] and "Viertel" in lines[0]


def test_a_missing_good_entry_is_reported(mini):
    cfg = _good_config(mini)
    entries = dict(cfg.reference_strategies["medium"])
    entries["best"] = entries.pop("good")
    cfg = _with_entries(mini, "medium", entries)
    placements = [_placement("best", "good"), _placement("middle", "mediocre"), _placement("poor", "bad")]
    lines = strategies.check_strategies(cfg, "medium", placements, MINI_CLUES, Fraction(1, 3))
    assert len(lines) == 1 and "'good'" in lines[0]


def test_a_good_start_that_differs_from_the_clue_procedure_is_reported(mini):
    cfg = _good_config(mini)
    entries = copy.deepcopy(cfg.reference_strategies["medium"])
    entries["good"]["start"] = dict(entries["good"]["start"], M1=0)
    cfg = _with_entries(mini, "medium", entries)
    lines = strategies.check_strategies(cfg, "medium", _placements(), MINI_CLUES, Fraction(1, 3))
    assert len(lines) == 1 and "Hinweis" in lines[0] and "good" in lines[0]


def test_a_clue_edit_that_changes_the_good_plan_breaks_the_check(mini):
    cfg = _good_config(mini)
    other = tuple(dataclasses.replace(clue, measures=("M6",), weight=3) if clue.measures else clue for clue in MINI_CLUES)
    assert strategies.clue_good_start(mini, "medium", other) != strategies.clue_good_start(mini, "medium", MINI_CLUES)
    lines = strategies.check_strategies(cfg, "medium", _placements(), other, Fraction(1, 3))
    assert len(lines) == 1 and "good" in lines[0]


def test_every_line_is_german(mini):
    cfg = dataclasses.replace(mini, reference_strategies={})
    lines = strategies.check_strategies(cfg, "medium", [], MINI_CLUES, Fraction(0))
    assert lines and all(isinstance(line, str) and line for line in lines)


# ---------------------------------------------------------------------------------------------------------------
# strategies_tier and the console table
# ---------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("tier", TIERS)
def test_strategies_tier_bundles_the_pieces(mini, tier):
    block = strategies.strategies_tier(mini, tier, _store(tier), _layer(tier), MINI_CLUES)
    assert block["tier"] == tier
    assert block["placements"] == strategies.place_strategies(mini, tier, _store(tier), _layer(tier))
    assert block["non_clue_share"] == strategies.non_clue_share(mini, _store(tier), MINI_CLUES)
    assert block["good_start"] == strategies.clue_good_start(mini, tier, MINI_CLUES)
    assert block["failures"] == strategies.check_strategies(
        mini, tier, block["placements"], MINI_CLUES, block["non_clue_share"]
    )


def test_the_table_lists_every_strategy_with_its_placement(mini):
    blocks = {
        tier: strategies.strategies_tier(mini, tier, _store(tier), _layer(tier), MINI_CLUES) for tier in TIERS
    }
    text = strategies.format_strategies(blocks)
    lines = text.splitlines()
    assert "Referenzstrategien" in lines[0]
    for tier in TIERS:
        assert any(tier in line for line in lines)
    for name in ("good", "mediocre", "bad_ignore", "bad_all_in", "bad_hoard"):
        assert sum(1 for line in lines if name in line) >= 3
    assert "Final-Index" in text and "KZ" in text


def test_the_table_for_no_tiers_is_a_single_note():
    assert "keine" in strategies.format_strategies({}).lower()


# ---------------------------------------------------------------------------------------------------------------
# slow checks on the configured config and content (tuning targets today)
# ---------------------------------------------------------------------------------------------------------------


def _balance_inputs(config_path, content_dir):
    cfg = candidate.load_balance_config(config_path)
    clues = load_clues(content_dir / "clues.toml")
    return cfg, clues


def _tier_blocks(config_path, content_dir):
    cfg, clues = _balance_inputs(config_path, content_dir)
    for tier in cfg.budget_tiers:
        assert cfg.reference_strategies.get(tier), f"Tier {tier}: keine Referenzstrategien in der Config"
    stores = candidate.static_stores(config_path)
    layers = candidate.swap_layers(config_path)
    return {tier: strategies.strategies_tier(cfg, tier, stores[tier], layers[tier], clues) for tier in cfg.budget_tiers}


@pytest.mark.slow
@pytest.mark.balance
@candidate.TUNING_TARGET
def test_strategies_are_present_legal_and_in_budget(balance_config_path):
    cfg = candidate.load_balance_config(balance_config_path)
    for tier in cfg.budget_tiers:
        entries = cfg.reference_strategies.get(tier)
        assert entries, f"Tier {tier}: keine Referenzstrategien in der Config"
        assert {entry["kind"] for entry in entries.values()} == {"good", "mediocre", "bad"}
        for name, entry in entries.items():
            record = rules.evaluate_path(cfg, tier, refpaths.path_from_block(entry))  # PathError = illegal
            assert record["over_budget"] is False, f"{tier}/{name} liegt über dem Budget"


@pytest.mark.slow
@pytest.mark.balance
@candidate.TUNING_TARGET
def test_strategies_are_placed_by_kind_on_both_populations(balance_config_path, balance_content_dir):
    blocks = _tier_blocks(balance_config_path, balance_content_dir)
    misplaced = [
        f"{tier}/{placement.name}"
        for tier, block in blocks.items()
        for placement in block["placements"]
        if not placement.placed
    ]
    assert not misplaced, f"Nicht im erwarteten Viertel: {misplaced}\n{strategies.format_strategies(blocks)}"


@pytest.mark.slow
@pytest.mark.balance
@candidate.TUNING_TARGET
def test_the_good_strategy_is_derived_from_the_clues(balance_config_path, balance_content_dir):
    cfg, clues = _balance_inputs(balance_config_path, balance_content_dir)
    assert strategies.clue_scores(clues), "content/clues.toml enthält noch keine Maßnahmen-Zuordnung"
    for tier in cfg.budget_tiers:
        entries = cfg.reference_strategies.get(tier)
        assert entries and "good" in entries, f"Tier {tier}: keine Strategie 'good'"
        assert entries["good"]["start"] == strategies.clue_good_start(cfg, tier, clues), tier


@pytest.mark.slow
@pytest.mark.balance
@candidate.TUNING_TARGET
def test_buying_only_the_clued_measures_is_not_automatically_best(balance_config_path, balance_content_dir):
    cfg, clues = _balance_inputs(balance_config_path, balance_content_dir)
    assert strategies.clue_scores(clues), "content/clues.toml enthält noch keine Maßnahmen-Zuordnung"
    stores = candidate.static_stores(balance_config_path)
    for tier in cfg.budget_tiers:
        share = strategies.non_clue_share(cfg, stores[tier], clues)
        assert share >= strategies.NON_CLUE_SHARE_MIN, f"{tier}: nur {share} der besten Pläne enthalten eine unbelegte Maßnahme"


@pytest.mark.slow
@pytest.mark.balance
@candidate.TUNING_TARGET
def test_the_configured_clue_mapping_is_complete(balance_config_path, balance_content_dir):
    from planspiel.texts import load_texts

    cfg = candidate.load_balance_config(balance_config_path)
    texts = load_texts(balance_content_dir / "texte.toml")
    clues = load_clues(balance_content_dir / "clues.toml")
    issues = check_clues(cfg, texts, clues, require_mapping=True)
    assert not issues, [(issue.code, issue.path) for issue in issues]
