import os
import sys
import subprocess
import globals as g
import parserfuncs as pf
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
            g.resolved = False # reset resolved
            parseLine(line, lineNum)

        file.close()
    else:
        msg.error(filename + " not found.")

def parseLine(line, lineNum):
    tokens = pf.tokenize(line, lineNum)
    nTokens = len(tokens)
    if nTokens == 0:
        return
    else:
        keyword = tokens[0]
        #  If it has failed a comparison, we skip processing until we find the end statement that closes the block.
        if g.nested_level_comparison_results_failed > 0:
            if keyword == kw.IF:
                g.nested_level += 1
            elif keyword == kw.END:
                parse_end(tokens, lineNum)
            return 

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
        elif keyword == kw.EXIT:
            parse_exit(tokens, lineNum)
        elif keyword == kw.IF:
            parse_if(tokens, lineNum)
        elif keyword == kw.END:
            parse_end(tokens, lineNum)
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


def invoke_rt(tokens, lineNum):
    if len(tokens) < 2:
        msg.syntax_error("Invalid call to rt. Command: rt [-url] <recipe/rt-file> [args...]", lineNum)
        return

    rt_script = os.path.join(os.path.dirname(__file__), "rt.py")
    cmd = [sys.executable, rt_script] + tokens[1:]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        msg.error("rt call failed with return code " + str(result.returncode), lineNum)

def parse_exit(tokens, lineNum):
    if len(tokens) == 1:
        msg.info("Exit")
        sys.exit(0)
    else:
        msg.syntax_error("exit does not accept arguments", lineNum)

def parse_if(tokens, lineNum):
    if len(tokens) == 4:
        g.nested_level += 1
        operand1 = tokens[1]
        operator = tokens[2]
        operand2 = tokens[3]

        if operator in [g.Operators.EQUAL, g.Operators.NOT_EQUAL, g.Operators.GREATER, g.Operators.LESS, g.Operators.CREATER_EQUAL, g.Operators.LESS_EQUAL]:
            # resolve operands
            operand1 = utils.resolve(operand1, lineNum)
            operand2 = utils.resolve(operand2, lineNum)

            if operand1.isdigit() and operand2.isdigit():
                operand1 = int(operand1)
                operand2 = int(operand2)
            elif operand1.isdigit() and not operand2.isdigit() or \
                 not operand1.isdigit() and operand2.isdigit():
                    msg.syntax_error("Cannot compare a numeric operand with a non-numeric operand", lineNum)
                    return

            # compare operands
            if operator == g.Operators.EQUAL:
                condition = operand1 == operand2
            elif operator == g.Operators.NOT_EQUAL:
                condition = operand1 != operand2
            elif operator == g.Operators.GREATER:
                condition = operand1 > operand2
            elif operator == g.Operators.LESS:
                condition = operand1 < operand2
            elif operator == g.Operators.CREATER_EQUAL:
                condition = operand1 >= operand2
            elif operator == g.Operators.LESS_EQUAL:
                condition = operand1 <= operand2

            if False == condition:
                g.nested_level_comparison_results_failed = g.nested_level
            
        else:
            msg.syntax_error("Invalid operator in if statement", lineNum)

def parse_end(tokens, lineNum):
    if len(tokens) == 1:
        if g.nested_level > 0:
            if g.nested_level == g.nested_level_comparison_results_failed:
                g.nested_level_comparison_results_failed = 0 # reset failed comparison results when the block is closed
            g.nested_level -= 1
        else:
            msg.syntax_error("end statement without a previous if statement", lineNum)
    else:
        msg.syntax_error("end does not accept arguments", lineNum)