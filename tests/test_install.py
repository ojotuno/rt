import os
import tarfile

import pytest
from conftest import make_package

from rt.packing import find_install_recipe, is_package

INSTALL = """
print "installing from " args[0] " argc=" argc
> pwd
> cat data.txt
"""


@pytest.fixture
def package(tmp_path):
    return make_package(tmp_path / "app.rt", {"install": INSTALL, "data.txt": "payload\n"})


def test_install_into_current_dir(rt, package, tmp_path):
    result = rt("app.rt")
    assert result.code == 0, result.err
    assert result.lines == ["installing from app.rt argc=1", str(tmp_path), "payload"]
    assert (tmp_path / "data.txt").read_text() == "payload\n"
    assert "Processing installation recipe" in result.out


def test_install_into_dest_with_args(rt, package, tmp_path):
    make_package(tmp_path / "app.rt", {"install": 'print args[1] "," args[2]\n> pwd\n'})
    result = rt("app.rt", "dest/dir", "a", "b")
    assert result.code == 0, result.err
    assert result.lines == ["a,b", str(tmp_path / "dest/dir")]
    assert os.getcwd() == str(tmp_path)


def test_install_recipe_in_subdir_runs_from_there(rt, tmp_path):
    make_package(tmp_path / "app.tar.gz", {"app-1.0/install": "> pwd", "app-1.0/x": ""})
    result = rt("app.tar.gz", "out")
    assert result.lines == [str(tmp_path / "out/app-1.0")]


def test_package_detected_by_content_not_extension(rt, tmp_path):
    make_package(tmp_path / "download", {"install": 'print "ok"'})
    assert rt("download", "out").lines == ["ok"]


def test_plain_tar_is_accepted(rt, tmp_path):
    make_package(tmp_path / "app.tar", {"install": 'print "ok"'}, mode="w")
    assert rt("app.tar", "out").lines == ["ok"]


def test_missing_install_recipe_warns(rt, tmp_path):
    make_package(tmp_path / "app.rt", {"data.txt": "x"})
    result = rt("app.rt", "out")
    assert result.code == 0
    assert "installation recipe 'install' not found" in result.err
    assert (tmp_path / "out/data.txt").exists()


def test_failing_install_recipe(rt, tmp_path):
    make_package(tmp_path / "app.rt", {"install": "> exit 4"})
    result = rt("app.rt", "out")
    assert result.code == 1
    assert "exit code 4" in result.err


def test_path_traversal_is_blocked(rt, tmp_path):
    make_package(tmp_path / "evil.rt", {"../escaped": "x", "install": 'print "no"'})
    result = rt("evil.rt", "out")
    assert result.code == 1
    assert "cannot extract" in result.err
    assert not (tmp_path / "escaped").exists()


def test_corrupt_package(rt, tmp_path):
    data = (make_package(tmp_path / "ok.rt", {"install": "print x"})).read_bytes()
    (tmp_path / "bad.rt").write_bytes(data[:40])
    result = rt("bad.rt", "out")
    assert result.code == 1


def test_pack_then_install_roundtrip(rt, recipe, tree, tmp_path):
    tree({"bin/tool.sh": "#!/bin/sh\necho tool", "install": "> sh bin/tool.sh"}, base="app")
    assert rt(recipe("root_dir app\nadd bin\nadd install\ntarget_dir ..\npack app.rt\n")).code == 0
    result = rt("app.rt", "installed")
    assert result.code == 0
    assert result.lines == ["tool"]


def test_find_install_recipe_prefers_shallowest():
    assert find_install_recipe(["a/b/install", "a/install", "x"]) == "a/install"
    assert find_install_recipe(["installer", "x/notinstall"]) is None


def test_is_package(tmp_path):
    (tmp_path / "text").write_text("print hi\n")
    (tmp_path / "empty").write_text("")
    make_package(tmp_path / "p.rt", {"a": "b"})
    assert is_package(str(tmp_path / "p.rt"))
    assert not is_package(str(tmp_path / "text"))
    assert not is_package(str(tmp_path / "empty"))
    assert not is_package(str(tmp_path / "missing"))


# --- rt -show -------------------------------------------------------------------

def test_show_package_tree(rt, tmp_path):
    path = tmp_path / "p.rt"
    with tarfile.open(path, "w:gz") as tar:
        for name in ("src", "src/a.py", "src/sub", "README"):
            info = tarfile.TarInfo(name)
            if "." not in name and name != "README":
                info.type = tarfile.DIRTYPE
            tar.addfile(info)
    result = rt("-show", "p.rt")
    assert result.code == 0
    assert "├─ README" in result.out
    assert "└─ src/" in result.out
    assert "   ├─ a.py" in result.out
    assert "   └─ sub/" in result.out  # empty dir shown as directory
    assert "2 files, 2 directories" in result.out
    assert "Done!" not in result.out


def test_show_invalid(rt, tmp_path):
    (tmp_path / "r").write_text("print x")
    assert rt("-show", "r").code == 1
    assert rt("-show").code == 2
