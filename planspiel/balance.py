"""Konsolidierter Balance-Bericht (BAL-04): alle Prüfungen der Phase 6 in einem Lauf.

`build_balance_report` wertet eine Konfiguration samt Inhalten (Texte, Hinweise) vollständig aus: Verteilung mit Top-K
und Pareto-Front im Budget, Überziehungs-Gate, Handrechen-Prüfung, Final-Index-Gewicht, Entscheidungen (BAL-06),
Referenzstrategien und Hinweis-Zuordnung (BAL-07), Belohnung (BAL-08) und Streuung (BAL-09). Jeder Block trägt sein
eigenes Urteil und seine Fehlerzeilen; nicht berechnete Teile sind benannt und zählen nicht zum Gesamturteil. Mit einer
Basis-Konfiguration entsteht der Vorher-nachher-Vergleich für den Abnahme-Checkpoint (D-04).

Die Schicht `static` rechnet die statische Enumeration und das statische Gate (einige Minuten); `all` ergänzt die
Tausch-Schicht und alles, was von ihr abhängt. Das Pfad-Gate mit Kalibrierung von X kommt mit `paths=True` hinzu.
"""
import argparse
import dataclasses
import json
import sys
import time
import warnings
from fractions import Fraction
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from planspiel import choices, gate, parallel, rewarding, rules, spread, strategies
from planspiel.cli import configure_utf8_stdio
from planspiel.config import DEFAULT_CONFIG_PATH, load_config, read_raw_config
from planspiel.enumerate import store_worker, swap_layer_worker
from planspiel.fmt import format_approx
from planspiel.index_weights import KZ_SHARE_MAX, KZ_SHARE_MIN, final_index_block, format_final_index_block
from planspiel.report import (
    format_console,
    format_swap_console,
    summarize_swap_layer,
    summarize_tier,
)
from planspiel.rounding import exact_to_json
from planspiel.texts import CLUES_FILE, CONTENT_DIR, TEXTE_FILE, check_clues, load_clues, load_texts
from planspiel.validate import HandCalcWarning, validate

MISSING = "<missing>"
LAYERS = ("static", "all")
NOT_COMPUTED_SWAP = "nicht berechnet (nur mit --layers all)"
NOT_COMPUTED_PATHS = "nicht berechnet (nur mit --paths)"
SOURCE_CONFIG = "Konfiguration"
SOURCE_CANDIDATE = "Kandidat"
REPORT_JSON = "balance_report.json"
REPORT_TEXT = "balance_report.txt"
COMPARISON_NOTE = "Final-Index-Kennzahlen beider Spalten mit k der Kandidatenkonfiguration"

TIER_BLOCK_LABELS = {
    "distribution": "Verteilung",
    "gate": "Überziehungs-Gate",
    "choices": "Entscheidungen (BAL-06)",
    "strategies": "Referenzstrategien (BAL-07)",
    "rewarding": "Belohnung (BAL-08)",
    "spread_input": "Streuung",
}
CROSS_BLOCK_LABELS = {
    "spread": "Streuung (BAL-09)",
    "choices": "Entscheidungen zwischen den Tiers (BAL-06)",
    "final_index": "Final-Index",
    "hand_calc": "Handrechnung",
    "clue_mapping": "Hinweis-Zuordnung",
    "calibration": "Kalibrierung von X",
}


# ---------------------------------------------------------------------------------------------------------------
# blocks
# ---------------------------------------------------------------------------------------------------------------


def _checked(failures: List[str], data) -> Dict:
    return {"passed": not failures, "failures": failures, "data": data}


def _info(data) -> Dict:
    return {"passed": None, "failures": [], "data": data}


def _skipped(note: str) -> Dict:
    return {"passed": None, "failures": [], "data": None, "note": note}


def _gate_line(tier: str, label: str, result) -> str:
    return (
        f"Tier {tier}: Überziehungs-Gate ({label}): nötiges X (strikt) {result.min_x_strict}, "
        f"Konfiguration X = {result.config_x}; Pläne, die nicht strikt verlieren: {result.violations_at_config_x}, "
        f"nicht verlierbar: {result.unlosable}, nicht kürzbar: {result.untrimmable}"
    )


