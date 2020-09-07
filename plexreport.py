import sys
import getpass
import logging.config
import yaml
from pathlib import Path

# app specific modules
from plexinfo import sqlitedb as mydb
from plexinfo import plexutils as myutil
from plexapi.myplex import MyPlexAccount

logger = logging.getLogger("PlexReport")

with open("log.conf", 'rt') as f:
    config = yaml.safe_load(f.read())

logging.config.dictConfig(config)


def main():
    plexRptData = Path.cwd() / 'Data'
    plexScripts = Path.cwd() / 'Scripts'
    userName = "dbjock"
    collectionCSVFile = "C:/Users/Pops/Downloads/collection_diff.csv"
    libCSVFile = "C:/Users/Pops/Downloads/movie_diff.csv"

    logger.debug(f"getpass from user {userName}")
    userPass = getpass.getpass(prompt=f"Enter {userName}'s Plex Password: ")
    print(f"Authenticating {userName}")
    try:
        plexAcct = MyPlexAccount(userName, userPass)
    except Exception as err:
        logger.critical(f"Error:  {err}", exc_info=True)
        sys.exit()

    logger.debug(f"username: {userName} authenticated.")
    ###################################################
    dbFile = ":memory:"
    db1 = mydb.LocalDB(dbLoc=dbFile)
    db1.initDB(plexScripts)
    print("-"*70)
    ############################################################
    # Connecting to Plex Servers
    server1 = "FerrisFam1"
    print(f"{server1}: Connecting ")
    plexServer1 = myutil.connectPlexServer(plexAcct, server1)

    server2 = "FerrisFam2"
    print(f"{server2}: Connecting ")
    plexServer2 = myutil.connectPlexServer(plexAcct, server2)

    secName = "Movies"
    ############################################################
    # Reporting on Collection differences
    print()
    print(f"{server1}: Exporting collection data for movie library section : {secName}")
    xmovLib = plexServer1.library.section(secName)
    myutil.collection2Db(db1, xmovLib, dbSvrNameTag='server1')

    print(f"{server2}: Exporting collection data for movie library section : {secName}")
    xmovLib = plexServer2.library.section(secName)
    myutil.collection2Db(db1, xmovLib, dbSvrNameTag='server2')

    print(f"Creating Collection Diff file :{collectionCSVFile}")
    db1.exportColDiff(collectionCSVFile)

    ############################################################
    # Reporting on movie differences
    print()
    print(f"{server1}: Exporting movie data for movie library section : {secName}")
    xmovLib = plexServer1.library.section(secName)
    myutil.movieLib2Db(db1, xmovLib, 'server1')

    print(f"{server2}: Exporting movie data for movie library section : {secName}")
    xmovLib = plexServer2.library.section(secName)
    myutil.movieLib2Db(db1, xmovLib, 'server2')

    print(f"Creating Movie Library Diff file :{libCSVFile}")
    db1.exportLibDiff(libCSVFile)


if __name__ == '__main__':
    main()
