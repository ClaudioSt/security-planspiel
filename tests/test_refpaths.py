"""Reference path candidates: legal game paths near the swap-layer median, ranked by the mechanics they touch
(PRINT-10 part 2, D-18, D-22). The finder runs on the mini config here; the real tiers are checked at the checkpoint."""
import dataclasses
from fractions import Fraction

import pytest

from planspiel import enumerate as enum
from planspiel import refpaths, report, rules
from planspiel.cli import main
from planspiel.rules import Path, PathError, Window
from tests.support import REPO_ROOT, harness

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
TIERS = ("low", "medium", "high")


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


@pytest.fixture(scope="module")
def medians(mini):
    result = {}
    for tier in TIERS:
        summary = report.summarize_swap_layer(mini, tier, enum.enumerate_swap_layer(mini, tier))
        result[tier] = summary["percentiles"]["in_budget"]["kz_final"]["p50"]
    return result


def _wave(**override):
    base = dict(
        wave_id=1, attack_id="a", selection={}, cia={"c": 0, "i": 0, "a": 0}, e_value=Fraction(0),
        bonus_met=(), bonus_missed=(), bonus_reduction=0, gesamtreduktion=Fraction(0), case=1,
        damage_before_eur=0, recovery_factor=Fraction(0), damage_eur=0, kz_attack=Fraction(0), kz_event=0,
        kz_change_exact=Fraction(0), kz_change=0, kz_before=50, kz_unclamped=50, kz_after=50, own_opex_k=0,
        event_budget_k=0, event_opex_k=0, events=(), window_cost_k=0, remaining_k=0,
    )
    base.update(override)
    return rules.WaveTrace(**base)


def _trace(waves, windows=(), review_change=0):
    review = rules.ReviewTrace(
        kz_pre_review=50, kz_review_change=review_change, kz_final=50 + review_change, own_spend_k=0,
        remaining_k=0, total_damage_eur=0, over_budget=False, ros=None, final_events=(),
    )
    return rules.PathTrace("low", 0, 0, tuple(waves), tuple(windows), review)


def _plain_waves():
    return [_wave(wave_id=1, selection={"M1": 1}), _wave(wave_id=2, selection={"M1": 1})]


REVIEW_DELTAS = (0, 5, 10, 15)


def test_the_plain_trace_touches_no_mechanic():
    assert refpaths.mechanics_score(_trace(_plain_waves()), REVIEW_DELTAS) == 0


@pytest.mark.parametrize(
    "name, waves, windows, review_change",
    [
        ("fall-3 wave", [_wave(case=3), _wave(case=3)], (), 0),
        ("two distinct Falle", [_wave(case=1), _wave(case=2)], (), 0),
        ("recovery wave", [_wave(recovery_factor=Fraction(1, 10)), _wave()], (), 0),
        ("bonus met and missed in one wave", [_wave(bonus_met=("M1",), bonus_missed=("M2",)), _wave()], (), 0),
        ("non-zero event KZ", [_wave(kz_event=-4), _wave()], (), 0),
        (
            "voluntary move in a window without swap",
            [_wave(selection={"M1": 1}), _wave(selection={"M1": 1})],
            (rules.WindowTrace(after_wave=1, swap=None, increase_k=0, credit_k=0, cost_k=0, selection={"M1": 2}),),
            0,
        ),
        ("middle Budget Review tier", [_wave(), _wave()], (), 5),
    ],
)
def test_each_mechanic_adds_exactly_one_point(name, waves, windows, review_change):
    del name
    waves = [_wave(**{**w._asdict(), "selection": w.selection or {"M1": 1}}) for w in waves]
    assert refpaths.mechanics_score(_trace(waves, windows, review_change), REVIEW_DELTAS) == 1


