"""Preflight tests for the TeX driver: fake kpsewhich only, no TeX installation needed."""
import subprocess

import pytest

from planspiel import texbuild
from planspiel.texbuild import MissingTex, TexBuildError


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
