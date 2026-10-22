"""Driver tests: pass loop, error extraction, job-name safety. Fake runner only, no TeX needed."""
from pathlib import Path

import pytest

from planspiel import texbuild
from planspiel.texbuild import TexBuildError


class FakeLualatex:
    """Runner stand-in: writes aux/log/pdf into the job dir per pass, in the style of a real run."""

    def __init__(self, aux_sequence, *, returncode=0, log="", pdf=b"%PDF-fake"):
        self.aux_sequence = list(aux_sequence)
        self.returncode = returncode
        self.log = log
        self.pdf = pdf
        self.calls = []
        self.stale_seen = []

    def __call__(self, cmd, *, cwd, timeout_s, env=None):
        cwd = Path(cwd)
        job = Path(cmd[-1]).stem
        if not self.calls:
            self.stale_seen = [p.name for p in cwd.iterdir() if p.stem == job]
        self.calls.append({"cmd": list(cmd), "cwd": cwd, "timeout_s": timeout_s, "env": env})
        aux = self.aux_sequence[min(len(self.calls), len(self.aux_sequence)) - 1]
        (cwd / f"{job}.aux").write_bytes(aux)
        (cwd / f"{job}.log").write_text(self.log, encoding="utf-8")
        if self.returncode == 0:
            (cwd / f"{job}.pdf").write_bytes(self.pdf)
        return self.returncode, "", ""


def test_command_carries_all_safety_flags(tmp_path):
    fake = FakeLualatex([b"A", b"A"])
    texbuild.run_lualatex(tmp_path, "smoke.tex", runner=fake)
    cmd = fake.calls[0]["cmd"]
    for flag in ("--disable-installer", "-interaction=nonstopmode", "-halt-on-error",
                 "-file-line-error", "-recorder"):
        assert flag in cmd
    assert cmd[0] == "lualatex" and cmd[-1] == "smoke.tex"
    assert "--shell-escape" not in cmd
    assert fake.calls[0]["cwd"] == tmp_path
    assert fake.calls[0]["timeout_s"] == 300


def test_stale_outputs_are_deleted_before_the_first_pass(tmp_path):
    for suffix in ("aux", "pdf", "log", "fls"):
        (tmp_path / f"smoke.{suffix}").write_text("old", encoding="utf-8")
    (tmp_path / "other.aux").write_text("keep", encoding="utf-8")
    fake = FakeLualatex([b"A", b"A"])
    texbuild.run_lualatex(tmp_path, "smoke.tex", runner=fake)
    assert fake.stale_seen == []
    assert (tmp_path / "other.aux").exists()


def test_stable_aux_stops_after_two_passes(tmp_path):
    fake = FakeLualatex([b"A", b"A"])
    pdf = texbuild.run_lualatex(tmp_path, "smoke.tex", runner=fake)
    assert len(fake.calls) == 2
    assert pdf == tmp_path / "smoke.pdf"


def test_aux_that_settles_in_pass_two_needs_three_passes(tmp_path):
    fake = FakeLualatex([b"A", b"B", b"B"])
    texbuild.run_lualatex(tmp_path, "smoke.tex", runner=fake)
    assert len(fake.calls) == 3


def test_aux_that_never_settles_raises(tmp_path):
    fake = FakeLualatex([b"A", b"B", b"C"])
    with pytest.raises(TexBuildError, match="stabil"):
        texbuild.run_lualatex(tmp_path, "smoke.tex", runner=fake)


def test_environment_carries_the_belt_and_braces_variables(tmp_path):
    fake = FakeLualatex([b"A", b"A"])
    texbuild.run_lualatex(tmp_path, "smoke.tex", runner=fake)
    env = fake.calls[0]["env"]
    assert env["SOURCE_DATE_EPOCH"] == "0" and env["FORCE_SOURCE_DATE"] == "1"


