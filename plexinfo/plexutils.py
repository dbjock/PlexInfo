import sys
import logging
import traceback
import csv
from pathlib import Path
from plexinfo import sqlitedb as mydb

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
        movieLib (plexapi.library.MovieSection): The movie section to export
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
            mRow['Genres'] = _genreStr(m.genres)
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


def _genreStr(genreList):
    tmpLst = []
    for i in genreList:
        tmpLst.append(i.tag)

    tmpLst.sort()
    return tmpLst


def _collection2Rec(dbObj, colKey, colVal):
    """Add collection records to database

    Args:
        dbObj (class sqlitedb.LocalDB): Database obj to be updated
        colKey (class sqlitedb.ColKey): The Collection Key record object
        colVal (class sqlitedb.ColKeVal): The value of the Collect key
    """
    # Saving the key
    logger.debug(f"writing to database collection key: {colKey.sKey}")
    colVal.srckey_id = dbObj.addColKeyRec(colKey)
    logger.debug(f"writing to database collection key value: {colVal.sValue}")
    dbObj.addColValRec(colVal)


def _movie2Rec(dbObj, svrName, uFilePath, libName, sKey, keyVal):
    "TODO: Why all the values for mydb.LibSrcKey? Just sent over mydb.LibSrcKey"
    srcR = mydb.LibSrcKey()
    srcR.svrName = svrName
    srcR.uFilePath = uFilePath
    srcR.libName = libName
    srcR.sKey = sKey

    valR = mydb.LibKeyVal()
    valR.sValue = keyVal
    logger.debug(f"write to lib key table, and get rowID")
    valR.srckey_id = dbObj.addLibKeyRec(srcR)
    logger.debug(f"rowID : {valR.srckey_id}")
    dbObj.addLibValRec(valR)


def movieLib2Db(dbObj, movieLib, svrName, maxItems=0):
    """Export movie library items into database

    Args:
        dbObj (sqlitedb.LocalDB object): database object to update
        movieLib (plexapi.library.MovieSection): Movie lib section to export
        svrName (string): Name of the plex server
        maxItems (int, optional): max records to write. Defaults to 0.
    """
    # Get all media from the movie library
    logger.info(f"Getting all movies from the movie library: {movieLib.title}")
    mList = movieLib.all()
    itemCount = 0
    if maxItems > 0:
        logger.warning(f"Max Movies allowed to be exported: {maxItems}")

    logger.debug("updating database")
    for m in mList:
        itemCount += 1
        # The Key part of the key/value pair
        _movie2Rec(dbObj, svrName=svrName, uFilePath=_uFilePath(
            m.locations[0]), libName=movieLib.title, sKey="guid", keyVal=str(m.guid))
        # ##############################
        _movie2Rec(dbObj, svrName=svrName, uFilePath=_uFilePath(
            m.locations[0]), libName=movieLib.title, sKey="Title", keyVal=m.title)
        # ##############################
        _movie2Rec(dbObj, svrName=svrName, uFilePath=_uFilePath(
            m.locations[0]), libName=movieLib.title, sKey="TitleSort", keyVal=m.titleSort)
        # ###############################
        _movie2Rec(dbObj, svrName=svrName, uFilePath=_uFilePath(
            m.locations[0]), libName=movieLib.title, sKey="OrigTitle", keyVal=m.originalTitle)
        # ###############################
        _movie2Rec(dbObj, svrName=svrName, uFilePath=_uFilePath(
            m.locations[0]), libName=movieLib.title, sKey="Year", keyVal=m.year)
        # ###############################
        _movie2Rec(dbObj, svrName=svrName, uFilePath=_uFilePath(
            m.locations[0]), libName=movieLib.title, sKey="Location", keyVal=str(m.locations))
        # ###############################
        _movie2Rec(dbObj, svrName=svrName, uFilePath=_uFilePath(
            m.locations[0]), libName=movieLib.title, sKey="Genres", keyVal=str(_genreStr(m.genres)))
        # ###############################
        _movie2Rec(dbObj, svrName=svrName, uFilePath=_uFilePath(
            m.locations[0]), libName=movieLib.title, sKey="Media", keyVal=str(m.media))

        if itemCount % 20 == 0:
            logging.info(f"Movies exported to db: {itemCount}")

        if itemCount == maxItems:
            break

    logger.debug("database update done")


def collection2Db(dbObj, movieLib, dbSvrNameTag, maxItems=0):
    pass
    mCollections = movieLib.collection()
    # Iterate thru collections (mCollections) in the Movie Library
    itemCount = 1
    for c in mCollections:
        c_keyRec = mydb.ColKey()
        c_valRec = mydb.ColKeyVal()

        c_keyRec.svrName = dbSvrNameTag
        c_keyRec.libName = movieLib.title
        c_keyRec.colName = c.title

        c_keyRec.sKey = "collectionMode"
        c_valRec.sValue = c.collectionMode
        _collection2Rec(dbObj, c_keyRec, c_valRec)

        c_keyRec.sKey = "collectionSort"
        c_valRec.sValue = c.collectionSort
        _collection2Rec(dbObj, c_keyRec, c_valRec)

        childList = []
        for c_child in c.children:
            childList.append(c_child.title)

        childList.sort()
        c_keyRec.sKey = f"children"
        c_valRec.sValue = str(childList)
        _collection2Rec(dbObj, c_keyRec, c_valRec)

        if itemCount == maxItems:
            break

        itemCount += 1


if __name__ == '__main__':
    pass
