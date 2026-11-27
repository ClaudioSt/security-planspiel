"""WEB-02: texts of the web app (content/web.toml) and the phase-split content export for the server.

The web app may only show an attack from the start of its wave. The export therefore splits the content into
`always` (story, measures, sheets, practice, web texts), `waves` (revealed attack texts, events and headlines per
wave) and `final`; `server` holds what only the server evaluates (clues, business cases, value-to-case links).
"""
import copy

import pytest

from planspiel.config import load_config
from planspiel.export_web import build_export
from planspiel.texts import Texts, giveaway_hits, load_content
from planspiel.web_content import check_web_texts, load_web_texts
from tests.support import REPO_ROOT

CONFIG_PATH = REPO_ROOT / "simulation_config.json"


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def content():
    return load_content(REPO_ROOT / "content")


@pytest.fixture(scope="module")
def web():
    return load_web_texts(REPO_ROOT / "content" / "web.toml")


@pytest.fixture(scope="module")
def export():
    return build_export(CONFIG_PATH)


def _with(web: Texts, key: str, value) -> Texts:
    data = copy.deepcopy(web.data)
    node = data
    parts = key.split(".")
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value
    return Texts(data)


def _codes(issues):
    return {issue.code for issue in issues}


def test_web_texts_pass(cfg, content, web):
    assert check_web_texts(cfg, web, content.terms, content.texts) == []


def test_digits_are_refused(cfg, content, web):
    issues = check_web_texts(cfg, _with(web, "web.mentor.planung.tier_title", "Budget in drei Stufen: 3"), content.terms)
    assert "web.digit" in _codes(issues)


def test_giveaway_before_the_wave_is_refused(cfg, content, web):
    issues = check_web_texts(cfg, _with(web, "web.mentor.analyse.title", "Achtung Ransomware"), content.terms)
    assert "web.giveaway" in _codes(issues)


def test_reveal_names_only_its_own_attack(cfg, content, web):
    issues = check_web_texts(cfg, _with(web, "web.reveal.ot.headline_case_1", "Ransomware legt Fertigung lahm"), content.terms)
    assert "web.giveaway" in _codes(issues)


def test_unknown_placeholders_are_refused(cfg, content, web):
    issues = check_web_texts(cfg, _with(web, "web.mentor.intro.title", "Willkommen bei {firma}"), content.terms)
    assert "web.placeholder" in _codes(issues)


def test_value_cases_must_exist_and_match_the_goal(cfg, content, web):
    wrong_goal = _with(web, "web.werte.buero.faelle", {"c": "single_pc"})
    unknown = _with(web, "web.werte.buero.faelle", {"a": "gibt_es_nicht"})
    assert "web.value_case" in _codes(check_web_texts(cfg, wrong_goal, content.terms))
    assert "web.value_case" in _codes(check_web_texts(cfg, unknown, content.terms))


def test_more_values_than_attacks(cfg, web):
    assert len(web.subtree("web.werte")) > len(cfg.attacks)


def test_every_attack_has_headlines(cfg, web):
    for attack_id in cfg.attacks:
        for case in (1, 2, 3):
            assert web.has(f"web.reveal.{attack_id}.headline_case_{case}")


