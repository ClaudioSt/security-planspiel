"""The frozen MHP baseline: strict loader, provenance and isolation (FLOW-04, D-14, D-26).

`content/mhp_baseline.json` holds the values the MHP facilitators printed and played, in today's key names. These tests
prove where it came from (the config at commit 1cfb2fa, plus the printed override), that the loader is strict, and that
nothing but the "Was ist neu" builder can read it.
"""
import ast
import builtins
import copy
import dataclasses
import json
import pathlib
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from fractions import Fraction

import pytest

from planspiel.config import Config, load_config
from planspiel.was_neu import BASELINE_FILE, Baseline, PrintedOverride, load_baseline
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT

BASELINE_PATH = CONTENT_DIR / BASELINE_FILE
OLD_COMMIT = "1cfb2fa"
PRINTED_LOCATIONS = (REPO_ROOT / "final_documents", REPO_ROOT / "archive" / "mhp_print_material_2026-07")
DRAWINGML = "{http://schemas.openxmlformats.org/drawingml/2006/main}t"
WORDPROCESSINGML = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"


def _raw():
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"), parse_float=Fraction)


def _write(tmp_path, raw):
    target = tmp_path / BASELINE_FILE
    target.write_text(json.dumps(raw, ensure_ascii=False, default=float), encoding="utf-8")
    return target


# --- loader ---------------------------------------------------------------------------------------------------


def test_a_missing_file_gives_none(tmp_path):
    assert load_baseline(tmp_path / BASELINE_FILE) is None


def test_the_real_file_loads():
    baseline = load_baseline(BASELINE_PATH)
    assert isinstance(baseline, Baseline)
    assert baseline.source.config_commit == OLD_COMMIT
    assert len(baseline.source.printed_overrides) == 1
    override = baseline.source.printed_overrides[0]
    assert isinstance(override, PrintedOverride)
    assert override.key == "budget_review.boundary"
    assert baseline.budget_review["boundary"] == "above"
    assert set(baseline.measures) == {f"M{n}" for n in range(1, 11)}
    assert set(baseline.attacks) == {"ransomware", "ot", "exfil"}


def _mutations():
    def top(raw):
        raw["extra"] = 1

    def group(raw):
        raw["budget_tiers"]["low"]["foo"] = 1

    def wave(raw):
        raw["waves"]["1"]["foo"] = 1

    def string_number(raw):
        raw["budget_tiers"]["low"]["budget"] = "350"

    def string_in_event(raw):
        raw["events"]["sparprogramm"]["budget_delta"] = "-20"

    def schema(raw):
        raw["schema"] = 2

    def boundary(raw):
        raw["budget_review"]["boundary"] = "below"

    def override_extra(raw):
        raw["source"]["printed_overrides"][0]["note"] = "x"

    def override_missing(raw):
        del raw["source"]["printed_overrides"][0]["part"]

    def override_path(raw):
        raw["source"]["printed_overrides"][0]["file"] = "final_documents/Events_Security-Game.pptx"

    def override_backslash(raw):
        raw["source"]["printed_overrides"][0]["file"] = "x\\Events_Security-Game.pptx"

    def printed_empty(raw):
        raw["source"]["printed_overrides"][0]["printed"] = []

    def printed_number(raw):
        raw["source"]["printed_overrides"][0]["printed"] = [25001]

    def source_extra(raw):
        raw["source"]["date"] = "2026-07-06"

    return [
        (top, "extra"),
        (group, "foo"),
        (wave, "foo"),
        (string_number, "budget"),
        (string_in_event, "budget_delta"),
        (schema, "schema"),
        (boundary, "boundary"),
        (override_extra, "note"),
        (override_missing, "part"),
        (override_path, "file"),
        (override_backslash, "file"),
        (printed_empty, "printed"),
        (printed_number, "printed"),
        (source_extra, "date"),
    ]


@pytest.mark.parametrize("mutate,needle", _mutations(), ids=lambda value: getattr(value, "__name__", value))
def test_the_loader_is_strict(tmp_path, mutate, needle):
    raw = copy.deepcopy(_raw())
    mutate(raw)
    target = _write(tmp_path, raw)
    with pytest.raises(ValueError) as caught:
        load_baseline(target)
    assert BASELINE_FILE in str(caught.value)
    assert needle in str(caught.value)


