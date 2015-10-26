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
  \file scietl/srtm2scidb/main.cpp

  \brief SRTM to SciDB multidimensional array conversion tool.

  \author Ricardo Cartaxo Modesto de Souza
  \author Eduardo Llapa Rodriguez
 */
 
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

int main(int argc, char **argv)
{
  GDALAllRegister();

// let's buffer the data
  std::cout << "\tbuffering data... " << std::endl;

  int64_t ncols = 0;
  int64_t nrows = 0;

  GDALDatasetH dataset = GDALOpen(argv[1], GA_ReadOnly);
    
    if(dataset == 0)
    {
      std::cout << "\tCould not open " << argv[1] << std::endl;
      return 1;
    }
    
    GDALRasterBandH band = GDALGetRasterBand(dataset, 1);

    if(band == 0)
    {
      GDALClose(dataset);
      std::cout << "\nCould not access data in " << argv[1] << std::endl;
      return 1;
    }

    ncols = GDALGetRasterBandXSize(band);
    nrows = GDALGetRasterBandYSize(band);
    std::cout << "\tnrows = " << nrows << std::endl;

    GDALDataType pixel_type = GDALGetRasterDataType(band);

    int16_t* buffer = new int16_t[ncols * nrows];
    
    CPLErr result = GDALRasterIO(band, GF_Read, 0, 0, static_cast<int>(ncols), static_cast<int>(nrows), buffer, static_cast<int>(ncols), static_cast<int>(nrows), pixel_type, 0, 0);

    GDALClose(dataset);
    if(result == CE_Failure)
    {
      std::cout << "\nCould not read data input file " << argv[1] << std::endl;
      return 1;
    }

// lets decode the input file tile information NnnWwww.hgt

  char e[2],n[2];
  int64_t ie,in;
    int64_t inorthing;              //!< Northing identifier (-90 to 89).
    int64_t ieasting;                //!< Easting identifier (-180 t0 179).

    boost::filesystem::path p(argv[1]);
  sscanf (p.filename().c_str(),"%1s%2ld%1s%3ld",n,&in,e,&ie);
  inorthing = n[0] == 'N' ? in : -in;
  ieasting = e[0] == 'E' ? ie : -ie;

  int64_t tile_h = ieasting+180;
  int64_t tile_v = inorthing+90;
  
  int64_t offset_h = tile_h * (ncols-1);
  int64_t offset_v = tile_v * (nrows-1);

    std::cout << "\ttile_h = " << tile_h << std::endl;
    std::cout << "\ttile_v = " << tile_v << std::endl;
    std::cout << "\toffset_h = " << offset_h << std::endl;
    std::cout << "\toffset_v = " << offset_v << std::endl;

// lets write the output to a SciDB binary file
  std::string target_file_name = std::string(argv[2]);
  FILE* f = fopen(target_file_name.c_str(), "w+b");
  
  if(f == 0)
  {
      std::cout << "\nCould not open output file " << target_file_name << std::endl;
      return 1;
  }

  for(int64_t i = 0; i != nrows-1; ++i)
  {
    int64_t gi =  offset_v + i;

    for(int64_t j = 0; j != ncols-1; ++j)
    {
      int64_t gj = offset_h + j; 
        int64_t idx = gj + gi ;
      fwrite(&gj, sizeof(unsigned char), sizeof(int64_t), f);
      fwrite(&gi, sizeof(unsigned char), sizeof(int64_t), f);
      fwrite(&buffer[(ncols-1-i)*nrows+j], sizeof(int16_t), 1, f);
    }
  }

  fclose(f);
}

