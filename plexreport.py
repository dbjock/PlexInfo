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
from plexapi.myplex import MyPlexAccount

logger = logging.getLogger("PlexReport")

with open("log.conf", 'rt') as f:
    config = yaml.safe_load(f.read())

logging.config.dictConfig(config)
VERSION = "1.BETA"


def main(args):
    plexRptData = Path.cwd() / 'Data'
    plexScripts = Path.cwd() / 'Scripts'
    now = datetime.now()
    logger.debug(f"args is {args}")

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
    dbFile = ":memory:"
    db1 = mydb.LocalDB(dbLoc=dbFile)
    db1.initDB(plexScripts)
    print("-"*70)
    ############################################################
    # Connecting to Plex Servers
    msg = f"Connecting to servers"
    print(msg)
    logger.info(f"{msg}")
    plexServer1 = myutil.connectPlexServer(plexAcct, args.server1)

    msg = f"{args.server1} - Connected"
    print(msg)
    logger.info(f"{msg}")

    plexServer2 = myutil.connectPlexServer(plexAcct, args.server2)
    msg = f"{args.server2} - Connected"
    print(msg)
    logger.info(f"{msg}")

    ############################################################
    # Reporting on Collection differences

    print()
    print(f"{args.server1}: Exporting collection data from movie library section : {args.secName}")
    xmovLib = plexServer1.library.section(args.secName)
    myutil.collection2Db(db1, xmovLib, dbSvrNameTag='server1')

    print(f"{args.server2}: Exporting collection data from movie library section : {args.secName}")
    xmovLib = plexServer2.library.section(args.secName)
    myutil.collection2Db(db1, xmovLib, dbSvrNameTag='server2')

    csvFilename = f"{args.secName}_collections_{now.strftime('%Y-%m-%d-%H%M')}.csv"
    if args.dirSave == None:
        collectionCSVFile = Path.cwd() / csvFilename
    else:
        collectionCSVFile = Path(args.dirSave) / csvFilename

    print(f"Creating Collection Diff file {collectionCSVFile}")
    db1.exportColDiff(collectionCSVFile)
    ############################################################
    # Reporting on movie differences
    print()
    print(f"{args.server1}: Exporting movie data from movie library section : {args.secName}")
    xmovLib = plexServer1.library.section(args.secName)
    myutil.movieLib2Db(db1, xmovLib, 'server1')

    print(f"{args.server2}: Exporting movie data from movie library section : {args.secName}")
    xmovLib = plexServer2.library.section(args.secName)
    myutil.movieLib2Db(db1, xmovLib, 'server2')

    csvFilename = f"{args.secName}_library_{now.strftime('%Y-%m-%d-%H%M')}.csv"
    # Path.cwd
    if args.dirSave == None:
        libCSVFile = Path.cwd() / csvFilename
    else:
        libCSVFile = Path(args.dirSave) / csvFilename

    print(f"Creating Movie Library Diff file :{libCSVFile}")
    db1.exportLibDiff(libCSVFile)


if __name__ == '__main__':
    logger.info("========= Starting ===========")
    msg = (f"Plexreport Version: {VERSION}")
    logger.info(f"{msg}")
    parser = argparse.ArgumentParser(description="Plex Diff Report")
    commandSubparser = parser.add_subparsers(title="Commands", dest='command')
    parser.add_argument('-u', help='The Plex User ID',
                        type=str, dest='userName', metavar='plex_userid', required=True)

    # Movie Library command
    movLib_parser = commandSubparser.add_parser(
        'movie', help="Get a comparison report for a movie library including it's collections")
    movLibGroup = movLib_parser.add_argument_group(
        "Comparison report for a Movie library including Collections")
    movLibGroup.add_argument('server1', help='First plex server', type=str,
                             metavar='server_name')
    movLibGroup.add_argument('server2', help='Second plex server', type=str,
                             metavar='server_name')
    movLibGroup.add_argument(
        'secName', help='Movie library name', metavar='lib_name', type=str)

    movLibGroup.add_argument(
        '--OutPath', help='Directory path where csv files will be placed. Default is current directory', metavar='DirPath', type=str, dest='dirSave')

    parsedArgs = parser.parse_args()
    main(parsedArgs)
