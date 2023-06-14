import sys
import info
import core
import utils
import messages as msg
import parserfuncs as pf
import urlget
import os

def run_rt(rtfile):
  # add all arguments
  pf.add_arguments()

  ext = utils.getFullExt(rtfile)
  
  if ext not in [".rt", ".tar.gz", ".zip"]:
    core.process_rtfile(rtfile, False) # try to precess install recipe
  else:
    dest = ""
    if nargs == 3:
      dest = sys.argv[2]
    core.run_installer(rtfile, dest, ext);            
  
  if msg.g_error == False:
    msg.done()
  else:
    msg.done_not_ok()

# RT entry point
if __name__ == "__main__":
  nargs = len(sys.argv)

  if nargs == 1:
    info.show_info()
  elif nargs == 3 and sys.argv[1] == "-url":
    filename = urlget.download_file(sys.argv[2])
    msg.append_ok()
    run_rt(filename)
    if os.path.exists(filename):
      os.remove(filename)
    else:
      msg.error("Cannot remove temporary file", 0)
  else:
    run_rt(sys.argv[1])
  
 
