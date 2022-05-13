import colors as c
import sys

rt = "[rt] "
rt_out = "[rt-out] "

def info(msg, endl = '\n'):
  print(rt + msg, end= endl)
  sys.stdout.flush()

def done():
  print(rt + c.green + "Done!" + c.off)
  sys.stdout.flush()

def append_ok():
  print(c.green + " [OK]" + c.off)
  sys.stdout.flush()

def ok():
  print(rt + c.green + "[OK]" + c.off)
  sys.stdout.flush()

def error(msg):
  print(rt + c.red + "Error: " + msg + c.off)
  sys.stdout.flush()

def syntax_error(lineNun, msg):
  print(rt + c.red + "Syntax error in line " + str(lineNun) + ": " + msg + c.off)
  sys.stdout.flush()

def warning(msg):
  print(rt + c.yellow + "Warning: " + msg + c.off)
  sys.stdout.flush()

def debug(msg):
  print("-- DEBUG -- " + msg)
  sys.stdout.flush()

def print_recipe_msg(msg):
  print(rt_out + msg)
  sys.stdout.flush()
