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

    texts_path = Path(content_dir) / TEXTE_FILE
    clues_path = Path(content_dir) / CLUES_FILE
    loaded = []
    # Each input is loaded on its own so an error names the file that actually carries it (a ConfigError is a ValueError).
    for label, source, loader in (
        ("config", config, load_config),
        ("texte.toml", texts_path, load_texts),
        ("clues.toml", clues_path, load_clues),
    ):
        try:
            loaded.append(loader(Path(source)))
        except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
            print(f"ERROR {label} {source}: {error}")
            print("1 Fehler, 0 Warnung(en)")
            return 1
    cfg, texts, clues = loaded
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


def _referenzpfade_command(
    parser: argparse.ArgumentParser,
    config: str,
    tiers: list[str] | None,
    median: int | None,
    out_dir: str | None,
    starts: int,
    keep: int,
) -> int:
    import time

    from planspiel.config import load_config
    from planspiel.refpaths import candidate_paths, format_tier_report, swap_layer_median

    cfg = load_config(Path(config))
    names = tiers or list(cfg.budget_tiers)
    unknown = [name for name in names if name not in cfg.budget_tiers]
    if unknown:
        parser.error(f"Unbekanntes Budget-Tier '{unknown[0]}'. Verfügbar: {', '.join(cfg.budget_tiers)}.")
    target_dir = Path(out_dir) if out_dir else None
    if target_dir is not None:
        target_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        started = time.perf_counter()
        tier_median = median if median is not None else swap_layer_median(cfg, name)
        candidates = [] if tier_median is None else candidate_paths(
            cfg, name, median=tier_median, starts=starts, keep=keep
        )
        text = format_tier_report(cfg, name, tier_median, candidates)
        print(text)
        print()
        print(f"Laufzeit: {time.perf_counter() - started:.1f} s")
        print()
        if target_dir is not None:
            path = target_dir / f"referenzpfade_{name}.txt"
            path.write_text(text + "\n", encoding="utf-8", newline="\n")
            print(f"Ausgabe: {path}")
            print()
    return 0


def _gate_command(
    parser: argparse.ArgumentParser,
    config: str,
    tiers: list[str] | None,
    paths: bool = False,
    narrow: bool = False,
    jobs: int = 1,
) -> int:
    from planspiel.config import load_config

    if narrow and not paths:
        parser.error("--narrow gehört zu --paths.")
    # Exit 1 is the verdict "NICHT bestanden"; an unreadable or invalid config (ConfigError is a ValueError) and errors
    # re-raised from the tier workers exit with 2.
    try:
        cfg = load_config(Path(config))
        names = tiers or list(cfg.budget_tiers)
        unknown = [name for name in names if name not in cfg.budget_tiers]
        if unknown:
            parser.error(f"Unbekanntes Budget-Tier '{unknown[0]}'. Verfügbar: {', '.join(cfg.budget_tiers)}.")
        if paths:
            return _gate_paths_command(config, names, narrow, jobs, set(names) == set(cfg.budget_tiers))
        return _gate_static_command(cfg, names)
    except (OSError, ValueError) as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        return 2


def _gate_static_command(cfg, names: list[str]) -> int:
    from planspiel.gate import format_gate_report, gate_tier

    all_passed = True
    for name in names:
        result = gate_tier(cfg, name)
        print(format_gate_report(result))
        print()
        all_passed = all_passed and result.passed
    print("Überziehungs-Gate: bestanden" if all_passed else "Überziehungs-Gate: NICHT bestanden")
    return 0 if all_passed else 1


def _gate_paths_command(config: str, names: list[str], narrow: bool, jobs: int, all_tiers: bool = True) -> int:
    import functools

    from planspiel import gate, parallel

    results = parallel.map_tiers(functools.partial(gate.paths_worker, narrow=narrow), config, names, jobs)
    all_passed = True
    for name in names:
        static, families = results[name]
        print(gate.format_gate_report(static))
        print()
        all_passed = all_passed and static.passed
        for family, result in families.items():
            print(gate.format_path_gate_report(result))
            print()
            if family != gate.NARROW_FAMILY:
                all_passed = all_passed and result.passed
    if all_tiers:  # X is the maximum over all tiers (D-13); a subset of the tiers cannot calibrate it
        calibration = gate.calibrate(
            {name: results[name][0] for name in names}, {name: results[name][1] for name in names}
        )
        print(gate.format_calibration(calibration))
    else:
        print("Kalibrierung von X: nicht berechnet (nur über alle Tiers)")
    print()
    print("Überziehungs-Gate: bestanden" if all_passed else "Überziehungs-Gate: NICHT bestanden")
    return 0 if all_passed else 1


