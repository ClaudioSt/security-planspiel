import itertools
from array import array
from fractions import Fraction
from typing import Callable, Dict, Iterable, NamedTuple, Optional

from planspiel import rules

LEVEL_OPTIONS = (0, 1, 2, 3)

STORE_LAYOUT = (
    ("code_index", "I"),
    ("kz_final", "B"),
    ("own_cost", "H"),
    ("total_cost", "i"),
    ("damage_eur", "I"),
    ("over_budget", "B"),
    ("kz_pre_review", "B"),
    ("remaining", "h"),
)


class CompactRecord(NamedTuple):
    code_index: int
    kz_final: int
    own_cost: int
    ros: Optional[Fraction]
    damage_eur: int
    over_budget: bool
    total_cost: int
    kz_pre_review: int
    remaining: int


class ResultStore:
    """One 19-byte record per dependency-valid combination, integers only (D-17)."""

    def __init__(self, base_losses):
        assert array("I").itemsize >= 4
        self.base_losses = base_losses
        self._columns = {name: array(typecode) for name, typecode in STORE_LAYOUT}

    def append(self, code_index: int, outcome: "rules.CompactOutcome") -> None:
        columns = self._columns
        columns["code_index"].append(code_index)
        columns["kz_final"].append(outcome.kz_final)
        columns["own_cost"].append(outcome.own_cost)
        columns["total_cost"].append(outcome.total_cost)
        columns["damage_eur"].append(outcome.damage_eur)
        columns["over_budget"].append(1 if outcome.over_budget else 0)
        columns["kz_pre_review"].append(outcome.kz_pre_review)
        columns["remaining"].append(outcome.remaining)

    def __len__(self) -> int:
        return len(self._columns["code_index"])

    def column(self, name: str) -> array:
        return self._columns[name]

    def record(self, i: int) -> CompactRecord:
        columns = self._columns
        damage_eur = columns["damage_eur"][i]
        own_cost = columns["own_cost"][i]
        total_cost = columns["total_cost"][i]
        return CompactRecord(
            code_index=columns["code_index"][i],
            kz_final=columns["kz_final"][i],
            own_cost=own_cost,
            ros=rules.ros(self.base_losses, Fraction(damage_eur, 1000), own_cost),
            damage_eur=damage_eur,
            over_budget=bool(columns["over_budget"][i]),
            total_cost=total_cost,
            kz_pre_review=columns["kz_pre_review"][i],
            remaining=columns["remaining"][i],
        )

    @property
    def bytes_per_record(self) -> int:
        return sum(column.itemsize for column in self._columns.values())


def iter_selections(measure_ids: Iterable[str], level_options: Iterable[int]) -> Iterable[Dict[str, int]]:
    measure_list = list(measure_ids)
    for levels in itertools.product(level_options, repeat=len(measure_list)):
        yield {measure: level for measure, level in zip(measure_list, levels)}


def code_from_index(code_index: int, n_measures: int) -> str:
    base = len(LEVEL_OPTIONS)
    digits = []
    for _ in range(n_measures):
        code_index, digit = divmod(code_index, base)
        digits.append(str(digit))
    return "".join(reversed(digits))


def enumerate_tier(
    cfg, tier_name: str, on_outcome: Optional[Callable[[int, "rules.CompactOutcome"], None]] = None
) -> ResultStore:
    kernel = rules.TierKernel(cfg, tier_name)
    store = ResultStore(rules.base_losses(cfg.waves, cfg.attacks))
    for code_index, selection in enumerate(iter_selections(cfg.measure_ids, LEVEL_OPTIONS)):
        outcome = kernel.evaluate(selection)
        if outcome is None:
            continue
        store.append(code_index, outcome)
        if on_outcome is not None:
            on_outcome(code_index, outcome)
    return store


def enumerate_swap_layer(cfg, tier_name: str) -> Dict:
    """Tausch-Schicht (D-24): jeder gültige Plan der ersten Welle mit jedem legalen Kurswechsel-Tausch; Pläne ohne
    möglichen Tausch (D-22) zählen als statischer Pfad. Nur Zähler, KZ-Histogramme und je das beste Ergebnis im
    und über Budget werden gehalten."""
    tables = rules.TierTables(cfg, tier_name)
    prefix = tables.prefix_waves
    suffix = tables.wave_count - prefix
    histogram = ([0] * 101, [0] * 101)
    exempt_by_flag = [0, 0]
    swaps_by_flag = [0, 0]
    start_plans = 0
    last_start = -1
    best = [None, None]
    best_head = [None, None]
    grid = 4 ** len(tables.measure_ids)
    best_in_budget = array("b", [-1]) * grid
    worst_in_budget = array("b", [-1]) * grid
    in_budget_paths = array("I", [0]) * grid
    for start, end, dropped, incoming, level, cost in tables.swap_paths():
        outcome = tables.path_outcome((start,) * prefix + (end,) * suffix, cost)
        flag = 1 if outcome.over_budget else 0
        kz_final = outcome.kz_final
        histogram[flag][kz_final] += 1
        if not flag:
            in_budget_paths[start] += 1
            if kz_final > best_in_budget[start]:
                best_in_budget[start] = kz_final
            if worst_in_budget[start] < 0 or kz_final < worst_in_budget[start]:
                worst_in_budget[start] = kz_final
        if start != last_start:
            start_plans += 1
            last_start = start
        if dropped is None:
            exempt_by_flag[flag] += 1
        else:
            swaps_by_flag[flag] += 1
        head = (-kz_final, outcome.own_cost)
        if best_head[flag] is not None and head > best_head[flag]:
            continue
        key = head + (start, end, -1 if dropped is None else dropped, -1 if incoming is None else incoming)
        if best[flag] is None or key < best[flag][0]:
            best_head[flag] = head
            best[flag] = (key, {
                "start": start,
                "end": end,
                "dropped": dropped,
                "incoming": incoming,
                "level": level,
                "window_cost": cost,
                "outcome": outcome,
            })

    exempt_static = sum(exempt_by_flag)
    swap_count = sum(swaps_by_flag)
    return {
        "kurswechsel_wave": tables.kurswechsel_wave,
        "counts": {
            "start_plans": start_plans,
            "exempt_static": exempt_static,
            "swap_paths": swap_count,
            "legal_games": exempt_static + swap_count,
            "in_budget": exempt_by_flag[0] + swaps_by_flag[0],
            "over_budget": exempt_by_flag[1] + swaps_by_flag[1],
            "swap_in_budget": swaps_by_flag[0],
            "swap_over_budget": swaps_by_flag[1],
        },
        "histogram": {"in_budget": histogram[0], "over_budget": histogram[1]},
        "best": {
            "in_budget": None if best[0] is None else best[0][1],
            "over_budget": None if best[1] is None else best[1][1],
        },
        "starts": {
            "best_in_budget": best_in_budget,
            "worst_in_budget": worst_in_budget,
            "in_budget_paths": in_budget_paths,
        },
    }


def store_worker(config_path: str, tier_name: str) -> ResultStore:
    from pathlib import Path

    from planspiel.config import load_config

    return enumerate_tier(load_config(Path(config_path)), tier_name)


def swap_layer_worker(config_path: str, tier_name: str) -> Dict:
    from pathlib import Path

    from planspiel.config import load_config

    return enumerate_swap_layer(load_config(Path(config_path)), tier_name)
