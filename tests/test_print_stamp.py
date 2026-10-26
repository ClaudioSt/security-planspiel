"""Version stamp core: content hash, UTC commit date, scoped dirty flag, recorder parsing (PRINT-11, D-15, D-19)."""
import pytest

from planspiel import stamp
from planspiel.stamp import Stamp, StampError
from tests.support.gitrepo import commit_all, make_repo, write

DIGEST = "ab12cd34" + "0" * 56
STY = b"% style\nline two\n"


# --- content hash -------------------------------------------------------------------------------


def test_hash_is_a_sha256_hex_and_ignores_insertion_order():
    one = stamp.content_hash({"a": "x\n", "b": "y\n"}, {"planspiel.sty": STY})
    two = stamp.content_hash({"b": "y\n", "a": "x\n"}, {"planspiel.sty": STY})
    assert one == two
    assert len(one) == 64 and set(one) <= set("0123456789abcdef")


def test_hash_changes_with_a_document_or_the_style():
    base = stamp.content_hash({"a": "x\n"}, {"planspiel.sty": STY})
    assert stamp.content_hash({"a": "x2\n"}, {"planspiel.sty": STY}) != base
    assert stamp.content_hash({"a": "x\n"}, {"planspiel.sty": STY + b"% more\n"}) != base
    assert stamp.content_hash({"a": "x\n", "b": ""}, {"planspiel.sty": STY}) != base


def test_hash_does_not_depend_on_style_line_endings():
    lf = stamp.content_hash({"a": "x\n"}, {"planspiel.sty": b"% a\n% b\n"})
    crlf = stamp.content_hash({"a": "x\n"}, {"planspiel.sty": b"% a\r\n% b\r\n"})
    assert lf == crlf


def test_hash_cannot_take_a_stamp():
    import inspect

    assert list(inspect.signature(stamp.content_hash).parameters) == ["documents", "static_files", "assets"]


def test_hash_separates_name_from_content():
    first = stamp.content_hash({"ab": "c"}, {})
    second = stamp.content_hash({"a": "bc"}, {})
    assert first != second


# --- text forms ---------------------------------------------------------------------------------


def test_stamp_text_uses_seven_hex_characters_and_the_middle_dot():
    assert stamp.stamp_text(DIGEST, "2026-10-19", False) == "Stand 2026-10-19 \u00b7 ab12cd3"
    assert stamp.stamp_text(DIGEST, "2026-10-19", True) == "Stand 2026-10-19 \u00b7 ab12cd3+lokal"


def test_stamp_tex_is_one_line_with_the_text_escaped():
    out = stamp.stamp_tex("Stand 2026-10-19 \u00b7 ab12cd3+lokal")
    assert out == "\\def\\footerstamp{Stand 2026-10-19 \u00b7 ab12cd3+lokal}\n"
    assert out.count("\n") == 1
    escaped = stamp.stamp_tex("a_b&c")
    assert "a\\_b\\&c" in escaped


# --- git: commit date ---------------------------------------------------------------------------


@pytest.fixture
def repo(tmp_path):
    root = make_repo(tmp_path / "repo")
    write(root, "simulation_config.json", "{}\n")
    write(root, "content/texte.toml", "a = 1\n")
    write(root, "content/clues.toml", "b = 1\n")
    write(root, "print/planspiel.sty", "% sty\n")
    write(root, "print/templates/a.tex.j2", "a\n")
    write(root, "content/assets/images/a.png", "png\n")
    write(root, "planspiel/x.py", "x = 1\n")
    write(root, "pyproject.toml", "[project]\n")
    write(root, "uv.lock", "lock\n")
    write(root, ".planning/STATE.md", "state\n")
    commit_all(root, "initial", "2026-10-20T01:30:00+02:00")
    return root


def test_date_is_the_utc_date_of_the_commit(repo):
    assert stamp.input_date_utc(repo) == "2026-10-19"


def test_a_code_only_commit_leaves_the_date_unchanged(repo):
    write(repo, "planspiel/x.py", "x = 2\n")
    commit_all(repo, "code", "2026-10-25T12:00:00+00:00")
    assert stamp.input_date_utc(repo) == "2026-10-19"


