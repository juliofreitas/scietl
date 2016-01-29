/*
  Copyright (C) 2014 National Institute For Space Research (INPE) - Brazil.

  This file is part of SciETL - a free and open source tool to Extract, Transform and Load data to SciDB.

  SciETL is free software: you can
  redistribute it and/or modify it under the terms of the
  GNU Lesser General Public License as published by
  the Free Software Foundation, either version 3 of the License,
  or (at your option) any later version.

  SciETL is distributed in the hope that
  it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with SciETL. See LICENSE. If not, write to
  e-sensing team at <esensing-team@dpi.inpe.br>.
 */

/*!
  \file scietl/focos2scidb/main.cpp

  \brief Focus to SciDB multidimensional array conversion tool.

  \author Gilberto Ribeiro de Queiroz
 */

// Focos2SciDB
#include "../Version.hpp"
#include "Exception.hpp"

// STL
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>

// Boost
#include <boost/filesystem.hpp>
#include <boost/foreach.hpp>
#include <boost/format.hpp>
#include <boost/program_options.hpp>
#include <boost/shared_array.hpp>
#include <boost/timer/timer.hpp>

// GDAL
#include <gdal.h>

int main(int argc, char **argv)
{
  GDALAllRegister();

  return EXIT_SUCCESS;
}

