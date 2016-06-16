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
  \file scietl/fire2scidb/main.cpp

  \brief Focus to SciDB multidimensional array conversion tool.

  \author Gilberto Ribeiro de Queiroz
 */

// fire2scidb
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
    
    boost::program_options::options_description options_all("Fire Data Products to SciDB's Binary Load Format Conversion Options");
    
    options_all.add_options()
    ("version", "Print fire2scidb conversion tool version.\n")
    ("verbose", "Turns on verbose mode: prints timing and some more information about the conversion progress.\n")
    ("help", "Prints help message.\n")
    ("f", boost::program_options::value<std::string>(&parsed_args.source_file_name), "The source fire data product file to convert to SciDB's load format.\n")
    ("o", boost::program_options::value<std::string>(&parsed_args.target_file_name), "The target file name: the SciDB binary data file.\n")
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
      std::cout << "\n\nfire2scidb version: " SCIETL_VERSION_STRING "\n" << std::endl;
      
      return EXIT_SUCCESS;
    }
    
    parsed_args.verbose = options.count("verbose") ? true : false;
    
    valid_args(parsed_args);
    
    if(parsed_args.verbose)
      std::cout << "fire2scidb started" << std::endl;
    
    convert(parsed_args);
    
    const boost::timer::cpu_times elapsed_times(timer.elapsed());
    
    if(parsed_args.verbose)
    {
      
      std::cout << "\telapsed time: " << boost::timer::format(elapsed_times, 3, "%ws wall") << std::endl;
      
      std::cout << "fire2scidb finished successfully!\n" << std::endl;
    }
  }
  catch(const scietl::exception& e)
  {
    if(const std::string* d = boost::get_error_info<scietl::error_description>(e))
      std::cerr << "\nThe following error ocurried: " << *d << "\n";
    
    return EXIT_FAILURE;
  }
  catch(const std::exception& e)
  {
    std::cerr << "\n\nfire2scidb finished with errors!\n";
    
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
    throw scietl::invalid_arg_value() << scietl::error_description("missing input file name!");
  
  if(!boost::filesystem::exists(args.source_file_name))
    throw scietl::invalid_dir_error() << scietl::error_description("could not find input file!");
  
  if(args.target_file_name.empty())
    throw scietl::invalid_arg_value() << scietl::error_description("missing output file name!");
  
  if(boost::filesystem::exists(args.target_file_name))
    throw scietl::invalid_arg_value() << scietl::error_description("can not overwrite an existing output file!");
}

void convert(const input_arguments& args)
{
  if(args.verbose)
    std::cout << "\tbuffering data...\n" << std::flush;
  
// let's try to open the dataset
  scietl::core::GDALDatasetPtr dataset(GDALOpen(args.source_file_name.c_str(), GA_ReadOnly));
  
  if(dataset == nullptr)
  {
    boost::format err_msg("could not open dataset: '%1%'!");
    throw scietl::gdal_error() << scietl::error_description((err_msg % args.source_file_name).str());
  }
  
// does the raster have at least one data band?
  int nbands = GDALGetRasterCount(dataset);
  
  if(nbands < 1)
  {
    boost::format err_msg("invalid raster data: %1%. It must have at least one data band!");
    throw scietl::gdal_error() << scietl::error_description((err_msg % args.source_file_name).str());
  }

// for each data band, we will buffer its whole data
  std::vector<boost::shared_array<unsigned char> > data_bands;
  std::vector<std::size_t> pixel_size_bands;
  std::vector<std::pair<int, int> > band_dimensions;
  
  for(int i = 1; i <= nbands; ++i)
  {
    GDALRasterBandH band = GDALGetRasterBand(dataset, i);
    
    if(band == 0)
    {
      boost::format err_msg("could not access data band '%1%' for file: %2%!");
      throw scietl::gdal_error() << scietl::error_description((err_msg % i % args.source_file_name).str());
    }

// get band dimensions and pixel infromation
    int ncols = GDALGetRasterBandXSize(band);
    int nrows = GDALGetRasterBandYSize(band);
    
    band_dimensions.push_back(std::make_pair(ncols, nrows));
    
    GDALDataType pixel_type = GDALGetRasterDataType(band);
    
    std::size_t pixel_size = scietl::core::num_bytes(pixel_type);
    
    pixel_size_bands.push_back(pixel_size);

// allocate a buffer for the band
    boost::shared_array<unsigned char> buffer(new unsigned char[ncols * nrows * pixel_size]);
    
    if(args.verbose)
    {
      std::cout << "\t\t#band: " << i << "; #cols: " << ncols << "; #rows: "
      << nrows << "; pixel-size: " << pixel_size << "byte(s); data-size: "
      << (static_cast<double>(ncols * nrows * pixel_size) / static_cast<double>(1024*1024))
      << " MiB... " << std::flush;
    }

// read the band data to the buffer
    CPLErr result = GDALRasterIO(band, GF_Read, 0, 0, ncols, nrows, buffer.get(), ncols, nrows, pixel_type, 0, 0);
  
    if(result == CE_Failure)
    {
      boost::format err_msg("could not read band '%1%' for dataset: '%2%'!");
      throw scietl::gdal_error() << scietl::error_description((err_msg % i % args.source_file_name).str());
    }

// keep the band data buffer in a list (actually a vector!)
    data_bands.push_back(buffer);
    
    if(args.verbose)
      std::cout << "OK!\n" << std::endl;
  }

// we are optmistic: now let's check
// if all bands have the same dimension.
// ok: this will avoid any surprises!
  int ncols = band_dimensions[0].first;
  int nrows = band_dimensions[0].second;

  for(int i = 1; i < nbands; ++i)
  {
    if(ncols != band_dimensions[i].first)
    {
      boost::format err_msg("input file '%1%' have bands with different number of columns and rows.");
      throw scietl::gdal_error() << scietl::error_description((err_msg % args.source_file_name).str());
    }
  }
  
  if(args.verbose)
    std::cout << "\tsaving data do SciDB binary file... " << std::flush;

// it's time to save the data in a binary file
  std::ofstream f(args.target_file_name.c_str(), std::ios::binary);

  if(!f.is_open())
  {
    boost::format err_msg("could not create file: '%1%'. Please, check if target file or dir exist.");
    throw scietl::gdal_error() << scietl::error_description((err_msg % args.target_file_name).str());
  }

  std::vector<unsigned char*> buffer_marks;

  for(const auto& b : data_bands)
    buffer_marks.push_back(b.get());
 
  int16_t t = args.time_point;

  for(int i = 0; i != nrows; ++i)
  {
    int16_t row = static_cast<int16_t>(i);

    for(int j = 0; j != ncols; ++j)
    {
// write col-id, row-id, time-id
      int16_t col = static_cast<int16_t>(j);
 
      f.write(reinterpret_cast<char*>(&col), sizeof(int16_t));
      f.write(reinterpret_cast<char*>(&row), sizeof(int16_t));
      f.write(reinterpret_cast<char*>(&t), sizeof(int16_t));

// write band data
      for(int k = 0;  k != nbands; ++k)
      {
        f.write(reinterpret_cast<char*>(buffer_marks[k]), pixel_size_bands[k]);
        buffer_marks[k] += pixel_size_bands[k];
      }
    }
  }
  
  f.close();
  
  if(args.verbose)
    std::cout << "OK!" << std::endl;
}

