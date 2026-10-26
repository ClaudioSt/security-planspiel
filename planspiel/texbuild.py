"""Non-interactive LuaLaTeX driver: preflight, bounded subprocesses, aux-stable pass loop.

Every TeX subprocess runs with the MiKTeX installer disabled, stdin closed and a timeout that
kills the whole process tree. A bare call on a missing package would hang on MiKTeX's invisible
installer dialog.
"""
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Tuple

# Probe file -> MiKTeX package id (for `miktex packages install`).
TEX_PROBES: Dict[str, str] = {
    "fontspec.sty": "fontspec",
    "babel.sty": "babel",
    "ngerman.ldf": "babel-german",
    "geometry.sty": "geometry",
    "xcolor.sty": "xcolor",
    "colortbl.sty": "colortbl",
    "array.sty": "tools",
    "tabularx.sty": "tools",
    "tikz.sty": "pgf",
    "graphicx.sty": "graphics",
    "multicol.sty": "tools",
}

# Files copied from the print directory into every build directory.
STATIC_FILES = ("planspiel.sty",)
# Images TeX may read, by fixed name (D-19). The names are code constants: no content string ever chooses
# a file name, and the files are looked up under `<content dir>/ASSET_DIR` only.
ASSET_DIR = Path("assets") / "images"
ASSET_FILES = ("zeitungsartikel_bild_audit.png", "zeitungsartikel_bild_fabrik.png")
# Written by build_documents after hashing; never part of the content hash.
STAMP_FILE = "stamp.tex"

LUALATEX = [
    "lualatex",
    "--disable-installer",
    "-interaction=nonstopmode",
    "-halt-on-error",
    "-file-line-error",
    "-recorder",
]

KPSEWHICH_TIMEOUT_S = 30
KILL_SETTLE_S = 1.0
JOB_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_LOG_FILE_LINE = re.compile(r"^\S+:\d+: ")

# (returncode, stdout, stderr); raises TexBuildError on timeout.
Runner = Callable[..., Tuple[int, str, str]]


class TexBuildError(RuntimeError):
    """A TeX tool failed, hung, or produced a non-reproducible result."""


@dataclass(frozen=True)
class MissingTex:
    file: str
    package: str


def check_job_name(job: str) -> None:
    if not JOB_NAME.match(job):
        raise ValueError(f"Ungültiger Jobname {job!r}: erlaubt sind a-z, 0-9, _ und - (nicht am Anfang)")


def check_asset_name(name: str) -> None:
    if not name or name in (".", "..") or "/" in name or "\\" in name or ":" in name or Path(name).name != name:
        raise ValueError(f"Ungültiger Asset-Name {name!r}: nur ein einfacher Dateiname ohne Pfad ist erlaubt")


def asset_paths(content_dir: Path) -> Dict[str, Path]:
    """The fixed asset names mapped to their files under `content_dir`; a missing file stops the build."""
    folder = Path(content_dir) / ASSET_DIR
    paths = {}
    for name in ASSET_FILES:
        path = folder / name
        if not path.is_file():
            raise TexBuildError(f"Bild {name} fehlt: erwartet in {folder}")
        paths[name] = path
    return paths


def _kill_tree(pid: int) -> None:
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                timeout=30,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass
        time.sleep(KILL_SETTLE_S)  # taskkill returns before the killed processes released their file handles
    else:
        try:  # the child leads its own session (see _run_bounded), so its pid is the group id
            os.killpg(pid, signal.SIGKILL)
        except OSError:
            pass


def _run_bounded(
    cmd: List[str],
    *,
    cwd: Optional[Path] = None,
    timeout_s: float,
    env: Optional[Dict[str, str]] = None,
    popen=subprocess.Popen,
    kill_tree: Callable[[int], None] = _kill_tree,
) -> Tuple[int, str, str]:
    session = {} if sys.platform == "win32" else {"start_new_session": True}  # own group: killpg reaches grandchildren
    proc = popen(
        cmd,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        **session,
    )
    try:
        out, err = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired as exc:
        kill_tree(proc.pid)
        proc.kill()
        try:
            proc.communicate(timeout=10)
        except Exception:  # noqa: BLE001 - reaping is best effort, the error below is what matters
            pass
        raise TexBuildError(
            f"Zeitlimit von {timeout_s} s überschritten: {cmd[0]} wurde samt Kindprozessen beendet"
        ) from exc
    return proc.returncode, out, err


def _found_names(stdout: str) -> set:
    names = set()
    for line in stdout.splitlines():
        line = line.strip()
        if line:
            names.add(re.split(r"[\\/]", line)[-1].lower())
    return names


