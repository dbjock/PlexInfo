import sys
import logging
import traceback

logger = logging.getLogger("PlexUtils")


def connectPlexServer(plexAcct, svrName):
    """Will connect to the server
    plexAcct : MyPlexAccount object
    svrName  : Plex server name

    Returns : Plex server connection object"""
    logger.debug(f"connecting to svrName: {svrName}")
    try:
        plexConnect = plexAcct.resource(svrName).connect()
    except Exception as err:
        logger.critical(f"Error:  {err}", exc_info=True)
        sys.exit(1)

    logger.debug(f"successfully connected to svrName: {svrName}")
    return plexConnect


def dump_movieLibAtt(movieLib):
    """Print attributes of the movie Library Type"""
    print(f"  Library Title: {movieLib.title}")
    print(f"  Settings:  {movieLib.settings()}")
    print(f"  it is a      : {movieLib.type} type")
    print(f"  items        : {movieLib.totalSize}")
    print(f"  Agent        : {movieLib.agent}")
    print(f"  Key          : {movieLib.key}")
    print(f"  Locations    : {movieLib.locations}")
    print(f"  Scanner      : {movieLib.scanner}")


if __name__ == '__main__':
    pass
