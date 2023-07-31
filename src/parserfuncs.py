import globals as g
import messages as msg
import subprocess
import tarfile
import utils
import sys
import glob
import os
import colors

kw = g.Keywords()

def tokenize(line, lineNum, separator=' '):
    tokens = []
    token = ""
    quotes = False
    for char in line:
        if char == kw.COMMENT:
            return tokens
        elif char == separator:
            if not quotes and len(token) > 0:
                tokens.append(utils.resolve(token, lineNum))
                token = ""
            elif quotes:   
                token += char # add space as part of the token because is in a quoted string
        else:
            if char == '"':
                if quotes:
                    quotes = False
                else:
                    quotes = True
            if char not in ['\n', '\t']:
                token += char
    
    if len(token) > 0:
        tokens.append(utils.resolve(token, lineNum))

    return tokens


# append add instruction to the list
def append_instruction(action, data,  as_or_in = "", from_as_data = "", lineNum = -1):
    inst = g.Instruction(action, data, as_or_in, from_as_data, lineNum)
    process_instruction(inst)

# set root_dir
def set_root_dir(path, lineNum):
    path = utils.resolve(path, lineNum)
    if (not utils.using_wildcards(path) and os.path.isdir(path)):
        g.root_dir = os.path.abspath(path)
        os.chdir(g.root_dir) #set working directoy
        msg.info("set root_dir -> " + path)
    else:
        msg.error("root_dir contains a invalid path", lineNum)

#set targer_dir
def set_target_dir(path, lineNum):
    path = utils.resolve(path, lineNum)
    if not utils.using_wildcards(path)  and os.path.isdir(path):
        g.target_dir = path
        msg.info("set target_dir -> " + path)
    else:
        msg.error("target_dir contains a invalid path", lineNum)

#print functions
def print_str(str):
    msg.print_recipe_msg(str)

# get arguments from command line
def add_arguments():
    for i, arg in enumerate(sys.argv):
        if i > 0: # discard rt name
            g.arguments.append(arg)

def process_instruction(inst):
    searchPath = ""
    ## set paths from ignore
    if inst.action == g.action_t.ignore:
        if len(inst.from_as) > 0 :
            if os.path.isabs(inst.from_as):
                searchPath = inst.from_as + "/" + inst.data
            else:
                msg.error("Instructions only allows absolute paths in from-statement. Aborted!", inst.line)
        else:
            searchPath = os.path.abspath(inst.data)
    else: # set path from add
        searchPath = os.path.abspath(inst.data)

    filesPerInstruc = []
    # get all the files
    if msg.g_error == False:
        if "*" in searchPath: # WILDCARDS
            try:
                # resolve wildcards and get files
                filesPerInstruc = glob.glob(searchPath, recursive=True) 
            except:
                msg.error(inst.data + " cannot be resolved")
        else: # NOT WILDCARDS
            # -------- DIRECTORY ---------#
            if os.path.isdir(searchPath): 
                for currentDir, subdirs, files in os.walk(searchPath):
                    for f in files:
                        filesPerInstruc.append(currentDir + "/" + f)
            # ------- FILES ------------#
            elif os.path.isfile(searchPath): 
                filesPerInstruc.append(searchPath)
            else:
                msg.warning("File " + searchPath + " not found in line " + str(inst.line) + ". Step skipped!")
                pass                

        ## ADD files  
        if (inst.action == g.action_t.add and len(filesPerInstruc) > 0): 
            for f in filesPerInstruc:
                if "/" in f: #directories -> get dest list
                    pos = searchPath.rfind('/')
                    if pos > -1: # constains a wildcard
                        root = searchPath[:pos] # get path until first occurence of * (if so)
                    else:
                        root = searchPath
                    
                    destFiles = []
                    if len(inst.from_as) > 0:
                        if inst.as_in == g.Keywords.AS:
                            if inst.from_as[len(inst.from_as)-1] != "/":
                                g.packfiles.append([f, inst.from_as])
                            else:
                                msg.error("Value of as-statement cannot be a path. Aborted!", str(inst.line))
                                break
                        elif inst.as_in == g.Keywords.IN:
                             # if as value doesn´t end in /, append it
                            if inst.from_as[len(inst.from_as) - 1] != "/": 
                                inst.from_as += '/'
                            destFiles = (f.replace(root, inst.from_as)).replace("//", "/") # sanitace path
                            g.packfiles.append([f, destFiles])
                    else:
                        destFiles = (f.replace(root, "")).replace("//", "/") # sanitace path
                        g.packfiles.append([f, destFiles])
                  
                    # destFiles.append(f.replace(g.root_dir, "")) #TODO: option of create root dir will be here

                else: # it is a file -> insert in global list directly
                    g.packfiles.append([f, ""])

        ## IGNORE files -> remove from list of files to add
        elif inst.action == g.action_t.ignore:
            i = 0
            while i < len(g.packfiles): #loop over list of list -> item will be a list
                for fileToignore in filesPerInstruc:
                    if g.packfiles[i][0] == fileToignore:
                        del g.packfiles[i]
                        i -= 1
                i += 1


def pack(filename, lineNum):
    # pack file following the instructions
    ########################################
    if (g.target_dir == ""):
        msg.warning("target_dir not defined. The default target_dir is the script working directoy")
        set_target_dir(g.original_workingdir, lineNum)

    if g.root_dir == "":
        msg.warning("root_dir is empty. Processing relative paths from working directory")
        set_root_dir(g.original_workingdir, lineNum)          

    if msg.g_error == False:
        create_targz(filename)
        # clean data for the new pack
        g.instructions = []
        g.packfiles = []

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
    if os.path.isfile(tar_file):
        tarball = tarfile.open(tar_file, "r:gz")
        msg.info('Decompressing package "' + tar_file + '"...', "")
        tarball.extractall(dest)
        msg.append_ok()
        tarball.close()
    else:
        msg.error("File not found " + tar_file);

def create_targz(filename):
    msg.info(colors.darkmagenta + 'Packing "' + filename + colors.off)
    targzfile = (g.target_dir + "/" + filename).replace("//", "/") # sanitace path
    if (os.path.isfile(targzfile)):
        os.remove(targzfile)
    tarball = tarfile.open(targzfile, "w:gz")
    numFiles = 0
    #calculate num of files
    numFiles = len(g.packfiles)
    currentNumFile = 1

    # pack
    for fileList in g.packfiles:
        print_str("[" + str(currentNumFile) +  "/" + str(numFiles) + "] " + fileList[0] + " -> " + fileList[1])
        tarball.add(fileList[0], fileList[1])
        currentNumFile += 1

    tarball.close()
    msg.success("Package created: " + targzfile)

def extract_ZIP(zipfile):
    msg.error("ZIP files not implemented yet")