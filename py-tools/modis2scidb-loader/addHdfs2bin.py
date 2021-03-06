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
# Author: Alber Sanchez
#
import os
import sys
import argparse
from pyhdf.SD import SD
from pyhdf.SD import SDC
from array import array
import datetime
import logging

#********************************************************
# UTIL
#********************************************************

def isLeapYear(year):
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

def doy2date(yyyydoy):
    '''Returns an int array year-month-day (e.g [2001, 1, 1]) out of the given year-day-of-the-year (e.g 2001001)'''
    if len(str(yyyydoy)) == 7:
        year = int(str(yyyydoy)[:4])
        doy = int(str(yyyydoy)[4:])
        if doy > 0 and doy < 367:
            firstdayRegular = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
            firstdayLeap = [1, 32, 61, 92, 122, 153, 183, 214, 245, 275, 306, 336, 367]
            if isLeapYear(year):
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

def date2grid(dateDOY, period, startyear):
    '''Return an time index (timid) from the input date (MODIS DOY) and time period (e.g 8 days). '''
    res = -1
    year = int(dateDOY[0:4])
    doy = int(dateDOY[4:7])
    ppy = int(365 / period) + 1 # Periods per year
    if(period > 0 and (doy - 1) % period == 0):
        idd = (doy - 1) / period
        idy = (year - startyear) * ppy
        res = idy + idd
    else:
        logging.error("date2grid: Invalid date")
    return res

def getHV(tile):
    '''Returns the h and v components (i.e ['08', '10']) from the given tile id. Use map to get int instead of strings. results = map(int, results)'''
    h = tile[1:3]
    v = tile[4:6]
    return [h, v]

def tile2grid(tile, resolution):
    '''Return the indexes (lonid, latid) of the upper left pixel of the image on the given tile'''
    hv = map(int, getHV(tile))
    h = hv[0]
    v = hv[1]
    lonid = h * resolution
    latid = v * resolution
    return {'lonid':lonid, 'latid':latid}

def addHdf2bin(hdfFilepath, bfpath, period, startyear, lineMin, lineMax, sampMin, sampMax):
    '''Adds an HDF to a binary file and return its path'''


    # Dictionary used to convert from a numeric data type to its symbolic representation - http://pysclint.sourceforge.net/pyhdf/pyhdf.SD.html
    typeTab = {
        SDC.CHAR:    'CHAR',
        SDC.CHAR8:   'CHAR8',
        SDC.UCHAR8:  'UCHAR8',
        SDC.INT8:    'INT8',
        SDC.UINT8:   'UINT8',
        SDC.INT16:   'INT16',
        SDC.UINT16:  'UINT16',
        SDC.INT32:   'INT32',
        SDC.UINT32:  'UINT32',
        SDC.FLOAT32: 'FLOAT32',
        SDC.FLOAT64: 'FLOAT64'
    }

    #TODO:Not yet tested to work with SciDB: CHAR, CHAR8, UCHAR8, INT8, UINT8, INT32, UINT32, FLOAT32, FLOAT64
    typeTab2 = {
        'CHAR': 'c',
        'CHAR8': 'b',
        'UCHAR8': 'B',
        'INT8': 'h',
        'UINT8': 'H',
        'INT16': 'h',
        'UINT16': 'H',
        'INT32': 'l',
        'UINT32': 'L',
        'FLOAT32': 'f',
        'FLOAT64': 'd'
    }    

    try:
        path, filename = os.path.split(hdfFilepath)
        hdf = SD(hdfFilepath, SDC.READ)
        ds = hdf.datasets()
        banddict = {} # band values
        banddatatype = {}
        bandindex = {}# band index in the file
        bandres = {} # band resolution e.g. (4800, 4800)
        for k in ds.keys():
            banddict[k] = hdf.select(k)
            banddatatype[k] = typeTab2[typeTab[ds[k][2]]]
            bandindex[ds[k][3]] = k
            bandres[k] = ds[k][1]
        sortedbandindexkeys = sorted(bandindex.keys())
        #Get the temporal index
        dateDOY = filename[9:16]
        timid = date2grid(dateDOY, period, startyear)
        #Get the spatial indexes
        tile = filename[17:23]
        #Test: All the bands have the same resolution
        resolution = 0
        firsttime = True
        for k in bandres:
            if bandres[k][0] != bandres[k][1]:
                raise Exception('Band resolution mismatch')
            if firsttime:
                firsttime = False
                resolution = bandres[k][0]
        llid = tile2grid(tile, resolution)
        deltalonid = llid['lonid']
        deltalatid = llid['latid']
        bfile = open(bfpath, "ab")
        for i in range(lineMin, lineMax + 1):
            rowdict = {}
            for k in banddict.keys():
                rowdict[k] = banddict[k][i, ]
            latid = deltalatid + i
            for j in range(sampMin, sampMax + 1):
                lonid = deltalonid + j
                idx = [lonid + (latid * pow(10, 6)) +  (timid * pow(10, 11))]# Encodes the indexes in a single value
                idxa = array('L', idx)
                #print str(lonid) + " "  + str(latid) + " " + str(timid) + " " + str(idx)
                idxa.tofile(bfile) # Writes the coordinates to the file
                #Get values
                for k in sortedbandindexkeys:
                    bandname = bandindex[k]
                    val = [rowdict[bandname][j]]
                    vala = array(banddatatype[bandname], val)
                    vala.tofile(bfile) # Writes the band value to the file
        bfile.close()
    except IOError as e:
        logging.exception("IOError:\n" + str(e.message) + " " + hdfFilepath)
    except:
        e = sys.exc_info()[0]
        logging.exception("Unknown exception:\n" + str(e.message) + " " + hdfFilepath)
    return bfpath