def _print_command(
    config: str, content_dir: str, print_dir: str, out_dir: str, build_dir: str, check: bool = False
) -> int:
    import shutil
    import tomllib

    import jinja2

    from planspiel import render, stamp, texbuild, veil
    from planspiel.config import load_config
    from planspiel.printmodel import PrintModelError
    from planspiel.texts import CLUES_FILE, check_clues, check_texts, load_clues, load_content
    from planspiel.was_neu import BASELINE_FILE, load_baseline

    failure = 2 if check else 1  # --check: 1 means stale, 2 means the check itself could not run
    if not check:
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
    try:
        cfg = load_config(Path(config))
        content = load_content(Path(content_dir))
        clues = load_clues(Path(content_dir) / CLUES_FILE)
        baseline = load_baseline(Path(content_dir) / BASELINE_FILE)
    except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError, ValueError) as error:
        print(f"ERROR print.input {config} / {content_dir}: {error}")
        print("1 Fehler")
        return failure
    texts = content.texts
    try:
        assets = texbuild.asset_paths(Path(content_dir))
    except texbuild.TexBuildError as error:
        print(f"ERROR print.input {error}")
        print("1 Fehler")
        return failure
    # The checks of `planspiel texts` (no numbers in prose, veil, required keys) hold at print time too.
    text_errors = [issue for issue in check_texts(cfg, content) if issue.level == "error"]
    if text_errors:
        for issue in text_errors:
            print(f"ERROR print.texts {issue.code} {issue.path}: {issue.message}")
        print(f"{len(text_errors)} Fehler")
        return failure
    # The clue matrix of the facilitator booklet is a print input: it must quote the pre-wave texts verbatim (VEIL-03).
    clue_errors = [issue for issue in check_clues(cfg, texts, clues) if issue.level == "error"]
    if clue_errors:
        for issue in clue_errors:
            print(f"ERROR print.clues {issue.code} {issue.path}: {issue.message}")
        print(f"{len(clue_errors)} Fehler")
        return failure
    try:
        documents = render.render_all(cfg, texts, Path(print_dir) / "templates", clues=clues, baseline=baseline)
    except PrintModelError as error:
        print(f"ERROR print.model {error}")
        print("1 Fehler")
        return failure
    except KeyError as error:  # a text key the content source does not carry
        print(f"ERROR print.model {error.args[0] if error.args else error}")
        print("1 Fehler")
        return failure
    except (jinja2.TemplateError, TypeError, ValueError) as error:
        print(f"ERROR print.render {error}")
        print("1 Fehler")
        return failure
    veil_issues = veil.scan_documents(cfg, texts, content.terms, documents)
    if veil_issues:
        for issue in veil_issues:
            print(f"ERROR print.veil {issue.code} {issue.path}: {issue.message}")
        print(f"{len(veil_issues)} Fehler")
        return failure
    try:
        repo = stamp.repo_for_inputs(Path(config))
        off_default = stamp.nondefault_inputs(repo, Path(config), Path(content_dir), Path(print_dir))
        version = stamp.compute_stamp(
            documents, Path(print_dir), repo, unofficial=bool(off_default), assets=assets
        )
    except (stamp.StampError, OSError) as error:
        print(f"ERROR print.stamp {error}")
        print("1 Fehler")
        return failure
    if off_default:
        print(f"Hinweis: {', '.join(off_default)} weicht vom Repository-Standard ab, der Stand gilt als +lokal.")
    if check:
        findings = stamp.check_freshness(documents, version, Path(out_dir))
        if not findings:
            print(f"Druckmaterial aktuell: {version.text} ({len(documents)} Dokument(e) in {out_dir})")
            return 0
        for finding in findings:
            print(f"STALE {finding}")
        print(f"{len(findings)} veraltet.")
        print("Reihenfolge: Eingaben committen, `uv run planspiel print` ausführen, final_documents/generated/ committen.")
        return 1
    print(f"Stand: {version.text}")
    try:
        pdfs = texbuild.build_documents(
            documents, Path(print_dir), Path(build_dir), stamp_tex=stamp.stamp_tex(version.text), assets=assets
        )
    except (texbuild.TexBuildError, ValueError, OSError) as error:
        print(f"ERROR print.tex {error}")
        print("1 Fehler")
        return 1
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    previously_published = stamp.previous_pdf_names(target)
    published = {}
    for job in sorted(pdfs):
        published[job] = target / f"{job}.pdf"
        try:
            shutil.copyfile(pdfs[job], published[job])
        except OSError as error:  # e.g. the PDF is open in a viewer on Windows
            print(f"ERROR print.publish {published[job]} lässt sich nicht schreiben (in einem Programm geöffnet?): {error}")
            print("1 Fehler")
            return 1
        print(f"{published[job]}")
    keep = {path.name for path in published.values()}
    for name in sorted(previously_published - keep):  # only files this pipeline wrote earlier
        old = target / name
        if old.is_file():
            try:
                old.unlink()
            except OSError as error:
                print(f"ERROR print.publish {old} lässt sich nicht entfernen (in einem Programm geöffnet?): {error}")
                print("1 Fehler")
                return 1
            print(f"Entfernt (nicht mehr im Druckumfang): {old}")
    stamp.write_manifest(target, version, documents, published)
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
    referenz_parser = subparsers.add_parser(
        "referenzpfade",
        help="Schlägt je Tier typische, legale Spielpfade (Start, Kurswechsel-Tausch, freiwilliger Zug) für die "
        "Lösungsschlüssel vor.",
    )
    referenz_parser.add_argument(
        "--config", default="simulation_config.json", help="Pfad zur Konfigurationsdatei."
    )
    referenz_parser.add_argument(
        "--tier",
        action="append",
        default=None,
        help="Budget-Tier (wiederholbar, Standard: alle Tiers der Konfiguration).",
    )
    referenz_parser.add_argument(
        "--median",
        type=int,
        default=None,
        help="End-KZ-Median im Budget statt des Tausch-Schicht-Medians (spart je Tier etwa vier Minuten).",
    )
    referenz_parser.add_argument(
        "--out", default=None, help="Verzeichnis für referenzpfade_<tier>.txt (Standard: nur ausgeben)."
    )
    referenz_parser.add_argument(
        "--starts", type=int, default=40, help="Anzahl der Startauswahlen, die ausgebaut werden (Standard: 40)."
    )
    referenz_parser.add_argument(
        "--keep", type=int, default=3, help="Anzahl der Kandidaten je Tier (Standard: 3)."
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
    gate_parser.add_argument(
        "--paths",
        action="store_true",
        help="prüft zusätzlich Spielpfade: Tausch-Schicht, Tausch mit einem Zug im Fenster nach Welle 2 und, wo kein "
        "Tausch möglich ist, je ein Zug im Fenster nach Welle 1 oder 2",
    )
    gate_parser.add_argument(
        "--narrow",
        action="store_true",
        help="zeigt zusätzlich die enge Kürzung (gleiches Tauschpaar) als Diagnose (nur mit --paths)",
    )
    gate_parser.add_argument(
        "--jobs", type=int, default=1, help="Anzahl der Prozesse für --paths, höchstens ein Prozess je Tier."
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
    print_parser.add_argument(
        "--check",
        action="store_true",
        help="prüft ohne TeX, ob die PDFs in --out-dir zum aktuellen Stand passen "
        "(Exit 0 aktuell, 1 veraltet, 2 Umgebungsfehler).",
    )
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "print":
        return _print_command(
            args.config, args.content_dir, args.print_dir, args.out_dir, args.build_dir, args.check
        )
    if args.command == "texts":
        return _texts_command(args.config, args.content_dir)
    if args.command == "clues":
        return _clues_command(args.config, args.content_dir)
    if args.command == "tausch":
        return _tausch_command(parser, args.config, args.tier, args.summary_dir)
    if args.command == "referenzpfade":
        return _referenzpfade_command(
            parser, args.config, args.tier, args.median, args.out, args.starts, args.keep
        )
    if args.command == "gate":
        return _gate_command(parser, args.config, args.tier, args.paths, args.narrow, args.jobs)
    return _validate_command(args.config, args.strict)
