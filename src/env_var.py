import os

def set(var, value):
  os.environ[var] = value

def get(var):
  return os.environ[var]