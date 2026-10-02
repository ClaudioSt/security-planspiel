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
)


class CompactRecord(NamedTuple):
    code_index: int
    kz_final: int
    own_cost: int
    ros: Optional[Fraction]
    damage_eur: int
    over_budget: bool
    total_cost: int


class ResultStore:
    """One 16-byte record per dependency-valid combination, integers only (D-17)."""

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
