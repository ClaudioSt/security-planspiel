import json
import re
import subprocess
import sys

from planspiel.config import load_config
from planspiel.texts import load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT

MOJIBAKE_MARKERS = ("Ã", "Â", "â€")


def _display_strings(config):
    for measure in config.measures.values():
        yield measure.name
    for wave_events in config.events.values():
        for event in wave_events:
            yield event.name
    for event in config.final_events:
        yield event.name
    for _, text in load_texts(CONTENT_DIR / "texte.toml").strings():
        yield text


def test_loader_decodes_config_as_utf8():
    assert load_config(CONFIG_PATH).events[1][1].name == "Operative Unterstützung"


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


ID_KEYS = {"id", "measure", "measures", "attack_id", "type", "default_budget_tier"}

TRANSLITERATION_PATTERNS = tuple(
    re.compile(stem, re.IGNORECASE)
    for stem in (
        r"stoerung",
        r"fuehr",
        r"geschaeft",
        r"unterstuetz",
        r"verkuend",
        r"pruef",
        r"haeng",
        r"\bfuer\b",
        r"hoechst",
        r"verschaerf",
        r"massnahm",
        r"ueber",
        r"moeglich",
        r"koenn",
        r"muess",
        r"waehr",
        r"\bgross",
        r"schliess",
    )
)


def _load_raw():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _walk_display_strings(node, path="$"):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ID_KEYS:
                continue
            yield from _walk_display_strings(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk_display_strings(value, f"{path}[{index}]")
    elif isinstance(node, str):
        yield path, node


def _walk_ascii_targets(node, path="$", under_id_key=False):
    if isinstance(node, dict):
        for key, value in node.items():
            yield f"{path}.{key} (key)", key
            yield from _walk_ascii_targets(value, f"{path}.{key}", key in ID_KEYS)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk_ascii_targets(value, f"{path}[{index}]", under_id_key)
    elif isinstance(node, str) and under_id_key:
        yield path, node


def test_revealed_attack_name_uses_umlauts():
    assert load_texts(CONTENT_DIR / "texte.toml").get("attacks.ot.revealed.name") == "OT-Störung"


def test_display_strings_have_no_transliterations():
    offenders = [
        f"{path}: {text!r} (stem {pattern.pattern})"
        for path, text in _walk_display_strings(_load_raw())
        for pattern in TRANSLITERATION_PATTERNS
        if pattern.search(text)
    ]
    assert offenders == []


def test_ids_and_keys_stay_ascii():
    offenders = [path for path, text in _walk_ascii_targets(_load_raw()) if not text.isascii()]
    assert offenders == []


def _texte_strings():
    return load_texts(CONTENT_DIR / "texte.toml").strings()


def test_texte_toml_has_no_mojibake():
    offenders = [
        f"{key}: {marker}" for key, text in _texte_strings() for marker in MOJIBAKE_MARKERS if marker in text
    ]
    assert offenders == []


def test_texte_toml_has_no_transliterations():
    offenders = [
        f"{key}: {text!r} (stem {pattern.pattern})"
        for key, text in _texte_strings()
        for pattern in TRANSLITERATION_PATTERNS
        if pattern.search(text)
    ]
    assert offenders == []


def test_texte_toml_keys_are_ascii():
    keys = [key for key, _ in load_texts(CONTENT_DIR / "texte.toml").leaves()]
    assert keys
    assert [key for key in keys if not key.isascii()] == []
