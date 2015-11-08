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

from subprocess import call, CalledProcessError
import sys
import argparse
import os
import datetime
import logging
import json
sys.path.append(os.path.join('/opt/scidb/14.12', 'lib'))
import scidbapi

DATABASE_NAME = "modis_metadata"
TABLE_LOG_NAME = "logs_hdfs"
TABLE_MODIS_NAME = "modis"
CURRENT_DIR = os.getcwd()
CONT = 0


def process_data_types(schema):
    '''Return the data types from each field in an array schema'''
    datatypes = []
    for s in schema[1:schema.find('>')].split(','):
        ss = s.strip()
        datatypes.append(ss[ss.index(':') + 1:len(ss)])
    return ', '.join(datatypes)


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


def doy2date(yyyydoy):
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


def date2grid(dateDOY, period, startyear, startday):
    '''Return an time index (timid) from the input date (MODIS DOY) and time period (e.g 8 days). '''
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


def list_hdfs_from_dir(path):
    return os.popen("find {0} -name *.hdf | sort".format(path)).read().split('\n')


def get_hdf_from_server(hdfname, product):
    concated_date = hdfname[len(product)+2:len(product)+9]
    date = ".".join([str(intdate) for intdate in doy2date(concated_date)])
    hv = hdfname.split('.')[2]
    wget = "wget -r -nd -np -nc -l1 -A *{0}*.hdf -R 'xml' e4ftl01.cr.usgs.gov/MOLT/{1}.005/{2}".format(hv, product, date)
    print(wget)
    # output = os.popen("php5 getHDF.php {}".format(args.product)).read()
    # command = filter(None, output.split("\n"))[0]
    # wget = command[command.find('wget'):]
    # for wget in wgets:
        # date_hdf = wget[wget.find("usgs.gov")+19+len(product):].replace(" ", "").replace("&", "").split('.')
        # day_of_year = str(datetime.date(int(date_hdf[0]), int(date_hdf[1]), int(date_hdf[2])).timetuple().tm_yday)
    return ""


def hdf_to_bin(hdffile, product, config_loader, modis_id):
    global CONT
    period = config_loader.get('period')
    startday = config_loader.get('start_date')
    hdf_dir, filename = os.path.split(hdffile)
    if not os.path.isfile(hdffile):
        print("HDF {0} does not exists.".format(filename))
        return ""
    yyyydoy = filename.split('.')[1][1:]
    timeid = date2grid(yyyydoy, period, int(startday[:4]), int(startday[4:]))
    if timeid == -1:
        print("Invalid timeid: Day(JSON) {0}, Day(HDF) {1} - Result: {2}".format(startday, yyyydoy, timeid))
        return False
    command = ""
    date = "-".join([str(intdate) for intdate in doy2date(int(yyyydoy))])

    try:
        call("rm *.bin", shell=True)
        initial = datetime.datetime.now()
        call("modis2scidb --f {0} --o {1} --b '{2}' --t {3} --verbose".format(
            hdffile, os.path.join(CURRENT_DIR, filename.replace('.hdf', '.bin')), config_loader['bands'], timeid), shell=True)
        bin_time = datetime.datetime.now() - initial
        print("DONE to generate binary {0}".format(bin_time))
        logger.info("binary,{0},{1},{2}".format(filename, bin_time, CONT))
        print("Creating temp array {0}_1D".format(product))
        command = "CREATE ARRAY {0}{1}".format("{0}{1}".format(product, "_1D"), config_loader["1d"])

        create = CONNECTION_SCIDB.executeQuery(command)
        CONNECTION_SCIDB.completeQuery(create.queryID)
        print("Done")

        schema = process_data_types(config_loader["1d"])
        print("Loading to 1D array....")

        load_one = CONNECTION_SCIDB.executeQuery("load({0}_1D, \'{1}\', -2, \'({2})\', 0, shadowArray)".format(
            product, os.path.join(CURRENT_DIR, filename.replace('.hdf', '.bin')), schema))

        CONNECTION_SCIDB.completeQuery(load_one.queryID)

        array1D_time = datetime.datetime.now() - (bin_time+initial)
        print("Done to load 1D. - {0} \nRedimension to 3D array...".format(array1D_time))
        logger.info("load1D,{0},{1},{2}".format(filename, array1D_time, CONT))
        command = """
            insert(
                redimension(
                    apply({0}_1D,col_id, int64(lltid - floor(lltid/pow(10,11)) * pow(10,11) - floor((lltid - (floor(lltid/pow(10,11)) * pow(10,11)))/pow(10,6)) * pow(10,6)), row_id, int64(floor((lltid - (floor(lltid/pow(10,11)) * pow(10,11)))/pow(10,6))),time_id, int64(floor(lltid/pow(10,11)))), {1}
                ),
                {2}
            )
        """.format(product, product, product)

        redimension_query = CONNECTION_SCIDB.executeQuery(command)
        CONNECTION_SCIDB.completeQuery(redimension_query.queryID)

        redimension_time = datetime.datetime.now() - (bin_time+initial+array1D_time)
        print("Done redimension. - {0}".format(redimension_time))
        logger.info("redimension,{0},{1},{2}".format(filename, redimension_time, CONT))
        CONT += 1
        print("Removing {0}_1D, shadowArray..".format(product))
        remove_query1D = CONNECTION_SCIDB.executeQuery("remove({0}_1D)".format(product))
        CONNECTION_SCIDB.completeQuery(remove_query1D.queryID)
        removE_queryShadow = CONNECTION_SCIDB.executeQuery("remove(shadowArray)".format(product))
        CONNECTION_SCIDB.completeQuery(removE_queryShadow.queryID)

        total_final = datetime.datetime.now()
        final = total_final - initial
        print("Final Time: {0}".format(final))
        logger.info("final,{0},{1},{2}".format(filename, final, CONT))
        print("HDFs completed: {0}\n\n".format(CONT))

    except CalledProcessError as error:
        print("CalledProcessError: {0} - {1}".format(command, error))
        exit(1)
    except ValueError as error:
        print("ValueError: {0} - {1}".format(command, error))
        exit(1)
    except OSError as error:
        print("OSError: {0} - {1}".format(command, error))
        exit(1)
    except IndexError as error:
        print("SciDBError IndexError: {0}".format(error.message))
        exit(1)
    except:
        error = sys.exc_info()[0]
        print(error)
        logger.exception("Exception error: {0} - {1}".format(command, error))
        exit(1)
    cursor.close()