def _strings(node, path=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _strings(value, f"{path}.{key}" if path else key)
    elif isinstance(node, list):
        for item in node:
            yield from _strings(item, path)
    elif isinstance(node, str):
        yield path, node


def test_always_content_reveals_no_attack(cfg, content, export):
    always = export["content.json"]["always"]
    attack_ids = tuple(cfg.attacks)
    revealed_names = {content.texts.get(f"attacks.{a}.revealed.name").lower() for a in attack_ids}
    for path, text in _strings(always):
        if path.startswith("measures."):
            continue  # the measure deck uses the names-only profile (D-24): "Phishing" on the M6 card is a defence term
        assert giveaway_hits(text, content.terms, attack_ids, profile="story") == [], path
        assert not any(name in text.lower() for name in revealed_names), path
    for path, text in _strings(always.get("measures", {})):
        assert not any(name in text.lower() for name in revealed_names), path


def test_always_content_has_no_attack_ids_as_keys(cfg, export):
    def keys(node):
        if isinstance(node, dict):
            for key, value in node.items():
                yield key
                yield from keys(value)
        elif isinstance(node, list):
            for item in node:
                yield from keys(item)

    found = set(keys(export["content.json"]["always"]))
    assert not found & set(cfg.attacks)


def test_always_content_has_no_facilitator_sheets(export):
    sheets = set(export["content.json"]["always"]["sheets"])
    assert not sheets & {"cheatsheet", "spielleitung", "ablauf", "debrief", "was_neu", "probelauf"}
    assert {"welle", "register", "teamheft"} <= sheets


def test_waves_carry_the_revealed_texts(cfg, content, export):
    waves = export["content.json"]["waves"]
    for wave in cfg.waves:
        entry = waves[str(wave.wave_id)]
        assert entry["attack_id"] == wave.attack_id
        assert entry["attack"]["name"] == content.texts.get(f"attacks.{wave.attack_id}.revealed.name")
        assert set(entry["events"]) == {event.id for event in cfg.events.get(wave.wave_id, [])}
        assert set(entry["headlines"]) == {"headline_case_1", "headline_case_2", "headline_case_3"}


def test_server_part_never_carries_like_attack(export):
    def walk(node):
        if isinstance(node, dict):
            assert "like_attack" not in node
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(export["content.json"])


def test_server_part_has_cases_values_and_clues(cfg, export):
    server = export["content.json"]["server"]
    assert set(server["cases"]) == {case.id for case in cfg.risk_matrix.cases}
    assert {"case", "answer", "band", "goal"} <= set(next(iter(server["cases"].values())))
    assert server["value_cases"]["konstruktionsdaten"] == {"c": "design_data", "i": "data_trust"}
    assert {clue["attack"] for clue in server["clues"]} == set(cfg.attacks)
    assert "faelle" not in str(export["content.json"]["always"]["web"]["werte"])


def test_team_texts_cover_every_du_text(cfg, content, web):
    """Teams read the mentor in the plural: every mentor text that addresses one person has a team version."""
    from planspiel.web_content import missing_team_texts

    assert missing_team_texts(web) == []
    broken = _with(web, "web.mentor_team.analyse", {})
    assert "web.mentor_team.analyse.paragraphs" in missing_team_texts(broken)


def test_team_texts_only_override_existing_keys(cfg, content, web):
    issues = check_web_texts(cfg, _with(web, "web.mentor_team.analyse.erfunden", "Hallo"), content.terms)
    assert "web.team_text" in _codes(issues)


def test_feedback_questions(cfg, content, web):
    questions = web.get("web.feedback.questions")
    assert len(questions) >= 3
    assert len({q["id"] for q in questions}) == len(questions)
    assert all(q["text"] for q in questions)


def test_feedback_ids_are_stable(web):
    ids = [q["id"] for q in web.get("web.feedback.questions")]
    assert ids[:3] == ["verstanden", "zusammenhang", "bedienung"]


BADGES = {
    "spurensucher", "geschlossene_kette", "lueckenlos", "volle_abwehr", "unverwundbar", "kopfrechner",
    "augenmass", "im_budget", "kurs_gehalten", "audit_bestanden", "benutzerfreundlich",
}


def test_badges_have_texts(web):
    badges = web.subtree("web.badges")
    assert set(badges) == BADGES
    for badge in badges.values():
        assert badge["name"] and badge["description"]


def test_hidden_badges_are_marked(web):
    hidden = {key for key, badge in web.subtree("web.badges").items() if badge.get("hidden")}
    assert hidden == {"kurs_gehalten", "audit_bestanden", "benutzerfreundlich"}


def test_hidden_badges_name_an_event_of_the_config(cfg, content, web):
    events = {event.id for events in cfg.events.values() for event in events}
    for key, badge in web.subtree("web.badges").items():
        if badge.get("hidden"):
            assert badge.get("event") in events, key
    broken = _with(web, "web.badges.kurs_gehalten.event", "gibt_es_nicht")
    assert "web.badge_event" in _codes(check_web_texts(cfg, broken, content.terms))


def test_episode_titles_for_every_chapter(web):
    episodes = web.subtree("web.episodes")
    assert set(episodes) >= {"analyse", "uebung", "planung", "welle", "fenster", "abschluss", "debrief"}


def test_scene_quotes_point_at_story_strings(cfg, content, web):
    """Scenes and dialogues never carry their own clue text: they point at a story string (source and index),
    so a pinned note is the same string as in the printed documents and clues.toml stays the only clue list."""
    from planspiel.web_content import scene_quotes

    quotes = scene_quotes(web)
    assert quotes, "the server room scene has quotes"
    for path, source, index in quotes:
        node = content.texts.get(source)
        assert isinstance(node, list) and 0 <= index < len(node), path


def test_broken_scene_quote_is_an_error(cfg, content, web):
    broken = _with(web, "web.szenen.serverraum.objekte.backup.index", 99)
    assert "web.scene_quote" in _codes(check_web_texts(cfg, broken, content.terms, content.texts))


def test_server_room_reaches_clues_of_every_attack(cfg, content, web):
    from planspiel.texts import load_clues
    from planspiel.web_content import scene_quotes

    clues = load_clues(REPO_ROOT / "content" / "clues.toml")
    reachable = {content.texts.get(source)[index] for _, source, index in scene_quotes(web)}
    attacks = {clue.attack for clue in clues if any(clue.quote in text for text in reachable)}
    assert attacks == set(cfg.attacks)


def test_recipient_of_the_request_is_the_brand_placeholder(export):
    """The printed request goes to the consultancy of the paper round; the web app fills in its own brand."""
    always = export["content.json"]["always"]
    assert always["story"]["anfrage_mail"]["kopf"]["an"] == "{beratung_mail}"
    assert "VWI" not in str(always)


def test_dialogue_expressions_are_known(cfg, content, web):
    for figure, dialogue in web.subtree("web.dialoge").items():
        for question in dialogue["fragen"]:
            assert question.get("ausdruck", "neutral") in {"neutral", "erfreut", "besorgt"}
    broken = copy.deepcopy(web.data)
    broken["web"]["dialoge"]["it"]["fragen"][0]["ausdruck"] = "wütend"
    assert "web.expression" in _codes(check_web_texts(cfg, Texts(broken), content.terms, content.texts))


def test_scene_figures_belong_to_the_cast(cfg, content, web):
    cast = set(web.subtree("web.cast"))
    for scene_id, scene in web.subtree("web.szenen").items():
        assert scene.get("figur") in cast, scene_id
    broken = copy.deepcopy(web.data)
    broken["web"]["szenen"]["serverraum"]["figur"] = "gibt_es_nicht"
    assert "web.scene_figure" in _codes(check_web_texts(cfg, Texts(broken), content.terms, content.texts))


SCENE_FIGURES = {"serverraum": "it", "buero_weber": "weber", "werkshalle": "produktion"}


@pytest.mark.parametrize("scene_id", sorted(SCENE_FIGURES))
def test_every_scene_reaches_clues_of_every_attack(cfg, content, web, scene_id):
    """Each scene (objects plus the conversation with its figure) offers a clue for every attack, so no scene is
    a dead end and the order of visits does not matter."""
    from planspiel.texts import load_clues
    from planspiel.web_content import scene_quotes

    figure = SCENE_FIGURES[scene_id]
    assert web.subtree(f"web.szenen.{scene_id}")["figur"] == figure
    quotes = [
        (source, index) for path, source, index in scene_quotes(web)
        if path.startswith(f"web.szenen.{scene_id}.") or path.startswith(f"web.dialoge.{figure}.")
    ]
    assert len(quotes) >= 8
    clues = load_clues(REPO_ROOT / "content" / "clues.toml")
    reachable = {content.texts.get(source)[index] for source, index in quotes}
    assert {clue.attack for clue in clues if any(clue.quote in text for text in reachable)} == set(cfg.attacks)
