#!/usr/bin/env python3

import sys
import info
import core
import utils
import messages as msg

# 
if __name__ == "__main__":
  nargs = len(sys.argv)

  if nargs == 1 or nargs > 3:
    info.show_info()
  else:
    file = sys.argv[1]
    ext = utils.getFullExt(file)
    packageExt = [".rt", ".tar.gz", ".zip"]

    if ext not in packageExt:
      rtFile = sys.argv[1]
      core.run_rtfile_processor(rtFile, False) # from installation = False
    else:
      dest = ""
      if nargs == 3:
        dest = sys.argv[2]
      core.run_installer(file, dest, ext);            
    
    msg.done()