# RT - Recipie Tool

## Description

RT is a packing tool to bundle, check and install applications and dependencies.

It is desing to be stratightfoward, user-friendy and cooperative.

**Increate the power with scipt calls**
**No many options to remember**
**No many file to configure**

## How to use RT
Everything you need is a recipie file to give intructions about what you want to do.

#**Features:**
* Add path
* Add file
* Add extension
* Ignore path
* Ignore extension
* root dir 
* target dir
* '>' Run console command
* invoke script with args and get those arguments by adding * (*arg1, *arg2)
* create file 
* write file
* OS check
* read file (TODO)
* condiiotnal checks (TODO)
* variable declaratinos (TODO)
* '$' use of environment variables
* pack builds, check dependencies and install packages

#**Config File:**
* Bind compiler tools
* create aliases

#**Instrcutionsto create a package**
To create a package the order below must be followed: 

1. root_dir => root_dir = path/env_var/env_var + path/*arg  (if path does not exist it tries to create it)
2. target_dir => target_dir = path/env_var/env_var + path/*arg (if path does not exist it tries to create it)
3. packing instructions => add_path, add_file, add_ext, ignore_path, ignore_file, ignore_ext, 
4. pack call => pack filename

NOTE: Between steps can be other instructions like create_file, or invoke a script
