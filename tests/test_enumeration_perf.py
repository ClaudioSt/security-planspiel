"""Measured bounds of the full enumeration per tier (FOUND-06; D-17, D-30; T-01-20).

Machine of the measurement: Windows 11, 48 GB, uv CPython 3.12. Slow: run with `uv run pytest -m slow -s`.
"""
import json
import re
import subprocess
import sys
import time

import pytest

from planspiel.enumerate import ResultStore
from tests.support import CONFIG_PATH, REPO_ROOT

TIERS = ("low", "medium", "high")
MAX_SECONDS_PER_TIER = 120
MAX_PEAK_BYTES = 500 * 1024 * 1024
MAX_BYTES_PER_RECORD = 32

CHILD = """
import sys
import time

from planspiel.simulate import main
from tests.support.peak_memory import peak_rss_bytes

config, tier, summary, dump = sys.argv[1:5]
argv = ["--config", config, "--budget-tier", tier, "--summary", summary]
if dump != "-":
    argv += ["--dump-jsonl", dump]
started = time.perf_counter()
rc = main(argv)
seconds = time.perf_counter() - started
print(f"PERF tier={tier} seconds={seconds:.1f} peak_mb={peak_rss_bytes() / 2**20:.0f} rc={rc}")
"""

PERF_LINE = re.compile(r"PERF tier=(\w+) seconds=([\d.]+) peak_mb=(\d+) rc=(\d+)")


def _golden(tier):
    return json.loads((REPO_ROOT / "tests" / "golden" / f"digest_{tier}.json").read_text(encoding="utf-8"))


def _run_child(tier, summary_path, dump_path):
    started = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "-c", CHILD, str(CONFIG_PATH), tier, str(summary_path), dump_path],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    wall = time.perf_counter() - started
    stdout = result.stdout.decode("utf-8", errors="replace")
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    match = PERF_LINE.search(stdout)
    assert match, stdout[-500:]
    peak_bytes = int(match.group(3)) * 1024 * 1024
    print(f"PERF tier={tier} wall_seconds={wall:.1f} child_seconds={match.group(2)} peak_mb={match.group(3)}")
    return wall, peak_bytes


def test_store_record_is_within_the_byte_bound():
    assert ResultStore(620).bytes_per_record <= MAX_BYTES_PER_RECORD


@pytest.mark.slow
@pytest.mark.parametrize("tier", TIERS)
def test_summary_run_stays_within_the_measured_bounds(tier, tmp_path):
    summary_path = tmp_path / f"summary_{tier}.json"
    wall, peak_bytes = _run_child(tier, summary_path, "-")
    assert wall <= MAX_SECONDS_PER_TIER
    assert peak_bytes <= MAX_PEAK_BYTES

    golden = _golden(tier)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    combinations = summary["combinations"]
    assert combinations["valid"] == golden["count"]
    assert combinations["in_budget"] == golden["in_budget"]
    assert combinations["in_budget"] + combinations["over_budget"] == combinations["valid"]
    assert [len(summary["top"][key]) for key in ("kz_final", "ros", "final_index")] == [10, 10, 10]
    assert summary["pareto"]["count"] == len(summary["pareto"]["points"])
    assert list(tmp_path.iterdir()) == [summary_path]
    assert not list(REPO_ROOT.glob("simulation_full*.jsonl"))


@pytest.mark.slow
def test_dump_at_scale_streams_within_the_memory_bound(tmp_path):
    summary_path = tmp_path / "summary_low.json"
    dump_path = tmp_path / "dump_low.jsonl"
    _, peak_bytes = _run_child("low", summary_path, str(dump_path))
    assert peak_bytes <= MAX_PEAK_BYTES

    golden = _golden("low")
    lines = over = 0
    with open(dump_path, encoding="utf-8") as handle:
        for line in handle:
            lines += 1
            if '"over_budget":true' in line:
                over += 1
    assert lines == golden["count"] == 782336
    assert over == golden["over_budget"]
