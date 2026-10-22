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


def _texts_command(config: str, content_dir: str) -> int:
    import tomllib

    from planspiel.config import load_config
    from planspiel.texts import check_texts, load_content

    try:
        issues = check_texts(load_config(Path(config)), load_content(Path(content_dir)))
    except (OSError, tomllib.TOMLDecodeError) as error:
        print(f"ERROR texts.toml {content_dir}: {error}")
        print("1 Fehler, 0 Warnung(en)")
        return 1
    errors = [issue for issue in issues if issue.level == "error"]
    warnings = [issue for issue in issues if issue.level == "warning"]
    for issue in issues:
        label = "ERROR" if issue.level == "error" else "WARN"
        print(f"{label} {issue.code} {issue.path}: {issue.message}")
    print(f"{len(errors)} Fehler, {len(warnings)} Warnung(en)")
    return 1 if errors else 0


def _clues_command(config: str, content_dir: str) -> int:
    import tomllib

    from planspiel.config import load_config
    from planspiel.texts import (
        CLUES_FILE,
        TEXTE_FILE,
        FacilitatorView,
        check_clues,
        format_clue_matrix,
        load_clues,
        load_texts,
    )

    clues_path = Path(content_dir) / CLUES_FILE
    try:
        cfg = load_config(Path(config))
        texts = load_texts(Path(content_dir) / TEXTE_FILE)
        clues = load_clues(clues_path)
    except (OSError, tomllib.TOMLDecodeError) as error:
        print(f"ERROR clues.toml {clues_path}: {error}")
        print("1 Fehler, 0 Warnung(en)")
        return 1
    print(format_clue_matrix(FacilitatorView(cfg, texts, clues).clue_matrix()))
    print()
    issues = check_clues(cfg, texts, clues)
    errors = [issue for issue in issues if issue.level == "error"]
    warnings = [issue for issue in issues if issue.level == "warning"]
    for issue in issues:
        label = "ERROR" if issue.level == "error" else "WARN"
        print(f"{label} {issue.code} {issue.path}: {issue.message}")
    print(f"{len(errors)} Fehler, {len(warnings)} Warnung(en)")
    return 1 if errors else 0


