"""The final-index weights live in config and every caller reads them (PRINT-10 part 1, D-23, T-05-45).

With the weights 1 and 1 every output stays identical: the digests below were taken from a run before the move.
"""
import contextlib
import copy
import dataclasses
import hashlib
import io
import json
from fractions import Fraction

import pytest

from planspiel import analyze, balance, rules
from planspiel.config import FinalIndexWeights, load_config
from planspiel.enumerate import enumerate_tier
from planspiel.report import dump_record, summarize_tier
from planspiel.validate import validate
from tests.support import CONFIG_PATH, REPO_ROOT, harness

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
ONE = FinalIndexWeights(Fraction(1), Fraction(1))

# sha256 of json.dumps(summarize_tier(mini, tier, ..., top_k=1000), sort_keys=True, ensure_ascii=False), before the move
MINI_SUMMARY_DIGESTS = {
    "low": "0790ec3478565acf1e638daccd05f6c5e753373bc4b7bf605ad84f7840dd2db7",
    "medium": "8c7325f49a96337295af572be7f2e466e91bd4701d1556ca9ba4990f88561539",
    "high": "d6519d67d2a819d21c07fec8d449642875898c6e444465d931a9973a7a52d31c",
}
ANALYZE_DIGEST = "9c30f423ab84cf3a06963b14de9a997b35bcf225ca7792f4fe8f5d1ee5707330"
ANALYZE_NO_ROS_DIGEST = "77f92af7a564b79ef2974ea85e0c379eaef4c369e8a6a226ea01122b1ab8b025"
BALANCE_DIGEST = "d3af3a547e68b0d3fa7a90661173a38eb60e1f17104f9f712998329482c7d0ae"

RESULTS = {
    "results": [
        {"kz_final": 70, "total_damage": 40, "costs": {"security_spend": 100, "total": 110, "event_opex": 10}, "selection": {"M1": 1, "M2": 2}},
        {"kz_final": 55, "total_damage": 10, "costs": {"security_spend": 50, "total": 50, "event_opex": 0}, "selection": {"M1": 0, "M2": 3}},
        {"kz_final": 90, "total_damage": 200, "costs": {"security_spend": 300, "total": 300, "event_opex": 0}, "selection": {"M1": 3, "M2": 3}},
    ]
}


def _digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _captured(function, *args):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        function(*args)
    return buffer.getvalue()


def _write_config(tmp_path, source, weights, name="weighted.json"):
    raw = json.loads(source.read_text(encoding="utf-8"))
    raw["final_index"] = weights
    target = tmp_path / name
    target.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    return target


@pytest.fixture(scope="module")
def mini():
    return harness.load_config(MINI)


