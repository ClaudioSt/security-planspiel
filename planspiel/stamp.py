"""Version stamp of the print material (PRINT-11, D-15, D-19).

The stamp reads "Stand <date> · <7 hex>" and, on a tree with local changes in a build input,
ends in "+lokal". The hash covers the rendered .tex of the whole print set plus the style, with
line endings normalised. The date is the UTC date of the last commit touching the data inputs, so
neither the wall clock nor a pure code commit moves it. The stamp itself reaches TeX through a
separate `stamp.tex` written after hashing and never feeds back into the hash.
"""
import hashlib
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Set

from planspiel import texbuild
from planspiel.render import tex_escape

# Inputs whose last commit date names the stamp (D-19).
DATA_INPUTS = ("simulation_config.json", "content/texte.toml", "print/planspiel.sty", "print/templates")
# Inputs whose local modification appends "+lokal". Output directories are never listed, so a
# rebuild cannot make the tree dirty.
BUILD_INPUTS = ("simulation_config.json", "content/texte.toml", "print", "planspiel", "pyproject.toml", "uv.lock")
MANIFEST_NAME = "manifest.json"

GIT_TIMEOUT_S = 30
_ABSOLUTE = re.compile(r"^(?:[A-Za-z]:/|/)")


class StampError(RuntimeError):
    """The stamp cannot be determined (no git checkout, no commit on the inputs)."""


class Stamp(NamedTuple):
    text: str
    digest: str
    date: str
    dirty: bool


def _git(repo: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            stdin=subprocess.DEVNULL,
            timeout=GIT_TIMEOUT_S,
            check=True,
        )
    except FileNotFoundError as exc:
        raise StampError("Git nicht gefunden: der Stand wird aus dem Repository abgeleitet") from exc
    except subprocess.TimeoutExpired as exc:
        raise StampError(f"Git-Aufruf überschritt das Zeitlimit von {GIT_TIMEOUT_S} s ({args[0]})") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip().splitlines()
        raise StampError(
            f"Git-Aufruf fehlgeschlagen ({args[0]}): {detail[-1] if detail else 'kein Git-Repository?'}"
        ) from exc
    return result.stdout


def repo_root(start: Optional[Path] = None) -> Path:
    out = _git(Path(start) if start is not None else Path.cwd(), "rev-parse", "--show-toplevel")
    return Path(out.strip())


def content_hash(documents: Dict[str, str], static_files: Dict[str, bytes]) -> str:
    """SHA-256 over the rendered documents and the files TeX reads besides them."""
    digest = hashlib.sha256()
    for name in sorted(documents):
        digest.update(b"tex\0" + name.encode("utf-8") + b"\0" + documents[name].encode("utf-8") + b"\0")
    for name in sorted(static_files):
        data = static_files[name]
        if name.endswith((".sty", ".tex", ".cls")):
            data = data.replace(b"\r\n", b"\n")
        digest.update(b"file\0" + name.encode("utf-8") + b"\0" + data + b"\0")
    return digest.hexdigest()


def input_date_utc(repo: Path) -> str:
    out = _git(Path(repo), "log", "-1", "--format=%ct", "--", *DATA_INPUTS).strip()
    if not out:
        raise StampError(
            "Kein Commit berührt die Eingaben "
            f"({', '.join(DATA_INPUTS)}): erst committen, dann bauen"
        )
    return datetime.fromtimestamp(int(out), tz=timezone.utc).strftime("%Y-%m-%d")


def is_dirty(repo: Path) -> bool:
    out = _git(Path(repo), "status", "--porcelain", "--untracked-files=all", "--", *BUILD_INPUTS)
    return bool(out.strip())


def stamp_text(digest: str, date: str, dirty: bool) -> str:
    return f"Stand {date} · {digest[:7]}{'+lokal' if dirty else ''}"


def compute_stamp(documents: Dict[str, str], print_dir: Path, repo: Path) -> Stamp:
    static_files = {name: (Path(print_dir) / name).read_bytes() for name in texbuild.STATIC_FILES}
    digest = content_hash(documents, static_files)
    date = input_date_utc(repo)
    dirty = is_dirty(repo)
    return Stamp(stamp_text(digest, date, dirty), digest, date, dirty)


def stamp_tex(text: str) -> str:
    return "\\def\\footerstamp{" + tex_escape(text) + "}\n"


def _slashed(path: object) -> str:
    return str(path).replace("\\", "/").rstrip("/")


def recorded_local_inputs(fls_path: Path, build_dir: Path) -> Set[str]:
    """Files TeX read from the build dir (relative POSIX names), parsed from a `-recorder` .fls."""
    roots: List[str] = [_slashed(build_dir), _slashed(Path(build_dir).resolve())]
    names: Set[str] = set()
    for line in Path(fls_path).read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("PWD "):
            roots.append(_slashed(line[4:].strip()))
            continue
        if not line.startswith("INPUT "):
            continue
        raw = line[6:].strip().replace("\\", "/")
        if _ABSOLUTE.match(raw):
            for root in roots:
                prefix = root.casefold() + "/"
                if raw.casefold().startswith(prefix):
                    names.add(raw[len(prefix):])
                    break
            continue
        parts: List[str] = []
        for part in raw.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if not parts:
                    parts = [".."]
                    break
                parts.pop()
            else:
                parts.append(part)
        if parts and parts[0] != "..":
            names.add("/".join(parts))
    return names
