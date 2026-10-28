"""BAL-09 (D-07, D-11): "Ergebnisse bleiben kontrolliert" - Tiers sind vergleichbar, das beste Ergebnis liegt knapp
unter 100, und die Streuung je Tier bleibt in einem festen Bereich.

Alle Kriterien sind reine Funktionen über die Zusammenfassungen von `report.summarize_tier` (statische Schicht) und
`report.summarize_swap_layer` (legale Tausch-Schicht); es zählen nur Pläne im Budget (D-09). Jedes Kriterium hat eine
eigene Prüffunktion, damit ein Test jedes einzeln absichern kann und kein Kriterium ein anderes verdeckt.

Die Schwellen sind Vorschläge aus der Recherche (Q7) und werden am Checkpoint D-04 zur Abnahme vorgelegt.
"""
from typing import Callable, Dict, List, NamedTuple, Optional, Tuple

CORRIDOR_WIDTH = 6
BEST_MIN = 90
BEST_MAX = 98
IQR_MIN = 13
IQR_MAX = 21
IQR_TIER_DIFF = 4
P5_P95_MAX = 50
MEDIAN_START_MAX = 28

STATIC_LABEL = "statische Schicht"
LEGAL_LABEL = "legale Tausch-Schicht"


class TierSpread(NamedTuple):
    tier: str
    kz_start: int
    best_static: Optional[int]
    best_legal: Optional[int]
    median_static: Optional[int]
    median_legal: Optional[int]
    iqr_static: Optional[int]
    iqr_legal: Optional[int]
    p5_p95_static: Optional[int]
    p5_p95_legal: Optional[int]


def _best(summary: Optional[Dict]) -> Optional[int]:
    if summary is None:
        return None
    entry = summary["best"]["in_budget"]
    return None if entry is None else entry["kz_final"]


def _difference(summary: Optional[Dict], high: str, low: str) -> Optional[int]:
    if summary is None:
        return None
    ranks = summary["percentiles"]["in_budget"]["kz_final"]
    if ranks[high] is None or ranks[low] is None:
        return None
    return ranks[high] - ranks[low]


def _median(summary: Optional[Dict]) -> Optional[int]:
    return None if summary is None else summary["percentiles"]["in_budget"]["kz_final"]["p50"]


def tier_spread(static_summary: Dict, swap_summary: Optional[Dict] = None) -> TierSpread:
    """Kennzahlen eines Tiers; IQR = p75 - p25, Breite = p95 - p5; ohne Zusammenfassung (oder ohne Pläne im Budget)
    sind die betreffenden Felder None."""
    return TierSpread(
        static_summary["tier"],
        static_summary["kz_start"],
        _best(static_summary),
        _best(swap_summary),
        _median(static_summary),
        _median(swap_summary),
        _difference(static_summary, "p75", "p25"),
        _difference(swap_summary, "p75", "p25"),
        _difference(static_summary, "p95", "p5"),
        _difference(swap_summary, "p95", "p5"),
    )


Spreads = Dict[str, TierSpread]

# (Label im Dativ, Feldsuffix) je Schicht für die Kennzahlen best / median / iqr / p5_p95
_LAYERS: Tuple[Tuple[str, str], ...] = (("statischen Schicht", "static"), ("legalen Tausch-Schicht", "legal"))


def _values(spreads: Spreads, metric: str, suffix: str) -> List[Tuple[str, int]]:
    """(Tier, Wert) aller Tiers, für die die Kennzahl berechnet ist."""
    found = []
    for tier, entry in spreads.items():
        value = getattr(entry, f"{metric}_{suffix}")
        if value is not None:
            found.append((tier, value))
    return found


def _window(values: List[Tuple[str, int]]) -> Optional[Tuple[int, int, str, str]]:
    if len(values) < 2:
        return None
    low = min(values, key=lambda item: item[1])
    high = max(values, key=lambda item: item[1])
    return low[1], high[1], low[0], high[0]


def check_missing(spreads: Spreads) -> List[str]:
    """Die statische Schicht braucht Pläne im Budget; die legale Schicht darf fehlen (nicht berechnet)."""
    return [
        f"Tier {tier}: Auf der statischen Schicht gibt es keine Pläne im Budget, die Streuung ist nicht messbar"
        for tier, entry in spreads.items()
        if None in (entry.best_static, entry.median_static, entry.iqr_static, entry.p5_p95_static)
    ]


def check_corridor(spreads: Spreads) -> List[str]:
    """D-07: bestes und mittleres End-KZ im Budget liegen je Schicht in einem Korridor der Breite CORRIDOR_WIDTH."""
    failures: List[str] = []
    for metric, name in (("best", "Bestes End-KZ im Budget"), ("median", "Median der End-KZ im Budget")):
        for label, suffix in _LAYERS:
            window = _window(_values(spreads, metric, suffix))
            if window is None:
                continue
            low, high, low_tier, high_tier = window
            if high - low > CORRIDOR_WIDTH:
                failures.append(
                    f"{name} auf der {label}: Tiers liegen {high - low} KZ auseinander ({low_tier} {low}, "
                    f"{high_tier} {high}; erlaubt: höchstens {CORRIDOR_WIDTH})"
                )
    return failures


