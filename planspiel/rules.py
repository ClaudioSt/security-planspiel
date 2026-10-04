from fractions import Fraction
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

from planspiel.config import Attack, BudgetTier, Config, Event, Measure, Wave
from planspiel.rounding import round_half_away_frac, started_steps


def _requirements_met(measure: Measure, level: int, selection: Dict[str, int]) -> bool:
    for dependency in measure.dependencies:
        if level >= dependency["level"]:
            for req in dependency["requires"]:
                if selection.get(req["measure"], 0) < req["min_level"]:
                    return False
    return True


def dependencies_satisfied(selection: Dict[str, int], measures: Dict[str, Measure]) -> bool:
    return all(_requirements_met(measures[measure_id], level, selection) for measure_id, level in selection.items())


def compute_cia(selection: Dict[str, int], measures: Dict[str, Measure], base_cia: Dict[str, int]) -> Dict[str, int]:
    totals = {"c": base_cia.get("c", 0), "i": base_cia.get("i", 0), "a": base_cia.get("a", 0)}
    for measure_id, level in selection.items():
        level_data = measures[measure_id].levels[level]
        for key in totals:
            totals[key] += level_data.cia[key]
    return totals


def compute_costs(selection: Dict[str, int], measures: Dict[str, Measure], wave_count: int) -> Tuple[int, int, int]:
    init = 0
    opex_per_wave = 0
    for measure_id, level in selection.items():
        level_data = measures[measure_id].levels[level]
        init += level_data.init
        opex_per_wave += level_data.opex
    total = init + opex_per_wave * wave_count
    return init, opex_per_wave, total


def security_spend(init: int, opex_by_wave: Sequence[int], window_costs: Sequence[int] = ()) -> int:
    """Eigene Sicherheitsausgaben für den RoS: Init, OPEX je Welle, Init-Differenzen im Change-Fenster inkl. Kurswechsel-Differenz; keine Event-Effekte."""
    return init + sum(opex_by_wave) + sum(window_costs)


def compute_recovery(selection: Dict[str, int], measures: Dict[str, Measure]) -> Fraction:
    recovery = Fraction(0)
    for measure_id, level in selection.items():
        recovery = max(recovery, measures[measure_id].levels[level].recovery)
    return recovery


def _to_int(value) -> int:
    if value.denominator != 1:
        raise ValueError(f"expected an integral value, got {value}")
    return int(value)


def e_value_scaled(cia: Dict[str, int], weights: Dict[str, Fraction], ws: int) -> int:
    """E-Wert mal ws als ganze Zahl (ws = kgV der Gewichts-Nenner, integral by construction)."""
    return _to_int(cia["c"] * weights["c"] * ws + cia["i"] * weights["i"] * ws + cia["a"] * weights["a"] * ws)


def reduction_above_threshold_scaled(
    e_scaled: int, bonus: int, e_threshold: int, mitigation_cap: int, ws: int
) -> int:
    return min(mitigation_cap * ws, max(0, e_scaled + bonus * ws - e_threshold * ws))


def severity_scaled(base_severity: int, severity_multiplier: Fraction, reduction_scaled: int, ws: int) -> int:
    return max(0, _to_int(base_severity * severity_multiplier * ws) - reduction_scaled)


def damage_euros(severity_scaled: int, s_unit: int, recovery_scaled: int, ws: int, rs: int) -> int:
    """Schaden in ganzen Euro; severity_scaled ist mal ws, recovery_scaled mal rs skaliert."""
    quotient, remainder = divmod(severity_scaled * s_unit * 1000 * (rs - recovery_scaled), ws * rs)
    if remainder:
        raise ValueError("damage is not a whole number of euros")
    return quotient


def clamp_kz(value: int) -> int:
    return max(0, min(100, value))


def compute_bonus_reduction(
    wave: Wave,
    selection: Dict[str, int],
) -> Tuple[int, List[str]]:
    """Bonus reduction from specific measures (per Angriffs-Arbeitsblatt: 'Gesamtbonus')."""
    bonus_reduction = 0
    bonus_descriptions = []
    for bm in wave.bonus_measures:
        if selection.get(bm.measure, 0) >= bm.min_level:
            bonus_reduction += bm.bonus
            bonus_descriptions.append(bm.description)

    return bonus_reduction, bonus_descriptions