# --- config ---------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("path", [CONFIG_PATH, MINI], ids=["real", "mini"])
def test_both_configs_carry_the_weights_one_and_one(path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["final_index"] == {"weight_kz": 1, "weight_ros": 1}
    assert load_config(path).final_index == ONE


def test_final_index_precedes_practice_in_the_config_fields():
    names = [field.name for field in dataclasses.fields(load_config(MINI).__class__)]
    assert names.index("final_index") < names.index("practice")
    assert names[-1] == "practice"


# --- validator -------------------------------------------------------------------------------------------------


def _issues(mutate):
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    mutate(raw)
    return [issue for issue in validate(raw) if issue.level == "error"]


def _delete_block(raw):
    del raw["final_index"]


def _delete_key(raw):
    del raw["final_index"]["weight_ros"]


def _negative(raw):
    raw["final_index"]["weight_kz"] = -1


def _both_zero(raw):
    raw["final_index"] = {"weight_kz": 0, "weight_ros": 0}


def _not_a_number(raw):
    raw["final_index"]["weight_ros"] = "viel"


def _not_an_object(raw):
    raw["final_index"] = [1, 1]


@pytest.mark.parametrize(
    ("mutate", "code", "path_fragment"),
    [
        (_delete_block, "schema.top_level", "final_index"),
        (_delete_key, "schema.keys", "final_index.weight_ros"),
        (_negative, "schema.range", "final_index.weight_kz"),
        (_both_zero, "schema.range", "final_index"),
        (_not_a_number, "schema.type", "final_index.weight_ros"),
        (_not_an_object, "schema.type", "final_index"),
    ],
    ids=["missing-block", "missing-key", "negative", "both-zero", "not-a-number", "not-an-object"],
)
def test_broken_weights_are_validator_errors(mutate, code, path_fragment):
    errors = _issues(mutate)
    assert any(issue.code == code and issue.path.startswith(path_fragment) for issue in errors), errors


def test_a_one_sided_zero_weight_is_allowed():
    assert _issues(lambda raw: raw["final_index"].update(weight_kz=0)) == []


# --- rules.final_index has no defaults -------------------------------------------------------------------------


def test_final_index_requires_both_weights():
    with pytest.raises(TypeError):
        rules.final_index(80, Fraction(1, 2))
    with pytest.raises(TypeError):
        rules.final_index(80, None)
    assert rules.final_index(80, Fraction(1, 2), Fraction(1), Fraction(1)) == 130


# --- every caller reads the config -----------------------------------------------------------------------------


def _weighted(mini, kz, ros):
    return dataclasses.replace(mini, final_index=FinalIndexWeights(Fraction(kz), Fraction(ros)))


def test_summary_final_index_follows_the_config_weights(mini):
    plain = summarize_tier(mini, "low", enumerate_tier(mini, "low"), top_k=1000)
    heavy = summarize_tier(_weighted(mini, 2, 1), "low", enumerate_tier(mini, "low"), top_k=1000)
    plain_by_code = {entry["code"]: entry for entry in plain["top"]["final_index"]}
    heavy_by_code = {entry["code"]: entry for entry in heavy["top"]["final_index"]}
    assert plain_by_code and plain_by_code.keys() == heavy_by_code.keys()
    changed = 0
    for code, entry in heavy_by_code.items():
        base = plain_by_code[code]
        assert entry["kz_final"] == base["kz_final"] and entry["ros"] == base["ros"]
        expected = Fraction(2 * entry["kz_final"])
        if entry["ros"] is not None:
            expected += Fraction(str(entry["ros"])) * 100
        assert Fraction(str(entry["final_index"])) == expected
        changed += entry["final_index"] != base["final_index"]
    assert changed > 0


def test_dump_record_takes_the_weights(mini):
    outcome = rules.CompactOutcome(
        kz_final=70, own_cost=100, total_cost=104, damage_eur=5000, event_opex=4,
        event_budget=0, over_budget=False, kz_after=(70, 70, 70), kz_pre_review=70, remaining=0,
    )
    base = rules.base_losses(mini.waves, mini.attacks)
    one = dump_record(mini.measure_ids, 5, outcome, base, ONE)
    two = dump_record(mini.measure_ids, 5, outcome, base, FinalIndexWeights(Fraction(2), Fraction(1)))
    assert one["final_index"] != two["final_index"]
    assert one["ros"] == two["ros"]
    with pytest.raises(TypeError):
        dump_record(mini.measure_ids, 5, outcome, base)


def test_balance_reads_the_config_weights(tmp_path):
    plain = _captured(balance.run_analysis, MINI)
    heavy = _captured(balance.run_analysis, _write_config(tmp_path, MINI, {"weight_kz": 2, "weight_ros": 1}))
    assert plain != heavy


def test_analyze_resolves_weights_from_the_given_config(tmp_path, capsys):
    results = tmp_path / "results.json"
    results.write_text(json.dumps(RESULTS), encoding="utf-8")
    heavy = _write_config(tmp_path, MINI, {"weight_kz": 2, "weight_ros": 1})

    analyze.main(["--input", str(results), "--config", str(MINI)])
    plain_out = capsys.readouterr().out
    analyze.main(["--input", str(results), "--config", str(heavy)])
    heavy_out = capsys.readouterr().out
    assert plain_out != heavy_out

    analyze.main(["--input", str(results), "--config", str(heavy), "--weight-kz", "1", "--weight-ros", "1"])
    assert capsys.readouterr().out == plain_out


def test_analyze_without_config_uses_the_repository_config(tmp_path, capsys, monkeypatch):
    results = tmp_path / "results.json"
    results.write_text(json.dumps(RESULTS), encoding="utf-8")

    analyze.main(["--input", str(results)])
    plain_out = capsys.readouterr().out
    assert "Final-Index: min 55,00, max 90,00" in plain_out

    monkeypatch.setattr(analyze, "DEFAULT_CONFIG_PATH", _write_config(tmp_path, CONFIG_PATH, {"weight_kz": 2, "weight_ros": 1}))
    analyze.main(["--input", str(results)])
    assert "Final-Index: min 110,00, max 180,00" in capsys.readouterr().out

    analyze.main(["--input", str(results), "--weight-kz", "3"])
    assert "Final-Index: min 165,00, max 270,00" in capsys.readouterr().out


def test_analyze_weight_flags_default_to_none():
    args = analyze.parse_args([])
    assert args.weight_kz is None and args.weight_ros is None
    args = analyze.parse_args(["--weight-kz", "2", "--weight-ros", "1/2"])
    assert (args.weight_kz, args.weight_ros) == (Fraction(2), Fraction(1, 2))


# --- outputs unchanged at 1 and 1 -------------------------------------------------------------------------------


@pytest.mark.parametrize("tier", ["low", "medium", "high"])
def test_mini_summary_is_unchanged(mini, tier):
    summary = summarize_tier(mini, tier, enumerate_tier(mini, tier), top_k=1000)
    assert _digest(json.dumps(summary, sort_keys=True, ensure_ascii=False)) == MINI_SUMMARY_DIGESTS[tier]


def test_analyze_output_is_unchanged():
    assert _digest(_captured(analyze.compute_summary, RESULTS, 2, 620, Fraction(1), Fraction(1))) == ANALYZE_DIGEST
    assert _digest(_captured(analyze.compute_summary, RESULTS, 2, None, Fraction(1), Fraction(1))) == ANALYZE_NO_ROS_DIGEST


def test_balance_output_is_unchanged():
    assert _digest(_captured(balance.run_analysis)) == BALANCE_DIGEST
