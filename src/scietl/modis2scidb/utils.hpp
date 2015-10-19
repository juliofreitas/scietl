/*
  Copyright (C) 2014 National Institute For Space Research (INPE) - Brazil.

  This file is part of SciETL.

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
  e-sensing team at <esensning-team@dpi.inpe.br>.
 */

/*!
  \file scietl/modis2scidb/utils.hpp

  \brief Utility functions for dealing with MODIS data.

  \author Gilberto Ribeiro de Queiroz
 */

#ifndef __SCIETL_MODIS2SCIDB_UTILS_HPP__
#define __SCIETL_MODIS2SCIDB_UTILS_HPP__

// Modis2SciDB
#include "exception.hpp"
#include "types.hpp"

// STL
#include <iosfwd>
#include <string>
#include <utility>
#include <vector>

// Boost
#include <boost/date_time/gregorian/gregorian_types.hpp>
#include <boost/filesystem.hpp>

// GDAL
#include <gdal.h>

namespace modis2scidb
{
  //! Parse band data in the following format: <band-num>,<band-alias>[(;<band-num>,<band-alias>)*].
  std::vector<uint16_t> parse_bands(const std::string& str);

  //! Parse one dimension tiles: 0-9  or 9-9 or just 9
  std::pair<unsigned int, unsigned int>
  parse_tile_dimension_range(const std::string& range);

  //! Parse a given MODIS file name, decomposing it in base parts as a modis_file_descriptor.
  modis_file_descriptor parse_modis_file_name(const std::string& file_name);

  //! Parse a MODIS acquisition date in the following format: AYYYYDDD (YYYY => date year; DDD => julian day)
  boost::gregorian::date parse_modis_acquisition_date(const std::string& adate);

  //! Search for the name of each spectral band in a MODIS HDF file.
  std::vector<std::string>
  extract_subdatasets_pattern_names(const std::string& file_name);

  //! Create a name with a pattern for the subdataset that can be used in format expressions to open GDAL subdatasets.
  std::string make_subdataset_pattern(const std::string& file_name,
                                      const std::string& subdataset_name);

  std::size_t num_bytes(GDALDataType dt);

}  // end namespace modis2scidb

#endif  // __SCIETL_MODIS2SCIDB_UTILS_HPP__
