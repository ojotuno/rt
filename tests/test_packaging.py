import os

import pytest
from conftest import members

from rt.errors import RecipeError
from rt.packing import IgnoreRule, PackPlan, arcname

PROJECT = {
    "src/main.c": "c",
    "src/main.o": "o",
    "src/lib/util.c": "c",
    "src/lib/util.o": "o",
    "src/.hidden": "h",
    "res/song.mp3": "m",
    "res/img.png": "p",
    "README": "r",
    "install.sh": "sh",
}


@pytest.fixture
def project(tree):
    return tree(PROJECT, base="project")


def pack(rt, recipe, body, name="out.tar.gz"):
    result = rt(recipe(f"target_dir dist\nroot_dir project\n{body}\npack {name}\n"))
    assert result.code == 0, result.err
    return members(f"dist/{name}"), result


# --- add -----------------------------------------------------------------------

def test_add_file(rt, recipe, project):
    assert pack(rt, recipe, "add README")[0] == ["README"]


def test_add_directory_keeps_its_name(rt, recipe, project):
    names, _ = pack(rt, recipe, "add res")
    assert names == ["res/img.png", "res/song.mp3"]


def test_add_wildcard(rt, recipe, project):
    names, _ = pack(rt, recipe, "add src/*.c")
    assert names == ["main.c"]


def test_add_recursive_wildcard_keeps_subpaths(rt, recipe, project):
    names, _ = pack(rt, recipe, "add src/**/*.c")
    assert names == ["lib/util.c", "main.c"]


def test_add_wildcard_in_middle(rt, recipe, project):
    names, _ = pack(rt, recipe, "add */*.png")
    assert names == ["res/img.png"]


def test_add_in_directory(rt, recipe, project):
    names, _ = pack(rt, recipe, "add src in pkg/code\nadd README in docs/")
    assert names == ["docs/README", "pkg/code/src/.hidden", "pkg/code/src/lib/util.c",
                     "pkg/code/src/lib/util.o", "pkg/code/src/main.c", "pkg/code/src/main.o"]


def test_add_as_renames_file(rt, recipe, project):
    names, _ = pack(rt, recipe, "add README as docs/READ.txt")
    assert names == ["docs/READ.txt"]


def test_add_as_renames_directory(rt, recipe, project):
    # used to map every file of the directory to the same name
    names, _ = pack(rt, recipe, "add res as media")
    assert names == ["media/img.png", "media/song.mp3"]


def test_add_as_with_many_matches_fails(rt, recipe, project):
    result = rt(recipe("root_dir project\nadd res/* as x\n"))
    assert result.code == 1
    assert "'as' needs a single match" in result.err


def test_add_missing_is_a_warning(rt, recipe, project):
    names, result = pack(rt, recipe, "add nothere\nadd README")
    assert names == ["README"]
    assert "nothing matches 'nothere'" in result.err


def test_add_absolute_and_expanded_paths(rt, recipe, project, monkeypatch, tmp_path):
    monkeypatch.setenv("RT_PROJECT", str(tmp_path / "project"))
    monkeypatch.setenv("RT_DIR", "pkg")
    names, _ = pack(rt, recipe, "add $(RT_PROJECT)/README in $(RT_DIR)")
    assert names == ["pkg/README"]


def test_add_same_file_twice_is_packed_once(rt, recipe, project):
    names, _ = pack(rt, recipe, "add README\nadd README")
    assert names == ["README"]


def test_add_refuses_paths_outside_the_package(rt, recipe, project):
    result = rt(recipe("root_dir project\nadd README as ../evil\n"))
    assert result.code == 1
    assert "invalid path inside the package" in result.err


# --- ignore --------------------------------------------------------------------

def test_ignore_name_matches_anywhere(rt, recipe, project):
    names, _ = pack(rt, recipe, "add src\nignore *.o\nignore .hidden")
    assert names == ["src/lib/util.c", "src/main.c"]


def test_ignore_directory_name(rt, recipe, project):
    names, _ = pack(rt, recipe, "add src\nignore lib")
    assert names == ["src/.hidden", "src/main.c", "src/main.o"]


def test_ignore_relative_path(rt, recipe, project):
    names, _ = pack(rt, recipe, "add src\nignore ./src/lib")
    assert names == ["src/.hidden", "src/main.c", "src/main.o"]


def test_ignore_path_with_wildcard(rt, recipe, project):
    names, _ = pack(rt, recipe, "add src\nignore src/*.o")
    assert names == ["src/.hidden", "src/lib/util.c", "src/main.c"]


