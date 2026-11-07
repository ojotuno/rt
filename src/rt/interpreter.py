"""Execute a parsed recipe."""

from __future__ import annotations

from typing import Callable, TypeVar

from . import commands, conditions
from .context import Context
from .errors import RtError
from .parser import IfBlock, Node, Statement

T = TypeVar("T")


def _located(stmt: Statement, fn: Callable[[Context, Statement], T], ctx: Context) -> T:
    try:
        return fn(ctx, stmt)
    except RtError as exc:
        raise exc.locate(stmt.line, stmt.source)


def execute(nodes: list[Node], ctx: Context) -> None:
    for node in nodes:
        if isinstance(node, IfBlock):
            if _located(node.condition, conditions.evaluate, ctx):
                execute(node.body, ctx)
        else:
            _located(node, commands.get(node.keyword).run, ctx)
