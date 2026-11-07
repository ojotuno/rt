"""Package creation, extraction and inspection (.rt files are .tar.gz archives)."""

from __future__ import annotations

import fnmatch
import glob
import os
import posixpath
import re
import tarfile
import zlib
from typing import Callable, Iterator

from . import log
from .errors import RecipeError, RtError

INSTALL_RECIPE = "install"
# What a damaged/truncated archive can raise while reading it.
ARCHIVE_ERRORS = (tarfile.TarError, OSError, EOFError, zlib.error)
WILDCARD_RE = re.compile(r"[*?\[]")


def has_wildcards(path: str) -> bool:
    return bool(WILDCARD_RE.search(path))


def arcname(path: str) -> str:
    """Normalize a path inside the package; refuse paths escaping it."""
    arc = posixpath.normpath(path.replace(os.sep, "/")).lstrip("/")
    if arc in ("", ".") or arc == ".." or arc.startswith("../"):
        raise RecipeError(f"invalid path inside the package: {path!r}")
    return arc


def _files_under(path: str) -> Iterator[str]:
    if os.path.isdir(path) and not os.path.islink(path):
        for current, dirs, files in os.walk(path):
            dirs.sort()
            for name in sorted(files):
                yield os.path.join(current, name)
    else:
        yield path


def _split_pattern(abs_pattern: str) -> tuple[list[str], str]:
    """Return (matches, root). Paths inside the package are relative to root."""
    if not has_wildcards(abs_pattern):
        exists = os.path.lexists(abs_pattern)
        return ([abs_pattern] if exists else []), os.path.dirname(abs_pattern)
    parts = abs_pattern.split(os.sep)
    first = next(i for i, part in enumerate(parts) if has_wildcards(part))
    root = os.sep.join(parts[:first]) or os.sep
    return sorted(glob.glob(abs_pattern, recursive=True)), root


class IgnoreRule:
    """`pattern` without '/' matches any path component below `base` (like .gitignore);
    with '/' it is a path (relative to `base` or absolute) and matches it and everything below."""

    def __init__(self, pattern: str, base: str) -> None:
        pattern = pattern.rstrip("/") or "/"
        self.pattern = pattern
        if "/" not in pattern:
            self._scope = base
            self._component = re.compile(fnmatch.translate(pattern)).match
            self._path = None
        else:
            full = os.path.normpath(os.path.join(base, pattern))
            parts = full.split(os.sep)
            fixed = next((i for i, part in enumerate(parts) if has_wildcards(part)), len(parts))
            # Only paths below the wildcard-free prefix can match.
            self._scope = os.sep.join(parts[:fixed]) or os.sep
            self._component = None
            self._path = re.compile(fnmatch.translate(full)).match
        self._prefix = self._scope.rstrip(os.sep) + os.sep

    def matches(self, src: str) -> bool:
        if src != self._scope and not src.startswith(self._prefix):
            return False
        if self._component:
            return any(self._component(part) for part in src[len(self._prefix):].split(os.sep))
        # src itself or one of its parents inside the scope
        candidate = src
        while len(candidate) >= len(self._scope):
            if self._path(candidate):
                return True
            parent = os.path.dirname(candidate)
            if parent == candidate:
                break
            candidate = parent
        return False


