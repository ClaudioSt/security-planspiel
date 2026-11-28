"""The Budget Review is an event: only its event card prints the remaining-budget tiers and the overspend rule (D-3).

Teamheft page 5 used to print the tiers and an overspend table from the start of the game, which gave the event
away. Every player-facing document except the event deck is scanned for the card's wording; facilitator documents
may keep the values.
"""
import pytest

from planspiel import audience, render, veil
from planspiel.cards import EVENT_DECK_JOB
from planspiel.config import load_config
from planspiel.eventtext import effect_rows
from planspiel.review_text import format_eur, tier_rows
from planspiel.texts import PreAttackView, load_texts
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"


@pytest.fixture(scope="module")
def setup():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, texts, render.render_all(cfg, texts, TEMPLATES)


def _player_jobs(documents):
    return [
        job for job in documents
        if audience.audience_of(job) != audience.FACILITATOR and job != EVENT_DECK_JOB
    ]


def test_there_are_player_documents_to_scan(setup):
    assert "spieler-teamheft" in _player_jobs(setup[2])


def test_no_player_document_but_the_event_deck_prints_the_review_values(setup):
    cfg, texts, documents = setup
    final = next(event for event in cfg.final_events if event.type == "final_budget_tier")
    words = PreAttackView(cfg, texts).sheet("eventkarten")
    needles = ["angefangene", words["overspend_label"]]
    for from_eur, _, _ in tier_rows(final.params["tiers"])[1:]:
        needles.append(f"{words['tier_from']} {format_eur(from_eur)} €")
    needles.extend(row.text for row in effect_rows(final, cfg, texts).rows)
    assert len(needles) > 6
    card = " ".join(veil.detex(documents[EVENT_DECK_JOB]).split())
    assert all(needle in card for needle in needles), "the scan reads the card wording from the detexed source"
    for job in _player_jobs(documents):
        printed = veil.detex(documents[job])
        printed = " ".join(printed.split())
        for needle in needles:
            assert needle not in printed, f"{job} prints {needle!r}"


# Quick 261125-fsu (user, 2026-11-25): "Kurswechsel steht im Teamheft, ist aber ein Event". Every event, not only the
# Budget Review, stays off the player sheets until its card is handed out. The Teamheft names its last two chapters
# "Return on Security" and "Budget Review" by decision (deck and Ablaufplan use the same words), so the final event's
# name is allowed there; its values stay guarded by the test above.
NAME_ALLOWED = {("budget_review", "spieler-teamheft")}


def _event_names(cfg):
    events = [event for wave_events in cfg.events.values() for event in wave_events] + list(cfg.final_events)
    assert len(events) == 8
    return [(event.id, event.name) for event in events]


def test_no_player_document_but_the_event_deck_names_an_event(setup):
    cfg, texts, documents = setup
    for job in _player_jobs(documents):
        printed = " ".join(veil.detex(documents[job]).split()).casefold()
        for event_id, name in _event_names(cfg):
            if (event_id, job) in NAME_ALLOWED:
                continue
            assert name.casefold() not in printed, f"{job} names the event {name!r}"


def test_the_event_deck_does_name_every_event(setup):
    cfg, texts, documents = setup
    card = " ".join(veil.detex(documents[EVENT_DECK_JOB]).split()).casefold()
    for _, name in _event_names(cfg):
        assert name.casefold() in card, name
