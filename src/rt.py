#!/usr/bin/env python3

import sys
import info
import parser
import core

if __name__ == "__main__":
  nargs = len(sys.argv)

  if nargs == 1:
    info.show_info()
  else:
    rtFile = sys.argv[1]
    core.run(rtFile);