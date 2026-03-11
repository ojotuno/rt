import sys
import info
import core
import utils
import os

# RT entry point
if __name__ == "__main__":
  nargs = len(sys.argv) - 1
  utils.set_origin_workingdir(os.getcwd())

  if nargs == 0:
    info.show_info()
    exit(0)

  if nargs == 1:
    arg = sys.argv[1]
    if arg == "-update":
      update_url = "https://github.com/ojotuno/rt/releases/download/lastest/rt.rt"
      core.download_and_run_file(update_url)
    else:
      core.run_rt(sys.argv[1])
  elif nargs == 2:
    arg = sys.argv[1] # first argument
    if arg == "-url":
      core.download_and_run_file(sys.argv[2]) # second argument is url
    elif arg == "-show":
      core.show_content(sys.argv[2])
    else:
      core.run_rt(sys.argv[1]) # run with args
  else:
    core.run_rt(sys.argv[1]) # run with args

  