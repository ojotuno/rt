import globals as g
import messages as msg
import subprocess
import tarfile
import utils
import sys
import glob
import os

kw = g.Keywords()

def tokenize(line, lineNum, separator=" "):
    tokens = []
    str = ""
    quotes = False
    for char in line:
        if char == kw.COMMENT:
            return tokens
        elif char == separator:
            if not quotes:
                tokens.append(utils.resolve(str, lineNum))
                str = ""
            else:
                str += char # add space as part of the token because is in a quoted string
        else:
            if char == '"':
                if quotes:
                    quotes = False
                else:
                    quotes = True
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

def pack(filename, lineNum):
    # pack file following the instructions
    ########################################
    if (g.target_dir == ""):
        msg.info("target_dir not defined. The default target_dir is working directoy")
        g.target_dir = os.getcwd()

    if g.root_dir == "":
        msg.info("root_dir is empty. Processing relative paths from working directory")
    else:
        if os.path.isdir(g.root_dir):
            os.chdir(g.root_dir) #set working directoy
        else:
            msg.error("root_dir is set but it is not a valid directoy. Aborted!")        

    if msg.g_error == False:
        msg.info("Generating " + filename + "...",)
        for i in g.instructions:
            if "*" in i.data: #using wildcards
                if not os.path.isabs(i.data): ## if relative
                        i.data = os.path.abspath(i.data)
                
                g.packfiles += glob.glob(i.data, recursive=True) ## add files from wildcards
            else:
                if os.path.isdir(i.data): ## if directory
                    if not os.path.isabs(i.data): ## if relative
                        i.data = os.path.abspath(i.data)
                
                    for currentDir, subdirs, files in os.walk(i.data):
                        for f in files:
                            g.packfiles.append(currentDir + "/" + f) ## add files from directories with no wildcards
                else: # add just a file
                    g.packfiles.append(i.data)
        
        print("Files to pack")
        print(g.packfiles)

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