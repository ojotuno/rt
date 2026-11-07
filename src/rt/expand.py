"""Variable expansion: $(ENV), args[N] and argc."""

from __future__ import annotations

import os
import re

from .errors import RecipeError
from .lexer import Token

ENV_RE = re.compile(r"\$\((\w+)\)")
ARG_RE = re.compile(r"\bargs\[(\d+)\]")
ARGC_WORD_RE = re.compile(r"(?<!\S)argc(?!\S)")
ARGC = "argc"


def expand_text(text: str, args: list[str]) -> str:
    """Replace every $(ENV) and args[N] inside text."""

    def env(match: re.Match) -> str:
        name = match.group(1)
        if name not in os.environ:
            raise RecipeError(f"environment variable not found: {name}")
        return os.environ[name]

    def arg(match: re.Match) -> str:
        index = int(match.group(1))
        if index >= len(args):
            raise RecipeError(f"args[{index}] out of range (argc = {len(args)})")
        return args[index]

    return ARG_RE.sub(arg, ENV_RE.sub(env, text))


def expand_token(token: Token, args: list[str]) -> str:
    """Expand a token. A bare (unquoted) `argc` becomes the number of arguments."""
    if not token.quoted and token.value == ARGC:
        return str(len(args))
    return expand_text(token.value, args)


def expand_shell(text: str, args: list[str]) -> str:
    """Expand raw shell text, keeping its quoting and spacing untouched."""
    return ARGC_WORD_RE.sub(str(len(args)), expand_text(text, args))
