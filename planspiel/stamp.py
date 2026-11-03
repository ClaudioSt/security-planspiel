"""Version stamp of the print material (PRINT-11, D-15, D-19).

The stamp reads "Stand <date> · <7 hex>" and, on a tree with local changes in a build input,
ends in "+lokal". The hash covers the rendered .tex of the whole print set plus the style, with
line endings normalised. The date is the UTC date of the last commit touching the data inputs, so
neither the wall clock nor a pure code commit moves it. The stamp itself reaches TeX through a
separate `stamp.tex` written after hashing and never feeds back into the hash.
"""
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Mapping, NamedTuple, Optional, Set

from planspiel import texbuild
from planspiel.render import tex_escape

# Inputs whose last commit date names the stamp (D-19).
DATA_INPUTS = (
    "simulation_config.json",
    "content/texte.toml",
    "content/clues.toml",
    "content/mhp_baseline.json",
    "content/assets/images",
    "print/planspiel.sty",
    "print/templates",
)
# Inputs whose local modification appends "+lokal". Output directories are never listed, so a
# rebuild cannot make the tree dirty.
BUILD_INPUTS = (
    "simulation_config.json",
    "content/texte.toml",
    "content/clues.toml",
    "content/mhp_baseline.json",
    "content/assets/images",
    "print",
    "planspiel",
    "pyproject.toml",
    "uv.lock",
)
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


def content_hash(
    documents: Dict[str, str], static_files: Dict[str, bytes], assets: Optional[Mapping[str, bytes]] = None
) -> str:
    """SHA-256 over the rendered documents and the files TeX reads besides them.

    `assets` (images, by fixed name) are hashed byte for byte after the static files; without assets the
    digest equals the one from before assets existed."""
    digest = hashlib.sha256()
    for name in sorted(documents):
        digest.update(b"tex\0" + name.encode("utf-8") + b"\0" + documents[name].encode("utf-8") + b"\0")
    for name in sorted(static_files):
        data = static_files[name]
        if name.endswith((".sty", ".tex", ".cls")):
            data = data.replace(b"\r\n", b"\n")
        digest.update(b"file\0" + name.encode("utf-8") + b"\0" + data + b"\0")
    for name in sorted(assets or {}):
        digest.update(b"asset\0" + name.encode("utf-8") + b"\0" + assets[name] + b"\0")
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


def repo_for_inputs(config: Path) -> Path:
    """The repository holding `config`; a loose config elsewhere falls back to the working directory."""
    try:
        return repo_root(Path(config).resolve().parent)
    except StampError:
        return repo_root()


def _same_path(given: Path, default: Path) -> bool:
    try:
        return os.path.samefile(given, default)
    except OSError:
        return False


def nondefault_inputs(repo: Path, config: Path, content_dir: Path, print_dir: Path) -> List[str]:
    """CLI options whose path is not the repository default. The date and dirty check only describe the
    default inputs (DATA_INPUTS, BUILD_INPUTS), so a build from other paths must count as unofficial."""
    repo = Path(repo)
    expected = (
        ("--config", config, repo / "simulation_config.json"),
        ("--content-dir", content_dir, repo / "content"),
        ("--print-dir", print_dir, repo / "print"),
    )
    return [option for option, given, default in expected if not _same_path(Path(given), default)]


def compute_stamp(
    documents: Dict[str, str],
    print_dir: Path,
    repo: Path,
    *,
    unofficial: bool = False,
    assets: Optional[Mapping[str, Path]] = None,
) -> Stamp:
    static_files = {name: (Path(print_dir) / name).read_bytes() for name in texbuild.STATIC_FILES}
    asset_bytes = {name: Path(path).read_bytes() for name, path in (assets or {}).items()}
    digest = content_hash(documents, static_files, asset_bytes)
    date = input_date_utc(repo)
    dirty = is_dirty(repo) or unofficial
    return Stamp(stamp_text(digest, date, dirty), digest, date, dirty)


def stamp_tex(text: str) -> str:
    return "\\def\\footerstamp{" + tex_escape(text) + "}\n"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_manifest(out_dir: Path, version: Stamp, documents: Dict[str, str], pdfs: Dict[str, Path]) -> Path:
    """Record stamp, hash and per-document SHA-256 next to the published PDFs (D-20)."""
    entries = {}
    for job in sorted(documents):
        pdf = Path(pdfs[job])
        entries[job] = {
            "pdf": pdf.name,
            "tex_sha256": _sha256(documents[job].encode("utf-8")),
            "pdf_sha256": _sha256(pdf.read_bytes()),
        }
    manifest = {
        "stamp": version.text,
        "hash": version.digest,
        "date": version.date,
        "dirty": version.dirty,
        "documents": entries,
    }
    path = Path(out_dir) / MANIFEST_NAME
    path.write_text(
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def previous_pdf_names(out_dir: Path) -> Set[str]:
    """PDF file names the manifest in `out_dir` lists, i.e. the files an earlier build wrote itself.

    Unreadable manifests and names that are not plain file names yield nothing: cleanup may only
    ever touch files this pipeline published into `out_dir`.
    """
    try:
        manifest = json.loads((Path(out_dir) / MANIFEST_NAME).read_text(encoding="utf-8"))
        names = {
            entry.get("pdf", f"{job}.pdf") for job, entry in manifest["documents"].items()
        }
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return set()
    return {name for name in names if isinstance(name, str) and name.endswith(".pdf") and Path(name).name == name}


def check_freshness(documents: Dict[str, str], version: Stamp, out_dir: Path) -> List[str]:
    """Why the PDFs in `out_dir` do not match the current inputs; an empty list means fresh."""
    out_dir = Path(out_dir)
    manifest_path = out_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        return [f"{MANIFEST_NAME} fehlt in {out_dir}: das Druckmaterial wurde hier noch nicht gebaut"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        recorded = manifest["documents"]
        recorded_stamp = manifest["stamp"]
        recorded_hash = manifest["hash"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f"{MANIFEST_NAME} ist unlesbar oder hat ein unerwartetes Format ({exc})"]
    findings: List[str] = []
    if recorded_stamp != version.text or recorded_hash != version.digest:
        findings.append(f"Stempel: Manifest nennt \"{recorded_stamp}\", die Eingaben ergeben \"{version.text}\"")
    for job in sorted(documents):
        entry = recorded.get(job)
        if entry is None:
            findings.append(f"{job}: nicht im Manifest (neues Dokument im Druckumfang)")
        elif entry.get("tex_sha256") != _sha256(documents[job].encode("utf-8")):
            findings.append(f"{job}: Inhalt hat sich geändert (gerenderte .tex weicht vom Manifest ab)")
    for job in sorted(recorded):
        if job not in documents:
            findings.append(f"{job}: nicht mehr im Druckumfang, die PDF ist veraltet")
    known = set()
    for job in sorted(recorded):
        name = recorded[job].get("pdf", f"{job}.pdf")
        known.add(name)
        pdf = out_dir / name
        if not pdf.is_file():
            findings.append(f"{name}: fehlt")
        elif _sha256(pdf.read_bytes()) != recorded[job].get("pdf_sha256"):
            findings.append(f"{name}: SHA-256 weicht vom Manifest ab (von Hand verändert oder anderer Stand)")
    for pdf in sorted(out_dir.glob("*.pdf")):
        if pdf.name not in known:
            findings.append(f"{pdf.name}: nicht im Manifest (verwaiste Datei)")
    return findings


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
