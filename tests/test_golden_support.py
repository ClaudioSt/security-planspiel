import pytest

from tests.support.golden import check_golden, diff_lines, flatten, normalize


def case(code, expected, tags=()):
    return {"code": code, "tags": list(tags), "valid": True, "expected": expected}


def doc(*cases, tier="medium", stage="legacy-float"):
    return {"format": 1, "tier": tier, "stage": stage, "cases": list(cases)}


def test_flatten_nested_structures():
    assert flatten({"a": {"b": [1, {"c": 2}]}}) == {"a.b[0]": 1, "a.b[1].c": 2}


def test_flatten_keeps_empty_containers_as_leaves():
    assert flatten({"events": [], "cia": {}}) == {"events": [], "cia": {}}


def test_normalize_returns_json_native_data():
    assert normalize({1: (1, 2), "x": {"y": (3,)}}) == {"1": [1, 2], "x": {"y": [3]}}


def test_single_field_change_yields_one_domain_line():
    old = doc(case("0000000000", {"kz_final": 15}))
    new = doc(case("0000000000", {"kz_final": 16}))
    lines, noise, representation = diff_lines("medium", old, new)
    assert lines == ["medium 0000000000 | kz_final | 15 -> 16"]
    assert noise == {}
    assert representation == {}


def test_nested_change_uses_field_path_below_expected():
    old = doc(case("0000000001", {"waves": [{"kz_after": 10}, {"kz_after": 20}]}))
    new = doc(case("0000000001", {"waves": [{"kz_after": 10}, {"kz_after": 25}]}))
    lines, _, _ = diff_lines("low", old, new)
    assert lines == ["low 0000000001 | waves[1].kz_after | 20 -> 25"]


def test_float_noise_is_aggregated_per_field_without_lines():
    old = doc(case("0000000001", {"waves": [{"damage": 96.00000000000001}, {"damage": 2.4285714285714284}]}))
    new = doc(case("0000000001", {"waves": [{"damage": 96}, {"damage": "17/7"}]}))
    lines, noise, representation = diff_lines("medium", old, new)
    assert lines == []
    assert noise == {"waves[].damage": 2}
    assert representation == {}


def test_representation_only_changes_are_aggregated_per_field():
    old = doc(case("0000000001", {"e_value": 22.5, "bonus": 3.0}))
    new = doc(case("0000000001", {"e_value": "22.5", "bonus": 3}))
    lines, noise, representation = diff_lines("medium", old, new)
    assert lines == []
    assert noise == {}
    assert representation == {"e_value": 1, "bonus": 1}


def test_real_numeric_change_is_a_line_not_noise():
    old = doc(case("0000000001", {"damage": 96.0}))
    new = doc(case("0000000001", {"damage": 96.5}))
    lines, noise, _ = diff_lines("medium", old, new)
    assert lines == ["medium 0000000001 | damage | 96.0 -> 96.5"]
    assert noise == {}


def test_bool_to_int_is_a_real_change():
    old = doc(case("0000000001", {"e_reached": True}))
    new = doc(case("0000000001", {"e_reached": 1}))
    lines, _, _ = diff_lines("medium", old, new)
    assert lines == ["medium 0000000001 | e_reached | true -> 1"]


def test_string_to_string_change_is_a_real_change():
    old = doc(case("0000000001", {"note": "1.0"}))
    new = doc(case("0000000001", {"note": "1.00"}))
    lines, _, _ = diff_lines("medium", old, new)
    assert lines == ['medium 0000000001 | note | "1.0" -> "1.00"']


def test_added_and_removed_fields_show_missing_side():
    old = doc(case("0000000002", {"kz_final": 10, "old_only": 1}))
    new = doc(case("0000000002", {"kz_final": 10, "new_only": 2}))
    lines, _, _ = diff_lines("medium", old, new)
    assert lines == [
        "medium 0000000002 | old_only | 1 -> <missing>",
        "medium 0000000002 | new_only | <missing> -> 2",
    ]


def test_added_and_removed_cases_show_missing_side():
    old = doc(case("0000000003", {"kz_final": 1}))
    new = doc(case("0000000004", {"kz_final": 1}))
    lines, _, _ = diff_lines("medium", old, new)
    assert lines == [
        "medium 0000000003 | (case) | present -> <missing>",
        "medium 0000000004 | (case) | <missing> -> present",
    ]


