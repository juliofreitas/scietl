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

    required_arguments = parser.add_argument_group("Required Arguments")

    required_arguments.add_argument("-d", "--directory",
                                    help="Source directory with the fire spot data",
                                    required=True)
    required_arguments.add_argument("-o", "--outdir",
                                    help="Temporary directory for converting TIFF files into SciDB binary data",
                                    required=True)
    required_arguments.add_argument("-p", "--product",
                                    help="The type of firespot product: 'm' for monthly or 'd' for daily",
                                    required=True)

    args = parser.parse_args()

    source_dir = args.directory

    output_dir = args.outdir

    product = args.product

    fire_spot_files = os.popen("find {0} -name *.tif | sort".format(source_dir)).read().split('\n')

    fire_spot_files.remove('')

    for fire_file in fire_spot_files:

        input_file_dir, input_file_name = os.path.split(fire_file)

        outfile_name = os.path.join(output_dir, input_file_name.replace(".tif", ".scidb"))

        time_point = extract_time_point_from_monthly_data(input_file_name) if product == "m" else extract_time_point_from_daily_data(input_file_name)

        focos2scidb_cmd = "focos2scidb --f {0} --o {1} --t {2}".format(fire_file, outfile_name, time_point[2])

        #print(focos2scidb_cmd)

        retcode = subprocess.call(focos2scidb_cmd, shell=True)

        if retcode != 0:
            print("Error converting file '{0}' to {1}.".format(fire_file, outfile_name))
            exit(1);
