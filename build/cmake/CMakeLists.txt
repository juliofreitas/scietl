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

cmake_minimum_required(VERSION 2.8.12)

project(scietl)

#
# main variables for the build script
#

# variables that control the system versioning
set(SCIETL_VERSION_MAJOR 1)
set(SCIETL_VERSION_MINOR 0)
set(SCIETL_VERSION_PATCH 0)
set(SCIETL_VERSION_STATUS "alpha")
set(SCIETL_VERSION_STATUS_FULL "-alpha1")
set(SCIETL_VERSION_STRING "${SCIETL_VERSION_MAJOR}.${SCIETL_VERSION_MINOR}.${SCIETL_VERSION_PATCH}${SCIETL_VERSION_STATUS_FULL}")
set(SCIETL_VERSION "0x010000")

# variables storing absolute paths
set(SCIETL_ABSOLUTE_ROOT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../..)

set(SCIETL_BASE_DESTINATION_DIR "")

if(NOT DEFINED SCIETL_DESTINATION_RUNTIME)
  set(SCIETL_DESTINATION_RUNTIME "${SCIETL_BASE_DESTINATION_DIR}bin")
endif()


#
# global definitions, includes and config
#

# Common definitions to all modules
add_definitions(-DBOOST_ALL_NO_LIB -DBOOST_FILESYSTEM_VERSION=3 -DBOOST_UBLAS_TYPE_CHECK=0)

# Specific definitions per platform
if(APPLE)
  add_definitions(-ftemplate-depth-1024)
endif()

# Build will generate files into a single folder
if((CMAKE_GENERATOR STREQUAL Xcode) OR MSVC)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
  set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
  set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
else()
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
  set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
  set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
endif()

# Where to find modules (find procedures)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/modules")

# Compiler options: warning and C++ 11
if(CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX OR (CMAKE_CXX_COMPILER MATCHES ".*clang"))
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -pedantic -std=c++11")
endif()

# Turn on multi process compilation on Windows
if(MSVC)
  add_definitions(/MP)
endif()

# Enable CTest
enable_testing()

# Build tree directory will be needed in all projects.
include_directories(${CMAKE_BINARY_DIR})


#
# including CMake's auxiliary files
#

include(CMakeDependentOption)


#
# first check of libraries
#

find_package(Boost 1.54.0 REQUIRED system date_time chrono log timer filesystem program_options)

if(NOT Boost_FOUND)
  message(FATAL_ERROR "SciETL: could not find required Boost libraries!")
endif()

find_package(GDAL REQUIRED)

#
# build options
#
# warning: please, do not change the order below!
#

option(SCIETL_MODIS2SCIDB_ENABLED "Build SciETL MODIS conversion tool?" ON)
option(SCIETL_SRTM2SCIDB_ENABLED "Build SciETL SRTM conversion tool?" ON)


#
# process SciETL configuration files
#

#configure_file(${CMAKE_SOURCE_DIR}/terrama2-config-pkg.cmake.in
#               ${CMAKE_BINARY_DIR}/pkg/terrama2-config.cmake @ONLY)

#configure_file(${CMAKE_SOURCE_DIR}/terrama2-config-version.cmake.in
#               ${CMAKE_BINARY_DIR}/terrama2-config-version.cmake @ONLY)

#configure_file(${CMAKE_SOURCE_DIR}/terrama2-config.cmake.in
#               ${CMAKE_BINARY_DIR}/terrama2-config.cmake @ONLY)

#configure_file(${SCIETL_ABSOLUTE_ROOT_DIR}/src/terrama2/Config.hpp.in
#               ${CMAKE_BINARY_DIR}/terrama2_config.hpp @ONLY)

#configure_file(${SCIETL_ABSOLUTE_ROOT_DIR}/src/terrama2/Defines.hpp.in
#               ${CMAKE_BINARY_DIR}/terrama2_defines.hpp @ONLY)

configure_file(${SCIETL_ABSOLUTE_ROOT_DIR}/src/scietl/Version.hpp.in
               ${CMAKE_BINARY_DIR}/scietl_version.hpp @ONLY)

#configure_file(${SCIETL_ABSOLUTE_ROOT_DIR}/COPYING ${CMAKE_BINARY_DIR}/COPYING.txt COPYONLY)


