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
monthly_start_date = "2000-01";
daily_start_date = "2014-01-01";
create_1d_array_cmd = "iquery -naq \"CREATE ARRAY fire_risk_1d_tmp <col_id:int16, row_id:int16, time_id:int16, v:uint16> [i=0:*,1410001];\""
tmp_array_1d = "fire_risk_1d_tmp"
tmp_array_data_format = "'(int16, int16, int16, uint16)'"
array_3d_montlhy_name = "fire_risk_montlhy"
array_3d_daily_name = "fire_risk_daily"


def compute_monthly_time_index(year, month, initial_year, initial_month):
    """Compute..."""

    dyear = year - initial_year;

    dmonth = month if dyear == 0 else month - initial_month

    time_index = 12 * dyear + dmonth

    return time_index


def extract_time_point_from_monthly_data(file_name):
    """Compute..."""

    if len(file_name) < 7:
        print("Invalid file format: '{0}'.\nCould not extract date information!".format(file_name))
        exit(1)

    year = int(file_name[0:4])
    month = int(file_name[5:7])

    time_index = compute_monthly_time_index(year, month, int(monthly_start_date[0:4]), int(monthly_start_date[5:7]))

    return time_index


def extract_time_point_from_daily_data(file_name):
    """Compute..."""

    if len(file_name) < 8:
        print("Invalid file format: '{0}'.\nCould not extract date information!".format(file_name))
        exit(1)

    year = int(file_name[0:4])
    month = int(file_name[4:6])
    day = int(file_name[6:8])

    iyear = int(daily_start_date[0:4])
    imonth = int(daily_start_date[5:7])
    iday = int(daily_start_date[8:10])

    time_delta = datetime.date(year, month, day) - datetime.date(iyear, imonth, iday)

    time_index = time_delta.days()

    return time_index


if __name__ == '__main__':

#
# Parse command line options
#
    parser = argparse.ArgumentParser(description="Load Fire Spot data to SciDB")

    required_arguments = parser.add_argument_group("Required Arguments")

    required_arguments.add_argument("-d", "--directory",
                                    help="Source directory with the fire spot data",
                                    required=True)

    required_arguments.add_argument("-o", "--outdir",
                                    help="Temporary directory for converting TIFF files into SciDB binary data",
                                    required=True)

    args = parser.parse_args()

    source_dir = args.directory

    output_dir = args.outdir

#
# Search for input risk-fire files
#
    fire_spot_files = os.popen("find {0} -name *.tif | sort".format(source_dir)).read().split('\n')

    fire_spot_files.remove('')

#
# For each file we have found:
# - let's check if its name is valid
# - let's find if it is a monthly or daily data
# - convert it to SciDB binary format
# - load converted data to a 1D temporary array
# - transform and insert 1D array into final 3D array
# - remove temporary 1D array
#
    print("Converting risk-fire data...")

    for fire_file in fire_spot_files:

        input_file_dir, input_file_name = os.path.split(fire_file)

        match_montly = re.match(r"[0-9]{4}_[0-9]{2}", input_file_name)

        match_daily = re.match(r"[0-9]{8}", input_file_name)

        if(not match_montly and not match_daily):
            print("Error: file '{0}' is not montly nor daily focos data!".format(fire_file))
            exit(1)

        outfile_name = os.path.join(output_dir, input_file_name.replace(".tif", ".scidb"))

        time_index = extract_time_point_from_monthly_data(input_file_name) if match_montly else extract_time_point_from_daily_data(input_file_name)

        focos2scidb_cmd = "focos2scidb --f {0} --o {1} --t {2} --verbose".format(fire_file, outfile_name, time_index)

        retcode = subprocess.call(focos2scidb_cmd, shell=True)

        if retcode != 0:
            print("Error converting file '{0}' to {1}.".format(fire_file, outfile_name))
            exit(1);

        retcode = subprocess.call(create_1d_array_cmd, shell=True)

        if retcode != 0:
            print("Error creating temporary 1D array: '{0}'.".format(create_1d_array_cmd))
            exit(1);

        load_data_in_1d_array_cmd = "iquery -naq \"load({0}, {1}, -2, {2});\"".format(tmp_array_1d, outfile_name, tmp_array_data_format)

        retcode = subprocess.call(load_data_in_1d_array_cmd, shell=True)

        if retcode != 0:
            print("Error loading file '{0}' to array 1D '{1}'.".format(outfile_name, tmp_array_1d))
            exit(1);

        array_3d = array_3d_montlhy_name if match_montly else array_3d_daily_name

        load_data_in_3d_array_cmd = "iquery -naq \"insert(redimension(apply({3}, col, int64(col_id), row, int64(row_id), time_idx, int64(time_id), value, v), {1}), {0});\"".format(array_3d, array_3d, tmp_array_1d)

        retcode = subprocess.call(load_data_in_3d_array_cmd, shell=True)

        if retcode != 0:
            print("Error converting 1D array '{0}' to 3D array '{1}'.".format(tmp_array_1d, array_3d))
            exit(1);

        drop_temp_1d_array_cmd = "iquery -naq \"remove({0});\"".format(tmp_array_1d)

        retcode = subprocess.call(drop_temp_1d_array_cmd, shell=True)

        if retcode != 0:
            print("Error dropping 1D array '{0}'.".format(tmp_array_1d))
            exit(1);

    print("Converting risk-fire data... finished!")
