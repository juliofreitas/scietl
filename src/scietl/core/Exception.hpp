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
  \file scietl/core/Exception.hpp

  \brief Base exception class for SciETL Core Runtime Module.

  \author Gilberto Ribeiro de Queiroz
 */

#ifndef __SCIETL_CORE_EXCEPTION_HPP__
#define __SCIETL_CORE_EXCEPTION_HPP__

// SciETL
#include "../Exception.hpp"

namespace scietl
{
  namespace core
  {
    //! Base exception class for focos2scidb.
    struct exception: virtual scietl::exception { };

  }  // end namespace core
}    // end namespace scietl

#endif // __SCIETL_EXCEPTION_HPP__