def test_a_swap_window_alone_is_not_a_voluntary_move():
    swap_window = rules.WindowTrace(
        after_wave=1, swap=("M1", "M2"), increase_k=0, credit_k=0, cost_k=0, selection={"M1": 0, "M2": 1}
    )
    waves = [_wave(selection={"M1": 1, "M2": 0}), _wave(selection={"M1": 0, "M2": 1})]
    assert refpaths.mechanics_score(_trace(waves, (swap_window,)), REVIEW_DELTAS) == 0


@pytest.mark.parametrize("review_change", [0, 15, -9])
def test_lowest_highest_and_overspend_review_tiers_score_nothing(review_change):
    assert refpaths.mechanics_score(_trace(_plain_waves(), review_change=review_change), REVIEW_DELTAS) == 0


def test_the_review_criterion_is_skipped_without_tier_deltas():
    assert refpaths.mechanics_score(_trace(_plain_waves(), review_change=5)) == 0


def test_the_score_can_reach_the_maximum():
    waves = [
        _wave(selection={"M1": 1}, case=3, recovery_factor=Fraction(1, 10), bonus_met=("M1",), bonus_missed=("M2",),
              kz_event=3),
        _wave(selection={"M1": 1}, case=1),
    ]
    window = rules.WindowTrace(after_wave=1, swap=None, increase_k=0, credit_k=0, cost_k=0, selection={"M1": 2})
    assert refpaths.mechanics_score(_trace(waves, (window,), 5), REVIEW_DELTAS) == refpaths.MECHANICS_MAX


def test_voluntary_moves_exclude_the_swap_and_its_repair(mini):
    start = {"M1": 3, "M2": 2, "M4": 0, "M6": 0}
    swapped = rules.swap_repair(start, "M2", mini.measures)
    swapped["M4"] = 1
    window_one = Window(swapped, ("M2", "M4"))
    only_swap = Path(start, (window_one,))
    assert refpaths.voluntary_moves(mini, only_swap) == []
    moved = dict(swapped, M6=2)
    path = Path(start, (window_one, Window(moved)))
    assert refpaths.voluntary_moves(mini, path) == [(2, "M6", 0, 2)]
    extra = Path(start, (Window(dict(swapped, M6=1), ("M2", "M4")),))
    assert refpaths.voluntary_moves(mini, extra) == [(1, "M6", 0, 1)]


@pytest.mark.parametrize("tier", TIERS)
def test_candidates_are_legal_in_budget_and_near_the_median(mini, medians, tier):
    median = medians[tier]
    found = refpaths.candidate_paths(mini, tier, median=median)
    assert 1 <= len(found) <= 3
    swap_window = [wave.wave_id for wave in mini.waves].index(rules.kurswechsel_wave(mini.events))
    for candidate in found:
        assert candidate.tier == tier
        record = rules.evaluate_path(mini, tier, candidate.path)  # raises nothing: legal, Kurswechsel enforced
        assert record["over_budget"] is False
        assert candidate.path.windows[swap_window].swap is not None
        assert refpaths.voluntary_moves(mini, candidate.path)
        assert abs(record["kz_final"] - median) <= 2
        assert candidate.trace.review.kz_final == record["kz_final"]
        assert candidate.score == refpaths.mechanics_score(candidate.trace, refpaths.review_deltas(mini))


@pytest.mark.parametrize("tier", TIERS)
def test_candidates_are_sorted_by_score_then_distance_and_deterministic(mini, medians, tier):
    median = medians[tier]
    first = refpaths.candidate_paths(mini, tier, median=median)
    second = refpaths.candidate_paths(mini, tier, median=median)
    assert [(c.path, c.score) for c in first] == [(c.path, c.score) for c in second]
    keys = [(-c.score, abs(c.trace.review.kz_final - median)) for c in first]
    assert keys == sorted(keys)


def test_keep_limits_the_number_of_candidates(mini, medians):
    assert len(refpaths.candidate_paths(mini, "medium", median=medians["medium"], keep=1)) == 1


