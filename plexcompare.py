import os
import sys
import getpass
import logging.config
import yaml
import argparse
from pathlib import Path
from datetime import datetime

# app specific modules
from plexinfo import sqlitedb as mydb
from plexinfo import plexutils as myutil
from plexinfo import appconfig as appcfg
from plexapi.myplex import MyPlexAccount

logger = logging.getLogger("PlexCompare")
now = datetime.now()

with open("log.conf", 'rt') as f:
    config = yaml.safe_load(f.read())

logging.config.dictConfig(config)
VERSION = "0.1"


def movieCompare(dbObj, svr1, svr2, args):
    """Compares the movie library (and collections)

    Args:
        dbObj (databse obj): database object to save data to
        svr1 (Plex server connection object): Server1 to compare
        svr2 (Plex server connection object): Server 2 to compare
        args : arguments from the command line parser
    """
    logger.debug(f"Comparison starting for movie library type")
    xlist = ['server1', 'server2']
    for svrNameTag in xlist:
        if svrNameTag == 'server1':
            plexSvrName = args.server1
            xmovLib = svr1.library.section(args.movieLibName)
        else:
            plexSvrName = args.server2
            xmovLib = svr2.library.section(args.movieLibName)

        msg = f"{plexSvrName}: Exporting collection data from movie library : {args.movieLibName}"
        print(msg)
        logger.info(msg)
        myutil.collection2Db(
            dbObj, xmovLib, dbSvrNameTag=svrNameTag, maxItems=int(appcfg.sec_compare.get("collectionmax", 0)))

        msg = f"{plexSvrName}: Exporting movie data from movie library : {args.movieLibName}"
        print(msg)
        logger.info(msg)
        myutil.movieLib2Db(dbObj, xmovLib, svrNameTag,
                           maxItems=int(appcfg.sec_compare.get("moviemax", 0)))

    # Create Collection diff csv file
    csvFilename = f"{args.movieLibName}_collections_{now.strftime('%Y-%m-%d-%H%M')}.csv"
    logger.debug(f"exporting to file: {csvFilename}")
    if args.dirSave == None:
        collectionCSVFile = Path.cwd() / csvFilename
    else:
        collectionCSVFile = Path(args.dirSave) / csvFilename

    logger.debug(f"exporting to file: {collectionCSVFile}")
    msg = f"Creating Collection Diff file {collectionCSVFile}"
    print(msg)
    logger.info(msg)
    dbObj.exportColDiff(collectionCSVFile)

    # Create Movie diff csv file
    csvFilename = f"{args.movieLibName}_library_{now.strftime('%Y-%m-%d-%H%M')}.csv"
    # Path.cwd
    if args.dirSave == None:
        libCSVFile = Path.cwd() / csvFilename
    else:
        libCSVFile = Path(args.dirSave) / csvFilename

    print(f"Creating Movie Library Diff file {libCSVFile}")
    dbObj.exportLibDiff(libCSVFile)


def main(args):
    logger.debug(f"args is {args}")
    logger.debug(f"Checking for config file")

    logger.debug(
        f"PLEXINFO_CONFIG_FILE {os.environ.get('PLEXINFO_CONFIG_FILE')}")
    if os.environ.get('PLEXINFO_CONFIG_FILE') != None:
        cfgFile = Path(os.environ.get('PLEXINFO_CONFIG_FILE'))
    else:
        cfgFile = None

    if cfgFile != None:
        if cfgFile.is_file():
            logger.debug(f"loading config file: {cfgFile}")
            appcfg.loadCfg(cfgFile)
            logger.info(f"Config file loaded: {cfgFile}")
        else:
            logger.debug(f"config file {cfgFile} not found")

    logger.debug(f"Config section [compare]: {appcfg.sec_compare}")
    logger.debug(f"Config section [db]: {appcfg.sec_db}")
    logger.debug(f"Config section [server]: {appcfg.sec_server}")
    logger.debug(f"Config section [paths]: {appcfg.sec_paths}")

    # quit()
    logger.debug(f"getpass from user {args.userName}")
    userPass = getpass.getpass(
        prompt=f"Enter {args.userName}'s Plex Password: ")
    msg = f"Authenticating {args.userName}"
    print(msg)
    logger.info(f"{msg}")
    try:
        plexAcct = MyPlexAccount(args.userName, userPass)
    except Exception as err:
        logger.critical(f"Error:  {err}", exc_info=True)
        sys.exit()

    logger.info(f"username: {args.userName} authenticated.")
    ###################################################
    # Setting up database
    msg = f"Setting up internal database"
    print(msg)
    logger.info(msg)
    if appcfg.sec_db.get('filename') == None:
        dbFile = ":memory:"
        logger.debug(f"No dbfile config setting. dbFile = {dbFile}")
    else:
        dbFile = appcfg.sec_paths['data'] / appcfg.sec_db['filename']
        msg = f"  OVERRIDE: database saving to file: {dbFile}"
        logger.info(msg)
        print(msg)
        if dbFile.exists():
            logger.debug(f"Deleting existing dbfile : {dbFile}")
            dbFile.unlink()

    db1 = mydb.LocalDB(dbLoc=str(dbFile))
    db1.initDB(appcfg.sec_paths['scripts'])
    ############################################################
    # Connecting to Plex Servers
    msg = f"Connecting to servers"
    print(msg)
    logger.info(f"{msg}")
    plexServer1 = myutil.connectPlexServer(plexAcct, args.server1)

    msg = f"  {args.server1} - Connected"
    print(msg)
    logger.info(f"{msg}")

    plexServer2 = myutil.connectPlexServer(plexAcct, args.server2)
    msg = f"  {args.server2} - Connected"
    print(msg)
    logger.info(f"{msg}")
    ############################################################
    # Reporting Movie Libary section differences
    if args.movieLibName != None:
        movieCompare(db1, plexServer1, plexServer2, args)


if __name__ == '__main__':
    logger.info("========= Starting ===========")
    msg = (f"PlexCompare Version: {VERSION}")
    logger.info(f"{msg}")
    parser = argparse.ArgumentParser(description="Plex Compare Report")

    parser.add_argument('-u', help='The Plex User ID',
                        type=str, dest='userName', metavar='plex_userid', required=True)
    parser.add_argument('server1', help='First plex server', type=str,
                        metavar='server_name')
    parser.add_argument('server2', help='Second plex server',
                        type=str, metavar='server_name')
    parser.add_argument(
        '--OutPath', help='Directory path where csv files will be placed. Default is current directory', metavar='DirPath', type=str, dest='dirSave')

    parser.add_argument(
        '--Movie', help='Movie library name to compare', dest='movieLibName', metavar='lib_name', type=str)
    parsedArgs = parser.parse_args()
    main(parsedArgs)
