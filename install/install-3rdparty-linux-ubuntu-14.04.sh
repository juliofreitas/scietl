#!/bin/bash
#
#   Copyright (C) 2014 National Institute For Space Research (INPE) - Brazil.
#
#  This file is part of SciETL.
#
#  SciETL is free software: you can
#  redistribute it and/or modify it under the terms of the
#  GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License,
#  or (at your option) any later version.
#
#  SciETL is distributed in the hope that
#  it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with SciETL. See LICENSE. If not, write to
#  e-sensing team at <esensning-team@dpi.inpe.br>.
#
#
#  Description: Install all required software for SciETL on Linux Ubuntu 14.04.
#
#  Author: Gilberto Ribeiro de Queiroz
#          Eduardo Llapa Rodriguez
#
#
#  Example:
#  $ SCIETL_DEPENDENCIES_DIR="/home/gribeiro/MyLibs" ./install-3rdparty-linux-ubuntu-14.04.sh
#

echo "***************************************************************"
echo "* SciETL 3rd-party Libraries Installer for Linux Ubuntu 14.04 *"
echo "***************************************************************"
echo ""
sleep 1s

#
# Valid parameter val or abort script
#
function valid()
{
  if [ $1 -ne 0 ]; then
    echo $2
    echo ""
    exit
  fi
}


#
# Update Ubuntu install list
#
sudo apt-get update
valid $? "Error: could not update apt-get database list"


#
# gcc
#
gcpp_test=`dpkg -s g++ | grep Status`

if [ "$gcpp_test" != "Status: install ok installed" ]; then
  sudo  apt-get -y install g++
  valid $? "Error: could not install g++! Please, install g++: sudo apt-get -y install g++"
  echo "g++ installed!"
else
  echo "g++ already installed!"
fi


#
# zlibdevel
#
zlibdevel_test=`dpkg -s zlib1g-dev | grep Status`

if [ "$zlibdevel_test" != "Status: install ok installed" ]; then
  sudo apt-get -y install zlib1g-dev
  valid $? "Error: could not install zlib1g-dev! Please, install g++: sudo apt-get -y install zlib1g-dev"
  echo "zlib1g-dev installed!"
else
  echo "zlib1g-dev already installed!"
fi


#
# python support
#
pysetup_test=`dpkg -s python-setuptools | grep Status`

if [ "$gcpp_test" != "Status: install ok installed" ]; then
  sudo apt-get -y install python-setuptools
  valid $? "Error: could not install python-setuptools! Please, install readline: sudo apt-get -y install python-setuptools"
  echo "python-setuptools installed!"
else
  echo "python-setuptools already installed!"
fi

pypip_test=`dpkg -s python-pip | grep Status`

if [ "$pypip_test" != "Status: install ok installed" ]; then
  sudo apt-get -y install python-pip
  valid $? "Error: could not install python-pip! Please, install readline: sudo apt-get -y install python-pip"
  echo "python-pip installed!"
else
  echo "python-pip already installed!"
fi

pydev_test=`dpkg -s python-dev | grep Status`

if [ "$pydev_test" != "Status: install ok installed" ]; then
  sudo apt-get -y install python-dev
  valid $? "Error: could not install python-dev! Please, install readline: sudo apt-get -y install python-dev"
  echo "python-dev installed!"
else
  echo "python-dev already installed!"
fi

numpy_test=`dpkg -s python-numpy | grep Status`

if [ "$numpy_test" != "Status: install ok installed" ]; then
  sudo apt-get -y install python-numpy
  valid $? "Error: could not install python-numpy! Please, install readline: sudo apt-get -y install python-numpy"
  echo "python-numpy installed!"
else
  echo "python-numpy already installed!"
fi


#
# autoconf
#
autoconf_test=`dpkg -s autoconf | grep Status`

if [ "$autoconf_test" != "Status: install ok installed" ]; then
  sudo apt-get -y install autoconf
  valid $? "Error: could not install autoconf! Please, install readline: sudo apt-get -y install autoconf" 
  echo "autoconf installed!"
else
  echo "autoconf already installed!"
fi


#
# GNU gettext
#
gettext_test=`dpkg -s gettext | grep Status`

if [ "$gettext_test" != "Status: install ok installed" ]; then
  sudo apt-get -y install gettext
  valid $? "Error: could not install gettext! Please, install readline: sudo apt-get -y install gettext" 
  echo "gettext installed!"
else
  echo "gettext already installed!"
fi


#
# CMake
#
cmake_test=`dpkg -s cmake | grep Status`