def kz_slope(kz_at_full_damage, kz_at_full_mitigation, mitigation_cap) -> Fraction:
    return (Fraction(kz_at_full_mitigation) - Fraction(kz_at_full_damage)) / mitigation_cap


def attack_kz_delta(kz_at_full_damage, slope: Fraction, reduction_scaled: int, ws: int) -> Fraction:
    # KZ-Delta linear zwischen den auf dem Arbeitsblatt festgelegten Endpunkten
    # interpoliert (Fall 1: redu=0 -> kz_at_full_damage, Fall 2: redu=cap ->
    # kz_at_full_mitigation), statt der im Word-Dokument widersprüchlichen
    # Fall-3-Subformel (deren Steigung bei Welle 2/3 nicht zu den eigenen
    # Fall-1/Fall-2-Werten passt).
    return kz_at_full_damage + slope * Fraction(reduction_scaled, ws)


def wave_kz_change(attack_kz_delta, event_kz) -> int:
    """Einziger Rundungspunkt: KZ-Änderung der Welle (Angriff + Events), ab ,5 vom Betrag aufrunden."""
    return round_half_away_frac(attack_kz_delta + Fraction(event_kz))


def apply_attack(
    selection: Dict[str, int],
    measures: Dict[str, Measure],
    attack: Attack,
    wave: Wave,
    cia: Dict[str, int],
    ws: int,
    rs: int,
    severity_multiplier: Fraction = Fraction(1),
) -> Dict:
    """
    Apply an attack exactly as specified on the printed Angriffs-Arbeitsblatt
    (z.B. Angriff-1_Ransomware.docx):

        Gesamtreduktion = E-Wert + Gesamtbonus
        Fall 1: Gesamtreduktion <= e_threshold              -> volle Basisschadenswirkung
        Fall 2: Gesamtreduktion >= e_threshold + mitigation_cap -> kein Schaden
        Fall 3: dazwischen                                  -> lineare Interpolation

    No flooring/division is applied to E-Wert or Gesamtreduktion - the formula
    matches the paper worksheet number-for-number. All values are exact: integers
    scaled by ws (weights) and rs (recovery); damage is whole euros.
    """
    e_scaled = e_value_scaled(cia, wave.weights, ws)
    e_value = Fraction(e_scaled, ws)
    bonus_reduction, bonus_descriptions = compute_bonus_reduction(wave, selection)

    gesamtreduktion = e_value + bonus_reduction
    reduction_scaled = reduction_above_threshold_scaled(
        e_scaled, bonus_reduction, wave.e_threshold, attack.mitigation_cap, ws
    )
    reduktion_ueber_schwelle = Fraction(reduction_scaled, ws)

    # Apply severity multiplier (larger companies are bigger targets)
    effective_base_severity = attack.base_severity * severity_multiplier
    severity_s = severity_scaled(attack.base_severity, severity_multiplier, reduction_scaled, ws)
    severity = Fraction(severity_s, ws)

    slope = kz_slope(attack.kz_at_full_damage, attack.kz_at_full_mitigation, attack.mitigation_cap)
    kz_delta = attack_kz_delta(attack.kz_at_full_damage, slope, reduction_scaled, ws)
    cia_delta = {key: severity * impact for key, impact in attack.cia_impact.items()}

    recovery_factor = Fraction(0)
    if attack.allow_recovery:
        recovery_factor = compute_recovery(selection, measures)
    damage = Fraction(damage_euros(severity_s, attack.s_unit, _to_int(recovery_factor * rs), ws, rs), 1000)

    return {
        "e_value": e_value,
        "bonus_reduction": bonus_reduction,
        "bonus_descriptions": bonus_descriptions,
        "gesamtreduktion": gesamtreduktion,
        "capped_reduction": reduktion_ueber_schwelle,
        "effective_base_severity": effective_base_severity,
        "severity": severity,
        "damage": damage,
        "kz_delta": kz_delta,
        "cia_delta": cia_delta,
        "recovery_factor": recovery_factor,
    }


