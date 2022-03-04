import globals as g

# add class Path
def add_path(path):
  g.paths2Add.append(path)

# add path into dict
def add_file(file, newPathInPckg):
  g.files2Add[file] = newPathInPckg  

def add_ext(ext):
  g.ext2Add.append(ext)

def ignore_path(path):
  g.paths2Ignore.append(path)

def ignore_file(file):
  g.files2ignore.append(file)

def ignore_ext(ext):
  g.ext2ignore.append(ext)

def set_root_dir(value):
  g.root_dir = value;

def set_target_dir(value)
  g.target_dir = value;

def print(str):
  print(str);

def add_arguments(arg):
  g.argument.append(arg)

def add_alias(alias, value):
  g.aliases[alias] = value

def pack(filename):
  return ""

# get file esxtension
def get_file_ext(file):
  dot_index = file.find(".")
  return file[dot_index + 1: len(file)]