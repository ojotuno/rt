"""Split recipe lines into tokens.

Rules:
- Tokens are separated by spaces or tabs.
- "double quotes" group text (spaces included). Inside quotes, \\" and \\\\ are escapes.
- `#` starts a comment when it begins a word outside quotes (so `issue#1` is kept).
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import RecipeSyntaxError


@dataclass(frozen=True)
class Token:
    value: str
    quoted: bool = False


def strip_comment(text: str) -> str:
    in_quotes = False
    escaped = False
    for i, char in enumerate(text):
        if escaped:
            escaped = False
        elif char == "\\" and in_quotes:
            escaped = True
        elif char == '"':
            in_quotes = not in_quotes
        elif char == "#" and not in_quotes and (i == 0 or text[i - 1].isspace()):
            return text[:i]
    return text


def tokenize(text: str) -> list[Token]:
    """Tokenize text that has already had its comment removed."""
    tokens: list[Token] = []
    buf: list[str] = []
    in_word = in_quotes = quoted = escaped = False

    for char in text:
        if escaped:
            buf.append(char)
            escaped = False
        elif in_quotes:
            if char == "\\":
                escaped = True
            elif char == '"':
                in_quotes = False
            else:
                buf.append(char)
        elif char == '"':
            in_word = in_quotes = quoted = True
        elif char.isspace():
            if in_word:
                tokens.append(Token("".join(buf), quoted))
                buf, in_word, quoted = [], False, False
        else:
            buf.append(char)
            in_word = True

    if in_quotes:
        raise RecipeSyntaxError("unterminated quoted string")
    if in_word:
        tokens.append(Token("".join(buf), quoted))
    return tokens
