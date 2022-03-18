#class path
class Path:
  path : '' #path value
  pathInPckg : '' # path name inside tha package
  ext2ignore : [] #extensions to ignore while adding the path
  files2Ignore : [] #files to ignore while adding the files
  paths2Ignore : [] # paths/ subpaths to ignore while adding the path

# paths to add list<Path>
paths2Add = []

# files to add 
# dict {path : newPathInPckg}
files2Add = []

# extension to add
ext2Add = []

# files to ignore
files2ignore = []

# paths to ignore
paths2ignore = []

# extension to ignore
ext2ignore = []

# recepie arguments <name, value>
arguments = []

#aliases <alias, value>
aliases = {}

# keywords
keywords = ("arguments", "root_dir", "target_dir", "add_path", "add_file", "add_ext",
"ignore_path", "ignore_file", "ignore_ext", "pack", "git", "svn", ">", "print")

# root dir
root_dir = ""

#target dir
target_dir = ""

# install file
install_file = "install"

# Constants (keywords)
class Keywords:
    add_path = 'add_path'
    add_file = 'add_file'
    add_ext = 'add_ext'
    ignore_path = 'ignore_path'
    ignore_file = 'ignore_file'
    ignore_ext = 'ignore_ext'
    root_dir = "root_dir" #mandatory
    target_dir = "target_dir" #mandatory
    pack = "pack" #mandatory (meanwhile install does not exist)
    run_cmd = ">"
    env_var = "$"
    comment = '#'
    amd = "and"
    print = "print"
    arguments = "arguments"
    git = "git"
    svn = "svn"