#
# build modules
#

if(SCIETL_MODIS2SCIDB_ENABLED)
  add_subdirectory(scietl_modis2scidb)
endif()

if(SCIETL_SRTM2SCIDB_ENABLED)
  add_subdirectory(scietl_srtm2scidb)
endif()


#
# install and targets export
#

#file(GLOB SCIETL_HDR_FILES ${SCIETL_ABSOLUTE_ROOT_DIR}/src/terrama2/*.hpp)

#install(FILES ${CMAKE_BINARY_DIR}/terrama2_config.hpp
#              ${CMAKE_BINARY_DIR}/terrama2_version.hpp
#              ${SCIETL_HDR_FILES}
#        DESTINATION ${SCIETL_DESTINATION_HEADERS}/terrama2 COMPONENT devel)

#install(FILES ${SCIETL_ABSOLUTE_ROOT_DIR}/src/terrama2.hpp
#        DESTINATION ${SCIETL_DESTINATION_HEADERS} COMPONENT devel)

#install(FILES ${SCIETL_BINARY_DIR}/pkg/terrama2-config.cmake
#              ${SCIETL_BINARY_DIR}/terrama2-config-version.cmake
#        DESTINATION ${SCIETL_DESTINATION_LIBRARY}/cmake/terrama2-${SCIETL_VERSION_STRING} COMPONENT devel)

#install(EXPORT terrama2-targets
#        DESTINATION ${SCIETL_DESTINATION_LIBRARY}/cmake/terrama2-${SCIETL_VERSION_STRING}
#        FILE terrama2-exports.cmake
#        COMPONENT devel)

#install(DIRECTORY ${SCIETL_ABSOLUTE_ROOT_DIR}/share/terrama2/config
#        DESTINATION ${SCIETL_DESTINATION_SHARE}/terrama2 COMPONENT runtime)

#install(DIRECTORY ${SCIETL_ABSOLUTE_ROOT_DIR}/share/terrama2/icons
#        DESTINATION ${SCIETL_DESTINATION_SHARE}/terrama2 COMPONENT runtime)


#
# Track dependencies
#
#if(SCIETL_TRACK_3RDPARTY_DEPENDENCIES)
  #set(CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP ON)

  #include(InstallRequiredSystemLibraries)

  #install(PROGRAMS ${CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS}
  #        DESTINATION bin
  #        COMPONENT runtime)

  #add_subdirectory(fix_bundle)
#endif()


#
# CPack
#

#set(CPACK_SOURCE_INSTALLED_DIRECTORIES "${SCIETL_ABSOLUTE_ROOT_DIR};/")

#configure_file(${SCIETL_SOURCE_DIR}/terrama2-cpack-options.cmake.in
#               ${SCIETL_BINARY_DIR}/terrama2CPackOptions.cmake
#               @ONLY)

#set(CPACK_PROJECT_CONFIG_FILE ${SCIETL_BINARY_DIR}/terrama2CPackOptions.cmake)

#include(CPack)

# defining installation types, components and groups
#cpack_add_install_type(full DISPLAY_NAME "Complete")
#cpack_add_install_type(minimalistic DISPLAY_NAME "Minimalistic")

#cpack_add_component_group(general_group
#                          DISPLAY_NAME "Applications"
#                          DESCRIPTION "SciETL web servers, web clients and GUI applications"
#                          EXPANDED)

#cpack_add_component_group(devel_group
#                          DISPLAY_NAME "Development Tools"
#                          DESCRIPTION "Development Tools: header files, libraries and cmake stuffs"
#                          EXPANDED)

#cpack_add_component(runtime
#                    DISPLAY_NAME "Runtime Libraries and Executables"
#                    DESCRIPTION "Install only necessary shared libraries (or DLLs) and executables"
#                    GROUP general_group
#                    INSTALL_TYPES full minimalistic)

#cpack_add_component(devel
#                    DISPLAY_NAME "Development package"
#                    DESCRIPTION "Install header files, cmake stuffs and additional shared libraries"
#                    GROUP devel_group
#                    INSTALL_TYPES full minimalistic)

#
# Uninstall target
#

#configure_file("${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake.in"
#               "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
#               IMMEDIATE @ONLY)

#add_custom_target(uninstall COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake)

