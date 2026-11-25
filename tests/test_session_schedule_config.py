"""The session_schedule block: loader, validator, invisibility to the rules and the FLOW-02 product rules (D-01..D-04, D-19, D-22, D-27).

The block is read only by the facilitator print models and by the intro-deck test (`persons_per_team`). The product
rules (200 minutes since quick 261125-fsu, which dropped the joint practice wave; story block 35, debriefing 30 with stages 3/5/14/8; the D-02 order with a 25-minute wave 1 and 20-minute waves 2 and 3; 3 teams of 5) live here and not in the validator, so a future
schedule change is a deliberate test edit.
"""
import copy
import dataclasses
import json

import pytest

from planspiel import rules
from planspiel.config import DebriefStage, PrintRow, ScheduleBlock, SessionSchedule, load_config
from planspiel.validate import validate
from tests.support import CONFIG_PATH

D02_BLOCKS = (
    ("intro", 10), ("break_1", 5), ("story_groups", 35), ("measures_budget", 30), ("break_2", 15),
    ("wave_1", 25), ("wave_2", 20), ("wave_3", 20), ("closing", 10), ("debrief", 30),
)
PROPOSED_JOBS = (
    "angriff-1_ransomware", "angriff-2_ot", "angriff-3_exfil", "spieler-massnahmenkarten", "spieler-eventkarten",
    "spieler-teamheft", "spieler-so-funktioniert-eine-welle", "spieler-unternehmenssteckbrief",
    "spieler-zeitungsartikel", "spieler-anfrage-mail", "spieler-audit-mail", "uebung-welle-0",
    "spielleitung-uebersicht",
)


def _raw():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _errors(raw):
    return [issue for issue in validate(raw) if issue.level == "error"]


def _codes(raw):
    return [issue.code for issue in _errors(raw)]


def _load(raw, tmp_path, name="config.json"):
    target = tmp_path / name
    target.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    return load_config(target)


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


# --- loader ----------------------------------------------------------------------------------------------------


def test_the_real_config_carries_the_schedule(cfg):
    schedule = cfg.session_schedule
    assert isinstance(schedule, SessionSchedule)
    assert (schedule.total_minutes, schedule.teams, schedule.persons_per_team) == (200, 3, 5)
    assert all(isinstance(block, ScheduleBlock) for block in schedule.blocks)
    assert tuple((block.id, block.minutes) for block in schedule.blocks) == D02_BLOCKS
    assert [block.wave for block in schedule.blocks if block.wave is not None] == [1, 2, 3]
    assert {block.id: block.wave for block in schedule.blocks if block.wave is not None} == {
        "wave_1": 1, "wave_2": 2, "wave_3": 3,
    }


def test_the_print_list_holds_every_proposed_job_in_order(cfg):
    rows = cfg.session_schedule.print_list
    assert all(isinstance(row, PrintRow) for row in rows)
    jobs = [row.job for row in rows]
    positions = [jobs.index(job) for job in PROPOSED_JOBS]
    assert positions == sorted(positions)
    by_job = {row.job: row for row in rows}
    for job in PROPOSED_JOBS:
        if job.startswith("spielleitung-"):
            assert (by_job[job].per_team, by_job[job].facilitator) == (0, 1)
        else:
            assert (by_job[job].per_team, by_job[job].facilitator) == (1, 1)


def test_a_config_without_the_block_has_no_schedule(tmp_path):
    raw = _raw()
    del raw["session_schedule"]
    plain = _load(raw, tmp_path)
    assert plain.session_schedule is None
    assert _errors(raw) == []


def test_the_block_is_hashable_data(cfg):
    assert isinstance(cfg.session_schedule.blocks, tuple)
    assert isinstance(cfg.session_schedule.print_list, tuple)


# --- invisible to the rules (T-07-09) ---------------------------------------------------------------------------


def test_the_block_never_reaches_the_real_machinery(cfg, tmp_path):
    raw = _raw()
    del raw["session_schedule"]
    plain = _load(raw, tmp_path)
    assert dataclasses.replace(cfg, session_schedule=None) == plain
    selection = {"M1": 2, "M2": 2, "M3": 1, "M4": 1, "M5": 0, "M6": 1, "M7": 0, "M8": 0, "M9": 0, "M10": 0}
    assert rules.evaluate_plan(cfg, "medium", selection) == rules.evaluate_plan(plain, "medium", selection)
    assert rules.TierKernel(cfg, "medium").evaluate(selection) == rules.TierKernel(plain, "medium").evaluate(selection)


