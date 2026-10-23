"""Render stage of the print pipeline: strict Jinja environment and the document registry.

Numbers reach the page only as strings formatted in code; `tex_escape` is the Jinja `finalize`
hook and rejects everything else, so a template cannot print a raw number or an undefined name.
"""
import re
from pathlib import Path
from typing import Callable, Dict, Tuple

import jinja2

from planspiel import audience, texbuild
from planspiel.printmodel import build_attack_sheets

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


def tex_escape(value: object) -> str:
    """Escape the LaTeX specials and babel's `"` shorthand in one pass; reject non-strings and control characters."""
    if isinstance(value, jinja2.Undefined):
        str(value)  # StrictUndefined raises UndefinedError here, naming the missing variable
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


def attack_worksheets(cfg, texts, env: jinja2.Environment) -> Dict[str, str]:
    """One attack worksheet per wave, rendered from the print model with angriff.tex.j2."""
    template = env.get_template("angriff.tex.j2")
    return {sheet.job: template.render(sheet=sheet) for sheet in build_attack_sheets(cfg, texts)}


# Each builder takes (cfg, texts, env) and returns {job name: .tex source}.
DocumentBuilder = Callable[..., Dict[str, str]]
DOCUMENT_BUILDERS: Tuple[DocumentBuilder, ...] = (attack_worksheets,)


def render_all(cfg, texts, template_dir: Path) -> Dict[str, str]:
    env = make_env(template_dir)
    documents: Dict[str, str] = {}
    for builder in DOCUMENT_BUILDERS:
        for job, source in builder(cfg, texts, env).items():
            texbuild.check_job_name(job)
            audience.audience_of(job)
            if job in documents:
                raise ValueError(f"Dokument {job!r} wird von mehreren Erzeugern geliefert")
            documents[job] = source
    return {job: documents[job] for job in sorted(documents)}
