import functools
import http.server
import os
import subprocess
import sys
import threading

import pytest
from conftest import REPO, make_package

import rt as rt_pkg
from rt import commands
from rt.download import filename_for


def test_help(rt):
    for argv in ([], ["-h"], ["--help"]):
        result = rt(*argv)
        assert result.code == 0
        assert "Usage:" in result.out


def test_help_lists_every_command(rt):
    out = rt("--help").out
    for cmd in commands.all_commands():
        assert cmd.usage in out
    assert "if A OP B ... end" in out


def test_unknown_option(rt):
    result = rt("-nope")
    assert result.code == 2
    assert "unknown option: -nope" in result.err


def test_missing_file(rt):
    result = rt("nothere")
    assert result.code == 1
    assert "file not found: nothere" in result.err


def test_binary_file_is_not_a_recipe(rt, tmp_path):
    (tmp_path / "bin").write_bytes(b"\xff\xfe\x00\x81")
    result = rt("bin")
    assert result.code == 1
    assert "is not a recipe" in result.err


def test_usage_errors(rt):
    assert rt("-url").code == 2
    assert rt("-update", "x").code == 2


# --- downloads -------------------------------------------------------------------

@pytest.fixture
def server(tmp_path):
    """Serve tmp_path/www over HTTP. Yields the base URL."""
    www = tmp_path / "www"
    www.mkdir()

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def end_headers(self):
            if self.path.startswith("/download"):  # owncloud-like link without file name
                self.send_header("Content-Disposition", 'attachment; filename="pkg.rt"')
            super().end_headers()

        def translate_path(self, path):
            if path.startswith("/download"):
                path = "/pkg.rt"
            return super().translate_path(path)

    handler = functools.partial(Handler, directory=str(www))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}", www
    httpd.shutdown()


def test_url_recipe_runs_in_current_dir(rt, server, tmp_path):
    base, www = server
    (www / "recipe").write_text('print "remote " args[1]\n> pwd\n')
    result = rt("-url", f"{base}/recipe", "x")
    assert result.code == 0, result.err
    assert result.lines == ["remote x", str(tmp_path)]


def test_url_package_is_installed_and_cleaned(rt, server, tmp_path):
    base, www = server
    make_package(www / "pkg.rt", {"install": "> pwd"})
    result = rt("-url", f"{base}/download?id=1")
    assert result.code == 0, result.err
    workdir = result.lines[0]
    assert os.path.basename(workdir).startswith("rt-")
    assert not os.path.exists(workdir)  # temp dir removed


def test_url_not_found(rt, server):
    base, _ = server
    result = rt("-url", f"{base}/missing")
    assert result.code == 1
    assert "download failed" in result.err


def test_rt_url_from_recipe(rt, recipe, server):
    base, www = server
    (www / "child").write_text('print "child"')
    result = rt(recipe(f"rt -url {base}/child\nprint parent\n"))
    assert result.lines == ["child", "parent"]


def test_update_uses_update_url(rt, server, monkeypatch):
    base, www = server
    make_package(www / "pkg.rt", {"install": 'print "updated"'})
    monkeypatch.setattr(rt_pkg, "UPDATE_URL", f"{base}/pkg.rt")
    monkeypatch.setattr("rt.cli.UPDATE_URL", f"{base}/pkg.rt")
    assert rt("-update").lines == ["updated"]


@pytest.mark.parametrize("url, header, expected", [
    ("http://h/a/b.rt", None, "b.rt"),
    ("http://h/a/b.rt?x=1", None, "b.rt"),
    ("http://h/download", "pkg.rt", "pkg.rt"),
    ("http://h/", None, "download"),
    ("http://h/x", "../../etc/passwd", "passwd"),
])
def test_filename_for(url, header, expected):
    assert filename_for(url, header) == expected


# --- launcher ---------------------------------------------------------------------

def test_launcher_from_source_checkout(recipe, tmp_path):
    path = recipe('print "args: " argc " " args[1]')
    proc = subprocess.run([sys.executable, str(REPO / "bin" / "rt"), str(path), "hi"],
                          capture_output=True, text=True, cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "args: 2 hi" in proc.stdout


def test_launcher_exit_code(recipe, tmp_path):
    path = recipe("> exit 1")
    proc = subprocess.run([sys.executable, str(REPO / "bin" / "rt"), str(path)],
                          capture_output=True, text=True, cwd=tmp_path)
    assert proc.returncode == 1


def test_python_m_rt(tmp_path):
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    proc = subprocess.run([sys.executable, "-m", "rt", "--help"], capture_output=True, text=True, env=env)
    assert proc.returncode == 0
    assert "Usage:" in proc.stdout
