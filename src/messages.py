import colors as c
import sys

rt = "[rt] "

def info(msg, endl = '\n'):
  print(rt + msg, end = endl)

def done():
  print(rt + c.green + "Done!" + c.off)

def append_ok():
  print(c.green + " [OK]" + c.off)

def ok():
  print(rt + c.green + "[OK]" + c.off)

def error(msg):
  print(rt + c.red + "Error: " + msg + c.off)

def syntax_error(lineNun, msg):
  print(rt + c.red + "Syntax error in line " + str(lineNun) + ": " + msg + c.off)

def warning(msg):
  print(rt + c.yellow + "Warning: " + msg + c.off)

def debug(msg):
  print("-- DEBUG -- " + msg)

def flush():
  sys.stdout.flush()