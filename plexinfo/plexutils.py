import sys
import logging
import traceback
import csv
from pathlib import Path

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


def csvExportMovie(movieLib, outFile, maxItems=0):
    """Export movie library items to csv file

    Args:
        movieLib (plexapi.library.MovieSection): The movie section to extract
        outFile ([string]): output file for the data
        maxItems (int, optional): max records to write. Defaults to 0.
    """
    # Columns layout.
    colHdr = ['LibName', 'guid', 'Title', 'TitleSort',
              'OrigTitle', 'Year', 'Location', 'uFilePath', 'Genres', 'Media']

    # Get all media from the movie library
    logger.info(f"Getting all movies from the {movieLib.title}")
    mList = movieLib.all()
    itemCount = 1
    if maxItems > 0:
        logging.warning(f"Max items that will be returned: {maxItems}")
    logger.info(f"Writing to {outFile}")
    outcsv = open(outFile, 'w', newline='')
    with outcsv:
        csvWrite = csv.DictWriter(outcsv, fieldnames=colHdr)
        csvWrite.writeheader()
        for m in mList:
            itemCount += 1
            mRow = {}
            mRow['LibName'] = movieLib.title
            mRow['guid'] = m.guid
            mRow['Title'] = m.title
            mRow['TitleSort'] = m.titleSort
            mRow['OrigTitle'] = m.originalTitle
            mRow['Year'] = m.year
            mRow['Location'] = m.locations
            mRow['uFilePath'] = _uFilePath(m.locations[0])
            mRow['Genres'] = m.genres
            mRow['Media'] = m.media
            csvWrite.writerow(mRow)

            if itemCount == maxItems:
                break

    logger.info(f"Wrote {itemCount} items from {movieLib.title}")
    print(f"Wrote {itemCount} items from {movieLib.title}")


def _uFilePath(plexLoc):
    """Provides universal path and filename (no drive)

    Args:
        plexLoc (string): file path and name (plex location)

    Returns:
        string: full file path and name
        example: /dir/dirA/dirB/my file name.mkv
    """
    p_theLoc = Path(plexLoc)
    if p_theLoc.drive:
        offset = 1  # windows path
    else:
        offset = 2  # non windows path
    uPath = ""
    for x in range(offset, len(p_theLoc.parts)):
        uPath = uPath + f"/{p_theLoc.parts[x]}"
    return uPath


if __name__ == '__main__':
    pass
