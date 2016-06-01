# SciETL
Extract, Transform and Load of Geospatial Data for SciDB

SciETL is a set of command line tools for data conversion and a set of Python scripts for data ingestion into SciDB.

Threre are three command line tools for converting common Earth Observation datasets to spatio-temporal arrays in SciDB:
- **modis2scidb:** a command line application for converting **MODIS HDF** data to a binary format that can be used to load data to a SciDB 1D-array.

- **fire2scidb:** a command line application for converting **Fire Data Products** to a binary format that can be used to load data to a SciDB 1D-array.

- **srtm2scidb:** a command line application for converting **SRTM HGT** data to a binary format that can be used to load data to a SciDB 1D-array.

There are two Python scripts for orchestrating the data conversion from above products and the data ingestion to a multidimensional array in SciDB:
- **modis2scidb-loader:** a Python command line application for orchestrating the load of a set of MODIS HDF data into a SciDB multidimensional array.

- **fire2scidb-loader:** a Python command line application for orchestrating the load of a set of Fire Data Products into a SciDB multidimensional array.


# Using SciETL

## Command Line Tools for Data Conversion

### modis2scidb

**modis2scidb** is a command line application for converting **MODIS HDF** data to a binary format that can be used to load data to a SciDB 1D-array.

Command syntax:
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
$ ./modis2scidb --f MOD13Q1.A2002241.h13v10.005.2008248173553.hdf --o mod13q1-1d-array.scidb --t 1 --b "0,1,2,3,4,5,6,7,8"
```

See [MODIS to SciDB manual](https://github.com/e-sensing/scietl/blob/master/doc/modis2scidb-user-manual.txt) for more information on it.


### fire2scidb

**fire2scidb** is a command line application for converting **Fire Data Products** to a binary format that can be used to load data to a SciDB 1D-array.

Command Syntax:
```
fire2scidb [--version] [--help] --f <source-file> --o <output-file> --t <time-point>
```

It accepts the following options:
- ```--version```: Prints FOCOS to SciDB conversion tool version.
- ```--verbose```: Turns on verbose mode: prints timing and some more information about the conversion progress.
- ```--help```: Prints help message.
- ```--f```: The source file containing the fire data product.
- ```--t```: The time point in the timeline. This will depend on the array time dimension.
- ```--o```: The output file name.

Example:
```
$ ./fire2scidb --f 2000_01_grd5km_focos_referencia.tif --o 2000_01_grd5km_focos_referencia.scidb --t 1
```

See [Fire to SciDB manual](https://github.com/e-sensing/scietl/blob/master/doc/fire2scidb-user-manual.txt) for more information on it.


### srtm2scidb

**srtm2scidb:** a command line application for converting **SRTM HGT** data to a binary format that can be used to load data to a SciDB 1D-array.

Command Syntax
```
srtm2scidb <srtm-hgt-source-file> <scidb-output-file>
```

Example:
```
$ ./srtm2scidb S34W054.hgt name.scidb
```

See [SRTM to SciDB manual](https://github.com/e-sensing/scietl/blob/master/doc/srtm2scidb-user-manual.txt) for more information on it.


## Python Script for Loading Data into SciDB

### fire2scidb-loader

**fire2scidb-loader:** a Python command line application for orchestrating the load of a set of Fire Data Products into a SciDB multidimensional array. 

Command Syntax
```
$ python fire2scidb-loader.py ...
```

Example:
```
$ python fire2scidb-loader.py ...
```

Some requirements for running the script:
- If you want to load the daily number of hotspots data, you will need a target array named **hotspot_daily** with the following definition:
```
CREATE ARRAY hotspot_daily <measure:uint8>[col=0:1020,1,0, row=0:1380,1381,0, time_idx=1:*,1,0];
```

- If you want to load the monthly aggregated hotspot data, you will need a target array named **hotspot_monthly** with the following definition:
```
CREATE ARRAY hotspot_monthly <measure:uint8>[col=0:1020,1,0, row=0:1380,1381,0, time_idx=1:*,1,0];
```

- If you want to load the data with observed daily risk of fire, you will need a target array named **hotspot_risk_daily** with the following definition:
```
CREATE ARRAY hotspot_risk_daily <measure:uint8>[col=1:5157,1,0, row=1:5796,5796,0, time_idx=1:*,1,0];
```

- If you want to load the data with monthly prevalent risk of fire, you will need a target array named **hotspot_risk_monthly** with the following definition:
```
CREATE ARRAY hotspot_risk_monthly <high_risk:uint8, low_risk:uint8, medium_risk:uint8>[col=1:5300,1325,0, row=1:6600,1650,0, time_idx=1:*,1,0];
```

This script is available in the folder [py-tools/fire2scidb-loader](https://github.com/e-sensing/scietl/tree/master/py-tools/fire2scidb-loader).


### modis2scidb-loader

modis2scidb-loader is a Python command line application for orchestrating the load of a set of MODIS HDF data into SciDB multidimensional arrays. These scripts are available in the [py-tools folder](https://github.com/e-sensing/scietl/tree/master/py-tools).

The modis2scidb-loader is organized as follows:
- **addHdfs2bin.py:** script that export/adds an HDF file to SciDB's binary format.
- **checkFolder.py:** script that checks a folder for SciDB's binary files.
- **load2scidb.py:** script that loads a binary file to a SciDB database.
- **run.py:** it builds the path to the MODIS files and then it calls **addHdfs2bin.py**.

In order to use modis2scidb-loader:
- Download the scripts to the *script-folder*.
- Copy the file to the SciDB coordinator instance.
- Create a destination array in SciDB. This is the *dest-array*:
  -  For MOD09Q1:
```
CREATE ARRAY MOD09Q1 <red:int16, nir:int16, quality:uint16>
             [col_id=48000:72000,1014,5,row_id=38400:62400,1014,5,time_id=0:9200,1,0];