def count_measures_at_level(selection: Dict[str, int], min_level: int) -> int:
    """Count how many measures are at or above the specified level."""
    return sum(1 for level in selection.values() if level >= min_level)


def _tier_lookup(value: float, tiers: List[List[float]]) -> float:
    """
    tiers: list of [min_inclusive, value], sorted ascending by min_inclusive.
    Returns the value of the highest tier whose min_inclusive <= value.
    Werte unterhalb des ersten Minimums sind kein gültiger Eingang und lösen ValueError aus.
    """
    if value < tiers[0][0]:
        raise ValueError(f"Wert {value} liegt unter dem ersten Stufenminimum {tiers[0][0]}")
    result = tiers[0][1]
    for min_inclusive, tier_value in tiers:
        if value >= min_inclusive:
            result = tier_value
    return result


def budget_review_delta(remaining: float, tiers: List[List[float]], kz_per_step: int, step: int) -> int:
    """KZ-Änderung des Budget Reviews aus dem Restbudget (k€).

    Druckbare Regel: Restbudget >= 0 -> Bonus nach Stufentabelle; Restbudget < 0 ->
    "je angefangene Schrittweite Überziehung −X KZ". Die Schrittweite step ist in k€ wie
    das Budget-Ledger und wird explizit an started_steps gegeben.
    """
    if remaining < 0:
        return -kz_per_step * started_steps(-remaining, step)
    return _tier_lookup(remaining, tiers)


def penalty_params(final_events: List[Event]) -> Tuple[int, int]:
    """(kz_per_step, step in k€) des ersten Budget-Review-Events."""
    for event in final_events:
        if event.type == "final_budget_tier":
            penalty = event.params["overspend_penalty"]
            return penalty["kz_per_step"], penalty["step"]
    raise ValueError("Kein final_budget_tier-Event in final_events")


def swap_possible(selection: Dict[str, int]) -> bool:
    """Kurswechsel (D-22): ein Maßnahmentausch ist nur möglich, wenn in der Kurswechsel-Welle
    mindestens eine Maßnahme aktiv und mindestens eine inaktiv ist."""
    levels = selection.values()
    return any(level > 0 for level in levels) and any(level == 0 for level in levels)


def swap_legal(wave1: Dict[str, int], window_end: Dict[str, int], dropped: str, incoming: str) -> bool:
    """Maßnahmentausch (D-09, D-23, D-28): die wegfallende Maßnahme war in der Kurswechsel-Welle aktiv und
    endet auf Level 0; die neue war dort inaktiv und ist am Fensterende aktiv (kein Kündigen und Wiederaufnehmen)."""
    return (
        dropped != incoming
        and wave1[dropped] > 0
        and window_end[dropped] == 0
        and wave1[incoming] == 0
        and window_end[incoming] > 0
    )


def swap_credit(
    measures: Dict[str, Measure], wave1: Dict[str, int], dropped: str, incoming: str, window_end: Dict[str, int]
) -> int:
    """Kurswechsel-Gutschrift (D-11, D-23): Init der wegfallenden Maßnahme auf ihrem Level der Kurswechsel-Welle,
    höchstens die Init-Kosten der neuen Maßnahme; das Team zahlt max(0, Init neu − Init weg), nie eine Erstattung."""
    return min(
        measures[dropped].levels[wave1[dropped]].init,
        measures[incoming].levels[window_end[incoming]].init,
    )


def swap_repair(selection: Dict[str, int], dropped: str, measures: Dict[str, Measure]) -> Dict[str, int]:
    """Kanonische Reparatur (D-28): die wegfallende Maßnahme auf 0, dann jede Maßnahme auf das höchste Level
    senken, dessen Abhängigkeiten erfüllt sind, bis sich nichts mehr ändert."""
    repaired = dict(selection)
    repaired[dropped] = 0
    changed = True
    while changed:
        changed = False
        for measure_id in measures:
            level = repaired.get(measure_id, 0)
            while level > 0 and not _requirements_met(measures[measure_id], level, repaired):
                level -= 1
            if level != repaired.get(measure_id, 0):
                repaired[measure_id] = level
                changed = True
    return repaired


