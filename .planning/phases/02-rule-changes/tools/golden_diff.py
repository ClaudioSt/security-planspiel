"""All-combination golden diff for Phase-2 rule changes (D-20).

`dump --label L --tier T` enumerates every dependency-valid combination of a config with the fast kernel
and writes compact per-combination columns (array.tofile, gitignored). `report --pre A --post B` compares
two dumps and writes a Markdown report for the human review before goldens are regenerated.
Imports only the installed `planspiel` package, never `tests`.
"""
import argparse
import json
import time
from array import array
from fractions import Fraction
from pathlib import Path

from planspiel import rules
from planspiel.config import load_config
from planspiel.enumerate import code_from_index, enumerate_tier

PHASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
CONFIG_PATH = REPO_ROOT / "simulation_config.json"
DEFAULT_DIR = PHASE_DIR / "golden-diff"

COLUMN_TYPES = {
    "code": "I",
    "kz_final": "B",
    "own_cost": "H",
    "total_cost": "i",
    "damage_eur": "I",
    "over_budget": "B",
    "remaining": "i",
    "ros_num": "q",
    "ros_den": "q",
}

EXPECTED = {
    "02-01": {
        "kz_changed": {"low": 512_006, "medium": 648_246, "high": 739_828},
        "in_budget_pre": {"low": 69_454, "medium": 124_321, "high": 197_753},
        "in_budget_post": {"low": 69_454, "medium": 124_321, "high": 197_753},
        "best_in_budget": {"low": "100 -> 98", "medium": "100 -> 100", "high": "100 -> 100"},
        "best_over_budget": {"low": "85 -> 85", "medium": "85 -> 85", "high": "85 -> 85"},
        "mean_shift": {"low": "-8.84", "medium": "-12.84", "high": "-16.56"},
        "flips": 0,
        "ros_changed": 0,
        "damage_changed": 0,
    },
    "02-02": {
        "kz_changed": 0,
        "in_budget_pre": {"low": 69_454, "medium": 124_321, "high": 197_753},
        "in_budget_post": {"low": 69_454, "medium": 124_321, "high": 197_753},
        "flips": 0,
        "ros_changed": 779_900,
        "max_ros": "0.1206",
        "best_ros": "0002012210 (1.581) -> 0002022200 (1.494)",
        "ros_overlap": "93 / 100",
        "damage_changed": 0,
    },
}


def column_types(wave_count):
    types = dict(COLUMN_TYPES)
    for w in range(wave_count):
        types[f"kz_after_{w + 1}"] = "B"
    return types


def dump(label, tier, config_path, out_dir):
    cfg = load_config(config_path)
    wave_count = len(cfg.waves)
    types = column_types(wave_count)
    columns = {name: array(typecode) for name, typecode in types.items()}
    tier_cfg = cfg.budget_tiers[tier]
    started = time.time()

    def collect(code_index, outcome):
        ledger = rules.budget_ledger(tier_cfg.budget, outcome.own_cost, outcome.event_opex, outcome.event_budget)
        columns["remaining"].append(ledger.remaining_budget)
        for w in range(wave_count):
            columns[f"kz_after_{w + 1}"].append(outcome.kz_after[w])

    store = enumerate_tier(cfg, tier, on_outcome=collect)
    for name in ("code_index", "kz_final", "own_cost", "total_cost", "damage_eur", "over_budget"):
        target_name = "code" if name == "code_index" else name
        columns[target_name].extend(store.column(name))
    for i in range(len(store)):
        ros = store.record(i).ros
        columns["ros_num"].append(0 if ros is None else ros.numerator)
        columns["ros_den"].append(0 if ros is None else ros.denominator)

    target = out_dir / label / tier
    target.mkdir(parents=True, exist_ok=True)
    for name, column in columns.items():
        with open(target / f"{name}.bin", "wb") as handle:
            column.tofile(handle)
    meta = {
        "label": label,
        "tier": tier,
        "count": len(store),
        "wave_count": wave_count,
        "columns": types,
        "n_measures": len(cfg.measure_ids),
        "seconds": round(time.time() - started, 1),
    }
    (target / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"{label} {tier}: {meta['count']} combinations in {meta['seconds']} s")


def load_columns(out_dir, label, tier):
    target = out_dir / label / tier
    meta = json.loads((target / "meta.json").read_text(encoding="utf-8"))
    columns = {}
    for name, typecode in meta["columns"].items():
        column = array(typecode)
        with open(target / f"{name}.bin", "rb") as handle:
            column.fromfile(handle, meta["count"])
        columns[name] = column
    return columns, meta


def ros_value(columns, i):
    den = columns["ros_den"][i]
    return None if den == 0 else Fraction(columns["ros_num"][i], den)


