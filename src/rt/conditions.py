"""`if A OP B` conditions.

`==` and `!=` compare numerically when both sides are numbers, otherwise as text.
`<`, `>`, `<=`, `>=` require numbers.
"""

from __future__ import annotations

import operator
import re
from typing import TYPE_CHECKING

from .errors import RecipeError, RecipeSyntaxError

if TYPE_CHECKING:
    from .context import Context
    from .parser import Statement

OPERATORS = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.le,
    ">=": operator.ge,
}
EQUALITY = {"==", "!="}
NUMBER_RE = re.compile(r"[+-]?\d+(\.\d+)?")


def validate(stmt: Statement) -> None:
    if len(stmt.args) != 3 or stmt.args[1].value not in OPERATORS:
        raise RecipeSyntaxError(f"usage: if VALUE OPERATOR VALUE  (operators: {' '.join(OPERATORS)})")


def _number(text: str) -> int | float | None:
    if not NUMBER_RE.fullmatch(text):
        return None
    return float(text) if "." in text else int(text)


def compare(left: str, op: str, right: str) -> bool:
    a, b = _number(left), _number(right)
    if a is not None and b is not None:
        return OPERATORS[op](a, b)
    if op in EQUALITY:
        return OPERATORS[op](left, right)
    raise RecipeError(f"operator {op} needs numbers, got {left!r} and {right!r}")


def evaluate(ctx: Context, stmt: Statement) -> bool:
    left = ctx.expand(stmt.args[0])
    right = ctx.expand(stmt.args[2])
    return compare(left, stmt.args[1].value, right)