def kurswechsel_wave(events: Dict[int, List[Event]]) -> Optional[int]:
    """Wellen-ID, deren Events den Kurswechsel enthalten; None ohne Kurswechsel."""
    for wave_id in sorted(events):
        if any(event.type == "kurswechsel" for event in events[wave_id]):
            return wave_id
    return None


def evaluate_event(
    event: Event,
    selection: Dict[str, int],
    remaining_budget: Optional[float] = None,
) -> Tuple[int, int, int, str]:
    """
    Evaluate a single event exactly as specified on Events_Security-Game.pptx.

    Returns: (kz_delta, opex_delta, budget_delta, effect_description)
    """
    p = event.params

    if event.type == "kurswechsel":
        # Pflicht-Maßnahmentausch im Change-Fenster danach (D-13): wird vom Pfadmodell angewendet,
        # im statischen Referenzplan ohne Change-Fenster-Züge hat das Event keine Wirkung.
        return 0, 0, 0, "Kurswechsel: Pflicht-Maßnahmentausch im folgenden Change-Fenster (im Referenzplan ohne Change-Fenster-Züge nicht angewendet)"

    if event.type == "flat_budget":
        return 0, 0, p["budget_delta"], event.description

    if event.type == "opex_discount_per_active_measure":
        active = count_measures_at_level(selection, 1)
        opex_delta = p["opex_per_measure"] * active
        return 0, opex_delta, 0, f"{active} aktive Maßnahmen x {p['opex_per_measure']}k€"

    if event.type == "checklist_tier":
        count = sum(
            1 for m in p["measures"]
            if selection.get(m, 0) >= p["min_level"]
        )
        kz_delta = _tier_lookup(count, p["tiers"])
        return kz_delta, 0, 0, f"{count}/{len(p['measures'])} Maßnahmen erfüllt"

    if event.type == "measure_level_tier":
        level = selection.get(p["measure"], 0)
        kz_delta = p["tiers"][str(level)]
        return kz_delta, 0, 0, f"{p['measure']} auf Level {level}"

    if event.type == "level_bonus_per_measure":
        count = count_measures_at_level(selection, p["level"])
        kz_delta = count * p["kz_per_measure"]
        return kz_delta, 0, 0, f"{count} Maßnahmen auf Level {p['level']}"

    if event.type == "and_condition":
        all_met = all(
            (selection.get(c["measure"], 0) >= c["min_level"])
            if "min_level" in c
            else (selection.get(c["measure"], 0) == c["level_eq"])
            for c in p["clauses"]
        )
        kz_delta = p["kz_delta"] if all_met else 0
        return kz_delta, 0, 0, "Bedingung erfüllt" if all_met else "Bedingung nicht erfüllt"

    if event.type == "final_budget_tier":
        penalty = p["overspend_penalty"]
        kz_delta = budget_review_delta(remaining_budget, p["tiers"], penalty["kz_per_step"], penalty["step"])
        return kz_delta, 0, 0, f"Restbudget {remaining_budget:.0f}k€"

    raise ValueError(f"Unknown event type: {event.type}")


def apply_events(
    wave_id: int,
    selection: Dict[str, int],
    events: Dict[int, List[Event]],
) -> Tuple[int, int, int, List[Dict]]:
    """
    Apply events for a wave.

    Returns:
        kz_delta: Total KZ change from events
        budget_delta: Total budget change from events
        opex_delta: Total OPEX change from events
        event_results: List of event outcomes
    """
    kz_delta = 0
    budget_delta = 0
    opex_delta = 0
    event_results = []

    wave_events = events.get(wave_id, [])
    for event in wave_events:
        ev_kz, ev_opex, ev_budget, description = evaluate_event(event, selection)

        kz_delta += ev_kz
        budget_delta += ev_budget
        opex_delta += ev_opex

        event_results.append({
            "id": event.id,
            "name": event.name,
            "effect_description": description,
            "kz_delta": ev_kz,
            "budget_delta": ev_budget,
            "opex_delta": ev_opex,
        })

    return kz_delta, budget_delta, opex_delta, event_results


