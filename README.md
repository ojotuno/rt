# RT - Recipe Tool

## Description

RT is a packing tool to bundle, check and install applications and dependencies. 

It designed to be extremely easy and basic to use. 

**Increase the power with scipt calls**
**No configuration needed, just python**

## Usage
Everything you need is a recipe file to give intructions about what you want to do.
When calling RT with and .rt, .tar.gz or .zip file as argument it will extract the file and will search for the _install_ file.

### How to call rt

`rt rt-file [ARGS] `
`rt recipe [ARGS] `

> rt-file or recipe: Can be a RT recipe file or a package file. This argument will be treated as package file if the file have the following extensions: rt, tar.gz, gzip or zip otherwise will try to read the file as a recipe.

> ARGS: argument that can be accesed from built-in array "args".

### How to install a package

When packing it has to be included a file named _install_ that will contain the recipe to install the recipe.

### Features:
* Add / ignore paths, files and extensions
* root dir and target_dir 
* '>' Run console command
* Using of recipe coomand arguments
* OS check (TODO: does not make sense if there is no conditionals)
* read file (TODO)
* condiiotnal checks (TODO)
* variable declaratinos (TODO)
* '$()' use of environment variables
* pack builds, check dependencies and install packages
* print messages (print "msg")
* concact print messages by using spaces (print "msg" "msg2")
* git and svn native support 

### Config File:
* Bind compiler tools (TODO)
* create aliases (TODO)

### Instructions to create a package:

To create a package the order below must be followed: 

1. target_dir 

`target_dir path/env_var/env_var + path/*arg` (if path does not exist it tries to create it)

2. packing instructions 
 
`add, ignore, root_dir, target_dir`

3. pack call 

`pack _filename_`

NOTE: Between steps can be other instructions like create_file, or invoke a script

## Syntax
`root_dir _path_ as root_dir_in_path` 

 > Indicates the root directory (*\_path\_*) where start to walk. Can be changed at any point of the recipe. Instructions are related to this root. The root_dir_in_path indicates the path in the package where stating to include the files, if not used, the files will be inserted exacly as the root_dir indicates.
 
`target_dir _path_` 
 > Indicates the target directory (*\_path\_*) where the pckg will be generated. It is mandatory and has to be declared before calling pack.

`add [_pattern_] [as _path_]*` 

> Add a pattern into the package. If used [as path], insertes the pattern inside the _path_ indicated.

`ignore [_pattern_] from [_path_]*`

> Ignores the pattern from being inserted in the package. The [from path] is optional, if used goes to the ignore applies to the _path_ indicated. if not used the default path is the root_dir.

`pack _filename_`

> Starts packing into *\_filename\_* all the files and folders according the instructions given before this call.

`print "_str_" ...`

> Prints out the *\_str\_*
> To concatenate strings uses spaces. 

 `args`

> the "args" keyword contains the value of the arguments being the first position the first argument, not the name of the binary. For example:
```
$rt filename1 value2
print args[0] # this prints filename1
print args[1] #this prints value2
```

#### Example of pack recipe 
```
root_dir $ROOT_DIR as root_path_in_package # just for packing 
target_dir args[0] # just for packing

> ./createVersionFile.sh

add version.h
ignore *.cpp
ignore *.c
ignore *.o

#ignore path scripts inside the root dir
ignore ./scripts

#ignore mp3 files only from ./res dir
ignore .mp3 from ./res

#ignore .log files from ./bin dir and all the subdirectories
ignore .log from ./bin*

#add the content of config dir inside "release" folder
add /tmp/config as /relase/config

print "Creating pacakge.."

#at this momments packs the file with the instructions above. THe recipe can contains as much as packs the users wanted
pack my-pckg.rt

git add my-pckg.rt
git commit -m "uploaded new version"
git push
```
