import colors as c
import sys

rt = "[rt] "
rt_debug = "[rt-debug] "
# global var to check error
g_error = False
g_counter = 0

def check_errors():
    return g_error


def info(msg, endl="\n"):
    print(rt + msg, end=endl)
    sys.stdout.flush()


def done():
    print(rt + c.green + "Done!" + c.off)
    sys.stdout.flush()


def done_not_ok():
    print(rt + c.yellow + "Finished with " + str(g_counter) + " errors" + c.off)
    sys.stdout.flush()


def append_ok():
    print(c.green + " [OK]" + c.off)
    sys.stdout.flush()


def ok():
    print(rt + c.green + "[OK]" + c.off)
    sys.stdout.flush()


def error(lineNun, msg):
    print(rt + c.red + "Error in line " + str(lineNun) + ": " + msg + c.off)
    global g_error
    global g_counter
    g_error = True
    g_counter += 1
    sys.stdout.flush()


def syntax_error(lineNun, msg):
    print(rt + c.red + "Syntax error in line " + str(lineNun) + ": " + msg + c.off)
    global g_error
    global g_counter
    g_error = True
    g_counter += 1
    sys.stdout.flush()


def warning(msg):
    print(rt + c.yellow + "Warning: " + msg + c.off)
    sys.stdout.flush()


def debug(msg):
    print(rt_debug)
    print(msg)
    sys.stdout.flush()


def print_recipe_msg(msg):
    print(msg)
    sys.stdout.flush()
