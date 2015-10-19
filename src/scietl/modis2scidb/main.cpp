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
  \file scietl/modis2scidb/main.cpp

  \brief MODIS to SciDB multidimensional array conversion tool.

  \author Gilberto Ribeiro de Queiroz
 */

// Modis2SciDB
#include "../Version.hpp"
#include "exception.hpp"
#include "utils.hpp"

// STL
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>

// Boost
#include <boost/filesystem.hpp>
#include <boost/foreach.hpp>
#include <boost/format.hpp>
#include <boost/program_options.hpp>
#include <boost/shared_array.hpp>
#include <boost/timer/timer.hpp>

// GDAL
#include <gdal.h>

//! The list of possible input parameters
struct input_arguments
{
  std::string source_file_name;
  std::string target_file_name;
  std::vector<uint16_t> bands;
  int64_t time_point;
  bool verbose;
};

//! Valid input arguments and throw exceptions if an invalid arg is detected.
void valid_args(input_arguments& args);

//! Convert the files to one of SciDB load formats
void convert(const input_arguments& args);

int main(int argc, char **argv)
{
  GDALAllRegister();

  try
  {
    boost::timer::cpu_timer timer;

    input_arguments parsed_args;

    std::string bands_str;

    boost::program_options::options_description options_all("MODIS to SciDB's Multidimensional Array Conversion Options");

    options_all.add_options()
      ("version", "Prints MODIS to SciDB conversion tool version.\n")
      ("help", "Prints help message.\n")
      ("verbose", "Turns on verbose mode: prints timing and some more information about the conversion progress.\n")
      ("f", boost::program_options::value<std::string>(&parsed_args.source_file_name), "The source HDF file to convert to SciDB's load format.\n")
      ("o", boost::program_options::value<std::string>(&parsed_args.target_file_name), "The target folder to store SciDB data file.\n")
      ("t", boost::program_options::value<int64_t>(&parsed_args.time_point), "The timeline position for the dataset.\n")
      ("b", boost::program_options::value<std::string>(&bands_str), "A list of comma separated spectral bands to extract data, starting from 0: \"3,4\".\n")
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
      std::cout << "\n\nmodis2scidb version: " SCIETL_VERSION_STRING "\n" << std::endl;

      return EXIT_SUCCESS;
    }

    parsed_args.verbose = options.count("verbose") ? true : false;

    parsed_args.bands = modis2scidb::parse_bands(bands_str);

    valid_args(parsed_args);

    if(parsed_args.verbose)
      std::cout << "\nmodis2scidb started\n" << std::endl;

    convert(parsed_args);

    if(parsed_args.verbose)
      std::cout << "\n\nmodis2scidb finished successfully!\n" << std::endl;
  }
  catch(const modis2scidb::exception& e)
  {
    std::cerr << "\n\nmodis2scidb finished with errors!\n";

    if(const std::string* d = boost::get_error_info<modis2scidb::error_description>(e))
      std::cerr << "\nThe following error has occurried: " << *d << "\n";
    
    std::cerr << "\nPlease, use 'modis2scidb --help' for help with input parameters. "
                 "If you find it is a bug, please, report it to gribeiro@dpi.inpe.br.\n"
              << std::endl;
 
    return EXIT_FAILURE;
  }
  catch(const std::exception& e)
  {
    std::cerr << "\n\nmodis2scidb finished with errors!\n";

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
    throw modis2scidb::invalid_arg_value() << modis2scidb::error_description("missing input HDF file name!");

  if(!boost::filesystem::exists(args.source_file_name))
    throw modis2scidb::invalid_dir_error() << modis2scidb::error_description("could not find input HDF file!");
  
  if(args.target_file_name.empty())
    throw modis2scidb::invalid_arg_value() << modis2scidb::error_description("missing output file name!");
  
  if(boost::filesystem::exists(args.target_file_name))
    throw modis2scidb::invalid_arg_value() << modis2scidb::error_description("can not overwrite an existing output file!");
}

