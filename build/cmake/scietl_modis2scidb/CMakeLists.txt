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
#  Description: Main CMake script for SciETL build system.
#
#  Author: Gilberto Ribeiro de Queiroz
#          Eduardo Llapa Rodriguez
#          Matheus Cavassan Zaglia
#          Roger Victor
#

file(GLOB SCIETL_SRC_FILES ${SCIETL_ABSOLUTE_ROOT_DIR}/src/scietl/modis2scidb/*.cpp)
file(GLOB SCIETL_HDR_FILES ${SCIETL_ABSOLUTE_ROOT_DIR}/src/scietl/modis2scidb/*.hpp)

source_group("Source Files"  FILES ${SCIETL_SRC_FILES})
source_group("Header Files"  FILES ${SCIETL_HDR_FILES})

add_executable(modis2scidb ${SCIETL_HDR_FILES} ${SCIETL_SRC_FILES})

target_link_libraries(modis2scidb ${Boost_SYSTEM_LIBRARY}
                                  ${Boost_DATE_TIME_LIBRARY}
                                  ${Boost_CHRONO_LIBRARY}
                                  ${Boost_TIMER_LIBRARY}
                                  ${Boost_FILESYSTEM_LIBRARY}
                                  ${Boost_PROGRAM_OPTIONS_LIBRARY}
                                  ${GDAL_LIBRARY})

install(TARGETS modis2scidb
        EXPORT scietl-targets
        RUNTIME DESTINATION ${SCIETL_DESTINATION_RUNTIME} COMPONENT runtime
        LIBRARY DESTINATION ${SCIETL_DESTINATION_LIBRARY} COMPONENT runtime
        ARCHIVE DESTINATION ${SCIETL_DESTINATION_ARCHIVE} COMPONENT runtime)
