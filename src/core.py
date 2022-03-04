import globals as g
import parser
import os
import tarfile

def run_packer(rtFile):
    parser.parse(rtFile)

def run_installer(src, dest):
    dir = ""
    if len(dest) != 0:
        dir = dest
    else:
        dir = os.getcwd() #current working directory

    # TODO
    pckg = tarfile.open(src, "r:gz")
    # unpack into dir
    # check if install file exist
