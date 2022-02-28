# RT - Recipie Tool

## Description

RT is a packing tool to bundle, check and install applications and dependencies.

It is desing to be stratightfoward, user-friendy and cooperative.

**Increate the power with scipt calls**
**No many options to remember**
**No many file to configure**

## Usage
Everything you need is a recipie file to give intructions about what you want to do.

### How to call rt

`rt src dest*`

> src: Can be a recepie file or a package file.
> dest (optional): Where the package will be unpacked. If empty, will be unpacked in the current directory.

### How to install a package

When packing it has to be included a file named _install_ that will contain the recepie to install the recepie.

### Features:
* Add path
* Add file
* Add extension
* Ignore path
* Ignore extension
* root dir 
* target dir
* '>' Run console command
* Using of recepie arguments. Use those arguments by define them (args = ...)
* OS check (TODO: does not make sense if there is no conditionals)
* read file (TODO)
* condiiotnal checks (TODO)
* variable declaratinos (TODO)
* '$' use of environment variables
* pack builds, check dependencies and install packages
* print messages (print "msg")
* git and svn native support 
* build your app

### Config File:
* Bind compiler tools
* create aliases

### Instrcutions to create a package:

To create a package the order below must be followed: 

1. target_dir 

`target_dir path/env_var/env_var + path/*arg` (if path does not exist it tries to create it)

2. packing instructions 
 
`add_path, add_file, add_ext, ignore_path, ignore_file, ignore_ext, etc`

3. pack call 

`pack _filename_`

NOTE: Between steps can be other instructions like create_file, or invoke a script

## Syntax
`root_dir _path_` 
 > Indicates the root directory (*\_path\_*) where start to walk. Can be changed at any point of the recepie. Instructions are related to this root
 
`target_dir _path_` 
 > Indicates the target directory (*\_path\_*) where the pckg will be generated. It is mandatory and has to be declared before calling pack.

`add_path _pathSrc _new_pckg_path_ (and ignore_path | ignore_file | ignore_ext and ..)*` 

> Adds _\_pathSrc\__ and its contain inside the package file as *\_new_pckg_path\_*. If path does not exist it will be created inside the pacakge

`add_path _path-to-add_ (and ignore_path | ignore_file | ignore_ext and ..)*`

> Adds *_path-to-add_* and its contain inside the final tar.gz
  
`add_file _file-to-add_ _path-where-to-add_`

> Adds the file *\_file-to-add\_* inside the path *\_path-where-to-add\_*

`add_file _files-to-add_`

> Adds the file *\_files-to-add\_* inside the package preserving the path inside it.

`add_ext _extensions_ `

> Add all the files with the *\_extensions\_* inside the package

`ignore_path _path_`

> Ignores the path *\_path\_* and its contains

`ignore_file _file-to-ignore_`

> Ignores the file *\_file-to-ignore\_*

`ignore_ext _extension_`

> Ignores all the files with the *\_extension\_* extesion

`arguments _arg1_ _arg2_ ...`

> Set the arguments to use the recepie. If the recepie call does not match with the argumentes defined it will raise and error. This tipically goes in the begining of the recepie.

`pack _filename_`

> Starts packing into *\_filename\_* all the files and folders according the instructions given before this call.

`print _str_`

> Prints out the *\_str\_*

`_path_`

 > This can be a path, an environment varriable or env_va and paths cocatenated by '/'.  e.g `$myenvvar/folder or $var1/$var2/folder` etc. If '/' is the last character in any environment variable, the duplicity it will be resolved atumatically.

#### Script Example:
```
arguments targetFile
root_dir $ROOT_DIR
target_dir targetFile

> ./createVersionFile.sh

add_file version.h
ignore_ext cpp
ignore_ext c
ignore_ext o

#ignore mp3 files only from ./res dir
ignore_ext /res/ mp3

#add config dir inside release folder
add_path /tmp/config relase/config

pack myversion.tar.gz

git add myversion.tar.gz
git commit -m "uploaded new version"
git push
```