if [ "$cmake_test" != "Status: install ok installed" ]; then
  sudo apt-get -y install cmake cmake-qt-gui
  valid $? "Error: could not install CMake! Please, install CMake: sudo apt-get -y install cmake"
  echo "CMake installed!"
else
    if [ ! command -v cmake --version >/dev/null 2>&1 ]; then
      valid 1 "CMake already installed but not found in PATH!"
    else
      echo "CMake already installed!"
    fi
fi


#
# Check for scietl-3rdparty-linux-ubuntu-14.04.tar.gz
#
if [ ! -f ./scietl-3rdparty-linux-ubuntu-14.04.tar.gz ]; then
  echo "Please, make sure to have scietl-3rdparty-linux-ubuntu-14.04.tar.gz in the current directory!"
  echo ""
  exit
fi


#
# Extract packages
#
echo "extracting packages..."
echo ""
sleep 1s

tar xzvf scietl-3rdparty-linux-ubuntu-14.04.tar.gz
valid $? "Error: could not extract 3rd party libraries (scietl-3rdparty-linux-ubuntu-14.04.tar.gz)"

echo "packages extracted!"
echo ""
sleep 1s


#
# Go to 3rd party libraries dir
#
cd scietl-3rdparty-linux-ubuntu-14.04
valid $? "Error: could not enter 3rd-party libraries dir (scietl-3rdparty-linux-ubuntu-14.04)"


#
# Check installation dir
#
if [ "$SCIETL_DEPENDENCIES_DIR" == "" ]; then
  SCIETL_DEPENDENCIES_DIR = "/opt/scietl"
fi

export PATH="$PATH:$SCIETL_DEPENDENCIES_DIR/bin"
export LD_LIBRARY_PATH="$PATH:$SCIETL_DEPENDENCIES_DIR/lib"

echo "installing 3rd-party libraries to '$SCIETL_DEPENDENCIES_DIR' ..."
echo ""
sleep 1s


#
# BZIP2
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/lib/libbz2.a" ]; then
  echo "installing bzip2..."
  echo ""
  sleep 1s

  tar xzvf bzip2-1.0.6-ubuntu.tar.gz
  valid $? "Error: could not uncompress bzip2-1.0.6-ubuntu.tar.gz!"

  cd bzip2-1.0.6
  valid $? "Error: could not enter bzip2-1.0.6 dir!"

  make
  valid $? "Error: could not make BZIP2!"

  make install PREFIX=$SCIETL_DEPENDENCIES_DIR
  valid $? "Error: Could not install BZIP2!"

  cd ..
fi


#
# Proj4 version 4.9.1 (with proj-datumgrid version 1.5)
# Site: https://trac.osgeo.org/proj/
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/lib/libproj.so" ]; then
  echo "installing Proj4..."
  sleep 1s

  tar xzvf proj-4.9.1.tar.gz
  valid $? "Error: could not uncompress proj-4.9.1.tar.gz!"

  cd proj-4.9.1
  valid $? "Error: could not enter proj-4.9.1 dir!"

  ./configure --prefix=$SCIETL_DEPENDENCIES_DIR
  valid $? "Error: could not configure Proj4!"

  make -j 4
  valid $? "Error: could not make Proj4!"

  make install
  valid $? "Error: Could not install Proj4!"

  cd ..
fi


#
# GEOS
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/lib/libgeos.so" ]; then
  echo "installing GEOS..."
  echo ""
  sleep 1s

  tar xjvf geos-3.4.2.tar.bz2
  valid $? "Error: could not uncompress geos-3.4.2.tar.bz2!"

  cd geos-3.4.2
  valid $? "Error: could not enter geos-3.4.2 dir!"

  ./configure --prefix=$SCIETL_DEPENDENCIES_DIR
  valid $? "Error: could not configure GEOS!"

  make -j 4
  valid $? "Error: could not make GEOS!"

  make install
  valid $? "Error: Could not install GEOS!"

  cd ..
fi


#
# libPNG
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/lib/libpng.so" ]; then
  echo "installing libPNG..."
  echo ""
  sleep 1s

  tar xzvf libpng-1.5.17.tar.gz
  valid $? "Error: could not uncompress libpng-1.5.17.tar.gz!"

  cd libpng-1.5.17
  valid $? "Error: could not enter libpng-1.5.17 dir!"

  ./configure --prefix=$SCIETL_DEPENDENCIES_DIR
  valid $? "Error: could not configure libPNG!"

  make -j 4
  valid $? "Error: could not make libPNG!"

  make install
 valid $? "Error: Could not install libPNG!"

  cd ..