# --- validator -------------------------------------------------------------------------------------------------


def test_the_real_config_validates():
    assert _errors(_raw()) == []


def _mutated(mutate):
    raw = _raw()
    mutate(raw["session_schedule"])
    return raw


def _block(raw_block, block_id):
    return next(block for block in raw_block["blocks"] if block["id"] == block_id)


def test_blocks_must_add_up_to_the_total():
    raw = _mutated(lambda s: _block(s, "closing").update(minutes=11))
    assert "schedule.sum" in _codes(raw)
    raw = _mutated(lambda s: s.update(total_minutes=191))
    assert "schedule.sum" in _codes(raw)


def test_duplicate_and_malformed_ids_are_rejected():
    raw = _mutated(lambda s: _block(s, "closing").update(id="debrief"))
    assert "schedule.id" in _codes(raw)
    raw = _mutated(lambda s: _block(s, "closing").update(id="Closing Block"))
    assert "schedule.id" in _codes(raw)


@pytest.mark.parametrize("minutes", [0, -5])
def test_minutes_must_be_positive(minutes):
    raw = _mutated(lambda s: _block(s, "closing").update(minutes=minutes))
    assert "schema.range" in _codes(raw)


def test_unknown_keys_are_rejected_in_the_block_a_block_and_a_print_row():
    assert "schema.keys" in _codes(_mutated(lambda s: s.update(start_time="14:00")))
    assert "schema.keys" in _codes(_mutated(lambda s: _block(s, "closing").update(start="14:00")))
    assert "schema.keys" in _codes(_mutated(lambda s: s["print_list"][0].update(color=True)))


def test_every_config_wave_needs_its_block():
    def drop(schedule):
        schedule["blocks"] = [block for block in schedule["blocks"] if block["id"] != "wave_2"]
        schedule["total_minutes"] -= 20

    assert "schedule.wave_block" in _codes(_mutated(drop))


def test_a_wave_value_must_be_a_config_wave_or_zero_and_unique():
    assert "schedule.wave_block" in _codes(_mutated(lambda s: _block(s, "wave_3").update(wave=7)))
    assert "schedule.wave_block" in _codes(_mutated(lambda s: _block(s, "wave_3").update(wave=2)))


def test_a_negative_quantity_is_rejected():
    assert "schema.range" in _codes(_mutated(lambda s: s["print_list"][0].update(per_team=-1)))
    assert "schema.range" in _codes(_mutated(lambda s: s["print_list"][0].update(facilitator=-1)))


def test_a_duplicate_or_malformed_print_job_is_rejected():
    assert "schedule.print_job" in _codes(_mutated(lambda s: s["print_list"][1].update(job=s["print_list"][0]["job"])))
    assert "schedule.print_job" in _codes(_mutated(lambda s: s["print_list"][0].update(job="Angriff 1.pdf")))


def test_a_facilitator_document_never_goes_to_the_teams():
    def spread(schedule):
        row = next(row for row in schedule["print_list"] if row["job"].startswith("spielleitung-"))
        row["per_team"] = 1

    assert "schedule.print_veil" in _codes(_mutated(spread))


def test_teams_and_persons_per_team_need_at_least_one():
    assert "schema.range" in _codes(_mutated(lambda s: s.update(teams=0)))
    for value in (0, -1):
        assert "schema.range" in _codes(_mutated(lambda s, v=value: s.update(persons_per_team=v)))
    for value in ("5", 4.5):
        assert "schema.type" in _codes(_mutated(lambda s, v=value: s.update(persons_per_team=v)))


def test_persons_per_team_is_required():
    raw = _mutated(lambda s: s.pop("persons_per_team"))
    errors = _errors(raw)
    assert any("persons_per_team" in issue.path or "persons_per_team" in issue.message for issue in errors)


def test_the_validator_does_not_mutate_its_input():
    raw = _raw()
    before = copy.deepcopy(raw)
    validate(raw)
    assert raw == before


# --- FLOW-02 product rules on the real config ---------------------------------------------------------------


def test_the_schedule_is_the_d02_sequence_of_200_minutes(cfg):
    schedule = cfg.session_schedule
    assert schedule.total_minutes == 200
    assert sum(block.minutes for block in schedule.blocks) == 200
    assert tuple((block.id, block.minutes) for block in schedule.blocks) == D02_BLOCKS


