from ctypes import util
from email import utils
import colors as color
import os
import globals as g
import core_funcs as f
import messages as msg
import utils

kw = g.Keywords()

def parseLine(line, lineNum):
    tokens = f.tokenize(line, lineNum)
    nTokens = len(tokens)
    if nTokens == 0:
        pass
    else:
        keyword = tokens[0]
        if keyword == kw.add_path:
            parse_add_path(tokens, lineNum)
        elif keyword == kw.add_file:
            parse_add_file(tokens, lineNum)
        elif keyword == kw.add_ext:
            parse_add_ext(tokens, False, lineNum)
        elif keyword == kw.add_ext_recursive:
            parse_add_ext(tokens, True, lineNum)
        elif keyword == kw.ignore_path:
            parse_ignore_path(tokens, lineNum)
        elif keyword == kw.ignore_file:
            parse_ignore_file(tokens, lineNum)
        elif keyword == kw.ignore_ext:
            parse_ignore_ext(tokens, lineNum)
        elif keyword == kw.root_dir:
            parse_root_dir(tokens, lineNum)
        elif keyword == kw.target_dir:
            parse_target_dir(tokens, lineNum)
        elif keyword == kw.pack:
            parse_pack(tokens, lineNum)
        elif keyword == kw.run_cmd:
            parse_run_cmd(tokens)
        elif keyword == kw.print:
            parse_print(tokens)
        elif keyword == kw.git:
            parse_git(tokens, lineNum)
        elif keyword == kw.svn:
            parse_svn(tokens, lineNum)
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

## Actions ##
## Actions cannot be executed if there are syntax errors
def parse_pack(tokens):
    if msg.g_error == False:
        return ""

def parse_print(tokens):
    if msg.g_error == False:
        message = utils.concat_tokens(tokens[1:])
        f.print_str(message)


def parse_git(tokens):
    if msg.g_error == False:
        command = utils.concat_tokens(tokens)
        f.run_cmd(command)


def parse_svn(tokens):
    if msg.g_error == False:
        command = utils.concat_tokens(tokens)
        f.run_cmd(command)


def parse_run_cmd(tokens):
    if msg.g_error == False:
        command = utils.concat_tokens(tokens[1:])
        f.run_cmd(command)


## Instructions ##
def parse_add_path(tokens, lineNum):
    numTokens = len(tokens)
    if numTokens == 2:
        f.add_path(tokens[1], "")
    elif numTokens == 3:
        f.add_path(tokens[1], tokens[2])
    else:
        return msg.syntax_error(lineNum, "add_path takes 2 o 3 arguments")


def parse_add_file(tokens, lineNum):
    numTokens = len(tokens)
    if numTokens == 2:
        f.add_file(tokens[1], "")
    elif numTokens == 3:
        f.add_file(tokens[1], tokens[2])
    else:
        return msg.syntax_error(lineNum, "add_path takes 2 o 3 arguments")


def parse_add_ext(tokens, recursive, lineNum):
    numTokens = len(tokens)
    if numTokens >= 2:
        for token in tokens[1:]:
            if "/" in token:
                path, ext = utils.split_path_and_ext(token)
                f.add_ext(path, ext, recursive)  # recursive false
            else:
                f.add_ext(".", token, recursive)  # recursive False
    else:
        return msg.syntax_error(lineNum, "add_path takes at least 2 arguments")


def parse_ignore_path(tokens, lineNum):
    numTokens = len(tokens)
    if numTokens == 2:
        f.ignore_path(tokens[1])
    else:
        return msg.syntax_error(lineNum, "ignore_path takes just 2 arguments")


def parse_ignore_file(tokens, lineNum):
    numTokens = len(tokens)
    if numTokens == 2:
        f.ignore_file(tokens[1])
    else:
        return msg.syntax_error(lineNum, "ignore_path takes just 2 arguments")


def parse_ignore_ext(tokens, lineNum):
    numTokens = len(tokens)
    if numTokens == 2:
        f.ignore_ext(tokens[1])
    else:
        return msg.syntax_error(lineNum, "ignore_path takes just 2 arguments")


def parse_root_dir(tokens):
    if len(tokens) == 2:
        if "*" not in tokens[1]:
            f.set_root_dir(utils.resolve(tokens[1]))  # root_dir value
        else:
            msg.syntax_error("root_dir cannot conatins * in the path")
    else:
        msg.syntax_error("root_dir only accepts one value")


def parse_target_dir(tokens):
    if len(tokens) == 2:
        if "*" not in tokens[1]:
            f.set_target_dir(utils.resolve(tokens[1]))  # root_dir value
        else:
            msg.syntax_error("target_dir cannot conatins * in the path")
    else:
        msg.syntax_error("target_dir only accepts one value")

def parse_aliases(tokens, lineNum):
    # check if alias
    # else syntax error
    msg.syntax_error(lineNum, "parse_aliases " + utils.concat_tokens(tokens))



