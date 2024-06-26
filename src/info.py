import colors
import buildnum

def show_logo():                                                                                                                                
  print(colors.green + """
 .----------------.  .----------------. 
| .--------------. || .--------------. |
| |  _______     | || |  _________   | |
| | |_   __ \    | || | |  _   _  |  | |
| |   | |__) |   | || | |_/ | | \_|  | |
| |   |  __ /    | || |     | |      | |
| |  _| |  \ \_  | || |    _| |_     | |
| | |____| |___| | || |   |_____|    | |
| |              | || |              | |
| '--------------' || '--------------' |
 '----------------'  '----------------' 
 """)
  print(colors.red + " Build number: " + buildnum.num + colors.off)
                                                              
def show_info():
  show_logo()

  print(colors.off + " ")
  print(colors.off + "Usage:")
  print(colors.off + "---------- ")
  print(colors.off + "rt RECIPE_FILE ")
  print(colors.off + "rt RTFILE.[rt, tar.gz, zip] [DEST]* ")
  print(colors.off + "rt -url [url]")
  print(colors.off + "rt -update")
  print(colors.off + "---------- ")
  print(colors.off + "Every line has to be formed by " + colors.blue + "keyword " + colors.yellow + "argument")
  print(colors.off + "Keywords: root_dir, target_dir, add, ignore, print, args, git, svn")
  print(colors.off + "Arguments: path/patterns/file/extension/evinronment variable with inside of the expresion $() ")
  print(colors.off + "")
  print(colors.blue + "root_dir _path_ as root_dir_in_path ")
  print(colors.off + "Indicates the root directory _path_ where start to walk. Can be changed at any point of the recipe. Instructions are related to this root. The root_dir_in_path indicates the path in the package where stating to include the files, if not used, the files will be inserted exacly as the root_dir indicates.")
  print(colors.off + " ")
  print(colors.blue + "target_dir _path_ ")
  print(colors.off + "Indicates the target directory (*\_path\_*) where the pckg will be generated. It is mandatory and has to be declared before calling pack.")
  print(colors.off + "")
  print(colors.blue + "add [file/path] (as [name])*")
  print(colors.blue + "add [file/path] (in [path])*")
  print(colors.off + "Adds a file/path into the package. If used [as] replace the file/path into the package with the name indicated in [name]. If used [in] inserts the file/path in the package inside the directory indicated into the package [path]")
  print(colors.off + "")
  print(colors.blue + "ignore [_pattern_] from [_path_]*")
  print(colors.off + "Ignores the pattern from being inserted in the package. The [from path] is optional, if used goes to the ignore applies to the _path_ indicated. if not used the default path is the root_dir.")
  print(colors.off + "")
  print(colors.blue + "rt -url <recipe/rt-file>")
  print(colors.off + "-url indicates that the recipe/rt-file has to be downloaded first from the url to be processed")
  print(colors.off + "Calls the recipe or the rt file and execute it")
  print(colors.off + "")
  print(colors.blue + "pack FILENAME -rootdir DIR -mock")
  print(colors.off + "-rootdir includes the DIR as the root dic in the package file")
  print(colors.off + "-mock  Mocks the packing, i, e, it does not pack and shows the files to be included")
  print(colors.off + "Starts packing into *\_filename\_* all the files and folders according the instructions given before this call.")
  print(colors.off + "")
  print(colors.blue + "print \"_str_\" ...")
  print(colors.off + "Prints out the *\_str\_*. To concatenate strings uses spaces.")
  print(colors.off + "")
  print(colors.blue + "args`")
  print(colors.off + "The \"args\" keyword contains the value of the arguments being the first position the first argument, not the name of the binary.")
  print(colors.off + "")
  print(colors.blue + "$(ENV)")
  print(colors.off + "Get the value of the environmente variable ENV")