void convert(const input_arguments& args)
{
// determine the subdataset pattern name using the first available file
  if(args.verbose)
    std::cout << "\tlooking for the names of subdatasets (or variables)... " << std::flush;
  
  std::vector<std::string> band_names = modis2scidb::extract_subdatasets_pattern_names(args.source_file_name);

  if(args.verbose)
    std::cout << "OK!" << std::endl;
  
// check if band numbers are in the valid range
  if(args.verbose)
    std::cout << "\tchecking the range for choosed band numbers... " << std::flush;
  
  std::size_t num_bands = args.bands.size();
  
  for(std::size_t i = 0; i != num_bands; ++i)
    if(args.bands[i] >= band_names.size())
      throw modis2scidb::invalid_arg_value() << modis2scidb::error_description("band number is invalid!");
  
  if(args.verbose)
    std::cout << "OK!" << std::endl;

// let's buffer each subdataset
  if(args.verbose)
    std::cout << "\tbuffering data... " << std::flush;

  std::vector<boost::shared_array<unsigned char> > data_buffers;
  std::vector<unsigned char*> aux_data_buffers;
  std::vector<std::size_t> band_datatype_size;
  
  int64_t ncols = 0;
  int64_t nrows = 0;

  for(std::size_t i = 0; i != num_bands; ++i)
  {
    if(args.verbose)
      std::cout << "\n\t\tband #" << args.bands[i] << "... " << std::flush;

    boost::format subdataset(band_names[args.bands[i]]);

    subdataset.bind_arg(1, args.source_file_name);
    
    GDALDatasetH dataset = GDALOpen(subdataset.str().c_str(), GA_ReadOnly);
    
    if(dataset == 0)
    {
      boost::format err_msg("could not open subdataset: '%1%', for input hdf file: '%2%'!");
      throw modis2scidb::gdal_error() << modis2scidb::error_description((err_msg % subdataset.str() % args.source_file_name).str());
    }
    
    GDALRasterBandH band = GDALGetRasterBand(dataset, 1);
    
    if(band == 0)
    {
      GDALClose(dataset);
      boost::format err_msg("could not access band: %1%!");
      throw modis2scidb::gdal_error() << modis2scidb::error_description((err_msg % args.bands[i]).str());
    }
    
    if(i == 0)
    {
      ncols = GDALGetRasterBandXSize(band);
      nrows = GDALGetRasterBandYSize(band);
    }
    else
    {
      if((GDALGetRasterBandXSize(band) != ncols) ||
         (GDALGetRasterBandYSize(band) != nrows))
      {
        GDALClose(dataset);
        throw modis2scidb::gdal_error() << modis2scidb::error_description("selected bands must have the same dimension (rows and cols)!");
      }
    }
    
    GDALDataType pixel_type = GDALGetRasterDataType(band);
    
    std::size_t pixel_size = modis2scidb::num_bytes(pixel_type);
    
    band_datatype_size.push_back(pixel_size);
    
    boost::shared_array<unsigned char> buffer(new unsigned char[ncols * nrows * pixel_size]);
    
    data_buffers.push_back(buffer);
    
    aux_data_buffers.push_back(buffer.get());
    
    CPLErr result = GDALRasterIO(band, GF_Read, 0, 0, static_cast<int>(ncols), static_cast<int>(nrows), buffer.get(), static_cast<int>(ncols), static_cast<int>(nrows), pixel_type, 0, 0);

    if(result == CE_Failure)
    {
      GDALClose(dataset);
      boost::format err_msg("could not read subdataset: '%1%', for input hdf file: '%2%'!");
      throw modis2scidb::gdal_error() << modis2scidb::error_description((err_msg % subdataset.str() % args.source_file_name).str());
    }

    GDALClose(dataset);

    if(args.verbose)
      std::cout << "OK!" << std::flush;
  }

  if(args.verbose)
    std::cout << "\n\tOK!" << std::endl;

// lets write the output to a SciDB binary file
  if(args.verbose)
    std::cout << "\tsaving data... " << std::flush;
  
  boost::filesystem::path input_file(args.source_file_name);

  modis2scidb::modis_file_descriptor file_info = modis2scidb::parse_modis_file_name(input_file.filename().string());

  int64_t tile_h = boost::lexical_cast<int64_t>(file_info.tile.substr(1, 2));
  int64_t tile_v = boost::lexical_cast<int64_t>(file_info.tile.substr(4, 2));
  
  int64_t offset_h = tile_h * ncols;
  int64_t offset_v = tile_v * nrows;

  FILE* f = fopen(args.target_file_name.c_str(), "wb");
  
  if(f == 0)
  {
    boost::format err_msg("could not open output file: '%1%', for write! check if path exists.");
    throw modis2scidb::gdal_error() << modis2scidb::error_description((err_msg % args.target_file_name).str());
  }

  for(int64_t i = 0; i != nrows; ++i)
  {
    int64_t gi =  offset_v + i;

    for(int64_t j = 0; j != ncols; ++j)
    {
      int64_t gj = offset_h + j;
      
      int64_t idx = gj + (gi * 1000000) +  (args.time_point * 100000000000);
      
      fwrite(&idx, sizeof(unsigned char), sizeof(int64_t), f);

      //fwrite(&args.time_point, sizeof(unsigned char), sizeof(int64_t), f);
      //fwrite(&gj, sizeof(unsigned char), sizeof(int64_t), f);
      //fwrite(&gi, sizeof(unsigned char), sizeof(int64_t), f);

      for(std::size_t b = 0; b != num_bands; ++b)
      {
        unsigned char* buffer = aux_data_buffers[b];

        fwrite(buffer, sizeof(unsigned char), band_datatype_size[b], f);

        aux_data_buffers[b] = buffer + band_datatype_size[b];
      }
    }
  }

  fclose(f);
}

