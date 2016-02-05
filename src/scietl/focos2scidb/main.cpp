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
#include "Exception.hpp"

// SciETL
#include "../Version.hpp"
#include "../core/GDALWrapper.hpp"
#include "../core/GDALUtils.hpp"

// STL
#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>

// Boost
#include <boost/filesystem.hpp>
#include <boost/foreach.hpp>
#include <boost/format.hpp>
#include <boost/program_options.hpp>
#include <boost/shared_array.hpp>
#include <boost/timer/timer.hpp>


//! The list of possible input parameters
struct input_arguments
{
  std::string source_file_name;
  std::string target_file_name;
  int16_t time_point;
  bool verbose;
};

void valid_args(input_arguments& args);

void convert(const input_arguments& args);

int main(int argc, char **argv)
{
  GDALAllRegister();
  
  try
  {
    boost::timer::cpu_timer timer;
    
    input_arguments parsed_args;
    
    boost::program_options::options_description options_all("Fire Points to SciDB's Multidimensional Array Conversion Options");
    
    options_all.add_options()
    ("version", "Print Fire Points to SciDB conversion tool version.\n")
    ("help", "Prints help message.\n")
    ("verbose", "Turns on verbose mode: prints timing and some more information about the conversion progress.\n")
    ("f", boost::program_options::value<std::string>(&parsed_args.source_file_name), "The source TIFF file to convert to SciDB's load format.\n")
    ("o", boost::program_options::value<std::string>(&parsed_args.target_file_name), "The target folder to store SciDB data file.\n")
    ("t", boost::program_options::value<int16_t>(&parsed_args.time_point), "The timeline position for the dataset.\n")
    ;
    
    boost::program_options::variables_map options;
    
    boost::program_options::store(boost::program_options::parse_command_line(argc, argv, options_all), options);
    
    boost::program_options::notify(options);
    
    if(options.count("help"))
    {
      std::cout << options_all << std::endl;
      
      return EXIT_SUCCESS;
    }
    
    if(options.count("version"))
    {
      std::cout << "\n\nfocos2scidb version: " SCIETL_VERSION_STRING "\n" << std::endl;
      
      return EXIT_SUCCESS;
    }
    
    parsed_args.verbose = options.count("verbose") ? true : false;
    
    valid_args(parsed_args);
    
    if(parsed_args.verbose)
      std::cout << "\nfocos2scidb started\n" << std::endl;
    
    convert(parsed_args);
    
    if(parsed_args.verbose)
      std::cout << "\n\nfocos2scidb finished successfully!\n" << std::endl;
  }
  catch(const std::exception& e)
  {
    std::cerr << "\n\nfocos2scidb finished with errors!\n";
    
    if(e.what() != 0)
      std::cerr << "\nAn unexpected error has occurried: " << e.what() << "\n";
    
    std::cerr << "\nPlease, report it to gribeiro@dpi.inpe.br.\n" << std::endl;
    
    return EXIT_FAILURE;
  }
  catch(...)
  {
    std::cerr << "\n\nAn unexpected error has occurried with no additional information.\n" << std::endl;
    
    return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}

void valid_args(input_arguments& args)
{
  if(args.source_file_name.empty())
    throw scietl::invalid_arg_value() << scietl::error_description("missing input GeoTIFF file name!");
  
  if(!boost::filesystem::exists(args.source_file_name))
    throw scietl::invalid_dir_error() << scietl::error_description("could not find input GeoTIFF file!");
  
  if(args.target_file_name.empty())
    throw scietl::invalid_arg_value() << scietl::error_description("missing output file name!");
  
  if(boost::filesystem::exists(args.target_file_name))
    throw scietl::invalid_arg_value() << scietl::error_description("can not overwrite an existing output file!");
}

void convert(const input_arguments& args)
{
  if(args.verbose)
    std::cout << "\n\tbuffering data... " << std::flush;
  
  scietl::core::GDALDatasetPtr dataset(GDALOpen(args.source_file_name.c_str(), GA_ReadOnly));
  
  if(dataset == nullptr)
  {
    boost::format err_msg("could not open dataset: '%1%'!");
    throw scietl::gdal_error() << scietl::error_description((err_msg % args.source_file_name).str());
  }
  
  if(GDALGetRasterCount(dataset) != 1)
  {
    boost::format err_msg("invalid raster data: %1%. It must have only one data band!");
    throw scietl::gdal_error() << scietl::error_description((err_msg % args.source_file_name).str());
  }
  
  GDALRasterBandH band = GDALGetRasterBand(dataset, 1);
    
  if(band == 0)
  {
    boost::format err_msg("could not access band data for file: %1%!");
    throw scietl::gdal_error() << scietl::error_description((err_msg % args.source_file_name).str());
  }
  
  int ncols = GDALGetRasterBandXSize(band);
  int nrows = GDALGetRasterBandYSize(band);
  
  if((ncols != 1021) || (nrows != 1381))
  {
    boost::format err_msg("invalid raster size: %1%. It must be a 1021x1381!");
    throw scietl::gdal_error() << scietl::error_description((err_msg % args.source_file_name).str());
  }
  
  GDALDataType pixel_type = GDALGetRasterDataType(band);
  
  if(pixel_type != GDT_Byte)
  {
    boost::format err_msg("invalid raster pixel type: %1%. It must be a raster with a single band with pixels of byte data type!");
    throw scietl::gdal_error() << scietl::error_description((err_msg % args.source_file_name).str());
  }
  
  std::size_t pixel_size = scietl::core::num_bytes(pixel_type);
  
  boost::shared_array<unsigned char> buffer(new unsigned char[ncols * nrows * pixel_size]);
  
  CPLErr result = GDALRasterIO(band, GF_Read, 0, 0, ncols, nrows, buffer.get(), ncols, nrows, pixel_type, 0, 0);
  
  if(result == CE_Failure)
  {
    boost::format err_msg("could not read dataset: '%1%'!");
    throw scietl::gdal_error() << scietl::error_description((err_msg % args.source_file_name).str());
  }
  
  if(args.verbose)
  {
    std::cout << "OK!" << std::flush;
    std::cout << "\n\tsaving data... " << std::flush;
  }
  
  std::ofstream f(args.target_file_name.c_str(), std::ios::binary);

  if(!f.is_open())
  {
    boost::format err_msg("could not create file: '%1%'. Please, check if target file or dir exist.");
    throw scietl::gdal_error() << scietl::error_description((err_msg % args.target_file_name).str());
  }

  unsigned char* bookmark = buffer.get();

  for(int i = 0; i != nrows; ++i)
  {
    for(int j = 0; j != ncols; ++j)
    {
      int16_t col = static_cast<int16_t>(j);
      int16_t row = static_cast<int16_t>(j);
      int16_t t = args.time_point;
      
      f.write(reinterpret_cast<char*>(&col), sizeof(int16_t));
      f.write(reinterpret_cast<char*>(&row), sizeof(int16_t));
      f.write(reinterpret_cast<char*>(&t), sizeof(int16_t));
      f.write(reinterpret_cast<char*>(bookmark), pixel_size);
      
      bookmark += pixel_size;
    }
  }
  
  f.close();
}