def _gate_block(tier: str, static, families: Optional[Dict]) -> Dict:
    failures = []
    if not static.passed:
        failures.append(_gate_line(tier, "statisch", static))
    for family, result in (families or {}).items():
        if family != gate.NARROW_FAMILY and not result.passed:
            failures.append(_gate_line(tier, gate.PATH_LABELS[family], result))
    return _checked(failures, {"static": static, "paths": families})


def _final_index_failure(block: Dict) -> List[str]:
    if block["passed"]:
        return []
    return [
        f"Gewicht KZ {_plain(block['weight_kz'])}, k = {_plain(block['weight_ros'])}, KZ-Anteil "
        f"{format_approx(block['kz_share'])} (Soll: Gewicht KZ gleich 1, Anteil {format_approx(KZ_SHARE_MIN)} bis "
        f"{format_approx(KZ_SHARE_MAX)}); aus den Daten empfohlenes k {block['k']}"
    ]


def _final_index_result(stores: Dict, weights, configured) -> Dict:
    try:
        block = final_index_block(stores, weights)
    except ValueError as error:
        return _checked([str(error)], None)
    block["configured_weights"] = {"weight_kz": configured.weight_kz, "weight_ros": configured.weight_ros}
    return _checked(_final_index_failure(block), block)


def _issue_rows(issues) -> List[Dict]:
    return [
        {"level": issue.level, "code": issue.code, "path": issue.path, "message": issue.message} for issue in issues
    ]


def _issue_block(issues) -> Dict:
    errors = [issue for issue in issues if issue.level == "error"]
    return _checked([f"{issue.code} {issue.path}: {issue.message}" for issue in errors], _issue_rows(issues))


def _calibration_block(calibration) -> Dict:
    failures = []
    if not calibration.calibrated:
        failures.append(
            f"X = {calibration.config_x} ist nicht kalibriert, empfohlen ist {calibration.recommended_x} "
            f"(Maximum + 1; bestimmend: Tier {calibration.binding_tier}, Familie {calibration.binding_family})"
        )
    if not calibration.within_target:
        failures.append(
            f"Das empfohlene X = {calibration.recommended_x} liegt über dem Ziel X <= {calibration.x_target}"
        )
    return _checked(failures, calibration)


def _tier_swap_blocks(cfg, tier, store, static_summary, swap_summary, swap_layer, clues) -> Dict[str, Dict]:
    """Blöcke eines Tiers, die von der Tausch-Schicht abhängen (BAL-06, BAL-07, BAL-08)."""
    tables = rules.TierTables(cfg, tier)
    choice_block = choices.choices_tier(cfg, tier, store, tables, swap_layer)
    reward_block = rewarding.rewarding_tier(cfg, tier, static_summary, swap_summary, tables, swap_layer)
    del tables
    strategy_block = strategies.strategies_tier(cfg, tier, store, swap_layer, clues)
    return {
        "choices": _checked(choices.check_choices({tier: choice_block}), choice_block),
        "strategies": _checked(list(strategy_block["failures"]), strategy_block),
        "rewarding": _checked(rewarding.check_rewarding({tier: reward_block}), reward_block),
    }


