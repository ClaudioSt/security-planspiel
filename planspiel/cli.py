import argparse
import json
import sys
from pathlib import Path


def configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def _validate_command(config: str, strict: bool) -> int:
    from planspiel.config import read_raw_config
    from planspiel.validate import validate

    try:
        issues = validate(read_raw_config(Path(config)))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR schema.json {config}: {error}")
        print("1 Fehler, 0 Warnung(en)")
        return 1
    errors = [issue for issue in issues if issue.level == "error"]
    warnings = [issue for issue in issues if issue.level == "warning"]
    for issue in issues:
        label = "ERROR" if issue.level == "error" else "WARN"
        print(f"{label} {issue.code} {issue.path}: {issue.message}")
    print(f"{len(errors)} Fehler, {len(warnings)} Warnung(en)")
    return 1 if errors or (strict and warnings) else 0


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="planspiel",
        description="Werkzeuge für das CIA-Planspiel (Simulation, Prüfungen).",
    )
    subparsers = parser.add_subparsers(dest="command")
    validate_parser = subparsers.add_parser(
        "validate", help="Prüft die Konfiguration auf Fehler und Handrechenbarkeit."
    )
    validate_parser.add_argument(
        "--config", default="simulation_config.json", help="Pfad zur Konfigurationsdatei."
    )
    validate_parser.add_argument(
        "--strict",
        action="store_true",
        help="Warnungen zählen als Fehler (wird in Phase 6 verwendet).",
    )
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    return _validate_command(args.config, args.strict)
