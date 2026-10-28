"""Messung des Final-Index-Gewichts k aus den Daten (BAL-03, D-15).

Der Final-Index ist KZ + k * RoS (RoS auf zwei Nachkommastellen). k wird so gewählt, dass die KZ etwa 2/3 und die RoS
etwa 1/3 der Streuung im Budget trägt. Als robustes Streuungsmaß dient der Interquartilsabstand (IQR, Nearest-Rank wie in
report.nearest_rank) über alle Kombinationen im Budget mit eigenen Kosten > 0, über die Stufen zusammengelegt.
"""
from collections import Counter
from fractions import Fraction
from typing import Dict, Iterable, List, Tuple

from planspiel import rules
from planspiel.rounding import round_half_away_frac

TARGET_KZ_SHARE = Fraction(2, 3)
KZ_SHARE_MIN = Fraction(3, 5)
KZ_SHARE_MAX = Fraction(73, 100)
K_STEP = 5


def _counted_nearest_rank(counts: Counter, p: int):
    total = sum(counts.values())
    rank = max(0, (p * total + 99) // 100 - 1)
    seen = 0
    for value in sorted(counts):
        seen += counts[value]
        if seen > rank:
            return value
    raise ValueError("Keine Kombinationen im Budget.")


def pooled_iqr(stores: Iterable) -> Tuple[int, Fraction]:
    kz_counts: Counter = Counter()
    ros_counts: Counter = Counter()
    for store in stores:
        kz_col = store.column("kz_final")
        own_col = store.column("own_cost")
        damage_col = store.column("damage_eur")
        over_col = store.column("over_budget")
        ros_cache: Dict[Tuple[int, int], Fraction] = {}
        for kz, own, damage, over in zip(kz_col, own_col, damage_col, over_col):
            if over or own == 0:
                continue
            kz_counts[kz] += 1
            key = (damage, own)
            if key not in ros_cache:
                ros_cache[key] = rules.ros(store.base_losses, Fraction(damage, 1000), own)
            ros_counts[ros_cache[key]] += 1
    iqr_kz = _counted_nearest_rank(kz_counts, 75) - _counted_nearest_rank(kz_counts, 25)
    iqr_ros = _counted_nearest_rank(ros_counts, 75) - _counted_nearest_rank(ros_counts, 25)
    return iqr_kz, iqr_ros


def kz_share(iqr_kz, iqr_ros, k) -> Fraction:
    total = Fraction(iqr_kz) + Fraction(k) * Fraction(iqr_ros)
    if total == 0:
        raise ValueError("Keine Streuung in KZ und RoS.")
    return Fraction(iqr_kz) / total


def recommended_k(iqr_kz, iqr_ros, target: Fraction = TARGET_KZ_SHARE, step: int = K_STEP) -> Tuple[Fraction, int]:
    if iqr_ros == 0:
        raise ValueError("Die RoS hat keine Streuung, k ist nicht bestimmbar.")
    k_raw = Fraction(iqr_kz) * (1 - target) / (target * Fraction(iqr_ros))
    return k_raw, round_half_away_frac(k_raw / step) * step


def final_index_block(stores_by_tier: Dict, weights) -> Dict:
    pooled_kz, pooled_ros = pooled_iqr(stores_by_tier.values())
    k_raw, k = recommended_k(pooled_kz, pooled_ros)
    tiers = {}
    for tier, store in stores_by_tier.items():
        iqr_kz, iqr_ros = pooled_iqr([store])
        tiers[tier] = {
            "iqr_kz": iqr_kz,
            "iqr_ros": iqr_ros,
            "kz_share": kz_share(iqr_kz, iqr_ros, weights.weight_ros),
        }
    share = kz_share(pooled_kz, pooled_ros, weights.weight_ros)
    return {
        "pooled": {"iqr_kz": pooled_kz, "iqr_ros": pooled_ros},
        "tiers": tiers,
        "k_raw": k_raw,
        "k": k,
        "weight_kz": weights.weight_kz,
        "weight_ros": weights.weight_ros,
        "kz_share": share,
        "passed": weights.weight_kz == 1 and KZ_SHARE_MIN <= share <= KZ_SHARE_MAX,
    }


def _decimal(value, digits: int = 2) -> str:
    return f"{float(value):.{digits}f}".replace(".", ",")


def format_final_index_block(block: Dict) -> str:
    lines: List[str] = ["Final-Index: Streuung (IQR) im Budget, Eigenkosten > 0"]
    pooled = block["pooled"]
    lines.append(f"  gesamt: IQR KZ {pooled['iqr_kz']}, IQR RoS {_decimal(pooled['iqr_ros'])}")
    for tier, values in block["tiers"].items():
        lines.append(
            f"  {tier}: IQR KZ {values['iqr_kz']}, IQR RoS {_decimal(values['iqr_ros'])}, "
            f"KZ-Anteil bei k = {_decimal(block['weight_ros'], 1)}: {_decimal(values['kz_share'])}"
        )
    lines.append(
        f"Konfiguriert: Gewicht KZ {_decimal(block['weight_kz'], 1)}, k = {_decimal(block['weight_ros'], 1)}, "
        f"KZ-Anteil {_decimal(block['kz_share'])} (Soll {_decimal(KZ_SHARE_MIN)} bis {_decimal(KZ_SHARE_MAX)})"
    )
    lines.append(f"Empfohlenes k: {block['k']} (roh {_decimal(block['k_raw'], 1)})")
    lines.append("Ergebnis: " + ("bestanden" if block["passed"] else "nicht bestanden"))
    return "\n".join(lines)
