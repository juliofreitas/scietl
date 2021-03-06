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

#Run as scidb user
import os
import sys
import time
import subprocess as subp
import argparse
import datetime
import logging
import re

#********************************************************
#WORKER
#********************************************************
def main(argv):
    parser = argparse.ArgumentParser(description = "Monitors a folder for SDBBIN files for uploading to SCIDB")
    parser.add_argument("path_to_watch", help = "Folder path")
    parser.add_argument("scriptFolder", help = "Folder containing python scripts")
    parser.add_argument("destArray", help = "3D Array to upload the data to")
    parser.add_argument("product", help = "MODIS product. e.g MOD09Q1")
    parser.add_argument("-t", "--checktime", help = "Waiting time between folder inspections. Default is 60 (seconds)", type = int, default = 60)
    parser.add_argument("--log", help = "Log level", default = 'WARNING')
    #Get paramters
    args = parser.parse_args()
    path_to_watch = args.path_to_watch
    scriptFolder = args.scriptFolder
    destArray = args.destArray
    checktime = args.checktime
    prod = args.product
    log = args.log

    if path_to_watch[-1:] != '/':
        path_to_watch = path_to_watch + '/'
    if scriptFolder[-1:] != '/':
        scriptFolder = scriptFolder + '/'
    ####################################################
    # CONFIG
    ####################################################
    numeric_loglevel = getattr(logging, log.upper(), None)
    if not isinstance(numeric_loglevel, int):
        raise ValueError('Invalid log level: %s' % log)
    logging.basicConfig(filename = 'log_checkFolder.log', level = numeric_loglevel, format = '%(asctime)s %(levelname)s: %(message)s')
    logging.info("checkFolder: " + str(args))
    #
    #checktime = 60 # seconds
    ## GIS-OBAMA
    #path_to_watch = "/mnt/lun0/test/toLoad/"
    #scriptFolder = '/mnt/lun0/test/test013/scripts/'
    # CHRONOS
    #path_to_watch = "/dados/scidb/toLoad/"
    #scriptFolder = '/dados/scidb/scripts/'
    ####################################################
    # SCRIPT
    ####################################################


    sdbInstances = int(subp.check_output("iquery -aq \"list('instances');\" | wc -l", shell=True)) - 3


    cmdprefix = "parallel -j " + str(sdbInstances) + " --no-notice python " + scriptFolder + "load2scidb.py --loadInstance -2 --log " + log + " --product " + prod + " {1} " + destArray + " ::: "
    before = dict ([(f, None) for f in os.listdir (path_to_watch)])
    while 1:
        time.sleep (checktime)
        after = dict ([(f, None) for f in os.listdir (path_to_watch)])
        added = [f for f in after if not f in before]
        if added:
            sdbbinList = []
            for ad in added:
                fileFullPath = path_to_watch + str(ad)
                fileName, fileExtension = os.path.splitext(fileFullPath)
                if(fileExtension == '.sdbbin'):
                    sdbbinList.append(fileFullPath)
            #Call to load2scidb.py
            cmd = cmdprefix + " ".join(sdbbinList)
            try:
                #logging.info("Loading SDBBINs : ", re.escape(str(cmd)))
                subp.check_call(str(cmd), shell=True)
                for f in sdbbinList:
                    #logging.info("Removing SDBBIN : ", re.escape(str(f)))
                    os.remove(f)
            except subp.CalledProcessError as e:
                logging.exception("CalledProcessError: " + str(cmd) + "\n" + str(e.message))
            except ValueError as e:
                logging.exception("ValueError: " + str(cmd) + "\n" + str(e.message))
            except OSError as e:
                logging.exception("OSError: " + str(cmd) + "\n" + str(e.message))
            except:
                e = sys.exc_info()[0]
                logging.exception("Unknown exception: " + str(cmd) + "\n" + str(e.message))
        before = after


if __name__ == "__main__":
   main(sys.argv[1:])
