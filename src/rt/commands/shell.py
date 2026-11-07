"""Shell commands: `> CMD`, git, svn."""

from __future__ import annotations

import subprocess
import sys

from ..errors import RecipeError
from . import command


def run_shell(cmd: str) -> None:
    sys.stdout.flush()
    sys.stderr.flush()
    code = subprocess.run(cmd, shell=True).returncode
    if code != 0:
        raise RecipeError(f"command failed with exit code {code}: {cmd}")


@command(">", usage="> COMMAND", min_args=1,
         summary="Run a shell command. A non-zero exit code stops the recipe (use `|| true` to allow it).")
def shell(ctx, stmt):
    run_shell(ctx.expand_shell(stmt.rest))


def _tool(name: str) -> None:
    @command(name, usage=f"{name} ARGS...", min_args=1, summary=f"Run `{name} ARGS...`.")
    def run(ctx, stmt):
        run_shell(f"{name} {ctx.expand_shell(stmt.rest)}")


for _name in ("git", "svn"):
    _tool(_name)
