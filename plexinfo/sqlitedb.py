import sys
import logging
import sqlite3
import hashlib
import csv
from pathlib import Path

logger = logging.getLogger("sqlitedb")


class LocalDB():
    def __init__(self, dbLoc=None):
        """init the sqlite database class

        Args:
            dbLoc ([string], optional): database filename. Defaults to :memory:
        """
        self.conn = None
        if dbLoc == None:
            dbLoc = ":memory:"

        logger.debug(f"attempt open db {dbLoc}")
        try:
            self.conn = sqlite3.connect(
                dbLoc, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        except sqlite3.Error as errID:
            logger.critical(
                f"Database connection failure. ", exc_info=True)
            sys.exit(1)
        except Exception as err:
            logger.critical(f"Error:  {err}", exc_info=True)
            sys.exit(1)

        logger.debug(f"successful connection to {dbLoc}")

        c = self.conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("PRAGMA database_list;")
        xtmp = c.fetchall()
        logger.debug(f"PRAGMA database_list: {xtmp}")

    def _exeScriptFile(self, scriptFileName):
        """Executes a Script file. (internal use only)

        Args:
            scriptFileName (string): SQL script file to run
        """

        logger.debug(f"loading script: {scriptFileName} to memory")
        scriptFile = open(scriptFileName, 'r')
        script = scriptFile.read()
        scriptFile.close()
        logger.debug(f"executing script: {scriptFileName}")
        try:
            c = self.conn.cursor()
            c.executescript(script)
        except Exception as e:
            logger.critical(
                f"Unexpected Error running script: {scriptFileName}. Exception {e}", exc_info=True)
            sys.exit(1)

        self.conn.commit()
        logger.debug(f"script: {scriptFileName} commited successfully")

    def _exeSQLInsert(self, sql, theVals):
        """Submit insert type sql. (internal use only)

        Args:
            sql (string): The insert Sql, this will include INSERT
            theVals     : The value parms passed into the sql.
                theVals type depends on the sql, i.e. list or dict.

        Returns:
            [list]: [int,string]
            Samples:
                [0, "Commit successful"]
                [2, f"sqlite integrity error: {e.args[0]}"]
            Unexpected error will exit app
        """
        logger.debug(f"Sql: {sql}")
        logger.debug(f"Values: {theVals}")
        try:
            c = self.conn.cursor()
            c.execute(sql, theVals)
            self.conn.commit()

        except sqlite3.IntegrityError as e:
            logger.warning(f"sqlite integrity error: {e.args[0]}")
            return [2, f"sqlite integrity error: {e.args[0]}"]
        except Exception as e:
            logger.critical(
                f"Unexpected error executing sql: {sql}. Values are {theVals} Exception: {e}", exc_info=True)
            sys.exit(1)

        logger.debug("successful commit of sql")
        return [0, "Commit successful"]

    def initDB(self, scriptPath):
        """Create tables, views, indexes for the database

        ASSUMPTION database is new, and tables do not exist.
        Args:
            scriptPath (string): Path to script(s). Defaults to None.
        """
        logger.info(f"scriptPath={scriptPath}")
        gtScripts = Path(scriptPath)
        logger.info(f"Executing scripts to create database")

        scriptFile = gtScripts / "createtables.sql"
        logger.debug(f"Executing {scriptFile}")
        self._exeScriptFile(scriptFileName=f'{scriptFile}')

    def addLibKeyRec(self, srcRec):
        """Add a record to the Library Key table

        Args:
            srcRec ([class srcRec]): Source record to add

        Returns:
            [int]: The primary key id for the added source record
        """
        sql = "INSERT INTO t_libkeys (server, library, filePath, skey, uKey) VALUES (:server, :libName, :uFilePath, :sKey, :uKey)"
        theVals = {'server': srcRec.svrName,
                   'libName': srcRec.libName, 'uFilePath': srcRec.uFilePath, 'sKey': srcRec.sKey, 'uKey': srcRec.uKey}
        r = self._exeSQLInsert(sql, theVals)

        # Getting the rowID for the record just added.
        try:
            c = self.conn.cursor()
            c.execute("select last_insert_rowid()")
            row = c.fetchone()
        except Exception as e:
            logger.critical(
                f"Unexpected error executing sql: {sql}. Exception: {e}", exc_info=True)
            sys.exit(1)

        return row[0]

    def addLibValRec(self, keyRec):
        sql = "INSERT INTO t_libvals (srcKey_id, s_value) VALUES (:srcKey, :sValue)"
        theVals = {'srcKey': keyRec.srckey_id, 'sValue': keyRec.sValue}
        logger.debug(f"adding movie library value record")
        return self._exeSQLInsert(sql, theVals)

    def exportLibDiff(self, oFile):
        """Export the Library diff query to a csv file

        Args:
            oFile (string): File name for the csv file
        """
        logger.debug(f"oFile={oFile}")

        sql = "SELECT library, filePath, skey, server1_val, server2_val, isDiff FROM v_lib_DiffResults"

        try:
            logger.debug(f"executing sql: {sql}")
            localc = self.conn.cursor()
            localc.execute(sql)

        except Exception as e:
            logger.critical(
                f"Unexpected error executing sql: {sql}. Values are {theVals} Exception: {e}", exc_info=True)
            sys.exit(1)

        logger.debug(f"Writing sql results to:  {oFile}")
        with open(oFile, "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file, dialect='excel')
            csv_writer.writerow([i[0] for i in localc.description])
            csv_writer.writerows(localc)

    def exportColDiff(self, oFile):
        logger.debug(f"oFile={oFile}")
        sql = "select libname as library, colname, skey, server1_val, server2_val, isdiff FROM v_col_DiffResults"
        try:
            logger.debug(f"executing sql: {sql}")
            localc = self.conn.cursor()
            localc.execute(sql)
        except Exception as e:
            logger.critical(
                f"Unexpected error executing sql: {sql}. Values are {theVals} Exception: {e}", exc_info=True)
            sys.exit(1)

        logger.debug(f"Writing sql results to:  {oFile}")
        with open(oFile, "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file, dialect='excel')
            csv_writer.writerow([i[0] for i in localc.description])
            csv_writer.writerows(localc)

    def addColKeyRec(self, keyRec):
        """Add a record to the Collection keys table

        Args:
            keyRec (Class ColKey): Collection Key's object with values to write

        Returns:
            [int]: The primary key id for the added key record
        """
        pass
        sql = "INSERT INTO t_colkeys (svrName, libName, colName, sKey, uKey) VALUES (:svrName, :libName, :colName, :sKey, :uKey)"
        theVals = {'svrName': keyRec.svrName, 'libName': keyRec.libName,
                   'colName': keyRec.colName, "sKey": keyRec.sKey, "uKey": keyRec.uKey}

        logger.debug(f"adding collection key record : {theVals}, ")
        r = self._exeSQLInsert(sql, theVals)
        # Getting the rowID for the record just added.
        try:
            xcursor = self.conn.cursor()
            xcursor.execute("select last_insert_rowid()")
            row = xcursor.fetchone()
        except Exception as e:
            logger.critical(
                f"Unexpected error executing sql: {sql}. Exception: {e}", exc_info=True)
            sys.exit(1)

        return row[0]

    def addColValRec(self, valRec):
        sql = "INSERT INTO t_colvals (colkey_id, s_value) VALUES (:ColKey, :sValue)"
        theVals = {'ColKey': valRec.srckey_id, 'sValue': valRec.sValue}

        logger.debug(f"adding collection value record {valRec.srckey_id}")

        return self._exeSQLInsert(sql, theVals)


class LibSrcKey():
    def __init__(self):
        self.svrName = ""
        self.libName = ""
        self.uFilePath = ""
        self.sKey = ""

    @property
    def uKey(self):
        # Returns unique key created by
        # returning md5 hexdigest of the combined:
        #  - Library Name (libname)
        #  - Universal File Path (uFilePath)
        #  - Key (sKey)
        str2hash = self.libName + self.uFilePath + self.sKey
        return hashlib.md5(str2hash.encode()).hexdigest()


class LibKeyVal():
    def __init__(self):
        self.srckey_id = ""
        self.sValue = ""

    def __repr__(self):
        return f"srckey_id={self.srckey_id}, svalue={self.sValue}"


class ColKey():
    def __init__(self):
        self.svrName = ""
        self.libName = ""
        self.colName = ""
        self.sKey = ""

    @property
    def uKey(self):
        # Returns unique key created by
        # returning md5 hexdigest of the combined:
        #  - Library Name (libname)
        #  - Collection Name (colName)
        #  - Key (sKey)
        str2hash = self.libName + self.colName + self.sKey
        return hashlib.md5(str2hash.encode()).hexdigest()


class ColKeyVal():
    def __init__(self):
        self.srckey_id = ""
        self.sValue = ""

    def __repr__(self):
        return f"srckey_id={self.srckey_id}, svalue={self.sValue}"
