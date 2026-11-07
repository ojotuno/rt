"""root_dir, target_dir, add, ignore, pack."""

from __future__ import annotations

import os

from .. import log
from ..errors import RecipeError, RecipeSyntaxError
from ..packing import has_wildcards, write_package
from . import command


def _no_wildcards(stmt) -> None:
    if has_wildcards(stmt.args[0].value):
        raise RecipeSyntaxError(f"{stmt.keyword} cannot contain wildcards")


def _expand_dir(ctx, stmt) -> str:
    path = ctx.expand(stmt.args[0])
    if has_wildcards(path):
        raise RecipeError(f"{stmt.keyword} cannot contain wildcards: {path}")
    return path


@command("root_dir", usage="root_dir PATH", nargs=1, validate=_no_wildcards,
         summary="Change the working directory. Relative paths and commands run from here.")
def root_dir(ctx, stmt):
    path = _expand_dir(ctx, stmt)
    if not os.path.isdir(path):
        raise RecipeError(f"root_dir: directory not found: {path}")
    os.chdir(path)
    log.info(f"root_dir -> {os.getcwd()}")


@command("target_dir", usage="target_dir PATH", nargs=1, validate=_no_wildcards,
         summary="Directory where `pack` writes packages (created if missing).")
def target_dir(ctx, stmt):
    path = os.path.abspath(_expand_dir(ctx, stmt))
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as exc:
        raise RecipeError(f"target_dir: cannot create {path}: {exc}") from exc
    ctx.target_dir = path
    log.info(f"target_dir -> {path}")


def _validate_add(stmt) -> None:
    if len(stmt.args) == 3 and stmt.args[1].value not in ("as", "in"):
        raise RecipeSyntaxError("usage: add PATTERN [as NAME | in DIR]")


@command("add", usage="add PATTERN [as NAME | in DIR]", nargs=(1, 3), validate=_validate_add,
         summary="Queue files for the next pack. Supports * ? [] and ** wildcards.")
def add(ctx, stmt):
    pattern = ctx.expand(stmt.args[0])
    if len(stmt.args) == 3:
        ctx.plan.add(pattern, stmt.args[1].value, ctx.expand(stmt.args[2]))
    else:
        ctx.plan.add(pattern)


def _validate_ignore(stmt) -> None:
    if len(stmt.args) == 3 and stmt.args[1].value != "from":
        raise RecipeSyntaxError("usage: ignore PATTERN [from DIR]")


@command("ignore", usage="ignore PATTERN [from DIR]", nargs=(1, 3), validate=_validate_ignore,
         summary="Exclude files from the next pack. A name without '/' matches anywhere.")
def ignore(ctx, stmt):
    pattern = ctx.expand(stmt.args[0])
    base = os.path.abspath(ctx.expand(stmt.args[2])) if len(stmt.args) == 3 else os.getcwd()
    ctx.plan.ignore(pattern, base)


@command("pack", usage="pack FILENAME", nargs=1,
         summary="Write the queued files to target_dir/FILENAME (.tar.gz) and clear the queue.")
def pack(ctx, stmt):
    if ctx.target_dir is None:
        log.warn(f"target_dir not set, using {ctx.origin_dir}")
        ctx.target_dir = ctx.origin_dir
    path = os.path.join(ctx.target_dir, ctx.expand(stmt.args[0]))
    files = ctx.plan.files(exclude=(path,))
    if not files:
        log.warn(f"package {path} is empty")

    log.info(f"Packing {path}")
    write_package(path, files, lambda i, n, src, arc: log.plain(f"[{i}/{n}] {src} -> {arc}"))
    ctx.plan.reset()
    log.success(f"Package created: {path}")