def test_ignore_from_relative_dir(rt, recipe, project):
    # `from` used to require an absolute path
    names, _ = pack(rt, recipe, "add src\nadd res\nignore *.c from src/lib\nignore *.mp3 from ./res")
    assert names == ["res/img.png", "src/.hidden", "src/lib/util.o", "src/main.c", "src/main.o"]


def test_ignore_absolute_path(rt, recipe, project, tmp_path):
    names, _ = pack(rt, recipe, f"add res\nignore {tmp_path}/project/res/song.mp3")
    assert names == ["res/img.png"]


def test_ignore_before_add_also_applies(rt, recipe, project):
    names, _ = pack(rt, recipe, "ignore *.o\nadd src/lib")
    assert names == ["lib/util.c"]


def test_ignore_outside_scope_does_not_match(tmp_path):
    rule = IgnoreRule("*.c", str(tmp_path / "a"))
    assert not rule.matches(str(tmp_path / "b" / "x.c"))
    assert rule.matches(str(tmp_path / "a" / "deep" / "x.c"))


# --- pack ----------------------------------------------------------------------

def test_pack_resets_queue_between_packages(rt, recipe, project):
    result = rt(recipe("""
        root_dir project
        target_dir dist
        add README
        ignore *.png
        pack one.tar.gz
        add res
        pack two.tar.gz
    """))
    assert result.code == 0
    assert members("project/dist/one.tar.gz") == ["README"]
    assert members("project/dist/two.tar.gz") == ["res/img.png", "res/song.mp3"]


def test_pack_without_target_dir_uses_start_dir(rt, recipe, project, tmp_path):
    result = rt(recipe("root_dir project\nadd README\npack p.rt\n"))
    assert result.code == 0
    assert "target_dir not set" in result.err
    assert members(tmp_path / "p.rt") == ["README"]


def test_target_dir_is_created_and_absolute(rt, recipe, project, tmp_path):
    # target_dir is resolved when declared, not when packing
    result = rt(recipe("target_dir out/new\nroot_dir project\nadd README\npack p.rt\n"))
    assert result.code == 0
    assert members(tmp_path / "out/new/p.rt") == ["README"]


def test_pack_progress_and_success(rt, recipe, project):
    _, result = pack(rt, recipe, "add README")
    assert "[1/1]" in result.out and "-> README" in result.out
    assert "Package created:" in result.out


def test_empty_package_warns(rt, recipe, project):
    names, result = pack(rt, recipe, "")
    assert names == []
    assert "is empty" in result.err


def test_pack_skips_itself(rt, recipe, project):
    result = rt(recipe("root_dir project\ntarget_dir .\nadd *\npack self.tar.gz\nadd *\npack self.tar.gz\n"))
    assert result.code == 0
    assert "self.tar.gz" not in members("project/self.tar.gz")


def test_pack_overwrites_existing(rt, recipe, project):
    pack(rt, recipe, "add README")
    names, _ = pack(rt, recipe, "add install.sh")
    assert names == ["install.sh"]


def test_pack_file_name_from_args(rt, recipe, project):
    result = rt(recipe("root_dir project\ntarget_dir dist\nadd README\npack args[1].rt\n"), "v2")
    assert result.code == 0
    assert members("project/dist/v2.rt") == ["README"]


# --- root_dir / target_dir --------------------------------------------------------

def test_root_dir_missing(rt, recipe):
    result = rt(recipe("root_dir nothere"))
    assert result.code == 1
    assert "root_dir: directory not found: nothere" in result.err


def test_root_dir_wildcard_after_expansion(rt, recipe, monkeypatch):
    monkeypatch.setenv("RT_W", "a*")
    result = rt(recipe("root_dir $(RT_W)"))
    assert result.code == 1
    assert "cannot contain wildcards" in result.err


def test_target_dir_cannot_be_a_file(rt, recipe, tmp_path):
    (tmp_path / "file").write_text("x")
    result = rt(recipe("target_dir file"))
    assert result.code == 1
    assert "target_dir: cannot create" in result.err


# --- unit ------------------------------------------------------------------------

@pytest.mark.parametrize("path, expected", [
    ("a/b", "a/b"), ("/a/./b/", "a/b"), ("a/../b", "b"),
])
def test_arcname(path, expected):
    assert arcname(path) == expected


@pytest.mark.parametrize("path", ["..", "../a", "a/../..", ".", ""])
def test_arcname_rejects(path):
    with pytest.raises(RecipeError):
        arcname(path)


def test_plan_files_exclude(tmp_path):
    (tmp_path / "a").write_text("a")
    plan = PackPlan()
    os.chdir(tmp_path)
    assert plan.add("a") == 1
    assert plan.files(exclude=(str(tmp_path / "a"),)) == []
