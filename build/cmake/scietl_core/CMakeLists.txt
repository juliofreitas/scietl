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
#  Description: CMake script for core runtime module.
#
#  Author: Gilberto Ribeiro de Queiroz
#

include_directories(${Boost_INCLUDE_DIR})
include_directories(${GDAL_INCLUDE_DIR})

file(GLOB SCIETL_SRC_FILES ${SCIETL_ABSOLUTE_ROOT_DIR}/src/scietl/core/*.cpp)
file(GLOB SCIETL_HDR_FILES ${SCIETL_ABSOLUTE_ROOT_DIR}/src/scietl/core/*.hpp)

source_group("Source Files"  FILES ${SCIETL_SRC_FILES})
source_group("Header Files"  FILES ${SCIETL_HDR_FILES})

add_library(scietl_core STATIC ${SCIETL_HDR_FILES} ${SCIETL_SRC_FILES})

