#!/usr/bin/env python3

from heapq import nlargest
import sys
import info
import core

if __name__ == "__main__":
  nargs = len(sys.argv)

  if nargs == 1 | nargs > 3:
    info.show_info()
  else:
    if (nargs == 2):
      rtFile = sys.argv[1]
      core.run_packer(rtFile);
    else:
      src = sys.argv[1]
      dest = sys.argv[2]
      core.run_installer(src, dest);            