#********************************************************
#WORKER
#********************************************************
def main(argv):
    t0 = datetime.datetime.now()
    parser = argparse.ArgumentParser(description = "Add pixels from an HDF file to a SCIDB's binary file")
    parser.add_argument("hdfFilepaths", help = "Path to the HDF files (separated by ';') or to the folder containing them")
    parser.add_argument("binaryFilepath", help = "Path to the (new or existing) binary file for storing the results. Use .sdbbin as file extension")
    parser.add_argument("-lmin", "--lineMin", help = "HDF start row. Default = 0", type = int, default = 0)
    parser.add_argument("-lmax", "--lineMax", help = "HDF end row. Default = 4799", type = int, default = 4799)
    parser.add_argument("-smin", "--sampMin", help = "HDF start column. Default = 0", type = int, default = 0)
    parser.add_argument("-smax", "--sampMax", help = "HDF end column. Default = 4799", type = int, default = 4799)
    parser.add_argument("-r", "--resolution", help = "Number of pixel in a HDF; usually 4800 x 4800. Default = 4800", type = int, default = 4800)
    parser.add_argument("-p", "--period", help = "Time period between HDFs. i.e 8 means the time index starts at 0 for the image of January 1st of 2000", type = int, default = 16)
    parser.add_argument("-s", "--startyear", help = "Starting year of the time index", type = int, default = 2000)
    parser.add_argument("--log", help = "Log level", default = 'WARNING')
    #Get paramters
    args = parser.parse_args()
    hdfFilepaths = args.hdfFilepaths
    binaryFilepath = args.binaryFilepath
    period = args.period
    startyear = args.startyear
    resolution = args.resolution
    lineMin = args.lineMin
    lineMax = args.lineMax
    sampMin = args.sampMin
    sampMax = args.sampMax
    log = args.log
    ####################################################
    # CONFIG
    ####################################################
    numeric_loglevel = getattr(logging, log.upper(), None)
    if not isinstance(numeric_loglevel, int):
        raise ValueError('Invalid log level: %s' % log)
    logging.basicConfig(filename = 'log_addHdfs2bin.log', level = numeric_loglevel, format = '%(asctime)s %(levelname)s: %(message)s')
    logging.info("addHdfs2bin: " + str(args))
    #
    #period = 8 # An image each 8 days
    #startyear = 2000 # The time index starts at 0 for the image taken January 1st of 2000. It increases by 1 every week
    #resolution = 4800 # A  Modis image has 4800 x 4800 pixels
    ####################################################
    # SCRIPT
    ####################################################
    hpaths = hdfFilepaths.split(';')
    #print "Adding HDFs to binary file..."
    hdfcount = 0
    for hp in hpaths:
        if os.path.isfile(hp):
            if hp.endswith('.hdf'):
                #print hp + ' ...'
                tmp = addHdf2bin(hp, binaryFilepath, period, startyear, lineMin, lineMax, sampMin, sampMax)
                logging.info('HDF: ' + hp + ' added to: ' + binaryFilepath)
                hdfcount += 1
            else:
                logging.warning('Unknown file type: ' + hp)
        elif os.path.isdir(hp):
            for (dirpath, dirnames, filenames) in os.walk(hp):
                for fn in filenames:
                    if fn.endswith('.hdf'):
                        #print dirpath + '/' + fn + ' ...'
                        tmp = addHdf2bin(dirpath + '/' + fn, binaryFilepath, period, startyear, lineMin, lineMax, sampMin, sampMax)
                        logging.info('HDF: ' + hp + ' added to: ' + binaryFilepath)
                        hdfcount += 1
                    else:
                        logging.warning('Unknown file type: ' + fn)
                break
    t1 = datetime.datetime.now()    
    tt = t1 - t0
    logging.info("Number of HDFs added: " + str(hdfcount) + " in " + str(tt))

if __name__ == "__main__":
   main(sys.argv[1:])
