"""Manifest, orphan cleanup and `planspiel print --check` without TeX (PRINT-11, D-19, D-20)."""
import hashlib
import json
from pathlib import Path

import pytest

from planspiel import render, stamp, texbuild
from planspiel.cli import main
from tests.support import MINI_CONTENT_DIR, REPO_ROOT

MINI = REPO_ROOT / "tests" / "fixtures" / "mini_config.json"


def _argv(tmp_path, *extra):
    options = {
        "--config": str(MINI),
        "--content-dir": str(MINI_CONTENT_DIR),
        "--print-dir": str(REPO_ROOT / "print"),
        "--out-dir": str(tmp_path / "out"),
        "--build-dir": str(tmp_path / "build"),
    }
    return ["print", *extra, *[part for item in options.items() for part in item]]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def world(monkeypatch):
    """Fake renderer, TeX and git: `state` is what the next run sees."""
    state = {"docs": {"alpha": "eins\n", "beta": "zwei ä\n"}, "dirty": False}
    monkeypatch.setattr(texbuild, "preflight", lambda **kwargs: [])
    monkeypatch.setattr(render, "render_all", lambda *args, **kwargs: dict(state["docs"]))

    def fake_build(documents, print_dir, build_dir, *, stamp_tex, **kwargs):
        build_dir.mkdir(parents=True, exist_ok=True)
        pdfs = {}
        for job in documents:
            pdfs[job] = build_dir / f"{job}.pdf"
            pdfs[job].write_bytes(b"%PDF-fake-" + job.encode() + stamp_tex.encode("utf-8"))
        return pdfs

    monkeypatch.setattr(texbuild, "build_documents", fake_build)
    monkeypatch.setattr(stamp, "repo_root", lambda *args, **kwargs: Path("."))
    monkeypatch.setattr(stamp, "input_date_utc", lambda repo: "2026-10-19")
    monkeypatch.setattr(stamp, "is_dirty", lambda repo: state["dirty"])
    return state


def _build(tmp_path):
    assert main(_argv(tmp_path)) == 0


def _manifest(tmp_path):
    return json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))


# --- manifest -----------------------------------------------------------------------------------


def test_manifest_records_stamp_hash_and_every_document(world, tmp_path):
    _build(tmp_path)
    manifest = _manifest(tmp_path)
    assert set(manifest) == {"stamp", "hash", "date", "dirty", "documents"}
    assert manifest["date"] == "2026-10-19" and manifest["dirty"] is False
    assert len(manifest["hash"]) == 64 and manifest["stamp"].startswith("Stand 2026-10-19 · " + manifest["hash"][:7])
    assert set(manifest["documents"]) == {"alpha", "beta"}
    alpha = manifest["documents"]["alpha"]
    assert alpha == {
        "pdf": "alpha.pdf",
        "tex_sha256": _sha("eins\n".encode("utf-8")),
        "pdf_sha256": _sha((tmp_path / "out" / "alpha.pdf").read_bytes()),
    }


