"""Turn recipe text into a tree of nodes.

The whole recipe is parsed (and every syntax error collected) before anything runs,
so a typo at the end of a recipe never leaves it half executed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Union

from . import commands, conditions
from .errors import ParseErrors, RecipeSyntaxError
from .lexer import Token, strip_comment, tokenize

SHELL = ">"
IF = "if"
END = "end"


@dataclass
class Statement:
    keyword: str
    args: list[Token]
    rest: str  # raw text after the keyword (used by shell commands)
    line: int
    source: str


@dataclass
class IfBlock:
    condition: Statement
    body: list["Node"] = field(default_factory=list)


Node = Union[Statement, IfBlock]


def lex_line(raw: str, line: int, source: str) -> Statement | None:
    text = strip_comment(raw).strip()
    if not text:
        return None
    if text.startswith(SHELL):  # `> cmd` and `>cmd`
        keyword, rest = SHELL, text[len(SHELL):].strip()
    else:
        parts = re.split(r"\s+", text, maxsplit=1)
        keyword, rest = parts[0], parts[1] if len(parts) > 1 else ""
    return Statement(keyword, tokenize(rest), rest, line, source)


def parse(text: str, source: str = "<recipe>") -> list[Node]:
    root: list[Node] = []
    stack: list[tuple[IfBlock | None, list[Node]]] = [(None, root)]
    errors: list[RecipeSyntaxError] = []

    for number, raw in enumerate(text.splitlines(), start=1):
        try:
            stmt = lex_line(raw, number, source)
            if stmt is None:
                continue
            if stmt.keyword == IF:
                conditions.validate(stmt)
                block = IfBlock(stmt)
                stack[-1][1].append(block)
                stack.append((block, block.body))
            elif stmt.keyword == END:
                if stmt.args:
                    raise RecipeSyntaxError("end does not accept arguments")
                if len(stack) == 1:
                    raise RecipeSyntaxError("end without a matching if")
                stack.pop()
            else:
                command = commands.get(stmt.keyword)
                if command is None:
                    raise RecipeSyntaxError(f"unknown keyword: {stmt.keyword}")
                command.check(stmt)
                stack[-1][1].append(stmt)
        except RecipeSyntaxError as exc:
            errors.append(exc.locate(number, source))

    for block, _ in stack[1:]:
        errors.append(RecipeSyntaxError("if without end", block.condition.line, source))

    if errors:
        raise ParseErrors(errors)
    return root