def test_document_level_fields_use_file_label():
    old = doc(case("0000000005", {"kz_final": 1}), stage="legacy-float")
    new = doc(case("0000000005", {"kz_final": 1}), stage="exact")
    lines, _, _ = diff_lines("medium", old, new)
    assert lines == ['medium (file) | stage | "legacy-float" -> "exact"']


def test_digest_style_documents_without_cases_are_compared_field_wise():
    old = {"format": 1, "tier": "low", "count": 5, "digest": "aa", "kz_histogram": [1, 2]}
    new = {"format": 1, "tier": "low", "count": 5, "digest": "bb", "kz_histogram": [1, 3]}
    lines, _, _ = diff_lines("low", old, new)
    assert lines == [
        'low (file) | digest | "aa" -> "bb"',
        "low (file) | kz_histogram[1] | 2 -> 3",
    ]


def test_check_golden_missing_file_names_update_command(tmp_path):
    with pytest.raises(pytest.fail.Exception, match="uv run pytest --update-golden"):
        check_golden(tmp_path / "missing.json", doc(), update=False, report=[])


def test_check_golden_identical_passes_and_reports_nothing(tmp_path):
    path = tmp_path / "g.json"
    report = []
    check_golden(path, doc(case("0000000000", {"kz_final": 1})), update=True, report=report)
    report.clear()
    check_golden(path, doc(case("0000000000", {"kz_final": 1})), update=False, report=report)
    check_golden(path, doc(case("0000000000", {"kz_final": 1})), update=True, report=report)
    assert report == []


def test_check_golden_mismatch_shows_first_30_lines_and_total(tmp_path):
    path = tmp_path / "g.json"
    cases_old = [case(f"{i:010d}", {"kz_final": 1}) for i in range(40)]
    cases_new = [case(f"{i:010d}", {"kz_final": 2}) for i in range(40)]
    check_golden(path, doc(*cases_old), update=True, report=[])
    with pytest.raises(pytest.fail.Exception) as excinfo:
        check_golden(path, doc(*cases_new), update=False, report=[])
    message = str(excinfo.value)
    assert "40 differences" in message
    assert sum(1 for line in message.splitlines() if line.startswith("medium 00")) == 30
    assert "--update-golden" in message
    assert json_kz(path) == 1


def json_kz(path):
    import json
    return json.loads(path.read_text(encoding="utf-8"))["cases"][0]["expected"]["kz_final"]


def test_check_golden_update_rewrites_file_and_reports(tmp_path):
    path = tmp_path / "g.json"
    check_golden(path, doc(case("0000000000", {"kz_final": 15, "name": "OT-Störung"})), update=True, report=[])
    report = []
    check_golden(path, doc(case("0000000000", {"kz_final": 16, "name": "OT-Störung"})), update=True, report=report)
    assert "medium 0000000000 | kz_final | 15 -> 16" in report
    raw = path.read_bytes()
    assert b"\r" not in raw
    assert raw.endswith(b"\n")
    text = raw.decode("utf-8")
    assert "Störung" in text
    assert '\n  "format": 1' in text
    assert json_kz(path) == 16


def test_check_golden_update_reports_counters(tmp_path):
    path = tmp_path / "g.json"
    check_golden(path, doc(case("0000000000", {"damage": 96.00000000000001, "e": 22.5})), update=True, report=[])
    report = []
    check_golden(path, doc(case("0000000000", {"damage": 96, "e": "22.5"})), update=True, report=report)
    assert any(line.startswith("noise cleanup: damage x1") for line in report)
    assert any(line.startswith("representation only: e x1") for line in report)
    assert not any("|" in line and "->" in line for line in report)


def test_check_golden_representation_only_mismatch_fails_without_update(tmp_path):
    path = tmp_path / "g.json"
    check_golden(path, doc(case("0000000000", {"e": 22.5})), update=True, report=[])
    with pytest.raises(pytest.fail.Exception, match="representation only: e x1"):
        check_golden(path, doc(case("0000000000", {"e": "22.5"})), update=False, report=[])
