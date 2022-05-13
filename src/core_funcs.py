import globals as g
import messages as msg
import subprocess
import tarfile

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
  g.root_dir = value

def set_target_dir(value):
  g.target_dir = value

def print_str(str):
  msg.print_recipe_msg(str)

def add_arguments(arg):
  g.argument.append(arg)

def add_alias(alias, value):
  g.aliases[alias] = value

def pack(filename):
  return ""

def run_cmd(command):
  try:
    p = subprocess.run(command, shell=True, check=True, universal_newlines=True)
  except subprocess.CalledProcessError as e:
    msg.info("Returned code " + str(e.returncode))

# get file esxtension
def get_file_ext(file):
  dot_index = file.find(".")
  return file[dot_index + 1: len(file)]

def extract_TAR(tar_file, dest):
  tarball = tarfile.open(tar_file, "r:gz")
  msg.info("Decompressing package \"" + tar_file + "\"...", '')
  tarball.extractall(dest)
  msg.append_ok()
  tarball.close()

def extract_ZIP(zipfile):
  msg.error("ZIP files not implemented yet")

