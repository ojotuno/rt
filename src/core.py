import globals as g
import fileparser
import os
import messages as msg
import utils
import core_funcs as f

def process_rtfile(rtFile, installation):
    if True == installation:
        msg.info("Processing installation recipe..")
    else:
        msg.info("Processing recipe...")
    fileparser.parse(rtFile)

def run_installer(src, dest, ext):
    # 1.decompres in dest or current dir
    dir = ""
    if len(dest) != 0:
        dir = os.path.abspath(dest)
        dir = utils.rm_backslah_from_path(dir)
    else:
        dir = os.getcwd() #current working directory

    # 3. unpack into dir
    if ext in [".rt", ".tar.gz"]:
        f.extract_TAR(src, dir)
    else:
        f.extract_ZIP(src, dir) #TODO: not implemented yet

    install_foudn = False
    install_path = ""
    for currrentDir, dirname, files in os.walk(dir):
        if g.install_file in files:
            install_foudn = True
            install_path = currrentDir
            break

    # check if "install" filename exist
    if install_foudn:
        process_rtfile(install_path + "/" + g.install_file, True) # from install = True
    else:
        msg.warning("Installation recipe not found.")    