def simulate_waves(
    selections: Sequence[Dict[str, int]],
    budget_tier: BudgetTier,
    waves: List[Wave],
    attacks: Dict[str, Attack],
    measures: Dict[str, Measure],
    events: Dict[int, List[Event]],
    base_cia: Dict[str, int],
    kz_start: int,
    ws: int,
    rs: int,
) -> Dict:
    """Wellenschleife mit der je Welle geltenden Auswahl: CIA, Angriff, Recovery, Bonus und Events der Welle k
    nutzen selections[k]."""
    if len(selections) != len(waves):
        raise ValueError(f"{len(selections)} Auswahlen für {len(waves)} Wellen")
    kz = kz_start
    total_damage = 0
    total_event_opex = 0
    total_event_budget = 0
    cia_mali = {"c": 0, "i": 0, "a": 0}
    per_wave = []

    for wave, selection in zip(waves, selections):
        cia = compute_cia(selection, measures, base_cia)
        attack = attacks[wave.attack_id]

        # Apply attack with new E-Value based mitigation
        attack_result = apply_attack(
            selection, measures, attack, wave, cia, ws, rs,
            severity_multiplier=budget_tier.severity_multiplier
        )
        e_value = attack_result["e_value"]

        # Apply events
        event_kz, event_budget, event_opex, event_results = apply_events(
            wave.wave_id, selection, events
        )
        total_event_budget += event_budget
        total_event_opex += event_opex

        # KZ-Änderung der Welle einmal runden, dann begrenzen
        kz = clamp_kz(kz + wave_kz_change(attack_result["kz_delta"], event_kz))

        total_damage += attack_result["damage"]
        for key in cia_mali:
            cia_mali[key] += attack_result["cia_delta"][key]

        per_wave.append({
            "wave_id": wave.wave_id,
            "wave_name": wave.name,
            "attack": wave.attack_id,
            "cia": cia,
            "e_value": e_value,
            "bonus_reduction": attack_result["bonus_reduction"],
            "bonus_descriptions": attack_result["bonus_descriptions"],
            "gesamtreduktion": attack_result["gesamtreduktion"],
            "capped_reduction": attack_result["capped_reduction"],
            "severity": attack_result["severity"],
            "damage": attack_result["damage"],
            "kz_delta_attack": attack_result["kz_delta"],
            "events": event_results,
            "kz_after": kz,
        })

    return {
        "kz_final": kz,
        "total_damage": total_damage,
        "total_event_opex": total_event_opex,
        "total_event_budget": total_event_budget,
        "cia_mali": cia_mali,
        "waves": per_wave,
    }


def simulate_selection(
    selection: Dict[str, int],
    budget_tier: BudgetTier,
    waves: List[Wave],
    attacks: Dict[str, Attack],
    measures: Dict[str, Measure],
    events: Dict[int, List[Event]],
    base_cia: Dict[str, int],
    kz_start: int,
    ws: int,
    rs: int,
) -> Dict:
    return {
        "selection": selection,
        **simulate_waves(
            [selection] * len(waves), budget_tier, waves, attacks, measures, events, base_cia, kz_start, ws, rs
        ),
    }


def base_losses(waves: List[Wave], attacks: Dict[str, Attack]) -> int:
    total = 0
    for wave in waves:
        attack = attacks[wave.attack_id]
        total += attack.base_severity * attack.s_unit
    return total


def ros(base_losses: float, total_damage: float, own_spend: float) -> Optional[Fraction]:
    if own_spend == 0:
        return None
    avoided_losses = Fraction(base_losses) - total_damage
    return (avoided_losses - own_spend) / own_spend


def final_index(
    kz_final: int, ros: Optional[Fraction], weight_kz: Fraction = Fraction(1), weight_ros: Fraction = Fraction(1)
) -> Fraction:
    if ros is None:
        return weight_kz * kz_final
    return (weight_kz * kz_final) + (weight_ros * (ros * 100))


