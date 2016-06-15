#!/usr/bin/python
#
#  Copyright (C) 2016 National Institute For Space Research (INPE) - Brazil.
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
#  Authors: Gilberto Ribeiro de Queiroz (gribeiro@dpi.inpe.br)
#           Raphael Willian da Costa (raphael.costa@dpi.inpe.br)
#
#  Description: Load fire spots data to SciDB.
#

import argparse
import datetime
import os
import re
import subprocess

#
# change this for fine tuning
#
scidb_cluster_name = "focos"

geo_arrays = {
  "hotspot_daily": {
        "file_extension": "tif",
        "start_date": "2014-01-01",
        "create_1d_array_cmd": "iquery -naq \"CREATE ARRAY hotspot_daily_1d_tmp <col:int16, row:int16, time_idx:int16, measure:uint8> [i=0:1410000,1410001,0];\"",
        "tmp_array_1d": "hotspot_daily_1d_tmp",
        "tmp_array_data_format": "'(int16, int16, int16, uint8)'",
        "array_3d": "hotspot_daily"
  },
  "hotspot_monthly": {
        "file_extension": "tif",
        "start_date": "2000-01",
        "create_1d_array_cmd": "iquery -naq \"CREATE ARRAY hotspot_monthly_1d_tmp <col:int16, row:int16, time_idx:int16, measure:uint8> [i=0:1410000,1410001,0];\"",
        "tmp_array_1d": "hotspot_monthly_1d_tmp",
        "tmp_array_data_format": "'(int16, int16, int16, uint8)'",
        "array_3d": "hotspot_monthly"
  },
  "hotspot_risk_daily": {
        "file_extension": "env",
        "start_date": "2015-12-01",
        "create_1d_array_cmd": "iquery -naq \"CREATE ARRAY hotspot_risk_daily_1d_tmp <col:int16, row:int16, time_idx:int16, measure:uint8> [i=0:29889971,29889972,0];\"",
        "tmp_array_1d": "hotspot_risk_daily_1d_tmp",
        "tmp_array_data_format": "'(int16, int16, int16, uint8)'",
        "array_3d": "hotspot_risk_daily"
  },
  "hotspot_risk_monthly": {
        "file_extension": "tif",
        "start_date": "2015-01",
        "create_1d_array_cmd": "iquery -naq \"CREATE ARRAY hotspot_risk_monthly_1d_tmp <col:int16, row:int16, time_idx:int16, high_risk:uint8, medium_risk:uint8, low_risk:uint8> [i=0:34979999,34980000,0];\"",
        "tmp_array_1d": "hotspot_risk_monthly_1d_tmp",
        "tmp_array_data_format": "'(int16, int16, int16, uint8, uint8, uint8)'",
        "array_3d": "hotspot_risk_monthly"
  }
}

def compute_monthly_time_index(year, month, initial_year):
    """Compute the time index for a monthly file.
       Time index start at 1 for initial_year."""

    dyear = year - initial_year;

    time_index = 12 * dyear + month

    return time_index


def compute_daily_time_index(year, month, day, initial_date):
    """Compute the time index for a daily file.
       Time index start at 1 for initial day."""

    iyear = int(initial_date[0:4])
    imonth = int(initial_date[5:7])
    iday = int(initial_date[8:10])

    time_delta = datetime.date(year, month, day) - datetime.date(iyear, imonth, iday)

    time_index = time_delta.days + 1

    return time_index


def extract_time_point_from_file_name(file_name, initial_date):
    """Given a file name, extracts the date part and
       compute a time point from a initial date"""

# is date format yyyymmdd?
    d = re.search('[0-9]{8}', file_name)

    if d is not None:
        year = int(d.group(0)[0:4])
        month = int(d.group(0)[4:6])
        day = int(d.group(0)[6:8])

        return compute_daily_time_index(year, month, day, initial_date)

# is date format yyyy-mm-dd or yyyy_mm_dd?
    d = re.search('[0-9]{4}[-|_][0-9]{2}[-|_][0-9]{2}', file_name)

    if d is not None:
        year = int(d.group(0)[0:4])
        month = int(d.group(0)[5:7])
        day = int(d.group(0)[8:10])

        return compute_daily_time_index(year, month, day, initial_date)

