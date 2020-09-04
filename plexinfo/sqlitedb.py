import sys
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger("sqlitedb")


class LocalDB():
    def __init__(self, dbLoc=":memory:"):
        """init the sqlite database class

        Args:
            dbLoc ([string], optional): database filename. Defaults to :memory:
        """
        self.conn = None
        logger.debug(f"attempt open db {dbLoc}")
        try:
            self.conn = sqlite3.connect(
                dbLoc, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            # self.cursor = self.conn.cursor()
        except sqlite3.Error as errID:
            logger.critical(
                f"Database connection failure. ", exc_info=True)
            sys.exit(1)
        except Exception as err:
            logger.critical(f"Error:  {err}", exc_info=True)
            sys.exit(1)

        logger.debug(f"successful connection to {dbLoc}")

        c = self.conn.cursor()
        c.execute("PRAGMA database_list;")
        xtmp = c.fetchall()
        logger.debug(f"PRAGMA database_list: {xtmp}")
        logger.debug(f"dbfile: {xtmp[0][2]}")

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
        except:
            logger.critical(
                f"Unexpected Error running script: {scriptFileName}", exc_info=True)
            sys.exit(1)

        self.conn.commit()
        logger.debug(f"script: {scriptFileName} commited")

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
        except:
            logger.critical(
                f"Unexpected error executing sql: {sql}", exc_info=True)
            sys.exit(1)

        logger.debug("successful commit of sql")
        return [0, "Commit successful"]

    def initDB(self, scriptPath):
        """Create tables, views, indexes for the database

        ASSUMPTION database is new, and tables do not exist.
        Args:
            scriptPath (string): Path to script(s). Defaults to None.
        """
        logger.debug(f"scriptPath={scriptPath}")
        gtScripts = Path(scriptPath)

        scriptFile = gtScripts / "createTables.sql"
        logger.debug(f"Executing {scriptFile}")
        self._exeScriptFile(scriptFileName=f'{scriptFile}')


class srcRec():
    def __init__(self):
        self.server = ""
        self.library = ""
        self.fileobj = ""
