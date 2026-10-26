"""Print models of the four pre-wave story documents: Unternehmenssteckbrief, Zeitungsartikel and the two mails (PRINT-12).

The documents are veiled content from Phase 3 (`[story.*]` in content/texte.toml); the clue quotes of
content/clues.toml stand verbatim in them. The models only order and name the stored strings, they never
rewrite one: headings keep their stored case, nothing a subtree holds is dropped, and an unexpected key or value type
stops the build instead of silently losing text. The two newspaper images are referred to only through
`texbuild.ASSET_FILES`, so no content string ever chooses a file name (D-19).

The module is a pre-wave builder: it reads the story subtrees and the sheet labels through `PreAttackView` and never
touches revealed text or wave data (VEIL-02).
"""
import dataclasses
from dataclasses import dataclass

from planspiel import texbuild
from planspiel.config import Config
from planspiel.printmodel import PrintModelError
from planspiel.texts import STORY_DOCS, PreAttackView, Texts

STORY_JOBS = {
    "steckbrief": "spieler-unternehmenssteckbrief",
    "zeitungsartikel": "spieler-zeitungsartikel",
    "anfrage_mail": "spieler-anfrage-mail",
    "audit_mail": "spieler-audit-mail",
}
# Roles of the keys inside one section table. A heading is `heading` or `headline`; `text` and `paragraphs` are body
# paragraphs in stored order; nested tables become subsections.
_HEADING_KEYS = ("heading", "headline")
_PARAGRAPH_KEYS = ("text", "paragraphs")
_BULLET_KEYS = ("bullets",)
_NEWS_KEYS = ("dateline", "lead", "caption")
_SECTION_KEYS = (*_HEADING_KEYS, *_PARAGRAPH_KEYS, *_BULLET_KEYS, *_NEWS_KEYS)
# Fields of a model that identify it or name a file but are never printed.
_NOT_PRINTED = frozenset({"job", "images", "image"})


@dataclass(frozen=True)
class Section:
    """A heading with paragraphs, bullets and nested subsections; the newspaper sections add dateline, lead, caption."""

    heading: str = ""
    paragraphs: tuple[str, ...] = ()
    bullets: tuple[str, ...] = ()
    subsections: tuple["Section", ...] = ()
    dateline: str = ""
    lead: str = ""
    caption: str = ""
    image: str = ""


@dataclass(frozen=True)
class Steckbrief:
    job: str
    title: str
    sections: tuple[Section, ...]

    def printed_strings(self) -> list[str]:
        return _printed(self)


@dataclass(frozen=True)
class Zeitungsartikel:
    job: str
    masthead: str
    header_items: tuple[str, ...]
    ticker: tuple[str, ...]
    footer_items: tuple[str, ...]
    sections: tuple[Section, ...]
    images: tuple[str, ...]

    def printed_strings(self) -> list[str]:
        return _printed(self)


@dataclass(frozen=True)
class MailLabels:
    sender: str
    recipient: str
    subject: str


@dataclass(frozen=True)
class Mail:
    job: str
    labels: MailLabels
    sender: str
    recipient: str
    subject: str
    salutation: str
    sections: tuple[Section, ...]
    closing_lines: tuple[str, ...]
    footer_lines: tuple[str, ...]

    def printed_strings(self) -> list[str]:
        return _printed(self)


StoryDocument = Steckbrief | Zeitungsartikel | Mail


def _printed(value: object) -> list[str]:
    """Every string of a model that ends up on the paper, in field order (job and image names excluded)."""
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, tuple):
        return [text for part in value for text in _printed(part)]
    if dataclasses.is_dataclass(value):
        return [
            text
            for field in dataclasses.fields(value)
            if field.name not in _NOT_PRINTED
            for text in _printed(getattr(value, field.name))
        ]
    return []


