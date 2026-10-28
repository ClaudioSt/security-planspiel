"""BAL-08 (D-10): "Das Spiel ist insgesamt belohnend" - ein vernünftiges, aber mittelmäßiges Team endet über dem
Start-KZ, und nach einer schwachen ersten Welle ist ein Comeback möglich.

Beide Kennzahlen sind reine Funktionen: der Median-Abstand liest die Perzentile der beiden Zusammenfassungen
(statische Schicht und legale Tausch-Schicht, nur Pläne im Budget, D-09); das Comeback liest die Start-Aggregate der
Tausch-Schicht (D-05: Comeback wird auf der Tausch-Schicht gemessen). Die KZ nach Welle 1 kommt ausschließlich aus
`TierTables.path_outcome`, nie aus einer nachgebauten Wellenformel.

Die Schwellen sind Vorschläge aus der Recherche (Q7) und werden am Checkpoint D-04 zur Abnahme vorgelegt.
"""
from fractions import Fraction
from typing import Dict, List, NamedTuple, Optional, Tuple

from planspiel.fmt import format_approx
from planspiel.report import nearest_rank

MEDIAN_MARGIN = 5
COMEBACK_DROP = 5
COMEBACK_GAIN = 10
COMEBACK_SHARE = Fraction(9, 10)

STATIC_LABEL = "statische Schicht"
LEGAL_LABEL = "legale Tausch-Schicht"


class ComebackResult(NamedTuple):
    hit: int
    with_continuation: int
    without_continuation: int
    share_gain: Optional[Fraction]
    share_above_start: Optional[Fraction]
    median_best: Optional[int]
    p90_best: Optional[int]


def _margin(summary: Dict) -> Optional[int]:
    p50 = summary["percentiles"]["in_budget"]["kz_final"]["p50"]
    return None if p50 is None else p50 - summary["kz_start"]


def median_margins(static_summary: Dict, swap_summary: Dict) -> Tuple[Optional[int], Optional[int]]:
    """(Median der End-KZ im Budget minus Start-KZ) auf der statischen und der legalen Schicht; None ohne Pläne im Budget."""
    return _margin(static_summary), _margin(swap_summary)


def comeback(tables, starts: Dict, drop: int = COMEBACK_DROP, gain: int = COMEBACK_GAIN) -> ComebackResult:
    """Treffer-Starts: gültige Starts, deren KZ nach Welle 1 höchstens Start-KZ minus drop beträgt. Mit Fortsetzung:
    Treffer-Starts mit mindestens einem legalen Pfad im Budget; deren bestes End-KZ (aus `starts["best_in_budget"]`)
    liefert den Anteil mit Start-KZ + gain oder mehr, den Anteil über dem Start-KZ sowie Median und p90 (nearest rank)."""
    kz_start = tables.tier.kz_start
    best_in_budget = starts["best_in_budget"]
    in_budget_paths = starts["in_budget_paths"]
    hit = 0
    bests: List[int] = []
    for state, valid in enumerate(tables.valid):
        if not valid:
            continue
        kz_after_one = tables.path_outcome((state,) * tables.wave_count, 0).kz_after[0]
        if kz_after_one > kz_start - drop:
            continue
        hit += 1
        if in_budget_paths[state] > 0:
            bests.append(best_in_budget[state])
    if not bests:
        return ComebackResult(hit, 0, hit, None, None, None, None)
    bests.sort()
    return ComebackResult(
        hit,
        len(bests),
        hit - len(bests),
        Fraction(sum(best >= kz_start + gain for best in bests), len(bests)),
        Fraction(sum(best > kz_start for best in bests), len(bests)),
        nearest_rank(bests, 50),
        nearest_rank(bests, 90),
    )


def rewarding_tier(cfg, tier: str, static_summary: Dict, swap_summary: Dict, tables, swap_layer: Dict) -> Dict:
    """Alle BAL-08-Kennzahlen eines Tiers."""
    static_margin, legal_margin = median_margins(static_summary, swap_summary)
    return {
        "tier": tier,
        "kz_start": cfg.budget_tiers[tier].kz_start,
        "static_margin": static_margin,
        "legal_margin": legal_margin,
        "comeback": comeback(tables, swap_layer["starts"]),
    }


def check_rewarding(blocks_by_tier: Dict[str, Dict]) -> List[str]:
    """Deutsche Fehlerzeilen; leer, wenn BAL-08 in jedem Tier erfüllt ist."""
    failures: List[str] = []
    for tier, block in blocks_by_tier.items():
        for label, margin in ((STATIC_LABEL, block["static_margin"]), (LEGAL_LABEL, block["legal_margin"])):
            if margin is None:
                failures.append(f"Tier {tier}: Auf der {label} gibt es keine Pläne im Budget, der Median fehlt")
            elif margin < MEDIAN_MARGIN:
                failures.append(
                    f"Tier {tier}: Der Median im Budget liegt auf der {label} nur {margin} KZ über dem Start-KZ "
                    f"(verlangt: mindestens {MEDIAN_MARGIN})"
                )
        result = block["comeback"]
        if result.hit and result.with_continuation == 0:
            failures.append(
                f"Tier {tier}: Comeback unmöglich: keiner der {result.hit} Starts mit mindestens {COMEBACK_DROP} KZ "
                f"Verlust nach Welle 1 hat eine Fortsetzung im Budget"
            )
        elif result.share_gain is not None and result.share_gain < COMEBACK_SHARE:
            failures.append(
                f"Tier {tier}: Comeback nach Welle 1 nur bei {format_approx(result.share_gain)} der Starts mit "
                f"Fortsetzung (Start-KZ + {COMEBACK_GAIN} erreichbar; verlangt: mindestens {format_approx(COMEBACK_SHARE)})"
            )
    return failures


def _margin_text(label: str, margin: Optional[int]) -> str:
    return f"{label} keine Pläne im Budget" if margin is None else f"{label} {margin:+d}"


def format_rewarding(blocks_by_tier: Dict[str, Dict]) -> str:
    """Deutscher Bericht je Tier: Median-Abstände und Comeback-Kennzahlen."""
    lines = []
    for tier, block in blocks_by_tier.items():
        lines.append(
            f"Tier {tier} (Start-KZ {block['kz_start']}): Median im Budget minus Start-KZ: "
            f"{_margin_text(STATIC_LABEL, block['static_margin'])}, {_margin_text(LEGAL_LABEL, block['legal_margin'])} "
            f"(verlangt: mindestens {MEDIAN_MARGIN})"
        )
        result = block["comeback"]
        if not result.hit:
            lines.append(f"  Comeback: kein Start verliert in Welle 1 mindestens {COMEBACK_DROP} KZ")
            continue
        line = (
            f"  Comeback: {result.hit} Starts mit mindestens {COMEBACK_DROP} KZ Verlust nach Welle 1, "
            f"{result.with_continuation} mit Fortsetzung im Budget, {result.without_continuation} ohne"
        )
        if result.share_gain is not None:
            line += (
                f"; Start-KZ + {COMEBACK_GAIN} erreichbar bei {format_approx(result.share_gain)} "
                f"(verlangt: mindestens {format_approx(COMEBACK_SHARE)}), über dem Start-KZ bei "
                f"{format_approx(result.share_above_start)}; bestes End-KZ Median {result.median_best}, "
                f"p90 {result.p90_best}"
            )
        lines.append(line)
    return "\n".join(lines)
