"""Preflight tests for the TeX driver: fake kpsewhich only, no TeX installation needed."""
import re
import shutil
import subprocess

import pytest

from planspiel import texbuild
from planspiel.texbuild import MissingTex, TexBuildError
from tests.support.tex import PRINT_DIR, tex_skip_reason


class FakeRun:
    """Stands in for the bounded runner; records every call."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, cmd, *, cwd=None, timeout_s, env=None):
        self.calls.append({"cmd": list(cmd), "cwd": cwd, "timeout_s": timeout_s})
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


FONTSPEC_PATH = r"C:\Users\x\AppData\Local\Programs\MiKTeX\tex\latex\fontspec\FontSpec.sty"


def test_missing_tex_files_reports_only_the_absent_probe():
    fake = FakeRun([(2, FONTSPEC_PATH + "\n", "")])
    missing = texbuild.missing_tex_files(["fontspec.sty", "colortbl.sty"], run=fake)
    assert missing == ["colortbl.sty"]
    call = fake.calls[0]
    assert call["cmd"] == ["kpsewhich", "--miktex-disable-installer", "fontspec.sty", "colortbl.sty"]
    assert call["timeout_s"] == 30


def test_missing_tex_files_matches_case_insensitive_and_posix_paths():
    fake = FakeRun([(0, "/usr/share/texmf/tex/latex/xcolor/XColor.sty\n", "")])
    assert texbuild.missing_tex_files(["xcolor.sty"], run=fake) == []


def test_missing_tex_files_falls_back_without_flag_when_option_is_unknown():
    fake = FakeRun([
        (1, "", "kpsewhich: unrecognized option '--miktex-disable-installer'"),
        (0, "/texlive/fontspec.sty\n", ""),
    ])
    assert texbuild.missing_tex_files(["fontspec.sty", "colortbl.sty"], run=fake) == ["colortbl.sty"]
    assert fake.calls[1]["cmd"] == ["kpsewhich", "fontspec.sty", "colortbl.sty"]


def test_missing_tex_files_does_not_fall_back_for_other_stderr():
    fake = FakeRun([(2, "", "some other warning")])
    texbuild.missing_tex_files(["colortbl.sty"], run=fake)
    assert len(fake.calls) == 1


def test_kpsewhich_timeout_mentions_the_installer_dialog():
    fake = FakeRun([TexBuildError("Zeitlimit von 30 s ueberschritten")])
    with pytest.raises(TexBuildError, match="Installer"):
        texbuild.missing_tex_files(["colortbl.sty"], run=fake)


def test_preflight_reports_missing_lualatex_and_kpsewhich():
    problems = texbuild.preflight(which=lambda name: None)
    assert any("lualatex" in p for p in problems)
    assert any("kpsewhich" in p for p in problems)


def test_preflight_reports_each_missing_probe_with_package_id():
    found = "\n".join(f"C:\\tex\\{name}" for name in texbuild.TEX_PROBES if name != "colortbl.sty")
    fake = FakeRun([(2, found, "")])
    problems = texbuild.preflight(which=lambda name: name, run=fake)
    assert problems == ["colortbl.sty fehlt (MiKTeX-Paket colortbl)"]


def test_preflight_is_empty_when_everything_is_installed():
    found = "\n".join(f"C:\\tex\\{name}" for name in texbuild.TEX_PROBES)
    fake = FakeRun([(0, found, "")])
    assert texbuild.preflight(which=lambda name: name, run=fake) == []


def test_missing_tex_returns_structured_entries():
    found = "\n".join(f"C:\\tex\\{name}" for name in texbuild.TEX_PROBES if name != "colortbl.sty")
    fake = FakeRun([(2, found, "")])
    assert texbuild.missing_tex(run=fake) == [MissingTex("colortbl.sty", "colortbl")]


def test_probe_table_maps_files_to_miktex_packages():
    assert texbuild.TEX_PROBES["colortbl.sty"] == "colortbl"
    assert texbuild.TEX_PROBES["ngerman.ldf"] == "babel-german"
    assert texbuild.TEX_PROBES["array.sty"] == "tools"
    assert texbuild.TEX_PROBES["tabularx.sty"] == "tools"


class FakeProc:
    """Minimal Popen stand-in: first communicate() times out when asked, second returns."""

    def __init__(self, *, hang, returncode=0, out="o", err="e"):
        self.pid = 4242
        self.hang = hang
        self.returncode = returncode
        self._reply = (out, err)
        self.killed = False
        self.communicate_calls = 0

    def communicate(self, timeout=None):
        self.communicate_calls += 1
        if self.hang and self.communicate_calls == 1:
            raise subprocess.TimeoutExpired("cmd", timeout)
        return self._reply

    def kill(self):
        self.killed = True


def test_run_bounded_closes_stdin_and_uses_an_argument_list():
    seen = {}

    def popen(cmd, **kwargs):
        seen["cmd"], seen["kwargs"] = cmd, kwargs
        return FakeProc(hang=False, returncode=3, out="out", err="err")

    result = texbuild._run_bounded(["kpsewhich", "x.sty"], cwd=None, timeout_s=7, popen=popen)
    assert result == (3, "out", "err")
    assert seen["cmd"] == ["kpsewhich", "x.sty"]
    assert seen["kwargs"]["stdin"] == subprocess.DEVNULL
    assert not seen["kwargs"].get("shell")
    assert seen["kwargs"]["encoding"] == "utf-8"
    assert seen["kwargs"]["errors"] == "replace"


def test_run_bounded_kills_the_process_tree_on_timeout():
    proc = FakeProc(hang=True)
    killed = []
    with pytest.raises(TexBuildError, match="12 s"):
        texbuild._run_bounded(
            ["lualatex", "x.tex"], cwd=None, timeout_s=12,
            popen=lambda cmd, **kw: proc, kill_tree=killed.append,
        )
    assert killed == [4242]
    assert proc.killed


def test_run_bounded_starts_its_own_session_on_posix(monkeypatch):
    seen = {}

    def popen(cmd, **kwargs):
        seen.update(kwargs)
        return FakeProc(hang=False)

    monkeypatch.setattr(texbuild.sys, "platform", "linux")
    texbuild._run_bounded(["lualatex", "x.tex"], cwd=None, timeout_s=7, popen=popen)
    assert seen["start_new_session"] is True


def test_run_bounded_leaves_the_session_alone_on_windows(monkeypatch):
    seen = {}

    def popen(cmd, **kwargs):
        seen.update(kwargs)
        return FakeProc(hang=False)

    monkeypatch.setattr(texbuild.sys, "platform", "win32")
    texbuild._run_bounded(["lualatex", "x.tex"], cwd=None, timeout_s=7, popen=popen)
    assert "start_new_session" not in seen


def test_kill_tree_signals_the_whole_process_group_on_posix(monkeypatch):
    signalled = []
    monkeypatch.setattr(texbuild.sys, "platform", "linux")
    monkeypatch.setattr(texbuild.os, "killpg", lambda pgid, sig: signalled.append((pgid, sig)), raising=False)
    monkeypatch.setattr(texbuild.signal, "SIGKILL", 9, raising=False)
    texbuild._kill_tree(4242)
    assert signalled == [(4242, 9)]


def test_kill_tree_ignores_a_group_that_is_already_gone(monkeypatch):
    def gone(pgid, sig):
        raise ProcessLookupError(pgid)

    monkeypatch.setattr(texbuild.sys, "platform", "linux")
    monkeypatch.setattr(texbuild.os, "killpg", gone, raising=False)
    monkeypatch.setattr(texbuild.signal, "SIGKILL", 9, raising=False)
    texbuild._kill_tree(4242)


# --- style drift (fast, no TeX) -------------------------------------------------------------

PACKAGE_LINE = re.compile(r"\\(?:RequirePackage|usepackage)(?:\[[^\]]*\])?\{([^}]*)\}")
OPTION_IMPLIED = ("colortbl.sty", "ngerman.ldf")
LOCAL_PACKAGES = {"planspiel"}  # the shared style, loaded by every template


def _loaded_packages():
    sources = [PRINT_DIR / "planspiel.sty", *sorted((PRINT_DIR / "templates").glob("*.j2"))]
    names = set()
    for source in sources:
        for match in PACKAGE_LINE.finditer(source.read_text(encoding="utf-8")):
            parts = (part.strip() for part in match.group(1).split(","))
            names.update(part for part in parts if part and part not in LOCAL_PACKAGES)
    return names


def test_every_loaded_package_is_a_probe():
    packages = _loaded_packages()
    assert packages, "print/planspiel.sty loads no packages?"
    missing = sorted(f"{name}.sty" for name in packages if f"{name}.sty" not in texbuild.TEX_PROBES)
    assert not missing, f"not covered by TEX_PROBES: {missing}"


def test_option_implied_files_are_probes():
    for name in OPTION_IMPLIED:
        assert name in texbuild.TEX_PROBES


def test_miktex_package_list_covers_the_probes_and_is_sorted():
    lines = (PRINT_DIR / "miktex-packages.txt").read_text(encoding="utf-8").splitlines()
    assert lines == sorted(set(lines))
    assert not any(line.startswith("#") or not line.strip() for line in lines)
    expected = set(texbuild.TEX_PROBES.values()) | {"tikzfill"}
    assert set(lines) == expected


def test_skip_reason_without_packages_only_checks_the_engine():
    if shutil.which("lualatex") is None:
        assert tex_skip_reason(require_packages=False) is not None
    else:
        assert tex_skip_reason(require_packages=False) is None