def best_plan(columns, indices):
    best = None
    for i in indices:
        key = (-columns["kz_final"][i], columns["own_cost"][i], columns["code"][i])
        if best is None or key < best[0]:
            best = (key, i)
    return None if best is None else best[1]


def describe_best(columns, i, n_measures):
    if i is None:
        return "-"
    code = code_from_index(columns["code"][i], n_measures)
    return f"KZ {columns['kz_final'][i]}, {code}, own cost {columns['own_cost'][i]}"


def codes_text(codes, n_measures, limit=10):
    return ", ".join(code_from_index(c, n_measures) for c in codes[:limit]) or "-"


def pairs_text(items, n_measures, fmt, limit=10):
    return "; ".join(f"{code_from_index(code, n_measures)}: {fmt(old)} -> {fmt(new)}" for code, old, new in items[:limit]) or "-"


def top_ros_codes(columns, count, limit=100):
    scored = []
    for i in range(count):
        value = ros_value(columns, i)
        if value is not None:
            scored.append((-value, columns["code"][i]))
    scored.sort()
    return [code for _, code in scored[:limit]]


def tier_section(out_dir, pre_label, post_label, tier, plan):
    pre, meta = load_columns(out_dir, pre_label, tier)
    post, post_meta = load_columns(out_dir, post_label, tier)
    if meta["count"] != post_meta["count"] or pre["code"] != post["code"]:
        raise SystemExit(f"{tier}: pre and post dumps enumerate different combinations")
    count = meta["count"]
    n_measures = meta["n_measures"]
    wave_count = meta["wave_count"]
    expected = EXPECTED.get(plan, {})

    def exp(key, default="-"):
        value = expected.get(key)
        if value is None:
            return default
        return value.get(tier, default) if isinstance(value, dict) else value

    kz_changed, kz_changed_pre_in, kz_changed_pre_over = [], 0, 0
    shift_sum = 0
    zero_all = zero_over = 0
    over_flips, flip_codes = 0, []
    ros_changed, max_ros = [], (Fraction(0), None)
    damage_changed, own_changed, total_changed, remaining_changed = [], 0, 0, 0
    in_pre = in_post = 0
    wave_changed = [0] * wave_count

    for i in range(count):
        code = pre["code"][i]
        old_kz, new_kz = pre["kz_final"][i], post["kz_final"][i]
        pre_over, post_over = pre["over_budget"][i], post["over_budget"][i]
        in_pre += 1 - pre_over
        in_post += 1 - post_over
        if pre_over != post_over:
            over_flips += 1
            flip_codes.append(code)
        shift_sum += new_kz - old_kz
        if new_kz == 0:
            zero_all += 1
            if post_over:
                zero_over += 1
        if old_kz != new_kz:
            kz_changed.append((code, old_kz, new_kz))
            if pre_over:
                kz_changed_pre_over += 1
            else:
                kz_changed_pre_in += 1
        for w in range(wave_count):
            if pre[f"kz_after_{w + 1}"][i] != post[f"kz_after_{w + 1}"][i]:
                wave_changed[w] += 1
        if pre["ros_num"][i] != post["ros_num"][i] or pre["ros_den"][i] != post["ros_den"][i]:
            old_ros, new_ros = ros_value(pre, i), ros_value(post, i)
            if old_ros != new_ros:
                ros_changed.append((code, old_ros, new_ros))
                if old_ros is not None and new_ros is not None and abs(new_ros - old_ros) > max_ros[0]:
                    max_ros = (abs(new_ros - old_ros), code)
        if pre["damage_eur"][i] != post["damage_eur"][i]:
            damage_changed.append((code, pre["damage_eur"][i], post["damage_eur"][i]))
        own_changed += pre["own_cost"][i] != post["own_cost"][i]
        total_changed += pre["total_cost"][i] != post["total_cost"][i]
        remaining_changed += pre["remaining"][i] != post["remaining"][i]

    in_idx_pre = [i for i in range(count) if not pre["over_budget"][i]]
    over_idx_pre = [i for i in range(count) if pre["over_budget"][i]]
    in_idx_post = [i for i in range(count) if not post["over_budget"][i]]
    over_idx_post = [i for i in range(count) if post["over_budget"][i]]
    best_in_pre, best_in_post = best_plan(pre, in_idx_pre), best_plan(post, in_idx_post)
    best_over_pre, best_over_post = best_plan(pre, over_idx_pre), best_plan(post, over_idx_post)

    def kz_of(columns, i):
        return "-" if i is None else columns["kz_final"][i]

    best_ros_pre = max(((ros_value(pre, i), -pre["code"][i]) for i in range(count) if ros_value(pre, i) is not None), default=None)
    best_ros_post = max(((ros_value(post, i), -post["code"][i]) for i in range(count) if ros_value(post, i) is not None), default=None)

    def ros_text(entry):
        if entry is None:
            return "-"
        value, neg_code = entry
        return f"{code_from_index(-neg_code, n_measures)} ({float(value):.3f})"

    overlap = len(set(top_ros_codes(pre, count)) & set(top_ros_codes(post, count)))
    mean_shift = Fraction(shift_sum, count)
    max_ros_text = "0.0000" if max_ros[1] is None else f"{float(max_ros[0]):.4f} ({code_from_index(max_ros[1], n_measures)})"

    lines = [
        f"## Tier {tier}",
        "",
        f"Combinations compared: {count}",
        "",
        "| Kennzahl | vorher | nachher | erwartet (Research) |",
        "|---|---|---|---|",
        f"| combinations | {count} | {count} | {count} |",
        f"| in-budget count | {in_pre} | {in_post} | {exp('in_budget_pre')} / {exp('in_budget_post')} |",
        f"| over-budget flips | - | {over_flips} | {exp('flips')} |",
        f"| KZ changed (all) | - | {len(kz_changed)} | {exp('kz_changed')} |",
        f"| KZ changed (pre in-budget) | - | {kz_changed_pre_in} | - |",
        f"| KZ changed (pre over-budget) | - | {kz_changed_pre_over} | - |",
        f"| mean KZ shift | - | {float(mean_shift):.2f} | {exp('mean_shift')} |",
        f"| KZ = 0 (all) | - | {zero_all} | - |",
        f"| KZ = 0 (over-budget) | - | {zero_over} | - |",
        f"| best in-budget KZ | {kz_of(pre, best_in_pre)} | {kz_of(post, best_in_post)} | {exp('best_in_budget')} |",
        f"| best over-budget KZ | {kz_of(pre, best_over_pre)} | {kz_of(post, best_over_post)} | {exp('best_over_budget')} |",
        f"| best in-budget plan | {describe_best(pre, best_in_pre, n_measures)} | {describe_best(post, best_in_post, n_measures)} | - |",
        f"| best over-budget plan | {describe_best(pre, best_over_pre, n_measures)} | {describe_best(post, best_over_post, n_measures)} | - |",
        f"| RoS changed | - | {len(ros_changed)} | {exp('ros_changed')} |",
        f"| max abs RoS change | - | {max_ros_text} | {exp('max_ros')} |",
        f"| best-RoS plan | {ros_text(best_ros_pre)} | {ros_text(best_ros_post)} | {exp('best_ros')} |",
        f"| top-100 RoS overlap | - | {overlap} / 100 | {exp('ros_overlap')} |",
        f"| damage changed | - | {len(damage_changed)} | {exp('damage_changed')} |",
        f"| own cost changed | - | {own_changed} | 0 |",
        f"| budget total changed | - | {total_changed} | 0 |",
        f"| remaining budget changed | - | {remaining_changed} | 0 |",
    ]
    for w in range(wave_count):
        lines.append(f"| kz_after wave {w + 1} changed | - | {wave_changed[w]} | - |")
    lines += [
        "",
        "Example codes per changed metric (up to 10, `code: old -> new`):",
        "",
        f"- KZ: {pairs_text(kz_changed, n_measures, str)}",
        f"- RoS: {pairs_text(ros_changed, n_measures, lambda v: 'None' if v is None else f'{float(v):.4f}')}",
        f"- damage: {pairs_text(damage_changed, n_measures, str)}",
        f"- over-budget flips: {codes_text(flip_codes, n_measures)}",
        "",
    ]
    return lines


