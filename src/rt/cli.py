"""Command line entry point.

Exit codes: 0 ok, 1 recipe failed, 2 wrong usage.
"""

from __future__ import annotations

import sys
from typing import Callable

from . import UPDATE_URL, helptext, log, packing, runner
from .errors import ParseErrors, RtError, UsageError

HELP_FLAGS = {"-h", "-help", "--help"}


def _need(args: list[str], count: int, usage: str) -> None:
    if len(args) < count:
        raise UsageError(f"usage: {usage}")


def _action(option: str, rest: list[str], depth: int) -> Callable[[], None]:
    if option == "-url":
        _need(rest, 1, "rt -url URL [ARGS...]")
        return lambda: runner.run_url(rest[0], rest[1:], depth)
    if option == "-update":
        if rest:
            raise UsageError("usage: rt -update")
        return lambda: runner.run_url(UPDATE_URL, [], depth)
    if option.startswith("-"):
        raise UsageError(f"unknown option: {option} (see rt --help)")
    return lambda: runner.run_path(option, rest, depth)


def dispatch(argv: list[str], depth: int = 0) -> int:
    if not argv or argv[0] in HELP_FLAGS:
        helptext.show_help()
        return 0
    if depth > runner.MAX_DEPTH:
        log.error(f"too many nested rt calls (> {runner.MAX_DEPTH})")
        return 1

    option, rest = argv[0], argv[1:]
    try:
        if option == "-show":
            _need(rest, 1, "rt -show PACKAGE")
            packing.show_package(rest[0])
            return 0
        action = _action(option, rest, depth)
    except UsageError as exc:
        log.error(str(exc))
        return 2
    except RtError as exc:
        log.error(str(exc))
        return 1

    errors = 0
    try:
        action()
    except ParseErrors as exc:
        for err in exc.errors:
            log.error(f"syntax error: {err}")
        errors = len(exc.errors)
    except RtError as exc:
        log.error(str(exc))
        errors = 1

    if depth == 0:
        if errors:
            log.error(f"Finished with {errors} error(s)")
        else:
            log.success("Done!")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    try:
        return dispatch(sys.argv[1:] if argv is None else argv)
    except KeyboardInterrupt:
        log.error("interrupted")
        return 130