def check_best_band(spreads: Spreads) -> List[str]:
    """D-11: das beste End-KZ im Budget liegt je Tier und Schicht in [BEST_MIN, BEST_MAX], die Kappung bei 100 greift kaum."""
    failures: List[str] = []
    for label, suffix in _LAYERS:
        for tier, best in _values(spreads, "best", suffix):
            if not BEST_MIN <= best <= BEST_MAX:
                failures.append(
                    f"Tier {tier}: Bestes End-KZ im Budget auf der {label} ist {best} "
                    f"(erlaubt: {BEST_MIN} bis {BEST_MAX})"
                )
    return failures


def check_iqr(spreads: Spreads) -> List[str]:
    """Der Interquartilsabstand der End-KZ im Budget liegt je Tier in [IQR_MIN, IQR_MAX], die Tiers unterscheiden sich
    um höchstens IQR_TIER_DIFF."""
    failures: List[str] = []
    for label, suffix in _LAYERS:
        values = _values(spreads, "iqr", suffix)
        for tier, iqr in values:
            if not IQR_MIN <= iqr <= IQR_MAX:
                failures.append(
                    f"Tier {tier}: Interquartilsabstand der End-KZ im Budget auf der {label} ist {iqr} "
                    f"(erlaubt: {IQR_MIN} bis {IQR_MAX})"
                )
        window = _window(values)
        if window is not None and window[1] - window[0] > IQR_TIER_DIFF:
            low, high, low_tier, high_tier = window
            failures.append(
                f"Unterschied des Interquartilsabstands zwischen den Tiers auf der {label}: {high - low} "
                f"({low_tier} {low}, {high_tier} {high}; erlaubt: höchstens {IQR_TIER_DIFF})"
            )
    return failures


def check_width(spreads: Spreads) -> List[str]:
    """Die Breite p5 bis p95 der End-KZ im Budget ist je Tier und Schicht höchstens P5_P95_MAX."""
    failures: List[str] = []
    for label, suffix in _LAYERS:
        for tier, width in _values(spreads, "p5_p95", suffix):
            if width > P5_P95_MAX:
                failures.append(
                    f"Tier {tier}: Breite p5 bis p95 der End-KZ im Budget auf der {label} ist {width} "
                    f"(erlaubt: höchstens {P5_P95_MAX})"
                )
    return failures


def check_median_bound(spreads: Spreads) -> List[str]:
    """Der Median der End-KZ im Budget liegt höchstens MEDIAN_START_MAX über dem Start-KZ (kein Leicht-Modus)."""
    failures: List[str] = []
    for label, suffix in _LAYERS:
        for tier, median in _values(spreads, "median", suffix):
            margin = median - spreads[tier].kz_start
            if margin > MEDIAN_START_MAX:
                failures.append(
                    f"Tier {tier}: Median im Budget liegt auf der {label} {margin} KZ über dem Start-KZ "
                    f"(erlaubt: höchstens {MEDIAN_START_MAX})"
                )
    return failures


CRITERIA: Tuple[Callable[[Spreads], List[str]], ...] = (
    check_missing,
    check_corridor,
    check_best_band,
    check_iqr,
    check_width,
    check_median_bound,
)


def check_spread(spreads_by_tier: Spreads) -> List[str]:
    """Deutsche Fehlerzeilen aller Kriterien; leer, wenn BAL-09 in jedem Tier erfüllt ist."""
    failures: List[str] = []
    for criterion in CRITERIA:
        failures.extend(criterion(spreads_by_tier))
    return failures


def _cell(value: Optional[int]) -> str:
    return "nicht berechnet" if value is None else str(value)


def format_spread(spreads_by_tier: Spreads) -> str:
    """Deutsche Tabelle je Tier: Start-KZ, bestes End-KZ, Median, Interquartilsabstand, Breite p5 bis p95 (statisch / legal)."""
    lines = [
        f"Streuung der End-KZ im Budget (statisch = {STATIC_LABEL}, legal = {LEGAL_LABEL}); verlangt: bestes "
        f"{BEST_MIN} bis {BEST_MAX}, Korridor der Tiers höchstens {CORRIDOR_WIDTH}, Interquartilsabstand "
        f"{IQR_MIN} bis {IQR_MAX} (Unterschied höchstens {IQR_TIER_DIFF}), Breite p5 bis p95 höchstens {P5_P95_MAX}, "
        f"Median höchstens {MEDIAN_START_MAX} über Start"
    ]
    for tier, entry in spreads_by_tier.items():
        lines.append(
            f"Tier {tier} (Start-KZ {entry.kz_start}): "
            f"bestes {_cell(entry.best_static)} / {_cell(entry.best_legal)}, "
            f"Median {_cell(entry.median_static)} / {_cell(entry.median_legal)}, "
            f"Interquartilsabstand {_cell(entry.iqr_static)} / {_cell(entry.iqr_legal)}, "
            f"Breite p5 bis p95 {_cell(entry.p5_p95_static)} / {_cell(entry.p5_p95_legal)}"
        )
    return "\n".join(lines)