def test_a_template_commit_moves_the_date(repo):
    write(repo, "print/templates/a.tex.j2", "changed\n")
    commit_all(repo, "template", "2026-10-26T12:00:00+00:00")
    assert stamp.input_date_utc(repo) == "2026-10-26"


def test_a_texts_commit_moves_the_date(repo):
    write(repo, "content/texte.toml", "a = 2\n")
    commit_all(repo, "texts", "2026-10-27T12:00:00+00:00")
    assert stamp.input_date_utc(repo) == "2026-10-27"


def test_an_image_commit_moves_the_date(repo):
    write(repo, "content/assets/images/a.png", "changed png\n")
    commit_all(repo, "image", "2026-10-28T12:00:00+00:00")
    assert stamp.input_date_utc(repo) == "2026-10-28"


def test_no_commit_on_the_data_inputs_is_an_error(tmp_path):
    root = make_repo(tmp_path / "bare")
    write(root, "README.md", "x\n")
    commit_all(root, "readme", "2026-10-20T12:00:00+00:00")
    with pytest.raises(StampError, match="Commit"):
        stamp.input_date_utc(root)


def test_outside_a_checkout_is_an_error(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    outside = tmp_path / "plain"
    outside.mkdir()
    with pytest.raises(StampError, match="Git"):
        stamp.input_date_utc(outside)
    with pytest.raises(StampError, match="Git"):
        stamp.is_dirty(outside)
    with pytest.raises(StampError, match="Git"):
        stamp.repo_root(outside)


def test_repo_root_finds_the_toplevel(repo):
    assert stamp.repo_root(repo / "print").resolve() == repo.resolve()


def test_the_clues_are_a_data_and_a_build_input():
    """content/clues.toml feeds the facilitator booklet, so a change moves the date and marks the tree (research F15)."""
    assert "content/clues.toml" in stamp.DATA_INPUTS
    assert "content/clues.toml" in stamp.BUILD_INPUTS


def test_a_clues_commit_moves_the_date(repo):
    write(repo, "content/clues.toml", "b = 2\n")
    commit_all(repo, "clues", "2026-10-29T12:00:00+00:00")
    assert stamp.input_date_utc(repo) == "2026-10-29"


# --- git: dirty flag ----------------------------------------------------------------------------


def test_clean_tree_is_not_dirty(repo):
    assert stamp.is_dirty(repo) is False


@pytest.mark.parametrize(
    "rel",
    [
        "planspiel/x.py",
        "content/texte.toml",
        "content/clues.toml",
        "print/planspiel.sty",
        "simulation_config.json",
        "uv.lock",
        "content/assets/images/a.png",
    ],
)
def test_modified_build_input_is_dirty(repo, rel):
    write(repo, rel, "changed\n")
    assert stamp.is_dirty(repo) is True


@pytest.mark.parametrize(
    "rel",
    ["print/new.sty", "planspiel/new.py", "print/templates/new.tex.j2", "content/assets/images/new.png"],
)
def test_untracked_build_input_is_dirty(repo, rel):
    write(repo, rel, "new\n")
    assert stamp.is_dirty(repo) is True


@pytest.mark.parametrize(
    "rel",
    ["final_documents/generated/x.pdf", "build/print/y.tex", ".planning/STATE.md"],
)
def test_changes_outside_the_build_inputs_are_not_dirty(repo, rel):
    write(repo, rel, "changed\n")
    assert stamp.is_dirty(repo) is False


# --- compute_stamp ------------------------------------------------------------------------------


def test_compute_stamp_matches_the_parts(repo):
    docs = {"a": "x\n", "b": "y\n"}
    result = stamp.compute_stamp(docs, repo / "print", repo)
    assert isinstance(result, Stamp)
    digest = stamp.content_hash(docs, {"planspiel.sty": (repo / "print" / "planspiel.sty").read_bytes()})
    assert result.digest == digest
    assert result.date == "2026-10-19"
    assert result.dirty is False
    assert result.text == stamp.stamp_text(digest, "2026-10-19", False)


def test_digest_ignores_the_dirty_flag(repo):
    docs = {"a": "x\n"}
    clean = stamp.compute_stamp(docs, repo / "print", repo)
    write(repo, "planspiel/x.py", "x = 99\n")
    dirty = stamp.compute_stamp(docs, repo / "print", repo)
    assert dirty.dirty is True and clean.dirty is False
    assert dirty.digest == clean.digest
    assert dirty.text == clean.text + "+lokal"


# --- inputs outside the repository defaults (WR-07) -----------------------------------------------


def test_default_inputs_are_official(repo):
    assert stamp.nondefault_inputs(repo, repo / "simulation_config.json", repo / "content", repo / "print") == []
    roundabout = repo / "print" / ".." / "print"
    assert stamp.nondefault_inputs(repo, repo / "simulation_config.json", repo / "content", roundabout) == []


@pytest.mark.parametrize(
    ("option", "config", "content", "print_dir"),
    [
        ("--config", "experiment.json", "content", "print"),
        ("--content-dir", "simulation_config.json", "other", "print"),
        ("--print-dir", "simulation_config.json", "content", "elsewhere"),
    ],
)
def test_inputs_off_the_defaults_are_named(repo, option, config, content, print_dir):
    (repo / "experiment.json").write_text("{}", encoding="utf-8")
    (repo / "other").mkdir()
    (repo / "elsewhere").mkdir()
    found = stamp.nondefault_inputs(repo, repo / config, repo / content, repo / print_dir)
    assert found == [option]


def test_missing_inputs_count_as_off_the_defaults(repo):
    assert stamp.nondefault_inputs(repo, repo / "nope.json", repo / "content", repo / "print") == ["--config"]


def test_unofficial_inputs_mark_the_stamp_lokal(repo):
    docs = {"a": "x"}
    official = stamp.compute_stamp(docs, repo / "print", repo)
    marked = stamp.compute_stamp(docs, repo / "print", repo, unofficial=True)
    assert marked.dirty is True and marked.digest == official.digest
    assert marked.text == official.text + "+lokal"


def test_repo_follows_the_config_path_not_the_working_directory(repo, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # not a git repository
    assert stamp.repo_for_inputs(repo / "simulation_config.json").resolve() == repo.resolve()


def test_repo_falls_back_to_the_working_directory_for_a_loose_config(repo, tmp_path, monkeypatch):
    loose = tmp_path / "loose"
    loose.mkdir()
    (loose / "c.json").write_text("{}", encoding="utf-8")
    monkeypatch.chdir(repo)
    assert stamp.repo_for_inputs(loose / "c.json").resolve() == repo.resolve()


# --- recorder -----------------------------------------------------------------------------------

FLS = """PWD C:/work/build
INPUT C:/Users/x/AppData/Local/Programs/MiKTeX/tex/latex/base/article.cls
INPUT ./smoke.tex
INPUT smoke.aux
INPUT ./planspiel.sty
INPUT ./stamp.tex
INPUT C:/WINDOWS/Fonts/arial.ttf
INPUT C:/work/build/extra.dat
INPUT C:/elsewhere/other.tex
OUTPUT smoke.log
OUTPUT smoke.aux
OUTPUT smoke.pdf
"""


def test_recorded_local_inputs_keeps_only_files_in_the_build_dir(tmp_path):
    fls = tmp_path / "smoke.fls"
    fls.write_text(FLS, encoding="utf-8")
    found = stamp.recorded_local_inputs(fls, tmp_path)
    assert found == {"smoke.tex", "smoke.aux", "planspiel.sty", "stamp.tex", "extra.dat"}


def test_recorded_local_inputs_ignores_relative_paths_that_leave_the_build_dir(tmp_path):
    fls = tmp_path / "x.fls"
    fls.write_text("PWD C:/work/build\nINPUT ../up.tex\nINPUT ./x.tex\n", encoding="utf-8")
    assert stamp.recorded_local_inputs(fls, tmp_path) == {"x.tex"}


def test_manifest_name():
    assert stamp.MANIFEST_NAME == "manifest.json"
