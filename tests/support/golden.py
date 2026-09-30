"""Golden file comparison with a domain-readable diff and an explicit rewrite path."""
import json
import re
from fractions import Fraction
from pathlib import Path

import pytest

from planspiel.rounding import exact_to_json

NOISE_TOLERANCE = Fraction(1, 10**9)
MAX_SHOWN_LINES = 30
MISSING = "<missing>"

_DECIMAL = re.compile(r"^-?\d+(\.\d+)?$")
_RATIO = re.compile(r"^-?\d+/\d+$")
_INDEX = re.compile(r"\[\d+\]")


def _exactify(value):
    if isinstance(value, Fraction):
        return exact_to_json(value)
    if isinstance(value, dict):
        return {key: _exactify(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_exactify(item) for item in value]
    return value


def normalize(value):
    return json.loads(json.dumps(_exactify(value)))


def flatten(obj, prefix=""):
    if isinstance(obj, dict) and obj:
        out = {}
        for key, value in obj.items():
            out.update(flatten(value, f"{prefix}.{key}" if prefix else str(key)))
        return out
    if isinstance(obj, list) and obj:
        out = {}
        for index, value in enumerate(obj):
            out.update(flatten(value, f"{prefix}[{index}]"))
        return out
    return {prefix: obj}


def _number(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            return None
        return Fraction(value)
    if isinstance(value, str) and (_DECIMAL.match(value) or _RATIO.match(value)):
        return Fraction(value)
    return None


def _same(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return type(a) is type(b) and a == b


def _classify(old, new):
    """Return "same", "noise", "representation" or "changed" for two scalar leaves."""
    if _same(old, new):
        return "same"
    if isinstance(old, str) and isinstance(new, str):
        return "changed"
    a, b = _number(old), _number(new)
    if a is None or b is None:
        return "changed"
    delta = abs(a - b)
    if delta == 0:
        return "representation"
    if delta < NOISE_TOLERANCE:
        return "noise"
    return "changed"


def _show(value):
    return MISSING if value is MISSING else json.dumps(value, ensure_ascii=False)


def _field_name(path):
    if path.startswith("expected."):
        path = path[len("expected."):]
    return path


def _counter_name(path):
    return _INDEX.sub("[]", _field_name(path))


def _diff_leaves(prefix, old, new, lines, noise, representation):
    old_flat = flatten(old)
    new_flat = flatten(new)
    paths = list(old_flat) + [p for p in new_flat if p not in old_flat]
    for path in paths:
        old_value = old_flat.get(path, MISSING)
        new_value = new_flat.get(path, MISSING)
        if old_value is MISSING or new_value is MISSING:
            lines.append(f"{prefix} | {_field_name(path)} | {_show(old_value)} -> {_show(new_value)}")
            continue
        kind = _classify(old_value, new_value)
        if kind == "changed":
            lines.append(f"{prefix} | {_field_name(path)} | {_show(old_value)} -> {_show(new_value)}")
        elif kind == "noise":
            key = _counter_name(path)
            noise[key] = noise.get(key, 0) + 1
        elif kind == "representation":
            key = _counter_name(path)
            representation[key] = representation.get(key, 0) + 1


def diff_lines(label, old_doc, new_doc):
    lines, noise, representation = [], {}, {}

    old_head = {k: v for k, v in old_doc.items() if k != "cases"}
    new_head = {k: v for k, v in new_doc.items() if k != "cases"}
    _diff_leaves(f"{label} (file)", old_head, new_head, lines, noise, representation)

    old_cases = {c["code"]: c for c in old_doc.get("cases", [])}
    new_cases = {c["code"]: c for c in new_doc.get("cases", [])}
    for code in list(old_cases) + [c for c in new_cases if c not in old_cases]:
        prefix = f"{label} {code}"
        if code not in new_cases:
            lines.append(f"{prefix} | (case) | present -> {MISSING}")
        elif code not in old_cases:
            lines.append(f"{prefix} | (case) | {MISSING} -> present")
        else:
            old_body = {k: v for k, v in old_cases[code].items() if k != "code"}
            new_body = {k: v for k, v in new_cases[code].items() if k != "code"}
            _diff_leaves(prefix, old_body, new_body, lines, noise, representation)
    return lines, noise, representation


def _counter_lines(noise, representation):
    out = [f"noise cleanup: {field} x{n} (|delta| < 1e-9)" for field, n in noise.items()]
    out += [f"representation only: {field} x{n}" for field, n in representation.items()]
    return out


def _write(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def check_golden(path: Path, actual: dict, update: bool, report: list) -> None:
    actual = normalize(actual)
    if not path.exists():
        if not update:
            pytest.fail(
                f"golden file {path.name} is missing; create it with `uv run pytest --update-golden`",
                pytrace=False,
            )
        _write(path, actual)
        report.append(f"created {path.name}")
        return

    expected = json.loads(path.read_text(encoding="utf-8"))
    if _same(expected, actual):
        return

    label = actual.get("tier", path.stem)
    lines, noise, representation = diff_lines(label, expected, actual)
    counters = _counter_lines(noise, representation)

    if update:
        _write(path, actual)
        report.append(f"== {path.name} ==")
        report.extend(lines)
        report.extend(counters)
        return

    shown = lines[:MAX_SHOWN_LINES]
    message = [f"golden file {path.name} differs: {len(lines)} differences"]
    message.extend(shown)
    if len(lines) > len(shown):
        message.append(f"... {len(lines) - len(shown)} more")
    message.extend(counters)
    message.append("If the change is intended, rewrite with `uv run pytest --update-golden` and review the diff.")
    pytest.fail("\n".join(message), pytrace=False)