def prepare_to_upload(config_loader):
    geo_array = config_loader['geo_array']
    product = config_loader['product']
    hdffiles = os.popen("find {0} -name *.hdf | sort".format(config_loader['hdf_path'])).read().split('\n')
    hdffiles.remove('')
    print("{0} HDFs to upload.".format(len(hdffiles)))
    invalid_hdfs = set([h for h in hdffiles if not os.path.split(h)[1].startswith(product.upper())])
    if invalid_hdfs:
        print("Found {0} invalid hdf files to modis product. To be ignored: ".format(len(invalid_hdfs)))
        for invalid in invalid_hdfs:
            print("\tSkipping {0}".format(invalid))
        hdffiles = list(set(hdffiles) - invalid_hdfs)
    cursor = CONNECTION.cursor()
    modis_detail = get_modis_details(geo_array)
    print(modis_detail)
    if modis_detail is None:
        raise ValueError("{0} is empty in database. Query returned {1}".format(geo_array, modis_detail))
    if not config_loader.get('bands', ''):
        raise ValueError("bands are invalids or undefined. Returned {0}".format(config_loader.get('bands', '')))
    if not config_loader.get('1d', ''):
        raise ValueError("geo_array 1d invalid or undefined. Returned {0}".format(config_loader.get('1d', '')))
    for hdf in hdffiles:
        hdf_dir, filename = os.path.split(hdf)
        if CONNECTION.status == STATUS_IN_TRANSACTION:
            try:
                CONNECTION.commit()
            except:
                CONNECTION.rollback()
        cursor.execute("SELECT * FROM geo_array_data_files WHERE array_id = {0} AND data_file = '{1}'".format(modis_detail[0], filename))
        if cursor.fetchone():
            print("\tSkipping {0}: Already uploaded.".format(hdf))
        else:
            hdf_to_bin(hdf, geo_array, configs['load'], modis_detail[0])
            # hdf_to_bin(hdf, product, configs['load'].get('period', 16), configs['load']['start_date'], modis_detail[0])
    call("rm *.bin", shell=True)
    cursor.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Upload to scidb")
    parser.add_argument("config", help="Put the JSON config of postgres and MODIS")
    args = parser.parse_args()

    try:
        with open('{0}'.format(args.config)) as file:
            configs = json.loads(file.read())
        psql_params = configs.get('pg', '')
        CONNECTION = psycopg2.connect(**psql_params)
        CONNECTION_SCIDB = scidbapi.connect("localhost", 1239)
    except IOError as error:
        print("IOError: Cannot open filename: {0}".format(error.message))
        exit(2)
    except psycopg2.Error as error:
        print("Error: {0}".format(error.message))
        exit(3)
    except IndexError as error:
        print("IndexError: {0}".format(error.message))
        exit(3)
    if configs['load'].get('geo_array', '') not in [geo_array[0] for geo_array in list_all_geo_arrays()]:
        raise ValueError("{0} not valid MODIS product.".format(configs['load'].get('geo_array', '')))
    if not os.path.isdir(configs['load']['hdf_path']):
        raise AttributeError("{0} not a valid directory or does not exist.".format(configs['load']['hdf_path']))

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if not os.path.exists(os.path.join(CURRENT_DIR, "logs")):
        try:
            os.makedirs(os.path.join(CURRENT_DIR, "logs"))
        except OSError as oserror:
            print("OSError: {0}".format(oserror.message))
            exit(2)

    log_file = '{0}.log'.format(os.path.join(os.path.join(CURRENT_DIR, "logs"), configs['load']['geo_array']))
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    program_start = datetime.datetime.now()
    prepare_to_upload(configs['load'])
    CONNECTION.close()
    CONNECTION_SCIDB.disconnect()
    program_close = datetime.datetime.now() - program_start
    logger.info("total_to_upload,{0}".format(program_close))



