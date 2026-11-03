"""`planspiel print`: preflight first, then render, build and publish (PRINT-01, D-13, D-14, D-17)."""
from pathlib import Path

import pytest

from planspiel import render, stamp, texbuild
from planspiel.cli import main
from tests.support import MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"
PROBLEM = "colortbl.sty fehlt (MiKTeX-Paket colortbl)"


@pytest.fixture(autouse=True)
def fixed_git(monkeypatch):
    monkeypatch.setattr(stamp, "repo_root", lambda *args, **kwargs: Path("."))
    monkeypatch.setattr(stamp, "input_date_utc", lambda repo: "2026-10-19")
    monkeypatch.setattr(stamp, "is_dirty", lambda repo: False)
    monkeypatch.setattr(stamp, "nondefault_inputs", lambda *args, **kwargs: [])


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
    monkeypatch.setattr(render, "render_all", lambda *args, **kwargs: seen.append("render") or {"spieler-smoke": "x"})

    def fake_build(documents, print_dir, build_dir, *, stamp_tex, **kwargs):
        seen.append("build")
        assert stamp_tex.startswith("\\def\\footerstamp{Stand 2026-10-19 · ")
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
    assert (tmp_path / "out" / "spieler-smoke.pdf").read_bytes() == b"%PDF-fake"
    assert "spieler-smoke.pdf" in out
    assert "1 Dokument(e) gebaut" in out
    assert calls == ["render", "build"]


