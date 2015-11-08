
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
#  Authors: Raphael Willian da Costa
#           Alber Sanchez
#           Gilberto Ribeiro de Queiroz
#           Ricardo Cartaxo Modesto de Souza
#
#  Description: Load a set of MODIS HDF files to a SciDB array.
#

import argparse
import datetime
import json
import logging
import os
import sys


def process_data_types(schema):
    '''Parse the array scheme and return a comma separated list of data types.'''
    datatypes = []

    attributes = schema[schema.find('<') + 1:schema.find('>')]

    for attr in attributes.split(','):
        attr = attr.strip()
        attr_type = attr[attr.index(':') + 1:len(attr)]
        datatypes.append(attr_type)
    return ', '.join(datatypes)


#x = "<lltid:int64, red:int16, nir:int16, quality:uint16>[k=0:*, 1048576, 0]"
#print(process_data_types(x))

def is_leap_year(year):
    '''Returns TRUE if the given year (int) is leap and FALSE otherwise'''
    leapyear = False
    if year % 4 != 0:
        leapyear = False
    elif year % 100 != 0:
        leapyear = True
    elif year % 400 == 0:
        leapyear = True
    else:
        leapyear = False
    return leapyear

#print(is_leap_year(2000))
#print(is_leap_year(2001))

def day_of_year_to_date(yyyydoy):
    '''Returns an int array year-month-day (e.g [2001, 1, 1]) out of the given year-day-of-the-year (e.g 2001001)'''
    if len(str(yyyydoy)) == 7:
        year = int(str(yyyydoy)[:4])
        doy = int(str(yyyydoy)[4:])
        if doy > 0 and doy < 367:
            firstdayRegular = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
            firstdayLeap = [1, 32, 61, 92, 122, 153, 183, 214, 245, 275, 306, 336, 367]
            if is_leap_year(year):
                firstday = firstdayLeap
            else:
                firstday = firstdayRegular
            for i in range(len(firstday) - 1):
                start = firstday[i]
                end = firstday[i + 1]
                if doy >= start and doy < end:
                    month = i + 1
                    break
            day = doy - firstday[month - 1] + 1
        res = [year, month, day]
    return res

#print(day_of_year_to_date(2001001))
#print(day_of_year_to_date(2001009))
#print(day_of_year_to_date(2001017))
#print(day_of_year_to_date(2001025))
#print(day_of_year_to_date(2001033))

#dateDOY => string
def date2grid(dateDOY, period, startyear, startday):
    '''Return a time index (timid) from the input date (MODIS DOY) and time period (e.g 8 days). '''
    res = -1
    year = int(dateDOY[0:4])
    doy = int(dateDOY[4:7])
    ppy = int(365 / period) + 1  # Periods per year
    if period > 0 and (doy - 1) % period == 0:
        idd = (doy - 1) / period
        idy = (year - startyear) * ppy
        iii = (startday - 1) / period
        res = idy + idd - iii
    else:
        logging.error("date2grid: Invalid date")
    return res


#print(date2grid("2001001", 8, 2001, 1))
#print(date2grid("2001009", 8, 2001, 1))
#print(date2grid("2001017", 8, 2001, 1))
#print(date2grid("2001025", 8, 2001, 1))
#print(date2grid("2001033", 8, 2001, 1))
#print(date2grid("2001033", 8, 2001, 17))

def list_hdfs_from_dir(path):
    return os.popen("find {0} -name *.hdf | sort".format(path)).read().split('\n')

#print(list_hdfs_from_dir("/home/scidb/GeospatialData/MOD09Q1"))



