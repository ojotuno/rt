from enum import Enum

class action_t(Enum):
    none = -1
    add_path = 0
    add_file = 1
    add_ext = 2
    ignore_path = 3
    ignore_file = 4
    ignore_ext = 5


class Actions:
    action: action_t.none
    data = "" # first argument = path, pattern, file or extension
    from_as = "" # argument 2. empty = root_dir

#dict instructions {path, actions}
instrcutions = {}

# recepie arguments <name, value>
arguments = []

# aliases <alias, value>
aliases = {}

# root dir
root_dir = ""

# target dir
target_dir = ""

# install file
install_file = "install"

# keywords
keywords = (
    "args",
    "root_dir",
    "target_dir",
    "add_path",
    "add_file",
    "add_ext",
    "ignore_path",
    "ignore_file",
    "ignore_ext",
    "pack",
    "git",
    "svn",
    ">",
    "print"
)


# Constants (keywords)
class Keywords:
    add_path = "add_path"
    add_file = "add_file"
    add_ext = "add_ext"
    ignore_path = "ignore_path"
    ignore_file = "ignore_file"
    ignore_ext = "ignore_ext"
    root_dir = "root_dir"  # mandatory
    target_dir = "target_dir"  # mandatory
    pack = "pack"  # mandatory (meanwhile install does not exist)
    run_cmd = ">"
    env_var = "$"
    comment = "#"
    amd = "and"
    print = "print"
    arguments = "args"
    git = "git"
    svn = "svn"
