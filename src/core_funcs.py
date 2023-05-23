import globals as g
import messages as msg
import subprocess
import tarfile
import utils
import sys

kw = g.Keywords()

def tokenize(line, lineNum, separator=" "):
    tokens = []
    str = ""
    for char in line:
        if char == kw.comment:
            return tokens
        elif char == separator:
            tokens.append(utils.resolve(str, lineNum))
            str = ""
        else:
            if char != "\n":
                str += char
    
    if len(str) > 0:
        tokens.append(utils.resolve(str, lineNum))

    return tokens


# add class Path
def add_path(srcPath, pathInsidePckg):
    g.paths2Add.append((srcPath, pathInsidePckg))


# add path into dict
def add_file(file, newPathInPckg):
    g.files2Add[file] = newPathInPckg


def add_ext(path, ext, recursive):
    if path not in g.ext2Add:
        g.ext2Add[path] = {}
    g.ext2Add[path][ext] = recursive  # create key entry


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


def add_arguments():
    for i, arg in enumerate(sys.argv):
        if i > 0: # discard rt name
            g.arguments.append(arg)
    

def add_alias(alias, value):
    g.aliases[alias] = value


def pack(filename):
    # pack
    clean_data_from_instructions()


def run_cmd(command):
    try:
        p = subprocess.run(command, shell=True, check=True, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        msg.info("Returned code " + str(e.returncode))


# get file esxtension
def get_file_ext(file):
    dot_index = file.find(".")
    return file[dot_index + 1 : len(file)]


def extract_TAR(tar_file, dest):
    tarball = tarfile.open(tar_file, "r:gz")
    msg.info('Decompressing package "' + tar_file + '"...', "")
    tarball.extractall(dest)
    msg.append_ok()
    tarball.close()


def compress_TAR(tar_file, files, dest):
    tarball = tarfile.open(dest + tar_file, "r:gz")
    msg.info('Creating package "' + tar_file + '"...', "")
    # TODO: hacer bien
    tarball.add()


def extract_ZIP(zipfile):
    msg.error("ZIP files not implemented yet")


def clean_data_from_instructions():
    g.paths2Add.clear()
    g.files2Add.clear()
    g.ext2Add.clear()
    g.files2ignore.clear()
    g.paths2ignore.clear()
    g.ext2ignore.clear()