# is date format yyyy-mm or yyyy_mm?
    d = re.search('[0-9]{4}[-|_][0-9]{2}', file_name)

    if d is not None:
        year = int(d.group(0)[0:4])
        month = int(d.group(0)[5:7])

        return compute_monthly_time_index(year, month, int(initial_date[0:4]))

    exit(1)

if __name__ == '__main__':

#
# Parse command line options
#
    parser = argparse.ArgumentParser(description="Load Fire Spot data to SciDB")

    required_arguments = parser.add_argument_group("Required Arguments")

    required_arguments.add_argument("-d", "--directory",
                                    help="Source directory with the fire spot data",
                                    required=True)

    required_arguments.add_argument("-p", "--product",
                                help="The data product",
                                required=True)

    required_arguments.add_argument("-o", "--outdir",
                                    help="Temporary directory for converting TIFF files into SciDB binary data",
                                    required=True)

    args = parser.parse_args()

    source_dir = args.directory

    data_product = args.product

    output_dir = args.outdir

    geo_array = geo_arrays[data_product]

    file_extension = geo_array["file_extension"]

#
# Search for input risk-fire files
#
    fire_spot_files = os.popen("find {0} -name *.{1} | sort".format(source_dir, file_extension)).read().split('\n')

    fire_spot_files.remove('')

#
# For each file we have found:
# - let's check if its name is valid
# - let's find if it is a monthly or daily data
# - convert it to SciDB binary format
# - load converted data to a 1D temporary array
# - transform and insert 1D array into final 3D array
# - remove temporary 1D array

    print("Converting risk-fire data...")

    for fire_file in fire_spot_files:

# extrac file name and select chronon
         input_file_dir, input_file_name = os.path.split(fire_file)

         outfile_name = os.path.join(output_dir, input_file_name.replace(".{0}".format(file_extension), ".scidb"))

         time_index = extract_time_point_from_file_name(input_file_name, geo_array["start_date"])

# remove old binary file from target directory
         remove_old_bin_file_cmd = "rm {0}".format(outfile_name)

         retcode = subprocess.call(remove_old_bin_file_cmd, shell=True)

         if retcode == 0:
             print("Old file '{0}' removed. Generating new binary file... ".format(outfile_name))

# convert raster-file to SciDB binary
         focos2scidb_cmd = "fire2scidb --f {0} --o {1} --t {2} --verbose".format(fire_file, outfile_name, time_index)

         retcode = subprocess.call(focos2scidb_cmd, shell=True)

         if retcode != 0:
             print("Error converting file '{0}' to {1}.".format(fire_file, outfile_name))
             exit(1);

# remove old 1D temporary array if any
         drop_temp_1d_array_cmd = "iquery -naq \"remove({0});\"".format(geo_array["tmp_array_1d"])

         subprocess.call(drop_temp_1d_array_cmd, shell=True)

# create temporary 1D array
         retcode = subprocess.call(geo_array["create_1d_array_cmd"], shell=True)

         if retcode != 0:
             print("Error creating temporary 1D array: '{0}'.".format(geo_array["create_1d_array_cmd"]))
             exit(1);

# Load data to 1D temporary array
         load_data_in_1d_array_cmd = "iquery -naq \"load({0}, '{1}', -2, {2});\"".format(geo_array["tmp_array_1d"], outfile_name, geo_array["tmp_array_data_format"])

         retcode = subprocess.call(load_data_in_1d_array_cmd, shell=True)

         if retcode != 0:
             print("Error loading file '{0}' to array 1D '{1}'.".format(outfile_name, tmp_array_1d))
             exit(1);

# Insert data from temporary 1D to 3D
         load_data_in_3d_array_cmd = "iquery -naq \"insert(redimension({2}, {1}), {0});\"".format(geo_array["array_3d"], geo_array["array_3d"], geo_array["tmp_array_1d"])

         retcode = subprocess.call(load_data_in_3d_array_cmd, shell=True)

         if retcode != 0:
             print("Error converting 1D array '{0}' to 3D array '{1}'.".format(geo_array["tmp_array_1d"], geo_array["array_3d"]))
             exit(1);

    print("Converting risk-fire data... finished!")