def test_a_non_object_file_is_an_error(tmp_path):
    target = tmp_path / BASELINE_FILE
    target.write_text("[1]", encoding="utf-8")
    with pytest.raises(ValueError, match=BASELINE_FILE):
        load_baseline(target)


# --- printed provenance (D-26) -----------------------------------------------------------------------------------


def _printed_text(file_name, part):
    for directory in PRINTED_LOCATIONS:
        candidate = directory / file_name
        if candidate.is_file():
            break
    else:
        pytest.fail(f"printed MHP file {file_name} is in neither {PRINTED_LOCATIONS[0]} nor {PRINTED_LOCATIONS[1]}")
    with zipfile.ZipFile(candidate) as package:
        root = ET.fromstring(package.read(part))
    tag = DRAWINGML if part.startswith("ppt/") else WORDPROCESSINGML
    return "".join(element.text or "" for element in root.iter() if element.tag == tag)


def _value_at(raw, dotted):
    node = raw
    for key in dotted.split("."):
        node = node[key]
    return node


def _override_records():
    return _raw()["source"]["printed_overrides"]


def test_the_override_set_is_exactly_the_budget_review_boundary():
    records = _override_records()
    assert records == [
        {
            "key": "budget_review.boundary",
            "value": "above",
            "file": "Events_Security-Game.pptx",
            "part": "ppt/slides/slide9.xml",
            "location": "Budget Review",
            "printed": ["25.001", "50.001", "75.001"],
        }
    ]


@pytest.mark.parametrize("record", _override_records(), ids=lambda record: record["key"])
def test_printed_overrides_match_the_printed_mhp_material(record):
    text = _printed_text(record["file"], record["part"])
    start = text.find(record["location"])
    assert start >= 0, f"{record['location']!r} not printed in {record['file']} {record['part']}"
    after = text[start + len(record["location"]):]
    for printed in record["printed"]:
        assert printed in after, f"{printed!r} not printed after {record['location']!r}"
    assert _value_at(_raw(), record["key"]) == record["value"]


# --- config provenance (D-14: "confirm it matches the MHP state") -----------------------------------------------------


def _git(*args):
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL, timeout=30,
    )


def _old_config():
    if _git("cat-file", "-e", OLD_COMMIT).returncode != 0:
        pytest.skip(f"commit {OLD_COMMIT} is not in this clone (shallow clone)")
    shown = _git("show", f"{OLD_COMMIT}:simulation_config.json")
    assert shown.returncode == 0, shown.stderr
    return json.loads(shown.stdout, parse_float=Fraction)


def _map_old(old):
    """The old raw config in today's key names, numbers and ids only (RESEARCH Q1 schema table)."""
    mapped = {
        "schema": 1,
        "base_cia": dict(old["base_cia"]),
        "budget_tiers": {
            name: {key: tier[key] for key in ("budget", "kz_start", "severity_multiplier")}
            for name, tier in old["budget_tiers"].items()
        },
        "waves": {
            str(wave["id"]): {
                "weights": dict(wave["weights"]),
                "e_threshold": wave["e_threshold"],
                "bonus_measures": [
                    {key: bonus[key] for key in ("measure", "min_level", "bonus")}
                    for bonus in wave["bonus_measures"]
                ],
            }
            for wave in old["waves"]
        },
        "attacks": {
            attack_id: {
                key: attack[key]
                for key in (
                    "base_severity", "s_unit", "kz_at_full_damage", "kz_at_full_mitigation", "cia_impact",
                    "mitigation_cap", "allow_recovery",
                )
            }
            for attack_id, attack in old["attacks"].items()
        },
        "measures": {
            measure_id: {
                "levels": {
                    level: {
                        "cia": dict(info["cia"]),
                        "init": info["init"],
                        "opex": info["opex"],
                        "recovery": info.get("recovery", 0),
                    }
                    for level, info in measure["levels"].items()
                    if level != "0"
                }
            }
            for measure_id, measure in old["measures"].items()
        },
        "events": {},
    }
    for events in old["events"].values():
        for event in events:
            if event["type"] == "noop":
                continue
            mapped["events"][event["id"]] = {
                key: value for key, value in event.items() if key not in ("id", "name", "description", "type")
            }
    review = old["final_events"][0]
    first, *tiers = review["tiers"]
    mapped["budget_review"] = {
        "boundary": "inclusive",
        "tiers": tiers,
        "overspend": {"flat_kz": first[1]},
    }
    return mapped


