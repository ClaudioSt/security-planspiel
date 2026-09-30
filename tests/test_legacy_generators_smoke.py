import importlib
import sys

from tests.support import REPO_ROOT

XLSX = REPO_ROOT / "angriff_berechnung.xlsx"


def test_legacy_generators_load_umlaut_config(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    monkeypatch.syspath_prepend(str(REPO_ROOT))
    mtime_before = XLSX.stat().st_mtime_ns

    for name in ("generate_attack_calculator", "generate_pptx_cards", "generate_from_template"):
        sys.modules.pop(name, None)

    calculator = importlib.import_module("generate_attack_calculator")
    assert calculator.config["waves"][1]["name"] == "OT-Störung"

    for name in ("generate_pptx_cards", "generate_from_template"):
        module = importlib.import_module(name)
        assert module.load_config()["waves"][1]["name"] == "OT-Störung"

    assert XLSX.stat().st_mtime_ns == mtime_before
