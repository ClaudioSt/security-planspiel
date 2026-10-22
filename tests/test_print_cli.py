"""`planspiel print`: preflight first, then render, build and publish (PRINT-01, D-13, D-14, D-17)."""
import pytest

from planspiel import render, texbuild
from planspiel.cli import main
from tests.support import MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
PROBLEM = "colortbl.sty fehlt (MiKTeX-Paket colortbl)"


def _argv(tmp_path, **overrides):
    options = {
        "--config": str(MINI),
        "--content-dir": str(MINI_CONTENT_DIR),
        "--print-dir": str(REPO_ROOT / "print"),
        "--out-dir": str(tmp_path / "out"),
        "--build-dir": str(tmp_path / "build"),
    }
    options.update(overrides)
    return ["print", *[part for item in options.items() for part in item]]


@pytest.fixture
def calls(monkeypatch):
    seen = []
    monkeypatch.setattr(render, "render_all", lambda *args, **kwargs: seen.append("render") or {"smoke": "x"})

    def fake_build(documents, print_dir, build_dir, **kwargs):
        seen.append("build")
        build_dir.mkdir(parents=True, exist_ok=True)
        pdfs = {}
        for job in documents:
            pdfs[job] = build_dir / f"{job}.pdf"
            pdfs[job].write_bytes(b"%PDF-fake")
        return pdfs

    monkeypatch.setattr(texbuild, "build_documents", fake_build)
    return seen


def test_preflight_failure_stops_before_render_and_build(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [PROBLEM])
    assert main(_argv(tmp_path)) == 1
    out = capsys.readouterr().out
    assert f"ERROR print.preflight {PROBLEM}" in out
    assert "miktex packages install" in out
    assert "print/miktex-packages.txt" in out
    assert "1 Fehler" in out
    assert calls == []
    assert not (tmp_path / "out").exists()


def test_success_publishes_pdfs(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    assert main(_argv(tmp_path)) == 0
    out = capsys.readouterr().out
    assert (tmp_path / "out" / "smoke.pdf").read_bytes() == b"%PDF-fake"
    assert "smoke.pdf" in out
    assert "1 Dokument(e) gebaut" in out
    assert calls == ["render", "build"]


def test_no_registered_document_builds_nothing(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    monkeypatch.setattr(render, "DOCUMENT_BUILDERS", ())
    assert main(_argv(tmp_path)) == 0
    assert "0 Dokument(e) gebaut" in capsys.readouterr().out


def test_tex_failure_returns_one(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    monkeypatch.setattr(render, "render_all", lambda *args, **kwargs: {"smoke": "x"})

    def broken(*args, **kwargs):
        raise texbuild.TexBuildError("smoke: lualatex endete mit Exit-Code 1")

    monkeypatch.setattr(texbuild, "build_documents", broken)
    assert main(_argv(tmp_path)) == 1
    out = capsys.readouterr().out
    assert "ERROR print.tex smoke: lualatex endete mit Exit-Code 1" in out
    assert not (tmp_path / "out").exists()


def test_unreadable_config_returns_one(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    assert main(_argv(tmp_path, **{"--config": str(tmp_path / "missing.json")})) == 1
    assert "ERROR print.input" in capsys.readouterr().out
    assert calls == []


def test_help_lists_the_options(capsys):
    with pytest.raises(SystemExit) as raised:
        main(["print", "--help"])
    assert raised.value.code == 0
    out = capsys.readouterr().out
    for option in ("--config", "--content-dir", "--print-dir", "--out-dir", "--build-dir"):
        assert option in out
