"""All-combination diff for the exact-arithmetic switch (plan 01-06, D-05 step 3).

`dump --stage pre|post --tier T` evaluates every dependency-valid combination of the real config and
writes compact per-combination columns (array.tofile, gitignored). `report` compares the pre (float)
and post (exact) dumps and writes a Markdown report. Imports only the installed `planspiel` package.
"""
import argparse
import itertools
import json
import time
from array import array
from pathlib import Path

from planspiel import rules
from planspiel.config import load_config

PHASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
CONFIG_PATH = REPO_ROOT / "simulation_config.json"
DEFAULT_DIR = PHASE_DIR / "exact-switch"
LEVELS = 4

EXPECTED_KZ_CHANGED = {"low": 121_306, "medium": 168_625, "high": 194_360}
EXPECTED_TIES = 1_050
NOISE_EPS = 1e-9


def column_names(wave_count):
    return (
        ["code", "kz_final", "damage_k", "cost_total"]
        + [f"kz_after_{w + 1}" for w in range(wave_count)]
        + ["w3_capped", "e_bits", "over"]
    )


def column_types(wave_count):
    types = {"code": "I", "kz_final": "d", "damage_k": "d", "cost_total": "d", "w3_capped": "d", "e_bits": "B", "over": "B"}
    for w in range(wave_count):
        types[f"kz_after_{w + 1}"] = "d"
    return types


def dump(stage, tier, out_dir):
    cfg = load_config(CONFIG_PATH)
    wave_count = len(cfg.waves)
    types = column_types(wave_count)
    columns = {name: array(types[name]) for name in column_names(wave_count)}
    measure_ids = cfg.measure_ids
    started = time.time()

    for index, levels in enumerate(itertools.product(range(LEVELS), repeat=len(measure_ids))):
        selection = dict(zip(measure_ids, levels))
        if not rules.dependencies_satisfied(selection, cfg.measures):
            continue
        record = rules.evaluate_plan(cfg, tier, selection)
        columns["code"].append(index)
        columns["kz_final"].append(float(record["kz_final"]))
        columns["damage_k"].append(float(record["total_damage"]))
        columns["cost_total"].append(float(record["costs"]["total"]))
        bits = 0
        for w, wave in enumerate(record["waves"]):
            columns[f"kz_after_{w + 1}"].append(float(wave["kz_after"]))
            bits |= int(bool(wave["e_reached"])) << w
        columns["w3_capped"].append(float(record["waves"][2]["capped_reduction"]))
        columns["e_bits"].append(bits)
        columns["over"].append(int(bool(record["over_budget"])))

    target = out_dir / stage / tier
    target.mkdir(parents=True, exist_ok=True)
    for name, column in columns.items():
        with open(target / f"{name}.bin", "wb") as handle:
            column.tofile(handle)
    meta = {
        "count": len(columns["code"]),
        "columns": types,
        "measure_ids": measure_ids,
        "seconds": round(time.time() - started, 1),
    }
    (target / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"{stage} {tier}: {meta['count']} combinations in {meta['seconds']} s")


def load_columns(out_dir, stage, tier):
    target = out_dir / stage / tier
    meta = json.loads((target / "meta.json").read_text(encoding="utf-8"))
    columns = {}
    for name, typecode in meta["columns"].items():
        column = array(typecode)
        with open(target / f"{name}.bin", "rb") as handle:
            column.fromfile(handle, meta["count"])
        columns[name] = column
    return columns, meta


def decode(index, measure_ids):
    digits = []
    for _ in measure_ids:
        digits.append(index % LEVELS)
        index //= LEVELS
    return "".join(str(d) for d in reversed(digits))


def examples(codes, measure_ids, limit=10):
    return ", ".join(decode(code, measure_ids) for code in codes[:limit]) or "-"


