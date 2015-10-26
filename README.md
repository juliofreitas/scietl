# SciETL
Extract, Transform and Load for SciDB

Right now we have some command line tools for converting common Earth Observation datasets to spatio-temporal arrays in SciDB:
- **modis2scidb:** a command line application for converting MODIS HDF data into SciDB multidimensional arrays.

## modis2scidb

modis2scidb is a command line application for converting MODIS HDF data into SciDB multidimensional arrays.
```
modis2scidb [--version] [--help] --f <modis-hdf-source-file>
            --o <output-file>
            --b "<which bands to convert>" --t <time-point>
```

It accepts the following options:
- ```--version```: Prints MODIS to SciDB conversion tool version.
- ```--verbose```: Turns on verbose mode: prints timing and some more information about the conversion progress.
- ```--help```: Prints help message.
- ```--f```: The source HDF file.
- ```--t```: The time point in the timeline. A number starting from 0.
- ```--b```: A comma separated list of data bands to convert to SciDB load format (see example below).
- ```--o```: The output file name.

Example:
```
$ modis2scidb --f MOD13Q1.A2002241.h13v10.005.2008248173553.hdf --o mod13q1-1d-array.scidb --t 1 --b "0,1,2,3,4,5,6,7,8"
```

See [MODIS to SciDB manual](https://github.com/e-sensing/scietl/blob/master/doc/modis2scidb-user-manual.txt) for more information on it.

## Source Code Instructions

In the root directory of SciETL codebase (the source code tree) there are some text files explaining the details of the codebase:

- **[BRANCHES-AND-TAGS:](https://github.com/e-sensing/scietl/blob/master/BRANCHES-AND-TAGS)** Notes on how to switch to the right branch to work on or the right tag to get the source code.

- **[BUILD-INSTRUCTIONS:](https://github.com/e-sensing/scietl/blob/master/BUILD-INSTRUCTIONS)** Notes on how to compile and install SciETL for each platform.

- **CHANGELOG:** List of changes in SciETL source code. **Not available yet!**

- **[DEPENDENCIES:](https://github.com/e-sensing/scietl/blob/master/DEPENDENCIES)** The list of third-party library you must install before building SciETL.

- **[LICENSE:](https://github.com/e-sensing/scietl/blob/master/LICENSE)** Licence statement in plain txt format.

- **[README:](https://github.com/e-sensing/scietl/blob/master/README)** Contains instructions about how to build and how is organized SciETL source code.

If you want to build SciETL from source, first take a look at the section **Dependencies** (below in this document) and read the right tip for automatically building the dependencies in your platform.

## Source Code Organization

- **[build/cmake:](https://github.com/e-sensing/scietl/tree/master/build/cmake)** Contains the CMake scripts with commands, macros and functions used to build the environment for compiling libraries and executables in different platforms using the CMake tool.
 
- **[install:](https://github.com/e-sensing/scietl/tree/master/install)** Bash scripts for helping building and installing SciETL.

- **licenses:** Copyright notices of third-party libraries used by SciETL. **Not available yet!**

- **[resources:](https://github.com/e-sensing/scietl/tree/master/resources)** Fonts, images, sql, and xml files among other resources of general use.

- **[src:](https://github.com/e-sensing/scietl/tree/master/src)** Contains the source code of SciETL and its automatic test system.
 
## Dependencies

The file named **[DEPENDENCIES](https://github.com/e-sensing/scietl/blob/master/DEPENDENCIES)** in the root of SciETL source tree contains the official list of third-party libraries and tools that you must install before building SciETL from source.

If you want to build yourself SciETL then you need to install some third-party libraries. Below we show the list of third-party libraries dependencies and its versions:
- **Boost (Mandatory):** SciETL is built on top of Boost libraries. You will need to have them installed in order to build SciETL. Make sure to have at least version 1.54.0 installed. If you prefer to install from source, download it from: http://www.boost.org.

- **GDAL (Mandatory):** **TODO**.
 
### Bash script for building all dependencies on Linux Ubuntu 14.04

We have prepared a special bash script for building and installing the dependencies on Linux Ubuntu 14.04. This script can be found in SciETL source tree under *install* folder. Follow the steps below:

- Download the third-party libraries package used by the development team: [scietl-3rdparty-linux-ubuntu-14.04.tar.gz](http://www.dpi.inpe.br/esensing-devel/scietl-3rdparty-linux-ubuntu-14.04.tar.gz).

- Copy the script [install-3rdparty-linux-ubuntu-14.04.sh](https://raw.githubusercontent.com/e-sensing/scietl/master/install/install-3rdparty-linux-ubuntu-14.04.sh) to the same folder you have downloaded the *scietl-3rdparty-linux-ubuntu-14.04.tar.gz* package.

- Open the shell command line and call the script *install-3rdparty-linux-ubuntu-14.04.sh* setting the target to install all the stuffs from these third-party libraries and tools:
```
$ SCIETL_DEPENDENCIES_DIR="/home/user/mylibs" ./install-3rdparty-linux-ubuntu-14.04.sh
```

**Note:** Don't choose as target location a system folder such as */usr* or */usr/local*. Try some user specifiic folder. The best suggestion is to replace the folder named *user* by your user name.


## Cloning SciETL Repository

- Open the shell command line.

- Make a new folder to host SciETL source code:
```
$ mkdir -p /home/user/mydevel/scietl/codebase
```

- Change the current directory to that new folder:
```
$ cd /home/user/mydevel/scietl/codebase
```

- Make a local copy of SciETL repository:
```
$ git clone https://github.com/e-sensing/scietl.git .
```

## Branches
You can check all branches available (remotes and local) and see the current one (marked with "*"):

`$ git branch -a`

The output of above command will be something like:
```
  * master
  remotes/origin/HEAD -> origin/master
  remotes/origin/master
```

In the above output the "* master" means that the current branch is master.

We have the following branches:
- **master:** This is the branch where the development team is working to add new features to future versions of SciETL. It may be instable although the codebase is subject to automatic tests (regression and unittests). We don't recommend to generate production versions of SciETL from this branch. Use it for testing new features and get involved with SciETL development.

To switch to one of the branches listed above, use the checkout command and create a local branch to track the remote branch. The syntax of "git checkout" is:

`$ git checkout -b <local_branch_name> <remote_branch_name without this part "remotes/">`

In order to switch to branch *b-1.0.0-alpha* you can use the following command:

`$ git checkout -b b-1.0.0-alpha origin/b-1.0.0-alpha`

## Tags

Also there are tags which usually are originated from a release branch. For instance, tag *t-1.0.0-alpha1* will be originated from branch *b-1.0.0-alpha*.

To check all tags available, use:

`$ git tag -l           (list all tag names)`
```
  t-1.0.0-alpha1
  t-1.0.0-alpha2
  t-1.0.0-beta1
  t-1.0.0-rc1
  t-1.0.0
  ...
```

If you want to checkout a specific version given by a tag and create a local branch to work on you can use the following git command:

`$ git checkout -b <local_branch_tag_name> <one_of_tag_name_listed>`

For instance, to checkout *t-1.0.0-alpha1* you can enter the following command:

`$ git checkout -b t-1.0.0-alpha1  t-1.0.0-alpha1`

## Build Instructions

After choosing the right branch or tag to work on, follow the insructions on **DEPENDENCIES** section. Make sure you have all the third-party library dependencies listed in this section before trying to build SciETL.

The `build/cmake` folder contains a CMake project for building SciETL.

Until now its build has been tested on:
- Linux Ubuntu 14.04

You should use at least CMake version 2.8.12 for building SciETL. Older versions than this may not work properly.

Follow the build steps below according to your platform.

### Building on Linux with GNU G++

1.1. Open a Command Prompt (Shell).

1.2. We will assume that the codebase (all the source tree) is located at:

`/home/user/mydevel/scietl/codebase`

1.3. Create a folder out of the SciETL source tree to generate the build system, for example:
```
$ cd /home/user/mydevel/scietl
$ mkdir build-release
$ cd build-release
```
**Note:** for the sake of simplicity create this directory in the same level as the source tree (as showned above).

1.4. For Linux systems you must choose the build configuration:
```
$ cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE:STRING="Release" -DCMAKE_INSTALL_PREFIX:PATH="/home/user/myinstall/scietl" -DCMAKE_PREFIX_PATH:PATH="/home/user/mylibs;/home/user/mylibs/terralib5/lib/cmake" ../codebase/build/cmake
```

1.5 Building (with 4 process in parallel):
```
$ make -j 4
```

1.6 Installing:
```
$ make install
```

1.7 Uninstalling:
```
$ make uninstall
```

Notes:
* Some Linux flavours with different versions of GNU gcc and Boost will need more parameters such as:
```
  -DCMAKE_INCLUDE_PATH:PATH="/usr/local;/opt/include"
  -DCMAKE_LIBRARY_PATH:PATH="/usr/local;/opt/lib"
  -DCMAKE_PROGRAM_PATH:PATH="/usr/local/bin;/opt/bin"
  -DBOOST_ROOT:PATH="/opt/boost"
```
* Boost can also be indicated by BOOST_INCLUDEDIR (note: without an '_' separating INCLUDE and DIR):
```
  -DBOOST_INCLUDEDIR:PATH="/usr/local/include"
```
* For generating a debug version set CMAKE_BUILD_TYPE as:
```
  -DCMAKE_BUILD_TYPE:STRING="Debug"
```

### Quick Notes for Developers

If you have built SciETL in Debug mode and you want to run it inside the build tree, you may need to set some environment variables:
* For Mac OS X, you can set the following variables:
```
$ export DYLD_FALLBACK_LIBRARY_PATH=/Users/user/mylibs/lib
$ export DYLD_FALLBACK_FRAMEWORK_PATH=/Users/user/mylibs/lib/
```

* For Linux, you can set the following variable:
```
$ export LD_LIBRARY_PATH=/home/user/mylibs/lib
```

If you want to use QtCreator on Linux Ubuntu 14.04 you can install it through the following command:
```
$ sudo apt-get install qtcreator
```

On Linux Ubuntu 14.04 you can install git through the following command:
```
$ sudo apt-get install git
```

If you have experienced  any problem building any of the third-party tool on Mac OS X, try to install Xcode command line tools:
```
$ xcode-select --install
```

## Reporting Bugs

Any problem should be reported to esensing-team@dpi.inpe.br.


For more information on SciETL, please, visit e-Sensing project main web page at: http://www.dpi.inpe.br/esensing.


