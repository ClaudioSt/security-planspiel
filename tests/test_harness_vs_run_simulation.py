import json

import pytest

from planspiel import simulate
from tests.support import CONFIG_PATH, harness
from tests.support.golden import normalize


@pytest.mark.slow
def test_harness_matches_run_simulation_on_in_budget_window(tmp_path):
    cfg = harness.load_config()
    empty = {m: 0 for m in harness.measure_ids(cfg)}
    budget_available = harness.evaluate(cfg, "medium", empty)["costs"]["budget_available"]
    min_cost = budget_available - 2

    output = tmp_path / "out.json"
    summary = simulate.run_simulation(CONFIG_PATH, "medium", output, min_cost, None, 0.0)
    data = json.loads(output.read_text(encoding="utf-8"))
    results = data["results"]
    assert summary["total_outcomes"] == len(results) > 0

    expected = []
    for code in harness.iter_codes(cfg):
        record = harness.evaluate(cfg, "medium", harness.selection_of(cfg, code))
        if not record["valid"]:
            continue
        total = record["costs"]["total"]
        if total >= min_cost and total <= record["costs"]["budget_available"]:
            assert not record["over_budget"]
            expected.append((code, record))
    expected.sort(key=lambda item: (-item[1]["kz_final"], item[1]["total_damage"]))

    assert [harness.code_of(cfg, r["selection"]) for r in results] == [code for code, _ in expected]
    for result, (code, record) in zip(results, expected):
        assert result == normalize({k: record[k] for k in harness.LEGACY_RECORD_KEYS}), code
