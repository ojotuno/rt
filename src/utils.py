import env_var as env
import re  # regular expresions
import messages as msg
import globals as g

def getFullExt(str):
    index = str.find(".")
    return str[index:]

def rm_backslah_from_path(path):
    szPath = len(path)

    if path[szPath - 1] == "/":
        return path[: szPath - 1]
    else:
        return path
    
def set_origin_workingdir(path):
    g.original_workingdir = path

def concat_tokens(tokens):
    result = ""
    rexpr = r"\".*\""
    for token in tokens:
        str = re.match(rexpr, token)
        if str is not None:
            result += (str.group())[1:-1]
    return result

def create_command(tokens):
    command = ""
    for token in tokens:
        command += token + " "
    return command

def resolve(str, lineNum):
    value = ""
    if "$" in str:
        value = resolve_env_vars(str, lineNum)
    else:
        value = str
    
    return resolve_args(value, lineNum)

# resolve a environments vars inside of "$()"" expresion like $(HOME)/$(USER)/dev/projects
def resolve_env_vars(path, lineNum):
    pattern = r"\$\((\w+)\)"
    matches = re.findall(pattern, path)

    if len(matches) == 0:
        msg.syntax_error("Environment variable not well formed", lineNum)
        return path
    else:
        for match in matches:
            env_variable = match
            try:
                env_value = env.get(env_variable)
                if env_value:
                    path = path.replace(f"$({env_variable})", env_value)
                else:
                    msg.error(env_variable + " environment variable not found", lineNum)
                return path
            except:
                msg.error("Environment variable in line " + env_variable + " does not exists", lineNum)

def resolve_args(argsStr, lineNum):
    pattern = r"args\[(\d+)\]"
    match = re.search(pattern, argsStr)
    if match is not None:
        index = int(match.group(1))             
        if len(g.arguments) > index:
            return g.arguments[index]
        else:
            msg.error("Argument index out of range", lineNum)
    
    return argsStr

def using_wildcards(path):
    return '*' in path

def split_path_and_ext(token):
    extDot = token.rfind(".")
    path = token[: extDot - 1]
    ext = token[extDot:]
    return path, ext

import re

def isdir(path):
    begin = ["./", "/", "//", "../"]
    for item in begin:
        if item in path:
            return True
    return False

def get_filename_from_path(path):
    pos = path.rfind("/")
    if pos >= 0:
        return path[pos +1:] # /....../file
    else:
        return path # a file with no path (install.sh for example)


def check_add_statement(val1, val2, lineNum):
    # val1 has to be a file or a directory
    # val2 has to be a file or a absolute path
    # if (isdir(val1)):
    #     # if len(val2) > 0 :
    #     #     if not p.isabs(val2):
    #     #         msg.syntax_error("ADD value is directory but AS value is a file",lineNum)
    #     #         return False
    #     #     elif val2[0] is not "/": #is relative
    #     #         msg.syntax_error("AS value cannot be a relative directory", lineNum)
    #     #         return False
    #     return True
    # else: 
    #     if len(val2) > 0 and isdir(val2):
    #         msg.syntax_error("Add value is a file but AS value is a directory", lineNum)
    #         return False
        
    return True

def check_ignore_statement(val1, val2, lineNum):
    # val1 has to be file or directory
    # val2 has to be always a valid path
    if len(val2) > 0 and not isdir(val2):
            msg.syntax_error("From value has to be a valid directory", lineNum)
            return False
    return True