def test_manifest_is_canonical_utf8_with_lf(world, tmp_path):
    _build(tmp_path)
    raw = (tmp_path / "out" / "manifest.json").read_bytes()
    assert raw.endswith(b"}\n") and b"\r" not in raw
    text = raw.decode("utf-8")
    assert text == json.dumps(json.loads(text), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def test_two_identical_runs_write_identical_manifests(world, tmp_path):
    _build(tmp_path)
    first = (tmp_path / "out" / "manifest.json").read_bytes()
    _build(tmp_path)
    assert (tmp_path / "out" / "manifest.json").read_bytes() == first


def test_dirty_tree_is_recorded_in_the_manifest(world, tmp_path):
    world["dirty"] = True
    _build(tmp_path)
    manifest = _manifest(tmp_path)
    assert manifest["dirty"] is True and manifest["stamp"].endswith("+lokal")


def test_build_removes_pdfs_the_previous_manifest_listed_and_keeps_other_files(world, tmp_path):
    out = tmp_path / "out"
    _build(tmp_path)
    (out / "notes.txt").write_text("keep", encoding="utf-8")
    world["docs"] = {"alpha": "eins\n"}
    _build(tmp_path)
    assert not (out / "beta.pdf").exists()
    assert (out / "notes.txt").read_text(encoding="utf-8") == "keep"
    assert (out / "alpha.pdf").exists()


def test_build_never_deletes_pdfs_the_pipeline_did_not_write(world, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "Anfrage-Mail.pdf").write_bytes(b"%PDF-by-hand")
    _build(tmp_path)
    assert (out / "Anfrage-Mail.pdf").read_bytes() == b"%PDF-by-hand"
    world["docs"] = {"alpha": "eins\n"}
    _build(tmp_path)
    assert (out / "Anfrage-Mail.pdf").exists()
    assert not (out / "beta.pdf").exists()


def test_build_ignores_a_manifest_entry_that_points_outside_the_out_dir(world, tmp_path):
    out = tmp_path / "out"
    _build(tmp_path)
    outside = tmp_path / "outside.pdf"
    outside.write_bytes(b"%PDF-outside")
    manifest = _manifest(tmp_path)
    manifest["documents"]["gamma"] = {"pdf": "../outside.pdf", "tex_sha256": "x", "pdf_sha256": "x"}
    (out / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    _build(tmp_path)
    assert outside.exists()


def test_build_survives_an_unreadable_previous_manifest(world, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "manifest.json").write_text("not json", encoding="utf-8")
    (out / "Zeitungsartikel.pdf").write_bytes(b"%PDF-by-hand")
    _build(tmp_path)
    assert (out / "Zeitungsartikel.pdf").exists()


# --- --check ------------------------------------------------------------------------------------


def test_check_right_after_a_build_is_fresh(world, tmp_path, capsys):
    _build(tmp_path)
    capsys.readouterr()
    assert main(_argv(tmp_path, "--check")) == 0
    out = capsys.readouterr().out
    assert "aktuell" in out and "STALE" not in out
    assert _manifest(tmp_path)["stamp"] in out


def test_check_runs_without_tex(world, monkeypatch, tmp_path):
    _build(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("--check darf TeX nicht anfassen")

    monkeypatch.setattr(texbuild, "preflight", forbidden)
    monkeypatch.setattr(texbuild, "build_documents", forbidden)
    assert main(_argv(tmp_path, "--check")) == 0


def _stale_lines(capsys):
    out = capsys.readouterr().out
    return out, [line for line in out.splitlines() if line.startswith("STALE ")]


def _assert_order_hint(out):
    assert "uv run planspiel print" in out
    assert "final_documents/generated/" in out


def test_check_names_a_changed_document(world, tmp_path, capsys):
    _build(tmp_path)
    capsys.readouterr()
    world["docs"]["beta"] = "zwei geaendert\n"
    assert main(_argv(tmp_path, "--check")) == 1
    out, lines = _stale_lines(capsys)
    assert any(line.startswith("STALE beta") and "Inhalt" in line for line in lines)
    assert not any(line.startswith("STALE alpha") for line in lines)
    _assert_order_hint(out)


def test_check_reports_a_dirty_tree_with_old_and_new_stamp(world, tmp_path, capsys):
    _build(tmp_path)
    old = _manifest(tmp_path)["stamp"]
    capsys.readouterr()
    world["dirty"] = True
    assert main(_argv(tmp_path, "--check")) == 1
    out, lines = _stale_lines(capsys)
    assert len(lines) == 1
    assert old in lines[0] and old + "+lokal" in lines[0]
    _assert_order_hint(out)


def test_check_reports_a_missing_pdf(world, tmp_path, capsys):
    _build(tmp_path)
    capsys.readouterr()
    (tmp_path / "out" / "alpha.pdf").unlink()
    assert main(_argv(tmp_path, "--check")) == 1
    out, lines = _stale_lines(capsys)
    assert len(lines) == 1 and "alpha.pdf" in lines[0] and "fehlt" in lines[0]
    _assert_order_hint(out)


def test_check_reports_a_hand_edited_pdf(world, tmp_path, capsys):
    _build(tmp_path)
    capsys.readouterr()
    (tmp_path / "out" / "beta.pdf").write_bytes(b"%PDF-edited")
    assert main(_argv(tmp_path, "--check")) == 1
    out, lines = _stale_lines(capsys)
    assert len(lines) == 1 and "beta.pdf" in lines[0] and "SHA-256" in lines[0]
    _assert_order_hint(out)


def test_check_reports_an_orphan_pdf(world, tmp_path, capsys):
    _build(tmp_path)
    capsys.readouterr()
    (tmp_path / "out" / "extra.pdf").write_bytes(b"%PDF-extra")
    assert main(_argv(tmp_path, "--check")) == 1
    out, lines = _stale_lines(capsys)
    assert len(lines) == 1 and "extra.pdf" in lines[0] and "Manifest" in lines[0]
    _assert_order_hint(out)


def test_check_reports_a_missing_manifest(world, tmp_path, capsys):
    _build(tmp_path)
    capsys.readouterr()
    (tmp_path / "out" / "manifest.json").unlink()
    assert main(_argv(tmp_path, "--check")) == 1
    out, lines = _stale_lines(capsys)
    assert lines and "manifest.json" in lines[0]
    _assert_order_hint(out)


def test_check_reports_a_document_added_to_the_print_set(world, tmp_path, capsys):
    _build(tmp_path)
    capsys.readouterr()
    world["docs"]["gamma"] = "drei\n"
    assert main(_argv(tmp_path, "--check")) == 1
    _, lines = _stale_lines(capsys)
    assert any(line.startswith("STALE gamma") for line in lines)


def test_check_reports_a_document_removed_from_the_print_set(world, tmp_path, capsys):
    _build(tmp_path)
    capsys.readouterr()
    del world["docs"]["beta"]
    assert main(_argv(tmp_path, "--check")) == 1
    _, lines = _stale_lines(capsys)
    assert any("beta" in line for line in lines)


def test_check_without_any_output_dir_is_stale(world, tmp_path, capsys):
    assert main(_argv(tmp_path, "--check")) == 1
    out, lines = _stale_lines(capsys)
    assert lines and "manifest.json" in lines[0]
    _assert_order_hint(out)


def test_check_stamp_error_is_an_environment_error(world, monkeypatch, tmp_path, capsys):
    _build(tmp_path)
    capsys.readouterr()

    def outside(*args, **kwargs):
        raise stamp.StampError("Git-Aufruf fehlgeschlagen (rev-parse): not a git repository")

    monkeypatch.setattr(stamp, "repo_root", outside)
    assert main(_argv(tmp_path, "--check")) == 2
    assert "ERROR print.stamp" in capsys.readouterr().out


def test_check_with_unreadable_config_is_an_environment_error(world, tmp_path, capsys):
    argv = _argv(tmp_path, "--check")
    argv[argv.index("--config") + 1] = str(tmp_path / "missing.json")
    assert main(argv) == 2
    assert "ERROR print.input" in capsys.readouterr().out


def test_help_lists_the_check_flag(capsys):
    with pytest.raises(SystemExit):
        main(["print", "--help"])
    assert "--check" in capsys.readouterr().out
