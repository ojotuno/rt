import colors as color
import os
import globals as g
import funcs as f

kw = g.Keywords()

def parser_error(str):
    print(color.darkred + "Syntax error: " + str + color.off);

def parser_warning(str):
    print(color.yellow + "Warning: " + str + color.off)

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
        parser_error("root_dir only acepts one value");

def parse_target_dir(tokens):
    return ""

def parse_pack(tokens):
    return ""

def parse_run_cmd(tokens):
    return ""

def parse_print(tokens):
    return ""

def parse_arguments(tokens):
    return ""

def parse_git(tokens):
    return ""

def parse_svn(tokens):
    return ""

def parse_aliases(tokens):
    return ""

def resolve_url(url):
    return ""

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
        else :
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
                parse_aliases(tokens)

def parser(filename):
    if os.path.exists(filename) == True:
        file = open(filename)
        lineNum = 0
        for line in file:
            lineNum = lineNum + 1
            parseLine(line, lineNum)
        file.close()

        check_script_aguments()
    else:
        parser_error(filename + " not found.")
