from ctypes import util
from email import utils
import colors as color
import os
import subprocess
import globals as g
import core_funcs as f
import messages as msg
import utils
import env_var as env

kw = g.Keywords()

def parse_add_path(tokens):
    return ""

def parse_add_file(tokens):
    return ""

def parse_add_ext(tokens):
    return ""

def parse_ignore_path(tokens):
    return ""

def parse_ignore_file(tokens):
    return ""

def parse_ignore_ext(tokens):
    return ""
    
def parse_root_dir(tokens):
    if len(tokens) == 2:
        value = resolve_url(tokens[1]) # could be a path, a envvar, env var+paths, aliases and all can be mixted
        f.set_root_dir(value) # root_dir value
    else:
        msg.error("root_dir only acepts one value")

def parse_target_dir(tokens):
    return ""

def parse_pack(tokens):
    return ""

def parse_run_cmd(tokens):
    command = utils.concat_tokens(tokens[1:])
    #msg.info("Executing command: " + color.blue + command + color.off)
    #msg.flush()
    try:
        p = subprocess.run(command, shell=True, check=True, universal_newlines=True)
        msg.info("Returned code " + str(p.returncode))
    except subprocess.CalledProcessError as e:
        msg.info("Returned code " + str(e.returncode))

def parse_print(tokens):
    message = utils.concat_tokens(tokens[1:])
    print(message)

def parse_arguments(tokens):
    return ""

def parse_git(tokens):
    command = utils.concat_tokens(tokens)
    try:
        p = subprocess.run(command, shell=True, check=True, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        msg.info("Returned code " + str(e.returncode))

def parse_svn(tokens):
    return ""

def parse_aliases(tokens, lineNum):
    #check if alias 
    # else syntax error
    msg.syntax_error(lineNum, utils.concat_tokens(tokens))

def resolve_url(url):
    if url[0] == "$":
        arg = url.split("/")
        solvedPath = ""
        for token in arg:
            if token[0] == "$":
                envVar = token[1:]
                solvedPath = solvedPath + env.get(envVar)
            else:
                solvedPath = solvedPath + "/" + token
        return solvedPath
    else:
        return url

# TODO: change it to make only a syntaxic analisys
def parseLine(line, lineNum):
  # tokenize
    tokens = line.split()
    nTokens = len(tokens)
    if nTokens == 0:
        pass
    else:
        if kw.comment == tokens[0][0]:
            pass
        else:
            keyword = tokens[0]
            if keyword == kw.add_path:
                parse_add_path(tokens)
            elif keyword == kw.add_file:
                parse_add_file(tokens)
            elif keyword == kw.add_ext:
                parse_add_ext(tokens)
            elif keyword == kw.ignore_path:
                parse_ignore_path(tokens)
            elif keyword == kw.ignore_file:
                parse_ignore_file(tokens)
            elif keyword == kw.ignore_ext:
                parse_ignore_ext(tokens)
            elif keyword == kw.root_dir:
                parse_root_dir(tokens)
            elif keyword == kw.target_dir:
                parse_target_dir(tokens)
            elif keyword == kw.pack: 
                parse_pack(tokens)
            elif keyword == kw.run_cmd:
                parse_run_cmd(tokens)
            elif keyword == kw.print:
                parse_print(tokens)
            elif keyword == kw.arguments:
                parse_arguments(tokens)
            elif keyword == kw.git:
                parse_git(tokens)
            elif keyword == kw.svn:
                parse_svn(tokens)
            else:
                parse_aliases(tokens, lineNum)

def parse(filename):

    if os.path.exists(filename) == True:
        file = open(filename)
        lineNum = 0

        # read recepie file
        for line in file:
            lineNum = lineNum + 1
            parseLine(line, lineNum)

        file.close()
    else:
        msg.error(filename + " not found.")