def test_wave_one_has_25_minutes_the_other_waves_20_and_the_debrief_30(cfg):
    # D-34 deviation, user-approved 2026-11-04: the solo run took 30 min against 20, wave 1 is re-budgeted to 25
    blocks = {block.id: block for block in cfg.session_schedule.blocks}
    for wave in cfg.waves:
        assert blocks[f"wave_{wave.wave_id}"].minutes == (25 if wave.wave_id == 1 else 20)
    assert blocks["debrief"].minutes == 30


def test_no_whiteboard_and_no_window_block_and_no_start_time(cfg):
    for block in cfg.session_schedule.blocks:
        assert "whiteboard" not in block.id and "pinnwand" not in block.id
        assert "window" not in block.id and "change" not in block.id
    raw = _raw()["session_schedule"]
    assert not any("start" in key or "clock" in key or "time" in key for key in raw)
    assert not any("start" in key or "clock" in key or "time" in key for block in raw["blocks"] for key in block)


def test_three_teams_of_five_and_a_practice_wave_block(cfg):
    assert cfg.session_schedule.teams == 3
    assert cfg.session_schedule.persons_per_team == 5
    assert cfg.practice is not None
    assert any(block.wave == 0 for block in cfg.session_schedule.blocks)


# --- FLOW-03: debrief stage minutes (D-11) ---------------------------------------------------------------------

DEBRIEF_STAGES = (("reaction", 3), ("description", 5), ("analysis", 14), ("application", 8))


def test_the_debrief_stages_are_the_four_flow_03_stages_and_fill_the_debrief_block(cfg):
    schedule = cfg.session_schedule
    assert all(isinstance(stage, DebriefStage) for stage in schedule.debrief_stages)
    assert tuple((stage.id, stage.minutes) for stage in schedule.debrief_stages) == DEBRIEF_STAGES
    block = next(block for block in schedule.blocks if block.id == "debrief")
    assert sum(stage.minutes for stage in schedule.debrief_stages) == block.minutes


def test_a_schedule_without_stages_still_loads(tmp_path):
    raw = _raw()
    del raw["session_schedule"]["debrief_stages"]
    assert _errors(raw) == []
    assert _load(raw, tmp_path).session_schedule.debrief_stages == ()


def test_stage_minutes_must_add_up_to_the_debrief_block():
    raw = _mutated(lambda s: s["debrief_stages"][0].update(minutes=4))
    assert "schedule.debrief_sum" in _codes(raw)


def test_stages_need_a_debrief_block():
    def drop(schedule):
        schedule["blocks"] = [block for block in schedule["blocks"] if block["id"] != "debrief"]
        schedule["total_minutes"] -= 20

    assert "schedule.debrief_block" in _codes(_mutated(drop))


def test_duplicate_and_malformed_stage_ids_are_rejected():
    assert "schedule.id" in _codes(_mutated(lambda s: s["debrief_stages"][1].update(id="reaction")))
    assert "schedule.id" in _codes(_mutated(lambda s: s["debrief_stages"][1].update(id="Second Stage")))


def test_stage_minutes_must_be_positive_and_keys_known():
    assert "schema.range" in _codes(_mutated(lambda s: s["debrief_stages"][0].update(minutes=0)))
    assert "schema.keys" in _codes(_mutated(lambda s: s["debrief_stages"][0].update(label="x")))


# --- RISK-07: optional management pitch speaking time (D-17) -----------------------------------------------


def test_the_pitch_speaking_time_is_sixty_seconds_outside_the_timed_blocks(cfg):
    schedule = cfg.session_schedule
    assert schedule.pitch_seconds == 60
    assert schedule.total_minutes == 200
    assert tuple((stage.id, stage.minutes) for stage in schedule.debrief_stages) == DEBRIEF_STAGES


def test_a_schedule_without_a_pitch_time_loads_with_none(tmp_path):
    raw = _raw()
    del raw["session_schedule"]["pitch_seconds"]
    assert _errors(raw) == []
    assert _load(raw, tmp_path).session_schedule.pitch_seconds is None


def test_the_pitch_time_needs_at_least_one_second_and_an_integer():
    assert "schema.range" in _codes(_mutated(lambda s: s.update(pitch_seconds=0)))
    assert "schema.type" in _codes(_mutated(lambda s: s.update(pitch_seconds="60")))
