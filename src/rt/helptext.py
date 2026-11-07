"""`rt --help`. The keyword list is generated from the command registry."""

from . import BUILD, commands, log

LOGO = r"""
 .----------------.  .----------------.
| .--------------. || .--------------. |
| |  _______     | || |  _________   | |
| | |_   __ \    | || | |  _   _  |  | |
| |   | |__) |   | || | |_/ | | \_|  | |
| |   |  __ /    | || |     | |      | |
| |  _| |  \ \_  | || |    _| |_     | |
| | |____| |___| | || |   |_____|    | |
| |              | || |              | |
| '--------------' || '--------------' |
 '----------------'  '----------------'"""

USAGE = """\
Usage:
  rt RECIPE [ARGS...]            run a recipe
  rt PACKAGE [DEST] [ARGS...]    extract a .rt/.tar.gz package into DEST (default: .)
                                 and run its `install` recipe
  rt -url URL [ARGS...]          download a recipe or package and run it
  rt -show PACKAGE               show the content of a package
  rt -update                     update rt to the latest release
  rt -h | --help                 this help"""

LANGUAGE = [
    ("if A OP B ... end", "Run the block when the condition holds. OP: == != < > <= >= "
                          "(< > <= >= need numbers). Blocks can be nested."),
    ("args[N]", "Argument N. args[0] is the recipe/package, args[1].. the user arguments."),
    ("argc", "Number of arguments, args[0] included."),
    ("$(ENV)", "Value of the environment variable ENV (error if it is not set)."),
    ("# comment", "Comment until end of line (when # starts a word outside quotes)."),
]


def _entry(usage: str, summary: str) -> None:
    log.plain("  " + log.paint(usage, "blue"))
    log.plain("      " + summary)


def show_help() -> None:
    log.plain(log.paint(LOGO, "green"))
    log.plain(log.paint(f" Build: {BUILD}", "red"))
    log.plain("")
    log.plain(USAGE)
    log.plain("")
    log.plain("Recipe keywords (one statement per line):")
    for cmd in commands.all_commands():
        _entry(cmd.usage, cmd.summary)
    log.plain("")
    log.plain("Language:")
    for usage, summary in LANGUAGE:
        _entry(usage, summary)