def build_balance_report(
    config_path,
    content_dir,
    tiers: Optional[List[str]] = None,
    layers: str = "static",
    paths: bool = False,
    jobs: int = 1,
    index_weights=None,
    log: Optional[Callable[[str], None]] = None,
) -> Dict:
    """Vollständiger Bericht für Konfiguration und Inhalte. Fehlerhafte Eingaben (ungültige Konfiguration, fehlende oder
    kaputte Texte und Hinweise) lösen eine Ausnahme aus, statt ein Teilurteil zu liefern (T-06-20).

    `index_weights` (FinalIndexWeights) ersetzt die Final-Index-Gewichte der Konfiguration in allen Kennzahlen, die auf dem
    Final-Index beruhen; die Gewichte der Konfiguration bleiben im Final-Index-Block als Information stehen."""
    if layers not in LAYERS:
        raise ValueError(f"Unbekannte Schicht '{layers}'. Verfügbar: {', '.join(LAYERS)}.")
    say = log or (lambda _message: None)
    config_path = Path(config_path)
    content_dir = Path(content_dir)
    raw = read_raw_config(config_path)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", HandCalcWarning)
        cfg = load_config(config_path)
    names = list(tiers) if tiers else list(cfg.budget_tiers)
    unknown = [name for name in names if name not in cfg.budget_tiers]
    if unknown:
        raise ValueError(f"Unbekanntes Budget-Tier '{unknown[0]}'. Verfügbar: {', '.join(cfg.budget_tiers)}.")
    texts = load_texts(content_dir / TEXTE_FILE)
    clues = load_clues(content_dir / CLUES_FILE)

    weights = cfg.final_index if index_weights is None else index_weights
    cfg_eval = cfg if index_weights is None else dataclasses.replace(cfg, final_index=index_weights)
    swap = layers == "all"

    say("Statische Enumeration")
    stores = parallel.map_tiers(store_worker, config_path, names, jobs)
    static_summaries = {tier: summarize_tier(cfg_eval, tier, stores[tier]) for tier in names}
    if paths:
        say("Statisches Gate und Pfad-Gate")
        gate_results = parallel.map_tiers(gate.paths_worker, config_path, names, jobs)
    else:
        say("Statisches Gate")
        gate_results = {tier: (gate.gate_tier(cfg, tier, stores[tier]), None) for tier in names}
    swap_layers: Dict[str, Dict] = {}
    swap_summaries: Dict[str, Dict] = {}
    if swap:
        say("Tausch-Schicht")
        swap_layers = parallel.map_tiers(swap_layer_worker, config_path, names, jobs)
        swap_summaries = {tier: summarize_swap_layer(cfg_eval, tier, swap_layers[tier]) for tier in names}

    tier_blocks: Dict[str, Dict[str, Dict]] = {}
    spreads = {}
    for tier in names:
        static_gate, families = gate_results[tier]
        spreads[tier] = spread.tier_spread(static_summaries[tier], swap_summaries.get(tier))
        blocks = {
            "distribution": _info({"static": static_summaries[tier], "legal": swap_summaries.get(tier)}),
            "gate": _gate_block(tier, static_gate, families),
        }
        if swap:
            say(f"Entscheidungen, Belohnung und Referenzstrategien: Tier {tier}")
            blocks.update(
                _tier_swap_blocks(
                    cfg_eval, tier, stores[tier], static_summaries[tier], swap_summaries[tier], swap_layers[tier], clues
                )
            )
        else:
            blocks.update({name: _skipped(NOT_COMPUTED_SWAP) for name in ("choices", "strategies", "rewarding")})
        blocks["spread_input"] = _info(spreads[tier])
        tier_blocks[tier] = {name: blocks[name] for name in TIER_BLOCK_LABELS}

    cross: Dict[str, Dict] = {"spread": _checked(spread.check_spread(spreads), spreads)}
    if swap:
        choice_blocks = {tier: tier_blocks[tier]["choices"]["data"] for tier in names}
        per_tier_lines = {line for tier in names for line in tier_blocks[tier]["choices"]["failures"]}
        cross_failures = [line for line in choices.check_choices(choice_blocks) if line not in per_tier_lines]
        cross["choices"] = _checked(
            cross_failures,
            choices.cross_tier_choices(choice_blocks, {tier: block["band"] for tier, block in choice_blocks.items()}),
        )
    else:
        cross["choices"] = _skipped(NOT_COMPUTED_SWAP)
    cross["final_index"] = _final_index_result(stores, weights, cfg.final_index)
    cross["hand_calc"] = _issue_block(validate(raw, hand_calc_level="error"))
    cross["clue_mapping"] = _issue_block(check_clues(cfg, texts, clues, require_mapping=True))
    if paths:
        cross["calibration"] = _calibration_block(
            gate.calibrate(
                {tier: gate_results[tier][0] for tier in names}, {tier: gate_results[tier][1] for tier in names}
            )
        )

    report = {
        "config": str(config_path),
        "content_dir": str(content_dir),
        "layers": layers,
        "paths": paths,
        "index_weights_source": SOURCE_CONFIG if index_weights is None else SOURCE_CANDIDATE,
        "final_index_weights": {"weight_kz": weights.weight_kz, "weight_ros": weights.weight_ros},
        "tiers": tier_blocks,
        "cross_tier": cross,
    }
    report["verdict"] = _verdict(report)
    return report


def _named_blocks(report: Dict) -> List[Tuple[str, Dict]]:
    named = []
    for tier, blocks in report["tiers"].items():
        for name, block in blocks.items():
            named.append((f"{TIER_BLOCK_LABELS[name]}, Tier {tier}", block))
    for name, block in report["cross_tier"].items():
        named.append((CROSS_BLOCK_LABELS[name], block))
    return named


