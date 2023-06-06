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

def concat_tokens(tokens):
    result = ""
    rexpr = r"\".*\""
    for token in tokens:
        str = re.match(rexpr, token)
        if str is not None:
            result += (str.group())[1:-1]
    return result

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

    for match in matches:
        env_variable = match
        try:
            env_value = env.get(env_variable)
            if env_value:
                path = path.replace(f"$({env_variable})", env_value)
            else:
                msg.error(lineNum, env_variable + " environment variable not found")
            return path
        except:
            msg.error(str(lineNum), "Environment variable in line " + env_variable + " does not exists")
            exit()

def resolve_args(argsStr, lineNum):
    pattern = r'args\[(\d+)\]'
    match = re.search(pattern, argsStr)
    if match:
        index = int(match.group(1))             
        if len(g.arguments) > index:
            return g.arguments[index]
        else:
            msg.error(lineNum, "Argument index out of range")
    
    return argsStr

def split_path_and_ext(token):
    extDot = token.rfind(".")
    path = token[: extDot - 1]
    ext = token[extDot:]
    return path, ext
