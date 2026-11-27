"""WEB-02: texts of the web app (content/web.toml) and the phase-split content for the web server.

`content/web.toml` is a separate file so that the print inputs and their stamp stay untouched. Its checks:
no digits (numbers come from the config), giveaway lint with the story profile for everything the player sees
before a wave, `web.reveal.<attack>` may name only its own attack, the only placeholder is `{beratung}`, and the
value-to-case links point at `risk_matrix.cases` with the matching protection goal.

`build_content` splits texte.toml and web.toml by phase for the server's veil filter:
- `always`: story, measure cards, player sheets (no facilitator sheets), practice, web texts without
  the reveal headlines and without the value-to-case links;
- `waves[<id>]`: the revealed attack texts, the events and the headlines of that wave;
- `final`: the final events;
- `server`: what only the server evaluates (business cases with band and goal, value-to-case links, clues).
`risk_matrix.cases[].like_attack` is a validator anchor and is never exported.
"""
import copy
import re
from pathlib import Path
from typing import Dict, List

from planspiel.config import Config
from planspiel.texts import GiveawayTerms, Texts, giveaway_hits, load_clues, load_texts
from planspiel.validate import Issue

WEB_FILE = "web.toml"
PLACEHOLDERS = {"beratung"}
GOALS = ("c", "i", "a")
EXPRESSIONS = ("neutral", "erfreut", "besorgt")
_PLACEHOLDER = re.compile(r"\{([^{}]*)\}")
# Player-facing sheets only; facilitator sheets (cheat sheet, schedule, debrief guide, was-neu, Probelauf) stay out.
PLAYER_SHEETS = ("angriff", "budget", "ros", "teamheft", "register", "tracking", "welle", "backup_recovery", "karten", "eventkarten", "labels")
REQUIRED_MENTOR = ("intro", "analyse", "uebung", "planung", "welle", "fenster", "abschluss", "debrief")


_DU = re.compile(r"\b(du|dir|dich|dein|deine|deinem|deinen|deiner|deines)\b", re.IGNORECASE)


def _du_keys(node: Dict, prefix: str) -> List[str]:
    found = []
    for key, value in node.items():
        path = f"{prefix}.{key}"
        if isinstance(value, dict):
            found += _du_keys(value, path)
        elif key == "paragraphs" or any(_DU.search(text) for text in ([value] if isinstance(value, str) else value)):
            found.append(path)
    return found


def missing_team_texts(web: Texts) -> List[str]:
    """Mentor texts that address one person (du, dein, ...) and every paragraph list need a team version."""
    missing = []
    for path in _du_keys(web.subtree("web.mentor"), "web.mentor"):
        team_path = path.replace("web.mentor.", "web.mentor_team.", 1)
        if not web.has(team_path):
            missing.append(team_path)
    return missing


def load_web_texts(path: Path) -> Texts:
    return load_texts(path)


def scene_quotes(web: Texts) -> List[tuple]:
    """(path, story source, index) of every scene object and dialogue answer that points at a story string."""
    found = []
    scenes = web.subtree("web.szenen") if web.has("web.szenen") else {}
    for scene_id, scene in scenes.items():
        for object_id, obj in scene.get("objekte", {}).items():
            if "quelle" in obj or "index" in obj:
                found.append((f"web.szenen.{scene_id}.objekte.{object_id}", obj.get("quelle"), obj.get("index")))
    dialogues = web.subtree("web.dialoge") if web.has("web.dialoge") else {}
    for figure, dialogue in dialogues.items():
        for number, question in enumerate(dialogue.get("fragen", [])):
            if "quelle" in question or "index" in question:
                found.append((f"web.dialoge.{figure}.fragen.{number}", question.get("quelle"), question.get("index")))
    return found