fi


#
# Independent JPEG Group version v9a
# Site: http://www.ijg.org
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/lib/libjpeg.so" ]; then
  echo "installing Independent JPEG Group Library..."
  sleep 1s

  tar xzvf jpegsrc.v9a.tar.gz
  valid $? "Error: could not uncompress jpegsrc.v9a.tar.gz!"

  cd jpeg-9a
  valid $? "Error: could not enter jpeg-9a dir!"

  ./configure --prefix=$SCIETL_DEPENDENCIES_DIR
  valid $? "Error: could not configure JPEG!"

  make -j 4
  valid $? "Error: could not make JPEG!"

  make install
  valid $? "Error: Could not install JPEG!"

  cd ..
fi


#
# TIFF
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/lib/libtiff.so" ]; then
  echo "installing TIFF..."
  echo ""
  sleep 1s

  tar xzvf tiff-4.0.3.tar.gz
  valid $? "Error: could not uncompress tiff-4.0.3.tar.gz!"

  cd tiff-4.0.3
  valid $? "Error: could not enter tiff-4.0.3!"

  ./configure --enable-cxx --with-jpeg-include-dir=$SCIETL_DEPENDENCIES_DIR/include --with-jpeg-lib-dir=$SCIETL_DEPENDENCIES_DIR/lib --prefix=$SCIETL_DEPENDENCIES_DIR
  valid $? "Error: could not configure TIFF!"

  make -j 4
  valid $? "Error: could not make TIFF!"

  make install
  valid $? "Error: Could not install TIFF!"

  cd ..
fi


#
# GeoTIFF
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/lib/libgeotiff.so" ]; then
  echo "installing GeoTIFF..."
  echo ""
  sleep 1s

  tar xzvf libgeotiff-1.4.0.tar.gz
  valid $? "Error: could not uncompress libgeotiff-1.4.0.tar.gz!"

  cd libgeotiff-1.4.0
  valid $? "Error: could not enter libgeotiff-1.4.0!"

  ./configure --with-jpeg=$SCIETL_DEPENDENCIES_DIR --with-zlib --with-libtiff=$SCIETL_DEPENDENCIES_DIR --with-proj=$SCIETL_DEPENDENCIES_DIR --prefix=$SCIETL_DEPENDENCIES_DIR
  valid $? "Error: could not configure GeoTIFF!"

  make -j 4
  valid $? "Error: could not make GeoTIFF!"

  make install
  valid $? "Error: Could not install GeoTIFF!"

  cd ..
fi


#
# SZIP
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/lib/libsz.so" ]; then
  echo "installing SZIP..."
  echo ""
  sleep 1s

  tar xzvf szip-2.1.tar.gz
  valid $? "Error: could not uncompress szip-2.1.tar.gz!"

  cd szip-2.1
  valid $? "Error: could not enter szip-2.1!"

  ./configure --prefix=$SCIETL_DEPENDENCIES_DIR
  valid $? "Error: could not configure SZIP!"

  make -j 4
  valid $? "Error: could not make SZIP!"

  make install
  valid $? "Error: Could not install SZIP!"

  cd ..
fi


#
# ICU
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/lib/libicuuc.so" ]; then
  echo "installing ICU..."
  echo ""
  sleep 1s

  tar xzvf icu4c-52_1-src.tgz
  valid $? "Error: could not uncompress icu4c-52_1-src.tgz!"

  cd icu/source
  valid $? "Error: could not enter icu/source!"

  chmod +x runConfigureICU configure install-sh
  valid $? "Error: could not set runConfigureICU to execute mode!"

  CPPFLAGS="-DU_USING_ICU_NAMESPACE=0 -DU_CHARSET_IS_UTF8=1 -DU_NO_DEFAULT_INCLUDE_UTF_HEADERS=1" ./runConfigureICU Linux/gcc --prefix=$SCIETL_DEPENDENCIES_DIR
  valid $? "Error: could not runConfigureICU!"

  make -j 4
  valid $? "Error: could not make ICU!"

  #make check
  #valid $? "Error: could not check ICU build!"

  make install
  valid $? "Error: Could not install ICU!"

  cd ../..
fi


