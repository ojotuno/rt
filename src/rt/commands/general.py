"""print, rt, exit."""

from __future__ import annotations

from .. import log
from ..errors import RecipeError, RecipeExit
from . import command


@command("print", usage='print "TEXT" [VALUE ...]',
         summary="Print the values concatenated (no separator added: put spaces inside quotes).")
def print_(ctx, stmt):
    log.plain("".join(ctx.expand_all(stmt.args)))


@command("rt", usage="rt [-url] RECIPE|PACKAGE [ARGS...]", min_args=1,
         summary="Run another recipe or package. Its failure stops this recipe.")
def rt(ctx, stmt):
    argv = ctx.expand_all(stmt.args)
    log.info("Calling: rt " + " ".join(argv))
    code = ctx.call_rt(argv)
    if code != 0:
        raise RecipeError(f"rt call failed with exit code {code}")


@command("exit", usage="exit", nargs=0, summary="Stop the current recipe successfully.")
def exit_(ctx, stmt):
    raise RecipeExit()