def test_without_a_median_the_swap_layer_p50_is_used(mini, medians):
    assert refpaths.swap_layer_median(mini, "medium") == medians["medium"]
    implicit = refpaths.candidate_paths(mini, "medium")
    explicit = refpaths.candidate_paths(mini, "medium", median=medians["medium"])
    assert [(c.path, c.score) for c in implicit] == [(c.path, c.score) for c in explicit]


def test_format_candidate_prints_the_German_worksheet_numbers(mini, medians):
    candidate = refpaths.candidate_paths(mini, "medium", median=medians["medium"])[0]
    text = refpaths.format_candidate(candidate, mini)
    for label in (
        "Tier medium", "Mechanik-Punkte", "Start:", "Welle 1", "Welle 3", "E-Wert", "Bonus", "GR", "Fall",
        "Schaden", "KZ-Änderung", "KZ ", "Restbudget", "Budget Review", "KZ final", "RoS", "Final-Index", "Gewichte KZ",
    ):
        assert label in text, label
    swap = candidate.path.windows[0].swap
    assert f"{swap[0]} gegen {swap[1]}" in text


def test_cli_prints_candidate_blocks_for_one_tier(mini, medians, capsys):
    code = main(["referenzpfade", "--config", str(MINI), "--tier", "medium", "--median", str(medians["medium"])])
    out = capsys.readouterr().out
    assert code == 0
    assert "Referenzpfade Tier medium" in out
    assert "Kandidat 1" in out and "Final-Index" in out and "vorläufig" not in out


def test_cli_without_tier_covers_every_tier_and_survives_an_empty_one(mini, capsys):
    code = main(["referenzpfade", "--config", str(MINI), "--median", "99"])
    out = capsys.readouterr().out
    assert code == 0
    for tier in TIERS:
        assert f"Referenzpfade Tier {tier}" in out
    assert "Keine Kandidaten" in out


def test_cli_writes_one_file_per_tier(mini, medians, tmp_path, capsys):
    code = main(["referenzpfade", "--config", str(MINI), "--out", str(tmp_path)])
    capsys.readouterr()
    assert code == 0
    for tier in TIERS:
        text = (tmp_path / f"referenzpfade_{tier}.txt").read_text(encoding="utf-8")
        assert f"Referenzpfade Tier {tier}" in text
        assert f"Median {medians[tier]}" in text


def test_cli_rejects_an_unknown_tier():
    with pytest.raises(SystemExit):
        main(["referenzpfade", "--config", str(MINI), "--tier", "nope"])


def test_reference_path_converts_the_config_block(mini):
    block = {
        "start": {"M1": 2, "M2": 1, "M4": 0, "M6": 0},
        "windows": [
            {"selection": {"M1": 2, "M2": 0, "M4": 1, "M6": 0}, "swap": ["M2", "M4"]},
            {"selection": {"M1": 1, "M2": 0, "M4": 1, "M6": 0}},
        ],
    }
    cfg = dataclasses.replace(mini, reference_plans={"medium": block})
    path = refpaths.reference_path(cfg, "medium")
    assert path == Path(
        {"M1": 2, "M2": 1, "M4": 0, "M6": 0},
        (
            Window({"M1": 2, "M2": 0, "M4": 1, "M6": 0}, ("M2", "M4")),
            Window({"M1": 1, "M2": 0, "M4": 1, "M6": 0}, None),
        ),
    )
    assert isinstance(path.windows[0].swap, tuple)
    rules.evaluate_path(cfg, "medium", path)  # legal
    with pytest.raises(KeyError):
        refpaths.reference_path(mini, "medium")  # no block in the mini config


def test_path_error_stays_the_rules_error(mini):
    """The finder never relaxes legality: a path without its swap is still refused by the rules."""
    start = {"M1": 1, "M2": 0, "M4": 0, "M6": 0}
    with pytest.raises(PathError):
        rules.evaluate_path(mini, "medium", Path(start))