def test_nonzero_exit_reports_job_code_and_relevant_log_lines(tmp_path):
    noise = [f"noise line {i}" for i in range(30)]
    relevant = [f"! error number {i}" for i in range(15)]
    log = "\n".join(
        noise + ["./smoke.tex:12: Undefined control sequence.", "File `x.sty' not found."] + relevant
    )
    fake = FakeLualatex([b"A"], returncode=1, log=log)
    with pytest.raises(TexBuildError) as info:
        texbuild.run_lualatex(tmp_path, "smoke.tex", runner=fake)
    message = str(info.value)
    assert "smoke" in message and "1" in message
    assert "./smoke.tex:12: Undefined control sequence." in message
    assert "noise line" not in message
    assert len([ln for ln in message.splitlines() if ln.startswith("!")]) <= 10


def test_missing_package_name_reaches_the_error(tmp_path):
    log = "! LaTeX Error: File `planspielmissingpkg.sty' not found.\n"
    fake = FakeLualatex([b"A"], returncode=1, log=log)
    with pytest.raises(TexBuildError, match="planspielmissingpkg"):
        texbuild.run_lualatex(tmp_path, "smoke.tex", runner=fake)


def test_timeout_from_the_runner_propagates(tmp_path):
    def runner(cmd, *, cwd, timeout_s, env=None):
        raise TexBuildError(f"Zeitlimit von {timeout_s} s ueberschritten")

    with pytest.raises(TexBuildError, match="5 s"):
        texbuild.run_lualatex(tmp_path, "smoke.tex", timeout_s=5, runner=runner)


STAMP_TEX = "\\def\\footerstamp{Stand 2000-01-01 · test000}\n"


def make_print_dir(tmp_path):
    print_dir = tmp_path / "print"
    print_dir.mkdir()
    (print_dir / "planspiel.sty").write_text("% style\n", encoding="utf-8", newline="\n")
    return print_dir


def test_build_documents_writes_lf_utf8_and_builds_in_sorted_order(tmp_path):
    print_dir = make_print_dir(tmp_path)
    build_dir = tmp_path / "build"
    order = []

    def run(job_dir, tex_name, *, timeout_s):
        order.append(tex_name)
        return Path(job_dir) / (Path(tex_name).stem + ".pdf")

    result = texbuild.build_documents(
        {"b-doc": "zeile eins\nzeile ä\n", "a_doc": "x\n"}, print_dir, build_dir, stamp_tex=STAMP_TEX, run=run
    )
    assert order == ["a_doc.tex", "b-doc.tex"]
    assert result == {"a_doc": build_dir / "a_doc.pdf", "b-doc": build_dir / "b-doc.pdf"}
    assert (build_dir / "planspiel.sty").read_bytes() == b"% style\n"
    raw = (build_dir / "b-doc.tex").read_bytes()
    assert raw == "zeile eins\nzeile ä\n".encode("utf-8")
    assert b"\r" not in raw
    assert b"\r" not in (build_dir / "a_doc.tex").read_bytes()


@pytest.mark.parametrize("bad", ["../x", "Angriff 1", "", "-lead", "a/b", "A", "x.tex"])
def test_build_documents_rejects_unsafe_job_names_before_writing(tmp_path, bad):
    print_dir = make_print_dir(tmp_path)
    build_dir = tmp_path / "build"
    with pytest.raises(ValueError):
        texbuild.build_documents(
            {"ok": "x", bad: "y"}, print_dir, build_dir, stamp_tex=STAMP_TEX, run=lambda *a, **k: None
        )
    assert not build_dir.exists()


def test_static_files_lists_the_style():
    assert texbuild.STATIC_FILES == ("planspiel.sty",)


def test_build_documents_writes_stamp_tex_before_running_tex(tmp_path):
    print_dir = make_print_dir(tmp_path)
    build_dir = tmp_path / "build"
    seen = []

    def run(job_dir, tex_name, *, timeout_s):
        seen.append((Path(job_dir) / "stamp.tex").read_bytes())
        return Path(job_dir) / (Path(tex_name).stem + ".pdf")

    texbuild.build_documents({"a": "x\n"}, print_dir, build_dir, stamp_tex=STAMP_TEX, run=run)
    assert seen == [STAMP_TEX.encode("utf-8")]
    assert b"\r" not in (build_dir / "stamp.tex").read_bytes()


def test_build_documents_requires_a_stamp(tmp_path):
    print_dir = make_print_dir(tmp_path)
    with pytest.raises(TypeError):
        texbuild.build_documents({"a": "x\n"}, print_dir, tmp_path / "build", run=lambda *a, **k: None)
