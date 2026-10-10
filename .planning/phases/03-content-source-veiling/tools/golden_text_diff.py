"""Text-only classifier for the characterization golden change of plan 03-01 (D-08).

Rebuilds every golden case in memory exactly like `test_golden_sample_matches`, compares it with the file on
disk field by field and classifies every differing path. Only three patterns are allowed to differ:

- `wave_name`: waves[i].wave_name disappears (the wave name left the config),
- `bonus_descriptions`: waves[i].bonus_descriptions (and its elements) disappear,
- `sparprogramm_label`: the effect_description of the Sparprogramm event becomes the label generated from the
  config's `budget_delta`.

Everything else has to be identical (`_same`). Any other difference counts as "unexpected" and the exit code is 1.
If unexpected > 0, fix the code, never widen the allowed patterns.

Run from the repository root: `uv run python .planning/phases/03-content-source-veiling/tools/golden_text_diff.py`.
It imports `tests.support`, so the repository root is put at the front of `sys.path`.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tests.support import harness  # noqa: E402
from tests.support.golden import MISSING, _same, flatten, normalize  # noqa: E402

TIERS = ("low", "medium", "high")
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"

WAVE_NAME = re.compile(r"^waves\[(\d+)\]\.wave_name$")
BONUS_DESCRIPTIONS = re.compile(r"^waves\[(\d+)\]\.bonus_descriptions(\[\d+\])?$")
EFFECT_DESCRIPTION = re.compile(r"^waves\[(\d+)\]\.events\[(\d+)\]\.effect_description$")
PATTERNS = ("wave_name", "bonus_descriptions", "sparprogramm_label")


def sparprogramm_label(cfg):
    for wave_events in cfg.events.values():
        for event in wave_events:
            if event.id == "sparprogramm":
                return f"Gesamtbudget {event.params['budget_delta']}k€"
    raise SystemExit("Sparprogramm event not found in the config")


def rebuild(cfg, tier, disk):
    cases = []
    for case in disk["cases"]:
        record = harness.evaluate(cfg, tier, harness.selection_of(cfg, case["code"]))
        entry = {"code": case["code"], "tags": case["tags"], "valid": record["valid"]}
        if record["valid"]:
            entry["expected"] = normalize({k: v for k, v in record.items() if k != "valid"})
        cases.append(entry)
    return {
        "format": 1,
        "tier": tier,
        "stage": harness.STAGE,
        "meta": disk["meta"],
        "cases": cases,
    }


def classify(path, old_flat, new_flat, label):
    """Return the allowed pattern name for a differing path, or None if the difference is unexpected."""
    old = old_flat.get(path, MISSING)
    new = new_flat.get(path, MISSING)
    if WAVE_NAME.match(path):
        return "wave_name" if old is not MISSING and new is MISSING else None
    if BONUS_DESCRIPTIONS.match(path):
        return "bonus_descriptions" if old is not MISSING and new is MISSING else None
    match = EFFECT_DESCRIPTION.match(path)
    if match and old is not MISSING and new is not MISSING:
        sibling = f"waves[{match.group(1)}].events[{match.group(2)}].id"
        if old_flat.get(sibling) == "sparprogramm" and new_flat.get(sibling) == "sparprogramm" and new == label:
            return "sparprogramm_label"
    return None


def check_tier(cfg, tier, label):
    path = GOLDEN_DIR / f"characterization_{tier}.json"
    disk = json.loads(path.read_text(encoding="utf-8"))
    memory = rebuild(cfg, tier, disk)
    counts = {name: 0 for name in PATTERNS}
    unexpected = []

    head_disk = {k: v for k, v in disk.items() if k != "cases"}
    head_memory = {k: v for k, v in memory.items() if k != "cases"}
    if not _same(head_disk, head_memory):
        unexpected.append("document header differs")
    if [c["code"] for c in disk["cases"]] != [c["code"] for c in memory["cases"]]:
        unexpected.append("case codes differ")

    valid_cases = 0
    for old_case, new_case in zip(disk["cases"], memory["cases"]):
        if old_case["tags"] != new_case["tags"] or old_case["valid"] != new_case["valid"]:
            unexpected.append(f"{old_case['code']}: tags or valid flag differ")
            continue
        if not old_case["valid"]:
            continue
        valid_cases += 1
        old_flat = flatten(old_case["expected"])
        new_flat = flatten(new_case["expected"])
        for field in list(old_flat) + [p for p in new_flat if p not in old_flat]:
            old = old_flat.get(field, MISSING)
            new = new_flat.get(field, MISSING)
            if old is not MISSING and new is not MISSING and _same(old, new):
                continue
            pattern = classify(field, old_flat, new_flat, label)
            if pattern is None:
                unexpected.append(f"{tier} {old_case['code']} | {field} | {old!r} -> {new!r}")
            else:
                counts[pattern] += 1

    identical = _same(disk, memory)
    print(f"== {tier} ==")
    print(f"valid cases: {valid_cases} of {len(disk['cases'])}")
    for name in PATTERNS:
        print(f"{name}: {counts[name]}")
    print(f"unexpected: {len(unexpected)}")
    for line in unexpected[:30]:
        print(f"  {line}")
    if identical:
        print("differences: 0")
    print()
    return len(unexpected)


def main():
    parser = argparse.ArgumentParser(description="Text-only classifier for the characterization goldens (D-08).")
    parser.add_argument("--tier", action="append", choices=TIERS, help="Tier (repeatable, default: all).")
    args = parser.parse_args()
    cfg = harness.load_config()
    label = sparprogramm_label(cfg)
    print(f"generated Sparprogramm label: {label}")
    print()
    total = sum(check_tier(cfg, tier, label) for tier in (args.tier or TIERS))
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