def _tausch_command(parser: argparse.ArgumentParser, config: str, tiers: list[str] | None, summary_dir: str) -> int:
    import time

    from planspiel.config import load_config
    from planspiel.enumerate import enumerate_swap_layer
    from planspiel.report import SUMMARY_FILENAME, SWAP_LAYER, format_swap_console, summarize_swap_layer, write_summary

    cfg = load_config(Path(config))
    names = tiers or list(cfg.budget_tiers)
    unknown = [name for name in names if name not in cfg.budget_tiers]
    if unknown:
        parser.error(f"Unbekanntes Budget-Tier '{unknown[0]}'. Verfügbar: {', '.join(cfg.budget_tiers)}.")
    target_dir = Path(summary_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        started = time.perf_counter()
        layer = enumerate_swap_layer(cfg, name)
        summary = summarize_swap_layer(cfg, name, layer)
        path = target_dir / SUMMARY_FILENAME.format(tier=f"{SWAP_LAYER}_{name}")
        write_summary(path, summary)
        seconds = time.perf_counter() - started
        print(format_swap_console(summary))
        print()
        print(f"Laufzeit: {seconds:.1f} s")
        print(f"Zusammenfassung: {path}")
        print()
    return 0


def _gate_command(parser: argparse.ArgumentParser, config: str, tiers: list[str] | None) -> int:
    from planspiel.config import load_config
    from planspiel.gate import format_gate_report, gate_tier

    cfg = load_config(Path(config))
    names = tiers or list(cfg.budget_tiers)
    unknown = [name for name in names if name not in cfg.budget_tiers]
    if unknown:
        parser.error(f"Unbekanntes Budget-Tier '{unknown[0]}'. Verfügbar: {', '.join(cfg.budget_tiers)}.")
    all_passed = True
    for name in names:
        result = gate_tier(cfg, name)
        print(format_gate_report(result))
        print()
        all_passed = all_passed and result.passed
    print("Überziehungs-Gate: bestanden" if all_passed else "Überziehungs-Gate: NICHT bestanden")
    return 0 if all_passed else 1


def _print_command(config: str, content_dir: str, print_dir: str, out_dir: str, build_dir: str) -> int:
    import shutil
    import tomllib

    import jinja2

    from planspiel import render, texbuild
    from planspiel.config import load_config
    from planspiel.texts import TEXTE_FILE, load_texts

    try:
        problems = texbuild.preflight()
    except texbuild.TexBuildError as error:
        problems = [str(error)]
    if problems:
        for problem in problems:
            print(f"ERROR print.preflight {problem}")
        print("Installieren (MiKTeX Console oder Terminal): miktex packages install --package-id-file print/miktex-packages.txt")
        print(f"{len(problems)} Fehler")
        return 1
    texte_path = Path(content_dir) / TEXTE_FILE
    try:
        cfg = load_config(Path(config))
        texts = load_texts(texte_path)
    except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError, ValueError) as error:
        print(f"ERROR print.input {config} / {texte_path}: {error}")
        print("1 Fehler")
        return 1
    try:
        documents = render.render_all(cfg, texts, Path(print_dir) / "templates")
    except (jinja2.TemplateError, TypeError, ValueError) as error:
        print(f"ERROR print.render {error}")
        print("1 Fehler")
        return 1
    try:
        pdfs = texbuild.build_documents(documents, Path(print_dir), Path(build_dir))
    except texbuild.TexBuildError as error:
        print(f"ERROR print.tex {error}")
        print("1 Fehler")
        return 1
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    for job in sorted(pdfs):
        shutil.copyfile(pdfs[job], target / f"{job}.pdf")
        print(f"{target / f'{job}.pdf'}")
    print(f"{len(pdfs)} Dokument(e) gebaut: {target}")
    return 0


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
    tausch_parser = subparsers.add_parser(
        "tausch",
        help="Bewertet jeden Plan der ersten Welle mit jedem legalen Maßnahmentausch des Kurswechsels.",
    )
    tausch_parser.add_argument(
        "--config", default="simulation_config.json", help="Pfad zur Konfigurationsdatei."
    )
    tausch_parser.add_argument(
        "--tier",
        action="append",
        default=None,
        help="Budget-Tier (wiederholbar, Standard: alle Tiers der Konfiguration).",
    )
    tausch_parser.add_argument(
        "--summary-dir",
        default=".",
        help="Verzeichnis für simulation_summary_tausch_<tier>.json (Standard: Arbeitsverzeichnis).",
    )
    gate_parser = subparsers.add_parser(
        "gate",
        help="Prüft je Tier, dass Überziehen nie lohnt (gekürzte Version im Budget erreicht eine höhere End-KZ).",
    )
    gate_parser.add_argument(
        "--config", default="simulation_config.json", help="Pfad zur Konfigurationsdatei."
    )
    gate_parser.add_argument(
        "--tier",
        action="append",
        default=None,
        help="Budget-Tier (wiederholbar, Standard: alle Tiers der Konfiguration).",
    )
    texts_parser = subparsers.add_parser(
        "texts", help="Prüft content/texte.toml: Abdeckung, Ziffern und Story-Regeln."
    )
    texts_parser.add_argument(
        "--config", default="simulation_config.json", help="Pfad zur Konfigurationsdatei."
    )
    texts_parser.add_argument(
        "--content-dir",
        default="content",
        help="Verzeichnis mit texte.toml, digit_allowlist.toml und giveaway_terms.toml.",
    )
    clues_parser = subparsers.add_parser(
        "clues",
        help="Zeigt die Hinweis-Matrix für die Spielleitung und prüft sie: mindestens zwei Hinweise aus zwei Dokumenten je Angriff.",
    )
    clues_parser.add_argument(
        "--config", default="simulation_config.json", help="Pfad zur Konfigurationsdatei."
    )
    clues_parser.add_argument(
        "--content-dir",
        default="content",
        help="Verzeichnis mit texte.toml und clues.toml.",
    )
    print_parser = subparsers.add_parser(
        "print", help="Baut alle Druckmaterialien (LaTeX → PDF) aus Konfiguration und Texten."
    )
    print_parser.add_argument(
        "--config", default="simulation_config.json", help="Pfad zur Konfigurationsdatei."
    )
    print_parser.add_argument(
        "--content-dir", default="content", help="Verzeichnis mit texte.toml."
    )
    print_parser.add_argument(
        "--print-dir", default="print", help="Verzeichnis mit planspiel.sty und templates/."
    )
    print_parser.add_argument(
        "--out-dir", default="final_documents/generated", help="Zielverzeichnis für die fertigen PDFs."
    )
    print_parser.add_argument(
        "--build-dir", default="build/print", help="Arbeitsverzeichnis für TeX-Quellen und Hilfsdateien."
    )
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "print":
        return _print_command(args.config, args.content_dir, args.print_dir, args.out_dir, args.build_dir)
    if args.command == "texts":
        return _texts_command(args.config, args.content_dir)
    if args.command == "clues":
        return _clues_command(args.config, args.content_dir)
    if args.command == "tausch":
        return _tausch_command(parser, args.config, args.tier, args.summary_dir)
    if args.command == "gate":
        return _gate_command(parser, args.config, args.tier)
    return _validate_command(args.config, args.strict)
