import subprocess
import sys

from simulate_outcomes import load_config
from tests.support import CONFIG_PATH, REPO_ROOT

MOJIBAKE_MARKERS = ("Ã", "Â", "â€")


def _display_strings(config):
    (_, _, _, waves, measures, events, _, final_events) = config
    for wave in waves:
        yield wave.name
        for bonus in wave.bonus_measures:
            yield bonus.description
    for measure in measures.values():
        yield measure.name
    for wave_events in events.values():
        for event in wave_events:
            yield event.name
            yield event.description
    for event in final_events:
        yield event.name
        yield event.description


def test_loader_decodes_config_as_utf8():
    waves = load_config(CONFIG_PATH)[3]
    assert waves[0].bonus_measures[0].description == "EDR/XDR erkennt Ransomware früh"


def test_no_mojibake_in_loaded_config():
    config = load_config(CONFIG_PATH)
    offenders = [
        (text, marker)
        for text in _display_strings(config)
        for marker in MOJIBAKE_MARKERS
        if marker in text
    ]
    assert offenders == []


def test_utf8_stdio_helper():
    code = (
        "from planspiel.cli import configure_utf8_stdio; "
        "configure_utf8_stdio(); "
        "print('OT-Störung − ≥ €')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert result.stdout.decode("utf-8").strip() == "OT-Störung − ≥ €"
