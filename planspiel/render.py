"""Render stage of the print pipeline: strict Jinja environment and the document registry.

Numbers reach the page only as strings formatted in code; `tex_escape` is the Jinja `finalize`
hook and rejects everything else, so a template cannot print a raw number or an undefined name.
"""
import re
from pathlib import Path
from typing import Callable, Dict, Tuple

import jinja2

from planspiel import audience, texbuild
from planspiel.booklet import build_team_booklet
from planspiel.cards import build_event_deck, build_measure_deck
from planspiel.master import build_master_sheet
from planspiel.practice import build_practice_document
from planspiel.printmodel import build_attack_sheets
from planspiel.story import Mail, Steckbrief, Zeitungsartikel, build_story_documents
from planspiel.wave_page import build_wave_page

_TEX_SPECIALS = str.maketrans(
    {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        # babel-ngerman makes `"` an active shorthand (`"a` would print `ä`, the quote vanishes).
        # The TeX input ligatures (-- << >> '' ,, ...) are switched off in planspiel.sty: an empty
        # group does not interrupt them in LuaTeX.
        '"': r"\textquotedbl{}",
    }
)
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b-\x1f]")
_ASSET_NAME_CHARACTERS = re.compile(r"[A-Za-z0-9._-]+")


class AssetName(str):
    r"""A fixed image file name for `\includegraphics`: `tex_escape` leaves it as it is (an escaped `\_` breaks the lookup).

    Only `asset_name` creates one, and only for a name in `texbuild.ASSET_FILES`, so no content string reaches TeX unescaped.
    """

    __slots__ = ()


def asset_name(name: str) -> AssetName:
    if name not in texbuild.ASSET_FILES or not _ASSET_NAME_CHARACTERS.fullmatch(name):
        raise ValueError(f"Kein bekanntes Bild: {name!r} (erlaubt: {', '.join(texbuild.ASSET_FILES)})")
    return AssetName(name)


def tex_escape(value: object) -> str:
    """Escape the LaTeX specials and babel's `"` shorthand in one pass; reject non-strings and control characters."""
    if isinstance(value, jinja2.Undefined):
        str(value)  # StrictUndefined raises UndefinedError here, naming the missing variable
    if isinstance(value, AssetName):
        return str(value)
    if not isinstance(value, str):
        raise TypeError(
            f"Nur Strings dürfen in eine Vorlage ausgegeben werden, nicht {type(value).__name__}: {value!r}"
        )
    if _CONTROL_CHARACTERS.search(value):
        raise ValueError(f"Steuerzeichen im Text für LaTeX: {value!r}")
    return value.translate(_TEX_SPECIALS)


def make_env(template_dir: Path) -> jinja2.Environment:
    return jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
        undefined=jinja2.StrictUndefined,
        finalize=tex_escape,
        keep_trailing_newline=True,
        loader=jinja2.FileSystemLoader(str(template_dir)),
    )


def attack_worksheets(cfg, texts, env: jinja2.Environment, clues) -> Dict[str, str]:
    """One attack worksheet per wave, rendered from the print model with angriff.tex.j2."""
    template = env.get_template("angriff.tex.j2")
    return {sheet.job: template.render(sheet=sheet) for sheet in build_attack_sheets(cfg, texts)}


def measure_cards(cfg, texts, env: jinja2.Environment, clues) -> Dict[str, str]:
    """The measure deck (legend card plus one card per measure level), rendered with karten.tex.j2."""
    deck = build_measure_deck(cfg, texts)
    return {deck.job: env.get_template("karten.tex.j2").render(deck=deck)}


def event_cards(cfg, texts, env: jinja2.Environment, clues) -> Dict[str, str]:
    """The event deck (seven wave events plus the Budget Review card), rendered with the same karten.tex.j2."""
    deck = build_event_deck(cfg, texts)
    return {deck.job: env.get_template("karten.tex.j2").render(deck=deck)}


def team_booklet(cfg, texts, env: jinja2.Environment, clues) -> Dict[str, str]:
    """The team booklet (planning first, RoS and Budget Review last), rendered with teamheft.tex.j2 and its partials."""
    booklet = build_team_booklet(cfg, texts)
    return {booklet.job: env.get_template("teamheft.tex.j2").render(booklet=booklet)}


def wave_page(cfg, texts, env: jinja2.Environment, clues) -> Dict[str, str]:
    """The one-page explainer "So funktioniert eine Welle", rendered with welle.tex.j2."""
    page = build_wave_page(cfg, texts)
    return {page.job: env.get_template("welle.tex.j2").render(page=page)}


def practice_document(cfg, texts, env: jinja2.Environment, clues) -> Dict[str, str]:
    """The Welle 0 worked example, rendered with uebung.tex.j2; nothing without a practice block in the config."""
    doc = build_practice_document(cfg, texts)
    if doc is None:
        return {}
    return {doc.job: env.get_template("uebung.tex.j2").render(doc=doc)}


def master_sheet(cfg, texts, env: jinja2.Environment, clues) -> Dict[str, str]:
    """The facilitator booklet (parameters, check rows, answer keys, clue matrix), rendered with master.tex.j2;
    nothing without reference plans in the config."""
    sheet = build_master_sheet(cfg, texts, clues)
    if sheet is None:
        return {}
    return {sheet.job: env.get_template("master.tex.j2").render(sheet=sheet)}


STORY_TEMPLATES = {
    Steckbrief: "story_steckbrief.tex.j2",
    Zeitungsartikel: "story_zeitungsartikel.tex.j2",
    Mail: "story_mail.tex.j2",
}


def story_documents(cfg, texts, env: jinja2.Environment, clues) -> Dict[str, str]:
    """The four pre-wave story documents; the template is chosen by the model type, the mails share one."""
    assets = {name: asset_name(name) for name in texbuild.ASSET_FILES}
    return {
        model.job: env.get_template(STORY_TEMPLATES[type(model)]).render(doc=model, asset=assets)
        for model in build_story_documents(cfg, texts)
    }


# Each builder takes (cfg, texts, env, clues) and returns {job name: .tex source}; only the master sheet reads the clues.
DocumentBuilder = Callable[..., Dict[str, str]]
DOCUMENT_BUILDERS: Tuple[DocumentBuilder, ...] = (
    attack_worksheets, measure_cards, event_cards, team_booklet, wave_page, story_documents, practice_document,
    master_sheet,
)


def render_all(cfg, texts, template_dir: Path, clues: tuple = ()) -> Dict[str, str]:
    env = make_env(template_dir)
    documents: Dict[str, str] = {}
    for builder in DOCUMENT_BUILDERS:
        for job, source in builder(cfg, texts, env, clues).items():
            texbuild.check_job_name(job)
            audience.audience_of(job)
            if job in documents:
                raise ValueError(f"Dokument {job!r} wird von mehreren Erzeugern geliefert")
            documents[job] = source
    return {job: documents[job] for job in sorted(documents)}
