#!/usr/bin/env python

import sys
import info
import core
import utils
import messages as msg
import core_funcs as f

# 
if __name__ == "__main__":
  nargs = len(sys.argv)

  if nargs == 1 or nargs > 3:
    info.show_info()
  else:
    file = sys.argv[1]
    ext = utils.getFullExt(file)
    packageExt = [".rt", ".tar.gz", ".zip"]

    # add all arguments
    f.add_arguments()
    
    if ext not in packageExt:
      rtFile = sys.argv[1]
      core.process_rtfile(rtFile, False) # from installation = False
    else:
      dest = ""
      if nargs == 3:
        dest = sys.argv[2]
      core.run_installer(file, dest, ext);            
    
    if msg.g_error == False:
      msg.done()
    else:
      msg.done_not_ok()