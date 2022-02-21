import colors
import globals as g

def run(rtFile):
    while 1:
        instruction = parser.parseLine(rtFile)
        if instruction.type == Ins.Runnable:
            #Run instructions (create/write files, run console commands, )
        elif instruction.isPack == Ins.Pack:
            # creation of target_file when pack
        else:
            continue


def checkIfEnvironvar(arg):
    if arg[0] == "$":
        arg = arg.split("/")
        solvedPath = ""
        for token in arg:
            if token[0] == "$":
                envVar = token[1:]
                solvedPath = solvedPath + env.get(envVar)
            else:
                solvedPath = solvedPath + "/" + token
        return solvedPath
    else:
        return arg

def parse_next_intruc():
    if nTokens == 0:
        pass
    elif nTokens == 1:
        firstChar = tokens[0][0]
        if firstChar == COMMENT:
            pass
        elif firstChar == SCRIPT_ARG:
            g.arguments.append(tokens[0])
        else:
            print(colors.red + "Config file error:" + colors.off + "command not found. Line:" + str(lineNum) + " " + line)   
    elif nTokens == 2:
        cmd = tokens[0]
        arg = tokens[1]
        arg = checkIfEnvironvar(arg)

        if cmd == ADD_FILE:
            g.files2Add.append(arg)
        elif cmd == ADD_EXT:
            g.ext2Add.append(arg)
        elif cmd == ADD_PATH:
            g.paths2Add.append((arg, ''))
        elif cmd == IGNORE_FILE:
            g.files2ignore.append(arg)
        elif cmd == IGNORE_EXT:
            g.ext2ignore.append(arg)
        elif cmd == IGNORE_PATH:
            g.paths2ignore.append(arg)
        else:
            print(colors.red + "Config file error:" + colors.off + "command not found. Line:" + str(lineNum) + " " + line)    
    elif nTokens == 3:
        keyword = tokens[0]
        if keyword == ROOT_DIR:
            root_dir = checkIfEnvironvar(tokens[2])
        elif keyword == TARGET_DIR:
            target_dir = checkIfEnvironvar(tokens[2])
        elif keyword == TARGET_FILE:
            target_file = checkIfEnvironvar(tokens[2])
        elif keyword == ADD_PATH:
            g.paths2Add.append((checkIfEnvironvar(tokens[1]), tokens[2]))
    else:
        print(colors.red + "Config file error:" + colors.off + " format error. Line:" + str(lineNum) + ' ' + line)
        exit()