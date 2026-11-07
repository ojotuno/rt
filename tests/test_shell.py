import os
import stat


def test_shell_command_output_and_order(rt, recipe):
    result = rt(recipe("""
        print "one"
        > echo "two   spaced"
        >echo three # comment
        print "four"
    """))
    assert result.code == 0
    assert result.lines == ["one", "two   spaced", "three", "four"]


def test_shell_expands_variables(rt, recipe, monkeypatch):
    monkeypatch.setenv("RT_X", "xx")
    result = rt(recipe("> echo $(RT_X) args[1] argc $HOME"), "a1")
    assert result.lines == [f"xx a1 2 {os.environ['HOME']}"]


def test_shell_runs_in_root_dir(rt, recipe, tmp_path):
    (tmp_path / "sub").mkdir()
    result = rt(recipe("root_dir sub\n> pwd\n"))
    assert result.lines == [str(tmp_path / "sub")]


def test_failing_command_stops_recipe(rt, recipe):
    result = rt(recipe("> false\nprint never\n"))
    assert result.code == 1
    assert result.lines == []
    assert "recipe:1: command failed with exit code 1: false" in result.err


def test_failure_can_be_allowed_with_or_true(rt, recipe):
    result = rt(recipe("> false || true\nprint after\n"))
    assert result.code == 0
    assert result.lines == ["after"]


def _fake_tool(tmp_path, monkeypatch, name):
    bindir = tmp_path / "fakebin"
    bindir.mkdir(exist_ok=True)
    tool = bindir / name
    tool.write_text(f'#!/bin/sh\necho "{name} called with: $*"\n')
    tool.chmod(tool.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ['PATH']}")


def test_git_and_svn(rt, recipe, tmp_path, monkeypatch):
    _fake_tool(tmp_path, monkeypatch, "git")
    _fake_tool(tmp_path, monkeypatch, "svn")
    # git/svn used to crash with TypeError
    result = rt(recipe("""
        git commit -m "msg with spaces" args[1]
        svn update
    """), "extra")
    assert result.code == 0
    assert result.lines == ["git called with: commit -m msg with spaces extra", "svn called with: update"]
