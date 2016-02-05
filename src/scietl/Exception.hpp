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
  \file scietl/Exception.hpp

  \brief Base exception class for SciETL.

  \author Gilberto Ribeiro de Queiroz
 */

#ifndef __SCIETL_EXCEPTION_HPP__
#define __SCIETL_EXCEPTION_HPP__

// STL
#include <stdexcept>
#include <string>

// Boost
#include <boost/exception/all.hpp>

namespace scietl
{
  //! Base exception class for focos2scidb.
  struct exception: virtual std::exception, virtual boost::exception { };

  //! An exception occurried during a parse action.
  struct parse_error: virtual exception { };

  //! An exception indicating an invalid argument value.
  struct invalid_arg_value: virtual exception { };

  //! An exception indicating an invalid directory.
  struct invalid_dir_error: virtual exception { };

  //! An exception indicating an error due to file handling.
  struct file_error: virtual exception { };

  //! An exception indicatin an error reported by GDAL.
  struct gdal_error: virtual exception { };

  //! An exception indicating a data conversion error.
  struct conversion_error: virtual exception { };

  //! The base type for error report messages.
  typedef boost::error_info<struct tag_error_description, std::string> error_description;
}

#endif // __SCIETL_EXCEPTION_HPP__