def over_budget(total_cost: float, budget_available: float) -> bool:
    return total_cost > budget_available


class BudgetLedger(NamedTuple):
    total_cost: int
    budget_available: int
    over_budget: bool
    remaining_budget: int
    security_spend: int


def budget_ledger(tier_budget: int, own_spend: int, event_opex: int, event_budget: int) -> BudgetLedger:
    total_cost = own_spend + event_opex
    budget_available = tier_budget + event_budget
    return BudgetLedger(
        total_cost=total_cost,
        budget_available=budget_available,
        over_budget=over_budget(total_cost, budget_available),
        remaining_budget=budget_available - total_cost,
        security_spend=own_spend,
    )


def apply_final_events(
    final_events: List[Event], selection: Dict[str, int], remaining_budget, kz: int
) -> Tuple[int, List[Dict]]:
    records = []
    for event in final_events:
        ev_kz, _, _, description = evaluate_event(event, selection, remaining_budget=remaining_budget)
        kz = clamp_kz(kz + ev_kz)
        records.append({
            "id": event.id,
            "name": event.name,
            "effect_description": description,
            "kz_delta": ev_kz,
        })
    return kz, records


def evaluate_plan(cfg: Config, tier_name: str, selection: Dict[str, int]) -> Dict:
    tier = cfg.budget_tiers[tier_name]
    init, opex_per_wave, _ = compute_costs(selection, cfg.measures, len(cfg.waves))
    own = security_spend(init, [opex_per_wave] * len(cfg.waves))
    outcome = simulate_selection(
        selection, tier, cfg.waves, cfg.attacks, cfg.measures, cfg.events, cfg.base_cia, tier.kz_start,
        cfg.ws, cfg.rs,
    )
    ledger = budget_ledger(tier.budget, own, outcome["total_event_opex"], outcome["total_event_budget"])

    outcome["kz_final"], outcome["final_events"] = apply_final_events(
        cfg.final_events, selection, ledger.remaining_budget, outcome["kz_final"]
    )

    outcome["costs"] = {
        "init": init,
        "opex_per_wave": opex_per_wave,
        "security_spend": ledger.security_spend,
        "total": ledger.total_cost,
        "event_opex": outcome["total_event_opex"],
        "event_budget": outcome["total_event_budget"],
        "budget_available": ledger.budget_available,
    }

    outcome["over_budget"] = ledger.over_budget
    outcome["ros"] = ros(base_losses(cfg.waves, cfg.attacks), outcome["total_damage"], ledger.security_spend)
    return outcome


class Window(NamedTuple):
    selection: Dict[str, int]
    swap: Optional[Tuple[str, str]] = None


class Path(NamedTuple):
    start: Dict[str, int]
    windows: Tuple[Window, ...] = ()


class PathError(ValueError):
    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason


def window_cost(
    measures: Dict[str, Measure],
    before: Dict[str, int],
    after: Dict[str, int],
    swap: Optional[Tuple[str, str]] = None,
) -> int:
    """Kosten eines Change-Fensters (D-02, D-03, D-27, D-11): nur die Netto-Änderung je Maßnahme im Fenster zählt,
    nie eine Erstattung; ein deklarierter Maßnahmentausch trägt die Kurswechsel-Gutschrift."""
    cost = 0
    for measure_id, measure in measures.items():
        gain = measure.levels[after.get(measure_id, 0)].init - measure.levels[before.get(measure_id, 0)].init
        cost += max(0, gain)
    if swap is not None:
        dropped, incoming = swap
        cost -= swap_credit(measures, before, dropped, incoming, after)
    return cost


def _checked_selection(cfg: Config, selection: Dict[str, int], where: str) -> None:
    if set(selection) != set(cfg.measures):
        raise PathError("unknown_measure", f"{where}: Die Maßnahmen-IDs passen nicht zur Konfiguration")
    for measure_id, level in selection.items():
        if level not in cfg.measures[measure_id].levels:
            raise PathError("level_range", f"{where}: Level {level} von {measure_id} ist nicht zulässig")
    if not dependencies_satisfied(selection, cfg.measures):
        raise PathError("dependencies", f"{where}: Abhängigkeiten nicht erfüllt")


