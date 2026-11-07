import io
import tarfile
import textwrap
from dataclasses import dataclass
from pathlib import Path

import pytest

from rt.cli import dispatch

REPO = Path(__file__).resolve().parent.parent
RECIPES = REPO / "tests" / "recipes"


@dataclass
class Result:
    code: int
    out: str
    err: str

    @property
    def lines(self):
        """stdout lines without rt's own [rt] messages."""
        return [l for l in self.out.splitlines() if not l.startswith("[rt] ")]


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NO_COLOR", "1")


@pytest.fixture
def rt(capfd):
    """rt("recipe", "arg") -> Result. Runs rt in-process."""

    def run(*argv):
        capfd.readouterr()
        code = dispatch([str(a) for a in argv])
        captured = capfd.readouterr()
        return Result(code, captured.out, captured.err)

    return run


@pytest.fixture
def recipe(tmp_path):
    """recipe("print hi") -> path of a recipe file with that (dedented) content."""

    def write(text, name="recipe"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text).lstrip("\n"))
        return path

    return write


@pytest.fixture
def tree(tmp_path):
    """tree({"a/b.txt": "x", ...}, base="src") -> base path with those files."""

    def make(files, base="."):
        root = tmp_path / base
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        return root

    return make


def members(package):
    with tarfile.open(package) as tar:
        return sorted(m.name for m in tar.getmembers())


def make_package(path, files, mode="w:gz"):
    """Build a tar package from {arcname: content}."""
    with tarfile.open(path, mode) as tar:
        for name, content in files.items():
            data = content.encode()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o755 if name.endswith(".sh") else 0o644
            tar.addfile(info, io.BytesIO(data))
    return path