def missing_tex_files(probe_files: List[str], *, run: Optional[Runner] = None) -> List[str]:
    """Probe files that kpsewhich cannot find, in input order."""
    run = run or _run_bounded
    try:
        _, out, err = run(
            ["kpsewhich", "--miktex-disable-installer", *probe_files], timeout_s=KPSEWHICH_TIMEOUT_S
        )
        if "unrecognized option" in err:  # TeX Live: no installer, so the bare call cannot hang
            _, out, err = run(["kpsewhich", *probe_files], timeout_s=KPSEWHICH_TIMEOUT_S)
    except TexBuildError as exc:
        raise TexBuildError(
            "kpsewhich hängt vermutlich am MiKTeX-Installer-Dialog; "
            f"mit deaktiviertem Installer neu starten ({exc})"
        ) from exc
    found = _found_names(out)
    return [name for name in probe_files if name.lower() not in found]


def missing_tex(*, run: Optional[Runner] = None) -> List[MissingTex]:
    return [MissingTex(name, TEX_PROBES[name]) for name in missing_tex_files(list(TEX_PROBES), run=run)]


def preflight(*, which: Callable[[str], Optional[str]] = shutil.which, run: Optional[Runner] = None) -> List[str]:
    """Human-readable problems; an empty list means the TeX toolchain is ready."""
    problems = []
    for tool in ("lualatex", "kpsewhich"):
        if which(tool) is None:
            problems.append(f"{tool} nicht im PATH gefunden")
    if problems:
        return problems
    return [f"{item.file} fehlt (MiKTeX-Paket {item.package})" for item in missing_tex(run=run)]


def _log_excerpt(log_path: Path) -> List[str]:
    if not log_path.exists():
        return []
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    picked = [
        line for line in lines
        if line.startswith("!") or _LOG_FILE_LINE.match(line) or "not found" in line
    ]
    return picked[:10]


def run_lualatex(
    job_dir: Path,
    tex_name: str,
    *,
    timeout_s: int = 300,
    max_passes: int = 3,
    runner: Optional[Runner] = None,
) -> Path:
    """Build `tex_name` in `job_dir` until the aux file is stable; return the PDF path."""
    runner = runner or _run_bounded
    job_dir = Path(job_dir)
    stem = Path(tex_name).stem
    for suffix in ("aux", "pdf", "log", "fls"):
        stale = job_dir / f"{stem}.{suffix}"
        try:
            stale.unlink(missing_ok=True)
        except OSError as exc:  # e.g. a PDF still open in a viewer on Windows
            raise TexBuildError(f"{stale.name} lässt sich nicht löschen (in einem Programm geöffnet?): {exc}") from exc
    env = {**os.environ, "SOURCE_DATE_EPOCH": "0", "FORCE_SOURCE_DATE": "1"}  # belt and braces only
    aux_path = job_dir / f"{stem}.aux"
    previous = None
    for _ in range(max_passes):
        code, _, _ = runner([*LUALATEX, tex_name], cwd=job_dir, timeout_s=timeout_s, env=env)
        if code != 0:
            excerpt = "\n".join(_log_excerpt(job_dir / f"{stem}.log"))
            raise TexBuildError(f"{stem}: lualatex endete mit Exit-Code {code}\n{excerpt}".rstrip())
        current = aux_path.read_bytes() if aux_path.exists() else b""
        if current == previous:
            break
        previous = current
    else:
        raise TexBuildError(
            f"{stem}: die aux-Datei stabilisiert sich nach {max_passes} Durchläufen nicht "
            "(PDF wäre nicht reproduzierbar)"
        )
    pdf = job_dir / f"{stem}.pdf"
    if not pdf.exists():
        raise TexBuildError(f"{stem}: lualatex lieferte kein PDF")
    return pdf


def build_documents(
    documents: Dict[str, str],
    print_dir: Path,
    build_dir: Path,
    *,
    stamp_tex: str,
    timeout_s: int = 300,
    run: Optional[Callable[..., Path]] = None,
    assets: Optional[Mapping[str, Path]] = None,
) -> Dict[str, Path]:
    """Write each document as `<job>.tex` into `build_dir` and build it; return `{job: pdf}`.

    `stamp_tex` is written to `stamp.tex` before TeX runs; the style stops the build without it.
    `assets` (name -> file) are copied next to the documents under their plain names.
    """
    assets = dict(assets or {})
    for job in documents:
        check_job_name(job)
    for name in assets:
        check_asset_name(name)
    run = run or run_lualatex
    build_dir = Path(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    for name in STATIC_FILES:
        shutil.copyfile(Path(print_dir) / name, build_dir / name)
    for name in sorted(assets):
        shutil.copyfile(assets[name], build_dir / name)
    (build_dir / STAMP_FILE).write_text(stamp_tex, encoding="utf-8", newline="\n")
    pdfs = {}
    for job in sorted(documents):
        (build_dir / f"{job}.tex").write_text(documents[job], encoding="utf-8", newline="\n")
        pdfs[job] = run(build_dir, f"{job}.tex", timeout_s=timeout_s)
    return pdfs