def evaluate_path(cfg: Config, tier_name: str, path: Path, *, enforce_kurswechsel: bool = True) -> Dict:
    """Exakte Auswertung eines Spiels mit Change-Fenstern: Fenster i folgt auf Welle i+1, fehlende Fenster lassen
    die Auswahl unverändert. Init-Differenzen werden im Fenster gebucht, Wirkung und OPEX gelten ab der nächsten
    Welle (D-06); der Kurswechsel erzwingt genau einen Maßnahmentausch, außer der Plan ist ausgenommen (D-22)."""
    tier = cfg.budget_tiers[tier_name]
    wave_count = len(cfg.waves)
    if len(path.windows) > wave_count - 1:
        raise PathError("too_many_windows", f"{len(path.windows)} Fenster bei {wave_count} Wellen")

    _checked_selection(cfg, path.start, "Start")
    selections = [path.start]
    for number, window in enumerate(path.windows, start=1):
        _checked_selection(cfg, window.selection, f"Fenster {number}")
        selections.append(window.selection)
    while len(selections) < wave_count:
        selections.append(selections[-1])

    kurswechsel = kurswechsel_wave(cfg.events)
    swap_window = None if kurswechsel is None else [wave.wave_id for wave in cfg.waves].index(kurswechsel)

    window_costs = []
    windows = []
    for index, window in enumerate(path.windows):
        before = selections[index]
        swap = window.swap
        if swap is not None:
            if index != swap_window:
                raise PathError("swap_without_kurswechsel", f"Fenster {index + 1}: Kein Maßnahmentausch ohne Kurswechsel")
            dropped, incoming = swap
            if dropped not in before or incoming not in before:
                raise PathError("unknown_measure", f"Fenster {index + 1}: Tausch nennt eine unbekannte Maßnahme")
            if not swap_possible(before) or not swap_legal(before, window.selection, dropped, incoming):
                raise PathError("kurswechsel_illegal", f"Fenster {index + 1}: Der Maßnahmentausch ist nicht zulässig")
        cost = window_cost(cfg.measures, before, window.selection, swap)
        window_costs.append(cost)
        windows.append({"swap": swap, "cost": cost})

    if enforce_kurswechsel and swap_window is not None and swap_possible(selections[swap_window]):
        if swap_window >= len(path.windows) or path.windows[swap_window].swap is None:
            raise PathError("kurswechsel_missing", f"Fenster {swap_window + 1}: Der Pflicht-Maßnahmentausch fehlt")

    outcome = simulate_waves(
        selections, tier, cfg.waves, cfg.attacks, cfg.measures, cfg.events, cfg.base_cia, tier.kz_start,
        cfg.ws, cfg.rs,
    )
    init = compute_costs(path.start, cfg.measures, 1)[0]
    opex_by_wave = [compute_costs(selection, cfg.measures, 1)[1] for selection in selections]
    own = security_spend(init, opex_by_wave, window_costs)
    ledger = budget_ledger(tier.budget, own, outcome["total_event_opex"], outcome["total_event_budget"])
    kz_final, final_events = apply_final_events(
        cfg.final_events, selections[-1], ledger.remaining_budget, outcome["kz_final"]
    )

    return {
        "selections": selections,
        "windows": windows,
        "kz_pre_review": outcome["kz_final"],
        "kz_final": kz_final,
        "total_damage": outcome["total_damage"],
        "total_event_opex": outcome["total_event_opex"],
        "total_event_budget": outcome["total_event_budget"],
        "cia_mali": outcome["cia_mali"],
        "waves": outcome["waves"],
        "final_events": final_events,
        "costs": {
            "init": init,
            "window_costs": window_costs,
            "opex_by_wave": opex_by_wave,
            "security_spend": ledger.security_spend,
            "event_opex": outcome["total_event_opex"],
            "event_budget": outcome["total_event_budget"],
            "total": ledger.total_cost,
            "budget_available": ledger.budget_available,
            "remaining": ledger.remaining_budget,
        },
        "over_budget": ledger.over_budget,
        "ros": ros(base_losses(cfg.waves, cfg.attacks), outcome["total_damage"], ledger.security_spend),
    }


