"""Run recipes, install packages and handle downloads."""

from __future__ import annotations

import os
import posixpath

from . import interpreter, log, packing
from .context import Context
from .errors import RecipeExit, RtError
from .parser import parse

MAX_DEPTH = 32  # nested `rt` calls


def _call_rt(depth: int):
    def call(argv: list[str]) -> int:
        from .cli import dispatch  # cli imports runner

        return dispatch(argv, depth + 1)

    return call


def run_recipe(path: str, args: list[str], depth: int = 0, title: str = "Processing recipe") -> None:
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except UnicodeDecodeError as exc:
        raise RtError(f"{path} is not a recipe (binary file?)") from exc
    except OSError as exc:
        raise RtError(f"cannot read {path}: {exc.strerror}") from exc

    nodes = parse(text, source=path)
    log.info(f"{title}: {path}")
    cwd = os.getcwd()
    ctx = Context(recipe=path, args=args, origin_dir=cwd, call_rt=_call_rt(depth))
    try:
        interpreter.execute(nodes, ctx)
    except RecipeExit:
        log.info("Exit")
    finally:
        os.chdir(cwd)  # root_dir must not leak to the caller


def install_package(archive: str, dest: str, args: list[str], depth: int = 0) -> None:
    dest = os.path.abspath(dest)
    os.makedirs(dest, exist_ok=True)
    log.info(f"Extracting {archive} -> {dest}")
    names = packing.extract_package(archive, dest)
    recipe = packing.find_install_recipe(names)
    if recipe is None:
        log.warn(f"installation recipe '{packing.INSTALL_RECIPE}' not found in {archive}")
        return
    recipe_path = os.path.join(dest, *posixpath.normpath(recipe).split("/"))
    cwd = os.getcwd()
    os.chdir(os.path.dirname(recipe_path))
    try:
        run_recipe(recipe_path, args, depth, title="Processing installation recipe")
    finally:
        os.chdir(cwd)


def run_path(path: str, extra: list[str], depth: int = 0) -> None:
    """`rt RECIPE [ARGS...]` or `rt PACKAGE [DEST] [ARGS...]`."""
    if not os.path.isfile(path):
        raise RtError(f"file not found: {path}")
    if packing.is_package(path):
        dest = extra[0] if extra else os.getcwd()
        install_package(path, dest, [path, *extra[1:]], depth)
    else:
        run_recipe(path, [path, *extra], depth)


def run_url(url: str, extra: list[str], depth: int = 0) -> None:
    """Download a recipe or package to a temp dir and run it.
    Packages are installed from the temp dir; recipes run in the current directory."""
    # Imported here: urllib/tempfile are slow to import and only needed for downloads.
    import shutil
    import tempfile

    from . import download

    tmp = tempfile.mkdtemp(prefix="rt-")
    try:
        path = download.download(url, tmp)
        if packing.is_package(path):
            install_package(path, tmp, [path, *extra], depth)
        else:
            run_recipe(path, [path, *extra], depth)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
