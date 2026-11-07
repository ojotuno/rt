"""Run the example recipes in tests/recipes. Lines starting with FAIL must never print."""

import shutil
import subprocess

import pytest
from conftest import RECIPES, members

CASES = {
    "if-eq": ([], 2),
    "if-neq": ([], 2),
    "if-numeric": ([], 10),
    "if-args": (["foo", "bar", "42"], 6),
    "if-env": ([], 3),
    "if-nested": ([], 4),
}


@pytest.mark.parametrize("name", CASES)
def test_if_recipes(rt, name, monkeypatch):
    monkeypatch.setenv("USER", "tester")
    args, oks = CASES[name]
    result = rt(RECIPES / name, *args)
    assert result.code == 0, result.err
    assert not [l for l in result.lines if "FAIL" in l]
    assert sum(l.startswith("OK") for l in result.lines) == oks


def test_run_if_tests_calls_every_recipe(rt, tmp_path, monkeypatch):
    monkeypatch.setenv("USER", "tester")
    shutil.copytree(RECIPES, tmp_path / "tests" / "recipes")
    result = rt("tests/recipes/run_if_tests")
    assert result.code == 0, result.err
    assert sum(l.startswith("OK") for l in result.lines) == sum(n for _, n in CASES.values())


def test_hello_world(rt):
    assert rt(RECIPES / "hello-world").lines == ["hello world"]


def test_args_and_argc(rt):
    assert rt(RECIPES / "args", "a", "b", "c").lines == [str(RECIPES / "args"), "a", "b", "c"]
    assert rt(RECIPES / "argc", "x").lines == ["RT reciper is being calling with 2 arguments",
                                               str(RECIPES / "argc"), "x"]


def test_exit_recipes(rt, tmp_path):
    assert rt(RECIPES / "exit").lines == ["Print this string and then exit"]
    assert rt(RECIPES / "exit2").code == 0
    assert not (tmp_path / "rt.rt").exists()
    assert rt(RECIPES / "exit3").code == 1  # exit with arguments is a syntax error


@pytest.fixture
def release(tmp_path):
    """Copy the repo, run build-new-release-version there. Returns (repo, script output)."""
    repo = tmp_path / "repo"
    shutil.copytree(RECIPES.parent.parent, repo,
                    ignore=shutil.ignore_patterns(".git", "releases", "__pycache__", ".pytest_cache"))
    proc = subprocess.run([str(repo / "build-new-release-version")], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return repo, proc.stdout


def test_build_new_release_version(release):
    repo, out = release
    names = members(repo / "releases" / "rt.rt")
    assert {"install", "install.sh", "bin/rt", "src/rt/cli.py", "src/rt/buildnum.py",
            "src/rt/commands/general.py"} <= set(names)
    assert not [n for n in names if "__pycache__" in n]
    assert set(members(repo / "releases" / "rt.tar.gz")) == set(names) - {"install"}
    assert not list((repo / "releases").glob("*.part"))
    # the script reports every step
    for text in ("==> Generating build number", "+ sh ", "==> Creating", "+ tar -czvf", "Release ready"):
        assert text in out


def test_release_package_installs_working_rt(rt, release, tmp_path, monkeypatch):
    """Install rt.rt with PREFIX in a temp dir and run the installed rt."""
    repo, _ = release
    prefix = tmp_path / "prefix"
    monkeypatch.setenv("PREFIX", str(prefix))
    result = rt(repo / "releases" / "rt.rt", "unpacked")
    assert result.code == 0, result.err

    launcher = prefix / "bin" / "rt"
    assert str(prefix / "lib" / "rt") in launcher.read_text()  # @LIBDIR@ replaced
    (tmp_path / "hello").write_text('print "installed " argc\n')
    proc = subprocess.run([str(launcher), "hello", "x"], capture_output=True, text=True, cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "installed 2" in proc.stdout
    build = (repo / "src" / "rt" / "buildnum.py").read_text().split('"')[1]
    assert f"Build: {build}" in subprocess.run([str(launcher)], capture_output=True, text=True).stdout