class PackPlan:
    """Files queued by add/ignore for the next `pack`."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._entries: dict[str, str] = {}  # arcname -> source path
        self._ignores: list[IgnoreRule] = []

    def add(self, pattern: str, mode: str | None = None, dest: str | None = None) -> int:
        """mode None: keep the matched name. 'as': rename the (single) match to dest.
        'in': put the matches inside directory dest. Returns the number of files queued."""
        abs_pattern = os.path.abspath(pattern)
        matches, root = _split_pattern(abs_pattern)
        if not matches:
            log.warn(f"nothing matches {pattern!r}, skipped")
            return 0
        if mode == "as" and len(matches) > 1:
            raise RecipeError(f"'as' needs a single match but {pattern!r} matches {len(matches)}; use 'in'")

        count = 0
        for match in matches:
            for src in _files_under(match):
                if mode == "as":
                    arc = dest if src == match else posixpath.join(dest, os.path.relpath(src, match))
                else:
                    arc = os.path.relpath(src, root)
                    if mode == "in":
                        arc = posixpath.join(dest, arc)
                self._entries[arcname(arc)] = src
                count += 1
        return count

    def ignore(self, pattern: str, base: str) -> None:
        self._ignores.append(IgnoreRule(pattern, base))

    def files(self, exclude: tuple[str, ...] = ()) -> list[tuple[str, str]]:
        """(source, arcname) pairs that survive the ignore rules."""
        excluded = {os.path.abspath(p) for p in exclude}
        return [
            (src, arc)
            for arc, src in self._entries.items()
            if src not in excluded and not any(rule.matches(src) for rule in self._ignores)
        ]


def write_package(path: str, files: list[tuple[str, str]],
                  on_file: Callable[[int, int, str, str], None] | None = None) -> None:
    """Write files atomically into a .tar.gz at path."""
    tmp = path + ".part"
    try:
        with tarfile.open(tmp, "w:gz") as tar:
            for index, (src, arc) in enumerate(files, start=1):
                if on_file:
                    on_file(index, len(files), src, arc)
                tar.add(src, arc, recursive=False)
        os.replace(tmp, path)
    except OSError as exc:
        raise RecipeError(f"cannot write package {path}: {exc}") from exc
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def is_package(path: str) -> bool:
    try:
        return os.path.isfile(path) and tarfile.is_tarfile(path)
    except ARCHIVE_ERRORS:
        return False


def extract_package(path: str, dest: str) -> list[str]:
    """Extract safely (no absolute paths, no '..', no links escaping dest).
    Returns the member names."""
    try:
        with tarfile.open(path, "r:*") as tar:
            names = tar.getnames()
            if hasattr(tarfile, "data_filter"):
                tar.extractall(dest, filter="data")
            else:  # Python without extraction filters
                _check_members(tar, dest)
                tar.extractall(dest)
        return names
    except ARCHIVE_ERRORS as exc:
        raise RtError(f"cannot extract {path}: {exc}") from exc


def _check_members(tar: tarfile.TarFile, dest: str) -> None:
    root = os.path.realpath(dest)

    def inside(path: str) -> bool:
        return os.path.commonpath([root, os.path.realpath(path)]) == root

    for member in tar.getmembers():
        target = os.path.join(root, member.name)
        if os.path.isabs(member.name) or not inside(target):
            raise tarfile.TarError(f"member escapes destination: {member.name}")
        if member.issym() and not inside(os.path.join(os.path.dirname(target), member.linkname)):
            raise tarfile.TarError(f"link escapes destination: {member.name}")
        if member.islnk() and not inside(os.path.join(root, member.linkname)):
            raise tarfile.TarError(f"link escapes destination: {member.name}")


def find_install_recipe(names: list[str]) -> str | None:
    """The shallowest member called `install`."""
    candidates = [n for n in names if posixpath.basename(n.rstrip("/")) == INSTALL_RECIPE]
    if not candidates:
        return None
    return min(candidates, key=lambda n: (n.strip("/").count("/"), n))


def show_package(path: str) -> None:
    """Print the content of a package as a tree."""
    if not is_package(path):
        raise RtError(f"not a valid rt package: {path}")
    try:
        with tarfile.open(path, "r:*") as tar:
            members = tar.getmembers()
    except ARCHIVE_ERRORS as exc:
        raise RtError(f"cannot read {path}: {exc}") from exc

    tree: dict = {}
    dirs: set[int] = set()  # ids of nodes that are directories
    for member in members:
        node = tree
        for part in [p for p in member.name.split("/") if p and p != "."]:
            node = node.setdefault(part, {})
        if member.isdir():
            dirs.add(id(node))

    rule = "─" * 50
    log.plain(log.paint("Contents of: ", "cyan") + log.paint(path, "yellow"))
    log.plain(log.paint(rule, "grey"))
    _print_tree(tree, "", dirs)
    log.plain(log.paint(rule, "grey"))
    files = sum(1 for m in members if not m.isdir())
    folders = sum(1 for m in members if m.isdir())
    log.plain(f"{files} files, {folders} directories")


def _print_tree(node: dict, prefix: str, dirs: set[int]) -> None:
    names = sorted(node)
    for i, name in enumerate(names):
        last = i == len(names) - 1
        connector = "└─ " if last else "├─ "
        child = node[name]
        if child or id(child) in dirs:
            log.plain(prefix + connector + log.paint(name + "/", "blue"))
            _print_tree(child, prefix + ("   " if last else "│  "), dirs)
        else:
            log.plain(prefix + connector + name)
