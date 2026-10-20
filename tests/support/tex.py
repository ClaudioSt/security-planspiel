"""Shared helpers for the print pipeline tests."""
import shutil
from functools import lru_cache
from typing import Optional

from planspiel import texbuild
from tests.support import REPO_ROOT

PRINT_DIR = REPO_ROOT / "print"
SMOKE_TEX = REPO_ROOT / "tests" / "fixtures" / "print" / "smoke.tex"


@lru_cache(maxsize=None)
def tex_skip_reason(require_packages: bool = True) -> Optional[str]:
    """Why PDF tests cannot run here, or None when they can."""
    if shutil.which("lualatex") is None:
        return "lualatex nicht im PATH gefunden"
    if not require_packages:
        return None
    try:
        problems = texbuild.preflight()
    except texbuild.TexBuildError as exc:
        return str(exc)
    return "; ".join(problems) if problems else None