def _text(path: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PrintModelError(f"{path}: ein nicht leerer Text wird erwartet, gefunden {value!r}")
    return value


def _texts(path: str, value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise PrintModelError(f"{path}: eine nicht leere Liste von Texten wird erwartet, gefunden {value!r}")
    return tuple(_text(f"{path}[{number}]", item) for number, item in enumerate(value))


def _section(path: str, node: object) -> Section:
    if not isinstance(node, dict):
        raise PrintModelError(f"{path}: ein Abschnitt (Tabelle) wird erwartet, gefunden {node!r}")
    fields: dict[str, object] = {}
    paragraphs: list[str] = []
    subsections: list[Section] = []
    for key, value in node.items():
        where = f"{path}.{key}"
        if isinstance(value, dict):
            subsections.append(_section(where, value))
        elif key in _HEADING_KEYS:
            if "heading" in fields:
                raise PrintModelError(f"{path}: Überschrift doppelt (heading und headline)")
            fields["heading"] = _text(where, value)
        elif key == "text":
            paragraphs.append(_text(where, value))
        elif key == "paragraphs":
            paragraphs.extend(_texts(where, value))
        elif key in _BULLET_KEYS:
            fields["bullets"] = _texts(where, value)
        elif key in _NEWS_KEYS:
            fields[key] = _text(where, value)
        else:
            raise PrintModelError(f"{where}: unbekannter Schlüssel (erlaubt: {', '.join(_SECTION_KEYS)} und Unterabschnitte)")
    return Section(paragraphs=tuple(paragraphs), subsections=tuple(subsections), **fields)  # type: ignore[arg-type]


def _sections(path: str, story: dict, named: tuple[str, ...]) -> tuple[Section, ...]:
    """Every table of the story document that is not one of the explicitly named top-level keys, in stored order."""
    sections = []
    for key, value in story.items():
        if key in named:
            continue
        sections.append(_section(f"{path}.{key}", value))
    return tuple(sections)


def _steckbrief(story: dict) -> Steckbrief:
    path = "story.steckbrief"
    return Steckbrief(
        job=STORY_JOBS["steckbrief"],
        title=_text(f"{path}.doc_title", story["doc_title"]),
        sections=_sections(path, story, ("doc_title",)),
    )


def _images(sections: tuple[Section, ...]) -> tuple[Section, ...]:
    """Give the captioned sections the fixed image names in order; every image must have exactly one caption."""
    captioned = [number for number, section in enumerate(sections) if section.caption]
    if len(captioned) != len(texbuild.ASSET_FILES):
        raise PrintModelError(
            f"Zeitungsartikel: {len(texbuild.ASSET_FILES)} Bilder, aber {len(captioned)} Abschnitte mit Bildunterschrift"
        )
    placed = list(sections)
    for number, name in zip(captioned, texbuild.ASSET_FILES):
        placed[number] = dataclasses.replace(placed[number], image=name)
    return tuple(placed)


def _zeitungsartikel(story: dict) -> Zeitungsartikel:
    path = "story.zeitungsartikel"
    named = ("doc_title", "kopfzeile", "ticker", "fusszeile")
    lists = {key: _texts(f"{path}.{key}", story[key]) if key in story else () for key in named[1:]}
    return Zeitungsartikel(
        job=STORY_JOBS["zeitungsartikel"],
        masthead=_text(f"{path}.doc_title", story["doc_title"]),
        header_items=lists["kopfzeile"],
        ticker=lists["ticker"],
        footer_items=lists["fusszeile"],
        sections=_images(_sections(path, story, named)),
        images=texbuild.ASSET_FILES,
    )


def _lines(path: str, story: dict, key: str) -> tuple[str, ...]:
    if key not in story:
        return ()
    node = story[key]
    if not isinstance(node, dict) or set(node) != {"lines"}:
        raise PrintModelError(f"{path}.{key}: ein Abschnitt mit genau dem Schlüssel 'lines' wird erwartet")
    return _texts(f"{path}.{key}.lines", node["lines"])


def _mail(doc: str, story: dict, labels: MailLabels) -> Mail:
    path = f"story.{doc}"
    kopf = story.get("kopf")
    if not isinstance(kopf, dict) or set(kopf) != {"von", "an"}:
        raise PrintModelError(f"{path}.kopf: eine Tabelle mit den Schlüsseln 'von' und 'an' wird erwartet")
    salutation = ""
    if "anrede" in story:
        anrede = story["anrede"]
        if not isinstance(anrede, dict) or set(anrede) != {"text"}:
            raise PrintModelError(f"{path}.anrede: ein Abschnitt mit genau dem Schlüssel 'text' wird erwartet")
        salutation = _text(f"{path}.anrede.text", anrede["text"])
    named = ("doc_title", "kopf", "anrede", "gruss", "fusszeile")
    return Mail(
        job=STORY_JOBS[doc],
        labels=labels,
        sender=_text(f"{path}.kopf.von", kopf["von"]),
        recipient=_text(f"{path}.kopf.an", kopf["an"]),
        subject=_text(f"{path}.doc_title", story["doc_title"]),
        salutation=salutation,
        sections=_sections(path, story, named),
        closing_lines=_lines(path, story, "gruss"),
        footer_lines=_lines(path, story, "fusszeile"),
    )


def build_story_documents(cfg: Config, texts: Texts) -> tuple[Steckbrief, Zeitungsartikel, Mail, Mail]:
    """The four story documents in `STORY_DOCS` order: Steckbrief, Zeitungsartikel, Anfrage-Mail, Audit-Mail."""
    view = PreAttackView(cfg, texts)
    sheet = view.sheet("labels")
    labels = MailLabels(sender=sheet["mail_from"], recipient=sheet["mail_to"], subject=sheet["mail_subject"])
    stories = {doc: view.story(doc) for doc in STORY_DOCS}
    return (
        _steckbrief(stories["steckbrief"]),
        _zeitungsartikel(stories["zeitungsartikel"]),
        _mail("anfrage_mail", stories["anfrage_mail"], labels),
        _mail("audit_mail", stories["audit_mail"], labels),
    )