#
# Boost
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/lib/libboost_thread.so" ]; then
  echo "installing boost..."
  echo ""
  sleep 1s

  tar xzvf boost_1_58_0.tar.gz
  valid $? "Error: could not uncompress boost_1_58_0.tar.gz!"

  cd boost_1_58_0
  valid $? "Error: could not enter boost_1_58_0!"

  ./bootstrap.sh
  valid $? "Error: could not configure Boost!"

  ./b2 runtime-link=shared link=shared variant=release threading=multi --prefix=$SCIETL_DEPENDENCIES_DIR -sICU_PATH=$SCIETL_DEPENDENCIES_DIR -sICONV_PATH=/usr -sBZIP2_INCLUDE=$SCIETL_DEPENDENCIES_DIR/include -sBZIP2_LIBPATH=$SCIETL_DEPENDENCIES_DIR/lib install
  valid $? "Error: could not make boost"

  cd ..
fi


#
# HDF4
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/lib/libmfhdf.a" ]; then
  echo "installing HDF4..."
  echo ""
  sleep 1s

  tar xzvf hdf-4.2.9.tar.gz
  valid $? "Error: could not uncompress hdf-4.2.9.tar.gz!"

  cd hdf-4.2.9
  valid $? "Error: could not enter hdf-4.2.9!"

  CFLAGS=-fPIC ./configure --prefix=$SCIETL_DEPENDENCIES_DIR --with-szlib=$SCIETL_DEPENDENCIES_DIR --with-zlib --with-jpeg=$SCIETL_DEPENDENCIES_DIR --enable-netcdf --disable-fortran
  valid $? "Error: could not configure hdf-4!"

  make -j 4
  valid $? "Error: could not make hdf-4"

  make install
  valid $? "Error: Could not install hdf-4"

  cd ..
fi


#
# GDAL/OGR 1.11.2
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/gdal1/lib/libgdal.so" ]; then
  echo "installing GDAL/OGR..."
  echo ""
  sleep 1s

  tar xzvf gdal-1.11.2.tar.gz
  valid $? "Error: could not uncompress gdal-1.11.2.tar.gz!"

  cd gdal-1.11.2
  valid $? "Error: could not enter gdal-1.11.2!"

  CPPFLAGS="-I$SCIETL_DEPENDENCIES_DIR/include" LDFLAGS=-L$SCIETL_DEPENDENCIES_DIR/lib ./configure --with-png=$SCIETL_DEPENDENCIES_DIR --with-libtiff=$SCIETL_DEPENDENCIES_DIR --with-geotiff=$SCIETL_DEPENDENCIES_DIR --with-jpeg=$SCIETL_DEPENDENCIES_DIR  --with-gif --with-ecw=yes --with-expat=yes --with-geos=$SCIETL_DEPENDENCIES_DIR/bin/geos-config --with-threads --without-python --prefix=$SCIETL_DEPENDENCIES_DIR/gdal1 --with-hdf4=$SCIETL_DEPENDENCIES_DIR --without-netcdf 
  valid $? "Error: could not configure gdal!"

  make -j 4 -s
  valid $? "Error: could not make gdal"

  make install
  valid $? "Error: Could not install gdal"

  cd ..
fi

#
# GDAL/OGR 2.0.1
#
if [ ! -f "$SCIETL_DEPENDENCIES_DIR/gdal2/lib/libgdal.so" ]; then
  echo "installing GDAL/OGR..."
  echo ""
  sleep 1s

  tar xzvf gdal-2.0.1.tar.gz
  valid $? "Error: could not uncompress gdal-2.0.1.tar.gz!"

  cd gdal-2.0.1
  valid $? "Error: could not enter gdal-2.0.1!"

  CPPFLAGS="-I$SCIETL_DEPENDENCIES_DIR/include" LDFLAGS=-L$SCIETL_DEPENDENCIES_DIR/lib ./configure --with-png=$SCIETL_DEPENDENCIES_DIR --with-libtiff=$SCIETL_DEPENDENCIES_DIR --with-geotiff=$SCIETL_DEPENDENCIES_DIR --with-jpeg=$SCIETL_DEPENDENCIES_DIR  --with-gif --with-ecw=yes --with-expat=yes --with-geos=$SCIETL_DEPENDENCIES_DIR/bin/geos-config --with-threads --without-python --prefix=$SCIETL_DEPENDENCIES_DIR/gdal2 --with-hdf4=$SCIETL_DEPENDENCIES_DIR --without-netcdf
  valid $? "Error: could not configure gdal!"

  make -j 4 -s
  valid $? "Error: could not make gdal"

  make install
  valid $? "Error: Could not install gdal"

  cd ..
fi


#
# Finished!
#
clear
echo "***************************************************************"
echo "* SciETL 3rd-party Libraries Installer for Linux Ubuntu 14.04 *"
echo "***************************************************************"
echo ""
echo "finished successfully!"

