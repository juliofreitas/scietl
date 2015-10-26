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
  \file scietl/modis2scidb/Types.hpp

  \brief General data types used in MODIS to SciDB.

  \author Gilberto Ribeiro de Queiroz
 */

#ifndef __SCIETL_MODIS2SCIDB_TYPES_HPP__
#define __SCIETL_MODIS2SCIDB_TYPES_HPP__

// Modis2SciDB
#include "Constants.hpp"

// STL
#include <cstdint>
#include <map>
#include <set>
#include <string>
#include <vector>

namespace modis2scidb
{
  //! A class for keeping a decomposed MODIS file name.
  /*!
    We support definitions like the ones showned in the following sites:
    <ul>
      <li>http://modis-atmos.gsfc.nasa.gov/MOD06_L2/filename.html</li>
      <li>http://modis-atmos.gsfc.nasa.gov/products_filename.html</li>
      <li>https://lpdaac.usgs.gov/products/modis_overview</li>
    </ul>

    MOD = data collected from the Terra (AM overpass)
    MYD = data collected from the Aqua (PM overpass)

    Example: MOD06_L2.AYYYYDDD.h08v05.VVV.YYYYDDDHHMMSS.hdf

    MOD06_L2      => Earth Science Data Type Name => Product Short Name
    AYYYYDDD      => Date Year and Julian Date (Julian Date of Acquisition)
    h08v05        => Tile Identifier (horizontalXXverticalYY)
    VVV           => Collection Version
    YYYYDDDHHMMSS => Production Date & Time (Julian Date of Production)
   */
  struct modis_file_descriptor
  {
    std::string data_type_name;       //!< Earth Science Data Type Name (product short name).
    std::string acquisition_date;     //!< Date year and julian date (julian date of acquisition).
    std::string tile;                 //!< Tile identifier.
    std::string collection_version;   //!< Collection version.
    std::string production_date;      //!< Production Date & Time (julian date of production).
  };

} // end namespace modis2scidb

#endif  // __SCIETL_MODIS2SCIDB_TYPES_HPP__
