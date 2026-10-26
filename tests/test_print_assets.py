"""Fixed-name, hashed asset path for print images (PRINT-12, Phase 4 D-19, T-05-33, T-05-34)."""
from pathlib import Path

import pytest

from planspiel import stamp, texbuild
from tests.support import CONTENT_DIR, MINI_CONTENT_DIR

STAMP_TEX = "\\def\\footerstamp{Stand 2026-10-19}\n"
DOCS = {"a": "x\n", "b": "y\n"}
STATIC = {"planspiel.sty": b"% style\nline two\n"}
# Hash of DOCS + STATIC computed with the code before assets existed (plan 05-08 state).
HASH_WITHOUT_ASSETS = "015c946c1f4b3d85359d157acf0813930947dc54f623d267706897ebd021717c"


def make_print_dir(tmp_path):
    print_dir = tmp_path / "print"
    print_dir.mkdir()
    (print_dir / "planspiel.sty").write_text("% style\n", encoding="utf-8", newline="\n")
    return print_dir


# --- asset list and paths -----------------------------------------------------------------------


def test_asset_names_are_code_constants():
    assert texbuild.ASSET_DIR == Path("assets") / "images"
    assert texbuild.ASSET_FILES == ("zeitungsartikel_bild_audit.png", "zeitungsartikel_bild_fabrik.png")


def test_asset_paths_maps_exactly_the_fixed_names_to_existing_files():
    paths = texbuild.asset_paths(CONTENT_DIR)
    assert list(paths) == list(texbuild.ASSET_FILES)
    for name, path in paths.items():
        assert path == CONTENT_DIR / "assets" / "images" / name
        assert path.is_file()


def test_asset_paths_ignores_other_files_in_the_image_folder(tmp_path):
    images = tmp_path / "assets" / "images"
    images.mkdir(parents=True)
    for name in texbuild.ASSET_FILES:
        (images / name).write_bytes(b"png")
    (images / "extra.png").write_bytes(b"other")
    assert set(texbuild.asset_paths(tmp_path)) == set(texbuild.ASSET_FILES)


def test_a_missing_image_raises_naming_it(tmp_path):
    images = tmp_path / "assets" / "images"
    images.mkdir(parents=True)
    (images / texbuild.ASSET_FILES[0]).write_bytes(b"png")
    with pytest.raises(texbuild.TexBuildError, match=texbuild.ASSET_FILES[1]):
        texbuild.asset_paths(tmp_path)


def test_a_missing_image_folder_raises(tmp_path):
    with pytest.raises(texbuild.TexBuildError, match=texbuild.ASSET_FILES[0]):
        texbuild.asset_paths(tmp_path)


def test_a_directory_in_place_of_an_image_raises(tmp_path):
    images = tmp_path / "assets" / "images"
    images.mkdir(parents=True)
    (images / texbuild.ASSET_FILES[0]).write_bytes(b"png")
    (images / texbuild.ASSET_FILES[1]).mkdir()
    with pytest.raises(texbuild.TexBuildError, match=texbuild.ASSET_FILES[1]):
        texbuild.asset_paths(tmp_path)


def test_the_mini_content_carries_both_images():
    assert set(texbuild.asset_paths(MINI_CONTENT_DIR)) == set(texbuild.ASSET_FILES)


# --- copy into the build directory --------------------------------------------------------------


def test_build_documents_copies_each_asset_before_tex_runs(tmp_path):
    print_dir = make_print_dir(tmp_path)
    source = tmp_path / "src"
    source.mkdir()
    (source / "one.png").write_bytes(b"\x89PNG one")
    (source / "two.png").write_bytes(b"\x89PNG two")
    build_dir = tmp_path / "build"
    seen = []

    def run(job_dir, tex_name, *, timeout_s):
        seen.append(sorted(p.name for p in Path(job_dir).glob("*.png")))
        return Path(job_dir) / (Path(tex_name).stem + ".pdf")

    texbuild.build_documents(
        {"a": "x\n"}, print_dir, build_dir, stamp_tex=STAMP_TEX, run=run,
        assets={"one.png": source / "one.png", "two.png": source / "two.png"},
    )
    assert seen == [["one.png", "two.png"]]
    assert (build_dir / "one.png").read_bytes() == b"\x89PNG one"
    assert (build_dir / "two.png").read_bytes() == b"\x89PNG two"


def test_build_documents_without_assets_copies_none(tmp_path):
    print_dir = make_print_dir(tmp_path)
    build_dir = tmp_path / "build"
    texbuild.build_documents(
        {"a": "x\n"}, print_dir, build_dir, stamp_tex=STAMP_TEX,
        run=lambda job_dir, tex_name, *, timeout_s: Path(job_dir) / "a.pdf",
    )
    assert not list(build_dir.glob("*.png"))


