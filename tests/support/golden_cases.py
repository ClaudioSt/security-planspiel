"""Deterministic selection of golden cases per tier (D-07, D-09, D-23).

Sample membership is stored in the golden files; this finder only runs when a file is bootstrapped.
Tag names are a contract: later plans look up `census:tie_w3:` and `census:wave_clamp_high` by tag.
"""
import random

from tests.support import harness

SEED = 20260930
REMAINING_BUDGET_TARGETS = (-1, 0, 24, 25, 49, 50, 74, 75)
RANDOM_SAMPLE_SIZE = 6
TIE_TOLERANCE = 1e-9


def _fmt(value) -> str:
    return str(int(value)) if float(value).is_integer() else str(value)


def _strategy_cases(cfg):
    from planspiel.balance import define_strategies

    for strategies in define_strategies().values():
        for strategy in strategies:
            yield harness.code_of(cfg, strategy.selection), f"strategy:{strategy.name}"


def _edge_cases(cfg):
    n = len(cfg.measures)
    yield "0" * n, "edge:empty"
    yield "1" * n, "edge:all_l1"
    yield "3" * n, "edge:all_l3"


def _dependency_cases(cfg, tier_name):
    ids = harness.measure_ids(cfg)
    for measure_id, measure in cfg.measures.items():
        for dependency in measure.dependencies:
            level = dependency["level"]
            for requirement in dependency["requires"]:
                required = requirement["measure"]
                for required_level in (requirement["min_level"] - 1, requirement["min_level"]):
                    if required_level < 0:
                        continue
                    selection = {m: 0 for m in ids}
                    selection[measure_id] = level
                    selection[required] = required_level
                    valid = harness.evaluate(cfg, tier_name, selection)["valid"]
                    state = "valid" if valid else "invalid"
                    yield (
                        harness.code_of(cfg, selection),
                        f"dep:{measure_id}={level},{required}={required_level}:{state}",
                    )


def _wave_totals(cfg, tier_name, record):
    prev_kz = cfg.budget_tiers[tier_name].kz_start
    for index, wave in enumerate(record["waves"]):
        event_kz = sum(event["kz_delta"] for event in wave["events"])
        total = wave["kz_delta_attack"] + event_kz
        yield index + 1, wave, event_kz, total, prev_kz + total
        prev_kz = wave["kz_after"]


def _census(cfg, tier_name):
    found = {}
    ties = {}
    valid_codes = []

    def hit(tag, code):
        found.setdefault(tag, code)

    for code in harness.iter_codes(cfg):
        record = harness.evaluate(cfg, tier_name, harness.selection_of(cfg, code))
        if not record["valid"]:
            continue
        valid_codes.append(code)

        if record["kz_final"] == 100:
            hit("census:final_kz_100", code)
        remaining = record["costs"]["budget_available"] - record["costs"]["total"]
        if remaining in REMAINING_BUDGET_TARGETS:
            hit(f"census:remaining_{remaining}", code)

        for number, wave, event_kz, total, pre_clamp in _wave_totals(cfg, tier_name, record):
            wave_cfg = cfg.waves[number - 1]
            cap = cfg.attacks[wave_cfg.attack_id].mitigation_cap
            if wave["gesamtreduktion"] == wave_cfg.e_threshold:
                hit(f"census:g_eq_threshold_w{number}", code)
            if wave["gesamtreduktion"] == wave_cfg.e_threshold + cap:
                hit(f"census:g_eq_threshold_plus_cap_w{number}", code)
            if pre_clamp > 100:
                hit("census:wave_clamp_high", code)
            if pre_clamp < 0:
                hit("census:wave_clamp_low", code)
            if abs(total % 1 - 0.5) < TIE_TOLERANCE:
                signature = (number, wave["bonus_reduction"], wave["e_value"])
                ties.setdefault(signature, (code, event_kz))

    return found, ties, valid_codes


def _ordered_census_tags(cfg, found, ties):
    waves = range(1, len(cfg.waves) + 1)
    order = [f"census:g_eq_threshold_w{n}" for n in waves]
    order += [f"census:g_eq_threshold_plus_cap_w{n}" for n in waves]
    order += ["census:final_kz_100", "census:wave_clamp_high", "census:wave_clamp_low"]
    order += [f"census:remaining_{v}" for v in REMAINING_BUDGET_TARGETS]
    for tag in order:
        if tag in found:
            yield found[tag], tag
    for (number, bonus, e_value), (code, event_kz) in sorted(ties.items()):
        yield code, f"census:tie_w{number}:{_fmt(bonus)}/{_fmt(e_value)}/{_fmt(event_kz)}"


def build_case_list(cfg, tier_name):
    cases = {}

    def add(code, tag):
        tags = cases.setdefault(code, [])
        if tag not in tags:
            tags.append(tag)

    for code, tag in _strategy_cases(cfg):
        add(code, tag)
    for code, tag in _edge_cases(cfg):
        add(code, tag)
    for code, tag in _dependency_cases(cfg, tier_name):
        add(code, tag)

    found, ties, valid_codes = _census(cfg, tier_name)
    for code, tag in _ordered_census_tags(cfg, found, ties):
        add(code, tag)

    for index, code in enumerate(random.Random(SEED).sample(valid_codes, RANDOM_SAMPLE_SIZE)):
        add(code, f"random:{index}")

    return [{"code": code, "tags": tags} for code, tags in cases.items()]
