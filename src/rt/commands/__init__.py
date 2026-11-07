"""Command registry.

Adding a keyword is just a decorated function in any module of this package:

    @command("hello", usage="hello NAME", summary="Greets NAME.", nargs=1)
    def hello(ctx, stmt):
        log.plain("Hello " + ctx.expand(stmt.args[0]))

`nargs` (int or tuple of ints) and `min_args` are checked when the recipe is parsed.
`validate(stmt)` can add extra parse-time checks (raise RecipeSyntaxError).
`run(ctx, stmt)` raises RecipeError on failure. The command shows up in `rt --help`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional

from ..errors import RecipeSyntaxError

if TYPE_CHECKING:
    from ..context import Context
    from ..parser import Statement

Runner = Callable[["Context", "Statement"], None]
Validator = Callable[["Statement"], None]


@dataclass(frozen=True)
class Command:
    name: str
    usage: str
    summary: str
    run: Runner
    nargs: int | tuple[int, ...] | None = None
    min_args: int = 0
    validate: Optional[Validator] = None

    def check(self, stmt: Statement) -> None:
        count = len(stmt.args)
        allowed = (self.nargs,) if isinstance(self.nargs, int) else self.nargs
        if count < self.min_args or (allowed is not None and count not in allowed):
            raise RecipeSyntaxError(f"usage: {self.usage}")
        if self.validate:
            self.validate(stmt)


_REGISTRY: dict[str, Command] = {}


def command(name: str, *, usage: str, summary: str, nargs=None, min_args: int = 0,
            validate: Optional[Validator] = None) -> Callable[[Runner], Runner]:
    def register(fn: Runner) -> Runner:
        if name in _REGISTRY:
            raise ValueError(f"command already registered: {name}")
        _REGISTRY[name] = Command(name, usage, summary, fn, nargs, min_args, validate)
        return fn

    return register


def get(name: str) -> Command | None:
    return _REGISTRY.get(name)


def all_commands() -> list[Command]:
    return list(_REGISTRY.values())


# Import the modules that register commands (order = order in --help).
from . import packaging, shell, general  # noqa: E402,F401