def test_success_prints_the_stamp(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    assert main(_argv(tmp_path)) == 0
    assert "Stand: Stand 2026-10-19 · " in capsys.readouterr().out


def test_dirty_tree_marks_the_stamp(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    monkeypatch.setattr(stamp, "is_dirty", lambda repo: True)
    assert main(_argv(tmp_path)) == 0
    assert "+lokal" in capsys.readouterr().out


def test_stamp_error_stops_before_the_build(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])

    def outside(*args, **kwargs):
        raise stamp.StampError("Git-Aufruf fehlgeschlagen (rev-parse): not a git repository")

    monkeypatch.setattr(stamp, "repo_root", outside)
    assert main(_argv(tmp_path)) == 1
    out = capsys.readouterr().out
    assert "ERROR print.stamp Git-Aufruf fehlgeschlagen" in out
    assert calls == ["render"]
    assert not (tmp_path / "out").exists()


def test_no_registered_document_builds_nothing(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    monkeypatch.setattr(render, "DOCUMENT_BUILDERS", ())
    assert main(_argv(tmp_path)) == 0
    assert "0 Dokument(e) gebaut" in capsys.readouterr().out


def test_tex_failure_returns_one(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    monkeypatch.setattr(render, "render_all", lambda *args, **kwargs: {"spieler-smoke": "x"})

    def broken(*args, **kwargs):
        raise texbuild.TexBuildError("spieler-smoke: lualatex endete mit Exit-Code 1")

    monkeypatch.setattr(texbuild, "build_documents", broken)
    assert main(_argv(tmp_path)) == 1
    out = capsys.readouterr().out
    assert "ERROR print.tex spieler-smoke: lualatex endete mit Exit-Code 1" in out
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


def test_print_model_error_exits_one_with_its_own_code(monkeypatch, tmp_path, capsys):
    from planspiel.printmodel import PrintModelError

    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])

    def broken(*args, **kwargs):
        raise PrintModelError("Welle 1: Fall 3 ist nicht handrechenbar")

    monkeypatch.setattr(render, "render_all", broken)
    assert main(_argv(tmp_path)) == 1
    out = capsys.readouterr().out
    assert "ERROR print.model Welle 1: Fall 3 ist nicht handrechenbar" in out
    assert not (tmp_path / "out").exists()


def test_print_model_error_makes_check_fail_with_two(monkeypatch, tmp_path, capsys):
    from planspiel.printmodel import PrintModelError

    def broken(*args, **kwargs):
        raise PrintModelError("Welle 1: Fall 3 ist nicht handrechenbar")

    monkeypatch.setattr(render, "render_all", broken)
    assert main([*_argv(tmp_path), "--check"]) == 2
    assert "ERROR print.model" in capsys.readouterr().out


def test_check_without_style_file_exits_two_not_with_a_traceback(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(render, "render_all", lambda *args, **kwargs: {"spieler-smoke": "x"})
    empty_print_dir = tmp_path / "print"
    (empty_print_dir / "templates").mkdir(parents=True)
    argv = [*_argv(tmp_path, **{"--print-dir": str(empty_print_dir)}), "--check"]
    assert main(argv) == 2
    out = capsys.readouterr().out
    assert "ERROR print.stamp" in out
    assert "planspiel.sty" in out


def test_build_without_style_file_exits_one_with_a_message(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    monkeypatch.setattr(render, "render_all", lambda *args, **kwargs: {"spieler-smoke": "x"})
    argv = _argv(tmp_path, **{"--print-dir": str(tmp_path / "no_print_dir")})
    assert main(argv) == 1
    assert "ERROR print.stamp" in capsys.readouterr().out


def test_missing_text_key_exits_two_under_check(monkeypatch, tmp_path, capsys):
    def broken(*args, **kwargs):
        raise KeyError("Schlüssel 'sheets.labels.kz' fehlt in der Inhaltsquelle")

    monkeypatch.setattr(render, "render_all", broken)
    assert main([*_argv(tmp_path), "--check"]) == 2
    out = capsys.readouterr().out
    assert "ERROR print.model" in out
    assert "sheets.labels.kz" in out


def test_invalid_job_name_is_reported_by_check(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(render, "DOCUMENT_BUILDERS", (lambda cfg, texts, env, clues: {"Angriff-X": "x"},))
    assert main([*_argv(tmp_path), "--check"]) == 2
    out = capsys.readouterr().out
    assert "ERROR print.render" in out
    assert "Angriff-X" in out


def test_locked_pdf_names_the_file_and_exits_one(monkeypatch, calls, tmp_path, capsys):
    import shutil

    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])

    def locked(source, target, *args, **kwargs):
        raise PermissionError(13, "Der Prozess kann nicht auf die Datei zugreifen", str(target))

    monkeypatch.setattr(shutil, "copyfile", locked)
    assert main(_argv(tmp_path)) == 1
    out = capsys.readouterr().out
    assert "ERROR print.publish" in out
    assert "spieler-smoke.pdf" in out


def _content_with_number_in_prose(tmp_path):
    import shutil

    content = tmp_path / "content"
    shutil.copytree(MINI_CONTENT_DIR, content)
    texte = content / "texte.toml"
    text = texte.read_text(encoding="utf-8")
    assert 'focus = "Zugriffe regeln"' in text
    texte.write_text(text.replace('focus = "Zugriffe regeln"', 'focus = "Zugriffe regeln, Schwelle 23"'), encoding="utf-8")
    return content


def test_number_in_prose_stops_the_build_before_render(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    content = _content_with_number_in_prose(tmp_path)
    assert main(_argv(tmp_path, **{"--content-dir": str(content)})) == 1
    out = capsys.readouterr().out
    assert "ERROR print.texts" in out
    assert "measures.M1.focus" in out
    assert calls == []
    assert not (tmp_path / "out").exists()


def test_number_in_prose_makes_check_fail_with_two(monkeypatch, calls, tmp_path, capsys):
    content = _content_with_number_in_prose(tmp_path)
    assert main([*_argv(tmp_path, **{"--content-dir": str(content)}), "--check"]) == 2
    assert "ERROR print.texts" in capsys.readouterr().out
    assert calls == []


def test_inputs_off_the_defaults_mark_the_stamp_and_are_named(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    monkeypatch.setattr(stamp, "nondefault_inputs", lambda *args, **kwargs: ["--config"])
    assert main(_argv(tmp_path)) == 0
    out = capsys.readouterr().out
    assert "+lokal" in out
    assert "--config" in out


LEAK = "\documentclass{article}\begin{document}Ransomware\end{document}"


def test_a_veil_leak_stops_the_build_before_the_stamp_and_tex(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    monkeypatch.setattr(render, "render_all", lambda *args, **kwargs: {"spieler-smoke": LEAK})
    monkeypatch.setattr(stamp, "compute_stamp", lambda *args, **kwargs: pytest.fail("stamp must not run"))
    assert main(_argv(tmp_path)) == 1
    out = capsys.readouterr().out
    assert "ERROR print.veil veil.name spieler-smoke:" in out
    assert "1 Fehler" in out
    assert calls == []
    assert not (tmp_path / "out").exists()


def test_a_veil_leak_makes_check_fail_with_two(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(render, "render_all", lambda *args, **kwargs: {"spieler-smoke": LEAK})
    monkeypatch.setattr(stamp, "compute_stamp", lambda *args, **kwargs: pytest.fail("stamp must not run"))
    assert main([*_argv(tmp_path), "--check"]) == 2
    out = capsys.readouterr().out
    assert "ERROR print.veil" in out
    assert calls == []


def _content_without_an_image(tmp_path, name):
    import shutil

    content = tmp_path / "content"
    shutil.copytree(MINI_CONTENT_DIR, content)
    (content / "assets" / "images" / name).unlink()
    return content


@pytest.mark.parametrize("name", texbuild.ASSET_FILES)
def test_a_missing_image_stops_the_build_with_print_input(monkeypatch, calls, tmp_path, capsys, name):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    content = _content_without_an_image(tmp_path, name)
    assert main(_argv(tmp_path, **{"--content-dir": str(content)})) == 1
    out = capsys.readouterr().out
    assert "ERROR print.input" in out
    assert name in out
    assert "1 Fehler" in out
    assert calls == []
    assert not (tmp_path / "out").exists()


def test_a_missing_image_makes_check_fail_with_two(monkeypatch, calls, tmp_path, capsys):
    content = _content_without_an_image(tmp_path, texbuild.ASSET_FILES[0])
    assert main([*_argv(tmp_path, **{"--content-dir": str(content)}), "--check"]) == 2
    out = capsys.readouterr().out
    assert "ERROR print.input" in out
    assert texbuild.ASSET_FILES[0] in out
    assert calls == []


def test_the_assets_under_the_content_dir_reach_stamp_and_build(monkeypatch, tmp_path):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    monkeypatch.setattr(render, "render_all", lambda *args, **kwargs: {"spieler-smoke": "x"})
    seen = {}
    real_stamp = stamp.compute_stamp

    def spy_stamp(*args, **kwargs):
        seen["stamp"] = kwargs.get("assets")
        return real_stamp(*args, **kwargs)

    def fake_build(documents, print_dir, build_dir, *, stamp_tex, **kwargs):
        seen["build"] = kwargs.get("assets")
        build_dir.mkdir(parents=True, exist_ok=True)
        (build_dir / "spieler-smoke.pdf").write_bytes(b"%PDF-fake")
        return {"spieler-smoke": build_dir / "spieler-smoke.pdf"}

    monkeypatch.setattr(stamp, "compute_stamp", spy_stamp)
    monkeypatch.setattr(texbuild, "build_documents", fake_build)
    assert main(_argv(tmp_path)) == 0
    expected = {name: MINI_CONTENT_DIR / "assets" / "images" / name for name in texbuild.ASSET_FILES}
    assert seen == {"stamp": expected, "build": expected}


def test_check_hashes_the_images_but_builds_nothing(monkeypatch, calls, tmp_path):
    seen = {}
    real_stamp = stamp.compute_stamp

    def spy_stamp(*args, **kwargs):
        seen["assets"] = kwargs.get("assets")
        return real_stamp(*args, **kwargs)

    monkeypatch.setattr(stamp, "compute_stamp", spy_stamp)
    main([*_argv(tmp_path), "--check"])
    assert set(seen["assets"]) == set(texbuild.ASSET_FILES)
    assert calls == ["render"]


# ---- content/clues.toml is a print input (PRINT-10, research F15) -----------------------------------------------


def _content_with_clues(tmp_path, text=None):
    import shutil

    content = tmp_path / "content"
    shutil.copytree(MINI_CONTENT_DIR, content)
    if text is None:
        (content / "clues.toml").unlink()
    else:
        (content / "clues.toml").write_text(text, encoding="utf-8")
    return content


BROKEN_CLUES = """[[clue]]
attack = "ransomware"
source = "story.steckbrief.betrieb.bullets"
quote = "Dieses Zitat steht in keinem Dokument des Inhalts"
why = "Absichtlich falsch."
"""


def test_the_clues_of_the_content_dir_reach_the_render_stage(monkeypatch, tmp_path):
    from planspiel.texts import load_clues

    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    seen = {}

    def spy(cfg, texts, template_dir, **kwargs):
        seen["clues"] = kwargs.get("clues")
        return {"spieler-smoke": "x"}

    monkeypatch.setattr(render, "render_all", spy)
    main([*_argv(tmp_path), "--check"])
    assert seen["clues"] == load_clues(MINI_CONTENT_DIR / "clues.toml")
    assert len(seen["clues"]) == 6


def test_a_clue_error_stops_the_build_before_render(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    content = _content_with_clues(tmp_path, BROKEN_CLUES)
    assert main(_argv(tmp_path, **{"--content-dir": str(content)})) == 1
    out = capsys.readouterr().out
    assert "ERROR print.clues clues.quote_not_found clues[1]:" in out
    assert "ERROR print.clues clues.too_few" in out
    assert "Fehler" in out
    assert calls == []
    assert not (tmp_path / "out").exists()


def test_a_clue_error_makes_check_fail_with_two(monkeypatch, calls, tmp_path, capsys):
    content = _content_with_clues(tmp_path, BROKEN_CLUES)
    assert main([*_argv(tmp_path, **{"--content-dir": str(content)}), "--check"]) == 2
    assert "ERROR print.clues" in capsys.readouterr().out
    assert calls == []


def test_a_missing_clues_file_stops_the_build_with_print_input(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    content = _content_with_clues(tmp_path, None)
    assert main(_argv(tmp_path, **{"--content-dir": str(content)})) == 1
    out = capsys.readouterr().out
    assert "ERROR print.input" in out
    assert "clues.toml" in out
    assert calls == []


def _content_with_baseline(tmp_path, text):
    import shutil

    from planspiel.was_neu import BASELINE_FILE

    content = tmp_path / "content"
    shutil.copytree(MINI_CONTENT_DIR, content)
    (content / BASELINE_FILE).write_text(text, encoding="utf-8")
    return content


def test_the_cli_hands_the_baseline_file_to_render_all(monkeypatch, calls, tmp_path):
    from planspiel.was_neu import BASELINE_FILE, Baseline
    from tests.support import CONTENT_DIR

    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    seen = []
    monkeypatch.setattr(render, "render_all", lambda *args, **kwargs: seen.append(kwargs) or {"spieler-smoke": "x"})
    assert main(_argv(tmp_path)) == 0
    assert seen[-1]["baseline"] is None  # the mini content dir carries no baseline file
    content = _content_with_baseline(tmp_path, (CONTENT_DIR / BASELINE_FILE).read_text(encoding="utf-8"))
    assert main(_argv(tmp_path, **{"--content-dir": str(content)})) == 0
    assert isinstance(seen[-1]["baseline"], Baseline)


def test_a_malformed_baseline_stops_the_print_with_an_input_error(monkeypatch, calls, tmp_path, capsys):
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    content = _content_with_baseline(tmp_path, "{ not json")
    assert main(_argv(tmp_path, **{"--content-dir": str(content)})) == 1
    out = capsys.readouterr().out
    assert "ERROR print.input" in out and "mhp_baseline.json" in out
    assert calls == []


def test_a_malformed_baseline_makes_check_fail_with_two(monkeypatch, calls, tmp_path, capsys):
    content = _content_with_baseline(tmp_path, '{"schema": 99}')
    argv = _argv(tmp_path, **{"--content-dir": str(content)})
    argv.insert(1, "--check")
    assert main(argv) == 2
    assert "ERROR print.input" in capsys.readouterr().out
    assert calls == []
