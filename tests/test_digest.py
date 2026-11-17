import copy
import json

import pytest

from tests.support import CONFIG_PATH, REPO_ROOT, harness
from tests.support.digest import compute_digest
from tests.support.golden import check_golden

TIERS = ("low", "medium", "high")


@pytest.mark.slow
@pytest.mark.parametrize("tier", TIERS)
def test_full_digest_matches(tier, update_golden, golden_report):
    cfg = harness.load_config()
    path = REPO_ROOT / "tests" / "golden" / f"digest_{tier}.json"
    check_golden(path, compute_digest(cfg, tier), update_golden, golden_report)


def test_digest_is_deterministic_and_sensitive(tmp_path):
    cfg = harness.load_config()
    first = compute_digest(cfg, "medium", limit=3000)
    assert first == compute_digest(cfg, "medium", limit=3000)
    assert first["count"] == 3000

    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(raw)
    mutated["attacks"]["ransomware"]["kz_at_full_damage"] -= 8
    mutated_path = tmp_path / "simulation_config.json"
    mutated_path.write_text(json.dumps(mutated, ensure_ascii=False), encoding="utf-8")
    assert compute_digest(harness.load_config(mutated_path), "medium", limit=3000)["digest"] != first["digest"]
