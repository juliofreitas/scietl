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
  \file scietl/GDALUtils.cpp

  \brief Utility functions for dealing with GDAL and SciDB.

  \author Gilberto Ribeiro de Queiroz
 */

// SciETL
#include "GDALUtils.hpp"
#include "Exception.hpp"

std::size_t
scietl::core::num_bytes(GDALDataType dt)
{
  switch(dt)
  {
    case GDT_Byte:
      return sizeof(char);
      
    case GDT_UInt16:
      return sizeof(uint16_t);
      
    case GDT_Int16:
      return sizeof(int16_t);
      
    case GDT_UInt32:
      return sizeof(uint32_t);
      
    case GDT_Int32:
      return sizeof(int32_t);
      
    case GDT_Float32:
      return sizeof(float);
      
    case GDT_Float64:
      return sizeof(double);
      
    default:
      throw scietl::conversion_error() << scietl::error_description("can not determine the number of bytes for this GDAL type!");
  }
}