def _verdict(report: Dict) -> Dict:
    checks = []
    failures = []
    for name, block in _named_blocks(report):
        if block["passed"] is None:
            continue
        checks.append({"name": name, "passed": block["passed"]})
        if not block["passed"]:
            failures.extend(f"{name.split(', Tier ')[0]}: {line}" for line in block["failures"])
    failed = sum(1 for check in checks if not check["passed"])
    return {"passed": failed == 0, "failed_checks": failed, "checks": checks, "failures": failures}


# ---------------------------------------------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------------------------------------------


def _jsonable(value):
    if isinstance(value, Fraction):
        return exact_to_json(value)
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, tuple) and hasattr(value, "_fields"):
        return {name: _jsonable(item) for name, item in value._asdict().items()}
    if isinstance(value, dict):
        return {_key_text(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return [_jsonable(item) for item in sorted(value)]
    if isinstance(value, (list, tuple)) or hasattr(value, "typecode"):
        return [_jsonable(item) for item in value]
    return str(value)


def _key_text(key) -> str:
    if isinstance(key, tuple):
        return ",".join(str(part) for part in key)
    return str(key)


def report_json(report: Dict) -> Dict:
    """JSON-fähige Form des Berichts (Brüche über `exact_to_json`, Tupel-Schlüssel als Text)."""
    return _jsonable(report)


# ---------------------------------------------------------------------------------------------------------------
# text report
# ---------------------------------------------------------------------------------------------------------------


def _plain(value) -> str:
    exact = Fraction(value)
    return str(exact.numerator) if exact.denominator == 1 else format_approx(exact)


def _result_line(block: Dict) -> str:
    if block["passed"] is None:
        return f"Ergebnis: {block.get('note', 'ohne Urteil')}"
    return "Ergebnis: bestanden" if block["passed"] else "Ergebnis: NICHT bestanden (Fehlerzeilen im Gesamturteil)"


def _section(title: str, body: str, block: Dict) -> List[str]:
    lines = ["", f"-- {title}"]
    lines.append(body if block["data"] is not None else block.get("note", "keine Daten"))
    lines.append(_result_line(block))
    return lines


def _format_tier(tier: str, blocks: Dict[str, Dict]) -> List[str]:
    lines = ["", "=" * 100, f"Tier {tier}", "=" * 100]
    distribution = blocks["distribution"]["data"]
    lines.append(format_console(distribution["static"]))
    lines.append("")
    if distribution["legal"] is None:
        lines.append(f"Tausch-Schicht: {NOT_COMPUTED_SWAP}")
    else:
        lines.append(format_swap_console(distribution["legal"]))

    gate_block = blocks["gate"]
    lines.extend(["", "-- Überziehungs-Gate", gate.format_gate_report(gate_block["data"]["static"])])
    families = gate_block["data"]["paths"]
    if families is None:
        lines.append(f"Pfad-Gate: {NOT_COMPUTED_PATHS}")
    else:
        lines.extend(gate.format_path_gate_report(result) for result in families.values())
    lines.append(_result_line(gate_block))

    for name, formatter in (
        ("choices", choices.format_choices),
        ("strategies", strategies.format_strategies),
        ("rewarding", rewarding.format_rewarding),
    ):
        block = blocks[name]
        body = "" if block["data"] is None else formatter({tier: block["data"]})
        lines.extend(_section(TIER_BLOCK_LABELS[name], body, block))
    return lines


def _format_cross(cross: Dict[str, Dict]) -> List[str]:
    lines = ["", "=" * 100, "Über alle Tiers", "=" * 100]
    lines.extend(_section(CROSS_BLOCK_LABELS["spread"], spread.format_spread(cross["spread"]["data"]), cross["spread"]))

    block = cross["choices"]
    body = ""
    if block["data"] is not None:
        body = "\n".join(
            [
                f"Tiers {first} und {second}: Jaccard-Ähnlichkeit der Bänder {format_approx(value)}"
                for (first, second), value in block["data"]["jaccard"].items()
            ]
            + [f"Tiers {first} und {second}: gleicher bester Plan" for first, second in block["data"]["same_best"]]
        )
    lines.extend(_section(CROSS_BLOCK_LABELS["choices"], body or "keine Auffälligkeiten", block))

    block = cross["final_index"]
    body = ""
    if block["data"] is not None:
        configured = block["data"]["configured_weights"]
        body = "\n".join(
            format_final_index_block(block["data"]).splitlines()[:-1]
            + [
                f"Gewichte der Konfigurationsdatei (Information): KZ {_plain(configured['weight_kz'])}, "
                f"k = {_plain(configured['weight_ros'])}"
            ]
        )
    lines.extend(_section(CROSS_BLOCK_LABELS["final_index"], body, block))

    for name in ("hand_calc", "clue_mapping"):
        block = cross[name]
        rows = [f"{row['level'].upper()} {row['code']} {row['path']}: {row['message']}" for row in block["data"]]
        lines.extend(_section(CROSS_BLOCK_LABELS[name], "\n".join(rows) or "keine Meldungen", block))

    if "calibration" in cross:
        block = cross["calibration"]
        lines.extend(_section(CROSS_BLOCK_LABELS["calibration"], gate.format_calibration(block["data"]), block))
    return lines


def format_balance_report(report: Dict) -> str:
    """Deutscher Bericht je Tier, dann die Blöcke über alle Tiers, die Liste der Prüfungen und das Gesamturteil."""
    weights = report["final_index_weights"]
    lines = [
        "Balance-Bericht",
        f"Konfiguration: {report['config']}",
        f"Inhalte: {report['content_dir']}",
        f"Schichten: {report['layers']}" + (", Pfad-Gate mit Kalibrierung" if report["paths"] else ""),
        f"Final-Index-Gewichte ({report['index_weights_source']}): KZ {_plain(weights['weight_kz'])}, "
        f"k = {_plain(weights['weight_ros'])}",
    ]
    for tier, blocks in report["tiers"].items():
        lines.extend(_format_tier(tier, blocks))
    lines.extend(_format_cross(report["cross_tier"]))

    verdict = report["verdict"]
    lines.extend(["", "=" * 100, "Prüfungen (nicht berechnete Teile zählen nicht zum Urteil)", "=" * 100])
    for check in verdict["checks"]:
        lines.append(f"  {'bestanden' if check['passed'] else 'NICHT bestanden':<16}{check['name']}")
    skipped = [name for name, block in _named_blocks(report) if block["passed"] is None and block["data"] is None]
    for name in skipped:
        lines.append(f"  {'nicht berechnet':<16}{name}")
    lines.append("")
    if verdict["passed"]:
        lines.append("Gesamturteil: alle berechneten Prüfungen bestanden")
    else:
        lines.append(f"Gesamturteil: {verdict['failed_checks']} Prüfung(en) nicht bestanden")
        lines.extend(f"  {failure}" for failure in verdict["failures"])
    return "\n".join(lines)


# ---------------------------------------------------------------------------------------------------------------
# config diff and comparison
# ---------------------------------------------------------------------------------------------------------------


def _same(old, new) -> bool:
    return isinstance(old, bool) == isinstance(new, bool) and old == new


def _diff(path: str, old, new, rows: List[Tuple[str, object, object]]) -> None:
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(set(old) | set(new), key=str):
            child = f"{path}.{key}" if path else str(key)
            if key not in new:
                rows.append((child, old[key], MISSING))
            elif key not in old:
                rows.append((child, MISSING, new[key]))
            else:
                _diff(child, old[key], new[key], rows)
    elif isinstance(old, list) and isinstance(new, list):
        for index in range(max(len(old), len(new))):
            child = f"{path}[{index}]"
            if index >= len(new):
                rows.append((child, old[index], MISSING))
            elif index >= len(old):
                rows.append((child, MISSING, new[index]))
            else:
                _diff(child, old[index], new[index], rows)
    elif not _same(old, new):
        rows.append((path, old, new))


def config_diff(old_raw: Dict, new_raw: Dict) -> List[Tuple[str, object, object]]:
    """Jeder geänderte Wert als (JSON-Pfad, alt, neu), nach Pfad sortiert; `MISSING` für fehlende Seiten."""
    rows: List[Tuple[str, object, object]] = []
    _diff("", old_raw, new_raw, rows)
    return sorted(rows, key=lambda row: row[0])


def _value_text(value) -> str:
    if value is MISSING or (isinstance(value, str) and value == MISSING):
        return "fehlt"
    if isinstance(value, (Fraction, int)) and not isinstance(value, bool):
        return str(exact_to_json(value))
    text = value if isinstance(value, str) else json.dumps(_jsonable(value), ensure_ascii=False)
    return text if len(text) <= 70 else text[:67] + "..."


def format_config_diff(rows: List[Tuple[str, object, object]]) -> str:
    if not rows:
        return "keine"
    return "\n".join(f"  {path}: {_value_text(old)} → {_value_text(new)}" for path, old, new in rows)


def _metrics(report: Dict) -> Dict[Tuple[str, str], object]:
    found: Dict[Tuple[str, str], object] = {}
    for tier, blocks in report["tiers"].items():
        static_gate = blocks["gate"]["data"]["static"]
        found[("Nötiges X (strikt), statisches Gate", tier)] = static_gate.min_x_strict
        for family, result in (blocks["gate"]["data"]["paths"] or {}).items():
            found[(f"Nötiges X (strikt), Pfade {family}", tier)] = result.min_x_strict

        distribution = blocks["distribution"]["data"]
        for label, summary in (("statische Schicht", distribution["static"]), ("legale Tausch-Schicht", distribution["legal"])):
            if summary is None:
                continue
            best = summary["best"]["in_budget"]
            found[(f"Bestes End-KZ im Budget, {label}", tier)] = None if best is None else best["kz_final"]
            found[(f"Median der End-KZ im Budget, {label}", tier)] = summary["percentiles"]["in_budget"]["kz_final"]["p50"]
        spread_input = blocks["spread_input"]["data"]
        found[("Interquartilsabstand der End-KZ im Budget, statische Schicht", tier)] = spread_input.iqr_static
        if distribution["legal"] is not None:
            found[("Interquartilsabstand der End-KZ im Budget, legale Tausch-Schicht", tier)] = spread_input.iqr_legal

        choice_block = blocks["choices"]["data"]
        if choice_block is not None:
            ids = choice_block["measure_ids"]
            shares = sorted(choice_block["band_shares"].items(), key=lambda item: (-item[1][0], item[0]))
            if shares:
                found[("Größter Band-Anteil (Level >= 1)", tier)] = shares[0][1][0]
                found[("Maßnahme des größten Band-Anteils", tier)] = ids[shares[0][0]]
            drops = sorted(choice_block["drops"].items(), key=lambda item: (-item[1], item[0]))
            if drops:
                found[("Größter Wegfall-Abfall der besten End-KZ", tier)] = drops[0][1]
                found[("Maßnahme des größten Wegfall-Abfalls", tier)] = ids[drops[0][0]]
        strategy_block = blocks["strategies"]["data"]
        if strategy_block is not None:
            for placement in strategy_block["placements"]:
                if not placement.legal:
                    continue
                found[(f"Strategie {placement.name} ({placement.kind}): Final-Index unter", tier)] = placement.fi_below
                found[(f"Strategie {placement.name} ({placement.kind}): KZ unter", tier)] = placement.kz_below
            found[("Anteil bester Pläne mit Maßnahme ohne Hinweis", tier)] = strategy_block["non_clue_share"]

    cross = report["cross_tier"]
    block = cross["final_index"]["data"]
    if block is not None:
        found[("KZ-Anteil bei dem verwendeten k", "-")] = block["kz_share"]
        found[("Empfohlenes k (aus den Daten)", "-")] = block["k"]
        found[("Konfiguriertes k der Konfigurationsdatei (nur zur Information)", "-")] = block["configured_weights"][
            "weight_ros"
        ]
    if "calibration" in cross:
        found[("Empfohlenes X (Maximum + 1)", "-")] = cross["calibration"]["data"].recommended_x
    return found


def compare_reports(old: Dict, new: Dict) -> List[Tuple[str, str, object, object]]:
    """Zeilen (Kennzahl, Tier, alt, neu) der Schlüsselkennzahlen beider Berichte; `None`, wo ein Bericht sie nicht hat."""
    old_metrics = _metrics(old)
    new_metrics = _metrics(new)
    keys = list(old_metrics) + [key for key in new_metrics if key not in old_metrics]
    return [(metric, tier, old_metrics.get((metric, tier)), new_metrics.get((metric, tier))) for metric, tier in keys]


def _cell(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "ja" if value else "nein"
    if isinstance(value, Fraction):
        return format_approx(value)
    return str(value)


def format_comparison(rows: List[Tuple[str, str, object, object]]) -> str:
    lines = [f"{'Kennzahl':<72}{'Tier':<8}{'vorher':>12}{'nachher':>12}"]
    for metric, tier, old, new in rows:
        lines.append(f"{metric:<72}{tier:<8}{_cell(old):>12}{_cell(new):>12}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------------------------------------------
# command line
# ---------------------------------------------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Konsolidierter Balance-Bericht: alle Prüfungen der Phase 6 für eine Konfiguration samt Inhalten. "
        "Exit 0 nur, wenn jede berechnete Prüfung besteht."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Pfad der Konfiguration (JSON).")
    parser.add_argument("--content-dir", default=str(CONTENT_DIR), help="Verzeichnis mit Texten und Hinweisen.")
    parser.add_argument(
        "--tier", action="append", default=None, help="Budget-Tier auswerten (wiederholbar; Standard: alle)."
    )
    parser.add_argument(
        "--layers",
        choices=LAYERS,
        default="static",
        help="static: statische Enumeration und statisches Gate; all: zusätzlich Tausch-Schicht und alles, was von ihr "
        "abhängt (Entscheidungen, Referenzstrategien, Belohnung).",
    )
    parser.add_argument(
        "--paths", action="store_true", help="Pfad-Gate und Kalibrierung von X berechnen (dauert deutlich länger)."
    )
    parser.add_argument("--jobs", type=int, default=1, help="Prozesse für die Tiers (höchstens einer je Tier).")
    parser.add_argument(
        "--out", default=None, help="Verzeichnis für balance_report.json und balance_report.txt (ohne Angabe: keine Dateien)."
    )
    parser.add_argument(
        "--baseline-config",
        default=None,
        help="Basis-Konfiguration für den Vorher-nachher-Vergleich (Konfigurationsänderungen und Kennzahlen).",
    )
    parser.add_argument(
        "--baseline-content-dir", default=str(CONTENT_DIR), help="Inhalte der Basis-Konfiguration."
    )
    return parser


def _write(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main(argv=None) -> int:
    configure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.jobs < 1:
        parser.error("--jobs muss mindestens 1 sein.")
    started = time.perf_counter()

    def log(message: str) -> None:
        print(f"[{time.perf_counter() - started:6.1f} s] {message}", file=sys.stderr, flush=True)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", HandCalcWarning)
            candidate = load_config(Path(args.config))
        unknown = [name for name in args.tier or [] if name not in candidate.budget_tiers]
        if unknown:
            parser.error(f"Unbekanntes Budget-Tier '{unknown[0]}'. Verfügbar: {', '.join(candidate.budget_tiers)}.")
        report = build_balance_report(
            args.config, args.content_dir, args.tier, args.layers, args.paths, args.jobs, log=log
        )
        baseline = None
        if args.baseline_config:
            log("Basis-Konfiguration")
            baseline = build_balance_report(
                args.baseline_config,
                args.baseline_content_dir,
                args.tier,
                args.layers,
                args.paths,
                args.jobs,
                index_weights=candidate.final_index,
                log=log,
            )
    except (OSError, ValueError) as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        return 2

    text = format_balance_report(report)
    rows = diff = None
    if baseline is not None:
        diff = config_diff(read_raw_config(Path(args.baseline_config)), read_raw_config(Path(args.config)))
        rows = compare_reports(baseline, report)
        text += "\n\n".join(
            [
                "",
                "Konfigurationsänderungen (alt → neu)\n" + format_config_diff(diff),
                f"Kennzahlen vorher → nachher\n{COMPARISON_NOTE}\n" + format_comparison(rows),
            ]
        )
    print(text)
    print()
    print(f"Laufzeit: {time.perf_counter() - started:.1f} s")

    if args.out:
        target = Path(args.out)
        target.mkdir(parents=True, exist_ok=True)
        data = report_json(report)
        if baseline is not None:
            data["config_diff"] = _jsonable([list(row) for row in diff])
            data["comparison"] = _jsonable([list(row) for row in rows])
        _write(target / REPORT_JSON, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        _write(target / REPORT_TEXT, text + "\n")
        print(f"Ausgabe: {target / REPORT_JSON}, {target / REPORT_TEXT}")
    return 0 if report["verdict"]["passed"] else 1
