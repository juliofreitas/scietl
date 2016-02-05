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
  \file scietl/core/GDALUtils.hpp

  \brief Utility functions for dealing with GDAL and SciDB.

  \author Gilberto Ribeiro de Queiroz
 */

#ifndef __SCIETL_GDALUTILS_HPP__
#define __SCIETL_GDALUTILS_HPP__

// GDAL
#include <gdal.h>

// STL
#include <cstddef>

namespace scietl
{
  namespace core
  {
    /*!
      \brief Compute the number of bytes for a given GDAL data type.

      \exception scietl::conversion_error If we don't know the given GDAL data type size.
     */
    std::size_t num_bytes(GDALDataType dt);
    
  }  // end namespace core
}    // end namespace scietl

#endif // __SCIETL_GDALUTILS_HPP__
