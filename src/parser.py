import colors
import os

# Constants (keywords)
ADD_PATH = 'add_path'
ADD_FILE = 'add_file'
ADD_EXT = 'add_ext'
IGNORE_PATH = 'ignore_path'
IGNORE_FILE = 'ignore_file'
IGNORE_EXT = 'ignore_ext'
ROOT_DIR = "root_dir" #mandatory
TARGET_DIR = "target_dir" #mandatory
TARGET_FILE = "target_file" #mandatory
PACK_TARGET_FILE = "pack" #mandatory (meanwhile install does not exist)
INSTALL_TARGET_FILE = "install" # TODO
CREATE_FILE = "create_file"
WRITE_FILE = "write_file"
RUN_CONSOLE_CMD = ">"
SCRIPT_ARG = "*"
COMMENT = '#'


# TODO: change it to make only a syntaxic analisys
def parseLine(line, lineNum):
  # tokenize
    tokens = line.split()
    nTokens = len(tokens)
    if nTokens == 0:
        pass
    else:
        firstChar = tokens[0][0]
        if firstChar == COMMENT:
            pass
        elif firstChar == RUN_CONSOLE_CMD:
            # check console cmd
        elif firstChar == SCRIPT_ARG:
            #store script arg
    
def syntax_analysis(filename):
    if os.path.exists(filename) == True:
        file = open(filename)
        lineNum = 0
        for line in file:
            lineNum = lineNum + 1
            parseLine(line, lineNum)
        file.close()

        check_script_aguments()
    else:
        print(colors.darkred + "ERROR: " + filename + " not found." + colors.off)