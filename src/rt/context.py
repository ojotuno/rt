"""State of a running recipe. One Context per recipe (nested `rt` calls get their own)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from . import expand
from .lexer import Token
from .packing import PackPlan


@dataclass
class Context:
    recipe: str
    args: list[str]  # args[0] is the recipe/package, args[1..] the user arguments
    origin_dir: str  # working directory when the recipe started
    call_rt: Callable[[list[str]], int]  # runs a nested `rt ...` call, returns its exit code
    target_dir: str | None = None
    plan: PackPlan = field(default_factory=PackPlan)

    def expand(self, token: Token) -> str:
        return expand.expand_token(token, self.args)

    def expand_all(self, tokens: list[Token]) -> list[str]:
        return [self.expand(t) for t in tokens]

    def expand_shell(self, text: str) -> str:
        return expand.expand_shell(text, self.args)