@pytest.mark.parametrize(
    "bad", ["../x.png", "a/b.png", "a\\b.png", "..", ".", "", "/abs.png", "C:\\x.png"]
)
def test_asset_names_with_separators_or_dots_are_rejected_before_writing(tmp_path, bad):
    print_dir = make_print_dir(tmp_path)
    source = tmp_path / "x.png"
    source.write_bytes(b"png")
    build_dir = tmp_path / "build"
    with pytest.raises(ValueError):
        texbuild.build_documents(
            {"a": "x\n"}, print_dir, build_dir, stamp_tex=STAMP_TEX, run=lambda *a, **k: None,
            assets={bad: source},
        )
    assert not build_dir.exists()


# --- content hash -------------------------------------------------------------------------------


def test_hash_without_assets_equals_the_hash_of_the_time_before_assets():
    assert stamp.content_hash(DOCS, STATIC) == HASH_WITHOUT_ASSETS
    assert stamp.content_hash(DOCS, STATIC, assets={}) == HASH_WITHOUT_ASSETS
    assert stamp.content_hash(DOCS, STATIC, assets=None) == HASH_WITHOUT_ASSETS


def test_a_one_byte_change_of_an_asset_changes_the_hash():
    base = stamp.content_hash(DOCS, STATIC, assets={"a.png": b"\x89PNG0"})
    assert base != HASH_WITHOUT_ASSETS
    assert stamp.content_hash(DOCS, STATIC, assets={"a.png": b"\x89PNG1"}) != base


def test_reordering_the_asset_dict_does_not_change_the_hash():
    one = stamp.content_hash(DOCS, STATIC, assets={"a.png": b"1", "b.png": b"2"})
    two = stamp.content_hash(DOCS, STATIC, assets={"b.png": b"2", "a.png": b"1"})
    assert one == two


def test_an_asset_is_not_a_static_file_of_the_same_name():
    as_asset = stamp.content_hash(DOCS, {}, assets={"planspiel.sty": b"x"})
    as_static = stamp.content_hash(DOCS, {"planspiel.sty": b"x"})
    assert as_asset != as_static


def test_asset_bytes_are_hashed_without_line_ending_normalisation():
    lf = stamp.content_hash(DOCS, STATIC, assets={"a.png": b"a\nb"})
    crlf = stamp.content_hash(DOCS, STATIC, assets={"a.png": b"a\r\nb"})
    assert lf != crlf


def test_the_asset_name_is_part_of_the_hash():
    assert stamp.content_hash(DOCS, STATIC, assets={"a.png": b"x"}) != stamp.content_hash(
        DOCS, STATIC, assets={"b.png": b"x"}
    )


# --- stamp inputs -------------------------------------------------------------------------------


def test_the_image_folder_is_a_data_and_a_build_input():
    assert "content/assets/images" in stamp.DATA_INPUTS
    assert "content/assets/images" in stamp.BUILD_INPUTS


def test_compute_stamp_hashes_the_asset_bytes(tmp_path):
    from tests.support.gitrepo import commit_all, make_repo, write

    repo = make_repo(tmp_path / "repo")
    write(repo, "simulation_config.json", "{}\n")
    write(repo, "content/texte.toml", "a = 1\n")
    write(repo, "print/planspiel.sty", "% sty\n")
    image = repo / "content" / "assets" / "images" / "a.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"\x89PNG0")
    commit_all(repo, "initial", "2026-10-20T01:30:00+02:00")
    first = stamp.compute_stamp(DOCS, repo / "print", repo, assets={"a.png": image})
    plain = stamp.compute_stamp(DOCS, repo / "print", repo)
    expected = stamp.content_hash(
        DOCS, {"planspiel.sty": (repo / "print" / "planspiel.sty").read_bytes()}, {"a.png": b"\x89PNG0"}
    )
    assert first.digest == expected
    assert first.digest != plain.digest
    image.write_bytes(b"\x89PNG1")
    second = stamp.compute_stamp(DOCS, repo / "print", repo, assets={"a.png": image})
    assert second.digest != first.digest
    assert second.dirty is True and first.dirty is False


# --- probes, package list, binary attribute ------------------------------------------------------


def test_graphicx_and_multicol_are_probed():
    assert texbuild.TEX_PROBES["graphicx.sty"] == "graphics"
    assert texbuild.TEX_PROBES["multicol.sty"] == "tools"


def test_graphics_is_in_the_install_list():
    lines = (Path(__file__).resolve().parents[1] / "print" / "miktex-packages.txt").read_text(encoding="utf-8").split()
    assert "graphics" in lines and "tools" in lines
    assert lines == sorted(lines)
