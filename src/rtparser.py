import os
import sys
import globals as g
import parserfuncs as pf
import messages as msg
import utils
import wget


kw = g.Keywords()

def parse(filename):
    if os.path.exists(filename) == True:
        file = open(filename)
        lineNum = 0
        # read recepie file
        for line in file:
            lineNum = lineNum + 1
            g.resolved = False # reset resolved
            parseLine(line, lineNum)

        file.close()
    else:
        msg.error(filename + " not found.")

def parseLine(line, lineNum):
    tokens = pf.tokenize(line, lineNum)
    nTokens = len(tokens)
    if nTokens == 0:
        pass
    else:
        keyword = tokens[0]
        if keyword == kw.ADD:
            parse_add(tokens, lineNum)
        elif keyword == kw.IGNORE:
            parse_ignore(tokens, lineNum)
        elif keyword == kw.ROOT_DIR:
            parse_root_dir(tokens, lineNum)
        elif keyword == kw.TARGET_DIR:
            parse_target_dir(tokens, lineNum)
        elif keyword == kw.PACK:
            parse_pack(tokens, lineNum)
        elif keyword == kw.RUN_CMD:
            parse_run_cmd(tokens)
        elif keyword == kw.PRINT:
            parse_print(tokens)
        elif keyword == kw.GIT:
            parse_git(tokens, lineNum)
        elif keyword == kw.SVN:
            parse_svn(tokens, lineNum)
        elif keyword == kw.PACK:
            parse_pack(tokens, lineNum)
        elif keyword == kw.RT:
            invoke_rt(tokens, lineNum)
        else:
            msg.syntax_error("Keyword not recognised", lineNum)

######################## Actions ########################
def parse_pack(tokens, lineNum):
    if msg.g_error == False:
        if len(tokens) == 2:
            pf.pack(tokens[1], lineNum)
        else:
            msg.syntax_error("pack only gets one argument", lineNum)

def parse_print(tokens):
    if msg.g_error == False:
        message = utils.concat_tokens(tokens[1:])
        pf.print_str(message)


def parse_git(tokens):
    if msg.g_error == False:
        command = utils.create_command(tokens)
        pf.run_cmd(command)


def parse_svn(tokens):
    if msg.g_error == False:
        command = utils.create_command(tokens)
        pf.run_cmd(command)


def parse_run_cmd(tokens):
    if msg.g_error == False:
        command = utils.create_command(tokens[1:])
        pf.run_cmd(command)


###################### Instructions ######################
def parse_add(tokens, lineNum):
    numTokens = len(tokens)
    if numTokens == 2:
        if utils.check_add_statement(tokens[1], "", lineNum):
            pf.append_instruction(g.action_t.add, tokens[1], lineNum=lineNum)
    elif numTokens == 4 and (tokens[2] == kw.AS or tokens[2] == kw.IN):
        if utils.check_add_statement(tokens[1], tokens[3], lineNum):
            pf.append_instruction(g.action_t.add, tokens[1], tokens[2], tokens[3], lineNum)
    else:
        return msg.syntax_error("The syntax of add isntruciton is: add PATH [as PATH]* ",lineNum)

def parse_ignore(tokens, lineNum):
    numTokens = len(tokens)
    if numTokens == 2:
        if utils.check_ignore_statement(tokens[1], "", lineNum):
            pf.append_instruction(g.action_t.ignore, tokens[1], lineNum=lineNum)
    elif numTokens == 4 and tokens[2] == kw.FROM:
        if utils.check_ignore_statement(tokens[1], tokens[3], lineNum):
            pf.append_instruction(g.action_t.ignore, tokens[1], "", tokens[3], lineNum)
    else:
        return msg.syntax_error("The syntax of ignore isntruciton is: ignore PATH [from PATH]* ", lineNum)

def parse_root_dir(tokens, lineNum):
    if len(tokens) == 2:
        if "*" not in tokens[1]:
            pf.set_root_dir(utils.resolve(tokens[1], lineNum), lineNum)  # root_dir value
        else:
            msg.syntax_error("root_dir cannot conatins wildcards(*) in the path", lineNum)
    else:
        msg.syntax_error("root_dir only accepts one value", lineNum, )


def parse_target_dir(tokens, lineNum):
    if len(tokens) == 2:
        if "*" not in tokens[1]:
            pf.set_target_dir(utils.resolve(tokens[1], lineNum), lineNum)  # root_dir value
        else:
            msg.syntax_error("target_dir cannot conatins wildcards (*) in the path", lineNum)
    else:
        msg.syntax_error("target_dir only accepts one value", lineNum)


import core
import shutil

def invoke_rt(tokens, lineNum):
    if len(tokens) in [2,3]:
        def invoke_rt(ext, rtfile, remove=False):
            if ext not in [".rt", ".tar.gz", ".zip"]:
                core.process_rtfile(rtfile, core.RT_MODE.Call) # try to precess install recipe
                if remove:
                    os.remove(rtfile)
            else:
                msg.debug("rt file")
                tmpDir = utils.createTmpDir()
                print("created tmp dir")
                currentDir = os.getcwd()
                print("Current working dir = " + currentDir)
                # os.chdir(tmpDir)
                # print("Entered in " + os.getcwd())
                print("Running installer...")
                core.run_installer(rtfile, tmpDir, ext);      
                utils.removeTmpDir(tmpDir)

        #execute rt
        rtfile = ""
        remove = False
        if len(tokens) == 3 and tokens[1] == "-url":
            rtfile = wget.download(tokens[2])
            remove = True
        elif len(tokens) == 2:
            rtfile = tokens[1]
        else:
            msg.syntax_error("Invalind call to rt. Command: rt -url(optional) <recipe/rt-file>", lineNum)
            
        invoke_rt(utils.getFullExt(rtfile), rtfile, remove)
    else:
        msg.syntax_error("Invalind call to rt. Command: rt -url(optional) <recipe/rt-file>", lineNum)