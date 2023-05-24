# RT - Recipe Tool

## Description

RT is a packing tool to bundle, check and install applications and dependencies.

It is desing to be stratightfoward, user-friendy and cooperative.

**Increate the power with scipt calls**
**No many options to remember**
**No many file to configure**

## Usage
Everything you need is a recipe file to give intructions about what you want to do.

### How to call rt

`rt srcFiles dest* `

> srcFile: Can be a recipe file or a package file. This argument will be treated as package file if the file have the following extensions: rt, tar.gz, gzip, zip

> dest (optinal): destiny where to deccompress the package file. Only valid if srcFile is a package file.

### How to install a package

When packing it has to be included a file named _install_ that will contain the recipe to install the recipe.

### Features:
* Add path
* Add file
* Add extension
* Ignore path
* Ignore extension
* root dir 
* target dir
* '>' Run console command
* Using of recipe coomand arguments
* OS check (TODO: does not make sense if there is no conditionals)
* read file (TODO)
* condiiotnal checks (TODO)
* variable declaratinos (TODO)
* '$()' use of environment variables
* pack builds, check dependencies and install packages
* print messages (print "msg")
* contact print messages by using spaces (print "msg" "msg2")
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

 > Indicates the root directory (*\_path\_*) where start to walk. Can be changed at any point of the recipe. Instructions are related to this root
 
`target_dir _path_` 
 > Indicates the target directory (*\_path\_*) where the pckg will be generated. It is mandatory and has to be declared before calling pack.

`add_path _path-to-add_`

`add_path _pathSrc [as _new_pckg_path_]` 

`eg) add_path /tmp/config as /src/config # inserts config sir from tmp inside of the value of root_dir and then /src/config` 

>1) Adds *_path-to-add_* and its contain inside the final tar.gz. the [as _new_pckg_path_] inserts the file inside the virtual path inside the package file as *\_new_pckg_path\_*.

`add_file _file-to-add_`

`add_file _file-to-add_ [as _path-where-to-add_]`

> Adds the file *\_files-to-add\_* inside the package preserving the path inside it.
> Adds the file *\_file-to-add\_* inside the path *\_path-where-to-add\_*. The [as _path-where-to-add_] is optional and if not used the default path is the root_dir

`add_ext _extensions_ [from _path_]` 

`eg) add_ext .cpp .h `

`eg) add_ext .cpp .h from ./dir/* #add extension from dir and subdirectories`

> The same as add_ext but with recursive checking. Using add_ext_recursive after using add_ext it overrides the result in case of path and extension repetition. The [from path] is optional and if not used the default path is the root_dir

`ignore_path _path_ from [_path]`

`eg) ignore_path /bin 'ignores /bin from root_dir`

`eg) ignore_path /*/bin from /tmp #ignores /tmp/*/bin directories`

`eg) ignore_path /bin from * #ignores all the bin directories`

> Ignores the path *\_path\_* and its contains
> The *\_path\_* can contains a path, args or a env var eg: ignore_path /tmp
> If the path ignored is not included then it does nothing.

`ignore_file _file_ [from _path]`

`eg) ignore_file file.log from /tmp`

`eg) ignore_file * from /tmp #ignore all files from tmp but not tmp directory`

> Ignores the file *\_file\_*
> The *\_file\_* can contains a path, args or a env var eg: "ignore_file file.log from /tmp". The [from path] is optional and if not used the default path is the root_dir

`ignore_ext _extension_ [from _path_]`

> Ignores all the files with the *\_extension\_* extesion. The [from path] is optional and if not used the default path is the root_dir

`pack _filename_`

> Starts packing into *\_filename\_* all the files and folders according the instructions given before this call.

`print "_str_ ...`

> Prints out the *\_str\_*
> To concatenate strings uses spaces. eg) print the name of

 `args`

> the "args" keyword contains the value of the arguments being the first position the first argument, not the name of the binary. For example:
```
$rt filename1 value2
print args[0] # this prints filename1
print args[1] #this prints value2
```

#### Example of pack recipe 
```
root_dir $ROOT_DIR
target_dir args[0]

> ./createVersionFile.sh

add_file version.h
ignore_ext cpp
ignore_ext c
ignore_ext o

#ignore mp3 files only from ./res dir
ignore_ext mp3 from ./res

#ignore .log files from ./bin dir and all the subdirectories
ignore_ext log from ./bin*

#add the content of config dir inside "release" folder
add_path /tmp/config as /relase/config

#at this momments packs the file with the instructions above. THe recipe can contains as much as packs the users wanted
pack myversion.tar.gz

git add myversion.tar.gz
git commit -m "uploaded new version"
git push
```