class CompactOutcome(NamedTuple):
    kz_final: int
    own_cost: int
    total_cost: int
    damage_eur: int
    event_opex: int
    event_budget: int
    over_budget: bool
    kz_after: Tuple[int, ...]
    kz_pre_review: int
    remaining: int


class TierKernel:
    """Lean per-tier evaluation: composes the shared primitives with memoization, no per-wave dict trees."""

    def __init__(self, cfg: Config, tier_name: str):
        self.cfg = cfg
        self.tier = cfg.budget_tiers[tier_name]
        self.wave_count = len(cfg.waves)
        self.wave_context = []
        for wave in cfg.waves:
            attack = cfg.attacks[wave.attack_id]
            slope = kz_slope(attack.kz_at_full_damage, attack.kz_at_full_mitigation, attack.mitigation_cap)
            self.wave_context.append((wave, attack, slope))
        self._e_scaled = {}
        self._attack = {}
        self._change = {}

    def evaluate(self, selection: Dict[str, int]) -> Optional[CompactOutcome]:
        cfg = self.cfg
        tier = self.tier
        if not dependencies_satisfied(selection, cfg.measures):
            return None
        init, opex_per_wave, _ = compute_costs(selection, cfg.measures, self.wave_count)
        own_cost = security_spend(init, (opex_per_wave,) * self.wave_count)
        cia = compute_cia(selection, cfg.measures, cfg.base_cia)
        recovery_scaled = _to_int(compute_recovery(selection, cfg.measures) * cfg.rs)

        kz = tier.kz_start
        damage_total = 0
        event_opex_total = 0
        event_budget_total = 0
        kz_after = []
        for index, (wave, attack, slope) in enumerate(self.wave_context):
            e_key = (index, cia["c"], cia["i"], cia["a"])
            e_scaled = self._e_scaled.get(e_key)
            if e_scaled is None:
                e_scaled = self._e_scaled[e_key] = e_value_scaled(cia, wave.weights, cfg.ws)

            bonus, _ = compute_bonus_reduction(wave, selection)
            reduction = reduction_above_threshold_scaled(
                e_scaled, bonus, wave.e_threshold, attack.mitigation_cap, cfg.ws
            )
            recovery = recovery_scaled if attack.allow_recovery else 0

            attack_key = (index, reduction, recovery)
            attack_result = self._attack.get(attack_key)
            if attack_result is None:
                severity = severity_scaled(attack.base_severity, tier.severity_multiplier, reduction, cfg.ws)
                attack_result = self._attack[attack_key] = (
                    damage_euros(severity, attack.s_unit, recovery, cfg.ws, cfg.rs),
                    attack_kz_delta(attack.kz_at_full_damage, slope, reduction, cfg.ws),
                )
            damage, attack_kz = attack_result

            event_kz, event_budget, event_opex, _ = apply_events(wave.wave_id, selection, cfg.events)

            change_key = (index, reduction, event_kz)
            change = self._change.get(change_key)
            if change is None:
                change = self._change[change_key] = wave_kz_change(attack_kz, event_kz)
            kz = clamp_kz(kz + change)

            damage_total += damage
            event_opex_total += event_opex
            event_budget_total += event_budget
            kz_after.append(kz)

        ledger = budget_ledger(tier.budget, own_cost, event_opex_total, event_budget_total)
        kz_final, _ = apply_final_events(cfg.final_events, selection, ledger.remaining_budget, kz)
        return CompactOutcome(
            kz_final=kz_final,
            own_cost=own_cost,
            total_cost=ledger.total_cost,
            damage_eur=damage_total,
            event_opex=event_opex_total,
            event_budget=event_budget_total,
            over_budget=ledger.over_budget,
            kz_after=tuple(kz_after),
            kz_pre_review=kz,
            remaining=ledger.remaining_budget,
        )
