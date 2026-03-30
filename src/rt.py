import sys
import info
import core
import utils
import os
from globals import Arguments
import messages as msg

# RT entry point
if __name__ == "__main__":
  nargs = len(sys.argv) - 1
  utils.set_origin_workingdir(os.getcwd())

  if nargs == 0:
    info.show_info()
    exit(0)

  if nargs == 1:
    arg = sys.argv[1]
    if arg == Arguments.UPDATE:
      update_url = "https://github.com/ojotuno/rt/releases/download/lastest/rt.rt"
      core.download_and_run_file(update_url)
    elif arg == Arguments.SHOW:
      msg.error("The " + Arguments.SHOW + " argument requires a second argument with the path of the recipe to show") 
    elif arg == Arguments.URL:
      msg.error("The " + Arguments.URL + " argument requires a second argument")
    else:
      core.run_rt(sys.argv[1])
  elif nargs == 2:
    arg = sys.argv[1] # first argument
    if arg == Arguments.URL:
      core.download_and_run_file(sys.argv[2]) # second argument is url
    elif arg == Arguments.SHOW:
      core.show_content(sys.argv[2])
    elif arg == Arguments.UPDATE:
      msg.error("The " + Arguments.UPDATE + " argument does not accept a second argument")
    else:
      core.run_rt(sys.argv[1]) # run with args
  else:
    core.run_rt(sys.argv[1]) # run with args

  