import sys
import info
import core
import utils
import messages as msg
import os

# RT entry point
if __name__ == "__main__":
  nargs = len(sys.argv)
  utils.set_origin_workingdir(os.getcwd())

  if nargs == 2:
    arg = sys.argv[1]
    if arg == "-update":
      update_url = "https://github.com/ojotuno/rt/releases/download/lastest/rt.rt"
      core.download_and_run_file(update_url)
    else:
      core.run_rt(sys.argv[1])
  elif nargs == 3:
    arg = sys.argv[1]
    if arg == "-url":
      core.download_and_run_file(sys.argv[2])
    elif arg == "-show":
      msg.warning("TODO: show rt package content ")
  else:
    info.show_info()

  