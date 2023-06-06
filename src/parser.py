import os
import globals as g
import core_funcs as cf
import messages as msg
import utils

kw = g.Keywords()

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

def parseLine(line, lineNum):
    tokens = cf.tokenize(line, lineNum)
    nTokens = len(tokens)
    if nTokens == 0:
        pass
    else:
        keyword = tokens[0]
        if keyword == kw.add:
            parse_add(tokens, lineNum)
        elif keyword == kw.ignore:
            parse_ignore(tokens, lineNum)
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
            msg.syntax_error(lineNum, "Keyword not recognised")


######################## Actions ########################
def parse_pack(tokens, lineNum):
    if msg.g_error == False:
        if len(tokens) == 2:
            cf.pack(tokens, lineNum)
        else:
            msg.syntax_error(lineNum, "pack only gets one argument")

def parse_print(tokens):
    if msg.g_error == False:
        message = utils.concat_tokens(tokens[1:])
        cf.print_str(message)


def parse_git(tokens):
    if msg.g_error == False:
        command = utils.concat_tokens(tokens)
        cf.run_cmd(command)


def parse_svn(tokens):
    if msg.g_error == False:
        command = utils.concat_tokens(tokens)
        cf.run_cmd(command)


def parse_run_cmd(tokens):
    if msg.g_error == False:
        command = utils.concat_tokens(tokens[1:])
        cf.run_cmd(command)


###################### Instructions ######################
def parse_add(tokens, lineNum):
    numTokens = len(tokens)
    if numTokens == 2:
        f.add_path(tokens[1], "")
    elif numTokens == 3:
        f.add_path(tokens[1], tokens[2])
    else:
        return msg.syntax_error(lineNum, "add_path takes 2 o 3 arguments")

def parse_ignore(tokens, lineNum):
    numTokens = len(tokens)
    if numTokens == 2:
        f.ignore_file(tokens[1])
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