def report(out_dir, pre_label, post_label, tiers, out_path, plan):
    lines = [
        f"# Golden diff {pre_label} -> {post_label}",
        "",
        "Generated by `.planning/phases/02-rule-changes/tools/golden_diff.py report`.",
        "All dependency-valid combinations per tier are compared before/after the rule change.",
        "",
    ]
    for tier in tiers:
        lines += tier_section(out_dir, pre_label, post_label, tier, plan)
    out_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"wrote {out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    dump_parser = sub.add_parser("dump")
    dump_parser.add_argument("--label", required=True)
    dump_parser.add_argument("--tier", required=True)
    dump_parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    dump_parser.add_argument("--out-dir", type=Path, default=DEFAULT_DIR)

    report_parser = sub.add_parser("report")
    report_parser.add_argument("--pre", required=True)
    report_parser.add_argument("--post", required=True)
    report_parser.add_argument("--tiers", nargs="+", required=True)
    report_parser.add_argument("--out", type=Path, required=True)
    report_parser.add_argument("--plan")
    report_parser.add_argument("--out-dir", type=Path, default=DEFAULT_DIR)

    args = parser.parse_args()
    if args.command == "dump":
        dump(args.label, args.tier, args.config, args.out_dir)
    else:
        report(args.out_dir, args.pre, args.post, args.tiers, args.out, args.plan)


if __name__ == "__main__":
    main()
