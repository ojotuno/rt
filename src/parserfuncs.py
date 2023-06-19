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
def append_instruction(action, data, from_as_data = "", lineNum = -1):
    i = g.Instruction(action, data, from_as_data, lineNum)
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
        msg.warning("target_dir not defined. The default target_dir is working directoy")
        g.target_dir = os.getcwd()
    else:
         if not os.path.isdir(g.target_dir):
            msg.error("target_dir is set but it is not a valid directoy. Aborted!")   
            msg.warning("target_dir = " + g.target_dir)   

    if g.root_dir == "":
        msg.warning("root_dir is empty. Processing relative paths from working directory")
        g.root_dir = os.getcwd()
    else:
        if os.path.isdir(g.root_dir):
            os.chdir(g.root_dir) #set working directoy
        else:
            msg.error("root_dir is set but it is not a valid directoy. Aborted!")        
            msg.warning("root_dir = " + g.root_dir)   

    if msg.g_error == False:
        for i in g.instructions:
            searchPath = ""
            ## set paths from ignore
            if i.action == g.action_t.ignore:
                if len(i.from_as) > 0 :
                    if os.path.isabs(i.from_as):
                        searchPath = i.from_as + "/" + i.data
                    else:
                        msg.error("Instructions only allow from-statement values as absolute path. Aborted!", i.line)
                        break
                else:
                    searchPath = os.path.abspath(i.data)
            else: # set path from add
                searchPath = os.path.abspath(i.data)

            filesPerInstruc = []
            if "*" in searchPath: # WILDCARDS
                try:
                    filesPerInstruc = glob.glob(searchPath, recursive=True) ## add files from wildcards
                except:
                    msg.error(i.data + " cannot be resolved")
            else: # NOT WILDCARDS
                if os.path.isdir(searchPath): ## if directory
                    for currentDir, subdirs, files in os.walk(searchPath):
                        for f in files:
                            filesPerInstruc.append(currentDir + "/" + f)
                elif os.path.isfile(searchPath): # add just a file
                    if len(i.from_as) == 0:
                        if i.action == g.action_t.ignore:
                            filesPerInstruc = searchPath
                        else:
                            filesPerInstruc = [[searchPath], [searchPath.replace(g.root_dir, "")]]
                    else: # there is from/as
                        if i.action == g.action_t.ignore:
                            filesPerInstruc = i.from_as + searchPath
                        else:
                            if i.from_as[len(i.from_as)-1] == "/": # file added into dir
                                msg.info(colors.darkblue + searchPath + colors.off + 
                                        " will be added into " + colors.darkblue + i.from_as + colors.off)
                                i.from_as = i.from_as + searchPath
                            else: # file renamed
                                msg.info(colors.darkblue + searchPath + colors.off + " renamed to " +
                                        colors.darkblue + i.from_as + colors.off)

                            filesPerInstruc = [[searchPath], [i.from_as]]
                else:
                    msg.warning("File " + searchPath + " not found in line " + str(i.line) + ". Step skipped!")
                    pass                

            ## ADD files  
            if (i.action == g.action_t.add): 
                if len(filesPerInstruc) > 0 and type(filesPerInstruc[0]) is str: #directories -> get dest list
                    pos = searchPath.find('*')
                    if pos > -1:
                        root = searchPath[:pos] # get path until first occurence of * (if so)
                    else:
                        root = searchPath

                    if len(i.from_as) > 0 and (i.from_as[len(i.from_as) - 1] is not "/"): # if as value dont ends in /, append it
                        i.from_as += '/'

                    destFiles = []
                    for f in filesPerInstruc: # generate files in pack file
                        if len(i.from_as) > 0:
                            filepath = (f.replace(root, i.from_as)).replace("//", "/") # sanitace path
                            destFiles.append(filepath)
                        else:
                            destFiles.append(f.replace(g.root_dir, "")) #TODO: option of create root dir will be here

                    if len(filesPerInstruc) > 0:
                        g.packfiles.append([filesPerInstruc, destFiles])
                else: # it is a file -> insert in global list directly
                    if len(filesPerInstruc) > 0:
                        g.packfiles.append(filesPerInstruc)

            ## IGNORE files -> remove from list of files to add
            elif i.action == g.action_t.ignore:
                for i in range(len(g.packfiles)): #loop over list of list -> item will be a list
                    if len(g.packfiles[i]) > 0:
                        for j in range(len(filesPerInstruc)):
                            for k in range(len(g.packfiles[i][0])): # 0 and 1 will have the same size
                                if g.packfiles[i][0][k] == filesPerInstruc[j]:
                                    del g.packfiles[i][0][k] #delete from src list
                                    del g.packfiles[i][1][k] #delete froms dest list (path in pack file)
    else:
        msg.error("Errors found, skipping pack")

    if msg.g_error == False:
        create_targz(filename)

    # clean data for the new pack
    g.instructions.clear()

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

def create_targz(filename):
    msg.info(colors.darkmagenta + 'Packing "' + filename + colors.off)
    targzfile = g.target_dir + "/" + filename
    if (os.path.isfile(targzfile)):
        os.remove(targzfile)
    tarball = tarfile.open(targzfile, "w:gz")
    numFiles = 0
    for fileList in g.packfiles:
        for i in range(len(fileList[0])):
            numFiles +=1

    currentNumFile = 1
    for fileList in g.packfiles:
        for i in range(len(fileList[0])):
            print("[" + str(currentNumFile) +  "/" + str(numFiles) + "] " + fileList[1][i])
            tarball.add(fileList[0][i], fileList[1][i])
            currentNumFile += 1

    tarball.close()
    msg.ok()


def extract_ZIP(zipfile):
    msg.error("ZIP files not implemented yet")