"""Event deck: model, template branches and registration in the print set (PRINT-06, D-02, D-05, D-07, D-26)."""
import json
import re

import pytest

from planspiel import audience, fmt, render, rules, veil
from planspiel.cards import (
    CARDS_PER_SHEET,
    EVENT_DECK_JOB,
    EventCard,
    ReviewCard,
    build_event_deck,
    printed_strings,
)
from planspiel.config import load_config
from planspiel.eventtext import effect_rows
from planspiel.texts import PreAttackView, load_content, load_texts
from planspiel.wave_page import build_wave_page
from tests.support import CONFIG_PATH, CONTENT_DIR, MINI_CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"
MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
SETUPS = [
    pytest.param((MINI, MINI_CONTENT_DIR), id="mini"),
    pytest.param((CONFIG_PATH, CONTENT_DIR), id="real"),
]


@pytest.fixture(params=SETUPS)
def loaded(request):
    config_path, content_dir = request.param
    cfg = load_config(config_path)
    texts = load_texts(content_dir / "texte.toml")
    return cfg, texts, build_event_deck(cfg, texts)


@pytest.fixture(scope="module")
def real():
    cfg = load_config(CONFIG_PATH)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    return cfg, texts, build_event_deck(cfg, texts), render.render_all(cfg, texts, TEMPLATES)


def _schedule(cfg):
    """(wave key, event) in the order the cards are printed: waves ascending, config order inside a wave."""
    return [(wave_id, event) for wave_id in sorted(cfg.events) for event in cfg.events[wave_id]]


def _card_id(event):
    return event.id.replace("_", "-")


def test_the_deck_is_the_wave_events_in_schedule_order_then_the_review_card(loaded):
    cfg, _, deck = loaded
    assert deck.job == EVENT_DECK_JOB == "spieler-eventkarten"
    expected = [_card_id(event) for _, event in _schedule(cfg)] + [_card_id(cfg.final_events[0])]
    assert [card.card_id for card in deck.cards] == expected
    assert len(deck.cards) == 8
    assert [card.kind for card in deck.cards] == ["event"] * 7 + ["review"]


def test_the_real_schedule_is_the_seven_events_of_the_game(real):
    cfg, _, deck, _ = real
    assert [event.name for _, event in _schedule(cfg)] == [
        "Kurswechsel", "Operative Unterstützung", "Sparprogramm", "OEM-Audit",
        "Kritische Schwachstelle im System", "Exzellenz-Bonus", "Nervige Authentifizierung",
    ]
    assert [card.title for card in deck.cards][-1] == "Budget Review"


def test_the_sheets_are_two_pages_of_four_cards(loaded):
    deck = loaded[2]
    assert CARDS_PER_SHEET == 4
    assert [len(sheet) for sheet in deck.sheets] == [4, 4]
    assert [card for sheet in deck.sheets for card in sheet] == list(deck.cards)


def test_backup_recovery_is_not_a_ninth_card(loaded):
    cfg, texts, deck = loaded
    title = texts.get("sheets.backup_recovery.title")
    assert all(title not in printed_strings(card) for card in deck.cards)
    assert len(deck.cards) == 8


def test_an_event_card_carries_header_title_texts_and_generated_effect_lines(loaded):
    cfg, texts, deck = loaded
    view = PreAttackView(cfg, texts)
    labels = view.sheet("labels")
    cards = {card.card_id: card for card in deck.cards}
    for wave_id, event in _schedule(cfg):
        card = cards[_card_id(event)]
        assert isinstance(card, EventCard)
        event_texts = view.event(event.id)
        effect = effect_rows(event, cfg, texts)
        assert card.header == f"{labels['event_after_wave']} {wave_id}"
        assert card.title == event.name
        assert card.narrative == event_texts["narrative"]
        assert card.rule == event_texts.get("rule")
        assert card.effect_heading == effect.heading
        assert card.effect_lines == tuple(row.text for row in effect.rows)


def test_the_real_header_numbers_are_the_wave_keys(real):
    _, _, deck, _ = real
    assert [card.header for card in deck.cards[:-1]] == [
        "Event in Welle 1", "Event in Welle 1",
        "Event in Welle 2", "Event in Welle 2", "Event in Welle 2",
        "Event in Welle 3", "Event in Welle 3",
    ]


def test_no_event_header_says_after_the_wave(real):
    """D-28: events are step 1 of their wave, so the header must not read as if they came after it."""
    _, _, deck, _ = real
    assert all("Nach" not in card.header for card in deck.cards[:-1])


def test_the_header_uses_the_wave_word_of_the_wave_page_whose_first_step_is_the_events(real):
    cfg, texts, deck, _ = real
    page = build_wave_page(cfg, texts)
    assert page.steps[0].key == "events"
    assert "der Welle" in page.steps[0].text
    wave_word = PreAttackView(cfg, texts).sheet("tracking")["wave"]
    for card in deck.cards[:-1]:
        before_number = card.header.rsplit(" ", 1)[0]
        assert before_number.endswith(wave_word)


