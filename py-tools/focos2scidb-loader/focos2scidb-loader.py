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
#  Authors: Raphael Willian da Costa (raphael.costa@dpi.inpe.br)
#           Gilberto Ribeiro de Queiroz (gribeiro@dpi.inpe.br)
#
#  Description: Load fire spots data to SciDB.
#

import argparse
import os
import subprocess

#
# change this for fine tuning
#
scidb_cluster_name = "focos"
monthly_start_date = "2000-01-01";
daily_start_date = "2014-01-01";

def extract_time_point_from_monthly_data(file_name):
    year = file_name[0:4]
    month = file_name[5:7]
    day = "01"

    return year, month, day

def extract_time_point_from_daily_data(file_name):
    year = file_name[0:4]
    month = file_name[4:6]
    day = file_name[6:8]

    return year, month, day


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Load Fire Spot data to SciDB")
    parser.add_argument("--d", help="Source directory with the fire spot data")
    parser.add_argument("--k", help="Kind of fire spot data: 'm' for monthly or 'd' for daily")

    args = parser.parse_args()

    source_dir = args.d
    dataset_type = args.k

    fire_spot_files = os.popen("find {0} -name *.tif | sort".format(source_dir)).read().split('\n')

    fire_spot_files.remove('')

    for fire_file in fire_spot_files:

        file_dir, file_name = os.path.split(fire_file)

        time_point = extract_time_point_from_monthly_data(file_name) if dataset_type == "m" else extract_time_point_from_daily_data(file_name)

        
