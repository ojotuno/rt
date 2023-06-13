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


# append add instruction to the list
def append_instruction(action, data, from_as_data = ""):
    i = g.Instruction(action, data, from_as_data)
    g.instructions.append(i)

# set root_dir
def set_root_dir(value):
    g.root_dir = value

#set targer_dir
def set_target_dir(value):
    g.target_dir = value

#print functions
def print_str(str):
    msg.print_recipe_msg(str)

# get arguments from command line
def add_arguments():
    for i, arg in enumerate(sys.argv):
        if i > 0: # discard rt name
            g.arguments.append(arg)


# pack file following the instructions
def pack(filename):

    # clean data for the new pack
    g.instructions.clear


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

    