def test_the_review_card_carries_tiers_and_the_overspend_rule(loaded):
    cfg, texts, deck = loaded
    card = deck.cards[-1]
    assert isinstance(card, ReviewCard)
    event = cfg.final_events[0]
    view = PreAttackView(cfg, texts)
    effect = effect_rows(event, cfg, texts)
    assert card.header == view.sheet("eventkarten")["review_header"]
    assert card.title == event.name
    assert card.narrative == view.event(event.id)["narrative"]
    assert card.rule == view.event(event.id)["rule"]
    assert card.tier_heading == effect.heading
    assert card.tier_lines == tuple(row.text for row in effect.rows[:-1])
    kz_per_step, step_k = rules.penalty_params(cfg.final_events)
    assert card.overspend_line == effect.rows[-1].text
    assert f"KZ {fmt.MINUS}{kz_per_step}" in card.overspend_line
    assert fmt.format_money(step_k * 1000) in card.overspend_line


def test_the_full_penalty_table_is_not_on_the_card(loaded):
    deck = loaded[2]
    review = deck.cards[-1]
    assert len(review.tier_lines) < 10
    assert len([text for text in printed_strings(review) if "angefangene" in text]) == 1


def test_operative_unterstuetzung_prints_its_rule_and_the_generated_line(real):
    cfg, texts, deck, documents = real
    card = next(card for card in deck.cards if card.card_id == "operative-unterstuetzung")
    assert card.rule == "Zählt für jede Maßnahme, die in dieser Welle aktiv ist."
    assert card.effect_lines == ("OPEX −2.000 € je aktiver Maßnahme",)
    source = documents[EVENT_DECK_JOB]
    assert source.index(render.tex_escape(card.rule)) < source.index(render.tex_escape(card.effect_lines[0]))


def test_the_print_set_holds_the_event_deck(real):
    jobs = list(real[3])
    assert EVENT_DECK_JOB in jobs
    assert jobs == sorted(jobs)
    assert audience.audience_of(EVENT_DECK_JOB) == audience.PREWAVE
    assert audience.scan_profile(EVENT_DECK_JOB) == audience.PROFILE_STORY


def test_the_deck_skeleton_and_one_report_per_card(loaded):
    cfg, texts, deck = loaded
    source = render.render_all(cfg, texts, TEMPLATES)[EVENT_DECK_JOB]
    assert source.startswith("\\documentclass")
    assert source.endswith("\\end{document}\n")
    assert "\r" not in source
    assert source.count("\\cardreport{") == 8
    assert source.count("\\begin{cardsheet}") == 2
    for card in deck.cards:
        assert source.count(f"\\cardreport{{{card.card_id}}}") == 1, card.card_id


def test_every_printed_fragment_is_in_the_tex(loaded):
    cfg, texts, deck = loaded
    source = render.render_all(cfg, texts, TEMPLATES)[EVENT_DECK_JOB]
    fragments = deck.printed_fragments()
    assert fragments
    for fragment in fragments:
        assert render.tex_escape(fragment) in source, fragment


def test_the_event_deck_has_no_duplex_back_pages(loaded):
    cfg, texts, deck = loaded
    source = render.render_all(cfg, texts, TEMPLATES)[EVENT_DECK_JOB]
    assert source.count("\\begin{cardsheet}") == len(deck.sheets)
    assert source.count("\clearpage") == 0  # sheets start new pages through cardsheet only: one page per sheet


def test_the_event_deck_uses_the_one_line_title_guard(loaded):
    cfg, texts, deck = loaded
    source = render.render_all(cfg, texts, TEMPLATES)[EVENT_DECK_JOB]
    assert source.count("\\cardheader{") == 8
    for card in deck.cards:
        assert f"\\cardheader{{{card.card_id}}}" in source, card.card_id


@pytest.mark.parametrize("setup", SETUPS)
def test_the_event_deck_passes_the_story_veil_scan(setup):
    config_path, content_dir = setup
    cfg = load_config(config_path)
    content = load_content(content_dir)
    documents = {EVENT_DECK_JOB: render.render_all(cfg, content.texts, TEMPLATES)[EVENT_DECK_JOB]}
    assert veil.scan_documents(cfg, content.texts, content.terms, documents) == []


def test_a_budget_cut_reaches_the_card_without_a_template_change(tmp_path):
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    raw["events"]["wave_2"][0]["budget_delta"] = -30
    path = tmp_path / "config.json"
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    cfg = load_config(path)
    texts = load_texts(CONTENT_DIR / "texte.toml")
    source = render.render_all(cfg, texts, TEMPLATES)[EVENT_DECK_JOB]
    assert "Budget −30.000 €" in source
    assert "Budget −20.000 €" not in source


def test_the_card_template_keeps_both_branches_and_plain_variables():
    text = (TEMPLATES / "karten.tex.j2").read_text(encoding="utf-8")
    assert 'card.kind == "event"' in text
    assert 'card.kind == "review"' in text
    for expression in re.findall(r"\\VAR\{([^}]*)\}", text):
        assert re.match(r"^[A-Za-z_][A-Za-z0-9_.\[\]'\"]*$", expression), expression