```
- For MOD13Q1:
```
CREATE ARRAY MOD13Q1 &lt;ndvi:int16, evi:int16, quality:uint16, red:int16, nir:int16, blue:int16, mir:int16, viewza:int16, sunza:int16, relaza:int16, cdoy:int16, reli:int16&gt; [col_id=48000:72000,502,5,row_id=38400:62400,502,5,time_id=0:9200,1,0];
```
- Create a folder accessible by SciDB. This is the *check-folder* from where data is loaded to SciDB.
- Run *checkFolder.py* pointing to the *check-folder*. The files found here will be uploaded to SciDB. For example:
```
$ python checkFolder.py /home/scidb/toLoad/ /home/scidb/modis2scidb/ MOD09Q1 &
```
- Run *addHdfs2bin.py* to export MODIS HDFs to binary files. After finishing, the file can be copied to the *check-folder*. For example:
```
$ python addHdfs2bin.py /home/scidb/MODIS_ARC/MODIS/MOD09Q1.005/2000.02.18/MOD09Q1.A2000049.h10v08.005.2006268191328.hdf /home/scidb/MOD09Q1.A2000049.h10v08.005.2006268191328.sdbbin

$ mv /home/scidb/MOD09Q1.A2000049.h10v08.005.2006268191328.sdbbin /home/scidb/toLoad/MOD09Q1.A2000049.h10v08.005.2006268191328.sdbbin
```
- Alternatively, you can use *run.py* to make calls to *addHdfs2bin.py* on many HDFs.

These scripts are available in the folder [py-tools/modis2scidb-loader](https://github.com/e-sensing/scietl/tree/master/py-tools/modis2scidb-loader).

# Source Code Instructions

In the root directory of SciETL codebase (the source code tree) there are some text files explaining the details of the codebase:

- **[BRANCHES-AND-TAGS:](https://github.com/e-sensing/scietl/blob/master/BRANCHES-AND-TAGS)** Notes on how to switch to the right branch to work on or the right tag to get the source code.

- **[BUILD-INSTRUCTIONS:](https://github.com/e-sensing/scietl/blob/master/BUILD-INSTRUCTIONS)** Notes on how to compile and install SciETL for each platform.

- **CHANGELOG:** List of changes in SciETL source code. **Not available yet!**

- **[DEPENDENCIES:](https://github.com/e-sensing/scietl/blob/master/DEPENDENCIES)** The list of third-party library you must install before building SciETL.

- **[LICENSE:](https://github.com/e-sensing/scietl/blob/master/LICENSE)** License statement in plain txt format.

- **[README:](https://github.com/e-sensing/scietl/blob/master/README)** Contains instructions about how to build and how is organized SciETL source code.

If you want to build SciETL from source, first take a look at the section **Dependencies** (below in this document) and read the right tip for automatically building the dependencies in your platform.


# Source Code Organization

- **[build/cmake:](https://github.com/e-sensing/scietl/tree/master/build/cmake)** Contains the CMake scripts with commands, macros and functions used to build the environment for compiling libraries and executables in different platforms using the CMake tool.
 
- **[install:](https://github.com/e-sensing/scietl/tree/master/install)** Bash scripts for helping building and installing SciETL.

- **licenses:** Copyright notices of third-party libraries used by SciETL. **Not available yet!**

- **[resources:](https://github.com/e-sensing/scietl/tree/master/resources)** Fonts, images, sql, and xml files among other resources of general use.

- **[src:](https://github.com/e-sensing/scietl/tree/master/src)** Contains the source code of SciETL and its automatic test system.


# Third-Party Dependencies

The file named **[DEPENDENCIES](https://github.com/e-sensing/scietl/blob/master/DEPENDENCIES)** in the root of SciETL source tree contains the official list of third-party libraries and tools that you must install before building SciETL from source.

If you want to build yourself SciETL then you need to install some third-party libraries. Below we show the list of third-party libraries dependencies and its versions:
- **Boost (Mandatory):** SciETL is built on top of Boost libraries. You will need to have them installed in order to build SciETL. Make sure to have at least version 1.54.0 installed. If you prefer to install from source, download it from: http://www.boost.org.

- **GDAL (Mandatory):** **TODO**.

- **Python (Mandatory):** **TODO**.

- **pyhdf (Mandatory):** **TODO**.
 
## Bash script for building all dependencies on Linux Ubuntu 14.04

We have prepared a special bash script for building and installing the dependencies on Linux Ubuntu 14.04. This script can be found in SciETL source tree under *install* folder. Follow the steps below:

- Download the third-party libraries package used by the development team: [scietl-3rdparty-linux-ubuntu-14.04.tar.gz](http://www.dpi.inpe.br/esensing-devel/scietl-3rdparty-linux-ubuntu-14.04.tar.gz).

- Copy the script [install-3rdparty-linux-ubuntu-14.04.sh](https://raw.githubusercontent.com/e-sensing/scietl/master/install/install-3rdparty-linux-ubuntu-14.04.sh) to the same folder you have downloaded the *scietl-3rdparty-linux-ubuntu-14.04.tar.gz* package.

- Open the shell command line and call the script *install-3rdparty-linux-ubuntu-14.04.sh* setting the target to install all the stuffs from these third-party libraries and tools:
```
$ SCIETL_DEPENDENCIES_DIR="/home/user/mylibs" ./install-3rdparty-linux-ubuntu-14.04.sh
```

**Note:** Don't choose as target location a system folder such as */usr* or */usr/local*. Try some user specific folder. The best suggestion is to replace the folder named *user* by your user name.


# Cloning SciETL Repository

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

# Branches

**Note:** We have only one branch: master. This is just a remainder on how to use branches.

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

For example, if you want to switch to branch *b-1.0.0-alpha* you can use the following command:

`$ git checkout -b b-1.0.0-alpha origin/b-1.0.0-alpha`


# Tags

**Note:** We don't have any tags yet. This is just a remainder on how to use tags.

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


# Build Instructions

After choosing the right branch or tag to work on, follow the instructions on **DEPENDENCIES** section. Make sure you have all the third-party library dependencies listed in this section before trying to build SciETL.

The `build/cmake` folder contains a CMake project for building SciETL.

Until now its build has been tested on:
- Linux Ubuntu 14.04

You should use at least CMake version 2.8.12 for building SciETL. Older versions than this may not work properly.

Follow the build steps below according to your platform.


## Building on Linux with GNU G++

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
$ cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE:STRING="Release" -DCMAKE_INSTALL_PREFIX:PATH="/home/user/myinstall/scietl" -DCMAKE_PREFIX_PATH:PATH="/home/user/mylibs" ../codebase/build/cmake
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

# Quick Notes for Developers

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


# Reporting Bugs

Any problem should be reported to esensing-team@dpi.inpe.br.


# Contact

For more information on SciETL, please, visit e-Sensing project main web page at: http://www.esensing.org.

