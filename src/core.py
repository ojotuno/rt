import globals as g
import rtparser
import os
import messages as msg
import utils
import parserfuncs as pf
import sys
import wget

class RT_MODE:
   Default = 0
   Install = 1
   Call = 2

def run_rt(rtfile, url=False):
  # add all arguments
  pf.add_arguments()

  ext = utils.getFullExt(rtfile)
  
  if ext not in [".rt", ".tar.gz", ".zip"]:
    process_rtfile(rtfile, RT_MODE.Default) # try to precess install recipe
  else:
    dest = ""
    if len(sys.argv) == 3 and url == False:
      dest = sys.argv[2]
    else:
      dest = os.getcwd()
    run_installer(rtfile, dest, ext);            
  
  if msg.g_error == False:
    msg.done()
  else:
    msg.done_not_ok()

def download_and_run_file(url):
    currentDir = os.getcwd()
    [filename, tmpDir] = wget.download(url)
    if filename != "":
      run_rt(filename, url=True)
    os.chdir(currentDir)
    utils.removeTmpDir(tmpDir)

def process_rtfile(rtFile, mode:RT_MODE):
    if mode == RT_MODE.Default:
        msg.info("Processing recipe..")
    elif mode == RT_MODE.Install:
        msg.info("Processing installation recipe..")
    elif mode== RT_MODE.Call:
        msg.info("Calling to " + rtFile)
    rtparser.parse(rtFile)

def run_installer(src, dest, ext):
    # 1.decompres in dest or current dir
    dir = ""
    decrompressInTmpDir = len(dest) != 0
    if decrompressInTmpDir:
        dir = os.path.abspath(dest)
        dir = utils.rm_backslah_from_path(dir)
    else:
        dir = os.getcwd() #current working directory

    # 3. unpack into dir
    if ext in [".rt", ".tar.gz"]:
        pf.extract_TAR(src, dir)
    else:
        pf.extract_ZIP(src, dir) #TODO: not implemented yet

    install_found = False
    install_path = ""
    for currrentDir, dirname, files in os.walk(dir):
        if g.install_file in files:
            install_found = True
            install_path = currrentDir
            break

    # check if "install" filename exist
    if install_found:
        if decrompressInTmpDir:
          currentDir = os.getcwd()
          os.chdir(dir)
          process_rtfile(install_path + "/" + g.install_file, RT_MODE.Install) # from install = True
          os.chdir(currentDir)
        else:
          process_rtfile(install_path + "/" + g.install_file, RT_MODE.Install) # from install = True
    else:
        msg.warning("Installation recipe not found.")    