def tier_section(out_dir, tier):
    pre, meta = load_columns(out_dir, "pre", tier)
    post, post_meta = load_columns(out_dir, "post", tier)
    if meta["count"] != post_meta["count"] or pre["code"] != post["code"]:
        raise SystemExit(f"{tier}: pre and post dumps enumerate different combinations")
    measure_ids = meta["measure_ids"]
    count = meta["count"]

    changed, changed_integral, kz_noise = [], 0, 0
    down = up = 0
    max_shift = 0.0
    movers = []
    e_flips, over_flips, damage_changes, noise_only, ties = [], [], [], [], []
    down_codes, up_codes = [], []

    for i in range(count):
        code = pre["code"][i]
        old_kz, new_kz = pre["kz_final"][i], post["kz_final"][i]
        shift = new_kz - old_kz
        if shift != 0 and abs(shift) <= NOISE_EPS:
            kz_noise += 1
        elif shift != 0:
            changed.append(code)
            if old_kz == int(old_kz):
                changed_integral += 1
            if shift <= -0.5 + NOISE_EPS:
                down += 1
                down_codes.append(code)
            elif shift >= 0.5 - NOISE_EPS:
                up += 1
                up_codes.append(code)
            if abs(shift) > max_shift:
                max_shift = abs(shift)
            movers.append((abs(shift), code, old_kz, new_kz))
        if pre["e_bits"][i] != post["e_bits"][i]:
            e_flips.append(code)
        if pre["over"][i] != post["over"][i]:
            over_flips.append(code)
        if abs(post["damage_k"][i] - pre["damage_k"][i]) * 1000 > 0.5:
            damage_changes.append(code)
        legacy_euros = pre["damage_k"][i] * 1000
        if legacy_euros != round(legacy_euros):
            noise_only.append(code)
        if pre["w3_capped"][i] == 3.5:
            ties.append(code)

    movers.sort(key=lambda m: (-m[0], m[1]))
    expected = EXPECTED_KZ_CHANGED[tier]
    lines = [
        f"## Tier {tier}",
        "",
        f"Combinations compared: {count}",
        "",
        "| Metric | Measured | Research expectation |",
        "|---|---|---|",
        f"| Final KZ changed (abs delta > 1e-9) | {len(changed)} | {expected} |",
        f"| Final KZ differs by float noise only (0 < abs delta <= 1e-9) | {kz_noise} | not counted |",
        f"| ... of the changed, legacy KZ already integral | {changed_integral} | 0 (2 in high) |",
        f"| KZ shift >= 0.5 down | {down} | see research Q5 |",
        f"| KZ shift >= 0.5 up | {up} | see research Q5 |",
        f"| Max absolute KZ shift | {max_shift:.4f} | up to 3 x 0.5 (one rounding per wave accumulates) |",
        f"| E-target flips | {len(e_flips)} | 0 |",
        f"| Over-budget flips | {len(over_flips)} | 0 |",
        f"| Damage changes > 0.5 EUR | {len(damage_changes)} | 0 |",
        f"| Legacy damage with float noise only (non-integer euros) | {len(noise_only)} | 179084 |",
        f"| Wave-3 ties (legacy capped reduction == 3.5) | {len(ties)} | {EXPECTED_TIES} |",
        "",
        "Top 10 movers by |delta final KZ| (code, legacy, exact):",
        "",
    ]
    for shift, code, old_kz, new_kz in movers[:10]:
        lines.append(f"- {decode(code, measure_ids)}: {old_kz!r} -> {new_kz!r} (shift {shift:.4g})")
    lines += [
        "",
        "Example codes per category (up to 10):",
        "",
        f"- final KZ changed: {examples(changed, measure_ids)}",
        f"- KZ shift down >= 0.5: {examples(down_codes, measure_ids)}",
        f"- KZ shift up >= 0.5: {examples(up_codes, measure_ids)}",
        f"- E-target flips: {examples(e_flips, measure_ids)}",
        f"- over-budget flips: {examples(over_flips, measure_ids)}",
        f"- damage changes > 0.5 EUR: {examples(damage_changes, measure_ids)}",
        f"- legacy float-noise damage: {examples(noise_only, measure_ids)}",
        f"- wave-3 ties: {examples(ties, measure_ids)}",
        "",
    ]
    return lines


def report(out_dir, tiers, out_path):
    lines = [
        "# Exact-arithmetic switch: all-combination diff (float vs exact-rounded)",
        "",
        "Generated by `.planning/phases/01-simulation-foundation/tools/exact_switch_diff.py report`.",
        "Pre = legacy float arithmetic, post = exact integer-scaled arithmetic with one rounding point per wave.",
        "",
    ]
    for tier in tiers:
        lines += tier_section(out_dir, tier)
    out_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"wrote {out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    dump_parser = sub.add_parser("dump")
    dump_parser.add_argument("--stage", choices=["pre", "post"], required=True)
    dump_parser.add_argument("--tier", required=True)
    dump_parser.add_argument("--out-dir", type=Path, default=DEFAULT_DIR)

    report_parser = sub.add_parser("report")
    report_parser.add_argument("--tiers", nargs="+", required=True)
    report_parser.add_argument("--out", type=Path, required=True)
    report_parser.add_argument("--out-dir", type=Path, default=DEFAULT_DIR)

    args = parser.parse_args()
    if args.command == "dump":
        dump(args.stage, args.tier, args.out_dir)
    else:
        report(args.out_dir, args.tiers, args.out)


if __name__ == "__main__":
    main()
