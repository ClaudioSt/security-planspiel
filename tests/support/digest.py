"""Full-enumeration digest over the canonical outputs of all dependency-valid combinations (D-08)."""
import hashlib
from fractions import Fraction

from planspiel.rounding import exact_to_json
from tests.support import harness


def canon(value) -> str:
    if isinstance(value, bool):
        return "1" if value else "0"
    if value is None:
        return "-"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Fraction):
        return str(exact_to_json(value))
    if isinstance(value, float):
        return repr(value)
    raise TypeError(f"cannot canonicalize {type(value).__name__}")


def canonical_line(code: str, record: dict) -> str:
    kz_after = ",".join(canon(wave["kz_after"]) for wave in record["waves"])
    fields = [
        code,
        canon(record["kz_final"]),
        canon(record["total_damage"]),
        canon(record["costs"]["total"]),
        canon(record["total_event_opex"]),
        canon(record["total_event_budget"]),
        kz_after,
        canon(record["over_budget"]),
    ]
    return "|".join(fields)


def compute_digest(cfg, tier_name: str, limit: int | None = None, evaluate=None) -> dict:
    evaluate = evaluate or harness.evaluate
    sha = hashlib.sha256()
    count = in_budget = over_budget = 0
    histogram = [0] * 101
    sum_damage = 0

    for code in harness.iter_codes(cfg):
        record = evaluate(cfg, tier_name, harness.selection_of(cfg, code))
        if not record["valid"]:
            continue
        sha.update((canonical_line(code, record) + "\n").encode("utf-8"))
        count += 1
        if record["over_budget"]:
            over_budget += 1
        else:
            in_budget += 1
        histogram[record["kz_final"]] += 1
        sum_damage += record["total_damage"]
        if limit is not None and count >= limit:
            break

    return {
        "format": 1,
        "tier": tier_name,
        "stage": harness.STAGE,
        "count": count,
        "in_budget": in_budget,
        "over_budget": over_budget,
        "kz_histogram": histogram,
        "sum_damage": canon(sum_damage),
        "digest": sha.hexdigest(),
    }