def _flatten(node, prefix=""):
    if isinstance(node, dict):
        flat = {}
        for key, value in node.items():
            flat.update(_flatten(value, f"{prefix}.{key}" if prefix else key))
        return flat
    return {prefix: node}


def test_the_baseline_is_the_config_at_the_mhp_commit_except_the_printed_overrides():
    raw = _raw()
    overridden = {record["key"] for record in raw["source"]["printed_overrides"]}
    content = {key: value for key, value in raw.items() if key != "source"}
    expected = _flatten(_map_old(_old_config()))
    actual = _flatten(content)
    for key in overridden:
        expected.pop(key, None)
        actual.pop(key, None)
    assert actual == expected


def test_the_measure_dependencies_never_changed_since_the_mhp_commit():
    """If a rebalance changes a dependency, the Was-ist-neu diff must grow a dependency group first."""
    old = _old_config()
    current = json.loads((REPO_ROOT / "simulation_config.json").read_text(encoding="utf-8"), parse_float=Fraction)
    for measure_id, measure in old["measures"].items():
        assert measure["dependencies"] == current["measures"][measure_id]["dependencies"], measure_id


def test_the_baseline_holds_no_prose_outside_the_source_block():
    raw = _raw()
    allowed_strings = {"measure", "measures", "boundary"}

    def walk(node, key):
        if isinstance(node, dict):
            for child_key, value in node.items():
                walk(value, child_key)
        elif isinstance(node, list):
            for value in node:
                walk(value, key)
        elif isinstance(node, str):
            assert key in allowed_strings, f"string under {key!r}: {node!r}"

    walk({k: v for k, v in raw.items() if k != "source"}, "")
    assert "archive/" not in BASELINE_PATH.read_text(encoding="utf-8")


# --- isolation (D-14, T-07-10) -----------------------------------------------------------------------------------


def _planspiel_sources():
    return sorted((REPO_ROOT / "planspiel").glob("*.py"))


def test_the_baseline_file_name_occurs_only_in_the_builder_and_the_stamp():
    holders = {
        source.name for source in _planspiel_sources() if "mhp_baseline" in source.read_text(encoding="utf-8")
    }
    assert holders == {"was_neu.py", "stamp.py"}


def _imports_was_neu(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[-1] == "was_neu" for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.split(".")[-1] == "was_neu":
                return True
            if module in ("planspiel", "") and any(alias.name == "was_neu" for alias in node.names):
                return True
    return False


def test_only_the_renderer_and_the_cli_may_import_the_builder():
    importers = {
        source.name
        for source in _planspiel_sources()
        if _imports_was_neu(ast.parse(source.read_text(encoding="utf-8")))
    }
    assert importers <= {"render.py", "cli.py"}


def test_config_has_no_baseline_field():
    names = [field.name for field in dataclasses.fields(Config)]
    assert not [name for name in names if "baseline" in name or "mhp" in name]


def test_load_config_never_reads_the_baseline(monkeypatch):
    seen = []
    real_read_text = pathlib.Path.read_text
    real_open = builtins.open

    def read_text(self, *args, **kwargs):
        seen.append(str(self))
        return real_read_text(self, *args, **kwargs)

    def spy_open(file, *args, **kwargs):
        seen.append(str(file))
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, "read_text", read_text)
    monkeypatch.setattr(builtins, "open", spy_open)
    first = load_config(CONFIG_PATH)
    monkeypatch.undo()
    assert seen and not [item for item in seen if "mhp_baseline" in item]
    assert first == load_config(CONFIG_PATH)