def check_web_texts(cfg: Config, web: Texts, terms: GiveawayTerms, texts: Texts | None = None) -> List[Issue]:
    issues: List[Issue] = []
    if texts is not None:
        for path, source, index in scene_quotes(web):
            node = texts.get(source) if isinstance(source, str) and source.startswith("story.") and texts.has(source) else None
            if not isinstance(node, list) or not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(node):
                issues.append(Issue("error", "web.scene_quote", path, f"Kein Story-Satz unter {source} [{index}]"))
    attack_ids = tuple(cfg.attacks)
    for chapter in REQUIRED_MENTOR:
        if not web.has(f"web.mentor.{chapter}.title"):
            issues.append(Issue("error", "web.missing", f"web.mentor.{chapter}.title", "Kapiteltext fehlt"))
    for attack_id in attack_ids:
        for case in (1, 2, 3):
            key = f"web.reveal.{attack_id}.headline_case_{case}"
            if not web.has(key):
                issues.append(Issue("error", "web.missing", key, "Schlagzeile fehlt"))

    for key, text in web.strings("web"):
        if any(char.isnumeric() for char in text):
            issues.append(Issue("error", "web.digit", key, "Ziffer in Web-Text; Zahlen kommen aus der Config"))
        for name in _PLACEHOLDER.findall(text):
            if name not in PLACEHOLDERS:
                issues.append(Issue("error", "web.placeholder", key, f"Unbekannter Platzhalter {{{name}}}"))
        if key.startswith("web.reveal."):
            own = key.split(".")[2]
            others = tuple(a for a in attack_ids if a != own)
            hits = [h for h in giveaway_hits(text, terms, others, profile="story") if h in {o.lower() for o in others}]
            hits += _other_attack_terms(text, own, terms)
        else:
            hits = giveaway_hits(text, terms, attack_ids, profile="story")
        if hits:
            issues.append(Issue("error", "web.giveaway", key, f"Verbotener Begriff: {', '.join(sorted(set(hits)))}"))

    for path in missing_team_texts(web):
        issues.append(Issue("error", "web.team_text", path, "Teamfassung fehlt"))
    if web.has("web.mentor_team"):
        for key, _ in web.strings("web.mentor_team"):
            if not web.has(key.replace("web.mentor_team.", "web.mentor.", 1)):
                issues.append(Issue("error", "web.team_text", key, "Teamfassung ohne Grundtext"))
    questions = web.get("web.feedback.questions") if web.has("web.feedback.questions") else []
    if len({q.get("id") for q in questions}) != len(questions):
        issues.append(Issue("error", "web.feedback", "web.feedback.questions", "Doppelte Fragen-ID"))

    dialogues = web.subtree("web.dialoge") if web.has("web.dialoge") else {}
    for figure, dialogue in dialogues.items():
        for number, question in enumerate(dialogue.get("fragen", [])):
            if question.get("ausdruck", "neutral") not in EXPRESSIONS:
                issues.append(Issue("error", "web.expression", f"web.dialoge.{figure}.fragen.{number}", "Unbekannter Ausdruck"))
    event_ids = {event.id for events in cfg.events.values() for event in events}
    badges = web.subtree("web.badges") if web.has("web.badges") else {}
    for badge_id, badge in badges.items():
        if isinstance(badge, dict) and badge.get("hidden") and badge.get("event") not in event_ids:
            issues.append(Issue("error", "web.badge_event", f"web.badges.{badge_id}.event", "Verdecktes Abzeichen ohne gültiges Ereignis"))

    cases = {case.id: case for case in (cfg.risk_matrix.cases if cfg.risk_matrix else ())}
    werte = web.subtree("web.werte") if web.has("web.werte") else {}
    for value_id, entry in werte.items():
        links = entry.get("faelle", {}) if isinstance(entry, dict) else {}
        if not links:
            issues.append(Issue("error", "web.value_case", f"web.werte.{value_id}", "Wert ohne Fall"))
        for goal, case_id in links.items():
            case = cases.get(case_id)
            if goal not in GOALS or case is None or case.goal != goal:
                issues.append(
                    Issue("error", "web.value_case", f"web.werte.{value_id}.faelle.{goal}", f"Fall '{case_id}' passt nicht")
                )
    return issues


# Giveaway stems per attack for the reveal check: a headline of one attack must not use another attack's stems.
_ATTACK_STEMS = {
    "ransomware": ("ransomware", "verschlüssel", "lösegeld", "erpress"),
    "exfil": ("exfil", "datendiebstahl", "darknet"),
    "ot": ("ot-stör",),
}


def _other_attack_terms(text: str, own: str, terms: GiveawayTerms) -> List[str]:
    lowered = text.lower()
    return [stem for attack, stems in _ATTACK_STEMS.items() if attack != own for stem in stems if stem in lowered]


def _without(node: Dict, *keys: str) -> Dict:
    copied = copy.deepcopy(node)
    for key in keys:
        copied.pop(key, None)
    return copied


def build_content(cfg: Config, content_dir: Path) -> Dict:
    texts = load_texts(content_dir / "texte.toml")
    web = load_web_texts(content_dir / WEB_FILE)
    clues = load_clues(content_dir / "clues.toml")

    web_public = _without(web.subtree("web"), "reveal")
    werte = web_public.get("werte", {})
    web_public["werte"] = {value_id: _without(entry, "faelle") for value_id, entry in werte.items()}

    story = copy.deepcopy(texts.subtree("story"))
    # The printed request is addressed to the consultancy of the paper round; the web app fills in its brand.
    story["anfrage_mail"]["kopf"]["an"] = "{beratung_mail}"
    always = {
        "story": story,
        "measures": texts.subtree("measures"),
        "sheets": {name: texts.subtree(f"sheets.{name}") for name in PLAYER_SHEETS if texts.has(f"sheets.{name}")},
        "practice": texts.subtree("practice"),
        "web": web_public,
    }
    waves = {}
    for wave in cfg.waves:
        attack_id = wave.attack_id
        waves[str(wave.wave_id)] = {
            "attack_id": attack_id,
            "attack": texts.subtree(f"attacks.{attack_id}.revealed"),
            "headlines": web.subtree(f"web.reveal.{attack_id}"),
            "events": {event.id: texts.subtree(f"events.{event.id}") for event in cfg.events.get(wave.wave_id, [])},
        }
    final = {event.id: texts.subtree(f"final_events.{event.id}") for event in cfg.final_events}

    cheatsheet = texts.subtree("sheets.cheatsheet")
    cases = {
        case.id: {**cheatsheet["cases"][case.id], "band": case.band, "goal": case.goal}
        for case in (cfg.risk_matrix.cases if cfg.risk_matrix else ())
    }
    server = {
        "cases": cases,
        "bands": [{"id": band.id, "min_k": band.minimum} for band in cfg.risk_matrix.bands] if cfg.risk_matrix else [],
        "value_cases": {value_id: dict(entry.get("faelle", {})) for value_id, entry in werte.items()},
        "clues": [
            {
                "attack": clue.attack,
                "source": clue.source,
                "quote": clue.quote,
                "why": clue.why,
                "measures": list(clue.measures),
                "weight": clue.weight,
            }
            for clue in clues
        ],
    }
    return {"schema": 1, "always": always, "waves": waves, "final": final, "server": server}
