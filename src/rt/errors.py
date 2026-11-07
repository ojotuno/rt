"""Exceptions used across RT."""

from __future__ import annotations


class RtError(Exception):
    """Base error. Optionally carries the recipe location where it happened."""

    def __init__(self, message: str, line: int | None = None, source: str | None = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.source = source

    def locate(self, line: int, source: str) -> RtError:
        """Attach a location if the error does not have one yet."""
        if self.line is None:
            self.line, self.source = line, source
        return self

    def __str__(self) -> str:
        if self.line is None:
            return self.message
        return f"{self.source}:{self.line}: {self.message}"


class UsageError(RtError):
    """Wrong command line usage."""


class RecipeSyntaxError(RtError):
    """A recipe line is malformed. Detected before anything runs."""


class ParseErrors(RtError):
    """All syntax errors found in a recipe."""

    def __init__(self, errors: list[RecipeSyntaxError]):
        super().__init__(f"{len(errors)} syntax error(s)")
        self.errors = errors


class RecipeError(RtError):
    """A recipe statement failed while running."""


class RecipeExit(Exception):
    """Raised by `exit` to stop the current recipe successfully."""
