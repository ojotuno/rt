from enum import Enum

class action_t(Enum):
    none = -1
    add = 0
    ignore = 1

class Instruction:
    def __init__(self, action, data, from_as, lineNum):
        self.action = action
        self.data = data
        self.from_as = from_as
        self.line = lineNum

    action: action_t.none
    data = "" # first argument = path, pattern, file or extension
    from_as = "" # argument 2. empty = root_dir
    line = -1

# list of lists [[[src..], [dest..]], ] to follow to pack
packfiles = []

# recepie arguments <name, value>
arguments = []

# root dir -> pair (root_dir, path_in_package)
root_dir = ""

# target dir
target_dir = ""

original_workingdir = ""

# install file const
install_file = "install"

# Constants (keywords)
class Keywords:
    ADD = "add"
    IGNORE = "ignore"
    ROOT_DIR = "root_dir"  # mandatory
    TARGET_DIR = "target_dir"  # mandatory
    PACK = "pack"  # mandatory (meanwhile install does not exist)
    RUN_CMD = ">"
    ENV_VAR = "$"
    COMMENT = "#"
    AND = "and"
    PRINT = "print"
    ARGS = "args"
    GIT = "git"
    SVN = "svn"
    AS = "as"
    FROM = "from"
