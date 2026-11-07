# RT - Recipe Tool

RT packs, installs and automates projects using plain-text **recipes**.
No configuration and no dependencies: just Python 3.

## Installation

Download the `.tar.gz` release, extract it and run `./install.sh`.
It installs to `/usr/local` (`/usr/local/lib/rt` + `/usr/local/bin/rt`) and uses sudo if needed.
To install without sudo: `PREFIX=$HOME/.local ./install.sh`.

## Update

```
rt -update
```

## Usage

```
rt RECIPE [ARGS...]            run a recipe
rt PACKAGE [DEST] [ARGS...]    extract a package into DEST (default: .) and run its `install` recipe
rt -url URL [ARGS...]          download a recipe or package and run it
rt -show PACKAGE               show the content of a package
rt -update                     update rt to the latest release
rt -h | --help                 help (lists every keyword)
```

- A **package** (`.rt`, `.tar.gz`) is a gzip tar archive. RT detects it by content, not by extension.
  To make it installable, include a recipe named `install`. It runs from its own directory inside DEST.
- Anything else is treated as a recipe.
- With `-url`, the file is downloaded to a temp dir (removed afterwards). Packages are installed
  from there, and recipes run in the current directory.
- Exit code: `0` ok, `1` the recipe failed, `2` wrong usage.

## Recipes

There is one statement per line: `keyword arguments...`.
The whole recipe is checked for syntax errors **before** anything runs.
At runtime the first error stops the recipe.

### Packing

| Statement | Description |
|---|---|
| `root_dir PATH` | Change the working directory. Relative paths and `>` commands run from here. |
| `target_dir PATH` | Directory where `pack` writes packages (created if missing). If it is not set, RT uses the directory where it was started. |
| `add PATTERN` | Queue files. A directory keeps its own name (`add res` gives `res/...`). Wildcards: `*` `?` `[]` `**`. With wildcards, paths are kept relative to the part before the first wildcard (`add src/**/*.c` gives `lib/util.c`, `main.c`). |
| `add PATTERN in DIR` | Put the matches inside DIR in the package. |
| `add PATH as NAME` | Rename a single file or directory in the package. |
| `ignore PATTERN [from DIR]` | Exclude files from the next `pack`, wherever the `ignore` appears in the recipe. A name without `/` (`*.o`, `__pycache__`) matches anywhere below DIR. A path (`./build`, `src/*.o`) matches that path and everything under it. DIR defaults to the current directory. |
| `pack FILENAME` | Write the queued files to `target_dir/FILENAME` and clear the queue (the `add`s and `ignore`s). |

### Running things

| Statement | Description |
|---|---|
| `> COMMAND` | Run a shell command. A non-zero exit code stops the recipe (use `|| true` to allow failures). |
| `git ARGS...` / `svn ARGS...` | Run git / svn. |
| `rt [-url] RECIPE\|PACKAGE [ARGS...]` | Run another recipe or package. If it fails, this recipe stops. Its `exit` and `root_dir` don't affect the caller. |
| `print "TEXT" [VALUE ...]` | Print the values joined **without** separator (put spaces inside quotes). |
| `exit` | Stop the current recipe successfully. |
| `if A OP B` ... `end` | Conditional block, can be nested. `==` `!=` compare as numbers when both sides are numbers, otherwise as text. `<` `>` `<=` `>=` need numbers. |

### Values

| Syntax | Value |
|---|---|
| `args[N]` | Argument N. `args[0]` is the recipe/package, `args[1]`... the user arguments. |
| `argc` | Number of arguments, `args[0]` included. |
| `$(ENV)` | Environment variable (error if not set). `$HOME` without parentheses is left as is, for the shell. |
| `"..."` | Quoted text keeps spaces. `\"` and `\\` are escapes. `$(ENV)` and `args[N]` also expand inside quotes. |
| `# ...` | Comment, when `#` starts a word outside quotes. |

### Example

```
# rt release.rcp 1.2.0
if argc < 2
print "usage: rt release.rcp VERSION"
exit
end

target_dir $(HOME)/releases
root_dir ./project

> ./scripts/create_version_file.sh args[1]

add bin
add config in etc/myapp
add install.sh
add packaging/install as install
ignore *.o
ignore ./bin/debug

print "Packing version " args[1]
pack myapp-args[1].rt

git tag release-args[1]
```

## Development

```
bin/rt RECIPE ...              # run from the source checkout
python3 -m pip install pytest
python3 -m pytest              # test suite
./build-new-release-version    # build number + releases/rt.tar.gz and releases/rt.rt
```

Layout (`src/rt/`):

| Module | Role |
|---|---|
| `cli.py` | Command line options, exit codes |
| `runner.py` | Run recipes, install packages, downloads |
| `lexer.py` → `parser.py` | Text → tokens → tree of statements and `if` blocks (all syntax errors collected) |
| `interpreter.py` | Walks the tree |
| `context.py` | State of one running recipe (args, target_dir, pack queue) |
| `expand.py` | `$(ENV)`, `args[N]`, `argc` |
| `conditions.py` | `if` operators |
| `packing.py` | add/ignore logic, tar creation, safe extraction, `-show` |
| `commands/` | Keywords, one decorated function each |

### Adding a keyword

Add a function to any module in `src/rt/commands/` (or add a new module and import it at the end of `commands/__init__.py`):

```python
@command("mkdir", usage="mkdir PATH", nargs=1, summary="Create a directory.")
def mkdir(ctx, stmt):
    path = ctx.expand(stmt.args[0])          # resolves $(ENV), args[N], argc
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as exc:
        raise RecipeError(f"mkdir: {exc}")   # stops the recipe with file:line
```

The argument count (`nargs` / `min_args`, plus an optional `validate`) is checked when the recipe is parsed.
The keyword shows up in `rt --help` automatically. `stmt.rest` holds the raw text after the keyword (as used by `>`).
Block keywords (like `if`) live in `parser.py` and `interpreter.py`.
