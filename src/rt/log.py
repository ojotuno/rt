"""Console output. Colors are only used on a TTY and when NO_COLOR is not set."""

import os
import sys

PREFIX = "[rt] "

COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "grey": "\033[90m",
}
RESET = "\033[0m"


def _use_color(stream) -> bool:
    return "NO_COLOR" not in os.environ and hasattr(stream, "isatty") and stream.isatty()


def paint(text: str, color: str, stream=None) -> str:
    stream = stream or sys.stdout
    return f"{COLORS[color]}{text}{RESET}" if _use_color(stream) else text


def _emit(stream, text: str, end: str = "\n") -> None:
    # Flush both streams so our output and child process output stay ordered.
    other = sys.stderr if stream is sys.stdout else sys.stdout
    other.flush()
    stream.write(text + end)
    stream.flush()


def plain(msg: str, end: str = "\n") -> None:
    """Recipe output (print, progress): no prefix."""
    _emit(sys.stdout, msg, end)


def info(msg: str) -> None:
    _emit(sys.stdout, PREFIX + msg)


def success(msg: str) -> None:
    _emit(sys.stdout, PREFIX + paint(msg, "green"))


def warn(msg: str) -> None:
    _emit(sys.stderr, PREFIX + paint("Warning: " + msg, "yellow", sys.stderr))


def error(msg: str) -> None:
    _emit(sys.stderr, PREFIX + paint("Error: " + msg, "red", sys.stderr))
